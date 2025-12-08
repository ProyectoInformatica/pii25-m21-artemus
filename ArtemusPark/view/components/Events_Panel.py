import flet as ft
from flet import Column, Container, Row, Icon, Text, Icons, Colors  # <--- IMPORTANTE: minúsculas
from datetime import datetime


class EventsPanel(Column):
    def __init__(self, events: list):
        super().__init__()
        # Configuración de la columna (scroll, espaciado)
        self.spacing = 10
        self.scroll = ft.ScrollMode.AUTO
        self.expand = True

        # Carga inicial de controles
        self.controls = [self._create_event_item(e) for e in events]

    def update_events(self, new_events: list):
        """
        Limpia la lista actual y renderiza los nuevos eventos.
        """
        self.controls.clear()
        self.controls.extend([self._create_event_item(e) for e in new_events])
        self.update()
        print(f"EventsPanel: Updated UI with {len(new_events)} events")

    def _create_event_item(self, event: dict):
        raw_ts = event.get("timestamp")

        # Lógica para manejar Timestamp (float) o Texto ISO (str)
        if isinstance(raw_ts, (float, int)):
            try:
                # Convertir timestamp numérico a hora legible
                time_str = datetime.fromtimestamp(raw_ts).strftime("%H:%M:%S")
            except Exception:
                time_str = "--:--"
        elif isinstance(raw_ts, str):
            # Cortar cadena ISO si viene como texto
            time_str = raw_ts.split("T")[-1][:5]
        else:
            time_str = "--:--"

        # Iconos y colores según el tipo
        evt_type = event.get("type", "unknown")
        print(f"EventsPanel: Event type {evt_type}")

        # Corregido: uso de 'Icons' y 'Colors' en minúscula
        if evt_type == "temperature":
            icon = Icons.THERMOSTAT
            color = Colors.ORANGE
        elif evt_type == "humidity":
            icon = Icons.WATER_DROP
            color = Colors.BLUE
        elif evt_type == "light":
            icon = Icons.LIGHT
            color = Colors.YELLOW
        elif evt_type == "door":
            icon = Icons.DOOR_SLIDING
            color = Colors.BROWN
        else:
            icon = Icons.INFO
            color = Colors.GREY

        val_str = str(event.get("value", "--"))

        return Container(
            content=Row(
                controls=[
                    Icon(icon, color=color),
                    Text(f"{evt_type.title()}: {val_str}", expand=True, weight=ft.FontWeight.BOLD, color=Colors.BLACK),
                    Text(time_str, color=Colors.GREY_500, size=12)
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ),
            padding=10,
            bgcolor=Colors.WHITE,
            border=ft.border.all(1, Colors.GREY_200),
            border_radius=8,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=3,
                color=Colors.with_opacity(0.1, Colors.BLACK),
            )
        )
