import flet as ft
from config.Colors import AppColors

class SensorCard(ft.Container):
    def __init__(self, title: str, icon: str, value: str, unit: str, footer_text: str):
        super().__init__()
        self.width = 180
        self.height = 110
        self.bgcolor = AppColors.BG_CARD
        self.border_radius = 12
        self.padding = 15
        self.shadow = ft.BoxShadow(spread_radius=1, blur_radius=5, color="#1A000000")

        # GUARDAMOS EL CONTROL DE TEXTO EN UNA VARIABLE (self.value_text)
        self.value_text = ft.Text(value, size=22, weight=ft.FontWeight.BOLD, color=AppColors.TEXT_MAIN)

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
                        self.value_text, # Usamos la variable aquí
                        ft.Text(unit, size=12, color=AppColors.TEXT_MUTED),
                    ],
                ),
                ft.Text(footer_text, size=10, color=AppColors.TEXT_LIGHT_GREY, no_wrap=True, overflow=ft.TextOverflow.ELLIPSIS),
            ],
        )

    # --- NUEVO MÉTODO PARA ACTUALIZAR EL DATO ---
    def update_value(self, new_value):
        # 1. Cambiamos el valor de la variable de texto
        self.value_text.value = str(new_value)

        # 2. IMPORTANTE: Actualizamos LA TARJETA ENTERA (self), no solo el texto.
        # Esto evita el error "Control must be added to the page first"
        self.update()