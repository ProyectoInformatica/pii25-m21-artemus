import flet as ft
from ArtemusPark.view.Styles import ColorPalette, Styles


def SensorCard(title, value, unit, subtext, icon):
    return ft.Container(
        bgcolor="#f9fafb",
        border=ft.border.all(1, "#e5e7eb"),
        border_radius=18,
        padding=15,
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Text(title, color=ColorPalette.TEXT_MUTED, size=12),
                        ft.Text(icon),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Row(
                    [
                        ft.Text(str(value), size=22, weight=ft.FontWeight.BOLD),
                        ft.Text(unit, color=ColorPalette.TEXT_MUTED),
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.BASELINE,
                ),
                ft.Text(subtext, size=11, color=ColorPalette.TEXT_MUTED),
            ]
        ),
    )


def DashboardPage(data):
    print(f"[DashboardPage] Rendering dashboard")

    # Capacity Card
    capacity_card = ft.Container(
        expand=1,
        bgcolor=ColorPalette.CARD_BG,
        padding=20,
        border_radius=Styles.BORDER_RADIUS,
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Text(
                            "Aforo actual",
                            weight=ft.FontWeight.BOLD,
                            color=ColorPalette.TEXT_MUTED,
                        ),
                        ft.Container(
                            content=ft.Text("Live", color=ColorPalette.ACCENT, size=10),
                            bgcolor="#dbeafe",
                            padding=5,
                            border_radius=10,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Text(str(data.capacity_current), size=36, weight=ft.FontWeight.BOLD),
                ft.Text(
                    f"Max: {data.capacity_max} · Ocupación: {int(data.capacity_current / data.capacity_max * 100)}%",
                    size=12,
                    color=ColorPalette.TEXT_MUTED,
                ),
            ]
        ),
    )

    # Alert Card
    alert_card = ft.Container(
        expand=1,
        bgcolor=ColorPalette.CARD_BG,
        padding=20,
        border_radius=Styles.BORDER_RADIUS,
        content=ft.Column(
            [
                ft.Text(
                    "Alertas", weight=ft.FontWeight.BOLD, color=ColorPalette.TEXT_MUTED
                ),
                ft.Container(
                    content=ft.Text(
                        "⚠ Humo detectado cerca del lago",
                        color=ColorPalette.DANGER,
                        size=12,
                    ),
                    bgcolor="#fee2e2",
                    padding=8,
                    border_radius=20,
                ),
                ft.Container(expand=True),
                ft.Text("Última act: 09:15", size=11, color=ColorPalette.TEXT_MUTED),
            ]
        ),
    )

    # Grid of Sensors
    sensors_grid = ft.ResponsiveRow(
        columns=4,
        controls=[
            ft.Column(
                col={"sm": 6, "md": 3},
                controls=[
                    SensorCard(
                        "Temperatura", data.temperature, "ºC", "Zona arbolada", "🌡"
                    )
                ],
            ),
            ft.Column(
                col={"sm": 6, "md": 3},
                controls=[
                    SensorCard("Humedad", data.humidity, "%", "Riego activo", "💧")
                ],
            ),
            ft.Column(
                col={"sm": 6, "md": 3},
                controls=[
                    SensorCard("Viento", data.wind_speed, "km/h", "Sin riesgo", "💨")
                ],
            ),
            ft.Column(
                col={"sm": 6, "md": 3},
                controls=[
                    SensorCard("Aire AQI", data.air_quality, "%", "MQ-2 Normal", "☁️")
                ],
            ),
        ],
    )

    # Mock Chart using Flet LineChart
    chart_data = [
        ft.LineChartData(
            data_points=[ft.LineChartDataPoint(i, 20 + (i % 5)) for i in range(10)],
            color=ColorPalette.ACCENT,
            stroke_width=3,
        )
    ]

    chart_container = ft.Container(
        bgcolor="#f9fafb",
        border_radius=18,
        padding=10,
        expand=True,
        content=ft.LineChart(
            data_series=chart_data,
            min_y=15,
            max_y=30,
            min_x=0,
            max_x=9,
            left_axis=ft.ChartAxis(labels_size=0),
            bottom_axis=ft.ChartAxis(labels_size=0),
            border=ft.border.all(0),
        ),
    )

    return ft.Column(
        expand=True,
        scroll=ft.ScrollMode.AUTO,
        controls=[
            ft.Row([capacity_card, alert_card], spacing=20),
            ft.Text("Sensores", weight=ft.FontWeight.BOLD),
            sensors_grid,
            ft.Container(height=20),
            ft.Row(
                height=300,
                controls=[
                    ft.Container(
                        expand=2,
                        bgcolor="#ecfdf5",
                        border_radius=18,
                        content=ft.Column(
                            [
                                ft.Container(
                                    padding=10,
                                    content=ft.Text(
                                        "Mapa del Parque", weight=ft.FontWeight.BOLD
                                    ),
                                ),
                                ft.Icon(
                                    name=ft.Icons.MAP,
                                    size=100,
                                    color=ft.Colors.GREEN_200,
                                ),  # Placeholder for SVG
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                    ),
                    ft.Container(
                        expand=1,
                        content=ft.Column(
                            [
                                ft.Container(
                                    bgcolor=ColorPalette.CARD_BG,
                                    border_radius=18,
                                    padding=10,
                                    content=ft.Column(
                                        [
                                            ft.Text(
                                                "Resumen Temp",
                                                size=12,
                                                weight=ft.FontWeight.BOLD,
                                            ),
                                            ft.Container(
                                                height=100, content=chart_container
                                            ),
                                        ]
                                    ),
                                ),
                                ft.Container(
                                    expand=True,
                                    bgcolor=ColorPalette.CARD_BG,
                                    border_radius=18,
                                    padding=10,
                                    content=ft.Column(
                                        [
                                            ft.Text(
                                                "Registro Alertas",
                                                size=12,
                                                weight=ft.FontWeight.BOLD,
                                            ),
                                            ft.ListTile(
                                                leading=ft.Text("🔥"),
                                                title=ft.Text(
                                                    "Alerta Crítica", size=12
                                                ),
                                                subtitle=ft.Text(
                                                    "Humo en Lago", size=10
                                                ),
                                            ),
                                        ]
                                    ),
                                ),
                            ]
                        ),
                    ),
                ],
            ),
        ],
    )
