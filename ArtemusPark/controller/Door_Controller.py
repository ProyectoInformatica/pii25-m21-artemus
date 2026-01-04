import logging
import random
import time
from typing import Callable, Optional

from ArtemusPark.model.Door_Model import DoorModel
from ArtemusPark.repository.Auth_Repository import AuthRepository
from ArtemusPark.config.Sensor_Config import SENSOR_CONFIG

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
        
        self.auth_repo = AuthRepository()
        self.users_list = list(self.auth_repo.get_all_users().keys())

    def run(self, sensor_id: str):
        """Bucle que simula el sensor de puerta."""
        readable_name = sensor_id
        for sensor in SENSOR_CONFIG.get("door", []):
            if sensor["id"] == sensor_id:
                readable_name = sensor["name"]
                break

        while self.controller_ref.running:
            if not self.controller_ref.park_open:
                msg = f"[{readable_name}] Park is CLOSED. Door activity is suspended."
                print(msg)
                logging.info(msg)
                time.sleep(5)
                continue
            else:
                is_open = bool(random.randint(0, 1))
                direction = "IN" if random.random() < 0.6 else "OUT"
                sim_user = random.choice(self.users_list) if self.users_list else "unknown"

                data = DoorModel(
                    is_open=is_open,
                    sensor_id=sensor_id,
                    name=readable_name,
                    direction=direction,
                    username=sim_user
                )
                msg = f"[{readable_name}] Door {'OPEN' if is_open else 'CLOSED'} ({direction}) - User: {sim_user}"

            print(msg)
            logging.info(msg)

            if self.on_new_data:
                self.on_new_data(data)
            time.sleep(5)

        print(f"[{readable_name}] Door thread stopped.")
