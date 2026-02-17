"""
Script de inicialización de la base de datos MariaDB para Artemus Park.
Crea la base de datos y todas las tablas necesarias.
"""

import mysql.connector
from mysql.connector import Error
from ArtemusPark.database.DB_Config import DB_CONFIG, ADMIN_DB_CONFIG

# SQL para crear la base de datos
CREATE_DATABASE_SQL = f"""
CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;
"""

# SQL para crear las tablas
CREATE_TABLES_SQL = """
-- Tabla de Usuarios
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('admin', 'maintenance', 'user') NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    dni VARCHAR(20) UNIQUE NOT NULL,
    phone VARCHAR(20),
    address VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_role (role)
) ENGINE=InnoDB;

-- Tabla de Relaciones de Supervisor (usuarios y sus supervisores)
CREATE TABLE IF NOT EXISTS user_supervisors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    supervisor_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (supervisor_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_supervisor (user_id, supervisor_id)
) ENGINE=InnoDB;

-- Tabla de Sensores Asignados (para mantenimiento)
CREATE TABLE IF NOT EXISTS user_assigned_sensors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    sensor_id VARCHAR(50) NOT NULL,
    sensor_type ENUM('temperature', 'humidity', 'smoke', 'wind', 'door', 'light') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_sensor_assignment (user_id, sensor_id)
) ENGINE=InnoDB;

-- Tabla de Solicitudes
CREATE TABLE IF NOT EXISTS requests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    request_type ENUM('sensor_change', 'maintenance', 'access_request', 'other') DEFAULT 'sensor_change',
    message TEXT NOT NULL,
    status ENUM('PENDING', 'APPROVED', 'REJECTED', 'COMPLETED') DEFAULT 'PENDING',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_status (status),
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB;

-- Tabla de Mediciones de Temperatura
CREATE TABLE IF NOT EXISTS temperature_measurements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sensor_id VARCHAR(50) NOT NULL,
    timestamp DATETIME NOT NULL,
    value DECIMAL(5,2) NOT NULL,
    status VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_sensor_date (sensor_id, timestamp),
    INDEX idx_timestamp (timestamp)
) ENGINE=InnoDB;

-- Tabla de Mediciones de Humedad
CREATE TABLE IF NOT EXISTS humidity_measurements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sensor_id VARCHAR(50) NOT NULL,
    timestamp DATETIME NOT NULL,
    value DECIMAL(5,2) NOT NULL,
    status VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_sensor_date (sensor_id, timestamp),
    INDEX idx_timestamp (timestamp)
) ENGINE=InnoDB;

-- Tabla de Mediciones de Humo
CREATE TABLE IF NOT EXISTS smoke_measurements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sensor_id VARCHAR(50) NOT NULL,
    timestamp DATETIME NOT NULL,
    value DECIMAL(5,2) NOT NULL,
    status VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_sensor_date (sensor_id, timestamp),
    INDEX idx_timestamp (timestamp)
) ENGINE=InnoDB;

-- Tabla de Mediciones de Viento
CREATE TABLE IF NOT EXISTS wind_measurements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sensor_id VARCHAR(50) NOT NULL,
    timestamp DATETIME NOT NULL,
    value DECIMAL(5,2) NOT NULL,
    status VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_sensor_date (sensor_id, timestamp),
    INDEX idx_timestamp (timestamp)
) ENGINE=InnoDB;

-- Tabla de Estado de Puertas
CREATE TABLE IF NOT EXISTS door_status (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sensor_id VARCHAR(50) NOT NULL,
    timestamp DATETIME NOT NULL,
    status VARCHAR(20) NOT NULL,
    is_open BOOLEAN NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_sensor_date (sensor_id, timestamp),
    INDEX idx_timestamp (timestamp)
) ENGINE=InnoDB;

-- Tabla de Mediciones de Luz
CREATE TABLE IF NOT EXISTS light_measurements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sensor_id VARCHAR(50) NOT NULL,
    timestamp DATETIME NOT NULL,
    value DECIMAL(5,2) NOT NULL,
    status VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_sensor_date (sensor_id, timestamp),
    INDEX idx_timestamp (timestamp)
) ENGINE=InnoDB;

-- Tabla de Configuración del Sistema
CREATE TABLE IF NOT EXISTS system_config (
    id INT AUTO_INCREMENT PRIMARY KEY,
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;
"""

