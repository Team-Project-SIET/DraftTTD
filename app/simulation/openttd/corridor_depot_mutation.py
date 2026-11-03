"""Native depot-connectivity mutation wire contract (protocol 10, additive).

Milestone D5-F12-DEPOT: the F-12 finding (E58, §2) proved the D5 world's
depot 45487 can neither be entered nor be the anchor of a return-capable
route because its front tile 45743 carries E+W+S road bits and no N bit. E58
§2.1 prescribes the minimal world fix of record — demolish the depot, lay
the 2-tile road pair 45743 ↔ 45487 (the span API needs ``start != end``, and
building road pieces into a standing depot tile is refuted), then rebuild
the depot at 45487 facing its pinned front (the depot build auto-clears the
S bit the road pair laid on 45487, while 45743 keeps the N stub). This
module is the protocol-10 wire contract for that one-shot native mutation
(``docs/d5-f12-depot-mutation-protocol-2026-11-02.md``): typed requests,
fail-closed response parsing, one pinned six-exchange schedule and a
fail-closed phase verifier that distinguishes a verified mutation from a
missing, malformed, stale, divergent or halting one.

Unlike the strictly read-only census of protocol 9, this contract admits
exactly three mutating ops — ``demolish`` (``GSTile.DemolishTile``),
``road`` (``GSRoad.BuildRoad``) and ``depot`` (``GSRoad.BuildRoadDepot``) —
each pinned to the D4 depot tile 45487 and its front 45743, and exactly two
sparse observation ops: ``observe`` (the depot/edge fact set the v2
``ObserveDepot`` instrument reads) and ``fleet`` (the company's primary
vehicles through ``GSVehicleList``). The attempt-level ``max_cost`` ceiling
is 3000; funds are read back per exchange and every exchange must satisfy
``funds_after == funds_before - cost`` with ``cost`` signed (a demolish
refund class may credit, never zero). The before-state and after-state
observe exchanges are fixed-fact confirmation gates: the before gate must
reproduce the E58 diagnosis verbatim (depot present, front 45743, owner 0,
linked, and *both* ``AreRoadTilesConnected`` directions false) before any
command can run, halting STALE_PIN-preservingly on any divergence; the
after gate must show the identical identity facts with both directions
true. The fleet gate requires company 0's zero fleet (the D5 world's
retained fact); any vehicle halts with its per-vehicle ``in_depot`` rows
listed.

Protocol 10 stays additive over protocols 5/6/7/8/9 (the number allocation
of record): the GameScript bridge dispatches protocol-10 tables through a
separate guarded mutation handler shipped in its own package directory
(``d5_depot_mutation_package``), so the frozen census/freight sources the
E47/E64 stageings pinned never drift. Named constants (E33's lesson, the
survey-6/protocol-9 precedent): request and response bodies are canonical
UTF-8 JSON bounded by MAX_DEPOT_MUTATION_REQUEST_BYTES /
MAX_DEPOT_MUTATION_RESPONSE_BYTES (512 each — the largest fleet response
carries four rows, measured under 400 bytes). Tile bounds are 256x256-safe
(``TileID <= 65535``), imported from corridor_construction. The world is
the same pinned Seed-17 corridor world as protocol 9: the consumed A1
extension after-save.
"""

import hashlib
import json
from collections.abc import Sequence
from typing import Annotated, Literal

from pydantic import Field, StrictBool, StrictInt, model_validator

from app.planning.canonical import canonical_bytes
from app.planning.domain import Contract, Digest
from app.simulation.openttd.corridor_construction import (
    CompanyID,
    Money,
    SignedMoney,
    TileID,
)

DEPOT_MUTATION_PROTOCOL = 10
# Small bodies: the largest request carries its op pins (two tile echoes on
# the road/depot exchanges measured worst case under 260 bytes), the largest
# response one full depot fact set or four fleet rows (measured under 400
# bytes). 512 is the survey-6/protocol-9 precedent bound.
MAX_DEPOT_MUTATION_REQUEST_BYTES = 512
MAX_DEPOT_MUTATION_RESPONSE_BYTES = 512
# The attempt-level cost ceiling of record (E58 §2.1: demolish refund class
# plus two road pieces and one depot; the native arithmetic is never pinned
# — funds are chained per exchange instead). Every request echoes it and
# the handler accepts nothing else.
MAX_DEPOT_MUTATION_COST = 3000
# The bounded fleet readback: company 0's primary vehicles through
# GSVehicleList; the D5 world's retained fact is the zero fleet, and four
# rows is a generous diagnostic budget for a halt record.
MAX_DEPOT_MUTATION_FLEET_ROWS = 4
PLANNED_DEPOT_EXCHANGES = 6
DEPOT_MUTATION_REQUEST_BUDGET = 32
DEPOT_MUTATION_COMPANY = 0
DEPOT_MUTATION_CARGO_ID = 1
FUNDS_AT_F12_OPEN = 490257

