"""D5-CARGOFLOW-1 native staging pipeline (offline preparation only).

The F-11/E97 lineage halted terminal at ``transit-00`` with a zero-flow
observation the freight instrument could not attribute, and the cargo-dispatch
probe design record (``docs/d5-cargo-dispatch-probe-2026-11-04.md``)
prescribed this round's step: a strictly read-only native observation of the
industry→station cargo dispatch over the authoritative depot-chain world of
record — a fixed fourteen-sample ladder, every 5 sim days from the loaded
world's own clock, sampling the industry stockpiles, the per-source station
waiting and planned families, the monthly production and transported levels,
the current date and the funds echo, with zero company commands anywhere in
the plan (``docs/…`` §5: attempt-6 stays terminal; a probe verdict never
re-opens a freight attempt by itself).

The pipeline is a fourth narrow pipeline bound explicitly to
``CargoFlowPlan`` and its single pinned fourteen-sample schedule, reusing the
proven shared ceremony by import rather than copy (the census pipeline's
shape: staging → preflight → claim → one encrypted session → replay). Its
prerequisite of record is the depot-chain binding the freight v2 pipeline
already derives and verifies (``D5-F12-DEPOT-3`` after-save,
``183b2027…6a6``, world-pin version 3, plus the verified reload chain) —
imported through ``corridor_freight_v2_native.prerequisite_binding`` and
never re-derived here. The staging/claim machinery in
``corridor_freight_native`` stays plan-bound to its own contract families, so
a ``FreightPlan``, ``FreightPlanV2``, ``AcceptSurveyPlan`` or ``BoxCensusPlan``
can never be staged, sealed, executed or replayed as a cargo-flow probe, and
the probe's own schema refuses every foreign request on its session surface.

The probe is strictly read-only: its schedule admits only the ``sample``
observation op (every mutation-capable op is outside the protocol-10 contract
entirely), ``max_cost`` is 0 on every exchange, funds are read back per
sample, and cleanup is certified before any completion verdict. Nothing here
launches OpenTTD, connects to a port, writes a claim or mutates any world or
retained artifact.
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
from app.simulation.openttd.corridor_cargoflow import (
    CARGOFLOW_EXCHANGE_IDS,
    CARGOFLOW_OPS,
    CARGOFLOW_PICKUP_TILE,
    CARGOFLOW_REQUEST_BUDGET,
    CARGOFLOW_SAMPLE_OFFSETS,
    CARGOFLOW_SPAN_DAYS,
    CARGOFLOW_WAIT_DAY_CAP,
    CARGOFLOW_WAIT_MAX_TICKS,
    MAX_CARGOFLOW_REQUEST_BYTES,
    MAX_CARGOFLOW_RESPONSE_BYTES,
    PLANNED_CARGOFLOW_EXCHANGES,
    CargoFlowPlan,
    CargoFlowReadback,
    CargoFlowRequest,
    cargoflow_phase_outcome,
    cargoflow_plan,
    verify_request_against_cargoflow_plan,
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
CARGOFLOW_PACKAGE = PACKAGES / "d5_cargoflow_package"
AI_PACKAGE = PACKAGES / "road_company_package"
CARGOFLOW_CLOSURE_ROOT = "app.simulation.openttd.proof.corridor_cargoflow_native"

KIND = "cargoflow"
MILESTONE_CARGOFLOW = "D5-CARGOFLOW"
# The probe is its own fresh lineage (design record §6.4): the freight
# identities D5-FREIGHT-5 (spent) and D5-FREIGHT-6 (terminal) stay exactly as
# recorded and nothing here re-opens them.
CARGOFLOW_ATTEMPT = "D5-CARGOFLOW-1"
D5_CARGOFLOW_PRELAUNCH_SCHEMA = "d5-cargoflow-prelaunch-v1"
# The probe keeps the shared native consumed-launch marker family; its
# prerequisite lineage schema is the freight v2 depot-chain binding schema the
# shared ceremony already pins (the probe re-derives the depot prerequisite
# bytes but never writes them, design record §6.4).
D5_CARGOFLOW_LAUNCH_CONSUMED_SCHEMA = freight_native.D5_FREIGHT_LAUNCH_CONSUMED_SCHEMA
D5_CARGOFLOW_PREREQUISITE_SCHEMA = freight_v2_native.D5_FREIGHT_V2_PREREQUISITE_SCHEMA

# Prerequisite lineage of record: the pinned, consumed, replay-verified
# depot-mutation attempt (D5-F12-DEPOT-3 after-save, world-pin version 3),
# imported from the freight v2 binding's own pins — the probe world is the
# freight world of record, and one pin source of record stays one pin.
PINNED_PREREQUISITE = freight_v2_native.DEPOT_PREREQUISITE
PINNED_PREREQUISITE_AFTER_SAVE = freight_v2_native.DEPOT_PREREQUISITE_AFTER_SAVE
RELOAD_PREREQUISITE = freight_v2_native.RELOAD_PREREQUISITE
if PINNED_PREREQUISITE_AFTER_SAVE != (
    "183b20273a54ebe1a2cd9306145a9ea820bbd6114b1608c42079b4e1b1efe6a6"
):
    raise RuntimeError("the cargo-dispatch probe depot world pin drifted")

# The probe GameScript readiness marker is its own (the staged handler logs
# "D5_CARGOFLOW_READY" at Start); the road-company readiness marker follows
# the staged AI bootstrap exactly as the census does.
CARGOFLOW_READY_MARKER = "D5_CARGOFLOW_READY"

CARGOFLOW_EXCHANGE_MARGIN_SECONDS = freight_native.FREIGHT_EXCHANGE_MARGIN_SECONDS


class CargoflowStagingError(freight_v2_native.FreightV2StagingError):
    """Offline cargo-dispatch staging or pin derivation failed; nothing launched."""


# --- Migration-safety: the probe pipeline is cargoflow-plan typed -------------


def _require_cargoflow_plan(plan) -> CargoFlowPlan:
    """Refuse anything that is not the pinned ``CargoFlowPlan``.

    The other pipeline plans share several field names with a
    ``CargoFlowPlan``; every probe entry point guards here so a freight,
    survey or census plan can never be staged, sealed, executed or replayed
    as a dispatch probe, and so the single probe plan can never drift from
    its pinned derivation.
    """
    if not isinstance(plan, CargoFlowPlan):
        raise CargoflowStagingError("the cargo-dispatch probe accepts a CargoFlowPlan only")
    if plan.schema_version != 1:
        raise CargoflowStagingError("the probe plan carries an unknown schema version")
    if plan.digest != cargoflow_plan().digest:
        raise CargoflowStagingError("the probe plan drifted from the pinned observations")
    return plan


def cargoflow_pipeline_plan() -> CargoFlowPlan:
    """The single pinned plan of record re-derived from the module pins."""
    return _require_cargoflow_plan(cargoflow_plan())


# --- The pinned probe schedule ------------------------------------------------


def cargoflow_schedule() -> list[dict]:
    """The fixed fourteen read-only sample exchanges as staged plan rows.

    Order and offsets refuse drift (sample-00 at offset 0 first — the
    anchor latch — then every 5-day step through sample-13 at offset 65),
    and every row carries its own planned ladder offset. No
    mutation-capable op can enter a probe schedule: a foreign op is a
    staging error, never a run-time rejection that is benignly retried.
    """
    schedule: list[dict] = []
    for index, exchange in enumerate(CARGOFLOW_EXCHANGE_IDS):
        schedule.append(
            dict(
                exchange=exchange,
                op="sample",
                offset=int(CARGOFLOW_SAMPLE_OFFSETS[index]),
            )
        )
    ids = [row["exchange"] for row in schedule]
    if (
        ids != list(CARGOFLOW_EXCHANGE_IDS)
        or len(schedule) != PLANNED_CARGOFLOW_EXCHANGES
        or [row["offset"] for row in schedule] != list(CARGOFLOW_SAMPLE_OFFSETS)
        or schedule[0]["offset"] != 0
        or schedule[-1]["offset"] != CARGOFLOW_SPAN_DAYS
    ):
        raise CargoflowStagingError("the staged probe schedule drifted from the wire contract")
    if any(row["op"] not in CARGOFLOW_OPS for row in schedule):
        raise CargoflowStagingError("a probe schedule row carries a mutation-capable or foreign op")
    return schedule


def staged_cargoflow_schedule(policy: dict) -> list[dict]:
    """The staged schedule one plan-policy record binds its digest to.

    The probe has one schedule version and one derivation: a staged record
    naming a foreign version pairing is refused here before any schedule can
    be trusted.
    """
    if policy.get("schedule_version", 0) != 1:
        raise ValueError(
            f"plan record names an unknown cargo-dispatch schedule version: "
            f"{policy.get('schedule_version', 0)}"
        )
    return cargoflow_schedule()


# --- Hypotheses (retained census), never facts --------------------------------


def cargoflow_industry_hypotheses() -> dict:
    """The retained box-census industry rows re-bound as probe hypotheses.

    The consumed ``D5-BOX-CENSUS-2`` receipt (candidate-2) is the industry
    identity measurement of record on this same consumed depot-chain world:
    the pickup stop's discovery box measured exactly one member (industry 0,
    tile 44983, producing cargo 1 with last-month production 104) and the
    bay box measured exactly one member (industry 1, tile 51116, accepting
    cargo 1, the 15.3 non-producer fact ``p == -1`` verbatim, E65). The
    probe re-binds those identities as hypotheses only, never as expected
    values: the probe measures none of them fail-closed against the bound
    numbers — it records time series. Absent retained evidence (a fresh
    clone) is recorded as ``RETAINED_CENSUS_ABSENT`` — no hypothesis is
    invented.
    """
    receipt_path = (
        PROJECT / "artifacts/experiments/d5-box-census-native-candidate-2/receipt.json"
    )
    if not receipt_path.is_file():
        return dict(
            state="RETAINED_CENSUS_ABSENT",
            industries=[],
            statement=(
                "the retained census receipt of record is absent from this "
                "checkout; no hypothesis is invented and the probe proceeds "
                "without one"
            ),
        )
    receipt = json.loads(receipt_path.read_text())
    boxes = receipt.get("boxes")
    if not isinstance(boxes, dict):
        raise CargoflowStagingError("the retained census receipt lacks its box map")
    plan = cargoflow_pipeline_plan()
    centres = (
        (
            int(CARGOFLOW_PICKUP_TILE),
            int(plan.pickup_industry),
            "PRODUCING_PICKUP",
        ),
        (
            int(plan.delivery),
            int(plan.bay_industry),
            "ACCEPTING_BAY",
        ),
    )
    rows = []
    for centre, pinned_industry, role in centres:
        entry = boxes.get(str(centre))
        if not isinstance(entry, dict):
            raise CargoflowStagingError(
                f"the retained census receipt lacks a box row for stop {centre}"
            )
        members = entry.get("members")
        if not isinstance(members, list) or len(members) != 1:
            raise CargoflowStagingError(
                f"the retained census box {centre} does not carry exactly-one "
                "membership to re-bind"
            )
        member = members[0]
        if not isinstance(member, dict) or "id" not in member or "tile" not in member:
            raise CargoflowStagingError(
                f"the retained census box {centre} member lacks its identity"
            )
        if int(member["id"]) != pinned_industry:
            raise CargoflowStagingError(
                "the retained census identity drifted from the pinned probe "
                f"industries: box {centre} measured industry {member['id']}"
            )
        rows.append(
            dict(
                centre=centre,
                role=role,
                industry=int(member["id"]),
                tile=int(member["tile"]),
                production_units=int(member["p"]),
                accepted_state=int(member["a"]),
                exactly_one=bool(entry["exactly_one"]),
                kind="HYPOTHESIS",
            )
        )
    return dict(
        state="RETAINED_CENSUS_REBOUND",
        industries=rows,
        source="artifacts/experiments/d5-box-census-native-candidate-2/receipt.json",
        source_sha256=hashlib.sha256(receipt_path.read_bytes()).hexdigest(),
        statement=(
            "the industry identities of record are the retained census "
            "observations of record re-bound as hypotheses only; the probe "
            "measures time series, never bound values"
        ),
        derivation="corridor_cargoflow_native.cargoflow_industry_hypotheses",
    )


# --- The probe plan policy, budgets and readback story ------------------------


def _cargoflow_expected_world(plan: CargoFlowPlan) -> dict:
    """The expected world-pin set of the staged probe candidate."""
    return dict(
        pickup=int(plan.pickup),
        pickup_front=int(plan.pickup_front),
        delivery=int(plan.delivery),
        delivery_front=int(plan.delivery_front),
        depot=int(plan.depot),
        depot_front=int(plan.depot_front),
        company=plan.company,
        cargo=plan.cargo,
        pickup_sid=int(plan.pickup_sid),
        bay_sid=int(plan.bay_sid),
        pickup_industry=int(plan.pickup_industry),
        bay_industry=int(plan.bay_industry),
        expected_funds=plan.expected_funds,
        request_budget=plan.request_budget,
        sample_offsets=[int(offset) for offset in CARGOFLOW_SAMPLE_OFFSETS],
        statement=(
            "the staged probe world is the consumed depot-mutation attempt "
            "after-save (world-pin version 3): the corridor pickup stop, the "
            "A1 bay stop and the company depot with their pinned fronts, the "
            "pinned station and industry identities, and exact close-out "
            "funds at native admission time; the probe queries nothing else"
        ),
    )


def _cargoflow_sample_grid() -> dict:
    """The pinned sample geometry of record as a policy grid."""
    return dict(
        schema="d5-cargoflow-sample-grid-v1",
        planned_samples=PLANNED_CARGOFLOW_EXCHANGES,
        cadence_days=5,
        span_days=int(CARGOFLOW_SPAN_DAYS),
        offsets=[int(offset) for offset in CARGOFLOW_SAMPLE_OFFSETS],
        wait_ticks=int(CARGOFLOW_WAIT_MAX_TICKS),
        wait_day_cap=int(CARGOFLOW_WAIT_DAY_CAP),
        statement=(
            "the equality-gated sample ladder: the anchor latches once at "
            "sample-00 (offset 0), every later sample sleeps in-package "
            "until anchor + its exact offset, and overshoot, pause or tick "
            "regression fail closed; the 65-day span crosses at least two "
            "month boundaries of any OpenTTD calendar pair, so the "
            "≥2-boundaries property never depends on the saved world's "
            "calendar position"
        ),
    )


def cargoflow_plan_policy() -> dict:
    """The authorized read-only plan policy for the staged probe candidate."""
    plan = cargoflow_pipeline_plan()
    schedule = cargoflow_schedule()
    plan_digest = plan_digest_of(schedule)
    if (
        not schedule
        or schedule[0]["exchange"] != plan.schedule[0]
        or schedule[0]["offset"] != 0
        or schedule[0]["op"] != "sample"
    ):
        raise CargoflowStagingError("the probe schedule must begin with the anchor sample")
    expected_world = _cargoflow_expected_world(plan)
    return dict(
        company=plan.company,
        target_tile=int(CARGOFLOW_PICKUP_TILE),
        max_cost=0,
        command="none",
        command_statement=(
            "the staged probe contains no mutation-capable command of any "
            "kind; building, orders, purchases, vehicles, saves and any "
            "cost-bearing operation are outside this candidate forever"
        ),
        stale_rule=(
            "each sample re-observes its pinned identity immediately before "
            "its dispatch inside the handler; any mismate stops the phase "
            "without any command and preserves the verified prefix"
        ),
        identity=(
            "wire contract protocol 10: every exchange presents one uniform "
            "prelaunch seal digest; the probe records time-series "
            "measurements only (one read-only session, one company, zero "
            "commands)"
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
        hypotheses=cargoflow_industry_hypotheses(),
        sample_grid=_cargoflow_sample_grid(),
        world=expected_world,
        read_only=dict(
            schema="d5-cargoflow-readonly-v1",
            permitted_ops=list(CARGOFLOW_OPS),
            max_cost=0,
            funds_readback_required=True,
            statement=(
                "every exchange is a pure observation; a mutation-capable "
                "op cannot enter the schedule, the session surface or the "
                "replay, and no probe verdict re-opens a freight attempt"
            ),
        ),
    )


def cargoflow_budgets() -> dict:
    """The staged budget table for the probe candidate (no cost budget)."""
    plan = cargoflow_pipeline_plan()
    return dict(
        launches=1,
        connection_attempts=1,
        requests=CARGOFLOW_REQUEST_BUDGET,
        planned_exchanges=PLANNED_CARGOFLOW_EXCHANGES,
        gsadmin_bytes=MAX_CARGOFLOW_REQUEST_BYTES,
        response_bytes=MAX_CARGOFLOW_RESPONSE_BYTES,
        retries=0,
        reconnects=0,
        readiness_seconds=45,
        request_seconds=10,
        watch_seconds=freight_native.FREIGHT_WATCH_WALL_SECONDS,
        exchange_margin_seconds=CARGOFLOW_EXCHANGE_MARGIN_SECONDS,
        watch_ticks=int(CARGOFLOW_WAIT_MAX_TICKS),
        wait_day_cap=int(CARGOFLOW_WAIT_DAY_CAP),
        total_seconds=900,
        max_cost=0,
        expected_funds=int(plan.expected_funds),
    )


def cargoflow_expected_readback_policy() -> dict:
    return dict(
        sample=(
            "each sample exchange sleeps in-package to its exact planned "
            "ladder day and then returns READY with the complete "
            "observation set of record: the latched anchor, the clock "
            "facts (tick, day, year, month, day-of-month), both industry "
            "stockpiles, the waiting and planned families at both pinned "
            "stops (totals plus the pickup/bay-sourced forms), and the "
            "monthly production and transported levels of both industries; "
            "native fact families ride verbatim (the 15.3 -1 facts), and "
            "any other unsupported fact refuses the exchange terminally"
        ),
        ladder=(
            "the ladder is exact: a sample's day minus its latched anchor "
            "must equal its pinned offset both in the handler and on the "
            "Python side; an overshoot is WINDOW_EXHAUSTED and a later "
            "anchor drift is a phase halt with the prefix preserved"
        ),
        funds=(
            "every READY sample echoes the bank balance exactly at the "
            "close-out funds pin: the probe has no fleet, no purchase and "
            "no running cost, so a drifted balance halts the phase at that "
            "sample"
        ),
        verdicts=(
            "the probe reports a time-series record, not a success/failure "
            "verdict: pickup waiting rose → DISPATCH_OBSERVED_LATE; a "
            "measured stockpile rose while pickup waiting never rose → "
            "DISPATCH_REFUSED_AT_SELECTOR; neither rose → "
            "DISPATCH_STOCKPILE_STATIC; an unobserved or unfinished ladder "
            "decides CARGOFLOW_GATE_UNDECIDED_INCOMPLETE"
        ),
        receipt=(
            "CARGOFLOW_COMPLETE only after all fourteen samples verify in "
            "execution order with certified cleanup; a refused, missing, "
            "malformed, out-of-order, stale, divergent or inconclusive "
            "observation leaves the probe incomplete forever"
        ),
    )


# --- Probe prerequisite binding (depot lineage re-scoped) --------------------


def cargoflow_prerequisite_binding(prerequisite: Path | None = None) -> dict:
    """Bind the consumed depot-mutation attempt of record, probe-scoped.

    The probe prerequisite is exactly the freight v2 prerequisite: the
    pinned, consumed, fully replay-verified depot-mutation attempt at its
    retained after-save digest, with the verified observe-only reload chain
    embedded. The checked derivation of record is the freight v2 binding's
    own (``freight_v2_native.prerequisite_binding``); this wrapper only
    scope-checks the pinned directory against the probe pins and re-labels
    the recorded verification statement for the probe lineage. A wrong
    directory is a probe staging error before any world is staged.
    """
    prerequisite = Path(
        PINNED_PREREQUISITE if prerequisite is None else prerequisite
    ).resolve()
    if prerequisite != freight_v2_native.DEPOT_PREREQUISITE:
        raise CargoflowStagingError("the probe source world requires the pinned depot prerequisite")
    try:
        binding = freight_v2_native.prerequisite_binding(prerequisite)
    except freight_v2_native.FreightV2StagingError as error:
        raise CargoflowStagingError(str(error)) from None
    if binding.get("schema") != D5_CARGOFLOW_PREREQUISITE_SCHEMA:
        raise CargoflowStagingError("the probe prerequisite schema drifted from the depot lineage")
    if Path(binding["retained_directory"]).resolve() != prerequisite:
        raise CargoflowStagingError(
            "the probe prerequisite binding is not the pinned retained attempt"
        )
    return dict(
        binding,
        verification=(
            "full replay verification of the consumed depot-mutation attempt "
            "receipt (F12_MUTATION_COMPLETION_VERIFIED) plus the pinned "
            "authoritative after-save digest and the verified observe-only "
            "reload chain (probe-scoped binding of the shared freight v2 "
            "derivation of record)"
        ),
    )


# --- Probe candidate staging --------------------------------------------------


def staged_cargoflow_composition() -> tuple[dict[str, bytes], str, int]:
    """Byte-exact save-restore composition for the D5 dispatch probe.

    The retained staged ``info.nut`` announces the save's stored GameScript
    identity (name/version); the staged main is the read-only probe handler
    of its own package directory (``d5_cargoflow_package``) with the
    save-restore bridge class defined inline after the proof class. No
    frozen package byte drifts for the probe's sake.
    """
    with zipfile.ZipFile(SEED17_RUN / "frozen-source.zip") as archive:
        info_bytes = archive.read("staged/info.nut")
    text = info_bytes.decode()
    create_instance = re.search(r'CreateInstance\(\)\s*\{\s*return\s+"([^"]+)"', text)
    version = re.search(r"GetVersion\(\)\s*\{\s*return\s+(\d+)", text)
    if create_instance is None or version is None or SOURCE_SAVE_GS_NAME not in text:
        raise CargoflowStagingError("retained staged GameScript identity incomplete")
    main_text = (CARGOFLOW_PACKAGE / "main.nut").read_text()
    bridge_class = create_instance.group(1)
    expected_bridge = f"class {bridge_class} extends D5CargoFlowProof"
    if expected_bridge not in main_text:
        raise CargoflowStagingError(
            f"staged probe main.nut missing required bridge class {bridge_class}"
        )
    return (
        {
            "info.nut": info_bytes,
            "main.nut": (CARGOFLOW_PACKAGE / "main.nut").read_bytes(),
        },
        bridge_class,
        int(version.group(1)),
    )


def prepare_cargoflow_candidate(
    directory: Path, *, prerequisite: Path | None = None
) -> PreparedProof:
    """Stage the fresh save-load composition; no process or connection."""
    plan = _require_cargoflow_plan(cargoflow_plan())
    prerequisite = Path(PINNED_PREREQUISITE if prerequisite is None else prerequisite).resolve()
    if prerequisite != PINNED_PREREQUISITE:
        raise CargoflowStagingError("the probe source world requires the pinned depot prerequisite")
    schedule = cargoflow_schedule()
    policy = cargoflow_plan_policy()
    if len(schedule) != len(plan.schedule):
        raise CargoflowStagingError("the scheduled probe samples drifted")
    if policy["schedule_version"] != 1:
        raise CargoflowStagingError("the staged probe schedule derivation drifted")
    if sha256(BINARY) != BINARY_SHA256 or matching_processes(BINARY):
        raise CargoflowStagingError("pinned binary / exclusive runtime gate failed")
    directory = directory.resolve()
    binding = cargoflow_prerequisite_binding(prerequisite)
    welcome = binding["expected_welcome"]
    world = stage_world(binding, welcome)
    if sha256(source_save_path(world)) != world["save_sha256"]:
        raise CargoflowStagingError("the staged source-save digest mismatch")
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
        composition, create_instance, version = staged_cargoflow_composition()
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
        for source in (CARGOFLOW_PACKAGE, AI_PACKAGE):
            for path in sorted(source.glob("*.nut")):
                frozen[str(path.resolve())] = sha256(path)
        frozen.update(
            {
                str(path): sha256(path)
                for path in sorted(workspace.root.rglob("*"))
                if path.is_file() and path.name != ".admin-secret"
            }
        )
        frozen.update(freight_native.d2_source_closure(CARGOFLOW_CLOSURE_ROOT))
        frozen.update(freight_native.d2_dependency_inventory(CARGOFLOW_CLOSURE_ROOT))
        prepared = PreparedProof(
            directory,
            spec,
            key_path,
            key.public_hex,
            (reservation.game_port, reservation.admin_port),
        )
        metadata = dict(
            schema=D5_CARGOFLOW_PRELAUNCH_SCHEMA,
            milestone=MILESTONE_CARGOFLOW,
            kind=KIND,
            attempt=CARGOFLOW_ATTEMPT,
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
                    "GameScript name/version; the read-only protocol-10 "
                    "D5CargoFlowProof ships in its own bounded package "
                    "(d5_cargoflow_package) and satisfies the frozen "
                    "save-restore identity through its bridge class, with "
                    "zero company commands anywhere in its plan"
                ),
            ),
            save_policy=(
                "owned session-before.sav and after-diagnostic.sav only; the "
                "authoritative source save, the prerequisite attempt record "
                "and every historical artifact stay untouched; the probe "
                "saves nothing itself and mutates nothing"
            ),
            plan_policy=policy,
            expected_readback=cargoflow_expected_readback_policy(),
            bootstrap_command=f"start_ai {STAGED_AI_DIRECTORY}",
            execution_command=[
                str(PROJECT / ".venv/bin/python"),
                "-m",
                "app.simulation.openttd.proof.corridor_cargoflow_native",
                "run",
                str(directory),
            ],
            budgets=cargoflow_budgets(),
            cleanup=[
                "close secure session",
                "quit and reap process",
                "verify endpoints",
                "retain session logs and the pre-probe save",
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
                source=int(CARGOFLOW_PICKUP_TILE),
                manifest_verified=True,
                statement=(
                    "the probe binds the authoritative depot-mutation "
                    "after-save (183b20273a54ebe1a2cd9306145a9ea820bbd6114"
                    "b1608c42079b4e1b1efe6a6, world-pin version 3) with its "
                    "verified reload chain, and the pinned OpenTTD 15.3 "
                    "binary; the pinned fourteen-sample schedule is the "
                    "contract module's own guarded derivation"
                ),
            ),
            environment=freight_native.launch_environment(prepared),
            environment_overrides=dict(spec.environment),
            frozen=frozen,
            cross_schedule_guard=dict(
                schema="d5-cargoflow-cross-guard-v1",
                cargoflow_ops=list(CARGOFLOW_OPS),
                statement=(
                    "this candidate refuses every mutation-capable op: a "
                    "freight request (any protocol-5/8 op) fails the probe "
                    "session schema check with protocol 10 required, a "
                    "survey or census request fails it the same way, and "
                    "any probe request fails the freight, survey and census "
                    "session checks with their required protocols 5/6/8/9"
                ),
            ),
        )
        metadata["prerequisite"] = dict(
            schema=D5_CARGOFLOW_PREREQUISITE_SCHEMA,
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


# --- Probe preflight (offline launch-boundary rehearsal) ---------------------


def cargoflow_preflight(prepared: PreparedProof) -> dict:
    """Offline launch-boundary rehearsal: re-derive every binding, trust nothing.

    The probe has one schedule version and one plan; every derivation below
    is re-derived from the module pins and the staged record must match it
    exactly, so a record claiming a foreign lineage or a drifted schedule is
    refused here.
    """
    directory = prepared.directory
    if sha256(directory / "PRELAUNCH.json") != (directory / "PRELAUNCH.sha256").read_text().strip():
        raise ValueError("the probe prelaunch seal mismatch")
    metadata = read_prelaunch(directory)
    if (directory / "CLAIM.json").exists():
        raise ValueError("the one native attempt already consumed")
    if metadata.get("schema") != D5_CARGOFLOW_PRELAUNCH_SCHEMA:
        raise ValueError("the staged prelaunch record is not the D5 cargoflow lineage")
    if metadata.get("kind") != KIND or metadata.get("milestone") != MILESTONE_CARGOFLOW:
        raise ValueError("the staged probe lineage drifted")
    if metadata.get("attempt") != CARGOFLOW_ATTEMPT:
        raise ValueError("the staged attempt identity drifted from its own scope")
    verify_freeze(metadata["frozen"])
    freight_native.require_frozen_d2_closure(metadata["frozen"], CARGOFLOW_CLOSURE_ROOT)
    freight_native.require_frozen_d2_dependencies(metadata["frozen"], CARGOFLOW_CLOSURE_ROOT)
    policy = metadata["plan_policy"]
    plan = cargoflow_pipeline_plan()
    schedule = staged_cargoflow_schedule(policy)
    if policy["schedule"] != schedule or policy["plan_digest"] != plan_digest_of(schedule):
        raise ValueError("the staged probe schedule drifted from the compiled derivation")
    if policy["plan_model_digest"] != plan.digest:
        raise ValueError("the staged probe plan digest drifted from the pinned plan")
    if policy.get("schedule_version") != 1:
        raise ValueError("the staged probe schedule version drifted")
    for row in schedule:
        if row["op"] not in CARGOFLOW_OPS:
            raise ValueError("a scheduled probe row carries a mutation-capable or foreign op")
        expected_offset = CARGOFLOW_SAMPLE_OFFSETS[CARGOFLOW_EXCHANGE_IDS.index(row["exchange"])]
        if row["offset"] != expected_offset:
            raise ValueError("a scheduled probe row drifted from its pinned ladder offset")
    if policy.get("max_cost") != 0:
        raise ValueError("the staged probe must budget zero cost")
    if policy["read_only"]["schema"] != "d5-cargoflow-readonly-v1":
        raise ValueError("the staged probe read-only schema drifted")
    if policy["read_only"]["permitted_ops"] != list(CARGOFLOW_OPS):
        raise ValueError("the staged probe's read-only op set drifted")
    expected_world = _cargoflow_expected_world(plan)
    for name, expected in expected_world.items():
        if policy["world"].get(name) != expected:
            raise ValueError(f"the staged probe world pin {name} drifted")
    if policy["target_tile"] != int(CARGOFLOW_PICKUP_TILE):
        raise ValueError("the staged probe control tile drifted")
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
        raise ValueError("the staged probe observation kinds drifted")
    if policy["sample_grid"] != _cargoflow_sample_grid():
        raise ValueError("the staged probe sample grid drifted from the pinned geometry")
    staged_hypotheses = policy["hypotheses"]
    expected_hypotheses = cargoflow_industry_hypotheses()
    if staged_hypotheses.get("state") != expected_hypotheses.get("state"):
        raise ValueError(
            f"the staged probe hypothesis state is not its own derivation "
            f"({expected_hypotheses.get('state')})"
        )
    if expected_hypotheses.get("state") == "RETAINED_CENSUS_REBOUND":
        if staged_hypotheses != expected_hypotheses:
            raise ValueError("the staged probe hypothesis record drifted from the retained bytes")
    if metadata.get("budgets") != cargoflow_budgets():
        raise ValueError("the staged probe budget pins drifted")
    if metadata["public_key"] != prepared.public_key or metadata["binary_sha256"] != BINARY_SHA256:
        raise ValueError("the staged identity pins drifted")
    binding = cargoflow_prerequisite_binding(Path(metadata["prerequisite"]["directory"]))
    required = ("attempt", "milestone", "directory", "prelaunch_sha256", "after_save_sha256")
    if {name: metadata["prerequisite"][name] for name in required} != dict(
        attempt=binding["attempt"],
        milestone=binding["milestone"],
        directory=binding["retained_directory"],
        prelaunch_sha256=binding["prelaunch_digest"],
        after_save_sha256=binding["save_sha256"],
    ):
        raise ValueError("the staged prerequisite binding drifted from its verified record")
    if metadata["prerequisite"].get("schema") != D5_CARGOFLOW_PREREQUISITE_SCHEMA:
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
    composition, _, _ = staged_cargoflow_composition()
    staged_identity = Path(metadata["workspace"]) / "game" / SOURCE_SAVE_GS_NAME
    if staged_identity.joinpath("info.nut").read_bytes() != composition["info.nut"]:
        raise ValueError("the staged GameScript identity drifted from the retained composition")
    if staged_identity.joinpath("main.nut").read_bytes() != composition["main.nut"]:
        raise ValueError("the staged probe handler drifted from its bounded package")
    if not prepared.spec.workspace.root.is_relative_to(directory / "isolated"):
        raise ValueError("the workspace ownership mismatch")
    ClearingNativeBackend(authorized_one_launch=True).preflight(prepared)
    reservation = EndpointReservation.allocate(*prepared.endpoints)
    reservation.close()
    return metadata


# --- Wire protocol 10: secure session and one-launch backend -----------------


def encode_cargoflow_request(payload: bytes) -> bytes:
    return encode_gamescript(payload, max_payload_bytes=MAX_CARGOFLOW_REQUEST_BYTES)


def decode_cargoflow_request(payload: bytes) -> bytes:
    return decode_gamescript(payload, max_payload_bytes=MAX_CARGOFLOW_REQUEST_BYTES)


class CargoflowSecureSession(SecureAdminSession):
    """Only the probe operations extend the secure write policy.

    A freight request cannot parse as a CargoFlowRequest (protocol 10
    required, and the freight/survey/census op sets are outside the probe
    Literal), so no foreign protocol exchange can travel on the probe
    session; a probe request parses on none of the older sessions for the
    mirrored reason.
    """

    def validate_outbound(self, frame: bytes) -> None:
        if self.state is not AuthState.ACTIVE:
            raise ValueError("encrypted ACTIVE stream required")
        if len(frame) < 3 or struct.unpack_from("<H", frame)[0] != len(frame):
            raise ValueError("invalid frame")
        if frame[2] == ADMIN_GAMESCRIPT:
            request = CargoFlowRequest.model_validate_json(decode_cargoflow_request(frame[3:]))
            if request.op not in CARGOFLOW_OPS:
                raise ValueError("a mutation-capable op cannot ride the probe session")
            request.to_bytes()
        elif frame not in (gamescript_subscription(), encode_admin_quit()):
            super().validate_outbound(frame)


class CargoflowNativeBackend(freight_native.FreightNativeBackend):
    """One-launch backend carrying the shared consumed marker, probe session."""

    launch_marker_schema = D5_CARGOFLOW_LAUNCH_CONSUMED_SCHEMA

    async def connect(self, prepared: PreparedProof, *, frame_observer) -> CargoflowSecureSession:
        if not any(
            r["table"] == "tcp" and r["local_port"] == prepared.endpoints[1] and r["state"] == 10
            for r in kernel_socket_rows()
        ):
            raise ValueError("the native Admin listener readiness absent")
        key = AuthorizedKey.from_bytes(prepared.key_path.read_bytes())
        session = await CargoflowSecureSession.connect_secure(
            "127.0.0.1",
            prepared.endpoints[1],
            5,
            key=key,
            frame_observer=frame_observer,
        )
        self.session = session
        return session


def cargoflow_exchange_timeout_seconds(*, budget_table: dict, offset: int) -> float:
    """Sample-00 is a bounded immediate request/readback; every later sample
    may legitimately spend its in-package ladder wait, so it gets the
    freight-window wall clock plus the shared client margin. The offset-0
    anchor latch is immediate by construction (the loaded world's own clock
    at admission time) and stays on the plain request budget."""
    if not 0 <= int(offset) <= max(CARGOFLOW_SAMPLE_OFFSETS):
        raise ValueError("no probe budget exists for a foreign ladder offset")
    if int(offset) == 0:
        return float(budget_table["request_seconds"])
    return float(budget_table["watch_seconds"]) + float(budget_table["exchange_margin_seconds"])


def event_loop_deadline(seconds: float) -> float:
    return time.monotonic() + seconds


def _cargoflow_exchange_request(entry: dict, seal: str, plan: CargoFlowPlan) -> CargoFlowRequest:
    """Build one fixed probe request: pins, zero cost, its pinned offset."""
    return CargoFlowRequest(
        op="sample",
        request_id=entry["exchange"],
        plan=seal,
        company=plan.company,
        max_cost=0,
        pickup=int(plan.pickup),
        delivery=int(plan.delivery),
        depot=int(plan.depot),
        offset=int(entry["offset"]),
    )


async def cargoflow_exchange(
    session,
    request: CargoFlowRequest,
    directory: Path,
    *,
    budget_table: dict | None = None,
    overall_deadline: float | None = None,
    clock=time.monotonic,
    timeout_factory=asyncio.timeout,
) -> CargoFlowReadback:
    """One sealed protocol-10 sample exchange; every frame and file retained.

    Bounded request bytes, the ladder-offset timeout clamped to the overall
    attempt budget, duplicate/stale frame refusal and fail-closed parsing —
    the probe twin of the census exchange, over the 512/1400-byte protocol-10
    bounds.
    """
    budget_table = budget_table if budget_table is not None else cargoflow_budgets()
    permitted = cargoflow_exchange_timeout_seconds(
        budget_table=budget_table, offset=request.offset
    )
    if overall_deadline is not None:
        remaining = overall_deadline - clock()
        if remaining <= 0:
            raise TimeoutError("the probe attempt overall budget exhausted")
        permitted = min(permitted, remaining)
    raw = request.to_bytes()
    (directory / (request.request_id + "-request.json")).write_bytes(raw)
    await session.send(encode_cargoflow_request(raw))
    decoder = AdminFrameDecoder()
    try:
        async with timeout_factory(permitted):
            while True:
                chunk = await session.receive()
                if not chunk:
                    raise ConnectionError("the probe stream disconnected")
                game_frames = []
                for kind, payload in decoder.feed_frames(chunk):
                    if kind != SERVER_GAMESCRIPT:
                        raise ValueError("an unexpected probe packet")
                    game_frames.append(payload)
                if len(game_frames) > 1:
                    raise ValueError("a duplicate probe response frame")
                if game_frames:
                    body = game_frames[0]
                    if (directory / (request.request_id + "-response.json")).exists():
                        raise ValueError("a duplicate probe response file")
                    response = decode_gamescript(
                        body, max_payload_bytes=MAX_CARGOFLOW_RESPONSE_BYTES
                    )
                    readback = CargoFlowReadback.parse_for(request, response)
                    (directory / (request.request_id + "-response.json")).write_bytes(response)
                    return readback
    except TimeoutError:
        raise TimeoutError(
            f"the probe sample {request.request_id} exceeded its {permitted:.1f}s budget"
        ) from None


# --- Probe execution (authorized one-attempt path only) ----------------------


def apply_cargoflow_cleanup_outcome(result: dict, *, complete: bool) -> None:
    """Fail closed on the probe's final cleanup verdict."""
    result["cleanup_complete"] = bool(complete)
    if complete:
        return
    result["cleanup_failure"] = True
    if result.get("verified") is True or result.get("status") == "NATIVE_CARGOFLOW_COMPLETE":
        freight_native.deny_verification(
            result,
            status="FAILED_CLEANUP",
            message=(
                "ValueError: cleanup was not certified; no verified probe completion is possible"
            ),
        )


