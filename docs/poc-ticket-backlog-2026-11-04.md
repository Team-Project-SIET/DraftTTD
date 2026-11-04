# Full-Scope Functional PoC — ticket backlog (2026-11-04)

Round record. Objective: execute the approved Full-Scope Functional PoC
roadmap as sequentially worked tickets, in this repository's own task
convention (a standalone dated document under `docs/`; `TASKS.md`,
`EVIDENCE_INDEX.md` and `CONTEXT.md` are not restructured by this file —
a lookup row is appended to `EVIDENCE_INDEX.md` only when a round closes,
which is this repository's precedent for every round).

## Authority and reconciliation (2026-11-04)

- Design authority for the next native round, after operator review, is
  [d5-cargoflow-delivery-design-2026-11-04.md](d5-cargoflow-delivery-design-2026-11-04.md)
  (fresh road-vehicle delivery identity `D5-CARGOFLOW-2`, wire protocol
  id 11, package `d5_cargoflow2_package`, pipeline
  `proof/corridor_cargoflow2_native.py`). Its §1.1 discloses that no
  `E100` record exists in this repository (git history ends at
  `81ce350 E99`); nothing is imported from the absent label.
- Evidence base: E62–E99 as recorded in `EVIDENCE_INDEX.md` (latest
  retained round: E99, `D5-CARGOFLOW-1`, candidate consumed once,
  terminal halt `PHASE_HALTED_PREFIX_PRESERVED` at `sample-07` after
  seven verified READY samples, verdict `DISPATCH_STOCKPILE_STATIC`).
- Terminal predecessors, never re-opened: attempt-6, D5-FREIGHT-6
  (halt `transit-00`, E97), D5-CARGOFLOW-1 (halt `sample-07`, E99).
  The two fence defects E99 exposed are the subject of the design's
  §4 fixes (modeled funds trajectory; sampling-instant alignment).
  Protocols 8/9/10 are frozen; no frozen byte is edited.
- Build prerequisite of record: the `D5-F12-DEPOT-3` world-pin
  (after-save sha256
  `183b20273a54ebe1a2cd9306145a9ea820bbd6114b1608c42079b4e1b1efe6a6`,
  world-pin version 3) plus its verified reload chain, staged in
  `app/simulation/openttd/proof/corridor_freight_v2_native.py`.
- Repository state at backlog creation: branch `miles/fright-delivery`,
  HEAD `956c14f` (`design-d5-cargoflow`), only dirty file the design
  record itself. No native execution, staging, review, signing or
  launch has happened for `D5-CARGOFLOW-2`.

## Dependency graph

```
T-001 offline implementation of D5-CARGOFLOW-2
  └─ T-002 operator staging approval → prepare/PRELAUNCH PASS   (GATE)
       └─ T-003 independent read-only candidate review           (GATE)
            └─ T-004 Gate C Option-1 signing                     (GATE)
                 └─ T-005 launch approval → ONE launch → replay  (GATE)
                      └─ T-006 verdict reconciliation
                           ├─ halt class → T-007 capture fix design round (new)
                           └─ delivered class → T-020 M8 block
T-020 M8: ≥2 executable routes, P05 selection, native landing
  └─ T-021 P07 closed loop + funds-taxonomy decision
       └─ T-022 PoC completion declaration + round-close E-row
Post-PoC (P2 backlog, separate approvals): T-030 fleet/capacity,
T-031 matched A/B, T-032 five-year, T-033 OPEX/ROI consolidation,
T-034 full regression 15.3.
```

## Execution constraints (per `CONTEXT.md`, `AGENTS.md`, design §6)

Constraints binding every ticket: historical evidence and terminal
candidate identities are immutable; no relaunches; no verification
weakening; the `CONTEXT.md` authority pin is preserved; no secrets or
`.perch` access; no git commit/push/reset or destructive operations;
no tests are staged or represented as native proof. Staging, independent
review, Gate C signing and launch are each a separate explicit operator
approval obtained in-session before that step runs; otherwise the round
stops at that gate. Only `.venv/bin/python` from the repository root;
lint/type gates per `REPRODUCE.md`.

## Tickets

### T-001 — D5-CARGOFLOW-2 offline implementation

- **Status:** in progress.
- **Objective and scope:** implement, fully offline, exactly what
  design §5 prescribes: the protocol-11 wire contract
  `app/simulation/openttd/corridor_cargoflow2.py`, the additively-shipped
  composed package `app/simulation/openttd/d5_cargoflow2_package/`, the
  staging pipeline `app/simulation/openttd/proof/corridor_cargoflow2_native.py`
  (v3-prerequisite chain, prepare/preflight/verify-only-offline), and the
  focused suites `tests/test_corridor_cargoflow2.py`,
  `tests/test_corridor_cargoflow2_native.py` and their companion shapes.
- **Dependencies:** design record accepted by operator (this file only;
  no code dependency).
- **Acceptance criteria:** every constant, schedule, funds model and
  outcome clause matches the design's pinned values (cargo 1; tiles
  45748/50862/45487; sids 0/2; industries 0/1; funds 489650; purchase
  4429; capacity 20; loan 100000; rate 2; 25/station/month terminal rate
  with 25/month fee; ladder offsets 0..55 step 5; 25 exchanges; request
  budget 32; byte bounds per §5/§8). Funds fence is the modeled §4.3
  trajectory with the exact Fract carry arithmetic, halting
  `CARGOFLOW2_FUNDS_DIVERGED` on deviation. §5.5 outcome typing
  verbatim. §7 seven acceptance conditions expressible. No native
  execution of any kind.
