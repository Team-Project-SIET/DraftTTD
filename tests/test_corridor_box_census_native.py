"""Controlled offline tests for the D5-BOX-CENSUS-1 native staging pipeline.

The pipeline under test is
``app/simulation/openttd/proof/corridor_box_census_native.py``, staged as a
fresh candidate from the pinned consumed A1 prerequisite
(``d5-corridor-extension-native-candidate-3``) exactly as the survey
pipeline is. Everything here is strictly offline: no OpenTTD launch, no
AdminPort connection, no claim, no authorization artifact, and no mutation
of any retained attempt record or authoritative save. Replay behavior is
exercised with real production verdict paths (claim-absent, tampered
retained evidence, synthetic retained evidence without operator
authorization), so every refusal is the real fail-closed outcome, never a
mock of the verifier.

The one synthetic consumed fixture stages a REAL candidate (prerequisite =
the pinned consumed A1 candidate-3) and fabricates only the missing
post-launch artifacts — ten correlated protocol-9 census frames over the
read-only schedule, the runtime welcome, cleanup certification and the flat
retained receipt exactly as the execution writes it. The
operator-authorization gate is the one seam monkeypatched (no authorized
census run exists under the tests); every prerequisite, identity, digest,
phase, box, frame and cleanup fact is otherwise verified by the production
replay path.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import re
from pathlib import Path

import pytest

import app.simulation.openttd.proof.corridor_accept_survey_native as survey_native
import app.simulation.openttd.proof.corridor_box_census_native as work
import app.simulation.openttd.proof.corridor_freight_native as d5
from app.simulation.openttd import corridor_box_census as cc
from app.simulation.openttd.proof.harness import manifest, sha256
from app.simulation.openttd.proof.operator_authorization import (
    authorization_payload,
    canonical_authorization_bytes,
)
from app.simulation.openttd.proof.terrain_clearing import claim_status
from tests.test_corridor_accept_survey import SEAL as SURVEY_SEAL
from tests.test_corridor_accept_survey_native import _admin_frame
from tests.test_corridor_freight import PRELAUNCH as FREIGHT_SEAL

EXCHANGES = list(cc.CENSUS_EXCHANGE_IDS)
FUNDS = cc.FUNDS_AT_A1_CLOSE


def census_request(exchange: str, seal: str = FREIGHT_SEAL) -> cc.CensusRequest:
    entry = next(row for row in work.census_schedule() if row["exchange"] == exchange)
    return work._census_exchange_request(entry, seal, work.census_plan())


def freight_site_request() -> d5.FreightRequest:
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


def census_reply_bytes(
    request: cc.CensusRequest,
    *,
    status: str = "READY",
    radius: int | None = None,
    accept: int | None = None,
    prod: int | None = None,
    funds: int = FUNDS,
    count: int | None = None,
    more: bool | None = None,
    rows: list[dict] | None = None,
) -> bytes:
    body: dict = {
        "protocol": 9,
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
        "cost": 0,
    }
    if request.tile is not None:
        body["tile"] = request.tile
    if request.cursor is not None:
        body["cursor"] = request.cursor
    if status == "READY":
        if request.op == "radius":
            body["radius"] = 3 if radius is None else radius
        elif request.op == "accept":
            body["accept"] = 0 if accept is None else accept
            body["radius"] = 3 if radius is None else radius
        elif request.op == "prod":
            body["prod"] = 104 if prod is None else prod
        elif request.op == "box":
            body["count"] = 0 if count is None else count
            body["more"] = False if more is None else more
            body["rows"] = [] if rows is None else rows
    return json.dumps(body, separators=(",", ":")).encode()


@pytest.fixture(scope="module")
def staged(tmp_path_factory):
    prepared = work.prepare_box_census_candidate(
        tmp_path_factory.mktemp("census-staging") / "candidate"
    )
    yield prepared
    prepared.spec.workspace.close()


def metadata_of(prepared) -> dict:
    return json.loads((prepared.directory / "PRELAUNCH.json").read_text())


# --- the plan-bound pipeline and the cross-session guards --------------------


def test_census_pipeline_accepts_a_boxcensusplan_only():
    plan = work.census_plan()
    assert work._require_census_plan(plan).digest == plan.digest
    with pytest.raises(work.CensusStagingError, match="BoxCensusPlan"):
        work._require_census_plan(d5.freight_plan())
    with pytest.raises(work.CensusStagingError, match="BoxCensusPlan"):
        work._require_census_plan(dict(digest=plan.digest))
    with pytest.raises(work.CensusStagingError, match="BoxCensusPlan"):
        work._require_census_plan(survey_native.survey_plan_v2())


def test_freight_survey_and_census_requests_cannot_cross_the_sessions():
    """A freight (protocol 5) or survey (protocol 6) frame cannot travel on
    the census session, and a census frame cannot travel on either older
    session; every refusal lands before any handler can run."""
    freight = object.__new__(d5.FreightSecureSession)
    freight._state = d5.AuthState.ACTIVE
    survey = object.__new__(survey_native.SurveySecureSession)
    survey._state = d5.AuthState.ACTIVE
    census = object.__new__(work.CensusSecureSession)
    census._state = d5.AuthState.ACTIVE
    census_frame = work.encode_census_request(census_request("radius-00").to_bytes())
    census.validate_outbound(census_frame)
    with pytest.raises(Exception):
        census.validate_outbound(d5.encode_freight_request(freight_site_request().to_bytes()))
    with pytest.raises(Exception):
        census.validate_outbound(
            survey_native.encode_survey_request(survey_request().to_bytes())
        )
    with pytest.raises(Exception):
        census.validate_outbound(b"garbage")
    survey.validate_outbound(
        survey_native.encode_survey_request(survey_request().to_bytes())
    )
    with pytest.raises(Exception, match="protocol|missing"):
        survey.validate_outbound(census_frame)
    freight.validate_outbound(d5.encode_freight_request(freight_site_request().to_bytes()))
    with pytest.raises(Exception, match="protocol|missing"):
        freight.validate_outbound(census_frame)


def test_census_schedule_is_the_pinned_ten_exchange_read_only_census():
    schedule = work.census_schedule()
    assert [row["exchange"] for row in schedule] == EXCHANGES
    assert all(row["op"] in cc.CENSUS_OPS for row in schedule)
    assert [row["observation_tile"] for row in schedule if row["op"] == "accept"] == [
        50351,
        50862,
    ]
    assert [row["observation_tile"] for row in schedule if row["op"] == "box"] == [
        45748,
        45748,
        45748,
        50862,
        50862,
        50862,
    ]
    assert [row["page_cursor"] for row in schedule if row["op"] == "box"] == [0, 3, 6, 0, 3, 6]
    assert work.CENSUS_ATTEMPT == "D5-BOX-CENSUS-1"
    for foreign in ("site", "purchase", "order", "truck", "radiate"):
        with pytest.raises(ValueError, match="foreign op"):
            work.census_exchange_timeout_seconds(
                budget_table=work.census_budgets(), op=foreign
            )


# --- staging correctness ------------------------------------------------------


def test_staged_candidate_binds_the_census_lineage(staged):
    metadata = metadata_of(staged)
    assert metadata["schema"] == work.D5_CENSUS_PRELAUNCH_SCHEMA
    assert metadata["schema"] == "d5-box-census-prelaunch-v1"
    assert metadata["attempt"] == work.CENSUS_ATTEMPT == "D5-BOX-CENSUS-1"
    assert metadata["milestone"] == work.MILESTONE_CENSUS
    assert metadata["kind"] == work.KIND == "census"
    assert metadata["budgets"]["max_cost"] == 0
    assert metadata["budgets"]["planned_exchanges"] == 10
    assert metadata["budgets"]["requests"] == cc.CENSUS_REQUEST_BUDGET == 32
    assert metadata["budgets"]["expected_funds"] == FUNDS == 490257
    assert metadata["plan_policy"]["max_cost"] == 0
    assert metadata["plan_policy"]["plan_model_digest"] == work.census_plan().digest
    assert metadata["plan_policy"]["schedule_version"] == 1
    assert metadata["plan_policy"]["world"]["box_centres"] == [45748, 50862]
    assert metadata["plan_policy"]["world"]["spot_tiles"] == [50351, 50862]
    assert metadata["plan_policy"]["target_tile"] == 50351
    assert (
        metadata["prerequisite"]["after_save_sha256"]
        == work.PINNED_PREREQUISITE_AFTER_SAVE
        == "3748e00ce57bcb076466f50cac3776c202b4fd130d6c6071935e9d43e45420bd"
    )
    assert metadata["prerequisite"]["attempt"] == "D5-CORRIDOR-EXTENSION-3"
    assert metadata["world"]["save_sha256"] == work.PINNED_PREREQUISITE_AFTER_SAVE
    read_only = metadata["plan_policy"]["read_only"]
    assert read_only["schema"] == "d5-box-census-readonly-v1"
    assert read_only["permitted_ops"] == ["radius", "accept", "prod", "box"]
    assert read_only["max_cost"] == 0 and read_only["funds_readback_required"] is True
    assert metadata["cross_schedule_guard"]["schema"] == "d5-box-census-cross-guard-v1"
    assert metadata["bootstrap_command"] == "start_ai RoadProofCompany"


def test_no_consumed_attempt_or_lineage_name_in_the_staged_candidate(staged):
    """The consumed attempt ids of the other contract families appear zero
    times in the fresh census candidate's staged bytes."""
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
            "d5-accept-survey-prelaunch",
            "d5-freight-prelaunch-v1",
            "D5-FREIGHT-1",
        ):
            assert foreign not in text, (path, foreign)


