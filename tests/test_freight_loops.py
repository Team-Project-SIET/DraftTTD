"""Ticket-05 loop engine, offline fixtures: sealed cycles, built-service
exclusion, pause pacing and CLI gating qualify without any native process."""

import asyncio
import io
from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from test_qualification_coordinator import QualificationWire, collect
from test_supplemental_planning_contracts import correspondence, fact_dict, facts

import app.simulation.openttd.proof.road_mutation as road_mutation
from app.openttd_demo import main as demo_main
from app.planning.p08_adapter import MonthlyBatchPolicy
from app.simulation.openttd.cargo_page import CargoCatalogRecord
from app.simulation.openttd.freight_native_network import (
    network_from_facts,
    paused_world_clock,
)
from app.simulation.openttd.proof.freight_delivery import (
    NETWORK_BUDGETS,
    loop_gate,
    loop_scaled_budgets,
    network_budgets,
    prepare,
    validate_loop_cycles,
)
from app.simulation.openttd.world_planning_observation import WorldPlanningObservation


@pytest.fixture(scope="module")
def qualified_vanilla():
    async def qualified():
        wire = QualificationWire(industries=(2, 17, 30, 40), produces=(1,))
        wire.accepts = (1,)
        wire.metrics = (80, 0, 0)
        result = await collect(wire, await wire.owner())
        return WorldPlanningObservation(result.verification.stability.final, result)

    def record(i, label, freight, effect, classes):
        return CargoCatalogRecord(i, f"{i:08X}", freight, effect, classes)

    with patch("test_structural_world.CargoCatalogRecord", side_effect=record):
        world = asyncio.run(qualified())
    captured = []
    policy = MonthlyBatchPolicy(
        start_date=date(2001, 1, 1), delivery_batch_limit=40, budget_gbp=Decimal(4000)
    )
    for producer, acceptor, row, width in ((2, 17, 1, 6), (2, 30, 4, 6), (40, 30, 7, 9)):
        d = fact_dict(world)
        d["engines"][0]["purchase_cost_gbp"] = 500
        start_y = 1 if row == 1 else row - 1
        d["region"] = dict(x=0, y=start_y, width=width, height=2)
        prototype = d["tiles"][0]
        map_width = world.context.world.map_width
        eligible = {(x, y) for y in (1, 4, 7) for x in range(9 if y == 7 else 6)}
        eligible |= {(1, 2), (1, 3), (1, 6)}
        d["tiles"] = [
            dict(prototype, tile_id=y * map_width + x, x=x, y=y, buildable=(x, y) in eligible)
            for y in range(start_y, start_y + 2)
            for x in range(width)
        ]
        d["coverage_scopes"] = [
            dict(industry_id=producer, cargo_id=1, role="pickup"),
            dict(industry_id=acceptor, cargo_id=1, role="delivery"),
        ]
        d["coverage"] = [
            dict(
                tile_id=t["tile_id"],
                **scope,
                producer_count=1,
                acceptance_eighths=8,
                industry_covered=t["y"] == row
                and t["x"] == (0 if scope["role"] == "pickup" else width - 1),
            )
            for t in d["tiles"]
            for scope in d["coverage_scopes"]
        ]
        captured.append(facts(world, d))
    return world, captured, correspondence(world), policy


def demands(power):
    return [str(r.demand_id) for r in power.scenario.cargo_demands]


def test_network_budgets_scale_only_loop_volume():
    assert network_budgets(2) == NETWORK_BUDGETS
    scaled = network_budgets(2, loop_cycles=3)
    assert scaled == NETWORK_BUDGETS | dict(
        requests=NETWORK_BUDGETS["requests"] * 3,
        mutations=NETWORK_BUDGETS["mutations"] * 3,
        supplemental_requests=NETWORK_BUDGETS["supplemental_requests"] * 3,
        total_seconds=NETWORK_BUDGETS["total_seconds"] * 3,
        construction_commands=NETWORK_BUDGETS["construction_commands"] * 3,
        world_preparation_mutations=NETWORK_BUDGETS["world_preparation_mutations"],
        selected_services=NETWORK_BUDGETS["selected_services"],
    )
    assert loop_scaled_budgets(dict(requests=5), 2) == dict(requests=10)
    assert loop_scaled_budgets({}, 2) == {}


