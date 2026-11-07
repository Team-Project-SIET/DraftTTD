"""Focused tests for the offline Phase C feasibility decision engine.

Offline only: no OpenTTD launch, no AdminPort connection, no candidate
consumption, no Gate C signing, no native receipts, no historical evidence
mutation. The engine under test (``app.planning.phase_c_feasibility``) derives
the FD-C-2 decision from retained artifacts with digests recorded; these tests
bind its typed construction rules, the five outcome classes with their
precedence, the typed P05 prerequisite gate, missing/artifact-unreadable
behavior (UNKNOWN, never fabricated), the completed-search infeasibility
constructor, the prohibited-evidence-domain refusal, determinism, and — when
the retained evidence is installed in this checkout — the real decision of
record. Synthetic fixtures are clearly separate fixtures under ``tmp_path``;
they never stand in for native evidence.
"""

import hashlib
import json
import sys
from functools import lru_cache
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))

REPO = Path(__file__).resolve().parents[1]

from app.planning.phase_c_feasibility import (  # noqa: E402
    _COMPLETED_SEARCH_TAG,
    DIMENSION_IDS,
    POLICY_ID,
    PROHIBITED_EVIDENCE_DOMAINS,
    SCHEMA,
    BlockerKind,
    DecisionOutcome,
    DimensionAssessment,
    EvidenceDomain,
    EvidenceRow,
    FeasibilityState,
    P05RefusalCode,
    PhaseCDecision,
    PhaseCInputs,
    _observed_infeasible_row,
    decide,
    derive_phase_c_decision,
    main,
    p05_prerequisite,
)

#: The retained artifacts the real decision is derived from (skipped as a
#: whole when the checkout carries no evidence: UNKNOWN, never fabricated).
SNAPSHOT = REPO / "artifacts/experiments/v2-snapshot-p08-readiness/snapshot-assessment-report.json"
SMOKE = (
    REPO
    / "artifacts/demos/random-smoke-correction-b84b9bd854a342f1a86e4ba669d8e450"
    / "native-smoke-summary.json"
)
SEED2026 = (
    REPO / "artifacts/demos/playable-demo-3e93cc7d1e8d43aab66a4f653665caaa/planning-diagnostic.json"
)
WIDENED = (
    REPO / "artifacts/demos/playable-demo-9b9a398e406f4ec1bf8e37a69116ac93/planning-diagnostic.json"
)
SEED42 = REPO / "artifacts/demos/playable-demo-1570c66a2e564613a102b3e95647e8b1/result.json"
RECONCILIATION = (
    REPO / "artifacts/experiments/v1v2-semantic-reconciliation/reconciliation-report.json"
)
REBINDING = (
    REPO
    / "artifacts/experiments/v1v2-semantic-reconciliation"
    / "p08-native-isbuildable-rebinding-report.json"
)
CORRESPONDENCE = (
    REPO / "artifacts/demos/classification-exec-seed17-3a8f9e46/correspondence-verdict.json"
)

_HEX256 = "0123456789abcdef"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _row(domain: EvidenceDomain, statement: str) -> EvidenceRow:
    """A stub evidence row for aggregation-only tests (no artifact read)."""

    return EvidenceRow(
        domain=domain,
        source="<aggregation test>",
        sha256="ABSENT",
        statement=statement,
    )


def _dim(
    dimension_id: str,
    state: FeasibilityState,
    *,
    blocker_kind: BlockerKind = BlockerKind.NONE,
    blocker: str | None = None,
    domain: EvidenceDomain = EvidenceDomain.SOURCE_TREE,
    rows: tuple[EvidenceRow, ...] | None = None,
) -> DimensionAssessment:
    if rows is None:
        rows = (_row(domain, f"{dimension_id} stub row"),)
    return DimensionAssessment(
        dimension_id=dimension_id,
        state=state,
        rows=rows,
        blocker_kind=blocker_kind,
        blocker=blocker,
        unknown_reason=f"unobserved {dimension_id}" if state is FeasibilityState.UNKNOWN else None,
    )


def _all_dims(**overrides: DimensionAssessment) -> dict[str, DimensionAssessment]:
    """A complete VERIFIED dimension set with per-id overrides."""

    dims = {dim: _dim(dim, FeasibilityState.VERIFIED) for dim in DIMENSION_IDS}
    dims.update(overrides)
    return dims


