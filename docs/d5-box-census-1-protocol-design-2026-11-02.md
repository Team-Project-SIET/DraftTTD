# D5-BOX-CENSUS-1 — protocol design (E59)

Status: docs-only offline design, 2026-11-02. Design only — no source
implementation, no candidate staging, no evidence mutation, no signing,
no AdminPort connection, no OpenTTD launch, no Git mutation. `artifacts/` and
`D5-FREIGHT-3` untouched; `E58` text intact. Implementation is a separate
operator-approved round with its own staging, review, Gate C signing and
launch-approval gates (E49 lifecycle precedent).

## 1. Purpose and evidence base

`E58` left branch 8 (v2 discovery boxes exactly-one) unresolved from
retained evidence and prescribed this census: a read-only native enumeration
of the two radius-3 stop boxes of the D5 world so that the v2 site gate
(`app/simulation/openttd/d5_freight_v2_package/main.nut:660-664`,
`DiscoveryBoxes` :486-522) is predictable before `D5-FREIGHT-4` spends a
launch. Facts of record the census re-measures fail-closed (all from
`artifacts/experiments/d5-accept-survey-native-candidate-2/`, E49):

- `radius-00`: truck-stop coverage radius **3**.
- `accept-00` (tile 50351, r 3): cargo-1 acceptance **0**.
- `accept-01` (tile 50862, r 3): cargo-1 acceptance **8**.
- `prod-00` (industry id 0): last-month production **104**.

World of record: the pinned 256×256 Seed-17 corridor world
(`docs/d5-corridor-freight-preparation.md` §2.1); all retained industry
inventories (`E58` §3.2) bind the attempt19 world and are non-evidence here.

## 2. Protocol decision

New **protocol 9** wire contract in a new module
`app/simulation/openttd/corridor_box_census.py`, additive over the shared
machinery (`canonical_bytes`, `TileID`/`TileID`-family bounds,
`validate_request_id`, the Digest type). Protocol number allocation of
record: 4 construction, 5 freight v1, 6 accept-survey, 7 terrain survey,
8 freight v2 → 9 is the next free number. Reason to add a protocol instead
of extending protocol 6: the E51 precedent — v2 freight kept the protocol-5
bytes unmodified rather than retrofitting the consumed survey families — and
the list-shaped rows do not fit `SurveyReadback`'s strict scalar subsets
without weakening the frozen contract the consumed E47/E49 records verify
against.

GameScript side: a **separate composed package directory**
`app/simulation/openttd/d5_census_package/` (own `main.nut`/`info.nut`,
own staged composition identity), so the shipped `d5_freight_package`
bytes (the frozen source the E47 staged composition pinned at
`0337fb36…97ae`) do not drift for the bridge handler's sake. The census
handler mirrors `SurveyHandle` (`d5_freight_package/main.nut:255-344`):
same field checks, same one-shot budget accounting, same halt discipline,
separate `census_planned` table and `q.op` whitelist.

## 3. Wire contract

### 3.1 Constants

```
CENSUS_PROTOCOL = 9
MAX_CENSUS_REQUEST_BYTES = 512          # survey-6 precedent bound
MAX_CENSUS_RESPONSE_BYTES = 512
MAX_BOX_PAGE_ROWS = 3                   # rows per box page response
MAX_BOX_PAGES = 3                       # pbox/dbox page exchanges per box
BOX_PAGE_CURSORS = (0, 3, 6)            # static cursor grid; drained pages are READY-empty
CENSUS_REQUEST_BUDGET = 32              # same per-session cap as survey-6
CENSUS_COMPANY = 0
CENSUS_CARGO_ID = 1
FUNDS_PIN = 490257                      # A1 close-out level (E44/E49/E56)
PICKUP_CENTRE = 45748                   # v2 pickup stop, box centre
DELIVERY_CENTRE = 50862                 # v2 delivery stop, box centre
SPOT_CONTROL_TILE = 50351               # expected 0 (E49 accept-00)
SPOT_STOP_TILE = 50862                  # expected 8 (E49 accept-01)
SPOT_PROD_INDUSTRY = 0                  # expected 104 (E49 prod-00)
```

Tile bounds reuse the 256×256-safe `TileID <= 65535` family. Industry ids
are validated `0 <= id <= 65535` (native industry pool is a 16-bit index —
confirm against the 15.3 pool at implementation; open question 3).

### 3.2 Ops

Four ops; three are byte-comparable re-measures of E49's instruments, one
is new:

| op | request carries | reads natively | response data |
|----|-----------------|----------------|---------------|
| `radius` | — | `GSStation.GetCoverageRadius(GSStation.STATION_TRUCK_STOP)` | `radius 0..255` |
| `accept` | `tile` ∈ {50351, 50862} | `GSTile.GetCargoAcceptance(tile, 1, 1, 1, radius)` | `accept 0..8`, `tile` echo, `radius` echo |
| `prod` | — | `GSIndustry.GetLastMonthProduction(0, 1)` | `prod 0..2^31-1` |
| `box` | `tile` ∈ {45748, 50862}, `cursor` ∈ {0, 3, 6} | 49-tile scan | `rows`, `count`, `more`, `cursor` echo, `tile` echo |

`box` scan semantics (the census core, mirroring `DiscoveryBoxes` exactly):

- Iterate the 7×7 box around the centre in **`DiscoveryBoxes` iteration
  order**: `dy` from `-radius` to `+radius` outer, `dx` inner, i.e. tile
  sequence deterministic; skip out-of-map tiles; the radius is the freshly
  measured native radius (radius must already be measured this session).
- For each tile: `ind = GSIndustry.GetIndustryID(tile)`; `null`/`< 0`/an
  invalid id is not a member (source:
  `ottd/src/script/api/script_industry.cpp:41-42`).
- Per distinct industry id record `p = GSIndustry.GetLastMonthProduction(
  ind, 1)` (negative → `D5_NATIVE_FACT` throw, `SurveyProdOp` precedent) and
  `a = GSIndustry.IsCargoAccepted(ind, 1)` (source-verified values:
  `0 = CAS_NOT_ACCEPTED`, `1 = CAS_ACCEPTED`, `2 = CAS_TEMP_REFUSED`,
  invalid industry/cargo → 0 — `script_industry.cpp:69-81`), plus
  `tile` = the **minimum tile index** of the box tiles belonging to that
  industry (deterministic anchor).
- Industry-role definitions (fixed here, matching the v2 gate):
  *producer* iff `p > 0` (v2 :510-512), *acceptor* iff `a == 1`
  (v2 :507-508). Rows carry raw `p`/`a`; the Python report derives roles —
  never the GameScript.
- Rows are ordered ascending by industry id per page; pages are position-
  cursor slices of the full deterministic membership list (`cursor` =
  number of ids drained before this page).
- A page beyond the drained set is **READY with an empty `rows` list and
  `more = false`** — a drained page is a measurement of absence, never a
  refusal. If the third page still reports `more = true` (≥ 10 distinct
  industries in the box), the census completes with an explicit
  **overflow finding**; nothing is enforced, nothing silently discarded.

### 3.3 Request model

```
CensusRequest: protocol: Literal[9] = 9
  op: Literal["radius","accept","prod","box"]
  request_id: ^[a-z0-9-]{1,32}$
  plan: Digest (64 hex)
  company: 0, max_cost: = 0
  pickup/delivery/depot: fixed corridor pins 45748 / 50351 / 45487
  tile: TileID | None          # required on accept and box, null otherwise
  cursor: 0..6 | None          # required on box, null otherwise
```

Correlation pins echo the survey's corridor identity defence (refused
before any observation on drift — `SurveyRequest.coherent` precedent).
Box op pins: maximum request ≈ **217 B** (measured worst case), far inside
512.

### 3.4 Response model

```
CensusReadback: protocol: Literal[9]
  op, request_id, plan, company, max_cost, pickup, delivery, depot
  status: READY | UNSUPPORTED_NATIVE_FACT | INVALID_LOCATION |
          INVALID_COMPANY | PAUSED | STALE_PIN | OUT_OF_ORDER
  funds: SignedMoney, cost: Money
  radius / accept / prod: as survey-6 domains
  tile | None                   # echoed on accept and box success
  cursor | None, count | None, more | None
  rows | None                   # list of row records
row = {id: 0..65535, tile: TileID, p: 0..2^31-1, a: 0..2}
```

Strict per-op field subsets as in survey-6: refusals carry **no
observation set**; success subsets complete; `parse_for` re-checks the
correlation keys (`protocol, op, request_id, plan, company, max_cost`),
the corridor pins and the `tile`/`cursor` echoes. Box-page consistency
validators: `cursor` == planned page cursor of that request_id; `rows`
sorted ascending by `id`, `len(rows) <= 3`; every `row.tile` inside
`ABS(tile_x - centre_x) <= r` and `ABS(tile_y - centre_y) <= r` (tile
arithmetic over the pinned 256-wide map); `rows` is the ascending id slice
`[cursor, cursor + 3)` of the box membership, so a cursor at or past the
membership count yields a READY-empty drained page (`more = false`);
`more == (count > cursor + len(rows))`; no id repeated across pages of one
box. A `radius` echo is required before any `accept`/`box` success is
recorded (survey-6 ordering rule).