# Datos iniciales de usuarios
DEFAULT_USERS = [
    (
        "admin1",
        "admin123",
        "admin",
        "Adrian Molina",
        "11111111H",
        "600111111",
        "Calle Falsa 123",
    ),
    (
        "admin_super",
        "root2025",
        "admin",
        "Sonia Ortega",
        "22222222J",
        "600222222",
        "Avenida Siempre Viva 45",
    ),
    (
        "boss_artemus",
        "masterkey",
        "admin",
        "Javier Torres",
        "33333333P",
        "600333333",
        "Plaza Mayor 1",
    ),
    (
        "admin_alpha",
        "alpha_pass",
        "admin",
        "Marta Vega",
        "44444444A",
        "600444444",
        "Rua Augusta 10",
    ),
    (
        "maint_joe",
        "fixitnow",
        "maintenance",
        "Jose Pardo",
        "55555555K",
        "600555555",
        "Paseo de la Castellana 50",
    ),
    (
        "tech_sarah",
        "cables99",
        "maintenance",
        "Sara Marin",
        "66666666Q",
        "600666666",
        "Gran Via 20",
    ),
    (
        "eng_mike",
        "wrench77",
        "maintenance",
        "Miguel Rios",
        "77777777B",
        "600777777",
        "Via Laietana 30",
    ),
    (
        "client_ana",
        "guest001",
        "user",
        "Ana Garcia",
        "88888888Y",
        "600888888",
        "Calle del Arenal 1",
    ),
    (
        "visit_tom",
        "parkfun2",
        "user",
        "Tomas Perez",
        "99999999R",
        "600999999",
        "Calle Alcala 15",
    ),
    (
        "user_demo",
        "testpass",
        "user",
        "Dario Ponce",
        "10101010P",
        "600101010",
        "Calle Mayor 5",
    ),
    (
        "user_sofia",
        "sofia_pass",
        "user",
        "Sofia Martin",
        "12121212M",
        "600121212",
        "Plaza de Espana 3",
    ),
    (
        "user_pedro",
        "pedro_pass",
        "user",
        "Pedro Ruiz",
        "13131313S",
        "600131313",
        "Paseo del Prado 10",
    ),
    (
        "user_maria",
        "maria_pass",
        "user",
        "Maria Gomez",
        "14141414W",
        "600141414",
        "Calle Serrano 25",
    ),
    (
        "user_luis",
        "luis_pass",
        "user",
        "Luis Hernandez",
        "15151515N",
        "600151515",
        "Ronda de Toledo 5",
    ),
    (
        "user_laura",
        "laura_pass",
        "user",
        "Laura Diaz",
        "16161616E",
        "600161616",
        "Calle de la Paz 7",
    ),
    (
        "user_carlos",
        "carlos_pass",
        "user",
        "Carlos Sanchez",
        "17171717D",
        "600171717",
        "Avenida de America 12",
    ),
]

# Relaciones de supervisores
SUPERVISOR_RELATIONS = [
    ("user_laura", "admin1"),
    ("user_carlos", "admin1"),
    ("client_ana", "admin_super"),
    ("visit_tom", "admin_super"),
    ("user_demo", "admin_super"),
    ("client_ana", "boss_artemus"),
    ("user_sofia", "boss_artemus"),
    ("user_pedro", "boss_artemus"),
    ("user_maria", "admin_alpha"),
    ("user_luis", "admin_alpha"),
]

# Sensores asignados a mantenimiento
ASSIGNED_SENSORS = [
    ("maint_joe", "temp_01", "temperature"),
    ("maint_joe", "hum_01", "humidity"),
    ("maint_joe", "door_01", "door"),
    ("tech_sarah", "smoke_01", "smoke"),
    ("tech_sarah", "light_01", "light"),
    ("tech_sarah", "wind_01", "wind"),
]


def init_database():
    """Inicializa la base de datos completa."""
    conn = None
    try:
        # Conectar como admin (sin base de datos específica)
        conn = mysql.connector.connect(**ADMIN_DB_CONFIG)
        cursor = conn.cursor()

        # Crear base de datos
        print(f"Creando base de datos '{DB_CONFIG['database']}'...")
        cursor.execute(CREATE_DATABASE_SQL)
        print("Base de datos creada/verificada exitosamente.")

        # Usar la base de datos
        cursor.execute(f"USE {DB_CONFIG['database']}")

        # Crear tablas
        print("Creando tablas...")
        for statement in CREATE_TABLES_SQL.split(";"):
            stmt = statement.strip()
            if stmt:
                cursor.execute(stmt)
        print("Tablas creadas exitosamente.")

        # Insertar usuarios por defecto
        print("Insertando usuarios por defecto...")
        cursor.executemany(
            """
            INSERT IGNORE INTO users (username, password, role, full_name, dni, phone, address)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
            DEFAULT_USERS,
        )

        # Insertar relaciones de supervisores
        print("Configurando relaciones de supervisores...")
        for user, supervisor in SUPERVISOR_RELATIONS:
            cursor.execute(
                """
                INSERT IGNORE INTO user_supervisors (user_id, supervisor_id)
                SELECT u1.id, u2.id 
                FROM users u1, users u2 
                WHERE u1.username = %s AND u2.username = %s
            """,
                (user, supervisor),
            )

        # Insertar sensores asignados
        print("Configurando sensores asignados...")
        for username, sensor_id, sensor_type in ASSIGNED_SENSORS:
            cursor.execute(
                """
                INSERT IGNORE INTO user_assigned_sensors (user_id, sensor_id, sensor_type)
                SELECT id, %s, %s FROM users WHERE username = %s
            """,
                (sensor_id, sensor_type, username),
            )

        conn.commit()
        print("Base de datos inicializada exitosamente.")
        print(f"Total de usuarios insertados: {len(DEFAULT_USERS)}")

    except Error as e:
        print(f"Error inicializando base de datos: {e}")
        raise
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


if __name__ == "__main__":
    init_database()
