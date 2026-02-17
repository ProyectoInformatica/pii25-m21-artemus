# Arquitectura para Manejo de Asincronía y Concurrencia

## 1. PROBLEMAS A RESOLVER

```
┌─────────────────────────────────────────────────────────────────┐
│                    FUENTES DE DATOS                             │
├─────────────────────────────────────────────────────────────────┤
│  Sensores IoT    │   APIs Externas   │   Sistemas Legacy       │
│  - MQTT          │   - REST          │   - CSV imports         │
│  - WebSocket     │   - GraphQL       │   - Batch uploads       │
│  - HTTP POST     │   - Webhooks      │   - Manual entry        │
└─────────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────────┐
│                    DESAFIOS                                     │
├─────────────────────────────────────────────────────────────────┤
│  • Datos llegan desordenados (timestamp antiguo despues de nuevo)│
│  • Duplicacion de mensajes (red no confiable)                   │
│  • Escrituras simultaneas (race conditions)                     │
│  • Latencia variable (sensores en diferentes redes)             │
│  • Fallos parciales (algunos datos no llegan)                   │
│  • Consistencia eventual vs strong consistency                  │
└─────────────────────────────────────────────────────────────────┘
```

## 2. ARQUITECTURA PROPUESTA: EVENT-DRIVEN CON CQRS

```
┌────────────────────────────────────────────────────────────────────────┐
│                        CAPA DE INGESTA                                  │
├────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐        │
│   │ Sensor   │    │  API     │    │  File    │    │  Manual  │        │
│   │ MQTT     │    │  Gateway │    │  Upload  │    │  Entry   │        │
│   └────┬─────┘    └────┬─────┘    └────┬─────┘    └────┬─────┘        │
│        │               │               │               │               │
│        └───────────────┴───────────────┴───────────────┘               │
│                        │                                                │
│                        ▼                                                │
│   ┌─────────────────────────────────────────────────────────────┐     │
│   │              MESSAGE QUEUE (RabbitMQ/Kafka)                  │     │
│   │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │     │
│   │  │ sensor.raw   │  │ sensor.high  │  │ dlq.errors   │       │     │
│   │  │ (todos)      │  │ (prioridad)  │  │ (fallos)     │       │     │
│   │  └──────────────┘  └──────────────┘  └──────────────┘       │     │
│   └─────────────────────────────────────────────────────────────┘     │
│                        │                                                │
└────────────────────────┼────────────────────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────────────────┐
│                      CAPA DE PROCESAMIENTO                              │
├────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   ┌─────────────────────────────────────────────────────────────┐     │
│   │              STREAM PROCESSOR (Kafka Streams/Flink)          │     │
│   │                                                              │     │
│   │  • Ordenamiento por timestamp (windowing)                   │     │
│   │  • Deduplicacion por ID + timestamp                         │     │
│   │  • Validacion de esquema                                    │     │
│   │  • Enriquecimiento de datos (metadatos)                     │     │
│   │  • Agregaciones en tiempo real (avg, max, min)              │     │
│   │                                                              │     │
│   │  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │     │
│   │  │ 5min window │───▶│ 1hour window│───▶│ 1day window │     │     │
│   │  └─────────────┘    └─────────────┘    └─────────────┘     │     │
│   └─────────────────────────────────────────────────────────────┘     │
│                        │                                                │
└────────────────────────┼────────────────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  WRITE DB    │  │  READ DB     │  │  CACHE       │
│  (OLTP)      │  │  (OLAP)      │  │  (Redis)     │
│              │  │              │  │              │
│  PostgreSQL  │  │  ClickHouse  │  │  Sessions    │
│  - Raw data  │  │  - Analytics │  │  - Hot data  │
│  - ACID      │  │  - Aggregates│  │  - Pub/Sub   │
└──────────────┘  └──────────────┘  └──────────────┘
```

## 3. IMPLEMENTACION TECNICA

### 3.1 Esquema de Base de Datos Mejorado