Measured response budget (worst widths, all fields max):

| frame | bytes |
|-------|-------|
| box request (worst) | 217 |
| box response, page 3, worst rows — the handler-emitted table shape (a
  Squirrel table carries no null keys, so its never-assigned `accept`/
  `prod`/`radius` observation fields cost zero wire bytes) | **431** (slack 81) |
| box response, page 3 in the Python-side null-inclusive canonical form
  (the parse-side audit shape; never wire bytes) | 471 |
| spot response (retained receipts: 246–274 B) | ≤ 512 |

Page size 3 is chosen on the page-4 margin (a same-audit page 4 measures
478, margin 34 B) and 9 enumerable ids per box exceeds the v2 gate's own
8-role bound, so pages never hide rows silently: anything past page 3 with
`more = true` is an explicit overflow finding — nothing observable
disappears. (Implementation-round byte audit, E60: the two wire rows above
were re-measured against the compiled contract and confirmed exact; the
audit additionally records the null-inclusive parse-side canonical 471 B,
which the GameScript wire never emits.)

## 4. GameScript package (d5_census_package)

Composition mirrors the survey package shape:

- `census_planned` = the ten rows of §5, each `[request_id, op, "READY"]`;
  shared corridor pins; `used` one-shot id set; the same 32-request cap.
- `CensusHandle(q)` — field checks and correlation checks as
  `SurveyHandle` (:255-344): id shape, `Hex64(plan)`, company 0,
  `max_cost == 0`, unique corridor pins; per-op field presence exactly as
  §3.3; `plan_id` latch; refusal ladder `OUT_OF_ORDER → INVALID_COMPANY →
  STALE_PIN → PAUSED → handlers`; funds read at the exchange boundary
  (`GSCompany.GetBankBalance`), never changed; `GSAdmin.Send(r)`; log
  `D5_CENSUS <request_id> <status>`; stage advance only on the exact READY
  of the planned exchange, halt otherwise (prefix-preserving).
- `BoxScanOp(q, r)`: pin/cursor validation; native radius re-fetched and
  echoed; 49-tile scan per §3.2; page slice; bounds guard `D5_NATIVE_FACT`
  on any negative production read; response guard mirrors `SurveyGuard`
  (`D5_RESPONSE_OUT_OF_BOUNDS` class on rows domains).
- No mutation of any kind; company-mode observation only.

## 5. Execution schedule (exact: 10 planned exchanges)

```
radius-00  radius   tile=null
acc-00     accept   tile=50351   expected 0   (E49 accept-00 control)
acc-01     accept   tile=50862   expected 8   (E49 accept-01 stop)
prod-00    prod     tile=null
pbox-00    box      tile=45748   cursor 0
pbox-01    box      tile=45748   cursor 3
pbox-02    box      tile=45748   cursor 6
dbox-00    box      tile=50862   cursor 0
dbox-01    box      tile=50862   cursor 3
dbox-02    box      tile=50862   cursor 6
```

10 planned exchanges, request budget 32, one launch, one connection, zero
retries/reconnects, `max_cost = 0`, no window lease. Spot reads come first
so a wrong-world load is caught before any box row is trusted (the E45
"positive control halts, never relabeled" discipline); box pages after —
box facts are meaningless if the controls do not reproduce, so a spot
divergence halts the census prefix-preservingly rather than being
recorded alongside box rows.

## 6. World and prerequisite binding

Prerequisite = the consumed A1 extension attempt of record
(`artifacts/experiments/d5-corridor-extension-native-candidate-3/`,
attempt `D5-CORRIDOR-EXTENSION-3`, seal `404d42d9…6acd8` consumed,
after-save `3748e00c…5420bd`, replay `EXTENSION_COMPLETION_VERIFIED`) —
the same chain anchor the E47 survey candidates bound. Every D5 native
session since A1 reloads the identical world state (staged `source.sav`
consumed as session input; session-owned re-saves re-serialize the same
content — E49 documented behaviour, so no `.sav`-byte-pin is implied).
Funds pin 490257 (A1 close-out receipts; re-measured unchanged at E49 and
E56). The functional identity of the world is asserted by the three spot
reads reproducing E49 — no industrial placement is assumed from any other
world's inventory (`E58` §3.2).

Prelaunch schema `d5-box-census-prelaunch-v1`, attempt map
`{1: "D5-BOX-CENSUS-1"}`, plan/schedule digest pins staged == derived,
prerequisites binding, budgets, preflight refusal gates, one-launch
executor and the funds/max-cost echo checks are the E47 survey-native
pattern re-used by import (shared ceremony, new schedule family).

## 7. Receipts, verification, replay, failure behaviour

