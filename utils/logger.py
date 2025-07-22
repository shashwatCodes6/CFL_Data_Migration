import logging
import os
from datetime import datetime
import time
import json
import threading

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
    def __init__(self, file_name, flush_interval_seconds=10, max_buffer_size=100):
        self.logger = get_logger()
        self.file_name = file_name
        self.file_path = os.path.join("data/responses", self.file_name)
        self._log_buffer = []
        self._lock = threading.Lock()  # For thread-safe access to buffer
        self._flush_interval_seconds = flush_interval_seconds
        self._max_buffer_size = max_buffer_size
        self._flush_thread = None
        self._running = False

        os.makedirs("data/responses", exist_ok=True)
        # Initialize with existing data if any
        if os.path.exists(self.file_path):
            with open(self.file_path, "r", encoding="utf-8") as f:
                try:
                    existing_data = json.load(f)
                    # We only load existing data on startup. New logs will be appended to buffer.
                    # If you need to *also* preserve old data and new data in the same file,
                    # you'll need to decide how to merge or keep them distinct.
                    # For simplicity here, assume _log_buffer starts fresh for *new* entries.
                    # A more robust solution might load existing_data into _log_buffer initially.
                except json.JSONDecodeError:
                    pass # File exists but is empty or malformed, start with empty buffer

    def start_auto_flush(self):
        """Starts a background thread to automatically flush the buffer."""
        if not self._running:
            self._running = True
            self._flush_thread = threading.Thread(target=self._auto_flush_loop, daemon=True)
            self._flush_thread.start()

    def stop_auto_flush(self):
        """Stops the background flush thread and performs a final flush."""
        if self._running:
            self._running = False
            if self._flush_thread:
                self._flush_thread.join() # Wait for the flush thread to finish
            self.flush() # Perform a final flush

    def _auto_flush_loop(self):
        """The loop for the background flush thread."""
        while self._running:
            time.sleep(self._flush_interval_seconds)
            self.flush()

    def save_log_entry(self, log_entry_dict):
        """Adds a log entry to the in-memory buffer."""
        log_entry_dict["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self._lock:
            self._log_buffer.append(log_entry_dict)
            if len(self._log_buffer) >= self._max_buffer_size:
                self.flush() # Flush immediately if buffer size limit is reached

    def flush(self):
        """Writes the current buffer content to the file."""
        if not self._log_buffer:
            return

        with self._lock:
            entries_to_write = list(self._log_buffer) # Take a copy
            self._log_buffer.clear() # Clear the buffer

        # Read existing data to append to it
        existing_data = []
        if os.path.exists(self.file_path):
            with open(self.file_path, "r", encoding="utf-8") as f:
                try:
                    existing_data = json.load(f)
                except json.JSONDecodeError:
                    pass # File exists but is empty or malformed

        existing_data.extend(entries_to_write)

        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(existing_data, f, indent=2)
        print(f"Flushed {len(entries_to_write)} entries to {self.file_path}")


    def info(self, msg):
        self.logger.info(msg)

    def warn(self, msg):
        self.logger.warning(msg)

    def error(self, msg):
        self.logger.error(msg)

    def debug(self, msg):
        self.logger.debug(msg)
