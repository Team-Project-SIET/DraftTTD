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

**Amended 2026-11-04 after operator review** (design-only; no bytes
outside this document touched): §5.3 now pins the tail offsets,
worst-case elapsed days, the dual 60-day-authority enforcement and the
polling-versus-exchange budget split; new §3.4 separates the five
cargo stages with independent observables and §7 re-types the
consumption proof accordingly; §4 states the complete financial model
— purchase, monthly interest staircase, station fee, running costs
with exact fractional carry, the empty other-expenses set, and
measured delivery income — under an exact zero-residual fence.

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
- **The running-cost raw value is pinned natively, not derived.**
  `RoadVehicle::GetRunningCost()` is a price-table product
  (`GetPrice(PR_RUNNING_ROADVEH, cost_factor)`,
  `ottd/src/roadveh_cmd.cpp:1644-1652`) whose inputs — the runtime
  `_price`, the difficulty `vehicle_costs` multiplier, the engine
  property — are not jointly pinnable offline; the census figure 421
  is the per-economy-year **display** figure
  (`GetDisplayRunningCost() = GetRunningCost() >> 8`,
  `ottd/src/vehicle_base.h:566`). The new round's `engine-00` op
  therefore reads `GSEngine.GetRunningCost(123)`
  (`ottd/src/script/api/script_engine.cpp:139-143`) and pins the raw
  value as the parameter of record, admitted fail-closed: a raw of 0,
  or one inconsistent with the display figure and the E97 window
  delta (funds 485221 → 485214 over a running window — a raw-421
  misreading would charge ≈ 0 per day), refuses the admission.
- **Correction of record (2026-11-05, E111/T-009).** The bullet above
  documents the inverted premise this design carried: `GSEngine.GetRunningCost`
  on the pinned binary returns the **display** figure directly (the 256-scaled
  raw exists only at the vehicle core surface and is never script-exposed), so
  the engine-00 census pins the display value 421 by direct comparison — no
  second shift — and the funds model reconstructs the 8.8 day charges from the
  pinned display figure (display/365, identical billing arithmetic, exact
  fraction carry). "a raw-421 misreading would charge ≈ 0 per day" stays true
  at the CORE surface the bullet cites; the window bound (funds 485221 →
  485214, Δ7) corroborates unchanged. Consumed candidates 1–2 record the
  defect's outcome; the corrective fix is this round's FD-A-1/T-009 work.
- **No other charges**: `economy.inflation` false,
  `economy.infrastructure_maintenance` false (defaults of record), and
  the negative-cash interest branch of `CompaniesPayInterest` cannot
  fire while funds stay near 485k.
- **No service diversion inside the attempt**: `servint_roadveh`
  defaults to 150 days (`ottd/src/table/settings/game_settings.ini:386-390`),
  `NeedsServicing` requires the interval elapsed
  (`ottd/src/vehicle.cpp:201+`), and the 55-day ladder ends long before
  day 150 after purchase.
- **Command costs are whole-unit and fraction-free.** Command results
  pay through `SubtractMoneyFromCompany`
  (`ottd/src/command.cpp:193,384`) — the purchase debit of exactly
  4429 never touches `money_fraction`.
- **The Fract-path charge set is enumerable.** The only
  `SubtractMoneyFromCompanyFract` call sites in the engine are the
  four vehicle running-cost handlers (`ottd/src/aircraft_cmd.cpp:473`,
  `ottd/src/roadveh_cmd.cpp:1741`, `ottd/src/ship_cmd.cpp:280`,
  `ottd/src/train_cmd.cpp:4209`); this attempt owns exactly one road
  vehicle, so the shared fraction state evolves solely under the
  daily road-vehicle charge.
- **The founding loan of record** is `INITIAL_LOAN = 100000`
  (`ottd/src/economy_type.h:213`); with inflation disabled
  `_economy.inflation_prices` stays 65536 (`economy.cpp:936`), so the
  scaled founding loan is exactly 100000.

### 3.4 The five cargo stages and their independent observables

The delivery proof splits into five stages. Each stage has its own
observable family; no single number proves two stages, and a stage
without its evidence is unproven, never assumed:

