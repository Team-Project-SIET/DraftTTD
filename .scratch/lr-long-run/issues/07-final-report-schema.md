# 07 — Final report schema and P07 integration

Type: wayfinder:grilling (HITL)
Blocked by: 02 (journal schema), 03 (incremental manifest + verify)

## Question

Decide the LR final report's schema and its P07 integration as reviewable
design criteria (not code) — the deliverable that makes the 2 h run's history
human-reviewable and machine-verifiable.

The decision must fix, as reviewable criteria:

1. The report sections of record covering the required fields:
   infrastructure, vehicles, cargo, delivery, finances, failures, and planner
   decisions — each section naming its source evidence class (journal events,
   receipt shapes, checkpoints) and its OBSERVED/DERIVED/UNKNOWN label policy.
2. The economics presentation under D14: per-cycle/monthly/annual rows derived
   offline from receipts; aggregate-only OPEX with categories UNKNOWN;
   `compare_arms` guards carried verbatim (revenue ≠ profit; no per-service
   revenue implication; no forecast; UNKNOWN is not zero).
3. The measured-outcome presentation under D1: in-game years, game-time
   progression, pause accounting, and cycle statistics reported as measured
   facts — the expectation band never restated as a result.
4. The machine-verifiable companion: the report's every number carries its
   source digest; the verify command of record (ticket 03) validates the
   report's inputs; P07 reuse boundary (which P07 outputs extend vs which are
   replaced, additive-only over the frozen families).
5. The identity discipline: the report derives under a new identity per run
   (never relabeling any prior record); the offline derivation re-runs
   byte-deterministically (the E204 successor-derivation pattern).

Constraints: design-only; no code; retained receipts byte-untouched; the
report consumes only verified evidence — no UNKNOWN is promoted anywhere.
