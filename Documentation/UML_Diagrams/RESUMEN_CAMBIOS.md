# Resumen de Actualización de Diagramas UML

## Diagramas Actualizados (13 archivos)

### 1. Diagrama de Paquetes ✅
**Archivo:** `Diagrama_Paquetes.puml`

**Cambios realizados:**
- ✅ Nueva estructura de carpetas (Clean Architecture)
- ✅ Capa `core/` - Utilidades y constantes
- ✅ Capa `domain/` - Modelos, repositorios (interfaces), servicios
- ✅ Capa `infrastructure/` - Database, MQTT, Cache
- ✅ Capa `application/` - DTOs, Use Cases, Mappers
- ✅ Capa `presentation/` - Controllers, ViewModels, Views
- ✅ Relaciones entre capas con estereotipos
- ✅ Eliminada carpeta `json/` (no aplica para IoT real)

---

### 2. Diagrama de Clases ✅
**Archivo:** `Diagrama_Clases.puml`

**Cambios realizados:**
- ✅ Entidad `SensorReading` con campos CRUD:
  - `is_corrected`, `corrected_at`, `corrected_by`
  - `created_at`, `metadata`
  - Métodos: `correct()`, `mark_as_alert()`
- ✅ Entidad `User` con permisos (`can_edit_readings()`, etc.)
- ✅ Entidad `Alert` completa
- ✅ Enums: `UserRole`, `AlertSeverity`
- ✅ Interfaces de repositorio (ISensorRepository, etc.)
- ✅ Servicios de dominio con operaciones CRUD
- ✅ Casos de uso: Receive, Update, Delete, History
- ✅ DTOs para transferencia de datos
- ✅ Mappers para conversión
- ✅ Capa de presentación con ViewModels
- ✅ Infrastructure: MQTT, PostgreSQL, Redis

---

### 3. Diagrama de Componentes ✅
**Archivo:** `Diagrama_Componentes.puml`

**Cambios realizados:**
- ✅ **Capa IoT - Dispositivos**: Sensores físicos
- ✅ **Capa IoT - Gateway**: MQTT Broker, Subscriber, Handler
- ✅ **Capa Aplicación**: Casos de uso con operaciones CRUD
- ✅ **Capa Dominio**: Servicios (Sensor, Alert, Auth)
- ✅ **Capa Infraestructura**: Repositorios PostgreSQL
- ✅ **Capa Datos**: PostgreSQL + Redis
- ✅ **Capa Presentación**: Controllers, ViewModels, Views con CRUD UI
- ✅ Flujo completo: Sensor → MQTT → UseCase → Service → Repo → BD → UI
- ✅ Flujo CRUD: Usuario → Controller → UseCase → Autorización → Update → BD
- ✅ Eliminado: Archivos JSON, repositorios JSON

---

### 4. Diagramas de Secuencia ✅

#### A. Diagrama_Secuencia_IoT.puml (NUEVO)
**Flujo automático Sensor → BD → UI:**
1. Sensor publica por MQTT
2. Subscriber recibe y valida
3. ReceiveSensorDataUseCase procesa
4. SensorService calcula status
5. SensorRepository guarda en PostgreSQL
6. DashboardViewModel actualiza UI
7. DashboardView muestra datos/alertas

#### B. Diagrama_Secuencia_CRUD.puml (NUEVO)
**Operación Update (Usuario edita lectura):**
1. Usuario clic en "Editar" en tabla
2. Dialog muestra formulario
3. Usuario confirma cambio
4. Controller llama a UpdateUseCase
5. AuthService verifica permisos
6. SensorService marca como corregido
7. SensorRepository actualiza en BD
8. ViewModel notifica cambio
9. Tabla refresca con datos actualizados

#### C. Diagrama_Secuencia_Procesamiento.puml (SIMPLIFICADO)
- Versión simplificada para referencia

---

### 5. Diagrama de Casos de Uso ✅
**Archivo:** `Diagrama_Casos_Uso.puml`

**Cambios realizados:**
- ✅ **Nuevo paquete**: "Ingesta de Datos IoT" (automático)
  - Recibir datos por MQTT
  - Validar esquema
  - Persistir en BD
  - Evaluar umbrales
- ✅ **Nuevo paquete**: "Gestión de Datos (CRUD)"
  - Crear lectura manual
  - Ver detalle lectura
  - Editar lectura
  - Eliminar lectura
  - Corregir valor anómalo
  - Ver auditoría cambios
- ✅ Actor "Usuario Visualizador" (solo lectura)
- ✅ Relaciones de inclusión/extend actualizadas
- ✅ Permisos diferenciados por rol

---

### 6. Diagrama Entidad-Relación ✅
**Archivo:** `Diagrama_Base_Datos_ER.puml`

