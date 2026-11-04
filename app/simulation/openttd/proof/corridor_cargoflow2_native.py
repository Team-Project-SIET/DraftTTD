"""D5-CARGOFLOW-2 native staging pipeline (offline preparation only).

The D5-CARGOFLOW-1 lineage halted terminal at ``sample-07`` with
``PHASE_HALTED_PREFIX_PRESERVED`` — a funds fence aimed at a static
close-out level while the world legitimately pays monthly charges, and a
funds echo sampled at a different instant than the observations it shares
a response with (``docs/d5-cargoflow-delivery-design-2026-11-04.md`` §2).
That verdict stays terminal and unlabeled-unchanged; this module binds the
fresh identity ``D5-CARGOFLOW-2`` to the real road-vehicle delivery
attempt under the additive wire protocol 11 (``cargoflow-delivery``) and
fixes both defects by design: the funds fence becomes the modeled
trajectory of record (§4, zero residual, never a tolerance), and every
response carries one observation instant (§4.5). Fresh attempt, staged
package, wire module and native pipeline are all new-round instruments;
no frozen byte of the protocols 8/9/10 instruments drifts (§5.1).

The pipeline is a fifth narrow pipeline bound explicitly to
``Cargoflow2Plan`` and its single pinned 25-exchange schedule, reusing
the proven shared ceremony by import rather than copy (the E99
cargoflow pipeline's shape: staging → preflight → claim → one encrypted
session → replay). Its prerequisite of record is the depot-chain binding
the freight v2 pipeline already derives and verifies (``D5-F12-DEPOT-3``
after-save, ``183b2027…6a6``, world-pin version 3, plus the verified
reload chain) — imported through
``corridor_freight_v2_native.prerequisite_binding`` and never re-derived
here. The staging/claim machinery in ``corridor_freight_native`` stays
plan-bound to its own contract families, so a ``FreightPlan``,
``FreightPlanV2``, ``AcceptSurveyPlan``, ``BoxCensusPlan`` or
``CargoFlowPlan`` can never be staged, sealed, executed or replayed as a
cargo-flow delivery attempt, and the attempt's own session surface
refuses every foreign request (protocol 11 required).

The fixed schedule of record (§5.3) runs the freight-family instrument
chain with the vehicle first — ``site-00`` … ``vread-01``, the engine pin
admitted fail-closed at its census, one quote-first purchase inside the
pinned ceiling, the two pinned orders read back independently, the start
— then the bounded 5-day ``arrive-00`` first-arrival watch that latches
the ladder anchor, then the twelve-sample flow ladder at exactly its
pinned economy-day offsets, then the two read-only tail exchanges in the
``flow-11`` economy day. The 60-economy-day attempt authority is
enforced twice by design: the package refuses any ladder step whose
target day escapes the authority, and this pipeline checks the elapsed
economy-day ledger before sending each request — either check failing
halts fail-closed with no further bytes on the wire (the typed
``AUTHORITY_EXCEEDED`` refusal surface of record).

The funds fence itself is applied by the production
``app.simulation.openttd.corridor_cargoflow2.cargoflow2_phase_outcome``
at every verified exchange (the zero-residual trajectory of record: the
exact purchase debit, the monthly staircase + station fee, the 8.8
fixed-point day running costs with exact carry, and the engine-read
income attributed at the same instants); the model is never loosened to
pass. Nothing here launches OpenTTD, connects to a port, writes a claim
or mutates any world or retained artifact; staging, review, Gate C
signing and launch each remain their own explicit operator approvals.
"""

import argparse
import asyncio
import hashlib
import json
import os
import re
import shutil
import struct
import time
import zipfile
from dataclasses import asdict
from pathlib import Path
from typing import Any

from app.simulation.openttd.admin_crypto import AuthorizedKey
from app.simulation.openttd.admin_protocol import AdminFrameDecoder, encode_admin_quit
from app.simulation.openttd.corridor_cargoflow2 import (
    CARGOFLOW2_ARRIVE_MAX_DAYS,
    CARGOFLOW2_ENGINE,
    CARGOFLOW2_ENGINE_MAX_COST,
    CARGOFLOW2_EXCHANGE_IDS,
    CARGOFLOW2_FLOW_OFFSETS,
    CARGOFLOW2_NAME,
    CARGOFLOW2_OPS,
    CARGOFLOW2_ORDER_DELIVERY_FLAGS,
    CARGOFLOW2_ORDER_PICKUP_FLAGS,
    CARGOFLOW2_PICKUP_TILE,
    CARGOFLOW2_PROTOCOL,
    CARGOFLOW2_PURCHASE_QUOTE,
    CARGOFLOW2_READ_ONLY_SCHEMA,
    CARGOFLOW2_REQUEST_BUDGET,
    CARGOFLOW2_SPAN_DAYS,
    CARGOFLOW2_TAIL_OFFSET,
    CARGOFLOW2_WAIT_DAY_CAP,
    CARGOFLOW2_WAIT_MAX_TICKS,
    MAX_CARGOFLOW2_REQUEST_BYTES,
    MAX_CARGOFLOW2_RESPONSE_BYTES,
    PLANNED_CARGOFLOW2_EXCHANGES,
    Cargoflow2FundsModel,
    Cargoflow2Plan,
    Cargoflow2Readback,
    Cargoflow2Request,
    cargoflow2_phase_outcome,
    cargoflow2_plan,
    verify_request_against_cargoflow2_plan,
)
from app.simulation.openttd.gamescript_transport import (
    ADMIN_GAMESCRIPT,
    SERVER_GAMESCRIPT,
    GameScriptTransport,
    decode_gamescript,
    encode_gamescript,
    gamescript_subscription,
)
from app.simulation.openttd.proof import corridor_freight_native as freight_native
from app.simulation.openttd.proof import corridor_freight_v2_native as freight_v2_native
from app.simulation.openttd.proof.classification_capture import script_log_health_findings
from app.simulation.openttd.proof.corridor_construction_native import (
    source_save_path,
    stage_world,
)
from app.simulation.openttd.proof.endpoints import (
    kernel_socket_rows,
    verify_cleanup_endpoints,
)
from app.simulation.openttd.proof.graphics import stage_opengfx
from app.simulation.openttd.proof.harness import (
    BINARY,
    BINARY_SHA256,
    PROJECT,
    EndpointReservation,
    PreparedProof,
    manifest,
    sha256,
    source_freeze,
    verify_freeze,
    write_json,
)
from app.simulation.openttd.proof.native import matching_processes
from app.simulation.openttd.proof.operator_authorization import (
    CLAIM_AUTHORIZATION_EVIDENCE_SCHEMA,
    authorization_payload,
    canonical_authorization_bytes,
    grant_launch,
)
from app.simulation.openttd.proof.road_mutation import console, save, wait_log
from app.simulation.openttd.proof.terrain_classification_preparation import SEED17_RUN
from app.simulation.openttd.proof.terrain_clearing import (
    STAGED_AI_DIRECTORY,
    ClearingNativeBackend,
    replay_authorization_state,
)
from app.simulation.openttd.proof.terrain_terraform_native import (
    ROAD_PROOF_COMPANY_READY_MARKER,
    WELCOME_ORDER,
    plan_digest_of,
    read_prelaunch,
)
from app.simulation.openttd.proof.world_correspondence import (
    SOURCE_SAVE_GS_NAME,
    verify_staged_source_save,
)
from app.simulation.openttd.secure_admin import AuthState, SecureAdminSession

PACKAGES = Path(__file__).resolve().parents[1]
CARGOFLOW2_PACKAGE = PACKAGES / "d5_cargoflow2_package"
AI_PACKAGE = PACKAGES / "road_company_package"
CARGOFLOW2_CLOSURE_ROOT = "app.simulation.openttd.proof.corridor_cargoflow2_native"

KIND = "cargoflow2"
MILESTONE_CARGOFLOW2 = "D5-CARGOFLOW"
# Fresh attempt identity of record (design record §5.1): the consumed
# D5-CARGOFLOW-1 stays exactly as recorded and nothing here re-opens it.
D5_CARGOFLOW2_ATTEMPT = "D5-CARGOFLOW-2"
D5_CARGOFLOW2_PRELAUNCH_SCHEMA = "d5-cargoflow2-prelaunch-v1"
# The attempt keeps the shared native consumed-launch marker family; its
# prerequisite lineage schema is the freight v2 depot-chain binding schema
# the shared ceremony already pins (the attempt re-derives the depot
# prerequisite bytes but never writes them, design record §5.1).
D5_CARGOFLOW2_LAUNCH_CONSUMED_SCHEMA = freight_native.D5_FREIGHT_LAUNCH_CONSUMED_SCHEMA
D5_CARGOFLOW2_PREREQUISITE_SCHEMA = freight_v2_native.D5_FREIGHT_V2_PREREQUISITE_SCHEMA

# Candidate directory of record (fresh round, candidate-1; the naming
# pattern of record of the corridor native families with the new identity).
CARGOFLOW2_CANDIDATE_DIRECTORY = "d5-corridor-cargoflow2-native-candidate-1"

# Prerequisite lineage of record: the pinned, consumed, replay-verified
# depot-mutation attempt (D5-F12-DEPOT-3 after-save, world-pin version 3),
# imported from the freight v2 binding's own pins — the attempt world is
# the freight world of record, and one pin source of record stays one pin.
PINNED_PREREQUISITE = freight_v2_native.DEPOT_PREREQUISITE
PINNED_PREREQUISITE_AFTER_SAVE = freight_v2_native.DEPOT_PREREQUISITE_AFTER_SAVE
RELOAD_PREREQUISITE = freight_v2_native.RELOAD_PREREQUISITE
if PINNED_PREREQUISITE_AFTER_SAVE != (
    "183b20273a54ebe1a2cd9306145a9ea820bbd6114b1608c42079b4e1b1efe6a6"
):
    raise RuntimeError("the cargo-flow delivery depot world pin drifted")

# The attempt GameScript readiness marker is its own (the staged protocol-11
# handler logs "D5_CARGOFLOW2_READY" at Start); the road-company readiness
# marker follows the staged AI bootstrap exactly as the E99 probe does.
CARGOFLOW2_READY_MARKER = "D5_CARGOFLOW2_READY"

CARGOFLOW2_EXCHANGE_MARGIN_SECONDS = freight_native.FREIGHT_EXCHANGE_MARGIN_SECONDS


class Cargoflow2StagingError(freight_v2_native.FreightV2StagingError):
    """Offline cargo-flow delivery staging or pin derivation failed; nothing launched."""


# --- Migration-safety: the pipeline is cargoflow2-plan typed ---------------


def _require_cargoflow2_plan(plan) -> Cargoflow2Plan:
    """Refuse anything that is not the pinned ``Cargoflow2Plan``.

    The other pipeline plans share several field names with a
    ``Cargoflow2Plan``; every attempt entry point guards here so a freight,
    survey, census or dispatch-probe plan can never be staged, sealed,
    executed or replayed as a delivery attempt, and so the single attempt
    plan can never drift from its pinned derivation.
    """
    if not isinstance(plan, Cargoflow2Plan):
        raise Cargoflow2StagingError(
            "the cargo-flow delivery attempt accepts a Cargoflow2Plan only"
        )
    if plan.schema_version != 1:
        raise Cargoflow2StagingError("the attempt plan carries an unknown schema version")
    if plan.digest != cargoflow2_plan().digest:
        raise Cargoflow2StagingError("the attempt plan drifted from the pinned observations")
    return plan


def cargoflow2_pipeline_plan() -> Cargoflow2Plan:
    """The single pinned plan of record re-derived from the module pins."""
    return _require_cargoflow2_plan(cargoflow2_plan())


# --- The pinned attempt schedule ---------------------------------------------


