"""
CDHAS REST API Router Module
Backwards-compatibility interface exporting the aggregated APIRouter.
"""
from backend.routers import api_router as router
from backend.services.session_service import fetch_sessions_from_db, filter_sessions, get_session_by_id, get_dashboard_data
from backend.models.constants import FALLBACK_SESSIONS

__all__ = ["router", "fetch_sessions_from_db", "filter_sessions", "get_session_by_id", "get_dashboard_data", "FALLBACK_SESSIONS"]
