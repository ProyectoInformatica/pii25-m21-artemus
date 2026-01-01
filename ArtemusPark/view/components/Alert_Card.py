import flet as ft
from datetime import datetime
from ArtemusPark.config.Colors import AppColors


class AlertCard(ft.Container):
    def __init__(self):
        super().__init__()
        self.bgcolor = AppColors.BG_CARD
        self.border_radius = 12
        self.padding = 20
        self.border = ft.border.all(1, ft.Colors.GREY_300)

        self.icon_alert = ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN, size=40)
        self.title_alert = ft.Text(
            "Sistema Normal", size=16, weight="bold", color=AppColors.TEXT_MAIN
        )
        self.desc_alert = ft.Text(
            "No hay incidencias activas.", size=12, color=AppColors.TEXT_MUTED
        )

        self.content = ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[self.icon_alert, self.title_alert, self.desc_alert],
        )

    def show_alert(self, title, description, is_critical=False):
        """
        Método para actualizar la alerta desde fuera.
        """
        self.title_alert.value = title
        self.desc_alert.value = description

        if is_critical:
            self.icon_alert.name = ft.Icons.WARNING_AMBER_ROUNDED
            self.icon_alert.color = ft.Colors.RED
            self.bgcolor = ft.Colors.RED_50
            self.border = ft.border.all(2, ft.Colors.RED)
        else:
            self.icon_alert.name = ft.Icons.INFO
            self.icon_alert.color = ft.Colors.BLUE
            self.bgcolor = AppColors.BG_CARD
            self.border = ft.border.all(1, ft.Colors.GREY_300)

        self.update()
