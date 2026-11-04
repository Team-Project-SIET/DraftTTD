# CargoFlow delivery round (design record, 2026-11-04)

**Status: witnessed design record.** The E99 probe round
(`D5-CARGOFLOW-1`, `d5-corridor-cargoflow-native-candidate-1`) halted
terminal at `sample-07` with `PHASE_HALTED_PREFIX_PRESERVED` after seven
verified READY samples. This record designs the next round — a real
road-vehicle delivery attempt under the fresh identity `D5-CARGOFLOW-2`
— and corrects the two defects the halt exposed: a funds fence aimed at
a static close-out level while the world legitimately pays monthly
charges, and a funds echo sampled at a different instant than the
observations it shares a response with. It changes no consumed byte,
leaves every terminal verdict exactly as recorded, and never re-uses
`D5-CARGOFLOW-1`. Implementation, suites, staging, review, Gate C
signing and launch each remain their own explicit operator approvals;
nothing in this record executes natively on its own words.

## 1. What E99 measured, and what it did not measure

Measured natively (all on the loaded v3 depot-mutation world,
`183b20273a54ebe1…1efe6a6`, world-pin version 3, start-day clock
712223 = Jan 1, 1950, funds of record 489650, fleet 0):

1. Seven READY samples (`sample-00` … `sample-06`, days 712228–712258,
   offsets 0–30, ladder arithmetic exact: day − anchor == pinned
   offset), each echoing funds **489650** — the static close-out pin —
   and each measuring: `stock_pickup` **−1** (all seven),
   `stock_bay` **0** (all seven), `wait_pickup`/`wait_bay` and every
   `from0`/`from1`/planned variant **0**, `prod_pickup` **104** (Jan)
   then **117** (Feb, from `sample-06` on), `trans_pickup` **0**,
   `prod_bay`/`trans_bay` **−1** (the bay industry does not produce
   coal).
2. `sample-07` (day 712263, offset 35) echoed funds **489458** — a
   drain of exactly **192** — and the Python fence refused it:
   `cargo-flow funds must equal the close-out level exactly`.
3. The retained phase outcome typed the verdict
   `DISPATCH_STOCKPILE_STATIC` (H1) with
   `verification: CARGOFLOW_INCOMPLETE`, status
   `PHASE_HALTED_PREFIX_PRESERVED`, prefix preserved, `sampled_months`
   `[[1950,1],[1950,2]]`.

NOT measured natively, and unproven for this world:

- Anything with a vehicle present: no purchase, no orders, no start —
  the probe issued zero company commands by design.
- The selector-open regime: `HasVehicleEverTriedLoading()` never had a
  vehicle to become true, so the `selectgoods` gate stayed closed for
  the whole span.
- The delivery side end to end: no load, no loaded departure, no
  unload, no accepted-pile growth at the bay industry, no revenue.
- The producer-side stockpile (`i->produced[cargo].waiting`) directly —
  it is not script-observable (§3.1); only its downstream consequences
  are.

### 1.1 Disclosure: the E100 label has no record in this repository

A round labelled `E100` appears in the operator's task prompt but has
no record anywhere in this repository: no entry in `TASKS.md` or
`EVIDENCE_INDEX.md`, no document under `docs/`, and the git log ends at
commit `81ce350 E99`. This record therefore imports nothing from E100:
every mechanic and number below is re-derived from the OpenTTD 15.3
sources at the committed submodule (`ottd/`) and from the retained E99
receipt bytes under
`artifacts/experiments/d5-corridor-cargoflow-native-candidate-1/`. If
an E100 record is later filed, it reconciles against this document; it
does not substitute for it.

## 2. The halt of record was a fence-target defect, not a world behavior

The E99 funds fence compared every sample's funds echo against the
static close-out level 489650 — correct for a probe with no fleet, no
purchase and no running cost (`corridor_cargoflow_native.py:507-510`
says exactly that). But the world is not cost-free: at the first
economy month boundary the engine charges loan interest plus a
station-value fee to every company, fleet or no fleet. The 192 drain is
that charge, exactly:

