# AGENTS.md

Guidance for AI agents working in this repository.

## Read first

This repo has a strict handoff/evidence discipline. Read these before touching code:

1. `AI_HANDOFF.md` — current state, what is VERIFIED/FAILED/UNKNOWN, per-area file map
2. `TASKS.md` and `EVIDENCE_INDEX.md` — task ledger and evidence records
3. `REPRODUCE.md` — the commands of record for inspection, focused tests, and reports
4. `CONTEXT.md` — project rules; its header is **prepend-only** (sha256-pinned by authority manifests under `docs/authority/`; later edits broke that pin — do not rewrite history in it)

Documentation states future intent; `artifacts/` holds the evidence of what actually happened. When they disagree, trust artifacts.

## Safety rules (do not skip)

- **Never launch OpenTTD, connect to AdminPort, or enable `--run-openttd` / `--run-postgres`** unless the user explicitly authorizes a native run in this session. Native attempts are one-shot: no retry, no reconnect. Docs describing commands are *not* authorization.
- Never modify or regenerate historical evidence (retained attempt bytes in `artifacts/`, which are git-ignored), never relabel a FAILED terminal result, and never replace missing native evidence with synthetic fixtures.
- Do not execute the root file named `--version` and preserve it; it is an accidental artifact of unknown provenance kept for integrity.
- Do not commit/push historical runtime artifacts; they are transfer-only via separate reviewed archives.

## Toolchain and commands

- Python 3.14 (`mise`-managed, see `mise.toml`), deps via uv: `uv sync --locked`. `pyproject.toml`/`uv.lock` are the dependency authority.
- Run everything as `.venv/bin/python` from the repo root (uv-managed venv; no system python).
- Lint: `ruff` (line length 100, py314 target, isort via `I` rules). Type checking uses `ty` with extra paths in `typings/` (currently only `monocypher.pyi`, a stub for the pinned `pymonocypher` dependency).
- Focused tests: run only the test files a change touches; many suites are paired (`tests/test_X.py` offline + `tests/test_X_native.py`), and the `_native` variants may still be controlled/offline — check the file's markers before assuming.
  ```bash
  .venv/bin/pytest -q tests/test_openttd_demo.py tests/test_corridor_extension.py
  ```
- Some tests require git-ignored retained evidence under `artifacts/`; expected failures there mean missing evidence, not a code bug — do not fix by regenerating evidence.
- `pytest-testpaths` is `tests/`; default `addopts = -q`. The `openttd` marker + `--run-openttd` / `--run-postgres` options gate the only truly native/integration runs.
- Alembic migrations live in `alembic/`; PostgreSQL (via `docker-compose.yml`) is only needed for DB persistence paths, never for the OpenTTD demo.

## Architecture (what's where)

Single Python package `app/` (no monorepo). Pipeline: CLI → isolated OpenTTD runtime → qualified observations → **P08** (`app/planning/p08_*.py`, bounded road candidates) → **P05** (`app/planning/optimizer.py`, OR-Tools CP-SAT service selection) → ExecutionPlan → freight compiler/executor (`app/simulation/openttd/`) → encrypted AdminPort + GameScript (`.nut` bridge files) → independent readback → retained receipts → **P07** (`app/experiments/performance_insights.py`, offline reporting).

- Planning logic (route optimization, validation, identity) stays in Python; GameScript (`.nut`) only executes company commands under `GSCompanyMode`.
- Editing a base `.nut` file alone is insufficient — the runner stages composed packages; check staged-package correspondence and replay (`app/simulation/openttd/freight_delivery_package/`, `proof/`).
- Native demo entrypoint: `python -m app.openttd_demo` (requires `OPENTTD_BINARY` and `OPENTTD_OPENGFX_ARCHIVE` env vars **before** Python starts; binary/graphics sha256 are pinned, other versions unsupported). Offline planning: `python -m app.openttd_demo plan` (and `check`, `report`, `compare`).
- `OpenTTD-Knowledge/` and `OpenTTD-Knowledge.zip` are reference documentation pulled in for study, not part of the app.
- Work happens on branch `devmodule2`; the tree habitually contains uncommitted work-in-progress. Check `git status` for what you actually have locally.
