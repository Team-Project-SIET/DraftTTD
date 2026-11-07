"""Native suite for the D5-F12-DEPOT-RELOAD observe-only pipeline (protocol 10).

The pipeline ``app/simulation/openttd/proof/corridor_depot_recheck_native.py``
is bound to the round-2 depot lineage: the one ``reload-00`` observe exchange
over the consumed ``D5-F12-DEPOT-3`` authoritative after-save, zero spend,
zero mutation, zero saves, and a verified completion whose loaded-source
digest binds three ways (staged record = run record = retained depot save).
This suite stages its own tmp candidates (offline only) and replays
fabricated consumed attempts through the module's own verifications. The
pinned prerequisite ``artifacts/experiments/d5-corridor-depot-mutation-native-
candidate-3`` is read-only here — it is never written, moved or re-derived —
and the prerequisite-refusal arms use fake directories only. No native
runtime is launched and no AdminPort is connected anywhere in this suite.

The depot native suite ``test_corridor_depot_mutation_native.py`` is the
fixture template for the staged/consumed attempts; the shared wire-frame
helper (``_admin_frame``) is imported from it, not copied.
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
from pathlib import Path
from typing import Any

import pytest

import app.simulation.openttd.proof.corridor_depot_mutation_native as depot_native
import app.simulation.openttd.proof.corridor_depot_recheck_native as work
import app.simulation.openttd.proof.corridor_freight_native as d5
from app.simulation.openttd import corridor_depot_mutation as dm
from app.simulation.openttd.proof.harness import manifest, sha256
from app.simulation.openttd.proof.world_correspondence import SOURCE_SAVE_GS_NAME
from tests.test_corridor_accept_survey_native import _admin_frame

# The round-2 facts of record (the E82 after-00 measurement); the module's
# own prerequisite binding must re-derive exactly this set from the
# consumed depot attempt.
FACTS_OF_RECORD = dict(
    depot_present=True,
    front_read=45743,
    owner=0,
    depot_linked=True,
    connected_front_to_depot=True,
    connected_depot_to_front=True,
)
FUNDS_OF_RECORD = 489650


def recheck_request(seal: str) -> dm.DepotRequest:
    return work._recheck_exchange_request(work.recheck_schedule()[0], seal)


def demolish_request(seal: str) -> dm.DepotRequest:
    """The depot family's demolish shape (a foreign op for the recheck)."""
    plan = depot_native.depot_plan()
    return dm.DepotRequest(
        op="demolish",
        request_id="demo-00",
        plan=seal,
        company=plan.company,
        max_cost=plan.max_cost,
        pickup=plan.pickup,
        delivery=plan.delivery,
        depot=plan.depot,
        tile=plan.depot,
        front_tile=None,
    )


def relabelled_request(seal: str) -> dm.DepotRequest:
    """A legal observe shape under a foreign exchange identity."""
    plan = depot_native.depot_plan()
    return dm.DepotRequest(
        op="observe",
        request_id="reload-01",
        plan=seal,
        company=plan.company,
        max_cost=plan.max_cost,
        pickup=plan.pickup,
        delivery=plan.delivery,
        depot=plan.depot,
        tile=None,
        front_tile=None,
    )


def readback_bytes(request: dm.DepotRequest, **overrides: Any) -> bytes:
    """A correlated observe readback payload of record."""
    body: dict = {
        "protocol": 10,
        "op": request.op,
        "request_id": request.request_id,
        "plan": request.plan,
        "company": request.company,
        "max_cost": request.max_cost,
        "pickup": request.pickup,
        "delivery": request.delivery,
        "depot": request.depot,
        "status": overrides.pop("status", "READY"),
        "funds": overrides.pop("funds", FUNDS_OF_RECORD),
        "cost": overrides.pop("cost", 0),
    }
    if body["status"] == "READY" and request.op == "observe":
        body.update(dict(FACTS_OF_RECORD))
    body.update(overrides)
    return json.dumps(body, separators=(",", ":")).encode()


def _phase_of(seal: str, wire: bytes, *, facts: dict | None = None):
    readback = dm.DepotReadback.parse_for(recheck_request(seal), wire)
    return work.recheck_phase_outcome(
        [(recheck_request(seal), readback)],
        prelaunch_digest=seal,
        facts_of_record=FACTS_OF_RECORD if facts is None else facts,
        funds_of_record=FUNDS_OF_RECORD,
    )


@pytest.fixture(scope="module")
def staged(tmp_path_factory):
    prepared = work.prepare_depot_recheck_candidate(
        tmp_path_factory.mktemp("recheck-staging") / "candidate"
    )
    yield prepared
    prepared.spec.workspace.close()


def metadata_of(prepared) -> dict:
    return json.loads((prepared.directory / "PRELAUNCH.json").read_text())


# --- the plan-bound pipeline and the observe-only guards ----------------------