- `CompaniesPayInterest` (`ottd/src/economy.cpp:809-841`) charges, at
  each economy MONTH boundary, the staircase installment
  `yearly·(m+1)/12 − yearly·m/12` on `yearly = current_loan · rate/100`,
  plus `_price[PR_STATION_VALUE] >> 2` under `EXPENSES_OTHER`.
- World of record: founding loan 100000 (`ottd/src/company_cmd.cpp:619`;
  with inflation disabled `_economy.inflation_prices` is 65536, so the
  scaled loan is exactly INITIAL_LOAN), `difficulty.initial_interest`
  default 2 ⇒ `yearly = 2000`; `_price[PR_STATION_VALUE]` base 100
  (`ottd/src/table/pricebase.h:11`) ⇒ fee 25.
- At the Feb 1 boundary the 0-based month index is 1, so the installment
  is `2000·2/12 − 2000·1/12 = 333 − 166 = 167`, plus 25 ⇒ **192**.
  Funds 489650 − 192 = 489458 — the exact `sample-07` echo.

The fence's comparison target was wrong, not the world. E99's recorded
drain window "(712259, 712263]" was an artifact of a second defect: the
package reads the funds echo **before** its in-package wait
(`d5_cargoflow_package/main.nut:408` — `r.funds =
GSCompany.GetBankBalance(q.company)` precedes `CargoFlowSampleOp`),
while the day/tick and cargo observations are taken **after** the wait.
Each response's funds therefore belongs to the *previous* sample's
observation instant: `sample-06`'s echo (labelled day 712258) was
actually taken at Jan 31+ε, pre-charge; `sample-07`'s echo was taken at
Feb 5+, post-charge. The charge instant is Feb 1 (day 712254) — a
normal monthly event, not a mid-month anomaly. Both defects are fixed
by design in this round (§4, §5.4). The E99 verdict and halt stay
terminal and unlabeled-unchanged; nothing here relabels them.

## 3. Primary-source mechanics of record (OpenTTD 15.3, `ottd/` at the committed submodule)

### 3.1 Four corrections to the E98-era framing

1. **`GSIndustry.GetStockpiledCargo` is not a producer waiting-pile
   API.** It returns `i->GetCargoAccepted(cargo)->waiting`
   (`ottd/src/script/api/script_industry.cpp:83-94`) — the *accepted*
   pile of a consuming industry. The producer pile
   `i->produced[cargo].waiting` is not script-observable. Consequently
   E99's `stock_pickup = −1` on all eight samples is the pinned
   **non-acceptance echo** (the pickup industry produces coal, accepts
   nothing): it is a staleness guard of record, never a queue signal.
   `stock_bay = 0` (not −1) proves the bay industry *does* accept coal.
2. **`last_speed` is the selector key, and a zero-load arrival sets
   it.** `GoodsEntry::HasVehicleEverTriedLoading() { return last_speed
   != 0; }` (`ottd/src/station_base.h:261`); `ge->last_speed =
   ClampTo<uint8_t>(t)` is set in `LoadUnloadVehicle`
   (`ottd/src/economy.cpp:1764`), for road vehicles from
   `cached_max_speed / 2` — the pinned engine's census max_speed 48 ⇒
   24 ≠ 0. The station-side comment is explicit: trying to load with
   nothing available still counts. The first arrival at the pickup stop
   opens the gate.
3. **The `selectgoods` gate, not the rating, was the blocker.**
   `CanMoveGoodsToStation` (`ottd/src/station_cmd.cpp:4578-4600`)
   refuses a station when `_settings_game.order.selectgoods` (default
   true, `ottd/src/table/settings/game_settings.ini:75`) is on and no
   vehicle ever tried loading there. A fresh GoodsEntry starts at
   `INITIAL_STATION_RATING = 175` (`ottd/src/station_base.h:23,235`) —
   the rating-0 refusal was never the operative gate.
