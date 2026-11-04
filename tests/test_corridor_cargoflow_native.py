"""Controlled offline tests for the D5-CARGOFLOW-1 native staging pipeline.

The pipeline under test is
``app/simulation/openttd/proof/corridor_cargoflow_native.py``, staged as a
fresh candidate from the pinned consumed depot-mutation prerequisite
(``d5-corridor-depot-mutation-native-candidate-3``, world-pin version 3) as
the freight v2 binding derives it. Everything here is strictly offline: no
OpenTTD launch, no AdminPort connection, no claim, no authorization artifact,
and no mutation of any retained attempt record or authoritative save.
Replay behavior is exercised with real production verdict paths (claim
absent, tampered retained evidence, synthetic retained evidence without
operator authorization), so every refusal is the real fail-closed outcome,
never a mock of the verifier.

The one synthetic consumed fixture stages a REAL candidate (prerequisite =
the pinned depot-mutation attempt of record) and fabricates only the missing
post-launch artifacts — fourteen correlated protocol-10 probe frames over
the read-only ladder with a coherent stockpile-static world, the runtime
welcome, cleanup certification and the flat retained receipt exactly as the
execution writes it. The operator-authorization gate is the one seam
monkeypatched (no authorized probe run exists under the tests); every
prerequisite, identity, digest, phase, sample and cleanup fact is otherwise
verified by the production replay path.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import re
from pathlib import Path

import pytest

import app.simulation.openttd.proof.corridor_accept_survey_native as survey_native
import app.simulation.openttd.proof.corridor_box_census_native as census_native
import app.simulation.openttd.proof.corridor_cargoflow_native as work
import app.simulation.openttd.proof.corridor_freight_native as d5
import app.simulation.openttd.proof.corridor_freight_v2_native as freight_v2_native
from app.simulation.openttd import corridor_cargoflow as cf
from app.simulation.openttd.proof.harness import manifest, sha256
from app.simulation.openttd.proof.operator_authorization import (
    authorization_payload,
    canonical_authorization_bytes,
)
from app.simulation.openttd.proof.terrain_clearing import claim_status
from tests.test_corridor_accept_survey import SEAL as SURVEY_SEAL
from tests.test_corridor_accept_survey_native import _admin_frame
from tests.test_corridor_cargoflow import ANCHOR, FUNDS, ready_payload
from tests.test_corridor_freight import PRELAUNCH as FREIGHT_SEAL

SCHEDULE = work.cargoflow_schedule()
PLAN = work.cargoflow_pipeline_plan()
EXCHANGES = list(cf.CARGOFLOW_EXCHANGE_IDS)


def cargoflow_request(entry_index: int, seal: str = FREIGHT_SEAL) -> cf.CargoFlowRequest:
    return work._cargoflow_exchange_request(SCHEDULE[entry_index], seal, PLAN)


def ready_readback(request: cf.CargoFlowRequest, **overrides) -> cf.CargoFlowReadback:
    return cf.CargoFlowReadback.model_validate(ready_payload(request, **overrides))


def _wire_of(readback) -> bytes:
    return json.dumps(
        readback.model_dump(mode="json", exclude_none=True), separators=(",", ":")
    ).encode()


@pytest.fixture(scope="module")
def staged(tmp_path_factory):
    prepared = work.prepare_cargoflow_candidate(
        tmp_path_factory.mktemp("cargoflow-staging") / "candidate"
    )
    yield prepared
    prepared.spec.workspace.close()


def metadata_of(prepared) -> dict:
    return json.loads((prepared.directory / "PRELAUNCH.json").read_text())


# --- the plan-bound pipeline and the cross-session guards --------------------


def test_cargoflow_pipeline_accepts_a_cargoflowplan_only():
    plan = work.cargoflow_pipeline_plan()
    assert work._require_cargoflow_plan(plan).digest == plan.digest
    with pytest.raises(work.CargoflowStagingError, match="CargoFlowPlan"):
        work._require_cargoflow_plan(d5.freight_plan())
    with pytest.raises(work.CargoflowStagingError, match="CargoFlowPlan"):
        work._require_cargoflow_plan(census_native.census_plan())
    with pytest.raises(work.CargoflowStagingError, match="CargoFlowPlan"):
        work._require_cargoflow_plan(survey_native.survey_plan_v2())
    with pytest.raises(work.CargoflowStagingError, match="CargoFlowPlan"):
        work._require_cargoflow_plan(dict(digest=plan.digest))


def test_probe_schedule_is_the_pinned_fourteen_sample_ladder():
    schedule = work.cargoflow_schedule()
    assert [row["exchange"] for row in schedule] == EXCHANGES
    assert [row["offset"] for row in schedule] == list(cf.CARGOFLOW_SAMPLE_OFFSETS)
    assert all(row["op"] == "sample" for row in schedule)
    assert work.CARGOFLOW_ATTEMPT == "D5-CARGOFLOW-1"
    budgets = work.cargoflow_budgets()
    with pytest.raises(ValueError, match="foreign ladder offset"):
        work.cargoflow_exchange_timeout_seconds(budget_table=budgets, offset=66)
    with pytest.raises(ValueError, match="foreign ladder offset"):
        work.cargoflow_exchange_timeout_seconds(budget_table=budgets, offset=-1)
    assert (
        work.cargoflow_exchange_timeout_seconds(budget_table=budgets, offset=0)
        == budgets["request_seconds"]
    )
    assert (
        work.cargoflow_exchange_timeout_seconds(budget_table=budgets, offset=65)
        == budgets["watch_seconds"] + budgets["exchange_margin_seconds"]
    )


def test_freight_survey_census_requests_cannot_cross_the_probe_sessions():
    """A freight (protocol 5) or census (protocol 9) frame cannot travel on
    the probe session, and a probe frame cannot travel on either older
    session; every refusal lands before any handler can run."""
    probe = object.__new__(work.CargoflowSecureSession)
    probe._state = d5.AuthState.ACTIVE
    census = object.__new__(census_native.CensusSecureSession)
    census._state = d5.AuthState.ACTIVE
    survey = object.__new__(survey_native.SurveySecureSession)
    survey._state = d5.AuthState.ACTIVE
    probe_frame = work.encode_cargoflow_request(cargoflow_request(0).to_bytes())
    probe.validate_outbound(probe_frame)
    census.validate_outbound(
        census_native.encode_census_request(
            census_native._census_exchange_request(
                next(iter(census_native.census_schedule())),
                FREIGHT_SEAL,
                census_native.census_plan(),
            ).to_bytes()
        )
    )
    survey.validate_outbound(
        survey_native.encode_survey_request(
            survey_native.SurveyRequest(
                op="accept",
                request_id="accept-00",
                plan=SURVEY_SEAL,
                company=0,
                max_cost=0,
                pickup=45748,
                delivery=50351,
                depot=45487,
                tile=50351,
            ).to_bytes()
        )
    )
    with pytest.raises(Exception):
        census.validate_outbound(probe_frame)
    with pytest.raises(Exception):
        survey.validate_outbound(probe_frame)
    with pytest.raises(Exception):
        probe.validate_outbound(census_native.encode_census_request(
            census_native._census_exchange_request(
                next(iter(census_native.census_schedule())),
                FREIGHT_SEAL,
                census_native.census_plan(),
            ).to_bytes()
        ))


# --- staging correctness ------------------------------------------------------


def test_staged_candidate_binds_the_probe_lineage(staged):
    metadata = metadata_of(staged)
    assert metadata["schema"] == work.D5_CARGOFLOW_PRELAUNCH_SCHEMA
    assert metadata["schema"] == "d5-cargoflow-prelaunch-v1"
    assert metadata["attempt"] == work.CARGOFLOW_ATTEMPT == "D5-CARGOFLOW-1"
    assert metadata["milestone"] == work.MILESTONE_CARGOFLOW
    assert metadata["kind"] == work.KIND == "cargoflow"
    assert metadata["budgets"]["max_cost"] == 0
    assert metadata["budgets"]["planned_exchanges"] == 14
    assert metadata["budgets"]["requests"] == cf.CARGOFLOW_REQUEST_BUDGET == 32
    assert metadata["budgets"]["expected_funds"] == FUNDS == 489650
    assert metadata["budgets"]["launches"] == 1 and metadata["budgets"]["retries"] == 0
    assert metadata["plan_policy"]["max_cost"] == 0
    assert metadata["plan_policy"]["plan_model_digest"] == PLAN.digest
    assert metadata["plan_policy"]["schedule_version"] == 1
    assert metadata["plan_policy"]["command"] == "none"
    assert metadata["plan_policy"]["target_tile"] == 45748
    assert (
        metadata["prerequisite"]["after_save_sha256"]
        == work.PINNED_PREREQUISITE_AFTER_SAVE
        == "183b20273a54ebe1a2cd9306145a9ea820bbd6114b1608c42079b4e1b1efe6a6"
    )
    assert metadata["prerequisite"]["attempt"] == "D5-F12-DEPOT-3"
    assert metadata["prerequisite"]["milestone"] == "D5-F12-DEPOT"
    assert metadata["world"]["save_sha256"] == work.PINNED_PREREQUISITE_AFTER_SAVE
    assert metadata["world"]["source_save"] == "after.sav"
    read_only = metadata["plan_policy"]["read_only"]
    assert read_only["schema"] == "d5-cargoflow-readonly-v1"
    assert read_only["permitted_ops"] == ["sample"]
    assert read_only["max_cost"] == 0 and read_only["funds_readback_required"] is True
    grid = metadata["plan_policy"]["sample_grid"]
    assert grid["schema"] == "d5-cargoflow-sample-grid-v1"
    assert grid["planned_samples"] == 14 and grid["cadence_days"] == 5
    assert grid["span_days"] == 65 and grid["offsets"] == list(cf.CARGOFLOW_SAMPLE_OFFSETS)
    assert grid["wait_ticks"] == 2048 and grid["wait_day_cap"] == 60
    assert metadata["cross_schedule_guard"]["schema"] == "d5-cargoflow-cross-guard-v1"
    assert metadata["bootstrap_command"] == "start_ai RoadProofCompany"


def test_no_consumed_attempt_or_lineage_name_in_the_staged_candidate(staged):
    """The consumed attempt ids of the other contract families appear zero
    times in the fresh probe candidate's staged bytes."""
    for path in sorted(staged.directory.rglob("*")):
        if not path.is_file():
            continue
        blob = path.read_bytes()
        try:
            text = blob.decode()
        except UnicodeDecodeError:
            text = ""
        for foreign in (
            "D5-BOX-CENSUS-2",
            "d5-box-census-prelaunch",
            "d5-accept-survey-prelaunch",
            "d5-freight-prelaunch-v1",
            "d5-freight-v2-prelaunch",
            "D5-FREIGHT-1",
            "D5-FREIGHT-2",
            "D5-FREIGHT-3",
            "D5-FREIGHT-4",
            "D5-FREIGHT-5",
            "D5-FREIGHT-6",
        ):
            assert foreign not in text, (path, foreign)


