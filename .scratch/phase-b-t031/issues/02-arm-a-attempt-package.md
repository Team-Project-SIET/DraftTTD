# 02: Arm A native attempt package (T-031)

**Type:** gate package
**Status:** arm-A attempt 2 (`canonical-fleet-matched-a-t031-2`) EXECUTED
ONCE under the operator's fresh explicit arm-A grant at HEAD `28e7570` —
terminal FAILED rc 1 (E185: no script death this time; the native world
loaded and answered everything, and the correspondence gate
`compare_canonical` correctly refused `bridge_sha256` — the staged
post-fix bridge `6c6a703c…` cannot correspond to the create-q3 anchor
sealed under the pre-fix bridge `0fa190a0…`; sealed read-only, never
retried, never relabeled; grant consumed and void; stale supersession
advances identities). Diagnosis-only round E186: the create anchor is
bridge-generation-bound, so the contract-preserving path is a fresh
canonical create under the fixed bridge. `CREATE` advanced to
`canonical-fleet-create-q4`; `ARM_A` advanced to
`canonical-fleet-matched-a-t031-3` — re-stage THIS arm only after the
create-q4 anchor exists:
`prepare ... --canonical artifacts/runtime/canonical-fleet-create-q4
--arm A`; authorizes nothing by itself; the launch requires the
operator's separate fresh explicit authorization
**Spec:** `docs/specs/t031-matched-ab-experiments.md`

## Preconditions (all offline-checkable)

- Clean tree at the commit of record (≥ `a9291c2`), branch
  `miles/fright-delivery`; `stash@{0}` untouched.
- Binary pin `276d5b698a6b706154f3af588f6f885b3aebe518f4ecc8f869abf71383b1904c`;
  OpenGFX pin
  `43a0c1dabf39cb865394f3a6cc36d4da5c10ecfaaf55652043104806810903be`
  (`artifacts/runtime/verified-assets/opengfx-8.0-all.zip`).
- `pgrep -x openttd` empty before the run.
- E2 manifest re-verified inside
  `artifacts/runtime/canonical-fleet-create-q4/` (0 mismatches); no
  byte modified by the check.

## Commands of record (one launch, one connection, no retry/reconnect)

```bash
.venv/bin/python -m app.simulation.openttd.proof.canonical_fleet_matched prepare \
  artifacts/runtime/canonical-fleet-matched-a-t031-3 \
  --canonical artifacts/runtime/canonical-fleet-create-q4 --arm A
.venv/bin/python -m app.simulation.openttd.proof.canonical_fleet_matched preflight \
  artifacts/runtime/canonical-fleet-matched-a-t031-3 --arm A
.venv/bin/python -m app.simulation.openttd.proof.canonical_fleet_matched verify \
  artifacts/runtime/canonical-fleet-matched-a-t031-3 --arm A   # AUTHORIZATION_UNVERIFIED
.venv/bin/python -m app.simulation.openttd.proof.canonical_fleet_matched run \
  artifacts/runtime/canonical-fleet-matched-a-t031-3 --arm A --authorize-one-launch
```

## Grant text style (of record)

One execution only; no retry, no relaunch, no reconnect; no seed, world
or scope change; stop on unexpected failure and retain the receipts;
failure is never retried or relabeled; receipts retained whatever the
outcome. This arm-A authorization is NOT shared with arm B, with the
T-030 exercise, or with any earlier attempt (all prior grants void).

## Expected receipts (arm A)

- `result.json` typed `CANONICAL_FLEET_MATCHED_VERIFIED`.
- Reload correspondence pair + `canonical-dispatch.json` (arm A adds
  nothing) + `exercise-correspondence.json`.
- Per-service receipts 0/1/2 (three originals, no
  `additional_vehicles`), telemetry bindings exactly three.
- `arm-record.json` (identity `canonical-fleet-matched-a-t031-3`,
  `dispatch_purchase_capex=0`, five-anniversary summary, provenance
  labels: in-run construction spending OBSERVED-zero; originals'
  historical construction cost UNKNOWN, belonging to the E2 create
  attempt).
- Certified cleanup + manifest 0 mismatches → then the E-row.

## Fail-closed rules

Partial mutation records its physical vehicle id and is never retried
or accepted; failure stops before further boundaries; cleanup still
runs; nothing relabeled; attempt dir read-only hereafter.