# The pinned corridor world every protocol-10 request echoes (the consumed
# A1 extension after-save geometry; the pins reuse the protocol-5/6/9 D4
# lineage identity — the mutation never touches an unpinned tile).
DEPOT_MUTATION_PICKUP_TILE = 45748
DEPOT_MUTATION_PICKUP_FRONT_TILE = 45747
DEPOT_MUTATION_DELIVERY_TILE = 50351
DEPOT_MUTATION_DELIVERY_FRONT_TILE = 50095
DEPOT_MUTATION_DEPOT_TILE = 45487
DEPOT_MUTATION_DEPOT_FRONT_TILE = 45743

# The pinned GS constants the observe gate rides on (GSTile.GetOwner's
# invalid fact and GSRoad.GetRoadDepotFrontTile's invalid tile both arrive
# as the native -1 of record; the wire carries it and the gates refuse it).
DEPOT_MUTATION_INVALID_FACT = -1

DEPOT_MUTATION_OPS = ("observe", "demolish", "road", "depot", "fleet")
# Exactly the three E58 §2.1 mutations of record. Every other op (the two
# sparse observations) mutates nothing.
DEPOT_MUTATING_OPS = ("demolish", "road", "depot")

DepotOp = Literal["depot", "demolish", "fleet", "observe", "road"]
# Waiting on the bridge: protocol 10 keeps the frozen survey-6 status family
# (READY / UNSUPPORTED_NATIVE_FACT / INVALID_LOCATION / INVALID_COMPANY /
# PAUSED / STALE_PIN / OUT_OF_ORDER).
DepotStatus = Literal[
    "READY",
    "UNSUPPORTED_NATIVE_FACT",
    "INVALID_LOCATION",
    "INVALID_COMPANY",
    "PAUSED",
    "STALE_PIN",
    "OUT_OF_ORDER",
]
# Single identity of record: the depot mutation has one attempt, one
# prelaunch schema and one mutation-profile schema; a re-run attempt of the
# lineage needs its own design record of record first.
DEPOT_ATTEMPT_SCHEMA_VERSION = 1

_DEPOT_SEQUENCE: tuple[tuple[str, DepotOp, int | None, int | None], ...] = (
    # The fixed six-exchange schedule (E58 §2.1 order): the prescribed fix
    # passes through a demolish; the road pair must exist before the depot
    # can be rebuilt against its stub; the before/after observe gates
    # bracket the whole thing; the fleet gate closes the phase.
    ("before-00", "observe", None, None),
    ("demo-00", "demolish", DEPOT_MUTATION_DEPOT_TILE, None),
    ("road-00", "road", DEPOT_MUTATION_DEPOT_TILE, DEPOT_MUTATION_DEPOT_FRONT_TILE),
    ("depot-00", "depot", DEPOT_MUTATION_DEPOT_TILE, DEPOT_MUTATION_DEPOT_FRONT_TILE),
    ("after-00", "observe", None, None),
    ("fleet-00", "fleet", None, None),
)
DEPOT_MUTATION_EXCHANGE_IDS: tuple[str, ...] = tuple(
    row[0] for row in _DEPOT_SEQUENCE
)
_DEPOT_OP_BY_ID: dict[str, DepotOp] = {row[0]: row[1] for row in _DEPOT_SEQUENCE}
# The pinned per-op tile mapping: exchange -> (depot tile, front tile or
# None). demolish carries the depot tile only; road and depot carry both.
DEPOT_EXCHANGE_TILES: dict[str, tuple[int, int | None]] = {
    row[0]: (row[2] if row[2] is not None else DEPOT_MUTATION_DEPOT_TILE, row[3])
    for row in _DEPOT_SEQUENCE
    if row[1] in ("demolish", "road", "depot")
}
_DEPOT_SUCCESS_STATUS: dict[DepotOp, str] = {op: "READY" for op in DEPOT_MUTATION_OPS}
_DEPOT_REFUSAL_STATUS = frozenset(
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
    len(DEPOT_MUTATION_EXCHANGE_IDS) != PLANNED_DEPOT_EXCHANGES
    or len(set(DEPOT_MUTATION_EXCHANGE_IDS)) != PLANNED_DEPOT_EXCHANGES
    or set(_DEPOT_OP_BY_ID.values()) != set(DEPOT_MUTATION_OPS)
    or DEPOT_EXCHANGE_TILES
    != {
        "demo-00": (45487, None),
        "road-00": (45487, 45743),
        "depot-00": (45487, 45743),
    }
    or _DEPOT_OP_BY_ID
    != {
        "before-00": "observe",
        "demo-00": "demolish",
        "road-00": "road",
        "depot-00": "depot",
        "after-00": "observe",
        "fleet-00": "fleet",
    }
    or DEPOT_MUTATION_EXCHANGE_IDS
    != ("before-00", "demo-00", "road-00", "depot-00", "after-00", "fleet-00")
    or list(DEPOT_MUTATING_OPS) != ["demolish", "road", "depot"]
):
    raise RuntimeError(
        "depot mutation exchange schedule drifted from the pinned observations"
    )


