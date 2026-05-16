import flet as ft
from datetime import datetime, timedelta


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
                    ft.ChartAxisLabel(value=0, label=ft.Text("0°C", size=10)),
                    ft.ChartAxisLabel(value=10, label=ft.Text("10°C", size=10)),
                    ft.ChartAxisLabel(value=20, label=ft.Text("20°C", size=10)),
                    ft.ChartAxisLabel(value=30, label=ft.Text("30°C", size=10)),
                    ft.ChartAxisLabel(value=40, label=ft.Text("40°C", size=10)),
                    ft.ChartAxisLabel(value=50, label=ft.Text("50°C", size=10)),
                ],
                labels_size=42,
            ),
            bottom_axis=ft.ChartAxis(
                labels=[],  # Dynamic labels
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
                            "Evolución de Temperatura (24h)",
                            size=14,
                            weight=ft.FontWeight.BOLD,
                            color="#000000",
                        ),
                        ft.Text("Últimas 24 horas", size=12, color="#000000"),
                    ],
                ),
                ft.Container(height=20),
                self.chart,
            ],
        )
        self._update_time_labels()

    def _update_time_labels(self):
        """Genera etiquetas de tiempo para el eje X basadas en la hora actual."""
        now = datetime.now()
        day_ago = now - timedelta(hours=24)
        labels = []

        # Generar etiquetas cada 3 horas
        for i in range(0, 25, 3):
            label_time = day_ago + timedelta(hours=i)
            labels.append(
                ft.ChartAxisLabel(
                    value=i, label=ft.Text(label_time.strftime("%H:%M"), size=10)
                )
            )
        self.chart.bottom_axis.labels = labels

    def update_data(self, chart_data: list):
        """Actualiza los puntos del gráfico con nuevos datos."""
        self._update_time_labels()
        if not chart_data:
            return

        new_points = []
        for p in chart_data:
            new_points.append(
                ft.LineChartDataPoint(
                    x=p["x"],
                    y=p["y"],
                    tooltip=f"{p['y']:.1f}°C\n{p.get('tooltip','')}",
                )
            )

        self.main_line.data_points = new_points
        y_values = [point.y for point in new_points]
        if y_values:
            min_temp = min(y_values)
            max_temp = max(y_values)
            self.chart.min_y = max(0, int(min_temp // 5) * 5 - 5)
            self.chart.max_y = int((max_temp + 5) // 5) * 5 + 5

        if self.chart.page:
            try:
                self.chart.update()
            except Exception:
                pass
