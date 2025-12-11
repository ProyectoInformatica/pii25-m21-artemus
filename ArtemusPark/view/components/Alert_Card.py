import flet as ft
from datetime import datetime
from config.Colors import AppColors


class AlertCard(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True  # IMPORTANTE: Esto hace que ocupe todo el ancho disponible
        self.height = 140  # Misma altura que la tarjeta de Aforo
        self.bgcolor = AppColors.BG_CARD
        self.border_radius = 12
        self.border = ft.border.all(1, ft.Colors.GREY_300)
        self.padding = 20
        # self.shadow = ft.BoxShadow(blur_radius=10, color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK))

        # --- Elementos internos ---
        self.title = ft.Text(
            "Alertas", size=14, weight=ft.FontWeight.W_500, color=AppColors.TEXT_MUTED
        )

        # Contenedor del mensaje de alerta (La caja roja o verde)
        self.status_container = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN),
                    ft.Text("Sin incidencias activas", color=ft.Colors.GREEN_700),
                ]
            ),
            bgcolor=ft.Colors.GREEN_50,
            border_radius=8,
            padding=10,
            expand=True,
            alignment=ft.alignment.center_left,
        )

        self.last_update_text = ft.Text(
            "Última actualización: --:--", size=12, color=AppColors.TEXT_LIGHT_GREY
        )

        self.content = ft.Column(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[self.title, self.status_container, self.last_update_text],
        )

    def show_alert(self, message: str, is_critical: bool = True):
        """
        Cambia el estado visual de la tarjeta.
        """
        timestamp = datetime.now().strftime("%H:%M")
        self.last_update_text.value = f"Última actualización: {timestamp}"

        if is_critical:
            # Estilo ALARMA (Caja Roja como en tu diseño)
            self.status_container.bgcolor = ft.Colors.RED_50
            self.status_container.content.controls = [
                ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, color=ft.Colors.RED),
                ft.Text(message, color=ft.Colors.RED_700, weight=ft.FontWeight.BOLD),
            ]
        else:
            # Estilo NORMAL (Verde)
            self.status_container.bgcolor = ft.Colors.GREEN_50
            self.status_container.content.controls = [
                ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN),
                ft.Text(message, color=ft.Colors.GREEN_700),
            ]

        self.update()
