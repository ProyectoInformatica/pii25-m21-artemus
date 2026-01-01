from dataclasses import dataclass, field
import time


@dataclass
class TemperatureModel:
    """Modelo de datos para sensores de temperatura."""
    value: int  
    status: str  
    timestamp: float = field(default_factory=time.time)
