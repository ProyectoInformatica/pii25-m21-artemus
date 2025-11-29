import logging
from datetime import datetime
from typing import Callable, Dict, List

from ArtemusPark.controller.Door_Controller import DoorController
from ArtemusPark.controller.Humidity_Controller import HumidityController
from ArtemusPark.controller.Light_Controller import LightController
from ArtemusPark.controller.Temperature_Controller import TemperatureController
from ArtemusPark.controller.Wind_Controller import WindController

logging.basicConfig(
    filename="notifications.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


class Notification:
    def __init__(self, source: str, level: str, message: str):
        self.source = source
        self.level = level
        self.message = message
        self.timestamp = datetime.now()

    def __str__(self) -> str:
        # Formato legible para consola/log
        return f"[{self.timestamp}] [{self.source}] [{self.level}] {self.message}"


class NotificationSystem:
    def __init__(self):
        self._subscribers: Dict[str, List[Callable[[Notification], None]]] = {}

    def subscribe(
        self, event_type: str, callback: Callable[[Notification], None]
    ) -> None:
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


from ArtemusPark.Notifications.Notification_system import NotificationSystem


class SensorController:
    OPEN_HOUR = 9
    CLOSE_HOUR = 18

    def __init__(self):
        # Sistema de notificaciones compartido
        self.notification_system = NotificationSystem()

        # General state
        self.running = False
        self.park_open = False
        self.simulated_hour = 8

        # Historias...

        self.humidity_controller = HumidityController(
            on_new_data=self._on_humidity,
            notification_system=self.notification_system,
        )
        self.temperature_controller = TemperatureController(
            on_new_data=self._on_temperature,
            notification_system=self.notification_system,
        )
        self.wind_controller = WindController(
            on_new_data=self._on_wind,
            notification_system=self.notification_system,
        )
        self.door_controller = DoorController(
            controller_ref=self,
            on_new_data=self._on_door,
            # opcional: también podrías pasar notification_system aquí
        )
        self.light_controller = LightController(
            controller_ref=self,
            on_new_data=self._on_light,
            notification_system=self.notification_system,
        )
