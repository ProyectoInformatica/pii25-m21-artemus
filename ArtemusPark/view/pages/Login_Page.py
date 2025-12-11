import flet as ft
from ArtemusPark.config.Colors import AppColors


class LoginPage(ft.Container):
    def __init__(self, on_login_success):
        super().__init__()
        self.on_login_success = on_login_success
        self.expand = True
        self.bgcolor = AppColors.BG_MAIN
        self.alignment = ft.alignment.center

        self.dd_role = ft.Dropdown(
            label="Selecciona tu Rol",
            width=280,

            # --- SOLUCIÓN HÍBRIDA ---
            options=[
                ft.dropdown.Option(
                    key="admin",
                    text="Administrador",  # <--- Esto se muestra en la CAJA al seleccionar (evita que salga la key)
                    content=ft.Text("Administrador", color=AppColors.BG_DARK, weight=ft.FontWeight.W_500)
                    # <--- Esto se muestra en la LISTA (con tu color)
                ),
                ft.dropdown.Option(
                    key="maintenance",
                    text="Mantenimiento",
                    content=ft.Text("Mantenimiento", color=AppColors.BG_DARK, weight=ft.FontWeight.W_500)
                ),
                ft.dropdown.Option(
                    key="user",
                    text="Cliente",
                    content=ft.Text("Cliente", color=AppColors.BG_DARK, weight=ft.FontWeight.W_500)
                ),
            ],
            # ------------------------

            bgcolor=AppColors.BG_CARD,
            border_radius=8,
            border_color=AppColors.TEXT_LIGHT_GREY,

            # Este estilo controla el texto UNA VEZ SELECCIONADO en la caja principal
            text_style=ft.TextStyle(
                color=AppColors.BG_DARK,
                size=16,
                weight=ft.FontWeight.W_500
            ),

            hover_color=AppColors.TRANSPARENT,
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
                spacing=20,
                controls=[
                    # CORREGIDO: ft.Icons (Mayúscula) y SECURITY (Icono estándar)
                    ft.Icon(ft.Icons.SECURITY, size=50, color=AppColors.BG_DARK),
                    ft.Text(
                        "ARTEMUS PARK",
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        color=AppColors.BG_DARK,
                    ),
                    ft.Text(
                        "Identifícate para acceder", size=14, color=AppColors.TEXT_MUTED
                    ),
                    ft.Divider(height=10, color="transparent"),
                    self.dd_role,
                    self.btn_enter,
                ],
            ),
        )

    def _handle_login(self, e):
        role = self.dd_role.value
        if role:
            print(f"Login: Iniciando sesión como {role}")
            self.on_login_success(role)
