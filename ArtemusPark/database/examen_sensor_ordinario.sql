USE artemus;

CREATE TABLE IF NOT EXISTS Sensor_Ordinario (
    id_sensor_ordinario INT AUTO_INCREMENT PRIMARY KEY,
    valor_numerico INT NOT NULL,
    valor_texto VARCHAR(100) NOT NULL,
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO Sensor_Ordinario (
    valor_numerico,
    valor_texto
)
VALUES (
    75,
    'NORMAL'
);

SELECT *
FROM Sensor_Ordinario
ORDER BY fecha DESC;