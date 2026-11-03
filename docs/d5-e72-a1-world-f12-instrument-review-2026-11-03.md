# E72 — A1 world evidence review and F-12 instrument correction (2026-11-03)

Status: read-only evidence review; the only writes are this document and the
E72 ledger rows. No source change, no
candidate staging, no signing, no launch, no AdminPort connection, no artifact
(`artifacts/`) modification, no Git mutation. All prior rows, verdicts and
retained bytes are untouched. This document records the E72 findings; the
`D5-F12-DEPOT-1` consumption (staging → verification → Gate C → one launch)
facts it reviews are already byte-preserved in
`artifacts/experiments/d5-corridor-depot-mutation-native-candidate-1/` and are
summarized here cross-referenced, never relabeled.

## 1. Purpose and method

The `D5-F12-DEPOT-1` native run (one operator-approved launch, 2026-11-03)
halted at its FIRST exchange (`before-00`) with a wire STAGE that read
`depot_present: False, front_read: -1, owner: -1, depot_linked: False`,
where the E58 §2.1 before-gate of record prescribes
`depot_present True / front_read 45743 / owner 0 / depot_linked True`. The
harness refused fail-closed (`STALE_PIN`, zero dispatch, world untouched,
`PHASE_HALTED_PREFIX_PRESERVED`). E72 re-establishes, from retained evidence
only, the actual A1 world state at tiles `44983`, `45743`, `45487`, `51116`,
and separates world facts from instrument facts.

Method: the census is receipt-and-source based (the E57 precedent — no `.sav`
parse needed, per-session save bytes merely re-serialize the same content).
Read inputs:

- `artifacts/experiments/d4-corridor-native-candidate-5/` — `depot-06-*` /
  `confirm-06-*` (protocol-4 native depot reads; the only operations anywhere
  in the lineage to touch 45487).
- `artifacts/experiments/d5-corridor-extension-native-candidate-3/` — the A1
  consumed schedule (`full-00`/`road-01`/`spur-02`/`station-03`/`route-00`,
  `accept-01`) and `after.sav`.
- `artifacts/experiments/d5-box-census-native-candidate-2/` — protocol-9
  census reads (`pbox-*`, `dbox-*`, `prod-00`, `acc-01`),
  plan `deb121ad…690f`, attempt `D5-BOX-CENSUS-2`.
- `artifacts/experiments/d5-corridor-freight-native-candidate-3/` — the E56
  consumed site-00 attempt (terminal `INVALID_SITE`, no observation set on
  the wire by design).
- `app/simulation/openttd/d4_corridor_package/main.nut`,
  `app/simulation/openttd/d5_freight_v2_package/main.nut`,
  `app/simulation/openttd/d5_depot_mutation_package/main.nut` — the three
  depot-probe implementations.
- `ottd/src/script/api/script_road.cpp`, `ottd/src/script/api/script_object.cpp`,
  `ottd/src/script/script_storage.hpp` — OpenTTD 15.3 script context source.

## 2. The consumed attempt's terminal state (preserved verbatim)

| Fact | Value |
|---|---|
| Attempt / seal | `D5-F12-DEPOT-1` / `9b0e01417a3e5a8ae9584a6d86285c9ee0b7f89517f970b38331102938ae12fe` |
| Plan digests | schedule `49f5b510b2c659946fcbfbfaa4885365cf05c1453dccb1ccfc417a2d4bae1382`, mutation schedule `8be74b2c651e35228618f06f177c2142dcc62edaf3d6b7bde3f7f6976e7ccc18` |
| Authorization | record `73734487b3de289e5f8dc7cdba98b90431c09c5bd1f0333db00e14d22f872463`, payload `f2ab5cd9…9085`, verified under pinned anchor `cbb63ff5…40c614` before write |
| Claim | consumed exactly once (`CLAIM.json` `consumed: true`, `LAUNCH-CONSUMED.json` binds auth + seal) |
| Halt | `before-00` (the only exchange), `not dispatched`, `exchanges: []`, `mutated: []`, `requests: 1`, `state_changed: false`, `status PHASE_HALTED_PREFIX_PRESERVED`, `verified: false`, exit 1 |
| Halt error (verbatim) | `ValueError: the depot mutation exchange before-00 failed verification: STALE_PIN: the before-00 observe gate diverged from the E58 prescription — depot_present: measured False, prescribed True; front_read: measured -1, prescribed 45743; owner: measured -1, prescribed 0; depot_linked: measured False, prescribed True` |
| before-00 wire (verbatim) | `{"company": 0, "connected_depot_to_front": false, "connected_front_to_depot": false, "cost": 0, "delivery": 50351, "depot": 45487, "depot_linked": false, "depot_present": false, "front_read": -1, "funds": 490257, "max_cost": 3000, "op": "observe", "owner": -1, "pickup": 45748, "plan": "9b0e0141…12fe", "protocol": 10, "request_id": "before-00", "status": "READY"}` |
| Cleanup | graceful attempted (`quit_requested`, `reaped`, returncode 0, `remaining_processes: []`) but `verification_error: "Live or ambiguous endpoint socket: {'table': 'tcp', 'local': '127.0.0.1', 'local_port': 49787, 'remote': '127.0.0.1', 'remote_port': 47366, 'state': 5, 'inode': 0}"` → `cleanup_complete: false` / `cleanup_failure: true` |
| Session log key line | `[18] [I] D5_F12_DEPOT before-00 READY` — the script handled the observe and replied READY with its (defect-scoped) facts; then disconnect, network shutdown, map saved |

