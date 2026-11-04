"""Offline staging/replay tests for the D5-CARGOFLOW-2 attempt record.

The record under test is
``app/simulation/openttd/proof/corridor_cargoflow2_native.py`` — the fresh
one-attempt delivery candidate staging, its preflight rehearsals, the
request-day authority, the exchange persistence/bounds and the offline
replay verification that re-derives every retained binding (mirroring the
protocol-10 probe trio's split shape). Nothing here launches OpenTTD,
connects to an AdminPort or writes any native state: only module-scoped
own-workspace candidates and synthetic replay evidence are touched.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import re
from pathlib import Path
from typing import cast

import pytest

import app.simulation.openttd.proof.corridor_accept_survey_native as survey_native
import app.simulation.openttd.proof.corridor_box_census_native as census_native
import app.simulation.openttd.proof.corridor_cargoflow2_native as work
import app.simulation.openttd.proof.corridor_cargoflow_native as probe10
import app.simulation.openttd.proof.corridor_freight_native as d5
import app.simulation.openttd.proof.corridor_freight_v2_native as freight_v2_native
from app.simulation.openttd import corridor_cargoflow2 as cf
from app.simulation.openttd.proof.harness import manifest, sha256
from app.simulation.openttd.proof.operator_authorization import (
    authorization_payload,
    canonical_authorization_bytes,
)
from app.simulation.openttd.proof.terrain_clearing import claim_status
from tests.test_corridor_accept_survey import SEAL as SURVEY_SEAL
from tests.test_corridor_accept_survey_native import _admin_frame
from tests.test_corridor_cargoflow2 import (
    ANCHOR,
    EXCHANGES,
    FUNDS,
    PRELAUNCH,
    SCHEDULE,
    VEHICLE,
    built_ladder,
)
from tests.test_corridor_freight import PRELAUNCH as FREIGHT_SEAL

PLAN = work.cargoflow2_pipeline_plan()


def cargoflow2_request(entry_index: int, seal: str = PRELAUNCH) -> cf.Cargoflow2Request:
    return work.cargoflow2_request_table(PLAN, seal, vehicle=VEHICLE)[entry_index]


def _wire_of(readback) -> bytes:
    return json.dumps(
        readback.model_dump(mode="json", exclude_none=True), separators=(",", ":")
    ).encode()


@pytest.fixture(scope="module")
def staged(tmp_path_factory):
    prepared = work.prepare_cargoflow2_candidate(
        tmp_path_factory.mktemp("cargoflow2-staging") / "candidate"
    )
    yield prepared
    prepared.spec.workspace.close()


def metadata_of(prepared) -> dict:
    return json.loads((prepared.directory / "PRELAUNCH.json").read_text())


# --- the plan-bound pipeline and the cross-session guards --------------------


def test_cargoflow2_pipeline_accepts_a_cargoflow2plan_only():
    plan = work.cargoflow2_pipeline_plan()
    assert work._require_cargoflow2_plan(plan).digest == plan.digest
    for foreign in (
        d5.freight_plan(),
        census_native.census_plan(),
        survey_native.survey_plan_v2(),
        freight_v2_native.freight_plan_v2(),
        dict(digest=plan.digest),
    ):
        with pytest.raises(work.Cargoflow2StagingError, match="Cargoflow2Plan"):
            work._require_cargoflow2_plan(foreign)


def test_attempt_schedule_is_the_pinned_ladder_of_record():
    schedule = work.cargoflow2_schedule()
    assert [row["exchange"] for row in schedule] == list(EXCHANGES)
    assert [row["offset"] for row in schedule] == (
        [-1] * 11 + list(cf.CARGOFLOW2_FLOW_OFFSETS) + [cf.CARGOFLOW2_TAIL_OFFSET] * 2
    )
    assert [row["op"] for row in schedule] == (
        ["site", "engine", "purchase", "vread", "order", "order", "order-read",
         "monitor", "start", "vread", "arrive-watch"]
        + ["flow"] * 12
        + ["finance", "finish"]
    )
    assert work.D5_CARGOFLOW2_ATTEMPT == "D5-CARGOFLOW-2"
    assert work.D5_CARGOFLOW2_PRELAUNCH_SCHEMA == "d5-cargoflow2-prelaunch-v1"
    budgets = work.cargoflow2_budgets()
    assert budgets["launches"] == 1 and budgets["retries"] == 0
    assert budgets["requests"] == 32 and budgets["planned_exchanges"] == 25
    assert budgets["max_cost"] == 5000 and budgets["total_seconds"] == 900
    # Instant exchanges keep the request budget; waits ride the window.
    for op in ("site", "engine", "purchase", "vread", "order", "order-read",
               "monitor", "start"):
        assert work.cargoflow2_exchange_timeout_seconds(
            budget_table=budgets, op=op, offset=-1
        ) == budgets["request_seconds"]
    assert work.cargoflow2_exchange_timeout_seconds(
        budget_table=budgets, op="arrive-watch", offset=-1
    ) == budgets["watch_seconds"] + budgets["exchange_margin_seconds"]
    assert work.cargoflow2_exchange_timeout_seconds(
        budget_table=budgets, op="flow", offset=0
    ) == budgets["request_seconds"]
    assert work.cargoflow2_exchange_timeout_seconds(
        budget_table=budgets, op="flow", offset=5
    ) == budgets["watch_seconds"] + budgets["exchange_margin_seconds"]
    assert work.cargoflow2_exchange_timeout_seconds(
        budget_table=budgets, op="finance", offset=55
    ) == budgets["request_seconds"]
    with pytest.raises(ValueError, match="foreign ladder offset"):
        work.cargoflow2_exchange_timeout_seconds(budget_table=budgets, op="flow", offset=56)
    with pytest.raises(ValueError, match="flow-11 economy day"):
        work.cargoflow2_exchange_timeout_seconds(budget_table=budgets, op="finance", offset=5)
    with pytest.raises(ValueError, match="no delivery budget"):
        work.cargoflow2_exchange_timeout_seconds(budget_table=budgets, op="radius", offset=-1)


def test_other_native_sessions_never_carry_the_delivery_frames():
    """A delivery (protocol 11) frame cannot travel on any older native
    session, and none of their frames can ride the delivery session; every
    refusal lands before any handler can run."""
    d2 = object.__new__(work.Cargoflow2SecureSession)
    d2._state = d5.AuthState.ACTIVE
    census = object.__new__(census_native.CensusSecureSession)
    census._state = d5.AuthState.ACTIVE
    survey = object.__new__(survey_native.SurveySecureSession)
    survey._state = d5.AuthState.ACTIVE
    probe = object.__new__(probe10.CargoflowSecureSession)
    probe._state = d5.AuthState.ACTIVE
    delivery_frame = work.encode_cargoflow2_request(cargoflow2_request(0).to_bytes())
    probe_frame = probe10.encode_cargoflow_request(
        probe10._cargoflow_exchange_request(
            probe10.cargoflow_schedule()[0],
            FREIGHT_SEAL,
            probe10.cargoflow_pipeline_plan(),
        ).to_bytes()
    )
    d2.validate_outbound(delivery_frame)
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
        census.validate_outbound(delivery_frame)
    with pytest.raises(Exception):
        survey.validate_outbound(delivery_frame)
    with pytest.raises(Exception):
        probe.validate_outbound(delivery_frame)
    with pytest.raises(Exception):
        d2.validate_outbound(probe_frame)


# --- staging correctness ------------------------------------------------------


def test_staged_candidate_binds_the_attempt_lineage(staged):
    metadata = metadata_of(staged)
    assert metadata["schema"] == work.D5_CARGOFLOW2_PRELAUNCH_SCHEMA
    assert metadata["schema"] == "d5-cargoflow2-prelaunch-v1"
    assert metadata["attempt"] == work.D5_CARGOFLOW2_ATTEMPT == "D5-CARGOFLOW-2"
    assert metadata["milestone"] == work.MILESTONE_CARGOFLOW2
    assert metadata["kind"] == work.KIND == "cargoflow2"
    assert metadata["budgets"]["max_cost"] == 5000
    assert metadata["budgets"]["planned_exchanges"] == 25
    assert metadata["budgets"]["requests"] == cf.CARGOFLOW2_REQUEST_BUDGET == 32
    assert metadata["budgets"]["expected_start_funds"] == FUNDS == 489650
    assert metadata["budgets"]["launches"] == 1 and metadata["budgets"]["retries"] == 0
    policy = metadata["plan_policy"]
    assert policy["max_cost"] == 5000
    assert policy["plan_model_digest"] == PLAN.digest
    assert policy["schedule_version"] == 1
    assert policy["command"] == "purchase"
    assert policy["target_tile"] == 45748
    assert (
        metadata["prerequisite"]["after_save_sha256"]
        == work.PINNED_PREREQUISITE_AFTER_SAVE
        == "183b20273a54ebe1a2cd9306145a9ea820bbd6114b1608c42079b4e1b1efe6a6"
    )
    assert metadata["prerequisite"]["attempt"] == "D5-F12-DEPOT-3"
    assert metadata["prerequisite"]["milestone"] == "D5-F12-DEPOT"
    assert metadata["world"]["save_sha256"] == work.PINNED_PREREQUISITE_AFTER_SAVE
    assert metadata["world"]["source_save"] == "after.sav"
    read_only = policy["read_only"]
    assert read_only["schema"] == cf.CARGOFLOW2_READ_ONLY_SCHEMA
    assert read_only["permitted_ops"] == list(cf.CARGOFLOW2_OPS)
    assert read_only["max_cost"] == 0 and read_only["funds_readback_required"] is True
    grid = policy["ladder_grid"]
    assert grid["schema"] == "d5-cargoflow2-ladder-grid-v1"
    assert grid["planned_exchanges"] == 25 and grid["cadence_days"] == 5
    assert grid["span_days"] == 55 and grid["offsets"] == list(cf.CARGOFLOW2_FLOW_OFFSETS)
    assert grid["wait_ticks"] == 2048 and grid["day_budget"] == 60
    assert metadata["cross_schedule_guard"]["schema"] == "d5-cargoflow2-cross-guard-v1"
    assert metadata["bootstrap_command"] == "start_ai RoadProofCompany"


def test_no_consumed_attempt_or_lineage_name_in_the_staged_candidate(staged):
    """The consumed attempt ids of the other contract families appear zero
    times in the fresh delivery candidate's staged bytes."""
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
            "D5-CARGOFLOW-1",
            "d5-cargoflow-prelaunch-v1",
        ):
            assert foreign not in text, (path, foreign)


