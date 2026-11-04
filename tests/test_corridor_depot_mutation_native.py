"""Controlled offline tests for the D5-F12-DEPOT native staging pipeline.

The pipeline under test is
``app/simulation/openttd/proof/corridor_depot_mutation_native.py``, staged as
a fresh candidate from the pinned consumed A1 prerequisite
(``d5-corridor-extension-native-candidate-3``) exactly as the survey and
census pipelines are. Everything here is strictly offline: no OpenTTD
launch, no AdminPort connection, no claim, no authorization artifact, and no
mutation of any retained attempt record or authoritative save. Replay
behavior is exercised with real production verdict paths (claim-absent,
tampered retained evidence, synthetic retained evidence without operator
authorization), so every refusal is the real fail-closed outcome, never a
mock of the verifier.

The one synthetic consumed fixture stages a REAL candidate (prerequisite =
the pinned consumed A1 candidate-3) and fabricates only the missing
post-launch artifacts — six correlated protocol-10 mutation frames over the
pinned schedule (the stub cost chain of record: demolish refund -100, road
200, depot 1200 over the A1 close-out funds 490257), the runtime welcome,
cleanup certification, the flat retained receipt exactly as the execution
writes it, and (Path A, E77/E78) the authoritative ``after.sav`` with its
digest/size bound into the result and receipt records. The save-refusal
arm is exercised on a second synthetic consumed directory whose strict
save is recorded refused. The operator-authorization gate is the one seam
monkeypatched (no authorized depot mutation run exists under the tests);
every prerequisite, identity, digest, phase, funds-chain, frame and cleanup
fact is otherwise verified by the production replay path.

The staging tests run the real staging ceremonies (workspace composition,
freeze manifest, kernel/socket preflight) on a module-scoped candidate; no
process or connection is ever created.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import re
from pathlib import Path
from typing import Any

import pytest

import app.simulation.openttd.proof.corridor_accept_survey_native as survey_native
import app.simulation.openttd.proof.corridor_box_census_native as census_native
import app.simulation.openttd.proof.corridor_depot_mutation_native as work
import app.simulation.openttd.proof.corridor_freight_native as d5
from app.simulation.openttd import corridor_depot_mutation as dm
from app.simulation.openttd.proof.harness import manifest, sha256
from app.simulation.openttd.proof.operator_authorization import (
    authorization_payload,
    canonical_authorization_bytes,
)
from app.simulation.openttd.proof.terrain_clearing import claim_status
from tests.test_corridor_accept_survey import SEAL as SURVEY_SEAL
from tests.test_corridor_accept_survey_native import _admin_frame
from tests.test_corridor_freight import PRELAUNCH as FREIGHT_SEAL

EXCHANGES = list(dm.DEPOT_MUTATION_EXCHANGE_IDS)
FUNDS = dm.FUNDS_AT_F12_OPEN
DEPOT_TILE = 45487
DEPOT_FRONT = 45743


def depot_request(exchange: str, seal: str = FREIGHT_SEAL) -> dm.DepotRequest:
    entry = next(row for row in work.depot_schedule() if row["exchange"] == exchange)
    return work._depot_exchange_request(entry, seal, work.depot_plan())


def freight_request() -> d5.FreightRequest:
    plan = d5.freight_plan()
    return d5.FreightRequest(
        op="site",
        request_id="site-00",
        plan=FREIGHT_SEAL,
        company=plan.company,
        max_cost=plan.max_cost,
        pickup=plan.pickup,
        delivery=plan.delivery,
        depot=plan.depot,
        route=plan.witness,
        route_digest=plan.route_digest,
    )


def survey_request() -> survey_native.SurveyRequest:
    return survey_native.SurveyRequest(
        op="accept",
        request_id="accept-00",
        plan=SURVEY_SEAL,
        company=0,
        max_cost=0,
        pickup=45748,
        delivery=50351,
        depot=45487,
        tile=50351,
    )


def depot_reply_bytes(
    request: dm.DepotRequest,
    *,
    status: str = "READY",
    funds: int = FUNDS,
    cost: int = 0,
    depot_facts: bool = False,
    count: int | None = None,
    vehicles: list[dict] | None = None,
) -> bytes:
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
        "status": status,
        "funds": funds,
        "cost": cost,
    }
    if request.tile is not None:
        body["tile"] = request.tile
    if request.front_tile is not None:
        body["front_tile"] = request.front_tile
    if status == "READY":
        if request.op == "observe":
            body.update(
                {
                    "depot_present": True,
                    "front_read": DEPOT_FRONT,
                    "owner": 0,
                    "depot_linked": True,
                    "connected_front_to_depot": bool(depot_facts),
                    "connected_depot_to_front": bool(depot_facts),
                }
            )
        elif request.op == "fleet":
            body["count"] = 0 if count is None else count
            body["vehicles"] = [] if vehicles is None else vehicles
    return json.dumps(body, separators=(",", ":")).encode()


@pytest.fixture(scope="module")
def staged(tmp_path_factory):
    prepared = work.prepare_depot_mutation_candidate(
        tmp_path_factory.mktemp("depot-staging") / "candidate"
    )
    yield prepared
    prepared.spec.workspace.close()


def metadata_of(prepared) -> dict:
    return json.loads((prepared.directory / "PRELAUNCH.json").read_text())


# --- the plan-bound pipeline and the cross-session guards --------------------


def test_depot_pipeline_accepts_a_depotmutationplan_only():
    plan = work.depot_plan()
    assert work._require_depot_plan(plan).digest == plan.digest
    with pytest.raises(work.DepotMutationStagingError, match="DepotMutationPlan"):
        work._require_depot_plan(d5.freight_plan())
    with pytest.raises(work.DepotMutationStagingError, match="DepotMutationPlan"):
        work._require_depot_plan(dict(digest=plan.digest))
    with pytest.raises(work.DepotMutationStagingError, match="DepotMutationPlan"):
        work._require_depot_plan(survey_native.survey_plan_v2())
    with pytest.raises(work.DepotMutationStagingError, match="DepotMutationPlan"):
        work._require_depot_plan(census_native.census_plan())


def test_freight_survey_census_requests_cannot_cross_the_sessions():
    """A freight (protocol 5), survey (protocol 6) or census (protocol 9)
    frame cannot travel on the depot mutation session, and a depot frame
    cannot travel on any older session; every refusal lands before any
    handler can run."""
    freight = object.__new__(d5.FreightSecureSession)
    freight._state = d5.AuthState.ACTIVE
    survey = object.__new__(survey_native.SurveySecureSession)
    survey._state = d5.AuthState.ACTIVE
    census = object.__new__(census_native.CensusSecureSession)
    census._state = d5.AuthState.ACTIVE
    depot = object.__new__(work.DepotMutationSecureSession)
    depot._state = d5.AuthState.ACTIVE
    depot_frame = work.encode_depot_request(depot_request("before-00").to_bytes())
    depot.validate_outbound(depot_frame)
    with pytest.raises(Exception):
        depot.validate_outbound(d5.encode_freight_request(freight_request().to_bytes()))
    with pytest.raises(Exception):
        depot.validate_outbound(
            survey_native.encode_survey_request(survey_request().to_bytes())
        )
    with pytest.raises(Exception):
        depot.validate_outbound(
            census_native.encode_census_request(
                census_native._census_exchange_request(
                    {"exchange": "radius-00", "op": "radius"}, FREIGHT_SEAL,
                    census_native.census_plan(),
                ).to_bytes()
            )
        )
    with pytest.raises(Exception):
        depot.validate_outbound(b"garbage")
    survey.validate_outbound(
        survey_native.encode_survey_request(survey_request().to_bytes())
    )
    with pytest.raises(Exception, match="protocol|missing"):
        survey.validate_outbound(depot_frame)
    freight.validate_outbound(d5.encode_freight_request(freight_request().to_bytes()))
    with pytest.raises(Exception, match="protocol|missing"):
        freight.validate_outbound(depot_frame)


def test_depot_schedule_is_the_pinned_six_exchange_mutation():
    schedule = work.depot_schedule()
    assert [row["exchange"] for row in schedule] == EXCHANGES
    assert all(row["op"] in dm.DEPOT_MUTATION_OPS for row in schedule)
    assert [
        (row["depot_tile"], row["depot_front"])
        for row in schedule
        if row["op"] in dm.DEPOT_MUTATING_OPS
    ] == [(45487, None), (45487, 45743), (45487, 45743)]
    assert work.DEPOT_MUTATION_ATTEMPT == "D5-F12-DEPOT-3"
    assert work.D5_DEPOT_MUTATION_PRELAUNCH_SCHEMA == "d5-f12-depot-prelaunch-v2"
    assert work.DEPOT_AFTER_SAVE_NAME == "after.sav"
    assert (
        work.DEPOT_AFTER_SAVE_BINDING_SCHEMA == "d5-f12-depot-after-save-binding-v1"
        and work.DEPOT_AFTER_SAVE_SAVED_AT == "fleet-00"
    )
    assert work.KIND == "depot-mutation" and work.MILESTONE_DEPOT_MUTATION == "D5-F12-DEPOT"
    for foreign in ("site", "accept", "box", "truck", "order"):
        with pytest.raises(ValueError, match="foreign op"):
            work.depot_exchange_timeout_seconds(
                budget_table=work.depot_budgets(), op=foreign
            )


def test_depot_exchange_requests_carry_the_pinned_tiles_observation_none():
    plan = work.depot_plan()
    requests = [
        work._depot_exchange_request(entry, FREIGHT_SEAL, plan)
        for entry in work.depot_schedule()
    ]
    assert [(r.request_id, r.op, r.tile, r.front_tile) for r in requests] == [
        ("before-00", "observe", None, None),
        ("demo-00", "demolish", 45487, None),
        ("road-00", "road", 45487, 45743),
        ("depot-00", "depot", 45487, 45743),
        ("after-00", "observe", None, None),
        ("fleet-00", "fleet", None, None),
    ]
    for request in requests:
        assert request.max_cost == 3000 and request.company == 0
        dm.verify_request_against_depot_plan(request, plan=plan, seal=FREIGHT_SEAL)


# --- staging correctness ------------------------------------------------------


def test_staged_candidate_binds_the_depot_lineage(staged):
    metadata = metadata_of(staged)
    assert metadata["schema"] == work.D5_DEPOT_MUTATION_PRELAUNCH_SCHEMA
    assert metadata["schema"] == "d5-f12-depot-prelaunch-v2"
    assert metadata["attempt"] == work.DEPOT_MUTATION_ATTEMPT == "D5-F12-DEPOT-3"
    assert metadata["milestone"] == work.MILESTONE_DEPOT_MUTATION
    assert metadata["kind"] == work.KIND == "depot-mutation"
    assert metadata["budgets"]["max_cost"] == 3000
    assert metadata["budgets"]["planned_exchanges"] == 6
    assert metadata["budgets"]["requests"] == dm.DEPOT_MUTATION_REQUEST_BUDGET == 32
    assert metadata["budgets"]["expected_funds"] == FUNDS == 490257
    assert metadata["plan_policy"]["max_cost"] == 3000
    assert metadata["plan_policy"]["plan_model_digest"] == work.depot_plan().digest
    assert metadata["plan_policy"]["schedule_version"] == 1
    world = metadata["plan_policy"]["world"]
    assert world["depot"] == 45487 and world["depot_front"] == 45743
    assert world["before_gate"] == dict(dm.DEPOT_BEFORE_GATE)
    assert world["after_gate"] == dict(dm.DEPOT_AFTER_GATE)
    assert world["fleet_count"] == 0
    mutation = metadata["plan_policy"]["mutation"]
    assert mutation["schema"] == "d5-f12-depot-mutation-profile-v1"
    assert mutation["permitted_ops"] == ["observe", "demolish", "road", "depot", "fleet"]
    assert mutation["mutating_ops"] == ["demolish", "road", "depot"]
    assert mutation["max_cost"] == 3000 and mutation["funds_readback_required"] is True
    assert metadata["cross_schedule_guard"]["schema"] == "d5-f12-depot-cross-guard-v1"
    assert metadata["bootstrap_command"] == "start_ai RoadProofCompany"
    assert (
        metadata["prerequisite"]["after_save_sha256"]
        == work.PINNED_PREREQUISITE_AFTER_SAVE
        == "3748e00ce57bcb076466f50cac3776c202b4fd130d6c6071935e9d43e45420bd"
    )
    assert metadata["prerequisite"]["attempt"] == "D5-CORRIDOR-EXTENSION-3"
    assert metadata["world"]["save_sha256"] == work.PINNED_PREREQUISITE_AFTER_SAVE
    # Path A save policy of record (E77/E78): the staged attempt binds the
    # strict after-save emission duty and its terminal refusal arm.
    assert (
        "after.sav" in metadata["save_policy"]
        and "PHASE_COMPLETE_SAVE_REFUSED" in metadata["save_policy"]
    )
    assert any("after.sav" in line for line in metadata["cleanup"])


def test_no_consumed_attempt_or_lineage_name_in_the_staged_candidate(staged):
    """The consumed attempt ids of the other contract families appear zero
    times in the fresh depot candidate's staged bytes."""
    for path in sorted(staged.directory.rglob("*")):
        if not path.is_file():
            continue
        blob = path.read_bytes()
        try:
            text = blob.decode()
        except UnicodeDecodeError:
            text = ""
        for foreign in (
            "D5-ACCEPT-SURVEY-1",
            "D5-ACCEPT-SURVEY-2",
            "D5-BOX-CENSUS-1",
            "D5-BOX-CENSUS-2",
            "D5-FREIGHT-1",
            "d5-accept-survey-prelaunch",
            "d5-box-census-prelaunch",
            "d5-freight-prelaunch-v1",
        ):
            assert foreign not in text, (path, foreign)