def test_recheck_pipeline_constants():
    assert work.KIND == "depot-recheck"
    assert work.MILESTONE_DEPOT_RECHECK == "D5-F12-DEPOT-RELOAD"
    assert work.RECHECK_ATTEMPT == "D5-F12-DEPOT-RELOAD-1"
    assert work.D5_DEPOT_RECHECK_PRELAUNCH_SCHEMA == "d5-f12-depot-reload-prelaunch-v1"
    assert work.D5_DEPOT_RECHECK_PREREQUISITE_SCHEMA == "d5-native-prerequisite-attempt-v1"
    assert work.D5_DEPOT_RECHECK_LAUNCH_CONSUMED_SCHEMA == "d5-native-launch-consumed"
    assert work.RECHECK_EXCHANGE_ID == "reload-00" and work.RECHECK_OP == "observe"
    assert work.PLANNED_RECHECK_EXCHANGES == 1 and work.RECHECK_REQUEST_BUDGET == 1
    assert work.RECHECK_MAX_COST == 0
    assert work.RECHECK_READY_MARKER == "D5_F12_DEPOT_RECHECK_READY"
    assert work.RECHECK_START_DAY_FLOOR == 712223
    assert work.RECHECK_AFTER_RECEIPT_NAME == "after-reload-receipt.json"
    assert work.RECHECK_AFTER_RECEIPT_SCHEMA == "d5-f12-depot-reload-receipt-v1"
    assert work.RECHECK_FORBIDDEN_ARTIFACTS == (
        "after.sav",
        "session-before.sav",
        "after-diagnostic.sav",
        "session-before-identity.json",
        "receipt.json",
    )
    assert work.recheck_budgets() == dict(
        launches=1,
        connection_attempts=1,
        requests=1,
        planned_exchanges=1,
        gsadmin_bytes=512,
        response_bytes=512,
        retries=0,
        reconnects=0,
        readiness_seconds=45,
        request_seconds=10,
        total_seconds=120,
        max_cost=0,
    )
    profile = work.recheck_profile()
    assert profile["permitted_ops"] == ["observe"]
    assert profile["mutating_ops"] == []
    assert profile["max_cost"] == 0 and profile["wire_max_cost_echo"] == 3000
    assert profile["zero_spend_required"] is True


def test_recheck_schedule_is_the_pinned_one_exchange_observe_gate():
    assert work.recheck_schedule() == [{"exchange": "reload-00", "op": "observe"}]
    assert work.staged_recheck_schedule({"schedule_version": 1}) == work.recheck_schedule()
    with pytest.raises(work.RecheckStagingError, match="one pinned reload observe gate"):
        work._require_recheck_schedule([{"exchange": "reload-01", "op": "observe"}])
    with pytest.raises(work.RecheckStagingError, match="one pinned reload observe gate"):
        work._require_recheck_schedule([{"exchange": "demo-00", "op": "demolish"}])
    with pytest.raises(work.RecheckStagingError, match="one pinned reload observe gate"):
        work._require_recheck_schedule(
            [
                {"exchange": "reload-00", "op": "observe"},
                {"exchange": "reload-01", "op": "observe"},
            ]
        )
    with pytest.raises(ValueError, match="unknown depot recheck schedule version"):
        work.staged_recheck_schedule({"schedule_version": 2})
    with pytest.raises(work.RecheckStagingError, match="one pinned observe exchange only"):
        work._recheck_exchange_request({"exchange": "reload-01", "op": "observe"}, "a" * 64)


def test_recheck_request_is_the_pinned_observe_exchange_with_no_tiles():
    request = recheck_request("a" * 64)
    assert (request.request_id, request.op) == ("reload-00", "observe")
    assert request.tile is None and request.front_tile is None
    # The wire max_cost echo of record is the depot contract's forced
    # attempt echo; the recheck's own ceiling stays zero Python-side.
    assert request.max_cost == 3000 and request.company == 0
    assert (request.pickup, request.delivery, request.depot) == (45748, 50351, 45487)
    dm.verify_request_against_depot_plan(
        request, plan=depot_native.depot_plan(), seal="a" * 64
    )
    work.verify_request_against_recheck_plan(request, seal="a" * 64)
    with pytest.raises(ValueError, match="staged prelaunch seal"):
        work.verify_request_against_recheck_plan(request, seal="b" * 64)
    with pytest.raises(ValueError, match="one pinned reload-00 exchange"):
        work.verify_request_against_recheck_plan(relabelled_request("a" * 64), seal="a" * 64)
    with pytest.raises(ValueError, match="non-observe op"):
        work.verify_request_against_recheck_plan(demolish_request("a" * 64), seal="a" * 64)
    # A genuinely pin-drifted observe request: the legal shape under a
    # moved pickup tile (the label and op stay pinned).
    with pytest.raises(ValueError, match="pins drifted"):
        work.verify_request_against_recheck_plan(
            recheck_request("a" * 64).model_copy(update={"pickup": 45749}), seal="a" * 64
        )
    with pytest.raises(ValueError, match="carries no tile"):
        work.verify_request_against_recheck_plan(
            recheck_request("a" * 64).model_copy(update={"tile": 45487}), seal="a" * 64
        )
    with pytest.raises(ValueError, match="carries no tile"):
        work.verify_request_against_recheck_plan(
            recheck_request("a" * 64).model_copy(update={"front_tile": 45743}),
            seal="a" * 64,
        )


