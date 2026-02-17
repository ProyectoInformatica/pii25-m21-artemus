# Documentación UML - Sistema Artemus Park

## Índice de Diagramas

Esta carpeta contiene la documentación completa de arquitectura y diseño del sistema Artemus Park, incluyendo diagramas UML y propuesta de migración a base de datos.

---

## 📊 Diagramas Disponibles

### 1. Diagrama de Casos de Uso
**Archivo:** `Diagrama_Casos_Uso.puml`

**Descripción:** Muestra todas las interacciones entre actores y el sistema, organizadas por paquetes funcionales:
- **Monitoreo de Sensores**: Visualización de datos en tiempo real
- **Gestión de Emergencias**: Detección y respuesta a alertas
- **Administración del Sistema**: Gestión de usuarios y configuración
- **Mantenimiento**: Solicitudes y asignaciones a técnicos
- **Servicios al Cliente**: Funcionalidades para usuarios finales

**Actores identificados:**
- Administrador (acceso total)
- Técnico de Mantenimiento (sensores asignados)
- Usuario Cliente (información general)
- Sensor (sistema automatizado)

---

### 2. Diagramas de Actividad

#### 2.1 Procesamiento de Datos de Sensores
**Archivo:** `Diagrama_Actividad_Procesamiento.puml`

**Descripción:** Flujo completo desde la captura del sensor hasta:
- Validación de datos
- Almacenamiento en base de datos
- Evaluación de riesgos
- Generación de alertas
- Actualización del dashboard

#### 2.2 Autenticación y Gestión
**Archivo:** `Diagrama_Actividad_Autenticacion.puml`

**Descripción:** Flujo de login según rol de usuario:
- Validación de credenciales
- Redirección según permisos
- Funcionalidades específicas por rol

---

### 3. Diagrama de Clases
**Archivo:** `Diagrama_Clases.puml`

**Descripción:** Arquitectura completa del sistema organizada en capas:

#### Capas identificadas:
1. **Models**: Entidades de datos (TemperatureModel, SmokeModel, UserModel, etc.)
2. **Controllers**: Lógica de control y orquestación
3. **Repositories**: Acceso a datos y persistencia
4. **Services**: Lógica de negocio (evaluación de riesgos)
5. **Views**: Interfaz de usuario y componentes visuales
6. **Configuration**: Configuraciones del sistema

**Relaciones principales:**
- Herencia entre modelos base y específicos
- Composición entre SensorController y controladores específicos
- Uso de repositorios desde controladores
- Inyección de dependencias en vistas

---

### 4. Diagrama de Secuencia
**Archivo:** `Diagrama_Secuencia_Procesamiento.puml`

**Descripción:** Secuencia temporal del flujo de datos:
1. Sensor envía medición
2. Controlador valida y procesa
3. Paralelismo: Guardar en BD + Evaluar riesgos
4. Actualización de vista
5. Manejo de alertas según severidad

**Aspectos destacados:**
- Procesamiento paralelo (par/and)
- Decisiones condicionales (alt/else)
- Ciclo continuo de monitoreo

---

### 5. Diagrama de Componentes
**Archivo:** `Diagrama_Componentes.puml`

**Descripción:** Arquitectura de alto nivel mostrando:
- **Capa de Presentación**: Dashboard, paneles administrativos
- **Capa de Control**: Controladores de sensores
- **Capa de Servicios**: Lógica de negocio
- **Capa de Repositorio**: Acceso a datos
- **Capa de Datos**: Base de datos y archivos JSON
- **Dispositivos**: Sensores IoT

**Conectividad:**
- Protocolos de comunicación (HTTP, MQTT, SQL)
- Dependencias entre componentes
- Flujo de datos entre capas

---

### 6. Diagrama de Despliegue
**Archivo:** `Diagrama_Despliegue.puml`

**Descripción:** Infraestructura propuesta para producción:

#### Servidores:
- **Servidor Web**: Nginx como reverse proxy y load balancer
- **Servidores de Aplicación**: Múltiples instancias Python/Flet
- **Servidor de Base de Datos**: PostgreSQL con PgBouncer
- **Servidor de Cache**: Redis para sesiones y cache
- **Servidor de Mensajería**: RabbitMQ/Kafka para IoT
- **Servidor de Monitoreo**: Prometheus + Grafana + ELK

#### Dispositivos:
- Gateway IoT para sensores
- Protocolo MQTT para comunicación

