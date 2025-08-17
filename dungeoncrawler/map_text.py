"""Utility functions returning static map-related text."""

from gettext import gettext as _


def get_legend_text() -> str:
    """Return the map legend text shown with the in-game map."""

    return "\n".join(
        [
            _("Legend:"),
            _(" @ - You"),
            _(" E - Exit"),
            _(" . - Floor"),
            _(" · - Discovered"),
            _("   - Unexplored"),
        ]
    )


__all__ = ["get_legend_text"]
