import flet as ft
import time
import threading
from datetime import datetime

from flet.core.types import MainAxisAlignment

from ArtemusPark.config.Colors import AppColors
from ArtemusPark.config.Sensor_Config import SENSOR_CONFIG
from ArtemusPark.service.Dashboard_Service import DashboardService
from ArtemusPark.repository import (
    Light_Repository,
    Temperature_Repository,
    Door_Repository,
)
from ArtemusPark.repository.Auth_Repository import AuthRepository
from ArtemusPark.repository.Requests_Repository import RequestsRepository


class AdminPage(ft.Container):
    def __init__(self, user_role="admin", current_username=None):
        super().__init__()
        self.expand = True
        self.padding = 20
        self.bgcolor = AppColors.BG_MAIN

        self.service = DashboardService()
        self.auth_repo = AuthRepository()
        self.req_repo = RequestsRepository()
        self.simulation_running = False
        # Guardamos el nombre del usuario actual
        self.current_username = current_username if current_username else "Admin"

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
                            # Usamos f-string para que el avatar dependa del usuario actual
                            ft.CircleAvatar(
                                foreground_image_src=f"https://ui-avatars.com/api/?name={self.current_username}&background=0D8ABC&color=fff",
                                radius=30,
                            ),
                            ft.Column(
                                [
                                    # Mostramos el nombre del usuario real
                                    ft.Text(
                                        self.current_username,
                                        weight="bold",
                                        size=16,
                                        color=ft.Colors.BLACK,
                                    ),
                                    ft.Text(
                                        # Podemos asumir un email ficticio basado en el usuario
                                        f"{self.current_username.lower()}@artemus.park",
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
                                        icon=ft.Icons.INFO_OUTLINE,
                                        icon_color=ft.Colors.BLUE_GREY,
                                        tooltip="Ver datos",
                                        on_click=lambda e, u=username: self._open_user_details_dialog(
                                            u
                                        ),
                                    ),
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

    def _open_user_details_dialog(self, username):
        users = self.auth_repo.get_all_users()
        user_data = users.get(username, {})
        assigned = user_data.get("assigned_sensors", [])
        assigned_text = ", ".join(assigned) if assigned else "Sin asignaciones"
        supervisors = self._get_supervisors_for_user(username, users)
        supervisors_text = (
            ", ".join(sorted(supervisors)) if supervisors else "Sin supervisores"
        )
        subordinates = user_data.get("subordinates", [])
        subordinates_text = (
            ", ".join(sorted(subordinates)) if subordinates else "Sin subordinados"
        )

        dialog = ft.AlertDialog(
            title=ft.Text(f"Datos de {username}"),
            content=ft.Column(
                [
                    ft.Text(f"Rol: {user_data.get('role', '-')}"),
                    ft.Text(f"Nombre completo: {user_data.get('full_name', '-')}"),
                    ft.Text(f"DNI: {user_data.get('dni', '-')}"),
                    ft.Text(f"Telefono: {user_data.get('phone', '-')}"),
                    ft.Text(f"Direccion: {user_data.get('address', '-')}"),
                    ft.Text(f"Sensores asignados: {assigned_text}"),
                    ft.Text(f"Supervisores: {supervisors_text}"),
                    ft.Text(f"Subordinados: {subordinates_text}"),
                ],
                width=360,
                tight=True,
            ),
            actions=[
                ft.TextButton("Cerrar", on_click=lambda e: self.page.close(dialog)),
            ],
        )
        self.page.open(dialog)

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

        # Profile fields (mandatory for ALL roles now)
        tf_full_name = ft.TextField(
            label="Nombre Completo", value=user_data.get("full_name", "")
        )
        tf_dni = ft.TextField(label="DNI", value=user_data.get("dni", ""))
        tf_phone = ft.TextField(label="Teléfono", value=user_data.get("phone", ""))
        tf_address = ft.TextField(label="Dirección", value=user_data.get("address", ""))

        profile_section = ft.Column(
            [
                ft.Text("Datos Personales (Obligatorios):", weight="bold"),
                tf_full_name,
                tf_dni,
                tf_phone,
                tf_address,
                ft.Divider(),
            ],
        )

        def handle_first_step_save(e):
            if (
                    not tf_user.value
                    or not tf_pass.value
                    or not dd_role.value
                    or not tf_full_name.value
                    or not tf_dni.value
                    or not tf_phone.value
                    or not tf_address.value
            ):
                self.page.open(
                    ft.SnackBar(
                        content=ft.Text("Todos los campos son obligatorios", color=AppColors.TEXT_WHITE),
                        bgcolor=ft.Colors.RED,
                    )
                )
                return

            # DNI Validation
            if not self._is_valid_dni(tf_dni.value):
                self.page.open(
                    ft.SnackBar(
                        content=ft.Text("DNI inválido. Debe tener 8 números y letra correcta.",
                                        color=AppColors.TEXT_WHITE),
                        bgcolor=ft.Colors.RED,
                    )
                )
                return

            # Phone Validation
            if not tf_phone.value.strip().isdigit() or len(tf_phone.value.strip()) != 9:
                self.page.open(
                    ft.SnackBar(
                        content=ft.Text("Teléfono inválido. Debe contener 9 dígitos numéricos.",
                                        color=AppColors.TEXT_WHITE),
                        bgcolor=ft.Colors.RED,
                    )
                )
                return

            # Prepare data payload
            user_payload = {
                "username": tf_user.value,
                "password": tf_pass.value,
                "role": dd_role.value,
                "full_name": tf_full_name.value,
                "dni": tf_dni.value,
                "phone": tf_phone.value,
                "address": tf_address.value,
                "is_edit": is_edit,
                "original_username": username,
            }

            if dd_role.value == "user":
                # User role doesn't need technical dialog, save directly
                self._save_final(user_payload)
                self.page.close(dialog)
            else:
                # Maintenance/Admin need 2nd step
                self.page.close(dialog)
                self._open_technical_dialog(user_payload)

        dialog = ft.AlertDialog(
            title=ft.Text("Editar Usuario" if is_edit else "Nuevo Usuario"),
            content=ft.Column(
                [
                    tf_user,
                    tf_pass,
                    dd_role,
                    ft.Divider(),
                    profile_section,
                ],
                height=400,
                width=350,
                scroll=ft.ScrollMode.AUTO,
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self.page.close(dialog)),
                ft.ElevatedButton(
                    "Siguiente" if dd_role.value != "user" else "Guardar",
                    on_click=handle_first_step_save,
                ),
            ],
        )

        def on_role_change(e):
            dialog.actions[1].text = (
                "Siguiente" if dd_role.value != "user" else "Guardar"
            )
            dialog.update()

        dd_role.on_change = on_role_change
        self.page.open(dialog)

    def _open_technical_dialog(self, user_payload):
        users = self.auth_repo.get_all_users()
        username = user_payload.get("original_username")
        user_data = users.get(username, {}) if user_payload["is_edit"] else {}
        role = user_payload["role"]

        content_controls = []

        # Sensors (for maintenance)
        sensor_checks = []
        if role == "maintenance":
            assigned = user_data.get("assigned_sensors", [])

            def on_sensor_change(e):
                checked_count = sum(1 for c in sensor_checks if isinstance(c, ft.Checkbox) and c.value)
                if checked_count > 3:
                    e.control.value = False
                    e.control.update()
                    self.page.open(
                        ft.SnackBar(
                            content=ft.Text(
                                "Máximo 3 sensores permitidos",
                                color=AppColors.TEXT_WHITE,
                            ),
                            bgcolor=ft.Colors.RED,
                        )
                    )

            for s_type, s_list in SENSOR_CONFIG.items():
                # Reemplazo de continue: Si s_list no está vacío, procesamos
                if s_list:
                    sensor_checks.append(ft.Text(f"{s_type.capitalize()}:", weight=ft.FontWeight.BOLD, size=12))

                    for sensor in s_list:
                        s_id = sensor["id"]
                        s_name = sensor["name"]
                        is_checked = s_id in assigned

                        cb = ft.Checkbox(
                            label=f"{s_name} ({s_id})",
                            value=is_checked,
                            data=s_id,  # Store ID in data
                            on_change=on_sensor_change,
                        )
                        sensor_checks.append(cb)

            content_controls.append(
                ft.Column(
                    [
                        ft.Text("Lista de Componentes (Selecione ID):", weight="bold"),
                        ft.Container(
                            content=ft.Column(sensor_checks, spacing=0, scroll=ft.ScrollMode.AUTO),
                            height=200,  # Limit height for scroll
                            border=ft.border.all(1, ft.Colors.GREY_300),
                            padding=5,
                            border_radius=5
                        ),
                        ft.Divider(),
                    ]
                )
            )

        # Supervision/Subordinates logic
        supervisor_checks = []
        subordinate_checks = []

        if role == "maintenance":
            supervisor_candidates = [
                u for u, d in users.items() if d.get("role") == "admin"
            ]  # Can be supervised by any admin
            current_supervisors = (
                self._get_supervisors_for_user(username, users)
                if user_payload["is_edit"]
                else set()
            )

            for sup in supervisor_candidates:
                # Reemplazo de continue: Evitar auto-referencia si el rol cambió
                if sup != user_payload["username"]:
                    supervisor_checks.append(
                        ft.Checkbox(label=sup, value=(sup in current_supervisors))
                    )

            content_controls.append(
                ft.Column(
                    [
                        ft.Text(
                            "¿Por quién va a ser supervisado? (Supervisores):", weight="bold"
                        ),
                        ft.Column(supervisor_checks, spacing=0),
                    ]
                )
            )

        if role == "admin":
            subordinate_candidates = [
                u for u, d in users.items() if d.get("role") == "user"
            ]
            current_subordinates = set(user_data.get("subordinates", []))

            for sub in subordinate_candidates:
                subordinate_checks.append(
                    ft.Checkbox(label=sub, value=(sub in current_subordinates))
                )

            content_controls.append(
                ft.Column(
                    [
                        ft.Text("Usuarios subordinados:", weight="bold"),
                        ft.Column(subordinate_checks, spacing=0),
                    ]
                )
            )

        def save_second_step(e):
            selected_sensors = [c.data for c in sensor_checks if isinstance(c, ft.Checkbox) and c.value]
            selected_supervisors = [c.label for c in supervisor_checks if c.value]
            selected_subordinates = [c.label for c in subordinate_checks if c.value]

            final_payload = user_payload.copy()
            final_payload["assigned_sensors"] = selected_sensors
            final_payload["selected_supervisors"] = selected_supervisors
            final_payload["selected_subordinates"] = selected_subordinates

            self._save_final(final_payload)
            self.page.close(dialog)

        dialog = ft.AlertDialog(
            title=ft.Text(f"Configuración Técnica ({role})"),
            content=ft.Column(
                content_controls, height=400, width=350, scroll=ft.ScrollMode.AUTO
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self.page.close(dialog)),
                ft.ElevatedButton("Guardar", on_click=save_second_step),
            ],
        )
        self.page.open(dialog)

    def _save_final(self, payload):
        try:
            username = payload["username"]
            is_edit = payload["is_edit"]
            original_username = payload.get("original_username")

            # Default empty lists if not present (e.g. user role)
            assigned_sensors = payload.get("assigned_sensors", [])
            selected_supervisors = payload.get("selected_supervisors", [])
            selected_subordinates = payload.get("selected_subordinates", [])

            if is_edit:
                # Use original_username for key update in case username changed (not supported yet fully but good practice)
                target_user = original_username if original_username else username
                self.auth_repo.update_user(
                    target_user,
                    password=payload["password"],
                    role=payload["role"],
                    assigned_sensors=assigned_sensors,
                    full_name=payload["full_name"],
                    dni=payload["dni"],
                    phone=payload["phone"],
                    address=payload["address"],
                )
            else:
                self.auth_repo.add_user(
                    username,
                    payload["password"],
                    payload["role"],
                    full_name=payload["full_name"],
                    dni=payload["dni"],
                    phone=payload["phone"],
                    address=payload["address"],
                )
                self.auth_repo.update_user(
                    username, assigned_sensors=assigned_sensors
                )

            target_username = original_username if is_edit else username
            role = payload["role"]

            if role == "admin":
                self._sync_subordinates(target_username, selected_subordinates)
                # Clear supervisors if switching to admin
                self.auth_repo.update_user(target_username, supervisors=[])
            elif role == "maintenance":
                # Maintenance logic for supervisors
                self._sync_supervisors(target_username, selected_supervisors)
                self.auth_repo.update_user(target_username, subordinates=[])
            else:  # User
                self.auth_repo.update_user(target_username, supervisors=[], subordinates=[])

            self._load_users()
            self.page.open(
                ft.SnackBar(
                    content=ft.Text("Usuario guardado correctamente", color="white"),
                    bgcolor=ft.Colors.GREEN_700,
                )
            )
        except Exception as ex:
            self.page.open(
                ft.SnackBar(
                    content=ft.Text(f"Error: {str(ex)}", color="white"),
                    bgcolor=ft.Colors.RED_700,
                )
            )

    def _get_supervisors_for_user(self, username, users):
        supervisors = set(users.get(username, {}).get("supervisors", []))
        for sup_name, sup_data in users.items():
            if sup_data.get("role") == "admin":
                if username in sup_data.get("subordinates", []):
                    supervisors.add(sup_name)
        return supervisors

    def _sync_supervisors(self, username, selected_supervisors):
        users = self.auth_repo.get_all_users()
        admin_users = [u for u, d in users.items() if d.get("role") == "admin"]
        for sup in admin_users:
            subs = set(users.get(sup, {}).get("subordinates", []))
            if sup in selected_supervisors:
                subs.add(username)
            else:
                subs.discard(username)
            self.auth_repo.update_user(sup, subordinates=list(subs))
        self.auth_repo.update_user(username, supervisors=selected_supervisors)

    def _sync_subordinates(self, supervisor, selected_subordinates):
        self.auth_repo.update_user(supervisor, subordinates=selected_subordinates)
        users = self.auth_repo.get_all_users()
        user_accounts = [u for u, d in users.items() if d.get("role") == "user"]
        for user in user_accounts:
            sups = set(users.get(user, {}).get("supervisors", []))
            if user in selected_subordinates:
                sups.add(supervisor)
            else:
                sups.discard(supervisor)
            self.auth_repo.update_user(user, supervisors=list(sups))

    def _delete_user(self, username):
        def confirm_delete(e):
            self.auth_repo.delete_user(username)
            self.page.close(dialog)
            self._load_users()
            self.page.open(
                ft.SnackBar(
                    content=ft.Text(f"Usuario {username} eliminado", color="white"),
                    bgcolor=ft.Colors.RED_700,
                )
            )

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
            values = [p.y for p in self.energy_data_points]
            if values:
                min_val = min(values)
                max_val = max(values)
                padding = 50
                self.chart.min_y = max(0, min_val - padding)
                self.chart.max_y = max_val + padding
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
                # Ignoramos errores de actualización de UI si la página ya no está activa
                ...
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

    def _is_valid_dni(self, dni):
        """Valida formato y letra de DNI español (8 dígitos + letra)."""
        if not dni:
            return False
        dni = dni.strip().upper()
        if len(dni) != 9:
            return False
        if not dni[:8].isdigit() or not dni[8].isalpha():
            return False
        letters = "TRWAGMYFPDXBNJZSQVHLCKE"
        number = int(dni[:8])
        return dni[8] == letters[number % 23]