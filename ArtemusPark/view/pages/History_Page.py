import time
import flet as ft
from datetime import datetime, timedelta
from ArtemusPark.config.Colors import AppColors
from ArtemusPark.service.Dashboard_Service import DashboardService


class HistoryPage(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.padding = 20
        self.bgcolor = AppColors.BG_MAIN

        self.service = DashboardService()
        self.range_limits = (28, 35)
        self.sort_descending = False
        self._is_mounted = False

        self.sort_button = ft.IconButton(
            icon=ft.Icons.ARROW_UPWARD,
            tooltip="Orden: Más antiguo primero",
            on_click=self._toggle_sort,
            icon_color=ft.Colors.BLUE,
        )

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
                    ]
                ),
                ft.Row([
                    self.sort_button,
                ]),
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
            ],
            rows=[],
        )

        self.table_content = ft.Column(
            controls=[self.data_table],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        )

        self.content = ft.Column(
            expand=True,
            controls=[
                header,
                ft.Tabs(
                    label_color=ft.Colors.BLACK,
                    unselected_label_color=ft.Colors.BLACK87,
                    selected_index=0,
                    on_change=self._on_range_change,
                    tabs=[
                        ft.Tab(text="1 mes"),
                        ft.Tab(text="1 semana"),
                        ft.Tab(text="1 dia"),
                    ],
                ),
                ft.Divider(height=20, color="transparent"),
                ft.Container(
                    content=self.table_content,
                    padding=10,
                    bgcolor=ft.Colors.WHITE,
                    border_radius=12,
                    shadow=ft.BoxShadow(
                        blur_radius=5,
                        color=ft.Colors.with_opacity(0.05, ft.Colors.BLACK),
                    ),
                    expand=True,
                ),
            ],
        )

    def did_mount(self):
        """1. Se ejecuta al entrar: Nos suscribimos a los avisos."""
        self._is_mounted = True
        self.page.pubsub.subscribe(self._on_message)
        self.load_data()

    def will_unmount(self):
        """2. Se ejecuta al salir: Nos desconectamos."""
        self._is_mounted = False

    def _on_message(self, message):
        """3. Escuchamos el 'grito' del main.py"""
        if message == "refresh_dashboard":
            if not self._is_mounted or not self.page:
                return
            self.load_data()

    def _toggle_sort(self, e):
        self.sort_descending = not self.sort_descending
        if self.sort_descending:
            self.sort_button.icon = ft.Icons.ARROW_DOWNWARD
            self.sort_button.tooltip = "Orden: Más reciente primero"
        else:
            self.sort_button.icon = ft.Icons.ARROW_UPWARD
            self.sort_button.tooltip = "Orden: Más antiguo primero"
        self.sort_button.update()
        self.load_data()

    def _on_range_change(self, e):
        index = e.control.selected_index
        self.data_table.rows.clear()
        self.update()
        
        if index == 0:
            self.range_limits = (28, 35)
        elif index == 1:
            self.range_limits = (6, 8)
        else:
            self.range_limits = (0, 2)
            
        self.load_data()

    def load_data(self):
        """Pide el historial al servicio y rellena la tabla con datos reales según el rango."""
        logs = self.service.get_history_by_range(*self.range_limits)

        logs.sort(key=lambda x: x["timestamp"], reverse=self.sort_descending)
        logs = logs[:30]

        self.data_table.rows.clear() # Limpiar de nuevo por seguridad antes de rellenar

        if not logs:
            self.table_content.scroll = None
            self.table_content.alignment = ft.MainAxisAlignment.CENTER
            self.table_content.controls = [
                ft.Text(
                    "No hay datos disponibles para mostrar.",
                    weight=ft.FontWeight.BOLD,
                    size=16,
                    color=ft.Colors.BLACK54,
                    text_align=ft.TextAlign.CENTER,
                )
            ]
        else:
            self.table_content.scroll = ft.ScrollMode.AUTO
            self.table_content.alignment = ft.MainAxisAlignment.START
            for log in logs:
                row = self._create_row(
                    log["time_str"],
                    log["type"],
                    log["location"],
                    str(log["detail"]),
                )
                self.data_table.rows.append(row)
            self.table_content.controls = [self.data_table]

        self.update()

    def _create_row(self, time, type_e, loc, detail):
        """Crea una fila de datos para la tabla."""

        
        return ft.DataRow(
            cells=[
                ft.DataCell(ft.Text(time, size=12, color=ft.Colors.BLACK)),
                ft.DataCell(
                    ft.Row(
                        [
                            ft.Text(type_e, color=ft.Colors.BLACK),
                        ]
                    )
                ),
                ft.DataCell(ft.Text(loc, color=ft.Colors.BLACK)),
                ft.DataCell(ft.Text(detail, color=ft.Colors.BLACK)),
            ]
        )
