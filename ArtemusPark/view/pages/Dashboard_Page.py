import asyncio
import flet as ft
from datetime import datetime
from ArtemusPark.config.Colors import AppColors
from ArtemusPark.view.components.Temp_Chart import TempChart
from ArtemusPark.view.components.Sensor_Card import SensorCard
from ArtemusPark.view.components.Events_Panel import EventsPanel
from ArtemusPark.view.components.Capacity_Card import CapacityCard
from ArtemusPark.view.components.Alert_Card import AlertCard
from ArtemusPark.view.components.Map_Card import MapCard
from ArtemusPark.service.Dashboard_Service import DashboardService
from ArtemusPark.config.Park_Config import OPEN_HOUR, CLOSE_HOUR


class DashboardPage(ft.Container):
    def __init__(self, user_name="Usuario", user_role="user", on_navigate=None, permissions=None):
        super().__init__()
        self.expand = True
        self.bgcolor = AppColors.BG_MAIN
        self.padding = 18
        self.user_name = user_name
        self.user_role = user_role
        self.permissions = permissions or []
        self.service = DashboardService()
        self.on_navigate = on_navigate
        self._is_mounted = False

        self.card_capacity = CapacityCard(max_capacity=2000)
        self.card_capacity.expand = 2

        self.card_alerts = AlertCard()
        self.card_alerts.expand = 2

        self.card_temp = SensorCard("Temperatura", "🌡", "--", "ºC")
        self.card_hum = SensorCard("Humedad", "💧", "--", "%")
        self.card_wind = SensorCard("Viento", "💨", "--", "km/h")
        self.card_air = SensorCard("Calidad Aire", "☁️", "--", "ppm")

        for c in [self.card_temp, self.card_hum, self.card_wind, self.card_air]:
            c.expand = 1

        # Revertido: El mapa ya no necesita manejar permisos complejos para luces aquí
        self.card_map = MapCard(on_sensor_click=self._handle_sensor_click, permissions=self.permissions)
        self.chart_component = TempChart()
        self.panel_events = EventsPanel(self.service.get_recent_events())

        self.main_card_container = self._build_main_card()

        self.content = ft.Column(
            scroll=ft.ScrollMode.AUTO,
            controls=[self._build_window_bar(), self.main_card_container],
        )

    def _handle_sensor_click(self, sensor_type):
        """Maneja el clic en los sensores del mapa y muestra detalles (Solo lectura)."""
        if "VIEW_SENSORS" not in self.permissions and self.user_role != "admin":
             self.page.open(ft.SnackBar(content=ft.Text("No tienes permiso para ver detalles de sensores")))
             return

        type_map = {
            "lights": "light",
            "capacity": "door",
            "smoke": "smoke",
            "temperature": "temperature",
            "humidity": "humidity",
            "wind": "wind",
        }

        target_type = type_map.get(sensor_type, sensor_type)
        display_title = target_type.capitalize()

        all_sensors = self.service.get_sensors_health_status()
        filtered_sensors = [s for s in all_sensors if s["type"] == target_type]

        rows = []
        for s in filtered_sensors:
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(s["name"])),
                        ft.DataCell(
                            ft.Container(
                                content=ft.Text(s["status"], size=12, color="white"),
                                bgcolor=(ft.Colors.GREEN if s["is_online"] else ft.Colors.RED),
                                padding=5, border_radius=5,
                            )
                        ),
                        ft.DataCell(ft.Text(str(s["last_value"]))),
                        ft.DataCell(ft.Text(s["last_seen"])),
                    ]
                )
            )

        if rows:
            content = ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("Nombre")),
                    ft.DataColumn(ft.Text("Estado")),
                    ft.DataColumn(ft.Text("Valor")),
                    ft.DataColumn(ft.Text("Últ. Act.")),
                ],
                rows=rows,
                border=ft.border.all(1, ft.Colors.GREY_300),
            )

            dialog = ft.AlertDialog(
                title=ft.Text(f"Detalle de {display_title}"),
                content=ft.Column([content], height=300, width=650, scroll=ft.ScrollMode.AUTO, tight=True),
                actions=[ft.TextButton("Cerrar", on_click=lambda e: self.page.close(dialog))],
            )
            self.page.open(dialog)

    def did_mount(self):
        self._is_mounted = True
        self._clock_running = True
        self.page.run_task(self._clock_loop)
        self.page.pubsub.subscribe(self._on_message)
        self._on_message("refresh_dashboard")
        if self.service.is_catastrophe_mode():
            self._activate_catastrophe_protocol()

    def _on_message(self, message):
        if not self._is_mounted or not self.page: return
        if message == "refresh_dashboard":
            data = self.service.get_latest_sensor_data()
            if data: self.card_capacity.update_occupancy(data.get("occupancy", 0))
            avg_data = self.service.get_average_sensor_data()
            if avg_data:
                def update_sensor_ui(card, map_key, value):
                    if value is None:
                        card.update_value("--")
                        self.card_map.update_marker_status_by_type(map_key, False)
                    else:
                        card.update_value(value)
                        self.card_map.update_marker_status_by_type(map_key, True)
                update_sensor_ui(self.card_temp, "temperature", avg_data.get("temperature"))
                update_sensor_ui(self.card_hum, "humidity", avg_data.get("humidity"))
                update_sensor_ui(self.card_wind, "wind", avg_data.get("wind"))
                update_sensor_ui(self.card_air, "air_quality", avg_data.get("air_quality"))
                self.card_map.update_sensor_data(data)
            chart_data = self.service.get_temp_chart_data()
            self.chart_component.update_data(chart_data)
            if "VIEW_SECURITY_LOGS" in self.permissions or self.user_role == "admin":
                new_events = self.service.get_recent_events()
                self.panel_events.update_events(new_events)
            else:
                self.panel_events.update_events([])
        elif message == "catastrophe_mode": self._activate_catastrophe_protocol()
        elif message == "normal_mode": self._deactivate_catastrophe_protocol()

    def _activate_catastrophe_protocol(self):
        self.bgcolor = ft.Colors.RED_900
        self.main_card_container.bgcolor = ft.Colors.RED_50
        if self.card_alerts: self.card_alerts.show_alert("ALERTA CATÁSTROFE", "¡SISTEMA CRÍTICO!", is_critical=True)
        try: self.update()
        except: pass

    def _deactivate_catastrophe_protocol(self):
        self.bgcolor = AppColors.BG_MAIN
        self.main_card_container.bgcolor = AppColors.GLASS_WHITE
        if self.card_alerts: self.card_alerts.show_alert("Sistema Normal", "Protocolo desactivado.", is_critical=False)
        try: self.update()
        except: pass

    def _build_window_bar(self):
        self.txt_welcome = ft.Text(f"Bienvenido/a {self.user_name}", weight=ft.FontWeight.BOLD, color=AppColors.TEXT_MUTED)
        now = datetime.now()
        self.clock_icon = ft.Icon(ft.Icons.WB_SUNNY, size=18)
        self.txt_clock = ft.Text(now.strftime("%H:%M:%S"), weight=ft.FontWeight.BOLD, size=18)
        self.clock_container = ft.Container(padding=ft.padding.symmetric(horizontal=14, vertical=8), border_radius=999, content=ft.Row(spacing=8, controls=[self.clock_icon, self.txt_clock]))
        self._update_clock_pill(now)
        return ft.Row(controls=[self.txt_welcome, self.clock_container, ft.Text("Dashboard", weight=ft.FontWeight.BOLD, color=AppColors.TEXT_MUTED)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

    async def _clock_loop(self):
        while self._clock_running:
            now = datetime.now()
            self.txt_clock.value = now.strftime("%H:%M:%S")
            self._update_clock_pill(now)
            try: self.clock_container.update()
            except: pass
            await asyncio.sleep(1)

    def _update_clock_pill(self, now):
        hour = now.hour
        if OPEN_HOUR <= hour < CLOSE_HOUR:
            self.clock_icon.name = ft.Icons.WB_SUNNY
            self.clock_container.bgcolor = ft.Colors.AMBER_50
        else:
            self.clock_icon.name = ft.Icons.NIGHTLIGHT_ROUND
            self.clock_container.bgcolor = ft.Colors.INDIGO_900

    def _build_main_card(self):
        self.txt_sensors_title = ft.Text("Sensores (Media)", size=16, weight=ft.FontWeight.BOLD, color=AppColors.TEXT_MAIN)
        self.txt_events_title = ft.Text("Eventos Recientes", weight=ft.FontWeight.BOLD, color="#6b7280")
        return ft.Container(expand=True, bgcolor=AppColors.GLASS_WHITE, border_radius=12, padding=20, content=ft.Column(spacing=20, controls=[
            ft.Row(controls=[self.card_capacity, self.card_alerts]),
            ft.Divider(height=10, color=AppColors.BG_MAIN),
            self.txt_sensors_title,
            ft.Row(spacing=15, controls=[self.card_temp, self.card_hum, self.card_wind, self.card_air]),
            ft.Divider(height=10, color=AppColors.BG_MAIN),
            ft.Row(height=500, controls=[
                ft.Container(content=self.card_map, alignment=ft.alignment.top_center),
                ft.Container(width=20),
                ft.Column(expand=True, spacing=15, controls=[
                    ft.Container(expand=1, content=self.chart_component),
                    ft.Container(expand=1, bgcolor="white", border_radius=12, border=ft.border.all(1, ft.Colors.GREY_300), padding=15, content=ft.Column([
                        self.txt_events_title,
                        ft.Divider(height=1, color=AppColors.BG_MAIN),
                        self.panel_events,
                    ])),
                ]),
            ]),
        ]))
