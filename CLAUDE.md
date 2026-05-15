# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Artemus Park** is an IoT smart-park management system built with Python 3 and Flet (desktop GUI framework). It simulates and monitors environmental sensors (temperature, humidity, wind, air quality, lighting, doors) for an urban park, storing data in a MySQL database.

## Commands

### Run the application
```bash
cd ArtemusPark
python -m ArtemusPark.main
# OR from project root:
python -m flet run ArtemusPark/main.py
```
The app requires a running MySQL instance on `localhost:3306` with an `artemus` database (see Database Setup below).

### Install dependencies
```bash
pip install -r requirements.txt
# requirements: flet==0.28.3, flet-desktop==0.28.3, cryptography==42.0.5
```

### Lint and format
```bash
black .                                          # auto-format (CI enforces this)
flake8 . --max-line-length=88 --ignore=E203,W503  # style check
pylint $(git ls-files '*.py')                    # full lint
```

CI runs Black automatically on every push and commits the result. Run Black locally before pushing to avoid churn commits.

### Tests
The `tests/` directory is currently empty. The CI pipeline runs `pytest` but there are no test files yet.

## Architecture

The application follows a strict layered architecture inside `ArtemusPark/`:

```
main.py              ← entry point: Flet app, sensor simulation loop, routing
config/              ← static constants (colors, sensor IDs, park thresholds)
database/            ← DB connection pool (DatabaseManager), schema bootstrap
model/               ← pure data classes (TemperatureModel, DoorModel, etc.)
repository/          ← SQL access layer, one file per sensor/entity type
service/             ← business logic (Dashboard aggregation, crypto, risk calc)
view/
  pages/             ← full-page Flet Components (Login, Dashboard, Chat, Admin…)
  components/        ← reusable sub-widgets (Sidebar, SensorCard, TempChart…)
```

### Data flow
`main.py` runs an async loop every 3 seconds (`sensor_simulation_loop`) that calls `generate_sensor_snapshot()` → Repository `save_*` functions → MySQL. The UI subscribes to Flet's `page.pubsub` for `"refresh_dashboard"` events. Views pull data through Services which call Repositories; views never query the DB directly.

### Database
- **Engine:** MySQL 9.x via `mysql-connector-python` with a 15-connection pool (`DatabaseManager`).
- **Config:** hardcoded in `database/db_connection.py` — host `localhost`, db `artemus`, user `root`, password `""`.
- **Bootstrap:** `DatabaseManager.ensure_basic_data()` runs on first connection and creates roles, permissions, sensor types, the Global chat, and the default admin user. The full schema is in `database/artemus.sql`.
- **Sensor config:** loaded dynamically from the `Sensor` table at runtime; `config/Sensor_Config.py` is only the static fallback when the DB is empty.

### Database setup (first run)
```sql
CREATE DATABASE artemus CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```
Then import the schema:
```bash
mysql -u root artemus < ArtemusPark/database/artemus.sql
```
The app auto-seeds roles, permissions, and admin user on startup.

**Default admin credentials:** username `admin_soto`, password `admin123`.

### Authentication & crypto
Passwords are stored as `SHA2(password, 256)`. Each user gets an RSA-2048 key pair on first login (`Auth_Repository.ensure_keys_exist`). The private key is encrypted with Fernet (AES) derived from the user's password via PBKDF2 and held in memory for the session — used by `Chat_Page` for E2E encrypted private messages.

### Role/permission system
Three roles: `admin` (all 9 permissions), `maintenance` (permissions 1–6), `user` (VIEW_DASHBOARD only). Permission strings are loaded from `Role_Permission` table and passed down as a `permissions: list[str]` to every page that needs access control.

### Catastrophe mode
`DashboardService._catastrophe_active` is a class-level flag. When active, `main.py` sets `page.bgcolor = RED_900` and publishes `"catastrophe_mode"` via pubsub.

## Git conventions (from README)

**Branch format:**
```
feature/issueX_Y_[username]_[brief_description]
```

**PR naming:** must match the exact Trello task name.

PRs target the `development` branch. CI runs on pushes/PRs to `development`.
