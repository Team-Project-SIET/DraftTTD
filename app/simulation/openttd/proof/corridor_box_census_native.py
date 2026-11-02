"""D5-BOX-CENSUS-1 native staging pipeline (offline preparation only).

The branch-8 finding (E58) left the ``D5-FREIGHT-4`` site gate's
exactly-one discovery boxes unresolved from retained evidence and prescribed
the box census of ``docs/d5-box-census-1-protocol-design-2026-11-02.md``
(E59): a strictly read-only native enumeration of the industries inside each
stop's radius-3 discovery box over the authoritative A1 close-out world. The
protocol-9 wire contract (``app.simulation.openttd.corridor_box_census``)
plus its GameScript handler in ``d5_census_package`` are already written; the
remaining gap is the native pipeline. The staging/claim machinery in
``corridor_freight_native`` and ``corridor_accept_survey_native`` is
plan-bound to their own contract families, so the census gets a third narrow
pipeline bound explicitly to ``BoxCensusPlan`` and its single pinned
ten-exchange schedule, reusing the proven shared ceremony by import rather
than copy. The survey's prerequisite binding of record (the consumed A1
extension attempt ``D5-CORRIDOR-EXTENSION-3``, candidate-3, after-save
``3748e00c…5420bd``) is reused through its own reviewed derivation, and its
``SurveyStagingError`` is wrapped as ``CensusStagingError`` at the boundary.
No contract family is retrofitted: protocols 5/6 stay byte-frozen, and a
request of any foreign protocol family cannot parse on the census session
(and the census request cannot parse on either older session).

This is not a generic abstraction layer: census staging, preflight, sealing,
execution and replay keep the survey and freight pipelines untouched and
cannot accept an ``AcceptSurveyPlan`` or a ``FreightPlan``, and those
pipelines still cannot accept a ``BoxCensusPlan`` (disjoint wire schemas on
all three sessions refuse the foreign request before it reaches any
handler).

The census is strictly read-only: its schedule admits only the ``radius``,
``accept``, ``prod`` and ``box`` observation ops (every mutation-capable op
is outside the census contract entirely), ``max_cost`` is 0 on every
exchange, funds are read back per exchange and cleanup is certified before
any completion verdict. Nothing here launches OpenTTD, connects to a port,
writes a claim or mutates any world or retained artifact.
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
from app.simulation.openttd.corridor_box_census import (
    BOX_EXCHANGE_SPECS,
    BOX_MEMBERSHIP_LIMIT,
    BOX_PAGE_CURSORS,
    CENSUS_BOX_CENTRES,
    CENSUS_CENTRE_ROLES,
    CENSUS_EXCHANGE_IDS,
    CENSUS_OPS,
    CENSUS_PICKUP_INDUSTRY,
    CENSUS_PICKUP_TILE,
    CENSUS_REQUEST_BUDGET,
    CENSUS_SPOT_CONTROL_TILE,
    FUNDS_AT_A1_CLOSE,
    MAX_BOX_PAGE_ROWS,
    MAX_CENSUS_REQUEST_BYTES,
    MAX_CENSUS_RESPONSE_BYTES,
    PLANNED_CENSUS_EXCHANGES,
    SPOT_EXCHANGE_TILES,
    SPOT_PROD_EXCHANGE,
    BoxCensusPlan,
    CensusReadback,
    CensusRequest,
    box_census_plan,
    census_phase_outcome,
    verify_request_against_census_plan,
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
CENSUS_PACKAGE = PACKAGES / "d5_census_package"
AI_PACKAGE = PACKAGES / "road_company_package"
CENSUS_CLOSURE_ROOT = "app.simulation.openttd.proof.corridor_box_census_native"

KIND = "census"
MILESTONE_CENSUS = "D5-BOX-CENSUS"
# Single attempt identity of record (E59 §6): one attempt, one prelaunch
# schema; a re-run attempt of the lineage needs its own design record first.
CENSUS_ATTEMPT = "D5-BOX-CENSUS-1"
D5_CENSUS_PRELAUNCH_SCHEMA = "d5-box-census-prelaunch-v1"
# The census candidate keeps the shared native consumed-launch marker family
# and the shared prerequisite lineage schema (`d5-native-prerequisite-
# attempt-v1`) — the same shared schemas the freight and survey candidates
# bind, per the no-retrofit rule for consumed contract families.
D5_CENSUS_LAUNCH_CONSUMED_SCHEMA = freight_native.D5_FREIGHT_LAUNCH_CONSUMED_SCHEMA
D5_CENSUS_PREREQUISITE_SCHEMA = freight_native.D5_FREIGHT_PREREQUISITE_SCHEMA
if D5_CENSUS_PREREQUISITE_SCHEMA != survey_native.D5_SURVEY_PREREQUISITE_SCHEMA:
    raise RuntimeError("the census prerequisite schema drifted from the shared lineage schema")

# Prerequisite lineage of record: the pinned, consumed, replay-verified A1
# extension attempt (``D5-CORRIDOR-EXTENSION-3``), imported from the survey
# binding's own pins — the census world is the survey's world, and one pin
# source of record stays one pin.
PINNED_PREREQUISITE = survey_native.PINNED_PREREQUISITES[
    survey_native.SURVEY_SCHEDULE_VERSION
]
PINNED_PREREQUISITE_AFTER_SAVE = survey_native.PINNED_PREREQUISITE_AFTER_SAVES[
    survey_native.SURVEY_SCHEDULE_VERSION
]

# The census GameScript readiness marker is its own (the staged handler logs
# "D5_CENSUS_READY" at Start); the road-company readiness marker follows the
# staged AI bootstrap exactly as protocol 6 does.
CENSUS_READY_MARKER = "D5_CENSUS_READY"

CENSUS_EXCHANGE_MARGIN_SECONDS = freight_native.FREIGHT_EXCHANGE_MARGIN_SECONDS


class CensusStagingError(freight_native.FreightStagingError):
    """Offline census staging or pin derivation failed; nothing was launched."""


# --- Migration-safety: the census pipeline is census-plan typed --------------


def _require_census_plan(plan) -> BoxCensusPlan:
    """Refuse anything that is not the pinned ``BoxCensusPlan``.

    A ``FreightPlan`` or ``AcceptSurveyPlan`` shares several field names with
    ``BoxCensusPlan``; every census entry point guards here so a freight or
    survey plan can never be staged, sealed, executed or replayed as a census,
    and so the single census plan can never drift from its pinned derivation.
    """
    if not isinstance(plan, BoxCensusPlan):
        raise CensusStagingError("the census pipeline accepts a BoxCensusPlan only")
    if plan.schema_version != 1:
        raise CensusStagingError("the census plan carries an unknown schema version")
    if plan.digest != box_census_plan().digest:
        raise CensusStagingError("the census plan drifted from the pinned observations")
    return plan


def census_plan() -> BoxCensusPlan:
    """The single pinned plan of record re-derived from the module pins.

    The census has one schedule version and one plan; its staged records
    never carry a rebuilt plan, only the digests they must match against this
    derivation (the versioned ``staged_survey_plan`` machinery has no census
    counterpart by design).
    """
    return _require_census_plan(box_census_plan())


# --- The pinned census schedule ---------------------------------------------


def census_schedule() -> list[dict]:
    """The fixed ten read-only census exchanges as staged plan rows.

    Order refuses drift (radius first, the control-of-record zero, the A1
    stop, the production control, then the three pickup-stop pages and the
    three A1-stop pages on the static cursor grid) and every row carries its
    own observation tile and page cursor where the schedule has one. No
    mutation-capable op can enter a census schedule: a foreign op is a
    staging error, never a run-time rejection that is benignly retried.
    """
    schedule: list[dict] = []
    for exchange in CENSUS_EXCHANGE_IDS:
        if exchange == "radius-00":
            schedule.append(dict(exchange=exchange, op="radius"))
        elif exchange.upper().startswith("ACC-"):
            schedule.append(
                dict(
                    exchange=exchange,
                    op="accept",
                    observation_tile=SPOT_EXCHANGE_TILES[exchange],
                )
            )
        elif exchange == SPOT_PROD_EXCHANGE:
            schedule.append(dict(exchange=exchange, op="prod"))
        elif exchange in BOX_EXCHANGE_SPECS:
            tile, cursor = BOX_EXCHANGE_SPECS[exchange]
            schedule.append(
                dict(
                    exchange=exchange,
                    op="box",
                    observation_tile=int(tile),
                    page_cursor=int(cursor),
                )
            )
        else:
            raise CensusStagingError(f"the census schedule of record cannot route {exchange}")
    ids = [row["exchange"] for row in schedule]
    if ids != list(CENSUS_EXCHANGE_IDS) or len(schedule) != PLANNED_CENSUS_EXCHANGES:
        raise CensusStagingError("the staged census schedule drifted from the wire contract")
    if any(row["op"] not in CENSUS_OPS for row in schedule):
        raise CensusStagingError("a census schedule row carries a mutation-capable or foreign op")
    return schedule


def staged_census_schedule(policy: dict) -> list[dict]:
    """The staged schedule one plan-policy record binds its digest to.

    The census has one schedule version and one derivation: a staged record
    naming a foreign version pairing is refused here before any schedule can
    be trusted.
    """
    if policy.get("schedule_version", 0) != 1:
        raise ValueError(
            f"plan record names an unknown box-census schedule version: "
            f"{policy.get('schedule_version', 0)}"
        )
    return census_schedule()


# --- Hypotheses (retained E49 census), never facts ---------------------------


def census_spot_hypotheses() -> dict:
    """The retained E49 spot observations re-bound as census hypotheses.

    The consumed ``D5-ACCEPT-SURVEY-2`` receipt (candidate-2) is the chain-
    continuity measurement of record on this same consumed A1 after-save:
    control 50351 measured 0/8, the A1 bay stop 50862 measured 8/8 and the
    pickup production control measured 104 units. The census re-measures
    those spots fail-closed in-schedule and re-binds the retained values as
    hypotheses only, never as expected values: a native measurement
    differing from one is a recorded finding, never normalized or refused —
    the divergence halts the phase at the spot exchange itself (the halt-on-
    divergence discipline of record), which is a phase fact, not a
    hypothesis mismatch. Absent retained evidence (a fresh clone) is
    recorded as ``RETAINED_CENSUS_ABSENT`` — no hypothesis is invented.
    """
    receipt_path = (
        PROJECT / "artifacts/experiments/d5-accept-survey-native-candidate-2/receipt.json"
    )
    if not receipt_path.is_file():
        return dict(
            state="RETAINED_CENSUS_ABSENT",
            spots=[],
            production=None,
            statement=(
                "the retained survey receipt of record is absent from this "
                "checkout; no hypothesis is invented and the census proceeds "
                "without one"
            ),
        )
    receipt = json.loads(receipt_path.read_text())
    observations = receipt.get("observations")
    if not isinstance(observations, dict):
        raise CensusStagingError("the retained survey receipt lacks its observation map")
    plan = census_plan()
    rows = []
    for index, tile in enumerate(plan.spots):
        entry = observations.get(str(int(tile)))
        if not isinstance(entry, dict) or "value" not in entry:
            raise CensusStagingError(
                f"the retained survey receipt lacks a spot row for observation tile {tile}"
            )
        rows.append(
            dict(
                observation_index=index,
                tile=int(tile),
                hypothesis_eighths=int(entry["value"]),
                request_id=entry.get("request_id"),
                kind="HYPOTHESIS",
            )
        )
    production = receipt.get("production")
    if production is None:
        raise CensusStagingError("the retained survey receipt lacks its production control")
    return dict(
        state="RETAINED_CENSUS_REBOUND",
        spots=rows,
        production=dict(
            exchange=SPOT_PROD_EXCHANGE,
            industry=CENSUS_PICKUP_INDUSTRY,
            hypothesis_units=int(production),
            kind="HYPOTHESIS",
        ),
        source="artifacts/experiments/d5-accept-survey-native-candidate-2/receipt.json",
        source_sha256=hashlib.sha256(receipt_path.read_bytes()).hexdigest(),
        statement=(
            "chain-continuity spot values are the retained E49 survey "
            "observations of record re-bound as hypotheses only; the "
            "census re-measures them in-schedule and halts on divergence"
        ),
        derivation="corridor_box_census_native.census_spot_hypotheses",
    )


# --- The census plan policy, budgets and readback story ----------------------


def _census_expected_world(plan: BoxCensusPlan) -> dict:
    """The expected world-pin set of the staged census candidate."""
    return dict(
        pickup=int(CENSUS_PICKUP_TILE),
        delivery=int(plan.delivery),
        delivery_front=int(plan.delivery_front),
        depot=int(plan.depot),
        depot_front=int(plan.depot_front),
        company=plan.company,
        cargo=plan.cargo,
        pickup_industry=int(plan.pickup_industry),
        spot_tiles=[int(tile) for tile in plan.spots],
        box_centres=[int(centre) for centre in plan.box_centres],
        expected_funds=plan.expected_funds,
        request_budget=plan.request_budget,
        statement=(
            "the staged census world is the consumed A1 extension close-out: "
            "the corridor stops must read company truck stops with their "
            "pinned fronts, the depot joined to its pinned front; the census "
            "only queries the pinned observation tiles (50351 the control, "
            "50862 the A1 bay stop) and the pinned box centres (45748 the "
            "pickup stop, 50862 the A1 bay stop)"
        ),
    )


def _census_box_grid() -> dict:
    """The pinned box page geometry of record as a policy box grid."""
    return dict(
        schema="d5-box-census-box-grid-v1",
        page_rows=MAX_BOX_PAGE_ROWS,
        page_cursors=[int(cursor) for cursor in BOX_PAGE_CURSORS],
        membership_limit=BOX_MEMBERSHIP_LIMIT,
        centres=[
            dict(
                tile=int(centre),
                role=CENSUS_CENTRE_ROLES[centre],
            )
            for centre in CENSUS_BOX_CENTRES
        ],
        statement=(
            "the box counts list every pinned scan centre with its role of "
            "record (producer iff p > 0, acceptor iff a == 1); pages sit on "
            "the static cursor grid, emptily drained beyond membership"
        ),
    )


def census_plan_policy() -> dict:
    """The authorized read-only plan policy for the staged census candidate."""
    plan = census_plan()
    schedule = census_schedule()
    plan_digest = plan_digest_of(schedule)
    if schedule[0]["exchange"] != plan.schedule[0] or schedule[0]["op"] != "radius":
        raise CensusStagingError("the census schedule must begin with the radius observation")
    control_tile = CENSUS_SPOT_CONTROL_TILE
    expected_world = _census_expected_world(plan)
    return dict(
        company=plan.company,
        target_tile=int(control_tile),
        max_cost=0,
        command="none",
        command_statement=(
            "the staged census contains no mutation-capable command of any "
            "kind; building, orders, purchases, vehicles, saves and any "
            "cost-bearing operation are outside this candidate forever"
        ),
        stale_rule=(
            "re-observe every pin of each exchange immediately before its "
            "one dispatch; any mismatch stops the phase without any command "
            "and preserves the verified prefix"
        ),
        identity=(
            "wire contract protocol 9: every exchange presents one uniform "
            "prelaunch seal digest; the census records measurements only "
            "(one read-only session, one company, zero commands)"
        ),
        schedule=schedule,
        plan_digest=plan_digest,
        plan_model_digest=plan.digest,
        schedule_version=1,
        observations=[
            dict(
                tile=int(tile),
                kind="CONTROL" if tile == control_tile else "A1_STOP",
            )
            for tile in plan.spots
        ],
        hypotheses=census_spot_hypotheses(),
        box_grid=_census_box_grid(),
        world=expected_world,
        read_only=dict(
            schema="d5-box-census-readonly-v1",
            permitted_ops=list(CENSUS_OPS),
            max_cost=0,
            funds_readback_required=True,
            statement=(
                "every exchange is a pure observation; a mutation-capable "
                "op cannot enter the schedule, the session surface or the "
                "replay"
            ),
        ),
    )


def census_budgets() -> dict:
    """The staged budget table for the census candidate (no cost budget)."""
    return dict(
        launches=1,
        connection_attempts=1,
        requests=CENSUS_REQUEST_BUDGET,
        planned_exchanges=PLANNED_CENSUS_EXCHANGES,
        gsadmin_bytes=MAX_CENSUS_REQUEST_BYTES,
        response_bytes=MAX_CENSUS_RESPONSE_BYTES,
        retries=0,
        reconnects=0,
        readiness_seconds=45,
        request_seconds=10,
        total_seconds=300,
        max_cost=0,
        expected_funds=FUNDS_AT_A1_CLOSE,
    )


def census_expected_readback_policy() -> dict:
    return dict(
        radius=(
            "the radius exchange returns READY with the native truck-stop "
            "coverage radius (0..255); no acceptance or box observation is "
            "possible before this exchange verifies"
        ),
        accept=(
            "each accept exchange returns READY with the measured native "
            "acceptance (0..8 eighths) for exactly its pinned spot tile plus "
            "the radius echo; a value outside 0..8 can never parse and a "
            "divergence from the zero/8 spots of record halts the census "
            "prefix-preservingly with the raw measured value in the halt "
            "record"
        ),
        prod=(
            "the prod exchange returns READY with the pickup industry's "
            "last-month production of cargo 1; a divergence from the "
            "measured 104 of record halts the census prefix-preservingly "
            "with the raw measured value in the halt record"
        ),
        box=(
            "each box exchange returns READY with the echoed pinned centre "
            "and page cursor plus the page's deterministic ascending-id rows "
            "slice, its count and its more flag; a drained page is a "
            "READY-empty measurement of absence (more = false), and a third "
            "page still reporting more = true is an explicit "
            "CENSUS_GATE_UNDECIDED_OVERFLOW finding, never a refusal"
        ),
        receipt=(
            "CENSUS_COMPLETE only after all ten exchanges verify in "
            "execution order with certified cleanup; a refused, missing, "
            "malformed, out-of-range, stale, divergent or inconclusive "
            "observation leaves the census incomplete forever"
        ),
    )


# --- Census prerequisite binding (A1 lineage re-scoped) ----------------------


def census_prerequisite_binding(prerequisite: Path | None = None) -> dict:
    """Bind the consumed A1 extension attempt of record, census-scoped.

    The census prerequisite is exactly the survey prerequisite: the pinned,
    consumed, fully replay-verified A1 attempt at its retained after-save
    digest. The checked derivation of record is the survey binding's own
    (``survey_native.survey_prerequisite_binding_v2``); this wrapper only
    scope-checks the pinned directory against the census pins and re-labels
    the recorded verification statement for the census lineage. A wrong
    directory is a census staging error before any world is staged.
    """
    prerequisite = Path(
        PINNED_PREREQUISITE if prerequisite is None else prerequisite
    ).resolve()
    if prerequisite != survey_native.PINNED_PREREQUISITES[survey_native.SURVEY_SCHEDULE_VERSION]:
        raise CensusStagingError("the census source world requires the pinned A1 prerequisite")
    try:
        binding = survey_native.survey_prerequisite_binding(prerequisite, version=2)
    except survey_native.SurveyStagingError as error:
        raise CensusStagingError(str(error)) from None
    if binding.get("schema") != D5_CENSUS_PREREQUISITE_SCHEMA:
        raise CensusStagingError("the census prerequisite schema drifted from the shared lineage")
    if Path(binding["retained_directory"]).resolve() != prerequisite:
        raise CensusStagingError(
            "the census prerequisite binding is not the pinned retained attempt"
        )
    return dict(
        binding,
        verification=(
            "full replay verification of the consumed A1 extension attempt "
            "receipt (EXTENSION_COMPLETION_VERIFIED) plus the pinned "
            "authoritative after-save digest (census-scoped binding of the "
            "shared survey derivation of record)"
        ),
    )


# --- Census candidate staging ------------------------------------------------


def staged_census_composition() -> tuple[dict[str, bytes], str, int]:
    """Byte-exact save-restore composition for the D5 box-census candidate.

    The retained staged ``info.nut`` announces the save's stored GameScript
    identity (name/version); the staged main is the bounded census handler
    of its own package directory (``d5_census_package``) with the save-restore
    bridge class defined inline after the proof class. The frozen
    ``d5_freight_package`` bytes the E47 staging pinned never drift for the
    census handler's sake.
    """
    with zipfile.ZipFile(SEED17_RUN / "frozen-source.zip") as archive:
        info_bytes = archive.read("staged/info.nut")
    text = info_bytes.decode()
    create_instance = re.search(r'CreateInstance\(\)\s*\{\s*return\s+"([^"]+)"', text)
    version = re.search(r"GetVersion\(\)\s*\{\s*return\s+(\d+)", text)
    if create_instance is None or version is None or SOURCE_SAVE_GS_NAME not in text:
        raise CensusStagingError("retained staged GameScript identity incomplete")
    main_text = (CENSUS_PACKAGE / "main.nut").read_text()
    bridge_class = create_instance.group(1)
    expected_bridge = f"class {bridge_class} extends D5CensusProof"
    if expected_bridge not in main_text:
        raise CensusStagingError(
            f"staged census main.nut missing required bridge class {bridge_class}"
        )
    return (
        {
            "info.nut": info_bytes,
            "main.nut": (CENSUS_PACKAGE / "main.nut").read_bytes(),
        },
        bridge_class,
        int(version.group(1)),
    )


def prepare_box_census_candidate(
    directory: Path, *, prerequisite: Path | None = None
) -> PreparedProof:
    """Stage the fresh save-load composition; no process or connection."""
    plan = _require_census_plan(box_census_plan())
    prerequisite = Path(PINNED_PREREQUISITE if prerequisite is None else prerequisite).resolve()
    if prerequisite != PINNED_PREREQUISITE:
        raise CensusStagingError("the census source world requires the pinned A1 prerequisite")
    schedule = census_schedule()
    policy = census_plan_policy()
    if len(schedule) != len(plan.schedule):
        raise CensusStagingError("the scheduled census exchanges drifted")
    if policy["schedule_version"] != 1:
        raise CensusStagingError("the staged census schedule derivation drifted")
    if sha256(BINARY) != BINARY_SHA256 or matching_processes(BINARY):
        raise CensusStagingError("pinned binary / exclusive runtime gate failed")
    directory = directory.resolve()
    binding = census_prerequisite_binding(prerequisite)
    welcome = binding["expected_welcome"]
    world = stage_world(binding, welcome)
    if sha256(source_save_path(world)) != world["save_sha256"]:
        raise CensusStagingError("the staged source-save digest mismatch")
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
        composition, create_instance, version = staged_census_composition()
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
        for source in (CENSUS_PACKAGE, AI_PACKAGE):
            for path in sorted(source.glob("*.nut")):
                frozen[str(path.resolve())] = sha256(path)
        frozen.update(
            {
                str(path): sha256(path)
                for path in sorted(workspace.root.rglob("*"))
                if path.is_file() and path.name != ".admin-secret"
            }
        )
        frozen.update(freight_native.d2_source_closure(CENSUS_CLOSURE_ROOT))
        frozen.update(freight_native.d2_dependency_inventory(CENSUS_CLOSURE_ROOT))
        prepared = PreparedProof(
            directory,
            spec,
            key_path,
            key.public_hex,
            (reservation.game_port, reservation.admin_port),
        )
        metadata = dict(
            schema=D5_CENSUS_PRELAUNCH_SCHEMA,
            milestone=MILESTONE_CENSUS,
            kind=KIND,
            attempt=CENSUS_ATTEMPT,
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
                    "GameScript name/version; the additive protocol-9 "
                    "D5CensusProof ships in its own bounded package "
                    "(d5_census_package) and satisfies the frozen "
                    "save-restore identity through its bridge class"
                ),
            ),
            save_policy=(
                "owned session-before.sav and after-diagnostic.sav only; the "
                "authoritative source save, the prerequisite attempt record "
                "and every historical artifact stay untouched; the census "
                "saves nothing itself"
            ),
            plan_policy=policy,
            expected_readback=census_expected_readback_policy(),
            bootstrap_command=f"start_ai {STAGED_AI_DIRECTORY}",
            execution_command=[
                str(PROJECT / ".venv/bin/python"),
                "-m",
                "app.simulation.openttd.proof.corridor_box_census_native",
                "run",
                str(directory),
            ],
            budgets=census_budgets(),
            cleanup=[
                "close secure session",
                "quit and reap process",
                "verify endpoints",
                "retain session logs and the pre-census save",
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
                source=int(CENSUS_SPOT_CONTROL_TILE),
                manifest_verified=True,
                statement=(
                    "the census binds the authoritative A1 extension "
                    "after-save (3748e00ce57bcb076466f50cac3776c202b4fd130d6c"
                    "6071935e9d43e45420bd) and the pinned OpenTTD 15.3 "
                    "binary; the pinned census schedule is the contract "
                    "module's own guarded derivation"
                ),
            ),
            environment=freight_native.launch_environment(prepared),
            environment_overrides=dict(spec.environment),
            frozen=frozen,
            cross_schedule_guard=dict(
                schema="d5-box-census-cross-guard-v1",
                census_ops=list(CENSUS_OPS),
                statement=(
                    "this candidate refuses every mutation-capable op: a "
                    "freight request (any protocol-5 op) fails the census "
                    "session schema check with protocol 9 required, a survey "
                    "request (any protocol-6 op) fails it the same way, and "
                    "any census request fails the freight and survey session "
                    "checks with their required protocols 5 and 6"
                ),
            ),
        )
        metadata["prerequisite"] = dict(
            schema=D5_CENSUS_PREREQUISITE_SCHEMA,
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


# --- Census preflight (offline launch-boundary rehearsal) --------------------


def census_preflight(prepared: PreparedProof) -> dict:
    """Offline launch-boundary rehearsal: re-derive every binding, trust nothing.

    The census has one schedule version and one plan; every derivation below
    is re-derived from the module pins and the staged record must match it
    exactly, so a record claiming a foreign lineage or a drifted schedule is
    refused here.
    """
    directory = prepared.directory
    if sha256(directory / "PRELAUNCH.json") != (directory / "PRELAUNCH.sha256").read_text().strip():
        raise ValueError("the census prelaunch seal mismatch")
    metadata = read_prelaunch(directory)
    if (directory / "CLAIM.json").exists():
        raise ValueError("the one native attempt already consumed")
    if metadata.get("schema") != D5_CENSUS_PRELAUNCH_SCHEMA:
        raise ValueError("the staged prelaunch record is not the D5 census lineage")
    if metadata.get("kind") != KIND or metadata.get("milestone") != MILESTONE_CENSUS:
        raise ValueError("the staged census lineage drifted")
    if metadata.get("attempt") != CENSUS_ATTEMPT:
        raise ValueError("the staged attempt identity drifted from its own scope")
    verify_freeze(metadata["frozen"])
    freight_native.require_frozen_d2_closure(metadata["frozen"], CENSUS_CLOSURE_ROOT)
    freight_native.require_frozen_d2_dependencies(metadata["frozen"], CENSUS_CLOSURE_ROOT)
    policy = metadata["plan_policy"]
    plan = census_plan()
    schedule = staged_census_schedule(policy)
    if policy["schedule"] != schedule or policy["plan_digest"] != plan_digest_of(schedule):
        raise ValueError("the staged census schedule drifted from the compiled derivation")
    if policy["plan_model_digest"] != plan.digest:
        raise ValueError("the staged census plan digest drifted from the pinned plan")
    if policy.get("schedule_version") != 1:
        raise ValueError("the staged census schedule version drifted")
    for row in schedule:
        if row["op"] not in CENSUS_OPS:
            raise ValueError("a scheduled census row carries a mutation-capable or foreign op")
        spot_spec = SPOT_EXCHANGE_TILES.get(row["exchange"])
        page_spec = BOX_EXCHANGE_SPECS.get(row["exchange"])
        if row["op"] == "accept" and row["observation_tile"] != spot_spec:
            raise ValueError("a scheduled census spot row drifted from its pinned tile")
        if row["op"] == "box" and (row["observation_tile"], row["page_cursor"]) != page_spec:
            raise ValueError("a scheduled census box row drifted from its pinned page spec")
    if policy.get("max_cost") != 0:
        raise ValueError("the staged census must budget zero cost")
    if policy["read_only"]["schema"] != "d5-box-census-readonly-v1":
        raise ValueError("the staged census read-only schema drifted")
    if policy["read_only"]["permitted_ops"] != list(CENSUS_OPS):
        raise ValueError("the staged census's read-only op set drifted")
    expected_world = _census_expected_world(plan)
    for name, expected in expected_world.items():
        if policy["world"].get(name) != expected:
            raise ValueError(f"the staged census world pin {name} drifted")
    if policy["target_tile"] != int(CENSUS_SPOT_CONTROL_TILE):
        raise ValueError("the staged census control tile drifted")
    if policy["observations"] != [
        dict(
            tile=int(tile),
            kind="CONTROL" if tile == CENSUS_SPOT_CONTROL_TILE else "A1_STOP",
        )
        for tile in plan.spots
    ]:
        raise ValueError("the staged census observation kinds drifted")
    if policy["box_grid"] != _census_box_grid():
        raise ValueError("the staged census box grid drifted from the pinned geometry")
    staged_hypotheses = policy["hypotheses"]
    expected_hypotheses = census_spot_hypotheses()
    if staged_hypotheses.get("state") != expected_hypotheses.get("state"):
        raise ValueError(
            f"the staged census hypothesis state is not its own derivation "
            f"({expected_hypotheses.get('state')})"
        )
    if expected_hypotheses.get("state") == "RETAINED_CENSUS_REBOUND":
        if staged_hypotheses != expected_hypotheses:
            raise ValueError("the staged census hypothesis record drifted from the retained bytes")
    if metadata.get("budgets") != census_budgets():
        raise ValueError("the staged census budget pins drifted")
    if metadata["public_key"] != prepared.public_key or metadata["binary_sha256"] != BINARY_SHA256:
        raise ValueError("the staged identity pins drifted")
    binding = census_prerequisite_binding(Path(metadata["prerequisite"]["directory"]))
    required = ("attempt", "milestone", "directory", "prelaunch_sha256", "after_save_sha256")
    if {name: metadata["prerequisite"][name] for name in required} != dict(
        attempt=binding["attempt"],
        milestone=binding["milestone"],
        directory=binding["retained_directory"],
        prelaunch_sha256=binding["prelaunch_digest"],
        after_save_sha256=binding["save_sha256"],
    ):
        raise ValueError("the staged prerequisite binding drifted from its verified record")
    if metadata["prerequisite"].get("schema") != D5_CENSUS_PREREQUISITE_SCHEMA:
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
    composition, _, _ = staged_census_composition()
    staged_identity = Path(metadata["workspace"]) / "game" / SOURCE_SAVE_GS_NAME
    if staged_identity.joinpath("info.nut").read_bytes() != composition["info.nut"]:
        raise ValueError("the staged GameScript identity drifted from the retained composition")
    if staged_identity.joinpath("main.nut").read_bytes() != composition["main.nut"]:
        raise ValueError("the staged census handler drifted from its bounded package")
    if not prepared.spec.workspace.root.is_relative_to(directory / "isolated"):
        raise ValueError("the workspace ownership mismatch")
    ClearingNativeBackend(authorized_one_launch=True).preflight(prepared)
    reservation = EndpointReservation.allocate(*prepared.endpoints)
    reservation.close()
    return metadata


# --- Wire protocol 9: secure session and one-launch backend ------------------


def encode_census_request(payload: bytes) -> bytes:
    return encode_gamescript(payload, max_payload_bytes=MAX_CENSUS_REQUEST_BYTES)


def decode_census_request(payload: bytes) -> bytes:
    return decode_gamescript(payload, max_payload_bytes=MAX_CENSUS_REQUEST_BYTES)


class CensusSecureSession(SecureAdminSession):
    """Only the census operations extend the secure write policy.

    A freight request cannot parse as a CensusRequest (protocol 9 required,
    and the freight op set is outside the census Literal), so a protocol-5
    exchange can never travel on the census session; the same holds for a
    survey request. A census request parses on neither older session for the
    mirrored reason.
    """

    def validate_outbound(self, frame: bytes) -> None:
        if self.state is not AuthState.ACTIVE:
            raise ValueError("encrypted ACTIVE stream required")
        if len(frame) < 3 or struct.unpack_from("<H", frame)[0] != len(frame):
            raise ValueError("invalid frame")
        if frame[2] == ADMIN_GAMESCRIPT:
            request = CensusRequest.model_validate_json(decode_census_request(frame[3:]))
            if request.op not in CENSUS_OPS:
                raise ValueError("a mutation-capable op cannot ride the census session")
            request.to_bytes()
        elif frame not in (gamescript_subscription(), encode_admin_quit()):
            super().validate_outbound(frame)


class CensusNativeBackend(freight_native.FreightNativeBackend):
    """One-launch backend carrying the shared consumed marker, census session."""

    launch_marker_schema = D5_CENSUS_LAUNCH_CONSUMED_SCHEMA

    async def connect(self, prepared: PreparedProof, *, frame_observer) -> CensusSecureSession:
        if not any(
            r["table"] == "tcp" and r["local_port"] == prepared.endpoints[1] and r["state"] == 10
            for r in kernel_socket_rows()
        ):
            raise ValueError("the native Admin listener readiness absent")
        key = AuthorizedKey.from_bytes(prepared.key_path.read_bytes())
        session = await CensusSecureSession.connect_secure(
            "127.0.0.1",
            prepared.endpoints[1],
            5,
            key=key,
            frame_observer=frame_observer,
        )
        self.session = session
        return session


def census_exchange_timeout_seconds(*, budget_table: dict, op: str) -> float:
    """Every census op is a bounded immediate request/readback; no windows."""
    if op not in CENSUS_OPS:
        raise ValueError("no census budget exists for a foreign op")
    return float(budget_table["request_seconds"])


def event_loop_deadline(seconds: float) -> float:
    return time.monotonic() + seconds


def _census_exchange_request(entry: dict, seal: str, plan: BoxCensusPlan) -> CensusRequest:
    """Build one fixed census request: pins, zero cost, its pinned spec."""
    exchange = entry["exchange"]
    tile = None
    cursor = None
    if entry["op"] == "accept":
        tile = int(plan.spots[plan.schedule.index(exchange) - 1])
    elif entry["op"] == "box":
        point, cursor = BOX_EXCHANGE_SPECS[exchange]
        tile = int(point)
    return CensusRequest(
        op=entry["op"],
        request_id=exchange,
        plan=seal,
        company=plan.company,
        max_cost=0,
        pickup=int(CENSUS_PICKUP_TILE),
        delivery=plan.delivery,
        depot=plan.depot,
        tile=tile,
        cursor=cursor,
    )


async def census_exchange(
    session,
    request: CensusRequest,
    directory: Path,
    *,
    budget_table: dict | None = None,
    overall_deadline: float | None = None,
    clock=time.monotonic,
    timeout_factory=asyncio.timeout,
) -> CensusReadback:
    """One sealed protocol-9 exchange; every frame and file is retained.

    Bounded request bytes, per-exchange timeout clamped to the overall
    attempt budget, duplicate/stale frame refusal and fail-closed parsing —
    the census twin of the survey exchange, over the 512-byte protocol-9
    bounds.
    """
    budget_table = budget_table if budget_table is not None else census_budgets()
    permitted = census_exchange_timeout_seconds(budget_table=budget_table, op=request.op)
    if overall_deadline is not None:
        remaining = overall_deadline - clock()
        if remaining <= 0:
            raise TimeoutError("the census attempt overall budget exhausted")
        permitted = min(permitted, remaining)
    raw = request.to_bytes()
    (directory / (request.request_id + "-request.json")).write_bytes(raw)
    await session.send(encode_census_request(raw))
    decoder = AdminFrameDecoder()
    try:
        async with timeout_factory(permitted):
            while True:
                chunk = await session.receive()
                if not chunk:
                    raise ConnectionError("the census proof stream disconnected")
                game_frames = []
                for kind, payload in decoder.feed_frames(chunk):
                    if kind != SERVER_GAMESCRIPT:
                        raise ValueError("an unexpected census packet")
                    game_frames.append(payload)
                if len(game_frames) > 1:
                    raise ValueError("a duplicate census response frame")
                if game_frames:
                    body = game_frames[0]
                    if (directory / (request.request_id + "-response.json")).exists():
                        raise ValueError("a duplicate census response file")
                    response = decode_gamescript(body, max_payload_bytes=MAX_CENSUS_RESPONSE_BYTES)
                    readback = CensusReadback.parse_for(request, response)
                    (directory / (request.request_id + "-response.json")).write_bytes(response)
                    return readback
    except TimeoutError:
        raise TimeoutError(
            f"the census exchange {request.request_id} exceeded its {permitted:.1f}s budget"
        ) from None


# --- Census execution (authorized one-attempt path only) ---------------------


def apply_census_cleanup_outcome(result: dict, *, complete: bool) -> None:
    """Fail closed on the census's final cleanup verdict."""
    result["cleanup_complete"] = bool(complete)
    if complete:
        return
    result["cleanup_failure"] = True
    if result.get("verified") is True or result.get("status") == "NATIVE_CENSUS_COMPLETE":
        freight_native.deny_verification(
            result,
            status="FAILED_CLEANUP",
            message=(
                "ValueError: cleanup was not certified; no verified census completion is possible"
            ),
        )


