from typing import List, Dict, Any, Optional
from datetime import datetime
from ArtemusPark.database.DB_Manager import db_manager
from ArtemusPark.model.Wind_Model import WindModel


def _serialize_measurement(measurement: WindModel) -> Dict[str, Any]:
    """Convierte el modelo a un diccionario."""
    return {
        "sensor_id": measurement.sensor_id,
        "timestamp": datetime.fromtimestamp(measurement.timestamp),
        "value": float(measurement.speed),
        "status": measurement.state,
    }


def save_wind_measurement(measurement: WindModel) -> int:
    """Guarda un registro de viento en la base de datos."""
    data = _serialize_measurement(measurement)
    query = """
        INSERT INTO wind_measurements (sensor_id, timestamp, value, status)
        VALUES (%s, %s, %s, %s)
    """
    return db_manager.execute_insert(query, (
        data["sensor_id"], 
        data["timestamp"], 
        data["value"], 
        data["status"]
    ))


def load_all_wind_measurements(limit: int = 1000) -> List[Dict[str, Any]]:
    """Carga todos los registros de viento."""
    query = """
        SELECT sensor_id, timestamp, value, status
        FROM wind_measurements
        ORDER BY timestamp DESC
        LIMIT %s
    """
    return db_manager.execute_query(query, (limit,))


def load_wind_by_sensor(sensor_id: str, limit: int = 100) -> List[Dict[str, Any]]:
    """Carga registros de viento para un sensor específico."""
    query = """
        SELECT sensor_id, timestamp, value, status
        FROM wind_measurements
        WHERE sensor_id = %s
        ORDER BY timestamp DESC
        LIMIT %s
    """
    return db_manager.execute_query(query, (sensor_id, limit))


def load_wind_by_date_range(start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
    """Carga registros de viento en un rango de fechas."""
    query = """
        SELECT sensor_id, timestamp, value, status
        FROM wind_measurements
        WHERE timestamp BETWEEN %s AND %s
        ORDER BY timestamp DESC
    """
    return db_manager.execute_query(query, (start_date, end_date))


def get_latest_wind_by_sensor(sensor_id: str) -> Optional[Dict[str, Any]]:
    """Obtiene la última medición de viento de un sensor."""
    query = """
        SELECT sensor_id, timestamp, value, status
        FROM wind_measurements
        WHERE sensor_id = %s
        ORDER BY timestamp DESC
        LIMIT 1
    """
    result = db_manager.execute_query(query, (sensor_id,))
    return result[0] if result else None
