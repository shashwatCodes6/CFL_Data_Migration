import uuid
from datetime import datetime
import pandas as pd

class ARInvoice():
    def date_to_epoch(self, date_value):
        if pd.isna(date_value):
            return None
        return int(pd.to_datetime(date_value, dayfirst=True).timestamp() * 1000)  # milliseconds

    def generate(self, parsed_data):
        payloads = []
        print(parsed_data)

        for entry in parsed_data:
            validation_uuid = str(uuid.uuid4())

            # SEGMENTS
            segment_mapping = {
                "LEGAL_ENTITY": "Legal Entity",
                "BUSINESS_UNIT": "Business Unit",
                "LOCATION": "Location",
                "INTERCOMPANY_CODE": "Inter Company",
                "MISCELLANEOUS1_CODE": "Miscellaneous",
                "MISCELLANEOUS2_CODE": "Cost Centre",
                "MISCELLANEOUS3_CODE": "Service",
                "MISCELLANEOUS4_CODE": "Analysis",
                "MISCELLANEOUS5_CODE": "null",
                "MISCELLANEOUS6_CODE": "null",
                "MISCELLANEOUS7_CODE": "null",
                "MISCELLANEOUS8_CODE": "null",
                "MISCELLANEOUS9_CODE": "null",
                "MISCELLANEOUS10_CODE": "null"
            }


            segments = []
            for segment_name, column_name in segment_mapping.items():
                if column_name != "null":
                    code_value = entry.get(segment_name, [""])[0]
                    print(segment_name, code_value)
                    if code_value:
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
                "invoiceLineDetails": []
            }

            # MULTIPLE LINE HANDLING
            num_lines = len(entry.get("Item", []))
            for i in range(num_lines):
                line_uuid = str(uuid.uuid4())
                tax_override_flag = entry.get("Is tax overriden", ["false"] * num_lines)[i]
                tax_overridden_amount = entry.get("Tax over ridden amount", [""] * num_lines)[i]

                tax_rule = {
                    "validationUUID": line_uuid,
                    "isTaxOverRidden": tax_override_flag == "TRUE",
                    "taxRuleName": entry.get("Tax Rule", [""])[i]
                }

                # Only add override amount if overridden
                if tax_rule["isTaxOverRidden"]:
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

            payloads.append(payload)

        return payloads
