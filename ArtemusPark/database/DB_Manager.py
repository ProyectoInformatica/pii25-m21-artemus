import mysql.connector
from mysql.connector import Error, pooling
from contextlib import contextmanager
from ArtemusPark.database.DB_Config import DB_CONFIG, ADMIN_DB_CONFIG


class DatabaseManager:
    """Gestor de conexiones y operaciones con MariaDB/MySQL."""
    
    _instance = None
    _pool = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._connect()
    
    def _connect(self):
        """Establece la conexión pool con la base de datos."""
        try:
            self._pool = pooling.MySQLConnectionPool(
                pool_name="artemus_pool",
                pool_size=5,
                pool_reset_session=True,
                **DB_CONFIG
            )
        except Error as e:
            print(f"Error creating connection pool: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """Context manager para obtener una conexión del pool."""
        conn = None
        cursor = None
        try:
            conn = self._pool.get_connection()
            cursor = conn.cursor(dictionary=True)
            yield cursor
            conn.commit()
        except Error as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    @contextmanager
    def get_admin_connection(self):
        """Context manager para conexión administrativa (sin base de datos específica)."""
        conn = None
        cursor = None
        try:
            conn = mysql.connector.connect(**ADMIN_DB_CONFIG)
            cursor = conn.cursor(dictionary=True)
            yield cursor
            conn.commit()
        except Error as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    def execute_query(self, query, params=None):
        """Ejecuta una consulta SELECT y retorna los resultados."""
        with self.get_connection() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()
    
    def execute_update(self, query, params=None):
        """Ejecuta una consulta INSERT, UPDATE o DELETE."""
        with self.get_connection() as cursor:
            cursor.execute(query, params)
            return cursor.rowcount
    
    def execute_insert(self, query, params=None):
        """Ejecuta un INSERT y retorna el ID generado."""
        with self.get_connection() as cursor:
            cursor.execute(query, params)
            return cursor.lastrowid
    
    def execute_many(self, query, params_list):
        """Ejecuta una consulta con múltiples conjuntos de parámetros."""
        with self.get_connection() as cursor:
            cursor.executemany(query, params_list)
            return cursor.rowcount


# Singleton instance
db_manager = DatabaseManager()
