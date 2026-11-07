"""Package VM tests for the D5-F12-DEPOT mutation handler (protocol 10).

The shipped GameScript package
``app/simulation/openttd/d5_depot_mutation_package/main.nut`` runs inside the
real Squirrel VM against a mutation stub world that reproduces the E58 §2.1
pre-fix and post-fix depot/edge semantics (per-tile facing road bits with the
depot door contribution, the demolish refund, the road pair and the depot
rebuild costs, and the company fleet). Every dispatched reply is parsed back
through the protocol-10 wire contract, never through the package's own
words. The suite owns the handler's planned table, guards and refusal
ladder, its echo discipline against the stub world's native facts, the
prescribed demolish-road-depot sequence through the real stub mutation
arithmetic, and the one-shot 32-request budget with duplicate drop. Nothing
here launches OpenTTD, connects to an AdminPort or writes any native or save
state: only the tests' own VM world is mutated.

The VM scaffolding (``build_vm``/``drive``/stubs) and the fixture worlds live
in ``tests/test_corridor_depot_mutation.py`` and are imported, not copied.
"""

from __future__ import annotations

from tests.test_corridor_depot_mutation import (
    FUNDS,
    FUNDS_AFTER_DEMO,
    FUNDS_AFTER_DEPOT,
    FUNDS_AFTER_ROAD,
    OTHER_PLAN,
    base_request,
    build_vm,
    drive,
    expect_drop,
    make_request,
    reply,
    run_depot_vm,
    squirrel_table,
    vm_root,
)


def test_handler_full_schedule_and_ready_marker():
    vm, exchanges, phase = run_depot_vm()
    assert phase["verification"] == "DEPOT_MUTATION_COMPLETE"
    assert phase["gate"]["verdict"] == "DEPOT_MUTATION_GATE_PASSES"
    logs = [str(line) for line in vm_root(vm)["markers"]]
    assert logs[0] == "D5_F12_DEPOT before-00 READY"
    assert logs[1] == "D5_F12_DEPOT demo-00 READY"
    assert logs[len(logs) - 3] == "D5_F12_DEPOT depot-00 READY"
    assert logs[len(logs) - 2] == "D5_F12_DEPOT after-00 READY"
    assert logs[len(logs) - 1] == "D5_F12_DEPOT fleet-00 READY"
    replies = [dict(reply_row) for reply_row in vm_root(vm)["replies"]]
    assert [reply_row["status"] for reply_row in replies] == ["READY"] * 6
    # The stub cost chain of record: refund -100, road 200, depot 1200.
    assert [reply_row["cost"] for reply_row in replies] == [
        0,
        -100,
        200,
        1200,
        0,
        0,
    ]
    assert [reply_row["funds"] for reply_row in replies] == [
        FUNDS,
        FUNDS_AFTER_DEMO,
        FUNDS_AFTER_ROAD,
        FUNDS_AFTER_DEPOT,
        FUNDS_AFTER_DEPOT,
        FUNDS_AFTER_DEPOT,
    ]
    vm.execute("::bridge2 <- NetworkFreightProof();")
    vm.execute("::is_bridge <- bridge2 instanceof D5DepotMutationProof;")
    assert vm_root(vm)["is_bridge"] is True


def test_handler_start_marker():
    vm = build_vm(stop_at=1)
    vm.execute('try { bridge.Start(); } catch (e) { ::start_error <- e; }')
    markers = [str(m) for m in vm_root(vm)["markers"]]
    assert markers and markers[0] == "D5_F12_DEPOT_READY"
    assert vm_root(vm)["start_error"] == "CONTROLLED_STOP"


def test_handler_full_mutation_changes_the_stub_world():
    """The three commands really mutate the stub ground: before/after facts."""
    vm, exchanges, phase = run_depot_vm()
    after = exchanges[4][1]
    assert after.depot_present is True
    assert after.front_read == 45743 and after.owner == 0
    assert after.depot_linked is True
    # The fix of record: both AreRoadTilesConnected directions true.
    assert after.connected_front_to_depot is True
    assert after.connected_depot_to_front is True
    assert phase["state_changed"] is True
    assert [row["exchange"] for row in phase["mutations"]] == [
        "demo-00",
        "road-00",
        "depot-00",
    ]


