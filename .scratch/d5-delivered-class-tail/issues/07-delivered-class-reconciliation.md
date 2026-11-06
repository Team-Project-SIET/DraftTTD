# 07: Delivered-class reconciliation

**What to build:** the offline truth replay of record over the delivered
class (or the terminal state T-06 actually produced) — unload-chain
reconciliation, funds fence across the unload leg, labels of record —
read-only, one replay invocation.

**Blocked by:** 06. **Blocked-to:** 08 (the E36 closure decision)

**Status:** ready-for-agent

- [ ] Load → departure → arrival → unload-attraction → bay-acceptance
      chain reconciled rows-verbatim from the retained result; funds
      fence zero-residual at every observed instant (any residual finding
      of record, never normalized); ADR-0001 labels travel; day/tick
      figures script-tick, never steady-state
- [ ] If the delivered class landed: the DELIVERED verdict's own facts
      of record booked (unload rows, cycle day figures, final funds); if
      a halt landed instead: this ticket is N/A for its class and the
      sibling loop carries the round — recorded, not stretched
- [ ] The E114 comparison's figures ride read-only as observed (the twin
      figure vs the native close) and stay UNKNOWN — never reconciled by
      hand, never closed here
- [ ] Reconciliation verdict of record (`T09-CLASS RECONCILIATION PASS`-
      shaped) with script + transcript outside the repo; `git diff
      --check` clean; `CONTEXT.md` pin intact; one commit, no push
