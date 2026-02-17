# Estrategia de Migración: JSON a Base de Datos SQL

## 1. RESUMEN EJECUTIVO

Este documento describe la estrategia para migrar el sistema Artemus Park desde su arquitectura actual basada en archivos JSON a una base de datos relacional SQL (PostgreSQL/MySQL).

### Ventajas de la Migración

- **Escalabilidad**: Capacidad de manejar millones de registros sin degradación
- **Consultas complejas**: SQL permite análisis avanzados y reportes en tiempo real
- **Integridad de datos**: Constraints, foreign keys, y transacciones ACID
- **Concurrencia**: Múltiples usuarios pueden leer/escribir simultáneamente
- **Backup y recuperación**: Herramientas maduras para respaldo y restauración
- **Seguridad**: Control de acceso granular a nivel de tabla y fila

---

## 2. ESTRATEGIA DE MIGRACIÓN

### Fase 1: Preparación (Semana 1-2)

#### 2.1 Configuración de Infraestructura

```bash
# 1. Instalar PostgreSQL
sudo apt-get install postgresql-14 postgresql-contrib

# 2. Crear base de datos
sudo -u postgres createdb artemus_park

# 3. Crear usuario
sudo -u postgres createuser -P artemus_user

# 4. Configurar permisos
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE artemus_park TO artemus_user;"
```

#### 2.2 Dependencias Python

Agregar a `requirements.txt`:

```
# Base de datos
psycopg2-binary>=2.9.0  # Para PostgreSQL
# mysql-connector-python>=8.0.0  # Alternativa para MySQL

# ORM (opcional pero recomendado)
SQLAlchemy>=2.0.0
alembic>=1.10.0  # Para migraciones

# Pool de conexiones
psycopg2-pool>=1.0.0
```

#### 2.3 Estructura de Directorios

```
ArtemusPark/
├── database/
│   ├── __init__.py
│   ├── connection.py       # Gestión de conexiones
│   ├── models.py          # Modelos SQLAlchemy
│   ├── migrations/        # Scripts de migración Alembic
│   └── seeds/            # Datos iniciales
├── repository/
│   ├── base_repository.py  # Clase base con CRUD
│   └── ... (actualizar repositorios existentes)
└── config/
    └── database_config.py  # Configuración de BD
```

---

### Fase 2: Implementación de Capa de Datos (Semana 3-4)

#### 2.1 Configuración de Conexión

```python
# ArtemusPark/database/connection.py

import os
from contextlib import contextmanager
from psycopg2 import pool, extras
from dotenv import load_dotenv

load_dotenv()

# Pool de conexiones
connection_pool = pool.ThreadedConnectionPool(
    minconn=5,
    maxconn=20,
    host=os.getenv('DB_HOST', 'localhost'),
    port=os.getenv('DB_PORT', '5432'),
    database=os.getenv('DB_NAME', 'artemus_park'),
    user=os.getenv('DB_USER', 'artemus_user'),
    password=os.getenv('DB_PASSWORD', '')
)

@contextmanager
def get_db_connection():
    """Context manager para obtener conexión del pool."""
    conn = connection_pool.getconn()
    try:
        yield conn
    finally:
        connection_pool.putconn(conn)

@contextmanager
def get_db_cursor(cursor_factory=None):
    """Context manager para obtener cursor."""
    with get_db_connection() as conn:
        cursor = conn.cursor(cursor_factory=cursor_factory or extras.RealDictCursor)
        try:
            yield cursor
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
```

#### 2.2 Modelo Base de Repositorio