The world was never mutated. The budget consumed: 1 launch, 1 connection,
1 request of 32. The attempt is terminal and stays terminal.

## 3. Tile-by-tile findings and classification

Classification legend: `RECEIPT_VERIFIED` (native readback receipts on disk),
`CENSUS_VERIFIED` (the retained `D5-BOX-CENSUS-2` protocol-9 receipts),
`CONTRADICTED` (a measurement contradicted by the receipt record; cause
resolved below), `UNKNOWN` (no evidence).

| Tile | Fact | Classification | Evidence |
|---|---|---|---|
| `44983` | pickup producer industry: id `0`, production `104`, exactly-one in the pickup box (center `45748`, r3) | **CENSUS_VERIFIED** | `d5-box-census-native-candidate-2/pbox-00-response.json` row `{"a": 0, "id": 0, "p": 104, "tile": 44983}`, `count 1`, `more false`; `pbox-01`/`pbox-02` empty (cursors `3`/`6`); `prod-00-response.json` `prod: 104` |
| `51116` | delivery acceptor industry: id `1`, production `-1`, exactly-one in the delivery box (center `50862`, r3); box acceptance `8` at `50862` r3 | **CENSUS_VERIFIED** | `dbox-00-response.json` row `{"a": 1, "id": 1, "p": -1, "tile": 51116}`, `count 1`, `more false`; `dbox-01`/`dbox-02` empty; `acc-01-response.json` `accept: 8`, `radius: 3`, `tile: 50862` |
| `45743` | depot-front road tile: present, company-0 corridor bits laid by D4 run A (`45747→45743`, 5 tiles); the depot-facing (north) stub was never built — the directed edge `45743↔45487` reads false in both directions on the A1 world | **RECEIPT_VERIFIED** (edge false proven natively at E56) | D4 candidate-5 route read `ROUTE_VERIFIED` 23/23 incl. run A; `E56`'s site-00 `INVALID_SITE` fired AFTER the sequential identity branch (below), and the only in-chain failure left is the F-12 directed edge probe — the E57 diagnosis confirmed by source (`script_road.cpp:107-125`, `road_map.cpp:54-70`) |
| `45487` | road depot EXISTS on the A1 world: company-owned (owner `0`), front tile `45743`, identity-linked true; NOT the entry factor (the missing stub) — exactly the E58 §2.1 F-12 starting state | **RECEIPT_VERIFIED** (depot identity) + the F-12 before-00 "absent" read **CONTRADICTED** (instrument false negative, §4) | D4 `depot-06-response.json` (`{"depot": true, "depot_front_id": 45743, "depot_linked": true, "front_owner": 0, "cost": 390, …}`) and `confirm-06-response.json` (`{"depot": true, "depot_front_id": 45743, "depot_linked": true, "front_owner": 0}`, protocol 4 `READ`) on the world that became A1's source; A1's retained receipts contain no demolish and no op touching 45487; A1 `after.sav` re-digests `3748e00ce57bcb076466f50cac3776c202b4fd130d6c6071935e9d43e45420bd` on disk today |

`UNKNOWN` items on these four tiles: none. (The E58-era branch-8 uncertainty
on the census boxes was resolved by the consumed `D5-BOX-CENSUS-2`: both
boxes measure exactly-one.)

## 4. Root cause: the before-00 depot-absent read was an instrument false negative

### 4.1 The measurement decode