```sql
-- Tabla de eventos crudos (append-only)
CREATE TABLE sensor_events (
    event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sensor_id VARCHAR(50) NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    
    -- Timestamps criticos
    sensor_timestamp TIMESTAMP NOT NULL,  -- Cuando el sensor midio
    received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Cuando llego al server
    processed_at TIMESTAMP,  -- Cuando se proceso
    
    -- Datos del payload
    payload JSONB NOT NULL,
    payload_hash VARCHAR(64),  -- Para deduplicacion
    
    -- Metadata
    source_ip INET,
    protocol VARCHAR(20),  -- 'mqtt', 'http', 'ws'
    
    -- Estado de procesamiento
    status VARCHAR(20) DEFAULT 'pending',  -- pending, processing, completed, error
    retry_count INT DEFAULT 0,
    error_message TEXT,
    
    -- Control de concurrencia
    processing_lock UUID,
    locked_at TIMESTAMP,
    
    -- Optimizacion
    batch_id UUID,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) PARTITION BY RANGE (sensor_timestamp);

-- Indices clave para performance
CREATE INDEX idx_events_sensor_time ON sensor_events(sensor_id, sensor_timestamp DESC);
CREATE INDEX idx_events_status ON sensor_events(status) WHERE status IN ('pending', 'error');
CREATE INDEX idx_events_payload_hash ON sensor_events(payload_hash);
CREATE INDEX idx_events_batch ON sensor_events(batch_id);
CREATE INDEX idx_events_received ON sensor_events(received_at DESC);

-- Vista materializada para deduplicacion
CREATE MATERIALIZED VIEW sensor_events_dedup AS
SELECT DISTINCT ON (sensor_id, sensor_timestamp, payload_hash)
    event_id,
    sensor_id,
    sensor_timestamp,
    payload,
    received_at
FROM sensor_events
WHERE status = 'completed'
ORDER BY sensor_id, sensor_timestamp, payload_hash, received_at ASC;

-- Refrescar cada 5 minutos
CREATE INDEX idx_mv_dedup ON sensor_events_dedup(sensor_id, sensor_timestamp);
```

### 3.2 Sistema de Colas con Prioridad

