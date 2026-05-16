import json
import mysql.connector
from ArtemusPark.database.db_connection import get_connection, get_sensor_id
from ArtemusPark.service.Crypto_Service import CryptoService


class AuthRepository:
    """Repository to handle user authentication using individual permissions stored in User table."""

    def get_user_permissions(self, username):
        """Returns a list of permission descriptions for the user based on their role."""
        conn = get_connection()
        try:
            cursor = conn.cursor(buffered=True)
            # Primero obtenemos el rol del usuario para los permisos por defecto
            cursor.execute(
                "SELECT r.role FROM User u JOIN Role r ON u.id_role = r.id_role WHERE u.username = %s",
                (username,),
            )
            role_row = cursor.fetchone()
            user_role = role_row[0] if role_row else "user"

            # Intentamos obtener permisos de la tabla asociativa
            query = """
                SELECT p.description 
                FROM Permission p
                JOIN Role_Permission rp ON p.id_permission = rp.id_permission
                JOIN User u ON u.id_role = rp.id_role
                WHERE u.username = %s AND u.active = TRUE
            """
            cursor.execute(query, (username,))
            perms = [row[0] for row in cursor.fetchall()]
            cursor.close()

            # SI NO HAY PERMISOS EN LA BD, ASIGNAMOS LOS BÁSICOS POR CÓDIGO (Fallback)
            if not perms:
                if user_role == "admin":
                    return [
                        "MANAGE_USERS",
                        "VIEW_SECURITY_LOGS",
                        "EXPORT_DATA_REPORTS",
                        "MANAGE_SENSORS",
                        "VIEW_DASHBOARD",
                        "CHAT_ACCESS",
                    ]
                elif user_role == "maintenance":
                    return ["VIEW_DASHBOARD", "VIEW_MAINTENANCE", "CHAT_ACCESS"]
                else:
                    return ["VIEW_DASHBOARD", "CHAT_ACCESS"]

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
        """Returns all users including role and supervisor information."""
        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True, buffered=True)
            cursor.execute("""
                SELECT u.username, u.full_name, u.password_hash, u.dni,
                       u.phone, u.address_street, u.address_city, u.address_zip, 
                       r.role, u.active, h.superior_dni, u.public_key
                FROM User u
                JOIN Role r ON u.id_role = r.id_role
                LEFT JOIN User_Hierarchy h ON u.dni = h.subordinate_dni
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

                # Get permissions based on role
                perm_cursor = conn.cursor(buffered=True)
                perm_cursor.execute(
                    """
                    SELECT p.description FROM Permission p
                    JOIN Role_Permission rp ON p.id_permission = rp.id_permission
                    JOIN Role r ON r.id_role = rp.id_role
                    WHERE r.role = %s
                """,
                    (row["role"],),
                )
                role_permissions = [p[0] for p in perm_cursor.fetchall()]
                perm_cursor.close()

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
                    "permissions": role_permissions,
                    "superior_dni": row["superior_dni"],
                    "public_key": row["public_key"],
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
                SELECT u.*, r.role, h.superior_dni
                FROM User u 
                JOIN Role r ON u.id_role = r.id_role
                LEFT JOIN User_Hierarchy h ON u.dni = h.subordinate_dni
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

            # Get permissions based on role
            perm_cursor = conn.cursor(buffered=True)
            perm_cursor.execute(
                """
                SELECT p.description FROM Permission p
                JOIN Role_Permission rp ON p.id_permission = rp.id_permission
                JOIN Role r ON r.id_role = rp.id_role
                WHERE r.role = %s
            """,
                (row["role"],),
            )
            role_permissions = [p[0] for p in perm_cursor.fetchall()]
            perm_cursor.close()

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
                "permissions": role_permissions,
                "superior_dni": row["superior_dni"],
                "public_key": row.get("public_key"),
                "private_key_encrypted": row.get("private_key"),
            }
            cursor.close()
            return result
        finally:
            conn.close()

    def ensure_keys_exist(self, username, password):
        """Generates RSA keys for a user if they don't have them yet."""
        user = self.get_user_by_username(username)
        if user and not user.get("public_key"):
            priv, pub = CryptoService.generate_rsa_keys()
            pub_pem = CryptoService.export_public_key(pub)
            priv_enc = CryptoService.export_private_key_encrypted(priv, password)

            conn = get_connection()
            try:
                cursor = conn.cursor(buffered=True)
                cursor.execute(
                    "UPDATE User SET public_key = %s, private_key = %s WHERE username = %s",
                    (pub_pem, priv_enc, username),
                )
                conn.commit()
                return pub_pem, priv_enc
            finally:
                conn.close()
        return user.get("public_key"), user.get("private_key_encrypted")

    def add_user(self, username, password, role, permissions=None, **kwargs):
        """Inserts a user with role and optional supervisor."""
        conn = get_connection()
        try:
            cursor = conn.cursor(buffered=True)
            cursor.execute("SELECT id_role FROM Role WHERE role = %s", (role,))
            role_row = cursor.fetchone()
            id_role = role_row[0] if role_row else 3  # Default to user

            dni = kwargs.get("dni")

            # --- RSA KEY GENERATION ---
            priv, pub = CryptoService.generate_rsa_keys()
            pub_pem = CryptoService.export_public_key(pub)
            priv_enc = CryptoService.export_private_key_encrypted(priv, password)

            query = """
                INSERT INTO User
                    (dni, id_role, username, full_name, password_hash, phone, 
                     address_street, address_city, address_zip, public_key, private_key, active)
                VALUES (%s, %s, %s, %s, SHA2(%s, 256), %s, %s, %s, %s, %s, %s, TRUE)
            """
            cursor.execute(
                query,
                (
                    dni,
                    id_role,
                    username,
                    kwargs.get("full_name"),
                    password,
                    kwargs.get("phone"),
                    kwargs.get("address_street"),
                    kwargs.get("address_city"),
                    kwargs.get("address_zip"),
                    pub_pem,
                    priv_enc,
                ),
            )

            # Assign sensors if any
            assigned_sensors = kwargs.get("assigned_sensors", [])
            for sensor_id in assigned_sensors:
                cursor.execute(
                    "INSERT INTO User_Sensor (dni, id_sensor) VALUES (%s, %s)",
                    (dni, sensor_id),
                )

            # Hierarchy
            superior_dni = kwargs.get("superior_dni")
            if superior_dni:
                cursor.execute(
                    "INSERT INTO User_Hierarchy (superior_dni, subordinate_dni) VALUES (%s, %s)",
                    (superior_dni, dni),
                )

            # --- AUTO-ADD TO GLOBAL CHAT ---
            cursor.execute("SELECT id_chat FROM Chat WHERE name = 'Global'")
            global_chat_row = cursor.fetchone()
            if global_chat_row:
                global_chat_id = global_chat_row[0]
                cursor.execute(
                    "INSERT IGNORE INTO User_Chat (dni, id_chat) VALUES (%s, %s)",
                    (dni, global_chat_id),
                )

            conn.commit()
            cursor.close()
        finally:
            conn.close()

    def update_user(self, dni, permissions=None, **kwargs):
        """Updates user data including role and supervisor."""
        conn = get_connection()
        try:
            cursor = conn.cursor(buffered=True)


            if "password" in kwargs and kwargs["password"]:
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

            if "address_street" in kwargs:
                cursor.execute(
                    "UPDATE User SET address_street=%s WHERE dni=%s",
                    (kwargs["address_street"], dni),
                )

            if "address_city" in kwargs:
                cursor.execute(
                    "UPDATE User SET address_city=%s WHERE dni=%s",
                    (kwargs["address_city"], dni),
                )

            if "address_zip" in kwargs:
                cursor.execute(
                    "UPDATE User SET address_zip=%s WHERE dni=%s",
                    (kwargs["address_zip"], dni),
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

            if "assigned_sensors" in kwargs:
                # Clear and re-assign
                cursor.execute("DELETE FROM User_Sensor WHERE dni = %s", (dni,))
                for sensor_id in kwargs["assigned_sensors"]:
                    cursor.execute(
                        "INSERT INTO User_Sensor (dni, id_sensor) VALUES (%s, %s)",
                        (dni, sensor_id),
                    )

            if "superior_dni" in kwargs:
                cursor.execute(
                    "DELETE FROM User_Hierarchy WHERE subordinate_dni = %s", (dni,)
                )
                if kwargs["superior_dni"]:
                    cursor.execute(
                        "INSERT INTO User_Hierarchy (superior_dni, subordinate_dni) VALUES (%s, %s)",
                        (kwargs["superior_dni"], dni),
                    )

            if "profile_picture" in kwargs:
                cursor.execute(
                    "UPDATE User SET profile_picture=%s WHERE dni=%s",
                    (kwargs["profile_picture"], dni),
                )

            conn.commit()
            cursor.close()
        except Exception:
            try:
                conn.rollback()
            except Exception:
                pass
            raise
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
        """Physical deletion: Cleans up all related tables before deleting the user."""
        conn = get_connection()
        try:
            cursor = conn.cursor(buffered=True)

            # 1. Limpiar jerarquía (donde sea superior o subordinado)
            cursor.execute(
                "DELETE FROM User_Hierarchy WHERE superior_dni = %s OR subordinate_dni = %s",
                (dni, dni),
            )

            # 2. Limpiar sensores asignados
            cursor.execute("DELETE FROM User_Sensor WHERE dni = %s", (dni,))

            # 3. Limpiar participación en chats
            cursor.execute("DELETE FROM User_Chat WHERE dni = %s", (dni,))

            # 4. Limpiar mensajes (Columna correcta: sender_dni)
            cursor.execute("DELETE FROM Message WHERE sender_dni = %s", (dni,))

            # 5. Limpiar tickets de mantenimiento (Tabla correcta: Ticket, Columna: user_dni)
            cursor.execute("DELETE FROM Ticket WHERE user_dni = %s", (dni,))

            # 6. Limpiar registros de acceso a puertas
            # Intentamos con Door_Control y si falla (por el backup) intentamos con Door
            try:
                cursor.execute("DELETE FROM Door_Control WHERE user_dni = %s", (dni,))
            except mysql.connector.Error as e:
                if e.errno == 1146:  # Table doesn't exist
                    try:
                        # En algunas versiones la tabla se llama Door y usa username
                        cursor.execute(
                            "SELECT username FROM User WHERE dni = %s", (dni,)
                        )
                        user_row = cursor.fetchone()
                        if user_row:
                            cursor.execute(
                                "DELETE FROM Door WHERE username = %s", (user_row[0],)
                            )
                    except mysql.connector.Error:
                        pass  # Si tampoco existe Door, ignoramos

            # 7. Finalmente borrar el usuario
            cursor.execute("DELETE FROM User WHERE dni = %s", (dni,))

            conn.commit()
            cursor.close()
        except mysql.connector.Error as err:
            conn.rollback()
            raise err
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
