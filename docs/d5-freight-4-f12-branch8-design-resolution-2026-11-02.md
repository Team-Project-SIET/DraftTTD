# D5 Freight Delivery v2 — F-12 and branch-8 design/evidence resolution (E58)

Status: docs-only offline record, 2026-11-02. Read-only over `artifacts/` and
`ottd/`; no source change, no candidate change, no evidence regeneration, no
launch/connection/signing/claim/retry. Prior recorded text (E57 included) is
untouched. A future `D5-FREIGHT-4` requires a fresh identity, fresh staging,
independent review, Gate C re-signing and a separate explicit launch approval
(E53/E56 precedent) — nothing in this record changes that.

## 1. Scope

`E56` halted at the first exchange (`site-00` → `INVALID_SITE`), refusal
branch 4 of 8: the F-12 directed depot-entry probe. Branch 8 (discovery boxes
exactly-one) was left UNKNOWN and moot. The question this record closes at the
design/evidence level: what must be true, and in what order it must be
measured or built, before `D5-FREIGHT-4` can pass `site-00` without being
another one-request failure.

## 2. Branch 4 (F-12 depot edge): instrument kept, world fix prescribed

E57 verdict stands, now closed with the one missing feasibility check:

- The instrument is correct and stays strict. `GSRoad.AreRoadTilesConnected`
  requires the neighbor-facing road bit on both tiles
  (`ottd/src/script/api/script_road.cpp:107-125`); a depot tile contributes
  only its exit bit (`ottd/src/road_map.cpp:54-70`); the depot door emits only
  its door trackdir (`ottd/src/road_cmd.cpp:2184-2191`); entry into the depot
  requires the front tile's north (depot-facing) trackdir
  (`ottd/src/pathfinder/follow_track.hpp:272-312`). YAPF movement agrees:
  a vehicle can leave through the door but cannot steer back in without the
  stub.
- The world defect: tile 45743 = (175,178) carries E+W (D4 run-A full-op
  endpoints) + S (D4 corner-join half-op 45743→45999) and **no N**. Geometry:
  45487=(175,177), 45743=(175,178), 45999=(175,179). The stale design
  assumption is exactly the D4 op03 claim quoted in
  `docs/handoff/2026-10-25/d4-corridor-op03-root-cause.md` — "span endpoints …
  includes 45743" — which covered corridor-facing bits only.
- New feasibility check (this record): `CmdBuildRoadDepot`
  (`ottd/src/road_cmd.cpp:1137`) runs `CMD_LANDSCAPE_CLEAR` on the target tile
  in the non-rotate path, so a depot can be (re)built onto a tile that still
  carries road bits. Building road pieces **into** a standing depot tile stays
  refuted (`road_cmd.cpp:516-518`), and every script span API needs
  `start != end` (`script_road.cpp` `_BuildRoadInternal`), so the stub cannot
  be laid before the depot is gone: any minimal fix passes through a
  demolish.

### 2.1 Prescribed world fix (design, not yet staged)

Three mutations, no relaxation of any gate:

1. `GSTile.DemolishTile(45487)` (exists: `script_tile.cpp:285` =
   `CMD_LANDSCAPE_CLEAR`; legal: no vehicle on/inside the tile — D5 world has
   zero fleet, funds ledger unaffected by demolish refunds class).
2. Road pair build `45743 ↔ 45487` (2-tile half-op lays the span-facing bit on
   both tiles: N on 45743, S on 45487 — the missing stub).
3. `GSRoad.BuildRoadDepot(45487, front 45743)` — auto-clears 45487's S bit by
   the §2 check above; the stub persists on 45743.

Post-fix verification ops (fixed-fact confirmations, E49 confirm pattern):
`AreRoadTilesConnected(45743,45487)` **and** `(45487,45743)` both true;
depot identity/front/owner/linked facts unchanged (`front_id 45743`,
owner 0, `depot_linked true`); readback per op with native quote equality
under the per-op budget.

Consequences for `D5-FREIGHT-4`: the plan model ends every cycle `in_depot`,
so on the un-fixed world a relaxed branch-4 gate would only move the failure
to depot return — the fix is mandatory, not optional; branch 4 stays strict
 nevertheless (the probe measures exactly the thing the world lacks). After
the fix lands, `D5-FREIGHT-4`'s prerequisite chain re-binds to the post-fix
after-save (its own new identity in the A0→A1→… chain), not to the current
post-A1 save alone.

## 3. Branch 8 (discovery boxes exactly-one): unresolved offline; census prescribed

### 3.1 The gate and its kinship to proven facts

Gate shape (`app/simulation/openttd/d5_freight_v2_package/main.nut`):
acceptance bound first (:654-658): `GSTile.GetCargoAcceptance(50862,
FREIGHT_CARGO, 1, 1, radius) == 8`; then the membership scan (:660-664):

```squirrel
local producing = DiscoveryBoxes(q, this.pickup, false)
local accepting = DiscoveryBoxes(q, this.delivery, true)
if (producing.ids.len() != 1 || accepting.ids.len() != 1) → INVALID_SITE
```

