import logging
from typing import Dict, Any, List

# Importamos los repositorios necesarios
from ArtemusPark.repository import (
    Temperature_Repository,
    Humidity_Repository,
    Wind_Repository,
    Smoke_Repository,
    Door_Repository,  # <--- NUEVO
    Light_Repository,  # <--- NUEVO
)

logger = logging.getLogger(__name__)


class DashboardService:
    def get_latest_sensor_data(self) -> Dict[str, Any]:
        # Cargamos los datos crudos primero para inspeccionarlos
        temps = Temperature_Repository.load_all_temperature_measurements()
        hums = Humidity_Repository.load_all_humidity_measurements()

        # LOGS DE DEPURACIÓN
        print(f"DEBUG: Loaded {len(temps)} temperature records")
        print(f"DEBUG: Loaded {len(hums)} humidity records")

        return {
            "temperature": self._get_last_value(temps, "value", 0.0),
            "humidity": self._get_last_value(hums, "value", 0),
            "wind": self._get_last_value(
                Wind_Repository.load_all_wind_measurements(), "speed", 0
            ),
            "air_quality": self._get_last_value(
                Smoke_Repository.load_all_smoke_measurements(), "value", 0
            ),
        }

    # NUEVO MÉTODO
    def get_recent_events(self) -> List[Dict[str, Any]]:
        print("DashboardService.get_recent_events: Fetching combined events")

        # 1. Cargar eventos de diferentes fuentes
        doors = Door_Repository.load_all_door_events()
        lights = Light_Repository.load_all_light_events()

        # 2. Normalizar un poco los datos para que tengan campos comunes
        combined = []
        for d in doors:
            d["type"] = "door"
            d["label"] = f"Puerta: {d.get('name')}"
            combined.append(d)

        for l in lights:
            l["type"] = "light"
            l["label"] = "Iluminación"
            l["status"] = "Encendido" if l.get("is_on") else "Apagado"
            combined.append(l)

        # 3. Ordenar por fecha (timestamp) descendente (los más nuevos primero)
        # Asumimos formato ISO strings que se pueden ordenar alfabéticamente
        combined.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

        # 4. Devolver solo los últimos 10
        return combined[:10]

    def _get_last_value(self, data_list: List[Dict], key: str, default: Any):
        if not data_list:
            return default
        return data_list[-1].get(key, default)
