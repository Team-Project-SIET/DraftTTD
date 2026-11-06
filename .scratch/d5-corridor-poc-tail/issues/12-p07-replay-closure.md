# 12: P07 replay closure (T-021b)

**What to build:** the corridor reporting closure — the reporting/evaluation
layer run fresh on the corridor lineage's terminal evidence, replayed into a
sibling output (never overwriting prior outputs): per-service totals,
charts and operational history with world/seed/plan attribution intact,
OBSERVED native measurements kept distinct from DERIVED aggregates and
CONTROLLED inputs, comparisons carrying distinct seed/config/experiment
identities, and the unmeasured categories staying UNKNOWN under the taxonomy
of record from ticket 11.

**Blocked by:** 11 (Funds-taxonomy decision). **Status:** done 2026-11-06
(the round granted in-session as the frontier instruction "do Ticket 12";
offline reporting only — no staging, no claim, no signature, no launch, no
native run; the item's "no commit/push" wording read against the standing
round governance of the whole tail: the round's book lands as ONE commit,
agent sessions never push — the same pattern every prior round ran under;
recorded here, not stretched).

- [x] Fresh sibling output directory of record produced by the evaluation
      machinery's replay arm — no historical output overwritten, no retread
      of old receipts as new: THREE fresh sibling outputs under
      `artifacts/experiments/p07-replay-d5-corridor-2026-11-06/` —
      `round3-depot-chain/` (D5-F12-DEPOT-3), `route-v1-round6/`
      (D5-CARGOFLOW-2, the selected route's consumed round-6 identity) and
      `route-v2-round7/` (D5-CARGOFLOW-2, the adjudicated v2/corner-swap
      round-7 identity) — each produced by one `analyze-native-attempts`
      invocation into a new output directory; the retained zone re-hash
      proved byte-stable (46,723 historical files before == after; only the
      15 fresh output files added); the outputs land with their own script
      generation, never over any prior output (the command of record is
      booked in REPRODUCE.md)
- [x] The delivered attempts' native receipts replayed — the D5 receipt
      generations are now readable by the analytics arm: the widening
      (`app/experiments/native_attempt_analytics.py`, insert-only; the
      D2/D3/D4 `phase.completed` reader byte-untouched) added the
      generation-agnostic `phase.receipts` reader + the retained
      `funds_chain` join + optional `funds_before`/`funds_after`, `seed`
      (verbatim from `runtime-identity.json`), `finance` (verbatim
      `phase.finance`) and `route_version` (verbatim from the plan policy)
      fields, so the corridor lineage's receipts reach evaluation truly:
      6 receipt rows for the depot chain (costs joining the zero-residual
      funds chain) and 25 receipt rows for each corridor round with the
      funds echo at every exchange instant (round-7 series
      [485217 … 484770], round-6 series the same instants with 484986 at
      the one-unit divergence, the finance close funds 484769 / income 0 /
      delivered 0 copied verbatim into both corridor outputs)
- [x] Attribution asserted: every identity/history row carries its
      world/save/seed/plan provenance (per-attempt prelaunch + result
      digests, `source_world_sha256`, seed 17, plan digest and
      route-version row) — asserted by the round audit
      (`/tmp/opencode/c12_p07_replay_audit.py`, transcript
      `/tmp/opencode/c12_p07_replay_audit_output.txt`): 64/64 PASS, 0
      FAIL — and the failed-planning clause holds by construction: the
      replay consumed only executed, consumed round identities (the
      staged-superseded candidates 3–4 of the corridor line entered no
      report, retaining their own diagnostics in the books, never dressed
      as delivery receipts)
- [x] The OBSERVED/DERIVED/CONTROLLED/UNKNOWN discipline asserted in the
      outputs: every document carries the new ADR-0001 limitation note
      (retained receipt reads OBSERVED, arithmetic DERIVED and labeled,
      retained budgets/ceilings CONTROLLED, everything unmeasured UNKNOWN,
      day/tick figures script-tick instants never steady-state, revenue
      never reported as profit) beside the verbatim status/UNKNOWN notes;
      statuses copied verbatim (`NATIVE_DEPOT_MUTATION_COMPLETE`,
      `NATIVE_CARGOFLOW2_COMPLETE` ×2, verified true), the
      COMPLETE-not-delivered class reported as observed — no report
      printed income or delivery as profit
- [x] Comparisons of record keep distinct identities: the analytics
      machinery's own attempt-identity guard refuses two directories with
      the same `attempt_id` in one invocation by design (round-6 and
      round-7, both `D5-CARGOFLOW-2`, therefore replay as two separate
      arms of record); the audit asserted no pooled comparison statement,
      no comparison artifact, the distinct staged seals
      (`e929d7b2…ec49` vs `9c5f7272…e19257`) and the shared pinned world
      with distinct plan-model digests (v1 `98d055c4…f506ca`, v2
      `e1cafb23…c08b0`); the fixed-demo baseline reports were never
      sourced by the corridor replay and are byte-untouched
- [x] Focused evaluation suites + lint/type gates green:
      `tests/test_native_attempt_analytics.py` 39 passed (five new
      inserts covering the corridor/depot generation readers, the
      UNKNOWN paths, and the ADR-0001 note),
      `tests/test_performance_insights.py` 28 passed, the corridor
      trio (wire 85 + VM 11 + native 46) 142 passed;
      `ruff check` clean; `uvx ty check` on the touched pair = the 3
      pre-existing diagnostics of record (analytics lines 346/348/778 —
      untouched regions, present at HEAD, count unchanged), none
      introduced; `git diff --check` clean; `CONTEXT.md` pin
      `847d710a…984d` intact; ledger row appended (backlog status log +
      E126 + AI_HANDOFF tail); booked with the round's single commit, no
      push