def test_cargoflow_prerequisite_binding_must_be_the_pinned_depot_attempt():
    binding = work.cargoflow_prerequisite_binding()
    assert binding["attempt"] == "D5-F12-DEPOT-3"
    assert binding["milestone"] == "D5-F12-DEPOT"
    assert binding["save"] == "after.sav"
    assert binding["save_sha256"] == work.PINNED_PREREQUISITE_AFTER_SAVE
    assert binding["schema"] == work.D5_CARGOFLOW_PREREQUISITE_SCHEMA
    assert "F12_MUTATION_COMPLETION_VERIFIED" in binding["verification"]
    assert "probe-scoped" in binding["verification"]
    shared = freight_v2_native.prerequisite_binding(freight_v2_native.DEPOT_PREREQUISITE)
    for name in ("attempt", "milestone", "retained_directory", "save_sha256"):
        assert binding[name] == shared[name]
    with pytest.raises(work.CargoflowStagingError, match="pinned depot prerequisite"):
        work.cargoflow_prerequisite_binding(
            Path("artifacts/experiments/d4-corridor-native-candidate-4")
        )
    with pytest.raises(work.CargoflowStagingError, match="pinned depot prerequisite"):
        work.cargoflow_prerequisite_binding(survey_native.PINNED_PREREQUISITES[1])


