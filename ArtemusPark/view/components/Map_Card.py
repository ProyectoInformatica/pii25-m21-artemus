import flet as ft
from ArtemusPark.config.Colors import AppColors


class MapCard(ft.Container):
    def __init__(self, on_sensor_click=None):
        super().__init__()
        self.border_radius = 12
        self.bgcolor = ft.Colors.WHITE
        self.padding = 20
        self.border = ft.border.all(1, ft.Colors.GREY_300)
        self.alignment = ft.alignment.center
        self.on_sensor_click = on_sensor_click

        self.map_size = 400

        self.sensor_config = [
            ("wind", 0.25, 0.50, ft.Colors.BLUE_GREY, "Viento", ft.Icons.AIR),
            (
                "temperature",
                0.375,
                0.72,
                AppColors.DANGER,
                "Temperatura",
                ft.Icons.THERMOSTAT,
            ),
            ("humidity", 0.625, 0.72, AppColors.ACCENT, "Humedad", ft.Icons.WATER_DROP),
            ("lights", 0.75, 0.50, ft.Colors.YELLOW_600, "Luces", ft.Icons.LIGHTBULB),
            ("capacity", 0.625, 0.28, ft.Colors.PURPLE, "Aforo", ft.Icons.PEOPLE),
            (
                "smoke",
                0.375,
                0.28,
                ft.Colors.ORANGE_700,
                "Calidad Aire",
                ft.Icons.CLOUD,
            ),
        ]

        self.markers = {}
        self.content = self._build_map()

    def _build_map(self):
        """Construye la capa visual del mapa con marcadores."""
        stack_controls = [
            ft.Image(
                src="/img/artemus_park_map.png",
                fit=ft.ImageFit.CONTAIN,
                width=self.map_size,
                height=self.map_size,
                border_radius=12,
            )
        ]

        marker_size = 36

        for key, top_pct, left_pct, color, label, icon in self.sensor_config:

            icon_control = ft.Icon(icon, color=ft.Colors.WHITE, size=18)

            marker = ft.Container(
                content=icon_control,
                bgcolor=color,
                shape=ft.BoxShape.CIRCLE,
                width=marker_size,
                height=marker_size,
                alignment=ft.alignment.center,
                tooltip=f"{label}: --",
                shadow=ft.BoxShadow(blur_radius=6, color=ft.Colors.BLACK26),
                on_hover=self._on_marker_hover,
                on_click=self._on_marker_click,
                data=key,
                scale=1.0,
                animate_scale=ft.Animation(300, ft.AnimationCurve.ELASTIC_OUT),
            )

            self.markers[key] = marker

            left_pos = (self.map_size * left_pct) - (marker_size / 2)
            top_pos = (self.map_size * top_pct) - (marker_size / 2)

            stack_controls.append(
                ft.Container(
                    content=marker,
                    left=left_pos,
                    top=top_pos,
                )
            )

        return ft.Stack(
            width=self.map_size, height=self.map_size, controls=stack_controls
        )

    def _on_marker_hover(self, e):
        """Efecto visual al pasar el ratón"""
        e.control.scale = 1.2 if e.data == "true" else 1.0
        e.control.update()

    def _on_marker_click(self, e):
        """Maneja el clic en un marcador y llama al callback principal"""
        if self.on_sensor_click:
            self.on_sensor_click(e.control.data)

    def update_light_marker_status(self, is_on: bool, consumption: float):
        """Actualiza el marcador de luces y el texto de consumo."""
        marker = self.markers.get("lights")
        if marker:
            marker_icon_control = marker.content
            marker_icon_control.icon = (
                ft.Icons.LIGHTBULB if is_on else ft.Icons.LIGHTBULB_OUTLINE
            )
            marker.bgcolor = ft.Colors.ORANGE_500 if is_on else ft.Colors.GREY_500
            marker.tooltip = "Encendido" if is_on else "Apagado"
            marker.update()

    def update_sensor_data(self, data: dict):
        """Actualiza tooltips y estados de los marcadores"""

        if "temperature" in data:
            self._update_marker("temperature", f"{data['temperature']}ºC")

        if "humidity" in data:
            self._update_marker("humidity", f"{data['humidity']}%")

        if "wind" in data:
            self._update_marker("wind", f"{data['wind']} km/h")

        if "air_quality" in data:
            self._update_marker("smoke", f"AQI: {data['air_quality']}")

        if "occupancy" in data:
            self._update_marker("capacity", f"Personas: {data['occupancy']}")

        if "light_is_on" in data and "light_consumption" in data:
            self.update_light_marker_status(
                data["light_is_on"], data["light_consumption"]
            )

    def _update_marker(self, key, text):
        if key in self.markers:
            self.markers[key].tooltip = text
            self.markers[key].update()
