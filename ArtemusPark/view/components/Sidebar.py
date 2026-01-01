import flet as ft
from ArtemusPark.config.Colors import AppColors


class Sidebar(ft.Container):

    def __init__(self, on_nav_change, on_logout, user_role="user", username=""):
        super().__init__()
        self.on_nav_change = on_nav_change
        self.on_logout = on_logout
        self.user_role = user_role
        self.username = username

        self.width = 260
        self.bgcolor = AppColors.BG_DARK
        self.padding = ft.padding.symmetric(vertical=24, horizontal=20)

        self.content_column = self._build_content()
        self.content = self.content_column

    def _build_content(self):
        """Construye el contenido vertical de la barra lateral."""
        controls_list = [
            ft.Text(
                "ARTEMUS",
                size=22,
                weight=ft.FontWeight.BOLD,
                color="white",
                style=ft.TextStyle(font_family="RobotoCondensed", letter_spacing=1.5),
            ),
            ft.Divider(height=30, color="transparent"),
            self._make_button("Dashboard", "📊", "dashboard", active=True),
        ]

        if self.user_role in ["admin", "maintenance"]:
            controls_list.append(self._make_button("Historial", "🧾", "history"))

        if self.user_role in ["admin", "maintenance"]:
            controls_list.append(self._make_button("Mantenimiento", "🛠", "maintenance"))

        if self.user_role == "admin":
            controls_list.append(self._make_button("Administración", "⚙️", "admin"))

        controls_list.append(ft.Container(expand=True))

        controls_list.append(
            ft.Container(
                padding=ft.padding.only(top=10),
                border=ft.border.only(top=ft.border.BorderSide(1, "#374151")),
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Column(
                            spacing=2,
                            controls=[
                                ft.Text(
                                    f"{self.username.upper()} ({self.user_role.upper()})",
                                    size=12,
                                    weight=ft.FontWeight.BOLD,
                                    color="white",
                                ),
                            ],
                        ),
                        ft.IconButton(
                            icon=ft.Icons.LOGOUT_ROUNDED,
                            icon_color="#ef4444",
                            tooltip="Cerrar Sesión",
                            on_click=lambda e: self.on_logout(),
                        ),
                    ],
                ),
            )
        )

        return ft.Column(controls=controls_list)

    def _make_button(self, text, icon, key, active=False):
        """Crea un botón de navegación personalizado."""
        bg_color = "#111827" if active else "transparent"
        text_color = "white" if active else "#9ca3af"

        return ft.Container(
            data=key,
            padding=10,
            border_radius=10,
            bgcolor=bg_color,
            ink=True,
            on_click=self._handle_click,
            content=ft.Row(
                controls=[
                    ft.Text(icon, size=16),
                    ft.Text(text, size=14, color=text_color),
                ]
            ),
        )

    def _handle_click(self, e):
        """Maneja el evento de clic en un botón de navegación."""
        clicked_key = e.control.data
        self.on_nav_change(clicked_key)

        for control in self.content_column.controls:
            if isinstance(control, ft.Container) and control.data is not None:
                if control.data == clicked_key:
                    control.bgcolor = "#111827"
                    control.content.controls[1].color = "white"
                else:
                    control.bgcolor = "transparent"
                    control.content.controls[1].color = "#9ca3af"
        self.update()
