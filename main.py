import os
import glob
import json
from utils.config_loader import load_config
from parser.AR_Parser import ARInvoiceParser
from parser.AP_Invoice import APInvoiceParser
from parser.AP_Credit_Note import APCreditNoteParser
from parser.AR_Credit_Note import ARCreditNoteParser
from utils.logger import get_logger
from parser.Masters_Party import MasterPartyParser
from parser.LE_Party import LEPartyParser
from parser.base_parser import BaseParser
import pandas as pd

config = load_config()
logger = get_logger()

PARSER_MAP = {
    "AR_Invoice": ARInvoiceParser,
    "AR_Credit Note": ARCreditNoteParser,
    "AP_Invoice": APInvoiceParser,
    "AP_Credit Note": APCreditNoteParser,
    "Masters_Party": MasterPartyParser,
    "LE_Party": LEPartyParser
}

def detect_parser_by_sheet(sheet_name):
    for keyword, parser_class in PARSER_MAP.items():
        if keyword in sheet_name:
            return parser_class
    return None


def detect_parser(file_path) -> BaseParser | ValueError:
    """Detect parser based on filename or config logic."""
    if "AR" in file_path:
        return PARSER_MAP["AR"]
    else:
        raise ValueError(f"No parser defined for: {file_path}")

def main():
    input_dir = config["paths"]["input_dir"]
    output_dir = config["paths"]["output_dir"]

    os.makedirs(output_dir, exist_ok=True)

    for file_name in os.listdir(input_dir):
        if not file_name.endswith(".xlsx"):
            continue

        file_path = os.path.join(input_dir, file_name)
        logger.info(f"Opening Excel file: {file_path}")

        try:
            # Get sheet names first
            xl = pd.ExcelFile(file_path, engine="openpyxl")
            sheet_names = xl.sheet_names

            for sheet_name in sheet_names:
                logger.info(f"Processing sheet: {sheet_name}")
                parser_class = detect_parser_by_sheet(sheet_name)

                if not parser_class:
                    logger.warning(f"No parser found for sheet: {sheet_name}")
                    continue

                df = xl.parse(sheet_name, dtype=str)
                if df.empty:
                    logger.warning(f"Skipping empty sheet: {sheet_name}")
                    continue

                df['row_number'] = df.index    # for indexing the row number of the entry 
                df.columns = df.columns.str.strip()

                parser = parser_class(df)
                parsed_data = parser.parse()

                output_file = os.path.join(
                    output_dir,
                    f"{os.path.splitext(file_name)[0]}_{sheet_name}.json"
                )

                with open(output_file, "w") as f:
                    json.dump(parsed_data, f, indent=2)
                logger.info(f"Saved payload to: {output_file}")


        except Exception as e:
            logger.error(f"Failed processing {file_path}: {str(e)}")


if __name__ == "__main__":
    main()
