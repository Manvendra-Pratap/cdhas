import os
import asyncio
import threading
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import uvicorn

from backend.config import settings
from backend.routers import api_router, websocket_router
from backend.routers.health import get_health, get_status, get_metrics
from backend.middleware import RequestTimingMiddleware
from backend.security import RateLimitMiddleware, RequestSanitizerMiddleware
from backend.monitoring import ObservabilityLatencyMiddleware
from backend.realtime import background_worker
from backend.utils.exceptions import (
    CDHASBaseException,
    cdhas_exception_handler,
    http_exception_handler,
    validation_exception_handler,
)
from backend.utils.logger import get_logger

logger = get_logger("main")

tags_metadata = [
    {
        "name": "Authentication & Security",
        "description": "JWT authentication login, token refresh, logout, and user profile management.",
    },
    {
        "name": "Health Telemetry",
        "description": "API status checks, database connection verification, and backend latency metrics.",
    },
    {
        "name": "Dashboard Telemetry",
        "description": "Executive posture summary, geography distribution, temporal attack volume, and AI cluster intelligence.",
    },
    {
        "name": "Sessions Telemetry",
        "description": "Honeypot session explorer with multi-parameter search, instant pagination, and command telemetry.",
    },
    {
        "name": "ML & Behavioral Intelligence",
        "description": "Isolation Forest anomaly scores, K-Means behavioral clustering, and threat posture analytics.",
    },
    {
        "name": "Real-time WebSockets",
        "description": "Asynchronous WebSocket channels for real-time dashboard metrics, attack alerts, and live sessions stream.",
    },
]

app = FastAPI(
    title=settings.APP_TITLE,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    openapi_tags=tags_metadata,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Custom Exception Handlers
app.add_exception_handler(CDHASBaseException, cdhas_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

# Custom Observability & Security Middleware
app.add_middleware(ObservabilityLatencyMiddleware)
app.add_middleware(RateLimitMiddleware, requests_per_minute=settings.RATE_LIMIT_PER_MINUTE)
app.add_middleware(RequestSanitizerMiddleware, max_bytes=settings.MAX_REQUEST_SIZE_BYTES)
app.add_middleware(RequestTimingMiddleware)

# Enable CORS for frontend clients configured via settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Top-level Health & Observability Endpoints
app.add_api_route("/health", get_health, tags=["Health Telemetry"], methods=["GET"])
app.add_api_route("/status", get_status, tags=["Health Telemetry"], methods=["GET"])
app.add_api_route("/metrics", get_metrics, tags=["Health Telemetry"], methods=["GET"])

# Mount API & WebSocket Routers
app.include_router(api_router)
app.include_router(websocket_router)

bg_task = None

@app.on_event("startup")
async def startup_event():
    """Launch log watcher & real-time background worker tasks on startup."""
    global bg_task
    logger.info(f"Starting {settings.APP_TITLE} v{settings.APP_VERSION} with Observability & Structured Logging active.")

    # Launch Real-time background worker task
    bg_task = asyncio.create_task(background_worker.start())
    logger.info("Real-time background worker task spawned.")

    log_path = os.environ.get("CDHAS_COWRIE_LOG_PATH")
    if log_path and os.path.exists(os.path.dirname(log_path)):
        try:
            from backend.parser.log_watcher import start as start_watcher
            watcher_thread = threading.Thread(target=start_watcher, daemon=True)
            watcher_thread.start()
            logger.info(f"Log watcher started in background for path '{log_path}'")
        except Exception as err:
            logger.warning(f"Log watcher background start deferred: {err}")
    else:
        logger.info("CDHAS_COWRIE_LOG_PATH not specified or path unavailable; running with static/mongo telemetry.")

@app.on_event("shutdown")
async def shutdown_event():
    global bg_task
    logger.info("Shutting down CDHAS backend...")
    background_worker.stop()
    if bg_task:
        bg_task.cancel()
        try:
            await bg_task
        except asyncio.CancelledError:
            pass

@app.get("/", tags=["System Root"])
def root():
    return {
        "system": settings.APP_TITLE,
        "version": settings.APP_VERSION,
        "status": "online",
        "observability": "Structured Logging & Metrics Active",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
        "status_endpoint": "/status",
        "metrics": "/metrics",
        "websockets": [
            "ws://localhost:8000/ws/dashboard",
            "ws://localhost:8000/ws/alerts",
            "ws://localhost:8000/ws/sessions",
        ],
    }

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
