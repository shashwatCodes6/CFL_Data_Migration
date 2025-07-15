from parser.base_parser import BaseParser
from payload.AP_Invoice import APInvoice

class APCreditNoteParser(BaseParser):
    def __init__(self, dataframe):
        self.df = dataframe

    def parse(self):
        if self.df.empty:
            raise ValueError("Sheet is empty.")
        
        df = self.df
        
        grouped = df.groupby(["LEGAL_ENTITY", "Invoice Number"]).agg(list).reset_index()
        data = grouped.to_dict(orient="records")
        ARInvoicePayloadGen = APInvoice()
        payload = ARInvoicePayloadGen.generate(data)

        return payload