def test_cargoflow2_prerequisite_binding_must_be_the_pinned_depot_attempt():
    binding = work.cargoflow2_prerequisite_binding()
    assert binding["attempt"] == "D5-F12-DEPOT-3"
    assert binding["milestone"] == "D5-F12-DEPOT"
    assert binding["save"] == "after.sav"
    assert binding["save_sha256"] == work.PINNED_PREREQUISITE_AFTER_SAVE
    assert binding["schema"] == work.D5_CARGOFLOW2_PREREQUISITE_SCHEMA
    assert "F12_MUTATION_COMPLETION_VERIFIED" in binding["verification"]
    assert "attempt-scoped" in binding["verification"]
    shared = freight_v2_native.prerequisite_binding(freight_v2_native.DEPOT_PREREQUISITE)
    for name in ("attempt", "milestone", "retained_directory", "save_sha256"):
        assert binding[name] == shared[name]
    with pytest.raises(work.Cargoflow2StagingError, match="pinned depot prerequisite"):
        work.cargoflow2_prerequisite_binding(
            Path("artifacts/experiments/d4-corridor-native-candidate-4")
        )
    with pytest.raises(work.Cargoflow2StagingError, match="pinned depot prerequisite"):
        work.cargoflow2_prerequisite_binding(survey_native.PINNED_PREREQUISITES[1])