def test_census_prerequisite_binding_must_be_the_pinned_a1_attempt():
    binding = work.census_prerequisite_binding()
    assert binding["attempt"] == "D5-CORRIDOR-EXTENSION-3"
    assert binding["milestone"] == "D5-CORRIDOR-EXTENSION"
    assert binding["save"] == "after.sav"
    assert (
        binding["save_sha256"]
        == "3748e00ce57bcb076466f50cac3776c202b4fd130d6c6071935e9d43e45420bd"
    )
    with pytest.raises(work.CensusStagingError, match="requires the pinned A1 prerequisite"):
        work.census_prerequisite_binding(
            Path("artifacts/experiments/d4-corridor-native-candidate-4")
        )
    with pytest.raises(work.CensusStagingError, match="requires the pinned A1 prerequisite"):
        work.census_prerequisite_binding(survey_native.PINNED_PREREQUISITES[1])
    survey_binding = survey_native.survey_prerequisite_binding(version=2)
    for name in ("attempt", "milestone", "retained_directory", "save_sha256"):
        assert binding[name] == survey_binding[name]


def test_staged_source_save_is_the_authoritative_a1_after_save(staged):
    metadata = metadata_of(staged)
    staged_save = Path(metadata["workspace"]) / "source.sav"
    assert sha256(staged_save) == work.PINNED_PREREQUISITE_AFTER_SAVE
    assert metadata["world"]["source_save"] == "after.sav"


