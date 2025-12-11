import flet as ft
from ArtemusPark.config.Colors import AppColors


class Sidebar(ft.Container):
    def __init__(self, on_nav_change, user_role="user"):
        super().__init__()
        self.on_nav_change = on_nav_change
        self.user_role = user_role
        self.width = 260
        self.bgcolor = AppColors.BG_DARK  # Usamos tu color oscuro
        self.padding = ft.padding.symmetric(vertical=24, horizontal=20)

        self.content_column = self._build_content()
        self.content = self.content_column

    def _build_content(self):
        controls_list = [
            ft.Text("ARTEMUS", size=22, weight=ft.FontWeight.BOLD, color="white"),
            ft.Divider(height=30, color="transparent"),
        ]

        # 1. Dashboard (Todos)
        controls_list.append(self._make_button("Dashboard", "📊", "dashboard", active=True))

        # 2. Historial (Admin y Cliente)
        if self.user_role in ["admin", "client"]:
             controls_list.append(self._make_button("Historial", "🧾", "history"))

        # 3. Mantenimiento (AHORA TAMBIÉN PARA CLIENTE)
        if self.user_role in ["admin", "client"]:
            controls_list.append(self._make_button("Mantenimiento", "🛠", "maintenance"))

        # 4. Administración (EXCLUSIVO ADMIN)
        if self.user_role == "admin":
            controls_list.append(self._make_button("Administración", "⚙️", "admin"))

        controls_list.append(ft.Container(expand=True))
        controls_list.append(ft.Text(f"Perfil: {self.user_role.upper()}", color="grey", size=12))

        return ft.Column(controls=controls_list)

    def _make_button(self, text, icon, key, active=False):
        # Colores seguros usando Hex strings o AppColors
        bg_color = "#111827" if active else "transparent"  # Color oscuro si activo
        text_color = "white" if active else "#9ca3af"  # Blanco si activo, gris si no

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
        print(f"Sidebar: Navegando a {clicked_key}")

        # 1. Llamar a la función del Main para cambiar la vista
        self.on_nav_change(clicked_key)

        # 2. INTERACTIVIDAD VISUAL (Cambiar colores)
        for control in self.content_column.controls:
            # Solo modificamos si es un Botón (Container con data)
            if isinstance(control, ft.Container) and control.data is not None:
                if control.data == clicked_key:
                    # ESTE ES EL BOTÓN ACTIVO
                    control.bgcolor = "#111827"
                    control.content.controls[1].color = "white"
                else:
                    # ESTE ES UN BOTÓN INACTIVO
                    control.bgcolor = "transparent"
                    control.content.controls[1].color = "#9ca3af"

                control.update()