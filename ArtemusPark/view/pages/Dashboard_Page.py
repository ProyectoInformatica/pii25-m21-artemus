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

        # Guardamos referencia al contenedor principal para cambiar su color
        self.main_card_container = self._build_main_card()

        self.content = ft.Column(
            scroll=ft.ScrollMode.AUTO,
            controls=[self._build_window_bar(), self.main_card_container],
        )

    def did_mount(self):
        # 1. Suscribirse al PubSub
        self.page.pubsub.subscribe(self._on_message)

        # 2. COMPROBAR ESTADO AL NACER
        # Si venimos de Admin y pulsaste el botón, el servicio lo recuerda.
        if self.service.is_catastrophe_mode():
            self._activate_catastrophe_protocol()

    def will_unmount(self):
        self.page.pubsub.unsubscribe_all()

    def _on_message(self, message):
        """Manejo completo de mensajes sin 'pass'"""

        # --- CASO 1: RECIBIMOS ORDEN DE REFRESCO (Cada 3 seg) ---
        if message == "refresh_dashboard":

            # A. Siempre actualizamos los datos numéricos (es vital verlos en emergencia)
            data = self.service.get_latest_sensor_data()
            if data:
                self.card_temp.update_value(data.get("temperature", 0))
                self.card_hum.update_value(data.get("humidity", 0))
                self.card_wind.update_value(data.get("wind", 0))
                self.card_air.update_value(data.get("air_quality", 0))
                self.card_capacity.update_occupancy(data.get("occupancy", 0))

            # B. Actualizamos gráficas y tablas
            chart_data = self.service.get_temp_chart_data()
            self.chart_component.update_data(chart_data)

            new_events = self.service.get_recent_events()
            self.panel_events.update_events(new_events)

            # C. CONTROL DE LA TARJETA DE ALERTAS
            # Solo si NO estamos en catástrofe, dejamos que el sistema muestre alertas normales.
            # Si estamos en catástrofe, BLOQUEAMOS cualquier otro mensaje para que se quede en rojo.
            if not self.service.is_catastrophe_mode():
                # Aquí podrías poner lógica de alertas normales de sensores
                # Por ahora, restauramos el estado "Normal" si no hay emergencia
                self.card_alerts.show_alert(
                    "Sistema Normal", "No hay incidencias activas.", is_critical=False
                )
                # Restauramos colores de fondo por si acaso
                self.bgcolor = AppColors.BG_MAIN
                self.main_card_container.bgcolor = AppColors.GLASS_WHITE
                self.update()

        # --- CASO 2: RECIBIMOS LA ALERTA DE CATÁSTROFE ---
        elif message == "catastrophe_mode":
            self._activate_catastrophe_protocol()

    def _activate_catastrophe_protocol(self):
        """Pone toda la interfaz en modo emergencia"""

        # 1. Fondo Rojo Sangre
        self.bgcolor = ft.Colors.RED_900

        # 2. Fondo de tarjetas Rojo Claro (para leer bien el texto)
        self.main_card_container.bgcolor = ft.Colors.RED_50

        # 3. Tarjeta de Alerta en modo CRÍTICO
        if self.card_alerts:
            self.card_alerts.show_alert(
                title="PROTOCOLO DE EMERGENCIA",
                description="¡CATÁSTROFE DETECTADA! EVACUACIÓN INMEDIATA.",
                is_critical=True,
            )

        self.update()

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
                                        ft.Text(
                                            "Eventos Recientes",
                                            weight=ft.FontWeight.BOLD,
                                            color="#6b7280",
                                        ),
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
