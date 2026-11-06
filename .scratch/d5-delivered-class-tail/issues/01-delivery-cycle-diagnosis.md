# 01: Read-only delivery-cycle diagnosis

**What to build:** the diagnosis of record for the terminal in-transit
class — why every corridor attempt loads and departs but never delivers —
executed read-only over the retained bytes, per the E105/E112 method.

**Blocked by:** nothing (spec front). **Blocked-to:** 02 (the offline fix)

**Status:** ready-for-agent

- [ ] Retained timelines assembled read-only: round-6 and round-7
      `phase.receipts` rows (days 712,228…712,287), the load rows
      the load rows (5/10/15 at day 712,271 + 20 at 712,272,
      day-converted via `date = 712,229 + floor((tick − 48) / 74)` with `DAY_TICKS = 74`),
      the loaded departure (20 t at day 712,274), and the finish instant
      (day 712,287, tick 4,342) with `unloadings []`
- [ ] Hypotheses dispositioned with dispositions of record: at minimum —
      (a) the ladder carries no unload/cycle-completion observation stop
      (the 25-exchange ladder ends at anchor+55 before the cycle can
      close); (b) the delivery leg's transit time exceeds the remaining
      report window (50,095 in transit at finish, 13 days after
      departure); (c) any bay-acceptance/attraction condition the
      GameScript surface would need for the unload rows to appear
- [ ] The fix space derived from the dispositions (ladder/observation
      extension inside the 60-day authority; schedule_version advance;
      delivered-class verdict typing) — bound to no pin modification,
      zero v1 byte drift; residual unknowns recorded UNKNOWN, never
      fudged
- [ ] Books of record: ticket file + backlog row + E-row for the
      diagnosis; read-only over `artifacts/` (zone re-hash byte-stable);
      `git diff --check` clean; `CONTEXT.md` pin `847d710a…984d` intact;
      one commit, no push