```python
# ArtemusPark/messaging/event_queue.py

import json
import hashlib
from datetime import datetime
from typing import Dict, Any, Optional
import pika
from redis import Redis
import logging

logger = logging.getLogger(__name__)

class EventPriority:
    """Prioridades de eventos."""
    CRITICAL = 10  # Emergencias (humo, fuego)
    HIGH = 20      # Alertas importantes
    NORMAL = 30    # Datos regulares
    LOW = 40       # Logs, estadisticas
    BATCH = 50     # Procesamiento batch

class SensorEventQueue:
    """
    Cola de eventos con soporte para:
    - Priorizacion
    - Deduplicacion
    - Retry con backoff exponencial
    - Dead Letter Queue (DLQ)
    """
    
    def __init__(self, rabbitmq_url: str, redis_url: str):
        self.rabbitmq_url = rabbitmq_url
        self.redis = Redis.from_url(redis_url, decode_responses=True)
        self.connection = None
        self.channel = None
        self._connect()
    
    def _connect(self):
        """Establece conexion con RabbitMQ."""
        params = pika.URLParameters(self.rabbitmq_url)
        params.heartbeat = 600
        params.blocked_connection_timeout = 300
        
        self.connection = pika.BlockingConnection(params)
        self.channel = self.connection.channel()
        
        # Declarar exchanges y colas
        self._setup_topology()
    
    def _setup_topology(self):
        """Configura la topologia de colas."""
        # Exchange principal (topic routing)
        self.channel.exchange_declare(
            exchange='sensors.topic',
            exchange_type='topic',
            durable=True
        )
        
        # Exchange para dead letters
        self.channel.exchange_declare(
            exchange='sensors.dlx',
            exchange_type='topic',
            durable=True
        )
        
        # Colas por prioridad
        queues = [
            ('sensors.critical', EventPriority.CRITICAL),
            ('sensors.high', EventPriority.HIGH),
            ('sensors.normal', EventPriority.NORMAL),
            ('sensors.low', EventPriority.LOW),
            ('sensors.batch', EventPriority.BATCH),
        ]
        
        for queue_name, priority in queues:
            # Cola principal con max-priority
            self.channel.queue_declare(
                queue=queue_name,
                durable=True,
                arguments={
                    'x-max-priority': 50,
                    'x-dead-letter-exchange': 'sensors.dlx',
                    'x-dead-letter-routing-key': f'{queue_name}.failed'
                }
            )
            
            # Binding
            routing_key = f'sensor.{queue_name.split(".")[1]}'
            self.channel.queue_bind(
                exchange='sensors.topic',
                queue=queue_name,
                routing_key=routing_key
            )
            
            # Cola de dead letters para esta prioridad
            dlq_name = f'{queue_name}.dlq'
            self.channel.queue_declare(queue=dlq_name, durable=True)
            self.channel.queue_bind(
                exchange='sensors.dlx',
                queue=dlq_name,
                routing_key=f'{queue_name}.failed'
            )
    
    def publish_event(self, event: Dict[str, Any], priority: int = EventPriority.NORMAL) -> bool:
        """
        Publica un evento con deduplicacion.
        
        Args:
            event: Datos del evento
            priority: Nivel de prioridad
            
        Returns:
            bool: True si se publico, False si es duplicado
        """
        try:
            # Generar hash para deduplicacion
            event_hash = self._calculate_hash(event)
            dedup_key = f"dedup:{event['sensor_id']}:{event_hash}"
            
            # Verificar si ya existe (ventana de 5 minutos)
            if self.redis.set(dedup_key, "1", nx=True, ex=300):
                # No existe, podemos procesar
                
                # Determinar cola segun prioridad
                queue_name = self._get_queue_by_priority(priority)
                
                # Enriquecer evento
                enriched_event = {
                    **event,
                    'event_hash': event_hash,
                    'published_at': datetime.utcnow().isoformat(),
                    'priority': priority,
                    'retry_count': 0
                }
                
                # Publicar
                self.channel.basic_publish(
                    exchange='sensors.topic',
                    routing_key=f'sensor.{queue_name.split(".")[1]}',
                    body=json.dumps(enriched_event).encode(),
                    properties=pika.BasicProperties(
                        delivery_mode=2,  # Persistente
                        priority=priority,
                        content_type='application/json',
                        message_id=event_hash
                    )
                )
                
                logger.info(f"Evento publicado: {event['sensor_id']} con prioridad {priority}")
                return True
            else:
                logger.warning(f"Evento duplicado detectado: {event['sensor_id']}")
                return False
                
        except Exception as e:
            logger.error(f"Error publicando evento: {e}")
            raise
    
    def _calculate_hash(self, event: Dict[str, Any]) -> str:
        """Calcula hash del evento para deduplicacion."""
        # Incluir campos que identifican unicamente la medicion
        hash_data = f"{event['sensor_id']}:{event['timestamp']}:{event.get('value')}"
        return hashlib.sha256(hash_data.encode()).hexdigest()[:16]
    
    def _get_queue_by_priority(self, priority: int) -> str:
        """Mapea prioridad a nombre de cola."""
        if priority <= EventPriority.CRITICAL:
            return 'sensors.critical'
        elif priority <= EventPriority.HIGH:
            return 'sensors.high'
        elif priority <= EventPriority.NORMAL:
            return 'sensors.normal'
        elif priority <= EventPriority.LOW:
            return 'sensors.low'
        else:
            return 'sensors.batch'
    
    def consume_events(self, queue_name: str, callback, prefetch_count: int = 10):
        """
        Consume eventos de una cola.
        
        Args:
            queue_name: Nombre de la cola
            callback: Funcion callback(ch, method, properties, body)
            prefetch_count: Numero de mensajes a prefetch
        """
        self.channel.basic_qos(prefetch_count=prefetch_count)
        
        self.channel.basic_consume(
            queue=queue_name,
            on_message_callback=callback,
            auto_ack=False  # Ack manual para garantizar procesamiento
        )
        
        logger.info(f"Consumiendo de {queue_name}...")
        self.channel.start_consuming()
    
    def acknowledge(self, delivery_tag: int):
        """Confirma procesamiento exitoso."""
        self.channel.basic_ack(delivery_tag=delivery_tag)
    
    def reject_with_retry(self, delivery_tag: int, event: Dict[str, Any], error: str):
        """
        Rechaza mensaje con reintento.
        Si excede max retries, va a DLQ.
        """
        retry_count = event.get('retry_count', 0)
        max_retries = 3
        
        if retry_count < max_retries:
            # Re-publicar con delay (usando plugin delayed-message o Redis)
            event['retry_count'] = retry_count + 1
            event['last_error'] = error
            event['retry_at'] = datetime.utcnow().isoformat()
            
            # Calcular delay exponencial: 2^retry_count segundos
            delay_seconds = 2 ** retry_count
            
            # Usar cola delayed o re-publicar directamente
            self.channel.basic_publish(
                exchange='sensors.topic',
                routing_key=f'sensor.{self._get_queue_by_priority(event["priority"]).split(".")[1]}',
                body=json.dumps(event).encode(),
                properties=pika.BasicProperties(
                    delivery_mode=2,
                    priority=event['priority'],
                    expiration=str(delay_seconds * 1000)  # ms
                )
            )
            
            self.channel.basic_ack(delivery_tag=delivery_tag)
            logger.info(f"Evento reencolado para retry {retry_count + 1}/{max_retries}")
        else:
            # Max retries alcanzado, rechazar (ira a DLQ)
            self.channel.basic_reject(delivery_tag=delivery_tag, requeue=False)
            logger.error(f"Evento rechazado a DLQ despues de {max_retries} intentos")
    
    def close(self):
        """Cierra conexiones."""
        if self.connection and not self.connection.is_closed:
            self.connection.close()
```

