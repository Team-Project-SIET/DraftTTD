# 04 — The continuous-world loop architecture

Type: grilling
Status: resolved
Blocked by: 03

## Question

Design the looping engine the destination names: ONE world (one ramrom
seed, 256×256 temperate flat, 1950-01-01) stays alive across repeated
analyze → plan → play cycles — the CP-SAT planner re-enters the same
running game, re-analyzes the assets (industries, materials, yields),
and grows the company with newly-formed freight services while the
spectator GUI shows every cycle. The decision must fix: the re-entry
mechanism (does the planning driver hold the one AdminPort connection
across cycles, or reconnect per cycle under the reconnect rules?), the
cycle cadence and budgets (when does a cycle's play phase end on a
continuous world — goal-scoped, time-scoped, or service-shaped?), the
funds model across cycles (does the company keep its money and purchase
rails for the next cycle?), how a cycle ends softly when the operator
closes the window (ticket-level: ended-by-operator, loop continues or
waits for the operator), when the product abandons a world for a fresh
ramrom seed ("nothing more forms"), and what is recorded per cycle
(receipts, P07 readback, the seed and world identity). Folded in: the
process-display clause (game window + console + per-run HTML report).

## Answer

Decided 2026-11-07; spec of record `docs/specs/ramrom-product.md` §3.
Items: cycle = one fresh qualified-month read + P05/CP-SAT plan +
execution + verified deliveries on the SAME alive world (never stale
facts — towns grow roads, industries change); re-entry = reconnect per
cycle under the existing one-attempt-per-connect discipline; cycle ends
softly on delivery-verified, operator window-close (ended-by-operator,
never failure) or time budget; the company keeps funds and vehicles
across cycles (the post-cycle save is the next cycle's before); a fresh
seed is drawn after 2 consecutive zero-service cycles; every cycle
appends receipts, diagnostic and an HTML report indexed by the run's
final report. Implementation surface: ticket 05 (build) — the §2
capture-fix slice landed this round, the loop engine builds next.
