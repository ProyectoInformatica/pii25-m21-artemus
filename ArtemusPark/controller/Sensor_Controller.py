import threading
from typing import List, Optional

from ArtemusPark.controller.Humidity_Controller import HumidityController
from ArtemusPark.controller.Temperature_Controller import TemperatureController
from ArtemusPark.controller.Wind_Controller import WindController
from ArtemusPark.model.Humidity_Model import HumidityModel
from ArtemusPark.model.Temperature_Model import TemperatureModel
from ArtemusPark.model.Wind_Model import WindModel


class SensorController:

    def __init__(self):
        self.humidity_history: List[HumidityModel] = []
        self.temperature_history: List[TemperatureModel] = []
        self.wind_history: List[WindModel] = []

        self.humidity_controller = HumidityController(on_new_data=self._on_humidity)
        self.temperature_controller = TemperatureController(on_new_data=self._on_temperature)
        self.wind_controller = WindController(on_new_data=self._on_wind)

    def _on_humidity(self, data: HumidityModel):
        self.humidity_history.append(data)

    def _on_temperature(self, data: TemperatureModel):
        self.temperature_history.append(data)

    def _on_wind(self, data: WindModel):
        self.wind_history.append(data)

    def start(self):
        num_sensors = 5

        for i in range(num_sensors):
            threading.Thread(
                target=self.humidity_controller.run,
                daemon=True,
                args=(f"Humidity {i + 1}",)   # 👈 tupla
            ).start()

            threading.Thread(
                target=self.temperature_controller.run,
                daemon=True,
                args=(f"Temperature {i + 1}",)  # 👈 tupla
            ).start()

            threading.Thread(
                target=self.wind_controller.run,
                daemon=True,
                args=(f"Wind {i + 1}",)   # 👈 tupla
            ).start()

    def latest_humidity(self) -> Optional[HumidityModel]:
        return self.humidity_history[-1] if self.humidity_history else None

    def latest_temperature(self) -> Optional[TemperatureModel]:
        return self.temperature_history[-1] if self.temperature_history else None

    def latest_wind(self) -> Optional[WindModel]:
        return self.wind_history[-1] if self.wind_history else None