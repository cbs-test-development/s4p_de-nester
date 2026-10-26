"""Reading the leg map CSV and writing its filtered copy.

The leg map is a CSV with at least the columns in :data:`REQUIRED_COLUMNS`.
Each row describes one leg, keyed by its serial number (``LegSn``).
"""

from __future__ import annotations

import csv
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

SERIAL_COLUMN = "LegSn"
LEG_LOCATION_COLUMN = "LegLocation"
ARRAY_LOCATION_COLUMN = "ArrayLocation"
REQUIRED_COLUMNS = (SERIAL_COLUMN, LEG_LOCATION_COLUMN, ARRAY_LOCATION_COLUMN)

FILE_NAME_COLUMN = "File Name"

# utf-8-sig reads files with or without a BOM, and writes one so Excel opens
# the output with the right encoding.
CSV_ENCODING = "utf-8-sig"

Row = dict[str, str]


@dataclass(frozen=True, slots=True)
class LegMap:
    """A loaded leg map: its header, in order, and its data rows."""

    fieldnames: list[str]
    rows: list[Row]


def load_legmap(path: Path) -> LegMap:
    """Read the leg map at ``path``.

    Rows with an empty ``LegSn`` are skipped, and serials are stripped of
    surrounding whitespace. Missing cells read as ``""``; cells beyond the
    header are dropped.

    Raises:
        ValueError: if the file has no header, lacks a required column, or has
            no data rows.
    """
    with path.open(newline="", encoding=CSV_ENCODING) as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError(f"{path.name} has no header row.")
        fieldnames = list(reader.fieldnames)
        missing = [column for column in REQUIRED_COLUMNS if column not in fieldnames]
        if missing:
            raise ValueError(f"{path.name} is missing column(s): {', '.join(missing)}")
        rows: list[Row] = []
        for raw in reader:
            row = {name: raw.get(name) or "" for name in fieldnames}
            row[SERIAL_COLUMN] = row[SERIAL_COLUMN].strip()
            if row[SERIAL_COLUMN]:
                rows.append(row)
    if not rows:
        raise ValueError(f"{path.name} has no data rows.")
    return LegMap(fieldnames=fieldnames, rows=rows)


def index_by_serial(rows: Iterable[Row]) -> tuple[dict[str, Row], list[str]]:
    """Index rows by serial, keeping the first row for each serial.

    Returns the index and the serials that appeared more than once, once per
    extra occurrence, in file order.
    """
    index: dict[str, Row] = {}
    duplicates: list[str] = []
    for row in rows:
        serial = row[SERIAL_COLUMN]
        if serial in index:
            duplicates.append(serial)
        else:
            index[serial] = row
    return index, duplicates


def write_filtered_legmap(
    path: Path, fieldnames: list[str], records: Iterable[tuple[Row, str]]
) -> None:
    """Write a leg map with one row per ``(row, file name)`` pair.

    The output keeps the original columns in order and adds ``File Name`` as
    the last column. An existing ``File Name`` column is moved to the end and
    overwritten.
    """
    output_fields = [name for name in fieldnames if name != FILE_NAME_COLUMN]
    output_fields.append(FILE_NAME_COLUMN)
    with path.open("w", newline="", encoding=CSV_ENCODING) as handle:
        writer = csv.DictWriter(handle, fieldnames=output_fields, extrasaction="ignore")
        writer.writeheader()
        for row, file_name in records:
            writer.writerow({**row, FILE_NAME_COLUMN: file_name})
