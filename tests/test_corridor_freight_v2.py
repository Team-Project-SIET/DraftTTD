"""Controlled offline tests for the D5 v2 native corridor-freight wire contract.

The shipped ``d5_freight_v2_package/main.nut`` runs inside the real Squirrel VM
against a stub freight world that reproduces the post-mutation close-out
lifecycle
semantics (census-tested quotes, BuildVehicle, tile-destination order appends
with the real 15.x flag values, per-industry GSCargoMonitor
arming/consumption, quarterly finance reads and the directed depot-edge and
stop-radius discovery world); every dispatched reply is parsed back through
the protocol-8 wire contract, never through the package's own words. Stub
knobs inject controlled native refusals so the fail-closed statuses are
exercised against the shipped package itself. The stub order layer keeps the
N1/N2/N3 evidence records (``::append_calls``, ``::n3_calls``): tile
destinations, zero-or-OF_NO_LOAD policies, and the two-argument
AreOrderFlagsValid destination form. Nothing here launches OpenTTD, connects
to an AdminPort or writes any native or save state: only the tests' own VM
world is mutated.
"""

from __future__ import annotations

import re
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
from squirrel import SQVM

from app.simulation.openttd import corridor_freight_v2 as cfv
from app.simulation.openttd.corridor_freight_v2 import (
    MAX_FREIGHT_REQUEST_BYTES_V2,
    MAX_FREIGHT_RESPONSE_BYTES_V2,
    FreightReadbackV2,
    FreightRequestV2,
    freight_phase_outcome_v2,
    verify_freight_attempt_v2,
)
from app.simulation.openttd.proof import corridor_freight_v2_native as work

REPO = Path(__file__).resolve().parents[1]
PACKAGE = REPO / "app" / "simulation" / "openttd" / "d5_freight_v2_package"
API = REPO / "tests" / "fixtures" / "gamescript_api_15.nut"

PRELAUNCH = "a" * 64
OTHER_PLAN = "b" * 64

# The module's own derivations drive every staged pin in the tests, so a
# derivation drift is caught here before any staging: nothing is re-told.
SCHEDULE = work.freight_schedule()
PLAN = work.freight_plan_v2()
EXCHANGES = list(cfv.FREIGHT_EXCHANGE_IDS_V2)

ENGINE_QUOTE = 4429  # the fixed-demo census quote, within the £5,000 ceiling
ENGINE_CAPACITY = 20  # the stub engine's one vehicle capacity slot
ENGINE_MAX_SPEED = 48  # the census speed the reply echoes
FUNDS = 489650  # the pinned post-mutation close-out funds the stub world carries
PICKUP = cfv.A1_PICKUP_STOP_TILE_V2
PICKUP_FRONT = cfv.A1_PICKUP_FRONT_TILE_V2
DELIVERY = cfv.A1_DELIVERY_STOP_TILE_V2
DELIVERY_FRONT = cfv.A1_DELIVERY_FRONT_TILE_V2
DEPOT_TILE = cfv.A1_DEPOT_TILE_V2
DEPOT_FRONT = cfv.A1_DEPOT_FRONT_TILE_V2
PICKUP_INDUSTRY = 7  # the stub world's producer, discovered at the pickup box
DELIVERY_INDUSTRY = 9  # the stub world's acceptor, discovered at the delivery box
ROUTE = cfv.FREIGHT_ROUTE_V2
# The zero-departure exemption covers only the depot and the pickup stop:
# route[2] on the road proves a real empty departure (F-11).
ZERO_DEPARTURE_TILE = int(ROUTE[2])
LOADS = (20, 19, 18, 17, 16, 15)  # cycle 0 full; the rest partial (F-4 gate)
INCOME_PER_CYCLE = 1080  # the stub world's fixed funds/income walk per deliver
INCOME_TOTAL = INCOME_PER_CYCLE * 6
FINAL_FUNDS = FUNDS - ENGINE_QUOTE + INCOME_TOTAL
POSITION_PROGRESS = len(ROUTE) - 1

WORLD = """
::dims <- [256, 256];
::tiles <- {};
::road_links <- {};
::stops <- {};
::station_types <- {};
::depots <- {};
::vehicles <- {};
::orders <- {};
::engines <- {};
::industries <- {};
::industry_of_tile <- {};
::tests <- {};
::account <- 0;
::funds <- 489650;
::quote_cost <- 4429;
::exec_cost <- 4429;
::engine_price <- 4429;
::engine_capacity <- 20;
::next_vehicle <- 1;
::cur_roadtype <- 0;
::roadtype_ok <- true;
::mode_ok <- true;
::valid_company <- true;
::second_company <- 0;
::no_op <- false;
::engine_ok <- true;
::paused <- false;
/* GSCompanyMode's constructor assigns this slot; Squirrel needs it declared. */
::cur_company <- 0;
::days <- 730;
::ticks <- 0;
::reject_start <- false;
::no_stops <- false;
/* Per-industry cargo monitor state (the v2 keyed monitor arming). */
::monitors <- { id = "monitors", pickup = {}, delivery = {} };
::finances <- { id = "finances", income = 0, delivered = 0 };
::waiting <- 5;
::last_accepted <- 900;
::accept <- 8;
::test_calls <- 0;
::real_calls <- 0;
::depot_tile <- 45487;
::depot_front <- 45743;
/* N1/N2/N3 stub evidence: what the appends and the two-arg gate saw. */
::append_calls <- [];
::n3_calls <- [];
::sniffer <- {last = "missing"};
/* Optional per-tick mover hook: only tests that simulate movement set it. */
::mover <- null;
function GetTick() { return ::ticks; }
function break_link(a, b) {
    if (a in ::road_links && b in ::road_links[a]) delete ::road_links[a][b];
    if (b in ::road_links && a in ::road_links[b]) delete ::road_links[b][a];
}
"""

WORLD_SEED = """
function stub_seed(tile, owner) {
    if (tile in ::tiles) {
        if (::tiles[tile].owner == -1) ::tiles[tile].owner = owner;
        return;
    }
    /* bit 7 = road (IsRoadTile), bit 9 = the ROADTYPE_ROAD presence bit. */
    ::tiles[tile] <- {flags = 0x0280, owner = owner};
    ::road_links[tile] <- {};
}
/* The depot: company-owned at the pinned tile, joined to its pinned front. */
::depots[::depot_tile] <- {front = ::depot_front};
stub_seed(::depot_tile, 0);
stub_seed(::depot_front, 0);
::road_links[::depot_tile][::depot_front] <- true;
::road_links[::depot_front][::depot_tile] <- true;
/* The derived A1 vehicle route: every adjacent pair joined by company road,
 * and every tile company-owned (the v2 witness re-checks both facts). */
::route_tiles <- ["""
WORLD_SEED += ", ".join(str(tile) for tile in ROUTE)
WORLD_SEED += """
];
for (local i = 0; i + 1 < ::route_tiles.len(); i++) {
    stub_seed(::route_tiles[i], 0);
    stub_seed(::route_tiles[i + 1], 0);
    ::road_links[::route_tiles[i]][::route_tiles[i + 1]] <- true;
    ::road_links[::route_tiles[i + 1]][::route_tiles[i]] <- true;
}
/* The two truck-stop-typed stops with their pinned fronts and station ids. */
if (!::no_stops) {
    ::stops["""
WORLD_SEED += (
    f"{PICKUP}] <- {{front = {PICKUP_FRONT}, sid = 0}};\n"
    f"    ::stops[{DELIVERY}] <- {{front = {DELIVERY_FRONT}, sid = 2}};\n"
    "    ::station_types[0] <- 0x1;\n    ::station_types[2] <- 0x1;"
)
WORLD_SEED += """
}
/* One producer industry inside the pickup stop's radius box, one acceptor
 * inside the delivery bay's box (the F-3 unique-cargo discovery world).
 * The industry tiles are valid company road tiles themselves, so the
 * bounded radius scan reads them. */
::industries[7] <- {production = 100, accepts = false};
::industry_of_tile[45749] <- 7;
::industries[9] <- {production = 0, accepts = true};
::industry_of_tile[50865] <- 9;
stub_seed(45749, 0);
stub_seed(50865, 0);
/* The pinned provisional truck engine plus the compatible-universe echo. */
::engines[123] <- true;
::engines[124] <- true;
::engines[125] <- true;
::engines[126] <- true;
::engines[127] <- true;
"""

