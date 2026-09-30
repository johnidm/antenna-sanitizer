"""Sanitize playground: type input, see the sanitized result live."""

from typing import ClassVar

from textual.app import ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import Footer, Header, Input

from src.core.sanitizer import Sanitizer
from src.tui.widgets.result_panel import ResultPanel


class SanitizeScreen(Screen[None]):
    TITLE = "Sanitize text"
    AUTO_FOCUS = "#source"
    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("escape", "app.pop_screen", "Back"),
    ]

    def __init__(self, sanitizer: Sanitizer) -> None:
        super().__init__()
        self.sanitizer = sanitizer

    def compose(self) -> ComposeResult:
        yield Header(icon="📡")
        with VerticalScroll(id="body"):
            with Vertical(id="source-card", classes="card") as card:
                card.border_title = "Input"
                card.border_subtitle = "type or paste anything"
                yield Input(placeholder="Type something to sanitize…", id="source")
            yield ResultPanel([rule.name for rule in self.sanitizer.rules], id="result")
        yield Footer()

    def on_input_changed(self, event: Input.Changed) -> None:
        panel = self.query_one(ResultPanel)
        panel.result = self.sanitizer.sanitize(event.value) if event.value else None
