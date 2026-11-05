# 12: P07 replay closure (T-021b)

**What to build:** the corridor reporting closure — the reporting/evaluation
layer run fresh on the corridor lineage's terminal evidence, replayed into a
sibling output (never overwriting prior outputs): per-service totals,
charts and operational history with world/seed/plan attribution intact,
OBSERVED native measurements kept distinct from DERIVED aggregates and
CONTROLLED inputs, comparisons carrying distinct seed/config/experiment
identities, and the unmeasured categories staying UNKNOWN under the taxonomy
of record from ticket 11.

**Blocked by:** 11 (Funds-taxonomy decision).

**Status:** ready-for-agent

- [ ] Fresh sibling output directory of record produced by the evaluation
      machinery's replay arm — no historical output overwritten, no retread
      of old receipts as new
- [ ] The delivered attempts' native receipts replayed — the two-route
      corridor lineage's receipt set (round-3-class and selected-route
      attempts) reaches evaluation with its identities intact
- [ ] Attribution asserted: every chart/total/history row carries its
      world/save/seed/plan identity provenance; failed plannings retain
      diagnostics, never delivery receipts
- [ ] The OBSERVED/DERIVED/CONTROLLED/UNKNOWN discipline asserted in the
      outputs (labels travel with the numbers; revenue is never printed as
      profit; milestone rates labeled as script-tick rates)
- [ ] Comparisons of record keep distinct identities (no conflation across
      lineages; the fixed-demo baseline stays distinct from the corridor
      runs)
- [ ] Focused evaluation suites + lint/type gates green; `git diff --check`
      clean; `CONTEXT.md` pin intact; ledger row appended; no commit/push
