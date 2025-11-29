import logging
import time
from datetime import datetime
from typing import Callable, Optional

from ArtemusPark.model.Light_Model import LightModel

from ArtemusPark.Notifications.Notification_system import (
    NotificationSystem,
    Notification,
)

logging.basicConfig(
    filename="light_controller.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


class LightController:
    def __init__(
        self,
        controller_ref=None,
        on_new_data: Optional[Callable[[LightModel], None]] = None,
        notification_system: Optional[NotificationSystem] = None,
    ):
        self.controller_ref = controller_ref
        self.on_new_data = on_new_data
        self.notification_system = notification_system
        self._last_state: Optional[bool] = None

    def _should_be_on(self, simulated_hour: int) -> bool:

        return simulated_hour >= 19 or simulated_hour < 7

    def _notify_out_of_schedule(
        self,
        simulated_hour: int,
        is_on: bool,
    ) -> None:
        if not self.notification_system:
            return

        scheduled_on = self._should_be_on(simulated_hour)
        if is_on != scheduled_on:
            state = "ENCENDIDA" if is_on else "APAGADA"
            msg = (
                f"Luz {state} fuera del horario programado "
                f"(hora simulada: {simulated_hour:02d}:00, "
                f"debería estar {'ENCENDIDA' if scheduled_on else 'APAGADA'})."
            )
            notification = Notification(
                source="LightController",
                level="WARNING",
                message=msg,
            )
            self.notification_system.notify("LIGHT", notification)

    def run(self, name: str):
        """
        Simulates a light sensor/controller.
        Logic: Lights turn ON between 19:00 and 07:00 based on SIMULATED time.
        """
        # Si no hay referencia, no podemos leer la hora simulada, así que fallamos o usamos hora real
        if not self.controller_ref:
            logging.error(
                "LightController needs controller_ref to read simulated time."
            )
            return

        while self.controller_ref.running:
            # Check SIMULATED time from the main controller
            current_hour = self.controller_ref.simulated_hour

            # Logic: ON between 19:00 and 07:00
            should_be_on = self._should_be_on(current_hour)

            status = "ON" if should_be_on else "OFF"
            value = 100 if should_be_on else 0

            data = LightModel(is_on=should_be_on, status=status, value=value)

            msg = f"[{name}] Light {status} (Simulated Hour: {current_hour})"
            print(msg)
            logging.info(msg)

            if self._last_state is None or self._last_state != should_be_on:
                # Notificar si el cambio es fuera del horario programado
                self._notify_out_of_schedule(current_hour, should_be_on)
                self._last_state = should_be_on

            if self.on_new_data:
                try:
                    self.on_new_data(data)
                except Exception:
                    logging.exception("Error in on_new_data callback")

            time.sleep(1)