def test_staged_source_save_is_the_authoritative_depot_after_save(staged):
    metadata = metadata_of(staged)
    staged_save = Path(metadata["workspace"]) / "source.sav"
    assert sha256(staged_save) == work.PINNED_PREREQUISITE_AFTER_SAVE
    assert metadata["world"]["source_save"] == "after.sav"


def test_staged_composition_reuses_the_frozen_info_and_the_probe_main(staged):
    composition, bridge_class, version = work.staged_cargoflow_composition()
    assert (bridge_class, version) == ("NetworkFreightProof", 1)
    workspace = Path(metadata_of(staged)["workspace"])
    staged_main = (workspace / "game" / work.SOURCE_SAVE_GS_NAME / "main.nut").read_bytes()
    assert staged_main == composition["main.nut"]
    assert b"class NetworkFreightProof extends D5CargoFlowProof" in staged_main


def test_authorization_payload_rebuilds_and_no_claim_exists(staged):
    metadata = metadata_of(staged)
    seal = sha256(staged.directory / "PRELAUNCH.json")
    digest = work.staged_cargoflow_authorization_payload_digest(staged.directory)
    rebuilt = hashlib.sha256(
        canonical_authorization_bytes(authorization_payload(metadata, seal))
    ).hexdigest()
    assert rebuilt == digest
    assert not (staged.directory / "CLAIM.json").exists()
    assert not (staged.directory / "AUTHORIZATION.json").exists()
    assert claim_status(staged.directory) == "ABSENT"


def test_cargoflow_preflight_re_derives_every_binding(staged):
    metadata = work.cargoflow_preflight(staged)
    assert metadata["attempt"] == work.CARGOFLOW_ATTEMPT


def test_cargoflow_preflight_refuses_seal_tampering(staged):
    target = staged.directory
    original = (target / "PRELAUNCH.json").read_bytes()
    seal_text = (target / "PRELAUNCH.sha256").read_text()
    metadata = json.loads(original)
    metadata["budgets"]["max_cost"] = 7
    (target / "PRELAUNCH.json").write_text(json.dumps(metadata, sort_keys=True, indent=2) + "\n")
    (target / "PRELAUNCH.sha256").write_text(sha256(target / "PRELAUNCH.json") + "\n")
    try:
        with pytest.raises(ValueError, match="budget pins drifted"):
            work.cargoflow_preflight(staged)
    finally:
        (target / "PRELAUNCH.json").write_bytes(original)
        (target / "PRELAUNCH.sha256").write_text(seal_text)


