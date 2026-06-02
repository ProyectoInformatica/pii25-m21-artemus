import logging
import time
import flet as ft
from typing import Dict, Any, List
from datetime import datetime, timedelta
from ArtemusPark.database.db_connection import load_sensor_config
from ArtemusPark.config.Thresholds_Config import SENSOR_ONLINE_WINDOW_SECONDS

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

    _catastrophe_active = False

    def __init__(self):
        self.sensor_config = load_sensor_config()

    def set_catastrophe_mode(self, active: bool):
        """Activa o desactiva la alarma globalmente"""
        DashboardService._catastrophe_active = active

    def is_catastrophe_mode(self) -> bool:
        """Consulta si la alarma está activa"""
        return DashboardService._catastrophe_active

    def get_latest_sensor_data(self) -> Dict[str, Any]:
        """Obtiene los últimos datos de todos los sensores."""
        temps = Temperature_Repository.load_all_temperature_measurements()
        hums = Humidity_Repository.load_all_humidity_measurements()
        winds = Wind_Repository.load_all_wind_measurements()
        air_qualities = Smoke_Repository.load_all_smoke_measurements()
        lights = Light_Repository.load_all_light_events()
        doors = Door_Repository.load_all_door_events()

        real_occupancy = self._calculate_occupancy()

        return {
            "temperature": self._get_last_value(temps, "value", 0),
            "temperature_ts": self._get_last_value(temps, "timestamp", 0),
            "humidity": self._get_last_value(hums, "value", 0),
            "humidity_ts": self._get_last_value(hums, "timestamp", 0),
            "wind": self._get_last_value(winds, "speed", 0),
            "wind_ts": self._get_last_value(winds, "timestamp", 0),
            "air_quality": self._get_last_value(air_qualities, "value", 0),
            "air_quality_ts": self._get_last_value(air_qualities, "timestamp", 0),
            "occupancy": real_occupancy,
            "occupancy_ts": self._get_last_value(doors, "timestamp", 0),
            "light_is_on": self._get_last_value(lights, "is_on", False),
            "light_consumption": self._get_last_value(lights, "value", 0),
        }

    def _calculate_occupancy(self) -> int:
        """Calcula la ocupación actual basada en eventos de puertas."""
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
        """Prepara datos promediados por hora para el gráfico de temperatura (últimas 24 horas)."""
        temps = Temperature_Repository.load_all_temperature_measurements()
        if not temps:
            return []

        now = datetime.now()
        day_ago = now - timedelta(hours=24)

        # Agrupar valores por hora (0-23)
        hourly_bins = {}  # int_hour -> list of values

        for item in temps:
            ts = (
                item.get("timestamp", 0)
                if isinstance(item, dict)
                else getattr(item, "timestamp", 0)
            )
            dt = datetime.fromtimestamp(ts)

            if dt > day_ago:
                # Calcular a cuántas horas de distancia está del inicio del periodo (day_ago)
                delta = dt - day_ago
                hour_index = int(delta.total_seconds() // 3600)

                if 0 <= hour_index < 24:
                    if hour_index not in hourly_bins:
                        hourly_bins[hour_index] = []

                    val = (
                        item.get("value", 0)
                        if isinstance(item, dict)
                        else getattr(item, "value", 0)
                    )
                    hourly_bins[hour_index].append(float(val))

        chart_data = []
        for h in range(24):
            if h in hourly_bins:
                values = hourly_bins[h]
                avg_val = sum(values) / len(values)
                # La etiqueta muestra la hora de inicio del bloque promediado
                time_label = (day_ago + timedelta(hours=h)).strftime("%H:00")
                chart_data.append(
                    {
                        "x": float(h),
                        "y": round(avg_val, 2),
                        "tooltip": f"Media: {round(avg_val, 1)}°C\nHora: {time_label}",
                    }
                )

        # No es estrictamente necesario si iteramos el rango 24, pero asegura orden
        chart_data.sort(key=lambda p: p["x"])
        return chart_data

    def get_recent_events(self) -> List[Dict[str, Any]]:
        """Obtiene una lista de eventos recientes (puertas y luces)."""
        doors = Door_Repository.load_all_door_events()
        lights = Light_Repository.load_all_light_events()
        combined = []

        def get_sensor_name(s_type, s_id):
            if not s_id:
                return "Desconocido"
            for s in self.sensor_config.get(s_type, []):
                if s["id"] == s_id:
                    return s["name"]
            return s_id

        for d in doors:
            if isinstance(d, dict):
                s_id = d.get("sensor_id")
                name = get_sensor_name("door", s_id)
                is_open = d.get("is_open")
                ts = d.get("timestamp")
            else:
                s_id = getattr(d, "sensor_id", None)
                name = get_sensor_name("door", s_id)
                if not name and hasattr(d, "name"):
                    name = d.name
                is_open = getattr(d, "is_open", False)
                ts = getattr(d, "timestamp", 0)

            combined.append(
                {
                    "type": "door",
                    "label": f"{name }",
                    "status": "Abierta" if is_open else "Cerrada",
                    "timestamp": ts,
                }
            )

        for l in lights:
            if isinstance(l, dict):
                s_id = l.get("sensor_id")
                name = get_sensor_name("light", s_id)
                is_on = l.get("is_on")
                ts = l.get("timestamp")
            else:
                s_id = getattr(l, "sensor_id", None)
                name = get_sensor_name("light", s_id)
                is_on = getattr(l, "is_on", False)
                ts = getattr(l, "timestamp", 0)

            combined.append(
                {
                    "type": "light",
                    "label": f"{name }",
                    "status": "Encendido" if is_on else "Apagado",
                    "timestamp": ts,
                }
            )

        combined.sort(key=lambda x: str(x.get("timestamp", "")), reverse=True)
        return combined[:15]

    def get_history_by_date(self, date_str: str) -> List[Dict[str, Any]]:
        """Carga el historial de una fecha específica desde la BBDD."""
        history = []

        sources = [
            (
                Temperature_Repository.load_temperature_measurements_by_date(date_str),
                "Temperatura",
                "value",
            ),
            (
                Humidity_Repository.load_humidity_measurements_by_date(date_str),
                "Humedad",
                "value",
            ),
            (
                Wind_Repository.load_wind_measurements_by_date(date_str),
                "Viento",
                "speed",
            ),
            (
                Smoke_Repository.load_smoke_measurements_by_date(date_str),
                "Calidad Aire",
                "value",
            ),
            (Door_Repository.load_door_events_by_date(date_str), "Puerta", "is_open"),
            (Light_Repository.load_light_events_by_date(date_str), "Luz", "value"),
        ]

        for data_list, type_label, detail_key in sources:
            for item in data_list:
                ts = item.get("timestamp", 0)
                val = item.get(detail_key, "--")
                status = item.get("status", "Info")

                if type_label == "Puerta":
                    status = "Abierta" if item.get("is_open") else "Cerrada"
                elif type_label == "Luz":
                    status = "ON" if item.get("is_on") else "OFF"

                try:
                    time_str = datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
                except Exception:
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

        history.sort(key=lambda x: x["timestamp"], reverse=True)
        return history

    def get_history_by_range(
        self, min_days: int, max_days: int
    ) -> List[Dict[str, Any]]:
        """
        Carga el historial cuya fecha caiga dentro del rango de días relativos a hoy.
        min_days: Días atrás mínimos (ej. 6).
        max_days: Días atrás máximos (ej. 8).
        """
        history = []
        today = datetime.now().date()

        for days_back in range(min_days, max_days + 1):
            date_str = (today - timedelta(days=days_back)).strftime("%Y-%m-%d")
            history.extend(self.get_history_by_date(date_str))

        history.sort(key=lambda x: x["timestamp"], reverse=True)
        return history

    def get_all_history_logs(self) -> List[Dict[str, Any]]:
        """Recopila el historial completo de todos los sensores."""
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
                        "detail": f"{val }",
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
        """Verifica si los sensores configurados están enviando datos recientemente."""
        self.sensor_config = load_sensor_config()
        now = time.time()
        threshold = SENSOR_ONLINE_WINDOW_SECONDS
        health_report = []

        all_data = {
            "temperature": Temperature_Repository.load_all_temperature_measurements(),
            "humidity": Humidity_Repository.load_all_humidity_measurements(),
            "wind": Wind_Repository.load_all_wind_measurements(),
            "air_quality": Smoke_Repository.load_all_smoke_measurements(),
            "door": Door_Repository.load_all_door_events(),
            "lighting": Light_Repository.load_all_light_events(),
        }

        icon_map = {
            "temperature": ft.Icons.THERMOSTAT,
            "humidity": ft.Icons.WATER_DROP,
            "wind": ft.Icons.AIR,
            "air_quality": ft.Icons.CLOUD,
            "door": ft.Icons.SENSOR_DOOR,
            "lighting": ft.Icons.LIGHTBULB,
        }

        for sensor_type, sensors in self.sensor_config.items():
            type_data = all_data.get(sensor_type, [])

            for sensor_config in sensors:
                s_id = sensor_config["id"]
                s_name = sensor_config["name"]
                db_id = sensor_config.get("db_id")

                sensor_data = [
                    d
                    for d in type_data
                    if (
                        isinstance(d, dict)
                        and (d.get("sensor_id") == s_id or d.get("sensor_id") == db_id)
                    )
                    or (
                        not isinstance(d, dict)
                        and (
                            getattr(d, "sensor_id", None) == s_id
                            or getattr(d, "sensor_id", None) == db_id
                        )
                    )
                ]

                is_online = False
                last_seen = "Nunca"
                last_value = "--"

                if sensor_data:
                    last_item = sensor_data[-1]
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

                    if sensor_type == "temperature":
                        val = (
                            last_item.get("value")
                            if isinstance(last_item, dict)
                            else last_item.value
                        )
                        last_value = f"{val }°C"
                    elif sensor_type == "humidity":
                        val = (
                            last_item.get("value")
                            if isinstance(last_item, dict)
                            else last_item.value
                        )
                        last_value = f"{val }%"
                    elif sensor_type == "wind":
                        val = (
                            last_item.get("speed")
                            if isinstance(last_item, dict)
                            else getattr(last_item, "speed", 0)
                        )
                        last_value = f"{val } km/h"
                    elif sensor_type == "air_quality":
                        val = (
                            last_item.get("value") or last_item.get("co2_level")
                            if isinstance(last_item, dict)
                            else getattr(
                                last_item, "value", getattr(last_item, "co2_level", 0)
                            )
                        )
                        last_value = f"AQI {val }"
                    elif sensor_type == "door":
                        is_open = (
                            last_item.get("is_open")
                            if isinstance(last_item, dict)
                            else last_item.is_open
                        )
                        last_value = "Abierta" if is_open else "Cerrada"
                    elif sensor_type == "lighting":
                        is_on = (
                            last_item.get("is_on")
                            if isinstance(last_item, dict)
                            else last_item.is_on
                        )
                        last_value = "ON" if is_on else "OFF"

                health_report.append(
                    {
                        "id": s_id,
                        "db_id": db_id,
                        "name": s_name,
                        "type": sensor_type,
                        "status": "En Línea" if is_online else "Sin Señal",
                        "is_online": is_online,
                        "icon": icon_map.get(sensor_type, ft.Icons.DEVICE_UNKNOWN),
                        "last_seen": last_seen,
                        "last_value": last_value,
                    }
                )

        return health_report

    def _get_last_value(self, data_list: List[Dict], key: str, default: Any):
        """Helper para obtener el último valor de una lista."""
        if not data_list:
            return default
        last = data_list[-1]
        if isinstance(last, dict):
            return last.get(key, default)
        return getattr(last, key, default)

    def get_average_sensor_data(self) -> Dict[str, Any]:
        """Obtiene el promedio de los datos de todos los sensores."""
        avg_data = {}

        temps = Temperature_Repository.load_all_temperature_measurements()
        if temps:
            avg_data["temperature"] = round(
                sum(
                    (item.get("value", 0) if isinstance(item, dict) else item.value)
                    for item in temps
                )
                / len(temps)
            )
        else:
            avg_data["temperature"] = None

        hums = Humidity_Repository.load_all_humidity_measurements()
        if hums:
            avg_data["humidity"] = round(
                sum(
                    (item.get("value", 0) if isinstance(item, dict) else item.value)
                    for item in hums
                )
                / len(hums)
            )
        else:
            avg_data["humidity"] = None

        winds = Wind_Repository.load_all_wind_measurements()
        if winds:
            avg_data["wind"] = round(
                sum(
                    (item.get("speed", 0) if isinstance(item, dict) else item.speed)
                    for item in winds
                )
                / len(winds)
            )
        else:
            avg_data["wind"] = None

        smokes = Smoke_Repository.load_all_smoke_measurements()
        if smokes:
            avg_data["air_quality"] = round(
                sum(
                    (item.get("value", 0) if isinstance(item, dict) else item.value)
                    for item in smokes
                )
                / len(smokes)
            )
        else:
            avg_data["air_quality"] = None

        return avg_data
