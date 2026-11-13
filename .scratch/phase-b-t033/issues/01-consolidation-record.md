# 01: Consolidated OPEX/ROI record (T-033)

**Type:** task
**Status:** resolved 2026-11-11 (commit this round); RE-DERIVED
2026-11-12 after Phase B native closure — the current record of record
is `artifacts/experiments/phase-b-consolidation-2026-11-12/` (all four
sources VERIFIED, 0 UNKNOWN-PENDING; consolidated vehicle-purchase
CAPEX 8,858 GBP OBSERVED = T-030's £4,429 + arm B's £4,429 + arm A £0
+ T-032 £0; revenue OBSERVED from the arms'/continuous's own
`freight_revenue` — arm A 50,940 / arm B 68,383 / T-032 50,940;
T-030 revenue UNKNOWN (its flow retains no arm-record-style financial
summary); OPEX/ROI DERIVED for the arms + T-032 from their own
financial metrics, UNKNOWN for T-030; OPEX categories stay UNKNOWN
until their own native observations exist — the guards and the
UNKNOWN-is-not-zero rule carried intact; no profit claim). The
re-derivation also fixed a latent key mismatch: the module read
`income`, the real receipts key `freight_revenue` (the
`financial_attribution` vocabulary of record) — module + test updated,
6 offline tests pass, ruff/format clean. Zero launches; zero
AdminPort; no retained `artifacts/` byte touched (only the new
analysis directory was created)
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
