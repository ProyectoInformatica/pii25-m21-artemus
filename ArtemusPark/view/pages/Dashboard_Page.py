import flet as ft
from ArtemusPark.config.Colors import AppColors
from ArtemusPark.view.components.Temp_Chart import TempChart
from ArtemusPark.view.components.Sensor_Card import SensorCard
from ArtemusPark.view.components.Events_Panel import EventsPanel
from ArtemusPark.view.components.Capacity_Card import CapacityCard
from ArtemusPark.view.components.Alert_Card import AlertCard
from ArtemusPark.view.components.Map_Card import MapCard
from ArtemusPark.service.Dashboard_Service import DashboardService


class DashboardPage(ft.Container):
    def __init__(self, user_role="user", on_navigate=None):
        super().__init__()
        self.expand = True
        self.bgcolor = AppColors.BG_MAIN
        self.padding = 18
        self.user_role = user_role
        self.service = DashboardService()
        self.on_navigate = on_navigate

        self.card_capacity = CapacityCard(max_capacity=2000)
        self.card_capacity.expand = 2

        self.card_alerts = AlertCard()
        self.card_alerts.expand = 2

        self.card_temp = SensorCard("Temperatura", "🌡", "--", "ºC", "Zona Central")
        self.card_hum = SensorCard("Humedad", "💧", "--", "%", "Suelo Riego A")
        self.card_wind = SensorCard("Viento", "💨", "--", "km/h", "Estación Norte")
        self.card_air = SensorCard("Calidad Aire", "☁️", "--", "ppm", "Sensor MQ-135")

        for c in [self.card_temp, self.card_hum, self.card_wind, self.card_air]:
            c.expand = 1

        self.card_map = MapCard()
        self.chart_component = TempChart()
        self.panel_events = EventsPanel(self.service.get_recent_events())

        self.main_card_container = self._build_main_card()

        self.content = ft.Column(
            scroll=ft.ScrollMode.AUTO,
            controls=[self._build_window_bar(), self.main_card_container],
        )

    def _build_sensor_row(self, name, status, bg_color):
        return ft.Container(
            padding=10,
            bgcolor=bg_color,
            border_radius=8,
            border=ft.border.all(
                1, ft.Colors.GREY_300 if bg_color == ft.Colors.WHITE else "transparent"
            ),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text(name, weight=ft.FontWeight.BOLD, color="black"),
                    ft.Container(
                        padding=ft.padding.symmetric(horizontal=8, vertical=4),
                        bgcolor="green" if status == "En línea" else "grey",
                        border_radius=4,
                        content=ft.Text(status, size=10, color="white"),
                    ),
                ],
            ),
        )

    def did_mount(self):
        """Suscribe a eventos y verifica estado inicial."""
        self.page.pubsub.subscribe(self._on_message)
        self._on_message("refresh_dashboard")

        if self.service.is_catastrophe_mode():
            self._activate_catastrophe_protocol()

    def will_unmount(self):
        """Desuscribe eventos."""
        self.page.pubsub.unsubscribe_all()

    def _on_message(self, message):
        """Gestor de mensajes centralizado"""

        if message == "refresh_dashboard":

            data = self.service.get_latest_sensor_data()
            if data:
                self.card_temp.update_value(data.get("temperature", 0))
                self.card_hum.update_value(data.get("humidity", 0))
                self.card_wind.update_value(data.get("wind", 0))
                self.card_air.update_value(data.get("air_quality", 0))
                self.card_capacity.update_occupancy(data.get("occupancy", 0))

                self.card_map.update_sensor_data(data)

            chart_data = self.service.get_temp_chart_data()
            self.chart_component.update_data(chart_data)

            new_events = self.service.get_recent_events()
            self.panel_events.update_events(new_events)

            if not self.service.is_catastrophe_mode():

                pass

        elif message == "catastrophe_mode":
            self._activate_catastrophe_protocol()

        elif message == "normal_mode":
            self._deactivate_catastrophe_protocol()

    def _activate_catastrophe_protocol(self):
        """Pone todo ROJO"""
        self.bgcolor = ft.Colors.RED_900
        self.main_card_container.bgcolor = ft.Colors.RED_50

        self.txt_welcome.color = ft.Colors.WHITE
        self.txt_dashboard.color = ft.Colors.WHITE
        self.txt_sensors_title.color = ft.Colors.RED_900
        self.txt_events_title.color = ft.Colors.RED_900

        if self.card_alerts:
            self.card_alerts.show_alert(
                "PROTOCOLO DE EMERGENCIA",
                "¡EVACUACIÓN! Siga las luces de emergencia.",
                is_critical=True,
            )
        self.update()

    def _deactivate_catastrophe_protocol(self):
        """Pone todo VERDE/AZUL (Normal)"""
        self.bgcolor = AppColors.BG_MAIN
        self.main_card_container.bgcolor = AppColors.GLASS_WHITE

        self.txt_welcome.color = AppColors.TEXT_MUTED
        self.txt_dashboard.color = AppColors.TEXT_MUTED
        self.txt_sensors_title.color = AppColors.TEXT_MAIN
        self.txt_events_title.color = "#6b7280"

        if self.card_alerts:
            self.card_alerts.show_alert(
                "Sistema Normal", "El protocolo ha sido desactivado.", is_critical=False
            )
        self.update()

    def _build_window_bar(self):
        self.txt_welcome = ft.Text(
            f"Bienvenido/a {self.user_role}",
            weight=ft.FontWeight.BOLD,
            color=AppColors.TEXT_MUTED,
        )
        self.txt_dashboard = ft.Text(
            "Dashboard", weight=ft.FontWeight.BOLD, color=AppColors.TEXT_MUTED
        )
        return ft.Row(
            controls=[
                self.txt_welcome,
                self.txt_dashboard,
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

    def _build_main_card(self):
        self.txt_sensors_title = ft.Text(
            "Sensores",
            size=16,
            weight=ft.FontWeight.BOLD,
            color=AppColors.TEXT_MAIN,
        )
        self.txt_events_title = ft.Text(
            "Eventos Recientes",
            weight=ft.FontWeight.BOLD,
            color="#6b7280",
        )

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
                    self.txt_sensors_title,
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
                    ft.Row(
                        height=500,
                        controls=[
                            ft.Container(
                                content=self.card_map, alignment=ft.alignment.top_center
                            ),
                            ft.Container(width=20),
                            ft.Column(
                                expand=True,
                                spacing=15,
                                controls=[
                                    ft.Container(
                                        expand=1, content=self.chart_component
                                    ),
                                    ft.Container(
                                        expand=1,
                                        bgcolor="white",
                                        border_radius=12,
                                        border=ft.border.all(1, ft.Colors.GREY_300),
                                        padding=15,
                                        content=ft.Column(
                                            controls=[
                                                self.txt_events_title,
                                                ft.Divider(
                                                    height=1, color=AppColors.BG_MAIN
                                                ),
                                                self.panel_events,
                                            ]
                                        ),
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
        )
