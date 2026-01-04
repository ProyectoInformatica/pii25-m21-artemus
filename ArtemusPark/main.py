import asyncio
import time
import random
import flet as ft

from ArtemusPark.repository.Auth_Repository import AuthRepository
from view.pages.Login_Page import LoginPage
from view.components.Sidebar import Sidebar
from view.pages.Dashboard_Page import DashboardPage
from view.pages.Placeholder_Page import PlaceholderPage
from view.pages.History_Page import HistoryPage
from view.pages.Maintenance_Page import MaintenancePage
from view.pages.Requests_Page import RequestsPage
from view.pages.Admin_Page import AdminPage


from model.Temperature_Model import TemperatureModel
from model.Humidity_Model import HumidityModel
from model.Wind_Model import WindModel
from model.Smoke_Model import SmokeModel
from model.Door_Model import DoorModel
from model.Light_Model import LightModel


from repository.Temperature_Repository import (
    save_temperature_measurement,
    load_all_temperature_measurements,
)
from repository.Humidity_Repository import save_humidity_measurement
from repository.Wind_Repository import save_wind_measurement
from repository.Smoke_Repository import save_smoke_measurement
from repository.Door_Repository import save_door_event
from repository.Light_Repository import save_light_event

import multiprocessing


async def main(page: ft.Page):
    """Punto de entrada de la aplicación GUI."""
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

    auth_repo = AuthRepository()
    all_users = list(auth_repo.get_all_users().keys())

    async def sensor_simulation_loop():
        """Genera datos aleatorios de sensores periódicamente."""
        while True:
            now = time.time()

            temp_val = int(random.uniform(20, 32))
            temp_status = "HOT" if temp_val > 30 else "MILD"
            save_temperature_measurement(
                TemperatureModel(value=temp_val, status=temp_status, timestamp=now)
            )

            hum_val = int(random.uniform(30, 60))
            save_humidity_measurement(
                HumidityModel(value=hum_val, status="NORMAL", timestamp=now)
            )

            wind_speed = int(random.uniform(0, 25))
            wind_state = "WARNING" if wind_speed > 20 else "SAFE"
            save_wind_measurement(
                WindModel(
                    speed=wind_speed, state=wind_state, label="Norte", timestamp=now
                )
            )

            smoke_val = int(random.uniform(0, 50))
            smoke_status = "CLEAR" if smoke_val < 30 else "WARNING"
            save_smoke_measurement(
                SmokeModel(value=smoke_val, status=smoke_status, timestamp=now)
            )

            if random.random() < 0.4:
                is_open = True
                direction = "IN" if random.random() < 0.6 else "OUT"
                sim_user = random.choice(all_users) if all_users else "unknown"
                save_door_event(
                    DoorModel(
                        is_open=is_open,
                        name="Torniquete Principal",
                        direction=direction,
                        username=sim_user,
                        timestamp=now,
                    )
                )

            if random.random() < 0.9:
                is_on = random.choice([True, False])

                watts = round(random.uniform(100, 250), 2) if is_on else 0.5

                save_light_event(
                    LightModel(value=watts, status="OK", is_on=is_on, timestamp=now)
                )

            try:
                page.pubsub.send_all("refresh_dashboard")
            except Exception as e:
                print(f"Error enviando pubsub: {e}")

            await asyncio.sleep(3)

    """Iniciar simulación al empezar para tener siempre datos disponibles"""

    def seed_historical_data_if_needed(days=30):
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

            temp_val = int(random.uniform(18, 32))
            temp_status = "HOT" if temp_val > 30 else "MILD"
            save_temperature_measurement(
                TemperatureModel(value=temp_val, status=temp_status, timestamp=ts)
            )

            hum_val = int(random.uniform(30, 65))
            save_humidity_measurement(
                HumidityModel(value=hum_val, status="NORMAL", timestamp=ts)
            )

            wind_speed = int(random.uniform(0, 25))
            wind_state = "WARNING" if wind_speed > 20 else "SAFE"
            save_wind_measurement(
                WindModel(
                    speed=wind_speed, state=wind_state, label="Norte", timestamp=ts
                )
            )

            smoke_val = int(random.uniform(0, 50))
            smoke_status = "CLEAR" if smoke_val < 30 else "WARNING"
            save_smoke_measurement(
                SmokeModel(value=smoke_val, status=smoke_status, timestamp=ts)
            )

            if random.random() < 0.5:
                is_open = True
                direction = "IN" if random.random() < 0.6 else "OUT"
                sim_user = random.choice(all_users) if all_users else "unknown"
                save_door_event(
                    DoorModel(
                        is_open=is_open,
                        name="Torniquete Principal",
                        direction=direction,
                        username=sim_user,
                        timestamp=ts,
                    )
                )

            if random.random() < 0.7:
                is_on = random.choice([True, False])
                watts = round(random.uniform(100, 250), 2) if is_on else 0.5
                save_light_event(
                    LightModel(value=watts, status="OK", is_on=is_on, timestamp=ts)
                )

    seed_historical_data_if_needed()
    page.run_task(sensor_simulation_loop)

    def change_view(page_name, data=None):
        """Cambia la vista actual en el área de contenido principal."""
        current_role = session.get("role")
        current_username = session.get("username")

        display_name = current_username
        if current_username:
            all_users_data = auth_repo.get_all_users()
            user_data = all_users_data.get(current_username)
            if user_data and user_data.get("full_name"):
                display_name = user_data["full_name"]

        if page_name == "admin" and current_role != "admin":

            page.snack_bar = ft.SnackBar(ft.Text("Acceso denegado"))
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
            content_area.content = MaintenancePage(current_username=current_username)

        elif page_name == "requests":
            content_area.content = RequestsPage(
                user_role=current_role, current_username=current_username
            )

        elif page_name == "admin":
            content_area.content = AdminPage(
                user_role=current_role, current_username=current_username
            )

        content_area.update()

    def logout():
        """Cierra la sesión del usuario actual y vuelve al login."""
        print("Cerrando sesión...")
        session["role"] = None
        session["username"] = None
        page.clean()

        page.add(LoginPage(on_login_success=login_success))

    def login_success(username, role):
        """Maneja el inicio de sesión exitoso y configura la interfaz principal."""
        session["role"] = role
        session["username"] = username
        page.clean()

        sidebar = Sidebar(
            on_nav_change=change_view,
            on_logout=logout,
            user_role=role,
            username=username,
        )

        page.add(ft.Row(expand=True, spacing=0, controls=[sidebar, content_area]))
        if role == "admin":
            target_view = "admin"
        elif role == "maintenance":
            target_view = "maintenance"
        else:
            target_view = "dashboard"
        sidebar.set_active(target_view)
        change_view(target_view)

    page.add(LoginPage(on_login_success=login_success))


if __name__ == "__main__":
    multiprocessing.freeze_support()
    ft.app(target=main, assets_dir="assets")