| Stage | Engine site | Independent observable of record |
| --- | --- | --- |
| S1 producer transport (industry → station) | `TransportIndustryGoods` books `p.history[THIS_MONTH].transported += am` (`industry_cmd.cpp:523-543`) | `trans_pickup > 0` at a post-boundary sample (`GSIndustry.GetLastMonthTransported`) — the engine's own monthly accounting |
| S2 pickup queue (station storage) | `UpdateStationWaiting` appends into the goods entry (`station_cmd.cpp:4401-4415`) | `wait_pickup > 0` **and** `wait_pickup_from0 > 0` — the source-attributed form pins the cargo to industry 0 |
| S3 vehicle loading | `LoadUnloadVehicle` at the pickup stop (also sets `last_speed`, `economy.cpp:1764`) | latched load event: `GSVehicle.GetCargoLoad > 0` at the pinned stop tile, plus a departure latch (location leaves the stop) with the load still > 0 |
| S4 unloading at the bay | the unload path calls `DeliverGoods` (`economy.cpp:1220`) | latched load→0 transition at the bay stop tile, a positive income delta in that span, and the finance readback's delivered/last-accepted fields increased |
| S5 industry consumption | `DeliverGoodsToIndustry` books `it->waiting += amount` on the accepted pile (`economy.cpp:1069`) | `stock_bay` measured rise (delivery received) **followed by** a later measured net decrease (the industry processing the pile) |

S1 is engine accounting, S2 station storage, S3/S4 vehicle state, S5
industry storage: four independent measurement surfaces. A `stock_bay`
rise without a later decrease proves delivery received but leaves
consumption unproven — typed honestly (§7), never folded into a
success.

## 4. The financial model of record (Section B)

The fence target moves from the static close-out level to the
**modeled trajectory**. The exact-funds invariant is preserved, never
weakened: the reconciliation is zero-residual with no tolerance, and
any unexplained divergence halts the attempt fail-closed at that
exchange.

### 4.1 Parameters, all pinned

| Parameter | Value | Source of record |
| --- | --- | --- |
| start funds | 489650 | depot-mutation close-out pin |
| purchase quote | 4429 | `ENGINE_CENSUS_V2["price"]` |
| founding loan | 100000 | `INITIAL_LOAN` (`economy_type.h:213`), inflation off |
| interest rate | 2 | `difficulty.initial_interest` default |
| station-value fee | 25 per month | `_price[PR_STATION_VALUE] >> 2`, pinned by the E99 cross-check (192 − 167) |
| running cost raw | pinned natively at `engine-00` | `GSEngine.GetRunningCost(123)` (`script_engine.cpp:139-143`) |
| capacity | 20 | `ENGINE_CENSUS_V2` |

### 4.2 The complete charge set

1. **Purchase** — −4429 exactly at `purchase-00`. Command results pay
   through `SubtractMoneyFromCompany` (`command.cpp:193,384`): whole
   units, fraction state untouched. The freight family verified
   natively that funds move by exactly the recorded quote.
2. **Monthly loan interest** — at each economy MONTH boundary, the
   staircase installment `yearly·(m+1)/12 − yearly·m/12` on
   `yearly = current_loan · rate / 100` (integer division), where `m`
   is the new 0-based month index. `current_loan` stays 100000 for the
   whole attempt (no loan commands in the schedule). Feb 1 (m=1):
   333 − 166 = **167**; Mar 1 (m=2): 500 − 333 = **167**. Whole units,
   fraction-free.
3. **Station-value fee** — `_price[PR_STATION_VALUE] >> 2` = **25** at
   every month boundary under `EXPENSES_OTHER`. The runtime price is
   constant: with inflation disabled `RecomputePrices` never re-runs
   (`economy.cpp:1972` sits inside the inflation branch), so the fee
   is 25 at every boundary of the attempt. Pinned by the E99
   cross-check: 192 − 167 = 25.
4. **Vehicle running costs** — at each economy-day boundary, for the
   previous day's `running_ticks`: the 8.8 fixed-point amount
   `C256 = raw · rt / (365 · 74)` (integer division), paid through
   `SubtractMoneyFromCompanyFract`. `rt = 74` for every economy day
   the vehicle is started and not `Stopped` — driving and loading both
   accrue (`roadveh_cmd.cpp:1662`), and breakdowns do not set
   `Stopped`, so they move no money. The start day is partial: its
   tick count is derived from the latched (day, tick) phase of record,
   which the receipts' own day-ladder pairs pin. The vehicle never
   enters a depot after `start-00` (the two-order loop has no depot
   order), so no `Stopped` time exists.
