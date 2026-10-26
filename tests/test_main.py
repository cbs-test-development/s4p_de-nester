"""Tests for :mod:`app.main`."""

from __future__ import annotations

import logging
from pathlib import Path

import pytest

from app.config import Settings
from app.main import configure_logging, run


@pytest.fixture
def basic_config_calls(monkeypatch: pytest.MonkeyPatch) -> list[dict[str, object]]:
    """Replace ``logging.basicConfig`` with a recorder and return its calls.

    The real one changes the root logger for the rest of the session - global
    state no test should leave behind. It is also a no-op under pytest, whose log
    capture already attaches a handler to the root logger, so asserting on the
    root logger's level would prove nothing.
    """
    calls: list[dict[str, object]] = []
    monkeypatch.setattr(logging, "basicConfig", lambda **kwargs: calls.append(kwargs))
    return calls


def test_run_with_explicit_settings_returns_zero(
    basic_config_calls: list[dict[str, object]],
) -> None:
    settings = Settings(app_name="test-service", app_env="test", log_level="DEBUG")

    assert run(settings) == 0
    assert basic_config_calls[0]["level"] == "DEBUG"


def test_run_without_settings_loads_them_from_the_environment(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    basic_config_calls: list[dict[str, object]],
) -> None:
    # An empty working directory means no stray .env is picked up.
    monkeypatch.chdir(tmp_path)
    for name in ("APP_NAME", "APP_ENV", "LOG_LEVEL"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("LOG_LEVEL", "warning")

    assert run() == 0
    assert basic_config_calls[0]["level"] == "WARNING"


def test_configure_logging_passes_uppercased_level(
    basic_config_calls: list[dict[str, object]],
) -> None:
    configure_logging("debug")

    assert len(basic_config_calls) == 1
    assert basic_config_calls[0]["level"] == "DEBUG"
