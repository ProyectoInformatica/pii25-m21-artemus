from dataclasses import dataclass
from typing import Optional, List, Dict, Any

from ArtemusPark.repository.Humidity_Repository import (
    load_all_humidity_measurements,
)


@dataclass
class HumidityMetrics:
    count: int
    average_value: Optional[float]
    max_value: Optional[int]
    min_value: Optional[int]
    low_count: int
    normal_count: int
    high_count: int


def compute_humidity_metrics() -> HumidityMetrics:
    """
    Compute statistics for humidity based on stored measurements.
    """
    records: List[Dict[str, Any]] = load_all_humidity_measurements()
    if not records:
        return HumidityMetrics(
            count=0,
            average_value=None,
            max_value=None,
            min_value=None,
            low_count=0,
            normal_count=0,
            high_count=0,
        )

    values = [int(r["value"]) for r in records]
    count = len(values)
    total = sum(values)
    max_value = max(values)
    min_value = min(values)
    avg = total / count if count > 0 else None

    low_count = sum(1 for r in records if r.get("status") == "LOW")
    normal_count = sum(1 for r in records if r.get("status") == "NORMAL")
    high_count = sum(1 for r in records if r.get("status") == "HIGH")

    return HumidityMetrics(
        count=count,
        average_value=avg,
        max_value=max_value,
        min_value=min_value,
        low_count=low_count,
        normal_count=normal_count,
        high_count=high_count,
    )