def cargoflow2_schedule() -> list[dict]:
    """The fixed 25 exchange lines as staged plan rows (design record §5.3).

    Order and echoes refuse drift: the fixed freight-family instrument
    chain runs first (``site-00`` … ``arrive-00``), then the twelve flow
    rows at their exact pinned ladder offsets 0..55, then the two tail
    rows in the ``flow-11`` economy day. Every row carries its own planned
    echoes — the order rows pin their stop indexes with the pinned flags
    to come, ``arrive-00`` pins its bounded 5-day watch, and every
    flow/tail row pins its economy-day offset; every pre-vehicle row
    stays at -1. The op ladder is this pipeline's own derivation of
    record; the wire contract's trust anchor re-checks it position by
    position when the staged request table derives (``corridor_cargoflow2``
    is the trust anchor — the op derivation never leaves this module
    unverified, and a drifted op is a staging error, never a run-time
    rejection that is benignly retried).
    """
    planned_ops = {
        "site-00": "site",
        "engine-00": "engine",
        "purchase-00": "purchase",
        "vread-00": "vread",
        "order-00": "order",
        "order-01": "order",
        "order-read-00": "order-read",
        "monitor-00": "monitor",
        "start-00": "start",
        "vread-01": "vread",
        "arrive-00": "arrive-watch",
    }
    schedule: list[dict] = []
    for exchange in CARGOFLOW2_EXCHANGE_IDS:
        op = planned_ops.get(exchange, exchange.rsplit("-", 1)[0])
        row = dict(exchange=exchange, op=op, offset=-1)
        if op == "flow":
            row["offset"] = int(CARGOFLOW2_FLOW_OFFSETS[int(exchange.rsplit("-", 1)[1])])
        elif op in ("finance", "finish"):
            row["offset"] = int(CARGOFLOW2_TAIL_OFFSET)
        elif op == "order":
            row["order_index"] = 0 if exchange == "order-00" else 1
        elif op == "arrive-watch":
            row["watch_days"] = int(CARGOFLOW2_ARRIVE_MAX_DAYS)
        schedule.append(row)
    flow_rows = [row for row in schedule if row["op"] == "flow"]
    tail_rows = [row for row in schedule if row["op"] in ("finance", "finish")]
    order_rows = [row for row in schedule if row["op"] == "order"]
    if (
        [row["exchange"] for row in schedule] != list(CARGOFLOW2_EXCHANGE_IDS)
        or len(schedule) != PLANNED_CARGOFLOW2_EXCHANGES
        or schedule[0]["op"] != "site"
        or schedule[0]["offset"] != -1
        or schedule[10]["exchange"] != "arrive-00"
        or schedule[11]["exchange"] != "flow-00"
        or [row["offset"] for row in flow_rows] != list(CARGOFLOW2_FLOW_OFFSETS)
        or flow_rows[0]["offset"] != 0
        or flow_rows[-1]["offset"] != CARGOFLOW2_SPAN_DAYS
        or [row["offset"] for row in tail_rows] != [
            CARGOFLOW2_TAIL_OFFSET,
            CARGOFLOW2_TAIL_OFFSET,
        ]
        or [row["order_index"] for row in order_rows] != [0, 1]
        or [row["watch_days"] for row in schedule if row["op"] == "arrive-watch"] != [
            CARGOFLOW2_ARRIVE_MAX_DAYS
        ]
        or CARGOFLOW2_ARRIVE_MAX_DAYS + CARGOFLOW2_SPAN_DAYS != int(
            cargoflow2_pipeline_plan().day_budget
        )
    ):
        raise Cargoflow2StagingError("the staged attempt schedule drifted from the wire contract")
    if any(row["op"] not in CARGOFLOW2_OPS for row in schedule):
        raise Cargoflow2StagingError("a staged schedule row carries a foreign op")
    return schedule


def staged_cargoflow2_schedule(policy: dict) -> list[dict]:
    """The staged schedule one plan-policy record binds its digest to.

    The attempt has one schedule version and one derivation: a staged
    record naming a foreign version pairing is refused here before any
    schedule can be trusted.
    """
    if policy.get("schedule_version", 0) != 1:
        raise ValueError(
            f"plan record names an unknown cargo-flow delivery schedule "
            f"version: {policy.get('schedule_version', 0)}"
        )
    return cargoflow2_schedule()


# --- Hypotheses (retained E99 control), never facts ---------------------------


def cargoflow2_hypotheses() -> dict:
    """The retained E99 probe receipt re-bound as the pre-arrival control (§5.2).

    The consumed ``D5-CARGOFLOW-1`` receipt (candidate-1) is the
    no-vehicle control of record on this same consumed depot-chain world:
    its verified seven-sample prefix latched the launch-day anchor and
    measured ``stock_pickup`` -1 (the pinned non-acceptance echo — the
    pickup industry accepts nothing), ``stock_bay`` 0 (the bay industry
    does accept) and every waiting family 0 across ``sample-00`` …
    ``sample-06`` — the first seven ladder steps of this round's own
    offsets. Without a vehicle the pickup station never received cargo.
    The attempt re-binds those identity rows as hypotheses only, never as
    expected values: the ladder measures its own time series, never bound
    values. Absent retained evidence (a fresh clone) is recorded as
    ``RETAINED_PROBE_ABSENT`` — no hypothesis is invented.
    """
    receipt_path = (
        PROJECT
        / "artifacts/experiments/d5-corridor-cargoflow-native-candidate-1/result.json"
    )
    if not receipt_path.is_file():
        return dict(
            state="RETAINED_PROBE_ABSENT",
            samples=[],
            statement=(
                "the retained E99 probe receipt of record is absent from this "
                "checkout; no hypothesis is invented and the attempt proceeds "
                "without one"
            ),
        )
    receipt = json.loads(receipt_path.read_text())
    phase = receipt.get("phase")
    if not isinstance(phase, dict):
        raise Cargoflow2StagingError("the retained E99 receipt lacks its phase record")
    samples = phase.get("samples")
    if not isinstance(samples, dict) or not samples:
        raise Cargoflow2StagingError("the retained E99 receipt lacks its sampled ladder")
    plan = cargoflow2_pipeline_plan()
    retained_anchor = phase.get("anchor")
    if retained_anchor is None or int(retained_anchor) != int(plan.launch_day):
        raise Cargoflow2StagingError(
            "the retained E99 anchor drifted from the pinned launch day of record"
        )
    offsets = sorted(int(key) for key in samples)
    if offsets != list(CARGOFLOW2_FLOW_OFFSETS[: len(offsets)]) or len(offsets) != 7:
        raise Cargoflow2StagingError(
            "the retained E99 sampled prefix drifted from the pinned "
            "seven-sample before-arrival ladder"
        )
    rows = []
    for key in sorted(samples, key=int):
        sample = samples[key]
        measured = dict(
            offset=int(key),
            stock_pickup=int(sample["stock_pickup"]),
            stock_bay=int(sample["stock_bay"]),
            wait_pickup=int(sample["wait_pickup"]),
            wait_bay=int(sample["wait_bay"]),
        )
        if measured["stock_pickup"] != -1:
            raise Cargoflow2StagingError(
                "the retained no-vehicle control drifted: a sample contradicted "
                f"its pinned non-acceptance echo at offset {measured['offset']}"
            )
        if measured["stock_bay"] != 0 or measured["wait_pickup"] != 0 or measured["wait_bay"] != 0:
            raise Cargoflow2StagingError(
                "the retained no-vehicle control drifted: a sample measured a "
                f"queue or accepted pile the pre-arrival control forbids at "
                f"offset {measured['offset']}"
            )
        rows.append(dict(measured, kind="HYPOTHESIS"))
    return dict(
        state="RETAINED_PROBE_REBOUND",
        samples=rows,
        source="artifacts/experiments/d5-corridor-cargoflow-native-candidate-1/result.json",
        source_sha256=hashlib.sha256(receipt_path.read_bytes()).hexdigest(),
        statement=(
            "the pre-arrival control of record is the retained E99 "
            "seven-sample prefix re-bound as hypotheses only; the delivery "
            "ladder measures its own time series, never bound values, and "
            "the decisive queue observation stays wait_pickup > 0 at any "
            "post-arrival flow sample (§5.2 item 3)"
        ),
        derivation="corridor_cargoflow2_native.cargoflow2_hypotheses",
    )


# --- The attempt plan policy, budgets and readback story ---------------------


def _cargoflow2_expected_world(plan: Cargoflow2Plan) -> dict:
    """The expected world-pin set of the staged attempt candidate."""
    return dict(
        pickup=int(plan.pickup),
        pickup_front=int(plan.pickup_front),
        delivery=int(plan.delivery),
        delivery_front=int(plan.delivery_front),
        depot=int(plan.depot),
        depot_front=int(plan.depot_front),
        company=plan.company,
        cargo=plan.cargo,
        engine=int(plan.engine),
        pickup_sid=int(plan.pickup_sid),
        bay_sid=int(plan.bay_sid),
        pickup_industry=int(plan.pickup_industry),
        bay_industry=int(plan.bay_industry),
        start_funds=int(plan.start_funds),
        purchase_quote=int(plan.purchase_quote),
        founding_loan=int(plan.founding_loan),
        interest_rate=int(plan.interest_rate),
        station_fee=int(plan.station_fee),
        launch_day=int(plan.launch_day),
        arrive_max_days=int(plan.arrive_max_days),
        flow_span_days=int(plan.flow_span_days),
        day_budget=int(plan.day_budget),
        request_budget=plan.request_budget,
        flow_offsets=[int(offset) for offset in CARGOFLOW2_FLOW_OFFSETS],
        statement=(
            "the staged attempt world is the consumed depot-mutation attempt "
            "after-save (world-pin version 3): the corridor pickup stop, the "
            "A1 bay stop and the company depot with their pinned fronts, the "
            "pinned station and industry identities, the pinned provisional "
            "engine and its financial-model pins at the close-out funds and "
            "launch-day pins (§4.1); the attempt queries nothing else"
        ),
    )


def _cargoflow2_ladder_grid() -> dict:
    """The pinned ladder geometry of record as a policy grid (§5.3)."""
    return dict(
        schema="d5-cargoflow2-ladder-grid-v1",
        planned_exchanges=PLANNED_CARGOFLOW2_EXCHANGES,
        fixed_exchanges=len(CARGOFLOW2_EXCHANGE_IDS) - len(CARGOFLOW2_FLOW_OFFSETS) - 2,
        flow_samples=len(CARGOFLOW2_FLOW_OFFSETS),
        tail_exchanges=2,
        cadence_days=5,
        arrival_bound_days=int(CARGOFLOW2_ARRIVE_MAX_DAYS),
        span_days=int(CARGOFLOW2_SPAN_DAYS),
        tail_offset=int(CARGOFLOW2_TAIL_OFFSET),
        day_budget=int(cargoflow2_pipeline_plan().day_budget),
        offsets=[int(offset) for offset in CARGOFLOW2_FLOW_OFFSETS],
        wait_ticks=int(CARGOFLOW2_WAIT_MAX_TICKS),
        wait_day_cap=int(CARGOFLOW2_WAIT_DAY_CAP),
        statement=(
            "the equality-gated ladder: the arrival watch latches the anchor "
            "once and is bounded at 5 economy days (a timeout is a terminal "
            "ARRIVE_TIMEOUT, never a retry), every flow sample sleeps "
            "in-package until the anchor + its exact pinned offset, and the "
            "two tail exchanges ride the flow-11 economy day with no "
            "in-package wait; overshoot, pause or clock regression fail "
            "closed. Arrival-bound plus flow span exactly equals the "
            "60-economy-day attempt authority, and that authority is "
            "enforced twice: package-side against every ladder step's "
            "target day and pipeline-side against the elapsed day ledger "
            "before every send"
        ),
    )