### 3.3 Procesador de Eventos con Ordenamiento

```python
# ArtemusPark/processing/event_processor.py

import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from collections import defaultdict
import heapq
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)

@dataclass(order=True)
class TimedEvent:
    """Evento ordenable por timestamp."""
    sensor_timestamp: datetime = field(compare=True)
    received_at: datetime = field(compare=False)
    event_data: Dict[str, Any] = field(compare=False)
    event_id: str = field(compare=False)

class EventWindowProcessor:
    """
    Procesa eventos en ventanas de tiempo con ordenamiento.
    Implementa el patron "Event Time Processing".
    """
    
    def __init__(self, window_size_seconds: int = 60, allowed_lateness_seconds: int = 30):
        self.window_size = timedelta(seconds=window_size_seconds)
        self.allowed_lateness = timedelta(seconds=allowed_lateness_seconds)
        
        # Buffer de eventos por ventana
        self.windows: Dict[datetime, List[TimedEvent]] = defaultdict(list)
        self.event_heap: List[TimedEvent] = []
        
        # Watermark: el timestamp mas alto que hemos visto menos el lateness
        self.current_watermark: Optional[datetime] = None
        
        # Locks para concurrencia
        self._lock = asyncio.Lock()
    
    async def add_event(self, event: Dict[str, Any]) -> bool:
        """
        Agrega evento al buffer.
        
        Returns:
            bool: True si se acepto, False si es muy viejo (despues de watermark)
        """
        sensor_ts = datetime.fromisoformat(event['sensor_timestamp'].replace('Z', '+00:00'))
        received_ts = datetime.utcnow()
        
        timed_event = TimedEvent(
            sensor_timestamp=sensor_ts,
            received_at=received_ts,
            event_data=event,
            event_id=event.get('event_id', str(hash(str(event))))
        )
        
        async with self._lock:
            # Actualizar watermark si es necesario
            if self.current_watermark is None or sensor_ts > self.current_watermark:
                self.current_watermark = sensor_ts
            
            # Verificar si el evento es demasiado viejo
            if self.current_watermark - sensor_ts > self.allowed_lateness:
                logger.warning(f"Evento {timed_event.event_id} descartado por tardio. "
                             f"Watermark: {self.current_watermark}, Evento: {sensor_ts}")
                return False
            
            # Agregar al heap (ordena automaticamente)
            heapq.heappush(self.event_heap, timed_event)
            
            # Calcular ventana
            window_start = self._get_window_start(sensor_ts)
            self.windows[window_start].append(timed_event)
            
            logger.debug(f"Evento agregado: {timed_event.event_id} en ventana {window_start}")
            return True
    
    def _get_window_start(self, timestamp: datetime) -> datetime:
        """Calcula el inicio de la ventana para un timestamp."""
        seconds = timestamp.second + timestamp.microsecond / 1_000_000
        window_seconds = (seconds // self.window_size.total_seconds()) * self.window_size.total_seconds()
        return timestamp.replace(second=int(window_seconds), microsecond=0)
    
    async def process_ready_windows(self) -> List[List[Dict[str, Any]]]:
        """
        Procesa ventanas que han pasado el watermark.
        
        Returns:
            Lista de ventanas procesadas, cada una con sus eventos ordenados
        """
        async with self._lock:
            if not self.current_watermark:
                return []
            
            ready_windows = []
            windows_to_remove = []
            
            for window_start, events in self.windows.items():
                # Una ventana esta lista si su fin es menor que el watermark
                window_end = window_start + self.window_size
                
                if window_end <= self.current_watermark - self.allowed_lateness:
                    # Ordenar eventos por timestamp del sensor
                    sorted_events = sorted(events, key=lambda e: e.sensor_timestamp)
                    
                    ready_windows.append({
                        'window_start': window_start,
                        'window_end': window_end,
                        'events': [e.event_data for e in sorted_events],
                        'event_count': len(sorted_events)
                    })
                    
                    windows_to_remove.append(window_start)
                    
                    logger.info(f"Ventana {window_start} procesada con {len(events)} eventos")
            
            # Limpiar ventanas procesadas
            for ws in windows_to_remove:
                del self.windows[ws]
            
            return ready_windows
    
    async def get_ordered_events(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Obtiene eventos ordenados por timestamp del sensor.
        
        Args:
            limit: Maximo numero de eventos a retornar
            
        Returns:
            Lista de eventos ordenados
        """
        async with self._lock:
            # Extraer del heap sin remover
            events = heapq.nsmallest(limit, self.event_heap)
            return [e.event_data for e in events]


class AsyncEventProcessor:
    """
    Procesador asincrono de eventos con:
    - Batch processing
    - Retry con backoff
    - Circuit breaker
    """
    
    def __init__(self, db_connection, batch_size: int = 100, flush_interval: int = 5):
        self.db = db_connection
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        
        self.buffer: List[Dict[str, Any]] = []
        self.buffer_lock = asyncio.Lock()
        
        # Circuit breaker
        self.failure_count = 0
        self.failure_threshold = 5
        self.circuit_open = False
        self.last_failure_time: Optional[datetime] = None
        
        # Estadisticas
        self.processed_count = 0
        self.error_count = 0
    
    async def start(self):
        """Inicia el procesador."""
        asyncio.create_task(self._flush_loop())
        asyncio.create_task(self._circuit_monitor())
    
    async def process_event(self, event: Dict[str, Any]) -> bool:
        """
        Procesa un evento individual.
        
        Returns:
            bool: True si se proceso exitosamente
        """
        if self.circuit_open:
            logger.warning("Circuit breaker abierto, evento rechazado")
            return False
        
        try:
            async with self.buffer_lock:
                self.buffer.append(event)
                
                # Flush inmediato si alcanzamos batch_size
                if len(self.buffer) >= self.batch_size:
                    await self._flush_buffer()
            
            return True
            
        except Exception as e:
            logger.error(f"Error procesando evento: {e}")
            self._record_failure()
            return False
    
    async def _flush_loop(self):
        """Loop que hace flush periodico del buffer."""
        while True:
            await asyncio.sleep(self.flush_interval)
            
            async with self.buffer_lock:
                if self.buffer:
                    await self._flush_buffer()
    
    async def _flush_buffer(self):
        """Escribe el buffer a la base de datos."""
        if not self.buffer:
            return
        
        events_to_flush = self.buffer.copy()
        self.buffer.clear()
        
        try:
            # Insertar en batch
            await self._batch_insert(events_to_flush)
            
            self.processed_count += len(events_to_flush)
            self.failure_count = 0  # Resetear contador de fallos
            
            logger.info(f"Batch de {len(events_to_flush)} eventos insertado")
            
        except Exception as e:
            logger.error(f"Error en batch insert: {e}")
            
            # Re-agregar al buffer para retry
            self.buffer.extend(events_to_flush)
            self._record_failure()
            
            # Si el buffer crece demasiado, descartar eventos mas viejos
            if len(self.buffer) > self.batch_size * 3:
                discarded = self.buffer[:-self.batch_size * 2]
                self.buffer = self.buffer[-self.batch_size * 2:]
                logger.error(f"Descartados {len(discarded)} eventos por buffer lleno")
    
    async def _batch_insert(self, events: List[Dict[str, Any]]):
        """Inserta eventos en batch."""
        # Implementar con COPY de PostgreSQL para mejor performance
        query = """
            INSERT INTO sensor_events 
            (sensor_id, event_type, sensor_timestamp, payload, payload_hash, source_ip, protocol, status)
            VALUES ($1, $2, $3, $4, $5, $6, $7, 'completed')
            ON CONFLICT (sensor_id, sensor_timestamp, payload_hash) DO NOTHING
        """
        
        # Usar asyncpg para operaciones async
        async with self.db.acquire() as conn:
            await conn.executemany(query, [
                (
                    e['sensor_id'],
                    e.get('event_type', 'measurement'),
                    e['sensor_timestamp'],
                    json.dumps(e.get('payload', e)),
                    e.get('event_hash', ''),
                    e.get('source_ip'),
                    e.get('protocol', 'unknown')
                )
                for e in events
            ])
    
    def _record_failure(self):
        """Registra un fallo para el circuit breaker."""
        self.failure_count += 1
        self.error_count += 1
        self.last_failure_time = datetime.utcnow()
        
        if self.failure_count >= self.failure_threshold:
            self.circuit_open = True
            logger.error(f"Circuit breaker ABIERTO despues de {self.failure_count} fallos")
    
    async def _circuit_monitor(self):
        """Monitorea y cierra el circuit breaker."""
        while True:
            await asyncio.sleep(30)
            
            if self.circuit_open:
                # Intentar cerrar despues de 60 segundos
                if (datetime.utcnow() - self.last_failure_time).seconds > 60:
                    self.circuit_open = False
                    self.failure_count = 0
                    logger.info("Circuit breaker CERRADO")
```

