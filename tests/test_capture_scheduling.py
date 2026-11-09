"""Offline month-capacity scheduling tests for supplemental capture (E156 remediation).

No native runtime: synthetic brackets, fake planning exchanges and region
geometry are the only inputs. The month chain mirrors the sealed attempt-4
qualification chain (January [712223, 712254) -> February [712254, 712282)
-> March [712282, 712313)); the guard month is
``production.qualification.current_month`` (March) while the serialized
``world-planning-observation.json`` anchor ``qualified_month`` is February -
a different property on a different object.
"""

import asyncio
import json
from types import SimpleNamespace as NS

import pytest
from test_random_distance import seed17_world
from test_supplemental_planning_contracts import world_for

import app.simulation.openttd.freight_native_network as native_network
from app.demo_random import DemoBudgets
from app.simulation.openttd.capture_scheduling import (
    HEURISTIC_EXCHANGES_PER_DAY,
    MAX_ENGINES_BOUND,
    CapacityPolicy,
    CaptureCapacityError,
    CaptureSchedule,
    CaptureWindowExceeded,
    SessionDecision,
    SessionForecast,
    build_forecasts,
    forecast_session,
    plan_sessions,
    qualified_capture_month,
    require_planned,
)
from app.simulation.openttd.freight_native_network import (
    bounded_relationships,
    replay_network_capture,
)
from app.simulation.openttd.freight_runtime_planning import capture_planning_facts, cycle_request_id
from app.simulation.openttd.production_observation import EconomyMonth

GATE_MONTH = EconomyMonth(year=1950, month=3, start_date=712282, end_date=712313)
ANCHOR_MONTH = EconomyMonth(year=1950, month=2, start_date=712254, end_date=712282)
MARCH_START = GATE_MONTH.start_date


def fc(relationship, position=0, estimate=700, ceiling=546, tiles=450):
    return SessionForecast(
        relationship=relationship,
        position=position,
        region_tiles=tiles,
        exchange_estimate=estimate,
        exchange_ceiling=ceiling,
    )


# ---------------------------------------------------------------- scheduling


def test_schedule_orders_smallest_first_with_identity_tie_break():
    forecasts = [
        fc((0, 7, 5), position=0, estimate=900),
        fc((0, 1, 1), position=1, estimate=300),
        fc((2, 3, 9), position=2, estimate=300),
    ]
    schedule = plan_sessions([(0, 7, 5), (0, 1, 1), (2, 3, 9)], GATE_MONTH, MARCH_START, forecasts)
    assert [d.relationship for d in schedule.decisions] == [(0, 1, 1), (2, 3, 9), (0, 7, 5)]


def test_schedule_is_deterministic_for_identical_inputs():
    relationships = [(1, 2, 3), (4, 5, 6), (0, 0, 0)]
    forecasts = [fc(r, i, 500) for i, r in enumerate(relationships)]
    first = plan_sessions(relationships, GATE_MONTH, MARCH_START, forecasts)
    second = plan_sessions(relationships, GATE_MONTH, MARCH_START, forecasts)
    assert first.decisions == second.decisions
    assert [d.relationship for d in first.decisions] == [(0, 0, 0), (1, 2, 3), (4, 5, 6)]


def test_no_relationship_lost_and_deferrals_carry_explicit_reasons():
    relationships = [(0, 1, 1), (2, 3, 4), (5, 6, 7)]
    forecasts = [fc((0, 1, 1), 0, 400), fc((2, 3, 4), 1, 400), fc((5, 6, 7), 2, 2500)]
    schedule = plan_sessions(relationships, GATE_MONTH, MARCH_START, forecasts)
    assert len(schedule.decisions) == 3
    assert sorted(d.relationship for d in schedule.decisions) == sorted(relationships)
    assert len(schedule.planned) == 2 and len(schedule.deferred) == 1
    assert schedule.deferred[0].relationship == (5, 6, 7)
    assert schedule.deferred[0].reason and "INSUFFICIENT_CAPACITY" in schedule.deferred[0].reason


def test_capture_inside_window_fits():
    schedule = plan_sessions([(0, 1, 1)], GATE_MONTH, MARCH_START, [fc((0, 1, 1))])
    assert schedule.planned[0].fits
    assert schedule.planned[0].planned_first_date == 712282
    assert schedule.planned[0].planned_last_date == 712291


