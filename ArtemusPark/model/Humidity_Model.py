import time
from dataclasses import dataclass, field


@dataclass
class HumidityModel:
    value: int                  # %
    status: str                 # "LOW" | "NORMAL" | "HIGH"
    timestamp: float = field(default_factory=time.time)