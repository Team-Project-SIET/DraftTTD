"""Controlled offline tests for the D5-BOX-CENSUS-1 wire contract (protocol 9).

The contract under test is ``app/simulation/openttd/corridor_box_census.py``
and the additive protocol-9 census handler shipped in
``app/simulation/openttd/d5_census_package/main.nut``. The shipped package
runs inside the real Squirrel VM against a census stub world that reproduces
the v2 ``DiscoveryBoxes`` scan semantics (per-tile industry ownership,
last-month production, acceptance states and the measured truck-stop
coverage radius); every dispatched reply is parsed back through the
protocol-9 wire contract, never through the package's own words.

The census is one schedule generation (no version families like the survey
contract has): a single pinned ten-exchange plan whose spot re-measures halt
on divergence with the raw measured value legible in the halt record, and
whose box pages measure membership as recorded rows, never verdicts.
Overflows and drained pages are measurements too. Nothing here launches
OpenTTD, connects to an AdminPort or writes any native or save state: only
the tests' own VM world is mutated.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from squirrel import SQVM

from app.planning.canonical import canonical_bytes
from app.simulation.openttd import corridor_box_census as cc
from app.simulation.openttd.proof import corridor_box_census_native as work

REPO = Path(__file__).resolve().parents[1]
PACKAGE = REPO / "app" / "simulation" / "openttd" / "d5_census_package"

PRELAUNCH = "a" * 64
OTHER_PLAN = "b" * 64

SCHEDULE = work.census_schedule()
PLAN = work.census_plan()
EXCHANGES = [entry["exchange"] for entry in SCHEDULE]
FUNDS = work.FUNDS_AT_A1_CLOSE
PICKUP_CENTRE = 45748
DELIVERY_CENTRE = 50862

API = """
::events <- [];
::replies <- [];
::send_ok <- true;
::ticks <- 0;
::sniffer <- {last = "missing"};
class GSController {
    function Sleep(ticks) {
        if (ticks != 1) throw "unexpected script sleep";
        ::ticks++;
        if (::ticks == ::stop_at) throw "CONTROLLED_STOP";
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
::dims <- [256, 256];
::industries <- {};
::ind_tiles <- {};
::accepts <- {};
::default_accept <- 0;
::funds <- 490257;
::paused <- false;
::valid_company <- true;
::second_company <- 1;
::mode_ok <- true;
::cur_company <- -1;
::station_radius <- 3;
::stop_at <- -1;
function census_seed(industry, tiles, production, accepted) {
    if (!(industry in ::industries)) ::industries[industry] <- {p = production, a = accepted};
    foreach (tile in tiles) ::ind_tiles[tile] <- industry;
}
/* The chain-continuity spots of record (E49 re-measures): the control zero
 * and the A1 bay stop eight eighths. */
::accepts[50351] <- 0;
::accepts[50862] <- 8;
"""

STUB = """
class GSGame {
    static function IsPaused() { return ::paused; }
}
class GSCompany {
    static COMPANY_INVALID = -1;
    static function ResolveCompanyID(c) {
        return !::valid_company ? -1 : (c == 0 || c == ::second_company) ? c : -1;
    }
    static function GetBankBalance(_) { return ::funds; }
}
class GSCompanyMode {
    constructor(c) {
        if (c != 0 && c != ::second_company) throw "company";
        ::cur_company = c;
    }
    static function IsValid() { return ::mode_ok; }
}
class GSMap {
    static function GetMapSizeX() { return ::dims[0]; }
    static function GetMapSizeY() { return ::dims[1]; }
    static function IsValidTile(t) { return t >= 0 && t <= 65535; }
}
class GSStation {
    static STATION_TRUCK_STOP = 0x1;
    static function GetCoverageRadius(_) { return ::station_radius; }
}
class GSTile {
    static function GetCargoAcceptance(tile, _, _, _, _) {
        return (tile in ::accepts) ? ::accepts[tile] : ::default_accept;
    }
}
class GSIndustry {
    static CAS_ACCEPTED = 1;
    static CAS_NOT_ACCEPTED = 0;
    static CAS_TEMP_REFUSED = 2;
    static CAS_INVALID = -1;
    static function GetIndustryID(tile) {
        return (tile in ::ind_tiles) ? ::ind_tiles[tile] : null;
    }
    static function IsValidIndustry(ind) { return ind in ::industries; }
    static function GetLastMonthProduction(ind, _) {
        local rec = (ind in ::industries) ? ::industries[ind] : null;
        return rec == null ? GSIndustry.CAS_INVALID : rec.p;
    }
    static function IsCargoAccepted(ind, _) {
        local rec = (ind in ::industries) ? ::industries[ind] : null;
        return rec == null ? GSIndustry.CAS_INVALID : rec.a;
    }
}
function json_cell(v) {
    if (v == null) return "null";
    if (typeof v == "bool") return v ? "true" : "false";
    if (typeof v == "string") return "\\"" + v + "\\"";
    if (typeof v == "array") {
        local out = "[";
        foreach (e in v) out = out + json_cell(e) + ",";
        if (out.len() > 1) out = out.slice(0, out.len() - 1);
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


def build_vm(**knobs: int | bool) -> SQVM:
    """Fresh VM with the census API fixture, the controlled world and the package."""
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
    vm.execute("::bridge <- D5CensusProof();")
    return vm


def seed_industries(vm: SQVM, entries: list[tuple[int, list[int], int, int]]) -> None:
    """Shape the stub industry ground between exchanges (real ground would)."""
    for industry, tiles, production, accepted in entries:
        tiles_literal = ",".join(str(tile) for tile in tiles)
        vm.execute(f"census_seed({industry}, [{tiles_literal}], {production}, {accepted});")


def vm_root(vm: SQVM) -> dict[str, Any]:
    return vm.get_roottable()


def drive(vm: SQVM, request: cc.CensusRequest) -> cc.CensusReadback:
    """Dispatch one request over the wire and parse the reply into Python."""
    replies = vm_root(vm)["replies"]
    before = len(replies)
    vm.execute("::bridge.Handle(" + request.to_bytes().decode() + ");")
    if len(vm_root(vm)["replies"]) == before:
        raise AssertionError(f"package dropped request {request.request_id}: no reply")
    vm.execute("::sniffer.last = last_reply_json();")
    raw = vm_root(vm)["sniffer"]["last"]
    assert len(raw.encode()) <= cc.MAX_CENSUS_RESPONSE_BYTES, (
        f"response for {request.request_id} exceeds {cc.MAX_CENSUS_RESPONSE_BYTES} bytes"
    )
    return cc.CensusReadback.parse_for(request, raw.encode())


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
    """A valid-shaped request payload for the raw handler tests."""
    payload = {
        "protocol": 9,
        "op": "radius",
        "request_id": "radius-00",
        "plan": PRELAUNCH,
        "company": 0,
        "max_cost": 0,
        "pickup": 45748,
        "delivery": 50351,
        "depot": 45487,
        "tile": None,
        "cursor": None,
    }
    payload.update(overrides)
    return payload


def readback_payload(request: cc.CensusRequest, **overrides) -> dict:
    """A correlated success readback the handler-shaped table satisfies."""
    payload = {
        "protocol": 9,
        "op": request.op,
        "request_id": request.request_id,
        "plan": request.plan,
        "company": request.company,
        "max_cost": request.max_cost,
        "pickup": request.pickup,
        "delivery": request.delivery,
        "depot": request.depot,
        "status": "READY",
        "funds": FUNDS,
        "cost": 0,
    }
    if request.tile is not None:
        payload["tile"] = request.tile
    if request.cursor is not None:
        payload["cursor"] = request.cursor
    payload.update(overrides)
    return payload


def make_request(entry_index: int) -> cc.CensusRequest:
    return work._census_exchange_request(SCHEDULE[entry_index], PRELAUNCH, PLAN)


def run_census_vm(world: list[tuple[int, list[int], int, int]] | None = None):
    """The exact ten planned exchanges in order (the production builder)."""
    vm = build_vm()
    if world:
        seed_industries(vm, world)
    exchanges: list[tuple[cc.CensusRequest, cc.CensusReadback]] = []
    for entry in SCHEDULE:
        request = make_request(EXCHANGES.index(entry["exchange"]))
        readback = drive(vm, request)
        probes = cc.census_phase_outcome(
            exchanges + [(request, readback)], prelaunch_digest=PRELAUNCH, plan=PLAN
        )
        assert probes["failed"] is None, (entry["exchange"], probes["failed"])
        exchanges.append((request, readback))
    phase = cc.census_phase_outcome(exchanges, prelaunch_digest=PRELAUNCH, plan=PLAN)
    return vm, exchanges, phase


# --- The pinned schedule and plan (drift gates) ------------------------------


def test_pinned_schedule_constants():
    assert cc.CENSUS_EXCHANGE_IDS == (
        "radius-00",
        "acc-00",
        "acc-01",
        "prod-00",
        "pbox-00",
        "pbox-01",
        "pbox-02",
        "dbox-00",
        "dbox-01",
        "dbox-02",
    )
    assert cc.PLANNED_CENSUS_EXCHANGES == 10
    assert cc.CENSUS_OPS == ("radius", "accept", "prod", "box")
    assert cc.SPOT_EXCHANGE_TILES == {"acc-00": 50351, "acc-01": 50862}
    assert cc.SPOT_EXPECTED_ACCEPTS == {"acc-00": 0, "acc-01": 8}
    assert cc.BOX_EXCHANGE_SPECS == {
        "pbox-00": (45748, 0),
        "pbox-01": (45748, 3),
        "pbox-02": (45748, 6),
        "dbox-00": (50862, 0),
        "dbox-01": (50862, 3),
        "dbox-02": (50862, 6),
    }
    assert cc.BOX_PAGE_CURSORS == (0, 3, 6)
    assert cc.MAX_BOX_PAGE_ROWS == 3 and cc.MAX_BOX_PAGES == 3
    assert cc.MAX_CENSUS_REQUEST_BYTES == cc.MAX_CENSUS_RESPONSE_BYTES == 512
    assert cc.CENSUS_PROTOCOL == 9
    assert cc.CENSUS_PICKUP_TILE == 45748 and cc.CENSUS_DELIVERY_TILE == 50351
    assert cc.CENSUS_DEPOT_TILE == 45487
    assert cc.CENSUS_SPOT_TILES == (50351, 50862)
    assert cc.CENSUS_BOX_CENTRES == (45748, 50862)
    assert cc.CENSUS_CENTRE_ROLES == {45748: "producer", 50862: "acceptor"}
    assert cc.FUNDS_AT_A1_CLOSE == FUNDS == 490257


def test_plan_pinned_and_digest_stable():
    plan = cc.box_census_plan()
    assert plan.company == 0 and plan.cargo == 1
    assert plan.expected_funds == FUNDS
    assert plan.spots == cc.CENSUS_SPOT_TILES
    assert plan.box_centres == cc.CENSUS_BOX_CENTRES
    assert plan.box_page_rows == 3
    assert plan.schedule == cc.CENSUS_EXCHANGE_IDS
    assert plan.pickup_industry == 0
    assert plan.request_budget == 32
    assert plan.schema_version == 1
    assert plan.digest == cc.box_census_plan().digest


@pytest.mark.parametrize(
    "field, value",
    [
        ("expected_funds", 492149),
        ("box_page_rows", 2),
        ("pickup_industry", 1),
        ("request_budget", 33),
        ("company", 1),
        ("cargo", 2),
    ],
)
def test_plan_field_drift_refused(field, value):
    payload = cc.box_census_plan().model_dump()
    payload[field] = value
    with pytest.raises(ValueError):
        cc.BoxCensusPlan.model_validate(payload)


# --- The bounded wire: exact request bytes and the 512 floor -----------------


def test_exact_request_bytes_of_record():
    request = make_request(0)
    expected = (
        '{"company":0,'
        '"cursor":null,'
        '"delivery":50351,'
        '"depot":45487,'
        '"max_cost":0,'
        '"op":"radius",'
        '"pickup":45748,'
        f'"plan":"{PRELAUNCH}",'
        '"protocol":9,'
        '"request_id":"radius-00",'
        '"tile":null}'
    )
    assert request.to_bytes().decode() == expected


def test_request_slots_of_record():
    accept = make_request(1)
    assert accept.op == "accept" and accept.tile == 50351 and accept.cursor is None
    stop = make_request(2)
    assert stop.tile == 50862
    box = make_request(9)
    assert box.op == "box" and (box.tile, box.cursor) == (50862, 6)


def test_worst_case_request_byte_audit_is_217():
    request = make_request(9)
    assert len(request.to_bytes()) == 217
    for entry_index in range(len(SCHEDULE)):
        assert len(make_request(entry_index).to_bytes()) <= 512


def test_request_op_domain_refusals():
    def make(op, **overrides):
        payload = dict(
            op=op,
            request_id="radius-00",
            plan=PRELAUNCH,
            company=0,
            max_cost=0,
            pickup=45748,
            delivery=50351,
            depot=45487,
        )
        payload.update(overrides)
        return cc.CensusRequest.model_validate(payload)

    with pytest.raises(ValueError, match="accept exchanges may only query"):
        make("accept", request_id="acc-00", tile=45748)
    with pytest.raises(ValueError, match="box exchanges may only query"):
        make("box", request_id="pbox-00", tile=50351, cursor=0)
    with pytest.raises(ValueError, match="only the accept and box ops carry a tile"):
        make("radius", tile=45748)
    with pytest.raises(ValueError, match="carry exactly one pinned tile"):
        make("accept", request_id="acc-00")
    with pytest.raises(ValueError, match="box exchanges carry their page cursor"):
        make("box", request_id="pbox-00", tile=45748)
    with pytest.raises(ValueError, match="box page cursors sit on the pinned static grid"):
        make("box", request_id="pbox-00", tile=45748, cursor=2)
    with pytest.raises(ValueError, match="only the box op carries a cursor"):
        make("accept", request_id="acc-00", tile=50351, cursor=0)
    with pytest.raises(ValueError, match="carry exactly one pinned tile"):
        make("box", request_id="pbox-00", cursor=0)
    with pytest.raises(ValueError, match="only the box op carries a cursor"):
        make("radius", cursor=0)
    with pytest.raises(ValueError):
        make("radius", company=False)


# --- The request verifier (Python trust anchor) ------------------------------


def test_request_verifier_slots():
    for entry_index in range(len(SCHEDULE)):
        request = make_request(entry_index)
        cc.verify_request_against_census_plan(request, plan=PLAN, seal=PRELAUNCH)


def test_request_verifier_refusals():
    spot = make_request(1)
    with pytest.raises(ValueError, match="not the staged prelaunch seal"):
        cc.verify_request_against_census_plan(spot, plan=PLAN, seal=OTHER_PLAN)
    with pytest.raises(ValueError, match="accept request tile drifted"):
        cc.verify_request_against_census_plan(
            spot.model_copy(update={"tile": 50862}), plan=PLAN, seal=PRELAUNCH
        )
    box = make_request(4)
    with pytest.raises(ValueError, match="box request drifted"):
        cc.verify_request_against_census_plan(
            box.model_copy(update={"cursor": 3}), plan=PLAN, seal=PRELAUNCH
        )
    with pytest.raises(ValueError, match="company drifted"):
        cc.verify_request_against_census_plan(
            spot.model_copy(update={"company": 1}), plan=PLAN, seal=PRELAUNCH
        )
    with pytest.raises(ValueError, match="pins drifted"):
        cc.verify_request_against_census_plan(
            spot.model_copy(update={"pickup": 45487}), plan=PLAN, seal=PRELAUNCH
        )


# --- Response parsing: correlation, echoes, subsets, page formula ------------


def test_parse_accepts_handler_shape_without_null_keys():
    request = make_request(0)
    raw = json.dumps(readback_payload(request, radius=3), separators=(",", ":")).encode()
    readback = cc.CensusReadback.parse_for(request, raw)
    assert readback.radius == 3 and readback.tile is None and readback.status == "READY"


def test_parse_ceiling_duplicate_and_correlation():
    request = make_request(0)
    with pytest.raises(ValueError, match="exceeds 512 bytes"):
        cc.CensusReadback.parse_for(request, b"0" * 513)
    body = json.dumps(readback_payload(request, radius=3), separators=(",", ":"))
    duplicate = body[:-1] + ',"radius":3}'
    with pytest.raises(ValueError, match="duplicate response key"):
        cc.CensusReadback.parse_for(request, duplicate.encode())
    with pytest.raises(ValueError, match="correlation mismatch"):
        cc.CensusReadback.parse_for(
            request, json.dumps(readback_payload(request, radius=3, request_id="radius-01"),
                                separators=(",", ":")).encode()
        )
    with pytest.raises(ValueError, match="correlation mismatch"):
        cc.CensusReadback.parse_for(
            request, json.dumps(readback_payload(request, radius=3, plan=OTHER_PLAN),
                                separators=(",", ":")).encode()
        )
    with pytest.raises(ValueError, match="pin mismatch"):
        cc.CensusReadback.parse_for(
            request, json.dumps(readback_payload(request, radius=3, pickup=45487),
                                separators=(",", ":")).encode()
        )


def test_parse_spot_and_page_echoes():
    spot = make_request(1)
    with pytest.raises(ValueError, match="tile echo mismatch"):
        cc.CensusReadback.parse_for(
            spot,
            json.dumps(
                readback_payload(spot, accept=0, radius=3, tile=50862),
                separators=(",", ":"),
            ).encode(),
        )
    page = make_request(6)
    rows = [
        {"id": 0, "tile": 45745, "p": 104, "a": 0},
        {"id": 3, "tile": 45746, "p": 0, "a": 1},
    ]
    with pytest.raises(ValueError, match="cursor echo mismatch"):
        cc.CensusReadback.parse_for(
            page,
            json.dumps(
                readback_payload(page, count=2, more=False, rows=rows, cursor=0),
                separators=(",", ":"),
            ).encode(),
        )


def test_parse_box_success_requires_complete_observation_set():
    page = make_request(4)
    rows = [{"id": 0, "tile": 45745, "p": 104, "a": 0}]
    with pytest.raises(ValueError, match="success readback lacks"):
        cc.CensusReadback.parse_for(
            page, json.dumps(readback_payload(page, count=1, more=False),
                             separators=(",", ":")).encode()
        )
    with pytest.raises(ValueError, match="must echo its pinned centre"):
        cc.CensusReadback.parse_for(
            page,
            json.dumps(
                readback_payload(page, count=1, more=False, rows=rows, tile=None, cursor=0),
                separators=(",", ":"),
            ).encode(),
        )
    with pytest.raises(ValueError, match="must echo its page cursor"):
        cc.CensusReadback.parse_for(
            page,
            json.dumps(
                readback_payload(page, count=1, more=False, rows=rows, cursor=None),
                separators=(",", ":"),
            ).encode(),
        )
    with pytest.raises(ValueError, match="carries fields outside its subset"):
        cc.CensusReadback.parse_for(
            page,
            json.dumps(readback_payload(page, count=1, more=False, rows=rows, radius=3),
                       separators=(",", ":")).encode(),
        )


def test_parse_box_rows_and_more_formula():
    page = make_request(4)
    pairs = [
        {"id": 1, "tile": 45745, "p": 104, "a": 0},
        {"id": 0, "tile": 45746, "p": 0, "a": 1},
    ]
    with pytest.raises(ValueError, match="must ascend by industry id"):
        cc.CensusReadback.parse_for(
            page, json.dumps(readback_payload(page, count=2, more=False, rows=pairs, cursor=0),
                             separators=(",", ":")).encode()
        )
    four = pairs + [{"id": 2, "tile": 45747, "p": 1, "a": 0},
                    {"id": 4, "tile": 45748, "p": 9, "a": 2}]
    with pytest.raises(ValueError, match="more than its pinned row budget"):
        cc.CensusReadback.parse_for(
            page, json.dumps(readback_payload(page, count=4, more=True, rows=four, cursor=0),
                             separators=(",", ":")).encode()
        )
    worst = [
        {"id": 65533, "tile": 65535, "p": 2147483647, "a": 2},
        {"id": 65534, "tile": 65535, "p": 2147483647, "a": 2},
        {"id": 65535, "tile": 65535, "p": 2147483647, "a": 2},
    ]
    with pytest.raises(ValueError, match="more flag drifted from its own membership"):
        cc.CensusReadback.parse_for(
            page, json.dumps(readback_payload(page, count=3, more=True, rows=worst, cursor=0),
                             separators=(",", ":")).encode()
        )
    drained = cc.CensusReadback.parse_for(
        page,
        json.dumps(readback_payload(page, count=1, more=False, rows=[worst[0]], cursor=0),
                   separators=(",", ":")).encode(),
    )
    assert drained.count == 1 and drained.more is False
    full = cc.CensusReadback.parse_for(
        page, json.dumps(readback_payload(page, count=4, more=True, rows=worst, cursor=0),
                         separators=(",", ":")).encode()
    )
    assert full.more is True and full.count == 4


def test_parse_refusal_observability_boundaries():
    spot = make_request(1)
    with pytest.raises(ValueError, match="unclaimed observation set"):
        cc.CensusReadback.parse_for(
            spot,
            json.dumps(readback_payload(spot, status="INVALID_LOCATION", accept=0, radius=3),
                       separators=(",", ":")).encode(),
        )
    page = make_request(5)
    with pytest.raises(ValueError, match="unclaimed observation set"):
        cc.CensusReadback.parse_for(
            page,
            json.dumps(
                readback_payload(page, status="INVALID_LOCATION", count=0,
                                 more=False, rows=[]),
                separators=(",", ":"),
            ).encode(),
        )
    with pytest.raises(ValueError, match="Input should be 'READY'"):
        cc.CensusReadback.parse_for(
            spot,
            json.dumps(readback_payload(spot, status="SURVEY_COMPLETE"),
                       separators=(",", ":")).encode(),
        )
    with pytest.raises(ValueError, match="must not name a tile"):
        prod = make_request(3)
        cc.CensusReadback.parse_for(
            prod, json.dumps(readback_payload(prod, prod=104, tile=45748),
                             separators=(",", ":")).encode()
        )
    with pytest.raises(ValueError):
        cc.CensusReadback.parse_for(
            spot,
            json.dumps(readback_payload(spot, accept=0, radius=3, funds=False, tile=50351),
                       separators=(",", ":")).encode(),
        )


def test_worst_case_response_byte_audit_is_431_wire_and_471_null_form():
    page = make_request(9)
    rows = [
        {"id": 65533, "tile": 65535, "p": 2147483647, "a": 2},
        {"id": 65534, "tile": 65535, "p": 2147483647, "a": 2},
        {"id": 65535, "tile": 65535, "p": 2147483647, "a": 2},
    ]
    wire = json.dumps(readback_payload(page, count=10, more=True, rows=rows),
                      separators=(",", ":")).encode()
    assert len(wire) == 431  # the measured handler-table worst case (E59 §3.4 table)
    wire_readback = cc.CensusReadback.parse_for(page, wire)
    assert wire_readback.more is True and len(wire_readback.rows) == 3
    null_form = {
        **readback_payload(page, count=10, more=True, rows=rows),
        "accept": None,
        "prod": None,
        "radius": None,
    }
    raw_null = json.dumps(null_form, sort_keys=True, ensure_ascii=False,
                          separators=(",", ":")).encode()
    assert len(raw_null) == 471  # the Python-side null-inclusive canonical audit
    assert cc.CensusReadback.parse_for(page, raw_null) == wire_readback
    assert len(canonical_bytes(wire_readback)) == 471


# --- The phase verifier: full completion, drained pages, overflow ------------

PASS_WORLD = [
    (0, [45748], 104, 0),  # the pickup producer of record
    (2, [45751], 0, 0),  # a non-producer member inside the pickup box
    (5, [45749, 44981], 0, 0),  # two member tiles: anchor = the first scan sighting
    (1, [50862], 0, 1),  # the A1 acceptor of record
    (4, [50863], 0, 0),  # a non-acceptor member inside the A1 box
]


def test_full_schedule_completes_and_gate_passes():
    vm, exchanges, phase = run_census_vm(PASS_WORLD)
    assert phase["verification"] == "CENSUS_COMPLETE"
    assert phase["failed"] is None and not phase["pending"]
    assert phase["radius"] == 3 and phase["production"] == 104
    assert phase["funds"] == FUNDS
    assert set(phase["observations"]) == {50351, 50862}
    assert phase["observations"][50351]["value"] == 0
    assert phase["observations"][50862]["value"] == 8
    assert phase["branch8"]["verdict"] == "CENSUS_GATE_PASSES"
    assert phase["branch8"]["role_counts"] == {"producer": 1, "acceptor": 1}
    assert [receipt["request_id"] for receipt in phase["receipts"]] == EXCHANGES
    boxes = phase["boxes"]
    assert boxes[str(PICKUP_CENTRE)]["role_filtered"] == [{"id": 0, "tile": 45748}]
    assert boxes[str(DELIVERY_CENTRE)]["role_filtered"] == [{"id": 1, "tile": 50862}]
    assert boxes[str(PICKUP_CENTRE)]["exactly_one"] is True
    logs = [str(line) for line in vm_root(vm)["markers"]]
    assert logs[0] == "D5_CENSUS radius-00 READY"
    assert logs[len(logs) - 1] == "D5_CENSUS dbox-02 READY"


def test_min_tile_anchor_is_first_scan_sighting():
    _, _, phase = run_census_vm(PASS_WORLD)
    members = phase["boxes"][str(PICKUP_CENTRE)]["members"]
    anchor = next(row for row in members if row["id"] == 5)
    assert anchor["tile"] == 44981  # ascending scan meets the lower tile first
    assert [(row["id"], row["tile"]) for row in members] == [
        (5, 44981),
        (0, 45748),
        (2, 45751),
    ]  # DiscoveryBoxes iteration order: ascending member tile, then id


def test_drained_pages_measure_absence():
    world = [(0, [45748], 104, 0), (1, [50862], 0, 1)]
    _, _, phase = run_census_vm(world)
    pickup = phase["boxes"][str(PICKUP_CENTRE)]
    delivery = phase["boxes"][str(DELIVERY_CENTRE)]
    for box in (pickup, delivery):
        assert [page["cursor"] for page in box["pages"]] == [0, 3, 6]
        assert [page["row_count"] for page in box["pages"]] == [1, 0, 0]
        assert [page["more"] for page in box["pages"]] == [False, False, False]
    assert pickup["count"] == 1 and delivery["count"] == 1
    assert phase["branch8"]["verdict"] == "CENSUS_GATE_PASSES"


def test_overflow_is_an_explicit_undecided_finding():
    world = [
        (0, [45748], 104, 0),  # the producer of record keeps the prod control
        (2, [45751], 1, 0),
        (5, [45749, 44981], 1, 0),
        (6, [45489], 1, 0),
        (7, [45233], 1, 0),
        (8, [45745], 1, 0),
        (9, [45746], 1, 0),
        (10, [45747], 1, 0),
        (65534, [45750], 1, 0),
        (65535, [46001], 1, 0),
        (1, [50862], 0, 1),
    ]
    _, _, phase = run_census_vm(world)
    pickup = phase["boxes"][str(PICKUP_CENTRE)]
    assert pickup["count"] == 10
    assert pickup["overflow"] is True
    assert [page["row_count"] for page in pickup["pages"]] == [3, 3, 3]
    assert [page["more"] for page in pickup["pages"]] == [True, True, True]
    assert phase["branch8"]["verdict"] == "CENSUS_GATE_UNDECIDED_OVERFLOW"
    assert "more distinct industries" in phase["branch8"]["statement"]


def test_branch_recompute_fails_on_two_producers():
    world = [
        (0, [45748], 104, 0),
        (10, [45750], 5, 0),  # a second producer inside the pickup box
        (1, [50862], 0, 1),
    ]
    _, _, phase = run_census_vm(world)
    assert phase["branch8"]["verdict"] == "CENSUS_GATE_FAILS"
    assert phase["branch8"]["role_counts"] == {"producer": 2, "acceptor": 1}


def test_branch_recompute_fails_on_two_acceptors():
    world = [
        (0, [45748], 104, 0),
        (1, [50862], 0, 1),
        (11, [50864], 0, 2),  # CAS_TEMP_REFUSED is not an acceptor
        (12, [50865], 0, 1),  # a second accepted industry inside the box
    ]
    _, _, phase = run_census_vm(world)
    assert phase["branch8"]["verdict"] == "CENSUS_GATE_FAILS"
    assert phase["branch8"]["role_counts"] == {"producer": 1, "acceptor": 2}


# --- The phase verifier: divergence halts and incomplete paths ---------------


def measured_prefix(index: int) -> list[tuple[cc.CensusRequest, cc.CensusReadback]]:
    """Ready exchanges for schedule positions [0, index)."""
    exchanges = []
    for position in range(index):
        request = make_request(position)
        payload = readback_payload(request)
        if request.op == "radius":
            payload["radius"] = 3
        elif request.op == "accept":
            payload["accept"] = cc.SPOT_EXPECTED_ACCEPTS[request.request_id]
            payload["radius"] = 3
        elif request.op == "prod":
            payload["prod"] = 104
        exchanges.append((request, cc.CensusReadback.model_validate(payload)))
    return exchanges


def divergent_exchange(index: int, **overrides) -> tuple[cc.CensusRequest, cc.CensusReadback]:
    """The READY-shaped readback at schedule position `index` with a foreign value."""
    request = make_request(index)
    payload = readback_payload(request)
    payload.update(overrides)
    if request.op == "accept":
        payload.setdefault("radius", 3)
    if request.op == "box":
        payload.setdefault("cursor", request.cursor)
        payload["count"] = overrides.get("count", 0)
        payload["more"] = overrides.get("more", False)
        payload["rows"] = tuple(overrides.get("rows", []))
    return (request, cc.CensusReadback.model_validate(payload))


def test_spot_divergence_halts_verbatim():
    exchanges = measured_prefix(1) + [divergent_exchange(1, accept=3, radius=3)]
    phase = cc.census_phase_outcome(exchanges, prelaunch_digest=PRELAUNCH, plan=PLAN)
    assert phase["verification"] == "CENSUS_INCOMPLETE"
    assert phase["failed"]["label"] == "acc-00"
    assert phase["failed"]["status"] == "READY"
    assert "measured 3, expected 0" in phase["failed"]["error"]
    assert phase["pending"] == EXCHANGES[2:]

    exchanges = measured_prefix(2) + [divergent_exchange(2, accept=7, radius=3)]
    phase = cc.census_phase_outcome(exchanges, prelaunch_digest=PRELAUNCH, plan=PLAN)
    assert "measured 7, expected 8" in phase["failed"]["error"]
    assert phase["failed"]["label"] == "acc-01"

    exchanges = measured_prefix(3) + [divergent_exchange(3, prod=96)]
    phase = cc.census_phase_outcome(exchanges, prelaunch_digest=PRELAUNCH, plan=PLAN)
    assert "measured 96, expected 104" in phase["failed"]["error"]
    assert phase["failed"]["label"] == "prod-00"


def test_radius_must_precede_every_observation():
    accept = divergent_exchange(1, accept=3, radius=3)
    phase = cc.census_phase_outcome([accept], prelaunch_digest=PRELAUNCH, plan=PLAN)
    assert phase["failed"]["label"] == "acc-00"
    assert "out of order: expected radius-00" in phase["failed"]["error"]
    box = divergent_exchange(4)
    phase = cc.census_phase_outcome([box], prelaunch_digest=PRELAUNCH, plan=PLAN)
    assert phase["failed"]["label"] == "pbox-00"
    assert "out of order" in phase["failed"]["error"]


def test_count_drift_halt_across_pages():
    prefix = measured_prefix(4)  # radius through prod-00 in order
    first = divergent_exchange(
        4, count=2, more=True, rows=[{"id": 0, "tile": 45748, "p": 104, "a": 0}]
    )
    second = divergent_exchange(
        5, count=3, more=False, rows=[{"id": 1, "tile": 45749, "p": 2, "a": 0}]
    )
    exchanges = [*prefix, first, second]
    phase = cc.census_phase_outcome(exchanges, prelaunch_digest=PRELAUNCH, plan=PLAN)
    assert phase["failed"]["label"] == "pbox-01"
    assert "2 then 3" in phase["failed"]["error"]


def test_cross_page_ascending_id_halt():
    prefix = measured_prefix(4)
    first = divergent_exchange(
        4, count=9, more=True, rows=[{"id": 20, "tile": 45748, "p": 104, "a": 0}]
    )
    second = divergent_exchange(
        5, count=9, more=True, rows=[{"id": 19, "tile": 45749, "p": 1, "a": 0}]
    )
    exchanges = [*prefix, first, second]
    phase = cc.census_phase_outcome(exchanges, prelaunch_digest=PRELAUNCH, plan=PLAN)
    assert "ascending order across the pages" in phase["failed"]["error"]


def test_geometry_violation_halt():
    prefix = measured_prefix(4)
    page = divergent_exchange(
        4, count=1, more=False, rows=[{"id": 0, "tile": 100, "p": 104, "a": 0}]
    )
    exchanges = [*prefix, page]
    phase = cc.census_phase_outcome(exchanges, prelaunch_digest=PRELAUNCH, plan=PLAN)
    assert "outside the measured scan box" in phase["failed"]["error"]


def test_geometry_matches_squirrel_box_and_map_edges():
    geometry = cc.census_box_geometry(3, PICKUP_CENTRE)
    assert 45748 in geometry and 45749 in geometry and 44981 in geometry
    assert 45744 not in geometry  # one column left of the box
    assert 44497 not in geometry  # one row short of the box
    corner = cc.census_box_geometry(3, 0)
    assert len(corner) == 16
    assert 0 in corner and 3 in corner and 768 in corner and 771 in corner and 4 not in corner


def test_malformed_and_missing_observations_fail_closed():
    request = make_request(0)
    phase = cc.census_phase_outcome(
        [(request, ValueError("torn frame"))], prelaunch_digest=PRELAUNCH, plan=PLAN
    )
    assert phase["failed"]["status"] == "MALFORMED"
    assert "torn frame" in phase["failed"]["error"]
    assert phase["verification"] == "CENSUS_INCOMPLETE"
    refusal = cc.CensusReadback.model_validate(readback_payload(request, status="INVALID_COMPANY"))
    phase = cc.census_phase_outcome([(request, refusal)], prelaunch_digest=PRELAUNCH, plan=PLAN)
    assert phase["failed"]["status"] == "INVALID_COMPANY"
    assert phase["failed"]["error"] == "census exchange radius-00 ended INVALID_COMPANY"


# The shipped GameScript handler tests live in tests/test_corridor_box_census_vm.py
# (E59 design §9 item 6); the VM stubs and world fixtures they share stay here.
