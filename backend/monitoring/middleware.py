import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from backend.monitoring.metrics import metrics_collector
from backend.utils.logger import get_logger

perf_logger = get_logger("performance")

class ObservabilityLatencyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        latency_ms = round((time.time() - start_time) * 1000, 2)

        # Record metrics
        metrics_collector.record_request(latency_ms)

        # Log slow requests (> 500ms) to performance channel log (logs/performance.log)
        if latency_ms > 500.0:
            perf_logger.warning(
                f"SLOW REQUEST WARNING: HTTP {request.method} '{request.url.path}' -> {response.status_code} "
                f"took {latency_ms}ms (Threshold: 500ms)"
            )
        else:
            perf_logger.info(f"HTTP {request.method} '{request.url.path}' -> {response.status_code} ({latency_ms}ms)")

        return response
