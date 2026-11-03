"""D5-F12-DEPOT native staging pipeline (offline preparation only).

The F-12 finding (E58, §2) proved the D5 world's depot 45487 can neither be
entered nor anchor a return-capable route: its front tile 45743 carries
E+W+S road bits and no N bit. E58 §2.1 prescribed the minimal world fix of
record — demolish the depot, lay the 2-tile road pair 45743 <-> 45487, then
rebuild the depot at 45487 against its pinned front — and this pipeline
stages that fix as the one attempt of record (``D5-F12-DEPOT-1``) over the
authoritative A1 close-out world, exactly as the census pipeline does for
its read-only schedule. The protocol-10 wire contract
(``app.simulation.openttd.corridor_depot_mutation``) plus its GameScript
handler in ``d5_depot_mutation_package`` carry the pinned six-exchange
schedule; the staging/claim machinery in ``corridor_freight_native`` and
``corridor_accept_survey_native`` is plan-bound to their own contract
families, so the depot mutation gets its own narrow pipeline bound
explicitly to ``DepotMutationPlan``, reusing the proven shared ceremony by
import rather than copy. The survey's prerequisite binding of record (the
consumed A1 extension attempt ``D5-CORRIDOR-EXTENSION-3``, candidate-3,
after-save ``3748e00c…5420bd``) is reused through its own reviewed
derivation, and its ``SurveyStagingError`` is wrapped as
``DepotMutationStagingError`` at the boundary. No contract family is
retrofitted: protocols 5/6/9 stay byte-frozen, and a request of any foreign
protocol family cannot parse on the depot-mutation session (and the depot
request cannot parse on any older session).

This is not a generic abstraction layer: depot staging, preflight, sealing,
execution and replay keep the survey, freight and census pipelines
untouched and cannot accept an ``AcceptSurveyPlan``, ``FreightPlan`` or
``BoxCensusPlan``, and those pipelines still cannot accept a
``DepotMutationPlan`` (disjoint wire schemas on all four sessions refuse
the foreign request before it reaches any handler).

Unlike the strictly read-only census, this candidate is a one-shot native
mutation: its schedule admits exactly the three prescribed mutating ops
(``demolish``, ``road``, ``depot`` — each pinned to the D4 depot tile
45487 and its front 45743) plus the two sparse observations (``observe``,
``fleet``); every mutating exchange re-observes its precondition before
the one command (STALE_PIN on drift, before any command), funds are
chained per exchange (``funds_after == funds_before - cost``, cost
signed), the attempt-level ``max_cost`` ceiling is 3000, the before/after
observe gates encode the E58 diagnosis and its prescribed resolution, and
the fleet gate demands the retained zero fleet. Nothing here launches
OpenTTD, connects to a port, writes a claim or mutates any world or
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
from app.simulation.openttd.corridor_depot_mutation import (
    DEPOT_AFTER_GATE,
    DEPOT_BEFORE_GATE,
    DEPOT_EXCHANGE_TILES,
    DEPOT_MUTATING_OPS,
    DEPOT_MUTATION_DEPOT_FRONT_TILE,
    DEPOT_MUTATION_DEPOT_TILE,
    DEPOT_MUTATION_EXCHANGE_IDS,
    DEPOT_MUTATION_OPS,
    DEPOT_MUTATION_PICKUP_TILE,
    DEPOT_MUTATION_REQUEST_BUDGET,
    FUNDS_AT_F12_OPEN,
    MAX_DEPOT_MUTATION_COST,
    MAX_DEPOT_MUTATION_REQUEST_BYTES,
    MAX_DEPOT_MUTATION_RESPONSE_BYTES,
    PLANNED_DEPOT_EXCHANGES,
    DepotMutationPlan,
    DepotReadback,
    DepotRequest,
    depot_mutation_plan,
    depot_phase_outcome,
    verify_request_against_depot_plan,
)
from app.simulation.openttd.gamescript_transport import (
    ADMIN_GAMESCRIPT,
    SERVER_GAMESCRIPT,
    GameScriptTransport,
    decode_gamescript,
    encode_gamescript,
    gamescript_subscription,
)
from app.simulation.openttd.proof import corridor_accept_survey_native as survey_native
from app.simulation.openttd.proof import corridor_freight_native as freight_native
from app.simulation.openttd.proof.classification_capture import script_log_health_findings
from app.simulation.openttd.proof.corridor_construction_native import (
    source_save_path,
    stage_world,
)
from app.simulation.openttd.proof.endpoints import (
    kernel_socket_rows,
    verify_cleanup_endpoints,
)
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
DEPOT_MUTATION_PACKAGE = PACKAGES / "d5_depot_mutation_package"
AI_PACKAGE = PACKAGES / "road_company_package"
DEPOT_MUTATION_CLOSURE_ROOT = "app.simulation.openttd.proof.corridor_depot_mutation_native"

KIND = "depot-mutation"
MILESTONE_DEPOT_MUTATION = "D5-F12-DEPOT"
# Single attempt identity of record. D5-F12-DEPOT-1 carries the E58 §2.1
# prescribed fix verbatim: one attempt, one prelaunch schema; a re-run
# attempt of the lineage needs its own design record first.
DEPOT_MUTATION_ATTEMPT = "D5-F12-DEPOT-1"
D5_DEPOT_MUTATION_PRELAUNCH_SCHEMA = "d5-f12-depot-prelaunch-v1"
# The depot-mutation candidate keeps the shared native consumed-launch
# marker family and the shared prerequisite lineage schema
# (`d5-native-prerequisite-attempt-v1`) — the same shared schemas the
# freight, survey and census candidates bind, per the no-retrofit rule for
# consumed contract families.
D5_DEPOT_MUTATION_LAUNCH_CONSUMED_SCHEMA = freight_native.D5_FREIGHT_LAUNCH_CONSUMED_SCHEMA
D5_DEPOT_MUTATION_PREREQUISITE_SCHEMA = freight_native.D5_FREIGHT_PREREQUISITE_SCHEMA
if D5_DEPOT_MUTATION_PREREQUISITE_SCHEMA != survey_native.D5_SURVEY_PREREQUISITE_SCHEMA:
    raise RuntimeError(
        "the depot mutation prerequisite schema drifted from the shared lineage schema"
    )

# Prerequisite lineage of record: the pinned, consumed, replay-verified A1
# extension attempt (``D5-CORRIDOR-EXTENSION-3``), imported from the survey
# binding's own pins — the depot-mutation world is the survey's world, and
# one pin source of record stays one pin.
PINNED_PREREQUISITE = survey_native.PINNED_PREREQUISITES[
    survey_native.SURVEY_SCHEDULE_VERSION
]
PINNED_PREREQUISITE_AFTER_SAVE = survey_native.PINNED_PREREQUISITE_AFTER_SAVES[
    survey_native.SURVEY_SCHEDULE_VERSION
]

# The depot mutation GameScript readiness marker is its own (the staged
# handler logs "D5_F12_DEPOT_READY" at Start); the road-company readiness
# marker follows the staged AI bootstrap exactly as protocols 6/9 do.
DEPOT_MUTATION_READY_MARKER = "D5_F12_DEPOT_READY"

DEPOT_MUTATION_EXCHANGE_MARGIN_SECONDS = freight_native.FREIGHT_EXCHANGE_MARGIN_SECONDS


class DepotMutationStagingError(freight_native.FreightStagingError):
    """Offline depot mutation staging or pin derivation failed; nothing was launched."""


# --- Migration-safety: the depot pipeline is depot-plan typed ----------------


def _require_depot_plan(plan) -> DepotMutationPlan:
    """Refuse anything that is not the pinned ``DepotMutationPlan``.

    A ``FreightPlan``, ``AcceptSurveyPlan`` or ``BoxCensusPlan`` shares
    several field names with ``DepotMutationPlan``; every depot entry point
    guards here so a foreign plan can never be staged, sealed, executed or
    replayed as a depot mutation, and so the single plan can never drift
    from its pinned derivation.
    """
    if not isinstance(plan, DepotMutationPlan):
        raise DepotMutationStagingError(
            "the depot mutation pipeline accepts a DepotMutationPlan only"
        )
    if plan.schema_version != 1:
        raise DepotMutationStagingError("the depot plan carries an unknown schema version")
    if plan.digest != depot_mutation_plan().digest:
        raise DepotMutationStagingError(
            "the depot mutation plan drifted from the pinned observations"
        )
    return plan


def depot_plan() -> DepotMutationPlan:
    """The single pinned plan of record re-derived from the module pins.

    The depot mutation has one schedule version and one plan; its staged
    records never carry a rebuilt plan, only the digests they must match
    against this derivation.
    """
    return _require_depot_plan(depot_mutation_plan())


# --- The pinned depot mutation schedule --------------------------------------


def depot_schedule() -> list[dict]:
    """The fixed six mutation exchanges as staged plan rows.

    Order refuses drift (the before gate first, the three prescribed E58
    §2.1 mutations in order, the after gate, the fleet gate) and every
    mutating row carries its own pinned depot tile/front pair. A foreign or
    mutating-unpinned op is a staging error, never a run-time rejection
    that is benignly retried.
    """
    schedule: list[dict] = []
    for exchange in DEPOT_MUTATION_EXCHANGE_IDS:
        slot = DEPOT_EXCHANGE_TILES.get(exchange)
        if slot is None:
            op = "fleet" if exchange == "fleet-00" else "observe"
            schedule.append(dict(exchange=exchange, op=op))
        else:
            tile, front = slot
            schedule.append(
                dict(
                    exchange=exchange,
                    op="demolish" if exchange.startswith("demo-") else exchange.split("-")[0],
                    depot_tile=int(tile),
                    depot_front=(int(front) if front is not None else None),
                )
            )
    ids = [row["exchange"] for row in schedule]
    if ids != list(DEPOT_MUTATION_EXCHANGE_IDS) or len(schedule) != PLANNED_DEPOT_EXCHANGES:
        raise DepotMutationStagingError("the staged depot schedule drifted from the wire contract")
    if any(row["op"] not in DEPOT_MUTATION_OPS for row in schedule):
        raise DepotMutationStagingError(
            "a depot schedule row carries a mutation-capable or foreign op outside the profile"
        )
    if [row["op"] for row in schedule if row["op"] in DEPOT_MUTATING_OPS] != list(
        DEPOT_MUTATING_OPS
    ):
        raise DepotMutationStagingError(
            "the three prescribed E58 §2.1 mutations drifted from their pinned order"
        )
    return schedule


def staged_depot_schedule(policy: dict) -> list[dict]:
    """The staged schedule one plan-policy record binds its digest to.

    The depot mutation has one schedule version and one derivation: a
    staged record naming a foreign version pairing is refused here before
    any schedule can be trusted.
    """
    if policy.get("schedule_version", 0) != 1:
        raise ValueError(
            f"plan record names an unknown depot mutation schedule version: "
            f"{policy.get('schedule_version', 0)}"
        )
    return depot_schedule()


# --- Hypotheses (retained E58 §2.1), never facts ------------------------------


def depot_precondition_hypotheses() -> dict:
    """The E58 §2.1 prescription re-bound as depot mutation hypotheses.

    ``docs/d5-freight-4-f12-branch8-design-resolution-2026-11-02.md`` (E58)
    is the authority of record for the pre-fix diagnosis and the prescribed
    fix; this derivation binds that doc by path and sha256 and re-binds its
    §2.1 rows as the fixed-fact before/after gate hypotheses the wire
    contract pins. The gates are fixed-fact gates, never expected values:
    a native measurement differing from one halts the phase
    STALE_PIN-preservingly at that exchange itself (the halt-on-divergence
    discipline of record), which is a phase fact, not a hypothesis
    mismatch. Absent retained evidence (a fresh clone) is recorded as
    ``RETAINED_E58_ABSENT`` — the pinned gates stay pinned, no hypothesis
    is invented; nothing is normalized, and the staged record never claims
    the doc proves the post-fix world (that is what the attempt measures).
    """
    doc_path = PROJECT / "docs" / "d5-freight-4-f12-branch8-design-resolution-2026-11-02.md"
    if not doc_path.is_file():
        return dict(
            state="RETAINED_E58_ABSENT",
            before_gates=dict(DEPOT_BEFORE_GATE),
            after_gates=dict(DEPOT_AFTER_GATE),
            fleet=0,
            source=None,
            source_sha256=None,
            statement=(
                "the E58 §2.1 design record is absent from this checkout; the "
                "pinned fixed-fact gates stay the gates of record anyway and no "
                "hypothesis is invented"
            ),
        )
    text = doc_path.read_text()
    for needle in (
        "DemolishTile(45487)",
        "45743",
        "BuildRoadDepot",
        "AreRoadTilesConnected",
    ):
        if needle not in text:
            raise DepotMutationStagingError(
                f"the E58 §2.1 prescription of record lost its {needle} text"
            )
    return dict(
        state="RETAINED_E58_REBOUND",
        before_gates=dict(DEPOT_BEFORE_GATE),
        after_gates=dict(DEPOT_AFTER_GATE),
        fleet=0,
        source="docs/d5-freight-4-f12-branch8-design-resolution-2026-11-02.md",
        source_sha256=hashlib.sha256(doc_path.read_bytes()).hexdigest(),
        statement=(
            "the before/after observe gates are the E58 §2.1 prescription of "
            "record re-bound as fixed-fact gates (diagnosis verbatim, then "
            "both AreRoadTilesConnected directions true); the phase halts "
            "STALE_PIN-preservingly on any divergence at the gate exchange "
            "itself, and the zero-fleet gate demands the retained world fact"
        ),
        derivation="corridor_depot_mutation_native.depot_precondition_hypotheses",
    )


# --- The depot plan policy, budgets and readback story -----------------------


def _depot_expected_world(plan: DepotMutationPlan) -> dict:
    """The expected world-pin set of the staged depot candidate."""
    return dict(
        pickup=int(DEPOT_MUTATION_PICKUP_TILE),
        delivery=int(plan.delivery),
        delivery_front=int(plan.delivery_front),
        depot=int(plan.depot),
        depot_front=int(plan.depot_front),
        company=plan.company,
        cargo=plan.cargo,
        expected_funds=plan.expected_funds,
        request_budget=plan.request_budget,
        max_cost=plan.max_cost,
        before_gate=dict(DEPOT_BEFORE_GATE),
        after_gate=dict(DEPOT_AFTER_GATE),
        fleet_count=0,
        statement=(
            "the staged depot world is the consumed A1 extension close-out: "
            "the corridor stops must read company truck stops with their "
            "pinned fronts, the pinned depot 45487 present against its "
            "front 45743 with owner 0 and both AreRoadTilesConnected "
            "directions false (the E58 §2.1 diagnosis), and the company "
            "zero fleet; the attempt mutates only the pinned depot tile "
            "and its front"
        ),
    )


def _depot_mutation_profile() -> dict:
    """The authorized mutation profile for the staged depot candidate."""
    return dict(
        schema="d5-f12-depot-mutation-profile-v1",
        permitted_ops=list(DEPOT_MUTATION_OPS),
        mutating_ops=list(DEPOT_MUTATING_OPS),
        observation_ops=["observe", "fleet"],
        max_cost=MAX_DEPOT_MUTATION_COST,
        funds_readback_required=True,
        funds_chain="funds_after == funds_before - cost on every exchange with cost signed",
        mutation_tiles=dict(
            depot=int(DEPOT_MUTATION_DEPOT_TILE),
            front=int(DEPOT_MUTATION_DEPOT_FRONT_TILE),
        ),
        statement=(
            "exactly three cost-bearing commands exist in this candidate — "
            "GSTile.DemolishTile(45487), GSRoad.BuildRoad(45487, 45743) and "
            "GSRoad.BuildRoadDepot(45487, 45743) — each re-observing its "
            "precondition before the one dispatch; orders, station, refit, "
            "vehicle, terraform and save commands are outside the profile "
            "forever, and every exchange readbacks funds with the signed "
            "cost of record"
        ),
    )


def depot_plan_policy() -> dict:
    """The authorized plan policy for the staged depot candidate."""
    plan = depot_plan()
    schedule = depot_schedule()
    plan_digest = plan_digest_of(schedule)
    if schedule[0]["exchange"] != plan.schedule[0] or schedule[0]["op"] != "observe":
        raise DepotMutationStagingError(
            "the depot schedule must begin with the before-state observe gate"
        )
    return dict(
        company=plan.company,
        target_tile=int(DEPOT_MUTATION_DEPOT_TILE),
        max_cost=MAX_DEPOT_MUTATION_COST,
        command="demolish;road;depot",
        command_statement=(
            "the staged depot candidate carries exactly the three E58 §2.1 "
            "commands of record against the pinned depot tile and front, in "
            "the pinned order, each behind its pre-dispatch precondition "
            "re-observation; a fourth command or an unpinned tile can never "
            "enter the schedule, the session surface or the replay"
        ),
        stale_rule=(
            "re-observe the depot facts and the per-exchange precondition "
            "immediately before each one dispatch; any mismatch stops the "
            "phase without any command and preserves the verified prefix"
        ),
        identity=(
            "wire contract protocol 10: every exchange presents one uniform "
            "prelaunch seal digest and the pinned attempt ceiling; the depot "
            "mutation records measurements and signed costs only "
            "(one session, one company, three pinned commands)"
        ),
        schedule=schedule,
        plan_digest=plan_digest,
        plan_model_digest=plan.digest,
        schedule_version=1,
        observations=[
            dict(
                exchange=row["exchange"],
                kind="MUTATION" if row["op"] in DEPOT_MUTATING_OPS else "GATE",
                tile=row.get("depot_tile"),
                front_tile=row.get("depot_front"),
            )
            for row in schedule
        ],
        hypotheses=depot_precondition_hypotheses(),
        mutation=_depot_mutation_profile(),
        world=_depot_expected_world(plan),
    )


def depot_budgets() -> dict:
    """The staged budget table for the depot candidate."""
    return dict(
        launches=1,
        connection_attempts=1,
        requests=DEPOT_MUTATION_REQUEST_BUDGET,
        planned_exchanges=PLANNED_DEPOT_EXCHANGES,
        gsadmin_bytes=MAX_DEPOT_MUTATION_REQUEST_BYTES,
        response_bytes=MAX_DEPOT_MUTATION_RESPONSE_BYTES,
        retries=0,
        reconnects=0,
        readiness_seconds=45,
        request_seconds=10,
        total_seconds=300,
        max_cost=MAX_DEPOT_MUTATION_COST,
        expected_funds=FUNDS_AT_F12_OPEN,
    )


def depot_expected_readback_policy() -> dict:
    return dict(
        observe=(
            "the observe exchanges return READY with the complete v2 "
            "ObserveDepot fact set per appended request (depot_present, "
            "front_read, owner, depot_linked, both AreRoadTilesConnected "
            "directions); the before gate must reproduce the E58 §2.1 "
            "diagnosis verbatim and the after gate the prescribed "
            "resolution — any divergence halts the phase "
            "STALE_PIN-preservingly with the raw measured values in the "
            "halt record"
        ),
        demolish=(
            "the demolish exchange returns READY with its tile echo, the "
            "funds after the command and the signed cost of record "
            "(funds_before - funds_after; a refund class may credit); a "
            "funds chain break or a precondition drift halts the phase "
            "with the raw values legible"
        ),
        road=(
            "the road exchange returns READY with its tile and front-tile "
            "echoes plus the signed cost chain readback; the precondition "
            "re-observation must confirm the depot gone, its tile bare and "
            "the stub still missing in both directions before the one "
            "BuildRoad dispatch"
        ),
        depot=(
            "the depot exchange returns READY with its tile and front-tile "
            "echoes plus the signed cost chain readback; the precondition "
            "re-observation must confirm the road pair laid (front reads "
            "connected toward the depot) before the one BuildRoadDepot "
            "dispatch, which auto-clears the S bit the pair laid on the "
            "depot tile"
        ),
        fleet=(
            "the fleet exchange returns READY with the company's primary "
            "vehicle count and its ascending rows; the pinned D5 fact is "
            "the zero fleet, any vehicle halts with its per-vehicle "
            "in_depot rows listed and a row budget overrun is an "
            "unsupported native fact, never a truncation"
        ),
        receipt=(
            "NATIVE_DEPOT_MUTATION_COMPLETE only after all six exchanges "
            "verify in execution order with certified cleanup and the "
            "phase gate passing; a refused, missing, malformed, stale, "
            "divergent, out-of-budget or halting exchange leaves the "
            "session incomplete forever"
        ),
    )


# --- Depot prerequisite binding (A1 lineage re-scoped) -----------------------


def depot_prerequisite_binding(prerequisite: Path | None = None) -> dict:
    """Bind the consumed A1 extension attempt of record, depot-scoped.

    The depot prerequisite is exactly the survey prerequisite: the pinned,
    consumed, fully replay-verified A1 attempt at its retained after-save
    digest. The checked derivation of record is the survey binding's own
    (``survey_native.survey_prerequisite_binding``); this wrapper only
    scope-checks the pinned directory against the depot pins and re-labels
    the recorded verification statement for the depot lineage. A wrong
    directory is a depot staging error before any world is staged.
    """
    prerequisite = Path(
        PINNED_PREREQUISITE if prerequisite is None else prerequisite
    ).resolve()
    if prerequisite != survey_native.PINNED_PREREQUISITES[survey_native.SURVEY_SCHEDULE_VERSION]:
        raise DepotMutationStagingError(
            "the depot source world requires the pinned A1 prerequisite"
        )
    try:
        binding = survey_native.survey_prerequisite_binding(prerequisite, version=2)
    except survey_native.SurveyStagingError as error:
        raise DepotMutationStagingError(str(error)) from None
    if binding.get("schema") != D5_DEPOT_MUTATION_PREREQUISITE_SCHEMA:
        raise DepotMutationStagingError(
            "the depot prerequisite schema drifted from the shared lineage"
        )
    if Path(binding["retained_directory"]).resolve() != prerequisite:
        raise DepotMutationStagingError(
            "the depot prerequisite binding is not the pinned retained attempt"
        )
    return dict(
        binding,
        verification=(
            "full replay verification of the consumed A1 extension attempt "
            "receipt (EXTENSION_COMPLETION_VERIFIED) plus the pinned "
            "authoritative after-save digest (depot-scoped binding of the "
            "shared survey derivation of record)"
        ),
    )


# --- Depot candidate staging --------------------------------------------------


def staged_depot_composition() -> tuple[dict[str, bytes], str, int]:
    """Byte-exact save-restore composition for the D5-F12-DEPOT candidate.

    The retained staged ``info.nut`` announces the save's stored GameScript
    identity (name/version); the staged main is the bounded mutation
    handler of its own package directory (``d5_depot_mutation_package``)
    with the save-restore bridge class defined inline after the proof
    class. The frozen census/freight bytes the E47/E64 stageings pinned
    never drift for the depot handler's sake.
    """
    with zipfile.ZipFile(SEED17_RUN / "frozen-source.zip") as archive:
        info_bytes = archive.read("staged/info.nut")
    text = info_bytes.decode()
    create_instance = re.search(r'CreateInstance\(\)\s*\{\s*return\s+"([^"]+)"', text)
    version = re.search(r"GetVersion\(\)\s*\{\s*return\s+(\d+)", text)
    if create_instance is None or version is None or SOURCE_SAVE_GS_NAME not in text:
        raise DepotMutationStagingError("retained staged GameScript identity incomplete")
    main_text = (DEPOT_MUTATION_PACKAGE / "main.nut").read_text()
    bridge_class = create_instance.group(1)
    expected_bridge = f"class {bridge_class} extends D5DepotMutationProof"
    if expected_bridge not in main_text:
        raise DepotMutationStagingError(
            f"staged depot main.nut missing required bridge class {bridge_class}"
        )
    return (
        {
            "info.nut": info_bytes,
            "main.nut": main_text.encode(),
        },
        bridge_class,
        int(version.group(1)),
    )


def prepare_depot_mutation_candidate(
    directory: Path, *, prerequisite: Path | None = None
) -> PreparedProof:
    """Stage the fresh save-load composition; no process or connection."""
    plan = _require_depot_plan(depot_mutation_plan())
    prerequisite = Path(PINNED_PREREQUISITE if prerequisite is None else prerequisite).resolve()
    if prerequisite != PINNED_PREREQUISITE:
        raise DepotMutationStagingError(
            "the depot source world requires the pinned A1 prerequisite"
        )
    schedule = depot_schedule()
    policy = depot_plan_policy()
    if len(schedule) != len(plan.schedule):
        raise DepotMutationStagingError("the scheduled depot exchanges drifted")
    if policy["schedule_version"] != 1:
        raise DepotMutationStagingError("the staged depot schedule derivation drifted")
    if sha256(BINARY) != BINARY_SHA256 or matching_processes(BINARY):
        raise DepotMutationStagingError("pinned binary / exclusive runtime gate failed")
    directory = directory.resolve()
    binding = depot_prerequisite_binding(prerequisite)
    welcome = binding["expected_welcome"]
    world = stage_world(binding, welcome)
    if sha256(source_save_path(world)) != world["save_sha256"]:
        raise DepotMutationStagingError("the staged source-save digest mismatch")
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
        graphics = freight_native.stage_opengfx(
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
        composition, create_instance, version = staged_depot_composition()
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
        for source in (DEPOT_MUTATION_PACKAGE, AI_PACKAGE):
            for path in sorted(source.glob("*.nut")):
                frozen[str(path.resolve())] = sha256(path)
        frozen.update(
            {
                str(path): sha256(path)
                for path in sorted(workspace.root.rglob("*"))
                if path.is_file() and path.name != ".admin-secret"
            }
        )
        frozen.update(freight_native.d2_source_closure(DEPOT_MUTATION_CLOSURE_ROOT))
        frozen.update(freight_native.d2_dependency_inventory(DEPOT_MUTATION_CLOSURE_ROOT))
        prepared = PreparedProof(
            directory,
            spec,
            key_path,
            key.public_hex,
            (reservation.game_port, reservation.admin_port),
        )
        metadata = dict(
            schema=D5_DEPOT_MUTATION_PRELAUNCH_SCHEMA,
            milestone=MILESTONE_DEPOT_MUTATION,
            kind=KIND,
            attempt=DEPOT_MUTATION_ATTEMPT,
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
                    "GameScript name/version; the additive protocol-10 "
                    "D5DepotMutationProof ships in its own bounded package "
                    "(d5_depot_mutation_package) and satisfies the frozen "
                    "save-restore identity through its bridge class"
                ),
            ),
            save_policy=(
                "owned session-before.sav and after-diagnostic.sav only; the "
                "authoritative source save, the prerequisite attempt record "
                "and every historical artifact stay untouched; the depot "
                "mutation saves nothing itself"
            ),
            plan_policy=policy,
            expected_readback=depot_expected_readback_policy(),
            bootstrap_command=f"start_ai {STAGED_AI_DIRECTORY}",
            execution_command=[
                str(PROJECT / ".venv/bin/python"),
                "-m",
                "app.simulation.openttd.proof.corridor_depot_mutation_native",
                "run",
                str(directory),
            ],
            budgets=depot_budgets(),
            cleanup=[
                "close secure session",
                "quit and reap process",
                "verify endpoints",
                "retain session logs and the pre-mutation save",
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
                source=int(DEPOT_MUTATION_DEPOT_TILE),
                manifest_verified=True,
                statement=(
                    "the depot mutation binds the authoritative A1 extension "
                    "after-save (3748e00ce57bcb076466f50cac3776c202b4fd130d6c"
                    "6071935e9d43e45420bd) and the pinned OpenTTD 15.3 "
                    "binary; the pinned six-exchange schedule is the "
                    "contract module's own guarded derivation and the "
                    "before/after gates are the E58 §2.1 prescription bound "
                    "by path and sha256"
                ),
            ),
            environment=freight_native.launch_environment(prepared),
            environment_overrides=dict(spec.environment),
            frozen=frozen,
            cross_schedule_guard=dict(
                schema="d5-f12-depot-cross-guard-v1",
                depot_ops=list(DEPOT_MUTATION_OPS),
                mutating_ops=list(DEPOT_MUTATING_OPS),
                statement=(
                    "this candidate carries exactly the protocol-10 depot "
                    "mutation profile: a freight request (any protocol-5 op) "
                    "fails the depot session schema check with protocol 10 "
                    "required, a survey request (any protocol-6 op) and a "
                    "census request (any protocol-9 op) fail it the same "
                    "way, and any depot request fails the freight, survey "
                    "and census session checks with their required "
                    "protocols 5, 6 and 9"
                ),
            ),
        )
        metadata["prerequisite"] = dict(
            schema=D5_DEPOT_MUTATION_PREREQUISITE_SCHEMA,
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


# --- Depot preflight (offline launch-boundary rehearsal) ---------------------


def depot_preflight(prepared: PreparedProof) -> dict:
    """Offline launch-boundary rehearsal: re-derive every binding, trust nothing.

    The depot mutation has one schedule version and one plan; every
    derivation below is re-derived from the module pins and the staged
    record must match it exactly, so a record claiming a foreign lineage or
    a drifted schedule is refused here.
    """
    directory = prepared.directory
    if sha256(directory / "PRELAUNCH.json") != (directory / "PRELAUNCH.sha256").read_text().strip():
        raise ValueError("the depot prelaunch seal mismatch")
    metadata = read_prelaunch(directory)
    if (directory / "CLAIM.json").exists():
        raise ValueError("the one native attempt already consumed")
    if metadata.get("schema") != D5_DEPOT_MUTATION_PRELAUNCH_SCHEMA:
        raise ValueError("the staged prelaunch record is not the D5 depot lineage")
    if metadata.get("kind") != KIND or metadata.get("milestone") != MILESTONE_DEPOT_MUTATION:
        raise ValueError("the staged depot lineage drifted")
    if metadata.get("attempt") != DEPOT_MUTATION_ATTEMPT:
        raise ValueError("the staged attempt identity drifted from its own scope")
    verify_freeze(metadata["frozen"])
    freight_native.require_frozen_d2_closure(metadata["frozen"], DEPOT_MUTATION_CLOSURE_ROOT)
    freight_native.require_frozen_d2_dependencies(metadata["frozen"], DEPOT_MUTATION_CLOSURE_ROOT)
    policy = metadata["plan_policy"]
    plan = depot_plan()
    schedule = staged_depot_schedule(policy)
    if policy["schedule"] != schedule or policy["plan_digest"] != plan_digest_of(schedule):
        raise ValueError("the staged depot schedule drifted from the compiled derivation")
    if policy["plan_model_digest"] != plan.digest:
        raise ValueError("the staged depot plan digest drifted from the pinned plan")
    if policy.get("schedule_version") != 1:
        raise ValueError("the staged depot schedule version drifted")
    for row in schedule:
        if row["op"] not in DEPOT_MUTATION_OPS:
            raise ValueError("a scheduled depot row carries a foreign op outside the profile")
        slot = DEPOT_EXCHANGE_TILES.get(row["exchange"])
        if row["op"] in DEPOT_MUTATING_OPS:
            if (row["depot_tile"], row["depot_front"]) != slot:
                raise ValueError("a scheduled depot mutation row drifted from its pinned tiles")
            if row["depot_tile"] != plan.depot or (
                row["depot_front"] is not None and row["depot_front"] != plan.depot_front
            ):
                raise ValueError("a scheduled depot mutation row drifted from the plan pins")
        elif row["op"] != "observe" and row["op"] != "fleet":
            raise ValueError("a scheduled depot row carries an unknown observation op")
    if [row["op"] for row in schedule if row["op"] in DEPOT_MUTATING_OPS] != list(
        DEPOT_MUTATING_OPS
    ):
        raise ValueError("the three prescribed mutations drifted from their pinned order")
    if policy.get("max_cost") != MAX_DEPOT_MUTATION_COST:
        raise ValueError("the staged depot budget drifted off the pinned attempt ceiling")
    if policy["mutation"]["schema"] != "d5-f12-depot-mutation-profile-v1":
        raise ValueError("the staged depot mutation-profile schema drifted")
    if policy["mutation"] != _depot_mutation_profile():
        raise ValueError("the staged depot mutation profile drifted")
    expected_world = _depot_expected_world(plan)
    for name, expected in expected_world.items():
        if policy["world"].get(name) != expected:
            raise ValueError(f"the staged depot world pin {name} drifted")
    if policy["target_tile"] != int(DEPOT_MUTATION_DEPOT_TILE):
        raise ValueError("the staged depot target tile drifted")
    if policy["observations"] != [
        dict(
            exchange=row["exchange"],
            kind="MUTATION" if row["op"] in DEPOT_MUTATING_OPS else "GATE",
            tile=row.get("depot_tile"),
            front_tile=row.get("depot_front"),
        )
        for row in schedule
    ]:
        raise ValueError("the staged depot observation kinds drifted")
    staged_hypotheses = policy["hypotheses"]
    expected_hypotheses = depot_precondition_hypotheses()
    if staged_hypotheses.get("state") != expected_hypotheses.get("state"):
        raise ValueError(
            f"the staged depot hypothesis state is not its own derivation "
            f"({expected_hypotheses.get('state')})"
        )
    if expected_hypotheses.get("state") == "RETAINED_E58_REBOUND":
        if staged_hypotheses != expected_hypotheses:
            raise ValueError("the staged depot hypothesis record drifted from the retained bytes")
    if metadata.get("budgets") != depot_budgets():
        raise ValueError("the staged depot budget pins drifted")
    if metadata["public_key"] != prepared.public_key or metadata["binary_sha256"] != BINARY_SHA256:
        raise ValueError("the staged identity pins drifted")
    binding = depot_prerequisite_binding(Path(metadata["prerequisite"]["directory"]))
    required = ("attempt", "milestone", "directory", "prelaunch_sha256", "after_save_sha256")
    if {name: metadata["prerequisite"][name] for name in required} != dict(
        attempt=binding["attempt"],
        milestone=binding["milestone"],
        directory=binding["retained_directory"],
        prelaunch_sha256=binding["prelaunch_digest"],
        after_save_sha256=binding["save_sha256"],
    ):
        raise ValueError("the staged prerequisite binding drifted from its verified record")
    if metadata["prerequisite"].get("schema") != D5_DEPOT_MUTATION_PREREQUISITE_SCHEMA:
        raise ValueError("the staged prerequisite schema drifted")
    stored_world = metadata["world"]
    if (
        stored_world.get("retained_directory") != binding["retained_directory"]
        or stored_world.get("source_save") != binding["save"]
        or stored_world.get("save_sha256") != binding["save_sha256"]
        or stored_world.get("save_sha256") != PINNED_PREREQUISITE_AFTER_SAVE
    ):
        raise ValueError("the staged world is not the pinned prerequisite after-save")
    if metadata["world"]["expected_welcome"] != binding["expected_welcome"]:
        raise ValueError("the retained world identity requirements drifted")
    verify_staged_source_save(
        {"save_sha256": metadata["world"]["save_sha256"]},
        Path(metadata["workspace"]) / "source.sav",
    )
    composition, _, _ = staged_depot_composition()
    staged_identity = Path(metadata["workspace"]) / "game" / SOURCE_SAVE_GS_NAME
    if staged_identity.joinpath("info.nut").read_bytes() != composition["info.nut"]:
        raise ValueError("the staged GameScript identity drifted from the retained composition")
    if staged_identity.joinpath("main.nut").read_bytes() != composition["main.nut"]:
        raise ValueError("the staged depot handler drifted from its bounded package")
    if not prepared.spec.workspace.root.is_relative_to(directory / "isolated"):
        raise ValueError("the workspace ownership mismatch")
    ClearingNativeBackend(authorized_one_launch=True).preflight(prepared)
    reservation = EndpointReservation.allocate(*prepared.endpoints)
    reservation.close()
    return metadata


# --- Wire protocol 10: secure session and one-launch backend -----------------


def encode_depot_request(payload: bytes) -> bytes:
    return encode_gamescript(payload, max_payload_bytes=MAX_DEPOT_MUTATION_REQUEST_BYTES)


def decode_depot_request(payload: bytes) -> bytes:
    return decode_gamescript(payload, max_payload_bytes=MAX_DEPOT_MUTATION_REQUEST_BYTES)


class DepotMutationSecureSession(SecureAdminSession):
    """Only the depot mutation operations extend the secure write policy.

    A freight request cannot parse as a DepotRequest (protocol 10 required,
    and the freight/survey/census op sets are outside the depot Literal),
    so a protocol-5/6/9 exchange can never travel on the depot session; a
    depot request parses on none of the older sessions for the mirrored
    reason.
    """

    def validate_outbound(self, frame: bytes) -> None:
        if self.state is not AuthState.ACTIVE:
            raise ValueError("encrypted ACTIVE stream required")
        if len(frame) < 3 or struct.unpack_from("<H", frame)[0] != len(frame):
            raise ValueError("invalid frame")
        if frame[2] == ADMIN_GAMESCRIPT:
            request = DepotRequest.model_validate_json(decode_depot_request(frame[3:]))
            if request.op not in DEPOT_MUTATION_OPS:
                raise ValueError("a foreign op cannot ride the depot mutation session")
            request.to_bytes()
        elif frame not in (gamescript_subscription(), encode_admin_quit()):
            super().validate_outbound(frame)


class DepotMutationNativeBackend(freight_native.FreightNativeBackend):
    """One-launch backend carrying the shared consumed marker, depot session."""

    launch_marker_schema = D5_DEPOT_MUTATION_LAUNCH_CONSUMED_SCHEMA

    async def connect(self, prepared: PreparedProof, *, frame_observer):
        if not any(
            r["table"] == "tcp" and r["local_port"] == prepared.endpoints[1] and r["state"] == 10
            for r in kernel_socket_rows()
        ):
            raise ValueError("the native Admin listener readiness absent")
        key = AuthorizedKey.from_bytes(prepared.key_path.read_bytes())
        session = await DepotMutationSecureSession.connect_secure(
            "127.0.0.1",
            prepared.endpoints[1],
            5,
            key=key,
            frame_observer=frame_observer,
        )
        self.session = session
        return session


def depot_exchange_timeout_seconds(*, budget_table: dict, op: str) -> float:
    """Every depot op is a bounded immediate request/readback; no windows."""
    if op not in DEPOT_MUTATION_OPS:
        raise ValueError("no depot mutation budget exists for a foreign op")
    return float(budget_table["request_seconds"])


def event_loop_deadline(seconds: float) -> float:
    return time.monotonic() + seconds


def _depot_exchange_request(entry: dict, seal: str, plan: DepotMutationPlan) -> DepotRequest:
    """Build one fixed depot request: pins, pinned ceiling, its pinned spec."""
    exchange = entry["exchange"]
    tile = None
    front = None
    if entry["op"] in DEPOT_MUTATING_OPS:
        depot_tile, depot_front = DEPOT_EXCHANGE_TILES[exchange]
        tile = int(depot_tile)
        front = int(depot_front) if depot_front is not None else None
    return DepotRequest(
        op=entry["op"],
        request_id=exchange,
        plan=seal,
        company=plan.company,
        max_cost=plan.max_cost,
        pickup=plan.pickup,
        delivery=plan.delivery,
        depot=plan.depot,
        tile=tile,
        front_tile=front,
    )


async def depot_exchange(
    session,
    request: DepotRequest,
    directory: Path,
    *,
    budget_table: dict | None = None,
    overall_deadline: float | None = None,
    clock=time.monotonic,
    timeout_factory=asyncio.timeout,
) -> DepotReadback:
    """One sealed protocol-10 exchange; every frame and file is retained.

    Bounded request bytes, per-exchange timeout clamped to the overall
    attempt budget, duplicate/stale frame refusal and fail-closed parsing —
    the depot twin of the census exchange, over the 512-byte protocol-10
    bounds.
    """
    budget_table = budget_table if budget_table is not None else depot_budgets()
    permitted = depot_exchange_timeout_seconds(budget_table=budget_table, op=request.op)
    if overall_deadline is not None:
        remaining = overall_deadline - clock()
        if remaining <= 0:
            raise TimeoutError("the depot mutation attempt overall budget exhausted")
        permitted = min(permitted, remaining)
    raw = request.to_bytes()
    (directory / (request.request_id + "-request.json")).write_bytes(raw)
    await session.send(encode_depot_request(raw))
    decoder = AdminFrameDecoder()
    try:
        async with timeout_factory(permitted):
            while True:
                chunk = await session.receive()
                if not chunk:
                    raise ConnectionError("the depot mutation proof stream disconnected")
                game_frames = []
                for kind, payload in decoder.feed_frames(chunk):
                    if kind != SERVER_GAMESCRIPT:
                        raise ValueError("an unexpected depot mutation packet")
                    game_frames.append(payload)
                if len(game_frames) > 1:
                    raise ValueError("a duplicate depot mutation response frame")
                if game_frames:
                    body = game_frames[0]
                    if (directory / (request.request_id + "-response.json")).exists():
                        raise ValueError("a duplicate depot mutation response file")
                    response = decode_gamescript(
                        body, max_payload_bytes=MAX_DEPOT_MUTATION_RESPONSE_BYTES
                    )
                    readback = DepotReadback.parse_for(request, response)
                    (directory / (request.request_id + "-response.json")).write_bytes(response)
                    return readback
    except TimeoutError:
        raise TimeoutError(
            f"the depot mutation exchange {request.request_id} exceeded its "
            f"{permitted:.1f}s budget"
        ) from None


# --- Depot execution (authorized one-attempt path only) ----------------------


def apply_depot_cleanup_outcome(result: dict, *, complete: bool) -> None:
    """Fail closed on the depot mutation's final cleanup verdict."""
    result["cleanup_complete"] = bool(complete)
    if complete:
        return
    result["cleanup_failure"] = True
    if result.get("verified") is True or result.get("status") == "NATIVE_DEPOT_MUTATION_COMPLETE":
        freight_native.deny_verification(
            result,
            status="FAILED_CLEANUP",
            message=(
                "ValueError: cleanup was not certified; no verified depot "
                "mutation completion is possible"
            ),
        )


