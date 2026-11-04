"""D5-F12-DEPOT-RELOAD native staging pipeline (observe-only, offline prep).

The Path A design record (``docs/d5-authoritative-post-mutation-save-pipeline-
2026-11-03.md``, E78 §7 round 3) re-loads the round-2 authoritative world of
record in a fresh native session and re-measures the freight-relevant depot
facts so the digest-only binding of the consumed D5-F12-DEPOT-3 attempt is
never trusted alone. This pipeline stages that one-exchange reload attempt of
record over the retained depot ``after.sav`` exactly as the survey/census
pipelines stage their read-only re-checks over the consumed A1 close-out: a
fresh copy of that save is staged (the retained file itself is never opened
for anything but its own digest), the round-2 attempt must still replay
verify, and the staged GameScript is the additive observe-only handler of its
own package directory (``d5_depot_recheck_package``) — the depot mutation
package's guard machinery mirrored field for field minus every mutating op
``d5_depot_mutation_package`` dispatches only its own six planned exchanges).

The protocol-10 wire contract is reused verbatim on its observe subset:
``app.simulation.openttd.corridor_depot_mutation``'s fail-closed
``DepotRequest``/``DepotReadback`` frames. The single ``reload-00`` exchange
is an observe gate of record: the full v2 ObserveDepot fact set plus the
balance at the exchange boundary and the zero cost of record (an observe
readback can never spend — the recheck's attempt-level spend ceiling is zero,
and the wire ``max_cost`` echo stays the depot contract's forced attempt echo
because the model accepts nothing else). Every measured fact is compared
against the round-2 binding's transcribed facts-of-record (the E82 after-00
measurement) and any divergence halts the recheck STALE_PIN-preservingly at
the exchange itself. The zero fleet cannot ride the observe wire subset: it
stays the round-2 fact of record, transcribed and disclosed — never faked
and never re-measured wire-side.

Zero-mutation discipline of record: no authoritative save of any kind is
emitted — no after-save, no finally-diagnostic save, not even a
session-before identity save — so the world of record stays the staged
authoritative depot ``after.sav`` before and after this attempt, byte-exact.
A save artifact appearing in a consumed recheck candidate is a contradiction
of the attempt itself, and a verified reload binds its loaded-source digest
three ways instead (staged record ≡ run-time binding ≡ retained depot save).

This is not a generic abstraction layer: recheck staging, preflight, sealing,
execution and replay keep the survey, freight, census and depot-mutation
pipelines untouched and cannot accept a ``FreightPlan``, ``AcceptSurveyPlan``,
``BoxCensusPlan`` or a mutating ``DepotRequest`` op, and those pipelines still
cannot accept the recheck's observe-only frames as their own.

Unlike the strictly read-only census but like every native family, this
candidate is a one-shot native observation: one launch, one connection, one
planned exchange, one request budget slot, zero spend, zero mutation, zero
saves. Nothing here launches OpenTTD, connects to a port, writes a claim or
mutates any world or retained artifact.
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
from app.simulation.openttd.admin_protocol import encode_admin_quit
from app.simulation.openttd.corridor_depot_mutation import (
    DEPOT_MUTATION_COMPANY,
    DEPOT_MUTATION_DELIVERY_TILE,
    DEPOT_MUTATION_DEPOT_FRONT_TILE,
    DEPOT_MUTATION_DEPOT_TILE,
    DEPOT_MUTATION_PICKUP_TILE,
    MAX_DEPOT_MUTATION_COST,
    MAX_DEPOT_MUTATION_REQUEST_BYTES,
    MAX_DEPOT_MUTATION_RESPONSE_BYTES,
    DepotRequest,
)
from app.simulation.openttd.gamescript_transport import (
    ADMIN_GAMESCRIPT,
    GameScriptTransport,
    gamescript_subscription,
)
from app.simulation.openttd.proof import corridor_accept_survey_native as survey_native
from app.simulation.openttd.proof import (
    corridor_depot_mutation_native as depot_native,
)
from app.simulation.openttd.proof import (
    corridor_freight_native as freight_native,
)
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
from app.simulation.openttd.proof.road_mutation import console, wait_log
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
RECHECK_PACKAGE = PACKAGES / "d5_depot_recheck_package"
AI_PACKAGE = PACKAGES / "road_company_package"
RECHECK_CLOSURE_ROOT = "app.simulation.openttd.proof.corridor_depot_recheck_native"

KIND = "depot-recheck"
MILESTONE_DEPOT_RECHECK = "D5-F12-DEPOT-RELOAD"
# Single attempt identity of record. Identities are never reused: the
# observe-only reload family runs once per authoritative round-2 world, and
# any later re-load needs its own design record of record first.
RECHECK_ATTEMPT = "D5-F12-DEPOT-RELOAD-1"
D5_DEPOT_RECHECK_PRELAUNCH_SCHEMA = "d5-f12-depot-reload-prelaunch-v1"
# The recheck family keeps the shared native prerequisite lineage schema and
# the shared consumed-launch marker family (`d5-native-prerequisite-attempt-v1`,
# `d5-native-launch-consumed`) — the same shared schemas the freight, survey,
# census and depot candidates bind, per the no-retrofit rule for consumed
# contract families.
D5_DEPOT_RECHECK_PREREQUISITE_SCHEMA = freight_native.D5_FREIGHT_PREREQUISITE_SCHEMA
D5_DEPOT_RECHECK_LAUNCH_CONSUMED_SCHEMA = freight_native.D5_FREIGHT_LAUNCH_CONSUMED_SCHEMA
if D5_DEPOT_RECHECK_PREREQUISITE_SCHEMA != survey_native.D5_SURVEY_PREREQUISITE_SCHEMA:
    raise RuntimeError(
        "the depot recheck prerequisite schema drifted from the shared lineage schema"
    )

# The zero-spend and one-exchange attempt profile of record. The wire
# ``max_cost`` echo is the depot contract's forced figure (MAX_DEPOT_MUTATION_
# COST exactly); the recheck's own ceiling is zero and no spend-capable op
# exists in its profile.
RECHECK_OP = "observe"
RECHECK_EXCHANGE_ID = "reload-00"
PLANNED_RECHECK_EXCHANGES = 1
RECHECK_MAX_COST = 0
RECHECK_REQUEST_BUDGET = 1
RECHECK_MAX_REQUEST_BYTES = MAX_DEPOT_MUTATION_REQUEST_BYTES
RECHECK_MAX_RESPONSE_BYTES = MAX_DEPOT_MUTATION_RESPONSE_BYTES

if RECHECK_EXCHANGE_ID != "reload-00" or RECHECK_OP != "observe":
    raise RuntimeError("the depot recheck schedule of record drifted")

# The depot GameScript readiness marker is its own (the staged handlers log
# "D5_F12_DEPOT_RECHECK_READY" at Start); the road-company readiness marker
# follows the staged AI bootstrap exactly as protocols 6/9/10 do.
RECHECK_READY_MARKER = "D5_F12_DEPOT_RECHECK_READY"

RECHECK_EXCHANGE_MARGIN_SECONDS = freight_native.FREIGHT_EXCHANGE_MARGIN_SECONDS

# The reload session's world identity of record. Seed 17 / landscape 0 /
# 256x256 / revision 15.3 are pinned exact (the retained Seed-17 corridor
# world); ``start_day`` is load-derived for a saved world, so the pin of
# record is its floor — the depot attempt's own welcome pin — recorded and
# replayed verbatim under the ">= floor" semantics here and in the run/verify
# gates. Any received start_day below the floor refuses the reload identity.
RECHECK_START_DAY_FLOOR = 712223
RECHECK_EXPECTED_WELCOME = dict(
    revision="15.3",
    seed=17,
    landscape=0,
    start_day=RECHECK_START_DAY_FLOOR,
    width=256,
    height=256,
)

# The reload receipt of record (the round-3 family's own world binding for
# the downstream freight lineage): written once by the verified run, then
# compared byte-exactly by every replay.
RECHECK_AFTER_RECEIPT_NAME = "after-reload-receipt.json"
RECHECK_AFTER_RECEIPT_SCHEMA = "d5-f12-depot-reload-receipt-v1"
RECHECK_AFTER_RECEIPT_STATEMENT = (
    "the reload's measured receipt of record: the single observe exchange "
    "measured the loaded round-2 authoritative world's facts and funds "
    "fresh and they equal the round-2 binding exactly; no save of any kind "
    "is emitted, the loaded world of record stays the retained depot "
    "after-save both before and after this attempt, and the zero fleet is "
    "the round-2 fact of record transcribed here — the observe wire cannot "
    "carry fleet fields, so it is disclosed, never faked or re-measured"
)

# Zero-save discipline of record: none of these artifact names may exist in
# a consumed recheck candidate (the recheck writes none of them, and their
# presence contradicts the zero-mutation capsule itself).
RECHECK_FORBIDDEN_ARTIFACTS = (
    depot_native.DEPOT_AFTER_SAVE_NAME,
    "session-before.sav",
    "after-diagnostic.sav",
    "session-before-identity.json",
    "receipt.json",
)

# Prerequisite lineage of record: the pinned, consumed, replay-verified
# round-2 depot attempt (``D5-F12-DEPOT-3``, candidate-3) at its retained
# authoritative after-save digest — the Path A world of record the freight
# lineage consumes downstream (E78/E82).
RECHECK_PREREQUISITE = (
    PROJECT / "artifacts/experiments/d5-corridor-depot-mutation-native-candidate-3"
).resolve()
RECHECK_PREREQUISITE_AFTER_SAVE = (
    "183b20273a54ebe1a2cd9306145a9ea820bbd6114b1608c42079b4e1b1efe6a6"
)
RECHECK_PREREQUISITE_ATTEMPT = "D5-F12-DEPOT-3"
RECHECK_PREREQUISITE_MILESTONE = "D5-F12-DEPOT"


class RecheckStagingError(freight_native.FreightStagingError):
    """Offline depot recheck staging or pin derivation failed; nothing was launched."""


# --- Migration safety: the recheck pipeline is recheck-typed -----------------


def _require_recheck_schedule(schedule: list[dict]) -> list[dict]:
    """Refuse any schedule that is not the pinned one-exchange observe gate."""
    if schedule != [dict(exchange=RECHECK_EXCHANGE_ID, op=RECHECK_OP)]:
        raise RecheckStagingError(
            "the depot recheck pipeline accepts the one pinned reload observe gate only"
        )
    return schedule


# --- The pinned depot recheck schedule ---------------------------------------


def recheck_schedule() -> list[dict]:
    """The fixed one-exchange reload schedule as a staged plan row.

    The single planned exchange is the observe gate of record: a drifted
    world is caught at the one read itself, nothing follows it in this
    package, and no op outside the observe subset can ever enter the
    schedule, the session surface or the replay.
    """
    return _require_recheck_schedule([dict(exchange=RECHECK_EXCHANGE_ID, op=RECHECK_OP)])


def staged_recheck_schedule(policy: dict) -> list[dict]:
    """The staged schedule one plan-policy record binds its digest to."""
    if policy.get("schedule_version", 0) != 1:
        raise ValueError(
            f"plan record names an unknown depot recheck schedule version: "
            f"{policy.get('schedule_version', 0)}"
        )
    return recheck_schedule()


# --- Hypotheses (retained E78 §7 record), never facts ------------------------


def recheck_hypotheses(binding: dict) -> dict:
    """The E78 §7 round-3 spec re-bound as recheck hypotheses.

    ``docs/d5-authoritative-post-mutation-save-pipeline-2026-11-03.md`` (E78)
    is the authority of record for the round-3 reload family; this derivation
    binds that doc by path and sha256 and re-binds its round-3 rows as the
    fixed comparisons the staged record pins. The facts and funds of record
    are transcribed from the round-2 binding (never invented) and are
    re-measured fresh by the one observe exchange; any divergence halts the
    recheck STALE_PIN-preservingly at the exchange itself. Absent retained
    evidence (a fresh clone) is recorded as ``RETAINED_E78_ABSENT`` — the
    staged facts of record stay the gates of record anyway and no hypothesis
    is invented; nothing is normalized, and the staged record never claims
    the doc proves the loaded world (that is what the attempt measures).
    """
    doc_path = PROJECT / "docs" / "d5-authoritative-post-mutation-save-pipeline-2026-11-03.md"
    facts = dict(binding["facts_of_record"])
    funds = int(binding["funds_of_record"])
    fleet = int(binding["fleet_of_record"])
    if not doc_path.is_file():
        return dict(
            state="RETAINED_E78_ABSENT",
            facts_of_record=facts,
            funds_of_record=funds,
            fleet_of_record=fleet,
            source=None,
            source_sha256=None,
            statement=(
                "the E78 design record is absent from this checkout; the "
                "staged facts of record stay the gates of record anyway and "
                "no hypothesis is invented"
            ),
        )
    text = doc_path.read_text()
    for needle in (
        "D5-F12-DEPOT-RELOAD-1",
        "d5-f12-depot-reload-prelaunch-v1",
        "DEPOT_RELOAD_FACTS_VERIFIED",
        "corridor_depot_recheck_native.py",
    ):
        if needle not in text:
            raise RecheckStagingError(f"the E78 §7 spec of record lost its {needle} text")
    return dict(
        state="RETAINED_E78_REBOUND",
        facts_of_record=facts,
        funds_of_record=funds,
        fleet_of_record=fleet,
        source="docs/d5-authoritative-post-mutation-save-pipeline-2026-11-03.md",
        source_sha256=hashlib.sha256(doc_path.read_bytes()).hexdigest(),
        statement=(
            "the round-3 reload spec is the E78 design record §7 re-bound as "
            "fixed comparisons: the measured facts and funds are the round-2 "
            "binding's own facts of record (transcribed, never invented) "
            "re-measured fresh by the one observe exchange, the zero fleet "
            "stays the transcribed fact of record (the observe wire cannot "
            "carry fleet fields), the zero-spend and zero-save disciplines "
            "stand, and any divergence halts the recheck STALE_PIN-"
            "preservingly at the exchange itself"
        ),
        derivation="corridor_depot_recheck_native.recheck_hypotheses",
    )


# --- The recheck plan policy, budgets and readback story ---------------------


def recheck_profile() -> dict:
    """The authorized observe-only profile for the staged recheck candidate."""
    return dict(
        schema="d5-f12-depot-reload-profile-v1",
        permitted_ops=["observe"],
        mutating_ops=[],
        observation_ops=["observe"],
        max_cost=RECHECK_MAX_COST,
        wire_max_cost_echo=int(MAX_DEPOT_MUTATION_COST),
        zero_spend_required=True,
        facts_of_record_source=(
            "the consumed round-2 depot attempt's own after-save binding"
        ),
        statement=(
            "exactly one measurement op exists in this candidate — the depot "
            "observe instrument over the pinned depot tile and front — and "
            "it can never spend: the wire max_cost echo stays the depot "
            "contract's forced attempt echo because DepotRequest accepts "
            "nothing else, while the recheck's own attempt-level ceiling is "
            "zero and no spend-capable op exists; no save and no mutation "
            "can exist in this profile"
        ),
    )


def _recheck_expected_world(binding: dict) -> dict:
    """The expected world-pin set of the staged recheck candidate."""
    return dict(
        depot=int(DEPOT_MUTATION_DEPOT_TILE),
        depot_front=int(DEPOT_MUTATION_DEPOT_FRONT_TILE),
        company=int(DEPOT_MUTATION_COMPANY),
        facts_of_record=dict(binding["facts_of_record"]),
        funds_of_record=int(binding["funds_of_record"]),
        fleet_of_record=int(binding["fleet_of_record"]),
        statement=(
            "the staged reload world is the consumed round-2 depot after-save: "
            "the facts of record (the E82 after-00 measurement) and the funds "
            "of record are transcribed from the depot attempt's own after-save "
            "binding, and the reload re-measures them fresh and demands exact "
            "equality; the zero fleet stays a fact of record the observe wire "
            "cannot carry, disclosed here instead of faked"
        ),
    )


def recheck_plan_policy(binding: dict) -> dict:
    """The authorized plan policy for the staged recheck candidate."""
    schedule = recheck_schedule()
    plan_digest = plan_digest_of(schedule)
    plan = depot_native.depot_plan()
    if schedule[0]["exchange"] != RECHECK_EXCHANGE_ID or schedule[0]["op"] != RECHECK_OP:
        raise RecheckStagingError("the recheck schedule must begin with the reload observe gate")
    return dict(
        company=int(DEPOT_MUTATION_COMPANY),
        target_tile=int(DEPOT_MUTATION_DEPOT_TILE),
        max_cost=RECHECK_MAX_COST,
        wire_max_cost_echo=int(MAX_DEPOT_MUTATION_COST),
        command="",
        command_statement=(
            "the staged recheck carries no command of any kind — no demolish, "
            "no road, no depot, no fleet read, no terraform, no save; the one "
            "observe exchange records measurements only"
        ),
        stale_rule=(
            "compare every measured reload fact and the measured funds with "
            "the round-2 binding of record at the one read, immediately; any "
            "mismatch stops the recheck without any command and preserves "
            "the empty prefix"
        ),
        identity=(
            "wire contract protocol 10 observe subset: the reload exchange "
            "presents one uniform prelaunch seal digest and the pinned "
            "corridor identity, and records measurements only (one session, "
            "one company, zero commands)"
        ),
        schedule=schedule,
        plan_digest=plan_digest,
        plan_model_digest=plan.digest,
        schedule_version=1,
        observations=[
            dict(exchange=row["exchange"], kind="GATE", tile=None, front_tile=None)
            for row in schedule
        ],
        hypotheses=recheck_hypotheses(binding),
        profile=recheck_profile(),
        world=_recheck_expected_world(binding),
    )


def recheck_budgets() -> dict:
    """The staged budget table for the recheck candidate."""
    return dict(
        launches=1,
        connection_attempts=1,
        requests=RECHECK_REQUEST_BUDGET,
        planned_exchanges=PLANNED_RECHECK_EXCHANGES,
        gsadmin_bytes=RECHECK_MAX_REQUEST_BYTES,
        response_bytes=RECHECK_MAX_RESPONSE_BYTES,
        retries=0,
        reconnects=0,
        readiness_seconds=45,
        request_seconds=10,
        total_seconds=120,
        max_cost=RECHECK_MAX_COST,
    )


def recheck_expected_readback_policy() -> dict:
    return dict(
        observe=(
            "the reload exchange returns READY with the complete v2 "
            "ObserveDepot fact set (depot_present, front_read, owner, "
            "depot_linked, both AreRoadTilesConnected directions) plus the "
            "balance at the exchange boundary and the zero cost of record; "
            "every fact is compared with the round-2 binding's facts of "
            "record and any divergence halts the recheck STALE_PIN-"
            "preservingly at the exchange itself"
        ),
        fleet=(
            "the observe wire subset cannot carry fleet fields: the zero "
            "fleet stays the round-2 fact of record transcribed into the "
            "staged world pins and the reload receipt, disclosed — never "
            "faked and never re-measured wire-side"
        ),
        zero_save=(
            "no save of any kind is emitted by this attempt: no authoritative "
            "save, no finally-diagnostic save and no session-before save; the "
            "world of record is the staged depot after-save and nothing may "
            "relabel that"
        ),
        receipt=(
            "after-reload-receipt.json (schema d5-f12-depot-reload-receipt-v1) "
            "binds the measured phase, the loaded-source digest and the "
            "facts of record; NATIVE_DEPOT_RELOAD_COMPLETE only after the one "
            "exchange verifies with certified cleanup, the zero-spend and "
            "zero-mutation demands hold and the nothing-was-saved discipline "
            "stands; any refusal keeps the recheck incomplete forever"
        ),
    )


# --- Depot recheck prerequisite binding (round-2 lineage) --------------------


def recheck_prerequisite_binding(prerequisite: Path | None = None) -> dict:
    """Bind the consumed round-2 depot attempt of record, recheck-scoped.

    The recheck prerequisite is exactly the pinned Path A world of record:
    the consumed, fully replay-verified round-2 depot attempt
    (``D5-F12-DEPOT-3``, candidate-3) at its retained authoritative
    ``after.sav`` digest. The checked derivation of record runs the depot
    candidate's own full replay verification
    (``depot_native.verify_depot_mutation_attempt`` →
    ``F12_MUTATION_COMPLETION_VERIFIED``) and cross-checks its retained
    after-save binding against the replayed phase (edge facts ≡ the phase's
    after-00 facts, funds ≡ the funds chain's close, fleet ≡ the zero fleet).
    The retained save is only ever read here — never opened for writing,
    moved or rewritten. A wrong directory is a recheck staging error before
    any world is staged.
    """
    prerequisite = Path(RECHECK_PREREQUISITE if prerequisite is None else prerequisite).resolve()
    if prerequisite != RECHECK_PREREQUISITE.resolve():
        raise RecheckStagingError(
            "the depot recheck world requires the pinned round-2 depot attempt"
        )
    retained_save = Path(prerequisite) / depot_native.DEPOT_AFTER_SAVE_NAME
    if retained_save.is_symlink() or not retained_save.is_file():
        raise RecheckStagingError(
            "the pinned prerequisite after-save is not a retained regular file"
        )
    if sha256(retained_save) != RECHECK_PREREQUISITE_AFTER_SAVE:
        raise RecheckStagingError(
            "the retained prerequisite after-save digest drifted from its pinned record"
        )
    metadata = read_prelaunch(prerequisite)
    if (
        metadata.get("attempt") != RECHECK_PREREQUISITE_ATTEMPT
        or metadata.get("milestone") != RECHECK_PREREQUISITE_MILESTONE
    ):
        raise RecheckStagingError("the recheck prerequisite is not the pinned D5-F12-DEPOT-3")
    depot_welcome = metadata["world"]["expected_welcome"]
    for field, pinned in RECHECK_EXPECTED_WELCOME.items():
        if field == "start_day":
            if depot_welcome.get(field) is None or depot_welcome.get(field) < pinned:
                raise RecheckStagingError(
                    "the depot prerequisite welcome start_day sits below the reload floor"
                )
        elif depot_welcome.get(field) != pinned:
            raise RecheckStagingError(
                "the depot prerequisite welcome drifted from the pinned reload identity"
            )
    verdict = depot_native.verify_depot_mutation_attempt(prerequisite)
    if verdict.get("verification") != "F12_MUTATION_COMPLETION_VERIFIED":
        raise RecheckStagingError(
            "the depot prerequisite replay is not a verified depot mutation completion"
        )
    binding_path = Path(prerequisite) / depot_native.DEPOT_AFTER_SAVE_BINDING_NAME
    if not binding_path.is_file():
        raise RecheckStagingError("the depot prerequisite after-save binding is absent")
    depot_binding = json.loads(binding_path.read_text())
    if (
        depot_binding.get("schema") != depot_native.DEPOT_AFTER_SAVE_BINDING_SCHEMA
        or depot_binding.get("attempt") != RECHECK_PREREQUISITE_ATTEMPT
        or depot_binding.get("milestone") != RECHECK_PREREQUISITE_MILESTONE
        or depot_binding.get("after_save_sha256") != RECHECK_PREREQUISITE_AFTER_SAVE
        or depot_binding.get("saved_at_fleet_exchange") != depot_native.DEPOT_AFTER_SAVE_SAVED_AT
        or depot_binding.get("source_world") != depot_native.PINNED_PREREQUISITE_AFTER_SAVE
    ):
        raise RecheckStagingError(
            "the depot prerequisite after-save binding drifted from its record"
        )
    phase = verdict["receipt"]["phase"]
    if phase.get("gate", {}).get("verdict") != "DEPOT_MUTATION_GATE_PASSES":
        raise RecheckStagingError("the depot prerequisite phase gate is not the pass verdict")
    if not phase.get("funds_chain"):
        raise RecheckStagingError("the depot prerequisite phase lacks its funds chain")
    if depot_binding.get("funds_at_close") != phase["funds_chain"][-1]["funds_after"]:
        raise RecheckStagingError("the depot prerequisite funds of record drifted from its phase")
    after_facts = (phase.get("observations") or {}).get("after-00", {}).get("facts")
    if after_facts is None or depot_binding.get("edge_facts") != after_facts:
        raise RecheckStagingError(
            "the depot prerequisite facts of record drifted from its phase"
        )
    if phase.get("fleet") is None or phase["fleet"].get("count") != depot_binding.get(
        "fleet_count"
    ):
        raise RecheckStagingError("the depot prerequisite fleet of record drifted from its phase")
    if phase["fleet"]["count"] != 0:
        raise RecheckStagingError("the depot prerequisite fleet of record is not the zero fleet")
    return dict(
        schema=D5_DEPOT_RECHECK_PREREQUISITE_SCHEMA,
        role="PREREQUISITE_ATTEMPT",
        retained_directory=str(prerequisite),
        save=depot_native.DEPOT_AFTER_SAVE_NAME,
        save_sha256=RECHECK_PREREQUISITE_AFTER_SAVE,
        qualified_save_sha256=metadata["world"].get("qualified_save_sha256"),
        prelaunch_digest=depot_binding["prelaunch_sha256"],
        attempt=RECHECK_PREREQUISITE_ATTEMPT,
        milestone=RECHECK_PREREQUISITE_MILESTONE,
        expected_welcome=dict(RECHECK_EXPECTED_WELCOME),
        facts_of_record=dict(depot_binding["edge_facts"]),
        funds_of_record=int(depot_binding["funds_at_close"]),
        fleet_of_record=int(depot_binding["fleet_count"]),
        verification=(
            "full replay verification of the consumed round-2 depot attempt "
            "receipt (F12_MUTATION_COMPLETION_VERIFIED) plus its pinned "
            "authoritative after-save digest and its after-save binding's "
            "facts/funds/fleet-of-record cross-checks against the replayed "
            "phase (the round-2 facts of record are transcribed here, never "
            "invented, and re-measured fresh by the reload)"
        ),
        provenance=dict(
            schema=depot_native.D5_DEPOT_MUTATION_PRELAUNCH_SCHEMA,
            attempt=RECHECK_PREREQUISITE_ATTEMPT,
            milestone=RECHECK_PREREQUISITE_MILESTONE,
            prelaunch_sha256=depot_binding["prelaunch_sha256"],
            after_save_sha256=RECHECK_PREREQUISITE_AFTER_SAVE,
            after_save_size_bytes=depot_binding["save_size_bytes"],
            replay="F12_MUTATION_COMPLETION_VERIFIED",
            funds_at_close=int(depot_binding["funds_at_close"]),
            fleet_count=int(depot_binding["fleet_count"]),
            statement=(
                "the round-2 authoritative world of record (Path A): the "
                "depot attempt's strict after-save binds the post-mutation "
                "facts of record; the recheck reloads exactly these bytes "
                "and demands the measured facts and funds equal them"
            ),
        ),
    )


def _recheck_prerequisite_record(binding: dict) -> dict:
    """The staged ``prerequisite`` record shape for one recheck binding."""
    return dict(
        schema=D5_DEPOT_RECHECK_PREREQUISITE_SCHEMA,
        attempt=binding["attempt"],
        milestone=binding["milestone"],
        directory=binding["retained_directory"],
        after_save=binding["save"],
        after_save_sha256=binding["save_sha256"],
        verification=binding["verification"],
    )


def _recheck_world_record(binding: dict) -> dict:
    """The staged ``world`` record shape for one recheck binding."""
    return stage_world(
        dict(
            retained_directory=binding["retained_directory"],
            save=binding["save"],
            save_sha256=binding["save_sha256"],
            qualified_save_sha256=binding.get("qualified_save_sha256"),
        ),
        binding["expected_welcome"],
    )


# --- Depot recheck candidate staging -----------------------------------------


def staged_recheck_composition() -> tuple[dict[str, bytes], str, int]:
    """Byte-exact save-restore composition for the D5-F12-DEPOT-RELOAD-1
    candidate.

    The retained staged ``info.nut`` announces the save's stored GameScript
    identity (name/version); the staged main is the observe-only reload
    handler of its own package directory (``d5_depot_recheck_package``) with
    the save-restore bridge class defined inline after the proof class. The
    frozen census/freight/depot bytes the E47/E64/E79 stagings pinned never
    drift for the recheck handler's sake.
    """
    with zipfile.ZipFile(SEED17_RUN / "frozen-source.zip") as archive:
        info_bytes = archive.read("staged/info.nut")
    text = info_bytes.decode()
    create_instance = re.search(r'CreateInstance\(\)\s*\{\s*return\s+"([^"]+)"', text)
    version = re.search(r"GetVersion\(\)\s*\{\s*return\s+(\d+)", text)
    if create_instance is None or version is None or SOURCE_SAVE_GS_NAME not in text:
        raise RecheckStagingError("retained staged GameScript identity incomplete")
    main_text = (RECHECK_PACKAGE / "main.nut").read_text()
    bridge_class = create_instance.group(1)
    expected_bridge = f"class {bridge_class} extends D5DepotRecheckProof"
    if expected_bridge not in main_text:
        raise RecheckStagingError(
            f"staged recheck main.nut missing required bridge class {bridge_class}"
        )
    return (
        {
            "info.nut": info_bytes,
            "main.nut": main_text.encode(),
        },
        bridge_class,
        int(version.group(1)),
    )


def prepare_depot_recheck_candidate(
    directory: Path, *, prerequisite: Path | None = None
) -> PreparedProof:
    """Stage the fresh save-load composition; no process or connection."""
    prerequisite = Path(RECHECK_PREREQUISITE if prerequisite is None else prerequisite).resolve()
    if prerequisite != RECHECK_PREREQUISITE.resolve():
        raise RecheckStagingError(
            "the depot recheck world requires the pinned round-2 depot attempt"
        )
    if sha256(BINARY) != BINARY_SHA256 or matching_processes(BINARY):
        raise RecheckStagingError("pinned binary / exclusive runtime gate failed")
    directory = directory.resolve()
    binding = recheck_prerequisite_binding(prerequisite)
    policy = recheck_plan_policy(binding)
    world = _recheck_world_record(binding)
    if sha256(source_save_path(world)) != world["save_sha256"]:
        raise RecheckStagingError("the staged source-save digest mismatch")
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
        composition, create_instance, version = staged_recheck_composition()
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
        for source in (RECHECK_PACKAGE, AI_PACKAGE):
            for path in sorted(source.glob("*.nut")):
                frozen[str(path.resolve())] = sha256(path)
        frozen.update(
            {
                str(path): sha256(path)
                for path in sorted(workspace.root.rglob("*"))
                if path.is_file() and path.name != ".admin-secret"
            }
        )
        frozen.update(freight_native.d2_source_closure(RECHECK_CLOSURE_ROOT))
        frozen.update(freight_native.d2_dependency_inventory(RECHECK_CLOSURE_ROOT))
        prepared = PreparedProof(
            directory,
            spec,
            key_path,
            key.public_hex,
            (reservation.game_port, reservation.admin_port),
        )
        metadata = dict(
            schema=D5_DEPOT_RECHECK_PRELAUNCH_SCHEMA,
            milestone=MILESTONE_DEPOT_RECHECK,
            kind=KIND,
            attempt=RECHECK_ATTEMPT,
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
                    "observe-only D5DepotRecheckProof ships in its own "
                    "bounded package (d5_depot_recheck_package) and "
                    "satisfies the frozen save-restore identity through its "
                    "bridge class"
                ),
            ),
            save_policy=(
                "zero-mutation observe-only session: no authoritative save "
                "and no finally-diagnostic save is emitted at any point (not "
                "even a session-before identity save); the world of record "
                "is the staged authoritative depot after-save and it stays "
                "byte-exact before and after this attempt; the loaded "
                "source copy is digest-bound at staging and at the run "
                "boundary, and no save file of any kind may appear in the "
                "candidate directory"
            ),
            plan_policy=policy,
            expected_readback=recheck_expected_readback_policy(),
            bootstrap_command=f"start_ai {STAGED_AI_DIRECTORY}",
            execution_command=[
                str(PROJECT / ".venv/bin/python"),
                "-m",
                "app.simulation.openttd.proof.corridor_depot_recheck_native",
                "run",
                str(directory),
            ],
            budgets=recheck_budgets(),
            cleanup=[
                "close secure session",
                "quit and reap process",
                "verify endpoints",
                "retain session logs",
                "emit no save of any kind (the zero-mutation discipline): "
                "the world of record stays the retained depot after-save "
                "before and after this attempt",
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
                    "the depot recheck binds the authoritative round-2 "
                    "after-save (183b20273a54ebe1a2cd9306145a9ea820bbd6114b1"
                    "608c42079b4e1b1efe6a6) and the pinned OpenTTD 15.3 "
                    "binary; the pinned one-exchange observe schedule is the "
                    "recheck module's own guarded derivation over the depot "
                    "wire contract's observe subset, and the facts/funds/ "
                    "fleet of record are transcribed from the depot attempt's "
                    "own after-save binding and re-measured fresh; the "
                    "welcome identity is pinned exact on seed/landscape/"
                    "dims/revision with start_day as its load-derived floor "
                    "(>= 712223, the depot attempt's own welcome pin); the "
                    "attempt emits no save of any kind"
                ),
            ),
            environment=freight_native.launch_environment(prepared),
            environment_overrides=dict(spec.environment),
            frozen=frozen,
            cross_schedule_guard=dict(
                schema="d5-f12-depot-reload-cross-guard-v1",
                observe_ops=["observe"],
                mutating_ops=[],
                statement=(
                    "this candidate carries the observe-only protocol-10 "
                    "reload profile: a depot mutating op (any demolish/road/"
                    "depot frame) or a fleet frame fails the recheck session "
                    "schema check, a freight request (any protocol-5 op), a "
                    "survey request (any protocol-6 op) and a census request "
                    "(any protocol-9 op) fail it the same way, and any "
                    "recheck frame fails the freight, survey, census and "
                    "depot-mutation session checks with their required "
                    "protocols and dispatched ops"
                ),
            ),
        )
        metadata["prerequisite"] = _recheck_prerequisite_record(binding)
        write_json(directory / "PRELAUNCH.json", metadata)
        (directory / "PRELAUNCH.sha256").write_text(sha256(directory / "PRELAUNCH.json") + "\n")
        return prepared
    finally:
        reservation.close()


# --- Depot recheck preflight (offline launch-boundary rehearsal) -------------


def recheck_preflight(prepared: PreparedProof) -> dict:
    """Offline launch-boundary rehearsal: re-derive every binding, trust nothing.

    The depot recheck has one schedule version and one derivation; every
    derivation below is re-derived from the module pins and the staged
    record must match it exactly, so a record claiming a foreign lineage or
    a drifted schedule is refused here.
    """
    directory = prepared.directory
    if sha256(directory / "PRELAUNCH.json") != (directory / "PRELAUNCH.sha256").read_text().strip():
        raise ValueError("the recheck prelaunch seal mismatch")
    metadata = read_prelaunch(directory)
    if (directory / "CLAIM.json").exists():
        raise ValueError("the one native attempt already consumed")
    if metadata.get("schema") != D5_DEPOT_RECHECK_PRELAUNCH_SCHEMA:
        raise ValueError("the staged prelaunch record is not the D5 reload lineage")
    if metadata.get("kind") != KIND or metadata.get("milestone") != MILESTONE_DEPOT_RECHECK:
        raise ValueError("the staged recheck lineage drifted")
    if metadata.get("attempt") != RECHECK_ATTEMPT:
        raise ValueError("the staged attempt identity drifted from its own scope")
    verify_freeze(metadata["frozen"])
    freight_native.require_frozen_d2_closure(metadata["frozen"], RECHECK_CLOSURE_ROOT)
    freight_native.require_frozen_d2_dependencies(metadata["frozen"], RECHECK_CLOSURE_ROOT)
    binding = recheck_prerequisite_binding(Path(metadata["prerequisite"].get("directory", "")))
    if metadata["prerequisite"] != _recheck_prerequisite_record(binding):
        raise ValueError("the staged prerequisite binding drifted from its verified record")
    if metadata["prerequisite"].get("schema") != D5_DEPOT_RECHECK_PREREQUISITE_SCHEMA:
        raise ValueError("the staged prerequisite schema drifted")
    if metadata["world"] != _recheck_world_record(binding):
        raise ValueError("the staged world is not the pinned depot after-save record")
    if metadata["world"]["source_save"] != depot_native.DEPOT_AFTER_SAVE_NAME:
        raise ValueError("the staged world save name drifted")
    if metadata["world"]["save_sha256"] != RECHECK_PREREQUISITE_AFTER_SAVE:
        raise ValueError("the staged world is not the pinned round-2 authoritative after-save")
    if metadata["world"]["expected_welcome"] != binding["expected_welcome"]:
        raise ValueError("the retained world identity requirements drifted")
    policy = metadata["plan_policy"]
    schedule = staged_recheck_schedule(policy)
    if policy["schedule"] != schedule or policy["plan_digest"] != plan_digest_of(schedule):
        raise ValueError("the staged recheck schedule drifted from the compiled derivation")
    if policy["plan_model_digest"] != depot_native.depot_plan().digest:
        raise ValueError("the staged corridor-identity plan digest drifted from the pinned plan")
    if policy.get("schedule_version") != 1:
        raise ValueError("the staged recheck schedule version drifted")
    if policy.get("max_cost") != RECHECK_MAX_COST:
        raise ValueError("the staged recheck budget drifted off its zero-spend ceiling")
    if policy["profile"]["schema"] != "d5-f12-depot-reload-profile-v1":
        raise ValueError("the staged recheck profile schema drifted")
    if policy["profile"] != recheck_profile():
        raise ValueError("the staged recheck withdraw profile drifted")
    for row in schedule:
        if row["op"] != RECHECK_OP:
            raise ValueError("a scheduled recheck row carries a foreign op outside the profile")
        if row["exchange"] != RECHECK_EXCHANGE_ID:
            raise ValueError("a scheduled recheck row carries a foreign exchange identity")
    if policy.get("observations") != [
        dict(exchange=row["exchange"], kind="GATE", tile=None, front_tile=None) for row in schedule
    ]:
        raise ValueError("the staged recheck observation kinds drifted")
    staged_hypotheses = policy["hypotheses"]
    expected_hypotheses = recheck_hypotheses(binding)
    if staged_hypotheses.get("state") != expected_hypotheses.get("state"):
        raise ValueError(
            f"the staged recheck hypothesis state is not its own derivation "
            f"({expected_hypotheses.get('state')})"
        )
    if expected_hypotheses.get("state") == "RETAINED_E78_REBOUND":
        if staged_hypotheses != expected_hypotheses:
            raise ValueError("the staged recheck hypothesis record drifted from the retained bytes")
    if metadata.get("budgets") != recheck_budgets():
        raise ValueError("the staged recheck budget pins drifted")
    if metadata["public_key"] != prepared.public_key or metadata["binary_sha256"] != BINARY_SHA256:
        raise ValueError("the staged identity pins drifted")
    if metadata["save_policy"].count("no authoritative save") != 1 or (
        "no finally-diagnostic save" not in metadata["save_policy"]
        or "no save file of any kind" not in metadata["save_policy"]
    ):
        raise ValueError("the staged save policy lost its zero-save discipline of record")
    verify_staged_source_save(
        {"save_sha256": metadata["world"]["save_sha256"]},
        Path(metadata["workspace"]) / "source.sav",
    )
    composition, _, _ = staged_recheck_composition()
    staged_identity = Path(metadata["workspace"]) / "game" / SOURCE_SAVE_GS_NAME
    if staged_identity.joinpath("info.nut").read_bytes() != composition["info.nut"]:
        raise ValueError("the staged GameScript identity drifted from the retained composition")
    if staged_identity.joinpath("main.nut").read_bytes() != composition["main.nut"]:
        raise ValueError("the staged recheck handler drifted from its bounded package")
    if not prepared.spec.workspace.root.is_relative_to(directory / "isolated"):
        raise ValueError("the workspace ownership mismatch")
    ClearingNativeBackend(authorized_one_launch=True).preflight(prepared)
    reservation = EndpointReservation.allocate(*prepared.endpoints)
    reservation.close()
    return metadata


# --- Wire protocol 10: secure session and one-launch backend -----------------


def encode_recheck_request(payload: bytes) -> bytes:
    return depot_native.encode_depot_request(payload)


def decode_recheck_request(payload: bytes) -> bytes:
    return depot_native.decode_depot_request(payload)


class DepotRecheckSecureSession(depot_native.DepotMutationSecureSession):
    """Only the observe subset extends the depot session's write policy.

    A depot mutating op (demolish/road/depot) or a fleet frame cannot ride
    the observe-only recheck session, and no freight/survey/census frame
    can (protocol 10 required and the foreign op sets are outside the
    observe subset). The single planned exchange identity is enforced here
    before any frame can ever leave the candidate.
    """

    def validate_outbound(self, frame: bytes) -> None:
        if self.state is not AuthState.ACTIVE:
            raise ValueError("encrypted ACTIVE stream required")
        if len(frame) < 3 or struct.unpack_from("<H", frame)[0] != len(frame):
            raise ValueError("invalid frame")
        if frame[2] == ADMIN_GAMESCRIPT:
            request = DepotRequest.model_validate_json(decode_recheck_request(frame[3:]))
            if request.op != RECHECK_OP:
                raise ValueError("a non-observe op cannot ride the observe-only recheck session")
            if request.request_id != RECHECK_EXCHANGE_ID:
                raise ValueError("a foreign exchange identity cannot ride the recheck session")
            request.to_bytes()
        elif frame not in (gamescript_subscription(), encode_admin_quit()):
            SecureAdminSession.validate_outbound(self, frame)


class DepotRecheckNativeBackend(depot_native.DepotMutationNativeBackend):
    """One-launch backend carrying the shared consumed marker, recheck session."""

    launch_marker_schema = D5_DEPOT_RECHECK_LAUNCH_CONSUMED_SCHEMA

    async def connect(self, prepared: PreparedProof, *, frame_observer):
        if not any(
            r["table"] == "tcp" and r["local_port"] == prepared.endpoints[1] and r["state"] == 10
            for r in kernel_socket_rows()
        ):
            raise ValueError("the native Admin listener readiness absent")
        key = AuthorizedKey.from_bytes(prepared.key_path.read_bytes())
        session = await DepotRecheckSecureSession.connect_secure(
            "127.0.0.1",
            prepared.endpoints[1],
            5,
            key=key,
            frame_observer=frame_observer,
        )
        self.session = session
        return session


def recheck_exchange_timeout_seconds(*, budget_table: dict, op: str) -> float:
    """The one recheck op is a bounded immediate request/readback; no windows."""
    if op != RECHECK_OP:
        raise ValueError("no depot recheck budget exists for a foreign op")
    return float(budget_table["request_seconds"])


def event_loop_deadline(seconds: float) -> float:
    return time.monotonic() + seconds


def _recheck_exchange_request(entry: dict, seal: str) -> DepotRequest:
    """Build the one fixed recheck request: pins, its observe op, the seal.

    The wire ``max_cost`` echo is the depot contract's forced figure — the
    model accepts exactly MAX_DEPOT_MUTATION_COST and nothing else — while
    the recheck's own attempt-level ceiling is zero and the observe op can
    never spend. The observation carries no tile and no front tile, exactly
    as the depot observe subset serializes their absence.
    """
    if entry.get("exchange") != RECHECK_EXCHANGE_ID or entry.get("op") != RECHECK_OP:
        raise RecheckStagingError("the recheck carries the one pinned observe exchange only")
    return DepotRequest(
        op=RECHECK_OP,
        request_id=RECHECK_EXCHANGE_ID,
        plan=seal,
        company=int(DEPOT_MUTATION_COMPANY),
        max_cost=int(MAX_DEPOT_MUTATION_COST),
        pickup=int(DEPOT_MUTATION_PICKUP_TILE),
        delivery=int(DEPOT_MUTATION_DELIVERY_TILE),
        depot=int(DEPOT_MUTATION_DEPOT_TILE),
        tile=None,
        front_tile=None,
    )


def verify_request_against_recheck_plan(request: DepotRequest, *, seal: str) -> None:
    """Refuse a request that is not bound to the local recheck plan.

    Python is the trust anchor: the request must present the staged seal,
    the pinned corridor identity, the pinned observe op and the single
    pinned exchange identity, and it must carry no tile of any kind. The
    depot contract's own plan-level check (over the consumed depot plan the
    recheck binds as its corridor identity) runs after the recheck-specific
    gates. This runs before any byte reaches the Admin session.
    """
    if request.plan != seal:
        raise ValueError("request plan digest is not the staged prelaunch seal")
    if request.op != RECHECK_OP:
        raise ValueError("a non-observe op cannot ride the observe-only recheck")
    if request.request_id != RECHECK_EXCHANGE_ID:
        raise ValueError("the recheck carries the one pinned reload-00 exchange only")
    if request.company != int(DEPOT_MUTATION_COMPANY):
        raise ValueError("request company drifted from the pinned recheck company")
    if (request.pickup, request.delivery, request.depot) != (
        int(DEPOT_MUTATION_PICKUP_TILE),
        int(DEPOT_MUTATION_DELIVERY_TILE),
        int(DEPOT_MUTATION_DEPOT_TILE),
    ):
        raise ValueError("request pins drifted from the planned corridor")
    if request.tile is not None or request.front_tile is not None:
        raise ValueError("the observe recheck carries no tile of any kind")
    depot_native.verify_request_against_depot_plan(
        request, plan=depot_native.depot_plan(), seal=seal
    )


# --- The recheck phase outcome ------------------------------------------------


def _recheck_state() -> dict:
    return dict(
        index=0,
        observations={},
        ledger=[],
        funds=None,
        funds_chain=[],
        divergence=False,
    )


def _recheck_read_step(
    state: dict,
    request: DepotRequest,
    readback,  # DepotReadback
    *,
    facts_of_record: dict,
    funds_of_record: int,
    seal: str,
) -> dict:
    """Verify the one ordered protocol-10 observe exchange against the record."""
    expected = RECHECK_EXCHANGE_ID
    if request.request_id != expected or readback.request_id != expected:
        raise ValueError(f"depot recheck exchange out of order: expected {expected}")
    verify_request_against_recheck_plan(request, seal=seal)
    if readback.status != "READY":
        raise ValueError(f"depot recheck exchange {expected} ended {readback.status}")
    # The zero-spend discipline of record: an observe readback can never
    # carry a nonzero signed cost (the wire subset has no spend-capable op).
    if readback.cost != 0:
        raise ValueError(
            f"the zero-spend observe recheck refused a cost-bearing readback at "
            f"{expected}: cost {readback.cost}"
        )
    # The funds of record: the single readback opens at the round-2 binding's
    # close (funds_of_record) and must satisfy funds_after == funds_before -
    # cost with its zero cost — i.e. the measured balance must equal the
    # round-2 funds of record exactly.
    if readback.funds != funds_of_record - readback.cost:
        raise ValueError(
            f"the depot recheck funds of record broke at {expected}: "
            f"{readback.funds} != {funds_of_record} - {readback.cost}"
        )
    if request.op == RECHECK_OP:
        facts = dict(
            depot_present=readback.depot_present,
            front_read=readback.front_read,
            owner=readback.owner,
            depot_linked=readback.depot_linked,
            connected_front_to_depot=readback.connected_front_to_depot,
            connected_depot_to_front=readback.connected_depot_to_front,
        )
        defects = [
            f"{name}: measured {facts.get(name)!r}, pinned {wanted!r}"
            for name, wanted in facts_of_record.items()
            if facts.get(name) != wanted
        ]
        if defects:
            state["divergence"] = True
            # The fixed-fact comparison of record (round-2 binding): any
            # divergence halts STALE_PIN-preservingly with the raw measured
            # values legible, and the recheck can never reload a divergent
            # world.
            raise ValueError(
                f"STALE_PIN: the {expected} fact comparison diverged from the "
                f"round-2 binding — " + "; ".join(defects)
            )
        state["observations"][expected] = dict(
            facts=facts,
            request_id=readback.request_id,
            digest=readback.digest,
            funds=readback.funds,
        )
    else:
        raise ValueError("a foreign op cannot enter the recheck phase")  # pragma: no cover
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
            funds_before=funds_of_record,
            cost=readback.cost,
            funds_after=readback.funds,
        )
    )
    state["index"] += 1
    receipt = dict(
        schema="company-depot-recheck-receipt-v1",
        request_id=readback.request_id,
        op=request.op,
        seal=seal,
        status=readback.status,
        funds=readback.funds,
        cost=readback.cost,
        verification="DEPOT_RELOAD_MEASURED",
    )
    receipt = {**receipt, "facts": dict(state["observations"][expected]["facts"])}
    return receipt


def _recheck_gate_verdict(state: dict, *, complete: bool) -> dict:
    """The offline round-2 re-compute from the reload exchange alone.

    The gate passes only on a complete schedule whose single observe gate
    recorded exactly the transcribed facts of record at the transcribed
    funds of record with its zero cost. An incomplete schedule can never
    manufacture a verdict; nothing here is an admissibility claim.
    """
    if complete:
        return dict(
            verdict="DEPOT_RELOAD_GATE_PASSES",
            statement=(
                "the single reload exchange reproduced the round-2 binding's "
                "facts of record verbatim (both AreRoadTilesConnected "
                "directions true under the identical identity facts), the "
                "measured funds equal the transcribed funds of record, the "
                "readback cost is the zero of record and nothing was saved "
                "or mutated, so the loaded world of record is the round-2 "
                "after-save and nothing else"
            ),
            mutations=list(state["ledger"]),
        )
    if state["divergence"]:
        return dict(
            verdict="DEPOT_RELOAD_GATE_DIVERGED",
            statement=(
                "the reload exchange carried a measured fact that diverged "
                "from the pinned round-2 binding; the recheck can never "
                "reload-verify a divergent world and the divergence is "
                "terminal preservable evidence, never a relabelable failure"
            ),
            mutations=list(state["ledger"]),
        )
    return dict(
        verdict="DEPOT_RELOAD_GATE_UNDECIDED_INCOMPLETE",
        statement=(
            "the one reload exchange did not complete its verified READY "
            "measurement; the round-2 equality stands unevidenced and this "
            "is a recorded fact, never a manufactured verdict"
        ),
        mutations=list(state["ledger"]),
    )


def recheck_phase_outcome(
    exchanges: list[tuple[DepotRequest, Any]],
    *,
    prelaunch_digest: str,
    facts_of_record: dict,
    funds_of_record: int,
) -> dict:
    """Fail-closed recheck verification over preserved evidence only.

    Each exchange is ``(request, readback_or_error)``; an error element is
    an observation whose bytes never parsed or correlated (malformed,
    stale, torn or duplicate). The first halted exchange ends verification:
    earlier receipts are preserved, later exchanges are pending, and an
    unfinished schedule can never manufacture success. The phase records
    measurements only — mutations stay structurally empty forever.
    """
    receipts: list[dict] = []
    failed = None
    state = _recheck_state()
    for request, readback in exchanges:
        if failed is not None:
            continue
        if isinstance(readback, Exception):
            failed = dict(
                label=request.request_id,
                status="MALFORMED",
                error=str(readback),
                world_state="HALTED_BEFORE_RELOAD",
            )
            continue
        try:
            receipts.append(
                _recheck_read_step(
                    state,
                    request,
                    readback,
                    facts_of_record=facts_of_record,
                    funds_of_record=funds_of_record,
                    seal=prelaunch_digest,
                )
            )
        except Exception as error:  # noqa: BLE001 - fail closed on any defect
            failed = dict(
                label=request.request_id,
                status=str(getattr(readback, "status", "UNKNOWN")),
                error=str(error),
                world_state="HALTED_BEFORE_RELOAD",
            )
            continue
    complete = failed is None and len(state["ledger"]) == PLANNED_RECHECK_EXCHANGES
    # The pending set of record carries the planned exchanges that never
    # verified — the failed label itself never returns to pending.
    pending = (
        [RECHECK_EXCHANGE_ID][state["index"]:]
        if failed is None
        else [RECHECK_EXCHANGE_ID][1:]
    )
    return dict(
        schema="depot-recheck-phase-outcome-v1",
        seal=prelaunch_digest,
        receipts=receipts,
        failed=failed,
        pending=pending,
        observations=state["observations"],
        funds=state["funds"],
        funds_chain=state["funds_chain"],
        divergence=state["divergence"],
        state_changed=False,
        mutations=[],
        gate=_recheck_gate_verdict(state, complete=complete),
        observation_kinds=("MEASURED", "REFUSED", "MISSING", "MALFORMED"),
        verification="DEPOT_RELOAD_OBSERVED" if complete else "DEPOT_RELOAD_INCOMPLETE",
    )


# --- Depot recheck execution (authorized one-attempt path only) --------------


def apply_depot_recheck_cleanup_outcome(result: dict, *, complete: bool) -> None:
    """Fail closed on the recheck's final cleanup verdict."""
    result["cleanup_complete"] = bool(complete)
    if complete:
        return
    result["cleanup_failure"] = True
    if result.get("verified") is True or result.get("status") == "NATIVE_DEPOT_RELOAD_COMPLETE":
        freight_native.deny_verification(
            result,
            status="FAILED_CLEANUP",
            message=(
                "ValueError: cleanup was not certified; no verified depot "
                "recheck completion is possible"
            ),
        )


