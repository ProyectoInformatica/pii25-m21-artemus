import logging
import threading
import time
from typing import List, Optional

from ArtemusPark.controller.Humidity_Controller import HumidityController
from ArtemusPark.controller.Temperature_Controller import TemperatureController
from ArtemusPark.controller.Wind_Controller import WindController
from ArtemusPark.controller.Door_Controller import DoorController
from ArtemusPark.controller.Light_Controller import LightController

from ArtemusPark.model.Humidity_Model import HumidityModel
from ArtemusPark.model.Temperature_Model import TemperatureModel
from ArtemusPark.model.Wind_Model import WindModel
from ArtemusPark.model.Door_Model import DoorModel
from ArtemusPark.model.Light_Model import LightModel

from ArtemusPark.repository.Wind_Repository import save_wind_measurement
from ArtemusPark.service.Wind_Risk_Service import check_wind_risk

from ArtemusPark.repository.Humidity_Repository import save_humidity_measurement
from ArtemusPark.repository.Temperature_Repository import save_temperature_measurement
from ArtemusPark.repository.Door_Repository import save_door_event
from ArtemusPark.repository.Light_Repository import save_light_event


logger = logging.getLogger(__name__)


class SensorController:
    # Park schedule
    OPEN_HOUR = 9
    CLOSE_HOUR = 18

    def __init__(self):
        # General state
        self.running = False
        self.park_open = False  # Park closed by default
        self.simulated_hour = 8  # Initial simulated hour (8:00)

        # Sensor histories
        self.humidity_history: List[HumidityModel] = []
        self.temperature_history: List[TemperatureModel] = []
        self.wind_history: List[WindModel] = []
        self.door_history: List[DoorModel] = []
        self.light_history: List[LightModel] = []

        # Sensor controllers
        self.humidity_controller = HumidityController(on_new_data=self._on_humidity)
        self.temperature_controller = TemperatureController(
            on_new_data=self._on_temperature
        )
        self.wind_controller = WindController(on_new_data=self._on_wind)
        self.door_controller = DoorController(
            controller_ref=self, on_new_data=self._on_door
        )

        # AQUÍ ESTÁ EL CAMBIO: Pasamos controller_ref=self
        self.light_controller = LightController(
            controller_ref=self, on_new_data=self._on_light
        )

    # ---------- DATA CALLBACKS ---------- #

    def _on_humidity(self, data: HumidityModel):
        self.humidity_history.append(data)
        save_humidity_measurement(data)

    def _on_temperature(self, data: TemperatureModel):
        self.temperature_history.append(data)
        save_temperature_measurement(data)

    def _on_wind(self, data: WindModel):
        """
        Called automatically by WindController when a new wind measurement arrives.

        Responsibilities:
        - Store measurement in history
        - Persist measurement to JSON "database"
        - Check against risk threshold
        - Trigger automatic alert if above limit
        """
        # 1) Store in memory history
        self.wind_history.append(data)

        # 2) Persist to JSON (repository)
        save_wind_measurement(data)

        # 3) Check risk level
        risk_result = check_wind_risk(data)

        # 4) Trigger alert if risky
        if risk_result.is_risky:
            alert_msg = f"[ALERT] {risk_result.message}"
            print(alert_msg)
            logger.warning(alert_msg)

            # TODO (future):
            # - Notify Flet UI
            # - Activate LEDs / buzzer
            # - Send notification to cloud / dashboard

    def _on_door(self, data: DoorModel):
        self.door_history.append(data)
        save_door_event(data)

    def _on_light(self, data: LightModel):
        self.light_history.append(data)
        save_light_event(data)

    # ---------- TIME SIMULATION AND PARK STATUS ---------- #

    def simulate_time_and_status(self):
        """Thread that simulates hour and park OPEN/CLOSED status."""
        while self.running:
            is_open_time = self.OPEN_HOUR <= self.simulated_hour < self.CLOSE_HOUR

            if is_open_time and not self.park_open:
                self.park_open = True
                print(f"\n--- PARK OPEN at {self.simulated_hour}:00 ---")
            elif not is_open_time and self.park_open:
                self.park_open = False
                print(f"\n--- PARK CLOSED at {self.simulated_hour}:00 ---")

            print(
                f"[Simulated Time: {self.simulated_hour}:00] "
                f"Park {'OPEN' if self.park_open else 'CLOSED'}"
            )

            # Advance simulated hour
            self.simulated_hour += 1
            if self.simulated_hour >= 24:
                self.simulated_hour = 0

            time.sleep(1)

    # ---------- START / STOP SENSORS ---------- #

    def start(self):
        self.running = True

        num_sensors = 5  # humidity / temperature / wind sensors
        num_light_sensors = 5  # light sensors
        door_sensors = 2  # number of door sensors

        print("--- Starting Sensors and Park Clock ---")

        # Time + park status thread
        threading.Thread(target=self.simulate_time_and_status, daemon=True).start()

        # Humidity, temperature, wind and light sensors
        for i in range(num_sensors):
            sensor_num = i + 1

            # threading.Thread(
            #     target=self.humidity_controller.run,
            #     daemon=True,
            #     args=(f"HumiditySens{sensor_num}",),
            # ).start()
            #
            # threading.Thread(
            #     target=self.temperature_controller.run,
            #     daemon=True,
            #     args=(f"TempSens{sensor_num}",),
            # ).start()
            #
            # threading.Thread(
            #     target=self.wind_controller.run,
            #     daemon=True,
            #     args=(f"WindSens{sensor_num}",),
            # ).start()

        # Light sensors
        for i in range(num_light_sensors):
            sensor_num = i + 1
            threading.Thread(
                target=self.light_controller.run,
                daemon=True,
                args=(f"LightSens{sensor_num}",),
            ).start()

        # Door sensors
        for i in range(door_sensors):
            sensor_num = i + 1
            threading.Thread(
                target=self.door_controller.run,
                daemon=True,
                args=(f"DoorSens{sensor_num}",),
            ).start()

        print("Sensors are now active.")

    def stop(self):
        print("\n--- Stop request received. Waiting for threads to finish... ---")
        self.running = False
        # Sensor threads have infinite loops; for now we just give them some time
        # in case they check internal flags.
        time.sleep(6)
        print("Controller and threads stopped.")

    # ---------- QUERY METHODS (for UI / API) ---------- #

    def latest_humidity(self) -> Optional[HumidityModel]:
        return self.humidity_history[-1] if self.humidity_history else None

    def latest_temperature(self) -> Optional[TemperatureModel]:
        return self.temperature_history[-1] if self.temperature_history else None

    def latest_wind(self) -> Optional[WindModel]:
        return self.wind_history[-1] if self.wind_history else None

    def latest_light(self) -> Optional[LightModel]:
        return self.light_history[-1] if self.light_history else None