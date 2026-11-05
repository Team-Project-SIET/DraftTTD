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
CARGOFLOW2_YEARLY_INTEREST = (
    CARGOFLOW2_FOUNDING_LOAN * CARGOFLOW2_INTEREST_RATE // 100
)
DAYS_IN_ECONOMY_YEAR = 365
DAY_TICKS = 74

# The launch day of record: L = 712228 (Jan 6, 1950 — the save's current
# date at load, pinned by E99's ``sample-00`` anchor at tick 17). The 1950
# calendar base of record: day 712223 is Jan 1, 1950. The attempt can never
# leave 1950 (its last admissible observation day is 712288 = L + 60 = the
# worst-case ladder end, a normal early-March day), so the month-boundary
# days that can fall inside an attempt span are enumerated exactly.
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
    **{
        f"flow-{index:02d}": offset
        for index, offset in enumerate(CARGOFLOW2_FLOW_OFFSETS)
    },
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
    _CARGOFLOW2_FIXED_SEQUENCE
    + _CARGOFLOW2_FLOW_SEQUENCE
    + _CARGOFLOW2_TAIL_SEQUENCE
)
CARGOFLOW2_EXCHANGE_IDS: tuple[str, ...] = tuple(
    exchange_id for exchange_id, _ in _CARGOFLOW2_SEQUENCE
)
_CARGOFLOW2_OP_BY_ID: dict[str, Cargoflow2Op] = dict(_CARGOFLOW2_SEQUENCE)
_CARGOFLOW2_REQUEST_OFFSET_BY_ID: dict[str, int] = {
    exchange_id: _CARGOFLOW2_OFFSET_BY_ID.get(exchange_id, -1)
    for exchange_id in CARGOFLOW2_EXCHANGE_IDS
}

