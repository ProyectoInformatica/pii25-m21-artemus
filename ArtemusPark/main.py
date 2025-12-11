import asyncio
import time
import random
import flet as ft

from ArtemusPark.view.pages.Login_Page import LoginPage
from view.components.Sidebar import Sidebar
from view.pages.Dashboard_Page import DashboardPage
from view.pages.Placeholder_Page import PlaceholderPage

# Importamos el repositorio y modelo para guardar datos reales
from repository.Temperature_Repository import save_temperature_measurement
from model.Temperature_Model import TemperatureModel


async def main(page: ft.Page):
    page.title = "Artemus Smart Park"
    page.padding = 0
    page.bgcolor = "#e5e7eb"

    # 1. ESTADO DE SESIÓN
    session = {"role": None}

    # 2. CONTENEDOR PRINCIPAL (Se usará después del login)
    content_area = ft.Container(
        expand=True, bgcolor="#e5e7eb", padding=20, content=ft.Text("Cargando...")
    )

    # ---------------------------------------------------------
    # A. TAREA DE FONDO: SIMULACIÓN DE SENSORES
    # ---------------------------------------------------------
    async def sensor_simulation_loop():
        """Genera datos cada 3s para que el Dashboard se mueva"""
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
    # ---------------------------------------------------------
    # B. LÓGICA DE NAVEGACIÓN Y PERMISOS
    # ---------------------------------------------------------
    def change_view(page_name):
        current_role = session["role"]
        print(f"Navegando a {page_name} como {current_role}")

        # --- PROTECCIÓN DE SEGURIDAD --

        # 1. Admin: Solo para admin (Sin cambios)
        if page_name == "admin" and current_role != "admin":
            show_error("🚫 Acceso denegado: Solo administradores")
            return

        # 2. Maintenance: AHORA PERMITIDO PARA ADMIN Y CLIENTE
        # Cambiamos la condición para que deje pasar si eres admin O cliente
        if page_name == "maintenance" and current_role not in ["admin", "client"]:
            show_error("🚫 Acceso denegado: Área técnica restringida")
            return

        # 3. History: Solo Admin y Cliente (Sin cambios)
        if page_name == "history" and current_role == "user":
            show_error("🔒 Acceso denegado: Función para Clientes")
            return

        # --- CAMBIO DE VISTA ---
        content_area.content = None

        if page_name == "dashboard":
            content_area.content = DashboardPage()
        elif page_name == "admin":
            content_area.content = PlaceholderPage(
                "Administración", "Configuración de sistema..."
            )
        elif page_name == "maintenance":
            content_area.content = PlaceholderPage(
                "Mantenimiento", "Estado de sensores..."
            )
        elif page_name == "history":
            content_area.content = PlaceholderPage(
                "Historial", "Gráficos detallados..."
            )

        content_area.update()

    def show_error(msg):
        page.snack_bar = ft.SnackBar(content=ft.Text(msg), bgcolor="red")
        page.snack_bar.open = True
        page.update()

    # ---------------------------------------------------------
    # C. LÓGICA DE LOGIN EXITOSO
    # ---------------------------------------------------------
    def login_success(role):
        """Se ejecuta cuando el usuario entra correctamente"""
        session["role"] = role

        # 1. Limpiamos el Login de la pantalla
        page.clean()

        # 2. Creamos la Sidebar con los permisos de ese rol
        sidebar = Sidebar(on_nav_change=change_view, user_role=role)

        # 3. Montamos la aplicación real
        page.add(ft.Row(expand=True, spacing=0, controls=[sidebar, content_area]))

        # 4. Cargamos el Dashboard
        change_view("dashboard")

    # ---------------------------------------------------------
    # D. ARRANQUE
    # ---------------------------------------------------------

    # 1. Arrancar el motor de datos (invisible)
    page.run_task(sensor_simulation_loop)

    # 2. Mostrar SOLAMENTE la pantalla de Login al principio
    page.add(LoginPage(on_login_success=login_success))


if __name__ == "__main__":
    ft.app(target=main)
