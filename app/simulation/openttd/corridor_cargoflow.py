"""Cargo-dispatch observation probe wire contract (protocol 10, additive).

Milestone D5-CARGOFLOW-1 (``docs/d5-cargo-dispatch-probe-2026-11-04.md``): the
F-11/E97 lineage halted terminal at ``transit-00`` with a zero-flow observation
the freight instrument could not attribute. This module is the protocol-10
wire contract for the read-only dispatch probe that attributes it — a fixed
fourteen-sample ladder, every 5 sim days from the loaded world's own clock
(anchor + offsets 0..65), measuring the industry-side stockpiles, the
per-source station waiting, the planned side, the per-month production and
transported levels, and the current date of record, in company mode — one
company, zero commands, max_cost 0 on every exchange.

Protocol 10 stays additive over the number allocation of record (4
construction, 5 freight v1, 6 accept-survey, 7 terrain survey, 8 freight v2,
9 box census): the GameScript bridge dispatches protocol-10 tables through a
separate guarded handler shipped in its own package directory
(``d5_cargoflow_package``), so no frozen package byte drifts. Named constants
(E33's lesson): request bodies are canonical UTF-8 JSON bounded by
MAX_CARGOFLOW_REQUEST_BYTES (512 — the survey/protocol-8/9 precedent: the
largest request carries one pinned sample offset, measured well below);
response bodies bound by MAX_CARGOFLOW_RESPONSE_BYTES (1400 — the protocol-8
precedent bound, widened for the 24-field sample the probe record §5 fixed).

The sampled world of record is the consumed depot-mutation attempt's
authoritative after-save (``D5-F12-DEPOT-3``, world-pin version 3): the
corridor pickup stop 45748, the A1 bay stop 50862 and the depot 45487, with
the station/industry identities of record the retained extension and census
receipts pinned (pickup sid 0, bay sid 2, producer industry 0 with tile
44983, acceptor industry 1 with tile 51116). The probe queries nothing else.
Funds equal the depot-mutation close-out pin on every sample: the probe has
no fleet, no purchase and no running cost, so the balance is expected
static; a drifted balance is a halt-on-divergence chain break, never a
normalized number.
"""

import hashlib
import json
from collections.abc import Sequence
from typing import Annotated, Literal

from pydantic import Field, StrictInt, StrictStr, model_validator

from app.planning.canonical import canonical_bytes
from app.planning.domain import Contract, Digest
from app.simulation.openttd.corridor_construction import (
    CompanyID,
    Money,
    SignedMoney,
    TileID,
)
from app.simulation.openttd.corridor_freight_v2 import (
    FREIGHT_CARGO_ID,
    FUNDS_AT_DEPOT_MUTATION_CLOSE,
)

CARGOFLOW_PROTOCOL = 10
MAX_CARGOFLOW_REQUEST_BYTES = 512
MAX_CARGOFLOW_RESPONSE_BYTES = 1400
PLANNED_CARGOFLOW_EXCHANGES = 14
CARGOFLOW_REQUEST_BUDGET = 32
CARGOFLOW_COMPANY = 0
# The corridor cargo of record, imported from the freight v2 wire so the two
# contracts cannot drift apart on the id the whole D5 lineage pins.
CARGOFLOW_CARGO = FREIGHT_CARGO_ID

# The depot-chain world of record's three tiles (world-pin version 3, the
# pins the freight v2 staging natively re-checked): the probe only echoes
# them and never queries a foreign tile.
CARGOFLOW_PICKUP_TILE = 45748
CARGOFLOW_PICKUP_FRONT_TILE = 45747
CARGOFLOW_BAY_TILE = 50862
CARGOFLOW_BAY_FRONT_TILE = 50863
CARGOFLOW_DEPOT_TILE = 45487
CARGOFLOW_DEPOT_FRONT_TILE = 45743

# The station identities of record: the A1 extension receipt pinned the
# corridor stops as sids {0, 1} with the new bay at sid 2; the pickup stop is
# sid 0 and the A1 bay sid 2 — the dispatch probe record's own §5 sampling
# list.
CARGOFLOW_PICKUP_SID = 0
CARGOFLOW_BAY_SID = 2

