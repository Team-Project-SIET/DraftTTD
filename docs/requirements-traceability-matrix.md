# Requirements traceability matrix (2026-11-13)

This matrix traces the system's core requirements to the components that
implement them, the customer use cases they serve, the focused test suites
that guard them, and the evidence rows that prove (or honestly qualify) them.
It complements — and defers to — the consolidated requirements → evidence view
of record, [requirements-evidence-matrix.md](requirements-evidence-matrix.md),
and the requirement sources in [srs.md](srs.md).

Status labels follow [CUSTOMER_PRESENTATION_INDEX.md](CUSTOMER_PRESENTATION_INDEX.md) §1.
Branch of record: `miles/fright-delivery`, HEAD `90ebadb`. Documentation only
— no runtime authorization.

## How to read the test column

Test files are cited by the repo's focused-suite convention: offline suites
(`tests/test_X.py`) pair with controlled native suites (`tests/test_X_native.py`),
and the `openttd` marker plus `--run-openttd` / `--run-postgres` gates the only
truly native runs — check a file's markers before assuming how it runs
([REPRODUCE.md](../REPRODUCE.md)). Suites backed by retained `artifacts/`
evidence can fail on a clone because evidence is missing — that is missing
evidence, not a code bug, and the fix is never regenerating evidence.

## Matrix

| Req | Requirement | Implementing components | Use case | Test files | Evidence | Status |
| --- | --- | --- | --- | --- | --- | --- |
| R-01 | Encrypted, authenticated Admin transport (X25519 + per-direction keys, MAC, strict framing) | `app/simulation/openttd/admin_crypto.py`, `admin_session.py`, `secure_admin.py`, `admin_protocol.py` | UC-1, UC-8 | `tests/test_admin_protocol.py`, `tests/test_admin_observer.py`, `tests/test_ed25519_cryptography.py` | E1 (encrypted session), E40/E49 (handshake `AUTHENTICATED`/`VERIFIED`) | VERIFIED |
| R-02 | Runtime qualification: binary/asset pins, effective settings, source-trust checks | `app/simulation/openttd/proof/native.py`, `runtime/assets` paths, demo `check` CLI | UC-1, UC-7 | `tests/test_runtime_assets.py`, `tests/test_native_save_path.py` | REPRODUCE.md pins (`276d5b69…1904c`, `43a0c1da…03be`) | VERIFIED |
| R-03 | Bounded road-candidate generation for planning (P08) | `app/planning/p08_road.py`, `p08_network.py`, `p08_adapter.py`, `canonical.py` | UC-5, UC-1 | `tests/test_p08_bounded_routing.py`, `tests/test_p08_controlled_e2e.py`, `tests/test_p08_feasibility_classification.py` | Gap analysis (bounded candidates); E142 feasibility binding | CONTROLLED |
| R-04 | Service selection optimization (P05, CP-SAT, bounded) | `app/planning/optimizer.py` | UC-1, UC-2 | `tests/test_planning_optimizer.py`, `tests/test_p08_classification_workflow.py` | E1 (3 P05-selected services); E119 (selection of record, reproducible 5/5) | VERIFIED within fixed attempts; offline layer CONTROLLED |
| R-05 | Typed planning contracts and fail-closed validation (anti-bypass) | `app/planning/domain.py`, `app/planning/validation.py` | UC-1, UC-7 | `tests/test_supplemental_planning_contracts.py`, `tests/test_plan_setup.py` | `validation.py:78-86` re-parse; ADR-0001 label discipline | CONTROLLED |
| R-06 | ExecutionPlan compilation into staged GameScript packages + wire schedules | `app/simulation/openttd/` compiler/executor stack (`freight_delivery_package/`, `gamescript_transport.py`) | UC-1, UC-3 | `tests/test_freight_delivery.py`, `tests/test_gamescript_protocol.py`, `tests/test_gamescript_transport_classification.py` | Staged↔live byte-equality reviews (E122/E131) | VERIFIED (staging) / native use PROVEN per scope |
| R-07 | Native freight delivery in fixed prepared worlds | `app/simulation/openttd/proof/freight_delivery.py`, driver stack | UC-1, UC-2 | `tests/test_live_service.py`, `tests/test_plan_live_runner.py`, `tests/test_native_freight_network.py` | E1; Attempts 4/9/12/14/17 (README §handover) | VERIFIED (fixed demo scope) |
| R-08 | Receipt replay verification and certified cleanup | `app/simulation/openttd/proof/road_mutation.py`, `historical_protection.py`, `native.py` | UC-8 | `tests/test_road_mutation.py`, `tests/test_outcome_manifest.py`, `tests/test_workspace_recovery.py`, `tests/test_historical_protection.py` | Cleanup gates 4/4 flags (`road_mutation.py:607-612`); E1 cleanup PASS | VERIFIED |
| R-09 | P07 offline reporting/analytics from retained receipts | `app/experiments/performance_insights.py`, `native_attempt_analytics.py` | UC-7 | `tests/test_performance_insights.py`, `tests/test_native_attempt_analytics.py`, `tests/test_p07_proof_harness.py` | E1 (fresh P07), E126 (replay closure, three outputs) | VERIFIED |
| R-10 | Random-world generation and planning feasibility | demo CLI `--random-world`; `app/planning/phase_c_feasibility.py` | UC-5 | `tests/test_demo_random.py`, `tests/test_demo_random_native.py`, `tests/test_random_capture_schema.py` | E142 (FD-C-1 verified / FD-C-2 `INCOMPLETE_EVIDENCE`), E204, E198–E201 | PARTIAL — generation/feasibility CONTROLLED; observed-world delivery UNPROVEN |
| R-11 | Corridor road/station/depot construction (reviewed v3 scope) | corridor construction pipeline (`proof/corridor_*_native.py`) | UC-3 | `tests/test_corridor_construction_native.py`, `tests/test_corridor_extension_native.py`, `tests/test_corridor_depot_mutation.py` | E35 (all seven v3 ops verified, receipt-bound after-save), E44 | PROVEN (v3 scope only) |
| R-12 | Read-only corridor survey and acceptance census | `corridor_accept_survey_native.py`, `corridor_box_census.py` | UC-4 | `tests/test_corridor_accept_survey.py`, `tests/test_corridor_terrain_survey.py` | E40 (A0 survey), E44 (A1 extension), E49 (census `SURVEY_COMPLETION_VERIFIED`) | VERIFIED |
| R-13 | Corridor cargo-flow execution and delivery (Cargoflow2) | `corridor_cargoflow2_native.py`, freight-v2 contracts | UC-3 (delivery gap) | `tests/test_corridor_cargoflow2.py`, `tests/test_corridor_cargoflow_native.py`, `tests/test_corridor_freight_v2.py` | E36 (open), E124/E133 (`CARGOFLOW2_LOADED_NEVER_DELIVERED`), E128 (root cause), E134/E135 | PARTIAL — pipeline executes natively; delivery NOT PROVEN, E36 open |
| R-14 | Operator authorization ceremony (staging → review → Gate C → one-shot claim → launch) | `proof/operator_authorization.py`, `terrain_clearing.py`, Gate C signers | UC-8 | `tests/test_proof_cli.py`, `tests/test_preparation_lifecycle.py`, `tests/test_live_launch_preparation.py` | `operator_authorization.py:347-348`; `terrain_clearing.py:1376-1382`; E132/E137 signing records | VERIFIED |
| R-15 | Runtime isolation from the user's OpenTTD profile and owned-process hygiene | `app/simulation/openttd/runtime/config.py`, `ownership.py`, `external.py` | UC-1, UC-8 | `tests/test_workspace_recovery.py`, `tests/test_runtime_assets.py` | `runtime/config.py:52-56` refusal; certified cleanup flags | VERIFIED |
| R-16 | Canonical fleet identity and continuous (create/reload) correspondence | `app/planning/canonical.py`, canonical fleet modules | UC-6 | `tests/test_canonical_fleet_exercise.py`, `tests/test_canonical_fleet_gui.py`, `tests/test_canonical_reload_context.py`, `tests/test_freight_canonical_persistence.py` | E2 (canonical create/reload correspondence) | VERIFIED |
| R-17 | Long-horizon economy observation (canonical continuous pipeline) | continuous pipeline + consolidation (Phase B stack) | UC-6 | `tests/test_phase_b_consolidation.py`, `tests/test_freight_continuous_analytics.py`, `tests/test_freight_finance.py` | E195 (`CANONICAL_FIVE_YEAR_CONTINUOUS_VERIFIED`, 1951–1955) | VERIFIED |
| R-18 | Regression floor: full-suite gate with typed dispositions | whole `tests/` tree; command of record in REPRODUCE.md | all | full suite (E207/E208 runs) | E207 (baseline 57 failed/54 skipped, immutable), E208 (green 6327/55/0, exit 0) | CONTROLLED |

