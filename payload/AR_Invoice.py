class ARInvoice():
    def generate(self, parsed_data):
        res = []
        
        for entry in parsed_data:
            res.append({
                "Legal Entity": entry["Legal Entity"],
                "Invoice Number": entry["Invoice Number"],
                "Line": entry["Line"]
            })

        return res