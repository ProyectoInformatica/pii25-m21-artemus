# Guía: MariaDB con Docker para Artemus Park

Esta guía te ayudará a configurar MariaDB usando Docker para el proyecto Artemus Park.

## 📋 Requisitos

- Docker instalado (ver instrucciones abajo)
- Docker Compose (generalmente viene con Docker)
- ~500MB de espacio libre

---

## 🐳 Instalación de Docker

### Linux (Ubuntu/Debian)

```bash
# Actualizar repositorios
sudo apt-get update

# Instalar dependencias
sudo apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release

# Agregar clave GPG oficial de Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Agregar repositorio de Docker
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Instalar Docker
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Verificar instalación
sudo docker --version
sudo docker compose version

# (Opcional) Agregar tu usuario al grupo docker para no usar sudo
sudo usermod -aG docker $USER
# Cierra sesión y vuelve a iniciar para aplicar los cambios
```

### Windows

1. Descarga Docker Desktop desde: https://www.docker.com/products/docker-desktop
2. Ejecuta el instalador y sigue las instrucciones
3. Reinicia tu computadora
4. Abre Docker Desktop y espera a que esté listo

### macOS

```bash
# Usando Homebrew
brew install --cask docker

# O descarga desde: https://www.docker.com/products/docker-desktop
```

---

## 🗄️ Configuración de MariaDB con Docker

### Paso 1: Crear el archivo docker-compose.yml

Crea un archivo llamado `docker-compose.yml` en la raíz del proyecto:

```yaml
version: '3.8'

services:
  mariadb:
    image: mariadb:11.4
    container_name: artemus-mariadb
    restart: unless-stopped
    environment:
      MARIADB_ROOT_PASSWORD: artemus_root_2025
      MARIADB_DATABASE: artemus_db
      MARIADB_USER: artemus_user
      MARIADB_PASSWORD: artemus_pass_2025
      TZ: Europe/Madrid
    ports:
      - "3306:3306"
    volumes:
      - mariadb_data:/var/lib/mysql
      - ./init-scripts:/docker-entrypoint-initdb.d:ro
    networks:
      - artemus-network
    healthcheck:
      test: ["CMD", "healthcheck.sh", "--connect", "--innodb_initialized"]
      start_period: 10s
      interval: 10s
      timeout: 5s
      retries: 3

  # (Opcional) phpMyAdmin para gestionar la base de datos vía web
  phpmyadmin:
    image: phpmyadmin/phpmyadmin:latest
    container_name: artemus-phpmyadmin
    restart: unless-stopped
    environment:
      PMA_HOST: mariadb
      PMA_PORT: 3306
      PMA_USER: root
      PMA_PASSWORD: artemus_root_2025
    ports:
      - "8080:80"
    depends_on:
      - mariadb
    networks:
      - artemus-network

volumes:
  mariadb_data:
    driver: local

networks:
  artemus-network:
    driver: bridge
```

### Paso 2: Crear directorio para scripts de inicialización

```bash
mkdir -p init-scripts
```

### Paso 3: Iniciar los contenedores

```bash
# Desde la raíz del proyecto donde está docker-compose.yml
docker compose up -d

# Verificar que los contenedores están corriendo
docker compose ps

# Ver logs
docker compose logs -f mariadb
```

### Paso 4: Configurar la aplicación

Edita el archivo `ArtemusPark/database/.env`:

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=artemus_user
DB_PASSWORD=artemus_pass_2025
DB_NAME=artemus_db
```

### Paso 5: Inicializar la base de datos

```bash
# Primero espera unos segundos a que MariaDB esté listo
sleep 10

# Ejecutar script de inicialización
python ArtemusPark/database/Init_DB.py
```

---

## 🔧 Comandos útiles de Docker

### Gestión de contenedores

```bash
# Ver contenedores activos
docker ps

# Ver todos los contenedores (incluyendo detenidos)
docker ps -a

# Detener los servicios
docker compose down

# Detener y eliminar volúmenes (⚠️ borra todos los datos)
docker compose down -v

# Reiniciar servicios
docker compose restart

# Ver logs en tiempo real
docker compose logs -f

# Ver logs de un servicio específico
docker compose logs -f mariadb
```

### Acceder a MariaDB

```bash
# Acceder al contenedor de MariaDB
docker exec -it artemus-mariadb mariadb -u root -p
# Contraseña: artemus_root_2025

# O usar el usuario de la aplicación
docker exec -it artemus-mariadb mariadb -u artemus_user -p artemus_db
# Contraseña: artemus_pass_2025
```

### Backup y Restore

```bash
# Crear backup
docker exec artemus-mariadb mariadb-dump -u root -partemus_root_2025 artemus_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Restaurar backup
docker exec -i artemus-mariadb mariadb -u root -partemus_root_2025 artemus_db < backup_archivo.sql
```

### Actualizar MariaDB

```bash
# Detener contenedores
docker compose down

