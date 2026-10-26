# Coding standards and conventions

This file is the canonical description of how this repo works. It is read by
both humans and AI coding agents. Keep it current: if you change a convention,
change it here in the same PR.

Customise it for your service. Everything below is the template's default, not
an org mandate — but if you loosen something, say why in the same edit.

---

## Layout

```
src/app/          the code. Not a distributable package.
  main.py         the single entrypoint
  config.py       environment/config loading
  <feature>/      one package per feature
tests/            mirrors src/app/ 1:1
docs/             mirrors src/app/ feature-for-feature
data/             datasets used by the app and notebooks
notebooks/        experiments and training runs
```

Three mirrors, and they are the rule this repo cares about most:

- `src/app/billing/invoices.py` → `tests/billing/test_invoices.py`
- `src/app/billing/` → `docs/billing/README.md`

When you add a feature package, add its test package and its `docs/<feature>/README.md`
in the same PR. A feature with no doc is not finished. Test which cover multiple modules can be added to the root tests dir (Not recommended).

Keep `main.py` thin — wiring only. Logic lives in feature packages. When a module
starts doing two things, split it; a file you can hold in your head is a file you
can change safely.

You are free to modify the layout to suit the needs of the project.

## Environment

**Always work inside a virtual environment — `venv` or conda.** Never install this
project's dependencies into a system, global, or base conda Python.

Either tool is fine. Pick one per clone and stay in it:

```powershell
# venv - what the docs assume
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1

# conda
conda create -n <service-name> python=3.12
conda activate <service-name>
```

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

Then `pip install -r requirements-dev.txt`.

- `.venv/` is gitignored. Name a conda environment after the service so it is
  obvious which clone it belongs to.
- **Activate it before running the checks.** `ruff`, `mypy`, and `pytest` resolve
  from `PATH`; with nothing active you can silently run a different installation —
  an Anaconda `mypy`, or a `pytest` without `pytest-cov` — and get a result that
  means nothing. A pass from the wrong environment is worse than a failure.
- Never `pip install` anything without adding a pinned line to `requirements.txt`
  or `requirements-dev.txt` in the same change. An undocumented dependency works
  on your machine and nowhere else.
- **Agents:** confirm the environment is active before running commands rather
  than assuming it — `python -c "import sys; print(sys.prefix)"` should point
  inside the environment, not at a system Python. If an import fails, activate the
  environment or add the dependency; never install globally to work around it.

## Imports and the src layout

`src/app/` is **not installed**. Two consequences:

- `pytest` works because `pyproject.toml` sets `pythonpath = ["src"]`.
- Running the app needs `PYTHONPATH=src` (`$env:PYTHONPATH="src"` in PowerShell).

Import from the `app` package root — `from app.config import load_settings`.
Never use relative imports that climb out of a package (`from ...foo import`),
and never manipulate `sys.path` in application code.

## Style and types

`ruff` and `mypy --strict` are not advisory. CI fails on either.

- Formatting is `ruff format`. Do not hand-format; do not argue with it.
- Line length is 100.
- Annotate everything, including tests. `Any` needs a comment explaining why.
- No `# type: ignore` without a specific error code and a reason:
  `# type: ignore[arg-type]  # upstream stub is wrong, see <issue>`.
- Public functions get a docstring saying what they do, and what they raise if
  the answer is non-obvious. Skip docstrings on obvious private helpers — the
  `D` ruleset is deliberately off.

## Configuration

All configuration comes from the environment, read in `src/app/config.py`.

- Every variable the service reads **must** be listed in `.env.example` with a
  comment and a safe placeholder. If it is not in `.env.example`, it does not exist.
- Add a field to `Settings` and read it in `load_settings()`. Use `required()`
  for variables with no sane default, `optional()` for ones with a default.
- Never read `os.environ` outside `config.py`. Pass `Settings` down instead.
- Never commit `.env`. Never put a real secret in `.env.example`.

## Tests

