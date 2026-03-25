import mysql.connector
from datetime import datetime
from typing import List, Dict, Any

from ArtemusPark.model.Light_Model import LightModel
from ArtemusPark.bbdd.db_connection import get_connection, get_tipo_id

TIPO_NOMBRE = "Iluminacion"


def save_light_event(event: LightModel) -> None:
    tipo_id = get_tipo_id(TIPO_NOMBRE)
    ts = datetime.fromtimestamp(event.timestamp)
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Dato (id_tipo, sensor_codigo, descripcion, timestamp) VALUES (%s, %s, %s, %s)",
            (tipo_id, event.sensor_id, event.status, ts),
        )
        id_dato = cursor.lastrowid
        cursor.execute(
            "INSERT INTO Iluminacion (id_dato, is_on, valor) VALUES (%s, %s, %s)",
            (id_dato, event.is_on, event.value),
        )
        conn.commit()
        cursor.close()
    except mysql.connector.Error:
        conn.rollback()
        raise
    finally:
        conn.close()


def load_all_light_events() -> List[Dict[str, Any]]:
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT d.sensor_codigo AS sensor_id,
                   UNIX_TIMESTAMP(d.timestamp) AS timestamp,
                   i.is_on AS is_on,
                   i.valor AS value,
                   d.descripcion AS status
            FROM Iluminacion i
            JOIN Dato d ON i.id_dato = d.id_dato
            ORDER BY d.timestamp ASC
            """)
        rows = cursor.fetchall()
        cursor.close()
        return rows
    finally:
        conn.close()


def load_light_events_by_date(date_str: str) -> List[Dict[str, Any]]:
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT d.sensor_codigo AS sensor_id,
                   UNIX_TIMESTAMP(d.timestamp) AS timestamp,
                   i.is_on AS is_on,
                   i.valor AS value,
                   d.descripcion AS status
            FROM Iluminacion i
            JOIN Dato d ON i.id_dato = d.id_dato
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