def cargoflow2_funds_model_gate() -> dict:
    """The pinned financial-model construction of record (§4.1).

    The attempt's modeled trajectory is the production
    ``Cargoflow2FundsModel`` fence of record; this offline gate builds it
    once from the plan's own pins and pins its untouched founding state:
    the model starts at the close-out funds with its quote, a zero
    fraction, no admitted running-cost raw and no purchase debit. Every
    staged record must re-derive this exact table (footprint of the
    zero-residual fence of record).
    """
    plan = cargoflow2_pipeline_plan()
    model = Cargoflow2FundsModel(
        start_funds=int(plan.start_funds), purchase_quote=int(plan.purchase_quote)
    )
    if (
        model.funds != int(plan.start_funds)
        or model.fraction != 0
        or model.running_cost is not None
        or model.baseline_income is not None
        or model.purchase_paid
        or model.started is not None
        or model.income_deltas
    ):
        raise Cargoflow2StagingError(
            "the attempt funds model drifted from its pinned founding construction"
        )
    return dict(
        schema="d5-cargoflow2-funds-model-of-record-v1",
        start_funds=int(plan.start_funds),
        purchase_quote=int(plan.purchase_quote),
        founding_loan=int(plan.founding_loan),
        interest_rate=int(plan.interest_rate),
        station_fee=int(plan.station_fee),
        launch_day=int(plan.launch_day),
        arrival_bound_days=int(plan.arrive_max_days),
        flow_span_days=int(plan.flow_span_days),
        day_budget=int(plan.day_budget),
        other_expenses="none of record (§4.2 item 5): inflation and "
        "infrastructure maintenance are off; any observed funds movement "
        "outside the pinned charge set plus measured income halts the "
        "attempt fail-closed",
        statement=(
            "the modeled-trajectory fence of record: the exact purchase "
            "debit, the staircase monthly interest plus the pinned station "
            "fee at each economy-month boundary, the per-economy-day "
            "running costs through the exact 8.8 fixed-point fraction "
            "carry, and the delivery income attributed from the engine's "
            "own quarter accounting at the same observation instants; the "
            "Feb 1 charge of record (167 + 25 = 192, funds 489650 → "
            "489458) is the E99-replicated cross-check of record"
        ),
    )


def cargoflow2_plan_policy() -> dict:
    """The authorized plan policy for the staged attempt candidate."""
    plan = cargoflow2_pipeline_plan()
    schedule = cargoflow2_schedule()
    plan_digest = plan_digest_of(schedule)
    if (
        not schedule
        or schedule[0]["exchange"] != plan.schedule[0]
        or schedule[0]["offset"] != -1
        or schedule[0]["op"] != "site"
        or schedule[11]["exchange"] != "flow-00"
        or schedule[11]["offset"] != 0
    ):
        raise Cargoflow2StagingError("the attempt schedule must begin with the site pin")
    expected_world = _cargoflow2_expected_world(plan)
    return dict(
        company=plan.company,
        target_tile=int(CARGOFLOW2_PICKUP_TILE),
        max_cost=int(CARGOFLOW2_ENGINE_MAX_COST),
        command="purchase",
        command_statement=(
            "the staged attempt's cost-bearing surface is exactly the "
            "quote-first purchase inside the pinned authority ceiling; the "
            "two order sets and the start are freight-family commands of "
            "record, every other exchange observes, and no cost-bearing "
            "operation outside this chain is inside the candidate forever"
        ),
        stale_rule=(
            "each exchange re-observes its pinned identity immediately "
            "before its dispatch inside the handler; any mismate stops the "
            "phase without further dispatch and preserves the verified "
            "prefix"
        ),
        identity=(
            f"wire contract protocol {CARGOFLOW2_PROTOCOL} "
            f"({CARGOFLOW2_NAME}): every exchange presents one uniform "
            "prelaunch seal digest; the attempt runs the freight-family "
            "instrument chain plus ladder with one company, one vehicle "
            "and exactly one purchase"
        ),
        schedule=schedule,
        plan_digest=plan_digest,
        plan_model_digest=plan.digest,
        schedule_version=1,
        observations=[
            dict(
                industry=int(plan.pickup_industry),
                kind="PRODUCING_PICKUP",
            ),
            dict(
                industry=int(plan.bay_industry),
                kind="ACCEPTING_BAY",
            ),
        ],
        hypotheses=cargoflow2_hypotheses(),
        ladder_grid=_cargoflow2_ladder_grid(),
        funds_model=cargoflow2_funds_model_gate(),
        world=expected_world,
        read_only=dict(
            schema=CARGOFLOW2_READ_ONLY_SCHEMA,
            permitted_ops=list(CARGOFLOW2_OPS),
            max_cost=0,
            funds_readback_required=True,
            statement=(
                "every exchange is fail-closed: a success frame echoes its "
                "funds level and, from the site pin onward, its "
                "quarter-income read at the same observation instant (§4.5: "
                "one response, one instant), and only the pinned purchase, "
                "the two order sets and the start ride company mode; an "
                "attempt verdict never re-opens a freight attempt and no "
                "halted E99 label is relabeled"
            ),
        ),
    )


def cargoflow2_budgets() -> dict:
    """The staged budget table for the attempt candidate."""
    plan = cargoflow2_pipeline_plan()
    return dict(
        launches=1,
        connection_attempts=1,
        requests=CARGOFLOW2_REQUEST_BUDGET,
        planned_exchanges=PLANNED_CARGOFLOW2_EXCHANGES,
        gsadmin_bytes=MAX_CARGOFLOW2_REQUEST_BYTES,
        response_bytes=MAX_CARGOFLOW2_RESPONSE_BYTES,
        retries=0,
        reconnects=0,
        readiness_seconds=45,
        request_seconds=10,
        watch_seconds=freight_native.FREIGHT_WATCH_WALL_SECONDS,
        exchange_margin_seconds=CARGOFLOW2_EXCHANGE_MARGIN_SECONDS,
        watch_ticks=int(CARGOFLOW2_WAIT_MAX_TICKS),
        wait_day_cap=int(CARGOFLOW2_WAIT_DAY_CAP),
        day_budget=int(plan.day_budget),
        total_seconds=900,
        max_cost=int(CARGOFLOW2_ENGINE_MAX_COST),
        expected_start_funds=int(plan.start_funds),
    )


def cargoflow2_expected_readback_policy() -> dict:
    return dict(
        chain=(
            "the fixed instrument chain is the freight-family chain of "
            "record ported in meaning: the site pin re-pins the corridor "
            "identities, the engine census admits the pinned engine "
            "fail-closed and pins the raw running cost of record, the "
            "purchase realizes exactly its pinned tested quote, the "
            "vehicle reads back in the depot and RUNNING after the start, "
            "both orders set and independently read back with their pinned "
            "flags (pickup 0, delivery 128), the monitors arm, and every "
            "success frame echoes its own observation instant and income "
            "read"
        ),
        arrival=(
            "arrive-00 polls per tick for the first pinned pickup-stop "
            "arrival within its 5-economy-day bound, latches the arrival "
            "(day, tick) with its empty-load echo of record and the "
            "ladder anchor; a timeout is a terminal ARRIVE_TIMEOUT, never "
            "a retry"
        ),
        ladder=(
            "the ladder is exact: a flow sample's day minus its latched "
            "anchor must equal its pinned offset both in the handler and "
            "on the Python side; an overshoot is WINDOW_EXHAUSTED, a "
            "clock stall is CLOCK_STALLED, and a later anchor drift is a "
            "phase halt with the prefix preserved"
        ),
        funds=(
            "every exchange reconciles against the modeled trajectory of "
            "record exactly (§4.4 zero residual): the exact purchase "
            "debit, the monthly staircase plus the pinned station fee, "
            "the 8.8 fixed-point day running cost through its exact "
            "fraction carry with the start day partial from its latched "
            "tick, and the engine-read income attributed at the same "
            "instants; residual ≠ 0 is a halt, never a tolerance"
        ),
        verdicts=(
            "the delivery verdict is rebuilt from the receipts alone "
            "(§7): the seven acceptance criteria hold → "
            "CARGOFLOW2_DELIVERY_VERIFIED; a latched load never delivered "
            "→ CARGOFLOW2_LOADED_NEVER_DELIVERED; delivery received "
            "without a later measured drain → "
            "CARGOFLOW2_CONSUMPTION_UNOBSERVED; the observed arrival with "
            "a queue that never filled → CARGOFLOW2_QUEUE_NEVER_FILLED; "
            "a funds residual → CARGOFLOW2_FUNDS_DIVERGED; an unobserved "
            "or unfinished ladder decides CARGOFLOW2_GATE_UNDECIDED_"
            "INCOMPLETE"
        ),
        receipt=(
            "CARGOFLOW2_COMPLETE only after all 25 exchanges verify in "
            "execution order with certified cleanup; a refused, missing, "
            "malformed, out-of-order, stale, divergent or inconclusive "
            "exchange leaves the attempt incomplete forever"
        ),
    )


# --- Attempt prerequisite binding (depot lineage re-scoped) -----------------


def cargoflow2_prerequisite_binding(prerequisite: Path | None = None) -> dict:
    """Bind the consumed depot-mutation attempt of record, attempt-scoped.

    The attempt prerequisite is exactly the freight v2 prerequisite: the
    pinned, consumed, fully replay-verified depot-mutation attempt at its
    retained after-save digest, with the verified observe-only reload
    chain embedded. The checked derivation of record is the freight v2
    binding's own (``freight_v2_native.prerequisite_binding``); this
    wrapper only scope-checks the pinned directory against the attempt
    pins and re-labels the recorded verification statement for the
    cargo-flow delivery lineage. A wrong directory is an attempt staging
    error before any world is staged.
    """
    prerequisite = Path(PINNED_PREREQUISITE if prerequisite is None else prerequisite).resolve()
    if prerequisite != freight_v2_native.DEPOT_PREREQUISITE:
        raise Cargoflow2StagingError(
            "the attempt source world requires the pinned depot prerequisite"
        )
    try:
        binding = freight_v2_native.prerequisite_binding(prerequisite)
    except freight_v2_native.FreightV2StagingError as error:
        raise Cargoflow2StagingError(str(error)) from None
    if binding.get("schema") != D5_CARGOFLOW2_PREREQUISITE_SCHEMA:
        raise Cargoflow2StagingError(
            "the attempt prerequisite schema drifted from the depot lineage"
        )
    if Path(binding["retained_directory"]).resolve() != prerequisite:
        raise Cargoflow2StagingError(
            "the attempt prerequisite binding is not the pinned retained attempt"
        )
    return dict(
        binding,
        verification=(
            "full replay verification of the consumed depot-mutation attempt "
            "receipt (F12_MUTATION_COMPLETION_VERIFIED) plus the pinned "
            "authoritative after-save digest and the verified observe-only "
            "reload chain (attempt-scoped binding of the shared freight v2 "
            "derivation of record)"
        ),
    )


# --- Attempt candidate staging ------------------------------------------------


def staged_cargoflow2_composition() -> tuple[dict[str, bytes], str, int]:
    """Byte-exact save-restore composition for the D5 delivery attempt.

    The retained staged ``info.nut`` announces the save's stored GameScript
    identity (name/version); the staged main is the protocol-11 delivery
    handler of its own package directory (``d5_cargoflow2_package``) with
    the save-restore bridge class defined inline after the proof class. No
    frozen package byte drifts for the attempt's sake.
    """
    with zipfile.ZipFile(SEED17_RUN / "frozen-source.zip") as archive:
        info_bytes = archive.read("staged/info.nut")
    text = info_bytes.decode()
    create_instance = re.search(r'CreateInstance\(\)\s*\{\s*return\s+"([^"]+)"', text)
    version = re.search(r"GetVersion\(\)\s*\{\s*return\s+(\d+)", text)
    if create_instance is None or version is None or SOURCE_SAVE_GS_NAME not in text:
        raise Cargoflow2StagingError("retained staged GameScript identity incomplete")
    main_text = (CARGOFLOW2_PACKAGE / "main.nut").read_text()
    bridge_class = create_instance.group(1)
    expected_bridge = f"class {bridge_class} extends D5CargoFlow2Proof"
    if expected_bridge not in main_text:
        raise Cargoflow2StagingError(
            f"staged attempt main.nut missing required bridge class {bridge_class}"
        )
    return (
        {
            "info.nut": info_bytes,
            "main.nut": (CARGOFLOW2_PACKAGE / "main.nut").read_bytes(),
        },
        bridge_class,
        int(version.group(1)),
    )


