# 01: Exercise conductor (canonical fleet exercise stage)

**Type:** task
**Status:** resolved 2026-11-11
**Spec:** `docs/specs/t030-fleet-capacity-exercise.md`

**What to build:** the runnable T-030 exercise stage of record — new
module `app/simulation/openttd/proof/canonical_fleet_exercise.py`
additive to `proof/canonical_fleet.py` (never modify the frozen
create/reload lane): a `canonical-fleet-exercise-t030-1` identity with
its own execution contract, prepare/preflight/verify/run CLI, staging
from the E2 created evidence with the same byte-pinned bridge package
(`package_bytes()` correspondence to the q3 suspension.json validation
record is required to hold), the proven reload correspondence sequence,
then the purchase→dispatch→unpause conductor
(`dispatch_loaded_arm`, arm B) with owned snapshot saves and cleanup,
typed result `CANONICAL_FLEET_EXERCISE_VERIFIED`. Offline regression
tests (`tests/test_canonical_fleet_exercise.py`) pin: identity
separation and refusal of the q3 identities, contract/prelaunch
fail-closed refusals (CLAIM present, contract mutation, bridge drift,
canonical evidence drift), the byte-pin drift guard, the orchestrating
sequence wire (authorize gate, correspondence-before-intervention
order, arm B, snapshot receipts, cleanup), and prepare-side refusal
symmetry with the reload lane. Nothing launched; no `artifacts/` byte
modified; no historical evidence touched.

**Blocked by:** nothing (dependencies 1–3 of the spec are DONE).

## Answer

Implemented and committed `c6ec803` on `miles/fright-delivery`
(2026-11-11, offline only — zero launches, zero AdminPort, no
`artifacts/` byte touched):

- `app/simulation/openttd/proof/canonical_fleet_exercise.py` — the
  exercise stage of record: `EXERCISE =
  canonical-fleet-exercise-t030-1`, `SCHEMA =
  canonical-fleet-exercise-prelaunch-v1`, `EXERCISE_CONTRACT`
  (purchase/dispatch/unpause true, `intervention_service=1`,
  `armed_boundary="canonical-arm"`);
  `require_bridge_validation` (q3-era
  `artifacts/validation/canonical-fleet-reload-q3/suspension.json`
  byte-pin, source_commit `14ec60f2…` + per-file package SHA-256
  equality, verified live to match the composed package at HEAD);
  `prepare` (stages from the E2 created evidence —
  `verify_created_source` + `verify_save` first, canonical.cfg
  derived config with fresh endpoints, OpenGFX staged into
  `baseset/OpenGFX`, the byte-identical package into
  `RoadFreightProof`, frozen-source seal incl. the four Squirrel
  helpers + `openttdlab` + the validation record, PRELAUNCH seal);
  `preflight` (fail-closed on identity/CLAIM/contract/bridge/config/
  canonical drift + `CanonicalBackend.validate_launch` +
  endpoint re-reservation); `conduct_exercise` (reload
  correspondence FIRST via `driver.establish_reload_context` →
  `reload-before` boundary → `protected_save("reload-readback")` →
  `verify_reloaded` (exact runtime signature — source save sha256 is
  taken internally from `created`; the frozen `canonical_fleet.py`
  call site at line 614 already matches it, no latent inconsistency)
  → `reload-after` boundary → `require_stable_boundary` + restored/
  originals/finance checks → `compare_canonical` → reload receipts
  bound to `EXERCISE_CONTRACT` → `dispatch_loaded_arm(arm="B")` →
  `exercise-correspondence.json` binding the three receipt digests,
  typed `CANONICAL_FLEET_EXERCISE_VERIFIED`); `mutation_receipts`
  (counts `capacity-add`/`canonical-start`/`canonical-dispatched`
  response bytes); `run` (authorize gate → preflight → CLAIM
  launches_allowed=1 retries=0 → launch/connect/welcome
  `("15.3", 42, 64, 64)` seed-42 64×64 identity → conduct → q3-shell
  cleanup); CLI `prepare|preflight|verify|run` with `--canonical` +
  `--authorize-one-launch`.
- `tests/test_canonical_fleet_exercise.py` — 12 offline tests, all
  green: identity-family independence, canonical-required prepare,
  drifted-bridge refusal before any workspace write, missing-record
  byte-pin refusal, skip-typed positive byte-pin at HEAD, contract
  refusal, conductor wiring sequence (context → before → save →
  reloaded → after → dispatch arm B) with receipt-digest pins,
  unrestored-boundary refusal, boundary-drift refusal, authorization
  gate writing nothing, mutation receipts, verify states
  (AUTHORIZATION_UNVERIFIED / ATTEMPT_NOT_VERIFIED /
  MANIFEST_MISMATCH / CANONICAL_FLEET_EXERCISE_VERIFIED).
- Lane suites green at HEAD: exercise+driver 31 passed, dispatch/
  integration/transport 25 passed, reload-only (the q3 no-purchase
  tripwire) + reload-context + failure-reporting + runtime 70
  passed — the frozen reload lane stays unreachable from the
  exercise module.
- Statics: `ruff check`, `ruff format --check`, `py_compile`, scoped
  `uvx ty check` (All checks passed!), `git diff --check` — all
  clean on the two touched paths.
- The frozen `proof/canonical_fleet.py` is byte-untouched; consumed
  q1/q2/q3 identities untouched; all retained evidence byte-verified
  earlier this round (both q3 manifests 0 mismatches).

Not done here: the native attempt itself — it waits for the
preauthorization package (ticket 02) plus a fresh explicit operator
grant; every prior grant is void for reuse.
