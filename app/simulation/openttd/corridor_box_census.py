"""Native corridor box-census wire contract (protocol 9, additive).

Milestone D5-BOX-CENSUS-1: the branch-8 finding (E58) left the v2 site gate's
exactly-one discovery boxes unresolved from retained evidence, so the next
authority-gated step is a strictly read-only census over the authoritative A1
close-out world that enumerates the industries inside each stop's radius-3
discovery box. This module is the protocol-9 wire contract for that census
(``docs/d5-box-census-1-protocol-design-2026-11-02.md``, E59): typed
requests, fail-closed response parsing, one pinned ten-exchange schedule, and
a fail-closed phase verifier that distinguishes a measured box membership
from a missing, malformed, stale, divergent or inconclusive observation.

The census is pure observation. Three ops re-measure the E49 instruments
byte-comparably (radius, the two pinned spot acceptances, the pickup
production control — each a halt-on-divergence chain-continuity control
except the measured radius, which is recorded as a fact); the new ``box`` op
mirrors the v2 gate's ``DiscoveryBoxes`` scan exactly: a fresh radius read,
the 7x7 tile box in ``DiscoveryBoxes`` iteration order, and one row per
distinct industry ``{id, tile = minimum member tile, p, a}`` where
``p = GSIndustry.GetLastMonthProduction`` and ``a = GSIndustry.IsCargoAccepted``
(0 = not accepted, 1 = accepted, 2 = temporary refusal). Roles are derived
Python-side — producer iff ``p > 0``, acceptor iff ``a == 1`` — matching the
v2 gate verbatim, so the branch-8 verdict is offline-replayable from rows.
The census enforces no exactly-one condition anywhere: an empty box, a
multi-industry box and a page-3 overflow are all recorded findings, and a
drained page is a measurement of absence, never a refusal.

Protocol 9 stays additive over protocols 5/6/7/8 (the number allocation of
record: 4 construction, 5 freight v1, 6 accept-survey, 7 terrain survey,
8 freight v2): the GameScript bridge dispatches protocol-9 tables through a
separate guarded census handler shipped in its own package directory
(``d5_census_package``), so the frozen ``d5_freight_package`` source the E47
staged composition pinned never drifts. Named constants (E33's lesson):
request and response bodies are canonical UTF-8 JSON bounded by
MAX_CENSUS_REQUEST_BYTES / MAX_CENSUS_RESPONSE_BYTES (512 each — the largest
box response carries three worst-width rows, measured at 431 bytes, a
comfortable margin). Tile bounds are 256x256-safe (``TileID <= 65535``),
imported from corridor_construction. The world is the same pinned Seed-17
corridor world as protocol 6: the consumed A1 extension after-save.
"""

import hashlib
import json
from collections.abc import Sequence
from typing import Annotated, Literal

from pydantic import Field, StrictInt, model_validator

from app.planning.canonical import canonical_bytes
from app.planning.domain import Contract, Digest
from app.simulation.openttd.corridor_construction import (
    CompanyID,
    Money,
    SignedMoney,
    TileID,
)

CENSUS_PROTOCOL = 9
# Small bodies: the largest request carries one box centre and its page
# cursor (217 bytes measured worst case), the largest response one page of
# three worst-width box rows (431 bytes measured). 512 is the survey-6 and
# protocol-8 precedent bound.
MAX_CENSUS_REQUEST_BYTES = 512
MAX_CENSUS_RESPONSE_BYTES = 512
# Native eighths (0..8), the bounded truck-stop coverage radius readback and
# the bounded industry scan (the v2 DiscoveryBoxes: radius must read 1..8 or
# the GameScript scan refuses with an unsupported-native-fact halt).
MAX_CENSUS_RADIUS = 255
CENSUS_MAX_SCAN_RADIUS = 8
CENSUS_MAP_WIDTH = 256
CENSUS_MAP_HEIGHT = 256
CENSUS_MAX_TILE_ID = CENSUS_MAP_WIDTH * CENSUS_MAP_HEIGHT - 1
PLANNED_CENSUS_EXCHANGES = 10
CENSUS_REQUEST_BUDGET = 32
CENSUS_COMPANY = 0
CENSUS_CARGO_ID = 1
CENSUS_PICKUP_INDUSTRY = 0
FUNDS_AT_A1_CLOSE = 490257

# The pinned corridor world every census request echoes (the consumed A1
# extension after-save geometry; the pins reuse the protocol-5/6 D4 lineage
# identity — the census never queries an un-pinned tile).
CENSUS_PICKUP_TILE = 45748
CENSUS_PICKUP_FRONT_TILE = 45747
CENSUS_DELIVERY_TILE = 50351
CENSUS_DELIVERY_FRONT_TILE = 50095
CENSUS_DEPOT_TILE = 45487
CENSUS_DEPOT_FRONT_TILE = 45743