class DepotMutationPlan(Contract):
    """The pinned identities and ordered exchanges of one mutation attempt.

    The plan binds the authoritative A1 after-save identity (the corridor
    pins funds and world exactly as protocols 5/6/9 do) plus the depot pin
    pair, the attempt ceiling and the six-exchange schedule. Staging and
    sealing remain the adopted ceremony's gates; this plan types what those
    stages must bind.
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
    max_cost: Money
    expected_funds: SignedMoney
    schedule: tuple[str, ...]
    request_budget: Annotated[StrictInt, Field(gt=0, le=DEPOT_MUTATION_REQUEST_BUDGET)] = (
        DEPOT_MUTATION_REQUEST_BUDGET
    )

    @property
    def digest(self) -> str:
        return hashlib.sha256(canonical_bytes(self)).hexdigest()

    @model_validator(mode="after")
    def coherent(self) -> DepotMutationPlan:
        if self.company != DEPOT_MUTATION_COMPANY or self.cargo != DEPOT_MUTATION_CARGO_ID:
            raise ValueError("the depot mutation drives company 0 with cargo 1")
        if (self.pickup, self.pickup_front) != (
            DEPOT_MUTATION_PICKUP_TILE,
            DEPOT_MUTATION_PICKUP_FRONT_TILE,
        ):
            raise ValueError("pickup pins drifted from the D4 corridor stops")
        if (self.delivery, self.delivery_front) != (
            DEPOT_MUTATION_DELIVERY_TILE,
            DEPOT_MUTATION_DELIVERY_FRONT_TILE,
        ):
            raise ValueError("delivery pins drifted from the D4 corridor stops")
        if (self.depot, self.depot_front) != (
            DEPOT_MUTATION_DEPOT_TILE,
            DEPOT_MUTATION_DEPOT_FRONT_TILE,
        ):
            raise ValueError("depot pins drifted from the D4 corridor depot")
        if self.max_cost != MAX_DEPOT_MUTATION_COST:
            raise ValueError(
                "the plan binds the E58 §2.1 attempt ceiling exactly (max_cost 3000)"
            )
        if self.expected_funds != FUNDS_AT_F12_OPEN:
            raise ValueError("the plan binds the A1 close-out funds exactly")
        if self.schedule != DEPOT_MUTATION_EXCHANGE_IDS:
            raise ValueError("schedule drifted from the planned six mutation exchanges")
        return self


def depot_mutation_plan() -> DepotMutationPlan:
    """The pinned D5-F12-DEPOT plan derived from the module's own pins."""
    return DepotMutationPlan(
        company=DEPOT_MUTATION_COMPANY,
        cargo=DEPOT_MUTATION_CARGO_ID,
        pickup=DEPOT_MUTATION_PICKUP_TILE,
        pickup_front=DEPOT_MUTATION_PICKUP_FRONT_TILE,
        delivery=DEPOT_MUTATION_DELIVERY_TILE,
        delivery_front=DEPOT_MUTATION_DELIVERY_FRONT_TILE,
        depot=DEPOT_MUTATION_DEPOT_TILE,
        depot_front=DEPOT_MUTATION_DEPOT_FRONT_TILE,
        max_cost=MAX_DEPOT_MUTATION_COST,
        expected_funds=FUNDS_AT_F12_OPEN,
        schedule=DEPOT_MUTATION_EXCHANGE_IDS,
    )


