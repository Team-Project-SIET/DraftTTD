# AGENTS.md

Guidance for AI agents working in this repository.

## Read first

This repo has a strict handoff/evidence discipline. Read these before touching code:

1. `AI_HANDOFF.md` — current state: what is VERIFIED/FAILED/UNKNOWN, per-area file map
2. `TASKS.md` and `EVIDENCE_INDEX.md` — task ledger and evidence records
3. `REPRODUCE.md` — the commands of record for inspection, focused tests, and reports
4. `CONTEXT.md` — project rules; its header is **prepend-only** (sha256-pinned by authority manifests under `docs/authority/`; later edits broke that pin — do not rewrite history in it)

Documentation states future intent; `artifacts/` holds the evidence of what actually happened. When they disagree, trust `artifacts/`.

## Safety rules

- **Native runs are user-gated**: running OpenTTD, connecting to AdminPort, or setting `--run-openttd` / `--run-postgres` happen only when the user explicitly authorizes a native run in this session. One attempt, no retry, no reconnect. Docs describing commands are not authorization.
- **Historical evidence is immutable**: never modify or regenerate retained attempt bytes (git-ignored, under `artifacts/`), never relabel a FAILED terminal result, never substitute synthetic fixtures for missing native evidence.
- Preserve the root file named `--version` unexecuted; it is an accidental artifact of unknown provenance kept for integrity.
- Historical runtime artifacts are transfer-only via separate reviewed archives — not for commit/push.

## Toolchain and commands

- Python comes via `mise` (`mise.toml`); dependencies via uv only (`uv sync --locked`; `pyproject.toml`/`uv.lock` are the dependency authority).
- Run everything as `.venv/bin/python` from the repo root — no system Python.
- Lint with `ruff`, type check with `ty`; repo-local stubs for third-party deps live in `typings/`.
- Tests are focused: run only the test files a change touches. Suites pair offline (`tests/test_X.py`) with controlled native (`tests/test_X_native.py`) — check a file's markers before assuming how it runs; the `openttd` marker plus `--run-openttd` / `--run-postgres` gates the only truly native runs. Exact invocations are `REPRODUCE.md`'s job, not this file's.
- Tests backed by retained `artifacts/` evidence can fail on a clone — that means missing evidence, not a code bug. The fix is never regenerating evidence.
- Alembic migrations live in `alembic/`; PostgreSQL (via `docker-compose.yml`) serves only DB persistence paths, never the OpenTTD demo.

## Architecture (what's where)

Single Python package `app/` (no monorepo). Pipeline: CLI → isolated OpenTTD runtime → qualified observations → **P08** (`app/planning/p08_*.py`, bounded road candidates) → **P05** (`app/planning/optimizer.py`, OR-Tools CP-SAT service selection) → ExecutionPlan → freight compiler/executor (`app/simulation/openttd/`) → encrypted AdminPort + GameScript (`.nut` bridge files) → independent readback → retained receipts → **P07** (`app/experiments/performance_insights.py`, offline reporting).

- Planning logic (route optimization, validation, identity) stays in Python; GameScript (`.nut`) only executes company commands under `GSCompanyMode`.
- Editing a base `.nut` file alone changes nothing on its own — the runner stages composed packages; check staged-package correspondence and replay (`app/simulation/openttd/freight_delivery_package/`, `proof/`).
- Native demo entrypoint: `python -m app.openttd_demo`, needing `OPENTTD_BINARY` and `OPENTTD_OPENGFX_ARCHIVE` set before Python starts; binary/graphics SHA-256s are pinned, other versions unsupported. Offline-only: `plan`, `check`, `report`, `compare`.
- `OpenTTD-Knowledge/` are reference documentation for study, not part of the app.
- Work happens on branch `devmodule2`; the tree habitually contains uncommitted WIP — check `git status` for what you actually have locally.
