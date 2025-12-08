import flet as ft
from ArtemusPark.config.Colors import AppColors
from ArtemusPark.view.components.Temp_Chart import TempChart
from ArtemusPark.view.components.Sensor_Card import SensorCard
from ArtemusPark.service.Dashboard_Service import DashboardService

class DashboardPage(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.bgcolor = AppColors.BG_MAIN
        self.padding = 18

        # 1. Obtenemos los datos del servicio
        self.service = DashboardService()
        self.data = self.service.get_latest_sensor_data()

        self.content = ft.Column(
            controls=[
                self._build_window_bar(),
                self._build_main_card()
            ]
        )

    def _build_window_bar(self):
        return ft.Row(
            controls=[
                ft.Row(
                    spacing=6,
                    controls=[
                        ft.Container(width=10, height=10, border_radius=5, bgcolor=AppColors.ERROR_LIGHT),
                        ft.Container(width=10, height=10, border_radius=5, bgcolor=AppColors.WARNING),
                        ft.Container(width=10, height=10, border_radius=5, bgcolor=AppColors.SUCCESS),
                    ]
                ),
                ft.Text("Dashboard", weight=ft.FontWeight.W_600, color=AppColors.TEXT_MUTED),
                ft.Container(width=40)
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )

    def _build_main_card(self):
        # Convertimos a string para pintarlo
        t = str(self.data.get("temperature", 0))
        h = str(self.data.get("humidity", 0))
        w = str(self.data.get("wind", 0))
        a = str(self.data.get("air_quality", 0))

        return ft.Container(
            expand=True,
            bgcolor=AppColors.GLASS_WHITE,
            border_radius=24,
            padding=20,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=30,
                color=AppColors.SHADOW
            ),
            content=ft.Column(
                scroll=ft.ScrollMode.AUTO,
                spacing=20,
                controls=[
                    ft.Divider(height=10, color="transparent"),

                    # Gráfico
                    ft.Text("Histórico Térmico", size=16, weight=ft.FontWeight.BOLD, color=AppColors.TEXT_MAIN),
                    ft.Container(
                        height=300,
                        content=TempChart()
                    )
                ]
            )
        )