import mysql.connector
from datetime import datetime
from typing import List, Dict, Any

from ArtemusPark.model.Wind_Model import WindModel
from ArtemusPark.bbdd.db_connection import get_connection, get_sensor_id

TIPO_NOMBRE = "Wind"


def save_wind_measurement(measurement: WindModel) -> None:
    """Saves a wind measurement to the database."""
    sensor_id = get_sensor_id(measurement.sensor_id, TIPO_NOMBRE)
    ts = datetime.fromtimestamp(measurement.timestamp)
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Measurement (id_sensor, description, timestamp) VALUES (%s, %s, %s)",
            (sensor_id, measurement.state, ts),
        )
        id_measurement = cursor.lastrowid
        cursor.execute(
            "INSERT INTO Wind (id_measurement, direction, speed) VALUES (%s, %s, %s)",
            (id_measurement, "N", measurement.speed),
        )
        conn.commit()
        cursor.close()
    except mysql.connector.Error:
        conn.rollback()
        raise
    finally:
        conn.close()


def load_all_wind_measurements() -> List[Dict[str, Any]]:
    """Loads all wind measurements from the database."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT s.name AS sensor_id,
                   UNIX_TIMESTAMP(m.timestamp) AS timestamp,
                   v.direction AS direction,
                   v.speed AS speed,
                   m.description AS state
            FROM Wind v
            JOIN Measurement m ON v.id_measurement = m.id_measurement
            JOIN Sensor s ON m.id_sensor = s.id_sensor
            ORDER BY m.timestamp ASC
            """)
        rows = cursor.fetchall()
        cursor.close()
        return rows
    finally:
        conn.close()


def load_wind_measurements_by_date(date_str: str) -> List[Dict[str, Any]]:
    """Loads wind measurements for a specific date."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT s.name AS sensor_id,
                   UNIX_TIMESTAMP(m.timestamp) AS timestamp,
                   v.direction AS direction,
                   v.speed AS speed,
                   m.description AS state
            FROM Wind v
            JOIN Measurement m ON v.id_measurement = m.id_measurement
            JOIN Sensor s ON m.id_sensor = s.id_sensor
            WHERE DATE(m.timestamp) = %s
            ORDER BY m.timestamp ASC
            """,
            (date_str,),
        )
        rows = cursor.fetchall()
        cursor.close()
        return rows
    finally:
        conn.close()
