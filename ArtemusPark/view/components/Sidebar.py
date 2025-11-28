import flet as ft
from ArtemusPark.view.Styles import ColorPalette


def Sidebar(controller):
    print(f"[Sidebar] Building sidebar component")

    def create_nav_item(icon, label, data_target, active=False):
        return ft.Container(
            data=data_target,
            padding=ft.padding.all(12),
            border_radius=ft.border_radius.all(50),
            bgcolor="#1f2933" if active else ft.Colors.TRANSPARENT,
            on_click=controller.navigate,
            content=ft.Row(
                controls=[
                    ft.Text(icon, size=18),
                    ft.Text(label, color="#f9fafb" if active else "#9ca3af", weight=ft.FontWeight.W_500),
                ],
                spacing=12
            )
        )

    nav_items = ft.Column(
        spacing=10,
        controls=[
            create_nav_item("📊", "Dashboard", "dashboard", active=True),
            create_nav_item("🧾", "Historial", "history"),
            create_nav_item("🛠", "Mantenimiento", "maintenance"),
            create_nav_item("⚙️", "Administración", "admin"),
        ]
    )

    # Registramos la columna en el controlador para poder actualizar los estados visuales (active)
    controller.set_sidebar_reference(nav_items)

    return ft.Container(
        width=260,
        bgcolor=ColorPalette.BG_DARK,
        padding=24,
        content=ft.Column(
            controls=[
                # CORRECCIÓN: Se eliminó 'letter_spacing=2' porque causaba el error
                ft.Text("ARTEMUS", size=26, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                ft.Container(height=30),
                nav_items,
                ft.Container(expand=True),
                ft.Text("Artemus Smart Park · v0.4", color="#4b5563", size=12)
            ]
        )
    )