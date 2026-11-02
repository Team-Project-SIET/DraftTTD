"""D5 native corridor freight-cycle proof preparation, protocol 8 (freight v2).

Stages the reviewed freight-delivery v2 cycle as one fresh save-load candidate
that reuses the proven D2/D3/D4/D5 native machinery exactly: the same operator
authorization, runtime freeze, dependency identity, immutable launch
environment, one-shot claim, signed replay and cleanup boundaries. No second
security framework is introduced; the shared machinery is parameterized at
call time (closure root, prerequisite lineage, sealed freight pins) so the
consumed v1 freight ceremony is untouched.

The staged candidate ``D5-FREIGHT-3`` binds the A1 close-out lineage
byte-exactly:

1. Its source world is the replay-verified retained ``after.sav`` of the
   consumed A1 corridor-extension candidate (``D5-CORRIDOR-EXTENSION-3``) —
   the route-receipt bound new delivery bay, corridor stops, depot and
   company road at the verified extension close-out, with the pinned
   authoritative after-save digest.
2. Its vehicle route is derived from the actual pinned 31-tile construction
   witness (the A1 extension's built route): the ordered 29-tile subsequence
   that removes the stale D4 delivery bay and the backtracked repeat of its
   front tile. The route is never hand-invented; witness and route digests
   are two separate bindings of record.
3. Its schedule is the fixed thirty-exchange cycle-looped plan the wire
   contract pins (ten fixed exchanges, six load/transit/deliver cycles, a
   finance corroboration and a finish).
4. Wire contract v8 (``app.simulation.openttd.corridor_freight_v2``): every
   exchange presents one uniform prelaunch plan digest; per-op admission
   intents (site, engine) and per-op receipts are latched between exchanges
   and verified by the production freight v2 verifiers — one attempt, one
   company, one vehicle, one purchase.

Native buildability is never inferred here: site facts, the F-3 unique
industry discoveries, the pinned-engine census admission, the tested quote,
the funds reconciliation, monitor arithmetic and the finance corroboration
happen natively at admission/exchange time through
``app.simulation.openttd.corridor_freight_v2``.

Nothing in this module launches OpenTTD, connects to any port, or mutates
any tile; the staged pre-launch claim is never written, so nothing can
launch until a separate operator authorization creates it.
"""

import argparse
import asyncio
import json
import os
import re
import shutil
import struct
import time
import zipfile
from dataclasses import asdict
from functools import lru_cache
from pathlib import Path
from typing import Any

from app.simulation.openttd.admin_crypto import AuthorizedKey
from app.simulation.openttd.admin_protocol import AdminFrameDecoder, encode_admin_quit
from app.simulation.openttd.corridor_freight_v2 import (
    A1_AFTER_SAVE_SHA256_V2,
    A1_DELIVERY_FRONT_TILE_V2,
    A1_DELIVERY_STOP_TILE_V2,
    A1_DEPOT_FRONT_TILE_V2,
    A1_DEPOT_TILE_V2,
    A1_PICKUP_FRONT_TILE_V2,
    A1_PICKUP_STOP_TILE_V2,
    ENGINE_CENSUS_V2,
    ENGINE_PIN_PROVISIONAL_V2,
    ENGINE_PIN_V2,
    FREIGHT_ATTEMPT_V2,
    FREIGHT_CARGO_ID,
    FREIGHT_COMPANY,
    FREIGHT_CYCLE_DAY_CAP_V2,
    FREIGHT_CYCLE_WALL_CAP_SECONDS_V2,
    FREIGHT_DAY_BUDGET_V2,
    FREIGHT_EXCHANGE_IDS_V2,
    FREIGHT_MAX_COST_V2,
    FREIGHT_OPS_V2,
    FREIGHT_REQUEST_BUDGET_V2,
    FREIGHT_ROUTE_LENGTH_V2,
    FREIGHT_ROUTE_V2,
    FREIGHT_RUNNING_COST_ALLOWANCE_V2,
    FREIGHT_SCHEDULE_VERSION,
    FREIGHT_STALE_BACKTRACK_TILE_V2,
    FREIGHT_STALE_DELIVERY_TILE_V2,
    FREIGHT_WITNESS_LENGTH_V2,
    FUNDS_AT_A1_CLOSE,
    MAX_FREIGHT_REQUEST_BYTES_V2,
    MAX_FREIGHT_RESPONSE_BYTES_V2,
    MAX_FREIGHT_SEND_BYTES,
    PINNED_WITNESS,
    PLANNED_FREIGHT_CYCLES_V2,
    PLANNED_FREIGHT_EXCHANGES_V2,
    WATCH_MAX_TICKS_V2,
    FreightPlanV2,
    FreightReadbackV2,
    FreightRequestV2,
    admit_freight_engine_v2,
    admit_freight_site_v2,
    freight_exchange_cycle_index_v2,
    freight_exchange_sequence_v2,
    freight_phase_outcome_v2,
    freight_window_dispatch_refusal_v2,
    verify_freight_attempt_v2,
)
from app.simulation.openttd.gamescript_transport import (
    ADMIN_GAMESCRIPT,
    SERVER_GAMESCRIPT,
    GameScriptTransport,
    decode_gamescript,
    encode_gamescript,
    gamescript_subscription,
)
from app.simulation.openttd.proof.classification_capture import script_log_health_findings
from app.simulation.openttd.proof.corridor_accept_survey_native import (
    A1_PREREQUISITE_ATTEMPT,
    A1_PREREQUISITE_MILESTONE,
    PINNED_PREREQUISITE,
    PINNED_PREREQUISITE_AFTER_SAVE,
)
from app.simulation.openttd.proof.corridor_construction_native import (
    source_save_path,
    stage_world,
)
from app.simulation.openttd.proof.corridor_extension_native import (
    ACCEPTANCE_RECHECK_STATEMENT,
    D5_EXTENSION_PRELAUNCH_SCHEMA,
    verify_extension_attempt,
)
from app.simulation.openttd.proof.corridor_extension_native import (
    KIND as EXTENSION_KIND,
)
from app.simulation.openttd.proof.corridor_freight_native import (
    D5_FREIGHT_LAUNCH_CONSUMED_SCHEMA,
    D5_FREIGHT_PREREQUISITE_SCHEMA,
    FREIGHT_EXCHANGE_MARGIN_SECONDS,
    FREIGHT_WATCH_WALL_SECONDS,
    apply_cleanup_outcome,
    deny_verification,
    event_loop_deadline,
    exit_status,
    verdict_exit_status,
)
from app.simulation.openttd.proof.endpoints import kernel_socket_rows, verify_cleanup_endpoints
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
    grant_launch,
)
from app.simulation.openttd.proof.road_mutation import console, save, wait_log
from app.simulation.openttd.proof.terrain_classification_preparation import SEED17_RUN
from app.simulation.openttd.proof.terrain_clearing import (
    STAGED_AI_DIRECTORY,
    WELCOME_ORDER,
    ClearingNativeBackend,
    ClearingStagingError,
    d2_dependency_inventory,
    d2_source_closure,
    launch_critical_identity,
    launch_environment,
    replay_authorization_state,
    require_frozen_d2_closure,
    require_frozen_d2_dependencies,
    retained_welcome,
)
from app.simulation.openttd.proof.terrain_clearing import (
    reopen as reopen_candidate,
)
from app.simulation.openttd.proof.terrain_terraform_native import (
    ROAD_PROOF_COMPANY_READY_MARKER,
    plan_digest_of,
    read_prelaunch,
)
from app.simulation.openttd.proof.world_correspondence import (
    SOURCE_SAVE_GS_NAME,
    verify_staged_source_save,
)
from app.simulation.openttd.runtime.base import LaunchSpecification
from app.simulation.openttd.runtime.config import AdminSettings, RuntimeWorkspace
from app.simulation.openttd.runtime.identity import RuntimeIdentity
from app.simulation.openttd.secure_admin import AuthState, SecureAdminSession

PACKAGES = Path(__file__).resolve().parents[1]
FREIGHT_V2_PACKAGE = PACKAGES / "d5_freight_v2_package"
AI_PACKAGE = PACKAGES / "road_company_package"
D5_V2_CLOSURE_ROOT = "app.simulation.openttd.proof.corridor_freight_v2_native"

KIND = "freight"
MILESTONE_FREIGHT = "D5-FREIGHT"
FREIGHT_ATTEMPT = FREIGHT_ATTEMPT_V2

# Versioned prelaunch evidence for the freight v2 candidate (additive sister
# record of the shared prelaunch machinery; the claim, launch boundary, freeze
# and replay gates are the shared D2 implementations parameterized at call
# time). The prerequisite schema stays the shared native family the v1 freight
# candidate binds; the consumed-launch marker stays the shared native family.
D5_FREIGHT_V2_PRELAUNCH_SCHEMA = "d5-freight2-prelaunch-v1"
D5_FREIGHT_V2_PREREQUISITE_SCHEMA = D5_FREIGHT_PREREQUISITE_SCHEMA
D5_FREIGHT_V2_LAUNCH_CONSUMED_SCHEMA = D5_FREIGHT_LAUNCH_CONSUMED_SCHEMA

# The freight v2 candidate's prerequisite lineage: the consumed A1 corridor
# extension attempt whose replay-verified retained after.sav is the staged
# source world. Pins are absolute: the binding and staging guards compare a
# ``.resolve()``ed prerequisite against them, so a relative constant can
# never equal its own resolved prerequisite.
if PINNED_PREREQUISITE_AFTER_SAVE != A1_AFTER_SAVE_SHA256_V2:
    raise RuntimeError("the A1 prerequisite after-save digest drifted from the v2 pin")

# The staged running GameScript announces its own readiness marker (identical
# to the D2/D3/D4 staged machinery).
FREIGHT_V2_READY_MARKER = "D5_V2_READY"

# Schedule-derivation version of the staged freight plan. Version 2 is the
# thirty-exchange cycle-looped derivation the wire contract pins exactly.
SCHEDULE_VERSION = FREIGHT_SCHEDULE_VERSION

