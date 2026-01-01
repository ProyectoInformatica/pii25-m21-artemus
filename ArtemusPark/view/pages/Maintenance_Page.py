import flet as ft
from ArtemusPark.config.Colors import AppColors
from ArtemusPark.service.Dashboard_Service import DashboardService


class MaintenancePage(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.padding = 20
        self.bgcolor = AppColors.BG_MAIN
        self.service = DashboardService()

        self.grid_devices = ft.GridView(
            expand=1,
            runs_count=5,
            max_extent=250,
            child_aspect_ratio=1.2,
            spacing=20,
            run_spacing=20,
            controls=[],
        )

        self.content = ft.Column(
            controls=[
                ft.Text(
                    "Monitor de Estado de Sensores",
                    size=24,
                    weight="bold",
                    color=ft.Colors.BLACK,
                ),
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text(
                            "Verde: Recibiendo datos | Rojo: Sin conexión (>15s)",
                            size=14,
                            color=ft.Colors.GREY_700,
                        ),
                        ft.IconButton(
                            icon=ft.Icons.REFRESH,
                            icon_color=ft.Colors.BLUE,
                            on_click=lambda e: self.update_data(),
                        ),
                    ],
                ),
                ft.Divider(height=20, color="transparent"),
                self.grid_devices,
            ]
        )

    def did_mount(self):
        """Inicia suscripción y carga datos iniciales."""
        self.page.pubsub.subscribe(self._on_message)

        self.update_data()

    def will_unmount(self):
        """Limpia suscripciones."""
        self.page.pubsub.unsubscribe_all()

    def _on_message(self, message):
        if message == "refresh_dashboard":
            self.update_data()

    def update_data(self):
        """Consulta el estado de salud y regenera las tarjetas"""
        health_data = self.service.get_sensors_health_status()

        self.grid_devices.controls.clear()

        for device in health_data:
            card = self._build_device_card(
                name=device["name"],
                status_text=device["status"],
                icon=device["icon"],
                is_online=device["is_online"],
                last_seen=device["last_seen"],
            )
            self.grid_devices.controls.append(card)

        self.update()

    def _build_device_card(self, name, status_text, icon, is_online, last_seen):
        """Crea la tarjeta visual para un dispositivo."""

        if is_online:
            status_color = ft.Colors.GREEN
            bg_icon = ft.Colors.GREEN_50
            border_color = ft.Colors.GREEN_200
        else:
            status_color = ft.Colors.RED
            bg_icon = ft.Colors.RED_50
            border_color = ft.Colors.RED_200

        return ft.Container(
            bgcolor=ft.Colors.WHITE,
            padding=15,
            border_radius=12,
            border=ft.border.all(1, border_color),
            shadow=ft.BoxShadow(
                blur_radius=5, color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK)
            ),
            content=ft.Column(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Container(
                                content=ft.Icon(icon, color=status_color),
                                bgcolor=bg_icon,
                                padding=10,
                                border_radius=10,
                            ),
                            ft.Icon(
                                ft.Icons.FIBER_MANUAL_RECORD,
                                color=status_color,
                                size=20,
                            ),
                        ],
                    ),
                    ft.Column(
                        spacing=2,
                        controls=[
                            ft.Text(
                                name, weight="bold", size=16, color=ft.Colors.BLACK
                            ),
                            ft.Text(
                                status_text, color=status_color, weight="bold", size=12
                            ),
                        ],
                    ),
                    ft.Container(
                        border=ft.border.only(top=ft.BorderSide(1, ft.Colors.GREY_100)),
                        padding=ft.padding.only(top=10),
                        content=ft.Row(
                            controls=[
                                ft.Icon(
                                    ft.Icons.ACCESS_TIME, size=12, color=ft.Colors.GREY
                                ),
                                ft.Text(
                                    f"Último dato: {last_seen}",
                                    size=10,
                                    color=ft.Colors.GREY_700,
                                ),
                            ]
                        ),
                    ),
                ],
            ),
        )
