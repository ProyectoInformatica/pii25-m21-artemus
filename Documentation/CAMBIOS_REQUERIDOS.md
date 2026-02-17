# Cambios Requeridos en la Arquitectura - Artemus Park

## Resumen de Cambios Necesarios

Para soportar el flujo completo **IoT → Base de Datos → UI con operaciones CRUD**, estos son los cambios requeridos en la estructura actual:

---

## 1. CAMBIOS ESTRUCTURALES

### Antes (Actual)
```
ArtemusPark/
├── config/
├── model/           # Solo entidades
├── controller/      # Controladores de sensores
├── repository/      # JSON files
├── service/         # Solo Wind/Smoke risk
├── view/            # UI Flet
└── json/            # ❌ ELIMINAR
```

### Después (Propuesto)
```
ArtemusPark/
├── config/                    # ✅ Mantener
├── core/                      # 🆕 NUEVO: Utilidades base
│   ├── exceptions.py
│   ├── validators.py
│   └── constants.py
├── domain/                    # 🆕 NUEVO: Lógica de negocio pura
│   ├── models/               # ✅ Mover de /model
│   ├── repositories/         # 🆕 Interfaces (contratos)
│   └── services/             # 🆕 Lógica de negocio
├── infrastructure/            # 🆕 NUEVO: Implementaciones técnicas
│   ├── database/
│   │   ├── connection.py
│   │   ├── migrations/
│   │   └── repositories/     # ✅ Implementaciones SQL
│   ├── mqtt/                 # 🆕 Handler MQTT
│   │   ├── client.py
│   │   └── subscriber.py
│   └── cache/
│       └── redis_client.py
├── application/               # 🆕 NUEVO: Casos de uso
│   ├── dto/                  # Data Transfer Objects
│   ├── use_cases/            # Operaciones CRUD
│   └── mappers/              # Conversores
├── presentation/              # 🆕 NUEVO: Capa de presentación
│   ├── controllers/          # Controladores UI
│   ├── views/                # ✅ Mover de /view
│   └── viewmodels/           # 🆕 Lógica de vista
└── tests/
    ├── unit/
    ├── integration/
    └── e2e/
```

---

## 2. COMPONENTES QUE HAY QUE AÑADIR

### A. Capa de Infraestructura (infrastructure/)

**database/connection.py** - Conexión a PostgreSQL:
```python
import asyncpg
from contextlib import asynccontextmanager

class DatabaseConnection:
    """Gestor de conexiones a PostgreSQL."""
    
    def __init__(self, dsn: str):
        self.dsn = dsn
        self.pool = None
    
    async def connect(self):
        self.pool = await asyncpg.create_pool(self.dsn)
    
    @asynccontextmanager
    async def acquire(self):
        async with self.pool.acquire() as conn:
            yield conn
```

**mqtt/subscriber.py** - Suscripción a topics MQTT:
```python
import paho.mqtt.client as mqtt
import asyncio
import json

class MQTTSubscriber:
    """Suscriptor MQTT para recibir datos de sensores."""
    
    def __init__(self, broker: str, topics: list, message_handler):
        self.broker = broker
        self.topics = topics
        self.handler = message_handler
        self.client = mqtt.Client()
        
    def on_message(self, client, userdata, msg):
        """Callback cuando llega mensaje."""
        try:
            payload = json.loads(msg.payload.decode())
            # Enviar a handler asíncrono
            asyncio.create_task(self.handler(payload))
        except Exception as e:
            logger.error(f"Error procesando mensaje MQTT: {e}")
    
    def start(self):
        self.client.on_message = self.on_message
        self.client.connect(self.broker)
        for topic in self.topics:
            self.client.subscribe(topic, qos=1)
        self.client.loop_start()
```

### B. Capa de Dominio (domain/)

**repositories/sensor_repository.py** - Interfaz (contrato):
```python
from abc import ABC, abstractmethod
from typing import List, Optional
from domain.models.sensor import SensorReading

class SensorRepository(ABC):
    """Contrato para repositorio de sensores."""
    
    @abstractmethod
    async def save(self, reading: SensorReading) -> str:
        """Guarda una lectura. Retorna ID."""
        pass
    
    @abstractmethod
    async def get_by_id(self, reading_id: str) -> Optional[SensorReading]:
        """Obtiene lectura por ID."""
        pass
    
    @abstractmethod
    async def get_by_sensor(
        self, 
        sensor_id: str, 
        start_time: datetime, 
        end_time: datetime
    ) -> List[SensorReading]:
        """Obtiene lecturas de un sensor en rango de tiempo."""
        pass
    
    @abstractmethod
    async def update(self, reading_id: str, data: dict) -> bool:
        """Actualiza una lectura."""
        pass
    
    @abstractmethod
    async def delete(self, reading_id: str) -> bool:
        """Elimina una lectura."""
        pass
```

