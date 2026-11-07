"""Package VM tests for the D5-F12-DEPOT-RELOAD observe-only handler (protocol 10).

The shipped GameScript package
``app/simulation/openttd/d5_depot_recheck_package/main.nut`` runs inside the
real Squirrel VM against a stub world that reproduces the post-mutation round-2
world of record: the depot 45487 against its pinned front 45743 with owner 0,
the N stub bit of the round-2 fix laid on 45743, both AreRoadTilesConnected
directions true, and the bank balance at the E82 funds of record. Every
dispatched reply is parsed back through the protocol-10 wire contract, never
through the package's own words. The suite owns the one-exchange reload gate,
the handler's guard machinery and refusal ladder, its zero-spend / zero-tile /
echo discipline against the stub world's native facts, and the E72 road-context
regression pair, and it re-verifies the measured exchange through the
production ``corridor_depot_recheck_native.recheck_phase_outcome`` against the
round-2 facts of record. Nothing here launches OpenTTD, connects to an
AdminPort or writes any native or save state: only the tests' own VM world is
mutated.

The VM scaffolding (stubs, fixture worlds, ``drive``/``reply``/``expect_drop``)
lives in ``tests/test_corridor_depot_mutation.py`` and is imported, not copied.
Historical candidate directories are never touched: this suite is read-only
with respect to ``artifacts/``.
"""

from __future__ import annotations

from pathlib import Path

from squirrel import SQVM

import app.simulation.openttd.proof.corridor_depot_recheck_native as work
from tests.test_corridor_depot_mutation import (
    API,
    DEPOT_FRONT,
    PRELAUNCH,
    STUB,
    WORLD,
    base_request,
    drive,
    expect_drop,
    reply,
    squirrel_table,
    vm_root,
)

RECHECK_PACKAGE = (
    Path(__file__).resolve().parents[1]
    / "app"
    / "simulation"
    / "openttd"
    / "d5_depot_recheck_package"
)

# The funds of record for the reload's exchange boundary (E82 close-out).
FUNDS_OF_RECORD = 489650

# The round-2 facts of record (the E82 after-00 measurement, transcribed
# from the consumed depot attempt's after-save binding).
FACTS_OF_RECORD = dict(
    depot_present=True,
    front_read=DEPOT_FRONT,
    owner=0,
    depot_linked=True,
    connected_front_to_depot=True,
    connected_depot_to_front=True,
)


def build_recheck_vm(**knobs: int | bool) -> SQVM:
    """Fresh VM with the shared stub world, the round-2 post-fix shims and
    the observe-only reload package."""
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
    # The round-2 post-fix world of record: the N stub bit at 45743 and the
    # funds of record at the reload's exchange boundary.
    vm.execute("::road_bits[45743].n = true;")
    vm.execute("::funds = 489650;")
    vm.execute((RECHECK_PACKAGE / "main.nut").read_text())
    vm.execute("::bridge <- D5DepotRecheckProof();")
    return vm


def recheck_request(request_id: str = "reload-00", **overrides) -> dict:
    """A valid-shaped observe request payload for the raw handler tests,
    pinned by default to the one planned reload exchange identity."""
    payload = base_request(op="observe", request_id=request_id)
    payload.update(overrides)
    return payload


def typed_request(seal: str = PRELAUNCH):
    """The one production recheck request of record, over the module pins."""
    return work._recheck_exchange_request(work.recheck_schedule()[0], seal)


# --- the one-exchange reload gate --------------------------------------------


def test_handler_single_reload_exchange_measures_post_fix_facts():
    vm = build_recheck_vm()
    request = typed_request()
    readback = drive(vm, request)
    assert readback.status == "READY"
    assert readback.cost == 0  # the zero-spend discipline of record
    assert readback.funds == FUNDS_OF_RECORD == 489650
    assert readback.tile is None and readback.front_tile is None
    assert readback.depot_present is True
    assert readback.front_read == DEPOT_FRONT
    assert readback.owner == 0
    assert readback.depot_linked is True
    # The round-2 resolution of record: both directions true.
    assert readback.connected_front_to_depot is True
    assert readback.connected_depot_to_front is True
    markers = [str(line) for line in vm_root(vm)["markers"]]
    assert markers[-1] == "D5_F12_DEPOT_RECHECK reload-00 READY"
    phase = work.recheck_phase_outcome(
        [(request, readback)],
        prelaunch_digest=PRELAUNCH,
        facts_of_record=FACTS_OF_RECORD,
        funds_of_record=FUNDS_OF_RECORD,
    )
    assert phase["verification"] == "DEPOT_RELOAD_OBSERVED"
    assert phase["gate"]["verdict"] == "DEPOT_RELOAD_GATE_PASSES"
    assert phase["state_changed"] is False
    assert phase["mutations"] == []
    assert [row["cost"] for row in phase["receipts"]] == [0]
    assert [row["funds_after"] for row in phase["funds_chain"]] == [FUNDS_OF_RECORD]
    assert [row["exchange"] for row in phase["funds_chain"]] == ["reload-00"]