#### Servicios Externos:
- Email (SendGrid/AWS SES)
- SMS (Twilio)
- Cloud Storage
- Autenticación externa

---

### 7. Diagrama de Estados - Alertas
**Archivo:** `Diagrama_Estados_Alertas.puml`

**Descripción:** Ciclo de vida completo de una alerta:

#### Estados:
1. **Detection**: Validación inicial del umbral
2. **Pending**: Alerta creada, esperando reconocimiento
3. **Acknowledged**: Técnico asignado, en investigación
4. **InProgress**: Trabajo activo en solución
5. **Escalated**: Escalamiento por timeout o dificultad
6. **Critical**: Emergencia confirmada, protocolo activo
7. **Resolved**: Problema solucionado y documentado
8. **Reopened**: Reapertura si el problema persiste

**Transiciones:**
- Automáticas (timeout, umbral)
- Manuales (reconocimiento, resolución)

---

### 8. Modelo Entidad-Relación
**Archivo:** `Diagrama_Base_Datos_ER.puml`

**Descripción:** Modelo relacional completo para base de datos SQL:

#### Entidades principales:
- **users**: Usuarios del sistema con roles
- **sensors**: Catálogo de sensores instalados
- **sensor_measurements**: Mediciones históricas (particionada)
- **alerts**: Registro de alertas y eventos
- **maintenance_requests**: Solicitudes de mantenimiento
- **user_sensor_assignments**: Asignación técnico-sensor
- **sensor_maintenance_logs**: Historial de mantenimientos
- **park_access_logs**: Registro de accesos
- **system_config**: Configuraciones del sistema

**Características:**
- Relaciones 1:N y N:M
- Índices recomendados
- Notas de implementación
- Vistas para consultas frecuentes

---

### 9. Esquema SQL Completo
**Archivo:** `esquema_base_datos.sql`

**Descripción:** Script SQL completo listo para ejecutar:

#### Contenido:
- ✅ Definición de tipos ENUM
- ✅ Creación de todas las tablas
- ✅ Índices optimizados
- ✅ Claves foráneas y constraints
- ✅ Particionamiento de tablas de mediciones
- ✅ Vistas útiles (sensor_latest_status, active_alerts)
- ✅ Funciones y triggers (auto-update de timestamps)
- ✅ Datos iniciales (seed)
- ✅ Comentarios en español

**Compatibilidad:** PostgreSQL 14+ (con instrucciones para MySQL)

---

### 10. Estrategia de Migración
**Archivo:** `ESTRATEGIA_MIGRACION_JSON_A_BD.md`

**Descripción:** Guía completa para migrar de JSON a base de datos:

#### Secciones:
1. **Resumen Ejecutivo**: Ventajas de la migración
2. **Estrategia de 5 Fases**: Timeline de 9 semanas
3. **Implementación de Capa de Datos**: Código Python
4. **Script de Migración**: Carga de datos históricos
5. **Doble Escritura**: Estrategia de transición segura
6. **Verificación**: Validación de integridad
7. **Consideraciones**: Particionamiento, limpieza, optimización
8. **Plan de Contingencia**: Rollback si es necesario
9. **Checklist**: Tareas pre/durante/post migración

#### Código incluido:
- Configuración de conexión a BD
- Repositorio base con CRUD
- Repositorio específico de temperatura
- Script de migración con progreso
- Verificación de datos migrados
- Estrategia de doble escritura

---

## 🛠️ Cómo Visualizar los Diagramas

### Opción 1: VS Code con Extensión PlantUML
1. Instalar extensión "PlantUML"
2. Abrir cualquier archivo `.puml`
3. Presionar `Alt+D` para previsualizar
4. Exportar a PNG/SVG/PDF

### Opción 2: PlantUML Online
1. Visitar: http://www.plantuml.com/plantuml/uml/
2. Copiar contenido del archivo `.puml`
3. Ver diagrama generado automáticamente

### Opción 3: PlantUML Local (Java)
```bash
# Instalar Java y Graphviz
sudo apt-get install default-jre graphviz

# Descargar plantuml.jar
wget https://sourceforge.net/projects/plantuml/files/plantuml.jar/download

# Generar diagrama
java -jar plantuml.jar Diagrama_Casos_Uso.puml
```

---

## 📈 Arquitectura Propuesta

### Estado Actual (JSON)
```
Sensores → Controladores → Repositorios → Archivos JSON
                                ↓
                            Vistas Flet
```

