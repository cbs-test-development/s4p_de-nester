# Architecture

> Skeleton. Fill each section in for your service and delete this line.

## Overview

<!-- What the service does, and its place in the wider system. -->

## Components

<!-- One row per module or package: responsibility, and what it depends on. -->

| Component | Responsibility | Depends on |
| --- | --- | --- |
| `src/app/main.py` | Entrypoint. Wiring only: loads settings, configures logging, opens the GUI. | `app.config`, `app.denest.gui` |
| `src/app/config.py` | Reads the environment into `Settings`. | `python-dotenv` |
| `src/app/denest/` | Flattens nested S4P files and writes a filtered leg map. See [denest/README.md](denest/README.md). | standard library only (`tkinter` for the GUI) |

## Data flow

<!-- How a request or record moves through the components above. -->

## Layout conventions

<!--
Inherited from the template. `tests/` mirrors `src/app/` 1:1, `docs/` mirrors it
feature-for-feature. See AGENTS.md.
-->

## Trade-offs

<!--
Decisions worth defending, and what they cost. Template defaults to record or
revisit: src layout without installation (PYTHONPATH), hand-pinned requirements
with no lockfile, coverage gated (90% on changed lines, 80% overall),
notebooks committed with outputs, no enforced commit or versioning convention.
-->

## CI

<!-- Status checks: lint, typecheck, test. See .github/workflows/ci.yml. -->

## Deployment

<!--
How this is built, where it runs, how config and secrets reach it, how to roll
back. The template ships no Dockerfile - this is each service's own decision.
-->
