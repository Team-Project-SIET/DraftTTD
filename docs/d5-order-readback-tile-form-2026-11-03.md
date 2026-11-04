# Order-readback tile-form fix (design record, 2026-11-03)

**Status: witnessed design record.** Round of record: Path A R4 launched
`D5-FREIGHT-5` (`d5-corridor-freight-native-candidate-5`) once and
halted terminal at `order-00` with `READBACK_MISMATCH` (E92). This
record fixes the instrument that mis-read the halt, defines the fresh
identity `D5-FREIGHT-6`, and leaves every consumed candidate and every
historical byte untouched. Implementation, suites, staging, review,
Gate C signing and launch each remain their own explicit operator
approvals — nothing in this record executes natively on its own words.

## 1. What E92 measured, and what it did not measure

The candidate-5 run preserved, in order, all four exchanges before the
first order exchange — every one on the loaded v3 depot-mutation world
(`183b20273a54ebe1…1efe6a6`, world-pin version 3):

1. `site-00` SITE_ADMITTED — accept 8, production 104,
   `pickup_sid 0`, `delivery_sid 2`, and **`depot_edge true`**: the
   site gate of record (`corridor_freight_v2.py:1277-1278`,
   `depot_edge is True`, E58 branch-4 strict, UNTOUCHED) passes
   natively for the first time in the family. The F-12 chain exists
   for exactly this measurement.
2. `engine-00` ENGINE_ADMITTED — engine pin 123, quote 4429.
3. `purchase-00` BUILT — cost 4429, funds 489650 → 485221, vehicle 1.
4. `vread-00` READ — positive vehicle readback, NATIVE_STATE_CHANGED.

The halt then came at `order-00`: the package reported
`status READBACK_MISMATCH` with `cost 0`; the native pipeline classified
`world_state UNCERTAIN_AFTER_FAILED_COMMAND` (conservative post-mutation
class — an append command may have persisted before the mismatching
readback) and preserved the prefix. The replay verifies
`PHASE_HALTED_EVIDENCE_PRESERVED` exit 1.

E92 did **not** measure: any world defect, any staging or signing
defect, or any change to the E58 world assumptions. The site, engine,
purchase and readback observations re-measured the staged facts
verbatim. AppendOrder returned true (the package would have typed
`UNSUPPORTED_NATIVE_FACT` otherwise); the first condition of the
readback comparison was what tripped, short-circuiting the check.

## 2. The defect, bounded to primary sources

The defect is an instrument defect in the package's model of the
15.3 script order API — the E72 class (script-layer model of the
native API wrong; offline stub shares the model, so both suites stay
green while native trips).

