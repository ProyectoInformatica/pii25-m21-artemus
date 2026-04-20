import threading
import time
import mysql.connector
from mysql.connector.pooling import MySQLConnectionPool
from datetime import datetime
from typing import Dict, Optional

# =====================================================================
# SYSTEM CONFIGURATION
# =====================================================================
DB_CONFIG = {
    "host": "localhost",
    "database": "artemus",
    "user": "root",
    "password": "",
    "port": 3306,
}


# =====================================================================
# DATABASE MANAGER CLASS
# =====================================================================
class DatabaseManager:
    connection_pool = None
    type_cache = {}
    sensor_cache = {}

    @classmethod
    def initialize_pool(cls):
        """Initializes the MySQL connection pool."""
        if cls.connection_pool is None:
            try:
                cls.connection_pool = MySQLConnectionPool(
                    pool_name="artemus_pool",
                    pool_size=15,
                    pool_reset_session=True,
                    **DB_CONFIG,
                )
                cls.ensure_basic_data()
            except mysql.connector.Error as error:
                print(f"DATABASE ERROR: {error}")
                raise error

    @classmethod
    def ensure_basic_data(cls):
        """Ensures Roles, Zones, Types and Admin exist. Forces admin update to ensure login."""

        conn = cls.get_connection()
        try:
            # Use buffered=True to avoid 'Unread result found' errors
            cursor = conn.cursor(buffered=True)

            # 1. Roles
            cursor.executemany(
                "INSERT IGNORE INTO Role (id_role, role) VALUES (%s, %s)",
                [(1, "admin"), (2, "maintenance"), (3, "user")],
            )

            # 2. Zones
            cursor.execute(
                "INSERT IGNORE INTO Zone (id_zone, name) VALUES (1, 'Main Zone')"
            )

            # 3. Types
            types = [
                (1, "Temperature"),
                (2, "Humidity"),
                (3, "Wind"),
                (4, "Air_Quality"),
                (5, "Lighting"),
                (6, "Door"),
            ]
            cursor.executemany(
                "INSERT IGNORE INTO Type (id_type, description) VALUES (%s, %s)", types
            )

            # 3.1 Permissions
            permissions = [
                (1, "VIEW_DASHBOARD"),
                (2, "VIEW_HISTORY"),
                (3, "VIEW_REQUESTS"),
                (4, "MANAGE_REQUESTS"),
                (5, "VIEW_MAINTENANCE"),
                (6, "MANAGE_SENSORS"),
                (7, "ACCESS_ADMIN_PANEL"),
                (8, "MANAGE_USERS"),
                (9, "ACTIVATE_EMERGENCY"),
            ]
            cursor.executemany(
                "INSERT IGNORE INTO Permission (id_permission, description) VALUES (%s, %s)",
                permissions,
            )

            # 3.2 Role_Permission mapping
            role_perms = []
            # Admin (Role 1) gets all (1-9)
            for p_id in range(1, 10):
                role_perms.append((1, p_id))
            # Maintenance (Role 2) gets 1-6
            for p_id in range(1, 7):
                role_perms.append((2, p_id))
            # User (Role 3) gets only 1
            role_perms.append((3, 1))

            cursor.executemany(
                "INSERT IGNORE INTO Role_Permission (id_role, id_permission) VALUES (%s, %s)",
                role_perms,
            )

            # 4. Default Admin (admin123) - Using REPLACE to force password update
            # Hash of 'admin123': a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3
            admin_sql = """
                REPLACE INTO User 
                (dni, id_role, username, full_name, password_hash, active, address_street, address_city, address_zip) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(
                admin_sql,
                (
                    "12345678X",
                    1,
                    "admin_soto",
                    "Adrian Soto",
                    "a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3",
                    True,
                    "Central Ave 45",
                    "Madrid",
                    "28001",
                ),
            )

            conn.commit()
            cursor.close()
        finally:
            conn.close()

    @classmethod
    def get_connection(cls):
        if cls.connection_pool is None:
            cls.initialize_pool()
        return cls.connection_pool.get_connection()

    @classmethod
    def get_type_id(cls, type_name: str) -> int:
        if type_name in cls.type_cache:
            return cls.type_cache[type_name]
        conn = cls.get_connection()
        try:
            cursor = conn.cursor(buffered=True)
            cursor.execute(
                "SELECT id_type FROM Type WHERE description = %s", (type_name,)
            )
            res = cursor.fetchone()
            if res:
                cls.type_cache[type_name] = res[0]
                cursor.close()
                return res[0]
            cursor.close()
            return 1
        finally:
            conn.close()


# =====================================================================
# PUBLIC FUNCTIONS
# =====================================================================
def get_connection():
    return DatabaseManager.get_connection()


def get_tipo_id(name: str):
    return DatabaseManager.get_type_id(name)


def get_sensor_id(sensor_name: str, type_name: str) -> int:
    """Gets sensor ID from Sensor table."""
    if sensor_name in DatabaseManager.sensor_cache:
        return DatabaseManager.sensor_cache[sensor_name]

    conn = get_connection()
    try:
        cursor = conn.cursor(buffered=True)
        cursor.execute("SELECT id_sensor FROM Sensor WHERE name = %s", (sensor_name,))
        res = cursor.fetchone()

        if res:
            sensor_id = res[0]
        else:
            type_id = DatabaseManager.get_type_id(type_name)
            cursor.execute(
                "INSERT INTO Sensor (id_zone, id_type, id_role, name) VALUES (%s, %s, %s, %s)",
                (1, type_id, 1, sensor_name),
            )
            conn.commit()
            sensor_id = cursor.lastrowid

        DatabaseManager.sensor_cache[sensor_name] = sensor_id
        cursor.close()
        return sensor_id
    finally:
        conn.close()


def load_sensor_config():
    """Loads sensor configuration from the database to replace static SENSOR_CONFIG."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True, buffered=True)
        query = """
            SELECT s.name, s.id_sensor, t.description as type
            FROM Sensor s
            JOIN Type t ON s.id_type = t.id_type
            WHERE s.active = TRUE
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()

        config = {}
        for row in rows:
            s_type = row["type"].lower()
            if s_type not in config:
                config[s_type] = []
            config[s_type].append(
                {"id": row["name"], "db_id": row["id_sensor"], "name": row["name"]}
            )

        # Fallback if DB is empty but we need something to work with
        if not config:
            from ArtemusPark.config.Sensor_Config import SENSOR_CONFIG

            return SENSOR_CONFIG

        return config
    finally:
        conn.close()
