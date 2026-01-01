import flet as ft
from ArtemusPark.config.Colors import AppColors
from ArtemusPark.repository.Auth_Repository import AuthRepository


class LoginPage(ft.Container):
    def __init__(self, on_login_success):
        super().__init__()
        self.on_login_success = on_login_success
        self.expand = True
        self.bgcolor = AppColors.BG_MAIN
        self.alignment = ft.alignment.center

        self.auth_repo = AuthRepository()

        self.tf_username = ft.TextField(
            label="Usuario",
            width=280,
            bgcolor=AppColors.BG_CARD,
            border_radius=8,
            border_color=AppColors.TEXT_LIGHT_GREY,
            text_style=ft.TextStyle(
                color=AppColors.BG_DARK, size=16, weight=ft.FontWeight.W_500
            ),
            cursor_color=AppColors.BG_DARK,
            on_change=self._reset_error_state,
            on_submit=self._handle_login,
        )

        self.tf_password = ft.TextField(
            label="Contraseña",
            width=280,
            password=True,
            can_reveal_password=True,
            bgcolor=AppColors.BG_CARD,
            border_radius=8,
            border_color=AppColors.TEXT_LIGHT_GREY,
            text_style=ft.TextStyle(
                color=AppColors.BG_DARK, size=16, weight=ft.FontWeight.W_500
            ),
            cursor_color=AppColors.BG_DARK,
            on_change=self._reset_error_state,
            on_submit=self._handle_login,
        )

        self.btn_enter = ft.ElevatedButton(
            text="Entrar al Sistema",
            width=280,
            height=45,
            bgcolor=AppColors.BG_DARK,
            color=AppColors.TEXT_WHITE,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
            on_click=self._handle_login,
        )

        self.content = ft.Container(
            width=350,
            padding=40,
            bgcolor=AppColors.BG_CARD,
            border_radius=15,
            shadow=ft.BoxShadow(blur_radius=15, color=AppColors.SHADOW),
            content=ft.Column(
                tight=True,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=15,
                controls=[
                    ft.Image(
                        src="/img/artemusLogo2Negro.png",
                        width=200,
                        height=200,
                        fit=ft.ImageFit.CONTAIN,
                    ),
                    ft.Text(
                        "ARTEMUS PARK",
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        color=AppColors.BG_DARK,
                        text_align=ft.TextAlign.CENTER,
                        style=ft.TextStyle(
                            font_family="RobotoCondensed", letter_spacing=1.5
                        ),
                    ),
                    ft.Text(
                        "Identifícate para acceder", size=14, color=AppColors.TEXT_MUTED
                    ),
                    self.tf_username,
                    self.tf_password,
                    ft.Container(height=10),  
                    self.btn_enter,
                ],
            ),
        )

    def _reset_error_state(self, e):
        """Limpia los estados de error en los campos de texto."""
        if self.tf_username.border_color == ft.Colors.RED:
            self.tf_username.border_color = AppColors.TEXT_LIGHT_GREY
            self.tf_username.update()
        if self.tf_password.border_color == ft.Colors.RED:
            self.tf_password.border_color = AppColors.TEXT_LIGHT_GREY
            self.tf_password.update()

    def _handle_login(self, e):
        """Valida credenciales y notifica éxito o error."""
        username = self.tf_username.value
        password = self.tf_password.value

        if not username or not password:
            self._show_error("Por favor, completa todos los campos")
            return

        role = self.auth_repo.authenticate(username, password)

        if role:
            print(f"Login: Acceso concedido a {username} ({role})")
            self.on_login_success(role)
        else:
            self._show_error("Usuario o contraseña incorrectos")

    def _show_error(self, message):
        """Muestra un mensaje de error visual."""
        self.tf_username.border_color = ft.Colors.RED
        self.tf_password.border_color = ft.Colors.RED
        self.tf_username.update()
        self.tf_password.update()

        self.page.open(
            ft.SnackBar(
                content=ft.Text(f"⚠️ {message}", color="white"),
                bgcolor=ft.Colors.RED_700,
            )
        )
