"""Finding S4P files on disk and matching them to leg map serials."""

from __future__ import annotations

from collections.abc import Collection
from pathlib import Path

from app.denest.naming import S4P_SUFFIX


def is_inside(path: Path, parent: Path) -> bool:
    """Return whether ``path`` is ``parent`` or somewhere beneath it, after resolving both."""
    return path.resolve().is_relative_to(parent.resolve())


def find_s4p_files(root: Path, output_dir: Path) -> list[Path]:
    """Return every ``.s4p`` file under ``root``, sorted, matching the suffix case-insensitively.

    If ``output_dir`` lies beneath ``root`` it is skipped, so files copied by a
    previous run are not picked up again.
    """
    skip_output = is_inside(output_dir, root) and output_dir.resolve() != root.resolve()
    found: list[Path] = []
    for current, dirnames, filenames in root.walk():
        if skip_output:
            dirnames[:] = [name for name in dirnames if not is_inside(current / name, output_dir)]
        found.extend(
            current / filename for filename in filenames if filename.lower().endswith(S4P_SUFFIX)
        )
    found.sort()
    return found


def match_serial(path: Path, serials: Collection[str]) -> str | None:
    """Return the leg map serial that ``path`` belongs to, or ``None``.

    A folder named exactly after a serial wins, the nearest such folder first.
    Otherwise the filename must start with the serial followed by ``_`` or
    ``.``; when several serials qualify, the longest wins.
    """
    for part in reversed(path.parts[:-1]):
        if part in serials:
            return part
    best: str | None = None
    for serial in serials:
        if path.name.startswith((f"{serial}_", f"{serial}.")) and (
            best is None or len(serial) > len(best)
        ):
            best = serial
    return best