### Estado Objetivo (Base de Datos)
```
Sensores → Controladores → Repositorios → PostgreSQL
                    ↓                        ↓
            Servicios de                  Cache
            Riesgos (Redis)
                    ↓
            Mensajería (RabbitMQ)
                    ↓
            Vistas Flet + Web
```

### Beneficios de la Migración

| Aspecto | JSON | Base de Datos |
|---------|------|---------------|
| **Escalabilidad** | Limitada por disco | Millones de registros |
| **Consultas** | Lineales, lentas | SQL optimizado, índices |
| **Concurrencia** | Bloqueos de archivo | ACID, transacciones |
| **Backup** | Copia manual | Automático, point-in-time |
| **Análisis** | Scripts custom | BI, reportes avanzados |
| **Seguridad** | Básica | RBAC, encriptación |
| **Integración** | Compleja | APIs, conectores |

---

## 🗂️ Estructura de Sensores

Basado en `ArtemusPark/config/Sensor_Config.py`:

| Tipo | IDs | Descripción | Umbrales |
|------|-----|-------------|----------|
| **Temperature** | temp_01, temp_02, temp_03 | Zonas Norte, Sur, Central | >30°C Warning, >35°C Emergency |
| **Humidity** | hum_01, hum_02 | Jardines, Invernadero | Configurable |
| **Wind** | wind_01 | Torre Principal | >60km/h Warning, >80km/h Emergency |
| **Smoke** | smoke_01, smoke_02 | Cafetería, Almacén | >30ppm Warning, >45ppm Emergency |
| **Door** | door_01, door_02 | Torniquete, Proveedores | Estado binario |
| **Light** | light_01, light_02 | Paseo Central, Parking | Estado ON/OFF + valor |

---

## 📊 Tipos de Datos por Sensor

### Temperatura
```json
{
  "sensor_id": "temp_01",
  "timestamp": 1770133134.491,
  "value": 31,
  "status": "HOT"
}
```

### Iluminación
```json
{
  "sensor_id": "light_01",
  "timestamp": 1770133134.491,
  "is_on": true,
  "status": "OK",
  "value": 217.95
}
```

### Humo
```json
{
  "sensor_id": "smoke_01",
  "timestamp": 1770133134.491,
  "value": 46,
  "status": "WARNING"
}
```

---

## 🔐 Roles de Usuario

Basado en `ArtemusPark/json/users.json`:

| Rol | Permisos | Usuarios Ejemplo |
|-----|----------|------------------|
| **Admin** | Acceso total, gestión usuarios, reportes | admin1, admin_super, boss_artemus |
| **Maintenance** | Sensores asignados, solicitudes mantenimiento | maint_joe, tech_sarah |
| **User** | Dashboard básico, solicitudes visita | client_ana, visit_tom, user_demo |

---

## 📝 Notas de Implementación

### Migración Recomendada
1. ✅ PostgreSQL 14+ (mejor soporte JSON y particionamiento)
2. ✅ Pool de conexiones (psycopg2-pool)
3. ✅ ORM opcional (SQLAlchemy) o SQL nativo
4. ✅ Migraciones versionadas (Alembic)
5. ✅ Estrategia de doble escritura durante transición

### Optimizaciones Futuras
- [ ] Implementar particionamiento mensual automático
- [ ] Agregar índices BRIN para consultas por tiempo
- [ ] Configurar replicación master-slave
- [ ] Implementar caché con Redis
- [ ] Agregar cola de mensajes para IoT
- [ ] Dashboard de monitoreo con Grafana

---

## 📚 Recursos Adicionales

- **Documentación Original**: Ver carpeta `/Documentation/`
- **Configuración Sensores**: `ArtemusPark/config/Sensor_Config.py`
- **Controlador Principal**: `ArtemusPark/controller/Sensor_Controller.py`
- **Repositorios Actuales**: `ArtemusPark/repository/*_Repository.py`

---

## 🤝 Contribución

Para actualizar o agregar diagramas:
1. Crear archivo `.puml` con nombre descriptivo
2. Seguir convenciones de nomenclatura
3. Incluir comentarios explicativos
4. Actualizar este README
5. Verificar que renderiza correctamente

---

## 📄 Licencia

Esta documentación es parte del proyecto Artemus Park y sigue las mismas licencias del proyecto principal.

---

**Última actualización:** Febrero 2025  
**Versión:** 1.0  
**Autor:** Sistema de documentación automática