def test_staged_source_save_is_the_authoritative_depot_after_save(staged):
    metadata = metadata_of(staged)
    staged_save = Path(metadata["workspace"]) / "source.sav"
    assert sha256(staged_save) == work.PINNED_PREREQUISITE_AFTER_SAVE
    assert metadata["world"]["source_save"] == "after.sav"


def test_staged_composition_reuses_the_frozen_info_and_the_attempt_main(staged):
    composition, bridge_class, version = work.staged_cargoflow2_composition()
    assert (bridge_class, version) == ("NetworkFreightProof", 1)
    workspace = Path(metadata_of(staged)["workspace"])
    staged_main = (workspace / "game" / work.SOURCE_SAVE_GS_NAME / "main.nut").read_bytes()
    assert staged_main == composition["main.nut"]
    assert b"class NetworkFreightProof extends D5CargoFlow2Proof" in staged_main


def test_authorization_payload_rebuilds_and_no_claim_exists(staged):
    metadata = metadata_of(staged)
    seal = sha256(staged.directory / "PRELAUNCH.json")
    digest = work.staged_cargoflow2_authorization_payload_digest(staged.directory)
    rebuilt = hashlib.sha256(
        canonical_authorization_bytes(authorization_payload(metadata, seal))
    ).hexdigest()
    assert rebuilt == digest
    assert not (staged.directory / "CLAIM.json").exists()
    assert not (staged.directory / "AUTHORIZATION.json").exists()
    assert claim_status(staged.directory) == "ABSENT"


def test_funds_model_gate_is_the_pinned_founding_construction(staged):
    gate = work.cargoflow2_funds_model_gate()
    assert metadata_of(staged)["plan_policy"]["funds_model"] == gate
    assert gate["schema"] == "d5-cargoflow2-funds-model-of-record-v1"
    assert gate["start_funds"] == FUNDS
    assert gate["purchase_quote"] == 4429
    assert gate["launch_day"] == 712228 and gate["day_budget"] == 60


def test_cargoflow2_preflight_re_derives_every_binding(staged):
    metadata = work.cargoflow2_preflight(staged)
    assert metadata["attempt"] == work.D5_CARGOFLOW2_ATTEMPT


def test_cargoflow2_preflight_refuses_seal_tampering(staged):
    target = staged.directory
    original = (target / "PRELAUNCH.json").read_bytes()
    seal_text = (target / "PRELAUNCH.sha256").read_text()
    metadata = json.loads(original)
    metadata["budgets"]["max_cost"] = 7
    (target / "PRELAUNCH.json").write_text(json.dumps(metadata, sort_keys=True, indent=2) + "\n")
    (target / "PRELAUNCH.sha256").write_text(sha256(target / "PRELAUNCH.json") + "\n")
    try:
        with pytest.raises(ValueError, match="budget pins drifted"):
            work.cargoflow2_preflight(staged)
    finally:
        (target / "PRELAUNCH.json").write_bytes(original)
        (target / "PRELAUNCH.sha256").write_text(seal_text)


def test_cargoflow2_preflight_refuses_attempt_and_lineage_drift(staged):
    target = staged.directory
    original = (target / "PRELAUNCH.json").read_bytes()
    seal_text = (target / "PRELAUNCH.sha256").read_text()
    for tampered_name, tampered_value in (
        ("attempt", "D5-CARGOFLOW-3"),
        ("schema", "d5-cargoflow2-prelaunch-v2"),
        ("kind", "cargoflow"),
        ("milestone", "D5-BOX-CENSUS"),
    ):
        metadata = json.loads(original)
        metadata[tampered_name] = tampered_value
        (target / "PRELAUNCH.json").write_text(
            json.dumps(metadata, sort_keys=True, indent=2) + "\n"
        )
        (target / "PRELAUNCH.sha256").write_text(sha256(target / "PRELAUNCH.json") + "\n")
        try:
            with pytest.raises(ValueError, match="lineage|identity"):
                work.cargoflow2_preflight(staged)
        finally:
            (target / "PRELAUNCH.json").write_bytes(original)
            (target / "PRELAUNCH.sha256").write_text(seal_text)


def test_cargoflow2_preflight_refuses_a_drifted_schedule_grid_scope_or_world(staged):
    target = staged.directory
    original = (target / "PRELAUNCH.json").read_bytes()
    seal_text = (target / "PRELAUNCH.sha256").read_text()
    for tamper in (
        lambda policy: policy["schedule"].pop(1),
        lambda policy: policy["schedule"][11].update(offset=10),
        lambda policy: policy["ladder_grid"].update(span_days=50),
        lambda policy: policy["read_only"].update(permitted_ops=["site"]),
        lambda policy: policy["world"].update(founding_loan=0),
    ):
        metadata = json.loads(original)
        tamper(metadata["plan_policy"])
        (target / "PRELAUNCH.json").write_text(
            json.dumps(metadata, sort_keys=True, indent=2) + "\n"
        )
        (target / "PRELAUNCH.sha256").write_text(sha256(target / "PRELAUNCH.json") + "\n")
        try:
            with pytest.raises(ValueError, match="drifted"):
                work.cargoflow2_preflight(staged)
        finally:
            (target / "PRELAUNCH.json").write_bytes(original)
            (target / "PRELAUNCH.sha256").write_text(seal_text)


