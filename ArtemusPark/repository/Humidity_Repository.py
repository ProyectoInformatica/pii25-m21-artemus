import mysql.connector
from datetime import datetime
from typing import List, Dict, Any

from ArtemusPark.model.Humidity_Model import HumidityModel
from ArtemusPark.database.db_connection import get_connection, get_sensor_id

TIPO_NOMBRE = "Humidity"


def save_humidity_measurement(measurement: HumidityModel) -> None:
    """Saves a humidity measurement to the database."""
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
            "INSERT INTO Humidity (id_measurement, relative_humidity) VALUES (%s, %s)",
            (id_measurement, measurement.value),
        )
        conn.commit()
        cursor.close()
    except mysql.connector.Error:
        conn.rollback()
        raise
    finally:
        conn.close()


def load_all_humidity_measurements() -> List[Dict[str, Any]]:
    """Loads all humidity measurements from the database."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT s.name AS sensor_id,
                   UNIX_TIMESTAMP(m.timestamp) AS timestamp,
                   h.relative_humidity AS value,
                   m.description AS status
            FROM Humidity h
            JOIN Measurement m ON h.id_measurement = m.id_measurement
            JOIN Sensor s ON m.id_sensor = s.id_sensor
            ORDER BY m.timestamp ASC
            """)
        rows = cursor.fetchall()
        cursor.close()
        return rows
    finally:
        conn.close()


def load_humidity_measurements_by_date(date_str: str) -> List[Dict[str, Any]]:
    """Loads humidity measurements for a specific date."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT s.name AS sensor_id,
                   UNIX_TIMESTAMP(m.timestamp) AS timestamp,
                   h.relative_humidity AS value,
                   m.description AS status
            FROM Humidity h
            JOIN Measurement m ON h.id_measurement = m.id_measurement
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
