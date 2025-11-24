import json
from pathlib import Path
from typing import List, Dict, Any
from ArtemusPark.model.Door_Model import DoorModel

DATA_FILE = Path("door_events.json")


def _serialize(event: DoorModel) -> Dict[str, Any]:
    return {
        "timestamp": event.timestamp,
        "is_open": event.is_open,
        "name": event.name,
    }


def save_door_event(event: DoorModel) -> None:
    """
    Append a single door event to the JSON 'database'.
    """
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
    """
    Returns all stored door events as plain dicts.
    """
    if not DATA_FILE.exists():
        return []

    try:
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