async def execute_depot_recheck_attempt(prepared: PreparedProof, backend) -> dict:
    """Execute the authorized one-attempt reload phase (never offline).

    One launch, one connection, the staged schedule's single observe
    exchange verified against the round-2 binding of record by the
    production ``recheck_phase_outcome``. Zero-mutation discipline: no
    save of any kind is emitted on any path, the exchange can never spend,
    and ``mutated`` stays structurally empty; the verified completion binds
    its loaded-source digest into the result and the reload receipt of
    record, and cleanup is certified before any completion verdict can
    stand. The first verification failure halts the phase
    prefix-preservingly at the exchange itself.
    """
    directory = prepared.directory
    recheck_preflight(prepared)
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
    world_record = metadata["plan_policy"]["world"]
    facts_of_record = world_record["facts_of_record"]
    funds_of_record = int(world_record["funds_of_record"])
    fleet_of_record = int(world_record["fleet_of_record"])
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
    exchanges: list[tuple[DepotRequest, Any]] = []
    overall_deadline = event_loop_deadline(metadata["budgets"]["total_seconds"])
    try:
        async with asyncio.timeout(metadata["budgets"]["total_seconds"]):
            await backend.launch(prepared, authorization=grant)
            result["native_launches"] = 1
            await wait_log(backend, prepared, RECHECK_READY_MARKER)
            console(backend, metadata["bootstrap_command"])
            await wait_log(backend, prepared, ROAD_PROOF_COMPANY_READY_MARKER)
            session = await backend.connect(
                prepared, frame_observer=lambda d, f: frames.append((d, f.hex()))
            )
            result["connections"] = 1
            await session.authenticate(metadata["attempt"], "1", timeout=10)
            welcome = session.welcome
            expected = metadata["world"]["expected_welcome"]
            if session.protocol is None or welcome is None:
                raise ValueError("the reload world identity mismatch")
            received = {field: getattr(welcome, field) for field in WELCOME_ORDER}
            # The reload identity of record: seed/landscape/dims/revision are
            # pinned exact; start_day is load-derived for a saved world and
            # pinned as its floor (>= the depot attempt's own welcome pin).
            for field in WELCOME_ORDER:
                wanted = True if field == "dedicated" else expected[field]
                got = received[field]
                if field == "start_day":
                    if got < wanted:
                        raise ValueError(
                            f"the reload world {field} fell below its pinned floor: "
                            f"{got} < {wanted}"
                        )
                elif got != wanted:
                    raise ValueError(
                        f"the reload world identity {field} drifted: {got} != {wanted}"
                    )
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
            # Zero-mutation discipline of record: the depot's session-before
            # save is deliberately absent — the staged authoritative depot
            # after-save IS the before world, digest-bound at staging. The
            # loaded source copy is re-digested here at the run boundary and
            # nothing else is written all run.
            staged_source = Path(metadata["workspace"]) / "source.sav"
            if staged_source.is_symlink() or not staged_source.is_file():
                raise ValueError(
                    "the staged authoritative source save is missing at the run boundary"
                )
            loaded_source = sha256(staged_source)
            if loaded_source != metadata["world"]["save_sha256"]:
                raise ValueError(
                    "the staged source save drifted from the pinned round-2 after-save"
                )
            result["loaded_source_sha256"] = loaded_source
            for entry in schedule:
                label = entry["exchange"]
                try:
                    request = _recheck_exchange_request(entry, seal)
                    if request.op != RECHECK_OP:
                        raise ValueError("a foreign op cannot enter the recheck run")
                    verify_request_against_recheck_plan(request, seal=seal)
                    readback = await depot_native.depot_exchange(
                        session,
                        request,
                        directory,
                        budget_table=metadata["budgets"],
                        overall_deadline=overall_deadline,
                    )
                    result["requests"] += 1
                    probe = recheck_phase_outcome(
                        exchanges + [(request, readback)],
                        prelaunch_digest=seal,
                        facts_of_record=facts_of_record,
                        funds_of_record=funds_of_record,
                    )
                    if probe["failed"] is not None:
                        raise ValueError(
                            f"the depot recheck exchange {label} failed verification: "
                            f"{probe['failed']['error']}"
                        )
                    exchanges.append((request, readback))
                    result["exchanges"].append(label)
                    result["last_status"] = readback.status
                    result["command_accepted"] = True
                    # The observe-only recheck can never mutate: the
                    # zero-mutation discipline records this structurally.
                    result["mutated"] = []
                    result["state_changed"] = False
                except Exception as error:
                    result["halt"] = dict(
                        label=label, error=type(error).__name__ + ": " + str(error)
                    )
                    break
            phase = recheck_phase_outcome(
                exchanges,
                prelaunch_digest=seal,
                facts_of_record=facts_of_record,
                funds_of_record=funds_of_record,
            )
            result["phase"] = phase
            if phase["verification"] == "DEPOT_RELOAD_OBSERVED":
                if len(exchanges) != len(schedule):
                    raise ValueError(
                        "the recheck completion evidence drifted from the staged schedule"
                    )
                if phase["gate"]["verdict"] != "DEPOT_RELOAD_GATE_PASSES":
                    raise ValueError("the recheck completion contradicts its phase gate")
                if result["mutated"] != [] or result["state_changed"] is not False:
                    raise ValueError(
                        "the observe-only recheck recorded a mutation it cannot carry"
                    )
                if result.get("loaded_source_sha256") != metadata["world"]["save_sha256"]:
                    raise ValueError("the recheck completion lost its loaded-source binding")
                result["verified"] = True
                result["status"] = "NATIVE_DEPOT_RELOAD_COMPLETE"
                write_json(
                    directory / RECHECK_AFTER_RECEIPT_NAME,
                    dict(
                        schema=RECHECK_AFTER_RECEIPT_SCHEMA,
                        attempt=RECHECK_ATTEMPT,
                        milestone=MILESTONE_DEPOT_RECHECK,
                        prelaunch_sha256=seal,
                        phase=phase,
                        loaded_source_sha256=result["loaded_source_sha256"],
                        funds_of_record=funds_of_record,
                        fleet_of_record=fleet_of_record,
                        statement=RECHECK_AFTER_RECEIPT_STATEMENT,
                    ),
                )
            else:
                result["status"] = "PHASE_HALTED_PREFIX_PRESERVED"
    except Exception as error:
        result["error"] = type(error).__name__ + ": " + str(error)
    finally:
        # Zero-mutation discipline of record: the depot's finally-diagnostic
        # save arm is deliberately absent — no save of any kind is written
        # all run, on any path, whatever halted.
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
            if result["status"] == "NATIVE_DEPOT_RELOAD_COMPLETE":
                freight_native.deny_verification(
                    result,
                    status="FAILED",
                    message=(
                        "ValueError: the retained script log health findings "
                        "deny the verified depot recheck completion"
                    ),
                )
        if result["returncode"] not in (None, 0):
            if result["status"] == "NATIVE_DEPOT_RELOAD_COMPLETE":
                freight_native.deny_verification(
                    result,
                    status="FAILED",
                    message=(
                        "ValueError: the native runtime exited abnormally after "
                        f"the depot recheck (return code {result['returncode']})"
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
        apply_depot_recheck_cleanup_outcome(result, complete=cleanup_complete)
        write_json(directory / "cleanup.json", cleanup)
        write_json(directory / "result.json", result)
        (directory / "artifact-manifest.sha256").write_text(manifest(directory))
    return result


# --- Depot recheck replay verification ---------------------------------------


def _parse_recheck_frames(directory: Path):
    """Parse the retained frame stream of the owned secure recheck session."""
    return depot_native._parse_depot_frames(directory)


def verify_recheck_attempt_identity(metadata: dict) -> dict:
    """Re-bind one retained recheck attempt to its pinned prerequisite.

    Replay never trusts the staged record's own declarations: the lineage
    (attempt/schema/prerequisite/world) is re-derived from the module's
    single pinned identity, the pinned round-2 depot attempt is re-verified
    through its own full replay, and the source-save digest, welcome floor,
    schedule, plan digests, observe-only profile, world pins (the
    transcribed facts/funds/fleet of record) and hypotheses are all
    re-derived. A foreign lineage or a drifted pin refuses.
    """
    if metadata.get("attempt") != RECHECK_ATTEMPT:
        raise ValueError("the retained attempt identity drifted from the staged scope")
    if (
        metadata.get("schema") != D5_DEPOT_RECHECK_PRELAUNCH_SCHEMA
        or metadata.get("kind") != KIND
        or metadata.get("milestone") != MILESTONE_DEPOT_RECHECK
    ):
        raise ValueError("the retained attempt is not the D5 depot recheck lineage")
    staged_prerequisite = metadata.get("prerequisite")
    if not isinstance(staged_prerequisite, dict):
        raise ValueError("the retained attempt lacks its prerequisite binding")
    binding = recheck_prerequisite_binding(Path(staged_prerequisite.get("directory", "")))
    if staged_prerequisite != _recheck_prerequisite_record(binding):
        raise ValueError("the retained prerequisite binding drifted from the pinned attempt")
    if staged_prerequisite.get("schema") != D5_DEPOT_RECHECK_PREREQUISITE_SCHEMA:
        raise ValueError("the retained prerequisite schema drifted")
    stored_world = metadata.get("world")
    if not isinstance(stored_world, dict):
        raise ValueError("the retained attempt lacks its world binding")
    if stored_world != _recheck_world_record(binding):
        raise ValueError("the retained world binding drifted from the pinned record")
    if stored_world.get("save_sha256") != RECHECK_PREREQUISITE_AFTER_SAVE:
        raise ValueError("the retained world is not the pinned round-2 authoritative after-save")
    if stored_world.get("expected_welcome") != binding["expected_welcome"]:
        raise ValueError("the retained world welcome drifted from the pinned identity")
    verify_staged_source_save(
        {"save_sha256": binding["save_sha256"]},
        source_save_path(stored_world),
    )
    staged_source = Path(metadata.get("workspace", "")) / "source.sav"
    if staged_source.is_file():
        verify_staged_source_save({"save_sha256": binding["save_sha256"]}, staged_source)
    policy = metadata.get("plan_policy")
    if not isinstance(policy, dict):
        raise ValueError("the retained attempt lacks its plan policy")
    schedule = staged_recheck_schedule(policy)
    if policy.get("schedule") != schedule or policy.get("plan_digest") != plan_digest_of(schedule):
        raise ValueError("the retained recheck schedule drifted from the compiled derivation")
    if policy.get("schedule_version") != 1:
        raise ValueError("the retained schedule version drifted")
    if policy.get("plan_model_digest") != depot_native.depot_plan().digest:
        raise ValueError("the retained corridor-identity plan digest drifted from the pinned plan")
    if metadata.get("budgets") != recheck_budgets():
        raise ValueError("the retained budget contract drifted")
    if policy.get("max_cost") != RECHECK_MAX_COST:
        raise ValueError("the retained recheck budget floated off its zero-spend ceiling")
    if policy.get("profile", {}).get("schema") != "d5-f12-depot-reload-profile-v1":
        raise ValueError("the retained recheck profile schema drifted")
    if policy.get("profile") != recheck_profile():
        raise ValueError("the retained observe-only profile drifted")
    world_pins = policy.get("world")
    if not isinstance(world_pins, dict):
        raise ValueError("the retained plan policy lacks its world pins")
    expected_pins = _recheck_expected_world(binding)
    for name, expected in expected_pins.items():
        if world_pins.get(name) != expected:
            raise ValueError(f"the retained recheck world pin {name} drifted")
    if (
        policy.get("company") != int(DEPOT_MUTATION_COMPANY)
        or policy.get("target_tile") != int(DEPOT_MUTATION_DEPOT_TILE)
        or policy.get("plan_model_digest") != depot_native.depot_plan().digest
        or policy.get("wire_max_cost_echo") != int(MAX_DEPOT_MUTATION_COST)
    ):
        raise ValueError("the retained recheck corridor pins drifted")
    if policy.get("observations") != [
        dict(exchange=row["exchange"], kind="GATE", tile=None, front_tile=None)
        for row in schedule
    ]:
        raise ValueError("the retained recheck observation kinds drifted")
    staged_hypotheses = policy.get("hypotheses")
    expected_hypotheses = recheck_hypotheses(binding)
    if (
        not isinstance(staged_hypotheses, dict)
        or staged_hypotheses.get("state") != expected_hypotheses.get("state")
    ):
        raise ValueError(
            f"the retained recheck hypothesis record drifted from its version derivation "
            f"({expected_hypotheses.get('state')})"
        )
    if expected_hypotheses.get("state") == "RETAINED_E78_REBOUND":
        if staged_hypotheses != expected_hypotheses:
            raise ValueError(
                "the retained recheck hypothesis record drifted from the retained bytes"
            )
    return binding


def verify_depot_recheck_attempt(directory: Path) -> dict:
    """Replay the retained reload phase; never trust a success label.

    The replay re-derives every retained fact independently — operator
    authorization evidence, the staged recheck schedule, the captured
    session frames, the single per-exchange request/response pair — then
    re-verifies the one exchange with the production
    :func:`recheck_phase_outcome` and the certified-cleanup gate. A forced
    or invented ``NATIVE_DEPOT_RELOAD_COMPLETE`` label alone can never
    verify; a refused, missing, malformed, stale, divergent or halting
    exchange always leaves the verdict incomplete. A verified completion
    additionally binds its zero-mutation capsule: ``mutated`` stays empty,
    the one readback carried its zero cost at the round-2 funds of record,
    no save artifact of any kind exists, and the loaded-source digest
    binds three ways — the staged world record, the run's own binding and
    the retained round-2 after-save re-digested here.
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
                "the recheck candidate was never consumed by an operator "
                "authorization; no verified reload is possible"
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
    # The recheck derives no replay-side artifact of its own: the run wrote
    # its reload receipt before the manifest, so every candidate file must
    # stand inside the manifest of record. Anything else is refused.
    unmanifested = present_names - manifest_names
    if unmanifested:
        raise ValueError("the artifact manifest is not exhaustive")
    if metadata.get("schema") != D5_DEPOT_RECHECK_PRELAUNCH_SCHEMA:
        return dict(
            verification="AUTHORIZATION_UNVERIFIED",
            authorization_state="UNKNOWN_PRELAUNCH_SCHEMA",
            statement=(
                f"the prelaunch record is not the launch-capable "
                f"[{D5_DEPOT_RECHECK_PRELAUNCH_SCHEMA!r}] lineage; no verified "
                "reload is possible"
            ),
        )
    authorization_state = replay_authorization_state(directory, metadata, seal, claims)
    if authorization_state is not None:
        return dict(
            verification="AUTHORIZATION_UNVERIFIED",
            authorization_state=authorization_state,
            statement=(
                "the retained authorization evidence does not match the "
                "operator-verified record; no verified reload is possible"
            ),
        )
    policy_replay = metadata["plan_policy"]
    schedule = staged_recheck_schedule(policy_replay)
    planned_ids = {row["exchange"] for row in schedule}
    if planned_ids != {RECHECK_EXCHANGE_ID} or len(schedule) != PLANNED_RECHECK_EXCHANGES:
        raise ValueError("the retained recheck schedule drifted from the wire recheck contract")
    binding = verify_recheck_attempt_identity(metadata)
    facts_of_record = binding["facts_of_record"]
    funds_of_record = int(binding["funds_of_record"])
    result = json.loads((directory / "result.json").read_text())
    runtime = json.loads((directory / "runtime-identity.json").read_text())
    expected_welcome = metadata["world"]["expected_welcome"]
    welcome = runtime.get("welcome")
    if runtime.get("encrypted") is not True or not isinstance(welcome, dict):
        raise ValueError("the owned single-runtime encrypted execution evidence missing")
    for field in WELCOME_ORDER:
        expected = True if field == "dedicated" else expected_welcome[field]
        if field == "start_day":
            if welcome.get(field) is None or welcome.get(field) < expected:
                raise ValueError(
                    f"the retained world welcome {field} fell below its pinned floor"
                )
        elif welcome.get(field) != expected:
            raise ValueError(f"the retained world welcome {field} drifted")
    outbound, outbound_requests, replies, request_positions, reply_positions = (
        _parse_recheck_frames(directory)
    )
    if len(outbound_requests) > metadata["budgets"]["requests"]:
        raise ValueError("the recheck request budget exceeded (outbound frames)")
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
            statement=(
                "an incomplete retained exchange (fewer outbound frames); no "
                "completion claimed"
            ),
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
            raise ValueError(f"a duplicate recheck request_id: {query.request_id}")
        seen_ids.add(query.request_id)
    response_map = {}
    for path in paths:
        response_path = path.with_name(path.name.replace("-request.json", "-response.json"))
        if response_path.is_file():
            response_map[path.read_bytes()] = response_path.read_bytes()
    for path in sorted(directory.glob("*-response.json")):
        exchange_id = path.name[: -len("-response.json")]
        try:
            readback = depot_native.DepotReadback.model_validate_json(path.read_bytes())
        except ValueError as error:
            raise ValueError(
                f"the retained response file is not a parseable readback: {path.name}"
            ) from error
        if readback.request_id != exchange_id:
            raise ValueError("the retained response file identity does not match its payload")
        if not (directory / (exchange_id + "-request.json")).is_file():
            raise ValueError("the retained response file lacks its request")
    for raw, response in response_map.items():
        if outbound.count(encode_recheck_request(raw)) != 1 or replies.count(response) != 1:
            raise ValueError("the retained exchange lacks unique secure-session frame evidence")
    retained_responses = set(response_map.values())
    for reply in replies:
        if reply not in retained_responses:
            raise ValueError("the retained gateway response lacks its durable response file")
    for raw, response in response_map.items():
        if reply_positions[response] < request_positions[raw]:
            raise ValueError("a retained response precedes its own request in the frame stream")
    halt_record = result.get("halt")
    exchanges: list[tuple[DepotRequest, Any]] = []
    # Mirror the depot replay's schedule walk: a halt at the planned
    # exchange (or a halt that prevented its request file from ever being
    # written) leaves the phase's exchange set empty and its halt record
    # intact — evidence, never a manufactured verdict.
    halted_at_exchange = (
        not (isinstance(halt_record, dict) and halt_record.get("label") == RECHECK_EXCHANGE_ID)
    )
    request_path = directory / (RECHECK_EXCHANGE_ID + "-request.json")
    if halted_at_exchange and request_path.is_file():
        query = DepotRequest.model_validate_json(request_path.read_bytes())
        raw = response_map.get(query.to_bytes())
        if raw is not None:
            exchanges.append((query, depot_native.DepotReadback.parse_for(query, raw)))
    phase = recheck_phase_outcome(
        exchanges,
        prelaunch_digest=seal,
        facts_of_record=facts_of_record,
        funds_of_record=funds_of_record,
    )
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
    if result["status"] == "NATIVE_DEPOT_RELOAD_COMPLETE":
        if phase["verification"] != "DEPOT_RELOAD_OBSERVED":
            raise ValueError("the verified completion contradicts its recheck phase outcome")
        if result.get("halt") is not None or not result.get("command_accepted"):
            raise ValueError("the verified completion contradicts its retained attempt record")
        if (result.get("native_launches"), result.get("connections")) != (
            metadata["budgets"]["launches"],
            metadata["budgets"]["connection_attempts"],
        ):
            raise ValueError("the verified completion contradicts its launch seal")
        if len(result.get("exchanges", [])) != PLANNED_RECHECK_EXCHANGES or not cleanup_complete:
            raise ValueError("the verified completion's cleanup or exchange inventory incomplete")
        if len(outbound_requests) != PLANNED_RECHECK_EXCHANGES:
            raise ValueError("the verified completion's request inventory drifted")
        if result.get("mutated") != [] or result.get("state_changed") is not False:
            raise ValueError(
                "the observe-only recheck cannot carry the mutation it labels"
            )
        if result.get("cleanup_failure") is not None or result.get("verified") is not True:
            raise ValueError("the verified completion label contradicts its own result flags")
        if result.get("requests") != PLANNED_RECHECK_EXCHANGES:
            raise ValueError("the verified completion's request accounting drifted")
        if not phase["receipts"] or any(row["cost"] != 0 for row in phase["receipts"]):
            raise ValueError("the verified completion's receipts are not zero-spend")
        if phase["funds"] != funds_of_record:
            raise ValueError("the verified completion's funds of record drifted")
        if phase["gate"]["verdict"] != "DEPOT_RELOAD_GATE_PASSES":
            raise ValueError("the verified completion's phase gate drifted from the pass verdict")
        if phase.get("observations", {}).get(RECHECK_EXCHANGE_ID) is None:
            raise ValueError("the verified completion lacks its reload observation of record")
        # The zero-save discipline of record: none of these names may exist
        # (a save artifact would be the depot family's, not this attempt's,
        # and its presence contradicts the zero-mutation capsule itself).
        for name in RECHECK_FORBIDDEN_ARTIFACTS:
            if (directory / name).is_file():
                raise ValueError(f"the zero-save recheck cannot carry {name}")
        # The loaded-source digest of record binds three ways: the run's own
        # binding, the staged world record and the retained round-2
        # after-save re-digested here (read-only, never moved or rewritten).
        loaded_source = result.get("loaded_source_sha256")
        if (
            not isinstance(loaded_source, str)
            or len(loaded_source) != 64
            or any(digit not in "0123456789abcdef" for digit in loaded_source)
        ):
            raise ValueError(
                "the verified recheck completion lacks its loaded-source digest"
            )
        if loaded_source != metadata["world"]["save_sha256"] or loaded_source != (
            RECHECK_PREREQUISITE_AFTER_SAVE
        ):
            raise ValueError(
                "the verified recheck completion's loaded-source binding drifted from the pin"
            )
        retained_save = Path(binding["retained_directory"]) / binding["save"]
        if retained_save.is_symlink() or not retained_save.is_file():
            raise ValueError(
                "the verified recheck completion lacks its retained round-2 after-save"
            )
        if sha256(retained_save) != loaded_source:
            raise ValueError(
                "the retained round-2 after-save digest drifted from the "
                "loaded-source binding"
            )
        receipt_path = directory / RECHECK_AFTER_RECEIPT_NAME
        if not receipt_path.is_file():
            raise ValueError("the verified recheck completion lacks its retained receipt")
        retained_receipt = json.loads(receipt_path.read_text())
        replay_phase = json.loads(json.dumps(phase))
        expected_receipt = dict(
            schema=RECHECK_AFTER_RECEIPT_SCHEMA,
            attempt=RECHECK_ATTEMPT,
            milestone=MILESTONE_DEPOT_RECHECK,
            prelaunch_sha256=seal,
            phase=replay_phase,
            loaded_source_sha256=loaded_source,
            funds_of_record=funds_of_record,
            fleet_of_record=int(binding["fleet_of_record"]),
            statement=RECHECK_AFTER_RECEIPT_STATEMENT,
        )
        if retained_receipt != expected_receipt:
            raise ValueError("the retained recheck receipt drifted from its verified re-derivation")
        # The one divergence risk of the nested receipt is a drifted
        # embedded phase: the receipt comparison above already binds it
        # byte-exactly, so the verdict's receipt is a faithful copy here.
        return dict(
            verification="DEPOT_RELOAD_FACTS_VERIFIED",
            receipt=dict(
                phase=dict(replay_phase),
                loaded_source_sha256=loaded_source,
            ),
            facts=dict(replay_phase["observations"][RECHECK_EXCHANGE_ID]["facts"]),
            funds=phase["funds"],
            zero_mutation=dict(
                mutated=result.get("mutated", []),
                state_changed=result.get("state_changed"),
                loaded_source_binding=(
                    "staged record == run binding == retained round-2 after-save"
                ),
            ),
            statement=(
                "the single observe exchange measured the loaded round-2 "
                "authoritative world's facts and funds fresh and they equal "
                "the round-2 binding exactly (facts and funds); no exchange "
                "carried a cost, no save of any kind was emitted, mutated "
                "stays empty and the world of record stays the retained "
                "depot after-save"
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
            phase["verification"] != "DEPOT_RELOAD_INCOMPLETE"
            or not isinstance(halt_record, dict)
            or len(result.get("exchanges", [])) != len(phase["receipts"])
            or (
                phase["failed"] is not None
                and phase["failed"].get("label") != halt_record.get("label")
            )
        ):
            raise ValueError("the halted recheck evidence contradicts its retained record")
        if not cleanup_complete:
            raise ValueError("the halted recheck attempt cleanup incomplete")
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


def staged_recheck_authorization_payload_digest(directory: Path) -> str:
    """The RFC-canonical digest of the candidate's own authorization payload."""
    directory = directory.resolve()
    metadata = read_prelaunch(directory)
    seal = sha256(directory / "PRELAUNCH.json")
    return hashlib.sha256(
        canonical_authorization_bytes(authorization_payload(metadata, seal))
    ).hexdigest()


def recheck_exit_status(result: dict) -> int:
    verified = (
        result.get("verified") is True
        and result.get("status") == "NATIVE_DEPOT_RELOAD_COMPLETE"
        and result.get("cleanup_complete") is True
        and result.get("state_changed", True) is False
        and result.get("mutated") == []
    )
    return 0 if verified else 1


def recheck_verdict_exit_status(verdict: dict) -> int:
    return 0 if verdict.get("verification") == "DEPOT_RELOAD_FACTS_VERIFIED" else 1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("prepare", "preflight", "run", "verify"))
    parser.add_argument("directory", type=Path)
    parser.add_argument("--prerequisite", type=Path, default=RECHECK_PREREQUISITE)
    args = parser.parse_args()
    directory = args.directory.resolve()
    if args.command == "prepare":
        prepared = prepare_depot_recheck_candidate(directory, prerequisite=args.prerequisite)
        recheck_preflight(prepared)
        print("PRELAUNCH PASS", directory)
    elif args.command == "preflight":
        recheck_preflight(freight_native.reopen_candidate(directory))
        print("PREFLIGHT PASS")
    elif args.command == "verify":
        verdict = verify_depot_recheck_attempt(directory)
        print(json.dumps(verdict, sort_keys=True))
        raise SystemExit(recheck_verdict_exit_status(verdict))
    else:
        read_prelaunch(directory)  # fail fast on any drifted prelaunch record
        result = asyncio.run(
            execute_depot_recheck_attempt(
                freight_native.reopen_candidate(directory),
                DepotRecheckNativeBackend(authorized_one_launch=True),
            )
        )
        print(json.dumps(result, sort_keys=True))
        raise SystemExit(recheck_exit_status(result))


if __name__ == "__main__":
    main()
