import json
from pathlib import Path
from typing import List, Dict, Any

from ArtemusPark.model.Wind_Model import WindModel
from model.Wind_Model import WindModel

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "wind_measurements.json"

def _serialize_measurement(measurement: WindModel) -> Dict[str, Any]:
    return {
        "timestamp": measurement.timestamp,
        "speed": measurement.speed,
        "state": measurement.state,
        "label": measurement.label,
    }


def save_wind_measurement(measurement: WindModel) -> None:
    """
    Append a single wind measurement to the JSON 'database'.
    """
    if DATA_FILE.exists():
        with DATA_FILE.open("r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
    else:
        data = []

    data.append(_serialize_measurement(measurement))

    with DATA_FILE.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def load_all_wind_measurements() -> List[Dict[str, Any]]:
    """
    Returns all stored measurements as plain dicts.
    """
    if not DATA_FILE.exists():
        return []

    with DATA_FILE.open("r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []
