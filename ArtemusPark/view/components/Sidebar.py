import flet as ft
import base64
from ArtemusPark.config.Colors import AppColors
from ArtemusPark.repository.Requests_Repository import RequestsRepository
from ArtemusPark.repository.Auth_Repository import AuthRepository
from ArtemusPark.service.Dashboard_Service import DashboardService


class Sidebar(ft.Container):

    def __init__(
        self, on_nav_change, on_logout, user_role="user", username="", permissions=None
    ):
        super().__init__()
        self.on_nav_change = on_nav_change
        self.on_logout = on_logout
        self.user_role = user_role
        self.username = username
        self.permissions = permissions or []
        self.auth_repo = AuthRepository()
        self.badge_controls = {}
        self.has_pending_requests = False
        if "MANAGE_REQUESTS" in self.permissions or self.user_role == "admin":
            self.has_pending_requests = self._check_pending_requests()

        self.width = 260
        self.bgcolor = AppColors.BG_DARK
        self.padding = ft.padding.symmetric(vertical=24, horizontal=20)

        # Avatar placeholder/default
        self.user_avatar = ft.CircleAvatar(
            radius=18,
            content=ft.Text(self.username[0].upper() if self.username else "?", size=14),
            bgcolor=ft.Colors.BLUE_GREY_700,
            color=ft.Colors.WHITE,
        )
        self._load_user_avatar()

        self.content_column = self._build_content()
        self.content = self.content_column

    def did_mount(self):
        self.page.pubsub.subscribe(self._on_message)
        if DashboardService().is_catastrophe_mode():
            self.bgcolor = ft.Colors.RED_900
            self.update()

    def _load_user_avatar(self):
        """Loads the user's profile picture from the repository."""
        try:
            profile_pic = self.auth_repo.get_user_profile_picture(self.username)
            if profile_pic:
                b64_str = base64.b64encode(profile_pic).decode("utf-8")
                # Create a fresh Image control to avoid caching issues
                self.user_avatar.content = ft.Image(
                    src_base64=b64_str,
                    border_radius=18,
                    fit=ft.ImageFit.COVER,
                    gapless_playback=True # Helps with smooth updates
                )
                self.user_avatar.bgcolor = ft.Colors.TRANSPARENT
            else:
                self.user_avatar.content = ft.Text(self.username[0].upper() if self.username else "?", size=14)
                self.user_avatar.bgcolor = ft.Colors.BLUE_GREY_700
        except Exception as e:
            print(f"Error loading sidebar avatar for {self.username}: {e}")

    def _on_message(self, message):
        if isinstance(message, dict):
            topic = message.get("topic")
            if topic == "requests_updated":
                self._refresh_pending_requests()
            elif topic == "profile_updated" and message.get("username") == self.username:
                self._load_user_avatar()
                self.user_avatar.update()
        elif message == "catastrophe_mode":
            self.bgcolor = ft.Colors.RED_900
            self.update()
        elif message == "normal_mode":
            self.bgcolor = AppColors.BG_DARK
            self.update()

    def _build_content(self):
        """Construye el contenido vertical de la barra lateral."""
        self.nav_buttons = {}
        controls_list = [
            ft.Text(
                "ARTEMUS PARK",
                size=22,
                weight=ft.FontWeight.BOLD,
                color="white",
                style=ft.TextStyle(font_family="RobotoCondensed", letter_spacing=1.5),
            ),
            ft.Divider(height=30, color="transparent"),
            self._make_button("Dashboard", "📊", "dashboard", active=True),
        ]

        if "VIEW_HISTORY" in self.permissions or self.user_role == "admin":
            controls_list.append(self._make_button("Historial", "🧾", "history"))

        if "VIEW_REQUESTS" in self.permissions or self.user_role == "admin":
            controls_list.append(
                self._make_button(
                    "Solicitudes",
                    "📩",
                    "requests",
                    show_badge=(
                        "MANAGE_REQUESTS" in self.permissions
                        or self.user_role == "admin"
                    )
                    and self.has_pending_requests,
                )
            )

        if "VIEW_MAINTENANCE" in self.permissions or self.user_role == "admin":
            controls_list.append(self._make_button("Mantenimiento", "🛠", "maintenance"))

        if "ACCESS_ADMIN_PANEL" in self.permissions or self.user_role == "admin":
            controls_list.append(self._make_button("Administración", "⚙️", "admin"))

        controls_list.append(ft.Container(expand=True))

        controls_list.append(
            ft.Container(
                padding=ft.padding.only(top=10),
                border=ft.border.only(top=ft.border.BorderSide(1, "#374151")),
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Row(
                            spacing=10,
                            controls=[
                                self.user_avatar,
                                ft.Column(
                                    spacing=2,
                                    controls=[
                                        ft.Text(
                                            f"{self.username.upper()}",
                                            size=12,
                                            weight=ft.FontWeight.BOLD,
                                            color="white",
                                        ),
                                        ft.Text(
                                            self._get_role_display_name().upper(),
                                            size=10,
                                            color="#9ca3af",
                                        ),
                                    ],
                                ),
                            ]
                        ),
                        ft.IconButton(
                            icon=ft.Icons.LOGOUT_ROUNDED,
                            icon_color="#ef4444",
                            tooltip="Cerrar Sesión",
                            on_click=self._handle_logout,
                        ),
                    ],
                ),
            )
        )

        return ft.Column(controls=controls_list)

    def _handle_logout(self, e):
        if self.on_logout:
            import asyncio

            if asyncio.iscoroutinefunction(self.on_logout):
                self.page.run_task(self.on_logout)
            else:
                self.on_logout()

    def _get_role_display_name(self):
        """Mapea el rol interno a un nombre amigable en español."""
        mapping = {
            "admin": "Administrador",
            "maintenance": "Mantenimiento",
            "user": "Usuario",
        }
        return mapping.get(self.user_role, self.user_role)

    def _make_button(self, text, icon, key, active=False, show_badge=False):
        """Crea un botón de navegación personalizado."""
        bg_color = "#111827" if active else "transparent"
        text_color = "white" if active else "#9ca3af"

        row_controls = [
            ft.Text(icon, size=16),
            ft.Text(text, size=14, color=text_color),
        ]
        if key == "requests" and self.user_role == "admin":
            badge = ft.Container(
                width=8,
                height=8,
                bgcolor=ft.Colors.RED,
                border_radius=4,
                margin=ft.margin.only(left=6),
                visible=show_badge,
            )
            self.badge_controls[key] = badge
            row_controls.append(badge)

        button = ft.Container(
            data=key,
            padding=10,
            border_radius=10,
            bgcolor=bg_color,
            ink=True,
            on_click=self._handle_click,
            content=ft.Row(controls=row_controls),
        )
        self.nav_buttons[key] = button
        return button

    def set_active(self, key):
        self._apply_active_state(key)
        if self.page:
            self.update()

    def _handle_click(self, e):
        """Maneja el evento de clic en un botón de navegación."""
        clicked_key = e.control.data
        if e.control.bgcolor == "#111827":
            return
        self.on_nav_change(clicked_key)

        self._apply_active_state(clicked_key)
        if self.page:
            self.update()

    def _apply_active_state(self, clicked_key):
        for control in self.content_column.controls:
            if isinstance(control, ft.Container) and control.data is not None:
                if control.data == clicked_key:
                    control.bgcolor = "#111827"
                    control.content.controls[1].color = "white"
                else:
                    control.bgcolor = "transparent"
                    control.content.controls[1].color = "#9ca3af"

    def _check_pending_requests(self):
        repo = RequestsRepository()
        reqs = repo.get_all_requests()
        return any(r.get("status") == "PENDING" for r in reqs)

    def _refresh_pending_requests(self):
        self.has_pending_requests = self._check_pending_requests()
        badge = self.badge_controls.get("requests")
        if badge is not None:
            badge.visible = self.has_pending_requests
            if badge.page:
                try:
                    badge.update()
                except Exception:
                    pass
