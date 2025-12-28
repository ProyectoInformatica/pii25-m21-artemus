import flet as ft
from ArtemusPark.config.Colors import AppColors
from ArtemusPark.view.components.Temp_Chart import TempChart
from ArtemusPark.view.components.Sensor_Card import SensorCard
from ArtemusPark.view.components.Events_Panel import EventsPanel
from ArtemusPark.view.components.Capacity_Card import CapacityCard
from ArtemusPark.view.components.Alert_Card import AlertCard
from ArtemusPark.service.Dashboard_Service import DashboardService


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

        # Gráfica
        self.chart_component = TempChart()

        # Eventos
        self.panel_events = EventsPanel(self.service.get_recent_events())

        # Guardamos referencia al contenedor para cambiarle el color luego
        self.main_card_container = self._build_main_card()

        self.content = ft.Column(
            scroll=ft.ScrollMode.AUTO,
            controls=[self._build_window_bar(), self.main_card_container],
        )

    def did_mount(self):
        # 1. Suscribirse
        self.page.pubsub.subscribe(self._on_message)

        # 2. Comprobar memoria al nacer
        # Si vienes de Admin y la alarma sigue puesta, ponte rojo inmediatamente.
        if self.service.is_catastrophe_mode():
            self._activate_catastrophe_protocol()

    def will_unmount(self):
        self.page.pubsub.unsubscribe_all()

    def _on_message(self, message):
        """Gestor de mensajes centralizado"""

        # CASO 1: Refresco habitual (cada 3s)
        if message == "refresh_dashboard":
            # Actualizamos datos numéricos siempre
            data = self.service.get_latest_sensor_data()
            if data:
                self.card_temp.update_value(data.get("temperature", 0))
                self.card_hum.update_value(data.get("humidity", 0))
                self.card_wind.update_value(data.get("wind", 0))
                self.card_air.update_value(data.get("air_quality", 0))
                self.card_capacity.update_occupancy(data.get("occupancy", 0))

            chart_data = self.service.get_temp_chart_data()
            self.chart_component.update_data(chart_data)

            new_events = self.service.get_recent_events()
            self.panel_events.update_events(new_events)

            # Si NO hay catástrofe, mostramos estado normal en la tarjeta de alertas
            if not self.service.is_catastrophe_mode():
                # Opcional: Podrías poner lógica de alertas de sensores aquí
                pass

        # CASO 2: ¡ACTIVAR EMERGENCIA!
        elif message == "catastrophe_mode":
            self._activate_catastrophe_protocol()

        # CASO 3: ¡DESACTIVAR EMERGENCIA! (Esto es lo que te faltaba)
        elif message == "normal_mode":
            self._deactivate_catastrophe_protocol()

    def _activate_catastrophe_protocol(self):
        """Pone todo ROJO"""
        self.bgcolor = ft.Colors.RED_900
        self.main_card_container.bgcolor = ft.Colors.RED_50

        # Cambiar colores de textos para catástrofe
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

        # Restaurar colores de textos
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
            bgcolor=AppColors.GLASS_WHITE,  # Color por defecto
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
                        height=450,
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
                                        self.txt_events_title,
                                        ft.Divider(height=1, color=AppColors.BG_MAIN),
                                        self.panel_events,
                                    ]
                                ),
                            ),
                        ],
                    ),
                ],
            ),
        )
