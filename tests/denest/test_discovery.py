"""Tests for :mod:`app.denest.discovery`."""

from __future__ import annotations

from pathlib import Path

from app.denest.discovery import find_s4p_files, is_inside, match_serial


def touch(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"")
    return path


def test_is_inside(tmp_path: Path) -> None:
    assert is_inside(tmp_path / "a" / "b", tmp_path / "a")
    assert is_inside(tmp_path / "a", tmp_path / "a")
    assert not is_inside(tmp_path / "ab", tmp_path / "a")
    assert not is_inside(tmp_path, tmp_path / "a")


def test_find_s4p_files_walks_nested_folders_and_ignores_other_files(tmp_path: Path) -> None:
    root = tmp_path / "root"
    expected = [
        touch(root / "a.s4p"),
        touch(root / "x" / "b.S4P"),
        touch(root / "x" / "y" / "c.s4p"),
    ]
    touch(root / "x" / "notes.txt")
    touch(root / "x" / "d.s4p.bak")

    assert find_s4p_files(root, tmp_path / "out") == sorted(expected)


def test_find_s4p_files_skips_an_output_folder_inside_the_root(tmp_path: Path) -> None:
    root = tmp_path / "root"
    kept = touch(root / "SN1" / "a.s4p")
    touch(root / "out" / "copied.s4p")
    touch(root / "out" / "deeper" / "copied.s4p")

    assert find_s4p_files(root, root / "out") == [kept]


def test_find_s4p_files_still_searches_a_root_inside_the_output_folder(tmp_path: Path) -> None:
    root = tmp_path / "out" / "root"
    kept = touch(root / "SN1" / "a.s4p")

    assert find_s4p_files(root, tmp_path / "out") == [kept]


def test_match_serial_prefers_the_nearest_matching_folder() -> None:
    path = Path("root") / "OUTER" / "INNER" / "OTHER_file.s4p"

    assert match_serial(path, {"OUTER", "INNER", "OTHER"}) == "INNER"


def test_match_serial_falls_back_to_a_filename_prefix() -> None:
    serials = {"SN1"}

    assert match_serial(Path("root") / "misc" / "SN1_PASS.s4p", serials) == "SN1"
    assert match_serial(Path("root") / "SN1.s4p", serials) == "SN1"


def test_match_serial_needs_a_separator_after_the_prefix() -> None:
    assert match_serial(Path("SN10_PASS.s4p"), {"SN1"}) is None


def test_match_serial_picks_the_longest_prefix() -> None:
    assert match_serial(Path("SN1_2_PASS.s4p"), ["SN1", "SN1_2"]) == "SN1_2"
    assert match_serial(Path("SN1_2_PASS.s4p"), ["SN1_2", "SN1"]) == "SN1_2"


def test_match_serial_returns_none_without_a_match() -> None:
    assert match_serial(Path("root") / "misc" / "unknown.s4p", {"SN1"}) is None
