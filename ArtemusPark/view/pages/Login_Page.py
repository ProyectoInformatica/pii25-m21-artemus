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
        self.is_registering = False

        self.tf_username = ft.TextField(
            label="Usuario",
            width=240,
            bgcolor=AppColors.BG_CARD,
            border_radius=8,
            border_color=AppColors.TEXT_LIGHT_GREY,
            text_style=ft.TextStyle(color=AppColors.BG_DARK, size=14),
            height=45,
            content_padding=10,
            on_change=self._reset_error_state,
            on_submit=self._handle_submit,
        )

        self.tf_password = ft.TextField(
            label="Contraseña",
            width=240,
            password=True,
            can_reveal_password=True,
            bgcolor=AppColors.BG_CARD,
            border_radius=8,
            border_color=AppColors.TEXT_LIGHT_GREY,
            text_style=ft.TextStyle(color=AppColors.BG_DARK, size=14),
            height=45,
            content_padding=10,
            on_change=self._reset_error_state,
            on_submit=self._handle_submit,
        )

        common_tf_props = {
            "width": 240,
            "bgcolor": AppColors.BG_CARD,
            "border_radius": 8,
            "border_color": AppColors.TEXT_LIGHT_GREY,
            "text_style": ft.TextStyle(color=AppColors.BG_DARK, size=14),
            "height": 45,
            "content_padding": 10,
            "visible": False,
        }

        self.tf_full_name = ft.TextField(label="Nombre Completo", **common_tf_props)
        self.tf_dni = ft.TextField(label="DNI (8 nums + letra)", **common_tf_props)
        self.tf_phone = ft.TextField(
            label="Teléfono", keyboard_type=ft.KeyboardType.PHONE, **common_tf_props
        )
        self.tf_street = ft.TextField(label="Calle / Dirección", **common_tf_props)
        self.tf_city = ft.TextField(label="Ciudad", **common_tf_props)
        self.tf_zip = ft.TextField(label="C. Postal", **common_tf_props)

        self.btn_enter = ft.ElevatedButton(
            text="Entrar al Sistema",
            width=240,
            height=45,
            bgcolor=AppColors.BG_DARK,
            color=AppColors.TEXT_WHITE,
            on_click=self._handle_submit,
        )

        self.btn_switch = ft.TextButton(
            text="¿No tienes cuenta? Regístrate",
            on_click=self._toggle_mode,
        )

        self.title_text = ft.Text(
            "ARTEMUS PARK",
            size=22,
            weight="bold",
            color=AppColors.BG_DARK,
        )

        self.sub_title_text = ft.Text(
            "Identifícate para acceder", size=13, color=AppColors.TEXT_MUTED
        )

        self.login_controls = ft.Column(
            [self.tf_username, self.tf_password],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        )

        self.input_fields_container = ft.Container(
            content=self.login_controls,
            padding=ft.padding.symmetric(vertical=10),
            alignment=ft.alignment.center,
        )

        self.content = ft.Container(
            width=700,
            height=600,
            padding=30,
            bgcolor=AppColors.BG_CARD,
            border_radius=15,
            alignment=ft.alignment.center,
            shadow=ft.BoxShadow(blur_radius=15, color=AppColors.SHADOW),
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=5,
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    ft.Image(src="/img/artemusLogo2Negro.png", width=100, height=100),
                    self.title_text,
                    self.sub_title_text,
                    self.input_fields_container,
                    ft.Container(height=10),
                    self.btn_enter,
                    self.btn_switch,
                ],
            ),
        )

    def _reset_error_state(self, e):
        fields = [
            self.tf_username,
            self.tf_password,
            self.tf_full_name,
            self.tf_dni,
            self.tf_phone,
            self.tf_street,
            self.tf_city,
            self.tf_zip,
        ]
        for f in fields:
            f.border_color = AppColors.TEXT_LIGHT_GREY
            if f.page:
                f.update()
        self.update()

    def _toggle_mode(self, e):
        self.is_registering = not self.is_registering

        tfs = [
            self.tf_username,
            self.tf_password,
            self.tf_full_name,
            self.tf_dni,
            self.tf_phone,
            self.tf_street,
            self.tf_city,
            self.tf_zip,
        ]
        for tf in tfs:
            tf.value = ""
        self._reset_error_state(None)

        if self.is_registering:
            self.title_text.value = "REGISTRO"
            self.sub_title_text.value = "Crea tu cuenta de usuario"
            self.btn_enter.text = "Registrarse"
            self.btn_switch.text = "¿Ya tienes cuenta? Inicia sesión"

            for tf in [
                self.tf_full_name,
                self.tf_dni,
                self.tf_phone,
                self.tf_street,
                self.tf_city,
                self.tf_zip,
            ]:
                tf.visible = True

            self.input_fields_container.content = ft.Row(
                [
                    ft.Column(
                        [
                            self.tf_username,
                            self.tf_password,
                            self.tf_full_name,
                            self.tf_dni,
                        ],
                        spacing=10,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Column(
                        [
                            self.tf_phone,
                            self.tf_street,
                            self.tf_city,
                            self.tf_zip,
                        ],
                        spacing=10,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=20,
            )

        else:
            self.title_text.value = "ARTEMUS PARK"
            self.sub_title_text.value = "Identifícate para acceder"
            self.btn_enter.text = "Entrar al Sistema"
            self.btn_switch.text = "¿No tienes cuenta? Regístrate"

            for tf in [
                self.tf_full_name,
                self.tf_dni,
                self.tf_phone,
                self.tf_street,
                self.tf_city,
                self.tf_zip,
            ]:
                tf.visible = False

            self.login_controls.controls = [self.tf_username, self.tf_password]
            self.input_fields_container.content = self.login_controls

        self.input_fields_container.update()
        self.content.update()
        self.update()

    def _handle_submit(self, e):
        """Maneja el envío del formulario con los campos desglosados."""
        username = self.tf_username.value
        password = self.tf_password.value

        if not username or not password:
            self._show_error("Por favor, completa todos los campos")
            return

        if self.is_registering:
            full_name = self.tf_full_name.value
            dni = self.tf_dni.value
            phone = self.tf_phone.value
            street = self.tf_street.value
            city = self.tf_city.value
            zip_code = self.tf_zip.value

            # Validaciones de los nuevos campos
            if not all([full_name, dni, phone, street, city, zip_code]):
                self._show_error("Todos los campos son obligatorios")
                return

            if not self._is_valid_dni(dni):
                self._show_error("DNI inválido", [self.tf_dni])
                return

            if not phone.isdigit() or len(phone) != 9:
                self._show_error("Teléfono inválido (9 dígitos)", [self.tf_phone])
                return

            try:
                self.auth_repo.add_user(
                    username,
                    password,
                    "user",
                    full_name=full_name,
                    dni=dni,
                    phone=phone,
                    address_street=street,
                    address_city=city,
                    address_zip=zip_code,
                )
                self._show_success("Registro exitoso. Ya puedes entrar.")
                self._toggle_mode(None)
            except Exception as ex:
                self._show_error(f"Error al registrar: {str(ex)}")
        else:
            role = self.auth_repo.authenticate(username, password)
            if role:
                self.on_login_success(username, role, password)
            else:
                self._show_error("Credenciales incorrectas")

    def _show_error(self, message, fields_to_highlight=None):
        """Muestra un mensaje de error visual y resalta campos."""
        if fields_to_highlight is None:
            fields_to_highlight = [self.tf_username, self.tf_password]
            if self.is_registering:
                fields_to_highlight.extend(
                    [
                        self.tf_full_name,
                        self.tf_dni,
                        self.tf_phone,
                        self.tf_street,
                        self.tf_city,
                        self.tf_zip,
                    ]
                )
        else:
            self._reset_error_state(None)

        for field in fields_to_highlight:
            field.border_color = ft.Colors.RED

        self.input_fields_container.update()

        if self.page:
            self.page.open(
                ft.SnackBar(
                    content=ft.Text(f"⚠️ {message }", color="white"),
                    bgcolor=ft.Colors.RED_700,
                )
            )

    def _show_success(self, message):
        """Muestra un mensaje de éxito visual."""
        if self.page:
            self.page.open(
                ft.SnackBar(
                    content=ft.Text(f"✅ {message }", color="white"),
                    bgcolor=ft.Colors.GREEN_700,
                )
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
