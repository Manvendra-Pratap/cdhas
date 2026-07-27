from typing import Optional
from fastapi import APIRouter, Query, status, Path
from backend.schemas.session import SessionSummary, SessionListResponse
from backend.schemas.error import ErrorResponse
from backend.services.session_service import filter_sessions, get_session_by_id

router = APIRouter(tags=["Sessions Telemetry"])

@router.get(
    "/sessions",
    response_model=SessionListResponse,
    status_code=status.HTTP_200_OK,
    summary="Search & Filter Honeypot Sessions",
    description="Retrieve paginated honeypot attack sessions with multi-parameter filtering across IP, Country, Severity, Protocol, Username, Archetype, Command strings, and Date ranges.",
    responses={
        200: {
            "description": "Paginated session list returned successfully."
        },
        400: {
            "model": ErrorResponse,
            "description": "Invalid filter timestamp or query parameter format."
        },
        422: {
            "model": ErrorResponse,
            "description": "Pagination parameters failed range validation constraints."
        }
    }
)
def get_sessions(
    page: int = Query(1, ge=1, description="Page index (1-based)"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page limit (1 to 100)"),
    ip: Optional[str] = Query(None, description="Global search term matching IP, country, username, or archetype"),
    country: Optional[str] = Query(None, description="Filter by origin country name or 2-letter ISO code"),
    severity: Optional[str] = Query(None, description="Filter by severity: Low, Medium, High, Critical, or All"),
    protocol: Optional[str] = Query(None, description="Filter by protocol: SSH, Telnet, HTTP"),
    username: Optional[str] = Query(None, description="Filter by attempted login username"),
    archetype: Optional[str] = Query(None, description="Filter by AI behavioral archetype classification"),
    command: Optional[str] = Query(None, description="Filter by command substring matching"),
    start_time: Optional[str] = Query(None, description="ISO 8601 start timestamp filter"),
    end_time: Optional[str] = Query(None, description="ISO 8601 end timestamp filter")
):
    return filter_sessions(
        page=page,
        page_size=page_size,
        ip=ip,
        country=country,
        severity=severity,
        protocol=protocol,
        username=username,
        archetype=archetype,
        command=command,
        start_time=start_time,
        end_time=end_time
    )

@router.get(
    "/sessions/{session_id}",
    response_model=SessionSummary,
    status_code=status.HTTP_200_OK,
    summary="Get Detailed Telemetry for a Single Session",
    description="Fetches full session details including command history, risk score, severity, and behavioral classification.",
    responses={
        200: {
            "description": "Session details found and returned."
        },
        404: {
            "model": ErrorResponse,
            "description": "Session ID not found in database."
        }
    }
)
def get_session(
    session_id: str = Path(..., min_length=1, max_length=64, description="Unique 8-character session identifier")
):
    return get_session_by_id(session_id)
