import pandas as pd

class BaseParser:
    def __init__(self, file_path):
        self.file_path = file_path
        
    def parse(self):
        raise NotImplementedError("Subclasses must implement the parse method.")