# The pinned box centres: the v2 pickup stop (its producer box) and the A1
# bay stop 50862 that E58's accepted design re-pins as the D5-FREIGHT-4
# delivery stop (its acceptor box). The centre roles of record match the v2
# gate's own filters: producer iff p > 0, acceptor iff a == 1.
CENSUS_PICKUP_CENTRE = CENSUS_PICKUP_TILE
CENSUS_DELIVERY_CENTRE = 50862
CENSUS_BOX_CENTRES: tuple[int, ...] = (CENSUS_PICKUP_CENTRE, CENSUS_DELIVERY_CENTRE)
CENSUS_CENTRE_ROLES: dict[int, str] = {
    CENSUS_PICKUP_CENTRE: "producer",
    CENSUS_DELIVERY_CENTRE: "acceptor",
}

# The pinned chain-continuity spot tiles of record (E49 re-measures): the
# D4 delivery stop control, expected zero, then the A1 bay stop, expected 8.
CENSUS_SPOT_CONTROL_TILE = CENSUS_DELIVERY_TILE
CENSUS_SPOT_STOP_TILE = CENSUS_DELIVERY_CENTRE
CENSUS_SPOT_TILES: tuple[int, ...] = (CENSUS_SPOT_CONTROL_TILE, CENSUS_SPOT_STOP_TILE)
SPOT_EXPECTED_PROD = 104
SPOT_PROD_EXCHANGE = "prod-00"

# Box pagination of record (E59 §3.1/§3.2): three rows per page, three pages
# per box on the static cursor grid; a page beyond the drained membership is
# READY-empty (absence is a measurement) and a third page still reporting
# ``more = true`` is an explicit overflow finding (>= 10 distinct industries
# in one box), never a failure and never a silent discard.
MAX_BOX_PAGE_ROWS = 3
MAX_BOX_PAGES = 3
BOX_PAGE_CURSORS: tuple[int, ...] = (0, 3, 6)
BOX_MEMBERSHIP_LIMIT = MAX_BOX_PAGE_ROWS * MAX_BOX_PAGES

CENSUS_OPS = ("radius", "accept", "prod", "box")

CensusOp = Literal["accept", "box", "prod", "radius"]
# Waiting on the bridge: protocol 9 keeps the frozen survey-6 status family.
CensusStatus = Literal[
    "READY",
    "UNSUPPORTED_NATIVE_FACT",
    "INVALID_LOCATION",
    "INVALID_COMPANY",
    "PAUSED",
    "STALE_PIN",
    "OUT_OF_ORDER",
]
# Single identity of record (E59 §6): the census has one attempt, one
# prelaunch schema and one read-only schema; a re-run attempt of the lineage
# would need its own design record of record first (open question 5).
CENSUS_ATTEMPT_SCHEMA_VERSION = 1

_CENSUS_SEQUENCE: tuple[tuple[str, CensusOp, int | None, int | None], ...] = (
    ("radius-00", "radius", None, None),
    ("acc-00", "accept", CENSUS_SPOT_CONTROL_TILE, 0),
    ("acc-01", "accept", CENSUS_SPOT_STOP_TILE, 8),
    (SPOT_PROD_EXCHANGE, "prod", None, None),
    ("pbox-00", "box", CENSUS_PICKUP_CENTRE, 0),
    ("pbox-01", "box", CENSUS_PICKUP_CENTRE, 3),
    ("pbox-02", "box", CENSUS_PICKUP_CENTRE, 6),
    ("dbox-00", "box", CENSUS_DELIVERY_CENTRE, 0),
    ("dbox-01", "box", CENSUS_DELIVERY_CENTRE, 3),
    ("dbox-02", "box", CENSUS_DELIVERY_CENTRE, 6),
)
CENSUS_EXCHANGE_IDS: tuple[str, ...] = tuple(row[0] for row in _CENSUS_SEQUENCE)
_CENSUS_OP_BY_ID: dict[str, CensusOp] = {row[0]: row[1] for row in _CENSUS_SEQUENCE}
# The pinned spot mapping: exchange -> (queried tile, expected acceptance).
SPOT_EXCHANGE_TILES: dict[str, int] = {
    row[0]: row[2] for row in _CENSUS_SEQUENCE if row[1] == "accept"
}
SPOT_EXPECTED_ACCEPTS: dict[str, int] = {
    row[0]: row[3] for row in _CENSUS_SEQUENCE if row[1] == "accept"
}
# The pinned box mapping: exchange -> (centre tile, page cursor).
BOX_EXCHANGE_SPECS: dict[str, tuple[int, int]] = {
    row[0]: (row[2], row[3]) for row in _CENSUS_SEQUENCE if row[1] == "box"
}
_CENSUS_SUCCESS_STATUS: dict[CensusOp, str] = {op: "READY" for op in CENSUS_OPS}
_CENSUS_REFUSAL_STATUS = frozenset(
    {
        "UNSUPPORTED_NATIVE_FACT",
        "INVALID_LOCATION",
        "INVALID_COMPANY",
        "PAUSED",
        "STALE_PIN",
        "OUT_OF_ORDER",
    }
)

