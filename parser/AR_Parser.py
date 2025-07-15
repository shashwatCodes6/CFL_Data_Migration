from parser.base_parser import BaseParser
from payload.AR_Invoice import ARInvoice

class ARInvoiceParser(BaseParser):
    def __init__(self, dataframe):
        self.df = dataframe

    def parse(self):
        if self.df.empty:
            raise ValueError("Sheet is empty.")
        
        df = self.df
        
        grouped = df.groupby(["Legal Entity", "Invoice Number"]).agg(list).reset_index()
        data = grouped.to_dict(orient="records")
        ARInvoicePayloadGen = ARInvoice()
        payload = ARInvoicePayloadGen.generate(data)

        return payload