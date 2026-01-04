import logging
import random
import time
from typing import Callable, Optional

# Asegúrate de que estos imports son correctos según tu estructura
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
        # Obtenemos usuarios reales para simular que fichan
        self.users_list = list(self.auth_repo.get_all_users().keys())

    def run(self, sensor_id: str):
        """Bucle que simula el sensor de puerta."""
        readable_name = sensor_id
        # Buscar el nombre legible en la configuración
        for sensor in SENSOR_CONFIG.get("door", []):
            if sensor["id"] == sensor_id:
                readable_name = sensor["name"]
                break

        print(f"[{readable_name}] Door sensor started.")

        while self.controller_ref.running:
            # 1. Verificar si el parque está cerrado
            if not self.controller_ref.park_open:
                msg = f"[{readable_name}] Park is CLOSED. Door activity suspended."
                print(msg)
                logging.info(msg)
                time.sleep(5)
                continue

            # 2. Lógica de simulación cuando el parque está ABIERTO
            else:
                # Decidimos si la puerta se abre o se cierra (50% probabilidad)
                is_open = bool(random.randint(0, 1))

                if is_open:
                    # SI SE ABRE: Decidimos dirección y usuario
                    # 60% probabilidad de entrada (IN), 40% salida (OUT)
                    direction = "IN" if random.random() < 0.6 else "OUT"
                    # Elegimos un usuario al azar si hay lista, si no "unknown"
                    sim_user = random.choice(self.users_list) if self.users_list else "unknown"

                    log_msg = f"[{readable_name}] Door OPEN ({direction}) - User: {sim_user}"
                else:
                    # SI SE CIERRA: No hay dirección de flujo ni usuario pasando
                    direction = "CLOSED"  # Usamos un valor neutro que no sea IN ni OUT
                    sim_user = None

                    log_msg = f"[{readable_name}] Door CLOSED"

                # Creamos el modelo con los datos coherentes
                data = DoorModel(
                    is_open=is_open,
                    sensor_id=sensor_id,
                    name=readable_name,
                    direction=direction,
                    username=sim_user
                )

                # Imprimir y guardar log
                print(log_msg)
                logging.info(log_msg)

                # Enviar datos al controlador principal si existe el callback
                if self.on_new_data:
                    self.on_new_data(data)

            # NOTA IMPORTANTE SOBRE INDENTACIÓN:
            # Este sleep debe estar DENTRO del while, pero FUERA del if/else.
            # Controla la velocidad de la simulación (cada 5 segundos ocurre algo).
            time.sleep(5)

        print(f"[{readable_name}] Door thread stopped.")