# The industry identities of record (the consumed box-census attempt's rows:
# producer industry 0, acceptor industry 1 — the two industries the probe's
# stockpile and monthly ops of record measure).
CARGOFLOW_PICKUP_IND = 0
CARGOFLOW_BAY_IND = 1

# The sample ladder of record: anchor-relative sim-day offsets every 5 days
# from 0 through 65. The 65-day span crosses at least two month boundaries
# of ANY month pair (the widest 31+31-day calendar gap cannot hold both
# boundaries outside a 65-day window), so the ≥2-boundaries schedule
# property of the approved design record never depends on the saved world's
# calendar position.
CARGOFLOW_SAMPLE_OFFSETS: tuple[int, ...] = tuple(range(0, 70, 5))
CARGOFLOW_SPAN_DAYS = CARGOFLOW_SAMPLE_OFFSETS[-1]
# The wait-window cap family (the freight-8 precedent scale): a module bound
# on the shared wait machinery, never a promise. Offsets ride the ladder cap;
# the day cap bounds only the per-window wait lease.
CARGOFLOW_WAIT_MAX_TICKS = 2048
CARGOFLOW_WAIT_DAY_CAP = 60
CARGOFLOW_OFFSET_CAP = CARGOFLOW_SPAN_DAYS

CARGOFLOW_OPS = ("sample",)

CargoFlowOp = Literal["sample"]
# Waiting on the bridge: protocol 10 keeps the frozen survey-6 status family
# plus the freight-8 window family the wait machinery abaixo lives in.
CargoFlowStatus = Literal[
    "READY",
    "UNSUPPORTED_NATIVE_FACT",
    "INVALID_COMPANY",
    "PAUSED",
    "STALE_PIN",
    "OUT_OF_ORDER",
    "WINDOW_EXHAUSTED",
    "CLOCK_STALLED",
]
CARGOFLOW_ATTEMPT_SCHEMA_VERSION = 1

_CARGOFLOW_SEQUENCE: tuple[tuple[str, int], ...] = tuple(
    (f"sample-{index:02d}", offset)
    for index, offset in enumerate(CARGOFLOW_SAMPLE_OFFSETS)
)
CARGOFLOW_EXCHANGE_IDS: tuple[str, ...] = tuple(row[0] for row in _CARGOFLOW_SEQUENCE)
_CARGOFLOW_OFFSET_BY_ID: dict[str, int] = {row[0]: row[1] for row in _CARGOFLOW_SEQUENCE}
_CARGOFLOW_REFUSAL_STATUS = frozenset(
    {
        "UNSUPPORTED_NATIVE_FACT",
        "INVALID_COMPANY",
        "PAUSED",
        "STALE_PIN",
        "OUT_OF_ORDER",
        "WINDOW_EXHAUSTED",
        "CLOCK_STALLED",
    }
)
# The wait-window echo family (the freight-8 inconclusive precedent): these
# two statuses may carry exactly the three window echoes — the honest
# halted-window evidence of record (anchor/tick/day) — while every other
# refusal carries none of the observation set.
_CARGOFLOW_WINDOW_ECHO_STATUS = frozenset({"WINDOW_EXHAUSTED", "CLOCK_STALLED"})
_CARGOFLOW_WINDOW_ECHO_FIELDS = ("anchor", "tick", "day")

if (
    len(CARGOFLOW_EXCHANGE_IDS) != PLANNED_CARGOFLOW_EXCHANGES
    or len(set(CARGOFLOW_EXCHANGE_IDS)) != PLANNED_CARGOFLOW_EXCHANGES
    or CARGOFLOW_SAMPLE_OFFSETS != (0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65)
    or CARGOFLOW_SPAN_DAYS != 65
    or CARGOFLOW_OPS != ("sample",)
    or CARGOFLOW_WAIT_MAX_TICKS != 2048
    or CARGOFLOW_WAIT_DAY_CAP != 60
    or CARGOFLOW_PICKUP_IND != 0
    or CARGOFLOW_BAY_IND != 1
):
    raise RuntimeError("cargo-dispatch sample ladder drifted from the pinned observations")


