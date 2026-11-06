# 01: Read-only delivery-cycle diagnosis

**What to build:** the diagnosis of record for the terminal in-transit
class — why every corridor attempt loads and departs but never delivers —
executed read-only over the retained bytes, per the E105/E112 method.

**Blocked by:** nothing (spec front). **Blocked-to:** 02 (the offline fix)

**Status:** done 2026-11-06 (the round granted in-session as the frontier
instruction "do next move"; read-only over the retained bytes and the live
module surface — no staging, no claim, no signature, no launch, no native
run; the diagnosis script `/tmp/opencode/t01_delivered_class_diagnosis.py` +
transcript `/tmp/opencode/t01_delivered_class_diagnosis_output.txt` —
**19/19 PASS, 0 FAIL**)

**The diagnosis of record — root cause: the plan's ladder composition, not
any world or machinery defect:**

- **(a) PROVEN — no cycle-completion observation exists.** The 25-exchange
  ladder ends `flow-11`/`finance-00`/`finish-00` all at anchor+55 = day
  712,287 (`CARGOFLOW2_FLOW_OFFSETS = tuple(range(0, 60, 5))`,
  `CARGOFLOW2_SPAN_DAYS = 55`); no unload/delivery observation exchange
  exists anywhere in the ladder, so the delivery cycle cannot be *observed
  completing* inside the authored plan.
- **(b) PROVEN — the loaded return misses the final stand by 2-3 days.**
  Round-7 trace of record: loaded departure 712,274; (175,178) @712,277
  (load 20; the empty bay→pickup leg ran 19 days round-6 / 20 days
  round-7); (175,186) @712,282; (175,195) @712,287 — still carrying 20 t,
  ~4 straight-tile units short of the bay (174,198) at the observed crawl
  (~9 tile rows per 5-day window, spd 38-48). Bay arrival ETA ≈
  712,289-712,290 = anchor+57/+58 > +55. The run ended before the vehicle
  could arrive and unload.
- **(c) PRESENT + PREEMPTED — the acceptance machinery is not defective.**
  The GameScript awards unload latches per (day, tick) (`main.nut`
  `kind = "unload"` + `GSCargoMonitor.GetIndustryDeliveryAmount`) and the
  wire surface (`corridor_cargoflow2.py` ~1910) maps the unloaded latch
  kind into `phase.unloadings`; **the delivered verdict class is already
  typed** — `CARGOFLOW2_DELIVERY_VERIFIED` with the seven §7 criteria
  (~2060-2100) — so the two runs' `unloadings []` is the preempted outcome
  of (a)+(b), never a missing row class.
- **Fix space of record (the 02 decision space):** extend the flow ladder
  by the minimal interval — `range(0, 60, 5)` covers 0..55 under the
  60-day authority framing, i.e., the ladder currently stands **one
  interval short of its own authority**; extending through anchor+60 (day
  712,292) observes the post-ETA arrival (+57/+58) with a 2-3-day settle
  margin while holding the authority line. The `schedule_version`/digest
  advance and the funds fence's two new instants (the E113 walk across
  712,289…712,292, the fence-extension arm) are ticket-02's composition;
  the delivered typing needs no code change — ticket-02's delivered lock =
  acceptance of the existing class only.

- [x] Retained timelines assembled read-only: round-6 and round-7
      `phase.receipts` rows (days 712,228…712,287), the load rows
      (5/10/15 at day 712,271 + 20 at 712,272, day-converted via
      `date = 712,229 + floor((tick − 48) / 74)` with `DAY_TICKS = 74`),
      the loaded departure (20 t at day 712,274), and the finish instant
      (day 712,287, tick 4,342) with `unloadings []`; per-exchange
      response `location`/`load`/`speed` reads assembled the full vehicle
      trace of record for both arms
- [x] Hypotheses dispositioned with dispositions of record: (a) the
      ladder carries no unload/cycle-completion observation stop — PROVEN
      from the ladder layout; (b) the delivery leg's transit time exceeds
      the remaining window — PROVEN from the trace arithmetic above;
      (c) the bay-acceptance/attraction condition — PRESENT + PREEMPTED,
      not defective
- [x] The fix space derived from the dispositions (ladder/observation
      extension through anchor+60 inside the 60-day authority;
      schedule_version advance; delivered typing already present) —
      bound to no pin modification, zero v1 byte drift; residual
      unknowns recorded UNKNOWN (the exact unload-latch instant vs the
      observation cadence — the run's own receipts decide it, never
      assumed), never fudged
- [x] Books of record: ticket file + backlog row + E-row (E128) for the
      diagnosis; read-only over `artifacts/` (zone re-hash byte-stable);
      `git diff --check` clean; `CONTEXT.md` pin `847d710a…984d` intact;
      one commit, no push
