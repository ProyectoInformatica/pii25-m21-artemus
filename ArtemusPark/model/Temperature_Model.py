from dataclasses import dataclass, field
import time

@dataclass
class TemperatureModel:
    value: int                  # ºC
    status: str                 # "COLD" | "MILD" | "HOT"
    timestamp: float = field(default_factory=time.time)