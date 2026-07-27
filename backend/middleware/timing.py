import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from backend.utils.logger import get_logger

logger = get_logger("middleware.timing")

class RequestTimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        process_time_ms = round(process_time * 1000, 2)

        response.headers["X-Process-Time"] = f"{process_time_ms}ms"

        logger.info(
            f"HTTP {request.method} '{request.url.path}' -> {response.status_code} ({process_time_ms}ms)"
        )

        return response
