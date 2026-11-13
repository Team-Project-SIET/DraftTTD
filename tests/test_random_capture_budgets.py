"""Offline budget sealing and legacy package correspondence; native is prohibited."""

import asyncio
import json
import zipfile
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
from test_demo_random_native import prohibit_native  # noqa: F401
from test_random_distance import controlled_input

from app.demo_random import DemoBudgets, RandomWorldSettings
from app.demo_random_native import random_budgets, stage_random
from app.simulation.openttd.freight_runtime_planning import PlanningReadback, capture_planning_facts
from app.simulation.openttd.proof import freight_delivery as native

RUN = Path("artifacts/demos/playable-demo-b84b9bd854a342f1a86e4ba669d8e450")


@pytest.mark.parametrize("relationships", [1, 16])
def test_explicit_and_legacy_request_budgets(relationships):
    new = DemoBudgets(max_relationships=relationships)
    old = DemoBudgets.from_sealed({"max_relationships": relationships})
    assert new.capture_tile_limit == 512 and new.capture_seconds == 45
    assert old.capture_tile_limit == 256
    for budget, expected in [(new, 548 * relationships + 1), (old, 292 * relationships + 1)]:
        assert budget.supplemental_request_limit == expected
        assert random_budgets(budget.model_dump(), 3, {})["supplemental_requests"] == expected
        staged = native.staged_package(
            True, True, True, network_service_limit=3, random_budget=budget.model_dump()
        )
        assert f"planner_requests>={expected}".encode() in staged["network-parent.nut"]


def test_legacy_staging_matches_consumed_frozen_source():
    metadata = json.loads((RUN / "PRELAUNCH.json").read_bytes())
    sealed = metadata["random_budget"]
    assert "capture_tile_limit" not in sealed
    with zipfile.ZipFile(RUN / "frozen-source.zip") as archive:
        source = archive.read("app/demo_random_native.py")
    namespace: dict[str, Any] = {"__name__": "retained_random_native"}
    exec(compile(source, "retained/demo_random_native.py", "exec"), namespace)
    base = native.staged_package(True, True, True, network_service_limit=3)
    assert stage_random(base, sealed) == namespace["stage_random"](base, sealed)


def test_stage_random_refuses_unknown_seam_shape(tmp_path):
    """Anchored seams fail preparation loudly instead of shipping silently rewritten code."""
    base = native.staged_package(True, True, True, network_service_limit=3)
    budget = {"capture_tile_limit": 512, "max_relationships": 16}
    grown = dict(base)
    grown["delivery.nut"] = base["delivery.nut"] + b"/64"  # unexpected extra 64-map seam
    with pytest.raises(ValueError, match="STAGING_SEAM_DRIFT: delivery.nut seam /64"):
        stage_random(grown, budget)
    removed = dict(base)
    removed["network-parent.nut"] = base["network-parent.nut"].replace(b"/64", b"", 1)
    with pytest.raises(ValueError, match=r"seam /64 matched 7 times, expected 8"):
        stage_random(removed, budget)


def test_loop_staging_keeps_the_audited_pre_stage_seam():
    """E145 repro: loop composition must not pre-scale the delivery seam the
    stage's own seam-shape audit anchors on; the scaled run-level floor is
    stamped by the stage itself."""
    budget = DemoBudgets(max_relationships=16)
    base = native.staged_package(True, True, True, network_service_limit=3)
    for name in ("delivery.nut", "main.nut"):
        assert base[name].count(b"drequests>=87") == 1
        assert base[name].count(b"drequests>=174") == 0
    staged = stage_random(base, budget.model_dump(), seam_requests=174)
    for name in ("delivery.nut", "main.nut"):
        assert staged[name].count(b"drequests>=174") == 1
        assert staged[name].count(b"drequests>=87") == 0
    # loop_cycles=1 stamps the same value the retained proven composition writes.
    assert stage_random(base, budget.model_dump(), seam_requests=29 * 3) == stage_random(
        base, budget.model_dump()
    )


