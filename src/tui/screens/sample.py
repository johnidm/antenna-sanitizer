"""Screen that shows a random sample of radio stations."""

from typing import ClassVar, cast

from textual.app import ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import Footer, Header

from src.core.stations import pick_random
from src.tui.widgets.station_card import StationCard


class SampleScreen(Screen[None]):
    TITLE = "Random stations"
    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("escape", "app.pop_screen", "Back"),
        Binding("r", "reshuffle", "Pick again"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="body"):
            yield VerticalScroll(id="stations")
        yield Footer()

    def on_mount(self) -> None:
        self.action_reshuffle()

    def action_reshuffle(self) -> None:
        from src.tui.app import AntennaSanitizerApp  # noqa: PLC0415

        app = cast(AntennaSanitizerApp, self.app)
        try:
            stations = app.get_stations()
            sample = pick_random(stations, n=3)
        except (OSError, ValueError) as exc:
            self.notify(str(exc), title="Stations unavailable", severity="error")
            self.app.pop_screen()
            return

        container = self.query_one("#stations", VerticalScroll)
        container.remove_children()
        for station in sample:
            container.mount(StationCard(station))