4. **The producer pile drains into the void while the selector is
   closed.** `TransportIndustryGoods`
   (`ottd/src/industry_cmd.cpp:521-543`) subtracts `cw` from
   `p.waiting` *before* calling `MoveGoodsToStation`; with the selector
   closed the moved amount is 0, the cargo is gone, and
   `p.history[THIS_MONTH].transported` stays 0 — exactly E99's
   `trans_pickup = 0`. Nothing accumulates at the pickup station, and
   nothing accumulates unboundedly at the industry.

### 3.2 The full flow with a vehicle present

1. **Production** — `ProduceIndustryGoodsHelper` adds `p.rate` to
   `p.waiting` every `INDUSTRY_PRODUCE_TICKS = 256` game ticks
   (`ottd/src/industry_cmd.cpp:1148-1154`,
   `ottd/src/timer/timer_game_tick.h`).
2. **Drain** — `TransportIndustryGoods` (above) moves only when
   `ClampTo<uint8_t>(p.waiting) > indspec->minimal_cargo`
   (`ottd/src/industrytype.h:116`); a recession halves the moved amount.
3. **Selector** — `MoveGoodsToStation`
   (`ottd/src/station_cmd.cpp:4593+`) distributes into
   `i->stations_near` through `CanMoveGoodsToStation`'s gates
   (exclusivity, rating 0, `selectgoods`/`last_speed`, stop class).
4. **Station receiver** — `UpdateStationWaiting`
   (`station_cmd.cpp:4401-4415`) appends the cargo into the station's
   goods entry (fractional accumulator first); `GSStation.GetCargoWaiting`
   counts exactly this — the `wait_pickup` observable.
5. **Loading** — the vehicle's pickup order (flags 0) makes
   `LoadUnloadVehicle` load whatever is waiting; it departs with
   `load ≤ capacity 20`.
6. **Delivery** — the delivery order (flags 128 = `OF_NO_LOAD`,
   `ottd/src/script/api/script_order.hpp`) unloads without loading.
   Unload calls `DeliverGoods`
   (`ottd/src/economy.cpp:1094+`, from `LoadUnloadVehicle` at
   `economy.cpp:1220`), which pays revenue and calls
   `DeliverGoodsToIndustry` (`economy.cpp:1039-1076`): for each
   industry in the bay station's `industries_near` that accepts the
   cargo (excluding the source industry, and skipping any industry
   temporarily refusing cargo), `it->waiting += amount` on the
   **accepted pile** — the `stock_bay` observable — plus
   `history[THIS_MONTH].accepted += amount` and `last_accepted = date`.
7. **Monthly accounting** — the economy MONTH timer
   (`ottd/src/economy.cpp:1979-1984`) runs `CompaniesGenStatistics()`
   then `CompaniesPayInterest()` at the first tick of each new month.

### 3.3 The funds mechanics of record

- **Monthly charges are whole-unit, fraction-free.**
  `CompaniesPayInterest` pays through `SubtractMoneyFromCompany`
  (`ottd/src/company_cmd.cpp:313-317`), which debits
  `SubtractMoneyFromAnyCompany` directly — no fraction accumulator.
  The Feb 1 charge is exactly 167 + 25 = 192.
- **Running costs are fractional.** `RoadVehicle::OnNewEconomyDay`
  (`ottd/src/roadveh_cmd.cpp:1734-1740`) charges, at each economy-day
  boundary, `GetRunningCost() · running_ticks / (DAYS_IN_YEAR ·
  DAY_TICKS)` — an 8.8 fixed-point amount paid through
  `SubtractMoneyFromCompanyFract` (`company_cmd.cpp:324-335`), whose
  fraction carry must be replicated exactly. `running_ticks` accrues
  every tick the front engine is not `VehState::Stopped`
  (`roadveh_cmd.cpp:1662`) — driving **and** loading; a breakdown does
  not set `Stopped` and does not change the charge; only an explicit
  stop (depot entry) does. `DAY_TICKS = 74`
  (`ottd/src/timer/timer_game_tick.h:75`).
