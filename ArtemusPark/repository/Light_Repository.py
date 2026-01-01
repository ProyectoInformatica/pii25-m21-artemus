import json
from pathlib import Path
from typing import List, Dict, Any
from ArtemusPark.model.Light_Model import LightModel


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "json" / "light_events.json"


def _serialize(event: LightModel) -> Dict[str, Any]:
    """Convierte el modelo a un diccionario serializable."""
    return {
        "timestamp": event.timestamp,
        "is_on": event.is_on,
        "status": event.status,
        "value": event.value,
    }


def save_light_event(event: LightModel) -> None:
    """Guarda un registro en el archivo JSON."""
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)

    if DATA_FILE.exists():
        try:
            data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            data = []
    else:
        data = []

    data.append(_serialize(event))
    DATA_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def load_all_light_events() -> List[Dict[str, Any]]:
    """Carga todos los registros del archivo JSON."""
    if not DATA_FILE.exists():
        return []
    try:
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
