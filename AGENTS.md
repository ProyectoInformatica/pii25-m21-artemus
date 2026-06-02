# Artemus Park IoT System - Agent Guidance

## Setup & Execution
- **Run the application**: `python ArtemusPark/main.py` (requires activated venv)
- **Dependencies**: `pip install -r requirements.txt` (flet & flet-desktop)
- **Virtual environment**: Already exists at `.venv`; activate with `source .venv/bin/activate`

## Development Workflow
- **Branch naming**: `feature/issueX_Y_[usuario]_[descripcion_breve]` (e.g., `feature/issue3_Y_Israel_sensor_humedad`)
- **PR naming**: Must exactly match Trello task name (e.g., "HU3 - 3: Establecer políticas de commits y revisiones")
- **Commits**: Follow Scrum practices; request review from Scrum Master before merging

## Code Quality
- **Linting/formatting**: CI runs black (autoformat), flake8 (style), pylint on push
- **Local check**: Run `black .` then `flake8 . --max-line-length=88 --ignore=E203,W503` then `pylint $(git ls-files '*.py')`
- **Important**: Black auto-commits changes in CI if diff exists

## Project Structure and Components
- **Entry point**: `ArtemusPark/main.py` - GUI application with sensor simulation loop
- **Core directories**:
  - `ArtemusPark/config/` - Configuration files (sensor, park, colors, wind)
  - `ArtemusPark/controller/` - MVC controllers for each sensor type
  - `ArtemusPark/model/` - Data models for sensors and entities
  - `ArtemusPark/repository/` - Data access layer for SQLite persistence
  - `ArtemusPark/service/` - Business logic services (metrics, risk assessment)
  - `ArtemusPark/view/` - Flet-based UI components:
    - `view/pages/` - Main application views (Dashboard, Admin, etc.)
    - `view/components/` - Reusable UI widgets (charts, cards, panels)
  - `ArtemusPark/bbdd/` - Database connection and initialization
  - `assets/` - GUI resources (icons, fonts, images)
- **Architecture**: MVC-like pattern with separation of concerns
- **Sensor simulation**: Async loop in main.py generates random data every 3 seconds
- **Role-based access**: Login determines accessible views (admin/maintenance/user)
- **PubSub system**: Flet's pubsub for cross-component messaging (`refresh_dashboard`)
- **Data persistence**: SQLite via repository layer
- **Historical data**: Seeded on startup if DB empty/older than 30 days

## Data & Sensors
- **Simulated sensors**: Temperature, humidity, wind, smoke, door, light
- **Config location**: Sensor IDs/names in `ArtemusPark/config/Sensor_Config.py`
- **Measurement flow**: Controllers → Repositories → SQLite via models

## Testing
- **Test location**: `tests/` directory (currently empty)
- **No test framework configured**: Add tests following project patterns if needed

## Common Gotchas
- **Multiprocessing**: `main.py` uses `multiprocessing.freeze_support()` for packaging
- **Assets**: GUI assets in `assets/` directory (icons, fonts)
- **Environment**: No special env vars needed; runs standalone with simulated data

## Preserved from Existing Guidelines
- **Git workflow**: Branch/PR naming conventions from README strictly enforced
- **Scrum**: 2-week sprints, Trello for task management, sprint review Fridays
- **Credentials**: See `credentials.md` for any needed sensitive information (not in repo)