class CargoFlowPlan(Contract):
    """The pinned identities and ordered sample ladder of one probe attempt.

    The plan binds the depot-chain world of record exactly as the freight v2
    staging does — corridor tiles, the station identities, the two industry
    identities, the close-out funds and the fourteen-sample schedule — so the
    staged prelaunch record, the preflight re-derivations and the replay all
    compare table-level pins, never prose.
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
    expected_funds: Money
    sample_span_days: Annotated[StrictInt, Field(ge=1, le=365)]
    schedule: tuple[StrictStr, ...]
    request_budget: Annotated[StrictInt, Field(gt=0, le=CARGOFLOW_REQUEST_BUDGET)] = (
        CARGOFLOW_REQUEST_BUDGET
    )

    @property
    def digest(self) -> str:
        return hashlib.sha256(canonical_bytes(self)).hexdigest()

    @model_validator(mode="after")
    def coherent(self) -> CargoFlowPlan:
        if self.company != CARGOFLOW_COMPANY or self.cargo != CARGOFLOW_CARGO:
            raise ValueError("the dispatch probe observes company 0 with cargo 1")
        if (self.pickup, self.pickup_front) != (
            CARGOFLOW_PICKUP_TILE,
            CARGOFLOW_PICKUP_FRONT_TILE,
        ):
            raise ValueError("pickup pins drifted from the depot-chain corridor")
        if (self.delivery, self.delivery_front) != (
            CARGOFLOW_BAY_TILE,
            CARGOFLOW_BAY_FRONT_TILE,
        ):
            raise ValueError("bay pins drifted from the depot-chain corridor")
        if (self.depot, self.depot_front) != (
            CARGOFLOW_DEPOT_TILE,
            CARGOFLOW_DEPOT_FRONT_TILE,
        ):
            raise ValueError("depot pins drifted from the depot-chain corridor")
        if self.pickup_sid != CARGOFLOW_PICKUP_SID or self.bay_sid != CARGOFLOW_BAY_SID:
            raise ValueError("station identities drifted from the pinned record sids")
        if (
            self.pickup_industry != CARGOFLOW_PICKUP_IND
            or self.bay_industry != CARGOFLOW_BAY_IND
        ):
            raise ValueError("industry identities drifted from the census receipt rows")
        if self.expected_funds != FUNDS_AT_DEPOT_MUTATION_CLOSE:
            raise ValueError("the plan binds the depot-mutation close-out funds exactly")
        if self.sample_span_days != CARGOFLOW_SPAN_DAYS:
            raise ValueError("sample span drifted from the pinned 65-day ladder")
        if self.schedule != CARGOFLOW_EXCHANGE_IDS:
            raise ValueError("schedule drifted from the planned fourteen samples")
        if self.pickup_sid == self.bay_sid:
            raise ValueError("the two observed stops must carry distinct station ids")
        if self.pickup_industry == self.bay_industry:
            raise ValueError("the two observed industries must be distinct")
        return self


def cargoflow_plan() -> CargoFlowPlan:
    """The pinned D5-CARGOFLOW-1 plan derived from the module's own pins."""
    return CargoFlowPlan(
        company=CARGOFLOW_COMPANY,
        cargo=CARGOFLOW_CARGO,
        pickup=CARGOFLOW_PICKUP_TILE,
        pickup_front=CARGOFLOW_PICKUP_FRONT_TILE,
        delivery=CARGOFLOW_BAY_TILE,
        delivery_front=CARGOFLOW_BAY_FRONT_TILE,
        depot=CARGOFLOW_DEPOT_TILE,
        depot_front=CARGOFLOW_DEPOT_FRONT_TILE,
        pickup_sid=CARGOFLOW_PICKUP_SID,
        bay_sid=CARGOFLOW_BAY_SID,
        pickup_industry=CARGOFLOW_PICKUP_IND,
        bay_industry=CARGOFLOW_BAY_IND,
        expected_funds=FUNDS_AT_DEPOT_MUTATION_CLOSE,
        sample_span_days=CARGOFLOW_SPAN_DAYS,
        schedule=CARGOFLOW_EXCHANGE_IDS,
    )