# Exchange accounting: the thirty planned cycles+scheduling and the package's
# own dispatcher request cap of 32 unique ids.
PLANNED_FREIGHT_REQUESTS = PLANNED_FREIGHT_EXCHANGES_V2
FREIGHT_STAGED_REQUESTS_BUDGET = FREIGHT_REQUEST_BUDGET_V2

# Protocol-8 timing contract. A non-window exchange is a bounded request /
# immediate readback and uses the staged ``request_seconds``. A watch-window
# exchange is permitted the design's full wall-clock window plus a small
# client margin, because the GameScript may legitimately spend the whole
# window before returning its bounded observation. Every exchange is further
# clamped to the remaining overall attempt budget, so thirty fresh windows
# can never extend the attempt beyond its total wall clock.
FREIGHT_WATCH_OPS = ("load-watch", "transit-watch", "deliver-watch")


class FreightV2StagingError(ClearingStagingError):
    """Offline freight-v2 staging or pin derivation failed; nothing launched."""


def staged_composition() -> tuple[dict[str, bytes], str, int]:
    """Byte-exact save-restore composition for the freight v2 candidate.

    The retained staged ``info.nut`` announces the save's stored GameScript
    identity (name/version); the staged main is the bounded v2 freight
    handler with the save-restore bridge class defined inline after the
    proof class. No separate identity.nut is needed.
    """
    with zipfile.ZipFile(SEED17_RUN / "frozen-source.zip") as archive:
        info_bytes = archive.read("staged/info.nut")
    text = info_bytes.decode()
    create_instance = re.search(r'CreateInstance\(\)\s*\{\s*return\s+"([^"]+)"', text)
    version = re.search(r"GetVersion\(\)\s*\{\s*return\s+(\d+)", text)
    if create_instance is None or version is None or SOURCE_SAVE_GS_NAME not in text:
        raise FreightV2StagingError("retained staged GameScript identity incomplete")
    main_text = (FREIGHT_V2_PACKAGE / "main.nut").read_text()
    bridge_class = create_instance.group(1)
    if f"class {bridge_class} extends D5FreightV2Proof" not in main_text:
        raise FreightV2StagingError(
            f"staged v2 main.nut missing required bridge class {bridge_class}"
        )
    return (
        {
            "info.nut": info_bytes,
            "main.nut": (FREIGHT_V2_PACKAGE / "main.nut").read_bytes(),
        },
        bridge_class,
        int(version.group(1)),
    )


# --- The pinned A1 close-out freight world (sealed, deterministic) ------------


@lru_cache(maxsize=1)
def freight_facts() -> dict:
    """Derive the staged freight v2 world's pins from the pinned A1 close-out.

    The prerequisite must be the replay-verified consumed A1 corridor
    extension attempt (``D5-CORRIDOR-EXTENSION-2`` succeeded nothing; the
    extension attempt of record is ``D5-CORRIDOR-EXTENSION-3``): its
    receipt-bound ``after.sav`` is the authoritative source world, its
    route receipt names the A1 close-out funds exactly, and its station
    receipt proves the new delivery bay is a distinct station beside the
    retained corridor stops. Every freight v2 world pin is compared with
    the compiled A1 evidence here, so a drift refuses staging before any
    run.
    """
    prerequisite = PINNED_PREREQUISITE
    metadata = read_prelaunch(prerequisite)
    if metadata.get("schema") != D5_EXTENSION_PRELAUNCH_SCHEMA:
        raise FreightV2StagingError("the A1 prerequisite is not the extension lineage")
    if metadata.get("kind") != EXTENSION_KIND or metadata.get("attempt") != (
        A1_PREREQUISITE_ATTEMPT
    ):
        raise FreightV2StagingError(
            "the A1 prerequisite attempt identity drifted from the extension of record"
        )
    seal = sha256(prerequisite / "PRELAUNCH.json")
    if (prerequisite / "PRELAUNCH.sha256").read_text().strip() != seal:
        raise FreightV2StagingError("A1 prerequisite prelaunch seal mismatch")
    claim_path = prerequisite / "CLAIM.json"
    if not claim_path.is_file():
        raise FreightV2StagingError("the A1 prerequisite attempt was never consumed")
    claim = json.loads(claim_path.read_text())
    if claim.get("prelaunch_digest") != seal or claim.get("consumed") is not True:
        raise FreightV2StagingError("the A1 prerequisite attempt claim is incomplete")
    after_save = prerequisite / "after.sav"
    if not after_save.is_file():
        raise FreightV2StagingError("the A1 prerequisite attempt retained no after world")
    after_digest = sha256(after_save)
    if after_digest != PINNED_PREREQUISITE_AFTER_SAVE or after_digest != (
        A1_AFTER_SAVE_SHA256_V2
    ):
        raise FreightV2StagingError(
            "the A1 prerequisite after-save digest is not the pinned authoritative world"
        )
    receipt_path = prerequisite / "receipt.json"
    if not receipt_path.is_file():
        raise FreightV2StagingError("the A1 prerequisite attempt retained no receipt")
    receipt = json.loads(receipt_path.read_text())
    if receipt.get("after_save_sha256") != after_digest:
        raise FreightV2StagingError("the A1 receipt does not bind its after save")
    if receipt.get("acceptance_recheck") != ACCEPTANCE_RECHECK_STATEMENT:
        raise FreightV2StagingError("the A1 acceptance-recheck requirement drifted")
    station_receipt = receipt.get("station_receipt")
    if not isinstance(station_receipt, dict) or station_receipt.get("verdict") != (
        "DISTINCT_NEW_STATION"
    ):
        raise FreightV2StagingError("the A1 station receipt is not a distinct new station")
    if station_receipt.get("existing_sids") != [0, 1] or station_receipt.get(
        "route_delivery_sid"
    ) != 2:
        raise FreightV2StagingError("the A1 station receipt drifts from the corridor ids")
    route_receipt = receipt.get("route")
    if not isinstance(route_receipt, dict) or int(route_receipt.get("funds", -1)) != (
        FUNDS_AT_A1_CLOSE
    ):
        raise FreightV2StagingError("the A1 route funds drifted from the close-out pin")
    verdict = verify_extension_attempt(prerequisite)
    if verdict.get("verification") != "EXTENSION_COMPLETION_VERIFIED":
        raise FreightV2StagingError(
            "the A1 prerequisite replay is not a verified extension completion: "
            f"{verdict.get('verification')}"
        )
    design_pins = metadata.get("design_pins")
    if not isinstance(design_pins, dict) or [int(tile) for tile in design_pins["witness"]] != (
        list(PINNED_WITNESS)
    ):
        raise FreightV2StagingError(
            "the A1 design witness drifted from the pinned construction witness"
        )
    if len(PINNED_WITNESS) != FREIGHT_WITNESS_LENGTH_V2 or len(FREIGHT_ROUTE_V2) != (
        FREIGHT_ROUTE_LENGTH_V2
    ):
        raise FreightV2StagingError("the pinned witness/route lengths drifted")
    if (PINNED_WITNESS[23], PINNED_WITNESS[24]) != (
        FREIGHT_STALE_DELIVERY_TILE_V2,
        FREIGHT_STALE_BACKTRACK_TILE_V2,
    ):
        raise FreightV2StagingError("the pinned witness did not backtrack the stale bay")
    expected_welcome = metadata["world"]["expected_welcome"]
    if expected_welcome != retained_welcome():
        raise FreightV2StagingError("the A1 welcome is not the retained world identity")
    return dict(
        attempt=A1_PREREQUISITE_ATTEMPT,
        milestone=A1_PREREQUISITE_MILESTONE,
        directory=str(prerequisite),
        prelaunch_digest=seal,
        save="after.sav",
        save_sha256=after_digest,
        qualified_save_sha256=metadata["world"].get("qualified_save_sha256"),
        station_sids=dict(existing=list(station_receipt["existing_sids"]), new=2),
        funds=FUNDS_AT_A1_CLOSE,
        expected_welcome=expected_welcome,
    )


def freight_plan_v2() -> FreightPlanV2:
    """The staged freight v2 plan the A1 close-out candidate drives.

    The plan derives entirely from the module's own pins of record: the
    pinned witness and its derived vehicle route, the A1 corridor stops,
    depot and funds, and the provisional census engine pin. The industry
    ids are never pinned (F-3); no optimizer is re-run — the extension
    construction already proved the geometry, so the witness derivation is
    the route authority of record.
    """
    return FreightPlanV2(
        attempt=FREIGHT_ATTEMPT_V2,
        company=FREIGHT_COMPANY,
        cargo=FREIGHT_CARGO_ID,
        engine=ENGINE_PIN_V2,
        pickup=A1_PICKUP_STOP_TILE_V2,
        pickup_front=A1_PICKUP_FRONT_TILE_V2,
        delivery=A1_DELIVERY_STOP_TILE_V2,
        delivery_front=A1_DELIVERY_FRONT_TILE_V2,
        depot=A1_DEPOT_TILE_V2,
        depot_front=A1_DEPOT_FRONT_TILE_V2,
        pickup_industry=-1,
        delivery_industry=-1,
        expected_funds=FUNDS_AT_A1_CLOSE,
        max_cost=FREIGHT_MAX_COST_V2,
        witness=PINNED_WITNESS,
        vehicle_route=FREIGHT_ROUTE_V2,
        schedule=FREIGHT_EXCHANGE_IDS_V2,
        cycles=PLANNED_FREIGHT_CYCLES_V2,
        day_budget=FREIGHT_DAY_BUDGET_V2,
        cycle_day_cap=FREIGHT_CYCLE_DAY_CAP_V2,
    )


def freight_schedule() -> list[dict]:
    """The fixed thirty-exchange freight v2 cycle, staged as plan rows.

    Each row carries the exchange id, its op, and the phase-budget echoes
    the windows present (bounded by the wire contract's own caps); order
    rows carry their stop index; E53 gives every watch window the same
    per-cap economy-day lease, and the wire contract's aggregate authority
    gate owns the 60-day budget arithmetic across them. A drift from the
    wire contract's own schedule refuses staging.
    """
    schedule: list[dict] = []
    for exchange_id, op in freight_exchange_sequence_v2(PLANNED_FREIGHT_CYCLES_V2):
        row: dict = dict(exchange=exchange_id, op=op)
        if op == "order":
            row["order_index"] = int(exchange_id.rsplit("-", 1)[-1])
        elif op == "load-watch":
            row["watch_ticks"] = WATCH_MAX_TICKS_V2
            row["watch_days"] = FREIGHT_CYCLE_DAY_CAP_V2
        elif op in ("transit-watch", "deliver-watch"):
            row["watch_ticks"] = WATCH_MAX_TICKS_V2
            row["watch_days"] = FREIGHT_CYCLE_DAY_CAP_V2
        schedule.append(row)
    if [entry["exchange"] for entry in schedule] != list(FREIGHT_EXCHANGE_IDS_V2):
        raise FreightV2StagingError("the staged freight v2 schedule drifted from the contract")
    return schedule


