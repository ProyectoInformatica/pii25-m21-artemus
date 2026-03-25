import mysql.connector
from datetime import datetime
from typing import List, Dict, Any

from ArtemusPark.model.Wind_Model import WindModel
from ArtemusPark.bbdd.db_connection import get_connection, get_sensor_id

TIPO_NOMBRE = "Viento"


def save_wind_measurement(measurement: WindModel) -> None:
    sensor_id = get_sensor_id(measurement.sensor_id, TIPO_NOMBRE)
    ts = datetime.fromtimestamp(measurement.timestamp)
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Dato (id_sensor, descripcion, timestamp) VALUES (%s, %s, %s)",
            (sensor_id, measurement.state, ts),
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
        cursor.execute(
            """
            SELECT s.nombre AS sensor_id,
                   UNIX_TIMESTAMP(d.timestamp) AS timestamp,
                   v.velocidad AS speed,
                   d.descripcion AS state
            FROM Viento v
            JOIN Dato d ON v.id_dato = d.id_dato
            JOIN Sensor s ON d.id_sensor = s.id_sensor
            ORDER BY d.timestamp ASC
            """
        )
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
            SELECT s.nombre AS sensor_id,
                   UNIX_TIMESTAMP(d.timestamp) AS timestamp,
                   v.velocidad AS speed,
                   d.descripcion AS state
            FROM Viento v
            JOIN Dato d ON v.id_dato = d.id_dato
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
