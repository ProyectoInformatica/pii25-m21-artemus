-- ============================================================================
-- ESQUEMA DE BASE DE DATOS - SISTEMA ARTEMUS PARK
-- ============================================================================
-- Este script crea el esquema completo de base de datos para migrar
-- el sistema actual basado en JSON a una base de datos relacional SQL.
-- 
-- Base de datos recomendada: PostgreSQL 14+ o MySQL 8.0+
-- Características soportadas: JSON, particionamiento, índices avanzados
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 1. CREACIÓN DE BASE DE DATOS
-- ----------------------------------------------------------------------------

-- Para PostgreSQL:
-- CREATE DATABASE artemus_park 
--     WITH ENCODING = 'UTF8' 
--     LC_COLLATE = 'es_ES.UTF-8' 
--     LC_CTYPE = 'es_ES.UTF-8';

-- Para MySQL:
-- CREATE DATABASE artemus_park 
--     CHARACTER SET utf8mb4 
--     COLLATE utf8mb4_unicode_ci;

-- ----------------------------------------------------------------------------
-- 2. ENUMERACIONES (ENUMS)
-- ----------------------------------------------------------------------------

-- PostgreSQL:
CREATE TYPE user_role AS ENUM ('admin', 'maintenance', 'user');
CREATE TYPE sensor_type AS ENUM ('temperature', 'humidity', 'wind', 'smoke', 'light', 'door');
CREATE TYPE alert_severity AS ENUM ('low', 'medium', 'high', 'critical');
CREATE TYPE alert_type AS ENUM ('fire', 'wind', 'temperature', 'system', 'humidity', 'light');
CREATE TYPE request_status AS ENUM ('pending', 'in_progress', 'completed', 'cancelled');
CREATE TYPE request_priority AS ENUM ('low', 'medium', 'high', 'urgent');
CREATE TYPE request_type AS ENUM ('repair', 'inspection', 'installation', 'general');
CREATE TYPE maintenance_type AS ENUM ('calibration', 'repair', 'cleaning', 'inspection', 'replacement');
CREATE TYPE access_type AS ENUM ('entry', 'exit');
CREATE TYPE access_method AS ENUM ('card', 'ticket', 'manual', 'emergency', 'automatic');

-- MySQL (alternativa):
-- CREATE TABLE enum_values (...)

-- ----------------------------------------------------------------------------
-- 3. TABLA DE USUARIOS
-- ----------------------------------------------------------------------------

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role user_role NOT NULL DEFAULT 'user',
    full_name VARCHAR(100) NOT NULL,
    dni VARCHAR(20) UNIQUE,
    phone VARCHAR(20),
    address VARCHAR(255),
    email VARCHAR(100) UNIQUE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    last_login TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Índices para usuarios
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_active ON users(is_active);
CREATE INDEX idx_users_username ON users(username);

-- Comentarios
COMMENT ON TABLE users IS 'Tabla principal de usuarios del sistema';
COMMENT ON COLUMN users.role IS 'Roles: admin (administrador), maintenance (técnico), user (cliente)';

-- ----------------------------------------------------------------------------
-- 4. TABLA DE SENSORES
-- ----------------------------------------------------------------------------