def _scheduled_exchange_ids(schedule: list[dict]) -> set[str]:
    """Every request id the staged schedule can legitimately produce."""
    ids = {entry["exchange"] for entry in schedule}
    if ids != set(FREIGHT_EXCHANGE_IDS_V2):
        raise FreightV2StagingError("the staged freight v2 schedule drifted from the contract")
    return ids


# --- Prerequisite-attempt source world (A1 extension candidate-3) --------------


def prerequisite_binding(prerequisite: Path = PINNED_PREREQUISITE) -> dict:
    """The fail-closed binding of the A1 extension attempt's after-save.

    The prerequisite must be the pinned, consumed, fully replay-verified A1
    corridor-extension attempt of record: its prelaunch seal integrity, its
    consumed one-shot claim, its retained ``after.sav`` at the pinned
    authoritative digest, its receipt binding the save with the acceptance
    recheck and the distinct-new-station verdict, its full extension replay
    verdict and the retained world welcome. The A1 lineage record is
    embedded as provenance; no historical D3/D4 chain walk is re-opened.
    """
    prerequisite = Path(prerequisite).resolve()
    if prerequisite != PINNED_PREREQUISITE:
        raise FreightV2StagingError("the staged world requires the pinned A1 prerequisite")
    if not prerequisite.is_dir() or any(part == ".." for part in prerequisite.parts):
        raise FreightV2StagingError("prerequisite attempt directory is not a real directory")
    facts = freight_facts()
    metadata = read_prelaunch(prerequisite)
    if metadata["world"].get("expected_welcome") != retained_welcome():
        raise FreightV2StagingError("the A1 prerequisite welcome is not the retained identity")
    return dict(
        schema=D5_FREIGHT_V2_PREREQUISITE_SCHEMA,
        role="PREREQUISITE_ATTEMPT",
        retained_directory=str(prerequisite),
        save=facts["save"],
        save_sha256=facts["save_sha256"],
        qualified_save_sha256=facts["qualified_save_sha256"],
        prelaunch_digest=facts["prelaunch_digest"],
        attempt=facts["attempt"],
        milestone=facts["milestone"],
        expected_welcome=facts["expected_welcome"],
        verification=(
            "full replay verification of the consumed A1 extension attempt "
            "receipt (EXTENSION_COMPLETION_VERIFIED) plus the pinned "
            "authoritative after-save digest"
        ),
        provenance=dict(
            schema=D5_EXTENSION_PRELAUNCH_SCHEMA,
            attempt=facts["attempt"],
            milestone=facts["milestone"],
            prelaunch_sha256=facts["prelaunch_digest"],
            after_save_sha256=facts["save_sha256"],
            replay="EXTENSION_COMPLETION_VERIFIED",
            station_sids=facts["station_sids"],
            acceptance_recheck=ACCEPTANCE_RECHECK_STATEMENT,
            statement=(
                "the staged freight v2 source world is the consumed A1 "
                "corridor-extension candidate's receipt-bound close-out save; "
                "the candidate-3 lineage record is embedded as provenance, "
                "never as a re-opened chain walk"
            ),
        ),
    )


# --- Candidate planning facts -------------------------------------------------


def _expected_world_pins(plan: FreightPlanV2) -> dict:
    """The world-pin table every v2 binding (staging, preflight, replay) checks."""
    return dict(
        pickup=plan.pickup,
        pickup_front=plan.pickup_front,
        delivery=plan.delivery,
        delivery_front=plan.delivery_front,
        depot=plan.depot,
        depot_front=plan.depot_front,
        company=plan.company,
        cargo=plan.cargo,
        engine=plan.engine,
        pickup_industry=plan.pickup_industry,
        delivery_industry=plan.delivery_industry,
        expected_funds=plan.expected_funds,
        witness=list(plan.witness),
        vehicle_route=list(plan.vehicle_route),
        cycles=plan.cycles,
        day_budget=plan.day_budget,
        cycle_day_cap=plan.cycle_day_cap,
        request_budget=plan.request_budget,
        watch_ticks=WATCH_MAX_TICKS_V2,
        window_day_cap=FREIGHT_CYCLE_DAY_CAP_V2,
        expected_fleet=0,
    )


def plan_policy() -> dict:
    """The freight v2 cycle's authorized plan policy for the staged candidate.

    The scalar ``target_tile`` keeps the proven shared authorization payload
    shape: the pickup stop tile, where the only vehicle-carrying chain of
    the plan starts. The complete ordered exchange scope joins the payload
    additively through the same shared authorization builder keys (schedule
    + ``plan_digest``; per-op admission intents are receipts, not plan
    identities). ``schedule_version`` names the schedule derivation the
    plan digest binds: the fixed thirty-exchange cycle-looped derivation.
    """
    schedule = freight_schedule()
    plan = freight_plan_v2()
    if schedule[0]["exchange"] != FREIGHT_EXCHANGE_IDS_V2[0] or schedule[0]["op"] != "site":
        raise FreightV2StagingError("the staged schedule must begin with the site admission")
    if any(entry["op"] not in FREIGHT_OPS_V2 for entry in schedule):
        raise FreightV2StagingError("a scheduled exchange carries an unknown op")
    commands = ("GSVehicle.BuildVehicle", "GSOrder.AppendOrder", "GSVehicle.StartStopVehicle")
    return dict(
        company=plan.company,
        target_tile=int(plan.pickup),
        max_cost=plan.max_cost,
        command=" + ".join(commands),
        stale_rule=(
            "re-observe every pin of each exchange immediately before its "
            "one dispatch; any mismatch stops the phase without any command "
            "and preserves the verified prefix"
        ),
        identity=(
            "wire contract v8: every exchange presents one uniform prelaunch "
            "plan digest; per-op admission intents are receipts, not new plan "
            "identities (one attempt, one company, one vehicle, one purchase)"
        ),
        schedule=schedule,
        plan_digest=plan_digest_of(schedule),
        plan_model_digest=plan.digest,
        schedule_version=SCHEDULE_VERSION,
        engine=dict(
            pin=plan.engine,
            provisional=ENGINE_PIN_PROVISIONAL_V2,
            capacity=ENGINE_CENSUS_V2["capacity"],
            cargo=ENGINE_CENSUS_V2["cargo"],
            price=ENGINE_CENSUS_V2["price"],
            running_cost_per_economy_year=ENGINE_CENSUS_V2["running_cost_per_economy_year"],
            max_speed=ENGINE_CENSUS_V2["max_speed"],
            statement=(
                "the engine pin is the provisional offline census pin "
                "(operator Option B); the native engine readback admits it "
                "fail-closed: any identity or census deviation refuses "
                "ENGINE_PIN_MISMATCH before any purchase mutation"
            ),
        ),
        route_provenance=dict(
            schema="d5-freight2-witness-route-derivation-v1",
            planner="pinned-witness-route-derivation",
            witness_length=FREIGHT_WITNESS_LENGTH_V2,
            route_length=FREIGHT_ROUTE_LENGTH_V2,
            witness=list(plan.witness),
            route=list(plan.vehicle_route),
            route_digest=plan.route_digest,
            witness_digest=plan.witness_digest,
            removed=list(
                (FREIGHT_STALE_DELIVERY_TILE_V2, FREIGHT_STALE_BACKTRACK_TILE_V2)
            ),
            statement=(
                "the vehicle route is derived from the actual pinned "
                "31-tile construction witness the A1 extension built "
                "(F-2): the stale D4 delivery bay and the backtracked "
                "repeat of its front tile are removed; the route is never "
                "hand-invented and its digest is a separate binding from "
                "the witness digest"
            ),
        ),
        world=dict(
            pickup=int(plan.pickup),
            pickup_front=int(plan.pickup_front),
            delivery=int(plan.delivery),
            delivery_front=int(plan.delivery_front),
            depot=plan.depot,
            depot_front=int(plan.depot_front),
            company=plan.company,
            cargo=plan.cargo,
            engine=plan.engine,
            pickup_industry=plan.pickup_industry,
            delivery_industry=plan.delivery_industry,
            expected_funds=plan.expected_funds,
            witness=list(plan.witness),
            vehicle_route=list(plan.vehicle_route),
            cycles=plan.cycles,
            day_budget=plan.day_budget,
            cycle_day_cap=plan.cycle_day_cap,
            request_budget=plan.request_budget,
            watch_ticks=WATCH_MAX_TICKS_V2,
            window_day_cap=FREIGHT_CYCLE_DAY_CAP_V2,
            expected_fleet=0,
            running_cost_allowance=FREIGHT_RUNNING_COST_ALLOWANCE_V2,
            statement=(
                "the staged freight v2 world is the A1 corridor-extension "
                "close-out: route-receipt-bound corridor stops with the new "
                "delivery bay, the company depot joined to its pinned front, "
                "one planned cycle vehicle on road fuel, and the industry "
                "ids to be discovered natively (F-3)"
            ),
        ),
        prerequisite_world=dict(
            schema=D5_FREIGHT_V2_PREREQUISITE_SCHEMA,
            statement=(
                "the freight v2 candidate's source world is the A1 "
                "corridor-extension close-out: both stops must read company "
                "truck stops with their pinned fronts, the directed "
                "front-to-depot road edge must be present, the vehicle "
                "route's 28 directed adjacent pairs must re-check connected "
                "on the company's own road, and an unpaused company with "
                "zero vehicles at exact close-out funds at native admission "
                "time"
            ),
        ),
    )


