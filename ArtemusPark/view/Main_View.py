import flet as ft
from ArtemusPark.view.components.Sidebar import Sidebar
from ArtemusPark.view.Styles import ColorPalette

def MainView(page: ft.Page, controller):
    print(f"[MainView] Assembling application shell")

    # Content Area: Asegúrate de que expand=True está presente
    content_area = ft.Container(
        expand=True,
        padding=20,
        bgcolor=ColorPalette.BG_LIGHT,  # Esto dará el fondo gris claro
        border_radius=ft.border_radius.only(top_left=24, bottom_left=24),
        content=None  # Empezamos vacío, el controlador lo llenará
    )

    controller.set_content_area(content_area)

    # Carga inicial sin actualizar pantalla (should_update=False)
    controller.update_content_view("dashboard", should_update=False)

    return ft.Row(
        spacing=0,
        controls=[
            Sidebar(controller),
            content_area
        ],
        expand=True
    )