"""Tests for :mod:`app.config`.

These also demonstrate the repo's test conventions:

* ``tests/`` mirrors ``src/app/`` one-to-one - ``app/config.py`` is tested by
  ``tests/test_config.py``.
* Tests are annotated (``-> None``) because mypy runs in strict mode over
  ``tests/`` as well as ``src/``.
* Environment state is changed through ``monkeypatch``, never directly, so
  tests cannot leak into one another.
* ``env_file=None`` keeps a test independent of whatever ``.env`` happens to
  exist on the machine running it.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from app.config import (
    DEFAULT_APP_ENV,
    DEFAULT_APP_NAME,
    DEFAULT_LOG_LEVEL,
    MissingSettingError,
    load_settings,
    required,
)

SETTING_NAMES = ("APP_NAME", "APP_ENV", "LOG_LEVEL")


@pytest.fixture
def clean_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Unset every setting, and remove anything a test's ``.env`` adds.

    ``load_dotenv`` writes straight into ``os.environ``, and ``delenv`` does not
    record a variable that was already absent, so it would not be cleaned up.
    Setting it first makes monkeypatch remember it and delete it on teardown.
    """
    for name in SETTING_NAMES:
        monkeypatch.setenv(name, "placeholder")
        monkeypatch.delenv(name)


@pytest.mark.usefixtures("clean_env")
def test_load_settings_applies_defaults() -> None:
    settings = load_settings(env_file=None)

    assert settings.app_name == DEFAULT_APP_NAME
    assert settings.app_env == DEFAULT_APP_ENV
    assert settings.log_level == DEFAULT_LOG_LEVEL


@pytest.mark.usefixtures("clean_env")
def test_load_settings_reads_env_file(tmp_path: Path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("APP_NAME=from-file\nLOG_LEVEL=DEBUG\n", encoding="utf-8")

    settings = load_settings(env_file=env_file)

    assert settings.app_name == "from-file"
    assert settings.log_level == "DEBUG"
    assert settings.app_env == DEFAULT_APP_ENV


@pytest.mark.usefixtures("clean_env")
def test_real_environment_wins_over_env_file(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("APP_NAME=from-file\n", encoding="utf-8")
    monkeypatch.setenv("APP_NAME", "from-environment")

    settings = load_settings(env_file=env_file)

    assert settings.app_name == "from-environment"


def test_required_returns_stripped_value(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SOME_SETTING", "  value  ")

    assert required("SOME_SETTING") == "value"


@pytest.mark.parametrize("value", [None, "", "   "], ids=["unset", "empty", "whitespace"])
def test_required_raises_when_missing(monkeypatch: pytest.MonkeyPatch, value: str | None) -> None:
    if value is None:
        monkeypatch.delenv("SOME_SETTING", raising=False)
    else:
        monkeypatch.setenv("SOME_SETTING", value)

    with pytest.raises(MissingSettingError) as excinfo:
        required("SOME_SETTING")

    assert excinfo.value.name == "SOME_SETTING"