## Coverage notes and honest gaps

- **Every row has evidence; no row is marked implemented on promise alone.**
  Rows R-10 and R-13 carry their PARTIAL status deliberately — random-world
  delivery and corridor cargo delivery are the two material unproven
  capabilities (E36 open; Phase C `INCOMPLETE_EVIDENCE`), and Phase D's WS-D2
  and WS-D3 exist precisely to close them under operator grants
  ([customer-future-development.md](customer-future-development.md)).
- **Not in scope of this matrix:** rail delivery (NOT IMPLEMENTED — no
  components exist; WS-D4 is an offline-only future build), concurrency,
  paid shared-asset reuse, closed-loop optimization, GUI product scope
  (probes VERIFIED E170/E180; product scope unbuilt), OPEX/ROI reporting
  (UNKNOWN per ADR-0001 D5).
- **Requirement wording authority:** this matrix restates requirements
  compactly for traceability; the normative wording lives in the source docs
  ([srs.md](srs.md), [requirements-evidence-matrix.md](requirements-evidence-matrix.md),
  spec/ADR files). Where wording and evidence disagree, trust the retained
  `artifacts/` evidence per the trust order in
  [CUSTOMER_PRESENTATION_INDEX.md](CUSTOMER_PRESENTATION_INDEX.md) §4.

## Related documents

- Customer presentation index: [CUSTOMER_PRESENTATION_INDEX.md](CUSTOMER_PRESENTATION_INDEX.md)
- Requirements → evidence view of record: [requirements-evidence-matrix.md](requirements-evidence-matrix.md)
- Use cases: [customer-use-cases.md](customer-use-cases.md)
