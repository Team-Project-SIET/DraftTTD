# 01: Matched A/B arms conductor

**Type:** task
**Status:** resolved 2026-11-11 (commit `a9291c2`)
**Spec:** `docs/specs/t031-matched-ab-experiments.md`

**What to build:** the T-031 matched A/B arms stage of record —
`app/simulation/openttd/proof/canonical_fleet_matched.py` (thin reuse of
the T-030 stage core generalized inside
`canonical_fleet_exercise.py`): identities
`canonical-fleet-matched-a/b-t031-1` with their own matched contracts
(arm A adds nothing; arm B adds only its service-1 vehicle), prepare
staging both arms from the same E2 canonical evidence under the same
byte-pinned bridge package with telemetry version 2 (vehicle_count 3/4,
max_tick_gap 100) and budgets
`network_budgets(3) | monitoring_budgets(count)`, arm receipts in the
retained continuous evidence shape (in-run construction spending
OBSERVED-zero; originals' historical construction cost stays UNKNOWN and
belongs to the E2 create attempt), conduct = reload correspondence then
ONE `dispatch_loaded_arm(arm)` then the retained
`freight_continuous.monitor_network` five-anniversary loop then
`arm-record.json` with provenance labels, typed
`CANONICAL_FLEET_MATCHED_VERIFIED`; `compare_arms` descriptive B-vs-A
record (OBSERVED deltas, UNKNOWN preserved, no profit claim, no
per-service revenue implication, no forecast); CLI
prepare/preflight/verify/run/compare with `--arm A|B`. Offline
regression `tests/test_canonical_fleet_matched.py` (11 tests incl. a
real offline arm-B staging). No launch; no `artifacts/` byte modified.

**Blocked by:** nothing (T-030 stage core DONE at `c6ec803`).

## Answer

Resolved by commit `a9291c2`. Stage core generalized in
`canonical_fleet_exercise.py` (prepare/preflight/verify/run/conduct take
identity/contract/budgets/capacity_telemetry/authorization/conduct
params; T-030's own contract, identity and receipts unchanged in
substance; its 14 tests stay green). The real offline staging test
exposed a latent prepare blocker — the q3-era helper pins bind the
RETAINED q3 frozen-source bytes (`canonical_protocol_vm.nut` drifted
post-q3 via the E92 readback-fidelity fix) — fixed by
`require_retained_vm_helpers` verifying the record's helper digests
against the retained q3 `frozen-source.zip` (fail-closed) while live
helpers are sealed per-stage; the frozen driver's identical check stays
byte-untouched (consumed q3 identities never re-prepared). Tests: 14
exercise + 11 matched; lane suites (driver/dispatch/integration/
transport, reload-only/context/failure/runtime, continuous/
matched-state/telemetry) green; statics clean (ruff, format,
py_compile, scoped `uvx ty`, `git diff --check`). Zero launches; zero
AdminPort; no `artifacts/` byte touched.
