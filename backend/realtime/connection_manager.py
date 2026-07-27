import json
from typing import Dict, List, Set, Any
from fastapi import WebSocket
from backend.utils.logger import get_logger

logger = get_logger("realtime.manager")

class ConnectionManager:
    def __init__(self):
        # Maps channel name ('dashboard', 'alerts', 'sessions') to set of connected WebSockets
        self.channels: Dict[str, Set[WebSocket]] = {
            "dashboard": set(),
            "alerts": set(),
            "sessions": set(),
        }

    async def connect(self, websocket: WebSocket, channel: str):
        await websocket.accept()
        if channel not in self.channels:
            self.channels[channel] = set()
        self.channels[channel].add(websocket)
        logger.info(f"WebSocket connected to channel '{channel}'. Total clients on '{channel}': {len(self.channels[channel])}")

    def disconnect(self, websocket: WebSocket, channel: str):
        if channel in self.channels and websocket in self.channels[channel]:
            self.channels[channel].remove(websocket)
            logger.info(f"WebSocket disconnected from channel '{channel}'. Remaining clients on '{channel}': {len(self.channels[channel])}")

    async def broadcast_to_channel(self, channel: str, message: Dict[str, Any]):
        if channel not in self.channels or not self.channels[channel]:
            return

        payload = json.dumps(message)
        stale_connections: List[WebSocket] = []

        for connection in list(self.channels[channel]):
            try:
                await connection.send_text(payload)
            except Exception as err:
                logger.warning(f"Failed to send to client on channel '{channel}' ({err}). Marking for disconnection.")
                stale_connections.append(connection)

        for connection in stale_connections:
            self.disconnect(connection, channel)

    async def broadcast_event(self, event_type: str, data: Dict[str, Any]):
        """Broadcast formatted event to appropriate channels."""
        event_message = {
            "event": event_type,
            "data": data,
        }

        if event_type in ("dashboard_update", "timeline_update"):
            await self.broadcast_to_channel("dashboard", event_message)
        elif event_type in ("new_session", "session_update"):
            await self.broadcast_to_channel("sessions", event_message)
            await self.broadcast_to_channel("dashboard", event_message)
        elif event_type in ("critical_alert", "high_severity_attack"):
            await self.broadcast_to_channel("alerts", event_message)
            await self.broadcast_to_channel("dashboard", event_message)
            await self.broadcast_to_channel("sessions", event_message)

manager = ConnectionManager()