def prepare_cargoflow2_candidate(
    directory: Path, *, prerequisite: Path | None = None
) -> PreparedProof:
    """Stage the fresh save-load composition; no process or connection."""
    plan = _require_cargoflow2_plan(cargoflow2_plan())
    prerequisite = Path(PINNED_PREREQUISITE if prerequisite is None else prerequisite).resolve()
    if prerequisite != PINNED_PREREQUISITE:
        raise Cargoflow2StagingError(
            "the attempt source world requires the pinned depot prerequisite"
        )
    schedule = cargoflow2_schedule()
    policy = cargoflow2_plan_policy()
    if len(schedule) != len(plan.schedule):
        raise Cargoflow2StagingError("the scheduled attempt exchanges drifted")
    if policy["schedule_version"] != 1:
        raise Cargoflow2StagingError("the staged attempt schedule derivation drifted")
    if sha256(BINARY) != BINARY_SHA256 or matching_processes(BINARY):
        raise Cargoflow2StagingError("pinned binary / exclusive runtime gate failed")
    directory = directory.resolve()
    binding = cargoflow2_prerequisite_binding(prerequisite)
    welcome = binding["expected_welcome"]
    world = stage_world(binding, welcome)
    if sha256(source_save_path(world)) != world["save_sha256"]:
        raise Cargoflow2StagingError("the staged source-save digest mismatch")
    directory.mkdir(parents=True, exist_ok=False)
    workspace = freight_native.RuntimeWorkspace.create(directory / "isolated", retain=True)
    reservation = EndpointReservation.allocate()
    try:
        key = AuthorizedKey.generate()
        key_path = workspace.root / ".admin-secret"
        with os.fdopen(
            os.open(key_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600), "wb"
        ) as stream:
            stream.write(key._secret)
        workspace.write_config(
            freight_native.AdminSettings(
                password="",
                port=reservation.admin_port,
                game_port=reservation.game_port,
                authorized_public_key_hex=key.public_hex,
            )
        )
        config = workspace.config.read_text().replace(
            "pause_on_newgame = true", "pause_on_newgame = false"
        )
        config += (
            "\n[ai]\nai_in_multiplayer = true\n[misc]\ngraphicsset = OpenGFX\n"
            f"[game_scripts]\n{SOURCE_SAVE_GS_NAME} = \n"
        )
        workspace.config.write_text(config)
        graphics = stage_opengfx(
            PROJECT / "artifacts/runtime/verified-assets/opengfx-8.0-all.zip",
            workspace.root / "baseset/OpenGFX",
        )
        write_json(
            directory / "graphics-identity.json",
            dict(asdict(graphics), directory=str(graphics.directory)),
        )
        staged_save = workspace.root / "source.sav"
        shutil.copyfile(source_save_path(world), staged_save)
        verify_staged_source_save({"save_sha256": world["save_sha256"]}, staged_save)
        (workspace.game / SOURCE_SAVE_GS_NAME).mkdir()
        composition, create_instance, version = staged_cargoflow2_composition()
        for name in ("info.nut", "main.nut"):
            (workspace.game / SOURCE_SAVE_GS_NAME / name).write_bytes(composition[name])
        (workspace.ai / STAGED_AI_DIRECTORY).mkdir()
        for name in ("info.nut", "main.nut"):
            shutil.copyfile(AI_PACKAGE / name, workspace.ai / STAGED_AI_DIRECTORY / name)
        argv = (
            str(BINARY),
            f"-D127.0.0.1:{reservation.game_port}",
            "-c",
            str(workspace.config),
            "-x",
            "-X",
            "-g",
            str(staged_save),
            "-dscript=4,grf=1,net=3",
        )
        spec = freight_native.LaunchSpecification(
            workspace,
            freight_native.RuntimeIdentity(BINARY.resolve(), "15.3", BINARY_SHA256),
            argv,
            workspace.root,
            workspace.environment,
            workspace.logs / "stdout.log",
            workspace.logs / "stderr.log",
        )
        frozen = source_freeze()
        for source in (CARGOFLOW2_PACKAGE, AI_PACKAGE):
            for path in sorted(source.glob("*.nut")):
                frozen[str(path.resolve())] = sha256(path)
        frozen.update(
            {
                str(path): sha256(path)
                for path in sorted(workspace.root.rglob("*"))
                if path.is_file() and path.name != ".admin-secret"
            }
        )
        frozen.update(freight_native.d2_source_closure(CARGOFLOW2_CLOSURE_ROOT))
        frozen.update(freight_native.d2_dependency_inventory(CARGOFLOW2_CLOSURE_ROOT))
        prepared = PreparedProof(
            directory,
            spec,
            key_path,
            key.public_hex,
            (reservation.game_port, reservation.admin_port),
        )
        metadata = dict(
            schema=D5_CARGOFLOW2_PRELAUNCH_SCHEMA,
            milestone=MILESTONE_CARGOFLOW2,
            kind=KIND,
            attempt=D5_CARGOFLOW2_ATTEMPT,
            candidate_directory=CARGOFLOW2_CANDIDATE_DIRECTORY,
            workspace=str(workspace.root),
            binary_sha256=BINARY_SHA256,
            argv=list(argv),
            public_key=key.public_hex,
            game_port=reservation.game_port,
            admin_port=reservation.admin_port,
            world=world,
            game_script_identity=dict(
                name=SOURCE_SAVE_GS_NAME,
                version=version,
                create_instance=create_instance,
                statement=(
                    "the staged composition announces the save's stored "
                    "GameScript name/version; the protocol-11 "
                    "D5CargoFlow2Proof ships in its own bounded package "
                    "(d5_cargoflow2_package) and satisfies the frozen "
                    "save-restore identity through its bridge class, with "
                    "no company command outside its pinned chain"
                ),
            ),
            save_policy=(
                "owned session-before.sav and after-diagnostic.sav only; the "
                "authoritative source save, the prerequisite attempt record "
                "and every historical artifact stay untouched; the attempt "
                "saves nothing itself"
            ),
            plan_policy=policy,
            expected_readback=cargoflow2_expected_readback_policy(),
            bootstrap_command=f"start_ai {STAGED_AI_DIRECTORY}",
            execution_command=[
                str(PROJECT / ".venv/bin/python"),
                "-m",
                "app.simulation.openttd.proof.corridor_cargoflow2_native",
                "run",
                str(directory),
            ],
            budgets=cargoflow2_budgets(),
            cleanup=[
                "close secure session",
                "quit and reap process",
                "verify endpoints",
                "retain session logs and the pre-attempt save",
                "remove credential",
                "dispose owned workspace",
                "never modify the retained save or any historical artifact",
            ],
            authorization=(
                "PENDING — requires ONE fresh operator authorization after "
                "all preflight gates; offline staging consumed no claim and "
                "no authorization file exists"
            ),
            pin_provenance=dict(
                source=int(CARGOFLOW2_PICKUP_TILE),
                manifest_verified=True,
                statement=(
                    "the attempt binds the authoritative depot-mutation "
                    "after-save (183b20273a54ebe1a2cd9306145a9ea820bbd6114"
                    "b1608c42079b4e1b1efe6a6, world-pin version 3) with its "
                    "verified reload chain, and the pinned OpenTTD 15.3 "
                    "binary; the pinned 25-exchange schedule is the "
                    "contract module's own guarded derivation plus this "
                    "pipeline's trust-anchored ladder"
                ),
            ),
            environment=freight_native.launch_environment(prepared),
            environment_overrides=dict(spec.environment),
            frozen=frozen,
            cross_schedule_guard=dict(
                schema="d5-cargoflow2-cross-guard-v1",
                protocol=CARGOFLOW2_PROTOCOL,
                protocol_name=CARGOFLOW2_NAME,
                cargoflow2_ops=list(CARGOFLOW2_OPS),
                statement=(
                    "this candidate refuses every foreign request on its "
                    "session surface: a freight request (any protocol-5/8 "
                    "op) fails the delivery session check with protocol 11 "
                    "required, a survey, census or dispatch-probe request "
                    "fails it the same way, and any delivery request fails "
                    "the freight, survey, census and probe session checks "
                    "with their required protocols 5/6/8/9/10"
                ),
            ),
        )
        metadata["prerequisite"] = dict(
            schema=D5_CARGOFLOW2_PREREQUISITE_SCHEMA,
            attempt=binding["attempt"],
            milestone=binding["milestone"],
            directory=binding["retained_directory"],
            prelaunch_sha256=binding["prelaunch_digest"],
            after_save_sha256=binding["save_sha256"],
            verification=binding["verification"],
        )
        metadata["prerequisite_provenance"] = binding["provenance"]
        write_json(directory / "PRELAUNCH.json", metadata)
        (directory / "PRELAUNCH.sha256").write_text(sha256(directory / "PRELAUNCH.json") + "\n")
        return prepared
    finally:
        reservation.close()


# --- Attempt preflight (offline launch-boundary rehearsal) --------------------


