import flet as ft
import json
from datetime import datetime
from ArtemusPark.config.Colors import AppColors
from ArtemusPark.config.Park_Config import OPEN_HOUR, CLOSE_HOUR
from ArtemusPark.repository.Chat_Repository import ChatRepository
from ArtemusPark.repository.Auth_Repository import AuthRepository
from ArtemusPark.service.Dashboard_Service import DashboardService
from ArtemusPark.service.Crypto_Service import CryptoService


class ChatPage(ft.Container):
    def __init__(
        self, current_username, current_user_role, permissions=None, private_key=None
    ):
        super().__init__()
        self.expand = True
        self.bgcolor = AppColors.BG_MAIN
        self.padding = 18

        self.username = current_username
        self.role = current_user_role
        self.permissions = permissions or []
        self.private_key = private_key

        self.chat_repo = ChatRepository()
        self.auth_repo = AuthRepository()
        self.dashboard_service = DashboardService()

        user_data = self.auth_repo.get_user_by_username(self.username)
        self.user_dni = user_data.get("dni", "")

        self.selected_chat_id = None
        self.chats = []
        self.messages = []
        self.is_group_selected = False

        # UI Components
        self.chat_list_column = ft.Column(scroll=ft.ScrollMode.ALWAYS, expand=True)
        self.messages_column = ft.Column(
            expand=True, spacing=10, scroll=ft.ScrollMode.ALWAYS, auto_scroll=False
        )

        self.search_input = ft.TextField(
            hint_text="Buscar mensajes...",
            prefix_icon=ft.Icons.SEARCH,
            border_radius=10,
            bgcolor="white",
            height=40,
            text_size=14,
            content_padding=10,
            on_change=self._handle_search,
        )

        self.message_input = ft.TextField(
            hint_text="Escribe un mensaje... (@Bot-Artemus estado)",
            expand=True,
            border_radius=20,
            bgcolor="white",
            color=ft.Colors.BLACK,
            on_submit=self._handle_send_click,
        )

        self.chat_header_text = ft.Text(
            "Selecciona un chat",
            weight=ft.FontWeight.BOLD,
            size=18,
            color=ft.Colors.BLACK,
        )

        # Actions for the selected chat
        self.btn_edit_name = ft.IconButton(
            ft.Icons.EDIT,
            tooltip="Editar nombre del chat",
            on_click=self._handle_edit_chat_name,
            visible=False,
        )
        self.btn_manage_members = ft.IconButton(
            ft.Icons.PEOPLE_OUTLINE,
            tooltip="Gestionar miembros",
            on_click=self._handle_manage_members,
            visible=False,
        )
        self.btn_leave_chat = ft.IconButton(
            ft.Icons.LOGOUT,
            tooltip="Salirse del grupo",
            icon_color=ft.Colors.ORANGE_700,
            on_click=self._handle_leave_chat,
            visible=False,
        )
        self.btn_delete_chat = ft.IconButton(
            ft.Icons.DELETE_OUTLINE,
            tooltip="Eliminar chat para todos",
            icon_color="red",
            on_click=self._handle_delete_chat,
            visible=False,
        )

        self.chat_actions = ft.Row(
            [
                self.btn_edit_name,
                self.btn_manage_members,
                self.btn_leave_chat,
                self.btn_delete_chat,
            ]
        )

        self.btn_scroll_bottom = ft.FloatingActionButton(
            icon=ft.Icons.KEYBOARD_ARROW_DOWN,
            on_click=lambda _: self.messages_column.scroll_to(offset=-1, duration=500),
            visible=False,
            mini=True,
            bgcolor=AppColors.ACCENT,
            opacity=0.8,
        )

        self.content = self._build_ui()

    def did_mount(self):
        self.page.pubsub.subscribe(self._on_message_received)
        self._refresh_chats()

    def _on_message_received(self, message):
        if message == "new_chat_message":
            if self.selected_chat_id:
                self._load_messages(self.selected_chat_id, scroll_to_bottom=True)
            self._refresh_chats()
        elif isinstance(message, dict) and message.get("topic") == "bot_alert":
            if self.selected_chat_id == 1:
                self._load_messages(1, scroll_to_bottom=True)

    def _refresh_chats(self):
        if not self.page:
            return
        self.chats = self.chat_repo.get_chats_for_user(self.user_dni)
        self.chat_list_column.controls.clear()

        for chat in self.chats:
            is_selected = chat["id_chat"] == self.selected_chat_id
            unread_count = chat.get("unread_count", 0)
            is_group = bool(chat.get("is_group", False))

            self.chat_list_column.controls.append(
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Icon(
                                ft.Icons.CHAT_BUBBLE_OUTLINE,
                                color=AppColors.ACCENT if not is_selected else "white",
                            ),
                            ft.Text(
                                chat["name"],
                                color=(
                                    AppColors.TEXT_MAIN if not is_selected else "white"
                                ),
                                weight=ft.FontWeight.BOLD if is_selected else None,
                                expand=True,
                            ),
                            ft.Container(
                                content=ft.Text(
                                    str(unread_count),
                                    color="white",
                                    size=10,
                                    weight="bold",
                                ),
                                bgcolor="red",
                                width=20,
                                height=20,
                                border_radius=10,
                                alignment=ft.alignment.center,
                                visible=unread_count > 0 and not is_selected,
                            ),
                        ]
                    ),
                    padding=10,
                    border_radius=10,
                    bgcolor=AppColors.ACCENT if is_selected else "white",
                    on_click=lambda e, cid=chat["id_chat"], cname=chat[
                        "name"
                    ], ig=is_group: self._select_chat(cid, cname, ig),
                    ink=True,
                )
            )
        try:
            self.update()
        except:
            pass

    def _select_chat(self, chat_id, chat_name, is_group=False):
        self.selected_chat_id = chat_id
        self.chat_header_text.value = chat_name
        self.is_group_selected = is_group
        self.btn_scroll_bottom.visible = True

        # PERMISSIONS SYSTEM
        can_manage_all = "MANAGE_CHATS" in self.permissions
        is_global = chat_id == 1

        if is_global:
            self.btn_edit_name.visible = can_manage_all
            self.btn_manage_members.visible = can_manage_all
            self.btn_leave_chat.visible = False
            self.btn_delete_chat.visible = can_manage_all
        elif is_group:
            self.btn_edit_name.visible = True
            self.btn_manage_members.visible = True
            self.btn_leave_chat.visible = True
            self.btn_delete_chat.visible = can_manage_all
        else:
            # Chat privado 1 a 1
            self.btn_edit_name.visible = False
            self.btn_manage_members.visible = False
            self.btn_leave_chat.visible = False
            self.btn_delete_chat.visible = True

        self.search_input.value = ""
        self._load_messages(chat_id)
        self._refresh_chats()
        self.page.pubsub.send_all("new_chat_message")

    def _handle_search(self, e):
        query = self.search_input.value.lower()
        if not self.selected_chat_id:
            return
        self._display_messages(query, scroll_to_bottom=False)

    def _load_messages(self, chat_id, scroll_to_bottom=True):
        if not self.page:
            return
        self.messages = self.chat_repo.get_messages_in_chat(chat_id, self.user_dni)
        self._display_messages(scroll_to_bottom=scroll_to_bottom)

    def _display_messages(self, filter_query="", scroll_to_bottom=True):
        self.messages_column.controls.clear()
        for msg in self.messages:
            content = msg["content"]
            is_encrypted_rsa = False

            # Intentar parsear como JSON para ver si es RSA
            try:
                data = json.loads(content)
                if isinstance(data, dict) and data.get("type") == "rsa":
                    payload = data.get("payload", {})
                    encrypted_val = payload.get(self.user_dni)
                    if encrypted_val and self.private_key:
                        content = CryptoService.decrypt_with_private_key(
                            encrypted_val, self.private_key
                        )
                        is_encrypted_rsa = True
                    else:
                        content = "[Mensaje cifrado para otro destinatario]"
            except:
                pass

            if filter_query and filter_query not in content.lower():
                continue

            is_me = msg["username"] == self.username
            alignment = (
                ft.MainAxisAlignment.END if is_me else ft.MainAxisAlignment.START
            )

            is_bot = msg.get("sender_dni") == "12345678X"
            is_alert = "⚠️ ALERTA" in content

            if is_alert:
                bg_color = ft.Colors.RED_100
            else:
                bg_color = (
                    AppColors.CHAT_OWNER_BG if is_me else AppColors.CHAT_INTERLOCUTOR_BG
                )

            if is_bot:
                sender_name = "Bot-Artemus"
            else:
                sender_name = msg["full_name"] or msg["username"]
                if is_me:
                    sender_name = f"{sender_name} (Tú)"

            if is_alert:
                msg_text_color = AppColors.CHAT_INTERLOCUTOR_TEXT
                msg_time_color = AppColors.CHAT_INTERLOCUTOR_TIME
                sender_color = ft.Colors.RED_700
            elif is_me:
                msg_text_color = AppColors.CHAT_OWNER_TEXT
                msg_time_color = AppColors.CHAT_OWNER_TIME
                sender_color = AppColors.ACCENT
            else:
                msg_text_color = AppColors.CHAT_INTERLOCUTOR_TEXT
                msg_time_color = AppColors.CHAT_INTERLOCUTOR_TIME
                sender_color = AppColors.CHAT_INTERLOCUTOR_NAME

            if is_alert:
                bubble_border = ft.border.all(2, ft.Colors.RED_700)
            else:
                bubble_border = None

            bubble_width = 320 if (is_alert or is_bot) else 300

            lock_icon = (
                ft.Icon(ft.Icons.LOCK_OUTLINE, size=10, color=msg_time_color)
                if is_encrypted_rsa
                else ft.Container()
            )

            self.messages_column.controls.append(
                ft.Row(
                    [
                        ft.Container(
                            content=ft.Column(
                                [
                                    (
                                        ft.Row(
                                            [
                                                ft.Text(
                                                    sender_name,
                                                    size=10,
                                                    weight=ft.FontWeight.BOLD,
                                                    color=sender_color,
                                                ),
                                                lock_icon,
                                            ],
                                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                            tight=True,
                                        )
                                        if not is_me
                                        else ft.Container()
                                    ),
                                    ft.Text(content, color=msg_text_color, width=280),
                                    ft.Text(
                                        msg["sent_at"].strftime("%H:%M"),
                                        size=9,
                                        color=msg_time_color,
                                        text_align=ft.TextAlign.RIGHT,
                                    ),
                                ],
                                spacing=2,
                                tight=True,
                            ),
                            padding=10,
                            border_radius=ft.border_radius.only(
                                top_left=15,
                                top_right=15,
                                bottom_left=15 if is_me else 0,
                                bottom_right=0 if is_me else 15,
                            ),
                            bgcolor=bg_color,
                            border=bubble_border,
                            width=bubble_width,
                        )
                    ],
                    alignment=alignment,
                )
            )
        try:
            self.update()
            if scroll_to_bottom:
                self.messages_column.scroll_to(offset=-1, duration=300)
        except:
            pass

    def _handle_send_click(self, e):
        # Check permission to send messages
        if "SEND_MESSAGES" not in self.permissions:
            self.page.open(
                ft.SnackBar(content=ft.Text("No tienes permiso para enviar mensajes"))
            )
            return

        text = self.message_input.value.strip()
        if not self.selected_chat_id or not text:
            return

        self.chat_repo.send_message(self.selected_chat_id, self.user_dni, text)
        self.message_input.value = ""
        self._load_messages(self.selected_chat_id, scroll_to_bottom=True)

        if text.lower().startswith("@bot-artemus"):
            self._process_bot_command(text)
            self._load_messages(self.selected_chat_id, scroll_to_bottom=True)

        self.page.pubsub.send_all("new_chat_message")
        self.message_input.focus()
        try:
            self.update()
        except:
            pass

    def _process_bot_command(self, text):
        cmd = text.lower().replace("@bot-artemus", "").strip()

        if "ayuda" in cmd or "help" in cmd or "comandos" in cmd:
            response = (
                "🤖 Comandos disponibles:\n"
                "• @Bot-Artemus estado — Sensores en tiempo real\n"
                "• @Bot-Artemus salud — Estado online/offline de sensores\n"
                "• @Bot-Artemus promedio — Medias históricas\n"
                "• @Bot-Artemus alarma — Estado de la alarma de emergencia\n"
                "• @Bot-Artemus ayuda — Esta ayuda"
            )

        elif "estado" in cmd or "sensores" in cmd:
            data = self.dashboard_service.get_latest_sensor_data()
            hora = datetime.now().hour
            parque = "Abierto" if OPEN_HOUR <= hora < CLOSE_HOUR else "Cerrado"
            response = (
                f"🤖 Estado Actual del Parque:\n"
                f"🏛️ Parque: {parque}\n"
                f"🌡️ Temp: {data['temperature']}°C\n"
                f"💧 Humedad: {data['humidity']}%\n"
                f"🌬️ Viento: {data['wind']} km/h\n"
                f"🌫️ Calidad Aire: {data['air_quality']} AQI\n"
                f"👥 Ocupación: {data['occupancy']} personas\n"
                f"💡 Luces: {'Encendidas' if data['light_is_on'] else 'Apagadas'}"
            )

        elif "salud" in cmd or "online" in cmd:
            health = self.dashboard_service.get_sensors_health_status()
            online = [s for s in health if s["is_online"]]
            offline = [s for s in health if not s["is_online"]]
            lines = [f"🤖 Salud de sensores ({len(online)}/{len(health)} online):"]
            for s in online:
                lines.append(f"  🟢 {s['name']} — {s['last_value']} ({s['last_seen']})")
            for s in offline:
                lines.append(f"  🔴 {s['name']} — Sin señal")
            response = "\n".join(lines)

        elif "promedio" in cmd or "media" in cmd:
            avg = self.dashboard_service.get_average_sensor_data()

            def fmt(v, unit):
                return f"{v}{unit}" if v is not None else "Sin datos"

            response = (
                f"🤖 Medias históricas:\n"
                f"🌡️ Temp media: {fmt(avg.get('temperature'), '°C')}\n"
                f"💧 Humedad media: {fmt(avg.get('humidity'), '%')}\n"
                f"🌬️ Viento medio: {fmt(avg.get('wind'), ' km/h')}\n"
                f"🌫️ Aire medio: {fmt(avg.get('air_quality'), ' AQI')}"
            )

        elif "alarma" in cmd or "emergencia" in cmd or "catastrofe" in cmd:
            activa = self.dashboard_service.is_catastrophe_mode()
            if activa:
                response = "🚨 ALARMA ACTIVA: El modo de catástrofe está activado."
            else:
                response = "✅ Sin alarma: El parque opera con normalidad."

        else:
            response = (
                "❓ Comando no reconocido. "
                "Escribe @Bot-Artemus ayuda para ver los comandos disponibles."
            )

        self.chat_repo.send_message(self.selected_chat_id, "12345678X", response)

    def _handle_share_status(self, e):
        if "SEND_MESSAGES" not in self.permissions:
            return
        if not self.selected_chat_id:
            return
        data = self.dashboard_service.get_latest_sensor_data()
        msg = (
            f"📍 Reporte de Sensores compartido por {self.username}:\n"
            f"• Temperatura: {data['temperature']}°C\n"
            f"• Viento: {data['wind']} km/h\n"
            f"• Ocupación: {data['occupancy']}"
        )
        self.chat_repo.send_message(self.selected_chat_id, self.user_dni, msg)
        self._load_messages(self.selected_chat_id, scroll_to_bottom=True)
        self.page.pubsub.send_all("new_chat_message")

    def _handle_manage_members(self, e):
        if not self.selected_chat_id:
            return
        participants = self.chat_repo.get_participants_in_chat(self.selected_chat_id)
        participant_dnis = {p["dni"] for p in participants}

        all_users = self.auth_repo.get_all_users()
        user_list_items = ft.Column(scroll=ft.ScrollMode.AUTO, height=300)

        def toggle_member(dni, is_adding):
            if is_adding:
                self.chat_repo.add_user_to_chat(self.selected_chat_id, dni)
            else:
                self.chat_repo.remove_user_from_chat(self.selected_chat_id, dni)
            self.page.pubsub.send_all("new_chat_message")

        for uname, udata in all_users.items():
            if udata["dni"] == self.user_dni:
                continue
            is_in = udata["dni"] in participant_dnis
            user_list_items.controls.append(
                ft.Checkbox(
                    label=f"{udata['full_name'] or uname} (@{uname})",
                    value=is_in,
                    on_change=lambda e, udni=udata["dni"]: toggle_member(
                        udni, e.control.value
                    ),
                )
            )

        dialog = ft.AlertDialog(
            title=ft.Text("Gestionar miembros del grupo"),
            content=user_list_items,
            actions=[
                ft.TextButton("Cerrar", on_click=lambda e: self.page.close(dialog))
            ],
        )
        self.page.open(dialog)

    def _handle_edit_chat_name(self, e):
        if not self.selected_chat_id:
            return
        name_input = ft.TextField(
            label="Nuevo nombre", value=self.chat_header_text.value
        )

        def save_name(e):
            if name_input.value.strip():
                self.chat_repo.update_chat_name(self.selected_chat_id, name_input.value)
                self.chat_header_text.value = name_input.value
                self.page.close(dialog)
                self._refresh_chats()

        dialog = ft.AlertDialog(
            title=ft.Text("Editar nombre del chat"),
            content=name_input,
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self.page.close(dialog)),
                ft.ElevatedButton("Guardar", on_click=save_name),
            ],
        )
        self.page.open(dialog)

    def _handle_leave_chat(self, e):
        if not self.selected_chat_id:
            return

        def confirm_leave(e):
            self.chat_repo.remove_user_from_chat(self.selected_chat_id, self.user_dni)
            self.selected_chat_id = None
            self.chat_header_text.value = "Selecciona un chat"
            self.btn_edit_name.visible = False
            self.btn_manage_members.visible = False
            self.btn_leave_chat.visible = False
            self.btn_delete_chat.visible = False
            self.messages_column.controls.clear()
            self.page.close(dialog)
            self._refresh_chats()
            self.page.pubsub.send_all("new_chat_message")

        dialog = ft.AlertDialog(
            title=ft.Text("Salirse del grupo"),
            content=ft.Text(
                "¿Quieres salirte del grupo? El chat seguirá existiendo para los demás miembros."
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self.page.close(dialog)),
                ft.ElevatedButton(
                    "Salirse",
                    bgcolor=ft.Colors.ORANGE_700,
                    color="white",
                    on_click=confirm_leave,
                ),
            ],
        )
        self.page.open(dialog)

    def _handle_delete_chat(self, e):
        if not self.selected_chat_id:
            return

        def confirm_delete(e):
            self.chat_repo.delete_chat(self.selected_chat_id)
            self.selected_chat_id = None
            self.chat_header_text.value = "Selecciona un chat"
            self.btn_edit_name.visible = False
            self.btn_manage_members.visible = False
            self.btn_leave_chat.visible = False
            self.btn_delete_chat.visible = False
            self.messages_column.controls.clear()
            self.page.close(dialog)
            self._refresh_chats()
            self.page.pubsub.send_all("new_chat_message")

        dialog = ft.AlertDialog(
            title=ft.Text("Borrar chat"),
            content=ft.Text(
                "¿Estás seguro de que quieres borrar este chat y todos sus mensajes?"
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self.page.close(dialog)),
                ft.ElevatedButton("Borrar", color="red", on_click=confirm_delete),
            ],
        )
        self.page.open(dialog)

    def _build_ui(self):
        return ft.Row(
            expand=True,
            spacing=20,
            controls=[
                ft.Container(
                    width=300,
                    bgcolor="white",
                    border_radius=12,
                    padding=15,
                    content=ft.Column(
                        [
                            ft.Text(
                                "Mensajes",
                                size=20,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.BLACK,
                            ),
                            ft.Divider(),
                            self.chat_list_column,
                            ft.ElevatedButton(
                                "Nuevo Chat / Grupo",
                                icon=ft.Icons.ADD,
                                on_click=self._show_new_chat_dialog,
                            ),
                        ]
                    ),
                ),
                ft.Container(
                    expand=True,
                    bgcolor=AppColors.GLASS_WHITE,
                    border_radius=12,
                    padding=20,
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Column(
                                        [self.chat_header_text, self.search_input],
                                        spacing=5,
                                    ),
                                    self.chat_actions,
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            ft.Divider(),
                            ft.Container(
                                expand=True,
                                content=ft.Stack(
                                    [
                                        ft.Container(
                                            content=self.messages_column,
                                            padding=ft.padding.only(bottom=10),
                                            expand=True,
                                        ),
                                    ],
                                    expand=True,
                                ),
                            ),
                            ft.Row(
                                [
                                    ft.IconButton(
                                        ft.Icons.BAR_CHART,
                                        tooltip="Compartir estado del parque",
                                        on_click=self._handle_share_status,
                                    ),
                                    self.message_input,
                                    ft.IconButton(
                                        icon=ft.Icons.SEND_ROUNDED,
                                        icon_color=AppColors.ACCENT,
                                        on_click=self._handle_send_click,
                                    ),
                                ]
                            ),
                        ]
                    ),
                ),
            ],
        )

    def _show_new_chat_dialog(self, e):
        users = self.chat_repo.get_all_users_for_chat_start(self.user_dni)
        selected_users = {self.user_dni}
        user_list = ft.Column(scroll=ft.ScrollMode.AUTO, height=300)
        chat_name_input = ft.TextField(
            label="Nombre del grupo (opcional)", hint_text="Solo para grupos"
        )

        def toggle_user(dni, checkbox):
            if checkbox.value:
                selected_users.add(dni)
            elif dni in selected_users:
                selected_users.remove(dni)

        for user in users:
            cb = ft.Checkbox(
                label=f"{user['full_name'] or user['username']} (@{user['username']})",
                on_change=lambda e, udni=user["dni"]: toggle_user(udni, e.control),
            )
            user_list.controls.append(cb)

        def create_group(e):
            if len(selected_users) < 2:
                return
            name = chat_name_input.value.strip() or (
                f"Grupo de {len(selected_users)} personas"
                if len(selected_users) > 2
                else "Chat"
            )
            chat_id = self.chat_repo.create_chat(name, list(selected_users))
            self.page.close(dialog)
            self._select_chat(chat_id, name, len(selected_users) > 2)
            self._refresh_chats()

        dialog = ft.AlertDialog(
            title=ft.Text("Crear nuevo chat o grupo"),
            content=ft.Column(
                [chat_name_input, ft.Text("Selecciona participantes:"), user_list],
                tight=True,
                width=400,
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self.page.close(dialog)),
                ft.ElevatedButton("Crear", on_click=create_group),
            ],
        )
        self.page.open(dialog)