**services/sensor_service.py** - Lógica de negocio:
```python
class SensorService:
    """Servicio de dominio para operaciones con sensores."""
    
    def __init__(self, repository: SensorRepository):
        self.repo = repository
    
    async def process_reading(self, data: dict) -> SensorReading:
        """Procesa una lectura entrante (validación + transformación)."""
        # Validar datos
        if not self._validate(data):
            raise InvalidReadingError("Datos inválidos")
        
        # Crear entidad
        reading = SensorReading(
            sensor_id=data['sensor_id'],
            value=data['value'],
            timestamp=datetime.fromtimestamp(data['timestamp']),
            status=self._calculate_status(data['value'], data['sensor_id'])
        )
        
        # Persistir
        reading.id = await self.repo.save(reading)
        return reading
    
    async def get_sensor_history(
        self, 
        sensor_id: str,
        hours: int = 24
    ) -> List[SensorReading]:
        """Obtiene historial de un sensor."""
        end = datetime.now()
        start = end - timedelta(hours=hours)
        return await self.repo.get_by_sensor(sensor_id, start, end)
    
    async def correct_reading(self, reading_id: str, new_value: float):
        """Corrige una lectura errónea."""
        reading = await self.repo.get_by_id(reading_id)
        if not reading:
            raise NotFoundError("Lectura no encontrada")
        
        reading.value = new_value
        reading.is_corrected = True
        reading.corrected_at = datetime.now()
        
        await self.repo.update(reading_id, {
            'value': new_value,
            'is_corrected': True,
            'corrected_at': datetime.now()
        })
```

### C. Capa de Aplicación (application/)

**use_cases/sensor_use_cases.py** - Casos de uso:
```python
class ReceiveSensorDataUseCase:
    """Caso de uso: Recibir datos de sensor."""
    
    def __init__(self, sensor_service: SensorService):
        self.service = sensor_service
    
    async def execute(self, raw_data: dict) -> SensorDTO:
        """Ejecuta el caso de uso."""
        reading = await self.service.process_reading(raw_data)
        return SensorMapper.to_dto(reading)

class GetSensorHistoryUseCase:
    """Caso de uso: Obtener historial."""
    
    def __init__(self, sensor_service: SensorService):
        self.service = sensor_service
    
    async def execute(self, sensor_id: str, hours: int = 24) -> List[SensorDTO]:
        readings = await self.service.get_sensor_history(sensor_id, hours)
        return [SensorMapper.to_dto(r) for r in readings]

class UpdateSensorReadingUseCase:
    """Caso de uso: Actualizar lectura (operación CRUD)."""
    
    def __init__(self, sensor_service: SensorService):
        self.service = sensor_service
    
    async def execute(self, reading_id: str, new_data: UpdateReadingDTO):
        # Validar permisos aquí si es necesario
        await self.service.correct_reading(reading_id, new_data.value)
        return {"status": "updated", "id": reading_id}
```

### D. Capa de Presentación (presentation/)

**controllers/dashboard_controller.py**:
```python
class DashboardController:
    """Controlador para el dashboard."""
    
    def __init__(
        self,
        receive_use_case: ReceiveSensorDataUseCase,
        history_use_case: GetSensorHistoryUseCase,
        update_use_case: UpdateSensorReadingUseCase
    ):
        self.receive_uc = receive_use_case
        self.history_uc = history_use_case
        self.update_uc = update_use_case
        self.view_model = DashboardViewModel()
    
    async def on_sensor_data_received(self, raw_data: dict):
        """Callback cuando llegan datos del sensor."""
        try:
            # Guardar en BD
            dto = await self.receive_uc.execute(raw_data)
            
            # Actualizar UI
            self.view_model.add_reading(dto)
            self.view_model.notify_update()
            
        except Exception as e:
            self.view_model.show_error(str(e))
    
    async def load_sensor_history(self, sensor_id: str):
        """Cargar historial para mostrar en gráfico."""
        readings = await self.history_uc.execute(sensor_id, hours=24)
        self.view_model.set_history(readings)
    
    async def on_user_corrects_reading(self, reading_id: str, new_value: float):
        """Usuario corrige una lectura."""
        try:
            await self.update_uc.execute(
                reading_id, 
                UpdateReadingDTO(value=new_value)
            )
            self.view_model.show_success("Lectura actualizada")
            
            # Refrescar datos
            await self.load_sensor_history(
                self.view_model.selected_sensor_id
            )
        except Exception as e:
            self.view_model.show_error(str(e))
```