def test_attempt_hypotheses_stay_hypotheses_over_the_retained_receipt(staged):
    hypotheses = metadata_of(staged)["plan_policy"]["hypotheses"]
    assert work.cargoflow2_hypotheses() == hypotheses
    assert hypotheses["state"] == "RETAINED_PROBE_REBOUND"
    rows = hypotheses["samples"]
    assert rows[0]["offset"] == 0 and rows[0]["stock_pickup"] == -1
    assert rows[0]["stock_bay"] == 0 and rows[0]["wait_pickup"] == 0
    assert rows[0]["wait_bay"] == 0 and rows[0]["kind"] == "HYPOTHESIS"
    assert [row["offset"] for row in rows] == list(range(0, 35, 5))
    assert all(row["kind"] == "HYPOTHESIS" for row in rows)
    assert hypotheses["source"] == (
        "artifacts/experiments/d5-corridor-cargoflow-native-candidate-1/result.json"
    )
    receipt_path = Path(
        "artifacts/experiments/d5-corridor-cargoflow-native-candidate-1/result.json"
    )
    receipt = json.loads(receipt_path.read_text())
    assert receipt["phase"]["samples"]["0"]["stock_pickup"] == -1
    assert receipt["phase"]["samples"]["30"]["stock_pickup"] == -1
    assert hypotheses["source_sha256"] == sha256(receipt_path)


def test_attempt_hypotheses_name_absent_evidence_without_inventing(tmp_path, monkeypatch):
    fake_project = tmp_path
    (fake_project / "artifacts").mkdir(exist_ok=True)
    monkeypatch.setattr(work, "PROJECT", fake_project)
    absent = work.cargoflow2_hypotheses()
    assert absent["state"] == "RETAINED_PROBE_ABSENT"
    assert absent["samples"] == []
    monkeypatch.undo()
    bound = work.cargoflow2_hypotheses()
    assert bound["state"] == "RETAINED_PROBE_REBOUND"


def test_expected_readback_policy_tells_the_attempt_story(staged):
    policy = metadata_of(staged)["expected_readback"]
    assert sorted(policy) == ["arrival", "chain", "funds", "ladder", "receipt", "verdicts"]
    assert "the purchase realizes exactly its pinned tested quote" in policy["chain"]
    assert "a timeout is a terminal ARRIVE_TIMEOUT" in policy["arrival"]
    assert "an overshoot is WINDOW_EXHAUSTED" in policy["ladder"]
    assert "residual ≠ 0 is a halt" in policy["funds"]
    assert "CARGOFLOW2_GATE_UNDECIDED_INCOMPLETE" in policy["verdicts"]
    assert "leaves the attempt incomplete forever" in policy["receipt"]


# --- the exchange helper and the delivery frame replay parsing ----------------


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


def test_cargoflow2_exchange_persists_request_and_response_pair(tmp_path):
    request = cargoflow2_request(0)
    response = _wire_of(built_ladder()[0][1])
    reply = _admin_frame(response + b"\0")
    readback = asyncio.run(work.cargoflow2_exchange(_FakeSession(reply), request, tmp_path))
    assert readback.status == "READY"
    assert (tmp_path / "site-00-request.json").read_bytes() == request.to_bytes()
    assert (tmp_path / "site-00-response.json").read_bytes() == response
    parsed = cf.Cargoflow2Readback.parse_for(request, response)
    assert parsed.status == readback.status


def test_cargoflow2_exchange_refuses_malformed_truncated_and_stale_replies(tmp_path):
    request = cargoflow2_request(0)

    class Broken:
        async def send(self, frame):
            pass

        async def receive(self):
            return b""

    with pytest.raises(ConnectionError):
        asyncio.run(work.cargoflow2_exchange(Broken(), request, tmp_path))
    # A reply correlated to a different ladder label is refused fail-closed.
    stale = _admin_frame(_wire_of(built_ladder()[0][1]) + b"\0")
    stale_request = cargoflow2_request(EXCHANGES.index("flow-04"))
    with pytest.raises(ValueError):
        asyncio.run(work.cargoflow2_exchange(_FakeSession(stale), stale_request, tmp_path))
    # Whatever the gateway sends that is not one gamescript response frame
    # can never become a measured delivery observation.
    with pytest.raises(ValueError):
        asyncio.run(
            work.cargoflow2_exchange(
                _FakeSession(_admin_frame(b"\x00junk\x00")), request, tmp_path
            )
        )


def test_cargoflow2_response_bounds_are_exactly_512_and_1400(tmp_path):
    request = cargoflow2_request(0)
    assert work.MAX_CARGOFLOW2_REQUEST_BYTES == 512
    assert work.MAX_CARGOFLOW2_RESPONSE_BYTES == 1400
    reply = _admin_frame(_wire_of(built_ladder()[0][1]) + b"\0")
    readback = asyncio.run(work.cargoflow2_exchange(_FakeSession(reply), request, tmp_path))
    assert readback.status == "READY"
    from app.simulation.openttd.gamescript_transport import encode_gamescript

    over = json.dumps(
        dict(built_ladder()[0][1].model_dump(mode="json", exclude_none=True), pad="x" * 1600),
        sort_keys=True,
    ).encode()
    with pytest.raises(ValueError):
        encode_gamescript(over)
    with pytest.raises(ValueError):
        work.decode_cargoflow2_request(over)


def test_cargoflow2_frame_replay_parser(tmp_path):
    request = cargoflow2_request(0)
    response = _wire_of(built_ladder()[0][1])
    reply = _admin_frame(response + b"\0")
    frames = [
        ["outbound", work.encode_cargoflow2_request(request.to_bytes()).hex()],
        ["inbound", reply.hex()],
    ]
    (tmp_path / "frames.json").write_text(json.dumps(frames))
    outbound, requests, replies, request_positions, reply_positions = (
        work._parse_cargoflow2_frames(tmp_path)
    )
    assert requests == [request]
    assert replies == [response]
    assert request_positions[request.to_bytes()] == 0
    assert set(reply_positions) == {response}
    from app.simulation.openttd.gamescript_transport import encode_gamescript

    with pytest.raises(ValueError, match="invalid Cargoflow2Request"):
        junk = [["outbound", encode_gamescript(b'{"op":"site"}').hex()]]
        (tmp_path / "frames.json").write_text(json.dumps(junk))
        work._parse_cargoflow2_frames(tmp_path)


