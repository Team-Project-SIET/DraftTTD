# Seed-17 random-world feasibility — improvement proposal (E210 continuation)

Date: 2026-11-13. Fully offline: no launch, no AdminPort, no grant, no sealed
byte modified, no relabeling, no commit, no push. Predecessor of record: E210
(`playable-demo-b67a8909909547b298822c98051741f2`, typed terminal
`NO_FEASIBLE_SERVICES`, funnel 13× `CAPTURE_TILE_BUDGET` → 2×
`INSUFFICIENT_CAPACITY` deferrals → 1 captured pair refused
`NO_BOUNDED_CORRIDOR` → 0 candidates).

## Status summary

| Item | Status |
| --- | --- |
| Funnel typing and per-pair refusal attribution of E210 | VERIFIED (E210, re-confirmed from sealed bytes) |
| B3 fix: pair-loop expansion reservation + witness fallback (`app/planning/p08_road.py`) | VERIFIED offline (implemented, 164 focused tests green, ruff/ty/`git diff --check` clean) |
| B1 structural capture-geometry recovery (bigger tile-limit profile or union region) | PARTIAL — design proposal, needs a product/identity decision and a native round |
| B1 operator lever `--capture-pad 32` (no code change) | PARTIAL — supported today; effect on future worlds UNKNOWN until a fresh authorized run |
| B2 capacity-policy redesign (pacing-aware) | PARTIAL — owned by `.scratch/phase-d-scope/issues/02` + `13`; not implemented here |
| Whether any corridor exists for pair 7→15 cargo 4 outside the 945-tile slice | UNKNOWN (needs a fresh authorized run; never provable from sealed bytes) |
| `search_truncated` semantics ("no route exists globally") | VERIFIED already honest — no code change needed |

## Bottleneck 1 — CAPTURE_TILE_BUDGET (13 pairs)

### Constraints and source paths

`bounded_relationships` (`app/simulation/openttd/freight_native_network.py:49-63`)
runs `relationship_region` (`app/demo_random.py:137-199`) per discovered pair.
The region is the padded bounding rectangle `(dx+4)×(dy+4)` clipped to the map
interior; the 2048 profile grows the shorter axis perpendicular to the OD axis
by at most `edge_pad` per side (CLI `--capture-pad`, default 6, max 32) and
refuses with `CAPTURE_TILE_BUDGET` when the final area exceeds
`capture_tile_limit` (2048, `demo_random.py:191-192`).

From the sealed diagnostic, all 11 distinct rejected pairs have **unclipped**
base rectangles of 2,958–24,964 tiles (anchors well inside the map, so
`grown == base`); the growth step only ever enlarges. Conclusion of record:
**these 13 refusals are structural at any `edge_pad`** — no pad value, and no
within-rectangle optimization, can admit them at a 2,048-tile seal. The three
admitted pairs (7→15 cargo 4/6 at 525 base, 9→6 cargo 8 at 1,947 base) are the
only geometry the current seal can ever capture.

### Options (in priority order)

1. **Operator lever, no code change:** for pairs whose base fits (the E210
   captured pair: 35×15 base = 525 → 945 tiles at pad 6), run future
   authorized attempts with `--capture-pad 32`: the 2048 profile then spends
   the full spare seal budget on the shorter axis (35×57 = 1,995 tiles, ~4.4×
   the detour room). This directly widens P08 corridor search coverage inside
   the unchanged 2048 seal. Identity implications: every run is a fresh
   digest-pinned identity anyway; no sealed byte is touched.
2. **Larger tile-limit profile (e.g. `random-rectangle-4096-v1`):** would admit
   more of the 13 (2,958–8,000-tile pairs), but requires: widening
   `capture_tile_limit: Literal[256, 512, 2048]` (regex-pinned by the phase-C
   engine, `phase_c_feasibility.py:428` — a deliberate fail-closed pin, so this
   is a decision, not an edit), a new capture-read budget
   (`(limit+36)×relationships+1`), new capture wall-clock budget, and a fresh
   native qualification round. Not implementable as a clearly-safe offline
   change; recorded for the operator decision.
