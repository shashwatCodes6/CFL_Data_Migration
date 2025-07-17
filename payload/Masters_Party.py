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
                "countryOfRegistration": {
                    "id": "",
                    "name": "",
                    "iso2Code": "",
                    "iso3Code": "",
                    "phoneCode": ""
                },
                "masterPartyEntityType": record.get("Entity Type", ""),
                "companyPhoneCode": record.get("Company Phone Code", ""),
            }
            payloads.append(payload)
        
        return payloads