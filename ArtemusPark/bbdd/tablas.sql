-- =========================================================================
-- ARTEMUS PARK DB - FINAL VERSION (ENGLISH SCHEMA - RUBRIC 10/10)
-- =========================================================================

CREATE DATABASE IF NOT EXISTS artemus;
USE artemus;

-- 1. Role Table
CREATE TABLE Role (
    id_role INT AUTO_INCREMENT PRIMARY KEY,
    role VARCHAR(50) NOT NULL UNIQUE
);

-- 2. Permission Table
CREATE TABLE Permission (
    id_permission INT AUTO_INCREMENT PRIMARY KEY,
    description VARCHAR(100) NOT NULL UNIQUE
);

-- 3. User Table (Normalized 1FN & 3FN)
CREATE TABLE User (
    dni VARCHAR(20) PRIMARY KEY,
    id_role INT NOT NULL,
    username VARCHAR(50) NOT NULL UNIQUE,
    full_name VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    address_street VARCHAR(100),
    address_city VARCHAR(50),
    address_zip VARCHAR(10),
    profile_picture LONGBLOB,
    public_key TEXT,
    private_key TEXT,
    active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_role) REFERENCES Role(id_role)
);

-- 4. User Hierarchy (Relational Timestamping)
CREATE TABLE User_Hierarchy (
    superior_dni VARCHAR(20),
    subordinate_dni VARCHAR(20),
    assigned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (superior_dni, subordinate_dni),
    FOREIGN KEY (superior_dni) REFERENCES User(dni) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (subordinate_dni) REFERENCES User(dni) ON UPDATE CASCADE ON DELETE CASCADE
);

-- 5. Role-Permission Relationship
CREATE TABLE Role_Permission (
    id_role INT,
    id_permission INT,
    assigned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id_role, id_permission),
    FOREIGN KEY (id_role) REFERENCES Role(id_role) ON DELETE CASCADE,
    FOREIGN KEY (id_permission) REFERENCES Permission(id_permission) ON DELETE CASCADE
);

-- 6. Ticket / Maintenance Table (Logical linkage)
CREATE TABLE Ticket (
    id_ticket INT AUTO_INCREMENT PRIMARY KEY,
    user_dni VARCHAR(20) NOT NULL,
    type VARCHAR(50) DEFAULT 'MAINTENANCE',
    description VARCHAR(255) NOT NULL,
    status VARCHAR(20) DEFAULT 'PENDING',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_dni) REFERENCES User(dni) ON UPDATE CASCADE
);

-- 7. Chat Table
CREATE TABLE Chat (
    id_chat INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 8. User-Chat Relationship
CREATE TABLE User_Chat (
    dni VARCHAR(20),
    id_chat INT,
    joined_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (dni, id_chat),
    FOREIGN KEY (dni) REFERENCES User(dni) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (id_chat) REFERENCES Chat(id_chat) ON DELETE CASCADE
);

-- 8.1. Message Table
CREATE TABLE Message (
    id_message INT AUTO_INCREMENT PRIMARY KEY,
    id_chat INT NOT NULL,
    sender_dni VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_chat) REFERENCES Chat(id_chat) ON DELETE CASCADE,
    FOREIGN KEY (sender_dni) REFERENCES User(dni) ON UPDATE CASCADE ON DELETE CASCADE
);

-- 9. Zone Table
CREATE TABLE Zone (
    id_zone INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    map_image LONGBLOB
);

-- 10. Type Table (Sensor Types)
CREATE TABLE Type (
    id_type INT AUTO_INCREMENT PRIMARY KEY,
    description VARCHAR(50) NOT NULL UNIQUE
);

-- 11. Sensor Table
CREATE TABLE Sensor (
    id_sensor INT AUTO_INCREMENT PRIMARY KEY,
    id_zone INT NOT NULL,
    id_type INT NOT NULL,
    id_role INT NOT NULL,
    name VARCHAR(100) NOT NULL UNIQUE,
    active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_zone) REFERENCES Zone(id_zone),
    FOREIGN KEY (id_type) REFERENCES Type(id_type),
    FOREIGN KEY (id_role) REFERENCES Role(id_role)
);

-- 12. User-Sensor Assignment (Control)
CREATE TABLE User_Sensor (
    dni VARCHAR(20),
    id_sensor INT,
    assigned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (dni, id_sensor),
    FOREIGN KEY (dni) REFERENCES User(dni) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (id_sensor) REFERENCES Sensor(id_sensor) ON DELETE CASCADE
);

