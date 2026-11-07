# Ticket 01 findings — why ramrom seed 2026 died: the NO_FEASIBLE_SERVICES diagnosis

Findings file for the wayfinder ticket
`.scratch/ramrom-product/issues/01-feasibility-diagnosis.md`. All facts come
from retained bytes (no native launches, no regeneration). Every fact is
cited `path:line` or `path:json-key`; every gap is marked UNKNOWN.

Run of record: `artifacts/demos/playable-demo-3e93cc7d1e8d43aab66a4f653665caaa`
(random world, seed 2026, 256×256 temperate flat 1950-01-01, towns 3 /
industries 3, generation request verified equal to requested settings:
`planning-diagnostic.json:actual_generation_settings`).

## 1. The decline chain (who throws the typed error, and when)

The funnel runs top-down in this exact order:

1. **Relationship discovery (offline, pre-native).**
   `app/demo_random.py:102` `discover_relationships` walks industry pairs and
   stops on either budget; the diagnostic records
   `pair_checks: 146` and `search_truncated: true`
   (`planning-diagnostic.json`). The cap hit was **selection count, not pair
   checks**: 146 of `max_pair_checks` 8192 were consumed when
   `len(selected)` reached `max_relationships` 16 (`app/demo_random.py:122-123`,
   `app/demo_random.py:47-48`). So "compatible=16" is a **budget cap, not a
   world census** — unknown how many pairs remain beyond check 146 (UNKNOWN).

2. **Capture admission per relationship (offline decision, per pair).**
   `app/demo_random.py:144-152`: the capture rectangle is the bounding box of
   the two anchor tiles extended by **exactly 2 tiles on every side**
   (`x = min-2, right = max+2`, same for y), and it is refused when
   `width*height > capture_tile_limit` (512) with
   `CAPTURE_TILE_BUDGET` (`app/demo_random.py:156`, list also at
   `app/demo_random.py:53`). Note the arithmetic to the diagnostic:
   `padded_capture_tiles = (dx + 4) * (dy + 4)` (`app/demo_random.py~174`).

3. **Native capture of relationship facts** → `network-facts-{0,1}.json`
   (region, tiles, coverage, engines, road costs). 762 data-point requests
   completed for the two admitted relationships
   (`planning-diagnostic.json:capture_requests_attempted/completed = 762/762`).

4. **Engine gate, relationship level.**
   `app/simulation/openttd/freight_native_network.py:109-135`: for
   service batches, engines must have `default_cargo_id == pickup cargo`
   and `0 < capacity <= supply` (supply = the qualified month's
   `last_month_produced` for that industry+cargo); the batch limit becomes
   the **smallest** passing capacity (line `capacities[0]`). Empty →
   rejection `NO_SUPPORTED_FULL_LOAD_ENGINE` (:114-135).

5. **Road scenario gate (corridor leg).**
   `app/simulation/openttd/freight_native_network.py:139-170`: calls
   `app/planning/p08_road.py` `generate_road_scenario(package,
   full_load_batch=True)`. Inside it, in order:
   - engine filter: default-cargo road engines of the region, then a strict
     `capacity == batch quantity` equality under `full_load_batch`
     (`app/planning/p08_road.py:334-341`), then vehicle-count feasibility
     (:342-345) → else `INVALID_ENGINE_COMPATIBILITY` / `CAPACITY_INFEASIBLE`;
   - station placement (:347-361) → `NO_STATION_PLACEMENT`/`MISSING_CATCHMENT`;
   - **complete reachability**: `corridor_reachability`
     (`app/planning/p08_road.py:240`, called at :363-389) runs a shared-super-
     source Dijkstra over `vacant()` tiles only
     (`app/planning/p08_road.py:125-137`: buildable, slope 0, no industry, and
     explicitly **not** water/coast/tree/farm/rock/rough/road/rail/
     water_transport/air_transport) — the graph is confined to the tiles the
     capture rectangle brought (`station_tiles` selects only from
     `value.facts.tiles`, `app/planning/p08_road.py:139-156`). Zero witnesses
     → `NO_BOUNDED_CORRIDOR` with the "N eligible pickup … disconnected"
     message (:388-402); after that a witness/depot second stage
     (:400-406, :457-460).
   - Also outside p08: a road scenario whose corridor is not 2..47 tiles →
     `NATIVE_CORRIDOR_BOUND` (`freight_native_network.py:149-151`).
6. **All packages empty → the typed terminal.**
   `app/simulation/openttd/freight_native_network.py:172-173`: with zero
   surviving packages it raises
   `ValueError: NO_FEASIBLE_SERVICES: no supported full-load road engine and supply`
   — byte-equal to `result.json:error` of the run. **CP-SAT (P05) was never
   invoked**: `selected_service_count: null` and `candidate_count: 0`
   (`planning-diagnostic.json`) — the second raise site at
   `freight_native_network.py:362` (P05 selects zero) was not reached.