`DepotObserveFacts` in `app/simulation/openttd/d5_depot_mutation_package/main.nut`
(:108-127, staged copy byte-identical to the tree, sha `57775cbb…68e6`) reads:

```squirrel
local depot = GSRoad.IsRoadDepotTile(this.depot_tile)          // 45487
local front_read = depot ? GSRoad.GetRoadDepotFrontTile(...) : -1
local owner = depot ? GSTile.GetOwner(...) : -1
```

The response's `front_read: -1` and `owner: -1` are short-circuits of
`depot == false`; the ONLY world measurement in the whole divergence is
`GSRoad.IsRoadDepotTile(45487) == false`.

### 4.2 The OpenTTD 15.3 script-context dependency (source-verified)

- `ottd/src/script/script_storage.hpp:67`:
  `RoadType road_type = INVALID_ROADTYPE;  ///< The current roadtype we build.`
  — every script's per-script storage initializes the current road type to
  `INVALID_ROADTYPE` and nothing in the engine sets it for the script.
- `ottd/src/script/api/script_road.cpp:44-51` —
  `ScriptRoad::IsRoadDepotTile`:
  `if (!IsRoadTypeAvailable(GetCurrentRoadType())) return false;`
  then the present-road-type test. With the current road type unset the
  function fail-closes to `false` for ANY tile.
- Same fail-close in `ScriptRoad::GetRoadDepotFrontTile` (:497-502, returns
  `INVALID_TILE`) and `ScriptRoad::AreRoadTilesConnected` (:111).
- `ScriptRoad::IsRoadTile` (:40-42) has NO such guard (truthful either way),
  but no road-presence fact about 45743 was carried on the before-00 wire.

Consequently a script that probes without first calling
`GSRoad.SetCurrentRoadType(GSRoad.ROADTYPE_ROAD)` reads
`IsRoadDepotTile == false` for every tile, regardless of the world.

### 4.3 F-12's dispatch never establishes the context

`DepotHandle` (:314-377) enters `GSCompanyMode`, reads funds, and dispatches
ops — with NO road-type set; `Start` (:381-390) doesn't set one either. The
only two `GSRoad.SetCurrentRoadType` call sites in the whole package are at
:172-173 (inside `DepotRoadOp`) and :194-195 (inside `DepotDepotOp`) — both
AFTER their operators' `STALE_PIN` pre-checks, which themselves call the
fail-closed probes. `DepotObserveOp` (the `before-00`/`after-00` gate
exchange) and `DepotDemolishOp` (the `demo-00` pre-check) never set the road
type at all. So `before-00`'s observe ran with `road_type = INVALID_ROADTYPE`
and read `IsRoadDepotTile(45487) == false` — a pure instrument false negative,
identical for any tile.

