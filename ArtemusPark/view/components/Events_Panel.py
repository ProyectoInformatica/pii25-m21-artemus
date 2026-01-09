import flet as ft
from flet import Container, Row, Icon, Text, Icons, Colors
from datetime import datetime


class EventsPanel(ft.ListView):
    def __init__(self, events: list):
        super().__init__()
        self.expand = True
        self.spacing = 10
        self.padding = ft.padding.only(right=10, bottom=10)

        self.controls = [self._create_event_item(e) for e in events]

    def update_events(self, new_events: list):
        """Actualiza la lista de eventos en el panel."""
        self.controls.clear()
        self.controls.extend([self._create_event_item(e) for e in new_events])
        if self.page:
            self.update()
        print(f"EventsPanel: Updated UI with {len (new_events )} events")

    def _create_event_item(self, event: dict):
        """Crea un componente visual para un evento individual."""
        raw_ts = event.get("timestamp")

        if isinstance(raw_ts, (float, int)):
            try:
                time_str = datetime.fromtimestamp(raw_ts).strftime("%H:%M:%S")
            except Exception:
                time_str = "--:--"
        elif isinstance(raw_ts, str):

            time_str = raw_ts.split("T")[-1][:5] if "T" in raw_ts else raw_ts[-8:-3]
        else:
            time_str = "--:--"

        evt_type = event.get("type", "unknown").lower()

        if "temp" in evt_type:
            icon = Icons.THERMOSTAT
            color = Colors.ORANGE
        elif "hum" in evt_type:
            icon = Icons.WATER_DROP
            color = Colors.BLUE
        elif "light" in evt_type:
            icon = Icons.LIGHTBULB
            color = Colors.YELLOW_700
        elif "door" in evt_type:
            icon = Icons.DOOR_SLIDING
            color = Colors.BROWN
        elif "alert" in evt_type:
            icon = Icons.WARNING_AMBER
            color = Colors.RED
        else:
            icon = Icons.INFO_OUTLINE
            color = Colors.GREY

        val_str = str(event.get("label", event.get("value", "--")))
        status_str = str(event.get("status", ""))

        return Container(
            content=Row(
                controls=[
                    Icon(icon, color=color),
                    ft.Column(
                        spacing=0,
                        expand=True,
                        controls=[
                            Text(
                                val_str,
                                weight=ft.FontWeight.BOLD,
                                color=Colors.BLACK87,
                                size=13,
                            ),
                            (
                                Text(status_str, size=11, color=Colors.GREY_600)
                                if status_str
                                else ft.Container()
                            ),
                        ],
                    ),
                    Text(time_str, color=Colors.GREY_500, size=12),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=10,
            bgcolor=Colors.WHITE,
            border=ft.border.all(1, Colors.GREY_100),
            border_radius=8,
        )
