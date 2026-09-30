"""Displays a ``SanitizeResult`` as a before/after comparison with rule chips."""

from collections.abc import Sequence

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.markup import escape
from textual.reactive import reactive
from textual.widgets import Static

from src.core.sanitizer import SanitizeResult

_EMPTY_HINT = "[dim]Start typing above to see the pipeline in action.[/dim]"


def _visible_whitespace(text: str) -> str:
    """Escape ``text`` for markup and render spaces/tabs as dim glyphs."""
    if not text:
        return "[dim italic]empty[/]"
    return (
        escape(text)
        .replace(" ", "[dim $secondary]·[/]")
        .replace("\t", "[dim $secondary]→[/]")
        .replace("\n", "[dim $secondary]↵[/]\n")
    )


def _chars(count: int) -> str:
    return f"{count} char{'s' if count != 1 else ''}"


class ResultPanel(Vertical):
    """Before/after panels plus one chip per rule, highlighting those applied."""

    result: reactive[SanitizeResult | None] = reactive(None)

    DEFAULT_CSS = """
    ResultPanel {
        height: auto;
    }

    ResultPanel .compare {
        height: auto;
    }

    ResultPanel .side {
        width: 1fr;
        height: auto;
        min-height: 5;
    }

    ResultPanel #before {
        margin-right: 1;
    }

    ResultPanel .rules {
        height: auto;
        margin-top: 1;
        padding: 0 1;
    }

    ResultPanel .rules-label {
        width: auto;
        margin-right: 1;
        color: $text-muted;
    }

    ResultPanel .chip {
        width: auto;
        margin-right: 1;
        padding: 0 1;
        color: $text-muted;
        background: $panel;
    }

    ResultPanel .chip.-applied {
        color: $background;
        background: $success;
        text-style: bold;
    }
    """

    def __init__(self, rule_names: Sequence[str], *, id: str | None = None) -> None:
        super().__init__(id=id)
        self.rule_names = list(rule_names)

    def compose(self) -> ComposeResult:
        with Horizontal(classes="compare"):
            yield Static(id="before", classes="card side")
            yield Static(id="after", classes="card side")
        with Horizontal(classes="rules"):
            yield Static("Rules", classes="rules-label")
            for index, name in enumerate(self.rule_names):
                yield Static(f"○ {escape(name)}", id=f"rule-{index}", classes="chip")

    def on_mount(self) -> None:
        self.query_one("#before", Static).border_title = "Before"
        self.query_one("#after", Static).border_title = "After"
        self.watch_result(self.result)

    def watch_result(self, result: SanitizeResult | None) -> None:
        if not self.is_mounted:
            return
        before = self.query_one("#before", Static)
        after = self.query_one("#after", Static)
        applied = set(result.applied) if result else set()

        for index, name in enumerate(self.rule_names):
            chip = self.query_one(f"#rule-{index}", Static)
            is_applied = name in applied
            chip.set_class(is_applied, "-applied")
            chip.update(f"{'✓' if is_applied else '○'} {escape(name)}")

        if result is None:
            before.update(_EMPTY_HINT)
            after.update(_EMPTY_HINT)
            before.border_subtitle = after.border_subtitle = ""
            return

        before.update(_visible_whitespace(result.original))
        after.update(_visible_whitespace(result.sanitized))
        before.border_subtitle = _chars(len(result.original))
        delta = len(result.sanitized) - len(result.original)
        status = (
            f"[$warning]● changed ({delta:+d})[/]" if result.changed else "[$success]✓ clean[/]"
        )
        after.border_subtitle = f"{status} · {_chars(len(result.sanitized))}"
