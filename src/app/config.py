"""Configuration loading.

Settings come from the process environment, with a local ``.env`` file filling
in anything the environment does not already define. Real environment variables
always win, so a deployed service is never affected by a stray ``.env``.

To add a setting: add a field to :class:`Settings`, read it in
:func:`load_settings`, and document it in ``.env.example``.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

DEFAULT_ENV_FILE = Path(".env")

DEFAULT_APP_NAME = "s4p-de-nester"
DEFAULT_APP_ENV = "local"
DEFAULT_LOG_LEVEL = "INFO"


class MissingSettingError(RuntimeError):
    """Raised when a required environment variable is missing or empty."""

    def __init__(self, name: str) -> None:
        super().__init__(
            f"Required environment variable {name!r} is not set. "
            f"See .env.example for the variables this service reads."
        )
        self.name = name


@dataclass(frozen=True, slots=True)
class Settings:
    """An immutable snapshot of the service's configuration."""

    app_name: str
    app_env: str
    log_level: str


def required(name: str) -> str:
    """Return the value of ``name``.

    Raises:
        MissingSettingError: if the variable is unset or empty.
    """
    value = os.environ.get(name, "").strip()
    if not value:
        raise MissingSettingError(name)
    return value


def optional(name: str, default: str) -> str:
    """Return the value of ``name``, or ``default`` if it is unset or empty."""
    return os.environ.get(name, "").strip() or default


def load_settings(env_file: Path | None = DEFAULT_ENV_FILE) -> Settings:
    """Build :class:`Settings` from the environment.

    Args:
        env_file: ``.env`` file to load before reading the environment. Pass
            ``None`` to read the environment only - tests do this to stay
            independent of whatever ``.env`` a developer has locally.
    """
    if env_file is not None:
        load_dotenv(env_file, override=False)

    return Settings(
        app_name=optional("APP_NAME", DEFAULT_APP_NAME),
        app_env=optional("APP_ENV", DEFAULT_APP_ENV),
        log_level=optional("LOG_LEVEL", DEFAULT_LOG_LEVEL),
    )