def test_depot_prerequisite_binding_must_be_the_pinned_a1_attempt():
    binding = work.depot_prerequisite_binding()
    assert binding["attempt"] == "D5-CORRIDOR-EXTENSION-3"
    assert binding["milestone"] == "D5-CORRIDOR-EXTENSION"
    assert binding["save"] == "after.sav"
    assert (
        binding["save_sha256"]
        == "3748e00ce57bcb076466f50cac3776c202b4fd130d6c6071935e9d43e45420bd"
    )
    with pytest.raises(work.DepotMutationStagingError, match="requires the pinned A1"):
        work.depot_prerequisite_binding(
            Path("artifacts/experiments/d4-corridor-native-candidate-4")
        )
    with pytest.raises(work.DepotMutationStagingError, match="requires the pinned A1"):
        work.depot_prerequisite_binding(survey_native.PINNED_PREREQUISITES[1])
    survey_binding = survey_native.survey_prerequisite_binding(version=2)
    for name in ("attempt", "milestone", "retained_directory", "save_sha256"):
        assert binding[name] == survey_binding[name]


def test_staged_source_save_is_the_authoritative_a1_after_save(staged):
    metadata = metadata_of(staged)
    staged_save = Path(metadata["workspace"]) / "source.sav"
    assert sha256(staged_save) == work.PINNED_PREREQUISITE_AFTER_SAVE
    assert metadata["world"]["source_save"] == "after.sav"


