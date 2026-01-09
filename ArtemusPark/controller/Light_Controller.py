import logging
import time
from datetime import datetime
from typing import Callable, Optional

from ArtemusPark.model.Light_Model import LightModel

logging.basicConfig(
    filename="light_controller.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


class LightController:
    def __init__(
        self,
        controller_ref=None,
        on_new_data: Optional[Callable[[LightModel], None]] = None,
    ):
        self.controller_ref = controller_ref
        self.on_new_data = on_new_data

    def run(self, name: str):
        """
        Simula el sensor/controlador de luz.
        Lógica: Las luces se encienden entre 19:00 y 07:00 (hora real).
        """

        while self.controller_ref.running:
            current_hour = datetime.now().hour

            should_be_on = current_hour >= 19 or current_hour < 7

            status = "ON" if should_be_on else "OFF"
            value = 100 if should_be_on else 0

            data = LightModel(is_on=should_be_on, status=status, value=value)

            msg = f"[{name }] Light {status } (Real Hour: {current_hour })"
            print(msg)
            logging.info(msg)

            if self.on_new_data:
                self.on_new_data(data)

            time.sleep(1)
