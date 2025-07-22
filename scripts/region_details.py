import requests
from scripts.token_manager import TokenManager
from dotenv import load_dotenv
import os
from utils.logger import get_logger

logger = get_logger()
load_dotenv()
tm = TokenManager("INT_TOKEN", "token")

def fetch_country_details(country_codes):
    if not country_codes or country_codes == "":
        return {}

    # Construct the request
    token = tm.get_token()
    headers = {
        "x-api-key": os.getenv("X_API_KEY"),
        "X-LS-FieldMask": "*",
        "x-location-service-integration-token": token,
    }
    params = {
        "_countryIso2": country_codes
    }
    
    response = requests.get(os.getenv("COUNTRY_URL"), headers=headers, params=params)
    listified_res = response.json()
    if len(listified_res) == 0:
        return {}
    return listified_res[0]


def fetch_state_details(state_code, country_code):
    if not state_code or state_code == "" or \
        not country_code or country_code == "":
        return {}

    # construct the request
    token = tm.get_token()
    headers = {
        "x-api-key": os.getenv("X_API_KEY"),
        "X-LS-FieldMask": "*",
        "x-location-service-integration-token": token,
    }
    params = {
        "_countryIso2": country_code
    }
    
    response = requests.get(os.getenv("STATE_URL"), headers=headers, params=params)
    listified_res = response.json()
    filtered_res = list(filter(lambda x: x["stateIso2"] == state_code, listified_res))
    if len(filtered_res) == 0:
        return {}
    return filtered_res[0]


def fetch_city_details(city_name, state_code, country_code):
    if not city_name or city_name == "" or \
        not state_code or state_code == "" or \
        not country_code or country_code == "":
        return {}
    
    # construct the request
    token = tm.get_token()
    headers = {
        "x-api-key": os.getenv("X_API_KEY"),
        "X-LS-FieldMask": "*",
        "x-location-service-integration-token": token,
    }
    params = {
        "_countryIso2": country_code,
        "_stateIso2": state_code, 
        "q": city_name,
    }
    
    response = requests.get(os.getenv("CITY_URL"), headers=headers, params=params)
    listified_res = response.json()
    filtered_res = list(filter(lambda x: x["name"] == city_name, listified_res))
    if len(filtered_res) == 0:
        return {}
    return filtered_res[0]


if __name__ == "__main__":
    print(fetch_country_details("IN|AU|US"))