The fail-closed architecture behaved exactly as designed on that reading: the
python-side before-gate refused `STALE_PIN` with the raw measured values
BEFORE any command (`last_status: NOT_DISPATCHED`, zero mutations, the
world and the attempt's prefix preserved).

### 4.4 Why every predecessor package measured `true` where F-12 measured `false`

The family established pattern is per-request context set + assert, inside
company mode, BEFORE any probe:

- D4 (`d4_corridor_package/main.nut:660-662`): sets
  `GSRoad.SetCurrentRoadType(GSRoad.ROADTYPE_ROAD)`, then
  `if (GetCurrentRoadType() != 0 || !IsRoadTypeAvailable(0))` →
  `UNSUPPORTED_NATIVE_FACT`, and only then dispatches ops — which is why
  D4's protocol-4 `depot-06`/`confirm-06` natively measured
  `{"depot": true, "depot_front_id": 45743, "depot_linked": true}`.
- D5-v2 (`d5_freight_v2_package/main.nut:1684-1690`): identical set+assert
  per request before `SiteOp` — which is why at E56 the sequential site
  refusal chain (`main.nut:620-635`: identity branch
  `!obs.depot.depot || obs.depot.owner != q.company ||
  obs.depot.front_id != this.depot_front || !obs.depot.linked` FIRST, the
  F-12 edge branch `!obs.depot.edge` SECOND) could only have fired at the
  edge branch — the E57 diagnosis, re-confirmed here.

F-12 is the single package of the family whose observe/gate path runs the
fail-closed probes without the context set.

### 4.5 Why the E70 offline validation could not catch it

The 73 passing offline suites compile the script and validate the wire
contract, staged pins and gates, but the road-type fail-close is a
native-runtime-only behavior: Squirrel compiles the calls without any
context check, and no offline suite can reproduce the engine's
`ScriptStorage` initialization. Native behavior is only observable natively,
which is operator-gated by policy.

## 5. Which E58 assumptions were incorrect

**None of the E58 world assumptions were wrong.** The depot at `45487`
exists, is company-0, fronts `45743`, is identity-linked, and its directed
entry edge reads false both ways — exactly the E58 §2.1 F-12 starting
diagnosis, and exactly what the demolish → road-pair → rebuild sequence
corrects. The census tiles (`44983`/`51116`) are re-confirmed by the
consumed box census and their facts carry into any later `D5-FREIGHT-4`
binding unchanged.

What WAS incorrect: the F-12 instrument's handling of the script road-type
context that every predecessor package establishes per request. The
before-00 gate's "prescribed" values were correct; the "measured" values
were not a measurement of the world at all — `IsRoadDepotTile` fail-closed
on the missing context before any world state was consulted.

## 6. Corrected F-12 design recommendation (fix round F-12b)

Scope: the F-12 mutation design, the E58 prescription, the protocol-10 wire
contract, the python-side pins, gates, schedules and budgets are all KEPT
unchanged. The single defect is bridge-layer and the fix is script-only:

1. In `app/simulation/openttd/d5_depot_mutation_package/main.nut`, establish
   the road-type context at dispatch entry, before ANY ScriptRoad probe,
   mirroring the D4/v2 pattern verbatim: inside `GSCompanyMode` at
   `DepotHandle`'s op dispatch, before the op switch:
   `GSRoad.SetCurrentRoadType(GSRoad.ROADTYPE_ROAD)` followed by the assert
   `GSRoad.GetCurrentRoadType() != 0 || !GSRoad.IsRoadTypeAvailable(0)` →
   reply status `UNSUPPORTED_NATIVE_FACT`. This covers `observe`, `demolish`,
   and the road/depot pre-checks; the existing set calls inside
   `DepotRoadOp`/`DepotDepotOp` become idempotent re-assertions and STAY
   (defense in depth, byte-minimal diff).
2. No runner change: the python side already treats an unexpected status as
   a recorded refusal; `UNSUPPORTED_NATIVE_FACT` joins the existing
   terminal-status handling unchanged.
3. Fresh attempt identity `D5-F12-DEPOT-2`, fresh candidate directory and
   seal, full gate sequence exactly as the commands of record in REPRODUCE.md
   prescribe; the consumed `D5-F12-DEPOT-1` stays terminal, byte-preserved,
   never retried, never relabeled.
4. Expected native reads after the fix (all instrument-verifiable):
   `before-00` → `depot_present true / front_read 45743 / owner 0 /
   depot_linked true / both directions false`; `demo-00` → demolish from the
   standing depot; `road-00` → pair build lays the missing north stub on
   45743 and the south bit on 45487; `depot-00` → rebuild with front 45743;
   `after-00` → same identity with both directions true; `fleet-00` → zero
   fleet. Funds chain pins `490257 → 490357 → 490157 → 488957 → 488957 → 488957`.
5. Cleanup: attempt-1's cleanup verdict (`cleanup_failure: true` with the
   live-or-ambiguous-endpoint socket ambiguity above) is preserved as
   reported; the cleanup machinery of the next attempt is unchanged and
   remains subject to its own certification gate.

## 7. Sequencing of record from here

1. (Operator-approved fix round) the §6.1 script-only correction + focused
   offline suites re-run on the touched files (`test_corridor_depot_mutation.py`,
   `_vm`, `_native` suites per REPRODUCE.md commands of record), E-row
   recording.
2. Stage `D5-F12-DEPOT-2` (fresh identity), staging approval, independent
   read-only verification.
3. Gate C signing once (Option-1 checklist), then ONE launch approval.
4. On `F12_MUTATION_COMPLETION_VERIFIED` + certified cleanup: the verified
   after-save becomes the new authoritative world binding, and only then
   may `D5-FREIGHT-4` staging resume (its E65 census facts and E53 budgets
   are preserved unchanged; sequencing of record remains:
   census → F-12 → `D5-FREIGHT-4`).
5. `D5-F12-DEPOT-1` remains terminal with `PHASE_HALTED_PREFIX_PRESERVED`;
   no retry, no relabel, no second launch of it under any circumstances.

## 8. Preservation statement

Strictly read-only execution of E72: no source change, no candidate staging,
no signing, no launch, no AdminPort connection, no `artifacts/` write, no
Git mutation, no rerun of any completed offline suite. The only writes are
this document and the E72 ledger rows appended to `EVIDENCE_INDEX.md`,
`TASKS.md` and `AI_HANDOFF.md`. `E68` and every historical verdict stand
unchanged.

