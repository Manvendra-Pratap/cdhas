import asyncio
from datetime import datetime
from backend.database.mongo import get_collection, check_mongo_health
from backend.services.session_service import get_dashboard_data
from backend.realtime.notification_service import notification_service
from backend.utils.logger import get_logger

logger = get_logger("realtime.worker")

class RealtimeBackgroundWorker:
    def __init__(self, refresh_interval: int = 5):
        self.refresh_interval = refresh_interval
        self.is_running = False
        self.last_seen_id = None

    async def start(self):
        self.is_running = True
        logger.info(f"Starting Real-time Background Worker (polling interval: {self.refresh_interval}s)...")
        
        # Try MongoDB Change Stream listener first
        try:
            if check_mongo_health():
                col = get_collection()
                # Check if replica set supports watch()
                with col.watch(max_await_time_ms=1000) as stream:
                    logger.info("MongoDB Change Stream listener established successfully.")
                    for change in stream:
                        if not self.is_running:
                            break
                        full_doc = change.get("fullDocument", {})
                        if full_doc:
                            await notification_service.notify_new_session(full_doc)
        except Exception as err:
            logger.info(f"MongoDB Change Stream unavailable ({err}). Switching to efficient polling fallback worker.")

        # Polling loop fallback & periodic dashboard update broadcaster
        while self.is_running:
            try:
                await asyncio.sleep(self.refresh_interval)
                
                # Fetch fresh dashboard data & broadcast updates
                dash_data = get_dashboard_data()
                dash_dict = dash_data.model_dump() if hasattr(dash_data, "model_dump") else dash_data

                await notification_service.notify_dashboard_update(dash_dict)
                await notification_service.notify_timeline_update(dash_dict.get("timeline", []))

                # Check for new sessions
                sessions = dash_dict.get("sessions", [])
                if sessions:
                    newest = sessions[0]
                    newest_id = newest.get("id")
                    if self.last_seen_id and newest_id != self.last_seen_id:
                        logger.info(f"Detected new incoming session '{newest_id}' from IP '{newest.get('ip')}'")
                        await notification_service.notify_new_session(newest)
                    self.last_seen_id = newest_id

            except asyncio.CancelledError:
                logger.info("Real-time Background Worker task cancelled.")
                break
            except Exception as err:
                logger.warning(f"Error in background worker loop: {err}")

    def stop(self):
        self.is_running = False
        logger.info("Stopped Real-time Background Worker.")

background_worker = RealtimeBackgroundWorker(refresh_interval=5)
