# Packaging

The app ships as a single Windows executable, `S4P-De-nester.exe`, built with
[PyInstaller](https://pyinstaller.org/). It bundles Python, Tk and the code
under `src/app/`, so the machine running it needs no Python install.

## Building

From the repo root, on Windows, inside the project virtual environment (see
[onboarding.md](onboarding.md)):

```powershell
pip install -r requirements-dev.txt   # pyinstaller is pinned there
python scripts/build_exe.py
```

Output:

| Path | What it is |
| --- | --- |
| `dist/S4P-De-nester.exe` | The executable. About 10 MB. |
| `build/` | PyInstaller's working files and the generated `.spec`. Safe to delete. |

Both directories are gitignored. Every PyInstaller option lives in
[scripts/build_exe.py](../scripts/build_exe.py); change them there, not on the
command line, so every build is the same.

PyInstaller does not cross-compile: build on Windows to get a Windows `.exe`.
The executable targets the Python version of the environment that built it.

## What the build does

- Entry point is [src/app/main.py](../src/app/main.py), exactly as
  `python -m app.main` runs it.
- `--paths src` stands in for `PYTHONPATH=src`.
- `--onefile` produces one file; it unpacks to a temporary folder on each
  launch, so the first start takes a second or two.
- `--windowed` means no console window. Log output from `app.main` goes nowhere
  in the executable; the window's own log pane is unaffected.

A `missing module named 'collections.abc'` line in
`build/S4P-De-nester/warn-S4P-De-nester.txt` is a known false alarm and can be
ignored.

## Checking a build

Run `dist/S4P-De-nester.exe`. The **S4P De-nester** window should open. Run a
job against a small leg map and folder tree and check the output folder.

Windows SmartScreen may warn about an unsigned executable from the internet.
Choose **More info → Run anyway**, or sign the executable if this becomes a
problem for users.