## 9. F-12b fix round record (E73, 2026-11-03)

Operator-approved fix round implementing §6 exactly as prescribed, offline
only (no candidate staging, no signing, no launch, no AdminPort, no
`artifacts/` write, no Git commit; `D5-F12-DEPOT-1` and all historical bytes
untouched; `CONTEXT.md` pin `36648f9c…cc29` intact).

### 9.1 The exact fix (script-only, no runner/contract change)

`app/simulation/openttd/d5_depot_mutation_package/main.nut`, `DepotHandle`
dispatch entry — after the funds readback and before the op switch, the
D4/D5-v2 per-request pattern verbatim (E56-era `d4_corridor_package/
main.nut:660-662`, `d5_freight_v2_package/main.nut:1684-1690`):

```squirrel
GSRoad.SetCurrentRoadType(GSRoad.ROADTYPE_ROAD)
if (GSRoad.GetCurrentRoadType() != 0 ||
    !GSRoad.IsRoadTypeAvailable(0)) {
    r.status = "UNSUPPORTED_NATIVE_FACT"
} else if (q.op == "observe") { ...
```

`UNSUPPORTED_NATIVE_FACT` is already a contract-legal refusal status
(`corridor_depot_mutation.py:114`, refusal frames carry no observation set
by contract). The existing in-op `SetCurrentRoadType` calls
(`DepotRoadOp`/`DepotDepotOp`) are kept as idempotent re-assertions; no
admission check, gate, budget, schedule, status ordering or funds chain
changed; the six-exchange schedule and the E58 §2.1 prescription are
untouched.

### 9.2 Regression coverage (the true red-green wall)

`tests/test_corridor_depot_mutation.py` — the shared VM stub `GSRoad` now
models the 15.3 native fail-close faithfully (the canonical-VM precedent):
the per-script context initializes to `INVALID_ROADTYPE = 63`
(`road_type.h:28`, mirroring `script_storage.hpp:67`), every depot/edge
probe gates on `IsRoadTypeAvailable(GetCurrentRoadType())`
(`script_road.cpp:44-51`/`:111`/`:497-502`), `SetCurrentRoadType` silently
no-ops an unavailable type, and `IsRoadTile` stays unguarded like the
engine (`:40-42`). An offline fidelity probe confirms the model reproduces
the consumed attempt's exact reading: unset context →
`IsRoadDepotTile(45487) == false` → after set → `true` (discarded `/tmp`
probe per the E60 precedent). With that model in place, if the dispatch-entry
set were absent, `before-00` would again measure the depot absent and every
schedule test would fail — the whole suite is the net.

Two focused tests added (`tests/test_corridor_depot_mutation_vm.py`):

- `test_dispatch_establishes_the_native_road_context_before_probes` —
  fresh VM starts at context 63; a real before-00 observe reads `READY`
  with `depot_present true / front_read 45743 / owner 0 / depot_linked
  true` and the context stands at 0 afterwards.
- `test_dispatch_assert_refuses_when_the_road_type_is_unavailable` — with
  the road type unavailable, the dispatch assert fires
  `UNSUPPORTED_NATIVE_FACT` before any probe (no unclaimed facts, context
  never faked).

### 9.3 Validation of record (each exit 0)

Same commands of record as the E70 round (REPRODUCE.md): suites
`29 + 10 + 36 = 75 passed` (was 73; the two E73 regression tests join the VM
suite), `ruff` all-passed on the touched python paths + package dir, and
`git diff --check` clean (whitespace); `uvx ty check` clean on the
documented file set.

### 9.4 Remaining risks and unchanged standing

- The fix is validated offline only; the road-context fact is
  native-runtime behavior, and the next native proof is the
  `D5-F12-DEPOT-2` launch itself (its expected `before-00` read is pinned
  in §6.4).
- Cleanup certification machinery is unchanged (attempt-1's
  `cleanup_failure: true` socket ambiguity stands preserved as reported).
- Tree state after the round: `main.nut` + the two test files modified,
  uncommitted (habitual WIP discipline); the staged `D5-F12-DEPOT-1`
  candidate bytes retain their seal and stay consumed/terminal; the next
  candidate is fresh identity `D5-F12-DEPOT-2` whose staging will re-derive
  digests from the fixed package — staging approval not yet granted. Zero
  other behavior changed; e.g., the census/freight packages are untouched.