# --- Typed construction rules ------------------------------------------------


class TestEvidenceRowRules:
    def test_plain_string_foreign_domain_refused(self):
        for name in sorted(PROHIBITED_EVIDENCE_DOMAINS):
            with pytest.raises(ValueError, match="must be an EvidenceDomain"):
                EvidenceRow(domain=name, source="s", sha256="ABSENT", statement="x")

    def test_enum_level_refusal_of_prohibited_names(self):
        # The protective belt's precondition: the admitted domain never
        # contains a prohibited name, so foreign evidence can never enter.
        for name in sorted(PROHIBITED_EVIDENCE_DOMAINS):
            with pytest.raises(ValueError):
                EvidenceDomain(name)

    def test_admitted_domains_and_prohibited_set_are_disjoint(self):
        assert not {d.value for d in EvidenceDomain} & PROHIBITED_EVIDENCE_DOMAINS

    def test_truncated_sha_refused_and_absent_marker_accepted(self):
        with pytest.raises(ValueError, match="sha256"):
            EvidenceRow(
                domain=EvidenceDomain.SOURCE_TREE, source="s", sha256="abc123", statement="x"
            )
        row = EvidenceRow(
            domain=EvidenceDomain.SOURCE_TREE, source="s", sha256="ABSENT", statement="x"
        )
        assert row.report()["observed_infeasible"] is False

    def test_full_sha_accepted(self):
        EvidenceRow(
            domain=EvidenceDomain.SOURCE_TREE, source="s", sha256=_HEX256 * 4, statement="x"
        )

    def test_direct_observed_infeasible_flag_refused(self):
        with pytest.raises(ValueError, match="_observed_infeasible_row"):
            EvidenceRow(
                domain=EvidenceDomain.SEED17_CENSUS,
                source="s",
                sha256="ABSENT",
                statement="anything",
                observed_infeasible=True,
            )


class TestObservedInfeasibilityConstructor:
    def test_verbatim_completed_search_tag_required(self):
        with pytest.raises(ValueError, match="verbatim"):
            _observed_infeasible_row(
                EvidenceDomain.SEED2026_PLANNING,
                "s",
                "ABSENT",
                "bounded search completed for the whole",
            )
        row = _observed_infeasible_row(
            EvidenceDomain.SEED2026_PLANNING,
            "s",
            "ABSENT",
            f"refused everywhere; {_COMPLETED_SEARCH_TAG} (non-truncated)",
        )
        assert row.observed_infeasible is True
        assert row.report()["observed_infeasible"] is True


class TestDimensionAssessmentRules:
    def test_unknown_dimension_id_refused(self):
        with pytest.raises(ValueError, match="unknown dimension id"):
            DimensionAssessment(
                dimension_id="not_a_dimension",
                state=FeasibilityState.UNKNOWN,
                rows=(),
                unknown_reason="r",
            )

    def test_blocked_requires_blocker(self):
        with pytest.raises(ValueError, match="blocker"):
            DimensionAssessment(
                dimension_id=DIMENSION_IDS[0],
                state=FeasibilityState.BLOCKED,
                rows=(_row(EvidenceDomain.SOURCE_TREE, "x"),),
            )

    def test_unknown_requires_reason(self):
        with pytest.raises(ValueError, match="reason"):
            DimensionAssessment(
                dimension_id=DIMENSION_IDS[0],
                state=FeasibilityState.UNKNOWN,
                rows=(),
            )

    def test_blocker_requires_kind(self):
        with pytest.raises(ValueError, match="blocker kind"):
            DimensionAssessment(
                dimension_id=DIMENSION_IDS[0],
                state=FeasibilityState.PARTIAL,
                rows=(_row(EvidenceDomain.SOURCE_TREE, "x"),),
                blocker="text",
            )

    def test_rows_required_for_every_state_except_unknown(self):
        for state in (
            FeasibilityState.VERIFIED,
            FeasibilityState.PARTIAL,
            FeasibilityState.BLOCKED,
        ):
            with pytest.raises(ValueError, match="cannot claim"):
                DimensionAssessment(
                    dimension_id=DIMENSION_IDS[0],
                    state=state,
                    rows=(),
                    blocker="boundary text" if state is FeasibilityState.BLOCKED else None,
                    blocker_kind=(
                        BlockerKind.SCOPE_LIMIT
                        if state is FeasibilityState.BLOCKED
                        else BlockerKind.NONE
                    ),
                )
        DimensionAssessment(
            dimension_id=DIMENSION_IDS[0],
            state=FeasibilityState.UNKNOWN,
            rows=(),
            unknown_reason="row-less unknown allowed",
        )

    def test_scope_limited_property_is_blocked_only(self):
        blocked = DimensionAssessment(
            dimension_id=DIMENSION_IDS[-1],
            state=FeasibilityState.BLOCKED,
            rows=(_row(EvidenceDomain.SOURCE_TREE, "x"),),
            blocker_kind=BlockerKind.SCOPE_LIMIT,
            blocker="boundary reached",
        )
        verified_documenting = DimensionAssessment(
            dimension_id=DIMENSION_IDS[-1],
            state=FeasibilityState.VERIFIED,
            rows=(_row(EvidenceDomain.SOURCE_TREE, "x"),),
            blocker_kind=BlockerKind.SCOPE_LIMIT,
            blocker="documented boundary, honored not hit",
        )
        assert blocked.scope_limited is True
        assert verified_documenting.scope_limited is False


