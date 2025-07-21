import logging
import os
from datetime import datetime
import json

_LOGGER = None  # Singleton logger instance

def get_logger(log_dir="data/logs"):
    global _LOGGER
    if _LOGGER:
        return _LOGGER

    os.makedirs(log_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = os.path.join(log_dir, f"log_{timestamp}.log")

    logger = logging.getLogger("CFLLogger")
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        # File handler
        file_handler = logging.FileHandler(log_filename)
        file_handler.setLevel(logging.DEBUG)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # Formatter
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    _LOGGER = logger
    return _LOGGER


class CustomLogger:
    def __init__(self):
        self.logger = get_logger()

    def save_log_entry(self, file_name, log_entry_dict):
        """Save or append a JSON dict to a JSON array in the response file"""
        os.makedirs("data/responses", exist_ok=True)
        file_path = os.path.join("data/responses", file_name)

        # Read existing data if file exists
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                try:
                    existing_data = json.load(f)
                except json.JSONDecodeError:
                    existing_data = []
        else:
            existing_data = []

        # Append new entry with timestamp
        log_entry_dict["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        existing_data.append(log_entry_dict)

        # Write updated list back to file
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(existing_data, f, indent=2)

    def info(self, msg):
        self.logger.info(msg)

    def warn(self, msg):
        self.logger.warning(msg)

    def error(self, msg):
        self.logger.error(msg)

    def debug(self, msg):
        self.logger.debug(msg)
