# 05: Halt-class loop (conditional arm)

**What to build:** the corrective branch of the round-3 machinery. If the
round-3 launch preserved a halt of record, this ticket produces the diagnosis
of record (read-only forensic method of the standing precedent:
source-level root cause with confidence stated, hypothesis matrix
dispositioned, residual unknowns kept UNKNOWN, corrective direction and
regression-lock matrix documented), then the offline fix executed with the
fix-round precedent (one source defect class at a time, every regression
lock the class needs, focused suites + lint/type gates), then re-entry into
ticket 01 as a fresh candidate round with its own operator-gated ladder. If
round 3 delivered, this ticket resolves trivially as "not needed".

**Blocked by:** 04 (Round-3: the one launch). Its "not needed" arm needs
nothing further.

**Status:** in-progress 2026-11-05 — diagnosis-of-record complete (E112),
refined by the 15.3 source pin (E113: one billing mechanism; the +1 is
the start-day rt frame error 47 vs 21); offline fix + fresh-round
re-entry gates remain, each its own explicit operator approval

- [x] Branch decision of record stated from the round-5 outcome (delivered →
      not needed; halt → proceed)
- [x] On the halt arm: preflight of record shows staged bytes untouched by
      the diagnosis; no candidate reconnection; prior terminal verdicts
      unrelabeled; the diagnosis runs read-only on preserved evidence only
- [x] Diagnosis of record: emitter traced exactly, root cause at source
      level with a confidence class, the family precedent cited, ledger +
      status-log records written; consumed identities untouched
- [ ] Offline fix of record: no wire/protocol loosening, no fail-closed gate
      widened, regression locks for the whole defect class (the class must
      fail the suite pre-fix), suites + lint/type gates green,
      `git diff --check` clean, `CONTEXT.md` pin intact
- [x] Cards block: the next candidate round requires the same staging →
      review → signing → launch gates of tickets 01–04, each its own
      explicit operator approval — this ticket authorizes none of them
- [x] Ledger row appended for every executed sub-step; nothing scheduled
      beyond what the operator approves in-session; no commit/push

**Round-5 arm — diagnosis of record (2026-11-05, E112):** branch decision =
proceed (the round-5 launch preserved the terminal halt class
`CARGOFLOW2_FUNDS_DIVERGED` at `arrive-00`; E110). Bounded read-only
forensics executed on preserved evidence only — script of record
`/tmp/opencode/t005_r5_diag_arrive00.py` + transcript
`/tmp/opencode/t005_r5_diag_arrive00_output.txt` (exit 0, tree clean,
manifest 37/37). Emitter traced exactly: the fence of record
(`Cargoflow2FundsModel.reconcile` residual check, `corridor_cargoflow2.py:1599-1617`)
composed by the runner wrapper (`proof/corridor_cargoflow2_native.py:1572`);
the production replay reproduces the retained phase outcome full-field and
the verbatim halt ValueError. **Root cause (CONFIRMED, high — source level):
the fence's day-charge walk diverges from the observed 4-debit native class
at three term level** — (1) model-only start-day partial charge
(rt = 74−27 = 47 → whole 1; native charged nothing pre-first-rollover),
(2) model-only day-230 borrow bonus (the `(fraction − low) % 256` scheme
books whole 2 where the class charges 1), (3) the unmodeled in-window
day-232 rollover (onset tick 270 ≤ read tick 292; the walk books
`range(prev_day, day)`). Closure: modeled 5 − observed 4 == 2 − 1 ==
residual +1. Native-internal mechanism kept UNKNOWN per discipline: two
policies — (A) flat 1 whole coin per rollover with internal retention and
(B) scalar cumulative `floor(421·elapsed/(365·74))` — both reproduce all 11
retained instants exactly; the fix targets the observed trajectory class,
not an asserted internal policy. Family precedent: E111 (method), E97
(funds-window bound); consumed candidate-5 untouched, round-5 verdicts
unrelabeled.

**Round-5 arm — 15.3 source pin (2026-11-05, E113):** the operator chose
"Pin via 15.3 source" and E112's H4 mechanism UNKNOWN is resolved at
tag-15.3 source level. Script of record
`/tmp/opencode/t005_r5_source_pin.py` + wrapper
`t005_r5_source_pin.sh` + transcript
`t005_r5_source_pin_output.txt` (exit 0, 0 failures across V1a–V6,
tree clean, manifest 37/37). **One mechanism of record:** charges fire
in `RoadVehicle::OnNewEconomyDay` (`roadveh_cmd.cpp:1728-1752`,
`running_ticks == 0` gate → `cost = GetRunningCost()·rt//(365·74)`
raw-256ths → `running_ticks = 0` → `SubtractMoneyFromCompanyFract`),
dispatched by the spread day-proc (`vehicle.cpp:921-950`,
`index % 74 == date_fract`, "not in the first tick of the day") after
economy `Elapsed` (`openttd.cpp:1264-1267`;
`timer_game_economy.cpp:131-136`) — vehicle 1 charges on the tick after
its day's roll: **events at `T0+1+74k`**. Kernel
(`company_cmd.cpp:324-336`): one `uint8_t money_fraction` subtracts the
charge's low byte with uint8 wrap, a wrap lends one whole coin,
`whole == 0` silent; display = raw >> 8 (`vehicle_base.h:566`), full
day = 295 raw. **Source walk reproduces the class exactly** (T0=48):
events {49,123,197,271}, rt [21,74,74,74] (first = ticks 28..48, the
start-day partial inside day-712229's event), whole [1,1,1,1], frac
[173,134,95,56], funds 485217 — 11/11 retained instants; robust at
rt_first {20,21,22} and across the T0 sweep [18..48] (31/31 anchors).
**Refined decomposition:** model [1,1,2,1] − source [1,1,1,1] =
[0,0,1,0] — the single delta is the model's day-712230 row (whole 2 vs
1), caused by its start-day rt frame 74−27 = 47 vs the true 21 (a
74−T0 = 26-tick misalignment shifting the fraction phase so that row
borrows early). H4 A/B superseded (neither A's {48,122,196,270} nor B's
{92,156,220,284}); H1/H2 refined (the start-day partial is source-true
inside day-712229's event; the borrow kernel is genuine and the
model's `whole 2` is the same borrow at a phase-shifted frame); H3
confirmed (the in-window day-712232 event, tick 271, is a real fourth
debit the model never books). Fix direction is now source-precise: the
funds-model day-walk moves to the charge-event frame (kernel
arithmetic unchanged; regression locks the whole class needs).

**Cards block of record (next candidate round):** the round-6 cycle
re-enters ticket 01's ladder with a fresh identity — pipeline constant
`candidate-5` → `candidate-6`, ONE staging `prepare`; then fresh
independent review (ticket 02 method), Gate C signing (ticket 03), ONE
launch (ticket 04) — four separate operator approvals, none authorized by
this ticket; settle-then-freeze: all remaining doc/vocabulary writes land
and are committed before round-6's identity advance.
