# 01 — Why no ramrom seed qualified: the NO_FEASIBLE_SERVICES diagnosis

Type: research
Status: resolved
Blocked by: none

## Question

Exactly which gate, byte-by-byte, rejected every candidate on the two
one-shot native random runs (historical seed 17, and today's seed 2026 at
`artifacts/demos/playable-demo-3e93cc7d1e8d43aab66a4f653665caaa`)? The
typed terminal is `NO_FEASIBLE_SERVICES: no supported full-load road
engine and supply` with discovery reporting compatible=16 / candidates=0.
The diagnosis must produce, from the retained bytes only (no native
launches): a per-candidate rejection table (which of the qualification
gates — road engine availability, full-load order support, supply
capture, station placement, distance/budget — failed and on what facts),
the state of the native engine catalogs the run captured, the captured
supply/production and cargo identity facts, and a ranked list of
suspected root causes with the cheapest offline experiment that would
confirm each. The answer feeds ticket 03's feasibility-fix decision.

## Answer

Resolved offline over the retained bytes only; findings file of record:
`.scratch/ramrom-product/research/01-feasibility-diagnosis.md`. Verdict in
one line: no ramrom world fails at the engine and not at the planner — it
fails at the capture seal: the ≤512-tile ±2-rectangle (`app/demo_random.py:149-152`)
is a silent distance gate (14/16 relationships died there pre-engine), and
both captured coal relationships were then severed by the same town-road
band (x≈183..192 inside 8-day/5-row-tall strips) because `vacant()`
refuses roads and the reachability graph is confined to captured tiles
(reproduced on raw bytes). CP-SAT was never invoked. Key recorded facts:
`CANDIDATE_SEARCH_LIMIT` = discovery truncated at the 16-relationship cap
(146 of 8192 pair checks); the only engine catalog captured has one coal
truck (engine 123, capacity 20, road, public); engine/supply gates zero
rejections; a seed-17 per-candidate table is UNKNOWN (no retained planning
bytes); budget admission arithmetic 2/2/6/9/11/12 of 16 at budgets
512/1024/2048/4096/8192/16384. Cheapest no-native confirmations (two
byte-replay facts already produced by this ticket plus one synthetic
padding test) are listed in the findings file §6.

## Comments

- 2026-11-07 (post-resolution addendum): operator asked for OpenTTD
  domain verification via search engine; findings file §8 now records the
  wiki check — captured engine identified as the base Balogh Coal Truck
  (1935, cap 20), all temperate freight cargos have base road-truck
  families, the town-road wall is crossable game-consistently
  (base drive-through stops / road joining), and a loop-architecture
  caution was recorded: towns grow roads and industries change, so every
  planner cycle must re-qualify the world. Ticket status stays resolved.