## 2. The seed-2026 per-candidate rejection table

Recorded in `planning-diagnostic.json` (`compatible_relationships` 16 rows,
`capture_rejections` 15 rows, `candidate_rejections` 2 rows) and reproduced
below. Industries: id 0 = type 0 coal mine at (158,241); id 1 = type 1 power
station at (195,237); id 14 = type 1 power station at (236,240)
(`planning-diagnostic.json:industries`).

| # | src | dst | cargo | dist | padded tiles | outcome |
|---|-----|-----|-------|------|-------------|---------|
| 1 | 0 | 1 | 1 COAL | 41 | 328 | captured → **NO_BOUNDED_CORRIDOR** (17 pickup / 20 delivery stops disconnected) |
| 2 | 0 | 14 | 1 COAL | 79 | 410 | captured → **NO_BOUNDED_CORRIDOR** (17 pickup / 20 delivery) |
| 3 | 0 | 18 | 1 COAL | 145 | 5390 | CAPTURE_TILE_BUDGET |
| 4 | 3 | 2 | 7 | 128 | 2688 | CAPTURE_TILE_BUDGET |
| 5 | 3 | 16 | 7 | 211 | 3434 | CAPTURE_TILE_BUDGET |
| 6 | 3 | 23 | 7 | 225 | 4642 | CAPTURE_TILE_BUDGET |
| 7 | 7 | 5 | 4 | 161 | 1134 | CAPTURE_TILE_BUDGET |
| 8 | 7 | 20 | 4 | 291 | 22078 | CAPTURE_TILE_BUDGET |
| 9 | 7 | 5 | 6 | 161 | 1134 | CAPTURE_TILE_BUDGET |
| 10 | 7 | 20 | 6 | 291 | 22078 | CAPTURE_TILE_BUDGET |
| 11 | 8 | 4 | 3 | 128 | 1143 | CAPTURE_TILE_BUDGET |
| 12 | 8 | 10 | 3 | 292 | 19136 | CAPTURE_TILE_BUDGET |
| 13 | 9 | 6 | 8 | 117 | 2646 | CAPTURE_TILE_BUDGET |
| 14 | 9 | 12 | 8 | 72 | 1239 | CAPTURE_TILE_BUDGET |
| 15 | 9 | 17 | 8 | 244 | 12740 | CAPTURE_TILE_BUDGET |
| 16 | 11 | 1 | 1 COAL | 294 | 22512 | CAPTURE_TILE_BUDGET |

Plus the truncation record: `CANDIDATE_SEARCH_LIMIT, checks: 146`
(capture_rejections[14]) — discovery ended at the 16-relationship cap, not
the 8192 pair-check budget.

**Engine gate outcome for the two captured relationships: PASSED.** The
captured engine catalog has exactly one road engine — engine id 123,
`capacity_cargo_units=20`, `default_cargo_id=1` (COAL), road type 0,
`public_available=true`, speed 48, purchase 4429 GBP
(`network-facts-0.json:engines[0]`, `network-facts-1.json:engines[0]`).
The engine leg supplies ≥ 20 (from the qualified month; the exact
production number is not present in the JSON bytes — the production digest
is a sha256 string, `world-planning-observation.json:production_digest` —
so the exact `last_month_produced` is UNKNOWN, while the pass itself is
implied by the batch-limit selection continuing to p08 and p08's
exact-equality passing).

**Corridor gate outcome for both: FAILED, and reproduced on the raw bytes
offline.** Replaying reachability over `network-facts-0.json` (41×8 strip,
328 tiles, 179 vacant) yields eligible pickup=17 in a component of 117
vacant tiles (x 160..186), eligible delivery=20 in a separate component of
33 tiles — **no shared component**. Same for `network-facts-1.json` (82×5
strip, 410 tiles, 259 vacant): 17 pickup vs 9 delivery in disjoint
components. The sever:

- **facts-0** (x 156..196, y 235..242): a contiguous non-vacant band at
  columns **x=183..192** — x=185 is 7/8 road, x=187-189 are 8/8
  unbuildable, x=188 is **road ×8**; roads are excluded from `vacant()`
  and their tiles are `buildable=false` in the capture. No corridor route
  can cross inside a strip only 8 rows tall.
- **facts-1** (x 156..237, y 238..242, 5 rows tall): the same
  town-road band at **x=185..191** (5/5 non-vacant for x=185..190), plus
  slopes from x=232 and trees from x=203..227 chopping the rest.

The strip height is what makes navigation impossible: the capture
rectangle is "anchors ± 2 tiles per axis" (`app/demo_random.py:149-152`),
so a single cross-cutting town road — ordinary OpenTTD terrain — kills the
pair even though the world would happily route around it with a wider
slice.

## 3. Budget arithmetic (offline, from the recorded pairs)