---

## 3. COMPONENTES QUE HAY QUE MODIFICAR

### A. Modelos Actuales

**Antes:**
```python
@dataclass
class TemperatureModel:
    value: int
    status: str
    sensor_id: str
    timestamp: float
```

**Después:**
```python
@dataclass
class SensorReading:
    """Entidad de dominio completa."""
    id: Optional[str] = None
    sensor_id: str = ""
    sensor_type: str = ""  # temperature, humidity, etc.
    value: float = 0.0
    unit: str = ""  # celsius, percent, kmh
    timestamp: datetime = field(default_factory=datetime.now)
    status: str = "normal"  # normal, warning, critical
    
    # Campos para auditoría/CRUD
    is_corrected: bool = False
    corrected_at: Optional[datetime] = None
    corrected_by: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    
    def correct(self, new_value: float, user_id: str):
        """Método de dominio para corrección."""
        self.value = new_value
        self.is_corrected = True
        self.corrected_at = datetime.now()
        self.corrected_by = user_id
```

### B. Vistas Flet (Views)

**Antes:** Solo lectura de datos simulados

**Después:** Interacción completa
```python
class SensorDashboardView:
    """Vista con capacidades CRUD."""
    
    def __init__(self, controller: DashboardController):
        self.controller = controller
        self.readings_table = None
        self.chart = None
        
    def build(self):
        return ft.Column([
            # Panel de sensores en tiempo real
            self._build_live_sensors_panel(),
            
            # Gráfico histórico
            self._build_chart_panel(),
            
            # Tabla de datos con operaciones CRUD
            self._build_data_table(),
            
            # Panel de edición
            self._build_edit_panel()
        ])
    
    def _build_data_table(self):
        """Tabla con capacidad de editar/eliminar."""
        self.readings_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Sensor")),
                ft.DataColumn(ft.Text("Valor")),
                ft.DataColumn(ft.Text("Fecha")),
                ft.DataColumn(ft.Text("Acciones")),  # 🆕 Nueva columna
            ],
            rows=[]
        )
        return self.readings_table
    
    def _build_edit_panel(self):
        """Panel para editar lecturas."""
        self.edit_value_field = ft.TextField(label="Nuevo valor")
        self.edit_button = ft.ElevatedButton(
            "Actualizar",
            on_click=self._on_update_click
        )
        return ft.Column([self.edit_value_field, self.edit_button])
    
    async def _on_update_click(self, e):
        """Handler cuando usuario actualiza una lectura."""
        selected = self.get_selected_reading()
        if selected:
            await self.controller.on_user_corrects_reading(
                selected.id,
                float(self.edit_value_field.value)
            )
```

---

## 4. COMPONENTES QUE HAY QUE ELIMINAR

### ❌ Eliminar:
1. **Carpeta `/json/`** - Reemplazada por base de datos SQL
2. **Repositorios JSON** - Reemplazados por implementaciones SQL
3. **Controladores de simulación** - Reemplazados por handlers MQTT reales
4. **Generadores de datos falsos** - Ya no se necesitan

### ⚠️ Deprecar gradualmente:
- Configuración de archivos JSON
- Funciones de exportación a JSON
- Caché en memoria simple (reemplazar por Redis)

---

## 5. FLUJO DE DATOS COMPLETO