def test_cargoflow_preflight_refuses_attempt_and_lineage_drift(staged):
    target = staged.directory
    original = (target / "PRELAUNCH.json").read_bytes()
    seal_text = (target / "PRELAUNCH.sha256").read_text()
    for tampered_name, tampered_value in (
        ("attempt", "D5-CARGOFLOW-2"),
        ("schema", "d5-cargoflow-prelaunch-v2"),
        ("kind", "freight"),
        ("milestone", "D5-FREIGHT"),
    ):
        metadata = json.loads(original)
        metadata[tampered_name] = tampered_value
        (target / "PRELAUNCH.json").write_text(
            json.dumps(metadata, sort_keys=True, indent=2) + "\n"
        )
        (target / "PRELAUNCH.sha256").write_text(sha256(target / "PRELAUNCH.json") + "\n")
        try:
            with pytest.raises(ValueError, match="lineage|identity"):
                work.cargoflow_preflight(staged)
        finally:
            (target / "PRELAUNCH.json").write_bytes(original)
            (target / "PRELAUNCH.sha256").write_text(seal_text)


def test_cargoflow_preflight_refuses_a_drifted_schedule_grid_scope_or_world(staged):
    target = staged.directory
    original = (target / "PRELAUNCH.json").read_bytes()
    seal_text = (target / "PRELAUNCH.sha256").read_text()
    for tamper in (
        lambda policy: policy["schedule"].pop(1),
        lambda policy: policy["schedule"][4].update(offset=10),
        lambda policy: policy["sample_grid"].update(span_days=60),
        lambda policy: policy["read_only"].update(permitted_ops=["sample", "site"]),
        lambda policy: policy["world"].update(depot_front=45744),
    ):
        metadata = json.loads(original)
        tamper(metadata["plan_policy"])
        (target / "PRELAUNCH.json").write_text(
            json.dumps(metadata, sort_keys=True, indent=2) + "\n"
        )
        (target / "PRELAUNCH.sha256").write_text(sha256(target / "PRELAUNCH.json") + "\n")
        try:
            with pytest.raises(ValueError, match="drifted"):
                work.cargoflow_preflight(staged)
        finally:
            (target / "PRELAUNCH.json").write_bytes(original)
            (target / "PRELAUNCH.sha256").write_text(seal_text)


def test_probe_hypotheses_stay_hypotheses_over_the_retained_census_receipt(staged):
    hypotheses = metadata_of(staged)["plan_policy"]["hypotheses"]
    assert hypotheses["state"] == "RETAINED_CENSUS_REBOUND"
    rows = hypotheses["industries"]
    assert rows[0]["role"] == "PRODUCING_PICKUP"
    assert rows[0]["industry"] == 0 and rows[0]["tile"] == 44983
    assert rows[0]["production_units"] == 104 and rows[0]["accepted_state"] == 0
    assert rows[0]["exactly_one"] is True and rows[0]["kind"] == "HYPOTHESIS"
    assert rows[1]["role"] == "ACCEPTING_BAY"
    assert rows[1]["industry"] == 1 and rows[1]["tile"] == 51116
    assert rows[1]["production_units"] == -1 and rows[1]["accepted_state"] == 1
    assert rows[1]["exactly_one"] is True and rows[1]["kind"] == "HYPOTHESIS"
    receipt_path = Path(
        "artifacts/experiments/d5-box-census-native-candidate-2/receipt.json"
    )
    receipt = json.loads(receipt_path.read_text())
    assert receipt["boxes"]["45748"]["members"] == [{"a": 0, "id": 0, "p": 104, "tile": 44983}]
    assert receipt["boxes"]["50862"]["members"] == [{"a": 1, "id": 1, "p": -1, "tile": 51116}]
    assert hypotheses["source_sha256"] == sha256(receipt_path)


def test_probe_hypotheses_name_absent_evidence_without_inventing(tmp_path, monkeypatch):
    fake_project = tmp_path
    (fake_project / "artifacts").mkdir(exist_ok=True)
    monkeypatch.setattr(work, "PROJECT", fake_project)
    absent = work.cargoflow_industry_hypotheses()
    assert absent["state"] == "RETAINED_CENSUS_ABSENT"
    assert absent["industries"] == []
    monkeypatch.undo()
    bound = work.cargoflow_industry_hypotheses()
    assert bound["state"] == "RETAINED_CENSUS_REBOUND"


def test_expected_readback_policy_tells_the_ladder_story(staged):
    policy = metadata_of(staged)["expected_readback"]
    assert sorted(policy) == ["funds", "ladder", "receipt", "sample", "verdicts"]
    assert "any other unsupported fact refuses the exchange terminally" in policy["sample"]
    assert "an overshoot is WINDOW_EXHAUSTED" in policy["ladder"]
    assert "a drifted balance halts the phase" in policy["funds"]
    assert "CARGOFLOW_GATE_UNDECIDED_INCOMPLETE" in policy["verdicts"]
    assert "leaves the probe incomplete forever" in policy["receipt"]


# --- the exchange helper and the probe frame replay parsing -------------------


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