```python
# ArtemusPark/repository/base_repository.py

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from ArtemusPark.database.connection import get_db_cursor

class BaseRepository(ABC):
    """Clase base para todos los repositorios."""
    
    table_name: str = None
    primary_key: str = 'id'
    
    @classmethod
    def insert(cls, data: Dict[str, Any]) -> int:
        """Inserta un registro y retorna el ID."""
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['%s'] * len(data))
        
        query = f"""
            INSERT INTO {cls.table_name} ({columns})
            VALUES ({placeholders})
            RETURNING {cls.primary_key}
        """
        
        with get_db_cursor() as cursor:
            cursor.execute(query, list(data.values()))
            result = cursor.fetchone()
            return result[cls.primary_key]
    
    @classmethod
    def find_by_id(cls, id: int) -> Optional[Dict[str, Any]]:
        """Busca un registro por ID."""
        query = f"SELECT * FROM {cls.table_name} WHERE {cls.primary_key} = %s"
        
        with get_db_cursor() as cursor:
            cursor.execute(query, (id,))
            return cursor.fetchone()
    
    @classmethod
    def find_all(cls, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Obtiene todos los registros con paginación."""
        query = f"""
            SELECT * FROM {cls.table_name}
            ORDER BY {cls.primary_key} DESC
            LIMIT %s OFFSET %s
        """
        
        with get_db_cursor() as cursor:
            cursor.execute(query, (limit, offset))
            return cursor.fetchall()
    
    @classmethod
    def update(cls, id: int, data: Dict[str, Any]) -> bool:
        """Actualiza un registro."""
        set_clause = ', '.join([f"{k} = %s" for k in data.keys()])
        query = f"""
            UPDATE {cls.table_name}
            SET {set_clause}, updated_at = CURRENT_TIMESTAMP
            WHERE {cls.primary_key} = %s
        """
        
        with get_db_cursor() as cursor:
            cursor.execute(query, list(data.values()) + [id])
            return cursor.rowcount > 0
    
    @classmethod
    def delete(cls, id: int) -> bool:
        """Elimina un registro."""
        query = f"DELETE FROM {cls.table_name} WHERE {cls.primary_key} = %s"
        
        with get_db_cursor() as cursor:
            cursor.execute(query, (id,))
            return cursor.rowcount > 0
```

#### 2.3 Repositorio de Mediciones Actualizado

```python
# ArtemusPark/repository/Temperature_Repository_DB.py

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from ArtemusPark.repository.base_repository import BaseRepository
from ArtemusPark.database.connection import get_db_cursor
from ArtemusPark.model.Temperature_Model import TemperatureModel

class TemperatureRepositoryDB(BaseRepository):
    """Repositorio de temperatura usando base de datos SQL."""
    
    table_name = 'sensor_measurements'
    
    @classmethod
    def save_temperature_measurement(cls, measurement: TemperatureModel) -> int:
        """Guarda una medición de temperatura en la BD."""
        # Obtener ID del sensor
        sensor_id = cls._get_sensor_id(measurement.sensor_id)
        
        data = {
            'sensor_id': sensor_id,
            'measured_at': datetime.fromtimestamp(measurement.timestamp),
            'value_numeric': measurement.value,
            'status': measurement.status,
            'unit': '°C'
        }
        
        return cls.insert(data)
    
    @classmethod
    def _get_sensor_id(cls, sensor_code: str) -> int:
        """Obtiene el ID interno del sensor por su código."""
        query = "SELECT id FROM sensors WHERE sensor_id = %s"
        
        with get_db_cursor() as cursor:
            cursor.execute(query, (sensor_code,))
            result = cursor.fetchone()
            if result:
                return result['id']
            raise ValueError(f"Sensor no encontrado: {sensor_code}")
    
    @classmethod
    def load_all_temperature_measurements(
        cls,
        sensor_code: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """Carga mediciones con filtros opcionales."""
        
        query = """
            SELECT 
                m.*,
                s.sensor_id as sensor_code,
                s.name as sensor_name
            FROM sensor_measurements m
            JOIN sensors s ON m.sensor_id = s.id
            WHERE s.sensor_type = 'temperature'
        """
        params = []
        
        if sensor_code:
            query += " AND s.sensor_id = %s"
            params.append(sensor_code)
        
        if start_date:
            query += " AND m.measured_at >= %s"
            params.append(start_date)
        
        if end_date:
            query += " AND m.measured_at <= %s"
            params.append(end_date)
        
        query += " ORDER BY m.measured_at DESC LIMIT %s"
        params.append(limit)
        
        with get_db_cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()
    
    @classmethod
    def get_temperature_statistics(
        cls,
        sensor_code: str,
        hours: int = 24
    ) -> Dict[str, Any]:
        """Obtiene estadísticas de temperatura."""
        
        query = """
            SELECT 
                AVG(value_numeric) as avg_temp,
                MIN(value_numeric) as min_temp,
                MAX(value_numeric) as max_temp,
                COUNT(*) as total_readings,
                COUNT(CASE WHEN status = 'HOT' THEN 1 END) as hot_readings
            FROM sensor_measurements m
            JOIN sensors s ON m.sensor_id = s.id
            WHERE s.sensor_id = %s
            AND m.measured_at >= %s
        """
        
        start_time = datetime.now() - timedelta(hours=hours)
        
        with get_db_cursor() as cursor:
            cursor.execute(query, (sensor_code, start_time))
            return cursor.fetchone()
```

