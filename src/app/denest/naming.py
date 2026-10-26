"""Destination filenames for de-nested S4P files.

Rename pattern::

    <switch/GPU>_Leg_<legLocation>_<original filename>.s4p

``<switch/GPU>`` is the ``ArrayLocation`` text before its last comma, with
whitespace turned into underscores. For example ``ArrayLocation``
``Switch 2-1 GPU 10-16 9-16, GPU``, ``LegLocation`` ``1`` and file
``96637071293261032812672_739908p5304_PASS.s4p`` become::

    Switch_2-1_GPU_10-16_9-16_Leg_1_96637071293261032812672_739908p5304_PASS.s4p
"""

from __future__ import annotations

import re

S4P_SUFFIX = ".s4p"

INVALID_FILENAME_CHARS = re.compile(r'[<>:"/\\|?*,\x00-\x1f]')
_WHITESPACE = re.compile(r"\s+")
_REPEATED_UNDERSCORES = re.compile(r"_+")


def safe_token(value: str) -> str:
    """Return ``value`` as a filename-safe token, or ``"Unknown"`` if nothing is left.

    Characters Windows forbids in filenames (and commas) are removed, runs of
    whitespace become a single underscore, and leading/trailing dots,
    underscores and spaces are stripped.
    """
    cleaned = INVALID_FILENAME_CHARS.sub("", value.strip())
    cleaned = _WHITESPACE.sub("_", cleaned)
    cleaned = _REPEATED_UNDERSCORES.sub("_", cleaned).strip(" ._")
    return cleaned or "Unknown"


def switch_gpu_token(array_location: str) -> str:
    """Return the switch/GPU part of an ``ArrayLocation``, dropping the endpoint after a comma."""
    text = array_location.strip()
    if "," in text:
        text = text.rsplit(",", 1)[0].strip()
    return safe_token(text)


def new_filename(array_location: str, leg_location: str, original_name: str) -> str:
    """Build the destination filename for one S4P file, always ending in ``.s4p``."""
    prefix = switch_gpu_token(array_location)
    leg = safe_token(leg_location)
    name = f"{prefix}_Leg_{leg}_{original_name}"
    if not name.lower().endswith(S4P_SUFFIX):
        name += S4P_SUFFIX
    return name


def unique_name(name: str, used: set[str]) -> str:
    """Return ``name``, or ``name`` with ``_2``, ``_3``... before ``.s4p`` if already used.

    Comparison ignores case, because Windows filesystems do: two names that
    differ only in case would overwrite each other. ``used`` holds lowercased
    names and is updated with the name returned.
    """
    if name.lower().endswith(S4P_SUFFIX):
        stem, ext = name[: -len(S4P_SUFFIX)], name[-len(S4P_SUFFIX) :]
    else:
        stem, ext = name, ""
    candidate = name
    number = 2
    while candidate.lower() in used:
        candidate = f"{stem}_{number}{ext}"
        number += 1
    used.add(candidate.lower())
    return candidate
