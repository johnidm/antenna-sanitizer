"""Sanitize screen — in development placeholder."""

from typing import ClassVar

from textual.app import ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import Center, Middle
from textual.screen import Screen
from textual.widgets import Footer, Header, Static


class SanitizeScreen(Screen[None]):
    TITLE = "Sanitize text"
    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("escape", "app.pop_screen", "Back"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(icon="📡")
        with Middle(), Center():
            yield Static(
                "🚧  [b]In development[/b]\n\n"
                "[dim]Sanitization features are currently in development.[/dim]",
                id="development-placeholder",
                classes="card",
            )
        yield Footer()