5. **Other expenses — none of record.** Inflation off (no
   `RecomputePrices`), infrastructure maintenance off, no property
   charges, no other vehicle classes. The charge set of record is
   exactly {purchase, loan interest, station fee, road-vehicle running
   cost}; any observed funds movement outside this set plus measured
   income is divergence → halt.
6. **Delivery income — measured, not modeled.** Every exchange from
   `site-00` onward carries `GSCompany.GetQuarterlyIncome(company,
   CURRENT_QUARTER)` at the same observation instant (the
   `d5_freight_v2_package/main.nut:1031-1032` pattern), and the model
   attributes per-span income deltas with quarter-reset handling (the
   whole attempt sits inside Q1 1950, so no reset fires). Event
   corroboration: every span containing a latched load>0 unload must
   show a positive income delta, and no income delta may appear
   without a latched unload. The per-delivery revenue formula
   (`GetTransportedGoodsIncome`, `economy.cpp`) stays corroboration
   depth, not the fence: income is read from the engine's own
   accounting at the same instants, so it attributes movement instead
   of absorbing it.

### 4.3 The exact fractional carry

`money_fraction` is a uint8 accumulator, 0 at founding. The complete
`SubtractMoneyFromCompanyFract` site set is the four vehicle
running-cost handlers (§3.3); this attempt owns one road vehicle, so
the fraction evolves solely under the daily road-vehicle charge. Per
charge, with fraction state `f` and 8.8 amount `C256`
(`company_cmd.cpp:324-335`):

```
low   = C256 & 0xFF
new_f = (f - low) mod 256
whole = (C256 >> 8) + (1 if new_f > f else 0)
funds -= whole ;  f = new_f
```

Purchase, interest and fee never touch `f`. A wrong `f` drifts the
whole-unit deductions within days, so the fence catches it immediately.

### 4.4 The zero-residual fence

At every exchange from `site-00` onward (fixed ops, flow samples,
tail), with the charge terms empty before `purchase-00`:

```
residual(e) = observed_funds(e)
  − (489650 − 4429 − Σ_monthly(e) − Σ_running(e) + Σ_income(e))
requirement: residual(e) == 0 exactly, at every exchange
```

- The income term is engine-read at the same instant as the funds
  echo (§4.2 item 6), so every pound of movement is attributed to
  either a modeled charge or an engine-read income delta — nothing
  can hide in an unmodeled category.
- The Feb 1 cross-check of record: modeled charge 167 + 25 = 192,
  funds 489650 → 489458 — the retained E99 echo, exact.
- The E97 running-cost precedent: funds 485221 → 485214 across a
  watch window — the daily Fract emulation reproduces this class.
- `residual ≠ 0` at any exchange halts the attempt
  `CARGOFLOW2_FUNDS_DIVERGED`. The model is never loosened to pass.

### 4.5 Sampling-instant alignment (the §2 fix)

The new package reads funds **after** the in-package wait, at the same
instant as the day/tick, cargo and income observations. One response,
one instant; the funds echo and its labelled day can never disagree
again.

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

### 5.3 The schedule of record and its boundaries

Fixed ops 11 + flow ladder 12 + tail 2 = **25 requests**, inside the
32-request budget of record (`FREIGHT_REQUEST_BUDGET_V2`,
`corridor_freight_v2.py:168`):

- **Fixed 11**: `site-00`, `engine-00`, `purchase-00`, `vread-00`,
  `order-00`, `order-01`, `order-read-00`, `monitor-00`, `start-00`,
  `vread-01`, `arrive-00`. The first ten are instant exchanges (no
  in-package wait) and complete within the launch day in the expected
  case; the authority enforcement below bounds them regardless.
  `engine-00` additionally pins the raw running cost of record (§4.1).
- **Arrival bound**: the launch day of record is L = 712228 (Jan 6,
  1950 — the save's current date at load, pinned by E99's `sample-00`
  anchor at tick 17). `arrive-00` waits at most 5 economy days
  (timeout by day 712233); a timeout is a terminal `ARRIVE_TIMEOUT`,
  never a retry. Its completion instant latches the ladder anchor A.
