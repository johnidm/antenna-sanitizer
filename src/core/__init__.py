"""Domain logic. Must not import from the TUI layer."""

from src.core.sanitizer import Rule, Sanitizer, SanitizeResult

__all__ = ["Rule", "SanitizeResult", "Sanitizer"]