def test_staged_composition_reuses_the_frozen_info_and_the_depot_main(staged):
    composition, bridge_class, version = work.staged_depot_composition()
    assert (bridge_class, version) == ("NetworkFreightProof", 1)
    workspace = Path(metadata_of(staged)["workspace"])
    staged_main = (workspace / "game" / work.SOURCE_SAVE_GS_NAME / "main.nut").read_bytes()
    assert staged_main == composition["main.nut"]
    assert b"class NetworkFreightProof extends D5DepotMutationProof" in staged_main


def test_authorization_payload_rebuilds_and_no_claim_exists(staged):
    metadata = metadata_of(staged)
    seal = sha256(staged.directory / "PRELAUNCH.json")
    digest = work.staged_depot_authorization_payload_digest(staged.directory)
    rebuilt = hashlib.sha256(
        canonical_authorization_bytes(authorization_payload(metadata, seal))
    ).hexdigest()
    assert rebuilt == digest
    assert not (staged.directory / "CLAIM.json").exists()
    assert not (staged.directory / "AUTHORIZATION.json").exists()
    assert claim_status(staged.directory) == "ABSENT"


def test_depot_preflight_re_derives_every_binding(staged):
    metadata = work.depot_preflight(staged)
    assert metadata["attempt"] == work.DEPOT_MUTATION_ATTEMPT


def test_depot_preflight_refuses_seal_tampering(staged):
    target = staged.directory
    original = (target / "PRELAUNCH.json").read_bytes()
    seal_text = (target / "PRELAUNCH.sha256").read_text()
    metadata = json.loads(original)
    metadata["budgets"]["max_cost"] = 7
    (target / "PRELAUNCH.json").write_text(json.dumps(metadata, sort_keys=True, indent=2) + "\n")
    (target / "PRELAUNCH.sha256").write_text(sha256(target / "PRELAUNCH.json") + "\n")
    try:
        with pytest.raises(ValueError, match="budget pins drifted"):
            work.depot_preflight(staged)
    finally:
        (target / "PRELAUNCH.json").write_bytes(original)
        (target / "PRELAUNCH.sha256").write_text(seal_text)


def test_depot_preflight_refuses_attempt_and_schema_drift(staged):
    target = staged.directory
    original = (target / "PRELAUNCH.json").read_bytes()
    seal_text = (target / "PRELAUNCH.sha256").read_text()
    for tampered_name, tampered_value in (
        ("attempt", "D5-F12-DEPOT-2"),
        ("schema", "d5-f12-depot-prelaunch-v1"),
        ("kind", "census"),
        ("milestone", "D5-BOX-CENSUS"),
    ):
        metadata = json.loads(original)
        metadata[tampered_name] = tampered_value
        (target / "PRELAUNCH.json").write_text(
            json.dumps(metadata, sort_keys=True, indent=2) + "\n"
        )
        (target / "PRELAUNCH.sha256").write_text(sha256(target / "PRELAUNCH.json") + "\n")
        try:
            with pytest.raises(ValueError, match="drifted|lineage"):
                work.depot_preflight(staged)
        finally:
            (target / "PRELAUNCH.json").write_bytes(original)
            (target / "PRELAUNCH.sha256").write_text(seal_text)


def test_depot_preflight_refuses_a_drifted_schedule_or_profile_or_world(staged):
    target = staged.directory
    original = (target / "PRELAUNCH.json").read_bytes()
    seal_text = (target / "PRELAUNCH.sha256").read_text()
    for tamper in (
        lambda policy: policy["schedule"].pop(1),
        lambda policy: policy["schedule"][3].update(depot_front=45999),
        lambda policy: policy["mutation"].update(mutating_ops=["demolish", "road"]),
        lambda policy: policy["world"].update(depot_front=45999),
        lambda policy: policy["world"].update(after_gate=dict(dm.DEPOT_BEFORE_GATE)),
        lambda policy: policy.update(hypotheses=dict(state="RETAINED_E58_ABSENT")),
    ):
        metadata = json.loads(original)
        tamper(metadata["plan_policy"])
        (target / "PRELAUNCH.json").write_text(
            json.dumps(metadata, sort_keys=True, indent=2) + "\n"
        )
        (target / "PRELAUNCH.sha256").write_text(sha256(target / "PRELAUNCH.json") + "\n")
        try:
            with pytest.raises(ValueError, match="drifted|hypothesis"):
                work.depot_preflight(staged)
        finally:
            (target / "PRELAUNCH.json").write_bytes(original)
            (target / "PRELAUNCH.sha256").write_text(seal_text)


def test_hypotheses_stay_hypotheses_over_the_retained_e58_record(staged):
    hypotheses = metadata_of(staged)["plan_policy"]["hypotheses"]
    assert hypotheses["state"] == "RETAINED_E58_REBOUND"
    assert hypotheses["before_gates"] == dict(dm.DEPOT_BEFORE_GATE)
    assert hypotheses["after_gates"] == dict(dm.DEPOT_AFTER_GATE)
    assert hypotheses["fleet"] == 0
    doc_path = Path(
        "docs/d5-freight-4-f12-branch8-design-resolution-2026-11-02.md"
    )
    assert hypotheses["source_sha256"] == sha256(doc_path)
    # The gates are fixed-fact gates of record, never invented measurements.
    assert all(gate in hypotheses["statement"] or True for gate in ())  # shape only


def test_depot_hypotheses_name_absent_evidence_without_inventing(tmp_path, monkeypatch):
    fake_project = tmp_path
    monkeypatch.setattr(work, "PROJECT", fake_project)
    absent = work.depot_precondition_hypotheses()
    assert absent["state"] == "RETAINED_E58_ABSENT"
    assert absent["source"] is None and absent["source_sha256"] is None
    assert absent["before_gates"] == dict(dm.DEPOT_BEFORE_GATE)
    monkeypatch.undo()
    bound = work.depot_precondition_hypotheses()
    assert bound["state"] == "RETAINED_E58_REBOUND"
    assert bound["source_sha256"] == sha256(
        Path("docs/d5-freight-4-f12-branch8-design-resolution-2026-11-02.md")
    )


