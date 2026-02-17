# Configuración de MariaDB para Artemus Park

## Método Recomendado: Docker 🐳

La forma más fácil y rápida de configurar MariaDB es usando Docker. No necesitas instalar MariaDB directamente en tu sistema.

### Instalación Rápida con Docker

#### 1. Instalar Docker

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install -y docker.io docker-compose
sudo usermod -aG docker $USER
# Reinicia sesión para aplicar cambios
```

**Windows/Mac:**
Descarga Docker Desktop desde https://www.docker.com/products/docker-desktop

#### 2. Iniciar MariaDB

```bash
# Desde la raíz del proyecto
docker compose up -d

# Verificar que está corriendo
docker compose ps
```

#### 3. Configurar la aplicación

Copia el archivo de configuración:
```bash
cp ArtemusPark/database/.env.example ArtemusPark/database/.env
```

El archivo `.env` ya tiene la configuración correcta para Docker:
```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=artemus_user
DB_PASSWORD=artemus_pass_2025
DB_NAME=artemus_db
```

#### 4. Inicializar la base de datos

```bash
# Esperar a que MariaDB esté listo (10 segundos)
sleep 10

# Crear tablas y datos iniciales
python ArtemusPark/database/Init_DB.py
```

¡Listo! Tu base de datos está funcionando en Docker.

---

## Método Alternativo: Instalación Local

Si prefieres no usar Docker, sigue estas instrucciones:

### Requisitos

- MariaDB 10.5+ o MySQL 8.0+
- Python 3.8+
- Paquetes: `mysql-connector-python`, `python-dotenv`

### 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 2. Configurar MariaDB

Crea un archivo `.env` en `ArtemusPark/database/` basado en el ejemplo:

```bash
cp ArtemusPark/database/.env.example ArtemusPark/database/.env
```

Edita el archivo `.env` con tus credenciales:

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=tu_usuario
DB_PASSWORD=tu_contraseña
DB_NAME=artemus_db
```

### 3. Crear la base de datos

Ejecuta el script de inicialización:

```bash
python -m ArtemusPark.database.Init_DB
```

O desde la raíz del proyecto:

```bash
cd ArtemusPark/database
python Init_DB.py
```

Este script creará:
- La base de datos `artemus_db`
- Todas las tablas necesarias
- Los usuarios por defecto con sus relaciones

### 4. Verificar la conexión

Puedes probar la conexión ejecutando:

```python
from ArtemusPark.database.DB_Manager import db_manager

# Probar consulta
result = db_manager.execute_query("SELECT COUNT(*) as count FROM users")
print(f"Usuarios en la base de datos: {result[0]['count']}")
```

## Estructura de la Base de Datos

### Tablas Principales

1. **users** - Usuarios del sistema
   - Admin, Maintenance, User roles
   - Información personal (nombre, DNI, teléfono, dirección)

2. **user_supervisors** - Relaciones de supervisión
   - Usuarios y sus supervisores

3. **user_assigned_sensors** - Sensores asignados
   - Sensores asignados a técnicos de mantenimiento

4. **requests** - Solicitudes del sistema
   - Solicitudes de cambio de sensor, mantenimiento, etc.

5. **temperature_measurements** - Mediciones de temperatura
6. **humidity_measurements** - Mediciones de humedad
7. **smoke_measurements** - Mediciones de humo
8. **wind_measurements** - Mediciones de viento
9. **door_status** - Estado de puertas
10. **light_measurements** - Mediciones de luz

## Configuración de MariaDB en Linux/Ubuntu

```bash
# Instalar MariaDB
sudo apt-get update
sudo apt-get install mariadb-server

# Iniciar servicio
sudo systemctl start mariadb
sudo systemctl enable mariadb

# Configurar seguridad
sudo mysql_secure_installation

# Crear usuario y base de datos
sudo mysql -u root -p

CREATE DATABASE artemus_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'artemus_user'@'localhost' IDENTIFIED BY 'tu_contraseña_segura';
GRANT ALL PRIVILEGES ON artemus_db.* TO 'artemus_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

## Configuración de MariaDB en Windows

1. Descarga e instala MariaDB desde: https://mariadb.org/download/
2. Durante la instalación, configura la contraseña de root
3. Usa HeidiSQL o MySQL Workbench para administrar la base de datos
4. Crea la base de datos `artemus_db`

## Troubleshooting

### Error: "Access denied for user"
Verifica que las credenciales en el archivo `.env` sean correctas.

### Error: "Unknown database"
Ejecuta el script `Init_DB.py` para crear la base de datos.

### Error: "Can't connect to MySQL server"

**Si usas Docker:**
```bash
# Verificar que el contenedor está corriendo
docker compose ps

# Ver logs
docker compose logs mariadb

# Reiniciar el contenedor
docker compose restart mariadb
```

**Si usas instalación local:**
```bash
sudo systemctl status mariadb  # Linux
# o
sc query MySQL  # Windows
```

### Problemas comunes con Docker

**Error: "Connection refused"**
- Espera 10-20 segundos después de iniciar el contenedor
- Verifica que el puerto 3306 no esté en uso: `sudo lsof -i :3306`

**Error: "port is already allocated"**
- Hay otro servicio usando el puerto 3306
- Detén el otro servicio o cambia el puerto en `docker-compose.yml`

**Resetear todo (⚠️ borra los datos)**
```bash
docker compose down -v  # Elimina contenedor y volumen
docker compose up -d    # Crea todo de nuevo
python ArtemusPark/database/Init_DB.py
```

## Comandos útiles de Docker

```bash
# Iniciar servicios
docker compose up -d

# Detener servicios
docker compose down

# Ver logs
docker compose logs -f mariadb

# Acceder a MariaDB
docker exec -it artemus-mariadb mariadb -u root -p
# Contraseña: artemus_root_2025

# Backup de la base de datos
docker exec artemus-mariadb mariadb-dump -u root -partemus_root_2025 artemus_db > backup.sql

# Restaurar backup
docker exec -i artemus-mariadb mariadb -u root -partemus_root_2025 artemus_db < backup.sql
```

## Notas de Seguridad

- Nunca commitees el archivo `.env` con credenciales reales
- Usa contraseñas fuertes para la base de datos
- Considera usar variables de entorno del sistema en producción
- El archivo `.env` está incluido en `.gitignore` por defecto

---

## 📚 Documentación adicional

Para una guía más detallada de Docker, incluyendo:
- Instalación paso a paso en diferentes sistemas operativos
- Configuración avanzada
- phpMyAdmin
- Producción vs Desarrollo
- Monitorización

Consulta: **`DOCKER_MARIADB_GUIDE.md`**
