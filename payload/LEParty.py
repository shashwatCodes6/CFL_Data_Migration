class LEPartyPayload:
    def __init__(self):
        pass
    
    def generate(self, data):
        payloads = []
        
        for record in data:
            payload = {
                "action": "SUBMIT",
                "sourceReferenceId": record.get("Source Reference ID", "System_source_reference"),
                "isCustomer": record.get("Party Role Customer", "false"),
                "isSupplier": record.get("Party Role Supplier", "false"),
                "accessIdentifiers": {
                    "legalEntityUUID": "0878e1cb-e96a-4025-bf19-40fa1188e687",
                    "businessUnitUUID": "",
                    "locationUUID": ""
                },
                "masterParty": {
                    "guid": record.get("Master Party ID", "")
                },
                "legalEntityPartyType": record.get("Party Type", "PNL"),
                "activeStatus": "ACTIVE",
                "legalEntityPartyAddressDetailList": self._get_address_details(record),
                "legalEntityPartyContactDetailList": self._get_contact_details(record),
                "legalEntityPartyTaxDetailList": self._get_tax_details(record),
                "legalEntityPartyBankDetailList": self._get_bank_details(record),
                "isPartySegment": record.get("Is party a segment", "false"),
                "documents": [],
                "deletedDocuments": [],
                "segmentDetails": self._get_segment_details(record)
            }
            payloads.append(payload)
        
        return payloads
    
    def _get_address_details(self, record):
        return [{
            "label": record.get("Address Label", "System Address"),
            "addressLine1": record.get("Address Line 1", ""),
            "addressLine2": record.get("Address Line 2", ""),
            "city": self._get_city_details(record),
            "state": self._get_state_details(record),
            "country": self._get_country_details(record),
            "postalCode": record.get("Postal Code", ""),
            "activeStatus": record.get("Address Active?", ""),
            "shipToSite": record.get("Ship to flag", "false"),
            "billToSite": record.get("Bill to flag", "false"),
            "supplierSite": record.get("Supplier Site", "false")
        }]
    
    def _get_city_details(self, record):
        return {
            "id": "",
            "name": record.get("City", ""),
            "stateId": "",
            "stateName": "",
            "stateIso2Code": record.get("State", ""),
            "countryId": "",
            "countryName": "",
            "countryIso2Code": record.get("Country", "")
        }
    
    def _get_state_details(self, record):
        return {
            "id": "",
            "name": "",
            "iso2Code": record.get("State", ""),
            "countryId": "",
            "countryIso2Code": record.get("Country", ""),
            "countryName": ""
        }
    
    def _get_country_details(self, record):
        return {
            "id": "",
            "name": "",
            "iso2Code": record.get("Country", ""),
            "iso3Code": "",
            "phoneCode": ""
        }
    
    def _get_contact_details(self, record):
        return [{
            "name": record.get("Contact Name", "System"),
            "countryCode": record.get("Contact Phone Code", ""),
            "telephoneNumber": record.get("Contact Phone", ""),
            "email": record.get("Contax Email", ""),
            "designation": record.get("Contact Designation", ""),
            "activeStatus": "ACTIVE"
        }]
    
    def _get_tax_details(self, record):
        return [{
            "id": None,
            "guid": None,
            "taxRegimeUUID": record.get("Tax Regime Code", ""),
            "taxStartDate": record.get("Start Date", ""),
            "taxEndDate": record.get("End Date", ""),
            "exemptFromTax": record.get("Exempt From Tax", ""),
            "taxRegistrationNumber": record.get("Tax Registration Number", ""),
            "activeStatus": record.get("Tax Regime Active?", "ACTIVE")
        }]
    
    def _get_bank_details(self, record):
        return [{
            "id": None,
            "guid": None,
            "bankAccountName": record.get("Bank Account Name", ""),
            "accountNumber": record.get("Bank Account Number", ""),
            "branchName": record.get("Bank Branch Name", ""),
            "branchNumber": record.get("Bank Branch Number", ""),
            "swiftCode": "",
            "ibanCode": record.get("IBAN Code", ""),
            "defaultBank": record.get("Bank Default", "false"),
            "activeStatus": record.get("Bank Active?", "ACTIVE"),
            "bankCountry": {
                "id": "",
                "name": "",
                "iso2Code": record.get("Bank Country", ""),
                "iso3Code": "",
                "phoneCode": ""
            }
        }]
    
    def _get_segment_details(self, record):
        if record.get("Is party a segment", "false").lower() == "true":
            return {
                "uuid": "",
                "segmentType": record.get("Segment Type", "BUSINESS_UNIT")
            }
        return {}