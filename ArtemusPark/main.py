import asyncio
import time
import random
import flet as ft

# Asegúrate de ajustar los imports según tu estructura de carpetas real
# Si "ArtemusPark" es tu carpeta raíz, mantén el prefijo.
from view.pages.Login_Page import LoginPage
from view.components.Sidebar import Sidebar
from view.pages.Dashboard_Page import DashboardPage
from view.pages.Placeholder_Page import PlaceholderPage

# --- IMPORTS DE MODELOS ---
from model.Temperature_Model import TemperatureModel
from model.Humidity_Model import HumidityModel
from model.Wind_Model import WindModel
from model.Smoke_Model import SmokeModel
from model.Door_Model import DoorModel
from model.Light_Model import LightModel

# --- IMPORTS DE REPOSITORIOS ---
from repository.Temperature_Repository import save_temperature_measurement
from repository.Humidity_Repository import save_humidity_measurement
from repository.Wind_Repository import save_wind_measurement
from repository.Smoke_Repository import save_smoke_measurement
from repository.Door_Repository import save_door_event
from repository.Light_Repository import save_light_event

import multiprocessing


async def main(page: ft.Page):
    page.title = "Artemus Smart Park"
    page.padding = 0
    page.bgcolor = "#e5e7eb"
    page.fonts = {"RobotoCondensed": "/fonts/RobotoCondensed.ttf"}
    page.window.icon = "/img/logo_pequenio.png"

    session = {"role": None}
    content_area = ft.Container(expand=True, padding=0)

    # ---------------------------------------------------------
    # TAREA DE FONDO: SIMULACIÓN DE DATOS
    # ---------------------------------------------------------
    async def sensor_simulation_loop():
        """Genera datos aleatorios cada 3s respetando tus Modelos"""
        while True:
            now = time.time()

            # 1. Temperatura
            # Modelo: value (int), status (str), timestamp (float)
            temp_val = int(random.uniform(20, 32))
            temp_status = "HOT" if temp_val > 30 else "MILD"
            save_temperature_measurement(
                TemperatureModel(value=temp_val, status=temp_status, timestamp=now)
            )

            # 2. Humedad
            # Modelo: value (int), status (str), timestamp
            hum_val = int(random.uniform(30, 60))
            save_humidity_measurement(
                HumidityModel(value=hum_val, status="NORMAL", timestamp=now)
            )

            # 3. Viento
            # Modelo: speed (int), state (str), label (str), timestamp
            wind_speed = int(random.uniform(0, 25))
            wind_state = "WARNING" if wind_speed > 20 else "SAFE"
            save_wind_measurement(
                WindModel(
                    speed=wind_speed, state=wind_state, label="Norte", timestamp=now
                )
            )

            # 4. Calidad Aire (Smoke)
            # Modelo: value (int), status (str), timestamp
            smoke_val = int(random.uniform(0, 50))
            smoke_status = "CLEAR" if smoke_val < 30 else "WARNING"
            save_smoke_measurement(
                SmokeModel(value=smoke_val, status=smoke_status, timestamp=now)
            )

            # 5. Eventos Aleatorios (Aumentamos probabilidad para ver movimiento)
            if random.random() < 0.4:
                if random.choice([True, False]):
                    # --- SIMULACIÓN DE PUERTA (AFORO) ---
                    is_open = True  # Asumimos que se abre para que pase alguien

                    # Decidimos aleatoriamente si entra o sale
                    # Damos más peso a entrar (60%) para que el aforo suba poco a poco
                    direction = "IN" if random.random() < 0.6 else "OUT"

                    save_door_event(
                        DoorModel(
                            is_open=is_open,
                            name="Torniquete Principal",
                            direction=direction,  # <--- Pasamos la dirección
                            timestamp=now,
                        )
                    )
                else:
                    # Luces (Sin cambios)
                    is_on = random.choice([True, False])
                    save_light_event(
                        LightModel(value=100, status="OK", is_on=is_on, timestamp=now)
                    )

            # ¡Avisar al Dashboard!
            try:
                page.pubsub.send_all("refresh_dashboard")
            except Exception as e:
                print(f"Error enviando pubsub: {e}")

            await asyncio.sleep(3)

    # ---------------------------------------------------------
    # NAVEGACIÓN Y LOGIN
    # ---------------------------------------------------------
    def change_view(page_name):
        # ... (Tu código de change_view se mantiene igual) ...
        current_role = session.get("role")

        if page_name == "admin" and current_role != "admin":
            return

        content_area.content = None

        if page_name == "dashboard":
            content_area.content = DashboardPage(user_role=current_role)
        elif page_name == "admin":
            content_area.content = PlaceholderPage(
                "Administración", "Configuración del sistema"
            )
        elif page_name == "maintenance":
            content_area.content = PlaceholderPage(
                "Mantenimiento", "Estado de sensores"
            )
        elif page_name == "history":
            content_area.content = PlaceholderPage("Historial", "Gráficas detalladas")

        content_area.update()

    # --- NUEVA FUNCIÓN LOGOUT ---
    def logout():
        print("Cerrando sesión...")
        session["role"] = None  # Borramos el rol
        page.clean()  # Limpiamos toda la interfaz
        # Volvemos a mostrar el Login
        page.add(LoginPage(on_login_success=login_success))

    def login_success(role):
        session["role"] = role
        page.clean()

        # Nota: La tarea de simulación sigue corriendo en segundo plano,
        # lo cual está bien para este prototipo.
        if not hasattr(page, "simulation_started"):
            page.run_task(sensor_simulation_loop)
            page.simulation_started = True

        # --- AQUÍ CONECTAMOS EL LOGOUT ---
        sidebar = Sidebar(
            on_nav_change=change_view,
            on_logout=logout,  # <--- Pasamos la función nueva
            user_role=role,
        )

        page.add(ft.Row(expand=True, spacing=0, controls=[sidebar, content_area]))
        change_view("dashboard")

    page.add(LoginPage(on_login_success=login_success))


if __name__ == "__main__":
    multiprocessing.freeze_support()
    ft.app(target=main,assets_dir="assets")