---

### Fase 3: Script de Migración de Datos (Semana 5)

```python
# migration_scripts/migrate_json_to_db.py

import json
import os
from pathlib import Path
from datetime import datetime
from tqdm import tqdm

# Importar modelos y repositorios
from ArtemusPark.database.connection import get_db_connection
from ArtemusPark.model.Temperature_Model import TemperatureModel
from ArtemusPark.model.Humidity_Model import HumidityModel
from ArtemusPark.model.Wind_Model import WindModel
from ArtemusPark.model.Smoke_Model import SmokeModel
from ArtemusPark.model.Light_Model import LightModel
from ArtemusPark.model.Door_Model import DoorModel

class JSONToDBMigration:
    """Script para migrar datos de JSON a Base de Datos."""
    
    BASE_DIR = Path(__file__).resolve().parent.parent
    JSON_DIR = BASE_DIR / "ArtemusPark" / "json"
    
    def __init__(self):
        self.migrated_count = 0
        self.errors = []
    
    def migrate_all(self):
        """Ejecuta la migración completa."""
        print("Iniciando migración de JSON a Base de Datos...")
        print("=" * 60)
        
        # Migrar cada tipo de sensor
        self._migrate_temperature()
        self._migrate_humidity()
        self._migrate_wind()
        self._migrate_smoke()
        self._migrate_light()
        self._migrate_doors()
        
        # Reporte final
        print("\n" + "=" * 60)
        print(f"Migración completada:")
        print(f"  - Total registros migrados: {self.migrated_count}")
        print(f"  - Errores encontrados: {len(self.errors)}")
        
        if self.errors:
            print(f"\nErrores:")
            for error in self.errors[:10]:  # Mostrar primeros 10
                print(f"  - {error}")
    
    def _migrate_temperature(self):
        """Migra datos de temperatura."""
        print("\nMigrando datos de temperatura...")
        temp_dir = self.JSON_DIR / "temperature"
        
        if not temp_dir.exists():
            print(f"  ⚠️  Directorio no encontrado: {temp_dir}")
            return
        
        json_files = list(temp_dir.glob("temp_*.json"))
        
        for json_file in tqdm(json_files, desc="  Archivos de temperatura"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                for record in data:
                    self._insert_measurement('temperature', record)
                    self.migrated_count += 1
                    
            except Exception as e:
                self.errors.append(f"{json_file}: {str(e)}")
    
    def _insert_measurement(self, sensor_type: str, record: dict):
        """Inserta una medición en la base de datos."""
        
        query = """
            INSERT INTO sensor_measurements 
            (sensor_id, measured_at, value_numeric, status, unit, created_at)
            VALUES (
                (SELECT id FROM sensors WHERE sensor_id = %s),
                to_timestamp(%s),
                %s,
                %s,
                %s,
                CURRENT_TIMESTAMP
            )
            ON CONFLICT DO NOTHING
        """
        
        # Determinar unidad según tipo
        units = {
            'temperature': '°C',
            'humidity': '%',
            'wind': 'km/h',
            'smoke': 'ppm',
            'light': 'lux',
            'door': 'boolean'
        }
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(query, (
                    record['sensor_id'],
                    record['timestamp'],
                    record.get('value'),
                    record.get('status', 'NORMAL'),
                    units.get(sensor_type, '')
                ))
                conn.commit()
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                cursor.close()
    
    # Métodos similares para otros tipos de sensores...
    def _migrate_humidity(self):
        """Migra datos de humedad."""
        pass
    
    def _migrate_wind(self):
        """Migra datos de viento."""
        pass
    
    def _migrate_smoke(self):
        """Migra datos de humo."""
        pass
    
    def _migrate_light(self):
        """Migra datos de iluminación."""
        pass
    
    def _migrate_doors(self):
        """Migra datos de puertas."""
        pass


if __name__ == "__main__":
    migrator = JSONToDBMigration()
    migrator.migrate_all()
```