STUB = """
class GSController {
    function Sleep(t) {
        if (t != 1) throw "unexpected script sleep";
        ::ticks++;
        ::days++;
        if (::mover != null) ::mover();
    }
}
class GSCompany {
    static COMPANY_INVALID = -1;
    static CURRENT_QUARTER = 1;
    static function ResolveCompanyID(c) {
        return !::valid_company ? -1 : (c == 0 || c == ::second_company) ? c : -1;
    }
    static function GetBankBalance(_) { return ::funds; }
    static function GetQuarterlyIncome(_, _) { return ::finances.income; }
    static function GetQuarterlyCargoDelivered(_, _) { return ::finances.delivered; }
}
class GSCompanyMode {
    constructor(c) {
        if (c != 0 && c != ::second_company) throw "company";
        ::cur_company = c;
    }
    static function IsValid() { return ::mode_ok; }
}
class GSAccounting {
    constructor() { ::account++; }
    function GetCosts() {
        return (::account in ::tests) ? (::no_op ? 0 : ::quote_cost) : ::exec_cost;
    }
}
class GSTestMode { constructor() { ::tests[::account] <- true; } }
class GSMap {
    static function GetMapSizeX() { return ::dims[0]; }
    static function GetMapSizeY() { return ::dims[1]; }
    static function IsValidTile(t) { return t in ::tiles; }
    static function GetTileX(t) { return t % ::dims[0]; }
    static function GetTileY(t) { return t / ::dims[0]; }
}
class GSRoad {
    static ROADTYPE_ROAD = 0;
    static ROADVEHTYPE_TRUCK = 1;
    static function SetCurrentRoadType(type) { ::cur_roadtype = type; }
    static function GetCurrentRoadType() { return ::cur_roadtype; }
    static function IsRoadTypeAvailable(_) { return ::roadtype_ok; }
    static function AreRoadTilesConnected(a, b) {
        return (a in ::road_links) && (b in ::road_links[a]);
    }
    static function IsRoadTile(t) {
        return (t in ::tiles) && (::tiles[t].flags & 0x0080) != 0;
    }
    static function IsRoadStationTile(t) { return t in ::stops; }
    static function IsDriveThroughRoadStationTile(_) { return false; }
    static function GetRoadStationFrontTile(t) {
        return (t in ::stops) ? ::stops[t].front : -1;
    }
    static function IsRoadDepotTile(t) { return t in ::depots; }
    static function GetRoadDepotFrontTile(t) {
        return (t in ::depots) ? ::depots[t].front : -1;
    }
    static function GetRoadVehicleTypeForCargo(_) { return GSRoad.ROADVEHTYPE_TRUCK; }
}
class GSStation {
    static STATION_TRUCK_STOP = 0x1;
    static STATION_BUS_STOP = 0x2;
    static function GetStationID(t) { return (t in ::stops) ? ::stops[t].sid : -1; }
    static function IsValidStation(sid) { return sid >= 0 && (sid in ::station_types); }
    static function HasStationType(sid, type) {
        return (sid in ::station_types) && (::station_types[sid] & type) != 0;
    }
    /* The A1 world's measured truck-stop coverage radius (the discovery box). */
    static function GetCoverageRadius(_) { return 3; }
    static function GetCargoWaiting(_, _) { return ::waiting; }
}
class GSTile {
    static function GetOwner(t) { return (t in ::tiles) ? ::tiles[t].owner : -1; }
    static function GetCargoAcceptance(_, _, _, _, _) { return ::accept; }
}
class GSIndustry {
    static CAS_ACCEPTED = 0;
    static CAS_NOT_ACCEPTED = -1;
    static function IsValidIndustry(id) { return id >= 0 && (id in ::industries); }
    static function GetIndustryID(t) {
        return (t in ::industry_of_tile) ? ::industry_of_tile[t] : null;
    }
    static function GetLastMonthProduction(id, _) {
        return (id in ::industries) ? ::industries[id].production : 0;
    }
    static function IsCargoAccepted(id, _) {
        return (id in ::industries && ::industries[id].accepts)
            ? GSIndustry.CAS_ACCEPTED : GSIndustry.CAS_NOT_ACCEPTED;
    }
    static function GetCargoLastAcceptedDate(id, _) {
        return (id in ::industries) ? ::last_accepted : -1;
    }
}
class GSVehicle {
    static VT_ROAD = 1;
    static VS_RUNNING = 0;
    static VS_STOPPED = 1;
    static VS_IN_DEPOT = 2;
    static VS_AT_STATION = 3;
    static VS_BROKEN = 4;
    static VS_CRASHED = 5;
    static function BuildVehicle(tile, engine) {
        if (!(tile in ::depots) || !(engine in ::engines)) return -1;
        if (::account in ::tests) { ::test_calls++; return 0; }
        ::real_calls++;
        ::funds -= ::exec_cost;
        local id = ::next_vehicle;
        ::next_vehicle++;
        ::vehicles[id] <- {owner = 0, engine = engine, location = tile,
            cargo = 1, capacity = ::engine_capacity, load = 0, state = 2,
            in_depot = true, speed = 0};
        ::orders[id] <- [];
        ::cur_vehicle <- id;
        return id;
    }
    static function IsValidVehicle(id) { return id >= 0 && (id in ::vehicles); }
    static function IsPrimaryVehicle(_) { return true; }
    static function GetOwner(id) { return ::vehicles[id].owner; }
    static function GetEngineType(id) { return ::vehicles[id].engine; }
    static function GetLocation(id) { return ::vehicles[id].location; }
    static function GetCapacity(id, _) { return ::vehicles[id].capacity; }
    static function IsInDepot(id) { return ::vehicles[id].in_depot; }
    static function GetCurrentSpeed(id) { return ::vehicles[id].speed; }
    static function GetState(id) { return ::vehicles[id].state; }
    static function GetCargoLoad(id, _) { return ::vehicles[id].load; }
    static function StartStopVehicle(id) {
        if (!(id in ::vehicles) || ::reject_start) return false;
        local v = ::vehicles[id];
        if (v.state != VS_RUNNING && v.state != VS_AT_STATION) {
            v.state = VS_RUNNING;
            v.speed = 5;
            v.in_depot = false;
        } else {
            v.state = VS_STOPPED;
            v.speed = 0;
        }
        return true;
    }
}
class GSVehicleList {
    items = null;
    index = 0;
    constructor() {
        this.items = [];
        foreach (id, _ in ::vehicles) this.items.append(id);
    }
    function Begin() {
        if (this.items.len() == 0) { this.index = 0; return null; }
        this.index = 0;
        return this.items[0];
    }
    function IsEnd() { return this.index >= this.items.len(); }
    function Next() {
        this.index++;
        if (this.index >= this.items.len()) return null;
        return this.items[this.index];
    }
}
class GSEngineList {
    items = null;
    index = 0;
    constructor(_) {
        this.items = [];
        foreach (id, _ in ::engines) this.items.append(id);
    }
    function Begin() {
        if (this.items.len() == 0) { this.index = 0; return null; }
        this.index = 0;
        return this.items[0];
    }
    function IsEnd() { return this.index >= this.items.len(); }
    function Next() {
        this.index++;
        if (this.index >= this.items.len()) return null;
        return this.items[this.index];
    }
}
class GSEngine {
    static function IsBuildable(e) { return ::engine_ok && (e in ::engines); }
    static function IsValidEngine(e) { return e in ::engines; }
    static function GetVehicleType(_) { return GSVehicle.VT_ROAD; }
    static function IsArticulated(_) { return false; }
    static function CanRunOnRoad(_, _) { return true; }
    static function HasPowerOnRoad(_, _) { return true; }
    static function GetCargoType(_) { return 1; }
    static function CanRefitCargo(_, _) { return true; }
    static function GetCapacity(_) { return ::engine_capacity; }
    static function GetPrice(_) { return ::engine_price; }
    static function GetMaxSpeed(_) { return 48; }
}
class GSCargo {
    static function IsValidCargo(cargo) { return cargo == 1; }
}
class GSOrder {
    /* N2: the real 15.x flag values (OF_FULL_LOAD is documented forbidden). */
    static OF_NONE = 0;
    static OF_FULL_LOAD = 64;
    static function AreOrderFlagsValid(dest, flags) {
        /* N3: the two-argument 15.x destination form. */
        ::n3_calls.append([dest, flags]);
        return (flags == GSOrder.OF_NONE || flags == 128) && (dest in ::stops);
    }
    static function AppendOrder(id, dest, flags) {
        /* N1 (15.3, E92): the append takes the stop TILE and stores the
         * resolved station (MakeGoToStation of GetStationIndex(dest))
         * alongside; the readback returns the canonical stop tile by
         * resolution — never the StationID. */
        ::append_calls.append([dest, flags]);
        if (!(id in ::vehicles) || !(dest in ::stops)) return false;
        ::orders[id].append({d = dest, sid = ::stops[dest].sid, f = flags});
        return true;
    }
    static function GetOrderCount(id) { return (id in ::orders) ? ::orders[id].len() : 0; }
    static function GetOrderDestination(id, i) { return ::orders[id][i].d; }
    static function GetOrderFlags(id, i) { return ::orders[id][i].f; }
    static function IsGotoStationOrder(id, i) {
        return ::orders[id][i].sid in ::station_types;
    }
}
class GSCargoMonitor {
    static function GetIndustryPickupAmount(_, cargo, industry, keep) {
        local value = (industry in ::monitors.pickup) ? ::monitors.pickup[industry] : 0;
        if (!keep) ::monitors.pickup[industry] <- 0;
        return value;
    }
    static function GetIndustryDeliveryAmount(_, cargo, industry, keep) {
        local value = (industry in ::monitors.delivery) ? ::monitors.delivery[industry] : 0;
        if (!keep) ::monitors.delivery[industry] <- 0;
        return value;
    }
}
class GSGame {
    static function IsPaused() { return ::paused; }
}
class GSDate {
    static function GetCurrentDate() { return ::days; }
}
function last_reply_json() {
    local r = ::replies[::replies.len() - 1];
    local out = "{";
    local first = true;
    foreach (k, v in r) {
        if (typeof k != "string") continue;
        if (!first) out = out + ",";
        first = false;
        out = out + "\\"" + k + "\\":";
        if (v == null) out = out + "null";
        else if (typeof v == "bool") out = out + (v ? "true" : "false");
        else if (typeof v == "string") out = out + "\\"" + v + "\\"";
        else if (typeof v == "array") {
            out = out + "[";
            local af = true;
            foreach (item in v) {
                if (!af) out = out + ",";
                af = false;
                out = out + item;
            }
            out = out + "]";
        }
        else out = out + v;
    }
    return out + "}";
}
"""


def build_vm(**knobs: int | bool) -> SQVM:
    """Fresh VM with the API fixture, the controlled freight world and the package."""
    vm = SQVM()
    vm.execute(API.read_text())
    vm.execute(WORLD)
    if knobs:
        assignments = []
        for name, value in knobs.items():
            literal = str(value).lower() if isinstance(value, bool) else str(value)
            assignments.append(f"::{name} = {literal};")
        vm.execute("\n".join(assignments))
    vm.execute(WORLD_SEED)
    vm.execute(STUB)
    vm.execute((PACKAGE / "main.nut").read_text())
    vm.execute("::bridge <- D5FreightV2Proof();")
    return vm


def vm_root(vm: SQVM) -> dict[str, Any]:
    return vm.get_roottable()


def drive(vm: SQVM, request: FreightRequestV2) -> FreightReadbackV2:
    """Dispatch one request over the wire and parse the reply into Python."""
    execute_request(vm, request)
    vm.execute("::sniffer.last = last_reply_json();")
    raw = vm_root(vm)["sniffer"]["last"]
    assert len(raw.encode()) <= MAX_FREIGHT_RESPONSE_BYTES_V2, (
        f"response for {request.request_id} exceeds {MAX_FREIGHT_RESPONSE_BYTES_V2} bytes"
    )
    return FreightReadbackV2.parse_for(request, raw.encode())


def execute_request(vm: SQVM, request: FreightRequestV2) -> dict:
    """Run one Handle dispatch; the reply payload is returned as a table."""
    replies = vm_root(vm)["replies"]
    before = len(replies)
    vm.execute("::bridge.Handle(" + request.to_bytes().decode() + ");")
    replies = vm_root(vm)["replies"]
    if len(replies) == before:
        raise AssertionError(f"package dropped request {request.request_id}: no reply")
    return replies[before]


def expect_drop(vm: SQVM, payload: dict) -> None:
    """A malformed request must be dropped silently: no reply, no state."""
    before = len(vm_root(vm)["replies"])
    vm.execute("::bridge.Handle(" + _squirrel_table(payload) + ");")
    assert len(vm_root(vm)["replies"]) == before


def _squirrel_table(payload: dict) -> str:
    """The handler-facing compact JSON of a request-shaped mapping."""
    pairs = []
    for key, value in payload.items():
        if isinstance(value, bool):
            literal = "true" if value else "false"
        elif value is None:
            literal = "null"
        elif isinstance(value, str):
            literal = '"' + value + '"'
        elif isinstance(value, (list, tuple)):
            literal = "[" + ",".join(str(item) for item in value) + "]"
        else:
            literal = str(value)
        pairs.append('"' + key + '" : ' + literal)
    return "{" + ",".join(pairs) + "}"


def shape_world(
    vm: SQVM, label: str, vehicle: int, *, zero: bool = False
) -> None:
    """Drive the stub world between exchanges (real running would do this).

    The loaded cycles arm the pickup monitor for the cycle's departure
    snapshot, put the truck at the pickup stop, and move it out on the
    first window Sleep with a one-shot ::mover (a real vehicle departs the
    stop on its own); the deliver exchange completes the monitor arithmetic
    with the delivery residue and walks the stub finances by the fixed
    per-cycle income. The typed zero cycles put the truck at the pickup
    stop first and move it to the on-route empty-departure tile on the
    first Sleep, leaving the monitors untouched (zero residue).
    """
    prefix = label.partition("-")[0]
    one = int(label.partition("-")[2]) if prefix in ("load", "transit", "deliver") else 0
    if prefix == "load":
        if zero:
            vm.execute(
                f"::vehicles[{vehicle}].location = {PICKUP};\n"
                "::mover <- function() {"
                f" ::vehicles[{vehicle}].location = {ZERO_DEPARTURE_TILE};"
                " ::mover = null;"
                "};"
            )
            return
        vm.execute(
            f"::vehicles[{vehicle}].load = {LOADS[one]};\n"
            f"::vehicles[{vehicle}].location = {PICKUP};\n"
            f"::monitors.pickup[{PICKUP_INDUSTRY}] <- {LOADS[one]};\n"
            "::mover <- function() {"
            f" ::vehicles[{vehicle}].location = {PICKUP_FRONT};"
            " ::mover = null;"
            "};"
        )
    elif prefix == "transit":
        vm.execute(f"::vehicles[{vehicle}].location = {DELIVERY};")
    elif prefix == "deliver":
        if zero:
            return
        # The F-6 ledger walk of record: the funds and the quarter income
        # move by the fixed per-cycle render; the stub delivered counter
        # adds its fixed per-row render (the finance gate reads deltas).
        # The pickup residue was set at the load exchange and still reads
        # the departure snapshot; the delivery residue arms here.
        vm.execute(
            f"::vehicles[{vehicle}].load = 0;\n"
            f"::monitors.delivery[{DELIVERY_INDUSTRY}] <- {LOADS[one]};\n"
            f"::funds += {INCOME_PER_CYCLE};\n"
            f"::finances.income += {INCOME_PER_CYCLE};\n"
            "::finances.delivered += 20;"
        )
    elif prefix == "finance":
        vm.execute("::last_accepted = 900;")


