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


# Load environment variables from .env
load_dotenv()
custom_logger = CustomLogger("Migration_template_AR_Credit Note.json")
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
    }
    API_URL = os.getenv("API_URL")
    response = requests.post(API_URL, json=payload, headers=headers)
    return response

def main():
    path_prefix = "data/output" # TODO: make it modular
    file_name = "Migration_template_AR_Credit Note.json"
    json_path = path_prefix + "/" + file_name
    custom_logger.start_auto_flush()

    if not os.path.exists(json_path):
        logger.error(f"File not found: {json_path}")
        return

    try:
        payload = load_payload(json_path)
        for idx, i in enumerate(payload):
            response = send_payload(i.get("payload", {}))

            # Collect log info
            log_entry = {
                "payload_number": idx + 1,
                "invoice_number": i.get("invoice_number", ""),
                "legal_entity": i.get("legal_entity", ""),
                "row_number": i.get("row_number", []),
                "status_code": response.status_code,
                "response": response.json()
            }
            custom_logger.save_log_entry(log_entry)
            
            # timeout of 3 seconds
            time.sleep(3)
            
    except Exception as e:
        logger.error(f"Error in db script: {e}")
        custom_logger.stop_auto_flush()
    
    custom_logger.stop_auto_flush()


if __name__ == "__main__":
    main()
