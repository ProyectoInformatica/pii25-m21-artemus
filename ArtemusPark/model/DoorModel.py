import random
import logging
import time

# Asumiendo que quieres que este archivo use un log diferente
logging.basicConfig(
    filename="doorModel.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


class DoorModel:
    """Modelo: simula sensores de puertas y usa el estado del controlador para detenerse."""

    # 1. Constructor para aceptar la referencia del controlador
    def __init__(self, controller_ref=None):
        self.controller_ref = controller_ref

    def _log(self, message: str):
        if self.controller_ref and hasattr(self.controller_ref, "log"):
            self.controller_ref.log(message)
        else:
            print(message)

    def door(self, name):
        """Abre la puerta a las 9:00 y la cierra a las 18:00 según la hora simulada."""

        while self.controller_ref.running:
            hour = self.controller_ref.simulated_hour

            if 9 <= hour < 18:
                # Horario de apertura
                message = f"[{name}] {hour}:00 → The door is open."
            else:
                # Fuera de horario
                message = f"[{name}] {hour}:00 → The door is close."

            self._log(message)
            time.sleep(5)

        self._log(f"[{name}] Hilo de puerta terminado.")

