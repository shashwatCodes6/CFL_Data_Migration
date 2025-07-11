import json
import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

API_URL = os.getenv("API_URL")
print(API_URL)

def load_payload(file_path):
    with open(file_path, "r") as f:
        return json.load(f)

def send_payload(payload):
    headers = {"Content-Type": "application/json"}
    response = requests.post(API_URL, json=payload, headers=headers)
    return response

def main():
    json_path = "data/output/AR_input.json"

    if not os.path.exists(json_path):
        print(f"File not found: {json_path}")
        return

    try:
        payload = load_payload(json_path)
        for i in payload:
            response = send_payload(i)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    main()
