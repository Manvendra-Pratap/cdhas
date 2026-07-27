from fastapi import APIRouter
from backend.routers.health import router as health_router
from backend.routers.dashboard import router as dashboard_router
from backend.routers.sessions import router as sessions_router
from backend.routers.intelligence import router as intelligence_router
from backend.routers.websocket import router as websocket_router
from backend.routers.auth import router as auth_router

api_router = APIRouter(prefix="/api")
api_router.include_router(health_router)
api_router.include_router(dashboard_router)
api_router.include_router(sessions_router)
api_router.include_router(intelligence_router)
api_router.include_router(auth_router)

__all__ = [
    "api_router",
    "health_router",
    "dashboard_router",
    "sessions_router",
    "intelligence_router",
    "websocket_router",
    "auth_router",
]