def test_planned_last_before_exclusive_boundary_fits():
    # 74 * 31 estimated exchanges: planned last = 712312 = exclusive end - 1.
    forecasts = [fc((0, 1, 1), 0, estimate=31 * HEURISTIC_EXCHANGES_PER_DAY)]
    schedule = plan_sessions([(0, 1, 1)], GATE_MONTH, MARCH_START, forecasts)
    assert schedule.planned
    assert schedule.planned[0].planned_last_date == GATE_MONTH.end_date - 1


def test_planned_last_at_exclusive_boundary_refused():
    forecasts = [fc((0, 1, 1), 0, estimate=32 * HEURISTIC_EXCHANGES_PER_DAY)]
    schedule = plan_sessions([(0, 1, 1)], GATE_MONTH, MARCH_START, forecasts)
    assert not schedule.planned
    assert schedule.deferred[0].planned_last_date == GATE_MONTH.end_date


def test_planned_last_past_exclusive_boundary_refused():
    forecasts = [fc((0, 1, 1), 0, estimate=40 * HEURISTIC_EXCHANGES_PER_DAY)]
    schedule = plan_sessions([(0, 1, 1)], GATE_MONTH, MARCH_START, forecasts)
    assert not schedule.planned
    last = schedule.deferred[0].planned_last_date
    assert last is not None and last > GATE_MONTH.end_date


def test_exchange_rate_is_policy_heuristic_not_engine_invariant():
    # 74/day is an E156 attempt-4 operating heuristic (response-disc mtimes),
    # not a verified engine bound: the policy knob must change decisions.
    assert HEURISTIC_EXCHANGES_PER_DAY == 74
    base = plan_sessions([(0, 1, 1)], GATE_MONTH, MARCH_START, [fc((0, 1, 1))])
    slower = plan_sessions(
        [(0, 1, 1)],
        GATE_MONTH,
        MARCH_START,
        [fc((0, 1, 1))],
        policy=CapacityPolicy(exchanges_per_day=37),
    )
    faster = plan_sessions(
        [(0, 1, 1)],
        GATE_MONTH,
        MARCH_START,
        [fc((0, 1, 1))],
        policy=CapacityPolicy(exchanges_per_day=200),
    )
    assert base.decisions[0].day_span == 10
    assert slower.decisions[0].day_span == 19
    assert faster.decisions[0].day_span == 4
    assert CapacityPolicy().exchanges_per_day == HEURISTIC_EXCHANGES_PER_DAY


def test_inter_session_gap_advances_next_session_open():
    forecasts = [fc((0, 1, 1), 0, estimate=700), fc((2, 3, 4), 1, estimate=700)]
    schedule = plan_sessions([(0, 1, 1), (2, 3, 4)], GATE_MONTH, MARCH_START, forecasts)
    first, second = schedule.planned
    assert first.planned_last_date == 712291
    # Conservative gap policy: the next session consumes the estimated span
    # plus the full gap before its first exchange (712282 + 10 + 1).
    assert second.planned_first_date == 712282 + 10 + CapacityPolicy().inter_session_days


def test_unknown_capacity_fails_closed():
    schedule = plan_sessions(
        [(0, 1, 1)], GATE_MONTH, MARCH_START, [fc((0, 1, 1), 0, estimate=None)]
    )
    assert not schedule.planned
    assert schedule.deferred[0].reason and "CAPACITY_UNKNOWN" in schedule.deferred[0].reason


def test_region_exceeding_capture_read_budget_refused():
    forecasts = [fc((0, 1, 1), 0, estimate=4000, tiles=4000, ceiling=546)]
    schedule = plan_sessions([(0, 1, 1)], GATE_MONTH, MARCH_START, forecasts)
    assert not schedule.planned
    assert "CAPTURE_READ_BUDGET" in (schedule.deferred[0].reason or "")


def test_forecast_length_mismatch_raises():
    with pytest.raises(ValueError, match="forecast mismatch"):
        plan_sessions([(0, 1, 1), (2, 3, 4)], GATE_MONTH, MARCH_START, [fc((0, 1, 1))])


