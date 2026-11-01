# D5 Freight Delivery v2 — independent adversarial design review (offline)

Status: **DESIGN-REVIEW RECORD ONLY.** Offline, read-only review of the locked D5
Freight Delivery v2 design decisions; produced 2026-11-01 on branch
`miles/fright-delivery`, HEAD `fee7459` (working tree clean, verified before the
review and unchanged after it except for the cross-referenced documentation
entries). No candidate, claim, seal, signature, authorization, launch,
AdminPort session, POSTGRES, replay-driven relabeling or git mutation exists
because of this record. It authorizes nothing. It changes no locked decision.
`OpenTTD-Knowledge/` was deliberately left untouched (pull-in reference, not
app content).

## 1. Inputs and method

The locked decisions D1–D8 (baseline `fee7459`; Option B stronger service
proof: max 32 protocol requests/exchanges under the repository's actual
counting semantics, 900 s, 60 economy days, one launch, one connection, zero
retries; the A1 after-save world `3748e00ce57bcb076466f50cac3776c202b4fd130d6c6071935e9d43e45420bd`
at £490,257; the pinned route with delivery bay 50862/station ID 2; no
`OF_FULL_LOAD`, per-cycle `delivered == loaded == monitor_delta`; quote-first
purchase ≤ £5,000 with strict funds reconciliation and zero construction; a
pinned engine ID without fallback; replay-verified cycle claims) were treated
as authoritative inputs. Three fresh-context read-only reviewer agents ran in
parallel (A: engine/world feasibility; B: protocol/budget feasibility;
C: accounting/proof integrity) against the retained evidence and current
implementation, and their findings were cross-reviewed against primary
sources. All three were constrained to the same read-only boundaries used for
this record.

Facts of record consulted (summary): E35 (`D4-CORRIDOR-5` complete, after-save
`a81ac836…ef261`, £496,543 → £492,149), E36 (`D5-FREIGHT-1` halted at site-00,
zero mutation), E40 (A0 survey: 50351 = 0/8, 50862 = 8/8, prod 104), E41–E44
(A1 v2 implementation, staging, signing, native completion: op-00 £1,144,
op-01 £142, op-02 spur £299, op-03 station £307 `DISTINCT_NEW_STATION` sid 2,
route 30/30, funds £490,257, after-save `3748e00c…5420bd`), E45–E49 (census
design, implementation, staging, signing, native completion
`SURVEY_COMPLETION_VERIFIED`). Labels used below: VERIFIED NATIVE (retained
consumed-attempt evidence), VERIFIED OFFLINE (re-derived from repository bytes),
IMPLEMENTED BUT NOT NATIVE-VERIFIED, DESIGN ASSUMPTION, UNKNOWN.

## 2. Verdict