def cargoflow2_preflight(prepared: PreparedProof) -> dict:
    """Offline launch-boundary rehearsal: re-derive every binding, trust nothing.

    The attempt has one schedule version and one plan; every derivation
    below is re-derived from the module pins and the staged record must
    match it exactly, so a record claiming a foreign lineage or a drifted
    schedule is refused here.
    """
    directory = prepared.directory
    if sha256(directory / "PRELAUNCH.json") != (directory / "PRELAUNCH.sha256").read_text().strip():
        raise ValueError("the attempt prelaunch seal mismatch")
    metadata = read_prelaunch(directory)
    if (directory / "CLAIM.json").exists():
        raise ValueError("the one native attempt already consumed")
    if metadata.get("schema") != D5_CARGOFLOW2_PRELAUNCH_SCHEMA:
        raise ValueError("the staged prelaunch record is not the D5 cargoflow-2 lineage")
    if metadata.get("kind") != KIND or metadata.get("milestone") != MILESTONE_CARGOFLOW2:
        raise ValueError("the staged attempt lineage drifted")
    if metadata.get("attempt") != D5_CARGOFLOW2_ATTEMPT:
        raise ValueError("the staged attempt identity drifted from its own scope")
    verify_freeze(metadata["frozen"])
    freight_native.require_frozen_d2_closure(metadata["frozen"], CARGOFLOW2_CLOSURE_ROOT)
    freight_native.require_frozen_d2_dependencies(metadata["frozen"], CARGOFLOW2_CLOSURE_ROOT)
    policy = metadata["plan_policy"]
    plan = cargoflow2_pipeline_plan()
    schedule = staged_cargoflow2_schedule(policy)
    if policy["schedule"] != schedule or policy["plan_digest"] != plan_digest_of(schedule):
        raise ValueError("the staged attempt schedule drifted from the compiled derivation")
    if policy["plan_model_digest"] != plan.digest:
        raise ValueError("the staged attempt plan digest drifted from the pinned plan")
    if policy.get("schedule_version") != 1:
        raise ValueError("the staged attempt schedule version drifted")
    for row in schedule:
        if row["op"] not in CARGOFLOW2_OPS:
            raise ValueError("a scheduled attempt row carries a foreign op")
        if row["op"] == "flow":
            index = int(row["exchange"].rsplit("-", 1)[1])
            if row["offset"] != int(CARGOFLOW2_FLOW_OFFSETS[index]):
                raise ValueError("a scheduled flow row drifted from its pinned ladder offset")
        elif row["op"] in ("finance", "finish"):
            if row["offset"] != CARGOFLOW2_TAIL_OFFSET:
                raise ValueError("a scheduled tail row drifted from its pinned economy day")
        elif row["op"] == "order":
            if row["order_index"] != (0 if row["exchange"] == "order-00" else 1):
                raise ValueError("a scheduled order row drifted from its pinned stop index")
        elif row["op"] == "arrive-watch":
            if row["watch_days"] != CARGOFLOW2_ARRIVE_MAX_DAYS:
                raise ValueError("the arrival watch row drifted from its pinned 5-day bound")
        elif row["offset"] != -1:
            raise ValueError("a fixed-chain row carries an unexpected ladder echo")
    if policy.get("max_cost") != int(CARGOFLOW2_ENGINE_MAX_COST):
        raise ValueError("the staged attempt cost ceiling drifted from the pinned authority")
    if policy["read_only"]["schema"] != CARGOFLOW2_READ_ONLY_SCHEMA:
        raise ValueError("the staged attempt surface record drifted")
    if policy["read_only"]["permitted_ops"] != list(CARGOFLOW2_OPS):
        raise ValueError("the staged attempt's op surface drifted")
    expected_world = _cargoflow2_expected_world(plan)
    for name, expected in expected_world.items():
        if policy["world"].get(name) != expected:
            raise ValueError(f"the staged attempt world pin {name} drifted")
    if policy["target_tile"] != int(CARGOFLOW2_PICKUP_TILE):
        raise ValueError("the staged attempt control tile drifted")
    if policy["observations"] != [
        dict(
            industry=int(plan.pickup_industry),
            kind="PRODUCING_PICKUP",
        ),
        dict(
            industry=int(plan.bay_industry),
            kind="ACCEPTING_BAY",
        ),
    ]:
        raise ValueError("the staged attempt observation kinds drifted")
    if policy["ladder_grid"] != _cargoflow2_ladder_grid():
        raise ValueError("the staged attempt ladder grid drifted from the pinned geometry")
    if policy["funds_model"] != cargoflow2_funds_model_gate():
        raise ValueError("the staged attempt funds-model pins drifted from the pinned fence")
    staged_hypotheses = policy["hypotheses"]
    expected_hypotheses = cargoflow2_hypotheses()
    if staged_hypotheses.get("state") != expected_hypotheses.get("state"):
        raise ValueError(
            f"the staged attempt hypothesis state is not its own derivation "
            f"({expected_hypotheses.get('state')})"
        )
    if expected_hypotheses.get("state") == "RETAINED_PROBE_REBOUND":
        if staged_hypotheses != expected_hypotheses:
            raise ValueError("the staged attempt hypothesis record drifted from the retained bytes")
    if metadata.get("budgets") != cargoflow2_budgets():
        raise ValueError("the staged attempt budget pins drifted")
    if metadata["public_key"] != prepared.public_key or metadata["binary_sha256"] != BINARY_SHA256:
        raise ValueError("the staged identity pins drifted")
    binding = cargoflow2_prerequisite_binding(Path(metadata["prerequisite"]["directory"]))
    required = ("attempt", "milestone", "directory", "prelaunch_sha256", "after_save_sha256")
    if {name: metadata["prerequisite"][name] for name in required} != dict(
        attempt=binding["attempt"],
        milestone=binding["milestone"],
        directory=binding["retained_directory"],
        prelaunch_sha256=binding["prelaunch_digest"],
        after_save_sha256=binding["save_sha256"],
    ):
        raise ValueError("the staged prerequisite binding drifted from its verified record")
    if metadata["prerequisite"].get("schema") != D5_CARGOFLOW2_PREREQUISITE_SCHEMA:
        raise ValueError("the staged prerequisite schema drifted")
    stored_world = metadata["world"]
    if (
        stored_world.get("retained_directory") != binding["retained_directory"]
        or stored_world.get("source_save") != binding["save"]
        or stored_world.get("save_sha256") != binding["save_sha256"]
        or stored_world.get("save_sha256") != PINNED_PREREQUISITE_AFTER_SAVE
    ):
        raise ValueError("the staged world is not the pinned depot after-save")
    if metadata["world"]["expected_welcome"] != binding["expected_welcome"]:
        raise ValueError("the retained world identity requirements drifted")
    verify_staged_source_save(
        {"save_sha256": metadata["world"]["save_sha256"]},
        Path(metadata["workspace"]) / "source.sav",
    )
    composition, _, _ = staged_cargoflow2_composition()
    staged_identity = Path(metadata["workspace"]) / "game" / SOURCE_SAVE_GS_NAME
    if staged_identity.joinpath("info.nut").read_bytes() != composition["info.nut"]:
        raise ValueError("the staged GameScript identity drifted from the retained composition")
    if staged_identity.joinpath("main.nut").read_bytes() != composition["main.nut"]:
        raise ValueError("the staged attempt handler drifted from its bounded package")
    if not prepared.spec.workspace.root.is_relative_to(directory / "isolated"):
        raise ValueError("the workspace ownership mismatch")
    ClearingNativeBackend(authorized_one_launch=True).preflight(prepared)
    reservation = EndpointReservation.allocate(*prepared.endpoints)
    reservation.close()
    return metadata


# --- Wire protocol 11: secure sessions and one-launch backend ----------------


def encode_cargoflow2_request(payload: bytes) -> bytes:
    return encode_gamescript(payload, max_payload_bytes=MAX_CARGOFLOW2_REQUEST_BYTES)


def decode_cargoflow2_request(payload: bytes) -> bytes:
    return decode_gamescript(payload, max_payload_bytes=MAX_CARGOFLOW2_REQUEST_BYTES)


class Cargoflow2SecureSession(SecureAdminSession):
    """Only the delivery operations extend the secure write policy.

    A freight request cannot parse as a ``Cargoflow2Request`` (protocol 11
    required, and the freight/survey/census/probe op sets are outside the
    attempt Literal), so no foreign protocol exchange can travel on the
    delivery session; a delivery request parses on none of the older
    sessions for the mirrored reason.
    """

    def validate_outbound(self, frame: bytes) -> None:
        if self.state is not AuthState.ACTIVE:
            raise ValueError("encrypted ACTIVE stream required")
        if len(frame) < 3 or struct.unpack_from("<H", frame)[0] != len(frame):
            raise ValueError("invalid frame")
        if frame[2] == ADMIN_GAMESCRIPT:
            request = Cargoflow2Request.model_validate_json(decode_cargoflow2_request(frame[3:]))
            if request.op not in CARGOFLOW2_OPS:
                raise ValueError("a foreign op cannot ride the delivery session")
            request.to_bytes()
        elif frame not in (gamescript_subscription(), encode_admin_quit()):
            super().validate_outbound(frame)


class Cargoflow2NativeBackend(freight_native.FreightNativeBackend):
    """One-launch backend carrying the shared consumed marker, delivery session."""

    launch_marker_schema = D5_CARGOFLOW2_LAUNCH_CONSUMED_SCHEMA

    async def connect(self, prepared: PreparedProof, *, frame_observer) -> Cargoflow2SecureSession:
        if not any(
            r["table"] == "tcp" and r["local_port"] == prepared.endpoints[1] and r["state"] == 10
            for r in kernel_socket_rows()
        ):
            raise ValueError("the native Admin listener readiness absent")
        key = AuthorizedKey.from_bytes(prepared.key_path.read_bytes())
        session = await Cargoflow2SecureSession.connect_secure(
            "127.0.0.1",
            prepared.endpoints[1],
            5,
            key=key,
            frame_observer=frame_observer,
        )
        self.session = session
        return session


def cargoflow2_exchange_timeout_seconds(*, budget_table: dict, op: str, offset: int) -> float:
    """Instant exchanges keep the request budget; waits ride the window.

    The fixed chain and the tail are bounded immediate request/readback
    exchanges; ``arrive-00`` may legitimately spend its whole 5-economy-day
    arrival window before returning its bounded observation, and every
    non-zero flow offset sleeps in-package until its ladder day, so each
    gets the freight-window wall clock plus the shared client margin. A
    foreign (op, offset) pairing is never dispatchable and spends no
    budget at all.
    """
    request_seconds = float(budget_table["request_seconds"])
    if op == "arrive-watch":
        return float(budget_table["watch_seconds"]) + float(budget_table["exchange_margin_seconds"])
    if op == "flow":
        if int(offset) not in CARGOFLOW2_FLOW_OFFSETS:
            raise ValueError("no delivery budget exists for a foreign ladder offset")
        if int(offset) > 0:
            return (
                float(budget_table["watch_seconds"])
                + float(budget_table["exchange_margin_seconds"])
            )
        return request_seconds
    if op in ("finance", "finish"):
        if int(offset) != CARGOFLOW2_TAIL_OFFSET:
            raise ValueError("the tail exchanges ride the flow-11 economy day of record")
        return request_seconds
    if op in ("site", "engine", "purchase", "vread", "order", "order-read", "monitor", "start"):
        return request_seconds
    raise ValueError(f"no delivery budget exists for the op {op!r}")


def event_loop_deadline(seconds: float) -> float:
    return time.monotonic() + seconds


def _cargoflow2_exchange_request(
    entry: dict, seal: str, plan: Cargoflow2Plan, state: dict
) -> Cargoflow2Request:
    """Build one fixed protocol-11 request at its planned position.

    Every non-site exchange ships the pinned engine identity; the vehicle
    echo is -1 until the purchase response names it, then the response's
    vehicle for every later exchange; the purchase carries its pinned
    tested quote and authority ceiling; the order rows pin one stop index
    with its pinned flags; ``arrive-00`` carries its 5-economy-day bound;
    the ladder and tail rows carry their planned offsets; every other
    request stays quiet. Post-purchase rows without a pinned vehicle are a
    driver fault, never a request (fail closed before any byte).
    """
    op = entry["op"]
    base: dict[str, Any] = dict(
        op=op,
        request_id=entry["exchange"],
        plan=seal,
        company=plan.company,
        max_cost=0,
        pickup=int(plan.pickup),
        delivery=int(plan.delivery),
        depot=int(plan.depot),
    )
    if op == "site":
        return Cargoflow2Request(**base)
    base["engine"] = int(CARGOFLOW2_ENGINE)
    if op == "engine":
        return Cargoflow2Request(**base)
    if op == "purchase":
        base["max_cost"] = int(CARGOFLOW2_ENGINE_MAX_COST)
        base["expected_cost"] = int(CARGOFLOW2_PURCHASE_QUOTE)
        return Cargoflow2Request(**base)
    vehicle = int(state["vehicle"])
    if vehicle < 0:
        raise ValueError(f"the {entry['exchange']} request has no pinned vehicle yet")
    base["vehicle"] = vehicle
    if op == "order":
        if int(entry["order_index"]) == 0:
            base["order_index"] = 0
            base["order_flags"] = int(CARGOFLOW2_ORDER_PICKUP_FLAGS)
        else:
            base["order_index"] = 1
            base["order_flags"] = int(CARGOFLOW2_ORDER_DELIVERY_FLAGS)
    elif op == "arrive-watch":
        base["watch_days"] = int(entry["watch_days"])
    elif op in ("flow", "finance", "finish"):
        base["offset"] = int(entry["offset"])
    return Cargoflow2Request(**base)


def cargoflow2_request_table(
    plan: Cargoflow2Plan, seal: str, *, vehicle: int
) -> list[Cargoflow2Request]:
    """The offline derivation of the attempt's request table under one seal.

    The pre-purchase rows always carry -1 both ways; the post-purchase
    rows carry the vehicle handle given here — at run time that handle is
    the purchase response's vehicle, pinned by the driver before its first
    use, so the offline table only ever checks the build shape. Every row
    is verified against the wire contract's trust anchor: an op, echo or
    position drift refuses the whole derivation.
    """
    state = dict(vehicle=int(vehicle))
    rows: list[Cargoflow2Request] = []
    for entry in cargoflow2_schedule():
        request = _cargoflow2_exchange_request(entry, seal, plan, state)
        verify_request_against_cargoflow2_plan(request, plan=plan, seal=seal)
        rows.append(request)
        if entry["op"] == "purchase":
            state["vehicle"] = int(vehicle)
    return rows


