from dataclasses import dataclass
from model.Door_Model import DoorModel


@dataclass
class DoorStatusResult:
    is_anomaly: bool
    is_open: bool
    park_open: bool
    message: str


def check_door_status(event: DoorModel, park_open: bool) -> DoorStatusResult:
    """
    Check if the door state is consistent with park status.
    Example rule:
    - If park is CLOSED, any OPEN door is an anomaly.
    - If park is OPEN, doors can be open or closed (no anomaly here).
    """
    is_open = event.is_open

    # Basic rule
    if not park_open and is_open:
        message = (
            f"Door '{event.name}' is OPEN while park is CLOSED → anomaly detected."
        )
        is_anomaly = True
    else:
        message = (
            f"Door '{event.name}' is "
            f"{'OPEN' if is_open else 'CLOSED'} (park is "
            f"{'OPEN' if park_open else 'CLOSED'})."
        )
        is_anomaly = False

    return DoorStatusResult(
        is_anomaly=is_anomaly,
        is_open=is_open,
        park_open=park_open,
        message=message,
    )
