# 05 — FD-C-2 candidate-funnel root cause (read-only, offline)

Covers 2026-11-11 offline round at `a8bc8e3` + the FD-C-2 fix commit on
`miles/fright-delivery`. No native execution, no grant, no AdminPort, no
evidence byte touched anywhere; all sealed run dirs re-proven read-only
after every probe (attempt-2 root + cycle manifests, attempt-6 root +
`result.json` + both cycle manifests re-hashed unchanged).

## Question of record

FD-C-2: why does every Phase C loop cycle end `NO_FEASIBLE_SERVICES` with
`candidate_count=0`? Focus areas: P08 search bounds, terrain
classification, candidate filtering, `search_truncated` behavior.

## Method of record

Every probe replays sealed recordings through the ticket-07 verify
machinery (`_replay_network_world(..., zero_service=True)` +
`network_from_facts(..., planning_rejections=...)`) and re-derives the
corridor geometry independently with the module's own primitives
(`select_benchmark`, `station_tiles(limit=None)`, `corridor_reachability`,
`find_depot`). Nothing was fabricated: every recorded reason string,
element count and digest was re-derived from retained bytes and compared.

## Funnel facts of record (reproduced, then cross-checked)

Attempt-6 (`0751d73c…`, sealed E157, 1 captured relationship):
`bounded_relationships` admits 6 triplets
`[0,1,1] [0,14,1] [7,5,4] [7,5,6] [8,4,3] [9,12,8]`, 10 ×
`CAPTURE_TILE_BUDGET` + `CANDIDATE_SEARCH_LIMIT` rejections; capture picks
`[0,1,1]` first both cycles; cycle-1 rejection
`NATIVE_CORRIDOR_BOUND: requires 2..47 road tiles`, cycle-2
`NO_BOUNDED_CORRIDOR: …38 eligible pickup and 20 eligible delivery stops
are disconnected…`; `search_truncated=true` (discovery capped by
`max_relationships=16`, not the pair budget).

Attempt-2 cycle-1 (`e6852692…`, sealed E152) — the funnel's deepest
recorded depth, ALL SIX bounded candidates captured (9,702/9,702 reads,
6 pause pairs): reproduced rejection chain, byte-identical to the
sealed `candidate_rejections`:

| candidate | reproduced classification |
| --- | --- |
| `[0,1,1]`  | over-bound: complete reachability minimum interior = 49 (> 47) |
| `[0,14,1]` | disconnected: 0 supported corridors (39/18 stops) |
| `[7,5,4]`  | disconnected: 0 supported corridors (17/24 stops) |
| `[7,5,6]`  | disconnected: 0 supported corridors (17/24 stops) |
| `[8,4,3]`  | disconnected: 0 supported corridors (38/30 stops) |
| `[9,12,8]` | over-bound: complete reachability minimum interior = 56 (> 47) |