def test_cargoflow_exchange_persists_request_and_response_pair(tmp_path):
    request = cargoflow_request(0)
    response = _wire_of(ready_readback(request))
    reply = _admin_frame(response + b"\0")
    readback = asyncio.run(work.cargoflow_exchange(_FakeSession(reply), request, tmp_path))
    assert readback.status == "READY" and readback.anchor == ANCHOR
    assert (tmp_path / "sample-00-request.json").read_bytes() == request.to_bytes()
    assert (tmp_path / "sample-00-response.json").read_bytes() == response
    parsed = cf.CargoFlowReadback.parse_for(request, response)
    assert parsed.digest == readback.digest


def test_cargoflow_exchange_refuses_malformed_truncated_and_stale_replies(tmp_path):
    request = cargoflow_request(0)

    class Broken:
        async def send(self, frame):
            pass

        async def receive(self):
            return b""

    with pytest.raises(ConnectionError):
        asyncio.run(work.cargoflow_exchange(Broken(), request, tmp_path))
    # A reply correlated to a different ladder label is refused fail-closed.
    stale = _admin_frame(_wire_of(ready_readback(request)) + b"\0")
    stale_request = cargoflow_request(5)
    with pytest.raises(ValueError):
        asyncio.run(work.cargoflow_exchange(_FakeSession(stale), stale_request, tmp_path))
    # Whatever the gateway sends that is not one gamescript response frame
    # can never become a measured probe observation.
    with pytest.raises(ValueError):
        asyncio.run(
            work.cargoflow_exchange(
                _FakeSession(_admin_frame(b"\x00junk\x00")), request, tmp_path
            )
        )


def test_cargoflow_response_bounds_are_exactly_512_and_1400(tmp_path):
    request = cargoflow_request(0)
    assert work.MAX_CARGOFLOW_REQUEST_BYTES == 512
    assert work.MAX_CARGOFLOW_RESPONSE_BYTES == 1400
    reply = _admin_frame(_wire_of(ready_readback(request)) + b"\0")
    readback = asyncio.run(work.cargoflow_exchange(_FakeSession(reply), request, tmp_path))
    assert readback.anchor == ANCHOR
    from app.simulation.openttd.gamescript_transport import encode_gamescript

    over = json.dumps({**ready_payload(request), "pad": "x" * 1600}, sort_keys=True).encode()
    with pytest.raises(ValueError):
        encode_gamescript(over)
    with pytest.raises(ValueError):
        work.decode_cargoflow_request(over)


def test_cargoflow_frame_replay_parser(tmp_path):
    request = cargoflow_request(0)
    response = _wire_of(ready_readback(request))
    reply = _admin_frame(response + b"\0")
    frames = [
        ["outbound", work.encode_cargoflow_request(request.to_bytes()).hex()],
        ["inbound", reply.hex()],
    ]
    (tmp_path / "frames.json").write_text(json.dumps(frames))
    outbound, requests, replies, request_positions, reply_positions = (
        work._parse_cargoflow_frames(tmp_path)
    )
    assert requests == [request]
    assert replies == [response]
    assert request_positions[request.to_bytes()] == 0
    assert set(reply_positions) == {response}
    from app.simulation.openttd.gamescript_transport import encode_gamescript

    with pytest.raises(ValueError, match="invalid CargoFlowRequest"):
        junk = [["outbound", encode_gamescript(b'{"op":"site"}').hex()]]
        (tmp_path / "frames.json").write_text(json.dumps(junk))
        work._parse_cargoflow_frames(tmp_path)


# --- replay verification fail-closed behavior --------------------------------


def test_unconsumed_probe_candidate_verifies_fail_closed(staged):
    verdict = work.verify_cargoflow_attempt(staged.directory)
    assert verdict == {
        "verification": "AUTHORIZATION_UNVERIFIED",
        "authorization_state": "CLAIM_ABSENT",
        "statement": (
            "the probe candidate was never consumed by an operator "
            "authorization; no verified completion is possible"
        ),
    }
    assert claim_status(staged.directory) == "ABSENT"


def test_probe_replay_refuses_a_claim_mismatched_to_its_seal(staged):
    target = staged.directory
    (target / "CLAIM.json").write_text(json.dumps(dict(prelaunch_digest="0" * 64)))
    try:
        with pytest.raises(ValueError, match="claim does not match"):
            work.verify_cargoflow_attempt(target)
    finally:
        (target / "CLAIM.json").unlink()


