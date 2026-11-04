"""Package VM refusal tests for the D5-CARGOFLOW-1 probe handler.

The shipped GameScript package ``app/simulation/openttd/d5_cargoflow_package/``
runs inside the real Squirrel VM against the controlled stub world of
``tests/test_corridor_cargoflow.py`` (imported, never copied). This suite owns
the handler's refusal ladder and halt discipline (every terminal non-READY
status halts the ladder prefix-preservingly), the sealed plan latch, the
wait-window machinery's echo class (``CLOCK_STALLED``/``WINDOW_EXHAUSTED``
frames carry exactly the anchor/tick/day echoes against the stub clock), the
one-shot 32-request budget with duplicate drop, and the request-shape drops
the entry ladder enforces. Nothing here launches OpenTTD, connects to an
AdminPort or writes any native or save state: only the tests' own VM world is
mutated.
"""

from __future__ import annotations

from tests.test_corridor_cargoflow import (
    ANCHOR,
    OTHER_PLAN,
    base_request,
    build_vm,
    drive,
    expect_drop,
    make_request,
    reply,
    squirrel_table,
    vm_root,
)


def test_handler_on_stage_and_latch_refusals():
    vm = build_vm()
    # An on-ladder exchange landing off its planned stage is answered
    # OUT_OF_ORDER and, being a terminal non-READY status (the census
    # halt discipline), permanently halts the ladder: later exchanges are
    # refused, never dispatched.
    off_stage = base_request(request_id="sample-03", offset=15)
    assert reply(vm, off_stage)["status"] == "OUT_OF_ORDER"
    assert reply(vm, base_request())["status"] == "OUT_OF_ORDER"
    # The seal latch of record stays intact on a fresh ladder.
    vm = build_vm()
    assert reply(vm, base_request())["status"] == "READY"
    labeled = base_request(request_id="sample-01", offset=5)
    labeled["plan"] = OTHER_PLAN  # not the seal the ladder latched
    assert reply(vm, labeled)["status"] == "OUT_OF_ORDER"
    # That stale-seal exchange is a terminal non-READY status too: the
    # halt keeps the seal of record, the pending ladder is refused.
    assert reply(vm, base_request(request_id="sample-02", offset=10))[
        "status"
    ] == "OUT_OF_ORDER"


def test_handler_company_and_pin_refusals():
    # A foreign company (the stub's company 1 resolves) is still refused:
    # the probe is pinned to the depot chain's company of record.
    vm = build_vm()
    assert reply(vm, base_request(company=1))["status"] == "INVALID_COMPANY"
    # A company outside the resolved domain is refused before the mode.
    vm = build_vm()
    assert reply(vm, base_request(company=7))["status"] == "INVALID_COMPANY"
    # A drifted corridor pin is stale.
    vm = build_vm()
    assert reply(vm, base_request(pickup=45487, depot=45489))["status"] == "STALE_PIN"
    # A paused world refuses before any observation.
    vm = build_vm(paused=True)
    assert reply(vm, base_request())["status"] == "PAUSED"


def test_handler_halt_discipline_after_a_refusal():
    vm = build_vm()
    assert reply(vm, base_request())["status"] == "READY"
    # A pause at a later sample is a terminal refusal: the ladder halts
    # prefix-preservingly and later exchanges are refused, not dispatched.
    vm.execute("::paused = true;")
    paused = reply(vm, base_request(request_id="sample-01", offset=5))
    assert paused["status"] == "PAUSED"
    assert paused["funds"] == 0  # a refusal carries no bank echo of record
    vm.execute("::paused = false;")
    assert reply(vm, base_request(request_id="sample-02", offset=10))[
        "status"
    ] == "OUT_OF_ORDER"


def test_handler_clock_stall_carries_the_honest_echoes():
    vm = build_vm()
    assert drive(vm, make_request(0)).status == "READY"
    vm.execute("::ticks_freeze = true;")
    stalled = drive(vm, make_request(1))
    assert stalled.status == "CLOCK_STALLED"
    assert stalled.anchor == ANCHOR and stalled.tick == 0
    assert stalled.day == ANCHOR + 1  # the day advanced while the tick froze
    # The stall typed the ladder: it can never advance afterwards.
    vm.execute("::ticks_freeze = false;")
    assert reply(vm, base_request(request_id="sample-02", offset=10))[
        "status"
    ] == "OUT_OF_ORDER"


def test_handler_window_exhaustion_never_reshuffles_the_ladder():
    # The clock passed sample-01's planned day between exchanges.
    vm = build_vm()
    assert drive(vm, make_request(0)).status == "READY"
    vm.execute(f"::day = {ANCHOR + 12};")
    exhausted = drive(vm, make_request(1))
    assert exhausted.status == "WINDOW_EXHAUSTED"
    assert exhausted.anchor == ANCHOR and exhausted.tick == 0
    assert exhausted.day == ANCHOR + 12
    # The run-window bound: a dead clock (day rate 0) burns the full
    # 2048-tick wait budget and fails closed at the anchor day.
    vm = build_vm(day_rate=0)
    assert drive(vm, make_request(0)).status == "READY"
    dead = drive(vm, make_request(1))
    assert dead.status == "WINDOW_EXHAUSTED"
    assert dead.tick == 2048 and dead.day == ANCHOR


def test_handler_station_and_fact_defences_are_typed():
    # A pinned station that vanished is a stale pin before any read.
    vm = build_vm()
    assert drive(vm, make_request(0)).status == "READY"
    vm.execute("::stops.rawdelete(2);;")
    assert drive(vm, make_request(1)).status == "STALE_PIN"
    # A native fact outside the measured domain is refused with the thrown
    # fact logged (D5_CARGOFLOW_THROW) before the exchange terminal status.
    vm = build_vm()
    vm.execute("::industries[0].stock = 70000;")
    assert drive(vm, make_request(0)).status == "UNSUPPORTED_NATIVE_FACT"
    markers = [str(line) for line in vm_root(vm)["markers"]]
    assert markers[0] == "D5_CARGOFLOW_THROW sample-00 D5_NATIVE_FACT"


def test_handler_budget_cap_and_duplicate_drop():
    vm = build_vm()
    for index in range(33):
        payload = base_request(request_id=f"probe-{index:02d}", offset=index % 66)
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
    expect_drop(vm, {"protocol": 11, "op": "sample", "request_id": "sample-00"})
    expect_drop(vm, base_request(op="radius"))
    expect_drop(vm, base_request(plan="z" * 64))  # the plan is not hex64
    expect_drop(vm, base_request(plan="a" * 63))  # a short plan digest
    expect_drop(vm, base_request(max_cost=1))  # a probe request budgets zero
    expect_drop(vm, base_request(company=15))  # outside the native company domain
    expect_drop(vm, base_request(request_id="wrong_label"))  # IdShape: no underscore
    expect_drop(vm, base_request(request_id="SAMPLE-00"))  # IdShape: no uppercase
    expect_drop(vm, base_request(request_id=""))  # the empty label
    expect_drop(vm, base_request(request_id="p" * 33))  # the 33-char label
    expect_drop(vm, base_request(offset=-1))  # outside the pinned ladder scale
    expect_drop(vm, base_request(offset=66))
    expect_drop(vm, base_request(offset="0"))  # the ladder rides integers only
    expect_drop(vm, base_request(pickup=45748, delivery=45748))  # degenerate pin set
    assert reply(vm, base_request())["status"] == "READY"  # the shaped request measures
    expect_drop(vm, base_request())  # the used sample-00 id cannot re-enter
