# Cargo dispatch probe (design record, 2026-11-04)

**Status: witnessed design record.** Round of record: Path A R4c launched
`D5-FREIGHT-6` (`d5-corridor-freight-native-candidate-6`) once and halted
terminal at `transit-00` with `WINDOW_EXHAUSTED` (E97), AFTER the order
readback fix measured native: `order-00`/`order-01` ORDERED and
`order-read-00` `NATIVE_ORDER_SET_VERIFIED` — the family's first native
order-set verification, the E92 `READBACK_MISMATCH` never recurring
(E93/E96). This record designs the next investigation round — a
read-only observation probe of the industry→station cargo dispatch —
under the fresh identity `D5-CARGOFLOW-1`. It changes no consumed
byte and leaves the freight family terminal as recorded. Implementation,
suites, staging, review, Gate C signing and launch each remain their own
explicit operator approvals; nothing in this record executes natively
on its own words.

## 1. What E97 measured, and what it did not measure

Measured natively (all on the loaded v3 depot-mutation world,
`183b20273a54ebe1…1efe6a6`, world-pin version 3):

1. The full instrument chain of record is green: site, engine, purchase,
   vehicle readback, both order appends, and the order-set inventory —
   the E92/E93 fix of record verified verbatim.
2. `vread-01` read the vehicle RUNNING (`speed 2`, `in_depot false`) in
   `frames.json` after `start-00` — the vehicle genuinely departed the
   depot (45487).
3. `load-00` (day 712234, tick 485, window 10 days / 2048 ticks): the
   vehicle passed the sampled pickup stop empty — `load 0`,
   `pickup_amount 0` — the typed F-11 event `ZERO_DEPARTED`
   (`NATIVE_ZERO_DEPARTED`), never a success, never folded into a
   window status (`corridor_freight_v2.py:1718-1751` of record).
4. `transit-00` (day 712244, tick 1158, second full window):
   `WINDOW_EXHAUSTED`, funds 485221 → 485214 (running costs accrued),
   0 completed cycles, `zero_departed_cycles 0`,
   `INCONCLUSIVE_WINDOW` / `zero_seen false` — conservative class,
   preserved, never relabeled.

NOT measured natively, and unproven for this world:

- Anything about the station-side cargo storages between the two
  watches: total station waiting sampled at most twice (0 at `site-00`
  before any production cycle ran, 0 at `load-00` 11 days later);
- the industry's own stockpile buffer (`i->produced[cargo].waiting`)
  over time — unobservable in the freight instrument of record;
- any month boundary (the save's start-day clock 712223; both watches
  ended within the first sim month);
- the current-month production rate of the pickup industry — only
  `GetLastMonthProduction` is measurable (104 at `site-00`, a figure of
  the month BEFORE the save).

## 2. The observation of record

The started vehicle took no cargo across two full typed watch windows
(≈ 2 × 10 days / 2048 ticks after the 712223 start-day clock), while the
instrument chain and the departure itself were green. The zero flow at
the pickup stop is consistent with every one of the 15.3 dispatch gates
below being closed for at least one reason; the family instrument never
ported the ability to distinguish them. The round's instrument defect
class from E92 (E72-class: stub faithfully shared the wrong model) does
NOT apply here — this halt is a world-behavior observation, recorded as
such — but the OFFLINE fixture shares a related fidelity gap (§4) which
must be marked before any next instrument is trusted.

## 3. Primary-source mechanics of record (OpenTTD 15.3, `ottd/` at the committed submodule)

The 15.3 flow from "industry produces" to "cargo waits at a station",
each step a gate a probe must observe:

1. **Production into the industry's own stockpile** —
   `ProduceIndustryGoodsHelper` adds `p.rate` to the industry's own
   `p.waiting` every `INDUSTRY_PRODUCE_TICKS = 256` game ticks
   (`ottd/src/industry_cmd.cpp:1148-1154`,
   `ottd/src/timer/timer_game_tick.h:82`). The stockpile is
   industry-side, capped `uint16_t`; nothing reaches a station here.
2. **The tile-loop mover** — `TileLoop_Industry` calls
   `TransportIndustryGoods(tile)` (`industry_cmd.cpp:852`), which for
   each produced cargo reads `cw = ClampTo<uint8_t>(p.waiting)` and
   moves ONLY if `cw > indspec->minimal_cargo` (`industrytype.h:116`);
   inside the gate it drains `p.waiting` and calls
   `MoveGoodsToStation(p.cargo, cw, {industry}, i->stations_near,
   i->exclusive_consumer)` (`industry_cmd.cpp:523-543`).
   A tiny stockpile below `minimal_cargo` NEVER moves; the tick caps a
   single tile-loop move at 255 pieces.
