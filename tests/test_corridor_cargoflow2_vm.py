"""Package VM refusal tests for the D5-CARGOFLOW-2 probe handler.

The shipped GameScript package ``app/simulation/openttd/d5_cargoflow2_package/``
runs inside the real Squirrel VM against the controlled stub world of
``tests/test_corridor_cargoflow2.py`` (imported, never copied). This suite owns
the handler's refusal ladder and halt discipline (any terminal non-planned
status halts the ladder prefix-preservingly), the sealed plan latch, the
planned ladder of record end to end (the 25 exchanges against the plans and
funds model of record), the wait-window machinery's echo class
(``CLOCK_STALLED``/``WINDOW_EXHAUSTED`` frames carry exactly the anchor/tick/day
echoes against the stub clock), the arrival watch's bounded timeout class, the
per-window latch bound (overflow refuses, never truncates), the one-shot
32-request budget with duplicate drop, the native-fact throw logging and the
request-shape drops the entry ladder enforces. Nothing here launches OpenTTD,
connects to an AdminPort or writes any native or save state: only the tests'
own VM world is mutated.
"""

from __future__ import annotations

import tests.test_corridor_cargoflow2 as t2
from tests.test_corridor_cargoflow2 import (
    ANCHOR,
    OTHER_PLAN,
    base_request,
    build_vm,
    drive,
    expect_drop,
    make_request,
    reply,
    run_probe_vm,
    squirrel_table,
    sweep_days,
    vm_root,
    witness_arrival,
)

# The planned prefix statuses of record (site-00 … arrive-00), verbatim from
# the handler's own 25-row schedule table.
_PREFIX_STATUS = (
    "READY", "READY", "BUILT", "READ", "ORDERED", "ORDERED",
    "ORDER_SET_VERIFIED", "ARMED", "STARTED", "READ", "ANCHORED",
)


def queued_moves(vm, rows):
    """Queue stub motion rows ``(tick, location, load)``; both lines run."""
    for tick, location, load in rows:
        body = (
            f"::vehicles[::cur_vehicle].location = {location}; "
            f"::vehicles[::cur_vehicle].load = {load};"
        )
        vm.execute(f"::moves.append({{tick = {tick}, fn = function() {{ {body} }}}});")


def anchored_vm(**knobs):
    """Fresh VM driven through the exact planned anchor prefix (site…arrive)."""
    t2._DRIVER = {"vehicle": -1}
    vm = build_vm(**knobs)
    sweep_days(vm, 0)
    witness_arrival(vm, at_tick=40)
    for index in range(11):
        readback = drive(vm, make_request(index))
        assert readback.status == _PREFIX_STATUS[index], (index, readback.status)
        if readback.op == "purchase":
            t2._DRIVER["vehicle"] = readback.vehicle
    return vm


def witnessed_prefix(**knobs):
    """Fresh VM driven through site…vread-01, awaiting the arrival watch."""
    t2._DRIVER = {"vehicle": -1}
    vm = build_vm(**knobs)
    sweep_days(vm, 0)
    for index in range(10):
        readback = drive(vm, make_request(index))
        assert readback.status == _PREFIX_STATUS[index], (index, readback.status)
        if readback.op == "purchase":
            t2._DRIVER["vehicle"] = readback.vehicle
    return vm


def test_ladder_of_record_runs_green():
    """The exact 25 planned exchanges verify against the world of record."""
    _, exchanges, phase = run_probe_vm()
    assert len(exchanges) == 25
    assert phase["failed"] is None and phase["pending"] == []
    assert phase["verification"] == "CARGOFLOW2_COMPLETE"
    # The stub world of record never fills its queue: the honest verdict
    # class of this green ladder, never folded into delivery.
    assert phase["verdict"]["verdict"] == "CARGOFLOW2_QUEUE_NEVER_FILLED"
    assert len(phase["receipts"]) == 25


def test_handler_on_stage_and_latch_refusals():
    vm = build_vm()
    # An on-ladder exchange landing off its planned stage is answered
    # OUT_OF_ORDER and, being a terminal non-planned status (the halt
    # discipline), permanently halts the ladder: later exchanges are
    # refused, never dispatched.
    off_stage = base_request(request_id="engine-00", op="engine", engine=123)
    assert reply(vm, off_stage)["status"] == "OUT_OF_ORDER"
    assert reply(vm, base_request())["status"] == "OUT_OF_ORDER"
    # A fresh ladder: the seal latch of record rides the plan echo.
    vm = build_vm()
    assert reply(vm, base_request())["status"] == "READY"
    labeled = base_request(request_id="engine-00", op="engine", engine=123)
    labeled["plan"] = OTHER_PLAN  # not the seal the ladder latched
    assert reply(vm, labeled)["status"] == "OUT_OF_ORDER"
    # The stale-seal halt keeps the seal of record; the ladder is refused.
    purchase = base_request(
        request_id="purchase-00", op="purchase", engine=123,
        expected_cost=4429, max_cost=5000,
    )
    assert reply(vm, purchase)["status"] == "OUT_OF_ORDER"


