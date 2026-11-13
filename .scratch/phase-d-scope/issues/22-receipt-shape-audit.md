# 22: Receipt-shape audit (WS-D5)

Type: task
**What to build:** a typed receipt-shape table of record for verified loop cycles: which retained receipt shapes carry which P&L-relevant facts (freight revenue, vehicle running cost, cash delta), what is OBSERVED vs DERIVED vs absent. From the operator's perspective: the economics workstream's inputs are named before anything is derived.

**Blocked by:** the first verified backbone cycle (any of 24/25/26 producing one).

**Status:** ready-for-agent
**Gates:** implementation starts only after M0 approval and a verified cycle exists; the audit consumes no native round; retained receipts byte-untouched; no commit.

- [ ] Audit record over ≥1 verified cycle's retained receipts: a per-shape fact table with evidence-class labels.
- [ ] Every P&L-relevant fact named with its source; absent facts typed absent (UNKNOWN stays UNKNOWN).
- [ ] The record lands under a new identity; retained receipts byte-untouched.
- [ ] No new native round consumed by this audit; no commit.
