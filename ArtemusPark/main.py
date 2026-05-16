import asyncio
import time
import multiprocessing
import flet as ft
from ArtemusPark.repository.Auth_Repository import AuthRepository
from ArtemusPark.repository.Requests_Repository import RequestsRepository
from ArtemusPark.config.Thresholds_Config import (
    TEMP_THRESHOLD,
    MQ_THRESHOLD,
    WIND_WARNING_THRESHOLD_KMH,
    HUMIDITY_LOW_THRESHOLD,
    HUMIDITY_HIGH_THRESHOLD,
    MAX_OCCUPANCY,
    SENSOR_ONLINE_WINDOW_SECONDS,
)


from ArtemusPark.view.pages.Login_Page import LoginPage
from ArtemusPark.view.components.Sidebar import Sidebar
from ArtemusPark.view.pages.Dashboard_Page import DashboardPage
from ArtemusPark.view.pages.Placeholder_Page import PlaceholderPage
from ArtemusPark.view.pages.History_Page import HistoryPage
from ArtemusPark.view.pages.Maintenance_Page import MaintenancePage
from ArtemusPark.view.pages.Requests_Page import RequestsPage
from ArtemusPark.view.pages.Admin_Page import AdminPage
from ArtemusPark.view.pages.Chat_Page import ChatPage
from ArtemusPark.view.pages.Profile_Page import ProfilePage


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

    async def monitor_loop():
        """Monitors real sensor data and sends critical alerts via chat."""
        from ArtemusPark.repository.Chat_Repository import ChatRepository

        chat_repo = ChatRepository()
        requests_repo = RequestsRepository()
        system_dni = "12345678X"
        last_alert_times = {
            "temperature": 0,
            "wind": 0,
            "air_quality": 0,
            "humidity_low": 0,
            "humidity_high": 0,
            "occupancy": 0,
        }
        ALERT_COOLDOWN = 20

        while True:
            now = time.time()
            try:
                data = service.get_latest_sensor_data()
                if data:
                    def fresh(ts_key):
                        return now - data.get(ts_key, 0) < SENSOR_ONLINE_WINDOW_SECONDS

                    alert_checks = [
                        (
                            "temperature",
                            fresh("temperature_ts") and data.get("temperature", 0) > TEMP_THRESHOLD,
                            f"⚠️ ALERTA CRÍTICA: Temperatura elevada ({data['temperature']}ºC) en sector principal.",
                            "INCIDENT_TEMPERATURE",
                        ),
                        (
                            "wind",
                            fresh("wind_ts") and data.get("wind", 0) > WIND_WARNING_THRESHOLD_KMH,
                            f"⚠️ ALERTA CRÍTICA: Vientos fuertes ({data['wind']} km/h) detectados.",
                            "INCIDENT_WIND",
                        ),
                        (
                            "air_quality",
                            fresh("air_quality_ts") and data.get("air_quality", 0) > MQ_THRESHOLD,
                            f"⚠️ ALERTA CRÍTICA: Calidad del aire deficiente (CO₂: {data['air_quality']}).",
                            "INCIDENT_AIR_QUALITY",
                        ),
                        (
                            "humidity_low",
                            fresh("humidity_ts") and 0 < data.get("humidity", 0) < HUMIDITY_LOW_THRESHOLD,
                            f"⚠️ ALERTA CRÍTICA: Humedad muy baja ({data['humidity']}%) — riesgo de incendio o sequía.",
                            "INCIDENT_HUMIDITY_LOW",
                        ),
                        (
                            "humidity_high",
                            fresh("humidity_ts") and data.get("humidity", 0) > HUMIDITY_HIGH_THRESHOLD,
                            f"⚠️ ALERTA CRÍTICA: Humedad muy alta ({data['humidity']}%) — riesgo sanitario.",
                            "INCIDENT_HUMIDITY_HIGH",
                        ),
                        (
                            "occupancy",
                            fresh("occupancy_ts") and data.get("occupancy", 0) > MAX_OCCUPANCY,
                            f"⚠️ ALERTA CRÍTICA: Aforo superado ({data['occupancy']} personas). Límite: {MAX_OCCUPANCY}.",
                            "INCIDENT_OCCUPANCY",
                        ),
                    ]
                    for key, condition, alert_msg, incident_type in alert_checks:
                        if condition and now - last_alert_times[key] > ALERT_COOLDOWN:
                            try:
                                chat_repo.send_message(1, system_dni, alert_msg)
                                page.pubsub.send_all("new_chat_message")
                                page.pubsub.send_all({"topic": "bot_alert"})
                                created_incident = requests_repo.create_system_incident(
                                    system_dni, alert_msg, incident_type
                                )
                                if created_incident:
                                    page.pubsub.send_all({"topic": "requests_updated"})
                                last_alert_times[key] = now
                            except Exception as chat_err:
                                print(f"Error enviando alerta: {chat_err}")
            except Exception as e:
                print(f"Error in monitor loop: {e}")

            try:
                page.pubsub.send_all("refresh_dashboard")
            except Exception as e:
                print(f"Error sending pubsub: {e}")

            await asyncio.sleep(3)

    page.run_task(monitor_loop)

    def change_view(page_name, data=None):
        """Changes the current view in the main content area."""
        current_role = session.get("role")
        current_username = session.get("username")

        display_name = current_username
        if current_username:
            user_data = auth_repo.get_user_by_username(current_username)
            if user_data and user_data.get("full_name"):
                display_name = user_data["full_name"]

        content_area.content = None

        if page_name == "dashboard":
            content_area.content = DashboardPage(
                user_name=display_name,
                user_role=current_role,
                on_navigate=change_view,
                permissions=session.get("permissions", []),
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
            if current_role == "admin":
                content_area.content = AdminPage(
                    user_role=current_role,
                    current_username=current_username,
                    permissions=session.get("permissions", []),
                )
            else:
                content_area.content = ProfilePage(username=current_username)

        elif page_name == "chat":
            content_area.content = ChatPage(
                current_username=current_username,
                current_user_role=current_role,
                permissions=session.get("permissions", []),
                private_key=session.get("private_key"),
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

    def login_success(username, role, password):
        """Handles successful login and configures the main interface."""
        print(f"Login exitoso: {username} ({role})")

        # Asegurar que tiene llaves RSA (migración para usuarios viejos)
        pub_key, priv_enc = auth_repo.ensure_keys_exist(username, password)

        # Desencriptar llave privada para la sesión actual
        from ArtemusPark.service.Crypto_Service import CryptoService

        private_key = CryptoService.decrypt_private_key(priv_enc, password)

        permissions = auth_repo.get_user_permissions(username)
        session["role"] = role
        session["username"] = username
        session["permissions"] = permissions
        session["private_key"] = private_key  # Llave viva en memoria durante la sesión

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
