import os
import logging
from logging.handlers import RotatingFileHandler
from backend.config import settings

LOG_DIR = settings.LOG_DIR
os.makedirs(LOG_DIR, exist_ok=True)

# Define separate log file paths
LOG_FILES = {
    "api": os.path.join(LOG_DIR, "api.log"),
    "database": os.path.join(LOG_DIR, "database.log"),
    "errors": os.path.join(LOG_DIR, "errors.log"),
    "security": os.path.join(LOG_DIR, "security.log"),
    "performance": os.path.join(LOG_DIR, "performance.log"),
}

LOG_FORMAT = logging.Formatter(
    "[%(asctime)s] [%(levelname)s] [%(name)s] [%(filename)s:%(lineno)d] - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

handlers: dict = {}

def get_channel_logger(name: str = "api") -> logging.Logger:
    """Returns or configures a logger for specific channels (api, database, errors, security, performance)."""
    channel = name.split(".")[0].lower()
    if channel not in LOG_FILES:
        channel = "api"

    logger = logging.getLogger(f"cdhas.{channel}")
    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))

    if not logger.handlers:
        # Rotating File Handler (5 MB per file, max 3 backups)
        file_handler = RotatingFileHandler(
            LOG_FILES[channel],
            maxBytes=5 * 1024 * 1024,
            backupCount=3,
            encoding="utf-8"
        )
        file_handler.setFormatter(LOG_FORMAT)
        file_handler.setLevel(logging.INFO)
        logger.addHandler(file_handler)

        # Stream Handler (Console output)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(LOG_FORMAT)
        console_handler.setLevel(logging.INFO)
        logger.addHandler(console_handler)

        # For error log channel, also attach errors file handler
        if channel == "errors":
            err_handler = RotatingFileHandler(
                LOG_FILES["errors"],
                maxBytes=5 * 1024 * 1024,
                backupCount=3,
                encoding="utf-8"
            )
            err_handler.setFormatter(LOG_FORMAT)
            err_handler.setLevel(logging.ERROR)
            logger.addHandler(err_handler)

    return logger