# --- Typed P05 prerequisite gate ---------------------------------------------


class TestP05PrerequisiteGate:
    def test_unknown_count_refused_even_when_valid_flag_absent(self):
        code, reason = p05_prerequisite(None, False)
        assert code is P05RefusalCode.UNKNOWN_CANDIDATE_COUNT
        assert "not zero" in reason

    def test_invalid_candidate_set_refused(self):
        code, _ = p05_prerequisite(4, False)
        assert code is P05RefusalCode.INVALID_CANDIDATE_SET

    def test_invalid_takes_precedence_over_empty(self):
        code, _ = p05_prerequisite(0, False)
        assert code is P05RefusalCode.INVALID_CANDIDATE_SET

    def test_empty_candidate_set_refused(self):
        code, reason = p05_prerequisite(0, True)
        assert code is P05RefusalCode.EMPTY_CANDIDATE_SET
        assert "freight_native_network.py:178" in reason

    def test_admissible_candidate_set(self):
        code, reason = p05_prerequisite(3, True)
        assert code is P05RefusalCode.ADMISSIBLE
        assert "3" in reason


# --- Outcome classes and deterministic precedence ----------------------------


class TestDecisionAggregation:
    def test_all_verified_is_feasible(self):
        outcome, reason = decide(_all_dims())
        assert outcome is DecisionOutcome.FEASIBLE_WITHIN_SUPPORTED_CAPABILITIES
        assert "all dimensions verified" in reason

    def test_verified_dimension_documenting_its_boundary_does_not_divert(self):
        boundary = DimensionAssessment(
            dimension_id="supported_map_search_limits",
            state=FeasibilityState.VERIFIED,
            rows=(_row(EvidenceDomain.SOURCE_TREE, "pinned limit"),),
            blocker_kind=BlockerKind.SCOPE_LIMIT,
            blocker="documented exact boundary",
        )
        outcome, _ = decide(_all_dims(supported_map_search_limits=boundary))
        assert outcome is DecisionOutcome.FEASIBLE_WITHIN_SUPPORTED_CAPABILITIES

    def test_unsupported_wins_over_everything(self):
        infeasible = _observed_infeasible_row(
            EvidenceDomain.SEED2026_PLANNING,
            "s",
            "ABSENT",
            f"NO_FEASIBLE_SERVICES; {_COMPLETED_SEARCH_TAG}",
        )
        outcome, reason = decide(
            _all_dims(
                p08_candidate_generation=_dim(
                    "p08_candidate_generation",
                    FeasibilityState.UNSUPPORTED,
                    rows=(infeasible,),
                ),
                supported_map_search_limits=_dim(
                    "supported_map_search_limits",
                    FeasibilityState.BLOCKED,
                    blocker_kind=BlockerKind.SCOPE_LIMIT,
                    blocker="boundary",
                    rows=(_row(EvidenceDomain.SOURCE_TREE, "x"),),
                ),
            )
        )
        assert outcome is DecisionOutcome.UNSUPPORTED_CAPABILITY
        assert "p08_candidate_generation" in reason

    def test_completed_search_infeasibility_beats_scope_limit(self):
        infeasible = _observed_infeasible_row(
            EvidenceDomain.SEED2026_PLANNING,
            "s",
            "ABSENT",
            f"world exhausted: {_COMPLETED_SEARCH_TAG}",
        )
        outcome, reason = decide(
            _all_dims(
                bounded_road_reachability=_dim(
                    "bounded_road_reachability",
                    FeasibilityState.PARTIAL,
                    rows=(infeasible,),
                    blocker_kind=BlockerKind.EVIDENCE_MISSING,
                    blocker="partial",
                ),
                supported_map_search_limits=_dim(
                    "supported_map_search_limits",
                    FeasibilityState.BLOCKED,
                    blocker_kind=BlockerKind.SCOPE_LIMIT,
                    blocker="boundary",
                    rows=(_row(EvidenceDomain.SOURCE_TREE, "x"),),
                ),
            )
        )
        assert outcome is DecisionOutcome.INFEASIBLE_FOR_OBSERVED_WORLD
        assert "bounded_road_reachability" in reason
        assert "observed world proven infeasible" in reason

    def test_scope_blocked_by_a_blocked_dimension_only(self):
        outcome, reason = decide(
            _all_dims(
                supported_map_search_limits=_dim(
                    "supported_map_search_limits",
                    FeasibilityState.BLOCKED,
                    blocker_kind=BlockerKind.SCOPE_LIMIT,
                    blocker=" widened capture is a separate implementation extension",
                    rows=(_row(EvidenceDomain.SOURCE_TREE, "x"),),
                ),
            )
        )
        assert outcome is DecisionOutcome.SEPARATE_SCOPE_EXTENSION
        assert "supported_map_search_limits" in reason

    def test_partial_unknown_and_blocked_nonscope_are_incomplete_evidence(self):
        partial = _dim("source_observation_completeness", FeasibilityState.PARTIAL)
        unknown = _dim("terrain_observation_completeness", FeasibilityState.UNKNOWN)
        blocked = _dim(
            "p05_planning_readiness",
            FeasibilityState.BLOCKED,
            blocker_kind=BlockerKind.PREREQUISITE_REFUSED,
            blocker="gate refused",
        )
        outcome, reason = decide(
            _all_dims(
                **{
                    "source_observation_completeness": partial,
                    "terrain_observation_completeness": unknown,
                    "p05_planning_readiness": blocked,
                }
            )
        )
        assert outcome is DecisionOutcome.INCOMPLETE_EVIDENCE
        for name in (
            "source_observation_completeness",
            "terrain_observation_completeness",
            "p05_planning_readiness",
        ):
            assert name in reason

    def test_outcome_is_independent_of_the_other_dimensions(self):
        # 4 then 5 without 1–3: BLOCKED with EVIDENCE_MISSING kind is never a
        # scope extension (that kind belongs to capability boundaries only).
        outcome, _ = decide(
            _all_dims(
                supported_map_search_limits=_dim(
                    "supported_map_search_limits",
                    FeasibilityState.BLOCKED,
                    blocker_kind=BlockerKind.EVIDENCE_MISSING,
                    blocker="plain blocked",
                ),
            )
        )
        assert outcome is DecisionOutcome.INCOMPLETE_EVIDENCE


