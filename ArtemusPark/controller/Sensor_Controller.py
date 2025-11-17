import threading
import time
from typing import List, Optional

from ArtemusPark.controller.Humidity_Controller import HumidityController
from ArtemusPark.controller.Temperature_Controller import TemperatureController
from ArtemusPark.controller.Wind_Controller import WindController
from ArtemusPark.model.Humidity_Model import HumidityModel
from ArtemusPark.model.Temperature_Model import TemperatureModel
from ArtemusPark.model.Wind_Model import WindModel
from ArtemusPark.model.DoorModel import DoorModel


class SensorController:
    # Horario del parque
    OPEN_HOUR = 9
    CLOSE_HOUR = 18

    def __init__(self):
        # Estado general
        self.running = False
        self.park_open = False          # Parque cerrado por defecto
        self.simulated_hour = 8         # Hora simulada inicial (8:00)

        # Históricos de sensores (nueva arquitectura)
        self.humidity_history: List[HumidityModel] = []
        self.temperature_history: List[TemperatureModel] = []
        self.wind_history: List[WindModel] = []

        # Controllers de sensores (nueva arquitectura)
        self.humidity_controller = HumidityController(on_new_data=self._on_humidity)
        self.temperature_controller = TemperatureController(
            on_new_data=self._on_temperature
        )
        self.wind_controller = WindController(on_new_data=self._on_wind)

        # Modelo de puertas (versión antigua, referencia al controller)
        self.door_model = DoorModel(controller_ref=self)

    # ---------- CALLBACKS DE DATOS (nueva arquitectura) ---------- #

    def _on_humidity(self, data: HumidityModel):
        self.humidity_history.append(data)

    def _on_temperature(self, data: TemperatureModel):
        self.temperature_history.append(data)

    def _on_wind(self, data: WindModel):
        self.wind_history.append(data)

    # ---------- SIMULACIÓN DE TIEMPO Y ESTADO DEL PARQUE ---------- #

    def simulate_time_and_status(self):
        """Hilo que simula la hora y el estado ABIERTO/CERRADO del parque."""
        while self.running:
            is_open_time = self.OPEN_HOUR <= self.simulated_hour < self.CLOSE_HOUR

            if is_open_time and not self.park_open:
                self.park_open = True
                print(f"\n--- PARQUE ABIERTO a las {self.simulated_hour}:00 ---")
            elif not is_open_time and self.park_open:
                self.park_open = False
                print(f"\n--- PARQUE CERRADO a las {self.simulated_hour}:00 ---")

            print(
                f"[Hora Simulada: {self.simulated_hour}:00] "
                f"Parque {'ABIERTO' if self.park_open else 'CERRADO'}"
            )

            # Avanzar hora simulada
            self.simulated_hour += 1
            if self.simulated_hour >= 24:
                self.simulated_hour = 0

            time.sleep(1)

    # ---------- ARRANQUE / PARADA DE SENSORES ---------- #

    def start(self):
        self.running = True

        num_sensors = 5     # humedad / temperatura / viento
        door_sensors = 2    # número de sensores de puerta

        print("--- Iniciando Sensores y Reloj de Parque ---")

        # Hilo de reloj y estado del parque
        threading.Thread(
            target=self.simulate_time_and_status,
            daemon=True
        ).start()

        # Sensores de humedad, temperatura y viento
        for i in range(num_sensors):
            sensor_num = i + 1

            threading.Thread(
                target=self.humidity_controller.run,
                daemon=True,
                args=(f"HumiditySens{sensor_num}",),
            ).start()

            threading.Thread(
                target=self.temperature_controller.run,
                daemon=True,
                args=(f"TempSens{sensor_num}",),
            ).start()

            threading.Thread(
                target=self.wind_controller.run,
                daemon=True,
                args=(f"WindSens{sensor_num}",),
            ).start()

        # Sensores de puertas (siguen usando DoorModel)
        for i in range(door_sensors):
            sensor_num = i + 1
            threading.Thread(
                target=self.door_model.door,
                daemon=True,
                args=(f"DoorSens{sensor_num}",),
            ).start()

        print("Sensores activos.")

    def stop(self):
        print(
            "\n--- Petición de Parada Recibida. Esperando a que los hilos terminen... ---"
        )
        self.running = False
        # Los hilos de sensores tienen bucles infinitos, así que aquí de momento
        # solo damos un pequeño margen por si alguno chequea flags internos.
        time.sleep(6)
        print("Controlador y hilos terminados.")

    # ---------- MÉTODOS DE CONSULTA (para UI / API) ---------- #

    def latest_humidity(self) -> Optional[HumidityModel]:
        return self.humidity_history[-1] if self.humidity_history else None

    def latest_temperature(self) -> Optional[TemperatureModel]:
        return self.temperature_history[-1] if self.temperature_history else None

    def latest_wind(self) -> Optional[WindModel]:
        return self.wind_history[-1] if self.wind_history else None
