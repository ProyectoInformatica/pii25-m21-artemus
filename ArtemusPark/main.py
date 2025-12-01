import flet as ft
from view.components.Sidebar import Sidebar
from view.pages.Dashboard import DashboardPage
from view.pages.Placeholder_Page import PlaceholderPage


def main(page: ft.Page):
    page.title = "Artemus Smart Park"
    page.padding = 0

    # Área derecha (donde va el contenido)
    content_area = ft.Container(
        expand=True,
        bgcolor="#e5e7eb",
        padding=20,
        content=ft.Text("Iniciando...")  # Texto temporal
    )

    # Función que se ejecuta al clicar en el Sidebar
    def change_view(page_name):
        print(f"Main: Cambiando vista a {page_name}")

        content_area.content = None  # Limpiamos

        if page_name == "dashboard":
            # PRUEBA: Si el Dashboard falla, comenta la linea de abajo y descomenta el Text
            content_area.content = DashboardPage()
            # content_area.content = ft.Text("ESTO ES EL DASHBOARD", size=30, color="black")

        elif page_name == "educational":
            content_area.content = PlaceholderPage("Zona Educativa", "Contenido...")
        elif page_name == "admin":
            content_area.content = PlaceholderPage("Administración", "Config...")
        elif page_name == "maintenance":
            content_area.content = PlaceholderPage("Mantenimiento", "Sensores...")
        elif page_name == "history":
            content_area.content = PlaceholderPage("Historial", "Gráficos...")

        content_area.update()  # IMPORTANTE: Refrescar pantalla

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
    ft.app(target=main)