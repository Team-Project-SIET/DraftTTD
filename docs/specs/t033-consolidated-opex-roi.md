# T-033 — Consolidated OPEX/ROI with provenance labels (Phase B, P2 backlog)

Goal of record (`docs/roadmap-and-scope-2026-11-05.md` §3, T-033 row):
a consolidated OPEX/ROI record where OPEX, net profit and ROI remain
UNKNOWN until the native receipts exist, and every number carries its
provenance label.

## Dependency map (2026-11-11 audit)

1. Phase B attempt stages T-030/T-031/T-032 built offline (commits
   `c6ec803`, `a9291c2`, `b63eb16`) — DONE; their native attempts are
   separately authorized (packages at the gates) and have NOT run.
2. Attribution machinery of record — DONE (`app/experiments/
   financial_attribution.py`: OBSERVED/DERIVED/HYPOTHESIS/UNKNOWN
   vocabulary, closed ledger category set, UNKNOWN_NOTE discipline;
   `analyze_financial_attribution` + `analyze-continuous-freight` CLI
   exist and stay the per-source analytics of record).
3. Consolidated record stage of record — MISSING → BUILT (commit this
   round): `app/experiments/phase_b_consolidation.py`.

## Design of record

- **Sources of record (fixed):** the four Phase B attempt identities
  (`canonical-fleet-exercise-t030-1`, `canonical-fleet-matched-a/b-
  t031-1`, `canonical-fleet-continuous-t032-1`) plus the E2 canonical
  funding context (`canonical-fleet-create-q3`, OBSERVED capital gift
  delta 400,000 GBP from the retained completed
  `capital-initialize-response.json` readback).
- **Per-source rows:** when the attempt dir does not exist, the row is
  `UNKNOWN_PENDING_NATIVE_AUTHORIZATION` — amounts UNKNOWN, never zero,
  never manufactured. When it exists: status from its own typed
  `result.json`; in-run vehicle-purchase capex OBSERVED from its own
  `canonical-dispatch.json` receipt (the stages construct nothing —
  construction spending OBSERVED-zero; the originals' historical
  construction cost stays UNKNOWN and belongs to the E2 create
  attempt); revenue only when the attempt's own summary carries it
  (OBSERVED); per-year OPEX/ROI DERIVED only from observed native
  accounting in the retained continuous snapshots.
- **OPEX discipline of record (unchanged):** the retained quarterly
  expense aggregate cannot be split through the read API, so
  vehicle-running/loan-interest/property stay UNKNOWN until their own
  native observations exist (`financial_attribution.UNKNOWN_CATEGORIES`).
- **Consolidated totals:** CAPEX total OBSERVED only when every source's
  own receipts exist; otherwise UNKNOWN. Guards verbatim: UNKNOWN_NOTE,
  per-year OPEX/ROI DERIVED only from observed native accounting, no
  per-service revenue implied, no numeric forecast, a positive revenue
  delta alone does not establish profit.
- **Output discipline:** the CLI refuses outputs under the retained
  evidence roots; the generated record goes to a fresh analysis
  directory (this round:
  `artifacts/experiments/phase-b-consolidation-2026-11-11/` —
  `phase-b-consolidated-opex.json` + `.md`, git-ignored like all
  artifacts, reproducible offline any time).

## Current record of record (2026-11-11)

All four native sources `UNKNOWN_PENDING_NATIVE_AUTHORIZATION`;
funding context OBSERVED 400,000 GBP (E2); consolidated CAPEX total
UNKNOWN. The record re-derives offline after each native attempt —
the CLI of record:

```bash
.venv/bin/python -m app.experiments.phase_b_consolidation \
  --output artifacts/experiments/phase-b-consolidation-<date>
```

## Offline regression of record

`tests/test_phase_b_consolidation.py` 6 passed: pending-row honesty
(UNKNOWN not zero), observed capex/revenue labeling from own receipts
(incl. FAILED row status and DERIVED-only-when-verified OPEX/ROI),
E2 funding context, totals/guards, markdown rendering, and the
retained-evidence output guard. Statics clean (ruff, format,
py_compile, scoped `uvx ty`, `git diff --check`).

## Tickets

- `01-consolidation-record.md` — resolved (this commit).
