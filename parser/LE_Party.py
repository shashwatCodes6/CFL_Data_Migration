from parser.base_parser import BaseParser
from payload.LEParty import LEPartyPayload

class LEPartyParser(BaseParser):
    def __init__(self, dataframe):
        self.df = dataframe

    def parse(self):
        if self.df.empty:
            raise ValueError("Sheet is empty.")
        
        df = self.df
        
        data = df.to_dict(orient="records")
        
        payload_gen = LEPartyPayload()
        
        payload = payload_gen.generate(data)
        
        return payload