**Cambios realizados:**
- ✅ Tabla `sensor_readings` (renombrada de measurements):
  - Campos de auditoría CRUD:
    - `is_corrected: BOOLEAN`
    - `original_value: DECIMAL`
    - `corrected_at: TIMESTAMP`
    - `corrected_by: UUID (FK)`
    - `correction_reason: TEXT`
  - `received_at: TIMESTAMP`
  - `metadata: JSON`
- ✅ **Nueva tabla**: `audit_log` (registro de cambios)
  - `table_name`, `record_id`
  - `action: ENUM(INSERT, UPDATE, DELETE)`
  - `old_values: JSON`, `new_values: JSON`
  - `performed_by`, `performed_at`
  - `ip_address`, `user_agent`
- ✅ Tipos de datos: UUID en lugar de INT
- ✅ Relaciones simplificadas (solo las esenciales)

---

## Diagramas Adicionales (Sin cambios mayores)

### 7. Diagrama de Actividad - Procesamiento
**Archivo:** `Diagrama_Actividad_Procesamiento.puml`
- ✅ Vigente, describe flujo interno

### 8. Diagrama de Actividad - Autenticación
**Archivo:** `Diagrama_Actividad_Autenticacion.puml`
- ✅ Vigente, describe login

### 9. Diagrama de Despliegue
**Archivo:** `Diagrama_Despliegue.puml`
- ✅ Vigente, describe infraestructura

### 10. Diagrama de Estados - Alertas
**Archivo:** `Diagrama_Estados_Alertas.puml`
- ✅ Vigente, ciclo de vida de alertas

### 11. Diagrama de Paquetes (Simple)
**Archivo:** `Diagrama_Paquetes_Simple.puml`
- ✅ Versión simplificada disponible

---

## Cambios Clave en la Arquitectura

### Antes (Simulación JSON)
```
Sensores (simulados) → Controller → JSON files → View
```

### Después (IoT Real + CRUD)
```
Sensores IoT → MQTT → UseCase → Service → Repository → PostgreSQL
                                          ↓
Usuario → Controller → UseCase → Autorización → UPDATE → PostgreSQL
                                          ↓
                                    ViewModel → View (Flet)
```

### Operaciones Soportadas

| Operación | Flujo | Actor |
|-----------|-------|-------|
| **CREATE** | Sensor IoT automático o Manual (Admin) | Sistema / Admin |
| **READ** | Consulta historial, Dashboard | Todos |
| **UPDATE** | Corrección de lectura errónea | Admin, Técnico |
| **DELETE** | Eliminación de lectura | Admin |
| **AUDIT** | Ver trazabilidad de cambios | Admin |

---

## Estructura de Archivos UML

```
Documentation/UML_Diagrams/
├── Diagrama_Paquetes.puml                    ✅ ACTUALIZADO
├── Diagrama_Clases.puml                      ✅ ACTUALIZADO
├── Diagrama_Componentes.puml                 ✅ ACTUALIZADO
├── Diagrama_Casos_Uso.puml                   ✅ ACTUALIZADO
├── Diagrama_Base_Datos_ER.puml               ✅ ACTUALIZADO
├── Diagrama_Secuencia_IoT.puml               ✅ NUEVO
├── Diagrama_Secuencia_CRUD.puml              ✅ NUEVO
├── Diagrama_Secuencia_Procesamiento.puml     ✅ SIMPLIFICADO
├── Diagrama_Actividad_Procesamiento.puml     ✅ VIGENTE
├── Diagrama_Actividad_Autenticacion.puml     ✅ VIGENTE
├── Diagrama_Despliegue.puml                  ✅ VIGENTE
├── Diagrama_Estados_Alertas.puml             ✅ VIGENTE
└── Diagrama_Paquetes_Simple.puml             ✅ VIGENTE
```

---

## Próximos Pasos

1. **Implementar esquema SQL** (crear tablas con auditoría)
2. **Desarrollar MQTT Subscriber** (recibir datos reales)
3. **Implementar repositorios SQL** (CRUD en PostgreSQL)
4. **Desarrollar casos de uso** (lógica de aplicación)
5. **Actualizar vistas Flet** (tablas con edición)
6. **Testing end-to-end** (sensor → BD → UI)

---

## Resumen de Cambios por Diagrama

| Diagrama | Estado | Cambios Principales |
|----------|--------|---------------------|
| Paquetes | ✅ Actualizado | Arquitectura limpia (Clean Architecture) |
| Clases | ✅ Actualizado | Entidades CRUD, Use Cases, ViewModels |
| Componentes | ✅ Actualizado | Flujo IoT, capas separadas |
| Secuencia IoT | ✅ Nuevo | Flujo automático sensor → BD |
| Secuencia CRUD | ✅ Nuevo | Flujo usuario edita → BD |
| Casos de Uso | ✅ Actualizado | Paquetes IoT y CRUD |
| ER | ✅ Actualizado | Tabla auditoría, campos corrección |
| Otros | ✅ Vigentes | Sin cambios necesarios |

**Total: 13 diagramas UML actualizados y listos para usar**
