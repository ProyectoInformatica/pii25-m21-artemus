import json
from pathlib import Path
from typing import List, Dict, Any
from ArtemusPark.model.Humidity_Model import HumidityModel

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "humidity_measurements.json"

def _serialize(measurement: HumidityModel) -> Dict[str, Any]:
    return {
        "timestamp": measurement.timestamp,
        "value": measurement.value,
        "status": measurement.status,
    }


def save_humidity_measurement(measurement: HumidityModel) -> None:
    """
    Append a single humidity measurement to the JSON 'database'.
    """
    if DATA_FILE.exists():
        try:
            data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            data = []
    else:
        data = []

    data.append(_serialize(measurement))

    DATA_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def load_all_humidity_measurements() -> List[Dict[str, Any]]:
    """
    Returns all stored humidity measurements as plain dicts.
    """
    if not DATA_FILE.exists():
        return []

    try:
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
