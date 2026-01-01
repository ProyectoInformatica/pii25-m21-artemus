import flet as ft
from ArtemusPark.config.Colors import AppColors
from ArtemusPark.service.Dashboard_Service import DashboardService


class HistoryPage(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.padding = 20
        self.bgcolor = AppColors.BG_MAIN

        
        self.service = DashboardService()

        
        header = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Row(
                    [
                        ft.Text(
                            "Historial de Eventos Reales",
                            size=24,
                            weight="bold",
                            color=ft.Colors.BLACK,
                        ),
                        
                        ft.Container(
                            content=ft.Text(
                                "LIVE", size=10, color=ft.Colors.WHITE, weight="bold"
                            ),
                            bgcolor=ft.Colors.RED_400,
                            padding=ft.padding.symmetric(horizontal=6, vertical=2),
                            border_radius=4,
                            margin=ft.margin.only(left=10),
                        ),
                    ]
                ),
                ft.OutlinedButton(
                    "Exportar CSV",
                    icon=ft.Icons.DOWNLOAD,
                    style=ft.ButtonStyle(color=ft.Colors.BLUE),
                ),
            ],
        )

        
        self.data_table = ft.DataTable(
            width=float("inf"),
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            border=ft.border.all(1, ft.Colors.GREY_200),
            heading_row_color=ft.Colors.GREY_100,
            
            columns=[
                ft.DataColumn(
                    ft.Text("Fecha/Hora", color=ft.Colors.BLACK, weight="bold")
                ),
                ft.DataColumn(ft.Text("Tipo", color=ft.Colors.BLACK, weight="bold")),
                ft.DataColumn(
                    ft.Text("Ubicación", color=ft.Colors.BLACK, weight="bold")
                ),
                ft.DataColumn(
                    ft.Text("Valor/Detalle", color=ft.Colors.BLACK, weight="bold")
                ),
                ft.DataColumn(ft.Text("Estado", color=ft.Colors.BLACK, weight="bold")),
            ],
            rows=[],  
        )

        self.content = ft.Column(
            scroll=ft.ScrollMode.AUTO,
            controls=[
                header,
                ft.Divider(height=20, color="transparent"),
                ft.Container(
                    content=self.data_table,
                    padding=10,
                    bgcolor=ft.Colors.WHITE,
                    border_radius=12,
                    shadow=ft.BoxShadow(
                        blur_radius=5,
                        color=ft.Colors.with_opacity(0.05, ft.Colors.BLACK),
                    ),
                ),
            ],
        )

    

    def did_mount(self):
        """1. Se ejecuta al entrar: Nos suscribimos a los avisos."""
        self.page.pubsub.subscribe(self._on_message)
        self.load_data()

    def will_unmount(self):
        """2. Se ejecuta al salir: Nos desconectamos."""
        self.page.pubsub.unsubscribe_all()

    def _on_message(self, message):
        """3. Escuchamos el 'grito' del main.py"""
        if message == "refresh_dashboard":
            self.load_data()

    

    def load_data(self):
        """Pide el historial al servicio y rellena la tabla"""
        
        logs = self.service.get_all_history_logs()

        self.data_table.rows.clear()

        
        for log in logs[:30]:
            row = self._create_row(
                log["time_str"],
                log["type"],
                log["location"],
                str(log["detail"]),
                log["status"],
            )
            self.data_table.rows.append(row)

        self.update()

    def _create_row(self, time, type_e, loc, detail, status):
        """Crea una fila de datos para la tabla."""
        status_upper = str(status).upper()

        
        if status_upper in ["ALERTA", "WARNING", "HOT", "OFFLINE", "CERRADA"]:
            color_bg = ft.Colors.RED_50
            color_txt = ft.Colors.RED
        elif status_upper in [
            "NORMAL",
            "SAFE",
            "CLEAR",
            "SUCCESS",
            "OK",
            "ON",
            "ABIERTA",
        ]:
            color_bg = ft.Colors.GREEN_50
            color_txt = ft.Colors.GREEN
        else:
            color_bg = ft.Colors.BLUE_50
            color_txt = ft.Colors.BLUE

        return ft.DataRow(
            cells=[
                ft.DataCell(ft.Text(time, size=12, color=ft.Colors.BLACK)),
                ft.DataCell(
                    ft.Row(
                        [
                            ft.Icon(ft.Icons.CIRCLE, size=8, color=color_txt),
                            ft.Text(type_e, color=ft.Colors.BLACK),
                        ]
                    )
                ),
                ft.DataCell(ft.Text(loc, color=ft.Colors.BLACK)),
                ft.DataCell(ft.Text(detail, color=ft.Colors.BLACK)),
                ft.DataCell(
                    ft.Container(
                        content=ft.Text(
                            status, size=10, color=color_txt, weight="bold"
                        ),
                        bgcolor=color_bg,
                        padding=ft.padding.symmetric(horizontal=8, vertical=4),
                        border_radius=10,
                    )
                ),
            ]
        )