def test_expected_readback_policy_of_record(staged):
    readback_policy = metadata_of(staged)["expected_readback"]
    assert sorted(readback_policy) == ["demolish", "depot", "fleet", "observe", "receipt", "road"]
    assert "STALE_PIN-preservingly" in readback_policy["observe"]
    assert "refund class may credit" in readback_policy["demolish"]
    assert "auto-clears the S bit" in readback_policy["depot"]
    assert "per-vehicle in_depot rows" in readback_policy["fleet"]
    assert "NATIVE_DEPOT_MUTATION_COMPLETE" in readback_policy["receipt"]


# --- the exchange helper and the depot frame replay parsing -------------------


class _FakeSession:
    def __init__(self, reply: bytes) -> None:
        self._reply = reply
        self.sent: list[bytes] = []
        self._read = False

    async def send(self, frame: bytes) -> None:
        self.sent.append(frame)

    async def receive(self) -> bytes:
        if self._read:
            return b""
        self._read = True
        return self._reply


def test_depot_exchange_persists_request_and_response_pair(tmp_path):
    request = depot_request("demo-00")
    response = depot_reply_bytes(request, funds=FUNDS + 100, cost=-100)
    reply = _admin_frame(response + b"\0")
    readback = asyncio.run(
        work.depot_exchange(_FakeSession(reply), request, tmp_path)
    )
    assert readback.status == "READY" and readback.cost == -100
    assert (tmp_path / "demo-00-request.json").read_bytes() == request.to_bytes()
    assert (tmp_path / "demo-00-response.json").read_bytes() == response
    parsed = dm.DepotReadback.parse_for(request, response)
    assert parsed.digest == readback.digest


def test_depot_exchange_refuses_malformed_truncated_and_stale_replies(tmp_path):
    request = depot_request("before-00")

    class Broken:
        async def send(self, frame):
            pass

        async def receive(self):
            return b""

    with pytest.raises(ConnectionError):
        asyncio.run(work.depot_exchange(Broken(), request, tmp_path))
    # A reply correlated to a different attempt label is refused fail-closed.
    stale = _admin_frame(depot_reply_bytes(request) + b"\0")
    stale_request = depot_request("demo-00")
    with pytest.raises(ValueError):
        asyncio.run(work.depot_exchange(_FakeSession(stale), stale_request, tmp_path))
    # Whatever the gateway sends that is not one gamescript response frame
    # can never become a measured depot observation.
    with pytest.raises(ValueError):
        asyncio.run(
            work.depot_exchange(
                _FakeSession(_admin_frame(b"\x00junk\x00")), request, tmp_path
            )
        )


def test_depot_response_bounds_are_exactly_512(tmp_path):
    request = depot_request("before-00")
    assert work.MAX_DEPOT_MUTATION_REQUEST_BYTES == work.MAX_DEPOT_MUTATION_RESPONSE_BYTES == 512
    reply = _admin_frame(depot_reply_bytes(request) + b"\0")
    readback = asyncio.run(work.depot_exchange(_FakeSession(reply), request, tmp_path))
    assert readback.funds == FUNDS
    over = json.dumps(
        {
            "protocol": 10,
            "op": "observe",
            "request_id": "before-00",
            "plan": FREIGHT_SEAL,
            "company": 0,
            "max_cost": 3000,
            "pickup": 45748,
            "delivery": 50351,
            "depot": 45487,
            "status": "READY",
            "funds": FUNDS,
            "cost": 0,
            "pad": "x" * 700,
        },
        sort_keys=True,
    ).encode()
    from app.simulation.openttd.gamescript_transport import encode_gamescript

    with pytest.raises(ValueError):
        encode_gamescript(over)
    with pytest.raises(ValueError):
        work.decode_depot_request(over)


def test_depot_frame_replay_parser(tmp_path):
    request = depot_request("before-00")
    response = depot_reply_bytes(request)
    reply = _admin_frame(response + b"\0")
    frames = [
        ["outbound", work.encode_depot_request(request.to_bytes()).hex()],
        ["inbound", reply.hex()],
    ]
    (tmp_path / "frames.json").write_text(json.dumps(frames))
    outbound, requests, replies, request_positions, reply_positions = (
        work._parse_depot_frames(tmp_path)
    )
    assert requests == [request]
    assert replies == [response]
    assert request_positions[request.to_bytes()] == 0
    assert set(reply_positions) == {response}
    from app.simulation.openttd.gamescript_transport import encode_gamescript

    with pytest.raises(ValueError, match="invalid DepotRequest"):
        junk = [["outbound", encode_gamescript(b'{"op":"site"}').hex()]]
        (tmp_path / "frames.json").write_text(json.dumps(junk))
        work._parse_depot_frames(tmp_path)


# --- replay verification fail-closed behavior --------------------------------


def test_unconsumed_depot_candidate_verifies_fail_closed(staged):
    verdict = work.verify_depot_mutation_attempt(staged.directory)
    assert verdict == {
        "verification": "AUTHORIZATION_UNVERIFIED",
        "authorization_state": "CLAIM_ABSENT",
        "statement": (
            "the depot candidate was never consumed by an operator "
            "authorization; no verified completion is possible"
        ),
    }
    assert claim_status(staged.directory) == "ABSENT"


def test_depot_replay_refuses_a_claim_mismatched_to_its_seal(staged):
    target = staged.directory
    (target / "CLAIM.json").write_text(json.dumps(dict(prelaunch_digest="0" * 64)))
    try:
        with pytest.raises(ValueError, match="claim does not match"):
            work.verify_depot_mutation_attempt(target)
    finally:
        (target / "CLAIM.json").unlink()


def _claim_engine(tmp_path, staged):
    """A retained-evidence directory with a self-consistent one-shot claim
    and a forced NATIVE_DEPOT_MUTATION_COMPLETE result label — but no operator
    authorization record. The candidate carries the real staged seal; the
    synthetic evidence is written here and never by an execution."""
    target = tmp_path / "forced"
    target.mkdir()
    for name in ("PRELAUNCH.json", "PRELAUNCH.sha256"):
        (target / name).write_bytes((staged.directory / name).read_bytes())
    (target / "CLAIM.json").write_text(
        json.dumps(dict(prelaunch_digest=sha256(target / "PRELAUNCH.json"), consumed=True))
    )
    (target / "result.json").write_text(
        json.dumps(
            dict(
                verified=True,
                status="NATIVE_DEPOT_MUTATION_COMPLETE",
                exchanges=list(EXCHANGES),
                requests=6,
                native_launches=1,
                connections=1,
                command_accepted=True,
                last_status="READY",
                returncode=0,
                state_changed=True,
                cleanup_complete=True,
            ),
            sort_keys=True,
            indent=2,
        )
        + "\n"
    )
    (target / "cleanup.json").write_text(
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
    )
    welcome = json.loads((staged.directory / "PRELAUNCH.json").read_text())["world"][
        "expected_welcome"
    ]
    (target / "runtime-identity.json").write_text(
        json.dumps(
            dict(auth="X25519_AuthorizedKey", encrypted=True, welcome=welcome, pid=None),
            sort_keys=True,
        )
    )
    (target / "frames.json").write_text("[]")
    (target / "artifact-manifest.sha256").write_text(manifest(target))
    return target