Admission at larger `capture_tile_limit`, computed from the 16 recorded
relationships (no native run needed):

| budget | admitted of 16 |
|--------|----------------|
| 512 (today) | 2 |
| 1024 | 2 |
| 2048 | 6 |
| 4096 | 9 |
| 8192 | 11 |
| 16384 | 12 |

So on this world the 512-tile rectangle budget is a **silent distance
gate**: only near-collinear industry pairs (roughly one axis ≲ 4..8 tiles)
fit, everything else dies before its engine/supply facts are ever
gathered. Raising the budget alone multiplies captured candidates (6..11
at 2048..8192) but each surviving pair still needs detour space (the facts
admitted at 2048 are 1134..1239-tile strips, whose connectivity is
UNKNOWN — those tiles were never captured).

## 4. Ranked root causes

1. **Capture-seal geometry is a silent distance gate** — highest
   confidence (14/16 relationships = 87.5% of the funnel died here,
   pre-engine). The ±2-per-axis rectangle with `capture_tile_limit=512`
   provably cannot serve a normal 256×256 sparse-industry world; 19 of 20
   recorded pairs exceeded it. Levers: larger budget and/or
   relationship-shaped (corridor/L-shaped) seals.
2. **Detour-free strips** — confidence high on the record (2/2 admitted
   pairs died exactly at the same town-road band, byte-reproduced
   offline); the reachability graph is restricted to captured tiles and
   `vacant()` refuses roads, so any single obstacle inside the thin strip
   is final. Levers: perpendicular padding ≫ ±2, or corridor-shaped
   capture, or road-crossing rules (an open design decision, not a
   mechanical fix — roads at grade could be legitimate for a truck
   product).
3. **Industry spread** (towns 3 / industries 3 over 256×256) force-feeds
   root cause 1: distances 41..294 Manhattan. The settings are the
   operator's spec of record; making distance work belongs to root
   causes 1–2 (industry count is an operator decision lever).
4. **Engine catalog thinness** — UNKNOWN whether more road engines exist
   in 1950 temperate for the other cargos (WOOD, IRON, OIL, GRAIN …): this
   run captured facts only for the two COAL relationships, so the catalog
   in `network-facts-{0,1}.json` (1 engine) is scoped to those. No
   candidate died at the engine gate on this seed (0 rejections with
   `NO_SUPPORTED_FULL_LOAD_ENGINE`), so this is **not** an observed root
   cause today — it is an exposure.

## 5. Seed-17 historical comparison

The retained seed-17 directories
(`artifacts/demos/classification-exec-seed17-3a8f9e46` → status
`TILE_CLASSIFICATION_V2_CAPTURED_INCOHERENT`; `…-e71c95a3` →
`FAILED_CLEANUP`, both from their `result.json`) show the seed-17 line
failed at an earlier pipeline stage and left **no** planning-diagnostic or
network-facts bytes — a seed-17 per-candidate table is UNKNOWN (missing
evidence, not absence of failure). An offline distance study exists
(`artifacts/demos/random-distance-seed17-offline-20261017/`, 135 passing
tests) confirming the distance-funnel was examined before; its scenario
values are not re-quoted here as fresh evidence.

## 6. Cheapest offline confirming experiments (for ticket 03, not yet done)

1. **Byte replay unit test** (zero cost, done in research): rebuild the two
   graphs from `network-facts-{0,1}.json` tiles under
   `app/planning/p08_road.py:125-137` vacancy rules and assert the
   17-pickup / 20-delivery (and 17/9) component split — evidence-backed
   fixture for any corridor change.
2. **Budget-matrix unit test** (zero cost, done in research): assert
   admission counts 2/2/6/9/11/12 for budgets
   512/1024/2048/4096/8192/16384 over the 16 recorded pairs — pins the
   "silent distance gate" claim numerically.
3. **Padding-widening synthetic test** (offline, no native): construct a
   small tile grid with a town-road wall, run the same reachability under
   ±2 padding (must stay disconnected) and under widened perpendicular
   padding (must connect) — proves the fix direction before any native
   grant is spent.

## 7. What the fix will likely touch (hypotheses for ticket 03 — NOT decisions)

- `app/demo_random.py:47-49` budgets (`capture_tile_limit` literal
  256|512; pair/relationship caps) and the ±2 pad (`:149-152`), or a new
  seal profile beyond `random-rectangle-512-v1`
  (`app/simulation/openttd/supplemental_planning_facts.py:92`,
  `app/simulation/openttd/tile_classification.py:777`).
- `app/simulation/openttd/freight_runtime_planning.py:301` (the runtime
  tile-limit consumer).
- Possibly `app/planning/p08_road.py` vacancy/corridor rules (road
  crossings) — a semantic decision.
- Not required by today's evidence: engine/production gates
  (`freight_native_network.py:109-135`) — no rejection exercised them.
