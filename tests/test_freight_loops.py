"""Ticket-05 loop engine, offline fixtures: sealed cycles, built-service
exclusion, pause pacing and CLI gating qualify without any native process."""

import asyncio
import io
import json
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
    command_readback_evidence,
    loop_gate,
    loop_scaled_budgets,
    network_budgets,
    prepare,
    validate_loop_cycles,
    verify_loop_receipt,
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


def staged_loop_root(tmp_path, *, payload=None):
    """One loop attempt root with the recording shape of records; no cycles."""
    from app.simulation.openttd.proof.harness import manifest, sha256

    root = tmp_path / "loop-root"
    root.mkdir()
    metadata = dict(network=True, loop_cycles=2, random_budget=dict(capture_tile_limit=1024))
    (root / "PRELAUNCH.json").write_text(json.dumps(metadata))
    (root / "PRELAUNCH.sha256").write_text(sha256(root / "PRELAUNCH.json") + "\n")
    default = dict(
        status="NATIVE_LOOP_DELIVERED_VERIFIED",
        loops=[
            dict(cycle=1, status="DELIVERY_VERIFIED", selected=["route-1"]),
            dict(cycle=2, status="ZERO_SERVICE", error="NO_FEASIBLE_SERVICES: not feasible"),
        ],
        loop_cycles_planned=2,
        loop_cycles_delivered=1,
        launches=1,
        connections=2,
        requests=0,
        mutations=0,
        supplemental_requests=0,
        qualification_requests=0,
    )
    (root / "result.json").write_text(json.dumps(default if payload is None else payload))
    (root / "cleanup.json").write_text(
        json.dumps(dict(reaped=True, workspace_disposed=True, credential_removed=True))
    )
    (root / "frames.json").write_text(json.dumps([]))
    (root / "artifact-manifest.sha256").write_text(manifest(root))
    return root


def manifest(root):
    from app.simulation.openttd.proof.harness import manifest as root_manifest

    return root_manifest(root)


def test_verify_loop_receipt_refuses_a_missing_cycle_recording(tmp_path):
    root = staged_loop_root(tmp_path)
    with pytest.raises(ValueError, match="loop cycle recording missing: loop-cycle-1"):
        verify_loop_receipt(root)


def test_verify_loop_receipt_refuses_tampered_recording(tmp_path):
    root = staged_loop_root(tmp_path)
    result = json.loads((root / "result.json").read_bytes())
    result["loops"][0]["selected"] = ["route-1", "route-2"]
    (root / "result.json").write_text(json.dumps(result))
    with pytest.raises(ValueError, match="loop attempt manifest mismatch"):
        verify_loop_receipt(root)


def test_verify_loop_receipt_refuses_mismatched_seal(tmp_path):
    root = staged_loop_root(tmp_path)
    (root / "PRELAUNCH.sha256").write_text("0" * 64 + "\n")
    (root / "artifact-manifest.sha256").write_text(manifest(root))
    with pytest.raises(ValueError, match="loop prelaunch seal mismatch"):
        verify_loop_receipt(root)


def test_verify_loop_receipt_refuses_non_loop_attempt(tmp_path):
    root = staged_loop_root(tmp_path)
    metadata = json.loads((root / "PRELAUNCH.json").read_bytes())
    metadata["loop_cycles"] = 1
    (root / "PRELAUNCH.json").write_text(json.dumps(metadata))
    (root / "artifact-manifest.sha256").write_text(manifest(root))
    with pytest.raises(ValueError, match="requires a sealed loop attempt"):
        verify_loop_receipt(root)


def test_verify_loop_receipt_refuses_failed_status(tmp_path):
    root = staged_loop_root(
        tmp_path,
        payload=dict(
            status="NATIVE_MULTI_SERVICE_DELIVERY_VERIFIED",
            loops=[dict(cycle=1, status="DELIVERY_VERIFIED", selected=["route-1"])],
            loop_cycles_planned=2,
            loop_cycles_delivered=1,
            launches=1,
            connections=1,
            requests=0,
            mutations=0,
            supplemental_requests=0,
            qualification_requests=0,
        ),
    )
    with pytest.raises(ValueError, match="did not reach a verified terminal status"):
        verify_loop_receipt(root)


