# Project Phase C — Random World reconciliation & feasibility (FD-C-1 / FD-C-2)

Date: 2026-11-07. Offline only. This round executed no OpenTTD launch, no
AdminPort connection, no candidate staging or signing, no claim consumption,
no native receipt acceptance and no mutation of any retained `artifacts/`
bytes; it grants no runtime authority of any kind. It implements the two
offline deliverables of §4 of
[the roadmap](roadmap-and-scope-2026-11-05.md) — FD-C-1
(Random World reconciliation record-of-record) and FD-C-2 (a typed Random
World feasibility decision engine with reports and tests) — and records what
each one actually verified. Nothing here claims that Random World freight
delivery is delivered or proven.

## 1. FD-C-1 — reconciliation record-of-record (verified, not rebuilt)

The reconciliation itself was already implemented and offline-activated in
the 2026-10-18/2026-10-25 rounds (policy `vacant-projection-1`, operator
decisions ADR-012 and ADR-013); see
[the reconciliation record](p08-v1v2-semantic-reconciliation.md), [the six-tile
policy decision](random-world-six-tile-policy-decision.md),
[ADR-012](handoff/2026-10-24/adr-012-six-temporal-tiles-census-authority.md)
and [ADR-013](handoff/2026-10-25/adr-013-p08-native-isbuildable-definitional-semantics.md).
This round therefore verified it rather than rebuilding it, by independent
re-derivation from the retained inputs
(`artifacts/demos/playable-demo-698799a2dfb146948fd2983ff2032253/network-facts-0.json`
sealed against `artifacts/demos/classification-exec-seed17-3a8f9e46/`):

- `reconciliation-report.json` sha256 `c1cfa970c2ccb8310b6bfb1f949ecbd846887ea9c3b04b3b763fe84ef2acf34d`
  — re-derived byte-equal. Verdict `SEMANTICALLY_RECONCILED_TEMPORAL_UNRESOLVED`
  with 83 `PROJECTED_FLAGS_DIFFER` disagreements resolved as 77 definitional
  `SEMANTIC_RECONCILED` (`SEMANTIC_V1_VACANT_VS_NATIVE_ISBUILDABLE` on
  `buildable`), 6 `TEMPORAL_SECOND_INSTANT` tiles (43951, 47286, 47288,
  48042, 48309, 51378), 0 genuine contradictions and 0 unresolved.
- `census-authority-policy-report.json` sha256 `221ce926cd0b24f3b1e32cb7d73b3844c93b5d9837f03187a2d6d6c15e0faf28`
  and `native-isbuildable-policy-report.json` sha256 `7616f6262c99dc7a97bd26c0043dcc1c0dc6ba5287f1b203b1ffe72529a3a65d`
  — re-derived byte-equal (ADR-012 then ADR-013 activations).
- `p08-native-isbuildable-rebinding-report.json` sha256 `079fce64c4a37295c05cb87cf129aa9317abccfddba9114bb84341ee04adee62`
  — re-derived byte-equal via `rebind_p08_policy`; the combined P08 binding
  is `allowed=true` for planning-classification only (`p08_complete=false`),
  rebinding 19 UNKNOWN → `TERRAIN_MODIFICATION` in the derived planning
  layer while the retained statuses stay untouched.
- `p08-policy-rebinding-report.json` sha256 `c9d11d41aba6e937b73897ea9d358897581990788af45c627ad1b32a5b107ed0`
  — re-derived byte-equal (same constructor, ADR-012 report bytes).
- `p08-unknown-occupancy-diagnosis.json` sha256 `66ed07ccf2fb519d713aa6069c51aabb210281e2dbbc2a967eae1c5fe7b7e459`
  — re-derived JSON-value-identical but **not byte-equal**: the retained
  serialization came from a one-off 2026-10-25 driver, not from the live
  module's `to_json_bytes`. The diagnosis itself (19 `DEFINITIONAL_
  VACANT_VS_NATIVE_ISBUILDABLE_SLOPED_CLEAR` tiles, `resolved=false`,
  all evidence consistent) reproduces exactly.

The sealed verdicts stay untouched: `SOURCE_SAVE_FUSION REJECTED`
(`correspondence-verdict.json`, save binding `f9ae7dcba3bf862bc0b1de7c2a2eb781978beb92c152c97a2a6b6d2d4f8fda70`)
and the retained P08 `INCOMPLETE_TILE_CLASSIFICATION` are immutable history;
the derived 19-tile mapping never relabels them. Focused suites of record:
`tests/test_v2_semantic_reconciliation.py` (15),
`tests/test_census_authority_policy.py` (14),
`tests/test_p08_policy_rebinding.py` (41),
`tests/test_p08_v2_snapshot.py` (13) — 83 passed.

## 2. FD-C-2 — the typed feasibility decision engine

New module `app/planning/phase_c_feasibility.py` (sha256 of the committed
bytes `c585874d9c547ae5…`, 1471 lines) with CLI
`python -m app.planning.phase_c_feasibility <output_dir> [--project-root …]`
emitting `feasibility-decision-report.json` + `.md`
(schema `phase-c-feasibility-decision/1`, policy `phase-c-feasibility/1`).
Design points enforced in code:

- **Ten required dimensions** in task order
  (`source_observation_completeness`, `tile_classification_completeness`,
  `source_save_correspondence`, `industry_cargo_compatibility`,
  `terrain_observation_completeness`, `catchment_station_eligibility`,
  `bounded_road_reachability`, `p08_candidate_generation`,
  `p05_planning_readiness`, `supported_map_search_limits`), each stated
  `VERIFIED`/`PARTIAL`/`UNSUPPORTED`/`BLOCKED`/`UNKNOWN` with verbatim
  evidence rows.
- **Five outcome classes** with deterministic precedence in
  `decide()`: any `UNSUPPORTED` dimension → `UNSUPPORTED_CAPABILITY`;
  any completed-search observed-world infeasibility row →
  `INFEASIBLE_FOR_OBSERVED_WORLD`; any `BLOCKED` dimension carrying a
  `SCOPE_LIMIT` blocker → `SEPARATE_SCOPE_EXTENSION`; any other
  `PARTIAL`/`UNKNOWN`/`BLOCKED` dimension → `INCOMPLETE_EVIDENCE`;
  otherwise `FEASIBLE_WITHIN_SUPPORTED_CAPABILITIES`. A `VERIFIED`
  dimension documenting its boundary (the limits dimension) does not
  divert the outcome — the boundary is honored, not hit.
- **Single-domain evidence rows**: `EvidenceRow` carries exactly one of
  seven admitted `EvidenceDomain` values (seed-17 census, seed-17 smoke,
  reconciliation-derived, snapshot-assessment-derived, seed-2026
  planning, seed-42 demo planning, source tree); plain-string domains
  are refused at construction, and the prohibited set
  {`D5_CORRIDOR`, `D5_CARGOFLOW`, `CANDIDATE11`, `FIXED_SCENARIO`} is
  disjoint from the admitted domains and refused by name. Candidate-11,
  D5-corridor and fixed-scenario evidence therefore cannot enter a
  Random World decision.
- **Observed-world infeasibility is fail-closed**: `observed_infeasible`
  is reachable only through `_observed_infeasible_row`, whose statement
  must contain the verbatim tag *bounded search completed for the whole
  candidate space*; a direct `EvidenceRow(observed_infeasible=True)` is
  refused. Derivation never builds such a row from the retained corpus
  (every recorded random-world search reports `search_truncated true`).
- **Typed P05 prerequisite gate** `p05_prerequisite()` mirroring the
  pipeline refusal of record (`freight_native_network.py:178`,
  `NO_FEASIBLE_SERVICES`): `UNKNOWN_CANDIDATE_COUNT` / `EMPTY_CANDIDATE_SET`
  / `INVALID_CANDIDATE_SET` / `ADMISSIBLE`, judged fail-closed (absent
  evidence is unknown, not zero); the engine never runs P05.
- **Absence is recorded, never fabricated or negated**: `_read_json`
  returns the digested marker for a missing file, invalid JSON or a
  non-object payload, and `_absent_row` records the file digest (when
  bytes exist) with `unobserved=true`; dimensions whose rows are all
  unobserved are `UNKNOWN`.
- **Constants of record re-verified against their own bytes**: the limits
  dimension regex-pins `MAX_RANDOM_TILES = 2048`
  (`supplemental_planning_facts.py`), `capture_tile_limit: Literal[256,
  512, 2048]` (`app/demo_random.py`), `MAX_INDUSTRY_RECORDS = 32`,
  `MAX_SERVICE_PACKAGES = 16`,
  `MAX_PATH_EXPANSIONS = MAX_STATION_PAIRS * 256`, and the
  `NATIVE_CORRIDOR_BOUND: requires 2..47 road tiles` detail string, and
  refuses stale statements when a pinned value drifts.

Tests `tests/test_phase_c_feasibility.py` (sha256 `cf6c094476b8d36b…`,
48 tests, all passing, offline): typed construction rules (prohibited and
string domains, sha256 validity, the infeasible-row constructor and its
verbatim tag), `DimensionAssessment` state invariants, all four P05-gate
branches, all five outcome classes and their precedence (including
unsupported-beats-scope and infeasible-beats-scope), decision-document
shape and refusal of missing/extra dimensions, fixture-aware derivation
under `tmp_path` (all-absent → all-UNKNOWN with unobserved rows,
present-but-unreadable rows carrying real digests, non-`REJECTED`
fusion verdict refused at construction, seed-2026 empty-candidate typed
refusal, month-pacing refusal row never an infeasibility row, limits
pinning + drift refusal), and — skip-safe when the retained evidence is
absent — the real decision of record with pinned dimension states,
domain-clean digest-pinned rows, no infeasibility rows, 19 present
inputs, and two independent in-process and CLI derivations byte-equal.

## 3. Decision of record

`artifacts/experiments/phase-c-feasibility-2026-11-07/`
(`feasibility-decision-report.json` sha256 `67183cf6cd1aa9981a5f8b0009726523e2f69972298aecc4ba46f9a201831fa4`,
`feasibility-decision-report.md` sha256 `edeac9837da38d110a75f07b2116c456141d0c0cdf693843bc05a88c1e855dab`,
derived from 19 present, digest-pinned inputs; two independent
derivations byte-equal):

| Dimension | State |
| --- | --- |
| source_observation_completeness | PARTIAL |
| tile_classification_completeness | PARTIAL |
| source_save_correspondence | PARTIAL |
| industry_cargo_compatibility | VERIFIED |
| terrain_observation_completeness | PARTIAL |
| catchment_station_eligibility | PARTIAL |
| bounded_road_reachability | PARTIAL |
| p08_candidate_generation | PARTIAL |
| p05_planning_readiness | PARTIAL |
| supported_map_search_limits | VERIFIED |

**Outcome: `INCOMPLETE_EVIDENCE`** — 27 evidence rows, every row on exactly
one admitted domain with a full sha256 (`unobserved` nowhere, gating
refusal `EMPTY_CANDIDATE_SET` recorded at P05 from the seed-2026
terminal of record) and **no observed-world infeasibility row anywhere**:
every recorded bounded random-world search was truncated (`search_truncated
true`), so the corpus can support no `INFEASIBLE_FOR_OBSERVED_WORLD` claim
even though both captured seed-2026 candidates were refused and the E141
widened-seal round hit the qualified-month capture gate. The engine's
recommended next action of record: charge the separately scoped operator
decision first — resolve the capture-pacing design (the ticket-03
family, e.g. pausing the world clock during fact capture) under the
roadmap fences, then a fresh gated native capture round. No feasibility
flip without new native evidence.

## 4. Verification ledger (commands actually executed this round)

`REPRODUCE.md` §-addendum carries the exact invocations; results: FD-C-2
suite 48 passed; FD-C-1 suites 83 passed (focused, offline);
`ruff check` and `ruff format --check` clean on the touched paths;
`python -m py_compile` clean on both new files; `git diff --check` clean;
`uvx ty check app/planning/phase_c_feasibility.py
tests/test_phase_c_feasibility.py` reports **1 diagnostic**
(`invalid-argument-type` at the deliberate runtime-validated refusal of a
plain-string evidence domain in the test file — the same never-repaired
class as the repository's pre-existing diagnostics; count, not repaired).
Retained `artifacts/` digests re-verified unchanged after all edits
(`c1cfa970…`, `221ce926…`, `7616f626…`, `079fce64…`, `c9d11d41…`,
`66ed07cc…`, `949a5798…` as pinned above).

## 5. What this round does not claim

No native launch, no AdminPort session, no candidate consumption, no
Gate C signing, no native receipts; no Random World delivery, no
complete-world feasibility verdict, no V1/V2 fusion (the sealed
`SOURCE_SAVE_FUSION REJECTED` is unchanged), no relabeling of any
historical terminal result, no production/OPEX/ROI claims, and no
promotion of any offline result to Native-Verified.