def test_day_authority_is_enforced_before_dispatch():
    # Instant fixed-chain exchanges never gate.
    for entry in SCHEDULE[:10]:
        assert work._cargoflow2_day_authority(
            entry, PLAN, elapsed_days=999, anchor=None
        ) is None
    flow0 = SCHEDULE[EXCHANGES.index("flow-00")]
    flow11 = SCHEDULE[EXCHANGES.index("flow-11")]
    arrive = SCHEDULE[EXCHANGES.index("arrive-00")]
    finance = SCHEDULE[EXCHANGES.index("finance-00")]
    finish = SCHEDULE[EXCHANGES.index("finish-00")]
    # The elapsed economy-day ledger bound.
    exceeded = work._cargoflow2_day_authority(
        flow0, PLAN, elapsed_days=61, anchor=ANCHOR
    )
    assert exceeded is not None
    assert "exceeded" in exceeded
    assert work._cargoflow2_day_authority(
        finance, PLAN, elapsed_days=60, anchor=ANCHOR
    ) is None  # the budget fits exactly at 60
    # The arrival watch's own 5-day bound.
    assert work._cargoflow2_day_authority(
        arrive, PLAN, elapsed_days=55, anchor=None
    ) is None
    unfittable = work._cargoflow2_day_authority(
        arrive, PLAN, elapsed_days=56, anchor=None
    )
    assert unfittable is not None
    assert "cannot fit" in unfittable
    # A ladder row cannot be bounded before the anchor latches.
    unbounded = work._cargoflow2_day_authority(
        flow11, PLAN, elapsed_days=None, anchor=None
    )
    assert unbounded is not None
    assert "bounded" in unbounded
    unbounded = work._cargoflow2_day_authority(
        finance, PLAN, elapsed_days=None, anchor=None
    )
    assert unbounded is not None
    assert "bounded" in unbounded
    # The ladder day rides the anchor exactly: flow-11 fits, offset 61 escapes.
    assert work._cargoflow2_day_authority(
        flow11, PLAN, elapsed_days=None, anchor=ANCHOR
    ) is None
    escape = work._cargoflow2_day_authority(
        dict(exchange="flow-12", op="flow", offset=61),
        PLAN,
        elapsed_days=None,
        anchor=ANCHOR,
    )
    assert escape is not None
    assert "escapes" in escape
    # The tail rows are ladder rows under the same anchor authority.
    assert work._cargoflow2_day_authority(
        finance, PLAN, elapsed_days=None, anchor=ANCHOR
    ) is None
    assert work._cargoflow2_day_authority(
        finish, PLAN, elapsed_days=None, anchor=ANCHOR
    ) is None


# --- replay verification fail-closed behavior --------------------------------


def test_unconsumed_attempt_candidate_verifies_fail_closed(staged):
    verdict = work.verify_cargoflow2_attempt(staged.directory)
    assert verdict == {
        "verification": "AUTHORIZATION_UNVERIFIED",
        "authorization_state": "CLAIM_ABSENT",
        "statement": (
            "the attempt candidate was never consumed by an operator "
            "authorization; no verified completion is possible"
        ),
    }
    assert claim_status(staged.directory) == "ABSENT"


def test_attempt_replay_refuses_a_claim_mismatched_to_its_seal(staged):
    target = staged.directory
    (target / "CLAIM.json").write_text(json.dumps(dict(prelaunch_digest="0" * 64)))
    try:
        with pytest.raises(ValueError, match="claim does not match"):
            work.verify_cargoflow2_attempt(target)
    finally:
        (target / "CLAIM.json").unlink()


