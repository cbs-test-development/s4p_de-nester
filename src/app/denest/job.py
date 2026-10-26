"""Planning and running a de-nest job.

A job reads the leg map, finds every S4P file under a root folder, copies the
ones whose serial is in the map into a flat output folder under a new name, and
writes ``<leg map stem>_filtered.csv`` beside them with one row per copied file.
"""

from __future__ import annotations

import logging
import shutil
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path

from app.denest.discovery import find_s4p_files, match_serial
from app.denest.legmap import (
    ARRAY_LOCATION_COLUMN,
    LEG_LOCATION_COLUMN,
    Row,
    index_by_serial,
    load_legmap,
    write_filtered_legmap,
)
from app.denest.naming import new_filename, unique_name

logger = logging.getLogger(__name__)

Log = Callable[[str], None]


@dataclass(frozen=True, slots=True)
class PlannedFile:
    """One S4P file to copy, and the leg map row it belongs to."""

    source: Path
    serial: str
    row: Row
    dest_name: str


@dataclass(frozen=True, slots=True)
class JobSummary:
    """What a finished job did."""

    copied: int
    unmatched: int
    serials: int
    filtered_path: Path

    def describe(self) -> str:
        """Return a short human-readable summary, suitable for a dialog."""
        return f"Copied {self.copied} file(s).\nFiltered leg map:\n{self.filtered_path}"


def plan_copies(
    index: Mapping[str, Row], sources: list[Path]
) -> tuple[list[PlannedFile], list[Path]]:
    """Match ``sources`` to serials and give each match a unique destination name.

    Planned files are ordered by their serial's position in ``index`` (the leg
    map's order, from :func:`app.denest.legmap.index_by_serial`), then by source
    path, so the filtered leg map follows the original. Returns the planned
    files and the sources no serial matched.
    """
    order = {serial: position for position, serial in enumerate(index)}
    matched: list[tuple[int, Path, str]] = []
    unmatched: list[Path] = []
    for source in sources:
        serial = match_serial(source, index)
        if serial is None:
            unmatched.append(source)
        else:
            matched.append((order[serial], source, serial))

    matched.sort(key=lambda item: (item[0], str(item[1]).lower()))
    used: set[str] = set()
    planned: list[PlannedFile] = []
    for _, source, serial in matched:
        row = index[serial]
        name = new_filename(row[ARRAY_LOCATION_COLUMN], row[LEG_LOCATION_COLUMN], source.name)
        planned.append(
            PlannedFile(source=source, serial=serial, row=row, dest_name=unique_name(name, used))
        )
    return planned, unmatched


def run_job(
    legmap_path: Path, s4p_root: Path, output_dir: Path, log: Log = logger.info
) -> JobSummary:
    """Run a whole de-nest job, reporting progress through ``log``.

    Existing files in ``output_dir`` with the same names are overwritten.

    Raises:
        ValueError: if ``legmap_path`` is not a file, ``s4p_root`` is not a
            folder, ``output_dir`` is ``s4p_root``, or the leg map is invalid
            (see :func:`app.denest.legmap.load_legmap`).
    """
    if not legmap_path.is_file():
        raise ValueError(f"Leg map CSV not found: {legmap_path}")
    if not s4p_root.is_dir():
        raise ValueError(f"S4P root folder not found: {s4p_root}")
    if output_dir.resolve() == s4p_root.resolve():
        raise ValueError("Choose an output folder that is not the S4P root folder.")

    legmap = load_legmap(legmap_path)
    index, duplicate_serials = index_by_serial(legmap.rows)
    log(f"Loaded {len(legmap.rows)} leg map rows ({len(index)} serial numbers).")
    for serial in duplicate_serials:
        log(f"Duplicate serial in leg map, kept the first row: {serial}")

    output_dir.mkdir(parents=True, exist_ok=True)
    sources = find_s4p_files(s4p_root, output_dir)
    log(f"Found {len(sources)} S4P file(s) under {s4p_root}.")
    planned, unmatched = plan_copies(index, sources)

    for item in planned:
        shutil.copy2(item.source, output_dir / item.dest_name)
        log(f"Copied {item.dest_name}")
        log(f"    from {item.source.relative_to(s4p_root)}")

    for source in unmatched:
        log(f"No leg map serial for {source.relative_to(s4p_root)}")

    filtered_path = output_dir / f"{legmap_path.stem}_filtered.csv"
    write_filtered_legmap(
        filtered_path, legmap.fieldnames, ((item.row, item.dest_name) for item in planned)
    )
    log(f"Wrote {filtered_path} ({len(planned)} row(s)).")

    summary = JobSummary(
        copied=len(planned),
        unmatched=len(unmatched),
        serials=len({item.serial for item in planned}),
        filtered_path=filtered_path,
    )
    log(
        f"Done. Copied {summary.copied} file(s) for {summary.serials} serial(s). "
        f"Unmatched files: {summary.unmatched}."
    )
    return summary
