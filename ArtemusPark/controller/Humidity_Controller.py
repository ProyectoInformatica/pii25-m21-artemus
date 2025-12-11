import logging
import random
import time
from typing import Callable, Optional

from model.Humidity_Model import HumidityModel

logging.basicConfig(
    filename="humidity_controller.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


class HumidityController:
    def __init__(self, on_new_data: Optional[Callable[[HumidityModel], None]] = None):
        self.on_new_data = on_new_data

    def run(self, name):
        while True:
            value = random.randint(0, 100)

            if value < 30:
                status = "LOW"
                msg = f"[{name}] Low humidity ({value}%) → irrigation ON"
            elif value < 70:
                status = "NORMAL"
                msg = f"[{name}] Normal humidity ({value}%) → irrigation OFF"
            else:
                status = "HIGH"
                msg = f"[{name}] High humidity ({value}%) → irrigation OFF"

            data = HumidityModel(value=value, status=status)
            print(msg)
            logging.info(msg)

            if self.on_new_data:
                self.on_new_data(data)

            time.sleep(1)
