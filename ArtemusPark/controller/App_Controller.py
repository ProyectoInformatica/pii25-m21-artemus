import flet as ft
from ArtemusPark.model.Data_Models import SensorData


class AppController:
    def __init__(self, page: ft.Page):
        print(f"[AppController.__init__] Initializing controller")
        self.page = page
        self.content_area = ft.Container()
        self.current_view = "dashboard"

        # Datos simulados (Mock)
        self.sensor_data = SensorData(24.0, 48, 10, 85, 1245, 2000)

    def navigate(self, e):
        target = e.control.data
        print(f"[AppController.navigate] Navigating to {target}")

        self.current_view = target

        # Actualizar estado visual de la sidebar
        if hasattr(self, "sidebar_column"):
            for control in self.sidebar_column.controls:
                if isinstance(control, ft.Container):
                    is_active = control.data == target
                    control.bgcolor = "#1f2933" if is_active else ft.Colors.TRANSPARENT

                    # Acceder al texto dentro del Row para cambiar color
                    if (
                        isinstance(control.content, ft.Row)
                        and len(control.content.controls) > 1
                    ):
                        control.content.controls[1].color = (
                            "#f9fafb" if is_active else "#9ca3af"
                        )
                    control.update()

        # Cambiar el contenido de la página principal
        self.update_content_view(target)

    def set_sidebar_reference(self, sidebar_col):
        self.sidebar_column = sidebar_col

    def set_content_area(self, content_container):
        self.content_area = content_container

    def update_content_view(self, target, should_update=True):
        print(
            f"[AppController.update_content_view] Target: {target}, Should Update: {should_update}"
        )

        # Imports ajustados a tus nombres de archivo (Mayúsculas)
        from ArtemusPark.view.pages.Dashboard import DashboardPage
        from ArtemusPark.view.pages.History import HistoryPage
        from ArtemusPark.view.pages.Maintenance import MaintenancePage
        from ArtemusPark.view.pages.Admin import AdminPage

        # Lógica de cambio de vista simplificada
        if target == "dashboard":
            self.content_area.content = DashboardPage(self.sensor_data)
        elif target == "history":
            self.content_area.content = HistoryPage()
        elif target == "maintenance":
            self.content_area.content = MaintenancePage()
        elif target == "admin":
            self.content_area.content = AdminPage(self)

        if should_update:
            self.content_area.update()

    def trigger_emergency(self):
        print(f"[AppController.trigger_emergency] Emergency mode activated")
        self.page.banner = ft.Banner(
            bgcolor=ft.Colors.RED_900,
            leading=ft.Icon(
                ft.Icons.WARNING_AMBER_ROUNDED, color=ft.Colors.WHITE, size=40
            ),
            content=ft.Text(
                "ALERTA DE EVACUACIÓN ENVIADA - MODO EMERGENCIA", color=ft.Colors.WHITE
            ),
            actions=[
                ft.TextButton(
                    "Desactivar",
                    style=ft.ButtonStyle(color=ft.Colors.WHITE),
                    on_click=self.close_banner,
                )
            ],
        )
        self.page.banner.open = True
        self.page.update()

    def close_banner(self, e):
        print(f"[AppController.close_banner] Closing banner")
        self.page.banner.open = False
        self.page.update()
