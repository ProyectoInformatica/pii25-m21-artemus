from typing import List, Dict, Any, Optional
from datetime import datetime
from ArtemusPark.database.DB_Manager import db_manager
from ArtemusPark.model.Light_Model import LightModel


def _serialize(event: LightModel) -> Dict[str, Any]:
    """Convierte el modelo a un diccionario."""
    return {
        "sensor_id": event.sensor_id,
        "timestamp": datetime.fromtimestamp(event.timestamp),
        "value": float(event.value) if hasattr(event, 'value') else (1.0 if event.is_on else 0.0),
        "status": event.status,
    }


def save_light_event(event: LightModel) -> int:
    """Guarda un evento de luz en la base de datos."""
    data = _serialize(event)
    query = """
        INSERT INTO light_measurements (sensor_id, timestamp, value, status)
        VALUES (%s, %s, %s, %s)
    """
    return db_manager.execute_insert(query, (
        data["sensor_id"], 
        data["timestamp"], 
        data["value"], 
        data["status"]
    ))


def load_all_light_events(limit: int = 1000) -> List[Dict[str, Any]]:
    """Carga todos los eventos de luz."""
    query = """
        SELECT sensor_id, timestamp, value, status
        FROM light_measurements
        ORDER BY timestamp DESC
        LIMIT %s
    """
    return db_manager.execute_query(query, (limit,))


def load_light_events_by_sensor(sensor_id: str, limit: int = 100) -> List[Dict[str, Any]]:
    """Carga eventos de luz para un sensor específico."""
    query = """
        SELECT sensor_id, timestamp, value, status
        FROM light_measurements
        WHERE sensor_id = %s
        ORDER BY timestamp DESC
        LIMIT %s
    """
    return db_manager.execute_query(query, (sensor_id, limit))


def load_light_events_by_date_range(start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
    """Carga eventos de luz en un rango de fechas."""
    query = """
        SELECT sensor_id, timestamp, value, status
        FROM light_measurements
        WHERE timestamp BETWEEN %s AND %s
        ORDER BY timestamp DESC
    """
    return db_manager.execute_query(query, (start_date, end_date))


def get_latest_light_by_sensor(sensor_id: str) -> Optional[Dict[str, Any]]:
    """Obtiene la última medición de luz de un sensor."""
    query = """
        SELECT sensor_id, timestamp, value, status
        FROM light_measurements
        WHERE sensor_id = %s
        ORDER BY timestamp DESC
        LIMIT 1
    """
    result = db_manager.execute_query(query, (sensor_id,))
    return result[0] if result else None


def get_active_lights() -> List[Dict[str, Any]]:
    """Obtiene las luces actualmente encendidas."""
    query = """
        SELECT l1.sensor_id, l1.timestamp, l1.value, l1.status
        FROM light_measurements l1
        INNER JOIN (
            SELECT sensor_id, MAX(timestamp) as max_timestamp
            FROM light_measurements
            GROUP BY sensor_id
        ) l2 ON l1.sensor_id = l2.sensor_id AND l1.timestamp = l2.max_timestamp
        WHERE l1.value > 0
    """
    return db_manager.execute_query(query)