- **Flow ladder 12**: `flow-00` … `flow-11`, offsets 0..55 step 5
  relative to A; `flow-00` observes at the anchor instant itself
  (offset 0, no wait). Day-ladder arithmetic of record carries over
  (day − anchor == pinned offset; overshoot = WINDOW_EXHAUSTED).
- **Tail offsets of record**: `finance-00` and `finish-00` execute
  immediately after `flow-11`'s response, in the same economy day
  (offset 55, no in-package wait). Their funds and income echoes are
  covered by the same model (§4.4), so the reconciliation spans the
  entire attempt with no unattributed gap.
- **Worst-case elapsed days and the 60-day authority**: arrival
  ≤ 5 days (A ≤ 712233) plus the 55-day ladder puts the last
  observation day at ≤ A + 55 ≤ **712288 = L + 60**. The
  60-economy-day attempt authority (`FREIGHT_DAY_BUDGET_V2`,
  `corridor_freight_v2.py:171`) is enforced twice, independently: the
  package refuses any ladder step whose target day exceeds the
  authority, and the pipeline checks elapsed days before sending each
  request — either check failing halts fail-closed.
- **Month-boundary coverage**: the Feb 1 boundary (day 712254) is
  inside the ladder for every admissible anchor (A ≤ 712233 < 712254 ≤
  A + 55); the Mar 1 boundary (day 712282) is additionally inside iff
  A ≥ 712227; `sampled_months` ≥ 2 distinct months holds for every
  admissible anchor (the samples always reach past Feb 1). The funds
  model covers every boundary that falls inside the span, and the
  Feb 1 charge (192) is the E99-replicated cross-check of record. A
  fast anchor reduces the number of exercised boundaries, never the
  exactness of the model — and the span is never stretched ad hoc.
- **Internal polling versus network budget**: the per-tick event
  polling inside `arrive-00` and the flow waits is internal to the
  package — it consumes game ticks and **zero** network exchanges;
  the 25-request budget is the only exchange budget. Polling cost is
  bounded by the per-tick GS instruction limit, within which the
  freight v2 watch loops already operated across full 2048-tick
  windows; every flow wait here spans 370 ticks (5 days), well inside
  that precedent. A latch array that would overflow its response
  budget refuses the exchange terminally — latches are never
  truncated to fit.
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
latches accumulated during the wait (bounded; an overflow refuses the
exchange terminally — latches are never truncated to fit). Response
schema
`cargo-flow2-sample-receipt-v1`; every exchange fail-closed
(`D5_NATIVE_FACT` on any throw, E99 discipline).

### 5.5 Outcome typing

Terminal classifications typed at the attempt layer, none of which
re-opens any other family:

- `CARGOFLOW2_DELIVERY_VERIFIED` — all seven acceptance criteria (§7)
  hold on the retained receipts.
- `CARGOFLOW2_QUEUE_NEVER_FILLED` — arrival witnessed, `wait_pickup`
  stayed 0 through the ladder: the drain side is implicated with the
  selector proven open, a stronger H1-class record than E99's.
- `CARGOFLOW2_LOADED_NEVER_DELIVERED` — a load latched, no bay
  arrival/unload observed.
- `CARGOFLOW2_CONSUMPTION_UNOBSERVED` — delivery received (`stock_bay`
  rose) but no measured net drain within the ladder (§3.4 S5).
- `CARGOFLOW2_FUNDS_DIVERGED` — the modeled-trajectory fence fired
  (fail-closed by construction).
- `CARGOFLOW2_GATE_UNDECIDED_INCOMPLETE` — an unobserved or unfinished
  ladder decides this, as in E99.

## 6. Event sequence of record

The expected native ordering, each step independently evidenced:

1. Launch on the reload chain; `site-00` re-pins the corridor identity
   (depot 45487, pickup stop sid 0 @ 45748, bay stop sid 2 @ 50862,
   industries 0 @ 44983 / 1 @ 51116, cargo 1 COAL, funds 489650).
2. `engine-00` admits the pinned engine at census and pins the raw
   running cost of record (`GSEngine.GetRunningCost`, §4.1);
   `purchase-00` realizes exactly −4429 (funds 485221); `vread-00`
   reads the vehicle in the depot.
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
7. `finance-00` corroborates the quarter income/delivered totals and
   `finish-00` certifies cleanup — both in the `flow-11` economy day
   (offset 55, §5.3); replay re-derives the verdict, including the
   five-stage chain (§3.4), from the receipts alone.