if (
    len(CENSUS_EXCHANGE_IDS) != PLANNED_CENSUS_EXCHANGES
    or len(set(CENSUS_EXCHANGE_IDS)) != PLANNED_CENSUS_EXCHANGES
    or set(_CENSUS_OP_BY_ID.values()) != set(CENSUS_OPS)
    or SPOT_EXCHANGE_TILES != {"acc-00": 50351, "acc-01": 50862}
    or SPOT_EXPECTED_ACCEPTS != {"acc-00": 0, "acc-01": 8}
    or BOX_EXCHANGE_SPECS
    != {
        "pbox-00": (45748, 0),
        "pbox-01": (45748, 3),
        "pbox-02": (45748, 6),
        "dbox-00": (50862, 0),
        "dbox-01": (50862, 3),
        "dbox-02": (50862, 6),
    }
    or CENSUS_BOX_CENTRES != (45748, 50862)
    or CENSUS_SPOT_TILES != (50351, 50862)
    or CENSUS_EXCHANGE_IDS[:4] != ("radius-00", "acc-00", "acc-01", SPOT_PROD_EXCHANGE)
):
    raise RuntimeError("box census exchange schedule drifted from the pinned observations")


class BoxCensusPlan(Contract):
    """The pinned identities and ordered observations of one census attempt.

    The plan binds the authoritative A1 after-save identity: the corridor
    pins funds and world exactly as protocol 6 does, the spot tiles in
    schedule order (control first), the box centres with their page
    geometry, and the ten-exchange schedule. Staging and sealing remain the
    adopted ceremony's gates; this plan types what those stages must bind.
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
    pickup_industry: Annotated[StrictInt, Field(ge=0, le=65535)]
    expected_funds: Money
    spots: tuple[TileID, ...]
    box_centres: tuple[TileID, ...]
    box_page_rows: Annotated[StrictInt, Field(ge=1, le=MAX_BOX_PAGE_ROWS)]
    schedule: tuple[str, ...]
    request_budget: Annotated[StrictInt, Field(gt=0, le=CENSUS_REQUEST_BUDGET)] = (
        CENSUS_REQUEST_BUDGET
    )

    @property
    def digest(self) -> str:
        return hashlib.sha256(canonical_bytes(self)).hexdigest()

    @model_validator(mode="after")
    def coherent(self) -> BoxCensusPlan:
        if self.company != CENSUS_COMPANY or self.cargo != CENSUS_CARGO_ID:
            raise ValueError("the box census drives company 0 with cargo 1")
        if (self.pickup, self.pickup_front) != (CENSUS_PICKUP_TILE, CENSUS_PICKUP_FRONT_TILE):
            raise ValueError("pickup pins drifted from the D4 corridor stops")
        if (self.delivery, self.delivery_front) != (
            CENSUS_DELIVERY_TILE,
            CENSUS_DELIVERY_FRONT_TILE,
        ):
            raise ValueError("delivery pins drifted from the D4 corridor stops")
        if (self.depot, self.depot_front) != (CENSUS_DEPOT_TILE, CENSUS_DEPOT_FRONT_TILE):
            raise ValueError("depot pins drifted from the D4 corridor depot")
        if self.pickup_industry != CENSUS_PICKUP_INDUSTRY:
            raise ValueError("the pickup control observes industry 0 only")
        if self.expected_funds != FUNDS_AT_A1_CLOSE:
            raise ValueError("the plan binds the A1 close-out funds exactly")
        if self.spots != CENSUS_SPOT_TILES:
            raise ValueError("spots drifted from the pinned control-first tile list")
        if self.box_centres != CENSUS_BOX_CENTRES:
            raise ValueError("box centres drifted from the pinned pickup-then-A1-stop list")
        if self.box_page_rows != MAX_BOX_PAGE_ROWS:
            raise ValueError("box page geometry drifted from the pinned three-row pages")
        if self.schedule != CENSUS_EXCHANGE_IDS:
            raise ValueError("schedule drifted from the planned ten census exchanges")
        return self


def box_census_plan() -> BoxCensusPlan:
    """The pinned D5-BOX-CENSUS-1 plan derived from the module's own pins."""
    return BoxCensusPlan(
        company=CENSUS_COMPANY,
        cargo=CENSUS_CARGO_ID,
        pickup=CENSUS_PICKUP_TILE,
        pickup_front=CENSUS_PICKUP_FRONT_TILE,
        delivery=CENSUS_DELIVERY_TILE,
        delivery_front=CENSUS_DELIVERY_FRONT_TILE,
        depot=CENSUS_DEPOT_TILE,
        depot_front=CENSUS_DEPOT_FRONT_TILE,
        pickup_industry=CENSUS_PICKUP_INDUSTRY,
        expected_funds=FUNDS_AT_A1_CLOSE,
        spots=CENSUS_SPOT_TILES,
        box_centres=CENSUS_BOX_CENTRES,
        box_page_rows=MAX_BOX_PAGE_ROWS,
        schedule=CENSUS_EXCHANGE_IDS,
    )