- **Required evidence:** offline gate outputs recorded in the ticket
  status log below (suite counts, lint/type results, byte audits).
- **Validation procedure:** `.venv/bin/python -m pytest` focused suites
  per `REPRODUCE.md`; `ruff check`; `uvx ty`; `git diff --check`;
  preflight/verify must run offline-read-only only. The E70-recorded
  baseline tolerance of five pre-existing `ty` diagnostics
  (`bf6cc0b`) remains the floor, no new diagnostics.
- **Risks and approvals:** wire byte budgets (25 exchanges) must be
  audited like the E68 round did; funds model exactness is checked by a
  dedicated suite pair. No operator approval is consumed: staging is
  the next gate and never runs on this ticket.

### T-002 — Operator staging gate: `D5-CARGOFLOW-2` candidate

- **Status:** pending (GATE; operator approval required).
- **Objective and scope:** on operator approval only, run the pipeline's
  offline `prepare` to stage the candidate, then one read-only
  `preflight` (`PRELAUNCH PASS` expected) and `verify`
  (`AUTHORIZATION_UNVERIFIED`/`CLAIM_ABSENT` exit 1 expected).
- **Dependencies:** T-001 complete.
- **Acceptance criteria:** candidate of record under
  `artifacts/experiments/d5-corridor-cargoflow2-native-candidate-1`;
  0 manifest mismatches; prerequisite bound to the pinned after-save
  `183b2027…efe6a6`; no consumption of any terminal identity.
- **Required evidence:** `PRELAUNCH.json`/`PRELAUNCH.sha256` unchanged
  after subsequent read-only steps; ticket status log with output lines.
- **Validation procedure:** pipeline `prepare`/`preflight`/`verify`
  invocations of record from `REPRODUCE.md`.
- **Risks and approvals:** the numeric attempt identity is consumed on
  launch only, but staging itself is an approval event; a stale staged
  candidate after post-approval source edits is re-staged only per the
  E53/E54 and E98/E99 precedent (fresh operator approval).

### T-003 — Independent read-only review of the staged candidate

- **Status:** pending (GATE; separate operator-approved reviewer, never
  the author session).
- **Objective and scope:** fresh-context audit of the staged bytes
  (seals, identity, world/prerequisite binding, schedule, funds model,
  replay inventory) with the E99/§12-style record.
- **Dependencies:** T-002.
- **Acceptance criteria:** verdict `READY-FOR-GATE-C` with zero
  reconciliation debt; any finding reopens offline implementation.
- **Required evidence:** review record row in this file and, on round
  close, the E-row.
- **Validation procedure:** independent reviewer's own re-derivation
  script and manual audit; author session may not self-certify.
- **Risks and approvals:** operator chooses reviewer and grants the
  approval; review is read-only.

### T-004 — Gate C Option-1 signing

- **Status:** pending (GATE; operator signing).
- **Objective and scope:** operator signs the authorization payload
  binding `D5-CARGOFLOW-2` to the freshly staged candidate; no
  authorization reuse across candidates.
