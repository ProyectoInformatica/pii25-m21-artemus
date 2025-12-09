import flet as ft
from ArtemusPark.config.Colors import AppColors
from ArtemusPark.view.components.Temp_Chart import TempChart
from ArtemusPark.view.components.Sensor_Card import SensorCard
from ArtemusPark.view.components.Events_Panel import EventsPanel
from ArtemusPark.service.Dashboard_Service import DashboardService


class DashboardPage(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.bgcolor = AppColors.BG_MAIN
        self.padding = 18

        self.service = DashboardService()

        # 1. Instanciamos las tarjetas (ocultas por ahora)
        self.card_temp = SensorCard("Temperatura", "🌡", "--", "ºC", "Zona Central")
        self.card_hum = SensorCard("Humedad", "💧", "--", "%", "Suelo Riego A")
        self.card_wind = SensorCard("Viento", "💨", "--", "km/h", "Estación Norte")
        self.card_air = SensorCard("Calidad Aire", "☁️", "--", "ppm", "Sensor MQ-135")

        # 2. Eventos iniciales
        initial_events = self.service.get_recent_events()
        self.panel_events = EventsPanel(initial_events)

        self.content = ft.Column(
            controls=[
                self._build_window_bar(),
                self._build_main_card()
            ]
        )

    # --- LÓGICA DE ACTUALIZACIÓN ---
    def did_mount(self):
        self.page.pubsub.subscribe(self._on_message)

    def will_unmount(self):
        self.page.pubsub.unsubscribe_all()

    def _on_message(self, message):
        if message == "refresh_dashboard":
            # Actualizar tarjetas si estuvieran visibles
            if self.card_temp.page:
                data = self.service.get_latest_sensor_data()
                if data:
                    self.card_temp.update_value(data.get("temperature", 0))
                    self.card_hum.update_value(data.get("humidity", 0))
                    self.card_wind.update_value(data.get("wind", 0))
                    self.card_air.update_value(data.get("air_quality", 0))

            # Actualizar lista de eventos
            new_events = self.service.get_recent_events()
            self.panel_events.update_events(new_events)

    # -------------------------------

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
        return ft.Container(
            expand=True,
            bgcolor=AppColors.GLASS_WHITE,
            border_radius=24,
            padding=20,
            shadow=ft.BoxShadow(blur_radius=30, color=AppColors.SHADOW),
            content=ft.Column(
                scroll=ft.ScrollMode.AUTO,
                spacing=20,
                controls=[
                    ft.Text("Estado de Sensores", size=16, weight=ft.FontWeight.BOLD, color=AppColors.TEXT_MAIN),

                    # --- TARJETAS COMENTADAS ---
                    ft.Container(
                        content=ft.Row(
                            wrap=True,
                            spacing=15,
                            run_spacing=15,
                            run_alignment=ft.MainAxisAlignment.CENTER,
                            controls=[
                                self.card_temp, self.card_hum, self.card_wind, self.card_air
                            ]
                        )
                    ),
                    # ---------------------------

                    ft.Divider(height=10, color="transparent"),

                    ft.Text("Resumen de Actividad", size=16, weight=ft.FontWeight.BOLD, color=AppColors.TEXT_MAIN),

                    ft.Row(
                        vertical_alignment=ft.CrossAxisAlignment.START,
                        controls=[
                            # 1. Gráfica (Izquierda)
                            ft.Container(
                                expand=2,
                                height=300,
                                content=TempChart()
                            ),

                            ft.Container(width=15),

                            # 2. Contenedor de "Eventos Recientes" (Derecha)
                            ft.Container(
                                expand=1,
                                height=300,
                                bgcolor=ft.Colors.WHITE,  # Fondo blanco para resaltar
                                border_radius=12,  # Bordes redondeados
                                padding=15,  # Espacio interno
                                shadow=ft.BoxShadow(  # Sombra suave
                                    blur_radius=10,
                                    color=ft.Colors.with_opacity(0.05, ft.Colors.BLACK)
                                ),
                                content=ft.Column(
                                    spacing=10,
                                    controls=[
                                        # TÍTULO DENTRO DEL CONTENEDOR
                                        ft.Text("Eventos Recientes", size=14, weight=ft.FontWeight.BOLD,
                                                color=AppColors.TEXT_MAIN),
                                        ft.Divider(height=1, color=ft.Colors.GREY_100),

                                        # LISTA DE EVENTOS
                                        self.panel_events
                                    ]
                                )
                            )
                        ]
                    )
                ]
            )
        )