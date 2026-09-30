"""Station card: name, country, language, tags, and openable URLs."""

from __future__ import annotations

import json

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.markup import escape
from textual.widgets import Link, Static

from src.core.stations import Station

_EMPTY = "[dim]—[/dim]"
_MAX_TAGS = 5


def _country_label(station: Station) -> str:
    if station.country and station.country_code:
        return f"{station.country} ({station.country_code})"
    return station.country or station.country_code


def _parse_tags(raw: str) -> list[str]:
    try:
        tags = json.loads(raw) if raw else []
    except json.JSONDecodeError:
        tags = raw.split(",")
    if not isinstance(tags, list):
        return []
    return [str(tag).strip() for tag in tags if str(tag).strip()]


def _row(label: str, value: str) -> str:
    return f"[dim]{label:<9}[/dim]{value or _EMPTY}"


def _format_fields(station: Station) -> str:
    languages = ", ".join(part.strip() for part in station.language.split(",") if part.strip())
    tags = _parse_tags(station.tags)[:_MAX_TAGS]
    chips = " ".join(f"[$background on $secondary] {escape(tag)} [/]" for tag in tags)
    return "\n".join(
        [
            _row("Country", escape(_country_label(station))),
            _row("Language", escape(languages)),
            _row("Tags", chips),
        ]
    )


class StationCard(Vertical):
    """Displays a station's details and openable URLs."""

    DEFAULT_CSS = """
    StationCard {
        height: auto;
        border: round $primary 60%;
        border-title-color: $primary;
        border-title-style: bold;
        border-subtitle-color: $secondary;
        background: $panel;
        padding: 1 2;

        &:hover, &:focus-within {
            border: round $accent;
            border-title-color: $accent;
        }
    }

    StationCard .fields {
        height: auto;
    }

    StationCard .links {
        height: auto;
        margin-top: 1;
    }

    StationCard .links Link {
        margin-right: 3;
        color: $accent;
        text-style: bold;
    }
    """

    def __init__(self, station: Station) -> None:
        super().__init__()
        self.station = station
        self.border_title = escape(station.name.strip() or "Unnamed station")
        self.border_subtitle = escape(station.country_code)

    def compose(self) -> ComposeResult:
        yield Static(_format_fields(self.station), classes="fields")
        with Horizontal(classes="links"):
            if self.station.stream_url:
                yield Link("▶ Stream", url=self.station.stream_url, tooltip=self.station.stream_url)
            if self.station.homepage_url:
                yield Link(
                    "⌂ Homepage",
                    url=self.station.homepage_url,
                    tooltip=self.station.homepage_url,
                )