# --- Decision document shape -------------------------------------------------


class TestPhaseCDecisionShapeAndDeterminism:
    def test_missing_and_extra_dimensions_refused(self, tmp_path):
        dims = _all_dims()
        with pytest.raises(ValueError, match="missing dimensions"):
            PhaseCDecision(
                outcome=DecisionOutcome.INCOMPLETE_EVIDENCE,
                outcome_reason="r",
                dimensions={k: v for k, v in dims.items() if k != "p05_planning_readiness"},
                inputs={},
            )
        extra = dict(dims)
        extra["bogus"] = _dim("supported_map_search_limits", FeasibilityState.VERIFIED)
        with pytest.raises(ValueError, match="unknown dimensions"):
            PhaseCDecision(
                outcome=DecisionOutcome.INCOMPLETE_EVIDENCE,
                outcome_reason="r",
                dimensions=extra,
                inputs={},
            )

    def test_report_structure_is_typed_and_ordered(self):
        decision = derive_phase_c_decision(PhaseCInputs())
        report = json.loads(decision.to_json_bytes())
        assert report["schema"] == SCHEMA
        assert report["policy_id"] == POLICY_ID
        assert report["offline_only"] is True
        assert [d["id"] for d in report["dimensions"]] == list(DIMENSION_IDS)
        assert report["decision"]["outcome"] == "INCOMPLETE_EVIDENCE"
        assert report["decision"]["recommended_next_action"]
        assert report["decision"]["not_claimed"]
        assert report["decision"]["gates_required_for_any_next_native"]
        assert report["evidence_domains"]
        assert all(p["digest"] == "ABSENT" for p in report["inputs"].values())

    def test_markdown_carries_the_decision(self):
        markdown = derive_phase_c_decision(PhaseCInputs()).to_markdown().decode()
        assert "# Random World feasibility decision (FD-C-2)" in markdown
        assert "**INCOMPLETE_EVIDENCE**" in markdown
        assert "Not claimed" in markdown
        assert "### source_observation_completeness" in markdown

    def test_two_cold_derivations_are_byte_equal(self):
        first = derive_phase_c_decision(PhaseCInputs())
        second = derive_phase_c_decision(PhaseCInputs())
        assert first.to_json_bytes() == second.to_json_bytes()
        assert first.to_markdown() == second.to_markdown()


# --- Fixture-context derivation (synthetic files under tmp_path) -------------


def _write(path: Path, payload) -> Path:
    """Write one fixture file (bytes pass through, others become JSON)."""

    if isinstance(payload, bytes):
        path.write_bytes(payload)
    else:
        path.write_text(json.dumps(payload))
    return path


class TestFixtureDerivation:
    def test_all_absent_inputs_give_unknown_rows_and_incomplete_outcome(self, tmp_path):
        root = tmp_path / "nowhere"
        inputs = PhaseCInputs(
            reconciliation_dir=root / "reconciliation",
            snapshot_report=root / "snapshot.json",
            seed17_smoke_summary=root / "smoke.json",
            seed17_smoke_result=root / "smoke-result.json",
            seed17_census_candidate=root / "candidate",
            seed2026_planning_diagnostic=root / "seed2026.json",
            seed2026_result=root / "seed2026-result.json",
            seed2026_widened_diagnostic=root / "widened.json",
            seed2026_widened_result=root / "widened-result.json",
            seed42_demo_result=root / "seed42.json",
            source_files=(),
        )
        decision = derive_phase_c_decision(inputs)
        assert decision.outcome is DecisionOutcome.INCOMPLETE_EVIDENCE
        states = {d: assessment.state for d, assessment in decision.dimensions.items()}
        assert set(states.values()) == {FeasibilityState.UNKNOWN}
        # UNKNOWN rows are statements of absence, never fabricated facts.
        for assessment in decision.dimensions.values():
            for row in assessment.rows:
                assert row.sha256 == "ABSENT"
                assert "unobserved" in row.statement

    def test_present_but_unreadable_artifacts_carry_real_digests(self, tmp_path):
        root = tmp_path / "garbled"
        root.mkdir()
        snapshot = _write(root / "snapshot.json", b"{ clearly not json")
        smoke = _write(root / "smoke.json", [1, 2, 3])  # JSON array, not an object
        inputs = PhaseCInputs(
            snapshot_report=snapshot,
            seed17_smoke_summary=smoke,
            seed2026_planning_diagnostic=root / "absent.json",
            source_files=(),
        )
        decision = derive_phase_c_decision(inputs)
        correspondence_dim = decision.dimensions["source_save_correspondence"]
        assert correspondence_dim.state is FeasibilityState.UNKNOWN
        assert correspondence_dim.rows[0].sha256 == _sha(snapshot)
        assert "not valid JSON" in correspondence_dim.rows[0].statement
        smoke_dim = decision.dimensions["industry_cargo_compatibility"]
        assert smoke_dim.state is FeasibilityState.UNKNOWN
        assert smoke_dim.rows[0].sha256 == _sha(smoke)
        assert "not a JSON object" in smoke_dim.rows[0].statement

    def test_non_rejected_fusion_verdict_is_a_construction_refusal(self, tmp_path):
        candidate = tmp_path / "candidate"
        candidate.mkdir()
        _write(candidate / "correspondence-verdict.json", {"status": "PASSED", "mode": "X"})
        inputs = PhaseCInputs(seed17_census_candidate=candidate)
        with pytest.raises(ValueError, match="drifted"):
            derive_phase_c_decision(inputs)

    def test_rejected_fusion_verdict_is_recorded_verbatim(self, tmp_path):
        candidate = tmp_path / "candidate"
        candidate.mkdir()
        _write(
            candidate / "correspondence-verdict.json",
            {"status": "REJECTED", "mode": "SOURCE_SAVE_FUSION", "save_binding_sha256": "f9" * 32},
        )
        inputs = PhaseCInputs(seed17_census_candidate=candidate)
        decision = derive_phase_c_decision(inputs)
        rows = decision.dimensions["tile_classification_completeness"].rows
        assert any(
            "SOURCE_SAVE_FUSION verdict REJECTED" in row.statement and "f9" * 32 in row.statement
            for row in rows
        )

    def test_smoke_only_fixture_verifies_industry_dim_and_partial_rest(self, tmp_path):
        smoke = _write(
            tmp_path / "native-smoke-summary.json",
            {
                "industry_count": 10,
                "cargo_catalog_count": 11,
                "positive_produced_cargo_labels": ["GRASS"],
                "rejected_compatible_pairs": 6,
                "admissible_relationships": 0,
                "rejection_reason": "CAPTURE_REGION_BOUND",
                "p08_generation": "NOT_RUN; discovery admitted zero relationships",
                "p08_candidate_count": 0,
                "p05_status": "NOT_RUN",
                "status": "FAILED",
            },
        )
        decision = derive_phase_c_decision(
            PhaseCInputs(seed17_smoke_summary=smoke, source_files=())
        )
        assert (
            decision.dimensions["industry_cargo_compatibility"].state is FeasibilityState.VERIFIED
        )
        assert decision.dimensions["p08_candidate_generation"].state is FeasibilityState.PARTIAL
        # The smoke evidence must land in the seed-17 smoke domain only.
        for assessment in decision.dimensions.values():
            for row in assessment.rows:
                if "native generation/discovery/GUI verified" in row.statement:
                    assert row.domain is EvidenceDomain.SEED17_SMOKE

    def test_seed2026_empty_candidates_give_the_typed_p05_refusal(self, tmp_path):
        diagnostic = _write(
            tmp_path / "planning-diagnostic.json",
            {
                "compatible_relationships": [{"source": 0, "destination": 1}],
                "candidate_count": 0,
                "selected_service_count": None,
                "status": "FAILED",
                "error": (
                    "ValueError: NO_FEASIBLE_SERVICES: "
                    "no supported full-load road engine and supply"
                ),
                "capture_requests_completed": 400,
                "search_truncated": True,
            },
        )
        decision = derive_phase_c_decision(
            PhaseCInputs(seed2026_planning_diagnostic=diagnostic, source_files=())
        )
        p05 = decision.dimensions["p05_planning_readiness"]
        assert p05.refusals
        refusal = p05.refusals[0]
        assert refusal["refusal_code"] == P05RefusalCode.EMPTY_CANDIDATE_SET.value
        assert refusal["domain"] == EvidenceDomain.SEED2026_PLANNING.value
        assert refusal["sha256"] == _sha(diagnostic)
        assert any("NO_FEASIBLE_SERVICES" in row.statement for row in p05.rows)

    def test_widened_run_produces_the_month_pacing_refusal_row(self, tmp_path):
        widened = _write(
            tmp_path / "planning-diagnostic.json",
            {
                "status": "FAILED",
                "error": "PlanningFactError: supplemental capture outside final M2 month",
                "capture_requests_completed": 712282,
            },
        )
        decision = derive_phase_c_decision(
            PhaseCInputs(seed2026_widened_diagnostic=widened, source_files=())
        )
        rows = decision.dimensions["source_observation_completeness"].rows
        typed = [row for row in rows if row.domain is EvidenceDomain.SEED2026_PLANNING]
        assert any("outside final M2 month" in row.statement for row in typed)
        assert any("typed refusal of record" in row.statement for row in rows)

    def test_month_pacing_row_is_never_an_infeasibility_row(self, tmp_path):
        widened = _write(
            tmp_path / "planning-diagnostic.json",
            {
                "status": "FAILED",
                "error": "PlanningFactError: supplemental capture outside final M2 month",
            },
        )
        decision = derive_phase_c_decision(
            PhaseCInputs(seed2026_widened_diagnostic=widened, source_files=())
        )
        for assessment in decision.dimensions.values():
            assert assessment.observed_infeasible is False

    def test_limits_dimension_pins_code_constants_fail_closed(self):
        decision = derive_phase_c_decision(
            PhaseCInputs(
                source_files=tuple(
                    REPO / p
                    for p in (
                        "app/simulation/openttd/supplemental_planning_facts.py",
                        "app/demo_random.py",
                        "app/simulation/openttd/industry_inventory.py",
                        "app/planning/p08_network.py",
                        "app/planning/p08_adapter.py",
                        "app/simulation/openttd/freight_native_network.py",
                    )
                )
            )
        )
        limits = decision.dimensions["supported_map_search_limits"]
        assert limits.state is FeasibilityState.VERIFIED
        statements = " | ".join(row.statement for row in limits.rows)
        assert "MAX_RANDOM_TILES = 2048" in statements
        assert "capture_tile_limit: Literal[256, 512, 2048]" in statements
        assert "MAX_SERVICE_PACKAGES = 16" in statements
        assert "MAX_PATH_EXPANSIONS = MAX_STATION_PAIRS * 256" in statements
        assert "NATIVE_CORRIDOR_BOUND: requires 2..47 road tiles" in statements
        for row in limits.rows:
            assert row.domain is EvidenceDomain.SOURCE_TREE
            assert len(row.sha256) == 64

    def test_drifted_constant_refuses_the_limits_dimension(self, tmp_path):
        drifted = tmp_path / "supplemental_planning_facts.py"
        drifted.write_text("MAX_RANDOM_TILES = 4096\n")
        with pytest.raises(ValueError, match="stale statements"):
            derive_phase_c_decision(
                PhaseCInputs(source_files=(drifted, REPO / "app/demo_random.py"))
            )

    def test_limits_dimension_without_code_files_is_unknown(self):
        decision = derive_phase_c_decision(PhaseCInputs(source_files=()))
        limits = decision.dimensions["supported_map_search_limits"]
        assert limits.state is FeasibilityState.UNKNOWN
        assert limits.unknown_reason


# --- Real retained decision (skip when the evidence is not installed) --------


def retained_inputs() -> PhaseCInputs:
    return PhaseCInputs(
        reconciliation_dir=REPO / "artifacts/experiments/v1v2-semantic-reconciliation",
        snapshot_report=SNAPSHOT,
        seed17_smoke_summary=SMOKE,
        seed17_smoke_result=REPO
        / "artifacts/demos/playable-demo-b84b9bd854a342f1a86e4ba669d8e450/result.json",
        seed17_census_candidate=REPO / "artifacts/demos/classification-exec-seed17-3a8f9e46",
        seed2026_planning_diagnostic=SEED2026,
        seed2026_result=REPO
        / "artifacts/demos/playable-demo-3e93cc7d1e8d43aab66a4f653665caaa/result.json",
        seed2026_widened_diagnostic=WIDENED,
        seed2026_widened_result=REPO
        / "artifacts/demos/playable-demo-9b9a398e406f4ec1bf8e37a69116ac93/result.json",
        seed42_demo_result=SEED42,
        source_files=tuple(
            REPO / relative
            for relative in (
                "app/simulation/openttd/supplemental_planning_facts.py",
                "app/demo_random.py",
                "app/simulation/openttd/industry_inventory.py",
                "app/planning/p08_network.py",
                "app/planning/p08_adapter.py",
                "app/simulation/openttd/freight_native_network.py",
            )
        ),
    )


