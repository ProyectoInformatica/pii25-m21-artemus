import flet as ft


class TempChart(ft.Container):
    def __init__(self):
        super().__init__()

        # --- TU ESTILO ORIGINAL ---
        self.expand = True
        self.constraints = ft.BoxConstraints(min_height=400)
        self.bgcolor = "#ffffff"
        self.border_radius = 12
        self.border = ft.border.all(1, ft.Colors.GREY_300)
        self.padding = 20

        # --- DATOS INICIALES (Con referencia para poder editar luego) ---
        self.main_line = ft.LineChartData(
            data_points=[
                ft.LineChartDataPoint(0, 0),
            ],
            stroke_width=3,
            color="#2563eb",  # Tu azul
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
                labels=[ft.ChartAxisLabel(value=20, label=ft.Text("20°", size=10))],
                labels_size=30,
            ),
            bottom_axis=ft.ChartAxis(
                labels=[
                    ft.ChartAxisLabel(value=0, label=ft.Text("Inicio", size=10)),
                    ft.ChartAxisLabel(value=5, label=ft.Text("Actual", size=10)),
                ],
                labels_size=20,
            ),
            tooltip_bgcolor="#111827",
            min_y=15,
            max_y=35,  # Ajustado para rango 20-30ºC
            expand=True,
        )

        self.content = ft.Column(
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text("Resumen (temperatura)", size=14, weight=ft.FontWeight.BOLD, color="#6b7280"),
                        ft.Text("Última hora", size=12, color="#9ca3af"),
                    ],
                ),
                ft.Container(height=20),
                self.chart,
            ]
        )

    # --- MÉTODO PARA RECIBIR DATOS DEL SERVICE ---
    def update_data(self, chart_data: list):
        if not chart_data:
            return

        new_points = []
        for p in chart_data:
            new_points.append(
                ft.LineChartDataPoint(
                    x=p["x"],
                    y=p["y"],
                    tooltip=f"{p['y']}°C\n{p.get('tooltip', '')}"
                )
            )

        self.main_line.data_points = new_points
        self.chart.update()