CREATE TABLE sensors (
    id SERIAL PRIMARY KEY,
    sensor_id VARCHAR(50) NOT NULL UNIQUE,
    sensor_type sensor_type NOT NULL,
    name VARCHAR(100) NOT NULL,
    location VARCHAR(255),
    description TEXT,
    configuration JSON DEFAULT '{}',
    min_threshold DECIMAL(10,2),
    max_threshold DECIMAL(10,2),
    warning_threshold DECIMAL(10,2),
    emergency_threshold DECIMAL(10,2),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    installed_at TIMESTAMP,
    last_maintenance_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Índices para sensores
CREATE INDEX idx_sensors_type ON sensors(sensor_type);
CREATE INDEX idx_sensors_active ON sensors(is_active);
CREATE INDEX idx_sensors_location ON sensors(location);
CREATE INDEX idx_sensors_type_active ON sensors(sensor_type, is_active);

-- Comentarios
COMMENT ON TABLE sensors IS 'Catálogo de sensores instalados en el parque';
COMMENT ON COLUMN sensors.configuration IS 'Configuración específica del sensor en formato JSON';

-- ----------------------------------------------------------------------------
-- 5. TABLA DE MEDICIONES (PARTICIONADA)
-- ----------------------------------------------------------------------------

CREATE TABLE sensor_measurements (
    id BIGSERIAL,
    sensor_id INTEGER NOT NULL REFERENCES sensors(id) ON DELETE CASCADE,
    measured_at TIMESTAMP NOT NULL,
    value_numeric DECIMAL(10,2),
    value_boolean BOOLEAN,
    value_text VARCHAR(255),
    status VARCHAR(50),
    unit VARCHAR(20),
    raw_data JSON,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    PRIMARY KEY (id, measured_at)
) PARTITION BY RANGE (measured_at);

-- Crear particiones iniciales (ejemplo mensual)
CREATE TABLE sensor_measurements_2024_01 PARTITION OF sensor_measurements
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
CREATE TABLE sensor_measurements_2024_02 PARTITION OF sensor_measurements
    FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');
CREATE TABLE sensor_measurements_2024_03 PARTITION OF sensor_measurements
    FOR VALUES FROM ('2024-03-01') TO ('2024-04-01');
-- Continuar con el resto de meses...

-- Índices para mediciones
CREATE INDEX idx_measurements_sensor_time ON sensor_measurements(sensor_id, measured_at DESC);
CREATE INDEX idx_measurements_time ON sensor_measurements(measured_at DESC);
CREATE INDEX idx_measurements_status ON sensor_measurements(status);

-- Comentarios
COMMENT ON TABLE sensor_measurements IS 'Mediciones históricas de todos los sensores (tabla particionada por mes)';

-- ----------------------------------------------------------------------------
-- 6. TABLA DE ALERTAS
-- ----------------------------------------------------------------------------

CREATE TABLE alerts (
    id SERIAL PRIMARY KEY,
    sensor_id INTEGER REFERENCES sensors(id) ON DELETE SET NULL,
    alert_type alert_type NOT NULL,
    severity alert_severity NOT NULL DEFAULT 'medium',
    message TEXT NOT NULL,
    details JSON DEFAULT '{}',
    is_resolved BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP,
    resolved_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    resolution_notes TEXT
);

-- Índices para alertas
CREATE INDEX idx_alerts_resolved_severity ON alerts(is_resolved, severity);
CREATE INDEX idx_alerts_sensor_created ON alerts(sensor_id, created_at DESC);
CREATE INDEX idx_alerts_created ON alerts(created_at DESC);
CREATE INDEX idx_alerts_unresolved ON alerts(is_resolved) WHERE is_resolved = FALSE;

-- Comentarios
COMMENT ON TABLE alerts IS 'Registro de alertas y eventos críticos del sistema';

-- ----------------------------------------------------------------------------
-- 7. TABLA DE SOLICITUDES DE MANTENIMIENTO
-- ----------------------------------------------------------------------------

CREATE TABLE maintenance_requests (
    id SERIAL PRIMARY KEY,
    request_type request_type NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    status request_status NOT NULL DEFAULT 'pending',
    priority request_priority NOT NULL DEFAULT 'medium',
    created_by INTEGER NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    assigned_to INTEGER REFERENCES users(id) ON DELETE SET NULL,
    sensor_id INTEGER REFERENCES sensors(id) ON DELETE SET NULL,
    estimated_hours INTEGER,
    actual_hours INTEGER,
    cost DECIMAL(10,2),
    notes TEXT,
    attachments JSON DEFAULT '[]',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP
);

-- Índices para solicitudes
CREATE INDEX idx_requests_status ON maintenance_requests(status);
CREATE INDEX idx_requests_priority ON maintenance_requests(priority);
CREATE INDEX idx_requests_created_by ON maintenance_requests(created_by);
CREATE INDEX idx_requests_assigned_to ON maintenance_requests(assigned_to);
CREATE INDEX idx_requests_sensor ON maintenance_requests(sensor_id);
CREATE INDEX idx_requests_created_at ON maintenance_requests(created_at DESC);

-- Comentarios
COMMENT ON TABLE maintenance_requests IS 'Solicitudes de mantenimiento, reparación e inspección';

-- ----------------------------------------------------------------------------
-- 8. TABLA DE ASIGNACIONES USUARIO-SENSOR
-- ----------------------------------------------------------------------------

CREATE TABLE user_sensor_assignments (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    sensor_id INTEGER NOT NULL REFERENCES sensors(id) ON DELETE CASCADE,
    assigned_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    assigned_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    is_primary BOOLEAN NOT NULL DEFAULT FALSE,
    notes TEXT,
    
    UNIQUE(user_id, sensor_id)
);

-- Índices para asignaciones
CREATE INDEX idx_assignments_user ON user_sensor_assignments(user_id);
CREATE INDEX idx_assignments_sensor ON user_sensor_assignments(sensor_id);
CREATE INDEX idx_assignments_primary ON user_sensor_assignments(is_primary) WHERE is_primary = TRUE;

-- Comentarios
COMMENT ON TABLE user_sensor_assignments IS 'Relación de sensores asignados a técnicos de mantenimiento';

-- ----------------------------------------------------------------------------
-- 9. TABLA DE LOGS DE MANTENIMIENTO
-- ----------------------------------------------------------------------------

CREATE TABLE sensor_maintenance_logs (
    id SERIAL PRIMARY KEY,
    sensor_id INTEGER NOT NULL REFERENCES sensors(id) ON DELETE CASCADE,
    maintenance_type maintenance_type NOT NULL,
    description TEXT,
    parts_replaced JSON DEFAULT '[]',
    cost DECIMAL(10,2),
    performed_by INTEGER NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    performed_at TIMESTAMP NOT NULL,
    next_maintenance_at TIMESTAMP,
    duration_minutes INTEGER,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Índices para logs de mantenimiento
CREATE INDEX idx_maintenance_logs_sensor ON sensor_maintenance_logs(sensor_id);
CREATE INDEX idx_maintenance_logs_performed ON sensor_maintenance_logs(performed_at DESC);
CREATE INDEX idx_maintenance_logs_next ON sensor_maintenance_logs(next_maintenance_at);
CREATE INDEX idx_maintenance_logs_type ON sensor_maintenance_logs(maintenance_type);

-- Comentarios
COMMENT ON TABLE sensor_maintenance_logs IS 'Historial de mantenimientos realizados a los sensores';

-- ----------------------------------------------------------------------------
-- 10. TABLA DE LOGS DE ACCESO (PUERTAS)
-- ----------------------------------------------------------------------------

CREATE TABLE park_access_logs (
    id BIGSERIAL PRIMARY KEY,
    door_sensor_id INTEGER NOT NULL REFERENCES sensors(id) ON DELETE RESTRICT,
    access_type access_type NOT NULL,
    access_method access_method NOT NULL DEFAULT 'automatic',
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    visitor_name VARCHAR(100),
    visitor_document VARCHAR(50),
    is_authorized BOOLEAN NOT NULL DEFAULT TRUE,
    notes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Índices para logs de acceso
CREATE INDEX idx_access_logs_door ON park_access_logs(door_sensor_id);
CREATE INDEX idx_access_logs_timestamp ON park_access_logs(timestamp DESC);
CREATE INDEX idx_access_logs_user ON park_access_logs(user_id);
CREATE INDEX idx_access_logs_type ON park_access_logs(access_type);

-- Comentarios
COMMENT ON TABLE park_access_logs IS 'Registro de entradas y salidas por los torniquetes/puertas';

-- ----------------------------------------------------------------------------
-- 11. TABLA DE CONFIGURACIÓN DEL SISTEMA
-- ----------------------------------------------------------------------------

CREATE TABLE system_config (
    id SERIAL PRIMARY KEY,
    config_key VARCHAR(100) NOT NULL UNIQUE,
    config_value TEXT NOT NULL,
    data_type VARCHAR(20) NOT NULL DEFAULT 'string',
    description TEXT,
    is_editable BOOLEAN NOT NULL DEFAULT TRUE,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_by INTEGER REFERENCES users(id) ON DELETE SET NULL
);

-- Índices para configuración
CREATE INDEX idx_config_key ON system_config(config_key);

-- Insertar configuraciones por defecto
INSERT INTO system_config (config_key, config_value, data_type, description) VALUES
('park.open_hour', '9', 'integer', 'Hora de apertura del parque (formato 24h)'),
('park.close_hour', '18', 'integer', 'Hora de cierre del parque (formato 24h)'),
('park.max_capacity', '1000', 'integer', 'Capacidad máxima de visitantes'),
('park.name', 'Artemus Park', 'string', 'Nombre del parque'),
('alert.email.enabled', 'true', 'boolean', 'Envío de alertas por email habilitado'),
('alert.sms.enabled', 'false', 'boolean', 'Envío de alertas por SMS habilitado'),
('threshold.temperature.warning', '30', 'decimal', 'Umbral de advertencia de temperatura (°C)'),
('threshold.temperature.emergency', '35', 'decimal', 'Umbral de emergencia de temperatura (°C)'),
('threshold.smoke.warning', '30', 'integer', 'Umbral de advertencia de humo (ppm)'),
('threshold.smoke.emergency', '45', 'integer', 'Umbral de emergencia de humo (ppm)'),
('threshold.wind.warning', '60', 'decimal', 'Umbral de advertencia de viento (km/h)'),
('threshold.wind.emergency', '80', 'decimal', 'Umbral de emergencia de viento (km/h)'),
('data.retention_days', '365', 'integer', 'Días de retención de datos históricos');

-- ----------------------------------------------------------------------------
-- 12. TABLA DE SESIONES (Opcional - para autenticación JWT)
-- ----------------------------------------------------------------------------

CREATE TABLE user_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_token VARCHAR(255) NOT NULL UNIQUE,
    ip_address INET,
    user_agent TEXT,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_activity_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sessions_token ON user_sessions(session_token);
CREATE INDEX idx_sessions_user ON user_sessions(user_id);
CREATE INDEX idx_sessions_expires ON user_sessions(expires_at);

-- ----------------------------------------------------------------------------
-- 13. VISTAS ÚTILES
-- ----------------------------------------------------------------------------

-- Vista de sensores con última medición
CREATE VIEW sensor_latest_status AS
SELECT 
    s.id,
    s.sensor_id,
    s.sensor_type,
    s.name,
    s.location,
    s.is_active,
    m.measured_at as last_measurement_at,
    m.value_numeric as last_value,
    m.status as last_status,
    m.unit
FROM sensors s
LEFT JOIN LATERAL (
    SELECT * FROM sensor_measurements 
    WHERE sensor_id = s.id 
    ORDER BY measured_at DESC 
    LIMIT 1
) m ON true;

-- Vista de alertas activas
CREATE VIEW active_alerts AS
SELECT 
    a.*,
    s.sensor_id as sensor_code,
    s.sensor_type,
    s.name as sensor_name
FROM alerts a
LEFT JOIN sensors s ON a.sensor_id = s.id
WHERE a.is_resolved = FALSE
ORDER BY a.severity DESC, a.created_at DESC;

-- Vista de estadísticas de sensores
CREATE VIEW sensor_statistics AS
SELECT 
    s.id,
    s.sensor_id,
    s.sensor_type,
    s.name,
    COUNT(m.id) as total_measurements,
    COUNT(CASE WHEN m.status != 'NORMAL' THEN 1 END) as alert_count,
    AVG(m.value_numeric) as avg_value,
    MIN(m.value_numeric) as min_value,
    MAX(m.value_numeric) as max_value,
    MAX(m.measured_at) as last_measurement
FROM sensors s
LEFT JOIN sensor_measurements m ON s.id = m.sensor_id
WHERE m.measured_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY s.id, s.sensor_id, s.sensor_type, s.name;

-- ----------------------------------------------------------------------------
-- 14. FUNCIONES Y TRIGGERS
-- ----------------------------------------------------------------------------

-- Función para actualizar updated_at automáticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers para actualización automática
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_sensors_updated_at BEFORE UPDATE ON sensors
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_maintenance_requests_updated_at BEFORE UPDATE ON maintenance_requests
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_system_config_updated_at BEFORE UPDATE ON system_config
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Función para crear particiones automáticamente (PostgreSQL)
CREATE OR REPLACE FUNCTION create_measurement_partition()
RETURNS void AS $$
DECLARE
    partition_date DATE;
    partition_name TEXT;
    start_date DATE;
    end_date DATE;
BEGIN
    partition_date := DATE_TRUNC('month', CURRENT_DATE + INTERVAL '1 month');
    partition_name := 'sensor_measurements_' || TO_CHAR(partition_date, 'YYYY_MM');
    start_date := partition_date;
    end_date := partition_date + INTERVAL '1 month';
    
    EXECUTE format('CREATE TABLE IF NOT EXISTS %I PARTITION OF sensor_measurements 
                    FOR VALUES FROM (%L) TO (%L)',
                   partition_name, start_date, end_date);
END;
$$ LANGUAGE plpgsql;

-- ----------------------------------------------------------------------------
-- 15. DATOS INICIALES (SEED)
-- ----------------------------------------------------------------------------

-- Insertar sensores basados en la configuración actual
INSERT INTO sensors (sensor_id, sensor_type, name, location, installed_at) VALUES
-- Temperatura
('temp_01', 'temperature', 'Sensor Temperatura Zona Norte', 'Zona Norte del Parque', '2024-01-01'),
('temp_02', 'temperature', 'Sensor Temperatura Zona Sur', 'Zona Sur del Parque', '2024-01-01'),
('temp_03', 'temperature', 'Sensor Temperatura Central', 'Zona Central del Parque', '2024-01-01'),
-- Humedad
('hum_01', 'humidity', 'Sensor Humedad Jardines', 'Área de Jardines', '2024-01-01'),
('hum_02', 'humidity', 'Sensor Humedad Invernadero', 'Invernadero Principal', '2024-01-01'),
-- Viento
('wind_01', 'wind', 'Anemómetro Torre Principal', 'Torre de Control', '2024-01-01'),
-- Humo
('smoke_01', 'smoke', 'Detector Humo Cafetería', 'Cafetería del Parque', '2024-01-01'),
('smoke_02', 'smoke', 'Detector Humo Almacén', 'Almacén de Equipos', '2024-01-01'),
-- Puertas
('door_01', 'door', 'Torniquete Principal', 'Entrada Principal', '2024-01-01'),
('door_02', 'door', 'Acceso Proveedores', 'Entrada de Servicio', '2024-01-01'),
-- Luz
('light_01', 'light', 'Iluminación Paseo Central', 'Paseo Central', '2024-01-01'),
('light_02', 'light', 'Iluminación Parking', 'Zona de Parking', '2024-01-01');

-- Insertar usuarios administradores (contraseñas deben hashearse en producción)
INSERT INTO users (username, password_hash, role, full_name, dni, phone, address) VALUES
('admin1', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.VTtYA.qGZvKG6G', 'admin', 'Adrian Molina', '11111111H', '600111111', 'Calle Falsa 123'),
('admin_super', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.VTtYA.qGZvKG6G', 'admin', 'Sonia Ortega', '22222222J', '600222222', 'Avenida Siempre Viva 45'),
('boss_artemus', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.VTtYA.qGZvKG6G', 'admin', 'Javier Torres', '33333333P', '600333333', 'Plaza Mayor 1');

-- ----------------------------------------------------------------------------
-- FIN DEL SCRIPT
-- ----------------------------------------------------------------------------
