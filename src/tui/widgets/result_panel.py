"""Displays a ``SanitizeResult``."""

from textual.reactive import reactive
from textual.widgets import Static

from src.core.sanitizer import SanitizeResult


class ResultPanel(Static):
    result: reactive[SanitizeResult | None] = reactive(None)

    def watch_result(self, result: SanitizeResult | None) -> None:
        if result is None:
            self.update("[dim]No input yet.[/dim]")
            return
        rules = ", ".join(result.applied) or "none"
        self.update(f"[b]Sanitized:[/b] {result.sanitized!r}\n[b]Rules applied:[/b] {rules}")
