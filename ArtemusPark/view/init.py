import time
from ArtemusPark.controller.init import SensorController


controller = SensorController()
controller.start()

try:
    print("Sensores activos... presiona Ctrl + C para detener.")
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    controller.stop()
    print("Programa detenido.")
