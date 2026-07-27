from fastapi import APIRouter, status
from backend.schemas.dashboard import DashboardResponse
from backend.services.session_service import get_dashboard_data

router = APIRouter(tags=["Dashboard Telemetry"])

@router.get(
    "/dashboard",
    response_model=DashboardResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Aggregated SOC Dashboard Telemetry",
    description="Returns executive metrics, top source countries, 24-hour attack timelines, behavioral threat intelligence clusters, and sensor health.",
    responses={
        200: {
            "description": "Dashboard telemetry snapshot compiled successfully.",
            "content": {
                "application/json": {
                    "example": {
                        "overview": {
                            "generatedAt": "2026-07-27T16:00:00Z",
                            "metrics": [
                                {"label": "Observed sessions", "value": "1,248", "change": "+18.4%", "tone": "blue", "icon": "◫"}
                            ],
                            "geography": [
                                {"country": "Germany", "code": "DE", "sessions": 126, "color": "#6fd6aa"}
                            ]
                        },
                        "timeline": [{"time": "14:00", "sessions": 89, "anomalies": 8}],
                        "sessions": [],
                        "intelligence": [],
                        "health": {"api": "online", "mongodb": "online", "cowrie": "online", "latency_ms": 4.12}
                    }
                }
            }
        }
    }
)
def get_dashboard():
    return get_dashboard_data()