# Descargar nueva imagen
docker pull mariadb:11.4

# Volver a iniciar
docker compose up -d
```

---

## 🌐 Acceso a phpMyAdmin (Opcional)

Si habilitaste phpMyAdmin en el docker-compose.yml:

1. Abre tu navegador en: http://localhost:8080
2. Usuario: `root`
3. Contraseña: `artemus_root_2025`
4. Servidor: `mariadb` (o déjalo en localhost si no funciona)

---

## 🛠️ Solución de problemas

### Error: "Connection refused"

1. Verifica que el contenedor esté corriendo:
   ```bash
   docker compose ps
   ```

2. Verifica los logs:
   ```bash
   docker compose logs mariadb
   ```

3. Asegúrate de que el puerto 3306 no esté en uso:
   ```bash
   sudo lsof -i :3306
   # Si hay otro proceso, cámbialo o cambia el puerto en docker-compose.yml
   ```

### Error: "Access denied for user"

1. Elimina el volumen y vuelve a crear el contenedor:
   ```bash
   docker compose down -v
   docker compose up -d
   ```

### Error: "Unknown database"

Ejecuta el script de inicialización:
```bash
python ArtemusPark/database/Init_DB.py
```

### Cambiar contraseñas

Si necesitas cambiar las contraseñas, modifica el `docker-compose.yml` y:

```bash
# Eliminar el contenedor y volumen
docker compose down -v

# Volver a crear
docker compose up -d

# Actualizar el archivo .env
```

---

## 💾 Persistencia de datos

Los datos de MariaDB se almacenan en un volumen Docker llamado `mariadb_data`. Esto significa que:

- ✅ Los datos persisten incluso si reinicias el contenedor
- ✅ Los datos se mantienen si actualizas la imagen de MariaDB
- ❌ Los datos se pierden si eliminas el volumen con `docker compose down -v`

Para hacer backup persistente fuera de Docker:

```bash
# Copiar datos del volumen a tu máquina
docker run --rm -v artemus-mariadb_data:/source -v $(pwd)/backup:/backup alpine tar czf /backup/mariadb_backup.tar.gz -C /source .

# Restaurar desde backup
docker run --rm -v artemus-mariadb_data:/target -v $(pwd)/backup:/backup alpine sh -c "cd /target && tar xzf /backup/mariadb_backup.tar.gz"
```

---

## 🎯 Producción vs Desarrollo

### Desarrollo (configuración actual)

- Usuario root con contraseña simple
- Puerto 3306 expuesto
- phpMyAdmin habilitado
- Logs detallados

### Producción (recomendado)

```yaml
version: '3.8'

services:
  mariadb:
    image: mariadb:11.4
    container_name: artemus-mariadb-prod
    restart: always
    environment:
      MARIADB_ROOT_PASSWORD_FILE: /run/secrets/db_root_password  # Usar secrets
      MARIADB_DATABASE: artemus_db
      MARIADB_USER_FILE: /run/secrets/db_user
      MARIADB_PASSWORD_FILE: /run/secrets/db_password
      TZ: Europe/Madrid
    ports:
      - "127.0.0.1:3306:3306"  # Solo localhost
    volumes:
      - mariadb_data:/var/lib/mysql
      - ./my.cnf:/etc/mysql/conf.d/custom.cnf:ro  # Configuración personalizada
    networks:
      - artemus-network
    secrets:
      - db_root_password
      - db_user
      - db_password
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 1G

volumes:
  mariadb_data:

networks:
  artemus-network:
    driver: bridge

secrets:
  db_root_password:
    file: ./secrets/db_root_password.txt
  db_user:
    file: ./secrets/db_user.txt
  db_password:
    file: ./secrets/db_password.txt
```

---

## 📊 Monitorización

```bash
# Ver uso de recursos
docker stats artemus-mariadb

# Ver tamaño del volumen
docker system df -v

# Limpiar contenedores y volúmenes no usados
docker system prune -a --volumes
```

---

## ✅ Checklist de verificación

Después de configurar, verifica:

- [ ] Docker está instalado y corriendo
- [ ] Contenedor `artemus-mariadb` está activo (`docker ps`)
- [ ] Archivo `.env` configurado correctamente
- [ ] Script `Init_DB.py` ejecutado sin errores
- [ ] La aplicación puede conectarse a la base de datos
- [ ] (Opcional) phpMyAdmin accesible en http://localhost:8080

¡Listo! Tu base de datos MariaDB está configurada con Docker. 🎉
