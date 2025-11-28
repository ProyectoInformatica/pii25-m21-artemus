import flet as ft


class ColorPalette:
    BG_DARK = "#131921"
    BG_LIGHT = "#f3f4f6"
    CARD_BG = "#ffffff"
    ACCENT = "#2563eb"
    DANGER = "#dc2626"
    SUCCESS = "#10b981"
    WARNING = "#f59e0b"
    TEXT_MAIN = "#111827"
    TEXT_MUTED = "#6b7280"


class Styles:
    SIDEBAR_WIDTH = 260
    BORDER_RADIUS = 16
    PADDING = 20

    SHADOW = ft.BoxShadow(
        spread_radius=1,
        blur_radius=10,
        color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK),
    )