## 7. Acceptance criteria (Section C)

All seven are measurable from the retained receipts alone:

1. **Queue positive (S2)**: `wait_pickup > 0` at ≥ 1 flow sample whose
   labelled day is after the `arrive-00` arrival latch — with
   `wait_pickup_from0 > 0` attributing the cargo to industry 0 — and
   `stock_pickup` still exactly −1 on every sample.
2. **Loads and departs (S3)**: a latched load event at the pickup stop
   with `GSVehicle.GetCargoLoad > 0` and a departure latch (location
   leaves the pinned stop tile) with the load still > 0.
3. **Delivery received (S4→S5 handoff)**: a latched load→0 transition
   at the bay stop tile, `stock_bay > 0` at ≥ 1 flow sample after that
   arrival, and a positive income delta in the unloading span with the
   finance readback's delivered/last-accepted fields increased.
4. **Industry consumption (S5)**: a later measured net decrease of
   `stock_bay` following its rise. A rise with no subsequent decrease
   leaves this criterion unproven and types
   `CARGOFLOW2_CONSUMPTION_UNOBSERVED` — never folded into a success.
5. **Producer transport (S1)**: the pickup industry's transported
   history of record rises above its anchor 0 (`trans_pickup > 0` at a
   post-boundary sample) — the engine's own monthly accounting,
   independent of the station- and vehicle-side observables.
6. **Financial reconciliation matches engine accounting**: the §4.4
   zero-residual fence holds at every exchange from `site-00` onward
   (purchase, monthly staircase + fee, Fract running costs, the empty
   other-expenses set, measured income); `residual ≠ 0` is a halt,
   never a tolerance.
7. **Replay independently verifies ≥ 1 complete delivery cycle**: the
   offline replay of the receipts reconstructs one full cycle through
   the five stages (§3.4) from the latched events without importing
   the native session's own verdict.

## 8. Risks and mitigations

1. **Arrival latency vs the 60-day authority** — `arrive-00` is
   bounded at 5 economy days; a timeout is terminal
   (`ARRIVE_TIMEOUT`), never a retry, and the ladder never starts
   without its anchor.
2. **Month-boundary count depends on the anchor** — `sampled_months
   ≥ 2` is a receipt property of record; an anchor too late for it
   halts fail-closed instead of stretching the span.
3. **Bay-side temporary refusal and consumption cadence** —
   `IndustryTemporarilyRefusesCargo` (`ottd/src/economy.cpp:1055`
   area) can delay accepted-pile growth, and a bay industry may
   receive without draining inside the ladder; the former delays
   criterion 3, the latter types `CARGOFLOW2_CONSUMPTION_UNOBSERVED`
   honestly (§7 criterion 4). Refusals and plateaus are recorded as
   observations, never invented around.
4. **Bay catchment** — the accepted pile grows only for industries in
   the bay station's `industries_near`; the world of record was built
   with the bay stop serving industry 1, and `stock_bay` reading 0
   (not −1) at every E99 sample already proves acceptance; the
   behavioral proof of catchment is criterion 3 itself.
5. **Funds-model exactness** — every parameter is pinned (§4.1);
   the running-cost raw is measured natively at `engine-00` rather
   than derived from the price table; the emulation replicates the
   Fract carry exactly (§4.3); the fence stays zero-residual and
   fail-closed. The model is never loosened to pass.
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
2. Approve the schedule arithmetic and boundaries (§5.3): 25 requests,
   the 12-sample 55-day ladder, the 5-day arrival bound, the tail at
   offset 55, the worst-case 60-day elapsed bound and its dual
   enforcement, and the polling-versus-exchange budget split.
3. Approve the complete financial model of record (§4) — purchase,
   monthly interest staircase, station fee, running costs with exact
   fractional carry, the empty other-expenses set, measured delivery
   income, and the native `GSEngine.GetRunningCost` pin at
   `engine-00` — as the zero-residual fence target, replacing the
   static close-out pin.
4. Approve the seven acceptance criteria (§7) — including the split
   delivery-received / industry-consumption proof — as the round's
   gate, and the outcome typing (§5.5) as terminal classifications.
5. Approve the E100 disclosure (§1.1) as recorded: this round's
   evidence base is the committed 15.3 sources and the retained E99
   receipts, nothing else.
