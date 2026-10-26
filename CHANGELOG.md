# Changelog

Maintained **by hand**. Nothing generates this file.

Every pull request that changes behaviour adds an entry under `Unreleased`
before it is merged. See the changelog section of [AGENTS.md](AGENTS.md).

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Use these categories, in this order, and omit any that are empty:

`Added` · `Changed` · `Deprecated` · `Removed` · `Fixed` · `Security`

On release, rename `Unreleased` to the new version with its date and start a
fresh `Unreleased` heading above it. The versioning scheme is this team's choice —
nothing in the repo enforces one.

---

## Unreleased

### Added

- S4P De-nester: run `python -m app.main` (with `PYTHONPATH=src`) to open a
  window that copies nested S4P files into one folder, renamed as
  `<switch/GPU>_Leg_<LegLocation>_<original filename>.s4p`, and writes
  `<leg map>_filtered.csv` with one row per copied file. See
  `docs/denest/README.md`. Compared with the original `denest_s4p.py` script:
  - Choosing an output folder that contains the S4P root no longer causes every
    file to be skipped.
  - Destination names that differ only in case now get a `_2` suffix instead of
    overwriting each other on Windows.
  - When a serial is repeated in the leg map, its files are ordered by the
    first row's position (the row whose data is used), not the last.
- Coverage is now enforced: 90% on changed lines in pull requests, 80% overall.
  Turn off either gate by setting its `fail_under` to 0 in `pyproject.toml`.
  Run `diff-cover coverage.xml --config-file pyproject.toml` after `pytest` to
  check the diff gate locally. (AB#60)
- Created `BRANCH_PROTECTION.md` setup guide in `docs/`, with supplementary
  images in `docs/images/branch-protection`, and linked it from
  `docs/onboarding.md` and `README.md`.
- Initial service scaffolding from `python-service-template`: ruff, mypy strict,
  pytest, and CI.

<!--
Write entries for the reader, not the committer. What changed from their point of
view, and what they need to do about it.

  ### Added
  - Invoice retry endpoint at `POST /invoices/{id}/retry`.

  ### Changed
  - `LOG_LEVEL` now defaults to `INFO` instead of `DEBUG`.

  ### Fixed
  - Webhook parser no longer crashes on an empty payload.

Reference the PR or issue where it helps: `(#42)`.
-->
