import json
import mysql.connector
from ArtemusPark.bbdd.db_connection import get_connection


class AuthRepository:
    """Repository to handle user authentication using individual permissions stored in User table."""

    def get_user_permissions(self, username):
        """Returns a list of permission descriptions for the user from permissions_list column."""
        conn = get_connection()
        try:
            cursor = conn.cursor(buffered=True)
            # We now read from the new column in User table
            query = "SELECT permissions_list FROM User WHERE username = %s AND active = TRUE"
            cursor.execute(query, (username,))
            row = cursor.fetchone()
            cursor.close()

            if row and row[0]:
                return [p.strip() for p in row[0].split(",") if p.strip()]
            return []
        finally:
            conn.close()

    def authenticate(self, username, password):
        """Verifies credentials using MySQL's SHA2(password, 256) function."""
        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True, buffered=True)
            query = """
                SELECT r.role FROM User u
                JOIN Role r ON u.id_role = r.id_role
                WHERE u.username = %s AND u.password_hash = SHA2(%s, 256) AND u.active = TRUE
            """
            cursor.execute(query, (username, password))
            row = cursor.fetchone()
            cursor.close()
            return row["role"] if row else None
        finally:
            conn.close()

    def get_all_users(self):
        """Returns all users including their individual permissions_list."""
        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True, buffered=True)
            cursor.execute("""
                SELECT u.username, u.full_name, u.password_hash, u.dni,
                       u.phone, u.address_street, u.address_city, u.address_zip, 
                       r.role, u.active, u.permissions_list
                FROM User u
                JOIN Role r ON u.id_role = r.id_role
                WHERE u.active = TRUE
                """)
            rows = cursor.fetchall()

            result = {}
            for row in rows:
                username = row["username"]
                dni = row["dni"]

                sub_cursor = conn.cursor(buffered=True)
                sub_cursor.execute(
                    "SELECT id_sensor FROM User_Sensor WHERE dni = %s", (dni,)
                )
                sensors = [s[0] for s in sub_cursor.fetchall()]
                sub_cursor.close()

                result[username] = {
                    "password": row["password_hash"],
                    "role": row["role"],
                    "full_name": row["full_name"],
                    "dni": dni,
                    "phone": row["phone"] or "",
                    "address_street": row["address_street"] or "",
                    "address_city": row["address_city"] or "",
                    "address_zip": row["address_zip"] or "",
                    "assigned_sensors": sensors,
                    "permissions": [
                        p.strip()
                        for p in (row["permissions_list"] or "").split(",")
                        if p.strip()
                    ],
                }
            cursor.close()
            return result
        finally:
            conn.close()

    def get_user_by_username(self, username):
        """Returns full data for a single user."""
        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True, buffered=True)
            cursor.execute(
                """
                SELECT u.*, r.role 
                FROM User u 
                JOIN Role r ON u.id_role = r.id_role
                WHERE u.username = %s AND u.active = TRUE
                """,
                (username,),
            )
            row = cursor.fetchone()
            if not row:
                cursor.close()
                return {}

            dni = row["dni"]
            sub_cursor = conn.cursor(buffered=True)
            sub_cursor.execute(
                "SELECT id_sensor FROM User_Sensor WHERE dni = %s", (dni,)
            )
            sensors = [s[0] for s in sub_cursor.fetchall()]
            sub_cursor.close()

            result = {
                "password": row["password_hash"],
                "role": row["role"],
                "full_name": row["full_name"],
                "dni": dni,
                "phone": row["phone"] or "",
                "address_street": row["address_street"] or "",
                "address_city": row["address_city"] or "",
                "address_zip": row["address_zip"] or "",
                "assigned_sensors": sensors,
                "permissions": [
                    p.strip()
                    for p in (row["permissions_list"] or "").split(",")
                    if p.strip()
                ],
            }
            cursor.close()
            return result
        finally:
            conn.close()

    def add_user(self, username, password, role, permissions=None, **kwargs):
        """Inserts a user with individual permissions."""
        conn = get_connection()
        try:
            cursor = conn.cursor(buffered=True)
            cursor.execute("SELECT id_role FROM Role WHERE role = %s", (role,))
            role_row = cursor.fetchone()
            id_role = role_row[0] if role_row else 3  # Default to user

            perms_str = ",".join(permissions) if permissions else ""

            query = """
                INSERT INTO User
                    (dni, id_role, username, full_name, password_hash, phone, 
                     address_street, address_city, address_zip, active, permissions_list)
                VALUES (%s, %s, %s, %s, SHA2(%s, 256), %s, %s, %s, %s, TRUE, %s)
            """
            cursor.execute(
                query,
                (
                    kwargs.get("dni"),
                    id_role,
                    username,
                    kwargs.get("full_name"),
                    password,
                    kwargs.get("phone"),
                    kwargs.get("address_street"),
                    kwargs.get("address_city"),
                    kwargs.get("address_zip"),
                    perms_str,
                ),
            )
            conn.commit()
            cursor.close()
        finally:
            conn.close()

    def update_user(self, dni, permissions=None, **kwargs):
        """Updates user data including individual permissions."""
        conn = get_connection()
        try:
            cursor = conn.cursor(buffered=True)

            if "password" in kwargs:
                cursor.execute(
                    "UPDATE User SET password_hash=SHA2(%s, 256) WHERE dni=%s",
                    (kwargs["password"], dni),
                )

            if "full_name" in kwargs:
                cursor.execute(
                    "UPDATE User SET full_name=%s WHERE dni=%s",
                    (kwargs["full_name"], dni),
                )

            if "phone" in kwargs:
                cursor.execute(
                    "UPDATE User SET phone=%s WHERE dni=%s", (kwargs["phone"], dni)
                )

            if "role" in kwargs:
                cursor.execute(
                    "SELECT id_role FROM Role WHERE role = %s", (kwargs["role"],)
                )
                row = cursor.fetchone()
                if row:
                    cursor.execute(
                        "UPDATE User SET id_role=%s WHERE dni=%s", (row[0], dni)
                    )

            if permissions is not None:
                perms_str = ",".join(permissions)
                cursor.execute(
                    "UPDATE User SET permissions_list=%s WHERE dni=%s", (perms_str, dni)
                )

            conn.commit()
            cursor.close()
        finally:
            conn.close()

    def get_user_profile_picture(self, username):
        """Returns the profile picture binary data for a user."""
        conn = get_connection()
        try:
            cursor = conn.cursor(buffered=True)
            cursor.execute(
                "SELECT profile_picture FROM User WHERE username = %s", (username,)
            )
            row = cursor.fetchone()
            return bytes(row[0]) if row and row[0] else None
        finally:
            conn.close()

    def delete_user(self, dni):
        """Logical deletion."""
        conn = get_connection()
        try:
            cursor = conn.cursor(buffered=True)
            cursor.execute("UPDATE User SET active = FALSE WHERE dni=%s", (dni,))
            conn.commit()
        finally:
            conn.close()

    def get_all_permissions(self):
        """Returns all available permissions in the system."""
        conn = get_connection()
        try:
            cursor = conn.cursor(buffered=True)
            cursor.execute("SELECT description FROM Permission")
            return [row[0] for row in cursor.fetchall()]
        finally:
            conn.close()