async def execute_box_census_attempt(prepared: PreparedProof, backend) -> dict:
    """Execute the authorized one-attempt census phase (never offline).

    One launch, one connection, the staged schedule's read-only exchanges in
    the pinned order, every exchange verified against the accumulated census
    state by the production ``census_phase_outcome``; the first verification
    failure halts the phase prefix-preservingly, and cleanup is certified
    before any completion verdict can stand.
    """
    directory = prepared.directory
    census_preflight(prepared)
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
    plan = census_plan()
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
    exchanges: list[tuple[CensusRequest, CensusReadback]] = []
    overall_deadline = event_loop_deadline(metadata["budgets"]["total_seconds"])
    try:
        async with asyncio.timeout(metadata["budgets"]["total_seconds"]):
            await backend.launch(prepared, authorization=grant)
            result["native_launches"] = 1
            await wait_log(backend, prepared, CENSUS_READY_MARKER)
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
                    request = _census_exchange_request(entry, seal, plan)
                    if request.op not in CENSUS_OPS:
                        raise ValueError("a mutation-capable op cannot enter the census run")
                    verify_request_against_census_plan(request, plan=plan, seal=seal)
                    readback = await census_exchange(
                        session,
                        request,
                        directory,
                        budget_table=metadata["budgets"],
                        overall_deadline=overall_deadline,
                    )
                    result["requests"] += 1
                    probe = census_phase_outcome(
                        exchanges + [(request, readback)], prelaunch_digest=seal, plan=plan
                    )
                    if probe["failed"] is not None:
                        raise ValueError(
                            f"the census exchange {label} failed verification: "
                            f"{probe['failed']['error']}"
                        )
                    exchanges.append((request, readback))
                    result["exchanges"].append(label)
                    result["last_status"] = readback.status
                    result["command_accepted"] = True
                    result["state_changed"] = False  # the census mutates nothing
                except Exception as error:
                    result["halt"] = dict(
                        label=label, error=type(error).__name__ + ": " + str(error)
                    )
                    break
            phase = census_phase_outcome(exchanges, prelaunch_digest=seal, plan=plan)
            result["phase"] = phase
            if phase["verification"] == "CENSUS_COMPLETE":
                if len(exchanges) != len(plan.schedule):
                    raise ValueError(
                        "the census completion evidence drifted from the staged schedule"
                    )
                if phase["radius"] is None or phase["production"] is None:
                    raise ValueError(
                        "the native radius or production control observation is missing"
                    )
                write_json(
                    directory / "receipt.json",
                    dict(
                        phase,
                        before_save_sha256=before_save,
                    ),
                )
                result["verified"] = True
                result["status"] = "NATIVE_CENSUS_COMPLETE"
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
            if result["status"] == "NATIVE_CENSUS_COMPLETE":
                freight_native.deny_verification(
                    result,
                    status="FAILED",
                    message=(
                        "ValueError: the retained script log health findings "
                        "deny the verified census completion"
                    ),
                )
        if result["returncode"] not in (None, 0):
            if result["status"] == "NATIVE_CENSUS_COMPLETE":
                freight_native.deny_verification(
                    result,
                    status="FAILED",
                    message=(
                        "ValueError: the native runtime exited abnormally after "
                        f"the census (return code {result['returncode']})"
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
        apply_census_cleanup_outcome(result, complete=cleanup_complete)
        write_json(directory / "cleanup.json", cleanup)
        write_json(directory / "result.json", result)
        (directory / "artifact-manifest.sha256").write_text(manifest(directory))
    return result


# --- Census replay verification ----------------------------------------------


def _parse_census_frames(directory: Path):
    """Parse the retained frame stream of the owned secure census session."""
    frames = json.loads((directory / "frames.json").read_text())
    outbound: list[bytes] = []
    replies: list[bytes] = []
    outbound_requests: list[CensusRequest] = []
    request_positions: dict[bytes, int] = {}
    reply_positions: dict[bytes, int] = {}
    for index, (direction, frame_hex) in enumerate(frames):
        frame = bytes.fromhex(frame_hex)
        if direction == "outbound":
            outbound.append(frame)
            if frame[2] != ADMIN_GAMESCRIPT:
                continue
            payload = decode_census_request(frame[3:])
            try:
                query = CensusRequest.model_validate_json(payload)
            except Exception:
                raise ValueError("an outbound frame contains an invalid CensusRequest") from None
            outbound_requests.append(query)
            request_positions[payload] = index
        else:
            for kind, body in AdminFrameDecoder().feed_frames(frame):
                if kind != SERVER_GAMESCRIPT:
                    continue
                reply = decode_gamescript(body, max_payload_bytes=MAX_CENSUS_RESPONSE_BYTES)
                if reply not in reply_positions:
                    reply_positions[reply] = index
                replies.append(reply)
    return outbound, outbound_requests, replies, request_positions, reply_positions


def verify_box_census_attempt_identity(metadata: dict, *, plan) -> dict:
    """Re-bind one retained census attempt to its pinned prerequisite and plan.

    Replay never trusts the staged record's own declarations: the lineage
    (attempt/schema/prerequisite/world) is re-derived from the module's
    single pinned identity, the pinned prerequisite is re-verified, and the
    source-save digest, welcome, schedule, plan digests, read-only scope,
    box grid and census hypotheses are all re-derived. A foreign lineage or
    a drifted pin refuses.
    """
    if metadata.get("attempt") != CENSUS_ATTEMPT:
        raise ValueError("the retained attempt identity drifted from the staged scope")
    if (
        metadata.get("schema") != D5_CENSUS_PRELAUNCH_SCHEMA
        or metadata.get("kind") != KIND
        or metadata.get("milestone") != MILESTONE_CENSUS
    ):
        raise ValueError("the retained attempt is not the D5 census lineage")
    staged_prerequisite = metadata.get("prerequisite")
    if not isinstance(staged_prerequisite, dict):
        raise ValueError("the retained attempt lacks its prerequisite binding")
    binding = census_prerequisite_binding(Path(staged_prerequisite.get("directory", "")))
    expected_prerequisite = dict(
        schema=D5_CENSUS_PREREQUISITE_SCHEMA,
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
    _require_census_plan(plan)
    policy = metadata.get("plan_policy")
    if not isinstance(policy, dict):
        raise ValueError("the retained attempt lacks its plan policy")
    schedule = staged_census_schedule(policy)
    if policy.get("schedule") != schedule or policy.get("plan_digest") != plan_digest_of(schedule):
        raise ValueError("the retained census schedule drifted from the compiled derivation")
    if policy.get("plan_model_digest") != plan.digest:
        raise ValueError("the retained plan digest drifted from the pinned census plan")
    if policy.get("schedule_version") != 1:
        raise ValueError("the retained schedule version drifted")
    if metadata.get("budgets") != census_budgets():
        raise ValueError("the retained budget contract drifted")
    if policy.get("max_cost") != 0:
        raise ValueError("the retained budget floated off the zero-cost contract")
    if policy.get("read_only", {}).get("schema") != "d5-box-census-readonly-v1":
        raise ValueError("the retained read-only schema drifted")
    if policy["read_only"]["permitted_ops"] != list(CENSUS_OPS):
        raise ValueError("the retained read-only op set drifted")
    world_pins = policy.get("world")
    if not isinstance(world_pins, dict):
        raise ValueError("the retained plan policy lacks its world pins")
    expected_pins = _census_expected_world(plan)
    for name, expected in expected_pins.items():
        if world_pins.get(name) != expected:
            raise ValueError(f"the retained census world pin {name} drifted")
    if (
        policy.get("company") != plan.company
        or policy.get("target_tile") != int(CENSUS_SPOT_CONTROL_TILE)
        or policy.get("plan_model_digest") != plan.digest
    ):
        raise ValueError("the retained census plan pins drifted")
    if policy.get("box_grid") != _census_box_grid():
        raise ValueError("the retained census box grid drifted from the pinned geometry")
    if policy.get("observations") != [
        dict(
            tile=int(tile),
            kind="CONTROL" if tile == CENSUS_SPOT_CONTROL_TILE else "A1_STOP",
        )
        for tile in plan.spots
    ]:
        raise ValueError("the retained census observation kinds drifted")
    staged_hypotheses = policy.get("hypotheses")
    expected_hypotheses = census_spot_hypotheses()
    if (
        not isinstance(staged_hypotheses, dict)
        or staged_hypotheses.get("state") != expected_hypotheses.get("state")
    ):
        raise ValueError(
            f"the retained census hypothesis record drifted from its version derivation "
            f"({expected_hypotheses.get('state')})"
        )
    return binding


def verify_box_census_attempt(directory: Path) -> dict:
    """Replay the retained protocol-9 phase; never trust a success label.

    The replay re-derives every retained fact independently — operator
    authorization evidence, the staged census schedule, the captured session
    frames, every per-exchange request/response pair — then re-verifies the
    whole schedule with the production
    :func:`app.simulation.openttd.corridor_box_census.census_phase_outcome`
    and the certified-cleanup gate. A forced or invented
    ``CENSUS_COMPLETE`` label alone can never verify; a refused, missing,
    malformed, out-of-range, stale, divergent or inconclusive exchange
    always leaves the verdict incomplete.
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
                "the census candidate was never consumed by an operator "
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
    if metadata.get("schema") != D5_CENSUS_PRELAUNCH_SCHEMA:
        return dict(
            verification="AUTHORIZATION_UNVERIFIED",
            authorization_state="UNKNOWN_PRELAUNCH_SCHEMA",
            statement=(
                f"the prelaunch record is not the launch-capable "
                f"[{D5_CENSUS_PRELAUNCH_SCHEMA!r}] lineage; no verified "
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
    schedule = staged_census_schedule(policy_replay)
    plan = census_plan()
    if policy_replay["schedule"] != schedule or policy_replay["plan_digest"] != plan_digest_of(
        schedule
    ):
        raise ValueError("the staged census schedule drifted from the compiled derivation")
    planned_ids = {row["exchange"] for row in schedule}
    if planned_ids != set(CENSUS_EXCHANGE_IDS) or len(schedule) != PLANNED_CENSUS_EXCHANGES:
        raise ValueError("the retained census schedule drifted from the wire contract")
    verify_box_census_attempt_identity(metadata, plan=plan)
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
    outbound, outbound_requests, replies, request_positions, reply_positions = _parse_census_frames(
        directory
    )
    if len(outbound_requests) > metadata["budgets"]["requests"]:
        raise ValueError("the census request budget exceeded (outbound frames)")
    paths = sorted(directory.glob("*-request.json"))
    file_queries = [CensusRequest.model_validate_json(path.read_bytes()) for path in paths]
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
            raise ValueError(f"a duplicate census request_id: {query.request_id}")
        seen_ids.add(query.request_id)
    response_map = {}
    for path in paths:
        response_path = path.with_name(path.name.replace("-request.json", "-response.json"))
        if response_path.is_file():
            response_map[path.read_bytes()] = response_path.read_bytes()
    for path in sorted(directory.glob("*-response.json")):
        exchange_id = path.name[: -len("-response.json")]
        try:
            readback = CensusReadback.model_validate_json(path.read_bytes())
        except ValueError as error:
            raise ValueError(
                f"the retained response file is not a parseable readback: {path.name}"
            ) from error
        if readback.request_id != exchange_id:
            raise ValueError("the retained response file identity does not match its payload")
        if not (directory / (exchange_id + "-request.json")).is_file():
            raise ValueError("the retained response file lacks its request")
    for raw, response in response_map.items():
        if outbound.count(encode_census_request(raw)) != 1 or replies.count(response) != 1:
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
    exchanges: list[tuple[CensusRequest, CensusReadback]] = []
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
            query = CensusRequest.model_validate_json(request_path.read_bytes())
            raw = response_map.get(query.to_bytes())
            if raw is not None:
                exchanges.append((query, CensusReadback.parse_for(query, raw)))
        if pending:
            break
    phase = census_phase_outcome(exchanges, prelaunch_digest=seal, plan=plan)
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
    if result["status"] == "NATIVE_CENSUS_COMPLETE":
        if phase["verification"] != "CENSUS_COMPLETE":
            raise ValueError("the verified completion contradicts its census phase outcome")
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
            raise ValueError("the census claimed a world change it cannot make")
        if len(outbound_requests) != len(plan.schedule):
            raise ValueError("the verified completion's request inventory drifted")
        if phase["radius"] is None or phase["production"] is None or not phase["observations"]:
            raise ValueError("the verified completion lacks its own re-derived observations")
        if set(phase.get("boxes") or {}) != {str(centre) for centre in plan.box_centres}:
            raise ValueError("the verified completion's box inventory drifted")
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
                raise ValueError("the retained census receipt replay mismatch")
            session_before = json.loads(
                (directory / "session-before-identity.json").read_text()
            ).get("sha256")
            if retained_receipt.get("before_save_sha256") != session_before:
                raise ValueError("the retained census receipt replay mismatch")
        return dict(
            verification="CENSUS_COMPLETION_VERIFIED",
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
            phase["verification"] != "CENSUS_INCOMPLETE"
            or not isinstance(halt_record, dict)
            or len(result.get("exchanges", [])) != len(phase["receipts"])
            or (
                phase["failed"] is not None
                and phase["failed"].get("label") != halt_record.get("label")
            )
        ):
            raise ValueError("the halted census evidence contradicts its retained record")
        if not cleanup_complete:
            raise ValueError("the halted census attempt cleanup incomplete")
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


def staged_census_authorization_payload_digest(directory: Path) -> str:
    """The RFC-canonical digest of the candidate's own authorization payload."""
    directory = directory.resolve()
    metadata = read_prelaunch(directory)
    seal = sha256(directory / "PRELAUNCH.json")
    return hashlib.sha256(
        canonical_authorization_bytes(authorization_payload(metadata, seal))
    ).hexdigest()


def census_exit_status(result: dict) -> int:
    verified = (
        result.get("verified") is True
        and result.get("status") == "NATIVE_CENSUS_COMPLETE"
        and result.get("cleanup_complete") is True
        and result.get("state_changed") is False
    )
    return 0 if verified else 1


def census_verdict_exit_status(verdict: dict) -> int:
    return 0 if verdict.get("verification") == "CENSUS_COMPLETION_VERIFIED" else 1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("prepare", "preflight", "run", "verify"))
    parser.add_argument("directory", type=Path)
    parser.add_argument("--prerequisite", type=Path, default=PINNED_PREREQUISITE)
    args = parser.parse_args()
    directory = args.directory.resolve()
    if args.command == "prepare":
        prepared = prepare_box_census_candidate(directory, prerequisite=args.prerequisite)
        census_preflight(prepared)
        print("PRELAUNCH PASS", directory)
    elif args.command == "preflight":
        census_preflight(freight_native.reopen_candidate(directory))
        print("PREFLIGHT PASS")
    elif args.command == "verify":
        verdict = verify_box_census_attempt(directory)
        print(json.dumps(verdict, sort_keys=True))
        raise SystemExit(census_verdict_exit_status(verdict))
    else:
        read_prelaunch(directory)  # fail fast on any drifted prelaunch record
        result = asyncio.run(
            execute_box_census_attempt(
                freight_native.reopen_candidate(directory),
                CensusNativeBackend(authorized_one_launch=True),
            )
        )
        print(json.dumps(result, sort_keys=True))
        raise SystemExit(census_exit_status(result))


if __name__ == "__main__":
    main()