```
┌─────────────────────────────────────────────────────────────────────┐
│                         FLUJO IoT → DB → UI                        │
└─────────────────────────────────────────────────────────────────────┘

1. RECEPCIÓN (Infraestructura)
   ┌──────────┐
   │  Sensor  │──MQTT──┐
   │  IoT     │        │
   └──────────┘        ▼
                ┌──────────────┐
                │ MQTT Broker  │
                │ (Mosquitto)  │
                └──────┬───────┘
                       │
                       ▼
                ┌──────────────┐
                │  Subscriber  │──┐
                │  (Python)    │  │
                └──────────────┘  │
                                  │
2. PROCESAMIENTO (Aplicación)     │
                                  ▼
                ┌──────────────────────────┐
                │ ReceiveSensorDataUseCase │
                │   - Validar              │
                │   - Transformar          │
                └──────────┬───────────────┘
                           │
                           ▼
                ┌──────────────────────────┐
                │     SensorService        │
                │   - Lógica de negocio    │
                │   - Calcular status      │
                └──────────┬───────────────┘
                           │
3. PERSISTENCIA            ▼
                ┌──────────────────────────┐
                │ SensorRepository (SQL)   │──┐
                │   - INSERT/UPDATE        │  │
                └──────────┬───────────────┘  │
                           │                  │
                           ▼                  │
                ┌──────────────────┐          │
                │   PostgreSQL     │          │
                │  (TimescaleDB)   │          │
                └──────────────────┘          │
                                              │
4. PRESENTACIÓN                               │
                                              ▼
                ┌──────────────────────────┐
                │   DashboardController    │
                │   - Recibe confirmación  │
                │   - Actualiza ViewModel  │
                └──────────┬───────────────┘
                           │
                           ▼
                ┌──────────────────────────┐
                │    DashboardViewModel    │
                │   - Estado reactivo      │
                │   - Notifica a UI        │
                └──────────┬───────────────┘
                           │
                           ▼
                ┌──────────────────────────┐
                │      DashboardView       │
                │   - Flet UI              │
                │   - Tabla CRUD           │
                └──────────────────────────┘

5. INTERACCIÓN USUARIO (CRUD)
   Usuario edita valor en tabla
          │
          ▼
   DashboardController.on_user_corrects_reading()
          │
          ▼
   UpdateSensorReadingUseCase.execute()
          │
          ▼
   SensorService.correct_reading() ──► UPDATE en BD
          │
          ▼
   Refrescar vista con datos actualizados
```

---

## 6. IMPLEMENTACIÓN POR FASES

### Fase 1: Infraestructura (Semana 1-2)
- [ ] Crear capa `infrastructure/database/`
- [ ] Implementar conexión PostgreSQL
- [ ] Crear esquema de base de datos
- [ ] Implementar repositorios SQL
- [ ] Configurar MQTT broker (Mosquitto)
- [ ] Crear subscriber MQTT

### Fase 2: Dominio (Semana 3)
- [ ] Refactorizar modelos actuales
- [ ] Crear interfaces de repositorio
- [ ] Implementar servicios de dominio
- [ ] Añadir lógica de negocio (alertas, validaciones)

### Fase 3: Aplicación (Semana 4)
- [ ] Crear DTOs
- [ ] Implementar casos de uso
- [ ] Crear mappers
- [ ] Implementar operaciones CRUD

### Fase 4: Presentación (Semana 5-6)
- [ ] Crear ViewModels
- [ ] Refactorizar views Flet
- [ ] Añadir tablas CRUD
- [ ] Implementar edición de datos
- [ ] WebSocket para tiempo real

### Fase 5: Integración (Semana 7)
- [ ] Conectar todo el flujo
- [ ] Testing end-to-end
- [ ] Optimización de queries

---

## 7. EJEMPLO DE CONFIGURACIÓN

**main.py** - Punto de entrada:
```python
async def main():
    # 1. Infraestructura
    db = DatabaseConnection(os.getenv("DATABASE_URL"))
    await db.connect()
    
    # 2. Repositorios
    sensor_repo = PostgresSensorRepository(db)
    
    # 3. Servicios
    sensor_service = SensorService(sensor_repo)
    
    # 4. Casos de uso
    receive_uc = ReceiveSensorDataUseCase(sensor_service)
    history_uc = GetSensorHistoryUseCase(sensor_service)
    update_uc = UpdateSensorReadingUseCase(sensor_service)
    
    # 5. Controladores
    dashboard_ctrl = DashboardController(
        receive_uc, history_uc, update_uc
    )
    
    # 6. MQTT Subscriber
    mqtt_handler = lambda data: dashboard_ctrl.on_sensor_data_received(data)
    subscriber = MQTTSubscriber(
        broker="localhost",
        topics=["sensors/+/data"],
        message_handler=mqtt_handler
    )
    subscriber.start()
    
    # 7. UI
    view = SensorDashboardView(dashboard_ctrl)
    await view.run()

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 8. RESUMEN DE CAMBIOS

| Componente | Acción | Complejidad |
|------------|--------|-------------|
| Estructura carpetas | **Cambiar** a arquitectura limpia | Media |
| Conexión BD | **Añadir** PostgreSQL + asyncpg | Media |
| MQTT | **Añadir** suscriptor y broker | Media |
| Modelos | **Modificar** añadir campos CRUD | Baja |
| Repositorios | **Reemplazar** JSON por SQL | Alta |
| Servicios | **Añadir** lógica de negocio | Media |
| Casos de uso | **Añadir** capa de aplicación | Media |
| Views | **Modificar** añadir CRUD UI | Media |
| JSON files | **Eliminar** | Baja |

**Tiempo estimado total:** 7-8 semanas para implementación completa.

---

¿Quieres que profundice en algún componente específico o que genere el código de alguna parte?