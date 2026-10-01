"""Textual application root."""

from typing import ClassVar

from textual.app import App
from textual.binding import Binding, BindingType

from src.tui.screens.menu import MenuScreen
from src.tui.theme import ANTENNA_DARK, ANTENNA_LIGHT


class AntennaSanitizerApp(App[None]):
    TITLE = "Antenna Sanitizer"
    CSS_PATH = "styles/app.tcss"
    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("q", "quit", "Quit"),
        Binding("d", "toggle_dark", "Toggle dark mode"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.register_theme(ANTENNA_DARK)
        self.register_theme(ANTENNA_LIGHT)
        self.theme = ANTENNA_DARK.name

    def on_mount(self) -> None:
        self.push_screen(MenuScreen())

    def action_toggle_dark(self) -> None:
        self.theme = ANTENNA_LIGHT.name if self.current_theme.dark else ANTENNA_DARK.name
