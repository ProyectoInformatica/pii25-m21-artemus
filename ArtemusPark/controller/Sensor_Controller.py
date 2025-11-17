import threading
import time
import random
# IMPORTA TUS MODELOS (ajusta la ruta si es necesario)
from ArtemusPark.model.Humidity_Temperature_Model import HumidityTemperatureModel
from ArtemusPark.model.DoorModel import DoorModel


class SensorController:
    # Definir el horario de operación del parque (Horas simuladas)
    OPEN_HOUR = 9
    CLOSE_HOUR = 18

    def __init__(self):
        self.running = False
        self.park_open = False  # Estado de apertura del parque (Cerrado por defecto)
        self.simulated_hour = 8  # Hora simulada inicial (8:00 AM)
        self.model = HumidityTemperatureModel(controller_ref=self)
        self.door_model = DoorModel(controller_ref=self)

    def simulate_time_and_status(self):
        """Función que corre en un hilo para simular el paso del tiempo y cambiar el estado del parque."""

        while self.running:
            is_open_time = self.OPEN_HOUR <= self.simulated_hour < self.CLOSE_HOUR
            if is_open_time and not self.park_open:
                self.park_open = True
                print(f"\n--- PARQUE ABIERTO a las {self.simulated_hour}:00 ---")
            elif not is_open_time and self.park_open:
                self.park_open = False
                print(f"\n--- PARQUE CERRADO a las {self.simulated_hour}:00 ---")
            print(f"[Hora Simulada: {self.simulated_hour}:00] Parque {'ABIERTO' if self.park_open else 'CERRADO'}")

            self.simulated_hour += 1
            if self.simulated_hour >= 24:
                self.simulated_hour = 0

            time.sleep(1)

    def start(self):
        self.running = True
        sens = 5
        doorsens = 2

        print("--- Iniciando Sensores y Reloj de Parque ---")

        threading.Thread(target=self.simulate_time_and_status, daemon=True).start()

        for i in range(sens):
            sensor_num = i + 1
            threading.Thread(target=self.model.humidity, daemon=True,args=(f"HumiditySens{sensor_num}",)).start()
            threading.Thread(target=self.model.temperature, daemon=True, args=(f"TempSens{sensor_num}",)).start()

        for i in range(doorsens):
            sensor_num = i + 1
            threading.Thread(target=self.door_model.door, daemon=True,
                             args=(f"DoorSens{sensor_num}",)).start()

        print("Sensores activos. Usa Ctrl+C para detener.")

    def stop(self):
        print("\n--- Petición de Parada Recibida. Esperando a que los hilos terminen... ---")
        self.running = False
        time.sleep(6)
        print("Controlador y hilos terminados.")


if __name__ == '__main__':
    controller = SensorController()

    try:
        controller.start()
        # Mantiene el hilo principal vivo
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        # Permite detener la ejecución con Ctrl+C
        controller.stop()