import flet as ft
from datetime import datetime
from ArtemusPark.config.Colors import AppColors
from ArtemusPark.repository.Requests_Repository import RequestsRepository
from ArtemusPark.repository.Auth_Repository import AuthRepository


class RequestsPage(ft.Container):
    def __init__(self, user_role, current_username):
        super().__init__()
        self.expand = True
        self.padding = 20
        self.bgcolor = AppColors.BG_MAIN

        self.user_role = user_role
        self.current_username = current_username
        self.req_repo = RequestsRepository()
        self.auth_repo = AuthRepository()

        self.requests_column = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO)

        title = "Gestión de Solicitudes" if user_role == "admin" else "Mis Solicitudes"

        self.content = ft.Column(
            [
                ft.Text(title, size=24, weight="bold", color=ft.Colors.BLACK),
                ft.Divider(),
                ft.Container(content=self.requests_column, expand=True),
            ]
        )

    def did_mount(self):
        self._load_requests()

    def _load_requests(self):
        reqs = self.req_repo.get_all_requests()
        # Sort by timestamp desc
        reqs.sort(key=lambda x: x.get("timestamp", 0), reverse=True)

        if self.user_role != "admin":
            reqs = [r for r in reqs if r.get("user") == self.current_username]

        self.requests_column.controls.clear()

        if not reqs:
            self.requests_column.controls.append(
                ft.Text("No hay solicitudes.", color=ft.Colors.GREY)
            )
        else:
            for req in reqs:
                self.requests_column.controls.append(self._build_request_card(req))

        self.requests_column.update()

    def _build_request_card(self, req):
        status = req.get("status")

        icon = ft.Icons.HOURGLASS_EMPTY
        icon_color = ft.Colors.ORANGE
        status_text = "Pendiente"

        if status == "ACCEPTED":
            icon = ft.Icons.THUMB_UP
            icon_color = ft.Colors.GREEN
            status_text = "Aceptada"
        elif status == "REJECTED":
            icon = ft.Icons.THUMB_DOWN
            icon_color = ft.Colors.RED
            status_text = "Rechazada"

        card_content = [
            ft.Row(
                [
                    ft.Icon(icon, color=icon_color),
                    ft.Text(f"Estado: {status_text}", weight="bold", color=icon_color),
                    ft.Container(expand=True),
                    ft.Text(
                        datetime.fromtimestamp(req.get("timestamp", 0)).strftime(
                            "%Y-%m-%d %H:%M"
                        ),
                        size=12,
                        color=ft.Colors.GREY,
                    ),
                ]
            ),
            ft.Text(
                f"Solicitante: {req.get('user')}",
                weight="bold",
                color=ft.Colors.BLACK87,
            ),
            ft.Text(f"Mensaje: {req.get('message')}", color=ft.Colors.BLACK87),
        ]

        if self.user_role == "admin" and status == "PENDING":
            card_content.append(ft.Divider())
            card_content.append(
                ft.Row(
                    [
                        ft.ElevatedButton(
                            "Aceptar",
                            icon=ft.Icons.CHECK,
                            bgcolor=ft.Colors.GREEN,
                            color=ft.Colors.WHITE,
                            on_click=lambda e, r=req: self._handle_request(
                                r, "ACCEPTED"
                            ),
                        ),
                        ft.ElevatedButton(
                            "Rechazar",
                            icon=ft.Icons.CLOSE,
                            bgcolor=ft.Colors.RED,
                            color=ft.Colors.WHITE,
                            on_click=lambda e, r=req: self._handle_request(
                                r, "REJECTED"
                            ),
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.END,
                )
            )

        return ft.Container(
            padding=15,
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            border=ft.border.all(1, ft.Colors.GREY_300),
            content=ft.Column(card_content),
        )

    def _handle_request(self, req, new_status):
        self.req_repo.update_request_status(req["id"], new_status)

        # If accepted and it's a sensor change, we might want to auto-open user dialog or just mark done.
        # Ideally admin should go to user management to assign sensors.
        # We can add a hint or button to jump to user management if we had better navigation context.
        # For now, just update status.

        self.page.snack_bar = ft.SnackBar(
            ft.Text(f"Solicitud marcada como {new_status}")
        )
        self.page.snack_bar.open = True
        self.page.update()
        self._load_requests()
