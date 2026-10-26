# denest

Copies S4P files out of a nested folder tree into one flat folder, renames each
one after the leg it was measured on, and writes a copy of the leg map that
lists only the legs that have files.

Source: [src/app/denest/](../../src/app/denest/). Tests: [tests/denest/](../../tests/denest/).

## Running it

```powershell
$env:PYTHONPATH="src"; python -m app.main
```

```bash
PYTHONPATH=src python -m app.main
```

This opens the **S4P De-nester** window. Pick:

| Field | What to choose |
| --- | --- |
| Leg map CSV | The leg map for the test run. |
| S4P root folder | The top of the folder tree that holds the S4P files, at any depth. |
| Output folder | Where the renamed copies go. Defaults to `<root>/renamed_s4p` when you pick a root first. Created if it does not exist. |

Press **Run**. The log shows every file copied and every file that could not be
matched to a serial; a dialog reports the total when the job finishes.

Source files are never moved or changed. Files in the output folder with the
same name as a new copy are overwritten.

## Inputs

### Leg map

A CSV file (UTF-8, with or without a byte-order mark) with a header row
containing at least:

| Column | Meaning |
| --- | --- |
| `LegSn` | Leg serial number. Used to match S4P files to rows. |
| `LegLocation` | Leg position, used in the new filename. |
| `ArrayLocation` | Switch/GPU location, such as `Switch 2-1 GPU 10-16 9-16, GPU`. |

Other columns are carried through to the output unchanged.

- Rows with a blank `LegSn` are ignored. Serials are trimmed of surrounding
  spaces.
- If a serial appears on more than one row, the **first** row is used and the
  log lists the repeats.
- The job stops with an error if the file has no header, is missing a required
  column, or has no rows with a serial.

### S4P files

Every file under the root whose name ends in `.s4p` (any case) is considered.
If the output folder is inside the root, it is skipped, so re-running does not
pick up earlier copies.

A file belongs to a serial when either:

1. **A folder on its path is named exactly after the serial.** The folder
   nearest the file wins. `root/batch/SN123/anything.s4p` belongs to `SN123`.
2. Otherwise, **its filename starts with the serial followed by `_` or `.`**.
   `SN123_PASS.s4p` belongs to `SN123`; `SN1234_PASS.s4p` does not. When several
   serials fit, the longest wins.

Files that match no serial are listed in the log and not copied.

## Outputs

### Renamed S4P files

```
<switch/GPU>_Leg_<LegLocation>_<original filename>.s4p
```

`<switch/GPU>` is `ArrayLocation` up to its last comma. For example:

| | |
| --- | --- |
| `ArrayLocation` | `Switch 2-1 GPU 10-16 9-16, GPU` |
| `LegLocation` | `1` |
| Original file | `96637071293261032812672_739908p5304_PASS.s4p` |
| New file | `Switch_2-1_GPU_10-16_9-16_Leg_1_96637071293261032812672_739908p5304_PASS.s4p` |

To keep the name valid on Windows, the `<switch/GPU>` and `LegLocation` parts
have the characters `< > : " / \ | ? *`, commas and control characters removed,
and runs of spaces replaced by a single `_`. A part left empty becomes
`Unknown`. `.s4p` is added if the original name lacked it.

If two files would get the same name (ignoring case, as Windows does), the later
ones get `_2`, `_3`, ... before `.s4p`.

### Filtered leg map

Written to the output folder as `<leg map name>_filtered.csv`. It has the
original columns, in order, plus a final `File Name` column holding the new
filename. There is **one row per copied file**, so a serial with three S4P files
appears three times. Rows follow the order of the original leg map; files for
the same serial are ordered by their source path. An existing `File Name`
column in the input is replaced.

The file is written with a byte-order mark so Excel opens it as UTF-8.

## Design

| Module | Responsibility |
| --- | --- |
| [naming.py](../../src/app/denest/naming.py) | Builds safe, unique destination names. |
| [legmap.py](../../src/app/denest/legmap.py) | Reads the leg map; writes the filtered copy. |
| [discovery.py](../../src/app/denest/discovery.py) | Finds S4P files and matches each to a serial. |
| [job.py](../../src/app/denest/job.py) | `run_job()`: validates inputs, plans, copies, and writes the filtered map. Reports progress through a `log` callback (the module logger by default). |
| [gui.py](../../src/app/denest/gui.py) | Tkinter window. Runs `run_job()` on a worker thread and shows its log. |

`gui.py` is UI wiring only and is excluded from coverage, because Tk needs a
display and CI has none (see `[tool.coverage.run]` in
[pyproject.toml](../../pyproject.toml)). Keep logic out of it: anything worth
testing belongs in one of the other modules.

`run_job()` can be called directly — from a notebook, for example:

```python
from pathlib import Path
from app.denest.job import run_job

summary = run_job(Path("legmap.csv"), Path("raw"), Path("raw/renamed_s4p"), print)
```

It raises `ValueError` with a readable message for a missing leg map or root
folder, an output folder equal to the root, or an invalid leg map.
