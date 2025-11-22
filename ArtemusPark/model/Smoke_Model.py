from dataclasses import dataclass, field
import time

@dataclass
class SmokeModel:
    value: int  # Densidad de humo (0-100) o ppm
    status: str  # "CLEAR" | "WARNING" | "ALARM"
    timestamp: float = field(default_factory=time.time)