Primary source of record, OpenTTD 15.3 (`ottd/` at the committed
submodule, the pinned binary's own source):

1. `ottd/src/script/api/script_order.cpp:455-500` —
   `ScriptOrder::AppendOrder(vehicle_id, TileIndex destination, flags)`
   delegates to `InsertOrder`, which resolves the destination by tile:
   `::GetOrderTypeByTile(destination)`; for a truck-stop tile
   (`MP_STATION`) this is `OT_GOTO_STATION` and the order is stored as
   `order.MakeGoToStation(::GetStationIndex(destination))` with
   `SetLoadType(GB(order_flags, 5, 3))` / `SetUnloadType(GB(flags, 2, 3))`.
   The append's input form is a TILE; the stored destination is a
   station index.
2. `ottd/src/script/api/script_order.cpp:241-284` —
   `ScriptOrder::GetOrderDestination(vehicle_id, order_position)` returns
   a TileIndex. For a goto-station order it translates the stored
   station back to a canonical tile: train-station tile if the station
   has one, else `bus_stops->xy`, **else `st->truck_stops->xy`** — the
   first truck-stop tile of the station. It never returns the StationID
   itself. (Ordered branch precedence exactly as in the source.)
3. `ottd/src/script/api/script_order.hpp:40-85` — the 15.3 flag layout:
   `OF_NONE = 0`, `OF_FULL_LOAD = 2 << 5`, `OF_FULL_LOAD_ANY = 3 << 5`,
   `OF_NO_LOAD = 1 << 7`, `OF_GOTO_NEAREST_DEPOT = 1 << 8`. The Python
   side pins these as record (`corridor_freight_v2.py:24`).

The package readback model (`app/simulation/openttd/d5_freight_v2_package/main.nut`)
compares the readback value against the site-latched **StationIDs**:

- `main.nut:937-939` (order op): `expected_sid = order_index == 0 ?
  this.site_sid0 : this.site_sid1`, then
  `if (d != expected_sid || f != flags || g != true) status =
  READBACK_MISMATCH`.
- `main.nut:978-980` (order-read inventory): the same form for
  `d0`, `d1`.
- `main.nut:897-900` — the N1 comment claims the readback "verifies
  that resolution against the site-latched sids". The sid-form
  readback was never true in 15.3.

The latches themselves are correct and native-proven by E92:
`this.site_sid0 = obs.pup.sid` where
`obs.pup.sid = GSStation.GetStationID(tile)` (`main.nut:392-421`,
`main.nut:699-700`) — real station indices 0 and 2, as the site-00
receipt records.

The offline stub shares the conflation, which is why both freight
suites were green across the entire v3 chain offline work:

- `tests/support/canonical_protocol_vm.nut:112` —
  `GSOrder.GetOrderDestination` returns `orders[n].tile` (the appended
  tile echoed back; the wire's own model, `corridor_freight_v2.py:932`,
  matches this tile-form correctly).
- `tests/support/canonical_protocol_vm.nut:94` —
  `GSStation.GetStationID(t){return t in ::stations ? t : 65535;}` —
  the tile-as-"id" model; offline, the latched sid equals the tile, so
  the package's tile-vs-sid comparison passes by construction.

The Python side of record needed no correction and stays untouched:
`corridor_freight_v2.py:1514-1530` already verifies
`read.dest == plan.pickup / plan.delivery` (tile form) with the
exact message "order destination must be the pinned stop tile (N1)",
and `corridor_freight_v2.py:817-819` reads the response keys
`dest`/`flags`/`goto`/`income` as-is.

Family-history note: this exchange path had never been natively
measured. Historical freight candidates 1 and 3 halted at `site-00`
(delivery acceptance below 1/8; INVALID_SITE on the pre-depot world)
and candidate-4 (`D5-FREIGHT-4`) was never signed or launched.
Candidate-5 is the first family member past the site gate, and its
`order-00` is the first native observation of this readback in the
D5 lineage.

## 3. The fix (package-side, minimal and faithful)

Two condition blocks in `main.nut` change; nothing else in the
package does.

### 3.1 OrderOp readback (`main.nut:930-942` today)

The 15.3 two-way truth is: append takes a stop tile and stores the
station the tile resolves to; the readback returns that station's
canonical stop tile. The faithful readback therefore verifies the
full round trip — tile-form destination equality **plus** the
resolved station identity:

```squirrel
    /* N1 (15.3, E92): the append takes the stop TILE and stores
     * GetStationIndex(tile); the readback returns the station's
     * canonical stop tile (truck_stops->xy), never the StationID.
     * The readback pins the tile-form destination AND deepens it
     * with the station identity: the tile must resolve to the same
     * site-latched station. Flags round-trip per the 15.3 layout;
     * the order must read goto-station. */
    local expected_tile = q.order_index == 0 ? this.pickup : this.delivery
    local expected_sid  = q.order_index == 0 ?
        this.site_sid0 : this.site_sid1
    if (d != expected_tile ||
        GSStation.GetStationID(d) != expected_sid ||
        f != flags ||
        g != true) {
        r.status = "READBACK_MISMATCH"
        return
    }
```

For the world of record each latched station has exactly one truck
stop (exactly-one box membership, measured at site-00 and by the
E68 census for the same tiles), so `st->truck_stops->xy` is the
pinned stop tile and `d == expected_tile` holds. The added
`GetStationID(d) == expected_sid` keeps the check honest if a
future world ever gives a station a multi-stop truckstation: the
instrument then still knows the stop resolved to the latched
station, while the tile-form check fails closed (terminal halt,
same discipline as E92) — never a silent widening.

The response record is unchanged: on success the op publishes
`r.dest <- dest` — per the wire contract the response field
carries the **appended stop tile** (`q`-derived), which is what
`corridor_freight_v2.py:1514-1530` verifies against `plan.pickup /
plan.delivery`. No response-shape change, no wire change.

### 3.2 OrderReadOp inventory (`main.nut:963-981` today)

The inventory readback gets the same two-way treatment for both
stops:

```squirrel
    if (d0 != this.pickup || GSStation.GetStationID(d0) != this.site_sid0 ||
        f0 != this.OF_NONE || g0 != true ||
        d1 != this.delivery || GSStation.GetStationID(d1) != this.site_sid1 ||
        f1 != this.OF_NO_LOAD || g1 != true) {
        r.status = "READBACK_MISMATCH"
        return
    }
```

(`order_len == 2`, `income` guard and every other line of op stay
verbatim.)

### 3.3 The N1/N2 comments

The comment blocks at `main.nut:897-900` (N1) and the inventory's
companion comment are re-stated to teach the actual 15.3 two-way
tile model with the E92 citation — the comments are part of the
instrument's honesty; the old wording is the defect's home.

### 3.4 Stub fidelity (the wire suite's embedded `GSOrder` fixture)

Amendment (disclosed at implementation review time): the freight wire
suite does not consume `tests/support/canonical_protocol_vm.nut` — it
embeds its own `GSOrder` fixture inside `tests/test_corridor_freight_v2.py`
(lines 386-409 at record time), which still modeled the old N1
sid-form store. The faithful two-way model is corrected there; the
`tests/support/canonical_protocol_vm.nut` line (whose only consumer is
the standalone squirrel validator) is corrected to the membership form
of the same model for consistency. `GSStation.GetStationID` in the
wire world already returns real sids (`(::stops[t]).sid` — 0/2), side
by side with every observe-path latch.

The faithful fixture form (tile in, station stored, tile-form
readback, flag round-trip verbatim):

```squirrel
static function AppendOrder(id, dest, flags) {
    ::append_calls.append([dest, flags]);
    if (!(id in ::vehicles) || !(dest in ::stops)) return false;
    /* N1 (15.3, E92): the append takes the stop TILE; the resolved
     * station (MakeGoToStation of GetStationIndex(dest)) is stored
     * alongside for the goto-station membership. */
    ::orders[id].append({d = dest, sid = ::stops[dest].sid, f = flags});
    return true;
}
static function GetOrderDestination(id, i) { return ::orders[id][i].d; }
static function IsGotoStationOrder(id, i) {
    return ::orders[id][i].sid in ::station_types;
}
```

`GetOrderFlags` unchanged (flags round-trip verbatim — the same
native-fact check the f-condition performs). The one evidence test
(`test_stub_appends_carry_tile_destinations_and_real_flags`) newly
asserts the stored shape: `d == the pinned stop tile`,
`sid == the latched sid (0 / 2)`, flags verbatim, OF_FULL_LOAD
never issued — append-call audit unchanged.

`GSOrder.IsGotoStationOrder` stays `true` for station destinations;
`GetOrderFlags`/`AppendOrder` unchanged (flags round-trip verbatim,
which is also the native-fact check the f-condition performs).

### 3.5 What does not change

Byte-identical to the R4-of-record forms, unchanged:

- schedule v2 (30 exchanges, ids `FREIGHT_EXCHANGE_IDS_V2`, cycles 6),
  route and witness policies, plan digest policy
  (`ed5bad8237dd6898…` survives), plan model fresh by identity+funds;
- funds chain of record (490257 A1 pin kept; funds-at-close 489650),
  budgets (max_cost 5000, wire echo 1450, 1 launch, 0 retries,
  0 reconnects), readback policy;
- site gate `corridor_freight_v2.py:1277-1278` (`depot_edge is True`)
  — untouched;
- prelaunch schema `d5-freight2-prelaunch-v2` and provenance
  `world_pin_version 3`;
- prerequisite chain: consumed `D5-F12-DEPOT-3` after-save
  `183b2027…6a6` at candidate-3 + `D5-F12-DEPOT-RELOAD-1`
  (`DEPOT_RELOAD_FACTS_VERIFIED`) — `freight_facts()` and
  `prerequisite_binding()` untouched;
- site/company tile pins, engine pin 123, binary pin
  `276d5b69…1904c`, OpenGFX pin `43a0c1da…03be`;
- the Python side (`corridor_freight_v2.py`, relay of record) — no
  edit (already tile-form correct, §2).

## 4. Fresh identity

Round discipline (E24/E74 identity-bump precedent): the consumed
`D5-FREIGHT-5` keeps its terminal halt preserved byte-verbatim and is
never re-used or relabeled; the next staged candidate is

- `FREIGHT_ATTEMPT_V2 = "D5-FREIGHT-6"` (`corridor_freight_v2.py`,
  single constant), consumed attempt-5's history intact.

Every staged fact re-derives from the same sources of record; the
plan model digest will be fresh (identity feeds it); the plan digest
`ed5bad8237dd6898…` byte-identical (schedule policy unchanged).

## 5. Implementation plan (offline, gated)

Order of work, each step fail-closed and stopped at every gate:

1. Offline implementation round (one operator approval): the two
   package condition blocks + comments (§3.1-3.3), the stub line +
   comment (§3.4), the identity bump (§4), and nothing else. Suites
   of record re-run green (the two freight suites, 61 + 67), ruff
   clean, `ty` only the five tolerated baseline diagnostics in
   untouched regions, `git diff --check` clean, ws-clean byte-untouched
   (all E92 pins re-digested).
2. Staging approval (one prepare run of record, schema
   `d5-freight2-prelaunch-v2`, world-pin version 3, prerequisite =
   consumed `D5-F12-DEPOT-3` at candidate-3, fresh COPY of the pin
   verified) then read-only `preflight`/`verify` — preflight may be
   re-run, launch stays absent.
3. Independent read-only review (E80/E85/E90 in-session precedent):
   re-derive every staged fact, including the new package readback
   conditions and the composed GameScript ≡ live package digest.
4. Gate C signing approval (Option-1 checklist; seed env-only, never
   printed/filed/arg-passed; verified under the pinned anchor before
   write; cleared after). Signature only — never launch approval.
5. Launch approval (exactly one native attempt, both outcomes
   terminal, no retry), then post-run replay verification, cleanup
   certification and manifest audit; evidence row appended.

## 6. Risks and mitigations

1. **f/g native round-trip stays unproven** for `OF_NO_LOAD`
   (delivery stop) and for `IsGotoStationOrder` — E92's halt came at
   the first condition, so natively only the d-condition had been
   exercised. The design keeps f/g as recorded instrument conditions
   (unweakened); if any native round-trip fact differs from the
   15.3-design, the halt returns fail-closed and its evidence
   preserves a new design round. No silent widening, ever.
2. **Multi-stop stations**: today both latched stations have exactly
   one truck stop (measured); the deepened identity check
   (`GetStationID(d) == latched sid`) is the robustness rider — if a
   future world returns a non-appended canonical tile, the
   tile-form check refuses terminally rather than pass on
   identity alone. Conservative by construction.
3. **Stub-scope creep**: only the one stub line + comments change;
   the observe path, fixtures and every other package's suites are
   not in scope; the two freight suites are the green gate for the
   stub change's blast radius (plus the depot/census/recheck suites
   re-run as part of the ws-clean re-verify pass).
4. **Composed-package correspondence**: the package bytes change →
   the composed GameScript in the staged candidate differs from
   `6704aa6e…952d` — the review gate re-derives the composed ≡ live
   equality against the NEW live package digest (recorded at review
   time), never against the retired E76 constant.
5. **Stale-predecessor bytes**: `D5-FREIGHT-4` (staged-once,
   stale-by-construction) and the consumed terminal candidates 1-5
   are byte-frozen; the identity `D5-FREIGHT-5` is spent and its
   name never re-used.

## 7. Open operator decisions at review time

Nothing in this record decides them; the review gate presents them
explicitly:

1. Approve the exact fixed condition blocks as written (§3.1-3.2) —
   in particular that the deepened station-identity check is
   **added** rather than replaced (the instrument gets stricter, not
   looser).
2. Approve the stub comment/line form (§3.4) as the offline model of
   record for the 15.3 canonical-stop-tile resolution.
3. Approve the fresh identity (`D5-FREIGHT-6`) and the frozen
   everything-else set (§3.5, §4) before staging is asked.
