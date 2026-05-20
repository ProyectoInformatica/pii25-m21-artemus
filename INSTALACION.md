# Guía de instalación — Artemus Park

Sistema IoT de gestión inteligente de parque urbano.  
Proyecto académico — Ingeniería Informática, Universidad Europea de Madrid.

---

## Requisitos previos

| Componente | Versión mínima |
|---|---|
| Python | 3.11 o superior |
| MySQL Server | 8.0 o superior (probado con 9.x) |
| pip | incluido con Python |
| Git | cualquier versión reciente |

> En **Windows** instala Python desde [python.org](https://www.python.org/downloads/) y MySQL Community Server desde [dev.mysql.com](https://dev.mysql.com/downloads/mysql/). En **macOS** puedes usar Homebrew (`brew install python mysql`). En **Linux** usa el gestor de paquetes de tu distribución.

---

## 1. Clonar el repositorio

```bash
git clone https://github.com/ProyectoInformatica/pii25-m21-artemus.git
cd pii25-m21-artemus
```

---

## 2. Crear y activar entorno virtual

```bash
# Crear entorno virtual
python -m venv venv

# Activar (Linux / macOS)
source venv/bin/activate

# Activar (Windows CMD)
venv\Scripts\activate.bat

# Activar (Windows PowerShell)
venv\Scripts\Activate.ps1
```

---

## 3. Instalar dependencias Python

```bash
pip install -r requirements.txt
pip install mysql-connector-python
```

> `mysql-connector-python` es la librería de conexión a MySQL. No figura en `requirements.txt` pero es obligatoria.

Paquetes que se instalarán:

| Paquete | Versión |
|---|---|
| flet | 0.28.3 |
| flet-desktop | 0.28.3 |
| cryptography | 42.0.5 |
| Pillow | ≥ 11.0.0 |
| mysql-connector-python | última estable |

---

## 4. Configurar MySQL

### 4.1 Asegúrate de que MySQL está en marcha

```bash
# Linux (systemd)
sudo systemctl start mysql

# macOS (Homebrew)
brew services start mysql

# Windows — abre el servicio desde el Panel de Control o ejecuta:
net start MySQL80
```

### 4.2 Configuración de acceso esperada por la aplicación

La aplicación se conecta con estos parámetros **hardcoded** en `ArtemusPark/database/db_connection.py`:

| Parámetro | Valor |
|---|---|
| Host | `localhost` |
| Puerto | `3306` |
| Base de datos | `artemus` |
| Usuario | `root` |
| Contraseña | *(vacía)* |

Si tu instalación de MySQL tiene contraseña para `root`, edita el archivo `ArtemusPark/database/db_connection.py` y ajusta el valor de `"password"` en `DB_CONFIG`:

```python
DB_CONFIG = {
    "host": "localhost",
    "database": "artemus",
    "user": "root",
    "password": "TU_CONTRASEÑA_AQUI",   # <-- modifica esta línea
    "port": 3306,
}
```

---

## 5. Importar el esquema de base de datos

El archivo SQL incluye la sentencia `CREATE DATABASE` y **elimina y recrea todas las tablas**, así que basta con ejecutarlo una sola vez.

```bash
mysql -u root -p < ArtemusPark/database/artemus.sql
```

> Si tu usuario `root` no tiene contraseña omite la `-p`:
> ```bash
> mysql -u root < ArtemusPark/database/artemus.sql
> ```

El script crea la base de datos `artemus` con codificación `utf8mb4`, todas las tablas y datos de ejemplo (mediciones de sensores, usuarios, roles, etc.).

### Verificar la importación (opcional)

```bash
mysql -u root -e "USE artemus; SHOW TABLES;"
```

Deberías ver tablas como: `Air_Quality`, `Door`, `Humidity`, `Lighting`, `Message`, `Role`, `Sensor`, `Temperature`, `User`, `Wind`, etc.

---

## 6. Ejecutar la aplicación

Desde la **raíz del repositorio** (no desde dentro de `ArtemusPark/`):

```bash
cd ArtemusPark
python -m ArtemusPark.main
```

O bien con Flet directamente:

```bash
python -m flet run ArtemusPark/main.py
```

Al arrancar, la aplicación:
1. Se conecta al pool de conexiones MySQL (15 conexiones).
2. Ejecuta `ensure_basic_data()`: crea roles, permisos, tipos de sensor y el usuario administrador por defecto si no existen.
3. Abre la ventana de escritorio (1420 × 820 px mínimo).

---

## 7. Credenciales de acceso

### Administrador creado automáticamente al arrancar

| Campo | Valor |
|---|---|
| Usuario | `admin_aldo` |
| Contraseña | `admin123` |
| Rol | Admin (todos los permisos) |

> Este usuario se crea o actualiza con `REPLACE INTO` cada vez que arranca la aplicación, por lo que siempre estará disponible aunque la base de datos ya tuviese datos.

### Usuarios de ejemplo cargados por el SQL

El archivo `artemus.sql` incluye usuarios de demostración adicionales. Un administrador de ejemplo importado directamente por el SQL:

| Usuario | Contraseña | Rol |
|---|---|---|
| `admin_1` | `admin1` | Admin |

> Las contraseñas se almacenan como `SHA-256`. Si necesitas recuperar la contraseña de un usuario desconocido, puedes actualizarla directamente en MySQL:
> ```sql
> UPDATE artemus.User
> SET password_hash = SHA2('nueva_contraseña', 256)
> WHERE username = 'nombre_usuario';
> ```

---

## 8. Roles y permisos

| Rol | Permisos |
|---|---|
| `admin` | Todos (VIEW_DASHBOARD, VIEW_HISTORY, VIEW_REQUESTS, MANAGE_REQUESTS, VIEW_MAINTENANCE, MANAGE_SENSORS, ACCESS_ADMIN_PANEL, MANAGE_USERS, ACTIVATE_EMERGENCY) |
| `maintenance` | Permisos 1–6 (sin panel de admin ni gestión de usuarios) |
| `user` | Solo VIEW_DASHBOARD |

---

## 9. Estructura del proyecto

```
pii25-m21-artemus/
├── ArtemusPark/
│   ├── main.py                  ← Punto de entrada
│   ├── config/                  ← Constantes (colores, umbrales, sensores)
│   ├── database/
│   │   ├── artemus.sql          ← Esquema completo + datos de ejemplo
│   │   ├── tablas.sql           ← Solo estructura de tablas (sin datos)
│   │   └── db_connection.py     ← Pool MySQL y configuración de conexión
│   ├── model/                   ← Clases de datos (Temperature, Door, etc.)
│   ├── repository/              ← Acceso a base de datos (SQL)
│   ├── service/                 ← Lógica de negocio
│   ├── view/
│   │   ├── pages/               ← Pantallas completas (Login, Dashboard, Chat…)
│   │   └── components/          ← Widgets reutilizables (Sidebar, Cards…)
│   ├── assets/
│   │   ├── img/                 ← Logos e iconos
│   │   └── fonts/               ← RobotoCondensed.ttf
│   └── esp32/                   ← Scripts Arduino para sensores físicos
├── requirements.txt
└── INSTALACION.md               ← Este archivo
```

---

## 10. Resolución de problemas frecuentes

### La aplicación no arranca: error de conexión MySQL

```
DATABASE ERROR: ...
```

- Verifica que MySQL está corriendo: `mysql -u root -e "SELECT 1"`
- Comprueba que la base de datos existe: `mysql -u root -e "SHOW DATABASES LIKE 'artemus'"`
- Revisa la contraseña en `db_connection.py`

### `ModuleNotFoundError: No module named 'mysql'`

```bash
pip install mysql-connector-python
```

### `ModuleNotFoundError: No module named 'flet'`

```bash
pip install flet==0.28.3 flet-desktop==0.28.3
```

### La ventana no se abre (Linux sin entorno gráfico)

Flet es una aplicación de escritorio y requiere un entorno gráfico (X11 o Wayland). En servidores sin GUI no es posible ejecutarla directamente.

### Error al importar el SQL: `ERROR 1046 (3D000): No database selected`

El archivo `artemus.sql` ya incluye `CREATE DATABASE` y `USE artemus`. Asegúrate de ejecutarlo tal como se indica en el paso 5, sin especificar base de datos en la línea de comandos.

---

## 11. Umbrales del sistema (referencia rápida)

| Sensor | Umbral de alerta |
|---|---|
| Temperatura | > 28 °C |
| Viento (aviso) | > 20 km/h |
| Viento (crítico) | > 40 km/h |
| Humedad baja | < 20 % |
| Humedad alta | > 90 % |
| CO₂ / Humo | > 2000 ADC |
| Aforo máximo | 200 personas |
| Sensor offline | sin datos > 30 s |

---

## Equipo de desarrollo

| Rol | Nombre |
|---|---|
| Scrum Master | Pablo Piqueras |
| Product Owner | Israel Gómez |
| Desarrollador Hardware | Aldo Zamora |
| QA / Documentación | Xiaojie Hu |

Universidad Europea de Madrid — Grado en Ingeniería Informática, curso 2024/2025.