def test_handler_company_and_pin_refusals():
    # A foreign company of the resolved domain is still refused: the probe
    # is pinned to the corridor's company of record; a company outside the
    # resolved domain refuses with the same status.
    vm = build_vm()
    assert reply(vm, base_request(company=1))["status"] == "INVALID_COMPANY"
    vm = build_vm()
    assert reply(vm, base_request(company=7))["status"] == "INVALID_COMPANY"
    # A drifted corridor pin at the site exchange is the INVALID_SITE
    # refusal of record; past it, the same drift is a stale admission.
    vm = build_vm()
    assert reply(vm, base_request(pickup=45489))["status"] == "INVALID_SITE"
    vm = build_vm()
    assert reply(vm, base_request())["status"] == "READY"
    assert reply(
        vm,
        base_request(
            request_id="engine-00", op="engine", engine=123, pickup=45489
        ),
    )["status"] == "STALE_ADMISSION"
    # A paused world refuses before any observation.
    vm = build_vm(paused=True)
    assert reply(vm, base_request())["status"] == "PAUSED"


def test_handler_halt_discipline_after_a_refusal():
    vm = build_vm()
    assert reply(vm, base_request())["status"] == "READY"
    # A pause at a later stage is a terminal refusal: the ladder halts
    # prefix-preservingly and later exchanges are refused, not dispatched.
    vm.execute("::paused = true;")
    paused = reply(vm, base_request(request_id="engine-00", op="engine", engine=123))
    assert paused["status"] == "PAUSED"
    assert paused["funds"] == 0  # a refusal carries no bank echo of record
    vm.execute("::paused = false;")
    purchase = base_request(
        request_id="purchase-00", op="purchase", engine=123,
        expected_cost=4429, max_cost=5000,
    )
    assert reply(vm, purchase)["status"] == "OUT_OF_ORDER"


def test_handler_clock_stall_carries_the_honest_echoes():
    vm = anchored_vm()
    assert drive(vm, make_request(11)).status == "READY"  # flow-00 at the anchor
    vm.execute("::ticks_freeze = true;")
    sweep_days(vm, 1)  # the planned day sweep keeps ending days
    stalled = drive(vm, make_request(12))
    assert stalled.status == "CLOCK_STALLED"
    assert stalled.anchor == ANCHOR and stalled.tick == 40
    assert stalled.day == ANCHOR + 1  # the day advanced while the tick froze
    # The stall typed the ladder: it can never advance afterwards.
    vm.execute("::ticks_freeze = false;")
    assert reply(
        vm,
        base_request(
            request_id="flow-02", op="flow", engine=123, offset=10, vehicle=1
        ),
    )["status"] == "OUT_OF_ORDER"


def test_handler_window_overshoot_and_dead_clock_fail_closed():
    # The clock passed flow-01's planned day between the exchanges.
    vm = anchored_vm()
    assert drive(vm, make_request(11)).status == "READY"
    vm.execute(f"::day = {ANCHOR + 12};")
    exhausted = drive(vm, make_request(12))
    assert exhausted.status == "WINDOW_EXHAUSTED"
    assert exhausted.anchor == ANCHOR and exhausted.tick == 40
    assert exhausted.day == ANCHOR + 12
    # The run-window bound: a dead clock (day rate 0) burns the full
    # 2048-tick wait budget and fails closed at the anchor day.
    vm = anchored_vm()
    assert drive(vm, make_request(11)).status == "READY"
    dead = drive(vm, make_request(12))
    assert dead.status == "WINDOW_EXHAUSTED"
    assert dead.tick == 2088 and dead.day == ANCHOR


def test_handler_latch_overflow_refuses_never_truncates():
    vm = anchored_vm()
    assert drive(vm, make_request(11)).status == "READY"  # flow-00 reads clean
    queued_moves(vm, [
        (41, 45748, 2),   # the anchor stay: the first load bump
        (42, 50862, 1),   # the bay: arrival + unload, one unit discharged
        (43, 45748, 3),   # back to the pickup: arrival + load
        (44, 50862, 2),   # the bay again: arrival + unload
        (45, 45748, 4),   # the 8th latch lands; the load edge overflows
    ])
    sweep_days(vm, 1)
    overflow = drive(vm, make_request(12))
    assert overflow.status == "LATCH_OVERFLOW"
    # The refusal carries none of the observation set (no window echoes).
    assert overflow.anchor is None and overflow.tick is None
    assert overflow.day is None
    # The overflow refused, never truncated: the ladder is typed dead.
    assert reply(
        vm,
        base_request(
            request_id="flow-02", op="flow", engine=123, offset=10, vehicle=1
        ),
    )["status"] == "OUT_OF_ORDER"


