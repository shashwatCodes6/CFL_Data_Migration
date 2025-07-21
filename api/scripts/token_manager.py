import time
import requests
from dotenv import load_dotenv, set_key
import os
import json
import base64
import random
import threading
from typing import Optional

load_dotenv()

def decode_jwt_exp(token: str) -> Optional[float]:
    """Decode JWT token to extract expiration time."""
    try:
        payload = token.split('.')[1]
        padding = '=' * (-len(payload) % 4)
        decoded = base64.urlsafe_b64decode(payload + padding)
        payload_json = json.loads(decoded)
        return payload_json.get("exp")
    except Exception as e:
        print(f"Failed to decode JWT: {e}")
        return None

class TokenRefreshError(Exception):
    """Custom exception for token refresh failures."""
    pass

class TokenManager:
    def __init__(self, name: str, res_header: str, max_retries: int = 3, base_delay: float = 1.0):
        """
        Initialize TokenManager with retry configuration.
        
        Args:
            name: Environment variable name for the token
            res_header: Response header key for the token
            max_retries: Maximum number of retry attempts (default: 3)
            base_delay: Base delay in seconds for exponential backoff (default: 1.0)
        """
        self.name = name
        self.res_header = res_header
        self.max_retries = max_retries
        self.base_delay = base_delay
        self._token_cache = None
        self._token_expiry = None
        self._refresh_lock = threading.Lock()
        self._last_refresh_attempt = 0
    
    def get_token(self, force_refresh: bool = False) -> str:
        """
        Get valid token, refreshing if necessary.
        
        Args:
            force_refresh: Force token refresh even if current token seems valid
        """
        with self._refresh_lock:
            # Force reload environment variables to get latest token
            if force_refresh:
                load_dotenv(override=True)
                self._token_cache = None  # Clear cache to force fresh read
            
            # Check cached token first
            if not force_refresh and self._token_cache and self._token_expiry:
                if time.time() < (self._token_expiry - 60):  # 60-second buffer
                    return self._token_cache
            
            # Always reload env before checking token to ensure we have latest value
            load_dotenv(override=True)
            access_token = os.getenv(self.name)
            exp = decode_jwt_exp(access_token) if access_token else None
            
            # Determine if refresh is needed
            needs_refresh = (
                force_refresh or
                not access_token or 
                not isinstance(exp, (int, float)) or 
                time.time() >= (exp - 60)  # 60-second buffer
            )
            
            if needs_refresh:
                # Prevent too frequent refresh attempts (rate limiting)
                current_time = time.time()
                if current_time - self._last_refresh_attempt < 5:  # 5-second cooldown
                    print(f"Skipping refresh for {self.name} - too recent (cooldown: 5s)")
                    if self._token_cache:
                        return self._token_cache
                
                self._last_refresh_attempt = current_time
                self.refresh_token()
                
                # Force reload after refresh and update cache
                load_dotenv(override=True)
                access_token = os.getenv(self.name)
                exp = decode_jwt_exp(access_token)
                if access_token and exp:
                    self._token_cache = access_token
                    self._token_expiry = exp
                    print(f"Token cached for {self.name}: {access_token[:20]}...")
                    
            return access_token or self._token_cache
    
    def refresh_token(self) -> None:
        """Refresh token with retry mechanism and exponential backoff."""
        last_exception = None
        
        for attempt in range(self.max_retries + 1):  # +1 for initial attempt
            try:
                print(f"Refreshing token for {self.name}... (attempt {attempt + 1}/{self.max_retries + 1})")
                
                # Get request body from environment
                req_body_env = os.getenv(self.name + "_REQ_BODY")
                if not req_body_env:
                    raise TokenRefreshError(f"Missing request body environment variable: {self.name}_REQ_BODY")
                
                try:
                    body = json.loads(req_body_env)
                except json.JSONDecodeError as e:
                    raise TokenRefreshError(f"Invalid JSON in request body: {e}")
                
                # Get URL from environment
                url = os.getenv(self.name + "_URL")
                if not url:
                    raise TokenRefreshError(f"Missing URL environment variable: {self.name}_URL")
                
                # Get API key
                api_key = os.getenv("X_API_KEY")
                if not api_key:
                    raise TokenRefreshError("Missing X_API_KEY environment variable")
                
                # Make the request with timeout
                response = requests.post(
                    url,
                    headers={"x-api-key": api_key},
                    json=body,
                    timeout=30  # 30-second timeout
                )
                
                # Check for successful response
                if response.status_code == 200:
                    token_data = response.json()
                    access_token = token_data.get(self.res_header)
                    
                    if not access_token:
                        raise TokenRefreshError(f"Token not found in response under key: {self.res_header}")
                    
                    # Validate the new token
                    exp = decode_jwt_exp(access_token)
                    if not exp or exp <= time.time():
                        raise TokenRefreshError("Received token is invalid or already expired")
                    
                    # Save the new token and reload environment
                    set_key(".env", self.name, access_token)
                    load_dotenv(override=True)  # Reload to ensure env var is updated
                    print(f"Token refreshed successfully for {self.name}")
                    return
                
                # Handle specific HTTP status codes
                elif response.status_code == 401:
                    raise TokenRefreshError("Authentication failed - check API key")
                elif response.status_code == 403:
                    raise TokenRefreshError("Forbidden - insufficient permissions")
                elif response.status_code == 429:
                    # Rate limited - wait longer before retry
                    print(f"Rate limited (429). Waiting before retry...")
                    if attempt < self.max_retries:
                        delay = self.base_delay * (3 ** attempt) + random.uniform(0, 1)
                        time.sleep(delay)
                        continue
                    raise TokenRefreshError("Rate limited - max retries exceeded")
                elif 500 <= response.status_code < 600:
                    # Server error - retry with backoff
                    raise TokenRefreshError(f"Server error: {response.status_code}")
                else:
                    # Client error - don't retry
                    raise TokenRefreshError(f"HTTP {response.status_code}: {response.text}")
                    
            except requests.exceptions.Timeout:
                last_exception = TokenRefreshError("Request timeout")
                print(f"Request timeout on attempt {attempt + 1}")
                
            except requests.exceptions.ConnectionError:
                last_exception = TokenRefreshError("Connection error")
                print(f"Connection error on attempt {attempt + 1}")
                
            except requests.exceptions.RequestException as e:
                last_exception = TokenRefreshError(f"Request failed: {str(e)}")
                print(f"Request failed on attempt {attempt + 1}: {e}")
                
            except TokenRefreshError as e:
                # Re-raise TokenRefreshError immediately for client errors
                if any(msg in str(e) for msg in ["Authentication failed", "Forbidden", "Missing", "Invalid JSON"]):
                    raise e
                last_exception = e
                print(f"Token refresh failed on attempt {attempt + 1}: {e}")
            
            except Exception as e:
                last_exception = TokenRefreshError(f"Unexpected error: {str(e)}")
                print(f"Unexpected error on attempt {attempt + 1}: {e}")
            
            # Calculate delay before next retry (exponential backoff with jitter)
            if attempt < self.max_retries:
                delay = self.base_delay * (2 ** attempt) + random.uniform(0, 1)
                print(f"Retrying in {delay:.1f} seconds...")
                time.sleep(delay)
        
        # All retries exhausted
        raise last_exception or TokenRefreshError("Failed to refresh token after all retries")
    
    def invalidate_cache(self):
        """Invalidate cached token to force refresh on next get_token call."""
        with self._refresh_lock:
            self._token_cache = None
            self._token_expiry = None
            # Force reload environment variables
            load_dotenv(override=True)
            print(f"Token cache invalidated for {self.name}")
    
    def get_fresh_token(self) -> str:
        """
        Get a fresh token, trying multiple methods to ensure we get the latest value.
        """
        # Method 1: Force reload environment
        load_dotenv(override=True)
        env_token = os.getenv(self.name)
        
        # Method 2: Read directly from file
        file_token = self.get_token_from_file()
        
        # Use file token if env token is outdated
        if file_token and env_token != file_token:
            print(f"Environment variable outdated for {self.name}, using file token")
            # Update environment with file token
            os.environ[self.name] = file_token
            return file_token
        
        token = env_token or file_token
        print(f"Fresh token for {self.name}: {token[:20] if token else 'None'}...")
        return token
    
    def get_token_with_401_retry(self, max_401_retries: int = 2) -> str:
        """
        Get token with automatic retry on 401 errors.
        This method should be used when making API calls that might return 401.
        
        Usage example:
            token = token_manager.get_token_with_401_retry()
            response = requests.get(url, headers={"Authorization": f"Bearer {token}"})
            if response.status_code == 401:
                # Token manager will automatically handle this
                token = token_manager.handle_401_and_retry()
        """
        return self.get_token()
    
    def handle_401_and_retry(self) -> str:
        """
        Handle 401 error by invalidating cache and getting fresh token.
        Call this method when you receive a 401 response.
        """
        print(f"Handling 401 error for {self.name} - forcing token refresh")
        self.invalidate_cache()
        return self.get_token(force_refresh=True)

