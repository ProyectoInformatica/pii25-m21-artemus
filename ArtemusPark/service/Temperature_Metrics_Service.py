from dataclasses import dataclass
from typing import Optional, List, Dict, Any

from repository.Temperature_Repository import (
    load_all_temperature_measurements,
)


@dataclass
class TemperatureMetrics:
    count: int
    average_value: Optional[float]
    max_value: Optional[int]
    min_value: Optional[int]
    cold_count: int
    mild_count: int
    hot_count: int


def compute_temperature_metrics() -> TemperatureMetrics:
    """
    Compute statistics for temperature based on stored measurements.
    """
    records: List[Dict[str, Any]] = load_all_temperature_measurements()
    if not records:
        return TemperatureMetrics(
            count=0,
            average_value=None,
            max_value=None,
            min_value=None,
            cold_count=0,
            mild_count=0,
            hot_count=0,
        )

    values = [int(r["value"]) for r in records]
    count = len(values)
    total = sum(values)
    max_value = max(values)
    min_value = min(values)
    avg = total / count if count > 0 else None

    cold_count = sum(1 for r in records if r.get("status") == "COLD")
    mild_count = sum(1 for r in records if r.get("status") == "MILD")
    hot_count = sum(1 for r in records if r.get("status") == "HOT")

    return TemperatureMetrics(
        count=count,
        average_value=avg,
        max_value=max_value,
        min_value=min_value,
        cold_count=cold_count,
        mild_count=mild_count,
        hot_count=hot_count,
    )
