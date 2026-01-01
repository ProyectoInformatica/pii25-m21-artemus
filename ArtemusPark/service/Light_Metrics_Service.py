from dataclasses import dataclass
from typing import Optional, List, Dict, Any

from ArtemusPark.repository.Light_Repository import load_all_light_events


@dataclass
class LightMetrics:
    count: int
    average_intensity: Optional[float]
    on_count: int
    off_count: int


def compute_light_metrics() -> LightMetrics:
    """
    Calcula estadísticas de uso de luz basadas en eventos almacenados.
    """
    records: List[Dict[str, Any]] = load_all_light_events()
    if not records:
        return LightMetrics(
            count=0,
            average_intensity=None,
            on_count=0,
            off_count=0,
        )

    
    values = [int(r["value"]) for r in records]
    count = len(values)
    total_value = sum(values)
    avg_intensity = total_value / count if count > 0 else None

    
    
    on_count = sum(1 for r in records if r.get("is_on") is True)
    off_count = sum(1 for r in records if r.get("is_on") is False)

    return LightMetrics(
        count=count,
        average_intensity=avg_intensity,
        on_count=on_count,
        off_count=off_count,
    )
