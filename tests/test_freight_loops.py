"""Ticket-05 loop engine, offline fixtures: sealed cycles, built-service
exclusion, pause pacing and CLI gating qualify without any native process."""

import ast
import asyncio
import hashlib
import json
import re
import shutil
from datetime import date
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from test_console_echo_handshake import (
    PAUSE_ECHO,
    Backend,
    EchoingGame,
    prepared_for,
    tail,
)
from test_qualification_coordinator import QualificationWire, collect
from test_random_distance import controlled_flat_coal_data, controlled_input
from test_supplemental_planning_contracts import correspondence, fact_dict, facts

import app.simulation.openttd.proof.road_mutation as road_mutation
from app.demo_random import DemoBudgets, relationship_region
from app.openttd_demo import main as demo_main
from app.planning.p08_adapter import MonthlyBatchPolicy
from app.simulation.openttd.cargo_page import CargoCatalogRecord
from app.simulation.openttd.freight_native_network import (
    network_from_facts,
    paused_world_clock,
)
from app.simulation.openttd.freight_runtime_planning import (
    PlanningRead,
    PlanningReadback,
    capture_planning_facts,
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


def test_pause_pair_pauses_and_resumes_once(tmp_path):
    prepared = prepared_for(tmp_path)
    game = EchoingGame(prepared.spec.stdout_path)
    backend = Backend(game)
    diagnostic = {}

    async def drive():
        async with paused_world_clock(backend, prepared, diagnostic=diagnostic):
            assert game.stream.getvalue() == b"pause\n"
            assert PAUSE_ECHO in tail(prepared)

    asyncio.run(drive())
    assert game.stream.getvalue() == b"pause\nunpause\n"
    assert diagnostic == dict(pause_pairs=1)


def test_failed_resume_is_recorded_never_silent(monkeypatch, tmp_path):
    real_ack = road_mutation.console_ack

    def console_ack(backend, prepared, command, marker, **kwargs):
        if command == "unpause":
            raise RuntimeError("owned console missing")
        return real_ack(backend, prepared, command, marker, **kwargs)

    monkeypatch.setattr(road_mutation, "console_ack", console_ack)
    prepared = prepared_for(tmp_path)
    game = EchoingGame(prepared.spec.stdout_path)
    backend = Backend(game)
    diagnostic = {}

    async def drive():
        with pytest.raises(RuntimeError, match="pausing capture"):
            async with paused_world_clock(backend, prepared, diagnostic=diagnostic):
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


# --- E150 follow-up audit: per-cycle artifact surface of the loop chain -------

SEALED_ATTEMPT1 = Path("artifacts/demos/playable-demo-246dc3a4f4fc4b40aee0f73696455473")


def test_cycle_copy_set_covers_every_prepared_directory_read_of_the_chain():
    """Audit of record (E150 follow-up): every plain constant path touched
    under prepared.directory by the per-cycle chain (freight_native_network +
    freight_runtime_planning) must be one of: a root-stage copy carried by the
    loop staging tuple of freight_delivery.py, a per-cycle file the flow
    writes itself before the read, or an exchange packet written by the
    exchange() disc into the cycle dir in the same flow. Any new read fails
    here until its source is classified and staged."""
    chain = []
    tree = ast.parse(Path("app/simulation/openttd/freight_native_network.py").read_text())
    chain.append(("freight_native_network", tree))
    tree = ast.parse(Path("app/simulation/openttd/freight_runtime_planning.py").read_text())
    chain.append(("freight_runtime_planning", tree))

    def prepared_directory(node):
        """Run-time cycle receiver: the `prepared.directory` attribute the
        loop chain passes down (the exact receiver attempt-1 died at).
        Verify-path plain `directory` names are a different layer, replayed
        against recordings by the E150 pin and the addendum #8 readback."""
        return (
            isinstance(node, ast.Attribute)
            and isinstance(node.value, ast.Name)
            and node.value.id == "prepared"
            and node.attr == "directory"
        )

    def write_target(node):
        return (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "write_json"
            and node.args
            and isinstance(node.args[0], ast.BinOp)
            and prepared_directory(node.args[0].left)
            and isinstance(node.args[0].right, ast.Constant)
            and isinstance(node.args[0].right.value, str)
        )

    def constant_paths(walk):
        for node in walk:
            if (
                isinstance(node, ast.BinOp)
                and isinstance(node.op, ast.Div)
                and prepared_directory(node.left)
                and isinstance(node.right, ast.Constant)
                and isinstance(node.right.value, str)
            ):
                yield node

    # A write_json call's args[0] path node WRITES the record; every other
    # occurrence of the same path — an sha256 digest nested in a write's
    # payload, an open/json read — is a READ. Classify per occurrence, then
    # per name.
    write_ids = set()
    for _module, walk in chain:
        for node in ast.walk(walk):
            if isinstance(node, ast.Call) and write_target(node):
                write_ids.add(id(node.args[0]))

    roles: dict[str, set[str]] = {}
    for module, walk in chain:
        for node in constant_paths(ast.walk(walk)):
            roles.setdefault(node.right.value, set()).add(
                "write" if id(node) in write_ids else "read"
            )

    staging = Path("app/simulation/openttd/proof/freight_delivery.py").read_text()
    copied_match = re.search(
        r"Per-cycle copies of every root artifact.*?for name in \(([^)]*)\)", staging, re.S
    )
    assert copied_match is not None
    copied_names = set(re.findall(r'"([A-Za-z0-9._-]+)"', copied_match.group(1)))
    # The staging source of truth: per-cycle copies of every root-only
    # artifact the chain reads, plus the seal companions the verify replay
    # needs; runtime-identity.json is written per cycle by run_loops itself.
    assert copied_names == {
        "PRELAUNCH.json",
        "PRELAUNCH.sha256",
        "CLAIM.json",
        "frozen-source.zip",
        "graphics-identity.json",
    }
    assert re.search(r'write_json\(\n\s+cycle_dir / "runtime-identity\.json"', staging)
    # Read partition of the chain's plain constant prepared.directory paths:
    # root-stage copies, per-cycle staging self-writes, chain self-writes
    # before read (qualification-prefix-frames.json from
    # collect_qualified_world), and exchange-disc packets (capacity digests
    # read the same connection's retained responses). Write-only names are
    # exactly the complement and are never read.
    reads = {name for name, level in roles.items() if "read" in level}
    assert reads == {
        "PRELAUNCH.json",
        "graphics-identity.json",
        "runtime-identity.json",
        "qualification-prefix-frames.json",
        "capacity-add-response.json",
        "capacity-read-response.json",
    }, sorted(reads)
    write_only = set(roles) - reads
    assert write_only and all(
        level == {"write"} for name, level in roles.items() if name in write_only
    )
    funding = re.search(r"for name in \(([^)]*capital-initialize-request[^)]*)\)", staging, re.S)
    assert funding is not None
    assert set(re.findall(r'"([A-Za-z0-9._-]+)"', funding.group(1))) == {
        "capital-initialize-request.json",
        "capital-initialize-response.json",
        "capital-read-request.json",
        "capital-read-response.json",
        "scenario-capital.json",
    }


def test_cycle_capture_builds_supplemental_facts_from_the_staged_cycle_dir(tmp_path):
    """E150 follow-up, end to end offline: stage loop-cycle-1 exactly like
    run_loops does (the extended copy set + per-cycle runtime-identity and
    loop marker), then drive the real supplemental-facts capture against the
    staged recording alone — attempt 1 died natively at exactly this seam on
    the missing per-cycle graphics-identity.json."""
    root = tmp_path / "attempt"
    cycle_dir = root / "loop-cycle-1"
    cycle_dir.mkdir(parents=True)
    (root / "PRELAUNCH.json").write_text(
        json.dumps(dict(planner=True, network=True, loop_cycles=2))
    )
    seal = hashlib.sha256((root / "PRELAUNCH.json").read_bytes()).hexdigest()
    (root / "PRELAUNCH.sha256").write_text(seal + "\n")
    (root / "CLAIM.json").write_text(
        json.dumps(dict(consumed=True, prelaunch_digest=seal, launches_allowed=1, retries=0))
    )
    (root / "frozen-source.zip").write_bytes(b"loop-cycle-pinning")
    (root / "graphics-identity.json").write_text(json.dumps(dict(archive_sha256="a" * 64)))
    for name in (
        "PRELAUNCH.json",
        "PRELAUNCH.sha256",
        "CLAIM.json",
        "frozen-source.zip",
        "graphics-identity.json",
    ):
        shutil.copyfile(root / name, cycle_dir / name)
    (cycle_dir / "runtime-identity.json").write_text(
        json.dumps(
            dict(encrypted=True, welcome=dict(revision="15.3", seed=17, width=64, height=64))
        )
    )
    (cycle_dir / "loop-cycle.json").write_text(
        json.dumps(dict(schema="ramrom-loop-cycle-v1", cycle=1, loop_cycles=2, funding_frames=4))
    )
    value = controlled_input()
    world = value.admitted.world
    data = controlled_flat_coal_data()
    lookup = {t["tile_id"]: t for t in data["tiles"]}
    scopes = {(c["tile_id"], c["role"]): c for c in data["coverage"]}
    calls = []

    async def exchange(session, request, directory, response_type):
        calls.append(request)
        assert directory == cycle_dir  # every planning packet lands in the cycle recording
        if request.kind == "settings":
            row = [1, 0, 0, 3, 0, 10, 50, 100]
        elif request.kind == "engines":
            row = [7]
        elif request.kind == "engine":
            row = [7, 1, 0, 30, 1000, 365, 40]
        else:
            assert request.arg in lookup
            row = (
                [request.arg, 0, 0, 1]
                + [0] * 10
                + [
                    -1,
                    1,
                    8,
                    int(scopes[request.arg, "pickup"]["industry_covered"]),
                    int(scopes[request.arg, "delivery"]["industry_covered"]),
                ]
            )
        date_value = value.facts.capture_economy_date_before
        payload = dict(
            protocol=1,
            type="planning_read_result",
            request_id=request.request_id,
            kind=request.kind,
            arg=request.arg,
            src=request.src,
            dst=request.dst,
            cargo=request.cargo,
            before=date_value,
            after=date_value,
            data=row,
        )
        raw = json.dumps(payload, separators=(",", ":")).encode()
        assert len(raw) <= 512
        (directory / (request.request_id + "-request.json")).write_bytes(request.to_bytes())
        (directory / (request.request_id + "-response.json")).write_bytes(raw)
        return PlanningReadback.parse_for(request, raw)

    captured = asyncio.run(
        capture_planning_facts(
            SimpleNamespace(health=lambda: None, session=object()),
            SimpleNamespace(directory=cycle_dir, endpoints=(1, 2)),
            world,
            read_exchange=exchange,
            relationship=(0, 1, 1),
            prefix="n0-",
            capture_budget=DemoBudgets(),
        )
    )
    assert len(captured.tiles) == 450 and len(captured.coverage) == 900
    region = relationship_region(world, (0, 1, 1), 512)
    assert dict(captured.region.model_dump()) == region
    digest = hashlib.sha256((cycle_dir / "graphics-identity.json").read_bytes()).hexdigest()
    assert captured.source.content_digest == digest
    assert captured.settings.generation_seed == 17
    stored = json.loads((cycle_dir / "supplemental-planning-facts.json").read_text())
    assert stored["source"]["content_digest"] == digest
    assert [scope.role for scope in captured.coverage_scopes] == ["pickup", "delivery"]
    captured.require_world(world)
    assert len({request.kind for request in calls}) == 4
    assert (cycle_dir / "planning-n0-0-request.json").is_file()
    assert (cycle_dir / "planning-n0-452-response.json").is_file()


def test_sealed_attempt1_failed_bytes_stay_pinned():
    """Attempt-1 of record keeps its sealed typed FAILED identity forever;
    this read-only pin re-derives its manifest integrity and its recorded
    facts exactly as E150 recorded them (a clone without the retained bytes
    fails here meaning missing evidence, never regeneration)."""
    result = json.loads((SEALED_ATTEMPT1 / "result.json").read_bytes())
    assert result["status"] == "FAILED"
    assert result["error"].startswith("FileNotFoundError: [Errno 2] No such file or directory: ")
    assert result["error"].endswith("/loop-cycle-1/graphics-identity.json'")
    assert result["launches"] == 1 and result["connections"] == 1
    assert result["requests"] == 0 and result["mutations"] == 0
    assert (result["funding_requests"], result["funding_mutations"]) == (2, 1)
    assert result["failure_save_error"] == "owned native save completion missing"
    assert not (SEALED_ATTEMPT1 / "loop-cycle-2").exists()
    assert manifest(SEALED_ATTEMPT1) == (SEALED_ATTEMPT1 / "artifact-manifest.sha256").read_text()
    cycle = SEALED_ATTEMPT1 / "loop-cycle-1"
    assert manifest(cycle) == (cycle / "artifact-manifest.sha256").read_text()
    diagnostic = json.loads((cycle / "planning-diagnostic.json").read_bytes())
    assert diagnostic["status"] == "FAILED"
    assert diagnostic["capture_requests_attempted"] == 832
    assert diagnostic["capture_requests_completed"] == 832
    assert diagnostic["pause_pairs"] == 1
    assert "pause_resume_error" not in diagnostic
    assert diagnostic["captured_relationships"] == 0 and diagnostic["search_truncated"] is True
    assert diagnostic["candidate_count"] is None and diagnostic["selected_service_count"] is None
    assert len(diagnostic["compatible_relationships"]) == 16
    observation = json.loads((cycle / "world-planning-observation.json").read_bytes())
    assert observation["qualified_month"]["economy_month"] == 2
    for name in (
        "capital-initialize-request.json",
        "capital-initialize-response.json",
        "capital-read-request.json",
        "capital-read-response.json",
        "scenario-capital.json",
        "before.sav",
        "planning-n0-0-request.json",
        "planning-n0-0-response.json",
        "loop-cycle.json",
        "network-candidates.json",
    ):
        assert (cycle / name).is_file()
    for name in ("cleanup.json", "stdout.log", "stderr.log", "artifact-manifest.sha256"):
        assert (cycle / name).is_file()


# --- Cross-cycle request identity (planner_used dedup fix) -------------------


def request_id_protocol_valid(value) -> bool:
    """Mirror of the GameScript ValidRequestID constraint
    (gamescript_bridge_package/main.nut:15): 1..64 chars, ASCII alnum plus
    `-`/`_` separators, never leading."""
    if type(value) is not str or not 1 <= len(value) <= 64:
        return False
    for index, ch in enumerate(value):
        if not (ch.isascii() and ch.isalnum()) and (index == 0 or ch not in "-_"):
            return False
    return True


PLANNER_CHANNEL_SCHEDULE = (
    "random-generation",
    "planning-seal",
    "planning-n0-0",
    "planning-n0-452",
    "planning-n15-2086",
)
DELIVERY_CHANNEL_SCHEDULE = (
    "select-0",
    "select-1",
    "activate-0",
    "s0-build-9",
    "s0-read-9",
    "s0-observe-3",
    "s0-finish",
    "s0-park",
    "s0-park-read",
)


def test_cycle_request_ids_keep_legacy_cycle1_and_are_unique_at_cycles_2_and_8():
    """The cleaner helper keeps cycle 1 byte-identical to the sealed legacy
    identifiers and suffixes later cycles deterministically; every produced id
    satisfies the GameScript ValidRequestID protocol constraint."""
    from app.simulation.openttd.freight_runtime_planning import cycle_request_id

    for schedule in (PLANNER_CHANNEL_SCHEDULE, DELIVERY_CHANNEL_SCHEDULE):
        assert [cycle_request_id(base, 1) for base in schedule] == list(schedule)
        for cycle in (2, 8):
            cycled = [cycle_request_id(base, cycle) for base in schedule]
            assert cycled == [base + f"-c{cycle}" for base in schedule]
            assert len(set(cycled + list(schedule))) == len(cycled) + len(schedule)
            assert all(request_id_protocol_valid(value) for value in cycled)
    widest = cycle_request_id("planning-n15-2086", 8)
    assert widest == "planning-n15-2086-c8"
    assert request_id_protocol_valid(widest) and len(widest) <= 64


def test_cycle_ids_satisfy_the_python_wire_contracts():
    """The GameScript guard allows 1..64 chars, but the Python wire contracts
    are the tighter bound of record: PlanningRead's field pattern (`1..32`,
    alnum plus `-`) on the planner channel and DeliveryRequest.to_bytes
    (`<=32`, ASCII alnum plus `-`) on the delivery channel. The cycled
    identities must satisfy the models the exchange layer actually wires."""
    from typing import Literal

    from app.simulation.openttd.freight_delivery import DeliveryRequest
    from app.simulation.openttd.freight_runtime_planning import PlanningRead, cycle_request_id

    plan_digest = "a" * 64
    op_for: dict[str, Literal["inspect", "build", "read", "observe", "finish"]] = {
        "select-0": "inspect",
        "select-1": "inspect",
        "activate-0": "read",
        "s0-build-9": "build",
        "s0-read-9": "read",
        "s0-observe-3": "observe",
        "s0-finish": "finish",
        "s0-park": "finish",
        "s0-park-read": "read",
    }
    for schedule in (PLANNER_CHANNEL_SCHEDULE, DELIVERY_CHANNEL_SCHEDULE):
        for base in schedule:
            request_id = cycle_request_id(base, 1)
            for cycle in (2, 8):
                cycled = cycle_request_id(base, cycle)
                if base in PLANNER_CHANNEL_SCHEDULE:
                    PlanningRead(
                        request_id=request_id, kind="settings", arg=0, src=0, dst=0, cargo=0
                    )
                    PlanningRead(request_id=cycled, kind="settings", arg=0, src=0, dst=0, cargo=0)
                else:
                    DeliveryRequest(
                        op=op_for[base], request_id=request_id, plan=plan_digest
                    ).to_bytes()
                    DeliveryRequest(op=op_for[base], request_id=cycled, plan=plan_digest).to_bytes()
            assert len(request_id) <= 32 and len(cycled) <= 32

    # A 33-char id passes the GameScript guard but is rejected by the Python
    # wire guard of record.
    with pytest.raises(ValueError):
        DeliveryRequest(op="read", request_id="a" * 33, plan=plan_digest).to_bytes()


def test_loop_cycle_marker_is_the_shared_cycle_source_of_truth(tmp_path):
    from app.simulation.openttd.freight_runtime_planning import loop_cycle

    # A directory without the marker replays as the legacy cycle 1.
    assert loop_cycle(tmp_path) == 1
    (tmp_path / "loop-cycle.json").write_text(
        json.dumps(dict(schema="ramrom-loop-cycle-v1", cycle=3))
    )
    assert loop_cycle(tmp_path) == 3
    (tmp_path / "loop-cycle.json").write_text(json.dumps(dict(schema="other", cycle=3)))
    with pytest.raises(ValueError, match="loop cycle marker invalid"):
        loop_cycle(tmp_path)
    (tmp_path / "loop-cycle.json").write_text(
        json.dumps(dict(schema="ramrom-loop-cycle-v1", cycle=9))
    )
    with pytest.raises(ValueError, match="loop cycle marker out of range"):
        loop_cycle(tmp_path)


class PlannerDrop(Exception):
    """Offline model of the GameScript planner_used silent drop."""


def fake_planning_exchange(tile_data, coverage, used, date_value=10):
    """Fake exchange that models the persistent planner_used set: a request id
    already consumed is rejected, and every accepted id is remembered."""

    async def fake(session, request, directory, response_type):
        if request.request_id in used:
            raise PlannerDrop(request.request_id)
        used.add(request.request_id)
        if request.kind == "settings":
            row = [1, 0, 0, 3, 0, 10, 50, 100]
        elif request.kind == "engines":
            row = [7]
        elif request.kind == "engine":
            row = [7, 1, 0, 30, 1000, 365, 40]
        else:
            assert request.arg in tile_data
            row = (
                [request.arg, 0, 0, 1]
                + [0] * 10
                + [
                    -1,
                    1,
                    8,
                    tile_data[request.arg]["pickup"],
                    tile_data[request.arg]["delivery"],
                ]
            )
        payload = dict(
            protocol=1,
            type="planning_read_result",
            request_id=request.request_id,
            kind=request.kind,
            arg=request.arg,
            src=request.src,
            dst=request.dst,
            cargo=request.cargo,
            before=date_value,
            after=date_value,
            data=row,
        )
        raw = json.dumps(payload, separators=(",", ":")).encode()
        assert len(raw) <= 512
        (directory / (request.request_id + "-request.json")).write_bytes(request.to_bytes())
        (directory / (request.request_id + "-response.json")).write_bytes(raw)
        return PlanningReadback.parse_for(request, raw)

    return fake


def _cycle_directory(root: Path, cycle: int) -> Path:
    cycle_dir = root / f"loop-cycle-{cycle}"
    cycle_dir.mkdir(parents=True, exist_ok=True)
    (cycle_dir / "graphics-identity.json").write_text(json.dumps(dict(archive_sha256="a" * 64)))
    (cycle_dir / "runtime-identity.json").write_text(
        json.dumps(
            dict(encrypted=True, welcome=dict(revision="15.3", seed=17, width=64, height=64))
        )
    )
    (cycle_dir / "loop-cycle.json").write_text(
        json.dumps(dict(schema="ramrom-loop-cycle-v1", cycle=cycle, loop_cycles=8))
    )
    return cycle_dir


def test_simulated_persistent_planner_used_accepts_all_reads_across_cycles(
    qualified_vanilla, tmp_path
):
    """Drive the real capture against a persistent dedup set over cycles 1,
    2 and 8: every planner-channel read progresses (request then response), no
    id is ever replayed, and cycle 1 keeps the legacy identifiers."""
    from app.simulation.openttd.freight_runtime_planning import cycle_request_id

    world = controlled_input().admitted.world
    data = controlled_flat_coal_data()
    capture_date = controlled_input().facts.capture_economy_date_before
    scopes = {(c["tile_id"], c["role"]): c for c in data["coverage"]}
    tile_views = {
        tile["tile_id"]: dict(
            pickup=int(scopes[tile["tile_id"], "pickup"]["industry_covered"]),
            delivery=int(scopes[tile["tile_id"], "delivery"]["industry_covered"]),
        )
        for tile in data["tiles"]
    }
    used: set[str] = set()
    first_ids: dict[int, list[str]] = {}
    for cycle in (1, 2, 8):
        cycle_dir = _cycle_directory(tmp_path, cycle)
        calls = []

        async def recording(session, request, directory, response_type):
            calls.append(request)
            return await fake_planning_exchange(tile_views, scopes, used, capture_date)(
                session, request, directory, response_type
            )

        asyncio.run(
            capture_planning_facts(
                SimpleNamespace(health=lambda: None, session=object()),
                SimpleNamespace(directory=cycle_dir),
                world,
                read_exchange=recording,
                relationship=(0, 1, 1),
                prefix="n0-",
                capture_budget=DemoBudgets(),
            )
        )
        first_ids[cycle] = [request.request_id for request in calls]
    # Cycle 1 legacy byte-identity; later cycles suffixed and globally unique.
    assert first_ids[1][0] == "planning-n0-0" and first_ids[1][-1] == "planning-n0-452"
    assert first_ids[2][0] == cycle_request_id("planning-n0-0", 2)
    assert first_ids[8][0] == cycle_request_id("planning-n0-0", 8)
    everything = first_ids[1] + first_ids[2] + first_ids[8]
    assert len(everything) == len(set(everything))
    assert all(request_id_protocol_valid(value) for value in everything)


def test_planner_dedup_contract_still_rejects_a_duplicate_id(tmp_path):
    """The GameScript deduplication contract stays the enforcement mechanism:
    an unchanged (legacy-style) replay is rejected by the modeled planner_used
    set, exactly as the native bridge does."""
    from app.simulation.openttd.freight_runtime_planning import cycle_request_id

    cycle_dir = _cycle_directory(tmp_path, 1)
    used: set[str] = set()
    fake = fake_planning_exchange({}, set(), used)
    request = PlanningRead(
        request_id="planning-n0-0", kind="settings", arg=0, src=0, dst=1, cargo=1
    )
    asyncio.run(fake(None, request, cycle_dir, PlanningReadback))
    with pytest.raises(PlannerDrop, match="planning-n0-0"):
        asyncio.run(fake(None, request, cycle_dir, PlanningReadback))
    request_id, cycle = request.request_id, 2
    replay = PlanningRead(request_id=f"{request_id}", kind="settings", arg=0, src=0, dst=1, cargo=1)
    with pytest.raises(PlannerDrop):
        asyncio.run(fake(None, replay, cycle_dir, PlanningReadback))
    suffixed = PlanningRead(
        request_id=cycle_request_id(request_id, cycle),
        kind="settings",
        arg=0,
        src=0,
        dst=1,
        cargo=1,
    )
    asyncio.run(fake(None, suffixed, cycle_dir, PlanningReadback))  # accepted


def test_exchange_read_timeout_is_typed_with_context_and_cause(tmp_path, monkeypatch):
    """The 20-second per-exchange read timeout surfaces typed, carrying only
    the request id, operation, duration and cycle; payloads are never exposed."""
    from app.simulation.openttd.proof import freight_delivery

    class StalledSession:
        async def send(self, raw):
            return None

        async def receive(self):
            await asyncio.sleep(1)

    (tmp_path / "loop-cycle.json").write_text(
        json.dumps(dict(schema="ramrom-loop-cycle-v1", cycle=2))
    )
    monkeypatch.setattr(freight_delivery, "EXCHANGE_SECONDS", 0.05)
    request = PlanningRead(
        request_id="planning-seal-c2", kind="settings", arg=0, src=1, dst=2, cargo=1
    )
    with pytest.raises(freight_delivery.ExchangeReadTimeout) as exc_info:
        asyncio.run(freight_delivery.exchange(StalledSession(), request, tmp_path))
    error = exc_info.value
    assert isinstance(error, TimeoutError) and type(error) is not TimeoutError
    assert error.__cause__.__class__ is TimeoutError
    assert error.request_id == "planning-seal-c2"
    assert error.op == "settings"
    assert error.seconds == pytest.approx(0.05)
    assert error.cycle == 2
    message = str(error)
    assert (
        "request_id=planning-seal-c2" in message
        and "op=settings" in message
        and "cycle=2" in message
        and "data" not in message
    )


def test_exchange_read_timeout_without_cycle_marker_reports_cycle_none(tmp_path, monkeypatch):
    from app.simulation.openttd.proof import freight_delivery

    class StalledSession:
        async def send(self, raw):
            return None

        async def receive(self):
            await asyncio.sleep(1)

    monkeypatch.setattr(freight_delivery, "EXCHANGE_SECONDS", 0.05)
    request = PlanningRead(
        request_id="planning-seal", kind="settings", arg=0, src=1, dst=2, cargo=1
    )
    with pytest.raises(freight_delivery.ExchangeReadTimeout) as exc_info:
        asyncio.run(freight_delivery.exchange(StalledSession(), request, tmp_path))
    assert exc_info.value.cycle is None and exc_info.value.request_id == "planning-seal"


def test_outer_attempt_budget_expires_as_a_bare_timeouterror(tmp_path, monkeypatch):
    """The outer attempt budget must stay distinguishable from the typed
    per-exchange read timeout: an outer expiry is never converted."""
    from app.simulation.openttd.proof import freight_delivery

    class StalledSession:
        async def send(self, raw):
            return None

        async def receive(self):
            await asyncio.sleep(1)

    monkeypatch.setattr(freight_delivery, "EXCHANGE_SECONDS", 5)
    request = PlanningRead(
        request_id="planning-seal", kind="settings", arg=0, src=1, dst=2, cargo=1
    )

    async def attempt():
        async with asyncio.timeout(0.05):
            await freight_delivery.exchange(StalledSession(), request, tmp_path)

    with pytest.raises(TimeoutError) as exc_info:
        asyncio.run(attempt())
    assert type(exc_info.value) is TimeoutError  # not the typed subclass


def test_capture_keeps_exchange_timeout_distinct_from_capture_budget_deadline(tmp_path):
    """An exchange read timeout propagates typed through the capture; only the
    capture's own deadline maps to the CAPTURE_TIME_BUDGET conversion."""
    from app.simulation.openttd.proof.freight_delivery import ExchangeReadTimeout

    backend = SimpleNamespace(health=lambda: None, session=None)
    world = controlled_input().admitted.world

    class StalledExchange:
        async def __call__(self, session, request, directory, response_type):
            raise ExchangeReadTimeout(request.request_id, request.kind, 20, None)

    with pytest.raises(ExchangeReadTimeout):
        asyncio.run(
            capture_planning_facts(
                backend,
                SimpleNamespace(directory=tmp_path),
                world,
                read_exchange=StalledExchange(),
                relationship=(0, 1, 1),
                capture_budget=DemoBudgets(),
            )
        )

    class SlowExchange:
        async def __call__(self, session, request, directory, response_type):
            await asyncio.sleep(0.01)
            return None

    budget = DemoBudgets().model_copy(update=dict(capture_seconds=0.0))
    with pytest.raises(ValueError, match="CAPTURE_TIME_BUDGET") as exc_info:
        asyncio.run(
            capture_planning_facts(
                backend,
                SimpleNamespace(directory=tmp_path),
                world,
                read_exchange=SlowExchange(),
                relationship=(0, 1, 1),
                capture_budget=budget,
            )
        )
    assert exc_info.value.__cause__.__class__ is TimeoutError