- **The census running cost of record** is 421 per economy year
  (`ENGINE_CENSUS_V2`, `corridor_freight_v2.py:144-149`), so
  `GetRunningCost()` = 421·256 = 107776 in 8.8 units; a full day
  (running_ticks 74) charges `107776·74 / (365·74) = 295` in 8.8 units.
- **No other charges**: `economy.inflation` false,
  `economy.infrastructure_maintenance` false (defaults of record), and
  the negative-cash interest branch of `CompaniesPayInterest` cannot
  fire while funds stay near 485k.
- **No service diversion inside the attempt**: `servint_roadveh`
  defaults to 150 days (`ottd/src/table/settings/game_settings.ini:386-390`),
  `NeedsServicing` requires the interval elapsed
  (`ottd/src/vehicle.cpp:201+`), and the 55-day ladder ends long before
  day 150 after purchase.

## 4. The funds model of record (Section B)

The fence target moves from the static close-out level to the **modeled
trajectory**. The exact-funds invariant is preserved, never weakened:
comparison stays exact equality; any unexplained divergence halts the
attempt fail-closed at that sample.

Parameters, all pinned from the world and engine census of record:

| Parameter | Value | Source of record |
| --- | --- | --- |
| start funds | 489650 | depot-mutation close-out pin |
| purchase quote | 4429 | `ENGINE_CENSUS_V2["price"]` |
| loan | 100000 | founding loan, inflation off |
| interest rate | 2 | `difficulty.initial_interest` default |
| station-value fee | 25 | `_price[PR_STATION_VALUE] >> 2`, base 100 |
| running cost | 421/economy-year | `ENGINE_CENSUS_V2` |
| capacity | 20 | `ENGINE_CENSUS_V2` |

Model, evaluated at each sample's single observation instant:

```
funds(sample_k) == 489650
  − 4429                                    (purchase-00, exact quote)
  − Σ monthly charges                        (§3.3 staircase + fee, whole units)
  − Σ running-cost deductions                (§3.3 Fract emulation)
  + Σ measured income deltas                 (quarter-income reads per span)
```

- The monthly term is closed-form integer arithmetic on the pinned
  parameters; the Feb 1 cross-check is 167 + 25 = 192, matching the
  retained E99 echo exactly.
- The running-cost term is an exact integer emulation of the Fract
  accumulator: per economy day with the vehicle started and not
  Stopped, `running_ticks = 74`; the charge lands at that day's
  boundary for the previous day's ticks. The start day is partial: its
  tick count follows from the (day, tick) phase of record, which the
  receipts' own day-ladder pairs pin. E97 precedent for the mechanism:
  funds 485221 → 485214 across a watch window.
- The income term is **measured, not modeled**: each flow sample
  carries the freight-family finance reads
  (`GSCompany.GetQuarterlyIncome` / `GetQuarterlyCargoDelivered`,
  `d5_freight_v2_package/main.nut:1031-1032` pattern), and the model
  attributes per-span income deltas with quarter-reset handling. The
  whole ladder sits inside Q1 1950, so no reset fires mid-ladder.
- **Sampling-instant alignment (the §2 fix)**: the new package reads
  funds **after** the in-package wait, at the same instant as the
  day/tick and cargo observations. One response, one instant; the
  funds echo and its labelled day can never disagree again.

## 5. The design (fresh identity `D5-CARGOFLOW-2`)

### 5.1 Identity and frozen bytes

- Fresh attempt identity `D5-CARGOFLOW-2`; new wire protocol id 11,
  name `cargoflow-delivery`; new wire module
  `app/simulation/openttd/corridor_cargoflow2.py`; new staged package
  `app/simulation/openttd/d5_cargoflow2_package/`; new native pipeline
  `app/simulation/openttd/proof/corridor_cargoflow2_native.py`, mirrored
  from the E99 runner discipline (isolated runtime, staging seal,
  read-only preflight/verify, claim boundaries, certified cleanup,
  manifest, replay verify).
