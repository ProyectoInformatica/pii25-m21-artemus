import pymysql
from typing import Any, Dict, List, Optional, Tuple
from contextlib import contextmanager
import logging

from ArtemusPark.config.Database_Config import DatabaseConfig

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class DatabaseConnectionManager:
    """Gestor de conexiones a MySQL con patrón Singleton.

    Proporciona una interfaz centralizada para interactuar con la base de datos,
    incluyendo manejo de reconexión automática, context managers y logging.
    """

    _instance: Optional["DatabaseConnectionManager"] = None
    _connection: Optional[pymysql.Connection] = None

    def __new__(cls) -> "DatabaseConnectionManager":
        """Implementa patrón Singleton para asegurar única instancia."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self) -> None:
        """Inicializa la instancia del singleton."""
        self._connection = None
        logger.info("DatabaseConnectionManager inicializado")

    def connect(self) -> bool:
        """Establece conexión a la base de datos.

        Returns:
            bool: True si la conexión es exitosa, False en caso contrario.
        """
        try:
            if self._connection is not None and self._check_connection():
                logger.info("Conexión existente está activa")
                return True

            self._connection = pymysql.connect(
                host=DatabaseConfig.DB_HOST,
                port=DatabaseConfig.DB_PORT,
                user=DatabaseConfig.DB_USER,
                password=DatabaseConfig.DB_PASSWORD,
                database=DatabaseConfig.DB_NAME,
                charset="utf8mb4",
                cursorclass=pymysql.cursors.DictCursor,
            )
            logger.info(
                f"Conexión establecida a {DatabaseConfig.DB_HOST}:" f"{DatabaseConfig.DB_PORT}/{DatabaseConfig.DB_NAME}"
            )
            return True

        except pymysql.MySQLError as e:
            logger.error(f"Error de conexión MySQL: {e}")
            self._connection = None
            return False

        except Exception as e:
            logger.error(f"Error inesperado al conectar: {e}")
            self._connection = None
            return False

    def _check_connection(self) -> bool:
        """Verifica si la conexión está activa.

        Returns:
            bool: True si la conexión está activa, False si no.
        """
        try:
            if self._connection is None:
                return False

            self._connection.ping()
            return True

        except Exception as e:
            logger.warning(f"Conexión inactiva: {e}")
            self._connection = None
            return False

    def reconnect(self) -> bool:
        """Cierra la conexión actual y establece una nueva.

        Returns:
            bool: True si reconexión es exitosa, False en caso contrario.
        """
        logger.info("Intentando reconectar...")
        self.disconnect()
        return self.connect()

    def disconnect(self) -> None:
        """Cierra la conexión a la base de datos."""
        try:
            if self._connection is not None:
                self._connection.close()
                logger.info("Conexión cerrada")
        except Exception as e:
            logger.error(f"Error al cerrar conexión: {e}")
        finally:
            self._connection = None

    def get_connection(self) -> Optional[pymysql.Connection]:
        """Obtiene la conexión activa.

        Si la conexión no está activa, intenta reconectar.

        Returns:
            Optional[pymysql.Connection]: Conexión activa o None si no se pudo conectar.
        """
        if not self._check_connection():
            logger.warning("Conexión perdida, reintentando...")
            if not self.reconnect():
                logger.error("No se pudo restablecer la conexión")
                return None

        return self._connection

    @contextmanager
    def get_cursor(self, commit: bool = True):
        """Context manager para obtener un cursor seguro.

        Args:
            commit: Si True, hace commit automático al salir.

        Yields:
            pymysql.cursors.DictCursor: Cursor para ejecutar queries.

        Example:
            with manager.get_cursor() as cursor:
                cursor.execute("SELECT * FROM users")
                results = cursor.fetchall()
        """
        connection = self.get_connection()
        if connection is None:
            logger.error("No hay conexión disponible")
            raise RuntimeError("No se pudo obtener conexión a la base de datos")

        cursor = connection.cursor()
        try:
            yield cursor
            if commit:
                connection.commit()
                logger.debug("Cambios confirmados (commit)")
        except Exception as e:
            connection.rollback()
            logger.error(f"Error en transacción, rollback ejecutado: {e}")
            raise
        finally:
            cursor.close()

    def execute_query(self, query: str, params: Tuple = ()) -> List[Dict[str, Any]]:
        """Ejecuta una query SELECT y retorna los resultados.

        Args:
            query: Consulta SQL con placeholders %s
            params: Tupla de parámetros para la query

        Returns:
            List[Dict[str, Any]]: Lista de diccionarios con los resultados

        Example:
            results = manager.execute_query(
                "SELECT * FROM users WHERE role = %s",
                ("admin",)
            )
        """
        try:
            with self.get_cursor(commit=False) as cursor:
                cursor.execute(query, params)
                results = cursor.fetchall()
                logger.debug(f"Query ejecutada: {query[:100]}... Resultados: {len(results)}")
                return results
        except Exception as e:
            logger.error(f"Error en execute_query: {e}")
            raise

    def execute_insert(self, query: str, params: Tuple = ()) -> Tuple[bool, Optional[int]]:
        """Ejecuta un INSERT y retorna el ID generado.

        Args:
            query: Consulta INSERT SQL
            params: Tupla de parámetros

        Returns:
            Tuple[bool, Optional[int]]: (Éxito, ID insertado)

        Example:
            success, user_id = manager.execute_insert(
                "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
                ("john_doe", "secret123", "user")
            )
        """
        try:
            with self.get_cursor(commit=True) as cursor:
                cursor.execute(query, params)
                inserted_id = cursor.lastrowid
                logger.info(f"INSERT exitoso. ID: {inserted_id}")
                return True, inserted_id
        except Exception as e:
            logger.error(f"Error en execute_insert: {e}")
            return False, None

    def execute_update(self, query: str, params: Tuple = ()) -> Tuple[bool, int]:
        """Ejecuta un UPDATE y retorna filas afectadas.

        Args:
            query: Consulta UPDATE SQL
            params: Tupla de parámetros

        Returns:
            Tuple[bool, int]: (Éxito, Número de filas afectadas)

        Example:
            success, rows = manager.execute_update(
                "UPDATE users SET role = %s WHERE id = %s",
                ("admin", 5)
            )
        """
        try:
            with self.get_cursor(commit=True) as cursor:
                cursor.execute(query, params)
                affected_rows = cursor.rowcount
                logger.info(f"UPDATE exitoso. Filas afectadas: {affected_rows}")
                return True, affected_rows
        except Exception as e:
            logger.error(f"Error en execute_update: {e}")
            return False, 0

    def execute_delete(self, query: str, params: Tuple = ()) -> Tuple[bool, int]:
        """Ejecuta un DELETE y retorna filas afectadas.

        Args:
            query: Consulta DELETE SQL
            params: Tupla de parámetros

        Returns:
            Tuple[bool, int]: (Éxito, Número de filas eliminadas)

        Example:
            success, rows = manager.execute_delete(
                "DELETE FROM users WHERE id = %s",
                (5,)
            )
        """
        try:
            with self.get_cursor(commit=True) as cursor:
                cursor.execute(query, params)
                deleted_rows = cursor.rowcount
                logger.info(f"DELETE exitoso. Filas eliminadas: {deleted_rows}")
                return True, deleted_rows
        except Exception as e:
            logger.error(f"Error en execute_delete: {e}")
            return False, 0

    def execute_many(self, query: str, data: List[Tuple]) -> Tuple[bool, int]:
        """Ejecuta múltiples operaciones INSERT/UPDATE en batch.

        Args:
            query: Consulta SQL con placeholders
            data: Lista de tuplas con parámetros

        Returns:
            Tuple[bool, int]: (Éxito, Número de filas afectadas)

        Example:
            success, rows = manager.execute_many(
                "INSERT INTO temp_readings (sensor_id, value) VALUES (%s, %s)",
                [("sensor_01", 25.5), ("sensor_02", 26.1)]
            )
        """
        try:
            with self.get_cursor(commit=True) as cursor:
                cursor.executemany(query, data)
                affected_rows = cursor.rowcount
                logger.info(f"executemany exitoso. Filas afectadas: {affected_rows}")
                return True, affected_rows
        except Exception as e:
            logger.error(f"Error en execute_many: {e}")
            return False, 0

    def test_connection(self) -> bool:
        """Prueba la conexión ejecutando una query simple.

        Returns:
            bool: True si la conexión funciona, False en caso contrario.
        """
        try:
            results = self.execute_query("SELECT 1 as test")
            logger.info("Test de conexión exitoso")
            return len(results) > 0
        except Exception as e:
            logger.error(f"Test de conexión fallido: {e}")
            return False
