from pydantic import BaseModel, Field

class HealthResponse(BaseModel):
    api: str = Field("online", example="online", description="API Status: online, degraded, offline")
    mongodb: str = Field("online", example="online", description="MongoDB Connectivity: online or offline")
    cowrie: str = Field("online", example="online", description="Cowrie log watcher status")
    latency_ms: float = Field(..., example=2.45, description="Backend ping latency in milliseconds")

class StatusResponse(BaseModel):
    status: str = Field("online", example="online")
    version: str = Field("1.0.0", example="1.0.0")
    uptime_seconds: float = Field(..., example=3600.5)
    uptime_human: str = Field(..., example="1h 0m 0s")

class MetricsResponse(BaseModel):
    api_status: str = Field("online", example="online")
    mongodb_connectivity: str = Field("online", example="online")
    cowrie_watcher_status: str = Field("online", example="online")
    memory_usage_mb: float = Field(..., example=54.2, description="Process Working Set Memory in MB")
    cpu_usage_percent: float = Field(..., example=1.4, description="CPU utilization percentage")
    application_uptime_seconds: float = Field(..., example=3600.5, description="Total application uptime in seconds")
    application_uptime_human: str = Field(..., example="1h 0m 0s", description="Formatted uptime string")
    request_count: int = Field(..., example=1240, description="Total HTTP requests served since startup")
    average_response_time_ms: float = Field(..., example=14.2, description="Average response latency across all endpoints")
    slow_request_count: int = Field(..., example=2, description="Requests taking > 500ms")
