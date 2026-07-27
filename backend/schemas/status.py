from pydantic import BaseModel, Field

class APIStatus(BaseModel):
    api: str = Field("online", example="online", description="REST API service status")
    mongodb: str = Field("online", example="online", description="MongoDB connection status")
    cowrie: str = Field("online", example="online", description="Cowrie honeypot sensor status")
    latency_ms: float = Field(..., example=4.52, description="Backend response latency in milliseconds")
