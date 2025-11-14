import random
import logging
import time

logging.basicConfig(
    filename='humidity_temperature_controller.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


class HumidityTemperatureModel:
    """Modelo: simula sensores de humedad y temperatura."""

    def humidity(self):
        while True:
            humidity = random.randint(0, 100)

            if humidity < 30:
                message = f"Humidity low ({humidity}%) → activating irrigation."
            elif humidity < 70:
                message = f"Humidity moderate ({humidity}%) → irrigation off."
            else:
                message = f"Humidity high ({humidity}%) → irrigation off."

            print(message)
            logging.info(message)
            time.sleep(1)  # espera 10 segundos antes de repetir

    def temperature(self):
        while True:
            temperature = random.randint(-5, 40)

            if temperature > 30:
                message = f"Hot weather ({temperature}°C)."
            elif temperature < 15:
                message = f"Cold weather ({temperature}°C)."
            else:
                message = f"Mild weather ({temperature}°C)."

            print(message)
            logging.info(message)
            time.sleep(1)
