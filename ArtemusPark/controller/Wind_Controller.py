import logging
import random
import time
from typing import Callable, Optional

from ArtemusPark.model.Wind_Model import WindModel

logging.basicConfig(
    filename="wind_controller.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


class WindController:
    def __init__(self, on_new_data: Optional[Callable[[WindModel], None]] = None):
        self.on_new_data = on_new_data

    def run(self, name: str):
        """
        Emulate an anemometer (wind speed in km/h).

            0–20  → SAFE
            21–40 → WARNING
            >40   → DANGER
        """
        while True:
            speed = random.randint(0, 60)

            if speed <= 20:
                state = "SAFE"
                label = "Safe wind"
            elif speed <= 40:
                state = "WARNING"
                label = "Wind – caution"
            else:
                state = "DANGER"
                label = "Danger! Strong wind"

            data = WindModel(speed=speed, state=state, label=label)

            msg = f"[{name}] {speed} km/h - {state} ({label})"
            print(msg)
            logging.info(msg)

            if self.on_new_data:
                self.on_new_data(data)

            time.sleep(1)