### 3.4 API Gateway con Rate Limiting

```python
# ArtemusPark/api/gateway.py

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import redis.asyncio as redis
from datetime import datetime
import jwt
import logging

logger = logging.getLogger(__name__)

# Rate limiting con Redis
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Artemus Park Sensor API")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Redis para rate limiting y cache
redis_client = redis.from_url("redis://localhost:6379/0")

@app.post("/sensors/data")
@limiter.limit("100/minute")  # Rate limit por IP
async def receive_sensor_data(
    request: Request,
    data: SensorData,
    auth: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Recibe datos de sensores con:
    - Rate limiting
    - Autenticacion
    - Validacion
    - Encolamiento
    """
    try:
        # Verificar token
        payload = jwt.decode(auth.credentials, SECRET_KEY, algorithms=["HS256"])
        sensor_id = payload.get("sensor_id")
        
        # Validar que el sensor existe
        if not await validate_sensor(sensor_id):
            raise HTTPException(status_code=403, detail="Sensor no autorizado")
        
        # Enriquecer datos
        enriched_data = {
            **data.dict(),
            "sensor_id": sensor_id,
            "received_at": datetime.utcnow().isoformat(),
            "source_ip": request.client.host,
            "protocol": "http"
        }
        
        # Determinar prioridad
        priority = determine_priority(data)
        
        # Publicar a cola
        event_queue = SensorEventQueue()
        published = await event_queue.publish_event(enriched_data, priority)
        
        if published:
            return {"status": "accepted", "event_id": enriched_data.get("event_hash")}
        else:
            return {"status": "duplicate", "message": "Evento ya existe"}
            
    except Exception as e:
        logger.error(f"Error procesando datos: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/sensors/{sensor_id}")
async def websocket_endpoint(websocket: WebSocket, sensor_id: str):
    """
    WebSocket para sensores que necesitan conexion persistente.
    """
    await websocket.accept()
    
    try:
        while True:
            # Recibir datos
            data = await websocket.receive_json()
            
            # Validar
            if data.get("sensor_id") != sensor_id:
                await websocket.send_json({"error": "Sensor ID mismatch"})
                continue
            
            # Procesar
            enriched_data = {
                **data,
                "received_at": datetime.utcnow().isoformat(),
                "protocol": "websocket"
            }
            
            # Publicar
            await event_queue.publish_event(enriched_data, EventPriority.NORMAL)
            
            # Confirmar recepcion
            await websocket.send_json({"status": "received", "timestamp": datetime.utcnow().isoformat()})
            
    except Exception as e:
        logger.error(f"Error en WebSocket: {e}")
        await websocket.close()
```

