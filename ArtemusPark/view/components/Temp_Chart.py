import flet as ft


class TempChart(ft.Container):
    def __init__(self):
        super().__init__()

        self.expand = True
        self.constraints = ft.BoxConstraints(min_height=400)
        self.bgcolor = "#ffffff"
        self.border_radius = 12
        self.border = ft.border.all(1, ft.Colors.GREY_300)
        self.padding = 20

        self.main_line = ft.LineChartData(
            data_points=[
                ft.LineChartDataPoint(0, 0),
            ],
            stroke_width=3,
            color="#2563eb",
            curved=True,
            stroke_cap_round=True,
            below_line_bgcolor="#1a2563eb",
        )

        self.chart = ft.LineChart(
            data_series=[self.main_line],
            border=ft.border.only(
                bottom=ft.border.BorderSide(1, "#e5e7eb"),
                left=ft.border.BorderSide(1, "transparent"),
            ),
            left_axis=ft.ChartAxis(
                labels=[
                    ft.ChartAxisLabel(value=10, label=ft.Text("10°C", size=10)),
                    ft.ChartAxisLabel(value=20, label=ft.Text("20°C", size=10)),
                    ft.ChartAxisLabel(value=30, label=ft.Text("30°C", size=10)),
                    ft.ChartAxisLabel(value=40, label=ft.Text("40°C", size=10)),
                ],
                labels_size=42,
            ),
            bottom_axis=ft.ChartAxis(
                labels=[
                    ft.ChartAxisLabel(value=0, label=ft.Text("00h", size=10)),
                    ft.ChartAxisLabel(value=3, label=ft.Text("03h", size=10)),
                    ft.ChartAxisLabel(value=6, label=ft.Text("06h", size=10)),
                    ft.ChartAxisLabel(value=9, label=ft.Text("09h", size=10)),
                    ft.ChartAxisLabel(value=12, label=ft.Text("12h", size=10)),
                    ft.ChartAxisLabel(value=15, label=ft.Text("15h", size=10)),
                    ft.ChartAxisLabel(value=18, label=ft.Text("18h", size=10)),
                    ft.ChartAxisLabel(value=21, label=ft.Text("21h", size=10)),
                    ft.ChartAxisLabel(value=24, label=ft.Text("24h", size=10)),
                ],
                labels_size=40,
            ),
            tooltip_bgcolor="#111827",
            min_x=0,
            max_x=24,
            min_y=10,
            max_y=45,
            expand=True,
        )

        self.content = ft.Column(
            expand=True,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text(
                            "Resumen (temperatura)",
                            size=14,
                            weight=ft.FontWeight.BOLD,
                            color="#000000",
                        ),
                        ft.Text("Actualmente", size=12, color="#000000"),
                    ],
                ),
                ft.Container(height=20),
                self.chart,
            ],
        )

    def update_data(self, chart_data: list):
        """Actualiza los puntos del gráfico con nuevos datos."""
        if not chart_data:
            return

        new_points = []
        for p in chart_data:
            new_points.append(
                ft.LineChartDataPoint(
                    x=p["x"],
                    y=p["y"],
                    tooltip=f"{p ['y']:.2f}°C\n{p .get ('tooltip','')}",
                )
            )

        self.main_line.data_points = new_points
        y_values = [point.y for point in new_points]
        if y_values:
            min_temp = min(y_values)
            max_temp = max(y_values)
            self.chart.min_y = min(0, int(min_temp // 5) * 5)
            self.chart.max_y = max(45, int((max_temp + 4) // 5) * 5)
        if self.chart.page:
            try:
                self.chart.update()
            except Exception:
                pass
