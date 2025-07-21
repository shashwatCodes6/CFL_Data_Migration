import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json
import requests
from dotenv import load_dotenv
import time
from token_manager import TokenManager
from utils.logger import get_logger

# Load environment variables from .env
load_dotenv()
logger = get_logger()
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
        logger.error(f"File not found: {json_path}")
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
            
            logger.info(f"Status: {response.status_code} Response: {str(log_entry)} Sheet: {file_name}")
            
            # timeout of 3 seconds
            time.sleep(3)

    except Exception as e:
        logger.error(f"Error in db script: {e}")

if __name__ == "__main__":
    main()
