"""Built-in rules. Add new ones here (or in a submodule) and register them."""

from dataclasses import dataclass

from src.core.sanitizer import Rule


@dataclass(frozen=True, slots=True)
class StripWhitespace:
    name: str = "strip-whitespace"

    def apply(self, value: str) -> str:
        return value.strip()


@dataclass(frozen=True, slots=True)
class CollapseWhitespace:
    name: str = "collapse-whitespace"

    def apply(self, value: str) -> str:
        return " ".join(value.split())


def default_rules() -> list[Rule]:
    return [StripWhitespace(), CollapseWhitespace()]
