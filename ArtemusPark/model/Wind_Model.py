import time
from dataclasses import dataclass, field

@dataclass
class WindModel:
    speed: int                  # km/h
    state: str                  # "SAFE" | "WARNING" | "DANGER"
    label: str                  # texto descriptivo
    timestamp: float = field(default_factory=time.time)