def test_attempt4_oversized_session_shape_is_refused():
    # E156 attempt-4 replay: session n2 estimated 1794 exchanges opening at
    # in-session date 712306; the conservative live-rate span of 25 days
    # reaches 712330, past the exclusive March end 712313.
    schedule = plan_sessions([(3, 2, 7)], GATE_MONTH, 712306, [fc((3, 2, 7), 0, estimate=1794)])
    assert not schedule.planned
    assert schedule.deferred[0].planned_last_date == 712330
    assert schedule.deferred[0].remaining_window_days == 7


def test_deferred_sessions_do_not_consume_capacity():
    forecasts = [fc((0, 1, 1), 0, estimate=3500), fc((2, 3, 4), 1, estimate=3501)]
    schedule = plan_sessions([(0, 1, 1), (2, 3, 4)], GATE_MONTH, MARCH_START, forecasts)
    assert all(not d.fits for d in schedule.decisions)
    assert schedule.decisions[1].planned_first_date == MARCH_START


def test_require_planned_fails_closed_typed_not_feasibility_coded():
    schedule = plan_sessions(
        [(0, 1, 1)], GATE_MONTH, MARCH_START, [fc((0, 1, 1), 0, estimate=None)]
    )
    assert not schedule.planned
    with pytest.raises(CaptureCapacityError) as info:
        require_planned(schedule)
    assert str(info.value).startswith("CAPTURE_SCHEDULE_EMPTY")
    assert "NO_FEASIBLE_SERVICES" not in str(info.value)
    fitting = plan_sessions([(0, 1, 1)], GATE_MONTH, MARCH_START, [fc((0, 1, 1))])
    assert require_planned(fitting) is fitting


# ----------------------------------------------------------------- forecasts


def test_build_forecasts_region_derivation_matches_native_region():
    world = seed17_world()
    forecasts = build_forecasts([(0, 1, 1)], world, DemoBudgets())
    assert len(forecasts) == 1
    assert forecasts[0].region_tiles == 450
    assert forecasts[0].exchange_estimate == 450 + 2 + MAX_ENGINES_BOUND
    assert forecasts[0].exchange_ceiling == 512 + 34


def test_forecast_session_unknown_region_fails_closed():
    world = seed17_world()
    forecast = forecast_session(world, (987, 986, 63), position=3, tile_limit=512, edge_pad=0)
    assert forecast.exchange_estimate is None
    assert forecast.exchange_ceiling == 512 + 34


# ------------------------------------------------------------ month identity


def test_gate_month_is_current_month_not_serialized_anchor():
    world = world_for()
    gate = qualified_capture_month(world)
    assert gate is world.production.qualification.current_month
    assert gate == GATE_MONTH
    anchor = world.qualification.qualified_month
    assert anchor == ANCHOR_MONTH
    assert anchor is not gate


def test_gate_month_matches_seed17_chain():
    world = seed17_world()
    gate = qualified_capture_month(world)
    assert gate == GATE_MONTH
    assert world.qualification.qualified_month == ANCHOR_MONTH
    assert world.qualification.qualified_month is not gate


# ------------------------------------------------ runtime guard (fake wire)


def _prepare(tmp_path):
    (tmp_path / "graphics-identity.json").write_text("{}")
    (tmp_path / "runtime-identity.json").write_text(json.dumps(dict(welcome=dict(seed=17))))


def _row(request):
    if request.kind == "settings":
        return [1, 0, 0, 3, 0, 10, 50, 100]
    if request.kind == "engines":
        return [7]
    if request.kind == "engine":
        return [7, 1, 0, 30, 1000, 365, 40]
    return [request.arg, 0, 0, 1] + [0] * 10 + [-1, 1, 8, 1, 1]


def capture_fake(brackets):
    """Fake planning exchange; `brackets` supplies (before, after) per call,
    the last repeating on overflow. Every exchange is retained on disc as a
    request/response pair even when the guard rejects it."""
    state = {"calls": 0}

    async def exchange(session, request, directory, response_type):
        state["calls"] += 1
        before, after = brackets[min(state["calls"] - 1, len(brackets) - 1)]
        payload = dict(
            protocol=1,
            type="planning_read_result",
            request_id=request.request_id,
            kind=request.kind,
            arg=request.arg,
            src=request.src,
            dst=request.dst,
            cargo=request.cargo,
            before=before,
            after=after,
            data=_row(request),
        )
        raw = json.dumps(payload, separators=(",", ":")).encode()
        assert len(raw) <= 512
        (directory / (request.request_id + "-request.json")).write_bytes(request.to_bytes())
        (directory / (request.request_id + "-response.json")).write_bytes(raw)
        return response_type.parse_for(request, raw)

    return exchange, state


