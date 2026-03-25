-- Creamos la bbdd en caso de que no exista
CREATE DATABASE IF NOT EXISTS artemus;
USE artemus;

-- Se usa TEXT como campo en algunas porque nose cuantos caracteres puede tener

CREATE TABLE Rol (
    id_rol INT AUTO_INCREMENT PRIMARY KEY,
    rol VARCHAR(50) NOT NULL
);

CREATE TABLE Permisos (
    id_permisos INT AUTO_INCREMENT PRIMARY KEY,
    descripcion VARCHAR(255) NOT NULL
);

CREATE TABLE Zona (
    id_zona INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    n_sensor INT DEFAULT 0,
    descripcion VARCHAR(255)
);

CREATE TABLE Tipo (
    id_tipo INT AUTO_INCREMENT PRIMARY KEY,
    descripcion VARCHAR(100) NOT NULL
);

CREATE TABLE Chat (
    id_chat INT AUTO_INCREMENT PRIMARY KEY,
    lista_chat TEXT,
    contenido_cifrado TEXT,
    fecha DATETIME
);

CREATE TABLE Incidencia (
    id_incidencia INT AUTO_INCREMENT PRIMARY KEY,
    descripcion VARCHAR(255),
    estado BOOLEAN,
    fecha DATETIME
);

-- Tablas con dependencias de otras se eliminan los datos en cascada para
-- que no genere fallos en los datos

CREATE TABLE Rol_Permisos (
    id_rol INT,
    id_permisos INT,
    PRIMARY KEY (id_rol, id_permisos),
    FOREIGN KEY (id_rol) REFERENCES Rol(id_rol) ON DELETE CASCADE,
    FOREIGN KEY (id_permisos) REFERENCES Permisos(id_permisos) ON DELETE CASCADE
);

CREATE TABLE Usuario (
    dni VARCHAR(20) PRIMARY KEY,
    id_rol INT NOT NULL,
    usuario VARCHAR(50) NOT NULL,
    nombre_usuario VARCHAR(100) NOT NULL,
    contrasena_hash VARCHAR(255) NOT NULL,
    telefono VARCHAR(20),
    direccion VARCHAR(255),
    c_publica TEXT,
    c_privada TEXT,
    estado_conexion BOOLEAN,
    sensores_asignados TEXT,
    supervisores TEXT,
    subordinados TEXT,
    FOREIGN KEY (id_rol) REFERENCES Rol(id_rol)
);

CREATE TABLE Ticket (
    id_ticket INT AUTO_INCREMENT PRIMARY KEY,
    usuario VARCHAR(50),
    tipo VARCHAR(50),
    descripcion VARCHAR(255),
    estado VARCHAR(20) DEFAULT 'PENDING',
    fecha DATETIME
);

-- Sensor se define antes que Dato porque Dato referencia a Sensor
CREATE TABLE Sensor (
    id_sensor INT AUTO_INCREMENT PRIMARY KEY,
    id_zona INT NOT NULL,
    id_tipo INT NOT NULL,
    id_rol INT,
    nombre VARCHAR(100),
    descripcion TEXT,
    FOREIGN KEY (id_zona) REFERENCES Zona(id_zona),
    FOREIGN KEY (id_tipo) REFERENCES Tipo(id_tipo),
    FOREIGN KEY (id_rol) REFERENCES Rol(id_rol)
);

CREATE TABLE Dato (
    id_dato INT AUTO_INCREMENT PRIMARY KEY,
    id_sensor INT NOT NULL,
    descripcion VARCHAR(255),
    estado BOOLEAN,
    timestamp DATETIME,
    consumo_ele FLOAT,
    FOREIGN KEY (id_sensor) REFERENCES Sensor(id_sensor)
);

CREATE TABLE Relacion_Chat (
    dni VARCHAR(20),
    id_chat INT,
    PRIMARY KEY (dni, id_chat),
    FOREIGN KEY (dni) REFERENCES Usuario(dni) ON DELETE CASCADE,
    FOREIGN KEY (id_chat) REFERENCES Chat(id_chat) ON DELETE CASCADE
);

CREATE TABLE Alerta (
    id_alerta INT AUTO_INCREMENT PRIMARY KEY,
    id_tipo INT NOT NULL,
    id_incidencia INT,
    descripcion TEXT,
    estado BOOLEAN,
    fecha DATETIME,
    FOREIGN KEY (id_tipo) REFERENCES Tipo(id_tipo),
    FOREIGN KEY (id_incidencia) REFERENCES Incidencia(id_incidencia)
);

-- Tablas con Herencia (Sensores)

CREATE TABLE Humedad (
    id_humedad INT AUTO_INCREMENT PRIMARY KEY,
    id_dato INT NOT NULL UNIQUE,
    humedad_relativa FLOAT,
    FOREIGN KEY (id_dato) REFERENCES Dato(id_dato) ON DELETE CASCADE
);

CREATE TABLE Temperatura (
    id_temperatura INT AUTO_INCREMENT PRIMARY KEY,
    id_dato INT NOT NULL UNIQUE,
    temperatura FLOAT,
    FOREIGN KEY (id_dato) REFERENCES Dato(id_dato) ON DELETE CASCADE
);

CREATE TABLE Iluminacion (
    id_iluminacion INT AUTO_INCREMENT PRIMARY KEY,
    id_dato INT NOT NULL UNIQUE,
    is_on BOOLEAN,
    valor FLOAT,
    FOREIGN KEY (id_dato) REFERENCES Dato(id_dato) ON DELETE CASCADE
);

CREATE TABLE Puerta (
    id_puerta INT AUTO_INCREMENT PRIMARY KEY,
    id_dato INT NOT NULL UNIQUE,
    nombre_usuario VARCHAR(100),
    entrada_salida VARCHAR(50),
    FOREIGN KEY (id_dato) REFERENCES Dato(id_dato) ON DELETE CASCADE
);

CREATE TABLE Calidad_Aire (
    id_calidad_aire INT AUTO_INCREMENT PRIMARY KEY,
    id_dato INT NOT NULL UNIQUE,
    nivel_co2 FLOAT,
    FOREIGN KEY (id_dato) REFERENCES Dato(id_dato) ON DELETE CASCADE
);

CREATE TABLE Viento (
    id_viento INT AUTO_INCREMENT PRIMARY KEY,
    id_dato INT NOT NULL UNIQUE,
    direccion VARCHAR(50),
    velocidad FLOAT,
    FOREIGN KEY (id_dato) REFERENCES Dato(id_dato) ON DELETE CASCADE
);

-- Datos iniciales
INSERT INTO Tipo (descripcion) VALUES
    ('Temperatura'),
    ('Humedad'),
    ('Viento'),
    ('Calidad_Aire'),
    ('Iluminacion'),
    ('Puerta');

INSERT INTO Zona (nombre, descripcion) VALUES
    ('Zona Principal', 'Zona por defecto');
