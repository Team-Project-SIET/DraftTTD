# 02 — Capture-scheduler capacity policy

Type: wayfinder:grilling (HITL)
Blocked by: nothing

## Question

Decide the redesign for the capture-scheduler capacity policy exposed by seed 8
(E200, typed `CAPTURE_SCHEDULE_EMPTY`): the scheduler deferred both candidate
relationships because their estimated live-rate spans (26 d / 28 d from
planned start 712290) overshoot the exclusive observation window ending 712312
— zero reads, zero capture, no candidates.

The decision must fix, as reviewable criteria (not code):

1. The chosen mechanism: pace capture reads differently, split one
   relationship's capture across sessions (and what identity/correspondence
   that requires), widen the capture window (and how that interacts with the
   window-v2 decision in ticket 01), or keep the policy and make the skip an
   honest typed per-relationship record instead of an attempt-terminal.
2. What is preserved: pause-the-clock pacing is natively proven four times
   (E150 cycle-1 832/832, E198 832/832, E199 831/831, E201 1372/1372) and the
   month-pace gate (E156 class) fired as designed — neither may be weakened
   silently; every change must keep the typed rejection surface honest.
3. The acceptance test shape for the offline bar: which retained seed-8/seed-9
   bytes become fixtures, and what the scheduler must produce on them
   (captured relationships, not empty schedules) without changing any sealed
   identity.

Constraints: offline only at this stage; the scheduler's native behavior is a
later granted round inside the backbone battery. Seed 8's consumed attempt is
never re-run; its bytes are fixtures, not targets.
