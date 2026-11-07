"""CargoFlow delivery wire contract (protocol 11, additive).

Milestone D5-CARGOFLOW-2 (``docs/d5-cargoflow-delivery-design-2026-11-04.md``):
the E99 dispatch probe halted terminal at ``sample-07`` under a fence-target
defect, not a world behavior (§2). This module is the protocol-11 wire
contract for the real road-vehicle delivery attempt: a vehicle with
pickup/delivery orders is pinned at its census, purchased, ordered,
independently read back and started (§5.2 — the freight-family instrument
chain of record), then ``arrive-watch`` latches the first pickup-station
arrival (the ladder anchor, bounded at 5 economy days), and the fixed
twelve-sample flow ladder every 5 economy days from that anchor (offsets
0..55) plus the two read-only tail exchanges in the ``flow-11`` economy day
run to a total of 25 requests inside the 32-request budget of record
(``FREIGHT_REQUEST_BUDGET_V2``). Every flow sample measures the E99
observation set plus the funds echo at the post-wait instant (§4.5: one
response, one instant), the quarter-income/delivered reads, the vehicle
state echo and the cycle latches accumulated during the in-package wait
(§5.3), all fail-closed in company mode, one company.

The delivered-class tail (``docs/specs/d5-delivered-class-tail.md``)
extends this contract arm-wise for the E36 closure: one 5-economy-day
rung — ``flow-12`` at anchor+60, the settle margin that completes the
delivery cycle — plus the two tails riding that same economy day
compose the delivered arm keyed by the (2, 2) pairing (26 planned
exchanges inside the 65-economy-day authority of record), carried by an
optional ``schedule_version`` arm field on the plan, the requests and
the readbacks; the v1 envelope of record above stays byte-equal.

Protocol 11 stays additive over the number allocation of record (4
construction, 5 freight v1, 6 accept-survey, 7 terrain survey, 8 freight
v2, 9 box census, 10 dispatch probe): the GameScript bridge dispatches
protocol-11 tables through a separate guarded handler shipped in its own
package directory (``d5_cargoflow2_package``), so no frozen package byte
drifts and protocols 8/9/10 stay historical instruments of record.

The world of record is the consumed depot-mutation after-save
(``D5-F12-DEPOT-3``, world-pin version 3, after-save ``183b2027…1efe6a6``)
on the pinned binary/OpenGFX versions; the corridor tiles, station
identities and industry identities are the retained E99 pins. The funds
fence is the modeled trajectory of record (§4.4, zero-residual — residual
≠ 0 is a halt, never a tolerance): the exact purchase debit, the monthly
loan-interest staircase + 25 station fee at each economy-month boundary,
per-economy-day running costs through the exact 8.8 fixed-point fraction
carry (§4.3), delivery income read from the engine's own quarter accounting
at every observation instant, and an empty other-expenses set.

The corridor attempt contract is parameterized over the corridor route of
record (family versioning precedent — the ``EXTENSION_SCHEDULE_VERSION`` /
``SURVEY_SCHEDULE_VERSION`` selector with per-version plan pins): one
version selector plus a versioned binding map keyed by route binding id
live here, beside the plan contract, and every derivation of record
(plan, staged ladder rows, pin table, funds-model wiring) takes one
``Cargoflow2RouteBinding``. The corridor route of record (v1: pickup tile
45748 with front 45747 and station sid 0, delivery bay tile 50862 with
front 50863 and station sid 2, depot tile 45487 with front 45743,
industries 0/1, cargo 1, engine 123) is the DEFAULT instance chosen at
composition time, byte-equal to the pins of record; a binding naming an
unregistered version, and any cross-version composition mixing (a
version-1-labelled plan carrying another binding's pins, or a funds model
admitting another binding's census figures), fails closed here.
"""

import hashlib
import json
from collections.abc import Sequence
from typing import Annotated, Any, Literal

from pydantic import Field, StrictBool, StrictInt, StrictStr, model_validator

from app.planning.canonical import canonical_bytes
from app.planning.domain import Contract, Digest
from app.simulation.openttd.corridor_cargoflow import (
    CARGOFLOW_BAY_FRONT_TILE,
    CARGOFLOW_BAY_IND,
    CARGOFLOW_BAY_SID,
    CARGOFLOW_BAY_TILE,
    CARGOFLOW_DEPOT_FRONT_TILE,
    CARGOFLOW_DEPOT_TILE,
    CARGOFLOW_PICKUP_FRONT_TILE,
    CARGOFLOW_PICKUP_IND,
    CARGOFLOW_PICKUP_SID,
    CARGOFLOW_PICKUP_TILE,
)
from app.simulation.openttd.corridor_construction import (
    CompanyID,
    Money,
    SignedMoney,
    TileID,
)
from app.simulation.openttd.corridor_freight_v2 import (
    ENGINE_CENSUS_V2,
    ENGINE_PIN_V2,
    FREIGHT_CARGO_ID,
    FREIGHT_DAY_BUDGET_V2,
    FREIGHT_MAX_COST_V2,
    FREIGHT_REQUEST_BUDGET_V2,
    FUNDS_AT_DEPOT_MUTATION_CLOSE,
    OF_NO_LOAD_V2,
    OF_NONE_V2,
)


