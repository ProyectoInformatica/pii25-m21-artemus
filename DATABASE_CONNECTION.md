# Conexión PyMySQL - Documentación

## Descripción

Este documento describe la implementación de la conexión a la base de datos MySQL con PyMySQL en el proyecto Artemus Park, siguiendo la arquitectura MVC del proyecto.

## Estructura de Archivos

```
ArtemusPark/database/
├── __init__.py                          # Exports públicas del módulo
├── Database_Connection_Manager.py       # Gestor singleton de conexiones
└── Database_Utils.py                    # Utilidades y helpers para queries
```

## Componentes Principales

### 1. Database_Connection_Manager.py

**Patrón:** Singleton  
**Responsabilidad:** Gestionar la única conexión a la base de datos

#### Características:

- **Singleton Pattern:** Garantiza una única instancia de conexión
- **Auto-reconexión:** Si la conexión se pierde, intenta reconectar automáticamente
- **Context Manager:** Proporciona `get_cursor()` para queries seguras
- **Logging detallado:** Registra todas las operaciones para debugging
- **Type Hints:** Tipos específicos para mejor IDE support

#### Métodos Principales:

```python
# Gestión de conexión
connect()               # Establece conexión
disconnect()            # Cierra conexión
reconnect()             # Reconecta
get_connection()        # Obtiene conexión activa

# Operaciones de BD
execute_query()         # SELECT (retorna resultados)
execute_insert()        # INSERT (retorna ID generado)
execute_update()        # UPDATE (retorna filas afectadas)
execute_delete()        # DELETE (retorna filas eliminadas)
execute_many()          # INSERT/UPDATE batch
test_connection()       # Prueba la conexión

# Context Manager
get_cursor()            # Context manager para queries seguras
```

#### Ejemplo de Uso:

```python
from ArtemusPark.database import DatabaseConnectionManager

manager = DatabaseConnectionManager()

# Query simple
results = manager.execute_query(
    "SELECT * FROM users WHERE role = %s",
    ("admin",)
)

# INSERT con ID generado
success, user_id = manager.execute_insert(
    "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
    ("john_doe", "secret123", "user")
)

# Context Manager (más seguro)
with manager.get_cursor() as cursor:
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()

# Probar conexión
if manager.test_connection():
    print("Conexión OK")
```

### 2. Database_Utils.py

**Responsabilidad:** Utilidades, decoradores y helpers para queries

#### Componentes:

**Excepciones:**
```python
DatabaseException  # Excepción personalizada para errores de BD
```

**Decoradores:**
```python
@handle_db_error(default_return=None)    # Maneja errores de forma consistente
@ensure_connection()                     # Asegura que hay conexión antes de ejecutar
```

**Query Builder:**
```python
QueryBuilder()
    .select("id", "username", "role")
    .from_table("users")
    .where("role", "=", "admin")
    .order_by("username", "ASC")
    .limit(10)
    .build()
# Retorna: (query_sql, parámetros)
```

**Funciones Helper:**
```python
build_insert_query(table, data)              # Construye INSERT
build_update_query(table, data, where)       # Construye UPDATE
build_delete_query(table, where)             # Construye DELETE
```

#### Ejemplo de Uso:

```python
from ArtemusPark.database import QueryBuilder, build_insert_query

# Con QueryBuilder
query, params = (
    QueryBuilder()
    .select("id", "username", "full_name")
    .from_table("users")
    .where("role", "=", "admin")
    .build()
)
results = manager.execute_query(query, params)

# Con helpers
data = {
    "username": "john_doe",
    "password": "secret",
    "role": "user",
    "full_name": "John Doe"
}
query, params = build_insert_query("users", data)
success, user_id = manager.execute_insert(query, params)
```

## Refactorización de Repositorios

Los repositorios han sido refactorizados para incluir métodos de BD en paralelo con métodos JSON:

### Auth_Repository.py

**Métodos JSON (existentes):**
```python
authenticate(username, password)      # JSON
get_all_users()                        # JSON
add_user(...)                          # JSON
update_user(...)                       # JSON
delete_user(username)                  # JSON
```

**Nuevos Métodos BD (prefijo `db_`):**
```python
db_authenticate(username, password)    # BD
db_get_all_users()                     # BD
db_get_user_by_username(username)      # BD
db_add_user(...)                       # BD
db_update_user(...)                    # BD
db_delete_user(username)               # BD
db_test_connection()                   # Prueba BD
```

### Temperature_Repository.py

**Métodos JSON (existentes):**
```python
save_temperature_measurement(measurement)      # JSON
load_all_temperature_measurements()            # JSON
```

