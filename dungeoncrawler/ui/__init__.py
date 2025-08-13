"""User interface utilities for terminal based front ends.

The project ships with two separate implementations of a user interface.  The
light‑weight :mod:`terminal` renderer is used throughout the test-suite and has
no third party dependencies.  A richer interface implemented with the optional
`textual <https://textual.textualize.io/>`_ framework is also provided, but the
library is not required for the core game logic or for running the tests.

Importing :mod:`dungeoncrawler.ui` should therefore not fail when ``textual`` is
missing.  We attempt to import the graphical ``DungeonApp`` but fall back to a
small placeholder that simply raises a :class:`ModuleNotFoundError` when used.
This mirrors the approach taken for other optional dependencies in the code
base and keeps the public API stable regardless of the environment.
"""

from .terminal import Renderer

try:  # pragma: no cover - exercised indirectly in tests when textual is absent
    from .textual_app import DungeonApp
except ModuleNotFoundError:  # pragma: no cover - textual not installed

    class DungeonApp:  # type: ignore[no-redef]
        """Placeholder for the optional textual based application.

        ``DungeonApp`` relies on the third party :mod:`textual` package.  When
        that dependency is not available importing :mod:`dungeoncrawler.ui`
        would otherwise raise ``ModuleNotFoundError`` which breaks consumers that
        only need the terminal renderer.  This stand‑in preserves the attribute
        while providing a clear error if instantiation is attempted.
        """

        def __init__(self, *args, **kwargs) -> None:  # pragma: no cover - simple guard
            raise ModuleNotFoundError("`textual` is required to use DungeonApp")


__all__ = ["Renderer", "DungeonApp"]
