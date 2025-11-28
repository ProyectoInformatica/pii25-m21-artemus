import time
from dataclasses import dataclass, field


@dataclass
class SmokeModel:
    value: int  # Densidad de humo (0-100)
    status: str  # "CLEAR" | "WARNING" | "ALARM"
    timestamp: float = field(default_factory=time.time)