def _claim_engine(tmp_path, staged):
    """A retained-evidence directory with a self-consistent one-shot claim
    and a forced NATIVE_CARGOFLOW2_COMPLETE result label — but no operator
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
                status="NATIVE_CARGOFLOW2_COMPLETE",
                exchanges=list(EXCHANGES),
                requests=25,
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


def test_attempt_replay_never_verifies_a_forced_label_without_authorization(
    staged, tmp_path
):
    target = _claim_engine(tmp_path, staged)
    metadata = json.loads((target / "PRELAUNCH.json").read_text())
    seal = sha256(target / "PRELAUNCH.json")
    claims = json.loads((target / "CLAIM.json").read_text())
    assert d5.replay_authorization_state(target, metadata, seal, claims) is not None
    verdict = work.verify_cargoflow2_attempt(target)
    assert verdict["verification"] == "AUTHORIZATION_UNVERIFIED"
    assert verdict["authorization_state"] not in (None, "CLAIM_ABSENT")


def test_attempt_replay_refuses_an_unreferenced_stray_file(staged, tmp_path):
    target = _claim_engine(tmp_path, staged)
    (target / "stray.txt").write_text("not in the manifest")
    with pytest.raises(ValueError, match="exhaustive"):
        work.verify_cargoflow2_attempt(target)
    (target / "stray.txt").unlink()
    verdict = work.verify_cargoflow2_attempt(target)
    assert verdict["verification"] == "AUTHORIZATION_UNVERIFIED"


def test_attempt_replay_refuses_an_unknown_prelaunch_schema(staged, tmp_path):
    target = tmp_path / "alien"
    target.mkdir()
    metadata = metadata_of(staged)
    metadata["schema"] = d5.D5_FREIGHT_PRELAUNCH_SCHEMA  # the freight lineage, not the attempt
    (target / "PRELAUNCH.json").write_text(json.dumps(metadata, sort_keys=True, indent=2) + "\n")
    (target / "PRELAUNCH.sha256").write_text(sha256(target / "PRELAUNCH.json") + "\n")
    (target / "CLAIM.json").write_text(
        json.dumps(dict(prelaunch_digest=sha256(target / "PRELAUNCH.json"), consumed=True))
    )
    (target / "artifact-manifest.sha256").write_text(manifest(target))
    verdict = work.verify_cargoflow2_attempt(target)
    assert verdict["authorization_state"] == "UNKNOWN_PRELAUNCH_SCHEMA"


# --- the single-attempt identity: its bindings cannot drift -------------------


def test_identity_pairs_the_record_with_the_attempt_plan_only(staged):
    metadata = metadata_of(staged)
    assert work.verify_cargoflow2_attempt_identity(metadata, plan=PLAN)
    for tampered_name, tampered_value in (
        ("schema", "d5-cargoflow2-prelaunch-v2"),
        ("kind", "census"),
        ("milestone", "D5-BOX-CENSUS"),
        ("attempt", "D5-CARGOFLOW-3"),
    ):
        crossed = json.loads(json.dumps(metadata))
        crossed[tampered_name] = tampered_value
        with pytest.raises(ValueError, match="identity drifted|not the D5 cargoflow-2 lineage"):
            work.verify_cargoflow2_attempt_identity(crossed, plan=PLAN)


def test_identity_refuses_a_crossed_plan_model(staged):
    metadata = metadata_of(staged)
    for foreign in (
        d5.freight_plan(),
        census_native.census_plan(),
        survey_native.survey_plan_v2(),
        freight_v2_native.freight_plan_v2(),
    ):
        with pytest.raises(work.Cargoflow2StagingError, match="Cargoflow2Plan"):
            work.verify_cargoflow2_attempt_identity(metadata, plan=foreign)


def test_identity_refuses_a_drifted_prerequisite_or_world_or_policy(staged):
    metadata = metadata_of(staged)
    for tamper in (
        lambda m: m["prerequisite"].update(after_save_sha256="9" * 64),
        lambda m: m["prerequisite"].update(attempt="D5-F12-DEPOT-2"),
        lambda m: m["world"].update(save_sha256="9" * 64),
        lambda m: m["plan_policy"].update(max_cost=5),
        lambda m: m["plan_policy"].update(
            ladder_grid=dict(schema="d5-cargoflow2-ladder-grid-v1")
        ),
        lambda m: m["plan_policy"].update(
            hypotheses=dict(samples=[], state="RETAINED_PROBE_ABSENT")
        ),
        lambda m: m["budgets"].update(requests=30),
    ):
        crossed = json.loads(json.dumps(metadata))
        tamper(crossed)
        with pytest.raises(ValueError, match="drifted|floated"):
            work.verify_cargoflow2_attempt_identity(crossed, plan=PLAN)


# --- exit-status discipline ---------------------------------------------------


def test_cargoflow2_exit_status_zero_only_for_the_verified_completion():
    assert (
        work.cargoflow2_exit_status(
            dict(
                verified=True,
                status="NATIVE_CARGOFLOW2_COMPLETE",
                cleanup_complete=True,
                state_changed=True,
            )
        )
        == 0
    )
    for bad in (
        dict(
            verified=True,
            status="NATIVE_CARGOFLOW2_COMPLETE",
            cleanup_complete=True,
            state_changed=False,
        ),
        dict(
            verified=True,
            status="NATIVE_CARGOFLOW2_COMPLETE",
            cleanup_complete=False,
            state_changed=True,
        ),
        dict(
            verified=True,
            status="PHASE_HALTED_PREFIX_PRESERVED",
            cleanup_complete=True,
            state_changed=True,
        ),
        dict(verified=False, status="FAILED", cleanup_complete=True, state_changed=True),
    ):
        assert work.cargoflow2_exit_status(bad) == 1
    verdict_zero = work.cargoflow2_verdict_exit_status(
        dict(verification="CARGOFLOW2_COMPLETION_VERIFIED")
    )
    assert verdict_zero == 0
    assert (
        work.cargoflow2_verdict_exit_status(
            dict(verification="PHASE_HALTED_EVIDENCE_PRESERVED")
        )
        == 1
    )


# --- the synthetic consumed delivery attempt ----------------------------------


def _consumed_cargoflow2_exchanges(seal: str):
    """The 25-exchange synthetic ladder of record under the real staged seal.

    The per-op readback shapes, funds figures, statuses and the §4.4 funds
    walk come from file #1's ``built_ladder`` harness of record; only the
    exchange plan seals are grafted to the real staged seal (the run's own
    plan identity), exactly as an execution would have sealed them.
    """
    template = built_ladder()
    table = work.cargoflow2_request_table(PLAN, seal, vehicle=VEHICLE)
    assert [request.request_id for request in table] == [
        request.request_id for request, _ in template
    ]
    exchanges = []
    for real_request, (template_request, template_readback) in zip(table, template, strict=True):
        payload = template_readback.model_dump(mode="json", exclude_none=True)
        payload["plan"] = real_request.plan
        raw = json.dumps(payload, separators=(",", ":")).encode()
        exchanges.append(
            (real_request, cf.Cargoflow2Readback.parse_for(real_request, raw))
        )
    return exchanges


@pytest.fixture(scope="module")
def consumed_attempt(tmp_path_factory):
    prepared = work.prepare_cargoflow2_candidate(
        tmp_path_factory.mktemp("cargoflow2-consumed") / "candidate"
    )
    directory = prepared.directory
    seal = sha256(directory / "PRELAUNCH.json")
    metadata = json.loads((directory / "PRELAUNCH.json").read_text())
    exchanges = _consumed_cargoflow2_exchanges(seal)
    frames = []
    for request, readback in exchanges:
        wire = _wire_of(readback)
        (directory / (request.request_id + "-request.json")).write_bytes(request.to_bytes())
        (directory / (request.request_id + "-response.json")).write_bytes(wire)
        frames.append(["outbound", work.encode_cargoflow2_request(request.to_bytes()).hex()])
        frames.append(["inbound", _admin_frame(wire + b"\0").hex()])
    (directory / "frames.json").write_text(json.dumps(frames))
    phase = cf.cargoflow2_phase_outcome(exchanges, prelaunch_digest=seal, plan=PLAN)
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
                requests=25,
                exchanges=[request.request_id for request, _ in exchanges],
                last_status="PHASE_STOPPED",
                command_accepted=True,
                state_changed=True,
                verified=True,
                status="NATIVE_CARGOFLOW2_COMPLETE",
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


def test_replay_verifies_a_fully_consumed_attempt_frame_sequence(
    consumed_attempt, monkeypatch
):
    directory, exchanges, _ = consumed_attempt
    monkeypatch.setattr(work, "replay_authorization_state", lambda *a, **k: None)
    verdict = work.verify_cargoflow2_attempt(directory)
    assert verdict["verification"] == "CARGOFLOW2_COMPLETION_VERIFIED"
    assert verdict["receipt"]["phase"]["verification"] == "CARGOFLOW2_COMPLETE"
    assert verdict["receipt"]["phase"]["anchor"] == ANCHOR
    assert verdict["receipt"]["phase"]["receipts"][0]["funds"] == FUNDS
    assert verdict["receipt"]["before_save_sha256"] == "9" * 64
    assert verdict["receipt"]["phase"]["sampled_months"] == [
        [1950, 1], [1950, 2], [1950, 3]
    ]
    phase = verdict["receipt"]["phase"]
    assert phase["verdict"]["verdict"] == "CARGOFLOW2_DELIVERY_VERIFIED"
    assert phase["series"]["stock_pickup"] == [-1] * 12
    assert phase["series"]["stock_bay"] == [0, 0, 0, 0, 10, 20, 15, 10, 8, 6, 5, 5]
    assert phase["series"]["wait_pickup"] == [0, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12]
    assert phase["series"]["wait_bay"] == [0] * 12
    assert phase["series"]["trans_pickup"] == [0, 0, 0, 0, 40, 40, 40, 40, 40, 40, 40, 40]
    assert phase["series"]["trans_bay"] == [0] * 12
    assert phase["series"]["prod_pickup"] == [104] * 12
    assert phase["series"]["prod_bay"] == [-1] * 12
    assert [received["request_id"] for received in phase["receipts"]] == list(EXCHANGES)
    assert len(exchanges) == 25
    assert work.cargoflow2_verdict_exit_status(verdict) == 0


def test_replay_fails_closed_on_a_tampered_retained_receipt(
    consumed_attempt, monkeypatch
):
    directory, _, _ = consumed_attempt
    monkeypatch.setattr(work, "replay_authorization_state", lambda *a, **k: None)
    before = json.loads((directory / "receipt.json").read_text())
    (directory / "receipt.json").write_text(
        json.dumps(dict(before, sampled_months=[[1950, 1]]), sort_keys=True, indent=2) + "\n"
    )
    (directory / "artifact-manifest.sha256").write_text(d5.manifest(directory))
    with pytest.raises(ValueError, match="receipt replay mismatch"):
        work.verify_cargoflow2_attempt(directory)
    (directory / "receipt.json").write_text(json.dumps(before, sort_keys=True, indent=2) + "\n")
    (directory / "artifact-manifest.sha256").write_text(d5.manifest(directory))


def test_replay_fails_closed_on_a_tampered_retained_response_inventory(
    consumed_attempt, monkeypatch
):
    directory, _, _ = consumed_attempt
    monkeypatch.setattr(work, "replay_authorization_state", lambda *a, **k: None)
    victim = directory / "flow-05-response.json"
    stored = victim.read_bytes()
    victim.unlink()
    (directory / "artifact-manifest.sha256").write_text(d5.manifest(directory))
    with pytest.raises(ValueError, match="lacks its durable response file"):
        work.verify_cargoflow2_attempt(directory)
    victim.write_bytes(stored)
    (directory / "artifact-manifest.sha256").write_text(d5.manifest(directory))
    verdict = work.verify_cargoflow2_attempt(directory)
    assert verdict["verification"] == "CARGOFLOW2_COMPLETION_VERIFIED"


def test_replay_fails_closed_on_a_result_label_the_evidence_contradicts(
    consumed_attempt, monkeypatch
):
    directory, _, _ = consumed_attempt
    monkeypatch.setattr(work, "replay_authorization_state", lambda *a, **k: None)
    before = json.loads((directory / "result.json").read_text())
    (directory / "result.json").write_text(
        json.dumps(dict(before, native_launches=2), sort_keys=True, indent=2) + "\n"
    )
    (directory / "artifact-manifest.sha256").write_text(d5.manifest(directory))
    with pytest.raises(ValueError, match="contradicts"):
        work.verify_cargoflow2_attempt(directory)
    (directory / "result.json").write_text(json.dumps(before, sort_keys=True, indent=2) + "\n")
    (directory / "artifact-manifest.sha256").write_text(d5.manifest(directory))


# --- the wire-to-Nut pin binding: the Python schedule can never drift ---------


def test_nut_pin_table_binds_to_the_python_attempt_schedule():
    """The shipped attempt GameScript's ``cargoflow2_planned`` rows and its
    pin table are read from the package bytes and must equal the wire
    contract's ladder exactly: ids, ops, offsets and planned statuses in
    order plus the pinned corridor, station, industry, company, engine and
    schedule-boundary identities."""
    text = (work.CARGOFLOW2_PACKAGE / "main.nut").read_text()
    planned_match = re.search(r"cargoflow2_planned = \[(.*?)\n    \]", text, re.DOTALL)
    assert planned_match, "the shipped package lost its cargoflow2_planned table"
    rows = re.findall(
        r'\["([a-z-]+-\d\d)",\s*"([a-z-]+)",\s*(-1|\d+),\s*"([A-Z_]+)"\]',
        planned_match.group(1),
    )
    assert (
        [(exchange, op, int(offset)) for exchange, op, offset, _status in rows]
        == [
            (row["exchange"], row["op"], int(row["offset"]))
            for row in work.cargoflow2_schedule()
        ]
    )
    assert [
        status
        for _exchange, op, _offset, status in rows
    ] == [
        cf._CARGOFLOW2_SUCCESS_STATUS[cast(cf.Cargoflow2Op, row["op"])]
        for row in work.cargoflow2_schedule()
    ]
    for marker, name, value in (
        (r"\n    pickup = (\d+)", "pickup", cf.CARGOFLOW2_PICKUP_TILE),
        (r"\n    delivery = (\d+)", "delivery", cf.CARGOFLOW2_BAY_TILE),
        (r"\n    depot_tile = (\d+)", "depot_tile", cf.CARGOFLOW2_DEPOT_TILE),
        (r"\n    PICKUP_SID = (\d+)", "PICKUP_SID", cf.CARGOFLOW2_PICKUP_SID),
        (r"\n    BAY_SID = (\d+)", "BAY_SID", cf.CARGOFLOW2_BAY_SID),
        (r"\n    PICKUP_IND = (\d+)", "PICKUP_IND", cf.CARGOFLOW2_PICKUP_IND),
        (r"\n    BAY_IND = (\d+)", "BAY_IND", cf.CARGOFLOW2_BAY_IND),
        (r"\n    CARGOFLOW2_COMPANY = (\d+)", "CARGOFLOW2_COMPANY", cf.CARGOFLOW2_COMPANY),
        (r"\n    CARGOFLOW2_CARGO = (\d+)", "CARGOFLOW2_CARGO", cf.CARGOFLOW2_CARGO),
        (r"\n    ENGINE_PIN = (\d+)", "ENGINE_PIN", cf.CARGOFLOW2_ENGINE),
        (r"\n    ENGINE_QUOTE = (\d+)", "ENGINE_QUOTE", cf.CARGOFLOW2_PURCHASE_QUOTE),
        (r"\n    ENGINE_MAX_COST = (\d+)", "ENGINE_MAX_COST", cf.CARGOFLOW2_ENGINE_MAX_COST),
        (r"\n    CAPACITY_PIN = (\d+)", "CAPACITY_PIN", cf.CARGOFLOW2_CAPACITY),
        (r"\n    SPEED_PIN = (\d+)", "SPEED_PIN", cf.CARGOFLOW2_MAX_SPEED),
        (r"\n    RUNNING_DISPLAY_PIN = (\d+)", "RUNNING_DISPLAY_PIN",
         cf.CARGOFLOW2_RUNNING_DISPLAY),
        (r"\n    OF_NONE = (\d+)", "OF_NONE", cf.CARGOFLOW2_ORDER_PICKUP_FLAGS),
        (r"\n    OF_NO_LOAD = (\d+)", "OF_NO_LOAD", cf.CARGOFLOW2_ORDER_DELIVERY_FLAGS),
        (r"\n    LAUNCH_DAY = (\d+)", "LAUNCH_DAY", cf.CARGOFLOW2_LAUNCH_DAY),
        (r"\n    ARRIVE_MAX_DAYS = (\d+)", "ARRIVE_MAX_DAYS", cf.CARGOFLOW2_ARRIVE_MAX_DAYS),
        (r"\n    ARRIVE_DEADLINE = (\d+)", "ARRIVE_DEADLINE",
         cf.CARGOFLOW2_LAUNCH_DAY + cf.CARGOFLOW2_ARRIVE_MAX_DAYS),
        (r"\n    DAY_BUDGET = (\d+)", "DAY_BUDGET", cf.CARGOFLOW2_DAY_BUDGET),
        (r"\n    AUTHORITY_LAST_DAY = (\d+)", "AUTHORITY_LAST_DAY",
         cf.CARGOFLOW2_LAUNCH_DAY + cf.CARGOFLOW2_DAY_BUDGET),
        (r"\n    WAIT_MAX_TICKS = (\d+)", "WAIT_MAX_TICKS", cf.CARGOFLOW2_WAIT_MAX_TICKS),
        (r"\n    LATCH_LIMIT = (\d+)", "LATCH_LIMIT", cf.CARGOFLOW2_LATCH_LIMIT),
        (r"\n    max_requests = (\d+)", "max_requests", cf.CARGOFLOW2_REQUEST_BUDGET),
    ):
        found = re.search(marker, text)
        assert found is not None, f"the shipped package lost its {name} pin"
        assert found.group(1) == str(value)


def test_attempt_bytes_never_parse_into_the_consumed_contract_families():
    """The protocol-11 attempt bytes cannot be retrofitted into the
    protocol-5, -6, -9 or -10 wire contracts."""
    from app.simulation.openttd import corridor_cargoflow as cf10
    from app.simulation.openttd.corridor_accept_survey import SurveyReadback
    from app.simulation.openttd.corridor_box_census import CensusReadback

    delivery = cargoflow2_request(0)
    probe_request_model = probe10._cargoflow_exchange_request(
        probe10.cargoflow_schedule()[0],
        FREIGHT_SEAL,
        probe10.cargoflow_pipeline_plan(),
    )
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
            delivery.to_bytes(),
        )
    with pytest.raises(Exception):
        SurveyReadback.parse_for(survey, delivery.to_bytes())
    with pytest.raises(Exception):
        cf10.CargoFlowReadback.parse_for(probe_request_model, delivery.to_bytes())