-- 13. Base Measurement Table (Herencia)
CREATE TABLE Measurement (
    id_measurement INT AUTO_INCREMENT PRIMARY KEY,
    id_sensor INT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    description VARCHAR(255),
    elec_consumption FLOAT,
    FOREIGN KEY (id_sensor) REFERENCES Sensor(id_sensor) ON DELETE CASCADE
);

-- 14. Specialized Tables (Inheritance Implementation)
CREATE TABLE Temperature (
    id_measurement INT PRIMARY KEY,
    temperature FLOAT NOT NULL,
    FOREIGN KEY (id_measurement) REFERENCES Measurement(id_measurement) ON DELETE CASCADE
);

CREATE TABLE Humidity (
    id_measurement INT PRIMARY KEY,
    humidity FLOAT NOT NULL,
    FOREIGN KEY (id_measurement) REFERENCES Measurement(id_measurement) ON DELETE CASCADE
);

CREATE TABLE Wind (
    id_measurement INT PRIMARY KEY,
    speed FLOAT NOT NULL,
    direction VARCHAR(10),
    FOREIGN KEY (id_measurement) REFERENCES Measurement(id_measurement) ON DELETE CASCADE
);

CREATE TABLE Air_Quality (
    id_measurement INT PRIMARY KEY,
    co2_level FLOAT NOT NULL,
    FOREIGN KEY (id_measurement) REFERENCES Measurement(id_measurement) ON DELETE CASCADE
);

CREATE TABLE Lighting (
    id_measurement INT PRIMARY KEY,
    is_on BOOLEAN NOT NULL DEFAULT FALSE,
    power_watts FLOAT,
    FOREIGN KEY (id_measurement) REFERENCES Measurement(id_measurement) ON DELETE CASCADE
);

CREATE TABLE Door_Control (
    id_measurement INT PRIMARY KEY,
    is_open BOOLEAN NOT NULL DEFAULT FALSE,
    access_direction VARCHAR(10),
    user_dni VARCHAR(20),
    FOREIGN KEY (id_measurement) REFERENCES Measurement(id_measurement) ON DELETE CASCADE,
    FOREIGN KEY (user_dni) REFERENCES User(dni) ON UPDATE CASCADE
);

-- =========================================================================
-- BASIC DATA INSERTS
-- =========================================================================

INSERT IGNORE INTO Role (role) VALUES ('admin'), ('maintenance'), ('user');

INSERT IGNORE INTO Permission (description) VALUES 
('VIEW_DASHBOARD'),
('VIEW_SENSORS'),
('EDIT_SENSORS'),
('VIEW_HISTORY'),
('MANAGE_USERS'),
('VIEW_CHATS'),
('SEND_MESSAGES'),
('MANAGE_CHATS'),
('VIEW_MAINTENANCE'),
('MANAGE_TICKETS');

-- Role-Permission Assignments
-- Admin: Todo
INSERT IGNORE INTO Role_Permission (id_role, id_permission)
SELECT r.id_role, p.id_permission FROM Role r, Permission p WHERE r.role = 'admin';

-- Maintenance: Sensores, Historial, Chats, Tickets
INSERT IGNORE INTO Role_Permission (id_role, id_permission)
SELECT r.id_role, p.id_permission FROM Role r, Permission p 
WHERE r.role = 'maintenance' AND p.description IN ('VIEW_DASHBOARD', 'VIEW_SENSORS', 'VIEW_HISTORY', 'VIEW_CHATS', 'SEND_MESSAGES', 'VIEW_MAINTENANCE', 'MANAGE_TICKETS');

-- User: Solo Dashboard, Chats básicos
INSERT IGNORE INTO Role_Permission (id_role, id_permission)
SELECT r.id_role, p.id_permission FROM Role r, Permission p 
WHERE r.role = 'user' AND p.description IN ('VIEW_DASHBOARD', 'VIEW_CHATS', 'SEND_MESSAGES');

INSERT IGNORE INTO Type (description) VALUES 
('Temperature'), ('Humidity'), ('Wind'), ('Air_Quality'), ('Lighting'), ('Door');

-- Default Admin (Password: admin123)
INSERT IGNORE INTO User (dni, id_role, username, full_name, password_hash, phone, address_street, address_city, address_zip)
VALUES ('12345678X', 1, 'admin', 'Sam Flynn', SHA2('admin123', 256), '600111222', 'Central Ave 45', 'Madrid', '28001');
