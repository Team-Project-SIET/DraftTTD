# P4 — Exit-Gate Full-Suite Regression (offline)

**File of record:** `.scratch/ramrom-product/research/07-exit-regression-full-suite-2026-11-12.md`
**Round:** P4 (operator-ordered full-suite exit round, first on file)
**Head at run time:** `74c8152` (branch `miles/fright-delivery`, uncommitted docs work aside)
**Date:** 2026-11-12
**Mode:** fully offline — no OpenTTD launch, no AdminPort, no `--run-openttd` / `--run-postgres`, no grant, no sealed `artifacts/` byte touched, no relabeling, no push.

## 1. Command of record and capture

There is no full-suite command of record on file (REPRODUCE.md records focused
suites only; full-tree health was recorded UNKNOWN). The operator ordered this
round as the named first full-suite exit round. The run:

```bash
.venv/bin/pytest tests/ -p no:cacheprovider > /tmp/opencode/exit-regression-2026-11-12/pytest-full.out 2>&1
```

- Working directory: repo root. Fresh capture directory created for this run
  (two earlier launch attempts died to an agent-side interruption and a server
  restart before producing a complete capture; neither produced a usable
  result and neither is recorded as a run outcome).
- Exit code: **1** (failures present).
- Capture: `/tmp/opencode/exit-regression-2026-11-12/pytest-full.out`
  (transient; this note and the ledgers are the durable record).

## 2. Summary line

```
57 failed, 6271 passed, 54 skipped in 3797.26s (1:03:17)
```

- Collected 6382 tests across 239 files (collect-only probe before the run);
  57 + 6271 + 54 = 6382 exactly — the whole tree ran to completion, no
  collection errors, no interrupted summary.
- The 54 skips are the offline self-skips of the native/postgres-gated tests
  (`tests/conftest.py` `--run-openttd` / `--run-postgres` options absent), as
  expected for an offline run.

## 3. Comparison against the 53 legacy known-red set

The 53 legacy offline reds of record (map lines 42–45; triage report
`.scratch/ramrom-product/research/04-legacy-53-regression-triage.md`, committed
on branch `Rarekk/legacy-53-regression-audit` as `e361450`, read via
`git show`): controlled P08 e2e ×51, corridor ladder VM ×1, structural-world
fixture ×1.

### Group A — controlled P08 e2e ×51: reproduced exactly

- `grep -c '^FAILED tests/test_p08_controlled_e2e.py'` = **51**.
- Spot-checked mechanism matches the triage's Group A diagnosis (frozen
  fixture digest drift): e.g. `test_full_accepted_artifact_pipeline_and_deterministic_record`
  fails in `admit()` → `accepted_bytes()` with
  `PlanningFactError: controlled accepted bytes mismatch`
  (`tests/test_p08_controlled_e2e.py:227` via `:537`).

### Group C — structural-world fixture ×1: reproduced exactly (same test ID)

- `tests/test_structural_world.py::test_real_catalog_and_enrichment_regression_fixtures_are_valid_but_separate_runs`
  FAILED with a manifest sha256 drift in `tests/fixtures/cargo_catalog_checkpoint`:
  computed `1c025d4a029758503573ae2e9defd05b393fc7bbd874ebc23be6cec5139953ce`
  vs sealed `f52aaac83eeb239ed77e609d5a29b4e934d692001f62a8bc40b882ed9123233b`
  (`tests/test_structural_world.py:702`).
- The earlier hypothesis that this one might pass on Linux (Windows CRLF
  cause) is **not** confirmed: it failed on Linux with a digest mismatch, not
  a line-ending artifact.

### Corridor family — ×1 red, but the failing test ID differs from the triage's named target

- FAILED: `tests/test_corridor_cargoflow2_vm.py::test_ladder_of_record_runs_green`
  — `AssertionError: package dropped request finance-00: no reply`
  (`tests/test_corridor_cargoflow2.py:580`, reached via `run_probe_vm` at
  `:667`). This is the corridor ladder VM test: the map's "corridor ladder VM
  ×1" count is reproduced at count 1.