def test_recheck_pinned_company_and_tiles_come_from_the_depot_lineage():
    request = recheck_request("c" * 64)
    plan = depot_native.depot_plan()
    assert request.company == plan.company == 0
    assert (request.pickup, request.delivery, request.depot) == (
        plan.pickup,
        plan.delivery,
        plan.depot,
    )
    assert plan.max_cost == 3000


def test_recheck_encoding_shares_the_depot_wire_bounds():
    payload = recheck_request("d" * 64).to_bytes()
    assert work.encode_recheck_request(payload) == depot_native.encode_depot_request(payload)
    assert bytes(payload) == bytes(dm.DepotRequest.model_validate_json(payload).to_bytes())


def test_recheck_session_carries_the_observe_exchange_only():
    """The observe-only write policy: a depot mutating op and a foreign
    exchange identity cannot ride the recheck session, and neither can
    unframed garbage."""
    session = object.__new__(work.DepotRecheckSecureSession)
    session._state = d5.AuthState.ACTIVE
    session.validate_outbound(work.encode_recheck_request(recheck_request("e" * 64).to_bytes()))
    with pytest.raises(ValueError, match="non-observe op"):
        session.validate_outbound(
            work.encode_recheck_request(demolish_request("e" * 64).to_bytes())
        )
    with pytest.raises(ValueError, match="foreign exchange identity"):
        session.validate_outbound(
            work.encode_recheck_request(relabelled_request("e" * 64).to_bytes())
        )
    with pytest.raises(Exception):
        session.validate_outbound(b"garbage")


def test_recheck_exit_statuses_fail_closed():
    verified = dict(
        verified=True,
        status="NATIVE_DEPOT_RELOAD_COMPLETE",
        cleanup_complete=True,
        state_changed=False,
        mutated=[],
    )
    assert work.recheck_exit_status(verified) == 0
    assert work.recheck_exit_status({**verified, "state_changed": True}) == 1
    assert work.recheck_exit_status({**verified, "mutated": ["reload-00"]}) == 1
    assert work.recheck_verdict_exit_status({"verification": "DEPOT_RELOAD_FACTS_VERIFIED"}) == 0
    assert (
        work.recheck_verdict_exit_status({"verification": "PHASE_HALTED_EVIDENCE_PRESERVED"})
        == 1
    )


# --- the production phase outcome arms ----------------------------------------


def test_phase_outcome_verifies_the_round2_equality():
    phase = _phase_of("f" * 64, readback_bytes(recheck_request("f" * 64)))
    assert phase["verification"] == "DEPOT_RELOAD_OBSERVED"
    assert phase["gate"]["verdict"] == "DEPOT_RELOAD_GATE_PASSES"
    assert phase["state_changed"] is False
    assert phase["mutations"] == []
    assert phase["failed"] is None and phase["pending"] == []
    assert phase["funds"] == FUNDS_OF_RECORD
    assert [row["exchange"] for row in phase["funds_chain"]] == ["reload-00"]
    assert [row["funds_before"] for row in phase["funds_chain"]] == [FUNDS_OF_RECORD]
    assert [row["cost"] for row in phase["receipts"]] == [0]
    receipt = phase["receipts"][0]
    assert receipt["verification"] == "DEPOT_RELOAD_MEASURED"
    assert receipt["facts"] == FACTS_OF_RECORD


def test_phase_outcome_refuses_fact_divergence_and_funds_drift():
    diverged = _phase_of(
        "a" * 64, readback_bytes(recheck_request("a" * 64), connected_front_to_depot=False)
    )
    assert diverged["verification"] == "DEPOT_RELOAD_INCOMPLETE"
    assert diverged["gate"]["verdict"] == "DEPOT_RELOAD_GATE_DIVERGED"
    assert "STALE_PIN" in diverged["failed"]["error"]
    assert "connected_front_to_depot: measured False, pinned True" in diverged["failed"]["error"]
    broket = _phase_of(
        "a" * 64, readback_bytes(recheck_request("a" * 64), funds=FUNDS_OF_RECORD - 1)
    )
    assert broket["verification"] == "DEPOT_RELOAD_INCOMPLETE"
    assert "funds of record broke" in broket["failed"]["error"]


