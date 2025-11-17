import random
import logging
import time

# Asumiendo que quieres que este archivo use un log diferente
logging.basicConfig(
    filename='doorModel.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


class DoorModel:
    """Modelo: simula sensores de puertas y usa el estado del controlador para detenerse."""

    # 1. Constructor para aceptar la referencia del controlador
    def __init__(self, controller_ref=None):
        self.controller_ref = controller_ref

    def door(self, name):
        """Simula lecturas de puerta (0=Cerrada, 1=Abierta)."""

        # El bucle verifica la bandera 'running' del controlador
        while self.controller_ref.running:
            if self.controller_ref.park_open:
                door_status = random.randint(0, 1)
                if door_status == 0:
                    message = f"[{name}] The door is close."
                else:
                    message = f"[{name}] The door is open."
            else:
                message = f"The park it is close."

            print(message)
            logging.info(message)
            time.sleep(5)

        print(f"[{name}] Hilo de puerta terminado.")