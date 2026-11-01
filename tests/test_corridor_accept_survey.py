"""Controlled offline tests for the D5-ACCEPT-SURVEY-2 wire contract (protocol 6).

The contract under test is ``app/simulation/openttd/corridor_accept_survey.py``
and the additive protocol-6 survey handler shipped inside
``app/simulation/openttd/d5_freight_package/main.nut``. The shipped package
runs inside the real Squirrel VM against the same stub freight world used by
``tests/test_corridor_freight.py``; every dispatched reply is parsed back
through the protocol-6 wire contract, never through the package's own words.

The current generation is the post-A1 census (v2, ``D5-ACCEPT-SURVEY-2``):
radius first, the control-of-record zero at 50351, the A1 bay stop 50862,
then the pickup production control — bound to the consumed A1 candidate-3
after-save funds pin. The consumed v1 record (``D5-ACCEPT-SURVEY-1``,
candidate-1) is replay-relevant history: its plan derivation and wire checks
stay pinned and are re-tested here against the v1 module surface so a v2
edit can never silently drift the v1 replay facts. The v1 census itself is
proved acceptance-only; nothing here touches road bits, pathfinding or
vehicles.

Binary safety: every test here is strictly offline — nothing launches
OpenTTD, connects to an AdminPort, stages a candidate, writes a claim or an
authorization, or touches any save or native state. The survey itself may
only ever execute later under a fresh, explicit operator authorization.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError
from squirrel import SQVM

from app.simulation.openttd.corridor_accept_survey import (
    FUNDS_AT_A1_CLOSE,
    FUNDS_AT_D4_CLOSE,
    MAX_SURVEY_REQUEST_BYTES,
    MAX_SURVEY_RESPONSE_BYTES,
    PLANNED_SURVEY_EXCHANGES,
    PLANNED_SURVEY_EXCHANGES_V2,
    SURVEY_A1_STOP_TILE,
    SURVEY_CANDIDATE_TILES,
    SURVEY_CONTROL_TILE,
    SURVEY_EXCHANGE_IDS,
    SURVEY_EXCHANGE_IDS_V2,
    SURVEY_OBSERVATION_TILES,
    SURVEY_OBSERVATION_TILES_V2,
    AcceptSurveyPlan,
    SurveyReadback,
    SurveyRequest,
    staged_survey_plan,
    survey_phase_outcome,
    survey_plan,
    survey_plan_v2,
    verify_request_against_survey_plan,
)
from tests.test_corridor_freight import build_vm as _freight_build_vm

SEAL = "c" * 64
OTHER_SEAL = "d" * 64
FUNDS_V1 = FUNDS_AT_D4_CLOSE
FUNDS = FUNDS_AT_A1_CLOSE
PINS = dict(pickup=45748, delivery=50351, depot=45487)
# The v2 census schedule (exchange, op, tile): the shipped handler runs this.
SCHEDULE = (
    ("radius-00", "radius", None),
    ("accept-00", "accept", 50351),
    ("accept-01", "accept", 50862),
    ("prod-00", "prod", None),
)
OP_BY_EXCHANGE = {exchange: op for exchange, op, _ in SCHEDULE}
# The v1 schedule of record, kept for the consumed-candidate-1 replay tests.
V1_SCHEDULE = (
    ("radius-00", "radius", None),
    ("accept-00", "accept", 50351),
    ("accept-01", "accept", 50607),
    ("accept-02", "accept", 50863),
    ("accept-03", "accept", 51119),
    ("accept-04", "accept", 51375),
    ("accept-05", "accept", 50605),
    ("prod-00", "prod", None),
)
OP_BY_EXCHANGE.update({e: op for e, op, _ in V1_SCHEDULE})


def vm(**knobs) -> SQVM:
    """Fresh VM with the API fixture, the controlled freight world and the package.

    The stub world carries the v2 close-out funds pin by default; the
    census never moves it (the observation surface is cost-free).
    """
    knobs = {"funds": FUNDS, **knobs}
    return _freight_build_vm(**knobs)


def order(exchange: str, tile: int | None, *, plan=None) -> SurveyRequest:
    plan = survey_plan_v2() if plan is None else plan
    return SurveyRequest(
        op=OP_BY_EXCHANGE[exchange],
        request_id=exchange,
        plan=SEAL,
        company=plan.company,
        max_cost=0,
        pickup=plan.pickup,
        delivery=plan.delivery,
        depot=plan.depot,
        tile=tile,
    )


def rerolled(exchange: str, tile: int | None, **changes) -> SurveyRequest:
    """A survey request outside the fixed schedule (different or malformed)."""
    req = order(exchange, tile)
    return SurveyRequest.model_validate({**req.model_dump(exclude_none=True), **changes})


def readback(
    req: SurveyRequest,
    *,
    status: str = "READY",
    funds: int = FUNDS,
    radius: int | None = None,
    accept: int | None = None,
    prod: int | None = None,
    tile_echo: int | None = None,
) -> SurveyReadback:
    data = {
        "protocol": 6,
        "op": req.op,
        "request_id": req.request_id,
        "plan": SEAL,
        "company": req.company,
        "max_cost": req.max_cost,
        "pickup": req.pickup,
        "delivery": req.delivery,
        "depot": req.depot,
        "status": status,
        "funds": funds,
        "cost": 0,
    }
    if req.tile is not None:
        data["tile"] = req.tile if tile_echo is None else tile_echo
    if req.op == "accept" and status == "READY":
        radius = 8 if radius is None else radius
        if accept is None:
            accept = 0
    if radius is not None:
        data["radius"] = radius
    if accept is not None:
        data["accept"] = accept
    if prod is not None:
        data["prod"] = prod
    return SurveyReadback.model_validate(data)


def controlled_exchanges(
    *,
    stop: int = 8,
    prod: int = 104,
    radius: int = 8,
    funds: int = FUNDS,
) -> list[tuple[SurveyRequest, SurveyReadback]]:
    """The full four-exchange v2 census as controlled evidence pairs.

    The control-of-record zero at 50351 is a *measured* zero under a
    correlated READY frame (the handler's own semantics); 50862 carries the
    A0 census hypothesis value 8; nothing is proven about traversal.
    """
    values = (0, stop)
    pairs: list[tuple[SurveyRequest, SurveyReadback]] = [
        (order("radius-00", None), readback(order("radius-00", None), radius=radius, funds=funds))
    ]
    for index, (exchange, _op, tile) in enumerate(SCHEDULE[1:3], start=1):
        req = order(exchange, tile)
        pairs.append(
            (req, readback(req, radius=radius, accept=values[index - 1], funds=funds))
        )
    pairs.append((order("prod-00", None), readback(order("prod-00", None), prod=prod, funds=funds)))
    return pairs


def complete_result(**kwargs) -> dict:
    return survey_phase_outcome(
        controlled_exchanges(**kwargs), prelaunch_digest=SEAL, plan=survey_plan_v2()
    )


# --- plans: the pinned v2 census and the consumed v1 history ------------------


def test_survey_plan_v2_pins_the_post_a1_census():
    plan = survey_plan_v2()
    assert plan.schema_version == 2
    assert plan.company == 0 and plan.cargo == 1
    assert (plan.pickup, plan.pickup_front) == (45748, 45747)
    assert (plan.delivery, plan.delivery_front) == (50351, 50095)
    assert (plan.depot, plan.depot_front) == (45487, 45743)
    assert plan.expected_funds == FUNDS == 490257
    assert plan.request_budget == 32
    assert plan.observations == (50351, 50862) == SURVEY_OBSERVATION_TILES_V2
    assert SURVEY_A1_STOP_TILE == 50862
    assert plan.schedule == SURVEY_EXCHANGE_IDS_V2 == tuple(e for e, _, _ in SCHEDULE)
    assert PLANNED_SURVEY_EXCHANGES_V2 == 4
    # The same corridor identity pins as v1: the stops and depot of the
    # consumed D4 lineage are all live in the A1 close-out world.
    assert plan.digest != survey_plan().digest


def test_survey_plan_v2_refuses_pinned_field_drift():
    base = survey_plan_v2()
    for field, expected in (
        ("expected_funds", "funds"),
        ("observations", "observations"),
        ("schedule", "schedule"),
    ):
        changed = dict(base.model_dump())
        if field == "expected_funds":
            changed[field] = 0
        elif field == "observations":
            changed[field] = (50862, 50351)  # control no longer first
        else:
            changed[field] = SURVEY_EXCHANGE_IDS_V2[1:]
        with pytest.raises(ValidationError, match=expected):
            AcceptSurveyPlan.model_validate(changed)


def test_staged_survey_plan_dispatches_by_version_and_refuses_foreign():
    assert staged_survey_plan(dict(schedule_version=2)).digest == survey_plan_v2().digest
    assert staged_survey_plan(dict(schedule_version=1)).digest == survey_plan().digest
    for foreign in (0, 3, "2", None):
        with pytest.raises(ValueError, match="unknown acceptance-survey version"):
            if foreign is None:
                staged_survey_plan({})
            else:
                staged_survey_plan(dict(schedule_version=foreign))


def test_v1_plan_stays_the_pinned_consumed_candidate1_derivation():
    """The consumed ``D5-ACCEPT-SURVEY-1`` plan facts of record (its retained
    prelaunch binds exactly these pins) — replay-relevant history, never a
    retargetable derivation."""
    plan = survey_plan()
    assert plan.company == 0 and plan.cargo == 1
    assert (plan.pickup, plan.pickup_front) == (45748, 45747)
    assert (plan.delivery, plan.delivery_front) == (50351, 50095)
    assert (plan.depot, plan.depot_front) == (45487, 45743)
    assert plan.expected_funds == FUNDS_V1 == 492149
    assert plan.request_budget == 32
    assert plan.observations == (50351, 50607, 50863, 51119, 51375, 50605)
    assert plan.schedule == SURVEY_EXCHANGE_IDS == tuple(e for e, _, _ in V1_SCHEDULE)
    assert SURVEY_CONTROL_TILE == 50351
    assert SURVEY_CANDIDATE_TILES == (50607, 50863, 51119, 51375, 50605)
    assert len(SURVEY_OBSERVATION_TILES) == 6
    assert PLANNED_SURVEY_EXCHANGES == 8


def test_v1_plan_refuses_pinned_field_drift():
    base = survey_plan()
    for field, expected in (
        ("expected_funds", "funds"),
        ("observations", "observations"),
        ("schedule", "schedule"),
    ):
        changed = dict(base.model_dump())
        if field == "expected_funds":
            changed[field] = 0
        elif field == "observations":
            changed[field] = (
                50607,
                50863,
                51119,
                51375,
                50605,
                50351,
            )  # control no longer first
        else:
            changed[field] = SURVEY_EXCHANGE_IDS[1:]
        with pytest.raises(ValidationError, match=expected):
            AcceptSurveyPlan.model_validate(changed)


def test_staged_world_pins_match_the_a1_after_save_funds():
    """The v2 funds pin is the A1 close-out level of record (native readback
    at the end of D5-CORRIDOR-EXTENSION-3); the v1 pin is the D4 close-out.
    Both stay pinned; neither is derivable from the other."""
    assert FUNDS_AT_A1_CLOSE == 490257
    assert FUNDS_AT_D4_CLOSE == 492149
    assert survey_plan_v2().expected_funds == FUNDS_AT_A1_CLOSE
    assert survey_plan().expected_funds == FUNDS_AT_D4_CLOSE


# --- wire contract: canonical bytes and fail-closed parsing ------------------


def test_survey_requests_are_canonical_and_bounded():
    raw = order("accept-00", 50351).to_bytes()
    assert raw.decode() == (
        '{"company":0,"delivery":50351,"depot":45487,"max_cost":0,"op":"accept",'
        '"pickup":45748,"plan":"' + SEAL + '","protocol":6,'
        '"request_id":"accept-00","tile":50351}'
    )
    assert len(raw) < MAX_SURVEY_REQUEST_BYTES
    assert len(order("radius-00", None).to_bytes()) < MAX_SURVEY_REQUEST_BYTES


def test_survey_requests_refuse_unpinned_or_mistyped_observations():
    with pytest.raises(ValidationError, match="pinned survey tiles"):
        rerolled("accept-00", 45747)
    with pytest.raises(ValidationError, match="exactly one pinned observation tile"):
        order("accept-00", None)
    with pytest.raises(ValidationError, match="only the accept op carries a tile"):
        rerolled("radius-00", 50351)
    with pytest.raises(ValidationError, match="max_cost"):
        SurveyRequest.model_validate({"max_cost": 7, "op": "accept", "request_id": "accept-00",
                                      "plan": SEAL, "company": 0, "pickup": 45748,
                                      "delivery": 50351, "depot": 45487, "tile": 50351})
    # The A1 stop tile is a pinned observation in either version; a
    # dismounted v1-style candidate tile refuses.
    assert order("accept-01", 50862, plan=survey_plan_v2())
    with pytest.raises(ValidationError, match="pinned survey tiles"):
        rerolled("accept-01", 50608)


def test_survey_readbacks_refuse_out_of_range_and_hybrid_observations():
    req = order("accept-00", 50351)
    for fragment, match in (({"accept": 9}, "accept"), ({"radius": 256}, "radius")):
        with pytest.raises(ValidationError, match=match):
            SurveyReadback.model_validate(
                readback(req).model_dump() | fragment
            )
    with pytest.raises(ValidationError, match="outside its subset"):
        SurveyReadback.model_validate(
            readback(order("prod-00", None), status="STALE_PIN").model_dump()
            | {"accept": 0}
        )
    with pytest.raises(ValidationError, match="must echo"):
        SurveyReadback.model_validate(
            SurveyReadback.model_validate(readback(req).model_dump()).model_dump()
            | {"tile": None}
        )
    with pytest.raises(ValidationError, match="lacks"):
        SurveyReadback.model_validate(
            {k: v for k, v in readback(req).model_dump().items() if k != "radius"}
        )


def test_survey_parse_is_cross_tile_refusing_and_size_bounded():
    req = order("accept-00", 50351)
    good = readback(req)
    raw = good.model_dump_json().encode()
    assert len(raw) <= MAX_SURVEY_RESPONSE_BYTES
    parsed = SurveyReadback.parse_for(req, raw)
    assert parsed.accept == good.accept and parsed.tile == 50351
    stale = SurveyReadback.model_validate(good.model_dump() | {"tile": 50862})
    with pytest.raises(ValueError, match="tile echo mismatch"):
        SurveyReadback.parse_for(req, stale.model_dump_json().encode())
    with pytest.raises(ValueError, match="exceeds"):
        SurveyReadback.parse_for(req, b"{\"protocol\":6" + b"a" * 700 + b"}")


def test_survey_parse_refuses_malformed_stale_and_duplicate_bodies():
    req = order("accept-00", 50351)
    good = readback(req)
    body = good.model_dump_json()
    for raw in (
        b"{",
        (body[:-1] + '"').encode(),
        b"[]",
        b"",
    ):
        with pytest.raises(Exception):
            SurveyReadback.parse_for(req, raw)
    # A well-formed response bound to a different exchange refuses on the
    # correlation stride.
    foreign = SurveyReadback.model_validate(
        {**readback(req).model_dump(), "request_id": "accept-01", "tile": 50862}
    )
    with pytest.raises(ValueError, match="correlation mismatch"):
        SurveyReadback.parse_for(req, foreign.model_dump_json().encode())
    duplicate = (
        '{"protocol":6,"op":"accept","request_id":"accept-00","plan":"' + SEAL
        + '","company":0,"max_cost":0,"pickup":45748,"delivery":50351,"depot":45487,'
        '"tile":50351,"status":"READY","funds":490257,"cost":0,"funds":490257,'
        '"accept":0,"radius":8}'
    )
    with pytest.raises(ValueError, match="duplicate"):
        SurveyReadback.parse_for(req, duplicate.encode())
    tripped = SurveyReadback.model_validate(
        good.model_dump() | {"plan": OTHER_SEAL}
    )
    with pytest.raises(ValueError, match="correlation mismatch"):
        SurveyReadback.parse_for(req, tripped.model_dump_json().encode())
    with pytest.raises(ValidationError, match="pinned survey tiles"):
        rerolled("accept-00", 45748)


def test_survey_request_verifier_binds_seal_pins_and_tile_slot():
    for plan, schedule in ((survey_plan_v2(), SCHEDULE), (survey_plan(), V1_SCHEDULE)):
        for exchange, _op, tile in schedule:
            verify_request_against_survey_plan(
                order(exchange, tile, plan=plan), plan=plan, seal=SEAL
            )
        with pytest.raises(ValueError, match="staged prelaunch seal"):
            verify_request_against_survey_plan(
                order("accept-00", 50351, plan=plan), plan=plan, seal=OTHER_SEAL
            )
        with pytest.raises(ValueError, match="pins drifted"):
            verify_request_against_survey_plan(
                rerolled("accept-00", 50351, depot=45486), plan=plan, seal=SEAL
            )
        with pytest.raises(ValueError, match="tile drifted|planned observation"):
            verify_request_against_survey_plan(
                order("accept-01", 50351, plan=plan), plan=plan, seal=SEAL
            )
        with pytest.raises(ValueError, match="tile drifted|planned observation"):
            verify_request_against_survey_plan(
                rerolled("accept-00", 50351, request_id="accept-09"), plan=plan, seal=SEAL
            )
    # A v2 tile inside a v1 plan slot refuses: the versions never share a
    # schedule mapping.
    with pytest.raises(ValueError, match="tile drifted|planned observation"):
        verify_request_against_survey_plan(
            order("accept-01", 50862, plan=survey_plan_v2()),
            plan=survey_plan(),
            seal=SEAL,
        )


# --- the survey verifier: measured zero vs everything else -------------------


def test_full_census_completes_and_records_measured_observations():
    result = complete_result(stop=8)
    assert result["verification"] == "SURVEY_COMPLETE"
    assert result["failed"] is None and result["pending"] == []
    assert result["radius"] == 8
    assert result["production"] == 104
    assert result["funds"] == FUNDS
    observations = result["observations"]
    assert observations[50351]["value"] == 0  # a measured zero under READY
    assert observations[50351]["request_id"] == "accept-00"
    assert observations[50862]["value"] == 8  # the A0 census hypothesis value
    assert observations[50862]["request_id"] == "accept-01"
    assert len(result["receipts"]) == PLANNED_SURVEY_EXCHANGES_V2


def test_producer_control_is_part_of_the_completed_census():
    result = complete_result(prod=0)
    assert result["production"] == 0
    assert result["verification"] == "SURVEY_COMPLETE"


def test_zero_records_mean_nothing_without_a_completed_schedule():
    result = survey_phase_outcome(
        controlled_exchanges()[:-1], prelaunch_digest=SEAL, plan=survey_plan_v2()
    )
    assert result["verification"] == "SURVEY_INCOMPLETE"
    assert result["failed"] is None
    assert "prod-00" in result["pending"]


def test_census_halts_on_funds_drift_before_recording_the_observation():
    pairs: list[tuple[SurveyRequest, SurveyReadback]] = []
    first = readback(order("radius-00", None), radius=8)
    pairs.append((order("radius-00", None), first))
    funds_drifted = readback(order("accept-00", 50351), radius=8, accept=0, funds=100)
    pairs.append((order("accept-00", 50351), funds_drifted))
    result = survey_phase_outcome(pairs, prelaunch_digest=SEAL, plan=survey_plan_v2())
    assert result["verification"] == "SURVEY_INCOMPLETE"
    assert result["failed"]["label"] == "accept-00"
    assert "exactly" in result["failed"]["error"]
    assert 50351 not in result["observations"]
    assert result["pending"] == list(SURVEY_EXCHANGE_IDS_V2[2:])


def test_census_records_typed_refusals_without_observations():
    refs = [
        (order("radius-00", None), readback(order("radius-00", None), status="PAUSED")),
    ]
    result = survey_phase_outcome(refs, prelaunch_digest=SEAL, plan=survey_plan_v2())
    assert result["failed"]["status"] == "PAUSED"
    assert result["failed"], "missing failure record"
    assert 50351 not in result["observations"]
    assert result["pending"] == list(SURVEY_EXCHANGE_IDS_V2[1:])


def test_census_labels_a_malformed_exchange_without_observations():
    pairs: list[tuple] = [(order("radius-00", None), ValueError("torn frame"))]
    result = survey_phase_outcome(pairs, prelaunch_digest=SEAL, plan=survey_plan_v2())
    assert result["failed"]["status"] == "MALFORMED"
    assert result["failed"]["label"] == "radius-00"
    assert result["pending"] == list(SURVEY_EXCHANGE_IDS_V2[1:])


def test_refusal_readbacks_cannot_carry_hidden_observations():
    """A spoofed hybrid (refusal + values) is refused by the wire contract."""
    req = order("accept-00", 50351)
    good = readback(req).model_dump()
    hybrid = {**good, "status": "INVALID_LOCATION"}
    with pytest.raises(ValidationError, match="unclaimed observation set"):
        SurveyReadback.model_validate(hybrid)


def test_v1_phase_outcome_semantics_are_unchanged():
    """The consumed v1 record's verification semantics replay the same: a
    controlled eight-exchange v1 sequence still verifies against the v1 plan
    with the shared kernel — only the funds pin and schedule differ."""
    pairs = [
        (req, readback(req, radius=8, funds=FUNDS_V1))
        for req in (order("radius-00", None, plan=survey_plan()),)
    ] + [
        (
            order(exchange, tile, plan=survey_plan()),
            readback(
                order(exchange, tile, plan=survey_plan()),
                radius=8,
                accept=(0 if exchange == "accept-00" else 8),
                funds=FUNDS_V1,
            ),
        )
        for (exchange, _op, tile) in V1_SCHEDULE[1:7]
    ]
    pairs.append(
        (order("prod-00", None, plan=survey_plan()),
         readback(order("prod-00", None, plan=survey_plan()), prod=104, funds=FUNDS_V1))
    )
    result = survey_phase_outcome(pairs, prelaunch_digest=SEAL, plan=survey_plan())
    assert result["verification"] == "SURVEY_COMPLETE"
    assert observations_of(result) == {
        50351: 0,
        50607: 8,
        50863: 8,
        51119: 8,
        51375: 8,
        50605: 8,
    }


def observations_of(result: dict) -> dict:
    return {tile: record["value"] for tile, record in result["observations"].items()}


# --- the shipped package: protocol-6 dispatch in the controlled VM ----------


def survey_drive(world: SQVM, req: SurveyRequest) -> SurveyReadback:
    world.execute("::bridge.Handle(" + req.to_bytes().decode() + ");")
    world.execute("::sniffer.last = last_reply_json();")
    raw = world.get_roottable()["sniffer"]["last"].encode()
    assert len(raw) <= MAX_SURVEY_RESPONSE_BYTES
    return SurveyReadback.parse_for(req, raw)


def dropped(world: SQVM, req: SurveyRequest) -> None:
    before = len(world.get_roottable()["replies"])
    world.execute("::bridge.Handle(" + req.to_bytes().decode() + ");")
    assert len(world.get_roottable()["replies"]) == before  # silently dropped


def test_handler_runs_the_full_pinned_census_in_order():
    world = vm()
    for exchange, _op, tile in SCHEDULE:
        reply = survey_drive(world, order(exchange, tile))
        assert reply.status == "READY"


def test_handler_measures_the_stub_values_and_close_out_funds():
    world = vm()
    reply = survey_drive(world, order("radius-00", None))
    assert (reply.status, reply.radius, reply.funds) == ("READY", 8, FUNDS)
    assert reply.accept is None and reply.tile is None and reply.prod is None
    control = survey_drive(world, order("accept-00", 50351))
    assert (control.status, control.accept, control.radius, control.tile) == (
        "READY",
        8,
        8,
        50351,
    )
    stop = survey_drive(world, order("accept-01", 50862))
    assert (stop.status, stop.accept, stop.radius, stop.tile) == ("READY", 8, 8, 50862)
    prod = survey_drive(world, order("prod-00", None))
    assert (prod.status, prod.prod) == ("READY", 100)


def test_handler_census_verifies_through_the_wire_kernel():
    """The live handler's four exchanges verify against the v2 plan with the
    production kernel (stub funds pinned to the A1 close-out level)."""
    world = vm()
    pairs = []
    for exchange, _op, tile in SCHEDULE:
        req = order(exchange, tile)
        readback_ = survey_drive(world, req)
        pairs.append((req, readback_))
    result = survey_phase_outcome(pairs, prelaunch_digest=SEAL, plan=survey_plan_v2())
    assert result["verification"] == "SURVEY_COMPLETE"
    assert result["funds"] == FUNDS
    assert set(observations_of(result)) == {50351, 50862}


def test_handler_refuses_a_non_pinned_tile_before_any_observation():
    world = vm()
    survey_drive(world, order("radius-00", None))
    # A scheduled accept exchange addressed to a tile outside the pinned v2
    # census observations replies INVALID_LOCATION with no observation
    # fields; a hand-built body is the only way past the Python-side pin
    # validator. 50863 was a v1 candidate tile and is no longer pinned; the
    # probe rides the current scheduled exchange id so the handler's stage
    # matcher lets it reach the pinned-tile guard.
    probe = (
        '{"protocol":6,"op":"accept","request_id":"accept-00","plan":"' + SEAL
        + '","company":0,"max_cost":0,"pickup":45748,"delivery":50351,"depot":45487,'
        '"tile":50863}'
    )
    world.execute(f"::bridge.Handle({probe});")
    world.execute("::sniffer.last = last_reply_json();")
    raw = world.get_roottable()["sniffer"]["last"].encode()
    probe_request = SurveyRequest.model_construct(
        op="accept", request_id="accept-00", plan=SEAL, company=0, max_cost=0,
        pickup=45748, delivery=50351, depot=45487, tile=50863,
    )
    refuted = SurveyReadback.parse_for(probe_request, raw)
    assert refuted.status == "INVALID_LOCATION"
    assert refuted.accept is None and refuted.radius is None
    # A refusal on the planned stage halts the survey prefix-preservingly;
    # this is evidence discipline, never an observation.


def test_handler_refuses_out_of_order_and_duplicate_survey_ids():
    world = vm()
    # An in-schedule exchange out of turn replies OUT_OF_ORDER and halts
    # the survey prefix-preservingly.
    reply = survey_drive(world, order("accept-00", 50351))
    assert reply.status == "OUT_OF_ORDER"
    # A fresh survey session then runs cleanly; a duplicate id is dropped
    # silently and the stage is untouched.
    world = vm()
    first = survey_drive(world, order("radius-00", None))
    assert first.status == "READY"
    dropped(world, order("radius-00", None))
    assert survey_drive(world, order("accept-00", 50351)).status == "READY"
    # A v1-only exchange id is outside the v2 staged schedule entirely.
    foreign = world
    out = survey_drive(foreign, order("accept-02", 50607))
    assert out.status == "OUT_OF_ORDER"


def test_handler_survey_refusal_halts_the_survey_prefix_preservingly():
    world = vm()
    survey_drive(world, order("radius-00", None))
    pinned = order("accept-00", 50351)
    first = survey_drive(world, pinned)
    assert first.status == "READY"
    # An out-of-schedule survey exchange halts the survey stage...
    delayed = (
        '{"protocol":6,"op":"prod","request_id":"prod-00","plan":"' + SEAL
        + '","company":0,"max_cost":0,"pickup":45748,"delivery":50351,"depot":45487,'
        '"tile":null}'
    )
    world.execute(f"::bridge.Handle({delayed});")
    world.execute("::sniffer.last = last_reply_json();")
    raw = world.get_roottable()["sniffer"]["last"].encode()
    probed = SurveyReadback.parse_for(order("prod-00", None), raw)
    assert probed.status == "OUT_OF_ORDER"
    # ...and every later in-schedule exchange is refused for the record.
    later = survey_drive(world, order("accept-01", 50862))
    assert later.status == "OUT_OF_ORDER"


def test_handler_refuses_a_drifted_survey_pin_and_company():
    world = vm()
    survey_drive(world, order("radius-00", None))
    assert survey_drive(world, rerolled("accept-00", 50351, depot=45486)).status == "STALE_PIN"
    foreign = vm()
    company_broadcast = order("radius-00", None).to_bytes().decode().replace(
        '"company":0', '"company":1'
    )
    foreign.execute("::bridge.Handle(" + company_broadcast + ");")
    foreign.execute("::sniffer.last = last_reply_json();")
    assert "INVALID_COMPANY" in foreign.get_roottable()["sniffer"]["last"]


def test_handler_refuses_paused_and_out_of_range_observations():
    world = vm(paused=True)
    reply = survey_drive(world, order("radius-00", None))
    assert reply.status == "PAUSED"
    fresh = vm(accept=9)
    survey_drive(fresh, order("radius-00", None))
    beyond = survey_drive(fresh, order("accept-00", 50351))
    assert beyond.status == "UNSUPPORTED_NATIVE_FACT"
    assert beyond.accept is None and beyond.radius is None


def test_survey_protocol_shares_the_dispatcher_request_budget():
    """The package budget cap is shared across both protocols (32 unique ids)."""
    world = vm()
    for exchange, _op, tile in SCHEDULE:
        survey_drive(world, order(exchange, tile))
    # A foreign id at any op is neither planned nor accepted.
    foreign = (
        '{"protocol":6,"op":"prod","request_id":"prod-extra","plan":"' + SEAL
        + '","company":0,"max_cost":0,"pickup":45748,"delivery":50351,"depot":45487}'
    )
    world.execute(f"::bridge.Handle({foreign});")
    before = len(world.get_roottable()["replies"])
    world.execute(f"::bridge.Handle({foreign});")  # duplicate id: dropped
    assert len(world.get_roottable()["replies"]) == before


def test_survey_plan_latch_refuses_the_freight_cycle_after_a_survey():
    """One session, one plan identity: a survey latches the plan, a freight
    exchange with the freight seal is refused OUT_OF_ORDER on the same VM
    instance, and vice versa is covered by the protocol-5 suite."""
    world = vm()
    for exchange, _op, tile in SCHEDULE:
        reply = survey_drive(world, order(exchange, tile))
        assert reply.cost == 0 and reply.funds == FUNDS
    commission = freight_site_request()
    world.execute("::bridge.Handle(" + commission.to_bytes().decode() + ");")
    world.execute("::sniffer.last = last_reply_json();")
    freight_raw = world.get_roottable()["sniffer"]["last"].encode()
    from app.simulation.openttd.corridor_freight import FreightReadback

    freight = FreightReadback.parse_for(commission, freight_raw)
    assert freight.status == "OUT_OF_ORDER"


def freight_site_request():
    from app.simulation.openttd.corridor_freight import FreightRequest
    from app.simulation.openttd.proof import corridor_freight_native as work
    from tests.test_corridor_freight import PRELAUNCH as FREIGHT_SEAL

    plan = work.freight_plan()

    return FreightRequest(
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
