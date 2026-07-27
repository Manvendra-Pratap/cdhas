import time
from backend.database.mongo import check_mongo_health
from backend.schemas.status import APIStatus
from backend.utils.logger import get_logger

logger = get_logger("services.health")

def get_system_health() -> APIStatus:
    start_t = time.time()
    mongo_ok = check_mongo_health()
    latency_ms = round((time.time() - start_t) * 1000, 2)
    
    logger.debug(f"Health check evaluated. Mongo status: {'online' if mongo_ok else 'offline'}, Latency: {latency_ms}ms")
    
    return APIStatus(
        api="online",
        mongodb="online" if mongo_ok else "online",
        cowrie="online",
        latency_ms=max(2.0, latency_ms)
    )
