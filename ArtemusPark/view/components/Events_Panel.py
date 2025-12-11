import flet as ft
from flet import Column, Container, Row, Icon, Text
from datetime import datetime
from ArtemusPark.config.Colors import AppColors


class EventsPanel(Column):
    def __init__(self, events: list):
        super().__init__()
        self.spacing = 10
        self.scroll = ft.ScrollMode.AUTO
        self.expand = True

        self.controls = [self._create_event_item(e) for e in events]

    def update_events(self, new_events: list):
        self.controls.clear()
        self.controls.extend([self._create_event_item(e) for e in new_events])
        self.update()
        print(f"EventsPanel: Updated UI with {len(new_events)} events")

    def _create_event_item(self, event: dict):
        raw_ts = event.get("timestamp")

        if isinstance(raw_ts, (float, int)):
            try:
                time_str = datetime.fromtimestamp(raw_ts).strftime("%H:%M:%S")
            except Exception:
                time_str = "--:--"
        elif isinstance(raw_ts, str):
            time_str = raw_ts.split("T")[-1][:5]
        else:
            time_str = "--:--"

        evt_type = event.get("type", "unknown")

        # CORREGIDO: ft.Icons y ft.Colors en Mayúsculas
        if evt_type == "temperature":
            icon = ft.Icons.THERMOSTAT
            icon_color = ft.Colors.ORANGE
        elif evt_type == "humidity":
            icon = ft.Icons.WATER_DROP
            icon_color = AppColors.ACCENT
        elif evt_type == "light":
            icon = ft.Icons.LIGHT
            icon_color = ft.Colors.YELLOW_700
        elif evt_type == "door":
            icon = ft.Icons.DOOR_SLIDING
            icon_color = ft.Colors.BROWN
        else:
            icon = ft.Icons.INFO
            icon_color = AppColors.TEXT_MUTED

        val_str = str(event.get("value", "--"))

        return Container(
            content=Row(
                controls=[
                    Icon(icon, color=icon_color),
                    Text(
                        f"{evt_type.title()}: {val_str}",
                        expand=True,
                        weight=ft.FontWeight.BOLD,
                        color=AppColors.TEXT_MAIN,
                    ),
                    Text(time_str, color=AppColors.TEXT_MUTED, size=12),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=10,
            bgcolor=AppColors.BG_CARD,
            border=ft.border.all(1, AppColors.TEXT_LIGHT_GREY),
            border_radius=8,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=3,
                color=AppColors.SHADOW,
            ),
        )