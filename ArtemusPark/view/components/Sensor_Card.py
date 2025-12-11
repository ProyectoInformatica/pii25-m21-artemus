import flet as ft
from ArtemusPark.config.Colors import AppColors


class SensorCard(ft.Container):
    def __init__(self, title: str, icon: str, value: str, unit: str, footer_text: str):
        super().__init__()
        self.width = 180
        # self.expand = True
        self.height = 120
        self.bgcolor = AppColors.BG_CARD
        self.border_radius = 12
        self.border = ft.border.all(1, ft.Colors.GREY_300)
        self.padding = 15

        # Sombra suave opcional (puedes descomentarla si quieres efecto 3D)
        # self.shadow = ft.BoxShadow(spread_radius=1, blur_radius=5, color="#1A000000")


        # 1. Variable para el texto del valor (se actualizará después)
        self.value_text = ft.Text(
            value, size=22, weight=ft.FontWeight.BOLD, color=AppColors.TEXT_MAIN
        )

        self.content = ft.Column(
            spacing=5,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                # Fila Superior: Título e Icono
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text(title, size=12, color=AppColors.TEXT_MUTED),
                        ft.Text(icon, size=16),
                    ],
                ),
                # Fila Central: Valor y Unidad (AHORA DESCOMENTADA)
                ft.Row(
                    vertical_alignment=ft.CrossAxisAlignment.END,
                    controls=[
                        self.value_text,  # Aquí va el número
                        ft.Text(unit, size=12, color=AppColors.TEXT_MUTED),
                    ],
                ),
                # Fila Inferior: Texto de pie de tarjeta
                ft.Text(
                    footer_text,
                    size=10,
                    color=AppColors.TEXT_LIGHT_GREY,
                    no_wrap=True,
                    overflow=ft.TextOverflow.ELLIPSIS,
                ),
            ],
        )

    def update_value(self, new_value):
        """
        Actualiza el número y refresca la tarjeta.
        """
        self.value_text.value = str(new_value)
        self.update()