def test_phase_outcome_refuses_a_status_refusal_and_a_malformed_exchange():
    refused = _phase_of("b" * 64, readback_bytes(recheck_request("b" * 64), status="STALE_PIN"))
    assert refused["verification"] == "DEPOT_RELOAD_INCOMPLETE"
    assert refused["gate"]["verdict"] == "DEPOT_RELOAD_GATE_UNDECIDED_INCOMPLETE"
    assert refused["failed"]["status"] == "STALE_PIN"
    malformed = work.recheck_phase_outcome(
        [(recheck_request("c" * 64), ValueError("the reply bytes never correlated"))],
        prelaunch_digest="c" * 64,
        facts_of_record=FACTS_OF_RECORD,
        funds_of_record=FUNDS_OF_RECORD,
    )
    assert malformed["verification"] == "DEPOT_RELOAD_INCOMPLETE"
    assert malformed["failed"]["status"] == "MALFORMED"
    empty = work.recheck_phase_outcome(
        [],
        prelaunch_digest="d" * 64,
        facts_of_record=FACTS_OF_RECORD,
        funds_of_record=FUNDS_OF_RECORD,
    )
    assert empty["verification"] == "DEPOT_RELOAD_INCOMPLETE"
    assert empty["pending"] == ["reload-00"]
    assert empty["gate"]["verdict"] == "DEPOT_RELOAD_GATE_UNDECIDED_INCOMPLETE"


# --- the prerequisite binding of record ---------------------------------------


def test_recheck_prerequisite_binding_is_the_pinned_round2_attempt():
    binding = work.recheck_prerequisite_binding()
    assert binding["attempt"] == "D5-F12-DEPOT-3"
    assert binding["milestone"] == "D5-F12-DEPOT"
    assert binding["save"] == "after.sav"
    assert binding["save_sha256"] == work.RECHECK_PREREQUISITE_AFTER_SAVE
    assert binding["facts_of_record"] == FACTS_OF_RECORD
    assert binding["funds_of_record"] == FUNDS_OF_RECORD
    assert binding["fleet_of_record"] == 0
    assert binding["expected_welcome"]["start_day"] >= work.RECHECK_START_DAY_FLOOR
    provenance = binding["provenance"]
    assert provenance["after_save_sha256"] == work.RECHECK_PREREQUISITE_AFTER_SAVE
    assert provenance["replay"] == "F12_MUTATION_COMPLETION_VERIFIED"
    assert provenance["statement"].startswith("the round-2 authoritative world of record")


def test_recheck_prerequisite_binding_refuses_foreign_directories(tmp_path):
    fake = tmp_path / "not-the-depot-attempt"
    fake.mkdir()
    with pytest.raises(work.RecheckStagingError, match="pinned round-2 depot attempt"):
        work.recheck_prerequisite_binding(fake)
    with pytest.raises(work.RecheckStagingError, match="pinned round-2 depot attempt"):
        work.prepare_depot_recheck_candidate(tmp_path / "candidate", prerequisite=fake)


# --- staging correctness -------------------------------------------------------


def test_staged_candidate_binds_the_recheck_lineage(staged):
    metadata = metadata_of(staged)
    assert metadata["schema"] == work.D5_DEPOT_RECHECK_PRELAUNCH_SCHEMA
    assert metadata["attempt"] == work.RECHECK_ATTEMPT == "D5-F12-DEPOT-RELOAD-1"
    assert metadata["milestone"] == work.MILESTONE_DEPOT_RECHECK
    assert metadata["kind"] == work.KIND == "depot-recheck"
    assert metadata["budgets"] == work.recheck_budgets()
    assert metadata["public_key"] == staged.public_key
    assert metadata["binary_sha256"] == d5.BINARY_SHA256
    policy = metadata["plan_policy"]
    assert policy["schedule"] == work.recheck_schedule()
    assert policy["plan_digest"] == work.plan_digest_of(policy["schedule"])
    assert policy["plan_model_digest"] == depot_native.depot_plan().digest
    assert policy["schedule_version"] == 1
    assert policy["max_cost"] == 0 and policy["wire_max_cost_echo"] == 3000
    world = policy["world"]
    assert world["facts_of_record"] == FACTS_OF_RECORD
    assert world["funds_of_record"] == FUNDS_OF_RECORD
    assert world["fleet_of_record"] == 0
    assert policy["profile"] == work.recheck_profile()
    assert metadata["world"]["mode"] == "PREREQUISITE_ATTEMPT_SOURCE_SAVE_LOAD"
    assert metadata["world"]["source_save"] == "after.sav"
    assert metadata["world"]["save_sha256"] == work.RECHECK_PREREQUISITE_AFTER_SAVE
    save_policy = metadata["save_policy"]
    assert save_policy.count("no authoritative save") == 1
    assert "no finally-diagnostic save" in save_policy
    assert "no save file of any kind" in save_policy
    assert metadata["prerequisite"]["schema"] == work.D5_DEPOT_RECHECK_PREREQUISITE_SCHEMA
    assert metadata["prerequisite"]["attempt"] == "D5-F12-DEPOT-3"
    assert metadata["prerequisite"]["milestone"] == "D5-F12-DEPOT"
    assert metadata["prerequisite"]["after_save"] == "after.sav"
    assert metadata["prerequisite"]["after_save_sha256"] == work.RECHECK_PREREQUISITE_AFTER_SAVE
    assert metadata["cross_schedule_guard"]["mutating_ops"] == []
    identity = metadata["game_script_identity"]
    assert identity["name"] == SOURCE_SAVE_GS_NAME
    assert identity["create_instance"] == "NetworkFreightProof"
    assert "no save" in metadata["expected_readback"]["zero_save"]