class CargoFlowRequest(Contract):
    """One protocol-10 sample request (fixed correlation stride).

    Every request carries the corridor identity pins (the native handler
    refuses a drifted pin before any observation), the uniform ``plan`` seal
    digest and the one sample offset it observes: an exact planned ladder
    step, so a replayed or reordered sample becomes OUT_OF_ORDER at the
    native handler and never a quietly reshuffled ladder. ``max_cost`` is 0
    on every sample: the probe has no cost-bearing operation of any kind.
    """

    protocol: Literal[10] = 10
    op: CargoFlowOp
    request_id: Annotated[str, Field(pattern=r"^[a-z0-9-]{1,32}$")]
    plan: Digest
    company: CompanyID
    max_cost: Annotated[StrictInt, Field(ge=0, le=0)]
    pickup: TileID
    delivery: TileID
    depot: TileID
    offset: Annotated[StrictInt, Field(ge=0, le=CARGOFLOW_OFFSET_CAP)]

    @model_validator(mode="after")
    def coherent(self) -> CargoFlowRequest:
        if self.op != "sample":
            raise ValueError("protocol 10 carries the sample op only")
        expected = _CARGOFLOW_OFFSET_BY_ID.get(self.request_id)
        if expected is None:
            raise ValueError("the sample request id is outside the pinned ladder")
        if self.offset != expected:
            raise ValueError("sample offset drifted from its planned ladder step")
        return self

    def to_bytes(self) -> bytes:
        raw = canonical_bytes(self)
        if len(raw) > MAX_CARGOFLOW_REQUEST_BYTES:
            raise ValueError(
                f"cargo-flow request exceeds {MAX_CARGOFLOW_REQUEST_BYTES} bytes"
            )
        return raw


