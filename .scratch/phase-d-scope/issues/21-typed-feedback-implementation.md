# 21: Typed feedback implementation

Type: task
**What to build:** ticket 06's decided policy, implemented: opt-in flags at plan time seed P05 cost assumptions only from verified P07 evidence classes, every seeded assumption recorded in the plan contract with its evidence class, provenance label, and source digest — and default behavior byte-unchanged. From the operator's perspective: "Optimization" is real, opt-in, and never automatic.

**Blocked by:** 06 (typed-feedback policy decision) and the first verified backbone cycle (any of 24/25/26 producing one — the evidence input this ticket consumes).

**Status:** ready-for-agent
**Gates:** implementation starts only after M0 approval and only once the evidence input exists; validation rides the backbone's verified-cycle receipts, never a separate native round; no commit.

- [ ] Opt-in flags implemented exactly as ticket 06 decided; default path proven byte-unchanged (pin tests).
- [ ] Every seeded assumption carries its evidence class, provenance label, and source digest in the plan contract.
- [ ] "Never automatic" negative tests green: no parameter change between cycles, no retraining, no UNKNOWN promoted to a number.
- [ ] Suites green; no native authority consumed; no commit.