class CensusRequest(Contract):
    """One protocol-9 census exchange request (fixed correlation stride).

    Every request carries the corridor identity pins (defence in depth: the
    native handler refuses a drifted pin before any observation), the
    uniform ``plan`` seal digest, and — on ``accept`` exactly — the one spot
    tile it queries, and — on ``box`` exactly — the pinned box centre and
    its page cursor. ``max_cost`` is 0 on every census exchange: the census
    has no cost-bearing operation of any kind.
    """

    protocol: Literal[9] = 9
    op: CensusOp
    request_id: Annotated[str, Field(pattern=r"^[a-z0-9-]{1,32}$")]
    plan: Digest
    company: CompanyID
    max_cost: Annotated[StrictInt, Field(ge=0, le=0)]
    pickup: TileID
    delivery: TileID
    depot: TileID
    tile: TileID | None = None
    cursor: Annotated[StrictInt, Field(ge=0, le=65535)] | None = None

    @model_validator(mode="after")
    def coherent(self) -> CensusRequest:
        if self.op in ("accept", "box"):
            if self.tile is None:
                raise ValueError("accept and box exchanges carry exactly one pinned tile")
            if self.op == "accept":
                if self.tile not in CENSUS_SPOT_TILES:
                    raise ValueError("accept exchanges may only query the pinned spot tiles")
            elif self.tile not in CENSUS_BOX_CENTRES:
                raise ValueError("box exchanges may only query the pinned box centres")
            if self.op == "box":
                if self.cursor is None:
                    raise ValueError("box exchanges carry their page cursor")
                if self.cursor not in BOX_PAGE_CURSORS:
                    raise ValueError("box page cursors sit on the pinned static grid")
        else:
            if self.tile is not None:
                raise ValueError("only the accept and box ops carry a tile")
        if self.op != "box" and self.cursor is not None:
            raise ValueError("only the box op carries a cursor")
        return self

    def to_bytes(self) -> bytes:
        raw = canonical_bytes(self)
        if len(raw) > MAX_CENSUS_REQUEST_BYTES:
            raise ValueError(f"census request exceeds {MAX_CENSUS_REQUEST_BYTES} bytes")
        return raw


class CensusRow(Contract):
    """One reported industry membership row of a box page.

    ``id`` is the native industry id, ``tile`` the minimum tile index of the
    industry's box tiles (the deterministic anchor of the deterministic
    scan), ``p`` the last-month production of cargo 1 — exactly ``-1`` is
    the 15.3 native fact that the industry does not handle this cargo as
    produced (``ScriptIndustry::GetLastMonthProduction`` returns ``-1`` and
    never a count there), any other negative native read stays an
    unsupported native fact, never a row — and ``a`` the cargo-1 acceptance
    state (0 not accepted, 1 accepted, 2 temporary refusal). Roles are
    never carried here: they are derived Python-side (producer iff
    ``p > 0``, acceptor iff ``a == 1``), so the ``-1`` fact neither creates
    nor removes any role-filtered membership.
    """

    id: Annotated[StrictInt, Field(ge=0, le=65535)]
    tile: TileID
    p: Annotated[StrictInt, Field(ge=-1, le=2147483647)]
    a: Annotated[StrictInt, Field(ge=0, le=2)]


_CENSUS_FIELDS = (
    "radius",
    "accept",
    "prod",
)
_CENSUS_BOX_DATA_FIELDS = frozenset({"count", "more", "rows"})

_CENSUS_SUBSETS: dict[CensusOp, frozenset[str]] = {
    "radius": frozenset(("radius",)),
    "accept": frozenset(("accept", "radius")),
    "prod": frozenset(("prod",)),
    "box": frozenset(),
}
# Tile echoes: the accept response must echo the spot it observed and the
# box response must echo its pinned centre, so a stale or cross-tile
# readback can never be mistaken for a fresh one. The cursor echo rides on
# box frames exactly like the tile echo (the handler attaches both before
# the refusal ladder, so refusals carry the echoes and never the data).
_TILE_ECHO_OPS = frozenset({"accept", "box"})


