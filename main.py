import os
import glob
import json
from utils.config_loader import load_config
from utils.logger import get_logger
from parser.invoice_parser import InvoiceParser
from parser.employee_parser import EmployeeParser
from payload.payload_builder import build_payload
from api.client import post_payload

logger = get_logger()
config = load_config()

PARSER_MAP = {
    "invoice": InvoiceParser,
    "employee": EmployeeParser,
}

def detect_parser(file_path):
    """Detect parser based on filename or config logic."""
    if "invoice" in file_path.lower():
        return PARSER_MAP["invoice"]
    elif "employee" in file_path.lower():
        return PARSER_MAP["employee"]
    else:
        raise ValueError(f"No parser defined for: {file_path}")

def main():
    input_dir = config["paths"]["input_dir"]
    output_dir = config["paths"]["output_dir"]

    os.makedirs(output_dir, exist_ok=True)
    
    files = glob.glob(os.path.join(input_dir, "*.xlsx"))
    for file_path in files:
        try:
            logger.info(f"Processing file: {file_path}")
            parser_class = detect_parser(file_path)
            parser = parser_class(file_path)
            parsed_data = parser.parse()
            
            payload = build_payload(parsed_data)
            
            # Save to file
            output_file = os.path.join(output_dir, os.path.basename(file_path).replace(".xlsx", ".json"))
            with open(output_file, "w") as f:
                json.dump(payload, f, indent=2)
            
            logger.info(f"Saved JSON to {output_file}")

            # # Optional: send to API
            # if config["api"]["enabled"]:
            #     response = post_payload(payload)
            #     logger.info(f"API response: {response.status_code} - {response.text}")

        except Exception as e:
            logger.error(f"Failed processing {file_path}: {str(e)}")

if __name__ == "__main__":
    main()