class DepotRequest(Contract):
    """One protocol-10 mutation exchange request (fixed correlation stride).

    Every request carries the corridor identity pins (defence in depth: the
    native handler refuses a drifted pin before any observation or command),
    the uniform ``plan`` seal digest and the attempt ``max_cost`` ceiling —
    exactly MAX_DEPOT_MUTATION_COST on every exchange. ``demolish`` names
    the pinned depot tile exactly; ``road`` and ``depot`` name the pinned
    depot tile and its front (a two-argument native call site whose span
    API needs ``start != end``); ``observe`` and ``fleet`` carry no tile.
    """

    protocol: Literal[10] = 10
    op: DepotOp
    request_id: Annotated[str, Field(pattern=r"^[a-z0-9-]{1,32}$")]
    plan: Digest
    company: CompanyID
    max_cost: Annotated[StrictInt, Field(ge=MAX_DEPOT_MUTATION_COST, le=MAX_DEPOT_MUTATION_COST)]
    pickup: TileID
    delivery: TileID
    depot: TileID
    tile: TileID | None = None
    front_tile: TileID | None = None

    @model_validator(mode="after")
    def coherent(self) -> DepotRequest:
        if self.op in ("demolish", "road", "depot"):
            if self.tile is None:
                raise ValueError("a mutating exchange names its pinned depot tile")
            if self.tile != self.depot:
                raise ValueError("mutating exchanges may only target the pinned depot tile")
            if self.front_tile is not None and self.tile == self.front_tile:
                raise ValueError("the native road span API needs start != end")
        else:
            if self.tile is not None:
                raise ValueError("only a mutating exchange carries a tile")
        if self.op in ("road", "depot"):
            if self.front_tile is None:
                raise ValueError("the road and depot exchanges name the pinned front")
            if self.front_tile != DEPOT_MUTATION_DEPOT_FRONT_TILE:
                raise ValueError("the road and depot exchanges name the pinned depot front")
        elif self.front_tile is not None:
            raise ValueError("only the road and depot ops carry a front tile")
        return self

    def to_bytes(self) -> bytes:
        raw = canonical_bytes(self)
        if len(raw) > MAX_DEPOT_MUTATION_REQUEST_BYTES:
            raise ValueError(
                f"depot mutation request exceeds {MAX_DEPOT_MUTATION_REQUEST_BYTES} bytes"
            )
        return raw


class DepotRow(Contract):
    """One reported primary-vehicle row of a fleet readback.

    ``id`` is the native vehicle id, ``tile`` its current location
    (``GSVehicle.GetLocation``) and ``in_depot`` the honest
    ``GSVehicle.IsInDepot`` read. Rows ascend by vehicle id with no
    duplicates; at most MAX_DEPOT_MUTATION_FLEET_ROWS ride one readback so
    a runaway fleet is halting evidence, never an unbounded dump. The D5
    world of record has the zero fleet: an empty list is the expected
    measurement, and the vacuous ``in_depot`` plan clause (every cycle ends
    in the depot) stands satisfied because no vehicle exists to report.
    """

    id: Annotated[StrictInt, Field(ge=0, le=65535)]
    tile: TileID
    in_depot: StrictBool


_DEPOT_FIELDS = (
    "depot_present",
    "front_read",
    "owner",
    "depot_linked",
    "connected_front_to_depot",
    "connected_depot_to_front",
)
_DEPOT_FLEET_DATA_FIELDS = frozenset({"count", "vehicles"})

# Strict per-op observation subsets (the protocol-9 precedent): the two
# sparse observations carry exactly their fact sets — observe the v2
# ObserveDepot facts, fleet the count and vehicle rows — and the three
# mutating ops carry no observation at all beyond their echoes, funds and
# signed cost (a refund class may credit; the chain is the proof).
_DEPOT_SUBSETS: dict[DepotOp, frozenset[str]] = {
    "observe": frozenset(_DEPOT_FIELDS),
    "demolish": frozenset(),
    "road": frozenset(),
    "depot": frozenset(),
    "fleet": frozenset(),
}


