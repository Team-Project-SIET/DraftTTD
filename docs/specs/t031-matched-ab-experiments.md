# T-031 — Matched A/B experiments (Phase B, P2 backlog)

Canonical fleet lane of record (E2 family). Goal of record
(`docs/roadmap-and-scope-2026-11-05.md` §3, T-031 row): matched A/B
experiments as separately authorized arms from the same verified canonical
state; done-ness = descriptive comparison record with per-arm receipts +
E-row. Attempt 19 is context only, never a matched arm. Design of record:
`docs/capacity-experiment.md` (A/B contract lines 40–56, canonical
qualification lines 109–234, bounded telemetry lines 295–334).

## Dependency map (2026-11-11 audit)

1. Phase A closed (T-022, E127) — DONE.
2. E2 canonical evidence — DONE (create-q3 + reload-q3, manifests
   re-verified 0 mismatches 2026-11-11; protected save sha256
   `51e45689ae40dfa53c2cc150a05076fcb6e5cc2f38ec4eff56908372ab1297eb`).
3. T-030 exercise stage (commit `c6ec803`) — DONE; its stage core
   generalized this round into the same module so matched arms reuse it
   (default-behavior preserving; T-030 contract, identity and receipts
   unchanged in substance).
4. Matched arms stage of record — MISSING → BUILT (commit `a9291c2`):
   `app/simulation/openttd/proof/canonical_fleet_matched.py`.
5. Gate ladder for the TWO native attempts (arm A, then arm B; each a
   separate staged candidate → preflight PASS → verify →
   AUTHORIZATION_UNVERIFIED/CLAIM_ABSENT → independent review → Gate C
   signing → fresh explicit ONE-launch authorization per arm) —
   OFFLINE preparable; the launches are operator-gated.
6. Post-run: per-arm receipts + arm records + descriptive comparison +
   E-row (after item 5's authorizations).

## Design of record (arms)

- **Same start state, same bridge.** Both arms stage from the SAME E2
  created evidence (`canonical-fleet-create-q3`) under the SAME
  byte-pinned bridge package (`freight.staged_package(True, True, True,
  "high-budget-500k", 3, 5, canonical=True)`; `package_bytes()` ↔
  suspension.json package byte-pin holds at HEAD). The pinned
  `canonical-parent.nut` already carries the full
  `continuous-begin/company/service/telemetry` producer set, so the arms
  run telemetry without changing package bytes.
- **Identities, never shared:** arm A `canonical-fleet-matched-a-t031-2`
  (attempt 1 `canonical-fleet-matched-a-t031-1` terminal FAILED sealed
  E183 — the armed seal killed the script on the post-dispatch
  `continuous-begin`; stale-supersession advanced the identity; fix
  round E184),
  arm B `canonical-fleet-matched-b-t031-1` (re-prepare with the E184
  fixed package before its grant; the pre-fix staging is superseded
  unsealed state); each its own CLAIM and its
  own fresh explicit authorization (not shared with the T-030 exercise,
  with each other, or with any earlier attempt; all prior grants void).
- **Arms:** arm A adds nothing (three original vehicles); arm B adds only
  its service-1 vehicle via the paused capacity-add intervention
  (`dispatch_loaded_arm(arm="B")` path). Both arms dispatch (the
  originals' reload correspondence is proven first in every arm).
- **Horizon:** five native economy anniversaries (EconomyProgress
  targets) via the retained `freight_continuous.monitor_network` loop;
  telemetry version 2 (`vehicle_count` 3 for A / 4 for B,
  `max_tick_gap=100`); budgets
  `freight.network_budgets(3) | monitoring_budgets(count)`.
- **Receipts of record:** per-service receipts in the retained continuous
  evidence shape; in-run construction spending OBSERVED-zero (the arms
  construct nothing); the originals' historical construction cost stays
  UNKNOWN and belongs to the E2 create attempt's receipts, never to an
  arm; arm-B `additional_vehicles` carries the OBSERVED fourth-vehicle
  capex.
- **Result of record:** typed `CANONICAL_FLEET_MATCHED_VERIFIED` per arm;
  `compare_arms` produces a DESCRIPTIVE B-vs-A record (OBSERVED deltas,
  UNKNOWN preserved, no profit claim, no per-service revenue implication,
  no forecast) — OPEX/ROI stay UNKNOWN until their own provenance exists.

## Execution contract of record (each arm)

- Fresh attempt identity per arm; one launch, one connection, no
  retry/reconnect; stop on unexpected failure; receipts retained whatever
  the outcome; nothing relabeled.
- Reload correspondence first (`establish_reload_context` →
  `reload-before` → `protected_save` → `verify_reloaded` → stable
  boundary), then the ONE dispatch, then the monitored five-year loop,
  then `arm-record.json` with provenance labels.
- Preparation never launches or connects; `verify` offline (typed states
  `AUTHORIZATION_UNVERIFIED` / `ATTEMPT_NOT_VERIFIED: …` /
  `CANONICAL_FLEET_MATCHED_VERIFIED`).

## Offline regression of record (commit `a9291c2`)

`tests/test_canonical_fleet_matched.py` 11 passed: identity-family
independence; prepare refusals; a REAL offline arm-B staging (workspace,
endpoints, OpenGFX, seal with telemetry/budgets assertions); receipt
shapes + `telemetry_options` derivation (3 vs 4 bindings); conductor
wiring with the monitor seam; missing-dispatch refusal; authorization
gate writing nothing; comparison record incl. UNKNOWN labeling and
swapped-arm refusal; verify states.
`tests/test_canonical_fleet_exercise.py` 14 passed (generalized core,
default behavior preserved). Lane suites green: driver/dispatch/
integration/transport, reload-only/context/failure/runtime,
continuous/matched-state/telemetry. Statics clean (ruff, format,
py_compile, scoped `uvx ty`, `git diff --check`).

## Retained-VM-helper pin fix (latent prepare blocker, closed same commit)

The q3-era `suspension.json` helper pins bind the RETAINED q3 frozen-source
bytes (`tests/support/canonical_protocol_vm.nut` drifted post-q3 via the
E92 readback-fidelity fix — live digest `ad96fd42…` vs the record's
`8353a172…`), so the old check would have refused EVERY fresh prepare at
grant time. The record's package byte-pin still matches exactly.
`require_retained_vm_helpers` now verifies the record's helper digests
against the retained stage-sealed `frozen-source.zip` (fail-closed evidence
integrity), while the live tree's newer helpers are sealed per-stage in
the stage's own frozen-source seal. The frozen driver's identical check is
left byte-untouched: consumed q3 identities are never re-prepared.

**E184 update:** the fix round regenerated the VM record as
`artifacts/validation/canonical-fleet-reload-q4/suspension.json` (25/25
cases rc 0 at the pinned exact 15.3 Squirrel source commit
`14ec60f248547d4d062a1160f0fc26d742319888`; q3 dir untouched) for the
fixed package bytes (armed seal now lets the observation-only
`continuous-*` family through), and re-pointed the retained-provenance
zip to the t031-1 attempt's stage seal — its 4 VM_HELPER entries are
byte-identical to the q4 record's pins (the q3 zip matched only 3/4,
helpers having evolved since the q3 era). `SUSPENSION_VALIDATION` now
points at q4; the q3 record stays retained history.

## Tickets

- `01-arms-conductor.md` — resolved (`a9291c2`).
- `02-arm-a-attempt-package.md` — prepared at the authorization gate.
- `03-arm-b-attempt-package.md` — prepared at the authorization gate.
