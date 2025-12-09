import flet as ft


class TempChart(ft.Container):
    def __init__(self):
        super().__init__()
        self.height = 300  # Le damos un poco más de altura para que respire
        self.bgcolor = "#ffffff"
        self.border_radius = 18
        self.border = ft.border.all(1, "#e5e7eb")
        self.padding = 20

        # Datos de ejemplo
        self.data_points = [
            ft.LineChartDataPoint(0, 23),
            ft.LineChartDataPoint(1, 24),
            ft.LineChartDataPoint(2, 23.5),
            ft.LineChartDataPoint(3, 22),
            ft.LineChartDataPoint(4, 24.5),
            ft.LineChartDataPoint(5, 25),
            ft.LineChartDataPoint(6, 24),
        ]

        self.chart = ft.LineChart(
            data_series=[
                ft.LineChartData(
                    data_points=self.data_points,
                    stroke_width=3,
                    color="#2563eb",
                    curved=True,
                    stroke_cap_round=True,
                    # CORREGIDO: Usamos Hex directo con transparencia (~10% opacidad)
                    below_line_bgcolor="#1a2563eb",
                )
            ],
            border=ft.border.only(
                bottom=ft.border.BorderSide(1, "#e5e7eb"),
                left=ft.border.BorderSide(1, "transparent"),
            ),
            left_axis=ft.ChartAxis(
                labels=[ft.ChartAxisLabel(value=20, label=ft.Text("20°", size=10))],
                labels_size=30,
            ),
            bottom_axis=ft.ChartAxis(
                labels=[
                    ft.ChartAxisLabel(value=0, label=ft.Text("00:00", size=10)),
                    ft.ChartAxisLabel(value=3, label=ft.Text("06:00", size=10)),
                    ft.ChartAxisLabel(value=6, label=ft.Text("12:00", size=10)),
                ],
                labels_size=20,
            ),
            tooltip_bgcolor="#111827",
            min_y=15,
            max_y=30,
            expand=True,
        )

        self.content = ft.Column(
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        # CORREGIDO: Color válido (#6b7280)
                        ft.Text(
                            "Resumen (temperatura)",
                            size=14,
                            weight=ft.FontWeight.BOLD,
                            color="#6b7280",
                        ),
                        ft.Text("Última hora", size=12, color="#9ca3af"),
                    ],
                ),
                ft.Container(height=20),
                self.chart,
            ]
        )