@pytest.mark.parametrize("value", [0, 9, "2", 1.5, None])
def test_loop_cycle_bounds_refuse_out_of_band(value):
    with pytest.raises(ValueError):
        validate_loop_cycles(value)


def test_network_from_facts_cycles_request_new_services_only(qualified_vanilla):
    world, captured, source, policy = qualified_vanilla
    baseline = network_from_facts(
        world, captured, source, policy, max_vehicles=4, service_batches=True
    )
    assert demands(baseline) == ["benchmark-2-1-17", "benchmark-2-1-30", "benchmark-40-1-30"]


def test_network_from_facts_excludes_already_built_services(qualified_vanilla):
    world, captured, source, policy = qualified_vanilla
    rejections = []
    second = network_from_facts(
        world,
        captured,
        source,
        policy,
        max_vehicles=4,
        service_batches=True,
        planning_rejections=rejections,
        exclude={(2, 17, 1)},
    )
    assert demands(second) == ["benchmark-2-1-30", "benchmark-40-1-30"]
    assert dict(source=2, destination=17, cargo=1, reason="SERVICE_ALREADY_BUILT") in rejections
    assert "CAPTURE_REGION_BOUND" not in [r.get("reason") for r in rejections]


def test_all_excluded_relationships_raise_typed_zero_service(qualified_vanilla):
    world, captured, source, policy = qualified_vanilla
    with pytest.raises(ValueError) as error:
        network_from_facts(
            world,
            captured,
            source,
            policy,
            max_vehicles=4,
            service_batches=True,
            exclude={(2, 17, 1), (2, 30, 1), (40, 30, 1)},
        )
    assert str(error.value) == (
        "NO_FEASIBLE_SERVICES: all 3 captured relationships are excluded already-built services"
    )


def test_pause_pair_pauses_and_resumes_once():
    backend = SimpleNamespace(process=SimpleNamespace(stdin=io.BytesIO()))
    diagnostic = {}

    async def drive():
        async with paused_world_clock(backend, diagnostic=diagnostic):
            assert backend.process.stdin.getvalue() == b"pause\n"

    asyncio.run(drive())
    assert backend.process.stdin.getvalue() == b"pause\nunpause\n"
    assert diagnostic == dict(pause_pairs=1)


def test_failed_resume_is_recorded_never_silent(monkeypatch):
    real = road_mutation.console

    def console(process, command):
        if command == "unpause":
            raise RuntimeError("owned console missing")
        return real(process, command)

    monkeypatch.setattr(road_mutation, "console", console)
    backend = SimpleNamespace(process=SimpleNamespace(stdin=io.BytesIO()))
    diagnostic = {}

    async def drive():
        with pytest.raises(RuntimeError, match="pausing capture"):
            async with paused_world_clock(backend, diagnostic=diagnostic):
                raise RuntimeError("pausing capture failed")

    asyncio.run(drive())
    assert diagnostic["pause_resume_error"] == "owned console missing"
    assert "pause_pairs" not in diagnostic


def test_loop_gate_typing():
    with pytest.raises(ValueError):
        loop_gate({})
    with pytest.raises(ValueError):
        loop_gate(dict(loop_cycles=2, network=True, planner=False))
    assert (
        loop_gate(
            dict(
                loop_cycles=2,
                network=True,
                planner=True,
                demo=True,
                random_world=dict(seed=2026),
            )
        )
        == 2
    )


def test_prepare_refuses_unsealed_loop_settings(tmp_path):
    target = tmp_path / "never-created"
    with pytest.raises(ValueError):
        prepare(target, loop_cycles=2)
    with pytest.raises(ValueError):
        prepare(target, demo=True, planner=True, network=True, loop_cycles=0)
    with pytest.raises(ValueError):
        prepare(target, demo=True, planner=True, network=True, loop_cycles=9)
    assert not target.exists()


def test_cycle_cli_requires_random_world():
    with pytest.raises(SystemExit):
        demo_main(["run", "--cycles", "3"])
    with pytest.raises(SystemExit):
        demo_main(["run", "--cycles", "0", "--random-world"])
    with pytest.raises(SystemExit):
        demo_main(["run", "--cycles", "9", "--random-world"])