@pytest.mark.skipif(
    not all(
        (
            SNAPSHOT.is_file(),
            SMOKE.is_file(),
            SEED2026.is_file(),
            WIDENED.is_file(),
            SEED42.is_file(),
            RECONCILIATION.is_file(),
            REBINDING.is_file(),
            CORRESPONDENCE.is_file(),
        )
    ),
    reason="retained Random World evidence is not installed in this checkout",
)
class TestRetainedDecision:
    @lru_cache(maxsize=1)
    def _decision(self):
        return derive_phase_c_decision(retained_inputs())

    def test_decision_of_record_is_incomplete_evidence(self):
        assert self._decision().outcome is DecisionOutcome.INCOMPLETE_EVIDENCE
        assert "incomplete evidence" in self._decision().outcome_reason

    def test_dim_states_of_record(self):
        states = {
            bit: assessment.state.value for bit, assessment in self._decision().dimensions.items()
        }
        assert states == {
            "source_observation_completeness": "PARTIAL",
            "tile_classification_completeness": "PARTIAL",
            "source_save_correspondence": "PARTIAL",
            "industry_cargo_compatibility": "VERIFIED",
            "terrain_observation_completeness": "PARTIAL",
            "catchment_station_eligibility": "PARTIAL",
            "bounded_road_reachability": "PARTIAL",
            "p08_candidate_generation": "PARTIAL",
            "p05_planning_readiness": "PARTIAL",
            "supported_map_search_limits": "VERIFIED",
        }

    def test_no_observed_world_infeasibility_anywhere(self):
        for assessment in self._decision().dimensions.values():
            assert assessment.observed_infeasible is False
            for row in assessment.rows:
                assert _COMPLETED_SEARCH_TAG not in row.statement
                assert row.observed_infeasible is False

    def test_every_row_is_domain_clean_and_digest_pinned(self):
        for assessment in self._decision().dimensions.values():
            assert assessment.rows
            for row in assessment.rows:
                assert isinstance(row.domain, EvidenceDomain)
                assert row.domain.value not in PROHIBITED_EVIDENCE_DOMAINS
                assert row.sha256 != "ABSENT"
                assert len(row.sha256) == 64

    def test_inputs_are_all_present_and_pinned(self):
        inputs = self._decision().inputs
        assert len(inputs) == 19
        assert all(payload["digest"] != "ABSENT" for payload in inputs.values())
        assert len({payload["digest"] for payload in inputs.values()}) == 19

    def test_rows_carry_the_retained_facts_spot_checked(self):
        decision = self._decision()
        assert any(
            "outside final M2 month" in row.statement
            for assessment in decision.dimensions.values()
            for row in assessment.rows
        )
        assert any(
            "sealed SOURCE_SAVE_FUSION verdict REJECTED" in row.statement
            for assessment in decision.dimensions.values()
            for row in assessment.rows
        )
        assert any(
            "TERRAIN_MODIFICATION in the derived planning layer only" in row.statement
            for assessment in decision.dimensions.values()
            for row in assessment.rows
        )
        assert any(
            "MAX_RANDOM_TILES = 2048" in row.statement
            for row in decision.dimensions["supported_map_search_limits"].rows
        )

    def test_two_independent_derivation_runs_are_byte_equal(self, tmp_path):
        first = derive_phase_c_decision(retained_inputs())
        second = derive_phase_c_decision(retained_inputs())
        assert first.to_json_bytes() == second.to_json_bytes()
        assert first.to_markdown() == second.to_markdown()

    def test_cli_writes_a_deterministic_pair(self, tmp_path):
        first_dir = tmp_path / "first"
        second_dir = tmp_path / "second"
        argv = lambda out: [str(out), "--project-root", str(REPO)]  # noqa: E731
        assert main(argv(first_dir)) == 0
        assert main(argv(second_dir)) == 0
        for name in ("feasibility-decision-report.json", "feasibility-decision-report.md"):
            assert (first_dir / name).read_bytes() == (second_dir / name).read_bytes()
        report = json.loads((first_dir / "feasibility-decision-report.json").read_bytes())
        assert report["schema"] == SCHEMA
        assert report["decision"]["outcome"] == "INCOMPLETE_EVIDENCE"
