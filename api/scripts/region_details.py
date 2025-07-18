import requests
from api.scripts.token_manager import TokenManager
from dotenv import load_dotenv
import os

load_dotenv()

def fetch_country_details(country_codes, retry=True):
    token = TokenManager.get_token()

    headers = {
        "x-api-key": os.getenv("X_API_KEY"),
        "X-LS-FieldMask": "*",
        "x-location-service-integration-token": token,
        "Cookie": os.getenv("COUNTRY_COOKIE")
    }

    params = {
        "_countryIso2": country_codes
    }
    
    response = requests.get(os.getenv("COUNTRY_URL"), headers=headers, params=params)

    if response.status_code == 401 and retry:
        TokenManager.refresh_token()
        return fetch_country_details(country_codes, retry=False)

    response.raise_for_status()
    return response.json()[0]
