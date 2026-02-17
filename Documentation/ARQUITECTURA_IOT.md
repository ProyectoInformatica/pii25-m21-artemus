# Arquitectura IoT - Sistema Artemus Park

## Índice
1. [Resumen Ejecutivo](#resumen-ejecutivo)
2. [Arquitectura Propuesta](#arquitectura-propuesta)
3. [Estructura del Proyecto](#estructura-del-proyecto)
4. [Componentes Principales](#componentes-principales)
5. [Flujo de Datos](#flujo-de-datos)
6. [Stack Tecnológico](#stack-tecnológico)
7. [Implementación](#implementación)
8. [Entregables Académicos](#entregables-académicos)

---

## Resumen Ejecutivo

### Contexto
Sistema de gestión de parque con monitoreo en tiempo real mediante sensores IoT físicos conectados vía WiFi/4G.

### Características del Sistema IoT
- **Sensores reales**: Conectados mediante MQTT, CoAP, HTTP POST
- **Frecuencia**: Datos cada 1-5 segundos por sensor
- **Volumen**: ~100-1000 sensores potenciales
- **Sin datos históricos**: Arquitectura greenfield (sin JSON previos)

### Objetivos
- Ingesta masiva de datos en tiempo real
- Procesamiento asíncrono con baja latencia (< 200ms)
- Alertas automáticas basadas en umbrales
- Dashboard en tiempo real

---

## Arquitectura Propuesta

### Diagrama de Alto Nivel

```
┌──────────────────────────────────────────────────────────────────────┐
│                         CAPA DE EDGE                                  │
│                    (Gateway IoT - Raspberry Pi / Industrial)          │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                 │
│   │  Sensores   │  │  Sensores   │  │  Sensores   │                 │
│   │  Zigbee     │  │  WiFi       │  │  LoRaWAN    │                 │
│   │  (Humedad)  │  │  (Temp)     │  │  (Viento)   │                 │
│   └──────┬──────┘  └──────┬──────┘  └──────┬──────┘                 │
│          │                │                │                         │
│          └────────────────┴────────────────┘                         │
│                            │                                         │
│                    ┌───────▼────────┐                               │
│                    │  IoT Gateway   │                               │
│                    │  (Mosquitto /  │                               │
│                    │   EMQX Broker) │                               │
│                    └───────┬────────┘                               │
│                            │ MQTT                                    │
└────────────────────────────┼─────────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────────┐
│                      CAPA DE NUBE (Servidor)                         │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   ┌─────────────────────────────────────────────────────────────┐   │
│   │              MQTT BROKER CLUSTER (Alta Disponibilidad)       │   │
│   │         ┌─────────────┐         ┌─────────────┐              │   │
│   │         │   Node 1    │◄───────►│   Node 2    │              │   │
│   │         │  (Master)   │         │  (Slave)    │              │   │
│   │         └──────┬──────┘         └─────────────┘              │   │
│   │                │                                              │   │
│   │                ▼ MQTT Topics                                  │   │
│   │    ┌──────────────────────────────────────────────┐          │   │
│   │    │  sensores/temperatura/+/datos               │          │   │
│   │    │  sensores/humedad/+/datos                   │          │   │
│   │    │  sensores/alertas/criticas                  │          │   │
│   │    └──────────────────────────────────────────────┘          │   │
│   └─────────────────────────────────────────────────────────────┘   │
│                              │                                       │
│                              ▼                                       │
│   ┌─────────────────────────────────────────────────────────────┐   │
│   │              INGESTA Y PROCESAMIENTO                         │   │
│   │                                                              │   │
│   │    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐ │   │
│   │    │   MQTT       │    │   Stream     │    │   Timeseries │ │   │
│   │    │   Handler    │───►│   Processor  │───►│   Database   │ │   │
│   │    │   (Python)   │    │   (Asyncio)  │    │   (InfluxDB/ │ │   │
│   │    │              │    │              │    │   TimescaleDB│ │   │
│   │    └──────────────┘    └──────────────┘    └──────────────┘ │   │
│   │                                                      │       │   │
│   │                                                      ▼       │   │
│   │                                               ┌──────────────┐│   │
│   │                                               │  PostgreSQL  ││   │
│   │                                               │  (Metadatos, ││   │
│   │                                               │   Config)    ││   │
│   │                                               └──────────────┘│   │
│   └─────────────────────────────────────────────────────────────┘   │
│                              │                                       │
│                              ▼                                       │
│   ┌─────────────────────────────────────────────────────────────┐   │
│   │              APLICACIÓN ARTEMUS PARK                         │   │
│   │                                                              │   │
│   │    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐ │   │
│   │    │  Dashboard   │    │  Alertas     │    │  API REST    │ │   │
│   │    │  (Flet/Web)  │    │  (WebSocket) │    │  (FastAPI)   │ │   │
│   │    └──────────────┘    └──────────────┘    └──────────────┘ │   │
│   │                                                              │   │
│   └─────────────────────────────────────────────────────────────┘   │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Estructura del Proyecto

```
ArtemusPark/
├── gateway/                 # Gateway IoT
│   ├── mqtt_broker/        # Configuración Mosquitto/EMQX
│   ├── edge_processor/     # Procesamiento en edge (opcional)
│   └── protocol_adapters/  # Adaptadores MQTT/CoAP/HTTP
│
├── ingestion/              # Capa de ingesta
│   ├── mqtt_handler.py     # Suscriptor MQTT
│   ├── message_parser.py   # Parser de payloads
│   ├── validator.py        # Validación de datos
│   └── buffer.py           # Buffer temporal
│
├── processing/             # Procesamiento
│   ├── stream_processor.py # Procesamiento en tiempo real
│   ├── aggregators.py      # Agregaciones (avg, min, max)
│   ├── alert_engine.py     # Motor de alertas
│   └── workers/            # Workers async
│
├── storage/                # Persistencia
│   ├── timeseries/         # InfluxDB/TimescaleDB
│   │   ├── connection.py
│   │   └── queries.py
│   ├── relational/         # PostgreSQL (config, users)
│   │   ├── models.py
│   │   └── migrations/
│   └── cache/              # Redis
│       ├── connection.py
│       └── pubsub.py
│
├── api/                    # API pública
│   ├── rest/               # Endpoints REST
│   ├── websocket/          # WebSocket para tiempo real
│   └── middleware/         # Auth, rate limiting
│
├── monitoring/             # Observabilidad
│   ├── metrics.py          # Métricas Prometheus
│   ├── logging.py          # Logs centralizados
│   └── health_checks.py    # Health checks
│
└── web/                    # Frontend (opcional)
    ├── dashboard/          # Alternativa/al complemento de Flet
    └── components/
```

---

## Componentes Principales

### 1. Gateway IoT (Edge)

| Componente | Función | Tecnología |
|------------|---------|------------|
| **MQTT Broker** | Recibir datos de sensores | Mosquitto / EMQX |
| **Protocol Adapter** | Soportar MQTT/CoAP/HTTP | Python paho-mqtt |
| **Edge Processor** | Filtrado básico en edge (opcional) | Node-RED / Python |

### 2. Capa de Ingesta

```python
# ingestion/mqtt_handler.py
import paho.mqtt.client as mqtt
import asyncio
from datetime import datetime

class IoTIngestionHandler:
    """
    Suscriptor MQTT para sensores IoT reales.
    Recibe datos y los encola para procesamiento.
    """
    
    def __init__(self, broker_host: str, topics: list):
        self.broker = broker_host
        self.topics = topics  # ["sensores/temperatura/+/datos", ...]
        self.client = mqtt.Client()
        self.buffer = []  # Buffer temporal
        
    def on_connect(self, client, userdata, flags, rc):
        """Suscripción a topics al conectar."""
        print(f"Conectado a MQTT broker: {rc}")
        for topic in self.topics:
            client.subscribe(topic, qos=1)  # QoS 1: Al menos una vez
    
    def on_message(self, client, userdata, msg):
        """
        Callback cuando llega mensaje de sensor.
        Ejemplo payload: {"sensor_id": "temp_01", "value": 25.5, "ts": 1234567890}
        """
        try:
            payload = json.loads(msg.payload.decode())
            
            # Enriquecer metadatos
            enriched = {
                "sensor_id": payload["sensor_id"],
                "value": payload["value"],
                "sensor_timestamp": payload["ts"],
                "received_at": datetime.utcnow().isoformat(),
                "topic": msg.topic,
                "qos": msg.qos
            }
            
            # Validar
            if self.validate(enriched):
                # Encolar para procesamiento async
                self.enqueue(enriched)
                
        except Exception as e:
            logger.error(f"Error procesando mensaje: {e}")
    
    def validate(self, data: dict) -> bool:
        """Validación de esquema."""
        required = ["sensor_id", "value", "sensor_timestamp"]
        return all(field in data for field in required)
    
    def enqueue(self, data: dict):
        """Agrega a buffer para procesamiento batch."""
        self.buffer.append(data)
        
        # Flush cuando buffer alcanza tamaño
        if len(self.buffer) >= 100:
            self.flush_buffer()
    
    def flush_buffer(self):
        """Envía buffer a procesamiento."""
        # Aquí iría a Kafka/RabbitMQ o directo a DB
        asyncio.create_task(process_batch(self.buffer.copy()))
        self.buffer.clear()
```

### 3. Base de Datos Timeseries

#### Opción 1: InfluxDB (Especializada IoT)
```sql
-- Bucket: artemus_park
-- Measurement: sensor_data
-- Tags: sensor_id, sensor_type, location
-- Fields: value, status
-- Timestamp: sensor_timestamp

-- Ejemplo query
SELECT mean("value") 
FROM "sensor_data" 
WHERE "sensor_type" = 'temperatura' 
  AND time > now() - 1h
GROUP BY time(5m), "sensor_id"
```

#### Opción 2: TimescaleDB (PostgreSQL + extensión)
```sql
-- Tabla híbrida SQL + timeseries
CREATE TABLE sensor_measurements (
    time TIMESTAMPTZ NOT NULL,
    sensor_id VARCHAR(50),
    sensor_type VARCHAR(20),
    value DOUBLE PRECISION,
    status VARCHAR(20)
);

-- Convertir a hypertable (particionamiento automático)
SELECT create_hypertable('sensor_measurements', 'time', chunk_time_interval => INTERVAL '1 day');

-- Índices optimizados
CREATE INDEX idx_sensor_time ON sensor_measurements(sensor_id, time DESC);
```

### 4. Motor de Alertas en Tiempo Real

```python
# processing/alert_engine.py
from datetime import datetime, timedelta
import asyncio

class RealTimeAlertEngine:
    """
    Evalúa alertas en tiempo real usando ventanas deslizantes.
    """
    
    def __init__(self):
        self.windows = {}  # Ventanas por sensor
        self.rules = {
            "temperatura": {"max": 35, "min": 5},
            "humedad": {"max": 90, "min": 10},
            "viento": {"max": 80}  # km/h
        }
    
    async def process_window(self, sensor_id: str, window_data: list):
        """
        Procesa ventana de 1 minuto de datos.
        """
        if not window_data:
            return
        
        # Calcular estadísticas
        values = [d["value"] for d in window_data]
        avg_val = sum(values) / len(values)
        max_val = max(values)
        min_val = min(values)
        
        sensor_type = sensor_id.split("_")[0]  # temp_01 -> temperatura
        
        # Evaluar reglas
        rule = self.rules.get(sensor_type, {})
        
        alerts = []
        if max_val > rule.get("max", float('inf')):
            alerts.append({
                "type": "CRITICAL",
                "message": f"{sensor_type} máximo excedido: {max_val}",
                "sensor_id": sensor_id,
                "timestamp": datetime.utcnow().isoformat()
            })
        
        # Emitir alertas
        for alert in alerts:
            await self.emit_alert(alert)
    
    async def emit_alert(self, alert: dict):
        """Envía alerta por WebSocket/email/SMS."""
        # WebSocket a dashboard
        await websocket_manager.broadcast(alert)
        
        # Persistir
        await save_alert_to_db(alert)
```

---

## Flujo de Datos

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  Sensor  │────▶│  MQTT    │────▶│  Stream  │────▶│  TS DB   │
│  IoT     │     │  Broker  │     │  Proc    │     │ (Influx) │
└──────────┘     └──────────┘     └────┬─────┘     └────┬─────┘
                                       │                │
                              ┌────────▼────────┐       │
                              │  Alert Engine   │       │
                              │  (Si umbral     │◄──────┘
                              │   excedido)     │
                              └────────┬────────┘
                                       │
                              ┌────────▼────────┐
                              │  WebSocket      │
                              │  Dashboard      │
                              │  (Tiempo real)  │
                              └─────────────────┘
```

### Latencias Esperadas
- Sensor → Broker: < 100ms
- Broker → Procesamiento: < 50ms
- Procesamiento → DB: < 20ms
- **Total: < 200ms** (perceptible como "tiempo real")

---

## Stack Tecnológico

### Opción 1: Simple (Recomendada para universidad)

| Capa | Tecnología |
|------|------------|
| **MQTT Broker** | Mosquitto |
| **Procesamiento** | Python asyncio |
| **Timeseries DB** | TimescaleDB (PostgreSQL) |
| **Cache/Sesiones** | Redis |
| **API** | FastAPI + WebSocket |
| **Frontend** | Flet (mantener) / Web |
| **Monitoreo** | Prometheus + Grafana |

### Opción 2: Escalable (Producción)

| Capa | Tecnología |
|------|------------|
| **MQTT Broker** | EMQX / HiveMQ |
| **Procesamiento** | Apache Kafka / Flink |
| **Timeseries DB** | InfluxDB |
| **Cache/Sesiones** | Redis Cluster |
| **API** | FastAPI + Socket.io |
| **Frontend** | React/Vue + WebSocket |
| **Monitoreo** | ELK Stack |

---

## Implementación

### Fase 1: Gateway e Ingesta (Semanas 1-2)
- Configurar Mosquitto MQTT Broker
- Implementar handler MQTT
- Validación de mensajes
- Buffer temporal

### Fase 2: Procesamiento y Storage (Semanas 3-4)
- Configurar TimescaleDB/InfluxDB
- Implementar stream processor
- Motor de alertas
- Workers async

### Fase 3: API y Dashboard (Semanas 5-6)
- API REST con FastAPI
- WebSocket para tiempo real
- Dashboard Flet/Web
- Sistema de notificaciones

### Fase 4: Testing y Monitoreo (Semanas 7-8)
- Pruebas de carga
- Latencia end-to-end
- Tolerancia a fallos
- Métricas y logs

---

## Entregables Académicos

### Memoria del Proyecto

```
1. INTRODUCCIÓN
   1.1 Contexto: Sistemas IoT en tiempo real
   1.2 Problema: Ingesta masiva de datos de sensores
   1.3 Solución: Arquitectura event-driven

2. MARCO TEÓRICO
   2.1 Protocolos IoT: MQTT, CoAP, HTTP
   2.2 Bases de datos timeseries
   2.3 Procesamiento de streams
   2.4 Patrón Pub/Sub

3. ANÁLISIS Y DISEÑO
   3.1 Requisitos funcionales (RF)
   3.2 Requisitos no funcionales (RNF): Latencia, throughput
   3.3 Arquitectura de software (C4 Model)
   3.4 Diagramas: Componentes, Despliegue, Secuencia

4. IMPLEMENTACIÓN
   4.1 Gateway IoT (Mosquitto)
   4.2 Handler MQTT (Python)
   4.3 Procesamiento async (Asyncio)
   4.4 Persistencia (TimescaleDB)
   4.5 Dashboard tiempo real (Flet + WebSocket)

5. PRUEBAS Y RESULTADOS
   5.1 Pruebas de carga (simular 100 sensores)
   5.2 Latencia end-to-end
   5.3 Throughput (eventos/segundo)
   5.4 Tolerancia a fallos

6. CONCLUSIONES
   6.1 Lecciones aprendidas sobre IoT
   6.2 Trabajo futuro: ML en edge, 5G, etc.
```

### Presentación
- Demo en vivo con sensores reales
- Métricas de performance
- Video de arquitectura

---

## Presupuesto Hardware (Demo)

| Componente | Especificación | Costo Estimado |
|------------|---------------|----------------|
| **Gateway IoT** | Raspberry Pi 4 + SD 64GB | €60 |
| **Sensores** | Kit ESP32 + DHT22 (temp/hum) x3 | €30 |
| **Servidor Cloud** | VPS 2CPU/4GB (DigitalOcean/AWS) | €20/mes |
| **Total** | | **~€110 inicial** |

---

## Decisiones Clave

### Flet vs Web

| Opción | Pros | Contras |
|--------|------|---------|
| **Mantener Flet** | Código existente, rápido de desarrollar | WebSocket limitado, menos flexible |
| **Añadir Web** | WebSocket nativo, mejor para tiempo real | Nuevo desarrollo, más complejo |

**Recomendación**: Añadir endpoint WebSocket a Flet (híbrido) o crear dashboard web paralelo.

### Asyncio vs Celery

| Opción | Cuándo usar |
|--------|-------------|
| **Asyncio** | < 1000 eventos/seg, simpler |
| **Celery + Redis** | > 1000 eventos/seg, necesita workers distribuidos |

**Recomendación**: Asyncio para proyecto universitario (suficiente).

---

## Resumen

### ¿Qué hay que hacer?
1. **Añadir Gateway IoT** (Mosquitto)
2. **Crear capa de ingesta** (handler MQTT)
3. **Migrar a Timeseries DB** (InfluxDB/TimescaleDB)
4. **Implementar procesamiento async** (asyncio)
5. **Añadir WebSocket** para tiempo real

### ¿Cuánto tiempo?
- **MVP funcional**: 4-6 semanas
- **Proyecto completo**: 8-10 semanas

### ¿Es viable para universidad?
✅ **Sí**, demuestra:
- Arquitectura distribuida
- Protocolos IoT (MQTT)
- Bases de datos timeseries
- Procesamiento en tiempo real
- Sistemas concurrentes

---

*Documento preparado para proyecto universitario de Ingeniería Informática*