def _run_capture(tmp_path, brackets, *, relationship=(0, 1, 1), prefix="n0-"):
    _prepare(tmp_path)
    exchange, state = capture_fake(brackets)
    backend = NS(health=lambda: None, session=object())
    world = seed17_world()

    def run():
        return asyncio.run(
            capture_planning_facts(
                backend,
                NS(directory=tmp_path),
                world,
                read_exchange=exchange,
                retain=False,
                relationship=relationship,
                prefix=prefix,
                capture_budget=DemoBudgets(),
            )
        )

    return run, backend, state


def test_runtime_guard_accepts_in_window_bracket(tmp_path):
    run, backend, _state = _run_capture(tmp_path, [(MARCH_START, MARCH_START)])
    captured = run()
    assert len(captured.tiles) == 450 and len(captured.coverage) == 900
    assert backend.planning_read_count == 453
    assert backend.planning_read_attempts == 453
    captured.require_world(seed17_world())


def test_runtime_guard_rejects_bracket_at_exclusive_end(tmp_path):
    end = GATE_MONTH.end_date
    run, backend, state = _run_capture(tmp_path, [(end, end)])
    with pytest.raises(CaptureWindowExceeded) as info:
        run()
    error = info.value
    assert error.relationship == (0, 1, 1)
    assert error.request_id == "planning-n0-0"
    assert error.cycle == 1
    assert (error.before, error.after) == (end, end)
    assert (error.month_start, error.month_end) == (MARCH_START, end)
    assert error.exchanges_so_far == 0
    assert str(error) == (
        "CAPTURE_WINDOW_EXCEEDED: request_id=planning-n0-0 cycle=1 "
        "relationship=0/1/1 observed=[712313, 712313] "
        "qualified_window=[712282, 712313) exchanges_so_far=0"
    )
    assert state["calls"] == 1
    assert backend.planning_read_attempts == 1
    assert backend.planning_read_count == 0
    assert len(list(tmp_path.glob("*-request.json"))) == 1
    assert len(list(tmp_path.glob("*-response.json"))) == 1


def test_runtime_guard_rejects_bracket_past_exclusive_end(tmp_path):
    run, backend, _state = _run_capture(tmp_path, [(MARCH_START, GATE_MONTH.end_date + 1)])
    with pytest.raises(CaptureWindowExceeded) as info:
        run()
    assert info.value.after == GATE_MONTH.end_date + 1
    assert backend.planning_read_count == 0


def test_runtime_guard_stops_subsequent_requests_mid_capture(tmp_path):
    start, end = MARCH_START, GATE_MONTH.end_date
    inside = (start, start)
    run, backend, state = _run_capture(tmp_path, [inside, inside, inside, (end, end)])
    with pytest.raises(CaptureWindowExceeded) as info:
        run()
    assert info.value.exchanges_so_far == 3
    assert info.value.request_id == "planning-n0-3"
    assert state["calls"] == 4
    assert backend.planning_read_attempts == 4
    assert backend.planning_read_count == 3
    assert len(list(tmp_path.glob("*-request.json"))) == 4
    assert len(list(tmp_path.glob("*-response.json"))) == 4


def test_incomplete_capture_persists_no_facts_artifact(tmp_path):
    start, end = MARCH_START, GATE_MONTH.end_date
    run, _backend, _state = _run_capture(tmp_path, [(start, start), (start, start), (end, end)])
    with pytest.raises(CaptureWindowExceeded):
        run()
    # Discs stay; no complete facts artifact for the incomplete relationship.
    assert not (tmp_path / "supplemental-planning-facts.json").exists()
    assert not (tmp_path / "network-facts-0.json").exists()


def test_capture_discs_are_all_in_window_when_accepted(tmp_path):
    run, backend, _state = _run_capture(tmp_path, [(MARCH_START, MARCH_START)])
    run()
    responses = [json.loads(p.read_bytes()) for p in sorted(tmp_path.glob("*-response.json"))]
    assert responses
    assert all(MARCH_START <= r["before"] <= r["after"] < GATE_MONTH.end_date for r in responses)
    assert backend.planning_read_count == 453