def test_handler_start_marker_and_bridge_identity():
    vm = build_recheck_vm(stop_at=1)
    vm.execute("try { bridge.Start(); } catch (e) { ::start_error <- e; }")
    markers = [str(m) for m in vm_root(vm)["markers"]]
    assert markers and markers[0] == "D5_F12_DEPOT_RECHECK_READY"
    assert vm_root(vm)["start_error"] == "CONTROLLED_STOP"
    # The save-restore identity bridge: the retained frozen info.nut name
    # resolves to the recheck proof class, exactly as the depot package does.
    vm.execute("::is_bridge <- NetworkFreightProof() instanceof D5DepotRecheckProof;")
    assert vm_root(vm)["is_bridge"] is True


def test_handler_diverging_world_halted_by_the_production_gates():
    """A drifted world is caught at the one read, STALE_PIN-preservingly."""
    vm = build_recheck_vm()
    # A world-side drift between staging and the read: the N stub bit goes.
    vm.execute("::road_bits[45743].n = false;")
    request = typed_request()
    readback = drive(vm, request)
    assert readback.status == "READY"  # the handler only measures
    assert readback.connected_front_to_depot is False
    phase = work.recheck_phase_outcome(
        [(request, readback)],
        prelaunch_digest=PRELAUNCH,
        facts_of_record=FACTS_OF_RECORD,
        funds_of_record=FUNDS_OF_RECORD,
    )
    assert phase["verification"] == "DEPOT_RELOAD_INCOMPLETE"
    assert phase["gate"]["verdict"] == "DEPOT_RELOAD_GATE_DIVERGED"
    assert phase["failed"] is not None
    assert "STALE_PIN" in phase["failed"]["error"]
    assert "connected_front_to_depot: measured False, pinned True" in phase["failed"]["error"]
    assert phase["pending"] == []


# --- the guard machinery and refusal ladder ----------------------------------


def test_handler_refusal_ladder():
    # A foreign exchange label outside the one-row reload schedule.
    vm = build_recheck_vm()
    assert reply(vm, base_request())["status"] == "OUT_OF_ORDER"

    # Company 1 exists in the stub and is refused (the fixed recheck company
    # pin is 0); every planned-label refusal halts the schedule, so each
    # refusal probe gets its own VM, as the depot suite does.
    vm = build_recheck_vm()
    assert reply(vm, recheck_request(company=1))["status"] == "INVALID_COMPANY"

    # A company that does not resolve at all is refused the same way.
    vm = build_recheck_vm()
    assert reply(vm, recheck_request(company=7))["status"] == "INVALID_COMPANY"

    # A drifted corridor pin is stale.
    vm = build_recheck_vm()
    assert reply(vm, recheck_request(pickup=45487, depot=45489))["status"] == "STALE_PIN"

    # A paused world is refused before any observation.
    vm = build_recheck_vm(paused=True)
    assert reply(vm, recheck_request())["status"] == "PAUSED"


def test_handler_halt_discipline_after_a_drifted_planned_exchange():
    """A terminal refusal on the planned exchange halts the schedule; the
    refused id cannot re-enter (budget accounting) and other labels stay
    refused without dispatching anything."""
    vm = build_recheck_vm(paused=True)
    assert reply(vm, recheck_request())["status"] == "PAUSED"
    expect_drop(vm, recheck_request())  # the same id never gets a second reply
    assert reply(vm, base_request())["status"] == "OUT_OF_ORDER"


def test_handler_budget_cap_and_duplicate_drop():
    vm = build_recheck_vm()
    for index in range(33):
        payload = recheck_request(request_id=f"probe-{index:02d}")
        before = len(vm_root(vm)["replies"])
        vm.execute("::bridge.Handle(" + squirrel_table(payload) + ");")
        if index < 32:
            assert len(vm_root(vm)["replies"]) == before + 1
        else:
            assert len(vm_root(vm)["replies"]) == before  # the 33rd id is dropped
    expect_drop(vm, recheck_request(request_id="probe-00"))  # a used id cannot re-enter


