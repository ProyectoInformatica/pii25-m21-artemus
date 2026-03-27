import mysql.connector
from datetime import datetime
from typing import List, Dict, Any

from ArtemusPark.model.Door_Model import DoorModel
from ArtemusPark.bbdd.db_connection import get_connection, get_sensor_id

TIPO_NOMBRE = "Door"


def save_door_event(event: DoorModel) -> None:
    """Saves a door event to the database."""
    sensor_id = get_sensor_id(event.sensor_id, TIPO_NOMBRE)
    ts = datetime.fromtimestamp(event.timestamp)
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Measurement (id_sensor, status, timestamp) VALUES (%s, %s, %s)",
            (sensor_id, event.is_open, ts),
        )
        id_measurement = cursor.lastrowid
        cursor.execute(
            "INSERT INTO Door (id_measurement, username, entry_exit) VALUES (%s, %s, %s)",
            (id_measurement, event.username, event.direction),
        )
        conn.commit()
        cursor.close()
    except mysql.connector.Error:
        conn.rollback()
        raise
    finally:
        conn.close()


def load_all_door_events() -> List[Dict[str, Any]]:
    """Loads all door events from the database."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT s.name AS sensor_id,
                   UNIX_TIMESTAMP(m.timestamp) AS timestamp,
                   m.status AS is_open,
                   p.username AS username,
                   p.entry_exit AS direction
            FROM Door p
            JOIN Measurement m ON p.id_measurement = m.id_measurement
            JOIN Sensor s ON m.id_sensor = s.id_sensor
            ORDER BY m.timestamp ASC
            """)
        rows = cursor.fetchall()
        cursor.close()
        return rows
    finally:
        conn.close()


def load_door_events_by_date(date_str: str) -> List[Dict[str, Any]]:
    """Loads door events for a specific date."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT s.name AS sensor_id,
                   UNIX_TIMESTAMP(m.timestamp) AS timestamp,
                   m.status AS is_open,
                   p.username AS username,
                   p.entry_exit AS direction
            FROM Door p
            JOIN Measurement m ON p.id_measurement = m.id_measurement
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
