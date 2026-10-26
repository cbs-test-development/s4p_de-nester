"""Service entrypoint.

Run it with::

    PYTHONPATH=src python -m app.main          # bash
    $env:PYTHONPATH="src"; python -m app.main  # PowerShell

This is the one documented way in. :func:`run` is the seam to replace with the
service's actual work - start a web server, consume a queue, run a job. Keep
this module thin: wiring belongs here, logic belongs in a feature package under
``src/app/``.
"""

from __future__ import annotations

import logging

from app.config import Settings, load_settings

logger = logging.getLogger(__name__)


def configure_logging(level: str) -> None:
    """Configure root logging. Call once, at startup, before anything logs."""
    logging.basicConfig(
        level=level.upper(),
        format="%(asctime)s %(levelname)-8s %(name)s %(message)s",
    )


def run(settings: Settings | None = None) -> int:
    """Run the service and return its process exit code.

    Args:
        settings: Configuration to use. Loaded from the environment when
            omitted; pass an explicit value in tests.
    """
    if settings is None:
        settings = load_settings()

    configure_logging(settings.log_level)
    logger.info("starting %s (env=%s)", settings.app_name, settings.app_env)

    # Replace this with the service's real work.
    logger.warning("run() is a stub - implement it in src/app/main.py")

    return 0


if __name__ == "__main__":
    raise SystemExit(run())
