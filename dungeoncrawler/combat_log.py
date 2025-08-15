from __future__ import annotations

"""Lightweight combat logger for capturing battle events.

The logger stores rendered combat messages in an in-memory buffer with a
configurable maximum size.  It understands core combat events allowing it to
render either concise summaries or more verbose mathematical breakdowns when
:mod:`dungeoncrawler.config` enables ``verbose_combat``.
"""

from dataclasses import dataclass
from typing import List

from .config import config
from .core.events import AttackResolved, Event


@dataclass
class CombatLog:
    """Buffer of combat messages with optional truncation."""

    max_lines: int = 100
    lines: List[str] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:  # pragma: no cover - tiny helper
        if self.lines is None:
            self.lines = []

    # ------------------------------------------------------------------
    # Logging helpers
    # ------------------------------------------------------------------
    def log(self, message: str) -> str:
        """Append ``message`` to the log respecting ``max_lines``."""

        self.lines.append(message)
        if len(self.lines) > self.max_lines:
            self.lines = self.lines[-self.max_lines :]
        return message

    def handle_event(self, event: Event) -> str:
        """Render ``event`` to a message and store it."""

        if isinstance(event, AttackResolved):
            if config.verbose_combat:
                base = max(0, event.attack - event.defense)
                detail = f"{event.attack}-{event.defense}={base}"
                if event.damage != base:
                    detail += f" -> {event.damage}"
                if event.critical:
                    msg = f"{event.attacker} critically hits {event.defender} ({detail})"
                else:
                    msg = f"{event.attacker} hits {event.defender} ({detail})"
                if event.defeated:
                    msg += f" {event.defender} is defeated."
            else:
                msg = event.message
        else:
            msg = event.message
        return self.log(msg)


__all__ = ["CombatLog"]