- **Dependencies:** T-003.
- **Acceptance criteria:** signed payload digest recorded; lifecycle
  advances past `CLAIM_ABSENT` only after signing.
- **Required evidence:** signed digest + appointment in status log.
- **Validation procedure:** pipeline `verify` exits 0 post-signing.
- **Risks and approvals:** single approval; fresh identity only.

### T-005 — Launch approval, one launch, read-only replay

- **Status:** pending (GATE; separate explicit operator approval).
- **Objective and scope:** exactly one native launch of the signed
  candidate at the pinned binary/OpenGFX versions; after exit, the
  read-only replay verifier re-derives the receipts; cleanup certified.
- **Dependencies:** T-004.
- **Acceptance criteria:** `D5-CARGOFLOW-2` outcome class per §5.5 as
  preserved by replay; funds ledger reconciles (§4.3 model, including
  the modeled monthly 192 charge); no retry on halt; consumed
  identity never relaunched.
- **Required evidence:** launch receipts, replay verdict, retained
  candidate artifacts (transfer-only discipline respected).
- **Validation procedure:** pipeline's in-place replay + snapshot
  inspection of record.
- **Risks and approvals:** one attempt; WINDOW_EXHAUSTED overshoots and
  `ARRIVE_TIMEOUT` are terminal, not failures to relaunch.

### T-006 — Delivery verdict reconciliation

- **Status:** pending (depends on T-005).
- **Objective and scope:** classify the outcome against §7; if any of
  the seven acceptance conditions is unmet, open a new capture-fix
  design round (fresh identity, design record first) — never relabel,
  never re-open a terminal attempt. If the delivery class is achieved,
  open the M8 block.
- **Dependencies:** T-005.
- **Acceptance criteria:** verdict written here and, at round close, an
  `EVIDENCE_INDEX.md` row; M8 block opened only on delivery class.
- **Required evidence:** verdict paragraph with receipt citations.
- **Validation procedure:** replay re-check; cross-check of §7 list.
- **Risks and approvals:** verdict text is subject to operator review;
  new design rounds each need their own approvals.

### T-020 — M8 route selection demonstrated on the corridor

- **Status:** pending, blocked by T-006 (delivery class).
- **Objective and scope:** ≥2 natively executable route candidates on
  the corridor world; P05 selects among them under its operating
  boundedness (bounded simulation, ≤16 relationships, ≤8 services);
  the selected route lands in a delivered native attempt (fresh
  identity, own gate ladder).
- **Dependencies:** T-006.
- **Acceptance criteria:** optimizer-selected route member of the
  delivered attempt; competing executable route natively proven; the
  E36 finding "no competing executable route" closed by record.
- **Required evidence:** selection artifact + delivered receipts +
  M8 design/review records.
- **Validation procedure:** focused suites + replay + round close row.
- **Risks and approvals:** each native attempt its own gated round.

### T-021 — P07 closed loop on native receipts + funds taxonomy

- **Status:** pending, blocked by T-020.
- **Objective and scope:** operator decides the funds taxonomy
  (running-cost category question recorded since E50);
  P07 replays phases' native receipts into fresh sibling output.
- **Dependencies:** T-020.
- **Acceptance criteria:** `evaluation.json`/`results.md`/
  `operational-history.json` replay-verified with attribution; OPEX =
  observed native cash deltas only; DERIVED segregated; unmeasured
  categories UNKNOWN; revenue ≠ profit stated.
- **Required evidence:** fresh P07 output + taxonomy (ADR) record.
- **Validation procedure:** P07 offline gate of record.
- **Risks and approvals:** taxonomy decision is an operator decision.

### T-022 — PoC completion declaration and round close

- **Status:** pending, blocked by T-021.
- **Objective and scope:** assemble the §7-class evidence set into the
  PoC completion record (delivered cycle + M8 selection + P07 replay
  on the corridor world), then the round-close ledger append.
- **Dependencies:** T-021.
- **Acceptance criteria:** full delivery receipt, ≥2 executable routes
  with optimizer selection, P07 replay-verified reports, offline
  gates exit 0, manifests intact, terminal identities untouched.
