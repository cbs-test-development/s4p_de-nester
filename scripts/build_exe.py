"""Build the S4P De-nester as a single Windows executable with PyInstaller.

Run from the repo root, inside the project virtual environment::

    python scripts/build_exe.py

The executable is written to ``dist/S4P-De-nester.exe``. ``build/`` holds
PyInstaller's working files and generated spec; both directories are
gitignored. See docs/packaging.md.
"""

from __future__ import annotations

from pathlib import Path

import PyInstaller.__main__

REPO_ROOT = Path(__file__).resolve().parent.parent
NAME = "S4P-De-nester"


def main() -> None:
    """Run PyInstaller with this project's settings."""
    build_dir = REPO_ROOT / "build"
    PyInstaller.__main__.run(
        [
            str(REPO_ROOT / "src" / "app" / "main.py"),
            f"--name={NAME}",
            "--onefile",
            # A GUI app: no console window behind it.
            "--windowed",
            # src/app is not installed; this is PyInstaller's PYTHONPATH=src.
            f"--paths={REPO_ROOT / 'src'}",
            f"--distpath={REPO_ROOT / 'dist'}",
            f"--workpath={build_dir}",
            # Keep the generated spec out of the repo root (*.spec is gitignored).
            f"--specpath={build_dir}",
            "--clean",
            "--noconfirm",
        ]
    )


if __name__ == "__main__":
    main()
