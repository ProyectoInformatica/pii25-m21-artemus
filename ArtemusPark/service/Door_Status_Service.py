from dataclasses import dataclass
from ArtemusPark.model.Door_Model import DoorModel


@dataclass
class DoorStatusResult:
    is_anomaly: bool
    is_open: bool
    park_open: bool
    message: str


def check_door_status(event: DoorModel, park_open: bool) -> DoorStatusResult:
    """
    Verifica si el estado de la puerta es consistente con el estado del parque.
    Ejemplo:
    - Si el parque está CERRADO, cualquier puerta ABIERTA es una anomalía.
    """
    is_open = event.is_open

    if not park_open and is_open:
        message = (
            f"Door '{event .name }' is OPEN while park is CLOSED → anomaly detected."
        )
        is_anomaly = True
    else:
        message = (
            f"Door '{event .name }' is "
            f"{'OPEN'if is_open else 'CLOSED'} (park is "
            f"{'OPEN'if park_open else 'CLOSED'})."
        )
        is_anomaly = False

    return DoorStatusResult(
        is_anomaly=is_anomaly,
        is_open=is_open,
        park_open=park_open,
        message=message,
    )
