import logging
import time
import flet as ft
from typing import Dict, Any, List
from datetime import datetime

# Importamos los modelos y repositorios
from ArtemusPark.model.Door_Model import DoorModel
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
    # Variable global
    _catastrophe_active = False

    def set_catastrophe_mode(self, active: bool):
        """Activa o desactiva la alarma globalmente"""
        DashboardService._catastrophe_active = active

    def is_catastrophe_mode(self) -> bool:
        """Consulta si la alarma está activa"""
        return DashboardService._catastrophe_active

    def get_latest_sensor_data(self) -> Dict[str, Any]:
        temps = Temperature_Repository.load_all_temperature_measurements()
        hums = Humidity_Repository.load_all_humidity_measurements()
        winds = Wind_Repository.load_all_wind_measurements()
        smokes = Smoke_Repository.load_all_smoke_measurements()

        real_occupancy = self._calculate_occupancy()

        return {
            "temperature": self._get_last_value(temps, "value", 0),
            "humidity": self._get_last_value(hums, "value", 0),
            "wind": self._get_last_value(winds, "speed", 0),
            "air_quality": self._get_last_value(smokes, "value", 0),
            "occupancy": real_occupancy,
        }

    def _calculate_occupancy(self) -> int:
        events = Door_Repository.load_all_door_events()
        count = 0
        for e in events:
            if isinstance(e, DoorModel):
                is_open = e.is_open
                direction = e.direction
            elif isinstance(e, dict):
                is_open = e.get("is_open")
                direction = e.get("direction", "IN")
            else:
                continue

            if str(is_open).lower() in ("true", "1", "yes"):
                dir_str = str(direction).upper()
                if dir_str == "IN":
                    count += 1
                elif dir_str == "OUT":
                    count -= 1
        return max(0, count)

    def get_temp_chart_data(self) -> List[Dict[str, Any]]:
        temps = Temperature_Repository.load_all_temperature_measurements()
        recent = temps[-10:] if temps else []
        chart_data = []
        for i, item in enumerate(recent):
            ts = (
                item.get("timestamp", 0)
                if isinstance(item, dict)
                else getattr(item, "timestamp", 0)
            )
            val = (
                item.get("value", 0)
                if isinstance(item, dict)
                else getattr(item, "value", 0)
            )
            try:
                time_label = datetime.fromtimestamp(ts).strftime("%H:%M:%S")
            except:
                time_label = ""
            chart_data.append({"x": i, "y": float(val), "tooltip": time_label})
        return chart_data

    def get_recent_events(self) -> List[Dict[str, Any]]:
        doors = Door_Repository.load_all_door_events()
        lights = Light_Repository.load_all_light_events()
        combined = []

        for d in doors:
            if isinstance(d, dict):
                name = d.get("name")
                is_open = d.get("is_open")
                ts = d.get("timestamp")
            else:
                name = getattr(d, "name", "Puerta")
                is_open = getattr(d, "is_open", False)
                ts = getattr(d, "timestamp", 0)

            combined.append(
                {
                    "type": "door",
                    "label": f"Puerta: {name}",
                    "status": "Abierta" if is_open else "Cerrada",
                    "timestamp": ts,
                }
            )

        for l in lights:
            if isinstance(l, dict):
                is_on = l.get("is_on")
                ts = l.get("timestamp")
            else:
                is_on = getattr(l, "is_on", False)
                ts = getattr(l, "timestamp", 0)

            combined.append(
                {
                    "type": "light",
                    "label": "Iluminación",
                    "status": "Encendido" if is_on else "Apagado",
                    "timestamp": ts,
                }
            )

        combined.sort(key=lambda x: str(x.get("timestamp", "")), reverse=True)
        return combined[:15]

    def get_all_history_logs(self) -> List[Dict[str, Any]]:
        history = []

        def add_records(source_list, type_label, detail_key):
            for item in source_list:
                if isinstance(item, dict):
                    ts = item.get("timestamp", 0)
                    val = item.get(detail_key, "--")
                    status = item.get("status", "Info")
                    if type_label == "Puerta":
                        status = "Abierta" if item.get("is_open") else "Cerrada"
                    elif type_label == "Luz":
                        status = "ON" if item.get("is_on") else "OFF"
                else:
                    ts = getattr(item, "timestamp", 0)
                    val = getattr(item, detail_key, "--")
                    status = getattr(item, "status", "Info")
                    if type_label == "Puerta":
                        status = (
                            "Abierta" if getattr(item, "is_open", False) else "Cerrada"
                        )
                    elif type_label == "Luz":
                        status = "ON" if getattr(item, "is_on", False) else "OFF"

                try:
                    time_str = datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
                except:
                    time_str = "Error fecha"

                history.append(
                    {
                        "timestamp": ts,
                        "time_str": time_str,
                        "type": type_label,
                        "location": "Zona Parque",
                        "detail": f"{val}",
                        "status": str(status),
                    }
                )

        add_records(
            Temperature_Repository.load_all_temperature_measurements(),
            "Temperatura",
            "value",
        )
        add_records(
            Humidity_Repository.load_all_humidity_measurements(), "Humedad", "value"
        )
        add_records(Wind_Repository.load_all_wind_measurements(), "Viento", "speed")
        add_records(
            Smoke_Repository.load_all_smoke_measurements(), "Calidad Aire", "value"
        )
        add_records(Door_Repository.load_all_door_events(), "Puerta", "name")
        add_records(Light_Repository.load_all_light_events(), "Luz", "value")

        history.sort(key=lambda x: x["timestamp"], reverse=True)
        return history

    def get_sensors_health_status(self) -> List[Dict[str, Any]]:
        now = time.time()
        threshold = 15

        def check_status(data_list, name_sensor, icon):
            is_online = False
            last_seen = "Nunca"
            if data_list:
                last_item = data_list[-1]
                ts = (
                    last_item.get("timestamp", 0)
                    if isinstance(last_item, dict)
                    else getattr(last_item, "timestamp", 0)
                )
                if (now - ts) < threshold:
                    is_online = True
                try:
                    last_seen = datetime.fromtimestamp(ts).strftime("%H:%M:%S")
                except:
                    last_seen = "Error fecha"

            return {
                "name": name_sensor,
                "status": "En Línea" if is_online else "Sin Señal",
                "is_online": is_online,
                "icon": icon,
                "last_seen": last_seen,
            }

        health_report = [
            check_status(
                Temperature_Repository.load_all_temperature_measurements(),
                "Sensor Temperatura",
                ft.Icons.THERMOSTAT,
            ),
            check_status(
                Humidity_Repository.load_all_humidity_measurements(),
                "Sensor Humedad",
                ft.Icons.WATER_DROP,
            ),
            check_status(
                Wind_Repository.load_all_wind_measurements(), "Anemómetro", ft.Icons.AIR
            ),
            check_status(
                Smoke_Repository.load_all_smoke_measurements(),
                "Detector Humo",
                ft.Icons.CLOUD,
            ),
            check_status(
                Door_Repository.load_all_door_events(), "Puertas", ft.Icons.SENSOR_DOOR
            ),
            check_status(
                Light_Repository.load_all_light_events(),
                "Iluminación",
                ft.Icons.LIGHTBULB,
            ),
        ]
        return health_report

    def _get_last_value(self, data_list: List[Dict], key: str, default: Any):
        if not data_list:
            return default
        last = data_list[-1]
        if isinstance(last, dict):
            return last.get(key, default)
        return getattr(last, key, default)
