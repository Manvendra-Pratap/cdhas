from datetime import datetime
from typing import Any, Optional, Dict
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from backend.utils.logger import get_logger

logger = get_logger("exceptions")

class CDHASBaseException(Exception):
    def __init__(self, message: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR, error_code: str = "INTERNAL_ERROR"):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(message)

class SessionNotFoundException(CDHASBaseException):
    def __init__(self, session_id: str):
        super().__init__(
            message=f"Session with ID '{session_id}' was not found in CDHAS telemetry database",
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="SESSION_NOT_FOUND"
        )

class DatabaseConnectionException(CDHASBaseException):
    def __init__(self, detail: str = "Database connection error"):
        super().__init__(
            message=detail,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            error_code="DATABASE_UNAVAILABLE"
        )

class InvalidFilterException(CDHASBaseException):
    def __init__(self, detail: str = "Invalid query filter parameters"):
        super().__init__(
            message=detail,
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="INVALID_FILTER"
        )

async def cdhas_exception_handler(request: Request, exc: CDHASBaseException):
    logger.warning(f"CDHAS Exception on {request.url.path}: {exc.message} (Code: {exc.error_code})")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status_code": exc.status_code,
            "error_code": exc.error_code,
            "message": exc.message,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    )

async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    logger.warning(f"HTTP Exception {exc.status_code} on {request.url.path}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status_code": exc.status_code,
            "error_code": "HTTP_ERROR",
            "message": exc.detail if isinstance(exc.detail, str) else "HTTP Request Error",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"Validation Error on {request.url.path}: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "status_code": 422,
            "error_code": "VALIDATION_ERROR",
            "message": "Invalid request parameters or payload format",
            "details": exc.errors(),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    )
