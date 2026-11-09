"""Pure month-capacity scheduling for supplemental relationship capture.

E156 context (attempt 4 ``playable-demo-da185e2c41dd45278e4152dcd7521af8``,
permanently FAILED/SEALED): cycle-1 session n2 issued 1794 planning reads,
ran past the exclusive end (712313) of the qualified observation month,
and the typed per-session gate discarded the whole session. Scheduling had
no remaining-window capacity accounting, and the effective session cost
depended on ``paused_world_clock`` freeze efficacy - a runtime-observed
property (freeze failed for sessions n1/n2 while all six console commands
echoed as processed) - not a code-level guarantee.

Policy here is conservative and additive: it refuses capture work the
configured capacity policy cannot bound, records deferred relationships
with explicit reasons, and claims no guarantee that a planned session ever
completes. The evidence model of record is untouched for definition:
per-session facts validation (`require_world`,
supplemental_planning_facts.py) and the post-qualification seal bracket
(freight_runtime_planning.py) stay authoritative. This module only decides
which sessions may start and in which order.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from app.simulation.openttd.production_observation import EconomyMonth

# Heuristic policy constants. Each is derived from the E156 attempt-4
# evidence and is an operating assumption of the capacity policy, not an
# invariant of the OpenTTD engine: capture runs may hold in a frozen clock
# for an entire session (attempt 3) or resume at live rate early
# (attempt 4 sesions n1/n2), so costs here are lower bounds on planning
# fidelity, never guarantees.
HEURISTIC_EXCHANGES_PER_DAY = 74
"""Best-effort live-rate bound: attempt-4 response-disc mtimes advance one
game day per ~74 planning reads on the continuously-running clock."""
HEURISTIC_INTER_SESSION_DAYS = 1
"""Conservative inter-session gap: opening one session may advance the clock
at live rate before and after the previous session closed; the attempt-4
disc series drifted 0-1 game day between consecutive session opens."""
CAPTURE_FIXED_EXCHANGES = 2
"""Exchange reads before any engine or tile rows: settings + engines list
(capture_planning_facts read schedule)."""
MAX_ENGINES_BOUND = 32
"""Ceiling for engine rows in one session: the facts contract
MAX_ENGINES (supplemental_planning_facts.py); estimate-only, not a
guarantee."""
CAPTURE_BUDGET_OVERHEAD = 34
"""Guaranteed capture read budget: capture_planning_facts refuses beyond
tile_limit + 34 reads (CAPTURE_REQUEST_BUDGET)."""
DEFAULT_TILE_LIMIT = 256
"""Historical capture tile limit when no capture budget is configured."""


class CaptureCapacityError(ValueError):
    """Plan refusal at capture open: the capacity policy schedules no session."""


class CaptureWindowExceeded(ValueError):
    """Runtime guard trip: an exchange bracket left the qualified month.

    Carries the evidence of the offending exchange (relationship identity,
    request id, cycle, observed bracket, active qualified month boundaries
    and the count of exchanges completed before the violation). The
    produced request/response discs on disk remain untouched; no facts
    artifact is written for the session.
    """

    def __init__(
        self,
        *,
        relationship: tuple[int, int, int],
        request_id: str,
        cycle: int,
        before: int,
        after: int,
        month_start: int,
        month_end: int,
        exchanges_so_far: int,
    ) -> None:
        self.relationship = tuple(relationship)
        self.request_id = request_id
        self.cycle = cycle
        self.before = before
        self.after = after
        self.month_start = month_start
        self.month_end = month_end
        self.exchanges_so_far = exchanges_so_far
        super().__init__(
            "CAPTURE_WINDOW_EXCEEDED: request_id="
            + request_id
            + " cycle="
            + str(cycle)
            + " relationship="
            + "/".join(map(str, self.relationship))
            + f" observed=[{before}, {after}]"
            + f" qualified_window=[{month_start}, {month_end})"
            + " exchanges_so_far="
            + str(exchanges_so_far)
        )


def qualified_capture_month(world) -> EconomyMonth:
    """Active observation month for the runtime guard and preflight.

    Resolves the month distinction documented by E156 against the object
    model: the gate month is ``world.production.qualification.current_month``
    (``ProductionWindowQualification.observed_months[-1]``); the serialized
    ``world-planning-observation.json`` anchor is a different property,
    ``world.qualification.qualified_month``, the measured month behind
    ``QualifiedProductionResult``. Attempt 4 seals both: gate month March
    ``[712282, 712313)`` while the serialized anchor was February
    ``[712254, 712282)``. No substitution or inference of a different month
    is allowed.
    """
    return world.production.qualification.current_month


@dataclass(frozen=True)
class SessionForecast:
    """Deterministic capacity forecast for one relationship capture session."""

    relationship: tuple[int, int, int]
    position: int
    region_tiles: int
    exchange_estimate: int | None  # None = unknown capacity; scheduler fails closed
    exchange_ceiling: int


@dataclass(frozen=True)
class SessionDecision:
    """One capture session's planned fit against the qualified month."""

    relationship: tuple[int, int, int]
    position: int
    exchange_estimate: int | None
    day_span: int | None
    planned_first_date: int | None
    planned_last_date: int | None
    remaining_window_days: int
    fits: bool
    reason: str | None


