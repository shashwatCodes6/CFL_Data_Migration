from scripts.region_details import fetch_country_details
from utils.logger import get_logger
import pandas as pd
import numpy as np

logger = get_logger()

class MasterPartyPayload:
    def __init__(self):
        pass

    def get_value(self, record, key, default="", index=0) -> str:
        value = record.get(key, default)

        if value is None or value == "":
            return ""

        if isinstance(value, (list, np.ndarray, pd.Series)):
            if len(value) == 0:
                return ""
            val = value[index] if len(value) > index else value[0]
            if pd.isna(val) or str(val).strip().lower() == "nan":
                return ""
            return str(val)

        if pd.isna(value) or str(value).strip().lower() == "nan":
            return ""

        return str(value)

    def generate(self, data):
        payloads = []

        for record in data:
            payload = {
                "action": "SUBMIT",
                "dunsNumber": self.get_value(record, "DUNS"),
                "masterPartyName": self.get_value(record, "Party Name"),
                "companyEmail": self.get_value(record, "Company Email"),
                "companyWebsite": self.get_value(record, "Company website"),
                "companyPhone": self.get_value(record, "Company Phone"),
                "activeStatus": self.get_value(record, "Active Status"),
                "description": self.get_value(record, "Description"),
                "countryOfRegistration": {},
                "masterPartyEntityType": self.get_value(record, "Entity Type"),
                "companyPhoneCode": self.get_value(record, "Company Phone Code")
            }

            try:
                iso2_code = self.get_value(record, "Country")
                if iso2_code:
                    country_details = fetch_country_details(iso2_code)
                    payload["countryOfRegistration"] = {
                        "id": country_details.get("id", ""),
                        "name": country_details.get("name", ""),
                        "iso2Code": country_details.get("iso2", ""),
                        "iso3Code": country_details.get("iso3", ""),
                        "phoneCode": country_details.get("phonecode", "")
                    }
            except Exception as e:
                logger.error(f"Failed to fetch country details for {iso2_code}: {e}")

            logger.info("Master party: " + str(payload))

            payloads.append({
                "payload": payload,
                "row_number": record.get("row_number", ""),
                "dunsNumber": self.get_value(record, "DUNS"),
                "masterPartyName": self.get_value(record, "Party Name")
            })

        return payloads
