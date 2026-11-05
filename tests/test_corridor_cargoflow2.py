"""Controlled offline tests for the D5-CARGOFLOW-2 wire contract (protocol 11).

The contract under test is ``app/simulation/openttd/corridor_cargoflow2.py``
and the additive delivery handler shipped in
``app/simulation/openttd/d5_cargoflow2_package/main.nut``. The shipped package
runs inside the real Squirrel VM against a stub world that reproduces the
civil calendar, the pinned stations' families and industries' facts with the
15.3 ``-1`` fact families verbatim, and the real road-vehicle lifecycle
(GSEngine census admission, BuildVehicle, tile-destination orders, start,
movement with load/unload edges) every dispatched reply is re-parsed through
the protocol-11 wire contract, never through the package's own words.

This file owns the shared harness of the D5-CARGOFLOW-2 split (the
protocol-10 trio's shape): the module pins/schedule/plan/budget gates, the
request build and byte audit, the §4 funds-model vector of record, the §4.5
per-op readback subset ladder, the §7 synthetic phase-outcome/verdict fixture
set — plus the EXPORTED VM harness (``API``/``WORLD``/``STUB``, ``ANCHOR``,
``PLAN``, ``base_request``/``make_request``/``build_vm``/``drive``/``reply``/
``expect_drop``/``squirrel_table``/``vm_root``/seed helpers) that
``tests/test_corridor_cargoflow2_vm.py`` imports; that sibling file owns the
shipped-handler reference against this stub world. Every verification here is
offline: nothing launches OpenTTD, connects to an AdminPort or writes any
native or save state — only the tests' own VM world is mutated.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, cast

import pytest
from pydantic import ValidationError
from squirrel import SQVM

from app.simulation.openttd import corridor_cargoflow2 as cf
from app.simulation.openttd.corridor_freight_v2 import FUNDS_AT_DEPOT_MUTATION_CLOSE
from app.simulation.openttd.proof import corridor_cargoflow2_native as work

REPO = Path(__file__).resolve().parents[1]
PACKAGE = REPO / "app" / "simulation" / "openttd" / "d5_cargoflow2_package"

PRELAUNCH = "a" * 64
OTHER_PLAN = "b" * 64
REQUEST_PLAN_DIGEST = "98d055c4e826296f79a8e7d70275be14256229732637fc6cdf547dca47f506ca"

SCHEDULE = work.cargoflow2_schedule()
PLAN = work.cargoflow2_pipeline_plan()
EXCHANGES = tuple(cf.CARGOFLOW2_EXCHANGE_IDS)
FUNDS = FUNDS_AT_DEPOT_MUTATION_CLOSE
QUOTE = cf.CARGOFLOW2_PURCHASE_QUOTE
ENGINE_RUNNING_DISPLAY = 421

# The stub world's launch instant and anchor: the fixed chain observes at the
# launch day (L = 712228) with the latched tick 30 of record, and the first
# arrival latches the same day inside arrive-00's flight window.
ANCHOR = 712228
TICK_OF_RECORD = 30
VEHICLE = 1

API = """
::events <- [];
::replies <- [];
::send_ok <- true;
::ticks <- 30;
::sniffer <- {last = "missing"};
class GSController {
    function GetTick() { return ::ticks; }
    function Sleep(howmany) {
        if (howmany != 1) throw "unexpected script sleep";
        local old_day = ::day;
        if (!::ticks_freeze) ::ticks = ::ticks + 1;
        ::day = ::day + ::day_rate;
        if (::stop_at >= 0 && ::ticks == ::stop_at) throw "CONTROLLED_STOP";
        run_motion(old_day, ::day);
    }
}
class GSEvent { static ET_ADMIN_PORT = 101; }
class ControlledAdminEvent {
    object = null;
    constructor(value) { this.object = value; }
    function GetEventType() { return GSEvent.ET_ADMIN_PORT; }
    function GetObject() { return this.object; }
}
class GSEventAdminPort {
    static function Convert(event) { return event; }
}
class GSEventController {
    static function IsEventWaiting() { return ::events.len() > 0; }
    static function GetNextEvent() { return ::events.remove(0); }
}
class GSAdmin {
    static function Send(value) {
        if (!::send_ok) return false;
        ::replies.append(value);
        return true;
    }
}
::markers <- [];
class GSLog {
    static function Info(value) { ::markers.append(value); }
}
"""

WORLD = """
::funds <- 489650;
::finances <- {income = 0, delivered = 0};
::paused <- false;
::valid_company <- true;
::second_company <- 1;
::mode_ok <- true;
::ticks_freeze <- false;
::day_rate <- 1;
::day <- 712228;
::stop_at <- -1;
/* The stops the order gate resolves (tile-keyed, the N1 stop-tile forms). */
::stops <- {};
/* The pinned stations' measured families, keyed by station id of record. */
::stations <- {};
/* The pinned industries' measured facts, keyed by industry id of record. */
::industries <- {};
::engines <- {};
::engine_ok <- true;
::engine_price <- 4429;
::engine_capacity <- 20;
::engine_display_running <- 421;
::engine_speed <- 48;
::vehicles <- {};
::orders <- {};
::next_vehicle <- 1;
::account <- 0;
::tests <- {};
::exec_cost <- 4429;
::quote_cost <- 4429;
::no_op <- false;
::reject_start <- false;
::depots <- {};
/* The 15.3 native fail-close model (the depot-mutation E72 stub idiom and
 * the T-006 root cause): the per-script current road type is
 * INVALID_ROADTYPE (63) until set, and a GSRoad tile predicate that
 * consults that current type fails closed until the package pins it. */
::cur_road_type <- 63;
::last_accepted <- -1;
/* Motion scripting: every Sleep runs the queued callbacks whose tick is due,
 * and a strictly increasing day sweep lands exactly the §4 financial world of
 * record: one whole-unit running charge per ended day through the same 8.8
 * fixed-point fraction carry the wire model walks (independent
 * reimplementation — the two must agree at every exchange, the funds fence
 * proves it), plus the whole monthly fee at each crossed 1950 boundary. */
::moves <- [];
::stub_frac <- 0;
::run_start_day <- -1;
::run_start_tick <- 0;
::stub_month_starts <- [712254, 712282];
function run_motion(old_day, new_day) {
    if (new_day > old_day) cargoflow2_stub_fees(old_day, new_day);
    for (local i = ::moves.len() - 1; i >= 0; i--) {
        if (::ticks >= ::moves[i].tick) {
            local act = ::moves[i].fn;
            ::moves.remove(i);
            act();
        }
    }
}
function cargoflow2_stub_fees(old_day, new_day) {
    for (local d = old_day; d < new_day; d++) {
        local rt = 74;
        if (d == ::run_start_day) rt = 74 - ::run_start_tick;
        local c256 = (::engine_display_running * rt * 256) / 27010;
        local next = (::stub_frac - (c256 % 256) + 256) % 256;
        local whole = (c256 >> 8) + (next > ::stub_frac ? 1 : 0);
        ::funds = ::funds - whole;
        ::stub_frac = next;
    }
    foreach (boundary in ::stub_month_starts) {
        if (old_day < boundary && new_day >= boundary) ::funds = ::funds - 192;
    }
}
function seed_stop(sid, w, from0, from1, pl, pl0, pl1) {
    ::stations[sid] <- {w = w, from0 = from0, from1 = from1,
                         pl = pl, pl0 = pl0, pl1 = pl1};
}
function cargoflow2_seed_stop(sid, w, from0, from1, pl, pl0, pl1) {
    seed_stop(sid, w, from0, from1, pl, pl0, pl1);
}
function seed_industry(ind, stock, prod, trans) {
    ::industries[ind] <- {stock = stock, prod = prod, trans = trans};
}
function cargoflow2_seed_industry(ind, stock, prod, trans) {
    seed_industry(ind, stock, prod, trans);
}
/* The pinned depot-chain world of record at admission: the producer
 * (industry 0) carries no accepted slot so its stock is the 15.3 -1 fact,
 * the acceptor (industry 1) carries stock 0 and the -1 non-producer fact,
 * and both pinned stops sit with empty families. */