---

### Fase 4: Estrategia de Doble Escritura (Semana 6-7)

Durante la transición, se implementará **doble escritura** para mantener ambos sistemas sincronizados:

```python
# ArtemusPark/repository/hybrid_repository.py

from typing import Optional
from ArtemusPark.model.Temperature_Model import TemperatureModel
from ArtemusPark.repository.Temperature_Repository import save_temperature_measurement as save_json
from ArtemusPark.repository.Temperature_Repository_DB import TemperatureRepositoryDB

# Flag para controlar modo de operación
USE_DATABASE = os.getenv('USE_DATABASE', 'false').lower() == 'true'
ENABLE_DUAL_WRITE = os.getenv('ENABLE_DUAL_WRITE', 'false').lower() == 'true'

def save_temperature_hybrid(measurement: TemperatureModel) -> Optional[int]:
    """
    Guarda temperatura en JSON y/o Base de Datos según configuración.
    
    Estrategia:
    - Fase 1: Solo JSON (actual)
    - Fase 2: JSON + DB (doble escritura)
    - Fase 3: Solo DB (target)
    """
    db_id = None
    
    # Siempre guardar en JSON (mientras dure la migración)
    try:
        save_json(measurement)
    except Exception as e:
        print(f"Error guardando en JSON: {e}")
    
    # Guardar en base de datos si está habilitado
    if USE_DATABASE or ENABLE_DUAL_WRITE:
        try:
            db_id = TemperatureRepositoryDB.save_temperature_measurement(measurement)
        except Exception as e:
            print(f"Error guardando en BD: {e}")
    
    return db_id
```

---

### Fase 5: Verificación y Rollback (Semana 8)

#### 5.1 Script de Verificación

```python
# migration_scripts/verify_migration.py

import json
from ArtemusPark.database.connection import get_db_cursor
from ArtemusPark.repository.Temperature_Repository import load_all_temperature_measurements as load_json
from ArtemusPark.repository.Temperature_Repository_DB import TemperatureRepositoryDB

def verify_temperature_migration():
    """Verifica que los datos de temperatura se migraron correctamente."""
    
    # Contar registros en JSON
    json_data = load_json()
    json_count = len(json_data)
    
    # Contar registros en BD
    with get_db_cursor() as cursor:
        cursor.execute("""
            SELECT COUNT(*) as count 
            FROM sensor_measurements m
            JOIN sensors s ON m.sensor_id = s.id
            WHERE s.sensor_type = 'temperature'
        """)
        db_count = cursor.fetchone()['count']
    
    print(f"Verificación de Temperatura:")
    print(f"  Registros en JSON: {json_count}")
    print(f"  Registros en BD: {db_count}")
    print(f"  Diferencia: {abs(json_count - db_count)}")
    
    # Verificar algunos registros específicos
    sample = json_data[:5]
    print(f"\nVerificación de muestra:")
    for record in sample:
        sensor_id = record['sensor_id']
        timestamp = record['timestamp']
        
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT m.* 
                FROM sensor_measurements m
                JOIN sensors s ON m.sensor_id = s.id
                WHERE s.sensor_id = %s
                AND EXTRACT(EPOCH FROM m.measured_at) = %s
            """, (sensor_id, timestamp))
            
            result = cursor.fetchone()
            if result:
                print(f"  ✓ {sensor_id} @ {timestamp}: OK")
            else:
                print(f"  ✗ {sensor_id} @ {timestamp}: NO ENCONTRADO")
```

---

## 3. CONSIDERACIONES IMPORTANTES

### 3.1 Particionamiento de Tablas

Para manejar grandes volúmenes de datos históricos:

