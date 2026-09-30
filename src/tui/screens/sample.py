"""Screen that shows a random sample of radio stations."""

from typing import ClassVar

from textual.app import ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import Footer, Header, Static

from src.core.stations import Station, load_stations, pick_random


def _format_station(station: Station, index: int) -> str:
    def field(label: str, value: str) -> str:
        display = value if value else "[dim]—[/dim]"
        return f"  [b]{label}:[/b] {display}"

    if station.country and station.country_code:
        country = f"{station.country} ({station.country_code})"
    else:
        country = station.country or station.country_code

    lines = [
        f"[b cyan]{index}. {station.name}[/b cyan]",
        field("ID", station.id),
        field("Country", country),
        field("Language", station.language),
        field("Stream", station.stream_url),
        field("Homepage", station.homepage_url),
        field("Logo", station.logo_url),
        field("Tags", station.tags),
    ]
    return "\n".join(lines)


class SampleScreen(Screen[None]):
    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("escape", "app.pop_screen", "Back"),
        Binding("r", "reshuffle", "Pick again"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._stations = load_stations()

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="body"), VerticalScroll(id="stations"):
            yield Static(id="station-list")
        yield Footer()

    def on_mount(self) -> None:
        self.action_reshuffle()

    def action_reshuffle(self) -> None:
        sample = pick_random(self._stations, n=3)
        content = "\n\n".join(
            _format_station(station, i) for i, station in enumerate(sample, start=1)
        )
        self.query_one("#station-list", Static).update(content)