def _cargoflow2_canonical_bytes(model: Contract) -> bytes:
    """The corridor-local canonical bytes of record: the shared planning
    envelope of record with one arm-key exception — the arm field
    ``schedule_version`` disappears from the bytes whenever the model does
    not name one, so every v1 digest of record stays byte-equal while the
    delivered arm's bytes carry its own key. The canonical envelope itself
    is untouched: it keeps the None of every other model verbatim."""
    value = json.loads(canonical_bytes(model))
    if value.get("schedule_version") is None:
        value.pop("schedule_version", None)
    return json.dumps(
        value,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


CARGOFLOW2_PROTOCOL = 11
CARGOFLOW2_NAME = "cargoflow-delivery"
MAX_CARGOFLOW2_REQUEST_BYTES = 512
# The widest flow readback (the E99 sample set plus the vehicle echo, the
# income/delivered reads and a full bounded latch array) is measured in the
# focused suite; the bound sits under the GSAdmin.Send ceiling of record.
MAX_CARGOFLOW2_RESPONSE_BYTES = 1400
MAX_CARGOFLOW2_SEND_BYTES = 1450
MAX_GAMESCRIPT_PAYLOAD_BYTES = 32763
PLANNED_CARGOFLOW2_EXCHANGES = 25
CARGOFLOW2_REQUEST_BUDGET = FREIGHT_REQUEST_BUDGET_V2
CARGOFLOW2_DAY_BUDGET = FREIGHT_DAY_BUDGET_V2
CARGOFLOW2_COMPANY = 0
# The corridor cargo of record, imported from the freight v2 wire so the
# whole D5 lineage pins one id (the dispatch probe's own import rule).
CARGOFLOW2_CARGO = FREIGHT_CARGO_ID

# The depot-chain world of record's corridor identities (world-pin version
# 3, frozen protocol-10 pins re-echoed, never re-queried).
CARGOFLOW2_PICKUP_TILE = CARGOFLOW_PICKUP_TILE
CARGOFLOW2_PICKUP_FRONT_TILE = CARGOFLOW_PICKUP_FRONT_TILE
CARGOFLOW2_BAY_TILE = CARGOFLOW_BAY_TILE
CARGOFLOW2_BAY_FRONT_TILE = CARGOFLOW_BAY_FRONT_TILE
CARGOFLOW2_DEPOT_TILE = CARGOFLOW_DEPOT_TILE
CARGOFLOW2_DEPOT_FRONT_TILE = CARGOFLOW_DEPOT_FRONT_TILE
CARGOFLOW2_PICKUP_SID = CARGOFLOW_PICKUP_SID
CARGOFLOW2_BAY_SID = CARGOFLOW_BAY_SID
CARGOFLOW2_PICKUP_IND = CARGOFLOW_PICKUP_IND
CARGOFLOW2_BAY_IND = CARGOFLOW_BAY_IND

# The vehicle of record: the freight v2 provisional engine pin, admitted
# fail-closed at its census (§5.2: cargo 1, capacity 20, price 4429,
# running 421/yr display figure, max_speed 48) and never enumerated for a
# lowest-compatible id.
CARGOFLOW2_ENGINE = ENGINE_PIN_V2
CARGOFLOW2_ENGINE_MAX_COST = FREIGHT_MAX_COST_V2
CARGOFLOW2_PURCHASE_QUOTE = ENGINE_CENSUS_V2["price"]
CARGOFLOW2_RUNNING_DISPLAY = ENGINE_CENSUS_V2["running_cost_per_economy_year"]
CARGOFLOW2_CAPACITY = ENGINE_CENSUS_V2["capacity"]
CARGOFLOW2_MAX_SPEED = ENGINE_CENSUS_V2["max_speed"]
CARGOFLOW2_ORDER_PICKUP_FLAGS = OF_NONE_V2
CARGOFLOW2_ORDER_DELIVERY_FLAGS = OF_NO_LOAD_V2

# The financial model of record (§4.1), every parameter pinned.
CARGOFLOW2_START_FUNDS = FUNDS_AT_DEPOT_MUTATION_CLOSE
CARGOFLOW2_FOUNDING_LOAN = 100000
CARGOFLOW2_INTEREST_RATE = 2
CARGOFLOW2_STATION_FEE = 25
CARGOFLOW2_YEARLY_INTEREST = CARGOFLOW2_FOUNDING_LOAN * CARGOFLOW2_INTEREST_RATE // 100
DAYS_IN_ECONOMY_YEAR = 365
DAY_TICKS = 74

# The E113 charge-event lattice of record: the spread economy-day proc
# ("This is called once per day for each vehicle, but not in the first
# tick of the day", vehicle.cpp:921-950 at tag-15.3) dispatches each
# vehicle on the first tick after its day's roll — vehicle 1's slot
# (``index % DAY_TICKS == 1``) inside ``CallVehicleTicks``, which runs
# after the economy ``Elapsed`` roll (openttd.cpp:1264-1267). The charge
# events sit at ``T0 + 1 + 74k``; with the day-roll anchor T0 = 48 (E112's
# clock law of record, ``date = 712229 + floor((tick - 48) / 74)``) the
# event k bills on its own rolled day ``CARGOFLOW2_LAUNCH_DAY + 1 + k``.
CARGOFLOW2_DAY_ROLL_ANCHOR = 48
CARGOFLOW2_CHARGE_SLOT = 1

# The launch day of record: L = 712228 (Jan 6, 1950 — the save's current
# date at load, pinned by E99's ``sample-00`` anchor at tick 17). The 1950
# calendar base of record: day 712223 is Jan 1, 1950. The attempt can never
# leave 1950 (its last admissible observation day is 712293 = L + 65, the
# delivered ladder's own settle margin on March 12, 1950 — the v1 ladder's
# worst-case end is 712288 = L + 60, a normal early-March day), so the
# month-boundary days that can fall inside an attempt span are enumerated
# exactly.
CARGOFLOW2_LAUNCH_DAY = 712228
_CALENDAR_BASE_DAY = 712223
DAYS_IN_MONTH_1950 = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
CARGOFLOW2_ARRIVE_MAX_DAYS = 5

# The flow ladder of record: anchor-relative economy-day offsets every 5
# days, 0..55. The arrival bound (§5.3) puts the anchor at most at day
# L + 5, so the last flow/tail day is at most L + 60: exactly the 60-day
# attempt authority enforced twice, package-side and pipeline-side.
CARGOFLOW2_FLOW_OFFSETS: tuple[int, ...] = tuple(range(0, 60, 5))
CARGOFLOW2_SPAN_DAYS = CARGOFLOW2_FLOW_OFFSETS[-1]
CARGOFLOW2_TAIL_OFFSET = CARGOFLOW2_SPAN_DAYS
CARGOFLOW2_WAIT_MAX_TICKS = 2048
CARGOFLOW2_WAIT_DAY_CAP = CARGOFLOW2_DAY_BUDGET
CARGOFLOW2_OFFSET_CAP = CARGOFLOW2_SPAN_DAYS
# The delivered-class tail (the D5 delivered-class tail spec, ticket 02): the
# extension rides the (route_version=2, schedule_version=2) pairing — one
# extra 5-economy-day rung, ``flow-12`` at anchor+60, gives the cycle its own
# completion stop. The loaded vehicle returns to its final stand with the
# unload ETA at anchor+57..58, so the rung at anchor+60 = day L + 64 is the
# settle margin of record, and both read-only tails move into that same
# economy day (the 60-day v1 envelope above stays untouched: its ladder,
# tails, 60-day budget and authority last day 712288).
CARGOFLOW2_DELIVERED_SCHEDULE_VERSION = 2
CARGOFLOW2_DELIVERED_FLOW_OFFSETS: tuple[int, ...] = CARGOFLOW2_FLOW_OFFSETS + (60,)
CARGOFLOW2_DELIVERED_SPAN_DAYS = CARGOFLOW2_DELIVERED_FLOW_OFFSETS[-1]
CARGOFLOW2_DELIVERED_TAIL_OFFSET = CARGOFLOW2_DELIVERED_SPAN_DAYS
CARGOFLOW2_DELIVERED_DAY_BUDGET = CARGOFLOW2_ARRIVE_MAX_DAYS + CARGOFLOW2_DELIVERED_SPAN_DAYS
PLANNED_CARGOFLOW2_DELIVERED_EXCHANGES = PLANNED_CARGOFLOW2_EXCHANGES + 1
CARGOFLOW2_DELIVERED_OFFSET_CAP = CARGOFLOW2_DELIVERED_SPAN_DAYS
CARGOFLOW2_DELIVERED_WAIT_DAY_CAP = CARGOFLOW2_DELIVERED_DAY_BUDGET
# Per-flow-sample latch bound of record: a latch array that would overflow
# its response budget refuses the exchange terminally (§5.3) — latches are
# never truncated to fit. Eight latches of five economy days is the widest
# window with measured headroom; the focused suite measures the widest
# readback against this bound.
CARGOFLOW2_LATCH_LIMIT = 8

CARGOFLOW2_OPS = (
    "site",
    "engine",
    "purchase",
    "vread",
    "order",
    "order-read",
    "monitor",
    "start",
    "arrive-watch",
    "flow",
    "finance",
    "finish",
)

Cargoflow2Op = Literal[
    "site",
    "engine",
    "purchase",
    "vread",
    "order",
    "order-read",
    "monitor",
    "start",
    "arrive-watch",
    "flow",
    "finance",
    "finish",
]

# The protocol-11 status family: the freight-8 success nouns, the frozen
# survey refusal family, the flow window/E99 echo family, and this round's
# typed arrivals.
Cargoflow2Status = Literal[
    "READY",
    "BUILT",
    "READ",
    "ORDERED",
    "ORDER_SET_VERIFIED",
    "ARMED",
    "STARTED",
    "ANCHORED",
    "FINANCE_VERIFIED",
    "PHASE_STOPPED",
    "INVALID_COMPANY",
    "INVALID_SITE",
    "NO_ENGINE",
    "UNAVAILABLE_ENGINE",
    "ENGINE_PIN_MISMATCH",
    "INSUFFICIENT_FUNDS",
    "COST_LIMIT",
    "COST_CHANGED",
    "PAUSED",
    "ALREADY_ATTEMPTED",
    "STALE_ADMISSION",
    "UNSUPPORTED_NATIVE_FACT",
    "READBACK_MISMATCH",
    "OUT_OF_ORDER",
    "WINDOW_EXHAUSTED",
    "CLOCK_STALLED",
    "ARRIVE_TIMEOUT",
    "AUTHORITY_EXCEEDED",
    "LATCH_OVERFLOW",
]
CARGOFLOW2_ATTEMPT_SCHEMA_VERSION = 1
CARGOFLOW2_RECEIPT_SCHEMA = "cargo-flow2-sample-receipt-v1"
CARGOFLOW2_OUTCOME_SCHEMA = "cargo-flow2-phase-outcome-v1"
CARGOFLOW2_READ_ONLY_SCHEMA = "d5-cargoflow2-readonly-v1"

_CARGOFLOW2_SUCCESS_STATUS: dict[Cargoflow2Op, str] = {
    "site": "READY",
    "engine": "READY",
    "purchase": "BUILT",
    "vread": "READ",
    "order": "ORDERED",
    "order-read": "ORDER_SET_VERIFIED",
    "monitor": "ARMED",
    "start": "STARTED",
    "arrive-watch": "ANCHORED",
    "flow": "READY",
    "finance": "FINANCE_VERIFIED",
    "finish": "PHASE_STOPPED",
}
_CARGOFLOW2_INCONCLUSIVE_STATUS = frozenset({"WINDOW_EXHAUSTED", "CLOCK_STALLED"})
_CARGOFLOW2_REFUSAL_STATUS = frozenset(
    {
        "INVALID_COMPANY",
        "INVALID_SITE",
        "NO_ENGINE",
        "UNAVAILABLE_ENGINE",
        "ENGINE_PIN_MISMATCH",
        "INSUFFICIENT_FUNDS",
        "COST_LIMIT",
        "COST_CHANGED",
        "PAUSED",
        "ALREADY_ATTEMPTED",
        "STALE_ADMISSION",
        "UNSUPPORTED_NATIVE_FACT",
        "READBACK_MISMATCH",
        "OUT_OF_ORDER",
        "ARRIVE_TIMEOUT",
        "AUTHORITY_EXCEEDED",
        "LATCH_OVERFLOW",
    }
)
# The wait-window echo family (E99 precedent): these statuses carry exactly
# the three ladder echoes — the honest halted-window evidence of record
# (anchor/tick/day) — while every other refusal carries none.
_CARGOFLOW2_WINDOW_ECHO_STATUS = frozenset({"WINDOW_EXHAUSTED", "CLOCK_STALLED"})
_CARGOFLOW2_WINDOW_ECHO_FIELDS = ("anchor", "tick", "day")
_CARGOFLOW2_OFFSET_BY_ID: dict[str, int] = {
    **{f"flow-{index:02d}": offset for index, offset in enumerate(CARGOFLOW2_FLOW_OFFSETS)},
    "finance-00": CARGOFLOW2_TAIL_OFFSET,
    "finish-00": CARGOFLOW2_TAIL_OFFSET,
}
_CARGOFLOW2_FIXED_SEQUENCE: tuple[tuple[str, Cargoflow2Op], ...] = (
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
    ("arrive-00", "arrive-watch"),
)
_CARGOFLOW2_FLOW_SEQUENCE: tuple[tuple[str, Cargoflow2Op], ...] = tuple(
    (f"flow-{index:02d}", "flow") for index in range(len(CARGOFLOW2_FLOW_OFFSETS))
)
_CARGOFLOW2_TAIL_SEQUENCE: tuple[tuple[str, Cargoflow2Op], ...] = (
    ("finance-00", "finance"),
    ("finish-00", "finish"),
)
_CARGOFLOW2_SEQUENCE: tuple[tuple[str, Cargoflow2Op], ...] = (
    _CARGOFLOW2_FIXED_SEQUENCE + _CARGOFLOW2_FLOW_SEQUENCE + _CARGOFLOW2_TAIL_SEQUENCE
)
CARGOFLOW2_EXCHANGE_IDS: tuple[str, ...] = tuple(
    exchange_id for exchange_id, _ in _CARGOFLOW2_SEQUENCE
)
_CARGOFLOW2_OP_BY_ID: dict[str, Cargoflow2Op] = dict(_CARGOFLOW2_SEQUENCE)
_CARGOFLOW2_REQUEST_OFFSET_BY_ID: dict[str, int] = {
    exchange_id: _CARGOFLOW2_OFFSET_BY_ID.get(exchange_id, -1)
    for exchange_id in CARGOFLOW2_EXCHANGE_IDS
}

# The delivered arm's own sequences of record: the same v1 shape with the
# thirteenth flow row appended — every arm resolution comes from the
# record's own ``schedule_version`` field, never from ids (the tail ids are
# arm-ambiguous between the 55- and 60-day ladders).
_CARGOFLOW2_DELIVERED_OP_BY_ID: dict[str, Cargoflow2Op] = dict(
    _CARGOFLOW2_SEQUENCE
    + tuple((exchange_id, "flow") for exchange_id in (f"flow-{len(CARGOFLOW2_FLOW_OFFSETS):02d}",))
)
_CARGOFLOW2_DELIVERED_OFFSET_BY_ID: dict[str, int] = {
    **{
        f"flow-{index:02d}": offset
        for index, offset in enumerate(CARGOFLOW2_DELIVERED_FLOW_OFFSETS)
    },
    "finance-00": CARGOFLOW2_DELIVERED_TAIL_OFFSET,
    "finish-00": CARGOFLOW2_DELIVERED_TAIL_OFFSET,
}
_CARGOFLOW2_DELIVERED_FLOW_SEQUENCE: tuple[tuple[str, Cargoflow2Op], ...] = tuple(
    (f"flow-{index:02d}", "flow") for index in range(len(CARGOFLOW2_DELIVERED_FLOW_OFFSETS))
)
_CARGOFLOW2_DELIVERED_SEQUENCE: tuple[tuple[str, Cargoflow2Op], ...] = (
    _CARGOFLOW2_FIXED_SEQUENCE + _CARGOFLOW2_DELIVERED_FLOW_SEQUENCE + _CARGOFLOW2_TAIL_SEQUENCE
)
CARGOFLOW2_DELIVERED_EXCHANGE_IDS: tuple[str, ...] = tuple(
    exchange_id for exchange_id, _ in _CARGOFLOW2_DELIVERED_SEQUENCE
)
_CARGOFLOW2_DELIVERED_REQUEST_OFFSET_BY_ID: dict[str, int] = {
    exchange_id: _CARGOFLOW2_DELIVERED_OFFSET_BY_ID.get(exchange_id, -1)
    for exchange_id in CARGOFLOW2_DELIVERED_EXCHANGE_IDS
}


def _cargoflow2_arm_offset_map(
    schedule_version: int | None,
) -> dict[str, int]:
    """The readback ladder offset map of one attempt arm, keyed by the
    record's own ``schedule_version`` (an unnamed arm is the v1 arm)."""
    return (
        _CARGOFLOW2_DELIVERED_OFFSET_BY_ID
        if schedule_version == CARGOFLOW2_DELIVERED_SCHEDULE_VERSION
        else _CARGOFLOW2_OFFSET_BY_ID
    )


def _cargoflow2_arm_request_offset_map(
    schedule_version: int | None,
) -> dict[str, int]:
    """The request ladder offset map of one attempt arm, resolved the same
    way."""
    return (
        _CARGOFLOW2_DELIVERED_REQUEST_OFFSET_BY_ID
        if schedule_version == CARGOFLOW2_DELIVERED_SCHEDULE_VERSION
        else _CARGOFLOW2_REQUEST_OFFSET_BY_ID
    )


def _cargoflow2_arm_op_by_id(
    schedule_version: int | None,
) -> dict[str, Cargoflow2Op]:
    """The exchange id → op map of one attempt arm, resolved the same way."""
    return (
        _CARGOFLOW2_DELIVERED_OP_BY_ID
        if schedule_version == CARGOFLOW2_DELIVERED_SCHEDULE_VERSION
        else _CARGOFLOW2_OP_BY_ID
    )


_MONTH_STARTS_1950 = tuple(_CALENDAR_BASE_DAY + sum(DAYS_IN_MONTH_1950[:m]) for m in range(0, 12))
# Boundaries of record as literals: the derived starts must equal these
# (the _assert_cargoflow2_calendar cross-check below), and this literal
# form keeps the §4 guard foldable for the type checker.
CARGOFLOW2_MONTH_BOUNDARY_DAYS: tuple[int, ...] = (
    712254,
    712282,
    712313,
    712343,
    712374,
    712404,
    712435,
    712466,
    712496,
    712527,
    712557,
)
_CARGOFLOW2_MONTH_INSTALLMENT_BY_DAY: dict[int, int] = {
    boundary: CARGOFLOW2_YEARLY_INTEREST * (m + 1) // 12 - CARGOFLOW2_YEARLY_INTEREST * m // 12
    for m, boundary in enumerate(CARGOFLOW2_MONTH_BOUNDARY_DAYS, start=1)
}
if (
    len(CARGOFLOW2_EXCHANGE_IDS) != PLANNED_CARGOFLOW2_EXCHANGES
    or len(set(CARGOFLOW2_EXCHANGE_IDS)) != PLANNED_CARGOFLOW2_EXCHANGES
    or _CARGOFLOW2_OFFSET_BY_ID["flow-11"] != 55
    or CARGOFLOW2_SPAN_DAYS != 55
    or CARGOFLOW2_ARRIVE_MAX_DAYS + CARGOFLOW2_SPAN_DAYS != CARGOFLOW2_DAY_BUDGET
    or CARGOFLOW2_LAUNCH_DAY + CARGOFLOW2_DAY_BUDGET != 712288
    or _CARGOFLOW2_MONTH_INSTALLMENT_BY_DAY[712254] != 167
    or _CARGOFLOW2_MONTH_INSTALLMENT_BY_DAY[712282] != 167
    or CARGOFLOW2_YEARLY_INTEREST != 2000
    or CARGOFLOW2_DAY_ROLL_ANCHOR != 48
    or CARGOFLOW2_CHARGE_SLOT != 1
    or PLANNED_CARGOFLOW2_EXCHANGES > CARGOFLOW2_REQUEST_BUDGET
    or CARGOFLOW2_WAIT_MAX_TICKS != 2048
    or CARGOFLOW2_WAIT_DAY_CAP != 60
    or CARGOFLOW2_PICKUP_IND != 0
    or CARGOFLOW2_BAY_IND != 1
    or CARGOFLOW2_PICKUP_SID != 0
    or CARGOFLOW2_BAY_SID != 2
    or _CARGOFLOW2_FIXED_SEQUENCE[-1][1] != "arrive-watch"
    or CARGOFLOW2_MONTH_BOUNDARY_DAYS
    != (
        712254,
        712282,
        712313,
        712343,
        712374,
        712404,
        712435,
        712466,
        712496,
        712527,
        712557,
    )
):
    raise RuntimeError("cargo-flow delivery schedule drifted from the pinned observations")
if (
    len(CARGOFLOW2_DELIVERED_EXCHANGE_IDS) != PLANNED_CARGOFLOW2_DELIVERED_EXCHANGES
    or len(set(CARGOFLOW2_DELIVERED_EXCHANGE_IDS)) != PLANNED_CARGOFLOW2_DELIVERED_EXCHANGES
    or len(CARGOFLOW2_DELIVERED_FLOW_OFFSETS) != 13
    or CARGOFLOW2_DELIVERED_FLOW_OFFSETS[:12] != CARGOFLOW2_FLOW_OFFSETS
    or _CARGOFLOW2_DELIVERED_OFFSET_BY_ID["flow-12"] != 60
    or _CARGOFLOW2_DELIVERED_OFFSET_BY_ID["finance-00"] != 60
    or CARGOFLOW2_DELIVERED_SPAN_DAYS != 60
    or CARGOFLOW2_ARRIVE_MAX_DAYS + CARGOFLOW2_DELIVERED_SPAN_DAYS
    != CARGOFLOW2_DELIVERED_DAY_BUDGET
    or CARGOFLOW2_DELIVERED_DAY_BUDGET != 65
    or CARGOFLOW2_LAUNCH_DAY + CARGOFLOW2_DELIVERED_DAY_BUDGET != 712293
    or PLANNED_CARGOFLOW2_DELIVERED_EXCHANGES > CARGOFLOW2_REQUEST_BUDGET
    or CARGOFLOW2_DELIVERED_EXCHANGE_IDS[:23] != CARGOFLOW2_EXCHANGE_IDS[:23]
    or CARGOFLOW2_DELIVERED_EXCHANGE_IDS[23:24] != ("flow-12",)
    or CARGOFLOW2_DELIVERED_EXCHANGE_IDS[24:] != CARGOFLOW2_EXCHANGE_IDS[23:]
    or len(_CARGOFLOW2_DELIVERED_OP_BY_ID) != PLANNED_CARGOFLOW2_DELIVERED_EXCHANGES
):
    raise RuntimeError("the delivered cargo-flow ladder drifted from its pinned observations")
if max(MAX_CARGOFLOW2_REQUEST_BYTES, MAX_CARGOFLOW2_RESPONSE_BYTES) > max(
    MAX_CARGOFLOW2_SEND_BYTES, MAX_GAMESCRIPT_PAYLOAD_BYTES
):
    raise RuntimeError("cargo-flow 11 byte bounds exceed the AdminPort payload limits")


def _assert_cargoflow2_calendar() -> None:
    """Derived 1950 month starts must equal the pinned boundaries (§4)."""
    if _MONTH_STARTS_1950[1:] != CARGOFLOW2_MONTH_BOUNDARY_DAYS:
        raise RuntimeError("the 1950 month starts drifted from the pinned boundaries")


_assert_cargoflow2_calendar()


def cargoflow2_month_charge(day: int) -> int:
    """The whole-unit monthly charge of record at one new economy month.

    The staircase installment on ``yearly = current_loan · rate/100`` (the
    founding loan never moves in this attempt) plus the pinned station-value
    fee (§4.2 items 2-3). Feb 1 charges 167 + 25 = 192 — the E99-replicated
    cross-check of record.
    """
    installment = _CARGOFLOW2_MONTH_INSTALLMENT_BY_DAY.get(day)
    if installment is None:
        raise ValueError(f"day {day} is not a pinned 1950 month boundary")
    return installment + CARGOFLOW2_STATION_FEE


Cargoflow2ActorId = Annotated[StrictInt, Field(ge=-1, le=65535)]
Cargoflow2Amount = Annotated[StrictInt, Field(ge=0, le=2147483647)]
Cargoflow2Clock = Annotated[StrictInt, Field(ge=0, le=2147483647)]
Cargoflow2SignedClock = Annotated[StrictInt, Field(ge=-1, le=2147483647)]
Cargoflow2WatchDays = Annotated[StrictInt, Field(ge=-1, le=CARGOFLOW2_DAY_BUDGET)]
Cargoflow2OrderIndex = Annotated[StrictInt, Field(ge=-1, le=1)]
Cargoflow2EchoFlags = Annotated[StrictInt, Field(ge=-1, le=255)]
# The echo offset domain covers both arms' ladders (55 and 60): the arm map
# of record, not this bound, names a request's planned ladder step.
Cargoflow2EchoOffset = Annotated[StrictInt, Field(ge=-1, le=CARGOFLOW2_DELIVERED_OFFSET_CAP)]
Cargoflow2VehicleState = Literal[
    "INVALID",
    "IN_DEPOT",
    "RUNNING",
    "STOPPED",
    "AT_STATION",
    "BROKEN",
    "CRASHED",
]
Cargoflow2LatchKind = Literal[
    "arrival_pickup",
    "arrival_bay",
    "load",
    "departure",
    "unload",
]


class Cargoflow2RouteBinding(Contract):
    """One versioned corridor route binding: the pinned route identity and
    attempt-clock parameters one admitted route's composition derives from.

    A binding owns every route-derived pin of record — the corridor stops
    with their fronts, the pinned station and industry identities, the
    depot, the engine census and authority pins, the order flags, the
    financial pins and the launch clock with its two boundary figures — and
    nothing of the ladder instrument (the exchange ids, ops, offsets and
    the staged ladder rows stay the module's derivation of record, riding
    the pinned flow ladder the shipped package carries). Version 1 is the
    corridor route of record and the DEFAULT instance; a second admitted
    route registers the next id and composes the same way. Cohesion fails
    closed: a binding whose stops share a station or industry identity,
    whose quote escapes its own authority, whose clock escapes the
    60-economy-day authority, the equality-gated ladder of record or the
    pinned 1950 boundary enumeration refuses at construction — so no
    registered binding can ever compose a plan or a funds model whose pins
    disagree with the binding itself. Version 1 is the corridor route of
    record and the DEFAULT instance; version 2 is the ticket-08 second
    admission of record (the same pinned identities, admitted through the
    same checks) and composes the same way.
    """

    route_version: Literal[1, 2]
    company: CompanyID
    cargo: Annotated[StrictInt, Field(ge=0, le=63)]
    pickup: TileID
    pickup_front: TileID
    pickup_sid: Annotated[StrictInt, Field(ge=0, le=65535)]
    pickup_industry: Annotated[StrictInt, Field(ge=0, le=65535)]
    delivery: TileID
    delivery_front: TileID
    bay_sid: Annotated[StrictInt, Field(ge=0, le=65535)]
    bay_industry: Annotated[StrictInt, Field(ge=0, le=65535)]
    depot: TileID
    depot_front: TileID
    engine: Cargoflow2ActorId
    engine_max_cost: Money
    purchase_quote: Money
    engine_running_display: Annotated[StrictInt, Field(ge=1, le=2147483647)]
    engine_capacity: Annotated[StrictInt, Field(ge=1, le=65535)]
    engine_max_speed: Annotated[StrictInt, Field(ge=0, le=2147483647)]
    order_pickup_flags: Annotated[StrictInt, Field(ge=0, le=255)]
    order_delivery_flags: Annotated[StrictInt, Field(ge=0, le=255)]
    start_funds: Money
    founding_loan: Money
    interest_rate: Annotated[StrictInt, Field(ge=0, le=100)]
    station_fee: Money
    launch_day: Cargoflow2Clock
    arrive_max_days: Annotated[StrictInt, Field(ge=1, le=CARGOFLOW2_DAY_BUDGET)]
    flow_span_days: Annotated[StrictInt, Field(ge=1, le=CARGOFLOW2_DAY_BUDGET)]

    @property
    def digest(self) -> str:
        return hashlib.sha256(_cargoflow2_canonical_bytes(self)).hexdigest()

    @model_validator(mode="after")
    def coherent(self) -> Cargoflow2RouteBinding:
        if self.pickup_sid == self.bay_sid:
            raise ValueError("the bound stops must carry distinct station ids")
        if self.pickup_industry == self.bay_industry:
            raise ValueError("the bound stops must observe distinct industries")
        if self.purchase_quote > self.engine_max_cost:
            raise ValueError("the purchase quote escaped the binding's own authority")
        if self.arrive_max_days + self.flow_span_days != CARGOFLOW2_DAY_BUDGET:
            raise ValueError(
                "the binding's arrival bound plus flow span must equal the "
                "60-economy-day attempt authority (the equality-gated ladder)"
            )
        if self.flow_span_days != CARGOFLOW2_FLOW_OFFSETS[-1]:
            raise ValueError("a route binding rides the pinned 12-sample flow ladder of record")
        if self.launch_day <= _CALENDAR_BASE_DAY or (
            self.launch_day + CARGOFLOW2_DAY_BUDGET > _CALENDAR_BASE_DAY + sum(DAYS_IN_MONTH_1950)
        ):
            raise ValueError(
                "the binding's attempt clock escapes the pinned 1950 boundary enumeration of record"
            )
        return self


# The route-version selector of record, named after the family precedent
# (``EXTENSION_SCHEDULE_VERSION`` / ``SURVEY_SCHEDULE_VERSION``): it selects
# the DEFAULT route binding at composition time, and the plan contract
# resolves every schema_version against its own registered binding below.
CARGOFLOW2_SCHEDULE_VERSION = 1

# The corridor route of record (v1): built exactly from this module's
# pinned route constants — the corridor pickup tile 45748 (front 45747,
# station sid 0), the delivery bay tile 50862 (front 50863, station sid 2),
# the depot tile 45487 (front 45743), industries 0/1, cargo 1, engine 123 —
# so the default plan derivation stays byte-equal to the plan of record.
CARGOFLOW2_ROUTE_OF_RECORD = Cargoflow2RouteBinding(
    route_version=1,
    company=CARGOFLOW2_COMPANY,
    cargo=CARGOFLOW2_CARGO,
    pickup=CARGOFLOW2_PICKUP_TILE,
    pickup_front=CARGOFLOW2_PICKUP_FRONT_TILE,
    pickup_sid=CARGOFLOW2_PICKUP_SID,
    pickup_industry=CARGOFLOW2_PICKUP_IND,
    delivery=CARGOFLOW2_BAY_TILE,
    delivery_front=CARGOFLOW2_BAY_FRONT_TILE,
    bay_sid=CARGOFLOW2_BAY_SID,
    bay_industry=CARGOFLOW2_BAY_IND,
    depot=CARGOFLOW2_DEPOT_TILE,
    depot_front=CARGOFLOW2_DEPOT_FRONT_TILE,
    engine=CARGOFLOW2_ENGINE,
    engine_max_cost=CARGOFLOW2_ENGINE_MAX_COST,
    purchase_quote=CARGOFLOW2_PURCHASE_QUOTE,
    engine_running_display=CARGOFLOW2_RUNNING_DISPLAY,
    engine_capacity=CARGOFLOW2_CAPACITY,
    engine_max_speed=CARGOFLOW2_MAX_SPEED,
    order_pickup_flags=CARGOFLOW2_ORDER_PICKUP_FLAGS,
    order_delivery_flags=CARGOFLOW2_ORDER_DELIVERY_FLAGS,
    start_funds=CARGOFLOW2_START_FUNDS,
    founding_loan=CARGOFLOW2_FOUNDING_LOAN,
    interest_rate=CARGOFLOW2_INTEREST_RATE,
    station_fee=CARGOFLOW2_STATION_FEE,
    launch_day=CARGOFLOW2_LAUNCH_DAY,
    arrive_max_days=CARGOFLOW2_ARRIVE_MAX_DAYS,
    flow_span_days=CARGOFLOW2_SPAN_DAYS,
)

# The second admission of record (v2, ticket 08 of the D5 corridor PoC
# tail): the bounded planning pipeline's competing candidate on the pinned
# corridor facts of record — the corner-swap route
# ``witness[:23] + (50351, 50352) + witness[27:]`` (29 tiles, ordered digest
# ``d14587b2f2973e1ed8da31d03e00f66863ce2cf3b13ef7f20d2f2a1f0c4dd482``,
# distinct from ``freight_route_digest_v2(FREIGHT_ROUTE_V2)`` — the delivered
# route's descriptive duplicate is refused as such), enumerated by the
# corridor route optimizer's bounded k-shortest machinery at the
# freight-route-v2 bound class and admitted through the same offline checks
# the delivered route passed, with the funds gates of record (evidence index
# E118). The candidate differs from the delivered route ONLY in the physical
# tile path, which the binding contract never encodes (the route identity
# lives in the plan's versioned digest and the derived evidence ledger), so
# a pin-for-pin equal binding under its own route_version is the honest
# representation. Typed open precondition riding this admission: the corner
# edge 50351<->50352 was never traversed in any retained witness of record
# and the stale bay's drive-through axis is unmeasured offline — its native
# connectivity resolves only under a later native route-read probe under
# its own explicit operator approval.
CARGOFLOW2_ROUTE_SECOND_ADMISSION = Cargoflow2RouteBinding(
    route_version=2,
    company=CARGOFLOW2_COMPANY,
    cargo=CARGOFLOW2_CARGO,
    pickup=CARGOFLOW2_PICKUP_TILE,
    pickup_front=CARGOFLOW2_PICKUP_FRONT_TILE,
    pickup_sid=CARGOFLOW2_PICKUP_SID,
    pickup_industry=CARGOFLOW2_PICKUP_IND,
    delivery=CARGOFLOW2_BAY_TILE,
    delivery_front=CARGOFLOW2_BAY_FRONT_TILE,
    bay_sid=CARGOFLOW2_BAY_SID,
    bay_industry=CARGOFLOW2_BAY_IND,
    depot=CARGOFLOW2_DEPOT_TILE,
    depot_front=CARGOFLOW2_DEPOT_FRONT_TILE,
    engine=CARGOFLOW2_ENGINE,
    engine_max_cost=CARGOFLOW2_ENGINE_MAX_COST,
    purchase_quote=CARGOFLOW2_PURCHASE_QUOTE,
    engine_running_display=CARGOFLOW2_RUNNING_DISPLAY,
    engine_capacity=CARGOFLOW2_CAPACITY,
    engine_max_speed=CARGOFLOW2_MAX_SPEED,
    order_pickup_flags=CARGOFLOW2_ORDER_PICKUP_FLAGS,
    order_delivery_flags=CARGOFLOW2_ORDER_DELIVERY_FLAGS,
    start_funds=CARGOFLOW2_START_FUNDS,
    founding_loan=CARGOFLOW2_FOUNDING_LOAN,
    interest_rate=CARGOFLOW2_INTEREST_RATE,
    station_fee=CARGOFLOW2_STATION_FEE,
    launch_day=CARGOFLOW2_LAUNCH_DAY,
    arrive_max_days=CARGOFLOW2_ARRIVE_MAX_DAYS,
    flow_span_days=CARGOFLOW2_SPAN_DAYS,
)

# The versioned binding map of record, keyed by route binding id. The map
# is the contract's own route registry: the plan gate and every derivation
# resolve through it, so an id never present here is an unknown route
# version everywhere, and no binding can be registered under an occupied
# id (a third admitted route takes the next id).
CARGOFLOW2_ROUTE_BINDINGS: dict[int, Cargoflow2RouteBinding] = {
    CARGOFLOW2_SCHEDULE_VERSION: CARGOFLOW2_ROUTE_OF_RECORD,
    CARGOFLOW2_ROUTE_SECOND_ADMISSION.route_version: CARGOFLOW2_ROUTE_SECOND_ADMISSION,
}

if (
    CARGOFLOW2_SCHEDULE_VERSION != 1
    or set(CARGOFLOW2_ROUTE_BINDINGS) != {1, 2}
    or CARGOFLOW2_ROUTE_BINDINGS[1] is not CARGOFLOW2_ROUTE_OF_RECORD
    or CARGOFLOW2_ROUTE_BINDINGS[2] is not CARGOFLOW2_ROUTE_SECOND_ADMISSION
    or CARGOFLOW2_ROUTE_OF_RECORD.route_version != 1
    or (CARGOFLOW2_ROUTE_OF_RECORD.company, CARGOFLOW2_ROUTE_OF_RECORD.cargo)
    != (CARGOFLOW2_COMPANY, CARGOFLOW2_CARGO)
    or (
        CARGOFLOW2_ROUTE_OF_RECORD.pickup,
        CARGOFLOW2_ROUTE_OF_RECORD.pickup_front,
        CARGOFLOW2_ROUTE_OF_RECORD.pickup_sid,
        CARGOFLOW2_ROUTE_OF_RECORD.pickup_industry,
    )
    != (
        CARGOFLOW2_PICKUP_TILE,
        CARGOFLOW2_PICKUP_FRONT_TILE,
        CARGOFLOW2_PICKUP_SID,
        CARGOFLOW2_PICKUP_IND,
    )
    or (
        CARGOFLOW2_ROUTE_OF_RECORD.delivery,
        CARGOFLOW2_ROUTE_OF_RECORD.delivery_front,
        CARGOFLOW2_ROUTE_OF_RECORD.bay_sid,
        CARGOFLOW2_ROUTE_OF_RECORD.bay_industry,
    )
    != (CARGOFLOW2_BAY_TILE, CARGOFLOW2_BAY_FRONT_TILE, CARGOFLOW2_BAY_SID, CARGOFLOW2_BAY_IND)
    or (CARGOFLOW2_ROUTE_OF_RECORD.depot, CARGOFLOW2_ROUTE_OF_RECORD.depot_front)
    != (CARGOFLOW2_DEPOT_TILE, CARGOFLOW2_DEPOT_FRONT_TILE)
    or (
        CARGOFLOW2_ROUTE_OF_RECORD.engine,
        CARGOFLOW2_ROUTE_OF_RECORD.engine_max_cost,
        CARGOFLOW2_ROUTE_OF_RECORD.purchase_quote,
        CARGOFLOW2_ROUTE_OF_RECORD.engine_running_display,
        CARGOFLOW2_ROUTE_OF_RECORD.engine_capacity,
        CARGOFLOW2_ROUTE_OF_RECORD.engine_max_speed,
    )
    != (
        CARGOFLOW2_ENGINE,
        CARGOFLOW2_ENGINE_MAX_COST,
        CARGOFLOW2_PURCHASE_QUOTE,
        CARGOFLOW2_RUNNING_DISPLAY,
        CARGOFLOW2_CAPACITY,
        CARGOFLOW2_MAX_SPEED,
    )
    or (
        CARGOFLOW2_ROUTE_OF_RECORD.order_pickup_flags,
        CARGOFLOW2_ROUTE_OF_RECORD.order_delivery_flags,
    )
    != (CARGOFLOW2_ORDER_PICKUP_FLAGS, CARGOFLOW2_ORDER_DELIVERY_FLAGS)
    or (
        CARGOFLOW2_ROUTE_OF_RECORD.start_funds,
        CARGOFLOW2_ROUTE_OF_RECORD.founding_loan,
        CARGOFLOW2_ROUTE_OF_RECORD.interest_rate,
        CARGOFLOW2_ROUTE_OF_RECORD.station_fee,
    )
    != (
        CARGOFLOW2_START_FUNDS,
        CARGOFLOW2_FOUNDING_LOAN,
        CARGOFLOW2_INTEREST_RATE,
        CARGOFLOW2_STATION_FEE,
    )
    or (
        CARGOFLOW2_ROUTE_OF_RECORD.launch_day,
        CARGOFLOW2_ROUTE_OF_RECORD.arrive_max_days,
        CARGOFLOW2_ROUTE_OF_RECORD.flow_span_days,
    )
    != (CARGOFLOW2_LAUNCH_DAY, CARGOFLOW2_ARRIVE_MAX_DAYS, CARGOFLOW2_SPAN_DAYS)
    or CARGOFLOW2_ROUTE_SECOND_ADMISSION.route_version != 2
    or (
        # The second admission carries the route of record's pinned
        # identities with only the binding id advanced (the candidate's
        # physical tile path lives in the derived evidence, never here).
        CARGOFLOW2_ROUTE_SECOND_ADMISSION.model_dump(exclude={"route_version"})
        != CARGOFLOW2_ROUTE_OF_RECORD.model_dump(exclude={"route_version"})
    )
):
    raise RuntimeError(
        "the corridor route-binding parameterization drifted from the route of record"
    )


def cargoflow2_route_binding(
    route_version: int = CARGOFLOW2_SCHEDULE_VERSION,
) -> Cargoflow2RouteBinding:
    """The registered route binding of one binding id; a foreign id refuses.

    The route of record (v1) is the DEFAULT: a derivation built with no
    binding argument resolves this selector, and its plan, schedule, pin
    table and funds model are byte-equal to the recorded composition.
    """
    if route_version not in CARGOFLOW2_ROUTE_BINDINGS:
        raise ValueError(
            f"no registered corridor route binding carries route binding id {route_version}"
        )
    return CARGOFLOW2_ROUTE_BINDINGS[route_version]


def cargoflow2_register_route_binding(binding: Cargoflow2RouteBinding) -> None:
    """Register one versioned route binding instance under its own id.

    The admission seam of the parameterization: a new admitted route
    binding takes the next unoccupied binding id that the plan version
    set spans (today 1 and 2; widening the set is a one-site change to
    that set, shared with the plan model). An occupied id refuses — a
    registered route binding is history of record once present, and a
    re-registration can never relabel it.
    """
    if binding.route_version in CARGOFLOW2_ROUTE_BINDINGS:
        raise ValueError(
            f"the corridor route binding id {binding.route_version} is already registered"
        )
    CARGOFLOW2_ROUTE_BINDINGS[binding.route_version] = binding


def cargoflow2_schedule_rows(binding: Cargoflow2RouteBinding) -> list[dict]:
    """The staged ladder rows of one route binding (design record §5.3).

    The fixed freight-family instrument chain runs first (``site-00`` …
    ``arrive-00``), then the twelve flow rows at their exact pinned ladder
    offsets 0..55, then the two tail rows in the binding's own flow-11
    economy day. The rows derive the same equality-gated ladder geometry
    for every binding — ids, ops and offsets are the shared instrument of
    record — while the watch bound and the tail economy day come from the
    binding itself; a binding that does not ride the pinned ladder
    refuses, so a route's schedule can never be mixed with another
    binding's boundaries.
    """
    if (
        binding.flow_span_days != CARGOFLOW2_FLOW_OFFSETS[-1]
        or binding.arrive_max_days + binding.flow_span_days != CARGOFLOW2_DAY_BUDGET
    ):
        raise ValueError("the route binding does not ride the equality-gated ladder of record")
    schedule: list[dict] = []
    for exchange in CARGOFLOW2_EXCHANGE_IDS:
        op = _CARGOFLOW2_OP_BY_ID[exchange]
        row = dict(exchange=exchange, op=op, offset=-1)
        if op == "flow":
            row["offset"] = int(CARGOFLOW2_FLOW_OFFSETS[int(exchange.rsplit("-", 1)[1])])
        elif op in ("finance", "finish"):
            row["offset"] = int(binding.flow_span_days)
        elif op == "order":
            row["order_index"] = 0 if exchange == "order-00" else 1
        elif op == "arrive-watch":
            row["watch_days"] = int(binding.arrive_max_days)
        schedule.append(row)
    if (
        [row["exchange"] for row in schedule] != list(CARGOFLOW2_EXCHANGE_IDS)
        or len(schedule) != PLANNED_CARGOFLOW2_EXCHANGES
        or [row["offset"] for row in schedule if row["op"] == "flow"]
        != list(CARGOFLOW2_FLOW_OFFSETS)
        or [row["offset"] for row in schedule if row["op"] in ("finance", "finish")]
        != [int(binding.flow_span_days)] * 2
        or [row["order_index"] for row in schedule if row["op"] == "order"] != [0, 1]
        or [row["watch_days"] for row in schedule if row["op"] == "arrive-watch"]
        != [int(binding.arrive_max_days)]
        or any(row["op"] not in CARGOFLOW2_OPS for row in schedule)
    ):
        raise RuntimeError("the route binding's staged schedule drifted from the ladder of record")
    return schedule


def cargoflow2_pin_table(binding: Cargoflow2RouteBinding) -> dict[str, int]:
    """The binding-sourced pin rows of one route binding.

    Exactly the pin-table members the shipped attempt GameScript composes
    from route identity (the pin-table binding test of record binds the
    shipped table to the default binding's rows): the corridor stop/depot
    tiles, the station and industry identities, the company/cargo/engine
    census and authority pins, the order flags, and the clock pins with
    their two derived boundaries. A different binding derives its own
    values; nothing here re-derives a foreign binding's pins.
    """
    return dict(
        pickup=int(binding.pickup),
        delivery=int(binding.delivery),
        depot_tile=int(binding.depot),
        PICKUP_SID=int(binding.pickup_sid),
        BAY_SID=int(binding.bay_sid),
        PICKUP_IND=int(binding.pickup_industry),
        BAY_IND=int(binding.bay_industry),
        CARGOFLOW2_COMPANY=int(binding.company),
        CARGOFLOW2_CARGO=int(binding.cargo),
        ENGINE_PIN=int(binding.engine),
        ENGINE_QUOTE=int(binding.purchase_quote),
        ENGINE_MAX_COST=int(binding.engine_max_cost),
        CAPACITY_PIN=int(binding.engine_capacity),
        SPEED_PIN=int(binding.engine_max_speed),
        RUNNING_DISPLAY_PIN=int(binding.engine_running_display),
        OF_NONE=int(binding.order_pickup_flags),
        OF_NO_LOAD=int(binding.order_delivery_flags),
        LAUNCH_DAY=int(binding.launch_day),
        ARRIVE_MAX_DAYS=int(binding.arrive_max_days),
        ARRIVE_DEADLINE=int(binding.launch_day) + int(binding.arrive_max_days),
        AUTHORITY_LAST_DAY=int(binding.launch_day) + CARGOFLOW2_DAY_BUDGET,
    )


class Cargoflow2Latch(Contract):
    """One latched cycle event of record with its own (day, tick) instant."""

    kind: Cargoflow2LatchKind
    day: Cargoflow2Clock
    tick: Cargoflow2Clock
    cargo: Cargoflow2Amount


class Cargoflow2Plan(Contract):
    """The pinned identities, schedule and financial-model pins of one attempt.

    The plan binds the depot-chain world of record exactly as the dispatch
    probe's plan does, plus this round's fixed instrument chain, the twelve
    flow samples, the two tail exchanges, and the financial-model pins the
    zero-residual fence reconciles against (§4.1). The version field
    selects one registered route binding (the route of record is v1, the
    DEFAULT): every route-derived pin validates against that binding's own
    values, so a plan carrying one binding's pins under another binding's
    version label refuses here — cross-version composition drift fails
    closed before any derived value can lean on it. The optional
    ``schedule_version`` arm field names the delivered extension: a plan
    that names it must be the second admission's own (2, 2) composition
    (26 planned exchanges inside the 65-economy-day delivered authority);
    with it absent the plan rides the v1 envelope of record byte-exactly.
    """

    schema_version: Literal[1, 2] = 1
    company: CompanyID
    cargo: Annotated[StrictInt, Field(ge=0, le=63)]
    pickup: TileID
    pickup_front: TileID
    delivery: TileID
    delivery_front: TileID
    depot: TileID
    depot_front: TileID
    pickup_sid: Annotated[StrictInt, Field(ge=0, le=65535)]
    bay_sid: Annotated[StrictInt, Field(ge=0, le=65535)]
    pickup_industry: Annotated[StrictInt, Field(ge=0, le=65535)]
    bay_industry: Annotated[StrictInt, Field(ge=0, le=65535)]
    engine: Cargoflow2ActorId
    start_funds: Money
    purchase_quote: Money
    founding_loan: Money
    interest_rate: Annotated[StrictInt, Field(ge=0, le=100)]
    station_fee: Money
    launch_day: Cargoflow2Clock
    arrive_max_days: Annotated[StrictInt, Field(ge=1, le=CARGOFLOW2_DAY_BUDGET)]
    flow_span_days: Annotated[StrictInt, Field(ge=1, le=CARGOFLOW2_DAY_BUDGET)]
    schedule: tuple[StrictStr, ...]
    schedule_version: Annotated[StrictInt, Field(ge=1)] | None = None
    request_budget: Annotated[StrictInt, Field(gt=0, le=CARGOFLOW2_REQUEST_BUDGET)] = (
        CARGOFLOW2_REQUEST_BUDGET
    )
    # The field bound only trims absurd values; the arm fences below carry
    # the exact 60/65 authority of record.
    day_budget: Annotated[StrictInt, Field(ge=1, le=DAYS_IN_ECONOMY_YEAR)] = CARGOFLOW2_DAY_BUDGET

    @property
    def digest(self) -> str:
        return hashlib.sha256(_cargoflow2_canonical_bytes(self)).hexdigest()

    @model_validator(mode="after")
    def coherent(self) -> Cargoflow2Plan:
        binding = CARGOFLOW2_ROUTE_BINDINGS.get(self.schema_version)
        if binding is None:
            raise ValueError(
                f"no registered corridor route binding carries plan version {self.schema_version}"
            )
        if self.company != binding.company or self.cargo != binding.cargo:
            raise ValueError("the delivery attempt observes company 0 with cargo 1")
        if (self.pickup, self.pickup_front) != (binding.pickup, binding.pickup_front):
            raise ValueError("pickup pins drifted from the depot-chain corridor")
        if (self.delivery, self.delivery_front) != (binding.delivery, binding.delivery_front):
            raise ValueError("bay pins drifted from the depot-chain corridor")
        if (self.depot, self.depot_front) != (binding.depot, binding.depot_front):
            raise ValueError("depot pins drifted from the depot-chain corridor")
        if self.pickup_sid != binding.pickup_sid or self.bay_sid != binding.bay_sid:
            raise ValueError("station identities drifted from the pinned record sids")
        if (
            self.pickup_industry != binding.pickup_industry
            or self.bay_industry != binding.bay_industry
        ):
            raise ValueError("industry identities drifted from the census receipt rows")
        if self.engine != binding.engine:
            raise ValueError("the plan binds the provisional engine pin exactly")
        if self.start_funds != binding.start_funds:
            raise ValueError("start funds drifted from the depot-mutation close pin")
        if (
            self.purchase_quote != binding.purchase_quote
            or self.founding_loan != binding.founding_loan
            or self.interest_rate != binding.interest_rate
            or self.station_fee != binding.station_fee
        ):
            raise ValueError("financial-model pins drifted from the §4.1 table")
        if self.launch_day != binding.launch_day:
            raise ValueError("launch day drifted from the pinned clock of record")
        if self.arrive_max_days != binding.arrive_max_days:
            raise ValueError("the arrival bound drifted from its pinned 5 days")
        if self.schedule_version == CARGOFLOW2_DELIVERED_SCHEDULE_VERSION:
            if self.schema_version != CARGOFLOW2_ROUTE_SECOND_ADMISSION.route_version:
                raise ValueError(
                    "the delivered composition rides the second admitted route's (2, 2) pairing"
                )
            if self.flow_span_days != CARGOFLOW2_DELIVERED_SPAN_DAYS:
                raise ValueError("flow span drifted from the pinned 60-day delivered ladder")
            if self.schedule != CARGOFLOW2_DELIVERED_EXCHANGE_IDS:
                raise ValueError("schedule drifted from the planned 26 exchanges")
        elif self.flow_span_days != binding.flow_span_days:
            raise ValueError("flow span drifted from the pinned 55-day ladder")
        elif self.schedule != CARGOFLOW2_EXCHANGE_IDS:
            raise ValueError("schedule drifted from the planned 25 exchanges")
        if self.pickup_sid == self.bay_sid:
            raise ValueError("the two observed stops must carry distinct station ids")
        if self.pickup_industry == self.bay_industry:
            raise ValueError("the two observed industries must be distinct")
        if self.schedule_version == CARGOFLOW2_DELIVERED_SCHEDULE_VERSION:
            if self.day_budget != CARGOFLOW2_DELIVERED_DAY_BUDGET:
                raise ValueError(
                    "a delivered attempt carries the 65-economy-day authority of record"
                )
        else:
            if self.day_budget != CARGOFLOW2_DAY_BUDGET:
                raise ValueError("a v1 attempt carries the 60-day authority of record")
        if self.arrive_max_days + self.flow_span_days > self.day_budget:
            raise ValueError(
                "the arrival bound plus flow span must fit the 60-day attempt authority"
            )
        return self


def cargoflow2_plan(
    binding: Cargoflow2RouteBinding | None = None,
) -> Cargoflow2Plan:
    """The pinned D5-CARGOFLOW-2 plan of one corridor route binding.

    The DEFAULT (no binding named) derives from the route of record, whose
    binding is built from this module's own pins — byte-equal to the plan
    of record. Any registered binding derives its own versioned plan; an
    unregistered binding id refuses at the map lookup.
    """
    resolved = binding if binding is not None else cargoflow2_route_binding()
    return Cargoflow2Plan(
        schema_version=resolved.route_version,
        company=resolved.company,
        cargo=resolved.cargo,
        pickup=resolved.pickup,
        pickup_front=resolved.pickup_front,
        delivery=resolved.delivery,
        delivery_front=resolved.delivery_front,
        depot=resolved.depot,
        depot_front=resolved.depot_front,
        pickup_sid=resolved.pickup_sid,
        bay_sid=resolved.bay_sid,
        pickup_industry=resolved.pickup_industry,
        bay_industry=resolved.bay_industry,
        engine=resolved.engine,
        start_funds=resolved.start_funds,
        purchase_quote=resolved.purchase_quote,
        founding_loan=resolved.founding_loan,
        interest_rate=resolved.interest_rate,
        station_fee=resolved.station_fee,
        launch_day=resolved.launch_day,
        arrive_max_days=resolved.arrive_max_days,
        flow_span_days=resolved.flow_span_days,
        schedule=CARGOFLOW2_EXCHANGE_IDS,
    )


def cargoflow2_delivered_plan(
    binding: Cargoflow2RouteBinding | None = None,
) -> Cargoflow2Plan:
    """The delivered 26-row plan of record, keyed by the (2, 2) pairing.

    The delivered arm of the second admitted route: the (2, 1) v1-row
    derivation above stays byte-equal, and this factory derives its own
    composition — the 26-row delivered ladder with schedule_version 2
    inside the 65-economy-day day budget (the settle margin that gives the
    cycle its own completion stop). The binding that names any other
    route id, and the default arm's route, never borrow it: the delivered
    extension rides the second admission alone.
    """
    resolved = (
        binding
        if binding is not None
        else cargoflow2_route_binding(CARGOFLOW2_ROUTE_SECOND_ADMISSION.route_version)
    )
    if resolved.route_version != CARGOFLOW2_ROUTE_SECOND_ADMISSION.route_version:
        raise ValueError("the delivered plan rides the second admitted route's (2, 2) pairing")
    return Cargoflow2Plan(
        schema_version=resolved.route_version,
        company=resolved.company,
        cargo=resolved.cargo,
        pickup=resolved.pickup,
        pickup_front=resolved.pickup_front,
        delivery=resolved.delivery,
        delivery_front=resolved.delivery_front,
        depot=resolved.depot,
        depot_front=resolved.depot_front,
        pickup_sid=resolved.pickup_sid,
        bay_sid=resolved.bay_sid,
        pickup_industry=resolved.pickup_industry,
        bay_industry=resolved.bay_industry,
        engine=resolved.engine,
        start_funds=resolved.start_funds,
        purchase_quote=resolved.purchase_quote,
        founding_loan=resolved.founding_loan,
        interest_rate=resolved.interest_rate,
        station_fee=resolved.station_fee,
        launch_day=resolved.launch_day,
        arrive_max_days=resolved.arrive_max_days,
        flow_span_days=CARGOFLOW2_DELIVERED_SPAN_DAYS,
        schedule=CARGOFLOW2_DELIVERED_EXCHANGE_IDS,
        schedule_version=CARGOFLOW2_DELIVERED_SCHEDULE_VERSION,
        day_budget=CARGOFLOW2_DELIVERED_DAY_BUDGET,
    )


def cargoflow2_delivered_schedule_rows(
    binding: Cargoflow2RouteBinding,
) -> list[dict]:
    """The delivered ladder rows of the (2, 2) pairing (design record §5.3).

    The fixed instrument chain runs first (``site-00`` … ``arrive-00``),
    then the thirteen flow rows at their pinned delivered offsets 0..60
    (``flow-12`` at anchor+60, the settle margin), then the two tail rows
    in the delivered span's own economy day. The rows derive their keys
    from the (2, 2) pairing of record; a binding of any other pairing
    refuses, so a delivered schedule can never be composed from a foreign
    arm's boundaries.
    """
    if (
        binding.route_version != CARGOFLOW2_ROUTE_SECOND_ADMISSION.route_version
        or binding.flow_span_days != CARGOFLOW2_FLOW_OFFSETS[-1]
        or binding.arrive_max_days + binding.flow_span_days != CARGOFLOW2_DAY_BUDGET
    ):
        raise ValueError(
            "the delivered ladder rows ride the second admitted route's (2, 2) pairing"
        )
    schedule: list[dict] = []
    for exchange in CARGOFLOW2_DELIVERED_EXCHANGE_IDS:
        op = _CARGOFLOW2_DELIVERED_OP_BY_ID[exchange]
        row = dict(exchange=exchange, op=op, offset=-1)
        if op == "flow":
            row["offset"] = int(CARGOFLOW2_DELIVERED_FLOW_OFFSETS[int(exchange.rsplit("-", 1)[1])])
        elif op in ("finance", "finish"):
            row["offset"] = int(CARGOFLOW2_DELIVERED_TAIL_OFFSET)
        elif op == "order":
            row["order_index"] = 0 if exchange == "order-00" else 1
        elif op == "arrive-watch":
            row["watch_days"] = int(binding.arrive_max_days)
        schedule.append(row)
    if (
        [row["exchange"] for row in schedule] != list(CARGOFLOW2_DELIVERED_EXCHANGE_IDS)
        or len(schedule) != PLANNED_CARGOFLOW2_DELIVERED_EXCHANGES
        or [row["offset"] for row in schedule if row["op"] == "flow"]
        != list(CARGOFLOW2_DELIVERED_FLOW_OFFSETS)
        or [row["offset"] for row in schedule if row["op"] in ("finance", "finish")]
        != [int(CARGOFLOW2_DELIVERED_TAIL_OFFSET)] * 2
        or [row["order_index"] for row in schedule if row["op"] == "order"] != [0, 1]
        or [row["watch_days"] for row in schedule if row["op"] == "arrive-watch"]
        != [int(binding.arrive_max_days)]
        or any(row["op"] not in CARGOFLOW2_OPS for row in schedule)
    ):
        raise RuntimeError("the delivered schedule drifted from its pinned ladder composition")
    return schedule


class Cargoflow2Request(Contract):
    """One protocol-11 exchange request (fixed correlation stride).

    Every request carries the corridor identity pins (the native handler
    refuses a drifted pin before any observation), the uniform ``plan`` seal
    digest and its op's phase echoes — the freight-family fixed op semantics
    ported verbatim in meaning (§5.2). ``max_cost`` is 0 everywhere except
    the quote-first purchase, which carries the pinned quote within the
    £5,000 ceiling of record.
    """

    protocol: Literal[11] = 11
    op: Cargoflow2Op
    request_id: Annotated[str, Field(pattern=r"^[a-z0-9-]{1,32}$")]
    plan: Digest
    company: CompanyID
    max_cost: Money
    pickup: TileID
    delivery: TileID
    depot: TileID
    engine: Cargoflow2ActorId = -1
    vehicle: Cargoflow2ActorId = -1
    expected_cost: Money = 0
    order_index: Cargoflow2OrderIndex = -1
    order_flags: Cargoflow2EchoFlags = -1
    watch_days: Cargoflow2WatchDays = -1
    offset: Cargoflow2EchoOffset = -1
    # The arm key of record: absent = the v1 envelope of record, 2 = the
    # delivered (2, 2) pairing. The shipped handler checks only the named
    # correlation members and tolerates this extra member.
    schedule_version: Annotated[StrictInt, Field(ge=1)] | None = None

    @model_validator(mode="after")
    def coherent(self) -> Cargoflow2Request:
        delivered = self.schedule_version == CARGOFLOW2_DELIVERED_SCHEDULE_VERSION
        quiet = (
            self.expected_cost == 0
            and self.order_index == -1
            and self.order_flags == -1
            and self.watch_days == -1
            and self.offset == -1
        )
        pitched = self.engine >= 0 and self.vehicle >= 0
        if self.op == "site":
            if self.engine != -1 or self.vehicle != -1 or not quiet:
                raise ValueError("site requests carry no engine, vehicle or phase echoes")
            return self
        elif self.engine != CARGOFLOW2_ENGINE:
            raise ValueError("every non-site request ships the pinned engine identity")
        if self.op == "engine":
            if self.vehicle != -1 or not quiet:
                raise ValueError("engine requests carry no vehicle or phase echoes")
        elif self.op == "purchase":
            if (
                self.vehicle != -1
                or self.order_index != -1
                or self.order_flags != -1
                or self.watch_days != -1
                or self.offset != -1
            ):
                raise ValueError("purchase request must present no phase echoes")
            if self.expected_cost != CARGOFLOW2_PURCHASE_QUOTE:
                raise ValueError("purchase request carries its pinned tested quote")
            if self.max_cost != CARGOFLOW2_ENGINE_MAX_COST:
                raise ValueError("purchase request carries the authority cost ceiling")
        elif self.op == "vread":
            if not pitched or not quiet:
                raise ValueError("vread echoes the pinned engine and live vehicle")
        elif self.op == "order":
            wanted_flags = (
                CARGOFLOW2_ORDER_PICKUP_FLAGS
                if self.order_index == 0
                else CARGOFLOW2_ORDER_DELIVERY_FLAGS
            )
            if (
                not pitched
                or self.order_index not in (0, 1)
                or self.expected_cost != 0
                or self.watch_days != -1
                or self.offset != -1
                or self.order_flags != wanted_flags
            ):
                raise ValueError("order requests pin one stop index with its pinned order flags")
        elif self.op == "arrive-watch":
            if (
                not pitched
                or self.order_index != -1
                or self.watch_days != CARGOFLOW2_ARRIVE_MAX_DAYS
                or self.offset != -1
                or self.expected_cost != 0
            ):
                raise ValueError("arrive-watch echoes the vehicle identity and its 5-day bound")
        elif self.op in ("finance", "finish"):
            tail_offset = CARGOFLOW2_DELIVERED_TAIL_OFFSET if delivered else CARGOFLOW2_TAIL_OFFSET
            tail_day = "flow-12" if delivered else "flow-11"
            if (
                not pitched
                or self.expected_cost != 0
                or self.watch_days != -1
                or self.order_index != -1
                or self.order_flags != -1
                or self.offset != tail_offset
            ):
                raise ValueError(
                    f"{self.op} echoes the vehicle identity and ladder step "
                    f"{tail_offset} (the {tail_day} economy day of record)"
                )
        elif self.op == "flow":
            if (
                not pitched
                or self.order_index != -1
                or self.expected_cost != 0
                or self.watch_days != -1
            ):
                raise ValueError("flow echoes the vehicle identity and its ladder step")
            flow_offsets = _cargoflow2_arm_offset_map(self.schedule_version)
            if (
                self.request_id not in flow_offsets
                or self.offset != (flow_offsets[self.request_id])
            ):
                raise ValueError("flow offset drifted from its planned ladder step")
        else:  # "order-read", "monitor", "start", "finance", "finish"
            if not pitched or not quiet:
                raise ValueError(f"{self.op} echoes the vehicle identity only")
        return self

    def to_bytes(self) -> bytes:
        raw = _cargoflow2_canonical_bytes(self)
        if len(raw) > MAX_CARGOFLOW2_REQUEST_BYTES:
            raise ValueError(f"cargo-flow 2 request exceeds {MAX_CARGOFLOW2_REQUEST_BYTES} bytes")
        return raw


_FEATURE_NAMES = (
    "stock_pickup",
    "stock_bay",
    "wait_pickup",
    "wait_pickup_from0",
    "wait_pickup_from1",
    "wait_bay",
    "wait_bay_from0",
    "wait_bay_from1",
    "count_pickup",
    "count_bay",
    "planned_pickup_from0",
    "planned_pickup_from1",
    "planned_bay_from0",
    "planned_bay_from1",
    "prod_pickup",
    "prod_bay",
    "trans_pickup",
    "trans_bay",
)

# Every observation field of the readback, in bridge-attach order (the
# phase echo fields — engine/vehicle/expected_cost/order/watch/offset and
# the universal income/funds/cost — are checked separately, and the per-op
# success subsets are strict).
_CARGOFLOW2_FIELDS = (
    "anchor",
    "tick",
    "day",
    "year",
    "month",
    "day_of_month",
    # the site-census echoes (main.nut attaches them verbatim on site-00)
    "pickup_sid",
    "bay_sid",
    "pickup_industry",
    "bay_industry",
    *_FEATURE_NAMES,
    "location",
    "state",
    "in_depot",
    "speed",
    "load",
    "capacity",
    "cargo",
    "owner",
    "price",
    "max_speed",
    "running_cost",
    "order_len",
    "dest0",
    "flags0",
    "goto0",
    "dest1",
    "flags1",
    "goto1",
    "dest",
    "flags",
    "goto",
    "pickup_amount",
    "delivery_amount",
    "delivered",
    "last_accepted",
    "stop_issued",
    "latches",
)

_CARGOFLOW2_SUBSETS: dict[Cargoflow2Op, frozenset[str]] = {
    "site": frozenset(("cargo", "pickup_sid", "bay_sid", "pickup_industry", "bay_industry")),
    "engine": frozenset(("cargo", "capacity", "price", "max_speed", "running_cost")),
    "purchase": frozenset(),
    "vread": frozenset(
        ("owner", "location", "capacity", "cargo", "state", "in_depot", "speed", "load")
    ),
    "order": frozenset(("dest", "flags", "goto")),
    "order-read": frozenset(("order_len", "dest0", "flags0", "goto0", "dest1", "flags1", "goto1")),
    "monitor": frozenset(("pickup_amount", "delivery_amount")),
    "start": frozenset(("state", "speed")),
    "arrive-watch": frozenset(("anchor", "location", "load", "latches")),
    "flow": frozenset(
        (
            "anchor",
            "year",
            "month",
            "day_of_month",
            *_FEATURE_NAMES,
            "location",
            "load",
            "in_depot",
            "speed",
            "delivered",
            "latches",
        )
    ),
    "finance": frozenset(("anchor", "delivered", "last_accepted")),
    "finish": frozenset(("anchor", "state", "speed", "in_depot", "stop_issued")),
}
_CARGOFLOW2_POST_PURCHASE_OPS = (
    "vread",
    "order",
    "order-read",
    "monitor",
    "start",
    "arrive-watch",
    "flow",
    "finance",
    "finish",
)


class Cargoflow2Readback(Contract):
    """One protocol-11 exchange response (strict per-op field subsets).

    The handler echoes the request correlation keys, ``funds``, its op's
    quarter income and a status literal (§4.2 item 6: the income read rides
    every exchange from ``site-00`` onward, at the same observation
    instant). Success frames carry the complete op subset plus the
    observation instant (tick, day; §4.5's own fix). Refusal frames carry
    none of the observation set; the window-echo family carries exactly its
    three ladder echoes. Latch arrays above the bound refuse the exchange —
    they are never truncated to fit (§5.3).
    """

    protocol: Literal[11] = 11
    op: Cargoflow2Op
    request_id: str
    plan: Digest
    company: CompanyID
    max_cost: Money
    pickup: TileID
    delivery: TileID
    depot: TileID
    engine: Cargoflow2ActorId = -1
    vehicle: Cargoflow2ActorId = -1
    expected_cost: Money = 0
    order_index: Cargoflow2OrderIndex = -1
    order_flags: Cargoflow2EchoFlags = -1
    watch_days: Cargoflow2WatchDays = -1
    offset: Cargoflow2EchoOffset = -1
    status: Cargoflow2Status
    funds: SignedMoney
    cost: Money
    income: SignedMoney | None = None
    # The correlated arm key of record — never echoed by the handler's
    # response composer (its ``r`` table copies explicit keys only), so
    # ``parse_for`` injects the request's own arm before validation and a
    # disagreeing raw frame refuses.
    schedule_version: Annotated[StrictInt, Field(ge=1)] | None = None

    anchor: Cargoflow2Clock | None = None
    tick: Cargoflow2Clock | None = None
    day: Cargoflow2Clock | None = None
    year: Cargoflow2Clock | None = None
    month: Annotated[StrictInt, Field(ge=1, le=12)] | None = None
    day_of_month: Annotated[StrictInt, Field(ge=1, le=31)] | None = None
    # The site-census echo fields of record (§5.2): the handler attaches the
    # pinned station and industry ids verbatim on site-00 and strips them
    # over the catch path like every other observation.
    pickup_sid: Annotated[StrictInt, Field(ge=0, le=65535)] | None = None
    bay_sid: Annotated[StrictInt, Field(ge=0, le=65535)] | None = None
    pickup_industry: Annotated[StrictInt, Field(ge=0, le=65535)] | None = None
    bay_industry: Annotated[StrictInt, Field(ge=0, le=65535)] | None = None
    stock_pickup: Annotated[StrictInt, Field(ge=-1, le=65535)] | None = None
    stock_bay: Annotated[StrictInt, Field(ge=-1, le=65535)] | None = None
    wait_pickup: Cargoflow2Amount | None = None
    wait_pickup_from0: Cargoflow2Amount | None = None
    wait_pickup_from1: Cargoflow2Amount | None = None
    wait_bay: Cargoflow2Amount | None = None
    wait_bay_from0: Cargoflow2Amount | None = None
    wait_bay_from1: Cargoflow2Amount | None = None
    count_pickup: Cargoflow2Amount | None = None
    count_bay: Cargoflow2Amount | None = None
    planned_pickup_from0: Cargoflow2Amount | None = None
    planned_pickup_from1: Cargoflow2Amount | None = None
    planned_bay_from0: Cargoflow2Amount | None = None
    planned_bay_from1: Cargoflow2Amount | None = None
    prod_pickup: Annotated[StrictInt, Field(ge=-1, le=2147483647)] | None = None
    prod_bay: Annotated[StrictInt, Field(ge=-1, le=2147483647)] | None = None
    trans_pickup: Annotated[StrictInt, Field(ge=-1, le=2147483647)] | None = None
    trans_bay: Annotated[StrictInt, Field(ge=-1, le=2147483647)] | None = None
    location: TileID | None = None
    state: Cargoflow2VehicleState | None = None
    in_depot: StrictBool | None = None
    speed: Cargoflow2Amount | None = None
    load: Cargoflow2Amount | None = None
    capacity: Cargoflow2Amount | None = None
    cargo: Annotated[StrictInt, Field(ge=0, le=63)] | None = None
    owner: Annotated[StrictInt, Field(ge=-1, le=65535)] | None = None
    running_cost: Annotated[StrictInt, Field(ge=1, le=2147483647)] | None = None
    # The engine-census echo fields of record (the §5.2 pinned admission):
    # the handler re-derives them fail-closed and the readback carries them
    # verbatim beside the running cost (E111: the script value is the
    # per-economy-year display figure).
    price: Money | None = None
    max_speed: Annotated[StrictInt, Field(ge=0, le=2147483647)] | None = None
    order_len: Annotated[StrictInt, Field(ge=0, le=65535)] | None = None
    dest0: TileID | None = None
    flags0: Annotated[StrictInt, Field(ge=0, le=255)] | None = None
    goto0: StrictBool | None = None
    dest1: TileID | None = None
    flags1: Annotated[StrictInt, Field(ge=0, le=255)] | None = None
    goto1: StrictBool | None = None
    dest: TileID | None = None
    flags: Annotated[StrictInt, Field(ge=0, le=255)] | None = None
    goto: StrictBool | None = None
    pickup_amount: Cargoflow2Amount | None = None
    delivery_amount: Cargoflow2Amount | None = None
    delivered: Cargoflow2Amount | None = None
    last_accepted: Cargoflow2SignedClock | None = None
    stop_issued: StrictBool | None = None
    latches: tuple[Cargoflow2Latch, ...] | None = Field(None, max_length=CARGOFLOW2_LATCH_LIMIT)

    @property
    def digest(self) -> str:
        return hashlib.sha256(_cargoflow2_canonical_bytes(self)).hexdigest()

    @classmethod
    def parse_for(cls, request: Cargoflow2Request, raw: bytes):
        if len(raw) > MAX_CARGOFLOW2_RESPONSE_BYTES:
            raise ValueError(f"cargo-flow 2 response exceeds {MAX_CARGOFLOW2_RESPONSE_BYTES} bytes")

        def unique(pairs):
            result = {}
            for key, value in pairs:
                if key in result:
                    raise ValueError("duplicate response key")
                result[key] = value
            return result

        value = json.loads(raw, object_pairs_hook=unique)
        # The wire frame is JSON: its single array-of-objects member arrives
        # as a list, so parse plane normalizes it to the latch tuples.
        if isinstance(value.get("latches"), list):
            value["latches"] = tuple(value["latches"])
        # The response composer never carries the arm key, so the readback
        # inherits the correlated request's arm before validation.
        if request.schedule_version is not None:
            value.setdefault("schedule_version", request.schedule_version)
        criteria = cls.model_validate(value)
        # phase echoes — engine, vehicle, expected_cost, order/flags/watch —
        # are NOT echoed-and-compared here, because the reply legitimately
        # decides some of them (the built purchase names the vehicle id the
        # pre-vehicle request could not carry). Every one of those echoes is
        # instead const-pinned per op position in coherent()'s
        # _check_echo_coherence against the plan constants — a hard
        # equality, not a request reflection.
        correlated = ("protocol", "op", "request_id", "plan", "company", "max_cost", "offset")
        if any(getattr(criteria, k) != getattr(request, k) for k in correlated):
            raise ValueError("cargo-flow 2 response correlation mismatch")
        for key in ("pickup", "delivery", "depot"):
            if getattr(criteria, key) != getattr(request, key):
                raise ValueError("cargo-flow 2 response pin mismatch")
        if criteria.schedule_version != request.schedule_version:
            raise ValueError("cargo-flow 2 response arm mismatch")
        return criteria

    @model_validator(mode="after")
    def coherent(self) -> Cargoflow2Readback:
        if self.op not in _CARGOFLOW2_SUCCESS_STATUS:
            raise ValueError("unknown cargo-flow 2 op")
        subset = _CARGOFLOW2_SUBSETS[self.op]
        present = {field for field in _CARGOFLOW2_FIELDS if getattr(self, field) is not None}
        income_present = self.income is not None
        status = self.status
        if status == _CARGOFLOW2_SUCCESS_STATUS[self.op]:
            outside = present - subset - {"tick", "day"}
            if outside:
                raise ValueError(
                    f"{self.op} readback carries fields outside its subset: {sorted(outside)}"
                )
            missing = subset - present
            if missing:
                raise ValueError(f"{self.op} success readback lacks {sorted(missing)}")
            if self.tick is None or self.day is None or not income_present:
                raise ValueError(
                    "every success frame echoes its observation instant and income read"
                )
            self._check_ladder_clock()
        elif status in _CARGOFLOW2_WINDOW_ECHO_STATUS:
            if self.op != "flow":
                raise ValueError("the window echo family belongs to flow exchanges")
            outside_window = present - set(_CARGOFLOW2_WINDOW_ECHO_FIELDS)
            if outside_window or income_present:
                raise ValueError(
                    f"{status} carries fields outside its window echo subset: "
                    f"{sorted(outside_window)}"
                )
        elif status in _CARGOFLOW2_REFUSAL_STATUS:
            if present or income_present:
                raise ValueError("refusal readback carries an unclaimed observation set")
        else:
            raise ValueError("unknown cargo-flow 2 status")
        self._check_echo_coherence()
        return self

    def _check_ladder_clock(self) -> None:
        """Ladder arithmetic of record: flow steps and tail share the anchor."""
        expected = _cargoflow2_arm_offset_map(self.schedule_version).get(self.request_id)
        if self.op in ("flow", "finance", "finish"):
            if expected is None:
                raise ValueError(
                    f"ladder readback id {self.request_id} is not a planned exchange of its own arm"
                )
            if self.anchor is None or self.day is None:
                raise ValueError("a ladder readback must carry its anchored clock")
            if self.day - self.anchor != expected:
                raise ValueError(
                    f"ladder day diverged: day - anchor = {self.day - self.anchor}, "
                    f"planned ladder step {expected}"
                )

    def _check_echo_coherence(self) -> None:
        """Phase-echo coherence by op position in the attempt."""
        if self.op == "site":
            if self.engine != -1 or self.vehicle != -1:
                raise ValueError("site readback must not name an engine or vehicle")
            if self.status == "READY" and self.cargo != CARGOFLOW2_CARGO:
                raise ValueError("the site readback re-pins the corridor cargo")
            if self.status == "READY" and (self.pickup_sid, self.bay_sid) != (
                CARGOFLOW2_PICKUP_SID,
                CARGOFLOW2_BAY_SID,
            ):
                raise ValueError("the site readback re-pins the corridor station ids")
            if self.status == "READY" and (self.pickup_industry, self.bay_industry) != (
                CARGOFLOW2_PICKUP_IND,
                CARGOFLOW2_BAY_IND,
            ):
                raise ValueError("the site readback re-pins the corridor industries")
        elif self.op == "engine":
            if self.vehicle != -1:
                raise ValueError("engine readback must not name a vehicle")
            if self.status == "READY":
                if self.engine != CARGOFLOW2_ENGINE:
                    raise ValueError("engine readback must name the pinned engine")
                if self.cargo != CARGOFLOW2_CARGO or self.capacity != CARGOFLOW2_CAPACITY:
                    raise ValueError("the engine readback echoes its census facts")
                if self.price != CARGOFLOW2_PURCHASE_QUOTE:
                    raise ValueError("the engine readback echoes its pinned price")
                # The success-field-subset check above refuses an engine
                # frame without its running cost; assert for the check.
                # E111: the script surface returns the display figure, so
                # the pin comparison applies no second shift — a 256-scaled
                # raw is script-unreachable and refuses here of record.
                assert self.running_cost is not None
                if self.running_cost != CARGOFLOW2_RUNNING_DISPLAY:
                    raise ValueError("the engine running cost disagrees with its display figure")
        elif self.op == "purchase":
            if self.order_index != -1 or self.watch_days != -1 or self.offset != -1:
                raise ValueError("purchase readback must not carry phase echoes")
            if self.status == "BUILT":
                if self.engine != CARGOFLOW2_ENGINE or self.vehicle < 0:
                    raise ValueError("built purchase must name the pinned engine and vehicle")
                if self.cost != CARGOFLOW2_PURCHASE_QUOTE:
                    raise ValueError("built purchase must cost its pinned quote")
            elif self.status in _CARGOFLOW2_REFUSAL_STATUS and self.vehicle != -1:
                raise ValueError("refused purchase must not name a vehicle")
        elif self.op in _CARGOFLOW2_POST_PURCHASE_OPS:
            if self.engine != CARGOFLOW2_ENGINE or self.vehicle < 0:
                raise ValueError("post-purchase readbacks echo the pinned engine and vehicle")
        if self.op != "order" and self.order_index != -1:
            raise ValueError("order echoes carry stop indexes")
        if self.op == "order" and self.status == "ORDERED":
            wanted = (
                CARGOFLOW2_ORDER_PICKUP_FLAGS
                if self.order_index == 0
                else CARGOFLOW2_ORDER_DELIVERY_FLAGS
            )
            if self.flags is None or self.flags != wanted:
                raise ValueError("the ordered order echoes its pinned flags")
            wanted_dest = CARGOFLOW2_PICKUP_TILE if self.order_index == 0 else CARGOFLOW2_BAY_TILE
            if self.dest is None or self.dest != wanted_dest:
                raise ValueError("the ordered order echoes its pinned stop tile")
        if self.op == "order-read" and self.status == "ORDER_SET_VERIFIED":
            if self.order_len != 2:
                raise ValueError("the two-order loop carries exactly two orders")
            if (self.dest0, self.flags0, self.goto0) != (
                CARGOFLOW2_PICKUP_TILE,
                CARGOFLOW2_ORDER_PICKUP_FLAGS,
                True,
            ):
                raise ValueError("order 0 drifted from the pinned pickup stop")
            if (self.dest1, self.flags1, self.goto1) != (
                CARGOFLOW2_BAY_TILE,
                CARGOFLOW2_ORDER_DELIVERY_FLAGS,
                True,
            ):
                raise ValueError("order 1 drifted from the pinned delivery bay")
        if self.op == "arrive-watch" and self.status == "ANCHORED":
            if self.anchor != self.day:
                raise ValueError("the arrival anchor is the arrival instant's own day")
            if self.location != CARGOFLOW2_PICKUP_TILE:
                raise ValueError("the first arrival latches at the pinned pickup stop")
            if self.load != 0:
                raise ValueError(
                    "the first arrival carries the empty load of record (the "
                    "selector was closed before this arrival — §5.2 item 2)"
                )
            if self.latches is None or not self.latches:
                raise ValueError("the anchored arrival carries its own latch")
            if self.latches[0].kind != "arrival_pickup":
                raise ValueError("the anchored arrival's latch is the pickup arrival")
            if self.latches[0].day != self.day or self.latches[0].tick != self.tick:
                raise ValueError("the arrival latch's instant is its own observation instant")
        if self.op == "flow" and self.status == "READY":
            if self.latches is not None and len(self.latches) > CARGOFLOW2_LATCH_LIMIT:
                raise ValueError("the latch array exceeds its response budget bound")
        if (
            self.op == "finish"
            and self.status == "PHASE_STOPPED"
            and (self.stop_issued is not False)
        ):
            raise ValueError("the finish exchange issues no command in this attempt's schedule")


def verify_request_against_cargoflow2_plan(
    request: Cargoflow2Request, *, plan: Cargoflow2Plan, seal: str
) -> None:
    """Refuse a request that is not bound to the local delivery plan.

    Python is the trust anchor: every request must present the staged seal,
    the pinned corridor identity and exactly its planned position.
    """
    if request.plan != seal:
        raise ValueError("request plan digest is not the staged prelaunch seal")
    if request.company != plan.company:
        raise ValueError("request company drifted from the planned company")
    if (request.pickup, request.delivery, request.depot) != (
        plan.pickup,
        plan.delivery,
        plan.depot,
    ):
        raise ValueError("request pins drifted from the planned corridor")
    if request.request_id not in plan.schedule:
        raise ValueError("request id drifted from the planned schedule")
    if request.schedule_version != plan.schedule_version:
        raise ValueError("request arm drifted from the planned schedule version")
    if _cargoflow2_arm_op_by_id(plan.schedule_version)[request.request_id] != request.op:
        raise ValueError("request op drifted from its planned position")


class Cargoflow2FundsModel:
    """The modeled funds trajectory of record (§4, zero-residual fence).

    The model owns: the exact purchase debit; the staircase monthly
    interest plus the pinned station fee at each new economy-month
    boundary; the running cost billed at every charge event of the E113
    lattice (events at ``T0 + 1 + 74k``, vehicle 1's slot, keyed by its
    own rolled day) through the exact 8.8 fixed-point fraction carry
    (§4.3) — the unstop partial bills inside the first billed event
    (rt = event − count start, from the latched + 1 unstop tick), every
    later event full ``DAY_TICKS``, and a pre-count (rt ≤ 0) event is
    silent with no state change; and the delivery income attributed from
    the engine's own quarter-income reads at the same observation
    instants. The purchase, interest and fee are whole-unit and
    fraction-free; only the vehicle running cost touches the fraction.
    Anything observed outside these terms is a divergence: the fence
    halts fail-closed at that exchange, and the model is never loosened
    to pass (§8 item 5).
    """

    def __init__(
        self,
        *,
        start_funds: int,
        purchase_quote: int,
        running_display: int = CARGOFLOW2_RUNNING_DISPLAY,
    ) -> None:
        self.start_funds = start_funds
        self.purchase_quote = purchase_quote
        self.running_display = running_display
        self.funds = start_funds
        self.fraction = 0
        self.running_cost: int | None = None
        self.baseline_income: int | None = None
        self.income_deltas: list[tuple[str, int, int, int]] = []
        self.started: tuple[int, int] | None = None
        self.frontier: tuple[int, int] | None = None
        self.purchase_paid = False
        self.running_costs: list[tuple[str, list[tuple[int, int, int]]]] = []
        # The charge-event cursor and the running-count period start of
        # record: the cursor starts one lattice step before the session
        # (the launch day's own event, tick −25 under T0 = 48), silent —
        # pre-unstop events bill nothing and take no state change.
        self._next_charge_tick = CARGOFLOW2_DAY_ROLL_ANCHOR + CARGOFLOW2_CHARGE_SLOT - DAY_TICKS
        self._run_period_start: int | None = None

    def admit_running_cost(self, display: int) -> None:
        """§4.1 (the E111 correction): the display pin arrives natively and
        is admitted fail-closed — a 256-scaled raw is script-unreachable.
        The admitted figure is the model's own binding's census display
        (a cross-version wiring mix refuses, in either direction)."""
        if self.running_cost is not None:
            raise ValueError("the running cost was already pinned at its exchange")
        if display != self.running_display:
            raise ValueError("the running cost is inconsistent with its display figure")
        self.running_cost = display

    def _day_running_cost(self, rt: int) -> int:
        """The 8.8 fixed-point day charge and its exact fraction carry (§4.3).

        The pinned figure is the per-economy-year display value of record
        (E111); the 8.8 day charge reconstructs its 256-scaled surface
        exactly, so the billing arithmetic of record is unchanged.
        """
        if self.running_cost is None:
            raise ValueError("the running cost was never pinned at engine-00")
        if not 0 < rt <= DAY_TICKS:
            raise ValueError(f"the running-tick count {rt} is outside its single day")
        c256 = self.running_cost * rt * 256 // (DAYS_IN_ECONOMY_YEAR * DAY_TICKS)
        low = c256 & 0xFF
        new_fraction = (self.fraction - low) % 256
        whole = (c256 >> 8) + (1 if new_fraction > self.fraction else 0)
        self.funds -= whole
        self.fraction = new_fraction
        return whole

    def start_vehicle(self, day: int, tick: int) -> None:
        """§4.2 item 4: the start day is not its own row — the vehicle
        unstops one tick after its latched acceptance and the running
        count starts there (E113's unstop latch), so the start-day partial
        bills inside the first billed lattice event on the next rolled
        day."""
        if self.started is not None:
            raise ValueError("the vehicle was already started")
        if self.frontier is None:
            raise ValueError("the model has no observation frontier before the start")
        self.started = (day, tick)
        self._run_period_start = tick + 1

    def advance(self, exchange_id: str, day: int, tick: int, income: int) -> int:
        """Reconcile the modeled funds up to one observation instant.

        Charge application order: the charge events of the E113 lattice up
        to this observation tick — event k bills on its own rolled day
        ``CARGOFLOW2_LAUNCH_DAY + 1 + k`` its own
        ``raw · rt // 27010`` charge at the 8.8 fraction carry since the
        last billed event (the first interval from the unstop count
        start, ``DAY_TICKS`` between consecutive events, an rt ≤ 0 event
        silent with no state change), then the whole-unit monthly
        charges at each new economy-month boundary crossed by the
        observation days, then the engine-read income delta. Returns the
        modeled funds level.
        """
        if self.frontier is not None and (day, tick) < self.frontier:
            raise ValueError("the observation clock ran backwards")
        daily: list[tuple[int, int, int]] = []
        while self._next_charge_tick <= tick:
            event_tick = self._next_charge_tick
            event_day = (
                CARGOFLOW2_LAUNCH_DAY
                + 1
                + ((event_tick - CARGOFLOW2_DAY_ROLL_ANCHOR - CARGOFLOW2_CHARGE_SLOT) // DAY_TICKS)
            )
            if self.started is not None and self.running_cost is not None:
                count_start = self._run_period_start
                if count_start is None:
                    # Unreachable on the walk of record — every started
                    # model was seeded by its own start_vehicle — but the
                    # guard keeps the count arithmetic total.
                    raise ValueError("the running count has no unstop period start")
                rt = event_tick - count_start
                if rt > 0:
                    whole = self._day_running_cost(rt)
                    daily.append((event_day, rt, whole))
                    self._run_period_start = event_tick
            self._next_charge_tick += DAY_TICKS
        if daily:
            self.running_costs.append((exchange_id, daily))
        monthly = 0
        if self.frontier is not None:
            prev_day, _prev_tick = self.frontier
            monthly = sum(
                cargoflow2_month_charge(boundary)
                for boundary in CARGOFLOW2_MONTH_BOUNDARY_DAYS
                if prev_day < boundary <= day
            )
            if monthly:
                self.funds -= monthly
        if self.baseline_income is None:
            self.baseline_income = income
            delta = 0
        else:
            delta = (
                income
                - self.baseline_income
                - sum(prior_delta for _, _, _, prior_delta in self.income_deltas)
            )
        self.funds += delta
        self.income_deltas.append((exchange_id, day, tick, delta))
        self.frontier = (day, tick)
        return self.funds

    def reconcile(
        self,
        *,
        exchange_id: str,
        day: int,
        tick: int,
        income: int,
        observed: int,
    ) -> int:
        """The zero-residual fence of record (§4.4): residual is a halt."""
        modeled = self.advance(exchange_id, day, tick, income)
        residual = observed - modeled
        if residual != 0:
            raise ValueError(
                "cargo-flow 2 funds diverged from the modeled trajectory: "
                f"{exchange_id} observed {observed}, modeled {modeled}, "
                f"residual {residual}"
            )
        return residual

    def debit_purchase(self) -> None:
        """The purchase debit: exactly the pinned quote, fraction-free."""
        if self.purchase_paid:
            raise ValueError("the purchase already moved its pinned quote")
        self.funds -= self.purchase_quote
        self.purchase_paid = True


def _latch_rows(latches) -> list[dict]:
    return [
        dict(kind=latch.kind, day=latch.day, tick=latch.tick, cargo=latch.cargo)
        for latch in latches
    ]


def cargoflow2_funds_model(binding: Cargoflow2RouteBinding) -> Cargoflow2FundsModel:
    """The funds-model wiring of record is binding-parameterized: a model
    of one route-family member carries that binding's own founding pins and
    its own census display figure — its admissions and its fence are its
    own version's, never another binding's."""
    return Cargoflow2FundsModel(
        start_funds=binding.start_funds,
        purchase_quote=binding.purchase_quote,
        running_display=binding.engine_running_display,
    )


def _cargoflow2_state() -> dict[str, Any]:
    return dict(
        index=0,
        anchor=None,
        arrival=None,
        samples={},
        ledger=[],
        funds=None,
        model=None,
        vehicle=None,
        loads=[],
        departures=[],
        pickup_arrivals=[],
        bay_arrivals=[],
        unloadings=[],
        finance=None,
    )


def _cargoflow2_read_step(
    state: dict,
    request: Cargoflow2Request,
    readback: Cargoflow2Readback,
    *,
    plan: Cargoflow2Plan,
    seal: str,
) -> dict:
    """Verify one ordered exchange against the accumulated attempt state."""
    plan_ids = plan.schedule
    expected = plan_ids[state["index"]]
    if request.request_id != expected or readback.request_id != expected:
        raise ValueError(f"cargo-flow 2 exchange out of order: expected {expected}")
    verify_request_against_cargoflow2_plan(request, plan=plan, seal=seal)
    if readback.status != _CARGOFLOW2_SUCCESS_STATUS[request.op]:
        raise ValueError(f"cargo-flow 2 exchange {expected} ended {readback.status}")
    if readback.cost != 0 and request.op != "purchase":
        raise ValueError("cargo-flow 2 exchanges outside the purchase observe at zero cost")
    if state["model"] is None:
        state["model"] = Cargoflow2FundsModel(
            start_funds=plan.start_funds, purchase_quote=plan.purchase_quote
        )
    model = state["model"]
    # The frame's own nonneg strict validation refuses a success frame
    # without its instant/income reads; assert here so the funds fence of
    # record is typed by construction.
    assert readback.tick is not None and readback.day is not None
    assert readback.income is not None
    day = readback.day
    tick = readback.tick
    income = readback.income
    if readback.op == "engine":
        model.reconcile(
            exchange_id=readback.request_id,
            day=day,
            tick=tick,
            income=income,
            observed=readback.funds,
        )
        # The success-field subset check refuses an engine frame without
        # its running cost; assert so the fence is typed (E111: the wire
        # value is the display figure, admitted against its pin).
        assert readback.running_cost is not None
        model.admit_running_cost(int(readback.running_cost))
    elif readback.op == "site":
        model.reconcile(
            exchange_id=readback.request_id,
            day=day,
            tick=tick,
            income=income,
            observed=readback.funds,
        )
    elif readback.op == "purchase":
        # §4.2 item 1: the funds echo already includes the debit; reconcile
        # the pre-debit level (observed + quote) at the same instant, then
        # subtract exactly the pinned quote.
        model.reconcile(
            exchange_id=readback.request_id,
            day=day,
            tick=tick,
            income=income,
            observed=readback.funds + plan.purchase_quote,
        )
        model.debit_purchase()
        state["vehicle"] = readback.vehicle
    else:
        model.reconcile(
            exchange_id=readback.request_id,
            day=day,
            tick=tick,
            income=income,
            observed=readback.funds,
        )
    if readback.op == "start":
        model.start_vehicle(day, tick)
    if readback.op == "arrive-watch":
        if state["anchor"] is not None:
            raise ValueError("the ladder anchor was already latched")
        state["anchor"] = readback.anchor
        # The winning arrival frame rides its latched cycle event (§5.3 by
        # construction — the success-field subset refuses an absent one).
        assert readback.latches is not None
        state["arrival"] = dict(
            day=readback.day,
            tick=readback.tick,
            latch=dict(
                kind=readback.latches[0].kind,
                day=readback.latches[0].day,
                tick=readback.latches[0].tick,
                cargo=readback.latches[0].cargo,
            ),
            latches=_latch_rows(readback.latches),
        )
    if readback.op in ("flow", "finance", "finish"):
        if state["anchor"] is None:
            raise ValueError("the flow ladder never starts without its anchor")
        if readback.op == "flow":
            sample = {
                **{name: int(getattr(readback, name)) for name in _FEATURE_NAMES},
                "year": readback.year,
                "month": readback.month,
                "day_of_month": readback.day_of_month,
                "funds": readback.funds,
                "income": readback.income,
                "delivered": readback.delivered,
                "vehicle": dict(
                    location=readback.location,
                    load=readback.load,
                    in_depot=readback.in_depot,
                    speed=readback.speed,
                ),
                "latches": _latch_rows(readback.latches),
            }
            state["samples"][int(readback.offset)] = sample
            for latch in sample["latches"]:
                kind = latch["kind"]
                if kind == "arrival_pickup":
                    state["pickup_arrivals"].append(dict(exchange=readback.request_id, **latch))
                elif kind == "arrival_bay":
                    state["bay_arrivals"].append(dict(exchange=readback.request_id, **latch))
                elif kind == "load":
                    state["loads"].append(dict(exchange=readback.request_id, **latch))
                elif kind == "departure":
                    state["departures"].append(dict(exchange=readback.request_id, **latch))
                elif kind == "unload":
                    state["unloadings"].append(dict(exchange=readback.request_id, **latch))
            # The tail rows carry their own slim evidence shapes: the finance
            # sample is the delivered/last-accepted reads of record; the
            # finish sample is the certified cleanup state of record. Neither
            # carries the industry observation set (their ops attach none of
            # it).
        elif readback.op == "finance":
            sample = dict(
                day=day,
                tick=tick,
                funds=readback.funds,
                income=readback.income,
                delivered=readback.delivered,
                last_accepted=readback.last_accepted,
            )
        else:
            sample = dict(
                day=day,
                tick=tick,
                funds=readback.funds,
                income=readback.income,
                state=readback.state,
                in_depot=readback.in_depot,
                speed=readback.speed,
                stop_issued=readback.stop_issued,
            )
    if readback.op == "finance":
        state["finance"] = dict(
            delivered=readback.delivered,
            last_accepted=readback.last_accepted,
            day=day,
            tick=tick,
            funds=readback.funds,
            income=readback.income,
        )
    state["ledger"].append(
        dict(
            exchange=request.request_id,
            op=request.op,
            status=readback.status,
            funds=readback.funds,
        )
    )
    state["funds"] = readback.funds
    state["index"] += 1
    receipt: dict[str, Any] = dict(
        schema=CARGOFLOW2_RECEIPT_SCHEMA,
        request_id=readback.request_id,
        op=request.op,
        plan_digest=plan.digest,
        seal=seal,
        offset=_cargoflow2_arm_request_offset_map(request.schedule_version)[request.request_id],
        status=readback.status,
        funds=readback.funds,
        income=readback.income,
        anchor=readback.anchor,
        tick=readback.tick,
        day=readback.day,
    )
    if readback.op in ("flow", "finance", "finish"):
        receipt["sample"] = sample
    elif readback.op == "arrive-watch":
        receipt["arrival"] = state["arrival"]
    return receipt


def _cargoflow2_series(samples: dict) -> dict:
    """The per-field sampled observation series as facts, keyed by order."""
    keys = sorted(samples)
    series: dict[str, list[int]] = {}
    for name in _FEATURE_NAMES:
        series[name] = [int(samples[offset][name]) for offset in keys]
    series["funds"] = [int(samples[offset]["funds"]) for offset in keys]
    series["income"] = [int(samples[offset]["income"]) for offset in keys]
    return series


def cargoflow2_verdict(
    samples: dict,
    *,
    anchor: int | None,
    loads: list[dict],
    departures: list[dict],
    unloadings: list[dict],
    pickup_arrivals: list[dict],
    bay_arrivals: list[dict],
    finance: dict | None,
) -> dict:
    """The offline delivery verdict from the sampled evidence alone (§7).

    All seven acceptance conditions are rebuilt from the receipts alone —
    the latched arrival/load/departure/unload events, the sampled series
    and the finance readback — never from the native session's own verdict.
    The typing reproduces §5.5 exactly: each unmet criterion decides its
    own terminal class in conservative order, never folded into a success.
    """
    if anchor is None or not samples:
        return dict(
            verdict="CARGOFLOW2_GATE_UNDECIDED_INCOMPLETE",
            statement=(
                "an unobserved or unfinished ladder decides this, as in E99: "
                "no arrival anchor or no flow sample can decide nothing"
            ),
        )
    flow_keys = sorted(samples)
    pickup_stock = [int(samples[offset]["stock_pickup"]) for offset in flow_keys]
    stock_pickup_mismatch = any(value != -1 for value in pickup_stock)
    queue_ok = any(
        offset > 0
        and int(samples[offset]["wait_pickup"]) > 0
        and int(samples[offset]["wait_pickup_from0"]) > 0
        for offset in flow_keys
    )
    trans_ok = any(int(samples[offset]["trans_pickup"]) > 0 for offset in flow_keys)
    stock_bay_series = [int(samples[offset]["stock_bay"]) for offset in flow_keys]
    bay_rise = any(
        stock_bay_series[i] - stock_bay_series[i - 1] > 0 for i in range(1, len(stock_bay_series))
    )
    bay_drain_after_rise = any(
        stock_bay_series[j] - stock_bay_series[i] < 0
        for i in range(1, len(stock_bay_series))
        if stock_bay_series[i] - stock_bay_series[i - 1] > 0
        for j in range(i + 1, len(stock_bay_series))
    )
    income_ok = any(delta > 0 for _, _, _, delta in _income_deltas_by_offset(samples))
    loaded_ok = any(int(row["cargo"]) > 0 for row in loads)
    departed_ok = any(int(row["cargo"]) > 0 for row in departures)
    unloaded_ok = any(int(row["cargo"]) > 0 for row in unloadings)
    bay_delivery_ok = bool(bay_arrivals) and bay_rise
    delivered_ok = unloaded_ok and bay_delivery_ok
    consumption_ok = bay_rise and bay_drain_after_rise
    finance_ok = finance is not None and (
        int(finance["delivered"]) > 0 and finance["last_accepted"] is not None
    )
    # §7 criterion 7: the five-stage cycle is reconstructed from the latched
    # events alone: a pickup arrival, a filled queue, a load, a loaded
    # departure, a bay arrival, an unload with stock rise, and a later
    # measured consumption.
    cycle_ok = all(
        (
            not stock_pickup_mismatch,
            bool(pickup_arrivals) or queue_ok,
            queue_ok,
            loaded_ok,
            departed_ok,
            delivered_ok,
            consumption_ok,
            trans_ok,
            income_ok,
            finance_ok,
        )
    )
    if cycle_ok:
        return dict(
            verdict="CARGOFLOW2_DELIVERY_VERIFIED",
            statement=(
                "the receipts carry one complete five-stage delivery cycle: the "
                "pickup queue filled after the vehicle's witnessed arrival (with "
                "the source attribution of record), a loaded departure ran the "
                "two-order loop, an unload reached the bay acceptance chain with "
                "a positive income delta, the finance delivered read rose, the "
                "accepted pile rose and later drained — all seven §7 criteria "
                "rebuilt from the evidence, never from the native verdict"
            ),
        )
    if loaded_ok and not delivered_ok:
        return dict(
            verdict="CARGOFLOW2_LOADED_NEVER_DELIVERED",
            statement=(
                "a load was latched, but no unloaded amount reached the bay "
                "acceptance chain inside the ladder"
            ),
        )
    if delivered_ok and not consumption_ok:
        return dict(
            verdict="CARGOFLOW2_CONSUMPTION_UNOBSERVED",
            statement=(
                "the bay accepted pile rose, but the ladder never measured its "
                "later net decrease: the industry side is unproven"
            ),
        )
    if not queue_ok:
        return dict(
            verdict="CARGOFLOW2_QUEUE_NEVER_FILLED",
            statement=(
                "the pickup waiting never rose inside the anchor's ladder: the "
                "selector was opened by the witnessed arrival, so the drain "
                "side is implicated — a stronger H1-class record than E99's"
            ),
        )
    return dict(
        verdict="CARGOFLOW2_GATE_UNDECIDED_INCOMPLETE",
        statement=(
            "the ladder ended without enough measured evidence; the attempt's "
            "five-stage chain stays undecided, never folded into a success"
        ),
    )


def _income_deltas_by_offset(samples: dict) -> list[tuple[int, int, int, int]]:
    """Per-flow-sample income deltas, keyed (offset, day, tick, delta)."""
    deltas: list[tuple[int, int, int, int]] = []
    baseline = None
    for offset in sorted(samples):
        income = int(samples[offset]["income"])
        if baseline is None:
            baseline = income
            delta = 0
        else:
            delta = income - baseline
        baseline = income
        sample = samples[offset]
        deltas.append((offset, int(sample["funds"]), int(sample["income"]), delta))
    return deltas


def cargoflow2_phase_outcome(
    exchanges: Sequence[tuple[Cargoflow2Request, Cargoflow2Readback | Exception]],
    *,
    prelaunch_digest: str,
    plan: Cargoflow2Plan,
) -> dict:
    """Fail-closed delivery verification over preserved evidence only.

    Each exchange is ``(request, readback_or_error)``; an error element is
    an observation whose bytes never parsed or correlated (malformed, stale,
    torn or duplicate). The first halted exchange ends verification: earlier
    receipts are preserved, later exchanges are pending, and an unfinished
    ladder can never manufacture success or a delivery verdict. The funds
    fence (§4.4) is applied at every verified exchange; the first residual
    ≠ 0 halts the attempt (``CARGOFLOW2_FUNDS_DIVERGED`` is typed by the
    failed error, never folded into a receipt).
    """
    receipts: list[dict] = []
    failed = None
    state = _cargoflow2_state()
    for request, readback in exchanges:
        if failed is not None:
            continue
        if isinstance(readback, Exception):
            failed = dict(
                label=request.request_id,
                status="MALFORMED",
                error=str(readback),
                world_state="HALTED_BEFORE_MUTATION",
            )
            continue
        try:
            receipts.append(
                _cargoflow2_read_step(state, request, readback, plan=plan, seal=prelaunch_digest)
            )
        except Exception as error:  # noqa: BLE001 - fail closed on any defect
            failed = dict(
                label=request.request_id,
                status=str(
                    getattr(readback, "status", "UNKNOWN")
                    if not isinstance(readback, Exception)
                    else "UNKNOWN"
                ),
                error=str(error),
                world_state="HALTED_BEFORE_MUTATION",
            )
            continue
    complete = failed is None and len(state["ledger"]) == len(plan.schedule)
    plan_ids = plan.schedule
    verified_label = failed["label"] if failed is not None else None
    pending = (
        list(plan_ids[state["index"] :])
        if failed is None
        else list(plan_ids[plan_ids.index(verified_label) + 1 :])
    )
    samples = state["samples"]
    series = _cargoflow2_series(samples) if samples else {}
    model = state["model"]
    verdict = cargoflow2_verdict(
        samples,
        anchor=state["anchor"],
        loads=state["loads"],
        departures=state["departures"],
        unloadings=state["unloadings"],
        pickup_arrivals=state["pickup_arrivals"],
        bay_arrivals=state["bay_arrivals"],
        finance=state["finance"],
    )
    verdict = dict(verdict)
    if failed is not None and "funds diverged" in failed["error"]:
        verdict = dict(
            verdict="CARGOFLOW2_FUNDS_DIVERGED",
            statement=failed["error"],
        )
    calendar = sorted({(int(sample["year"]), int(sample["month"])) for sample in samples.values()})
    return dict(
        schema=CARGOFLOW2_OUTCOME_SCHEMA,
        seal=prelaunch_digest,
        plan_digest=plan.digest,
        receipts=receipts,
        failed=failed,
        pending=pending,
        anchor=state["anchor"],
        arrival=state["arrival"],
        offset_ladder=list(CARGOFLOW2_FLOW_OFFSETS),
        samples=samples,
        series=series,
        loads=state["loads"],
        departures=state["departures"],
        pickup_arrivals=state["pickup_arrivals"],
        bay_arrivals=state["bay_arrivals"],
        unloadings=state["unloadings"],
        finance=state["finance"],
        funds_model=dict(
            running_cost=model.running_cost if model is not None else None,
            running_costs=model.running_costs if model is not None else [],
            income_deltas=model.income_deltas if model is not None else [],
        ),
        sampled_months=[[year, month] for year, month in calendar],
        verdict=verdict,
        observation_kinds=("MEASURED", "REFUSED", "MISSING", "MALFORMED"),
        verification="CARGOFLOW2_COMPLETE" if complete else "CARGOFLOW2_INCOMPLETE",
    )