def budgets() -> dict:
    """The staged budget table for the freight v2 candidate.

    The request accounting stays bound to the staged schedule derivation
    (30 planned exchanges of the 32 unique-id dispatcher cap); there is
    deliberately no aggregate phase-spending budget — the per-exchange
    ``max_cost`` ceiling plus the single realized purchase remain the only
    cost contract. The aggregate E53 economy-day authority (``day_budget``)
    binds the watch windows instead: every window dispatch is gated on the
    elapsed-day ledger against its per-window ``window_day_cap`` lease.
    """
    return dict(
        launches=1,
        connection_attempts=1,
        requests=FREIGHT_STAGED_REQUESTS_BUDGET,
        planned_exchanges=PLANNED_FREIGHT_REQUESTS,
        planned_cycles=PLANNED_FREIGHT_CYCLES_V2,
        gsadmin_bytes=MAX_FREIGHT_SEND_BYTES,
        response_bytes=MAX_FREIGHT_RESPONSE_BYTES_V2,
        retries=0,
        reconnects=0,
        readiness_seconds=45,
        request_seconds=10,
        watch_seconds=FREIGHT_WATCH_WALL_SECONDS,
        exchange_margin_seconds=FREIGHT_EXCHANGE_MARGIN_SECONDS,
        total_seconds=900,
        watch_ticks=WATCH_MAX_TICKS_V2,
        window_day_cap=FREIGHT_CYCLE_DAY_CAP_V2,
        day_budget=FREIGHT_DAY_BUDGET_V2,
        cycle_wall_cap_seconds=FREIGHT_CYCLE_WALL_CAP_SECONDS_V2,
        running_cost_allowance=FREIGHT_RUNNING_COST_ALLOWANCE_V2,
        max_cost=FREIGHT_MAX_COST_V2,
        expected_funds=FUNDS_AT_A1_CLOSE,
    )


def expected_readback_policy() -> dict:
    """The receipt contract's observable readback story for the freight v2 cycle."""
    return dict(
        admission=(
            "the site exchange returns READY with both stops as valid truck "
            "stop stations with their discovered ids, the depot owned with "
            "its directed front-to-depot edge proven, the fully connected "
            "vehicle-route summary, the delivery acceptance catchment at "
            "the pinned 8/8 bound, the recorded production/waiting levels, "
            "the F-3 unique-cargo-industry discoveries latched (producing "
            "pickup, accepting delivery), a company with zero vehicles and "
            "the A1 close-out funds exactly"
        ),
        engine=(
            "the engine exchange returns READY with the pinned engine id "
            "at its census price, capacity, cargo and speed inside the "
            "ceiling, and its bounded compatible-universe echo"
        ),
        purchase=(
            "the purchase exchange re-quotes equal to the tested quote and "
            "builds the one vehicle in the pinned depot, funds moving by "
            "exactly the recorded quote"
        ),
        vehicle=(
            "each independent vehicle readback re-observes the admitted "
            "identity, capacity and cargo natively at zero cost"
        ),
        orders=(
            "the two append exchanges record the pickup stop-tile order "
            "with OF_NONE and the delivery stop-tile order with OF_NO_LOAD "
            "against the site-read corridor (N1: tile destinations; N2: "
            "the real 15.x flags; OF_FULL_LOAD is never issued); the "
            "inventory exchange verifies the exact two-order set"
        ),
        drive=(
            "the cycles record their honest observations under their "
            "bounded tick/day budgets: the departure snapshot satisfies "
            "0 < load <= capacity (F-4, partial loads legal) and is typed "
            "only after the verified departure (E53: sampled pickup visit, "
            "then an on-route reading past the stop, with the pickup "
            "monitor's own reading equal to the truck load at that sample); "
            "an empty departure under the same proof with zero pickup "
            "residue is the typed ZERO_DEPARTED event (F-11), never a "
            "success; the depot-to-pickup travel leg stays waiting, an "
            "off-route vehicle is typed INVALID_ROUTE, the delivery is "
            "typed only at the pinned bay tile whose echo the DELIVERED "
            "reply carries, and the delivery window reconciles both "
            "monitor deltas with the departure snapshot exactly, consumes "
            "both with keep=false and re-arms by observing zero residue "
            "with keep=true under the 60-day aggregate day authority"
        ),
        finance=(
            "the finance exchange records the income and delivered-cargo "
            "deltas over the armed baselines plus the cargo acceptance "
            "date corroborating the delivery windows; a zero-delivery "
            "attempt must read zero income and zero delivered deltas"
        ),
        finish=(
            "the finish exchange records its issued stop and the vehicle's "
            "final enumerable state; the vehicle is never sold and no "
            "further authority is implied"
        ),
        receipt=(
            "attempt-bound only after every exchange verifies against the "
            "accumulated attempt state, in execution order, with the full "
            "attempt receipt re-verified from the retained exchanges"
        ),
    )


def attempt_name() -> str:
    """The candidate's one attempt name, bound to its own staged scope."""
    return FREIGHT_ATTEMPT_V2


# --- Candidate staging ---------------------------------------------------------


