import mysql.connector
from datetime import datetime
from typing import List, Dict, Any

from ArtemusPark.model.Light_Model import LightModel
from ArtemusPark.database.db_connection import get_connection, get_sensor_id

TIPO_NOMBRE = "Lighting"


def save_light_event(event: LightModel) -> None:
    """Saves a lighting event to the database."""
    sensor_id = get_sensor_id(event.sensor_id, TIPO_NOMBRE)
    ts = datetime.fromtimestamp(event.timestamp)
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Measurement (id_sensor, description, timestamp) VALUES (%s, %s, %s)",
            (sensor_id, event.status, ts),
        )
        id_measurement = cursor.lastrowid
        cursor.execute(
            "INSERT INTO Lighting (id_measurement, is_on, value) VALUES (%s, %s, %s)",
            (id_measurement, event.is_on, event.value),
        )
        conn.commit()
        cursor.close()
    except mysql.connector.Error:
        conn.rollback()
        raise
    finally:
        conn.close()


def load_all_light_events() -> List[Dict[str, Any]]:
    """Loads all lighting events from the database."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT s.name AS sensor_id,
                   UNIX_TIMESTAMP(m.timestamp) AS timestamp,
                   i.is_on AS is_on,
                   i.value AS value,
                   m.description AS status
            FROM Lighting i
            JOIN Measurement m ON i.id_measurement = m.id_measurement
            JOIN Sensor s ON m.id_sensor = s.id_sensor
            ORDER BY m.timestamp ASC
            """)
        rows = cursor.fetchall()
        cursor.close()
        return rows
    finally:
        conn.close()


def load_light_events_by_date(date_str: str) -> List[Dict[str, Any]]:
    """Loads lighting events for a specific date."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT s.name AS sensor_id,
                   UNIX_TIMESTAMP(m.timestamp) AS timestamp,
                   i.is_on AS is_on,
                   i.value AS value,
                   m.description AS status
            FROM Lighting i
            JOIN Measurement m ON i.id_measurement = m.id_measurement
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
