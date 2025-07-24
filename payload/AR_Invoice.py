import uuid
from datetime import datetime
import pandas as pd
import numpy as np
from utils.config_loader import load_config
from utils.logger import get_logger

logger = get_logger()
config = load_config()

class ARInvoice():
    def date_to_epoch(self, date_value):
        if pd.isna(date_value):
            return None
        return str(int(pd.to_datetime(date_value, dayfirst=True).timestamp() * 1000))  # milliseconds
    
    
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

        coa_code = config['coa_code'] if config['coa_code'] != "" else "DPWG_COA"

        for entry in parsed_data:
            validation_uuid = str(uuid.uuid4())

            segment_mapping = config['segment_mapping'][coa_code]
            segments = []

            for segment_name, column_name in segment_mapping.items():
                if column_name:
                    code_value = entry.get(segment_name, [""])
                    
                    if code_value:
                        if isinstance(code_value, list):
                            code_value = code_value[0]

                    # Skip if code_value is empty or NaN
                    if code_value != "" and not (isinstance(code_value, float) and np.isnan(code_value)):
                        segments.append({
                            "validationUUID": str(uuid.uuid4()),
                            "name": column_name,
                            "code": code_value
                        })


            payload = {
                "validationUUID": validation_uuid,
                "invoiceType": "AR",
                "segments": segments,
                "transactionSource": self._get_value(entry, "Transaction Source"),
                "transactionTypeName": self._get_value(entry, "Transaction Type"),
                "invoiceNumber": self._get_value(entry, "Invoice Number"),
                "orderRefNo": self._get_value(entry, "Order Reference Number"),
                "invoiceDateEpoch": self.date_to_epoch(self._get_value(entry, "Invoice Date", 0)),
                "accountingDateEpoch": self.date_to_epoch(self._get_value(entry, "Accounting date", 0)),
                "partyID": self._get_value(entry, "Customer"),
                "billToSite": self._get_value(entry, "Bill to"),
                "shipToSite": self._get_value(entry, "Ship to"),
                "dueDateEpoch": self.date_to_epoch(self._get_value(entry, "Due Date", 0)),
                "notes": self._get_value(entry, "Notes"),
                "currency": self._get_value(entry, "Currency"),
                "paymentTerm": self._get_value(entry, "Payment Term") if "Payment Term" in entry else "",
                "invoiceLineDetails": [], 
                "accessIdentifierCodes": {}
            }

            num_lines = len(entry.get("Line", []))
            for i in range(num_lines):
                line_uuid = str(uuid.uuid4())
                tax_override_flag = self._get_value(entry, "Is tax overriden", i)
                tax_overridden_amount = self._get_value(entry, "Tax over ridden amount", i)

                tax_rule = {
                    "validationUUID": line_uuid,
                    "isTaxOverRidden": str(tax_override_flag).lower(),
                    "taxRuleName": self._get_value(entry, "Tax Rule", i)
                }

                if tax_rule["isTaxOverRidden"] == "true":
                    tax_rule["taxOverRiddenAmount"] = tax_overridden_amount

                line = {
                    "validationUUID": line_uuid,
                    "itemName": self._get_value(entry, "Item", i),
                    "description": self._get_value(entry, "Line Description", i),
                    "lineRuleName": self._get_value(entry, "Revenue Rule", i),
                    "uomName": self._get_value(entry, "UOM", i),
                    "quantity": self._get_value(entry, "Quantity", i),
                    "unitPrice": self._get_value(entry, "Unit Price", i),
                    "discountPercentage": self._get_value(entry, "Discount %", i),
                    "taxRules": [tax_rule],
                    "activeStatus": "ACTIVE"
                }

                payload["invoiceLineDetails"].append(line)

            payload["accessIdentifierCodes"] = {
                "coaCode": coa_code,
                "legalEntityCode": self._get_value(entry, "LEGAL_ENTITY"),
                "businessUnitCode": self._get_value(entry, "BUSINESS_UNIT"),
                "locationCode": self._get_value(entry, "LOCATION")
            }

            logger.info("AR Invoice: " + str(payload))

            payloads.append({
                "payload": payload,
                "legal_entity": self._get_value(entry, "LEGAL_ENTITY"),
                "invoice_number": self._get_value(entry, "Invoice Number"),
                "row_number": entry.get("row_number", [])
            })

        return payloads