def _claim_engine(tmp_path, staged):
    """A retained-evidence directory with a self-consistent one-shot claim
    and a forced NATIVE_CARGOFLOW_COMPLETE result label — but no operator
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
                status="NATIVE_CARGOFLOW_COMPLETE",
                exchanges=list(EXCHANGES),
                requests=14,
                native_launches=1,
                connections=1,
                command_accepted=True,
                last_status="READY",
                returncode=0,
                state_changed=False,
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


def test_probe_replay_never_verifies_a_forced_label_without_authorization(
    staged, tmp_path
):
    target = _claim_engine(tmp_path, staged)
    metadata = json.loads((target / "PRELAUNCH.json").read_text())
    seal = sha256(target / "PRELAUNCH.json")
    claims = json.loads((target / "CLAIM.json").read_text())
    assert d5.replay_authorization_state(target, metadata, seal, claims) is not None
    verdict = work.verify_cargoflow_attempt(target)
    assert verdict["verification"] == "AUTHORIZATION_UNVERIFIED"
    assert verdict["authorization_state"] not in (None, "CLAIM_ABSENT")


def test_probe_replay_refuses_an_unreferenced_stray_file(staged, tmp_path):
    target = _claim_engine(tmp_path, staged)
    (target / "stray.txt").write_text("not in the manifest")
    with pytest.raises(ValueError, match="exhaustive"):
        work.verify_cargoflow_attempt(target)
    (target / "stray.txt").unlink()
    verdict = work.verify_cargoflow_attempt(target)
    assert verdict["verification"] == "AUTHORIZATION_UNVERIFIED"


def test_probe_replay_refuses_an_unknown_prelaunch_schema(staged, tmp_path):
    target = tmp_path / "alien"
    target.mkdir()
    metadata = metadata_of(staged)
    metadata["schema"] = d5.D5_FREIGHT_PRELAUNCH_SCHEMA  # the freight lineage, not the probe
    (target / "PRELAUNCH.json").write_text(json.dumps(metadata, sort_keys=True, indent=2) + "\n")
    (target / "PRELAUNCH.sha256").write_text(sha256(target / "PRELAUNCH.json") + "\n")
    (target / "CLAIM.json").write_text(
        json.dumps(dict(prelaunch_digest=sha256(target / "PRELAUNCH.json"), consumed=True))
    )
    (target / "artifact-manifest.sha256").write_text(manifest(target))
    verdict = work.verify_cargoflow_attempt(target)
    assert verdict["authorization_state"] == "UNKNOWN_PRELAUNCH_SCHEMA"


# --- the single-attempt identity: its bindings cannot drift -------------------


def test_identity_pairs_the_record_with_the_probe_plan_only(staged):
    metadata = metadata_of(staged)
    assert work.verify_cargoflow_attempt_identity(metadata, plan=PLAN)
    for tampered_name, tampered_value in (
        ("schema", "d5-cargoflow-prelaunch-v2"),
        ("kind", "census"),
        ("milestone", "D5-BOX-CENSUS"),
    ):
        crossed = json.loads(json.dumps(metadata))
        crossed[tampered_name] = tampered_value
        with pytest.raises(ValueError, match="identity drifted|not the D5 cargoflow lineage"):
            work.verify_cargoflow_attempt_identity(crossed, plan=PLAN)


def test_identity_refuses_a_crossed_plan_model(staged):
    metadata = metadata_of(staged)
    with pytest.raises(work.CargoflowStagingError, match="CargoFlowPlan"):
        work.verify_cargoflow_attempt_identity(metadata, plan=d5.freight_plan())
    with pytest.raises(work.CargoflowStagingError, match="CargoFlowPlan"):
        work.verify_cargoflow_attempt_identity(
            metadata, plan=census_native.census_plan()
        )
    with pytest.raises(work.CargoflowStagingError, match="CargoFlowPlan"):
        work.verify_cargoflow_attempt_identity(
            metadata, plan=survey_native.survey_plan_v2()
        )


def test_identity_refuses_a_drifted_prerequisite_or_world_or_policy(staged):
    metadata = metadata_of(staged)
    for tamper in (
        lambda m: m["prerequisite"].update(after_save_sha256="9" * 64),
        lambda m: m["prerequisite"].update(attempt="D5-F12-DEPOT-2"),
        lambda m: m["world"].update(save_sha256="9" * 64),
        lambda m: m["plan_policy"].update(max_cost=5),
        lambda m: m["plan_policy"].update(
            sample_grid=dict(schema="d5-cargoflow-sample-grid-v1")
        ),
        lambda m: m["plan_policy"].update(
            hypotheses=dict(industries=[], state="RETAINED_CENSUS_ABSENT")
        ),
        lambda m: m["budgets"].update(requests=30),
    ):
        crossed = json.loads(json.dumps(metadata))
        tamper(crossed)
        with pytest.raises(ValueError, match="drifted|floated"):
            work.verify_cargoflow_attempt_identity(crossed, plan=PLAN)


# --- exit-status discipline ---------------------------------------------------


def test_cargoflow_exit_status_zero_only_for_the_verified_completion():
    assert (
        work.cargoflow_exit_status(
            dict(
                verified=True,
                status="NATIVE_CARGOFLOW_COMPLETE",
                cleanup_complete=True,
                state_changed=False,
            )
        )
        == 0
    )
    for bad in (
        dict(
            verified=True,
            status="NATIVE_CARGOFLOW_COMPLETE",
            cleanup_complete=False,
            state_changed=False,
        ),
        dict(
            verified=True,
            status="PHASE_HALTED_PREFIX_PRESERVED",
            cleanup_complete=True,
            state_changed=False,
        ),
        dict(
            verified=True,
            status="NATIVE_CARGOFLOW_COMPLETE",
            cleanup_complete=True,
            state_changed=True,
        ),
        dict(verified=False, status="FAILED", cleanup_complete=True, state_changed=False),
    ):
        assert work.cargoflow_exit_status(bad) == 1
    verdict_zero = work.cargoflow_verdict_exit_status(
        dict(verification="CARGOFLOW_COMPLETION_VERIFIED")
    )
    assert verdict_zero == 0
    assert (
        work.cargoflow_verdict_exit_status(dict(verification="PHASE_HALTED_EVIDENCE_PRESERVED"))
        == 1
    )


# --- the synthetic consumed probe attempt -------------------------------------


def _consumed_probe_exchanges(seal: str, schedule):
    exchanges = []
    for entry in schedule:
        request = work._cargoflow_exchange_request(entry, seal, PLAN)
        readback = ready_readback(request)
        exchanges.append((request, readback))
    return exchanges


@pytest.fixture(scope="module")
def consumed_probe_attempt(tmp_path_factory):
    prepared = work.prepare_cargoflow_candidate(
        tmp_path_factory.mktemp("cargoflow-consumed") / "candidate"
    )
    directory = prepared.directory
    seal = sha256(directory / "PRELAUNCH.json")
    metadata = json.loads((directory / "PRELAUNCH.json").read_text())
    exchanges = _consumed_probe_exchanges(seal, metadata["plan_policy"]["schedule"])
    frames = []
    for request, readback in exchanges:
        wire = _wire_of(readback)
        (directory / (request.request_id + "-request.json")).write_bytes(request.to_bytes())
        (directory / (request.request_id + "-response.json")).write_bytes(wire)
        frames.append(["outbound", work.encode_cargoflow_request(request.to_bytes()).hex()])
        frames.append(["inbound", _admin_frame(wire + b"\0").hex()])
    (directory / "frames.json").write_text(json.dumps(frames))
    phase = cf.cargoflow_phase_outcome(exchanges, prelaunch_digest=seal, plan=PLAN)
    (directory / "session-before-identity.json").write_text(
        json.dumps(dict(sha256="9" * 64), sort_keys=True) + "\n"
    )
    (directory / "receipt.json").write_text(
        json.dumps(
            dict(phase, before_save_sha256="9" * 64),
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
    (directory / "result.json").write_text(
        json.dumps(
            dict(
                preflight="PASS",
                native_launches=1,
                connections=1,
                requests=14,
                exchanges=[request.request_id for request, _ in exchanges],
                last_status="READY",
                command_accepted=True,
                state_changed=False,
                verified=True,
                status="NATIVE_CARGOFLOW_COMPLETE",
                halt=None,
                returncode=0,
                cleanup_complete=True,
            ),
            sort_keys=True,
            indent=2,
        )
        + "\n"
    )
    (directory / "artifact-manifest.sha256").write_text(d5.manifest(directory))
    yield directory, exchanges, seal
    prepared.spec.workspace.close()


def test_replay_verifies_a_fully_consumed_probe_frame_sequence(
    consumed_probe_attempt, monkeypatch
):
    directory, exchanges, _ = consumed_probe_attempt
    monkeypatch.setattr(work, "replay_authorization_state", lambda *a, **k: None)
    verdict = work.verify_cargoflow_attempt(directory)
    assert verdict["verification"] == "CARGOFLOW_COMPLETION_VERIFIED"
    assert verdict["receipt"]["phase"]["verification"] == "CARGOFLOW_COMPLETE"
    assert verdict["receipt"]["phase"]["anchor"] == ANCHOR
    assert verdict["receipt"]["phase"]["receipts"][0]["funds"] == FUNDS
    assert verdict["receipt"]["before_save_sha256"] == "9" * 64
    assert verdict["receipt"]["phase"]["sampled_months"] == [[1951, 4], [1951, 5], [1951, 6]]
    phase = verdict["receipt"]["phase"]
    assert phase["verdict"]["verdict"] == "DISPATCH_STOCKPILE_STATIC"
    assert phase["series"]["stock_pickup"] == [-1] * 14
    assert phase["series"]["stock_bay"] == [0] * 14
    assert phase["series"]["wait_pickup"] == [0] * 14
    assert phase["series"]["prod_pickup"] == [104] * 14
    assert phase["series"]["prod_bay"] == [-1] * 14
    assert [receipt["request_id"] for receipt in phase["receipts"]] == EXCHANGES
    assert len(exchanges) == 14
    assert work.cargoflow_verdict_exit_status(verdict) == 0


def test_replay_fails_closed_on_a_tampered_retained_probe_receipt(
    consumed_probe_attempt, monkeypatch
):
    directory, _, _ = consumed_probe_attempt
    monkeypatch.setattr(work, "replay_authorization_state", lambda *a, **k: None)
    before = json.loads((directory / "receipt.json").read_text())
    (directory / "receipt.json").write_text(
        json.dumps(dict(before, sampled_months=[[1951, 4]]), sort_keys=True, indent=2) + "\n"
    )
    (directory / "artifact-manifest.sha256").write_text(d5.manifest(directory))
    with pytest.raises(ValueError, match="receipt replay mismatch"):
        work.verify_cargoflow_attempt(directory)
    (directory / "receipt.json").write_text(json.dumps(before, sort_keys=True, indent=2) + "\n")
    (directory / "artifact-manifest.sha256").write_text(d5.manifest(directory))


def test_replay_fails_closed_on_a_tampered_retained_response_inventory(
    consumed_probe_attempt, monkeypatch
):
    directory, _, _ = consumed_probe_attempt
    monkeypatch.setattr(work, "replay_authorization_state", lambda *a, **k: None)
    victim = directory / "sample-05-response.json"
    stored = victim.read_bytes()
    victim.unlink()
    (directory / "artifact-manifest.sha256").write_text(d5.manifest(directory))
    with pytest.raises(ValueError, match="lacks its durable response file"):
        work.verify_cargoflow_attempt(directory)
    victim.write_bytes(stored)
    (directory / "artifact-manifest.sha256").write_text(d5.manifest(directory))
    verdict = work.verify_cargoflow_attempt(directory)
    assert verdict["verification"] == "CARGOFLOW_COMPLETION_VERIFIED"


def test_replay_fails_closed_on_a_result_label_the_evidence_contradicts(
    consumed_probe_attempt, monkeypatch
):
    directory, _, _ = consumed_probe_attempt
    monkeypatch.setattr(work, "replay_authorization_state", lambda *a, **k: None)
    before = json.loads((directory / "result.json").read_text())
    (directory / "result.json").write_text(
        json.dumps(dict(before, native_launches=2), sort_keys=True, indent=2) + "\n"
    )
    (directory / "artifact-manifest.sha256").write_text(d5.manifest(directory))
    with pytest.raises(ValueError, match="contradicts"):
        work.verify_cargoflow_attempt(directory)
    (directory / "result.json").write_text(json.dumps(before, sort_keys=True, indent=2) + "\n")
    (directory / "artifact-manifest.sha256").write_text(d5.manifest(directory))


# --- the wire-to-Nut pin binding: the Python schedule can never drift ---------


def test_nut_pin_table_binds_to_the_python_probe_schedule():
    """The shipped probe GameScript's ``cargoflow_planned`` rows and its pin
    table are read from the package bytes and must equal the wire contract's
    ladder exactly: sample ids/offsets in order and the pinned corridor,
    station, industry, company and cargo identities."""
    text = (work.CARGOFLOW_PACKAGE / "main.nut").read_text()
    planned_match = re.search(r"cargoflow_planned = \[(.*?)\n    \]", text, re.DOTALL)
    assert planned_match, "the shipped package lost its cargoflow_planned table"
    rows = re.findall(r'\["(sample-\d\d)",\s*(\d+),\s*"[A-Z]+"\]', planned_match.group(1))
    assert [(exchange, int(offset)) for exchange, offset in rows] == list(
        zip(EXCHANGES, cf.CARGOFLOW_SAMPLE_OFFSETS)
    )
    for marker, name, value in (
        (r"\n    pickup = (\d+)", "pickup", "45748"),
        (r"\n    delivery = (\d+)", "delivery", "50862"),
        (r"\n    depot_tile = (\d+)", "depot_tile", "45487"),
        (r"\n    PICKUP_SID = (\d+)", "PICKUP_SID", "0"),
        (r"\n    BAY_SID = (\d+)", "BAY_SID", "2"),
        (r"\n    PICKUP_IND = (\d+)", "PICKUP_IND", "0"),
        (r"\n    BAY_IND = (\d+)", "BAY_IND", "1"),
        (r"\n    CARGOFLOW_COMPANY = (\d+)", "CARGOFLOW_COMPANY", "0"),
        (r"\n    CARGOFLOW_CARGO = (\d+)", "CARGOFLOW_CARGO", "1"),
        (r"\n    max_requests = (\d+)", "max_requests", "32"),
        (r"\n    WAIT_MAX_TICKS = (\d+)", "WAIT_MAX_TICKS", "2048"),
        (r"\n    WAIT_DAY_CAP = (\d+)", "WAIT_DAY_CAP", "60"),
    ):
        found = re.search(marker, text)
        assert found is not None, f"the shipped package lost its {name} pin"
        assert found.group(1) == value


def test_probe_bytes_never_parse_into_the_consumed_contract_families():
    """The protocol-10 probe bytes cannot be retrofitted into the protocol-5,
    -6 or -9 wire contracts."""
    from app.simulation.openttd.corridor_accept_survey import SurveyReadback
    from app.simulation.openttd.corridor_box_census import CensusReadback

    sample = cargoflow_request(0)
    survey = survey_native.SurveyRequest(
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
    with pytest.raises(Exception):
        CensusReadback.parse_for(
            census_native._census_exchange_request(
                next(iter(census_native.census_schedule())),
                FREIGHT_SEAL,
                census_native.census_plan(),
            ),
            sample.to_bytes(),
        )
    with pytest.raises(Exception):
        SurveyReadback.parse_for(survey, sample.to_bytes())
