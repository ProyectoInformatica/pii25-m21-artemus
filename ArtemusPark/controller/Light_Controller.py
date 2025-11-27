import threading
import time
import logging
from datetime import datetime
from typing import Callable, Optional



logging.basicConfig(
    filename="light_controller.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


from ArtemusPark.model.Light_Model import LightModel


logging.basicConfig(
    filename="light_controller.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

class LightController:
    def __init__(self, on_new_data: Optional[Callable[[LightModel], None]] = None,
                 tick_seconds: int = 3600):
        self.light_model = LightModel()
        self.on_new_data = on_new_data
        self.tick_seconds = max(1, tick_seconds)
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None


    def _should_be_on(self, now: datetime) -> bool:
        hour = now.hour
        return hour >= 19 or hour < 7

    def _update_state(self, is_on: bool) -> None:
        if self.light_model.is_on != is_on:
            self.light_model.is_on = is_on
            self.light_model.status = "ON" if is_on else "OFF"
            self.light_model.update_timestamp()
            logging.info("Light changed: %s", self.light_model.status)
            if self.on_new_data:
                try:
                    self.on_new_data(self.light_model)
                except Exception:
                    logging.exception("Error in on_new_data callback")

    def _run_loop(self) -> None:
        while not self._stop_event.is_set():
            now = datetime.now()
            should_on = self._should_be_on(now)
            self._update_state(should_on)
            # esperar un intervalo configurable
            #self._stop_event.wait(self.tick_seconds)

            logging.info(
                "Estado horario - Luz: %s (is_on=%s)",
                self.light_model.status,
                self.light_model.is_on,
            )

            self._stop_event.wait(self.tick_seconds)

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._run_loop,
            daemon=True,
            name="LightControllerThread",
        )
        self._thread.start()
        logging.info("LightController started")

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=2)
        logging.info("LightController stopped")





#hacer que enciendan a las 19 y se apaguen a las 7


