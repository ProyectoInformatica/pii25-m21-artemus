import flet as ft
from view.components.Sidebar import Sidebar
from view.pages.Dashboard import DashboardPage
from view.pages.Placeholder_Page import PlaceholderPage

async def main(page: ft.Page):
    page.title = "Artemus Smart Park"
    page.padding = 0

    # Área derecha (donde va el contenido)
    content_area = ft.Container(
        expand=True,
        bgcolor="#e5e7eb",
        padding=20,
        content=ft.Text("Iniciando...")
    )

    # Función que se ejecuta al clicar en el Sidebar
    def change_view(page_name):
        print(f"change_view: Switching to {page_name}")

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

    # Montamos todo
    page.add(
        ft.Row(
            expand=True,
            spacing=0,
            controls=[sidebar, content_area]
        )
    )

    # Forzamos la carga inicial
    change_view("dashboard")

if __name__ == "__main__":
    # Importante: ft.app(target=main) maneja async automáticamente
    ft.app(target=main)