class CensusReadback(Contract):
    """One protocol-9 census exchange response (strict per-op field subsets).

    The handler echoes the request correlation keys, ``funds`` and a status
    literal. Success frames carry the complete op subset — for ``box`` the
    echoed centre and cursor, the page's deterministic ``rows`` slice of one
    ``count``, and the ``more`` flag. Refusal frames carry none of that
    observation set (a spoofed hybrid is refused on the wire). Every
    success value is domain-checked here: box rows must ascend by industry
    id, sit on the pinned cursor grid and satisfy the ``more`` page formula;
    a value outside any row domain can never parse, so the fail-closed
    surface cannot accidentally record it as measured.
    """

    protocol: Literal[9] = 9
    op: CensusOp
    request_id: str
    plan: Digest
    company: CompanyID
    max_cost: Money
    pickup: TileID
    delivery: TileID
    depot: TileID
    tile: TileID | None = None
    cursor: Annotated[StrictInt, Field(ge=0, le=65535)] | None = None
    status: CensusStatus
    funds: SignedMoney
    cost: Money
    radius: Annotated[StrictInt, Field(ge=0, le=MAX_CENSUS_RADIUS)] | None = None
    accept: Annotated[StrictInt, Field(ge=0, le=8)] | None = None
    prod: Annotated[StrictInt, Field(ge=0, le=2147483647)] | None = None
    count: Annotated[StrictInt, Field(ge=0, le=65535)] | None = None
    more: bool | None = None
    rows: tuple[CensusRow, ...] | None = None

    @property
    def digest(self) -> str:
        return hashlib.sha256(canonical_bytes(self)).hexdigest()

    @model_validator(mode="after")
    def coherent(self) -> CensusReadback:
        if self.op not in _CENSUS_SUCCESS_STATUS:
            raise ValueError("unknown census op")
        subset = _CENSUS_SUBSETS[self.op]
        present = {field for field in _CENSUS_FIELDS if getattr(self, field) is not None}
        box_data = {
            field for field in _CENSUS_BOX_DATA_FIELDS if getattr(self, field) is not None
        }
        if self.op == "box":
            if present:
                raise ValueError(
                    f"{self.op} readback carries fields outside its subset: {sorted(present)}"
                )
            if self.status == _CENSUS_SUCCESS_STATUS[self.op]:
                missing = {
                    field for field in _CENSUS_BOX_DATA_FIELDS if getattr(self, field) is None
                }
                if missing:
                    raise ValueError(f"{self.op} success readback lacks {sorted(missing)}")
                if self.tile is None:
                    raise ValueError("box success must echo its pinned centre")
                if self.cursor is None:
                    raise ValueError("box success must echo its page cursor")
                if self.cursor not in BOX_PAGE_CURSORS:
                    raise ValueError("box page cursors sit on the pinned static grid")
                rows = self.rows or ()
                if len(rows) > MAX_BOX_PAGE_ROWS:
                    raise ValueError("a box page carries more than its pinned row budget")
                ids = [row.id for row in rows]
                if any(later <= earlier for earlier, later in zip(ids, ids[1:], strict=False)):
                    raise ValueError("box rows must ascend by industry id")
                page_count = self.count
                page_cursor = self.cursor
                if page_cursor is None or page_count is None:
                    raise ValueError("box page accounting lacks its cursor or count")
                if self.more != (page_count > page_cursor + len(rows)):
                    raise ValueError("box page more flag drifted from its own membership")
            elif self.status not in _CENSUS_REFUSAL_STATUS:  # pragma: no cover - literal exhausts
                raise ValueError("unknown census status")
            elif box_data:
                raise ValueError("refusal readback carries an unclaimed observation set")
            return self
        if box_data:
            raise ValueError("box data fields ride the box op only")
        if self.cursor is not None:
            raise ValueError("a page cursor echo rides the box op only")
        if self.status not in _CENSUS_REFUSAL_STATUS:
            outside = present - subset
            if outside:
                raise ValueError(
                    f"{self.op} readback carries fields outside its subset: {sorted(outside)}"
                )
            missing = subset - present
            if missing:
                raise ValueError(f"{self.op} success readback lacks {sorted(missing)}")
            if self.op == "accept":
                if self.tile is None:
                    raise ValueError("accept success must echo its observed spot tile")
                if self.radius is None:
                    raise ValueError("accept success must echo its native radius")
        elif self.status not in _CENSUS_REFUSAL_STATUS:  # pragma: no cover - literal exhausts
            raise ValueError("unknown census status")
        elif present:
            raise ValueError("refusal readback carries an unclaimed observation set")
        if self.op in ("radius", "prod") and self.tile is not None:
            raise ValueError("radius and production readbacks must not name a tile")
        return self

    @classmethod
    def parse_for(cls, request: CensusRequest, raw: bytes):
        if len(raw) > MAX_CENSUS_RESPONSE_BYTES:
            raise ValueError(f"census response exceeds {MAX_CENSUS_RESPONSE_BYTES} bytes")

        def unique(pairs):
            result = {}
            for key, value in pairs:
                if key in result:
                    raise ValueError("duplicate response key")
                result[key] = value
            return result

        value = json.loads(raw, object_pairs_hook=unique)
        # Python-mode strict validation rejects lists for the box page's only
        # tuple field, while JSON mode accepts wire arrays: lift the rows
        # array to its tuple (element-wise StrictInt bounds still apply).
        if isinstance(value, dict) and isinstance(value.get("rows"), list):
            value["rows"] = tuple(value["rows"])
        criteria = cls.model_validate(value)
        correlated = ("protocol", "op", "request_id", "plan", "company", "max_cost")
        if any(getattr(criteria, k) != getattr(request, k) for k in correlated):
            raise ValueError("census response correlation mismatch")
        for key in ("pickup", "delivery", "depot"):
            if getattr(criteria, key) != getattr(request, key):
                raise ValueError("census response pin mismatch")
        if request.tile is not None and criteria.tile != request.tile:
            raise ValueError("census response tile echo mismatch")
        if request.cursor is not None and criteria.cursor != request.cursor:
            raise ValueError("census response cursor echo mismatch")
        return criteria


