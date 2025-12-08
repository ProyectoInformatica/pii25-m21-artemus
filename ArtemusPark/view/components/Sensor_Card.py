import flet as ft
# Import ajustado a tu estructura (Mayúsculas)
from ArtemusPark.config.Colors import AppColors


class SensorCard(ft.Container):
    def __init__(self, title: str, icon: str, value: str, unit: str, footer_text: str):
        super().__init__()
        self.width = 180
        self.height = 110
        self.bgcolor = AppColors.BG_CARD
        self.border_radius = 12
        self.padding = 15

        self.shadow = ft.BoxShadow(
            spread_radius=1,
            blur_radius=5,
            color=AppColors.SHADOW  # si es un color válido de Flet
        )

        self.content = ft.Column(
            spacing=5,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text(title, size=12, color=AppColors.TEXT_MUTED),
                        ft.Text(icon, size=16),
                    ],
                ),
                ft.Row(
                    vertical_alignment=ft.CrossAxisAlignment.BASELINE,
                    controls=[
                        ft.Text(value, size=22, weight=ft.FontWeight.BOLD, color=AppColors.TEXT_MAIN),
                        ft.Text(unit, size=12, color=AppColors.TEXT_MUTED),
                    ],
                ),
                ft.Text(footer_text, size=10, color=AppColors.TEXT_LIGHT_GREY, no_wrap=True),
            ],
        )