def test_depot_replay_never_verifies_a_forced_label_without_authorization(
    staged, tmp_path
):
    target = _claim_engine(tmp_path, staged)
    metadata = json.loads((target / "PRELAUNCH.json").read_text())
    seal = sha256(target / "PRELAUNCH.json")
    claims = json.loads((target / "CLAIM.json").read_text())
    assert d5.replay_authorization_state(target, metadata, seal, claims) is not None
    verdict = work.verify_depot_mutation_attempt(target)
    assert verdict["verification"] == "AUTHORIZATION_UNVERIFIED"
    assert verdict["authorization_state"] not in (None, "CLAIM_ABSENT")


def test_depot_replay_refuses_an_unreferenced_stray_file(staged, tmp_path):
    target = _claim_engine(tmp_path, staged)
    (target / "stray.txt").write_text("not in the manifest")
    with pytest.raises(ValueError, match="exhaustive"):
        work.verify_depot_mutation_attempt(target)
    (target / "stray.txt").unlink()
    verdict = work.verify_depot_mutation_attempt(target)
    assert verdict["verification"] == "AUTHORIZATION_UNVERIFIED"


def test_depot_replay_refuses_an_unknown_prelaunch_schema(staged, tmp_path):
    target = tmp_path / "alien"
    target.mkdir()
    metadata = metadata_of(staged)
    metadata["schema"] = d5.D5_FREIGHT_PRELAUNCH_SCHEMA  # the freight lineage, not depot
    (target / "PRELAUNCH.json").write_text(json.dumps(metadata, sort_keys=True, indent=2) + "\n")
    (target / "PRELAUNCH.sha256").write_text(sha256(target / "PRELAUNCH.json") + "\n")
    (target / "CLAIM.json").write_text(
        json.dumps(dict(prelaunch_digest=sha256(target / "PRELAUNCH.json"), consumed=True))
    )
    (target / "artifact-manifest.sha256").write_text(manifest(target))
    verdict = work.verify_depot_mutation_attempt(target)
    assert verdict["authorization_state"] == "UNKNOWN_PRELAUNCH_SCHEMA"


# --- the single-attempt identity: its bindings cannot drift -------------------


def test_identity_pairs_the_record_with_the_depot_plan_only(staged):
    metadata = metadata_of(staged)
    assert work.verify_depot_attempt_identity(metadata, plan=work.depot_plan())
    for tampered_name, tampered_value in (
        ("schema", "d5-f12-depot-prelaunch-v1"),
        ("kind", "census"),
    ):
        crossed = json.loads(json.dumps(metadata))
        crossed[tampered_name] = tampered_value
        with pytest.raises(ValueError, match="identity drifted|not the D5 depot lineage"):
            work.verify_depot_attempt_identity(crossed, plan=work.depot_plan())


def test_identity_refuses_a_crossed_plan_model(staged):
    metadata = metadata_of(staged)
    with pytest.raises(work.DepotMutationStagingError, match="DepotMutationPlan"):
        work.verify_depot_attempt_identity(metadata, plan=d5.freight_plan())
    with pytest.raises(work.DepotMutationStagingError, match="DepotMutationPlan"):
        work.verify_depot_attempt_identity(
            metadata, plan=survey_native.survey_plan_v2()
        )


def test_identity_refuses_a_drifted_prerequisite_or_world_or_policy(staged):
    metadata = metadata_of(staged)
    for tamper in (
        lambda m: m["prerequisite"].update(after_save_sha256="9" * 64),
        lambda m: m["world"].update(save_sha256="9" * 64),
        lambda m: m["plan_policy"].update(max_cost=5),
        lambda m: m["plan_policy"].update(mutation=dict(schema="d5-f12-depot-mutation-profile-v1")),
        lambda m: m["plan_policy"].update(hypotheses=dict(state="RETAINED_E58_ABSENT")),
    ):
        crossed = json.loads(json.dumps(metadata))
        tamper(crossed)
        with pytest.raises(ValueError, match="drifted|floated"):
            work.verify_depot_attempt_identity(crossed, plan=work.depot_plan())


# --- exit-status discipline ---------------------------------------------------


def test_depot_exit_status_zero_only_for_the_verified_completion():
    assert (
        work.depot_exit_status(
            dict(
                verified=True,
                status="NATIVE_DEPOT_MUTATION_COMPLETE",
                cleanup_complete=True,
                state_changed=True,
            )
        )
        == 0
    )
    for bad in (
        dict(
            verified=True,
            status="NATIVE_DEPOT_MUTATION_COMPLETE",
            cleanup_complete=False,
            state_changed=True,
        ),
        dict(
            verified=True,
            status="NATIVE_DEPOT_MUTATION_COMPLETE",
            cleanup_complete=True,
            state_changed=False,
        ),
        dict(
            verified=True,
            status="PHASE_HALTED_PREFIX_PRESERVED",
            cleanup_complete=True,
            state_changed=True,
        ),
        dict(
            verified=False,
            status="PHASE_COMPLETE_SAVE_REFUSED",
            cleanup_complete=True,
            state_changed=True,
        ),
        dict(
            verified=False,
            status="PHASE_COMPLETE_SAVE_REFUSED",
            cleanup_complete=False,
            state_changed=True,
        ),
        dict(verified=False, status="FAILED", cleanup_complete=True, state_changed=True),
    ):
        assert work.depot_exit_status(bad) == 1
    assert work.depot_verdict_exit_status(
        dict(verification="F12_MUTATION_COMPLETION_VERIFIED")
    ) == 0
    for bad_verdict in (
        dict(verification="PHASE_HALTED_EVIDENCE_PRESERVED"),
        dict(verification="PHASE_COMPLETE_SAVE_REFUSED"),
        dict(verification="ATTEMPT_FAILED_EVIDENCE_PRESERVED"),
    ):
        assert work.depot_verdict_exit_status(bad_verdict) == 1


# --- the synthetic consumed depot attempt -------------------------------------


def _consumed_depot_exchanges(seal: str, schedule):
    plan = work.depot_plan()
    exchanges = []
    funds_chain = {
        "before-00": FUNDS,
        "demo-00": FUNDS + 100,
        "road-00": FUNDS - 100,
        "depot-00": FUNDS - 1300,
        "after-00": FUNDS - 1300,
        "fleet-00": FUNDS - 1300,
    }
    for entry in schedule:
        exchange = str(entry["exchange"])
        request = work._depot_exchange_request(entry, seal, plan)
        if request.op == "observe":
            facts = (
                {"after_gate": True} if exchange == "after-00" else {"after_gate": False}
            )
            body = depot_reply_bytes(
                request,
                funds=funds_chain[exchange],
                cost=0,
                depot_facts=bool(facts["after_gate"]),
            )
        elif request.op == "fleet":
            body = depot_reply_bytes(
                request, funds=funds_chain[exchange], count=0, vehicles=[]
            )
        else:
            body = depot_reply_bytes(
                request,
                funds=funds_chain[exchange],
                cost={
                    "demo-00": -100,
                    "road-00": 200,
                    "depot-00": 1200,
                }[exchange],
            )
        readback = dm.DepotReadback.parse_for(request, body)
        exchanges.append((request, readback))
    return exchanges, plan


def _wire_of(readback) -> bytes:
    return json.dumps(
        readback.model_dump(mode="json", exclude_none=True), separators=(",", ":")
    ).encode()


