from typing import List, Dict, Any, Optional
from datetime import datetime
from ArtemusPark.database.DB_Manager import db_manager
from ArtemusPark.model.Door_Model import DoorModel


def _serialize(event: DoorModel) -> Dict[str, Any]:
    """Convierte el modelo a un diccionario."""
    return {
        "sensor_id": event.sensor_id,
        "timestamp": datetime.fromtimestamp(event.timestamp),
        "status": event.direction if hasattr(event, 'direction') else ('open' if event.is_open else 'closed'),
        "is_open": event.is_open,
    }


def save_door_event(event: DoorModel) -> int:
    """Guarda un evento de puerta en la base de datos."""
    data = _serialize(event)
    query = """
        INSERT INTO door_status (sensor_id, timestamp, status, is_open)
        VALUES (%s, %s, %s, %s)
    """
    return db_manager.execute_insert(query, (
        data["sensor_id"], 
        data["timestamp"], 
        data["status"], 
        data["is_open"]
    ))


def load_all_door_events(limit: int = 1000) -> List[Dict[str, Any]]:
    """Carga todos los eventos de puertas."""
    query = """
        SELECT sensor_id, timestamp, status, is_open
        FROM door_status
        ORDER BY timestamp DESC
        LIMIT %s
    """
    return db_manager.execute_query(query, (limit,))


def load_door_events_by_sensor(sensor_id: str, limit: int = 100) -> List[Dict[str, Any]]:
    """Carga eventos de puerta para un sensor específico."""
    query = """
        SELECT sensor_id, timestamp, status, is_open
        FROM door_status
        WHERE sensor_id = %s
        ORDER BY timestamp DESC
        LIMIT %s
    """
    return db_manager.execute_query(query, (sensor_id, limit))


def load_door_events_by_date_range(start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
    """Carga eventos de puerta en un rango de fechas."""
    query = """
        SELECT sensor_id, timestamp, status, is_open
        FROM door_status
        WHERE timestamp BETWEEN %s AND %s
        ORDER BY timestamp DESC
    """
    return db_manager.execute_query(query, (start_date, end_date))


def get_latest_door_status(sensor_id: str) -> Optional[Dict[str, Any]]:
    """Obtiene el último estado de una puerta."""
    query = """
        SELECT sensor_id, timestamp, status, is_open
        FROM door_status
        WHERE sensor_id = %s
        ORDER BY timestamp DESC
        LIMIT 1
    """
    result = db_manager.execute_query(query, (sensor_id,))
    return result[0] if result else None


def get_open_doors() -> List[Dict[str, Any]]:
    """Obtiene todas las puertas actualmente abiertas."""
    query = """
        SELECT d1.sensor_id, d1.timestamp, d1.status, d1.is_open
        FROM door_status d1
        INNER JOIN (
            SELECT sensor_id, MAX(timestamp) as max_timestamp
            FROM door_status
            GROUP BY sensor_id
        ) d2 ON d1.sensor_id = d2.sensor_id AND d1.timestamp = d2.max_timestamp
        WHERE d1.is_open = TRUE
    """
    return db_manager.execute_query(query)
