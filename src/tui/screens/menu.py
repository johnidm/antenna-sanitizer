"""Main menu screen."""

from typing import ClassVar

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Footer, Header, OptionList
from textual.widgets.option_list import Option

from src.core.sanitizer import Sanitizer
from src.tui.screens.sample import SampleScreen
from src.tui.screens.sanitize import SanitizeScreen


class MenuScreen(Screen[None]):
    TITLE = "Menu"
    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("escape", "app.quit", "Quit", show=False),
    ]

    def __init__(self, sanitizer: Sanitizer) -> None:
        super().__init__()
        self.sanitizer = sanitizer

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="body"):
            yield OptionList(
                Option("Show 3 random stations", id="random-stations"),
                Option("Sanitize text", id="sanitize"),
                id="menu",
            )
        yield Footer()

    @on(OptionList.OptionSelected)
    def on_option_selected(self, event: OptionList.OptionSelected) -> None:
        match event.option.id:
            case "random-stations":
                self.app.push_screen(SampleScreen())
            case "sanitize":
                self.app.push_screen(SanitizeScreen(self.sanitizer))
