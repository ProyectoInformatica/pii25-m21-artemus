import mysql.connector
from ArtemusPark.database.db_connection import get_connection


class RequestsRepository:
    """Repository to manage maintenance tickets in the database."""

    def create_request(self, username, message, request_type="MAINTENANCE"):
        """Creates a new maintenance ticket."""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            # First, get the user's DNI from the username (case-insensitive)
            cursor.execute(
                "SELECT dni FROM User WHERE LOWER(username) = LOWER(%s)", (username,)
            )
            res = cursor.fetchone()
            if not res:
                raise ValueError(f"User '{username}' does not exist.")
            user_dni = res[0]

            cursor.execute(
                """
                INSERT INTO Ticket (user_dni, type, description, status)
                VALUES (%s, %s, %s, 'PENDING')
                """,
                (user_dni, request_type, message),
            )
            conn.commit()
            cursor.close()
        except mysql.connector.Error:
            conn.rollback()
            raise
        finally:
            conn.close()

    def create_system_incident(self, user_dni, message, incident_type):
        """Creates a pending automatic incident if one of the same type is not already open."""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id_ticket
                FROM Ticket
                WHERE user_dni = %s
                  AND type = %s
                  AND status = 'PENDING'
                LIMIT 1
                """,
                (user_dni, incident_type),
            )
            if cursor.fetchone():
                cursor.close()
                return False

            cursor.execute(
                """
                INSERT INTO Ticket (user_dni, type, description, status)
                VALUES (%s, %s, %s, 'PENDING')
                """,
                (user_dni, incident_type, message),
            )
            conn.commit()
            cursor.close()
            return True
        except mysql.connector.Error:
            conn.rollback()
            raise
        finally:
            conn.close()

    def get_all_requests(self):
        """Returns all maintenance tickets."""
        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT t.id_ticket AS id, u.username AS user, t.type,
                       t.description AS message, t.status,
                       UNIX_TIMESTAMP(t.created_at) AS timestamp
                FROM Ticket t
                JOIN User u ON t.user_dni = u.dni
                ORDER BY t.created_at DESC
                """)
            rows = cursor.fetchall()
            cursor.close()
            return rows
        finally:
            conn.close()

    def update_request_status(self, request_id, new_status):
        """Updates the status of a maintenance ticket."""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE Ticket SET status=%s WHERE id_ticket=%s",
                (new_status, request_id),
            )
            conn.commit()
            cursor.close()
        finally:
            conn.close()
