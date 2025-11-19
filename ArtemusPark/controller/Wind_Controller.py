import logging
import random
import time
from typing import Callable, Optional

from ArtemusPark.model.Wind_Model import WindModel
from ArtemusPark.config.wind_config import RISK_THRESHOLD_KMH, WARNING_THRESHOLD_KMH

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
    ):
        self.on_new_data = on_new_data
        self.risk_threshold_kmh = risk_threshold_kmh
        self.warning_threshold_kmh = warning_threshold_kmh

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

            if self.on_new_data:
                self.on_new_data(data)

            time.sleep(1)