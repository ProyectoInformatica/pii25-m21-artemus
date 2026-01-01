import flet as ft
from ArtemusPark.config.Colors import AppColors
from ArtemusPark.service.Dashboard_Service import DashboardService
from ArtemusPark.repository.Auth_Repository import AuthRepository
from ArtemusPark.repository.Requests_Repository import RequestsRepository


class MaintenancePage(ft.Container):
    def __init__(self, current_username=None):
        super().__init__()
        self.expand = True
        self.padding = 20
        self.bgcolor = AppColors.BG_MAIN
        self.service = DashboardService()
        self.current_username = current_username
        self.auth_repo = AuthRepository()
        self.req_repo = RequestsRepository()

        # Obtener sensores asignados al usuario
        self.assigned_sensors = []
        if self.current_username:
            user_data = self.auth_repo.get_all_users().get(self.current_username, {})
            self.assigned_sensors = user_data.get("assigned_sensors", [])

        # Contenedor para "Mis Sensores Asignados"
        self.my_sensors_row = ft.Row(spacing=20, scroll=ft.ScrollMode.AUTO)
        self.my_sensors_container = ft.Column(
            visible=bool(self.assigned_sensors),
            controls=[
                ft.Text(
                    f"⭐ Mis Sensores Asignados ({len(self.assigned_sensors)})",
                    size=20,
                    weight="bold",
                    color=AppColors.BG_DARK,
                ),
                ft.Text(
                    "Monitorización prioritaria de tus dispositivos asignados",
                    size=14,
                    color=ft.Colors.GREY_700,
                ),
                ft.Container(height=10),
                self.my_sensors_row,
                ft.Divider(height=30, color=ft.Colors.GREY_300),
            ]
        )

        self.grid_devices = ft.GridView(
            expand=1,
            runs_count=5,
            max_extent=250,
            child_aspect_ratio=1.2,
            spacing=20,
            run_spacing=20,
            controls=[],
        )
        
        # Boton de solicitud de cambio
        self.btn_request_change = ft.ElevatedButton(
            "Solicitar Cambio de Sensores",
            icon=ft.Icons.EDIT_NOTE,
            bgcolor=ft.Colors.BLUE_GREY_100,
            color=ft.Colors.BLUE_GREY_900,
            on_click=self._open_request_dialog,
            visible=bool(self.current_username)
        )

        self.content = ft.Column(
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                         ft.Text(
                            "Monitor de Estado del Sistema (Global)",
                            size=24,
                            weight="bold",
                            color=ft.Colors.BLACK,
                        ),
                        self.btn_request_change
                    ]
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
                self.my_sensors_container, # Insertamos la seccion personalizada aqui
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
            
    def _open_request_dialog(self, e):
        self.tf_request_msg = ft.TextField(
            label="Detalle de la solicitud", 
            multiline=True, 
            min_lines=3,
            hint_text="Ej: Solicito añadir el sensor de la Puerta Norte."
        )
        
        self.dlg_request = ft.AlertDialog(
            title=ft.Text("Solicitar Cambio de Sensores"),
            content=ft.Column([
                ft.Text("Describe los cambios que necesitas en tu asignación:"),
                self.tf_request_msg
            ], tight=True, width=400),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self.page.close(self.dlg_request)),
                ft.ElevatedButton("Enviar a Supervisor", on_click=self._submit_request, bgcolor=AppColors.BG_DARK, color="white")
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.open(self.dlg_request)

    def _submit_request(self, e):
        msg = self.tf_request_msg.value
        if not msg:
            self.tf_request_msg.error_text = "Escribe un motivo"
            self.tf_request_msg.update()
            return
            
        self.req_repo.create_request(self.current_username, msg)
        self.page.close(self.dlg_request)
        
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text("Solicitud enviada correctamente"),
            bgcolor="green"
        )
        self.page.snack_bar.open = True
        self.page.update()

    def update_data(self):
        """Consulta el estado de salud y regenera las tarjetas"""
        health_data = self.service.get_sensors_health_status()

        # 1. Actualizar Grid Global
        self.grid_devices.controls.clear()
        
        # 2. Actualizar Mis Sensores (si existen)
        if self.assigned_sensors:
            self.my_sensors_row.controls.clear()

        for device in health_data:
            # Crear tarjeta
            card = self._build_device_card(
                name=device["name"],
                status_text=device["status"],
                icon=device["icon"],
                is_online=device["is_online"],
                last_seen=device["last_seen"],
            )

            # Mapeo corregido para coincidir con DashboardService.get_sensors_health_status
            device_type_map = {
                "Sensor Temperatura": "temperature",
                "Sensor Humedad": "humidity",
                "Anemómetro": "wind", 
                "Detector Humo": "smoke",
                "Iluminación": "light",
                "Puertas": "door"
            }
            
            sensor_key = device_type_map.get(device["name"])
            
            # Agregamos a la seccion personal si coincide
            if sensor_key and sensor_key in self.assigned_sensors:
                # Clonar la tarjeta o crear una version destacada
                highlighted_card = self._build_device_card(
                     name=device["name"],
                     status_text=device["status"],
                     icon=device["icon"],
                     is_online=device["is_online"],
                     last_seen=device["last_seen"],
                     highlight=True
                )
                self.my_sensors_row.controls.append(highlighted_card)

            # Siempre agregar al grid global
            self.grid_devices.controls.append(card)

        self.update()

    def _build_device_card(self, name, status_text, icon, is_online, last_seen, highlight=False):
        """Crea la tarjeta visual para un dispositivo."""

        if is_online:
            status_color = ft.Colors.GREEN
            bg_icon = ft.Colors.GREEN_50
            border_color = ft.Colors.GREEN_200
        else:
            status_color = ft.Colors.RED
            bg_icon = ft.Colors.RED_50
            border_color = ft.Colors.RED_200
            
        if highlight:
            border_color = ft.Colors.BLUE_400
            bg_color = ft.Colors.BLUE_50
        else:
            bg_color = ft.Colors.WHITE

        return ft.Container(
            bgcolor=bg_color,
            padding=15,
            width=240 if highlight else None, # Fijo para fila horizontal
            border_radius=12,
            border=ft.border.all(2 if highlight else 1, border_color),
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
                                ft.Icons.STAR if highlight else ft.Icons.FIBER_MANUAL_RECORD,
                                color=ft.Colors.BLUE if highlight else status_color,
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
                        border=ft.border.only(top=ft.BorderSide(1, ft.Colors.GREY_300 if highlight else ft.Colors.GREY_100)),
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