async def execute_depot_mutation_attempt(prepared: PreparedProof, backend) -> dict:
    """Execute the authorized one-attempt depot phase (never offline).

    One launch, one connection, the staged schedule's exchanges in the
    pinned order, every exchange verified against the accumulated depot
    state by the production ``depot_phase_outcome``; the first verification
    failure halts the phase prefix-preservingly (the fixed-fact gate
    divergence and the per-exchange precondition drift both surface as
    STALE_PIN halt records with their raw values legible), and cleanup is
    certified before any completion verdict can stand.
    """
    directory = prepared.directory
    depot_preflight(prepared)
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
    plan = depot_plan()
    result: dict[str, Any] = dict(
        preflight="PASS",
        native_launches=0,
        connections=0,
        requests=0,
        exchanges=[],
        mutated=[],
        last_status="NOT_DISPATCHED",
        command_accepted=False,
        state_changed=False,
        verified=False,
        status="FAILED",
        halt=None,
    )
    frames = []
    exchanges: list[tuple[DepotRequest, DepotReadback]] = []
    overall_deadline = event_loop_deadline(metadata["budgets"]["total_seconds"])
    try:
        async with asyncio.timeout(metadata["budgets"]["total_seconds"]):
            await backend.launch(prepared, authorization=grant)
            result["native_launches"] = 1
            await wait_log(backend, prepared, DEPOT_MUTATION_READY_MARKER)
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
                    request = _depot_exchange_request(entry, seal, plan)
                    if request.op not in DEPOT_MUTATION_OPS:
                        raise ValueError("a foreign op cannot enter the depot run")
                    if (
                        request.op in DEPOT_MUTATING_OPS
                        and (request.tile, request.front_tile)
                        != DEPOT_EXCHANGE_TILES[request.request_id]
                    ):
                        raise ValueError("a mutating exchange drifted from its pinned tiles")
                    verify_request_against_depot_plan(request, plan=plan, seal=seal)
                    readback = await depot_exchange(
                        session,
                        request,
                        directory,
                        budget_table=metadata["budgets"],
                        overall_deadline=overall_deadline,
                    )
                    result["requests"] += 1
                    probe = depot_phase_outcome(
                        exchanges + [(request, readback)], prelaunch_digest=seal, plan=plan
                    )
                    if probe["failed"] is not None:
                        raise ValueError(
                            f"the depot mutation exchange {label} failed verification: "
                            f"{probe['failed']['error']}"
                        )
                    exchanges.append((request, readback))
                    result["exchanges"].append(label)
                    result["last_status"] = readback.status
                    result["command_accepted"] = True
                    # Unlike the strictly read-only census: one READY
                    # readback on a mutating op is a recorded world change,
                    # never normalized away.
                    if readback.status == "READY" and request.op in DEPOT_MUTATING_OPS:
                        result["state_changed"] = True
                        result["mutated"].append(label)
                except Exception as error:
                    result["halt"] = dict(
                        label=label, error=type(error).__name__ + ": " + str(error)
                    )
                    break
            phase = depot_phase_outcome(exchanges, prelaunch_digest=seal, plan=plan)
            result["phase"] = phase
            if phase["verification"] == "DEPOT_MUTATION_COMPLETE":
                if len(exchanges) != len(plan.schedule):
                    raise ValueError(
                        "the depot completion evidence drifted from the staged schedule"
                    )
                if phase["gate"]["verdict"] != "DEPOT_MUTATION_GATE_PASSES":
                    raise ValueError("the depot completion contradicts its phase gate")
                if phase["fleet"] is None or len(phase["mutations"]) != len(DEPOT_MUTATING_OPS):
                    raise ValueError(
                        "the native fleet gate or the prescribed mutation inventory is missing"
                    )
                if result["state_changed"] is not True:
                    raise ValueError(
                        "the depot completion reported zero state change it must own"
                    )
                write_json(
                    directory / "receipt.json",
                    dict(
                        phase,
                        before_save_sha256=before_save,
                    ),
                )
                result["verified"] = True
                result["status"] = "NATIVE_DEPOT_MUTATION_COMPLETE"
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
            if result["status"] == "NATIVE_DEPOT_MUTATION_COMPLETE":
                freight_native.deny_verification(
                    result,
                    status="FAILED",
                    message=(
                        "ValueError: the retained script log health findings "
                        "deny the verified depot mutation completion"
                    ),
                )
        if result["returncode"] not in (None, 0):
            if result["status"] == "NATIVE_DEPOT_MUTATION_COMPLETE":
                freight_native.deny_verification(
                    result,
                    status="FAILED",
                    message=(
                        "ValueError: the native runtime exited abnormally after "
                        f"the depot mutation (return code {result['returncode']})"
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
        apply_depot_cleanup_outcome(result, complete=cleanup_complete)
        write_json(directory / "cleanup.json", cleanup)
        write_json(directory / "result.json", result)
        (directory / "artifact-manifest.sha256").write_text(manifest(directory))
    return result


# --- Depot replay verification ------------------------------------------------


def _parse_depot_frames(directory: Path):
    """Parse the retained frame stream of the owned secure depot session."""
    frames = json.loads((directory / "frames.json").read_text())
    outbound: list[bytes] = []
    replies: list[bytes] = []
    outbound_requests: list[DepotRequest] = []
    request_positions: dict[bytes, int] = {}
    reply_positions: dict[bytes, int] = {}
    for index, (direction, frame_hex) in enumerate(frames):
        frame = bytes.fromhex(frame_hex)
        if direction == "outbound":
            outbound.append(frame)
            if frame[2] != ADMIN_GAMESCRIPT:
                continue
            payload = decode_depot_request(frame[3:])
            try:
                query = DepotRequest.model_validate_json(payload)
            except Exception:
                raise ValueError("an outbound frame contains an invalid DepotRequest") from None
            outbound_requests.append(query)
            request_positions[payload] = index
        else:
            for kind, body in AdminFrameDecoder().feed_frames(frame):
                if kind != SERVER_GAMESCRIPT:
                    continue
                reply = decode_gamescript(body, max_payload_bytes=MAX_DEPOT_MUTATION_RESPONSE_BYTES)
                if reply not in reply_positions:
                    reply_positions[reply] = index
                replies.append(reply)
    return outbound, outbound_requests, replies, request_positions, reply_positions


def verify_depot_attempt_identity(metadata: dict, *, plan) -> dict:
    """Re-bind one retained depot attempt to its pinned prerequisite and plan.

    Replay never trusts the staged record's own declarations: the lineage
    (attempt/schema/prerequisite/world) is re-derived from the module's
    single pinned identity, the pinned prerequisite is re-verified, and the
    source-save digest, welcome, schedule, plan digests, mutation profile,
    world pins and depot hypotheses are all re-derived. A foreign lineage
    or a drifted pin refuses.
    """
    if metadata.get("attempt") != DEPOT_MUTATION_ATTEMPT:
        raise ValueError("the retained attempt identity drifted from the staged scope")
    if (
        metadata.get("schema") != D5_DEPOT_MUTATION_PRELAUNCH_SCHEMA
        or metadata.get("kind") != KIND
        or metadata.get("milestone") != MILESTONE_DEPOT_MUTATION
    ):
        raise ValueError("the retained attempt is not the D5 depot lineage")
    staged_prerequisite = metadata.get("prerequisite")
    if not isinstance(staged_prerequisite, dict):
        raise ValueError("the retained attempt lacks its prerequisite binding")
    binding = depot_prerequisite_binding(Path(staged_prerequisite.get("directory", "")))
    expected_prerequisite = dict(
        schema=D5_DEPOT_MUTATION_PREREQUISITE_SCHEMA,
        attempt=binding["attempt"],
        milestone=binding["milestone"],
        directory=binding["retained_directory"],
        prelaunch_sha256=binding["prelaunch_digest"],
        after_save_sha256=binding["save_sha256"],
        verification=binding["verification"],
    )
    if staged_prerequisite != expected_prerequisite:
        raise ValueError("the retained prerequisite binding drifted from the pinned A1 attempt")
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
        raise ValueError("the retained world is not the pinned prerequisite after-save")
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
    _require_depot_plan(plan)
    policy = metadata.get("plan_policy")
    if not isinstance(policy, dict):
        raise ValueError("the retained attempt lacks its plan policy")
    schedule = staged_depot_schedule(policy)
    if policy.get("schedule") != schedule or policy.get("plan_digest") != plan_digest_of(schedule):
        raise ValueError("the retained depot schedule drifted from the compiled derivation")
    if policy.get("plan_model_digest") != plan.digest:
        raise ValueError("the retained plan digest drifted from the pinned depot plan")
    if policy.get("schedule_version") != 1:
        raise ValueError("the retained schedule version drifted")
    if metadata.get("budgets") != depot_budgets():
        raise ValueError("the retained budget contract drifted")
    if policy.get("max_cost") != MAX_DEPOT_MUTATION_COST:
        raise ValueError("the retained budget floated off the pinned attempt ceiling")
    if policy.get("mutation", {}).get("schema") != "d5-f12-depot-mutation-profile-v1":
        raise ValueError("the retained mutation-profile schema drifted")
    if policy["mutation"] != _depot_mutation_profile():
        raise ValueError("the retained depot mutation profile drifted")
    world_pins = policy.get("world")
    if not isinstance(world_pins, dict):
        raise ValueError("the retained plan policy lacks its world pins")
    expected_pins = _depot_expected_world(plan)
    for name, expected in expected_pins.items():
        if world_pins.get(name) != expected:
            raise ValueError(f"the retained depot world pin {name} drifted")
    if (
        policy.get("company") != plan.company
        or policy.get("target_tile") != int(DEPOT_MUTATION_DEPOT_TILE)
        or policy.get("plan_model_digest") != plan.digest
    ):
        raise ValueError("the retained depot plan pins drifted")
    if policy.get("observations") != [
        dict(
            exchange=row["exchange"],
            kind="MUTATION" if row["op"] in DEPOT_MUTATING_OPS else "GATE",
            tile=row.get("depot_tile"),
            front_tile=row.get("depot_front"),
        )
        for row in schedule
    ]:
        raise ValueError("the retained depot observation kinds drifted")
    staged_hypotheses = policy.get("hypotheses")
    expected_hypotheses = depot_precondition_hypotheses()
    if (
        not isinstance(staged_hypotheses, dict)
        or staged_hypotheses.get("state") != expected_hypotheses.get("state")
    ):
        raise ValueError(
            f"the retained depot hypothesis record drifted from its version derivation "
            f"({expected_hypotheses.get('state')})"
        )
    return binding


def verify_depot_mutation_attempt(directory: Path) -> dict:
    """Replay the retained protocol-10 phase; never trust a success label.

    The replay re-derives every retained fact independently — operator
    authorization evidence, the staged depot schedule, the captured session
    frames, every per-exchange request/response pair — then re-verifies the
    whole schedule with the production
    :func:`app.simulation.openttd.corridor_depot_mutation.depot_phase_outcome`
    and the certified-cleanup gate. A forced or invented
    ``NATIVE_DEPOT_MUTATION_COMPLETE`` label alone can never verify; a
    refused, missing, malformed, stale, divergent, out-of-budget or halting
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
                "the depot candidate was never consumed by an operator "
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
    if metadata.get("schema") != D5_DEPOT_MUTATION_PRELAUNCH_SCHEMA:
        return dict(
            verification="AUTHORIZATION_UNVERIFIED",
            authorization_state="UNKNOWN_PRELAUNCH_SCHEMA",
            statement=(
                f"the prelaunch record is not the launch-capable "
                f"[{D5_DEPOT_MUTATION_PRELAUNCH_SCHEMA!r}] lineage; no verified "
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
    schedule = staged_depot_schedule(policy_replay)
    plan = depot_plan()
    if policy_replay["schedule"] != schedule or policy_replay["plan_digest"] != plan_digest_of(
        schedule
    ):
        raise ValueError("the staged depot schedule drifted from the compiled derivation")
    planned_ids = {row["exchange"] for row in schedule}
    if planned_ids != set(DEPOT_MUTATION_EXCHANGE_IDS) or len(schedule) != PLANNED_DEPOT_EXCHANGES:
        raise ValueError("the retained depot schedule drifted from the wire contract")
    verify_depot_attempt_identity(metadata, plan=plan)
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
    outbound, outbound_requests, replies, request_positions, reply_positions = _parse_depot_frames(
        directory
    )
    if len(outbound_requests) > metadata["budgets"]["requests"]:
        raise ValueError("the depot request budget exceeded (outbound frames)")
    paths = sorted(directory.glob("*-request.json"))
    file_queries = [DepotRequest.model_validate_json(path.read_bytes()) for path in paths]
    for path, query in zip(paths, file_queries, strict=True):
        if query.request_id != path.name[: -len("-request.json")]:
            raise ValueError("the retained request file identity does not match its payload")
    if len(outbound_requests) < len(file_queries):
        return dict(
            verification="UNRESOLVED_ATTEMPT_EVIDENCE_PRESERVED",
            exchanges=result.get("exchanges", []),
            mutated=result.get("mutated", []),
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
            raise ValueError(f"a duplicate depot request_id: {query.request_id}")
        seen_ids.add(query.request_id)
    response_map = {}
    for path in paths:
        response_path = path.with_name(path.name.replace("-request.json", "-response.json"))
        if response_path.is_file():
            response_map[path.read_bytes()] = response_path.read_bytes()
    for path in sorted(directory.glob("*-response.json")):
        exchange_id = path.name[: -len("-response.json")]
        try:
            readback = DepotReadback.model_validate_json(path.read_bytes())
        except ValueError as error:
            raise ValueError(
                f"the retained response file is not a parseable readback: {path.name}"
            ) from error
        if readback.request_id != exchange_id:
            raise ValueError("the retained response file identity does not match its payload")
        if not (directory / (exchange_id + "-request.json")).is_file():
            raise ValueError("the retained response file lacks its request")
    for raw, response in response_map.items():
        if outbound.count(encode_depot_request(raw)) != 1 or replies.count(response) != 1:
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
    exchanges: list[tuple[DepotRequest, DepotReadback]] = []
    for position, entry in enumerate(schedule):
        label = entry["exchange"]
        if halted_position is None and isinstance(halt_record, dict) and (
            halt_record.get("label") == label
        ):
            halted_position = position
        pending = halted_position is not None and position > halted_position
        if not pending:
            request_path = directory / (label + "-request.json")
            if not request_path.is_file():
                continue
            query = DepotRequest.model_validate_json(request_path.read_bytes())
            raw = response_map.get(query.to_bytes())
            if raw is not None:
                exchanges.append((query, DepotReadback.parse_for(query, raw)))
        if pending:
            break
    phase = depot_phase_outcome(exchanges, prelaunch_digest=seal, plan=plan)
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
    if result["status"] == "NATIVE_DEPOT_MUTATION_COMPLETE":
        if phase["verification"] != "DEPOT_MUTATION_COMPLETE":
            raise ValueError("the verified completion contradicts its depot phase outcome")
        if result.get("halt") is not None or not result.get("command_accepted"):
            raise ValueError("the verified completion contradicts its retained attempt record")
        if (result.get("native_launches"), result.get("connections")) != (
            metadata["budgets"]["launches"],
            metadata["budgets"]["connection_attempts"],
        ):
            raise ValueError("the verified completion contradicts its launch seal")
        if len(result.get("exchanges", [])) != len(plan.schedule) or not cleanup_complete:
            raise ValueError("the verified completion's cleanup or exchange inventory incomplete")
        if result.get("state_changed") is not True:
            raise ValueError("the depot completion denied the world change it must own")
        if len(outbound_requests) != len(plan.schedule):
            raise ValueError("the verified completion's request inventory drifted")
        if phase["gate"]["verdict"] != "DEPOT_MUTATION_GATE_PASSES":
            raise ValueError("the verified completion's phase gate drifted from the pass verdict")
        if len(phase.get("mutations") or []) != len(DEPOT_MUTATING_OPS):
            raise ValueError("the verified completion lacks its three prescribed mutations")
        if {row["op"] for row in phase.get("mutations") or []} != set(DEPOT_MUTATING_OPS):
            raise ValueError("the verified completion's mutation ops drifted from the profile")
        if phase.get("fleet") is None or phase["fleet"].get("count") != 0:
            raise ValueError("the verified completion's fleet gate is not the zero fleet")
        if set(phase.get("observations") or {}) != {"before-00", "after-00"}:
            raise ValueError("the verified completion's observe gates drifted")
        if not phase["funds_chain"]:
            raise ValueError("the verified completion lacks its funds chain")
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
                raise ValueError("the retained depot receipt replay mismatch")
            session_before = json.loads(
                (directory / "session-before-identity.json").read_text()
            ).get("sha256")
            if retained_receipt.get("before_save_sha256") != session_before:
                raise ValueError("the retained depot receipt replay mismatch")
        return dict(
            verification="F12_MUTATION_COMPLETION_VERIFIED",
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
            phase["verification"] != "DEPOT_MUTATION_INCOMPLETE"
            or not isinstance(halt_record, dict)
            or len(result.get("exchanges", [])) != len(phase["receipts"])
            or (
                phase["failed"] is not None
                and phase["failed"].get("label") != halt_record.get("label")
            )
        ):
            raise ValueError("the halted depot evidence contradicts its retained record")
        if not cleanup_complete:
            raise ValueError("the halted depot attempt cleanup incomplete")
        return dict(
            verification=(
                "PHASE_HALTED_EVIDENCE_PRESERVED"
                if result["status"] == "PHASE_HALTED_PREFIX_PRESERVED"
                else "ATTEMPT_FAILED_EVIDENCE_PRESERVED"
            ),
            result_status=result["status"],
            exchanges=result.get("exchanges", []),
            mutated=result.get("mutated", []),
            failed=phase["failed"],
            pending=phase["pending"],
            error=result.get("error") or (phase["failed"] or {}).get("error"),
        )
    return dict(
        verification="ATTEMPT_FAILED_EVIDENCE_PRESERVED",
        result_status=result.get("status", "UNKNOWN"),
        error=result.get("error"),
    )


def staged_depot_authorization_payload_digest(directory: Path) -> str:
    """The RFC-canonical digest of the candidate's own authorization payload."""
    directory = directory.resolve()
    metadata = read_prelaunch(directory)
    seal = sha256(directory / "PRELAUNCH.json")
    return hashlib.sha256(
        canonical_authorization_bytes(authorization_payload(metadata, seal))
    ).hexdigest()


def depot_exit_status(result: dict) -> int:
    verified = (
        result.get("verified") is True
        and result.get("status") == "NATIVE_DEPOT_MUTATION_COMPLETE"
        and result.get("cleanup_complete") is True
        and result.get("state_changed") is True
    )
    return 0 if verified else 1


def depot_verdict_exit_status(verdict: dict) -> int:
    return 0 if verdict.get("verification") == "F12_MUTATION_COMPLETION_VERIFIED" else 1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("prepare", "preflight", "run", "verify"))
    parser.add_argument("directory", type=Path)
    parser.add_argument("--prerequisite", type=Path, default=PINNED_PREREQUISITE)
    args = parser.parse_args()
    directory = args.directory.resolve()
    if args.command == "prepare":
        prepared = prepare_depot_mutation_candidate(directory, prerequisite=args.prerequisite)
        depot_preflight(prepared)
        print("PRELAUNCH PASS", directory)
    elif args.command == "preflight":
        depot_preflight(freight_native.reopen_candidate(directory))
        print("PREFLIGHT PASS")
    elif args.command == "verify":
        verdict = verify_depot_mutation_attempt(directory)
        print(json.dumps(verdict, sort_keys=True))
        raise SystemExit(depot_verdict_exit_status(verdict))
    else:
        read_prelaunch(directory)  # fail fast on any drifted prelaunch record
        result = asyncio.run(
            execute_depot_mutation_attempt(
                freight_native.reopen_candidate(directory),
                DepotMutationNativeBackend(authorized_one_launch=True),
            )
        )
        print(json.dumps(result, sort_keys=True))
        raise SystemExit(depot_exit_status(result))


if __name__ == "__main__":
    main()
