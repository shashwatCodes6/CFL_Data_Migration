import numpy as np
import pandas as pd


class LEPartyPayload:
    def __init__(self):
        pass

    def get_value(self, record, key, default = "", index = 0) -> str:
        """
            Safely retrieve a value from a dictionary. Returns "" if:
            - key is missing
            - value is None
            - value is NaN (pandas or numpy)
            - value is an empty list or contains NaN
            - value is the string "nan"
        """
        value = record.get(key, default)

        # None or missing
        if value is None or value == "":
            return ""

        # Handle list or array
        if isinstance(value, (list, np.ndarray, pd.Series)):
            if len(value) == 0:
                return ""
            val = value[index] if len(value) > index else value[0]
            if pd.isna(val) or str(val).strip().lower() == "nan":
                return ""
            return str(val)

        # Handle scalars
        if pd.isna(value) or str(value).strip().lower() == "nan":
            return ""

        return str(value)

    
    def generate(self, data):
        payloads = []
        
        for record in data:
            payload = {
                "action": "SUBMIT",
                "sourceReferenceId": self.get_value(record, "Source Reference ID", "System_source_reference"),
                "isCustomer": self.get_value(record, "Party Role Customer", "false"),
                "isSupplier": self.get_value(record, "Party Role Supplier", "false"),
                "accessIdentifiers": {
                    "legalEntityUUID": "0878e1cb-e96a-4025-bf19-40fa1188e687",
                    "businessUnitUUID": "",
                    "locationUUID": ""
                },
                "masterParty": {
                    "guid": self.get_value(record, "Master Party ID", "")
                },
                "legalEntityPartyType": self.get_value(record, "Party Type", "PNL"),
                "activeStatus": "ACTIVE",
                "legalEntityPartyAddressDetailList": self._get_address_details(record),
                "legalEntityPartyContactDetailList": self._get_contact_details(record),
                "legalEntityPartyTaxDetailList": self._get_tax_details(record),
                "legalEntityPartyBankDetailList": self._get_bank_details(record),
                "isPartySegment": self.get_value(record, "Is party a segment", "false"),
                "documents": [],
                "deletedDocuments": [],
                "segmentDetails": self._get_segment_details(record)
            }
            payloads.append(payload)
        
        return payloads
    
    def _get_address_details(self, record):
        return [{
            "label": self.get_value(record, "Address Label"),
            "addressLine1": self.get_value(record, "Address Line 1", ""),
            "addressLine2": self.get_value(record, "Address Line 2", ""),
            "city": self._get_city_details(record),
            "state": self._get_state_details(record),
            "country": self._get_country_details(record),
            "postalCode": self.get_value(record, "Postal Code", ""),
            "activeStatus": self.get_value(record, "Address Active?", ""),
            "shipToSite": self.get_value(record, "Ship to flag", "false"),
            "billToSite": self.get_value(record, "Bill to flag", "false"),
            "supplierSite": self.get_value(record, "Supplier Site", "false")
        }]
    
    def _get_city_details(self, record):
        return {
            "id": "",
            "name": self.get_value(record, "City", ""),
            "stateId": "",
            "stateName": "",
            "stateIso2Code": self.get_value(record, "State", ""),
            "countryId": "",
            "countryName": "",
            "countryIso2Code": self.get_value(record, "Country", "")
        }
    
    def _get_state_details(self, record):
        return {
            "id": "",
            "name": "",
            "iso2Code": self.get_value(record, "State", ""),
            "countryId": "",
            "countryIso2Code": self.get_value(record, "Country", ""),
            "countryName": ""
        }
    
    def _get_country_details(self, record):
        return {
            "id": "",
            "name": "",
            "iso2Code": self.get_value(record, "Country", ""),
            "iso3Code": "",
            "phoneCode": ""
        }
    
    def _get_contact_details(self, record):
        return [{
            "name": self.get_value(record, "Contact Name", "System"),
            "countryCode": self.get_value(record, "Contact Phone Code", ""),
            "telephoneNumber": self.get_value(record, "Contact Phone", ""),
            "email": self.get_value(record, "Contax Email", ""),
            "designation": self.get_value(record, "Contact Designation", ""),
            "activeStatus": "ACTIVE"
        }]
    
    def _get_tax_details(self, record):
        return [{
            "id": None,
            "guid": None,
            "taxRegimeUUID": self.get_value(record, "Tax Regime Code", ""),
            "taxStartDate": self.get_value(record, "Start Date", ""),
            "taxEndDate": self.get_value(record, "End Date", ""),
            "exemptFromTax": self.get_value(record, "Exempt From Tax", ""),
            "taxRegistrationNumber": self.get_value(record, "Tax Registration Number", ""),
            "activeStatus": self.get_value(record, "Tax Regime Active?", "ACTIVE")
        }]
    
    def _get_bank_details(self, record):
        return [{
            "id": None,
            "guid": None,
            "bankAccountName": self.get_value(record, "Bank Account Name", ""),
            "accountNumber": self.get_value(record, "Bank Account Number", ""),
            "branchName": self.get_value(record, "Bank Branch Name", ""),
            "branchNumber": self.get_value(record, "Bank Branch Number", ""),
            "swiftCode": "",
            "ibanCode": self.get_value(record, "IBAN Code", ""),
            "defaultBank": self.get_value(record, "Bank Default", "false"),
            "activeStatus": self.get_value(record, "Bank Active?", "ACTIVE"),
            "bankCountry": {
                "id": "",
                "name": "",
                "iso2Code": self.get_value(record, "Bank Country", ""),
                "iso3Code": "",
                "phoneCode": ""
            }
        }]
    
    def _get_segment_details(self, record):
        if self.get_value(record, "Is party a segment", "false").lower() == "true":
            return {
                "uuid": "",
                "segmentType": self.get_value(record, "Segment Type", "BUSINESS_UNIT")
            }
        return {}