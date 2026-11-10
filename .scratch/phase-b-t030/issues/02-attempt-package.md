# 02: T-030 attempt package (ONE native exercise launch, operator-gated)

**Type:** gate
**Status:** claimed 2026-11-11 (package prepared; authorization NOT given)
**Spec:** `docs/specs/t030-fleet-capacity-exercise.md`
**Blocked by:** 01 (resolved, `c6ec803`) + fresh explicit operator
authorization.

**What this is:** the complete preauthorization package for the ONE
native T-030 exercise attempt of record. It authorizes nothing by
itself. All prior grants (E141, E142, E145, attempts 1–6 of the
FD-C-2 lane, and every grant before them) are void for reuse — this
attempt needs its own fresh explicit grant in its own session.

## Preconditions (offline, checked at HEAD `c6ec803`)

- Branch `miles/fright-delivery` clean, `stash@{0}` untouched.
- Binary pin `276d5b698a6b706154f3af588f6f885b3aebe518f4ecc8f869abf71383b1904c`
  and OpenGFX pin `43a0c1dabf39cb865394f3a6cc36d4da5c10ecfaaf55652043104806810903be`
  (`artifacts/runtime/verified-assets/opengfx-8.0-all.zip`).
- `pgrep -x openttd` empty immediately before the launch.
- The E2 canonical evidence `artifacts/runtime/canonical-fleet-create-q3/`
  manifest re-verified (0 mismatches) and its protected save still
  `51e45689ae40dfa53c2cc150a05076fcb6e5cc2f38ec4eff56908372ab1297eb`.

## Commands of record (in order; stop on any non-zero exit)

1. Stage (offline, argv never executed):

   ```
   .venv/bin/python -m app.simulation.openttd.proof.canonical_fleet_exercise \
       prepare artifacts/runtime/canonical-fleet-exercise-t030-1 \
       --canonical artifacts/runtime/canonical-fleet-create-q3
   ```

2. Preflight (offline):

   ```
   .venv/bin/python -m app.simulation.openttd.proof.canonical_fleet_exercise \
       preflight artifacts/runtime/canonical-fleet-exercise-t030-1
   ```

   Expected: `canonical fleet exercise preflight PASS`.

3. THE LAUNCH — only under the fresh explicit grant:

   ```
   .venv/bin/python -m app.simulation.openttd.proof.canonical_fleet_exercise \
       run artifacts/runtime/canonical-fleet-exercise-t030-1 \
       --authorize-one-launch
   ```

4. Independent verify (offline, after the attempt):

   ```
   .venv/bin/python -m app.simulation.openttd.proof.canonical_fleet_exercise \
       verify artifacts/runtime/canonical-fleet-exercise-t030-1
   ```

   Expected: `CANONICAL_FLEET_EXERCISE_VERIFIED` (or the typed refusal
   of record, never relabeled).

## Grant text the operator is asked to give (style of ticket-05/E157)

"Confirm — run the T-030 canonical fleet exercise attempt of record:
exactly one execution of the run command above at the current clean
HEAD, one launch, one fresh secure connection, no retry, no relaunch,
no reconnect, no seed or scope change; stop on unexpected failure;
honor the sealed exercise contract (reload correspondence first, then
the paused purchase → dispatch → unpause arm-B exercise); retain all
receipts sealed whatever the outcome."

## What the attempt must produce

`result.json` typed `CANONICAL_FLEET_EXERCISE_VERIFIED`, the reload
correspondence pair (`reload-correspondence.json` +
`reload-readback.sav`), `canonical-dispatch.json`,
`exercise-correspondence.json` binding the three receipt digests,
mutation receipts (`capacity-add`, `canonical-start`,
`canonical-dispatched` responses), cleanup certified
(`reaped`, workspace disposed, credential removed), manifest 0
mismatches, then the E-row.

## Fail-closed rules (unchanged from the spec)

Any drift from the paused construction gates refuses; a partial
mutation records its physical vehicle id and is never retried or
accepted as a complete receipt; failure stops before further
boundaries; cleanup still runs; nothing relabeled; no
feasibility/economics claim outside the receipts.
