"""Tests for :mod:`app.denest.legmap`."""

from __future__ import annotations

import csv
from pathlib import Path

import pytest

from app.denest.legmap import index_by_serial, load_legmap, write_filtered_legmap

HEADER = "LegSn,LegLocation,ArrayLocation,Notes\n"


def write_csv(path: Path, text: str, encoding: str = "utf-8") -> Path:
    path.write_text(text, encoding=encoding)
    return path


def read_csv(path: Path) -> list[list[str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.reader(handle))


def test_load_legmap_reads_header_and_rows(tmp_path: Path) -> None:
    path = write_csv(tmp_path / "map.csv", HEADER + 'SN1,1,"Sw 1, GPU",first\n')

    legmap = load_legmap(path)

    assert legmap.fieldnames == ["LegSn", "LegLocation", "ArrayLocation", "Notes"]
    assert legmap.rows == [
        {"LegSn": "SN1", "LegLocation": "1", "ArrayLocation": "Sw 1, GPU", "Notes": "first"}
    ]


def test_load_legmap_accepts_a_byte_order_mark(tmp_path: Path) -> None:
    path = write_csv(tmp_path / "map.csv", HEADER + "SN1,1,Sw,\n", encoding="utf-8-sig")

    assert load_legmap(path).fieldnames[0] == "LegSn"


def test_load_legmap_strips_serials_and_skips_blank_ones(tmp_path: Path) -> None:
    path = write_csv(tmp_path / "map.csv", HEADER + " SN1 ,1,Sw,\n  ,2,Sw,\n,3,Sw,\n")

    rows = load_legmap(path).rows

    assert [row["LegSn"] for row in rows] == ["SN1"]


def test_load_legmap_fills_short_rows_and_drops_extra_cells(tmp_path: Path) -> None:
    path = write_csv(tmp_path / "map.csv", HEADER + "SN1,1\nSN2,2,Sw,n,extra\n")

    rows = load_legmap(path).rows

    assert rows[0] == {"LegSn": "SN1", "LegLocation": "1", "ArrayLocation": "", "Notes": ""}
    assert rows[1] == {"LegSn": "SN2", "LegLocation": "2", "ArrayLocation": "Sw", "Notes": "n"}


def test_load_legmap_rejects_an_empty_file(tmp_path: Path) -> None:
    path = write_csv(tmp_path / "map.csv", "")

    with pytest.raises(ValueError, match="no header row"):
        load_legmap(path)


def test_load_legmap_names_missing_columns(tmp_path: Path) -> None:
    path = write_csv(tmp_path / "map.csv", "LegSn,Other\nSN1,x\n")

    with pytest.raises(ValueError, match="missing column\\(s\\): LegLocation, ArrayLocation"):
        load_legmap(path)


def test_load_legmap_rejects_a_file_with_no_usable_rows(tmp_path: Path) -> None:
    path = write_csv(tmp_path / "map.csv", HEADER + ",1,Sw,\n")

    with pytest.raises(ValueError, match="no data rows"):
        load_legmap(path)


def test_index_by_serial_keeps_the_first_row_and_reports_repeats() -> None:
    rows = [
        {"LegSn": "A", "LegLocation": "1"},
        {"LegSn": "B", "LegLocation": "2"},
        {"LegSn": "A", "LegLocation": "3"},
        {"LegSn": "A", "LegLocation": "4"},
    ]

    index, duplicates = index_by_serial(rows)

    assert list(index) == ["A", "B"]
    assert index["A"]["LegLocation"] == "1"
    assert duplicates == ["A", "A"]


def test_write_filtered_legmap_appends_file_name_column(tmp_path: Path) -> None:
    path = tmp_path / "out.csv"
    row = {"LegSn": "A", "LegLocation": "1", "ArrayLocation": "Sw, GPU"}

    write_filtered_legmap(
        path, ["LegSn", "LegLocation", "ArrayLocation"], [(row, "one.s4p"), (row, "two.s4p")]
    )

    assert read_csv(path) == [
        ["LegSn", "LegLocation", "ArrayLocation", "File Name"],
        ["A", "1", "Sw, GPU", "one.s4p"],
        ["A", "1", "Sw, GPU", "two.s4p"],
    ]


def test_write_filtered_legmap_moves_and_overwrites_an_existing_file_name(
    tmp_path: Path,
) -> None:
    path = tmp_path / "out.csv"
    row = {"File Name": "old", "LegSn": "A"}

    write_filtered_legmap(path, ["File Name", "LegSn"], [(row, "new.s4p")])

    assert read_csv(path) == [["LegSn", "File Name"], ["A", "new.s4p"]]


def test_write_filtered_legmap_writes_a_byte_order_mark(tmp_path: Path) -> None:
    path = tmp_path / "out.csv"

    write_filtered_legmap(path, ["LegSn"], [])

    assert path.read_bytes().startswith(b"\xef\xbb\xbf")