async def execute_cargoflow_attempt(prepared: PreparedProof, backend) -> dict:
    """Execute the authorized one-attempt probe phase (never offline).

    One launch, one connection, the staged schedule's read-only samples in
    the pinned ladder order, every sample verified against the accumulated
    probe state by the production ``cargoflow_phase_outcome``; the first
    verification failure halts the phase prefix-preservingly, and cleanup is
    certified before any completion verdict can stand.
    """
    directory = prepared.directory
    cargoflow_preflight(prepared)
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
    plan = cargoflow_pipeline_plan()
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
    exchanges: list[tuple[CargoFlowRequest, CargoFlowReadback]] = []
    overall_deadline = event_loop_deadline(metadata["budgets"]["total_seconds"])
    try:
        async with asyncio.timeout(metadata["budgets"]["total_seconds"]):
            await backend.launch(prepared, authorization=grant)
            result["native_launches"] = 1
            await wait_log(backend, prepared, CARGOFLOW_READY_MARKER)
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
                    request = _cargoflow_exchange_request(entry, seal, plan)
                    if request.op not in CARGOFLOW_OPS:
                        raise ValueError("a mutation-capable op cannot enter the probe run")
                    verify_request_against_cargoflow_plan(request, plan=plan, seal=seal)
                    readback = await cargoflow_exchange(
                        session,
                        request,
                        directory,
                        budget_table=metadata["budgets"],
                        overall_deadline=overall_deadline,
                    )
                    result["requests"] += 1
                    probe = cargoflow_phase_outcome(
                        exchanges + [(request, readback)], prelaunch_digest=seal, plan=plan
                    )
                    if probe["failed"] is not None:
                        raise ValueError(
                            f"the probe sample {label} failed verification: "
                            f"{probe['failed']['error']}"
                        )
                    exchanges.append((request, readback))
                    result["exchanges"].append(label)
                    result["last_status"] = readback.status
                    result["command_accepted"] = True
                    result["state_changed"] = False  # the probe mutates nothing
                except Exception as error:
                    result["halt"] = dict(
                        label=label, error=type(error).__name__ + ": " + str(error)
                    )
                    break
            phase = cargoflow_phase_outcome(exchanges, prelaunch_digest=seal, plan=plan)
            result["phase"] = phase
            if phase["verification"] == "CARGOFLOW_COMPLETE":
                if len(exchanges) != len(plan.schedule):
                    raise ValueError(
                        "the probe completion evidence drifted from the staged schedule"
                    )
                if phase["anchor"] is None or not phase["samples"]:
                    raise ValueError(
                        "the native anchor latch or the sampled series is missing"
                    )
                write_json(
                    directory / "receipt.json",
                    dict(
                        phase,
                        before_save_sha256=before_save,
                    ),
                )
                result["verified"] = True
                result["status"] = "NATIVE_CARGOFLOW_COMPLETE"
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
            if result["status"] == "NATIVE_CARGOFLOW_COMPLETE":
                freight_native.deny_verification(
                    result,
                    status="FAILED",
                    message=(
                        "ValueError: the retained script log health findings "
                        "deny the verified probe completion"
                    ),
                )
        if result["returncode"] not in (None, 0):
            if result["status"] == "NATIVE_CARGOFLOW_COMPLETE":
                freight_native.deny_verification(
                    result,
                    status="FAILED",
                    message=(
                        "ValueError: the native runtime exited abnormally after "
                        f"the probe (return code {result['returncode']})"
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
        apply_cargoflow_cleanup_outcome(result, complete=cleanup_complete)
        write_json(directory / "cleanup.json", cleanup)
        write_json(directory / "result.json", result)
        (directory / "artifact-manifest.sha256").write_text(manifest(directory))
    return result


# --- Probe replay verification ------------------------------------------------


def _parse_cargoflow_frames(directory: Path):
    """Parse the retained frame stream of the owned secure probe session."""
    frames = json.loads((directory / "frames.json").read_text())
    outbound: list[bytes] = []
    replies: list[bytes] = []
    outbound_requests: list[CargoFlowRequest] = []
    request_positions: dict[bytes, int] = {}
    reply_positions: dict[bytes, int] = {}
    for index, (direction, frame_hex) in enumerate(frames):
        frame = bytes.fromhex(frame_hex)
        if direction == "outbound":
            outbound.append(frame)
            if frame[2] != ADMIN_GAMESCRIPT:
                continue
            payload = decode_cargoflow_request(frame[3:])
            try:
                query = CargoFlowRequest.model_validate_json(payload)
            except Exception:
                raise ValueError("an outbound frame contains an invalid CargoFlowRequest") from None
            outbound_requests.append(query)
            request_positions[payload] = index
        else:
            for kind, body in AdminFrameDecoder().feed_frames(frame):
                if kind != SERVER_GAMESCRIPT:
                    continue
                reply = decode_gamescript(body, max_payload_bytes=MAX_CARGOFLOW_RESPONSE_BYTES)
                if reply not in reply_positions:
                    reply_positions[reply] = index
                replies.append(reply)
    return outbound, outbound_requests, replies, request_positions, reply_positions


def verify_cargoflow_attempt_identity(metadata: dict, *, plan) -> dict:
    """Re-bind one retained probe attempt to its pinned prerequisite and plan.

    Replay never trusts the staged record's own declarations: the lineage
    (attempt/schema/prerequisite/world) is re-derived from the module's
    single pinned identity, the pinned depot prerequisite is re-verified,
    and the source-save digest, welcome, schedule, plan digests, read-only
    scope, sample grid and probe hypotheses are all re-derived. A foreign
    lineage or a drifted pin refuses.
    """
    if metadata.get("attempt") != CARGOFLOW_ATTEMPT:
        raise ValueError("the retained attempt identity drifted from the staged scope")
    if (
        metadata.get("schema") != D5_CARGOFLOW_PRELAUNCH_SCHEMA
        or metadata.get("kind") != KIND
        or metadata.get("milestone") != MILESTONE_CARGOFLOW
    ):
        raise ValueError("the retained attempt is not the D5 cargoflow lineage")
    staged_prerequisite = metadata.get("prerequisite")
    if not isinstance(staged_prerequisite, dict):
        raise ValueError("the retained attempt lacks its prerequisite binding")
    binding = cargoflow_prerequisite_binding(Path(staged_prerequisite.get("directory", "")))
    expected_prerequisite = dict(
        schema=D5_CARGOFLOW_PREREQUISITE_SCHEMA,
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
    _require_cargoflow_plan(plan)
    policy = metadata.get("plan_policy")
    if not isinstance(policy, dict):
        raise ValueError("the retained attempt lacks its plan policy")
    schedule = staged_cargoflow_schedule(policy)
    if policy.get("schedule") != schedule or policy.get("plan_digest") != plan_digest_of(schedule):
        raise ValueError("the retained probe schedule drifted from the compiled derivation")
    if policy.get("plan_model_digest") != plan.digest:
        raise ValueError("the retained plan digest drifted from the pinned probe plan")
    if policy.get("schedule_version") != 1:
        raise ValueError("the retained schedule version drifted")
    if metadata.get("budgets") != cargoflow_budgets():
        raise ValueError("the retained budget contract drifted")
    if policy.get("max_cost") != 0:
        raise ValueError("the retained budget floated off the zero-cost contract")
    if policy.get("read_only", {}).get("schema") != "d5-cargoflow-readonly-v1":
        raise ValueError("the retained read-only schema drifted")
    if policy["read_only"]["permitted_ops"] != list(CARGOFLOW_OPS):
        raise ValueError("the retained read-only op set drifted")
    world_pins = policy.get("world")
    if not isinstance(world_pins, dict):
        raise ValueError("the retained plan policy lacks its world pins")
    expected_pins = _cargoflow_expected_world(plan)
    for name, expected in expected_pins.items():
        if world_pins.get(name) != expected:
            raise ValueError(f"the retained probe world pin {name} drifted")
    if (
        policy.get("company") != plan.company
        or policy.get("target_tile") != int(CARGOFLOW_PICKUP_TILE)
        or policy.get("plan_model_digest") != plan.digest
    ):
        raise ValueError("the retained probe plan pins drifted")
    if policy.get("sample_grid") != _cargoflow_sample_grid():
        raise ValueError("the retained probe sample grid drifted from the pinned geometry")
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
        raise ValueError("the retained probe observation kinds drifted")
    staged_hypotheses = policy.get("hypotheses")
    expected_hypotheses = cargoflow_industry_hypotheses()
    if (
        not isinstance(staged_hypotheses, dict)
        or staged_hypotheses.get("state") != expected_hypotheses.get("state")
    ):
        raise ValueError(
            f"the retained probe hypothesis record drifted from its version derivation "
            f"({expected_hypotheses.get('state')})"
        )
    return binding


def verify_cargoflow_attempt(directory: Path) -> dict:
    """Replay the retained protocol-10 phase; never trust a success label.

    The replay re-derives every retained fact independently — operator
    authorization evidence, the staged probe schedule, the captured session
    frames, every per-sample request/response pair — then re-verifies the
    whole ladder with the production
    :func:`app.simulation.openttd.corridor_cargoflow.cargoflow_phase_outcome`
    and the certified-cleanup gate. A forced or invented
    ``CARGOFLOW_COMPLETE`` label alone can never verify; a refused, missing,
    malformed, out-of-order, stale, divergent or inconclusive sample always
    leaves the verdict incomplete.
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
                "the probe candidate was never consumed by an operator "
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
    if metadata.get("schema") != D5_CARGOFLOW_PRELAUNCH_SCHEMA:
        return dict(
            verification="AUTHORIZATION_UNVERIFIED",
            authorization_state="UNKNOWN_PRELAUNCH_SCHEMA",
            statement=(
                f"the prelaunch record is not the launch-capable "
                f"[{D5_CARGOFLOW_PRELAUNCH_SCHEMA!r}] lineage; no verified "
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
    schedule = staged_cargoflow_schedule(policy_replay)
    plan = cargoflow_pipeline_plan()
    if policy_replay["schedule"] != schedule or policy_replay["plan_digest"] != plan_digest_of(
        schedule
    ):
        raise ValueError("the staged probe schedule drifted from the compiled derivation")
    planned_ids = {row["exchange"] for row in schedule}
    if planned_ids != set(CARGOFLOW_EXCHANGE_IDS) or len(schedule) != PLANNED_CARGOFLOW_EXCHANGES:
        raise ValueError("the retained probe schedule drifted from the wire contract")
    verify_cargoflow_attempt_identity(metadata, plan=plan)
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
        _parse_cargoflow_frames(directory)
    )
    if len(outbound_requests) > metadata["budgets"]["requests"]:
        raise ValueError("the probe request budget exceeded (outbound frames)")
    paths = sorted(directory.glob("*-request.json"))
    file_queries = [CargoFlowRequest.model_validate_json(path.read_bytes()) for path in paths]
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
            raise ValueError(f"a duplicate probe request_id: {query.request_id}")
        seen_ids.add(query.request_id)
    response_map = {}
    for path in paths:
        response_path = path.with_name(path.name.replace("-request.json", "-response.json"))
        if response_path.is_file():
            response_map[path.read_bytes()] = response_path.read_bytes()
    for path in sorted(directory.glob("*-response.json")):
        exchange_id = path.name[: -len("-response.json")]
        try:
            readback = CargoFlowReadback.model_validate_json(path.read_bytes())
        except ValueError as error:
            raise ValueError(
                f"the retained response file is not a parseable readback: {path.name}"
            ) from error
        if readback.request_id != exchange_id:
            raise ValueError("the retained response file identity does not match its payload")
        if not (directory / (exchange_id + "-request.json")).is_file():
            raise ValueError("the retained response file lacks its request")
    for raw, response in response_map.items():
        if outbound.count(encode_cargoflow_request(raw)) != 1 or replies.count(response) != 1:
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
    exchanges: list[tuple[CargoFlowRequest, CargoFlowReadback]] = []
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
            query = CargoFlowRequest.model_validate_json(request_path.read_bytes())
            raw = response_map.get(query.to_bytes())
            if raw is not None:
                exchanges.append((query, CargoFlowReadback.parse_for(query, raw)))
        if pending:
            break
    phase = cargoflow_phase_outcome(exchanges, prelaunch_digest=seal, plan=plan)
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
    if result["status"] == "NATIVE_CARGOFLOW_COMPLETE":
        if phase["verification"] != "CARGOFLOW_COMPLETE":
            raise ValueError("the verified completion contradicts its probe phase outcome")
        if result.get("halt") is not None or not result.get("command_accepted"):
            raise ValueError("the verified completion contradicts its retained attempt record")
        if (result.get("native_launches"), result.get("connections")) != (
            metadata["budgets"]["launches"],
            metadata["budgets"]["connection_attempts"],
        ):
            raise ValueError("the verified completion contradicts its launch seal")
        if len(result.get("exchanges", [])) != len(plan.schedule) or not cleanup_complete:
            raise ValueError("the verified completion's cleanup or exchange inventory incomplete")
        if result.get("state_changed", False) is not False:
            raise ValueError("the probe claimed a world change it cannot make")
        if len(outbound_requests) != len(plan.schedule):
            raise ValueError("the verified completion's request inventory drifted")
        if phase["anchor"] is None or not phase["samples"]:
            raise ValueError("the verified completion lacks its own re-derived ladder evidence")
        if len(phase["samples"]) != len(plan.schedule):
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
                raise ValueError("the retained probe receipt replay mismatch")
            session_before = json.loads(
                (directory / "session-before-identity.json").read_text()
            ).get("sha256")
            if retained_receipt.get("before_save_sha256") != session_before:
                raise ValueError("the retained probe receipt replay mismatch")
        return dict(
            verification="CARGOFLOW_COMPLETION_VERIFIED",
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
            phase["verification"] != "CARGOFLOW_INCOMPLETE"
            or not isinstance(halt_record, dict)
            or len(result.get("exchanges", [])) != len(phase["receipts"])
            or (
                phase["failed"] is not None
                and phase["failed"].get("label") != halt_record.get("label")
            )
        ):
            raise ValueError("the halted probe evidence contradicts its retained record")
        if not cleanup_complete:
            raise ValueError("the halted probe attempt cleanup incomplete")
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


def staged_cargoflow_authorization_payload_digest(directory: Path) -> str:
    """The RFC-canonical digest of the candidate's own authorization payload."""
    directory = directory.resolve()
    metadata = read_prelaunch(directory)
    seal = sha256(directory / "PRELAUNCH.json")
    return hashlib.sha256(
        canonical_authorization_bytes(authorization_payload(metadata, seal))
    ).hexdigest()


def cargoflow_exit_status(result: dict) -> int:
    verified = (
        result.get("verified") is True
        and result.get("status") == "NATIVE_CARGOFLOW_COMPLETE"
        and result.get("cleanup_complete") is True
        and result.get("state_changed") is False
    )
    return 0 if verified else 1


def cargoflow_verdict_exit_status(verdict: dict) -> int:
    return 0 if verdict.get("verification") == "CARGOFLOW_COMPLETION_VERIFIED" else 1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("prepare", "preflight", "run", "verify"))
    parser.add_argument("directory", type=Path)
    parser.add_argument("--prerequisite", type=Path, default=PINNED_PREREQUISITE)
    args = parser.parse_args()
    directory = args.directory.resolve()
    if args.command == "prepare":
        prepared = prepare_cargoflow_candidate(directory, prerequisite=args.prerequisite)
        cargoflow_preflight(prepared)
        print("PRELAUNCH PASS", directory)
    elif args.command == "preflight":
        cargoflow_preflight(freight_native.reopen_candidate(directory))
        print("PREFLIGHT PASS")
    elif args.command == "verify":
        verdict = verify_cargoflow_attempt(directory)
        print(json.dumps(verdict, sort_keys=True))
        raise SystemExit(cargoflow_verdict_exit_status(verdict))
    else:
        read_prelaunch(directory)  # fail fast on any drifted prelaunch record
        result = asyncio.run(
            execute_cargoflow_attempt(
                freight_native.reopen_candidate(directory),
                CargoflowNativeBackend(authorized_one_launch=True),
            )
        )
        print(json.dumps(result, sort_keys=True))
        raise SystemExit(cargoflow_exit_status(result))


if __name__ == "__main__":
    main()