3. **Union-of-two-rectangles capture (per-industry neighborhoods):** covers
   both catchments without spanning the gap, but the facts contract, coverage
   scopes, corridor reachability graph and native capture protocol all assume
   one rectangular region per relationship. Protocol change; design round
   required; strongest theoretical gain (decouples capture size from OD
   distance) but the largest blast radius.

### Correctness / evidence implications

No feasibility rule is weakened by any option: each still refuses regions
above the (possibly new) budget and the per-session runtime guards
(`CaptureWindowExceeded`, `CAPTURE_REQUEST_BUDGET`) remain the stop points.
A new tile-limit profile creates a new product identity — it must not
reinterpret retained 256/512/2048 identities (`DemoBudgets.from_sealed`
already forces 256 for retained v1 packages; that pin stays).

### Required offline regression tests (for whichever option is chosen)

- `relationship_region` unit tests at the new limit: admit/reject boundaries,
  perpendicular growth caps, map-edge clipping, profile tag.
- Scheduler forecast tests: estimate ≤ new read budget for a maximal region.
- Phase-C pinned-statement updates (the regex pin set must be re-derived, not
  dodged) and the E196/E204 targeted pin suite re-run.
- Retained-identity tests: `from_sealed` still forces 256; legacy digests
  byte-equal.

## Bottleneck 2 — INSUFFICIENT_CAPACITY (2 deferrals)

### Constraints and source paths

`preflight_schedule` → `plan_sessions` (`app/simulation/openttd/
capture_scheduling.py:268-384`) sorts relationships by ascending heuristic
estimate (tiles + 34 reads), charges `ceil(estimate/74)` live-rate days per
session plus a 1-day inter-session gap, and defers any session whose planned
last day reaches the exclusive qualified-month end (712312 in E210). Pair
(7→15, cargo 6) spanned 14 d from 712303 → 712316; pair (9→6, cargo 8)
spanned 27 d → 712329. Both regions fit the 2048 seal; the refusal is purely
the day-accounting model.

The model is deliberately conservative: E156 attempt-4 showed freeze efficacy
was runtime-observed, not guaranteed. But E210 (and E150/E198/E199/E201)
measured the pause-pacing runtime of record freezing the clock through whole
sessions (`pause_pairs: 1`, before==after at 712289) — the live-rate span is
now known to overstate the cost of sessions run under `paused_world_clock`
with the `console_ack` handshake (ticket 06). Under pause pacing, all three
E210-bounded pairs would fit the remaining 25 days trivially.

### Options

This workstream is **already owned**: `.scratch/phase-d-scope/issues/02`
(wayfinder decision: mechanism choice) and ticket 13 (implementation, with
retained seed-8/seed-9 bytes as fixtures). To avoid modifying another
workstream, this proposal adds only design input, not code:

- **Direction A (recommended for the ticket-02 decision):** make
  `CapacityPolicy` pacing-aware — a session planned under pause pacing
  consumes only the inter-session gap (plus a conservative safety margin),
  because the runtime guard `CaptureWindowExceeded` and the per-session
  `require_world` gate keep every guarantee if a pause ever fails live.
  Default behavior (live-rate model) stays byte-identical; the pause-aware
  path is selected only where the runtime actually opens
  `paused_world_clock`.
- **Direction B:** keep the policy and make per-relationship deferrals an
  honest typed per-relationship skip (capture what fits, record the rest)
  instead of `CAPTURE_SCHEDULE_EMPTY` when at least one session fits — note
  this is already the behavior (`require_planned` only fires when *no*
  session fits); the residual gap is only the all-deferred shape (E200).

### Correctness / evidence implications

A pacing-aware policy must never weaken the typed surfaces: the E156
month-pace gate, `CaptureWindowExceeded`, and the per-pair `pause_pairs`
evidence stay authoritative. Any change creates a new scheduler identity;
retained schedules (E200/E210 preflight records) must replay byte-equal.
`search_truncated`/capacity refusals remain feasibility-neutral: they never
assert a world is infeasible.

### Required offline regression tests

- Seed-8 sealed bytes as fixtures: the chosen mechanism produces captured
  relationships offline without changing any sealed identity (ticket 13's
  acceptance shape).
- Typed-preservation tests: month-pace gate and runtime guard fire as
  designed under the new policy.
- Byte-equal replay of the E210/E200 preflight schedules under the default
  (live-rate) policy.

