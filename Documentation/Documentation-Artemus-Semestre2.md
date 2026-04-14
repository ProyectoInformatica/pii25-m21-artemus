# Anteproyecto Semestre 2: Evolución del Proyecto Artemus

## 1. Introducción

Este documento presenta la planificación para la segunda fase del proyecto Artemus, centrándose en la migración de la gestión de datos hacia un sistema de base de datos robusto y la integración de conceptos avanzados para optimizar el rendimiento y la escalabilidad. El proyecto Artemus, inicialmente concebido como un sistema IoT inteligente para el monitoreo de un parque, busca ahora consolidar su infraestructura de datos y mejorar sus capacidades de procesamiento y análisis.

## 2. Inventario de Sensores y Nomenclatura

Basado en la documentación de `sensoresEspecificacione.pdf`, el sistema actualmente cuenta con un total de 13 sensores, cada uno con un identificador único (ID) que se utilizará en la API, el firmware y la base de datos.

| Nº  | Tipo          | ID del Sensor | Descripción                      |
|:----|:--------------|:--------------|:---------------------------------|
| 1   | Temperatura   | TEMP_01       | Sensor de temperatura n.º 1      |
| 2   | Temperatura   | TEMP_02       | Sensor de temperatura n.º 2      |
| 3   | Temperatura   | TEMP_03       | Sensor de temperatura n.º 3      |
| 4   | Temperatura   | TEMP_04       | Sensor de temperatura n.º 4      |
| 5   | Temperatura   | TEMP_05       | Sensor de temperatura n.º 5      |
| 6   | Humedad       | HUM_01        | Sensor de humedad n.º 1          |
| 7   | Humedad       | HUM_02        | Sensor de humedad n.º 2          |
| 8   | Humedad       | HUM_03        | Sensor de humedad n.º 3          |
| 9   | Humedad       | HUM_04        | Sensor de humedad n.º 4          |
| 10  | Humedad       | HUM_05        | Sensor de humedad n.º 5          |
| 11  | Puerta        | DOOR_01       | Sensor de apertura de puerta n.º 1 |
| 12  | Puerta        | DOOR_02       | Sensor de apertura de puerta n.º 2 |
| 13  | Anemómetro    | ANMETER       | Sensor de velocidad del viento   |

La convención de nombres para los IDs es la siguiente:
*   `TEMP_xx`: Sensores de temperatura.
*   `HUM_xx`: Sensores de humedad.
*   `DOOR_xx`: Sensores de puerta.
*   `ANMETER`: Anemómetro (único).

## 3. Planificación de la Estructura de Bases de Datos

Con la comprensión de que el equipo no tiene experiencia previa en bases de datos, se propone el siguiente plan.

### 3.1. Período de Formación y Capacitación (4 semanas)
*   (El contenido de esta sección se mantiene igual que en la versión anterior)

### 3.2. Diseño de la Base de Datos (2 semanas)

El diseño de la base de datos se basará en las estructuras de colección propuestas en `sensoresEspecificacione.pdf`, formalizándolas en un esquema relacional (o NoSQL, según se decida).

**Tabla/Colección `Sensores`:**
Esta tabla almacenará la información estática de cada sensor.

| Campo         | Tipo             | Descripción                                   |
|:--------------|:-----------------|:----------------------------------------------|
| `id`            | `string` (PK)    | Identificador único (ej., "TEMP_01")          |
| `tipo`          | `string`         | Tipo de sensor (temperatura, humedad, etc.)   |
| `ubicacion`     | `string`         | Zona del parque donde está instalado          |
| `estado`        | `string`         | "active" o "inactive"                         |
| `ultimo_ping`   | `datetime`       | Fecha y hora de la última comunicación        |
| `ultimo_valor`  | `number`/`string`| Última lectura recibida (opcional)            |

**Tabla/Colección `Mantenimiento`:**
Esta tabla servirá como un log para registrar todos los eventos de fallo y recuperación de los sensores.

| Campo              | Tipo             | Descripción                                   |
|:-------------------|:-----------------|:----------------------------------------------|
| `id_evento`        | `string` (PK)    | ID único del evento (ej., "EVT_00123")        |
| `sensor_id`        | `string` (FK)    | ID del sensor afectado (ej., "TEMP_03")       |
| `fecha_fallo`      | `datetime`       | Cuándo el sensor dejó de enviar datos         |
| `fecha_recuperacion`| `datetime`/`null`| Cuándo volvió a funcionar (si aplica)         |
| `tiempo_caida`     | `number`         | Duración total de la caída en segundos        |
| `causa`            | `string`         | Descripción breve del fallo (opcional)        |
| `estado_evento`    | `string`         | "abierto" o "cerrado"                         |

**Tabla/Colección `Mediciones`:**
Se creará una tabla adicional para almacenar las lecturas históricas de los sensores, permitiendo análisis y evitando sobrecargar la tabla `Sensores`.

| Campo         | Tipo             | Descripción                                   |
|:--------------|:-----------------|:----------------------------------------------|
| `id_medicion`   | `bigint` (PK)    | ID autoincremental de la medición             |
| `sensor_id`     | `string` (FK)    | ID del sensor que generó la lectura           |
| `timestamp`     | `datetime`       | Fecha y hora exactas de la medición           |
| `valor`         | `number`/`string`| El valor numérico o estado de la lectura      |


### 3.3. Implementación y Migración (9 semanas)
*   (El contenido de esta sección se mantiene similar, pero ahora se trabajará con las tablas específicas definidas arriba)

## 4. Proceso Automático de Verificación de Sensores (`cron job`)

Como se especifica en `sensoresEspecificacione.pdf`, es fundamental crear un proceso automático (`cron job` o `scheduler`) para supervisar el estado de los sensores.

### 4.1. Propósito
Detectar inactividad, gestionar cambios de estado y coordinar acciones de mantenimiento de forma proactiva.

### 4.2. Lógica del Proceso
1.  **Frecuencia:** El proceso se ejecutará periódicamente (ej., cada minuto).
2.  **Revisión:** Para cada sensor en la tabla `Sensores`, comparará `ultimo_ping` con la hora actual.
3.  **Criterio de Inactividad:** Un sensor se considera `inactivo` si no envía datos durante más de 60 segundos.
4.  **Acciones:**
    *   **Si un sensor se vuelve inactivo:**
        *   Actualiza su `estado` a "inactive" en la tabla `Sensores`.
        *   Crea un nuevo registro en la tabla `Mantenimiento` con `estado_evento` = "abierto".
    *   **Si un sensor inactivo vuelve a reportar:**
        *   Actualiza su `estado` a "active" en la tabla `Sensores`.
        *   Actualiza el registro correspondiente en `Mantenimiento`: establece `fecha_recuperacion`, calcula `tiempo_caida` y cambia `estado_evento` a "cerrado".

## 5. Conceptos Técnicos Avanzados
*   (El contenido de esta sección se mantiene igual que en la versión anterior)

## 6. Reacondicionamiento del Proyecto a la Nueva Modificación
*   (El contenido de esta sección se mantiene igual, pero ahora se enfoca en implementar los nuevos repositorios para las tablas `Sensores`, `Mantenimiento` y `Mediciones`)

---

Este plan actualizado es mucho más específico gracias a los detalles del `sensoresEspecificacione.pdf`. Proporciona una base sólida para diseñar la base de datos y los procesos de monitoreo.