def _cargoflow2_day_authority(
    entry: dict,
    plan: Cargoflow2Plan,
    *,
    elapsed_days: int | None,
    anchor: int | None,
) -> str | None:
    """The typed pre-dispatch refusals for the aggregate day authority (§5.3).

    Returns the refusal text when the planned exchange can no longer fit
    the 60-economy-day attempt authority against the elapsed day ledger —
    the freight v2 window gate (E53) re-pointed. The ledger's provenance
    is the readback day echoes themselves: every success frame echoes its
    observation instant, so the pipeline gate's arithmetic stays
    indistinguishable-by-induction from the retained evidence. Ladder-day
    rows are checked exactly against their latched anchor arrival; the
    arrival watch is checked against its pinned bound; instant exchanges
    pass. The stopped attempt dispatches nothing further, and the package
    enforces the same authority independently (dual enforcement).
    """
    if entry["op"] not in ("arrive-watch", "flow", "finance", "finish"):
        return None
    day_budget = int(plan.day_budget)
    if elapsed_days is not None and int(elapsed_days) > day_budget:
        return (
            f"the attempt's elapsed economy-day ledger ({int(elapsed_days)} days) "
            f"exceeded its {day_budget}-day authority before "
            f"{entry['exchange']} (the AUTHORITY_EXCEEDED surface)"
        )
    if entry["op"] == "arrive-watch":
        if elapsed_days is None:
            return None
        if int(elapsed_days) + int(plan.arrive_max_days) > day_budget:
            return (
                f"the arrival watch's {int(plan.arrive_max_days)}-day bound cannot "
                f"fit the remaining day authority before {entry['exchange']} "
                "(the AUTHORITY_EXCEEDED surface)"
            )
        return None
    if anchor is None:
        return (
            f"the {entry['exchange']} ladder day cannot be bounded before its "
            "arrival anchor is latched (the AUTHORITY_EXCEEDED surface)"
        )
    if int(anchor) + int(entry["offset"]) - int(plan.launch_day) > day_budget:
        return (
            f"the {entry['exchange']} ladder day escapes the attempt's "
            f"{day_budget}-day authority (the AUTHORITY_EXCEEDED surface)"
        )
    return None


async def cargoflow2_exchange(
    session,
    request: Cargoflow2Request,
    directory: Path,
    *,
    budget_table: dict | None = None,
    overall_deadline: float | None = None,
    clock=time.monotonic,
    timeout_factory=asyncio.timeout,
) -> Cargoflow2Readback:
    """One sealed protocol-11 exchange; every frame and file retained.

    Bounded request bytes, the op/offset-aware timeout clamped to the
    overall attempt budget, duplicate/stale frame refusal and fail-closed
    parsing — the E99 probe exchange twin, over the 512/1400-byte
    protocol-11 bounds.
    """
    budget_table = budget_table if budget_table is not None else cargoflow2_budgets()
    permitted = cargoflow2_exchange_timeout_seconds(
        budget_table=budget_table, op=request.op, offset=request.offset
    )
    if overall_deadline is not None:
        remaining = overall_deadline - clock()
        if remaining <= 0:
            raise TimeoutError("the delivery attempt overall budget exhausted")
        permitted = min(permitted, remaining)
    raw = request.to_bytes()
    (directory / (request.request_id + "-request.json")).write_bytes(raw)
    await session.send(encode_cargoflow2_request(raw))
    decoder = AdminFrameDecoder()
    try:
        async with timeout_factory(permitted):
            while True:
                chunk = await session.receive()
                if not chunk:
                    raise ConnectionError("the delivery session stream disconnected")
                game_frames = []
                for kind, payload in decoder.feed_frames(chunk):
                    if kind != SERVER_GAMESCRIPT:
                        raise ValueError("an unexpected protocol-11 packet")
                    game_frames.append(payload)
                if len(game_frames) > 1:
                    raise ValueError("a duplicate protocol-11 response frame")
                if game_frames:
                    body = game_frames[0]
                    if (directory / (request.request_id + "-response.json")).exists():
                        raise ValueError("a duplicate protocol-11 response file")
                    response = decode_gamescript(
                        body, max_payload_bytes=MAX_CARGOFLOW2_RESPONSE_BYTES
                    )
                    readback = Cargoflow2Readback.parse_for(request, response)
                    (directory / (request.request_id + "-response.json")).write_bytes(response)
                    return readback
    except TimeoutError:
        raise TimeoutError(
            f"the delivery exchange {request.request_id} exceeded its {permitted:.1f}s budget"
        ) from None


# --- Attempt execution (authorized one-attempt path only) ---------------------


def apply_cargoflow2_cleanup_outcome(result: dict, *, complete: bool) -> None:
    """Fail closed on the attempt's final cleanup verdict."""
    result["cleanup_complete"] = bool(complete)
    if complete:
        return
    result["cleanup_failure"] = True
    if result.get("verified") is True or result.get("status") == "NATIVE_CARGOFLOW2_COMPLETE":
        freight_native.deny_verification(
            result,
            status="FAILED_CLEANUP",
            message=(
                "ValueError: cleanup was not certified; no verified attempt "
                "completion is possible"
            ),
        )


async def execute_cargoflow2_attempt(prepared: PreparedProof, backend) -> dict:
    """Execute the authorized one-attempt delivery phase (never offline).

    One launch, one connection, the staged schedule's 25 exchanges in the
    pinned order, every exchange verified against the accumulated attempt
    state by the production ``cargoflow2_phase_outcome`` (the modeled
    trajectory of record included); the first verification failure halts
    the phase prefix-preservingly, and cleanup is certified before any
    completion verdict can stand.
    """
    directory = prepared.directory
    cargoflow2_preflight(prepared)
    seal = sha256(directory / "PRELAUNCH.json")
    metadata = json.loads((directory / "PRELAUNCH.json").read_text())
    grant = grant_launch(directory, metadata, seal)
    grant.launch_identity = freight_native.launch_critical_identity(prepared, metadata)
    write_json(
        directory / "CLAIM.json",
        dict(
            prelaunch_digest=seal,
            consumed=True,
            launches_allowed=1,
            retries=0,
            authorization_schema=CLAIM_AUTHORIZATION_EVIDENCE_SCHEMA,
            authorization_sha256=grant.authorization_sha256,
            operator_key_identity=grant.operator_key_identity,
        ),
    )
    backend.preflight(prepared)
    schedule: list[dict] = metadata["plan_policy"]["schedule"]
    plan = cargoflow2_pipeline_plan()
    result: dict[str, Any] = dict(
        preflight="PASS",
        native_launches=0,
        connections=0,
        requests=0,
        exchanges=[],
        last_status="NOT_DISPATCHED",
        command_accepted=False,
        state_changed=False,
        verified=False,
        status="FAILED",
        halt=None,
    )
    frames = []
    exchanges: list[tuple[Cargoflow2Request, Cargoflow2Readback]] = []
    state: dict[str, Any] = dict(
        site=None,
        engine=None,
        vehicle=-1,
        # §5.3 dual enforcement: the readback day echoes themselves are the
        # elapsed day ledger, and the arrival anchor bounds every later
        # ladder day exactly.
        day_latest=None,
        elapsed_days=None,
        anchor=None,
    )
    overall_deadline = event_loop_deadline(metadata["budgets"]["total_seconds"])
    try:
        async with asyncio.timeout(metadata["budgets"]["total_seconds"]):
            await backend.launch(prepared, authorization=grant)
            result["native_launches"] = 1
            await wait_log(backend, prepared, CARGOFLOW2_READY_MARKER)
            console(backend, metadata["bootstrap_command"])
            await wait_log(backend, prepared, ROAD_PROOF_COMPANY_READY_MARKER)
            session = await backend.connect(
                prepared, frame_observer=lambda d, f: frames.append((d, f.hex()))
            )
            result["connections"] = 1
            await session.authenticate(metadata["attempt"], "1", timeout=10)
            welcome = session.welcome
            expected = metadata["world"]["expected_welcome"]
            received = None
            if welcome is not None:
                received = tuple(getattr(welcome, field) for field in WELCOME_ORDER)
            wanted = (
                expected["revision"],
                True,
                expected["seed"],
                expected["landscape"],
                expected["start_day"],
                expected["width"],
                expected["height"],
            )
            if session.protocol is None or welcome is None or received != wanted:
                raise ValueError("the retained world identity mismatch")
            write_json(
                directory / "runtime-identity.json",
                dict(
                    auth="X25519_AuthorizedKey",
                    encrypted=session.state is AuthState.ACTIVE,
                    welcome=asdict(welcome),
                    pid=backend.process.pid if backend.process else None,
                ),
            )
            await GameScriptTransport(session, session.protocol).subscribe()
            before_save = await save(backend, prepared, "session-before")
            write_json(directory / "session-before-identity.json", dict(sha256=before_save))
            for entry in schedule:
                label = entry["exchange"]
                try:
                    # §5.3 dual enforcement: the day-authority gate fires
                    # before this exchange's request is ever built or sent —
                    # an exchange whose ladder day cannot fit the remaining
                    # 60-day aggregate authority (or whose anchor is not yet
                    # latched) types the pre-dispatch halt here, with no
                    # bytes on the wire and the typed refusal of record.
                    refusal = _cargoflow2_day_authority(
                        entry,
                        plan,
                        elapsed_days=state["elapsed_days"],
                        anchor=state["anchor"],
                    )
                    if refusal is not None:
                        raise ValueError(refusal)
                    request = _cargoflow2_exchange_request(entry, seal, plan, state)
                    if request.op not in CARGOFLOW2_OPS:
                        raise ValueError("a foreign op cannot enter the delivery run")
                    verify_request_against_cargoflow2_plan(request, plan=plan, seal=seal)
                    readback = await cargoflow2_exchange(
                        session,
                        request,
                        directory,
                        budget_table=metadata["budgets"],
                        overall_deadline=overall_deadline,
                    )
                    result["requests"] += 1
                    probe = cargoflow2_phase_outcome(
                        exchanges + [(request, readback)], prelaunch_digest=seal, plan=plan
                    )
                    if probe["failed"] is not None:
                        raise ValueError(
                            f"the delivery exchange {label} failed verification: "
                            f"{probe['failed']['error']}"
                        )
                    exchanges.append((request, readback))
                    result["exchanges"].append(label)
                    result["last_status"] = readback.status
                    result["command_accepted"] = True
                    result["state_changed"] = True  # the pinned chain mutates
                    if entry["op"] == "purchase":
                        state["vehicle"] = readback.vehicle
                    if entry["op"] == "arrive-watch":
                        if readback.anchor is None:
                            raise ValueError("the anchored arrival lost its ladder anchor")
                        state["anchor"] = int(readback.anchor)
                    if readback.day is not None:
                        day = int(readback.day)
                        if day < int(plan.launch_day):
                            raise ValueError(
                                "the attempt clock read beneath its launch day of record"
                            )
                        if state["day_latest"] is not None and day < int(state["day_latest"]):
                            raise ValueError("the attempt's observation day ledger regressed")
                        state["day_latest"] = day
                        state["elapsed_days"] = day - int(plan.launch_day)
                except Exception as error:
                    result["halt"] = dict(
                        label=label, error=type(error).__name__ + ": " + str(error)
                    )
                    break
            phase = cargoflow2_phase_outcome(exchanges, prelaunch_digest=seal, plan=plan)
            result["phase"] = phase
            if phase["verification"] == "CARGOFLOW2_COMPLETE":
                if len(exchanges) != len(plan.schedule):
                    raise ValueError(
                        "the attempt completion evidence drifted from the staged schedule"
                    )
                if phase["anchor"] is None or not phase["samples"]:
                    raise ValueError(
                        "the native ladder anchor or the sampled series is missing"
                    )
                write_json(
                    directory / "receipt.json",
                    dict(
                        phase,
                        before_save_sha256=before_save,
                    ),
                )
                result["verified"] = True
                result["status"] = "NATIVE_CARGOFLOW2_COMPLETE"
            else:
                result["status"] = "PHASE_HALTED_PREFIX_PRESERVED"
    except Exception as error:
        result["error"] = type(error).__name__ + ": " + str(error)
    finally:
        if result.get("last_status") not in ("NOT_DISPATCHED",):
            try:
                await save(backend, prepared, "after-diagnostic", diagnostic=True)
            except Exception as save_error:
                result["after_save_error"] = type(save_error).__name__ + ": " + str(save_error)
        write_json(directory / "frames.json", frames)
        cleanup = await backend.cleanup(prepared)
        result["returncode"] = cleanup.get("returncode")
        for name in ("stdout.log", "stderr.log"):
            path = prepared.spec.workspace.logs / name
            if path.is_file():
                shutil.copyfile(path, directory / name)
        findings = script_log_health_findings(
            "".join(
                (directory / name).read_text()
                for name in ("stdout.log", "stderr.log")
                if (directory / name).is_file()
            )
        )
        if findings:
            result["script_log_findings"] = findings
            if result["status"] == "NATIVE_CARGOFLOW2_COMPLETE":
                freight_native.deny_verification(
                    result,
                    status="FAILED",
                    message=(
                        "ValueError: the retained script log health findings "
                        "deny the verified attempt completion"
                    ),
                )
        if result["returncode"] not in (None, 0):
            if result["status"] == "NATIVE_CARGOFLOW2_COMPLETE":
                freight_native.deny_verification(
                    result,
                    status="FAILED",
                    message=(
                        "ValueError: the native runtime exited abnormally after "
                        f"the attempt (return code {result['returncode']})"
                    ),
                )
        cleanup_complete = False
        try:
            cleanup.update(verify_cleanup_endpoints(prepared, cleanup))
            prepared.spec.workspace.close()
            cleanup["workspace_disposed"] = not prepared.spec.workspace.root.exists()
            cleanup["credential_removed"] = not prepared.key_path.exists()
            cleanup_complete = bool(
                cleanup.get("reaped") is True
                and not cleanup.get("cleanup_error")
                and cleanup.get("workspace_disposed") is True
                and cleanup.get("credential_removed") is True
            )
            if not cleanup_complete:
                raise ValueError("cleanup incomplete")
        except Exception as error:
            cleanup["verification_error"] = str(error)
            cleanup_complete = False
        apply_cargoflow2_cleanup_outcome(result, complete=cleanup_complete)
        write_json(directory / "cleanup.json", cleanup)
        write_json(directory / "result.json", result)
        (directory / "artifact-manifest.sha256").write_text(manifest(directory))
    return result