def test_staged_package_loop_cycles_stamps_the_scaled_seam():
    """The composition of record with --cycles 2 completes staging and stamps
    the scaled floor; the verify replica recomposes the same bytes."""
    budget = DemoBudgets(max_relationships=16)
    loop = native.staged_package(
        True,
        True,
        True,
        network_service_limit=3,
        random_budget=budget.model_dump(),
        loop_cycles=2,
    )
    expected = stage_random(
        native.staged_package(True, True, True, network_service_limit=3),
        budget.model_dump(),
        seam_requests=174,
    )
    assert loop == expected
    single = native.staged_package(
        True, True, True, network_service_limit=3, random_budget=budget.model_dump()
    )
    assert loop["delivery.nut"] != single["delivery.nut"]
    assert (
        loop["delivery.nut"].replace(b"drequests>=174", b"drequests>=87")
        == (single["delivery.nut"])
    )
    from app.simulation.openttd.proof.freight_delivery import network_budgets

    assert network_budgets(3, random_budget=budget.model_dump(), loop_cycles=2)["requests"] == 174


def command_of_record_budgets():
    return DemoBudgets(
        max_relationships=16,
        capture_tile_limit=2048,
        capture_seconds=120,
        capture_edge_pad=6,
    )


def test_loop_cycles_two_lifecycle_seals_and_stamps(tmp_path):
    """End-to-end offline lifecycle of the command of record at --cycles 2:
    prepare seals the scaled budgets, the staged workspace package carries the
    scaled seam floor exactly once per file, and the preflight recomposition
    of record accepts those bytes (no claim, no process, no native grant)."""
    budget = command_of_record_budgets()
    prepared = native.prepare(
        tmp_path / ("playable-demo-" + "a" * 32),
        demo=True,
        planner=True,
        network=True,
        scenario="high-budget-500k",
        random_world=RandomWorldSettings(seed=2026).model_dump(),
        random_budget=budget.model_dump(),
        loop_cycles=2,
    )
    try:
        native.preflight(prepared)
        metadata = json.loads((prepared.directory / "PRELAUNCH.json").read_bytes())
        assert metadata["loop_cycles"] == 2 and metadata["network_service_limit"] == 3
        sealed = DemoBudgets.from_sealed(metadata["random_budget"])
        assert metadata["budgets"]["requests"] == 29 * 3 * 2 == 174
        assert metadata["budgets"]["mutations"] == 11 * 3 * 2 == 66
        assert (
            metadata["budgets"]["supplemental_requests"]
            == 2 * sealed.supplemental_request_limit
            == 2 * ((2048 + 36) * 16 + 1)
            == 66690
        )
        assert (
            metadata["budgets"]["total_seconds"] == 2400
            and metadata["budgets"]["construction_commands"] == 384
        )
        workspace = prepared.spec.workspace.game / "RoadFreightProof"
        for name in ("delivery.nut", "main.nut"):
            data = (workspace / name).read_bytes()
            assert data.count(b"drequests>=174") == 1
            assert data.count(b"drequests>=87") == 0
        with zipfile.ZipFile(prepared.directory / "frozen-source.zip") as archive:
            frozen_staged = {
                name: archive.read("staged/" + name) for name in ("delivery.nut", "main.nut")
            }
        for name, data in frozen_staged.items():
            assert data == (workspace / name).read_bytes()
        assert not (prepared.directory / "CLAIM.json").exists()
    finally:
        prepared.spec.workspace.close()


def test_loop_cycles_one_lifecycle_keeps_legacy_bytes(tmp_path):
    """The single-cycle lifecycle stays byte-identical to the retained proven
    composition: same seam floor, same frozen staged bytes, same preflight."""
    from app.simulation.openttd.proof.freight_delivery import network_budgets

    single = DemoBudgets(max_relationships=16)
    prepared = native.prepare(
        tmp_path / ("playable-demo-" + "b" * 32),
        demo=True,
        planner=True,
        network=True,
        scenario="high-budget-500k",
        random_world=RandomWorldSettings(seed=2026).model_dump(),
        random_budget=single.model_dump(),
        loop_cycles=1,
    )
    try:
        native.preflight(prepared)
        metadata = json.loads((prepared.directory / "PRELAUNCH.json").read_bytes())
        assert metadata["budgets"] == network_budgets(
            3, random_budget=single.model_dump(), loop_cycles=1
        )
        base = native.staged_package(True, True, True, "high-budget-500k", network_service_limit=3)
        proven = stage_random(base, single.model_dump())
        workspace = prepared.spec.workspace.game / "RoadFreightProof"
        for name, data in proven.items():
            assert (workspace / name).read_bytes() == data
        with zipfile.ZipFile(prepared.directory / "frozen-source.zip") as archive:
            staged = archive.read("staged/delivery.nut")
        assert staged.count(b"drequests>=87") == 1
        assert staged.count(b"drequests>=174") == 0
    finally:
        prepared.spec.workspace.close()


