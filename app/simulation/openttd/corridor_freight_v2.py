"""Versioned corridor freight v2 wire contract (protocol 8, additive).

Protocol 8 is a NEW protocol alongside the frozen protocol-5 chain. Protocol
5 and its GameScript package (``d5_freight_package``) are byte-preserved:
this module re-derives the v2 attempt from the A1 close-out world instead —
the consumed ``d5-corridor-extension-native-candidate-3`` after-save
``3748e00ce57bcb076466f50cac3776c202b4fd130d6c6071935e9d43e45420bd`` at
£490,257 — under the resolved design-review conditions
(``docs/d5-freight-delivery-v2-design-review-2026-11-01.md``):

- F-2 (route): the physical 31-tile construction witness is bound verbatim
  from the extension module and is NOT the vehicle route. The vehicle
  route is the 29-tile ordered subsequence that drops the stale D4 bay
  50351 and the backtracked repeat of 50095; the new delivery bay
  50862 is last, its front 50863 penultimate, and 45743 the single
  depot-adjacent tile. Route and witness bind as separate digests.
- F-3 (pins): all D4-era world pins (funds 492149, delivery 50351,
  industry 1) are dropped. Every v2 world identity is re-derived from the
  A1 after-save; the delivery industry id is NEVER pinned — it is
  discovered natively under the unique-cargo-accepting-industry policy
  during the site readback and only then latched.
- F-4 (order flags): the real 15.x flag values are pinned: ``OF_NONE``
  == 0, ``OF_FULL_LOAD`` == 64 (documented so it can never silently
  return), ``OF_NO_LOAD`` == 128. v2 orders use OF_NONE at the pickup
  stop and OF_NO_LOAD at the delivery bay; OF_FULL_LOAD must never be
  issued. ``AreOrderFlagsValid`` is the two-argument 15.x form and every
  append takes a stop TILE, not a station id (N1/N2/N3).
- F-5 (schedule): cycle-looped ``load``/``transit``/``deliver`` windows
  with per-cycle snapshot discipline — the departure snapshot gates
  ``0 < observed_load <= capacity``, the delivery exchange enforces
  ``load == 0``, both monitor deltas equal the departure load, and the
  consume-with-recheck re-arms both monitors at zero.
- F-6 (funds): equation of record
  ``funds(final) == 490257 - purchase_quote + sum(income deltas from the
  per-exchange quarter-income reads) + sum(running-cost entries)``, where
  each exchange span's running-cost attribution
  (``deltaFfunds - deltaIncome``) is non-positive in magnitude, bounded
  by a named per-exchange allowance and must reconcile to residual == 0.
  Sign-convention normalization of record (15.x): quarterly income reads
  positive, quarterly expenses read negative (costs subtracted), so the
  ledger never half-signs expenses: the equation works from funds levels
  and income reads only and never re-labels an expense sign.
- F-7/F-8/F-9 (budget): the schedule layer is the authority. Planned cycle
  count is fixed at staging from the request arithmetic
  ``10 fixed + 2 tail + 3*cycles <= 32`` (6 cycles max in one attempt),
  the Python runner re-checks remaining request/wall/day budgets before
  dispatching every cycle group, and physics caps (per-cycle economy-day
  cap = 60-day budget // cycles) discharge F-7's day authority.
- F-10 (engine): one buildable road engine at a PROVISIONAL offline pin
  (the ``attempt19`` retained census reality) with a fail-closed native
  admission: the request ships ``ENGINE_PIN_V2`` and the engine readback
  refuses ``NO_ENGINE`` / ``UNAVAILABLE_ENGINE`` /
  ``ENGINE_PIN_MISMATCH`` before any purchase mutation. The v1 op that
  ignored the request pin and picked the lowest compatible id is not
  copied: v2 honors the pin exactly.
- F-11: a typed ``ZERO_DEPARTED`` outcome exists at both the cycle-event
  and the phase-outcome layer; it is never a success relabel.
- F-12: the directed depot-entry probe (``AreRoadTilesConnected``
  front-to-depot in both directions) is part of the site admission.
- F-13: every window exchange echoes its elapsed ticks and economy days
  from the GameScript loop state; the native runner adds per-exchange
  wall-clock seconds to the retained records.

Every named constant of the v1 module with a different v2 value keeps a
``_V2`` suffix; no v1 identity is relabeled. Byte bounds are measured
against the actual canonical wire payloads in the focused suite and stay
under both the GSAdmin.Send ceiling (``MAX_FREIGHT_SEND_BYTES``) and the
AdminPort frame ceiling (``MAX_GAMESCRIPT_PAYLOAD_BYTES``).
The module validates invariants at import time; it issues no requests and
executes nothing.
"""

import hashlib
import json
from typing import Annotated, Literal

from pydantic import Field, StrictBool, StrictInt, model_validator

from app.planning.canonical import canonical_bytes
from app.planning.domain import Contract, Digest
from app.simulation.openttd.corridor_construction import (
    CompanyID,
    Money,
    OwnerID,
    SignedMoney,
    StationID,
    TileID,
)
from app.simulation.openttd.proof.corridor_extension_native import PINNED_WITNESS

FREIGHT_PROTOCOL_V2 = 8
# Measured bounds of record (canonical UTF-8 JSON, the focused suite asserts
# the widest built payloads): the 29-tile site request with both digests
# measures 640 bytes, and the widest response (the engine identity echo with
# its compatible-universe fleet) measures 1354 bytes — the response bound is
# capped below the GSAdmin.Send ceiling (1450) that actually carries the
# GameScript readback frames. Named constants first, per the protocol-5/6
# precedent. The Admin frame ceiling is unchanged.
MAX_FREIGHT_REQUEST_BYTES_V2 = 768
MAX_FREIGHT_RESPONSE_BYTES_V2 = 1400
MAX_FREIGHT_SEND_BYTES = 1450
MAX_GAMESCRIPT_PAYLOAD_BYTES = 32763
MAX_FREIGHT_ROUTE_TILES_V2 = 32
MAX_FREIGHT_WITNESS_TILES_V2 = 48
MAX_FREIGHT_FLEET_ECHO_V2 = 12
FREIGHT_MAP_WIDTH = 256
FREIGHT_MAP_HEIGHT = 256
FREIGHT_MAX_TILE_ID = FREIGHT_MAP_WIDTH * FREIGHT_MAP_HEIGHT - 1
FREIGHT_SCHEDULE_VERSION = 2
# Attempt identity of record: E53's fix round leaves the once-staged
# D5-FREIGHT-2 name on its (stale-by-drift, never consumed) candidate; a
# fresh candidate derives a fresh identity instead of reusing it.
FREIGHT_ATTEMPT_V2 = "D5-FREIGHT-3"
FREIGHT_COMPANY = 0
FREIGHT_CARGO_ID = 1
# World pins of record (E41-E44): the A1 close-out after-save and its funds.
A1_AFTER_SAVE_SHA256_V2 = (
    "3748e00ce57bcb076466f50cac3776c202b4fd130d6c6071935e9d43e45420bd"
)
FUNDS_AT_A1_CLOSE = 490257
# Per-op cost ceiling of record: the quote-first purchase stays at or below
# £5,000 (locked engine decision; the census price £4,429 fits).
FREIGHT_MAX_COST_V2 = 5000
# F-1/F-10 resolution of record (operator Option B): the engine pin is a
# PROVISIONAL offline pin re-derived from the attempt19 retained census
# (artifacts/runtime/openttd-15.3-first-freight-delivery-attempt19
# /network-facts-0.json; docs/road-vehicle-lifecycle-proof.md). The census
# world (seed 42) is NOT the A1 world, so the identity is provisional on
# disk; the native engine readback admits it fail-closed: any identity
# deviation refuses ENGINE_PIN_MISMATCH before any purchase mutation.
ENGINE_PIN_V2 = 123
ENGINE_PIN_PROVISIONAL_V2 = True
ENGINE_CENSUS_V2 = dict(
    cargo=1,
    capacity=20,
    price=4429,
    running_cost_per_economy_year=421,
    max_speed=48,
)
# F-2: the physical witness is bound verbatim from the extension module; the
# vehicle route is the ordered subsequence that removes the stale D4 bay and
# the backtracked repeat of its front tile.
FREIGHT_WITNESS_LENGTH_V2 = 31
FREIGHT_ROUTE_LENGTH_V2 = 29
FREIGHT_STALE_DELIVERY_TILE_V2 = 50351
FREIGHT_STALE_BACKTRACK_TILE_V2 = 50095
A1_PICKUP_STOP_TILE_V2 = 45748
A1_PICKUP_FRONT_TILE_V2 = 45747
A1_DELIVERY_STOP_TILE_V2 = 50862
A1_DELIVERY_FRONT_TILE_V2 = 50863
A1_DEPOT_TILE_V2 = 45487
A1_DEPOT_FRONT_TILE_V2 = 45743
# Schedule caps of record (F-5/F-7/F-8/F-9/§4): 10 fixed + 2 tail + 3 per
# cycle <= the 32-request budget fixes the planned cycle count at staging;
# the 60-economy-day attempt budget leases each cycle 10 days; wall budgets
# keep the legacy 60 s window / 900 s session shape in the ceremony module.
FREIGHT_REQUEST_BUDGET_V2 = 32
FREIGHT_FIXED_EXCHANGE_COUNT_V2 = 10
FREIGHT_TAIL_EXCHANGE_COUNT_V2 = 2
FREIGHT_DAY_BUDGET_V2 = 60
FREIGHT_CYCLE_WALL_CAP_SECONDS_V2 = 180
# Order-flag pins from the real 15.x header (N2). OF_FULL_LOAD is documented
# so the forbidden value can never silently return; v2 orders never use it.
OF_NONE_V2 = 0
OF_FULL_LOAD_FORBIDDEN_V2 = 64
OF_NO_LOAD_V2 = 128
# Per-window caps: the economy-day cap is the F-7 lease of record; the tick
# cap is the same 2048-tick window bound protocol 5 carried.
WATCH_MAX_TICKS_V2 = 2048
# F-6 taxonomy of record: an exchange span may attribute running costs only
# within this allowance (census running cost 421/economy-year over the
# 10-day window lease, rounded up); anything outside the taxonomy is a
# typed funds drift halt. Every exchange readback carries the quarter
# income, so each span attributes income deltas exactly.
FREIGHT_RUNNING_COST_ALLOWANCE_V2 = 12
FREIGHT_FUNDS_CATEGORIES_V2 = frozenset(
    {"PURCHASE", "INCOME", "RUNNING_COST", "ZERO"}
)

FREIGHT_OPS_V2 = (
    "site",
    "engine",
    "purchase",
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
)

FreightOpV2 = Literal[
    "site",
    "engine",
    "purchase",
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
]

FreightStatusV2 = Literal[
    "READY",
    "BUILT",
    "READ",
    "ORDERED",
    "ORDER_SET_VERIFIED",
    "ARMED",
    "STARTED",
    "LOADED",
    "AT_DELIVERY",
    "DELIVERED",
    "FINANCE_VERIFIED",
    "PHASE_STOPPED",
    "INVALID_COMPANY",
    "INVALID_SITE",
    "INVALID_LOCATION",
    "INVALID_ROUTE",
    "NO_ENGINE",
    "UNAVAILABLE_ENGINE",
    "ENGINE_PIN_MISMATCH",
    "ENGINE_LIMIT",
    "INSUFFICIENT_FUNDS",
    "COST_LIMIT",
    "COST_CHANGED",
    "PAUSED",
    "ALREADY_ATTEMPTED",
    "STALE_ADMISSION",
    "UNSUPPORTED_NATIVE_FACT",
    "READBACK_MISMATCH",
    "OUT_OF_ORDER",
    "CLOCK_STALLED",
    "WINDOW_EXHAUSTED",
    "ZERO_DEPARTED",
]

