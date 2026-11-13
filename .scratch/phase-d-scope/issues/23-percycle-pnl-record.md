# 23: Per-cycle P&L record (WS-D5)

Type: task
**What to build:** per-cycle P&L derived offline from the verified loop's retained receipts under a new identity: freight revenue, vehicle running cost, cash delta per cycle — extending the consolidated OPEX/ROI pattern to the random world, every number labeled with its source digest. From the operator's perspective: economics exist without spending a single native round.

**Blocked by:** 22 (receipt-shape audit).

**Status:** ready-for-agent
**Gates:** implementation starts only after M0 approval and the audit of record; no native round consumed; artifacts untouched; no commit.

- [ ] Derivation record under a new identity (never relabeling any prior record); per-cycle rows for each verified cycle.
- [ ] Every number carries an OBSERVED / DERIVED / UNKNOWN label plus its source digest; OPEX categories and ROI stay UNKNOWN wherever no native accounting observation exists.
- [ ] The derivation re-derives offline from the retained receipts (replay/verify shape).
- [ ] No native round consumed; retained artifacts untouched; no commit.
