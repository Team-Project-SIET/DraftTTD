"""Package VM tests for the D5-BOX-CENSUS-1 census handler (E59 §9 item 6).

The shipped GameScript package ``app/simulation/openttd/d5_census_package/``
runs inside the real Squirrel VM against a census stub world that reproduces
the v2 ``DiscoveryBoxes`` scan semantics (per-tile industry ownership,
last-month production, acceptance states and the measured truck-stop
coverage radius). Every dispatched reply is parsed back through the
protocol-9 wire contract, never through the package's own words. The suite
owns the handler's planned table, guards and refusal ladder, its echo
discipline against the stub world's native facts, and the one-shot
32-request budget with duplicate drop. Nothing here launches OpenTTD,
connects to an AdminPort or writes any native or save state: only the
tests' own VM world is mutated.

The VM scaffolding (``build_vm``/``drive``/stubs) and the fixture worlds
live in ``tests/test_corridor_box_census.py`` and are imported, not copied.
"""

from __future__ import annotations

from tests.test_corridor_box_census import (
    FUNDS,
    OTHER_PLAN,
    PASS_WORLD,
    SCHEDULE,
    base_request,
    build_vm,
    drive,
    expect_drop,
    make_request,
    reply,
    run_census_vm,
    seed_industries,
    squirrel_table,
    vm_root,
)


def test_handler_full_schedule_and_ready_marker():
    vm, exchanges, phase = run_census_vm(PASS_WORLD)
    assert phase["verification"] == "CENSUS_COMPLETE"
    logs = [str(line) for line in vm_root(vm)["markers"]]
    assert logs[0] == "D5_CENSUS radius-00 READY"
    assert logs[len(logs) - 1] == "D5_CENSUS dbox-02 READY"
    replies = [dict(reply_row) for reply_row in vm_root(vm)["replies"]]
    assert [reply_row["status"] for reply_row in replies] == ["READY"] * 10
    assert all(reply_row["funds"] == FUNDS for reply_row in replies)
    assert all(reply_row["cost"] == 0 for reply_row in replies)
    vm.execute("::bridge2 <- NetworkFreightProof();")
    vm.execute("::is_bridge <- bridge2 instanceof D5CensusProof;")
    assert vm_root(vm)["is_bridge"] is True


def test_handler_start_marker():
    vm = build_vm(stop_at=1)
    vm.execute('try { bridge.Start(); } catch (e) { ::start_error <- e; }')
    markers = [str(m) for m in vm_root(vm)["markers"]]
    assert markers and markers[0] == "D5_CENSUS_READY"
    assert vm_root(vm)["start_error"] == "CONTROLLED_STOP"


def test_handler_box_scan_values():
    vm = build_vm()
    seed_industries(vm, PASS_WORLD)
    for entry_index in range(4):  # radius, acc-00, acc-01, prod-00 in order
        readback = drive(vm, make_request(entry_index))
        assert readback.status == "READY"
    page = drive(vm, make_request(4))
    assert page.rows is not None  # a box request always reports its rows
    rows = [dict(row) for row in page.rows]
    assert rows == [
        {"id": 0, "tile": 45748, "p": 104, "a": 0},
        {"id": 2, "tile": 45751, "p": 0, "a": 0},
        {"id": 5, "tile": 44981, "p": 0, "a": 0},
    ]
    assert page.count == 3 and page.more is False and page.cursor == 0
    assert page.tile == 45748 and page.funds == FUNDS


def test_handler_refusal_ladder():
    vm = build_vm()

    assert reply(vm, base_request())["status"] == "READY"
    wrong_shape = dict(base_request(op="accept", request_id="acc-00", tile=50351))
    wrong_shape["request_id"] = "wrong_label"
    expect_drop(vm, wrong_shape)  # IdShape keeps the underscored id out
    late = dict(base_request(op="accept", request_id="acc-00", tile=50351, plan=OTHER_PLAN))
    assert reply(vm, late)["status"] == "OUT_OF_ORDER"  # the latch keeps its own seal
    # The census halt discipline: a terminal status that is not the planned
    # READY halts the census; later exchanges are refused, not dispatched.
    later = dict(base_request(op="box", request_id="pbox-00", tile=45748, cursor=0))
    assert reply(vm, later)["status"] == "OUT_OF_ORDER"


def test_handler_location_and_company_refusals():
    # An on-stage accept with a foreign spot tile is an out-of-census location.
    vm = build_vm()
    assert reply(vm, base_request())["status"] == "READY"
    assert reply(vm, base_request(op="accept", request_id="acc-00", tile=45745))[
        "status"
    ] == "INVALID_LOCATION"

    # A foreign company (the stub's second company exists) is refused.
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


def test_handler_unsupported_radius_refusals():
    vm = build_vm(station_radius=300)
    assert reply(vm, base_request())["status"] == "UNSUPPORTED_NATIVE_FACT"
    vm = build_vm(station_radius=9)
    seed_industries(vm, [(0, [45748], 104, 0)])  # the prod control's world fact
    assert reply(vm, base_request())["status"] == "READY"  # 9 is a measured fact
    for index in range(1, 4):  # the spots run out first to bring pbox-00 on stage
        payload = base_request(
            op=SCHEDULE[index]["op"],
            request_id=SCHEDULE[index]["exchange"],
            tile=50351 if SCHEDULE[index]["op"] == "accept" else None,
        )
        assert reply(vm, payload)["status"] == "READY"
    assert reply(vm, base_request(op="box", request_id="pbox-00", tile=45748,
                                      cursor=0))["status"] == "UNSUPPORTED_NATIVE_FACT"


def test_handler_drops_foreign_shapes():
    vm = build_vm()
    expect_drop(vm, {"protocol": 5})
    expect_drop(vm, {"protocol": 6, "op": "radius", "request_id": "radius-00"})
    expect_drop(vm, base_request(op="truck"))
    expect_drop(vm, base_request(plan="z" * 64))  # the plan is not hex64
    expect_drop(vm, base_request(max_cost=1))  # a census request budgets zero
    expect_drop(vm, base_request(company=15))  # outside the native company domain
    assert reply(vm, base_request(company=7))["status"] == "INVALID_COMPANY"
    expect_drop(vm, base_request(op="radius", tile=45748))  # tile rides tile ops only
    expect_drop(vm, base_request(op="accept", request_id="acc-00", tile=50351, cursor=0))
    expect_drop(vm, base_request(op="accept", request_id="acc-00"))  # missing tile
    expect_drop(vm, base_request(op="box", request_id="pbox-00", tile=45748))  # no cursor