_FREIGHT_SUCCESS_STATUS_V2: dict[FreightOpV2, str] = {
    "site": "READY",
    "engine": "READY",
    "purchase": "BUILT",
    "vread": "READ",
    "order": "ORDERED",
    "order-read": "ORDER_SET_VERIFIED",
    "monitor": "ARMED",
    "start": "STARTED",
    "load-watch": "LOADED",
    "transit-watch": "AT_DELIVERY",
    "deliver-watch": "DELIVERED",
    "finance": "FINANCE_VERIFIED",
    "finish": "PHASE_STOPPED",
}
_FREIGHT_INCONCLUSIVE_STATUS_V2 = frozenset(
    {"WINDOW_EXHAUSTED", "CLOCK_STALLED"}
)
# F-11: the typed zero-departure cycle event is its own status class: never
# success, never plain inconclusive — the attempt outcome types it on top.
_FREIGHT_ZERO_STATUS_V2 = frozenset({"ZERO_DEPARTED"})
_FREIGHT_REFUSAL_STATUS_V2 = frozenset(
    {
        "INVALID_SITE",
        "INVALID_COMPANY",
        "INVALID_LOCATION",
        "INVALID_ROUTE",
        "NO_ENGINE",
        "UNAVAILABLE_ENGINE",
        "ENGINE_PIN_MISMATCH",
        "ENGINE_LIMIT",
        "INSUFFICIENT_FUNDS",
        "COST_LIMIT",
        "COST_CHANGED",
        "PAUSED",
        "ALREADY_ATTEMPTED",
        "STALE_ADMISSION",
        "UNSUPPORTED_NATIVE_FACT",
        "READBACK_MISMATCH",
        "OUT_OF_ORDER",
    }
)
_FREIGHT_REPORTED_STATUS_V2 = (
    _FREIGHT_INCONCLUSIVE_STATUS_V2
    | _FREIGHT_ZERO_STATUS_V2
    | _FREIGHT_REFUSAL_STATUS_V2
    | frozenset(_FREIGHT_SUCCESS_STATUS_V2.values())
)
# Post-mutation refusal sets (conservative, as in protocol 5): a purchase
# COST_CHANGED may fire after the build command was issued, so the honest
# outcome label is UNCERTAIN_AFTER_FAILED_COMMAND, never untouched-world.
_FREIGHT_POST_MUTATION_STATUS_V2 = {
    "purchase": frozenset(
        {"COST_CHANGED", "READBACK_MISMATCH", "UNSUPPORTED_NATIVE_FACT"}
    ),
    "order": frozenset({"READBACK_MISMATCH", "UNSUPPORTED_NATIVE_FACT"}),
    "start": frozenset({"READBACK_MISMATCH", "UNSUPPORTED_NATIVE_FACT"}),
    "finish": frozenset({"READBACK_MISMATCH", "UNSUPPORTED_NATIVE_FACT"}),
}

_FREIGHT_FIXED_SEQUENCE_V2: tuple[tuple[str, FreightOpV2], ...] = (
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
)
_FREIGHT_TAIL_SEQUENCE_V2: tuple[tuple[str, FreightOpV2], ...] = (
    ("finance-00", "finance"),
    ("finish-00", "finish"),
)
_FREIGHT_CYCLE_SEQUENCE_V2: tuple[tuple[str, FreightOpV2], ...] = (
    ("load", "load-watch"),
    ("transit", "transit-watch"),
    ("deliver", "deliver-watch"),
)


def freight_cycle_sequence_v2(cycles: int) -> tuple[tuple[str, FreightOpV2], ...]:
    """The cycle-looped exchange sequence for ``cycles`` planned cycles."""
    if not 1 <= cycles <= freight_max_cycle_count_v2(FREIGHT_REQUEST_BUDGET_V2):
        raise ValueError("cycle count outside the planned schedule arithmetic")
    sequence: list[tuple[str, FreightOpV2]] = []
    for index in range(cycles):
        for base_id, op in _FREIGHT_CYCLE_SEQUENCE_V2:
            sequence.append((f"{base_id}-{index:02d}", op))
    return tuple(sequence)


def freight_exchange_sequence_v2(cycles: int) -> tuple[tuple[str, FreightOpV2], ...]:
    """The full ordered exchange schedule: fixed + cycles + tail."""
    return (
        _FREIGHT_FIXED_SEQUENCE_V2
        + freight_cycle_sequence_v2(cycles)
        + _FREIGHT_TAIL_SEQUENCE_V2
    )


def freight_exchange_ids_v2(cycles: int) -> tuple[str, ...]:
    """Ordered exchange ids for ``cycles`` planned cycles."""
    return tuple(exchange_id for exchange_id, _ in freight_exchange_sequence_v2(cycles))


def freight_planned_cycle_count_v2(budget: int = FREIGHT_REQUEST_BUDGET_V2) -> int:
    """The staging arithmetic of record: 10 fixed + 2 tail + 3*cycles <= budget."""
    span = budget - FREIGHT_FIXED_EXCHANGE_COUNT_V2 - FREIGHT_TAIL_EXCHANGE_COUNT_V2
    if span < 3:
        return 0
    return span // 3


def freight_exchange_cycle_index_v2(exchange_id: str) -> int | None:
    """The planned cycle index of a cycle exchange id, or None for fixed/tail."""
    cycle_bases = tuple(base for base, _ in _FREIGHT_CYCLE_SEQUENCE_V2)
    parts = exchange_id.split("-")
    if len(parts) != 2 or parts[0] not in cycle_bases:
        return None
    return int(parts[1])


def freight_max_cycle_count_v2(budget: int = FREIGHT_REQUEST_BUDGET_V2) -> int:
    """The maximum planned cycle count the request budget covers (§4 arithmetic)."""
    return freight_planned_cycle_count_v2(budget)


def freight_cycle_group_budget_ok_v2(
    exchanges_used: int, *, budget: int = FREIGHT_REQUEST_BUDGET_V2
) -> bool:
    """F-8 budget pre-check: a cycle group is dispatched only fully budgeted."""
    return exchanges_used + 3 <= budget


def freight_window_dispatch_refusal_v2(days_used: int, watch_days: int) -> str | None:
    """The E53 aggregate economy-day authority gate for one watch dispatch.

    Every watch window leases its per-cap economy days; the 60-day attempt
    authority binds the aggregate elapsed time across ALL windows, not any
    single one. ``days_used`` is the economy-day span the already-verified
    windows covered (each readback's own day echo against the start
    exchange's day-of-record). A window may be dispatched only while its
    lease fits what remains: ``days_used + watch_days`` crossing the
    authority is a typed pre-dispatch halt. Because every window also stops
    at its own lease day (``WINDOW_EXHAUSTED``), the aggregate span stays
    inside the budget by induction — the gate makes that induction check,
    never a promise.
    """
    if days_used + watch_days > FREIGHT_DAY_BUDGET_V2:
        return (
            f"a {watch_days}-economy-day window cannot fit the "
            f"{FREIGHT_DAY_BUDGET_V2}-day aggregate attempt authority: "
            f"{days_used} already elapsed"
        )
    return None


def window_watch_day_cap_v2(op: FreightOpV2) -> int:
    """The per-window economy-day lease the staged schedule rows carry.

    E53: all three watch windows lease the identical per-cap day count
    (the cycle day split of the attempt budget), so the row derivation
    stays uniform and the aggregate authority owns the budget arithmetic.
    Non-window operations carry no day lease (-1).
    """
    return FREIGHT_CYCLE_DAY_CAP_V2 if op in _FREIGHT_WATCH_OPS_V2 else -1


PLANNED_FREIGHT_CYCLES_V2 = freight_planned_cycle_count_v2()
PLANNED_FREIGHT_EXCHANGES_V2 = (
    FREIGHT_FIXED_EXCHANGE_COUNT_V2
    + 3 * PLANNED_FREIGHT_CYCLES_V2
    + FREIGHT_TAIL_EXCHANGE_COUNT_V2
)
# F-7's per-cycle economy-day lease of record: the 60-day attempt budget is
# leased evenly across the planned cycles at staging.
FREIGHT_CYCLE_DAY_CAP_V2 = FREIGHT_DAY_BUDGET_V2 // PLANNED_FREIGHT_CYCLES_V2
if FREIGHT_CYCLE_DAY_CAP_V2 * PLANNED_FREIGHT_CYCLES_V2 != FREIGHT_DAY_BUDGET_V2:
    raise RuntimeError("the cycle day lease must tile the attempt day budget exactly")
FREIGHT_EXCHANGE_IDS_V2: tuple[str, ...] = freight_exchange_ids_v2(
    PLANNED_FREIGHT_CYCLES_V2
)
_FREIGHT_OP_BY_ID_V2: dict[str, FreightOpV2] = dict(
    freight_exchange_sequence_v2(PLANNED_FREIGHT_CYCLES_V2)
)
_FREIGHT_CYCLE_INDEX_BY_ID_V2: dict[str, int] = {
    exchange_id: freight_exchange_cycle_index_v2(exchange_id)
    for exchange_id in FREIGHT_EXCHANGE_IDS_V2
}
if (
    len(FREIGHT_EXCHANGE_IDS_V2) != PLANNED_FREIGHT_EXCHANGES_V2
    or len(set(FREIGHT_EXCHANGE_IDS_V2)) != PLANNED_FREIGHT_EXCHANGES_V2
    or set(_FREIGHT_OP_BY_ID_V2.values()) != set(FREIGHT_OPS_V2)
    or PLANNED_FREIGHT_EXCHANGES_V2 > FREIGHT_REQUEST_BUDGET_V2
    or 3 * PLANNED_FREIGHT_CYCLES_V2
    > FREIGHT_REQUEST_BUDGET_V2 - FREIGHT_FIXED_EXCHANGE_COUNT_V2 - FREIGHT_TAIL_EXCHANGE_COUNT_V2
):
    raise RuntimeError("freight v2 schedule drifted from the planned cycle arithmetic")
if max(MAX_FREIGHT_REQUEST_BYTES_V2, MAX_FREIGHT_RESPONSE_BYTES_V2) > max(
    MAX_FREIGHT_SEND_BYTES, MAX_GAMESCRIPT_PAYLOAD_BYTES
):
    raise RuntimeError("freight v2 byte bounds exceed the AdminPort payload limits")

FreightActorIdV2 = Annotated[StrictInt, Field(ge=-1, le=65535)]
FreightPodV2 = Annotated[StrictInt, Field(ge=0, le=65535)]
FreightCargoV2 = Annotated[StrictInt, Field(ge=0, le=63)]
FreightIndustryV2 = Annotated[
    StrictInt, Field(ge=-1, le=65535)
]  # -1 is the undiscovered sentinel of record: industry ids are never pinned.
FreightIndustryCountV2 = Annotated[StrictInt, Field(ge=0, le=65535)]
FreightEighthsV2 = Annotated[StrictInt, Field(ge=0, le=8)]
FreightAmountV2 = Annotated[StrictInt, Field(ge=0, le=2147483647)]
FreightDateV2 = Annotated[StrictInt, Field(ge=-1, le=2147483647)]
FreightFlagsV2 = Annotated[StrictInt, Field(ge=0, le=255)]
FreightWatchTicksV2 = Annotated[StrictInt, Field(ge=-1, le=WATCH_MAX_TICKS_V2)]
FreightWatchDaysV2 = Annotated[StrictInt, Field(ge=-1, le=FREIGHT_DAY_BUDGET_V2)]
FreightOrderIndexV2 = Annotated[StrictInt, Field(ge=-1, le=1)]
FreightPairCountV2 = Annotated[StrictInt, Field(ge=0, le=64)]
FreightProgressV2 = Annotated[StrictInt, Field(ge=0, le=63)]
FreightRadiusV2 = Annotated[StrictInt, Field(ge=-1, le=255)]
FreightFleetV2 = Annotated[
    tuple[FreightActorIdV2, ...], Field(max_length=MAX_FREIGHT_FLEET_ECHO_V2)
]
FreightVehicleStateV2 = Literal[
    "INVALID",
    "IN_DEPOT",
    "RUNNING",
    "STOPPED",
    "AT_STATION",
    "BROKEN",
    "CRASHED",
]


def freight_route_digest_v2(route: tuple[int, ...]) -> str:
    """The canonical digest binding one ordered v2 route to a wire exchange.

    Python is the trust anchor: the digest is derived from the pinned
    witness and bound into the plan before any native run, and the
    GameScript only latches the carried values and refuses drift.
    """
    return hashlib.sha256(",".join(map(str, route)).encode()).hexdigest()


def freight_witness_digest_v2() -> str:
    """The canonical digest of the physical 31-tile construction witness."""
    return freight_route_digest_v2(PINNED_WITNESS)


