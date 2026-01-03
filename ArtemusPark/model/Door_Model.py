from dataclasses import dataclass, field
import time
from typing import Optional


@dataclass
class DoorModel:
    """Modelo de datos para eventos de puertas."""

    is_open: bool
    name: str
    direction: str
    username: Optional[str] = None
    timestamp: float = field(default_factory=time.time)
