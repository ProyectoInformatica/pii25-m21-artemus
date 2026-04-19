import flet as ft
import time
import threading
import base64
import os
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
    def __init__(self, user_role="admin", current_username=None, permissions=None):
        super().__init__()
        self.expand = True
        self.padding = 20
        self.bgcolor = AppColors.BG_MAIN

        self.service = DashboardService()
        self.auth_repo = AuthRepository()
        self.req_repo = RequestsRepository()
        self.simulation_running = False
        self.current_username = current_username
        self.permissions = permissions or []

        self.file_picker = ft.FilePicker(on_result=self._on_file_result)
        self.save_file_picker = ft.FilePicker(on_result=self._on_export_result)

        self.selected_image_bytes = None
        self.img_preview = ft.Image(
            src="",
            width=100,
            height=100,
            fit=ft.ImageFit.COVER,
            border_radius=50,
            visible=False,
        )

        if "MANAGE_USERS" not in self.permissions and user_role != "admin":
            self.content = ft.Center(
                ft.Text(
                    "No tienes permisos de Administrador",
                    size=24,
                    color=ft.Colors.BLACK,
                )
            )
            return

        # --- USER MANAGEMENT TABLE ---
        self.users_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Usuario", color=ft.Colors.BLACK)),
                ft.DataColumn(ft.Text("Rol", color=ft.Colors.BLACK)),
                ft.DataColumn(ft.Text("", color=ft.Colors.BLACK)),
            ],
            rows=[],
            width=float("inf"),
        )

        # --- CHART COMPONENTS ---
        self.energy_data_points = [ft.LineChartDataPoint(i, 50) for i in range(20)]
        now_str = datetime.now().strftime("%H:%M:%S")
        self.time_labels = [now_str for _ in range(20)]

        can_emergency = "VIEW_SECURITY_LOGS" in self.permissions or user_role == "admin"
        self.btn_catastrophe = ft.ElevatedButton(
            text="CARGANDO ESTADO...",
            icon=ft.Icons.WARNING_AMBER_ROUNDED,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                shape=ft.RoundedRectangleBorder(radius=10),
                padding=20,
            ),
            width=400,
            disabled=not can_emergency,
            on_click=self._toggle_catastrophe,
        )

        self.btn_export = ft.ElevatedButton(
            "Exportar Reporte de Sensores (PDF)",
            icon=ft.Icons.PICTURE_AS_PDF,
            on_click=self._start_export_flow,
            visible="EXPORT_DATA_REPORTS" in self.permissions,
            bgcolor=ft.Colors.ORANGE_800,
            color=ft.Colors.WHITE,
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

        # SECTIONS ASSEMBLY
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

        emergency_section = self._build_section_container(
            "Protocolos y Reportes",
            ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    self.btn_catastrophe,
                    ft.Container(height=10),
                    self.btn_export,
                ],
            ),
        )

        energy_section = self._build_section_container(
            "Monitor Energético",
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
                                    [self.txt_energy_value, self.txt_energy_detail],
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

        # MAIN LAYOUT
        left_column = ft.Column(expand=1, spacing=20, controls=[user_mgmt_section])
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
                self._build_admin_profile_section(),
                ft.Row(
                    controls=[left_column, right_column],
                    spacing=20,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                ),
            ],
        )

    def did_mount(self):
        if self.page:
            if self.file_picker not in self.page.overlay:
                self.page.overlay.append(self.file_picker)
            if self.save_file_picker not in self.page.overlay:
                self.page.overlay.append(self.save_file_picker)
            self.page.pubsub.subscribe(self._on_message)
            self.page.update()
        self.simulation_running = True
        self._update_button_state()
        self._load_users()
        if self.service.is_catastrophe_mode():
            self.bgcolor = ft.Colors.RED_900
        threading.Thread(target=self._realtime_energy_loop, daemon=True).start()

    def _on_file_result(self, e: ft.FilePickerResultEvent):
        if e.files:
            file_path = e.files[0].path
            with open(file_path, "rb") as f:
                self.selected_image_bytes = f.read()
            self.img_preview.src_base64 = base64.b64encode(
                self.selected_image_bytes
            ).decode("utf-8")
            self.img_preview.visible = True
            self.img_preview.update()

    def _start_export_flow(self, e):
        if not self.page:
            return

        try:
            if self.save_file_picker not in self.page.overlay:
                self.page.overlay.append(self.save_file_picker)

            self.page.open(
                ft.SnackBar(
                    content=ft.Text("Abriendo selector de ubicación para exportar PDF..."),
                    bgcolor=ft.Colors.BLUE_700,
                )
            )
            self.page.update()
            self.save_file_picker.save_file(
                dialog_title="Guardar reporte de sensores",
                file_name="Reporte_Artemus.pdf",
                file_type=ft.FilePickerFileType.CUSTOM,
                allowed_extensions=["pdf"],
            )
        except Exception as ex:
            self.page.open(
                ft.SnackBar(
                    content=ft.Text(f"No se pudo abrir el selector de archivo: {ex}"),
                    bgcolor=ft.Colors.RED_700,
                )
            )



    def _on_export_result(self, e: ft.FilePickerResultEvent):
        if not e.path:
            self.page.open(
                ft.SnackBar(
                    content=ft.Text("Exportación cancelada o no se recibió una ruta de guardado."),
                    bgcolor=ft.Colors.ORANGE_700,
                )
            )
            return

        try:
            report_rows = self.service.get_sensors_health_status()
            output_path = e.path if e.path.lower().endswith(".pdf") else f"{e.path}.pdf"
            self._export_sensor_report_pdf(output_path, report_rows)
            self.page.open(
                ft.SnackBar(
                    content=ft.Text(f"Reporte exportado con éxito en: {output_path}"),
                    bgcolor=ft.Colors.GREEN_700,
                )
            )
        except Exception as ex:
            self.page.open(
                ft.SnackBar(
                    content=ft.Text(f"Error al exportar reporte: {ex}"),
                    bgcolor=ft.Colors.RED_700,
                )
            )

    def _export_sensor_report_pdf(self, output_path, report_rows):
        pdf_bytes = self._build_simple_pdf(report_rows, output_path)
        with open(output_path, "wb") as pdf_file:
            pdf_file.write(pdf_bytes)


    def _build_simple_pdf(self, report_rows, output_path=None):
        report_title = "Reporte de Sensores Artemus"
        _ = os.path.basename(output_path) if isinstance(output_path, str) else "Reporte_Artemus.pdf"

        generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        lines = [
            report_title,
            f"Generado: {generated_at}",
            "",
        ]

        if not report_rows:
            lines.append("No hay datos de sensores disponibles.")
        else:
            for index, row in enumerate(report_rows, start=1):
                if isinstance(row, dict):
                    sensor_name = row.get("name") or row.get("sensor") or row.get("id") or f"Sensor {index}"
                    sensor_type = row.get("type", "-")
                    sensor_status = row.get("status", "-")
                    last_seen = row.get("last_seen", "-")
                    last_value = row.get("last_value", "-")
                else:
                    sensor_name = f"Sensor {index}"
                    sensor_type = "-"
                    sensor_status = str(row)
                    last_seen = "-"
                    last_value = "-"

                lines.extend(
                    [
                        f"{index}. {sensor_name}",
                        f"   Tipo: {sensor_type}",
                        f"   Estado: {sensor_status}",
                        f"   Ultima lectura: {last_value}",
                        f"   Ultima vez visto: {last_seen}",
                        "",
                    ]
                )

        return self._create_basic_pdf(lines)


    def _create_basic_pdf(self, lines):
        def escape_pdf_text(text):
            return (
                str(text)
                .replace("\\", "\\\\")
                .replace("(", "\\(")
                .replace(")", "\\)")
            )

        page_width = 595
        page_height = 842
        start_y = 800
        line_height = 16
        margin_bottom = 40

        pages = []
        current_page = []
        current_y = start_y

        for line in lines:
            safe_line = escape_pdf_text(line)
            current_page.append(f"BT /F1 11 Tf 40 {current_y} Td ({safe_line}) Tj ET")
            current_y -= line_height
            if current_y < margin_bottom:
                pages.append("\n".join(current_page))
                current_page = []
                current_y = start_y

        if current_page:
            pages.append("\n".join(current_page))

        if not pages:
            pages.append("BT /F1 11 Tf 40 800 Td (Sin datos) Tj ET")

        objects = []
        page_object_numbers = []

        objects.append("1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj")

        kids_refs = []
        next_object_number = 3
        font_object_number = 3 + (2 * len(pages))

        for _ in pages:
            page_object_number = next_object_number
            content_object_number = next_object_number + 1
            page_object_numbers.append(page_object_number)
            kids_refs.append(f"{page_object_number} 0 R")
            next_object_number += 2

        objects.append(
            f"2 0 obj << /Type /Pages /Count {len(pages)} /Kids [{' '.join(kids_refs)}] >> endobj"
        )

        for page_object_number, page_content in zip(page_object_numbers, pages):
            content_object_number = page_object_number + 1
            content_bytes = page_content.encode("latin-1", errors="replace")

            objects.append(
                f"{page_object_number} 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 {page_width} {page_height}] /Resources << /Font << /F1 {font_object_number} 0 R >> >> /Contents {content_object_number} 0 R >> endobj"
            )
            objects.append(
                f"{content_object_number} 0 obj << /Length {len(content_bytes)} >> stream\n{page_content}\nendstream endobj"
            )

        objects.append(
            f"{font_object_number} 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj"
        )

        pdf_parts = [b"%PDF-1.4\n"]
        offsets = [0]
        current_offset = len(pdf_parts[0])

        for obj in objects:
            obj_bytes = (obj + "\n").encode("latin-1", errors="replace")
            offsets.append(current_offset)
            pdf_parts.append(obj_bytes)
            current_offset += len(obj_bytes)

        xref_offset = current_offset
        xref_lines = [f"xref\n0 {len(offsets)}\n", "0000000000 65535 f \n"]
        for offset in offsets[1:]:
            xref_lines.append(f"{offset:010d} 00000 n \n")

        trailer = (
            f"trailer << /Size {len(offsets)} /Root 1 0 R >>\n"
            f"startxref\n{xref_offset}\n%%EOF"
        )

        pdf_parts.append("".join(xref_lines).encode("latin-1"))
        pdf_parts.append(trailer.encode("latin-1"))
        return b"".join(pdf_parts)

    def _on_message(self, message):
        if message == "catastrophe_mode":
            self.bgcolor = ft.Colors.RED_900
            try:
                self.update()
            except:
                pass
        elif message == "normal_mode":
            self.bgcolor = AppColors.BG_MAIN
            try:
                self.update()
            except:
                pass

    def will_unmount(self):
        self.simulation_running = False

    def _load_users(self):
        users = self.auth_repo.get_all_users()
        self.users_table.rows.clear()
        for username, data in users.items():
            is_me = username == self.current_username
            display_name = f"{username } (Tú)" if is_me else username
            delete_btn = ft.IconButton(
                icon=ft.Icons.DELETE,
                icon_color=ft.Colors.RED if not is_me else ft.Colors.GREY,
                disabled=is_me,
                on_click=lambda e, u=username: self._delete_user(u),
            )
            self.users_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(display_name, color=ft.Colors.BLACK)),
                        ft.DataCell(ft.Text(data["role"], color=ft.Colors.BLACK)),
                        ft.DataCell(
                            ft.Row(
                                [
                                    ft.IconButton(
                                        ft.Icons.INFO_OUTLINE,
                                        icon_color=ft.Colors.BLUE_GREY,
                                        on_click=lambda e, u=username: self._open_user_details_dialog(
                                            u
                                        ),
                                    ),
                                    ft.IconButton(
                                        ft.Icons.EDIT,
                                        icon_color=ft.Colors.BLUE,
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
        try:
            self.users_table.update()
        except:
            pass

    def _open_user_details_dialog(self, username):
        users = self.auth_repo.get_all_users()
        udata = users.get(username, {})
        assigned = udata.get("assigned_sensors", [])
        assigned_text = ", ".join(assigned) if assigned else "Sin asignaciones"
        perms = udata.get("permissions", [])
        perms_text = ", ".join(perms) if perms else "Sin permisos específicos"

        dialog = ft.AlertDialog(
            title=ft.Text(f"Detalles de {username}"),
            content=ft.Column(
                [
                    ft.Text(f"Rol: {udata.get('role','-')}"),
                    ft.Text(f"Nombre: {udata.get('full_name','-')}"),
                    ft.Text(f"DNI: {udata.get('dni','-')}"),
                    ft.Text(f"Teléfono: {udata.get('phone','-')}"),
                    ft.Text(
                        f"Permisos: {perms_text}", size=12, color=ft.Colors.BLUE_GREY
                    ),
                    ft.Text(f"Sensores: {assigned_text}", size=12),
                ],
                width=360,
                tight=True,
            ),
            actions=[
                ft.TextButton("Cerrar", on_click=lambda e: self.page.close(dialog))
            ],
        )
        self.page.open(dialog)

    def _open_user_dialog(self, username=None):
        users = self.auth_repo.get_all_users()
        is_edit = username is not None
        user_data = users.get(username, {}) if is_edit else {}

        tf_user = ft.TextField(
            label="Usuario", value=username if is_edit else "", disabled=is_edit
        )
        tf_pass = ft.TextField(
            label="Contraseña",
            value="",
            password=True,
            can_reveal_password=True,
            hint_text="Dejar vacío para no cambiar" if is_edit else "",
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
        tf_full_name = ft.TextField(
            label="Nombre Completo", value=user_data.get("full_name", "")
        )
        tf_dni = ft.TextField(
            label="DNI", value=user_data.get("dni", ""), disabled=is_edit
        )
        tf_phone = ft.TextField(label="Teléfono", value=user_data.get("phone", ""))
        tf_street = ft.TextField(
            label="Dirección", value=user_data.get("address_street", "")
        )
        tf_city = ft.TextField(label="Ciudad", value=user_data.get("address_city", ""))
        tf_zip = ft.TextField(label="C.P.", value=user_data.get("address_zip", ""))

        def handle_next(e):
            if not is_edit and not all([tf_user.value, tf_pass.value, tf_dni.value]):
                self.page.open(
                    ft.SnackBar(
                        content=ft.Text("Usuario, contraseña y DNI son obligatorios")
                    )
                )
                return

            user_payload = {
                "username": tf_user.value,
                "password": tf_pass.value,
                "role": dd_role.value,
                "full_name": tf_full_name.value,
                "dni": tf_dni.value,
                "phone": tf_phone.value,
                "address_street": tf_street.value,
                "address_city": tf_city.value,
                "address_zip": tf_zip.value,
                "is_edit": is_edit,
                "original_username": username,
                "current_perms": user_data.get("permissions", []),
                "assigned_sensors": user_data.get("assigned_sensors", []),
            }
            self.page.close(dialog)
            self._open_technical_dialog(user_payload)

        dialog = ft.AlertDialog(
            title=ft.Text("Editar Usuario" if is_edit else "Nuevo Usuario"),
            content=ft.Column(
                [
                    tf_user,
                    tf_pass,
                    dd_role,
                    tf_full_name,
                    tf_dni,
                    tf_phone,
                    tf_street,
                    tf_city,
                    tf_zip,
                ],
                height=400,
                width=350,
                scroll=ft.ScrollMode.AUTO,
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self.page.close(dialog)),
                ft.ElevatedButton("Siguiente", on_click=handle_next),
            ],
        )
        self.page.open(dialog)

    def _open_technical_dialog(self, user_payload):
        all_perms = self.auth_repo.get_all_permissions()
        current_perms = set(user_payload.get("current_perms", []))
        perm_checks = [
            ft.Checkbox(label=p, value=(p in current_perms), data=p) for p in all_perms
        ]

        sensor_checks = []
        if user_payload["role"] == "maintenance":
            assigned = user_payload.get("assigned_sensors", [])
            for s_type, s_list in SENSOR_CONFIG.items():
                sensor_checks.append(
                    ft.Text(f"{s_type.capitalize()}:", weight="bold", size=12)
                )
                for s in s_list:
                    sensor_checks.append(
                        ft.Checkbox(
                            label=f"{s['name']} ({s['id']})",
                            value=(s["id"] in assigned),
                            data=s["id"],
                        )
                    )

        def save_all(e):
            user_payload["permissions"] = [c.data for c in perm_checks if c.value]
            user_payload["assigned_sensors"] = [
                c.data for c in sensor_checks if isinstance(c, ft.Checkbox) and c.value
            ]
            self._save_final(user_payload)
            self.page.close(dialog)

        dialog = ft.AlertDialog(
            title=ft.Text("Configuración de Permisos y Sensores"),
            content=ft.Column(
                [
                    ft.Text("Permisos Individuales:", weight="bold"),
                    ft.Container(
                        content=ft.Column(perm_checks, spacing=0),
                        height=200,
                        scroll=ft.ScrollMode.AUTO,
                        border=ft.border.all(1, ft.Colors.GREY_300),
                        padding=5,
                    ),
                    ft.Divider(),
                    ft.Text(
                        "Sensores Asignados:",
                        weight="bold",
                        visible=user_payload["role"] == "maintenance",
                    ),
                    ft.Container(
                        content=ft.Column(sensor_checks, spacing=0),
                        height=150,
                        scroll=ft.ScrollMode.AUTO,
                        visible=user_payload["role"] == "maintenance",
                        border=ft.border.all(1, ft.Colors.GREY_300),
                        padding=5,
                    ),
                ],
                height=450,
                width=400,
            ),
            actions=[
                ft.TextButton(
                    "Atrás",
                    on_click=lambda e: (
                        self.page.close(dialog),
                        self._open_user_dialog(user_payload["original_username"]),
                    ),
                ),
                ft.ElevatedButton("Guardar Todo", on_click=save_all),
            ],
        )
        self.page.open(dialog)

    def _save_final(self, payload):
        try:
            dni = payload["dni"]
            update_data = {
                "role": payload["role"],
                "full_name": payload["full_name"],
                "phone": payload["phone"],
                "address_street": payload["address_street"],
                "address_city": payload["address_city"],
                "address_zip": payload["address_zip"],
                "assigned_sensors": payload.get("assigned_sensors", []),
                "permissions": payload.get("permissions", []),
            }
            if payload["password"]:
                update_data["password"] = payload["password"]

            if payload["is_edit"]:
                self.auth_repo.update_user(dni, **update_data)
            else:
                self.auth_repo.add_user(
                    payload["username"],
                    payload["password"],
                    payload["role"],
                    permissions=payload["permissions"],
                    **{
                        k: v
                        for k, v in payload.items()
                        if k
                        not in [
                            "username",
                            "password",
                            "role",
                            "is_edit",
                            "original_username",
                            "permissions",
                            "current_perms",
                            "assigned_sensors",
                        ]
                    },
                )

            self._load_users()
            self.page.open(
                ft.SnackBar(
                    content=ft.Text("Usuario y permisos actualizados"),
                    bgcolor=ft.Colors.GREEN_700,
                )
            )
        except Exception as ex:
            self.page.open(
                ft.SnackBar(
                    content=ft.Text(f"Error al guardar: {ex}"),
                    bgcolor=ft.Colors.RED_700,
                )
            )

    def _delete_user(self, username):
        def confirm(e):
            udata = self.auth_repo.get_user_by_username(username)
            if udata:
                self.auth_repo.delete_user(udata["dni"])
            self.page.close(dialog)
            self._load_users()

        dialog = ft.AlertDialog(
            title=ft.Text("Eliminar"),
            content=ft.Text(f"¿Borrar {username}?"),
            actions=[
                ft.TextButton("No", on_click=lambda e: self.page.close(dialog)),
                ft.ElevatedButton("Sí", bgcolor="red", color="white", on_click=confirm),
            ],
        )
        self.page.open(dialog)

    def _toggle_catastrophe(self, e):
        is_active = self.service.is_catastrophe_mode()
        self.service.set_catastrophe_mode(not is_active)
        self.page.pubsub.send_all("normal_mode" if is_active else "catastrophe_mode")
        self._update_button_state()

    def _update_button_state(self):
        is_active = self.service.is_catastrophe_mode()
        self.btn_catastrophe.text = (
            "DESACTIVAR PROTOCOLO" if is_active else "ACTIVAR PROTOCOLO"
        )
        self.btn_catastrophe.bgcolor = (
            ft.Colors.GREEN_700 if is_active else ft.Colors.RED_700
        )
        self.btn_catastrophe.update()

    def _build_admin_profile_section(self):
        admin_full_name = "Super Admin"
        avatar_src_base64 = None
        if self.current_username:
            user_data = self.auth_repo.get_user_by_username(self.current_username)
            admin_full_name = user_data.get("full_name", admin_full_name)
            profile_pic = self.auth_repo.get_user_profile_picture(self.current_username)
            if profile_pic:
                avatar_src_base64 = base64.b64encode(profile_pic).decode("utf-8")
        self.admin_avatar = ft.CircleAvatar(
            content=(
                ft.Image(
                    src_base64=avatar_src_base64,
                    border_radius=30,
                    fit=ft.ImageFit.COVER,
                )
                if avatar_src_base64
                else ft.Icon(ft.Icons.PERSON)
            ),
            radius=30,
        )
        return self._build_section_container(
            "Perfil",
            ft.Row(
                [self.admin_avatar, ft.Text(admin_full_name, weight="bold")],
                alignment=ft.MainAxisAlignment.START,
            ),
        )

    def _realtime_energy_loop(self):
        while self.simulation_running:
            self.txt_energy_value.value = f"{50 + (time.time() % 100):.1f} kW"
            try:
                self.txt_energy_value.update()
            except:
                pass
            time.sleep(1)

    def _build_section_container(self, title, content_control, visible=True):
        return ft.Container(
            bgcolor=ft.Colors.WHITE,
            padding=20,
            border_radius=12,
            border=ft.border.all(1, ft.Colors.GREY_200),
            visible=visible,
            content=ft.Column(
                [
                    ft.Text(title, weight="bold", size=16, color=ft.Colors.BLACK),
                    ft.Divider(height=10, color="transparent"),
                    content_control,
                ]
            ),
        )

    def _is_valid_dni(self, dni):
        return len(dni) == 9
