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
    def __init__(self, user_role="user", on_navigate=None): # Añadimos on_navigate
        super().__init__()
        self.expand = True
        self.bgcolor = AppColors.BG_MAIN
        self.padding = 18
        self.user_role = user_role
        self.service = DashboardService()
        self.on_navigate = on_navigate # Guardamos la función de navegación

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

        # Componentes Visuales
        self.card_map = MapCard(on_sensor_click=self._on_map_sensor_click) # Pasamos el callback
        self.chart_component = TempChart()
        self.panel_events = EventsPanel(self.service.get_recent_events())

        # Guardamos referencia al contenedor para cambiarle el color luego
        self.main_card_container = self._build_main_card()

        self.content = ft.Column(
            scroll=ft.ScrollMode.AUTO,
            controls=[self._build_window_bar(), self.main_card_container],
        )
    
    def _on_map_sensor_click(self, sensor_type: str):
        """Muestra un diálogo modal con la lista de sensores de ese tipo."""
        
        # 1. Configuración visual según el tipo
        configs = {
            "temperature": {"color": ft.Colors.RED_50, "icon": ft.Icons.THERMOSTAT, "title": "Temperatura"},
            "humidity": {"color": ft.Colors.BLUE_50, "icon": ft.Icons.WATER_DROP, "title": "Humedad"},
            "wind": {"color": ft.Colors.CYAN_50, "icon": ft.Icons.WIND_POWER, "title": "Viento"},
            "smoke": {"color": ft.Colors.YELLOW_50, "icon": ft.Icons.AIR, "title": "Calidad Aire"},
            "lights": {"color": ft.Colors.ORANGE_50, "icon": ft.Icons.LIGHTBULB, "title": "Iluminación"},
            "capacity": {"color": ft.Colors.PURPLE_50, "icon": ft.Icons.PEOPLE, "title": "Control Aforo"},
        }
        
        cfg = configs.get(sensor_type, {"color": ft.Colors.GREY_50, "icon": ft.Icons.INFO, "title": sensor_type})
        
        # 2. Generar lista simulada de componentes
        # En un sistema real, esto vendría de una base de datos de inventario
        component_list = ft.Column(
            spacing=10,
            height=200,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                self._build_sensor_row("Sensor Principal (Central)", "En línea", cfg["color"]),
                self._build_sensor_row("Nodo Entrada Norte", "En línea", ft.Colors.WHITE),
                self._build_sensor_row("Nodo Zona Picnic", "Standby", ft.Colors.WHITE),
                self._build_sensor_row("Nodo Mantenimiento", "Offline", ft.Colors.GREY_300),
            ]
        )

        # 3. Crear y abrir el diálogo
        dlg = ft.AlertDialog(
            title=ft.Row([ft.Icon(cfg["icon"], color="black"), ft.Text(f"Sensores de {cfg['title']}")], alignment=ft.MainAxisAlignment.CENTER),
            content=ft.Container(
                content=component_list,
                width=400,
                padding=10,
                bgcolor=cfg["color"], # Color de fondo temático
                border_radius=10
            ),
            actions=[
                ft.TextButton("Cerrar", on_click=lambda e: self.page.close_dialog())
            ],
            actions_alignment=ft.MainAxisAlignment.CENTER,
            bgcolor=ft.Colors.WHITE, # Fondo del marco del diálogo
        )
        
        # self.page.show_dialog(dlg)

    def _build_sensor_row(self, name, status, bg_color):
        return ft.Container(
            padding=10,
            bgcolor=bg_color,
            border_radius=8,
            border=ft.border.all(1, ft.Colors.GREY_300 if bg_color == ft.Colors.WHITE else "transparent"),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text(name, weight=ft.FontWeight.BOLD, color="black"),
                    ft.Container(
                        padding=ft.padding.symmetric(horizontal=8, vertical=4),
                        bgcolor="green" if status == "En línea" else "grey",
                        border_radius=4,
                        content=ft.Text(status, size=10, color="white")
                    )
                ]
            )
        )


    def did_mount(self):
        # 1. Suscribirse
        self.page.pubsub.subscribe(self._on_message)

        # 2. Comprobar memoria al nacer
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
                
                # Actualizar Mapa
                self.card_map.update_sensor_data(data)

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
                        height=500,  # Aumentamos altura para acomodar mapa
                        controls=[
                            # Columna Izquierda: Mapa
                            ft.Container(
                                content=self.card_map,
                                alignment=ft.alignment.top_center
                            ),
                            
                            ft.Container(width=20),
                            
                            # Columna Derecha: Gráfica + Eventos
                            ft.Column(
                                expand=True,
                                spacing=15,
                                controls=[
                                    # Gráfica (Arriba)
                                    ft.Container(
                                        expand=1, 
                                        content=self.chart_component
                                    ),
                                    
                                    # Eventos (Abajo)
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
                                ]
                            )
                        ],
                    ),
                ],
            ),
        )
