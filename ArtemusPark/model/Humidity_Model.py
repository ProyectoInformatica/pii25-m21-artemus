import time
from dataclasses import dataclass, field


@dataclass
class HumidityModel:
    """Modelo de datos para sensores de humedad."""

    value: int
    status: str
    timestamp: float = field(default_factory=time.time)