def run_attempt(
    vm: SQVM, *, plan=None, zero: bool = False
) -> tuple[list[tuple[FreightRequestV2, FreightReadbackV2]], Any]:
    """The exact thirty planned exchanges in order (the production builder)."""
    plan = plan or work.freight_plan_v2()
    state: dict[str, Any] = dict(site=None, engine=None, vehicle=-1)
    exchanges: list[tuple[FreightRequestV2, FreightReadbackV2]] = []
    for entry in work.freight_schedule():
        label = entry["exchange"]
        request = work._freight_exchange_request(entry, PRELAUNCH, plan, state)
        if state["vehicle"] >= 0:
            shape_world(vm, label, state["vehicle"], zero=zero)
        readback = drive(vm, request)
        probes = freight_phase_outcome_v2(
            exchanges + [(request, readback)], prelaunch_digest=PRELAUNCH, plan=plan
        )
        assert probes["failed"] is None, (label, probes["failed"])
        exchanges.append((request, readback))
        if entry["op"] == "site":
            state["site"] = work.admit_freight_site_v2(
                readback, prelaunch_digest=PRELAUNCH, plan=plan
            )
        elif entry["op"] == "engine":
            state["engine"] = work.admit_freight_engine_v2(
                readback, prelaunch_digest=PRELAUNCH, plan=plan, site=state["site"]
            )
        elif entry["op"] == "purchase":
            state["vehicle"] = readback.vehicle
    return exchanges, plan


def run_cycle(vm: SQVM, *, plan=None, zero: bool = False):
    """Alias of record: the complete attempt through the shipped package."""
    return run_attempt(vm, plan=plan, zero=zero)


def run_prefix_until(
    vm: SQVM, label: str, *, zero: bool = False
) -> tuple[list, Any]:
    """Drive the staged schedule prefix through `label` inclusive."""
    plan = work.freight_plan_v2()
    state: dict[str, Any] = dict(site=None, engine=None, vehicle=-1)
    exchanges: list[tuple[FreightRequestV2, FreightReadbackV2]] = []
    for entry in work.freight_schedule():
        request = work._freight_exchange_request(entry, PRELAUNCH, plan, state)
        if state["vehicle"] >= 0:
            shape_world(vm, entry["exchange"], state["vehicle"], zero=zero)
        readback = drive(vm, request)
        exchanges.append((request, readback))
        if entry["op"] == "site":
            state["site"] = work.admit_freight_site_v2(
                readback, prelaunch_digest=PRELAUNCH, plan=plan
            )
        elif entry["op"] == "engine":
            state["engine"] = work.admit_freight_engine_v2(
                readback, prelaunch_digest=PRELAUNCH, plan=plan, site=state["site"]
            )
        elif entry["op"] == "purchase":
            state["vehicle"] = readback.vehicle
        if entry["exchange"] == label:
            break
    return exchanges, plan


def run_refusals(
    vm: SQVM, labels: tuple[str, ...], *, plan=None
) -> tuple[list, Any]:
    """Drive the named stage prefix; return the raw exchange evidence."""
    plan = plan or work.freight_plan_v2()
    state: dict[str, Any] = dict(site=None, engine=None, vehicle=-1)
    exchanges: list[tuple[FreightRequestV2, FreightReadbackV2]] = []
    schedule = work.freight_schedule()
    for label in labels:
        index = list(cfv.FREIGHT_EXCHANGE_IDS_V2).index(label)
        entry = schedule[index]
        request = work._freight_exchange_request(entry, PRELAUNCH, plan, state)
        readback = drive(vm, request)
        exchanges.append((request, readback))
    return exchanges, plan


def _state_of(exchanges) -> dict:
    state: dict[str, Any] = dict(site=None, engine=None, vehicle=-1)
    plan = work.freight_plan_v2()
    for request, readback in exchanges:
        if request.op == "site":
            state["site"] = work.admit_freight_site_v2(
                readback, prelaunch_digest=PRELAUNCH, plan=plan
            )
        elif request.op == "engine":
            state["engine"] = work.admit_freight_engine_v2(
                readback,
                prelaunch_digest=PRELAUNCH,
                plan=plan,
                site=state["site"],
            )
        elif request.op == "purchase":
            state["vehicle"] = readback.vehicle
    return state


def _entry_of(label: str) -> dict:
    return next(e for e in work.freight_schedule() if e["exchange"] == label)


def probe_request(expression_ids: str, position: int, **echo: int) -> FreightRequestV2:
    """A valid-shaped request outside the staged schedule (cap accounting)."""
    payload: dict[str, Any] = {
        "protocol": 8,
        "op": "vread",
        "request_id": f"probe-{position:02d}",
        "plan": PRELAUNCH,
        "company": 0,
        "max_cost": 5000,
        "pickup": PICKUP,
        "delivery": DELIVERY,
        "depot": DEPOT_TILE,
        "route_digest": PLAN.route_digest,
        "witness_digest": None,
        "engine": 123,
        "vehicle": 1,
        "expected_cost": 0,
        "order_index": -1,
        "watch_ticks": -1,
        "watch_days": -1,
    }
    payload.update(echo)
    payload["request_id"] = expression_ids
    return FreightRequestV2.model_validate(payload)


def _request_payload(request: FreightRequestV2) -> dict:
    import json

    return json.loads(request.to_bytes())


def _site_base_payload() -> dict:
    return {
        "protocol": 8,
        "op": "site",
        "request_id": "site-00",
        "plan": PRELAUNCH,
        "company": 0,
        "max_cost": 5000,
        "pickup": PICKUP,
        "delivery": DELIVERY,
        "depot": DEPOT_TILE,
        "route_digest": PLAN.route_digest,
        "route": list(ROUTE),
        "witness_digest": PLAN.witness_digest,
        "engine": -1,
        "vehicle": -1,
        "expected_cost": 0,
        "order_index": -1,
        "watch_ticks": -1,
        "watch_days": -1,
    }


MALFORMED_SHAPES = (
    {"protocol": 4},
    {"protocol": 9},
    {"op": "mystery"},
    {"request_id": "X" * 33},
    {"request_id": "BAD-ID"},
    {"request_id": ""},
    {"plan": "a" * 63},
    {"route_digest": "a" * 63},
    {"company": 15},
    {"max_cost": -1},
    {"expected_cost": -1},
    {"order_index": 2},
    {"watch_days": 31},
    {"engine": 5},
    {"vehicle": 1},
    {"route": None},
)


# --- full happy attempt ----------------------------------------------------------


def test_full_attempt_completes_and_verifies_attempt_end_to_end():
    """All thirty planned exchanges answer READY..PHASE_STOPPED in order; the
    attempt verifies with six completed cycles and the F-6 funds equation."""
    vm = build_vm()
    exchanges, plan = run_attempt(vm)
    assert [request.request_id for request, _ in exchanges] == list(
        cfv.FREIGHT_EXCHANGE_IDS_V2
    )
    for request, readback in exchanges:
        assert readback.plan == PRELAUNCH and readback.company == 0
        assert len(request.to_bytes()) <= MAX_FREIGHT_REQUEST_BYTES_V2
    site = exchanges[0][1]
    assert site.status == "READY" and (site.truck0, site.sid0) == (True, 0)
    assert (site.truck1, site.sid1) == (True, 2) and site.accept == 8
    assert site.pairs_ok == site.pair_total == POSITION_PROGRESS  # 28 ordered pairs
    assert site.prod == 100 and site.wait == 5 and site.paused is False
    assert site.vehicles == 0 and site.depot_ok is True and site.depot_edge is True
    assert site.road_ready is True and (site.owner, site.cost) == (0, 0)
    assert site.pickup_industry == PICKUP_INDUSTRY
    assert site.delivery_industry == DELIVERY_INDUSTRY
    assert site.pickup_industry_count == site.delivery_industry_count == 1
    assert (site.pickup_radius, site.delivery_radius) == (3, 3)
    engine = exchanges[1][1]
    assert engine.status == "READY" and engine.engine == 123
    assert engine.capacity == ENGINE_CAPACITY and engine.cargo == 1
    assert engine.price == ENGINE_QUOTE and engine.max_speed == ENGINE_MAX_SPEED
    # The bounded compatible-universe echo: insertion-sorted descending.
    assert isinstance(engine.fleet, tuple)  # the replay lift of record
    assert engine.fleet == (127, 126, 125, 124, 123)
    assert engine.fleet_count == 5 and 123 in engine.fleet
    purchase = exchanges[2][1]
    assert purchase.status == "BUILT" and purchase.vehicle == 1
    assert purchase.cost == ENGINE_QUOTE and purchase.funds == FUNDS - ENGINE_QUOTE
    order0, order1 = exchanges[4][1], exchanges[5][1]
    assert (order0.dest, order0.flags, order0.goto) == (PICKUP, cfv.OF_NONE_V2, True)
    assert (order1.dest, order1.flags, order1.goto) == (
        DELIVERY, cfv.OF_NO_LOAD_V2, True,
    )
    inventory = exchanges[6][1]
    assert (inventory.order_len, inventory.dest0, inventory.dest1) == (
        2, PICKUP, DELIVERY,
    )
    assert (inventory.flags0, inventory.flags1) == (cfv.OF_NONE_V2, cfv.OF_NO_LOAD_V2)
    monitors = exchanges[7][1]
    assert monitors.status == "ARMED"
    assert monitors.pickup_amount == 0 and monitors.delivery_amount == 0
    started = exchanges[8][1]
    assert started.state == "RUNNING" and started.speed == 5
    # E53: the start reply carries the economy day of record the windows'
    # aggregate ledger is measured against.
    assert started.day is not None and started.day > 0
    vread_01 = exchanges[9][1]
    assert vread_01.state == "RUNNING" and vread_01.in_depot is False
    loaded = exchanges[10][1]
    assert loaded.load == ENGINE_CAPACITY == loaded.capacity and loaded.wait == 5
    # E53: the departure snapshot binds its matching monitor evidence.
    assert loaded.pickup_amount == loaded.load
    arrived = exchanges[11][1]
    assert (arrived.position, arrived.progress) == (DELIVERY, POSITION_PROGRESS)
    delivered = exchanges[12][1]
    assert delivered.load == 0 and delivered.pickup_amount == ENGINE_CAPACITY
    assert delivered.delivery_amount == ENGINE_CAPACITY and delivered.recheck is True
    # E53: the accepted delivery echoes the very bay tile it was typed at.
    assert delivered.position == DELIVERY
    finance = exchanges[28][1]
    assert finance.income == INCOME_TOTAL and finance.delivered == 120
    assert finance.last_accepted == 900
    finished = exchanges[29][1]
    assert finished.stop_issued is True and finished.state == "STOPPED"
    assert finished.speed == 0 and finished.funds == FINAL_FUNDS
    probes = freight_phase_outcome_v2(
        exchanges, prelaunch_digest=PRELAUNCH, plan=plan
    )
    assert probes["verification"] == "PHASE_COMPLETE"
    assert probes["completed_cycles"] == 6
    attempt = verify_freight_attempt_v2(
        exchanges, prelaunch_digest=PRELAUNCH, plan=plan
    )
    assert attempt["verification"] == "FREIGHT_ATTEMPT_VERIFIED"
    assert attempt["engine"] == 123 and attempt["vehicle"] == 1
    assert attempt["completed_cycles"] == 6
    assert attempt["site_industry"] == DELIVERY_INDUSTRY
    ledger = attempt["funds_ledger"]
    assert ledger[2]["delta"] == -ENGINE_QUOTE  # the purchase funds movement
    assert attempt["funds"] == dict(
        schema="company-freight2-funds-equation-v1",
        purchase_quote=ENGINE_QUOTE,
        income_total=INCOME_TOTAL,
        running_cost_total=0,
        initial_funds=FUNDS,
        final_funds=FINAL_FUNDS,
        residual=0,
        verification="FUNDS_EQUATION_VERIFIED",
    )


