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
custom_logger = CustomLogger("Migration_template_LE_Party.json")
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
        'Cookie': os.getenv("LE_PARTY_COOKIE"),
    }
    # Master Party API
    API_URL = os.getenv("LE_PARTY_URL")
    response = {}
    try:
        response = scraper.post(API_URL, json=payload, headers=headers, verify=certifi.where())
    except Exception as e:
        raise Exception("Error hitting the LE party url: " + e)
    
    return response
    

def main():
    path_prefix = "data/output" # TODO: make it modular
    file_name = "Migration_template_LE_Party.json"
    json_path = path_prefix + "/" + file_name

    if not os.path.exists(json_path):
        logger.error(f"File not found: {json_path}")
        return

    try:
        payload = load_payload(json_path)
        custom_logger.start_auto_flush()
        for idx, i in enumerate(payload):
            if "payload" in i:
                response = send_payload(i.get("payload"))

                # TODO: add responses as well
                log_entry = {
                    "payload_number": idx + 1,
                    "masterParty": i.get("masterParty", ""),
                    "status_code": response.status_code,
                    "response": response.json(),
                    "row_number": i.get("row_number", [])
                }

                custom_logger.save_log_entry(log_entry)

                # timeout of 3 seconds
                time.sleep(3)

    except Exception as e:
        print(f"Error: {e}")
        custom_logger.stop_auto_flush()
    
    custom_logger.stop_auto_flush()


if __name__ == "__main__":
    main()
