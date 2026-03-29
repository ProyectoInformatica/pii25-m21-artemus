import asyncio
import time
import random
import multiprocessing
import flet as ft
from ArtemusPark.repository.Auth_Repository import AuthRepository
from ArtemusPark.repository.Temperature_Repository import (
    save_temperature_measurement,
    load_all_temperature_measurements,
)
from ArtemusPark.repository.Humidity_Repository import save_humidity_measurement
from ArtemusPark.repository.Wind_Repository import save_wind_measurement
from ArtemusPark.repository.Smoke_Repository import save_smoke_measurement
from ArtemusPark.repository.Door_Repository import save_door_event
from ArtemusPark.repository.Light_Repository import save_light_event


from ArtemusPark.config.Sensor_Config import SENSOR_CONFIG


from ArtemusPark.model.Temperature_Model import TemperatureModel
from ArtemusPark.model.Humidity_Model import HumidityModel
from ArtemusPark.model.Wind_Model import WindModel
from ArtemusPark.model.Smoke_Model import SmokeModel
from ArtemusPark.model.Door_Model import DoorModel
from ArtemusPark.model.Light_Model import LightModel


from ArtemusPark.view.pages.Login_Page import LoginPage
from ArtemusPark.view.components.Sidebar import Sidebar
from ArtemusPark.view.pages.Dashboard_Page import DashboardPage
from ArtemusPark.view.pages.Placeholder_Page import PlaceholderPage
from ArtemusPark.view.pages.History_Page import HistoryPage
from ArtemusPark.view.pages.Maintenance_Page import MaintenancePage
from ArtemusPark.view.pages.Requests_Page import RequestsPage
from ArtemusPark.view.pages.Admin_Page import AdminPage


def generate_sensor_snapshot(timestamp: float, all_users: list):
    """Generates and saves a data snapshot for all configured sensors."""

    for sensor in SENSOR_CONFIG.get("temperature", []):
        temp_val = int(random.uniform(18, 32))
        temp_status = "HOT" if temp_val > 30 else "MILD"
        save_temperature_measurement(
            TemperatureModel(
                value=temp_val,
                status=temp_status,
                timestamp=timestamp,
                sensor_id=sensor["id"],
                name=sensor["name"],
            )
        )

    for sensor in SENSOR_CONFIG.get("humidity", []):
        hum_val = int(random.uniform(30, 65))
        save_humidity_measurement(
            HumidityModel(
                value=hum_val,
                status="NORMAL",
                timestamp=timestamp,
                sensor_id=sensor["id"],
                name=sensor["name"],
            )
        )

    for sensor in SENSOR_CONFIG.get("wind", []):
        wind_speed = int(random.uniform(0, 25))
        wind_state = "WARNING" if wind_speed > 20 else "SAFE"
        save_wind_measurement(
            WindModel(
                speed=wind_speed,
                state=wind_state,
                sensor_id=sensor["id"],
                name=sensor["name"],
                timestamp=timestamp,
            )
        )

    for sensor in SENSOR_CONFIG.get("smoke", []):
        smoke_val = int(random.uniform(0, 50))
        smoke_status = "CLEAR" if smoke_val < 30 else "WARNING"
        save_smoke_measurement(
            SmokeModel(
                value=smoke_val,
                status=smoke_status,
                timestamp=timestamp,
                sensor_id=sensor["id"],
                name=sensor["name"],
            )
        )

    for sensor in SENSOR_CONFIG.get("door", []):
        if random.random() < 0.45:
            is_open = True
            direction = "IN" if random.random() < 0.6 else "OUT"
            sim_user = random.choice(all_users) if all_users else "unknown"
            save_door_event(
                DoorModel(
                    is_open=is_open,
                    sensor_id=sensor["id"],
                    name=sensor["name"],
                    direction=direction,
                    username=sim_user,
                    timestamp=timestamp,
                )
            )

    for sensor in SENSOR_CONFIG.get("light", []):
        if random.random() < 0.8:
            is_on = random.choice([True, False])
            watts = round(random.uniform(100, 250), 2) if is_on else 0.5
            save_light_event(
                LightModel(
                    value=watts,
                    status="OK",
                    is_on=is_on,
                    timestamp=timestamp,
                    sensor_id=sensor["id"],
                    name=sensor["name"],
                )
            )