def test_staged_source_save_is_the_round2_authoritative_after_save(staged):
    metadata = metadata_of(staged)
    staged_save = Path(metadata["workspace"]) / "source.sav"
    assert staged_save.is_file()
    assert sha256(staged_save) == work.RECHECK_PREREQUISITE_AFTER_SAVE
    # The retained prerequisite authority: read-only here, never touched.
    retained = work.RECHECK_PREREQUISITE / "after.sav"
    assert sha256(retained) == work.RECHECK_PREREQUISITE_AFTER_SAVE
    assert retained.stat().st_size >= 1


def test_staged_composition_bridges_the_retained_save_restore_identity(staged):
    composition, create_instance, version = work.staged_recheck_composition()
    metadata = metadata_of(staged)
    assert create_instance == "NetworkFreightProof"
    assert metadata["game_script_identity"]["version"] == version
    assert (
        b"class NetworkFreightProof extends D5DepotRecheckProof" in composition["main.nut"]
    )
    staged_identity = Path(metadata["workspace"]) / "game" / SOURCE_SAVE_GS_NAME
    assert staged_identity.joinpath("info.nut").read_bytes() == composition["info.nut"]
    assert staged_identity.joinpath("main.nut").read_bytes() == composition["main.nut"]


def test_staged_freeze_binds_the_recheck_closure(staged):
    metadata = metadata_of(staged)
    frozen = metadata["frozen"]
    closure = d5.d2_source_closure(work.RECHECK_CLOSURE_ROOT)
    dependencies = d5.d2_dependency_inventory(work.RECHECK_CLOSURE_ROOT)
    for name, digest in closure.items():
        assert frozen[name] == digest
    for name, digest in dependencies.items():
        assert frozen[name] == digest
    # The closure root itself and the observe-only package main are two of
    # the frozen entries of record.
    assert frozen[str(Path(work.__file__).resolve())] == sha256(Path(work.__file__))
    recheck_main = work.RECHECK_PACKAGE / "main.nut"
    assert frozen[str(recheck_main.resolve())] == sha256(recheck_main)


def test_staged_authorization_payload_digest_is_stable(staged):
    digest = work.staged_recheck_authorization_payload_digest(staged.directory)
    assert re.fullmatch(r"[0-9a-f]{64}", digest)
    assert digest == work.staged_recheck_authorization_payload_digest(staged.directory)


def test_recheck_preflight_re_derives_every_binding(staged):
    metadata = work.recheck_preflight(staged)
    assert metadata["attempt"] == work.RECHECK_ATTEMPT
    assert metadata["plan_policy"]["schedule"] == work.recheck_schedule()


def _set_field(record: dict, dotted: str, value: Any) -> None:
    keys = dotted.split(".")

    def walk(current: dict, path: list[str]) -> None:
        key, rest = path[0], path[1:]
        if rest:
            walk(current[key], rest)
        else:
            current[key] = value

    walk(record, keys)


def _preflight_copy(staged, tmp_path, *mutations: tuple[str, Any], reseal: bool = False):
    """A refusal workspace: the two prelaunch records are copied; the
    staged workspace bytes stay put behind the original fixture (the early
    seal/lineage/policy checks never reach the workspace ownership gate)."""
    directory = tmp_path / "preflight-refusal"
    directory.mkdir(exist_ok=True)
    shutil.copyfile(staged.directory / "PRELAUNCH.json", directory / "PRELAUNCH.json")
    shutil.copyfile(staged.directory / "PRELAUNCH.sha256", directory / "PRELAUNCH.sha256")
    if mutations:
        metadata = json.loads((directory / "PRELAUNCH.json").read_text())
        for dotted, value in mutations:
            _set_field(metadata, dotted, value)
        (directory / "PRELAUNCH.json").write_text(
            json.dumps(metadata, sort_keys=True, indent=2) + "\n"
        )
        if reseal:
            (directory / "PRELAUNCH.sha256").write_text(
                sha256(directory / "PRELAUNCH.json") + "\n"
            )
    return directory