def test_attempt_plan_industries_stay_unpinned():
    """The industry ids are natively discovered facts, never plan pins."""
    assert PLAN.pickup_industry == -1 and PLAN.delivery_industry == -1


def test_every_exchange_reply_keeps_the_correlation_stride():
    """Success frames echo the request stride they verify (correlation)."""
    vm = build_vm()
    exchanges, _ = run_attempt(vm)
    for request, readback in exchanges:
        for field in ("protocol", "op", "request_id", "plan", "company", "max_cost"):
            assert getattr(readback, field) == getattr(request, field)
        for field in ("pickup", "delivery", "depot"):
            assert getattr(readback, field) == getattr(request, field)
        assert readback.route_digest == request.route_digest == PLAN.route_digest
        if request.op == "site":
            assert readback.witness_digest == PLAN.witness_digest
        else:
            assert readback.witness_digest is None
            assert request.route is None
        if request.engine >= 0:
            assert readback.engine == request.engine
        if request.op == "purchase":
            assert readback.vehicle == 1  # the built id is the purchase's answer
        elif request.op not in ("site", "engine"):
            assert readback.vehicle == request.vehicle
        if request.expected_cost > 0:
            assert readback.expected_cost == request.expected_cost
        if request.op in ("load-watch", "transit-watch", "deliver-watch"):
            assert readback.watch_ticks == request.watch_ticks
            # E53: all three watch windows lease the per-cycle day cap.
            assert readback.watch_days == request.watch_days == (
                cfv.FREIGHT_CYCLE_DAY_CAP_V2
            )


def test_purchase_funds_reconcile_exactly_once():
    """The funds ledger moves only on the purchase exchange, by the quote."""
    vm = build_vm()
    exchanges, plan = run_attempt(vm)
    probes = freight_phase_outcome_v2(exchanges, prelaunch_digest=PRELAUNCH, plan=plan)
    assert probes["verification"] == "PHASE_COMPLETE"
    attempt = verify_freight_attempt_v2(exchanges, prelaunch_digest=PRELAUNCH, plan=plan)
    deltas = [row["delta"] for row in attempt["funds_ledger"]]
    assert deltas.count(-ENGINE_QUOTE) == 1
    assert all(
        delta in (None, 0, INCOME_PER_CYCLE, -ENGINE_QUOTE) for delta in deltas
    )


# --- the typed zero-departure attempt --------------------------------------------


def test_zero_attempt_completes_as_typed_zero_cycle_events():
    """Six on-route empty departures read as ZERO_DEPARTED windows; the
    attempt stays honest: zero cycles completed, zero revenue, no income."""
    vm = build_vm()
    exchanges, plan = run_attempt(vm, zero=True)
    load_rows = [
        exchange
        for exchange in exchanges
        if exchange[0].op == "load-watch"
    ]
    assert len(load_rows) == 6
    for request, readback in load_rows:
        assert readback.status == "ZERO_DEPARTED"
        assert readback.load == 0 and readback.paused is False
        # E53: the typed event proves the empty departure via zero pickup
        # residue beside the departure sample itself.
        assert readback.pickup_amount == 0
        assert readback.tick is not None and readback.day is not None
        assert readback.income == 0 and readback.funds == FUNDS - ENGINE_QUOTE
    arrived = exchanges[11][1]
    assert (arrived.position, arrived.progress, arrived.load) == (
        DELIVERY, POSITION_PROGRESS, 0,
    )
    delivered = exchanges[12][1]
    assert delivered.load == 0
    assert delivered.pickup_amount == 0 and delivered.delivery_amount == 0
    assert delivered.recheck is True
    assert delivered.position == DELIVERY
    finance = exchanges[28][1]
    assert finance.income == 0 and finance.delivered == 0
    finished = exchanges[29][1]
    assert finished.stop_issued is True
    assert finished.funds == FUNDS - ENGINE_QUOTE
    probes = freight_phase_outcome_v2(
        exchanges, prelaunch_digest=PRELAUNCH, plan=plan
    )
    assert probes["verification"] == "PHASE_COMPLETE"
    assert probes["completed_cycles"] == 0
    assert probes["zero_departed_cycles"] == 6
    attempt = verify_freight_attempt_v2(
        exchanges, prelaunch_digest=PRELAUNCH, plan=plan
    )
    assert attempt["verification"] == "FREIGHT_ZERO_DEPARTED_VERIFIED"
    assert attempt["completed_cycles"] == 0
    assert attempt["zero_cycle_receipts"] == 6 and attempt["zero_watch_events"] == 6
    report = attempt["funds"]
    assert report["income_total"] == 0 and report["residual"] == 0
    assert report["final_funds"] == FUNDS - ENGINE_QUOTE


def test_mislabeled_zero_event_is_refused_and_preserved():
    """A ZERO_DEPARTED window claiming cargo is a typed event defect: the
    attempt halts with the zero evidence preserved, never a success."""
    vm = build_vm()
    exchanges, plan = run_prefix_until(vm, "load-00", zero=True)
    assert exchanges[-1][1].status == "ZERO_DEPARTED"
    request, readback = exchanges[-1]
    tampered = readback.model_copy(update={"load": 3})
    probes = freight_phase_outcome_v2(
        exchanges[:-1] + [(request, tampered)], prelaunch_digest=PRELAUNCH, plan=plan
    )
    assert probes["verification"] == "PARTIAL_EXECUTION_EVIDENCE"
    assert probes["failed"]["label"] == "load-00"
    assert probes["failed"]["world_state"] == "ZERO_DEPARTED_EVIDENCE_PRESERVED"
    assert probes["failed"]["status"] == "ZERO_DEPARTED"
    assert probes["zero_departed_cycles"] == 0


def test_python_level_zero_departure_verifier_hangs_zero_load_only():
    """The typed receipt refuses a drifted echo or a claimed cargo (F-11)."""
    from app.simulation.openttd.corridor_freight_v2 import (
        verify_freight_zero_departed_v2,
    )

    vm = build_vm()
    exchanges, _ = run_prefix_until(vm, "load-00", zero=True)
    readback = exchanges[-1][1]
    assert readback.status == "ZERO_DEPARTED" and readback.load == 0
    verify_freight_zero_departed_v2(readback, vehicle=1)
    with pytest.raises(ValueError, match="zero observed load"):
        verify_freight_zero_departed_v2(
            readback.model_copy(update={"load": 3}), vehicle=1
        )
    with pytest.raises(ValueError, match="zero-departure echo mismatch"):
        verify_freight_zero_departed_v2(
            readback.model_copy(update={"vehicle": 999}), vehicle=1
        )


# --- dispatcher discipline -------------------------------------------------------


def test_malformed_requests_are_dropped_without_any_reply():
    """Every malformed shape is silently dropped by the guarded entry point."""
    vm = build_vm()
    for shape in MALFORMED_SHAPES:
        expect_drop(vm, _site_base_payload() | shape)
    assert len(vm_root(vm)["replies"]) == 0


def test_false_witness_latches_but_the_replay_refuses_it():
    """A false (valid-shaped) witness digest answers, never dropped — the
    wire layer cannot verify the construction evidence; Python owns the
    pinned witness, and the replay verifier refuses the drifted site
    request before any byte reaches the Admin session."""
    vm = build_vm()
    request = work._freight_exchange_request(
        work.freight_schedule()[0],
        PRELAUNCH,
        work.freight_plan_v2(),
        dict(site=None, engine=None, vehicle=-1),
    )
    false_witness = request.model_copy(
        update={"witness_digest": "b" * 64}, deep=True
    )
    readback = drive(vm, false_witness)
    assert readback.status == "READY"
    assert readback.witness_digest == "b" * 64
    with pytest.raises(ValueError, match="witness digest drifted"):
        work.verify_request_against_plan(
            false_witness, plan=work.freight_plan_v2(), seal=PRELAUNCH
        )
    # The same shape with the pinned witness passes the trust anchor.
    work.verify_request_against_plan(
        request, plan=work.freight_plan_v2(), seal=PRELAUNCH
    )


def test_request_without_its_witness_key_is_dropped():
    """The wire serializes the witness digest's absence as null on every op:
    a request without the key at all is not a request the contract built."""
    vm = build_vm()
    payload = {k: v for k, v in _site_base_payload().items() if k != "witness_digest"}
    expect_drop(vm, payload)


def test_non_site_request_with_a_route_or_witness_stray_is_dropped():
    """Only the site request may carry a route; only site carries a witness."""
    vm = build_vm()
    base = {
        "protocol": 8,
        "op": "vread",
        "request_id": "probe-71",
        "plan": PRELAUNCH,
        "company": 0,
        "max_cost": 5000,
        "pickup": PICKUP,
        "delivery": DELIVERY,
        "depot": DEPOT_TILE,
        "route_digest": PLAN.route_digest,
        "witness_digest": None,
        "engine": 123,
        "vehicle": 1,
        "expected_cost": 0,
        "order_index": -1,
        "watch_ticks": -1,
        "watch_days": -1,
    }
    expect_drop(vm, base | {"route": list(ROUTE)})
    expect_drop(vm, base | {"witness_digest": PRELAUNCH})
    assert len(vm_root(vm)["replies"]) == 0


def test_site_offworld_pickup_tile_reaches_unsupported_native_fact():
    """A site request naming an off-world stop tile is answered, not dropped:
    the latched observation refuses on the native world, never silently."""
    vm = build_vm()
    payload = dict(_site_base_payload(), pickup=1)
    before = len(vm_root(vm)["replies"])
    vm.execute("::bridge.Handle(" + _squirrel_table(payload) + ");")
    replies = vm_root(vm)["replies"]
    assert len(replies) == before + 1
    assert replies[before]["status"] == "UNSUPPORTED_NATIVE_FACT"


def test_plan_digest_drift_is_refused_not_ignored():
    """A different plan digest after the latched first exchange is refused."""
    vm = build_vm()
    plan = work.freight_plan_v2()
    state = dict(site=None, engine=None, vehicle=-1)
    site_request = work._freight_exchange_request(
        work.freight_schedule()[0], PRELAUNCH, plan, state
    )
    assert drive(vm, site_request).status == "READY"
    engine_request = work._freight_exchange_request(
        work.freight_schedule()[1], OTHER_PLAN, plan, state
    )
    assert drive(vm, engine_request).status == "OUT_OF_ORDER"


def test_order_gate_and_prefix_preserving_halts():
    """The stage gate, one halted refusal, and the permanent OUT_OF_ORDER."""
    vm = build_vm()
    plan = work.freight_plan_v2()
    entry = work.freight_schedule()[1]  # engine-00 before its site stage
    request = work._freight_exchange_request(
        entry, PRELAUNCH, plan, dict(site=None, engine=None, vehicle=-1)
    )
    readback = drive(vm, request)
    assert readback.status == "OUT_OF_ORDER"
    # The halted schedule never recovers: even the planned next exchange
    # refusal is prefix-preserving, and no op is reordered or retried.
    halted = work._freight_exchange_request(
        work.freight_schedule()[0],
        PRELAUNCH,
        plan,
        dict(site=None, engine=None, vehicle=-1),
    )
    assert drive(vm, halted).status == "OUT_OF_ORDER"
    later = work._freight_exchange_request(
        work.freight_schedule()[2],
        PRELAUNCH,
        plan,
        dict(
            site=None,
            engine=SimpleNamespace(engine=123, quote=ENGINE_QUOTE),
            vehicle=-1,
        ),
    )
    assert drive(vm, later).status == "OUT_OF_ORDER"


