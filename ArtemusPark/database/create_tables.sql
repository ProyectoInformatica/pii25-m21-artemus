-- Artemus Park Database - Table Creation Script
-- Entity-Relationship Model based on diagramaTablasArtemus05.png

-- Table: Rol
CREATE TABLE Rol (
    id_rol INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    rol VARCHAR(50) NOT NULL UNIQUE
);

-- Table: Usuario
CREATE TABLE Usuario (
    id_usuario INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    id_rol INT NOT NULL,
    usuario VARCHAR(255) NOT NULL UNIQUE,
    nombre_usuario VARCHAR(255) NOT NULL,
    contrasena_hash VARCHAR(255) NOT NULL,
    telefono VARCHAR(20),
    direccion VARCHAR(255),
    c_publica VARCHAR(255),
    c_privada VARCHAR(255),
    estado_conexion BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (id_rol) REFERENCES Rol(id_rol) ON DELETE CASCADE
);

-- Table: Permisos
CREATE TABLE Permisos (
    id_permisos INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    descripcion VARCHAR(255)
);

-- Table: Rol_Permisos (Junction table for many-to-many relationship)
CREATE TABLE Rol_Permisos (
    id_rol INT NOT NULL,
    id_permisos INT NOT NULL,
    PRIMARY KEY (id_rol, id_permisos),
    FOREIGN KEY (id_rol) REFERENCES Rol(id_rol) ON DELETE CASCADE,
    FOREIGN KEY (id_permisos) REFERENCES Permisos(id_permisos) ON DELETE CASCADE
);

-- Table: Tipo
CREATE TABLE Tipo (
    id_tipo INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    descripcion VARCHAR(255)
);

-- Table: Zona
CREATE TABLE Zona (
    id_zona INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL,
    n_sensor INT,
    descripcion VARCHAR(255)
);

-- Table: Sensor
CREATE TABLE Sensor (
    id_sensor INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    id_zona INT NOT NULL,
    id_tipo INT NOT NULL,
    id_usuario INT NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    descripcion VARCHAR(255),
    FOREIGN KEY (id_zona) REFERENCES Zona(id_zona) ON DELETE CASCADE,
    FOREIGN KEY (id_tipo) REFERENCES Tipo(id_tipo) ON DELETE CASCADE,
    FOREIGN KEY (id_usuario) REFERENCES Usuario(id_usuario) ON DELETE CASCADE
);

-- Table: Incidencia
CREATE TABLE Incidencia (
    id_incidencia INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    descripcion VARCHAR(255),
    estado BOOLEAN DEFAULT TRUE,
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Table: Alerta
CREATE TABLE Alerta (
    id_alerta INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    id_incidencia INT,
    descripcion VARCHAR(255),
    estado BOOLEAN DEFAULT TRUE,
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_incidencia) REFERENCES Incidencia(id_incidencia) ON DELETE CASCADE
);

-- Table: Evento
CREATE TABLE Evento (
    id_evento INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    direccion VARCHAR(255),
    velocidad FLOAT
);

-- Table: Dato
CREATE TABLE Dato (
    id_dato INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    id_alerta INT,
    id_tipo INT NOT NULL,
    id_evento INT,
    estado BOOLEAN DEFAULT TRUE,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    descripcion VARCHAR(255),
    FOREIGN KEY (id_alerta) REFERENCES Alerta(id_alerta) ON DELETE SET NULL,
    FOREIGN KEY (id_tipo) REFERENCES Tipo(id_tipo) ON DELETE CASCADE,
    FOREIGN KEY (id_evento) REFERENCES Evento(id_evento) ON DELETE SET NULL
);

-- Table: Humedad
CREATE TABLE Humedad (
    id_humedad INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    id_dato INT NOT NULL,
    humedad_relativa FLOAT,
    FOREIGN KEY (id_dato) REFERENCES Dato(id_dato) ON DELETE CASCADE
);

-- Table: Temperatura
CREATE TABLE Temperatura (
    id_temperatura INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    id_dato INT NOT NULL,
    temperatura FLOAT,
    FOREIGN KEY (id_dato) REFERENCES Dato(id_dato) ON DELETE CASCADE
);

-- Table: Iluminacion
CREATE TABLE Iluminacion (
    id_iluminacion INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    id_dato INT NOT NULL,
    id_tipo INT,
    FOREIGN KEY (id_dato) REFERENCES Dato(id_dato) ON DELETE CASCADE,
    FOREIGN KEY (id_tipo) REFERENCES Tipo(id_tipo) ON DELETE SET NULL
);

-- Table: Puerta
CREATE TABLE Puerta (
    id_puerta INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    id_dato INT NOT NULL,
    nombre_usuario VARCHAR(255),
    entrada_salida VARCHAR(50),
    FOREIGN KEY (id_dato) REFERENCES Dato(id_dato) ON DELETE CASCADE
);

-- Table: Calidad_Aire
CREATE TABLE Calidad_Aire (
    id_calidad_aire INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    id_dato INT NOT NULL,
    nivel_co2 VARCHAR(50),
    FOREIGN KEY (id_dato) REFERENCES Dato(id_dato) ON DELETE CASCADE
);

-- Table: Ticket
CREATE TABLE Ticket (
    id_ticket INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    id_usuario INT NOT NULL,
    descripcion VARCHAR(255),
    estado BOOLEAN DEFAULT TRUE,
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES Usuario(id_usuario) ON DELETE CASCADE
);

-- Table: Chat
CREATE TABLE Chat (
    id_chat INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    lista_chats VARCHAR(255),
    contenido_cifrado VARCHAR(500),
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Table: Relacion_Chat (Junction table for Chat-Usuario relationship)
CREATE TABLE Relacion_Chat (
    id_chat INT NOT NULL,
    id_usuario INT NOT NULL,
    PRIMARY KEY (id_chat, id_usuario),
    FOREIGN KEY (id_chat) REFERENCES Chat(id_chat) ON DELETE CASCADE,
    FOREIGN KEY (id_usuario) REFERENCES Usuario(id_usuario) ON DELETE CASCADE
);
