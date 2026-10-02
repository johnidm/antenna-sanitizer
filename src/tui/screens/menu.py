"""Main menu screen."""

from typing import ClassVar

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import Vertical
from textual.content import Content
from textual.screen import Screen
from textual.widgets import Footer, Header, OptionList
from textual.widgets.option_list import Option

from src.tui.screens.sample import SampleScreen
from src.tui.screens.sanitize import SanitizeScreen
from src.tui.screens.stats import StatsScreen
from src.tui.widgets.banner import Banner


class MenuScreen(Screen[None]):
    TITLE = "Menu"
    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("escape", "app.quit", "Quit", show=False),
    ]

    def compose(self) -> ComposeResult:
        yield Header(icon="📡")
        with Vertical(id="menu-body"):
            yield Banner()
            menu = OptionList(
                self._menu_option(
                    "🎲",
                    "Random stations",
                    "Tune into 3 stations picked at random",
                    "random-stations",
                ),
                None,
                self._menu_option(
                    "📊",
                    "Stats",
                    "View dataset status counters and export readiness",
                    "stats",
                ),
                None,
                self._menu_option("✨", "Sanitize text", "In development", "sanitize"),
                id="menu",
                classes="card",
            )
            menu.border_title = "Main menu"
            yield menu
        yield Footer()

    @on(OptionList.OptionSelected)
    def on_option_selected(self, event: OptionList.OptionSelected) -> None:
        match event.option.id:
            case "random-stations":
                self.app.push_screen(SampleScreen())
            case "stats":
                self.app.push_screen(StatsScreen())
            case "sanitize":
                self.app.push_screen(SanitizeScreen())

    def _menu_option(self, icon: str, title: str, description: str, option_id: str) -> Option:
        prompt = Content.from_markup(
            f"{icon}  [b]{title}[/b]\n    [dim]{description}[/dim]",
        )
        return Option(prompt, id=option_id)
