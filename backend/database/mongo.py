from pymongo import MongoClient, ASCENDING, DESCENDING
from backend.config import settings
from backend.utils.logger import get_logger

logger = get_logger("database")

try:
    _client = MongoClient(settings.MONGO_URI, serverSelectionTimeoutMS=400, connectTimeoutMS=400)
    _db = _client[settings.DB_NAME]
    logger.info(f"Initialized MongoDB connection client for DB: '{settings.DB_NAME}' at {settings.MONGO_URI}")
except Exception as err:
    logger.error(f"Failed to initialize MongoDB client: {err}")
    _client = None
    _db = None

def get_collection():
    if _db is None:
        raise RuntimeError("MongoDB client is uninitialized")
    return _db[settings.COLLECTION_NAME]

def check_mongo_health() -> bool:
    try:
        col = get_collection()
        col.command("ping")
        return True
    except Exception as err:
        logger.debug(f"MongoDB ping health check failed: {err}")
        return False

def ensure_db_indexes():
    """Ensure database indexes exist for timestamp, country, source_ip, session_id, severity, and protocol."""
    try:
        if not check_mongo_health():
            return
        col = get_collection()
        indexes = [
            [("timestamp", DESCENDING)],
            [("country", ASCENDING)],
            [("source_ip", ASCENDING)],
            [("session_id", ASCENDING)],
            [("severity", ASCENDING)],
            [("protocol", ASCENDING)],
        ]
        for idx in indexes:
            col.create_index(idx, background=True)
        logger.info("MongoDB indexes created/verified for timestamp, country, source_ip, session_id, severity, protocol.")
    except Exception as err:
        logger.debug(f"Index creation deferred (MongoDB offline or uninitialized): {err}")