- Protocols 8/9/10 bytes stay frozen: `corridor_cargoflow.py` and the
  E99 package are historical instruments of record, amended by nobody.
- The prerequisite chain is re-derived, never written: the same
  consumed depot after-save pin `183b20273a54ebe1…1efe6a6` at
  `d5-corridor-depot-mutation-native-candidate-3` plus the verified
  reload chain; binary pin `276d5b69…904c`, OpenGFX `43a0c1da…03be`.
- The freight family (`D5-FREIGHT-1..6`), the depot-mutation family,
  and `D5-CARGOFLOW-1` stay terminal and untouched.

### 5.2 Section A — the vehicle comes first

The round's decisive change versus E99: a real road vehicle with
pickup/delivery orders exists and has **already arrived** at the pickup
stop before the observation ladder begins. The pre-arrival control of
record is E99's retained seven-sample prefix (no vehicle, every wait
reading 0): it establishes that without a vehicle the pickup station
never receives cargo.

1. `site-00`, `engine-00`, `purchase-00`, `vread-00`, `order-00`
   (goto pickup stop, flags 0), `order-01` (goto delivery stop, flags
   128), `order-read-00`, `monitor-00`, `start-00`, `vread-01` — the
   freight-family instrument chain of record, ported verbatim in
   meaning: the engine pin 123 admitted fail-closed at its census
   (cargo 1, capacity 20, price 4429, running 421/yr, max_speed 48),
   the purchase realizes exactly the tested quote, both orders set and
   independently read back, the vehicle starts and reads RUNNING.
2. `arrive-00` — a **bounded first-arrival watch** (new op kind
   `arrive-watch`): the package polls per tick (port of the freight
   watch loops, `d5_freight_v2_package/main.nut:1168/1179,
   1326/1349`) until `GSVehicle.GetLocation` equals the pinned pickup
   stop tile 45748, then latches the arrival (day, tick) and the load
   state (0 expected — the selector was closed). Bound: 5 economy
   days; a timeout is a terminal `ARRIVE_TIMEOUT`, never a retry.
3. From the arrival instant, `last_speed ≠ 0` holds engine-side for
   the pickup station's coal GoodsEntry; the `selectgoods` gate is
   open for every later drain. The gate state itself is not
   GS-observable — its consequence is: **`wait_pickup > 0` at any
   later sample is the decisive queue observation**, proving jointly
   that a qualifying drain ran and that the first arrival had opened
   the selector. The latch timestamps give the strict ordering of
   record: arrival day < first `wait_pickup > 0` day.
4. `stock_pickup` stays a pinned **−1 echo** on every sample: any
   other value is a native-fact mismatch and refuses the exchange
   fail-closed. It is never read as a queue signal.
5. `stock_bay` (the bay industry's accepted pile,
   `GSIndustry.GetStockpiledCargo(1, COAL)`) is the **delivery-leg
   observable**: it rises from 0 only after a loaded arrival is
   unloaded at the bay stop (§3.2 step 6).

### 5.3 The schedule of record

Fixed ops 11 + flow ladder 12 + tail 2 = **25 requests**, inside the
32-request budget of record (`FREIGHT_REQUEST_BUDGET_V2`,
`corridor_freight_v2.py:168`):

- **Fixed 11**: `site-00`, `engine-00`, `purchase-00`, `vread-00`,
  `order-00`, `order-01`, `order-read-00`, `monitor-00`, `start-00`,
  `vread-01`, `arrive-00`.
- **Flow ladder 12**: `flow-00` … `flow-11`, offsets 0..55 step 5
  (55-day span) relative to the anchor latched at `arrive-00`'s
  completion; the day-ladder arithmetic of record carries over
  (day − anchor == pinned offset, overshoot = WINDOW_EXHAUSTED).
- **Tail 2**: `finance-00`, `finish-00` (the freight-family tail
  vocabulary): the finance corroboration read and the certified
  close-out.
