from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from backend.realtime.connection_manager import manager
from backend.services.session_service import get_dashboard_data
from backend.utils.logger import get_logger

router = APIRouter(prefix="/ws", tags=["Real-time WebSockets"])
logger = get_logger("routers.websocket")

@router.websocket("/dashboard")
async def websocket_dashboard(websocket: WebSocket):
    """
    WebSocket endpoint streaming live dashboard metric updates, geography summaries, and timeline feeds.
    """
    await manager.connect(websocket, "dashboard")
    try:
        # Send initial state snapshot on connection
        initial_data = get_dashboard_data()
        payload = initial_data.model_dump() if hasattr(initial_data, "model_dump") else initial_data
        await websocket.send_json({"event": "dashboard_snapshot", "data": payload})

        while True:
            # Keep connection alive & listen for client ping/messages
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(websocket, "dashboard")
    except Exception as err:
        logger.warning(f"Error on /ws/dashboard connection: {err}")
        manager.disconnect(websocket, "dashboard")

@router.websocket("/alerts")
async def websocket_alerts(websocket: WebSocket):
    """
    WebSocket endpoint streaming live high severity attacks and critical alert notifications.
    """
    await manager.connect(websocket, "alerts")
    try:
        await websocket.send_json({
            "event": "alert_channel_ready",
            "message": "Connected to CDHAS Real-time Critical Alert Broadcast Channel"
        })
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(websocket, "alerts")
    except Exception as err:
        logger.warning(f"Error on /ws/alerts connection: {err}")
        manager.disconnect(websocket, "alerts")

@router.websocket("/sessions")
async def websocket_sessions(websocket: WebSocket):
    """
    WebSocket endpoint streaming live incoming session records as honeypots capture attacks.
    """
    await manager.connect(websocket, "sessions")
    try:
        await websocket.send_json({
            "event": "session_channel_ready",
            "message": "Connected to CDHAS Real-time Live Session Feed Channel"
        })
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(websocket, "sessions")
    except Exception as err:
        logger.warning(f"Error on /ws/sessions connection: {err}")
        manager.disconnect(websocket, "sessions")
