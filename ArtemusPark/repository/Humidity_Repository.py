import mysql.connector
from datetime import datetime
from typing import List, Dict, Any

from ArtemusPark.model.Humidity_Model import HumidityModel
from ArtemusPark.bbdd.db_connection import get_connection, get_sensor_id

TIPO_NOMBRE = "Humedad"


def save_humidity_measurement(measurement: HumidityModel) -> None:
    sensor_id = get_sensor_id(measurement.sensor_id, TIPO_NOMBRE)
    ts = datetime.fromtimestamp(measurement.timestamp)
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Dato (id_sensor, descripcion, timestamp) VALUES (%s, %s, %s)",
            (sensor_id, measurement.status, ts),
        )
        id_dato = cursor.lastrowid
        cursor.execute(
            "INSERT INTO Humedad (id_dato, humedad_relativa) VALUES (%s, %s)",
            (id_dato, measurement.value),
        )
        conn.commit()
        cursor.close()
    except mysql.connector.Error:
        conn.rollback()
        raise
    finally:
        conn.close()


def load_all_humidity_measurements() -> List[Dict[str, Any]]:
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT s.nombre AS sensor_id,
                   UNIX_TIMESTAMP(d.timestamp) AS timestamp,
                   h.humedad_relativa AS value,
                   d.descripcion AS status
            FROM Humedad h
            JOIN Dato d ON h.id_dato = d.id_dato
            JOIN Sensor s ON d.id_sensor = s.id_sensor
            ORDER BY d.timestamp ASC
            """)
        rows = cursor.fetchall()
        cursor.close()
        return rows
    finally:
        conn.close()


def load_humidity_measurements_by_date(date_str: str) -> List[Dict[str, Any]]:
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT s.nombre AS sensor_id,
                   UNIX_TIMESTAMP(d.timestamp) AS timestamp,
                   h.humedad_relativa AS value,
                   d.descripcion AS status
            FROM Humedad h
            JOIN Dato d ON h.id_dato = d.id_dato
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
