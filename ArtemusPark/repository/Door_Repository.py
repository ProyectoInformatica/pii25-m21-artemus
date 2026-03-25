import mysql.connector
from datetime import datetime
from typing import List, Dict, Any

from ArtemusPark.model.Door_Model import DoorModel
from ArtemusPark.bbdd.db_connection import get_connection, get_sensor_id

TIPO_NOMBRE = "Puerta"


def save_door_event(event: DoorModel) -> None:
    sensor_id = get_sensor_id(event.sensor_id, TIPO_NOMBRE)
    ts = datetime.fromtimestamp(event.timestamp)
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Dato (id_sensor, estado, timestamp) VALUES (%s, %s, %s)",
            (sensor_id, event.is_open, ts),
        )
        id_dato = cursor.lastrowid
        cursor.execute(
            "INSERT INTO Puerta (id_dato, nombre_usuario, entrada_salida) VALUES (%s, %s, %s)",
            (id_dato, event.username, event.direction),
        )
        conn.commit()
        cursor.close()
    except mysql.connector.Error:
        conn.rollback()
        raise
    finally:
        conn.close()


def load_all_door_events() -> List[Dict[str, Any]]:
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT s.nombre AS sensor_id,
                   UNIX_TIMESTAMP(d.timestamp) AS timestamp,
                   d.estado AS is_open,
                   p.nombre_usuario AS username,
                   p.entrada_salida AS direction
            FROM Puerta p
            JOIN Dato d ON p.id_dato = d.id_dato
            JOIN Sensor s ON d.id_sensor = s.id_sensor
            ORDER BY d.timestamp ASC
            """
        )
        rows = cursor.fetchall()
        cursor.close()
        return rows
    finally:
        conn.close()


def load_door_events_by_date(date_str: str) -> List[Dict[str, Any]]:
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT s.nombre AS sensor_id,
                   UNIX_TIMESTAMP(d.timestamp) AS timestamp,
                   d.estado AS is_open,
                   p.nombre_usuario AS username,
                   p.entrada_salida AS direction
            FROM Puerta p
            JOIN Dato d ON p.id_dato = d.id_dato
            JOIN Sensor s ON d.id_sensor = s.id_sensor
            WHERE DATE(d.timestamp) = %s
            ORDER BY d.timestamp ASC
            """,
            (date_str,),
        )
        rows = cursor.fetchall()
        cursor.close()
        return rows
    finally:
        conn.close()
