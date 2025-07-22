import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json
import requests
from dotenv import load_dotenv
import time
from token_manager import TokenManager
from utils.logger import get_logger
from utils.logger import CustomLogger
import cloudscraper
import certifi

scraper = cloudscraper.create_scraper()

# Load environment variables from .env
load_dotenv()
custom_logger = CustomLogger("Migration_template_Masters_Party.json")
logger = get_logger()
tm = TokenManager("AUTH_HEADER", "accessToken")

def load_payload(file_path):
    with open(file_path, "r") as f:
        return json.load(f)

def send_payload(payload):
    auth_token = tm.get_token()
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f"Bearer {auth_token}",
    }
    # Master Party API
    API_URL = os.getenv("MASTER_PARTY_URL")
    response = {}
    try:
        response = scraper.post(API_URL, json=payload, headers=headers, verify=certifi.where())
    except Exception as e:
        raise Exception("Error hitting the master party url: " + e)
    
    if response.status_code != 200:
        return response
    # Approval API 
    APPROVAL_URL = os.getenv("MASTER_PARTY_REVIEW_URL")
    request_body = {
        "uuid": response.json().get("guid", ""),
        "version": response.json().get("version", 1),
        "moduleType": "PARTY_MASTER",
        "action": "APPROVED",
    }
    approval_res = {}
    try:
        approval_res = scraper.post(APPROVAL_URL, json=request_body, headers=headers, verify=certifi.where())
    except Exception as e:
        raise Exception("Error hitting the master party approval url: " + e)

    return approval_res
    

def main():
    path_prefix = "data/output" # TODO: make it modular
    file_name = "Migration_template_Masters_Party.json"
    json_path = path_prefix + "/" + file_name

    if not os.path.exists(json_path):
        logger.error(f"File not found: {json_path}")
        return

    try:
        payload = load_payload(json_path)
        for idx, i in enumerate(payload):
            if "payload" in i:
                response = send_payload(i.get("payload"))

                log_entry = {
                    "payload_number": idx + 1,
                    "invoice_number": i.get("invoice_number", ""),
                    "legal_entity": i.get("legal_entity", ""),
                    "row_number": i.get("row_number", ""),
                    "status_code": response.status_code,
                    "response": response.json()
                }
                custom_logger.save_log_entry(log_entry)

                # timeout of 3 seconds
                time.sleep(3)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
