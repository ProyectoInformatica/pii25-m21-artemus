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
            width=280,
            bgcolor=AppColors.BG_CARD,
            border_radius=8,
            border_color=AppColors.TEXT_LIGHT_GREY,
            text_style=ft.TextStyle(
                color=AppColors.BG_DARK, size=16, weight=ft.FontWeight.W_500
            ),
            cursor_color=AppColors.BG_DARK,
            on_change=self._reset_error_state,
            on_submit=self._handle_submit,
            height=40,
            content_padding=10
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
            on_submit=self._handle_submit,
            height=40,
            content_padding=10
        )

        common_tf_props = {
            "width": 280,
            "bgcolor": AppColors.BG_CARD,
            "border_radius": 8,
            "border_color": AppColors.TEXT_LIGHT_GREY,
            "text_style": ft.TextStyle(
                color=AppColors.BG_DARK, size=16, weight=ft.FontWeight.W_500
            ),
            "cursor_color": AppColors.BG_DARK,
            "height": 40,
            "content_padding": 10,
            "visible": False
        }
        
        self.tf_full_name = ft.TextField(
            label="Nombre Completo", 
            **common_tf_props
        )
        self.tf_dni = ft.TextField(
            label="DNI (8 nums + letra)", 
            **common_tf_props
        )
        self.tf_phone = ft.TextField(
            label="Teléfono (9 dígitos)", 
            keyboard_type=ft.KeyboardType.PHONE,
            **common_tf_props
        )
        self.tf_address = ft.TextField(
            label="Dirección", 
            **common_tf_props
        )

        self.btn_enter = ft.ElevatedButton(
            text="Entrar al Sistema",
            width=280,
            height=45,
            bgcolor=AppColors.BG_DARK,
            color=AppColors.TEXT_WHITE,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
            on_click=self._handle_submit,
        )

        self.btn_switch = ft.TextButton(
            text="¿No tienes cuenta? Regístrate",
            on_click=self._toggle_mode,
            style=ft.ButtonStyle(color=AppColors.TEXT_MUTED),
        )

        self.title_text = ft.Text(
            "ARTEMUS PARK",
            size=24,
            weight=ft.FontWeight.BOLD,
            color=AppColors.BG_DARK,
            text_align=ft.TextAlign.CENTER,
            style=ft.TextStyle(font_family="RobotoCondensed", letter_spacing=1.5),
        )

        self.sub_title_text = ft.Text(
            "Identifícate para acceder", size=14, color=AppColors.TEXT_MUTED
        )

        self.login_controls = ft.Column(
            [
                self.tf_username,
                self.tf_password,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        )

        self.input_fields_container = ft.Container(
            alignment=ft.alignment.center,
            height=155,
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            content=ft.AnimatedSwitcher(
                self.login_controls,
                transition=ft.AnimatedSwitcherTransition.FADE,
                duration=300,
                reverse_duration=100,
                switch_in_curve=ft.AnimationCurve.EASE_IN,
                switch_out_curve=ft.AnimationCurve.EASE_OUT,
            ),
        )
        self.animated_switcher = self.input_fields_container.content

        self.input_fields_block = ft.Container(
            expand=True,
            alignment=ft.alignment.center,
            content=self.input_fields_container,
        )

        self.content = ft.Container(
            width=650,
            height=650,
            padding=40,
            bgcolor=AppColors.BG_CARD,
            border_radius=15,
            shadow=ft.BoxShadow(blur_radius=15, color=AppColors.SHADOW),
            content=ft.Column(
                tight=False,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=15,
                controls=[
                    ft.Image(
                        src="/img/artemusLogo2Negro.png",
                        width=200,
                        height=200,
                        fit=ft.ImageFit.CONTAIN,
                    ),
                    self.title_text,
                    self.sub_title_text,
                    self.input_fields_block,
                    self.btn_enter,
                    self.btn_switch,
                ],
            ),
        )


    def _reset_error_state(self, e):
        """Limpia los estados de error en los campos de texto."""
        fields_to_check = [
            self.tf_username,
            self.tf_password,
            self.tf_full_name,
            self.tf_dni,
            self.tf_phone,
            self.tf_address,
        ]
        for field in fields_to_check:
            if field.border_color == ft.Colors.RED:
                field.border_color = AppColors.TEXT_LIGHT_GREY
                if field.page:
                    field.update()

    def _toggle_mode(self, e):
        """Alterna entre modo Login y Registro."""
        self.is_registering = not self.is_registering

        self.tf_username.value = ""
        self.tf_password.value = ""
        self.tf_full_name.value = ""
        self.tf_dni.value = ""
        self.tf_phone.value = ""
        self.tf_address.value = ""
        self._reset_error_state(None)

        if self.is_registering:
            self.title_text.value = "REGISTRO"
            self.sub_title_text.value = "Crea tu cuenta de usuario"
            self.btn_enter.text = "Registrarse"
            self.btn_switch.text = "¿Ya tienes cuenta? Inicia sesión"
            
            self.tf_full_name.visible = True
            self.tf_dni.visible = True
            self.tf_phone.visible = True
            self.tf_address.visible = True

            self.animated_switcher.content = ft.Row(
                [
                    ft.Container(
                        padding=ft.padding.only(top=10),
                        content=ft.Row(
                            [
                                ft.Column(
                                    [
                                        self.tf_username,
                                        self.tf_password,
                                        self.tf_full_name,
                                    ],
                                    spacing=10,
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                ),
                                ft.Column(
                                    [
                                        self.tf_dni,
                                        self.tf_phone,
                                        self.tf_address,
                                    ],
                                    spacing=10,
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=10,
                        ),
                    )
                ],
            )
            
        else:
            self.title_text.value = "ARTEMUS PARK"
            self.sub_title_text.value = "Identifícate para acceder"
            self.btn_enter.text = "Entrar al Sistema"
            self.btn_switch.text = "¿No tienes cuenta? Regístrate"

            self.tf_full_name.visible = False
            self.tf_dni.visible = False
            self.tf_phone.visible = False
            self.tf_address.visible = False

            self.animated_switcher.content = self.login_controls
            
        self.animated_switcher.update()
        self.content.update()
        self.update()
    def _handle_submit(self, e):
        """Maneja el envío del formulario (login o registro)."""
        username = self.tf_username.value
        password = self.tf_password.value

        if not username or not password:
            self._show_error("Por favor, completa todos los campos")
            return

        if self.is_registering:
            full_name = self.tf_full_name.value
            dni = self.tf_dni.value
            phone = self.tf_phone.value
            address = self.tf_address.value
            
            if not full_name.strip():
                self._show_error(
                    "El nombre completo no puede estar vacío.",
                    fields_to_highlight=[self.tf_full_name],
                )
                return
            if not dni.strip():
                self._show_error(
                    "El DNI no puede estar vacío.",
                    fields_to_highlight=[self.tf_dni],
                )
                return
            if not self._is_valid_dni(dni):
                self._show_error(
                    "DNI inválido. Debe tener 8 números y letra correcta.",
                    fields_to_highlight=[self.tf_dni],
                )
                return
            if not phone.strip():
                self._show_error(
                    "El teléfono no puede estar vacío.",
                    fields_to_highlight=[self.tf_phone],
                )
                return
            if not phone.strip().isdigit() or len(phone.strip()) != 9:
                self._show_error(
                    "Teléfono inválido. Debe contener 9 dígitos numéricos.",
                    fields_to_highlight=[self.tf_phone],
                )
                return
            if not address.strip():
                self._show_error(
                    "La dirección no puede estar vacía.",
                    fields_to_highlight=[self.tf_address],
                )
                return

            try:
                self.auth_repo.add_user(
                    username, password, "user", 
                    full_name=full_name, dni=dni, phone=phone, address=address
                )
                self._show_success("Registro exitoso. Por favor inicia sesión.")
                self._toggle_mode(None)
            except ValueError as ex:
                self._show_error(str(ex))
        else:
            role = self.auth_repo.authenticate(username, password)

            if role:
                print(f"Login: Acceso concedido a {username} ({role})")
                self.on_login_success(username, role)
            else:
                self._show_error("Usuario o contraseña incorrectos")

    def _show_error(self, message, fields_to_highlight=None):
        """Muestra un mensaje de error visual y resalta campos."""
        if fields_to_highlight is None:
            fields_to_highlight = [self.tf_username, self.tf_password]
            if self.is_registering:
                fields_to_highlight.extend([
                    self.tf_full_name,
                    self.tf_dni,
                    self.tf_phone,
                    self.tf_address,
                ])
        else:
            self._reset_error_state(None)
            
        for field in fields_to_highlight:
            field.border_color = ft.Colors.RED
        
        self.input_fields_container.update()
        
        if self.page:
            self.page.open(
                ft.SnackBar(
                    content=ft.Text(f"⚠️ {message}", color="white"),
                    bgcolor=ft.Colors.RED_700,
                )
            )

    def _show_success(self, message):
        """Muestra un mensaje de éxito visual."""
        if self.page:
            self.page.open(
                ft.SnackBar(
                    content=ft.Text(f"✅ {message}", color="white"),
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
