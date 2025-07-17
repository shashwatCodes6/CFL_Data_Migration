from parser.base_parser import BaseParser
from payload.Masters_Party import MasterPartyPayload

class MasterPartyParser(BaseParser):
    def __init__(self, dataframe):
        self.df = dataframe

    def parse(self):
        if self.df.empty:
            raise ValueError("Sheet is empty.")
        
        df = self.df
        
        data = df.to_dict(orient="records")
        
        payload_gen = MasterPartyPayload()
        
        payload = payload_gen.generate(data)
        
        return payload