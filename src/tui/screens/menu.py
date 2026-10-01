"""Main menu screen."""

from typing import ClassVar, cast

from textual import on, work
from textual.app import ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import Vertical
from textual.content import Content
from textual.screen import Screen
from textual.widgets import Footer, Header, OptionList, Static
from textual.widgets.option_list import Option

from src.tui.screens.sample import SampleScreen
from src.tui.screens.sanitize import SanitizeScreen
from src.tui.widgets.banner import Banner


def _menu_option(icon: str, title: str, description: str, option_id: str) -> Option:
    prompt = Content.from_markup(
        f"{icon}  [b]{title}[/b]\n    [dim]{description}[/dim]",
    )
    return Option(prompt, id=option_id)


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
                _menu_option(
                    "🎲",
                    "Random stations",
                    "Tune into 3 stations picked at random",
                    "random-stations",
                ),
                None,
                _menu_option("✨", "Sanitize text", "In development", "sanitize"),
                id="menu",
                classes="card",
            )
            menu.border_title = "Main menu"
            yield menu
            yield Static(self._stats("loading stations…"), id="stats")
        yield Footer()

    def on_mount(self) -> None:
        self._load_station_count()

    def _stats(self, stations: str) -> str:
        return f"[$secondary]●[/] {stations}"

    @work(thread=True, exclusive=True)
    def _load_station_count(self) -> None:
        from src.tui.app import AntennaSanitizerApp  # noqa: PLC0415

        app = cast(AntennaSanitizerApp, self.app)
        try:
            label = f"{len(app.get_stations()):,} stations"
        except OSError, ValueError:
            label = "[$error]stations unavailable[/]"
        app.call_from_thread(self.query_one("#stats", Static).update, self._stats(label))

    @on(OptionList.OptionSelected)
    def on_option_selected(self, event: OptionList.OptionSelected) -> None:
        match event.option.id:
            case "random-stations":
                self.app.push_screen(SampleScreen())
            case "sanitize":
                self.app.push_screen(SanitizeScreen())
