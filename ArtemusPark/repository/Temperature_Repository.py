import json
from pathlib import Path
from typing import List, Dict, Any
from ArtemusPark.model.Temperature_Model import TemperatureModel


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "json" / "temperature_measurements.json"


def _serialize(measurement: TemperatureModel) -> Dict[str, Any]:
    """Convierte el modelo a un diccionario serializable."""
    return {
        "timestamp": measurement.timestamp,
        "value": measurement.value,
        "status": measurement.status,
    }


def save_temperature_measurement(measurement: TemperatureModel) -> None:
    """Guarda un registro en el archivo JSON."""
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)

    if DATA_FILE.exists():
        try:
            data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            data = []
    else:
        data = []

    data.append(_serialize(measurement))
    DATA_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def load_all_temperature_measurements() -> List[Dict[str, Any]]:
    """Carga todos los registros del archivo JSON."""
    if not DATA_FILE.exists():
        return []
    try:
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
