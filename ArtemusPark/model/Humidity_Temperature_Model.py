import random
import logging
import time

logging.basicConfig(
    filename="humidity_temperature_controller.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


class HumidityTemperatureModel:
    """Modelo: simula sensores de humedad y temperatura."""

    # 1. Constructor para aceptar la referencia del controlador
    def __init__(self, controller_ref=None):
        self.controller_ref = controller_ref

    # La firma del método es simple: (self, name)
    def humidity(self, name):
        """Simula lecturas de humedad."""

        # El bucle verifica la bandera 'running' del controlador
        while self.controller_ref.running:
            humidity = random.randint(0, 100)

            if humidity < 30:
                message = (
                    f"[{name}] Humidity low ({humidity}%) → activating irrigation."
                )
            elif humidity < 70:
                message = f"[{name}] Humidity moderate ({humidity}%) → irrigation off."
            else:
                message = f"[{name}] Humidity high ({humidity}%) → irrigation off."

            print(message)
            logging.info(message)
            time.sleep(1)

        print(f"[{name}] Hilo de humedad terminado.")

    # La firma del método es simple: (self, name)
    def temperature(self, name):
        """Simula lecturas de temperatura."""

        # El bucle verifica la bandera 'running' del controlador
        while self.controller_ref.running:
            temperature = random.randint(-5, 40)

            if temperature > 30:
                message = f"[{name}] Hot weather ({temperature}°C)."
            elif temperature < 15:
                message = f"[{name}] Cold weather ({temperature}°C)."
            else:
                message = f"[{name}] Mild weather ({temperature}°C)."

            print(message)
            logging.info(message)
            time.sleep(1)

        print(f"[{name}] Hilo de temperatura terminado.")