- **Authority**: the freight family's 60-day per-attempt day authority
  is preserved; the arrival bound (≤ 5 days) plus the 55-day ladder
  fits exactly, and the receipts must show `sampled_months` ≥ 2
  distinct months. If the anchor lands too late for that, the attempt
  halts fail-closed — the span is never stretched ad hoc.
- **Cycle events are latched during the in-package waits** — no
  separate cycle-monitor exchanges. While a flow sample waits toward
  its offset day, the per-tick poll latches every arrival at either
  stop, every load/departure with its load count, and every unload
  with its delivered amount, each with (day, tick). The ladder
  therefore carries the full cycle evidence inside the 12 samples.

### 5.4 Section B in the instrument

Each flow sample's observation set: the E99 sample set (stockpiles,
waiting and planned families at both stops, monthly
production/transported, date, tick) **plus** the funds echo at the
post-wait instant (§4), the quarter-income/delivered reads, the
vehicle state echo (location, load, in_depot, speed), and the cycle
latches accumulated during the wait. Response schema
`cargo-flow2-sample-receipt-v1`; every exchange fail-closed
(`D5_NATIVE_FACT` on any throw, E99 discipline).

### 5.5 Outcome typing

Terminal classifications typed at the attempt layer, none of which
re-opens any other family:

- `CARGOFLOW2_DELIVERY_VERIFIED` — all six acceptance criteria (§7)
  hold on the retained receipts.
- `CARGOFLOW2_QUEUE_NEVER_FILLED` — arrival witnessed, `wait_pickup`
  stayed 0 through the ladder: the drain side is implicated with the
  selector proven open, a stronger H1-class record than E99's.
- `CARGOFLOW2_LOADED_NEVER_DELIVERED` — a load latched, no bay-side
  consumption observed.
- `CARGOFLOW2_FUNDS_DIVERGED` — the modeled-trajectory fence fired
  (fail-closed by construction).
- `CARGOFLOW2_GATE_UNDECIDED_INCOMPLETE` — an unobserved or unfinished
  ladder decides this, as in E99.

## 6. Event sequence of record

The expected native ordering, each step independently evidenced:

1. Launch on the reload chain; `site-00` re-pins the corridor identity
   (depot 45487, pickup stop sid 0 @ 45748, bay stop sid 2 @ 50862,
   industries 0 @ 44983 / 1 @ 51116, cargo 1 COAL, funds 489650).
2. `engine-00` admits the pinned engine at census; `purchase-00`
   realizes exactly −4429 (funds 485221); `vread-00` reads the vehicle
   in the depot.
3. `order-00`/`order-01` append the two orders; `order-read-00`
   verifies both (flags 0 / 128); `monitor-00` arms the cargo
   monitors; `start-00` starts the vehicle; `vread-01` reads it
   RUNNING out of the depot.
4. `arrive-00` latches the first arrival at the pickup stop
   (day/tick of record; load 0) and latches the ladder anchor.
5. The ladder runs: the first post-arrival qualifying drain moves coal
   into the pickup station (`wait_pickup > 0`, `trans_pickup` history
   begins); a later pickup arrival loads `load > 0` and departs loaded;
   the bay arrival unloads (`stock_bay > 0`, delivered counter,
   revenue); the cycle repeats under the two-order loop.
6. At the Feb 1 boundary the funds model predicts −192 (167 interest
   + 25 station value); every sample's funds echo equals the modeled
   trajectory exactly.
7. `finance-00` corroborates the quarter income/delivered totals;
   `finish-00` certifies cleanup; replay re-derives the verdict from
   the receipts alone.

## 7. Acceptance criteria (Section C)

All six are measurable from the retained receipts alone:

1. **Queue positive**: `wait_pickup > 0` at ≥ 1 flow sample whose
   labelled day is after the `arrive-00` arrival latch, with
   `stock_pickup` still exactly −1 on every sample.
2. **Loads and departs**: a latched load event at the pickup stop with
   `load > 0` and a subsequent departure latch (or state echo) showing
   the vehicle left loaded.
