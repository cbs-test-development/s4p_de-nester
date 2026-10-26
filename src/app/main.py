"""Service entrypoint.

Run it with::

    PYTHONPATH=src python -m app.main          # bash
    $env:PYTHONPATH="src"; python -m app.main  # PowerShell

This opens the S4P De-nester window (:mod:`app.denest.gui`). Keep this module
thin: wiring belongs here, logic belongs in a feature package under
``src/app/``.
"""

from __future__ import annotations

import logging
from collections.abc import Callable

from app.config import Settings, load_settings

logger = logging.getLogger(__name__)


def configure_logging(level: str) -> None:
    """Configure root logging. Call once, at startup, before anything logs."""
    logging.basicConfig(
        level=level.upper(),
        format="%(asctime)s %(levelname)-8s %(name)s %(message)s",
    )


def _launch_gui() -> None:
    # Imported here so importing app.main never needs Tk.
    from app.denest.gui import launch

    launch()


def run(settings: Settings | None = None, launch: Callable[[], None] = _launch_gui) -> int:
    """Run the service and return its process exit code.

    Args:
        settings: Configuration to use. Loaded from the environment when
            omitted; pass an explicit value in tests.
        launch: Starts the user interface and blocks until it closes. Defaults
            to the Tkinter window; tests pass a stand-in.
    """
    if settings is None:
        settings = load_settings()

    configure_logging(settings.log_level)
    logger.info("starting %s (env=%s)", settings.app_name, settings.app_env)

    launch()

    return 0


if __name__ == "__main__":
    raise SystemExit(run())