def test_duplicate_request_ids_are_dropped_silently():
    """The one-shot accounting never answers a duplicated id twice."""
    vm = build_vm()
    request = work._freight_exchange_request(
        work.freight_schedule()[0],
        PRELAUNCH,
        work.freight_plan_v2(),
        dict(site=None, engine=None, vehicle=-1),
    )
    assert drive(vm, request).status == "READY"
    expect_drop(vm, _request_payload(request))


def test_dispatcher_budget_refuses_the_request_after_the_cap():
    """32 unique valid-shaped requests fill the budget; the 33rd is dropped."""
    vm = build_vm()
    reply = drive(vm, probe_request("probe-00", 0))
    assert reply.status == "OUT_OF_ORDER"
    for position in range(1, 32):
        probe = probe_request(f"probe-{position:02d}", position)
        assert drive(vm, probe).status == "OUT_OF_ORDER"
    vm.execute("::sniffer.requests <- ::bridge.requests;")
    assert vm_root(vm)["sniffer"]["requests"] == work.FREIGHT_STAGED_REQUESTS_BUDGET == 32
    execute_drop(vm, probe_request("probe-999", 999))


def execute_drop(vm: SQVM, request: FreightRequestV2) -> None:
    before = len(vm_root(vm)["replies"])
    vm.execute("::bridge.Handle(" + request.to_bytes().decode() + ");")
    assert len(vm_root(vm)["replies"]) == before


# --- admission refusals (fail-closed, before any mutation) -----------------------


def test_paused_world_refuses_site_admission_and_halts():
    vm = build_vm(paused=True)
    exchanges, plan = run_refusals(vm, ("site-00",))
    assert exchanges[0][1].status == "PAUSED"
    probes = freight_phase_outcome_v2(exchanges, prelaunch_digest=PRELAUNCH, plan=plan)
    assert probes["failed"]["world_state"] == "HALTED_BEFORE_MUTATION"


def test_missing_stop_station_type_refuses_site_admission():
    vm = build_vm(no_stops=True)
    exchanges, plan = run_refusals(vm, ("site-00",))
    assert exchanges[0][1].status == "INVALID_SITE"


def test_fragmented_route_refuses_site_admission():
    vm = build_vm()
    vm.execute(f"break_link({ROUTE[2]}, {ROUTE[3]});")
    exchanges, plan = run_refusals(vm, ("site-00",))
    assert exchanges[0][1].status == "INVALID_SITE"


def test_broken_directed_depot_edge_refuses_site_admission():
    """F-12: one missing directed edge refuses the site before anything."""
    vm = build_vm()
    vm.execute(f"break_link({DEPOT_FRONT}, {DEPOT_TILE});")
    exchanges, plan = run_refusals(vm, ("site-00",))
    assert exchanges[0][1].status == "INVALID_SITE"


def test_acceptance_below_census_refuses_site_admission():
    vm = build_vm()
    vm.execute("::accept = 7;")
    exchanges, plan = run_refusals(vm, ("site-00",))
    assert exchanges[0][1].status == "INVALID_SITE"


def test_second_producer_discovery_refuses_site_admission():
    """F-3: a second cargo producer inside the pickup box refuses admission."""
    vm = build_vm()
    vm.execute(
        "stub_seed(45750, 0);\n"
        "::industry_of_tile[45750] <- 8;\n"
        "::industries[8] <- {production = 100, accepts = false};"
    )
    exchanges, plan = run_refusals(vm, ("site-00",))
    readback = exchanges[0][1]
    assert readback.status == "INVALID_SITE"
    assert readback.pickup_industry is None and readback.vehicles is None


def test_nonzero_fleet_refuses_site_as_a_typed_refusal():
    """A nonzero vehicle fleet is INVALID_SITE before any observation field
    attaches, so the refusal keeps the contract's refusal shape."""
    vm = build_vm()
    vm.execute(
        "::vehicles[7] <- {owner = 0, engine = 123, location = 45487, cargo = 1,"
        " capacity = 20, load = 0, state = 2, in_depot = true, speed = 0};"
        " ::orders[7] <- [];"
    )
    exchanges, plan = run_refusals(vm, ("site-00",))
    readback = exchanges[0][1]
    assert readback.status == "INVALID_SITE"
    # The refusal is a validly shaped readback (verified by the drive parse)
    # and carries no observation set, unlike a corrupted hybrid.
    assert readback.vehicles is None and readback.truck0 is None
    probes = freight_phase_outcome_v2(exchanges, prelaunch_digest=PRELAUNCH, plan=plan)
    assert probes["failed"]["world_state"] == "HALTED_BEFORE_MUTATION"


def test_foreign_company_refuses_site_and_halts():
    """Another resolvable company answers typed INVALID_COMPANY and the
    schedule halts prefix-preservingly."""
    vm = build_vm(second_company=5)
    site_request = work._freight_exchange_request(
        work.freight_schedule()[0],
        PRELAUNCH,
        work.freight_plan_v2(),
        dict(site=None, engine=None, vehicle=-1),
    ).model_copy(update={"company": 5})
    readback = drive(vm, site_request)
    assert readback.status == "INVALID_COMPANY"
    vm.execute("::sniffer.halted <- ::bridge.halted;")
    assert vm_root(vm)["sniffer"]["halted"] is True
    later = drive(
        vm,
        work._freight_exchange_request(
            work.freight_schedule()[1],
            PRELAUNCH,
            work.freight_plan_v2(),
            dict(site=None, engine=None, vehicle=-1),
        ),
    )
    assert later.status == "OUT_OF_ORDER"


def test_unbuildable_engine_pin_refuses_without_fallback():
    """F-10: a pin that cannot be built is refused ENGINE_PIN_MISMATCH, and
    no lowest-compatible fallback is ever substituted."""
    vm = build_vm(engine_ok=False)
    exchanges, plan = run_refusals(vm, ("site-00", "engine-00"))
    assert exchanges[0][1].status == "READY"
    assert exchanges[1][1].status == "ENGINE_PIN_MISMATCH"
    probes = freight_phase_outcome_v2(exchanges, prelaunch_digest=PRELAUNCH, plan=plan)
    assert probes["failed"]["world_state"] == "HALTED_BEFORE_MUTATION"


def test_engine_price_over_ceiling_refuses():
    vm = build_vm(engine_price=9000, quote_cost=9000, exec_cost=9000)
    exchanges, plan = run_refusals(vm, ("site-00", "engine-00"))
    assert exchanges[1][1].status == "COST_LIMIT"


def test_quote_drift_refuses():
    vm = build_vm(quote_cost=4430)
    exchanges, plan = run_refusals(vm, ("site-00", "engine-00"))
    assert exchanges[1][1].status == "COST_CHANGED"


def test_zero_cost_quote_refuses_as_unavailable():
    vm = build_vm(no_op=True)
    exchanges, plan = run_refusals(vm, ("site-00", "engine-00"))
    assert exchanges[1][1].status == "UNAVAILABLE_ENGINE"


def test_insufficient_funds_refuse_engine_admission():
    vm = build_vm()
    plan = work.freight_plan_v2()
    state = dict(site=None, engine=None, vehicle=-1)
    site_request = work._freight_exchange_request(
        work.freight_schedule()[0], PRELAUNCH, plan, state
    )
    assert drive(vm, site_request).status == "READY"
    vm.execute("::funds = 5;")
    engine_request = work._freight_exchange_request(
        work.freight_schedule()[1], PRELAUNCH, plan, state
    )
    assert drive(vm, engine_request).status == "INSUFFICIENT_FUNDS"


def test_post_purchase_identity_staleness_refuses_and_halts():
    """A drifted vehicle identity cannot command the admitted world."""
    vm = build_vm()
    exchanges, plan = run_prefix_until(vm, "purchase-00")
    request = work._freight_exchange_request(
        _entry_of("vread-00"), PRELAUNCH, plan, _state_of(exchanges)
    )
    assert request.request_id == "vread-00"
    stale = request.model_copy(update={"vehicle": 999})
    assert drive(vm, stale).status == "STALE_ADMISSION"
    # The refusal halted the schedule prefix-preservingly: the genuine
    # identity can no longer advance this attempt under another id.
    assert (
        drive(vm, request.model_copy(update={"request_id": "vread-99"})).status
        == "OUT_OF_ORDER"
    )


# --- staged windows ---------------------------------------------------------------


def test_window_exhaustion_is_honest_inconclusive():
    """A day-starved window never relabels itself as a success."""
    vm = build_vm()
    exchanges, plan = run_prefix_until(vm, "vread-01")
    assert exchanges[2][1].vehicle == 1
    request = work._freight_exchange_request(
        _entry_of("load-00"), PRELAUNCH, plan, _state_of(exchanges)
    )
    starved = request.model_copy(update={"watch_days": 1})
    readback = drive(vm, starved)
    assert readback.status == "WINDOW_EXHAUSTED"
    assert readback.tick is not None and readback.day is not None
    full = exchanges + [(starved, readback)]
    probes = freight_phase_outcome_v2(full, prelaunch_digest=PRELAUNCH, plan=plan)
    assert probes["failed"]["world_state"] == "INCONCLUSIVE_WINDOW"


def test_window_pause_refuses_instead_of_waiting():
    vm = build_vm()
    exchanges, plan = run_prefix_until(vm, "vread-01")
    vm.execute("::paused = true;")
    request = work._freight_exchange_request(
        _entry_of("load-00"), PRELAUNCH, plan, _state_of(exchanges)
    )
    readback = drive(vm, request)
    assert readback.status == "PAUSED"


def test_transit_off_route_refusal():
    vm = build_vm()
    exchanges, plan = run_prefix_until(vm, "vread-01")
    vehicle = exchanges[2][1].vehicle
    shape_world(vm, "load-00", vehicle)
    load_request = work._freight_exchange_request(
        _entry_of("load-00"), PRELAUNCH, plan, _state_of(exchanges)
    )
    assert load_request.watch_ticks == cfv.WATCH_MAX_TICKS_V2 == 2048
    loaded = drive(vm, load_request)
    assert loaded.status == "LOADED"
    vm.execute(f"::vehicles[{vehicle}].location = 46000;")
    transit_request = work._freight_exchange_request(
        _entry_of("transit-00"), PRELAUNCH, plan, _state_of(exchanges)
    )
    readback = drive(vm, transit_request)
    assert readback.status == "INVALID_ROUTE"
    # The refusal carries no observation set on the wire and halts.
    assert readback.position is None and readback.progress is None
    assert readback.tick is None and readback.day is None


def test_transit_forward_sampled_progress_reaches_delivery():
    """Sampled forward movement (even skipping tiles between samples) keeps
    the arrival semantics intact."""
    vm = build_vm()
    exchanges, plan = run_prefix_until(vm, "vread-01")
    vehicle = exchanges[2][1].vehicle
    shape_world(vm, "load-00", vehicle)
    load_request = work._freight_exchange_request(
        _entry_of("load-00"), PRELAUNCH, plan, _state_of(exchanges)
    )
    loaded = drive(vm, load_request)
    assert loaded.status == "LOADED"
    vm.execute(
        f"::vehicles[{vehicle}].location = {ROUTE[16]};\n"
        "::mover_seq <- ["
        + str(ROUTE[26])
        + ", "
        + str(DELIVERY)
        + "];\n"
        "::mover_i <- 0;\n"
        "::mover <- function() {"
        " if (::mover_i < ::mover_seq.len()) {"
        f"  ::vehicles[{vehicle}].location = ::mover_seq[::mover_i];"
        "  ::mover_i++;"
        " }"
        "};"
    )
    transit_request = work._freight_exchange_request(
        _entry_of("transit-00"), PRELAUNCH, plan, _state_of(exchanges)
    )
    readback = drive(vm, transit_request)
    assert readback.status == "AT_DELIVERY"
    assert (readback.position, readback.progress) == (DELIVERY, POSITION_PROGRESS)