def prepare_candidate(
    directory: Path, *, prerequisite: Path = PINNED_PREREQUISITE
) -> PreparedProof:
    """Stage the fresh save-load composition; no process or connection."""
    prerequisite = Path(prerequisite).resolve()
    if prerequisite != PINNED_PREREQUISITE:
        raise FreightV2StagingError("the staged world requires the pinned A1 prerequisite")
    schedule = freight_schedule()
    if (
        len(schedule) != PLANNED_FREIGHT_EXCHANGES_V2
        or [entry["exchange"] for entry in schedule] != list(FREIGHT_EXCHANGE_IDS_V2)
        or plan_policy()["schedule_version"] != SCHEDULE_VERSION
    ):
        raise FreightV2StagingError("the staged freight v2 schedule drifted")
    if sha256(BINARY) != BINARY_SHA256 or matching_processes(BINARY):
        raise FreightV2StagingError("pinned binary / exclusive runtime gate failed")
    directory = directory.resolve()
    binding = prerequisite_binding(prerequisite)
    welcome = binding["expected_welcome"]
    world = stage_world(binding, welcome)
    plan = plan_policy()
    if sha256(source_save_path(world)) != world["save_sha256"]:
        raise FreightV2StagingError("staged world source save digest mismatch")
    directory.mkdir(parents=True, exist_ok=False)
    workspace = RuntimeWorkspace.create(directory / "isolated", retain=True)
    reservation = EndpointReservation.allocate()
    try:
        key = AuthorizedKey.generate()
        key_path = workspace.root / ".admin-secret"
        with os.fdopen(
            os.open(key_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600), "wb"
        ) as stream:
            stream.write(key._secret)
        workspace.write_config(
            AdminSettings(
                password="",
                port=reservation.admin_port,
                game_port=reservation.game_port,
                authorized_public_key_hex=key.public_hex,
            )
        )
        config = workspace.config.read_text().replace(
            "pause_on_newgame = true", "pause_on_newgame = false"
        )
        # Save-load composition: no [game_creation] block; the queued source
        # save provides the world. Staged scripts announce retained identities.
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
        composition, create_instance, version = staged_composition()
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
        spec = LaunchSpecification(
            workspace,
            RuntimeIdentity(BINARY.resolve(), "15.3", BINARY_SHA256),
            argv,
            workspace.root,
            workspace.environment,
            workspace.logs / "stdout.log",
            workspace.logs / "stderr.log",
        )
        frozen = source_freeze()
        for source in (FREIGHT_V2_PACKAGE, AI_PACKAGE):
            for path in sorted(source.glob("*.nut")):
                frozen[str(path.resolve())] = sha256(path)
        frozen.update(
            {
                str(path): sha256(path)
                for path in sorted(workspace.root.rglob("*"))
                if path.is_file() and path.name != ".admin-secret"
            }
        )
        # The exact runtime closure of the freight v2 execution path (the
        # wire contract, the v2 ceremony module and the A1 lineage modules
        # they import) and the exact installed dependency bytes join the
        # shared source_freeze() contract through the same parameterized D2
        # machinery — never weakening it.
        frozen.update(d2_source_closure(D5_V2_CLOSURE_ROOT))
        frozen.update(d2_dependency_inventory(D5_V2_CLOSURE_ROOT))
        prepared = PreparedProof(
            directory,
            spec,
            key_path,
            key.public_hex,
            (reservation.game_port, reservation.admin_port),
        )
        metadata = dict(
            schema=D5_FREIGHT_V2_PRELAUNCH_SCHEMA,
            milestone=MILESTONE_FREIGHT,
            kind=KIND,
            attempt=attempt_name(),
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
                    "the staged composition announces the save's stored GameScript "
                    "name/version from the retained frozen-source evidence; the "
                    "freight v2 handler runs as the retained CreateInstance subclass"
                ),
            ),
            save_policy=(
                "owned session-before.sav and after.sav only; the retained "
                "source save, the prerequisite attempt record and every "
                "historical artifact stay untouched"
            ),
            plan_policy=plan,
            expected_readback=expected_readback_policy(),
            bootstrap_command=f"start_ai {STAGED_AI_DIRECTORY}",
            execution_command=[
                str(PROJECT / ".venv/bin/python"),
                "-m",
                "app.simulation.openttd.proof.corridor_freight_v2_native",
                "run",
                str(directory),
            ],
            budgets=budgets(),
            cleanup=[
                "close secure session",
                "quit and reap process",
                "verify endpoints",
                "retain session logs and saves",
                "remove credential",
                "dispose owned workspace",
                "never modify the retained save or any historical artifact",
            ],
            authorization=(
                "PENDING — requires ONE fresh operator authorization after all "
                "preflight gates; offline staging consumed no claim and no "
                "authorization file exists"
            ),
            pin_provenance=dict(
                source=plan["target_tile"],
                manifest_verified=True,
                statement=(
                    "the plan derives from the replay-verified consumed A1 "
                    "corridor-extension candidate's close-out world whose "
                    "actual built construction witness is bundled verbatim; "
                    "the vehicle route is the derived ordered subsequence of "
                    "that witness (F-2), never a renamed hardcoded route"
                ),
            ),
            environment=launch_environment(prepared),
            environment_overrides=dict(spec.environment),
            frozen=frozen,
        )
        metadata["prerequisite"] = dict(
            schema=D5_FREIGHT_V2_PREREQUISITE_SCHEMA,
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


def preflight(prepared: PreparedProof) -> dict:
    """Offline launch-boundary rehearsal of the staged freight v2 candidate.

    Opens nothing, consumes nothing: the seal, the frozen runtime closure,
    the schedule pins, the world binding and the endpoint reservation are
    re-checked against the compiled derivations, with the A1 lineage gates
    for the staged chain.
    """
    directory = prepared.directory
    if sha256(directory / "PRELAUNCH.json") != (directory / "PRELAUNCH.sha256").read_text().strip():
        raise ValueError("prelaunch seal mismatch")
    metadata = read_prelaunch(directory)
    if (directory / "CLAIM.json").exists():
        raise ValueError("one native attempt already consumed")
    if metadata.get("schema") != D5_FREIGHT_V2_PRELAUNCH_SCHEMA:
        raise ValueError("staged prelaunch record is not the freight v2 lineage")
    verify_freeze(metadata["frozen"])
    require_frozen_d2_closure(metadata["frozen"], D5_V2_CLOSURE_ROOT)
    require_frozen_d2_dependencies(metadata["frozen"], D5_V2_CLOSURE_ROOT)
    policy = metadata["plan_policy"]
    if metadata["attempt"] != attempt_name():
        raise ValueError("staged attempt identity drifted from its own scope")
    staged = freight_schedule()
    if policy["schedule"] != staged or policy["plan_digest"] != plan_digest_of(staged):
        raise ValueError("staged freight schedule drifted from the compiled derivation")
    if policy["schedule_version"] != SCHEDULE_VERSION:
        raise ValueError("the staged schedule derivation drifted")
    world = policy["world"]
    plan = freight_plan_v2()
    # Every execution-relevant world pin must match the compiled plan; a
    # re-sealed PRELAUNCH record is not a substitute for these derivations.
    expected_world = _expected_world_pins(plan)
    for name, expected in expected_world.items():
        if world.get(name) != expected:
            raise ValueError(f"staged world pin {name} drifted from the compiled plan")
    for name, expected in (
        ("company", plan.company),
        ("target_tile", plan.pickup),
        ("max_cost", plan.max_cost),
        ("plan_model_digest", plan.digest),
    ):
        if policy.get(name) != expected:
            raise ValueError(f"staged plan pin {name} drifted from the compiled plan")
    if metadata.get("budgets") != budgets():
        raise ValueError("staged budget pins drifted from the compiled contract")
    engine = policy.get("engine")
    if not isinstance(engine, dict):
        raise ValueError("the staged plan lacks its engine pin")
    expected_engine = dict(
        pin=ENGINE_PIN_V2,
        provisional=ENGINE_PIN_PROVISIONAL_V2,
        capacity=ENGINE_CENSUS_V2["capacity"],
        cargo=ENGINE_CENSUS_V2["cargo"],
        price=ENGINE_CENSUS_V2["price"],
        running_cost_per_economy_year=ENGINE_CENSUS_V2["running_cost_per_economy_year"],
        max_speed=ENGINE_CENSUS_V2["max_speed"],
    )
    for name, expected in expected_engine.items():
        if engine.get(name) != expected:
            raise ValueError(f"staged engine pin {name} drifted from the provisional pin")
    provenance = policy.get("route_provenance")
    if not isinstance(provenance, dict):
        raise ValueError("the staged plan lacks its route provenance")
    expected_provenance = dict(
        witness_length=FREIGHT_WITNESS_LENGTH_V2,
        route_length=FREIGHT_ROUTE_LENGTH_V2,
        witness=list(plan.witness),
        route=list(plan.vehicle_route),
        route_digest=plan.route_digest,
        witness_digest=plan.witness_digest,
        removed=[FREIGHT_STALE_DELIVERY_TILE_V2, FREIGHT_STALE_BACKTRACK_TILE_V2],
    )
    for name, expected in expected_provenance.items():
        if provenance.get(name) != expected:
            raise ValueError(f"staged route provenance pin {name} drifted")
    for entry in staged:
        if entry["op"] not in FREIGHT_OPS_V2:
            raise ValueError("a scheduled exchange carries an unknown op")
        # E53: every watch window presents the staged tick lease and the
        # uniform per-window economy-day lease; the aggregate attempt
        # authority gate owns the 60-day arithmetic across the windows.
        if entry["op"] in ("load-watch", "transit-watch", "deliver-watch") and (
            entry["watch_ticks"] != WATCH_MAX_TICKS_V2
            or entry["watch_days"] != FREIGHT_CYCLE_DAY_CAP_V2
        ):
            raise ValueError("the watch window exceeds its bounded phase budgets")
        if entry["op"] in ("site",) and entry.get("order_index") is not None:
            raise ValueError("a non-order exchange carries no stop index")
        if entry["op"] == "order" and entry.get("order_index") not in (0, 1):
            raise ValueError("order rows carry their stop index")
    binding = prerequisite_binding(Path(metadata["prerequisite"]["directory"]))
    required = ("attempt", "milestone", "directory", "prelaunch_sha256", "after_save_sha256")
    staged_prereq = {name: metadata["prerequisite"][name] for name in required}
    if staged_prereq != dict(
        attempt=binding["attempt"],
        milestone=binding["milestone"],
        directory=binding["retained_directory"],
        prelaunch_sha256=binding["prelaunch_digest"],
        after_save_sha256=binding["save_sha256"],
    ):
        raise ValueError("the staged prerequisite binding drifted from its replay-verified record")
    if metadata["prerequisite"].get("schema") != D5_FREIGHT_V2_PREREQUISITE_SCHEMA:
        raise ValueError("the staged prerequisite schema drifted from the freight v2 lineage")
    world_block = metadata["world"]
    if (
        world_block.get("retained_directory") != binding["retained_directory"]
        or world_block.get("source_save") != binding["save"]
        or world_block.get("save_sha256") != binding["save_sha256"]
        or world_block.get("qualified_save_sha256") != binding.get("qualified_save_sha256")
    ):
        raise ValueError("the staged world is not the pinned A1 after-save")
    if world_block["save_sha256"] != A1_AFTER_SAVE_SHA256_V2:
        raise ValueError("the staged world save digest is not the pinned authoritative world")
    if world_block["expected_welcome"] != retained_welcome():
        raise ValueError("retained world identity requirements drifted")
    verify_staged_source_save(
        {"save_sha256": world_block["save_sha256"]},
        Path(metadata["workspace"]) / "source.sav",
    )
    composition, _, _ = staged_composition()
    staged_identity = Path(metadata["workspace"]) / "game" / SOURCE_SAVE_GS_NAME
    if staged_identity.joinpath("info.nut").read_bytes() != composition["info.nut"]:
        raise ValueError("staged GameScript identity drifted from the retained composition")
    if staged_identity.joinpath("main.nut").read_bytes() != composition["main.nut"]:
        raise ValueError("staged freight v2 handler drifted from its bounded package")
    if not prepared.spec.workspace.root.is_relative_to(directory / "isolated"):
        raise ValueError("workspace ownership mismatch")
    ClearingNativeBackend(authorized_one_launch=True).preflight(prepared)
    reservation = EndpointReservation.allocate(*prepared.endpoints)
    reservation.close()
    return metadata


# --- Wire protocol 8: shared request bound for live and replay paths ----------


def encode_freight_request(payload: bytes) -> bytes:
    """Frame one protocol-8 request under its named application bound.

    Both the live exchange and the retained-frame replay call this helper, so
    the 768-byte request contract cannot silently fall back to the generic
    default on one path only.
    """
    return encode_gamescript(payload, max_payload_bytes=MAX_FREIGHT_REQUEST_BYTES_V2)


def decode_freight_request(payload: bytes) -> bytes:
    """Decode one protocol-8 request body under the same named bound."""
    return decode_gamescript(payload, max_payload_bytes=MAX_FREIGHT_REQUEST_BYTES_V2)


# --- Wire protocol 8: secure session and one-launch backend --------------------


class FreightV2SecureSession(SecureAdminSession):
    """Only the freight v2 operations extend the secure write policy.

    A protocol-5 freight request cannot parse as a v2 request (the protocol
    literal differs), so the frozen v1 handler can never ride this session.
    """

    def validate_outbound(self, frame: bytes) -> None:
        if self.state is not AuthState.ACTIVE:
            raise ValueError("encrypted ACTIVE stream required")
        if len(frame) < 3 or struct.unpack_from("<H", frame)[0] != len(frame):
            raise ValueError("invalid frame")
        if frame[2] == ADMIN_GAMESCRIPT:
            request = FreightRequestV2.model_validate_json(decode_freight_request(frame[3:]))
            request.to_bytes()
        elif frame not in (gamescript_subscription(), encode_admin_quit()):
            super().validate_outbound(frame)


class FreightV2NativeBackend(ClearingNativeBackend):
    """One-launch backend carrying the freight v2 lineage launch marker."""

    launch_marker_schema = D5_FREIGHT_V2_LAUNCH_CONSUMED_SCHEMA

    async def connect(self, prepared: PreparedProof, *, frame_observer) -> FreightV2SecureSession:
        """Bind the staged runtime's Admin listener to one owned secure session."""
        if not any(
            r["table"] == "tcp" and r["local_port"] == prepared.endpoints[1] and r["state"] == 10
            for r in kernel_socket_rows()
        ):
            raise ValueError("native Admin listener readiness absent")
        key = AuthorizedKey.from_bytes(prepared.key_path.read_bytes())
        session = await FreightV2SecureSession.connect_secure(
            "127.0.0.1",
            prepared.endpoints[1],
            5,
            key=key,
            frame_observer=frame_observer,
        )
        self.session = session
        return session


def exchange_timeout_seconds(request: FreightRequestV2, *, budget_table: dict) -> float:
    """The wall-clock budget one exchange may consume.

    Window exchanges are bounded by the design's watch-window wall budget plus
    the client margin; every other exchange is an immediate request/readback
    bounded by the staged request budget. Every exchange is finally clamped
    to the attempt's remaining overall budget in :func:`exchange`.
    """
    request_seconds = float(budget_table["request_seconds"])
    if request.op in FREIGHT_WATCH_OPS:
        return float(budget_table["watch_seconds"]) + float(budget_table["exchange_margin_seconds"])
    return request_seconds


async def exchange(
    session,
    request: FreightRequestV2,
    directory: Path,
    *,
    budget_table: dict | None = None,
    overall_deadline: float | None = None,
    clock=time.monotonic,
    timeout_factory=asyncio.timeout,
) -> FreightReadbackV2:
    """One sealed protocol-8 exchange; every frame and file is retained.

    The per-exchange timeout is derived from the applicable phase budget and
    clamped to the attempt's remaining overall budget. Timeout, cancellation,
    disconnection, duplicate frames and stale frames all fail closed; a late
    response for another request can never be accepted as this exchange.
    """
    budget_table = budget_table if budget_table is not None else budgets()
    permitted = exchange_timeout_seconds(request, budget_table=budget_table)
    if overall_deadline is not None:
        remaining = overall_deadline - clock()
        if remaining <= 0:
            raise TimeoutError("freight attempt overall watch window exhausted")
        permitted = min(permitted, remaining)
    raw = request.to_bytes()
    (directory / (request.request_id + "-request.json")).write_bytes(raw)
    await session.send(encode_freight_request(raw))
    decoder = AdminFrameDecoder()
    try:
        async with timeout_factory(permitted):
            while True:
                chunk = await session.receive()
                if not chunk:
                    raise ConnectionError("freight proof stream disconnected")
                game_frames = []
                for kind, payload in decoder.feed_frames(chunk):
                    if kind != SERVER_GAMESCRIPT:
                        raise ValueError("unexpected freight-proof packet")
                    game_frames.append(payload)
                if len(game_frames) > 1:
                    raise ValueError("duplicate freight-proof response frame")
                if game_frames:
                    response = decode_gamescript(
                        game_frames[0], max_payload_bytes=MAX_FREIGHT_RESPONSE_BYTES_V2
                    )
                    (directory / (request.request_id + "-response.json")).write_bytes(response)
                    return FreightReadbackV2.parse_for(request, response)
    except TimeoutError:
        raise TimeoutError(
            f"freight exchange {request.request_id} exceeded its {permitted:.1f}s budget"
        ) from None


def _freight_exchange_request(
    entry: dict, seal: str, plan: FreightPlanV2, state: dict
) -> FreightRequestV2:
    """Build one request whose op echoes are the latched admission facts."""
    op = entry["op"]
    engine = -1
    vehicle = -1
    expected_cost = 0
    order_index = -1
    watch_ticks = -1
    watch_days = -1
    if op == "purchase":
        engine = int(plan.engine)
        expected_cost = int(state["engine"].quote)
    elif op == "engine":
        engine = int(plan.engine)
    elif op in (
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
    ):
        engine = int(plan.engine)
        vehicle = int(state["vehicle"])
    if op == "order":
        order_index = int(entry["order_index"])
    if op == "load-watch" or op in ("transit-watch", "deliver-watch"):
        watch_ticks = int(entry["watch_ticks"])
        watch_days = int(entry["watch_days"])
    return FreightRequestV2(
        op=op,
        request_id=entry["exchange"],
        plan=seal,
        company=plan.company,
        max_cost=plan.max_cost,
        pickup=plan.pickup,
        delivery=plan.delivery,
        depot=plan.depot,
        route=tuple(plan.vehicle_route) if op == "site" else None,
        route_digest=plan.route_digest,
        witness_digest=plan.witness_digest if op == "site" else None,
        engine=engine,
        vehicle=vehicle,
        expected_cost=expected_cost,
        order_index=order_index,
        watch_ticks=watch_ticks,
        watch_days=watch_days,
    )


def verify_request_against_plan(
    request: FreightRequestV2, *, plan: FreightPlanV2, seal: str
) -> None:
    """Refuse a request that is not bound to the local planner plan.

    This is the trust anchor the GameScript cannot provide: Python owns the
    pinned witness and its derived route and derives their digests, so a
    stale or tampered request is rejected before any byte reaches the Admin
    session. The GameScript's ``route_digest``/``witness_digest`` latch then
    extends that binding across the attempt, refusing later drift before the
    purchase exchange.
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
    if request.max_cost != plan.max_cost:
        raise ValueError("request ceiling drifted from the planned ceiling")
    if request.route_digest != plan.route_digest:
        raise ValueError("request route digest drifted from the planned route")
    if request.op == "site":
        if request.route is None or list(request.route) != list(plan.vehicle_route):
            raise ValueError("site request route drifted from the planned vehicle route")
        if request.witness_digest != plan.witness_digest:
            raise ValueError("site request witness digest drifted from the pinned witness")
    elif request.route is not None or request.witness_digest is not None:
        raise ValueError("only the site request may carry a route or witness digest")


def _freight_day_authority(entry: dict, days_used: int) -> str | None:
    """The typed pre-dispatch refusals for the aggregate day authority (E53).

    Returns the refusal text when the planned exchange's window lease
    cannot fit the 60-day aggregate attempt authority against the elapsed
    day ledger. The ledger's provenance is the readback day echoes
    themselves: the start exchange latched the day of record and each
    verified window settled the span with its own day echo, so the dispatch
    gate's arithmetic stays indistinguishable-by-induction from the
    retained evidence — every window also stops at its own lease day, the
    stopped attempt dispatches nothing further, and the aggregate span
    cannot escape the budget. Non-window exchanges pass.
    """
    if entry["op"] not in ("load-watch", "transit-watch", "deliver-watch"):
        return None
    return freight_window_dispatch_refusal_v2(days_used, int(entry["watch_days"]))


async def execute_freight_attempt_v2(prepared: PreparedProof, backend) -> dict:
    """Execute the authorized one-attempt freight v2 phase (never offline).

    Bounded protocol-8 ceremony against an authorized backend seam: preflight,
    operator claim consumption, launch boundary, world identity, session
    saves, then the fixed thirty-exchange freight cycle in order. Every
    exchange runs one request whose readback is verified against the
    accumulated attempt state by the production freight v2 state machine;
    the first verification failure halts the phase: earlier verified exchanges
    are preserved, later exchanges never execute, and the world state after a
    failed attempt is explicitly uncertain (nothing compensates or retries).
    """
    directory = prepared.directory
    preflight(prepared)
    seal = sha256(directory / "PRELAUNCH.json")
    metadata = json.loads((directory / "PRELAUNCH.json").read_text())
    grant = grant_launch(directory, metadata, seal)
    grant.launch_identity = launch_critical_identity(prepared, metadata)
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
    plan = freight_plan_v2()
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
    exchanges: list[tuple[FreightRequestV2, FreightReadbackV2]] = []
    state: dict[str, Any] = dict(
        site=None,
        engine=None,
        vehicle=-1,
        # E53 aggregate day authority: the start exchange latches the day
        # of record; each verified watch window settles the elapsed span.
        day_reference=None,
        days_used=0,
    )
    overall_deadline = event_loop_deadline(metadata["budgets"]["total_seconds"])
    try:
        async with asyncio.timeout(metadata["budgets"]["total_seconds"]):
            await backend.launch(prepared, authorization=grant)
            result["native_launches"] = 1
            await wait_log(backend, prepared, FREIGHT_V2_READY_MARKER)
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
                raise ValueError("retained world identity mismatch")
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
                    # E53: the aggregate authority gate fires before this
                    # exchange's request is ever built or sent — a window
                    # whose lease cannot fit the remaining budget types the
                    # pre-dispatch halt here, with no bytes on the wire.
                    refusal = _freight_day_authority(entry, state["days_used"])
                    if refusal is not None:
                        raise ValueError(refusal)
                    request = _freight_exchange_request(entry, seal, plan, state)
                    verify_request_against_plan(request, plan=plan, seal=seal)
                    readback = await exchange(
                        session,
                        request,
                        directory,
                        budget_table=metadata["budgets"],
                        overall_deadline=overall_deadline,
                    )
                    result["requests"] += 1
                    probe = freight_phase_outcome_v2(
                        exchanges + [(request, readback)], prelaunch_digest=seal, plan=plan
                    )
                    if probe["failed"] is not None:
                        raise ValueError(
                            f"freight exchange {label} failed verification: "
                            f"{probe['failed']['error']}"
                        )
                    # The exchange binds under its own correlated readback
                    # request id in every case; the group receipts further
                    # name their request ids (purchase, vread-00), and cycle
                    # receipts name their cycle index.
                    receipt = probe["completed"][-1]
                    receipt_ids = {
                        value for key, value in receipt.items() if key.endswith("request_id")
                    }
                    receipt_ids |= set(receipt.get("request_ids") or ())
                    if readback.request_id != label or (receipt_ids and label not in receipt_ids):
                        raise ValueError(f"freight exchange {label} drifted from its schedule")
                    if entry["op"] == "deliver-watch" and receipt.get("cycle") != (
                        freight_exchange_cycle_index_v2(label)
                    ):
                        raise ValueError(f"freight cycle receipt {label} drifted from its cycle")
                    exchanges.append((request, readback))
                    result["exchanges"].append(label)
                    result["last_status"] = readback.status
                    result["command_accepted"] = True
                    result["state_changed"] = True
                    if entry["op"] == "site":
                        state["site"] = admit_freight_site_v2(
                            readback, prelaunch_digest=seal, plan=plan
                        )
                    elif entry["op"] == "engine":
                        state["engine"] = admit_freight_engine_v2(
                            readback, prelaunch_digest=seal, plan=plan, site=state["site"]
                        )
                    elif entry["op"] == "purchase":
                        state["vehicle"] = readback.vehicle
                    elif entry["op"] == "start" and label == "start-00":
                        # E53: the verified start reply fixes the day of
                        # record; every later window span is measured
                        # against it.
                        if readback.day is None:
                            raise ValueError("the start exchange did not echo its day of record")
                        state["day_reference"] = readback.day
                    elif entry["op"] in ("load-watch", "transit-watch", "deliver-watch"):
                        # E53: the verified window settles the elapsed-day
                        # ledger with its own day echo; a regression, or a
                        # span escaping the whole attempt authority, halts
                        # here (the probe above already ran the same gate).
                        if state["day_reference"] is None or readback.day is None:
                            raise ValueError("watch evidence lost its day ledger basis")
                        span = readback.day - state["day_reference"]
                        if span < 0 or span > FREIGHT_DAY_BUDGET_V2:
                            raise ValueError(
                                "the window day ledger regressed or escaped its authority"
                            )
                        state["days_used"] = span
                except Exception as error:
                    result["halt"] = dict(
                        label=label, error=type(error).__name__ + ": " + str(error)
                    )
                    break
            phase = freight_phase_outcome_v2(exchanges, prelaunch_digest=seal, plan=plan)
            result["phase"] = phase
            if phase["verification"] == "PHASE_COMPLETE":
                if len(exchanges) != PLANNED_FREIGHT_EXCHANGES_V2:
                    raise ValueError("phase completion evidence drifted from the staged schedule")
                attempt = verify_freight_attempt_v2(exchanges, prelaunch_digest=seal, plan=plan)
                after_save = await save(backend, prepared, "after")
                write_json(
                    directory / "receipt.json",
                    dict(
                        phase,
                        attempt,
                        before_save_sha256=before_save,
                        after_save_sha256=after_save,
                    ),
                )
                result["verified"] = True
                result["status"] = "NATIVE_FREIGHT_VERIFIED"
            else:
                result["status"] = "PHASE_HALTED_PREFIX_PRESERVED"
    except Exception as error:
        result["error"] = type(error).__name__ + ": " + str(error)
    finally:
        if result.get("last_status") not in ("NOT_DISPATCHED",):
            try:
                result["after_diagnostic_save_sha256"] = await save(
                    backend,
                    prepared,
                    "after-diagnostic",
                    diagnostic=True,
                )
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
            if result["status"] == "NATIVE_FREIGHT_VERIFIED":
                deny_verification(
                    result,
                    status="FAILED",
                    message=(
                        "ValueError: retained script log health findings deny the verified receipt"
                    ),
                )
        if result["returncode"] not in (None, 0):
            if result["status"] == "NATIVE_FREIGHT_VERIFIED":
                deny_verification(
                    result,
                    status="FAILED",
                    message=(
                        "ValueError: native runtime exited abnormally after receipt "
                        f"(return code {result['returncode']})"
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
        apply_cleanup_outcome(result, complete=cleanup_complete)
        write_json(directory / "cleanup.json", cleanup)
        write_json(directory / "result.json", result)
        (directory / "artifact-manifest.sha256").write_text(manifest(directory))
    return result


# --- Freight v2 attempt replay verification --------------------------------------


def _parse_v2_phase_frames(directory: Path):
    """Parse the retained frame stream of the owned secure session."""
    frames = json.loads((directory / "frames.json").read_text())
    outbound: list[bytes] = []
    replies: list[bytes] = []
    outbound_requests: list[FreightRequestV2] = []
    request_positions: dict[bytes, int] = {}
    reply_positions: dict[bytes, int] = {}
    for index, (direction, frame_hex) in enumerate(frames):
        frame = bytes.fromhex(frame_hex)
        if direction == "outbound":
            outbound.append(frame)
            if frame[2] != ADMIN_GAMESCRIPT:
                continue
            payload = decode_freight_request(frame[3:])
            try:
                query = FreightRequestV2.model_validate_json(payload)
            except Exception:
                raise ValueError("outbound frame contains invalid FreightRequestV2") from None
            outbound_requests.append(query)
            request_positions[payload] = index
        else:
            for kind, body in AdminFrameDecoder().feed_frames(frame):
                # The retained session stream also carries the handshake and
                # keepalive frames; only the gamescript exchanges are proof
                # material (the shared D2 chronology semantics).
                if kind != SERVER_GAMESCRIPT:
                    continue
                reply = decode_gamescript(body, max_payload_bytes=MAX_FREIGHT_RESPONSE_BYTES_V2)
                if reply not in reply_positions:
                    reply_positions[reply] = index
                replies.append(reply)
    return outbound, outbound_requests, replies, request_positions, reply_positions


def verify_attempt_identity(metadata: dict, *, plan: FreightPlanV2) -> dict:
    """Re-bind one retained attempt to its pinned prerequisite and plan.

    Replay must not trust the staged record's own declarations: the pinned A1
    prerequisite is re-verified from its retained receipt, the staged world's
    source-save digest must equal that prerequisite's receipt-bound after-save
    digest, the full retained welcome must match, and every plan/route/
    witness digest is re-derived. Returns the independently derived
    prerequisite binding for callers that need its provenance.
    """
    if metadata.get("attempt") != attempt_name():
        raise ValueError("retained attempt identity drifted from the staged scope")
    if (
        metadata.get("schema") != D5_FREIGHT_V2_PRELAUNCH_SCHEMA
        or metadata.get("kind") != KIND
        or metadata.get("milestone") != MILESTONE_FREIGHT
    ):
        raise ValueError("retained attempt is not the freight v2 lineage")
    staged_prerequisite = metadata.get("prerequisite")
    if not isinstance(staged_prerequisite, dict):
        raise ValueError("retained attempt lacks its prerequisite binding")
    binding = prerequisite_binding(Path(staged_prerequisite.get("directory", "")))
    expected_prerequisite = dict(
        schema=D5_FREIGHT_V2_PREREQUISITE_SCHEMA,
        attempt=binding["attempt"],
        milestone=binding["milestone"],
        directory=binding["retained_directory"],
        prelaunch_sha256=binding["prelaunch_digest"],
        after_save_sha256=binding["save_sha256"],
        verification=binding["verification"],
    )
    if staged_prerequisite != expected_prerequisite:
        raise ValueError("retained prerequisite binding drifted from the pinned A1 attempt")
    world = metadata.get("world")
    if not isinstance(world, dict):
        raise ValueError("retained attempt lacks its world binding")
    expected_world_binding = dict(
        retained_directory=binding["retained_directory"],
        source_save=binding["save"],
        save_sha256=binding["save_sha256"],
        qualified_save_sha256=binding.get("qualified_save_sha256"),
    )
    for name, expected in expected_world_binding.items():
        if world.get(name) != expected:
            raise ValueError(f"retained world {name} drifted from the pinned prerequisite")
    if world.get("save_sha256") != A1_AFTER_SAVE_SHA256_V2:
        raise ValueError("retained world is not the pinned A1 after-save")
    expected_welcome = world.get("expected_welcome")
    if expected_welcome != binding["expected_welcome"] or expected_welcome != retained_welcome():
        raise ValueError("retained world welcome drifted from the pinned identity")
    source_save = source_save_path(world)
    if not source_save.is_file():
        raise ValueError("the pinned prerequisite source save is absent")
    verify_staged_source_save({"save_sha256": binding["save_sha256"]}, source_save)
    staged_source = Path(metadata.get("workspace", "")) / "source.sav"
    if staged_source.is_file():
        verify_staged_source_save({"save_sha256": binding["save_sha256"]}, staged_source)

    plan_policy_dict = metadata.get("plan_policy")
    if not isinstance(plan_policy_dict, dict):
        raise ValueError("retained attempt lacks its plan policy")
    schedule = freight_schedule()
    if plan_policy_dict.get("schedule") != schedule or plan_policy_dict.get(
        "plan_digest"
    ) != plan_digest_of(schedule):
        raise ValueError("retained freight schedule drifted from the compiled derivation")
    if plan_policy_dict.get("plan_model_digest") != plan.digest:
        raise ValueError("retained plan model digest drifted from the compiled plan")
    if plan_policy_dict.get("schedule_version") != FREIGHT_SCHEDULE_VERSION:
        raise ValueError("retained schedule derivation version drifted")
    if metadata.get("budgets") != budgets():
        raise ValueError("retained budget contract drifted from the compiled contract")
    world_policy = plan_policy_dict.get("world")
    if not isinstance(world_policy, dict):
        raise ValueError("retained plan policy lacks its world pins")
    for name, expected in _expected_world_pins(plan).items():
        if world_policy.get(name) != expected:
            raise ValueError(f"retained world pin {name} drifted from the replayed plan")
    for name, expected in (
        ("company", plan.company),
        ("target_tile", plan.pickup),
        ("max_cost", plan.max_cost),
    ):
        if plan_policy_dict.get(name) != expected:
            raise ValueError(f"retained plan pin {name} drifted from the replayed plan")
    engine_pin = plan_policy_dict.get("engine")
    if not isinstance(engine_pin, dict):
        raise ValueError("retained plan policy lacks its engine pin")
    expected_engine = dict(
        pin=plan.engine,
        provisional=ENGINE_PIN_PROVISIONAL_V2,
        capacity=ENGINE_CENSUS_V2["capacity"],
        cargo=ENGINE_CENSUS_V2["cargo"],
        price=ENGINE_CENSUS_V2["price"],
        running_cost_per_economy_year=ENGINE_CENSUS_V2["running_cost_per_economy_year"],
        max_speed=ENGINE_CENSUS_V2["max_speed"],
    )
    for name, expected in expected_engine.items():
        if engine_pin.get(name) != expected:
            raise ValueError(f"retained engine pin {name} drifted from the provisional pin")
    provenance = plan_policy_dict.get("route_provenance")
    if not isinstance(provenance, dict):
        raise ValueError("retained plan policy lacks its route provenance")
    expected_provenance = dict(
        witness_length=FREIGHT_WITNESS_LENGTH_V2,
        route_length=FREIGHT_ROUTE_LENGTH_V2,
        witness=list(plan.witness),
        route=list(plan.vehicle_route),
        route_digest=plan.route_digest,
        witness_digest=plan.witness_digest,
        removed=[FREIGHT_STALE_DELIVERY_TILE_V2, FREIGHT_STALE_BACKTRACK_TILE_V2],
    )
    for name, expected in expected_provenance.items():
        if provenance.get(name) != expected:
            raise ValueError(f"retained route provenance pin {name} drifted")
    return binding


def verify_freight_attempt(directory: Path) -> dict:
    """Replay retained protocol-8 phase semantics; never trust a success label.

    The replay re-derives every retained fact independently: the operator
    authorization evidence, the staged freight schedule, the captured
    session frames and every per-exchange request/response pair, then
    re-verifies the whole attempt (receipt bound with the before/after save
    digests) with the production
    :func:`app.simulation.openttd.corridor_freight_v2.freight_phase_outcome_v2`
    and :func:`verify_freight_attempt_v2`. A success label alone is never
    evidence.
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
                "the candidate was never consumed by an operator authorization; "
                "no verified receipt is possible"
            ),
        )
    claims = json.loads(claims_path.read_text())
    if claims.get("prelaunch_digest") != seal:
        raise ValueError("attempt claim does not match its prelaunch seal")
    manifest_names: set[str] = set()
    for line in (directory / "artifact-manifest.sha256").read_text().splitlines():
        digest, name = line.split("  ", 1)
        if Path(name).name != name or not (directory / name).is_file():
            raise ValueError("artifact manifest mismatch")
        if sha256(directory / name) != digest:
            raise ValueError("artifact manifest mismatch")
        manifest_names.add(name)
    present_names = {
        path.name
        for path in directory.iterdir()
        if path.is_file() and path.name != "artifact-manifest.sha256"
    }
    if present_names != manifest_names:
        raise ValueError("artifact manifest is not exhaustive for the attempt directory")
    if metadata.get("schema") != D5_FREIGHT_V2_PRELAUNCH_SCHEMA:
        return dict(
            verification="AUTHORIZATION_UNVERIFIED",
            authorization_state="UNKNOWN_PRELAUNCH_SCHEMA",
            statement=(
                "the prelaunch record is not the launch-capable "
                f"{D5_FREIGHT_V2_PRELAUNCH_SCHEMA} lineage; no verified receipt is possible"
            ),
        )
    authorization_state = replay_authorization_state(directory, metadata, seal, claims)
    if authorization_state is not None:
        return dict(
            verification="AUTHORIZATION_UNVERIFIED",
            authorization_state=authorization_state,
            statement=(
                "the retained authorization evidence does not match the "
                "operator-verified record; no verified receipt is possible"
            ),
        )
    plan_policy_dict = metadata["plan_policy"]
    schedule = plan_policy_dict["schedule"]
    if plan_policy_dict["schedule"] != freight_schedule() or plan_policy_dict["plan_digest"] != (
        plan_digest_of(freight_schedule())
    ):
        raise ValueError("staged freight schedule drifted from the compiled derivation")
    _scheduled_exchange_ids(schedule)
    plan = freight_plan_v2()
    verify_attempt_identity(metadata, plan=plan)
    result = json.loads((directory / "result.json").read_text())
    runtime = json.loads((directory / "runtime-identity.json").read_text())
    expected_welcome = metadata["world"]["expected_welcome"]
    welcome = runtime.get("welcome")
    if runtime.get("encrypted") is not True or not isinstance(welcome, dict):
        raise ValueError("owned single-runtime encrypted execution evidence missing")
    for field in WELCOME_ORDER:
        expected = True if field == "dedicated" else expected_welcome[field]
        if welcome.get(field) != expected:
            raise ValueError(f"retained world welcome {field} drifted from the pinned identity")
    outbound, outbound_requests, replies, request_positions, reply_positions = (
        _parse_v2_phase_frames(directory)
    )
    if len(outbound_requests) > metadata["budgets"]["requests"]:
        raise ValueError("freight request budget exceeded (outbound frames)")
    paths = sorted(directory.glob("*-request.json"))
    file_queries = [FreightRequestV2.model_validate_json(path.read_bytes()) for path in paths]
    for path, query in zip(paths, file_queries, strict=True):
        if query.request_id != path.name[: -len("-request.json")]:
            raise ValueError("retained request file identity does not match its payload")
    if len(outbound_requests) < len(file_queries):
        return dict(
            verification="UNRESOLVED_ATTEMPT_EVIDENCE_PRESERVED",
            exchanges=result.get("exchanges", []),
            state_changed=result.get("state_changed", False),
            result_status=result.get("status", "UNKNOWN"),
            statement="incomplete retained exchange (fewer outbound frames); no receipt claimed",
        )
    if len(outbound_requests) > len(file_queries):
        raise ValueError("outbound frame count exceeds request file count (tampering)")
    if sorted(query.to_bytes() for query in outbound_requests) != sorted(
        query.to_bytes() for query in file_queries
    ):
        raise ValueError("outbound frame payloads do not match request file payloads")
    unknown = {query.request_id for query in file_queries} - _scheduled_exchange_ids(schedule)
    if unknown:
        raise ValueError(f"request identity outside the staged schedule: {sorted(unknown)}")
    seen_ids: set[str] = set()
    for query in outbound_requests:
        if query.request_id in seen_ids:
            raise ValueError(f"duplicate request_id in outbound frames: {query.request_id}")
        seen_ids.add(query.request_id)
    response_map = {}
    for path in paths:
        response_path = path.with_name(path.name.replace("-request.json", "-response.json"))
        if response_path.is_file():
            response_map[path.read_bytes()] = response_path.read_bytes()
    for path in sorted(directory.glob("*-response.json")):
        exchange_id = path.name[: -len("-response.json")]
        try:
            readback = FreightReadbackV2.model_validate_json(path.read_bytes())
        except ValueError as error:
            raise ValueError(
                f"retained response file is not a parseable readback: {path.name}"
            ) from error
        if readback.request_id != exchange_id:
            raise ValueError("retained response file identity does not match its payload")
        if not (directory / (exchange_id + "-request.json")).is_file():
            raise ValueError("retained response file lacks its request")
    for raw, response in response_map.items():
        if outbound.count(encode_freight_request(raw)) != 1 or replies.count(response) != 1:
            raise ValueError("retained exchange lacks unique secure-session frame evidence")
    retained_responses = set(response_map.values())
    for reply in replies:
        if reply not in retained_responses:
            raise ValueError("retained gateway response lacks its durable response file")
    for raw, response in response_map.items():
        if reply_positions[response] < request_positions[raw]:
            raise ValueError("a retained response precedes its own request in the frame stream")

    halted_position = None
    halt_record = result.get("halt")
    exchanges: list[tuple[FreightRequestV2, FreightReadbackV2]] = []
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
            query = FreightRequestV2.model_validate_json(request_path.read_bytes())
            raw = response_map.get(query.to_bytes())
            # A halted exchange the wire never completed (no response file)
            # is absent evidence, not a verification defect: the attempt's
            # halt already records the stop, so the pending suffix — not the
            # missing reply — carries the story.
            if raw is not None:
                exchange = FreightReadbackV2.parse_for(query, raw)
                exchanges.append((query, exchange))
        if pending:
            break
    phase = freight_phase_outcome_v2(exchanges, prelaunch_digest=seal, plan=plan)
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
            error=result.get("error", "process exited abnormally"),
            exit_evidence=dict(returncode=exit_codes[0], cleanup_returncode=exit_codes[1]),
        )
    if result["status"] == "NATIVE_FREIGHT_VERIFIED":
        if phase["verification"] != "PHASE_COMPLETE":
            raise ValueError("verified receipt contradicts its phase outcome")
        if result.get("halt") is not None or not result.get("command_accepted"):
            raise ValueError("verified receipt contradicts its retained attempt record")
        if (result.get("native_launches"), result.get("connections")) != (
            metadata["budgets"]["launches"],
            metadata["budgets"]["connection_attempts"],
        ):
            raise ValueError("verified receipt contradicts its launch/connection seal")
        if len(result.get("exchanges", [])) != PLANNED_FREIGHT_EXCHANGES_V2 or not cleanup_complete:
            raise ValueError("verified receipt cleanup or exchange inventory incomplete")
        if len(outbound_requests) != PLANNED_FREIGHT_EXCHANGES_V2:
            raise ValueError("verified receipt request inventory drifted from the schedule")
        attempt = verify_freight_attempt_v2(exchanges, prelaunch_digest=seal, plan=plan)
        receipt_path = directory / "receipt.json"
        if not receipt_path.is_file():
            raise ValueError("verified receipt record missing")
        expected = dict(
            phase,
            attempt=attempt,
            before_save_sha256=sha256(directory / "session-before.sav"),
            after_save_sha256=sha256(directory / "after.sav"),
        )
        # JSON round-trip both sides: the retained record stores serialized
        # arrays where the recomputed receipts hold python tuples; identity
        # semantics (not container type) define the replay match.
        if json.loads(receipt_path.read_text()) != json.loads(json.dumps(expected)):
            raise ValueError("retained freight receipt replay mismatch")
        return dict(verification="RECEIPT_VERIFIED", receipt=expected)
    if result["status"] == "FAILED_CLEANUP":
        # A genuine cleanup failure necessarily leaves cleanup incomplete. It is
        # preserved as failed evidence and can never replay as a verified
        # receipt; the dedicated arm avoids mislabelling it as a halted phase.
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
            phase["verification"] != "PARTIAL_EXECUTION_EVIDENCE"
            or not isinstance(halt_record, dict)
            or len(result.get("exchanges", [])) != len(phase["completed"])
            or (
                phase["failed"] is not None
                and phase["failed"].get("label") != halt_record.get("label")
            )
        ):
            raise ValueError("halted phase evidence contradicts its retained record")
        if not cleanup_complete:
            raise ValueError("halted attempt cleanup incomplete")
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("prepare", "preflight", "run", "verify"))
    parser.add_argument("directory", type=Path)
    parser.add_argument("--prerequisite", type=Path, default=PINNED_PREREQUISITE)
    args = parser.parse_args()
    directory = args.directory.resolve()
    if args.command == "prepare":
        prepared = prepare_candidate(directory, prerequisite=args.prerequisite)
        preflight(prepared)
        print("PRELAUNCH PASS", directory)
    elif args.command == "preflight":
        preflight(reopen_candidate(directory))
        print("PREFLIGHT PASS")
    elif args.command == "verify":
        verdict = verify_freight_attempt(directory)
        print(json.dumps(verdict, sort_keys=True))
        raise SystemExit(verdict_exit_status(verdict))
    else:
        read_prelaunch(directory)  # fail fast on any drifted prelaunch record
        result = asyncio.run(
            execute_freight_attempt_v2(
                reopen_candidate(directory),
                FreightV2NativeBackend(authorized_one_launch=True),
            )
        )
        print(json.dumps(result, sort_keys=True))
        raise SystemExit(exit_status(result))


if __name__ == "__main__":
    main()