## 4. ESTRATEGIAS DE CONCURRENCIA

### 4.1 Optimistic Locking

```sql
-- Agregar version a las tablas
ALTER TABLE sensor_measurements ADD COLUMN version INTEGER DEFAULT 0;

-- Actualizar con verificacion de version
UPDATE sensor_measurements 
SET value_numeric = $1, status = $2, version = version + 1
WHERE id = $3 AND version = $4;

-- Verificar si se actualizo
IF NOT FOUND THEN
    RAISE EXCEPTION 'Conflicto de concurrencia: el registro fue modificado';
END IF;
```

### 4.2 Idempotency Keys

```python
class IdempotencyHandler:
    """Maneja claves de idempotencia para evitar duplicados."""
    
    def __init__(self, redis_client):
        self.redis = redis_client
    
    async def check_or_store(self, idempotency_key: str, ttl: int = 86400) -> bool:
        """
        Verifica si la clave existe.
        Si no existe, la almacena y retorna True.
        Si existe, retorna False.
        """
        # Intentar setear solo si no existe (NX)
        result = await self.redis.set(
            f"idempotency:{idempotency_key}",
            datetime.utcnow().isoformat(),
            nx=True,
            ex=ttl
        )
        return result is not None
```

## 5. MONITOREO Y OBSERVABILIDAD

