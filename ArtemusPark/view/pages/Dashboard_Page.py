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

        # 1. Instancias Superiores
        self.card_capacity = CapacityCard(max_capacity=2000)
        self.card_capacity.expand = 2
        self.card_alerts = AlertCard()
        self.card_alerts.expand = 2

        # 2. INSTANCIAS DE TARJETAS DE SENSORES
        self.card_temp = SensorCard("Temperatura", "🌡", "--", "ºC", "Zona Central")
        self.card_hum = SensorCard("Humedad", "💧", "--", "%", "Suelo Riego A")
        self.card_wind = SensorCard("Viento", "💨", "--", "km/h", "Estación Norte")
        self.card_air = SensorCard("Calidad Aire", "☁️", "--", "ppm", "Sensor MQ-135")

        # --- CORRECCIÓN CLAVE: Forzamos la expansión aquí para asegurar el diseño ---
        self.card_temp.expand = 1
        self.card_hum.expand = 1
        self.card_wind.expand = 1
        self.card_air.expand = 1
        # --------------------------------------------------------------------------

        # 3. EVENTOS INICIALES
        initial_events = self.service.get_recent_events()
        self.panel_events = EventsPanel(initial_events)

        self.content = ft.Column(
            controls=[self._build_window_bar(), self._build_main_card()]
        )

    # --- LÓGICA DE ACTUALIZACIÓN ---
    def did_mount(self):
        self.page.pubsub.subscribe(self._on_message)
        # self.card_alerts.show_alert("Humo detectado cerca del lago", is_critical=True)

    def will_unmount(self):
        self.page.pubsub.unsubscribe_all()

    def _on_message(self, message):
        if message == "refresh_dashboard":
            data = self.service.get_latest_sensor_data()

            if data and self.card_temp.page:
                self.card_temp.update_value(data.get("temperature", 0))
                self.card_hum.update_value(data.get("humidity", 0))
                self.card_wind.update_value(data.get("wind", 0))
                self.card_air.update_value(data.get("air_quality", 0))

                occupancy = data.get("occupancy", 1201)
                self.card_capacity.update_occupancy(occupancy)

                if data.get("air_quality", 0) > 100:
                    self.card_alerts.show_alert(
                        "Calidad de aire peligrosa", is_critical=True
                    )

            new_events = self.service.get_recent_events()
            # self.panel_events.update_events(new_events)

    # -------------------------------

    def _build_window_bar(self):
        return ft.Row(
            controls=[
                ft.Text(
                    "Bienvenido/a " + self.user_role,
                    weight=ft.FontWeight.W_600,
                    color=AppColors.TEXT_MUTED,
                ),
                ft.Container(width=40),
                ft.Text(
                    "Dashboard", weight=ft.FontWeight.W_600, color=AppColors.TEXT_MUTED
                ),
                ft.Container(width=40),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )

    def _build_main_card(self):
        return ft.Container(
            expand=True,
            bgcolor=AppColors.GLASS_WHITE,
            border_radius=12,
            padding=20,
            content=ft.Column(
                # Quitamos el scroll general de aquí para que la página no se mueva
                scroll=ft.ScrollMode.AUTO,
                spacing=20,
                controls=[
                    # --- ZONA SUPERIOR (Igual que antes) ---
                    ft.Row(
                        alignment=ft.MainAxisAlignment.START,
                        vertical_alignment=ft.CrossAxisAlignment.START,
                        spacing=20,
                        controls=[self.card_capacity, self.card_alerts],
                    ),
                    ft.Divider(height=10, color=AppColors.BG_MAIN),
                    ft.Text(
                        "Sensores",
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color=AppColors.TEXT_MAIN,
                    ),
                    # --- ZONA SENSORES (Igual que antes) ---
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
                    # --- GRÁFICA + EVENTOS (CORREGIDO) ---
                    ft.Row(
                        # IMPORTANTE: Altura fija para esta sección.
                        # Esto "cierra la jaula" y obliga al scroll interno.
                        height=450,
                        controls=[
                            # Contenedor Gráfica
                            ft.Container(
                                expand=2, content=TempChart()  # 2/3 del ancho
                            ),
                            ft.Container(width=15),
                            # Contenedor Eventos
                            ft.Container(
                                expand=1,  # 1/3 del ancho
                                bgcolor=ft.Colors.WHITE,
                                border_radius=12,
                                border=ft.border.all(1, ft.Colors.GREY_300),
                                padding=15,
                                # Usamos Column para poner Título arriba y Lista abajo
                                content=ft.Column(
                                    spacing=10,
                                    controls=[
                                        ft.Text(
                                            "Eventos Recientes",
                                            size=14,
                                            weight=ft.FontWeight.BOLD,
                                            color=AppColors.TEXT_MAIN,
                                        ),
                                        ft.Divider(height=1, color=ft.Colors.GREY_100),
                                        # La lista se expande para llenar los 500px - (título)
                                        self.panel_events,
                                    ],
                                ),
                            ),
                        ],
                    ),
                ],
            ),
        )
