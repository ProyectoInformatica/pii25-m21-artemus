import flet as ft
from flet import ProgressBar
from ArtemusPark.config.Colors import AppColors

class CapacityCard(ft.Container):
    def __init__(self, max_capacity: int = 100):
        super().__init__()
        self.max_capacity = max_capacity

        self.width = 300
        self.height = 140
        self.bgcolor = AppColors.BG_CARD
        self.border_radius = 12
        self.padding = 20
        self.shadow = ft.BoxShadow(blur_radius=10, color=AppColors.SHADOW)

        self.txt_value = ft.Text("0", size=30, weight=ft.FontWeight.BOLD, color=AppColors.TEXT_MAIN)
        self.txt_percent = ft.Text("0%", size=12, color=AppColors.TEXT_MUTED)

        self.progress_bar = ProgressBar(
            value=0,
            color=AppColors.ACCENT,
            bgcolor=AppColors.BG_MAIN,
            height=8
        )

        self.content = ft.Column(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text("Aforo Actual", size=14, color=AppColors.TEXT_MUTED, weight=ft.FontWeight.W_500),
                        # CORREGIDO: ft.Icons (Mayúscula)
                        ft.Icon(ft.Icons.DIRECTIONS_CAR, size=20, color=AppColors.ACCENT),
                    ]
                ),

                ft.Row(
                    vertical_alignment=ft.CrossAxisAlignment.END,
                    controls=[
                        self.txt_value,
                        ft.Text(f"/ {self.max_capacity}", size=14, color=AppColors.TEXT_LIGHT_GREY),
                    ]
                ),

                ft.Column(
                    spacing=5,
                    controls=[
                        self.progress_bar,
                        ft.Row(
                            alignment=ft.MainAxisAlignment.END,
                            controls=[self.txt_percent]
                        )
                    ]
                )
            ]
        )

    def update_occupancy(self, current_value: int):
        if self.max_capacity <= 0:
            percentage = 0
        else:
            safe_value = min(current_value, self.max_capacity)
            percentage = safe_value / self.max_capacity

        self.txt_value.value = str(current_value)
        self.txt_percent.value = f"{int(percentage * 100)}%"
        self.progress_bar.value = percentage

        if percentage > 0.9:
            self.progress_bar.color = AppColors.DANGER
        elif percentage > 0.7:
            self.progress_bar.color = AppColors.WARNING
        else:
            self.progress_bar.color = AppColors.ACCENT

        self.update()