3. **The station selector** — `MoveGoodsToStation`
   (`ottd/src/station_cmd.cpp:4593-4690`) distributes into
   `all_stations` (= `i->stations_near`) split by per-company best
   rating × per-station rating; `CanMoveGoodsToStation`
   (`station_cmd.cpp:4578-4600`) REFUSES a station when
   `goods[cargo].rating == 0`, when `selectgoods` is on and no vehicle
   ever tried loading there, and applies the passenger/truck-stop class
   rule (freight is unaffected by the class rule).
   `i->stations_near` is the industry's catchment set of record.
4. **The station receiver** — `UpdateStationWaiting`
   (`station_cmd.cpp:4401-4415`) appends `CargoPacket`s into
   `st->goods[cargo]` (fractional accumulator first — amounts < 256
   still flow via `amount_fract`), creates the link graph node and sets
   the Rating state. `GSStation.GetCargoWaiting` counts exactly this.
5. **The monthly rating machine** — `UpdateStationRating`
   (`station_cmd.cpp:3973-4085`) recomputes ratings monthly from
   waiting/speed/pickup-time; a GoodsEntry starts at
   `INITIAL_STATION_RATING = 175` (`station_base.h:23,235`), so a fresh
   station is NOT refused by the rating-0 gate at birth.
6. **Delivered-goods side** (context only — nothing delivered to the
   pickup industry this run): `DeliverGoods`/`TriggerIndustryProduction`
   (`ottd/src/economy.cpp:1083-1178`).

### 3.1 The gate framings this probe must distinguish

Every H below is a path the above source admits for "two empty
watch windows, `last_month` production 104":

- **H1 rate collapse**: the current-month `p.rate` of the pickup
  industry is so small (dying-industry production curve) that stockpile
  cycles stay at or below `minimal_cargo` for the observed span —
  cargo never crosses gate 2.
- **H2 stockpile grows but selector refuses**: `stations_near` does not
  contain the pickup station (or `goods.rating == 0` persisted /
  exclusivity) — stockpile rises, station waiting stays 0 — gate 3
  closed.
- **H3 flow exists but was late or partial**: waiting rose within the
  second watch or later — gate 2/3 open, cadence/duration policy of
  record simply too short.
- **H4 routed elsewhere**: cargo reached a DIFFERENT station inside
  `stations_near` (if any other station exists in the industry
  catchment).

### 3.2 What the GameScript API of record can observe

15.3 GS API (read-only, no company actions):

- `GSIndustry.GetStockpiledCargo(industry, cargo)`
  (`ottd/src/script/api/script_industry.cpp:83`) — the H1/H2
  discriminator (does the industry-side buffer grow?).
- `GSStation.GetCargoWaiting(sid, cargo)` and the `.from/.via/.from_via`
  variants (`ottd/src/script/api/script_station.cpp:74-97`) — waiting
  time series, with per-source industry breakdown; `CountCargoWaiting`
  and the `GetCargoPlannedFrom` family give the planned side.
- `GSIndustry.GetLastMonthProduction/GetLastMonthTransported`
  (`script_industry.cpp:96-127`) — sampled at each month boundary, the
  production machine's own verdict of record.
- `GSStation.GetStationNum`-adjacent ids and
  `GSIndustry.GetLocation` — already used by the site gate of record.
- NOT observable from GS: `st->goods[cargo].rating`,
  `stations_near` membership, `minimal_cargo`, `p.rate` directly —
  the probe's verdict works with the observable subset; unobservables
  stay what the source study says they are.

## 4. The offline stub-fidelity gap of record (disclosed, not fixed in-session)

The freight wire stub models the station's cargo store as a constant:
`::waiting = 5` (`tests/test_corridor_freight_v2.py:113`) with
`GSStation.GetCargoWaiting(_, _) { return ::waiting; }`
(`:262`), and the freight stub `GSIndustry` carries no
`GetStockpiledCargo`. Every dispatch gate in §3 is invisible offline:
an e2e zero-flow outcome is unreachable by construction, so the suite of
record was green while the native world halts on exactly this dimension.
This is disclosed here as the known offline fidelity limit; any stub
amendment belongs to the probe round's own implementation approval, not
this record.

