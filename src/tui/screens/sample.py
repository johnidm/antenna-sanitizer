"""Screen that shows a random sample of radio stations."""

from typing import ClassVar, cast

from textual import events
from textual.app import ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import Grid, VerticalScroll
from textual.screen import Screen
from textual.widgets import Footer, Header, Static

from src.core.stations import pick_random
from src.tui.widgets.station_card import StationCard

SAMPLE_SIZE = 3
# Below this width the cards stack in a single column.
NARROW_WIDTH = 110


class SampleScreen(Screen[None]):
    TITLE = "Random stations"
    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("escape", "app.pop_screen", "Back"),
        Binding("r", "reshuffle", "Pick again"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(icon="📡")
        with VerticalScroll(id="body"):
            yield Static(id="sample-heading")
            yield Grid(id="stations")
        yield Footer()

    def on_mount(self) -> None:
        self.action_reshuffle()

    def on_resize(self, event: events.Resize) -> None:
        self.query_one("#stations", Grid).set_class(event.size.width < NARROW_WIDTH, "-narrow")

    def action_reshuffle(self) -> None:
        from src.tui.app import AntennaSanitizerApp  # noqa: PLC0415

        app = cast(AntennaSanitizerApp, self.app)
        try:
            stations = app.get_stations()
            sample = pick_random(stations, n=SAMPLE_SIZE)
        except (OSError, ValueError) as exc:
            self.notify(str(exc), title="Stations unavailable", severity="error")
            self.app.pop_screen()
            return

        self.query_one("#sample-heading", Static).update(
            f"📻  Now sampling [b $primary]{SAMPLE_SIZE}[/] of "
            f"[b]{len(stations):,}[/] stations  [dim]— press [b]r[/b] to reshuffle[/dim]"
        )
        container = self.query_one("#stations", Grid)
        container.remove_children()
        container.mount_all(StationCard(station) for station in sample)
