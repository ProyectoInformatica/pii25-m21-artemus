import flet as ft


class Sidebar(ft.Container):
    def __init__(self, on_nav_change):
        super().__init__()
        self.on_nav_change = on_nav_change  # La función que viene del Main
        self.width = 260
        self.bgcolor = "#131921"
        self.padding = ft.padding.symmetric(vertical=24, horizontal=20)
        self.content = self._build_content()

    def _build_content(self):
        return ft.Column(
            controls=[
                ft.Text("ARTEMUS", size=22, weight=ft.FontWeight.BOLD, color="white"),
                ft.Divider(height=30, color="transparent"),

                # Botones creados directamente
                self._make_button("Dashboard", "📊", "dashboard", active=True),
                self._make_button("Educativa", "📚", "educational"),
                self._make_button("Administración", "⚙️", "admin"),
                self._make_button("Mantenimiento", "🛠", "maintenance"),
                self._make_button("Historial", "🧾", "history"),

                ft.Container(expand=True),
                ft.Text("v0.1", color="grey")
            ]
        )

    def _make_button(self, text, icon, key, active=False):
        # Esta es la misma estructura que tu prueba_click.py
        return ft.Container(
            data=key,  # La clave para saber qué botón es
            padding=10,
            border_radius=10,
            bgcolor="#111827" if active else "transparent",

            # LAS DOS CLAVES QUE HICIERON FUNCIONAR TU PRUEBA:
            ink=True,
            on_click=self._handle_click,

            content=ft.Row(
                controls=[
                    ft.Text(icon, size=16),
                    ft.Text(text, size=14, color="white" if active else "#9ca3af")  # Gris si no está activo
                ]
            )
        )

    def _handle_click(self, e):
        # 1. Notificar al Main qué botón se pulsó
        clicked_key = e.control.data
        print(f"Sidebar: Click en {clicked_key}")
        self.on_nav_change(clicked_key)

        # 2. Actualizar visualmente la Sidebar (Reseteamos todos a transparente y marcamos el nuevo)
        # Recorremos los hijos de la columna (saltamos el título y divider, indices 0 y 1)
        for item in self.content.controls[2:7]:
            # Si el item es el que hemos clicado
            if item.data == clicked_key:
                item.bgcolor = "#111827"
                item.content.controls[1].color = "white"  # Texto blanco
            else:
                item.bgcolor = "transparent"
                item.content.controls[1].color = "#9ca3af"  # Texto gris
            item.update()