- `pytest` from the repo root. Options live in `pyproject.toml`.
- There are **no git hooks**. Nothing runs the tests on commit — you run them
  yourself, and CI runs them on push and on the PR. See
  [Before you commit or push](#before-you-commit-or-push).
- Mirror the source tree. One test module per source module.
- Change environment and global state through `monkeypatch`, never directly.
- Test behaviour through the public interface, not private helpers.
- Coverage is **gated twice**, and both gates run in the CI `test` job:
  - **Diff gate — 90%.** On a pull request, the lines added or changed must be
    at least 90% covered. `diff-cover` checks this and names the uncovered lines.
    It holds new code to a high bar without making you pay off old debt first.
    PRs with no Python changes pass it automatically.
  - **Overall gate — 80%.** Total coverage of `src/app/` must stay at or above
    80%, so it cannot slowly drift down. Branches count as well as lines.
- Both thresholds live **only** in `pyproject.toml`: `fail_under` under
  `[tool.diff_cover]` (diff gate) and under `[tool.coverage.report]` (overall
  gate). Never add `--cov-fail-under` to `addopts` — it overrides `fail_under`.
- **Changing a threshold.** Edit its `fail_under`; `0` turns that gate off. Not
  every service needs both — prototypes, thin wrappers, and notebook-heavy
  services may not, and an existing repo with old debt might keep only the diff
  gate. No CI or branch-protection change is needed. Say why in the same edit,
  and **never lower a threshold just to get a PR to pass** — add the tests.

## Commits, versioning, releases

Not prescribed. Commit message format, branching, versioning, and tagging are
this team's call — pick what suits the service and write it down here.

Nothing in the toolchain validates any of it. There is no commit-message hook and
no commit-message CI check. The only automated gates are lint, types, and tests.

## Changelog

**`CHANGELOG.md` is maintained by hand, and updating it is part of opening a
pull request — not an afterthought at release time.**

Before you request review or merge:

1. Add an entry under the `## Unreleased` heading in [CHANGELOG.md](CHANGELOG.md).
2. Put it under the right category — `Added`, `Changed`, `Deprecated`, `Removed`,
   `Fixed`, or `Security` — creating the heading if it is not there yet.
3. Write it for the person consuming the service, not the person who wrote the
   code. "Webhook parser no longer crashes on an empty payload" beats "fixed bug
   in parser". Say what someone has to *do* about it if the answer isn't nothing.
4. Reference the PR or issue number where it helps: `(#42)`.

Nothing generates this file and no tool will write it for you. A behaviour change
merged without a changelog entry is an incomplete PR; the checklist in
[.github/PULL_REQUEST_TEMPLATE.md](.github/PULL_REQUEST_TEMPLATE.md) asks for it.
Since nothing enforces it, this one is on reviewers.

The one exception: changes with no consumer-visible effect — a refactor, a test,
a typo, a CI tweak. Those need no entry. If you are unsure whether something is
visible, add the entry.

On release, rename `Unreleased` to whatever version scheme this team picked, plus
the date, then start a fresh `Unreleased` heading above it.

## Dependencies

- `requirements.txt` — runtime. `requirements-dev.txt` — tooling and CI.
- Hand-maintained, no lockfile, no `pip-compile`. Pin **everything** with `==`.
- New dependency? Say what it is for and why in the PR body.
- `requirements-dev.txt` is the single source of the tool versions. CI installs
  that same file, so local and CI cannot drift.

## Notebooks and data

`notebooks/` and `data/` are committed, and **notebooks keep their outputs** —
these repos are private and the outputs are part of the record.

- Linters and type checkers do not touch either directory. Exploratory code is
  not held to service standards.
- **Nothing in the toolchain may read or rewrite a non-Python file, anywhere.**
  Three mechanisms enforce this:
  1. `include = ["*.py", "*.pyi", "**/pyproject.toml"]` in `pyproject.toml` — a hard
     allowlist of file types ruff may open. Ruff's default `include` covers `*.ipynb`
     and `*.md`, and `ruff format` rewrites Python code blocks inside Markdown.
     Excluding directories does not stop that; narrowing `include` does.
  2. `files = ["src", "tests"]` in `[tool.mypy]`, so it never walks either directory.
  3. `data/** -text` in `.gitattributes` — git itself performs no line-ending
     conversion on datasets, so they stay byte-for-byte as committed.
- **Do not add git hooks.** There are none by design, and the usual `pre-commit`
  starter set — `trailing-whitespace`, `end-of-file-fixer`, `pretty-format-json`,
  `mixed-line-ending`, `check-added-large-files`, `nbstripout` — would variously
  rewrite committed JSON and CSV, strip the notebook outputs above, or reject
  notebooks for being large. Run the checks by hand instead.
- A notebook is an experiment, not a deliverable. When notebook code becomes
  something the service depends on, **move it into `src/app/`** with tests. Do
  not import from `notebooks/`.
- You can commit any data files in the data folder under 50mb in size. Anything under a 100mb in size should be verfied by the user before being committed. Do not commit any files over 100mb in size.

## Before you commit or push

**This repo has no git hooks. Nothing is checked automatically on commit — you run
the checks yourself.** Run all four from the repo root, with the virtual
environment active:

```bash
ruff check .            # lint
ruff format --check .   # formatting  (drop --check to fix in place)
mypy                    # strict type checking
pytest                  # the full test suite
```

All four must exit `0`. Read the output rather than assuming:

- `ruff check --fix .` fixes most lint findings; `ruff format .` fixes formatting.
- `pytest` exiting `5` means it collected **no tests**. That is a red build, not a
  pass.
- `pytest` fails when total coverage is under the overall gate (80%), even if
  every test passed. See [Tests](#tests). That includes a partial run
  (`pytest tests/test_x.py`, `pytest -k name`), which covers only part of the
  code. Add `--no-cov` when you run a subset. The checks above are always the
  full suite.
- A pass from outside the project virtual environment proves nothing — see
  [Environment](#environment).

Before opening a pull request, also run the diff gate — CI runs it on every PR:

```bash
git fetch origin main                                # the base to diff against
pytest                                               # writes coverage.xml
diff-cover coverage.xml --config-file pyproject.toml # changed lines >= 90% covered
```

It diffs against `origin/main` and counts your uncommitted changes too. If you
work from a fork, `origin` is your fork — fetch the team repo instead and pass
`--compare-branch=upstream/main` (or whichever remote points at it).

**This applies to AI agents as much as to people.** If you are an agent working in
this repo:

- Run all four commands before you commit, and again before you push or open a
  pull request. Do not assume anything else has run them — nothing has.
- Do not report work as complete, or open a pull request, on the strength of the
  code looking correct. Run the checks and state the actual result.
- If you could not run them — no environment, missing dependency, sandbox limit —
  say so explicitly. Never imply a check passed when you did not run it.
- Paste real command output into the PR body — the four checks plus
  `diff-cover`. The template asks for evidence, not a claim.

CI is the enforcement point: `lint`, `typecheck`, and `test` run on every push and
pull request, and they are what actually gates a merge. Running them locally first
only means finding out in seconds instead of minutes.

## Definition of done

Four checks and `diff-cover` green locally, CI green, `CHANGELOG.md` updated,
docs updated, `.env.example` updated. Then open the PR.
