"""Textual application root."""

from typing import ClassVar

from textual.app import App
from textual.binding import Binding, BindingType

from src.core.rules import default_rules
from src.core.sanitizer import Sanitizer
from src.core.stations import Station, load_stations
from src.tui.screens.menu import MenuScreen


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
        self._stations: list[Station] | None = None

    def get_stations(self) -> list[Station]:
        """Return stations, loading the CSV once on first use."""
        if self._stations is None:
            self._stations = load_stations()
        return self._stations

    def on_mount(self) -> None:
        self.push_screen(MenuScreen(self.sanitizer))

    def action_toggle_dark(self) -> None:
        self.theme = "textual-light" if self.current_theme.dark else "textual-dark"
