import logging

from offline_pipeline.config import LOG_FILE

LOGGER_NAME = "offline_pipeline"

logger = logging.getLogger(LOGGER_NAME)

logger.setLevel(logging.INFO)

logger.handlers.clear()

formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(message)s"
)

# Console

console_handler = logging.StreamHandler()

console_handler.setFormatter(formatter)

# File

file_handler = logging.FileHandler(
    LOG_FILE,
    encoding="utf-8"
)

file_handler.setFormatter(formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)
