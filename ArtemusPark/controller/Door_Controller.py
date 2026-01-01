import logging
import random
import time
from typing import Callable, Optional

from ArtemusPark.model.Door_Model import DoorModel

logging.basicConfig(
    filename="door_controller.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


class DoorController:
    """
    Controlador: ejecuta la lógica de sensores de puerta.
    Usa callbacks tipo on_new_data para entregar DoorModel al SensorController.
    """

    def __init__(
        self,
        controller_ref=None,
        on_new_data: Optional[Callable[[DoorModel], None]] = None,
    ):
        self.controller_ref = controller_ref  
        self.on_new_data = on_new_data  

    def run(self, name: str):
        """Bucle que simula el sensor de puerta."""

        while self.controller_ref.running:
            
            if not self.controller_ref.park_open:
                data = DoorModel(is_open=False, name=name)
                msg = f"[{name}] Park is CLOSED → Door forced CLOSED."
            else:
                
                is_open = bool(random.randint(0, 1))
                data = DoorModel(is_open=is_open, name=name)
                msg = f"[{name}] Door {'OPEN' if is_open else 'CLOSED'}"

            print(msg)
            logging.info(msg)

            if self.on_new_data:
                self.on_new_data(data)

            time.sleep(5)

        print(f"[{name}] Door thread stopped.")
