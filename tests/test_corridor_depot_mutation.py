"""Controlled offline tests for the D5-F12-DEPOT wire contract (protocol 10).

The contract under test is ``app/simulation/openttd/corridor_depot_mutation.py``
and the additive protocol-10 mutation handler shipped in
``app/simulation/openttd/d5_depot_mutation_package/main.nut``. The shipped
package runs inside the real Squirrel VM against a mutation stub world that
reproduces the E58 §2.1 pre-fix and post-fix depot/edge semantics (per-tile
facing road bits with the depot door contribution, demolition refunds, road
and depot construction costs and the company fleet); every dispatched reply
is parsed back through the protocol-10 wire contract, never through the
package's own words.

The mutation is one schedule generation: a single pinned six-exchange plan
whose before gate must reproduce the E58 diagnosis verbatim, whose three
prescribed commands each re-observe their precondition before the one
dispatch (STALE_PIN on drift, before any command), whose after gate proves
both ``AreRoadTilesConnected`` directions true under the identical identity
facts and whose fleet gate demands the retained zero fleet. Nothing here
launches OpenTTD, connects to an AdminPort or writes any native or save
state: only the tests' own VM world is mutated.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from squirrel import SQVM

from app.simulation.openttd import corridor_depot_mutation as dm
from app.simulation.openttd.proof import corridor_depot_mutation_native as work

REPO = Path(__file__).resolve().parents[1]
PACKAGE = REPO / "app" / "simulation" / "openttd" / "d5_depot_mutation_package"

PRELAUNCH = "a" * 64
OTHER_PLAN = "b" * 64

SCHEDULE = work.depot_schedule()
PLAN = work.depot_plan()
EXCHANGES = [entry["exchange"] for entry in SCHEDULE]
FUNDS = work.FUNDS_AT_F12_OPEN
DEPOT_TILE = 45487
DEPOT_FRONT = 45743

# The stub cost knobs of record: the demolish refunds (cost -100), the road
# pair charges 200 and the depot rebuild charges 1200, so the pinned funds
# chain runs 490257 -> 490357 -> 490157 -> 488957 across the three commands.
COST_KNOBS = dict(demolish_cost=-100, road_cost=200, depot_cost=1200)
FUNDS_AFTER_DEMO = FUNDS + 100
FUNDS_AFTER_ROAD = FUNDS_AFTER_DEMO - 200
FUNDS_AFTER_DEPOT = FUNDS_AFTER_ROAD - 1200

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
::map_w <- 256;
::funds <- 490257;
::paused <- false;
::valid_company <- true;
::second_company <- 1;
::mode_ok <- true;
::cur_company <- -1;
::cur_road_type <- 0;
::road_type_ok <- true;
::demolish_ok <- true;
::road_ok <- true;
::depot_ok <- true;
::demolish_cost <- -100;
::road_cost <- 200;
::depot_cost <- 1200;
::stop_at <- -1;
::default_owner <- 0;
::owners <- {};
::owners[45487] <- 0;
::owners[45743] <- 0;
/* The E58 pre-fix world of record: 45743 carries E+W+S (D4 run-A full-op
 * endpoints plus the corner-join half-op) and no N; the depot 45487 faces
 * its pinned front 45743 with the zero fleet. */
::road_bits <- {};
::road_bits[45743] <- {n = false, s = true, e = true, w = true};
::depots <- {};
::depots[45487] <- 45743;
::vehicles <- {};
function facing_bit(tile, dx, dy) {
    /* The facing bit of record: a depot contributes only its door bit
     * (toward its front); a road tile contributes whichever of its
     * carriageway bits the offset names. */
    if (tile in ::depots) {
        local front = ::depots[tile];
        local fx = (front % ::map_w) - (tile % ::map_w);
        local fy = (front / ::map_w) - (tile / ::map_w);
        return dx == fx && dy == fy;
    }
    if (!(tile in ::road_bits)) return false;
    local rec = ::road_bits[tile];
    if (dy == -1) return rec.n;
    if (dy == 1) return rec.s;
    if (dx == -1) return rec.w;
    if (dx == 1) return rec.e;
    return false;
}
function ensure_road_tile(tile) {
    if (!(tile in ::road_bits)) ::road_bits[tile] <- {n = false, s = false, e = false, w = false};
}
function depot_seed_vehicle(id, tile, in_depot) {
    ::vehicles[id] <- {tile = tile, in_depot = in_depot};
}
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
class GSTile {
    static function GetOwner(tile) {
        return (tile in ::owners) ? ::owners[tile] : ::default_owner;
    }
    static function DemolishTile(tile) {
        if (!::demolish_ok) return false;
        if (typeof tile != "integer" || tile < 0 || tile > 65535) return false;
        if (tile in ::depots) delete ::depots[tile];
        if (tile in ::road_bits) delete ::road_bits[tile];
        ::funds -= ::demolish_cost;
        return true;
    }
}
class GSRoad {
    static ROADTYPE_ROAD = 0;
    static function IsRoadTypeAvailable(_) { return ::road_type_ok; }
    static function SetCurrentRoadType(t) { ::cur_road_type = t; }
    static function GetCurrentRoadType() { return ::cur_road_type; }
    static function IsRoadTile(tile) { return tile in ::road_bits; }
    static function IsRoadDepotTile(tile) { return tile in ::depots; }
    static function GetRoadDepotFrontTile(tile) {
        return (tile in ::depots) ? ::depots[tile] : -1;
    }
    static function AreRoadTilesConnected(t1, t2) {
        if (typeof t1 != "integer" || typeof t2 != "integer" || t1 == t2) return false;
        if (t1 < 0 || t1 > 65535 || t2 < 0 || t2 > 65535) return false;
        local dx = (t2 % ::map_w) - (t1 % ::map_w);
        local dy = (t2 / ::map_w) - (t1 / ::map_w);
        if ((dx != 0 && dy != 0) || (dx == 0 && dy == 0)) return false;
        if (dx < -1 || dx > 1 || dy < -1 || dy > 1) return false;
        return facing_bit(t1, dx, dy) && facing_bit(t2, -dx, -dy);
    }
    static function BuildRoad(start, end) {
        if (!::road_ok) return false;
        if (typeof start != "integer" || typeof end != "integer" || start == end) return false;
        if (start < 0 || start > 65535 || end < 0 || end > 65535) return false;
        local sx = start % ::map_w, sy = start / ::map_w;
        local ex = end % ::map_w, ey = end / ::map_w;
        if (sx != ex && sy != ey) return false;
        local dx = ex > sx ? 1 : (ex < sx ? -1 : 0);
        local dy = ey > sy ? 1 : (ey < sy ? -1 : 0);
        local tile = start;
        while (tile != end) {
            local nxt = tile + dx + dy * ::map_w;
            ensure_road_tile(tile);
            ensure_road_tile(nxt);
            if (dx == 1) { ::road_bits[tile].e = true; ::road_bits[nxt].w = true; }
            else if (dx == -1) { ::road_bits[tile].w = true; ::road_bits[nxt].e = true; }
            else if (dy == 1) { ::road_bits[tile].s = true; ::road_bits[nxt].n = true; }
            else { ::road_bits[tile].n = true; ::road_bits[nxt].s = true; }
            tile = nxt;
        }
        ::funds -= ::road_cost;
        return true;
    }
    static function BuildRoadDepot(tile, front) {
        if (!::depot_ok) return false;
        if (typeof tile != "integer" || typeof front != "integer" || tile == front) return false;
        if (tile < 0 || tile > 65535 || front < 0 || front > 65535) return false;
        local dx = (front % ::map_w) - (tile % ::map_w);
        local dy = (front / ::map_w) - (tile / ::map_w);
        if ((dx != 0 && dy != 0) || (dx == 0 && dy == 0)) return false;
        if (dx < -1 || dx > 1 || dy < -1 || dy > 1) return false;
        /* The depot build rides CMD_LANDSCAPE_CLEAR on the target tile, so
         * the S bit the road pair laid there is auto-cleared. */
        if (tile in ::road_bits) delete ::road_bits[tile];
        ::depots[tile] <- front;
        ::funds -= ::depot_cost;
        return true;
    }
}
class GSVehicle {
    static function IsValidVehicle(vid) { return vid in ::vehicles; }
    static function GetLocation(vid) {
        local v = (vid in ::vehicles) ? ::vehicles[vid] : null;
        return v == null ? -1 : v.tile;
    }
    static function IsInDepot(vid) {
        local v = (vid in ::vehicles) ? ::vehicles[vid] : null;
        return v == null ? null : v.in_depot;
    }
}
class GSList {
    items = null;
    constructor() { items = {}; }
    function Count() { return items.len(); }
    function _get(key) { return items[key]; }
    function _nexti(prev) {
        local keys = [];
        foreach (key, _ in items) keys.append(key);
        keys.sort();
        if (prev == null) return keys.len() > 0 ? keys[0] : null;
        for (local i = 0; i < keys.len() - 1; i++)
            if (keys[i] == prev) return keys[i + 1];
        return null;
    }
}
class GSVehicleList extends GSList {
    constructor() {
        base.constructor();
        foreach (vid, _ in ::vehicles) items[vid] <- true;
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
    """Fresh VM with the mutation API fixture, the controlled world and the package."""
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
    vm.execute("::bridge <- D5DepotMutationProof();")
    return vm


def vm_world(vm: SQVM, fragment: str) -> None:
    """Shape the stub depot ground between exchanges (real ground would)."""
    vm.execute(fragment)


def vm_root(vm: SQVM) -> dict[str, Any]:
    return vm.get_roottable()


def drive(vm: SQVM, request: dm.DepotRequest) -> dm.DepotReadback:
    """Dispatch one request over the wire and parse the reply into Python."""
    replies = vm_root(vm)["replies"]
    before = len(replies)
    vm.execute("::bridge.Handle(" + request.to_bytes().decode() + ");")
    if len(vm_root(vm)["replies"]) == before:
        raise AssertionError(f"package dropped request {request.request_id}: no reply")
    vm.execute("::sniffer.last = last_reply_json();")
    raw = vm_root(vm)["sniffer"]["last"]
    assert len(raw.encode()) <= dm.MAX_DEPOT_MUTATION_RESPONSE_BYTES, (
        f"response for {request.request_id} exceeds "
        f"{dm.MAX_DEPOT_MUTATION_RESPONSE_BYTES} bytes"
    )
    return dm.DepotReadback.parse_for(request, raw.encode())


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
        "protocol": 10,
        "op": "observe",
        "request_id": "before-00",
        "plan": PRELAUNCH,
        "company": 0,
        "max_cost": 3000,
        "pickup": 45748,
        "delivery": 50351,
        "depot": 45487,
        "tile": None,
        "front_tile": None,
    }
    payload.update(overrides)
    return payload


def readback_payload(request: dm.DepotRequest, **overrides) -> dict:
    """A correlated success readback the handler-shaped table satisfies."""
    payload = {
        "protocol": 10,
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
    if request.front_tile is not None:
        payload["front_tile"] = request.front_tile
    if request.op == "observe":
        payload.update(
            {
                "depot_present": True,
                "front_read": DEPOT_FRONT,
                "owner": 0,
                "depot_linked": True,
                "connected_front_to_depot": False,
                "connected_depot_to_front": False,
            }
        )
    payload.update(overrides)
    return payload


def make_request(entry_index: int) -> dm.DepotRequest:
    return work._depot_exchange_request(SCHEDULE[entry_index], PRELAUNCH, PLAN)


def run_depot_vm():
    """The exact six planned exchanges in order (the production builder)."""
    vm = build_vm()
    exchanges: list[tuple[dm.DepotRequest, dm.DepotReadback]] = []
    for entry in SCHEDULE:
        request = make_request(EXCHANGES.index(entry["exchange"]))
        readback = drive(vm, request)
        probes = dm.depot_phase_outcome(
            exchanges + [(request, readback)], prelaunch_digest=PRELAUNCH, plan=PLAN
        )
        assert probes["failed"] is None, (entry["exchange"], probes["failed"])
        exchanges.append((request, readback))
    phase = dm.depot_phase_outcome(exchanges, prelaunch_digest=PRELAUNCH, plan=PLAN)
    return vm, exchanges, phase


# --- The pinned schedule and plan (drift gates) ------------------------------


def test_pinned_schedule_constants():
    assert dm.DEPOT_MUTATION_EXCHANGE_IDS == (
        "before-00",
        "demo-00",
        "road-00",
        "depot-00",
        "after-00",
        "fleet-00",
    )
    assert dm.PLANNED_DEPOT_EXCHANGES == 6
    assert dm.DEPOT_MUTATION_OPS == ("observe", "demolish", "road", "depot", "fleet")
    assert dm.DEPOT_MUTATING_OPS == ("demolish", "road", "depot")
    assert dm.DEPOT_EXCHANGE_TILES == {
        "demo-00": (45487, None),
        "road-00": (45487, 45743),
        "depot-00": (45487, 45743),
    }
    assert dm.MAX_DEPOT_MUTATION_REQUEST_BYTES == dm.MAX_DEPOT_MUTATION_RESPONSE_BYTES == 512
    assert dm.MAX_DEPOT_MUTATION_COST == 3000
    assert dm.MAX_DEPOT_MUTATION_FLEET_ROWS == 4
    assert dm.DEPOT_MUTATION_PROTOCOL == 10
    assert dm.DEPOT_MUTATION_PICKUP_TILE == 45748
    assert dm.DEPOT_MUTATION_PICKUP_FRONT_TILE == 45747
    assert dm.DEPOT_MUTATION_DELIVERY_TILE == 50351
    assert dm.DEPOT_MUTATION_DELIVERY_FRONT_TILE == 50095
    assert dm.DEPOT_MUTATION_DEPOT_TILE == 45487
    assert dm.DEPOT_MUTATION_DEPOT_FRONT_TILE == 45743
    assert dm.FUNDS_AT_F12_OPEN == FUNDS == 490257
    assert dm.DEPOT_BEFORE_GATE == {
        "depot_present": True,
        "front_read": 45743,
        "owner": 0,
        "depot_linked": True,
        "connected_front_to_depot": False,
        "connected_depot_to_front": False,
    }
    assert dm.DEPOT_AFTER_GATE == {
        "depot_present": True,
        "front_read": 45743,
        "owner": 0,
        "depot_linked": True,
        "connected_front_to_depot": True,
        "connected_depot_to_front": True,
    }


def test_plan_pinned_and_digest_stable():
    plan = dm.depot_mutation_plan()
    assert plan.company == 0 and plan.cargo == 1
    assert plan.expected_funds == FUNDS
    assert plan.max_cost == dm.MAX_DEPOT_MUTATION_COST == 3000
    assert plan.depot == 45487 and plan.depot_front == 45743
    assert plan.pickup == 45748 and plan.pickup_front == 45747
    assert plan.delivery == 50351 and plan.delivery_front == 50095
    assert plan.schedule == dm.DEPOT_MUTATION_EXCHANGE_IDS
    assert plan.request_budget == 32
    assert plan.schema_version == 1
    assert plan.digest == dm.depot_mutation_plan().digest
    assert plan.digest == work.depot_plan().digest


@pytest.mark.parametrize(
    "field, value",
    [
        ("expected_funds", 492149),
        ("max_cost", 3001),
        ("depot", 45743),
        ("depot_front", 45487),
        ("pickup", 45487),
        ("delivery", 45487),
        ("company", 1),
        ("cargo", 0),
    ],
)
def test_plan_drift_gates(field, value):
    payload = dm.depot_mutation_plan().model_dump()
    payload[field] = value
    with pytest.raises(ValueError):
        dm.DepotMutationPlan.model_validate(payload)


def test_worst_case_request_byte_audit():
    request = make_request(3)  # the widest mutating echo pair
    assert len(request.to_bytes()) < 512
    for entry_index in range(len(SCHEDULE)):
        assert len(make_request(entry_index).to_bytes()) <= dm.MAX_DEPOT_MUTATION_REQUEST_BYTES


def test_request_op_domain_refusals():
    def make(op, **overrides):
        payload = dict(
            op=op,
            request_id="demo-00",
            plan=PRELAUNCH,
            company=0,
            max_cost=3000,
            pickup=45748,
            delivery=50351,
            depot=45487,
        )
        payload.update(overrides)
        return dm.DepotRequest.model_validate(payload)

    with pytest.raises(ValueError, match="names its pinned depot tile"):
        make("demolish")
    with pytest.raises(ValueError, match="only target the pinned depot tile"):
        make("demolish", tile=45743)
    with pytest.raises(ValueError, match="only a mutating exchange carries a tile"):
        make("observe", tile=45487)
    with pytest.raises(ValueError, match="only the road and depot ops carry a front tile"):
        make("demolish", tile=45487, front_tile=45743)
    with pytest.raises(ValueError, match="name the pinned front"):
        make("road", tile=45487)
    with pytest.raises(ValueError, match="name the pinned depot front"):
        make("road", tile=45487, front_tile=45999)
    with pytest.raises(ValueError, match="needs start != end"):
        make("road", tile=45487, front_tile=45487)
    with pytest.raises(ValueError, match="needs start != end"):
        make("depot", tile=45487, front_tile=45487)
    with pytest.raises(ValueError):
        dm.DepotRequest.model_validate(base_request(max_cost=3001))


# --- The request verifier (Python trust anchor) ------------------------------


def test_request_verifier_slots():
    for entry_index in range(len(SCHEDULE)):
        request = make_request(entry_index)
        dm.verify_request_against_depot_plan(request, plan=PLAN, seal=PRELAUNCH)


def test_request_verifier_refusals():
    demo = make_request(1)
    with pytest.raises(ValueError, match="not the staged prelaunch seal"):
        dm.verify_request_against_depot_plan(demo, plan=PLAN, seal=OTHER_PLAN)
    with pytest.raises(ValueError, match="mutating request drifted"):
        dm.verify_request_against_depot_plan(
            demo.model_copy(update={"tile": 45743}), plan=PLAN, seal=PRELAUNCH
        )
    road = make_request(2)
    with pytest.raises(ValueError, match="mutating request drifted"):
        dm.verify_request_against_depot_plan(
            road.model_copy(update={"front_tile": 45999}), plan=PLAN, seal=PRELAUNCH
        )
    with pytest.raises(ValueError, match="company drifted"):
        dm.verify_request_against_depot_plan(
            demo.model_copy(update={"company": 1}), plan=PLAN, seal=PRELAUNCH
        )
    with pytest.raises(ValueError, match="pins drifted"):
        dm.verify_request_against_depot_plan(
            demo.model_copy(update={"pickup": 45487}), plan=PLAN, seal=PRELAUNCH
        )


# --- Response parsing: correlation, echoes, subsets, fleet rows --------------


def test_parse_accepts_handler_shape_without_null_keys():
    request = make_request(0)
    raw = json.dumps(readback_payload(request), separators=(",", ":")).encode()
    readback = dm.DepotReadback.parse_for(request, raw)
    assert readback.status == "READY" and readback.tile is None and readback.funds == FUNDS
    assert readback.depot_present is True and readback.owner == 0


def test_parse_ceiling_duplicate_and_correlation():
    request = make_request(0)
    with pytest.raises(ValueError, match="exceeds 512 bytes"):
        dm.DepotReadback.parse_for(request, b"0" * 513)
    body = json.dumps(readback_payload(request), separators=(",", ":"))
    duplicate = body[:-1] + ',"owner":0}'
    with pytest.raises(ValueError, match="duplicate response key"):
        dm.DepotReadback.parse_for(request, duplicate.encode())
    with pytest.raises(ValueError, match="correlation mismatch"):
        dm.DepotReadback.parse_for(
            request,
            json.dumps(
                readback_payload(request, request_id="before-01"), separators=(",", ":")
            ).encode(),
        )
    with pytest.raises(ValueError, match="correlation mismatch"):
        dm.DepotReadback.parse_for(
            request,
            json.dumps(
                readback_payload(request, max_cost=2999), separators=(",", ":")
            ).encode(),
        )
    with pytest.raises(ValueError, match="pin mismatch"):
        dm.DepotReadback.parse_for(
            request,
            json.dumps(
                readback_payload(request, pickup=45487), separators=(",", ":")
            ).encode(),
        )


def test_parse_tile_and_front_tile_echoes():
    demo = make_request(1)
    road = make_request(2)
    with pytest.raises(ValueError, match="tile echo mismatch"):
        dm.DepotReadback.parse_for(
            demo,
            json.dumps(
                readback_payload(demo, funds=FUNDS_AFTER_DEMO, cost=-100, tile=45743),
                separators=(",", ":"),
            ).encode(),
        )
    with pytest.raises(ValueError, match="front-tile echo mismatch"):
        dm.DepotReadback.parse_for(
            road,
            json.dumps(
                readback_payload(
                    road, funds=FUNDS_AFTER_ROAD, cost=200, front_tile=45999
                ),
                separators=(",", ":"),
            ).encode(),
        )
    # These pass: the echoes riding the mutating exchanges are exact.
    dm.DepotReadback.parse_for(
        road,
        json.dumps(
            readback_payload(road, funds=FUNDS_AFTER_ROAD, cost=200),
            separators=(",", ":"),
        ).encode(),
    )


def test_parse_mutation_success_carries_signed_cost_chain():
    demo = make_request(1)
    readback = dm.DepotReadback.parse_for(
        demo,
        json.dumps(
            readback_payload(demo, funds=FUNDS_AFTER_DEMO, cost=-100),
            separators=(",", ":"),
        ).encode(),
    )
    assert readback.cost == -100  # the demolish refund class may credit
    assert dm.depot_phase_outcome(
        observed_prefix(2), prelaunch_digest=PRELAUNCH, plan=PLAN
    )["funds_chain"][1]["funds_after"] == FUNDS_AFTER_DEMO


def test_parse_observe_success_requires_complete_fact_set():
    request = make_request(0)
    for missing in (
        "depot_present",
        "front_read",
        "owner",
        "depot_linked",
        "connected_front_to_depot",
        "connected_depot_to_front",
    ):
        body = readback_payload(request)
        body.pop(missing)
        with pytest.raises(ValueError, match="success readback lacks"):
            dm.DepotReadback.parse_for(
                request, json.dumps(body, separators=(",", ":")).encode()
            )


def test_parse_fleet_rows_and_count_formula():
    request = make_request(5)
    rows = [
        {"id": 0, "tile": 45743, "in_depot": True},
        {"id": 1, "tile": 45487, "in_depot": True},
    ]
    readback = dm.DepotReadback.parse_for(
        request, json.dumps(readback_payload(request, count=2, vehicles=rows),
                             separators=(",", ":")).encode()
    )
    assert readback.count == 2 and len(readback.vehicles) == 2
    with pytest.raises(ValueError, match="success readback lacks"):
        dm.DepotReadback.parse_for(
            request,
            json.dumps(readback_payload(request, count=0), separators=(",", ":")).encode(),
        )
    with pytest.raises(ValueError, match="fleet rows must ascend"):
        dm.DepotReadback.parse_for(
            request,
            json.dumps(
                readback_payload(request, count=2, vehicles=rows[::-1]),
                separators=(",", ":"),
            ).encode(),
        )
    with pytest.raises(ValueError, match="more than its pinned row budget"):
        dm.DepotReadback.parse_for(
            request,
            json.dumps(
                readback_payload(
                    request,
                    count=5,
                    vehicles=[
                        {"id": n, "tile": 45743, "in_depot": True} for n in range(5)
                    ],
                ),
                separators=(",", ":"),
            ).encode(),
        )
    with pytest.raises(ValueError, match="fleet count drifted below"):
        dm.DepotReadback.parse_for(
            request,
            json.dumps(
                readback_payload(request, count=1, vehicles=rows),
                separators=(",", ":"),
            ).encode(),
        )
    with pytest.raises(ValueError, match="success readback lacks"):
        dm.DepotReadback.parse_for(
            request,
            json.dumps(readback_payload(request, vehicles=rows), separators=(",", ":")).encode(),
        )
    with pytest.raises(ValueError, match="fleet data fields ride the fleet op only"):
        dm.DepotReadback.parse_for(
            make_request(0),
            json.dumps(
                readback_payload(make_request(0), count=0, vehicles=[]),
                separators=(",", ":"),
            ).encode(),
        )
    with pytest.raises(ValueError, match="carries fields outside its subset"):
        dm.DepotReadback.parse_for(
            request,
            json.dumps(
                readback_payload(request, count=2, vehicles=rows, depot_present=True),
                separators=(",", ":"),
            ).encode(),
        )


def test_parse_refusal_observability_boundaries():
    demo = make_request(1)
    with pytest.raises(ValueError, match="depot facts ride the observe op only"):
        dm.DepotReadback.parse_for(
            demo,
            json.dumps(
                readback_payload(demo, status="STALE_PIN", depot_present=True),
                separators=(",", ":"),
            ).encode(),
        )
    with pytest.raises(ValueError, match="refusal readback carries an unclaimed observation"):
        request = make_request(5)
        dm.DepotReadback.parse_for(
            request,
            json.dumps(
                readback_payload(request, status="PAUSED", count=0, vehicles=[]),
                separators=(",", ":"),
            ).encode(),
        )
    ceiled = dm.DepotReadback.parse_for(
        demo,
        json.dumps(
            readback_payload(demo, status="STALE_PIN", funds=FUNDS, cost=0),
            separators=(",", ":"),
        ).encode(),
    )
    assert ceiled.status == "STALE_PIN" and ceiled.tile == 45487


# --- The phase verifier: full completion, gates, funds chain ------------------


def observed_prefix(index: int) -> list[tuple[dm.DepotRequest, dm.DepotReadback]]:
    exchanges = []
    for entry_index, entry in enumerate(SCHEDULE[:index]):
        request = make_request(entry_index)
        if entry["op"] == "demolish":
            body = readback_payload(request, funds=FUNDS_AFTER_DEMO, cost=-100)
        elif entry["op"] == "road":
            body = readback_payload(request, funds=FUNDS_AFTER_ROAD, cost=200)
        elif entry["op"] == "depot":
            body = readback_payload(request, funds=FUNDS_AFTER_DEPOT, cost=1200)
        elif entry["exchange"] == "after-00":
            body = readback_payload(
                request,
                funds=FUNDS_AFTER_DEPOT,
                depot_linked=True,
                connected_front_to_depot=True,
                connected_depot_to_front=True,
            )
        elif entry["op"] == "fleet":
            body = readback_payload(request, funds=FUNDS_AFTER_DEPOT, count=0, vehicles=[])
        else:
            body = readback_payload(request)
        exchanges.append((request, dm.DepotReadback.parse_for(
            request, json.dumps(body, separators=(",", ":")).encode()
        )))
    return exchanges


def refused_payload(request: dm.DepotRequest, *, status: str) -> dict:
    """A refusal frame: echoes and funds only, never the observation set."""
    body = readback_payload(request, status=status)
    for name in dm.DEPOT_BEFORE_GATE:
        body.pop(name, None)
    return body


def diverged_exchange(index: int, **overrides) -> tuple[dm.DepotRequest, dm.DepotReadback]:
    request = make_request(index)
    if request.op == "observe":
        overrides.setdefault("depot_present", True)
        overrides.setdefault("front_read", DEPOT_FRONT)
        overrides.setdefault("owner", 0)
        overrides.setdefault("depot_linked", True)
        overrides.setdefault("connected_front_to_depot", index == 0)
        overrides.setdefault("connected_depot_to_front", index == 0)
        overrides.setdefault("funds", FUNDS)
    body = readback_payload(request, **overrides)
    return request, dm.DepotReadback.parse_for(
        request, json.dumps(body, separators=(",", ":")).encode()
    )


def complete_exchange_set() -> list[tuple[dm.DepotRequest, dm.DepotReadback]]:
    prefix = observed_prefix(4)  # through depot-00
    after = diverged_exchange(
        4,
        funds=FUNDS_AFTER_DEPOT,
        connected_front_to_depot=True,
        connected_depot_to_front=True,
    )
    fleet = diverged_exchange(
        5,
        funds=FUNDS_AFTER_DEPOT,
        count=0,
        vehicles=[],
    )
    return [*prefix, after, fleet]


def test_full_schedule_completes_and_gate_passes():
    exchanges = complete_exchange_set()
    phase = dm.depot_phase_outcome(exchanges, prelaunch_digest=PRELAUNCH, plan=PLAN)
    assert phase["verification"] == "DEPOT_MUTATION_COMPLETE"
    assert phase["failed"] is None and phase["pending"] == []
    assert phase["state_changed"] is True
    assert phase["gate"]["verdict"] == "DEPOT_MUTATION_GATE_PASSES"
    assert [row["funds_after"] for row in phase["funds_chain"]] == [
        FUNDS,
        FUNDS_AFTER_DEMO,
        FUNDS_AFTER_ROAD,
        FUNDS_AFTER_DEPOT,
        FUNDS_AFTER_DEPOT,
        FUNDS_AFTER_DEPOT,
    ]
    assert [row["cost"] for row in phase["funds_chain"][1:4]] == [-100, 200, 1200]
    assert [row["exchange"] for row in phase["mutations"]] == ["demo-00", "road-00", "depot-00"]
    assert phase["fleet"]["count"] == 0
    assert phase["observations"]["before-00"]["facts"]["connected_front_to_depot"] is False
    assert phase["observations"]["after-00"]["facts"]["connected_front_to_depot"] is True
    assert len(phase["receipts"]) == 6
    assert phase["receipts"][0]["schema"] == "company-depot-mutation-receipt-v1"
    assert phase["receipts"][1]["state_changed"] is True
    assert phase["receipts"][5]["vehicles"] == []


def test_before_gate_reproduces_the_e58_diagnosis_verbatim():
    """Each of the six before-gate facts diverging halts with the raw value
    legible in the STALE_PIN halt record, before any command."""
    for fact, wrong in (
        ("depot_present", False),
        ("front_read", 45999),
        ("owner", 1),
        ("depot_linked", False),
        ("connected_front_to_depot", True),
        ("connected_depot_to_front", True),
    ):
        exchanges = [diverged_exchange(0, **{fact: wrong})]
        phase = dm.depot_phase_outcome(exchanges, prelaunch_digest=PRELAUNCH, plan=PLAN)
        assert phase["failed"]["label"] == "before-00"
        assert phase["failed"]["world_state"] == "HALTED_BEFORE_MUTATION"
        assert "STALE_PIN" in phase["failed"]["error"]
        assert f"{fact}: measured" in phase["failed"]["error"]
        assert phase["pending"] == list(dm.DEPOT_MUTATION_EXCHANGE_IDS[1:])


def test_after_gate_demands_both_directions_true():
    for fact in (
        "connected_front_to_depot",
        "connected_depot_to_front",
        "depot_present",
        "front_read",
        "owner",
        "depot_linked",
    ):
        overrides = (
            {fact: False}
            if fact in (
                "depot_present",
                "depot_linked",
                "connected_front_to_depot",
                "connected_depot_to_front",
            )
            else ({fact: 0} if fact == "owner" else {fact: 45999})
        )
        overrides["funds"] = FUNDS_AFTER_DEPOT
        exchanges = complete_exchange_set()[:4]
        exchanges.append(diverged_exchange(4, **overrides))
        phase = dm.depot_phase_outcome(exchanges, prelaunch_digest=PRELAUNCH, plan=PLAN)
        assert phase["failed"]["label"] == "after-00"
        assert "STALE_PIN" in phase["failed"]["error"]


def test_fleet_gate_lists_per_vehicle_rows_on_a_halt():
    exchanges = complete_exchange_set()[:5]
    rows = [
        {"id": 0, "tile": 45743, "in_depot": True},
        {"id": 1, "tile": 50351, "in_depot": False},
    ]
    exchanges.append(
        diverged_exchange(5, funds=FUNDS_AFTER_DEPOT, count=2, vehicles=rows)
    )
    phase = dm.depot_phase_outcome(exchanges, prelaunch_digest=PRELAUNCH, plan=PLAN)
    assert phase["failed"]["label"] == "fleet-00"
    assert "zero fleet" in phase["failed"]["error"]
    assert "in_depot False" in phase["failed"]["error"]


def test_funds_chain_break_halts_verbatim():
    exchanges = observed_prefix(2)
    exchanges.append(diverged_exchange(2, funds=FUNDS_AFTER_DEMO, cost=200))
    phase = dm.depot_phase_outcome(exchanges, prelaunch_digest=PRELAUNCH, plan=PLAN)
    assert phase["failed"]["label"] == "road-00"
    assert "funds chain broke" in phase["failed"]["error"]


def test_mutating_exchange_refuses_over_the_attempt_ceiling():
    exchanges = observed_prefix(2)
    exchanges.append(
        diverged_exchange(2, funds=FUNDS_AFTER_DEMO - 3001, cost=3001)
    )
    phase = dm.depot_phase_outcome(exchanges, prelaunch_digest=PRELAUNCH, plan=PLAN)
    assert phase["failed"]["label"] == "road-00"
    assert "attempt ceiling" in phase["failed"]["error"]


def test_refusal_and_malformed_observations_fail_closed():
    exchanges = observed_prefix(1)
    exchanges.append(
        diverged_exchange(1, status="UNSUPPORTED_NATIVE_FACT", funds=FUNDS, cost=0)
    )
    phase = dm.depot_phase_outcome(exchanges, prelaunch_digest=PRELAUNCH, plan=PLAN)
    assert phase["failed"]["label"] == "demo-00"
    assert phase["failed"]["status"] == "UNSUPPORTED_NATIVE_FACT"
    assert phase["failed"]["world_state"] == "HALTED_MID_MUTATION"
    malformed = dm.depot_phase_outcome(
        [(make_request(0), ValueError("torn frame"))],
        prelaunch_digest=PRELAUNCH,
        plan=PLAN,
    )
    assert malformed["failed"]["status"] == "MALFORMED"
    refused_only = dm.depot_phase_outcome(
        [
            (
                make_request(0),
                dm.DepotReadback.parse_for(
                    make_request(0),
                    json.dumps(
                        refused_payload(make_request(0), status="PAUSED"),
                        separators=(",", ":"),
                    ).encode(),
                ),
            )
        ],
        prelaunch_digest=PRELAUNCH,
        plan=PLAN,
    )
    assert refused_only["failed"]["label"] == "before-00"
    assert refused_only["verification"] == "DEPOT_MUTATION_INCOMPLETE"
    assert refused_only["gate"]["verdict"] == "DEPOT_MUTATION_GATE_UNDECIDED_INCOMPLETE"


def test_out_of_order_and_unscheduled_exchanges_refuse():
    request = make_request(2)
    phase = dm.depot_phase_outcome(
        [(request, diverged_exchange(2)[1])], prelaunch_digest=PRELAUNCH, plan=PLAN
    )
    assert phase["failed"]["label"] == "road-00"
    assert "out of order: expected before-00" in phase["failed"]["error"]
