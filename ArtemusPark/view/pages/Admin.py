import flet as ft
from ArtemusPark.view.Styles import ColorPalette


def AdminPage(controller):
    print(f"[AdminPage] Rendering admin options")

    return ft.Column([
        ft.Text("Administración del Sistema", size=24, weight=ft.FontWeight.BOLD),
        ft.Divider(),
        ft.Container(
            bgcolor="#fef2f2",
            border=ft.border.all(1, "#fca5a5"),
            border_radius=16,
            padding=24,
            content=ft.Column([
                ft.Row([ft.Text("🚨", size=30),
                        ft.Text("ZONA DE PELIGRO", color="#991b1b", weight=ft.FontWeight.BOLD, size=20)]),
                ft.Text("Estas acciones afectan a la seguridad física del parque.", color="#7f1d1d"),
                ft.ElevatedButton(
                    "📢 ENVIAR ALERTA GENERAL DE EVACUACIÓN",
                    color=ft.Colors.WHITE,
                    bgcolor=ColorPalette.DANGER,
                    on_click=lambda _: controller.trigger_emergency()
                )
            ])
        )
    ])