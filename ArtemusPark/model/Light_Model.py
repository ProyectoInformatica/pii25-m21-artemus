import time
from dataclasses import dataclass, field


@dataclass
class LightModel:
    value: int  # %
    status: str  # "ON" | "OFF"
    is_on: bool
    timestamp: float = field(default_factory=time.time)