- The triage report's named target test
  `tests/test_corridor_cargoflow2.py::test_delivered_verdict_never_fires_on_the_terminal_class`
  **PASSED** this run (absent from the FAILED list). No force-fit is made in
  either direction: the corridor family contributed exactly one red, and that
  red is the VM ladder test, not the triage's named target.
- Both candidate Group-B descriptions cannot be true simultaneously; this run
  records what actually happened. Which description the historical 53
  intended (and why the VM ladder red now stands where the named target
  passes) is not adjudicated this round.

### Additional reds NOT in the legacy 53: 4

57 total − 51 (Group A) − 1 (corridor VM) − 1 (Group C) = 4:

1. `tests/test_classification_execution.py::test_sealed_budgets` —
   `assert 410 == 103` (`pages_limit`), `tests/test_classification_execution.py:121`.
2. `tests/test_terrain_classification_preparation.py::test_prepare_materializes_a_pending_authorization_candidate`
   — `{'total_response_bytes_limit': 208280} != 52324`,
   `{'pages_limit': 410} != 103`, `tests/test_terrain_classification_preparation.py:58`.
3. `tests/test_world_correspondence.py::test_fallback_schedule_is_sealed_and_explicit`
   — `assert 208280 == (103 * 508)` (`facts_response_bytes_limit`),
   `tests/test_world_correspondence.py:53`.
4. `tests/test_qualification_preparation.py::test_finalization_failure_cannot_publish_qualification[terminal]`
   — `assert not p.spec.workspace.root.exists()` → the runtime workspace
   `prelaunch/isolated/openttd-15.3-nct_7cgp` still exists after the FAILED
   finalization, `tests/test_qualification_preparation.py:386`.

Observation (recorded, not diagnosed): items 1–3 share one signature — the
code computes 410 pages / 208280 bytes (= 410 × 508) where the tests seal
103 pages / 52324 bytes (= 103 × 508); the sealed-constant tests and the
computed budget have drifted apart. Item 4 is a separate mechanism
(workspace retention after terminal finalization failure). Root-cause
adjudication and any fix are separate operator decisions, not part of P4
(the triage report's fix-branch proposals likewise stand as operator
decisions).

## 4. Outcome of record

- The exit gate **does not pass**: 57 reds against a known-red set of 53.
- The legacy-53 structure is recognizable in the run: Group A ×51 exact,
  Group C ×1 exact, corridor family ×1 (VM ladder test, count matches the
  map's description; the triage's named target passes instead).
- 4 additional reds exist beyond the legacy set. Because no historical
  full-suite baseline exists on file (REPRODUCE.md records full-tree health
  as UNKNOWN and this is the first recorded full-suite run), whether these 4
  are new regressions, long-standing tree state, or clone/evidence gaps
  cannot be established from file. They are recorded at this run's identity
  only.
- Nothing relabeled: no historical outcome changes; no forced matches; no
  invented pass criteria. The gate remains sealed/open exactly as the map
  states; this note is the recorded evidence of the gate's first full-suite
  execution.

## 5. UNKNOWNs preserved

- Whether the 4 additional reds are new vs pre-existing (no prior full-suite
  baseline on file; first run of record).
- Whether the corridor red of record in the historical 53 was the VM ladder
  test or the triage's named target (the two on-file descriptions disagree;
  this run fails the VM ladder and passes the named target).
- Group C's actual fixture-drift mechanism (digest mismatch recorded; the
  CRLF hypothesis is not confirmed and not adjudicated).
- Flakiness/ordering sensitivity of the suite (single offline capture only;
  no repeat runs this round).
- Root causes and fixes for all reds remain operator decisions (triage
  report proposals stand unexecuted).