`DiscoveryBoxes` (:486-522) scans the stop's radius-3 coverage box and reads
`GSIndustry.GetIndustryID(tile)` per tile, role-filtered (pickup: last-month
production > 0; delivery: `IsCargoAccepted != CAS_ACCEPTED` filtered out).

Proven-by-receipt on the same world lineage: the acceptance bound — census
`d5-accept-survey-native-candidate-2` (E49): `accept-01-response.json` =
acceptance 8/8 at tile 50862, radius 3; radius-00 = radius 3. What no receipt
proves: the **member counts**. `GetCargoAcceptance` is an aggregate — 8/8 can
be one industry or several; `prod-00-response.json` measured only the pinned
industry id 0 (= 104); no op ever enumerated box membership on the D5 world.

### 3.2 World-binding check of the only retained industry inventories

The only industry listings on disk live in the attempt19 runtime area
(`artifacts/runtime/openttd-15.3-first-freight-delivery-attempt19/`). This
year's parse (proper double-escape unescape of `qualification-session.json`
`response_payload` strings) recovers a complete page of 6 industries,
ids 0–5; **every entry satisfies `tile = x + y·64`** (width-64 basis):

| id | tile | x | y |
|----|------|---|---|
| 0 | 532 | 20 | 8 |
| 1 | 1060 | 36 | 16 |
| 2 | 1684 | 20 | 26 |
| 3 | 2212 | 36 | 34 |
| 4 | 2836 | 20 | 44 |
| 5 | 3364 | 36 | 52 |

The layout is synthetic (two columns, regular spacing, alternating types),
max tile 3364 < 4096 = 64². The D5 world is pinned **256×256, seed-17**
(`docs/d5-corridor-freight-preparation.md` §2.1) and its live tiles
(45748, 50862, 45487 …) exceed 4096, so this inventory cannot describe the D5
world. `network-facts-0/1/2.json` `coverage` rows (`producer_count 1`,
`tile_id 402` — tile 402 = 18 + 6·64, same 64-basis) and
`world-planning-observation.json` (`relevant_industry_lifetimes` ids 0/2/4)
are from the same attempt19 world and equally not binding. No retained D2/D3
read receipt shows anything but per-tile `industry: null`.

Verdict: **branch 8 is not offline-resolvable from retained evidence.** The
producer_count-1 / prod-104 / accept-8 impressions in the v2 design lineage
mix D5-world measurements (prod-00, accept-00/01) with a different world's
inventory (attempt19) — the same class of stale cross-world assumption the
design review already logged for engine 123 and bay 50351 (E50 F-1/F-2
class).

### 3.3 Assertion limit of the acceptance API (why E49 cannot be stretched)

`GSTile.GetCargoAcceptance` returns an eighth-scale aggregate over the
census radius; we have no receipts bounding how many acceptors sum into 8,
and no D5-world receipt ties a specific industry id to a specific tile near
either stop. Exactly-one acceptor (and identity of the producer) therefore
requires a native enumeration, not a cleverer read of the existing receipts.

## 4. Prescription: `D5-BOX-CENSUS-1` before any freight re-staging

Design sketch (details settled in the census round with its own operator
gates; E47→E49 machinery and budgets are the precedent):

- Fresh identity `D5-BOX-CENSUS-1`, read-only census pipeline precedent
  (`corridor_accept_survey_native.py` style: prelaunch → review → Gate C
  signing → separate launch approval → census report; `max_cost 0`,
  `state_changed: false` on every exchange), world bound to the current
  D5 lineage of record with the fail-close re-binding discipline (E45 §1
  pattern).
- Ops of record (read-only, small, each response reporting a list, never
  enforcing exactly-one — every outcome must be learnable, which is the whole
  point of facts-before-staging):
  - pickup box scan, center 45748 = (180,178), radius 3 (x 177–183,
    y 175–181): per valid industry tile → {industry id, tile, last-month
    production of the corridor cargo};
  - delivery box scan, center 50862 = (174,198), radius 3 (x 171–177,
    y 195–201): per valid industry tile → {industry id, tile,
    `IsCargoAccepted` status};
  - chain continuity spot reads: industry 0 production (expect 104),
    acceptance at 50351 (expect 0) and at 50862 (expect 8) re-bound
    fail-closed from the retained census facts.
- Interpretation rules fixed now: scan returns exactly 1/1 → the gate cannot
  surprise; scan returns ≠1 in either box → the *site plan* adapts first
  (re-pin stop or pre-build acceptance), never the gate; scan tallies are
  recorded as census evidence in their own retained receipts.

### 4.1 Recommended sequencing

1. `D5-BOX-CENSUS-1` (read-only; independent of the fix; can go first so a
   box-shaped surprise cannot waste the demolished-and-rebuilt state).
2. F-12 world fix (§2.1) in its own mutation candidate with post-fix
   verification.
3. Fresh `D5-FREIGHT-4`: staging, independent review, Gate C re-sign,
   separate launch approval — with the prerequisite chain now
   census + post-fix after-save.

## 5. What this record does not do

No fix round, no general code review, no package edit, no candidate, no
launch; `artifacts/` untouched; `D5-FREIGHT-3` and all prior evidence
byte-unchanged and terminal. Each next step is a separate operator-approved
gate.

Evidence index E58.
