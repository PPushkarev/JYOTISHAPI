import logging
import sys
from pathlib import Path

# Define the path for logs (at the project root)
BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True) # Create the directory if it doesn't exist

def setup_logging():
    logger = logging.getLogger("astro_api")
    logger.setLevel(logging.INFO)

    # Log format: Timestamp - Name - Level - Message
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # 1. Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 2. File handler
    file_handler = logging.FileHandler(LOG_DIR / "api.log", encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

# Create the logger instance
logger = setup_logging()