import flet as ft


class DashboardPage(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.bgcolor = "#e5e7eb"  # Fondo gris
        self.padding = 18

        self.content = ft.Column(
            controls=[
                # 1. La barra de título con los puntitos de colores
                self._build_window_bar(),

                # 2. El contenedor principal (Ahora está VACÍO)
                self._build_main_card()
            ]
        )

    def _build_window_bar(self):
        return ft.Row(
            controls=[
                ft.Row(
                    spacing=6,
                    controls=[
                        ft.Container(width=10, height=10, border_radius=5, bgcolor="#f97373"),
                        ft.Container(width=10, height=10, border_radius=5, bgcolor="#fbbf24"),
                        ft.Container(width=10, height=10, border_radius=5, bgcolor="#34d399"),
                    ]
                ),
                ft.Text("Dashboard", weight=ft.FontWeight.W_600, color="#6b7280"),
                ft.Container(width=40)  # Espaciador para equilibrar
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )

    def _build_main_card(self):
        return ft.Container(
            expand=True,
            bgcolor="#e6ffffff",  # Blanco con un poco de transparencia
            border_radius=24,
            padding=20,
            # Sombra suave
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=30,
                color="#140f172a"
            ),
            # CONTENIDO TEMPORAL
            content=ft.Column(
                controls=[
                    ft.Text("Dashboard listo para recibir componentes.", color="black", size=20),
                    ft.Text("Paso 1 completado.", color="grey")
                ]
            )
        )