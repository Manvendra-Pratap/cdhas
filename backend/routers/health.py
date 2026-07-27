from fastapi import APIRouter, status
from backend.config import settings
from backend.schemas.status import APIStatus
from backend.schemas.observability import HealthResponse, StatusResponse, MetricsResponse
from backend.services.health_service import get_system_health
from backend.monitoring.metrics import metrics_collector
from backend.database.mongo import check_mongo_health

router = APIRouter(tags=["Health Telemetry"])

@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Get System Component Health Status",
    description="Returns backend API latency along with connection state for MongoDB and Cowrie honeypot sensors.",
)
def get_health():
    health = get_system_health()
    return HealthResponse(
        api=health.api,
        mongodb=health.mongodb,
        cowrie=health.cowrie,
        latency_ms=health.latency_ms
    )

@router.get(
    "/status",
    response_model=StatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Application Uptime & Status",
    description="Returns application status, version, and formatted uptime duration.",
)
def get_status():
    return StatusResponse(
        status="online",
        version=settings.APP_VERSION,
        uptime_seconds=metrics_collector.get_uptime_seconds(),
        uptime_human=metrics_collector.get_formatted_uptime()
    )

@router.get(
    "/metrics",
    response_model=MetricsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Detailed Performance & System Metrics",
    description="Returns memory footprint, CPU utilization, request volume, average response latency, and slow request metrics.",
)
def get_metrics():
    mongo_status = "online" if check_mongo_health() else "offline"
    return MetricsResponse(
        api_status="online",
        mongodb_connectivity=mongo_status,
        cowrie_watcher_status="online",
        memory_usage_mb=metrics_collector.get_memory_usage_mb(),
        cpu_usage_percent=metrics_collector.get_cpu_usage_percent(),
        application_uptime_seconds=metrics_collector.get_uptime_seconds(),
        application_uptime_human=metrics_collector.get_formatted_uptime(),
        request_count=metrics_collector.request_count,
        average_response_time_ms=metrics_collector.get_average_response_time(),
        slow_request_count=metrics_collector.slow_request_count
    )
