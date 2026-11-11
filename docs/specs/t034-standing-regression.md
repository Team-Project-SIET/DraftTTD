# T-034 — Standing full 15.3 regression (Phase B, P2 backlog)

Goal of record (`docs/roadmap-and-scope-2026-11-05.md` §3, T-034 row): a
standing full 15.3 regression, re-runnable any round, with the
legacy-red set classified by ID (never relabeled) and the retained
artifact manifests re-verified.

## Standing regression of record (2026-11-11, at `f0f0155`)

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -m 'not openttd' \
  -p no:cacheprovider --no-header -q --tb=no --junitxml=<fresh>/t034.xml
```

Exact machine-counted totals (junitxml; the printed summary line is
unreliable because the `_squirrel` C extension prints
`Time difference = 0[ms]` at interpreter shutdown after pytest flushes):

- **6342 collected / 6286 passed / 56 failed / 0 errors / 50 skipped**
  (wall ~68 min).

## Legacy-red set, classified by ID (56; every ID pre-existing before this round)

1. `tests/test_p08_controlled_e2e.py` — 51 failed / 11 passed, the
   E159-recorded scope, re-proven by ID then (E159 (7)).
2. `tests/test_classification_execution.py::test_sealed_budgets` —
   verified failing identically at pre-round HEAD `f0b5960` in a
   detached worktree with venv+artifacts bound by symlink (E160
   precedent); the module-level guard had earlier masked this as a
   skip when the binding is incomplete — the failure of record is
   `assert 410 == 103` (`CLASSIFICATION_PAGE_LIMIT` derivation vs the
   test's sealed literal).
3. `tests/test_terrain_classification_preparation.py::test_prepare_materializes_a_pending_authorization_candidate` —
   same pre-round verification.
4. `tests/test_corridor_cargoflow2_vm.py::test_ladder_of_record_runs_green` —
   E155-recorded (`package dropped request finance-00`).
5. `tests/test_world_correspondence.py::test_fallback_schedule_is_sealed_and_explicit` —
   E155-recorded (`assert 208280 == (103 * 508)`).
6. `tests/test_structural_world.py::test_real_catalog_and_enrichment_regression_fixtures_are_valid_but_separate_runs` —
   E153-recorded clone-condition failure.

**Zero failures in any file this Phase B round touched**
(`canonical_fleet_exercise.py`, `canonical_fleet_matched.py`,
`canonical_fleet_continuous.py`, `phase_b_consolidation.py` and their
four test files — 38 tests of the round all green inside the full run).

## Statics of record (2026-11-11)

- Round-touched paths: `ruff check`, `ruff format`, `py_compile`,
  scoped `uvx ty`, `git diff --check` — clean (verified per commit).
- Repo-wide snapshot for honesty: `ruff check app/ tests/` finds 12
  errors in THREE files this round never touched
  (`app/simulation/openttd/corridor_construction.py` UP037 ×4,
  `app/simulation/openttd/proof/corridor_terrain_survey_native.py`
  I001/F401, `tests/test_corridor_terrain_survey_native.py` I001 ×3/
  F401/E501 ×2) — pre-existing committed WIP, counted, never relabeled,
  left for its own reviewed round (E160 precedent).
- `git diff --check` clean; tree clean at `f0f0155`; `stash@{0}` intact.

## Retained-artifact integrity sweep of record (2026-11-11, read-only)

- All **197** `artifact-manifest.sha256` files under `artifacts/`
  re-verified with `sha256sum -c --quiet` from inside each manifest's
  own directory: **0 mismatches**.
- Protected canonical save pin: `canonical-fleet-create-q3/canonical.sav`
  sha256 `51e45689ae40dfa53c2cc150a05076fcb6e5cc2f38ec4eff56908372ab1297eb` — holds.
- OpenGFX pin: `artifacts/runtime/verified-assets/opengfx-8.0-all.zip`
  sha256 `43a0c1dabf39cb865394f3a6cc36d4da5c10ecfaaf55652043104806810903be` — holds.
- OpenTTD binary pin:
  `/home/fed/Downloads/openttd-15.3-linux-generic-amd64/openttd` sha256
  `276d5b698a6b706154f3af588f6f885b3aebe518f4ecc8f869abf71383b1904c` — holds.
- `pgrep -x openttd` empty (no native process; zero launches all round).

## Tickets

- `01-standing-regression-record.md` — resolved (this commit).
