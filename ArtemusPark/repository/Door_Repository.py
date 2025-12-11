import json
from pathlib import Path
from typing import List, Dict, Any
from ArtemusPark.model.Door_Model import DoorModel

# --- RUTA ---
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "json" / "door_events.json"

def _serialize(event: DoorModel) -> Dict[str, Any]:
    return {
        "timestamp": event.timestamp,
        "is_open": event.is_open,
        "name": event.name,
        "direction": event.direction, # <--- GUARDAMOS LA DIRECCIÓN
    }

def save_door_event(event: DoorModel) -> None:
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

def load_all_door_events() -> List[Dict[str, Any]]:
    if not DATA_FILE.exists():
        return []
    try:
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []