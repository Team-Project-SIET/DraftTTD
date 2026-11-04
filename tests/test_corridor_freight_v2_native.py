"""Controlled offline tests for the D5 native protocol-8 freight staging contract.

No OpenTTD launch, no AdminPort connection, no native mutation, and no claim on
any retained artifact: staging, the pinned A1 prerequisite binding, the sealed
freight pins, the thirty-exchange protocol-8 schedule, budgets, authorization
payload reuse, preflight gates, freeze drift and the never-consumed fail-closed
verdicts are exercised against explicitly controlled evidence directories
only.

The pinned retained A1 corridor-extension and depot-mutation/reload chain
candidates (whose receipt-bound saves carry the freight world of record) are
read, never written. Their distinct diagnostic saves are never an acceptable
substitute. The prerequisite replays re-verify the retained authorizations
under the real pinned operator anchor, so these tests substitute no synthetic
identity anywhere.
"""

import asyncio
import contextlib
import hashlib
import json
import shutil
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

import app.simulation.openttd.proof.corridor_freight_v2_native as d5v2
from app.simulation.openttd.admin_protocol import encode_admin_frame
from app.simulation.openttd.corridor_freight_v2 import (
    A1_AFTER_SAVE_SHA256_V2,
    A1_DELIVERY_FRONT_TILE_V2,
    A1_DELIVERY_STOP_TILE_V2,
    A1_DEPOT_FRONT_TILE_V2,
    A1_DEPOT_TILE_V2,
    A1_PICKUP_FRONT_TILE_V2,
    A1_PICKUP_STOP_TILE_V2,
    ENGINE_CENSUS_V2,
    ENGINE_PIN_V2,
    FREIGHT_ATTEMPT_V2,
    FREIGHT_CYCLE_DAY_CAP_V2,
    FREIGHT_DAY_BUDGET_V2,
    FREIGHT_EXCHANGE_IDS_V2,
    FREIGHT_MAX_COST_V2,
    FREIGHT_REQUEST_BUDGET_V2,
    FREIGHT_ROUTE_LENGTH_V2,
    FREIGHT_ROUTE_V2,
    FREIGHT_SCHEDULE_VERSION,
    FREIGHT_STALE_BACKTRACK_TILE_V2,
    FREIGHT_STALE_DELIVERY_TILE_V2,
    FREIGHT_WITNESS_LENGTH_V2,
    FUNDS_AT_A1_CLOSE,
    FUNDS_AT_DEPOT_MUTATION_CLOSE,
    MAX_FREIGHT_REQUEST_BYTES_V2,
    MAX_FREIGHT_RESPONSE_BYTES_V2,
    MAX_FREIGHT_SEND_BYTES,
    PINNED_WITNESS,
    PLANNED_FREIGHT_CYCLES_V2,
    PLANNED_FREIGHT_EXCHANGES_V2,
    WATCH_MAX_TICKS_V2,
    FreightReadbackV2,
    FreightRequestV2,
    FreightStatusV2,
)
from app.simulation.openttd.gamescript_transport import (
    MAX_GAMESCRIPT_PAYLOAD_BYTES,
    decode_gamescript,
    encode_gamescript,
    gamescript_subscription,
)
from app.simulation.openttd.observation_protocol import MAX_PAYLOAD_BYTES
from app.simulation.openttd.proof.corridor_freight_native import (
    staged_authorization_payload_digest,
)
from app.simulation.openttd.proof.harness import sha256
from app.simulation.openttd.proof.operator_authorization import (
    authorization_payload,
    canonical_authorization_bytes,
)
from app.simulation.openttd.proof.terrain_clearing import (
    claim_status,
    retained_welcome,
)
from app.simulation.openttd.proof.world_correspondence import SOURCE_SAVE_GS_NAME

ENGINE_QUOTE_V2 = ENGINE_CENSUS_V2["price"]
SEAL = "a" * 64
VEHICLE = 1
LOADS: tuple[int, ...] = (20, 19, 18, 17, 16, 15)
INCOME_PER_CYCLE = 1080
DELIVERED_PER_CYCLE = 20


@pytest.fixture(scope="module")
def staged(tmp_path_factory):
    prepared = d5v2.prepare_candidate(tmp_path_factory.mktemp("d5v2-staging") / "candidate")
    yield prepared
    prepared.spec.workspace.close()


def metadata_of(prepared) -> dict:
    return json.loads((prepared.directory / "PRELAUNCH.json").read_text())


def _restamp_prelaunch(directory: Path) -> None:
    (directory / "PRELAUNCH.sha256").write_text(sha256(directory / "PRELAUNCH.json") + "\n")


def _add_freeze_probe(directory: Path, source: Path) -> Path:
    """Alias one extra frozen entry to a byte-identical in-candidate copy."""
    metadata = json.loads((directory / "PRELAUNCH.json").read_text())
    probe = directory / "freeze-probe" / source.name
    probe.parent.mkdir(exist_ok=True)
    probe.write_bytes(source.read_bytes())
    metadata["frozen"][str(probe.resolve())] = sha256(source)
    (directory / "PRELAUNCH.json").write_text(json.dumps(metadata, sort_keys=True, indent=2) + "\n")
    _restamp_prelaunch(directory)
    return probe


def _snapshot(root: Path) -> dict[str, str]:
    return {
        str(path.relative_to(root)): sha256(path)
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


# --- staging correctness and the pinned prerequisite lineage -----------------


def test_prerequisite_binding_is_pinned_and_read_only():
    """The depot-mutation world-of-record chain re-verifies without being touched."""
    before = _snapshot(d5v2.DEPOT_PREREQUISITE)
    before_a1 = _snapshot(d5v2.PINNED_PREREQUISITE)
    before_reload = _snapshot(d5v2.RELOAD_PREREQUISITE)
    binding = d5v2.prerequisite_binding()
    assert _snapshot(d5v2.DEPOT_PREREQUISITE) == before
    assert _snapshot(d5v2.PINNED_PREREQUISITE) == before_a1
    assert _snapshot(d5v2.RELOAD_PREREQUISITE) == before_reload
    assert sha256(d5v2.DEPOT_PREREQUISITE / "after.sav") == d5v2.DEPOT_PREREQUISITE_AFTER_SAVE
    assert binding == {
        "schema": d5v2.D5_FREIGHT_V2_PREREQUISITE_SCHEMA,
        "role": "PREREQUISITE_ATTEMPT",
        "world_pin_version": 3,
        "retained_directory": str(d5v2.DEPOT_PREREQUISITE),
        "save": "after.sav",
        "save_sha256": d5v2.DEPOT_PREREQUISITE_AFTER_SAVE,
        "qualified_save_sha256": None,
        "prelaunch_digest": sha256(d5v2.DEPOT_PREREQUISITE / "PRELAUNCH.json"),
        "attempt": d5v2.depot_native.DEPOT_MUTATION_ATTEMPT,
        "milestone": d5v2.depot_native.MILESTONE_DEPOT_MUTATION,
        "funds_of_record": FUNDS_AT_DEPOT_MUTATION_CLOSE,
        "expected_welcome": retained_welcome(),
        "verification": binding["verification"],
        "provenance": binding["provenance"],
    }
    assert (
        binding["provenance"]["a1_extension_lineage"]["after_save_sha256"]
        == d5v2.PINNED_PREREQUISITE_AFTER_SAVE
        == A1_AFTER_SAVE_SHA256_V2
    )
    assert (
        binding["provenance"]["a1_extension_lineage"]["replay"] == "EXTENSION_COMPLETION_VERIFIED"
    )
    assert binding["provenance"]["depot_mutation_chain"]["replay"] == (
        "F12_MUTATION_COMPLETION_VERIFIED"
    )
    assert binding["provenance"]["reload_chain"]["loaded_source_sha256"] == (
        d5v2.DEPOT_PREREQUISITE_AFTER_SAVE
    )
    assert binding["provenance"]["reload_chain"]["replay"] == "DEPOT_RELOAD_FACTS_VERIFIED"


def test_staged_candidate_binds_the_pinned_world_of_record(staged):
    metadata = metadata_of(staged)
    assert metadata["schema"] == d5v2.D5_FREIGHT_V2_PRELAUNCH_SCHEMA
    assert metadata["milestone"] == d5v2.MILESTONE_FREIGHT
    assert metadata["kind"] == d5v2.KIND
    assert metadata["attempt"] == d5v2.FREIGHT_ATTEMPT_V2 == FREIGHT_ATTEMPT_V2
    save_digest = sha256(d5v2.DEPOT_PREREQUISITE / "after.sav")
    assert save_digest == d5v2.DEPOT_PREREQUISITE_AFTER_SAVE
    prerequisite = metadata["prerequisite"]
    assert prerequisite == {
        "schema": d5v2.D5_FREIGHT_V2_PREREQUISITE_SCHEMA,
        "attempt": d5v2.depot_native.DEPOT_MUTATION_ATTEMPT,
        "milestone": d5v2.depot_native.MILESTONE_DEPOT_MUTATION,
        "directory": str(d5v2.DEPOT_PREREQUISITE),
        "prelaunch_sha256": sha256(d5v2.DEPOT_PREREQUISITE / "PRELAUNCH.json"),
        "after_save_sha256": save_digest,
        "verification": prerequisite["verification"],
    }
    assert prerequisite["prelaunch_sha256"] == sha256(
        d5v2.DEPOT_PREREQUISITE / "PRELAUNCH.json"
    )
    assert (
        metadata["prerequisite_provenance"]["a1_extension_lineage"]["prelaunch_sha256"]
        == sha256(d5v2.PINNED_PREREQUISITE / "PRELAUNCH.json")
    )
    assert metadata["prerequisite_provenance"]["reload_chain"]["loaded_source_sha256"] == (
        save_digest
    )
    assert (
        metadata["prerequisite_provenance"]["a1_extension_lineage"]["replay"]
        == "EXTENSION_COMPLETION_VERIFIED"
    )
    assert metadata["authorization"].startswith("PENDING")
    assert "no authorization file exists" in metadata["authorization"]
    assert claim_status(staged.directory) == "ABSENT"
    assert not (staged.directory / "CLAIM.json").exists()


def test_staging_refuses_any_unpinned_prerequisite(tmp_path):
    unrelated = tmp_path / "unrelated"
    unrelated.mkdir()
    with pytest.raises(d5v2.FreightV2StagingError, match="pinned depot"):
        d5v2.prepare_candidate(tmp_path / "candidate", prerequisite=unrelated)
    with pytest.raises(d5v2.FreightV2StagingError, match="pinned depot"):
        d5v2.prerequisite_binding(unrelated)
    assert not (tmp_path / "candidate").exists()


def test_staged_composition_carries_the_retained_save_identity(staged):
    composition, bridge, version = d5v2.staged_composition()
    gs = staged.spec.workspace.root / "game" / SOURCE_SAVE_GS_NAME
    assert gs.joinpath("info.nut").read_bytes() == composition["info.nut"]
    assert gs.joinpath("main.nut").read_bytes() == composition["main.nut"]
    assert bridge == "NetworkFreightProof" and version == 1
    main_text = gs.joinpath("main.nut").read_text()
    assert "class NetworkFreightProof extends D5FreightV2Proof" in main_text
    ai = staged.spec.workspace.root / "ai" / d5v2.STAGED_AI_DIRECTORY
    for name in ("info.nut", "main.nut"):
        assert sha256(ai / name) == sha256(d5v2.AI_PACKAGE / name)
    assert metadata_of(staged)["game_script_identity"]["create_instance"] == bridge


def test_staged_source_save_is_the_pinned_verified_after_world(staged):
    root = staged.spec.workspace.root
    assert sha256(root / "source.sav") == d5v2.DEPOT_PREREQUISITE_AFTER_SAVE
    assert sha256(root / "source.sav") == sha256(d5v2.DEPOT_PREREQUISITE / "after.sav")
    assert sha256(d5v2.PINNED_PREREQUISITE / "after.sav") == d5v2.PINNED_PREREQUISITE_AFTER_SAVE
    world = metadata_of(staged)["world"]
    assert world["mode"] == "PREREQUISITE_ATTEMPT_SOURCE_SAVE_LOAD"
    assert world["retained_directory"] == str(d5v2.DEPOT_PREREQUISITE)
    assert world["source_save"] == "after.sav"
    assert world["save_sha256"] == d5v2.DEPOT_PREREQUISITE_AFTER_SAVE
    assert world["qualified_save_sha256"] is None
    assert world["expected_welcome"] == retained_welcome()
    config = root.joinpath("openttd.cfg").read_text()
    assert "[game_creation]" not in config
    assert f"[game_scripts]\n{SOURCE_SAVE_GS_NAME} = \n" in config
    assert "ai_in_multiplayer = true" in config


def test_preflight_rehearsal_conserves_the_sealed_candidate(staged):
    prior = sha256(staged.directory / "PRELAUNCH.json")
    metadata = d5v2.preflight(staged)
    assert sha256(staged.directory / "PRELAUNCH.json") == prior
    assert metadata["attempt"] == d5v2.FREIGHT_ATTEMPT_V2
    assert not (staged.directory / "CLAIM.json").exists()
    assert claim_status(staged.directory) == "ABSENT"


# --- preflight refusal gates --------------------------------------------------


def test_tampered_workspace_config_refuses_v2_preflight(tmp_path):
    prepared = d5v2.prepare_candidate(tmp_path / "candidate")
    try:
        config = prepared.spec.workspace.config
        config.write_text(config.read_text() + "# tampered\n")
        with pytest.raises(ValueError):
            d5v2.preflight(prepared)
    finally:
        prepared.spec.workspace.close()


def test_drifted_source_save_refuses_v2_preflight(tmp_path):
    prepared = d5v2.prepare_candidate(tmp_path / "candidate")
    try:
        (prepared.spec.workspace.root / "source.sav").write_bytes(b"tampered world bytes")
        with pytest.raises(ValueError):
            d5v2.preflight(prepared)
    finally:
        prepared.spec.workspace.close()


def test_frozen_source_drift_refuses_v2_preflight(tmp_path):
    """Post-preparation frozen drift of the v2 module itself refuses preflight."""
    prepared = d5v2.prepare_candidate(tmp_path / "candidate")
    try:
        probe = _add_freeze_probe(prepared.directory, Path(d5v2.__file__))
        probe.write_bytes(probe.read_bytes() + b"\n# modified after preparation\n")
        with pytest.raises(ValueError, match="Frozen source"):
            d5v2.preflight(prepared)
        assert not (prepared.directory / "CLAIM.json").exists()
    finally:
        prepared.spec.workspace.close()


def test_removed_closure_entry_refuses_v2_preflight(tmp_path):
    prepared = d5v2.prepare_candidate(tmp_path / "candidate")
    try:
        target = str(Path(d5v2.__file__).resolve())
        metadata = json.loads((prepared.directory / "PRELAUNCH.json").read_text())
        assert target in metadata["frozen"]
        del metadata["frozen"][target]
        (prepared.directory / "PRELAUNCH.json").write_text(
            json.dumps(metadata, sort_keys=True, indent=2) + "\n"
        )
        _restamp_prelaunch(prepared.directory)
        with pytest.raises(ValueError, match="closure is not frozen"):
            d5v2.preflight(prepared)
        assert not (prepared.directory / "CLAIM.json").exists()
    finally:
        prepared.spec.workspace.close()


def test_drifted_schedule_pin_refuses_v2_preflight(tmp_path):
    prepared = d5v2.prepare_candidate(tmp_path / "candidate")
    try:
        metadata = json.loads((prepared.directory / "PRELAUNCH.json").read_text())
        metadata["plan_policy"]["schedule"][-1]["exchange"] = "finish-99"
        (prepared.directory / "PRELAUNCH.json").write_text(
            json.dumps(metadata, sort_keys=True, indent=2) + "\n"
        )
        _restamp_prelaunch(prepared.directory)
        with pytest.raises(ValueError, match="schedule drifted"):
            d5v2.preflight(prepared)
        assert not (prepared.directory / "CLAIM.json").exists()
    finally:
        prepared.spec.workspace.close()


def test_seal_and_claim_gates_refuse_drifted_or_drafted_launch_boundaries(tmp_path):
    """The outermost preflight gates: a drifted seal and any existing claim."""
    prepared = d5v2.prepare_candidate(tmp_path / "candidate")
    try:
        directory = prepared.directory
        prelaunch = directory / "PRELAUNCH.json"
        original = prelaunch.read_bytes()
        prelaunch.write_bytes(original + b"\n# drifted after staging\n")
        with pytest.raises(ValueError, match="prelaunch seal mismatch"):
            d5v2.preflight(prepared)
        prelaunch.write_bytes(original)
        (directory / "CLAIM.json").write_text("{}\n")
        with pytest.raises(ValueError, match="one native attempt already consumed"):
            d5v2.preflight(prepared)
        (directory / "CLAIM.json").unlink()
        # The restored candidate returns to the passing gate, boundary intact.
        d5v2.preflight(prepared)
    finally:
        prepared.spec.workspace.close()


def test_preflight_rejects_resealed_execution_pin_drift(tmp_path):
    """Every execution-relevant pin is bound, even after a valid re-seal.

    A re-sealed PRELAUNCH record must not be able to swap the world geometry,
    the route provenance, the engine census pin, the plan model identity,
    funds or the schedule derivation. Each mutation below is individually
    restored before the next.
    """
    prepared = d5v2.prepare_candidate(tmp_path / "candidate")
    directory = prepared.directory
    prelaunch = directory / "PRELAUNCH.json"
    original = prelaunch.read_bytes()

    def swap(section, key, value):
        def mutate(metadata):
            metadata[section][key] = value

        return mutate

    def swap_world(key, value):
        def mutate(metadata):
            metadata["plan_policy"]["world"][key] = value

        return mutate

    def swap_engine(key, value):
        def mutate(metadata):
            metadata["plan_policy"]["engine"][key] = value

        return mutate

    def swap_witness(metadata):
        metadata["plan_policy"]["world"]["witness"][4] = 12345

    def swap_route(metadata):
        metadata["plan_policy"]["world"]["vehicle_route"][4] = 12345

    def swap_provenance_witness(metadata):
        metadata["plan_policy"]["route_provenance"]["witness"][4] = 12345

    def swap_provenance_route(metadata):
        metadata["plan_policy"]["route_provenance"]["route"][4] = 12345

    def swap_provenance(key, value):
        def mutate(metadata):
            metadata["plan_policy"]["route_provenance"][key] = value

        return mutate

    mutations = (
        ("world pickup", swap_world("pickup", 45749), "world pin pickup"),
        (
            "world delivery front",
            swap_world("delivery_front", 50094),
            "world pin delivery_front",
        ),
        ("world depot", swap_world("depot", 45488), "world pin depot"),
        ("world witness", swap_witness, "world pin witness"),
        (
            "world vehicle route",
            swap_route,
            "world pin vehicle_route",
        ),
        ("world engine", swap_world("engine", 124), "world pin engine"),
        ("world funds", swap_world("expected_funds", 1), "world pin expected_funds"),
        ("world cycles", swap_world("cycles", 7), "world pin cycles"),
        (
            "world watch ticks",
            swap_world("watch_ticks", 1024),
            "world pin watch_ticks",
        ),
        (
            "engine pin provisional",
            swap_engine("provisional", False),
            "engine pin provisional",
        ),
        ("engine pin price", swap_engine("price", 1), "engine pin price"),
        (
            "engine pin capacity",
            swap_engine("capacity", 99),
            "engine pin capacity",
        ),
        (
            "engine pin max_speed",
            swap_engine("max_speed", 7),
            "engine pin max_speed",
        ),
        (
            "route provenance witness",
            swap_provenance_witness,
            "route provenance pin witness",
        ),
        (
            "route provenance route",
            swap_provenance_route,
            "route provenance pin route",
        ),
        (
            "route provenance route digest",
            swap_provenance("route_digest", "b" * 64),
            "route provenance pin route_digest",
        ),
        (
            "route provenance digest",
            swap_provenance("witness_digest", "c" * 64),
            "route provenance pin witness_digest",
        ),
        (
            "plan model digest",
            swap("plan_policy", "plan_model_digest", "c" * 64),
            "plan pin plan_model_digest",
        ),
        (
            "plan target tile",
            swap("plan_policy", "target_tile", 45749),
            "plan pin target_tile",
        ),
        ("plan max cost", swap("plan_policy", "max_cost", 1999), "plan pin max_cost"),
        (
            "schedule version",
            swap("plan_policy", "schedule_version", 3),
            "staged schedule derivation drifted",
        ),
        (
            "budget funds",
            swap("budgets", "expected_funds", 1),
            "budget pins drifted",
        ),
    )
    try:
        for label, mutate, message in mutations:
            metadata = json.loads(original)
            mutate(metadata)
            prelaunch.write_text(json.dumps(metadata, sort_keys=True, indent=2) + "\n")
            _restamp_prelaunch(directory)
            try:
                d5v2.preflight(prepared)
            except ValueError as error:
                assert message in str(error), (label, str(error))
            else:
                raise AssertionError(f"{label} did not refuse preflight")
        prelaunch.write_bytes(original)
        _restamp_prelaunch(directory)
        assert d5v2.preflight(prepared)["attempt"] == d5v2.FREIGHT_ATTEMPT_V2
    finally:
        prepared.spec.workspace.close()


def test_preflight_rejects_a_staged_world_that_is_not_the_pinned_after_save(tmp_path):
    """A re-sealed world digest must equal the independent prerequisite binding."""
    prepared = d5v2.prepare_candidate(tmp_path / "candidate")
    directory = prepared.directory
    try:
        prelaunch = directory / "PRELAUNCH.json"
        original = prelaunch.read_bytes()
        metadata = json.loads(original)
        metadata["world"]["save_sha256"] = "0" * 64
        prelaunch.write_text(json.dumps(metadata, sort_keys=True, indent=2) + "\n")
        _restamp_prelaunch(directory)
        with pytest.raises(ValueError, match="pinned depot-mutation after-save"):
            d5v2.preflight(prepared)
        prelaunch.write_bytes(original)
        _restamp_prelaunch(directory)
        assert d5v2.preflight(prepared)["attempt"] == d5v2.FREIGHT_ATTEMPT_V2
    finally:
        prepared.spec.workspace.close()


# --- sealed freight facts, schedule, budgets and route scope -----------------


def test_freight_facts_bind_the_world_of_record_chain():
    facts = d5v2.freight_facts()
    assert facts["world_pin_version"] == 3
    assert facts["attempt"] == d5v2.depot_native.DEPOT_MUTATION_ATTEMPT
    assert facts["milestone"] == d5v2.depot_native.MILESTONE_DEPOT_MUTATION
    assert facts["save"] == "after.sav"
    assert facts["save_sha256"] == d5v2.DEPOT_PREREQUISITE_AFTER_SAVE
    assert facts["qualified_save_sha256"] is None
    assert facts["funds"] == FUNDS_AT_DEPOT_MUTATION_CLOSE == 489650
    assert facts["station_sids"] == {"existing": [0, 1], "new": 2}
    assert facts["expected_welcome"] == retained_welcome()
    assert facts["depot_mutation"]["verification"] == "F12_MUTATION_COMPLETION_VERIFIED"
    assert facts["depot_mutation"]["funds_at_close"] == 489650
    assert facts["depot_mutation"]["after_save_sha256"] == facts["save_sha256"]
    assert facts["reload"]["attempt"] == d5v2.depot_recheck_native.RECHECK_ATTEMPT
    assert facts["reload"]["loaded_source_sha256"] == facts["save_sha256"]
    assert facts["reload"]["verification"] == "DEPOT_RELOAD_FACTS_VERIFIED"
    assert facts["a1_lineage"]["attempt"] == d5v2.A1_PREREQUISITE_ATTEMPT
    assert facts["a1_lineage"]["save_sha256"] == d5v2.PINNED_PREREQUISITE_AFTER_SAVE
    assert facts["a1_lineage"]["save_sha256"] == A1_AFTER_SAVE_SHA256_V2
    assert facts["a1_lineage"]["funds_at_close"] == FUNDS_AT_A1_CLOSE == 490257


def test_freight_schedule_is_the_fixed_thirty_exchange_cycle():
    schedule = d5v2.freight_schedule()
    assert [entry["exchange"] for entry in schedule] == list(FREIGHT_EXCHANGE_IDS_V2)
    assert len(schedule) == PLANNED_FREIGHT_EXCHANGES_V2 == 30
    assert len({entry["exchange"] for entry in schedule}) == 30
    prelude = [
        ("site-00", "site"),
        ("engine-00", "engine"),
        ("purchase-00", "purchase"),
        ("vread-00", "vread"),
        ("order-00", "order"),
        ("order-01", "order"),
        ("order-read-00", "order-read"),
        ("monitor-00", "monitor"),
        ("start-00", "start"),
        ("vread-01", "vread"),
    ]
    expected = [*prelude]
    for cycle in range(PLANNED_FREIGHT_CYCLES_V2):
        expected.append((f"load-{cycle:02d}", "load-watch"))
        expected.append((f"transit-{cycle:02d}", "transit-watch"))
        expected.append((f"deliver-{cycle:02d}", "deliver-watch"))
    expected.extend([("finance-00", "finance"), ("finish-00", "finish")])
    assert [(entry["exchange"], entry["op"]) for entry in schedule] == expected
    assert schedule[4]["order_index"] == 0 and schedule[5]["order_index"] == 1
    for cycle in range(PLANNED_FREIGHT_CYCLES_V2):
        load_row = schedule[10 + 3 * cycle]
        assert load_row["watch_ticks"] == WATCH_MAX_TICKS_V2
        assert load_row["watch_days"] == FREIGHT_CYCLE_DAY_CAP_V2 == 10
        transit_row = schedule[10 + 3 * cycle + 1]
        assert transit_row["watch_ticks"] == WATCH_MAX_TICKS_V2
        assert transit_row["watch_days"] == FREIGHT_CYCLE_DAY_CAP_V2 == 10
        assert d5v2.freight_exchange_cycle_index_v2(transit_row["exchange"]) == cycle
    assert d5v2._scheduled_exchange_ids(schedule) == set(FREIGHT_EXCHANGE_IDS_V2)


def test_freight_plan_rebinds_the_compiled_pins():
    plan = d5v2.freight_plan_v2()
    assert plan.company == 0
    assert plan.cargo == 1
    assert plan.engine == ENGINE_PIN_V2 == 123
    assert (plan.pickup, plan.pickup_front) == (
        A1_PICKUP_STOP_TILE_V2,
        A1_PICKUP_FRONT_TILE_V2,
    ) == (45748, 45747)
    assert (plan.delivery, plan.delivery_front) == (
        A1_DELIVERY_STOP_TILE_V2,
        A1_DELIVERY_FRONT_TILE_V2,
    ) == (50862, 50863)
    assert (plan.depot, plan.depot_front) == (A1_DEPOT_TILE_V2, A1_DEPOT_FRONT_TILE_V2) == (
        45487,
        45743,
    )
    assert (plan.pickup_industry, plan.delivery_industry) == (-1, -1)
    assert plan.expected_funds == FUNDS_AT_DEPOT_MUTATION_CLOSE == 489650
    assert plan.max_cost == FREIGHT_MAX_COST_V2 == 5000
    assert plan.witness == PINNED_WITNESS
    assert len(plan.witness) == FREIGHT_WITNESS_LENGTH_V2 == 31
    assert (plan.witness[23], plan.witness[24]) == (
        FREIGHT_STALE_DELIVERY_TILE_V2,
        FREIGHT_STALE_BACKTRACK_TILE_V2,
    ) == (50351, 50095)
    assert plan.vehicle_route == FREIGHT_ROUTE_V2
    assert len(plan.vehicle_route) == FREIGHT_ROUTE_LENGTH_V2 == 29
    assert plan.vehicle_route[0] == plan.pickup
    assert plan.vehicle_route[1] == plan.pickup_front
    assert plan.vehicle_route[-1] == plan.delivery
    assert FREIGHT_STALE_DELIVERY_TILE_V2 not in plan.vehicle_route
    assert plan.vehicle_route.count(FREIGHT_STALE_BACKTRACK_TILE_V2) == 1
    assert plan.schedule == FREIGHT_EXCHANGE_IDS_V2
    assert plan.cycles == PLANNED_FREIGHT_CYCLES_V2 == 6
    assert plan.day_budget == FREIGHT_DAY_BUDGET_V2 == 60
    assert plan.cycle_day_cap == FREIGHT_CYCLE_DAY_CAP_V2 == 10
    assert plan.request_budget == FREIGHT_REQUEST_BUDGET_V2 == 32
    assert len(plan.digest) == 64
    assert len(plan.route_digest) == len(plan.witness_digest) == 64
    assert plan.route_digest != plan.witness_digest


def test_plan_policy_binds_schedule_world_and_wire_identity():
    plan_policy = d5v2.plan_policy()
    schedule = d5v2.freight_schedule()
    plan = d5v2.freight_plan_v2()
    assert plan_policy["company"] == 0
    assert plan_policy["target_tile"] == 45748
    assert plan_policy["max_cost"] == FREIGHT_MAX_COST_V2
    assert plan_policy["command"] == (
        "GSVehicle.BuildVehicle + GSOrder.AppendOrder + GSVehicle.StartStopVehicle"
    )
    assert "re-observe every pin" in plan_policy["stale_rule"]
    assert "wire contract v8" in plan_policy["identity"]
    assert plan_policy["schedule"] == schedule
    assert plan_policy["plan_digest"] == d5v2.plan_digest_of(schedule)
    assert plan_policy["plan_model_digest"] == plan.digest
    assert plan_policy["schedule_version"] == FREIGHT_SCHEDULE_VERSION == 2
    engine = plan_policy["engine"]
    assert engine["pin"] == ENGINE_PIN_V2 == 123
    assert engine["provisional"] == d5v2.ENGINE_PIN_PROVISIONAL_V2
    assert engine["capacity"] == ENGINE_CENSUS_V2["capacity"] == 20
    assert engine["cargo"] == ENGINE_CENSUS_V2["cargo"] == 1
    assert engine["price"] == ENGINE_CENSUS_V2["price"] == 4429
    assert engine["max_speed"] == ENGINE_CENSUS_V2["max_speed"] == 48
    provenance = plan_policy["route_provenance"]
    assert provenance["witness"] == list(plan.witness)
    assert provenance["route"] == list(plan.vehicle_route)
    assert provenance["route_digest"] == plan.route_digest
    assert provenance["witness_digest"] == plan.witness_digest
    assert provenance["removed"] == [
        FREIGHT_STALE_DELIVERY_TILE_V2,
        FREIGHT_STALE_BACKTRACK_TILE_V2,
    ]
    world = plan_policy["world"]
    assert world["witness"] == list(plan.witness)
    assert world["vehicle_route"] == list(plan.vehicle_route)
    assert world["expected_funds"] == FUNDS_AT_DEPOT_MUTATION_CLOSE
    assert world["expected_fleet"] == 0
    assert world["request_budget"] == FREIGHT_REQUEST_BUDGET_V2 == 32
    assert world["watch_ticks"] == WATCH_MAX_TICKS_V2
    assert world["window_day_cap"] == FREIGHT_CYCLE_DAY_CAP_V2
    assert world["running_cost_allowance"] == d5v2.FREIGHT_RUNNING_COST_ALLOWANCE_V2 == 12
    assert (
        plan_policy["prerequisite_world"]["schema"] == d5v2.D5_FREIGHT_V2_PREREQUISITE_SCHEMA
    )
    assert "truck stops" in plan_policy["prerequisite_world"]["statement"]
    assert "D5-F12-DEPOT-3 after-save" in plan_policy["prerequisite_world"]["statement"]


def test_budgets_match_the_staged_contract():
    assert d5v2.budgets() == {
        "launches": 1,
        "connection_attempts": 1,
        "requests": 32,
        "planned_exchanges": 30,
        "planned_cycles": 6,
        "gsadmin_bytes": 1450,
        "response_bytes": 1400,
        "retries": 0,
        "reconnects": 0,
        "readiness_seconds": 45,
        "request_seconds": 10,
        "watch_seconds": 60,
        "exchange_margin_seconds": 5,
        "total_seconds": 900,
        "watch_ticks": 2048,
        "window_day_cap": 10,
        "day_budget": 60,
        "cycle_wall_cap_seconds": d5v2.FREIGHT_CYCLE_WALL_CAP_SECONDS_V2,
        "running_cost_allowance": 12,
        "max_cost": 5000,
        "expected_funds": 489650,
    }
    assert d5v2.PLANNED_FREIGHT_REQUESTS == len(d5v2.freight_schedule()) == 30
    assert d5v2.FREIGHT_STAGED_REQUESTS_BUDGET == FREIGHT_REQUEST_BUDGET_V2 == 32
    assert d5v2.MAX_FREIGHT_SEND_BYTES == MAX_FREIGHT_SEND_BYTES == 1450
    assert d5v2.MAX_FREIGHT_RESPONSE_BYTES_V2 == MAX_FREIGHT_RESPONSE_BYTES_V2 == 1400
    assert d5v2.MAX_FREIGHT_REQUEST_BYTES_V2 == MAX_FREIGHT_REQUEST_BYTES_V2 == 768
    assert "no aggregate phase-spending budget" in (d5v2.budgets.__doc__ or "")


def test_expected_readback_policy_covers_every_phase():
    policy = d5v2.expected_readback_policy()
    assert set(policy) == {
        "admission",
        "engine",
        "purchase",
        "vehicle",
        "orders",
        "drive",
        "finance",
        "finish",
        "receipt",
    }
    assert "zero vehicles" in policy["admission"]
    assert "census price" in policy["engine"]
    assert "funds moving by" in policy["purchase"]
    assert "zero cost" in policy["vehicle"]
    assert "OF_FULL_LOAD is never issued" in policy["orders"]
    assert "partial loads legal" in policy["drive"]
    assert "ZERO_DEPARTED" in policy["drive"]
    assert "zero income and zero delivered deltas" in policy["finance"]
    assert "never sold" in policy["finish"]
    assert "attempt-bound only" in policy["receipt"]


def test_attempt_name_binds_the_v2_scope():
    assert d5v2.attempt_name() == FREIGHT_ATTEMPT_V2 == "D5-FREIGHT-6"


# --- authorization payload, planned exchanges and wire identities -------------


def test_authorization_payload_adds_the_ordered_exchange_scope(staged):
    metadata = metadata_of(staged)
    seal = sha256(staged.directory / "PRELAUNCH.json")
    payload = authorization_payload(metadata, seal)
    schedule = d5v2.freight_schedule()
    assert payload["milestone"] == d5v2.MILESTONE_FREIGHT
    assert payload["attempt"] == d5v2.FREIGHT_ATTEMPT_V2
    assert payload["schema"] == d5v2.D5_FREIGHT_V2_PRELAUNCH_SCHEMA
    assert payload["target_tile"] == 45748
    assert payload["company"] == 0
    assert payload["max_cost"] == FREIGHT_MAX_COST_V2
    assert payload["source_world"]["source_save"] == "after.sav"
    assert payload["source_world"]["save_sha256"] == d5v2.DEPOT_PREREQUISITE_AFTER_SAVE
    assert payload["source_world"]["qualified_save_sha256"] is None
    assert payload["budgets"] == d5v2.budgets()
    assert payload["operation_schedule"] == schedule
    assert payload["plan_digest"] == d5v2.plan_digest_of(schedule)
    digest = hashlib.sha256(canonical_authorization_bytes(payload)).hexdigest()
    assert digest == staged_authorization_payload_digest(staged.directory)


def _production_site_request() -> FreightRequestV2:
    return d5v2._freight_exchange_request(
        d5v2.freight_schedule()[0],
        SEAL,
        d5v2.freight_plan_v2(),
        dict(site=None, engine=None, vehicle=-1),
    )


def test_production_site_request_is_640_bytes_and_passes_outbound_validation():
    """The real v2 site-00 request is accepted by the live protocol-8 path."""
    request = _production_site_request()
    raw = request.to_bytes()
    assert request.request_id == "site-00"
    assert len(raw) == 640
    assert len(raw) <= MAX_FREIGHT_REQUEST_BYTES_V2
    frame = d5v2.encode_freight_request(raw)
    assert frame[2] == d5v2.ADMIN_GAMESCRIPT
    assert len(frame) == len(raw) + 4  # 3-byte Admin header + terminating NUL
    assert len(frame) - 4 <= MAX_GAMESCRIPT_PAYLOAD_BYTES
    assert len(frame) <= MAX_FREIGHT_SEND_BYTES

    session = object.__new__(d5v2.FreightV2SecureSession)
    session._state = d5v2.AuthState.ACTIVE
    session.validate_outbound(frame)
    assert d5v2.decode_freight_request(frame[3:]) == raw
    assert FreightRequestV2.model_validate_json(frame[3:-1]).to_bytes() == raw


def _site_readback(request: FreightRequestV2) -> FreightReadbackV2:
    return FreightReadbackV2(
        protocol=8,
        op="site",
        request_id=request.request_id,
        plan=request.plan,
        company=request.company,
        max_cost=request.max_cost,
        pickup=request.pickup,
        delivery=request.delivery,
        depot=request.depot,
        route_digest=request.route_digest,
        witness_digest=request.witness_digest,
        engine=request.engine,
        vehicle=request.vehicle,
        expected_cost=request.expected_cost,
        order_index=request.order_index,
        watch_ticks=request.watch_ticks,
        watch_days=request.watch_days,
        status="READY",
        funds=FUNDS_AT_DEPOT_MUTATION_CLOSE,
        cost=0,
        paused=False,
        truck0=True,
        sid0=0,
        truck1=True,
        sid1=2,
        depot_ok=True,
        owner=0,
        pairs_ok=len(FREIGHT_ROUTE_V2) - 1,
        pair_total=len(FREIGHT_ROUTE_V2) - 1,
        accept=8,
        prod=100,
        wait=5,
        vehicles=0,
        road_ready=True,
        depot_edge=True,
        pickup_radius=3,
        delivery_radius=3,
        pickup_industry=7,
        pickup_industry_count=1,
        delivery_industry=9,
        delivery_industry_count=1,
        income=0,
    )


def _readback_bytes(readback: FreightReadbackV2) -> bytes:
    return json.dumps(
        readback.model_dump(mode="json", exclude_none=True),
        sort_keys=True,
        separators=(",", ":"),
    ).encode()


class _FakeFreightSession:
    """Records the live wire frame and yields one retained-shaped reply."""

    def __init__(self, reply: bytes) -> None:
        self.sent: list[bytes] = []
        self._reply = reply
        self._read = False

    async def send(self, frame: bytes) -> None:
        self.sent.append(frame)

    async def receive(self) -> bytes:
        if self._read:
            return b""
        self._read = True
        return self._reply


def test_live_exchange_sends_the_site_request_under_the_named_bound(tmp_path):
    """The production exchange() sends the site request and parses its reply."""
    request = _production_site_request()
    raw = request.to_bytes()
    readback = _site_readback(request)
    reply = encode_admin_frame(d5v2.SERVER_GAMESCRIPT, _readback_bytes(readback) + b"\0")
    session = _FakeFreightSession(reply)
    parsed = asyncio.run(d5v2.exchange(session, request, tmp_path))
    assert session.sent == [d5v2.encode_freight_request(raw)]
    assert (tmp_path / "site-00-request.json").read_bytes() == raw
    assert parsed.request_id == "site-00" and parsed.status == "READY"
    assert parsed.funds == FUNDS_AT_DEPOT_MUTATION_CLOSE


def test_replay_parses_and_reencodes_the_site_request(tmp_path):
    """Retained-frame replay uses the same named protocol-8 request bound."""
    request = _production_site_request()
    raw = request.to_bytes()
    frame = d5v2.encode_freight_request(raw)
    (tmp_path / "frames.json").write_text(json.dumps([["outbound", frame.hex()]]))

    outbound, requests, replies, positions, _ = d5v2._parse_v2_phase_frames(tmp_path)
    assert outbound == [frame]
    assert requests == [request]
    assert replies == []
    assert positions[raw] == 0
    # The replay verifier's unique-frame rule re-encodes the same payload.
    assert outbound.count(d5v2.encode_freight_request(raw)) == 1
    # Replayed requests run through the production plan verifier, and stale
    # evidence still fails closed.
    d5v2.verify_request_against_plan(requests[0], plan=d5v2.freight_plan_v2(), seal=SEAL)
    with pytest.raises(ValueError, match="prelaunch seal"):
        d5v2.verify_request_against_plan(requests[0], plan=d5v2.freight_plan_v2(), seal="b" * 64)

    over = d5v2.encode_gamescript(raw + b" " * (777 - len(raw)), max_payload_bytes=1000)
    (tmp_path / "frames.json").write_text(json.dumps([["outbound", over.hex()]]))
    with pytest.raises(ValueError):
        d5v2._parse_v2_phase_frames(tmp_path)


def test_v2_request_transport_accepts_exactly_768_and_refuses_769():
    """The protocol-8 request transport is inclusive at 768 and closed at 769."""
    assert MAX_FREIGHT_REQUEST_BYTES_V2 == 768
    raw = _production_site_request().to_bytes()
    at_limit = raw + b" " * (768 - len(raw))
    assert len(at_limit) == 768
    frame = d5v2.encode_freight_request(at_limit)
    assert len(frame) == 772
    assert frame == encode_gamescript(at_limit, max_payload_bytes=MAX_FREIGHT_REQUEST_BYTES_V2)
    assert d5v2.decode_freight_request(frame[3:]) == at_limit
    assert d5v2.decode_freight_request(frame[3:]) == decode_gamescript(
        frame[3:], max_payload_bytes=MAX_FREIGHT_REQUEST_BYTES_V2
    )
    session = object.__new__(d5v2.FreightV2SecureSession)
    session._state = d5v2.AuthState.ACTIVE
    session.validate_outbound(frame)
    with pytest.raises(ValueError):
        d5v2.encode_freight_request(at_limit + b" ")
    with pytest.raises(ValueError):
        d5v2.decode_freight_request(at_limit + b" \0")
    for malformed in (b"\xff\0", b"x\0\0", b"x", b"\0"):
        with pytest.raises(ValueError):
            d5v2.decode_freight_request(malformed)


def test_generic_transport_default_stays_at_512_bytes():
    """Only protocol 8 opts into 768; the generic transport default is 512."""
    assert MAX_PAYLOAD_BYTES == 512
    raw = _production_site_request().to_bytes()
    with pytest.raises(ValueError):
        encode_gamescript(raw)
    assert len(encode_gamescript(raw[:512])) == 516


def test_disabled_session_refuses_outbound_validation():
    """Validation only ever runs on an encrypted ACTIVE stream."""
    session = object.__new__(d5v2.FreightV2SecureSession)
    session._state = d5v2.AuthState.CONNECTED
    with pytest.raises(ValueError, match="encrypted ACTIVE stream required"):
        session.validate_outbound(b"\x10\x00\x2e")


def test_subscriptions_and_quit_frames_skip_request_validation():
    """Control frames of the gamescript subscription are validated as such."""
    session = object.__new__(d5v2.FreightV2SecureSession)
    session._state = d5v2.AuthState.ACTIVE
    session.validate_outbound(gamescript_subscription())
    session.validate_outbound(d5v2.encode_admin_quit())


def test_wire_requests_map_every_planned_exchange():
    """Every planned request is produced by the production wire builder."""
    plan = d5v2.freight_plan_v2()
    schedule = d5v2.freight_schedule()
    state = dict(site=None, engine=SimpleNamespace(engine=123, quote=ENGINE_QUOTE_V2), vehicle=-1)
    downstream = {
        "vread",
        "order",
        "order-read",
        "monitor",
        "start",
        "load-watch",
        "transit-watch",
        "deliver-watch",
        "finance",
        "finish",
    }
    for entry in schedule:
        request = d5v2._freight_exchange_request(entry, SEAL, plan, state)
        assert FreightRequestV2.model_validate_json(request.to_bytes().decode()).to_bytes() == (
            request.to_bytes()
        )
        assert len(request.to_bytes()) <= MAX_FREIGHT_REQUEST_BYTES_V2
        op = request.op
        if op == "purchase":
            assert (request.engine, request.expected_cost) == (123, ENGINE_QUOTE_V2)
            assert (request.vehicle, request.order_index) == (-1, -1)
            assert (request.watch_ticks, request.watch_days) == (-1, -1)
        elif op == "engine":
            assert (request.engine, request.vehicle) == (123, -1)
        elif op in downstream:
            assert (request.engine, request.vehicle) == (123, VEHICLE)
        else:
            assert (request.engine, request.vehicle) == (-1, -1)
        if op == "site":
            assert request.route == FREIGHT_ROUTE_V2
            assert request.witness_digest == plan.witness_digest
        else:
            assert request.route is None and request.witness_digest is None
        if op == "order":
            assert request.order_index == entry["order_index"]
        else:
            assert request.order_index == -1
        if op == "load-watch":
            assert (request.watch_ticks, request.watch_days) == (
                WATCH_MAX_TICKS_V2,
                FREIGHT_CYCLE_DAY_CAP_V2,
            )
        elif op in ("transit-watch", "deliver-watch"):
            assert (request.watch_ticks, request.watch_days) == (
                WATCH_MAX_TICKS_V2,
                FREIGHT_CYCLE_DAY_CAP_V2,
            )
        else:
            assert (request.watch_ticks, request.watch_days) == (-1, -1)
        d5v2.verify_request_against_plan(request, plan=plan, seal=SEAL)
        if op == "purchase":
            state["vehicle"] = VEHICLE  # the built id binds after the purchase


def test_request_buying_drift_refuses_the_trust_anchor():
    """The planner-owned pins refuse stale or tampered requests before bytes."""
    plan = d5v2.freight_plan_v2()
    request = _production_site_request()
    d5v2.verify_request_against_plan(request, plan=plan, seal=SEAL)
    drifted = request.model_copy(update={"witness_digest": "b" * 64}, deep=True)
    with pytest.raises(ValueError, match="witness digest drifted"):
        d5v2.verify_request_against_plan(drifted, plan=plan, seal=SEAL)
    route_drift = request.model_copy(update={"route": (45748, 45747)}, deep=True)
    with pytest.raises(ValueError, match="site request route drifted"):
        d5v2.verify_request_against_plan(route_drift, plan=plan, seal=SEAL)
    ceiling = request.model_copy(update={"max_cost": FREIGHT_MAX_COST_V2 + 1}, deep=True)
    with pytest.raises(ValueError, match="ceiling drifted"):
        d5v2.verify_request_against_plan(ceiling, plan=plan, seal=SEAL)
    pins = request.model_copy(update={"pickup": 45749}, deep=True)
    with pytest.raises(ValueError, match="pins drifted"):
        d5v2.verify_request_against_plan(pins, plan=plan, seal=SEAL)
    # The site request's route/witness digests are mandatory, not optional.
    stripped = request.model_copy(update={"witness_digest": None, "route": None}, deep=True)
    with pytest.raises(ValueError, match="site request route drifted"):
        d5v2.verify_request_against_plan(stripped, plan=plan, seal=SEAL)
    # And no non-site request may carry either correlation key.
    order_request = d5v2._freight_exchange_request(
        d5v2.freight_schedule()[4], SEAL, plan, dict(site=None, engine=None, vehicle=VEHICLE)
    )
    assert order_request.op == "order"
    carrier = order_request.model_copy(update={"route": plan.vehicle_route}, deep=True)
    with pytest.raises(
        ValueError, match="only the site request may carry a route or witness digest"
    ):
        d5v2.verify_request_against_plan(carrier, plan=plan, seal=SEAL)


# --- H2: exchange timing is derived from the phase and overall budgets -------


def _watch_request() -> tuple[FreightRequestV2, FreightReadbackV2]:
    entry = d5v2.freight_schedule()[10]
    state = dict(
        site=None, engine=SimpleNamespace(engine=123, quote=ENGINE_QUOTE_V2), vehicle=VEHICLE
    )
    request = d5v2._freight_exchange_request(entry, SEAL, d5v2.freight_plan_v2(), state)
    readback = FreightReadbackV2(
        protocol=8,
        op="load-watch",
        request_id=request.request_id,
        plan=request.plan,
        company=request.company,
        max_cost=request.max_cost,
        pickup=request.pickup,
        delivery=request.delivery,
        depot=request.depot,
        route_digest=request.route_digest,
        engine=request.engine,
        vehicle=request.vehicle,
        expected_cost=request.expected_cost,
        order_index=request.order_index,
        watch_ticks=request.watch_ticks,
        watch_days=request.watch_days,
        status="LOADED",
        funds=FUNDS_AT_DEPOT_MUTATION_CLOSE - ENGINE_QUOTE_V2,
        cost=0,
        load=20,
        capacity=20,
        wait=3,
        pickup_amount=20,
        tick=100,
        day=730,
        paused=False,
        income=0,
    )
    return request, readback


def _reply_frame(readback: FreightReadbackV2) -> bytes:
    return encode_admin_frame(d5v2.SERVER_GAMESCRIPT, _readback_bytes(readback) + b"\0")


def test_exchange_timeout_is_derived_from_the_phase_budget():
    table = d5v2.budgets()
    site = _production_site_request()
    watch, _ = _watch_request()
    assert d5v2.exchange_timeout_seconds(site, budget_table=table) == table["request_seconds"]
    assert d5v2.exchange_timeout_seconds(watch, budget_table=table) == (
        table["watch_seconds"] + d5v2.FREIGHT_EXCHANGE_MARGIN_SECONDS
    )
    assert d5v2.exchange_timeout_seconds(watch, budget_table=table) > 10


class _RecordingTimeout:
    def __init__(self) -> None:
        self.seen: list[float] = []

    def __call__(self, seconds: float):
        self.seen.append(seconds)
        return contextlib.nullcontext()


class _Clock:
    def __init__(self, now: float = 1000.0) -> None:
        self.now = now

    def __call__(self) -> float:
        return self.now


def test_watch_exchange_inside_its_budget_is_not_killed_at_ten_seconds(tmp_path):
    """A valid watch exchange gets its full window budget, not the old 10 s."""
    request, readback = _watch_request()
    session = _FakeFreightSession(_reply_frame(readback))
    timeout = _RecordingTimeout()
    clock = _Clock()
    # The logical exchange consumes 11 s, still inside the permitted window.
    clock.now += 11
    parsed = asyncio.run(
        d5v2.exchange(
            session,
            request,
            tmp_path,
            budget_table=d5v2.budgets(),
            overall_deadline=clock.now + 100,
            clock=clock,
            timeout_factory=timeout,
        )
    )
    assert parsed.request_id == "load-00" and parsed.status == "LOADED"
    assert timeout.seen == [
        d5v2.budgets()["watch_seconds"] + d5v2.FREIGHT_EXCHANGE_MARGIN_SECONDS
    ]


class _ExpiringTimeout:
    def __call__(self, seconds: float):
        outer = self

        class _Expire:
            async def __aenter__(self):
                raise TimeoutError("simulated expiry")

            async def __aexit__(self, *exc):
                return False

        assert seconds > 0 and outer is not None
        return _Expire()


def test_exchange_exceeding_its_permitted_budget_fails_closed(tmp_path):
    request, _ = _watch_request()
    session = _FakeFreightSession(b"")
    with pytest.raises(TimeoutError, match="exceeded its"):
        asyncio.run(
            d5v2.exchange(
                session,
                request,
                tmp_path,
                budget_table=d5v2.budgets(),
                timeout_factory=_ExpiringTimeout(),
            )
        )
    assert (tmp_path / "load-00-request.json").is_file()
    assert not (tmp_path / "load-00-response.json").exists()


def test_exchange_is_clamped_to_the_remaining_overall_budget(tmp_path):
    request, readback = _watch_request()
    clock = _Clock()
    timeout = _RecordingTimeout()
    session = _FakeFreightSession(_reply_frame(readback))
    asyncio.run(
        d5v2.exchange(
            session,
            request,
            tmp_path,
            budget_table=d5v2.budgets(),
            overall_deadline=clock.now + 3,
            clock=clock,
            timeout_factory=timeout,
        )
    )
    assert timeout.seen == [3.0]


def test_exhausted_overall_watch_window_refuses_before_sending(tmp_path):
    request, _ = _watch_request()
    clock = _Clock()
    session = _FakeFreightSession(b"")
    with pytest.raises(TimeoutError, match="overall watch window exhausted"):
        asyncio.run(
            d5v2.exchange(
                session,
                request,
                tmp_path,
                budget_table=d5v2.budgets(),
                overall_deadline=clock.now - 1,
                clock=clock,
            )
        )
    assert session.sent == []


class _CancellingSession:
    async def send(self, frame: bytes) -> None:
        return None

    async def receive(self) -> bytes:
        raise asyncio.CancelledError


def test_exchange_cancellation_propagates_without_a_success(tmp_path):
    request, _ = _watch_request()
    with pytest.raises(asyncio.CancelledError):
        asyncio.run(d5v2.exchange(_CancellingSession(), request, tmp_path))
    assert not (tmp_path / "load-00-response.json").exists()


class _LateResponseSession:
    def __init__(self, reply: bytes) -> None:
        self._reply = reply

    async def send(self, frame: bytes) -> None:
        return None

    async def receive(self) -> bytes:
        return self._reply


def test_exchange_refuses_a_stale_late_response_for_another_request(tmp_path):
    request, _ = _watch_request()
    stale = _production_site_request()
    stale_readback = _site_readback(stale)
    with pytest.raises(ValueError, match="correlation mismatch"):
        asyncio.run(
            d5v2.exchange(_LateResponseSession(_reply_frame(stale_readback)), request, tmp_path)
        )


class _DuplicateFrameSession:
    def __init__(self, reply: bytes) -> None:
        self._reply = reply

    async def send(self, frame: bytes) -> None:
        return None

    async def receive(self) -> bytes:
        return self._reply + self._reply


def test_exchange_refuses_duplicate_response_frames(tmp_path):
    request, readback = _watch_request()
    with pytest.raises(ValueError, match="duplicate freight-proof response frame"):
        asyncio.run(
            d5v2.exchange(_DuplicateFrameSession(_reply_frame(readback)), request, tmp_path)
        )


class _PartialThenExpiredSession:
    def __init__(self) -> None:
        self._calls = 0

    async def send(self, frame: bytes) -> None:
        return None

    async def receive(self) -> bytes:
        self._calls += 1
        if self._calls == 1:
            return b"\x01\x02"
        raise TimeoutError("expired after partial read")


def test_exchange_refuses_partial_reads_and_late_timeouts(tmp_path):
    request, _ = _watch_request()
    with pytest.raises(TimeoutError, match="exceeded its"):
        asyncio.run(d5v2.exchange(_PartialThenExpiredSession(), request, tmp_path))
    assert not (tmp_path / "load-00-response.json").exists()


# --- C1/H1/H3 + consumed-frame replay: synthetic packed attempt fixtures ----
#
# These fixtures are explicitly synthetic. They copy a freshly staged candidate
# (whose prerequisite is the real pinned depot-mutation world of record) and
# fabricate only the
# missing post-launch artifacts: thirty correlated protocol-8 frames, the
# runtime welcome, cleanup certification and a receipt. No native process,
# AdminPort session, candidate claim, signature or Gate C authorization is
# created. Because no authorized freight v2 attempt exists in the repository,
# the operator-authorization gate is the one seam monkeypatched in the success
# tests; every prerequisite, identity, digest, phase, frame and cleanup fact is
# otherwise verified by the production replay path.


def _synthetic_readback(
    request: FreightRequestV2,
    status: FreightStatusV2,
    funds: int,
    *,
    cost: int = 0,
    vehicle: int | None = None,
    engine: int | None = None,
    **observations,
) -> FreightReadbackV2:
    return FreightReadbackV2(
        protocol=8,
        op=request.op,
        request_id=request.request_id,
        plan=request.plan,
        company=request.company,
        max_cost=request.max_cost,
        pickup=request.pickup,
        delivery=request.delivery,
        depot=request.depot,
        route_digest=request.route_digest,
        witness_digest=request.witness_digest,
        engine=request.engine if engine is None else engine,
        vehicle=request.vehicle if vehicle is None else vehicle,
        expected_cost=request.expected_cost,
        order_index=request.order_index,
        watch_ticks=request.watch_ticks,
        watch_days=request.watch_days,
        status=status,
        funds=funds,
        cost=cost,
        **observations,
    )


def _consumed_freight_exchanges(
    seal: str, *, zero: bool = False
) -> tuple[list[tuple[FreightRequestV2, FreightReadbackV2]], d5v2.FreightPlanV2]:
    """The full thirty-exchange attempt of record, as retained evidence."""
    plan = d5v2.freight_plan_v2()
    schedule = d5v2.freight_schedule()
    state = dict(
        site=None, engine=SimpleNamespace(engine=123, quote=ENGINE_QUOTE_V2), vehicle=-1
    )
    pair_total = len(plan.vehicle_route) - 1
    funds = FUNDS_AT_DEPOT_MUTATION_CLOSE
    income = 0
    delivered = 0
    tick = 100
    day = 730
    exchanges: list[tuple[FreightRequestV2, FreightReadbackV2]] = []
    for entry in schedule:
        request = d5v2._freight_exchange_request(entry, seal, plan, state)
        op = request.op
        cycle = -1
        if op.endswith("-watch"):
            cycle = int(d5v2.freight_exchange_cycle_index_v2(request.request_id) or -1)
        load = 0 if zero else LOADS[max(cycle, 0)]
        if op == "site":
            readback = _synthetic_readback(
                request,
                "READY",
                funds,
                paused=False,
                truck0=True,
                sid0=0,
                truck1=True,
                sid1=2,
                depot_ok=True,
                owner=0,
                pairs_ok=pair_total,
                pair_total=pair_total,
                accept=8,
                prod=100,
                wait=5,
                vehicles=0,
                road_ready=True,
                depot_edge=True,
                pickup_radius=3,
                delivery_radius=3,
                pickup_industry=7,
                pickup_industry_count=1,
                delivery_industry=9,
                delivery_industry_count=1,
                income=income,
            )
        elif op == "engine":
            readback = _synthetic_readback(
                request,
                "READY",
                funds,
                cost=ENGINE_QUOTE_V2,
                available=True,
                compatible=True,
                capacity=20,
                cargo=1,
                price=ENGINE_QUOTE_V2,
                max_speed=48,
                fleet=(123,),
                fleet_count=1,
                income=income,
            )
        elif op == "purchase":
            funds -= ENGINE_QUOTE_V2
            readback = _synthetic_readback(
                request, "BUILT", funds, cost=ENGINE_QUOTE_V2, vehicle=VEHICLE, income=income
            )
        elif request.request_id == "vread-00":
            readback = _synthetic_readback(
                request,
                "READ",
                funds,
                owner=0,
                location=d5v2.A1_DEPOT_TILE_V2,
                capacity=20,
                cargo=1,
                state="IN_DEPOT",
                in_depot=True,
                speed=0,
                income=income,
            )
        elif op == "order":
            readback = _synthetic_readback(
                request,
                "ORDERED",
                funds,
                dest=request.pickup if request.order_index == 0 else request.delivery,
                flags=0 if request.order_index == 0 else 128,
                goto=True,
                income=income,
            )
        elif op == "order-read":
            readback = _synthetic_readback(
                request,
                "ORDER_SET_VERIFIED",
                funds,
                order_len=2,
                dest0=request.pickup,
                flags0=0,
                goto0=True,
                dest1=request.delivery,
                flags1=128,
                goto1=True,
                income=income,
            )
        elif op == "monitor":
            readback = _synthetic_readback(
                request,
                "ARMED",
                funds,
                pickup_amount=0,
                delivery_amount=0,
                income=income,
                delivered=delivered,
            )
        elif op == "start":
            readback = _synthetic_readback(
                request,
                "STARTED",
                funds,
                state="RUNNING",
                speed=40,
                day=day,
                income=income,
            )
        elif request.request_id == "vread-01":
            readback = _synthetic_readback(
                request,
                "READ",
                funds,
                owner=0,
                location=request.pickup,
                capacity=20,
                cargo=1,
                state="RUNNING",
                in_depot=False,
                speed=80,
                income=income,
            )
        elif op == "load-watch":
            if zero:
                readback = _synthetic_readback(
                    request,
                    "ZERO_DEPARTED",
                    funds,
                    load=0,
                    pickup_amount=0,
                    tick=tick,
                    day=day,
                )
            else:
                readback = _synthetic_readback(
                    request,
                    "LOADED",
                    funds,
                    load=load,
                    capacity=20,
                    wait=5,
                    pickup_amount=load,
                    tick=tick,
                    day=day,
                    paused=False,
                    income=income,
                )
        elif op == "transit-watch":
            readback = _synthetic_readback(
                request,
                "AT_DELIVERY",
                funds,
                position=request.delivery,
                progress=pair_total,
                load=load,
                tick=tick + 30,
                day=day,
                paused=False,
                income=income,
            )
        elif op == "deliver-watch":
            if not zero:
                funds += INCOME_PER_CYCLE
                income += INCOME_PER_CYCLE
                delivered += DELIVERED_PER_CYCLE
            readback = _synthetic_readback(
                request,
                "DELIVERED",
                funds,
                load=0,
                position=request.delivery,
                pickup_amount=load,
                delivery_amount=load,
                recheck=True,
                tick=tick + 50,
                day=day,
                paused=False,
                income=income,
            )
        elif op == "finance":
            readback = _synthetic_readback(
                request,
                "FINANCE_VERIFIED",
                funds,
                income=income,
                delivered=delivered,
                last_accepted=900,
            )
        elif op == "finish":
            readback = _synthetic_readback(
                request,
                "PHASE_STOPPED",
                funds,
                state="STOPPED",
                speed=0,
                in_depot=False,
                stop_issued=True,
                income=income,
            )
        else:  # pragma: no cover - the fixed schedule exhausts the ops
            raise AssertionError(op)
        exchanges.append((request, readback))
        if op == "purchase":
            state["vehicle"] = VEHICLE
        if op == "deliver-watch":  # one 10-day lease per completed cycle
            tick += 100
            day += 10
    return exchanges, plan


def _write_manifest(directory: Path) -> None:
    (directory / "artifact-manifest.sha256").write_text(d5v2.manifest(directory))


def _reseal(directory: Path) -> None:
    (directory / "PRELAUNCH.sha256").write_text(sha256(directory / "PRELAUNCH.json") + "\n")
    claim_path = directory / "CLAIM.json"
    if claim_path.is_file():
        claim = json.loads(claim_path.read_text())
        claim["prelaunch_digest"] = sha256(directory / "PRELAUNCH.json")
        claim_path.write_text(json.dumps(claim, sort_keys=True, indent=2) + "\n")


def _write_attempt(
    directory: Path,
    seal: str,
    exchanges: list[tuple[FreightRequestV2, FreightReadbackV2]],
    plan: d5v2.FreightPlanV2,
    *,
    zero: bool = False,
    verified: bool = True,
    halt: dict | None = None,
    result_exchanges: list[str] | None = None,
    cleanup_complete: bool = True,
) -> None:
    """Materialize the retained attempt evidence under an existing candidate."""
    labels = [request.request_id for request, _ in exchanges]
    for request, readback in exchanges:
        response = _readback_bytes(readback)
        (directory / (request.request_id + "-request.json")).write_bytes(request.to_bytes())
        (directory / (request.request_id + "-response.json")).write_bytes(response)
    frames = []
    for request, readback in exchanges:
        frames.append(["outbound", d5v2.encode_freight_request(request.to_bytes()).hex()])
        frames.append(["inbound", _reply_frame(readback).hex()])
    (directory / "frames.json").write_text(json.dumps(frames))
    (directory / "session-before.sav").write_bytes(b"synthetic session-before fixture")
    (directory / "after.sav").write_bytes(b"synthetic after fixture")
    if verified:
        phase = d5v2.freight_phase_outcome_v2(exchanges, prelaunch_digest=seal, plan=plan)
        attempt = d5v2.verify_freight_attempt_v2(exchanges, prelaunch_digest=seal, plan=plan)
        (directory / "receipt.json").write_text(
            json.dumps(
                dict(
                    phase,
                    attempt=attempt,
                    before_save_sha256=sha256(directory / "session-before.sav"),
                    after_save_sha256=sha256(directory / "after.sav"),
                ),
                sort_keys=True,
                indent=2,
            )
            + "\n"
        )
    (directory / "runtime-identity.json").write_text(
        json.dumps(
            dict(
                auth="X25519_AuthorizedKey",
                encrypted=True,
                welcome=dict(retained_welcome(), dedicated=True),
                pid=4242,
            ),
            sort_keys=True,
            indent=2,
        )
        + "\n"
    )
    cleanup = dict(
        reaped=True,
        sockets_closed=True,
        workspace_disposed=True,
        credential_removed=True,
        returncode=0,
    )
    if not cleanup_complete:
        cleanup = dict(
            cleanup, workspace_disposed=False, verification_error="cleanup incomplete"
        )
    (directory / "cleanup.json").write_text(json.dumps(cleanup, sort_keys=True, indent=2) + "\n")
    (directory / "CLAIM.json").write_text(
        json.dumps(
            dict(
                prelaunch_digest=seal,
                consumed=True,
                launches_allowed=1,
                retries=0,
                authorization_schema=d5v2.CLAIM_AUTHORIZATION_EVIDENCE_SCHEMA,
                authorization_sha256="f" * 64,
                operator_key_identity="synthetic-test-fixture",
            ),
            sort_keys=True,
            indent=2,
        )
        + "\n"
    )
    last_status = "PHASE_STOPPED" if verified else (halt or {}).get("last_status", "FAILED")
    (directory / "result.json").write_text(
        json.dumps(
            dict(
                preflight="PASS",
                native_launches=1,
                connections=1,
                requests=len(exchanges),
                exchanges=labels if result_exchanges is None else result_exchanges,
                last_status=last_status,
                command_accepted=verified,
                state_changed=verified,
                verified=verified,
                status=(
                    "NATIVE_FREIGHT_VERIFIED"
                    if verified
                    else (halt or {}).get("result_status", "FAILED")
                ),
                halt=halt["halt"] if halt and "halt" in halt else halt,
                returncode=0,
                cleanup_complete=cleanup_complete,
            ),
            sort_keys=True,
            indent=2,
        )
        + "\n"
    )
    _write_manifest(directory)


def _materialized_consumed(
    source: Path, destination: Path
) -> tuple[Path, list[tuple[FreightRequestV2, FreightReadbackV2]], str, d5v2.FreightPlanV2]:
    """Copy a fresh candidate and fabricate its full consumed attempt."""
    shutil.copytree(
        source,
        destination,
        ignore=shutil.ignore_patterns("isolated", "freeze-probe"),
    )
    seal = sha256(destination / "PRELAUNCH.json")
    exchanges, plan = _consumed_freight_exchanges(seal)
    _write_attempt(destination, seal, exchanges, plan)
    return destination, exchanges, seal, plan


@pytest.fixture(scope="module")
def consumed_attempt(tmp_path_factory, staged):
    prepared = d5v2.prepare_candidate(tmp_path_factory.mktemp("d5v2-consumed") / "candidate")
    directory, exchanges, seal, plan = _materialized_consumed(
        prepared.directory, prepared.directory.parent / "consumed"
    )
    yield directory, exchanges, seal, plan
    prepared.spec.workspace.close()


@pytest.fixture(scope="module")
def zero_consumed_attempt(tmp_path_factory, staged):
    prepared = d5v2.prepare_candidate(tmp_path_factory.mktemp("d5v2-consumed-zero") / "candidate")
    prepared.spec.workspace.close()
    destination = prepared.directory.parent / "consumed-zero"
    shutil.copytree(
        prepared.directory,
        destination,
        ignore=shutil.ignore_patterns("isolated", "freeze-probe"),
    )
    seal = sha256(destination / "PRELAUNCH.json")
    exchanges, plan = _consumed_freight_exchanges(seal, zero=True)
    _write_attempt(destination, seal, exchanges, plan, zero=True)
    yield destination, exchanges, seal, plan


def _copy_attempt(source: Path, destination: Path) -> Path:
    shutil.copytree(
        source,
        destination,
        ignore=shutil.ignore_patterns("isolated", "freeze-probe"),
    )
    return destination


def _authorization_passthrough(monkeypatch):
    monkeypatch.setattr(d5v2, "replay_authorization_state", lambda *args, **kwargs: None)


def test_unconsumed_candidate_verifies_fail_closed(staged):
    """No candidate may claim a receipt before its one-shot consumption."""
    assert not (staged.directory / "CLAIM.json").exists()
    verdict = d5v2.verify_freight_attempt(staged.directory)
    assert verdict == {
        "verification": "AUTHORIZATION_UNVERIFIED",
        "authorization_state": "CLAIM_ABSENT",
        "statement": (
            "the candidate was never consumed by an operator authorization; "
            "no verified receipt is possible"
        ),
    }
    assert claim_status(staged.directory) == "ABSENT"


def test_exit_status_zero_only_for_the_verified_receipt():
    assert (
        d5v2.exit_status(
            dict(
                verified=True,
                status="NATIVE_FREIGHT_VERIFIED",
                cleanup_complete=True,
            )
        )
        == 0
    )
    for status in (
        "FAILED",
        "FAILED_CLEANUP",
        "PHASE_HALTED_PREFIX_PRESERVED",
        "NOT_DISPATCHED",
    ):
        assert d5v2.exit_status(dict(verified=False, status=status, cleanup_complete=True)) == 1
    assert (
        d5v2.exit_status(
            dict(
                verified=True,
                status="NATIVE_FREIGHT_VERIFIED",
                cleanup_complete=False,
            )
        )
        == 1
    )
    assert (
        d5v2.exit_status(
            dict(verified=True, status="FAILED_CLEANUP", cleanup_complete=True)
        )
        == 1
    )


def test_cleanup_failure_after_success_denies_the_verified_result():
    result = dict(verified=True, status="NATIVE_FREIGHT_VERIFIED", cleanup_complete=True)
    d5v2.apply_cleanup_outcome(result, complete=False)
    assert result["verified"] is False
    assert result["status"] == "FAILED_CLEANUP"
    assert result["prior_status"] == "NATIVE_FREIGHT_VERIFIED"
    assert result["cleanup_complete"] is False
    assert result["cleanup_failure"] is True
    assert "no verified receipt is possible" in str(result["error"])
    assert d5v2.exit_status(result) == 1
    d5v2.apply_cleanup_outcome(result, complete=False)
    assert result["status"] == "FAILED_CLEANUP"
    assert result["prior_status"] == "NATIVE_FREIGHT_VERIFIED"


def test_cleanup_failure_after_an_unsuccessful_attempt_preserves_its_status():
    result = dict(
        verified=False,
        status="PHASE_HALTED_PREFIX_PRESERVED",
        cleanup_complete=True,
        error="ValueError: halted exchange",
    )
    d5v2.apply_cleanup_outcome(result, complete=False)
    assert result["verified"] is False
    assert result["status"] == "PHASE_HALTED_PREFIX_PRESERVED"
    assert result["cleanup_complete"] is False
    assert result["cleanup_failure"] is True
    assert result["error"] == "ValueError: halted exchange"
    assert d5v2.exit_status(result) == 1
    d5v2.apply_cleanup_outcome(result, complete=True)
    assert result["cleanup_failure"] is True
    assert d5v2.exit_status(result) == 1


def test_deny_verification_preserves_the_original_error():
    result = dict(verified=True, status="NATIVE_FREIGHT_VERIFIED")
    result["error"] = "RuntimeError: original failure"
    d5v2.deny_verification(result, status="FAILED", message="post-check denied success")
    assert result["verified"] is False
    assert result["status"] == "FAILED"
    assert result["prior_status"] == "NATIVE_FREIGHT_VERIFIED"
    assert result["error"] == "RuntimeError: original failure"
    assert result["denial_errors"] == ["post-check denied success"]


def test_replay_verifies_a_fully_consumed_valid_frame_sequence(consumed_attempt, monkeypatch):
    directory, exchanges, seal, _ = consumed_attempt
    _authorization_passthrough(monkeypatch)
    verdict = d5v2.verify_freight_attempt(directory)
    assert verdict["verification"] == "RECEIPT_VERIFIED"
    assert verdict["receipt"]["attempt"]["verification"] == "FREIGHT_ATTEMPT_VERIFIED"
    receipt = verdict["receipt"]["attempt"]
    assert len(receipt["receipts"]) == PLANNED_FREIGHT_EXCHANGES_V2 == 30
    assert d5v2.verdict_exit_status(verdict) == 0
    outbound, requests, replies, _, _ = d5v2._parse_v2_phase_frames(directory)
    assert len(outbound) == len(requests) == len(replies) == PLANNED_FREIGHT_EXCHANGES_V2
    assert [request.request_id for request in requests] == list(FREIGHT_EXCHANGE_IDS_V2)
    assert outbound == [
        d5v2.encode_freight_request(request.to_bytes()) for request, _ in exchanges
    ]


def test_replay_verifies_a_consumed_zero_departure_attempt(zero_consumed_attempt, monkeypatch):
    directory, exchanges, seal, _ = zero_consumed_attempt
    _authorization_passthrough(monkeypatch)
    verdict = d5v2.verify_freight_attempt(directory)
    assert verdict["verification"] == "RECEIPT_VERIFIED"
    attempt = verdict["receipt"]["attempt"]
    assert attempt["verification"] == "FREIGHT_ZERO_DEPARTED_VERIFIED"
    assert attempt["completed_cycles"] == 0
    assert attempt["zero_cycle_receipts"] == 6
    assert attempt["zero_watch_events"] == 6
    assert len(exchanges) == PLANNED_FREIGHT_EXCHANGES_V2


def test_replay_refuses_missing_duplicated_out_of_order_and_altered_frames(
    consumed_attempt, tmp_path, monkeypatch
):
    source, _, _, _ = consumed_attempt
    _authorization_passthrough(monkeypatch)

    missing = _copy_attempt(source, tmp_path / "missing")
    (missing / "deliver-00-response.json").unlink()
    _write_manifest(missing)
    with pytest.raises(ValueError):
        d5v2.verify_freight_attempt(missing)

    duplicated = _copy_attempt(source, tmp_path / "duplicated")
    frames = json.loads((duplicated / "frames.json").read_text())
    frames.insert(1, list(frames[0]))
    (duplicated / "frames.json").write_text(json.dumps(frames))
    _write_manifest(duplicated)
    with pytest.raises(ValueError):
        d5v2.verify_freight_attempt(duplicated)

    out_of_order = _copy_attempt(source, tmp_path / "out-of-order")
    frames = json.loads((out_of_order / "frames.json").read_text())
    frames[0], frames[2] = frames[2], frames[0]
    (out_of_order / "frames.json").write_text(json.dumps(frames))
    _write_manifest(out_of_order)
    with pytest.raises(ValueError, match="precedes its own request"):
        d5v2.verify_freight_attempt(out_of_order)

    altered = _copy_attempt(source, tmp_path / "altered")
    response_path = altered / "load-00-response.json"
    readback = json.loads(response_path.read_text())
    readback["load"] = 19
    response_path.write_text(json.dumps(readback, sort_keys=True, separators=(",", ":")))
    _write_manifest(altered)
    with pytest.raises(ValueError):
        d5v2.verify_freight_attempt(altered)


def test_replay_fails_closed_on_wrong_source_save_digest(consumed_attempt, tmp_path, monkeypatch):
    source, _, _, _ = consumed_attempt
    _authorization_passthrough(monkeypatch)
    attempt = _copy_attempt(source, tmp_path / "wrong-source")
    metadata = json.loads((attempt / "PRELAUNCH.json").read_text())
    metadata["world"]["save_sha256"] = "0" * 64
    (attempt / "PRELAUNCH.json").write_text(json.dumps(metadata, sort_keys=True, indent=2) + "\n")
    _reseal(attempt)
    _write_manifest(attempt)
    with pytest.raises(ValueError, match="pinned prerequisite|pinned depot"):
        d5v2.verify_freight_attempt(attempt)


def test_replay_fails_closed_on_wrong_pinned_a1_digest(consumed_attempt, monkeypatch):
    directory, _, _, _ = consumed_attempt
    _authorization_passthrough(monkeypatch)
    d5v2.freight_facts.cache_clear()
    try:
        monkeypatch.setattr(d5v2, "PINNED_PREREQUISITE_AFTER_SAVE", "0" * 64)
        d5v2.freight_facts.cache_clear()
        with pytest.raises(ValueError, match="pinned|authoritative"):
            d5v2.verify_freight_attempt(directory)
    finally:
        monkeypatch.undo()
        d5v2.freight_facts.cache_clear()
        d5v2.freight_facts()


def test_replay_fails_closed_on_incomplete_world_welcome(consumed_attempt, tmp_path, monkeypatch):
    source, _, _, _ = consumed_attempt
    _authorization_passthrough(monkeypatch)
    attempt = _copy_attempt(source, tmp_path / "welcome")
    runtime = json.loads((attempt / "runtime-identity.json").read_text())
    del runtime["welcome"]["width"]
    (attempt / "runtime-identity.json").write_text(json.dumps(runtime, sort_keys=True, indent=2))
    _write_manifest(attempt)
    with pytest.raises(ValueError, match="welcome"):
        d5v2.verify_freight_attempt(attempt)


def test_replay_fails_closed_on_candidate_receipt_identity_mismatch(
    consumed_attempt, tmp_path, monkeypatch
):
    source, _, _, _ = consumed_attempt
    _authorization_passthrough(monkeypatch)
    attempt = _copy_attempt(source, tmp_path / "identity")
    metadata = json.loads((attempt / "PRELAUNCH.json").read_text())
    metadata["attempt"] = "D5-FREIGHT-9"
    (attempt / "PRELAUNCH.json").write_text(json.dumps(metadata, sort_keys=True, indent=2) + "\n")
    _reseal(attempt)
    _write_manifest(attempt)
    with pytest.raises(ValueError, match="attempt identity"):
        d5v2.verify_freight_attempt(attempt)

    tampered_receipt = _copy_attempt(source, tmp_path / "receipt")
    receipt = json.loads((tampered_receipt / "receipt.json").read_text())
    receipt["after_save_sha256"] = "0" * 64
    (tampered_receipt / "receipt.json").write_text(json.dumps(receipt, sort_keys=True, indent=2))
    _write_manifest(tampered_receipt)
    with pytest.raises(ValueError, match="receipt replay mismatch"):
        d5v2.verify_freight_attempt(tampered_receipt)

    tampered_prerequisite = _copy_attempt(source, tmp_path / "prerequisite")
    metadata = json.loads((tampered_prerequisite / "PRELAUNCH.json").read_text())
    metadata["prerequisite"]["after_save_sha256"] = "0" * 64
    (tampered_prerequisite / "PRELAUNCH.json").write_text(
        json.dumps(metadata, sort_keys=True, indent=2) + "\n"
    )
    _reseal(tampered_prerequisite)
    _write_manifest(tampered_prerequisite)
    with pytest.raises(ValueError, match="prerequisite binding"):
        d5v2.verify_freight_attempt(tampered_prerequisite)


def test_replay_refuses_resealed_schedule_and_budget_drift(consumed_attempt, tmp_path, monkeypatch):
    source, _, _, _ = consumed_attempt
    _authorization_passthrough(monkeypatch)
    schedule_drift = _copy_attempt(source, tmp_path / "schedule")
    metadata = json.loads((schedule_drift / "PRELAUNCH.json").read_text())
    metadata["plan_policy"]["schedule"][0]["exchange"] = "site-99"
    (schedule_drift / "PRELAUNCH.json").write_text(
        json.dumps(metadata, sort_keys=True, indent=2) + "\n"
    )
    _reseal(schedule_drift)
    _write_manifest(schedule_drift)
    with pytest.raises(ValueError, match="schedule drifted"):
        d5v2.verify_freight_attempt(schedule_drift)

    budget_drift = _copy_attempt(source, tmp_path / "budgets")
    metadata = json.loads((budget_drift / "PRELAUNCH.json").read_text())
    metadata["budgets"]["requests"] = 99
    (budget_drift / "PRELAUNCH.json").write_text(
        json.dumps(metadata, sort_keys=True, indent=2) + "\n"
    )
    _reseal(budget_drift)
    _write_manifest(budget_drift)
    with pytest.raises(ValueError, match="budget (contract|pins drifted)"):
        d5v2.verify_freight_attempt(budget_drift)


def test_replay_refuses_a_resealed_route_provenance_drift(consumed_attempt, tmp_path, monkeypatch):
    source, _, _, _ = consumed_attempt
    _authorization_passthrough(monkeypatch)
    attempt = _copy_attempt(source, tmp_path / "provenance")
    metadata = json.loads((attempt / "PRELAUNCH.json").read_text())
    metadata["plan_policy"]["route_provenance"]["route_digest"] = "0" * 64
    (attempt / "PRELAUNCH.json").write_text(json.dumps(metadata, sort_keys=True, indent=2) + "\n")
    _reseal(attempt)
    _write_manifest(attempt)
    with pytest.raises(ValueError, match="route provenance pin route_digest"):
        d5v2.verify_freight_attempt(attempt)


def test_replay_refuses_an_outbound_budget_overflow(consumed_attempt, tmp_path, monkeypatch):
    source, exchanges, _, _ = consumed_attempt
    _authorization_passthrough(monkeypatch)
    attempt = _copy_attempt(source, tmp_path / "budget-overflow")
    frames = json.loads((attempt / "frames.json").read_text())
    request, readback = exchanges[0]
    extra = ["outbound", d5v2.encode_freight_request(request.to_bytes()).hex()]
    frames.extend([extra] * 3)
    (attempt / "frames.json").write_text(json.dumps(frames))
    _write_manifest(attempt)
    with pytest.raises(ValueError, match="request budget exceeded"):
        d5v2.verify_freight_attempt(attempt)


def test_replay_preserves_an_incomplete_wire_sequence(consumed_attempt, tmp_path, monkeypatch):
    source, _, _, _ = consumed_attempt
    _authorization_passthrough(monkeypatch)
    attempt = _copy_attempt(source, tmp_path / "unresolved")
    frames = json.loads((attempt / "frames.json").read_text())
    frames = [
        entry
        for index, entry in enumerate(frames)
        if not (entry[0] == "outbound" and index == 0)
    ]
    (attempt / "frames.json").write_text(json.dumps(frames))
    _write_manifest(attempt)
    verdict = d5v2.verify_freight_attempt(attempt)
    assert verdict["verification"] == "UNRESOLVED_ATTEMPT_EVIDENCE_PRESERVED"
    assert verdict["result_status"] == "NATIVE_FREIGHT_VERIFIED"
    assert verdict["state_changed"] is True
    assert d5v2.verdict_exit_status(verdict) == 1


def test_replay_refuses_a_gateway_reply_that_lost_its_durable_file(
    consumed_attempt, tmp_path, monkeypatch
):
    source, _, _, _ = consumed_attempt
    _authorization_passthrough(monkeypatch)
    attempt = _copy_attempt(source, tmp_path / "reply-only")
    frames = json.loads((attempt / "frames.json").read_text())
    frames = [entry for entry in frames if not (entry[0] == "inbound" and frames.index(entry) == 1)]
    (attempt / "frames.json").write_text(json.dumps(frames))
    _write_manifest(attempt)
    with pytest.raises(ValueError, match="unique secure-session frame evidence"):
        d5v2.verify_freight_attempt(attempt)


def test_verify_cli_exits_nonzero_for_unverified_verdicts(staged, monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["prog", "verify", str(staged.directory)])
    with pytest.raises(SystemExit) as exit_info:
        d5v2.main()
    assert exit_info.value.code == 1
    printed = json.loads(capsys.readouterr().out)
    assert printed["verification"] == "AUTHORIZATION_UNVERIFIED"


def test_verify_cli_exits_zero_only_for_a_verified_receipt(consumed_attempt, monkeypatch, capsys):
    directory, _, _, _ = consumed_attempt
    _authorization_passthrough(monkeypatch)
    monkeypatch.setattr(sys, "argv", ["prog", "verify", str(directory)])
    with pytest.raises(SystemExit) as exit_info:
        d5v2.main()
    assert exit_info.value.code == 0
    printed = json.loads(capsys.readouterr().out)
    assert printed["verification"] == "RECEIPT_VERIFIED"


def test_verify_cli_cannot_turn_errors_or_malformed_input_into_success(tmp_path, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["prog", "verify", str(tmp_path / "missing")])
    with pytest.raises(Exception) as error:
        d5v2.main()
    assert not isinstance(error.value, SystemExit)

    monkeypatch.setattr(sys, "argv", ["prog", "not-a-command", str(tmp_path)])
    with pytest.raises(SystemExit) as exit_info:
        d5v2.main()
    assert exit_info.value.code == 2


def test_replay_preserves_a_failed_cleanup_as_failed_evidence(
    consumed_attempt, tmp_path, monkeypatch
):
    source, _, _, _ = consumed_attempt
    _authorization_passthrough(monkeypatch)
    attempt = _copy_attempt(source, tmp_path / "failed-cleanup")
    result = json.loads((attempt / "result.json").read_text())
    result["status"] = "FAILED_CLEANUP"
    result["verified"] = False
    result["cleanup_complete"] = False
    result["cleanup_failure"] = True
    result["error"] = "ValueError: cleanup was not certified; no verified receipt is possible"
    (attempt / "result.json").write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    cleanup = json.loads((attempt / "cleanup.json").read_text())
    cleanup["workspace_disposed"] = False
    cleanup["verification_error"] = "cleanup incomplete"
    (attempt / "cleanup.json").write_text(json.dumps(cleanup, sort_keys=True, indent=2))
    _write_manifest(attempt)
    verdict = d5v2.verify_freight_attempt(attempt)
    assert verdict["verification"] == "ATTEMPT_FAILED_EVIDENCE_PRESERVED"
    assert verdict["result_status"] == "FAILED_CLEANUP"
    assert verdict["cleanup_complete"] is False
    assert d5v2.verdict_exit_status(verdict) == 1


def test_replay_refuses_a_manifest_that_omits_a_retained_file(
    consumed_attempt, tmp_path, monkeypatch
):
    """A rewritten manifest that silently drops a file is refused."""
    source, _, _, _ = consumed_attempt
    _authorization_passthrough(monkeypatch)
    attempt = _copy_attempt(source, tmp_path / "non-exhaustive-manifest")
    lines = (attempt / "artifact-manifest.sha256").read_text().splitlines()
    kept = [line for line in lines if not line.endswith("  cleanup.json")]
    assert len(kept) == len(lines) - 1
    (attempt / "artifact-manifest.sha256").write_text("\n".join(kept) + "\n")
    with pytest.raises(ValueError, match="not exhaustive"):
        d5v2.verify_freight_attempt(attempt)


def test_replay_refuses_a_malformed_orphan_response_file(consumed_attempt, tmp_path, monkeypatch):
    """An unparsable response file with no matching request fails closed."""
    source, _, _, _ = consumed_attempt
    _authorization_passthrough(monkeypatch)
    attempt = _copy_attempt(source, tmp_path / "orphan-response")
    (attempt / "orphan-99-response.json").write_text("{not json")
    _write_manifest(attempt)
    with pytest.raises(ValueError, match="not a parseable readback"):
        d5v2.verify_freight_attempt(attempt)


# --- halted-attempt evidence classes ----------------------------------------


def _halted_exchanges(
    seal: str, status: FreightStatusV2, *, observations: dict
) -> tuple[list, d5v2.FreightPlanV2, list, list]:
    """A complete prefix plus one halted row, cut at ``load-01`` (index 13)."""
    exchanges, plan = _consumed_freight_exchanges(seal)
    halt_index = 13
    assert exchanges[halt_index][0].request_id == "load-01"
    request = exchanges[halt_index][0]
    halted = (
        request,
        _synthetic_readback(request, status, exchanges[halt_index][1].funds, **observations),
    )
    return exchanges[:halt_index], plan, [halted], exchanges


def _halted_attempt(
    destination: Path, status: FreightStatusV2, *, observations: dict
) -> tuple[Path, list, str, d5v2.FreightPlanV2, dict]:
    """Stage a fresh candidate and materialize its truthful halt evidence.

    A halt terminates execution mid-exchange: the held prefix and the halt
    row have durable request/response recordings, and the pending suffix
    never ran, so its files must not exist. Fabricating them (for example
    by copying a complete attempt) misrepresents the halt and is refused.
    """
    prepared = d5v2.prepare_candidate(destination)
    try:
        seal = sha256(destination / "PRELAUNCH.json")
        completed_rows, plan, halted_rows, _ = _halted_exchanges(
            seal, status, observations=observations
        )
        rows = [*completed_rows, *halted_rows]
        halt_label = rows[-1][0].request_id
        halt = dict(
            halt=dict(
                label=halt_label,
                error=f"ValueError: freight exchange {halt_label} failed verification",
            ),
            result_status="PHASE_HALTED_PREFIX_PRESERVED",
            last_status=status,
        )
        _write_attempt(
            destination,
            seal,
            rows,
            plan,
            verified=False,
            halt=halt,
            result_exchanges=[request.request_id for request, _ in completed_rows],
        )
        return destination, rows, seal, plan, halt
    finally:
        prepared.spec.workspace.close()


def test_replay_preserves_a_refusal_halt_as_halted_prefix_evidence(
    tmp_path, monkeypatch
):
    """A post-prefix refusal replays as PHASE_HALTED_EVIDENCE_PRESERVED."""
    _authorization_passthrough(monkeypatch)
    attempt, rows, _, plan, halt = _halted_attempt(
        tmp_path / "refusal-halt", "STALE_ADMISSION", observations={}
    )
    verdict = d5v2.verify_freight_attempt(attempt)
    assert [request.request_id for request, _ in rows] == list(FREIGHT_EXCHANGE_IDS_V2)[:14]
    assert verdict["verification"] == "PHASE_HALTED_EVIDENCE_PRESERVED"
    assert verdict["result_status"] == "PHASE_HALTED_PREFIX_PRESERVED"
    assert verdict["failed"]["label"] == "load-01"
    assert verdict["failed"]["status"] == "STALE_ADMISSION"
    assert verdict["failed"]["world_state"] == "HALTED_BEFORE_MUTATION"
    assert verdict["pending"] == []  # the halt row is the last held evidence row
    assert d5v2.verdict_exit_status(verdict) == 1


def test_replay_preserves_a_window_halt_as_inconclusive_prefix_evidence(
    tmp_path, monkeypatch
):
    """A window-exhaustion halt replays with the world honest: inconclusive."""
    _authorization_passthrough(monkeypatch)
    attempt, _, _, _, _ = _halted_attempt(
        tmp_path / "window-halt",
        "WINDOW_EXHAUSTED",
        observations=dict(load=0, tick=100, day=730),
    )
    verdict = d5v2.verify_freight_attempt(attempt)
    assert verdict["verification"] == "PHASE_HALTED_EVIDENCE_PRESERVED"
    assert verdict["failed"]["label"] == "load-01"
    assert verdict["failed"]["world_state"] == "INCONCLUSIVE_WINDOW"
    assert d5v2.verdict_exit_status(verdict) == 1


def test_replay_refuses_a_halt_record_that_contradicts_its_evidence(
    tmp_path, monkeypatch
):
    """A halted result whose label drifts from its last failed row is refused."""
    _authorization_passthrough(monkeypatch)
    attempt, _, _, _, _ = _halted_attempt(
        tmp_path / "drifted-halt", "STALE_ADMISSION", observations={}
    )
    result = json.loads((attempt / "result.json").read_text())
    result["halt"]["label"] = "transit-99"
    (attempt / "result.json").write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    _write_manifest(attempt)
    with pytest.raises(ValueError, match="halted phase evidence contradicts"):
        d5v2.verify_freight_attempt(attempt)


def test_replay_preserves_a_plain_failed_attempt_as_failed_evidence(
    tmp_path, monkeypatch
):
    """A FAILED terminal result replays as failed evidence, not as a success."""
    _authorization_passthrough(monkeypatch)
    attempt, _, _, _, _ = _halted_attempt(
        tmp_path / "failed",
        "ENGINE_PIN_MISMATCH",
        observations={},
    )
    result = json.loads((attempt / "result.json").read_text())
    result["status"] = "FAILED"
    result["last_status"] = "ENGINE_PIN_MISMATCH"
    (attempt / "result.json").write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    _write_manifest(attempt)
    verdict = d5v2.verify_freight_attempt(attempt)
    assert verdict["verification"] == "ATTEMPT_FAILED_EVIDENCE_PRESERVED"
    assert verdict["result_status"] == "FAILED"
    assert verdict["failed"]["label"] == "load-01"
    assert d5v2.verdict_exit_status(verdict) == 1
