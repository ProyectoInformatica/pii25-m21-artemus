from dataclasses import dataclass, field
import time


@dataclass
class LightModel:
    value: int = 0  # porcentaje %
    status: str = "OFF"  # "LOW" | "NORMAL" | "HIGH" o "OFF"/"ON"
    is_on: bool = False
    timestamp: float = field(default_factory=time.time)

    def update_timestamp(self) -> None:
        self.timestamp = time.time()