async def main(page: ft.Page):
    """Application main GUI entry point."""
    page.title = "Artemus Park"
    page.window.width = 1420
    page.window.height = 820
    page.padding = 0
    page.bgcolor = "#e5e7eb"
    page.fonts = {"RobotoCondensed": "/fonts/RobotoCondensed.ttf"}
    page.window.icon = "/img/logo_pequenio.png"
    page.window.min_width = 1420
    page.window.min_height = 800

    session = {"role": None, "username": None}
    content_area = ft.Container(expand=True, padding=0)

    from ArtemusPark.service.Dashboard_Service import DashboardService
    service = DashboardService()
    
    auth_repo = AuthRepository()
    all_users = list(auth_repo.get_all_users().keys())

    async def sensor_simulation_loop():
        """Periodically generates random sensor data."""
        while True:
            now = time.time()
            try:
                generate_sensor_snapshot(now, all_users)
            except Exception as e:
                print(f"Error in sensor simulation: {e}")

            try:
                page.pubsub.send_all("refresh_dashboard")
            except Exception as e:
                print(f"Error sending pubsub: {e}")

            await asyncio.sleep(3)

    def seed_historical_data_if_needed(days=30):
        """Seeds historical data if the database is empty or outdated."""
        now = time.time()
        temps = load_all_temperature_measurements()
        if temps:
            min_ts = min(
                item.get("timestamp", now) for item in temps if isinstance(item, dict)
            )
            if min_ts <= now - (days * 86400):
                return

        for day in range(days, 0, -1):
            ts = now - (day * 86400) + random.uniform(0, 86000)
            generate_sensor_snapshot(ts, all_users)

    page.run_task(sensor_simulation_loop)
    seed_historical_data_if_needed()

    def change_view(page_name, data=None):
        """Changes the current view in the main content area."""
        current_role = session.get("role")
        current_username = session.get("username")

        display_name = current_username
        if current_username:
            user_data = auth_repo.get_user_by_username(current_username)
            if user_data and user_data.get("full_name"):
                display_name = user_data["full_name"]

        if page_name == "admin" and current_role != "admin":

            page.snack_bar = ft.SnackBar(ft.Text("Access Denied"))
            page.snack_bar.open = True
            page.update()
            return

        content_area.content = None

        if page_name == "dashboard":
            content_area.content = DashboardPage(
                user_name=display_name, user_role=current_role, on_navigate=change_view
            )

        elif page_name == "history":
            content_area.content = HistoryPage()

        elif page_name == "maintenance":
            content_area.content = MaintenancePage(
                current_username=current_username, user_role=current_role
            )

        elif page_name == "requests":
            content_area.content = RequestsPage(
                user_role=current_role, current_username=current_username
            )

        elif page_name == "admin":
            content_area.content = AdminPage(
                user_role=current_role, current_username=current_username
            )

        content_area.update()

    def on_message(message):
        if message == "catastrophe_mode":
            page.bgcolor = ft.Colors.RED_900
            page.update()
        elif message == "normal_mode":
            page.bgcolor = "#e5e7eb"
            page.update()

    async def logout():
        """Logs out the current user and returns to login page safely."""
        print("Iniciando cierre de sesión...")
        
        try:
            # 1. Limpiar subscripciones y re-suscribir el manejador de la página
            page.pubsub.unsubscribe_all()
            page.pubsub.subscribe(on_message)
            
            # 2. Limpiar sesión
            session["role"] = None
            session["username"] = None
            
            # 3. Limpieza total de la UI (Controles y Overlays)
            page.controls.clear()
            page.overlay.clear()
            
            # 4. Re-añadir Login
            page.add(LoginPage(on_login_success=login_success))
            page.update()
            print("Logout completado con éxito. UI lista.")
        except Exception as e:
            print(f"Error crítico durante el logout: {e}")
            page.clean()
            page.add(LoginPage(on_login_success=login_success))
            page.update()

    def login_success(username, role):
        """Handles successful login and configures the main interface."""
        print(f"Login exitoso: {username} ({role})")
        permissions = auth_repo.get_user_permissions(username)
        session["role"] = role
        session["username"] = username
        session["permissions"] = permissions
        
        # Limpiamos antes de añadir la nueva interfaz
        page.controls.clear()
        page.overlay.clear()

        sidebar = Sidebar(
            on_nav_change=change_view,
            on_logout=logout,
            user_role=role,
            username=username,
            permissions=permissions,
        )

        page.add(ft.Row(expand=True, spacing=0, controls=[sidebar, content_area]))
        
        target_view = "dashboard"
        if role == "admin":
            target_view = "admin"
        elif role == "maintenance":
            target_view = "maintenance"
            
        sidebar.set_active(target_view)
        change_view(target_view)
        page.update()

    # Suscribir manejador inicial
    page.pubsub.subscribe(on_message)

    if service.is_catastrophe_mode():
        page.bgcolor = ft.Colors.RED_900

    page.add(LoginPage(on_login_success=login_success))


if __name__ == "__main__":
    multiprocessing.freeze_support()
    ft.app(target=main, assets_dir="assets")