def test_stage_seam_contract_cannot_drift_silently(monkeypatch):
    """The floor handed to the audited stage must be exactly the sealed scaled
    budget of the attempt, for every loop_cycles; a composition that scales
    anywhere else fails this contract instead of shipping different bytes."""
    import app.demo_random_native as random_native

    budget = command_of_record_budgets()
    captured = []
    real = random_native.stage_random

    def spy(out, budgets, **kwargs):
        captured.append(kwargs.get("seam_requests"))
        return real(out, budgets, **kwargs)

    monkeypatch.setattr(random_native, "stage_random", spy)
    for loop_cycles, expected in ((1, 87), (2, 174), (8, 696)):
        native.staged_package(
            True,
            True,
            True,
            network_service_limit=3,
            random_budget=budget.model_dump(),
            loop_cycles=loop_cycles,
        )
    assert captured == [87, 174, 696]


def test_pre_stage_seam_boundaries_for_profiles_and_cycles():
    """Legacy non-random profiles keep their own proven seams, and the
    audited pre-stage shape holds for every cycle depth."""
    two_service = native.staged_package(True, True, True, network_service_limit=2)
    assert two_service["delivery.nut"].count(b"drequests>=58") == 1
    assert two_service["delivery.nut"].count(b"drequests>=87") == 0
    assert two_service["main.nut"].count(b"drequests>=58") == 1
    base = native.staged_package(True, True, True, network_service_limit=3)
    assert base["delivery.nut"].count(b"drequests>=87") == 1
    budget = command_of_record_budgets().model_dump()
    for loop_cycles, floor in ((2, 174), (8, 696)):
        staged = stage_random(base, budget, seam_requests=floor)
        for name in ("delivery.nut", "main.nut"):
            assert staged[name].count(f"drequests>={floor}".encode()) == 1
            assert staged[name].count(b"drequests>=87") == 0


def test_prepare_preflight_seals_explicit_capture_limits(tmp_path):
    budgets = DemoBudgets(max_relationships=2, capture_seconds=7)
    prepared = native.prepare(
        tmp_path / ("playable-demo-" + "d" * 32),
        demo=True,
        planner=True,
        network=True,
        scenario="high-budget-500k",
        random_world=RandomWorldSettings(seed=17).model_dump(),
        random_budget=budgets.model_dump(),
    )
    try:
        native.preflight(prepared)
        metadata = json.loads((prepared.directory / "PRELAUNCH.json").read_bytes())
        assert metadata["random_budget"]["capture_tile_limit"] == 512
        assert metadata["random_budget"]["capture_seconds"] == 7
        assert metadata["budgets"]["supplemental_requests"] == 1097
        assert not (prepared.directory / "CLAIM.json").exists()
    finally:
        prepared.spec.workspace.close()


def test_capture_timeout_is_explicit_without_connection(tmp_path):
    value = controlled_input()
    calls = []

    async def timeout(session, request, directory, response_type):
        calls.append(request.kind)
        raise TimeoutError("controlled deadline expiry")

    backend = SimpleNamespace(health=lambda: None, session=object())
    with pytest.raises(ValueError, match="CAPTURE_TIME_BUDGET"):
        asyncio.run(
            capture_planning_facts(
                backend,
                SimpleNamespace(directory=tmp_path),
                value.admitted.world,
                read_exchange=timeout,
                retain=False,
                relationship=(0, 1, 1),
                capture_budget=DemoBudgets(),
            )
        )
    assert calls == ["settings"]
    assert backend.planning_read_attempts == 1
    assert backend.planning_read_count == 0


def test_planning_reply_packet_and_tile_shape_bounds_unchanged():
    from app.simulation.openttd.freight_runtime_planning import PlanningRead

    request = PlanningRead(request_id="bound", kind="tile", arg=0, src=0, dst=1, cargo=1)
    payload = request.model_dump() | dict(type="planning_read_result", before=1, after=1)
    for size in (18, 20):
        with pytest.raises(ValueError, match="shape mismatch"):
            PlanningReadback.parse_for(
                request, json.dumps(payload | dict(data=[0] * size)).encode()
            )
    raw = json.dumps(payload | dict(data=[0] * 19)).encode()
    assert len(PlanningReadback.parse_for(request, raw).data) == 19
    with pytest.raises(ValueError, match="exceeds 512 bytes"):
        PlanningReadback.parse_for(request, raw + b" " * 513)
