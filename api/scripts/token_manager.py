import time
import requests
from dotenv import load_dotenv, set_key
import os
import json
import base64

load_dotenv()

def decode_jwt_exp(token):
    try:
        payload = token.split('.')[1]
        padding = '=' * (-len(payload) % 4)
        decoded = base64.urlsafe_b64decode(payload + padding)
        payload_json = json.loads(decoded)
        return payload_json.get("exp")
    except Exception as e:
        print("Failed to decode JWT:", e)
        return None

class TokenManager:
    def __init__(self, name, res_header):
        self.name = name
        self.res_header = res_header

    def get_token(self):
        access_token = os.getenv(self.name)

        exp = decode_jwt_exp(access_token) if access_token else None
        if not access_token or not exp or time.time() >= exp:
            self.refresh_token()

        return os.getenv(self.name)

    def refresh_token(self):
        print(f"Refreshing token for {self.name}...")
        body = json.loads(os.getenv(self.name + "_REQ_BODY"))

        response = requests.post(
            os.getenv(self.name + "_URL"),
            headers={"x-api-key": os.getenv("X_API_KEY")},
            json=body
        )

        if response.status_code != 200:
            raise Exception("Failed to refresh token")

        token_data = response.json()
        access_token = token_data.get(self.res_header, "")
        set_key(".env", self.name, access_token)
