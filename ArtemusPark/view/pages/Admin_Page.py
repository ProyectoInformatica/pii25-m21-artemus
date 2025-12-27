import flet as ft
import time
import threading
from datetime import datetime

from ArtemusPark.config.Colors import AppColors
from ArtemusPark.service.Dashboard_Service import DashboardService
from ArtemusPark.repository import (
    Light_Repository,
    Temperature_Repository,
    Door_Repository,
)


class AdminPage(ft.Container):
    def __init__(self, user_role="admin"):
        super().__init__()
        self.expand = True
        self.padding = 20
        self.bgcolor = AppColors.BG_MAIN

        # Instancia del servicio
        self.service = DashboardService()
        self.simulation_running = False

        # --- SEGURIDAD ---
        if user_role != "admin":
            self.content = ft.Center(
                ft.Text("Acceso Restringido", size=30, color=ft.Colors.BLACK)
            )
            return

        # --- DATOS GRÁFICA ---
        # Inicializamos 20 puntos de datos
        self.energy_data_points = [ft.LineChartDataPoint(i, 50) for i in range(20)]

        # Inicializamos etiquetas de tiempo
        now_str = datetime.now().strftime("%H:%M:%S")
        self.time_labels = [now_str for _ in range(20)]

        # --- BOTÓN DE CATÁSTROFE (INTELIGENTE) ---
        # Se configurará visualmente en did_mount
        self.btn_catastrophe = ft.ElevatedButton(
            text="CARGANDO ESTADO...",
            icon=ft.Icons.WARNING_AMBER_ROUNDED,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                shape=ft.RoundedRectangleBorder(radius=10),
                padding=20,
            ),
            width=400,
            on_click=self._toggle_catastrophe,
        )

        # Textos Energía
        self.txt_energy_value = ft.Text(
            "Iniciando...",
            size=40,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.BLUE_GREY_800,
        )
        self.txt_energy_detail = ft.Text(
            "Sincronizando...", size=12, color=ft.Colors.GREY
        )

        # Gráfica Energía
        self.chart = ft.LineChart(
            data_series=[
                ft.LineChartData(
                    data_points=self.energy_data_points,
                    stroke_width=3,
                    color=ft.Colors.BLUE,
                    curved=True,
                    stroke_cap_round=True,
                    below_line_bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.BLUE),
                )
            ],
            border=ft.border.all(1, ft.Colors.TRANSPARENT),
            left_axis=ft.ChartAxis(
                labels=[
                    ft.ChartAxisLabel(value=50, label=ft.Text("50kW", size=10)),
                    ft.ChartAxisLabel(value=200, label=ft.Text("200kW", size=10)),
                    ft.ChartAxisLabel(value=400, label=ft.Text("400kW", size=10)),
                    ft.ChartAxisLabel(value=600, label=ft.Text("600kW", size=10)),
                ],
                labels_size=40,
            ),
            bottom_axis=ft.ChartAxis(labels=[], labels_size=20),
            tooltip_bgcolor=ft.Colors.with_opacity(0.8, ft.Colors.BLUE_GREY),
            min_y=0,
            max_y=700,
            min_x=0,
            max_x=19,
            expand=True,
        )

        # --- ESTRUCTURA VISUAL ---
        self.content = ft.ListView(
            spacing=20,
            controls=[
                ft.Text(
                    "Panel de Administración",
                    size=24,
                    weight="bold",
                    color=ft.Colors.BLACK,
                ),
                # Perfil
                self._build_section_container(
                    "Perfil de Administrador",
                    ft.Row(
                        [
                            ft.CircleAvatar(
                                foreground_image_src="https://ui-avatars.com/api/?name=Admin+User&background=0D8ABC&color=fff",
                                radius=30,
                            ),
                            ft.Column(
                                [
                                    ft.Text(
                                        "Super Admin",
                                        weight="bold",
                                        size=16,
                                        color=ft.Colors.BLACK,
                                    ),
                                    ft.Text(
                                        "admin@artemus.park",
                                        color=ft.Colors.GREY_700,
                                        size=12,
                                    ),
                                ]
                            ),
                        ]
                    ),
                ),
                # Emergencia
                self._build_section_container(
                    "Control de Emergencia",
                    ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Text(
                                "Gestión de Protocolos de Seguridad",
                                color=ft.Colors.GREY_700,
                                size=12,
                            ),
                            ft.Container(height=10),
                            self.btn_catastrophe,
                        ],
                    ),
                ),
                # Monitor Energía
                self._build_section_container(
                    "Monitor de Consumo Eléctrico (Tiempo Real)",
                    ft.Container(
                        height=350,
                        content=ft.Column(
                            [
                                ft.Row(
                                    [
                                        ft.Icon(
                                            ft.Icons.ELECTRIC_BOLT,
                                            color=ft.Colors.AMBER,
                                            size=30,
                                        ),
                                        ft.Column(
                                            [
                                                self.txt_energy_value,
                                                self.txt_energy_detail,
                                            ],
                                            spacing=0,
                                        ),
                                    ],
                                    alignment=ft.MainAxisAlignment.CENTER,
                                ),
                                ft.Divider(color="transparent"),
                                self.chart,
                            ]
                        ),
                    ),
                ),
            ],
        )

    # --- CICLO DE VIDA ---
    def did_mount(self):
        self.simulation_running = True

        # 1. Configurar botón visualmente según estado guardado en el Servicio
        self._update_button_state()

        # 2. Iniciar gráfica en segundo plano
        threading.Thread(target=self._realtime_energy_loop, daemon=True).start()

    def will_unmount(self):
        self.simulation_running = False

    # --- ACCIÓN DEL BOTÓN (TOGGLE) ---
    def _toggle_catastrophe(self, e):
        # Leemos estado actual desde la memoria compartida
        is_active = self.service.is_catastrophe_mode()

        if is_active:
            # Si estaba activo, lo APAGAMOS
            self.service.set_catastrophe_mode(False)
            print("AdminPage: Enviando señal 'normal_mode'")
            self.page.pubsub.send_all("normal_mode")
        else:
            # Si estaba apagado, lo ENCENDEMOS
            self.service.set_catastrophe_mode(True)
            print("AdminPage: Enviando señal 'catastrophe_mode'")
            self.page.pubsub.send_all("catastrophe_mode")

        # Actualizamos el botón visualmente
        self._update_button_state()

    def _update_button_state(self):
        """Cambia el color y texto del botón según si hay emergencia o no"""
        is_active = self.service.is_catastrophe_mode()

        if is_active:
            self.btn_catastrophe.text = "DESACTIVAR PROTOCOLO Y RESTAURAR"
            self.btn_catastrophe.bgcolor = (
                ft.Colors.GREEN_700
            )  # Verde para volver a la calma
            self.btn_catastrophe.icon = ft.Icons.CHECK_CIRCLE_OUTLINE
        else:
            self.btn_catastrophe.text = "ACTIVAR PROTOCOLO DE CATÁSTROFE"
            self.btn_catastrophe.bgcolor = ft.Colors.RED_700  # Rojo para peligro
            self.btn_catastrophe.icon = ft.Icons.WARNING_AMBER_ROUNDED

        self.btn_catastrophe.update()

    # --- LÓGICA DE CONSUMO ---
    def _calculate_sensor_load(self) -> dict:
        """Calcula kW basándose en estado real de sensores"""
        base_load = 50.0
        reasons = []

        # 1. LUCES
        lights = Light_Repository.load_all_light_events()
        if lights:
            last_light = lights[-1]
            is_on = (
                last_light.get("is_on")
                if isinstance(last_light, dict)
                else getattr(last_light, "is_on", False)
            )
            if is_on:
                base_load += 150.0
                reasons.append("Luces ON")

        # 2. CLIMATIZACIÓN
        temps = Temperature_Repository.load_all_temperature_measurements()
        if temps:
            last_temp = temps[-1]
            val = (
                last_temp.get("value")
                if isinstance(last_temp, dict)
                else getattr(last_temp, "value", 22)
            )
            if val > 28:
                base_load += 200.0
                reasons.append(f"AC Máximo ({val}ºC)")
            elif val > 24:
                base_load += 100.0
                reasons.append(f"AC Medio ({val}ºC)")
            elif val < 15:
                base_load += 180.0
                reasons.append(f"Calefacción ({val}ºC)")

        # 3. MOTORES (Puertas)
        doors = Door_Repository.load_all_door_events()
        if doors:
            last_door = doors[-1]
            ts = (
                last_door.get("timestamp")
                if isinstance(last_door, dict)
                else getattr(last_door, "timestamp", 0)
            )
            if (time.time() - ts) < 5:
                base_load += 80.0
                reasons.append("Motor Puerta")

        return {"total": base_load, "details": ", ".join(reasons)}

    def _realtime_energy_loop(self):
        """Bucle que actualiza la gráfica"""
        while self.simulation_running:
            # 1. Calcular datos
            load_data = self._calculate_sensor_load()
            current_kw = load_data["total"]
            current_time_str = datetime.now().strftime("%H:%M:%S")

            # 2. Actualizar Textos
            self.txt_energy_value.value = f"{current_kw:.1f} kW"
            self.txt_energy_detail.value = (
                load_data["details"]
                if load_data["details"]
                else "Consumo Base (Standby)"
            )

            # 3. Mover Gráfica
            self.energy_data_points.pop(0)
            for i, p in enumerate(self.energy_data_points):
                p.x = i
            self.energy_data_points.append(ft.LineChartDataPoint(19, current_kw))

            # 4. Mover Eje X (Tiempo)
            self.time_labels.pop(0)
            self.time_labels.append(current_time_str)

            # Reconstruir etiquetas X (una de cada 4 para que no se monten)
            new_labels = []
            for i in range(0, 20, 4):
                new_labels.append(
                    ft.ChartAxisLabel(
                        value=i,
                        label=ft.Text(
                            self.time_labels[i],
                            size=10,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.GREY,
                        ),
                    )
                )
            self.chart.bottom_axis.labels = new_labels

            # Color alerta en gráfica si el consumo es alto
            color = ft.Colors.RED if current_kw > 500 else ft.Colors.BLUE
            self.chart.data_series[0].color = color
            self.chart.data_series[0].below_line_bgcolor = ft.Colors.with_opacity(
                0.2, color
            )

            # 5. Refrescar
            self.chart.update()
            self.txt_energy_value.update()
            self.txt_energy_detail.update()

            time.sleep(1)  # Actualizar cada segundo

    # --- HELPERS ---
    def _build_section_container(self, title, content_control):
        return ft.Container(
            bgcolor=ft.Colors.WHITE,
            padding=20,
            border_radius=12,
            border=ft.border.all(1, ft.Colors.GREY_200),
            content=ft.Column(
                [
                    ft.Text(title, weight="bold", size=16, color=ft.Colors.BLACK),
                    ft.Divider(height=20, color="transparent"),
                    content_control,
                ]
            ),
        )
