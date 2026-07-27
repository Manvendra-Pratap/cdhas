from typing import Optional, Any
from pydantic import BaseModel, Field

class ErrorResponse(BaseModel):
    status_code: int = Field(..., example=404, description="HTTP status code")
    error_code: str = Field(..., example="SESSION_NOT_FOUND", description="Machine-readable error identifier")
    message: str = Field(..., example="Session with ID 'xyz' was not found", description="Human-readable error explanation")
    timestamp: str = Field(..., example="2026-07-27T16:00:00Z", description="ISO 8601 UTC timestamp when error occurred")
    details: Optional[Any] = Field(None, description="Detailed validation error list or diagnostic breakdown")