def _cardinal_neighbours_v2(a: int, b: int) -> bool:
    return (
        abs(a % FREIGHT_MAP_WIDTH - b % FREIGHT_MAP_WIDTH)
        + abs(a // FREIGHT_MAP_WIDTH - b // FREIGHT_MAP_WIDTH)
        == 1
    )


def derive_freight_route_v2(witness: tuple[int, ...]) -> tuple[int, ...]:
    """Derive the 29-tile vehicle route from the pinned 31-tile witness (F-2).

    The physical witness is what the extension attempt actually built: it
    contains the stale D4 delivery bay (50351) and a backtracked repeat of
    its front tile (50095). A vehicle-legal stop-to-stop path removes both
    indices; the result is an ordered, unique, cardinal-contiguous path
    from the pickup stop to the new delivery bay.
    """
    if tuple(witness) != tuple(PINNED_WITNESS):
        raise ValueError("route derivation requires the pinned construction witness")
    if len(witness) != FREIGHT_WITNESS_LENGTH_V2:
        raise ValueError("the pinned witness must carry exactly 31 tiles")
    if (witness[23], witness[24]) != (
        FREIGHT_STALE_DELIVERY_TILE_V2,
        FREIGHT_STALE_BACKTRACK_TILE_V2,
    ):
        raise ValueError("the witness did not backtrack the stale D4 bay as recorded")
    route = witness[:23] + witness[25:]
    if len(route) != FREIGHT_ROUTE_LENGTH_V2:
        raise ValueError("the derived route must carry exactly 29 tiles")
    if len(set(route)) != len(route):
        raise ValueError("the derived route repeats a tile")
    if any(not 0 <= tile <= FREIGHT_MAX_TILE_ID for tile in route):
        raise ValueError("the derived route exceeds the map tile bound")
    if any(
        not _cardinal_neighbours_v2(a, b) for a, b in zip(route, route[1:], strict=False)
    ):
        raise ValueError("the derived route is not cardinally contiguous")
    if route[0] != A1_PICKUP_STOP_TILE_V2 or route[1] != A1_PICKUP_FRONT_TILE_V2:
        raise ValueError("the derived route must start at the pinned pickup stop")
    if route[-1] != A1_DELIVERY_STOP_TILE_V2 or route[-2] != A1_DELIVERY_FRONT_TILE_V2:
        raise ValueError("the derived route must end at the pinned delivery bay")
    if route[5] != A1_DEPOT_FRONT_TILE_V2:
        raise ValueError("the derived route must contain the pinned depot front")
    if A1_DEPOT_TILE_V2 in route:
        raise ValueError("the depot tile must not lie on the vehicle route")
    if not _cardinal_neighbours_v2(A1_DEPOT_TILE_V2, A1_DEPOT_FRONT_TILE_V2):
        raise ValueError("the depot front must be directly adjacent to the depot")
    if (
        len([tile for tile in route[1:-1] if _cardinal_neighbours_v2(tile, A1_DEPOT_TILE_V2)])
        != 1
    ):
        raise ValueError("the depot must touch exactly one route interior tile")
    return tuple(int(tile) for tile in route)


FREIGHT_ROUTE_V2 = derive_freight_route_v2(PINNED_WITNESS)
FREIGHT_ROUTE_DIGEST_V2 = freight_route_digest_v2(FREIGHT_ROUTE_V2)
_WITNESS_PAIR_TOTAL_V2 = len(PINNED_WITNESS) - 1
if not (
    _WITNESS_PAIR_TOTAL_V2 == 30
    and all(
        _cardinal_neighbours_v2(a, b)
        for a, b in zip(PINNED_WITNESS, PINNED_WITNESS[1:], strict=False)
    )
):
    raise RuntimeError("the pinned witness is not a cardinal-contiguous 31-tile path")


def _validate_freight_route_v2(route: tuple[int, ...]) -> None:
    """Validate one bounded v2 vehicle route (the same plan-side invariants)."""
    if not 3 <= len(route) <= MAX_FREIGHT_ROUTE_TILES_V2:
        raise ValueError(f"route must carry 3..{MAX_FREIGHT_ROUTE_TILES_V2} ordered tiles")
    if len(set(route)) != len(route):
        raise ValueError("route repeats a tile")
    if any(not 0 <= tile <= FREIGHT_MAX_TILE_ID for tile in route):
        raise ValueError("route tile exceeds the 256x256 map bound")
    if any(
        not _cardinal_neighbours_v2(a, b)
        for a, b in zip(route, route[1:], strict=False)
    ):
        raise ValueError("route tiles are not cardinally adjacent")
    if route[0] != A1_PICKUP_STOP_TILE_V2 or route[-1] != A1_DELIVERY_STOP_TILE_V2:
        raise ValueError("route endpoints must be the pinned pickup and delivery stops")
    if route[1] != A1_PICKUP_FRONT_TILE_V2 or route[-2] != A1_DELIVERY_FRONT_TILE_V2:
        raise ValueError("route fronts must be the pinned stop fronts")
    if A1_DEPOT_TILE_V2 in route:
        raise ValueError("depot must not lie on the route")
    fronts = [tile for tile in route[1:-1] if _cardinal_neighbours_v2(tile, A1_DEPOT_TILE_V2)]
    if fronts != [A1_DEPOT_FRONT_TILE_V2]:
        raise ValueError("depot must touch exactly one route interior tile: its pinned front")


class FreightRequestV2(Contract):
    """One protocol-8 freight exchange request (fixed correlation stride).

    Every request carries the full correlation stride — the v2 world pins,
    the uniform ``plan`` digest, and its op's echo fields (sentinel -1 or 0
    when unused) — so every readback is self-contained. The pinned engine
    request rides on every op except the site admission: engine-00 pins
    ``ENGINE_PIN_V2`` and the native handler admits it fail-closed instead
    of enumerating a lowest-compatible id.
    """

    protocol: Literal[8] = 8
    op: FreightOpV2
    request_id: Annotated[str, Field(pattern=r"^[a-z0-9-]{1,32}$")]
    plan: Digest
    company: CompanyID
    max_cost: Money
    pickup: TileID
    delivery: TileID
    depot: TileID
    route: tuple[TileID, ...] | None = None
    # Present on every exchange: the vehicle-route digest. The site request
    # also carries the physical-witness digest so the GameScript can latch
    # and echo it (Squirrel cannot re-hash; Python is the trust anchor).
    route_digest: Digest
    witness_digest: Digest | None = None
    engine: FreightActorIdV2 = -1
    vehicle: FreightActorIdV2 = -1
    expected_cost: Money = 0
    order_index: FreightOrderIndexV2 = -1
    watch_ticks: FreightWatchTicksV2 = -1
    watch_days: FreightWatchDaysV2 = -1

    @model_validator(mode="after")
    def coherent(self) -> FreightRequestV2:
        quiet = (
            self.expected_cost == 0
            and self.order_index == -1
            and self.watch_ticks == -1
            and self.watch_days == -1
        )
        pitched = self.engine >= 0 and self.vehicle >= 0
        if self.op == "site":
            if self.engine != -1 or self.vehicle != -1 or not quiet:
                raise ValueError("site requests carry no engine, vehicle or phase echoes")
            if self.route is None:
                raise ValueError("site request must carry the derived vehicle route")
            if self.witness_digest != freight_witness_digest_v2():
                raise ValueError("site request witness digest does not bind the witness")
            _validate_freight_route_v2(self.route)
            if self.route_digest != freight_route_digest_v2(self.route):
                raise ValueError("site request route digest does not bind its route")
        elif self.witness_digest is not None:
            raise ValueError("only the site request may carry a witness digest")
        elif self.route is not None:
            raise ValueError("only the site request may carry a route")
        if self.op == "site":
            return self
        if self.engine != ENGINE_PIN_V2:
            raise ValueError("every non-site request ships the provisional engine pin")
        if self.op == "engine":
            if self.vehicle != -1 or not quiet:
                raise ValueError("engine requests carry no vehicle or phase echoes")
        elif self.op == "purchase":
            if self.vehicle != -1:
                raise ValueError("purchase request must not name a vehicle")
            if self.order_index != -1 or self.watch_ticks != -1 or self.watch_days != -1:
                raise ValueError("purchase request must present no phase echoes")
            if not 0 < self.expected_cost <= self.max_cost:
                raise ValueError(
                    "purchase request needs its positive tested quote within the ceiling"
                )
        elif self.op == "vread":
            if not pitched or not quiet:
                raise ValueError("vehicle readback echoes the pinned engine and live vehicle")
        elif self.op == "order":
            if (
                not pitched
                or self.order_index not in (0, 1)
                or self.expected_cost != 0
                or self.watch_ticks != -1
                or self.watch_days != -1
            ):
                raise ValueError("order requests pin one stop index with no phase echoes")
        elif self.op in ("order-read", "monitor", "start", "finance", "finish"):
            if not pitched or not quiet:
                raise ValueError(f"{self.op} echoes the vehicle identity only")
        elif self.op == "load-watch":
            if not pitched or self.order_index != -1 or self.expected_cost != 0:
                raise ValueError("load-watch echoes the vehicle identity only")
            if self.watch_ticks < 1 or self.watch_days < 1:
                raise ValueError("load-watch presents its tick and day budget echoes")
        elif self.op in ("transit-watch", "deliver-watch"):
            if not pitched or self.order_index != -1 or self.expected_cost != 0:
                raise ValueError("window echoes the vehicle identity only")
            if self.watch_ticks < 1 or self.watch_days < 1:
                raise ValueError(
                    "window presents its tick and day budget echoes (E53: all "
                    "three watch windows lease the per-cycle day cap)"
                )
        else:  # pragma: no cover - FreightOpV2 excludes unknown ops
            raise ValueError("unknown freight op")
        return self

    def to_bytes(self) -> bytes:
        raw = canonical_bytes(self)
        if len(raw) > MAX_FREIGHT_REQUEST_BYTES_V2:
            raise ValueError(
                f"freight v2 request exceeds {MAX_FREIGHT_REQUEST_BYTES_V2} bytes"
            )
        return raw


_FREIGHT_FIELDS_V2 = (
    "paused",
    "truck0",
    "sid0",
    "truck1",
    "sid1",
    "depot_ok",
    "owner",
    "pairs_ok",
    "pair_total",
    "accept",
    "prod",
    "wait",
    "vehicles",
    "road_ready",
    "depot_edge",
    "pickup_radius",
    "delivery_radius",
    "pickup_industry",
    "pickup_industry_count",
    "delivery_industry",
    "delivery_industry_count",
    "available",
    "compatible",
    "capacity",
    "cargo",
    "price",
    "max_speed",
    "fleet",
    "fleet_count",
    "location",
    "state",
    "in_depot",
    "speed",
    "dest",
    "flags",
    "goto",
    "order_len",
    "dest0",
    "flags0",
    "goto0",
    "dest1",
    "flags1",
    "goto1",
    "pickup_amount",
    "delivery_amount",
    "recheck",
    "income",
    "delivered",
    "load",
    "position",
    "progress",
    "tick",
    "day",
    "last_accepted",
    "stop_issued",
)

_FREIGHT_SUBSETS_V2: dict[FreightOpV2, frozenset[str]] = {
    "site": frozenset(
        (
            "paused",
            "truck0",
            "sid0",
            "truck1",
            "sid1",
            "depot_ok",
            "owner",
            "pairs_ok",
            "pair_total",
            "accept",
            "prod",
            "wait",
            "vehicles",
            "road_ready",
            "depot_edge",
            "pickup_radius",
            "delivery_radius",
            "pickup_industry",
            "pickup_industry_count",
            "delivery_industry",
            "delivery_industry_count",
            "income",
        )
    ),
    "engine": frozenset(
        (
            "available",
            "compatible",
            "capacity",
            "cargo",
            "price",
            "max_speed",
            "fleet",
            "fleet_count",
            "income",
        )
    ),
    "purchase": frozenset(("income",)),
    "vread": frozenset(
        ("owner", "location", "capacity", "cargo", "state", "in_depot", "speed", "income")
    ),
    "order": frozenset(("dest", "flags", "goto", "income")),
    "order-read": frozenset(
        ("order_len", "dest0", "flags0", "goto0", "dest1", "flags1", "goto1", "income")
    ),
    "monitor": frozenset(
        ("pickup_amount", "delivery_amount", "income", "delivered")
    ),
    "start": frozenset(("state", "speed", "day", "income")),
    "load-watch": frozenset(
        ("load", "capacity", "wait", "pickup_amount", "tick", "day", "paused", "income")
    ),
    "transit-watch": frozenset(
        ("position", "progress", "load", "tick", "day", "paused", "income")
    ),
    "deliver-watch": frozenset(
        (
            "load",
            "position",
            "pickup_amount",
            "delivery_amount",
            "recheck",
            "tick",
            "day",
            "paused",
            "income",
        )
    ),
    "finance": frozenset(("income", "delivered", "last_accepted")),
    "finish": frozenset(("state", "speed", "in_depot", "stop_issued", "income")),
}
_FREIGHT_WATCH_OPS_V2 = ("load-watch", "transit-watch", "deliver-watch")
_FREIGHT_POST_PURCHASE_OPS_V2 = (
    "vread",
    "order",
    "order-read",
    "monitor",
    "start",
    *_FREIGHT_WATCH_OPS_V2,
    "finance",
    "finish",
)


class FreightReadbackV2(Contract):
    """One protocol-8 freight exchange response (strict per-op field subsets).

    The handler echoes the request correlation keys, ``funds``, its op's
    quarter income (the F-6 ledger basis every exchange span attributes)
    and a status literal, and reports only the observation set of its op:
    success frames carry the complete op subset, inconclusive and typed
    zero-departure frames may carry any subset, and refusal frames carry
    none (a spoofed hybrid is refused on the wire).
    """

    protocol: Literal[8] = 8
    op: FreightOpV2
    request_id: str
    plan: Digest
    company: CompanyID
    max_cost: Money
    pickup: TileID
    delivery: TileID
    depot: TileID
    route_digest: Digest
    witness_digest: Digest | None = None
    engine: FreightActorIdV2 = -1
    vehicle: FreightActorIdV2 = -1
    expected_cost: Money = 0
    order_index: FreightOrderIndexV2 = -1
    watch_ticks: FreightWatchTicksV2 = -1
    watch_days: FreightWatchDaysV2 = -1
    status: FreightStatusV2
    funds: SignedMoney
    cost: Money

    paused: StrictBool | None = None
    # Site admission observations. The industry ids are the natively
    # discovered unique cargo-accepting/producing identities (F-3): never
    # pinned, latched at site admission only.
    truck0: StrictBool | None = None
    sid0: StationID | None = None
    truck1: StrictBool | None = None
    sid1: StationID | None = None
    depot_ok: StrictBool | None = None
    owner: OwnerID | None = None
    pairs_ok: FreightPairCountV2 | None = None
    pair_total: FreightPairCountV2 | None = None
    accept: FreightEighthsV2 | None = None
    prod: FreightAmountV2 | None = None
    wait: FreightAmountV2 | None = None
    vehicles: FreightAmountV2 | None = None
    road_ready: StrictBool | None = None
    depot_edge: StrictBool | None = None
    pickup_radius: FreightRadiusV2 | None = None
    delivery_radius: FreightRadiusV2 | None = None
    pickup_industry: FreightIndustryV2 | None = None
    pickup_industry_count: FreightIndustryCountV2 | None = None
    delivery_industry: FreightIndustryV2 | None = None
    delivery_industry_count: FreightIndustryCountV2 | None = None
    # Engine admission observations: the pinned engine identity and its
    # F-10 fail-closed census facts, plus the bounded compatible-universe
    # echo (buildable road engine ids, descending, wire-capped).
    available: StrictBool | None = None
    compatible: StrictBool | None = None
    capacity: FreightAmountV2 | None = None
    cargo: FreightCargoV2 | None = None
    price: Money | None = None
    max_speed: FreightAmountV2 | None = None
    fleet: FreightFleetV2 | None = None
    fleet_count: FreightAmountV2 | None = None
    # Vehicle readback observations.
    location: TileID | None = None
    state: FreightVehicleStateV2 | None = None
    in_depot: StrictBool | None = None
    speed: FreightAmountV2 | None = None
    # Order observations: destinations are stop TILES (N1: the 15.x append
    # takes the tile, the order storage stays per-station and readbacks
    # echo the resolved station stop tile), flags carry real 15.x values.
    dest: TileID | None = None
    flags: FreightFlagsV2 | None = None
    goto: StrictBool | None = None
    order_len: FreightPodV2 | None = None
    dest0: TileID | None = None
    flags0: FreightFlagsV2 | None = None
    goto0: StrictBool | None = None
    dest1: TileID | None = None
    flags1: FreightFlagsV2 | None = None
    goto1: StrictBool | None = None
    # Monitor observations.
    pickup_amount: FreightAmountV2 | None = None
    delivery_amount: FreightAmountV2 | None = None
    recheck: StrictBool | None = None
    # Quarter income of record (F-6): every op echoes it, so each exchange
    # span attributes its income delta exactly.
    income: SignedMoney | None = None
    delivered: FreightAmountV2 | None = None
    # Window observations.
    load: FreightAmountV2 | None = None
    position: TileID | None = None
    progress: FreightProgressV2 | None = None
    tick: FreightAmountV2 | None = None
    day: FreightAmountV2 | None = None
    last_accepted: FreightDateV2 | None = None
    # Finish facts.
    stop_issued: StrictBool | None = None

    @property
    def digest(self) -> str:
        return hashlib.sha256(canonical_bytes(self)).hexdigest()

    @model_validator(mode="after")
    def coherent(self) -> FreightReadbackV2:
        if self.op not in _FREIGHT_SUCCESS_STATUS_V2:
            raise ValueError("unknown freight op")
        subset = _FREIGHT_SUBSETS_V2[self.op]
        present = set()
        for field in _FREIGHT_FIELDS_V2:
            if getattr(self, field) is not None:
                present.add(field)
        outside = present - subset
        if outside:
            raise ValueError(
                f"{self.op} readback carries fields outside its subset: {sorted(outside)}"
            )
        success = self.status == _FREIGHT_SUCCESS_STATUS_V2[self.op]
        if success:
            missing = subset - present
            if missing:
                raise ValueError(f"{self.op} success readback lacks {sorted(missing)}")
        elif self.status not in _FREIGHT_REPORTED_STATUS_V2:  # pragma: no cover
            raise ValueError("unknown freight status")
        elif (
            self.status not in _FREIGHT_INCONCLUSIVE_STATUS_V2
            and self.status not in _FREIGHT_ZERO_STATUS_V2
            and present
        ):
            raise ValueError("refusal readback carries an unclaimed observation set")
        # Echo coherence by op position in the attempt:
        if self.op == "site":
            if self.engine != -1 or self.vehicle != -1:
                raise ValueError("site readback must not name an engine or vehicle")
        elif self.op == "engine":
            if self.vehicle != -1:
                raise ValueError("engine readback must not name a vehicle")
            if success and self.engine != ENGINE_PIN_V2:
                raise ValueError("engine readback must name the pinned engine")
        elif self.op == "purchase":
            if self.order_index != -1 or self.watch_ticks != -1 or self.watch_days != -1:
                raise ValueError("purchase readback must not carry phase echoes")
            if success and (self.engine != ENGINE_PIN_V2 or self.vehicle < 0):
                raise ValueError("built purchase must name the pinned engine and vehicle")
            if (
                not success
                and self.status in _FREIGHT_REFUSAL_STATUS_V2
                and self.vehicle != -1
            ):
                raise ValueError("refused purchase must not name a vehicle")
        elif self.op in _FREIGHT_POST_PURCHASE_OPS_V2:
            if self.engine != ENGINE_PIN_V2 or self.vehicle < 0:
                raise ValueError("post-purchase readbacks echo the pinned engine and vehicle")
        if self.op != "order" and self.order_index != -1:
            raise ValueError("order echoes carry stop indexes")
        if self.op not in _FREIGHT_WATCH_OPS_V2 and self.watch_ticks != -1:
            raise ValueError("watch echoes belong to window exchanges")
        if self.op not in _FREIGHT_WATCH_OPS_V2 and self.watch_days != -1:
            raise ValueError("day budgets belong to watch windows")
        if success and self.op in _FREIGHT_WATCH_OPS_V2:
            if self.watch_ticks < 1:
                raise ValueError("window success must echo its tick budget")
            if self.watch_days < 1:
                raise ValueError(
                    "window success must echo its day budget (E53: every "
                    "watch window leases the per-cycle day cap)"
                )
        return self

    @classmethod
    def parse_for(cls, request: FreightRequestV2, raw: bytes):
        if len(raw) > MAX_FREIGHT_RESPONSE_BYTES_V2:
            raise ValueError(
                f"application response exceeds {MAX_FREIGHT_RESPONSE_BYTES_V2} bytes"
            )

        def unique(pairs):
            result = {}
            for key, value in pairs:
                if key in result:
                    raise ValueError("duplicate response key")
                result[key] = value
            return result

        value = json.loads(raw, object_pairs_hook=unique)
        # Python-mode strict validation rejects lists for the echo's only
        # tuple field, while JSON mode accepts wire arrays: lift the fleet
        # array to its tuple (element-wise StrictInt bounds still apply).
        if isinstance(value, dict) and isinstance(value.get("fleet"), list):
            value["fleet"] = tuple(value["fleet"])
        criteria = cls.model_validate(value)
        correlated = ("protocol", "op", "request_id", "plan", "company", "max_cost")
        if any(getattr(criteria, k) != getattr(request, k) for k in correlated):
            raise ValueError("freight response correlation mismatch")
        for key in ("pickup", "delivery", "depot", "route_digest"):
            if getattr(criteria, key) != getattr(request, key):
                raise ValueError("freight response pin mismatch")
        if (
            request.witness_digest is not None
            and criteria.witness_digest != request.witness_digest
        ):
            raise ValueError("freight response witness-digest mismatch")
        if request.witness_digest is None and criteria.witness_digest is not None:
            raise ValueError("freight response carries an unclaimed witness digest")
        for key in ("engine", "vehicle", "order_index", "watch_ticks", "watch_days"):
            expected = getattr(request, key)
            if expected >= 0 and getattr(criteria, key) != expected:
                raise ValueError("freight response echo mismatch")
        if request.expected_cost > 0 and criteria.expected_cost != request.expected_cost:
            raise ValueError("freight response quote-echo mismatch")
        return criteria


def _adjacent_v2(a: int, b: int) -> bool:
    return _cardinal_neighbours_v2(a, b)


class FreightPlanV2(Contract):
    """The geometry, identities and schedule of one v2 attempt.

    Schema 1 binds the A1 close-out geometry: the physical 31-tile
    construction witness verbatim, the 29-tile vehicle route derived from
    it, the new delivery bay 50862 (station 2), the company depot 45487
    with its single adjacent front 45743, and the A1 close-out funds
    £490,257. The delivery and pickup industry ids are NEVER pinned (F-3):
    they are discovered natively and latched at site admission. The
    pinned engine is the provisional census pin (F-1/F-10 Option B). The
    schedule of record is the cycle-looped thirty-exchange plan fixed by
    the request arithmetic at staging (6 cycles max).
    """

    schema_version: Literal[1] = 1
    schedule_version: Literal[2] = 2
    attempt: Annotated[str, Field(pattern=r"^D5-FREIGHT-[0-9]{1,8}$")]
    company: CompanyID
    cargo: FreightCargoV2
    engine: FreightActorIdV2
    pickup: TileID
    pickup_front: TileID
    delivery: TileID
    delivery_front: TileID
    depot: TileID
    depot_front: TileID
    pickup_industry: FreightIndustryV2
    delivery_industry: FreightIndustryV2
    expected_funds: Money
    max_cost: Money
    witness: tuple[TileID, ...]
    vehicle_route: tuple[TileID, ...]
    schedule: tuple[str, ...]
    cycles: Annotated[StrictInt, Field(gt=0, le=FREIGHT_REQUEST_BUDGET_V2)]
    day_budget: Annotated[StrictInt, Field(gt=0, le=65535)]
    cycle_day_cap: Annotated[StrictInt, Field(gt=0, le=65535)]
    request_budget: Annotated[StrictInt, Field(gt=0, le=FREIGHT_REQUEST_BUDGET_V2)] = (
        FREIGHT_REQUEST_BUDGET_V2
    )

    @property
    def digest(self) -> str:
        return hashlib.sha256(canonical_bytes(self)).hexdigest()

    @property
    def route_digest(self) -> str:
        """The wire binding every exchange must present for this plan."""
        return freight_route_digest_v2(self.vehicle_route)

    @property
    def witness_digest(self) -> str:
        """The physical construction-witness binding (separate from route)."""
        return freight_route_digest_v2(self.witness)

    @model_validator(mode="after")
    def coherent(self) -> FreightPlanV2:
        if self.company != FREIGHT_COMPANY or self.cargo != FREIGHT_CARGO_ID:
            raise ValueError("the freight v2 plan drives company 0 with cargo 1")
        if self.attempt != FREIGHT_ATTEMPT_V2:
            raise ValueError("the v2 attempt name is fixed of record")
        if self.engine != ENGINE_PIN_V2:
            raise ValueError("the plan binds the provisional engine pin exactly")
        if self.witness != tuple(PINNED_WITNESS):
            raise ValueError("the plan binds the pinned 31-tile construction witness")
        derived = derive_freight_route_v2(PINNED_WITNESS)
        if self.vehicle_route != derived:
            raise ValueError("the vehicle route must be derived from the pinned witness")
        _validate_freight_route_v2(self.vehicle_route)
        if (self.pickup, self.pickup_front) != (
            A1_PICKUP_STOP_TILE_V2,
            A1_PICKUP_FRONT_TILE_V2,
        ):
            raise ValueError("pickup pins drifted from the A1 corridor stops")
        if (self.delivery, self.delivery_front) != (
            A1_DELIVERY_STOP_TILE_V2,
            A1_DELIVERY_FRONT_TILE_V2,
        ):
            raise ValueError("delivery pins drifted from the A1 close-out bay")
        if (self.depot, self.depot_front) != (A1_DEPOT_TILE_V2, A1_DEPOT_FRONT_TILE_V2):
            raise ValueError("depot pins drifted from the A1 corridor depot")
        for pin, front in (
            (self.pickup, self.pickup_front),
            (self.delivery, self.delivery_front),
            (self.depot, self.depot_front),
        ):
            if not _adjacent_v2(pin, front):
                raise ValueError("each stop pins a directly adjacent front")
        if self.pickup_industry != -1 or self.delivery_industry != -1:
            raise ValueError("industry ids are discovered natively and never pinned")
        if self.expected_funds != FUNDS_AT_A1_CLOSE:
            raise ValueError("the plan binds the A1 close-out funds exactly")
        if self.max_cost != FREIGHT_MAX_COST_V2:
            raise ValueError("the plan binds the v2 per-op cost ceiling exactly")
        if self.cycles != PLANNED_FREIGHT_CYCLES_V2:
            raise ValueError("the planned cycle count comes from the staging arithmetic")
        if self.day_budget != FREIGHT_DAY_BUDGET_V2:
            raise ValueError("the plan binds the per-attempt day budget exactly")
        if self.cycle_day_cap != FREIGHT_CYCLE_DAY_CAP_V2:
            raise ValueError("the cycle day lease is the budget split across cycles")
        if self.schedule != freight_exchange_ids_v2(self.cycles):
            raise ValueError("schedule drifted from the planned v2 exchanges")
        return self


class FreightSiteIntentV2(Contract):
    """Latched v2 site admission facts from one fresh native READY readback."""

    schema_version: Literal[1] = 1
    prelaunch_digest: Digest
    plan_digest: Digest
    company: CompanyID
    cargo: FreightCargoV2
    pickup: TileID
    pickup_sid: StationID
    delivery: TileID
    delivery_sid: StationID
    depot: TileID
    depot_edge: StrictBool
    accept: FreightEighthsV2
    pickup_radius: FreightRadiusV2
    delivery_radius: FreightRadiusV2
    pickup_industry: FreightIndustryV2
    delivery_industry: FreightIndustryV2
    production: FreightAmountV2
    waiting: FreightAmountV2
    funds: Money
    before_digest: Digest

    @property
    def digest(self) -> str:
        return hashlib.sha256(canonical_bytes(self)).hexdigest()


class FreightEngineIntentV2(Contract):
    """Latched engine admission: the pinned truck at its census-tested quote."""

    schema_version: Literal[1] = 1
    prelaunch_digest: Digest
    site_digest: Digest
    company: CompanyID
    cargo: FreightCargoV2
    engine: FreightActorIdV2
    provisional: StrictBool
    capacity: FreightAmountV2
    price: Money
    max_speed: FreightAmountV2
    fleet: FreightFleetV2
    fleet_count: FreightAmountV2
    quote: Money
    before_digest: Digest

    @property
    def digest(self) -> str:
        return hashlib.sha256(canonical_bytes(self)).hexdigest()


def admit_freight_site_v2(
    readback: FreightReadbackV2, *, prelaunch_digest: str, plan: FreightPlanV2
) -> FreightSiteIntentV2:
    """Latch the v2 site admission facts from a fresh native READY readback.

    Requires: the world unpaused and on the company road, both stops valid
    truck-stop-typed stations, the depot owned with its directed front-to-
    depot edge proven (F-12), the vehicle route fully re-connected
    direction-by-direction (F-5's directed checks), full 8/8 cargo
    acceptance at the delivery bay (the pinned census bound), exactly one
    cargo-producing industry in the pickup stop's stop-radius and exactly
    one cargo-accepting industry in the delivery bay's stop-radius (the
    F-3 unique-cargo-industry discovery — ids latched here, never pinned),
    the A1 close-out funds exactly, and zero pre-existing vehicles.
    """
    if (
        readback.op != "site"
        or readback.status != "READY"
        or readback.plan != prelaunch_digest
        or readback.company != plan.company
        or readback.cost != 0
        or readback.route_digest != plan.route_digest
        or readback.witness_digest != plan.witness_digest
    ):
        raise ValueError("site admission requires a correlated READY observation at zero cost")
    if (readback.pickup, readback.delivery, readback.depot) != (
        plan.pickup,
        plan.delivery,
        plan.depot,
    ):
        raise ValueError("site pins drifted from the planned corridor")
    if readback.paused is not False:
        raise ValueError("site admission requires an unpaused world")
    if readback.funds != plan.expected_funds:
        raise ValueError("site funds must equal the A1 close-out level exactly")
    if readback.vehicles is None or readback.vehicles != 0:
        raise ValueError("site admission requires a company with zero vehicles")
    if readback.road_ready is not True:
        raise ValueError("the site readback must confirm the current road type")
    if (
        readback.truck0 is not True
        or readback.truck1 is not True
        or readback.sid0 is None
        or readback.sid0 < 0
        or readback.sid1 is None
        or readback.sid1 < 0
    ):
        raise ValueError("both corridor stops must be valid truck-stop-typed stations")
    if readback.depot_ok is not True or readback.owner != plan.company:
        raise ValueError("the corridor depot must be company-owned")
    if readback.depot_edge is not True:
        raise ValueError("the directed front-to-depot road edge must be present (F-12)")
    if (
        readback.pairs_ok is None
        or readback.pair_total is None
        or readback.pairs_ok != readback.pair_total
        or readback.pairs_ok != len(plan.vehicle_route) - 1
    ):
        raise ValueError("the vehicle route must re-check fully connected on native road")
    if readback.accept is None or readback.accept != 8:
        raise ValueError("delivery acceptance must read the pinned full 8/8 census bound")
    if (
        readback.pickup_radius is None
        or readback.pickup_radius < 1
        or readback.delivery_radius is None
        or readback.delivery_radius < 1
    ):
        raise ValueError("both stops must expose a positive station catchment radius")
    if (
        readback.pickup_industry is None
        or readback.pickup_industry < 0
        or readback.delivery_industry is None
        or readback.delivery_industry < 0
    ):
        raise ValueError("the unique cargo industries must be discovered before orders")
    if readback.pickup_industry == readback.delivery_industry:
        raise ValueError("the pickup and delivery industry identities must stay distinct")
    if (
        readback.pickup_industry_count is None
        or readback.pickup_industry_count != 1
        or readback.delivery_industry_count is None
        or readback.delivery_industry_count != 1
    ):
        # F-3 unique-cargo-industry discovery: counts must be exactly one, and
        # the GameScript discovery enforces the same gate before any READY —
        # so a readback claiming zero or several candidates is a defect, not a
        # downgrade.
        raise ValueError(
            "the industry discovery must observe exactly one cargo industry per stop"
        )
    return FreightSiteIntentV2(
        prelaunch_digest=prelaunch_digest,
        plan_digest=plan.digest,
        company=readback.company,
        cargo=plan.cargo,
        pickup=readback.pickup,
        pickup_sid=readback.sid0,
        delivery=readback.delivery,
        delivery_sid=readback.sid1,
        depot=readback.depot,
        depot_edge=readback.depot_edge,
        accept=readback.accept,
        pickup_radius=readback.pickup_radius,
        delivery_radius=readback.delivery_radius,
        pickup_industry=readback.pickup_industry,
        delivery_industry=readback.delivery_industry,
        production=readback.prod,
        waiting=readback.wait,
        funds=readback.funds,
        before_digest=readback.digest,
    )


def admit_freight_engine_v2(
    readback: FreightReadbackV2,
    *,
    prelaunch_digest: str,
    plan: FreightPlanV2,
    site: FreightSiteIntentV2,
) -> FreightEngineIntentV2:
    """Latch the pinned engine admission under the F-10 fail-closed policy.

    The request engine pin is the identity; the native readback refused
    NO_ENGINE / UNAVAILABLE_ENGINE / ENGINE_PIN_MISMATCH before this
    latching call. A successful READY readback must present the pinned
    engine id with a buildable road-to-cargo identity whose census facts
    (price, capacity, cargo) match the provisional pin exactly.
    """
    if (
        readback.op != "engine"
        or readback.status != "READY"
        or readback.plan != prelaunch_digest
        or readback.company != plan.company
        or readback.vehicle != -1
        or readback.engine != plan.engine
    ):
        raise ValueError("engine admission requires a correlated READY enumeration of the pin")
    if (
        readback.available is not True
        or readback.compatible is not True
        or readback.capacity is None
        or readback.capacity != ENGINE_CENSUS_V2["capacity"]
    ):
        raise ValueError("the admitted engine must match the census capacity")
    if readback.cargo is None or readback.cargo != ENGINE_CENSUS_V2["cargo"]:
        raise ValueError("the admitted engine must run the census cargo")
    if (
        readback.price is None
        or readback.price != ENGINE_CENSUS_V2["price"]
        or readback.max_speed is None
        or readback.max_speed != ENGINE_CENSUS_V2["max_speed"]
    ):
        raise ValueError("the admitted engine must match the census price and speed")
    if readback.fleet is None or readback.fleet_count is None:
        raise ValueError("the engine readback must echo its compatible universe")
    if readback.engine not in readback.fleet:
        raise ValueError("the pinned engine must appear in the echoed compatible universe")
    if not 0 < readback.cost <= min(plan.max_cost, readback.funds):
        raise ValueError("engine admission requires a positive affordable tested quote")
    if readback.funds != site.funds:
        raise ValueError("engine exchange funds drifted from the admitted site")
    return FreightEngineIntentV2(
        prelaunch_digest=prelaunch_digest,
        site_digest=site.digest,
        company=readback.company,
        cargo=readback.cargo,
        engine=readback.engine,
        provisional=ENGINE_PIN_PROVISIONAL_V2,
        capacity=readback.capacity,
        price=readback.price,
        max_speed=readback.max_speed,
        fleet=readback.fleet,
        fleet_count=readback.fleet_count,
        quote=readback.cost,
        before_digest=readback.digest,
    )


def verify_freight_purchase_built_v2(
    intent: FreightEngineIntentV2, before: FreightReadbackV2, built: FreightReadbackV2
) -> dict:
    """Verify the pinned-engine purchase execution result and emit its basis receipt."""
    if (
        built.op != "purchase"
        or built.status != "BUILT"
        or (
            built.plan,
            built.company,
        )
        != (intent.prelaunch_digest, intent.company)
    ):
        raise ValueError("purchase execution result correlation mismatch")
    if built.engine != intent.engine or built.vehicle < 0:
        raise ValueError("purchase result must name the pinned engine and one new vehicle")
    if built.cost != intent.quote:
        raise ValueError("purchase realized cost changed from the tested quote")
    if before.funds - built.funds != built.cost:
        raise ValueError("purchase funds must move by exactly the recorded quote")
    return dict(
        schema="company-freight2-purchase-basis-receipt-v1",
        request_id=built.request_id,
        prelaunch_digest=intent.prelaunch_digest,
        before_digest=intent.before_digest,
        built_digest=built.digest,
        company=intent.company,
        engine=intent.engine,
        engine_provisional=intent.provisional,
        vehicle=built.vehicle,
        quote=intent.quote,
        cost=built.cost,
        funds=dict(before=before.funds, after=built.funds),
        verification="NATIVE_STATE_CHANGED",
    )


def verify_freight_purchase_v2(
    intent: FreightEngineIntentV2,
    before: FreightReadbackV2,
    built: FreightReadbackV2,
    independent: FreightReadbackV2,
    *,
    plan: FreightPlanV2,
) -> dict:
    """Verify the purchase group: quote, purchase and independent read."""
    verify_freight_purchase_built_v2(intent, before, built)
    if (
        independent.op != "vread"
        or independent.status != "READ"
        or (
            independent.plan,
            independent.company,
        )
        != (intent.prelaunch_digest, intent.company)
    ):
        raise ValueError("independent vehicle readback correlation mismatch")
    if (independent.engine, independent.vehicle) != (intent.engine, built.vehicle):
        raise ValueError("independent readback identity mismatch")
    if (independent.owner, independent.capacity, independent.cargo) != (
        plan.company,
        intent.capacity,
        intent.cargo,
    ):
        raise ValueError("independent readback capacity or cargo mismatch")
    if (
        independent.state != "IN_DEPOT"
        or independent.in_depot is not True
        or independent.location != plan.depot
        or independent.speed != 0
    ):
        raise ValueError("purchased vehicle must be stopped in the pinned depot")
    if independent.cost != 0 or independent.funds != built.funds:
        raise ValueError("independent readback spending or funds mismatch")
    return dict(
        schema="company-freight2-purchase-receipt-v1",
        execution_request_id=built.request_id,
        readback_request_id=independent.request_id,
        plan_digest=plan.digest,
        before_digest=intent.before_digest,
        built_digest=built.digest,
        after_digest=independent.digest,
        company=plan.company,
        engine=intent.engine,
        engine_provisional=intent.provisional,
        vehicle=built.vehicle,
        cargo=intent.cargo,
        capacity=intent.capacity,
        quote=intent.quote,
        cost=built.cost,
        error_code=None,
        funds=dict(before=before.funds, after=built.funds),
        verification="NATIVE_STATE_CHANGED",
    )


def verify_freight_order_v2(
    read: FreightReadbackV2, *, index: int, vehicle: int, plan: FreightPlanV2
) -> dict:
    """Verify one appended stop order (N1/N2: tile destinations, v2 flags).

    Destination ids are stop TILES: the pickup stop tile for order 0
    (flags OF_NONE) and pinned delivery bay tile for order 1 (flags
    OF_NO_LOAD). Destination tiles resolve to their stations natively; the
    readback echoes the tile the append actually carried.
    """
    if read.op != "order" or read.status != "ORDERED" or read.cost != 0:
        raise ValueError("order append result mismatch")
    if read.engine != ENGINE_PIN_V2 or read.vehicle != vehicle:
        raise ValueError("order append echo mismatch")
    if read.order_index != index:
        raise ValueError("order append index mismatch")
    expected_dest = plan.pickup if index == 0 else plan.delivery
    expected_flags = OF_NONE_V2 if index == 0 else OF_NO_LOAD_V2
    if read.dest is None or read.dest != expected_dest:
        raise ValueError("order destination must be the pinned stop tile (N1)")
    if read.flags is None or read.flags != expected_flags:
        raise ValueError("order flags drifted from the v2 load policy (N2)")
    if read.goto is not True:
        raise ValueError("orders must goto-station")
    return dict(
        schema="company-freight2-order-receipt-v1",
        request_id=read.request_id,
        stop="pickup" if index == 0 else "delivery",
        order_index=index,
        dest=read.dest,
        dest_kind="stop_tile",
        flags=read.flags,
        goto=True,
        funds=read.funds,
        verification="NATIVE_STATE_CHANGED",
    )


def verify_freight_order_set_v2(
    appends: tuple[FreightReadbackV2, FreightReadbackV2],
    inventory: FreightReadbackV2,
    *,
    vehicle: int,
    plan: FreightPlanV2,
) -> dict:
    """Verify the exact two-order inventory over both recorded appends."""
    for index, append in enumerate(appends):
        verify_freight_order_v2(
            append, index=index, vehicle=vehicle, plan=plan
        )
    if (
        inventory.op != "order-read"
        or inventory.status != "ORDER_SET_VERIFIED"
        or inventory.cost != 0
    ):
        raise ValueError("order inventory mismatch")
    if inventory.vehicle != vehicle or inventory.order_len != 2:
        raise ValueError("the v2 order set carries exactly two orders")
    triples = (
        (inventory.dest0, inventory.flags0, inventory.goto0),
        (inventory.dest1, inventory.flags1, inventory.goto1),
    )
    if triples != (
        (plan.pickup, OF_NONE_V2, True),
        (plan.delivery, OF_NO_LOAD_V2, True),
    ):
        raise ValueError("order set drifted from the planned v2 inventory")
    return dict(
        schema="company-freight2-order-set-receipt-v1",
        request_id=inventory.request_id,
        append_request_ids=(appends[0].request_id, appends[1].request_id),
        orders=(
            dict(stop="pickup", dest=plan.pickup, flags=OF_NONE_V2, goto=True),
            dict(stop="delivery", dest=plan.delivery, flags=OF_NO_LOAD_V2, goto=True),
        ),
        funds=inventory.funds,
        verification="NATIVE_ORDER_SET_VERIFIED",
    )


def verify_freight_monitors_v2(armed: FreightReadbackV2, *, vehicle: int) -> dict:
    """Verify the pre-start monitor arming; both baselines must be zero."""
    if armed.op != "monitor" or armed.status != "ARMED" or armed.cost != 0:
        raise ValueError("monitor arming result mismatch")
    if armed.engine != ENGINE_PIN_V2 or armed.vehicle != vehicle:
        raise ValueError("monitor arming echo mismatch")
    if armed.pickup_amount != 0 or armed.delivery_amount != 0:
        raise ValueError("NONZERO_MONITOR_BASELINE")
    return dict(
        schema="company-freight2-monitor-receipt-v1",
        request_id=armed.request_id,
        pickup_baseline=armed.pickup_amount,
        delivery_baseline=armed.delivery_amount,
        income_baseline=armed.income,
        delivered_baseline=armed.delivered,
        funds=armed.funds,
        verification="NATIVE_MONITOR_ARMED",
    )


def verify_freight_start_v2(started: FreightReadbackV2, *, vehicle: int) -> dict:
    """Verify the started vehicle readback."""
    if started.op != "start" or started.status != "STARTED" or started.cost != 0:
        raise ValueError("start result mismatch")
    if started.engine != ENGINE_PIN_V2 or started.vehicle != vehicle:
        raise ValueError("start readback echo mismatch")
    if started.state != "RUNNING":
        raise ValueError("started vehicle must be natively running")
    return dict(
        schema="company-freight2-start-receipt-v1",
        request_id=started.request_id,
        funds=started.funds,
        verification="NATIVE_STATE_CHANGED",
    )


def verify_freight_started_v2(
    started: FreightReadbackV2,
    independent: FreightReadbackV2,
    *,
    engine: FreightEngineIntentV2,
    vehicle: int,
) -> dict:
    """Verify the started group including its independent post-start read."""
    verify_freight_start_v2(started, vehicle=vehicle)
    if independent.op != "vread" or independent.status != "READ" or independent.cost != 0:
        raise ValueError("independent started readback mismatch")
    if (independent.engine, independent.vehicle) != (engine.engine, vehicle):
        raise ValueError("independent started readback identity mismatch")
    if (
        independent.owner != engine.company
        or independent.state not in ("RUNNING", "AT_STATION")
        or independent.in_depot is not False
    ):
        raise ValueError("the started vehicle must be away from the depot")
    if independent.capacity != engine.capacity or independent.cargo != engine.cargo:
        raise ValueError("independent started readback capacity or cargo mismatch")
    return dict(
        schema="company-freight2-started-receipt-v1",
        execution_request_id=started.request_id,
        readback_request_id=independent.request_id,
        built_digest=started.digest,
        after_digest=independent.digest,
        funds=dict(before=started.funds, after=independent.funds),
        location=independent.location,
        verification="NATIVE_STATE_CHANGED",
    )


def verify_freight_loaded_v2(
    loaded: FreightReadbackV2,
    *,
    vehicle: int,
    engine: FreightEngineIntentV2,
    waiting_baseline: int,
) -> dict:
    """Verify the load-watch window result: the verified departure snapshot.

    The departure gate is the partial-load gate of record: the observed
    departure load must satisfy ``0 < load <= capacity`` — full-load is
    never demanded — and it is typed only when the window proves an actual
    departure (sampled pickup visit, then an on-route reading past the
    stop, E53). The departure sample must also carry its matching pickup
    monitor evidence: the industry monitor's own reading equals the truck
    load, so a first positive cargo atom never stands for a snapshot. The
    waiting delta against the admitted site baseline is recorded as
    observational corroboration only (unbounded industry arrivals can mask
    the decrement, so the delta is evidence, not a gate); the same honesty
    statement protocol 5 recorded stays in force.
    """
    if loaded.op != "load-watch" or loaded.status != "LOADED" or loaded.cost != 0:
        raise ValueError("load window result mismatch")
    if loaded.engine != ENGINE_PIN_V2 or loaded.vehicle != vehicle:
        raise ValueError("load echo mismatch")
    if loaded.capacity != engine.capacity:
        raise ValueError("load echo capacity mismatch")
    if loaded.load is None or not 0 < loaded.load <= loaded.capacity:
        raise ValueError("the observed load must satisfy 0 < load <= capacity")
    if loaded.wait is None:
        raise ValueError("the loaded readback must record its station waiting level")
    if loaded.pickup_amount is None or loaded.pickup_amount != loaded.load:
        raise ValueError(
            "the departure snapshot must carry its matching pickup monitor "
            "evidence (E53)"
        )
    waiting_delta = loaded.wait - waiting_baseline
    return dict(
        schema="company-freight2-loaded-receipt-v1",
        request_id=loaded.request_id,
        load=loaded.load,
        capacity=loaded.capacity,
        pickup_amount=loaded.pickup_amount,
        partial=loaded.load < loaded.capacity,
        waiting=loaded.wait,
        waiting_delta=waiting_delta,
        # Unbounded industry arrivals can mask the decrement: recorded
        # evidence, not an enforced gate.
        waiting_note="station arrivals unbounded; waiting delta recorded, not enforced",
        watch_ticks=loaded.watch_ticks,
        watch_days=loaded.watch_days,
        tick=loaded.tick,
        day=loaded.day,
        funds=loaded.funds,
        verification="NATIVE_LOAD_VERIFIED",
    )


def verify_freight_zero_departed_v2(zero: FreightReadbackV2, *, vehicle: int) -> dict:
    """Verify a typed zero-departure cycle event (F-11).

    The load watch observed a verified departure with no cargo load: the
    vehicle read past the sampled pickup stop empty and the pickup monitor
    read zero residue at that sample (E53). The cycle is dropped as a typed
    event: never a success, never folded into WINDOW_EXHAUSTED, and the
    receipt stays bound to the same exchange evidence so the phase outcome
    can type the attempt's zero-cycle terminal state.
    """
    if zero.op != "load-watch" or zero.status != "ZERO_DEPARTED" or zero.cost != 0:
        raise ValueError("zero-departure cycle event mismatch")
    if zero.engine != ENGINE_PIN_V2 or zero.vehicle != vehicle:
        raise ValueError("zero-departure echo mismatch")
    if zero.load != 0:
        raise ValueError("a zero-departure event must read zero observed load")
    if zero.pickup_amount != 0:
        raise ValueError(
            "a zero-departure event must carry zero pickup-monitor evidence (E53)"
        )
    return dict(
        schema="company-freight2-zero-departed-receipt-v1",
        request_id=zero.request_id,
        load=zero.load,
        pickup_amount=zero.pickup_amount,
        tick=zero.tick or 0,
        day=zero.day or 0,
        funds=zero.funds,
        verification="NATIVE_ZERO_DEPARTED",
    )


def verify_freight_arrival_v2(
    arrived: FreightReadbackV2,
    *,
    vehicle: int,
    load: int,
    plan: FreightPlanV2,
) -> dict:
    """Verify the transit-watch window result: a full v2-route progress.

    The arrival binds the vehicle to the delivery stop across the
    vehicle route's full ordered progress (route length - 1 pairs). For a
    zero-departure cycle the truck must still arrive empty and the
    monitor windows stay zero.
    """
    if arrived.op != "transit-watch" or arrived.status != "AT_DELIVERY" or arrived.cost != 0:
        raise ValueError("transit window result mismatch")
    if arrived.engine != ENGINE_PIN_V2 or arrived.vehicle != vehicle:
        raise ValueError("transit readback echo mismatch")
    if load < 0 or arrived.load != load:
        raise ValueError("the vehicle must read at delivery with its departure load")
    if arrived.position != plan.delivery:
        raise ValueError("the vehicle must read at the pinned delivery stop")
    if arrived.progress != len(plan.vehicle_route) - 1:
        raise ValueError("arrival must complete the vehicle route progress")
    return dict(
        schema="company-freight2-arrival-receipt-v1",
        request_id=arrived.request_id,
        position=arrived.position,
        progress=arrived.progress,
        load=arrived.load,
        watch_ticks=arrived.watch_ticks,
        tick=arrived.tick,
        day=arrived.day,
        funds=arrived.funds,
        verification="NATIVE_TRANSIT_VERIFIED",
    )


def verify_freight_delivered_v2(
    unloaded: FreightReadbackV2, *, vehicle: int, load: int, delivery: int
) -> dict:
    """Verify the deliver-watch window result: unload plus monitor arithmetic.

    The per-cycle snapshot discipline gates: the acceptance sample must
    read the vehicle at the pinned delivery bay with zero remaining cargo
    (E53: the at-bay gate precedes any unload arithmetic and the DELIVERED
    echo carries the bay tile), both monitor deltas must equal the
    departure load exactly, and the consume-with-recheck re-arming read
    must observe zero residue.
    """
    if unloaded.op != "deliver-watch" or unloaded.status != "DELIVERED" or unloaded.cost != 0:
        raise ValueError("delivery window result mismatch")
    if unloaded.engine != ENGINE_PIN_V2 or unloaded.vehicle != vehicle:
        raise ValueError("delivery readback echo mismatch")
    if unloaded.load != 0:
        raise ValueError("the vehicle must read empty after its unload")
    if unloaded.position != delivery:
        raise ValueError(
            "the delivery acceptance must read the vehicle at the pinned "
            "delivery bay (E53)"
        )
    if (
        unloaded.pickup_amount is None
        or unloaded.delivery_amount is None
        or unloaded.pickup_amount != load
        or unloaded.delivery_amount != load
    ):
        raise ValueError("monitor arithmetic must reconcile the departure load exactly")
    if unloaded.recheck is not True:
        raise ValueError("the delivery window must record a zero consume-recheck re-arm")
    return dict(
        schema="company-freight2-delivered-receipt-v1",
        request_id=unloaded.request_id,
        load=unloaded.load,
        position=unloaded.position,
        pickup_amount=unloaded.pickup_amount,
        delivery_amount=unloaded.delivery_amount,
        recheck=unloaded.recheck,
        watch_ticks=unloaded.watch_ticks,
        watch_days=unloaded.watch_days,
        tick=unloaded.tick,
        day=unloaded.day,
        funds=unloaded.funds,
        verification="NATIVE_DELIVERY_VERIFIED",
    )


def verify_freight_finance_v2(
    read: FreightReadbackV2,
    *,
    vehicle: int,
    income0: int | None,
    delivered0: int | None,
    deliver_day: int,
) -> dict:
    """Verify the finance corroboration: same-attempt revenue increase.

    The quarterly income and delivered-cargo deltas are recorded from the
    monitor-family readbacks; the recorded revenue is the income delta, so
    no cargo payment rate is invented. The last accepted date must sit
    within the delivery window (day - 1 tolerance).
    """
    if read.op != "finance" or read.status != "FINANCE_VERIFIED" or read.cost != 0:
        raise ValueError("finance result mismatch")
    if read.engine != ENGINE_PIN_V2 or read.vehicle != vehicle:
        raise ValueError("finance readback echo mismatch")
    income_delta = (read.income or 0) - (income0 if income0 is not None else 0)
    delivered_delta = (read.delivered or 0) - (delivered0 if delivered0 is not None else 0)
    if delivered_delta > 0:
        if income_delta <= 0:
            raise ValueError("quarter income did not increase across the v2 attempt")
        if read.last_accepted is None or read.last_accepted < deliver_day - 1:
            raise ValueError("cargo acceptance date does not corroborate the delivery window")
    else:
        # Zero cargo reached the delivery bay during the attempt: the
        # readback must agree (no revenue, no delivered cargo). Revenue
        # without delivery would be unexplained drift, here a typed defect.
        if income_delta != 0:
            raise ValueError("income moved during the attempt without any delivered cargo")
        if delivered_delta != 0:
            raise ValueError("delivered cargo increased without a loaded departure")
    return dict(
        schema="company-freight2-finance-receipt-v1",
        request_id=read.request_id,
        income=read.income,
        income_baseline=income0,
        delivered=read.delivered,
        delivered_baseline=delivered0,
        deliver_day=deliver_day,
        last_accepted=read.last_accepted,
        revenue=income_delta,
        funds=read.funds,
        verification="NATIVE_FINANCE_VERIFIED",
    )


def verify_freight_finish_v2(stopped: FreightReadbackV2, *, vehicle: int) -> dict:
    """Verify the finish exchange: its stop command issued with final facts.

    ``PHASE_STOPPED`` records the issued stop and the vehicle's final
    state; the owned vehicle is never sold and no further authority is
    implied. The readback must prove the stop: the final state must read
    stopped (``STOPPED`` or ``IN_DEPOT``) at zero speed and ``stop_issued``
    is true only when the toggle was actually issued.
    """
    if stopped.op != "finish" or stopped.status != "PHASE_STOPPED" or stopped.cost != 0:
        raise ValueError("finish result mismatch")
    if stopped.engine != ENGINE_PIN_V2 or stopped.vehicle != vehicle:
        raise ValueError("finish readback echo mismatch")
    if stopped.stop_issued is not True:
        raise ValueError("the finish exchange must report its stop command issued")
    if stopped.state not in ("STOPPED", "IN_DEPOT") or stopped.speed is None or stopped.speed != 0:
        raise ValueError("the finished vehicle must be proven stopped at zero speed")
    return dict(
        schema="company-freight2-finish-receipt-v1",
        request_id=stopped.request_id,
        state=stopped.state,
        speed=stopped.speed,
        in_depot=stopped.in_depot,
        funds=stopped.funds,
        verification="NATIVE_PHASE_STOPPED",
    )


def freight_funds_equation_v2(
    ledger: list[dict],
    *,
    initial_funds: int,
    purchase_quote: int,
    final_funds: int,
    allowance: int = FREIGHT_RUNNING_COST_ALLOWANCE_V2,
) -> dict:
    """The F-6 equation of record over one attempt's funds ledger.

    Sign-convention normalization of record (real 15.x engine source):
    quarterly income accumulates positive and quarterly expenses accrue
    negative, so this ledger never reads raw expense signs — every
    exchange span attributes exactly:

    - the purchase span delta must equal the negative purchase quote and
      must carry zero income share;
    - every other span's running-cost share ``running = funds_delta -
      income_delta`` must be zero-or-negative in magnitude (funds only
      ever move by income up or running costs down) and bounded by the
      named per-exchange allowance derived from the census running cost
      over the window lease;
    - the income share (the readback quarter income's change) must be
      non-negative — the in-window FinanceOp read basis of record.

    The residual of the equation
    ``initial - purchase_quote + sum(income) + sum(running) == final``
    must be zero. This identity is structural over a complete contiguous
    ledger; its substance is the typed classification: any span whose
    attribution violates the category bounds raises (the typed
    FUNDS_DRIFT halt for callers that map ValueError to a typed halt).

    A quarter roll mid-attempt would show as a negative income read and
    is refused by the monotonic gate rather than silently re-sumed.
    """
    income_total = 0
    running_total = 0
    purchase_seen = False
    violations: list[dict] = []
    for index, exchange in enumerate(ledger):
        delta = exchange.get("delta")
        income_delta = exchange.get("income_delta", 0)
        op = exchange.get("op")
        if delta is None:
            raise ValueError(
                f"ledger entry {index} does not attribute its funds span"
            )
        if op == "purchase":
            if delta != -purchase_quote:
                violations.append(
                    dict(index=index, reason="purchase delta drifted from the recorded quote")
                )
            if income_delta != 0:
                violations.append(
                    dict(index=index, reason="purchase span carries an income share")
                )
            purchase_seen = True
            continue
        if income_delta < 0:
            violations.append(
                dict(index=index, reason="income share decreased inside a span")
            )
        running = delta - income_delta
        if not -allowance <= running <= 0:
            violations.append(
                dict(
                    index=index,
                    reason="running-cost attribution outside the taxonomy",
                    running=running,
                )
            )
        income_total += income_delta
        running_total += running
    if not purchase_seen:
        raise ValueError("the funds ledger records no purchase span")
    residual = (
        (initial_funds - purchase_quote + income_total + running_total) - final_funds
    )
    if residual != 0:
        raise ValueError("funds equation residual must be zero")
    if violations:
        raise ValueError(f"funds spans outside the taxonomy: {violations}")
    return dict(
        schema="company-freight2-funds-equation-v1",
        purchase_quote=purchase_quote,
        income_total=income_total,
        running_cost_total=running_total,
        initial_funds=initial_funds,
        final_funds=final_funds,
        residual=residual,
        verification="FUNDS_EQUATION_VERIFIED",
    )


def _freight_state_v2() -> dict:
    return dict(
        index=0,
        site=None,
        engine=None,
        vehicle=-1,
        load=0,
        reads={},
        ledger=[],
        funds=None,
        income=None,
        cycle_receipts=[],
        cycle_events=[],
        zero_events=[],
        # E53 day-authority ledger: the start exchange's economy day of
        # record, and the aggregate span the verified windows covered so
        # far (None until the first watch window is verified).
        day_reference=None,
        day_used=None,
    )


def _freight_success_step_v2(
    state: dict,
    request: FreightRequestV2,
    readback: FreightReadbackV2,
    *,
    prelaunch_digest: str,
    plan: FreightPlanV2,
) -> dict:
    """Run one exchange's verification against the accumulated attempt state."""
    op = request.op
    cycle_index = _FREIGHT_CYCLE_INDEX_BY_ID_V2.get(request.request_id)
    if op == "site":
        site = admit_freight_site_v2(
            readback, prelaunch_digest=prelaunch_digest, plan=plan
        )
        state["site"] = site
        return dict(
            schema="company-freight2-site-receipt-v1",
            request_id=readback.request_id,
            prelaunch_digest=prelaunch_digest,
            plan_digest=plan.digest,
            before_digest=readback.digest,
            site_digest=site.digest,
            company=site.company,
            pickup_sid=site.pickup_sid,
            delivery_sid=site.delivery_sid,
            depot=site.depot,
            depot_edge=site.depot_edge,
            accept=site.accept,
            pickup_radius=site.pickup_radius,
            delivery_radius=site.delivery_radius,
            pickup_industry=site.pickup_industry,
            delivery_industry=site.delivery_industry,
            production=site.production,
            waiting=site.waiting,
            vehicles=readback.vehicles,
            funds=site.funds,
            verification="SITE_ADMITTED",
        )
    if op == "engine":
        engine = admit_freight_engine_v2(
            readback, prelaunch_digest=prelaunch_digest, plan=plan, site=state["site"]
        )
        state["engine"] = engine
        return dict(
            schema="company-freight2-engine-receipt-v1",
            request_id=readback.request_id,
            prelaunch_digest=prelaunch_digest,
            plan_digest=plan.digest,
            before_digest=readback.digest,
            engine_digest=engine.digest,
            site_digest=engine.site_digest,
            company=engine.company,
            engine=engine.engine,
            engine_provisional=engine.provisional,
            cargo=engine.cargo,
            capacity=engine.capacity,
            price=engine.price,
            max_speed=engine.max_speed,
            fleet=engine.fleet,
            fleet_count=engine.fleet_count,
            quote=engine.quote,
            funds=readback.funds,
            verification="ENGINE_ADMITTED",
        )
    if op == "purchase":
        receipt = verify_freight_purchase_built_v2(
            state["engine"], state["reads"]["engine-00"], readback
        )
        state["vehicle"] = readback.vehicle
        return receipt
    if op == "vread" and request.request_id == "vread-00":
        return verify_freight_purchase_v2(
            state["engine"],
            state["reads"]["engine-00"],
            state["reads"]["purchase-00"],
            readback,
            plan=plan,
        )
    if op == "order":
        return verify_freight_order_v2(
            readback, index=request.order_index, vehicle=state["vehicle"], plan=plan
        )
    if op == "order-read":
        return verify_freight_order_set_v2(
            (state["reads"]["order-00"], state["reads"]["order-01"]),
            readback,
            vehicle=state["vehicle"],
            plan=plan,
        )
    if op == "monitor":
        state["monitor"] = readback
        return verify_freight_monitors_v2(readback, vehicle=state["vehicle"])
    if op == "start":
        return verify_freight_start_v2(readback, vehicle=state["vehicle"])
    if op == "vread" and request.request_id == "vread-01":
        return verify_freight_started_v2(
            state["reads"]["start-00"], readback, engine=state["engine"], vehicle=state["vehicle"]
        )
    if op == "load-watch":
        if readback.status == "ZERO_DEPARTED":
            zero = verify_freight_zero_departed_v2(
                readback, vehicle=state["vehicle"]
            )
            state["zero_events"].append(zero)
            state["load"] = 0
            return zero
        receipt = verify_freight_loaded_v2(
            readback,
            vehicle=state["vehicle"],
            engine=state["engine"],
            waiting_baseline=state["site"].waiting,
        )
        state["load"] = receipt["load"]
        return receipt
    if op == "transit-watch":
        return verify_freight_arrival_v2(
            readback,
            vehicle=state["vehicle"],
            load=state["load"],
            plan=plan,
        )
    if op == "deliver-watch":
        if cycle_index is None:
            raise ValueError("cycle receipts belong to cycle exchanges")
        # The window gates run for zero and loaded departures alike: the
        # delivery pass must still be proven empty at the pinned bay with
        # zero monitor residue. The cycle layer claims the typed receipt
        # (F-11) on top.
        gate = verify_freight_delivered_v2(
            readback,
            vehicle=state["vehicle"],
            load=state["load"],
            delivery=plan.delivery,
        )
        if state["load"] == 0:
            cycle_receipt = dict(
                schema="company-freight2-zero-cycle-receipt-v1",
                cycle=cycle_index,
                load=0,
                pickup_amount=readback.pickup_amount,
                delivery_amount=readback.delivery_amount,
                recheck=readback.recheck,
                funds=readback.funds,
                verification="NATIVE_ZERO_CYCLE_VERIFIED",
            )
        else:
            cycle_receipt = dict(
                schema="company-freight2-cycle-receipt-v1",
                cycle=cycle_index,
                load=state["load"],
                request_ids=[
                    f"load-{cycle_index:02d}",
                    f"transit-{cycle_index:02d}",
                    f"deliver-{cycle_index:02d}",
                ],
                funds=readback.funds,
                delivery=gate["request_id"],
                verification="NATIVE_CYCLE_VERIFIED",
            )
        return cycle_receipt
    if op == "finance":
        monitor = state["reads"]["monitor-00"]
        deliver = state["reads"][f"deliver-{plan.cycles - 1:02d}"]
        return verify_freight_finance_v2(
            readback,
            vehicle=state["vehicle"],
            income0=monitor.income,
            delivered0=monitor.delivered,
            deliver_day=deliver.day,
        )
    if op == "finish":
        return verify_freight_finish_v2(readback, vehicle=state["vehicle"])
    raise ValueError(f"unhandled freight v2 op {op}")  # pragma: no cover


def _freight_verify_step_v2(
    state: dict,
    request: FreightRequestV2,
    readback: FreightReadbackV2,
    *,
    prelaunch_digest: str,
    plan: FreightPlanV2,
) -> dict:
    """Verify one ordered exchange as the fixed v2 schedule prescribes."""
    expected = FREIGHT_EXCHANGE_IDS_V2[state["index"]]
    if request.request_id != expected or readback.request_id != expected:
        raise ValueError(f"freight v2 exchange out of order: expected {expected}")
    if request.op != _FREIGHT_OP_BY_ID_V2[expected]:
        raise ValueError("freight v2 request op disagrees with its planned exchange")
    if (readback.plan, readback.company) != (prelaunch_digest, plan.company):
        raise ValueError("freight v2 readback is not plan-scoped")
    if (readback.pickup, readback.delivery, readback.depot) != (
        plan.pickup,
        plan.delivery,
        plan.depot,
    ):
        raise ValueError("freight v2 readback pins drifted from the planned corridor")
    expected_witness = plan.witness_digest if request.op == "site" else None
    if request.witness_digest != expected_witness:
        raise ValueError("freight v2 request witness digest drifted from the plan")
    expected_route = plan.vehicle_route if request.op == "site" else None
    if request.route != expected_route:
        raise ValueError("freight v2 request route drifted from the planned route")
    if request.route_digest != plan.route_digest:
        raise ValueError("freight v2 request route digest drifted from the planned route")
    if readback.route_digest != plan.route_digest:
        raise ValueError("freight v2 readback route digest drifted from the planned route")
    expected_witness = plan.witness_digest if request.op == "site" else None
    if readback.witness_digest != expected_witness:
        raise ValueError("freight v2 readback witness digest drifted from the plan")
    if request.max_cost != plan.max_cost:
        raise ValueError("request ceiling drifted from the planned ceiling")
    if request.expected_cost != readback.expected_cost:
        raise ValueError("request and readback quote echoes disagree")
    op = request.op
    if op in _FREIGHT_WATCH_OPS_V2:
        # E53 replay hardening: a watch request must present exactly the
        # staged per-window budgets the plan derivation schedules (tick cap
        # and the uniform per-window economy-day lease); anything else is a
        # request this schedule could never have built.
        if (
            request.watch_ticks != WATCH_MAX_TICKS_V2
            or request.watch_days != window_watch_day_cap_v2(op)
        ):
            raise ValueError(
                "watch request echoes drifted from the staged window budgets"
            )
        # E53 aggregate authority: the dispatch gate runs on the ledger the
        # already-verified windows recorded, before any window evidence is
        # consumed — the same refusal the executor types before dispatch,
        # so replayed evidence cannot exploit a window the live gate would
        # never have opened.
        if state["day_reference"] is None:
            raise ValueError(
                "the day authority is not latched: the start exchange's "
                "day of record must verify before any watch window"
            )
        refusal = freight_window_dispatch_refusal_v2(
            state["day_used"] if state["day_used"] is not None else 0,
            request.watch_days,
        )
        if refusal is not None:
            raise ValueError(refusal)
    if readback.status != _FREIGHT_SUCCESS_STATUS_V2[op] and not (
        op == "load-watch" and readback.status == "ZERO_DEPARTED"
    ):
        raise ValueError(f"freight v2 exchange {expected} ended {readback.status}")
    try:
        receipt = _freight_success_step_v2(
            state, request, readback, prelaunch_digest=prelaunch_digest, plan=plan
        )
    finally:
        state["reads"][request.request_id] = readback
    if op == "start" and request.request_id == "start-00":
        # E53: the day of record every later window span is measured
        # against; a missing or unusable echo is refused before the ledger
        # can gain windows.
        if readback.day is None:
            raise ValueError("the start exchange did not echo its day of record")
        state["day_reference"] = readback.day
    if op in _FREIGHT_WATCH_OPS_V2:
        # E53 day ledger: the verified window's own day echo settles the
        # aggregate span. A regression, or a span beyond the whole attempt
        # authority, is a typed verification defect.
        if readback.day is None or state["day_reference"] is None:
            raise ValueError("watch evidence lost its day ledger basis")
        span = readback.day - state["day_reference"]
        if span < 0 or span > FREIGHT_DAY_BUDGET_V2:
            raise ValueError("the window day ledger regressed or escaped its authority")
        state["day_used"] = span
    previous_income = state["income"]
    if state["funds"] is None:
        # The first span runs from the pinned A1 close-out funds on, so the
        # earliest covered window is expected to move nothing (zero
        # construction before the first exchange); a silent pre-exchange
        # drift surfaces here and is attributed by the equation.
        delta = readback.funds - plan.expected_funds
    else:
        delta = readback.funds - state["funds"]
    income_delta = (
        0
        if previous_income is None or readback.income is None
        else readback.income - previous_income
    )
    if readback.income is not None:
        state["income"] = readback.income
    state["ledger"].append(
        dict(
            exchange=request.request_id,
            op=op,
            status=readback.status,
            funds=readback.funds,
            delta=delta,
            income=readback.income,
            income_delta=income_delta,
        )
    )
    state["funds"] = readback.funds
    state["index"] += 1
    return receipt


def verify_freight_attempt_v2(
    exchanges: list[tuple[FreightRequestV2, FreightReadbackV2]],
    *,
    prelaunch_digest: str,
    plan: FreightPlanV2,
) -> dict:
    """Verify the fixed v2 attempt cycle and emit its receipts.

    Ordered-unique: exchange ``k`` must be the plan's scheduled exchange
    ``k``; any refusal, inconclusive window, typed zero event or
    verification defect halts the attempt with a raised error and the
    prefix evidence already latched. The F-6 funds equation runs over the
    complete ledger at the end; a residual other than zero halts. This
    verifies evidence; it never issues requests.
    """
    if len(exchanges) != PLANNED_FREIGHT_EXCHANGES_V2:
        raise ValueError(
            f"the freight v2 attempt verifies exactly its {PLANNED_FREIGHT_EXCHANGES_V2} exchanges"
        )
    state = _freight_state_v2()
    receipts: list[dict] = []
    for request, readback in exchanges:
        receipts.append(
            _freight_verify_step_v2(
                state, request, readback,
                prelaunch_digest=prelaunch_digest, plan=plan,
            )
        )
    final_funds = state["reads"]["finish-00"].funds
    funds_report = freight_funds_equation_v2(
        state["ledger"],
        initial_funds=plan.expected_funds,
        purchase_quote=state["engine"].quote,
        final_funds=final_funds,
    )
    completed = sum(
        1
        for receipt in receipts
        if isinstance(receipt, dict) and receipt.get("verification") == "NATIVE_CYCLE_VERIFIED"
    )
    zeroed = sum(
        1
        for receipt in receipts
        if isinstance(receipt, dict)
        and receipt.get("verification") == "NATIVE_ZERO_CYCLE_VERIFIED"
    )
    zero_watches = len(state["zero_events"])
    verification = "FREIGHT_ATTEMPT_VERIFIED"
    if completed == 0 and zeroed > 0:
        verification = "FREIGHT_ZERO_DEPARTED_VERIFIED"
    return dict(
        schema="company-freight2-attempt-receipt-v1",
        prelaunch_digest=prelaunch_digest,
        plan_digest=plan.digest,
        attempt=plan.attempt,
        schedule_version=FREIGHT_SCHEDULE_VERSION,
        company=plan.company,
        engine=state["engine"].engine,
        vehicle=state["vehicle"],
        site_industry=state["site"].delivery_industry,
        cycle_count=PLANNED_FREIGHT_CYCLES_V2,
        completed_cycles=completed,
        zero_cycle_receipts=zeroed,
        zero_watch_events=zero_watches,
        # E53: the aggregate economy-day authority the verified windows
        # covered (each window's own day echo against the start day of
        # record), bounded by the 60-day attempt budget.
        day_ledger=dict(
            reference=state["day_reference"],
            used=state["day_used"] if state["day_used"] is not None else 0,
            budget=FREIGHT_DAY_BUDGET_V2,
        ),
        receipts=receipts,
        funds_ledger=state["ledger"],
        funds=funds_report,
        verification=verification,
    )


def freight_phase_outcome_v2(
    exchanges: list[tuple[FreightRequestV2, FreightReadbackV2]],
    *,
    prelaunch_digest: str,
    plan: FreightPlanV2,
) -> dict:
    """Fail-closed freight-attempt verification over preserved evidence only.

    Each exchange is ``(request, readback)``. The first halted exchange
    ends verification: earlier receipts are preserved, later exchanges are
    pending, and no retry or compensating mutation is represented or
    implied. Inconclusive window halts keep the world state honest
    (inconclusive, never a success); refusals that can only fire after an
    op's mutation command are labelled UNCERTAIN_AFTER_FAILED_COMMAND,
    never as leaving the world unchanged; typed zero-departure halts keep
    their own F-11 outcome class; other admission refusals halt before any
    mutation; a successful status that fails verification leaves the world
    explicitly uncertain. This verifies evidence; it never issues requests.
    """
    receipts: list[dict] = []
    failed = None
    pending: list[str] = []
    zero_seen = False
    state = _freight_state_v2()
    for request, readback in exchanges:
        if failed is not None:
            pending.append(request.request_id)
            continue
        try:
            receipts.append(
                _freight_verify_step_v2(
                    state, request, readback,
                    prelaunch_digest=prelaunch_digest, plan=plan,
                )
            )
        except Exception as error:  # noqa: BLE001 - fail closed on any defect
            status = getattr(readback, "status", "")
            if status == "ZERO_DEPARTED":
                zero_seen = True
                world = "ZERO_DEPARTED_EVIDENCE_PRESERVED"
            elif status in _FREIGHT_INCONCLUSIVE_STATUS_V2:
                world = "INCONCLUSIVE_WINDOW"
            elif status in _FREIGHT_SUCCESS_STATUS_V2.values():
                world = "UNCERTAIN_AFTER_FAILED_COMMAND"
            elif status in _FREIGHT_POST_MUTATION_STATUS_V2.get(
                getattr(request, "op", None), frozenset()
            ):
                world = "UNCERTAIN_AFTER_FAILED_COMMAND"
            else:
                world = "HALTED_BEFORE_MUTATION"
            failed = dict(
                label=request.request_id,
                status=str(status),
                error=str(error),
                world_state=world,
                zero_seen=zero_seen,
            )
    completed = sum(
        1
        for receipt in receipts
        if isinstance(receipt, dict) and receipt.get("verification") == "NATIVE_CYCLE_VERIFIED"
    )
    zero_cycles = sum(
        1
        for receipt in receipts
        if isinstance(receipt, dict)
        and receipt.get("verification") == "NATIVE_ZERO_CYCLE_VERIFIED"
    )
    complete = failed is None and len(exchanges) == PLANNED_FREIGHT_EXCHANGES_V2
    verification = "PHASE_COMPLETE" if complete else "PARTIAL_EXECUTION_EVIDENCE"
    if not complete and completed == 0 and zero_cycles > 0:
        verification = "ZERO_DEPARTED"
    if (
        not complete
        and completed == 0
        and not zero_seen
        and failed is not None
        and failed["world_state"] == "ZERO_DEPARTED_EVIDENCE_PRESERVED"
    ):
        verification = "ZERO_DEPARTED"
    return dict(
        schema="freight2-phase-outcome-v1",
        schedule_version=FREIGHT_SCHEDULE_VERSION,
        completed=receipts,
        failed=failed,
        pending=pending,
        completed_cycles=completed,
        zero_departed_cycles=zero_cycles,
        verification=verification,
    )