## 5. The probe design (fresh identity `D5-CARGOFLOW-1`)

A read-only observation run, staged from the same consumed
prerequisite chain (depot after-save pin `183b2027…6a6` at
`d5-corridor-depot-mutation-native-candidate-3` + the verified reload
chain), observing the saved world WITHOUT any company action: no
engine purchase, no orders, no vehicle start. The whole freight
attempt-6 family stays terminal and untouched.

- **Instrument**: a small observation-only package
  (`d5_cargoflow_package/`, GameScript, staged like the census package
  `d5_census_package/` and the freight package) over the same
  encrypted-AdminPort GS protocol of record; the runner is a native
  CLI module (`corridor_cargoflow_native.py`) mirrored from the
  census/freight runner discipline (isolated runtime, staging seal,
  read-only `preflight`/`verify`, claim boundaries, certified cleanup,
  manifest, replay `verify`). Exact names/sizes are set at design
  review and implementation, not invented here.
- **Exchange family of record** (probe cycles, ids `FREIGHT`-free):
  a fixed sample cadence over a span that guarantees ≥ 2 month
  boundaries of the save's economy clock (span ≥ 40 sim days,
  sample every ~5 sim days ⇒ ≥ 9 samples), each sample measuring:
  `GetStockpiledCargo(industry 0/1, FREIGHT_CARGO)`,
  `GetCargoWaiting(pickup sid 0)` + `GetCargoWaitingFrom(... industry)`
  + `GetCargoWaiting(delivery sid 2)` (per-source if the API form
  allows), `CountCargoWaiting`/planned siblings,
  `GetLastMonthProduction/Transported` for both industries, the
  current date (month/day), and `GC` funds echo. Nothing else; every
  exchange fail-closed (`D5_NATIVE_FACT` on any throw, same
  discipline as the freight package).
- **Company context unchanged**: the probe issues zero company
  commands (no GSCompanyMode orders in its plan), so its budgets
  carry zero purchases and 1 launch — the budgets schema of the
  probe records this explicitly.
- **Outcome typing**: the probe reports a time-series record, not a
  success/failure verdict: if waiting at the pickup rises across the
  span (H3), the record verdict is `DISPATCH_OBSERVED_LATE`; if
  stockpile rises while station waiting stays 0 (H2/H4), verdict
  `DISPATCH_REFUSED_AT_SELECTOR`; if neither rises and last-month
  production decays (H1 after a boundary), verdict
  `DISPATCH_STOCKPILE_STATIC`. All verdicts are terminal observations
  typed at the attempt layer, none of which is a freight retry; the
  freight family's departure proof only re-opens after this probe's
  verdict is recorded and a design decision follows it.

## 6. Risks and mitigations

1. **Probe staleness**: the save ages while the probe observes — by
   design; the probe's own world facts (stockpile/waiting/production)
   are re-measured per sample, and its receipts pin the sampled dates
   so nothing masks drift.
2. **API shape risk**: `GetStockpiledCargo` and the `From` variants
   have 15.3 preconditions (valid ids, cargo); the sample ops use the
   same guarded-call discipline as the site gate (`throws →
   D5_NATIVE_FACT` fail-closed), so a native fact mismatch halts the
   probe terminally instead of recording invented zeros.
3. **No world mutation by construction**: the probe performs no
   company command (no GSCompanyMode orders in its plan); its
   staging/GameScript correspondence review asserts the absence of
   company-mode ops, mirroring the census precedent of record.
4. **Identity discipline**: `D5-CARGOFLOW-1` is fresh; the freight
   identities `D5-FREIGHT-5` (spent) and `D5-FREIGHT-6` (terminal,
   never re-used) stay exactly as recorded; the probe re-derives the
   depot prerequisite bytes but never writes them.
5. **Offline suites**: the probe module gets its own wire + native
   suites mirroring the census layout (34/8/35-class), run green on
   its own implementation round; the freight suites stay untouched
   except the stub-fidelity comment if and only if the implementation
   approval covers it.

## 7. Open operator decisions at review time

1. Approve the probe identity and its read-only observation scope
   (no company actions, no freight relaunch; attempt-6 terminal).
2. Approve the sample cadence and span (§5) as the observation policy
   of record, or amend them.
3. Approve the verdict typing set (§5) as terminal classifications,
   in particular that NO probe verdict re-opens a freight attempt by
   itself.
4. Approve the stub-fidelity disclosure (§4) as recorded without any
   same-session stub amendment.
