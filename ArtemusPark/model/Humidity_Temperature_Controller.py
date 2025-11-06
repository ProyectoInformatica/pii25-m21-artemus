import random
import logging
# Logs
logging.basicConfig(
    filename='humidity_temperature_controller.log',
    level=logging.INFO,# Esto hay que cambiarlo por Debug pero me gusta más en INFO
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
# Clase de humedad y de temperatura
class Humidity_Temperature_Controller:
    def humidity(self):
        irrigation = False
        humidity = random.randint(0, 100)
        if humidity < 30.00:
            irrigation = True
            message = f"Humidity it is low {humidity}, we active the irrigation"

        elif humidity < 70.00:
            message = f"Humidity it is high {humidity}, we deactivated the irrigation"
        else:
            message = f"Humidity it is {humidity}"

        print(message)
        logging.info(message)

    def temperature(self):
        temperature = random.randint(-5, 40)
        if temperature > 30.00:
            message = f"The weather it is heat {temperature}º"
        elif temperature < 15.00:
            message = f"The weather it is cold {temperature}º"
        else:
            message = f"The weather it is {temperature}º"

        print(message)
        logging.info(message)
