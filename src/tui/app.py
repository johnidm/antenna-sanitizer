"""Textual application root."""

from typing import ClassVar

from textual.app import App
from textual.binding import Binding, BindingType

from src.core.rules import default_rules
from src.core.sanitizer import Sanitizer
from src.tui.screens.home import HomeScreen


class AntennaSanitizerApp(App[None]):
    TITLE = "Antenna Sanitizer"
    CSS_PATH = "styles/app.tcss"
    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("q", "quit", "Quit"),
        Binding("d", "toggle_dark", "Toggle dark mode"),
    ]

    def __init__(self, sanitizer: Sanitizer | None = None) -> None:
        super().__init__()
        self.sanitizer = sanitizer or Sanitizer.from_rules(default_rules())

    def on_mount(self) -> None:
        self.push_screen(HomeScreen(self.sanitizer))

    def action_toggle_dark(self) -> None:
        self.theme = "textual-light" if self.current_theme.dark else "textual-dark"
