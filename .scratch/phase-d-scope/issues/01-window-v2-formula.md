# 01 — Observation-window v2 formula

Type: wayfinder:grilling (HITL)
Blocked by: nothing

## Question

Decide the exact distance-scaled observation-window v2 that Phase D proposes,
given the E206 root cause of record: the designed 60-economy-day guard
(`main.nut:151`, shared across all four phases from the pre-start date 712290)
fired as designed on seed 7 — the full-load wait consumed 50 of the 60 days and
the vehicle was still ≥24 Manhattan tiles short of a 32-Manhattan-haul
destination at expiry; the tick budget computed 4440 and was never binding.

The decision must fix, as reviewable criteria (not code):

1. The v2 formula of record: what the observation window scales with (route
   Manhattan distance? capture-reported haul class? planned full-load wait
   allowance?), its floor and ceiling, and whether load-wait enters the term
   separately from travel.
2. The versioned surface: where the v2 window lives (a versioned budget field
   sealed at prepare, like `loop_cycles`), so v1 identities stay byte-equal and
   no retained record is reinterpreted.
3. Typed-gate preservation: which existing typed outcomes must survive
   unchanged (`WINDOW_EXHAUSTED`, the 60-economy-day lifecycle bound, the
   2048-tick no-movement guard), and what the new extreme-distance behavior is
   (cap the window and refuse typed? admit and risk honest expiry?).
4. The relationship to the 60-economy-day observation lifecycle bound (README
   planning-boundary section) — does v2 raise that lifecycle ceiling too, and
   if so, under what typed budget lines.

Constraints: any native use of v2 is a later, separately granted round; this
ticket decides the proposal-level contract only. E206 is the forensics of
record; the window redesign there is explicitly "a fresh operator decision".