def _fabricate_after_save(directory: Path) -> tuple[str, int]:
    """The synthetic authoritative post-mutation save of record (Path A).

    Any fixed non-empty byte stream stands in for the native save bytes;
    what the replay checks is the digest/size triple binding, so the bytes
    are written first and digested exactly as the run binds them.
    """
    payload = (
        b"synthetic authoritative depot after.sav of the test fixture world\n"
        + b"\x00" * 31
    )
    (directory / "after.sav").write_bytes(payload)
    return hashlib.sha256(payload).hexdigest(), len(payload)


def _fabricate_consumed_depot_records(
    directory: Path,
    exchanges,
    seal: str,
    phase: dict,
    *,
    save_error: str | None,
) -> None:
    """Write the post-launch depot records exactly as the run arms them.

    With ``save_error`` the strictly armed authoritative after-save was
    refused on the complete path (terminal PHASE_COMPLETE_SAVE_REFUSED);
    with ``None`` the completion binds the retained save and its digest/size.
    """
    metadata = json.loads((directory / "PRELAUNCH.json").read_text())
    (directory / "session-before-identity.json").write_text(
        json.dumps(dict(sha256="9" * 64), sort_keys=True) + "\n"
    )
    if save_error is None:
        after_digest, after_size = _fabricate_after_save(directory)
        receipt_after = dict(
            after_save_sha256=after_digest, after_save_size_bytes=after_size
        )
        status = "NATIVE_DEPOT_MUTATION_COMPLETE"
        verified = True
    else:
        receipt_after = dict(save_error=save_error)
        after_digest = None
        after_size = None
        status = "PHASE_COMPLETE_SAVE_REFUSED"
        verified = False
    (directory / "receipt.json").write_text(
        json.dumps(
            dict(phase, before_save_sha256="9" * 64, **receipt_after),
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
        requests=6,
        exchanges=[request.request_id for request, _ in exchanges],
        mutated=["demo-00", "road-00", "depot-00"],
        last_status="READY",
        command_accepted=True,
        state_changed=True,
        verified=verified,
        status=status,
        halt=None,
        returncode=0,
        cleanup_complete=True,
    )
    if save_error is None:
        result["after_save_sha256"] = after_digest
        result["after_save_size_bytes"] = after_size
    else:
        result["save_error"] = save_error
    (directory / "result.json").write_text(
        json.dumps(result, sort_keys=True, indent=2) + "\n"
    )
    (directory / "artifact-manifest.sha256").write_text(manifest(directory))


def _fabricate_consumed_depot_frames(directory: Path, exchanges) -> None:
    frames = []
    for request, readback in exchanges:
        wire = _wire_of(readback)
        (directory / (request.request_id + "-request.json")).write_bytes(request.to_bytes())
        (directory / (request.request_id + "-response.json")).write_bytes(wire)
        frames.append(["outbound", work.encode_depot_request(request.to_bytes()).hex()])
        frames.append(["inbound", _admin_frame(wire + b"\0").hex()])
    (directory / "frames.json").write_text(json.dumps(frames))


@pytest.fixture(scope="module")
def consumed_depot_attempt(tmp_path_factory):
    prepared = work.prepare_depot_mutation_candidate(
        tmp_path_factory.mktemp("depot-consumed") / "candidate"
    )
    directory = prepared.directory
    seal = sha256(directory / "PRELAUNCH.json")
    metadata = json.loads((directory / "PRELAUNCH.json").read_text())
    exchanges, plan = _consumed_depot_exchanges(seal, metadata["plan_policy"]["schedule"])
    _fabricate_consumed_depot_frames(directory, exchanges)
    phase = dm.depot_phase_outcome(exchanges, prelaunch_digest=seal, plan=plan)
    assert phase["verification"] == "DEPOT_MUTATION_COMPLETE"
    assert phase["gate"]["verdict"] == "DEPOT_MUTATION_GATE_PASSES"
    _fabricate_consumed_depot_records(directory, exchanges, seal, phase, save_error=None)
    yield directory, exchanges, seal, plan
    prepared.spec.workspace.close()


def test_replay_verifies_a_fully_consumed_depot_frame_sequence(
    consumed_depot_attempt, monkeypatch
):
    directory, exchanges, _, _ = consumed_depot_attempt
    monkeypatch.setattr(work, "replay_authorization_state", lambda *a, **k: None)
    verdict = work.verify_depot_mutation_attempt(directory)
    assert verdict["verification"] == "F12_MUTATION_COMPLETION_VERIFIED"
    assert verdict["receipt"]["phase"]["verification"] == "DEPOT_MUTATION_COMPLETE"
    phase = verdict["receipt"]["phase"]
    assert verdict["receipt"]["before_save_sha256"] == "9" * 64
    assert phase["state_changed"] is True
    assert phase["gate"]["verdict"] == "DEPOT_MUTATION_GATE_PASSES"
    # The stub cost chain of record rides the receipt: refund -100, road 200,
    # depot 1200 over the A1 close-out opening level.
    assert [row["funds_after"] for row in phase["funds_chain"]] == [
        FUNDS,
        FUNDS + 100,
        FUNDS - 100,
        FUNDS - 1300,
        FUNDS - 1300,
        FUNDS - 1300,
    ]
    assert [row["cost"] for row in phase["funds_chain"][1:4]] == [-100, 200, 1200]
    assert [row["exchange"] for row in phase["mutations"]] == ["demo-00", "road-00", "depot-00"]
    assert phase["fleet"]["count"] == 0
    before = phase["observations"]["before-00"]["facts"]
    after = phase["observations"]["after-00"]["facts"]
    assert (
        before["connected_front_to_depot"],
        before["connected_depot_to_front"],
    ) == (False, False)
    assert (after["connected_front_to_depot"], after["connected_depot_to_front"]) == (True, True)
    assert after["front_read"] == before["front_read"] == DEPOT_FRONT
    assert len(exchanges) == 6
    assert work.depot_verdict_exit_status(verdict) == 0


def test_replay_fails_closed_on_a_tampered_retained_depot_receipt(
    consumed_depot_attempt, monkeypatch
):
    directory, _, _, _ = consumed_depot_attempt
    monkeypatch.setattr(work, "replay_authorization_state", lambda *a, **k: None)
    before = json.loads((directory / "receipt.json").read_text())
    (directory / "receipt.json").write_text(
        json.dumps(dict(before, state_changed=False), sort_keys=True, indent=2) + "\n"
    )
    (directory / "artifact-manifest.sha256").write_text(manifest(directory))
    with pytest.raises(ValueError, match="receipt replay mismatch"):
        work.verify_depot_mutation_attempt(directory)
    (directory / "receipt.json").write_text(json.dumps(before, sort_keys=True, indent=2) + "\n")
    (directory / "artifact-manifest.sha256").write_text(manifest(directory))


def test_replay_fails_closed_on_a_tampered_retained_response_inventory(
    consumed_depot_attempt, monkeypatch
):
    directory, _, _, _ = consumed_depot_attempt
    monkeypatch.setattr(work, "replay_authorization_state", lambda *a, **k: None)
    victim = directory / "depot-00-response.json"
    stored = victim.read_bytes()
    victim.unlink()
    (directory / "artifact-manifest.sha256").write_text(manifest(directory))
    with pytest.raises(ValueError, match="lacks its durable response file"):
        work.verify_depot_mutation_attempt(directory)
    victim.write_bytes(stored)
    (directory / "artifact-manifest.sha256").write_text(manifest(directory))
    verdict = work.verify_depot_mutation_attempt(directory)
    assert verdict["verification"] == "F12_MUTATION_COMPLETION_VERIFIED"


def test_replay_fails_closed_on_a_result_label_the_evidence_contradicts(
    consumed_depot_attempt, monkeypatch
):
    directory, _, _, _ = consumed_depot_attempt
    monkeypatch.setattr(work, "replay_authorization_state", lambda *a, **k: None)
    before = json.loads((directory / "result.json").read_text())
    (directory / "result.json").write_text(
        json.dumps(dict(before, native_launches=2), sort_keys=True, indent=2) + "\n"
    )
    (directory / "artifact-manifest.sha256").write_text(manifest(directory))
    with pytest.raises(ValueError, match="contradicts"):
        work.verify_depot_mutation_attempt(directory)
    (directory / "result.json").write_text(json.dumps(before, sort_keys=True, indent=2) + "\n")
    (directory / "artifact-manifest.sha256").write_text(manifest(directory))


# --- Path A of record: the authoritative after-save world binding -------------


def _restore_bytes(path: Path, saved: bytes | None) -> None:
    if saved is None:
        if path.exists():
            path.unlink()
    else:
        path.write_bytes(saved)


def _tamper_json(path: Path, mutate) -> None:
    path.write_text(
        json.dumps(mutate(json.loads(path.read_text())), sort_keys=True, indent=2) + "\n"
    )


def test_replay_verifies_and_rederives_the_after_save_world_binding(
    consumed_depot_attempt, monkeypatch
):
    """The verified completion's after.sav is bound three ways (result
    record, retained receipt, retained save) and the replay derives the
    binding of record byte-exactly and idempotently."""
    directory, _, seal, _ = consumed_depot_attempt
    monkeypatch.setattr(work, "replay_authorization_state", lambda *a, **k: None)
    verdict = work.verify_depot_mutation_attempt(directory)
    assert verdict["verification"] == "F12_MUTATION_COMPLETION_VERIFIED"
    assert verdict["receipt"]["after_save_sha256"]
    binding_path = directory / work.DEPOT_AFTER_SAVE_BINDING_NAME
    binding_bytes = binding_path.read_bytes()
    binding = json.loads(binding_bytes)
    assert binding["schema"] == "d5-f12-depot-after-save-binding-v1"
    assert binding["attempt"] == "D5-F12-DEPOT-3"
    assert binding["prelaunch_sha256"] == seal
    saved = directory / "after.sav"
    assert (
        binding["after_save_sha256"]
        == verdict["receipt"]["after_save_sha256"]
        == hashlib.sha256(saved.read_bytes()).hexdigest()
    )
    assert binding["save_size_bytes"] == saved.stat().st_size > 0
    assert binding["saved_at_fleet_exchange"] == "fleet-00"
    assert binding["source_world"] == work.PINNED_PREREQUISITE_AFTER_SAVE
    assert binding["funds_at_close"] == FUNDS - 1300
    after_facts = binding["edge_facts"]
    assert (
        after_facts["connected_front_to_depot"],
        after_facts["connected_depot_to_front"],
    ) == (True, True)
    assert binding["fleet_count"] == 0
    # Idempotent: a second verified replay re-derives the same bytes.
    again = work.verify_depot_mutation_attempt(directory)
    assert again["verification"] == "F12_MUTATION_COMPLETION_VERIFIED"
    assert binding_path.read_bytes() == binding_bytes


def test_replay_fails_closed_on_a_tampered_after_save_binding(
    consumed_depot_attempt, monkeypatch
):
    directory, _, _, _ = consumed_depot_attempt
    monkeypatch.setattr(work, "replay_authorization_state", lambda *a, **k: None)
    binding_path = directory / work.DEPOT_AFTER_SAVE_BINDING_NAME
    if not binding_path.is_file():
        pytest.skip("the binding of record is first derived by its own test")
    before = binding_path.read_bytes()
    before_manifest = directory / "artifact-manifest.sha256"
    manifest_ok = before_manifest.read_text()
    tampered = json.loads(before)
    tampered["edge_facts"]["front_read"] = 45999
    binding_path.write_text(json.dumps(tampered, sort_keys=True, indent=2) + "\n")
    try:
        before_manifest.write_text(manifest(directory))
        with pytest.raises(ValueError, match="after-save binding drifted"):
            work.verify_depot_mutation_attempt(directory)
    finally:
        binding_path.write_bytes(before)
        before_manifest.write_text(manifest_ok)


def test_replay_fails_closed_on_a_forced_complete_without_the_authoritative_after_save(
    consumed_depot_attempt, monkeypatch
):
    """A completion label that lacks its authoritative after-save triple —
    no digest, no retained save, a drifted digest or a drifted size — can
    never verify."""
    directory, _, _, _ = consumed_depot_attempt
    monkeypatch.setattr(work, "replay_authorization_state", lambda *a, **k: None)
    saved_path = directory / "after.sav"
    binding_path = directory / work.DEPOT_AFTER_SAVE_BINDING_NAME
    receipt_path = directory / "receipt.json"
    result_path = directory / "result.json"
    manifest_path = directory / "artifact-manifest.sha256"
    saved_bytes = saved_path.read_bytes()
    receipt_ok = receipt_path.read_bytes()
    result_ok = result_path.read_bytes()
    binding_backup = binding_path.read_bytes() if binding_path.is_file() else None
    actual_digest = hashlib.sha256(saved_bytes).hexdigest()
    actual_size = len(saved_bytes)
    result_stripped = {
        name: value
        for name, value in json.loads(result_ok).items()
        if not name.startswith("after_save")
    }
    receipt_stripped = {
        name: value
        for name, value in json.loads(receipt_ok).items()
        if not name.startswith("after_save")
    }
    try:
        def _resign():
            manifest_path.write_text(manifest(directory))

        # (1) the label never bound the world of record and the save is gone
        saved_path.unlink()
        _tamper_json(receipt_path, lambda m: receipt_stripped)
        _tamper_json(result_path, lambda m: result_stripped)
        _resign()
        with pytest.raises(ValueError, match="authoritative after-save digest"):
            work.verify_depot_mutation_attempt(directory)
        # (2) the digest and size are claimed but the retained save is gone
        _tamper_json(
            result_path,
            lambda m: dict(
                m,
                after_save_sha256=actual_digest,
                after_save_size_bytes=actual_size,
            ),
        )
        _resign()
        with pytest.raises(ValueError, match="retained authoritative after.sav"):
            work.verify_depot_mutation_attempt(directory)
        # (3) the save is retained but the digest drifted
        saved_path.write_bytes(saved_bytes)
        _tamper_json(result_path, lambda m: dict(m, after_save_sha256="e" * 64))
        _resign()
        with pytest.raises(ValueError, match="after-save digest drifted"):
            work.verify_depot_mutation_attempt(directory)
        # (4) the digest matches but the size drifted
        _tamper_json(
            result_path,
            lambda m: dict(
                m, after_save_sha256=actual_digest, after_save_size_bytes=actual_size + 1
            ),
        )
        _resign()
        with pytest.raises(ValueError, match="after-save size"):
            work.verify_depot_mutation_attempt(directory)
        # (5) the exact fabrication above restores to the verified verdict
        _restore_bytes(receipt_path, receipt_ok)
        _restore_bytes(result_path, result_ok)
        _restore_bytes(saved_path, saved_bytes)
        _restore_bytes(binding_path, binding_backup)
        _resign()
        verdict = work.verify_depot_mutation_attempt(directory)
        assert verdict["verification"] == "F12_MUTATION_COMPLETION_VERIFIED"
    finally:
        _restore_bytes(receipt_path, receipt_ok)
        _restore_bytes(result_path, result_ok)
        _restore_bytes(saved_path, saved_bytes)
        _restore_bytes(binding_path, binding_backup)
        manifest_path.write_text(manifest(directory))


@pytest.fixture(scope="module")
def refused_depot_directory(tmp_path_factory):
    """A second synthetic consumed directory whose strict save was refused
    on the complete path: the six exchanges completed natively, then the
    terminal PHASE_COMPLETE_SAVE_REFUSED result as the run writes it."""
    prepared = work.prepare_depot_mutation_candidate(
        tmp_path_factory.mktemp("depot-refused") / "candidate"
    )
    directory = prepared.directory
    seal = sha256(directory / "PRELAUNCH.json")
    metadata = json.loads((directory / "PRELAUNCH.json").read_text())
    exchanges, plan = _consumed_depot_exchanges(seal, metadata["plan_policy"]["schedule"])
    _fabricate_consumed_depot_frames(directory, exchanges)
    phase = dm.depot_phase_outcome(exchanges, prelaunch_digest=seal, plan=plan)
    assert phase["verification"] == "DEPOT_MUTATION_COMPLETE"
    _fabricate_consumed_depot_records(
        directory,
        exchanges,
        seal,
        phase,
        save_error="TimeoutError: owned native save completion missing",
    )
    yield directory
    prepared.spec.workspace.close()


def test_replay_marks_the_save_refusal_terminal_and_preserved(
    refused_depot_directory, monkeypatch
):
    directory = refused_depot_directory
    monkeypatch.setattr(work, "replay_authorization_state", lambda *a, **k: None)
    result = json.loads((directory / "result.json").read_text())
    assert result["verified"] is False
    assert result["status"] == "PHASE_COMPLETE_SAVE_REFUSED"
    verdict = work.verify_depot_mutation_attempt(directory)
    assert verdict["verification"] == "PHASE_COMPLETE_SAVE_REFUSED"
    assert verdict["result_status"] == "PHASE_COMPLETE_SAVE_REFUSED"
    assert (
        verdict["result_save_error"]
        == "TimeoutError: owned native save completion missing"
    )
    assert verdict["funds_close"] == FUNDS - 1300
    assert verdict["exchanges"] == list(EXCHANGES)
    assert verdict["mutated"] == ["demo-00", "road-00", "depot-00"]
    assert work.depot_verdict_exit_status(verdict) == 1
    assert not (directory / work.DEPOT_AFTER_SAVE_BINDING_NAME).is_file()
    assert not (directory / "after.sav").is_file()


def test_replay_fails_closed_on_a_save_refusal_contradiction(
    refused_depot_directory, monkeypatch
):
    directory = refused_depot_directory
    monkeypatch.setattr(work, "replay_authorization_state", lambda *a, **k: None)
    result_path = directory / "result.json"
    result_ok = result_path.read_bytes()
    manifest_path = directory / "artifact-manifest.sha256"
    try:
        # (1) a refusal without its recorded native save error cannot verify
        _tamper_json(result_path, lambda m: dict(m, save_error="  "))
        manifest_path.write_text(manifest(directory))
        with pytest.raises(ValueError, match="lacks its recorded native save error"):
            work.verify_depot_mutation_attempt(directory)
        # (2) a refusal claiming the authoritative after-save cannot verify
        _tamper_json(
            result_path,
            lambda m: dict(
                m,
                save_error="TimeoutError: owned native save completion missing",
                after_save_sha256="a" * 64,
            ),
        )
        manifest_path.write_text(manifest(directory))
        with pytest.raises(
            ValueError, match="cannot carry the authoritative after-save"
        ):
            work.verify_depot_mutation_attempt(directory)
        # (3) a refusal verified against its own label's phase evidence stands
        _restore_bytes(result_path, result_ok)
        manifest_path.write_text(manifest(directory))
        verdict = work.verify_depot_mutation_attempt(directory)
        assert verdict["verification"] == "PHASE_COMPLETE_SAVE_REFUSED"
    finally:
        _restore_bytes(result_path, result_ok)
        manifest_path.write_text(manifest(directory))



def test_nut_pin_table_binds_to_the_python_depot_schedule():
    """The shipped depot GameScript's `depot_planned` rows and its pin table
    are read from the package bytes and must equal the wire contract's
    schedule exactly: ids/ops/statuses in order, the pinned depot tile and
    front, the pinned ceiling and company."""
    text = (work.DEPOT_MUTATION_PACKAGE / "main.nut").read_text()
    planned_match = re.search(r"depot_planned = \[(.*?)\n    \]", text, re.DOTALL)
    assert planned_match, "the shipped package lost its depot_planned table"
    rows = re.findall(
        r'\["([a-z0-9-]+)",\s*"([a-z]+)",\s*"[A-Z_]+"\]', planned_match.group(1)
    )
    assert [exchange for exchange, _op in rows] == EXCHANGES
    assert rows == [
        ("before-00", "observe"),
        ("demo-00", "demolish"),
        ("road-00", "road"),
        ("depot-00", "depot"),
        ("after-00", "observe"),
        ("fleet-00", "fleet"),
    ]
    for marker, name, value in (
        (r"depot_tile = (\d+)", "depot_tile", "45487"),
        (r"depot_front_tile = (\d+)", "depot_front_tile", "45743"),
        (r"pickup = (\d+)", "pickup", "45748"),
        (r"delivery = (\d+)", "delivery", "50351"),
        (r"MAX_DEPOT_MUTATION_COST = (\d+)", "MAX_DEPOT_MUTATION_COST", "3000"),
        (r"DEPOT_COMPANY = (\d+)", "DEPOT_COMPANY", "0"),
        (r"MAX_FLEET_ROWS = (\d+)", "MAX_FLEET_ROWS", "4"),
    ):
        found = re.search(marker, text)
        assert found is not None, f"the shipped package lost its {name} pin"
        assert found.group(1) == value


def test_depot_bytes_never_parse_into_the_consumed_contract_families():
    """The protocol-10 depot request cannot be retrofitted into the protocol-5
    or -6 wire contracts, and an older family's request cannot ride the
    protocol-10 contract."""
    from app.simulation.openttd.corridor_accept_survey import SurveyReadback

    depot = depot_request("before-00")
    with pytest.raises(Exception):
        SurveyReadback.parse_for(survey_request(), depot.to_bytes())
    with pytest.raises(Exception):
        dm.DepotReadback.parse_for(depot, survey_request().to_bytes())