seed_industry(0, -1, 104, 0);
seed_industry(1, 0, -1, 0);
seed_stop(0, 0, 0, 0, 0, 0, 0);
seed_stop(2, 0, 0, 0, 0, 0, 0);
::stops[45748] <- {sid = 0};
::stops[50862] <- {sid = 2};
::depots[45487] <- {front = 45743};
::engines[123] <- true;
"""

STUB = """
class GSGame {
    static function IsPaused() { return ::paused; }
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
class GSDate {
    static function GetCurrentDate() { return ::day; }
    static function GetYear(day) { return 1950 + (day - ::calendar_base) / 365; }
    static function GetMonth(day) { return civil_month(day); }
    static function GetDayOfMonth(day) { return civil_day_of_month(day); }
}
/* The anchored 1950 calendar of record (corridor_cargoflow2.py): day
 * 712223 is Jan 1, 1950; the 1950 month lengths; the attempt never leaves
 * this year, so the fragment reproduces every civil field of record. */
::calendar_base <- 712223;
::month_lengths <- [31,28,31,30,31,30,31,31,30,31,30,31];
function civil_month(day) {
    local rem = day - ::calendar_base;
    rem = rem % 365;
    local month = 1;
    foreach (length in ::month_lengths) {
        if (rem < length) return month;
        rem = rem - length;
        month = month + 1;
    }
    throw "D5_TEST_CALENDAR";
}
function civil_day_of_month(day) {
    local rem = day - ::calendar_base;
    rem = rem % 365;
    foreach (length in ::month_lengths) {
        if (rem < length) return rem + 1;
        rem = rem - length;
    }
    throw "D5_TEST_CALENDAR";
}
class GSRoad {
    static ROADTYPE_ROAD = 0;
    static ROADTYPE_INVALID = 63;
    static function IsRoadTypeAvailable(t) { return t == GSRoad.ROADTYPE_ROAD; }
    static function SetCurrentRoadType(t) {
        if (GSRoad.IsRoadTypeAvailable(t)) ::cur_road_type = t;
    }
    static function GetCurrentRoadType() { return ::cur_road_type; }
    static function IsRoadDepotTile(t) {
        return GSRoad.IsRoadTypeAvailable(GSRoad.GetCurrentRoadType()) &&
            (t in ::depots);
    }
}
class GSStation {
    static function GetStationID(t) { return (t in ::stops) ? ::stops[t].sid : -1; }
    static function IsValidStation(sid) {
        return ::stations_ok && (sid in ::stations);
    }
    static function GetCargoWaiting(sid, _) {
        local stop = (sid in ::stations) ? ::stations[sid] : null;
        return stop == null ? -1 : stop.w;
    }
    static function GetCargoWaitingFrom(sid, from, _) {
        local stop = (sid in ::stations) ? ::stations[sid] : null;
        if (stop == null) return -1;
        return from == 0 ? stop.from0 : stop.from1;
    }
    static function GetCargoPlanned(sid, _) {
        local stop = (sid in ::stations) ? ::stations[sid] : null;
        return stop == null ? -1 : stop.pl;
    }
    static function GetCargoPlannedFrom(sid, from, _) {
        local stop = (sid in ::stations) ? ::stations[sid] : null;
        if (stop == null) return -1;
        return from == 0 ? stop.pl0 : stop.pl1;
    }
}
class GSIndustry {
    static function IsValidIndustry(ind) { return ind in ::industries; }
    static function GetStockpiledCargo(ind, _) {
        local rec = (ind in ::industries) ? ::industries[ind] : null;
        return rec == null ? -1 : rec.stock;
    }
    static function GetLastMonthProduction(ind, _) {
        local rec = (ind in ::industries) ? ::industries[ind] : null;
        return rec == null ? -1 : rec.prod;
    }
    static function GetLastMonthTransported(ind, _) {
        local rec = (ind in ::industries) ? ::industries[ind] : null;
        return rec == null ? -1 : rec.trans;
    }
    static function GetCargoLastAcceptedDate(ind, _) {
        return ind in ::industries ? ::last_accepted : -1;
    }
}
class GSCargoMonitor {
    static function GetIndustryPickupAmount(_, _, _, _) { return 0; }
    static function GetIndustryDeliveryAmount(_, _, _, _) { return 0; }
}
class GSEngine {
    static function IsBuildable(e) { return ::engine_ok && (e in ::engines); }
    static function GetCargoType(_) { return 1; }
    static function GetCapacity(_) { return ::engine_capacity; }
    static function GetPrice(_) { return ::engine_price; }
    static function GetMaxSpeed(_) { return ::engine_speed; }
    static function GetRunningCost(_) { return ::engine_display_running; }
}
class GSVehicle {
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
            v.speed = 30;
            v.in_depot = false;
            /* The running-cost world anchoring of record (the §4 partial
             * start day is charged from the latched (day, tick) instant). */
            ::run_start_day = ::day;
            ::run_start_tick = ::ticks;
        } else {
            v.state = VS_STOPPED;
            v.speed = 0;
        }
        return true;
    }
}
class GSOrder {
    static OF_NONE = 0;
    static OF_FULL_LOAD = 64;
    static function AreOrderFlagsValid(dest, flags) {
        /* N3: the two-argument 15.x destination form. */
        ::n3_calls.append([dest, flags]);
        return (flags == GSOrder.OF_NONE || flags == 128) && (dest in ::stops);
    }
    static function AppendOrder(id, dest, flags) {
        ::append_calls.append([dest, flags]);
        if (!(id in ::orders) || !(dest in ::stops)) return false;
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
class GSAccounting {
    constructor() { ::account++; }
    function GetCosts() {
        return (::account in ::tests) ? (::no_op ? 0 : ::quote_cost) : ::exec_cost;
    }
}
class GSTestMode { constructor() { ::tests[::account] <- true; } }
::n3_calls <- [];
::append_calls <- [];
::test_calls <- 0;
::real_calls <- 0;
::cur_vehicle <- -1;
::cur_company <- -1;
::stations_ok <- true;
::station_types <- {};
::station_types[0] <- 0x1;
::station_types[2] <- 0x1;
function json_cell(v) {
    if (v == null) return "null";
    if (typeof v == "bool") return v ? "true" : "false";
    if (typeof v == "string") return "\\"" + v + "\\"";
    if (typeof v == "array") {
        local out = "[";
        local first = true;
        foreach (e in v) {
            if (!first) out = out + ",";
            first = false;
            if (typeof e == "table") {
                local keys = "";
                foreach (kk, vv in e) {
                    if (typeof kk != "string") continue;
                    if (keys.len() > 0) keys = keys + ",";
                    keys = keys + "\\"" + kk + "\\":" + json_cell(vv);
                }
                out = out + "{" + keys + "}";
            } else {
                out = out + json_cell(e);
            }
        }
        return out + "]";
    }
    if (typeof v == "table") {
        local out = "{";
        local first = true;
        foreach (k, e in v) {
            if (typeof k != "string") continue;
            if (!first) out = out + ",";
            first = false;
            out = out + "\\"" + k + "\\":" + json_cell(e);
        }
        return out + "}";
    }
    return "" + v;
}
function last_reply_json() {
    local r = ::replies[::replies.len() - 1];
    local out = "{";
    local first = true;
    foreach (k, v in r) {
        if (typeof k != "string") continue;
        if (!first) out = out + ",";
        first = false;
        out = out + "\\"" + k + "\\":" + json_cell(v);
    }
    return out + "}";
}
"""


def civil_ymd(day: int) -> tuple[int, int, int]:
    """The anchored 1950 calendar of record (the module's calendar base)."""
    year, rem = divmod(day - cf._CALENDAR_BASE_DAY, 365)
    year += 1950
    month = 1
    for length in cf.DAYS_IN_MONTH_1950:
        if rem < length:
            return year, month, rem + 1
        rem -= length
        month += 1
    raise AssertionError("unreachable")


# --- The exported VM harness (the protocol-10 trio's export set, frame 11) ---


def build_vm(**knobs: int | bool) -> SQVM:
    """Fresh VM with the probe API fixture, the controlled world and the package."""
    vm = SQVM()
    vm.execute(API)
    vm.execute(WORLD)
    if knobs:
        assignments = []
        for name, value in knobs.items():
            literal = str(value).lower() if isinstance(value, bool) else str(value)
            assignments.append(f"::{name} = {literal};")
        vm.execute("\n".join(assignments))
    vm.execute(STUB)
    vm.execute((PACKAGE / "main.nut").read_text())
    vm.execute("::bridge <- D5CargoFlow2Proof();")
    return vm


def vm_root(vm: SQVM) -> dict[str, Any]:
    return vm.get_roottable()


def seed_stop(vm: SQVM, sid: int, w=0, from0=0, from1=0, pl=0, pl0=0, pl1=0) -> None:
    """Shape one pinned station's measured families between exchanges."""
    vm.execute(f"::cargoflow2_seed_stop({sid}, {w}, {from0}, {from1}, {pl}, {pl0}, {pl1});")


def seed_industry(vm: SQVM, ind: int, stock=0, prod=0, trans=0) -> None:
    """Shape one pinned industry's measured facts between exchanges."""
    vm.execute(f"::cargoflow2_seed_industry({ind}, {stock}, {prod}, {trans});")


def squirrel_table(payload: dict) -> str:
    pairs = []
    for key, value in payload.items():
        if value is None:
            literal = "null"
        elif isinstance(value, bool):
            literal = "true" if value else "false"
        elif isinstance(value, str):
            literal = '"' + value + '"'
        else:
            literal = str(value)
        pairs.append('"' + key + '" : ' + literal)
    return "{" + ",".join(pairs) + "}"


def base_request(**overrides) -> dict:
    """A valid-shaped raw protocol-11 site request payload for handler tests."""
    payload = {
        "protocol": 11,
        "op": "site",
        "request_id": "site-00",
        "plan": PRELAUNCH,
        "company": 0,
        "max_cost": 0,
        "pickup": 45748,
        "delivery": 50862,
        "depot": 45487,
        "engine": -1,
        "vehicle": -1,
        "expected_cost": 0,
        "order_index": -1,
        "order_flags": -1,
        "watch_days": -1,
        "offset": -1,
    }
    payload.update(overrides)
    return payload


_DRIVER = {"vehicle": -1}


def make_request(entry_index: int) -> cf.Cargoflow2Request:
    """Build one planned protocol-11 request at its driver state of record."""
    return work._cargoflow2_exchange_request(
        SCHEDULE[entry_index], PRELAUNCH, PLAN, _DRIVER
    )


def parse_from(request: cf.Cargoflow2Request, payload: dict) -> cf.Cargoflow2Readback:
    raw = json.dumps(payload, separators=(",", ":")).encode()
    return cf.Cargoflow2Readback.parse_for(request, raw)


def drive(vm: SQVM, request: cf.Cargoflow2Request) -> cf.Cargoflow2Readback:
    """Dispatch one request over the wire and parse the reply into Python."""
    replies = vm_root(vm)["replies"]
    before = len(replies)
    vm.execute("::bridge.Handle(" + request.to_bytes().decode() + ");")
    if len(vm_root(vm)["replies"]) == before:
        raise AssertionError(f"package dropped request {request.request_id}: no reply")
    vm.execute("::sniffer.last = last_reply_json();")
    raw = vm_root(vm)["sniffer"]["last"]
    assert len(raw.encode()) <= cf.MAX_CARGOFLOW2_RESPONSE_BYTES, (
        f"response for {request.request_id} exceeds "
        f"{cf.MAX_CARGOFLOW2_RESPONSE_BYTES} bytes"
    )
    return cf.Cargoflow2Readback.parse_for(request, raw.encode())


def raw_drive(vm: SQVM, payload: dict) -> dict | None:
    """Run one raw request-shaped dispatch; None when silently dropped."""
    before = len(vm_root(vm)["replies"])
    vm.execute("::bridge.Handle(" + squirrel_table(payload) + ");")
    if len(vm_root(vm)["replies"]) == before:
        return None
    return vm_root(vm)["replies"][before]


def expect_drop(vm: SQVM, payload: dict) -> None:
    assert raw_drive(vm, payload) is None


def reply(vm: SQVM, payload: dict) -> dict:
    """The raw reply table as a plain dict; a dropped request fails here."""
    table = raw_drive(vm, payload)
    assert table is not None  # a dropped request can never carry a reply
    return dict(table)


def settle_funds(vm: SQVM, value: int) -> None:
    """Pin the stub bank balance to an out-of-model funds figure."""
    vm.execute(f"::funds = {value};")


def witness_arrival(vm: SQVM, *, at_tick: int) -> None:
    """Queue the vehicle's first-arrival motion of record (the anchor latch)."""
    anchor = cf.CARGOFLOW2_PICKUP_TILE
    vm.execute(f"::motion_target <- {anchor};")
    vm.execute(
        f"::moves.append({{tick = {at_tick}, "
        "fn = function() { ::vehicles[::cur_vehicle].location = ::motion_target; }});"
    )


def sweep_days(vm: SQVM, rate: int) -> None:
    """Arm or pause the stub's day sweep: one ended economy day per Sleep."""
    vm.execute(f"::day_rate = {rate};")


def run_probe_vm() -> tuple[
    SQVM, list[tuple[cf.Cargoflow2Request, cf.Cargoflow2Readback]], dict
]:
    """The exact 25 planned exchanges in order (the production path offline).

    The stub's own funds arithmetic (``cargoflow2_stub_fees``) is the world's
    fee walk; the wire contract's zero-residual funds fence reconciles every
    exchange against the model of record — two independent implementations
    agree or the run halts. The stub carries the right run of fees so every
    reconcile passes: 485221 at the purchase and the daily/monthly stairway
    through the two crossed 1950 boundaries.
    """
    global _DRIVER
    _DRIVER = {"vehicle": -1}
    vm = build_vm()
    sweep_days(vm, 0)
    witness_arrival(vm, at_tick=40)
    exchanges: list[tuple[cf.Cargoflow2Request, cf.Cargoflow2Readback]] = []
    for index, row in enumerate(SCHEDULE):
        if row["op"] == "flow" and int(row["offset"]) > 0:
            sweep_days(vm, 1)
        request = make_request(index)
        readback = drive(vm, request)
        probes = cf.cargoflow2_phase_outcome(
            exchanges + [(request, readback)], prelaunch_digest=PRELAUNCH, plan=PLAN
        )
        assert probes["failed"] is None, (row["exchange"], probes["failed"])
        exchanges.append((request, readback))
        if row["op"] == "purchase":
            _DRIVER["vehicle"] = readback.vehicle
    phase = cf.cargoflow2_phase_outcome(exchanges, prelaunch_digest=PRELAUNCH, plan=PLAN)
    return vm, exchanges, phase


# --- The §4 funds walk: the favored funds trajectory of record ---------------


def _exchange_day(row: dict, *, arrival_day: int) -> int:
    if row["op"] == "arrive-watch":
        return arrival_day
    if row["op"] in ("flow", "finance", "finish"):
        return arrival_day + int(row["offset"])
    return cf.CARGOFLOW2_LAUNCH_DAY


def _exchange_tick(
    row: dict, *, start_tick: int, arrival_tick: int, sample_tick: int
) -> int:
    if row["op"] == "arrive-watch":
        return arrival_tick
    if row["op"] in ("flow", "finance", "finish"):
        return sample_tick
    return start_tick


def funds_walk(
    income_by_id: dict[str, int] | None = None,
    *,
    start_tick: int = TICK_OF_RECORD,
    arrival_tick: int = 40,
    sample_tick: int = 70,
    arrival_day: int = ANCHOR,
) -> tuple[dict[str, int], cf.Cargoflow2FundsModel]:
    """The modeled funds level at every exchange of the attempt.

    This is a secondary strip of the model of record walking exactly one
    advance per exchange in read order — the caller's readback funds figures
    come from here, so the §4.4 zero-residual fence inside
    ``cargoflow2_phase_outcome`` reconciles them against its own model
    construction with residual 0 by construction. Diverging by a unit at
    one exchange (the diverge knob) re-arms the fence and halts.
    """
    income_by_id = dict(income_by_id or {})
    model = cf.Cargoflow2FundsModel(
        start_funds=cf.CARGOFLOW2_START_FUNDS, purchase_quote=QUOTE
    )
    observed: dict[str, int] = {}
    for exchange_id in cf.CARGOFLOW2_EXCHANGE_IDS:
        row = SCHEDULE_BY_ID[exchange_id]
        day = _exchange_day(row, arrival_day=arrival_day)
        tick = _exchange_tick(
            row,
            start_tick=start_tick,
            arrival_tick=arrival_tick,
            sample_tick=sample_tick,
        )
        income = int(income_by_id.get(exchange_id, 0))
        if row["op"] == "purchase":
            model.advance(exchange_id, day, tick, income)
            model.debit_purchase()
            observed[exchange_id] = model.funds
            continue
        observed[exchange_id] = model.advance(exchange_id, day, tick, income)
        if row["op"] == "engine":
            model.admit_running_cost(ENGINE_RUNNING_DISPLAY)
        elif row["op"] == "start":
            model.start_vehicle(day, tick)
    return observed, model


SCHEDULE_BY_ID = {row["exchange"]: row for row in SCHEDULE}

# the flow rows that carry ended-day running rows in the funds walk
CARGOFLOW2_FLOW_ROW_IDS = tuple(f"flow-{index:02d}" for index in range(1, 12))


def _latch(
    kind: cf.Cargoflow2LatchKind, day: int, tick: int, cargo: int
) -> cf.Cargoflow2Latch:
    return cf.Cargoflow2Latch(kind=kind, day=day, tick=tick, cargo=cargo)


def default_stock_bay(unload_at: int | None) -> list[int]:
    """The bay-acceptance series of record: rise after unload, later drain."""
    if unload_at is None:
        return [0] * 12
    return [0, 0, 0, 0, 10, 20, 15, 10, 8, 6, 5, 5]


def built_ladder(
    *,
    wait_from: int | None = 1,
    queue_size: int = 12,
    load_at: int | None = 1,
    depart_at: int | None = 2,
    bay_at: int | None = 3,
    unload_at: int | None = 3,
    latch_cargo: int = 8,
    trans_from: int | None = 4,
    trans_amount: int = 40,
    stock_bay: list[int] | None = None,
    income_at: int | None = 2,
    income_step: int = 300,
    finance_ok: bool = True,
    diverge_at: str | None = None,
    divergence: int = 1,
    arrival_day: int = ANCHOR,
    start_tick: int = TICK_OF_RECORD,
    arrival_tick: int = 40,
    sample_tick: int = 70,
) -> list[tuple[cf.Cargoflow2Request, cf.Cargoflow2Readback]]:
    """One complete synthetic protocol-11 attempt ladder with its funds walk.

    Defaults shape the §7 five-stage happy cycle of record (a queue filled
    after the witnessed anchor, a load, a loaded departure, a bay arrival,
    an unload with the accepted pile rising and later draining, a positive
    income delta and a positive finance delivered read). Each knob re-arms
    one §5.5 failure class precisely; the funds walk keeps every exchange
    inside the §4 model until ``diverge_at`` re-arms the fence.
    """
    if stock_bay is None:
        stock_bay = default_stock_bay(unload_at)
    assert len(stock_bay) == 12

    income_series: list[int] = []
    base_income = 0
    for index in range(12):
        if income_at is not None and index >= income_at:
            base_income += income_step
        income_series.append(base_income)
    income_by_id = {
        f"flow-{index:02d}": int(income) for index, income in enumerate(income_series)
    }
    observed, _ = funds_walk(
        income_by_id,
        start_tick=start_tick,
        arrival_tick=arrival_tick,
        sample_tick=sample_tick,
        arrival_day=arrival_day,
    )

    latches_by_id: dict[int, list[cf.Cargoflow2Latch]] = {}
    for kind, at in (
        ("load", load_at),
        ("departure", depart_at),
        ("arrival_bay", bay_at),
        ("unload", unload_at),
    ):
        if at is None:
            continue
        day = arrival_day + int(cf.CARGOFLOW2_FLOW_OFFSETS[at])
        latches_by_id.setdefault(at, []).append(
            _latch(kind, day, sample_tick, latch_cargo)
        )

    ladder: list[tuple[cf.Cargoflow2Request, cf.Cargoflow2Readback]] = []
    state = dict(vehicle=-1)
    request_table = work.cargoflow2_request_table(PLAN, PRELAUNCH, vehicle=VEHICLE)
    for index, request in enumerate(request_table):
        exchange_id = request.request_id
        row = SCHEDULE_BY_ID[exchange_id]
        op = row["op"]
        funds = int(observed[exchange_id])
        if diverge_at == exchange_id:
            funds += divergence
        if op == "purchase":
            state["vehicle"] = VEHICLE
        day = _exchange_day(row, arrival_day=arrival_day)
        tick = _exchange_tick(
            row,
            start_tick=start_tick,
            arrival_tick=arrival_tick,
            sample_tick=sample_tick,
        )
        kwargs: dict[str, Any] = {}
        if op == "site":
            kwargs = dict(
                cargo=cf.CARGOFLOW2_CARGO,
                pickup_sid=cf.CARGOFLOW2_PICKUP_SID,
                bay_sid=cf.CARGOFLOW2_BAY_SID,
                pickup_industry=cf.CARGOFLOW2_PICKUP_IND,
                bay_industry=cf.CARGOFLOW2_BAY_IND,
            )
            cost = 0
        elif op == "engine":
            kwargs = dict(
                cargo=cf.CARGOFLOW2_CARGO,
                capacity=cf.CARGOFLOW2_CAPACITY,
                price=cf.CARGOFLOW2_PURCHASE_QUOTE,
                max_speed=cf.CARGOFLOW2_MAX_SPEED,
                running_cost=ENGINE_RUNNING_DISPLAY,
            )
            cost = 0
        elif op == "purchase":
            cost = QUOTE
        elif op == "vread":
            cost = 0
            kwargs = dict(
                owner=0,
                location=cf.CARGOFLOW2_DEPOT_TILE,
                capacity=cf.CARGOFLOW2_CAPACITY,
                cargo=0,
                state="IN_DEPOT",
                in_depot=True,
                speed=0,
                load=0,
            )
        elif op == "order":
            cost = 0
            wanted = (
                (cf.CARGOFLOW2_PICKUP_TILE, cf.CARGOFLOW2_ORDER_PICKUP_FLAGS, True)
                if int(row["order_index"]) == 0
                else (cf.CARGOFLOW2_BAY_TILE, cf.CARGOFLOW2_ORDER_DELIVERY_FLAGS, True)
            )
            kwargs = dict(dest=wanted[0], flags=wanted[1], goto=wanted[2])
        elif op == "order-read":
            cost = 0
            kwargs = dict(
                order_len=2,
                dest0=cf.CARGOFLOW2_PICKUP_TILE,
                flags0=cf.CARGOFLOW2_ORDER_PICKUP_FLAGS,
                goto0=True,
                dest1=cf.CARGOFLOW2_BAY_TILE,
                flags1=cf.CARGOFLOW2_ORDER_DELIVERY_FLAGS,
                goto1=True,
            )
        elif op == "monitor":
            cost = 0
            kwargs = dict(pickup_amount=0, delivery_amount=0)
        elif op == "start":
            cost = 0
            kwargs = dict(state="IN_DEPOT", speed=0)
        elif op == "arrive-watch":
            cost = 0
            kwargs = dict(
                anchor=arrival_day,
                location=cf.CARGOFLOW2_PICKUP_TILE,
                load=0,
                latches=(
                    _latch("arrival_pickup", arrival_day, arrival_tick, 0),
                ),
            )
        elif op == "flow":
            cost = 0
            findex = int(exchange_id.rsplit("-", 1)[1])
            year, month, day_of_month = civil_ymd(day)
            moved = depart_at is not None and findex > int(depart_at)
            kwargs = dict(
                anchor=arrival_day,
                year=year,
                month=month,
                day_of_month=day_of_month,
                stock_pickup=-1,
                stock_bay=int(stock_bay[findex]),
                wait_pickup=(
                    queue_size if wait_from is not None and findex >= int(wait_from) else 0
                ),
                wait_pickup_from0=(
                    queue_size if wait_from is not None and findex >= int(wait_from) else 0
                ),
                wait_pickup_from1=0,
                wait_bay=0,
                wait_bay_from0=0,
                wait_bay_from1=0,
                count_pickup=0,
                count_bay=0,
                planned_pickup_from0=0,
                planned_pickup_from1=0,
                planned_bay_from0=0,
                planned_bay_from1=0,
                prod_pickup=104,
                prod_bay=-1,
                trans_pickup=(
                    trans_amount
                    if trans_from is not None and findex >= int(trans_from) else 0
                ),
                trans_bay=0,
                location=(cf.CARGOFLOW2_BAY_TILE if moved else cf.CARGOFLOW2_PICKUP_TILE),
                load=0,
                in_depot=False,
                speed=30,
                delivered=0,
                latches=tuple(latches_by_id.get(findex, ())),
            )
        elif op == "finance":
            cost = 0
            kwargs = dict(
                anchor=arrival_day,
                delivered=(8 if finance_ok else 0),
                last_accepted=(day - 3),
            )
        else:  # finish
            cost = 0
            kwargs = dict(
                anchor=arrival_day,
                state="IN_DEPOT",
                speed=0,
                in_depot=True,
                stop_issued=False,
            )
        ladder.append(
            (
                request,
                cf.Cargoflow2Readback(
                    op=op,
                    request_id=exchange_id,
                    plan=PRELAUNCH,
                    company=PLAN.company,
                    max_cost=request.max_cost,
                    pickup=request.pickup,
                    delivery=request.delivery,
                    depot=request.depot,
                    engine=request.engine,
                    vehicle=(VEHICLE if state["vehicle"] >= 0 else -1),
                    expected_cost=request.expected_cost,
                    order_index=request.order_index,
                    order_flags=request.order_flags,
                    watch_days=request.watch_days,
                    offset=request.offset,
                    status=cast(
                        cf.Cargoflow2Status,
                        cf._CARGOFLOW2_SUCCESS_STATUS[cast(cf.Cargoflow2Op, op)],
                    ),
                    funds=funds,
                    cost=cost,
                    income=int(income_by_id.get(exchange_id, 0)),
                    tick=tick,
                    day=day,
                    **kwargs,
                ),
            )
        )
    return ladder


# --- The pinned schedule and plan (drift gates) ------------------------------


_WIDEST_REQUEST_ID = "purchase-00"
_REQUEST_DIGESTS: dict[str, str] = {
    "site-00": "becf98ff066dfb7ad160a9e819bf4ad58815d90a2f5b79a2349a90accf53b304",
    "engine-00": "acfd21cda7c3aa165b4d21ed1f40e58e4ac8fcdda30f18cb6b4e4c674c5af1e7",
    "purchase-00": "1723098ab130362ca0c30e16be9d3573c75c9424e42c8db88ef348e8ed530b38",
    "vread-00": "3114f276fe1c2624caf5801dc2507eb03951a72f63cc0dace74c72ff3cc49eac",
    "order-00": "a41700cf9a4cd1944223958f5b7589793bbedf80c84a1a2007c97efb139caaab",
    "order-01": "c129f27d9b749c4888a38d9ca8cdf63ec3e547384cffe5460731639302e760b7",
    "order-read-00": "cf2753f63910e74b89583035962d7d18a48aebbe9e45aa34e0afd2f54f6e9946",
    "monitor-00": "38decd2647b387f75a427a7f8428cff1f140d16edc2e23f2b7ae4cf125319584",
    "start-00": "96b7a6831bf934293ade87b137245b74b086adf2f4ad921bd81a5865e0c08b99",
    "vread-01": "c3ce5f3c6f9f0f495dedfcba2edf5a81a80dafa17c1ca05702c93aab2f31f642",
    "arrive-00": "b420e6c64f9297c03c880e980a36be376205f018018fcc5c7d29cb61dacf8b6c",
    "flow-00": "dcae4f9bf0244d28bb8fef039542aaa0330853278df052341c25b1f4fe546e5b",
    "flow-01": "4731a0dc70c919b0678a02ea8dacd04a1e62cfa28ecb899b7742e8d120fdd4dd",
    "flow-02": "df74f71d3adf76541ec8c28a26c07466ae3864dabfc8cadb2d6dfe1fd160a559",
    "flow-03": "e23c69a51703edb113b9e9e6e7ac7d8f2427bb53df63b97f84190fce33ee2e01",
    "flow-04": "ad3b51b128bda9aa80165e36ba70b9db67ffecb85f6606f1f5c8118ee45959a5",
    "flow-05": "cb9b4190ac7bd1cb50a9f57ec6995779631d6d156d8b3c2a689d2e00a1ba1d2f",
    "flow-06": "ac4c8c78b2a2c436e9acd5cad6bde042b6b67300269e6034c22c6bba1992f52f",
    "flow-07": "1d95835b5bd032769aff7bac3937bb5620ac0e35c1a717f66fde9d6fdbae8238",
    "flow-08": "43ab6462bd9fcc3ee7ae7c84a7c5842bfcb100bb7a579552e8467f191f58e667",
    "flow-09": "32bfd602bc55c4f2cf879e51667423b070468a6bb4e64c7a2cd7f6e66b071d83",
    "flow-10": "97fb6d0ad679ada8718a237812f28c1a0d73bc9e817e22a8393fd3f6fee0166a",
    "flow-11": "6fededb2b16cd10c9ffca6cc93eb26ed08abc9f73b56b79391ddf2dfe2e715d9",
    "finance-00": "1b234f3351e5c3cb001c0c8cdb57194cf3b5db92a3acc59aa3b73eaa3e4e6a64",
    "finish-00": "a67185c79d51fbc8bb43b79aeb86cdaaa54eb22cfcbee2b0a63afddf82922d0d",
}


def test_pinned_schedule_constants():
    assert cf.CARGOFLOW2_PROTOCOL == 11
    assert cf.CARGOFLOW2_COMPANY == 0
    assert cf.CARGOFLOW2_CARGO == 1
    assert cf.CARGOFLOW2_ENGINE == 123
    assert cf.CARGOFLOW2_CAPACITY == 20
    assert cf.CARGOFLOW2_MAX_SPEED == 48
    assert cf.CARGOFLOW2_RUNNING_DISPLAY == 421
    assert cf.CARGOFLOW2_PURCHASE_QUOTE == QUOTE == 4429
    assert cf.CARGOFLOW2_ENGINE_MAX_COST == 5000
    assert cf.CARGOFLOW2_START_FUNDS == FUNDS == 489650
    assert (cf.CARGOFLOW2_PICKUP_TILE, cf.CARGOFLOW2_BAY_TILE) == (45748, 50862)
    assert cf.CARGOFLOW2_DEPOT_TILE == 45487
    assert (cf.CARGOFLOW2_PICKUP_SID, cf.CARGOFLOW2_BAY_SID) == (0, 2)
    assert (cf.CARGOFLOW2_PICKUP_IND, cf.CARGOFLOW2_BAY_IND) == (0, 1)
    assert (cf.CARGOFLOW2_LAUNCH_DAY, cf._CALENDAR_BASE_DAY) == (712228, 712223)
    assert (cf.CARGOFLOW2_ARRIVE_MAX_DAYS, cf.CARGOFLOW2_SPAN_DAYS) == (5, 55)
    assert cf.CARGOFLOW2_FLOW_OFFSETS == tuple(range(0, 60, 5))
    assert cf.CARGOFLOW2_TAIL_OFFSET == 55
    assert cf.CARGOFLOW2_LATCH_LIMIT == 8
    assert (cf.CARGOFLOW2_REQUEST_BUDGET, cf.CARGOFLOW2_DAY_BUDGET) == (32, 60)
    assert (cf.PLANNED_CARGOFLOW2_EXCHANGES, len(cf.CARGOFLOW2_EXCHANGE_IDS)) == (25, 25)
    assert cf.CARGOFLOW2_EXCHANGE_IDS == EXCHANGES
    assert (cf.MAX_CARGOFLOW2_REQUEST_BYTES, cf.MAX_CARGOFLOW2_RESPONSE_BYTES) == (512, 1400)
    assert cf.cargoflow2_month_charge(712254) == 192
    assert cf.cargoflow2_month_charge(712282) == 192
    assert len(SCHEDULE) == 25


def test_status_family_of_record():
    expected_success = {
        "site": "READY",
        "engine": "READY",
        "purchase": "BUILT",
        "vread": "READ",
        "order": "ORDERED",
        "order-read": "ORDER_SET_VERIFIED",
        "monitor": "ARMED",
        "start": "STARTED",
        "arrive-watch": "ANCHORED",
        "flow": "READY",
        "finance": "FINANCE_VERIFIED",
        "finish": "PHASE_STOPPED",
    }
    assert cf._CARGOFLOW2_SUCCESS_STATUS == expected_success
    refusals = {
        "INVALID_COMPANY", "INVALID_SITE", "NO_ENGINE", "UNAVAILABLE_ENGINE",
        "ENGINE_PIN_MISMATCH", "INSUFFICIENT_FUNDS", "COST_LIMIT", "COST_CHANGED",
        "PAUSED", "ALREADY_ATTEMPTED", "STALE_ADMISSION", "UNSUPPORTED_NATIVE_FACT",
        "READBACK_MISMATCH", "OUT_OF_ORDER", "ARRIVE_TIMEOUT", "AUTHORITY_EXCEEDED",
        "LATCH_OVERFLOW",
    }
    assert cf._CARGOFLOW2_REFUSAL_STATUS == frozenset(refusals)
    assert cf._CARGOFLOW2_WINDOW_ECHO_STATUS == frozenset({"WINDOW_EXHAUSTED", "CLOCK_STALLED"})
    assert cf._CARGOFLOW2_WINDOW_ECHO_FIELDS == ("anchor", "tick", "day")
    covered = set(expected_success.values()) | refusals | cf._CARGOFLOW2_WINDOW_ECHO_STATUS
    literal = cf.Cargoflow2Status.__values__ if hasattr(cf.Cargoflow2Status, "__values__") else None
    if literal is not None:
        assert set(literal) == covered


def test_plan_pinned_and_digest_stable():
    plan = cf.cargoflow2_plan()
    assert plan.digest == PLAN.digest == REQUEST_PLAN_DIGEST
    assert plan.digest == cf.cargoflow2_plan().digest
    assert plan.company == 0
    assert plan.cargo == 1
    assert (plan.pickup, plan.pickup_front) == (45748, cf.CARGOFLOW2_PICKUP_FRONT_TILE)
    assert (plan.delivery, plan.delivery_front) == (50862, cf.CARGOFLOW2_BAY_FRONT_TILE)
    assert (plan.depot, plan.depot_front) == (45487, cf.CARGOFLOW2_DEPOT_FRONT_TILE)
    assert (plan.pickup_sid, plan.bay_sid, plan.pickup_industry, plan.bay_industry) == (0, 2, 0, 1)
    assert plan.engine == 123
    assert (plan.start_funds, plan.purchase_quote) == (489650, 4429)
    assert (plan.founding_loan, plan.interest_rate, plan.station_fee) == (100000, 2, 25)
    assert plan.launch_day == 712228
    assert (plan.arrive_max_days, plan.flow_span_days) == (5, 55)
    assert plan.schedule == cf.CARGOFLOW2_EXCHANGE_IDS
    assert plan.day_budget == 60


@pytest.mark.parametrize(
    "field, value",
    [
        ("company", 1),
        ("pickup", 45749),
        ("delivery", 50863),
        ("depot", 45488),
        ("engine", 124),
        ("start_funds", 489651),
        ("purchase_quote", 4430),
        ("launch_day", 712227),
        ("arrive_max_days", 6),
        ("flow_span_days", 54),
    ],
)
def test_plan_field_drift_refused(field, value):
    drifted = PLAN.model_copy(update={field: value})
    with pytest.raises(ValidationError):
        PLAN.model_validate(drifted.model_dump(mode="json"))


def test_exact_request_bytes_of_record():
    table = work.cargoflow2_request_table(PLAN, PRELAUNCH, vehicle=VEHICLE)
    for request in table:
        raw = request.to_bytes()
        assert len(raw) <= cf.MAX_CARGOFLOW2_REQUEST_BYTES
        decoded = hashlib.sha256(raw).hexdigest()
        assert decoded == _REQUEST_DIGESTS[request.request_id]


def test_request_echo_slots_of_record():
    table = work.cargoflow2_request_table(PLAN, PRELAUNCH, vehicle=VEHICLE)
    by_id = {request.request_id: request for request in table}
    site = by_id["site-00"]
    assert site.op == "site" and site.engine == -1 and site.vehicle == -1
    engine = by_id["engine-00"]
    assert engine.engine == cf.CARGOFLOW2_ENGINE and engine.vehicle == -1
    purchase = by_id["purchase-00"]
    assert purchase.expected_cost == QUOTE == cf.CARGOFLOW2_PURCHASE_QUOTE
    assert purchase.max_cost == cf.CARGOFLOW2_ENGINE_MAX_COST == 5000
    assert purchase.order_index == -1 and purchase.watch_days == -1 and purchase.offset == -1
    assert by_id["order-00"].order_index == 0
    assert by_id["order-00"].order_flags == cf.CARGOFLOW2_ORDER_PICKUP_FLAGS == 0
    assert by_id["order-01"].order_index == 1
    assert by_id["order-01"].order_flags == cf.CARGOFLOW2_ORDER_DELIVERY_FLAGS == 128
    assert by_id["arrive-00"].watch_days == cf.CARGOFLOW2_ARRIVE_MAX_DAYS == 5
    for row in SCHEDULE:
        request = by_id[row["exchange"]]
        if row["op"] in ("flow", "finance", "finish"):
            assert request.offset == int(row["offset"])
        else:
            assert request.offset == -1, row
        if row["op"] == "site":
            continue
        assert request.engine == cf.CARGOFLOW2_ENGINE, row
        if row["op"] in (
            "vread", "order", "order-read", "monitor", "start",
            "arrive-watch", "flow", "finance", "finish",
        ):
            assert request.vehicle == VEHICLE, row
        else:
            assert request.vehicle == -1, row


def test_worst_case_request_byte_audit_is_315():
    table = work.cargoflow2_request_table(PLAN, PRELAUNCH, vehicle=VEHICLE)
    sizes = {request.request_id: len(request.to_bytes()) for request in table}
    assert max(sizes.values()) == 315 == sizes[_WIDEST_REQUEST_ID]
    for exchange_id, size in sizes.items():
        assert size <= cf.MAX_CARGOFLOW2_REQUEST_BYTES, (exchange_id, size)


def test_request_verifier_accepts_the_clean_table():
    table = work.cargoflow2_request_table(PLAN, PRELAUNCH, vehicle=VEHICLE)
    for request in table:
        cf.verify_request_against_cargoflow2_plan(
            request, plan=PLAN, seal=PRELAUNCH
        )


@pytest.mark.parametrize("field, value", [
    ("plan", OTHER_PLAN),
    ("company", 1),
    ("pickup", 45749),
    ("delivery", 50863),
    ("depot", 45488),
    ("request_id", "site-x0"),
    ("op", "vread"),
])
def test_request_verifier_refusals(field, value):
    request = work.cargoflow2_request_table(PLAN, PRELAUNCH, vehicle=VEHICLE)[0]
    drifted = request.model_copy(update={field: value})
    with pytest.raises(ValueError):
        cf.verify_request_against_cargoflow2_plan(drifted, plan=PLAN, seal=PRELAUNCH)


def test_request_identity_domain_refusals():
    rows = [
        base_request(request_id="x" * 33),                     # request_id ceiling
        base_request(plan="short"),                            # 64-hex seal shape
        base_request(plan="A" * 64),                           # uppercase hex
        base_request(op="sample"),                             # protocol-11 op family
        base_request(engine=cf.CARGOFLOW2_ENGINE),             # site must stay quiet
        base_request(offset=0),                                # site must stay quiet
        base_request(op="vread", engine=123, vehicle=1, expected_cost=5),
        base_request(op="purchase", engine=123, expected_cost=4429, max_cost=5000,
                     order_index=0),                           # purchase phase echoes
        base_request(op="purchase", engine=123, expected_cost=4430, max_cost=5000),
        base_request(op="purchase", engine=123, expected_cost=4429, max_cost=4000),
    ]
    for payload in rows:
        with pytest.raises(ValidationError):
            cf.Cargoflow2Request.model_validate(payload)


def test_request_position_refusals():
    rows = [
        base_request(op="engine", engine=123, vehicle=1),      # engine never pitched
        base_request(op="order", engine=123, vehicle=1,
                     order_index=1, order_flags=cf.CARGOFLOW2_ORDER_PICKUP_FLAGS),
        base_request(op="arrive-watch", engine=123, vehicle=1,
                     watch_days=6, order_index=-1),
        base_request(op="flow", engine=123, vehicle=VEHICLE, watch_days=5,
                     order_index=-1),                          # flow offsets pinned per id
        base_request(op="flow-01", request_id="flow-01", engine=123,
                     vehicle=VEHICLE, offset=6),               # ladder arithmetic of record
        base_request(op="finance", request_id="finance-00", engine=123,
                     vehicle=VEHICLE, offset=54),              # tail offsets pinned
        base_request(op="finish", request_id="finish-00", engine=123,
                     vehicle=VEHICLE, offset=54),
        base_request(op="order-read", request_id="order-read-00", engine=123,
                     vehicle=VEHICLE, order_index=0),          # phase echo quiet rows
    ]
    for payload in rows:
        with pytest.raises(ValidationError):
            cf.Cargoflow2Request.model_validate(payload)


def test_parse_accepts_handler_shape():
    ladder = built_ladder()
    for request, readback in ladder:
        parsed = parse_from(request, readback.model_dump(mode="json"))
        assert parsed == readback
        assert parsed.request_id == request.request_id
        assert parsed.status == cf._CARGOFLOW2_SUCCESS_STATUS[request.op]
        assert parsed.digest == readback.digest


def test_parse_ceiling_duplicate_and_correlation():
    ladder = built_ladder()
    request, readback = ladder[0]
    body = json.dumps(readback.model_dump(mode="json"), separators=(",", ":")).encode()
    assert cf.Cargoflow2Readback.parse_for(request, body).request_id == "site-00"

    padded = body + b" " * (cf.MAX_CARGOFLOW2_RESPONSE_BYTES + 1)
    with pytest.raises(ValueError, match="exceeds 1400 bytes"):
        cf.Cargoflow2Readback.parse_for(request, padded)

    duplicate = body.replace(b'"protocol":11,', b'"protocol":11,"protocol":11,', 1)
    with pytest.raises(ValueError, match="duplicate response key"):
        cf.Cargoflow2Readback.parse_for(request, duplicate)

    other_request = ladder[1][0]
    with pytest.raises(ValueError, match="correlation mismatch"):
        cf.Cargoflow2Readback.parse_for(other_request, body)

    wrong_pins = request.model_copy(update={"pickup": 45749})
    with pytest.raises(ValueError, match="pin mismatch"):
        cf.Cargoflow2Readback.parse_for(wrong_pins, body)


def test_parse_success_requires_the_full_observation_set():
    ladder = built_ladder()
    by_id = {request.request_id: (request, readback) for request, readback in ladder}
    for exchange_id in (
        "site-00", "engine-00", "purchase-00", "vread-00", "order-00",
        "order-read-00", "monitor-00", "start-00", "arrive-00", "flow-04",
        "finance-00", "finish-00",
    ):
        request, readback = by_id[exchange_id]
        fields = cf._CARGOFLOW2_SUBSETS[readback.op]
        for missing in fields:
            payload = readback.model_dump(mode="json")
            payload[missing] = None
            # direct-validate plane (scalar JSON is safe; the one
            # array-of-objects member keeps its typed form unless it is
            # the member being refused)
            if missing != "latches":
                payload["latches"] = readback.latches
            with pytest.raises(ValidationError, match="success readback lacks"):
                cf.Cargoflow2Readback.model_validate(payload)


def test_refusal_frames_carry_no_observation_set():
    request = work.cargoflow2_request_table(PLAN, PRELAUNCH, vehicle=VEHICLE)[0]
    refusal = parse_from(request, dict(
        readback_body(request.op, request.request_id, status="PAUSED"),
        funds=FUNDS,
        cost=0,
    ))
    assert refusal.status == "PAUSED"

    payload = refusal.model_dump(mode="json")
    payload["cargo"] = cf.CARGOFLOW2_CARGO
    with pytest.raises(ValidationError, match="unclaimed observation set"):
        cf.Cargoflow2Readback.model_validate(payload)

    payload = refusal.model_dump(mode="json")
    payload["tick"] = 17
    with pytest.raises(ValidationError, match="unclaimed observation set"):
        cf.Cargoflow2Readback.model_validate(payload)


def readback_body(op: str, request_id: str, **overrides) -> dict:
    """A minimal correlated refusal/success-shaped raw body (the prelude only)."""
    body = {
        "protocol": 11,
        "op": op,
        "request_id": request_id,
        "plan": PRELAUNCH,
        "company": 0,
        "max_cost": 0,
        "pickup": 45748,
        "delivery": 50862,
        "depot": 45487,
        "engine": -1,
        "vehicle": -1,
        "expected_cost": 0,
        "order_index": -1,
        "order_flags": -1,
        "watch_days": -1,
        "offset": -1,
        "status": "OUT_OF_ORDER",
        "funds": 0,
        "cost": 0,
    }
    body.update(overrides)
    return body


def flow_request() -> cf.Cargoflow2Request:
    """The pinned flow-04 request of record (a post-purchase ladder row)."""
    return work.cargoflow2_request_table(PLAN, PRELAUNCH, vehicle=VEHICLE)[
        EXCHANGES.index("flow-04")
    ]


def test_window_echoes_parse_and_outside_fields_refuse():
    request = flow_request()
    # A refused flow frame still echoes its pinned phase pair.
    window = parse_from(request, readback_body(
        "flow", "flow-04", status="WINDOW_EXHAUSTED",
        engine=cf.CARGOFLOW2_ENGINE, vehicle=VEHICLE, offset=request.offset,
        plan=PRELAUNCH, anchor=ANCHOR, tick=48, day=ANCHOR + 20, funds=FUNDS,
    ))
    assert window.status == "WINDOW_EXHAUSTED"

    payload = window.model_dump(mode="json")
    payload["load"] = 5
    with pytest.raises(ValidationError, match="outside its window echo subset"):
        cf.Cargoflow2Readback.model_validate(payload)

    payload = window.model_dump(mode="json")
    payload["income"] = 300
    with pytest.raises(ValidationError, match="outside its window echo subset"):
        cf.Cargoflow2Readback.model_validate(payload)

    stalled = parse_from(request, readback_body(
        "flow", "flow-04", status="CLOCK_STALLED",
        engine=cf.CARGOFLOW2_ENGINE, vehicle=VEHICLE, offset=request.offset,
        plan=PRELAUNCH, anchor=ANCHOR, tick=48, day=ANCHOR + 21, funds=FUNDS,
    ))
    assert stalled.status == "CLOCK_STALLED"

    # The window echo family belongs to flow exchanges alone.
    with pytest.raises(ValidationError, match="window echo family belongs to flow"):
        cf.Cargoflow2Readback.model_validate(dict(
            readback_body("site", "site-00", status="WINDOW_EXHAUSTED"),
            anchor=ANCHOR, tick=1, day=ANCHOR, funds=FUNDS,
        ))


def test_ready_ladder_day_is_checked_against_the_anchor():
    by_id = {request.request_id: (request, readback) for request, readback in built_ladder()}
    request, readback = by_id["flow-04"]
    assert readback.anchor is not None
    assert readback.day == readback.anchor + 20

    payload = readback.model_dump(mode="json")
    payload["day"] = readback.anchor + 21
    payload["latches"] = readback.latches
    with pytest.raises(ValidationError, match="ladder day diverged: day - anchor = 21"):
        cf.Cargoflow2Readback.model_validate(payload)

    payload = readback.model_dump(mode="json")
    payload["anchor"] = readback.anchor - 1
    payload["latches"] = readback.latches
    with pytest.raises(ValidationError, match="ladder day diverged"):
        cf.Cargoflow2Readback.model_validate(payload)

    for exchange_id in ("finance-00", "finish-00"):
        request, readback = by_id[exchange_id]
        assert readback.day is not None and readback.anchor is not None
        assert readback.day == readback.anchor + 55
        payload = readback.model_dump(mode="json")
        payload["day"] = readback.day - 1
        with pytest.raises(ValidationError, match="ladder day diverged"):
            cf.Cargoflow2Readback.model_validate(payload)

    # Non-ladder exchanges are untouched by the arithmetic.
    request, readback = by_id["vread-00"]
    assert readback.anchor is None and readback.day == ANCHOR


@pytest.mark.parametrize("op, tweak, needle", [
    ("site", dict(vehicle=1), "site readback must not name an engine or vehicle"),
    ("site", dict(cargo=0), "the site readback re-pins the corridor cargo"),
    ("site", dict(bay_sid=3), "the site readback re-pins the corridor station ids"),
    ("site", dict(bay_industry=2), "the site readback re-pins the corridor industries"),
    ("engine", dict(price=4430), "the engine readback echoes its pinned price"),
    # The E111 inversion regression lock: a 256-scaled raw-sized running
    # cost refuses the readback (the old second-shift arithmetic would
    # have accepted it); any wrong display figure refuses the same way.
    ("engine", dict(running_cost=107776), "the engine running cost disagrees"),
    ("engine", dict(running_cost=420), "the engine running cost disagrees"),
    ("engine", dict(vehicle=1), "engine readback must not name a vehicle"),
    ("purchase", dict(vehicle=-1), "built purchase must name the pinned engine and vehicle"),
    ("purchase", dict(cost=4000), "built purchase must cost its pinned quote"),
    ("vread", dict(vehicle=-1), "post-purchase readbacks echo the pinned engine and vehicle"),
    ("vread", dict(engine=-1), "post-purchase readbacks echo the pinned engine and vehicle"),
    ("order", dict(flags=128), "the ordered order echoes its pinned flags"),
    ("order", dict(dest=50862), "the ordered order echoes its pinned stop tile"),
    ("order-read", dict(order_len=3), "the two-order loop carries exactly two orders"),
    ("order-read", dict(flags0=128), "order 0 drifted from the pinned pickup stop"),
    ("order-read", dict(flags1=0), "order 1 drifted from the pinned delivery bay"),
    ("arrive-watch", dict(anchor=ANCHOR - 1), "the arrival anchor is the arrival instant"),
    ("arrive-watch", dict(location=50862), "the first arrival latches at the pinned pickup stop"),
    ("arrive-watch", dict(load=5), "the first arrival carries the empty load of record"),
    ("arrive-watch", dict(latches=()), "the anchored arrival carries its own latch"),
    ("finish", dict(stop_issued=True), "the finish exchange issues no command in this attempt"),
])
def test_readback_echo_coherence_gates(op, tweak, needle):
    by_id = {request.request_id: (request, readback) for request, readback in built_ladder()}
    exchange_id = next(
        identifier
        for identifier, (_request, readback) in by_id.items()
        if readback.op == op
    )
    request, readback = by_id[exchange_id]
    payload = readback.model_dump(mode="json")
    payload.update(tweak)
    # direct-validate plane: the one array-of-objects member keeps its typed
    # tuple form (json dumps don't carry tuples)
    if isinstance(payload["latches"], list):
        payload["latches"] = tuple(payload["latches"])
    with pytest.raises(ValueError, match=needle):
        cf.Cargoflow2Readback.model_validate(payload)


def test_worst_case_response_byte_audit():
    """The widest per-op readback frame of record stays inside its ceiling.

    The wire plane is the handler's table shape: Squirrel cannot attach a
    null member, so the handler's widest legal frame is the None-free
    projection. The digest plane (canonical_bytes) adds the null members —
    an internal artifact, never wire bytes.
    """
    by_id = {request.request_id: (request, readback) for request, readback in built_ladder()}
    request, flow = by_id["flow-04"]
    payload = flow.model_dump(mode="json", exclude_none=True)
    payload["latches"] = tuple(
        dict(kind=kind, day=day, tick=tick, cargo=cargo)
        for kind, day, tick, cargo in (
            ("load", ANCHOR + 20, 70, 7),
            ("departure", ANCHOR + 20, 71, 7),
            ("arrival_bay", ANCHOR + 20, 72, 0),
            ("unload", ANCHOR + 20, 73, 7),
            ("arrival_pickup", ANCHOR + 20, 73, 0),
            ("load", ANCHOR + 21, 70, 13),
            ("departure", ANCHOR + 21, 71, 13),
            ("unload", ANCHOR + 22, 72, 13),
        )
    )
    widest = cf.Cargoflow2Readback.model_validate(payload)
    raw = json.dumps(
        widest.model_dump(mode="json", exclude_none=True), separators=(",", ":")
    ).encode()
    assert cf.CARGOFLOW2_LATCH_LIMIT == 8
    assert len(raw) <= cf.MAX_CARGOFLOW2_RESPONSE_BYTES, len(raw)
    parsed = cf.Cargoflow2Readback.parse_for(request, raw)
    assert len(parsed.latches) == cf.CARGOFLOW2_LATCH_LIMIT


# --- The §4 funds walk: the exact acquisition vector of record --------------


def test_funds_walk_exact_acquisition_vector():
    """The hand-carried funds vector of record, walked by the model alone.

    Every level was hand-derived from the §4 pins and reproduced by the
    real handler run (the stub fee engine agrees walk for walk): the
    purchase debit to 485221, the flow-01 level 485215 (the start-day
    partial 44-tick charge from the latched tick 30), the flow-06 level
    484994 (the Feb 1 charge 167+25 landed in its span), flow-11 at
    484774 (the Mar 1 charge in its span) and the tail rows frozen at
    the last level.
    """
    observed, model = funds_walk({})
    assert observed["site-00"] == 489650
    assert observed["engine-00"] == 489650
    assert observed["purchase-00"] == 485221
    assert observed["flow-00"] == 485221
    assert observed["flow-01"] == 485215
    assert observed["flow-02"] == 485209
    assert observed["flow-03"] == 485204
    assert observed["flow-04"] == 485198
    assert observed["flow-05"] == 485192
    assert observed["flow-06"] == 484994
    assert observed["flow-07"] == 484989
    assert observed["flow-08"] == 484983
    assert observed["flow-09"] == 484977
    assert observed["flow-10"] == 484971
    assert observed["flow-11"] == 484774
    assert observed["finance-00"] == 484774
    assert observed["finish-00"] == 484774
    assert model.running_cost == ENGINE_RUNNING_DISPLAY
    assert model.purchase_paid and model.started == (ANCHOR, TICK_OF_RECORD)


def test_funds_walk_running_rows_of_record():
    """The exact 8.8-carry whole rows: the start-day partial then full days.

    Row shape per ended day is ``(ended_day, running_ticks, whole_units)``:
    the start day runs 74 − 30 = 44 ticks from the latched instant, every
    later ended day runs the full 74. The two crossed 1950 boundaries
    show in the funds levels (flow-06 and flow-11), whole-unit and
    fraction-free, exactly one 192 each.
    """
    observed, model = funds_walk({})
    rows = dict(model.running_costs)
    assert [row for row in rows if row not in CARGOFLOW2_FLOW_ROW_IDS] == []
    flow_rows = rows["flow-01"]
    assert flow_rows[0] == (712228, 44, 1)
    assert [row for row in flow_rows[1:]] == [
        (712229, 74, 1),
        (712230, 74, 1),
        (712231, 74, 2),
        (712232, 74, 1),
    ]
    assert all(row[1] == 74 for rid, day_rows in rows.items() for row in day_rows[1:])
    assert list(rows) == ["flow-01", "flow-02", "flow-03", "flow-04", "flow-05", "flow-06",
                          "flow-07", "flow-08", "flow-09", "flow-10", "flow-11"]
    assert model.fraction in range(256)


def test_funds_model_refusals():
    """The model of record never loosens: repeat/misuse pins refuse."""
    from app.simulation.openttd.corridor_cargoflow2 import Cargoflow2FundsModel

    cold = Cargoflow2FundsModel(start_funds=FUNDS, purchase_quote=QUOTE)
    with pytest.raises(ValueError, match="no observation frontier"):
        cold.start_vehicle(ANCHOR, TICK_OF_RECORD)

    warm = Cargoflow2FundsModel(start_funds=FUNDS, purchase_quote=QUOTE)
    warm.advance("site-00", ANCHOR, 19, 0)
    warm.start_vehicle(ANCHOR, TICK_OF_RECORD)
    with pytest.raises(ValueError, match="already started"):
        warm.start_vehicle(ANCHOR, TICK_OF_RECORD)
    # §4 order of record: the raw lands at engine-00 before the start, so a
    # raw-less advance applies no running charge; the missing term is typed
    # by the funds fence instead (the real world charged it).
    assert warm.advance("flow-01", ANCHOR + 5, 70, 0) == FUNDS
    with pytest.raises(ValueError, match="funds diverged"):
        warm.reconcile(
            exchange_id="flow-01",
            day=ANCHOR + 5,
            tick=70,
            income=0,
            observed=FUNDS - 3,
        )

    warm.admit_running_cost(ENGINE_RUNNING_DISPLAY)
    with pytest.raises(ValueError, match="already pinned"):
        warm.admit_running_cost(ENGINE_RUNNING_DISPLAY)
    with pytest.raises(ValueError, match="inconsistent with its display figure"):
        Cargoflow2FundsModel(start_funds=FUNDS, purchase_quote=QUOTE).admit_running_cost(
            420
        )
    # The E111 inversion regression lock: the pinned display surface never
    # widens back to a 256-scaled raw — a raw-sized value refuses, never
    # admits (the old second-shift arithmetic would have accepted it).
    with pytest.raises(ValueError, match="inconsistent with its display figure"):
        Cargoflow2FundsModel(start_funds=FUNDS, purchase_quote=QUOTE).admit_running_cost(
            107776
        )
    with pytest.raises(ValueError, match="inconsistent with its display figure"):
        Cargoflow2FundsModel(start_funds=FUNDS, purchase_quote=QUOTE).admit_running_cost(
            0
        )

    warm.debit_purchase()
    assert warm.funds == FUNDS - QUOTE
    with pytest.raises(ValueError, match="already moved its pinned quote"):
        warm.debit_purchase()


def test_funds_walk_income_attr_of_record():
    """Income rides the observation instants entirely (no other term).

    The engine's own quarter-income reads are quarter-cumulative values;
    each flow instant from flow-02 onward attributes one more 300-unit
    delta, and the tail rows read the same cumulative quarter (delta 0),
    so the walk differs from the zero-income vector by exactly the
    cumulative attribution at every level.
    """
    income = {f"flow-{i:02d}": (max(0, i - 1) * 300) for i in range(12)}
    income["finance-00"] = 3000
    income["finish-00"] = 3000
    observed, _model = funds_walk(income)
    assert observed["flow-01"] == 485215  # before the first income delta
    assert observed["flow-02"] == 485209 + 300
    assert observed["flow-03"] == 485204 + 600
    assert observed["flow-04"] == 485198 + 900
    assert observed["flow-11"] == 484774 + 3000
    assert observed["finance-00"] == 484774 + 3000
    assert observed["finish-00"] == 484774 + 3000


# --- The §5.5 verdict slicing: knob matrix over the synthetic ladder --------


def phase_of(ladder):
    return cf.cargoflow2_phase_outcome(
        ladder, prelaunch_digest=PRELAUNCH, plan=PLAN
    )


def test_built_ladder_default_typed_delivery_verified():
    ladder = built_ladder()
    phase = phase_of(ladder)
    assert phase["failed"] is None
    assert phase["pending"] == []
    assert phase["verdict"]["verdict"] == "CARGOFLOW2_DELIVERY_VERIFIED"
    assert phase["anchor"] == ANCHOR
    assert len(phase["receipts"]) == 25
    assert phase["arrival"]["tick"] == 40


@pytest.mark.parametrize("knobs, expected", [
    ({}, "CARGOFLOW2_DELIVERY_VERIFIED"),
    (dict(wait_from=None, load_at=None, bay_at=None, unload_at=None,
            trans_from=None, income_at=None), "CARGOFLOW2_QUEUE_NEVER_FILLED"),
    (dict(bay_at=None, unload_at=None), "CARGOFLOW2_LOADED_NEVER_DELIVERED"),
    (dict(stock_bay=[0, 0, 0, 0, 5, 10, 10, 10, 10, 10, 10, 10]),
        "CARGOFLOW2_CONSUMPTION_UNOBSERVED"),
    (dict(trans_from=None, trans_amount=0), "CARGOFLOW2_GATE_UNDECIDED_INCOMPLETE"),
    (dict(income_at=None, income_step=0),
        "CARGOFLOW2_GATE_UNDECIDED_INCOMPLETE"),
    (dict(finance_ok=False), "CARGOFLOW2_GATE_UNDECIDED_INCOMPLETE"),
    (dict(load_at=2, depart_at=3, bay_at=4, unload_at=4),
        "CARGOFLOW2_DELIVERY_VERIFIED"),
])
def test_verdict_knob_matrix(knobs, expected):
    ladder = built_ladder(**knobs)
    for _request, readback in ladder:
        assert isinstance(readback, cf.Cargoflow2Readback)
    phase = phase_of(ladder)
    assert phase["verdict"]["verdict"] == expected, phase["verdict"]
    assert phase.get("failed") is None


def test_funds_divergence_halt_and_typing():
    ladder = built_ladder(diverge_at="flow-03", divergence=1)
    phase = phase_of(ladder)
    assert phase["failed"] is not None
    assert phase["failed"]["label"] == "flow-03"
    assert phase["failed"]["status"] == "READY"
    assert "funds diverged" in phase["failed"]["error"]
    assert phase["verdict"]["verdict"] == "CARGOFLOW2_FUNDS_DIVERGED"
    # earlier receipts are preserved; the diverged row keeps no receipt and
    # flow-04..finish stay pending
    assert len(phase["receipts"]) == EXCHANGES.index("flow-03")
    assert phase["pending"] == list(EXCHANGES[EXCHANGES.index("flow-03") + 1:])


def test_malformed_element_halts():
    ladder: list = built_ladder()
    index = EXCHANGES.index("flow-05")
    ladder[index] = (ladder[index][0], ValueError("torn frame bytes"))
    phase = phase_of(ladder)
    assert phase["failed"]["label"] == "flow-05"
    assert phase["failed"]["status"] == "MALFORMED"
    assert phase["failed"]["error"] == "torn frame bytes"
    assert phase["pending"] == list(EXCHANGES[index + 1:])


def test_wrong_seal_halts_with_verbatim_refusal():
    ladder = built_ladder()
    index = EXCHANGES.index("vread-00")
    request, readback = ladder[index]
    ladder[index] = (request.model_copy(update={"plan": OTHER_PLAN}), readback)
    phase = phase_of(ladder)
    assert phase["failed"]["label"] == "vread-00"
    assert phase["failed"]["error"] == (
        "request plan digest is not the staged prelaunch seal"
    )
    assert phase["pending"] == list(EXCHANGES[index + 1:])


def test_out_of_order_halts_with_verbatim_refusal():
    ladder = built_ladder()
    index = EXCHANGES.index("order-01")
    # the order-00 request presented at the order-01 position
    ladder[index] = (ladder[index - 1][0], ladder[index][1])
    phase = phase_of(ladder)
    assert phase["failed"]["label"] == "order-00"
    assert phase["failed"]["error"] == (
        "cargo-flow 2 exchange out of order: expected order-01"
    )
    assert phase["pending"] == list(EXCHANGES[EXCHANGES.index("order-01"):])


def test_non_purchase_cost_halts():
    ladder = built_ladder()
    index = EXCHANGES.index("vread-00")
    request, readback = ladder[index]
    drifted = readback.model_copy(update={"cost": 10})
    ladder[index] = (request, drifted)
    phase = phase_of(ladder)
    assert phase["failed"]["label"] == "vread-00"
    assert phase["failed"]["error"] == (
        "cargo-flow 2 exchanges outside the purchase observe at zero cost"
    )
    assert phase["pending"] == list(EXCHANGES[index + 1:])


def test_truncated_ladder_never_manufactures_success():
    """An unfinished ladder is undecided, never folded into a verdict."""
    ladder = built_ladder()[: EXCHANGES.index("flow-11") + 1]
    phase = phase_of(ladder)
    assert phase["failed"] is None
    assert phase["verdict"]["verdict"] == "CARGOFLOW2_GATE_UNDECIDED_INCOMPLETE"
    assert phase["pending"] == ["finance-00", "finish-00"]


def test_complete_ladder_sampling_of_record():
    """The ladder's monthly attribution and funds stairway of record."""
    ladder = built_ladder()
    by_id = {request.request_id: readback for request, readback in ladder}
    # the ladder's civil calendar attribution (the anchored 1950 calendar
    # of record): the launch day is Jan 6; both fee boundaries land inside
    # the sampled span.
    assert civil_ymd(ANCHOR) == (1950, 1, 6)
    assert civil_ymd(712254) == (1950, 2, 1)
    assert civil_ymd(712282) == (1950, 3, 1)
    assert by_id["flow-11"].day is not None
    assert civil_ymd(by_id["flow-11"].day) == (1950, 3, 2)
    # the funds stairway at the sampled instants (the model of record; the
    # default ladder's cumulative income attribution rides both levels)
    assert by_id["flow-06"].funds == 484994 + 1500 == 486494
    assert by_id["flow-11"].funds == 484774 + 3000 == 487774
    # this fixture's finance frame reads income 0 (its income_by_id carries
    # flow rows only), so its walk level unwinds the cumulative attribution
    assert by_id["finance-00"].funds == 484774
    # the last ladder row shares the finance row's economy day
    assert by_id["flow-11"].day == by_id["finance-00"].day


# --- The work gates of record ------------------------------------------------


def test_funds_model_gate_pin_table():
    gate = work.cargoflow2_funds_model_gate()
    assert gate["schema"] == "d5-cargoflow2-funds-model-of-record-v1"
    assert gate["start_funds"] == 489650
    assert gate["purchase_quote"] == 4429
    assert gate["founding_loan"] == 100000
    assert gate["interest_rate"] == 2
    assert gate["station_fee"] == 25
    assert gate["launch_day"] == 712228
    assert (gate["arrival_bound_days"], gate["flow_span_days"], gate["day_budget"]) == (5, 55, 60)
    assert "Feb 1 charge of record" in gate["statement"]
    # the gate re-derives the pinned founding construction (idempotent)
    assert work.cargoflow2_funds_model_gate() == gate


def test_retained_probe_rebound_hypotheses():
    hyp = work.cargoflow2_hypotheses()
    assert hyp["state"] == "RETAINED_PROBE_REBOUND"
    assert len(hyp["samples"]) == 7
    assert hyp["source"] == (
        "artifacts/experiments/d5-corridor-cargoflow-native-candidate-1/result.json"
    )
    retained = (REPO / hyp["source"]).read_bytes()
    assert hashlib.sha256(retained).hexdigest() == hyp["source_sha256"]
    rows = hyp["samples"]
    assert all(row["kind"] == "HYPOTHESIS" for row in rows)
    assert [row["offset"] for row in rows] == [0, 5, 10, 15, 20, 25, 30]
    for row in rows:
        assert row["stock_pickup"] == -1
        assert row["stock_bay"] == 0
        assert row["wait_pickup"] == 0
        assert row["wait_bay"] == 0
    assert "§5.2 item 3" in hyp["statement"]


# --- Ticket 07: the route-binding parameterization ---------------------------
#
# The corridor attempt contract is parameterized over the corridor route of
# record as its DEFAULT versioned binding instance (family versioning
# precedent — the schedule-version selector with per-version plan pins).
# This block binds the parameterization's external behavior: the recorded
# digests, pin rows and funds vector of the default binding stay byte-equal
# (the invariance locks of record), a non-default route binding derives its
# own consistent composition, and cross-version composition drift fails
# closed. Nothing here mutates native state; the only module state touched
# is a synthetic non-default binding registration, restored via monkeypatch.


_SCHEDULE_DIGEST_OF_RECORD = "5c0998f2d164198e2545ebd9709b2ae32afdbc3d4ef4dc8a7188a202e3f0bf2d"

# The default binding's pin rows of record — exactly the values the shipped
# attempt package's pin table carries for the route-sourced pins (the
# pin-table binding test binds the shipped table to the same values).
_DEFAULT_PIN_TABLE_OF_RECORD = {
    "pickup": 45748,
    "delivery": 50862,
    "depot_tile": 45487,
    "PICKUP_SID": 0,
    "BAY_SID": 2,
    "PICKUP_IND": 0,
    "BAY_IND": 1,
    "CARGOFLOW2_COMPANY": 0,
    "CARGOFLOW2_CARGO": 1,
    "ENGINE_PIN": 123,
    "ENGINE_QUOTE": 4429,
    "ENGINE_MAX_COST": 5000,
    "CAPACITY_PIN": 20,
    "SPEED_PIN": 48,
    "RUNNING_DISPLAY_PIN": 421,
    "OF_NONE": 0,
    "OF_NO_LOAD": 128,
    "LAUNCH_DAY": 712228,
    "ARRIVE_MAX_DAYS": 5,
    "ARRIVE_DEADLINE": 712233,
    "AUTHORITY_LAST_DAY": 712288,
}

# The §4 funds acquisition vector of record, walked whole (the exact
# purchase debit, the start-day partial, the two crossed 1950 boundaries,
# the income-free ladder).
_ACQUISITION_VECTOR_OF_RECORD = {
    "site-00": 489650,
    "engine-00": 489650,
    "purchase-00": 485221,
    "vread-00": 485221,
    "order-00": 485221,
    "order-01": 485221,
    "order-read-00": 485221,
    "monitor-00": 485221,
    "start-00": 485221,
    "vread-01": 485221,
    "arrive-00": 485221,
    "flow-00": 485221,
    "flow-01": 485215,
    "flow-02": 485209,
    "flow-03": 485204,
    "flow-04": 485198,
    "flow-05": 485192,
    "flow-06": 484994,
    "flow-07": 484989,
    "flow-08": 484983,
    "flow-09": 484977,
    "flow-10": 484971,
    "flow-11": 484774,
    "finance-00": 484774,
    "finish-00": 484774,
}


def test_default_binding_digests_pins_and_funds_vector_of_record():
    """The pinned-value locks of the parameterization: the corridor route of
    record's plan digest, staged schedule digest, pin rows and funds vector
    equal today's recorded values (zero semantic drift, whatever the
    parameterization adds)."""
    plan = cf.cargoflow2_plan()
    assert plan.digest == PLAN.digest == REQUEST_PLAN_DIGEST
    assert work.plan_digest_of(list(work.cargoflow2_schedule())) == _SCHEDULE_DIGEST_OF_RECORD
    pin_rows = {
        "pickup": cf.CARGOFLOW2_PICKUP_TILE,
        "delivery": cf.CARGOFLOW2_BAY_TILE,
        "depot_tile": cf.CARGOFLOW2_DEPOT_TILE,
        "PICKUP_SID": cf.CARGOFLOW2_PICKUP_SID,
        "BAY_SID": cf.CARGOFLOW2_BAY_SID,
        "PICKUP_IND": cf.CARGOFLOW2_PICKUP_IND,
        "BAY_IND": cf.CARGOFLOW2_BAY_IND,
        "CARGOFLOW2_COMPANY": cf.CARGOFLOW2_COMPANY,
        "CARGOFLOW2_CARGO": cf.CARGOFLOW2_CARGO,
        "ENGINE_PIN": cf.CARGOFLOW2_ENGINE,
        "ENGINE_QUOTE": cf.CARGOFLOW2_PURCHASE_QUOTE,
        "ENGINE_MAX_COST": cf.CARGOFLOW2_ENGINE_MAX_COST,
        "CAPACITY_PIN": cf.CARGOFLOW2_CAPACITY,
        "SPEED_PIN": cf.CARGOFLOW2_MAX_SPEED,
        "RUNNING_DISPLAY_PIN": cf.CARGOFLOW2_RUNNING_DISPLAY,
        "OF_NONE": cf.CARGOFLOW2_ORDER_PICKUP_FLAGS,
        "OF_NO_LOAD": cf.CARGOFLOW2_ORDER_DELIVERY_FLAGS,
        "LAUNCH_DAY": cf.CARGOFLOW2_LAUNCH_DAY,
        "ARRIVE_MAX_DAYS": cf.CARGOFLOW2_ARRIVE_MAX_DAYS,
        "ARRIVE_DEADLINE": cf.CARGOFLOW2_LAUNCH_DAY + cf.CARGOFLOW2_ARRIVE_MAX_DAYS,
        "AUTHORITY_LAST_DAY": cf.CARGOFLOW2_LAUNCH_DAY + cf.CARGOFLOW2_DAY_BUDGET,
    }
    assert pin_rows == _DEFAULT_PIN_TABLE_OF_RECORD
    observed, model = funds_walk({})
    assert observed == _ACQUISITION_VECTOR_OF_RECORD
    assert model.purchase_paid and model.started == (ANCHOR, TICK_OF_RECORD)


def _route_two() -> cf.Cargoflow2RouteBinding:
    """The parameterization's synthetic non-default binding: a second,
    internally-consistent route instance of the same contract family (its
    own bay station, engine census and close-out funds) — never a binding
    of this world of record, and registered only inside these tests."""
    return cf.Cargoflow2RouteBinding(
        route_version=2,
        company=0,
        cargo=1,
        pickup=45748,
        pickup_front=45747,
        pickup_sid=0,
        pickup_industry=0,
        delivery=51119,
        delivery_front=51118,
        bay_sid=3,
        bay_industry=1,
        depot=45487,
        depot_front=45743,
        engine=124,
        engine_max_cost=5000,
        purchase_quote=4700,
        engine_running_display=500,
        engine_capacity=30,
        engine_max_speed=40,
        order_pickup_flags=0,
        order_delivery_flags=128,
        start_funds=475000,
        founding_loan=100000,
        interest_rate=2,
        station_fee=25,
        launch_day=712228,
        arrive_max_days=5,
        flow_span_days=55,
    )


@pytest.fixture
def route_two(monkeypatch: pytest.MonkeyPatch) -> cf.Cargoflow2RouteBinding:
    """Register the synthetic non-default binding; restored on teardown."""
    binding = _route_two()
    monkeypatch.setitem(cf.CARGOFLOW2_ROUTE_BINDINGS, binding.route_version, binding)
    return binding


def test_route_binding_selector_and_map_of_record():
    """The version selector and the versioned binding map live in the
    contract module; the route of record is the map's only pre-registered
    default, and a foreign binding id refuses (no invented instance)."""
    binding = cf.cargoflow2_route_binding()
    assert cf.CARGOFLOW2_SCHEDULE_VERSION == 1
    assert binding is cf.CARGOFLOW2_ROUTE_BINDINGS[1]
    assert len(cf.CARGOFLOW2_ROUTE_BINDINGS) == 1
    assert binding.route_version == 1
    assert (binding.pickup, binding.pickup_front, binding.pickup_sid, binding.pickup_industry) == (
        45748, 45747, 0, 0,
    )
    assert (binding.delivery, binding.delivery_front, binding.bay_sid, binding.bay_industry) == (
        50862, 50863, 2, 1,
    )
    assert (binding.depot, binding.depot_front) == (45487, 45743)
    assert (binding.company, binding.cargo, binding.engine) == (0, 1, 123)
    with pytest.raises(ValueError, match="no registered corridor route binding"):
        cf.cargoflow2_route_binding(2)


def test_route_binding_registration_fail_closed(route_two: cf.Cargoflow2RouteBinding):
    """The admission seam registers one versioned binding instance and
    refuses re-registration of an occupied binding id."""
    assert cf.cargoflow2_route_binding(2) is route_two
    with pytest.raises(ValueError, match="already registered"):
        cf.cargoflow2_register_route_binding(route_two)
    with pytest.raises(ValueError, match="already registered"):
        cf.cargoflow2_register_route_binding(cf.CARGOFLOW2_ROUTE_OF_RECORD)
    assert set(cf.CARGOFLOW2_ROUTE_BINDINGS) == {1, 2}


def test_nondefault_route_binding_derives_its_own_schedule_plan_and_pin_table(
    route_two: cf.Cargoflow2RouteBinding,
):
    """A non-default binding derives its OWN consistent composition: the
    ladder instrument rows, a plan whose digest carries its own pins, and
    its own pin-table rows; the default binding derives the same rows and
    exactly today's recorded digests. The ladder ids are the binding-
    independent instrument of record — the route identity lives in the
    plan's pins, never in a relabeled schedule."""
    default = cf.cargoflow2_route_binding(1)
    default_rows = cf.cargoflow2_schedule_rows(default)
    assert default_rows == list(work.cargoflow2_schedule())
    assert work.plan_digest_of(default_rows) == _SCHEDULE_DIGEST_OF_RECORD
    assert cf.cargoflow2_plan(binding=default).digest == REQUEST_PLAN_DIGEST

    plan_two = cf.cargoflow2_plan(binding=route_two)
    assert plan_two.schema_version == 2
    assert plan_two.schedule == cf.CARGOFLOW2_EXCHANGE_IDS
    assert (plan_two.pickup, plan_two.pickup_front) == (
        route_two.pickup, route_two.pickup_front,
    )
    assert (plan_two.delivery, plan_two.delivery_front) == (
        route_two.delivery, route_two.delivery_front,
    )
    assert (plan_two.pickup_sid, plan_two.bay_sid) == (route_two.pickup_sid, route_two.bay_sid)
    assert (plan_two.pickup_industry, plan_two.bay_industry) == (
        route_two.pickup_industry, route_two.bay_industry,
    )
    assert plan_two.engine == route_two.engine == 124
    assert plan_two.start_funds == route_two.start_funds == 475000
    # deterministic, and never aliased onto the recorded composition
    assert cf.cargoflow2_plan(binding=route_two).digest == plan_two.digest
    assert plan_two.digest != REQUEST_PLAN_DIGEST

    rows_two = cf.cargoflow2_schedule_rows(route_two)
    assert rows_two == default_rows
    assert work.plan_digest_of(rows_two) == _SCHEDULE_DIGEST_OF_RECORD

    table_one = cf.cargoflow2_pin_table(default)
    table_two = cf.cargoflow2_pin_table(route_two)
    assert table_one == _DEFAULT_PIN_TABLE_OF_RECORD
    assert table_two != table_one
    assert table_two["ENGINE_PIN"] == 124
    assert table_two["ENGINE_QUOTE"] == 4700
    assert table_two["RUNNING_DISPLAY_PIN"] == 500
    assert (table_two["BAY_SID"], table_two["BAY_IND"]) == (3, 1)
    assert table_two["delivery"] == 51119
    assert (table_two["LAUNCH_DAY"], table_two["ARRIVE_MAX_DAYS"]) == \
        (route_two.launch_day, route_two.arrive_max_days)
    for name, value in (
        ("PICKUP_SID", 0),
        ("CARGOFLOW2_COMPANY", 0),
        ("OF_NONE", 0),
        ("OF_NO_LOAD", 128),
        ("ARRIVE_DEADLINE", 712233),
    ):
        assert table_two[name] == value, name


def test_cross_version_plan_composition_drift_refused(route_two: cf.Cargoflow2RouteBinding):
    """Mixing a schedule from one version with pins/digests of another
    fails closed at the plan gate: a plan cannot carry one binding's pins
    under another binding's version label, in either direction."""
    plan_two = cf.cargoflow2_plan(binding=route_two)
    mixed_forward = plan_two.model_dump(mode="json")
    mixed_forward["schedule"] = tuple(mixed_forward["schedule"])
    mixed_forward["schema_version"] = 1
    with pytest.raises(
        ValidationError,
        match="bay pins drifted from the depot-chain corridor",
    ):
        cf.Cargoflow2Plan.model_validate(mixed_forward)
    mixed_back = PLAN.model_dump(mode="json")
    mixed_back["schedule"] = tuple(mixed_back["schedule"])
    mixed_back["schema_version"] = 2
    with pytest.raises(
        ValidationError,
        match="bay pins drifted from the depot-chain corridor",
    ):
        cf.Cargoflow2Plan.model_validate(mixed_back)


def test_funds_model_wiring_follows_its_own_binding(route_two: cf.Cargoflow2RouteBinding):
    """The funds-model wiring of record is parameterized too: a model built
    for one binding carries that binding's own founding pins and admits
    only its own census display figure — a foreign binding's display figure
    (a cross-version wiring mix) refuses, in either direction."""
    model_two = cf.cargoflow2_funds_model(route_two)
    assert model_two.funds == route_two.start_funds == 475000
    assert model_two.purchase_quote == route_two.purchase_quote == 4700
    assert model_two.running_cost is None and model_two.fraction == 0
    assert not model_two.purchase_paid and model_two.income_deltas == []
    model_two.admit_running_cost(route_two.engine_running_display)  # its own census
    with pytest.raises(ValueError, match="inconsistent with its display figure"):
        cf.cargoflow2_funds_model(route_two).admit_running_cost(
            cf.CARGOFLOW2_RUNNING_DISPLAY
        )

    model_one = cf.cargoflow2_funds_model(cf.cargoflow2_route_binding())
    assert model_one.funds == cf.CARGOFLOW2_START_FUNDS == 489650
    assert model_one.purchase_quote == cf.CARGOFLOW2_PURCHASE_QUOTE == 4429
    model_one.admit_running_cost(cf.CARGOFLOW2_RUNNING_DISPLAY)  # its own census
    with pytest.raises(ValueError, match="inconsistent with its display figure"):
        cf.cargoflow2_funds_model(cf.cargoflow2_route_binding()).admit_running_cost(
            route_two.engine_running_display
        )
    # The default derivation is byte-equal to the model of record: the
    # recorded walk rides the default-wired model's display figure.
    assert model_one.funds == funds_walk({})[0]["site-00"] - model_one.purchase_quote * 0

