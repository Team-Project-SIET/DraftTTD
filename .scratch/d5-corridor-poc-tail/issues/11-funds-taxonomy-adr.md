# 11: Funds-taxonomy decision (T-021a)

**What to build:** the operator's funds taxonomy decision recorded as an
ADR-class document — the running-cost category under the halt-on-unexplained-
drift rule settled once, with the reporting rules pinned for the corridor
experiments: operating expense categories are observed native cash deltas
only, derived aggregates stay labeled DERIVED, unmeasured categories stay
UNKNOWN, revenue is timing-dependent and never reported as profit. The
decision is the operator's; this ticket drafts the record, surfaces any
decision options, and lands the confirmation — it never licenses new
mutation.

**Blocked by:** 10 (Selected-route delivered attempt).

**Status:** ready-for-agent

- [ ] Draft decision record exists: the taxonomy of record (the model's
      category set: exact purchase debit, monthly interest + station fees at
      the economy-month boundaries, per-day running cost through the exact
      8.8 carry from the pinned display figure, income at the same
      observation instants, the halt-on-unexplained-drift fence), its
      alternatives rejected, and its consequences for reporting
- [ ] Each fact of record separated OBSERVED / DERIVED / CONTROLLED in the
      draft — with the UNKNOWN set enumerated (unallocated cash decreases
      don't establish OPEX categories beyond the fence)
- [ ] The draft binds rounds of record (round-3 and second-route receipts of
      the corridor lineage) as its evidence anchors
- [ ] Operator confirmation session held; the decision confirmed inline;
      the record marked decision-of-record (ADR-class) — no further edit
      without a supersession of record
- [ ] Reporting vocabulary of record pinned for ticket 12: the label set,
      the attribution rules (world/seed/plan), the comparison-identity rules
- [ ] Ledger row appended; `git diff --check` clean; `CONTEXT.md` pin
      intact; no commit/push
