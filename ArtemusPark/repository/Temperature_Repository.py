import mysql.connector
from datetime import datetime
from typing import List, Dict, Any

from ArtemusPark.model.Temperature_Model import TemperatureModel
from ArtemusPark.bbdd.db_connection import get_connection, get_tipo_id

TIPO_NOMBRE = "Temperatura"


def save_temperature_measurement(measurement: TemperatureModel) -> None:
    tipo_id = get_tipo_id(TIPO_NOMBRE)
    ts = datetime.fromtimestamp(measurement.timestamp)
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Dato (id_tipo, sensor_codigo, descripcion, timestamp) VALUES (%s, %s, %s, %s)",
            (tipo_id, measurement.sensor_id, measurement.status, ts),
        )
        id_dato = cursor.lastrowid
        cursor.execute(
            "INSERT INTO Temperatura (id_dato, temperatura) VALUES (%s, %s)",
            (id_dato, measurement.value),
        )
        conn.commit()
        cursor.close()
    except mysql.connector.Error:
        conn.rollback()
        raise
    finally:
        conn.close()


def load_all_temperature_measurements() -> List[Dict[str, Any]]:
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT d.sensor_codigo AS sensor_id,
                   UNIX_TIMESTAMP(d.timestamp) AS timestamp,
                   t.temperatura AS value,
                   d.descripcion AS status
            FROM Temperatura t
            JOIN Dato d ON t.id_dato = d.id_dato
            ORDER BY d.timestamp ASC
            """)
        rows = cursor.fetchall()
        cursor.close()
        return rows
    finally:
        conn.close()


def load_temperature_measurements_by_date(date_str: str) -> List[Dict[str, Any]]:
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT d.sensor_codigo AS sensor_id,
                   UNIX_TIMESTAMP(d.timestamp) AS timestamp,
                   t.temperatura AS value,
                   d.descripcion AS status
            FROM Temperatura t
            JOIN Dato d ON t.id_dato = d.id_dato
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
