import logging
import random
import time
from typing import Callable, Optional

from ArtemusPark.model.Wind_Model import WindModel
from ArtemusPark.config.Wind_Config import RISK_THRESHOLD_KMH, WARNING_THRESHOLD_KMH
from ArtemusPark.Notifications.Notification_system import (
    NotificationSystem,
    Notification,
)

logging.basicConfig(
    filename="wind_controller.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


class WindController:
    def __init__(
        self,
        on_new_data: Optional[Callable[[WindModel], None]] = None,
        risk_threshold_kmh: int = RISK_THRESHOLD_KMH,
        warning_threshold_kmh: int = WARNING_THRESHOLD_KMH,
        notification_system: Optional[NotificationSystem] = None,
    ):
        self.on_new_data = on_new_data
        self.risk_threshold_kmh = risk_threshold_kmh
        self.warning_threshold_kmh = warning_threshold_kmh
        self.notification_system = notification_system

    def _notify_wind(self, speed: int, state: str, label: str, sensor_name: str) -> None:
        if not self.notification_system:
            return

        if state == "DANGER":
            level = "HIGH"
        elif state == "WARNING":
            level = "WARNING"
        else:
            level = "INFO"

        msg = f"[{sensor_name}] {speed} km/h - {state} ({label})"
        notification = Notification(
            source="WindController",
            level=level,
            message=msg,
        )
        self.notification_system.notify("WIND", notification)

    def run(self, name: str):
        """
        Emulate an anemometer (wind speed in km/h).
        """
        while True:
            speed = random.randint(0, 60)

            if speed <= self.warning_threshold_kmh:
                state = "SAFE"
                label = "Safe wind"
            elif speed <= self.risk_threshold_kmh:
                state = "WARNING"
                label = "Wind – caution"
            else:
                state = "DANGER"
                label = "Danger! Strong wind"

            data = WindModel(speed=speed, state=state, label=label)

            msg = f"[{name}] {speed} km/h - {state} ({label})"
            print(msg)
            logging.info(msg)

            # Notificación
            self._notify_wind(speed, state, label, name)

            if self.on_new_data:
                try:
                    self.on_new_data(data)
                except Exception:
                    logging.exception("Error in on_new_data callback")

            time.sleep(1)