```python
# Métricas clave a monitorear
METRICS = {
    'events_received_total': 'Contador total de eventos recibidos',
    'events_processed_total': 'Contador de eventos procesados exitosamente',
    'events_duplicates_total': 'Contador de eventos duplicados detectados',
    'events_errors_total': 'Contador de errores de procesamiento',
    'events_lag_seconds': 'Lag entre sensor_timestamp y processed_at',
    'queue_depth': 'Profundidad de la cola',
    'processing_duration_seconds': 'Histograma de tiempo de procesamiento',
    'circuit_breaker_state': 'Estado del circuit breaker (0=closed, 1=open)'
}
```

## 6. RECOMENDACION DE ARQUITECTURA

Para **Artemus Park**, te recomiendo esta arquitectura hibrida:

```
FASE 1 (Inmediata):
├── PostgreSQL con tabla de eventos (append-only)
├── Redis para deduplicacion y cache
└── Procesamiento sincrono con batch insert

FASE 2 (Escalamiento):
├── RabbitMQ para colas con prioridad
├── Workers asincronos para procesamiento
├── PostgreSQL particionado
└── Redis Streams para persistencia temporal

FASE 3 (Alta escala):
├── Apache Kafka para ingestion masiva
├── Kafka Streams para procesamiento en tiempo real
├── ClickHouse para analytics
└── Arquitectura CQRS completa
```

**Beneficios de esta aproximacion:**
- ✅ Maneja desorden de eventos (windowing)
- ✅ Deduplicacion automatica
- ✅ Tolerancia a fallos (retry, DLQ)
- ✅ Escalable horizontalmente
- ✅ Observable y monitoreable
- ✅ Mantiene consistencia eventual configurable
