import logging
from backend.logging_config import get_channel_logger

def get_logger(name: str = "api") -> logging.Logger:
    """Helper function to obtain named channel loggers (api, database, errors, security, performance)."""
    return get_channel_logger(name)
