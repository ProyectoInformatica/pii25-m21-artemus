from functools import wraps
from typing import Any, Callable, List, Tuple
import logging

from ArtemusPark.database.Database_Connection_Manager import DatabaseConnectionManager

logger = logging.getLogger(__name__)


class DatabaseException(Exception):
    """Excepción personalizada para errores de base de datos."""

    pass


def handle_db_error(default_return: Any = None) -> Callable:
    """Decorador para manejar errores de BD de forma consistente.

    Args:
        default_return: Valor a retornar si ocurre un error

    Example:
        @handle_db_error(default_return=None)
        def get_user(username: str):
            # método aquí
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except DatabaseException as e:
                logger.error(f"Error BD en {func.__name__}: {e}")
                return default_return
            except Exception as e:
                logger.error(f"Error inesperado en {func.__name__}: {e}")
                return default_return

        return wrapper

    return decorator


def ensure_connection(func: Callable) -> Callable:
    """Decorador que asegura que hay conexión antes de ejecutar.

    Intenta reconectar si es necesario.

    Example:
        @ensure_connection
        def query_database():
            # método aquí
    """

    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        manager = DatabaseConnectionManager()
        if not manager.get_connection():
            raise DatabaseException("No se pudo establecer conexión a la base de datos")
        return func(*args, **kwargs)

    return wrapper


class QueryBuilder:
    """Constructor fluido para queries SQL de forma segura.

    Proporciona métodos para construir queries de forma legible y segura.

    Example:
        query, params = (
            QueryBuilder()
            .select("id", "username", "role")
            .from_table("users")
            .where("role", "=", "admin")
            .build()
        )
    """

    def __init__(self) -> None:
        """Inicializa el constructor de queries."""
        self.select_fields: List[str] = []
        self.from_table_name: str = ""
        self.where_conditions: List[Tuple[str, str, Any]] = []
        self.join_conditions: List[str] = []
        self.order_by_fields: List[Tuple[str, str]] = []
        self.limit_value: int = 0
        self.params: List[Any] = []

    def select(self, *fields: str) -> "QueryBuilder":
        """Define los campos a seleccionar.

        Args:
            *fields: Nombres de campos

        Returns:
            QueryBuilder: Self para method chaining
        """
        self.select_fields = list(fields) if fields else ["*"]
        return self

    def from_table(self, table_name: str) -> "QueryBuilder":
        """Define la tabla principal.

        Args:
            table_name: Nombre de la tabla

        Returns:
            QueryBuilder: Self para method chaining
        """
        self.from_table_name = table_name
        return self

    def where(self, column: str, operator: str, value: Any) -> "QueryBuilder":
        """Agrega una condición WHERE.

        Args:
            column: Nombre de la columna
            operator: Operador SQL (=, !=, <, >, <=, >=, LIKE, IN)
            value: Valor a comparar

        Returns:
            QueryBuilder: Self para method chaining
        """
        self.where_conditions.append((column, operator, value))
        self.params.append(value)
        return self

    def order_by(self, field: str, direction: str = "ASC") -> "QueryBuilder":
        """Agrega ordenamiento.

        Args:
            field: Campo para ordenar
            direction: ASC o DESC (por defecto ASC)

        Returns:
            QueryBuilder: Self para method chaining
        """
        self.order_by_fields.append((field, direction))
        return self

    def limit(self, limit_count: int) -> "QueryBuilder":
        """Agrega LIMIT.

        Args:
            limit_count: Número máximo de resultados

        Returns:
            QueryBuilder: Self para method chaining
        """
        self.limit_value = limit_count
        return self

    def join(self, join_table: str, on_condition: str) -> "QueryBuilder":
        """Agrega un JOIN.

        Args:
            join_table: Tabla a unir
            on_condition: Condición ON

        Returns:
            QueryBuilder: Self para method chaining
        """
        self.join_conditions.append(f"JOIN {join_table} ON {on_condition}")
        return self

    def build(self) -> Tuple[str, Tuple[Any, ...]]:
        """Construye la query SQL final.

        Returns:
            Tuple[str, Tuple]: (Query SQL, Parámetros)

        Raises:
            ValueError: Si falta información crítica
        """
        if not self.select_fields or not self.from_table_name:
            raise ValueError("SELECT y FROM son obligatorios para construir una query")

        query_parts = [
            f"SELECT {', '.join(self.select_fields)}",
            f"FROM {self.from_table_name}",
        ]

        if self.join_conditions:
            query_parts.extend(self.join_conditions)

        if self.where_conditions:
            where_parts = []
            for column, operator, _ in self.where_conditions:
                where_parts.append(f"{column} {operator} %s")
            query_parts.append(f"WHERE {' AND '.join(where_parts)}")

        if self.order_by_fields:
            order_parts = [
                f"{field} {direction}" for field, direction in self.order_by_fields
            ]
            query_parts.append(f"ORDER BY {', '.join(order_parts)}")

        if self.limit_value > 0:
            query_parts.append(f"LIMIT {self.limit_value}")

        query = " ".join(query_parts)
        return query, tuple(self.params)


def build_insert_query(table_name: str, data: dict) -> Tuple[str, Tuple[Any, ...]]:
    """Construye una query INSERT de forma segura.

    Args:
        table_name: Nombre de la tabla
        data: Diccionario con {columna: valor}

    Returns:
        Tuple[str, Tuple]: (Query SQL, Parámetros)

    Example:
        query, params = build_insert_query(
            "users",
            {"username": "john", "password": "secret", "role": "user"}
        )
    """
    if not data:
        raise ValueError("Data no puede estar vacía para INSERT")

    columns = list(data.keys())
    values = list(data.values())
    placeholders = ", ".join(["%s"] * len(columns))

    query = (
        f"INSERT INTO {table_name} ({', '.join(columns)}) " f"VALUES ({placeholders})"
    )

    return query, tuple(values)


def build_update_query(
    table_name: str, data: dict, where_conditions: dict
) -> Tuple[str, Tuple[Any, ...]]:
    """Construye una query UPDATE de forma segura.

    Args:
        table_name: Nombre de la tabla
        data: Diccionario con {columna: nuevo_valor}
        where_conditions: Diccionario con {columna: valor}

    Returns:
        Tuple[str, Tuple]: (Query SQL, Parámetros)

    Example:
        query, params = build_update_query(
            "users",
            {"role": "admin"},
            {"id": 5}
        )
    """
    if not data or not where_conditions:
        raise ValueError("Data y where_conditions no pueden estar vacías para UPDATE")

    set_parts = [f"{col} = %s" for col in data.keys()]
    where_parts = [f"{col} = %s" for col in where_conditions.keys()]

    values = list(data.values()) + list(where_conditions.values())

    query = (
        f"UPDATE {table_name} SET {', '.join(set_parts)} "
        f"WHERE {' AND '.join(where_parts)}"
    )

    return query, tuple(values)


def build_delete_query(
    table_name: str, where_conditions: dict
) -> Tuple[str, Tuple[Any, ...]]:
    """Construye una query DELETE de forma segura.

    Args:
        table_name: Nombre de la tabla
        where_conditions: Diccionario con {columna: valor}

    Returns:
        Tuple[str, Tuple]: (Query SQL, Parámetros)

    Example:
        query, params = build_delete_query(
            "users",
            {"id": 5}
        )
    """
    if not where_conditions:
        raise ValueError("where_conditions no puede estar vacía para DELETE")

    where_parts = [f"{col} = %s" for col in where_conditions.keys()]
    values = list(where_conditions.values())

    query = f"DELETE FROM {table_name} WHERE {' AND '.join(where_parts)}"

    return query, tuple(values)