@dataclass(frozen=True)
class CaptureSchedule:
    decisions: tuple[SessionDecision, ...]

    @property
    def planned(self) -> tuple[SessionDecision, ...]:
        return tuple(d for d in self.decisions if d.fits)

    @property
    def deferred(self) -> tuple[SessionDecision, ...]:
        return tuple(d for d in self.decisions if not d.fits)

    def diagnostic(self) -> dict:
        """Additive planning-diagnostic record; never reinterprets history."""
        return dict(
            planned=[
                dict(
                    relationship=list(d.relationship),
                    position=d.position,
                    exchange_estimate=d.exchange_estimate,
                    planned_first_date=d.planned_first_date,
                    planned_last_date=d.planned_last_date,
                    remaining_window_days=d.remaining_window_days,
                )
                for d in self.planned
            ],
            deferred=[
                dict(
                    relationship=list(d.relationship),
                    position=d.position,
                    reason=d.reason,
                )
                for d in self.deferred
            ],
            policy=dict(
                exchanges_per_day=HEURISTIC_EXCHANGES_PER_DAY,
                inter_session_days=HEURISTIC_INTER_SESSION_DAYS,
            ),
        )


def forecast_session(
    world, relationship: tuple[int, int, int], *, position: int, tile_limit: int, edge_pad: int
) -> SessionForecast:
    """Deterministic capacity forecast for one relationship's capture schedule.

    The heuristic estimate reads ``region tiles + fixed reads + engine-list
    ceiling`` (the capture read schedule is settings, engines list, one read
    per listed engine, one per region tile). It is a heuristic: the true
    engine count is only observable at runtime, so estimates never imply a
    completion guarantee. The guaranteed bound is the capture read budget
    itself (``tile_limit + CAPTURE_BUDGET_OVERHEAD``), beyond which the
    session aborts with ``CAPTURE_REQUEST_BUDGET``. A region that cannot be
    computed offline fails closed with an unknown estimate.
    """
    ceiling = tile_limit + CAPTURE_BUDGET_OVERHEAD
    try:
        from app.demo_random import relationship_region

        region = relationship_region(world, relationship, tile_limit, edge_pad=edge_pad)
        tiles = region["width"] * region["height"]
    except ValueError, KeyError:
        return SessionForecast(
            relationship=relationship,
            position=position,
            region_tiles=0,
            exchange_estimate=None,
            exchange_ceiling=ceiling,
        )
    return SessionForecast(
        relationship=relationship,
        position=position,
        region_tiles=tiles,
        exchange_estimate=tiles + CAPTURE_FIXED_EXCHANGES + MAX_ENGINES_BOUND,
        exchange_ceiling=ceiling,
    )


def build_forecasts(relationships, world, capture_budget=None) -> tuple[SessionForecast, ...]:
    """Forecasts for every discovered relationship, discovery order preserved."""
    tile_limit = (
        capture_budget.capture_tile_limit if capture_budget is not None else DEFAULT_TILE_LIMIT
    )
    edge_pad = capture_budget.capture_edge_pad if capture_budget is not None else 0

    def region(relationship, position):
        return forecast_session(
            world, relationship, position=position, tile_limit=tile_limit, edge_pad=edge_pad
        )

    return tuple(
        region(relationship, position) for position, relationship in enumerate(relationships)
    )


@dataclass(frozen=True)
class CapacityPolicy:
    """Configurable capacity policy parameters; heuristics, not engine bounds."""

    exchanges_per_day: int = HEURISTIC_EXCHANGES_PER_DAY
    inter_session_days: int = HEURISTIC_INTER_SESSION_DAYS