def test_staged_composition_reuses_the_frozen_info_and_the_census_main(staged):
    composition, bridge_class, version = work.staged_census_composition()
    assert (bridge_class, version) == ("NetworkFreightProof", 1)
    workspace = Path(metadata_of(staged)["workspace"])
    staged_main = (workspace / "game" / work.SOURCE_SAVE_GS_NAME / "main.nut").read_bytes()
    assert staged_main == composition["main.nut"]
    assert b"class NetworkFreightProof extends D5CensusProof" in staged_main


def test_authorization_payload_rebuilds_and_no_claim_exists(staged):
    metadata = metadata_of(staged)
    seal = sha256(staged.directory / "PRELAUNCH.json")
    digest = work.staged_census_authorization_payload_digest(staged.directory)
    rebuilt = hashlib.sha256(
        canonical_authorization_bytes(authorization_payload(metadata, seal))
    ).hexdigest()
    assert rebuilt == digest
    assert not (staged.directory / "CLAIM.json").exists()
    assert not (staged.directory / "AUTHORIZATION.json").exists()
    assert claim_status(staged.directory) == "ABSENT"


def test_census_preflight_re_derives_every_binding(staged):
    metadata = work.census_preflight(staged)
    assert metadata["attempt"] == work.CENSUS_ATTEMPT


def test_census_preflight_refuses_seal_tampering(staged):
    target = staged.directory
    original = (target / "PRELAUNCH.json").read_bytes()
    seal_text = (target / "PRELAUNCH.sha256").read_text()
    metadata = json.loads(original)
    metadata["budgets"]["max_cost"] = 7
    (target / "PRELAUNCH.json").write_text(json.dumps(metadata, sort_keys=True, indent=2) + "\n")
    (target / "PRELAUNCH.sha256").write_text(sha256(target / "PRELAUNCH.json") + "\n")
    try:
        with pytest.raises(ValueError, match="budget pins drifted"):
            work.census_preflight(staged)
    finally:
        (target / "PRELAUNCH.json").write_bytes(original)
        (target / "PRELAUNCH.sha256").write_text(seal_text)


