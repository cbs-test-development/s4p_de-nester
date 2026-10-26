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


@pytest.fixture
def launches() -> list[None]:
    """A record of calls to a stand-in for the GUI launcher, which needs a display."""
    return []


def test_run_with_explicit_settings_returns_zero(
    basic_config_calls: list[dict[str, object]], launches: list[None]
) -> None:
    settings = Settings(app_name="test-service", app_env="test", log_level="DEBUG")

    assert run(settings, launch=lambda: launches.append(None)) == 0
    assert basic_config_calls[0]["level"] == "DEBUG"


def test_run_launches_the_interface_once(
    basic_config_calls: list[dict[str, object]], launches: list[None]
) -> None:
    settings = Settings(app_name="test-service", app_env="test", log_level="INFO")

    run(settings, launch=lambda: launches.append(None))

    assert launches == [None]


def test_run_launches_the_tkinter_window_by_default(
    monkeypatch: pytest.MonkeyPatch,
    basic_config_calls: list[dict[str, object]],
    launches: list[None],
) -> None:
    pytest.importorskip("tkinter")
    import app.denest.gui

    # Replace the window itself: opening it needs a display and blocks.
    monkeypatch.setattr(app.denest.gui, "launch", lambda: launches.append(None))
    settings = Settings(app_name="test-service", app_env="test", log_level="INFO")

    run(settings)

    assert launches == [None]


def test_run_without_settings_loads_them_from_the_environment(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    basic_config_calls: list[dict[str, object]],
    launches: list[None],
) -> None:
    # An empty working directory means no stray .env is picked up.
    monkeypatch.chdir(tmp_path)
    for name in ("APP_NAME", "APP_ENV", "LOG_LEVEL"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("LOG_LEVEL", "warning")

    assert run(launch=lambda: launches.append(None)) == 0
    assert basic_config_calls[0]["level"] == "WARNING"


def test_configure_logging_passes_uppercased_level(
    basic_config_calls: list[dict[str, object]],
) -> None:
    configure_logging("debug")

    assert len(basic_config_calls) == 1
    assert basic_config_calls[0]["level"] == "DEBUG"
