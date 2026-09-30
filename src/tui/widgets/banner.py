"""Wordmark banner shown on the main menu."""

from textual.widgets import Static

_WORDMARK = """\
[b $primary]▄▀█ █▄ █ ▀█▀ █▀▀ █▄ █ █▄ █ ▄▀█[/]
[b $primary]█▀█ █ ▀█  █  ██▄ █ ▀█ █ ▀█ █▀█[/]
[$secondary]▂ ▃ ▄ ▅ ▆ ▇ █[/]  [dim]s a n i t i z e r[/]  [$secondary]█ ▇ ▆ ▅ ▄ ▃ ▂[/]"""


class Banner(Static):
    """ASCII wordmark with signal bars."""

    DEFAULT_CSS = """
    Banner {
        width: 60;
        height: auto;
        text-align: center;
        margin-bottom: 1;
    }
    """

    def __init__(self) -> None:
        super().__init__(_WORDMARK)
