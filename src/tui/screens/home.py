"""Main screen: type input, see the sanitized result live."""

from typing import ClassVar

from textual.app import ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Footer, Header, Input

from src.core.sanitizer import Sanitizer
from src.tui.widgets.result_panel import ResultPanel


class HomeScreen(Screen[None]):
    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("escape", "app.pop_screen", "Back"),
    ]

    def __init__(self, sanitizer: Sanitizer) -> None:
        super().__init__()
        self.sanitizer = sanitizer

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="body"):
            yield Input(placeholder="Type something to sanitize…", id="source")
            yield ResultPanel(id="result")
        yield Footer()

    def on_input_changed(self, event: Input.Changed) -> None:
        self.query_one(ResultPanel).result = self.sanitizer.sanitize(event.value)
