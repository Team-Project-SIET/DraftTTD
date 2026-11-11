# 01: Consolidated OPEX/ROI record (T-033)

**Type:** task
**Status:** resolved 2026-11-11 (commit this round)
**Spec:** `docs/specs/t033-consolidated-opex-roi.md`

**What to build:** the consolidated OPEX/ROI record of record —
`app/experiments/phase_b_consolidation.py` aggregating the four Phase B
attempt identities plus the E2 funding context with provenance labels
(OBSERVED/DERIVED/UNKNOWN per `financial_attribution`'s vocabulary);
native receipts that do not exist yet stay
`UNKNOWN_PENDING_NATIVE_AUTHORIZATION` (never zero, never
manufactured); OPEX categories stay UNKNOWN until their own native
observations exist; consolidated CAPEX total OBSERVED only when every
source's own receipts exist; offline CLI writing JSON+markdown to a
fresh non-retained directory with a retained-evidence output guard.
Offline regression `tests/test_phase_b_consolidation.py`. Generate the
current record over the retained receipts of this date.

**Blocked by:** nothing (the record is honest at any completion state;
it re-derives offline after each native attempt).

## Answer

Resolved. Module + 6 offline tests; the current generated record of
record lives at `artifacts/experiments/phase-b-consolidation-2026-11-11/`
(all four sources UNKNOWN-PENDING; E2 funding context OBSERVED 400,000
GBP; consolidated CAPEX UNKNOWN). Statics clean. Zero launches; zero
AdminPort; no retained `artifacts/` byte touched (only the new
analysis directory was created).