def test_handler_arrival_watch_deadline_is_the_day_authority():
    # No arrival witness: the live clock rides into the deadline day of
    # record and the watch refuses (day 712234 > the deadline 712233).
    vm = witnessed_prefix()
    timeout = drive(vm, make_request(10))
    assert timeout.status == "ARRIVE_TIMEOUT"
    # A frozen world (day never ends) fails closed on the tick ceiling
    # instead: 2048 wait samples with no ended day at all.
    vm = witnessed_prefix(day_rate=0)
    dead = drive(vm, make_request(10))
    assert dead.status == "ARRIVE_TIMEOUT"
    assert dead.day is None  # the refusal carries no observation set


def test_handler_native_fact_throws_are_typed():
    # A clock read outside the measured domain throws at the exchange's own
    # instant of record: the thrown fact is logged with the exchange label
    # before the exchange's terminal status.
    vm = build_vm()
    vm.execute("::ticks = -1;")
    refused = drive(vm, make_request(0))
    assert refused.status == "UNSUPPORTED_NATIVE_FACT"
    markers = [str(line) for line in vm_root(vm)["markers"]]
    assert markers[0] == "D5_CARGOFLOW2_THROW site-00 D5_NATIVE_FACT"
    # A controlled stop inside a waiting window throws the stub fact too:
    # the same catch-all refusal forecloses the write path, and the wait's
    # honest echoes never appear in the stripped refusal frame.
    vm = anchored_vm()
    assert drive(vm, make_request(11)).status == "READY"
    vm.execute("::stop_at = 41;")
    sweep_days(vm, 1)
    stopped = drive(vm, make_request(12))
    assert stopped.status == "UNSUPPORTED_NATIVE_FACT"
    assert stopped.day is None and stopped.tick is None
    markers = [str(line) for line in vm_root(vm)["markers"]]
    assert "D5_CARGOFLOW2_THROW flow-01 CONTROLLED_STOP" in markers
    assert markers[-1] == "D5_CARGOFLOW2 flow-01 UNSUPPORTED_NATIVE_FACT"


def test_handler_budget_cap_and_duplicate_drop():
    vm = build_vm()
    for index in range(33):
        payload = base_request(request_id=f"probe-{index:02d}")
        before = len(vm_root(vm)["replies"])
        vm.execute("::bridge.Handle(" + squirrel_table(payload) + ");")
        if index < 32:
            assert len(vm_root(vm)["replies"]) == before + 1
        else:
            assert len(vm_root(vm)["replies"]) == before  # the 33rd id is dropped
    expect_drop(vm, base_request(request_id="probe-00"))  # a used id cannot re-enter


def test_handler_drops_foreign_shapes():
    vm = build_vm()
    expect_drop(vm, {"protocol": 9})
    expect_drop(vm, {"protocol": 11, "op": "radius", "request_id": "site-00"})
    expect_drop(vm, base_request(plan="z" * 64))  # the plan is not hex64
    expect_drop(vm, base_request(plan="a" * 63))  # a short plan digest
    expect_drop(vm, base_request(plan="A" * 64))  # uppercase hex
    # The purchase pitch carries the exact quote and cap echoes of record.
    expect_drop(vm, base_request(op="purchase", engine=123, expected_cost=4430,
        max_cost=5000))                            # a drifted quote
    expect_drop(vm, base_request(op="purchase", engine=123, expected_cost=4429,
        max_cost=4000))                            # a drifted pre-launch cap
    expect_drop(vm, base_request(offset=56))      # outside the pinned ladder scale
    expect_drop(vm, base_request(offset="0"))     # the ladder rides integers only
    expect_drop(vm, base_request(company=15))     # outside the native company domain
    expect_drop(vm, base_request(request_id="wrong_label"))  # IdShape: no underscore
    expect_drop(vm, base_request(request_id="SITE-00"))      # IdShape: no uppercase
    expect_drop(vm, base_request(request_id=""))             # the empty label
    expect_drop(vm, base_request(request_id="p" * 33))       # the 33-char label
    expect_drop(vm, base_request(pickup=45748, delivery=45748))  # degenerate pins
    expect_drop(vm, base_request(pickup=45748, depot=45748))  # degenerate depot
    assert reply(vm, base_request())["status"] == "READY"  # the shaped request measures
    expect_drop(vm, base_request())  # the used site-00 id cannot re-enter