def test_handler_drops_foreign_shapes():
    vm = build_recheck_vm()
    # Foreign protocol families never enter the observe-only session.
    expect_drop(vm, {"protocol": 5})
    expect_drop(vm, {"protocol": 6, "op": "radius", "request_id": "radius-00"})
    expect_drop(vm, {"protocol": 9, "op": "box", "request_id": "pbox-00"})
    # No spend-capable op exists in the observe-only profile.
    for op in ("demolish", "road", "depot", "fleet", "truck"):
        expect_drop(vm, recheck_request(op=op))
    # The wire contract's forced attempt echo: other figures never account.
    expect_drop(vm, recheck_request(plan="z" * 64))
    expect_drop(vm, recheck_request(max_cost=0))
    expect_drop(vm, recheck_request(max_cost=1))
    expect_drop(vm, recheck_request(max_cost=3001))
    # The reload never touches a tile of any kind.
    expect_drop(vm, recheck_request(tile=45487))
    expect_drop(vm, recheck_request(front_tile=45743))
    expect_drop(vm, recheck_request(tile=45487, front_tile=45743))
    # Outside the native company domain.
    expect_drop(vm, recheck_request(company=15))


def test_dispatch_establishes_the_native_road_context_before_probes():
    """E72 regression (shared with the depot family): the 15.3 per-script
    current road type is INVALID_ROADTYPE (63) until a script sets it and
    every ScriptRoad depot/edge probe fail-closes on it (script_storage.hpp:67,
    script_road.cpp:44-51/:111/:497-502). The stub models exactly that, so the
    reload exchange must read the post-fix depot facts only through the
    dispatcher's own set+assert, and the context must stay established."""
    vm = build_recheck_vm()
    assert vm_root(vm)["cur_road_type"] == 63
    readback = drive(vm, typed_request())
    assert readback.status == "READY"
    assert readback.depot_present is True
    assert readback.front_read == DEPOT_FRONT
    assert readback.depot_linked is True
    assert readback.connected_front_to_depot is True
    assert vm_root(vm)["cur_road_type"] == 0


def test_dispatch_assert_refuses_when_the_road_type_is_unavailable():
    """E72 regression pair: the dispatch-entry assert stops the exchange
    before any probe when the native road context cannot be established —
    the reply stays a refusal with no unclaimed facts and the context is
    never faked."""
    vm = build_recheck_vm(road_type_ok=False)
    readback = drive(vm, typed_request())
    assert readback.status == "UNSUPPORTED_NATIVE_FACT"
    assert readback.depot_present is None
    assert vm_root(vm)["cur_road_type"] == 63


def test_handler_zero_spend_never_reports_a_cost():
    """The observe exchange can never spend or refund: the balance is
    carried verbatim and the cost of record stays zero even on a stub world
    with nonzero demolish/road/depot cost knobs."""
    vm = build_recheck_vm(demolish_cost=-5000, road_cost=9000, depot_cost=50000)
    readback = drive(vm, typed_request())
    assert readback.funds == 489650 and readback.cost == 0


def test_handler_refusals_carry_no_fresh_read():
    """A refusal carries the zero funds of the refusal ladder, never a fresh
    world observation, and never any depot fact."""
    vm = build_recheck_vm()
    vm.execute("::funds = 490257;")
    row = reply(vm, base_request())  # a foreign label: refused before any read
    assert row["status"] == "OUT_OF_ORDER"
    assert row["funds"] == 0 and row["cost"] == 0
    assert "depot_present" not in row


def test_handler_reply_shape_of_record():
    vm = build_recheck_vm()
    request = typed_request()
    before = len(vm_root(vm)["replies"])
    vm.execute("::bridge.Handle(" + request.to_bytes().decode() + ");")
    assert len(vm_root(vm)["replies"]) == before + 1
    reply_row = dict(vm_root(vm)["replies"][before])
    # The observe reply shape of record: no tile, no front tile, no fleet.
    assert "tile" not in reply_row and "front_tile" not in reply_row
    assert "count" not in reply_row and "vehicles" not in reply_row
    assert reply_row["funds"] == 489650 and reply_row["cost"] == 0
    assert reply_row["max_cost"] == 3000  # the depot contract's forced echo
    assert reply_row["status"] == "READY"
    assert reply_row["depot_linked"] is True
