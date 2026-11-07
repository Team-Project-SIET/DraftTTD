# Random World capture pacing — decision of record (ticket 03 family, M2 window)

Date: 2026-11-07. Status: **decided** (offline; no native run this round). This
decision was taken by explicit operator task in the Phase C continuation round
of the ramrom map (`.scratch/ramrom-product/`), recorded here so the next
native attempt has one pacing design with fixed settings and fences.

## 1. The constraint of record

The qualified-month integrity gate never changed and was never in issue:
every supplemental planning read must satisfy, at its own capture instant,
`month.start_date <= before <= after < month.end_date`
(`app/simulation/openttd/supplemental_planning_facts.py:262`, typed
`PlanningFactError: supplemental capture outside final M2 month`). E141's
widened-seal run on seed 2026 typed that refusal mid-capture (n1 interrupted
at read 703) because the wall time of a 2048-tile capture scales with the
AdminPort round-trips (tiles + catchment + industries + status) and the live
game clock races it. n0 (832 reads) completed inside the month; the failure
mode is a scale race, not a contract error, and a budget reduction would only
re-introduce the E139 starvation of freight pairs.

## 2. Decision: pause the world clock during each supplemental capture

**Option A is chosen of record.** Each relationship capture runs with the
world clock paused, started from the owned console immediately before the
capture and resumed in a `finally` the moment the capture ends (success or
typed failure). The gate stays byte-identical and integrity-correct: a paused
clock records `before == after` inside the qualified month for every captured
fact, so the E141 race cannot occur at any capture-profile size. The
implementation surface of record is `paused_world_clock()` in
`app/simulation/openttd/freight_native_network.py`, wired around every
random-world supplemental capture in `_plan_network_world` and counted per
pair in the planning diagnostic (`pause_pairs`, `pause_resume_error`).

Rejected alternatives, for the record:

- **B — capture page-critical tiles first** (research §9 candidate 2): it
  shortens nothing structurally; with several relationships per attempt the
  total read mass still races the month, and it silently reorders capture
  evidence, which the bounded-capture discipline does not permit. Cost of
  change comparable to A for a weaker guarantee.
- **C — widen the qualified-month contract**: rejected outright. The M2 gate
  is the qualification identity of record; loosening it to fit cost would
  steal guarantee from integrity and invalidate the retained qualification
  semantics of every prior attempt.

## 3. Bounded capture settings of record

1. **One pause/resume pair per relationship capture.** No other state or
   command may pause the clock; no pause happens during qualification
   observation, planning, building, delivery or verification.
2. **The wall-clock budgets never change.** `capture_budget.capture_seconds`
   and the attempt's scaled `total_seconds` still bound the attempt (pause is
   a console ordering, not extra time); a capture that overruns its own
   deadline still types `CAPTURE_TIME_BUDGET`.
3. **The pause is unobservable to planning facts.** While paused, every read
   snapshots the same economy instant; the retyped facts keep their
   capture-window bracket (`before == after`, inside the month), so replay,
   correspondence and P05 inputs are unchanged in shape.
4. **Loop cycles inherit it automatically**: the pacing applies inside every
   cycle's re-capture on the live world, since the wiring sits in
   `_plan_network_world`, which each loop cycle re-enters.

## 4. Per-attempt evidence fences

1. The attempt's planning diagnostic must record
   `pause_pairs == captured_relationships` and must not record
   `pause_resume_error`; a missing pair or a failed resume is a typed
   attempt failure of its own identity, never retried inside the attempt.
2. The retained console log must show the exact `pause`/`unpause` command
   pairs of the attempt; their count is checked offline against the
   diagnostic during verify.
3. A capture that fails while paused (budget, truthiness, month gate or
   native refusal) still resumes the clock first, then raises; the retained
   failure save and diagnostic stay untouched.
4. Nothing here reopens or reclassifies any earlier terminal result: E139,
   E140 and E141 stay sealed at their own identities. A truncated search
   remains a truncated search forever — it can never be cited as proof of
   infeasibility, and the pause decision does not claim otherwise.
5. The first native run under this decision must observe one recorded risk
   honestly: the `pause` console command on an AdminPort-connected server is
   trusted but not yet native-
   evidenced. The attempt verifies that planning reads return while paused;
   if reads stall or the server refuses, the attempt types the failure
   (`PAUSED_CAPTURE_UNRESPONSIVE` or the native refusal verbatim) and the
   decision returns to the operator with evidence instead of a silent retry.

## 5. What this closes and what stays open

Closes: the M2 capture-pacing design question (map ticket 03 family) with an
implemented, offline-tested decision (`tests/test_freight_loops.py`), so the
next native capture round has one bounded design and fence set.

Stays open (native-gated, per-attempt grants): the fresh native capture round
that exercises the pacing plus the loop engine's first full verified cycle;
the FULL offline regression with the 53 legacy reds stays the map's EXIT gate
and was not run this round.