def test_transit_sampled_direction_monotonicity_refuses_a_backward_drive():
    """A sampled route index behind an earlier one is a typed INVALID_ROUTE
    refusal, fail-closed (sampled evidence)."""
    vm = build_vm()
    exchanges, plan = run_prefix_until(vm, "vread-01")
    vehicle = exchanges[2][1].vehicle
    shape_world(vm, "load-00", vehicle)
    load_request = work._freight_exchange_request(
        _entry_of("load-00"), PRELAUNCH, plan, _state_of(exchanges)
    )
    loaded = drive(vm, load_request)
    assert loaded.status == "LOADED"
    vm.execute(
        f"::vehicles[{vehicle}].location = {ROUTE[16]};\n"
        "::mover <- function() {"
        f" ::vehicles[{vehicle}].location = {ROUTE[2]};"
        " ::mover = null;"
        "};"
    )
    transit_request = work._freight_exchange_request(
        _entry_of("transit-00"), PRELAUNCH, plan, _state_of(exchanges)
    )
    readback = drive(vm, transit_request)
    assert readback.status == "INVALID_ROUTE"
    assert readback.position is None and readback.progress is None


def test_delivery_monitor_arithmetic_refuses_drift():
    vm = build_vm()
    exchanges, plan = run_prefix_until(vm, "transit-00")
    vehicle = exchanges[2][1].vehicle
    shape_world(vm, f"deliver-{0:02d}", vehicle)
    vm.execute(
        f"::monitors.pickup[{PICKUP_INDUSTRY}] <- 5;"
        f" ::monitors.delivery[{DELIVERY_INDUSTRY}] <- 5;"
    )
    request = work._freight_exchange_request(
        _entry_of("deliver-00"), PRELAUNCH, plan, _state_of(exchanges)
    )
    readback = drive(vm, request)
    assert readback.status == "READBACK_MISMATCH"


def test_running_cost_outside_allowance_raises_the_funds_taxonomy():
    """A deliver span whose funds moved further than income explains is a
    typed taxonomy halt: the attempt equation owns the F-6 ledger bounds."""
    vm = build_vm()
    exchanges = _drive_attempt(vm, funds_deficit="deliver-00")
    probes = freight_phase_outcome_v2(
        exchanges, prelaunch_digest=PRELAUNCH, plan=work.freight_plan_v2()
    )
    # The phase evidence stays complete; the ledger taxonomy is the attempt
    # equation's gate, so the halt surfaces there and nowhere else.
    assert probes["verification"] == "PHASE_COMPLETE"
    with pytest.raises(ValueError, match="outside the taxonomy"):
        verify_freight_attempt_v2(
            exchanges, prelaunch_digest=PRELAUNCH, plan=work.freight_plan_v2()
        )


def _drive_attempt(vm: SQVM, *, zero: bool = False, funds_deficit: str = ""):
    """Drive all thirty exchanges without the middle attempting-verifier."""
    plan = work.freight_plan_v2()
    state: dict[str, Any] = dict(site=None, engine=None, vehicle=-1)
    exchanges: list[tuple[FreightRequestV2, FreightReadbackV2]] = []
    for entry in work.freight_schedule():
        label = entry["exchange"]
        request = work._freight_exchange_request(entry, PRELAUNCH, plan, state)
        if state["vehicle"] >= 0:
            shape_world(vm, label, state["vehicle"], zero=zero)
        if label == funds_deficit:
            vm.execute("::funds -= 30;")  # the deliver span drifts outside ±12
        readback = drive(vm, request)
        exchanges.append((request, readback))
        if entry["op"] == "site":
            state["site"] = work.admit_freight_site_v2(
                readback, prelaunch_digest=PRELAUNCH, plan=plan
            )
        elif entry["op"] == "engine":
            state["engine"] = work.admit_freight_engine_v2(
                readback, prelaunch_digest=PRELAUNCH, plan=plan, site=state["site"]
            )
        elif entry["op"] == "purchase":
            state["vehicle"] = readback.vehicle
    return exchanges


# --- finish honesty ----------------------------------------------------------------


def test_finish_proves_the_stopped_state_and_only_a_real_toggle():
    """The finish readback proves the stop: zero speed, stopped state, and
    stop_issued true only for a toggle actually issued."""
    vm = build_vm()
    exchanges, plan = run_prefix_until(vm, "finance-00")
    vehicle = exchanges[2][1].vehicle
    request = work._freight_exchange_request(
        _entry_of("finish-00"), PRELAUNCH, plan, _state_of(exchanges)
    )
    readback = drive(vm, request)
    assert readback.status == "PHASE_STOPPED" and readback.stop_issued is True
    assert readback.state == "STOPPED" and readback.speed == 0
    from app.simulation.openttd.corridor_freight_v2 import verify_freight_finish_v2

    verify_freight_finish_v2(readback, vehicle=vehicle)
    # A claim of a stop without the state proof fails verification.
    with pytest.raises(ValueError, match="proven stopped"):
        verify_freight_finish_v2(
            readback.model_copy(update={"speed": 5}), vehicle=vehicle
        )
    with pytest.raises(ValueError, match="stop command issued"):
        verify_freight_finish_v2(
            readback.model_copy(update={"stop_issued": False}), vehicle=vehicle
        )


def test_already_stopped_vehicle_is_never_toggled_and_honestly_halted():
    """A vehicle that reads stopped before the finish exchange is not
    re-toggled: stop_issued stays false, so the exchange refuses the
    verification (an honest uncertain halt, never a claimed stop)."""
    vm = build_vm()
    exchanges, plan = run_prefix_until(vm, "finance-00")
    vehicle = exchanges[2][1].vehicle
    vm.execute(
        f"::vehicles[{vehicle}].state = GSVehicle.VS_STOPPED;"
        " ::vehicles[%d].speed = 0;" % vehicle
    )
    request = work._freight_exchange_request(
        _entry_of("finish-00"), PRELAUNCH, plan, _state_of(exchanges)
    )
    readback = drive(vm, request)
    assert readback.status == "PHASE_STOPPED" and readback.stop_issued is False
    probes = freight_phase_outcome_v2(
        exchanges + [(request, readback)], prelaunch_digest=PRELAUNCH, plan=plan
    )
    assert probes["failed"]["world_state"] == "UNCERTAIN_AFTER_FAILED_COMMAND"


# --- F-11 typed zero-departure exemptions ------------------------------------------


def test_zero_departure_window_exempts_the_depot_and_pickup_only():
    """A load watch on a depot- or pickup-standing vehicle keeps waiting for
    a departure instead of typing a zero event ahead of the road."""
    vm = build_vm()
    exchanges, plan = run_prefix_until(vm, "vread-01")
    # The truck stands in its depot with zero cargo: no zero event is typed
    # until the day lease runs out first.
    request = work._freight_exchange_request(
        _entry_of("load-00"), PRELAUNCH, plan, _state_of(exchanges)
    )
    starved = request.model_copy(update={"watch_days": 1})
    readback = drive(vm, starved)
    assert readback.status == "WINDOW_EXHAUSTED"


# --- E53 fix round regression tests -------------------------------------------------


def test_empty_depot_to_pickup_travel_keeps_waiting_instead_of_typing_zero():
    """Blocker (a): a vehicle observed empty on the depot-to-pickup travel
    leg is pre-departure waiting — WINDOW_EXHAUSTED under its lease, never
    the typed ZERO_DEPARTED event the old on-route rule fired."""
    vm = build_vm()
    exchanges, plan = run_prefix_until(vm, "vread-01")
    vehicle = exchanges[2][1].vehicle
    # Pre-pickup on-route travel: an empty truck between the depot front
    # and the pickup stop (route indices 4..5 belong to the depot leg).
    vm.execute(
        f"::vehicles[{vehicle}].load = 0;\n"
        f"::vehicles[{vehicle}].location = {ROUTE[3]};"
    )
    request = work._freight_exchange_request(
        _entry_of("load-00"), PRELAUNCH, plan, _state_of(exchanges)
    )
    readback = drive(vm, request)
    assert readback.status == "WINDOW_EXHAUSTED"
    assert readback.tick is not None and readback.day is not None
    probes = freight_phase_outcome_v2(
        exchanges + [(request, readback)], prelaunch_digest=PRELAUNCH, plan=plan
    )
    assert probes["failed"]["world_state"] == "INCONCLUSIVE_WINDOW"
    assert probes["zero_departed_cycles"] == 0


def test_empty_pickup_standing_and_depot_standing_keep_waiting_too():
    """Blocker (a) at the stop: standing empty at the pickup stop (index 0)
    never types the departure event, lease or not."""
    vm = build_vm()
    exchanges, plan = run_prefix_until(vm, "vread-01")
    vehicle = exchanges[2][1].vehicle
    vm.execute(
        f"::vehicles[{vehicle}].load = 0;\n"
        f"::vehicles[{vehicle}].location = {PICKUP};"
    )
    request = work._freight_exchange_request(
        _entry_of("load-00"), PRELAUNCH, plan, _state_of(exchanges)
    )
    readback = drive(vm, request)
    assert readback.status == "WINDOW_EXHAUSTED"
    probes = freight_phase_outcome_v2(
        exchanges + [(request, readback)], prelaunch_digest=PRELAUNCH, plan=plan
    )
    assert probes["failed"]["world_state"] == "INCONCLUSIVE_WINDOW"


def test_off_route_empty_and_loaded_samples_type_invalid_route():
    """Blocker (a) complement: a vehicle off the ordered road (not in the
    pinned depot) is a typed INVALID_ROUTE refusal — loaded or empty — and
    never a departure event."""
    vm = build_vm()
    exchanges, plan = run_prefix_until(vm, "vread-01")
    vehicle = exchanges[2][1].vehicle
    request = work._freight_exchange_request(
        _entry_of("load-00"), PRELAUNCH, plan, _state_of(exchanges)
    )
    vm.execute(
        f"::vehicles[{vehicle}].load = 0;\n"
        f"::monitors.pickup[{PICKUP_INDUSTRY}] <- 5;\n"
        f"::vehicles[{vehicle}].location = 46000;"
    )
    empty = drive(vm, request)
    assert empty.status == "INVALID_ROUTE"
    assert empty.load is None and empty.tick is None and empty.day is None
    load_only = request.model_copy(update={"request_id": "load-50"})
    # The second dispatch shapes a loaded off-route vehicle: still refusal,
    # and the first breach already halted the schedule (prefix-preserving).
    assert drive(vm, load_only).status == "OUT_OF_ORDER"


def test_off_route_loaded_sample_types_invalid_route():
    """The loaded form of the off-route refusal, with the schedule still
    intact (fresh VM: the refusal arrives before any halt)."""
    vm = build_vm()
    exchanges, plan = run_prefix_until(vm, "vread-01")
    vehicle = exchanges[2][1].vehicle
    vm.execute(
        f"::vehicles[{vehicle}].load = {LOADS[0]};\n"
        f"::monitors.pickup[{PICKUP_INDUSTRY}] <- {LOADS[0]};\n"
        f"::vehicles[{vehicle}].location = 46000;"
    )
    request = work._freight_exchange_request(
        _entry_of("load-00"), PRELAUNCH, plan, _state_of(exchanges)
    )
    readback = drive(vm, request)
    assert readback.status == "INVALID_ROUTE"
    assert readback.load is None and readback.position is None