class DepotReadback(Contract):
    """One protocol-10 exchange response (strict per-op field subsets).

    The handler echoes the request correlation keys, ``funds`` and a status
    literal. Success frames carry the complete op subset — for ``observe``
    the v2 ObserveDepot fact set (``front_read`` and ``owner`` keep the
    native ``-1`` invalid fact on the wire; the before/after gates refuse
    any -1 identity), for ``fleet`` the count and its ascending rows, for
    the three mutations only their echoes and the signed cost. Refusal
    frames carry none of the observation set (a spoofed hybrid is refused
    on the wire). Every success value is domain-checked here: fleet rows
    must ascend by vehicle id without duplicates and satisfy the row
    budget; a value outside any domain can never parse, so the fail-closed
    surface cannot accidentally record it as measured or commanded.
    """

    protocol: Literal[10] = 10
    op: DepotOp
    request_id: str
    plan: Digest
    company: CompanyID
    max_cost: Money
    pickup: TileID
    delivery: TileID
    depot: TileID
    tile: TileID | None = None
    front_tile: TileID | None = None
    status: DepotStatus
    funds: SignedMoney
    cost: SignedMoney
    depot_present: StrictBool | None = None
    front_read: Annotated[StrictInt, Field(ge=-1, le=65535)] | None = None
    owner: Annotated[StrictInt, Field(ge=-1, le=255)] | None = None
    depot_linked: StrictBool | None = None
    connected_front_to_depot: StrictBool | None = None
    connected_depot_to_front: StrictBool | None = None
    count: Annotated[StrictInt, Field(ge=0, le=65535)] | None = None
    vehicles: tuple[DepotRow, ...] | None = None

    @property
    def digest(self) -> str:
        return hashlib.sha256(canonical_bytes(self)).hexdigest()

    @model_validator(mode="after")
    def coherent(self) -> DepotReadback:
        if self.op not in _DEPOT_SUCCESS_STATUS:
            raise ValueError("unknown depot mutation op")
        subset = _DEPOT_SUBSETS[self.op]
        present = {field for field in _DEPOT_FIELDS if getattr(self, field) is not None}
        fleet_data = {
            field for field in _DEPOT_FLEET_DATA_FIELDS if getattr(self, field) is not None
        }
        if fleet_data and self.op != "fleet":
            raise ValueError("fleet data fields ride the fleet op only")
        if self.op == "fleet":
            if present:
                raise ValueError(
                    f"{self.op} readback carries fields outside its subset: {sorted(present)}"
                )
            if self.status == _DEPOT_SUCCESS_STATUS[self.op]:
                missing = {
                    field
                    for field in _DEPOT_FLEET_DATA_FIELDS
                    if getattr(self, field) is None
                }
                if missing:
                    raise ValueError(f"{self.op} success readback lacks {sorted(missing)}")
                rows = self.vehicles or ()
                if len(rows) > MAX_DEPOT_MUTATION_FLEET_ROWS:
                    raise ValueError(
                        "a fleet readback carries more than its pinned row budget"
                    )
                ids = [row.id for row in rows]
                if any(later <= earlier for earlier, later in zip(ids, ids[1:], strict=False)):
                    raise ValueError("fleet rows must ascend by vehicle id")
                if rows and self.count is not None and self.count < len(rows):
                    raise ValueError("fleet count drifted below its own rows")
            elif fleet_data:
                raise ValueError("refusal readback carries an unclaimed observation set")
            return self
        if present and self.op != "observe":
            raise ValueError("depot facts ride the observe op only")
        if self.status not in _DEPOT_REFUSAL_STATUS:
            outside = present - subset
            if outside:
                raise ValueError(
                    f"{self.op} readback carries fields outside its subset: {sorted(outside)}"
                )
            missing = subset - present
            if missing:
                raise ValueError(f"{self.op} success readback lacks {sorted(missing)}")
            if self.op == "observe" and (self.front_read is None or self.owner is None):
                raise ValueError("observe success must carry its native front and owner reads")
        elif present:
            raise ValueError("refusal readback carries an unclaimed observation set")
        return self

    @classmethod
    def parse_for(cls, request: DepotRequest, raw: bytes):
        if len(raw) > MAX_DEPOT_MUTATION_RESPONSE_BYTES:
            raise ValueError(
                f"depot mutation response exceeds {MAX_DEPOT_MUTATION_RESPONSE_BYTES} bytes"
            )

        def unique(pairs):
            result = {}
            for key, value in pairs:
                if key in result:
                    raise ValueError("duplicate response key")
                result[key] = value
            return result

        value = json.loads(raw, object_pairs_hook=unique)
        # Python-mode strict validation rejects lists for the fleet
        # readback's only tuple field, while JSON mode accepts wire arrays:
        # lift the vehicles array to its tuple (element-wise StrictInt
        # bounds still apply).
        if isinstance(value, dict) and isinstance(value.get("vehicles"), list):
            value["vehicles"] = tuple(value["vehicles"])
        criteria = cls.model_validate(value)
        correlated = ("protocol", "op", "request_id", "plan", "company", "max_cost")
        if any(getattr(criteria, k) != getattr(request, k) for k in correlated):
            raise ValueError("depot mutation response correlation mismatch")
        for key in ("pickup", "delivery", "depot"):
            if getattr(criteria, key) != getattr(request, key):
                raise ValueError("depot mutation response pin mismatch")
        if request.tile is not None and criteria.tile != request.tile:
            raise ValueError("depot mutation response tile echo mismatch")
        if request.front_tile is not None and criteria.front_tile != request.front_tile:
            raise ValueError("depot mutation response front-tile echo mismatch")
        return criteria