- **Required evidence:** completion record + E-row.
- **Validation procedure:** REPRODUCE commands of record.
- **Risks and approvals:** declaration is operator-reviewed.

### Post-PoC backlog (P2, separately approved efforts)

T-030 fleet/capacity native exercise (purchase/dispatch/unpause, 15.3,
canonical correspondence); T-031 matched A/B (separately authorized
arms, descriptive comparisons); T-032 five-year experiment (its own
finalization contract; per-year OPEX/ROI derived from observed
accounting); T-033 consolidated OPEX/ROI with provenance labels; T-034
full regression over the 15.3 qualification set. These are research
readiness, outside this round's PoC definition.

## Status log

- 2026-11-04 — backlog created; reconciliation recorded; T-001
  started (offline implementation, gates untouched).
- 2026-11-04 — T-001 core implementation wired and gated:
  - ``tests/test_corridor_cargoflow2.py``: 76/76 pytest green (wire
    contract, funds model of record, halt/verdict ladder, stub world,
    §5.5 outcome typing, E99 hypothesis pins).
  - ``ruff`` clean on both touched paths; ``uvx ty`` clean on both
    touched paths (and on ``app/simulation/openttd/corridor_cargoflow2.py``
    alone); ``git diff --check`` clean; the E70 baseline
    (``bf6cc0b``) floor untouched.
  - ty authenticity note: the module initially produced a Never
    cascade from any importer as far back as ty 0.0.55 — root cause
    was the §4 guard's ``max(CARGOFLOW2_MONTH_BOUNDARY_DAYS)`` term
    (a derived tuple no ty 0.0.x folds), which left the guard-human
    module-level ``raise`` statically reachable so ty inferred every
    later top-level definition unreachable. Fixed inside the ticket
    without weakening: the 11 boundary days are now a pinned literal
    guard term (protocol-10's ``CARGOFLOW_SAMPLE_OFFSETS`` style) and a
    new ``_assert_cargoflow2_calendar()`` cross-checks the derived
    1950 month starts against the pins at import (runtime-identical
    refusal surface, strictly more pins than the single max check).
    The full-tree ty 509-diagnostic drift (0.0.97 + unrelated WIP)
    stays out of scope, recorded honestly.
  - Funds fence narrowed by construction: the fence asserts the
    success-frame instant/income/raw facts the contract's own
    ``coherent()`` validator already refuses to omit, so the fence is
    typed on ints without any runtime change; tests for the ladder
    day arithmetic and funds stairway of record (485221 → … → 484774,
    two whole 192 monthly fees at flow-06/flow-11) pin the walked
    vector on the stub fee engine.
  - Full offline VM run green: ``run_probe_vm()`` 25/25 exchanges,
    funds fence zero-residual, verdict
    ``CARGOFLOW2_QUEUE_NEVER_FILLED``, sampled months
    [[1950,1],[1950,2],[1950,3]], finance funds 484774.
  - Byte audit of record: widest real request 315 B ≤ 512;
    widest real reply 1371 B ≤ 1400 (synthetic byte audit uses
    ``exclude_none=True`` per the handler's null-free frames).
- 2026-11-04 — T-001 handler VM suite (#2) added and gated:
  - ``tests/test_corridor_cargoflow2.py``: 76/76 green (unchanged).
  - ``tests/test_corridor_cargoflow2_vm.py``: 11/11 pytest green —
    the real handler of record inside the real Squirrel VM: exact
    25-exchange ladder of record (green run_probe_vm, honest
    ``CARGOFLOW2_QUEUE_NEVER_FILLED`` verdict, 25 receipts,
    ``CARGOFLOW2_COMPLETE``), on-stage/plan-latch OUT_OF_ORDER and
    halt discipline, company/pin/pause refusal vocabulary
    (INVALID_COMPANY ×2 stages, INVALID_SITE, STALE_ADMISSION,
    PAUSED with zero funds), CLOCK_STALLED honest echoes
    (anchor 712228/tick 40/day 712229 on ``ticks_freeze``),
    WINDOW_EXHAUSTED overshoot (day 712240) and dead-clock full
    2048-sample budget (tick 2088, day 712228), the LATCH_OVERFLOW
    refusal (9-edge stub bouncing through flow-01's 5-day window;
    overflow refuses, never truncates), the ARRIVE_TIMEOUT day
    authority (deadline 712234 > 712233 without a witness) and the
    dead-clock tick ceiling, the D5_NATIVE_FACT throw marker
    (site-00 ticks −1) and the CONTROLLED_STOP throw through the
    catch-all strip (flow-01 with no echo leaks), the 32-request
    budget with the 33rd drop + duplicate-id re-entry drop, and the
    foreign-shape drop matrix (protocol/op/plan-hex/quote+cap
    purchase echoes/offset scale/bootstrap types/IdShape/degenerate
    pins). Only shape/dup corrections needed against the first
    runtime read (used-id re-entry, purchase quote/cap echoes); the
    planned exact echo figures all held.
  - ``ruff`` clean on all three touched paths; ``uvx ty`` clean on
    the #1+#2 pair and on ``corridor_cargoflow2.py`` alone;
    ``git diff --check`` clean; CONTEXT.md sha pin
    ``36648f9c2fee4106…`` intact.
- 2026-11-04 — T-001 native staging/replay suite (#3) added and gated:
  - ``tests/test_corridor_cargoflow2_native.py``: 37/37 pytest green —
    plan-typing refusal (four crossed plan models + dict), the pinned
    25-exchange ladder of record and the full exchange-timeout table
    (instant/request ⋅ watch/margin ⋅ window, three foreign refusals), the
    cross-native-session guard (a delivery frame refused by census/survey/
    probe-10 sessions; a probe frame refused by the delivery session),
    staged lineage binding (schema/attempt/milestone/kind, budgets,
    command "purchase", prerequisite block, read-only surface,
    ladder grid, cross-guard, bootstrap), foreign consumed-name absence in
    staged bytes, depot prerequisite pin (+ two wrong-path refusals,
    attempt-scoped re-label), staged source save, frozen composition
    bridge (NetworkFreightProof extends D5CargoFlow2Proof), authorization
    payload digest with no claim, funds-model founding gate, preflight
    happy rehearsal plus three tamper matrices (seal/lineage/grid-world),
    E99 hypothesis rebind (+ receipts cross-check) and the absent-evidence
    state, expected-readback story, exchange persistence + the stale/
    malformed refusals + the 512/1400 bounds, frame parser (+junk refusal),
    the §5.3 day-authority matrix, verify fail-closed (unconsumed,
    claim-mismatch, forced label, stray file, unknown schema), identity
    matrix (plan pair, crossed models, prerequisite/world/policy drifts),
    exit-status matrix (zero only with ``state_changed`` True), the
    synthetic fully-consumed attempt verifying
    ``CARGOFLOW2_COMPLETION_VERIFIED`` (25 retained exchanges grafted to
    the real staged seal via ``built_ladder`` + real-seal request table;
    anchor 712228, sampled months [[1950,1],[1950,2],[1950,3]],
    DELIVERY_VERIFIED) plus its three tamper fail-closes, and the
    wire-to-Nut pin binding (``cargoflow2_planned`` 4-column rows and the
    25 pin LHS values bound to the contract constants, including the
    deadline/authority sums).
  - Runtime corrections against the first read only: ``torch`` slip,
    ``(.)` naming, operator-precedence parens, renamed
    ``cargoflow2_exchange``, day-escape offset 61 (60 still fits), a 4th
    capture group in the NUT status regex, ``[a-z-]+`` id class for
    ``order-read-00``, and the honest ``wait_pickup`` head (0 at flow-00;
    the queue rises at flow-01). The planned echo figures held.
  - Module typing discovered honestly: the staging module alone carried
    59 ty diagnostics; 58 were one ``base: dict[str, Any]`` annotation gap
    in ``_cargoflow2_exchange_request`` (type-level annotation only, no
    behavior change) — fixed inside the ticket. The remaining 1 is the
    ``connect`` LSP warning, the exact shape the tracked protocol-10
    module already carries (``corridor_cargoflow_native.py:975``);
    recorded as inherited precedent, not added by this round.
  - Gates: the #1+#2+#3 trio 124/124 pytest green; ``ruff`` clean on all
    touched paths; ``ty`` clean on the test file alone (pair prints the
    single inherited connect diagnostic); ``git diff --check`` clean;
    CONTEXT.md sha pin ``36648f9c2fee4106…`` intact.
