import threading
from ArtemusPark.model.Humidity_Temperature_Controller  import HumidityTemperatureController


class SensorController:

    def __init__(self):
        self.model = HumidityTemperatureController()
        self.running = False

    def start(self):
        self.running = True
        threading.Thread(target=self.model.humidity, daemon=True).start()
        threading.Thread(target=self.model.temperature, daemon=True).start()

    def stop(self):
        self.running = False
