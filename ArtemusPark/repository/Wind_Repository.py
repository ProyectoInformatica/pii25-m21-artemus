import mysql.connector
from datetime import datetime
from typing import List, Dict, Any

from ArtemusPark.model.Wind_Model import WindModel
from ArtemusPark.bbdd.db_connection import get_connection, get_tipo_id

TIPO_NOMBRE = "Viento"


def save_wind_measurement(measurement: WindModel) -> None:
    tipo_id = get_tipo_id(TIPO_NOMBRE)
    ts = datetime.fromtimestamp(measurement.timestamp)
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Dato (id_tipo, sensor_codigo, descripcion, timestamp) VALUES (%s, %s, %s, %s)",
            (tipo_id, measurement.sensor_id, measurement.state, ts),
        )
        id_dato = cursor.lastrowid
        cursor.execute(
            "INSERT INTO Viento (id_dato, velocidad) VALUES (%s, %s)",
            (id_dato, measurement.speed),
        )
        conn.commit()
        cursor.close()
    except mysql.connector.Error:
        conn.rollback()
        raise
    finally:
        conn.close()


def load_all_wind_measurements() -> List[Dict[str, Any]]:
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT d.sensor_codigo AS sensor_id,
                   UNIX_TIMESTAMP(d.timestamp) AS timestamp,
                   v.velocidad AS speed,
                   d.descripcion AS state
            FROM Viento v
            JOIN Dato d ON v.id_dato = d.id_dato
            ORDER BY d.timestamp ASC
            """)
        rows = cursor.fetchall()
        cursor.close()
        return rows
    finally:
        conn.close()


def load_wind_measurements_by_date(date_str: str) -> List[Dict[str, Any]]:
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT d.sensor_codigo AS sensor_id,
                   UNIX_TIMESTAMP(d.timestamp) AS timestamp,
                   v.velocidad AS speed,
                   d.descripcion AS state
            FROM Viento v
            JOIN Dato d ON v.id_dato = d.id_dato
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