def test_loaded_snapshot_requires_verified_departure_and_monitor_evidence():
    """Blocker (b): LOADED is typed only at a verified departure with its
    matching pickup-monitor echo — loading-in-progress at the stop keeps
    waiting; a departed-but-contradicted monitor refuses instead; a
    consistent departure snapshot verifies."""
    plan = work.freight_plan_v2()
    # 1. Standing at the pickup with cargo: no departure, no snapshot.
    vm = build_vm()
    exchanges, _ = run_prefix_until(vm, "vread-01")
    vehicle = exchanges[2][1].vehicle
    vm.execute(
        f"::vehicles[{vehicle}].load = {LOADS[0]};\n"
        f"::monitors.pickup[{PICKUP_INDUSTRY}] <- {LOADS[0]};\n"
        f"::vehicles[{vehicle}].location = {PICKUP};"
    )
    request = work._freight_exchange_request(
        _entry_of("load-00"), PRELAUNCH, plan, _state_of(exchanges)
    )
    waiting = drive(vm, request)
    assert waiting.status == "WINDOW_EXHAUSTED"
    # 2. Departed, but the monitor contradicts the truck load: fail-closed.
    vm2 = build_vm()
    exchanges2, plan = run_prefix_until(vm2, "vread-01")
    vehicle = exchanges2[2][1].vehicle
    vm2.execute(
        f"::vehicles[{vehicle}].load = {LOADS[0]};\n"
        f"::vehicles[{vehicle}].location = {PICKUP};\n"
        f"::monitors.pickup[{PICKUP_INDUSTRY}] <- {LOADS[0] - 1};\n"
        "::mover <- function() {"
        f" ::vehicles[{vehicle}].location = {PICKUP_FRONT};"
        " ::mover = null;"
        "};"
    )
    drifted = drive(vm2, request)
    assert drifted.status == "READBACK_MISMATCH"
    # 3. The verified departure with matching evidence types the snapshot.
    vm3 = build_vm()
    exchanges3, plan = run_prefix_until(vm3, "vread-01")
    vehicle = exchanges3[2][1].vehicle
    vm3.execute(
        f"::vehicles[{vehicle}].load = {LOADS[0]};\n"
        f"::vehicles[{vehicle}].location = {PICKUP};\n"
        f"::monitors.pickup[{PICKUP_INDUSTRY}] <- {LOADS[0]};\n"
        "::mover <- function() {"
        f" ::vehicles[{vehicle}].location = {PICKUP_FRONT};"
        " ::mover = null;"
        "};"
    )
    snapshot = drive(vm3, request)
    assert snapshot.status == "LOADED"
    assert snapshot.pickup_amount == snapshot.load == LOADS[0]


def test_zero_departure_requires_zero_pickup_monitor_evidence():
    """Blocker (b) complement: an empty departure past the pickup stop with
    a nonzero pickup residue contradicts the typed event (READBACK_MISMATCH);
    zero residue re-types the schedule's empty-run evidence."""
    plan = work.freight_plan_v2()
    base = work.freight_schedule()[10]
    # Nonzero residue: contradicted empty departure.
    vm = build_vm()
    exchanges, plan = run_prefix_until(vm, "vread-01")
    vehicle = exchanges[2][1].vehicle
    vm.execute(
        f"::vehicles[{vehicle}].location = {PICKUP};\n"
        f"::monitors.pickup[{PICKUP_INDUSTRY}] <- 7;\n"
        "::mover <- function() {"
        f" ::vehicles[{vehicle}].location = {ZERO_DEPARTURE_TILE};"
        " ::mover = null;"
        "};"
    )
    request = work._freight_exchange_request(
        _entry_of("load-00"), PRELAUNCH, plan, _state_of(exchanges)
    )
    contradicted = drive(vm, request)
    assert contradicted.status == "READBACK_MISMATCH"
    # Zero residue: the same proof types the F-11 event.
    vm2 = build_vm()
    exchanges2, plan = run_prefix_until(vm2, "vread-01")
    vm2.execute(
        f"::vehicles[{exchanges2[2][1].vehicle}].location = {PICKUP};\n"
        "::mover <- function() {"
        f" ::vehicles[{exchanges2[2][1].vehicle}].location = {ZERO_DEPARTURE_TILE};"
        " ::mover = null;"
        "};"
    )
    typed = drive(vm2, request)
    assert typed.status == "ZERO_DEPARTED"
    assert typed.pickup_amount == 0
    assert base["watch_days"] == cfv.FREIGHT_CYCLE_DAY_CAP_V2


def test_delivery_acceptance_requires_the_bay_with_zero_cargo():
    """Blocker (c): the deliver window types nothing until the vehicle
    stands at the pinned bay tile — the front approach (one tile away)
    keeps waiting even with zero cargo and settled monitors."""
    vm = build_vm()
    exchanges, plan = run_prefix_until(vm, "transit-00")
    load_request, loaded_readback = exchanges[-2]
    assert load_request.request_id == "load-00"
    assert loaded_readback.status == "LOADED"
    vehicle = loaded_readback.vehicle
    # The prefix's own load-00 window typed the verified departure (the
    # stub world's one-shot mover walked the truck out on the first Sleep).
    # Not at the bay: a fresh deliver-00 window stands the vehicle on the
    # front approach, one tile off the pinned bay, with the delivery residue
    # already armed — the at-bay gate still refuses to advance the unload
    # arithmetic, so the window stays waiting until its lease expires.
    vm.execute(
        f"::vehicles[{vehicle}].location = {ROUTE[27]};\n"
        f"::monitors.delivery[{DELIVERY_INDUSTRY}] <- {LOADS[0]};"
    )
    deliver_request = work._freight_exchange_request(
        _entry_of("deliver-00"), PRELAUNCH, plan, _state_of(exchanges)
    )
    starved = deliver_request.model_copy(update={"watch_days": 1})
    readback = drive(vm, starved)
    assert readback.status == "WINDOW_EXHAUSTED"
    assert readback.load is None
    # At the bay with zero cargo the window types the delivery.
    vm2 = build_vm()
    exchanges2, plan = run_prefix_until(vm2, "deliver-00")
    delivered = exchanges2[-1][1]
    assert delivered.status == "DELIVERED"
    assert delivered.position == DELIVERY
    assert delivered.load == 0 and delivered.recheck is True



def test_python_level_delivered_verifier_refuses_off_bay_acceptance():
    """Blocker (c) python-side: a DELIVERED echo naming any other tile than
    the plan's bay is refused before it can claim the cycle receipt."""
    from app.simulation.openttd.corridor_freight_v2 import verify_freight_delivered_v2

    vm = build_vm()
    exchanges, plan = run_prefix_until(vm, "deliver-00")
    delivered = exchanges[-1][1]
    assert delivered.status == "DELIVERED" and delivered.position == DELIVERY
    gate = verify_freight_delivered_v2(
        delivered, vehicle=delivered.vehicle, load=LOADS[0], delivery=plan.delivery
    )
    assert gate["position"] == DELIVERY
    for drifted in (
        delivered.model_copy(update={"position": DELIVERY_FRONT}),
        delivered.model_copy(update={"position": None}),
    ):
        with pytest.raises(ValueError, match="delivery bay"):
            verify_freight_delivered_v2(
                drifted,
                vehicle=delivered.vehicle,
                load=LOADS[0],
                delivery=plan.delivery,
            )
    # A verifier pinned to some other bay cannot accept this echo either.
    with pytest.raises(ValueError, match="delivery bay"):
        verify_freight_delivered_v2(
            delivered,
            vehicle=delivered.vehicle,
            load=LOADS[0],
            delivery=int(ROUTE[5]),
        )


def test_python_level_loaded_verifier_refuses_missing_monitor_evidence():
    """Blocker (b) python-side: a LOADED echo without its pickup-monitor
    evidence, or with drifted evidence, is refused."""
    from app.simulation.openttd.corridor_freight_v2 import verify_freight_loaded_v2

    vm = build_vm()
    exchanges, plan = run_prefix_until(vm, "load-00")
    site = work.admit_freight_site_v2(
        exchanges[0][1], prelaunch_digest=PRELAUNCH, plan=plan
    )
    engine = work.admit_freight_engine_v2(
        exchanges[1][1], prelaunch_digest=PRELAUNCH, plan=plan, site=site
    )
    loaded = exchanges[-1][1]
    assert loaded.status == "LOADED" and loaded.pickup_amount == loaded.load
    verify_freight_loaded_v2(
        loaded,
        vehicle=loaded.vehicle,
        engine=engine,
        waiting_baseline=site.waiting,
    )
    for drifted, match in (
        (loaded.model_copy(update={"pickup_amount": None}), "monitor"),
        (loaded.model_copy(update={"pickup_amount": loaded.load - 1}), "monitor"),
    ):
        with pytest.raises(ValueError, match=match):
            verify_freight_loaded_v2(
                drifted,
                vehicle=loaded.vehicle,
                engine=engine,
                waiting_baseline=site.waiting,
            )



def test_freight_window_dispatch_refusal_types_the_aggregate_day_gate():
    """Blocker (d) unit: the authority gate admits a window only while its
    lease fits the 60-day aggregate budget."""
    assert cfv.freight_window_dispatch_refusal_v2(0, 10) is None
    assert cfv.freight_window_dispatch_refusal_v2(50, 10) is None
    refusal = cfv.freight_window_dispatch_refusal_v2(51, 10)
    assert refusal is not None and "60-day aggregate attempt authority" in refusal
    assert cfv.freight_window_dispatch_refusal_v2(60, 10) is not None
    # Staged rows: every watch window leases exactly the cycle day cap.
    for entry in work.freight_schedule():
        if entry["op"].endswith("-watch"):
            assert entry["watch_days"] == cfv.FREIGHT_CYCLE_DAY_CAP_V2 == 10
            assert entry["watch_ticks"] == cfv.WATCH_MAX_TICKS_V2 == 2048


def test_freight_day_authority_helper_skips_non_window_exchanges():
    """Blocker (d) unit: the executor's pre-dispatch helper gates only the
    three watch ops, typing the same aggregate refusal."""
    schedule = work.freight_schedule()
    for entry in schedule:
        assert work._freight_day_authority(entry, 0) is None
    watch = next(e for e in schedule if e["op"] == "deliver-watch")
    assert work._freight_day_authority(watch, 50) is None
    refusal = work._freight_day_authority(watch, 55)
    assert refusal is not None and "60-day aggregate attempt authority" in refusal
    fixed = next(e for e in schedule if e["op"] == "vread")
    assert work._freight_day_authority(fixed, 9999) is None


def test_evidence_windows_beyond_the_day_authority_are_refused():
    """Blocker (d) replay: watch evidence whose day ledger crosses the
    60-day authority is refused by the production verifier — the gate is
    indistinguishable from the executor's pre-dispatch halt."""
    vm = build_vm()
    exchanges, plan = run_attempt(vm)
    reference = next(
        readback.day
        for request, readback in exchanges
        if request.request_id == "start-00"
    )
    assert reference is not None
    tampered_day = int(reference) + 55
    # Tamper the load-01 readback day far forward so its verified ledger
    # span stays inside the 60-day authority (55), but the next window's
    # dispatch gate (55 + 10) does not fit the aggregate attempt authority.
    rebuilt = []
    for request, readback in exchanges:
        if request.request_id == "load-01" and readback.status == "LOADED":
            readback = readback.model_copy(update={"day": tampered_day})
        rebuilt.append((request, readback))
    probes = freight_phase_outcome_v2(
        rebuilt, prelaunch_digest=PRELAUNCH, plan=plan
    )
    assert probes["verification"] == "PARTIAL_EXECUTION_EVIDENCE"
    assert "60-day aggregate attempt authority" in probes["failed"]["error"]


def test_watch_request_drifted_from_staged_window_budgets_is_refused():
    """Replay hardening: a watch request whose tick or day echoes drifted
    from the staged schedule rows is refused before any evidence binds."""
    plan = work.freight_plan_v2()
    vm = build_vm()
    exchanges, plan = run_prefix_until(vm, "load-00")
    request, readback = exchanges[-1]
    assert readback.status == "LOADED"
    prefix = exchanges[:-1]
    probes = freight_phase_outcome_v2(
        prefix + [(request, readback)], prelaunch_digest=PRELAUNCH, plan=plan
    )
    assert probes["failed"] is None
    for updates in (
        {"watch_ticks": cfv.WATCH_MAX_TICKS_V2 - 1},
        {"watch_ticks": 0},
        {"watch_days": cfv.FREIGHT_CYCLE_DAY_CAP_V2 + 1},
        {"watch_days": 0},
    ):
        drifted = request.model_copy(update=updates)
        tampered = freight_phase_outcome_v2(
            prefix + [(drifted, readback)], prelaunch_digest=PRELAUNCH, plan=plan
        )
        assert tampered["failed"] is not None, updates
        assert "staged window budgets" in tampered["failed"]["error"]



