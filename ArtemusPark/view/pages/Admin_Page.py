import flet as ft
import time
import threading
from datetime import datetime

from flet.core.types import MainAxisAlignment

from ArtemusPark.config.Colors import AppColors
from ArtemusPark.service.Dashboard_Service import DashboardService
from ArtemusPark.repository import (
    Light_Repository,
    Temperature_Repository,
    Door_Repository,
)
from ArtemusPark.repository.Auth_Repository import AuthRepository


class AdminPage(ft.Container):
    def __init__(self, user_role="admin", current_username=None):
        super().__init__()
        self.expand = True
        self.padding = 20
        self.bgcolor = AppColors.BG_MAIN

        self.service = DashboardService()
        self.auth_repo = AuthRepository()
        self.simulation_running = False
        self.current_username = current_username

        if user_role != "admin":
            self.content = ft.Center(
                ft.Text("Acceso Restringido", size=30, color=ft.Colors.BLACK)
            )
            return

        self.users_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Usuario", color=ft.Colors.BLACK)),
                ft.DataColumn(ft.Text("Rol", color=ft.Colors.BLACK)),
                ft.DataColumn(ft.Text("", color=ft.Colors.BLACK)),
            ],
            rows=[],
            width=float("inf"),
        )

        self.energy_data_points = [ft.LineChartDataPoint(i, 50) for i in range(20)]
        now_str = datetime.now().strftime("%H:%M:%S")
        self.time_labels = [now_str for _ in range(20)]

        self.btn_catastrophe = ft.ElevatedButton(
            text="CARGANDO ESTADO...",
            icon=ft.Icons.WARNING_AMBER_ROUNDED,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                shape=ft.RoundedRectangleBorder(radius=10),
                padding=20,
            ),
            width=400,
            on_click=self._toggle_catastrophe,
        )

        self.txt_energy_value = ft.Text(
            "Iniciando...",
            size=40,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.BLUE_GREY_800,
        )
        self.txt_energy_detail = ft.Text(
            "Sincronizando...", size=12, color=ft.Colors.GREY
        )

        self.chart = ft.LineChart(
            data_series=[
                ft.LineChartData(
                    data_points=self.energy_data_points,
                    stroke_width=3,
                    color=ft.Colors.BLUE,
                    curved=True,
                    stroke_cap_round=True,
                    below_line_bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.BLUE),
                )
            ],
            border=ft.border.all(1, ft.Colors.TRANSPARENT),
            left_axis=ft.ChartAxis(
                labels=[
                    ft.ChartAxisLabel(value=50, label=ft.Text("50kW", size=10)),
                    ft.ChartAxisLabel(value=200, label=ft.Text("200kW", size=10)),
                    ft.ChartAxisLabel(value=400, label=ft.Text("400kW", size=10)),
                    ft.ChartAxisLabel(value=600, label=ft.Text("600kW", size=10)),
                ],
                labels_size=40,
            ),
            bottom_axis=ft.ChartAxis(labels=[], labels_size=20),
            tooltip_bgcolor=ft.Colors.with_opacity(0.8, ft.Colors.BLUE_GREY),
            expand=True,
        )

        user_mgmt_section = self._build_section_container(
            "Gestión de Usuarios",
            ft.Column(
                controls=[
                    ft.ElevatedButton(
                        "Agregar Usuario",
                        icon=ft.Icons.ADD,
                        on_click=lambda e: self._open_user_dialog(),
                        bgcolor=ft.Colors.BLUE,
                        color=ft.Colors.WHITE,
                    ),
                    ft.Divider(color=AppColors.TRANSPARENT),
                    ft.Container(
                        content=ft.Column(
                            [self.users_table], scroll=ft.ScrollMode.AUTO
                        ),
                        height=500,
                        margin=2,
                    ),
                ],
                expand=True,
            ),
        )
        user_mgmt_section.expand = 1

        emergency_section = self._build_section_container(
            "Control de Emergencia",
            ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Text(
                        "Gestión de Protocolos de Seguridad",
                        color=ft.Colors.GREY_700,
                        size=12,
                    ),
                    ft.Container(height=10),
                    self.btn_catastrophe,
                ],
            ),
        )

        energy_section = self._build_section_container(
            "Monitor de Consumo Eléctrico (Tiempo Real)",
            ft.Container(
                height=350,
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Icon(
                                    ft.Icons.ELECTRIC_BOLT,
                                    color=ft.Colors.AMBER,
                                    size=30,
                                ),
                                ft.Column(
                                    [
                                        self.txt_energy_value,
                                        self.txt_energy_detail,
                                    ],
                                    spacing=0,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                        ft.Divider(color="transparent"),
                        self.chart,
                    ]
                ),
            ),
        )

        right_column = ft.Column(
            expand=1, spacing=20, controls=[emergency_section, energy_section]
        )

        self.content = ft.ListView(
            spacing=20,
            controls=[
                ft.Text(
                    "Panel de Administración",
                    size=24,
                    weight="bold",
                    color=ft.Colors.BLACK,
                ),
                self._build_section_container(
                    "Perfil de Administrador",
                    ft.Row(
                        [
                            ft.CircleAvatar(
                                foreground_image_src="https://ui-avatars.com/api/?name=Admin+User&background=0D8ABC&color=fff",
                                radius=30,
                            ),
                            ft.Column(
                                [
                                    ft.Text(
                                        "Super Admin",
                                        weight="bold",
                                        size=16,
                                        color=ft.Colors.BLACK,
                                    ),
                                    ft.Text(
                                        "admin@artemus.park",
                                        color=ft.Colors.GREY_700,
                                        size=12,
                                    ),
                                ]
                            ),
                        ]
                    ),
                ),
                ft.Row(
                    controls=[user_mgmt_section, right_column],
                    spacing=20,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                ),
            ],
        )

    def did_mount(self):
        self.simulation_running = True
        self._update_button_state()
        self._load_users()

        threading.Thread(target=self._realtime_energy_loop, daemon=True).start()

    def will_unmount(self):
        self.simulation_running = False

    def _load_users(self):
        users = self.auth_repo.get_all_users()
        self.users_table.rows.clear()
        for username, data in users.items():
            is_me = username == self.current_username
            display_name = f"{username} (Tú)" if is_me else username

            if len(display_name) > 24:
                display_name = display_name[:24] + "..."

            role_text = data["role"]
            if len(role_text) > 24:
                role_text = role_text[:24] + "..."

            delete_btn = ft.IconButton(
                icon=ft.Icons.DELETE,
                icon_color=ft.Colors.GREY if is_me else ft.Colors.RED,
                tooltip=(
                    "Eliminar" if not is_me else "No puedes eliminar tu propia cuenta"
                ),
                disabled=is_me,
                on_click=lambda e, u=username: self._delete_user(u),
            )

            self.users_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(
                            ft.Text(
                                display_name,
                                color=ft.Colors.BLACK,
                                overflow=ft.TextOverflow.ELLIPSIS,
                                max_lines=1,
                            )
                        ),
                        ft.DataCell(
                            ft.Text(
                                role_text,
                                color=ft.Colors.BLACK,
                                overflow=ft.TextOverflow.ELLIPSIS,
                                max_lines=1,
                            )
                        ),
                        ft.DataCell(
                            ft.Row(
                                [
                                    ft.IconButton(
                                        icon=ft.Icons.EDIT,
                                        icon_color=ft.Colors.BLUE,
                                        tooltip="Editar",
                                        on_click=lambda e, u=username: self._open_user_dialog(
                                            u
                                        ),
                                    ),
                                    delete_btn,
                                ],
                                alignment=ft.MainAxisAlignment.END,
                                spacing=0,
                            ),
                        ),
                    ]
                )
            )
        self.users_table.update()

    def _open_user_dialog(self, username=None):
        users = self.auth_repo.get_all_users()
        is_edit = username is not None
        user_data = users.get(username, {}) if is_edit else {}

        tf_user = ft.TextField(
            label="Usuario",
            value=username if is_edit else "",
            disabled=is_edit,
            max_length=24,
        )
        tf_pass = ft.TextField(
            label="Contraseña",
            value=user_data.get("password", ""),
            password=True,
            can_reveal_password=True,
        )
        dd_role = ft.Dropdown(
            label="Rol",
            options=[
                ft.dropdown.Option("admin"),
                ft.dropdown.Option("maintenance"),
                ft.dropdown.Option("user"),
            ],
            value=user_data.get("role", "user"),
        )

        def save(e):
            try:
                if is_edit:
                    self.auth_repo.update_user(username, tf_pass.value, dd_role.value)
                else:
                    self.auth_repo.add_user(tf_user.value, tf_pass.value, dd_role.value)
                self.page.close(dialog)
                self._load_users()
                self.page.snack_bar = ft.SnackBar(
                    ft.Text("Usuario guardado correctamente")
                )
                self.page.snack_bar.open = True
                self.page.update()
            except Exception as ex:
                self.page.snack_bar = ft.SnackBar(ft.Text(f"Error: {str(ex)}"))
                self.page.snack_bar.open = True
                self.page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("Editar Usuario" if is_edit else "Nuevo Usuario"),
            content=ft.Column([tf_user, tf_pass, dd_role], height=200, width=300),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self.page.close(dialog)),
                ft.ElevatedButton("Guardar", on_click=save),
            ],
        )
        self.page.open(dialog)

    def _delete_user(self, username):
        def confirm_delete(e):
            self.auth_repo.delete_user(username)
            self.page.close(dialog)
            self._load_users()
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Usuario {username} eliminado"))
            self.page.snack_bar.open = True
            self.page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("Confirmar eliminación"),
            content=ft.Text(f"¿Estás seguro de eliminar a {username}?"),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self.page.close(dialog)),
                ft.ElevatedButton(
                    "Eliminar",
                    bgcolor=ft.Colors.RED,
                    color=ft.Colors.WHITE,
                    on_click=confirm_delete,
                ),
            ],
        )
        self.page.open(dialog)

    def _toggle_catastrophe(self, e):
        is_active = self.service.is_catastrophe_mode()
        if is_active:
            self.service.set_catastrophe_mode(False)
            print("AdminPage: Enviando señal 'normal_mode'")
            self.page.pubsub.send_all("normal_mode")
        else:
            self.service.set_catastrophe_mode(True)
            print("AdminPage: Enviando señal 'catastrophe_mode'")
            self.page.pubsub.send_all("catastrophe_mode")
        self._update_button_state()

    def _update_button_state(self):
        is_active = self.service.is_catastrophe_mode()
        if is_active:
            self.btn_catastrophe.text = "DESACTIVAR PROTOCOLO Y RESTAURAR"
            self.btn_catastrophe.bgcolor = ft.Colors.GREEN_700
            self.btn_catastrophe.icon = ft.Icons.CHECK_CIRCLE_OUTLINE
        else:
            self.btn_catastrophe.text = "ACTIVAR PROTOCOLO DE CATÁSTROFE"
            self.btn_catastrophe.bgcolor = ft.Colors.RED_700
            self.btn_catastrophe.icon = ft.Icons.WARNING_AMBER_ROUNDED
        self.btn_catastrophe.update()

    def _calculate_sensor_load(self) -> dict:
        base_load = 50.0
        reasons = []
        lights = Light_Repository.load_all_light_events()
        if lights:
            last_light = lights[-1]
            is_on = (
                last_light.get("is_on")
                if isinstance(last_light, dict)
                else getattr(last_light, "is_on", False)
            )
            if is_on:
                base_load += 150.0
                reasons.append("Luces ON")
        temps = Temperature_Repository.load_all_temperature_measurements()
        if temps:
            last_temp = temps[-1]
            val = (
                last_temp.get("value")
                if isinstance(last_temp, dict)
                else getattr(last_temp, "value", 22)
            )
            if val > 28:
                base_load += 200.0
                reasons.append(f"AC Máximo ({val}ºC)")
            elif val > 24:
                base_load += 100.0
                reasons.append(f"AC Medio ({val}ºC)")
            elif val < 15:
                base_load += 180.0
                reasons.append(f"Calefacción ({val}ºC)")
        doors = Door_Repository.load_all_door_events()
        if doors:
            last_door = doors[-1]
            ts = (
                last_door.get("timestamp")
                if isinstance(last_door, dict)
                else getattr(last_door, "timestamp", 0)
            )
            if (time.time() - ts) < 5:
                base_load += 80.0
                reasons.append("Motor Puerta")
        return {"total": base_load, "details": ", ".join(reasons)}

    def _realtime_energy_loop(self):
        while self.simulation_running:
            load_data = self._calculate_sensor_load()
            current_kw = load_data["total"]
            current_time_str = datetime.now().strftime("%H:%M:%S")
            self.txt_energy_value.value = f"{current_kw:.1f} kW"
            self.txt_energy_detail.value = (
                load_data["details"]
                if load_data["details"]
                else "Consumo Base (Standby)"
            )
            self.energy_data_points.pop(0)
            for i, p in enumerate(self.energy_data_points):
                p.x = i
            self.energy_data_points.append(ft.LineChartDataPoint(19, current_kw))
            self.time_labels.pop(0)
            self.time_labels.append(current_time_str)
            new_labels = []
            for i in range(0, 20, 4):
                new_labels.append(
                    ft.ChartAxisLabel(
                        value=i,
                        label=ft.Text(
                            self.time_labels[i],
                            size=10,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.GREY,
                        ),
                    )
                )
            self.chart.bottom_axis.labels = new_labels
            color = ft.Colors.RED if current_kw > 500 else ft.Colors.BLUE
            self.chart.data_series[0].color = color
            self.chart.data_series[0].below_line_bgcolor = ft.Colors.with_opacity(
                0.2, color
            )
            try:
                self.chart.update()
                self.txt_energy_value.update()
                self.txt_energy_detail.update()
            except Exception:
                pass
            time.sleep(1)

    def _build_section_container(self, title, content_control):
        return ft.Container(
            bgcolor=ft.Colors.WHITE,
            padding=20,
            border_radius=12,
            border=ft.border.all(1, ft.Colors.GREY_200),
            content=ft.Column(
                [
                    ft.Text(title, weight="bold", size=16, color=ft.Colors.BLACK),
                    ft.Divider(height=20, color="transparent"),
                    content_control,
                ]
            ),
        )
