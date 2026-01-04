import json
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
from ArtemusPark.model.Door_Model import DoorModel


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "json" / "door"


def _serialize(event: DoorModel) -> Dict[str, Any]:
    """Convierte el modelo a un diccionario serializable."""
    return {
        "sensor_id": event.sensor_id,
        "timestamp": event.timestamp,
        "is_open": event.is_open,
        "direction": event.direction,
        "username": event.username,
    }


def save_door_event(event: DoorModel) -> None:
    """Guarda un registro en un archivo JSON diario."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    today = datetime.fromtimestamp(event.timestamp).strftime("%Y-%m-%d")
    file_path = DATA_DIR / f"door_{today}.json"

    if file_path.exists():
        try:
            data = json.loads(file_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            data = []
    else:
        data = []

    data.append(_serialize(event))
    file_path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def load_all_door_events() -> List[Dict[str, Any]]:
    """Carga todos los registros de los archivos JSON diarios."""
    if not DATA_DIR.exists():
        return []
    
    all_data = []
    for file_path in sorted(DATA_DIR.glob("door_*.json")):
        try:
            file_content = file_path.read_text(encoding="utf-8")
            data = json.loads(file_content)
            if isinstance(data, list):
                all_data.extend(data)
        except json.JSONDecodeError:
            continue
            
    return all_data