# --- Attempt replay verification -----------------------------------------------


def _parse_cargoflow2_frames(directory: Path):
    """Parse the retained frame stream of the owned secure delivery session."""
    frames = json.loads((directory / "frames.json").read_text())
    outbound: list[bytes] = []
    replies: list[bytes] = []
    outbound_requests: list[Cargoflow2Request] = []
    request_positions: dict[bytes, int] = {}
    reply_positions: dict[bytes, int] = {}
    for index, (direction, frame_hex) in enumerate(frames):
        frame = bytes.fromhex(frame_hex)
        if direction == "outbound":
            outbound.append(frame)
            if frame[2] != ADMIN_GAMESCRIPT:
                continue
            payload = decode_cargoflow2_request(frame[3:])
            try:
                query = Cargoflow2Request.model_validate_json(payload)
            except Exception:
                raise ValueError(
                    "an outbound frame contains an invalid Cargoflow2Request"
                ) from None
            outbound_requests.append(query)
            request_positions[payload] = index
        else:
            for kind, body in AdminFrameDecoder().feed_frames(frame):
                if kind != SERVER_GAMESCRIPT:
                    continue
                reply = decode_gamescript(
                    body, max_payload_bytes=MAX_CARGOFLOW2_RESPONSE_BYTES
                )
                if reply not in reply_positions:
                    reply_positions[reply] = index
                replies.append(reply)
    return outbound, outbound_requests, replies, request_positions, reply_positions


def verify_cargoflow2_attempt_identity(metadata: dict, *, plan) -> dict:
    """Re-bind one retained attempt to its pinned prerequisite and plan.

    Replay never trusts the staged record's own declarations: the lineage
    (attempt/schema/prerequisite/world) is re-derived from the module's
    single pinned identity, the pinned depot prerequisite is re-verified,
    and the source-save digest, welcome, schedule, plan digests, op
    surface, ladder grid, funds model and hypotheses are all re-derived. A
    foreign lineage or a drifted pin refuses.
    """
    if metadata.get("attempt") != D5_CARGOFLOW2_ATTEMPT:
        raise ValueError("the retained attempt identity drifted from the staged scope")
    if (
        metadata.get("schema") != D5_CARGOFLOW2_PRELAUNCH_SCHEMA
        or metadata.get("kind") != KIND
        or metadata.get("milestone") != MILESTONE_CARGOFLOW2
    ):
        raise ValueError("the retained attempt is not the D5 cargoflow-2 lineage")
    staged_prerequisite = metadata.get("prerequisite")
    if not isinstance(staged_prerequisite, dict):
        raise ValueError("the retained attempt lacks its prerequisite binding")
    binding = cargoflow2_prerequisite_binding(Path(staged_prerequisite.get("directory", "")))
    expected_prerequisite = dict(
        schema=D5_CARGOFLOW2_PREREQUISITE_SCHEMA,
        attempt=binding["attempt"],
        milestone=binding["milestone"],
        directory=binding["retained_directory"],
        prelaunch_sha256=binding["prelaunch_digest"],
        after_save_sha256=binding["save_sha256"],
        verification=binding["verification"],
    )
    if staged_prerequisite != expected_prerequisite:
        raise ValueError("the retained prerequisite binding drifted from the pinned depot attempt")
    stored_world = metadata.get("world")
    if not isinstance(stored_world, dict):
        raise ValueError("the retained attempt lacks its world binding")
    expected_world_binding = dict(
        retained_directory=binding["retained_directory"],
        source_save=binding["save"],
        save_sha256=binding["save_sha256"],
        qualified_save_sha256=binding.get("qualified_save_sha256"),
    )
    for name, expected in expected_world_binding.items():
        if stored_world.get(name) != expected:
            raise ValueError(f"the retained world {name} drifted from the pinned prerequisite")
    if stored_world.get("save_sha256") != PINNED_PREREQUISITE_AFTER_SAVE:
        raise ValueError("the retained world is not the pinned depot after-save")
    expected_welcome = stored_world.get("expected_welcome")
    if expected_welcome != binding["expected_welcome"]:
        raise ValueError("the retained world welcome drifted from the pinned identity")
    verify_staged_source_save(
        {"save_sha256": binding["save_sha256"]},
        source_save_path(stored_world),
    )
    staged_source = Path(metadata.get("workspace", "")) / "source.sav"
    if staged_source.is_file():
        verify_staged_source_save({"save_sha256": binding["save_sha256"]}, staged_source)
    _require_cargoflow2_plan(plan)
    policy = metadata.get("plan_policy")
    if not isinstance(policy, dict):
        raise ValueError("the retained attempt lacks its plan policy")
    schedule = staged_cargoflow2_schedule(policy)
    if policy.get("schedule") != schedule or policy.get("plan_digest") != plan_digest_of(schedule):
        raise ValueError("the retained attempt schedule drifted from the compiled derivation")
    if policy.get("plan_model_digest") != plan.digest:
        raise ValueError("the retained plan digest drifted from the pinned attempt plan")
    if policy.get("schedule_version") != 1:
        raise ValueError("the retained schedule version drifted")
    if metadata.get("budgets") != cargoflow2_budgets():
        raise ValueError("the retained budget contract drifted")
    if policy.get("max_cost") != int(CARGOFLOW2_ENGINE_MAX_COST):
        raise ValueError("the retained budget floated off the pinned cost authority")
    if policy.get("read_only", {}).get("schema") != CARGOFLOW2_READ_ONLY_SCHEMA:
        raise ValueError("the retained surface schema drifted")
    if policy["read_only"]["permitted_ops"] != list(CARGOFLOW2_OPS):
        raise ValueError("the retained op surface drifted")
    world_pins = policy.get("world")
    if not isinstance(world_pins, dict):
        raise ValueError("the retained plan policy lacks its world pins")
    expected_pins = _cargoflow2_expected_world(plan)
    for name, expected in expected_pins.items():
        if world_pins.get(name) != expected:
            raise ValueError(f"the retained attempt world pin {name} drifted")
    if (
        policy.get("company") != plan.company
        or policy.get("target_tile") != int(CARGOFLOW2_PICKUP_TILE)
        or policy.get("plan_model_digest") != plan.digest
    ):
        raise ValueError("the retained attempt plan pins drifted")
    if policy.get("ladder_grid") != _cargoflow2_ladder_grid():
        raise ValueError("the retained attempt ladder grid drifted from the pinned geometry")
    if policy.get("funds_model") != cargoflow2_funds_model_gate():
        raise ValueError("the retained funds-model pins drifted from the pinned fence")
    if policy.get("observations") != [
        dict(
            industry=int(plan.pickup_industry),
            kind="PRODUCING_PICKUP",
        ),
        dict(
            industry=int(plan.bay_industry),
            kind="ACCEPTING_BAY",
        ),
    ]:
        raise ValueError("the retained attempt observation kinds drifted")
    staged_hypotheses = policy.get("hypotheses")
    expected_hypotheses = cargoflow2_hypotheses()
    if (
        not isinstance(staged_hypotheses, dict)
        or staged_hypotheses.get("state") != expected_hypotheses.get("state")
    ):
        raise ValueError(
            f"the retained attempt hypothesis record drifted from its version derivation "
            f"({expected_hypotheses.get('state')})"
        )
    return binding


