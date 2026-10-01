"""App color themes."""

from textual.theme import Theme

GRUVBOX_DARK = Theme(
    name="gruvbox-dark",
    primary="#FABD2F",
    secondary="#8EC07C",
    accent="#FE8019",
    foreground="#EBDBB4",
    background="#282828",
    surface="#3C3836",
    panel="#504945",
    success="#B8BB26",
    warning="#FABD2F",
    error="#FB4934",
    dark=True,
)

GRUVBOX_LIGHT = Theme(
    name="gruvbox-light",
    primary="#B57614",
    secondary="#427B58",
    accent="#AF3A03",
    foreground="#3C3836",
    background="#FBF1C7",
    surface="#F2E5BC",
    panel="#EBDBB2",
    success="#79740E",
    warning="#B57614",
    error="#9D0006",
    dark=False,
)
