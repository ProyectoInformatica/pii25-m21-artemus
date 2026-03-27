import json
import mysql.connector
from ArtemusPark.bbdd.db_connection import get_connection

class AuthRepository:
    """Repository to handle user authentication using MySQL SHA2 function."""

    def get_user_permissions(self, username):
        """Returns a list of permission descriptions for the user."""
        conn = get_connection()
        try:
            cursor = conn.cursor(buffered=True)
            query = """
                SELECT p.description FROM Permission p
                JOIN Role_Permission rp ON p.id_permission = rp.id_permission
                JOIN User u ON u.id_role = rp.id_role
                WHERE u.username = %s AND u.active = TRUE
            """
            cursor.execute(query, (username,))
            perms = [row[0] for row in cursor.fetchall()]
            cursor.close()
            return perms
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
        """Returns all users from English tables."""
        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True, buffered=True)
            cursor.execute(
                """
                SELECT u.username, u.full_name, u.password_hash, u.dni,
                       u.phone, u.address_street, u.address_city, u.address_zip, r.role, u.active
                FROM User u
                JOIN Role r ON u.id_role = r.id_role
                WHERE u.active = TRUE
                """
            )
            rows = cursor.fetchall()
            
            result = {}
            for row in rows:
                username = row["username"]
                dni = row["dni"]
                
                sub_cursor = conn.cursor(buffered=True)
                
                sub_cursor.execute("SELECT id_sensor FROM User_Sensor WHERE dni = %s", (dni,))
                sensors = [s[0] for s in sub_cursor.fetchall()]

                sub_cursor.execute(
                    "SELECT u.username FROM User_Hierarchy h JOIN User u ON h.superior_dni = u.dni WHERE h.subordinate_dni = %s",
                    (dni,)
                )
                supervisors = [s[0] for s in sub_cursor.fetchall()]

                sub_cursor.execute(
                    "SELECT u.username FROM User_Hierarchy h JOIN User u ON h.subordinate_dni = u.dni WHERE h.superior_dni = %s",
                    (dni,)
                )
                subordinates = [s[0] for s in sub_cursor.fetchall()]
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
                "supervisors": supervisors,
                "subordinates": subordinates,
            }
            cursor.close()
            return result
        finally:
            conn.close()

    def add_user(self, username, password, role, full_name="", dni="", phone="", 
                 address_street="", address_city="", address_zip=""):
        """Inserts a user and hashes the password directly in MySQL."""
        conn = get_connection()
        try:
            cursor = conn.cursor(buffered=True)
            cursor.execute("SELECT id_role FROM Role WHERE role = %s", (role,))
            row = cursor.fetchone()
            if not row:
                raise ValueError(f"Role '{role}' does not exist.")
            
            id_role = row[0]

            query = """
                INSERT INTO User
                    (dni, id_role, username, full_name, password_hash, phone, 
                     address_street, address_city, address_zip, active)
                VALUES (%s, %s, %s, %s, SHA2(%s, 256), %s, %s, %s, %s, TRUE)
            """
            cursor.execute(query, (dni, id_role, username, full_name, password, phone, 
                                 address_street, address_city, address_zip))
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
                cursor.execute("SELECT id_role FROM Role WHERE role = %s", (kwargs["role"],))
                row = cursor.fetchone()
                if row:
                    cursor.execute(
                        "UPDATE User SET id_role=%s WHERE username=%s",
                        (row[0], username),
                    )

            # Update Address components
            if "address_street" in kwargs:
                cursor.execute(
                    "UPDATE User SET address_street=%s WHERE username=%s",
                    (kwargs["address_street"], username),
                )
            if "address_city" in kwargs:
                cursor.execute(
                    "UPDATE User SET address_city=%s WHERE username=%s",
                    (kwargs["address_city"], username),
                )
            if "address_zip" in kwargs:
                cursor.execute(
                    "UPDATE User SET address_zip=%s WHERE username=%s",
                    (kwargs["address_zip"], username),
                )
            
            # Update Sensors
            if "assigned_sensors" in kwargs:
                cursor.execute("SELECT dni FROM User WHERE username=%s", (username,))
                res = cursor.fetchone()
                if res:
                    dni = res[0]
                    cursor.execute("DELETE FROM User_Sensor WHERE dni=%s", (dni,))
                    
                    from ArtemusPark.bbdd.db_connection import get_sensor_id
                    from ArtemusPark.config.Sensor_Config import SENSOR_CONFIG
                    
                    for s_id_name in kwargs["assigned_sensors"]:
                        # Buscamos el tipo de sensor en SENSOR_CONFIG para obtener el ID real de la BD
                        s_type = "Temperature" # Default
                        for t, sensors in SENSOR_CONFIG.items():
                            if any(s["id"] == s_id_name for s in sensors):
                                s_type = t.capitalize()
                                break
                        
                        db_id = get_sensor_id(s_id_name, s_type)
                        if db_id:
                            cursor.execute(
                                "INSERT INTO User_Sensor (dni, id_sensor) VALUES (%s, %s)",
                                (dni, db_id),
                            )

            # --- NUEVA LÓGICA: Update Hierarchy (Supervisors) ---
            if "supervisors" in kwargs:
                cursor.execute("SELECT dni FROM User WHERE username=%s", (username,))
                res = cursor.fetchone()
                if res:
                    sub_dni = res[0]
                    # Borramos sus supervisores actuales (él es el subordinado)
                    cursor.execute("DELETE FROM User_Hierarchy WHERE subordinate_dni=%s", (sub_dni,))
                    for sup_username in kwargs["supervisors"]:
                        cursor.execute("SELECT dni FROM User WHERE username=%s", (sup_username,))
                        sup_res = cursor.fetchone()
                        if sup_res:
                            cursor.execute(
                                "INSERT INTO User_Hierarchy (superior_dni, subordinate_dni) VALUES (%s, %s)",
                                (sup_res[0], sub_dni),
                            )

            # --- NUEVA LÓGICA: Update Hierarchy (Subordinates) ---
            if "subordinates" in kwargs:
                cursor.execute("SELECT dni FROM User WHERE username=%s", (username,))
                res = cursor.fetchone()
                if res:
                    sup_dni = res[0]
                    # Borramos sus subordinados actuales (él es el superior)
                    cursor.execute("DELETE FROM User_Hierarchy WHERE superior_dni=%s", (sup_dni,))
                    for sub_username in kwargs["subordinates"]:
                        cursor.execute("SELECT dni FROM User WHERE username=%s", (sub_username,))
                        sub_res = cursor.fetchone()
                        if sub_res:
                            cursor.execute(
                                "INSERT INTO User_Hierarchy (superior_dni, subordinate_dni) VALUES (%s, %s)",
                                (sup_dni, sub_res[0]),
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
            cursor.execute("SELECT profile_picture FROM User WHERE username = %s", (username,))
            row = cursor.fetchone()
            return row[0] if row else None
        finally:
            conn.close()

    def delete_user(self, username):
        """Logical deletion in 'User' table."""
        conn = get_connection()
        try:
            cursor = conn.cursor(buffered=True)
            cursor.execute("UPDATE User SET active = FALSE WHERE username=%s", (username,))
            conn.commit()
            cursor.close()
        finally:
            conn.close()