def test_replay_refuses_bad_loop_cycle_marker(tmp_path):
    from app.simulation.openttd.freight_planning_replay import replay_qualified_world

    prefix = [
        ["inbound", "670000"],
        ["inbound", "680000"],
        ["outbound", "020000"],
        ["outbound", "070000"],
        ["inbound", "7e0000"],
    ]
    (tmp_path / "qualification-prefix-frames.json").write_text(json.dumps(prefix))
    (tmp_path / "frames.json").write_text(json.dumps(prefix))
    (tmp_path / "loop-cycle.json").write_text(
        json.dumps(dict(schema="ramrom-loop-cycle-v0", funding_frames=0))
    )
    with pytest.raises(ValueError, match="loop cycle replay marker mismatch"):
        asyncio.run(replay_qualified_world(tmp_path, dict(scenario="high-budget-500k"), {}))


PLAN_X, PLAN_Y, PLAN_F = "d" * 64, "e" * 64, "f" * 64


def command_log(tmp_path, lines):
    path = tmp_path / "stderr.log"
    path.write_text("\n".join(lines) + "\n")
    return path


def command_records():
    records = {"inspect-1": SimpleNamespace(s=[0] * 24)}
    for i in range(10):
        records[f"build-{i}"] = SimpleNamespace(s=[0] * 23 + [10 + i])
    return records


def full_command_lines(plan, foreign=()):
    lines = []
    for i in range(10):
        for digest in foreign:
            lines.append(
                "FREIGHT_CONSTRUCTION_STAGE"
                f" stage={i} result=1 quoted=7 cost=7 spent=7 plan={digest}"
            )
            lines.append(
                f"FREIGHT_CONSTRUCTION_ROAD stage={i % 6} classification=COMMAND_SUCCEEDED"
                f" result=1 after=1 before=0 spent=7 plan={digest}"
            )
        cost = 10 + i
        lines.append(
            f"FREIGHT_CONSTRUCTION_STAGE stage={i} result=1 quoted={cost} cost={cost} spent={cost}"
            f" plan={plan}"
        )
        if i < 6:
            lines.append(
                f"FREIGHT_CONSTRUCTION_ROAD stage={i} classification=COMMAND_SUCCEEDED"
                f" result=1 after=1 before=0 spent={cost} plan={plan}"
            )
    return lines


def test_command_readback_shares_the_stream_with_known_foreign_plans(tmp_path):
    plan = SimpleNamespace(digest=PLAN_X)
    evidence = command_readback_evidence(
        command_log(tmp_path, full_command_lines(PLAN_X, foreign=(PLAN_Y, PLAN_F))),
        plan,
        command_records(),
        network_plans=(PLAN_Y,),
        foreign_plans=(PLAN_F,),
    )
    assert len(evidence["construction_stage_readbacks"]) == 10
    assert all(
        int(row["stage"]) == i for i, row in enumerate(evidence["construction_stage_readbacks"])
    )


def test_command_readback_skips_foreign_only_streams(tmp_path):
    plan = SimpleNamespace(digest=PLAN_X)
    with pytest.raises(ValueError, match="missing construction command stage readback"):
        command_readback_evidence(
            command_log(tmp_path, full_command_lines(PLAN_Y, foreign=(PLAN_F,))),
            plan,
            command_records(),
            network_plans=(PLAN_Y,),
            foreign_plans=(PLAN_F,),
        )


def test_command_readback_refuses_unknown_plan_lines(tmp_path):
    plan = SimpleNamespace(digest=PLAN_X)
    with pytest.raises(ValueError, match="construction command provenance mismatch"):
        command_readback_evidence(
            command_log(tmp_path, [full_command_lines(PLAN_X)[0][:-64] + "a" * 64]),
            plan,
            command_records(),
            network_plans=(PLAN_Y,),
            foreign_plans=(PLAN_F,),
        )
