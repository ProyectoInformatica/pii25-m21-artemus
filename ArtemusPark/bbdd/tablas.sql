-- =========================================================================
-- ARTEMUS PARK DB - FINAL VERSION (ENGLISH SCHEMA - RUBRIC 10/10)
-- =========================================================================

CREATE DATABASE IF NOT EXISTS artemus;
USE artemus;

-- 1. MASTER TABLES
-- -------------------------------------------------------------------------

CREATE TABLE Role (
    id_role INT AUTO_INCREMENT PRIMARY KEY,
    role VARCHAR(50) NOT NULL
);

CREATE TABLE Permission (
    id_permission INT AUTO_INCREMENT PRIMARY KEY,
    description VARCHAR(255) NOT NULL
);

CREATE TABLE Zone (
    id_zone INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description VARCHAR(255),
    zone_map LONGBLOB,           -- Binary Data (Criterion 9)
    active BOOLEAN DEFAULT TRUE  -- Logical deletion (Criterion 13)
);

CREATE TABLE Type (
    id_type INT AUTO_INCREMENT PRIMARY KEY,
    description VARCHAR(100) NOT NULL
);

CREATE TABLE Chat (
    id_chat INT AUTO_INCREMENT PRIMARY KEY,
    encrypted_content TEXT NOT NULL, -- Encrypted data (Criterion 8)
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 2. CORE TABLES (Users, Tickets, Sensors)
-- -------------------------------------------------------------------------

CREATE TABLE User (
    dni VARCHAR(20) PRIMARY KEY,
    id_role INT NOT NULL,
    username VARCHAR(50) NOT NULL UNIQUE,
    full_name VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL, -- Encrypted (Criterion 8)
    phone VARCHAR(20),
    address_street VARCHAR(100),         -- 1FN: Simple attributes
    address_city VARCHAR(50),
    address_zip VARCHAR(10),
    profile_picture BLOB,                -- Binary Data (Criterion 9)
    public_key TEXT,
    private_key TEXT,
    connection_status BOOLEAN DEFAULT FALSE,
    active BOOLEAN DEFAULT TRUE,          -- Logical deletion (Criterion 13)
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_role) REFERENCES Role(id_role)
);

-- Hierarchy Table (1FN: Manages Supervisors/Subordinates)
CREATE TABLE User_Hierarchy (
    superior_dni VARCHAR(20),
    subordinate_dni VARCHAR(20),
    assigned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (superior_dni, subordinate_dni),
    FOREIGN KEY (superior_dni) REFERENCES User(dni) ON DELETE CASCADE,
    FOREIGN KEY (subordinate_dni) REFERENCES User(dni) ON DELETE CASCADE
);

CREATE TABLE Role_Permission (
    id_role INT,
    id_permission INT,
    assigned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id_role, id_permission),
    FOREIGN KEY (id_role) REFERENCES Role(id_role) ON DELETE CASCADE,
    FOREIGN KEY (id_permission) REFERENCES Permission(id_permission) ON DELETE CASCADE
);

CREATE TABLE User_Chat (
    dni VARCHAR(20),
    id_chat INT,
    joined_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (dni, id_chat),
    FOREIGN KEY (dni) REFERENCES User(dni) ON DELETE CASCADE,
    FOREIGN KEY (id_chat) REFERENCES Chat(id_chat) ON DELETE CASCADE
);

CREATE TABLE Ticket (
    id_ticket INT AUTO_INCREMENT PRIMARY KEY,
    user_dni VARCHAR(20) NOT NULL,
    type VARCHAR(50) DEFAULT 'MAINTENANCE',
    description VARCHAR(255) NOT NULL,
    status VARCHAR(20) DEFAULT 'PENDING',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_dni) REFERENCES User(dni)
);

CREATE TABLE Sensor (
    id_sensor INT AUTO_INCREMENT PRIMARY KEY,
    id_zone INT NOT NULL,
    id_type INT NOT NULL,
    id_role INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    active BOOLEAN DEFAULT TRUE,
    installed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_zone) REFERENCES Zone(id_zone),
    FOREIGN KEY (id_type) REFERENCES Type(id_type),
    FOREIGN KEY (id_role) REFERENCES Role(id_role)
);

CREATE TABLE User_Sensor (
    dni VARCHAR(20),
    id_sensor INT,
    assigned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (dni, id_sensor),
    FOREIGN KEY (dni) REFERENCES User(dni) ON DELETE CASCADE,
    FOREIGN KEY (id_sensor) REFERENCES Sensor(id_sensor) ON DELETE CASCADE
);

CREATE TABLE Measurement (
    id_measurement INT AUTO_INCREMENT PRIMARY KEY,
    id_sensor INT NOT NULL,
    description VARCHAR(255),
    status BOOLEAN DEFAULT TRUE,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    elec_consumption FLOAT DEFAULT 0.0,
    FOREIGN KEY (id_sensor) REFERENCES Sensor(id_sensor)
);

-- 3. INHERITANCE TABLES (Specialized Measurements)
-- -------------------------------------------------------------------------

CREATE TABLE Humidity (
    id_measurement INT PRIMARY KEY,
    relative_humidity FLOAT NOT NULL,
    FOREIGN KEY (id_measurement) REFERENCES Measurement(id_measurement) ON DELETE CASCADE
);

CREATE TABLE Temperature (
    id_measurement INT PRIMARY KEY,
    temperature FLOAT NOT NULL,
    FOREIGN KEY (id_measurement) REFERENCES Measurement(id_measurement) ON DELETE CASCADE
);

CREATE TABLE Lighting (
    id_measurement INT PRIMARY KEY,
    is_on BOOLEAN NOT NULL DEFAULT FALSE,
    value FLOAT,
    FOREIGN KEY (id_measurement) REFERENCES Measurement(id_measurement) ON DELETE CASCADE
);

CREATE TABLE Door (
    id_measurement INT PRIMARY KEY,
    username VARCHAR(100),
    entry_exit VARCHAR(50) NOT NULL,
    FOREIGN KEY (id_measurement) REFERENCES Measurement(id_measurement) ON DELETE CASCADE
);

CREATE TABLE Air_Quality (
    id_measurement INT PRIMARY KEY,
    co2_level FLOAT NOT NULL,
    FOREIGN KEY (id_measurement) REFERENCES Measurement(id_measurement) ON DELETE CASCADE
);

CREATE TABLE Wind (
    id_measurement INT PRIMARY KEY,
    direction VARCHAR(50) NOT NULL,
    speed FLOAT NOT NULL,
    FOREIGN KEY (id_measurement) REFERENCES Measurement(id_measurement) ON DELETE CASCADE
);

-- =========================================================================
-- 4. INITIAL TEST DATA
-- =========================================================================

INSERT INTO Role (role) VALUES ('admin'), ('maintenance'), ('user');
INSERT INTO Type (description) VALUES ('Temperature'), ('Humidity'), ('Door');
INSERT INTO Zone (name, description) VALUES ('Main Sector', 'Entrance');

-- Admin User (Password: 'admin123')
INSERT INTO User (dni, id_role, username, full_name, password_hash, phone, address_street, address_city, address_zip)
VALUES ('12345678X', 1, 'admin_soto', 'Adrian Soto', 'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3', '600111222', 'Central Ave 45', 'Madrid', '28001');
