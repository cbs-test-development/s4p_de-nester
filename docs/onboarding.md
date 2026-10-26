# Onboarding

Getting from a fresh clone to a green test run and your first commit.

## Prerequisites

- **Python 3.12.** The version is pinned in `pyproject.toml` (ruff target, mypy
  `python_version`) and in the CI workflows. On Windows, `py -0p` lists what you have.
- **git**, configured with your Amphenol email.

## Setup

Always work in a virtual environment — never install into a system or base conda
Python. The commands below use `venv`; conda is equally fine, see
[AGENTS.md](../AGENTS.md#environment).

```powershell
# PowerShell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
Copy-Item .env.example .env
```

```bash
# bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
```

There is nothing else to install. **This repo has no git hooks** — no
`pre-commit install` step, and nothing validates your commit messages. Lint, types,
and tests run in exactly two places: when you run them by hand, and in CI. See
[Checks](#checks).

Then edit `.env`. It is gitignored and must stay that way. `.env.example` lists
every variable the service reads.

## Running

```powershell
$env:PYTHONPATH="src"; python -m app.main   # PowerShell
```

```bash
PYTHONPATH=src python -m app.main           # bash
```

`src/app/` is not an installed package, so `PYTHONPATH` is how Python finds `app`.
Without it you get `ModuleNotFoundError: No module named 'app'`.

To avoid typing it every time, set it once in your IDE's terminal environment:

- **VS Code** — `"terminal.integrated.env.windows": { "PYTHONPATH": "src" }` in
  your *user* settings (the repo does not ship a `.vscode/` directory).
- **PyCharm** — mark `src` as a Sources Root (right-click → Mark Directory as).

Tests never need this — `pytest` sets it itself via `pythonpath` in `pyproject.toml`.

## Testing

```bash
pytest                                # everything, with a coverage report
pytest --no-cov tests/test_config.py  # one module
pytest --no-cov -k defaults           # by name
pytest -vv                            # verbose, when a failure is unclear
```

Use `--no-cov` whenever you run a subset. A partial run covers only part of the
code, so it would fail the overall gate even though every test passed.

Coverage is enforced by two gates, both set in `pyproject.toml`:

- **Overall — 80%.** A full `pytest` run fails if total coverage drops below it.
- **Diff — 90%.** On a pull request, CI fails if the lines you added or changed
  are less than 90% covered, and lists the uncovered lines. Check it locally
  before opening a PR:

  ```bash
  git fetch origin main
  pytest
  diff-cover coverage.xml --config-file pyproject.toml
  ```

Either gate can be turned off by setting its `fail_under` to `0` — see the Tests
section of [AGENTS.md](../AGENTS.md) for when that is reasonable.

New test files mirror the source tree: `src/app/billing/invoices.py` is tested by
`tests/billing/test_invoices.py`. Add an `__init__.py` to each new test package.

## Checks

**Run all four before you commit, and again before you push** — nothing runs them
for you:

```bash
ruff check .            # lint
ruff format --check .   # formatting
mypy                    # strict type checking
pytest                  # the full test suite, with the overall coverage gate
```

Before opening a pull request, also run the diff gate (see [Testing](#testing)).
Together, those five are exactly what CI runs.

There are no git hooks in this repo. A clean commit history says nothing about
whether any of this passes — skip them and CI on the PR is the first thing that
finds out.

Fixing things:

```bash
ruff check --fix .         # auto-fix most lint findings
ruff format .              # rewrite formatting in place
pytest -vv                 # verbose, when a failure is unclear
pytest --no-cov -k <name>  # run a subset by name
```

## Committing

No commit-message format is enforced — there is no `commit-msg` hook and no
commit-message CI check. Commit conventions, branching, versioning, and tagging
are this team's choice; whatever you settle on, record it in
[AGENTS.md](../AGENTS.md) so it is written down somewhere.

Run the four checks above first. Nothing gates the commit itself.

The one thing that *is* expected on every PR: update `CHANGELOG.md`. It is written
by hand, entries go under `## Unreleased` as you go rather than at release time,
and nothing generates it. See the changelog section of [AGENTS.md](../AGENTS.md).

## Troubleshooting

| Symptom | Cause |
| --- | --- |
| `ModuleNotFoundError: No module named 'app'` | `PYTHONPATH=src` not set. Tests are unaffected; only direct runs need it. |
| `mypy` can't find `app` | Run it from the repo root. `mypy_path` in `pyproject.toml` is relative. |
| Nothing ran on commit | Expected — this repo has no git hooks. Run the four checks yourself. |
| `pytest`: `unrecognized arguments: --cov` | A `pytest` without `pytest-cov`, from outside the project environment. Activate the virtualenv. |
| Checks pass locally but CI fails | You ran a different installation. `python -c "import sys; print(sys.prefix)"` should point inside your venv. |
| `pytest` exits 5 | No tests were collected. You deleted the last test — write a real one. |
| Notebook shows up in a lint failure | Should be impossible; ruff's `include` allowlist covers only `*.py` and `*.pyi`. Report it, don't work around it. |

## Next

- [AGENTS.md](../AGENTS.md) — the conventions you are expected to follow
- [architecture.md](architecture.md) — how the pieces fit and why
- [BRANCH_PROTECTION.md](BRANCH_PROTECTION.md) — setting up branch protection on a new repo (repo owners/admins)
