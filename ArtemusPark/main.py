import asyncio
import time
import random
import flet as ft
from view.components.Sidebar import Sidebar
from view.pages.Dashboard import DashboardPage
from view.pages.Placeholder_Page import PlaceholderPage

# Importamos el repositorio y modelo para guardar datos reales
from repository.Temperature_Repository import save_temperature_measurement
from model.Temperature_Model import TemperatureModel


async def main(page: ft.Page):
    page.title = "Artemus Smart Park"
    page.padding = 0

    # Área derecha (donde va el contenido)
    content_area = ft.Container(
        expand=True, bgcolor="#e5e7eb", padding=20, content=ft.Text("Iniciando...")
    )

    # --- AQUÍ ESTÁ LA CLAVE: Bucle de simulación ---
    async def sensor_simulation_loop():
        """
        Esta función corre en paralelo. Genera datos y avisa al Dashboard.
        """
        print("Main: Iniciando simulación de sensores en segundo plano...")
        while True:
            # 1. Generamos un dato simulado
            dummy_temp = TemperatureModel(
                timestamp=time.time(),
                value=int(random.randint(20, 30)),  # Simulamos 20-30 ºC
                status="OK",
            )

            # 2. Guardamos en el JSON (Base de datos)
            save_temperature_measurement(dummy_temp)
            # print(f"Main: Dato guardado {dummy_temp.value}")

            # 3. ¡ENVIAMOS LA SEÑAL!
            # Esto hace que DashboardPage ejecute su método _on_message
            page.pubsub.send_all("refresh_dashboard")

            # 4. Esperamos 3 segundos antes del siguiente dato
            await asyncio.sleep(3)

    # -----------------------------------------------

    # Función que se ejecuta al clicar en el Sidebar
    def change_view(page_name):
        print(f"Main: Cambiando vista a {page_name}")
        content_area.content = None

        if page_name == "dashboard":
            content_area.content = DashboardPage()
        elif page_name == "admin":
            content_area.content = PlaceholderPage("Administración", "Config...")
        elif page_name == "maintenance":
            content_area.content = PlaceholderPage("Mantenimiento", "Sensores...")
        elif page_name == "history":
            content_area.content = PlaceholderPage("Historial", "Gráficos...")

        content_area.update()

    # Creamos la Sidebar
    sidebar = Sidebar(on_nav_change=change_view)

    # Montamos la estructura visual
    page.add(ft.Row(expand=True, spacing=0, controls=[sidebar, content_area]))

    # ARRANCAMOS EL BUCLE DE SIMULACIÓN
    page.run_task(sensor_simulation_loop)

    # Cargamos la vista inicial
    change_view("dashboard")


if __name__ == "__main__":
    ft.app(target=main)
