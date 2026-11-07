"""Phase C Random World feasibility decision (offline, deterministic).

FD-C-2 of the Random World roadmap
(``docs/roadmap-and-scope-2026-11-05.md`` §4): a typed, evidence-driven
decision classifying whether Random World logistics planning is feasible
within the project's *currently supported capabilities*.

Discipline of record (binding on this module):

- Offline only: no OpenTTD launch, no AdminPort connection, no candidate
  consumption, no historical evidence mutation, no relabeling. Retained
  artifacts are read with digests recorded and never rewritten.
- Every claimed fact carries an evidence row with exactly one evidence
  domain. Candidate-11/D5-corridor/fixed-scenario evidence is never
  consulted for Random World feasibility, and a row naming such a domain
  is a construction-time refusal, not a warning.
- Retained artifacts are the only inputs. A missing artifact yields an
  ``UNKNOWN`` contribution, never a fabricated value and never a negative
  observation. A present-but-unreadable artifact is recorded with its
  digest and an explicit parse failure; the decision stays producible.
- P08 refusals are evidence of bounded-search outcomes, not of software
  defects, and never of complete-world infeasibility unless the backing
  evidence itself asserts a completed (non-truncated) bounded search for
  the whole candidate space; no row in the retained corpus does, so the
  observed-world infeasibility outcome stays unreachable today.
- P05 must not run when its prerequisite candidate set is invalid or
  empty: the prerequisite gate is typed here and refuses fail-closed.
  The engine never runs P05 and never claims a delivered service.
- Supported limits are pinned constants of the current tree re-checked
  by regex against their own bytes; a stale statement refuses instead of
  silently misreporting the boundary.

Outputs a deterministic, hash-pinned, versioned derived report. The
report itself is the FD-C-2 decision; independent re-derivation must
produce byte-equal JSON from byte-equal inputs.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

SCHEMA = "phase-c-feasibility-decision/1"
POLICY_ID = "phase-c-feasibility/1"
OFFLINE_ONLY = True

#: Retained input roots. Each is optional on disk (a clone without
#: retained evidence still derives a decision carrying UNKNOWN rows).
RECONCILIATION_DIR = "artifacts/experiments/v1v2-semantic-reconciliation"
SNAPSHOT_DIR = "artifacts/experiments/v2-snapshot-p08-readiness"
SEED17_SMOKE_SUMMARY_DIR = (
    "artifacts/demos/random-smoke-correction-b84b9bd854a342f1a86e4ba669d8e450"
)
SEED17_CENSUS_CANDIDATE = "artifacts/demos/classification-exec-seed17-3a8f9e46"
SEED2026_PLANNING_RUN = "artifacts/demos/playable-demo-3e93cc7d1e8d43aab66a4f653665caaa"
SEED2026_WIDENED_RUN = "artifacts/demos/playable-demo-9b9a398e406f4ec1bf8e37a69116ac93"
SEED42_DEMO_RUN = "artifacts/demos/playable-demo-1570c66a2e564613a102b3e95647e8b1"
SEED17_SMOKE_RUN = "artifacts/demos/playable-demo-b84b9bd854a342f1a86e4ba669d8e450"


class FeasibilityState(StrEnum):
    """Per-dimension assessment states (task §5.1)."""

    VERIFIED = "VERIFIED"
    PARTIAL = "PARTIAL"
    UNSUPPORTED = "UNSUPPORTED"
    BLOCKED = "BLOCKED"
    UNKNOWN = "UNKNOWN"


class BlockerKind(StrEnum):
    """Why a dimension is not (yet) an affirmative verdict."""

    NONE = "none"
    EVIDENCE_MISSING = "EVIDENCE_MISSING"
    SCOPE_LIMIT = "SCOPE_LIMIT"
    PREREQUISITE_REFUSED = "PREREQUISITE_REFUSED"


class DecisionOutcome(StrEnum):
    """The five mutually exclusive outcome classes (task §5.2)."""

    FEASIBLE_WITHIN_SUPPORTED_CAPABILITIES = "FEASIBLE_WITHIN_SUPPORTED_CAPABILITIES"
    INFEASIBLE_FOR_OBSERVED_WORLD = "INFEASIBLE_FOR_OBSERVED_WORLD"
    INCOMPLETE_EVIDENCE = "INCOMPLETE_EVIDENCE"
    UNSUPPORTED_CAPABILITY = "UNSUPPORTED_CAPABILITY"
    SEPARATE_SCOPE_EXTENSION = "SEPARATE_SCOPE_EXTENSION"


class EvidenceDomain(StrEnum):
    """Random World evidence domains; never mixed inside one row."""

    SEED17_CENSUS = "SEED17_CENSUS"
    SEED17_SMOKE = "SEED17_SMOKE"
    RECONCILIATION_DERIVED = "RECONCILIATION_DERIVED"
    SNAPSHOT_ASSESSMENT_DERIVED = "SNAPSHOT_ASSESSMENT_DERIVED"
    SEED2026_PLANNING = "SEED2026_PLANNING"
    SEED42_DEMO_PLANNING = "SEED42_DEMO_PLANNING"
    SOURCE_TREE = "SOURCE_TREE"


_DOMAIN_DESCRIPTIONS: dict[EvidenceDomain, str] = {
    EvidenceDomain.SEED17_CENSUS: (
        "retained seed-17 Tile Classification V2 census attempt (E16 lineage)"
    ),
    EvidenceDomain.SEED17_SMOKE: (
        "retained seed-17 native smoke + post-run review record (E4 lineage)"
    ),
    EvidenceDomain.RECONCILIATION_DERIVED: (
        "derived reconciliation and policy reports of the seed-17 domain "
        "(offline V1/V2 reconciliation, ADR-012/ADR-013)"
    ),
    EvidenceDomain.SNAPSHOT_ASSESSMENT_DERIVED: (
        "derived seed-17 census snapshot P08 assessment (p08-v2-snapshot-planning/1)"
    ),
    EvidenceDomain.SEED2026_PLANNING: ("retained seed-2026 random-world planning runs (E139/E141)"),
    EvidenceDomain.SEED42_DEMO_PLANNING: ("retained seed-42 demo window-close abort record (E140)"),
    EvidenceDomain.SOURCE_TREE: ("current source tree constants digested at derivation time"),
}

#: Domains foreign to the Random World question (per task §1). Evidence
#: claiming these domains never enters this decision; naming them is a
#: fail-closed construction error.
PROHIBITED_EVIDENCE_DOMAINS = frozenset(
    {"D5_CORRIDOR", "D5_CARGOFLOW", "CANDIDATE11", "FIXED_SCENARIO"}
)

#: The ten required dimensions in report order (task §5.1).
DIMENSION_IDS: tuple[str, ...] = (
    "source_observation_completeness",
    "tile_classification_completeness",
    "source_save_correspondence",
    "industry_cargo_compatibility",
    "terrain_observation_completeness",
    "catchment_station_eligibility",
    "bounded_road_reachability",
    "p08_candidate_generation",
    "p05_planning_readiness",
    "supported_map_search_limits",
)

DIMENSION_TITLES: dict[str, str] = {
    "source_observation_completeness": "Source observation completeness",
    "tile_classification_completeness": "Tile classification completeness",
    "source_save_correspondence": "Source-save correspondence",
    "industry_cargo_compatibility": "Industry and cargo compatibility",
    "terrain_observation_completeness": "Terrain observation completeness",
    "catchment_station_eligibility": "Catchment and station eligibility",
    "bounded_road_reachability": "Bounded road reachability",
    "p08_candidate_generation": "P08 candidate-generation capability",
    "p05_planning_readiness": "P05 planning readiness",
    "supported_map_search_limits": "Supported map and search limits",
}


class P05RefusalCode(StrEnum):
    """Typed P05 prerequisite refusals (fail-closed)."""

    UNKNOWN_CANDIDATE_COUNT = "UNKNOWN_CANDIDATE_COUNT"
    EMPTY_CANDIDATE_SET = "EMPTY_CANDIDATE_SET"
    INVALID_CANDIDATE_SET = "INVALID_CANDIDATE_SET"
    ADMISSIBLE = "ADMISSIBLE"


def p05_prerequisite(
    candidate_count: int | None,
    candidates_valid: bool | None,
) -> tuple[P05RefusalCode, str]:
    """Typed P05 prerequisite gate.

    Mirrors the pipeline contract of record: the candidate compiler
    refuses an empty package set with ``ValueError``
    ("NO_FEASIBLE_SERVICES",
    ``app/simulation/openttd/freight_native_network.py:178``) and P05
    never sees an invalid or empty prerequisite. This gate is the FD-C-2
    typed statement of the same contract; it never runs P05. Absent
    evidence is unknown, not zero.
    """

    if candidate_count is None:
        return P05RefusalCode.UNKNOWN_CANDIDATE_COUNT, (
            "candidate count unobserved; the gate refuses before P05 is "
            "considered (absent evidence is not zero)"
        )
    if candidates_valid is not True:
        return P05RefusalCode.INVALID_CANDIDATE_SET, (
            "candidate set not validated as admissible native facts; P05 prerequisite refused"
        )
    if candidate_count <= 0:
        return P05RefusalCode.EMPTY_CANDIDATE_SET, (
            "candidate set empty; P05 must not run "
            "(freight_native_network.py:178 refused the same way)"
        )
    return P05RefusalCode.ADMISSIBLE, (
        f"candidate set of {candidate_count} validated candidates is an "
        "admissible P05 prerequisite; execution still requires native "
        "receipts and is claimed nowhere here"
    )


ABSENT_MARKER = "ABSENT"
_HEX256 = re.compile(r"[0-9a-f]{64}\Z")


class _Absent:
    """Marker for an absent/unreadable input carrying its digest."""

    def __init__(self, sha256: str, reason: str) -> None:
        self.sha256 = sha256
        self.reason = reason


@dataclass(frozen=True)
class EvidenceRow:
    """One verbatim-attributed fact row inside a dimension.

    ``sha256`` pins the exact bytes the statement was derived from
    (``ABSENT`` when the row records an absence). ``statement`` carries
    the recorded fact without expansion. ``observed_infeasible`` is true
    only when the row's source asserted a completed (non-truncated)
    bounded search over the whole candidate space; construction refuses
    the flag anywhere else.
    """

    domain: EvidenceDomain
    source: str
    sha256: str
    statement: str
    observed_infeasible: bool = False
    unobserved: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.domain, EvidenceDomain):
            raise ValueError(
                "evidence row domain must be an EvidenceDomain; foreign "
                "evidence is refused at construction"
            )
        if self.domain.value in PROHIBITED_EVIDENCE_DOMAINS:
            raise ValueError(
                f"evidence row named the prohibited domain {self.domain}: "
                "Random World feasibility must never cite Candidate-11, "
                "D5-corridor or fixed-scenario evidence"
            )
        if self.sha256 != ABSENT_MARKER and not _HEX256.match(self.sha256):
            raise ValueError("evidence row sha256 must be a full sha256 or ABSENT")
        if self.observed_infeasible:
            raise ValueError(
                "observed-world infeasibility rows come only from _observed_infeasible_row"
            )

    def report(self) -> dict:
        return {
            "domain": self.domain.value,
            "sha256": self.sha256,
            "source": self.source,
            "statement": self.statement,
            "observed_infeasible": self.observed_infeasible,
            "unobserved": self.unobserved,
        }


_COMPLETED_SEARCH_TAG = "bounded search completed for the whole candidate space"


def _observed_infeasible_row(
    domain: EvidenceDomain, source: str, sha256: str, statement: str
) -> EvidenceRow:
    """The single sanctioned constructor of an infeasibility verdict row.

    Only inputs whose diagnostics assert a completed, non-truncated
    bounded search over the whole candidate space may pass through here
    (the derivation layer checks ``search_truncated`` first, so a
    truncated search can never reach this sentence).
    """

    if _COMPLETED_SEARCH_TAG not in statement:
        raise ValueError(
            "an observed-world infeasibility row must assert the completed "
            "bounded search of its source verbatim"
        )
    row = EvidenceRow(domain, source, sha256, statement)
    object.__setattr__(row, "observed_infeasible", True)
    return row


@dataclass(frozen=True)
class DimensionAssessment:
    """One FD-C-2 dimension with its evidence rows and state."""

    dimension_id: str
    state: FeasibilityState
    rows: tuple[EvidenceRow, ...]
    blocker_kind: BlockerKind = BlockerKind.NONE
    blocker: str | None = None
    unknown_reason: str | None = None
    refusals: tuple[dict, ...] = ()

    def __post_init__(self) -> None:
        if self.dimension_id not in DIMENSION_IDS:
            raise ValueError(f"unknown dimension id {self.dimension_id!r}")
        if self.state is FeasibilityState.BLOCKED and not self.blocker:
            raise ValueError("a BLOCKED dimension needs an explicit blocker")
        if self.state is FeasibilityState.UNKNOWN and not self.unknown_reason:
            raise ValueError("an UNKNOWN dimension needs an explicit reason")
        if self.blocker and self.blocker_kind is BlockerKind.NONE:
            raise ValueError("a blocker requires an explicit blocker kind")
        if not self.rows and self.state is not FeasibilityState.UNKNOWN:
            raise ValueError(
                f"dimension {self.dimension_id} without rows cannot claim {self.state}"
            )

    @property
    def observed_infeasible(self) -> bool:
        return any(row.observed_infeasible for row in self.rows)

    @property
    def all_unobserved(self) -> bool:
        """True when every row records an absence/unreadability."""

        return all(row.unobserved for row in self.rows)

    @property
    def scope_limited(self) -> bool:
        """True only when a BLOCKED dimension names a scope boundary.

        A VERIFIED dimension may document its boundary without diverting
        the decision: the boundary exists and is honored, not hit.
        """

        return (
            self.state is FeasibilityState.BLOCKED and self.blocker_kind is BlockerKind.SCOPE_LIMIT
        )

    def has(self, domain: EvidenceDomain) -> bool:
        return any(row.domain is domain for row in self.rows)

    def report_payload(self) -> dict:
        return {
            "id": self.dimension_id,
            "title": DIMENSION_TITLES[self.dimension_id],
            "state": self.state.value,
            "blocker_kind": self.blocker_kind.value,
            "blocker": self.blocker,
            "unknown_reason": self.unknown_reason,
            "rows": [row.report() for row in self.rows],
            "refusals": list(self.refusals),
            "observed_infeasible": self.observed_infeasible,
        }


def _absent_row(domain: EvidenceDomain, path: Path | None, absent: _Absent) -> EvidenceRow:
    """The row of record for an absent/unreadable input (never a fact)."""

    return EvidenceRow(
        domain=domain,
        source=str(path) if path is not None else "<no path>",
        sha256=absent.sha256,
        statement=f"retained artifact unobserved: {absent.reason}",
        unobserved=True,
    )


def _read_json(path: Path | None) -> tuple[dict | _Absent, str]:
    """Read one JSON artifact read-only; never mutate, never round-trip.

    Always returns a ``(document, digest)`` pair: ``document`` is ``dict``
    when readable, an :class:`_Absent` marker otherwise (absent file,
    invalid JSON, or non-object payload), and ``digest`` is the file's
    sha256 or ``ABSENT`` when there is nothing to digest. Call sites test
    ``isinstance(document, dict)`` and never fabricate on the absent path.
    """

    if path is None or not Path(path).is_file():
        return _Absent(
            ABSENT_MARKER, "artifact absent; UNKNOWN by rule, not negation"
        ), ABSENT_MARKER
    raw = Path(path).read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    try:
        document = json.loads(raw)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        return _Absent(digest, f"artifact present but not valid JSON ({exc})"), digest
    if not isinstance(document, dict):
        return _Absent(digest, "artifact present but not a JSON object"), digest
    return document, digest


@dataclass(frozen=True)
class PhaseCInputs:
    """Retained artifact paths feeding the decision (all optional)."""

    reconciliation_dir: Path | None = None
    snapshot_report: Path | None = None
    seed17_smoke_summary: Path | None = None
    seed17_smoke_result: Path | None = None
    seed17_census_candidate: Path | None = None
    seed17_retained_facts: Path | None = None
    seed2026_planning_diagnostic: Path | None = None
    seed2026_result: Path | None = None
    seed2026_widened_diagnostic: Path | None = None
    seed2026_widened_result: Path | None = None
    seed42_demo_result: Path | None = None
    source_files: tuple[Path, ...] = ()


#: Code files whose pinned constants the limits dimension re-checks by
#: regex against their own bytes (fail-closed when a pinned value drifts).
_LIMIT_SOURCE_FILES: tuple[str, ...] = (
    "app/simulation/openttd/supplemental_planning_facts.py",
    "app/demo_random.py",
    "app/simulation/openttd/industry_inventory.py",
    "app/planning/p08_network.py",
    "app/planning/p08_adapter.py",
    "app/simulation/openttd/freight_native_network.py",
)

_LIMIT_PINS: dict[str, tuple[re.Pattern[str], str]] = {
    "supplemental_planning_facts.py": (
        re.compile(r"MAX_RANDOM_TILES = 2048\b"),
        "MAX_RANDOM_TILES = 2048",
    ),
    "demo_random.py": (
        re.compile(r"capture_tile_limit: Literal\[256, 512, 2048\]"),
        "capture_tile_limit: Literal[256, 512, 2048]",
    ),
    "industry_inventory.py": (
        re.compile(r"MAX_INDUSTRY_RECORDS = 32\b"),
        "MAX_INDUSTRY_RECORDS = 32",
    ),
    "p08_network.py": (
        re.compile(r"MAX_SERVICE_PACKAGES = 16\b"),
        "MAX_SERVICE_PACKAGES = 16",
    ),
    "p08_adapter.py": (
        re.compile(r"MAX_PATH_EXPANSIONS = MAX_STATION_PAIRS \* 256\b"),
        "MAX_PATH_EXPANSIONS = MAX_STATION_PAIRS * 256",
    ),
    "freight_native_network.py": (
        re.compile(r"NATIVE_CORRIDOR_BOUND: requires 2\.\.47 road tiles"),
        "NATIVE_CORRIDOR_BOUND: requires 2..47 road tiles",
    ),
}


def _default_inputs(project_root: Path) -> PhaseCInputs:
    root = project_root
    inputs = PhaseCInputs(
        reconciliation_dir=root / RECONCILIATION_DIR,
        snapshot_report=root / SNAPSHOT_DIR / "snapshot-assessment-report.json",
        seed17_smoke_summary=root / SEED17_SMOKE_SUMMARY_DIR / "native-smoke-summary.json",
        seed17_smoke_result=root / SEED17_SMOKE_RUN / "result.json",
        seed17_census_candidate=root / SEED17_CENSUS_CANDIDATE,
        seed2026_planning_diagnostic=root / SEED2026_PLANNING_RUN / "planning-diagnostic.json",
        seed2026_result=root / SEED2026_PLANNING_RUN / "result.json",
        seed2026_widened_diagnostic=root / SEED2026_WIDENED_RUN / "planning-diagnostic.json",
        seed2026_widened_result=root / SEED2026_WIDENED_RUN / "result.json",
        seed42_demo_result=root / SEED42_DEMO_RUN / "result.json",
        source_files=tuple(root / relative for relative in _LIMIT_SOURCE_FILES),
    )
    return inputs


def _digest_of(path: Path | None) -> str:
    if path is None or not Path(path).is_file():
        return ABSENT_MARKER
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _dimension_source_observation(inputs: PhaseCInputs) -> DimensionAssessment:
    """Dimension 1: source observation completeness."""

    rows: list[EvidenceRow] = []
    loaded, sha = _read_json(inputs.seed17_smoke_summary)
    if isinstance(loaded, dict):
        admitted_pairs = int(loaded.get("admissible_relationships", 0))
        discovered_pairs = int(loaded.get("rejected_compatible_pairs", 0)) + admitted_pairs
        rows.append(
            EvidenceRow(
                domain=EvidenceDomain.SEED17_SMOKE,
                source=str(inputs.seed17_smoke_summary),
                sha256=sha,
                statement=(
                    "seed-17 smoke: native generation/discovery/GUI verified "
                    f"(industries {loaded.get('industry_count')}, cargos "
                    f"{loaded.get('cargo_catalog_count')}); capture admitted "
                    f"{admitted_pairs} of {discovered_pairs} compatible pairs "
                    f"({loaded.get('rejection_reason')}); "
                    f"P08 {loaded.get('p08_generation')}; "
                    f"P05 {loaded.get('p05_status')}"
                ),
            )
        )
    else:
        rows.append(_absent_row(EvidenceDomain.SEED17_SMOKE, inputs.seed17_smoke_summary, loaded))
    for label, source in (
        ("seed-2026", inputs.seed2026_planning_diagnostic),
        ("seed-2026 widened seal", inputs.seed2026_widened_diagnostic),
    ):
        loaded, sha = _read_json(source)
        if isinstance(loaded, dict):
            captured = loaded.get("captured_relationships")
            rejections = loaded.get("capture_rejections")
            reasons = (
                sorted({str(row.get("reason")) for row in rejections if isinstance(row, dict)})
                if isinstance(rejections, list)
                else []
            )
            rows.append(
                EvidenceRow(
                    domain=EvidenceDomain.SEED2026_PLANNING,
                    source=str(source),
                    sha256=sha,
                    statement=(
                        f"{label} planning diagnostic: "
                        f"{len(loaded.get('compatible_relationships') or [])} compatible "
                        f"relationships, {len(captured) if isinstance(captured, list) else 0} "
                        f"captured, {len(rejections) if isinstance(rejections, list) else 0} "
                        f"capture rejections ({', '.join(reasons) or 'none'}), capture "
                        f"requests completed {loaded.get('capture_requests_completed')}, "
                        f"terminal {loaded.get('status')}"
                    ),
                )
            )
            if "supplemental capture outside final M2 month" in str(loaded.get("error")):
                rows.append(
                    EvidenceRow(
                        domain=EvidenceDomain.SEED2026_PLANNING,
                        source=str(source),
                        sha256=sha,
                        statement=(
                            "typed refusal of record: supplemental capture "
                            "outside final M2 month (month-pacing gate; "
                            "never relabeled; captures must pace inside the "
                            "qualified in-game month)"
                        ),
                    )
                )
        else:
            rows.append(_absent_row(EvidenceDomain.SEED2026_PLANNING, source, loaded))
    if rows and all(row.unobserved for row in rows):
        return DimensionAssessment(
            dimension_id="source_observation_completeness",
            state=FeasibilityState.UNKNOWN,
            rows=tuple(rows),
            unknown_reason="all referenced observation artifacts were absent or unreadable",
        )
    return DimensionAssessment(
        dimension_id="source_observation_completeness",
        state=FeasibilityState.PARTIAL,
        rows=tuple(rows),
        blocker_kind=BlockerKind.EVIDENCE_MISSING,
        blocker=(
            "planning-tile observations are incomplete across the observed "
            "random worlds: capture budgets refused portions of the "
            "relationship funnel and one pace refusal interrupted a "
            "relationship mid-read"
        ),
    )


def _dimension_tile_classification(inputs: PhaseCInputs) -> DimensionAssessment:
    """Dimension 2: tile classification completeness."""

    rows: list[EvidenceRow] = []
    reconciliation = (
        inputs.reconciliation_dir / "reconciliation-report.json"
        if inputs.reconciliation_dir
        else None
    )
    if reconciliation is not None:
        loaded, sha = _read_json(reconciliation)
        if isinstance(loaded, dict):
            raw_gate = loaded.get("raw_gate") or {}
            policy = loaded.get("policy_verdict") or {}
            rows.append(
                EvidenceRow(
                    domain=EvidenceDomain.RECONCILIATION_DERIVED,
                    source=str(reconciliation),
                    sha256=sha,
                    statement=(
                        f"reconciliation verdict {loaded.get('verdict')}: raw gate "
                        f"{raw_gate.get('disagreement_tiles')} disagreements -> "
                        f"{policy.get('reconciled_definitional', {}).get('count')} definitional "
                        f"(SEMANTIC_V1_VACANT_VS_NATIVE_ISBUILDABLE on buildable), "
                        f"{policy.get('temporal_second_instant', {}).get('count')} temporal, "
                        f"{policy.get('genuine_contradictions', {}).get('count')} contradictions, "
                        f"{policy.get('unresolved_distinct_predicate', {}).get('count')} unresolved"
                    ),
                )
            )
        else:
            rows.append(_absent_row(EvidenceDomain.RECONCILIATION_DERIVED, reconciliation, loaded))
    rebinding = (
        inputs.reconciliation_dir / "p08-native-isbuildable-rebinding-report.json"
        if inputs.reconciliation_dir
        else None
    )
    if rebinding is not None:
        loaded, sha = _read_json(rebinding)
        if isinstance(loaded, dict):
            binding = loaded.get("p08_binding") or {}
            rows.append(
                EvidenceRow(
                    domain=EvidenceDomain.RECONCILIATION_DERIVED,
                    source=str(rebinding),
                    sha256=sha,
                    statement=(
                        "ADR-012+ADR-013 combined P08 rebinding: "
                        f"planning-classification binding allowed={binding.get('allowed')}, "
                        "p08_complete false, retained status "
                        f"{binding.get('preserved_retained_status')} preserved "
                        "untouched; the 19 retained-UNKNOWN tiles map to "
                        "TERRAIN_MODIFICATION in the derived planning layer only"
                    ),
                )
            )
        else:
            rows.append(_absent_row(EvidenceDomain.RECONCILIATION_DERIVED, rebinding, loaded))
    correspondence = (
        inputs.seed17_census_candidate / "correspondence-verdict.json"
        if inputs.seed17_census_candidate
        else None
    )
    if correspondence is not None:
        loaded, sha = _read_json(correspondence)
        if isinstance(loaded, dict):
            status = str(loaded.get("status"))
            if status != "REJECTED":
                raise ValueError(
                    "sealed source-save fusion verdict of record drifted: "
                    f"expected REJECTED, read {status}; refusing to derive a "
                    "classification verdict from drifting evidence"
                )
            rows.append(
                EvidenceRow(
                    domain=EvidenceDomain.SEED17_CENSUS,
                    source=str(correspondence),
                    sha256=sha,
                    statement=(
                        f"sealed {loaded.get('mode')} verdict {status} "
                        f"(save binding {loaded.get('save_binding_sha256')}); "
                        "immutable retained history, never relabeled"
                    ),
                )
            )
        else:
            rows.append(_absent_row(EvidenceDomain.SEED17_CENSUS, correspondence, loaded))
    if not rows:
        return DimensionAssessment(
            dimension_id="tile_classification_completeness",
            state=FeasibilityState.UNKNOWN,
            rows=(),
            unknown_reason="no classification evidence artifact was readable",
        )
    if rows and all(row.unobserved for row in rows):
        return DimensionAssessment(
            dimension_id="tile_classification_completeness",
            state=FeasibilityState.UNKNOWN,
            rows=tuple(rows),
            unknown_reason="all classification artifacts were absent or unreadable",
        )
    return DimensionAssessment(
        dimension_id="tile_classification_completeness",
        state=FeasibilityState.PARTIAL,
        rows=tuple(rows),
        blocker_kind=BlockerKind.EVIDENCE_MISSING,
        blocker=(
            "classification is complete and policy-bound only inside the "
            "seed-17 census region and its derived planning layer; "
            "arbitrary random worlds remain "
            "construction-classification-incomplete (P08 keeps "
            "INCOMPLETE_TILE_CLASSIFICATION there), and the six temporal "
            "tiles keep the fusion gate closed"
        ),
    )


def _dimension_source_save_correspondence(inputs: PhaseCInputs) -> DimensionAssessment:
    """Dimension 3: source-save correspondence."""

    loaded, sha = _read_json(inputs.snapshot_report)
    if not isinstance(loaded, dict):
        absent = loaded if isinstance(loaded, _Absent) else _Absent(ABSENT_MARKER, "unreadable")
        return DimensionAssessment(
            dimension_id="source_save_correspondence",
            state=FeasibilityState.UNKNOWN,
            rows=(
                _absent_row(
                    EvidenceDomain.SNAPSHOT_ASSESSMENT_DERIVED, inputs.snapshot_report, absent
                ),
            ),
            unknown_reason="no snapshot gate artifact was readable",
        )
    gate = loaded.get("gate") or {}
    sources = loaded.get("sources") or {}
    row = EvidenceRow(
        domain=EvidenceDomain.SNAPSHOT_ASSESSMENT_DERIVED,
        source=str(inputs.snapshot_report),
        sha256=sha,
        statement=(
            "snapshot gate: sealed save binding "
            f"{gate.get('sealed_save_binding_sha256')} for census-domain world "
            f"{sources.get('world_id')}, completeness reproduced "
            f"{gate.get('completeness_reproduced')}, manifest "
            f"{gate.get('manifest_verified')}/{gate.get('manifest_entries')}; "
            "the cross-instant fusion correspondence of record stays sealed "
            "REJECTED"
        ),
    )
    return DimensionAssessment(
        dimension_id="source_save_correspondence",
        state=FeasibilityState.PARTIAL,
        rows=(row,),
        blocker_kind=BlockerKind.EVIDENCE_MISSING,
        blocker=(
            "identity facts bind the source save and the census domain, but "
            "no same-state V1/V2 fusion correspondence is claimed anywhere"
        ),
    )


def _dimension_industry_cargo(inputs: PhaseCInputs) -> DimensionAssessment:
    """Dimension 4: industry and cargo compatibility."""

    rows: list[EvidenceRow] = []
    loaded, sha = _read_json(inputs.seed17_smoke_summary)
    if isinstance(loaded, dict):
        rows.append(
            EvidenceRow(
                domain=EvidenceDomain.SEED17_SMOKE,
                source=str(inputs.seed17_smoke_summary),
                sha256=sha,
                statement=(
                    f"seed-17 smoke: {loaded.get('industry_count')} industries and "
                    f"{loaded.get('cargo_catalog_count')} cargos observed natively "
                    f"(produced labels {loaded.get('positive_produced_cargo_labels')}); "
                    f"{loaded.get('rejected_compatible_pairs')} compatible pairs "
                    "discovered, capture-admitted "
                    f"{loaded.get('admissible_relationships')} "
                    f"({loaded.get('rejection_reason')})"
                ),
            )
        )
    else:
        rows.append(_absent_row(EvidenceDomain.SEED17_SMOKE, inputs.seed17_smoke_summary, loaded))
    loaded, sha = _read_json(inputs.seed2026_planning_diagnostic)
    if isinstance(loaded, dict):
        rows.append(
            EvidenceRow(
                domain=EvidenceDomain.SEED2026_PLANNING,
                source=str(inputs.seed2026_planning_diagnostic),
                sha256=sha,
                statement=(
                    "seed-2026 planning diagnostic: "
                    f"{len(loaded.get('compatible_relationships') or [])} compatible "
                    f"industry/cargo relationships discovered across "
                    f"{len(loaded.get('industries') or [])} observed industries; "
                    "pair checks stopped at the candidate-search budget "
                    "before whole-pair-space coverage"
                ),
            )
        )
    else:
        rows.append(
            _absent_row(
                EvidenceDomain.SEED2026_PLANNING, inputs.seed2026_planning_diagnostic, loaded
            )
        )
    if not rows or all(row.unobserved for row in rows):
        return DimensionAssessment(
            dimension_id="industry_cargo_compatibility",
            state=FeasibilityState.UNKNOWN,
            rows=tuple(rows),
            unknown_reason="no compatibility evidence artifact was readable",
        )
    return DimensionAssessment(
        dimension_id="industry_cargo_compatibility",
        state=FeasibilityState.VERIFIED,
        rows=tuple(rows),
    )


def _dimension_terrain(inputs: PhaseCInputs) -> DimensionAssessment:
    """Dimension 5: terrain observation completeness."""

    loaded, sha = _read_json(inputs.snapshot_report)
    if not isinstance(loaded, dict):
        absent = loaded if isinstance(loaded, _Absent) else _Absent(ABSENT_MARKER, "unreadable")
        return DimensionAssessment(
            dimension_id="terrain_observation_completeness",
            state=FeasibilityState.UNKNOWN,
            rows=(
                _absent_row(
                    EvidenceDomain.SNAPSHOT_ASSESSMENT_DERIVED, inputs.snapshot_report, absent
                ),
            ),
            unknown_reason="no terrain evidence artifact was readable",
        )
    census = loaded.get("census") or {}
    sources = loaded.get("sources") or {}
    row = EvidenceRow(
        domain=EvidenceDomain.SNAPSHOT_ASSESSMENT_DERIVED,
        source=str(inputs.snapshot_report),
        sha256=sha,
        statement=(
            f"census terrain: {census.get('pages')} pages / "
            f"{census.get('tiles')} tiles with per-tile geometry observed in "
            f"{sources.get('map_width')}x{sources.get('map_height')} map "
            f"(world {sources.get('world_id')}); no terrain outside the "
            "captured rectangle is claimed"
        ),
    )
    return DimensionAssessment(
        dimension_id="terrain_observation_completeness",
        state=FeasibilityState.PARTIAL,
        rows=(row,),
        blocker_kind=BlockerKind.EVIDENCE_MISSING,
        blocker=(
            "terrain facts exist only inside the census region; arbitrary "
            "random worlds carry no terrain observations offline"
        ),
    )


def _dimension_catchment(inputs: PhaseCInputs) -> DimensionAssessment:
    """Dimension 6: catchment and station eligibility."""

    loaded, sha = _read_json(inputs.snapshot_report)
    if not isinstance(loaded, dict):
        absent = loaded if isinstance(loaded, _Absent) else _Absent(ABSENT_MARKER, "unreadable")
        return DimensionAssessment(
            dimension_id="catchment_station_eligibility",
            state=FeasibilityState.UNKNOWN,
            rows=(
                _absent_row(
                    EvidenceDomain.SNAPSHOT_ASSESSMENT_DERIVED, inputs.snapshot_report, absent
                ),
            ),
            unknown_reason="no catchment evidence artifact was readable",
        )
    census = loaded.get("census") or {}
    eligibility = loaded.get("eligibility") or {}
    row = EvidenceRow(
        domain=EvidenceDomain.SNAPSHOT_ASSESSMENT_DERIVED,
        source=str(inputs.snapshot_report),
        sha256=sha,
        statement=(
            f"eligibility recomputed at the census instant: primary pickups "
            f"{eligibility.get('primary_pickups')} / deliveries "
            f"{eligibility.get('primary_deliveries')}, "
            f"{census.get('stop_viable_tiles')} stop-viable tiles; recomputed "
            "catchment geometry equals the historical industry capture "
            "(site stability)"
        ),
    )
    return DimensionAssessment(
        dimension_id="catchment_station_eligibility",
        state=FeasibilityState.PARTIAL,
        rows=(row,),
        blocker_kind=BlockerKind.EVIDENCE_MISSING,
        blocker=(
            "stop eligibility is proven for the census region only; general "
            "random worlds are unmeasured offline"
        ),
    )


def _dimension_reachability(inputs: PhaseCInputs) -> DimensionAssessment:
    """Dimension 7: bounded road reachability."""

    rows: list[EvidenceRow] = []
    loaded, sha = _read_json(inputs.snapshot_report)
    if isinstance(loaded, dict):
        primary = loaded.get("assessment_primary") or {}
        rows.append(
            EvidenceRow(
                domain=EvidenceDomain.SNAPSHOT_ASSESSMENT_DERIVED,
                source=str(inputs.snapshot_report),
                sha256=sha,
                statement=(
                    f"census-region assessment {primary.get('code')} with a "
                    f"{len(primary.get('corridor') or [])}-tile corridor inside "
                    "supported construction classes (clearing plus terrain "
                    "modification required; planning-only diagnostics, no "
                    "construction contract)"
                ),
            )
        )
    else:
        rows.append(
            _absent_row(EvidenceDomain.SNAPSHOT_ASSESSMENT_DERIVED, inputs.snapshot_report, loaded)
        )
    for label, source in (
        ("seed-2026", inputs.seed2026_planning_diagnostic),
        ("seed-2026 widened seal", inputs.seed2026_widened_diagnostic),
    ):
        loaded, sha = _read_json(source)
        if isinstance(loaded, dict):
            rejections = [
                str(rejection.get("reason"))
                for rejection in (loaded.get("candidate_rejections") or [])
                if isinstance(rejection, dict)
            ]
            rows.append(
                EvidenceRow(
                    domain=EvidenceDomain.SEED2026_PLANNING,
                    source=str(source),
                    sha256=sha,
                    statement=(
                        f"{label}: {len(rejections)} captured-candidate "
                        "rejections (NO_BOUNDED_CORRIDOR typed "
                        "disconnections retained verbatim); "
                        f"search_truncated {loaded.get('search_truncated')} "
                        "-> incomplete pair-space search, so no "
                        "observed-world infeasibility verdict from this row"
                    ),
                )
            )
        else:
            rows.append(_absent_row(EvidenceDomain.SEED2026_PLANNING, source, loaded))
    if not rows or all(row.unobserved for row in rows):
        return DimensionAssessment(
            dimension_id="bounded_road_reachability",
            state=FeasibilityState.UNKNOWN,
            rows=tuple(rows),
            unknown_reason="no reachability evidence artifact was readable",
        )
    return DimensionAssessment(
        dimension_id="bounded_road_reachability",
        state=FeasibilityState.PARTIAL,
        rows=tuple(rows),
        blocker_kind=BlockerKind.EVIDENCE_MISSING,
        blocker=(
            "corridors proven only where bounded searches completed; "
            "truncated pair-space searches cannot prove observed-world "
            "infeasibility (and never did)"
        ),
    )


def _dimension_p08(inputs: PhaseCInputs) -> DimensionAssessment:
    """Dimension 8: P08 candidate-generation capability."""

    rows: list[EvidenceRow] = []
    loaded, sha = _read_json(inputs.seed17_smoke_summary)
    if isinstance(loaded, dict):
        rows.append(
            EvidenceRow(
                domain=EvidenceDomain.SEED17_SMOKE,
                source=str(inputs.seed17_smoke_summary),
                sha256=sha,
                statement=(
                    f"seed-17 smoke: P08 {loaded.get('p08_generation')}, candidate "
                    f"count {loaded.get('p08_candidate_count')} (typed discovery "
                    "admission refusal, retained as recorded)"
                ),
            )
        )
    else:
        rows.append(_absent_row(EvidenceDomain.SEED17_SMOKE, inputs.seed17_smoke_summary, loaded))
    loaded, sha = _read_json(inputs.seed2026_planning_diagnostic)
    if isinstance(loaded, dict):
        rows.append(
            EvidenceRow(
                domain=EvidenceDomain.SEED2026_PLANNING,
                source=str(inputs.seed2026_planning_diagnostic),
                sha256=sha,
                statement=(
                    "seed-2026 planning diagnostic: "
                    f"candidate_count {loaded.get('candidate_count')} with "
                    f"{len(loaded.get('candidate_rejections') or [])} typed "
                    "rejections (NO_BOUNDED_CORRIDOR); neither a defect "
                    "finding nor a complete-world verdict"
                ),
            )
        )
    else:
        rows.append(
            _absent_row(
                EvidenceDomain.SEED2026_PLANNING, inputs.seed2026_planning_diagnostic, loaded
            )
        )
    loaded, sha = _read_json(inputs.snapshot_report)
    if isinstance(loaded, dict):
        primary = loaded.get("assessment_primary") or {}
        levelling = loaded.get("levelling") or {}
        rows.append(
            EvidenceRow(
                domain=EvidenceDomain.SNAPSHOT_ASSESSMENT_DERIVED,
                source=str(inputs.snapshot_report),
                sha256=sha,
                statement=(
                    "snapshot adapter: P08 bounded feasibility assessment "
                    f"produced a corridor ({primary.get('code')}) with "
                    f"{levelling.get('ops')} grouped levelling ops "
                    f"(kind {levelling.get('kind')}, attached "
                    f"{levelling.get('attached')}) from the policy-bound "
                    "census input"
                ),
            )
        )
    else:
        rows.append(
            _absent_row(EvidenceDomain.SNAPSHOT_ASSESSMENT_DERIVED, inputs.snapshot_report, loaded)
        )
    if not rows or all(row.unobserved for row in rows):
        return DimensionAssessment(
            dimension_id="p08_candidate_generation",
            state=FeasibilityState.UNKNOWN,
            rows=tuple(rows),
            unknown_reason="no P08 evidence artifact was readable",
        )
    return DimensionAssessment(
        dimension_id="p08_candidate_generation",
        state=FeasibilityState.PARTIAL,
        rows=tuple(rows),
        blocker_kind=BlockerKind.EVIDENCE_MISSING,
        blocker=(
            "candidate generation executes on admissible facts; the observed "
            "random worlds produced empty candidate sets under the current "
            "capture profiles"
        ),
    )


def _dimension_p05(inputs: PhaseCInputs) -> DimensionAssessment:
    """Dimension 9: P05 planning readiness (gate + observed evidence)."""

    rows: list[EvidenceRow] = []
    refusals: list[dict] = []
    loaded, sha = _read_json(inputs.seed2026_planning_diagnostic)
    if isinstance(loaded, dict):
        code, reason = p05_prerequisite(loaded.get("candidate_count"), True)
        refusals.append(
            {
                "domain": EvidenceDomain.SEED2026_PLANNING.value,
                "source": str(inputs.seed2026_planning_diagnostic),
                "sha256": sha,
                "refusal_code": code.value,
                "detail": reason,
                "observed": "candidate_count 0 (NO_FEASIBLE_SERVICES terminal)",
            }
        )
        rows.append(
            EvidenceRow(
                domain=EvidenceDomain.SEED2026_PLANNING,
                source=str(inputs.seed2026_planning_diagnostic),
                sha256=sha,
                statement=(
                    "seed-2026: candidate set empty -> the pipeline refused "
                    "NO_FEASIBLE_SERVICES and P05 never ran "
                    f"(selected_service_count {loaded.get('selected_service_count')}); "
                    "typed failure, no forced selection"
                ),
            )
        )
    else:
        rows.append(
            _absent_row(
                EvidenceDomain.SEED2026_PLANNING, inputs.seed2026_planning_diagnostic, loaded
            )
        )
    loaded, sha = _read_json(inputs.seed2026_widened_diagnostic)
    if isinstance(loaded, dict):
        rows.append(
            EvidenceRow(
                domain=EvidenceDomain.SEED2026_PLANNING,
                source=str(inputs.seed2026_widened_diagnostic),
                sha256=sha,
                statement=(
                    "seed-2026 widened seal: the relationship was interrupted "
                    "inside the month-pacing gate before any candidate set "
                    "existed; P05 untouched"
                ),
            )
        )
    loaded, sha = _read_json(inputs.seed42_demo_result)
    if isinstance(loaded, dict):
        selected = loaded.get("selected_services")
        rows.append(
            EvidenceRow(
                domain=EvidenceDomain.SEED42_DEMO_PLANNING,
                source=str(inputs.seed42_demo_result),
                sha256=sha,
                statement=(
                    "seed-42 demo window-close abort: P05 selected "
                    f"{len(selected) if isinstance(selected, list) else 0} "
                    "services natively before the operator closed the "
                    "client; no delivery receipts (terminal preserved, "
                    "never relabeled)"
                ),
            )
        )
    else:
        rows.append(
            _absent_row(EvidenceDomain.SEED42_DEMO_PLANNING, inputs.seed42_demo_result, loaded)
        )
    if not rows or all(row.unobserved for row in rows):
        return DimensionAssessment(
            dimension_id="p05_planning_readiness",
            state=FeasibilityState.UNKNOWN,
            rows=tuple(rows),
            unknown_reason="no P05 evidence artifact was readable",
        )
    return DimensionAssessment(
        dimension_id="p05_planning_readiness",
        state=FeasibilityState.PARTIAL,
        rows=tuple(rows),
        blocker_kind=BlockerKind.PREREQUISITE_REFUSED,
        blocker=(
            "no random-world candidate set reached a P05 selection; the "
            "typed gate refuses empty and invalid sets fail-closed"
        ),
        refusals=tuple(refusals),
    )


def _dimension_limits(inputs: PhaseCInputs) -> DimensionAssessment:
    """Dimension 10: supported map and search limits (code-pinned)."""

    rows: list[EvidenceRow] = []
    for path in inputs.source_files:
        pin = _LIMIT_PINS.get(Path(path).name)
        if pin is None:
            continue
        if not Path(path).is_file():
            continue
        raw = Path(path).read_bytes()
        text = raw.decode()
        pattern, pinned = pin
        if not pattern.search(text):
            raise ValueError(
                f"pinned limit value {pinned!r} not found in {path}; the "
                "limits dimension refuses stale statements"
            )
        rows.append(
            EvidenceRow(
                domain=EvidenceDomain.SOURCE_TREE,
                source=str(path),
                sha256=hashlib.sha256(raw).hexdigest(),
                statement=(
                    f"{Path(path).name}: supported limit pinned in code and byte-verified: {pinned}"
                ),
            )
        )
    if not rows:
        return DimensionAssessment(
            dimension_id="supported_map_search_limits",
            state=FeasibilityState.UNKNOWN,
            rows=(),
            unknown_reason="no code file could be pinned for the limit constants",
        )
    return DimensionAssessment(
        dimension_id="supported_map_search_limits",
        state=FeasibilityState.VERIFIED,
        rows=tuple(rows),
        blocker_kind=BlockerKind.SCOPE_LIMIT,
        blocker=(
            "supported limits are exact and re-verified; widening any limit "
            "(map size, capture budget, industry ceiling) is a separately "
            "scoped implementation extension, never implicit. A VERIFIED "
            "dimension documenting its boundary does not divert the outcome."
        ),
    )


def decide(dimensions: dict[str, DimensionAssessment]) -> tuple[DecisionOutcome, str]:
    """Deterministic FD-C-2 outcome aggregation.

    Precedence (the first matching step decides; later steps only fire
    when all previous steps are absent):

    1. any ``UNSUPPORTED`` dimension -> ``UNSUPPORTED_CAPABILITY``
    2. any completed-search observed-world infeasibility evidence row ->
       ``INFEASIBLE_FOR_OBSERVED_WORLD``
    3. any ``BLOCKED`` dimension with a ``SCOPE_LIMIT`` blocker ->
       ``SEPARATE_SCOPE_EXTENSION``
    4. any ``PARTIAL``/``UNKNOWN``/``BLOCKED`` dimension ->
       ``INCOMPLETE_EVIDENCE``
    5. otherwise -> ``FEASIBLE_WITHIN_SUPPORTED_CAPABILITIES``
    """

    unsupported = sorted(
        dim.dimension_id for dim in dimensions.values() if dim.state is FeasibilityState.UNSUPPORTED
    )
    if unsupported:
        return DecisionOutcome.UNSUPPORTED_CAPABILITY, (
            f"unsupported capability at dimensions {unsupported}"
        )
    infeasible = sorted(dim.dimension_id for dim in dimensions.values() if dim.observed_infeasible)
    if infeasible:
        return DecisionOutcome.INFEASIBLE_FOR_OBSERVED_WORLD, (
            "observed world proven infeasible by a completed bounded search "
            f"at dimensions {infeasible}"
        )
    scope = sorted(dim.dimension_id for dim in dimensions.values() if dim.scope_limited)
    if scope:
        return DecisionOutcome.SEPARATE_SCOPE_EXTENSION, (
            f"capability boundary reached; needs a separately scoped "
            f"extension at dimensions {scope}"
        )
    incomplete = sorted(
        dim.dimension_id
        for dim in dimensions.values()
        if dim.state
        in (FeasibilityState.PARTIAL, FeasibilityState.UNKNOWN, FeasibilityState.BLOCKED)
    )
    if incomplete:
        return DecisionOutcome.INCOMPLETE_EVIDENCE, (
            f"incomplete evidence at dimensions {incomplete}"
        )
    return DecisionOutcome.FEASIBLE_WITHIN_SUPPORTED_CAPABILITIES, (
        "all dimensions verified within currently supported capabilities"
    )


_NOT_CLAIMED: tuple[str, ...] = (
    "no historical V1/V2 fusion (sealed SOURCE_SAVE_FUSION REJECTED unchanged)",
    "no native construction, terraforming or service execution entitlement",
    "no complete observed-world infeasibility claim: every recorded bounded "
    "random-world search was truncated, not exhausted",
    "no same-instant census claim; per-page provenance and the six temporal "
    "tiles remain the fusion-gate facts",
    "no P08-refusal reinterpretation as a software defect",
    "no production quantity, OPEX or ROI claim",
)

_GATES_FOR_ANY_NEXT_NATIVE: tuple[str, ...] = (
    "fresh frozen-input identity on a new candidate (consumed identities are never reused)",
    "staging -> independent review -> Gate C signing -> ONE launch, each gate separately approved",
    "capture pacing inside the qualified in-game month (the typed "
    "month-pacing gate holds every supplemental capture there)",
    "certified cleanup and single-use claim consumption on every attempt",
)

_RECOMMENDED_BY_OUTCOME: dict[DecisionOutcome, str] = {
    DecisionOutcome.FEASIBLE_WITHIN_SUPPORTED_CAPABILITIES: (
        "a native Random World sub-phase under the standing fences is justified"
    ),
    DecisionOutcome.INFEASIBLE_FOR_OBSERVED_WORLD: (
        "Phase C closes on this statement; native random delivery is not "
        "pursued without a separately scoped capability change"
    ),
    DecisionOutcome.INCOMPLETE_EVIDENCE: (
        "charge the separately scoped operator decision first: resolve the "
        "capture-pacing design (ticket-03 family) under DG-9's fences, then "
        "a fresh gated native capture round; no feasibility flip without "
        "new native evidence"
    ),
    DecisionOutcome.UNSUPPORTED_CAPABILITY: (
        "implement or explicitly scope the unsupported capability before "
        "any further Random World planning work"
    ),
    DecisionOutcome.SEPARATE_SCOPE_EXTENSION: (
        "open the named scope-extension ticket with its own authorization "
        "boundary before further Random World work"
    ),
}


@dataclass(frozen=True)
class PhaseCDecision:
    """The typed FD-C-2 decision document."""

    outcome: DecisionOutcome
    outcome_reason: str
    dimensions: dict[str, DimensionAssessment]
    inputs: dict[str, dict[str, str]]

    def __post_init__(self) -> None:
        missing = [dim for dim in DIMENSION_IDS if dim not in self.dimensions]
        extra = [dim for dim in self.dimensions if dim not in DIMENSION_IDS]
        if missing:
            raise ValueError(f"decision missing dimensions {missing}")
        if extra:
            raise ValueError(f"decision carries unknown dimensions {extra}")

    def report(self) -> dict:
        return {
            "schema": SCHEMA,
            "policy_id": POLICY_ID,
            "offline_only": OFFLINE_ONLY,
            "decision": {
                "outcome": self.outcome.value,
                "outcome_reason": self.outcome_reason,
                "recommended_next_action": _RECOMMENDED_BY_OUTCOME[self.outcome],
                "gates_required_for_any_next_native": list(_GATES_FOR_ANY_NEXT_NATIVE),
                "not_claimed": list(_NOT_CLAIMED),
            },
            "dimensions": [self.dimensions[dim].report_payload() for dim in DIMENSION_IDS],
            "evidence_domains": {
                domain.value: _DOMAIN_DESCRIPTIONS[domain] for domain in EvidenceDomain
            },
            "inputs": dict(sorted(self.inputs.items())),
        }

    def to_json_bytes(self) -> bytes:
        return (json.dumps(self.report(), sort_keys=True, indent=1) + "\n").encode()

    def to_markdown(self) -> bytes:
        report = self.report()
        decision = report["decision"]
        lines: list[str] = [
            "# Random World feasibility decision (FD-C-2)",
            "",
            f"Policy: `{POLICY_ID}`. Offline only: no OpenTTD launch, no "
            "AdminPort connection, no candidate consumption, no historical "
            "evidence modification, no launch authorization of any kind.",
            "",
            "## Decision",
            "",
            f"- Outcome class: **{decision['outcome']}**.",
            f"- Reason: {decision['outcome_reason']}.",
            f"- Recommended next action: {decision['recommended_next_action']}",
            "",
            "### Not claimed",
            "",
        ]
        lines.extend(f"- {item}" for item in decision["not_claimed"])
        lines += ["", "### Gates required for any next native attempt", ""]
        lines.extend(f"- {item}" for item in decision["gates_required_for_any_next_native"])
        lines += [
            "",
            "## Evidence domains (each row carries exactly one)",
            "",
        ]
        lines.extend(f"- **{key}** — {value}" for key, value in report["evidence_domains"].items())
        lines += ["", "## Retained inputs (all read-only, digest-pinned)", ""]
        lines += ["| Label | Path | Digest |", "| --- | --- | --- |"]
        lines.extend(
            f"| {label} | `{payload['path']}` | `{payload['digest']}` |"
            for label, payload in report["inputs"].items()
        )
        lines += ["", "## Dimensions", ""]
        for dimension in report["dimensions"]:
            lines.append(f"### {dimension['id']} — {dimension['title']} — **{dimension['state']}**")
            if dimension.get("blocker"):
                lines.append(f"- Blocker ({dimension['blocker_kind']}): {dimension['blocker']}")
            if dimension.get("unknown_reason"):
                lines.append(f"- Unknown reason: {dimension['unknown_reason']}")
            if dimension["observed_infeasible"]:
                lines.append("- Carries a completed-search observed-world infeasibility row.")
            lines.append("")
            for row in dimension["rows"]:
                suffix = (
                    " *(completed-search observed-world infeasibility row)*"
                    if row["observed_infeasible"]
                    else ""
                )
                lines.append(f"- `[ {row['domain']} ]` {row['statement']}{suffix}")
                lines.append(f"  - source `{row['source']}` sha256 `{row['sha256']}`")
            for refusal in dimension["refusals"]:
                lines.append(
                    f"- P05 gate refusal `{refusal['refusal_code']}` "
                    f"[ {refusal['domain']} ]: {refusal['detail']} "
                    f"(observed: {refusal['observed']})"
                )
            lines.append("")
        return "\n".join(lines).encode()


def _input_catalogue(inputs: PhaseCInputs) -> dict[str, dict[str, str]]:
    """Every inspected input with its digest (``ABSENT`` when unread)."""

    catalogue: dict[str, dict[str, str]] = {}
    entries: tuple[tuple[str, Path | None], ...] = (
        (
            "reconciliation_report",
            inputs.reconciliation_dir / "reconciliation-report.json"
            if inputs.reconciliation_dir
            else None,
        ),
        (
            "reconciliation_adr012_report",
            inputs.reconciliation_dir / "census-authority-policy-report.json"
            if inputs.reconciliation_dir
            else None,
        ),
        (
            "reconciliation_adr013_report",
            inputs.reconciliation_dir / "native-isbuildable-policy-report.json"
            if inputs.reconciliation_dir
            else None,
        ),
        (
            "reconciliation_p08_rebinding_report",
            inputs.reconciliation_dir / "p08-native-isbuildable-rebinding-report.json"
            if inputs.reconciliation_dir
            else None,
        ),
        ("retained_snapshot_report", inputs.snapshot_report),
        ("seed17_smoke_summary", inputs.seed17_smoke_summary),
        ("seed17_smoke_result", inputs.seed17_smoke_result),
        (
            "seed17_correspondence_verdict",
            inputs.seed17_census_candidate / "correspondence-verdict.json"
            if inputs.seed17_census_candidate
            else None,
        ),
        ("seed17_retained_facts", inputs.seed17_retained_facts),
        ("seed2026_planning_diagnostic", inputs.seed2026_planning_diagnostic),
        ("seed2026_result", inputs.seed2026_result),
        ("seed2026_widened_planning_diagnostic", inputs.seed2026_widened_diagnostic),
        ("seed2026_widened_result", inputs.seed2026_widened_result),
        ("seed42_demo_result", inputs.seed42_demo_result),
    )
    for label, path in entries:
        if path is None:
            continue
        catalogue[label] = {"path": str(path), "digest": _digest_of(path)}
    for path in inputs.source_files:
        catalogue[f"source_{Path(path).name}"] = {
            "path": str(path),
            "digest": _digest_of(path),
        }
    return catalogue


def derive_phase_c_decision(inputs: PhaseCInputs) -> PhaseCDecision:
    """Derive the FD-C-2 decision from the retained (or fixture) inputs."""

    assessments = (
        _dimension_source_observation(inputs),
        _dimension_tile_classification(inputs),
        _dimension_source_save_correspondence(inputs),
        _dimension_industry_cargo(inputs),
        _dimension_terrain(inputs),
        _dimension_catchment(inputs),
        _dimension_reachability(inputs),
        _dimension_p08(inputs),
        _dimension_p05(inputs),
        _dimension_limits(inputs),
    )
    dimensions = {assessment.dimension_id: assessment for assessment in assessments}
    outcome, reason = decide(dimensions)
    return PhaseCDecision(
        outcome=outcome,
        outcome_reason=reason,
        dimensions=dimensions,
        inputs=_input_catalogue(inputs),
    )


def main(argv: list[str] | None = None) -> int:
    """Write the derived FD-C-2 decision; never touches retained inputs."""

    parser = argparse.ArgumentParser(description="offline Phase C feasibility decision")
    parser.add_argument("output_dir")
    parser.add_argument("--project-root", default=None)
    args = parser.parse_args(argv)
    root = Path(args.project_root) if args.project_root else Path.cwd()
    decision = derive_phase_c_decision(_default_inputs(root))
    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)
    (output / "feasibility-decision-report.json").write_bytes(decision.to_json_bytes())
    (output / "feasibility-decision-report.md").write_bytes(decision.to_markdown())
    print(
        f"policy={POLICY_ID} outcome={decision.outcome.value} "
        f"outcome_reason={decision.outcome_reason!r} "
        f"inputs={len(decision.inputs)}"
    )
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
