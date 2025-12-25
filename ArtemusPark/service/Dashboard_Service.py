import logging
import time
import flet as ft
from typing import Dict, Any, List
from datetime import datetime
from ArtemusPark.model.Door_Model import DoorModel

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
    # Variable de clase (COMPARTIDA por todas las instancias)
    _catastrophe_active = False

    # --- NUEVOS MÉTODOS PARA GESTIONAR LA ALERTA ---
    def set_catastrophe_mode(self, active: bool):
        """Activa o desactiva la alarma globalmente"""
        DashboardService._catastrophe_active = active

    def is_catastrophe_mode(self) -> bool:
        """Consulta si la alarma está activa"""
        return DashboardService._catastrophe_active
    def get_sensors_health_status(self) -> List[Dict[str, Any]]:
        """
        Verifica si los sensores están "vivos" basándose en la última lectura.
        Umbral: Si no hay datos en los últimos 10 segundos -> OFFLINE.
        """
        now = time.time()
        threshold = 15  # Segundos para considerar que el sensor "murió"

        # Helper para verificar estado
        def check_status(data_list, name_sensor, icon):
            is_online = False
            last_seen = "Nunca"

            if data_list:
                # Obtenemos el último elemento (puede ser dict u objeto)
                last_item = data_list[-1]

                # Extraer timestamp
                if isinstance(last_item, dict):
                    ts = last_item.get("timestamp", 0)
                else:
                    ts = getattr(last_item, "timestamp", 0)

                # Comprobar tiempo
                if (now - ts) < threshold:
                    is_online = True

                # Formatear hora para mostrar
                last_seen = datetime.fromtimestamp(ts).strftime("%H:%M:%S")

            return {
                "name": name_sensor,
                "status": "En Línea" if is_online else "Sin Señal",
                "is_online": is_online,
                "icon": icon,
                "last_seen": last_seen,
            }

        # Cargamos datos
        temps = Temperature_Repository.load_all_temperature_measurements()
        hums = Humidity_Repository.load_all_humidity_measurements()
        winds = Wind_Repository.load_all_wind_measurements()
        smokes = Smoke_Repository.load_all_smoke_measurements()
        doors = Door_Repository.load_all_door_events()
        lights = Light_Repository.load_all_light_events()

        # Construimos la lista de estados
        health_report = [
            check_status(temps, "Sensor Temperatura", ft.Icons.THERMOSTAT),
            check_status(hums, "Sensor Humedad", ft.Icons.WATER_DROP),
            check_status(winds, "Anemómetro (Viento)", ft.Icons.AIR),
            check_status(smokes, "Detector Humo/Gas", ft.Icons.CLOUD),
            check_status(doors, "Control Puertas", ft.Icons.SENSOR_DOOR),
            check_status(lights, "Control Iluminación", ft.Icons.LIGHTBULB),
        ]

        return health_report

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

    # Los datos que va a mostrar el historial
    def get_all_history_logs(self) -> List[Dict[str, Any]]:
        """
        Recopila TODOS los eventos (Sensores, Puertas, Luces, etc.)
        y los devuelve unificados y ordenados por fecha.
        """
        history = []

        # 1. Helper para normalizar datos
        def add_records(source_list, type_label, detail_key):
            for item in source_list:
                # Extraer timestamp
                if isinstance(item, dict):
                    ts = item.get("timestamp", 0)
                    val = item.get(detail_key, "--")
                    # Intentamos sacar un estado o status si existe
                    status = item.get("status", "Info")
                    # Para puertas/luces el estado es diferente
                    if type_label == "Puerta":
                        status = "Abierta" if item.get("is_open") else "Cerrada"
                    elif type_label == "Luz":
                        status = "ON" if item.get("is_on") else "OFF"
                else:
                    # Es un Objeto (Model)
                    ts = getattr(item, "timestamp", 0)
                    val = getattr(item, detail_key, "--")
                    status = getattr(item, "status", "Info")
                    if type_label == "Puerta":
                        status = (
                            "Abierta" if getattr(item, "is_open", False) else "Cerrada"
                        )
                    elif type_label == "Luz":
                        status = "ON" if getattr(item, "is_on", False) else "OFF"

                # Formatear hora
                try:
                    time_str = datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
                except:
                    time_str = "Error fecha"

                history.append(
                    {
                        "timestamp": ts,  # Para ordenar
                        "time_str": time_str,
                        "type": type_label,
                        "location": "Zona Parque",  # Podrías sacarlo del modelo si existiera
                        "detail": f"{val}",
                        "status": str(status),
                    }
                )

        # 2. Cargar datos de los repos
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
        add_records(
            Door_Repository.load_all_door_events(), "Puerta", "name"
        )  # En puerta el detalle es el nombre
        add_records(Light_Repository.load_all_light_events(), "Luz", "value")

        # 3. Ordenar por fecha (el más nuevo primero)
        history.sort(key=lambda x: x["timestamp"], reverse=True)

        return history

    def _calculate_occupancy(self) -> int:
        """
        Calcula el aforo leyendo tu DoorModel.
        Compatible tanto si el Repo devuelve objetos DoorModel como diccionarios.
        """
        events = Door_Repository.load_all_door_events()
        count = 0

        for e in events:
            # -------------------------------------------------------
            # 1. EXTRACCIÓN DE DATOS (Híbrida: Objeto o Dict)
            # -------------------------------------------------------
            if isinstance(e, DoorModel):
                # Es tu clase DoorModel
                is_open = e.is_open
                direction = e.direction
            elif isinstance(e, dict):
                # Es un diccionario (JSON crudo)
                is_open = e.get("is_open")
                direction = e.get("direction", "IN")
            else:
                continue  # Dato desconocido

            # -------------------------------------------------------
            # 2. LÓGICA DE CONTEO
            # -------------------------------------------------------
            # Convertimos a string y minúsculas para asegurar comparación (True/"true")
            val_open_str = str(is_open).lower()

            # Solo contamos si la puerta se abrió (True, "true", 1)
            if val_open_str in ("true", "1", "yes"):

                # Normalizamos dirección a Mayúsculas ("In" -> "IN")
                dir_str = str(direction).upper()

                if dir_str == "IN":
                    count += 1
                elif dir_str == "OUT":
                    count -= 1

        # Evitamos aforos negativos
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
