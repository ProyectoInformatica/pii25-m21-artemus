import flet as ft
from ArtemusPark.config.Colors import AppColors


class Sidebar(ft.Container):
    # 1. AÑADIMOS 'on_logout' AL CONSTRUCTOR
    def __init__(self, on_nav_change, on_logout, user_role="user"):
        super().__init__()
        self.on_nav_change = on_nav_change
        self.on_logout = on_logout  # Guardamos la función de logout
        self.user_role = user_role

        self.width = 260
        self.bgcolor = AppColors.BG_DARK
        self.padding = ft.padding.symmetric(vertical=24, horizontal=20)

        self.content_column = self._build_content()
        self.content = self.content_column

    def _build_content(self):
        controls_list = [
            ft.Text("ARTEMUS", size=22, weight=ft.FontWeight.BOLD, color="white"),
            ft.Divider(height=30, color="transparent"),
            self._make_button("Dashboard", "📊", "dashboard", active=True),
        ]

        # Lógica de botones según rol (Igual que antes)
        if self.user_role in ["admin", "maintenance"]:
            controls_list.append(self._make_button("Historial", "🧾", "history"))

        if self.user_role in ["admin", "maintenance"]:
            controls_list.append(self._make_button("Mantenimiento", "🛠", "maintenance"))

        if self.user_role == "admin":
            controls_list.append(self._make_button("Administración", "⚙️", "admin"))

        # Espaciador para empujar el footer hacia abajo
        controls_list.append(ft.Container(expand=True))

        # --- NUEVO FOOTER CON PERFIL Y LOGOUT ---
        controls_list.append(
            ft.Container(
                padding=ft.padding.only(top=10),
                # Una línea sutil para separar
                border=ft.border.only(top=ft.border.BorderSide(1, "#374151")),
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        # Info del Usuario
                        ft.Column(
                            spacing=2,
                            controls=[
                                ft.Text("Perfil:", size=10, color="#9ca3af"),
                                ft.Text(
                                    self.user_role.upper(),
                                    size=12,
                                    weight=ft.FontWeight.BOLD,
                                    color="white",
                                ),
                            ],
                        ),
                        # Botón de Logout
                        ft.IconButton(
                            icon=ft.Icons.LOGOUT_ROUNDED,
                            icon_color="#ef4444",  # Rojo suave
                            tooltip="Cerrar Sesión",
                            on_click=lambda e: self.on_logout(),  # Llamamos a la función
                        ),
                    ],
                ),
            )
        )

        return ft.Column(controls=controls_list)

    def _make_button(self, text, icon, key, active=False):
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
