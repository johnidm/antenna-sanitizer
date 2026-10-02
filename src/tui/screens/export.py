"""Screen for exporting ready stations to a dual-compatible SQL file."""

from __future__ import annotations

from pathlib import Path
from typing import ClassVar

from textual import on, work
from textual.app import ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, ProgressBar, Static

from src.core.export import (
    export_ready_stations_sql,
    generate_export_filename,
    get_default_exports_dir,
)
from src.core.stations import Station, StationStatus, load_stations


class ExportScreen(Screen[None]):
    """SQL export preview and execution screen."""

    TITLE = "Export SQL"
    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("escape", "app.pop_screen", "Back"),
        Binding("e", "export", "Export SQL"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._stations: list[Station] = []
        self._ready_stations: list[Station] = []
        self._output_dir: Path = get_default_exports_dir()
        self._target_filename: str = generate_export_filename()
        self._exported_file: Path | None = None
        self._is_exporting: bool = False
        self._is_loading: bool = True

    def compose(self) -> ComposeResult:
        yield Header(icon="📡")
        with Vertical(id="export-body"), Vertical(id="export-card", classes="card"):
            yield Static("💾  [b]Export Ready Stations to SQL[/]", id="export-header-title")
            yield Static(
                "[dim]Reading dataset and checking export readiness...[/dim]",
                id="export-summary",
            )
            yield Static("", id="export-guardrail")
            yield ProgressBar(id="export-progress", show_eta=True)
            with Horizontal(id="export-actions"):
                yield Button("💾 Export SQL", variant="primary", id="btn-export")
                yield Button("Back", variant="default", id="btn-back")
        yield Footer()

    def on_mount(self) -> None:
        card = self.query_one("#export-card", Vertical)
        card.border_title = "SQL Export (PostgreSQL & SQLite)"
        self.query_one("#export-progress", ProgressBar).display = False
        self.query_one("#btn-export", Button).disabled = True
        self._load_data_worker()

    @work(thread=True)
    def _load_data_worker(self) -> None:
        try:
            stations = load_stations()
            ready_stations = [s for s in stations if s.status == StationStatus.READY]
            self.app.call_from_thread(self._on_data_loaded, stations, ready_stations)
        except (OSError, ValueError) as exc:
            self.app.call_from_thread(self._on_data_load_error, str(exc))

    def _on_data_loaded(self, stations: list[Station], ready_stations: list[Station]) -> None:
        self._stations = stations
        self._ready_stations = ready_stations
        self._is_loading = False
        self._refresh_view()

    def _on_data_load_error(self, error_message: str) -> None:
        self._is_loading = False
        self.notify(error_message, title="Error loading stations", severity="error")
        self._refresh_view()

    def _refresh_view(self) -> None:
        title_widget = self.query_one("#export-header-title", Static)
        summary_widget = self.query_one("#export-summary", Static)
        guardrail_widget = self.query_one("#export-guardrail", Static)
        progress_bar = self.query_one("#export-progress", ProgressBar)
        btn_export = self.query_one("#btn-export", Button)
        btn_back = self.query_one("#btn-back", Button)

        if self._is_loading:
            return

        ready_count = len(self._ready_stations)
        total_count = len(self._stations)

        if self._exported_file:
            progress_bar.display = False
            title_widget.update("🎉  [b green]Export Successful![/]")
            file_size_kb = (
                self._exported_file.stat().st_size / 1024 if self._exported_file.exists() else 0.0
            )
            summary_widget.update(
                f"[b]{ready_count:,}[/] stations successfully written to:\n\n"
                f"[b $accent]{self._exported_file}[/]\n\n"
                f"[dim]File size: {file_size_kb:,.1f} KB[/dim]"
            )
            guardrail_widget.update(
                "[dim]Compatible with PostgreSQL (>= 9.5) and SQLite (>= 3.24.0)[/dim]"
            )
            btn_export.display = False
            btn_back.disabled = False
            btn_back.label = "Done"
            btn_back.variant = "primary"
            return

        progress_bar.display = False
        title_widget.update("💾  [b]Export Ready Stations to SQL[/]")

        summary_widget.update(
            f"[dim]{'Ready to Export:':<20}[/dim] [b green]{ready_count:,}[/] / "
            f"{total_count:,} stations\n"
            f"[dim]{'Output Directory:':<20}[/dim] [b]{self._output_dir}[/]\n"
            f"[dim]{'Output Filename:':<20}[/dim]  [b]{self._target_filename}[/]\n\n"
            "[dim]Format: INSERT ... ON CONFLICT (id) DO UPDATE SET (bulk transaction)[/dim]"
        )

        if ready_count == 0:
            guardrail_widget.update(
                "⚠️  [b yellow]No stations are currently marked as 'ready'.[/]\n"
                "[dim]Only stations with status='ready' are included in exports.\n"
                "Review or update station records to status='ready' to export them.[/dim]"
            )
            btn_export.disabled = True
            btn_export.tooltip = "Cannot export: 0 stations with status='ready'"
        else:
            guardrail_widget.update(
                f"[green]Ready to generate SQL with {ready_count:,} upsert statements.[/]"
            )
            btn_export.disabled = False
            btn_export.tooltip = None

    def action_export(self) -> None:
        if not self._ready_stations or self._exported_file or self._is_exporting:
            return

        self._is_exporting = True
        btn_export = self.query_one("#btn-export", Button)
        btn_back = self.query_one("#btn-back", Button)
        progress_bar = self.query_one("#export-progress", ProgressBar)
        guardrail_widget = self.query_one("#export-guardrail", Static)

        btn_export.disabled = True
        btn_back.disabled = True
        guardrail_widget.update("[dim]Generating SQL upsert statements...[/dim]")
        progress_bar.display = True
        progress_bar.update(total=len(self._ready_stations), progress=0)

        self._run_export_worker()

    @work(thread=True)
    def _run_export_worker(self) -> None:
        def on_progress(current: int, total: int) -> None:
            self.app.call_from_thread(self._update_progress, current, total)

        try:
            out_path, count = export_ready_stations_sql(
                self._ready_stations,
                output_dir=self._output_dir,
                filename=self._target_filename,
                progress_callback=on_progress,
            )
            self.app.call_from_thread(self._on_export_success, out_path, count)
        except (OSError, ValueError) as exc:
            self.app.call_from_thread(self._on_export_failure, str(exc))

    def _update_progress(self, current: int, total: int) -> None:
        progress_bar = self.query_one("#export-progress", ProgressBar)
        progress_bar.update(total=total, progress=current)

    def _on_export_success(self, out_path: Path, count: int) -> None:
        self._is_exporting = False
        self._exported_file = out_path
        self.notify(
            f"Exported {count:,} stations to {out_path.name}",
            title="Export complete",
            severity="information",
        )
        self._refresh_view()

    def _on_export_failure(self, error_message: str) -> None:
        self._is_exporting = False
        btn_export = self.query_one("#btn-export", Button)
        btn_back = self.query_one("#btn-back", Button)
        progress_bar = self.query_one("#export-progress", ProgressBar)
        progress_bar.display = False
        btn_export.disabled = False
        btn_back.disabled = False
        self.notify(error_message, title="Export failed", severity="error")
        self._refresh_view()

    @on(Button.Pressed, "#btn-export")
    def on_export_pressed(self) -> None:
        self.action_export()

    @on(Button.Pressed, "#btn-back")
    def on_back_pressed(self) -> None:
        self.app.pop_screen()
