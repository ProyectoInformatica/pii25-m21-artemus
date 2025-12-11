import logging
import time
from datetime import datetime
from typing import Callable, Optional

from model.Light_Model import LightModel

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
        Simulates a light sensor/controller.
        Logic: Lights turn ON between 19:00 and 07:00 based on SIMULATED time.
        """
        # Si no hay referencia, no podemos leer la hora simulada, así que fallamos o usamos hora real
        if not self.controller_ref:
            logging.error(
                "LightController needs controller_ref to read simulated time."
            )
            return

        while self.controller_ref.running:
            # Check SIMULATED time from the main controller
            current_hour = self.controller_ref.simulated_hour

            # Logic: ON between 19:00 and 07:00
            should_be_on = current_hour >= 19 or current_hour < 7

            status = "ON" if should_be_on else "OFF"
            value = 100 if should_be_on else 0

            data = LightModel(is_on=should_be_on, status=status, value=value)

            msg = f"[{name}] Light {status} (Simulated Hour: {current_hour})"
            print(msg)
            logging.info(msg)

            if self.on_new_data:
                self.on_new_data(data)

            time.sleep(1)