# --- finish honesty ----------------------------------------------------------------


def _site_ready(vm: SQVM):
    """A fresh native READY site readback from the shipped package."""
    site_request = work._freight_exchange_request(
        work.freight_schedule()[0],
        PRELAUNCH,
        work.freight_plan_v2(),
        dict(site=None, engine=None, vehicle=-1),
    )
    return drive(vm, site_request)


def test_python_level_site_admission_refuses_defects():
    """The Python latcher owns the fail-closed site gates the stub world
    already exercised natively: any drifted fact is refused, never absorbed."""
    plan = work.freight_plan_v2()
    readback = _site_ready(build_vm())
    assert readback.status == "READY"
    work.admit_freight_site_v2(readback, prelaunch_digest=PRELAUNCH, plan=plan)
    for update, match in (
        ({"pickup_industry_count": 0}, "exactly one cargo industry"),
        ({"pickup_industry_count": 2}, "exactly one cargo industry"),
        ({"funds": FUNDS + 1}, "close-out level"),
        ({"accept": 7}, "pinned full 8/8"),
        ({"depot_edge": False}, "F-12"),
        ({"pickup_industry": DELIVERY_INDUSTRY}, "must stay distinct"),
        ({"vehicles": 1}, "zero vehicles"),
        ({"road_ready": False}, "current road type"),
    ):
        with pytest.raises(ValueError, match=match):
            work.admit_freight_site_v2(
                readback.model_copy(update=update),
                prelaunch_digest=PRELAUNCH,
                plan=plan,
            )


def test_python_level_engine_admission_refuses_defects():
    """F-10: the Python latcher refuses any census drift or a foreign pin,
    holding the fail-closed engine admission the stub world already proved."""
    plan = work.freight_plan_v2()
    vm = build_vm()
    site = _site_ready(vm)
    site_intent = work.admit_freight_site_v2(
        site, prelaunch_digest=PRELAUNCH, plan=plan
    )
    engine_request = work._freight_exchange_request(
        work.freight_schedule()[1],
        PRELAUNCH,
        plan,
        dict(site=None, engine=None, vehicle=-1),
    )
    engine = drive(vm, engine_request)
    assert engine.status == "READY"
    work.admit_freight_engine_v2(
        engine, prelaunch_digest=PRELAUNCH, plan=plan, site=site_intent
    )
    for update, match in (
        ({"engine": 124}, "correlated READY enumeration"),
        ({"vehicle": 1}, "READY enumeration"),
        ({"capacity": 19}, "census capacity"),
        ({"cargo": 2}, "census cargo"),
        ({"price": 4430}, "census price and speed"),
        ({"max_speed": 47}, "census price and speed"),
        ({"fleet": (127, 126, 125, 124)}, "compatible universe"),
        ({"cost": 0}, "positive affordable tested quote"),
        ({"funds": FUNDS + 1}, "funds drifted"),
    ):
        with pytest.raises(ValueError, match=match):
            work.admit_freight_engine_v2(
                engine.model_copy(update=update),
                prelaunch_digest=PRELAUNCH,
                plan=plan,
                site=site_intent,
            )


# --- N1/N2/N3 order-layer evidence ------------------------------------------------


def test_stub_appends_carry_tile_destinations_and_real_flags():
    """N1/N2 order evidence: tile destinations, real 15.x flag values, and
    OF_FULL_LOAD never issued; N3 evidence: the two-argument destination."""
    vm = build_vm()
    run_prefix_until(vm, "order-read-00")
    # The binding returns squirrel arrays: read them back element-wise.
    append_calls = [list(entry) for entry in vm_root(vm)["append_calls"]]
    n3_calls = [list(entry) for entry in vm_root(vm)["n3_calls"]]
    # The stub appended tiles (N1), not station ids, exactly once per stop.
    assert append_calls == [[PICKUP, cfv.OF_NONE_V2], [DELIVERY, cfv.OF_NO_LOAD_V2]]
    assert n3_calls == append_calls  # the two-arg form saw identical inputs
    appended_flags = {flags for _, flags in append_calls}
    assert appended_flags == {cfv.OF_NONE_V2, cfv.OF_NO_LOAD_V2}
    # OF_FULL_LOAD is documented forbidden: no order carriage ever ships it.
    assert cfv.OF_FULL_LOAD_FORBIDDEN_V2 == 64
    assert cfv.OF_FULL_LOAD_FORBIDDEN_V2 not in appended_flags
    # The stored orders keep the tile-form destination and the resolved
    # station id (N1, 15.3, E92): d is the appended stop tile, sid is the
    # MakeGoToStation resolution; flags round-trip verbatim.
    vm.execute(
        "::sniffer.o0 <- ::orders[1][0];"
        " ::sniffer.o1 <- ::orders[1][1];"
    )
    orders = vm_root(vm)["sniffer"]
    assert (orders["o0"]["d"], orders["o0"]["f"]) == (PICKUP, cfv.OF_NONE_V2)
    assert orders["o0"]["sid"] == 0
    assert (orders["o1"]["d"], orders["o1"]["f"]) == (DELIVERY, cfv.OF_NO_LOAD_V2)
    assert orders["o1"]["sid"] == 2


def _order_readback(*, op: str, order_index: int, **extra: Any) -> FreightReadbackV2:
    """A wire-shaped freight reply for one order-layer exchange (follows the
    exact correlation stride and op subset the shipped package echoes)."""
    payload: dict[str, Any] = {
        "protocol": 8,
        "op": op,
        "request_id": "order-00" if op == "order" else "order-read-00",
        "plan": PRELAUNCH,
        "company": 0,
        "max_cost": 5000,
        "pickup": PICKUP,
        "delivery": DELIVERY,
        "depot": DEPOT_TILE,
        "route_digest": PLAN.route_digest,
        "witness_digest": None,
        "engine": 123,
        "vehicle": 1,
        "expected_cost": 0,
        "order_index": order_index,
        "watch_ticks": -1,
        "watch_days": -1,
        "status": "ORDERED" if op == "order" else "ORDER_SET_VERIFIED",
        "funds": FUNDS - ENGINE_QUOTE,
        "cost": 0,
        "income": 0,
    }
    payload.update(extra)
    return FreightReadbackV2.model_validate(payload)


def test_python_level_order_verifier_refuses_the_three_defects():
    """N1/N2/N3 python-side: wrong tile destinations, wrong flags, or a
    non-goto order are refused with the typed N1/N2/N3 messages."""
    from app.simulation.openttd.corridor_freight_v2 import (
        verify_freight_order_set_v2,
        verify_freight_order_v2,
    )

    plan = work.freight_plan_v2()
    append0 = _order_readback(
        op="order", order_index=0, dest=PICKUP, flags=cfv.OF_NONE_V2, goto=True
    )
    with pytest.raises(ValueError, match=r"\(N1\)"):
        verify_freight_order_v2(
            append0.model_copy(update={"dest": PICKUP_FRONT}),
            index=0,
            vehicle=1,
            plan=plan,
        )
    with pytest.raises(ValueError, match=r"\(N2\)"):
        verify_freight_order_v2(
            append0.model_copy(update={"flags": cfv.OF_FULL_LOAD_FORBIDDEN_V2}),
            index=0,
            vehicle=1,
            plan=plan,
        )
    with pytest.raises(ValueError, match="goto-station"):
        verify_freight_order_v2(
            append0.model_copy(update={"goto": False}), index=0, vehicle=1, plan=plan
        )
    appends = (
        append0,
        _order_readback(
            op="order", order_index=1, dest=DELIVERY, flags=cfv.OF_NO_LOAD_V2, goto=True
        ),
    )
    inventory = _order_readback(
        op="order-read",
        order_index=-1,
        order_len=2,
        dest0=PICKUP,
        flags0=cfv.OF_NONE_V2,
        goto0=True,
        dest1=DELIVERY,
        flags1=cfv.OF_NO_LOAD_V2,
        goto1=True,
    )
    verify_freight_order_set_v2(appends, inventory, vehicle=1, plan=plan)
    # The inventory carries the defect: a drifted order destination or flag
    # is refused against the planned v2 inventory (the appended receipts
    # stay bound to the same stop indexes).
    with pytest.raises(ValueError, match="planned v2 inventory"):
        verify_freight_order_set_v2(
            appends, inventory.model_copy(update={"dest1": DELIVERY_FRONT}),
            vehicle=1, plan=plan,
        )
    with pytest.raises(ValueError, match="exactly two orders"):
        verify_freight_order_set_v2(
            appends, inventory.model_copy(update={"order_len": 1}),
            vehicle=1, plan=plan,
        )


# --- package identity pins ---------------------------------------------------------


def test_package_planned_schedule_equals_the_wire_contract():
    """The shipped package's baked planned rows equal the T1 exchange table."""
    text = (PACKAGE / "main.nut").read_text()
    planned_span = re.search(r"planned = \[(.*?)\n    \]", text, re.DOTALL)
    assert planned_span is not None
    rows = re.findall(
        r'\["([a-z0-9-]+)", "([a-z-]+)", "([A-Z_]+)"\]', planned_span.group(1)
    )
    assert [(row[0], row[1]) for row in rows] == list(
        cfv.freight_exchange_sequence_v2(cfv.PLANNED_FREIGHT_CYCLES_V2)
    )
    assert all(cfv._FREIGHT_SUCCESS_STATUS_V2[op] == status for _, op, status in rows)
    assert len(rows) == cfv.PLANNED_FREIGHT_EXCHANGES_V2 == 30


def test_package_pinned_constants_match_the_frozen_module():
    """The package's world pins equal the compiled world constants."""
    text = (PACKAGE / "main.nut").read_text()
    for constant, value in (
        ("PICKUP", PICKUP),
        ("PICKUP_FRONT", PICKUP_FRONT),
        ("DELIVERY", DELIVERY),
        ("DELIVERY_FRONT", DELIVERY_FRONT),
        ("DEPOT_TILE", DEPOT_TILE),
        ("DEPOT_FRONT", DEPOT_FRONT),
        ("FREIGHT_COMPANY", 0),
        ("FREIGHT_CARGO", 1),
        ("ENGINE_PIN", 123),
        ("OF_NONE", 0),
        ("OF_FULL_LOAD_FORBIDDEN", 64),
        ("OF_NO_LOAD", 128),
        ("MAX_TICKS", cfv.WATCH_MAX_TICKS_V2),
        ("MAX_DAYS", cfv.FREIGHT_DAY_BUDGET_V2),
        ("FLEET_ECHO", cfv.MAX_FREIGHT_FLEET_ECHO_V2),
        ("MAX_ROUTE_TILES", cfv.MAX_FREIGHT_ROUTE_TILES_V2),
        ("max_requests", cfv.FREIGHT_REQUEST_BUDGET_V2),
    ):
        assert re.search(rf"\b{constant} = {value}\b", text), constant
    baked = re.search(r"BAKED_ROUTE = \[(.*?)\]", text, re.DOTALL)
    assert baked is not None
    tiles = [int(tile) for tile in re.findall(r"\d+", baked.group(1))]
    assert tiles == list(ROUTE)
    # The physical witness stays a Python-side digest: no .nut witness array.
    assert not re.search(r"\bWITNESS\b", text)


def test_package_carries_the_save_restore_bridge():
    text = (PACKAGE / "main.nut").read_text()
    assert "class NetworkFreightProof extends D5FreightV2Proof" in text


def test_local_vm_stubs_stay_single_purpose():
    first = build_vm()
    second = build_vm()
    assert first is not second
