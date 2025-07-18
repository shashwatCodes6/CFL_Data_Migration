import time
import requests
from dotenv import load_dotenv, set_key
from datetime import datetime, timezone
import os
import json
import base64

load_dotenv()


def decode_jwt_exp(token):
    try:
        payload = token.split('.')[1]
        # Fix padding
        padding = '=' * (-len(payload) % 4)
        decoded = base64.urlsafe_b64decode(payload + padding)
        payload_json = json.loads(decoded)
        return payload_json.get("exp")
    except Exception as e:
        print("Failed to decode JWT:", e)
        return None


class TokenManager:
    _access_token = os.getenv("INT_TOKEN")
    _expires_at = 0  # epoch

    @classmethod
    def get_token(cls):
        if cls._access_token is None or time.time() >= cls._expires_at:
            cls.refresh_token()
        return cls._access_token

    @classmethod
    def refresh_token(cls):
        print("Refreshing int token...")
        body = json.loads(os.getenv("INT_TOKEN_REQ_BODY"))
        response = requests.post(os.getenv("INT_TOKEN_URL"), headers={
            "x-api-key": os.getenv("X_API_KEY"),
        }, json=body)

        if response.status_code != 200:
            print(response.text)
            raise Exception("Failed to refresh token")

        token_data = response.json()
        cls._access_token = token_data["token"]
        set_key(".env", "INT_TOKEN", cls._access_token)

        jwt_exp = decode_jwt_exp(cls._access_token)
        cls._expires_at = jwt_exp - 60 