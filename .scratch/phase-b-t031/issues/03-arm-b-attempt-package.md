# 03: Arm B native attempt package (T-031)

**Type:** gate package
**Status:** staged 2026-11-11 at HEAD `2e5fcc9` — prepare rc 0,
preflight `canonical matched arm B preflight PASS`, verify
`AUTHORIZATION_UNVERIFIED` rc 1; authorizes nothing by itself; the
launch requires the operator's separate fresh explicit authorization,
requested only after arm A's attempt completes (ordering of record
below). **Update 2026-11-12 (E190):** arm A completed — attempt 3
`t031-3` EXECUTED once under the operator's fresh arm-A grant and typed
`CANONICAL_FLEET_MATCHED_VERIFIED` rc 0 (E190: reload correspondence
`EXACT_NATIVE_SEMANTIC_CORRESPONDENCE`, binding null, five annual
receipts 1951–1955, cleanup all-true, manifest match True). The
ordering-of-record condition is now satisfied: **arm B's grant is
next.** Before it is requested, remove the superseded pre-fix staging
dir (no CLAIM, no attempt bytes) and re-prepare with the fixed package
AND the create-q5 anchor:
`rm -rf artifacts/runtime/canonical-fleet-matched-b-t031-1 &&`
`canonical_fleet_matched prepare ... --canonical
artifacts/runtime/canonical-fleet-create-q5 --arm B` (identity
unchanged `canonical-fleet-matched-b-t031-1`), then preflight + verify
`AUTHORIZATION_UNVERIFIED`
**Spec:** `docs/specs/t031-matched-ab-experiments.md`

## Preconditions (all offline-checkable)

- Clean tree at the commit of record (≥ `a9291c2`), branch
  `miles/fright-delivery`; `stash@{0}` untouched.
- Binary pin `276d5b698a6b706154f3af588f6f885b3aebe518f4ecc8f869abf71383b1904c`;
  OpenGFX pin
  `43a0c1dabf39cb865394f3a6cc36d4da5c10ecfaaf55652043104806810903be`.
- `pgrep -x openttd` empty before the run.
- E2 manifest re-verified inside
  `artifacts/runtime/canonical-fleet-create-q5/` (0 mismatches); no
  byte modified by the check.
- Ordering of record: arm A's attempt completes (whatever its typed
  outcome) before arm B's authorization is requested; each arm is a
  separately authorized fresh world load of the same frozen canonical
  evidence.

## Commands of record (one launch, one connection, no retry/reconnect)

```bash
.venv/bin/python -m app.simulation.openttd.proof.canonical_fleet_matched prepare \
  artifacts/runtime/canonical-fleet-matched-b-t031-1 \
  --canonical artifacts/runtime/canonical-fleet-create-q5 --arm B
.venv/bin/python -m app.simulation.openttd.proof.canonical_fleet_matched preflight \
  artifacts/runtime/canonical-fleet-matched-b-t031-1 --arm B
.venv/bin/python -m app.simulation.openttd.proof.canonical_fleet_matched verify \
  artifacts/runtime/canonical-fleet-matched-b-t031-1 --arm B   # AUTHORIZATION_UNVERIFIED
.venv/bin/python -m app.simulation.openttd.proof.canonical_fleet_matched run \
  artifacts/runtime/canonical-fleet-matched-b-t031-1 --arm B --authorize-one-launch
```

## Grant text style (of record)

One execution only; no retry, no relaunch, no reconnect; no seed, world
or scope change; stop on unexpected failure and retain the receipts;
failure is never retried or relabeled; receipts retained whatever the
outcome. This arm-B authorization is NOT shared with arm A, with the
T-030 exercise, or with any earlier attempt (all prior grants void).

## Expected receipts (arm B)

- `result.json` typed `CANONICAL_FLEET_MATCHED_VERIFIED`.
- Reload correspondence pair + `canonical-dispatch.json` (arm B's
  service-1 vehicle: paused capacity-add, OBSERVED capex recorded) +
  `exercise-correspondence.json`.
- Per-service receipts 0/1/2 with `additional_vehicles` on service 1
  (four physical vehicles), telemetry bindings exactly four.
- `arm-record.json` (identity `canonical-fleet-matched-b-t031-1`,
  `dispatch_purchase_capex` OBSERVED, five-anniversary summary,
  provenance labels: fourth-vehicle capex OBSERVED; originals'
  historical construction cost UNKNOWN, belonging to the E2 create
  attempt).
- Certified cleanup + manifest 0 mismatches → then the E-row.

## Fail-closed rules

Partial mutation records its physical vehicle id and is never retried
or accepted; failure stops before further boundaries; cleanup still
runs; nothing relabeled; attempt dir read-only hereafter.

## After both arms (offline, no authorization needed)

```bash
.venv/bin/python -m app.simulation.openttd.proof.canonical_fleet_matched compare \
  artifacts/runtime/canonical-fleet-matched-a-t031-1 \
  --other-arm-directory artifacts/runtime/canonical-fleet-matched-b-t031-1 \
  --output artifacts/runtime/canonical-fleet-matched-a-t031-1
```

`compare_arms` is descriptive-only (OBSERVED deltas, UNKNOWN preserved;
no profit claim, no per-service revenue implication, no forecast).
