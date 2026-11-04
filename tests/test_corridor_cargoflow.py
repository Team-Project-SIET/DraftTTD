"""Controlled offline tests for the D5-CARGOFLOW-1 wire contract (protocol 10).

The contract under test is ``app/simulation/openttd/corridor_cargoflow.py``
and the additive read-only probe handler shipped in
``app/simulation/openttd/d5_cargoflow_package/main.nut``. The shipped package
runs inside the real Squirrel VM against a stub world that reproduces the
civil calendar (365-day year, driver-rate day advance), the two pinned
stations' waiting/planned families and the two pinned industries' stock,
production and transported values with the 15.3 ``-1`` fact families verbatim;
every dispatched reply is re-parsed through the protocol-10 wire contract,
never through the package's own words.

The probe is one schedule generation: a pinned fourteen-sample ladder whose
first sample latches the anchor once, whose later samples sleep in-package to
exactly anchor + their offset, and whose wait-window machinery refuses pause,
tick regression and any overshoot of the exact ladder day. Every
verification here is offline: nothing launches OpenTTD, connects to an
AdminPort or writes any native or save state — only the tests' own VM world
is mutated.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from squirrel import SQVM

from app.simulation.openttd import corridor_cargoflow as cf
from app.simulation.openttd.corridor_freight_v2 import FUNDS_AT_DEPOT_MUTATION_CLOSE
from app.simulation.openttd.proof import corridor_cargoflow_native as work

REPO = Path(__file__).resolve().parents[1]
PACKAGE = REPO / "app" / "simulation" / "openttd" / "d5_cargoflow_package"

PRELAUNCH = "a" * 64
OTHER_PLAN = "b" * 64

SCHEDULE = work.cargoflow_schedule()
PLAN = work.cargoflow_pipeline_plan()
EXCHANGES = list(cf.CARGOFLOW_EXCHANGE_IDS)
FUNDS = FUNDS_AT_DEPOT_MUTATION_CLOSE

# The stub world's fixed admission day: the anchor the first sample latches.
ANCHOR = 712223

API = """
::events <- [];
::replies <- [];
::send_ok <- true;
::ticks <- 0;
::sniffer <- {last = "missing"};
class GSController {
    function GetTick() { return ::ticks; }
    function Sleep(ticks) {
        if (ticks != 1) throw "unexpected script sleep";
        if (!::ticks_freeze) ::ticks = ::ticks + 1;
        ::day = ::day + ::day_rate;
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
::funds <- 489650;
::paused <- false;
::valid_company <- true;
::second_company <- 1;
::mode_ok <- true;
::stations_valid <- true;
::ticks_freeze <- false;
::day_rate <- 1;
::day <- 712223;
::stop_at <- -1;
::stops <- {};
::industries <- {};
::cur_company <- -1;
function cargoflow_seed_stop(sid, w, from0, from1, pl, pl0, pl1) {
    ::stops[sid] <- {w = w, from0 = from0, from1 = from1,
                     pl = pl, pl0 = pl0, pl1 = pl1};
}
function cargoflow_seed_industry(ind, stock, prod, trans) {
    ::industries[ind] <- {stock = stock, prod = prod, trans = trans};
}
/* The pinned depot-chain world of record at admission: the producer
 * (industry 0) carries no accepted slot so its stock is the 15.3 -1 fact,
 * the acceptor (industry 1) carries stock 0 and the -1 non-producer fact,
 * and both pinned stops sit with empty families. */
cargoflow_seed_industry(0, -1, 104, 0);
cargoflow_seed_industry(1, 0, -1, 0);
cargoflow_seed_stop(0, 0, 0, 0, 0, 0, 0);
cargoflow_seed_stop(2, 0, 0, 0, 0, 0, 0);
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
class GSDate {
    static function GetCurrentDate() { return ::day; }
    static function GetYear(day) { return day / 365; }
    static function GetMonth(day) { return civil_month(day); }
    static function GetDayOfMonth(day) { return civil_day_of_month(day); }
}
::month_lengths <- [31,28,31,30,31,30,31,31,30,31,30,31];
function civil_month(day) {
    local rem = day % 365;
    local month = 1;
    foreach (length in ::month_lengths) {
        if (rem < length) return month;
        rem = rem - length;
        month = month + 1;
    }
    throw "D5_TEST_CALENDAR";
}
function civil_day_of_month(day) {
    local rem = day % 365;
    foreach (length in ::month_lengths) {
        if (rem < length) return rem + 1;
        rem = rem - length;
    }
    throw "D5_TEST_CALENDAR";
}
class GSStation {
    static function IsValidStation(sid) { return ::stations_valid && (sid in ::stops); }
    static function GetCargoWaiting(sid, _) {
        local stop = (sid in ::stops) ? ::stops[sid] : null;
        return stop == null ? -1 : stop.w;
    }
    static function GetCargoWaitingFrom(sid, from, _) {
        local stop = (sid in ::stops) ? ::stops[sid] : null;
        if (stop == null) return -1;
        /* The stub keys its per-source forms by the absolute source
         * station of record (0 the pickup stop, 2 the bay stop), the same
         * naming the wire fields carry. */
        return from == 0 ? stop.from0 : stop.from1;
    }
    static function GetCargoPlanned(sid, _) {
        local stop = (sid in ::stops) ? ::stops[sid] : null;
        return stop == null ? -1 : stop.pl;
    }
    static function GetCargoPlannedFrom(sid, from, _) {
        local stop = (sid in ::stops) ? ::stops[sid] : null;
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
}
function json_cell(v) {
    if (v == null) return "null";
    if (typeof v == "bool") return v ? "true" : "false";
    if (typeof v == "string") return "\\"" + v + "\\"";
    if (typeof v == "array") {
        local out = "[";
            out = out + "\\"" + k + "\\":" + json_cell(e);
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


def civil_ymd(day: int) -> tuple[int, int, int]:
    """The stub calendar's civil date (no leap, 365-day year)."""
    year, rem = divmod(day, 365)
    month = 1
    for length in (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31):
        if rem < length:
            return year, month, rem + 1
        rem -= length
        month += 1
    raise AssertionError("unreachable")


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
    vm.execute("::bridge <- D5CargoFlowProof();")
    return vm


def vm_root(vm: SQVM) -> dict[str, Any]:
    return vm.get_roottable()


def seed_stop(vm: SQVM, sid: int, **fields: int) -> None:
    """Shape one stub stop's measured families between exchanges."""
    for name, value in fields.items():
        vm.execute(f"::stops[{sid}].{name} = {value};")


def seed_industry(vm: SQVM, ind: int, **fields: int) -> None:
    """Shape one stub industry's measured facts between exchanges."""
    for name, value in fields.items():
        vm.execute(f"::industries[{ind}].{name} = {value};")


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
    """A valid-shaped raw request payload for the handler tests."""
    payload = {
        "protocol": 10,
        "op": "sample",
        "request_id": "sample-00",
        "plan": PRELAUNCH,
        "company": 0,
        "max_cost": 0,
        "pickup": 45748,
        "delivery": 50862,
        "depot": 45487,
        "offset": 0,
    }
    payload.update(overrides)
    return payload


def make_request(entry_index: int) -> cf.CargoFlowRequest:
    return work._cargoflow_exchange_request(SCHEDULE[entry_index], PRELAUNCH, PLAN)


def ready_payload(request: cf.CargoFlowRequest, anchor: int = ANCHOR, **overrides) -> dict:
    """A READY sample body echoing the request with the full observation set."""
    offset = int(request.offset)
    year, month, day_of_month = civil_ymd(anchor + offset)
    payload: dict = {
        "protocol": 10,
        "op": "sample",
        "request_id": request.request_id,
        "plan": request.plan,
        "company": request.company,
        "max_cost": request.max_cost,
        "pickup": request.pickup,
        "delivery": request.delivery,
        "depot": request.depot,
        "offset": request.offset,
        "status": "READY",
        "funds": FUNDS,
        "cost": 0,
        "anchor": anchor,
        "tick": 74 * (offset + 1),
        "day": anchor + offset,
        "year": year,
        "month": month,
        "day_of_month": day_of_month,
        "stock_pickup": -1,
        "stock_bay": 0,
        "wait_pickup": 0,
        "wait_pickup_from0": 0,
        "wait_pickup_from1": 0,
        "wait_bay": 0,
        "wait_bay_from0": 0,
        "wait_bay_from1": 0,
        "count_pickup": 0,
        "count_bay": 0,
        "planned_pickup_from0": 0,
        "planned_pickup_from1": 0,
        "planned_bay_from0": 0,
        "planned_bay_from1": 0,
        "prod_pickup": 104,
        "prod_bay": -1,
        "trans_pickup": 0,
        "trans_bay": 0,
    }
    payload.update(overrides)
    return payload


def window_payload(
    request: cf.CargoFlowRequest, /, status: str, *, anchor: int, tick: int, day: int
) -> dict:
    """A WINDOW_EXHAUSTED/CLOCK_STALLED frame with its exact echo subset."""
    payload = {key: getattr(request, key) for key in request.model_dump()}
    payload.update(
        {
            "status": status,
            "funds": FUNDS,
            "cost": 0,
            "anchor": anchor,
            "tick": tick,
            "day": day,
        }
    )
    return payload


def parse_from(request: cf.CargoFlowRequest, payload: dict) -> cf.CargoFlowReadback:
    raw = json.dumps(payload, separators=(",", ":")).encode()
    return cf.CargoFlowReadback.parse_for(request, raw)


def drive(vm: SQVM, request: cf.CargoFlowRequest) -> cf.CargoFlowReadback:
    """Dispatch one request over the wire and parse the reply into Python."""
    replies = vm_root(vm)["replies"]
    before = len(replies)
    vm.execute("::bridge.Handle(" + request.to_bytes().decode() + ");")
    if len(vm_root(vm)["replies"]) == before:
        raise AssertionError(f"package dropped request {request.request_id}: no reply")
    vm.execute("::sniffer.last = last_reply_json();")
    raw = vm_root(vm)["sniffer"]["last"]
    assert len(raw.encode()) <= cf.MAX_CARGOFLOW_RESPONSE_BYTES, (
        f"response for {request.request_id} exceeds {cf.MAX_CARGOFLOW_RESPONSE_BYTES} bytes"
    )
    return cf.CargoFlowReadback.parse_for(request, raw.encode())


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


def run_probe_vm() -> tuple[SQVM, list[tuple[cf.CargoFlowRequest, cf.CargoFlowReadback]], dict]:
    """The exact fourteen planned exchanges in order (the production path)."""
    vm = build_vm()
    exchanges: list[tuple[cf.CargoFlowRequest, cf.CargoFlowReadback]] = []
    for index, entry in enumerate(SCHEDULE):
        request = make_request(index)
        readback = drive(vm, request)
        probes = cf.cargoflow_phase_outcome(
            exchanges + [(request, readback)], prelaunch_digest=PRELAUNCH, plan=PLAN
        )
        assert probes["failed"] is None, (entry["exchange"], probes["failed"])
        exchanges.append((request, readback))
        assert readback.status == "READY" and readback.anchor == ANCHOR
        assert readback.day == ANCHOR + int(entry["offset"])
    phase = cf.cargoflow_phase_outcome(exchanges, prelaunch_digest=PRELAUNCH, plan=PLAN)
    return vm, exchanges, phase


# --- The pinned schedule and plan (drift gates) ------------------------------


def test_pinned_schedule_constants():
    assert cf.CARGOFLOW_EXCHANGE_IDS == (
        "sample-00",
        "sample-01",
        "sample-02",
        "sample-03",
        "sample-04",
        "sample-05",
        "sample-06",
        "sample-07",
        "sample-08",
        "sample-09",
        "sample-10",
        "sample-11",
        "sample-12",
        "sample-13",
    )
    assert cf.PLANNED_CARGOFLOW_EXCHANGES == 14
    assert cf.CARGOFLOW_SAMPLE_OFFSETS == (0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65)
    assert cf.CARGOFLOW_SPAN_DAYS == 65 and cf.CARGOFLOW_OFFSET_CAP == 65
    assert cf.CARGOFLOW_OPS == ("sample",)
    assert cf.CARGOFLOW_REQUEST_BUDGET == 32
    assert cf.MAX_CARGOFLOW_REQUEST_BYTES == 512
    assert cf.MAX_CARGOFLOW_RESPONSE_BYTES == 1400
    assert cf.CARGOFLOW_PROTOCOL == 10
    assert cf.CARGOFLOW_PICKUP_TILE == 45748 and cf.CARGOFLOW_BAY_TILE == 50862
    assert cf.CARGOFLOW_DEPOT_TILE == 45487
    assert cf.CARGOFLOW_PICKUP_FRONT_TILE == 45747
    assert cf.CARGOFLOW_BAY_FRONT_TILE == 50863
    assert cf.CARGOFLOW_DEPOT_FRONT_TILE == 45743
    assert cf.CARGOFLOW_PICKUP_SID == 0 and cf.CARGOFLOW_BAY_SID == 2
    assert cf.CARGOFLOW_PICKUP_IND == 0 and cf.CARGOFLOW_BAY_IND == 1
    assert cf.CARGOFLOW_COMPANY == 0 and cf.CARGOFLOW_CARGO == 1
    assert cf.CARGOFLOW_WAIT_MAX_TICKS == 2048
    assert cf.CARGOFLOW_WAIT_DAY_CAP == 60
    assert cf.CARGOFLOW_ATTEMPT_SCHEMA_VERSION == 1
    assert cf.FUNDS_AT_DEPOT_MUTATION_CLOSE == FUNDS == 489650


def test_status_family_of_record():
    assert cf._CARGOFLOW_SAMPLE_FIELDS == (
        "anchor",
        "tick",
        "day",
        "year",
        "month",
        "day_of_month",
        "stock_pickup",
        "stock_bay",
        "wait_pickup",
        "wait_pickup_from0",
        "wait_pickup_from1",
        "wait_bay",
        "wait_bay_from0",
        "wait_bay_from1",
        "count_pickup",
        "count_bay",
        "planned_pickup_from0",
        "planned_pickup_from1",
        "planned_bay_from0",
        "planned_bay_from1",
        "prod_pickup",
        "prod_bay",
        "trans_pickup",
        "trans_bay",
    )
    assert cf._CARGOFLOW_WINDOW_ECHO_FIELDS == ("anchor", "tick", "day")
    assert cf._CARGOFLOW_WINDOW_ECHO_STATUS == frozenset(
        {"WINDOW_EXHAUSTED", "CLOCK_STALLED"}
    )
    assert cf._CARGOFLOW_REFUSAL_STATUS == frozenset(
        {
            "UNSUPPORTED_NATIVE_FACT",
            "INVALID_COMPANY",
            "PAUSED",
            "STALE_PIN",
            "OUT_OF_ORDER",
            "WINDOW_EXHAUSTED",
            "CLOCK_STALLED",
        }
    )


def test_plan_pinned_and_digest_stable():
    plan = cf.cargoflow_plan()
    assert plan.company == 0 and plan.cargo == 1
    assert plan.expected_funds == FUNDS
    assert (plan.pickup, plan.pickup_front) == (45748, 45747)
    assert (plan.delivery, plan.delivery_front) == (50862, 50863)
    assert (plan.depot, plan.depot_front) == (45487, 45743)
    assert plan.pickup_sid == 0 and plan.bay_sid == 2
    assert plan.pickup_industry == 0 and plan.bay_industry == 1
    assert plan.sample_span_days == 65
    assert plan.schedule == cf.CARGOFLOW_EXCHANGE_IDS
    assert plan.request_budget == 32
    assert plan.schema_version == 1
    assert plan.digest == cf.cargoflow_plan().digest == PLAN.digest
    assert plan == PLAN


@pytest.mark.parametrize(
    "field, value",
    [
        ("expected_funds", 492149),
        ("sample_span_days", 60),
        ("pickup_industry", 1),
        ("bay_industry", 0),
        ("pickup_sid", 2),
        ("bay_sid", 0),
        ("company", 1),
        ("cargo", 2),
    ],
)
def test_plan_field_drift_refused(field, value):
    payload = cf.cargoflow_plan().model_dump()
    payload[field] = value
    with pytest.raises(ValueError):
        cf.CargoFlowPlan.model_validate(payload)


# --- The bounded wire: exact request bytes and the 512 ceiling ----------------


def test_exact_request_bytes_of_record():
    request = make_request(0)
    expected = (
        '{"company":0,'
        '"delivery":50862,'
        '"depot":45487,'
        '"max_cost":0,'
        '"offset":0,'
        '"op":"sample",'
        '"pickup":45748,'
        f'"plan":"{PRELAUNCH}",'
        '"protocol":10,'
        '"request_id":"sample-00"}'
    )
    assert request.to_bytes().decode() == expected


def test_request_slots_of_record():
    anchor = make_request(0)
    assert anchor.op == "sample" and anchor.offset == 0
    late = make_request(5)
    assert late.request_id == "sample-05" and late.offset == 25
    last = make_request(13)
    assert last.request_id == "sample-13" and last.offset == 65


def test_worst_case_request_byte_audit_is_211():
    request = make_request(13)
    assert len(request.to_bytes()) == 211
    assert len(make_request(0).to_bytes()) == 210
    for entry_index in range(len(SCHEDULE)):
        assert len(make_request(entry_index).to_bytes()) <= 512


def test_request_identity_domain_refusals():
    def make(**overrides):
        payload = dict(
            op="sample",
            request_id="sample-00",
            plan=PRELAUNCH,
            company=0,
            max_cost=0,
            pickup=45748,
            delivery=50862,
            depot=45487,
            offset=0,
        )
        payload.update(overrides)
        return cf.CargoFlowRequest.model_validate(payload)

    with pytest.raises(ValueError, match="outside the pinned ladder"):
        make(request_id="other-00")
    with pytest.raises(ValueError, match="offset drifted from its planned"):
        make(request_id="sample-05", offset=20)
    with pytest.raises(ValueError, match="less than or equal to 65"):
        make(request_id="sample-13", offset=66)
    with pytest.raises(ValueError):
        make(protocol=9)  # the request protocol family is fixed on the wire
    with pytest.raises(ValueError):
        make(company=15)  # outside the native company domain


def test_request_verifier_slots():
    for entry_index in range(len(SCHEDULE)):
        request = make_request(entry_index)
        cf.verify_request_against_cargoflow_plan(request, plan=PLAN, seal=PRELAUNCH)


def test_request_verifier_refusals():
    anchor = make_request(0)
    with pytest.raises(ValueError, match="not the staged prelaunch seal"):
        cf.verify_request_against_cargoflow_plan(anchor, plan=PLAN, seal=OTHER_PLAN)
    late = make_request(5)
    with pytest.raises(ValueError, match="offset drifted"):
        cf.verify_request_against_cargoflow_plan(
            late.model_copy(update={"offset": 20}), plan=PLAN, seal=PRELAUNCH
        )
    with pytest.raises(ValueError, match="company drifted"):
        cf.verify_request_against_cargoflow_plan(
            anchor.model_copy(update={"company": 1}), plan=PLAN, seal=PRELAUNCH
        )
    with pytest.raises(ValueError, match="pins drifted"):
        cf.verify_request_against_cargoflow_plan(
            anchor.model_copy(update={"pickup": 45487}), plan=PLAN, seal=PRELAUNCH
        )


# --- Response parsing: correlation, echoes, subsets, ladder -------------------


def test_parse_accepts_handler_shape():
    request = make_request(0)
    readback = parse_from(request, ready_payload(request))
    assert readback.status == "READY" and readback.anchor == ANCHOR
    assert readback.day == ANCHOR and readback.day_of_month == civil_ymd(ANCHOR)[2]
    assert readback.stock_pickup == -1 and readback.prod_bay == -1
    assert readback.wait_pickup == 0 and readback.trans_pickup == 0


def test_parse_ceiling_duplicate_and_correlation():
    request = make_request(0)
    with pytest.raises(ValueError, match="exceeds 1400 bytes"):
        cf.CargoFlowReadback.parse_for(request, b"0" * 1401)
    body = json.dumps(ready_payload(request), separators=(",", ":"))
    duplicate = body[:-1] + ',"stock_bay":0}'
    with pytest.raises(ValueError, match="duplicate response key"):
        cf.CargoFlowReadback.parse_for(request, duplicate.encode())
    with pytest.raises(ValueError, match="correlation mismatch"):
        cf.CargoFlowReadback.parse_for(
            request,
            json.dumps(ready_payload(request, request_id="sample-01", day=ANCHOR + 5),
                       separators=(",", ":")).encode(),
        )
    with pytest.raises(ValueError, match="correlation mismatch"):
        cf.CargoFlowReadback.parse_for(
            request,
            json.dumps(ready_payload(request, plan=OTHER_PLAN), separators=(",", ":")).encode(),
        )
    with pytest.raises(ValueError, match="pin mismatch"):
        cf.CargoFlowReadback.parse_for(
            request,
            json.dumps(ready_payload(request, pickup=45487), separators=(",", ":")).encode(),
        )


def test_parse_ready_requires_the_full_observation_set():
    request = make_request(0)
    payload = ready_payload(request)
    payload.pop("stock_bay")
    with pytest.raises(ValueError, match="sample success readback lacks"):
        parse_from(request, payload)
    stripped = ready_payload(request)
    for name in cf._CARGOFLOW_SAMPLE_FIELDS:
        stripped.pop(name)
    with pytest.raises(ValueError, match="sample success readback lacks"):
        parse_from(request, stripped)


def test_refusal_frames_carry_no_observation_set():
    request = make_request(0)
    refusal = {key: getattr(request, key) for key in request.model_dump()}
    refusal.update({"status": "STALE_PIN", "funds": FUNDS, "cost": 0})
    assert parse_from(request, refusal).status == "STALE_PIN"
    with pytest.raises(ValueError, match="unclaimed observation set"):
        parse_from(request, {**refusal, "day": ANCHOR})
    for status in ("OUT_OF_ORDER", "INVALID_COMPANY", "PAUSED", "UNSUPPORTED_NATIVE_FACT"):
        assert parse_from(request, {**refusal, "status": status}).status == status
    with pytest.raises(ValueError):
        parse_from(request, {**refusal, "status": "SURVEY_COMPLETE"})


def test_window_echoes_parse_and_outside_fields_refuse():
    request = make_request(3)
    echo = window_payload(request, "WINDOW_EXHAUSTED", anchor=ANCHOR, tick=60, day=ANCHOR + 18)
    readback = parse_from(request, echo)
    assert readback.status == "WINDOW_EXHAUSTED"
    assert readback.anchor == ANCHOR and readback.tick == 60 and readback.day == ANCHOR + 18
    bare = window_payload(request, "WINDOW_EXHAUSTED", anchor=ANCHOR, tick=60, day=ANCHOR + 18)
    for name in ("anchor", "tick", "day"):
        bare.pop(name)
    assert parse_from(request, bare).status == "WINDOW_EXHAUSTED"
    echo["wait_pickup"] = 0
    with pytest.raises(ValueError, match="outside its window echo subset"):
        parse_from(request, echo)
    stalled = parse_from(
        request,
        {**window_payload(request, "CLOCK_STALLED", anchor=ANCHOR, tick=5, day=ANCHOR + 6)},
    )
    assert stalled.status == "CLOCK_STALLED"


def test_ready_ladder_day_is_checked_against_the_anchor():
    request = make_request(5)
    with pytest.raises(ValueError, match="sample day ladder diverged"):
        parse_from(request, ready_payload(request, day=ANCHOR + 30))
    # A shifted anchor whose day does not move with it breaks the ladder.
    with pytest.raises(ValueError, match="sample day ladder diverged"):
        parse_from(request, ready_payload(request, anchor=ANCHOR + 1, day=ANCHOR + 27))
    # A shifted anchor with its day intact is a legal readback on the model;
    # the phase verifier is what refuses a mid-ladder re-anchor.
    parsed = cf.CargoFlowReadback.model_validate(
        ready_payload(request, anchor=ANCHOR + 1)
    )
    day, anchor = parsed.day, parsed.anchor
    assert isinstance(day, int) and isinstance(anchor, int)
    assert day - anchor == 25


def test_worst_case_response_byte_audit_is_833():
    request = make_request(13)
    peak = dict(
        anchor=2147483647 - 65,
        tick=2147483647,
        day=2147483647,
        year=2147483647 - 65,
        month=12,
        day_of_month=31,
        stock_pickup=65535,
        stock_bay=65535,
        wait_pickup=2147483647,
        wait_pickup_from0=2147483647,
        wait_pickup_from1=2147483647,
        wait_bay=2147483647,
        wait_bay_from0=2147483647,
        wait_bay_from1=2147483647,
        count_pickup=2147483647,
        count_bay=2147483647,
        planned_pickup_from0=2147483647,
        planned_pickup_from1=2147483647,
        planned_bay_from0=2147483647,
        planned_bay_from1=2147483647,
        prod_pickup=2147483647,
        prod_bay=2147483647,
        trans_pickup=2147483647,
        trans_bay=2147483647,
    )
    payload = ready_payload(request, **peak)
    raw = json.dumps(payload, separators=(",", ":")).encode()
    assert len(raw) == 833  # the wire-capped ceiling stays far below the 1400 bound
    readback = cf.CargoFlowReadback.parse_for(request, raw)
    assert readback.day == 2147483647 and readback.stock_pickup == 65535
    # The realistic READY body measured against the pinned funds/civil calendar.
    realistic = json.dumps(ready_payload(request), separators=(",", ":")).encode()
    assert len(realistic) == 664
    assert cf.CargoFlowReadback.parse_for(request, realistic).anchor == ANCHOR


# --- The phase verifier: full completion and verdict slicing ------------------


def test_full_ladder_completes_and_samples_the_ladder_exactly():
    _, _, phase = run_probe_vm()
    assert phase["verification"] == "CARGOFLOW_COMPLETE"
    assert phase["schema"] == "cargo-flow-phase-outcome-v1"
    assert phase["failed"] is None and not phase["pending"]
    assert phase["seal"] == PRELAUNCH and phase["plan_digest"] == PLAN.digest
    assert phase["offset_ladder"] == list(cf.CARGOFLOW_SAMPLE_OFFSETS)
    assert phase["anchor"] == ANCHOR
    assert sorted(phase["samples"]) == list(cf.CARGOFLOW_SAMPLE_OFFSETS)
    assert [receipt["request_id"] for receipt in phase["receipts"]] == EXCHANGES
    assert all(
        receipt["verification"] == "CARGOFLOW_SAMPLE_MEASURED" for receipt in phase["receipts"]
    )
    assert phase["receipts"][0]["schema"] == "cargo-flow-sample-receipt-v1"
    assert phase["sampled_months"] == [[1951, 4], [1951, 5], [1951, 6]]
    assert set(phase["series"]) == set(cf._CARGOFLOW_SAMPLE_FIELDS)
    assert phase["series"]["wait_pickup"] == [0] * 14
    assert phase["series"]["stock_pickup"] == [-1] * 14
    assert phase["series"]["stock_bay"] == [0] * 14
    assert phase["series"]["prod_pickup"] == [104] * 14
    assert phase["series"]["prod_bay"] == [-1] * 14
    assert phase["verdict"]["verdict"] == "DISPATCH_STOCKPILE_STATIC"
    assert phase["observation_kinds"] == ("MEASURED", "REFUSED", "MISSING", "MALFORMED")


def built_ladder(wait_pickup=None, stock_pickup=None, stock_bay=None):
    """A synthetic ladder built Python-side from per-sample series slices."""
    exchanges = []
    for index in range(len(SCHEDULE)):
        request = make_request(index)
        overrides: dict[str, Any] = {}
        if wait_pickup is not None:
            overrides["wait_pickup"] = wait_pickup[index]
        if stock_pickup is not None:
            overrides["stock_pickup"] = stock_pickup[index]
        if stock_bay is not None:
            overrides["stock_bay"] = stock_bay[index]
        readback = cf.CargoFlowReadback.model_validate(ready_payload(request, **overrides))
        exchanges.append((request, readback))
    return exchanges


@pytest.mark.parametrize(
    "wait_pickup, stock_pickup, stock_bay, verdict",
    [
        ([0, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5], [0] * 14, [0] * 14, "DISPATCH_OBSERVED_LATE"),
        (
            [0] * 14,
            [-1, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
            [0] * 14,
            "DISPATCH_REFUSED_AT_SELECTOR",
        ),
        (
            [0] * 14,
            [0] * 14,
            [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26],
            "DISPATCH_REFUSED_AT_SELECTOR",
        ),
        ([0] * 14, [-1] * 14, [0] * 14, "DISPATCH_STOCKPILE_STATIC"),
    ],
)
def test_verdict_slicing_is_exactly_conservative(wait_pickup, stock_pickup, stock_bay, verdict):
    phase = cf.cargoflow_phase_outcome(
        built_ladder(wait_pickup, stock_pickup, stock_bay),
        prelaunch_digest=PRELAUNCH,
        plan=PLAN,
    )
    assert phase["verification"] == "CARGOFLOW_COMPLETE"
    assert phase["verdict"]["verdict"] == verdict


def test_verdict_undecided_without_its_discriminator_series():
    undecided = cf.cargoflow_verdict({})
    assert undecided["verdict"] == "CARGOFLOW_GATE_UNDECIDED_INCOMPLETE"
    assert "recorded fact" in undecided["statement"]
    missing_stock = cf.cargoflow_verdict({"wait_pickup": [0, 5]})
    assert missing_stock["verdict"] == "CARGOFLOW_GATE_UNDECIDED_INCOMPLETE"


# --- The phase verifier: divergence halts and incomplete paths ---------------


def measured_prefix(index: int) -> list[tuple[cf.CargoFlowRequest, cf.CargoFlowReadback]]:
    """Ready exchanges for ladder positions [0, index)."""
    ladder = []
    for entry in range(index):
        request = make_request(entry)
        ladder.append((request, cf.CargoFlowReadback.model_validate(ready_payload(request))))
    return ladder


def test_wrong_seal_halt_verbatim():
    request = work._cargoflow_exchange_request(SCHEDULE[0], OTHER_PLAN, PLAN)
    readback = cf.CargoFlowReadback.model_validate(ready_payload(request))
    phase = cf.cargoflow_phase_outcome(
        [(request, readback)], prelaunch_digest=PRELAUNCH, plan=PLAN
    )
    assert phase["verification"] == "CARGOFLOW_INCOMPLETE"
    assert phase["failed"]["label"] == "sample-00"
    assert "not the staged prelaunch seal" in phase["failed"]["error"]
    assert phase["failed"]["world_state"] == "HALTED_BEFORE_MUTATION"
    assert phase["pending"] == EXCHANGES[1:]
    assert phase["anchor"] is None and phase["samples"] == {}


def test_late_exchange_beyond_the_ladder_is_out_of_order():
    late = make_request(1)
    phase = cf.cargoflow_phase_outcome(
        [(late, cf.CargoFlowReadback.model_validate(ready_payload(late)))],
        prelaunch_digest=PRELAUNCH,
        plan=PLAN,
    )
    assert phase["failed"]["label"] == "sample-01"
    assert "out of order: expected sample-00" in phase["failed"]["error"]


@pytest.mark.parametrize(
    "index, overrides, needle",
    [
        (3, {"funds": FUNDS + 1}, "funds must equal the close-out level"),
        (3, {"cost": 1}, "samples must observe at zero cost"),
        (5, {"anchor": ANCHOR + 1, "day": ANCHOR + 26}, "anchor drifted across the ladder"),
    ],
)
def test_ready_divergence_halt_verbatim(index, overrides, needle):
    exchanges = measured_prefix(index)
    request = make_request(index)
    exchanges.append(
        (request, cf.CargoFlowReadback.model_validate(ready_payload(request, **overrides)))
    )
    phase = cf.cargoflow_phase_outcome(exchanges, prelaunch_digest=PRELAUNCH, plan=PLAN)
    assert phase["verification"] == "CARGOFLOW_INCOMPLETE"
    assert phase["failed"]["label"] == f"sample-{index:02d}"
    assert needle in phase["failed"]["error"]
    assert phase["pending"] == EXCHANGES[index + 1 :]
    assert len(phase["receipts"]) == index


def test_refusal_frame_halts_but_preserves_the_partial_verdict():
    window_request = make_request(3)
    window = parse_from(
        window_request,
        window_payload(
            window_request, "WINDOW_EXHAUSTED", anchor=ANCHOR, tick=60, day=ANCHOR + 18
        ),
    )
    phase = cf.cargoflow_phase_outcome(
        measured_prefix(3) + [(window_request, window)],
        prelaunch_digest=PRELAUNCH,
        plan=PLAN,
    )
    assert phase["failed"]["label"] == "sample-03"
    assert "ended WINDOW_EXHAUSTED" in phase["failed"]["error"]
    assert len(phase["receipts"]) == 3
    assert phase["anchor"] == ANCHOR
    assert phase["pending"] == EXCHANGES[4:]
    assert phase["verdict"]["verdict"] == "DISPATCH_STOCKPILE_STATIC"


def test_malformed_exception_element_types_a_halt():
    request = make_request(0)
    phase = cf.cargoflow_phase_outcome(
        [(request, ValueError("torn frame"))], prelaunch_digest=PRELAUNCH, plan=PLAN
    )
    assert phase["failed"] == {
        "label": "sample-00",
        "status": "MALFORMED",
        "error": "torn frame",
        "world_state": "HALTED_BEFORE_MUTATION",
    }
    assert phase["pending"] == EXCHANGES[1:] and phase["anchor"] is None
    exchanges = measured_prefix(2) + [(make_request(2), TimeoutError("the sample budget fled"))]
    phase = cf.cargoflow_phase_outcome(exchanges, prelaunch_digest=PRELAUNCH, plan=PLAN)
    assert phase["failed"]["label"] == "sample-02"
    assert phase["failed"]["status"] == "MALFORMED"
    assert "the sample budget fled" in phase["failed"]["error"]


# --- The VM: full schedule, anchor latch and counter ladder -------------------


def test_handler_full_schedule_and_ready_marker():
    vm, _, phase = run_probe_vm()
    assert phase["verification"] == "CARGOFLOW_COMPLETE"
    logs = [str(line) for line in vm_root(vm)["markers"]]
    assert logs[len(logs) - 1] == "D5_CARGOFLOW sample-13 READY"
    # The three-marker cadence of the static world's facts
    # (stock-not-accepted, non-producer, exchange) keeps the exchange
    # markers on the third logo slot of every sample.
    assert all("sample-" in line for line in logs[2::3])
    assert logs.count("D5_CARGOFLOW_STOCK_NOT_ACCEPTED 0") == 14
    assert logs.count("D5_CARGOFLOW_NON_PRODUCER 1") == 14
    replies = [dict(row) for row in vm_root(vm)["replies"]]
    assert [row["status"] for row in replies] == ["READY"] * 14
    assert all(row["funds"] == FUNDS for row in replies)
    assert all(row["cost"] == 0 and row["max_cost"] == 0 for row in replies)
    assert [row["offset"] for row in replies] == list(cf.CARGOFLOW_SAMPLE_OFFSETS)
    vm.execute("::bridge2 <- NetworkFreightProof();")
    vm.execute("::is_bridge <- bridge2 instanceof D5CargoFlowProof;")
    assert vm_root(vm)["is_bridge"] is True


def test_handler_start_marker():
    vm = build_vm(stop_at=1)
    vm.execute('try { bridge.Start(); } catch (e) { ::start_error <- e; }')
    markers = [str(m) for m in vm_root(vm)["markers"]]
    assert markers and markers[0] == "D5_CARGOFLOW_READY"
    assert vm_root(vm)["start_error"] == "CONTROLLED_STOP"


def test_handler_first_sample_measures_the_pinned_world_fact_families():
    vm = build_vm()
    readback = drive(vm, make_request(0))
    assert readback.status == "READY"
    assert readback.anchor == ANCHOR
    assert readback.year == civil_ymd(ANCHOR)[0]
    assert readback.month == civil_ymd(ANCHOR)[1]
    assert readback.day_of_month == civil_ymd(ANCHOR)[2]
    # The 15.3 native fact family rides verbatim (E65): the producer has no
    # accepted stock slot (stock -1) and the acceptor is the non-producer.
    assert readback.stock_pickup == -1
    assert readback.stock_bay == 0
    assert readback.prod_pickup == 104 and readback.prod_bay == -1
    logs = [str(line) for line in vm_root(vm)["markers"]]
    assert logs == [
        "D5_CARGOFLOW_STOCK_NOT_ACCEPTED 0",
        "D5_CARGOFLOW_NON_PRODUCER 1",
        "D5_CARGOFLOW sample-00 READY",
    ]


def test_handler_observes_a_rising_waiting_series_and_the_verdict_follows():
    vm = build_vm()
    exchanges = []
    for index, entry in enumerate(SCHEDULE):
        if entry["exchange"] == "sample-01":
            seed_stop(vm, 0, w=5, from0=5)
        request = make_request(index)
        readback = drive(vm, request)
        exchanges.append((request, readback))
        assert readback.wait_pickup == (0 if index == 0 else 5)
    phase = cf.cargoflow_phase_outcome(exchanges, prelaunch_digest=PRELAUNCH, plan=PLAN)
    assert phase["verification"] == "CARGOFLOW_COMPLETE"
    assert phase["verdict"]["verdict"] == "DISPATCH_OBSERVED_LATE"
    assert phase["series"]["wait_pickup"] == [0] + [5] * 13


def test_handler_per_source_families_follow_the_stub_decomposition():
    vm = build_vm()
    seed_stop(vm, 0, w=4, from0=3, from1=1)
    seed_stop(vm, 2, w=7, from0=2, from1=5, pl=9, pl0=6, pl1=3)
    first = drive(vm, make_request(0))
    assert first.wait_pickup == 4
    assert (first.wait_pickup_from0, first.wait_pickup_from1) == (3, 1)
    assert first.count_pickup == 0 and first.count_bay == 9
    assert (first.planned_pickup_from0, first.planned_pickup_from1) == (0, 0)
    assert (first.planned_bay_from0, first.planned_bay_from1) == (6, 3)