def test_census_preflight_refuses_attempt_and_schema_drift(staged):
    target = staged.directory
    original = (target / "PRELAUNCH.json").read_bytes()
    seal_text = (target / "PRELAUNCH.sha256").read_text()
    for tampered_name, tampered_value in (
        ("attempt", "D5-BOX-CENSUS-2"),
        ("schema", "d5-box-census-prelaunch-v2"),
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
            with pytest.raises(ValueError, match="drifted|lineage"):
                work.census_preflight(staged)
        finally:
            (target / "PRELAUNCH.json").write_bytes(original)
            (target / "PRELAUNCH.sha256").write_text(seal_text)


def test_census_preflight_refuses_a_drifted_schedule_or_box_grid(staged):
    target = staged.directory
    original = (target / "PRELAUNCH.json").read_bytes()
    seal_text = (target / "PRELAUNCH.sha256").read_text()
    for tamper in (
        lambda policy: policy["schedule"].pop(1),
        lambda policy: policy["schedule"][4].update(page_cursor=1),
        lambda policy: policy["box_grid"].update(page_rows=4),
        lambda policy: policy["read_only"].update(
            permitted_ops=["radius", "accept", "site"]
        ),
    ):
        metadata = json.loads(original)
        tamper(metadata["plan_policy"])
        (target / "PRELAUNCH.json").write_text(
            json.dumps(metadata, sort_keys=True, indent=2) + "\n"
        )
        (target / "PRELAUNCH.sha256").write_text(sha256(target / "PRELAUNCH.json") + "\n")
        try:
            with pytest.raises(ValueError, match="drifted"):
                work.census_preflight(staged)
        finally:
            (target / "PRELAUNCH.json").write_bytes(original)
            (target / "PRELAUNCH.sha256").write_text(seal_text)


def test_hypotheses_stay_hypotheses_over_the_retained_e49_receipt(staged):
    hypotheses = metadata_of(staged)["plan_policy"]["hypotheses"]
    assert hypotheses["state"] == "RETAINED_CENSUS_REBOUND"
    rows = hypotheses["spots"]
    assert rows[0]["tile"] == 50351 and rows[0]["hypothesis_eighths"] == 0
    assert rows[1]["tile"] == 50862 and rows[1]["hypothesis_eighths"] == 8
    assert all(row["kind"] == "HYPOTHESIS" for row in rows)
    assert [row["tile"] for row in rows] == list(cc.CENSUS_SPOT_TILES)
    assert hypotheses["production"]["hypothesis_units"] == 104
    assert hypotheses["production"]["exchange"] == "prod-00"
    receipt_path = Path(
        "artifacts/experiments/d5-accept-survey-native-candidate-2/receipt.json"
    )
    receipt = json.loads(receipt_path.read_text())
    assert receipt["observations"]["50351"]["value"] == 0
    assert receipt["observations"]["50862"]["value"] == 8
    assert receipt["production"] == 104
    assert hypotheses["source_sha256"] == sha256(receipt_path)


def test_census_hypotheses_name_absent_evidence_without_inventing(tmp_path, monkeypatch):
    fake_project = tmp_path
    (fake_project / "artifacts").mkdir(exist_ok=True)
    monkeypatch.setattr(work, "PROJECT", fake_project)
    absent = work.census_spot_hypotheses()
    assert absent["state"] == "RETAINED_CENSUS_ABSENT"
    assert absent["spots"] == [] and absent["production"] is None
    monkeypatch.undo()
    bound = work.census_spot_hypotheses()
    assert bound["state"] == "RETAINED_CENSUS_REBOUND"


def test_box_grid_and_expected_readback_policy_of_record(staged):
    metadata = metadata_of(staged)
    grid = metadata["plan_policy"]["box_grid"]
    assert grid["page_rows"] == 3
    assert grid["page_cursors"] == [0, 3, 6]
    assert grid["membership_limit"] == cc.BOX_MEMBERSHIP_LIMIT == 9
    assert grid["centres"] == [
        {"tile": 45748, "role": "producer"},
        {"tile": 50862, "role": "acceptor"},
    ]
    readback_policy = metadata["expected_readback"]
    assert sorted(readback_policy) == ["accept", "box", "prod", "radius", "receipt"]
    assert "CENSUS_GATE_UNDECIDED_OVERFLOW" in readback_policy["box"]
    assert "halts the census prefix-preservingly" in readback_policy["accept"]


# --- the exchange helper and the census frame replay parsing -----------------


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


def test_census_exchange_persists_request_and_response_pair(tmp_path):
    request = census_request("radius-00")
    response = census_reply_bytes(request)
    reply = _admin_frame(response + b"\0")
    readback = asyncio.run(work.census_exchange(_FakeSession(reply), request, tmp_path))
    assert readback.status == "READY" and readback.radius == 3
    assert (tmp_path / "radius-00-request.json").read_bytes() == request.to_bytes()
    assert (tmp_path / "radius-00-response.json").read_bytes() == response
    parsed = cc.CensusReadback.parse_for(request, response)
    assert parsed.digest == readback.digest


def test_census_exchange_refuses_malformed_truncated_and_stale_replies(tmp_path):
    request = census_request("radius-00")

    class Broken:
        async def send(self, frame):
            pass

        async def receive(self):
            return b""

    with pytest.raises(ConnectionError):
        asyncio.run(work.census_exchange(Broken(), request, tmp_path))
    # A reply correlated to a different attempt label is refused fail-closed.
    stale = _admin_frame(census_reply_bytes(request) + b"\0")
    stale_request = census_request("acc-01")
    with pytest.raises(ValueError):
        asyncio.run(work.census_exchange(_FakeSession(stale), stale_request, tmp_path))
    # Whatever the gateway sends that is not one gamescript response frame
    # can never become a measured census observation.
    with pytest.raises(ValueError):
        asyncio.run(
            work.census_exchange(
                _FakeSession(_admin_frame(b"\x00junk\x00")), request, tmp_path
            )
        )


def test_census_response_bounds_are_exactly_512(tmp_path):
    request = census_request("radius-00")
    assert work.MAX_CENSUS_REQUEST_BYTES == work.MAX_CENSUS_RESPONSE_BYTES == 512
    reply = _admin_frame(census_reply_bytes(request) + b"\0")
    readback = asyncio.run(work.census_exchange(_FakeSession(reply), request, tmp_path))
    assert readback.radius == 3
    over = json.dumps(
        {
            "protocol": 9,
            "op": "radius",
            "request_id": "radius-00",
            "plan": FREIGHT_SEAL,
            "company": 0,
            "max_cost": 0,
            "pickup": 45748,
            "delivery": 50351,
            "depot": 45487,
            "status": "READY",
            "funds": FUNDS,
            "cost": 0,
            "radius": 3,
            "pad": "x" * 700,
        },
        sort_keys=True,
    ).encode()
    from app.simulation.openttd.gamescript_transport import encode_gamescript

    with pytest.raises(ValueError):
        encode_gamescript(over)
    with pytest.raises(ValueError):
        work.decode_census_request(over)


def test_census_frame_replay_parser(tmp_path):
    request = census_request("radius-00")
    response = census_reply_bytes(request)
    reply = _admin_frame(response + b"\0")
    frames = [
        ["outbound", work.encode_census_request(request.to_bytes()).hex()],
        ["inbound", reply.hex()],
    ]
    (tmp_path / "frames.json").write_text(json.dumps(frames))
    outbound, requests, replies, request_positions, reply_positions = (
        work._parse_census_frames(tmp_path)
    )
    assert requests == [request]
    assert replies == [response]
    assert request_positions[request.to_bytes()] == 0
    assert set(reply_positions) == {response}
    from app.simulation.openttd.gamescript_transport import encode_gamescript

    with pytest.raises(ValueError, match="invalid CensusRequest"):
        junk = [["outbound", encode_gamescript(b'{"op":"site"}').hex()]]
        (tmp_path / "frames.json").write_text(json.dumps(junk))
        work._parse_census_frames(tmp_path)


# --- replay verification fail-closed behavior --------------------------------


def test_unconsumed_census_candidate_verifies_fail_closed(staged):
    verdict = work.verify_box_census_attempt(staged.directory)
    assert verdict == {
        "verification": "AUTHORIZATION_UNVERIFIED",
        "authorization_state": "CLAIM_ABSENT",
        "statement": (
            "the census candidate was never consumed by an operator "
            "authorization; no verified completion is possible"
        ),
    }
    assert claim_status(staged.directory) == "ABSENT"


def test_census_replay_refuses_a_claim_mismatched_to_its_seal(staged):
    target = staged.directory
    (target / "CLAIM.json").write_text(json.dumps(dict(prelaunch_digest="0" * 64)))
    try:
        with pytest.raises(ValueError, match="claim does not match"):
            work.verify_box_census_attempt(target)
    finally:
        (target / "CLAIM.json").unlink()


def _claim_engine(tmp_path, staged):
    """A retained-evidence directory with a self-consistent one-shot claim
    and a forced NATIVE_CENSUS_COMPLETE result label — but no operator
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
                status="NATIVE_CENSUS_COMPLETE",
                exchanges=list(EXCHANGES),
                requests=10,
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


def test_census_replay_never_verifies_a_forced_label_without_authorization(
    staged, tmp_path
):
    target = _claim_engine(tmp_path, staged)
    metadata = json.loads((target / "PRELAUNCH.json").read_text())
    seal = sha256(target / "PRELAUNCH.json")
    claims = json.loads((target / "CLAIM.json").read_text())
    assert d5.replay_authorization_state(target, metadata, seal, claims) is not None
    verdict = work.verify_box_census_attempt(target)
    assert verdict["verification"] == "AUTHORIZATION_UNVERIFIED"
    assert verdict["authorization_state"] not in (None, "CLAIM_ABSENT")


def test_census_replay_refuses_an_unreferenced_stray_file(staged, tmp_path):
    target = _claim_engine(tmp_path, staged)
    (target / "stray.txt").write_text("not in the manifest")
    with pytest.raises(ValueError, match="exhaustive"):
        work.verify_box_census_attempt(target)
    (target / "stray.txt").unlink()
    verdict = work.verify_box_census_attempt(target)
    assert verdict["verification"] == "AUTHORIZATION_UNVERIFIED"


def test_census_replay_refuses_an_unknown_prelaunch_schema(staged, tmp_path):
    target = tmp_path / "alien"
    target.mkdir()
    metadata = metadata_of(staged)
    metadata["schema"] = d5.D5_FREIGHT_PRELAUNCH_SCHEMA  # the freight lineage, not census
    (target / "PRELAUNCH.json").write_text(json.dumps(metadata, sort_keys=True, indent=2) + "\n")
    (target / "PRELAUNCH.sha256").write_text(sha256(target / "PRELAUNCH.json") + "\n")
    (target / "CLAIM.json").write_text(
        json.dumps(dict(prelaunch_digest=sha256(target / "PRELAUNCH.json"), consumed=True))
    )
    (target / "artifact-manifest.sha256").write_text(manifest(target))
    verdict = work.verify_box_census_attempt(target)
    assert verdict["authorization_state"] == "UNKNOWN_PRELAUNCH_SCHEMA"


# --- the single-attempt identity: its bindings cannot drift -------------------


def test_identity_pairs_the_record_with_the_census_plan_only(staged):
    metadata = metadata_of(staged)
    assert work.verify_box_census_attempt_identity(metadata, plan=work.census_plan())
    for tampered_name, tampered_value in (
        ("attempt", "D5-BOX-CENSUS-2"),
        ("schema", "d5-box-census-prelaunch-v2"),
        ("kind", "survey"),
        ("milestone", "D5-BOX-CENSUS-2"),
    ):
        crossed = json.loads(json.dumps(metadata))
        crossed[tampered_name] = tampered_value
        with pytest.raises(ValueError, match="identity drifted|not the D5 census lineage"):
            work.verify_box_census_attempt_identity(crossed, plan=work.census_plan())


def test_identity_refuses_a_crossed_plan_model(staged):
    metadata = metadata_of(staged)
    with pytest.raises(work.CensusStagingError, match="BoxCensusPlan"):
        work.verify_box_census_attempt_identity(metadata, plan=d5.freight_plan())
    with pytest.raises(work.CensusStagingError, match="BoxCensusPlan"):
        work.verify_box_census_attempt_identity(
            metadata, plan=survey_native.survey_plan_v2()
        )


def test_identity_refuses_a_drifted_prerequisite_or_world_or_policy(staged):
    metadata = metadata_of(staged)
    for tamper in (
        lambda m: m["prerequisite"].update(after_save_sha256="9" * 64),
        lambda m: m["world"].update(save_sha256="9" * 64),
        lambda m: m["plan_policy"].update(max_cost=5),
        lambda m: m["plan_policy"].update(box_grid=dict(schema="d5-box-census-box-grid-v1")),
        lambda m: m["plan_policy"].update(hypotheses=dict(state="RETAINED_CENSUS_ABSENT")),
    ):
        crossed = json.loads(json.dumps(metadata))
        tamper(crossed)
        with pytest.raises(ValueError, match="drifted|floated"):
            work.verify_box_census_attempt_identity(crossed, plan=work.census_plan())


# --- exit-status discipline ---------------------------------------------------


def test_census_exit_status_zero_only_for_the_verified_completion():
    assert (
        work.census_exit_status(
            dict(
                verified=True,
                status="NATIVE_CENSUS_COMPLETE",
                cleanup_complete=True,
                state_changed=False,
            )
        )
        == 0
    )
    for bad in (
        dict(
            verified=True,
            status="NATIVE_CENSUS_COMPLETE",
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
            status="NATIVE_CENSUS_COMPLETE",
            cleanup_complete=True,
            state_changed=True,
        ),
        dict(verified=False, status="FAILED", cleanup_complete=True, state_changed=False),
    ):
        assert work.census_exit_status(bad) == 1
    assert work.census_verdict_exit_status(dict(verification="CENSUS_COMPLETION_VERIFIED")) == 0
    assert (
        work.census_verdict_exit_status(dict(verification="PHASE_HALTED_EVIDENCE_PRESERVED"))
        == 1
    )


# --- the synthetic consumed census attempt ------------------------------------


_PICKUP_MEMBERS = [
    {"id": 0, "tile": 45748, "p": 104, "a": 0},
    {"id": 2, "tile": 45751, "p": 0, "a": 0},
    {"id": 5, "tile": 44981, "p": 0, "a": 0},
]
_DELIVERY_MEMBERS = [{"id": 1, "tile": 50862, "p": 0, "a": 1}]


def _box_page_rows(centre: int, cursor: int) -> list[dict]:
    members = _PICKUP_MEMBERS if centre == 45748 else _DELIVERY_MEMBERS
    return members[cursor : cursor + 3]


def _consumed_census_exchanges(seal: str, schedule):
    plan = work.census_plan()
    exchanges = []
    for entry in schedule:
        exchange = str(entry["exchange"])
        request = work._census_exchange_request(entry, seal, plan)
        if request.op == "box":
            page_centre, page_cursor = request.tile, request.cursor
            members = _PICKUP_MEMBERS if page_centre == 45748 else _DELIVERY_MEMBERS
            assert page_centre is not None and page_cursor is not None
            body = census_reply_bytes(
                request,
                count=len(members),
                more=False,
                rows=_box_page_rows(page_centre, page_cursor),
            )
        elif request.op == "accept":
            # The retained E49 spot facts: acc-00 measures 0, acc-01 measures 8.
            body = census_reply_bytes(request, accept=8 if exchange == "acc-01" else 0)
        elif request.op == "prod":
            body = census_reply_bytes(request, prod=104)
        else:
            body = census_reply_bytes(request, radius=3)
        readback = cc.CensusReadback.parse_for(request, body)
        exchanges.append((request, readback))
    return exchanges, plan


def _wire_of(readback) -> bytes:
    return json.dumps(
        readback.model_dump(mode="json", exclude_none=True), separators=(",", ":")
    ).encode()


@pytest.fixture(scope="module")
def consumed_census_attempt(tmp_path_factory):
    prepared = work.prepare_box_census_candidate(
        tmp_path_factory.mktemp("census-consumed") / "candidate"
    )
    directory = prepared.directory
    seal = sha256(directory / "PRELAUNCH.json")
    metadata = json.loads((directory / "PRELAUNCH.json").read_text())
    exchanges, plan = _consumed_census_exchanges(seal, metadata["plan_policy"]["schedule"])
    frames = []
    for request, readback in exchanges:
        wire = _wire_of(readback)
        (directory / (request.request_id + "-request.json")).write_bytes(request.to_bytes())
        (directory / (request.request_id + "-response.json")).write_bytes(wire)
        frames.append(["outbound", work.encode_census_request(request.to_bytes()).hex()])
        frames.append(["inbound", _admin_frame(wire + b"\0").hex()])
    (directory / "frames.json").write_text(json.dumps(frames))
    phase = cc.census_phase_outcome(exchanges, prelaunch_digest=seal, plan=plan)
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
                requests=10,
                exchanges=[request.request_id for request, _ in exchanges],
                last_status="READY",
                command_accepted=True,
                state_changed=False,
                verified=True,
                status="NATIVE_CENSUS_COMPLETE",
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
    yield directory, exchanges, seal, plan
    prepared.spec.workspace.close()


def test_replay_verifies_a_fully_consumed_census_frame_sequence(
    consumed_census_attempt, monkeypatch
):
    directory, exchanges, _, _ = consumed_census_attempt
    monkeypatch.setattr(work, "replay_authorization_state", lambda *a, **k: None)
    verdict = work.verify_box_census_attempt(directory)
    assert verdict["verification"] == "CENSUS_COMPLETION_VERIFIED"
    assert verdict["receipt"]["phase"]["verification"] == "CENSUS_COMPLETE"
    assert verdict["receipt"]["phase"]["radius"] == 3
    assert verdict["receipt"]["phase"]["production"] == 104
    assert verdict["receipt"]["phase"]["funds"] == FUNDS
    assert verdict["receipt"]["before_save_sha256"] == "9" * 64
    assert verdict["receipt"]["phase"]["observations"]["50351"]["value"] == 0
    assert verdict["receipt"]["phase"]["observations"]["50862"]["value"] == 8
    phase = verdict["receipt"]["phase"]
    assert phase["branch8"]["verdict"] == "CENSUS_GATE_PASSES"
    assert phase["branch8"]["role_counts"] == {"producer": 1, "acceptor": 1}
    boxes = phase["boxes"]
    assert boxes["45748"]["role_filtered"] == [{"id": 0, "tile": 45748}]
    assert boxes["50862"]["role_filtered"] == [{"id": 1, "tile": 50862}]
    assert boxes["45748"]["count"] == 3
    assert [page["row_count"] for page in boxes["45748"]["pages"]] == [3, 0, 0]
    assert [page["more"] for page in boxes["45748"]["pages"]] == [False, False, False]
    assert len(exchanges) == 10
    assert work.census_verdict_exit_status(verdict) == 0


def test_replay_fails_closed_on_a_tampered_retained_census_receipt(
    consumed_census_attempt, monkeypatch
):
    directory, _, _, _ = consumed_census_attempt
    monkeypatch.setattr(work, "replay_authorization_state", lambda *a, **k: None)
    before = json.loads((directory / "receipt.json").read_text())
    (directory / "receipt.json").write_text(
        json.dumps(dict(before, production=105), sort_keys=True, indent=2) + "\n"
    )
    (directory / "artifact-manifest.sha256").write_text(d5.manifest(directory))
    with pytest.raises(ValueError, match="receipt replay mismatch"):
        work.verify_box_census_attempt(directory)
    (directory / "receipt.json").write_text(json.dumps(before, sort_keys=True, indent=2) + "\n")
    (directory / "artifact-manifest.sha256").write_text(d5.manifest(directory))


def test_replay_fails_closed_on_a_tampered_retained_response_inventory(
    consumed_census_attempt, monkeypatch
):
    directory, _, _, _ = consumed_census_attempt
    monkeypatch.setattr(work, "replay_authorization_state", lambda *a, **k: None)
    victim = directory / "acc-01-response.json"
    stored = victim.read_bytes()
    victim.unlink()
    (directory / "artifact-manifest.sha256").write_text(d5.manifest(directory))
    with pytest.raises(ValueError, match="lacks its durable response file"):
        work.verify_box_census_attempt(directory)
    victim.write_bytes(stored)
    (directory / "artifact-manifest.sha256").write_text(d5.manifest(directory))
    verdict = work.verify_box_census_attempt(directory)
    assert verdict["verification"] == "CENSUS_COMPLETION_VERIFIED"


def test_replay_fails_closed_on_a_result_label_the_evidence_contradicts(
    consumed_census_attempt, monkeypatch
):
    directory, _, _, _ = consumed_census_attempt
    monkeypatch.setattr(work, "replay_authorization_state", lambda *a, **k: None)
    before = json.loads((directory / "result.json").read_text())
    (directory / "result.json").write_text(
        json.dumps(dict(before, native_launches=2), sort_keys=True, indent=2) + "\n"
    )
    (directory / "artifact-manifest.sha256").write_text(d5.manifest(directory))
    with pytest.raises(ValueError, match="contradicts"):
        work.verify_box_census_attempt(directory)
    (directory / "result.json").write_text(json.dumps(before, sort_keys=True, indent=2) + "\n")
    (directory / "artifact-manifest.sha256").write_text(d5.manifest(directory))


# --- the wire-to-Nut pin binding: the Python schedule can never drift ---------


def test_nut_pin_table_binds_to_the_python_census_schedule():
    """The shipped census GameScript's `census_planned` rows and its pin
    table are read from the package bytes and must equal the wire contract's
    schedule exactly: ids/ops in order, the two box centres and the two
    chain-continuity spots."""
    text = (work.CENSUS_PACKAGE / "main.nut").read_text()
    planned_match = re.search(r"census_planned = \[(.*?)\n    \]", text, re.DOTALL)
    assert planned_match, "the shipped package lost its census_planned table"
    rows = re.findall(r'\["([a-z0-9-]+)",\s*"([a-z]+)",\s*"[A-Z]+"\]', planned_match.group(1))
    assert [exchange for exchange, _op in rows] == EXCHANGES
    assert set(rows) == {
        ("radius-00", "radius"),
        ("acc-00", "accept"),
        ("acc-01", "accept"),
        ("prod-00", "prod"),
        ("pbox-00", "box"),
        ("pbox-01", "box"),
        ("pbox-02", "box"),
        ("dbox-00", "box"),
        ("dbox-01", "box"),
        ("dbox-02", "box"),
    }
    for marker, name, value in (
        (r"PBOX_CENTRE = (\d+)", "PBOX_CENTRE", "45748"),
        (r"DBOX_CENTRE = (\d+)", "DBOX_CENTRE", "50862"),
        (r"SPOT_CONTROL = (\d+)", "SPOT_CONTROL", "50351"),
        (r"SPOT_STOP = (\d+)", "SPOT_STOP", "50862"),
    ):
        found = re.search(marker, text)
        assert found is not None, f"the shipped package lost its {name} pin"
        assert found.group(1) == value
    native_schedule = work.census_schedule()
    for row in native_schedule:
        if row["op"] == "box":
            expected = cc.BOX_EXCHANGE_SPECS[row["exchange"]]
            assert (row["observation_tile"], row["page_cursor"]) == expected


def test_census_bytes_never_parse_into_the_consumed_contract_families():
    """The protocol-9 census request cannot be retrofitted into the protocol-5
    or -6 wire contracts."""
    from app.simulation.openttd.corridor_accept_survey import SurveyReadback

    census = census_request("radius-00")
    with pytest.raises(Exception):
        SurveyReadback.parse_for(survey_request(), census.to_bytes())
