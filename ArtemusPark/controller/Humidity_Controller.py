import logging
import random
import time
from typing import Callable, Optional

from ArtemusPark.model.Humidity_Model import HumidityModel
from ArtemusPark.Notifications.Notification_system import (
    NotificationSystem,
    Notification,
)

logging.basicConfig(
    filename="humidity_controller.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


class HumidityController:
    def __init__(
        self,
        on_new_data: Optional[Callable[[HumidityModel], None]] = None,
        notification_system: Optional[NotificationSystem] = None,
    ):
        self.on_new_data = on_new_data
        self.notification_system = notification_system

    def _notify_humidity(self, value: int, status: str, sensor_name: str) -> None:
        if not self.notification_system:
            return

        if value < 30:
            level = "LOW"
        elif value > 70:
            level = "HIGH"
        else:
            level = "INFO"

        msg = f"[{sensor_name}] Humedad {status} ({value}\\%)"
        notification = Notification(
            source="HumidityController",
            level=level,
            message=msg,
        )
        self.notification_system.notify("HUMIDITY", notification)

    def run(self, name: str):
        while True:
            value = random.randint(0, 100)

            if value < 30:
                status = "LOW"
                msg = f"[{name}] Humidity low ({value}\\%)"
            elif value > 70:
                status = "HIGH"
                msg = f"[{name}] Humidity high ({value}\\%)"
            else:
                status = "NORMAL"
                msg = f"[{name}] Humidity normal ({value}\\%)"

            data = HumidityModel(value=value, status=status)
            print(msg)
            logging.info(msg)

            # Notificación
            self._notify_humidity(value, status, name)

            if self.on_new_data:
                try:
                    self.on_new_data(data)
                except Exception:
                    logging.exception("Error in on_new_data callback")

            time.sleep(1)