# Helper function for making authenticated requests with automatic retry
def make_authenticated_request(token_manager: TokenManager, method: str, url: str, 
                             max_401_retries: int = 2, **kwargs) -> requests.Response:
    """
    Make an authenticated request with automatic 401 retry handling.
    
    Args:
        token_manager: TokenManager instance
        method: HTTP method ('GET', 'POST', etc.)
        url: Request URL
        max_401_retries: Maximum number of 401 retry attempts
        **kwargs: Additional arguments for requests (headers, json, params, etc.)
    
    Returns:
        requests.Response object
        
    Usage:
        response = make_authenticated_request(
            token_manager, 'GET', 'https://api.example.com/data',
            headers={'Content-Type': 'application/json'}
        )
    """
    for attempt in range(max_401_retries + 1):
        try:
            # Get token (fresh on retry)
            token = token_manager.get_token(force_refresh=(attempt > 0))
            
            if not token:
                raise TokenRefreshError("No token available")
            
            # Debug: Show token being used
            print(f"Using token for request (attempt {attempt + 1}): {token[:20]}...")
            
            # Prepare headers
            headers = kwargs.get('headers', {})
            headers['Authorization'] = f'Bearer {token}'
            kwargs['headers'] = headers
            
            # Make request
            response = requests.request(method, url, **kwargs)
            
            # If 401, invalidate cache and retry
            if response.status_code == 401 and attempt < max_401_retries:
                print(f"Received 401, attempting retry {attempt + 1}/{max_401_retries}")
                print(f"Response: {response.text[:200]}...")
                token_manager.invalidate_cache()
                continue
                
            return response
            
        except Exception as e:
            if attempt == max_401_retries:
                raise
            print(f"Request failed on attempt {attempt + 1}: {e}")
    
    # This should never be reached, but just in case
    raise TokenRefreshError("Max 401 retries exceeded")