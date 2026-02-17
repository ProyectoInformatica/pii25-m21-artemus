from typing import List, Dict, Any
from datetime import datetime
from ArtemusPark.database.DB_Manager import db_manager
from ArtemusPark.model.Smoke_Model import SmokeModel


def _serialize(measurement: SmokeModel) -> Dict[str, Any]:
    """Convierte el modelo a un diccionario."""
    return {
        "sensor_id": measurement.sensor_id,
        "timestamp": datetime.fromtimestamp(measurement.timestamp),
        "value": float(measurement.value),
        "status": measurement.status,
    }


def save_smoke_measurement(measurement: SmokeModel) -> int:
    """Guarda un registro de humo en la base de datos."""
    data = _serialize(measurement)
    query = """
        INSERT INTO smoke_measurements (sensor_id, timestamp, value, status)
        VALUES (%s, %s, %s, %s)
    """
    return db_manager.execute_insert(query, (
        data["sensor_id"], 
        data["timestamp"], 
        data["value"], 
        data["status"]
    ))


def load_all_smoke_measurements(limit: int = 1000) -> List[Dict[str, Any]]:
    """Carga todos los registros de humo."""
    query = """
        SELECT sensor_id, timestamp, value, status
        FROM smoke_measurements
        ORDER BY timestamp DESC
        LIMIT %s
    """
    return db_manager.execute_query(query, (limit,))


def load_smoke_by_sensor(sensor_id: str, limit: int = 100) -> List[Dict[str, Any]]:
    """Carga registros de humo para un sensor específico."""
    query = """
        SELECT sensor_id, timestamp, value, status
        FROM smoke_measurements
        WHERE sensor_id = %s
        ORDER BY timestamp DESC
        LIMIT %s
    """
    return db_manager.execute_query(query, (sensor_id, limit))


def load_smoke_by_date_range(start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
    """Carga registros de humo en un rango de fechas."""
    query = """
        SELECT sensor_id, timestamp, value, status
        FROM smoke_measurements
        WHERE timestamp BETWEEN %s AND %s
        ORDER BY timestamp DESC
    """
    return db_manager.execute_query(query, (start_date, end_date))


def get_latest_smoke_by_sensor(sensor_id: str) -> Dict[str, Any]:
    """Obtiene la última medición de humo de un sensor."""
    query = """
        SELECT sensor_id, timestamp, value, status
        FROM smoke_measurements
        WHERE sensor_id = %s
        ORDER BY timestamp DESC
        LIMIT 1
    """
    result = db_manager.execute_query(query, (sensor_id,))
    return result[0] if result else None


def get_smoke_alerts(threshold: float = 50.0) -> List[Dict[str, Any]]:
    """Obtiene mediciones de humo que superan un umbral (alertas)."""
    query = """
        SELECT sensor_id, timestamp, value, status
        FROM smoke_measurements
        WHERE value > %s
        ORDER BY timestamp DESC
    """
    return db_manager.execute_query(query, (threshold,))
