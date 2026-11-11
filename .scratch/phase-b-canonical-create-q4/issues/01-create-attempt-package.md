# 01: Canonical create-q4 native attempt package (Phase B anchor regeneration)

**Type:** gate package
**Status:** staged 2026-11-12 at HEAD `28e7570` — prepare rc 0
(`CANONICAL PREFLIGHT PASS; ZERO LAUNCHES`), preflight PASS re-run
offline, and the authorization gate holds (`create` without
`--authorize-one-launch` refuses, rc 2); authorizes nothing by itself;
the launch requires the operator's separate fresh explicit
authorization
**Why this stage exists (E185/E186):** the E184 armed-seal fix changed
the staged bridge digest (`6c6a703c…`); the arm attempt `t031-2` proved
the create-q3 anchor (sealed under the pre-fix bridge `0fa190a0…`)
loads and answers under the fixed bridge, but the exact-correspondence
contract (including `bridge_sha256`) correctly refused it. Each bridge
generation needs its own q-record (q4 VM record, done) AND its own
native create anchor — this stage is that anchor for the fixed bridge.
**Spec context:** `docs/specs/t031-matched-ab-experiments.md` (E186
update); evidence rows E183–E186.

## Preconditions (all offline-checkable)

- Clean tree at the commit of record (≥ `28e7570`), branch
  `miles/fright-delivery`; `stash@{0}` untouched.
- Binary pin `276d5b698a6b706154f3af588f6f885b3aebe518f4ecc8f869abf71383b1904c`;
  OpenGFX pin
  `43a0c1dabf39cb865394f3a6cc36d4da5c10ecfaaf55652043104806810903be`.
- `pgrep -x openttd` empty before the run.
- q4 VM record pins the staged package bytes
  (`artifacts/validation/canonical-fleet-reload-q4/suspension.json`,
  25/25 cases rc 0 at the pinned exact 15.3 Squirrel source commit).
- create-q3 stays sealed retained history; consumed identities are
  never re-prepared.

## Commands of record (one launch, one connection, no retry/reconnect)

```bash
.venv/bin/python -m app.simulation.openttd.proof.canonical_fleet prepare \
  artifacts/runtime/canonical-fleet-create-q4 --stage canonical-fleet-create-q4
.venv/bin/python -m app.simulation.openttd.proof.canonical_fleet preflight \
  artifacts/runtime/canonical-fleet-create-q4 --stage canonical-fleet-create-q4
.venv/bin/python -m app.simulation.openttd.proof.canonical_fleet create \
  artifacts/runtime/canonical-fleet-create-q4 --stage canonical-fleet-create-q4 \
  --authorize-one-launch
```

## Grant text style (of record)

One execution only; no retry, no relaunch, no reconnect; no seed, world
or scope change; stop on unexpected failure and retain the receipts;
failure is never retried or relabeled; receipts retained whatever the
outcome. This create authorization is NOT shared with the T-031 arms,
with T-032, with the T-030 exercise, or with any earlier attempt (all
prior grants void).

## Expected receipts (create-q4)

- `result.json` typed `CANONICAL_CREATED_PENDING_FRESH_PROCESS_RELOAD`
  (the q3 shape; `{launches: 1, connections: 1, mutations: …}`).
- `canonical.sav` + `canonical-provenance.json` (observation sealed
  under the FIXED bridge `6c6a703c…`) + before/paused/readback receipts.
- Certified cleanup + manifest 0 mismatches → then the E-row.
- Downstream of record: arm A `t031-3` re-stages with `--canonical
  artifacts/runtime/canonical-fleet-create-q4` (own fresh grant after
  preflight PASS + `AUTHORIZATION_UNVERIFIED`); arm B re-prepares with
  the fixed package + this anchor after arm A completes; T-032
  re-prepares likewise.

## Fail-closed rules

Partial creation records exactly what landed and is never retried or
accepted; failure stops before further stages; cleanup still runs;
nothing relabeled; attempt dir read-only hereafter; the create-q3
anchor and all earlier evidence stay byte-untouched.
