import pandas as pd

class BaseParser:
    def __init__(self, file_path):
        self.file_path = file_path

    def read_excel(self):
        return pd.read_excel(self.file_path, header=0, engine='openpyxl')

    def parse(self):
        raise NotImplementedError("Subclasses must implement the parse method.")