3. **Delivery received and consumed**: `stock_bay > 0` at ≥ 1 flow
   sample after a loaded bay arrival, corroborated by the delivered
   counter / `last_accepted`-class finance reads.
4. **Industry transported history increases**: the pickup industry's
   transported history of record rises above its anchor 0
   (`trans_pickup > 0` at a sample after the first delivered drain,
   or its month-boundary successor).
5. **Financial reconciliation matches engine accounting**: every
   sample's funds echo equals the §4 modeled trajectory exactly
   (purchase, monthly staircase + fee, Fract running costs, measured
   income); any unexplained divergence is a halt, never a tolerance.
6. **Replay independently verifies ≥ 1 complete delivery cycle**: the
   offline replay of the receipts reconstructs one full
   pickup→delivery cycle (arrival, load > 0, departure, bay arrival,
   unload, consumption) from the latched events without importing the
   native session's own verdict.

## 8. Risks and mitigations

1. **Arrival latency vs the 60-day authority** — `arrive-00` is
   bounded at 5 economy days; a timeout is terminal
   (`ARRIVE_TIMEOUT`), never a retry, and the ladder never starts
   without its anchor.
2. **Month-boundary count depends on the anchor** — `sampled_months
   ≥ 2` is a receipt property of record; an anchor too late for it
   halts fail-closed instead of stretching the span.
3. **Bay-side temporary refusal** — `IndustryTemporarilyRefusesCargo`
   (`ottd/src/economy.cpp:1055` area) can delay accepted-pile growth;
   criterion 3 needs only one qualifying sample, refusals are recorded
   as observations, never invented around.
4. **Bay catchment** — the accepted pile grows only for industries in
   the bay station's `industries_near`; the world of record was built
   with the bay stop serving industry 1, and `stock_bay` reading 0
   (not −1) at every E99 sample already proves acceptance; the
   behavioral proof of catchment is criterion 3 itself.
5. **Funds-model exactness** — every parameter is pinned
   (§4 table); the emulation replicates the Fract carry exactly; the
   fence stays exact and fail-closed. The model never weakens the
   invariant to pass.
6. **Service diversion** — `servint_roadveh` default 150 days cannot
   fire inside a ≤ 60-day attempt; if one ever occurs it is latched
   and terminal-classified, never absorbed silently.
7. **Offline stub fidelity** — the E98 §4 disclosure class applies:
   a cargoflow2 wire stub that cannot represent the selector gate or
   the accepted-pile mechanics must disclose the gap in its own
   record; any stub amendment belongs to the implementation approval,
   not this document.
8. **Identity discipline** — `D5-CARGOFLOW-2` is fresh; no terminal
   identity is re-used; the prerequisite bytes are re-derived and
   never written; historical evidence stays immutable.

## 9. Constraints compliance

This record authorizes no native run, connects to no AdminPort, and
sets no `--run-openttd`/`--run-postgres` flag. It modifies no retained
`artifacts/` byte, relabels no terminal verdict, substitutes no
synthetic fixture, and touches no `TASKS.md` / `EVIDENCE_INDEX.md` /
`AI_HANDOFF.md` entry. The `CONTEXT.md` prepend-only header stays
intact; the root `--version` file stays unexecuted; work remains on
branch `devmodule2`.

## 10. Open operator decisions at review time

1. Approve the fresh identity `D5-CARGOFLOW-2` and the Protocol 11
   (`cargoflow-delivery`) scope, with Protocols 8/9/10 frozen.
2. Approve the schedule arithmetic (§5.3): 25 requests, the 12-sample
   55-day ladder, the 5-day arrival bound, the 60-day authority.
3. Approve the funds model of record (§4) as the fence target,
   replacing the static close-out pin, with the exact-funds invariant
   preserved.
4. Approve the six acceptance criteria (§7) as the round's gate, and
   the outcome typing (§5.5) as terminal classifications.
5. Approve the E100 disclosure (§1.1) as recorded: this round's
   evidence base is the committed 15.3 sources and the retained E99
   receipts, nothing else.