def plan_sessions(
    relationships,
    month: EconomyMonth,
    current_date: int,
    forecasts,
    *,
    policy: CapacityPolicy = CapacityPolicy(),
) -> CaptureSchedule:
    """Deterministic smallest-first capture plan inside one observation month.

    Ordering: ascending heuristic estimate with the ``(src, dst, cargo)``
    identity as the stable tie-breaker. Deferred sessions never start and
    are recorded with typed reasons. ``day_span`` is the conservative
    live-rate policy cost ``ceil(estimate / exchanges_per_day)`` plus the
    inter-session gap counted against the next session's open; a planned
    session is not a promise of completion - the runtime guard
    (`CaptureWindowExceeded`) and the per-session ``require_world`` gate
    remain the authoritative stop points. ``current_date`` is the caller's
    best known world date; the exclusive month end (``after < end_date``)
    is preserved: a session whose planned last day is ``end_date - 1`` fits,
    one whose planned last day reaches ``end_date`` or later is deferred.
    """
    if len(relationships) != len(forecasts):
        raise ValueError("capture schedule forecast mismatch")

    def estimate(f: SessionForecast) -> tuple[float, tuple[int, int, int]]:
        return (
            math.inf if f.exchange_estimate is None else f.exchange_estimate,
            f.relationship,
        )

    ordered = sorted(forecasts, key=estimate)
    decisions: list[SessionDecision] = []
    planned_date = current_date
    for forecast in ordered:
        remaining = month.end_date - planned_date
        if forecast.exchange_estimate is None:
            decisions.append(
                SessionDecision(
                    relationship=forecast.relationship,
                    position=forecast.position,
                    exchange_estimate=None,
                    day_span=None,
                    planned_first_date=planned_date,
                    planned_last_date=None,
                    remaining_window_days=remaining,
                    fits=False,
                    reason="CAPACITY_UNKNOWN: region forecast unavailable; failing closed",
                )
            )
            continue
        if forecast.region_tiles + CAPTURE_FIXED_EXCHANGES > forecast.exchange_ceiling:
            decisions.append(
                SessionDecision(
                    relationship=forecast.relationship,
                    position=forecast.position,
                    exchange_estimate=forecast.exchange_estimate,
                    day_span=None,
                    planned_first_date=planned_date,
                    planned_last_date=None,
                    remaining_window_days=remaining,
                    fits=False,
                    reason=(
                        "CAPTURE_READ_BUDGET: region tiles "
                        + str(forecast.region_tiles)
                        + " exceed capture read budget "
                        + str(forecast.exchange_ceiling)
                        + "; session would abort with CAPTURE_REQUEST_BUDGET"
                    ),
                )
            )
            continue
        day_span = math.ceil(forecast.exchange_estimate / policy.exchanges_per_day)
        fits = planned_date + day_span <= month.end_date
        if fits:
            reason = None
        else:
            reason = (
                "INSUFFICIENT_CAPACITY: estimated live-rate span "
                + str(day_span)
                + "d from planned start "
                + str(planned_date)
                + " reaches "
                + str(planned_date + day_span - 1)
                + "; exclusive window ends "
                + str(month.end_date - 1)
            )
        decisions.append(
            SessionDecision(
                relationship=forecast.relationship,
                position=forecast.position,
                exchange_estimate=forecast.exchange_estimate,
                day_span=day_span,
                planned_first_date=planned_date,
                planned_last_date=planned_date + day_span - 1,
                remaining_window_days=remaining,
                fits=fits,
                reason=reason,
            )
        )
        if fits:
            planned_date = planned_date + day_span + policy.inter_session_days
    return CaptureSchedule(tuple(decisions))


def require_planned(schedule: CaptureSchedule, *, context: str = "capture open") -> CaptureSchedule:
    """Fail closed when the capacity policy planned no session at all.

    Raises the typed :class:`CaptureCapacityError` (message prefix
    ``CAPTURE_SCHEDULE_EMPTY``) listing every deferred relationship and its
    recorded reason. Feasibility-neutral by construction: this is the
    capacity preflight refusing work at capture open, not the planning
    pipeline's ``NO_FEASIBLE_SERVICES`` terminal, and it never asserts that
    a Random World is infeasible.
    """
    if schedule.planned:
        return schedule
    raise CaptureCapacityError(
        "CAPTURE_SCHEDULE_EMPTY: "
        + str(len(schedule.deferred))
        + " relationship(s) deferred by capacity policy ("
        + context
        + "); "
        + " | ".join(
            str(list(d.relationship)) + ": " + (d.reason or "unspecified")
            for d in schedule.deferred
        )
    )
