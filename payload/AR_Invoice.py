import uuid
from datetime import datetime
import pandas as pd
from utils.config_loader import load_config

config = load_config()

class ARInvoice():
    def date_to_epoch(self, date_value):
        if pd.isna(date_value):
            return None
        return int(pd.to_datetime(date_value, dayfirst=True).timestamp() * 1000)  # milliseconds
    
    
    def _get_value(self, entry, key, index=0):
        """Helper method to safely get values from entry, preserving original string representation"""
        value = entry.get(key)
        if value is None:
            return ""
        
        # Handle numpy nan values
        if isinstance(value, (list, np.ndarray)):
            if len(value) > index:
                val = value[index]
                return "" if pd.isna(val) else str(val)
            return ""
        
        # Handle scalar values (like LEGAL_ENTITY in your case)
        if index == 0:
            return "" if pd.isna(value) else str(value)
        return ""
    

    def generate(self, parsed_data):
        payloads = []

        # Coa Code to be fetched
        coa_code = config['coa_code'] if config['coa_code'] != "" else "DPWG_COA"
            

        for entry in parsed_data:
            validation_uuid = str(uuid.uuid4())

            # SEGMENTS
            segment_mapping = config['segment_mapping'][coa_code]

            segments = []
            for segment_name, column_name in segment_mapping.items():
                if column_name != "null":
                    code_value = entry.get(segment_name, [""])
                    print(segment_name, column_name, code_value, entry[segment_name])
                    if code_value:
                        if isinstance(code_value, list):
                            code_value = code_value[0]
                        
                        segments.append({
                            "validationUUID": str(uuid.uuid4()),
                            "name": column_name,
                            "code": code_value
                        })

            # BASIC INFO
            payload = {
                "validationUUID": validation_uuid,
                "invoiceType": "AR",
                "segments": segments,
                "transactionSource": entry.get("Transaction Source", [""])[0],
                "transactionTypeName": entry.get("Transaction Type", [""])[0],
                "invoiceNumber": entry.get("Invoice Number", [""])[0],
                "orderRefNo": entry.get("Order Reference Number", [""])[0],
                "invoiceDateEpoch": self.date_to_epoch(entry.get("Invoice Date", [None])[0]),
                "accountingDateEpoch": self.date_to_epoch(entry.get("Accounting date", [None])[0]),
                "partyID": entry.get("Customer", [""])[0],
                "billToSite": entry.get("Bill to", [""])[0],
                "shipToSite": entry.get("Ship to", [""])[0],
                "dueDateEpoch": self.date_to_epoch(entry.get("Due Date", [None])[0]),
                "notes": entry.get("Notes", [""])[0],
                "currency": entry.get("Currency", [""])[0],
                "paymentTerm": entry.get("Payment Term", [""])[0] if "Payment Term" in entry else "",
                "invoiceLineDetails": [], 
                "accessIdentifierCodes": {}
            }

            # MULTIPLE LINE HANDLING
            num_lines = len(entry.get("Line", []))
            for i in range(num_lines):
                line_uuid = str(uuid.uuid4())
                tax_override_flag = entry.get("Is tax overriden", ["false"] * num_lines)[i]
                tax_overridden_amount = entry.get("Tax over ridden amount", [""] * num_lines)[i]

                tax_rule = {
                    "validationUUID": line_uuid,
                    "isTaxOverRidden": str(tax_override_flag).lower(),
                    "taxRuleName": entry.get("Tax Rule", [""])[i]
                }

                # Only add override amount if overridden
                print(type(tax_override_flag))
                tax_rule["taxOverRiddenAmount"] = ""
                if tax_rule["isTaxOverRidden"] == "true":
                    tax_rule["taxOverRiddenAmount"] = tax_overridden_amount

                line = {
                    "validationUUID": line_uuid,
                    "itemName": entry.get("Item", [""])[i],
                    "description": entry.get("Line Description", [""])[i],
                    "lineRuleName": entry.get("Revenue Rule", [""])[i],
                    "uomName": entry.get("UOM", [""])[i],
                    "quantity": entry.get("Quantity", [""])[i],
                    "unitPrice": entry.get("Unit Price", [""])[i],
                    "discountPercentage": entry.get("Discount %", [""])[i],
                    "taxRules": [tax_rule],
                    "activeStatus": "ACTIVE"
                }

                payload["invoiceLineDetails"].append(line)


            payload["accessIdentifierCodes"] = {
                "coaCode": coa_code,
                "legalEntityCode": entry.get("LEGAL_ENTITY", [""])[0],
                "businessUnitCode": entry.get("BUSINESS_UNIT", [""])[0],
                "locationCode": entry.get("LOCATION", [""])[0]
            }

            payloads.append(payload)

        return payloads
