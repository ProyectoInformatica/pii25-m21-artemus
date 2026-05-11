import flet as ft
from ArtemusPark.config.Colors import AppColors
from ArtemusPark.repository.Chat_Repository import ChatRepository
from ArtemusPark.repository.Auth_Repository import AuthRepository
from ArtemusPark.service.Dashboard_Service import DashboardService


class ChatPage(ft.Container):
    def __init__(self, current_username, current_user_role, permissions=None):
        super().__init__()
        self.expand = True
        self.bgcolor = AppColors.BG_MAIN
        self.padding = 18

        self.username = current_username
        self.role = current_user_role
        self.permissions = permissions or []

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
        self.chat_list_column = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)
        self.messages_column = ft.Column(
            scroll=ft.ScrollMode.AUTO, expand=True, spacing=10
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
        self.btn_delete_chat = ft.IconButton(
            ft.Icons.DELETE_OUTLINE,
            tooltip="Borrar chat",
            icon_color="red",
            on_click=self._handle_delete_chat,
            visible=False,
        )

        self.chat_actions = ft.Row(
            [self.btn_edit_name, self.btn_manage_members, self.btn_delete_chat]
        )

        self.content = self._build_ui()

    def did_mount(self):
        self.page.pubsub.subscribe(self._on_message_received)
        self._refresh_chats()

    def _on_message_received(self, message):
        if message == "new_chat_message":
            if self.selected_chat_id:
                self._load_messages(self.selected_chat_id)
            self._refresh_chats()

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

        # PERMISSIONS SYSTEM
        can_manage_all = "MANAGE_CHATS" in self.permissions
        is_global = chat_id == 1

        if is_global:
            # En el Chat Global, solo si tiene permiso de gestionar chats
            self.btn_edit_name.visible = can_manage_all
            self.btn_manage_members.visible = can_manage_all
            self.btn_delete_chat.visible = can_manage_all
        else:
            # En otros chats:
            # Editar nombre y gestionar miembros solo si es grupo
            self.btn_edit_name.visible = is_group
            self.btn_manage_members.visible = is_group
            # Borrar chat: si es el creador o tiene permiso global (aquí simplificamos a si puede gestionar chats o es su chat)
            self.btn_delete_chat.visible = True

        self.search_input.value = ""
        self._load_messages(chat_id)
        self._refresh_chats()
        self.page.pubsub.send_all("new_chat_message")

    def _handle_search(self, e):
        query = self.search_input.value.lower()
        if not self.selected_chat_id:
            return
        self._display_messages(query)

    def _load_messages(self, chat_id):
        if not self.page:
            return
        self.messages = self.chat_repo.get_messages_in_chat(chat_id, self.user_dni)
        self._display_messages()

    def _display_messages(self, filter_query=""):
        self.messages_column.controls.clear()
        for msg in self.messages:
            if filter_query and filter_query not in msg["content"].lower():
                continue

            is_me = msg["username"] == self.username
            alignment = (
                ft.MainAxisAlignment.END if is_me else ft.MainAxisAlignment.START
            )

            is_alert = "⚠️ ALERTA" in msg["content"]
            bg_color = (
                ft.Colors.RED_100
                if is_alert
                else (AppColors.ACCENT_SOFT if is_me else "white")
            )

            if msg.get("sender_dni") == "12345678X":
                sender_name = "Bot-Artemus"
            else:
                sender_name = msg["full_name"] or msg["username"]
                if is_me:
                    sender_name = f"{sender_name} (Tú)"

            self.messages_column.controls.append(
                ft.Row(
                    [
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text(
                                        sender_name,
                                        size=10,
                                        weight=ft.FontWeight.BOLD,
                                        color=(
                                            ft.Colors.RED_700
                                            if is_alert
                                            else AppColors.ACCENT
                                        ),
                                    ),
                                    ft.Text(msg["content"], color=ft.Colors.BLACK),
                                    ft.Text(
                                        msg["sent_at"].strftime("%H:%M"),
                                        size=9,
                                        color=AppColors.TEXT_MUTED,
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
                                bottom_left=0 if is_me else 15,
                                bottom_right=15 if is_me else 0,
                            ),
                            bgcolor=bg_color,
                            border=(
                                ft.border.all(2, ft.Colors.RED_700)
                                if is_alert
                                else None
                            ),
                            width=320 if is_alert else 300,
                        )
                    ],
                    alignment=alignment,
                )
            )
        try:
            self.update()
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

        if text.lower().startswith("@bot-artemus"):
            self._process_bot_command(text)

        self.page.pubsub.send_all("new_chat_message")
        self.message_input.focus()
        try:
            self.update()
        except:
            pass

    def _process_bot_command(self, text):
        cmd = text.lower().replace("@bot-artemus", "").strip()
        if "estado" in cmd or "sensores" in cmd:
            data = self.dashboard_service.get_latest_sensor_data()
            response = (
                f"🤖 **Estado Actual del Parque**:\n"
                f"🌡️ Temp: {data['temperature']}°C\n"
                f"💧 Humedad: {data['humidity']}%\n"
                f"🌬️ Viento: {data['wind']} km/h\n"
                f"🌫️ Calidad Aire: {data['air_quality']} AQI\n"
                f"👥 Ocupación: {data['occupancy']} personas\n"
                f"💡 Luces: {'Encendidas' if data['light_is_on'] else 'Apagadas'}"
            )
            self.chat_repo.send_message(self.selected_chat_id, "12345678X", response)

    def _handle_share_status(self, e):
        if "SEND_MESSAGES" not in self.permissions:
            return
        if not self.selected_chat_id:
            return
        data = self.dashboard_service.get_latest_sensor_data()
        msg = (
            f"📍 **Reporte de Sensores compartido por {self.username}**:\n"
            f"• Temperatura: {data['temperature']}°C\n"
            f"• Viento: {data['wind']} km/h\n"
            f"• Ocupación: {data['occupancy']}"
        )
        self.chat_repo.send_message(self.selected_chat_id, self.user_dni, msg)
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

    def _handle_delete_chat(self, e):
        if not self.selected_chat_id:
            return

        def confirm_delete(e):
            self.chat_repo.delete_chat(self.selected_chat_id)
            self.selected_chat_id = None
            self.chat_header_text.value = "Selecciona un chat"
            self.btn_edit_name.visible = False
            self.btn_manage_members.visible = False
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
                                content=self.messages_column,
                                padding=ft.padding.only(bottom=10),
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
