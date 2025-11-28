import flet as ft
from ArtemusPark.controller.App_Controller import AppController
from ArtemusPark.view.Main_View import MainView


def main(page: ft.Page):
    print(f"[Main] Application started")

    page.title = "Artemus Smart Park"
    page.padding = 0
    page.bgcolor = "#131921"  # Matches sidebar background
    page.theme_mode = ft.ThemeMode.LIGHT

    # Initialize Controller
    controller = AppController(page)

    # Build UI
    page.add(MainView(page, controller))


if __name__ == "__main__":
    ft.app(target=main)