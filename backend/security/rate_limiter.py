import time
from typing import Dict, Tuple
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from backend.config import settings
from backend.utils.logger import get_logger

logger = get_logger("security.ratelimit")

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, requests_per_minute: int = 120):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        # Maps client IP -> (request_count, window_start_timestamp)
        self.clients: Dict[str, Tuple[int, float]] = {}

    async def dispatch(self, request: Request, call_next):
        # Skip rate-limiting for static assets or documentation
        if request.url.path in ("/docs", "/redoc", "/openapi.json", "/favicon.ico"):
            return await call_next(request)

        client_ip = request.client.host if request.client else "127.0.0.1"
        now = time.time()

        if client_ip in self.clients:
            count, start_time = self.clients[client_ip]
            if now - start_time > 60:
                # Reset window
                self.clients[client_ip] = (1, now)
            else:
                if count >= self.requests_per_minute:
                    logger.warning(f"Rate limit exceeded for IP '{client_ip}' on endpoint '{request.url.path}'")
                    return JSONResponse(
                        status_code=429,
                        content={
                            "status_code": 429,
                            "error_code": "RATE_LIMIT_EXCEEDED",
                            "message": "Too many requests. Rate limit exceeded. Please try again later.",
                            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                        }
                    )
                self.clients[client_ip] = (count + 1, start_time)
        else:
            self.clients[client_ip] = (1, now)

        response = await call_next(request)
        return response
