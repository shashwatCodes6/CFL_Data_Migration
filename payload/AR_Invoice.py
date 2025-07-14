class ARInvoice():
    def generate(self, parsed_data):
        res = []

        for entry in parsed_data:
            try:
                res.append({
                    "Legal Entity": str(entry["Legal Entity"]),
                    "Invoice Number": str(entry["Invoice Number"]),
                    "Line": [str(i) for i in entry["Line"]],
                    "Transaction Source": str(entry["Transaction Source"][0]),
                })
            except Exception as e:
                print(f"Exception {e} on record {entry["Legal Entity"]}, {entry["Invoice Number"]}")

        print ("Hello world")
        return res