# ------------------------------------------------------------ compatibility


def test_cycle_request_id_scheme_is_byte_compatible():
    assert cycle_request_id("planning-n0-0", 1) == "planning-n0-0"
    assert cycle_request_id("planning-seal", 1) == "planning-seal"
    assert cycle_request_id("random-generation", 1) == "random-generation"
    assert cycle_request_id("planning-n0-0", 2) == "planning-n0-0-c2"
    assert cycle_request_id("random-generation", 2) == "random-generation-c2"


def test_plan_sessions_does_not_mutate_relationship_inputs():
    relationships = [(0, 1, 1), (2, 3, 4)]
    forecasts = [fc(relationships[0]), fc(relationships[1], 1)]
    plan_sessions(relationships, GATE_MONTH, MARCH_START, forecasts)
    assert relationships == [(0, 1, 1), (2, 3, 4)]


def _replay_fixture(tmp_path, metadata, capture_budget):
    world = seed17_world()
    _prepare(tmp_path)
    relationships, rejected = bounded_relationships(world, metadata)
    (tmp_path / "network-candidates.json").write_text(
        json.dumps(dict(relationships=[list(r) for r in relationships], rejected=rejected))
    )
    exchange, _state = capture_fake([(MARCH_START, MARCH_START)])
    facts = []
    for position, relationship in enumerate(relationships):
        facts.append(
            asyncio.run(
                capture_planning_facts(
                    NS(health=lambda: None, session=object()),
                    NS(directory=tmp_path),
                    world,
                    read_exchange=exchange,
                    retain=False,
                    relationship=relationship,
                    prefix=f"n{position}-",
                    capture_budget=capture_budget,
                )
            )
        )
    return world, metadata, facts


def test_replay_schedule_era_replays_planned_positions_in_order(tmp_path):
    budget = DemoBudgets(capture_tile_limit=2048)
    metadata = {"random_world": True, "random_budget": budget.model_dump()}
    world, metadata, facts = _replay_fixture(tmp_path, metadata, budget)
    for position, fact in enumerate(facts):
        (tmp_path / f"network-facts-{position}.json").write_text(fact.model_dump_json())
    # The schedule-era marker is the diagnostic capture_preflight key.
    (tmp_path / "planning-diagnostic.json").write_text(
        json.dumps({"capture_preflight": {"planned": [], "deferred": []}})
    )
    assert replay_network_capture(tmp_path, world, metadata) == facts


def test_replay_legacy_era_without_marker_replays_every_position(tmp_path):
    metadata = {"random_world": True, "random_budget": DemoBudgets().model_dump()}
    world, metadata, facts = _replay_fixture(tmp_path, metadata, DemoBudgets())
    for position, fact in enumerate(facts):
        (tmp_path / f"network-facts-{position}.json").write_text(fact.model_dump_json())
    assert replay_network_capture(tmp_path, world, metadata) == facts


def test_replay_refuses_facts_artifact_for_deferred_relationship(tmp_path, monkeypatch):
    metadata = {"random_world": True, "random_budget": DemoBudgets().model_dump()}
    world, metadata, facts = _replay_fixture(tmp_path, metadata, DemoBudgets())
    for position, fact in enumerate(facts):
        (tmp_path / f"network-facts-{position}.json").write_text(fact.model_dump_json())
    (tmp_path / "planning-diagnostic.json").write_text(json.dumps({"capture_preflight": {}}))

    def deferred_plan(relationships, month, current_date, forecasts, **kwargs):
        return CaptureSchedule(
            tuple(
                SessionDecision(
                    relationship=f.relationship,
                    position=f.position,
                    exchange_estimate=None,
                    day_span=None,
                    planned_first_date=current_date,
                    planned_last_date=None,
                    remaining_window_days=month.end_date - current_date,
                    fits=False,
                    reason="CAPACITY_UNKNOWN: test-forced deferral",
                )
                for f in forecasts
            )
        )

    monkeypatch.setattr(native_network, "plan_sessions", deferred_plan)
    with pytest.raises(ValueError, match="deferred relationship"):
        replay_network_capture(tmp_path, world, metadata)
