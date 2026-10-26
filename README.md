# Python Service Template

Starting point for Python services. Click **Use this template**. You are recommended to override the README with your own.

## Check

```bash
ruff check .
ruff format --check .
mypy
pytest
```

Same four commands CI runs, as three status checks — the only automated validations
in the repo.

**There are no git hooks.** Nothing checks your code on commit, so run these
yourself before committing and pushing — otherwise CI is the first thing to find out.

## Layout

```
src/app/          your code
tests/            mirrors src/app/ 1:1
docs/             architecture, onboarding, one README per feature
data/             datasets (committed)
notebooks/        experiments (committed with outputs)
```

## First steps in a new repo

1. Replace `python-service-template` in [.env.example](.env.example) and
   [src/app/config.py](src/app/config.py).
2. Fill in [docs/architecture.md](docs/architecture.md).
3. Implement `run()` in [src/app/main.py](src/app/main.py).
4. Write tests as you go. Coverage is enforced — 90% on the lines each PR
   changes, 80% overall. Either gate can be tuned or turned off in
   [pyproject.toml](pyproject.toml); see the Tests section of [AGENTS.md](AGENTS.md).
5. Require `lint`, `typecheck`, `test` in branch protection.
6. Decide your commit, branching, and versioning conventions and record them in
   [AGENTS.md](AGENTS.md) — the template does not pick these for you.
7. Rewrite this README for your service.

## Conventions

The only automated gates are lint, types, and tests. Commit format, versioning,
and tagging are your team's choice — nothing enforces them.

`CHANGELOG.md` is manual — update it before you merge.
No linter or hook touches a non-Python file.

Details in [AGENTS.md](AGENTS.md).

## Docs

| | |
| --- | --- |
| [AGENTS.md](AGENTS.md) | Coding standards. |
| [docs/onboarding.md](docs/onboarding.md) | Setup, running, testing. |
| [docs/architecture.md](docs/architecture.md) | Design and trade-offs. |
| [docs/BRANCH_PROTECTION.md](docs/BRANCH_PROTECTION.md) | Branch Protection setup guide. |
| [CHANGELOG.md](CHANGELOG.md) | Hand-maintained release history. |