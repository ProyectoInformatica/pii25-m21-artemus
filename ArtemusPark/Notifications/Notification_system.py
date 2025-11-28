import logging
from datetime import datetime
from typing import Callable, Dict, List

logging.basicConfig(
    filename="notifications.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)



class Notification:
    def __init__(self, source: str, level: str, message: str):
        self.source = source          # p.ej. "LightController"
        self.level = level            # "INFO", "WARNING", "HIGH", "LOW", etc.
        self.message = message
        self.timestamp = datetime.now()

    def __str__(self) -> str:
        # Formato legible para consola/log
        return f"[{self.timestamp}] [{self.source}] [{self.level}] {self.message}"



class NotificationSystem:
    def __init__(self):
        self._subscribers: Dict[str, List[Callable[[Notification], None]]] = {}

    def subscribe(self, event_type: str, callback: Callable[[Notification], None]) -> None:
        """event_type p.ej. 'LIGHT', 'HUMIDITY', 'TEMPERATURE'."""
        self._subscribers.setdefault(event_type, []).append(callback)

    def notify(self, event_type: str, notification: Notification) -> None:
        # Log global
        logging.info(str(notification))

        # Notificar suscriptores
        for callback in self._subscribers.get(event_type, []):
            try:
                callback(notification)
            except Exception:
                logging.exception("Error en callback de notificación")