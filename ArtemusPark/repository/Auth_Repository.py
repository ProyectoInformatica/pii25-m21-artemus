import json
import mysql.connector
from ArtemusPark.bbdd.db_connection import get_connection


class AuthRepository:
    """Repository to handle user authentication using MySQL SHA2 function."""

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
        """Returns all users from English tables."""
        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True, buffered=True)
            cursor.execute("""
                SELECT u.username, u.full_name, u.password_hash, u.dni,
                       u.phone, u.address_street, u.address_city, u.address_zip, r.role, u.active
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

                sub_cursor.execute(
                    "SELECT u.username FROM User_Hierarchy h JOIN User u ON h.superior_dni = u.dni WHERE h.subordinate_dni = %s",
                    (dni,),
                )
                supervisors = [s[0] for s in sub_cursor.fetchall()]

                sub_cursor.execute(
                    "SELECT u.username FROM User_Hierarchy h JOIN User u ON h.subordinate_dni = u.dni WHERE h.superior_dni = %s",
                    (dni,),
                )
                subordinates = [s[0] for s in sub_cursor.fetchall()]
                sub_cursor.close()

                full_address = f"{row['address_street']}, {row['address_city']} ({row['address_zip']})"

                result[username] = {
                    "password": row["password_hash"],
                    "role": row["role"],
                    "full_name": row["full_name"],
                    "dni": dni,
                    "phone": row["phone"] or "",
                    "address": full_address.strip(", "),
                    "assigned_sensors": sensors,
                    "supervisors": supervisors,
                    "subordinates": subordinates,
                }

            cursor.close()
            return result
        finally:
            conn.close()

    def get_user_by_username(self, username):
        """Returns data for a single user by username."""
        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True, buffered=True)
            cursor.execute(
                """
                SELECT u.username, u.full_name, u.password_hash, u.dni,
                       u.phone, u.address_street, u.address_city, u.address_zip, r.role, u.active
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

            sub_cursor.execute(
                "SELECT u.username FROM User_Hierarchy h JOIN User u ON h.superior_dni = u.dni WHERE h.subordinate_dni = %s",
                (dni,),
            )
            supervisors = [s[0] for s in sub_cursor.fetchall()]

            sub_cursor.execute(
                "SELECT u.username FROM User_Hierarchy h JOIN User u ON h.subordinate_dni = u.dni WHERE h.superior_dni = %s",
                (dni,),
            )
            subordinates = [s[0] for s in sub_cursor.fetchall()]
            sub_cursor.close()

            full_address = (
                f"{row['address_street']}, {row['address_city']} ({row['address_zip']})"
            )

            result = {
                "password": row["password_hash"],
                "role": row["role"],
                "full_name": row["full_name"],
                "dni": dni,
                "phone": row["phone"] or "",
                "address": full_address.strip(", "),
                "assigned_sensors": sensors,
                "supervisors": supervisors,
                "subordinates": subordinates,
            }
            cursor.close()
            return result
        finally:
            conn.close()

    def add_user(
        self, username, password, role, full_name="", dni="", phone="", address=""
    ):
        """Inserts a user and hashes the password directly in MySQL."""
        conn = get_connection()
        try:
            cursor = conn.cursor(buffered=True)
            cursor.execute("SELECT id_role FROM Role WHERE role = %s", (role,))
            row = cursor.fetchone()
            if not row:
                raise ValueError(f"Role '{role}' does not exist.")

            id_role = row[0]
            parts = address.split(",")
            street = parts[0].strip() if len(parts) > 0 else address
            city = parts[1].strip() if len(parts) > 1 else ""
            zip_code = parts[2].strip() if len(parts) > 2 else ""

            query = """
                INSERT INTO User
                    (dni, id_role, username, full_name, password_hash, phone, 
                     address_street, address_city, address_zip, active)
                VALUES (%s, %s, %s, %s, SHA2(%s, 256), %s, %s, %s, %s, TRUE)
            """
            cursor.execute(
                query,
                (
                    dni,
                    id_role,
                    username,
                    full_name,
                    password,
                    phone,
                    street,
                    city,
                    zip_code,
                ),
            )
            conn.commit()
            cursor.close()
        except mysql.connector.Error:
            conn.rollback()
            raise
        finally:
            conn.close()

    def update_user(self, username, **kwargs):
        """Updates user data and hashes the password in MySQL if provided."""
        conn = get_connection()
        try:
            cursor = conn.cursor(buffered=True)

            # Update password
            if "password" in kwargs:
                cursor.execute(
                    "UPDATE User SET password_hash=SHA2(%s, 256) WHERE username=%s",
                    (kwargs["password"], username),
                )

            # Update basic info
            if "full_name" in kwargs:
                cursor.execute(
                    "UPDATE User SET full_name=%s WHERE username=%s",
                    (kwargs["full_name"], username),
                )

            if "dni" in kwargs:
                cursor.execute(
                    "UPDATE User SET dni=%s WHERE username=%s",
                    (kwargs["dni"], username),
                )

            if "phone" in kwargs:
                cursor.execute(
                    "UPDATE User SET phone=%s WHERE username=%s",
                    (kwargs["phone"], username),
                )

            # Update Profile Picture (Binary Data)
            if "profile_picture" in kwargs:
                cursor.execute(
                    "UPDATE User SET profile_picture=%s WHERE username=%s",
                    (kwargs["profile_picture"], username),
                )

            # Update Role
            if "role" in kwargs:
                cursor.execute(
                    "SELECT id_role FROM Role WHERE role = %s", (kwargs["role"],)
                )
                row = cursor.fetchone()
                if row:
                    cursor.execute(
                        "UPDATE User SET id_role=%s WHERE username=%s",
                        (row[0], username),
                    )

            # Update Address
            if "address" in kwargs:
                parts = kwargs["address"].split(",")
                street = parts[0].strip() if len(parts) > 0 else kwargs["address"]
                city = parts[1].strip() if len(parts) > 1 else ""
                zip_code = parts[2].strip() if len(parts) > 2 else ""
                cursor.execute(
                    "UPDATE User SET address_street=%s, address_city=%s, address_zip=%s WHERE username=%s",
                    (street, city, zip_code, username),
                )

            # Update Sensors
            if "assigned_sensors" in kwargs:
                cursor.execute("SELECT dni FROM User WHERE username=%s", (username,))
                res = cursor.fetchone()
                if res:
                    dni = res[0]
                    cursor.execute("DELETE FROM User_Sensor WHERE dni=%s", (dni,))
                    for s_id in kwargs["assigned_sensors"]:
                        cursor.execute(
                            "INSERT INTO User_Sensor (dni, id_sensor) VALUES (%s, %s)",
                            (dni, s_id),
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
            return row[0] if row else None
        finally:
            conn.close()

    def delete_user(self, username):
        """Logical deletion in 'User' table."""
        conn = get_connection()
        try:
            cursor = conn.cursor(buffered=True)
            cursor.execute(
                "UPDATE User SET active = FALSE WHERE username=%s", (username,)
            )
            conn.commit()
            cursor.close()
        finally:
            conn.close()
