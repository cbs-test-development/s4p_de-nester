# What

<!-- What does this change do? One or two sentences. -->

# Why

<!--
What problem does it solve? Link the work item. `Fixes AB#<id>` links an Azure
Boards item, and closes it on merge if the Azure Boards app is connected. Use
`Closes #<n>` for a GitHub issue.
-->

Fixes AB#

# How it was tested

<!--
Paste the evidence, not a claim. "Tested locally" is not evidence.

This repo has no git hooks, so nothing has checked your work before CI. Paste the
real output of all five commands below - the four checks plus diff-cover - with
the virtual environment active. Add test names, screenshots, or anything else
that proves the change works.
-->

```
> ruff check .

> ruff format --check .

> mypy

> pytest

> diff-cover coverage.xml --config-file pyproject.toml

```

# Checklist

<!-- Tick a box with [x] - no spaces inside the brackets, or it will not render. -->

- [ ] **`pytest` run locally and passing** - there are no git hooks, so nothing
      else has checked this before CI
- [ ] `diff-cover coverage.xml --config-file pyproject.toml` passing, or this PR
      explains why a coverage gate was changed
- [ ] `ruff check .`, `ruff format --check .`, and `mypy` clean
- [ ] **`CHANGELOG.md` updated**
- [ ] Tests added or updated, and `tests/` still mirrors `src/app/`
- [ ] Docs updated - `docs/<feature>/README.md`, and `docs/architecture.md` if the design changed
- [ ] New environment variables documented in `.env.example`
- [ ] New dependencies pinned with `==` in `requirements.txt` or `requirements-dev.txt`
