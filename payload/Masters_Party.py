from scripts import region_details
from utils.logger import get_logger

logger = get_logger()

class MasterPartyPayload:
    def __init__(self):
        pass
    
    def generate(self, data):
        payloads = []
        
        for record in data:
            payload = {
                "action": "SUBMIT",
                "dunsNumber": record.get("DUNS", ""),
                "masterPartyName": record.get("Party Name", ""),
                "companyEmail": record.get("Company Email", ""),
                "companyWebsite": record.get("Company website", ""),
                "companyPhone": record.get("Company Phone", ""),
                "activeStatus": record.get("Active Status", ""),
                "description": record.get("Description", ""),
                "countryOfRegistration": {},
                "masterPartyEntityType": record.get("Entity Type", ""),
                "companyPhoneCode": record.get("Company Phone Code", ""),
            }
            
            country_details = region_details.fetch_country_details(record.get("Country", ""))
            payload["countryOfRegistration"] = {
                "id": country_details.get("id", ""),
                "name": country_details.get("name", ""),
                "iso2Code": country_details.get("iso2", ""),
                "iso3Code": country_details.get("iso3", ""),
                "phoneCode": country_details.get("phonecode", ""),
            }

            logger.info("Master party: " + str(payload))

            payloads.append(payload)
        
        return payloads