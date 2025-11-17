import logging
import random
import time
from typing import Callable, Optional

from ArtemusPark.model.Temperature_Model import TemperatureModel

logging.basicConfig(
    filename="temperature_controller.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


class TemperatureController:
    def __init__(self, on_new_data: Optional[Callable[[TemperatureModel], None]] = None):
        self.on_new_data = on_new_data

    def run(self, name):
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

            if self.on_new_data:
                self.on_new_data(data)

            time.sleep(1)