def test_handler_road_dep_echoes_and_tile_shapes():
    vm = build_vm()
    before = drive(vm, make_request(0))
    assert before.tile is None and before.front_tile is None
    assert before.depot_present is True
    # The stub E58 diagnosis verbatim before any command.
    assert before.connected_front_to_depot is False
    assert before.connected_depot_to_front is False
    demo = drive(vm, make_request(1))
    assert demo.tile == 45487 and demo.front_tile is None
    road = drive(vm, make_request(2))
    assert road.tile == 45487 and road.front_tile == 45743
    assert road.funds == FUNDS_AFTER_ROAD and road.cost == 200
    depot = drive(vm, make_request(3))
    assert depot.tile == 45487 and depot.front_tile == 45743
    assert depot.funds == FUNDS_AFTER_DEPOT and depot.cost == 1200


def test_handler_refusal_ladder():
    vm = build_vm()

    assert reply(vm, base_request())["status"] == "READY"
    wrong_shape = dict(base_request(op="demolish", request_id="demo-00", tile=45487))
    wrong_shape["request_id"] = "wrong_label"
    expect_drop(vm, wrong_shape)  # IdShape keeps the underscored id out
    late = dict(
        base_request(op="demolish", request_id="demo-00", tile=45487, plan=OTHER_PLAN)
    )
    assert reply(vm, late)["status"] == "OUT_OF_ORDER"  # the latch keeps its own seal
    # The mutation halt discipline: a terminal status that is not the planned
    # READY halts the phase; later exchanges are refused, never dispatched.
    later = dict(base_request(op="road", request_id="road-00", tile=45487,
                              front_tile=45743))
    assert reply(vm, later)["status"] == "OUT_OF_ORDER"


def test_handler_location_and_company_refusals():
    # The stub's second company exists and is refused.
    vm = build_vm()
    assert reply(vm, base_request(company=1))["status"] == "INVALID_COMPANY"

    # A drifted corridor pin is stale.
    vm = build_vm()
    assert reply(vm, base_request(pickup=45487, depot=45489))["status"] == "STALE_PIN"

    # A paused world is refused before any observation.
    vm = build_vm(paused=True)
    assert reply(vm, base_request())["status"] == "PAUSED"


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
    expect_drop(vm, {"protocol": 5})
    expect_drop(vm, {"protocol": 6, "op": "radius", "request_id": "radius-00"})
    expect_drop(vm, {"protocol": 9, "op": "box", "request_id": "pbox-00"})
    expect_drop(vm, base_request(op="truck"))
    expect_drop(vm, base_request(plan="z" * 64))  # the plan is not hex64
    expect_drop(vm, base_request(max_cost=1))  # only the pinned 3000 echo is accounted
    expect_drop(vm, base_request(max_cost=3001))
    expect_drop(vm, base_request(company=15))  # outside the native company domain
    assert reply(vm, base_request(company=7))["status"] == "INVALID_COMPANY"
    expect_drop(vm, base_request(op="observe", tile=45487))  # tile rides mutations only
    expect_drop(vm, base_request(op="demolish", request_id="demo-00"))  # missing tile
    expect_drop(vm, base_request(op="road", request_id="road-00", tile=45487))
    expect_drop(vm, base_request(op="road", request_id="road-00", tile=45487,
                                 front_tile=45487))  # the span API needs start != end


def test_dispatch_establishes_the_native_road_context_before_probes():
    """E72 regression (the D5-F12-DEPOT-1 before-00 false negative).

    The 15.3 per-script current road type is INVALID_ROADTYPE (63) until a
    script sets it and every ScriptRoad depot/edge probe fail-closes on it
    (script_storage.hpp:67, script_road.cpp:44-51/:111/:497-502). The stub
    models exactly that, so a before-00 observe through the real package
    must read the world's depot facts — depot_present true / front 45743 /
    owner 0 / identity-linked true — only through the dispatcher's own
    set+assert, and the context must stay established afterwards."""
    vm = build_vm()
    assert vm_root(vm)["cur_road_type"] == 63
    readback = drive(vm, make_request(0))
    assert readback.status == "READY"
    assert readback.depot_present is True
    assert readback.front_read == 45743
    assert readback.owner == 0
    assert readback.depot_linked is True
    assert vm_root(vm)["cur_road_type"] == 0


def test_dispatch_assert_refuses_when_the_road_type_is_unavailable():
    """E72 regression pair: the dispatch-entry assert (D4/D5-v2 pattern)
    stops every probe before any op when the native road context cannot be
    established — the reply stays a refusal with no unclaimed facts and the
    context is never faked."""
    vm = build_vm(road_type_ok=False)
    readback = drive(vm, make_request(0))
    assert readback.status == "UNSUPPORTED_NATIVE_FACT"
    assert readback.depot_present is None
    assert vm_root(vm)["cur_road_type"] == 63
