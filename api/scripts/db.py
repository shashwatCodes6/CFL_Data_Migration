import json
import requests
import os
from dotenv import load_dotenv
import time
from token_manager import TokenManager

# Load environment variables from .env
load_dotenv()
tm = TokenManager("AUTH_HEADER", "accessToken")

def load_payload(file_path):
    with open(file_path, "r") as f:
        return json.load(f)

def send_payload(payload):
    auth_token = tm.get_token()
    headers = {
        "Content-Type": "application/json", 
        "Authorization": f"Bearer {auth_token}", 
        "Cookie": os.getenv("COOKIE")
    }
    API_URL = os.getenv("API_URL")
    response = requests.post(API_URL, json=payload, headers=headers)
    return response

def main():
    path_prefix = "data/output" # TODO: make it modular
    file_name = "Migration_template_AP_Credit Note.json"
    json_path = path_prefix + "/" + file_name

    if not os.path.exists(json_path):
        print(f"File not found: {json_path}")
        return

    try:
        payload = load_payload(json_path)
        for idx, i in enumerate(payload):
            response = send_payload(i)

            # Collect log info
            log_entry = {
                "payload_number": idx + 1,
                # TODO: both of them can be at different places in the payload
                # "invoice_number": i.get("Invoice Number", ""),
                # "legal_entity": i.get("LEGAL_ENTITY", ""),
                "status_code": response.status_code,
                "response": response.text
            }
            
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")

            # timeout of 3 seconds
            time.sleep(3)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
