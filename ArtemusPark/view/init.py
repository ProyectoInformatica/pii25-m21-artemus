import time
from controller.Sensor_Controller import SensorController

controller = SensorController()
controller.start()

try:
    print("Sensores activos... presiona Ctrl + C para detener.")
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    controller.stop()
    print("Programa detenido.")