def verify_request_against_depot_plan(
    request: DepotRequest, *, plan: DepotMutationPlan, seal: str
) -> None:
    """Refuse a request that is not bound to the local depot mutation plan.

    Python is the trust anchor: every request must present the staged seal,
    the pinned corridor identity, the pinned attempt ceiling and — for
    ``demolish`` — exactly the pinned depot tile, and — for ``road`` and
    ``depot`` — exactly the pinned depot tile and front pair of its
    scheduled exchange. This runs before any byte reaches the Admin
    session.
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
    if request.op in ("demolish", "road", "depot"):
        plan_ids = plan.schedule
        exchange_index = (
            plan_ids.index(request.request_id) if request.request_id in plan_ids else -1
        )
        expected_tile, expected_front = DEPOT_EXCHANGE_TILES[request.request_id]
        if (
            exchange_index < 1
            or request.tile != expected_tile
            or request.tile != plan.depot
            or request.front_tile != expected_front
        ):
            raise ValueError("mutating request drifted from the planned exchange specification")


# The before/after observe gates of record: the E58 §2.1 diagnosis verbatim
# (identity facts present, connectivity absent) and its prescribed
# resolution (the identical identity facts with connectivity present). Any
# divergence halts the phase STALE_PIN-preservingly before any later op.
_DEPOT_BEFORE_GATE = dict(
    depot_present=True,
    front_read=DEPOT_MUTATION_DEPOT_FRONT_TILE,
    owner=DEPOT_MUTATION_COMPANY,
    depot_linked=True,
    connected_front_to_depot=False,
    connected_depot_to_front=False,
)
_DEPOT_AFTER_GATE = dict(
    depot_present=True,
    front_read=DEPOT_MUTATION_DEPOT_FRONT_TILE,
    owner=DEPOT_MUTATION_COMPANY,
    depot_linked=True,
    connected_front_to_depot=True,
    connected_depot_to_front=True,
)
# Public aliases the native pipeline binds by name (the E58 §2.1 gates are
# part of the contract's surface of record, not private detail).
DEPOT_BEFORE_GATE: dict = _DEPOT_BEFORE_GATE
DEPOT_AFTER_GATE: dict = _DEPOT_AFTER_GATE


def _depot_gate_defects(facts: dict, expected: dict) -> list[str]:
    """Every observed observe-fact divergence from a fixed-fact gate."""
    return [
        f"{name}: measured {facts.get(name)!r}, prescribed {wanted!r}"
        for name, wanted in expected.items()
        if facts.get(name) != wanted
    ]


def _depot_state() -> dict:
    return dict(
        index=0,
        observations={},
        fleet=None,
        mutations=[],
        ledger=[],
        funds=None,
        funds_chain=[],
    )


def _depot_read_step(
    state: dict,
    request: DepotRequest,
    readback: DepotReadback,
    *,
    plan: DepotMutationPlan,
    seal: str,
) -> dict:
    """Verify one ordered protocol-10 exchange against the accumulated state."""
    plan_ids = plan.schedule
    expected = plan_ids[state["index"]]
    if request.request_id != expected or readback.request_id != expected:
        raise ValueError(f"depot mutation exchange out of order: expected {expected}")
    verify_request_against_depot_plan(request, plan=plan, seal=seal)
    if readback.status != "READY":
        raise ValueError(f"depot mutation exchange {expected} ended {readback.status}")
    # The funds chain of record: the first exchange opens at the pinned A1
    # close-out level and every later exchange must satisfy
    # funds_after == funds_before - cost, with cost signed (a demolish
    # refund class may credit — the chain is the arithmetic proof, the only
    # native-fact-faithful funds story on this contract).
    funds_before = plan.expected_funds if state["funds"] is None else state["funds"]
    if readback.funds != funds_before - readback.cost:
        raise ValueError(
            f"the depot funds chain broke at {expected}: "
            f"{readback.funds} != {funds_before} - {readback.cost}"
        )
    if request.op == "observe":
        facts = dict(
            depot_present=readback.depot_present,
            front_read=readback.front_read,
            owner=readback.owner,
            depot_linked=readback.depot_linked,
            connected_front_to_depot=readback.connected_front_to_depot,
            connected_depot_to_front=readback.connected_depot_to_front,
        )
        gate = _DEPOT_BEFORE_GATE if expected == "before-00" else _DEPOT_AFTER_GATE
        defects = _depot_gate_defects(facts, gate)
        if defects:
            # The fixed-fact gates of record (E58 §2.1): the before gate
            # must reproduce the diagnosis verbatim before any command can
            # run, the after gate must prove the fix. Any divergence halts
            # STALE_PIN-preservingly with the raw measured values legible.
            raise ValueError(
                f"STALE_PIN: the {expected} observe gate diverged from the "
                f"E58 prescription — " + "; ".join(defects)
            )
        state["observations"][expected] = dict(
            facts=facts,
            request_id=readback.request_id,
            digest=readback.digest,
            funds=readback.funds,
        )
    elif request.op == "fleet":
        rows = readback.vehicles or ()
        if readback.count != 0:
            # The zero-fleet gate of record: the D5 world's retained fact.
            # Any vehicle halts with its per-vehicle in_depot rows listed —
            # the vacuous in_depot satisfaction (no vehicle exists to
            # report one) fails loudly instead of being presumed.
            raise ValueError(
                f"STALE_PIN: the fleet gate demands the retained zero fleet, "
                f"measured {readback.count}: "
                + "; ".join(
                    f"id {row.id} tile {row.tile} in_depot {row.in_depot}" for row in rows
                )
            )
        state["fleet"] = dict(
            count=readback.count,
            vehicles=[],
            request_id=readback.request_id,
            digest=readback.digest,
        )
    else:
        if readback.cost > MAX_DEPOT_MUTATION_COST:
            raise ValueError("a mutating exchange exceeded the pinned attempt ceiling")
        state["mutations"].append(
            dict(
                exchange=readback.request_id,
                op=request.op,
                cost=readback.cost,
                funds=readback.funds,
                digest=readback.digest,
            )
        )
    state["ledger"].append(
        dict(
            exchange=request.request_id,
            op=request.op,
            status=readback.status,
            funds=readback.funds,
            cost=readback.cost,
        )
    )
    state["funds"] = readback.funds
    state["funds_chain"].append(
        dict(
            exchange=request.request_id,
            funds_before=funds_before,
            cost=readback.cost,
            funds_after=readback.funds,
        )
    )
    state["index"] += 1
    receipt = dict(
        schema="company-depot-mutation-receipt-v1",
        request_id=readback.request_id,
        op=request.op,
        plan_digest=plan.digest,
        seal=seal,
        status=readback.status,
        funds=readback.funds,
        cost=readback.cost,
        verification="DEPOT_MUTATION_OBSERVED",
    )
    if request.op == "observe":
        receipt = {**receipt, "facts": dict(state["observations"][expected]["facts"])}
    elif request.op == "fleet":
        receipt = {**receipt, "count": readback.count, "vehicles": []}
    else:
        receipt = {
            **receipt,
            "tile": request.tile,
            "front_tile": request.front_tile,
            "state_changed": True,
        }
    return receipt


def depot_gate_verdict(state: dict, *, complete: bool) -> dict:
    """The offline E58 §2.1 resolution recompute from protocol-10 rows alone.

    The gate passes only on a complete schedule whose both observe gates
    recorded exactly their prescribed fact sets, whose three prescribed
    mutations all carried READY readbacks inside the pinned ceiling and
    whose fleet gate confirmed the retained zero fleet (the vacuous
    ``in_depot`` satisfaction). An incomplete schedule can never
    manufacture a verdict; nothing here is an admissibility claim.
    """
    mutated = tuple(row["op"] for row in state["mutations"])
    if not complete or mutated != DEPOT_MUTATING_OPS:
        return dict(
            verdict="DEPOT_MUTATION_GATE_UNDECIDED_INCOMPLETE",
            statement=(
                "the three prescribed E58 §2.1 mutations did not all complete "
                "in verified order; the connectivity fix stands unevidenced"
                if complete
                else "an unevidenced mutation sequence can decide nothing; "
                "this is a recorded fact, never a manufactured verdict"
            ),
            mutations=list(mutated),
        )
    return dict(
        verdict="DEPOT_MUTATION_GATE_PASSES",
        statement=(
            "the before gate reproduced the E58 diagnosis verbatim, the "
            "prescribed demolish-road-depot sequence carried READY "
            "readbacks within the pinned ceiling, the after gate proves "
            "both AreRoadTilesConnected directions true with the identical "
            "identity facts and the fleet gate confirms the retained zero "
            "fleet, so the vacuous in_depot clause stands satisfied"
        ),
        mutations=list(mutated),
    )


def depot_phase_outcome(
    exchanges: Sequence[tuple[DepotRequest, DepotReadback | Exception]],
    *,
    prelaunch_digest: str,
    plan: DepotMutationPlan,
) -> dict:
    """Fail-closed depot mutation verification over preserved evidence only.

    Each exchange is ``(request, readback_or_error)``; an error element is
    an observation whose bytes never parsed or correlated (malformed,
    stale, torn or duplicate). The first halted exchange ends verification:
    earlier receipts are preserved, later exchanges are pending, and an
    unfinished schedule can never manufacture success. Exchange-level
    verdicts are recorded per observation kind:

    - ``MEASURED`` — a correlated READY readback whose domain-checked
      values (including the tile echoes, the fixed-fact gates and the
      funds chain) were accepted;
    - ``REFUSED`` — a typed refusal (unpaused/pin/company drift,
      unsupported native fact) carrying no observation set;
    - ``MISSING`` — a scheduled exchange without a readback;
    - ``MALFORMED`` — the attached error element for that exchange.
    """
    receipts: list[dict] = []
    failed = None
    state = _depot_state()
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
                _depot_read_step(state, request, readback, plan=plan, seal=prelaunch_digest)
            )
        except Exception as error:  # noqa: BLE001 - fail closed on any defect
            failed = dict(
                label=request.request_id,
                status=str(getattr(readback, "status", "UNKNOWN")),
                error=str(error),
                world_state=(
                    "HALTED_MID_MUTATION"
                    if request.op in DEPOT_MUTATING_OPS
                    else "HALTED_BEFORE_MUTATION"
                ),
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
    return dict(
        schema="depot-mutation-phase-outcome-v1",
        seal=prelaunch_digest,
        plan_digest=plan.digest,
        receipts=receipts,
        failed=failed,
        pending=pending,
        observations=state["observations"],
        fleet=state["fleet"],
        mutations=state["mutations"],
        funds=state["funds"],
        funds_chain=state["funds_chain"],
        state_changed=any(row["op"] in DEPOT_MUTATING_OPS for row in state["mutations"]),
        gates=dict(
            before=state["observations"].get("before-00"),
            after=state["observations"].get("after-00"),
        ),
        gate=depot_gate_verdict(state, complete=complete),
        observation_kinds=("MEASURED", "REFUSED", "MISSING", "MALFORMED"),
        verification="DEPOT_MUTATION_COMPLETE" if complete else "DEPOT_MUTATION_INCOMPLETE",
    )