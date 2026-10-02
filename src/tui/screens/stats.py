"""Screen that displays dataset metrics, status counts, and export readiness."""

from __future__ import annotations

from typing import ClassVar

from textual import events
from textual.app import ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import Grid, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import Footer, Header, Static

from src.core.stations import Station, StationStats, compute_stats, load_stations

NARROW_WIDTH = 110
VERY_NARROW_WIDTH = 70


class StatCard(Vertical):
    """Card widget displaying a single key metric."""

    DEFAULT_CSS = """
    StatCard {
        height: auto;
        min-height: 7;
        border: round $primary 60%;
        border-title-color: $primary;
        border-title-style: bold;
        background: $panel;
        padding: 1 2;
        align: center middle;

        &:hover {
            border: round $accent;
            border-title-color: $accent;
        }
    }

    StatCard .stat-value {
        text-align: center;
        text-style: bold;
        margin-bottom: 1;
    }

    StatCard .stat-subtitle {
        text-align: center;
        color: $text-muted;
    }
    """

    def __init__(self, title: str, value_markup: str, subtitle: str) -> None:
        super().__init__()
        self.border_title = title
        self._value_markup = value_markup
        self._subtitle = subtitle

    def compose(self) -> ComposeResult:
        yield Static(self._value_markup, classes="stat-value")
        yield Static(self._subtitle, classes="stat-subtitle")


class StatsScreen(Screen[None]):
    """Station dataset statistics and export readiness screen."""

    TITLE = "Statistics"
    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("escape", "app.pop_screen", "Back"),
        Binding("r", "refresh", "Refresh"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._stations: list[Station] | None = None

    def compose(self) -> ComposeResult:
        yield Header(icon="📡")
        with VerticalScroll(id="body"):
            yield Static(id="stats-heading")
            yield Grid(id="stats-grid")
            yield Vertical(id="stats-breakdown", classes="card")
        yield Footer()

    def on_mount(self) -> None:
        self.action_refresh()

    def on_resize(self, event: events.Resize) -> None:
        grid = self.query_one("#stats-grid", Grid)
        grid.set_class(event.size.width < NARROW_WIDTH, "-narrow")
        grid.set_class(event.size.width < VERY_NARROW_WIDTH, "-very-narrow")

    def action_refresh(self) -> None:
        try:
            self._stations = load_stations()
            stats = compute_stats(self._stations)
        except (OSError, ValueError) as exc:
            self.notify(str(exc), title="Failed to load statistics", severity="error")
            self.app.pop_screen()
            return

        self._update_display(stats)

    def _update_display(self, stats: StationStats) -> None:
        heading = self.query_one("#stats-heading", Static)
        heading.update(
            "📊  [b]Station Statistics & Export Readiness[/b]  "
            f"[dim]— {stats.total:,} total records  (press [b]r[/b] to refresh)[/dim]"
        )

        grid = self.query_one("#stats-grid", Grid)
        grid.remove_children()

        grid.mount_all(
            [
                StatCard(
                    title="Total Stations",
                    value_markup=f"[b $primary]{stats.total:,}[/]",
                    subtitle="Records in dataset",
                ),
                StatCard(
                    title="⏳ Pending Review",
                    value_markup=(
                        f"[b $warning]{stats.pending:,}[/] [dim]({stats.pending_pct:.1f}%)[/]"
                    ),
                    subtitle="Awaiting verification",
                ),
                StatCard(
                    title="✅ Ready to Export",
                    value_markup=(
                        f"[b $success]{stats.ready:,}[/] [dim]({stats.ready_pct:.1f}%)[/]"
                    ),
                    subtitle="Approved for export",
                ),
                StatCard(
                    title="❌ Rejected",
                    value_markup=(
                        f"[b $error]{stats.rejected:,}[/] [dim]({stats.rejected_pct:.1f}%)[/]"
                    ),
                    subtitle="Excluded from export",
                ),
            ]
        )

        breakdown = self.query_one("#stats-breakdown", Vertical)
        breakdown.border_title = "Dataset Health & Coverage"
        breakdown.remove_children()

        stream_pct = (stats.with_stream / stats.total * 100) if stats.total else 0.0
        hp_pct = (stats.with_homepage / stats.total * 100) if stats.total else 0.0

        bar_width = 30
        ready_blocks = round((stats.ready / stats.total) * bar_width) if stats.total else 0
        pending_blocks = round((stats.pending / stats.total) * bar_width) if stats.total else 0
        rejected_blocks = max(bar_width - ready_blocks - pending_blocks, 0)

        bar_markup = (
            f"[green]{'█' * ready_blocks}[/]"
            f"[yellow]{'█' * pending_blocks}[/]"
            f"[red]{'█' * rejected_blocks}[/]"
        )

        breakdown_text = (
            f"[b]Readiness Pipeline:[/b]  {bar_markup}  "
            f"[green]{stats.ready:,} ready[/]  •  "
            f"[yellow]{stats.pending:,} pending[/]  •  "
            f"[red]{stats.rejected:,} rejected[/]\n\n"
            f"[dim]{'Active Streams:':<20}[/dim] [b]{stats.with_stream:,}[/] / "
            f"{stats.total:,} [dim]({stream_pct:.1f}%)[/dim]\n"
            f"[dim]{'Homepages Available:':<20}[/dim] [b]{stats.with_homepage:,}[/] / "
            f"{stats.total:,} [dim]({hp_pct:.1f}%)[/dim]\n"
            f"[dim]{'Countries Covered:':<20}[/dim] [b]{stats.countries_count:,}[/] "
            "unique countries"
        )
        breakdown.mount(Static(breakdown_text))