- Per-exchange receipt `company-box-census-receipt-v1`: the survey receipt
  shape plus box fields (`tile, cursor, count, more, rows`) on `box`;
  correlation `plan_digest`, `seal`, status, funds echoed.
- Phase outcome `box-census-phase-outcome-v1`: fail-closed over preserved
  frames only; observation kinds `MEASURED / REFUSED / MISSING /
  MALFORMED`; the first halt ends verification, earlier receipts preserved,
  later planned exchanges pending; an unfinished schedule can never
  manufacture success.
- Success also re-derives, offline, from rows alone: the role-filtered
  v2 membership (producer filter `p > 0`, acceptor filter `a == 1`,
  iteration in `DiscoveryBoxes` order) per box, and whether the branch-8
  gate (`ids.len() == 1` both boxes) would pass, overflow, or fail —
  recorded as census facts, not as admissibility claims.
- Spot divergence (`acc-00 != 0`, `acc-01 != 8`, `prod-00 != 104`): halt
  with the divergent value recorded verbatim (`CENSUS_HALTED_
  EVIDENCE_PRESERVED`-class arm); never relabeled, never downgraded.
- Refusals (`INVALID_LOCATION`, `INVALID_COMPANY`, `PAUSED`,
  `STALE_PIN`, `OUT_OF_ORDER`, `UNSUPPORTED_NATIVE_FACT`) carry no
  observation set; MISSING/MALFORMED are recorded per exchange.
- Native replay verifier arms: `CENSUS_COMPLETION_VERIFIED` (all 10 READY,
  budgets intact, cleanup certified) / `CENSUS_HALTED_EVIDENCE_PRESERVED`
  / unresolved-arm classes; `verify` exit codes 0/1 as the survey
  pipeline does.

## 8. Outcome matrix (every result observable)

| outcome | meaning | next action (E58 ladder) |
|---------|---------|--------------------------|
| both boxes role-filtered exactly 1 | branch 8 predictable-true on the unchanged world | proceed fix → `D5-FREIGHT-4` |
| any box ≠ 1 | the site plan must adapt (re-pin stop / pre-build acceptance) | design round before any fix |
| overflow (`more=true` on page 3) | ≥ 10 industries in a box; members partially listed | adaptation finding; census still terminal-success |
| empty box (`count = 0`) | no industry in the box — a real fact, never refused | adaptation finding |
| spot divergence | world/control mismatch | halt; lineage investigation before anything else |
| refusal/missing/malformed | wire/world defect | halt; evidence preserved |

## 9. Tests and implementation plan (a later operator-approved round)

1. `app/simulation/openttd/corridor_box_census.py` — wire module per §§3.
2. `app/simulation/openttd/proof/corridor_box_census_native.py` — staging/
   preflight/execute/replay per §6/§7 (corridor_accept_survey_native
   pattern, shared ceremony by import).
3. `app/simulation/openttd/d5_census_package/` — package per §4.
4. `tests/test_corridor_box_census.py` — VM wire tests: plan pins, op
   subsets, row domains, page/cursor consistency, worst-case byte audit
   (assert the §3.4 numbers under max-width rows), spot-divergence halt,
   offsets/pagination determinism.
5. `tests/test_corridor_box_census_native.py` — staged-vs-derived digests,
   prerequisite re-verification, preflight refusal matrix, offline
   consumed synthetic replays (complete, drained-page, overflow, halt
   arms, tamper matrices), verify-CLI exit codes.
6. Package VM tests for the census handler (planned table, guards, echo
   discipline, one-shot budget).
7. `REPRODUCE.md` gains the census commands of record only after
   implementation exists.

## 10. Open questions

1. `GSAdmin.Send` per-frame ceiling below 512 — survey precedent says it
   fits; confirm at implementation.
2. Month/day rollover during the session flips `last-month production` —
   10 exchanges are minutes, the A1 session window far larger; no `day`
   echo field is planned. Reopened if a spot divergence ever shows time
   drift.
3. Industry-id pool bound (`<= 65535`) — verify against the 15.3 pool
   limits in the byte-audit test.
4. If the census finds boxes ≠ 1, the adaptation design (which stop
   re-pins or acceptance builders) is its own round — deliberately not
   sketched here.
5. Cursor-grid pages for a second census (a v2) would need their own
   schedule derivation — this record covers identity 1 only.

## 11. What this record does not do

No code written here; no candidate staged, signed, authorized, launched or
claimed; no `artifacts/` write of any kind; `D5-FREIGHT-3` and all prior
evidence byte-unchanged and terminal; no order of execution changes (an
implementation round still needs staging approval → independent review →
Gate C signing → separate explicit launch approval). Evidence index E59.