_MONTH_STARTS_1950 = tuple(
    _CALENDAR_BASE_DAY + sum(DAYS_IN_MONTH_1950[:m]) for m in range(0, 12)
)
# Boundaries of record as literals: the derived starts must equal these
# (the _assert_cargoflow2_calendar cross-check below), and this literal
# form keeps the §4 guard foldable for the type checker.
CARGOFLOW2_MONTH_BOUNDARY_DAYS: tuple[int, ...] = (
    712254, 712282, 712313, 712343, 712374, 712404,
    712435, 712466, 712496, 712527, 712557,
)
_CARGOFLOW2_MONTH_INSTALLMENT_BY_DAY: dict[int, int] = {
    boundary: CARGOFLOW2_YEARLY_INTEREST * (m + 1) // 12
    - CARGOFLOW2_YEARLY_INTEREST * m // 12
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
    or PLANNED_CARGOFLOW2_EXCHANGES > CARGOFLOW2_REQUEST_BUDGET
    or CARGOFLOW2_WAIT_MAX_TICKS != 2048
    or CARGOFLOW2_WAIT_DAY_CAP != 60
    or CARGOFLOW2_PICKUP_IND != 0
    or CARGOFLOW2_BAY_IND != 1
    or CARGOFLOW2_PICKUP_SID != 0
    or CARGOFLOW2_BAY_SID != 2
    or _CARGOFLOW2_FIXED_SEQUENCE[-1][1] != "arrive-watch"
    or CARGOFLOW2_MONTH_BOUNDARY_DAYS != (
        712254, 712282, 712313, 712343, 712374, 712404,
        712435, 712466, 712496, 712527, 712557,
    )
):
    raise RuntimeError(
        "cargo-flow delivery schedule drifted from the pinned observations"
    )
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
Cargoflow2EchoOffset = Annotated[StrictInt, Field(ge=-1, le=CARGOFLOW2_OFFSET_CAP)]
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
    zero-residual fence reconciles against (§4.1).
    """

    schema_version: Literal[1] = 1
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
    request_budget: Annotated[StrictInt, Field(gt=0, le=CARGOFLOW2_REQUEST_BUDGET)] = (
        CARGOFLOW2_REQUEST_BUDGET
    )
    day_budget: Annotated[StrictInt, Field(ge=1, le=CARGOFLOW2_DAY_BUDGET)] = (
        CARGOFLOW2_DAY_BUDGET
    )

    @property
    def digest(self) -> str:
        return hashlib.sha256(canonical_bytes(self)).hexdigest()

    @model_validator(mode="after")
    def coherent(self) -> Cargoflow2Plan:
        if self.company != CARGOFLOW2_COMPANY or self.cargo != CARGOFLOW2_CARGO:
            raise ValueError("the delivery attempt observes company 0 with cargo 1")
        if (self.pickup, self.pickup_front) != (
            CARGOFLOW2_PICKUP_TILE,
            CARGOFLOW2_PICKUP_FRONT_TILE,
        ):
            raise ValueError("pickup pins drifted from the depot-chain corridor")
        if (self.delivery, self.delivery_front) != (
            CARGOFLOW2_BAY_TILE,
            CARGOFLOW2_BAY_FRONT_TILE,
        ):
            raise ValueError("bay pins drifted from the depot-chain corridor")
        if (self.depot, self.depot_front) != (
            CARGOFLOW2_DEPOT_TILE,
            CARGOFLOW2_DEPOT_FRONT_TILE,
        ):
            raise ValueError("depot pins drifted from the depot-chain corridor")
        if self.pickup_sid != CARGOFLOW2_PICKUP_SID or self.bay_sid != CARGOFLOW2_BAY_SID:
            raise ValueError("station identities drifted from the pinned record sids")
        if (
            self.pickup_industry != CARGOFLOW2_PICKUP_IND
            or self.bay_industry != CARGOFLOW2_BAY_IND
        ):
            raise ValueError("industry identities drifted from the census receipt rows")
        if self.engine != CARGOFLOW2_ENGINE:
            raise ValueError("the plan binds the provisional engine pin exactly")
        if self.start_funds != CARGOFLOW2_START_FUNDS:
            raise ValueError("start funds drifted from the depot-mutation close pin")
        if (
            self.purchase_quote != CARGOFLOW2_PURCHASE_QUOTE
            or self.founding_loan != CARGOFLOW2_FOUNDING_LOAN
            or self.interest_rate != CARGOFLOW2_INTEREST_RATE
            or self.station_fee != CARGOFLOW2_STATION_FEE
        ):
            raise ValueError("financial-model pins drifted from the §4.1 table")
        if self.launch_day != CARGOFLOW2_LAUNCH_DAY:
            raise ValueError("launch day drifted from the pinned clock of record")
        if self.arrive_max_days != CARGOFLOW2_ARRIVE_MAX_DAYS:
            raise ValueError("the arrival bound drifted from its pinned 5 days")
        if self.flow_span_days != CARGOFLOW2_SPAN_DAYS:
            raise ValueError("flow span drifted from the pinned 55-day ladder")
        if self.schedule != CARGOFLOW2_EXCHANGE_IDS:
            raise ValueError("schedule drifted from the planned 25 exchanges")
        if self.pickup_sid == self.bay_sid:
            raise ValueError("the two observed stops must carry distinct station ids")
        if self.pickup_industry == self.bay_industry:
            raise ValueError("the two observed industries must be distinct")
        if self.arrive_max_days + self.flow_span_days > self.day_budget:
            raise ValueError(
                "the arrival bound plus flow span must fit the 60-day attempt authority"
            )
        return self


def cargoflow2_plan() -> Cargoflow2Plan:
    """The pinned D5-CARGOFLOW-2 plan derived from the module's own pins."""
    return Cargoflow2Plan(
        company=CARGOFLOW2_COMPANY,
        cargo=CARGOFLOW2_CARGO,
        pickup=CARGOFLOW2_PICKUP_TILE,
        pickup_front=CARGOFLOW2_PICKUP_FRONT_TILE,
        delivery=CARGOFLOW2_BAY_TILE,
        delivery_front=CARGOFLOW2_BAY_FRONT_TILE,
        depot=CARGOFLOW2_DEPOT_TILE,
        depot_front=CARGOFLOW2_DEPOT_FRONT_TILE,
        pickup_sid=CARGOFLOW2_PICKUP_SID,
        bay_sid=CARGOFLOW2_BAY_SID,
        pickup_industry=CARGOFLOW2_PICKUP_IND,
        bay_industry=CARGOFLOW2_BAY_IND,
        engine=CARGOFLOW2_ENGINE,
        start_funds=CARGOFLOW2_START_FUNDS,
        purchase_quote=CARGOFLOW2_PURCHASE_QUOTE,
        founding_loan=CARGOFLOW2_FOUNDING_LOAN,
        interest_rate=CARGOFLOW2_INTEREST_RATE,
        station_fee=CARGOFLOW2_STATION_FEE,
        launch_day=CARGOFLOW2_LAUNCH_DAY,
        arrive_max_days=CARGOFLOW2_ARRIVE_MAX_DAYS,
        flow_span_days=CARGOFLOW2_SPAN_DAYS,
        schedule=CARGOFLOW2_EXCHANGE_IDS,
    )


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

    @model_validator(mode="after")
    def coherent(self) -> Cargoflow2Request:
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
                raise ValueError(
                    "order requests pin one stop index with its pinned order flags"
                )
        elif self.op == "arrive-watch":
            if (
                not pitched
                or self.order_index != -1
                or self.watch_days != CARGOFLOW2_ARRIVE_MAX_DAYS
                or self.offset != -1
                or self.expected_cost != 0
            ):
                raise ValueError(
                    "arrive-watch echoes the vehicle identity and its 5-day bound"
                )
        elif self.op in ("finance", "finish"):
            if (
                not pitched
                or self.expected_cost != 0
                or self.watch_days != -1
                or self.order_index != -1
                or self.order_flags != -1
                or self.offset != CARGOFLOW2_TAIL_OFFSET
            ):
                raise ValueError(
                    f"{self.op} echoes the vehicle identity and ladder step "
                    f"{CARGOFLOW2_TAIL_OFFSET} (the flow-11 economy day of record)"
                )
        elif self.op == "flow":
            if (
                not pitched
                or self.order_index != -1
                or self.expected_cost != 0
                or self.watch_days != -1
            ):
                raise ValueError("flow echoes the vehicle identity and its ladder step")
            if self.request_id not in _CARGOFLOW2_OFFSET_BY_ID or self.offset != (
                _CARGOFLOW2_OFFSET_BY_ID[self.request_id]
            ):
                raise ValueError("flow offset drifted from its planned ladder step")
        else:  # "order-read", "monitor", "start", "finance", "finish"
            if not pitched or not quiet:
                raise ValueError(f"{self.op} echoes the vehicle identity only")
        return self

    def to_bytes(self) -> bytes:
        raw = canonical_bytes(self)
        if len(raw) > MAX_CARGOFLOW2_REQUEST_BYTES:
            raise ValueError(
                f"cargo-flow 2 request exceeds {MAX_CARGOFLOW2_REQUEST_BYTES} bytes"
            )
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
    "order-read": frozenset(
        ("order_len", "dest0", "flags0", "goto0", "dest1", "flags1", "goto1")
    ),
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
    latches: tuple[Cargoflow2Latch, ...] | None = Field(
        None, max_length=CARGOFLOW2_LATCH_LIMIT
    )

    @property
    def digest(self) -> str:
        return hashlib.sha256(canonical_bytes(self)).hexdigest()

    @classmethod
    def parse_for(cls, request: Cargoflow2Request, raw: bytes):
        if len(raw) > MAX_CARGOFLOW2_RESPONSE_BYTES:
            raise ValueError(
                f"cargo-flow 2 response exceeds {MAX_CARGOFLOW2_RESPONSE_BYTES} bytes"
            )

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
        return criteria

    @model_validator(mode="after")
    def coherent(self) -> Cargoflow2Readback:
        if self.op not in _CARGOFLOW2_SUCCESS_STATUS:
            raise ValueError("unknown cargo-flow 2 op")
        subset = _CARGOFLOW2_SUBSETS[self.op]
        present = {
            field for field in _CARGOFLOW2_FIELDS if getattr(self, field) is not None
        }
        income_present = self.income is not None
        status = self.status
        if status == _CARGOFLOW2_SUCCESS_STATUS[self.op]:
            outside = present - subset - {"tick", "day"}
            if outside:
                raise ValueError(
                    f"{self.op} readback carries fields outside its subset: "
                    f"{sorted(outside)}"
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
        expected = _CARGOFLOW2_OFFSET_BY_ID.get(self.request_id)
        if self.op in ("flow", "finance", "finish"):
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
            if (
                self.status == "READY"
                and (self.pickup_sid, self.bay_sid) != (
                    CARGOFLOW2_PICKUP_SID,
                    CARGOFLOW2_BAY_SID,
                )
            ):
                raise ValueError("the site readback re-pins the corridor station ids")
            if (
                self.status == "READY"
                and (self.pickup_industry, self.bay_industry) != (
                    CARGOFLOW2_PICKUP_IND,
                    CARGOFLOW2_BAY_IND,
                )
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
                    raise ValueError(
                        "the engine running cost disagrees with its display figure"
                    )
        elif self.op == "purchase":
            if self.order_index != -1 or self.watch_days != -1 or self.offset != -1:
                raise ValueError("purchase readback must not carry phase echoes")
            if self.status == "BUILT":
                if self.engine != CARGOFLOW2_ENGINE or self.vehicle < 0:
                    raise ValueError(
                        "built purchase must name the pinned engine and vehicle"
                    )
                if self.cost != CARGOFLOW2_PURCHASE_QUOTE:
                    raise ValueError("built purchase must cost its pinned quote")
            elif self.status in _CARGOFLOW2_REFUSAL_STATUS and self.vehicle != -1:
                raise ValueError("refused purchase must not name a vehicle")
        elif self.op in _CARGOFLOW2_POST_PURCHASE_OPS:
            if self.engine != CARGOFLOW2_ENGINE or self.vehicle < 0:
                raise ValueError(
                    "post-purchase readbacks echo the pinned engine and vehicle"
                )
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
            wanted_dest = (
                CARGOFLOW2_PICKUP_TILE
                if self.order_index == 0
                else CARGOFLOW2_BAY_TILE
            )
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
                raise ValueError(
                    "the arrival latch's instant is its own observation instant"
                )
        if self.op == "flow" and self.status == "READY":
            if self.latches is not None and len(self.latches) > CARGOFLOW2_LATCH_LIMIT:
                raise ValueError("the latch array exceeds its response budget bound")
        if self.op == "finish" and self.status == "PHASE_STOPPED" and (
            self.stop_issued is not False
        ):
            raise ValueError(
                "the finish exchange issues no command in this attempt's schedule"
            )


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
    if _CARGOFLOW2_OP_BY_ID[request.request_id] != request.op:
        raise ValueError("request op drifted from its planned position")


class Cargoflow2FundsModel:
    """The modeled funds trajectory of record (§4, zero-residual fence).

    The model owns: the exact purchase debit; the staircase monthly
    interest plus the pinned station fee at each new economy-month
    boundary; the per-economy-day running cost through the exact 8.8
    fixed-point fraction carry (§4.3) — the start day carries the partial
    tick count derived from the latched (day, tick) start instant; and the
    delivery income attributed from the engine's own quarter-income reads
    at the same observation instants. The purchase, interest and fee are
    whole-unit and fraction-free; only the vehicle running cost touches the
    fraction. Anything observed outside these terms is a divergence: the
    fence halts fail-closed at that exchange, and the model is never
    loosened to pass (§8 item 5).
    """

    def __init__(self, *, start_funds: int, purchase_quote: int) -> None:
        self.start_funds = start_funds
        self.purchase_quote = purchase_quote
        self.funds = start_funds
        self.fraction = 0
        self.running_cost: int | None = None
        self.baseline_income: int | None = None
        self.income_deltas: list[tuple[str, int, int, int]] = []
        self.started: tuple[int, int] | None = None
        self.frontier: tuple[int, int] | None = None
        self.purchase_paid = False
        self.running_costs: list[tuple[str, list[tuple[int, int, int]]]] = []

    def admit_running_cost(self, display: int) -> None:
        """§4.1 (the E111 correction): the display pin arrives natively and
        is admitted fail-closed — a 256-scaled raw is script-unreachable."""
        if self.running_cost is not None:
            raise ValueError("the running cost was already pinned at its exchange")
        if display != CARGOFLOW2_RUNNING_DISPLAY:
            raise ValueError(
                "the running cost is inconsistent with its display figure"
            )
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
        """§4.2 item 4: the start day is partial from its latched tick."""
        if self.started is not None:
            raise ValueError("the vehicle was already started")
        if self.frontier is None:
            raise ValueError("the model has no observation frontier before the start")
        self.started = (day, tick)

    def advance(
        self, exchange_id: str, day: int, tick: int, income: int
    ) -> int:
        """Reconcile the modeled funds up to one observation instant.

        Charge application order: the economy-day running-cost boundaries
        for days ended since the frontier (whole days at ``DAY_TICKS``; the
        start day partial from its latched tick), then the whole-unit
        monthly charges at each new economy-month boundary crossed, then
        the engine-read income delta. Returns the modeled funds level.
        """
        if self.frontier is not None and day < self.frontier[0]:
            raise ValueError("the observation clock ran backwards")
        daily: list[tuple[int, int, int]] = []
        monthly = 0
        if self.frontier is not None and day > self.frontier[0]:
            prev_day = self.frontier[0]
            if self.running_cost is not None and self.started is not None:
                start_day, start_tick = self.started
                for ended_day in range(max(prev_day, start_day), day):
                    rt = DAY_TICKS - start_tick if ended_day == start_day else DAY_TICKS
                    whole = self._day_running_cost(rt)
                    daily.append((ended_day, rt, whole))
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
            delta = income - self.baseline_income - sum(
                prior_delta for _, _, _, prior_delta in self.income_deltas
            )
        self.funds += delta
        self.income_deltas.append((exchange_id, day, tick, delta))
        self.frontier = (day, tick)
        if daily:
            self.running_costs.append((exchange_id, daily))
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
        raise ValueError(
            "cargo-flow 2 exchanges outside the purchase observe at zero cost"
        )
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
                    state["pickup_arrivals"].append(
                        dict(exchange=readback.request_id, **latch)
                    )
                elif kind == "arrival_bay":
                    state["bay_arrivals"].append(
                        dict(exchange=readback.request_id, **latch)
                    )
                elif kind == "load":
                    state["loads"].append(dict(exchange=readback.request_id, **latch))
                elif kind == "departure":
                    state["departures"].append(
                        dict(exchange=readback.request_id, **latch)
                    )
                elif kind == "unload":
                    state["unloadings"].append(
                        dict(exchange=readback.request_id, **latch)
                    )
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
        offset=_CARGOFLOW2_REQUEST_OFFSET_BY_ID[request.request_id],
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
        stock_bay_series[i] - stock_bay_series[i - 1] > 0
        for i in range(1, len(stock_bay_series))
    )
    bay_drain_after_rise = any(
        stock_bay_series[j] - stock_bay_series[i] < 0
        for i in range(1, len(stock_bay_series))
        if stock_bay_series[i] - stock_bay_series[i - 1] > 0
        for j in range(i + 1, len(stock_bay_series))
    )
    income_ok = any(
        delta > 0 for _, _, _, delta in _income_deltas_by_offset(samples)
    )
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
        deltas.append(
            (offset, int(sample["funds"]), int(sample["income"]), delta)
        )
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
                _cargoflow2_read_step(
                    state, request, readback, plan=plan, seal=prelaunch_digest
                )
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
        list(plan_ids[state["index"]:])
        if failed is None
        else list(plan_ids[plan_ids.index(verified_label) + 1:])
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
    if (
        failed is not None
        and "funds diverged" in failed["error"]
    ):
        verdict = dict(
            verdict="CARGOFLOW2_FUNDS_DIVERGED",
            statement=failed["error"],
        )
    calendar = sorted(
        {(int(sample["year"]), int(sample["month"])) for sample in samples.values()}
    )
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
