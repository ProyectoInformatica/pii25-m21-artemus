import flet as ft
from ArtemusPark.config.Colors import AppColors


class CapacityCard(ft.Container):
    def __init__(self, max_capacity: int = 100):
        super().__init__()
        self.max_capacity = max_capacity
        # self.width = 300  # Un poco más ancha que las de sensores
        self.expand = True
        self.height = 140
        self.bgcolor = AppColors.BG_CARD
        self.border_radius = 12
        self.border = ft.border.all(1, ft.Colors.GREY_300)
        self.padding = 20
        # self.shadow = ft.BoxShadow(
        #     blur_radius=10, color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK)
        # )

        # --- CONTROLES QUE SE ACTUALIZARÁN ---
        self.txt_value = ft.Text(
            "0", size=30, weight=ft.FontWeight.BOLD, color=AppColors.TEXT_MAIN
        )
        self.txt_percent = ft.Text("0%", size=12, color=AppColors.TEXT_MUTED)
        self.progress_bar = ft.ProgressBar(
            value=0, color=ft.Colors.BLUE, bgcolor=ft.Colors.GREY_200, height=8
        )

        # --- ESTRUCTURA VISUAL ---
        self.content = ft.Column(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                # Cabecera
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text(
                            "Aforo Actual",
                            size=14,
                            color=AppColors.TEXT_MUTED,
                            weight=ft.FontWeight.W_500,
                        ),
                        # Chip "Live" simulado o icono
                        ft.Container(
                            content=ft.Text("Live", size=10, color=ft.Colors.BLUE),
                            bgcolor=ft.Colors.BLUE_50,
                            padding=ft.padding.symmetric(horizontal=8, vertical=2),
                            border_radius=10,
                        ),
                    ],
                ),
                # Dato Central
                ft.Row(
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    controls=[
                        self.txt_value,
                        ft.Text(
                            f"Max visitantes: {self.max_capacity}",
                            size=12,
                            color=AppColors.TEXT_LIGHT_GREY,
                        ),
                    ],
                ),
                # Barra de Progreso y Porcentaje
                ft.Column(
                    spacing=5,
                    controls=[
                        self.progress_bar,
                        # ft.Row([self.txt_percent], alignment=ft.MainAxisAlignment.END), # Opcional
                    ],
                ),
            ],
        )

    def update_occupancy(self, current_value: int):
        # Evitar superar el máximo visualmente
        safe_value = min(current_value, self.max_capacity)
        percentage = safe_value / self.max_capacity

        # Actualizar textos
        self.txt_value.value = str(current_value)
        self.txt_percent.value = f"{int(percentage * 100)}%"

        # Actualizar barra y cambiar color si está casi lleno
        self.progress_bar.value = percentage
        if percentage > 0.9:
            self.progress_bar.color = ft.Colors.RED
        elif percentage > 0.7:
            self.progress_bar.color = ft.Colors.ORANGE
        else:
            self.progress_bar.color = ft.Colors.BLUE

        self.update()
