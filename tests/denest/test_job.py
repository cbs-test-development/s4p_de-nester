"""Tests for :mod:`app.denest.job`."""

from __future__ import annotations

import csv
import logging
from pathlib import Path

import pytest

from app.denest.job import JobSummary, plan_copies, run_job

LEGMAP = (
    "LegSn,LegLocation,ArrayLocation\n"
    'SN2,2,"Switch 2, GPU"\n'
    'SN1,1,"Switch 1, GPU"\n'
    'SN1,9,"Duplicate, GPU"\n'
    'SN3,3,"Switch 3, GPU"\n'
)


def touch(path: Path, content: bytes = b"") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    return path


@pytest.fixture
def workspace(tmp_path: Path) -> tuple[Path, Path, Path]:
    """A leg map, a nested S4P tree, and an output folder inside the tree."""
    legmap = tmp_path / "legmap.csv"
    legmap.write_text(LEGMAP, encoding="utf-8")
    root = tmp_path / "root"
    touch(root / "batch" / "SN1" / "a_PASS.s4p", b"sn1-a")
    touch(root / "batch" / "SN1" / "b_PASS.s4p", b"sn1-b")
    touch(root / "batch" / "SN2_PASS.s4p", b"sn2")
    touch(root / "batch" / "stray.s4p")
    touch(root / "out" / "old_copy.s4p")
    return legmap, root, root / "out"


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def test_plan_copies_orders_by_leg_map_then_path_and_reports_unmatched() -> None:
    index = {
        "SN2": {"LegSn": "SN2", "LegLocation": "2", "ArrayLocation": "Sw 2, GPU"},
        "SN1": {"LegSn": "SN1", "LegLocation": "1", "ArrayLocation": "Sw 1, GPU"},
    }
    sources = [
        Path("SN1") / "b.s4p",
        Path("SN1") / "A.s4p",
        Path("SN2_x.s4p"),
        Path("other.s4p"),
    ]

    planned, unmatched = plan_copies(index, sources)

    assert [(item.serial, item.dest_name) for item in planned] == [
        ("SN2", "Sw_2_Leg_2_SN2_x.s4p"),
        ("SN1", "Sw_1_Leg_1_A.s4p"),
        ("SN1", "Sw_1_Leg_1_b.s4p"),
    ]
    assert planned[1].row is index["SN1"]
    assert unmatched == [Path("other.s4p")]


def test_plan_copies_makes_clashing_names_unique() -> None:
    index = {"SN1": {"LegSn": "SN1", "LegLocation": "1", "ArrayLocation": "Sw, GPU"}}
    sources = [Path("a") / "SN1" / "x.s4p", Path("b") / "SN1" / "x.s4p"]

    planned, _ = plan_copies(index, sources)

    assert [item.dest_name for item in planned] == ["Sw_Leg_1_x.s4p", "Sw_Leg_1_x_2.s4p"]


def test_run_job_copies_renames_and_writes_filtered_map(
    workspace: tuple[Path, Path, Path],
) -> None:
    legmap, root, output = workspace
    messages: list[str] = []

    summary = run_job(legmap, root, output, messages.append)

    assert summary == JobSummary(
        copied=3, unmatched=1, serials=2, filtered_path=output / "legmap_filtered.csv"
    )
    assert (output / "Switch_2_Leg_2_SN2_PASS.s4p").read_bytes() == b"sn2"
    assert (output / "Switch_1_Leg_1_a_PASS.s4p").read_bytes() == b"sn1-a"
    assert (output / "Switch_1_Leg_1_b_PASS.s4p").read_bytes() == b"sn1-b"
    assert read_rows(summary.filtered_path) == [
        {
            "LegSn": "SN2",
            "LegLocation": "2",
            "ArrayLocation": "Switch 2, GPU",
            "File Name": "Switch_2_Leg_2_SN2_PASS.s4p",
        },
        {
            "LegSn": "SN1",
            "LegLocation": "1",
            "ArrayLocation": "Switch 1, GPU",
            "File Name": "Switch_1_Leg_1_a_PASS.s4p",
        },
        {
            "LegSn": "SN1",
            "LegLocation": "1",
            "ArrayLocation": "Switch 1, GPU",
            "File Name": "Switch_1_Leg_1_b_PASS.s4p",
        },
    ]
    assert "Duplicate serial in leg map, kept the first row: SN1" in messages
    assert f"No leg map serial for {Path('batch') / 'stray.s4p'}" in messages
    assert messages[-1] == "Done. Copied 3 file(s) for 2 serial(s). Unmatched files: 1."


def test_run_job_creates_a_missing_output_folder(
    workspace: tuple[Path, Path, Path], tmp_path: Path
) -> None:
    legmap, root, _ = workspace
    output = tmp_path / "new" / "folder"

    summary = run_job(legmap, root, output, lambda message: None)

    assert summary.filtered_path.is_file()
    # The old copy in root/out is now an ordinary unmatched file.
    assert summary.unmatched == 2


def test_run_job_logs_through_the_module_logger_by_default(
    workspace: tuple[Path, Path, Path], caplog: pytest.LogCaptureFixture
) -> None:
    legmap, root, output = workspace

    with caplog.at_level(logging.INFO, logger="app.denest.job"):
        run_job(legmap, root, output)

    assert any(message.startswith("Done.") for message in caplog.messages)


def test_run_job_rejects_a_missing_legmap(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="Leg map CSV not found"):
        run_job(tmp_path / "missing.csv", tmp_path, tmp_path / "out")


def test_run_job_rejects_a_missing_root(workspace: tuple[Path, Path, Path], tmp_path: Path) -> None:
    legmap, _, output = workspace

    with pytest.raises(ValueError, match="S4P root folder not found"):
        run_job(legmap, tmp_path / "missing", output)


def test_run_job_refuses_to_write_into_the_root(workspace: tuple[Path, Path, Path]) -> None:
    legmap, root, _ = workspace

    with pytest.raises(ValueError, match="not the S4P root folder"):
        run_job(legmap, root, root)


def test_job_summary_describe() -> None:
    summary = JobSummary(copied=2, unmatched=0, serials=1, filtered_path=Path("x.csv"))

    assert summary.describe() == "Copied 2 file(s).\nFiltered leg map:\nx.csv"
