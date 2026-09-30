"""Rule-based sanitization pipeline.

A ``Sanitizer`` runs an ordered sequence of ``Rule`` objects over an input.
New behaviour is added by writing a new rule, not by editing the pipeline.
"""

from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable


@runtime_checkable
class Rule(Protocol):
    """A single, self-contained sanitization step."""

    name: str

    def apply(self, value: str) -> str: ...


@dataclass(frozen=True, slots=True)
class SanitizeResult:
    original: str
    sanitized: str
    applied: tuple[str, ...] = ()

    @property
    def changed(self) -> bool:
        return self.original != self.sanitized


@dataclass(slots=True)
class Sanitizer:
    rules: list[Rule] = field(default_factory=list)

    @classmethod
    def from_rules(cls, rules: Iterable[Rule]) -> Sanitizer:
        return cls(rules=list(rules))

    def sanitize(self, value: str) -> SanitizeResult:
        current = value
        applied: list[str] = []
        for rule in self.rules:
            updated = rule.apply(current)
            if updated != current:
                applied.append(rule.name)
            current = updated
        return SanitizeResult(original=value, sanitized=current, applied=tuple(applied))
