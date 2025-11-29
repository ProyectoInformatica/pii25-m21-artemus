import logging
import random
import time
from typing import Callable, Optional

from ArtemusPark.model.Temperature_Model import TemperatureModel
from ArtemusPark.Notifications.Notification_system import (
    NotificationSystem,
    Notification,
)

logging.basicConfig(
    filename="temperature_controller.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


class TemperatureController:
    def __init__(
        self,
        on_new_data: Optional[Callable[[TemperatureModel], None]] = None,
        notification_system: Optional[NotificationSystem] = None,
    ):
        self.on_new_data = on_new_data
        self.notification_system = notification_system

    def _notify_temperature(self, value: int, status: str, sensor_name: str) -> None:
        if not self.notification_system:
            return

        if value <= 0 or value >= 35:
            level = "HIGH"
        elif value < 15 or value > 30:
            level = "WARNING"
        else:
            level = "INFO"

        msg = f"[{sensor_name}] Temperatura {status} ({value}°C)"
        notification = Notification(
            source="TemperatureController",
            level=level,
            message=msg,
        )
        self.notification_system.notify("TEMPERATURE", notification)

    def run(self, name: str):
        while True:
            value = random.randint(-5, 40)

            if value > 30:
                status = "HOT"
                msg = f"[{name}] Hot weather ({value}°C)"
            elif value < 15:
                status = "COLD"
                msg = f"[{name}] Cold weather ({value}°C)"
            else:
                status = "MILD"
                msg = f"[{name}] Mild weather ({value}°C)"

            data = TemperatureModel(value=value, status=status)
            print(msg)
            logging.info(msg)

            # Notificación
            self._notify_temperature(value, status, name)

            if self.on_new_data:
                try:
                    self.on_new_data(data)
                except Exception:
                    logging.exception("Error in on_new_data callback")

            time.sleep(1)
