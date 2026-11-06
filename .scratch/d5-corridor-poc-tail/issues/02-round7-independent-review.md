# 02r7: Round-7 independent review (read-only)

**What to build:** a fresh-context, read-only re-derivation audit of the
staged round-7 candidate-7 (the adjudicated v2-carrying composition after
the E120 widening round) — every binding asserted from disk and the live
production modules against the staged bytes (seal, lineage quartet, the
v2 plan-policy correspondence, the cross-binding invariance of the
binding-shared instrument tables, the one ladder of record, GameScript
byte-correspondence, frozen inventory, D2 closure and dependency
inventory, prerequisite chain, pre-consumption state, budgets, runtime
pins, predecessor integrity) — ending in the verdict `READY-FOR-GATE-C`,
the same per-round method ticket-02's earlier rounds re-derived, re-pinned
to candidate-7 facts and extended with the widening's binding-invariance
axis.

**Blocked by:** 10 (selected-route delivered attempt — its staging round,
E121).

**Status:** reviewed 2026-11-06 — verdict `READY-FOR-GATE-C` (21/21,
exit 0; zero findings, zero reconciliation debt; script + transcript
outside the repo tree)

- [x] One fresh audit script (per-round precedent; never the
      candidate-bound old script) re-derived every binding and wrote its
      full output transcript outside the repo tree
      (`/tmp/opencode/c7_review.py`,
      `/tmp/opencode/c7_review_output.txt`)
- [x] The staged candidate stayed untouched throughout: the seal figure
      re-digested now equals the staging figure of record
      `9c5f727200efa7b896ab2b8016d5183b1f1ee62baff7bfa204eb60bf01e19257`
      (before == after; sidecar byte-equal at audit time, check of
      record); the start and end `git status` showed no review-written
      change inside the repo tree
- [x] Round identity of record: the staged record names
      `d5-corridor-cargoflow2-native-candidate-7` and no consumed
      round-6 identity rides any staged byte; the retained candidate-6
      `PRELAUNCH.json` re-read byte-intact with its own attempt identity
      (nothing relabeled, nothing consumed again)
- [x] Lineage quartet: staged schema, kind, milestone and attempt equal
      the live module pins (`D5_CARGOFLOW2_PRELAUNCH_SCHEMA`, the
      staging kind, the cargo-flow-2 milestone, attempt `D5-CARGOFLOW-2`)
- [x] Fresh seal bound: staged seal `9c5f7272…e19257` == sidecar ==
      digest of record (differs from every predecessor's by
      construction — fresh composition)
- [x] Fix-carry proof: the freeze-pin chain re-derives clean against the
      live tree (every frozen blob re-hashes), the D2 source closure and
      the dependency inventory re-verify against the module's
      `CARGOFLOW2_CLOSURE_ROOT`, and `CONTEXT.md` remained at the
      authority-manifest pin `847d710a…984d` through the round
- [x] Staged↔live byte-equality: the staged GameScript identity
      (`workspace/game/<save-identity>/info.nut` + `main.nut`) byte-checks
      the live re-derived save-restore composition
      `staged_cargoflow2_composition()` — the save's stored GameScript
      identity handling and the protocol-11 delivery handler of the
      attempt's own package directory, no frozen package byte drifting
      for the attempt's sake
- [x] The v2-carrying derivation (the widening's own axis): the staged
      plan policy binds `route_version = 2` beside
      `schedule_version = 1`; the staged plan-model digest
      `e1cafb23…c08b0` equals binding 2's own live guarded factory
      derivation (`cargoflow2_pipeline_plan(2)` ==
      `corridor_cargoflow2.cargoflow2_plan(binding=…)`); the staged
      schedule is the one ladder of record (`cargoflow2_schedule()` ==
      the wire module's `cargoflow2_schedule_rows(binding 2)`), staged
      schedule digest `5c0998f2…bf2d` unchanged
- [x] Whole-policy correspondence: the staged plan policy equals the
      full live `cargoflow2_plan_policy(2)` field-for-field (zero diff)
      — the round-6 D1-class check re-pinned to the v2 composition
- [x] Binding-invariance extension (the E120 promise, now evidenced):
      the five binding-shared instrument tables — the hypothesis record,
      the funds-model fence, the ladder grid, the world pins and the
      read-only fence — are byte-equal across both admitted bindings'
      live derivations (`cargoflow2_plan_policy(1)` vs `…(2)`); the
      metadata-level expected-readback policy equals its live
      derivation; the budget contract of record (1 launch / 1
      connection / 0 retries / 32 requests) equals `cargoflow2_budgets()`
- [x] Prerequisite chain: the prerequisite binding is the pinned depot
      attempt `D5-F12-DEPOT-3` with after-save pin `183b2027…6ea6`, and
      the staged `source.sav` re-verifies on disk against the pin
- [x] Pre-consumption state: the candidate root is exactly the staged 4
      entries (`PRELAUNCH.json`, `PRELAUNCH.sha256`,
      `graphics-identity.json`, `isolated`) with no CLAIM,
      AUTHORIZATION, LAUNCH-CONSUMED or result marker anywhere, and a
      recursive workspace scan finds no claim-or-signature artifact
- [x] Runtime pins: the pinned binary re-digests to `276d5b69…904c` from
      the harness pin of record; the production preflight gate re-runs
      clean (`PREFLIGHT PASS`, exit 0, read-only)
- [x] Audit-side honesty of record: the first execution of the fresh
      script aborted 10/21 with exit 1 on an audit-side mis-placement of
      the expected-readback axis (asserted inside the plan-policy
      comparison, while the staged record carries `expected_readback` at
      the metadata level beside the budgets); nothing repo-side was
      touched by the abort and the script lives outside the repo tree;
      the corrected script re-ran the full table end-to-end to 21/21.
      The first-pass transcript was overwritten in place by the
      corrected re-run (the script writes one output path), so it is not
      retained — recorded here honestly rather than re-created; the
      retained transcript of record is the passing re-run
- [x] Review row appended to the PoC backlog status log + evidence
      (E122) + AI_HANDOFF tail; `git diff --check` clean; `CONTEXT.md`
      authority pin intact; committed once with the formed ticket; no
      push ever