The four `NO_BOUNDED_CORRIDOR` reasons1 are complete-search disconnection
proofs (E9 design: "a disconnected result is a complete infeasibility
proof, not a first-N-stop artifact") inside the supported model of record
(flat vacant covered tiles only — the diagnostic's own limitation text).
Engine admission independent re-check: every captured fact has a
capacity-feasible full-load road engine (`capacities` non-empty); 
`NO_SUPPORTED_FULL_LOAD_ENGINE` fired on none of record.

## Verdict on the four focus areas

- **Candidate filtering**: no defect of record. All 8 recorded captured
  candidates (attempt-2 cycle-1's six + attempt-6's two cycles) were
  honestly refused; the zero in-bounds depot-bearing routes pin the
  no-miss property against sealed bytes.
- **P08 search bounds / capture budget**: honest bounded refuses
  (2048-tile complete rectangle, `CANDIDATE_SEARCH_LIMIT` at the
  max_relationships cap; E139's admit-matrix remains the reference).
- **Terrain classification**: flat-vacant supported-set classification
  reproduces every recorded disconnection stop count exactly; no
  misclassification found on retained bytes.
- **`search_truncated` behavior**: recorded truthfully everywhere; the
  `INCOMPLETE_EVIDENCE` discipline (no feasibility claim from a truncated
  search) remains correct and unchanged.

**Root cause of the zero-candidate terminal**: an honest bounded
refusal chain of record — truncated discovery (16 = max_relationships
cap), region admission (6/16), capture budget/pacing, and complete-search
corridor classifications (over-bound 49/56/63/66/72 interiors; 4×
disconnected) for every candidate that ever reached planning. Not a code
defect; no feasibility or infeasibility claim is drawn from it
(`search_truncated=true` throughout).

## Latent defect found and fixed (the one real defect)

The incumbent pair loop in `generate_road_scenario`
(`app/planning/p08_road.py`) returned the FIRST examined pair's corridor
regardless of corridor length: an in-bounds supported corridor between a
later pair could be masked by an earlier over-bound route, and the
candidate then died at the native admission check
(`NATIVE_CORRIDOR_BOUND`) although `witness_order`'s "supported interior
first" ordering defines the opposite precedence. The witness fallback
recovering such corridors existed but was unreachable after any
first-success assembly.

Offline proof (fixture `test_incumbent_pair_loop_skips_an_over_bound_
first_pair` in `tests/test_p08_bounded_routing.py`): a 16×16, 256-tile
controlled region with water columns at x∈{6,10,13} (alternating edge
gaps) gives the anchor-first delivery stop `15,7` a ~66-interior round
trip while stop `3,1` holds a straight supported 2-interior corridor;
before the fix the loop assembled the over-bound corridor (red:
`assert (68 - 2) <= 47`), after the fix the supported corridor is
assembled (green).

Fix of record (smallest complete): shared bound constants
`CORRIDOR_INTERIOR_MIN/MAX = 2, 47` + `CORRIDOR_INTERIOR` (used by
`witness_order` unchanged); the pair loop now (a) skips assembled paths
outside the bound instead of returning them, and (b) prunes, without
charging the aggregate expansion budget, any pair whose delivery's
already-computed complete-reachability witness is over-bound (its
minimum route over every eligible pickup exceeds 47, so no pair can
yield a supported corridor). Over-bound-only candidates still end in the
explicit byte-stable `NATIVE_CORRIDOR_BOUND` text (the witness fallback
assembles an over-bound route when no supported one exists), so every
sealed recording of record replays with identical rejection strings.

## Suites and statics of record (fix commit)

- `tests/test_p08_bounded_routing.py` 18 passed (17 prior + 1 new; seed-17
  retained-replay corridor pin unchanged).
- `tests/test_freight_loops.py` 3 new sealed pins
  (attempt-2 rejections byte-parity + 10×CAPTURE_TILE_BUDGET/
  CANDIDATE_SEARCH_LIMIT mix, attempt-2 no-miss complete-witness guard,
  attempt-6 per-cycle rejections) — the six-file targeted set of record
  is 154 passed / 0 failed (151 prior + 3).
- `tests/test_random_distance.py` + `test_supplemental_planning_contracts.py`
  78 passed; four-file loop tuple 76 passed.
- `test_p08_controlled_e2e.py` 51 failed at HEAD `a8bc8e3` WITHOUT the fix
  (stash-verified) and 51 failed with it — pre-existing, out of the loop
  chain, reported separately, never relabeled.
- ruff check / format --check / py_compile / `uvx ty check` /
  `git diff --check` clean on all touched paths.
- Verify of record at the fixed state: `…proof.freight_delivery verify
  artifacts/demos/…0751d73c…` → rc 0, both cycles `ZERO_SERVICE` receipt;
  all sealed manifests unchanged.

1 The reason byte-strings of record are reproduced in
  `test_sealed_attempt2_candidate_rejections_replay`; this table
  summarizes.