def verify_cargoflow2_attempt(directory: Path) -> dict:
    """Replay the retained protocol-11 phase; never trust a success label.

    The replay re-derives every retained fact independently — operator
    authorization evidence, the staged attempt schedule, the captured
    session frames, every per-exchange request/response pair — then
    re-verifies the whole attempt with the production
    :func:`app.simulation.openttd.corridor_cargoflow2.cargoflow2_phase_outcome`
    and the certified-cleanup gate. A forced or invented
    ``CARGOFLOW2_COMPLETE`` label alone can never verify; a refused,
    missing, malformed, out-of-order, stale, divergent or inconclusive
    exchange always leaves the verdict incomplete.
    """
    directory = directory.resolve()
    metadata = read_prelaunch(directory)
    seal = sha256(directory / "PRELAUNCH.json")
    claims_path = directory / "CLAIM.json"
    if not claims_path.is_file():
        return dict(
            verification="AUTHORIZATION_UNVERIFIED",
            authorization_state="CLAIM_ABSENT",
            statement=(
                "the attempt candidate was never consumed by an operator "
                "authorization; no verified completion is possible"
            ),
        )
    claims = json.loads(claims_path.read_text())
    if claims.get("prelaunch_digest") != seal:
        raise ValueError("the attempt claim does not match its prelaunch seal")
    manifest_names: set[str] = set()
    for line in (directory / "artifact-manifest.sha256").read_text().splitlines():
        digest, name = line.split("  ", 1)
        if Path(name).name != name or not (directory / name).is_file():
            raise ValueError("the artifact manifest mismatch")
        if sha256(directory / name) != digest:
            raise ValueError("the artifact manifest mismatch")
        manifest_names.add(name)
    present_names = {
        path.name
        for path in directory.iterdir()
        if path.is_file() and path.name != "artifact-manifest.sha256"
    }
    if present_names != manifest_names:
        raise ValueError("the artifact manifest is not exhaustive")
    if metadata.get("schema") != D5_CARGOFLOW2_PRELAUNCH_SCHEMA:
        return dict(
            verification="AUTHORIZATION_UNVERIFIED",
            authorization_state="UNKNOWN_PRELAUNCH_SCHEMA",
            statement=(
                f"the prelaunch record is not the launch-capable "
                f"[{D5_CARGOFLOW2_PRELAUNCH_SCHEMA!r}] lineage; no verified "
                "completion is possible"
            ),
        )
    authorization_state = replay_authorization_state(directory, metadata, seal, claims)
    if authorization_state is not None:
        return dict(
            verification="AUTHORIZATION_UNVERIFIED",
            authorization_state=authorization_state,
            statement=(
                "the retained authorization evidence does not match the "
                "operator-verified record; no verified completion is possible"
            ),
        )
    policy_replay = metadata["plan_policy"]
    schedule = staged_cargoflow2_schedule(policy_replay)
    plan = cargoflow2_pipeline_plan()
    if policy_replay["schedule"] != schedule or policy_replay["plan_digest"] != plan_digest_of(
        schedule
    ):
        raise ValueError("the staged attempt schedule drifted from the compiled derivation")
    planned_ids = {row["exchange"] for row in schedule}
    if planned_ids != set(CARGOFLOW2_EXCHANGE_IDS) or len(schedule) != PLANNED_CARGOFLOW2_EXCHANGES:
        raise ValueError("the retained attempt schedule drifted from the wire contract")
    verify_cargoflow2_attempt_identity(metadata, plan=plan)
    result = json.loads((directory / "result.json").read_text())
    runtime = json.loads((directory / "runtime-identity.json").read_text())
    expected_welcome = metadata["world"]["expected_welcome"]
    welcome = runtime.get("welcome")
    if runtime.get("encrypted") is not True or not isinstance(welcome, dict):
        raise ValueError("the owned single-runtime encrypted execution evidence missing")
    for field in WELCOME_ORDER:
        expected = True if field == "dedicated" else expected_welcome[field]
        if welcome.get(field) != expected:
            raise ValueError(f"the retained world welcome {field} drifted")
    outbound, outbound_requests, replies, request_positions, reply_positions = (
        _parse_cargoflow2_frames(directory)
    )
    if len(outbound_requests) > metadata["budgets"]["requests"]:
        raise ValueError("the attempt request budget exceeded (outbound frames)")
    paths = sorted(directory.glob("*-request.json"))
    file_queries = [Cargoflow2Request.model_validate_json(path.read_bytes()) for path in paths]
    for path, query in zip(paths, file_queries, strict=True):
        if query.request_id != path.name[: -len("-request.json")]:
            raise ValueError("the retained request file identity does not match its payload")
    if len(outbound_requests) < len(file_queries):
        return dict(
            verification="UNRESOLVED_ATTEMPT_EVIDENCE_PRESERVED",
            exchanges=result.get("exchanges", []),
            state_changed=result.get("state_changed", False),
            result_status=result.get("status", "UNKNOWN"),
            statement="an incomplete retained exchange (fewer outbound frames); no completion claimed",  # noqa: E501
        )
    if len(outbound_requests) > len(file_queries):
        raise ValueError("the outbound frame count exceeds the request file count (tampering)")
    if sorted(q.to_bytes() for q in outbound_requests) != sorted(
        q.to_bytes() for q in file_queries
    ):
        raise ValueError("the outbound frame payloads do not match request file payloads")
    unknown = {q.request_id for q in file_queries} - planned_ids
    if unknown:
        raise ValueError(f"the request identity is outside the staged schedule: {sorted(unknown)}")
    seen_ids: set[str] = set()
    for query in outbound_requests:
        if query.request_id in seen_ids:
            raise ValueError(f"a duplicate delivery request_id: {query.request_id}")
        seen_ids.add(query.request_id)
    response_map = {}
    for path in paths:
        response_path = path.with_name(path.name.replace("-request.json", "-response.json"))
        if response_path.is_file():
            response_map[path.read_bytes()] = response_path.read_bytes()
    for path in sorted(directory.glob("*-response.json")):
        exchange_id = path.name[: -len("-response.json")]
        try:
            readback = Cargoflow2Readback.model_validate_json(path.read_bytes())
        except ValueError as error:
            raise ValueError(
                f"the retained response file is not a parseable readback: {path.name}"
            ) from error
        if readback.request_id != exchange_id:
            raise ValueError("the retained response file identity does not match its payload")
        if not (directory / (exchange_id + "-request.json")).is_file():
            raise ValueError("the retained response file lacks its request")
    for raw, response in response_map.items():
        if outbound.count(encode_cargoflow2_request(raw)) != 1 or replies.count(response) != 1:
            raise ValueError("the retained exchange lacks unique secure-session frame evidence")
    retained_responses = set(response_map.values())
    for reply in replies:
        if reply not in retained_responses:
            raise ValueError("the retained gateway response lacks its durable response file")
    for raw, response in response_map.items():
        if reply_positions[response] < request_positions[raw]:
            raise ValueError("a retained response precedes its own request in the frame stream")

    halted_position = None
    halt_record = result.get("halt")
    exchanges: list[tuple[Cargoflow2Request, Cargoflow2Readback]] = []
    for position, entry in enumerate(schedule):
        label = entry["exchange"]
        if (
            halted_position is None
            and isinstance(halt_record, dict)
            and (halt_record.get("label") == label)
        ):
            halted_position = position
        pending = halted_position is not None and position > halted_position
        if not pending:
            request_path = directory / (label + "-request.json")
            if not request_path.is_file():
                continue
            query = Cargoflow2Request.model_validate_json(request_path.read_bytes())
            raw = response_map.get(query.to_bytes())
            if raw is not None:
                exchanges.append((query, Cargoflow2Readback.parse_for(query, raw)))
        if pending:
            break
    phase = cargoflow2_phase_outcome(exchanges, prelaunch_digest=seal, plan=plan)
    cleanup_record = json.loads((directory / "cleanup.json").read_text())
    exit_codes = (result.get("returncode"), cleanup_record.get("returncode"))
    cleanup_complete = (
        all(
            cleanup_record.get(name) is True
            for name in ("reaped", "sockets_closed", "workspace_disposed", "credential_removed")
        )
        and not bool(cleanup_record.get("cleanup_error"))
        and not bool(cleanup_record.get("verification_error"))
    )
    if any(code not in (None, 0) for code in exit_codes):
        return dict(
            verification="ATTEMPT_FAILED_EVIDENCE_PRESERVED",
            result_status=result.get("status", "UNKNOWN"),
            error=result.get("error", "the process exited abnormally"),
            exit_evidence=dict(returncode=exit_codes[0], cleanup_returncode=exit_codes[1]),
        )
    if result["status"] == "NATIVE_CARGOFLOW2_COMPLETE":
        if phase["verification"] != "CARGOFLOW2_COMPLETE":
            raise ValueError("the verified completion contradicts its attempt phase outcome")
        if result.get("halt") is not None or not result.get("command_accepted"):
            raise ValueError("the verified completion contradicts its retained attempt record")
        if result.get("state_changed") is not True:
            raise ValueError("the verified completion contradicts its world-mutation evidence")
        if (result.get("native_launches"), result.get("connections")) != (
            metadata["budgets"]["launches"],
            metadata["budgets"]["connection_attempts"],
        ):
            raise ValueError("the verified completion contradicts its launch seal")
        if len(result.get("exchanges", [])) != len(plan.schedule) or not cleanup_complete:
            raise ValueError("the verified completion's cleanup or exchange inventory incomplete")
        if len(outbound_requests) != len(plan.schedule):
            raise ValueError("the verified completion's request inventory drifted")
        if phase["anchor"] is None or not phase["samples"]:
            raise ValueError("the verified completion lacks its own re-derived ladder evidence")
        if sorted(int(offset) for offset in phase["samples"]) != list(CARGOFLOW2_FLOW_OFFSETS):
            raise ValueError("the verified completion's sampled ladder inventory drifted")
        if result.get("cleanup_failure") is not None or result.get("verified") is not True:
            raise ValueError("the verified completion label contradicts its own result flags")
        receipt_path = directory / "receipt.json"
        if receipt_path.is_file():
            retained_receipt = json.loads(receipt_path.read_text())
            replay_phase = json.loads(json.dumps(phase)) if phase is not None else None
            # The run writes the phase fields flat together with its
            # before-save digest; the replay must read exactly that shape
            # and shrink nothing.
            if any(
                name not in retained_receipt or retained_receipt[name] != replay_phase[name]
                for name in replay_phase
            ):
                raise ValueError("the retained attempt receipt replay mismatch")
            session_before = json.loads(
                (directory / "session-before-identity.json").read_text()
            ).get("sha256")
            if retained_receipt.get("before_save_sha256") != session_before:
                raise ValueError("the retained attempt receipt replay mismatch")
        return dict(
            verification="CARGOFLOW2_COMPLETION_VERIFIED",
            receipt=dict(
                phase=json.loads(json.dumps(phase)),
                before_save_sha256=json.loads(
                    (directory / "session-before-identity.json").read_text()
                ).get("sha256"),
            ),
        )
    if result["status"] == "FAILED_CLEANUP":
        return dict(
            verification="ATTEMPT_FAILED_EVIDENCE_PRESERVED",
            result_status="FAILED_CLEANUP",
            exchanges=result.get("exchanges", []),
            error=result.get("error") or "cleanup was not certified",
            cleanup_complete=False,
            cleanup_error=cleanup_record.get("cleanup_error"),
            cleanup_verification_error=cleanup_record.get("verification_error"),
        )
    if result["status"] in ("PHASE_HALTED_PREFIX_PRESERVED", "FAILED"):
        if result["status"] == "PHASE_HALTED_PREFIX_PRESERVED" and (
            phase["verification"] != "CARGOFLOW2_INCOMPLETE"
            or not isinstance(halt_record, dict)
            or len(result.get("exchanges", [])) != len(phase["receipts"])
            or (
                phase["failed"] is not None
                and phase["failed"].get("label") != halt_record.get("label")
            )
        ):
            raise ValueError("the halted attempt evidence contradicts its retained record")
        if not cleanup_complete:
            raise ValueError("the halted attempt cleanup incomplete")
        return dict(
            verification=(
                "PHASE_HALTED_EVIDENCE_PRESERVED"
                if result["status"] == "PHASE_HALTED_PREFIX_PRESERVED"
                else "ATTEMPT_FAILED_EVIDENCE_PRESERVED"
            ),
            result_status=result["status"],
            exchanges=result.get("exchanges", []),
            failed=phase["failed"],
            pending=phase["pending"],
            error=result.get("error") or (phase["failed"] or {}).get("error"),
        )
    return dict(
        verification="ATTEMPT_FAILED_EVIDENCE_PRESERVED",
        result_status=result.get("status", "UNKNOWN"),
        error=result.get("error"),
    )


def staged_cargoflow2_authorization_payload_digest(directory: Path) -> str:
    """The RFC-canonical digest of the candidate's own authorization payload."""
    directory = directory.resolve()
    metadata = read_prelaunch(directory)
    seal = sha256(directory / "PRELAUNCH.json")
    return hashlib.sha256(
        canonical_authorization_bytes(authorization_payload(metadata, seal))
    ).hexdigest()


def cargoflow2_exit_status(result: dict) -> int:
    verified = (
        result.get("verified") is True
        and result.get("status") == "NATIVE_CARGOFLOW2_COMPLETE"
        and result.get("cleanup_complete") is True
        and result.get("state_changed") is True
    )
    return 0 if verified else 1


def cargoflow2_verdict_exit_status(verdict: dict) -> int:
    return 0 if verdict.get("verification") == "CARGOFLOW2_COMPLETION_VERIFIED" else 1


def _argument_parser() -> argparse.ArgumentParser:
    """The module CLI of record (mirrored subcommands and flags)."""
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("prepare", "preflight", "run", "verify"))
    parser.add_argument("directory", type=Path)
    parser.add_argument("--prerequisite", type=Path, default=PINNED_PREREQUISITE)
    return parser


def main():
    parser = _argument_parser()
    args = parser.parse_args()
    directory = args.directory.resolve()
    if args.command == "prepare":
        prepared = prepare_cargoflow2_candidate(directory, prerequisite=args.prerequisite)
        cargoflow2_preflight(prepared)
        print("PRELAUNCH PASS", directory)
    elif args.command == "preflight":
        cargoflow2_preflight(freight_native.reopen_candidate(directory))
        print("PREFLIGHT PASS")
    elif args.command == "verify":
        verdict = verify_cargoflow2_attempt(directory)
        print(json.dumps(verdict, sort_keys=True))
        raise SystemExit(cargoflow2_verdict_exit_status(verdict))
    else:
        read_prelaunch(directory)  # fail fast on any drifted prelaunch record
        result = asyncio.run(
            execute_cargoflow2_attempt(
                freight_native.reopen_candidate(directory),
                Cargoflow2NativeBackend(authorized_one_launch=True),
            )
        )
        print(json.dumps(result, sort_keys=True))
        raise SystemExit(cargoflow2_exit_status(result))


if __name__ == "__main__":
    main()
