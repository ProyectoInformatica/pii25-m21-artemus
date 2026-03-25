import mysql.connector
from datetime import datetime
from typing import List, Dict, Any

from ArtemusPark.model.Smoke_Model import SmokeModel
from ArtemusPark.bbdd.db_connection import get_connection, get_sensor_id

TIPO_NOMBRE = "Calidad_Aire"


def save_smoke_measurement(measurement: SmokeModel) -> None:
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
            "INSERT INTO Calidad_Aire (id_dato, nivel_co2) VALUES (%s, %s)",
            (id_dato, measurement.value),
        )
        conn.commit()
        cursor.close()
    except mysql.connector.Error:
        conn.rollback()
        raise
    finally:
        conn.close()


def load_all_smoke_measurements() -> List[Dict[str, Any]]:
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT s.nombre AS sensor_id,
                   UNIX_TIMESTAMP(d.timestamp) AS timestamp,
                   ca.nivel_co2 AS value,
                   d.descripcion AS status
            FROM Calidad_Aire ca
            JOIN Dato d ON ca.id_dato = d.id_dato
            JOIN Sensor s ON d.id_sensor = s.id_sensor
            ORDER BY d.timestamp ASC
            """
        )
        rows = cursor.fetchall()
        cursor.close()
        return rows
    finally:
        conn.close()


def load_smoke_measurements_by_date(date_str: str) -> List[Dict[str, Any]]:
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT s.nombre AS sensor_id,
                   UNIX_TIMESTAMP(d.timestamp) AS timestamp,
                   ca.nivel_co2 AS value,
                   d.descripcion AS status
            FROM Calidad_Aire ca
            JOIN Dato d ON ca.id_dato = d.id_dato
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
