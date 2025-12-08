import logging
from typing import Dict, Any, List
from ArtemusPark.repository import (
    Temperature_Repository,
    Humidity_Repository,
    Wind_Repository,
    Smoke_Repository,
    Light_Repository
)

# Configurar logger simple si no existe
logger = logging.getLogger(__name__)


class DashboardService:
    def get_latest_sensor_data(self) -> Dict[str, Any]:
        """Recupera el último valor registrado de cada sensor."""
        print("DashboardService.get_latest_sensor_data: Fetching latest data")

        return {
            "temperature": self._get_last_value(Temperature_Repository.load_all_temperature_measurements(), "value",
                                                0.0),
            "humidity": self._get_last_value(Humidity_Repository.load_all_humidity_measurements(), "value", 0),
            "wind": self._get_last_value(Wind_Repository.load_all_wind_measurements(), "speed", 0),
            "air_quality": self._get_last_value(Smoke_Repository.load_all_smoke_measurements(), "value", 0),
        }

    def get_temperature_history(self) -> List[float]:
        """Recupera los últimos 10 valores de temperatura para la gráfica."""
        print("DashboardService.get_temperature_history: Fetching history")
        all_data = Temperature_Repository.load_all_temperature_measurements()
        # Extraemos solo el valor 'value' de los últimos 10 registros
        return [entry["value"] for entry in all_data[-10:]] if all_data else []

    def _get_last_value(self, data_list: List[Dict], key: str, default: Any):
        if not data_list:
            return default
        return data_list[-1].get(key, default)