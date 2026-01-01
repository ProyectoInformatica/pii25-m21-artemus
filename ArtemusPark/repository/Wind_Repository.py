import json
from pathlib import Path
from typing import List, Dict, Any
from ArtemusPark.model.Wind_Model import WindModel


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "json" / "wind_measurements.json"


def _serialize_measurement(measurement: WindModel) -> Dict[str, Any]:
    """Convierte el modelo a un diccionario serializable."""
    return {
        "timestamp": measurement.timestamp,
        "speed": measurement.speed,
        "state": measurement.state,
        "label": measurement.label,
    }


def save_wind_measurement(measurement: WindModel) -> None:
    """Guarda un registro en el archivo JSON."""
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)

    if DATA_FILE.exists():
        try:
            data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            data = []
    else:
        data = []

    data.append(_serialize_measurement(measurement))
    DATA_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def load_all_wind_measurements() -> List[Dict[str, Any]]:
    """Carga todos los registros del archivo JSON."""
    if not DATA_FILE.exists():
        return []
    try:
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
