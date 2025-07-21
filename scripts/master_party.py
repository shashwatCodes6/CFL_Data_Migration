import json
import requests
import os
from dotenv import load_dotenv
import time
from token_manager import TokenManager
from utils.logger import get_logger

import cloudscraper
import certifi
scraper = cloudscraper.create_scraper()

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
            response = send_payload(i)

            logger.info(f"Master Party Status: {response.status_code} Response: {response.text}")

            # timeout of 3 seconds
            time.sleep(3)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