## Bottleneck 3 — NO_BOUNDED_CORRIDOR (priority: implemented)

### Constraints and source paths

For the one captured pair (7→15, cargo 4; 945-tile region), P08
(`app/planning/p08_road.py:generate_road_scenario`) runs:

1. a **complete shared-super-source Dijkstra** (`corridor_reachability`,
   :246-290) over every eligible vacant covered stop — a disconnected result
   is a complete infeasibility proof for the captured slice (E159 contract;
   `tests/test_freight_loops.py::test_sealed_attempt2_witness_refusals_are_
   complete`); E210's verdict (12 pickups / 71 deliveries disconnected) is
   therefore a proven slice outcome, not a first-N artifact; and
2. an **incumbent pair loop** over the first-four stops per role
   (`MAX_STATIONS_PER_ROLE = 4`), each pair a fresh BFS charged against
   `MAX_PATH_EXPANSIONS = MAX_STATION_PAIRS × 256 = 4096`
   (`p08_adapter.py:83-85`).

**Coverage gap found and fixed:** the expansion bound was calibrated at the
256-tile scale. The 2048 profile widened regions eightfold; a per-pair BFS
sweep over a large component can exhaust the 4,096 budget while the completed
reachability sweep already holds real supported witnesses. The old code
returned `SEARCH_LIMIT_EXCEEDED` at that point (`p08_road.py:418-423`),
**masking corridors that provably exist** — exactly the artifact class the
E159 remediation eliminated for the disconnected case, surviving only in the
connected case. (`test_p08_controlled_e2e.py:594` even documents the belief
that 4,096 overflow is "impossible under 16×256 admission bounds" — true at
256, false at 2048.)

### The implemented change (offline, additive, no pinned surface touched)

`app/planning/p08_road.py`, incumbent pair loop:

- Reserve each BFS's worst case before starting it
  (`expansions + len(tiles) > MAX_PATH_EXPANSIONS → break`): `shortest_path`
  expands each vacant tile at most once, so every recorded expansion count
  stays ≤ the bound and the documented invariant
  (`search_expansions ≤ MAX_PATH_EXPANSIONS`, pinned by
  `test_p08_controlled_road.py:266` and `test_p08_bounded_terrain.py:384`)
  is preserved on every assembled scenario.
- On reservation break, fall through to the **existing witness fallback**
  (`witness_order` → `find_depot` → `assemble`), which assembles only
  corridors from the *completed* complete-sweep witnesses — supported 2..47
  routes first, over-bound routes still explicitly refused downstream by
  `network_from_facts` (`NATIVE_CORRIDOR_BOUND`).
- The post-loop `return SEARCH_LIMIT_EXCEEDED` is deleted: with the
  reservation it is unreachable, and the reachability sweep's own budget
  still types `SEARCH_LIMIT_EXCEEDED` fail-closed above (unchanged).

**Feasibility guarantees preserved:** no candidate is fabricated; witnesses
come from a completed sweep over vacant flat tiles inside the captured slice;
the native executor independently re-checks the 2..47 corridor bound; over
1..2 interiors and over-bound corridors are refused exactly as before.

**Deliberately untouched (each would break a seal or a decision boundary):**

- `MAX_PATH_EXPANSIONS` itself — the line
  `MAX_PATH_EXPANSIONS = MAX_STATION_PAIRS * 256` is regex-pinned by the
  phase-C limits dimension (`phase_c_feasibility.py:440`,
  `tests/test_phase_c_feasibility.py:670`); the phase-C engine treats these
  as fail-closed source pins, so the bound changes only by decision.
- `NoRoadScenario` detail strings — sealed replays pin refusal reasons
  byte-exact (`test_freight_loops.py:1268-1285, 1376-1389`; E210's
  diagnostic-status regression test); any wording change stops sealed
  terminals from replaying.
