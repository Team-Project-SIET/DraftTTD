# T-032 — Five-year continuous operation experiment (Phase B, P2 backlog)

Canonical fleet lane of record (E2 family). Goal of record
(`docs/roadmap-and-scope-2026-11-05.md` §3, T-032 row): a five-year
continuous operation experiment with its own finalization contract;
done-ness = per-year OPEX/ROI DERIVED only from observed native
accounting + E-row. Attempt 19 is context only (terminal FAILED, E3);
its offline recovery (`artifacts/experiments/attempt19-offline-recovery/`,
`docs/five-year-freight-performance-analysis.md`) is separate and not a
precedent for this contract. Spec: `docs/specs/t031-matched-ab-experiments.md`
is the arms sibling; this stage is the single-arm continuous sibling.

## Dependency map (2026-11-11 audit)

1. Phase A closed (T-022, E127) — DONE.
2. E2 canonical evidence — DONE (manifests re-verified 0 mismatches
   2026-11-11).
3. T-030/T-031 stage core generalized (commits `c6ec803`, `a9291c2`) —
   DONE; the retained continuous machinery
   (`freight_continuous.monitor_network`, `EconomyProgress`,
   `period_reports`, `continuous_summary`,
   `verify_continuous_evidence`) is offline-green at HEAD.
4. Five-year continuous stage of record — MISSING → BUILT (commit
   `b63eb16`): `app/simulation/openttd/proof/canonical_fleet_continuous.py`.
5. Gate ladder for the ONE native attempt (staged candidate → preflight
   PASS → verify `AUTHORIZATION_UNVERIFIED` → independent review →
   Gate C signing → fresh explicit ONE-launch authorization) — OFFLINE
   preparable; the launch is operator-gated.
6. Post-run: continuous summary + finalization record + analytics +
   E-row (after item 5's authorization).

## Design of record

- **Identity of record:** `canonical-fleet-continuous-t032-1`; own
  CLAIM; fresh explicit authorization never shared with the T-030
  exercise, the T-031 arms, or any earlier attempt.
- **Same start state, same bridge:** stages from the SAME E2 created
  evidence under the SAME byte-pinned bridge package
  (`package_bytes()`), whose pinned `canonical-parent.nut` already
  carries the full `continuous-begin/company/service/telemetry` producer
  set.
- **The stage adds nothing:** arm-A-shaped dispatch (three original
  vehicles, `purchase=False`); reload correspondence proven first.
- **Horizon:** five native economy anniversaries (EconomyProgress
  targets) via the retained `monitor_network` loop, which writes
  `continuous-summary.json` (`continuous_summary`:
  classification `NATIVE_FIVE_YEAR_CONTINUOUS`, five complete economy
  years, `reconcile_snapshots` financial metrics, observation counts).
  Telemetry version 2 (`vehicle_count=3`, `max_tick_gap=100`); budgets
  `freight.network_budgets(3) | monitoring_budgets(3)`.
- **Finalization contract of record:** `continuous-finalization.json`
  binding the retained summary plus provenance labels — classification
  `NATIVE_FIVE_YEAR_CONTINUOUS`; per-year OPEX/ROI DERIVED only from the
  observed native accounting in the retained continuous snapshots (never
  manufactured); the originals' historical construction cost stays
  UNKNOWN and belongs to the E2 create attempt's receipts;
  fourth-vehicle capex NOT-APPLICABLE.
- **Result of record:** typed `CANONICAL_FIVE_YEAR_CONTINUOUS_VERIFIED`.

## Execution contract of record (the attempt)

Fresh attempt identity; one launch, one connection, no retry/reconnect;
stop on unexpected failure; receipts retained whatever the outcome
(`continuous-partial.json` is written by the monitor's `finally` on any
early exit and stays part of the retained evidence); nothing relabeled.
Preparation never launches or connects.

## Offline regression of record (commit `b63eb16`)

`tests/test_canonical_fleet_continuous.py` 7 passed: identity
independence (incl. all consumed identities), prepare refusals, a REAL
offline staging (seal/telemetry/budgets assertions), conductor wiring
with the monitor seam + plan copies + finalization provenance pins,
missing-dispatch refusal, authorization gate writing nothing, verify
states. Exercise 14 + matched 11 stay green; lane suites green
(driver/dispatch/integration/transport, reload-only/context/failure/
runtime, continuous/matched-state/telemetry). Statics clean (ruff,
format, py_compile, scoped `uvx ty`, `git diff --check`).

## Ticket

- `01-continuous-attempt-package.md` — prepared at the authorization
  gate.
