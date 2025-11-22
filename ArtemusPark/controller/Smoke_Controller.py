import logging
import random
import time
from typing import Callable, Optional

from ArtemusPark.model.Smoke_Model import SmokeModel

# Configuración del log específica para el controlador de humo
logging.basicConfig(
    filename="smoke_controller.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


class SmokeController:
    def __init__(self, on_new_data: Optional[Callable[[SmokeModel], None]] = None):
        self.on_new_data = on_new_data

    def run(self, name):
        while True:
            # Simulamos un valor de densidad de humo entre 0 y 100
            # En un escenario real, esto vendría del hardware del sensor
            value = random.randint(0, 100)

            # Lógica de umbrales para el humo
            if value > 95:
                status = "ALARM"
                msg = f"[{name}]  CRITICAL: Fire detected! ({value} density)"
            elif value > 40:
                status = "WARNING"
                msg = f"[{name}]  Warning: Smoke detected ({value} density)"
            else:
                status = "CLEAR"
                msg = f"[{name}] Air is clear ({value} density)"

            # Crear la instancia del modelo
            data = SmokeModel(value=value, status=status)

            # Imprimir y guardar en log
            print(msg)
            logging.info(msg)

            # Ejecutar callback si existe (útil para enviar datos a un servicio)
            if self.on_new_data:
                self.on_new_data(data)

            time.sleep(1)
