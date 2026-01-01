from dataclasses import dataclass, field
import time


@dataclass
class DoorModel:
    """Modelo de datos para eventos de puertas."""
    is_open: bool  
    name: str  
    direction: str  
    timestamp: float = field(default_factory=time.time)
