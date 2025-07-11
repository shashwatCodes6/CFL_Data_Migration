from parser.base_parser import BaseParser

class ARParser(BaseParser):
    def parse(self):
        df = self.read_excel()
        df.columns = df.iloc[0]          
        df = df.drop(df.index[0])   
        df.reset_index(drop=True, inplace=True)

        # grouped = df.groupby("InvoiceID").agg(list).reset_index()

        # data = []
        # for _, row in grouped.iterrows():
        #     item = {
        #         "invoice_id": row["InvoiceID"],
        #         "amounts": row["Amount"],
        #         "dates": row["Date"],
        #         # Add more fields
        #     }
        #     data.append(item)
        
        # return data
