import json
from pathlib import Path
from typing import List, Dict, Any
from ArtemusPark.model.Smoke_Model import SmokeModel

# --- CORRECCIÓN DE RUTA ---
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "json" / "smoke_measurements.json"

def _serialize(measurement: SmokeModel) -> Dict[str, Any]:
    return {
        "timestamp": measurement.timestamp,
        "value": measurement.value,
        "status": measurement.status,
    }

def save_smoke_measurement(measurement: SmokeModel) -> None:
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

def load_all_smoke_measurements() -> List[Dict[str, Any]]:
    if not DATA_FILE.exists():
        return []
    try:
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []