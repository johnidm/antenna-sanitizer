"""Station card: name, country, and openable URLs."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Link, Static

from src.core.stations import Station


def _country_label(station: Station) -> str:
    if station.country and station.country_code:
        return f"{station.country} ({station.country_code})"
    return station.country or station.country_code


def _format_fields(station: Station) -> str:
    country = _country_label(station)
    country_display = country if country else "[dim]—[/dim]"
    return "\n".join(
        [
            f"[b cyan]{station.name}[/b cyan]",
            f"[b]Country:[/b] {country_display}",
        ]
    )


class StationCard(Vertical):
    """Displays a station's name, country, and openable URLs."""

    DEFAULT_CSS = """
    StationCard {
        height: auto;
        margin-bottom: 1;
        border: round $primary;
        padding: 1 2;
    }

    StationCard .links {
        height: auto;
        margin-top: 1;
    }

    StationCard .links Link {
        margin-right: 2;
    }
    """

    def __init__(self, station: Station) -> None:
        super().__init__()
        self.station = station

    def compose(self) -> ComposeResult:
        yield Static(_format_fields(self.station))
        with Horizontal(classes="links"):
            if self.station.homepage_url:
                yield Link(
                    "Open homepage",
                    url=self.station.homepage_url,
                    tooltip=self.station.homepage_url,
                )
            if self.station.stream_url:
                yield Link(
                    "Open stream",
                    url=self.station.stream_url,
                    tooltip=self.station.stream_url,
                )