# The observation fields of one READY sample, in bridge-attach order. Every
# field is optional on the model so a refusal frame parses; a READY frame
# lacking any of them cannot parse.
_CARGOFLOW_SAMPLE_FIELDS = (
    "anchor",
    "tick",
    "day",
    "year",
    "month",
    "day_of_month",
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


class CargoFlowReadback(Contract):
    """One protocol-10 sample response (strict success/refusal field subsets).

    The handler echoes the request correlation keys, ``funds`` and a status
    literal. Success frames carry the complete 24-field observation set — the
    anchor they latched, the clock facts (tick, day, year, month, day of
    month), both stockpiles, the per-source waiting and planned families at
    both stops, the waiting counts, and the monthly production and
    transported levels of both industries. Refusal frames carry none of that
    observation set (a spoofed hybrid is refused on the wire). Native fact
    families ride verbatim: production, transported and the industry
    stockpiles may read the 15.3 ``-1`` fact (E65 — an industry without a
    produced/accepted slot for the measured cargo returns -1, never a
    count), bounded at greater than or equal to it; every measured waiting,
    planned and count value is bounded non-negative.
    """

    protocol: Literal[10] = 10
    op: CargoFlowOp
    request_id: str
    plan: Digest
    company: CompanyID
    max_cost: Money
    pickup: TileID
    delivery: TileID
    depot: TileID
    offset: Annotated[StrictInt, Field(ge=0, le=CARGOFLOW_OFFSET_CAP)]
    status: CargoFlowStatus
    funds: SignedMoney
    cost: Money
    anchor: Annotated[StrictInt, Field(ge=0, le=2147483647)] | None = None
    tick: Annotated[StrictInt, Field(ge=0, le=2147483647)] | None = None
    day: Annotated[StrictInt, Field(ge=0, le=2147483647)] | None = None
    year: Annotated[StrictInt, Field(ge=0, le=2147483647)] | None = None
    month: Annotated[StrictInt, Field(ge=1, le=12)] | None = None
    day_of_month: Annotated[StrictInt, Field(ge=1, le=31)] | None = None
    stock_pickup: Annotated[StrictInt, Field(ge=-1, le=65535)] | None = None
    stock_bay: Annotated[StrictInt, Field(ge=-1, le=65535)] | None = None
    wait_pickup: Annotated[StrictInt, Field(ge=0, le=2147483647)] | None = None
    wait_pickup_from0: Annotated[StrictInt, Field(ge=0, le=2147483647)] | None = None
    wait_pickup_from1: Annotated[StrictInt, Field(ge=0, le=2147483647)] | None = None
    wait_bay: Annotated[StrictInt, Field(ge=0, le=2147483647)] | None = None
    wait_bay_from0: Annotated[StrictInt, Field(ge=0, le=2147483647)] | None = None
    wait_bay_from1: Annotated[StrictInt, Field(ge=0, le=2147483647)] | None = None
    count_pickup: Annotated[StrictInt, Field(ge=0, le=2147483647)] | None = None
    count_bay: Annotated[StrictInt, Field(ge=0, le=2147483647)] | None = None
    planned_pickup_from0: Annotated[StrictInt, Field(ge=0, le=2147483647)] | None = None
    planned_pickup_from1: Annotated[StrictInt, Field(ge=0, le=2147483647)] | None = None
    planned_bay_from0: Annotated[StrictInt, Field(ge=0, le=2147483647)] | None = None
    planned_bay_from1: Annotated[StrictInt, Field(ge=0, le=2147483647)] | None = None
    prod_pickup: Annotated[StrictInt, Field(ge=-1, le=2147483647)] | None = None
    prod_bay: Annotated[StrictInt, Field(ge=-1, le=2147483647)] | None = None
    trans_pickup: Annotated[StrictInt, Field(ge=-1, le=2147483647)] | None = None
    trans_bay: Annotated[StrictInt, Field(ge=-1, le=2147483647)] | None = None

    @property
    def digest(self) -> str:
        return hashlib.sha256(canonical_bytes(self)).hexdigest()

    @model_validator(mode="after")
    def coherent(self) -> CargoFlowReadback:
        if self.op != "sample":
            raise ValueError("unknown cargo-flow op")
        present = {field for field in _CARGOFLOW_SAMPLE_FIELDS if getattr(self, field) is not None}
        if self.status == "READY":
            missing = {field for field in _CARGOFLOW_SAMPLE_FIELDS if getattr(self, field) is None}
            if missing:
                raise ValueError(f"sample success readback lacks {sorted(missing)}")
            self._check_day_ladder()
        elif self.status in _CARGOFLOW_WINDOW_ECHO_STATUS:
            outside = present - set(_CARGOFLOW_WINDOW_ECHO_FIELDS)
            if outside:
                raise ValueError(
                    f"{self.status} carries fields outside its window echo "
                    f"subset: {sorted(outside)}"
                )
        elif self.status in _CARGOFLOW_REFUSAL_STATUS:
            if present:
                raise ValueError("refusal readback carries an unclaimed observation set")
        else:
            raise ValueError("unknown cargo-flow status")
        return self

    def _check_day_ladder(self) -> None:
        """A READY sample sits exactly one planned ladder step from its anchor."""
        anchor = self.anchor
        day = self.day
        if anchor is None or day is None:
            raise ValueError("a sample readback must carry its clock")
        expected = _CARGOFLOW_OFFSET_BY_ID.get(self.request_id)
        if (day - anchor) != expected:
            raise ValueError(
                f"sample day ladder diverged: day - anchor = {day - anchor}, "
                f"planned ladder step {expected}"
            )

    @classmethod
    def parse_for(cls, request: CargoFlowRequest, raw: bytes):
        if len(raw) > MAX_CARGOFLOW_RESPONSE_BYTES:
            raise ValueError(
                f"cargo-flow response exceeds {MAX_CARGOFLOW_RESPONSE_BYTES} bytes"
            )

        def unique(pairs):
            result = {}
            for key, value in pairs:
                if key in result:
                    raise ValueError("duplicate response key")
                result[key] = value
            return result

        value = json.loads(raw, object_pairs_hook=unique)
        criteria = cls.model_validate(value)
        correlated = ("protocol", "op", "request_id", "plan", "company", "max_cost", "offset")
        if any(getattr(criteria, k) != getattr(request, k) for k in correlated):
            raise ValueError("cargo-flow response correlation mismatch")
        for key in ("pickup", "delivery", "depot"):
            if getattr(criteria, key) != getattr(request, key):
                raise ValueError("cargo-flow response pin mismatch")
        return criteria


def verify_request_against_cargoflow_plan(
    request: CargoFlowRequest, *, plan: CargoFlowPlan, seal: str
) -> None:
    """Refuse a request that is not bound to the local probe plan.

    Python is the trust anchor: every request must present the staged seal,
    the pinned corridor identity and exactly its planned ladder offset. This
    runs before any byte reaches the Admin session.
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
    if request.offset != _CARGOFLOW_OFFSET_BY_ID.get(request.request_id):
        raise ValueError("request offset drifted from the planned ladder")


_OBSERVATION_KINDS = ("MEASURED", "REFUSED", "MISSING", "MALFORMED")


def _cargoflow_state() -> dict:
    return dict(
        index=0,
        anchor=None,
        samples={},
        ledger=[],
        funds=None,
    )


def _series_table(samples: dict) -> dict:
    """The per-field sampled series as facts, keyed by ladder step order."""
    keys = sorted(samples)
    series: dict[str, list[int]] = {}
    for name in _CARGOFLOW_SAMPLE_FIELDS:
        values = [int(samples[offset][name]) for offset in keys]
        series[name] = values
    return series


def cargoflow_verdict(series: dict) -> dict:
    """The offline dispatch verdict from the sampled series alone.

    The three terminal observations of the approved design record, sliced in
    exactly-conservative order:

    - ``DISPATCH_OBSERVED_LATE`` — the pickup stop's waiting rose above its
      own anchor sample at any later sample (H3);
    - ``DISPATCH_REFUSED_AT_SELECTOR`` — a measured stockpile rose while the
      pickup waiting never rose (H2, with the H4 route-elsewhere ambiguity
      inside it; the per-source series is the recorded evidence both share);
    - ``DISPATCH_STOCKPILE_STATIC`` — neither a stockpile nor the pickup
      waiting ever rose above the anchor sample (H1 across the span).

    A ladder that never sampled the discriminator fields can decide nothing.
    """
    required = ("wait_pickup", "stock_pickup", "stock_bay")
    if any(name not in series for name in required):
        return dict(
            verdict="CARGOFLOW_GATE_UNDECIDED_INCOMPLETE",
            statement=(
                "an unobserved stock/load series can decide nothing; this is "
                "a recorded fact, never a manufactured verdict"
            ),
        )
    wait_pickup = series["wait_pickup"]
    stock_pickup = series["stock_pickup"]
    stock_bay = series["stock_bay"]
    wait_rose = any(later > wait_pickup[0] for later in wait_pickup[1:])
    stock_rose = any(
        later > first
        for series_row in (stock_pickup, stock_bay)
        for later, first in zip(series_row[1:], series_row, strict=False)
    )
    if wait_rose:
        return dict(
            verdict="DISPATCH_OBSERVED_LATE",
            statement=(
                "the pickup stop's waiting rose above its anchor sample inside "
                "the span: the industry-to-station dispatch exists and was "
                "later than the freight watches of record"
            ),
        )
    if stock_rose:
        return dict(
            verdict="DISPATCH_REFUSED_AT_SELECTOR",
            statement=(
                "a measured stockpile rose while the pickup waiting never "
                "rose: the industry-side dispatch path closed before the "
                "pickup stop received cargo (the refused-at-selector family, "
                "H2/H4 per the design record §3.1)"
            ),
        )
    return dict(
        verdict="DISPATCH_STOCKPILE_STATIC",
        statement=(
            "no measured stockpile nor pickup waiting ever rose above its "
            "anchor sample: the production-to-stockpile path itself stayed "
            "closed across the sampled span (H1)"
        ),
    )


def _cargoflow_read_step(
    state: dict,
    request: CargoFlowRequest,
    readback: CargoFlowReadback,
    *,
    plan: CargoFlowPlan,
    seal: str,
) -> dict:
    """Verify one ordered sample against the accumulated probe state."""
    plan_ids = plan.schedule
    expected = plan_ids[state["index"]]
    if request.request_id != expected or readback.request_id != expected:
        raise ValueError(f"cargo-flow exchange out of order: expected {expected}")
    verify_request_against_cargoflow_plan(request, plan=plan, seal=seal)
    if readback.status != "READY":
        raise ValueError(f"cargo-flow exchange {expected} ended {readback.status}")
    if readback.funds != plan.expected_funds:
        raise ValueError("cargo-flow funds must equal the close-out level exactly")
    if readback.cost != 0:
        raise ValueError("cargo-flow samples must observe at zero cost")
    if state["anchor"] is None:
        state["anchor"] = readback.anchor
    elif readback.anchor != state["anchor"]:
        raise ValueError(
            f"the sampled clock anchor drifted across the ladder: "
            f"{state['anchor']} then {readback.anchor}"
        )
    offset = int(request.offset)
    sample = {name: getattr(readback, name) for name in _CARGOFLOW_SAMPLE_FIELDS}
    state["samples"][offset] = sample
    state["ledger"].append(
        dict(
            exchange=request.request_id,
            op=request.op,
            status=readback.status,
            funds=readback.funds,
            offset=offset,
        )
    )
    state["funds"] = readback.funds
    state["index"] += 1
    return dict(
        schema="cargo-flow-sample-receipt-v1",
        request_id=readback.request_id,
        op=request.op,
        plan_digest=plan.digest,
        seal=seal,
        offset=offset,
        status=readback.status,
        funds=readback.funds,
        anchor=readback.anchor,
        day=readback.day,
        year=readback.year,
        month=readback.month,
        day_of_month=readback.day_of_month,
        sample=sample,
        verification="CARGOFLOW_SAMPLE_MEASURED",
    )


def cargoflow_phase_outcome(
    exchanges: Sequence[tuple[CargoFlowRequest, CargoFlowReadback | Exception]],
    *,
    prelaunch_digest: str,
    plan: CargoFlowPlan,
) -> dict:
    """Fail-closed probe verification over preserved evidence only.

    Each exchange is ``(request, readback_or_error)``; an error element is an
    observation whose bytes never parsed or correlated (malformed, stale,
    torn or duplicate). The first halted exchange ends verification: earlier
    receipts are preserved, later exchanges are pending, and an unfinished
    ladder can never manufacture success or a dispatch verdict.
    """
    receipts: list[dict] = []
    failed = None
    state = _cargoflow_state()
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
                _cargoflow_read_step(
                    state, request, readback, plan=plan, seal=prelaunch_digest
                )
            )
        except Exception as error:  # noqa: BLE001 - fail closed on any defect
            failed = dict(
                label=request.request_id,
                status=str(getattr(readback, "status", "UNKNOWN")),
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
    series = _series_table(state["samples"])
    calendar = sorted(
        {(int(sample["year"]), int(sample["month"])) for sample in state["samples"].values()}
    )
    return dict(
        schema="cargo-flow-phase-outcome-v1",
        seal=prelaunch_digest,
        plan_digest=plan.digest,
        receipts=receipts,
        failed=failed,
        pending=pending,
        anchor=state["anchor"],
        offset_ladder=list(CARGOFLOW_SAMPLE_OFFSETS),
        samples=state["samples"],
        series=series,
        sampled_months=[[year, month] for year, month in calendar],
        verdict=cargoflow_verdict(series),
        observation_kinds=_OBSERVATION_KINDS,
        verification="CARGOFLOW_COMPLETE" if complete else "CARGOFLOW_INCOMPLETE",
    )
