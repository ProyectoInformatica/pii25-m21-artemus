import flet as ft
from ArtemusPark.config.Colors import AppColors


class AdminPage(ft.Container):
    def __init__(self, user_role="admin"):
        super().__init__()
        self.expand = True
        self.padding = 20
        self.bgcolor = AppColors.BG_MAIN

        # Si no es admin, mostramos acceso denegado
        if user_role != "admin":
            self.content = ft.Center(ft.Text("Acceso Restringido", size=30, color=ft.Colors.BLACK))
            return

        self.content = ft.ListView(
            spacing=20,
            controls=[
                # Título Principal en Negro
                ft.Text("Configuración del Sistema", size=24, weight="bold", color=ft.Colors.BLACK),

                # --- SECCIÓN PERFIL ---
                self._build_section_container(
                    "Perfil de Administrador",
                    ft.Row([
                        # CORRECCIÓN DEL ERROR AQUÍ: Usamos foreground_image_src
                        ft.CircleAvatar(
                            foreground_image_src="https://ui-avatars.com/api/?name=Admin+User&background=0D8ABC&color=fff",
                            radius=30
                        ),
                        ft.Column([
                            ft.Text("Super Admin", weight="bold", size=16, color=ft.Colors.BLACK),
                            ft.Text("admin@artemus.park", color=ft.Colors.GREY_700, size=12)
                            # Gris oscuro para diferenciar
                        ])
                    ])
                ),

                # --- SECCIÓN GENERAL ---
                self._build_section_container(
                    "Preferencias Generales",
                    ft.Column([
                        self._build_switch("Modo Simulación", "Activar generación de datos aleatorios", True),
                        ft.Divider(),
                        self._build_switch("Notificaciones Push", "Recibir alertas en tiempo real", True),
                        ft.Divider(),
                        self._build_switch("Modo Mantenimiento", "Desactivar acceso a usuarios estándar", False),
                    ])
                ),

                # --- SECCIÓN USUARIOS ---
                self._build_section_container(
                    "Usuarios Activos",
                    ft.Column([
                        self._build_user_tile("Juan Pérez", "Operador", True),
                        self._build_user_tile("Ana García", "Seguridad", True),
                        self._build_user_tile("Carlos Ruiz", "Mantenimiento", False),
                    ])
                )
            ]
        )

    def _build_section_container(self, title, content_control):
        return ft.Container(
            bgcolor=ft.Colors.WHITE,
            padding=20,
            border_radius=12,
            border=ft.border.all(1, ft.Colors.GREY_200),
            content=ft.Column([
                # Títulos de sección en negro
                ft.Text(title, weight="bold", size=16, color=ft.Colors.BLACK),
                ft.Divider(height=20, color="transparent"),
                content_control
            ])
        )

    def _build_switch(self, label, sublabel, value):
        return ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Column(spacing=0, controls=[
                    # Etiqueta del switch en negro
                    ft.Text(label, weight="w500", color=ft.Colors.BLACK),
                    ft.Text(sublabel, size=12, color=ft.Colors.GREY_700)
                ]),
                ft.Switch(value=value, active_color=ft.Colors.BLUE)
            ]
        )

    def _build_user_tile(self, name, role, is_active):
        return ft.ListTile(
            leading=ft.Icon(ft.Icons.PERSON, color=ft.Colors.GREY_700),
            # Nombre del usuario en negro
            title=ft.Text(name, color=ft.Colors.BLACK, weight="bold"),
            subtitle=ft.Text(role, color=ft.Colors.GREY_700),
            trailing=ft.Icon(
                ft.Icons.CHECK_CIRCLE if is_active else ft.Icons.CANCEL,
                color=ft.Colors.GREEN if is_active else ft.Colors.RED
            )
        )