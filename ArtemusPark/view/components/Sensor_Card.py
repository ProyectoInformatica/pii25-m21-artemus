import flet as ft


class SensorCard(ft.Container):
    def __init__(self, title: str, icon: str, value: str, unit: str, footer_text: str):
        super().__init__()
        # Configurar propiedades visuales del contenedor
        self.border = ft.border.all(1, "#e5e7eb")
        self.border_radius = 18
        self.padding = 12
        self.bgcolor = "#f9fafb"
        self.width = 200  # Ancho fijo o flexible segun necesites

        # Estructura interna
        self.content = ft.Column(
            spacing=4,
            controls=[
                # Header: Titulo e Icono
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text(title, size=13, color="#6b7280"),  # muted text
                        ft.Text(icon, size=18)
                    ]
                ),
                # Value: Valor y Unidad
                ft.Row(
                    alignment=ft.MainAxisAlignment.START,
                    vertical_alignment=ft.CrossAxisAlignment.BASELINE,
                    controls=[
                        ft.Text(value, size=22, weight=ft.FontWeight.W_600),
                        ft.Text(unit, size=14, color="#6b7280")
                    ]
                ),
                # Footer
                ft.Text(footer_text, size=12, color="#6b7280")
            ]
        )