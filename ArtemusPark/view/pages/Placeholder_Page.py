import flet as ft


class PlaceholderPage(ft.Container):
    def __init__(self, title, description):
        super().__init__()
        self.expand = True
        self.bgcolor = "#e5e7eb"
        self.padding = 18
        self.content = ft.Container(
            border=ft.border.all(1, "#d1d5db"),
            border_radius=18,
            bgcolor="#f9fafb",
            padding=20,
            alignment=ft.alignment.center,
            content=ft.Column(
                # CORRECCIÓN AQUI:
                alignment=ft.MainAxisAlignment.CENTER,  # Eje vertical (Main Axis)
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,  # Eje horizontal (Cross Axis)
                controls=[
                    ft.Text(title, size=20, weight=ft.FontWeight.BOLD, color="#111827"),
                    ft.Text(
                        description,
                        size=14,
                        color="#6b7280",
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
            ),
        )
