"""Antenna color themes: warm amber dial on a deep night-blue receiver."""

from textual.theme import Theme

ANTENNA_DARK = Theme(
    name="antenna-dark",
    primary="#FFB000",
    secondary="#2EC4B6",
    accent="#FF6B5B",
    foreground="#E8E4D9",
    background="#0D1117",
    surface="#151B24",
    panel="#1C2430",
    success="#7BD389",
    warning="#FFB000",
    error="#FF5A5F",
    dark=True,
)

ANTENNA_LIGHT = Theme(
    name="antenna-light",
    primary="#B86E00",
    secondary="#128C82",
    accent="#D8483A",
    foreground="#2A2622",
    background="#F6F1E7",
    surface="#FFFBF3",
    panel="#EDE4D3",
    success="#2E8B57",
    warning="#B86E00",
    error="#C0392B",
    dark=False,
)
