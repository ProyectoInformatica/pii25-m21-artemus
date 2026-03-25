import json
import mysql.connector
from ArtemusPark.bbdd.db_connection import get_connection


class AuthRepository:
    """Repositorio para gestionar la autenticación de usuarios con persistencia en MariaDB."""

    def authenticate(self, username, password):
        """Verifica las credenciales y devuelve el rol si son correctas."""
        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT r.rol FROM Usuario u
                JOIN Rol r ON u.id_rol = r.id_rol
                WHERE u.usuario = %s AND u.contrasena_hash = %s
                """,
                (username, password),
            )
            row = cursor.fetchone()
            cursor.close()
            return row["rol"] if row else None
        finally:
            conn.close()

    def get_all_users(self):
        """Retorna todos los usuarios en el mismo formato que antes."""
        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT u.usuario, u.nombre_usuario, u.contrasena_hash, u.dni,
                       u.telefono, u.direccion, u.sensores_asignados,
                       u.supervisores, u.subordinados, r.rol
                FROM Usuario u
                JOIN Rol r ON u.id_rol = r.id_rol
                """
            )
            rows = cursor.fetchall()
            cursor.close()
            result = {}
            for row in rows:
                result[row["usuario"]] = {
                    "password": row["contrasena_hash"],
                    "role": row["rol"],
                    "full_name": row["nombre_usuario"],
                    "dni": row["dni"],
                    "phone": row["telefono"] or "",
                    "address": row["direccion"] or "",
                    "assigned_sensors": json.loads(row["sensores_asignados"] or "[]"),
                    "supervisors": json.loads(row["supervisores"] or "[]"),
                    "subordinates": json.loads(row["subordinados"] or "[]"),
                }
            return result
        finally:
            conn.close()

    def add_user(self, username, password, role, full_name="", dni="", phone="", address=""):
        """Agrega un nuevo usuario."""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id_rol FROM Rol WHERE rol = %s", (role,))
            row = cursor.fetchone()
            if not row:
                raise ValueError(f"Rol '{role}' no existe.")
            cursor.execute(
                """
                INSERT INTO Usuario
                    (dni, id_rol, usuario, nombre_usuario, contrasena_hash, telefono, direccion)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (dni, row[0], username, full_name, password, phone, address),
            )
            conn.commit()
            cursor.close()
        except mysql.connector.Error:
            conn.rollback()
            raise
        finally:
            conn.close()

    def update_user(
        self,
        username,
        password=None,
        role=None,
        assigned_sensors=None,
        full_name=None,
        dni=None,
        phone=None,
        address=None,
        supervisors=None,
        subordinates=None,
    ):
        """Actualiza datos de un usuario existente."""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            if password:
                cursor.execute(
                    "UPDATE Usuario SET contrasena_hash=%s WHERE usuario=%s",
                    (password, username),
                )
            if role:
                cursor.execute("SELECT id_rol FROM Rol WHERE rol=%s", (role,))
                row = cursor.fetchone()
                if row:
                    cursor.execute(
                        "UPDATE Usuario SET id_rol=%s WHERE usuario=%s",
                        (row[0], username),
                    )
            if full_name is not None:
                cursor.execute(
                    "UPDATE Usuario SET nombre_usuario=%s WHERE usuario=%s",
                    (full_name, username),
                )
            if dni is not None:
                cursor.execute(
                    "UPDATE Usuario SET dni=%s WHERE usuario=%s", (dni, username)
                )
            if phone is not None:
                cursor.execute(
                    "UPDATE Usuario SET telefono=%s WHERE usuario=%s", (phone, username)
                )
            if address is not None:
                cursor.execute(
                    "UPDATE Usuario SET direccion=%s WHERE usuario=%s",
                    (address, username),
                )
            if assigned_sensors is not None:
                cursor.execute(
                    "UPDATE Usuario SET sensores_asignados=%s WHERE usuario=%s",
                    (json.dumps(assigned_sensors), username),
                )
            if supervisors is not None:
                cursor.execute(
                    "UPDATE Usuario SET supervisores=%s WHERE usuario=%s",
                    (json.dumps(supervisors), username),
                )
            if subordinates is not None:
                cursor.execute(
                    "UPDATE Usuario SET subordinados=%s WHERE usuario=%s",
                    (json.dumps(subordinates), username),
                )
            conn.commit()
            cursor.close()
        except mysql.connector.Error:
            conn.rollback()
            raise
        finally:
            conn.close()

    def delete_user(self, username):
        """Elimina un usuario."""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Usuario WHERE usuario=%s", (username,))
            conn.commit()
            cursor.close()
        finally:
            conn.close()