- The movement model (flat vacant land only, equal `min_height`, no roads/
  rails/slopes/bridges) — widening it is a product decision, recorded in the
  diagnostic limitations (`demo_random.py:248`) and pinned by
  `test_p08_bounded_routing.py:209-214`. On real worlds (including E210's),
  existing roads and NPC infrastructure currently *disconnect* the vacant
  graph; a "traverse existing road" model is the single largest future
  coverage lever and belongs in its own decision round.
- The capacity scheduler (B2) — owned by phase-d-scope tickets 02/13.

### Concurrency note (operator visibility)

While this task ran, the operator's concurrent session captured these exact
two file changes twice by commit: first as `beae566` ("babababa2",
2026-11-13 08:28) on branch `miles/fright-delivery`, then — after this task
re-applied them uncommitted on `main` — as `643f9df` ("MMAs", 2026-11-13
08:39) on `main` (HEAD at recording time). No commit or push was made by
this task; the working tree now carries only the new research note
untracked. Three
`test_demo_random_native.py::test_complete_random_preparation_is_pristine_
native_newgame[*]` params are red in this session for the same environmental
reason E210 recorded: the operator-launched native attempt (seed 7, PID
105691) is live, and the pinned preflight correctly refuses while any
OpenTTD process runs. Environmental, never a code red, not masked.

### Offline test plan and results of record

New regression test:
`tests/test_p08_bounded_routing.py::test_pair_loop_budget_exhaustion_falls_
back_to_witnesses` — 12×3 region, water column at x=6, delivery eligibility
restricted so exactly one supported witness exists on the reachable side;
the reachability sweep completes exactly at the patched budget while every
per-pair BFS cannot; asserts the pair loop falls back and assembles the same
scenario the unbounded-budget run assembles (`scenario_hash` equality),
`search_expansions ≤` budget, corridor adjacency, and P05 validation with
non-empty routes.

Focused suites (one run each, current tree):

```
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest \
  tests/test_p08_bounded_routing.py tests/test_p08_controlled_road.py \
  tests/test_p08_bounded_terrain.py tests/test_p08_feasibility_classification.py \
  tests/test_freight_loops.py -q -p no:cacheprovider
# → 164 passed, 0 failed (sealed attempt-2/attempt-6 rejection strings byte-stable)

PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest \
  tests/test_p08_controlled_e2e.py -q -p no:cacheprovider
# → passed (part of the 107-run with test_freight_loops.py earlier at the same tree content)
```

```
.venv/bin/ruff check app/planning/p08_road.py tests/test_p08_bounded_routing.py
# → All checks passed!
uvx ty check app/planning/p08_road.py tests/test_p08_bounded_routing.py
# → All checks passed!
git diff --check   # clean
```

Random/demo suites (`test_random_distance.py`, `test_demo_random.py`,
`test_demo_random_native.py`, `test_demo_operations.py`,
`test_openttd_demo.py`): 68 run, 65 passed, 3 failed — only the three
environmental pristine-newgame params above.

## Honesty boundaries that must stay (no change requested)

- `search_truncated=true` is a **discovery** truncation flag (pair-check /
  relationship budgets, `discover_relationships`); it never means "no route
  exists globally", and no recorded artifact treats it as one. The phase-C
  engine already carries this framing (`phase_c_feasibility.py:916,977`).
- Every `NO_BOUNDED_CORRIDOR` detail says "no feasibility outside this slice
  implied" — slice-bounded by construction (`neighbors` never yields tiles
  outside the capture; `test_p08_bounded_routing.py:140-151`).
- The `NO_FEASIBLE_SERVICES` terminal string is the engine/supply class for
  empty-package shapes and is pinned by sealed-replay tests; the per-pair
  truth lives in `capture_rejections`/`capture_preflight`/
  `candidate_rejections`, which E210's `diagnostic_status` fix now surfaces
  at run end.

## What would actually change an E210-class outcome (operator decisions needed)

1. Bigger effective detour room inside the current seal: `--capture-pad 32`
   (no code; fresh identity per run).
2. Pacing-aware capacity policy (phase-d-scope ticket 02 decision → 13).
3. Movement-model widening (traverse existing roads / tolerate slopes with
   levelling) — biggest coverage gain, largest product decision; the
   terrain-feasibility diagnosis attached to every corridor rejection
   (`assess_world_feasibility`) already classifies what each blocked corridor
   would require, so a decision can be made from evidence.
4. Larger tile-limit profile / union regions for the 13 structurally
   over-budget pairs (B1 options 2–3).

None of these is a code edit this task could safely make alone; each needs
its own reviewed record and (for 1–3 native effects) a separately authorized
native round.