def verify_request_against_census_plan(
    request: CensusRequest, *, plan: BoxCensusPlan, seal: str
) -> None:
    """Refuse a request that is not bound to the local census plan.

    Python is the trust anchor: every request must present the staged seal,
    the pinned corridor identity and — for ``accept`` — exactly the pinned
    spot tile of its scheduled exchange and — for ``box`` — exactly the
    pinned centre and page cursor of its scheduled exchange. This runs
    before any byte reaches the Admin session.
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
    if request.op == "accept":
        plan_ids = plan.schedule
        exchange_index = (
            plan_ids.index(request.request_id) if request.request_id in plan_ids else -1
        )
        expected = SPOT_EXCHANGE_TILES.get(request.request_id)
        if (
            exchange_index < 1
            or expected is None
            or request.tile != expected
            or request.tile != plan.spots[exchange_index - 1]
        ):
            raise ValueError("accept request tile drifted from the planned observation")
    if request.op == "box":
        plan_ids = plan.schedule
        exchange_index = (
            plan_ids.index(request.request_id) if request.request_id in plan_ids else -1
        )
        expected = BOX_EXCHANGE_SPECS.get(request.request_id)
        box_start = plan_ids.index("pbox-00")
        if (
            exchange_index < box_start
            or expected is None
            or (request.tile, request.cursor) != expected
            or request.tile not in plan.box_centres
        ):
            raise ValueError("box request drifted from the planned page specification")


_OBSERVATION_KINDS = ("MEASURED", "REFUSED", "MISSING", "MALFORMED")


def _census_state() -> dict:
    return dict(
        index=0,
        observations={},
        boxes={},
        ledger=[],
        funds=None,
    )


def _census_read_step(
    state: dict,
    request: CensusRequest,
    readback: CensusReadback,
    *,
    plan: BoxCensusPlan,
    seal: str,
) -> dict:
    """Verify one ordered census exchange against the accumulated state."""
    plan_ids = plan.schedule
    expected = plan_ids[state["index"]]
    if request.request_id != expected or readback.request_id != expected:
        raise ValueError(f"census exchange out of order: expected {expected}")
    verify_request_against_census_plan(request, plan=plan, seal=seal)
    if readback.status != "READY":
        raise ValueError(f"census exchange {expected} ended {readback.status}")
    if readback.funds != plan.expected_funds:
        raise ValueError("census funds must equal the A1 close-out level exactly")
    if readback.cost != 0:
        raise ValueError("census exchanges must observe at zero cost")
    # Paused and unpinned worlds are refused inside the handler; a correlated
    # READY reply is the only surface that may record a measurement.
    if request.op == "radius":
        # A measured radius is a fact of record, never a halt: the box scans
        # below re-derive their geometry from it and any divergent value is
        # validated there, row by row.
        state["radius"] = readback.radius
    if request.op == "prod":
        measured = readback.prod
        if measured != SPOT_EXPECTED_PROD:
            raise ValueError(
                f"the chain-continuity spot {request.request_id} diverged: "
                f"measured {measured}, expected {SPOT_EXPECTED_PROD}"
            )
        state["prod"] = measured
    if request.op == "accept":
        radius = state.get("radius")
        if radius is None:
            raise ValueError("acceptance requires the measured native radius first")
        expected_accept = SPOT_EXPECTED_ACCEPTS[request.request_id]
        if readback.accept != expected_accept:
            raise ValueError(
                f"the chain-continuity spot {request.request_id} diverged: "
                f"measured {readback.accept}, expected {expected_accept}"
            )
        tile = plan.spots[state["index"] - 1]
        state["observations"][tile] = dict(
            value=readback.accept,
            radius=radius,
            request_id=readback.request_id,
            digest=readback.digest,
        )
    if request.op == "box":
        page_centre = request.tile
        page_rows = readback.rows
        if page_centre is None or page_rows is None or readback.cursor is None:
            raise ValueError(f"census exchange {request.request_id} lacks its box page shape")
        radius = state.get("radius")
        if radius is None:
            raise ValueError("box scans require the measured native radius first")
        centre = int(page_centre)
        box: dict = state["boxes"].get(centre)
        if box is None:
            box = state["boxes"][centre] = dict(
                centre=centre,
                count=None,
                last_id=-1,
                rows=[],
                pages=[],
            )
        if box["count"] is not None and box["count"] != readback.count:
            raise ValueError(
                f"box membership count drifted across the pages of box {centre}: "
                f"{box['count']} then {readback.count}"
            )
        box["count"] = readback.count
        for row in page_rows:
            if row.id <= box["last_id"]:
                raise ValueError("box rows drifted ascending order across the pages of one box")
            box["last_id"] = row.id
            box["rows"].append(dict(id=row.id, tile=row.tile, p=row.p, a=row.a))
        geometry = census_box_geometry(radius, centre)
        for row in page_rows:
            if row.tile not in geometry:
                raise ValueError("a box row lies outside the measured scan box of its centre")
        box["pages"].append(
            dict(
                request_id=request.request_id,
                cursor=readback.cursor,
                more=readback.more,
                row_count=len(page_rows),
            )
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
    receipt = dict(
        schema="company-box-census-receipt-v1",
        request_id=readback.request_id,
        op=request.op,
        plan_digest=plan.digest,
        seal=seal,
        status=readback.status,
        funds=readback.funds,
        verification="CENSUS_OBSERVED",
    )
    if request.op == "accept":
        accept_tile = request.tile
        if accept_tile is None or readback.accept is None:
            raise ValueError(f"census exchange {request.request_id} lacks its accept shape")
        receipt = {
            **receipt,
            "tile": accept_tile,
            "accept": readback.accept,
            "radius": readback.radius,
        }
    elif request.op == "radius":
        if readback.radius is None:
            raise ValueError(f"census exchange {request.request_id} lacks its radius shape")
        receipt = {**receipt, "radius": readback.radius}
    elif request.op == "prod":
        if readback.prod is None:
            raise ValueError(f"census exchange {request.request_id} lacks its prod shape")
        receipt = {**receipt, "prod": readback.prod}
    else:
        page_rows = readback.rows
        if page_rows is None:
            raise ValueError(f"census exchange {request.request_id} lacks its box page rows")
        receipt = {
            **receipt,
            "tile": page_centre,
            "cursor": readback.cursor,
            "count": readback.count,
            "more": readback.more,
            "rows": [dict(row) for row in page_rows],
        }
    return receipt


def census_box_geometry(radius: int, centre: int) -> frozenset[int]:
    """Every tile a radius-``radius`` box centred on ``centre`` must contain.

    The same 256-wide decomposition the GameScript scan uses (``dy`` outer,
    ``dx`` inner, ascending), so the phase outcome can fail closed on any
    row outside the measured scan box without knowing Squirrel.
    """
    if not 0 <= centre <= CENSUS_MAX_TILE_ID:
        raise ValueError("a census box centre must sit on the pinned 256x256 map")
    if not 0 <= radius <= MAX_CENSUS_RADIUS:
        raise ValueError("a census box radius must read within the native domain")
    width = CENSUS_MAP_WIDTH
    tx, ty = centre % width, centre // width
    tiles = []
    for dy in range(-radius, radius + 1):
        if not 0 <= ty + dy < CENSUS_MAP_HEIGHT:
            continue
        for dx in range(-radius, radius + 1):
            if not 0 <= (tile := (ty + dy) * width + (tx + dx)) <= CENSUS_MAX_TILE_ID:
                continue
            if not 0 <= tx + dx < width:
                continue
            tiles.append(tile)
    return frozenset(tiles)


def _census_box_records(state: dict, plan: BoxCensusPlan) -> dict:
    """The per-box merge of one census attempt as facts, never verdicts.

    ``members`` lists every listed row in ``DiscoveryBoxes`` iteration order
    (ascending member tile, then id); ``role_filtered`` applies the centre's
    role filter of record to that order; ``overflow`` is the page-3
    ``more`` finding and nothing else.
    """
    records = {}
    for centre in plan.box_centres:
        centre = int(centre)
        role = CENSUS_CENTRE_ROLES[centre]
        box = state["boxes"].get(centre)
        if box is None:
            records[str(centre)] = dict(
                centre=centre,
                role=role,
                recorded=False,
                count=None,
                members=[],
                role_filtered=[],
                exactly_one=False,
                overflow=False,
                pages=[],
            )
            continue
        ordered = sorted(box["rows"], key=lambda row: (row["tile"], row["id"]))
        if role == "producer":
            filtered = [row for row in ordered if row["p"] > 0]
        else:
            filtered = [row for row in ordered if row["a"] == 1]
        records[str(centre)] = dict(
            centre=centre,
            role=role,
            recorded=True,
            count=box["count"],
            members=ordered,
            role_filtered=[dict(id=row["id"], tile=row["tile"]) for row in filtered],
            exactly_one=len(filtered) == 1,
            overflow=any(
                page["more"] is True and page["cursor"] == BOX_PAGE_CURSORS[-1]
                for page in box["pages"]
            ),
            pages=[dict(page) for page in box["pages"]],
        )
    return records


def _census_branch_verdict(records: dict, *, complete: bool) -> dict:
    """The offline branch-8 recompute from census rows alone.

    The v2 gate checks ``ids.len() == 1`` on both role-filtered boxes; the
    census re-derives that verdict from the listed rows as a fact of record.
    An overflow keeps the verdict explicitly undecided (the listed pages are
    partial evidence); an incomplete schedule can never manufacture a
    verdict. Nothing here is an admissibility claim.
    """
    if not complete or any(record["recorded"] is not True for record in records.values()):
        return dict(
            verdict="CENSUS_GATE_UNDECIDED_INCOMPLETE",
            statement=(
                "an unevidenced role-filtered membership can decide nothing; "
                "this is a recorded fact, never a manufactured verdict"
            ),
            role_counts={},
        )
    if any(record["overflow"] for record in records.values()):
        return dict(
            verdict="CENSUS_GATE_UNDECIDED_OVERFLOW",
            statement=(
                "a box reported more distinct industries than its pinned page "
                "budget lists; the role-filtered membership above is partial "
                "evidence, so the exactly-one verdict stays undecided"
            ),
            role_counts={},
        )
    role_counts = {
        record["role"]: len(record["role_filtered"]) for record in records.values()
    }
    gate = all(
        record["exactly_one"] and len(record["role_filtered"]) == 1
        for record in records.values()
    )
    return dict(
        verdict="CENSUS_GATE_PASSES" if gate else "CENSUS_GATE_FAILS",
        statement=(
            "the role-filtered recompute from the listed census rows matches "
            "the v2 gate's own exactly-one check on both boxes"
            if gate
            else "the role-filtered recompute lists a box whose membership is "
            "not exactly one industry of the stop's role"
        ),
        role_counts=role_counts,
    )


def census_phase_outcome(
    exchanges: Sequence[tuple[CensusRequest, CensusReadback | Exception]],
    *,
    prelaunch_digest: str,
    plan: BoxCensusPlan,
) -> dict:
    """Fail-closed census verification over preserved evidence only.

    Each exchange is ``(request, readback_or_error)``; an error element is an
    observation whose bytes never parsed or correlated (malformed, stale,
    torn or duplicate). The first halted exchange ends verification: earlier
    receipts are preserved, later exchanges are pending, and an unfinished
    schedule can never manufacture success. Exchange-level verdicts are
    recorded per observation kind:

    - ``MEASURED`` — a correlated READY readback whose domain-checked values
      (including the tile/cursor echoes and the page slices) were accepted;
    - ``REFUSED`` — a typed refusal (out-of-map tile, unpaused/pin/company
      drift, unsupported native fact) carrying no observation set;
    - ``MISSING`` — a scheduled exchange without a readback;
    - ``MALFORMED`` — the attached error element for that exchange.
    """
    receipts: list[dict] = []
    failed = None
    state = _census_state()
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
                _census_read_step(state, request, readback, plan=plan, seal=prelaunch_digest)
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
    boxes = _census_box_records(state, plan)
    return dict(
        schema="box-census-phase-outcome-v1",
        seal=prelaunch_digest,
        plan_digest=plan.digest,
        receipts=receipts,
        failed=failed,
        pending=pending,
        observations=state["observations"],
        radius=state.get("radius"),
        production=state.get("prod"),
        funds=state["funds"],
        boxes=boxes,
        branch8=_census_branch_verdict(boxes, complete=complete),
        observation_kinds=_OBSERVATION_KINDS,
        verification="CENSUS_COMPLETE" if complete else "CENSUS_INCOMPLETE",
    )