```sql
-- Crear particiones mensuales automáticamente
CREATE OR REPLACE FUNCTION create_monthly_partition()
RETURNS void AS $$
DECLARE
    partition_date DATE;
    partition_name TEXT;
BEGIN
    partition_date := DATE_TRUNC('month', CURRENT_DATE + INTERVAL '1 month');
    partition_name := 'sensor_measurements_' || TO_CHAR(partition_date, 'YYYY_MM');
    
    EXECUTE format(
        'CREATE TABLE IF NOT EXISTS %I PARTITION OF sensor_measurements 
         FOR VALUES FROM (%L) TO (%L)',
        partition_name,
        partition_date,
        partition_date + INTERVAL '1 month'
    );
END;
$$ LANGUAGE plpgsql;

-- Programar con pg_cron o similar
SELECT cron.schedule('create-partition', '0 1 1 * *', 'SELECT create_monthly_partition()');
```

### 3.2 Limpieza de Datos Antiguos

```sql
-- Política de retención: mantener 2 años de datos
CREATE OR REPLACE FUNCTION archive_old_measurements()
RETURNS void AS $$
BEGIN
    -- Mover datos antiguos a tabla de archivo
    INSERT INTO sensor_measurements_archive
    SELECT * FROM sensor_measurements
    WHERE measured_at < CURRENT_DATE - INTERVAL '2 years';
    
    -- Eliminar de tabla principal
    DELETE FROM sensor_measurements
    WHERE measured_at < CURRENT_DATE - INTERVAL '2 years';
END;
$$ LANGUAGE plpgsql;
```

### 3.3 Optimización de Consultas

```sql
-- Índices recomendados adicionales
CREATE INDEX CONCURRENTLY idx_measurements_sensor_time 
ON sensor_measurements(sensor_id, measured_at DESC);

CREATE INDEX CONCURRENTLY idx_measurements_status_time 
ON sensor_measurements(status, measured_at) 
WHERE status != 'NORMAL';

-- Índice para búsquedas por rango de tiempo
CREATE INDEX CONCURRENTLY idx_measurements_time_brin 
ON sensor_measurements USING BRIN(measured_at);
```

---

## 4. PLAN DE CONTINGENCIA

### Rollback Strategy

Si es necesario volver a JSON:

```python
# migration_scripts/rollback_to_json.py

USE_DATABASE = False  # Deshabilitar escritura en BD
ENABLE_DUAL_WRITE = False  # Mantener solo JSON

# Los datos ya están en JSON, no se pierde información
# La BD puede mantenerse como respaldo histórico
```

### Monitoreo Durante Migración

```python
# Métricas clave a monitorear
METRICS = {
    'db_connection_pool_usage': 'Usar < 80%',
    'query_response_time_p95': '< 100ms',
    'json_to_db_sync_lag': '< 5 segundos',
    'migration_error_rate': '< 0.1%'
}
```

---

## 5. CHECKLIST DE MIGRACIÓN

### Pre-Migración
- [ ] Backup completo de archivos JSON
- [ ] Instalación y configuración de PostgreSQL
- [ ] Creación de usuarios y permisos
- [ ] Configuración de firewall y seguridad
- [ ] Pruebas en ambiente de desarrollo

### Durante Migración
- [ ] Ejecución de script de migración
- [ ] Verificación de integridad de datos
- [ ] Activación de doble escritura
- [ ] Monitoreo de performance
- [ ] Pruebas de todas las funcionalidades

### Post-Migración
- [ ] Desactivación de escritura en JSON
- [ ] Configuración de backups automáticos de BD
- [ ] Documentación actualizada
- [ ] Capacitación al equipo
- [ ] Plan de mantenimiento definido

---

## 6. TIMELINE RESUMIDO

| Fase | Duración | Actividades Principales |
|------|----------|------------------------|
| 1. Preparación | 2 semanas | Setup BD, dependencias, estructura |
| 2. Implementación | 2 semanas | Repositorios, modelos, conexiones |
| 3. Migración de Datos | 1 semana | Script de migración, verificación |
| 4. Doble Escritura | 2 semanas | Operación paralela, monitoreo |
| 5. Cutover | 1 semana | Cambio a BD exclusiva |
| 6. Limpieza | 1 semana | Remover código JSON, documentación |

**Total estimado: 9 semanas**

---

## 7. CONCLUSIÓN

La migración a base de datos SQL proporcionará:
- Mayor escalabilidad y performance
- Mejor integridad y consistencia de datos
- Capacidad de análisis avanzado
- Facilidad para reportes y auditorías
- Preparación para futuras integraciones

La estrategia de doble escritura minimiza riesgos y permite rollback inmediato si es necesario.