def test_recheck_preflight_refuses_prelaunch_tampering(staged, tmp_path):
    directory = _preflight_copy(staged, tmp_path, ("attempt", "D5-F12-DEPOT-RELOAD-9"))
    with pytest.raises(ValueError, match="seal mismatch"):
        work.recheck_preflight(d5.reopen_candidate(directory))


def test_recheck_preflight_refuses_attempt_and_schema_drift(staged, tmp_path):
    with pytest.raises(ValueError, match="staged attempt identity drifted"):
        work.recheck_preflight(
            d5.reopen_candidate(
                _preflight_copy(
                    staged,
                    tmp_path,
                    ("attempt", "D5-F12-DEPOT-RELOAD-2"),
                    reseal=True,
                )
            )
        )
    with pytest.raises(ValueError, match="not the D5 reload lineage"):
        work.recheck_preflight(
            d5.reopen_candidate(
                _preflight_copy(
                    staged, tmp_path, ("schema", "d5-f12-depot-prelaunch-v2"), reseal=True
                )
            )
        )


def test_recheck_preflight_refuses_schedule_and_budget_drift(staged, tmp_path):
    schedule = [{"exchange": "reload-01", "op": "observe"}]
    with pytest.raises(ValueError, match="schedule drifted"):
        work.recheck_preflight(
            d5.reopen_candidate(
                _preflight_copy(
                    staged, tmp_path, ("plan_policy.schedule", schedule), reseal=True
                )
            )
        )
    with pytest.raises(ValueError, match="zero-spend ceiling"):
        work.recheck_preflight(
            d5.reopen_candidate(
                _preflight_copy(
                    staged, tmp_path, ("plan_policy.max_cost", 100), reseal=True
                )
            )
        )


# --- the synthetic consumed recheck attempt ------------------------------------


def _consumed_recheck_exchange(seal: str, metadata: dict):
    entry = work.recheck_schedule()[0]
    request = work._recheck_exchange_request(entry, seal)
    facts = dict(metadata["plan_policy"]["world"]["facts_of_record"])
    funds = int(metadata["plan_policy"]["world"]["funds_of_record"])
    body = {
        "protocol": 10,
        "op": request.op,
        "request_id": request.request_id,
        "plan": request.plan,
        "company": request.company,
        "max_cost": request.max_cost,
        "pickup": request.pickup,
        "delivery": request.delivery,
        "depot": request.depot,
        "status": "READY",
        "funds": funds,
        "cost": 0,
        **facts,
    }
    readback = dm.DepotReadback.parse_for(
        request, json.dumps(body, separators=(",", ":")).encode()
    )
    return [(request, readback)], facts, funds


def _wire_of(readback: dm.DepotReadback) -> bytes:
    return json.dumps(
        readback.model_dump(mode="json", exclude_none=True), separators=(",", ":")
    ).encode()


def _fabricate_consumed_recheck_frames(directory: Path, exchanges) -> None:
    frames = []
    for request, readback in exchanges:
        wire = _wire_of(readback)
        (directory / (request.request_id + "-request.json")).write_bytes(request.to_bytes())
        (directory / (request.request_id + "-response.json")).write_bytes(wire)
        frames.append(["outbound", work.encode_recheck_request(request.to_bytes()).hex()])
        frames.append(["inbound", _admin_frame(wire + b"\0").hex()])
    (directory / "frames.json").write_text(json.dumps(frames))


def _refab_frames(directory: Path, *, with_response: bool = True) -> None:
    """Re-write the retained frame stream after a response-file tamper."""
    path = directory / "reload-00-request.json"
    request = dm.DepotRequest.model_validate_json(path.read_bytes())
    frames = [["outbound", work.encode_recheck_request(request.to_bytes()).hex()]]
    if with_response:
        wire = (directory / "reload-00-response.json").read_bytes()
        frames.append(["inbound", _admin_frame(wire + b"\0").hex()])
    (directory / "frames.json").write_text(json.dumps(frames))


def _fabricate_consumed_recheck_records(
    directory: Path, seal: str, phase: dict, metadata: dict, exchanges
) -> None:
    """Write the post-launch recheck records exactly as the run arms them.

    The observe-only run writes no save of any kind: the retained round-2
    authoritative after-save stays the only world binding and binds three
    ways (staged record = run record = retained file).
    """
    (directory / "runtime-identity.json").write_text(
        json.dumps(
            dict(
                auth="X25519_AuthorizedKey",
                encrypted=True,
                welcome=dict(metadata["world"]["expected_welcome"], dedicated=True),
                pid=4242,
            ),
            sort_keys=True,
            indent=2,
        )
        + "\n"
    )
    (directory / "cleanup.json").write_text(
        json.dumps(
            dict(
                reaped=True,
                sockets_closed=True,
                workspace_disposed=True,
                credential_removed=True,
                returncode=0,
            ),
            sort_keys=True,
        )
        + "\n"
    )
    (directory / "CLAIM.json").write_text(
        json.dumps(
            dict(
                prelaunch_digest=seal,
                consumed=True,
                launches_allowed=1,
                retries=0,
                authorization_schema="d2-clearing-claim-authorization-v2",
                authorization_sha256="f" * 64,
                operator_key_identity="synthetic-test-fixture",
            ),
            sort_keys=True,
        )
        + "\n"
    )
    result: dict[str, Any] = dict(
        preflight="PASS",
        native_launches=1,
        connections=1,
        requests=1,
        exchanges=[request.request_id for request, _ in exchanges],
        mutated=[],
        last_status="READY",
        command_accepted=True,
        state_changed=False,
        verified=True,
        status="NATIVE_DEPOT_RELOAD_COMPLETE",
        halt=None,
        returncode=0,
        cleanup_complete=True,
        loaded_source_sha256=work.RECHECK_PREREQUISITE_AFTER_SAVE,
    )
    (directory / "result.json").write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    (directory / work.RECHECK_AFTER_RECEIPT_NAME).write_text(
        json.dumps(
            dict(
                schema=work.RECHECK_AFTER_RECEIPT_SCHEMA,
                attempt=work.RECHECK_ATTEMPT,
                milestone=work.MILESTONE_DEPOT_RECHECK,
                prelaunch_sha256=seal,
                phase=dict(phase),
                loaded_source_sha256=work.RECHECK_PREREQUISITE_AFTER_SAVE,
                funds_of_record=int(metadata["plan_policy"]["world"]["funds_of_record"]),
                fleet_of_record=int(metadata["plan_policy"]["world"]["fleet_of_record"]),
                statement=work.RECHECK_AFTER_RECEIPT_STATEMENT,
            ),
            sort_keys=True,
            indent=2,
        )
        + "\n"
    )
    (directory / "artifact-manifest.sha256").write_text(manifest(directory))


@pytest.fixture(scope="module")
def consumed_recheck_attempt(tmp_path_factory):
    prepared = work.prepare_depot_recheck_candidate(
        tmp_path_factory.mktemp("recheck-consumed") / "candidate"
    )
    directory = prepared.directory
    seal = sha256(directory / "PRELAUNCH.json")
    metadata = json.loads((directory / "PRELAUNCH.json").read_text())
    exchanges, facts, funds = _consumed_recheck_exchange(seal, metadata)
    _fabricate_consumed_recheck_frames(directory, exchanges)
    phase = work.recheck_phase_outcome(
        exchanges,
        prelaunch_digest=seal,
        facts_of_record=facts,
        funds_of_record=funds,
    )
    assert phase["verification"] == "DEPOT_RELOAD_OBSERVED"
    assert phase["gate"]["verdict"] == "DEPOT_RELOAD_GATE_PASSES"
    _fabricate_consumed_recheck_records(directory, seal, phase, metadata, exchanges)
    yield directory, exchanges, seal
    prepared.spec.workspace.close()


def _consumed_for_tamper(consumed_recheck_attempt, tmp_path) -> Path:
    """A byte-for-byte clone of the consumed candidate for one refusal arm."""
    directory, _, _ = consumed_recheck_attempt
    clone = tmp_path / "recheck-tamper"
    if clone.exists():
        shutil.rmtree(clone)
    shutil.copytree(directory, clone)
    return clone


def test_replay_verifies_a_fully_consumed_recheck_frame_sequence(
    consumed_recheck_attempt, monkeypatch
):
    directory, exchanges, seal = consumed_recheck_attempt
    monkeypatch.setattr(work, "replay_authorization_state", lambda *a, **k: None)
    verdict = work.verify_depot_recheck_attempt(directory)
    assert verdict["verification"] == "DEPOT_RELOAD_FACTS_VERIFIED"
    assert verdict["receipt"]["phase"]["verification"] == "DEPOT_RELOAD_OBSERVED"
    assert verdict["receipt"]["phase"]["gate"]["verdict"] == "DEPOT_RELOAD_GATE_PASSES"
    assert verdict["facts"] == FACTS_OF_RECORD
    assert verdict["funds"] == FUNDS_OF_RECORD
    assert verdict["zero_mutation"]["mutated"] == []
    assert verdict["zero_mutation"]["state_changed"] is False
    assert verdict["zero_mutation"]["loaded_source_binding"] == (
        "staged record == run binding == retained round-2 after-save"
    )
    assert verdict["receipt"]["loaded_source_sha256"] == work.RECHECK_PREREQUISITE_AFTER_SAVE


