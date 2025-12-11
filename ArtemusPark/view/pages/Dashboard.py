import flet as ft
from ArtemusPark.config.Colors import AppColors

# Importamos TUS componentes
from ArtemusPark.view.components.Temp_Chart import TempChart
from ArtemusPark.view.components.Sensor_Card import SensorCard
from ArtemusPark.view.components.Events_Panel import EventsPanel
from ArtemusPark.view.components.Capacity_Card import CapacityCard
from ArtemusPark.service.Dashboard_Service import DashboardService


class DashboardPage(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.bgcolor = AppColors.BG_MAIN
        self.padding = 18

        self.service = DashboardService()

        # 1. Instanciar Tarjetas
        self.card_capacity = CapacityCard(max_capacity=50)

        self.card_temp = SensorCard("Temperatura", "🌡", "--", "ºC", "Zona Central")
        self.card_hum = SensorCard("Humedad", "💧", "--", "%", "Suelo Riego A")
        self.card_wind = SensorCard("Viento", "💨", "--", "km/h", "Estación Norte")
        self.card_air = SensorCard("Calidad Aire", "☁️", "--", "ppm", "Sensor MQ-135")

        # 2. Cargar Eventos Iniciales
        initial_events = self.service.get_recent_events()
        self.panel_events = EventsPanel(initial_events)

        # 3. Construir la UI
        self.content = ft.Column(
            controls=[self._build_header(), self._build_main_content()]
        )

    def did_mount(self):
        """Suscripción al sistema de eventos (PubSub)"""
        self.page.pubsub.subscribe(self._on_message)

    def will_unmount(self):
        """Desuscripción"""
        self.page.pubsub.unsubscribe_all()

    def _on_message(self, message):
        """Recepción de datos desde Main"""
        if message == "refresh_dashboard":
            # A. Datos de Sensores
            data = self.service.get_latest_sensor_data()
            if data and self.card_temp.page:
                self.card_temp.update_value(data.get("temperature", 0))
                self.card_hum.update_value(data.get("humidity", 0))
                self.card_wind.update_value(data.get("wind", 0))
                self.card_air.update_value(data.get("air_quality", 0))

                occupancy = data.get("occupancy", 25)
                self.card_capacity.update_occupancy(occupancy)

            # B. Datos de Eventos
            new_events = self.service.get_recent_events()
            self.panel_events.update_events(new_events)

    def _build_header(self):
        return ft.Row(
            controls=[
                ft.Text(
                    "Dashboard",
                    weight=ft.FontWeight.BOLD,
                    size=24,
                    color=AppColors.TEXT_MAIN,
                ),
                ft.Container(width=40),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

    def _build_main_content(self):
        return ft.Column(
            scroll=ft.ScrollMode.AUTO,
            spacing=20,
            controls=[
                ft.Text(
                    "Estado en Tiempo Real",
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    color=AppColors.TEXT_MUTED,
                ),
                # --- ZONA SUPERIOR: TARJETAS ---
                ft.Row(
                    wrap=True,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    spacing=20,
                    controls=[
                        self.card_capacity,
                        ft.Row(
                            wrap=True,
                            spacing=15,
                            run_spacing=15,
                            controls=[
                                self.card_temp,
                                self.card_hum,
                                self.card_wind,
                                self.card_air,
                            ],
                        ),
                    ],
                ),
                ft.Divider(height=20, color="transparent"),
                # --- ZONA INFERIOR: GRÁFICAS Y EVENTOS ---
                ft.Row(
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    spacing=20,
                    controls=[
                        # Izquierda: Gráfica
                        ft.Container(expand=2, height=350, content=TempChart()),
                        # Derecha: Panel de Eventos (CORREGIDO EL ERROR DE COLORES AQUÍ)
                        ft.Container(
                            expand=1,
                            height=350,
                            bgcolor=AppColors.BG_CARD,  # Antes era ft.colors.WHITE (Error)
                            border_radius=18,
                            padding=20,
                            shadow=ft.BoxShadow(blur_radius=10, color=AppColors.SHADOW),
                            content=ft.Column(
                                controls=[
                                    ft.Text(
                                        "Eventos Recientes",
                                        weight=ft.FontWeight.BOLD,
                                        color=AppColors.TEXT_MAIN,
                                    ),
                                    ft.Divider(
                                        height=10, color=AppColors.TEXT_LIGHT_GREY
                                    ),
                                    self.panel_events,
                                ]
                            ),
                        ),
                    ],
                ),
            ],
        )
