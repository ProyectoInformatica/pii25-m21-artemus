import flet as ft
from datetime import datetime
from ArtemusPark.config.Colors import AppColors
from ArtemusPark.repository.Chat_Repository import ChatRepository
from ArtemusPark.repository.Auth_Repository import AuthRepository

class ChatPage(ft.Container):
    def __init__(self, current_username, current_user_role):
        super().__init__()
        self.expand = True
        self.bgcolor = AppColors.BG_MAIN
        self.padding = 18
        
        self.username = current_username
        self.role = current_user_role
        self.chat_repo = ChatRepository()
        self.auth_repo = AuthRepository()
        
        user_data = self.auth_repo.get_user_by_username(self.username)
        self.user_dni = user_data.get("dni", "")
        
        self.selected_chat_id = None
        self.chats = []
        self.messages = []
        
        # UI Components
        self.chat_list_column = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)
        self.messages_column = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, spacing=10)
        self.message_input = ft.TextField(
            hint_text="Escribe un mensaje...",
            expand=True,
            border_radius=20,
            bgcolor="white",
            color=ft.Colors.BLACK,
            on_submit=self._handle_send_click
        )
        
        self.chat_header_text = ft.Text("Selecciona un chat", weight=ft.FontWeight.BOLD, size=18, color=ft.Colors.BLACK)
        
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
        if not self.page: return
        self.chats = self.chat_repo.get_chats_for_user(self.user_dni)
        self.chat_list_column.controls.clear()
        
        for chat in self.chats:
            is_selected = chat["id_chat"] == self.selected_chat_id
            unread_count = chat.get("unread_count", 0)
            
            self.chat_list_column.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.CHAT_BUBBLE_OUTLINE, color=AppColors.ACCENT if not is_selected else "white"),
                        ft.Text(chat["name"], color=AppColors.TEXT_MAIN if not is_selected else "white", weight=ft.FontWeight.BOLD if is_selected else None, expand=True),
                        # Unread Badge inside Chat list
                        ft.Container(
                            content=ft.Text(str(unread_count), color="white", size=10, weight="bold"),
                            bgcolor="red",
                            width=20, height=20,
                            border_radius=10,
                            alignment=ft.alignment.center,
                            visible=unread_count > 0 and not is_selected
                        )
                    ]),
                    padding=10,
                    border_radius=10,
                    bgcolor=AppColors.ACCENT if is_selected else "white",
                    on_click=lambda e, cid=chat["id_chat"], cname=chat["name"]: self._select_chat(cid, cname),
                    ink=True
                )
            )
        try:
            self.update()
        except Exception:
            pass

    def _select_chat(self, chat_id, chat_name):
        self.selected_chat_id = chat_id
        self.chat_header_text.value = chat_name
        self._load_messages(chat_id)
        self._refresh_chats()
        # Also notify sidebar that we read messages
        self.page.pubsub.send_all("new_chat_message")

    def _load_messages(self, chat_id):
        if not self.page: return
        self.messages = self.chat_repo.get_messages_in_chat(chat_id, self.user_dni)
        # Marking as read is done inside get_messages_in_chat in the repo
        self.messages_column.controls.clear()
        
        for msg in self.messages:
            is_me = msg["username"] == self.username
            alignment = ft.MainAxisAlignment.END if is_me else ft.MainAxisAlignment.START
            bg_color = AppColors.ACCENT_SOFT if is_me else "white"
            text_color = AppColors.TEXT_MAIN
            
            self.messages_column.controls.append(
                ft.Row(
                    [
                        ft.Container(
                            content=ft.Column([
                                ft.Text(msg["username"] if not is_me else "Tú", size=10, weight=ft.FontWeight.BOLD, color=AppColors.ACCENT),
                                ft.Text(msg["content"], color=text_color),
                                ft.Text(msg["sent_at"].strftime("%H:%M"), size=9, color=AppColors.TEXT_MUTED, text_align=ft.TextAlign.RIGHT)
                            ], spacing=2, tight=True),
                            padding=10,
                            border_radius=ft.border_radius.only(
                                top_left=15, top_right=15, 
                                bottom_left=0 if is_me else 15, 
                                bottom_right=15 if is_me else 0
                            ),
                            bgcolor=bg_color,
                            width=300,
                        )
                    ],
                    alignment=alignment
                )
            )
        try:
            self.update()
        except Exception:
            pass
        # Scroll to bottom
        # self.messages_column.scroll_to(offset=-1, duration=100)

    def _handle_send_click(self, e):
        if not self.selected_chat_id or not self.message_input.value.strip():
            return
            
        self.chat_repo.send_message(self.selected_chat_id, self.user_dni, self.message_input.value)
        self.message_input.value = ""
        self.page.pubsub.send_all("new_chat_message")
        self.message_input.focus()
        try:
            self.update()
        except Exception:
            pass

    def _build_ui(self):
        return ft.Row(
            expand=True,
            spacing=20,
            controls=[
                # Sidebar de chats
                ft.Container(
                    width=300,
                    bgcolor="white",
                    border_radius=12,
                    padding=15,
                    content=ft.Column([
                        ft.Text("Mensajes", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
                        ft.Divider(),
                        self.chat_list_column,
                        ft.ElevatedButton("Nuevo Chat", icon=ft.Icons.ADD, on_click=self._show_new_chat_dialog)
                    ])
                ),
                # Area de chat
                ft.Container(
                    expand=True,
                    bgcolor=AppColors.GLASS_WHITE,
                    border_radius=12,
                    padding=20,
                    content=ft.Column([
                        ft.Row([
                            self.chat_header_text,
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Divider(),
                        ft.Container(
                            expand=True,
                            content=self.messages_column,
                            padding=ft.padding.only(bottom=10)
                        ),
                        ft.Row([
                            self.message_input,
                            ft.IconButton(
                                icon=ft.Icons.SEND_ROUNDED,
                                icon_color=AppColors.ACCENT,
                                on_click=self._handle_send_click
                            )
                        ])
                    ])
                )
            ]
        )

    def _show_new_chat_dialog(self, e):
        users = self.chat_repo.get_all_users_for_chat_start(self.user_dni)
        
        user_list = ft.Column(scroll=ft.ScrollMode.AUTO, height=300)
        
        def start_chat(target_dni, target_name):
            chat_id = self.chat_repo.create_chat(f"Chat con {target_name}", [self.user_dni, target_dni])
            self.page.close(dialog)
            self.selected_chat_id = chat_id
            self._refresh_chats()
            self._select_chat(chat_id, f"Chat con {target_name}")

        for user in users:
            user_list.controls.append(
                ft.ListTile(
                    title=ft.Text(user["full_name"] or user["username"]),
                    subtitle=ft.Text(f"@{user['username']}"),
                    on_click=lambda e, udni=user["dni"], uname=user["username"]: start_chat(udni, uname)
                )
            )
            
        dialog = ft.AlertDialog(
            title=ft.Text("Iniciar nuevo chat"),
            content=user_list,
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self.page.close(dialog))
            ]
        )
        self.page.open(dialog)