**`DESIGN READY WITH CONDITIONS`.** The locked decisions are internally
consistent and every questioned mechanism has either a native-verified
precedent (quote-first purchase with cost equality, one-launch/one-connection/
zero-retry lifecycle, per-exchange funds readbacks, replay discipline) or a
bounded additive implementation path. Unconditional READY is withheld for two
gaps: (a) engine-ID offline provenance has no supporting evidence in the
repository (D6's required derivation source is absent on disk); (b) the
funds-halt rule needs an operator-approved category taxonomy so legitimate
vehicle running costs are neither relabeled as drift nor silently accepted.

## 3. Consolidated findings

Findings F-1..F-14 consolidate reviewers A-1..A-6, B-1..B-7, C-1..C-8 after
cross-review. Severity scale BLOCKER / MAJOR / MINOR / NIT per the review
charter. "Operator input" marks decisions that must be made before or during
implementation; none of them changes a locked decision.

### F-1 · BLOCKER · D6 (engine-ID provenance)

The repository contains no default-Temperate engine-list authority:
`OpenTTD-Knowledge/` holds API prose and external links only, and the only
native engine enumerations bind to different worlds (legacy road-vehicle
lifecycle, engine 123, cargo 1, capacity 20, price £4,429, on a seed-42 world —
`docs/road-vehicle-lifecycle-proof.md:21,49`). Implementing D6's "derived
offline from engine-list evidence" as written would seal an unestablished
identity. Native runtime validation of the pinned ID before purchase is
implementable and fail-closed (F-10), which caps the damage, but provenance
itself is unsupported. Resolution options (operator decision): acquire
authoritative engine-list evidence for the pinned runtime/GRF configuration
and bind it into the candidate; or amend D6's provenance wording to a
provisional offline pin that only the native fail-closed gate accepts.
Operator input: yes.

### F-2 · MAJOR · D3/D5/D7 (route representation)

A1's physical witness is 31 tiles with a revisit (backtracked 50095); a
vehicle-legal unique pickup(45748)→bay(50862) path is 29 tiles
(`corridor_extension_native.py` PINNED_WITNESS; route receipt 30/30). The
existing freight shape refuses it: `RouteOk` caps 3–24 unique tiles with
endpoints pickup→delivery, one depot-adjacent tile, no depot tile
(`app/simulation/openttd/d5_freight_package/main.nut:113,639–661`).
Resolution: a new versioned freight protocol/package carries the vehicle-legal
29-tile route (delivery 50862 last, front 50863 penultimate, 45743 the single
depot-adjacent tile) and binds the 31-tile physical witness for transit and
road-bit monitoring semantics. No locked decision changes.

### F-3 · MAJOR · D5/D8 (stale world pins)

Current v1 pins target the D4 world: funds equality against 492,149
(`app/simulation/openttd/corridor_freight.py:681–682,772,851–852`,
`FUNDS_AT_D4_CLOSE` line 92), delivery 50351 (`:301–303,772`), and
`FREIGHT_DELIVERY_INDUSTRY = 1` (`:91`). v2 runs on the A1 world at
£490,257 with delivery bay 50862 (station ID 2, provenance `ext-route-read.json`
`pickup_sid 0` / `delivery_sid 2`; station 1 = the old bay 50351). The
industry that supplies 8/8 coal acceptance near 50862 is UNKNOWN and must be
observed natively before orders. Resolution: v2 re-derives all world pins from
the A1 after-save; no silent substitution.

### F-4 · MAJOR · D4/D7 (full-load pins)

The implemented chain pins exactly what the design forbids: orders append
`OF_FULL_LOAD` (`corridor_freight.py:99`, `d5_freight_package/main.nut:1406`)
and the LOADED gate demands `load == capacity` (`main.nut:1320`). Resolution:
v2 order flags without `OF_FULL_LOAD`, departure gate `0 < load ≤ capacity`,
per-cycle completion gate delivered ≥ 1, additive contract versioning.

### F-5 · MAJOR · D7 (multi-cycle schedule, verifier, monitor discipline)

The entire freight chain is single-shot: 15 pinned exchange IDs
(`corridor_freight.py:86,167–183`), index-locked stages
(`d5_freight_package/main.nut:125–141,162–167,1734–1740`), replay/v verifier
that demands exactly 15 exchanges (`corridor_freight.py:1540–1541`), monitors
armed once and consumed once with no per-cycle snapshot chain
(`:1109–1110`, `main.nut:1400–1407`). Resolution: cycle-looped
`load-watch → transit-watch → deliver-watch` with per-cycle snapshot
discipline — departure snapshot with pickup-monitor delta 0 before departure
and L after; delivery equality (`load == 0`, both monitors equal L,
consume-with-recheck == 0) before re-entry; variable-length replay verifier
and per-cycle retained evidence; per-cycle finance read optional (costs one
request each, see §4). Survey/extension replay precedents show the pattern is
implementable.

### F-6 · MAJOR · D5 (funds equation vs legitimate costs)

The funds ledger records every per-exchange delta but enforces only the
purchase delta (`corridor_freight.py:33–38,949–968,1512–1522,1560–1561`);
"halt on unexplained funds drift" has no definition of _unexplained_. Vehicle
running costs are an expected, legitimate mechanism with no monitor, and a
−£1 non-purchase drift was observed natively on the legacy lane
(`docs/road-vehicle-lifecycle-proof.md:21,49`). Resolution (operator-approved
taxonomy): equation of record `490,257 − purchase + Σ(income deltas
attributed via in-window FinanceOp reads) + Σ(running-cost category as
observed, bounded by an operator-approved per-window allowance)`; any other
delta halts typed. Whether `GSEngine.GetRunningCost` exists in the 15.3
Script API is UNKNOWN and must be verified at implementation. Operator
input: yes.

### F-7 · MAJOR · D8 (per-attempt economy-day authority)

Each watch window is capped at ≤ 30 economy days
(`d5_freight_package/main.nut:1241–1247`) but no per-attempt 60-day budget is
enforced across windows; a saturated cycle can overspend the lifecycle
(3 × 30 = 90). Resolution: the Python schedule layer is the authority
(remaining days must exceed the next window/cycle caps before dispatch, with
headroom); saturated windows keep typed `WINDOW_EXHAUSTED` inconclusive
semantics.

### F-8 · MINOR · D8 (cap exhaustion shape)

The GameScript drops the 33rd request silently
(`main.nut:282–284,531–533,1647–1652`), surfacing client-side as a timeout —
not a typed budget refusal. Resolution: v2 pre-checks the remaining budget
before dispatching any cycle group; a partially budgeted final cycle is never
dispatched, so it can never be counted.

### F-9 · MINOR · D8 (wall-clock cycles)

Worst case all three windows saturate their 60 s wall caps → 180 s per cycle,
binding 900 s at about 4 cycles; in the realistic legacy-pace regime the
request cap binds first. Resolution: plan the cycle count from the §4
arithmetic at staging, keep window headroom, keep inconclusive semantics.

### F-10 · MINOR · D6 (pinned-engine admission additive)

The v1 engine op ignores any request engine pin and picks the lowest
compatible ID (`main.nut:697–698,943–956`); purchase later re-quotes the
latched ID (`:1007–1055`). Resolution: an additive read-only pinned-engine op
that validates `IsValidEngine`/`IsBuildable`/truck-type and **default cargo
== 1** (the existing `Compatible()` does not require it — reviewers A/C),
quotes it with the existing test-mode machinery, and refuses
`NO_ENGINE`/`UNAVAILABLE_ENGINE`/`COST_CHANGED`/`COST_LIMIT` before any
purchase mutation. Operator input: no (beyond F-1's provenance decision).

### F-11 · MINOR · D7 (zero-cycle terminal status)

"Zero completed cycles is valid but unsuccessful" has no distinct status slot;
current outcomes collapse to `PHASE_HALTED_PREFIX_PRESERVED, verified false`
(`proof/corridor_freight_native.py:1456–1457`, `corridor_freight.py:1599–1608`).
Resolution: a typed zero-cycle outcome, never a success relabel, still
receipt/manifest/replay-bound. (E36 is the archetype: refusal before mutation
with zero drift.)

### F-12 · MINOR · D3 (depot entry probe)

`depot_linked` checks ownership and the front tile, not the depot↔front road
bit (`d4_corridor_package/main.nut:184–190`); no vehicle has exited the depot
on this world. Mitigation of record: `BuildRoadFull` builds both straight bits
at span endpoints (`docs/handoff/2026-10-25/d4-corridor-op03-root-cause.md`),
which includes 45743. Resolution: one additional site readback road-bit probe
(front facing the depot) before purchase.

### F-13 · MINOR · D8 (duration retention)

Retained records lack explicit elapsed-duration fields (mtime-only
reconstruction). Resolution: echo per-window elapsed ticks/days/wall seconds
from the existing GameScript loop state (data already present internally).

### F-14 · NIT · docs

Pre-existing documentation-vs-code asymmetry: the check row
"every per-exchange funds delta reconciles exactly"
(`docs/d5-corridor-freight-design.md:414`) vs the honest header note
(`corridor_freight.py:33–38`). Carry the same honesty into v2 wording.

## 4. Request-budget calculation

Counting rule (VERIFIED OFFLINE, code-verified): one request = one unique
protocol-5 `ADMIN_GAMESCRIPT`/`SERVER_GAMESCRIPT` exchange under a fresh
unique request id; handshake/auth/welcome, subscription/ping, quit and save
operations are never counted; the v1 budget is
`FREIGHT_REQUEST_BUDGET = 32` (`corridor_freight.py:87`) and the GameScript
refuses silently at the cap.

| Component       | Count            | Composition (v1 IDs)                                                                                         |
| --------------- | ---------------- | ------------------------------------------------------------------------------------------------------------ |
| Fixed setup     | 10               | site-00, engine-00, purchase-00, vread-00, order-00, order-01, order-read-00, monitor-00, start-00, vread-01 |
| Per cycle (k=3) | 3                | load-NN, transit-NN, deliver-NN (monitor reads inside watch readbacks)                                       |
| Tail            | 2                | finance-00, finish-00                                                                                        |
| Total           | 10 + 2 + 3N ≤ 32 | **N ≤ 6**                                                                                                    |

Stricter/safer readings: k=4 (per-cycle finance read) → floor(20/4) = **5**;
k=5 → **4**. Wall-clock worst case (all three windows saturate 60 s) binds
900 s at about **4** cycles; the realistic regime is request-cap-governed
(legacy pace evidence: `docs/road-vehicle-lifecycle-proof.md:31–51` movement
costs a few hundred ticks). Delivery-timeout and window-exhausted mid-cycle
outcomes are inconclusive and never counted; per-cycle groups are only
dispatched with verified remaining budget (F-8). The implementation must fix
the per-cycle exchange set and planned cycle count at staging from this
arithmetic — no estimate from intuition.

## 5. Engine-ID feasibility assessment

1. Offline deterministic pin: not possible with current on-disk evidence
   (F-1) — treated as UNKNOWN until the operator's provenance decision.
2. Stability: engine IDs derive from GRF load order; the pinned runtime
   (binary + OpenGFX 8.0 + isolated config) makes the set deterministic in
   principle; engine 123 enumerated identically on two legacy worlds with the
   same graphics identity — supporting, not proving, seed-17 stability.
3. NewGRF/config risk: none beyond OpenGFX in the pinned runtime; the
   pre-launch graphics-identity check binds the configuration class.
4. Runtime cargo compatibility: implementable via
   `GSEngine.GetCargoType`/`CanRefitCargo`/
   `GSRoad.GetRoadVehicleTypeForCargo`, and must additionally require default
   cargo == 1 so no refit (outside the allowed mutation set) is ever needed.
5. Refusal before purchase: implementable — engine op is read-only plus one
   test quote; all refusal paths pre-mutation (`NO_ENGINE`,
   `UNAVAILABLE_ENGINE`, `COST_CHANGED`, `COST_LIMIT`,
   `INSUFFICIENT_FUNDS`).
6. Binding the engine-list evidence into candidate and replay: possible
   through the existing frozen-closure/staged-digest machinery once the
   evidence exists.

## 6. Financial accounting model

Money observed by the protocol is integer; "penny-accurate" means exact
integer equality over exchange-bounded windows. Equation of record:
`funds(final) == 490,257 − purchase_quote + Σ(income deltas via in-window
FinanceOp reads) + Σ(operator-approved running-cost allowance)`; the
`funds_ledger` records every per-exchange delta, consecutive windows leave no
gap, and any delta outside the taxonomy halts typed. Purchase attribution
is native-verified machinery on the legacy lane (quote £4,429 == realized
£4,429, funds 98,989 → 94,560 exactly). A1-world prices are UNKNOWN. Claims
of record must not derive throughput, OPEX, profit or ROI from this
experiment.

## 7. Per-cycle proof model

Cycle boundary of record: a completed exchange whose readback shows
`load == 0` at the delivery bay after a same-cycle observed departure with
`0 < load ≤ capacity`. Three channels: `loaded` = departure load
(`GSVehicle.GetCargoLoad`); `delivered` = unload event state plus
`GSCargoMonitor` industry delivery delta consumed at the boundary exchange
(keep=false, recheck == 0); `monitor_delta` = the same exchange's industry
monitor delta with the pickup monitor consumed inside the same window. The
v2 snapshot discipline (F-5) is what makes per-cycle attribution sound;
without it the monitors report cumulative-since-arm amounts. Cross-boundary
unload residue surfaces as a typed refusal or a failed snapshot gate — never
as a silently counted cycle. `after.sav` is emitted once at terminal
completion as in v1; per-cycle evidence lives in the retained per-exchange
frames. Categories observed / completed native / replay-verified stay
separate; only replay-verified cycles enter the claim-of-record.

## 8. Design-consistency checks (no conflicts found in the locked decisions)

Stronger service proof vs no throughput claim: consistent (bounded cycle
count, no rate derivation). Repeated cycles vs the 32 cap: consistent with
the §4 arithmetic; cycle count must be derived, not intuited. Partial loads
vs per-cycle strict equality: consistent once F-5 discipline exists.
Zero construction vs depot/station availability: consistent — the corridor,
bay, depot and pickup all exist natively in the A1 world (E44). 60 economy
days vs 900 s: consistent; the day budget needs the F-7 authority.
Quote-first vs one-shot: consistent; quote drift halts typed before
mutation. Native engine validation vs offline pin: consistent; provenance is
the open condition (F-1). Replay-verified vs observed cycles: consistent;
needs the F-5 verifier extension. Strict funds reconciliation vs legitimate
operating costs: the single real tension, resolved by the F-6 taxonomy
decision.

## 9. Unresolved UNKNOWN facts

1. Engine IDs, prices, capacities, cargo mapping on the A1 seed-17 world
   (legacy £4,429 engine 123 is a different world).
2. `GSEngine.GetRunningCost` availability in the 15.3 Script API and the
   running-cost accrual cadence.
3. Cargo-1 waiting at pickup at attempt start (production 104 is a
   last-month statistic; waiting backlog UNKNOWN).
4. The industry identity that supplies coal acceptance at 50862.
5. Truck traversal/pathfinding behavior on this corridor (no vehicle has
   ever moved on this world).
6. Per-cycle transit duration in economy days/ticks on this corridor.
7. Retained wall-clock session durations (until F-13 adds them).

## 10. Conditions before implementation

1. Resolve F-1/F-10: engine-list provenance evidence acquired, or operator
   amendment of D6 provenance wording; no pinned ID without it.
2. Operator approval of the F-6 funds taxonomy (running-cost category +
   per-window allowance) or an equivalent amendment of the drift-halt rule.
3. Implement the v2 versioned protocol/package per F-2/F-3/F-4/F-5/F-10 with
   re-derived pins (funds 490,257; delivery 50862/sid 2; delivery industry
   observed natively before orders) and the cycle-looped schedule/verifier.
4. Enforce the per-attempt day budget (F-7) and budget pre-checks (F-8);
   typed zero-cycle outcome (F-11); depot-entry probe (F-12); duration
   echoes (F-13); §4 arithmetic fixes the planned cycle count at staging.
5. All standing gates apply: focused offline suite runs, independent
   read-only review, staging + PRELAUNCH/PREFLIGHT, Gate C signing, and a
   separate explicit launch approval. Each is a distinct operator gate.

## 11. Stop condition

This record ends at design review. The next phase (v2 implementation)
requires separate explicit operator authorization.