**Nuevos Métodos BD (prefijo `db_`):**
```python
db_save_temperature_measurement(measurement)      # BD
db_load_all_temperature_measurements()            # BD
db_get_measurements_by_sensor(sensor_id)          # BD
db_get_measurements_by_date(date)                 # BD
db_get_measurements_by_sensor_and_date(...)       # BD
db_get_latest_measurement(sensor_id)              # BD
```

**Nota:** Los métodos JSON se mantienen para compatibilidad. Puedes usar ambos en paralelo durante la migración.

## Setup de Base de Datos

### Paso 1: Crear la BD

Ejecutar el script `schema.sql` en la raíz del proyecto:

```bash
mysql -u root -p < schema.sql
```

O desde MySQL CLI:
```sql
source schema.sql;
```

### Paso 2: Verificar Configuración

El archivo `ArtemusPark/config/Database_Config.py` debe tener:

```python
class DatabaseConfig:
    DB_NAME = "artemus_db"
    DB_USER = "root"
    DB_PASSWORD = ""  # Agregar contraseña si es necesaria
    DB_HOST = "localhost"
    DB_PORT = 3306
```

### Paso 3: Probar Conexión

```python
from ArtemusPark.repository.Auth_Repository import AuthRepository

auth_repo = AuthRepository()
if auth_repo.db_test_connection():
    print("✓ Conexión a BD exitosa")
else:
    print("✗ Error de conexión")
```

## Logging

El módulo database genera logs detallados para debugging. Los logs incluyen:

- Conexiones establecidas/perdidas
- Queries ejecutadas (primeros 100 caracteres)
- Número de resultados
- Errores y excepciones
- Commits y rollbacks

**Ejemplo de salida:**
```
2026-03-17 10:30:45 - DatabaseConnectionManager - INFO - Conexión establecida a localhost:3306/artemus_db
2026-03-17 10:30:46 - DatabaseConnectionManager - INFO - Test de conexión exitoso
2026-03-17 10:30:47 - DatabaseConnectionManager - INFO - INSERT exitoso. ID: 42
2026-03-17 10:30:48 - Database_Utils - INFO - Query ejecutada: SELECT * FROM users WHERE role = %s... Resultados: 3
```

## Patrones de Uso

### Opción A: Pasar a BD completamente

En controllers, cambiar:
```python
# ANTES (JSON)
users = auth_repo.get_all_users()

# DESPUÉS (BD)
users = auth_repo.db_get_all_users()
```

### Opción B: Migración gradual

Mantener ambos métodos y usar BD progresivamente:
```python
# Los nuevos módulos usan DB
# Los módulos antiguos siguen con JSON
# Eventualmente migrar todo a DB
```

### Opción C: Fallback (Recomendado durante transición)

```python
def get_users_with_fallback():
    try:
        # Intentar BD primero
        return auth_repo.db_get_all_users()
    except Exception as e:
        logger.warning(f"BD fallo, usando JSON: {e}")
        # Fallback a JSON si BD falla
        return auth_repo.get_all_users()
```

## Debugging

### Ver logs en consola

Los logs se configuran automáticamente en DEBUG por defecto. Para cambiar nivel:

```python
import logging
logging.getLogger("ArtemusPark.database").setLevel(logging.DEBUG)
```

### Verificar conexión activa

```python
manager = DatabaseConnectionManager()
if manager.get_connection() is None:
    print("No hay conexión activa")
else:
    print("Conexión activa")
```

### Test de queries

```python
manager = DatabaseConnectionManager()
try:
    results = manager.execute_query("SELECT 1 as test")
    print("Query exitosa:", results)
except Exception as e:
    print("Error en query:", e)
```

## Próximos Pasos

1. **Refactorizar repositorios restantes:**
   - Humidity_Repository.py
   - Wind_Repository.py
   - Smoke_Repository.py
   - Door_Repository.py
   - Light_Repository.py
   - Requests_Repository.py

2. **Actualizar Controllers**
   - Cambiar llamadas a métodos `db_*`
   - Agregar manejo de errores de BD

3. **Actualizar Services**
   - Usarán automáticamente métodos de BD de repositorios

4. **Tests de integración**
   - Verificar cada repositorio con BD
   - Validar migraciones de datos JSON → BD

5. **Producción**
   - Configurar contraseña segura en `Database_Config.py`
   - Implementar connection pooling si es necesario
   - Monitoreo de conexiones

---

**Última actualización:** 2026-03-17  
**Autor:** OpenCode Bot  
**Versión:** 1.0
