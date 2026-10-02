"""Screen for adding a new radio station."""

from __future__ import annotations

from typing import ClassVar

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import Grid, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Input, Label, Static

from src.core.stations import append_station, create_station


class AddStationScreen(Screen[None]):
    """Form screen for collecting station details and appending to the dataset."""

    TITLE = "Add Radio Station"
    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("escape", "app.pop_screen", "Back"),
        Binding("ctrl+s", "save", "Save Station"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(icon="📡")
        with Vertical(id="add-station-body"), Vertical(id="add-station-card", classes="card"):
            yield Static("📻  [b]Add New Radio Station[/]", id="add-station-header-title")
            yield Static(
                "[dim]Enter station details. Status will automatically be set to pending.[/dim]",
                id="add-station-subtitle",
            )

            with Grid(id="add-station-grid"):
                with Vertical(classes="field-group"):
                    yield Label("Name [b red]*[/]", classes="field-label")
                    yield Input(placeholder="e.g. Radio Paradise", id="input-name")

                with Vertical(classes="field-group"):
                    yield Label("Stream URL [b red]*[/]", classes="field-label")
                    yield Input(
                        placeholder="https://stream.radioparadise.com/aac-320",
                        id="input-stream-url",
                    )

                with Vertical(classes="field-group"):
                    yield Label("Country", classes="field-label")
                    yield Input(placeholder="e.g. United States", id="input-country")

                with Vertical(classes="field-group"):
                    yield Label("Country Code", classes="field-label")
                    yield Input(placeholder="e.g. US", max_length=2, id="input-country-code")

                with Vertical(classes="field-group"):
                    yield Label("Language", classes="field-label")
                    yield Input(placeholder="e.g. english", id="input-language")

                with Vertical(classes="field-group"):
                    yield Label("Tags (comma-separated)", classes="field-label")
                    yield Input(placeholder="e.g. rock, indie, eclectic", id="input-tags")

                with Vertical(classes="field-group"):
                    yield Label("Homepage URL", classes="field-label")
                    yield Input(
                        placeholder="https://radioparadise.com",
                        id="input-homepage-url",
                    )

                with Vertical(classes="field-group"):
                    yield Label("Logo URL", classes="field-label")
                    yield Input(
                        placeholder="https://radioparadise.com/logo.png",
                        id="input-logo-url",
                    )

            yield Static("", id="add-station-error")

            with Horizontal(id="add-station-actions"):
                yield Button("📻 Save Station", variant="primary", id="btn-save")
                yield Button("Cancel", variant="default", id="btn-cancel")
        yield Footer()

    def on_mount(self) -> None:
        card = self.query_one("#add-station-card", Vertical)
        card.border_title = "New Station Entry"
        self.query_one("#input-name", Input).focus()

    def _validate_url(self, url: str) -> bool:
        clean = url.strip().lower()
        return clean.startswith("http://") or clean.startswith("https://")

    def action_save(self) -> None:
        self._submit()

    @on(Button.Pressed, "#btn-save")
    def on_save_pressed(self) -> None:
        self._submit()

    @on(Button.Pressed, "#btn-cancel")
    def on_cancel_pressed(self) -> None:
        self.app.pop_screen()

    def _submit(self) -> None:
        error_widget = self.query_one("#add-station-error", Static)
        error_widget.update("")

        name = self.query_one("#input-name", Input).value.strip()
        stream_url = self.query_one("#input-stream-url", Input).value.strip()
        country = self.query_one("#input-country", Input).value.strip()
        country_code = self.query_one("#input-country-code", Input).value.strip().upper()
        language = self.query_one("#input-language", Input).value.strip()
        tags = self.query_one("#input-tags", Input).value.strip()
        homepage_url = self.query_one("#input-homepage-url", Input).value.strip()
        logo_url = self.query_one("#input-logo-url", Input).value.strip()

        # Validations
        if not name:
            error_widget.update("[bold red]⚠ Station name is required.[/]")
            self.query_one("#input-name", Input).focus()
            return

        if not stream_url:
            error_widget.update("[bold red]⚠ Stream URL is required.[/]")
            self.query_one("#input-stream-url", Input).focus()
            return

        if not self._validate_url(stream_url):
            error_widget.update("[bold red]⚠ Stream URL must begin with http:// or https://[/]")
            self.query_one("#input-stream-url", Input).focus()
            return

        if homepage_url and not self._validate_url(homepage_url):
            error_widget.update("[bold red]⚠ Homepage URL must begin with http:// or https://[/]")
            self.query_one("#input-homepage-url", Input).focus()
            return

        if logo_url and not self._validate_url(logo_url):
            error_widget.update("[bold red]⚠ Logo URL must begin with http:// or https://[/]")
            self.query_one("#input-logo-url", Input).focus()
            return

        station = create_station(
            name,
            stream_url,
            country=country,
            country_code=country_code,
            language=language,
            homepage_url=homepage_url,
            logo_url=logo_url,
            tags=tags,
        )

        try:
            append_station(station)
        except (OSError, ValueError) as exc:
            error_widget.update(f"[bold red]⚠ Failed to save station: {exc}[/]")
            return

        self.notify(
            f"Station '{station.name}' added with status 'pending' (UUID: {station.id[:8]}...)",
            title="Station Added",
            severity="information",
        )
        self.app.pop_screen()
