from dataclasses import dataclass, field
import time


@dataclass
class DoorModel:
    is_open: bool  # True = Abierta, False = Cerrada
    name: str  # Nombre del sensor
    timestamp: float = field(default_factory=time.time)