def test_replay_refuses_an_unconsumed_recheck_candidate(consumed_recheck_attempt, tmp_path):
    directory = _consumed_for_tamper(consumed_recheck_attempt, tmp_path)
    (directory / "CLAIM.json").unlink()
    (directory / "artifact-manifest.sha256").write_text(manifest(directory))
    verdict = work.verify_depot_recheck_attempt(directory)
    assert verdict["verification"] == "AUTHORIZATION_UNVERIFIED"
    assert verdict["authorization_state"] == "CLAIM_ABSENT"


def test_replay_refuses_a_funds_drifted_recheck_response(
    consumed_recheck_attempt, tmp_path, monkeypatch
):
    directory = _consumed_for_tamper(consumed_recheck_attempt, tmp_path)
    body = json.loads((directory / "reload-00-response.json").read_text())
    body["funds"] = FUNDS_OF_RECORD - 1
    wire = json.dumps(body, separators=(",", ":")).encode()
    (directory / "reload-00-response.json").write_bytes(wire)
    _refab_frames(directory)
    (directory / "artifact-manifest.sha256").write_text(manifest(directory))
    monkeypatch.setattr(work, "replay_authorization_state", lambda *a, **k: None)
    with pytest.raises(ValueError, match="contradicts its recheck phase outcome"):
        work.verify_depot_recheck_attempt(directory)


def test_replay_refuses_a_divergent_recheck_fact(
    consumed_recheck_attempt, tmp_path, monkeypatch
):
    directory = _consumed_for_tamper(consumed_recheck_attempt, tmp_path)
    body = json.loads((directory / "reload-00-response.json").read_text())
    body["connected_front_to_depot"] = False
    wire = json.dumps(body, separators=(",", ":")).encode()
    (directory / "reload-00-response.json").write_bytes(wire)
    _refab_frames(directory)
    (directory / "artifact-manifest.sha256").write_text(manifest(directory))
    monkeypatch.setattr(work, "replay_authorization_state", lambda *a, **k: None)
    with pytest.raises(ValueError, match="contradicts its recheck phase outcome"):
        work.verify_depot_recheck_attempt(directory)


def test_replay_refuses_a_drifted_recheck_receipt(
    consumed_recheck_attempt, tmp_path, monkeypatch
):
    directory = _consumed_for_tamper(consumed_recheck_attempt, tmp_path)
    receipt = json.loads((directory / work.RECHECK_AFTER_RECEIPT_NAME).read_text())
    receipt["statement"] = "a relabelled statement of record"
    (directory / work.RECHECK_AFTER_RECEIPT_NAME).write_text(json.dumps(receipt) + "\n")
    (directory / "artifact-manifest.sha256").write_text(manifest(directory))
    monkeypatch.setattr(work, "replay_authorization_state", lambda *a, **k: None)
    with pytest.raises(ValueError, match="receipt drifted"):
        work.verify_depot_recheck_attempt(directory)


def test_replay_refuses_a_recheck_carrying_a_save_artifact(
    consumed_recheck_attempt, tmp_path, monkeypatch
):
    """The zero-save discipline: a save artifact in a consumed candidate
    contradicts the zero-mutation capsule itself and can never verify."""
    directory = _consumed_for_tamper(consumed_recheck_attempt, tmp_path)
    (directory / "after.sav").write_bytes(hashlib.sha256(b"synthetic").digest() * 100)
    (directory / "artifact-manifest.sha256").write_text(manifest(directory))
    monkeypatch.setattr(work, "replay_authorization_state", lambda *a, **k: None)
    with pytest.raises(ValueError, match="cannot carry after.sav"):
        work.verify_depot_recheck_attempt(directory)


def test_replay_preserves_a_halted_recheck_attempt(
    consumed_recheck_attempt, tmp_path, monkeypatch
):
    """A halt at the exchange leaves the phase incomplete forever: the
    halt record stands as preserved evidence, nothing is relabelled."""
    directory = _consumed_for_tamper(consumed_recheck_attempt, tmp_path)
    (directory / "reload-00-response.json").unlink()
    (directory / work.RECHECK_AFTER_RECEIPT_NAME).unlink()
    result = json.loads((directory / "result.json").read_text())
    result.update(
        status="PHASE_HALTED_PREFIX_PRESERVED",
        verified=False,
        command_accepted=False,
        requests=0,
        exchanges=[],
        state_changed=False,
        mutated=[],
        halt=dict(label="reload-00", error="TimeoutError: exchange budget"),
    )
    (directory / "result.json").write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    _refab_frames(directory, with_response=False)
    (directory / "artifact-manifest.sha256").write_text(manifest(directory))
    monkeypatch.setattr(work, "replay_authorization_state", lambda *a, **k: None)
    verdict = work.verify_depot_recheck_attempt(directory)
    assert verdict["verification"] == "PHASE_HALTED_EVIDENCE_PRESERVED"
    assert verdict["result_status"] == "PHASE_HALTED_PREFIX_PRESERVED"
    assert verdict["pending"] == ["reload-00"]
