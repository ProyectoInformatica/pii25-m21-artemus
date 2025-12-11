import flet as ft
from config.Colors import AppColors
from view.components.Temp_Chart import TempChart
from view.components.Sensor_Card import SensorCard
from view.components.Events_Panel import EventsPanel
from view.components.Capacity_Card import CapacityCard
from view.components.Alert_Card import AlertCard
from service.Dashboard_Service import DashboardService


class DashboardPage(ft.Container):
    def __init__(self, user_role="user"):
        super().__init__()
        self.expand = True
        self.bgcolor = AppColors.BG_MAIN
        self.padding = 18
        self.user_role = user_role
        self.service = DashboardService()

        # KPIs Superiores
        self.card_capacity = CapacityCard(max_capacity=2000)
        self.card_capacity.expand = 2
        self.card_alerts = AlertCard()
        self.card_alerts.expand = 2

        # Sensores
        self.card_temp = SensorCard("Temperatura", "🌡", "--", "ºC", "Zona Central")
        self.card_hum = SensorCard("Humedad", "💧", "--", "%", "Suelo Riego A")
        self.card_wind = SensorCard("Viento", "💨", "--", "km/h", "Estación Norte")
        self.card_air = SensorCard("Calidad Aire", "☁️", "--", "ppm", "Sensor MQ-135")

        for c in [self.card_temp, self.card_hum, self.card_wind, self.card_air]:
            c.expand = 1

        # Gráfica (Instanciada aquí para tener referencia)
        self.chart_component = TempChart()

        # Eventos
        self.panel_events = EventsPanel(self.service.get_recent_events())

        self.content = ft.Column(
            scroll=ft.ScrollMode.AUTO,  # Scroll de página principal
            controls=[self._build_window_bar(), self._build_main_card()],
        )

    def did_mount(self):
        self.page.pubsub.subscribe(self._on_message)

    def will_unmount(self):
        self.page.pubsub.unsubscribe_all()

    def _on_message(self, message):
        if message == "refresh_dashboard":
            # 1. Sensores
            data = self.service.get_latest_sensor_data()
            if data:
                self.card_temp.update_value(data.get("temperature", 0))
                self.card_hum.update_value(data.get("humidity", 0))
                self.card_wind.update_value(data.get("wind", 0))
                self.card_air.update_value(data.get("air_quality", 0))
                self.card_capacity.update_occupancy(data.get("occupancy", 0))

            # 2. Gráfica
            chart_data = self.service.get_temp_chart_data()
            self.chart_component.update_data(chart_data)

            # 3. Eventos
            new_events = self.service.get_recent_events()
            self.panel_events.update_events(new_events)

    def _build_window_bar(self):
        return ft.Row(
            controls=[
                ft.Text(
                    f"Bienvenido/a {self.user_role}",
                    weight=ft.FontWeight.BOLD,
                    color=AppColors.TEXT_MUTED,
                ),
                ft.Text(
                    "Dashboard", weight=ft.FontWeight.BOLD, color=AppColors.TEXT_MUTED
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

    def _build_main_card(self):
        return ft.Container(
            expand=True,
            bgcolor=AppColors.GLASS_WHITE,
            border_radius=12,
            padding=20,
            content=ft.Column(
                spacing=20,
                controls=[
                    ft.Row(controls=[self.card_capacity, self.card_alerts]),
                    ft.Divider(height=10, color=AppColors.BG_MAIN),
                    ft.Text(
                        "Sensores",
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color=AppColors.TEXT_MAIN,
                    ),
                    ft.Row(
                        spacing=15,
                        controls=[
                            self.card_temp,
                            self.card_hum,
                            self.card_wind,
                            self.card_air,
                        ],
                    ),
                    ft.Divider(height=10, color=AppColors.BG_MAIN),
                    # Fila Inferior (Gráfica + Eventos)
                    ft.Row(
                        height=450,  # Altura fija para evitar scroll infinito
                        controls=[
                            ft.Container(expand=2, content=self.chart_component),
                            ft.Container(width=15),
                            ft.Container(
                                expand=1,
                                bgcolor="white",
                                border_radius=12,
                                border=ft.border.all(1, ft.Colors.GREY_300),
                                padding=15,
                                content=ft.Column(
                                    controls=[
                                        ft.Text(
                                            "Eventos Recientes",
                                            weight=ft.FontWeight.BOLD,
                                            color="#6b7280",
                                        ),
                                        ft.Divider(height=1, color=AppColors.BG_MAIN),
                                        self.panel_events,  # ListView expandible
                                    ]
                                ),
                            ),
                        ],
                    ),
                ],
            ),
        )
