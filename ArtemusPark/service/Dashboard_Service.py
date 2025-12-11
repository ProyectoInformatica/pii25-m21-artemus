import logging
from typing import Dict, Any, List
from datetime import datetime

# Importamos los repositorios
from ArtemusPark.repository import (
    Temperature_Repository,
    Humidity_Repository,
    Wind_Repository,
    Smoke_Repository,
    Door_Repository,
    Light_Repository,
)

logger = logging.getLogger(__name__)


class DashboardService:
    # def get_latest_sensor_data(self) -> Dict[str, Any]:
    #     """Obtiene el último valor de cada sensor para las tarjetas."""
    #     temps = Temperature_Repository.load_all_temperature_measurements()
    #     hums = Humidity_Repository.load_all_humidity_measurements()
    #     winds = Wind_Repository.load_all_wind_measurements()
    #     smokes = Smoke_Repository.load_all_smoke_measurements()
    #
    #     return {
    #         "temperature": self._get_last_value(temps, "value", 0.0),
    #         "humidity": self._get_last_value(hums, "value", 0),
    #         "wind": self._get_last_value(winds, "speed", 0),
    #         "air_quality": self._get_last_value(smokes, "value", 0),
    #         "occupancy": 1201  # Valor simulado fijo o aleatorio
    #     }

    def get_latest_sensor_data(self) -> Dict[str, Any]:
        temps = Temperature_Repository.load_all_temperature_measurements()
        hums = Humidity_Repository.load_all_humidity_measurements()
        winds = Wind_Repository.load_all_wind_measurements()
        smokes = Smoke_Repository.load_all_smoke_measurements()

        # --- CÁLCULO DE AFORO REAL ---
        real_occupancy = self._calculate_occupancy()

        return {
            "temperature": self._get_last_value(temps, "value", 0),
            "humidity": self._get_last_value(hums, "value", 0),
            "wind": self._get_last_value(winds, "speed", 0),
            "air_quality": self._get_last_value(smokes, "value", 0),
            "occupancy": real_occupancy,  # <--- USAMOS EL VALOR CALCULADO
        }

    def _calculate_occupancy(self) -> int:
        """
        Calcula el aforo actual basándose en el historial de entradas y salidas.
        """
        events = Door_Repository.load_all_door_events()

        # Empezamos con un aforo base (ej. al abrir el parque ya había gente)
        # O empezamos en 0. Para que no se vea vacío, ponemos una base simulada.
        count = 0

        for e in events:
            # Solo contamos si la puerta se ABRIÓ (is_open=True)
            if e.get("is_open"):
                direction = e.get("direction", "IN")

                if direction == "IN":
                    count += 1
                elif direction == "OUT":
                    count -= 1

        # Evitar números negativos
        return max(0, count)

    def get_temp_chart_data(self) -> List[Dict[str, Any]]:
        """
        Prepara los datos para la gráfica de temperatura (últimos 10 registros).
        """
        temps = Temperature_Repository.load_all_temperature_measurements()
        # Tomamos los últimos 10 (o menos si no hay tantos)
        recent = temps[-10:] if temps else []

        chart_data = []
        for i, item in enumerate(recent):
            # Intentamos formatear la hora para el tooltip
            ts = item.get("timestamp", 0)
            try:
                # Si es float (timestamp)
                if isinstance(ts, (int, float)):
                    time_label = datetime.fromtimestamp(ts).strftime("%H:%M:%S")
                else:
                    time_label = str(ts)
            except:
                time_label = ""

            chart_data.append(
                {
                    "x": i,  # Usamos índice 0,1,2... para simplificar el eje X
                    "y": float(item.get("value", 0)),
                    "tooltip": time_label,
                }
            )
        return chart_data

    def get_recent_events(self) -> List[Dict[str, Any]]:
        """Combina eventos de Puertas y Luces."""
        doors = Door_Repository.load_all_door_events()
        lights = Light_Repository.load_all_light_events()

        combined = []
        # Normalizar Puertas
        for d in doors:
            combined.append(
                {
                    "type": "door",
                    "label": f"Puerta: {d.get('name')}",
                    "status": "Abierta" if d.get("is_open") else "Cerrada",
                    "timestamp": d.get("timestamp"),
                }
            )
        # Normalizar Luces
        for l in lights:
            combined.append(
                {
                    "type": "light",
                    "label": "Iluminación",
                    "status": "Encendido" if l.get("is_on") else "Apagado",
                    "timestamp": l.get("timestamp"),
                }
            )

        # Ordenar por timestamp descendente
        combined.sort(key=lambda x: str(x.get("timestamp", "")), reverse=True)
        return combined[:15]

    def _get_last_value(self, data_list: List[Dict], key: str, default: Any):
        if not data_list:
            return default
        return data_list[-1].get(key, default)
