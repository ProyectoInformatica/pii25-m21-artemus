import mysql.connector
from datetime import datetime
from typing import List, Dict, Any

from ArtemusPark.model.Temperature_Model import TemperatureModel
from ArtemusPark.bbdd.db_connection import get_connection, get_sensor_id

TIPO_NOMBRE = "Temperature"


def save_temperature_measurement(measurement: TemperatureModel) -> None:
    """Saves a temperature measurement to the database."""
    sensor_id = get_sensor_id(measurement.sensor_id, TIPO_NOMBRE)
    ts = datetime.fromtimestamp(measurement.timestamp)
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Measurement (id_sensor, description, timestamp) VALUES (%s, %s, %s)",
            (sensor_id, measurement.status, ts),
        )
        id_measurement = cursor.lastrowid
        cursor.execute(
            "INSERT INTO Temperature (id_measurement, temperature) VALUES (%s, %s)",
            (id_measurement, measurement.value),
        )
        conn.commit()
        cursor.close()
    except mysql.connector.Error:
        conn.rollback()
        raise
    finally:
        conn.close()


def    load_all_temperature_measurements() -> List[Dict[str, Any]]:
    """Loads all temperature measurements from the database."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT s.name AS sensor_id,
                   UNIX_TIMESTAMP(m.timestamp) AS timestamp,
                   t.temperature AS value,
                   m.description AS status
            FROM Temperature t
            JOIN Measurement m ON t.id_measurement = m.id_measurement
            JOIN Sensor s ON m.id_sensor = s.id_sensor
            ORDER BY m.timestamp ASC
            """)
        rows = cursor.fetchall()
        cursor.close()
        return rows
    finally:
        conn.close()


def load_temperature_measurements_by_date(date_str: str) -> List[Dict[str, Any]]:
    """Loads temperature measurements for a specific date."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT s.name AS sensor_id,
                   UNIX_TIMESTAMP(m.timestamp) AS timestamp,
                   t.temperature AS value,
                   m.description AS status
            FROM Temperature t
            JOIN Measurement m ON t.id_measurement = m.id_measurement
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
