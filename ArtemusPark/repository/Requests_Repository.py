import mysql.connector
from ArtemusPark.bbdd.db_connection import get_connection


class RequestsRepository:
    """Repositorio para gestionar tickets de mantenimiento con persistencia en MariaDB."""

    def create_request(self, username, message, request_type="sensor_change"):
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO Ticket (usuario, tipo, descripcion, estado, fecha)
                VALUES (%s, %s, %s, 'PENDING', NOW())
                """,
                (username, request_type, message),
            )
            conn.commit()
            cursor.close()
        except mysql.connector.Error:
            conn.rollback()
            raise
        finally:
            conn.close()

    def get_all_requests(self):
        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT id_ticket AS id, usuario AS user, tipo AS type,
                       descripcion AS message, estado AS status,
                       UNIX_TIMESTAMP(fecha) AS timestamp
                FROM Ticket
                ORDER BY fecha DESC
                """
            )
            rows = cursor.fetchall()
            cursor.close()
            return rows
        finally:
            conn.close()

    def update_request_status(self, request_id, new_status):
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE Ticket SET estado=%s WHERE id_ticket=%s",
                (new_status, request_id),
            )
            conn.commit()
            cursor.close()
        finally:
            conn.close()
