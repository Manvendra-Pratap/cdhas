from typing import Dict, Any
from datetime import datetime
from backend.realtime.connection_manager import manager
from backend.utils.logger import get_logger

logger = get_logger("realtime.notification")

class RealtimeNotificationService:
    @staticmethod
    async def notify_new_session(session_data: Dict[str, Any]):
        logger.info(f"Broadcasting real-time new_session event for IP '{session_data.get('ip')}'")
        await manager.broadcast_event("new_session", session_data)

        severity = session_data.get("severity")
        score = session_data.get("score", 0.0)

        if severity == "Critical" or score >= 0.85:
            alert_payload = {
                "id": f"alert_{session_data.get('id')}_{int(datetime.utcnow().timestamp())}",
                "ip": session_data.get("ip"),
                "country": session_data.get("country"),
                "flag": session_data.get("flag"),
                "severity": "Critical",
                "archetype": session_data.get("archetype"),
                "time": datetime.utcnow().strftime("%H:%M:%S UTC"),
                "message": f"Critical attack vector detected from {session_data.get('ip')} ({session_data.get('country')})",
            }
            logger.warning(f"Broadcasting CRITICAL ATTACK ALERT for IP '{session_data.get('ip')}'")
            await manager.broadcast_event("critical_alert", alert_payload)
        elif severity == "High" or score >= 0.65:
            alert_payload = {
                "id": f"alert_{session_data.get('id')}_{int(datetime.utcnow().timestamp())}",
                "ip": session_data.get("ip"),
                "country": session_data.get("country"),
                "flag": session_data.get("flag"),
                "severity": "High",
                "archetype": session_data.get("archetype"),
                "time": datetime.utcnow().strftime("%H:%M:%S UTC"),
                "message": f"High severity attack detected from {session_data.get('ip')}",
            }
            await manager.broadcast_event("high_severity_attack", alert_payload)

    @staticmethod
    async def notify_dashboard_update(dashboard_data: Dict[str, Any]):
        await manager.broadcast_event("dashboard_update", dashboard_data)

    @staticmethod
    async def notify_timeline_update(timeline_data: Any):
        await manager.broadcast_event("timeline_update", {"timeline": timeline_data})

notification_service = RealtimeNotificationService()
