# 01: Five-year continuous native attempt package (T-032)

**Type:** gate package
**Status:** staged 2026-11-11 at HEAD `2e5fcc9` — prepare rc 0,
preflight `canonical five-year continuous preflight PASS`, verify
`AUTHORIZATION_UNVERIFIED` rc 1; authorizes nothing by itself; the
launch requires the operator's separate fresh explicit authorization.
**Update 2026-11-12 (E185/E186):** this staging inherits the create-q3
anchor, which is bound to the pre-fix bridge digest — the E184 bridge
fix and the E186 `CREATE` advance to `canonical-fleet-create-q5` mean
THIS staging is superseded unsealed state (no CLAIM, no attempt bytes):
before T-032's grant is requested, remove the superseded staging dir
and re-prepare with the fixed package AND the create-q5 anchor
(`rm -rf artifacts/runtime/canonical-fleet-continuous-t032-1 &&`
`canonical_fleet_continuous prepare ... --canonical
artifacts/runtime/canonical-fleet-create-q5`), then preflight + verify
`AUTHORIZATION_UNVERIFIED`. Ordering of record: T-031 arms first
(arm A's attempt completes before arm B; T-032's grant after T-031)
**Spec:** `docs/specs/t032-five-year-continuous.md`

## Preconditions (all offline-checkable)

- Clean tree at the commit of record (≥ `b63eb16`), branch
  `miles/fright-delivery`; `stash@{0}` untouched.
- Binary pin `276d5b698a6b706154f3af588f6f885b3aebe518f4ecc8f869abf71383b1904c`;
  OpenGFX pin
  `43a0c1dabf39cb865394f3a6cc36d4da5c10ecfaaf55652043104806810903be`.
- `pgrep -x openttd` empty before the run.
- E2 manifest re-verified inside
  `artifacts/runtime/canonical-fleet-create-q5/` (0 mismatches); no
  byte modified by the check.
- Budget note of record: `monitoring_budgets(3)` allows
  `monitor_seconds=7200` (2 h) wall-clock and 3600 polls × 2 s; the
  five-anniversary horizon is in NATIVE economy time and the stage
  stops typed when five complete economy years are observed.

## Commands of record (one launch, one connection, no retry/reconnect)

```bash
.venv/bin/python -m app.simulation.openttd.proof.canonical_fleet_continuous prepare \
  artifacts/runtime/canonical-fleet-continuous-t032-1 \
  --canonical artifacts/runtime/canonical-fleet-create-q5
.venv/bin/python -m app.simulation.openttd.proof.canonical_fleet_continuous preflight \
  artifacts/runtime/canonical-fleet-continuous-t032-1
.venv/bin/python -m app.simulation.openttd.proof.canonical_fleet_continuous verify \
  artifacts/runtime/canonical-fleet-continuous-t032-1   # AUTHORIZATION_UNVERIFIED
.venv/bin/python -m app.simulation.openttd.proof.canonical_fleet_continuous run \
  artifacts/runtime/canonical-fleet-continuous-t032-1 --authorize-one-launch
```

## Grant text style (of record)

One execution only; no retry, no relaunch, no reconnect; no seed, world
or scope change; stop on unexpected failure and retain the receipts;
failure is never retried or relabeled; receipts retained whatever the
outcome. This authorization is NOT shared with the T-030 exercise, the
T-031 arms, or any earlier attempt (all prior grants void).

## Expected receipts (T-032)

- `result.json` typed `CANONICAL_FIVE_YEAR_CONTINUOUS_VERIFIED`.
- Reload correspondence pair + `canonical-dispatch.json` (arm-A shape,
  no purchase) + `exercise-correspondence.json`.
- Per-service receipts 0/1/2 (three originals, no
  `additional_vehicles`), telemetry bindings exactly three.
- `continuous-snapshots.jsonl` + period reports + telemetry summary;
  `continuous-summary.json` classification
  `NATIVE_FIVE_YEAR_CONTINUOUS` with five complete economy years.
- `continuous-finalization.json` (identity, contract, summary,
  provenance labels as specified).
- Certified cleanup + manifest 0 mismatches → analytics + E-row.

## Fail-closed rules

Partial mutation records its physical vehicle id and is never retried
or accepted; failure stops before further boundaries; the monitor's
`finally` still writes `continuous-partial.json` and period reports;
cleanup still runs; nothing relabeled; attempt dir read-only hereafter.

## Post-run offline analytics (no authorization needed)

`.venv/bin/python -m app.experiments.cli analyze-continuous-freight
artifacts/runtime/canonical-fleet-continuous-t032-1 --output <fresh
analysis dir>` — the pipeline of record
(`app/experiments/freight_continuous_analytics.py`).
