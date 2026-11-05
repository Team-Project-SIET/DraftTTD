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
                           ├─ halt class → read-only root-cause diagnosis
                           │   ├─ R1: T-007 SiteOp road-type fix (executed
                           │   │   offline 2026-11-05, E106)
                           │   │   └─ fresh candidate cycle (round-2 ladder):
                           │   │       T-002 → T-003 → T-004 → T-005 → T-006
                           │   │       (same gates, fresh candidate identity
                           │   │       + seal; on halt, repeat diagnosis →
                           │   │       fix → fresh cycle; never relabel,
                           │   │       never relaunch a consumed attempt)
                           │   └─ R2: T-008 read-only diagnosis (complete
                           │       2026-11-05, E111 — census-gate scale
                           │       inversion confirmed, corrective direction
                           │       documented)
                           │       └─ future corrective ticket (pending;
                           │           opened only after operator review;
                           │           no fix, no staging invented here)
                           └─ delivered class → T-020 M8 block
T-020 M8: ≥2 executable routes, P05 selection, native landing
  └─ T-021 P07 closed loop + funds-taxonomy decision
       └─ T-022 PoC completion declaration + round-close E-row
Post-PoC (P2 backlog, separate approvals): T-030 fleet/capacity,
T-031 matched A/B, T-032 five-year, T-033 OPEX/ROI consolidation,
T-034 full regression 15.3.
```

Round ledger (authoritative per-ticket status stays in the ticket
entries and status log below; every ID and historical record preserved):

- **T-001** — complete 2026-11-04 (offline implementation; no gate
  consumed).
- **Round 1** (candidate-1, seal `c7a1c5d5…333b`): T-002 gates passed
  2026-11-04; T-003 42/42 re-derivation checks PASS, verdict
  READY-FOR-GATE-C 2026-11-04; T-004 signed 2026-11-04; T-005 ONE
  launch 2026-11-05 → terminal halt `INVALID_SITE` at `site-00`;
  T-006 reconciled **not achieved** 2026-11-05 → halt class.
- **T-007** — executed offline 2026-11-05 under explicit operator
  approval (E106): the completed root-cause fix of the T-006/E105
  diagnosis — `GSRoad.SetCurrentRoadType(GSRoad.ROADTYPE_ROAD)` before
  the re-pin join inside `SiteOp` of the protocol-11 package. Consumed
  candidate-1 stays sealed terminal evidence; no restaging on this
  ticket.
- **Round 2** (candidate-2, seal `f991a440…55d4e`, the T-007 fix
  cycle): **T-002 round 2 staged 2026-11-05 (E107) — complete**;
  **T-003 round 2 reviewed 2026-11-05 (E108, 45/45 re-derivation
  checks PASS, verdict READY-FOR-GATE-C) — the current gate of
  record**. The fresh cycle continues T-004 → T-005 → T-006, each its
  own explicit operator approval; nothing scheduled.
  **Round-2 tail of record:** T-004 round 2 signed 2026-11-05 (E109);
  **T-005 round 2 executed 2026-11-05 (E110): ONE launch — `site-00`
  `READY` live (the T-007 fix measured live-true), terminal halt
  `ENGINE_PIN_MISMATCH` at `engine-00`, replay reconciles exactly,
  candidate-2 consumed — nothing relabeled, nothing relaunched.**
  **T-008 read-only diagnosis completed 2026-11-05 (E111): root cause
  = census-gate scale inversion (the `(raw >> 8) == 421` join is
  unsatisfiable because the script surface already returns the display
  figure); corrective direction documented; no code changed.** Next:
  the future corrective ticket, opened only by operator review;
  nothing scheduled.
- **T-009** — executed offline 2026-11-05 under explicit operator
  approval (gate DG-1 of `docs/roadmap-and-scope-2026-11-05.md`): the
  completed corrective fix of the T-008/E111 diagnosis — the census
  display figure compared to its pin with no second shift, both Python
  mirrors, the 8.8 funds arithmetic of record preserved exactly
  (display/365 reconstruction), the full E111 regression-lock matrix
  and the marked design-§4 correction bullet. Suites 88 + 38 passed,
  ruff/ty "All checks passed!", `git diff --check` clean; the fresh
  candidate round 3 (staging → review → Gate C → one launch) remains
  the only native validation path; the consumed candidates 1–2 stay
  untouched.
- **T-008–T-019 are undefined, not reserved**: no ticket was ever
  assigned to these IDs, at backlog creation or since. The ladder was
  numbered T-001–T-007 and jumps to the pre-existing T-020/T-021/T-022
  M8/completion block, then the P2 backlog T-030+. **2026-11-05
  update:** the first T-008 assignment happened on 2026-11-05 under
  explicit operator task direction — the R2 `ENGINE_PIN_MISMATCH`
  read-only diagnosis ticket created below — and the first T-009
  assignment followed the same day, the corrective fix of record
  above. T-010–T-019 remain undefined.

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

- **Status:** round-2 gates passed 2026-11-05 under explicit operator
  approval (the T-007 fix cycle, fresh candidate identity, ONE
  `prepare`); first-round gates passed 2026-11-04 under explicit
  operator approval
  (staging approval consumed; prelaunch seal of record
  `c7a1c5d5…333b` == sidecar unchanged after every read-only step;
  pre-auth `verify` intentionally exit 1). Awaiting T-003 independent
  review gate on the round-2 candidate.
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

- **Status:** round-2 review complete 2026-11-05 under explicit
  operator approval — 45/45 re-derivation checks PASS, verdict
  **READY-FOR-GATE-C** for
  `d5-corridor-cargoflow2-native-candidate-2` / seal `f991a440…55d4e`
  (fix-carry verified byte-level: staged main digest `2c7f6b09…`
  contains the T-007 `SiteOp` fix, single occurrence, before the
  re-pin join; source↔staged main byte-equal; pipeline preflight and
  pre-auth verify re-executed read-only in-session). Round-1 review
  complete 2026-11-04 — 42/42 re-derivation checks PASS exit 0, verdict
  **READY-FOR-GATE-C** on candidate-1, zero reconciliation debt.
  Round-2 script of record
  `/tmp/opencode/t003_r2_review_cargoflow2_c2.py`
  (output `/tmp/opencode/t003_r2_output.txt`); zero staged defects,
  zero staging rewrites, candidate-1 and candidate-2 bytes untouched
  (both seals re-digested unchanged post-review). Awaiting T-004
  Gate C signing gate on the round-2 candidate.
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

- **Status:** round-2 signed 2026-11-05 under explicit operator
  approval — ONE signing operation (fresh seed-derived key asserted
  pre-write against the pinned operator anchor; production signer
  only); payload digest `3f489b18…4ee55788` (== production
  `staged_cargoflow2_authorization_payload_digest`),
  `AUTHORIZATION.json` record digest `45820767…7eeb9`, operator
  identity unchanged `sha256-ed25519-public-key:cbb63ff5…40c614`;
  seal `f991a440…55d4e` byte-equal after the write; post-write
  preflight PASS; lifecycle claim still `CLAIM_ABSENT` (minted only
  by the launch). Seed env unset + empty-verified. Round-1 signed
  2026-11-04 (candidate-1; payload `3d787802…61661`, record
  `427bbdb4…793cdc`). Awaiting T-005 launch gate on candidate-2.
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

- **Status:** round-2 executed 2026-11-05 under explicit operator
  approval — ONE launch of candidate-2 at the pinned OpenTTD 15.3
  binary + OpenGFX-8.0 archive; run of record `RC=1`, status
  `PHASE_HALTED_PREFIX_PRESERVED`, `preflight PASS`,
  `native_launches=1` (== budget), `connections=1`, `requests=2`,
  `verified=false`. **The E106/T-007 fix measured live-true:** site-00
  progressed to `READY` (response `READY` for depot `45487`, pickup
  `45748`, delivery `50862`, day 712228 tick 14, funds 489650, income
  0; stderr decisive line `D5_CARGOFLOW2 site-00 READY`; round-1's
  `INVALID_SITE` did not recur), the site op executed live
  (`state_changed=true`). Terminal halt class of record:
  `ENGINE_PIN_MISMATCH` at the staged exchange `engine-00` (response
  op `engine`, requested pin `engine=123`, cost 0, funds 489650, plan
  == seal `f991a440…55d4e`, protocol 11; stderr decisive line
  `D5_CARGOFLOW2 engine-00 ENGINE_PIN_MISMATCH`; `HALTED_BEFORE_
  MUTATION`; 23 later steps pending — the halt is terminal and the
  identity live-effective is unmeasured this round). Read-only replay
  of record: `verification PHASE_HALTED_EVIDENCE_PRESERVED`, failed
  exchange `engine-00` / `ENGINE_PIN_MISMATCH` / world_state
  `HALTED_BEFORE_MUTATION`, `RC=1` — verdict reconciles the run
  verdict exactly; nothing relabeled, nothing retried, nothing
  relaunched, no diagnostic round scheduled. Launch bindings of
  record: `LAUNCH-CONSUMED.json` binds authorization record
  `45820767…7eeb9`, seal `f991a440…55d4e`, operator identity
  unchanged `cbb63ff5…40c614`; `CLAIM.json`
  `launches_allowed=1 / retries=0 / consumed=true`; `native_launches=
  1` == budget; 1 connection; certified cleanup
  `reaped / sockets_closed / workspace_disposed / credential_removed`,
  `cleanup_error=[]`, `remaining_processes=[]`, `returncode=0`
  (pid 181344), listener closed, reservation released, no openttd
  process after, ports 60131/59411 free. Manifest 19/19 OK, 0
  non-OK; seal byte-equal + sidecar after the run; candidate root =
  20 files + empty `isolated/` shell; after-diagnostic save retained.
  `git diff --check` clean; CONTEXT pin `36648f9c2fee4106` intact.
  Candidate-2 is now consumed terminal evidence — never relaunched,
  never reconnected, never re-staged without a fresh round identity.
  Round-1 (candidate-1, halted `INVALID_SITE` at site-00, bindings
  `427bbdb4…793cdc` / `c7a1c5d5…333b`) remains retained history.
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

- **Status:** reconciled 2026-11-05 — the T-005 outcome class per §7
  is **not achieved** (halt at exchange 0; zero of the seven
  acceptance conditions observed), so per this ticket's rule a new
  capture-fix design round opens; the consumed attempt stays final.
  The read-only root-cause diagnosis of record (this round): the
  `INVALID_SITE` halt is a package-side GSRoad API sequencing defect —
  the protocol-11 `SiteOp` re-pin join
  (`d5_cargoflow2_package/main.nut`:389–402) calls
  `GSRoad.IsRoadDepotTile(this.depot_tile)` while the fresh script
  instance never calls `GSRoad.SetCurrentRoadType(GSRoad.ROADTYPE_ROAD)`
  (0 occurrences in the failing package vs ≥1 in every worked
  predecessor: freight v1, freight v2 `Handle` line 1694,
  depot-mutation 173, depot-recheck 242, extension 1016); on the
  pinned OpenTTD 15.3 the per-instance default is
  `ScriptStorage.road_type = INVALID_ROADTYPE` with
  `ScriptRoad::IsRoadDepotTile` early-returning false when the current
  road type is unavailable — the seventh join member fails
  deterministically, world-independent. No identity failed validation:
  on the identical launched world bytes (`183b2027…6a6`) the
  same-session precedent `d5-corridor-freight-native-candidate-5`
  measured every identity fact live-true (`sid0=0` `truck0=true`,
  `sid1=2` `truck1=true`, `pickup_industry=0` count 1,
  `delivery_industry=1` count 1, `depot_ok=true` `depot_edge=true`,
  `funds=489650` == pinned close-out, status `READY`); refusal path =
  normal `SiteOp` return (no `D5_CARGOFLOW2_THROW` in stderr, no
  observation fields, request echoes byte-equal the baked pins).
  **Safest next ticket (T-007):** single-package GSRoad sequencing
  fix (Set-before-Get inside `SiteOp`, family idiom), then a full
  fresh candidate cycle (staging → review → Gate C → ONE launch)
  under the same gate discipline; candidate-1 stays sealed consumed;
  nothing scheduled without operator approval.
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

### T-007 — Fix the D5-CARGOFLOW-2 `SiteOp` road-type initialization defect

- **Status:** executed 2026-11-05 offline under explicit operator
  approval (code fix + focused offline validation only; no staging, no
  signing, no candidate creation, no OpenTTD launch, no historical
  evidence modification, no Git mutations). The fix of record: in
  `d5_cargoflow2_package/main.nut` `SiteOp` (>387), the five-line
  comment of the T-006 root cause plus
  `GSRoad.SetCurrentRoadType(GSRoad.ROADTYPE_ROAD)` now precedes the
  `/* Re-pin gate: */` join (the freight v2 `Handle`:1694 family
  idiom); no other package byte changed (single GSRoad consumer of
  record: the `IsRoadDepotTile` join member; the 25-row
  `cargoflow2_planned` pin table is untouched). The VM stub world
  (`tests/test_corridor_cargoflow2.py`) gained the 15.3 fail-close
  model on the depot-mutation E72 idiom (`::cur_road_type <- 63`
  default; `IsRoadTypeAvailable`/`SetCurrentRoadType`/
  `GetCurrentRoadType`/fail-close `IsRoadDepotTile`), making the VM
  suite a true regression lock: the pre-fix package cannot pass it.
  **Offline validation of record:** `tests/test_corridor_cargoflow2_vm.py`
  + `tests/test_corridor_cargoflow2.py` → **87 passed** (1.32 s);
  `tests/test_corridor_cargoflow2_native.py` (offline native checks,
  incl. the wire-to-`nut` pin binding regex — unaffected by the fix)
  → **37 passed** (73.69 s); `ruff check` + `uvx ty check` on the
  touched test path → clean; `git diff --check` → clean;
  `CONTEXT.md` pin `36648f9c2fee4106` intact. Composition note of
  record: `staged_cargoflow2_composition()` stages this `main.nut` at
  the next staging round, so the next candidate's composition digest —
  and therefore its PRELAUNCH seal — differs from the consumed
  candidate-1 bytes (`c7a1c5d5…333b`, which stay sealed historical
  evidence). **NEXT (needs its own operator approval):** fresh
  candidate cycle T-002 staging → T-003 independent review → T-004
  Gate C signing → T-005 ONE launch, identical gate discipline,
  fresh identity; nothing scheduled.
- **Objective and scope:** fix the deterministic seventh-join-member
  refusal (E105 root cause) with the minimal single-package change;
  zero Python wire/protocol/guard/echo/exception-handling change.
- **Dependencies:** T-006 (root cause of record).
- **Acceptance criteria:** fix present in `SiteOp` before the
  `IsRoadDepotTile` join; focused offline suites green; static checks
  clean; exact diff verified; authority pin preserved.
- **Required evidence:** E106 row.
- **Validation procedure:** REPRODUCE.md static-check precedent
  (`ruff check`, `git diff --check`, `uvx ty check`) + the focused
  cargoflow2 suites.
- **Risks and approvals:** offline-validated only — the native world can
  only confirm it at the next Gate C launch, which is a fresh,
  separately approved attempt.

### T-008 — Read-only diagnosis: the R2 `ENGINE_PIN_MISMATCH` halt at `engine-00`

- **Status:** complete 2026-11-05, read-only forensic diagnosis under
  explicit operator task direction (diagnosis, not implementation: no
  source edits, no test edits, no staging/signing/claims, no launch,
  no AdminPort traffic, no replay reruns, no candidate reuse, no
  evidence regeneration, no Git mutations; T-005 round-2 terminal
  verdicts and both consumed candidates untouched). Full disposition
  lives in the status log and **E111**; the summary of record:
- **Root cause (CONFIRMED, source-level, deterministic):** the
  protocol-11 `engine-00` census join
  (`d5_cargoflow2_package/main.nut:448-454`) demands
  `(GSEngine.GetRunningCost(123) >> 8) == 421`, i.e. a raw of at least
  107,776; on the pinned binary (`276d5b69…904c`, upstream tag 15.3)
  `ScriptEngine::GetRunningCost` is a no-shift passthrough
  (`src/script/api/script_engine.cpp:139-143` → `engine.cpp:280-302`
  → `GetPrice(..., -8)` = `_price × factor >> 8`, `economy.cpp:949-962`
  / `economy_func.h:40`), i.e. it already returns the per-economy-year
  **display** figure — the same number the family has always recorded
  (`planner.nut:52` + `freight_runtime_planning.py:347-362`,
  `probe_package/main.nut:158`, `p08_road.py:604`), named
  `running_cost_gbp_per_economy_year = 421` since E8/attempt19; the
  256-scaled "raw" the join wanted exists only at the core vehicle
  surface (`roadveh_cmd.cpp:1652-1664`, billing numerator at
  `:1742-1745`, display conversion `vehicle_base.h:566`) and is NEVER
  script-exposed. The possible display values are exactly
  {421 (vehicle_costs ×6, measured on E8/attempt19 and consistent with
  the live purchase 4429 on the same ×6 construction leg), 562 (×8),
  632 (×9)} — `pricebase.h:57/:29` starts 1600/14000, engine 123 =
  the base road-vehicle row with `running_cost 90`, `cost_factor 108`
  (`engines.h:674-700`, `PR_RUNNING_ROADVEH` hardcoded `:658-670`);
  every possible value fails the join (1/2/2 ≠ 421); the gate is
  UNSATISFIABLE on every reachable world — a binary-and-setting
  independent formula defect, mirrored fail-closed in Python
  (`corridor_cargoflow2.py:1014` READ-step census check and
  `:1150-1157` `admit_running_cost`). The design premise itself
  (design §4 `docs/d5-cargoflow-delivery-design-2026-11-04.md:202-218`,
  package comment `main.nut:447-449`) inverted the two surfaces; the
  design's own E97 window bound (`funds 485221 → 485214`) is
  reproduced exactly by the display-421 billing arithmetic and had no
  contradiction with it — the bound was validated at the core surface
  and misapplied to the script surface.
- **Emitter path certified (Track A):** request→`CargoFlow2Handle`
  (`main.nut:1235`)→shape/echo admission (passed — the response's
  echo table comes from the decoded wire request, `:1265-1273`, so
  `engine:123` decoded correctly; `plan == f991a440…55d4e` == seal)→
  `EngineOp` (`:421`)→pin gate passed (`:427-429`)→`IsBuildable`
  passed (`:432-437`, else `UNAVAILABLE_ENGINE`)→**census join fails
  on the running-cost member → `ENGINE_PIN_MISMATCH` at `:453`**→
  refusal frame echo-only (`StripObservations` discipline, `:382-387`;
  observed frame `engine-00-response.json` carries zero census keys)→
  Python halt ladder `ENGINE_PIN_MISMATCH ∈ FAILURE_STATUSES`
  (`corridor_cargoflow2.py:208/:250`)→`HALTED_BEFORE_MUTATION`
  (`:1662/:1680`)→`PHASE_HALTED_PREFIX_PRESERVED` + replay
  `PHASE_HALTED_EVIDENCE_PRESERVED` (E110).
- **Refuted alternatives (all with receipts):** incorrect engine ID
  (echo + plan==seal); translation/indexing (same binary-pinned id
  read identically by both languages, no offset arithmetic);
  unavailable/not-buildable/company-gated (v2 candidate-5/-6
  `engine-00` READY + `purchase-00` BUILT charged exactly 4429 on the
  same world bytes `183b2027…6a6`, company 0); wrong category
  (VT_ROAD, COAL, capacity 20, speed 48, `road_type 0`); serialization
  mismatch (typed response, echoes verbatim, protocol 11); staged/
  source divergence (E108 45/45 byte audit; runtime behavior == the
  reviewed bytes' own branch behavior); binary/content-version
  (same binary across E8/attempt19/v2 candidates/candidate-2);
  world-value divergence as root cause (only the fifth member is
  world-bound; ALL its possible values fail the join — A1's own value
  among {421, 562, 632} stays UNPINNED offline, bounded, and
  immaterial to the verdict).
- **Mutation/halt semantics (Track E):** `state_changed=true`
  (`corridor_cargoflow2_native.py:1575`, "the pinned chain mutates")
  is Python bookkeeping set after the first positively-verified
  exchange (site-00), a channel/instance-state assertion, not a
  measured map delta; `HALTED_BEFORE_MUTATION` is the generic
  fail-closed label for any failed exchange and covers only the
  failed frame (EngineOp mutates nothing; `this.engine_id` only on
  success `:464-466`); `SiteOp` stays observation-only with the
  T-007 road-type re-pin a GS context set; `session-before.sav`
  `38dfa1a2…` ≠ `after-diagnostic.sav` `b0aa2383…` — the unpaused
  epoch-day advance 712223→712228 is the documented clock behavior;
  content-level save-delta attribution beyond that: UNKNOWN, not
  inferred.
- **Residual unknowns of record:** A1's in-save `economy.inflation`
  truthiness (design-only claim; corroborated offline by identical
  421/4429 across two independently generated worlds at mid-1951
  dates); A1's own running display among {421, 562, 632}; the
  after-diagnostic save content delta; whether any allowed settings
  combination could push the script running display ≥ 107,777
  (bounded NO for this binary).
- **Minimal corrective direction (not executed here):** compare
  display==display — GS join `raw != this.RUNNING_DISPLAY_PIN` (drop
  the second `>> 8`; keep the ≤2^31 sanity guard and fail-closed
  admission), Python mirrors `:1014` and `:1153` same; reword the
  inverted §4/comment premises (`main.nut:447-449`,
  `corridor_cargoflow2.py:109-110`); pin stays 421; no weakening of
  any other refusal.
- **Required regression tests for the future fix:** VM suite —
  engine-00 must reach READY with echoed `running_cost == 421` on a
  stub world whose `GetRunningCost` returns 421, and refuse any other
  value; wire tests — a READY frame with `running_cost 107,776` must
  be REFUSED (the old second-shift arithmetic would accept it:
  inversion regression lock), `421` accepted; `admit_running_cost` —
  accepts 421, refuses 0 and 107,776; wire-to-nut pin binding — no
  second shift remains on the running-cost census member; funds-model
  §4.1 arithmetic unchanged (display/365).
- **Dependencies:** T-005 round 2 (E110 terminal halt).
- **Acceptance criteria (this ticket):** emitter identified to line
  + source level; engine-123 semantics established as far as offline
  evidence permits; contract vs 15.3 semantics reconciled; mutation/
  halt semantics separated; historical comparison documented;
  hypotheses dispositioned with evidence; root cause + confidence
  stated (CONFIRMED, no native run needed); residual unknowns
  explicit; corrective direction, regression tests and the
  next-ticket proposal documented; no forbidden touch; authority pins
  intact.
- **Required evidence:** E111.
- **Validation procedure:** read-only reconstruction from staged
  artifact of record (candidate-2, seal `f991a440…55d4e`), retained
  sibling/precedent evidence, and upstream sources fetched read-only
  at tag 15.3 (= pinned binary version); integrity close per
  `REPRODUCE.md` (`git diff --check`, CONTEXT pin, manifest
  re-verification — executed; clean).
- **Risks and approvals:** the corrective fix itself is NOT executed
  on this ticket (operator approval required); a fresh candidate
  round 3 (staging → review → Gate C → one launch) remains the only
  native validation path; nothing scheduled.

### T-009 — Fix the D5-CARGOFLOW-2 engine census scale inversion

- **Status:** executed offline 2026-11-05 under explicit operator
  approval (gate DG-1, in-session: "open the corrective fix ticket and
  execute FD-A-1 offline now") — the T-008 corrective direction
  applied as specified. No staging, no signing, no claim, no launch,
  no reconnection, no `artifacts/` byte change, no commit/push.
- **Objective and scope:** the single GS census-line fix of record in
  `app/simulation/openttd/d5_cargoflow2_package/main.nut` (the joined
  running-cost member now compares the script display figure to
  `RUNNING_DISPLAY_PIN` directly — no second shift — with the honest
  `local display` rename and the fail-closed ≤2^31 sanity guard kept);
  both Python mirrors dropped of the second shift
  (`corridor_cargoflow2.py` wire readback check + `admit_running_cost`);
  the 8.8 funds arithmetic of record preserved exactly by
  reconstructing its 256-scaled surface from the pinned display figure
  (`c256 = display · 256 · rt / (365 · 74)` — integer-identical to the
  core-form charge the E99 window replicated); design §4 corrected via
  a clearly marked correction bullet (the original bullet preserved,
  its core-surface statements left intact).
- **Regression model of record (the full E111 matrix):** readback
  inversion locks — a `running_cost = 107776` engine frame (the old
  second-shift arithmetic would have admitted it) and a wrong display
  `420` both refuse the wire readback; the funds model's
  `admit_running_cost` accepts 421 of record and refuses 107776 and 0;
  the stub world's census figure is the display 421 (`GetRunningCost`
  behaves like the pinned binary surface) with its independent
  day-charge reimplementation using the same reconstruction, so the
  funds fence of record still proves the two agree; the wire-to-Nut
  byte lock asserts the shipped package carries neither a banned
  `(raw >> 8)` nor a missing `display != this.RUNNING_DISPLAY_PIN`
  join.
- **Offline validation of record:** `tests/test_corridor_cargoflow2.py`
  + `tests/test_corridor_cargoflow2_vm.py` → **88 passed** (exit 0);
  `tests/test_corridor_cargoflow2_native.py` → **38 passed** (exit 0,
  includes the new byte-lock test); `ruff check` on the touched module
  and both suites → "All checks passed!"; `uvx ty check` on the
  touched module + wire suite → "All checks passed!"; `git diff
  --check` clean; `CONTEXT.md` authority pin `36648f9c2fee4106`
  intact; consumed candidates 1–2 untouched (sealed terminal evidence;
  their seals refer to the pre-fix composition bytes of record).
- **Required evidence:** the validated diff + this ticket + status log
  entry of record; no new native evidence until the round-3 lifecycle
  runs.
- **Validation procedure:** focused suites + lint/type gates per
  `REPRODUCE.md` (E106 precedent invocations).
- **Risks and approvals:** the never-executed-tail caveat stands —
  purchase, departure gates, cycle ladder and delivery remain
  unmeasured natively on this protocol-11 line; if the round-3 launch
  halts at a class of record, the corrective loop repeats with a fresh
  round identity. Next gate: round-3 staging (T-002 round 3), then the
  unchanged ladder, each its own explicit operator approval; nothing
  scheduled.

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
- 2026-11-04 — T-002 read-only staging-readiness verification: no drift.
  Staging module digest == E100 (``f72fbcb7bf58de1c…``); wire contract
  ``2e652d62…``, package ``ffc8f030…``/``ecc5c50b…`` present; protocol
  pins intact (protocol 11, identity/schema/candidate dir of record);
  depot prerequisite ``after.sav`` re-digested == ``183b2027…6a6``; no
  ``*cargoflow2*`` artifact existed (fresh candidate); budgets pinned
  upstream (requests 32 / day 60 / max_cost 5000 / funds 489650 /
  launch 1); frozen inputs on disk (SEED17 ``frozen-source.zip``,
  OpenGFX ``opengfx-8.0-all.zip``, binary digest ``276d5b69…904c``,
  no openttd process); ``git diff --check`` clean; ``CONTEXT.md`` pin
  ``36648f9c2fee4106`` intact. REPRODUCE.md has no ``cargoflow2``
  entries — precedent-consistent (protocols 8/9/10 rounds also record
  invocations in E-rows); exact invocations recorded below.
- 2026-11-04 — T-002 Gate 2 staging executed under explicit operator
  approval (one `prepare` + read-only `preflight`/`verify`, stop before
  T-003; approval offered as a structured choice, answer recorded):
  - ONE `prepare` → ``PRELAUNCH PASS
    artifacts/experiments/d5-corridor-cargoflow2-native-candidate-1``
    first attempt; standalone `preflight` → ``PREFLIGHT PASS`` exit 0;
    pre-auth `verify` →
    ``{"authorization_state": "CLAIM_ABSENT", …,
    "verification": "AUTHORIZATION_UNVERIFIED"}`` exit 1 by design.
  - Staged root exactly 4 entries (``PRELAUNCH.json``,
    ``PRELAUNCH.sha256``, ``graphics-identity.json``, ``isolated/``);
    no gate files (no AUTHORIZATION/CLAIM/LAUNCH-CONSUMED). Seal of
    record ``c7a1c5d54e1c277410661f36b0af014a40f5c096c7b2bf579b533a63b389333b``
    == sidecar byte-exact, re-digested after every later step
    (unchanged). No ``artifact-manifest.sha256`` yet (family precedent:
    none is owed pre-launch; it appears with the launch receipts).
  - ``PRELAUNCH.json`` of record: schema ``d5-cargoflow2-prelaunch-v1``,
    milestone ``D5-CARGOFLOW``, kind ``cargoflow2``, attempt
    ``D5-CARGOFLOW-2``, candidate dir of record; binary
    ``276d5b698a6b…`` argv-pinned; ports game 52075 / admin 34135;
    fresh staged public key ``4547cc22c28bcb96…`` (secret retained
    0600 inside the candidate workspace only). Frozen inventory 3502
    entries incl. all four
    ``d5_cargoflow2_package``/``road_company_package`` ``.nut`` files;
    staged source world = the depot ``after.sav``
    (``PREREQUISITE_ATTEMPT_SOURCE_SAVE_LOAD``, digest-bound).
  - Plan of record: plan digest ``5c0998f2d164198e2545ebd9709b2ae32afdbc3d4ef4dc8a7188a202e3f0bf2d``
    + plan model digest; ``schedule_version 1``; exactly 25 exchanges
    (11 fixed ``offset -1`` chain
    site→engine→purchase→vread→order×2→order-read→monitor→start→vread,
    ``arrive-00`` watch bounded 5 days, ``flow-00…11`` at offsets
    0..55 step 5, tails ``finance-00``/``finish-00`` at offset 55);
    ladder grid schema ``d5-cargoflow2-ladder-grid-v1`` equality-gated
    5+55 = 60. Budgets: requests 32, launches 1, retries 0, reconnects
    0, 512/1400 B, 900 s, funds 489650, max_cost 5000, watch 2048
    ticks/60 s.
  - Funds model ``d5-cargoflow2-funds-model-of-record-v1`` staged:
    exact purchase debit 4429, monthly interest + 25 station fee at
    economy-month boundaries, per-day running costs with the exact 8.8
    fraction carry, income at the same observation instants; the Feb 1
    charge of record 167+25 = 192 (489650 → 489458) is the
    E99-replicated cross-check.
  - Hypotheses ``RETAINED_PROBE_REBOUND``: the 7-sample E99 prefix
    re-bound (source ``artifacts/experiments/d5-corridor-cargoflow-native-candidate-1/result.json``,
    ``774967a9a57f14dd…``); verdicts never previously bound.
  - Read-only policy ``d5-cargoflow2-readonly-v1``; cost-bearing
    surface = the quote-first ``purchase`` only. World block: tiles
    45748/50862/45487 (+ fronts 45747/50863/45743), sids 0/2,
    industries 0/1, cargo 1, engine 123, loan 100000, rate 2, launch
    day 712228, welcome ``start_day 712223`` seed 17 revision 15.3
    256×256.
  - Prerequisite block: attempt ``D5-F12-DEPOT-3``, after-save
    ``183b2027…6a6`` == the pinned world pin, prerequisite prelaunch
    ``4df12e1f…``, schema ``d5-native-prerequisite-attempt-v1``;
    provenance chain: A1 lineage after-save ``3748e00c…20bd``, depot
    chain, reload receipt (``funds_of_record 489650``, ``fleet_of_record 0``),
    world-pin version 3.
  - 0 manifest mismatches; no terminal identity touched; historical
    zones byte-untouched; writes confined to the fresh candidate dir;
    the reserve/check gate re-verified no other openttd process.
- 2026-11-04 — T-003 independent read-only review of the staged bytes
  under explicit operator approval (no modification, no signing, no
  launch; stop before Gate C):
  - Fresh re-derivation audit `/tmp/opencode/t003_review_cargoflow2_c1.py`
    (output `/tmp/opencode/t003_review_output.txt`): **42/42 checks
    PASS exit 0**, verdict **READY-FOR-GATE-C**, zero reconciliation
    debt. Every assertion re-derived from disk/live modules, then
    asserted against the staged bytes; production
    `cargoflow2_preflight`/`verify_cargoflow2_attempt` re-executed
    inside the audit (read-only) reproducing `PREFLIGHT PASS` and
    `AUTHORIZATION_UNVERIFIED`/`CLAIM_ABSENT` exit 1; seal re-digested
    unchanged at audit end (`c7a1c5d5…333b` == sidecar).
  - Re-derived bindings of record: 4-entry staged root, no gate files;
    identity quartet (schema `d5-cargoflow2-prelaunch-v1`, attempt
    `D5-CARGOFLOW-2`, candidate dir, milestone/kind) == live module
    pins; `plan_policy` == live `cargoflow2_plan_policy()` deep-equal
    (plan digest `5c0998f2…0bf2d` re-confirmed); 25-exchange schedule
    exact-by-name; ladder grid equality 5+55 = 60 (`tail_offset` 55 +
    `arrival_bound_days` 5); welcome `seed 17`/`start_day 712223`/
    revision 15.3 256×256; world tiles/sids/industries/engine 123/
    quote 4429/funds 489650/loan 100000/rate 2/fee 25/launch 712228
    == live wire constants; budgets (32/1/0/0, 512/1400 B, 900 s,
    watch 2048-60) == live `cargoflow2_budgets()`; funds model schema
    `…v1` with the 8.8 carry and Feb-1 192 cross-check statements;
    hypotheses `RETAINED_PROBE_REBOUND` == live output with source
    digest re-measured `774967a9…`; prerequisite re-pinned on disk:
    depot after-save `183b2027…6a6`, depot prelaunch `4df12e1f…`,
    reload receipt (funds 489650/fleet 0/loaded digest 3-way), A1
    lineage `3748e00c…20bd`, world-pin version 3, staged
    `source.sav` byte-equal; staged composition: AI pair + the
    delivery `main.nut` byte-equal to live roots, frozen inventory
    3502 entries with zero post-staging package drift; GameScript
    identity `info.nut` == the retained `frozen-source.zip` member
    (`staged/info.nut`, `fb7ca0ca…`) — the shipped package
    `info.nut` is intentionally a different file (save-restore identity
    of record); bridge class + `D5_CARGOFLOW2_READY` marker +
    `cargoflow2_planned` present in the staged delivery handler
    bytes.
  - Disclosures: (a) the review was executed in-session under the
    operator's T-003 approval, following the E98/E99 re-derivation
    precedent; the ticket's "separate reviewer" line is satisfied by
    the fresh-context re-derivation script rather than a second
    session — recorded openly as a disclosed deviation the operator
    committed by this approval. (b) Zero staged defects; three
    audit-script incidents self-caught before any claim: run-1
    KeyError on a misread grid key (`tail_offset`/`flow_samples`,
    not `flow_span_days`); run-2 reported a composition mismatch
    because the check wrongly required the staged GameScript
    identity `info.nut` to equal the shipped package's `info.nut` —
    production `staged_cargoflow2_composition()` stages the
    frozen-source.zip member by design; run-3 dropped an unavailable
    E99-byte corroboration (the consumed probe's certified cleanup
    disposed its workspace; its `isolated/` retains no `.nut` bytes).
    (c) The E99-probe hypothesis source remains read-only-rebound
    only; nothing reopens it.
  - NEXT: T-004 Gate C Option-1 signing (operator gate; payload binds
    `D5-CARGOFLOW-2` to the freshly staged candidate seal
    `c7a1c5d5…333b`; no authorization reuse across candidates).
- 2026-11-04 — T-004 Gate C Option-1 signing executed under explicit
  operator approval (ONE signing operation + read-only verification;
  stop before T-005; no launch):
  - Fresh signer script `/tmp/opencode/t004_gate_c_cargoflow2.sh`
    (re-derived per-round on the E98/E99 signer precedent; the
    candidate-bound e98 script is never reused). Pre-write refusal
    gates: gate surface absent (AUTHORIZATION.json/CLAIM.json/
    LAUNCH-CONSUMED.json/receipt.json/result.json/runtime-identity.json),
    live seal == sidecar == the operator-approved seal of record
    `c7a1c5d54e1c277410661f36b0af014a40f5c096c7b2bf579b533a63b389333b`
    (hard-asserted against the seal named in the approval).
  - Seed mechanics identical to E99: memory-only extraction from the
    operator-held PEM outside the repository (48-byte PKCS#8 DER,
    final-32-bytes window of record), env-only
    `CARGOFLOW_GATE_SEED`, never printed/never filed/never
    argument-passed; pre-write identity asserted
    (`public_from_seed(seed)` == pinned anchor `5063982bd28d…880f`);
    env unset + printenv-empty verified after. One invocation, no
    pre-write refusal needed (the measured window was already the E99
    corrected one).
  - Production signing surface only:
    `authorization_payload(metadata, seal)` +
    `canonical_authorization_bytes` + `sign_authorization_record` +
    `write_authorization_record` + `verify_authorization`; payload
    digest of record
    `3d787802c0f0d3fda825ffb86d6a4c29b3de1f97df43820d641423c2da361661`
    cross-checked == production
    `staged_cargoflow2_authorization_payload_digest(candidate)`;
    `AUTHORIZATION.json` record digest
    `427bbdb4103022ba95bd2f5d5f91bff5e5bd23d78a364d96ffac3d1261793cdc`;
    operator identity unchanged
    `sha256-ed25519-public-key:cbb63ff58f17f13df3e1be0735fad18497e3a0c6ad6b5dd55491d708ae40c614`.
  - Post-write read-only state of record: root = 5 top-level entries
    (`AUTHORIZATION.json` joins the 4 staged entries; no CLAIM.json,
    no LAUNCH-CONSUMED.json); seal byte-equal after the write;
    `preflight` PASS with the authorization present; standalone
    pre-launch `verify` → `AUTHORIZATION_UNVERIFIED` / `CLAIM_ABSENT`
    exit 1 as designed (the claim is minted only at the launch
    boundary; the lifecycle advanced by the presence of the verified
    authorization record).
  - Zero staged defects, zero re-writes: the signing completed in
    invocation-1; one auxiliary reproduction incident self-caught
    (the script's post-write block passed a relative candidate path,
    and `terrain_clearing.reopen` keeps the passed path unresolved,
    so `is_relative_to` refused in that auxiliary block only; the
    rerun of the read-only post-state used the resolved path exactly
    as the T-003 audit did and passed). The signing itself was never
    repeated.
  - NEXT: T-005 launch gate — ONE launch of the signed candidate at
    the pinned binary/OpenGFX versions, then read-only replay +
    cleanup. Requires its own explicit operator approval; nothing
    scheduled.
- 2026-11-05 — T-005 launch gate executed under explicit operator
  approval (exactly ONE native launch + read-only replay + certified
  cleanup; no retries, no relaunches, no second attempt; stop after
  final reporting):
  - Pre-launch gates re-verified fresh (nothing stale): live seal ==
    sidecar == the operator-approved seal of record
    `c7a1c5d54e1c277410661f36b0af014a40f5c096c7b2bf579b533a63b389333b`;
    pinned binary sha256 `276d5b69…904c`; OpenGFX
    `43a0c1dabf39cb86…10903be`; no openttd process; candidate root =
    5 entries (AUTHORIZATION.json + 4 staged); no
    CLAIM.json/LAUNCH-CONSUMED.json yet.
  - Launch command of record (E82/E99 invocation shape), executed
    exactly once: export `OPENTTD_BINARY=/home/fed/Downloads/openttd-15.3-linux-generic-amd64/openttd`
    and `OPENTTD_OPENGFX_ARCHIVE=/home/fed/codes/softdev2/artifacts/runtime/verified-assets/opengfx-8.0-all.zip`
    before Python starts, then
    `.venv/bin/python -m app.simulation.openttd.proof.corridor_cargoflow2_native run /home/fed/codes/softdev2/artifacts/experiments/d5-corridor-cargoflow2-native-candidate-1`.
    **`run` return code of record: 1.**
  - Run outcome of record: `status=PHASE_HALTED_PREFIX_PRESERVED`,
    `returncode=0`, `preflight=PASS`, `native_launches=1`
    (== budget), `connections=1` (== budget), `requests=1`,
    `exchanges=[]`, `command_accepted=false`, `state_changed=false`,
    `verified=false`; halt
    `{"label":"site-00","error":"ValueError: the delivery exchange site-00 failed verification: cargo-flow 2 exchange site-00 ended INVALID_SITE"}`;
    phase verdict `CARGOFLOW2_GATE_UNDECIDED_INCOMPLETE`.
    Exchange `site-00-request.json` (op=site, protocol 11, depot
    `45487`, pickup `45748`, delivery `50862`, plan ==
    the candidate seal) → `site-00-response.json` status
    **`INVALID_SITE`**; server stderr decisive line
    `D5_CARGOFLOW2 site-00 INVALID_SITE` before admin disconnect.
    Prefix preserved: all 26 later steps remained pending
    (engine-00 … finish-00); the halt class is terminal — nothing
    relabeled, nothing retried, no relaunch.
  - Read-only replay of record, executed once:
    `.venv/bin/python -m app.simulation.openttd.proof.corridor_cargoflow2_native verify /home/fed/codes/softdev2/artifacts/experiments/d5-corridor-cargoflow2-native-candidate-1`
    → **`{"verification":"PHASE_HALTED_EVIDENCE_PRESERVED","failed":{"label":"site-00","status":"INVALID_SITE","world_state":"HALTED_BEFORE_MUTATION",…},"result_status":"PHASE_HALTED_PREFIX_PRESERVED"}`,
    exit 1** — the replay verdict reconciles the run verdict exactly;
    no retry on halt; consumed identity never relaunched.
  - Post-run read-only state of record: root grew to 19 top-level
    entries (`CLAIM.json`, `LAUNCH-CONSUMED.json`, `frames.json`,
    `cleanup.json`, `result.json`, `runtime-identity.json`,
    `session-before-identity.json`, `session-before.sav`,
    `site-00-request.json`, `site-00-response.json`, `stdout.log`,
    `stderr.log`, `artifact-manifest.sha256` join the staged 5 +
    `isolated/`);
    `LAUNCH-CONSUMED.json` of record
    `{"authorization_sha256":"427bbdb4…793cdc","operator_key_identity":"sha256-ed25519-public-key:cbb63ff5…40c614","prelaunch_digest":"c7a1c5d5…333b","schema":"d5-native-launch-consumed"}`;
    `CLAIM.json` of record
    `{"authorization_schema":"d2-clearing-claim-authorization-v2","consumed":true,"launches_allowed":1,"retries":0}`
    with the same record/identity bindings. Pre-launch seal
    `PRELAUNCH.json` byte-equal after the run;
    `artifact-manifest.sha256` re-verified 16/16 OK, 0 non-OK.
  - Certified cleanup of record: `cleanup.json`
    `reaped=true`, `sockets_closed=true`, `workspace_disposed=true`,
    `credential_removed=true`, `cleanup_error=[]`,
    `remaining_processes=[]`, `returncode=0`, `graceful_attempted=true`
    (`quit_requested` → `reaped`), endpoint verification
    `connection_closed=true`, `listener_closed=true`,
    `process_reaped=true`, `reservation_released=true`, and a TCP
    `TIME_WAIT` kernel state on the admin-port tuple with
    `immediate_rebindability_required=false`
    (policy `linux-kernel-endpoint-closure-v1`); no openttd process
    after the run.
  - Integrity close-out: `git diff --check` clean; `CONTEXT.md` pin
    `36648f9c2fee4106` intact; historical zones untouched; no
    commit/push; staged bytes untouched apart from the pipeline-written
    post-launch artifacts; no standalone scripts used (CLI of record
    only).
  - NEXT: T-006+ downstream gates (verdict reconciliation → M8 → …)
    require their own explicit operator approval; nothing scheduled;
    the consumed candidate-1 lifecycle can never be relaunched.
- 2026-11-05 — T-006 read-only root-cause diagnosis executed under
  explicit operator approval (read-only only; no source edits, no
  restaging, no signing, no native run, no credential reads, no Git
  mutations; preserve terminal verdicts; consumed candidate-1 never
  relaunched or reconnected):
  - Outcome class of record (T-006's own §7 reconciliation): NOT
    achieved — halted at the first of 26 exchanges with
    `state_changed=false`/`HALTED_BEFORE_MUTATION`; per this ticket's
    rule the capture-fix round opens with a fresh identity and design
    record, never a relabel or reopen of the terminal attempt.
  - Dispatch path exclusion of record: `d5_cargoflow2_package/
    main.nut` has two `INVALID_SITE` emitters — (1) the pre-ladder
    pin-drift gate (`CargoFlow2PinsDrifted`, line 300 — request echoes
    `pickup 45748 / delivery 50862 / depot 45487 / offset -1` are
    byte-equal the baked GS pins, planned-op/offset match, excluded);
    (2) the seven-fact live re-derivation inside `SiteOp` (lines 393–399
    `GetStationID(pickup)==PICKUP_SID 0`, `GetStationID(delivery)==
    BAY_SID 2`, `IsValidStation 0/2`, `IsValidIndustry 0/1`,
    `IsRoadDepotTile(depot_tile)`). Caught-exception refusals are
    logged `D5_CARGOFLOW2_THROW` + `UNSUPPORTED_NATIVE_FACT`
    (catch at the dispatch) — stderr has no `D5_CARGOFLOW2_THROW`, so
    the refusal of record was a normal `SiteOp` join return.
  - **Root cause of record (high confidence):** the failing package's
    `SiteOp` calls `GSRoad.IsRoadDepotTile(this.depot_tile)` **without
    ever calling `GSRoad.SetCurrentRoadType(GSRoad.ROADTYPE_ROAD)`**
    (grep of record: 0 occurrences of `SetCurrentRoadType` in
    `d5_cargoflow2_package/main.nut` vs ≥1 in every worked
    predecessor — `d5_freight_v2_package/main.nut`:1694 (in `Handle`,
    before every op), `d5_depot_mutation_package/main.nut`:173,
    `d5_depot_recheck_package/main.nut`:242,
    `d5_extension_package/main.nut`:1016, freight v1 `vehicle.nut`:139
    (+ its defensive `GetCurrentRoadType()!=0` guard)). Upstream
    OpenTTD **15.3** source of record (tag of the pinned binary
    `276d5b69…904c`): `src/script/script_storage.hpp` —
    `RoadType road_type = INVALID_ROADTYPE;` (**every fresh script
    instance starts with no road type set**); `src/script/api/
    script_road.cpp` `ScriptRoad::IsRoadDepotTile` —
    `if (!IsRoadTypeAvailable(GetCurrentRoadType())) return false;`
    → the seventh join member evaluates false **deterministically,
    independent of the world**.
  - **No identity failed validation** (the evidence of record):
    identical launched world bytes (`183b2027…6a6` = depot-mutation-3
    after-save, staged + preflight-verified at `source.sav`; welcome
    identity `seed 17 / start_day 712223 / revision 15.3` matching all
    retained chain sessions) measured live-true by the same-session
    precedent `d5-corridor-freight-native-candidate-5` (its own
    `site-00-response.json`, v2 handler which DOES set the road type
    first): `sid0=0` `truck0=true` (pickup stop 45748 ⇒ station 0),
    `sid1=2` `truck1=true` (A1 bay 50862 ⇒ station 2),
    `pickup_industry=0` count 1, `delivery_industry=1` count 1,
    `depot_ok=true` `depot_edge=true`, `funds=489650` == pinned
    close-out funds, `status=READY`. The extension-3 chain independently
    confirmed bay tile 50862 carries `sid=2` (`confirm-03-response.json`)
    and the depot chain confirmed depot 45487 (`depot-00-response.json`,
    `after-00`: depot_present/linked, front 45743). The halted session
    advanced no ticks against the pinned instant (`state_changed=false`,
    launch-day/site exchange ran within the same second as the READY
    banner); nothing mutated.
  - **Which identity failed?** None. The falsified member is the
    road-depot tile **predicate** on depot 45487 — its
    road-type-availability precondition, falsified by the unset
    per-instance road type of the fresh GS instance — not the depot,
    not the pickup stop, not the delivery bay, not either industry.
  - Confidence: **high** for the class (two-source 15.3 proof +
    family Set-before-Get precedent + same-world live-measure
    superset); the residual (UNKNOWN, not guessable offline): the exact
    live `GetCurrentRoadType()` value inside the failing instance can
    never be re-measured (one-launch-of-record spent; no secondary
    native run permitted) — the determination rests on the released
    15.3 source of the exact tagged binary.
  - Integrity close-out: read-only reads only; no source files edited;
    no `artifacts/` bytes touched; `git diff --check` clean;
    `CONTEXT.md` pin `36648f9c2fee4106` intact; secrets/keys untouched.
  - NEXT (T-007, needs operator approval): single-package GSRoad
    sequencing fix inside `d5_cargoflow2_package/main.nut` `SiteOp`
    (Set-before-Get ROADTYPE_ROAD on the family idiom), then a full
    fresh candidate cycle (T-002 staging → T-003 review → T-004 Gate C
    → T-005 ONE launch) under the same gate discipline with a fresh
    candidate identity and seal; candidate-1 stays sealed consumed;
    nothing relabeled, nothing relaunched, nothing scheduled.
- 2026-11-05 — T-007 executed under explicit operator approval (the
  fix itself only; no staging, no signing, no candidate creation, no
  OpenTTD launch, no historical evidence modification, no Git
  mutations, candidate-1 untouched):
  - Package fix of record (`app/simulation/openttd/` `d5_cargoflow2_package/main.nut`):
    inside `SiteOp`, before the `/* Re-pin gate: */` join, a five-line
    comment of the T-006 root cause plus
    `GSRoad.SetCurrentRoadType(GSRoad.ROADTYPE_ROAD)` — the freight v2
    `Handle`:1694 family idiom. Grep of record: one GSRoad consumer in
    the package (`IsRoadDepotTile` join member at >399); the
    `cargoflow2_planned` pin table, guards, echoes, catch branch and
    every other package byte unchanged.
  - Regression model of record
    (`tests/test_corridor_cargoflow2.py`): the stub GSRoad gains the
    15.3 fail-close behavior on the depot-mutation E72 stub idiom —
    `::cur_road_type <- 63` default (INVALID_ROADTYPE),
    `IsRoadTypeAvailable(t) == (t == ROADTYPE_ROAD)`,
    `SetCurrentRoadType` silently no-ops an unavailable type,
    `GetCurrentRoadType`, and `IsRoadDepotTile` gated on
    `IsRoadTypeAvailable(GetCurrentRoadType())`. Consequence: the
    pre-fix package bytes now fail the VM suite, so the suite is a
    true regression lock for this defect class.
  - Offline validation of record: `tests/test_corridor_cargoflow2_vm.py`
    + `tests/test_corridor_cargoflow2.py` → **87 passed** (1.32 s);
    `tests/test_corridor_cargoflow2_native.py` → **37 passed** (73.69
    s; offline native checks only, including the wire-to-`nut` pin
    binding regex test — it binds the planned-row/pin-table shapes,
    which the fix does not touch). Static checks of record:
    `ruff check tests/test_corridor_cargoflow2.py` → "All checks
    passed!"; `uvx ty check` on the touched path → "All checks
    passed!"; `git diff --check` → clean.
  - Diff close-out of record: 4 files changed (+433/−7 across this
    round's ledger rows and the two fix files); exact hunks verified
    in `git diff` (main.nut +6: 5 comment lines + the Set line;
    test_corridor_cargoflow2.py: init default + the full fail-close
    GSRoad class); `CONTEXT.md` pin `36648f9c2fee4106` intact.
  - Sealing note of record: `staged_cargoflow2_composition()` stages
    this `main.nut`, so the NEXT candidate's composition digest and
    PRELAUNCH seal differ from the consumed candidate-1 bytes
    (`c7a1c5d5…333b`, sealed historical evidence, untouched); the
    next Gate C round derives its own fresh seal.
  - NEXT (needs its own operator approval): fresh candidate cycle
    T-002 staging → T-003 independent review → T-004 Gate C signing →
    T-005 ONE launch under the unchanged gate discipline; nothing
    scheduled, nothing relabeled, nothing relaunched. Evidence index
    E106.
- 2026-11-05 — T-002 round-2 staging executed under explicit operator
  approval (ONE `prepare` + read-only `preflight`/inline + standalone
  `preflight` + pre-auth `verify`; stop before T-003; never reuse
  candidate-1; no signing, no launch, no reconnection, no historical
  evidence modification, no Git mutations):
  - Identity advance of record: the pipeline's candidate-dir-of-record
    constant advanced
    `d5-corridor-cargoflow2-native-candidate-1` →
    `d5-corridor-cargoflow2-native-candidate-2` (the T-007 fix cycle's
    own round identity; comment records candidate-1 as sealed consumed
    history). No other pipeline byte edited. Focused suites re-run
    green on the edited module: `tests/test_corridor_cargoflow2_native.py`
    → 37 passed (63.16 s), `tests/test_corridor_cargoflow2_vm.py` +
    `tests/test_corridor_cargoflow2.py` → 87 passed (1.29 s);
    `ruff check` on the touched module → clean; `uvx ty check` on the
    module → 1 PRE-EXISTING diagnostic only (`invalid-method-override`
    at the `connect` method, line 1176 — outside this round's edit,
    which is a string constant; disclosed, not repaired, no behavior
    change).
  - ONE `prepare` → ``PRELAUNCH PASS
    artifacts/experiments/d5-corridor-cargoflow2-native-candidate-2``
    first attempt, exit 0; standalone `preflight` → ``PREFLIGHT PASS``
    exit 0; pre-auth `verify` →
    ``{"authorization_state": "CLAIM_ABSENT", …,
    "verification": "AUTHORIZATION_UNVERIFIED"}`` exit 1 by design.
  - Staged root exactly 4 entries (``PRELAUNCH.json``,
    ``PRELAUNCH.sha256``, ``graphics-identity.json``, ``isolated/``);
    no gate files (no AUTHORIZATION/CLAIM/LAUNCH-CONSUMED/artifact
    manifest). Seal of record
    ``f991a440de773b350a134db528d1ddef528c527ab893d2b5cce2e8fd00255d4e``
    == sidecar byte-exact, freshly derived from the fixed composition
    and ≠ candidate-1's ``c7a1c5d5…333b``.
  - Identity of record in the fresh ``PRELAUNCH.json``: schema
    ``d5-cargoflow2-prelaunch-v1``, milestone ``D5-CARGOFLOW``, kind
    ``cargoflow2``, attempt ``D5-CARGOFLOW-2``,
    candidate_directory ``d5-corridor-cargoflow2-native-candidate-2``,
    binary ``276d5b69…904c`` argv-pinned, fresh staged public key
    ``8554728676a19efb…``, ports game 60131 / admin 59411, workspace
    ``isolated/openttd-15.3-xkikmt5i``; frozen inventory 3502 entries;
    world block = the pinned depot after-save prerequisite
    ``183b2027…6a6`` (``PREREQUISITE_ATTEMPT_SOURCE_SAVE_LOAD``,
    welcome ``seed 17 / start_day 712223 / revision 15.3``); budgets
    byte-identical the round-1 plan of record (requests 32, launches
    1, retries 0, reconnects 0, funds 489650, max_cost 5000, watch
    2048 ticks/60 s, day 60).
  - **Fix-carry proof of record:** staged
    ``isolated/openttd-15.3-xkikmt5i/game/RoadFreightProof/main.nut``
    digest ``2c7f6b09e87d6ebf…`` == the frozen inventory entry, and
    the staged bytes contain ``GSRoad.SetCurrentRoadType`` (the T-007
    fix) — the composition digest necessarily differs from
    candidate-1's staged main ``ffc8f030cc4b2620…`` (pre-fix bytes),
    so candidate-2 is a genuinely new composition, not a relabel.
  - Read-only policy held: ``PRELAUNCH.sha256`` unchanged after the
    standalone preflight and verify steps; candidate-1 re-digested
    byte-identical ``c7a1c5d5…333b`` (sealed consumed, untouched);
    writes confined to the fresh candidate-2 directory.
  - NEXT (T-003, needs its own operator approval): independent
    read-only review of the staged round-2 candidate; nothing
    scheduled, nothing relaunched. Evidence index E107.
- 2026-11-05 — T-003 round-2 independent read-only review executed
  under explicit operator approval (no file writes inside the repo, no
  staging rerun, no signing, no claims, no OpenTTD launch, no
  reconnection; candidate-1 and candidate-2 bytes untouched):
  - Method of record: one fresh re-derivation script
    `/tmp/opencode/t003_r2_review_cargoflow2_c2.py`
    (output `/tmp/opencode/t003_r2_output.txt`) — 45 checks across
    identity/seal/structure, source↔staged correspondence (incl. the
    T-007 fix placement), binary/OpenGFX/world lineage, pins/budgets/
    plan re-derivation, pipeline preflight + pre-auth verify
    re-execution, environment confinement, absence of unauthorized
    gate/launch artifacts. **45/45 PASS, verdict READY-FOR-GATE-C.**
  - Review details of record: seal `f991a440de773b35…55d4e` ==
    sidecar + unchanged after the whole review (re-digested);
    staged `main.nut` byte-equal the app package AND contains the
    T-007 fix exactly once, inside `SiteOp`, before the `/* Re-pin
    gate: */` join; staged `info.nut` byte-equal the frozen
    `staged/info.nut`; staged AI byte-equal the package; inventory
    main-digest == recomputed staged digest `2c7f6b09e87d6ebf…` ≠
    candidate-1's pre-fix `ffc8f030…`; binary digest pin, argv pins
    (workspace cfg/source.sav/`-dscript=4,grf=1,net=3`), no openttd
    process; `source.sav` == pinned depot-3 after-save
    `183b2027…6a6`; welcome/pin/budgets/schedule/
    schedule_version/ladder-grid/funds-model blocks re-derived equal
    (plan digest + model digest re-computed from the live pipeline ==
    staged values); hypotheses `RETAINED_PROBE_REBOUND` still bound to
    the consumed protocol-10 receipt with its digest recomputed
    byte-true; OpenGFX staged files re-digested == identity == zip;
    `.admin-secret` mode 0600 asserted metadata-only (contents never
    read), excluded from the frozen inventory; environment overrides
    confined to the workspace; ports 60131/59411 sane+distinct;
    `cargoflow2_preflight` re-executed PASS; `verify_cargoflow2_attempt`
    re-executed → `AUTHORIZATION_UNVERIFIED`/`CLAIM_ABSENT` exit 1 by
    design; root exactly 4 entries, no gate files, no run logs/saves
    in the workspace; `save_policy` present. Script-side twos (a
    comment-suffix search string and a schedule-row key name) were
    corrected in the review script itself — the candidate needed zero
    corrections; both script digests recorded above.
  - Integrity close-out: candidate-1 seal re-digested
    `c7a1c5d5…333b` == sidecar (untouched); candidate-2 seal
    unchanged post-review; `git diff --check` clean; `CONTEXT.md` pin
    `36648f9c2fee4106` intact.
  - Residual risks of record (for T-004/T-005, not blocking): the E105
    residual UNKNOWN (exact live road type of the failing instance)
    remains unmeasurable offline — candidate-2 carries the fix whose
    live effect shows only at the ONE Gate C launch; the pre-existing
    `uvx ty` diagnostic (`invalid-method-override` at `connect`)
    remains unfixed upstream noise; ports are allocated fresh at
    T-005, so reuse of 60131/59411 is not guaranteed at launch.
  - NEXT (T-004, needs its own operator approval): Gate C Option-1
    signing on the round-2 candidate (fresh operator-held PEM, fresh
    seed discipline — `CARGOFLOW_GATE_SEED` env-only, never
    printed/filed/argument-passed); nothing scheduled, nothing
    relabeled, nothing relaunched. Evidence index E108.
- 2026-11-05 — T-004 round-2 Gate C Option-1 signing executed under
  explicit operator approval (signing only; ONE signing operation +
  read-only verification; stop before T-005; no claim, no launch, no
  reconnection, no consumption, no historical evidence modification,
  no Git mutations):
  - Pre-write identity + seal re-verification of record (the fresh
    round-2 signer script `/tmp/opencode/t004_gate_c_cargoflow2_c2.sh`,
    per-round re-derivation on the E99/E98 signer precedent; the
    candidate-1-bound `t004_gate_c_cargoflow2.sh` never reused):
    gate surface absent (AUTHORIZATION.json/CLAIM.json/
    LAUNCH-CONSUMED.json/receipt.json/result.json/runtime-identity.json),
    live seal == sidecar == the operator-approved seal of record
    `f991a440de773b350a134db528d1ddef528c527ab893d2b5cce2e8fd00255d4e`
    (hard-asserted twice in the script, incl. the exact candidate-2
    approval constant).
  - Seed mechanics identical to E99/round-1: memory-only extraction
    from the operator-held PEM outside the repository (48-byte PKCS#8
    DER, final-32-bytes window of record), env-only
    `CARGOFLOW_GATE_SEED`, never printed/never filed/never
    argument-passed; pre-write identity asserted
    (`public_from_seed(seed)` == pinned anchor
    `5063982bd28d…880f`); env unset + printenv-empty verified after
    (and outside the script session). Operator PEM contents never
    read beyond the DER-body parse; no credential inspection beyond
    that surface.
  - Production signing surface only: `authorization_payload(metadata,
    seal)` + `canonical_authorization_bytes` +
    `sign_authorization_record` + `write_authorization_record` +
    `verify_authorization`; payload digest of record
    `3f489b183c819a4d76775e88490d27e915d41eb56a9f3652ff5b70da4ee55788`
    cross-checked == production
    `staged_cargoflow2_authorization_payload_digest(candidate-2)`;
    `AUTHORIZATION.json` record digest
    `45820767c462be4469e8a11f8ab9d351f5badba7ad544ac694e20bfd3277eeb9`;
    operator identity unchanged
    `sha256-ed25519-public-key:cbb63ff58f17f13df3e1be0735fad18497e3a0c6ad6b5dd55491d708ae40c614`.
  - Post-write read-only state of record: root = 5 entries
    (`AUTHORIZATION.json` joins `PRELAUNCH.json`/`PRELAUNCH.sha256`/
    `graphics-identity.json`/`isolated/`; no CLAIM.json, no
    LAUNCH-CONSUMED.json); seal `f991a440…55d4e` byte-equal after the
    write; `preflight` PASS with the authorization present;
    standalone pre-launch `verify` → `AUTHORIZATION_UNVERIFIED` /
    `CLAIM_ABSENT` exit 1 as designed (the claim is minted only at
    the launch boundary; the lifecycle advanced by the presence of
    the verified authorization record).
  - Zero staged defects, zero re-writes: the signing completed in
    invocation-1 with no auxiliary incident (the round-1
    relative-path lesson baked in — the post-write block uses the
    absolute candidate path). No candidate bytes beyond
    `AUTHORIZATION.json` were written; the PRELAUNCH seal
    re-verified post-write.
  - NEXT (T-005, needs its own explicit operator approval): ONE launch
    of the signed candidate-2 at the pinned binary/OpenGFX versions,
    then read-only replay + integrity sweep + certified cleanup;
    nothing scheduled, nothing relaunched. Evidence index E109.
- 2026-11-05 — T-005 round-2 launch gate executed under explicit
  operator approval (exactly ONE native launch of candidate-2 +
  read-only replay + integrity sweep + certified cleanup of record;
  stop after final reporting; no retries, no relaunches, no
  reconnections, no source edits, no second attempt, no historical
  evidence modification, no Git mutations):
  - Pre-launch gates re-verified fresh (nothing stale; per-round
    script `/tmp/opencode/t005_r2_prelaunch_gates.sh`, E104
    precedent): no openttd process; gate surface = exactly the 4
    staged entries + `AUTHORIZATION.json` (+ `isolated/`), no launch
    receipts; live seal == sidecar == the operator-approved seal of
    record `f991a440de773b350a134db528d1ddef528c527ab893d2b5cce2e8fd0
    0255d4e`; `verify_authorization` PASS via the production surface
    (record `45820767…7eeb9`, payload `3f489b18…4ee55788` ==
    `staged_cargoflow2_authorization_digest`, operator identity
    `sha256-ed25519-public-key:cbb63ff5…40c614`); binary file
    sha256 == pin `276d5b69…904c`; staged `source.sav` digest ==
    the world bind `183b2027…efe6a6`; argv pins `-D127.0.0.1:60131` /
    `-c cfg` / `-g source.sav` / `-dscript=4,grf=1,net=3`; budgets
    `launches 1 / retries 0 / reconnects 0 / connection_attempts 1`;
    OpenGFX-8.0 archive present → `T-005 R2 PRE-LAUNCH GATES: ALL
    PASS`, one attempt.
  - Launch command of record (E104/E82 invocation shape), executed
    exactly once with `OPENTTD_BINARY` and `OPENTTD_OPENGFX_ARCHIVE`
    exported before Python starts:
    `.venv/bin/python -m app.simulation.openttd.proof.corridor_cargoflow2_native run /home/fed/codes/softdev2/artifacts/experiments/d5-corridor-cargoflow2-native-candidate-2`
    → **run return code of record: 1**.
  - Run outcome of record (verified terminal in the JSON of record):
    `preflight=PASS`, `native_launches=1` (== budget), `connections=1`
    (== budget), `requests=2`, `exchanges=["site-00"]`,
    `command_accepted=true`, `state_changed=true`, `verified=false`,
    `status=PHASE_HALTED_PREFIX_PRESERVED`. site-00 `READY` (day
    712228 tick 14, funds 489650, income 0 — funds fence intact); the
    E106/T-007 `GSRoad.SetCurrentRoadType` fix measured live-true;
    round-1's `INVALID_SITE` class did not recur. Halt of record:
    `{"label":"engine-00","error":"ValueError: the delivery exchange
    engine-00 failed verification: cargo-flow 2 exchange engine-00
    ended ENGINE_PIN_MISMATCH"}` — engine-00 response `ENGINE_PIN_
    MISMATCH`, op `engine`, requested pin `engine=123`, cost 0,
    plan == seal, protocol 11, world bind depot `45487` / pickup
    `45748` / delivery `50862`; stderr decisive line
    `D5_CARGOFLOW2 engine-00 ENGINE_PIN_MISMATCH`; phase verdict
    `CARGOFLOW2_GATE_UNDECIDED_INCOMPLETE`. The halt class is
    terminal; 23 later steps pending (the live engine-identity fact
    is unmeasured this round — recording the class is all T-005
    claimed, no diagnosis without a new approval).
  - Read-only replay of record, executed once:
    `.venv/bin/python -m app.simulation.openttd.proof.corridor_cargoflow2_native verify /home/fed/codes/softdev2/artifacts/experiments/d5-corridor-cargoflow2-native-candidate-2`
    → `{"verification":"PHASE_HALTED_EVIDENCE_PRESERVED","failed":
    {"label":"engine-00","status":"ENGINE_PIN_MISMATCH",
    "world_state":"HALTED_BEFORE_MUTATION",…},"exchanges":["site-00"],
    "result_status":"PHASE_HALTED_PREFIX_PRESERVED"}`, **exit 1** —
    the replay verdict reconciles the run verdict exactly; consumed
    identity never relaunched.
  - Post-run read-only state of record: root = 20 files + `isolated/`
    (empty shell, the E104 shape; `after-diagnostic.sav` retained);
    `LAUNCH-CONSUMED.json` binds authorization record `45820767…7eeb9`
    + seal `f991a440…55d4e` + operator identity `cbb63ff5…40c614`
    (`schema d5-native-launch-consumed`); `CLAIM.json` `consumed=true
    / launches_allowed=1 / retries=0`; certified cleanup of record
    `reaped=true / sockets_closed=true / workspace_disposed=true /
    credential_removed=true`, `cleanup_error=[]`,
    `remaining_processes=[]`, `returncode=0` (pid 181344, quit
    requested → reaped), listener closed, reservation released; post-
    run process/port check: no openttd process, game 60131 / admin
    59411 free; `artifact-manifest.sha256` re-verified 19/19 OK, 0
    non-OK; `PRELAUNCH.json` seal byte-equal + sidecar after the run.
  - Integrity close of record: `git diff --check` clean; CONTEXT pin
    `36648f9c2fee4106` intact; candidate-1 untouched (sealed
    R6 terminal evidence); no source edits; no ticket restructuring;
    nothing scheduled — any capture-fix round (fresh candidate
    round identity + explicit operator approval only) starts from
    T-002 staging. Evidence index E110.
- 2026-11-05 — T-008 read-only forensic diagnosis of the round-2
  `ENGINE_PIN_MISMATCH` halt at `engine-00`, executed under explicit
  operator task direction (docs-only; zero code edits, zero test
  edits, zero staging/signing/claims, zero launches, zero AdminPort
  traffic, zero replay reruns, zero candidate reuse, zero evidence
  regeneration, zero Git mutations; T-005 round-2 terminal verdicts
  untouched):
  - Emitter of record: the `engine-00` census join
    (`d5_cargoflow2_package/main.nut:448-454`); the echo/pin branch
    (`:427-429`) refuted by the live decoded-request echo table and
    the E110 observed frame shape, `UNAVAILABLE_ENGINE` (`:432-437`)
    refuted by `IsBuildable(123)` true (E8 census + freight-v2
    candidate-5/-6 `engine-00` READY on the same world bytes).
  - Root cause CONFIRMED at source level against tag-15.3 upstream
    (= the pinned binary version): the join's `(raw >> 8) == 421`
    member demands `raw ≥ 107,776`, while the script surface already
    returns the per-economy-year display figure (possible values
    exactly {421, 562, 632} across allowed `vehicle_costs`; all fail
    the join: 1/2/2 ≠ 421) — an UNSATISFIABLE gate, deterministic,
    world- and setting-independent; mirrored fail-closed in both
    Python checks (`corridor_cargoflow2.py:1014`, `:1153`); the
    inverted premise is documented in design §4 and the package
    comment and traced to the dual reading of core `RoadVehicle::
    GetRunningCost()` (256-scaled, billing surface, never
    script-exposed) vs script `Engine::GetRunningCost()` (display).
    Four of five census members measured live-equal on the same
    world bytes (candidate-5/-6, incl. live purchase 4429); A1's own
    fifth-member display value stays UNPINNED offline but bounded and
    immaterial.
  - Corrective direction of record: display==display comparison in
    the GS join (drop the second shift; fail-closed admission kept;
    pin stays 421) + both Python mirrors; reword the inverted
    premises; regression-lock matrix captured in the T-008 ticket
    (incl. the 107,776-refusal inversion lock and the no-second-shift
    byte binding). Next ticket proposed: "Fix the D5-CARGOFLOW-2
    engine census scale inversion", executed offline, then the usual
    fresh candidate round-3 ladder, each gate separately approved;
    nothing scheduled here.
  - Integrity close: `git diff --check` clean on both ledger files;
    `CONTEXT.md` pin `36648f9c2fee4106` intact; candidate-1 and
    candidate-2 artifact manifests re-verified untouched (19/19
    each); source WIP paths byte-identical to the pre-task set.
    Evidence index E111.
- 2026-11-05 — T-009 (the census-scale inversion fix, the T-008
  corrective direction of record) executed offline under explicit
  operator approval:
  - GS fix of record: `d5_cargoflow2_package/main.nut` — the census
    join reads `local display = GSEngine.GetRunningCost(pinned)` and
    compares `display != this.RUNNING_DISPLAY_PIN` with no second
    shift (header §4.1 comments + the pin comment reworded to the
    E111-corrected premise; the ≤2^31 sanity guard kept fail-closed).
  - Python mirrors of record: `corridor_cargoflow2.py` — wire readback
    compares `self.running_cost != CARGOFLOW2_RUNNING_DISPLAY` (a
    256-scaled raw refuses, message
    "the engine running cost disagrees with its display figure");
    `admit_running_cost(display)` refuses any value off the 421 pin
    (including 107776 — the E111 inversion regression lock — and 0);
    `_day_running_cost` reconstructs the unchanged 8.8 day charge as
    `c256 = display · 256 · rt / (365 · 74)` — integer-identical to
    the core-form billing the E99 window replicated.
  - Funds walk of record unchanged in its numbers: the stub world's
    census returns the display 421 and its independent day-charge
    reimplementation uses the same reconstruction, so every funds
    level of record (485221 → 484774 tail, the two 192 monthly fees,
    the exact 8.8 whole rows) still proves the model↔stub agreement.
  - Regression locks of record: readback refusal rows for
    `running_cost = 107776` (would have admitted under the old
    `(raw >> 8)` arithmetic) and `420`; funds-model refusal cases
    107776/0 with the 421 acceptance; the native byte-level lock
    (`(raw >> 8)` absent, `display != this.RUNNING_DISPLAY_PIN`
    present) — 1 new test in `tests/test_corridor_cargoflow2_native.py`
    plus one extra refusal param row in
    `tests/test_corridor_cargoflow2.py`.
  - Design doc §4 corrected by a clearly marked correction bullet
    (E111/T-009, the original inverted-premise bullet preserved).
  - Offline validation of record: `tests/test_corridor_cargoflow2.py`
    + `tests/test_corridor_cargoflow2_vm.py` → 88 passed (exit 0);
    `tests/test_corridor_cargoflow2_native.py` → 38 passed (exit 0);
    `ruff check` and `uvx ty check` on the touched paths → "All checks
    passed!"; `git diff --check` clean; `CONTEXT.md` pin
    `36648f9c2fee4106` intact; consumed candidates 1–2 byte-untouched;
    nothing staged, signed, claimed, launched or committed.
  - Next gate: round-3 staging (T-002 round 3), each its own explicit
    operator approval; nothing scheduled.
- 2026-11-05 — the Phase A tail spec of record published (`ready-for-agent`):
  [docs/specs/d5-corridor-poc-tail.md](../specs/d5-corridor-poc-tail.md) —
  the round-3 corrected attempt lifecycle (T-002/T-003/T-004/T-005 round 3),
  the delivered class (T-006), the M8 block (T-020), P07 + funds taxonomy
  (T-021) and the PoC completion declaration (T-022) specified in one
  contract. Tracker rows unchanged (the gates are already ticketed above);
  the spec adds the two-route admission semantics, the selection-artifact
  requirement, the funds-taxonomy/ADR requirement, the reporting-closure
  content and the corrective-loop semantics, each bound to the four
  existing test seams (replay verifier, funds fence, VM package suite,
  wire-to-Nut byte bindings) with zero new seams. Out of scope: Phase B,
  Phase C, executable terrain, evidence regeneration, commit authority.
  Nothing scheduled; every gate remains its own explicit operator approval.
- 2026-11-05 — the Phase A tail spec broken into 13 agent-executable tickets
  (tracer-bullet slices with blocking edges, approved under the to-tickets
  interview; granularity and edges confirmed by the operator) and published
  to the local tracker directory `.scratch/d5-corridor-poc-tail/issues/`
  (files 01–13, one per ticket, `ready-for-agent` each):
  01 round3-staging; 02 round3-independent-review; 03 round3-gate-c-signing;
  04 round3-one-launch; 05 halt-class-loop (conditional arm);
  06 delivered-class-reconciliation; 07 route-admission-contract-prefactor
  (expand-only, parallelizable); 08 second-route-admission; 09
  selection-of-record-m8; 10 selected-route-delivered-attempt; 11
  funds-taxonomy-adr; 12 p07-replay-closure; 13 poc-completion-declaration.
  Frontier of record today: 01 (round-3 staging, operator staging approval
  in-session) and 07 (prefactor, no approvals needed). The PoC backlog rows
  above remain the authority of record for live status; .scratch tickets are
  the execution view. Every ticket re-states the standing operator gates it
  must never bypass; no commit/push inside any ticket (commit authority is
  a separate staging-allowlist decision, DG-10).
- 2026-11-05 — T-002 round 3 STAGED (ticket 01 of `.scratch/
  d5-corridor-poc-tail/issues/01-round3-staging.md`, explicit operator
  staging approval in-session, one `prepare` first attempt):
  pipeline round-identity advance of record — `CARGOFLOW2_CANDIDATE_DIRECTORY`
  advanced `candidate-2` → `candidate-3` (comment of record: the T-009 fix
  cycle; candidates 1–2 sealed consumed history, never reused); that one
  constant is the ONLY pipeline edit; focused suites on the edited module
  re-run green (wire 77 + VM 11 + native 38 = **126 passed**, exit 0);
  `ruff check` clean; `uvx ty check` on the module → only the pre-existing
  disclosed `invalid-method-override` at `connect` (line 1176, untouched).
  ONE `prepare` (env of record: `OPENTTD_BINARY` + `OPENTTD_OPENGFX_ARCHIVE`
  exported before Python start) → `PRELAUNCH PASS` exit 0 first attempt:
  candidate of record `artifacts/experiments/d5-corridor-cargoflow2-
  native-candidate-3`, seal (`PRELAUNCH.json` sha256)
  `42f6bbafc19b12a059ff40d18a1e39e7232f525e909ccb179a1a6966e048e41d`
  — differs from both consumed predecessors (`c7a1c5d5…333b`,
  `f991a440…55d4e`); schema `d5-cargoflow2-prelaunch-v1`, kind `cargoflow2`,
  attempt `D5-CARGOFLOW-2`, milestone `D5-CARGOFLOW`; binary pin
  `276d5b69…904c`; ports game 48895 / admin 53133 (fresh allocation);
  workspace `isolated/openttd-15.3-i529afe4`; plan digest `5c0998f2…bf2d`
  (the corridor route of record unchanged); world block pinned on the
  depot-mutation-3 after-save `183b2027…6a6`
  (PREREQUISITE_ATTEMPT_SOURCE_SAVE_LOAD lineage); budgets byte-identical
  the round-2 plan (requests 32 / launches 1 / retries 0 / reconnects 0 /
  funds 489,650 / max_cost 5,000 / 25 planned exchanges / 60-day authority).
  `FIX-CARRY PROOF:` the staged
  `isolated/openttd-15.3-i529afe4/game/RoadFreightProof/main.nut`
  is byte-equal the live shipped package source, contains the T-007
  `SetCurrentRoadType` re-pin AND the T-009 `display !=
  this.RUNNING_DISPLAY_PIN` census join, and contains no `(raw >> 8)` —
  a genuinely new composition, not a relabel. Read-only gates of record:
  standalone `preflight` → `PREFLIGHT PASS` exit 0; pre-auth `verify` →
  `{"authorization_state": "CLAIM_ABSENT", "verification":
  "AUTHORIZATION_UNVERIFIED"}` exit 1 by design. Candidates 1–2 seals
  re-digested byte-identical after the round; no `artifacts/` byte changed
  anywhere else; writes confined to the fresh candidate-3 directory; root
  exactly the pre-gate family shape (4 entries). Nothing signed, claimed
  or launched beyond the books-commit of record (`ad59821`). NEXT: ticket
  02 independent read-only review (operator approval), then Gate C (03)
  and the ONE launch (04), each its own explicit operator approval;
  nothing scheduled.
- 2026-11-05 — T-009-cycle ticket 07 DONE (route-admission contract
  parameterization, expand-only; ticket `.scratch/d5-corridor-poc-tail/
  issues/07-route-admission-contract-prefactor.md`): the corridor attempt
  contract (`app/simulation/openttd/corridor_cargoflow2.py`) now carries the
  versioned route-binding family of record — `Cargoflow2RouteBinding`
  (versioned id `1|2`, fail-closed self-coherence), `CARGOFLOW2_ROUTE_
  BINDINGS` map + `cargoflow2_route_binding()` selector (v1 = the corridor
  route of record, DEFAULT) + `cargoflow2_register_route_binding()` (an
  occupied id refuses; a registered binding is history of record) — with
  binding-derived `cargoflow2_schedule_rows()` (equality-gated ladder of
  record), `cargoflow2_pin_table()` (the binding's own pins, byte-equal at
  v1: RUNNING_DISPLAY_PIN 421 et al.), `cargoflow2_plan(binding=)` (v1
  digest-of-record `5c0998f2…bf2d` unchanged; cross-version composition
  drift refuses fail-closed), and the funds-model wiring parameterized
  (`cargoflow2_funds_model(binding)`: a model carries its binding's own
  founding pins and admits only its own census display figure 421 / its
  binding's own — a cross-version wiring mix refuses, in either direction;
  the §4.3 8.8 carry arithmetic is untouched, the E111 display-pin-in /
  `(raw >> 8)`-out fence stays byte-locked). IMPLEMENTATION RECOVERY NOTE:
  the implementer subagent died on a provider free-usage limit mid-flight;
  its uncommitted worktree work was recovered inline and completed in-session
  (factory + per-instance display pin + `route_version` Literal typing,
  UP037 unquote on 3.14 deferred annotations, ty `--python` env resolution
  in the worktree). Tests insert-only, no existing test edited: wire +6,
  native +1 → **133 passed** (83 wire + 11 VM + 39 native, exit 0);
  `ruff check` clean; `uvx ty check` clean. Git of record: one commit on
  branch `route-contract-prefactor` (`e177d03`, the commit was made
  branchless on a detached worktree HEAD and the branch was named after —
  no history rewritten), merged `--no-ff` into `miles/fright-delivery` as
  `26568af`; no push. Post-merge mainline verification: 133/133 exit 0,
  ruff clean, ty clean; `git diff --check` clean; `CONTEXT.md` pin
  `36648f9c2fee4106` intact. No candidate lifecycle action of any kind in
  this ticket; no artifacts write; the round-3 stamped pipeline constant
  and candidate-3 staging state are untouched. NEXT unblocked: ticket 08
  (second-route admission) is machinery-unblocked by this prefactor but
  remains gated behind the round-3 ladder (02 review → 03 Gate C → 04
  launch → 05 halt-class → 06 delivered class) in dependency order.
- 2026-11-05 — T-002-cycle ticket 02 REVIEWED — verdict **REVIEW-FINDINGS**
  (45/46 re-derivation checks PASS, 1 FAIL, exits 0; ticket
  `.scratch/d5-corridor-poc-tail/issues/02-round3-independent-review.md`),
  fresh-context audit per the round-2 review-of-record method (the old
  candidate-bound script never reused): fresh script
  `/tmp/opencode/t002_r3_review_cargoflow2_c3.py`, transcript
  `/tmp/opencode/t002_r3_review_output.txt` (both outside the repo tree;
  reads only; no write inside the repo; no staging rerun; no signing; no
  claim; no launch). CLASSES: A identity/seal/structure — seal
  `42f6bbaf…e41d` == sidecar == books, 4-entry root, PENDING authorization,
  workspace `openttd-15.3-i529afe4` (checks 1–8 PASS); B correspondence —
  staged `main.nut` == live T-007+T-009 source bytes, the fix-carry class
  (single re-pin once, the T-009 census join `display !=
  this.RUNNING_DISPLAY_PIN` sited after its read, `RUNNING_DISPLAY_PIN`
  exactly 2, NO second shift), `info.nut` == frozen zip, staged AI ==
  package bytes, inventory main digest == staged bytes, staged main digest
  differs from BOTH sealed predecessor main digests, no run residue
  (checks 9–15 PASS); C lineage — binary pin, argv pins, no openttd
  process, `source.sav` == depot-3 after-save `183b2027…6a6`, world
  lineage, welcome identity, OpenGFX identity, save-restore GS identity
  (16–23 PASS); D pins/plan re-derivation — budgets byte-equal round-2,
  pin table, schedule of record 25, ladder schema, hypotheses bound to
  consumed probe receipt + recomputed digest, funds pins, plan digest
  re-derived == recorded `5c0998f2…bf2d`, plan model digest re-derived
  through the ticket-07 parameterized composition guard, guard protocol
  11, secret excluded + mode 0600 (24–36 PASS); E re-execution —
  verify pre-auth `CLAIM_ABSENT` exit 1 still exact (38–39 PASS);
  37 FAIL (finding below); F environment/ports (40–41 PASS); G
  immutability — no run leftovers, no post-run shape, candidate-1 AND
  candidate-2 AND candidate-3 seals re-digested byte-identical at the
  audit's end (42–46 PASS — the candidate of record is untouched).
  **FINDING (check 37, the reconciliation debt of record):** the
  production freeze gate refuses preflight re-execution — the staged
  frozen inventory pins
  `app/simulation/openttd/corridor_cargoflow2.py` at its staging-time
  bytes `d72d1762…7c2`, while the merged ticket-07 parameterization
  changed the live file to `477732f0…06f`; the mismatch set is exactly
  ONE of 3502 entries. Root class: a sequencing artifact — candidate-3
  was composed from pre-07 source (ticket 01 staging ran before the
  ticket-07 merge in the same round), and ticket 07's later merge moved
  the live contract bytes; preflight refusal is the by-design fail-closed
  gate doing its job. Consequence: candidate-3 cannot be Gate-C-signed in
  this state; Gate C and launch on candidate-3 are OFF the menu. Script
  side incidents, self-caught and disclosed: audit check 12 went through
  two iteration fixes (name-set assertion shape) — no staged defect
  (staged AI bytes verified directly byte-equal live in the diagnostic);
  the merged script's final run is the transcript of record. Verdict
  RECONCILIATION-DEBT: a fresh T-002 round must stage a new candidate
  (fresh identity, composed from the post-07 source — ticket-07's own
  same-digest guarantee was proven live: plan digest re-derivation checks
  32–33 reconcile byte-equal against the recorded `5c0998f2…bf2d`), then
  that candidate re-reviews (this ticket's method), then Gate C, then the
  ONE launch. Operator decision pending.
- 2026-11-05 — T-002 round 4 STAGED (the reconciliation round of record;
  ticket `01-round4-restage.md` in `.scratch/d5-corridor-poc-tail/issues/`,
  explicit operator re-stage approval in-session, one `prepare` first
  attempt): round identity advanced `candidate-3` → `candidate-4`
  (comment of record: reconciliation of the round-3 review finding —
  candidates 1–3 sealed consumed/unfulfillable history, never reused);
  that one constant is the ONLY pipeline edit; focused suites re-run
  green (83 + 11 + 39 = **133 passed**, exit 0), `ruff check` clean. ONE
  `prepare` → `PRELAUNCH PASS` exit 0 first attempt. **RECONCILIATION
  PROOF:** candidate-4's frozen inventory pins
  `app/simulation/openttd/corridor_cargoflow2.py` at the post-07 live
  bytes `477732f0…06f` — the exact single entry that refused the round-3
  candidate; all 3502 entries reconcile on the live tree; the round-3
  debt is discharged by construction. Candidate of record
  `artifacts/experiments/d5-corridor-cargoflow2-native-candidate-4`,
  seal (PRELAUNCH.json sha256)
  `325910c3a4df325408fbb859b251a587232638d9abac73312bd502c793377c9f`
  — differs from all three predecessors (`c7a1c5d5…333b`,
  `f991a440…55d4e`, `42f6bbaf…e41d`); schema `d5-cargoflow2-prelaunch-v1`,
  kind `cargoflow2`, attempt `D5-CARGOFLOW-2`, milestone `D5-CARGOFLOW`;
  plan digest `5c0998f2…bf2d` UNCHANGED of the corridor route of record
  (ticket-07 default-binding invariance held end-to-end through the
  parameterized composition), plan model digest `98d055c4…96f`, schedule
  version 1, ladder grid `d5-cargoflow2-ladder-grid-v1`, world lineage
  depot-mutation-3 after-save `183b2027…6a6`
  (`PREREQUISITE_ATTEMPT_SOURCE_SAVE_LOAD`), save-restore GS identity
  present (`NetworkFreightProof`), budgets byte-equal the of-record plan
  (funds 489,650 / max_cost 5,000 / 25 planned exchanges / 60-day
  authority); ports game 37155 / admin 36957 (fresh allocation), workspace
  `isolated/openttd-15.3-9__6eu5v`; root exactly the pre-gate family shape
  (4 entries). Read-only gates of record: standalone `preflight` →
  `PREFLIGHT PASS` exit 0; pre-auth `verify` →
  `{"authorization_state": "CLAIM_ABSENT", "verification":
  "AUTHORIZATION_UNVERIFIED"}` exit 1 by design. Candidates 1–3 seals
  re-digested byte-identical after the round; no `artifacts/` byte
  changed anywhere else; writes confined to the fresh candidate-4
  directory. Nothing signed, claimed or launched. NEXT: round-4
  independent review (ticket 02's method applies fresh, fresh-context,
  new ticket file of record), then Gate C (03 class), then the ONE
  launch (04 class) — each its own explicit operator approval.
- 2026-11-05 — CORRECTION OF RECORD (append-only; candidate-4 of the
  preceding row is now **seal-superseded**): after the round-4 staging
  row was written, the in-session model/domain work continued — the
  shared-language append to the root `CONTEXT.md` (six corridor terms:
  route binding / expand-only parameterization / staged candidate /
  freeze pin / seal / reconciliation debt), the
  `cargoflow2_register_route_binding` docstring rewording
  (plan-version-scoped truth per the code-review finding), and the
  candidate-lineage comment rewording. The candidate-4 freeze inventory
  pins all three files, and its live digest now disagrees for all three
  (three freeze-pin mismatches — the loop-class of candidate-3's debt,
  introduced by post-staging writes again). No signing, claim, launch,
  artifact write or code-data change happened anywhere; the round-4 seal
  stays on disk byte-exact (`325910c3…c9f`); candidates 1–3 stay sealed;
  the round-3 REVIEW-FINDINGS verdict keeps standing. The method of
  record stands: the write cluster completes to its final text, then the
  NEXT fresh staging round (candidate-5: one advance of the round
  identity + ONE `prepare`, a single operator-approved action) composes
  from the settled tree, and the fresh candidate re-reviews fresh.
  Discipline note of record: model/doc writes and stage freezes do not
  interleave — a staged round forbids any write inside a pinned source
  until its gates close or a fresh round supersedes it.
- 2026-11-05 — CODE-REVIEW CORRECTION ROW (append-only; the "no push"
  bookkeeping of record): the two-axis code review of `ad59821...HEAD`
  (2026-11-05) surfaced that `e177d03` and `2e5782f` rest on
  `origin/miles/fright-delivery` while several ticket rows and commit
  messages say "no push". Operator fact of record, given in-session:
  **the operator pushed those two commits manually, outside every agent
  session; no agent-run push subcommand exists.** The books' "no push"
  phrasing was written from the agent-session view and is NOT corrected
  retroactively — the rows stand as written (no relabel); this row adds
  the operator-side fact that must accompany them. The operator-side
  pushes were legitimate operator-authorized acts; commit authority stays
  the operator's, and agent sessions of record never push.
- 2026-11-05 — T-002 round 5 STAGED (the settled-tree round of record;
  ticket `.scratch/d5-corridor-poc-tail/issues/01-round5-stage.md`,
  grilling-round sanctioned, operator-approved as a single action, ONE
  `prepare` first attempt): identity advance `candidate-4` → `candidate-5`
  (only pipeline edit; lineage comment corrected to final truth), focused
  suites 133 exit 0, ruff clean. `PRELAUNCH PASS` exit 0. Candidate of
  record `artifacts/experiments/d5-corridor-cargoflow2-native-candidate-5`,
  seal (`PRELAUNCH.json` sha256)
  `d4715fd3b2d0a9f5be831dfcd9f80188a87ef6460173a55763a2ee2457537741` —
  differs from all four predecessors; **ZERO freeze-pin mismatches across
  all 3502 sealed entries** — the first fully-reconciling staging of the
  cycle; plan digest `5c0998f2…bf2d` UNCHANGED; workspace
  `isolated/openttd-15.3-7wet880f`; ports 41129/53847; root 4 entries;
  standalone `preflight` → `PREFLIGHT PASS`; pre-auth `verify` →
  `CLAIM_ABSENT` exit 1 by design; candidates 1–4 seals re-digested
  byte-identical; nothing signed, claimed or launched; no `artifacts/`
  byte touched outside the fresh candidate-5 directory. Legacy note: the
  selector-2 authority transition was sanctioned and landed BEFORE
  staging (`docs/authority/context-authority-supersession.json` binds the
  historical anchor `b94b9664…` → current `343daad2…caf`, reason carries
  the b94b9664 → 36648f9c → 343daad2 evolution chain; 44 authority
  assertions green) and the write cluster was committed `80ff619` (13
  files) BEFORE staging — commit then stage, the settle-then-freeze order
  of record; no push (agent side). NEXT: round-5 independent review
  (fresh-context, ticket 02's method), then Gate C signing, then the ONE
  launch — each its own explicit operator approval.
- 2026-11-05 — T-002 round-5 INDEPENDENT REVIEW: verdict
  `READY-FOR-GATE-C` — **50/50 checks PASS, zero failures, zero
  reconciliation debt, exit 0**; fresh-context read-only audit cloning
  ticket-02's round-3 method (classes A identity/seal, B staged
  correspondence + fix-carry, C binary/opengfx/world lineage, D
  pins/budgets/plan re-derivation, E pipeline re-execution, F env/ports,
  G no-leftovers + predecessor immutability) re-pinned to candidate-5
  facts, plus new H class (authority-of-record); script
  `/tmp/opencode/t002_r5_review_cargoflow2_c5.py`, full transcript
  `/tmp/opencode/t002_r5_review_output.txt`; preflight re-execution PASS
  with **0 of 3502 frozen-inventory mismatches** (check 37); candidates
  1–4 seals re-digested byte-identical (checks 44–47); candidate-5 seal
  unchanged after the audit (check 48); authority-of-record re-asserted
  (checks 49–50: supersession record binds the `b94b9664…` historical
  anchor → `343daad2…caf` current, live `CONTEXT.md` digest == the
  recorded current). INFO lineage fact of record: the staged
  `d5_cargoflow2_package/main.nut` digest
  `948f3b483e2b705b78cc775c1e75966654a4aa4854bea78b811566fb705d571b` is
  byte-equal across candidates 3–4–5 — the ticket-07 default-binding
  composition equality held through two staging rounds. Ticket of
  record: `.scratch/d5-corridor-poc-tail/issues/02-round5-independent-review.md`.
  Nothing written inside the repo by the reviewer; nothing signed,
  claimed or launched. NEXT: Gate C signing (operator PEM) in a separate
  explicit approval, then the ONE launch in its own approval.
- 2026-11-05 — T-004 round-5 Gate C Option-1 signing executed under
  explicit operator approval (signing only; ONE signing operation +
  read-only verification; stop before T-005; no claim, no launch, no
  reconnection, no consumption, no historical evidence modification, no
  Git mutations):
  - Pre-write identity + seal re-verification of record (the fresh
    round-5 signer script `/tmp/opencode/t004_gate_c_cargoflow2_c5.sh`,
    transcript `/tmp/opencode/t004_gate_c_cargoflow2_c5_output.txt`,
    per-round re-derivation on the E109/E99 signer precedent; the
    candidate-1/2-bound scripts never reused): gate surface absent
    (AUTHORIZATION.json/CLAIM.json/LAUNCH-CONSUMED.json/receipt.json/
    result.json/runtime-identity.json), live seal == sidecar == the
    operator-approved seal of record
    `d4715fd3b2d0a9f5be831dfcd9f80188a87ef6460173a55763a2ee2457537741`
    (hard-asserted twice in the script, incl. the exact candidate-5
    approval constant).
  - Seed mechanics identical to E109/E99: memory-only extraction from
    the operator-held PEM outside the repository (48-byte PKCS#8 DER,
    final-32-bytes window of record), env-only `CARGOFLOW_GATE_SEED`,
    never printed/filed/argument-passed; pre-write identity asserted
    (`public_from_seed(seed)` == pinned anchor
    `5063982bd28d…880f`); env unset + printenv-empty verified after.
    Operator PEM contents never read beyond the DER-body parse.
  - Production signing surface only: `authorization_payload(metadata,
    seal)` + `canonical_authorization_bytes` + `sign_authorization_record`
    + `write_authorization_record` + `verify_authorization`; payload
    digest of record
    `aa936f19498971f549e6906a30d852882e0b8a5ea9c5da13a5a6257b4e518d25`
    cross-checked == production
    `staged_cargoflow2_authorization_payload_digest(candidate-5)`;
    `AUTHORIZATION.json` record digest
    `57284ae0fd812f20e0152bc175f486230ba0f02b9c7c8df8acc8ff931382b01e`;
    operator identity unchanged
    `sha256-ed25519-public-key:cbb63ff58f17f13df3e1be0735fad18497e3a0c6ad6b5dd55491d708ae40c614`.
  - Post-write read-only state of record: root = 5 entries
    (`AUTHORIZATION.json` joins `PRELAUNCH.json`/`PRELAUNCH.sha256`/
    `graphics-identity.json`/`isolated/`; no CLAIM.json, no
    LAUNCH-CONSUMED.json); seal `d4715fd3…41ad` byte-equal after the
    write; `preflight` PASS with the authorization present; standalone
    pre-launch `verify` → `AUTHORIZATION_UNVERIFIED` / `CLAIM_ABSENT`
    exit 1 as designed.
  - Zero staged defects, zero re-writes: the signing completed first
    invocation with no auxiliary incident; candidates 1–4 re-digested
    byte-identical; no candidate bytes beyond AUTHORIZATION.json
    touched; the PRELAUNCH seal re-verified post-write.
  - NEXT (T-005 round 5, needs its own explicit operator approval): ONE
    launch of the signed candidate-5 at the pinned binary/OpenGFX
    versions + read-only replay + integrity sweep + certified cleanup;
    nothing scheduled, nothing relaunched.
- 2026-11-05 — T-005 round-5 launch gate executed under explicit
  operator approval (exactly ONE native launch of candidate-5 + read-only
  replay + integrity sweep + certified cleanup of record; stop after
  final reporting; no retries, no relaunches, no reconnections, no
  source edits, no second attempt, no historical evidence modification,
  no Git mutations):
  - Pre-launch gates re-verified fresh (nothing stale; per-round script
    `/tmp/opencode/t005_r5_prelaunch_gates.sh`, E110 precedent,
    transcript `/tmp/opencode/t005_r5_prelaunch_gates_output.txt`): no
    openttd process; gate surface = exactly the 4 staged entries +
    `AUTHORIZATION.json` (+ `isolated/`), no launch receipts; live seal
    == sidecar == the operator-approved seal of record
    `d4715fd3…41ad`; `verify_authorization` PASS via the production
    surface (record `57284ae0…b01e`, payload `aa936f19…` ==
    `staged_cargoflow2_authorization_payload_digest(candidate-5)`,
    operator identity `sha256-ed25519-public-key:cbb63ff5…40c614`);
    binary file sha256 == pin `276d5b69…904c`; staged `source.sav`
    digest == the world bind `183b2027…efe6a6`; argv pins
    `-D127.0.0.1:41129` / `-c cfg` / `-g source.sav` /
    `-dscript=4,grf=1,net=3`; budgets `launches 1 / retries 0 /
    reconnects 0 / connection_attempts 1`; OpenGFX-8.0 archive present
    → `T-005 R5 PRE-LAUNCH GATES: ALL PASS`, one attempt.
  - Launch command of record (E110/E104 invocation shape), executed
    exactly once with `OPENTTD_BINARY` and `OPENTTD_OPENGFX_ARCHIVE`
    exported before Python starts:
    `.venv/bin/python -m app.simulation.openttd.proof.corridor_cargoflow2_native run /home/fed/codes/softdev2/artifacts/experiments/d5-corridor-cargoflow2-native-candidate-5`
    → **run return code of record: 1** (transcript
    `/tmp/opencode/t005_r5_launch_output.txt`).
  - Run outcome of record (verified terminal in the JSON of record):
    `preflight=PASS`, `native_launches=1` (== budget), `connections=1`
    (== budget), `requests=11`, `command_accepted=true`,
    `state_changed=true`, `verified=false`,
    `status=PHASE_HALTED_PREFIX_PRESERVED`. **10 of 15 exchanges clean:**
    `site-00 READY` (day 712228 tick 15, funds 489650 — funds fence
    intact), **`engine-00 READY` (tick 16 — round-2's
    `ENGINE_PIN_MISMATCH` class did NOT recur; the T-009 census
    display-pin fix and the E111 engine fix both measured live-true on
    this composition)**, `purchase-00 BUILT` (tick 18, funds 485221 —
    purchase cost 4,429 under the 5,000 max-cost fence), `vread-00
    READ`, `order-00`/`order-01 ORDERED`, `order-read-00
    ORDER_SET_VERIFIED`, `monitor-00 ARMED`, `start-00 STARTED`,
    `vread-01 READ`. Halt of record at `arrive-00` (status ANCHORED,
    world state `HALTED_BEFORE_MUTATION`):
    `ValueError: the delivery exchange arrive-00 failed verification:
    cargo-flow 2 funds diverged from the modeled trajectory: arrive-00
    observed 485217, modeled 485216, residual 1`; phase verdict
    `CARGOFLOW2_GATE_UNDECIDED_INCOMPLETE`, verification
    `CARGOFLOW2_INCOMPLETE`. The halt class is terminal; no diagnosis
    without a new approval (recording the class is all T-005 claimed);
    the consumed identity is never relaunched.
  - Read-only replay of record, executed once: `verify` →
    `{"verification":"PHASE_HALTED_EVIDENCE_PRESERVED","failed":
    {"label":"arrive-00","status":"ANCHORED",
    "world_state":"HALTED_BEFORE_MUTATION",…}, "exchanges":[site-00 …
    vread-01] (10), "result_status":"PHASE_HALTED_PREFIX_PRESERVED"}`,
    **exit 1** (transcript `/tmp/opencode/t005_r5_replay_output.txt`)
    — the replay verdict reconciles the run verdict exactly; consumed
    identity never relaunched.
  - Post-run read-only state of record (transcript
    `/tmp/opencode/t005_r5_postrun_sweep_output.txt`): root = 38 files
    + `isolated/` (empty shell, workspace_disposed=true; richer
    retention than round-2's 20-file shape, manifest covers 37);
    `LAUNCH-CONSUMED.json` binds authorization record `57284ae0…b01e` +
    seal `d4715fd3…41ad` + operator identity `cbb63ff5…40c614` (schema
    `d5-native-launch-consumed`); `CLAIM.json` `consumed=true /
    launches_allowed=1 / retries=0`; certified cleanup of record
    `reaped=true / sockets_closed=true / workspace_disposed=true /
    credential_removed=true`, `cleanup_error=[]`,
    `remaining_processes=[]`, `returncode=0`; `artifact-manifest.sha256`
    re-verified 37/37 OK, 0 non-OK; `PRELAUNCH.json` seal byte-equal +
    sidecar after the run; post-run process check: no openttd process.
  - Integrity close of record: `git diff --check` clean; `CONTEXT.md`
    pin intact; candidates 1–4 re-digested byte-identical; no source
    edits; no ticket restructuring; nothing scheduled — any
    funds-divergence fix round (fresh candidate round identity +
    explicit operator approval only) starts from T-002 staging. NEXT
    (needs operator task direction): ticket 05 (halt-class loop) or
    06 (delivered-class) bookkeeping per this verdict; the arrive-00
    funds-residual-1 question is a fresh diagnostic-first candidate
    frame.
- 2026-11-05 — TICKET 05 (halt-class loop, round-5 arm) DIAGNOSIS-OF-RECORD
  EXECUTED READ-ONLY (E112; grilling round-1 task direction, Q2
  diagnosis-first; zero source edits, zero test edits, zero candidate
  lifecycle actions, zero launches, no commit yet): the arrive-00
  `CARGOFLOW2_FUNDS_DIVERGED` halt class forensically closed on preserved
  evidence only. Emitter of record traced exactly (two levels): the
  zero-residual fence itself (`Cargoflow2FundsModel.reconcile`
  `corridor_cargoflow2.py:1599-1617`) + the runner fail-closed wrap
  (`proof/corridor_cargoflow2_native.py:1572`) composing the recorded
  `result.json` halt.error verbatim. Production replay of record
  (script `/tmp/opencode/t005_r5_diag_arrive00.py` + transcript
  `t005_r5_diag_arrive00_output.txt`, exit 0): the retained wire bytes
  re-parse through the production Contract schemas (JSON mode), the
  production prefix verify (`cargoflow2_phase_outcome`, exchanges[0:10],
  seal `d4715fd3…41ad`) reproduces the retained `result.json` phase
  outcome **full-field**, the same per-step verify of record re-entered
  across all 11 exchanges reproduces the verbatim halt ValueError, and
  the pre-arrive funds-model witness (`income_deltas` 10 rows in
  `plan.schedule` order, `running_cost 421`, `running_costs []`)
  reproduces exactly. **Root cause (CONFIRMED, high, source level): the
  fence's day-charge walk diverges from the observed 4-debit native class
  at three term level** — (1) model-only start-day partial charge
  (rt = 74−27 = 47 → whole 1; native charged nothing before its first
  rollover tick 48), (2) model-only day-230 borrow bonus
  (`new_fraction = (fraction − low) % 256` books whole 2 on day-230 from
  fraction 30 < low 39; class level charges 1 per boundary), (3)
  class-only in-window day-232 rollover debit (native clock law
  `date = 712229 + floor((tick − 48)/74)` fits all 7 probe pairs + the
  arrive-00 instant; day-232 onset tick 270 ≤ read tick 292 while the
  walk books `range(prev_day, day)`). Closure: modeled 5 debits
  (489650 − 4429 − 5 = 485216) vs observed 4 (485217): 5 − 4 == 2 − 1 ==
  residual +1. Native-internal mechanism kept UNKNOWN per the E111
  discipline: (A) flat 1-coin-per-rollover with internal fractional
  retention (boundary set {48, 122, 196, 270}) and (B) scalar cumulative
  `floor(421·elapsed/(365·74))` (crossings {92, 156, 220, 284}) each
  reproduce all 11 retained instants exactly; `OpenTTD-Knowledge` carries
  no billing semantics (greps empty) and the binary disasm was out of
  scope — the fix round targets the observed trajectory class, not an
  asserted internal policy. No other terms (no month boundary in-window —
  next 712254; income 0 at every read; purchase whole-unit). Round-5
  verdicts untouched; candidate-5 stays consumed terminal history.
  Ticket `.scratch/d5-corridor-poc-tail/issues/05-halt-class-loop.md`
  boxes updated (diagnosis complete; cards block written; offline fix
  still open). NEXT: offline fix-of-record needs its own explicit
  operator direction (align the walk to the observed 4-debit class; no
  wire/fail-closed loosening; regression locks the whole class needs),
  then settle-then-freeze doc/vocabulary writes, then round-6 re-entry —
  fresh candidate identity `candidate-6` + ONE prepare, fresh review,
  Gate C, ONE launch, each gate separately approved.
- 2026-11-05 — TICKET 05 (halt-class loop, round-5 arm) 15.3 SOURCE
  PIN BOOKED (read-only, evidence E113; explicit operator approval
  "Approve all / Agree all" for the pin round + booking write): the
  operator chose "Pin via 15.3 source" to resolve E112's H4
  mechanism UNKNOWN. Provenance closed first: `roadveh_cmd.cpp` sha
  `d53206f2…467c8` and `vehicle_base.h` sha `3170cf99…4287` re-fetch
  byte-equal the retained E111 fetches (the retained bytes are true
  tag-15.3 upstream), and the remaining kernel files were fetched
  fresh (`company_cmd.cpp`, `vehicle.cpp`, `openttd.cpp`,
  `timer_game_economy.cpp`, `company_base.h` — full shas in the
  transcript). Script of record `/tmp/opencode/t005_r5_source_pin.py`
  + wrapper `t005_r5_source_pin.sh` + transcript
  `t005_r5_source_pin_output.txt` (exit 0, 0 failures across V1a–V6,
  tree clean, candidate-5 manifest re-verified 37/37). **One billing
  mechanism of record, all verbatim in-code**: charges fire in
  `RoadVehicle::OnNewEconomyDay` (`roadveh_cmd.cpp:1728-1752`,
  `running_ticks == 0` gate → `cost = GetRunningCost()·rt//(365·74)`
  in raw 256ths → `running_ticks = 0` → `SubtractMoneyFromCompanyFract`),
  dispatched by the spread day-proc (`vehicle.cpp:921-950`,
  `index % 74 == date_fract`, source comment "not in the first tick
  of the day") after economy `Elapsed` (`openttd.cpp:1264-1267`;
  `timer_game_economy.cpp:131-136` `date_fract++`, roll resets 0 +
  `date++`) — vehicle 1 charges on the tick after its day's roll:
  **events at `T0+1+74k`**. The kernel (`company_cmd.cpp:324-336`):
  one `uint8_t money_fraction` (`company_base.h:85`) subtracts the
  charge's low byte with uint8 wrap, a wrap lends one whole coin,
  `whole == 0` debits silently nothing; money scale display = raw >> 8
  (`vehicle_base.h:566`): 421 ⇒ raw 107776 ⇒ full day 295 raw = 1
  whole + 39 frac (the fence's 8.8 algebra exactly, proved rt 1..74).
  **The source walk (V2, T0=48) reproduces the observed class
  exactly**: rt at the first event = ticks 28..48 = 21 (unstop latch
  28; rt==0 events fully silent, consuming no reset), consumed rt
  ledger [21, 74, 74, 74], whole debits [1, 1, 1, 1] (first is a pure
  borrow), fraction trail [173, 134, 95, 56], funds 485217 — predicting
  **all 11 retained instants exactly**; robust at rt_first
  {20, 21, 22} and across the T0 sweep [18..48] (31/31 anchors, 4
  debits each). **Model-of-record repro (V5)**: the production
  `Cargoflow2FundsModel` walk rebuilt in-code reproduces the ledger
  [(712228, 47, 1), (712229, 74, 1), (712230, 74, 2), (712231, 74, 1)],
  funds 485216, end fraction 208, and raises the retained halt
  BYTE-VERBATIM at the arrive-00 reconcile; index-paired deltas
  [0, 0, 1, 0] — the single delta is the model's day-712230 row
  booking whole 2 vs the source event's 1, caused by the start-day rt
  frame 74−27 = 47 vs the true 21 (74−T0 = 26 ticks late, shifting the
  fraction phase so that row borrows early). **H4 A/B superseded**:
  the true lattice {T0+1+74k} is neither A's {48,122,196,270} (one
  tick early) nor B's {92,156,220,284}; amounts are per-event raw·rt
  with fraction continuity, not flat-1 (later real borrow events debit
  2 — horizon [419, 937, 1381, 1899, 2343, 2861, 3305, 3823], period
  74·7). H1/H2 refined (start-day partial is source-true inside
  day-712229's event; the borrow kernel is genuine and the model's
  `whole 2` is the same borrow at a phase-shifted frame); H3 confirmed
  (in-window day-712232 event, tick 271, is a real fourth debit the
  model never books while a phantom day-712228 row exists). Fix
  direction now source-precise: the funds-model day-walk moves to the
  charge-event frame (kernel arithmetic unchanged; regression locks
  the whole class needs — the pre-fix walk must fail the observed
  class's fences). Round-5 verdicts untouched; candidate-5 stays
  consumed terminal history; no test suite executed (nothing
  code-touched). NEXT: offline fix-of-record needs its own explicit
  operator approval (rewrite `corridor_cargoflow2.py`'s funds-model
  day-walk to the charge-event frame with the failing-regression lock
  first), then settle-then-freeze doc/vocabulary writes (spec §4.3
  wording, CONTEXT.md rows via authority transition 3, AI_HANDOFF
  refresh) committed BEFORE round-6's identity advance, then the
  round-6 gate ladder — `candidate-5` → `candidate-6` + ONE prepare,
  fresh review, Gate C, ONE launch, each gate separately approved.
- 2026-11-05 — TICKET 05 (halt-class loop, round-5 arm) OFFLINE FIX OF
  RECORD EXECUTED UNDER EXPLICIT OPERATOR APPROVAL ("resume ticket 05
  to next ticket"), evidence E114: the funds model's day-charge walk
  moved to the E113 charge-event frame — failing-regression lock first:
  `test_funds_model_charge_event_walk_candidate5_class` (candidate-5's
  own 11-instant corridor grid, arrive-00 reconcile `observed=485217`
  residual 0, running rows [(712229, 21, 1), (712230, 74, 1), (712231,
  74, 1), (712232, 74, 1)]) ran pre-fix RED (transcript
  `/tmp/opencode/t005_r6_lock_prefix_output.txt`, exit 1, `assert
  485221 == 485217` — the pre-fix walk charged nothing before
  arrive-00) then GREEN post-fix (transcript
  `/tmp/opencode/t005_r6_lock_postfix_output.txt`, exit 0). The fix
  (`app/simulation/openttd/corridor_cargoflow2.py`, funds model only;
  proviso kept: no wire/fail-closed gate touched, kernel
  byte-unchanged, `reconcile`'s zero-residual fence unchanged):
  constants `CARGOFLOW2_DAY_ROLL_ANCHOR = 48` +
  `CARGOFLOW2_CHARGE_SLOT = 1` pinned with the §4 guard; walk cursor
  started one lattice step pre-session (tick −25, silent);
  `start_vehicle` seeds the running count at `tick + 1` (no phantom
  start-day row); `advance` bills every lattice event up to the
  observation tick keyed by its own rolled day, gated on
  started-and-admitted (a raw-less advance stays charge-free, E111's
  order preserved), rt = event − count start (latched tick + 1, then
  event-after-each billed), rt ≤ 0 events silent with no state change,
  rows re-keyed `(event_day, rt, whole)`; the backstop guard widened to
  (day, tick) tuple ordering (same-day-tick-backwards arm, raise
  string intact). Toy twin, one law both frames
  (`tests/test_corridor_cargoflow2.py`): `_exchange_tick` walks
  law-consistent instants (base rows keep 30, arrival + flow-00 keep
  40, offset ≥ 1 at `48 + 74·(offset − 1)` in-day 0 — each read
  excludes that day's own event exactly as the stub's `[old_day,
  new_day)` fee loop never bills the crossing day); the Squirrel fee
  engine rewritten to the same law (silent `d ≤ run_start_day`, rt =
  `48 − run_start_tick` on the first charged day, full 74 after);
  `run_probe_vm` pre-shapes each ladder row's window start
  `offset − prev_offset` ticks short of the roll tick so the row's own
  sweep lands the law tick exactly (a first freeze-set attempt was
  rejected by the window's own `CLOCK_STALLED` watchdog — strictly
  increasing ticks is its contract — disclosed in the evidence).
  Re-derived funds figures of record (the walk itself the authority):
  flow-01 485217 (unstop partial rt-first 18 from the latched tick 30),
  flow-02..05 485211/485205/485199/485194, flow-06 484996 (Feb 1),
  flow-07..10 484990/484984/484979/484973, flow-11 484775 (Mar 1), rows
  witnessed flow-01 [(712229, 18, 1), (712230, 74, 1), (712231, 74, 1),
  (712232, 74, 1)], borrow rows [712234, 712241, 712247, 712254,
  712261, 712267, 712274, 712280] (8 borrows across 54 billed events,
  the E113 per-7-days rate; non-monthly whole 62; tail fraction 166;
  probe `/tmp/opencode/t005_r6_walk_probe.txt`);
  `_ACQUISITION_VECTOR_OF_RECORD` re-carried to the walk values. Gates
  green, exit 0: focused suites `tests/test_corridor_cargoflow2.py`
  (84) + `tests/test_corridor_cargoflow2_vm.py` (11) +
  `tests/test_corridor_cargoflow2_native.py` (39 offline) = 134 passed;
  the production-path run of record `test_ladder_of_record_runs_green`
  end-to-end green under the new law; `ruff check` clean on all four
  touched paths; `uvx ty check` clean (0 diagnostics); `git diff
  --check` clean; `CONTEXT.md` pin untouched, round-5 verdicts
  unrelabeled, candidate-5 stays consumed terminal history, no run, no
  staging, no candidate actions. NEXT: settle-then-freeze
  doc/vocabulary writes (spec §4.3 wording, CONTEXT.md rows via
  authority transition 3, AI_HANDOFF refresh) — own approval, BEFORE
  round-6; then the round-6 gate ladder — `candidate-5` →
  `candidate-6` + ONE prepare, fresh review, Gate C, ONE launch, each
  gate separately approved.
- 2026-11-05 — TICKET 05 (halt-class loop, round-5 arm) SETTLE-THEN-FREEZE
  DOC CLUSTER LANDED AND THE TICKET CLOSED, evidence E115, under explicit
  operator approval (grilling round answered "A A A": Q1-A docs gate
  first then closed; Q2-A ONE commit covering the doc-cluster round +
  the close-out; Q3-A the re-entry obligation carried in full by the
  round-6 ladder on tickets 01–04, ticket 05 issues no candidate
  actions). Landed: (1) design record
  `docs/d5-cargoflow-delivery-design-2026-11-04.md` §4.2 item 4 + §4.3
  re-worded to the E113 law of record — charge events at
  `T0 + 1 + 74k` keyed by their own rolled day, the unstop partial
  billed inside the first billed event (count start = latched tick +
  1, every billed event resets after billing), pre-count rt ≤ 0
  events fully silent changing no state, the start day never its own
  billed row, the `SubtractMoneyFromCompanyFract` borrow kernel block
  byte-unchanged; (2) spec of record `docs/specs/d5-corridor-poc-tail.md`
  — funds taxonomy names the charge-event lattice with the uint8-wrap
  borrow kernel unchanged, and the seam-2 funds-fence decision names
  the stub's independent charge-event reimplementation of the same E113
  law with the pinned walk levels re-carried 485221 → 484775 (the E114
  walk; the superseded 484774 never appears again); (3) CONTEXT.md —
  three corridor-vocabulary rows appended to the prepend-only
  shared-language zone with zero earlier bytes changed (**Day-roll
  anchor** — one economy day 74 script ticks, day rolls at tick 48,
  corridor clock `date = 712229 + floor((tick − 48) / 74)`; **Charge
  event** — the vehicle's spread day-proc slot on the first tick after
  its day's roll, billed keyed by its own rolled day, the launch day's
  own event silent pre-unstop; **Unstop count start** — count begins
  one tick after the latched acceptance, each billed event resets
  after billing); authority transition 3 bound the live bytes —
  `docs/authority/context-authority-supersession.json`
  `current_sha256` → `847d710abe87e2ed211a72d6455f3f1326b1476eca1711ab8be900080ec2984d`,
  evolution chain b94b9664 → 36648f9c → 343daad2 → 847d710a… in the
  reason, predecessor byte states reachable as git history, all
  historical freeze manifests frozen and unmodified; (4)
  AI_HANDOFF.md cargo-flow-2 row records the E112→E114 chain, this
  close and the round-6 pointer; ticket-05 status → closed with a
  close-out block; EVIDENCE_INDEX gained the E115 row; this entry
  closes the log's book. Gates of record: `tests/test_authority_supersession.py`
  green post-write (the transition record binds the live bytes),
  `git diff --check` clean, doc-only round (zero source edits, zero
  test edits, no suite run beyond the supersession gate, no run, no
  staging, no candidate actions, historical zones byte-untouched, no
  push). Commit: one — `T005 round-5 ticket-05 settle-then-freeze +
  ticket 05 closed`. Ticket 05's corrective arm is complete end-to-end:
  diagnosis (E112) → source pin (E113) → offline fix (E114) → doc
  freeze + close (E115). NEXT: the re-entry obligation is carried in
  full by the round-6 gate ladder on tickets 01–04 — `candidate-5` →
  `candidate-6` + ONE prepare (staging approval), fresh review
  (ticket 02 method), Gate C signing (ticket 03), ONE launch
  (ticket 04), each gate its own separate explicit operator approval;
  ticket 05 issues no candidate actions and holds none.
- 2026-11-05 — T-001/round-6 STAGE: round-6 gate 1 (staging approval
  in-session, one action) executed and booked on the settled
  post-settle-then-freeze tree — identity advance `candidate-5` →
  `candidate-6` (only pipeline edit; lineage comment of record updated:
  candidates 1–2 consumed with native verdicts, 3–4 seal-superseded by
  freeze-pin debts, candidate-5 consumed terminal history — the
  arrive-00 funds-residual halt class answered by E114/E115; candidate-6
  composes from the current tree, never a relabel); focused suites 134
  exit 0 (84 + 11 + 39), ruff clean, ty = the one frozen-mirror
  `connect` census-baseline diagnostic (untouched region); ONE
  `prepare` → `PRELAUNCH PASS` exit 0 FIRST ATTEMPT — candidate of
  record `artifacts/experiments/d5-corridor-cargoflow2-native-candidate-6`,
  seal `e929d7b2e749f2a14af9bb19fdf12f76f96fe912e7f1d716af733a44d926ec49`
  (≡ `PRELAUNCH.sha256`, differs from all five predecessors); ZERO
  freeze-pin mismatches across all 3502 sealed entries (E114 + E115 both
  committed before staging); plan digest of record unchanged `5c0998f2…bf2d`,
  plan model digest fresh `98d055c4e826296f79a8e7d70275be14256229732637fc6cdf547dca47f506ca`,
  ladder grid v1, 25 exchanges, max_cost 5000, company 0; workspace
  `isolated/openttd-15.3-m6aqc6ph`, ports game 36457 / admin 58297, root
  exactly 4 entries; standalone `preflight` → `PREFLIGHT PASS` exit 0;
  pre-auth `verify` → `AUTHORIZATION_UNVERIFIED`/`CLAIM_ABSENT` exit 1
  by design; candidates 1–5 seals re-digested byte-identical; gate files
  absent; nothing signed, claimed or launched; no `artifacts/` byte
  touched outside the fresh candidate-6 directory; no push. Books:
  ticket `01-round6-stage.md` + this entry + the pipeline stamp, one
  commit. NEXT GATES (each its own explicit operator approval, none
  granted by this stage): round-6 independent review (ticket 02 method,
  fresh-context read-only) → Gate C signing (ticket 03) → ONE launch
  (ticket 04).
- 2026-11-05 — T-002/round-6 INDEPENDENT REVIEW: round-6 gate 2 (review
  approval in-session) executed and booked — fresh-context read-only
  re-derivation audit of the staged candidate-6, ticket-02 method,
  54-axes classes A–F (A identity/seal, B staged correspondence +
  settle-then-freeze fix-carry + authority, C binary/opengfx/world
  lineage, D pins/budgets/plan re-derivation, E production pipeline
  re-execution via read-only subprocess + before==after immutability
  snapshots across all six candidates, F env/ports/keys): verdict of
  record `READY-FOR-GATE-C` **54/54 PASS, 0 FAIL, exit 0, zero
  findings, zero reconciliation debt** — fresh seal
  `e929d7b2e749f2a14af9bb19fdf12f76f96fe912e7f1d716af733a44d926ec49`
  == sidecar == digest of record, differs from all five predecessors;
  frozen closure binds the live settled tree exactly (CONTEXT.md ==
  authority-manifest current `847d710a…984d` transition 3 ADR-014, the
  live E114 funds model, the round-6 pipeline identity) with the
  event-lattice constants + commit guards present in-module
  (`DAY_ROLL_ANCHOR = 48`, `CHARGE_SLOT = 1`); staged GameScript
  main + AI package byte-equal to the live production packages and the
  staged `info.nut` equal to the LIVE re-derived save-restore
  composition (`staged_cargoflow2_composition()` — the save's stored
  GameScript identity, per the module of record), cross-round bytes
  byte-identical to candidates 3 and 4's retained workspaces
  (candidate-5's workspace removed by post-consume cleanup; the
  cross-round byte-check re-pins to 3–4); staged `source.sav` ==
  depot after-save pin == depot `after.sav` bytes `183b2027…6a6`,
  bound depot prelaunch seal == depot sidecar `4df12e1f…`, reload
  chain `D5-F12-DEPOT-RELOAD-1` bound with funds_of_record 489650;
  staged plan_policy == full live `cargoflow2_plan_policy()` (zero
  diff), plan digest `5c0998f2…bf2d` + model digest `98d055c4…`
  re-derived live and payload-continuity byte-equal across 3→6 (the
  E114 fix is execution-side; round identity = fresh seal + frozen
  settled-tree closure, never a relabel); production `preflight`
  re-run `PREFLIGHT PASS` exit 0 and pre-auth `verify` re-run
  `AUTHORIZATION_UNVERIFIED`/`CLAIM_ABSENT` exit 1 by design; the
  first audit pass ran 53/54 (exit 2) on an audit-side mis-formulated
  freshness axis (D3 demanded a never-seen value where the record's
  "fresh" means re-derived at staging) — re-grounded to record
  semantics and re-run clean, both transcripts retained; audit wrote
  nothing in the repo tree, all six PRELAUNCH byte-pictures before ==
  after, no staging rerun, no signing, no claim, no launch, no push.
  Books: ticket `02-round6-independent-review.md` + this row, one
  commit. Script + transcripts outside the repo:
  `/tmp/opencode/review_c6.py`,
  `/tmp/opencode/t6_review_c6_output.txt`,
  `/tmp/opencode/t6_review_c6_output_first_53of54.txt`. NEXT GATES
  (each its own explicit operator approval, none granted by this
  review): Gate C signing (ticket 03) → ONE launch (ticket 04, the
  only true native-run gate).
- 2026-11-05 — T-003/round-6 GATE C (signing approval in-session, one
  action) executed and booked — the operator's Option-1 signature over the
  reviewed round-6 candidate via the production signing surface only: one
  signing operation, first invocation, zero refusals, zero re-writes.
  Pre-write refusal gates held (gate surface absent; live seal == sidecar
  == operator-approved `e929d7b2e749f2a14af9bb19fdf12f76f96fe912e7f1d716af733a44d926ec49`;
  authorization payload digest
  `5433b7e5477ec2ffedf722b623ad1d3cc8f5777b7469b11d65659da420a108eb`
  staged == production re-derivation); seed mechanics of record
  (operator-held PEM 48-byte PKCS#8 final-32 window, memory-only,
  env-only `CARGOFLOW_GATE_SEED`, never printed/filed/argument-passed;
  `public_from_seed` == pinned anchor
  `5063982bd28d48573705f334ed4f396618c4930ce21083789dfbbf13a564880f`;
  operator key identity unchanged of record
  `sha256-ed25519-public-key:cbb63ff58f17f13df3e1be0735fad18497e3a0c6ad6b5dd55491d708ae40c614`);
  `AUTHORIZATION.json` written exactly once — record sha256 of record
  `e938eb62807965e864f3c5dade973d5259675187a406745a963bb724712f7e5c`,
  production `verify_authorization` PASS against the seeded anchor
  (record digest bound); post-write read-only state: root exactly 5
  entries (no CLAIM/LAUNCH-CONSUMED), seal byte-equal after the write,
  `preflight` `PREFLIGHT PASS` exit 0 with the authorization present,
  standalone `verify` still `AUTHORIZATION_UNVERIFIED`/`CLAIM_ABSENT`
  exit 1 by design (the claim mints at the launch boundary only);
  candidates 1–6 PRELAUNCH byte-pictures before == after; seed unset +
  empty verified; no candidate bytes beyond the authorization record
  touched; `git diff --check` clean; driver
  `/tmp/opencode/gate_c_cargoflow2_c6.py` + transcript
  `/tmp/opencode/t6_gate_c_output.txt` (+ CLI gate transcripts
  `/tmp/opencode/t6_gate_c_preflight_output.txt`,
  `/tmp/opencode/t6_gate_c_verify_output.txt`) outside the repo.
  Books: ticket `03-round6-gate-c-signing.md` + this row, one commit.
  The candidate-6 authorization grant is single-use and the launch is
  not granted: NEXT GATE — ticket 04r6 ONE launch (the only true
  native-run gate; needs the pinned `OPENTTD_BINARY` /
  `OPENTTD_OPENGFX_ARCHIVE` environment set before Python starts and an
  explicit in-session native-run approval; one attempt, no retry, no
  reconnect).
- 2026-11-05 — T-004/round-6 ONE LAUNCH (launch approval in-session, one
  action) executed and booked — the single native launch of the signed
  round-6 candidate-6 via the production pipeline CLI, ONE attempt, first
  invocation, no retry, no reconnect, rc 0
  `NATIVE_CARGOFLOW2_COMPLETE` (`"verified": true, "returncode": 0,
  "cleanup_complete": true, "state_changed": true, "halt": null, 1 launch /
  1 connection / 25 requests`; phase verification `CARGOFLOW2_COMPLETE`;
  phase seal == `e929d7b2…ec49`, plan digest
  `98d055c4e826296f79a8e7d70275be14256229732637fc6cdf547dca47f506ca`).
  **Binary resolution correction of record**: no env export at all — the
  cargo-flow-2 pipeline resolves the binary from the harness filesystem pin
  (`/home/fed/Downloads/openttd-15.3-linux-generic-amd64/openttd`, sha
  re-verified == the runtime pin
  `276d5b698a6b706154f3af588f6f885b3aebe518f4ecc8f869abf71383b1904c` at
  run start with the no-processes pre-check; the round-5 ticket's
  `OPENTTD_BINARY`-export note belonged to other entrypoints). The run
  minted `CLAIM.json` bound `prelaunch_digest e929d7b2…ec49` /
  `authorization_sha256 e938eb62…c7e5c` / operator identity
  `cbb63ff5…40c614` (`consumed=true / launches_allowed=1 / retries=0`),
  wrote `LAUNCH-CONSUMED.json` sha
  `329334b7d887037797ed29b9d39238c676cf8094a0e8939da7b0e4b717b02f02`, and
  executed the 25/25 exchange ladder with zero halt: site-00 READY (tick 15,
  funds 489650), engine-00 READY (E111 census fix live-true, running_cost
  421), purchase-00 BUILT (quote 4429 exact, funds 485221), vread-00 READ,
  order-00/order-01 ORDERED, order-read-00 ORDER_SET_VERIFIED, monitor-00
  ARMED, start-00 STARTED, vread-01 READ, **arrive-00 ANCHORED** at
  (712232, 292) funds 485217 — the round-5 `CARGOFLOW2_FUNDS_DIVERGED`
  halt class did NOT recur — flow-00..flow-11 READY with the native
  observed funds series [485217, 485212, 485206, 485201, 485195, 484997,
  484991, 484986, 484980, 484974, 484776, 484770], finance-00
  FINANCE_VERIFIED (day 712287, funds 484769, income 0, delivered 0),
  finish-00 PHASE_STOPPED. **Delivery verdict of record:
  `CARGOFLOW2_LOADED_NEVER_DELIVERED`** ("a load was latched, but no
  unloaded amount reached the bay acceptance chain inside the ladder") —
  the corridor's empty bay arrival 712251 (flow-04), pickup arrival 712270
  (flow-08), loads 5/10/15 at 712271 + 20 at 712272, loaded departure 20 t
  at 712274 (flow-09), the delivery leg in transit at finish (location
  50095, RUNNING) with `unloadings: []`, and the ladder's last stop
  (finance-00, 712287 = anchor 712232 + 55) preceding the delivery leg's
  return. **E114 cross-reality booked UNKNOWN for ticket 06**: the
  production fences of record all passed as recorded (arrive-00 anchored
  exactly on the E114-recorded walk level 485217 == 485217; finance-00
  FINANCE_VERIFIED), but the E114 probe/VM twin's later walk-of-record
  levels (flow-01 485217 → flow-06 484996 → flow-11 484775) differ from
  the native observed series (flow-01 485212 → last flow 484770, finance
  484769) — the twin-vs-native reconciliation is UNRESOLVED ledger
  material, never reconciled by hand. Post-run evidence complete: root
  68 entries, 25 receipt pairs + frames/receipt/result/cleanup/runtime
  identity + session-before + after-diagnostic sav, manifest
  `artifact-manifest.sha256` re-validated 66/66 OK 0 non-OK, seal
  byte-equal after the run, `isolated/` disposed empty shell; post-consume
  `verify` exit 0 (completion verified by the module's exit rule);
  certified cleanup all-true (`reaped/sockets_closed/workspace_disposed/
  credential_removed` all true, `remaining_processes: []`, endpoint
  checks `connection_closed=true`, game 36457 / admin 58297); no openttd
  process remains. Integrity close: `git diff --check` clean,
  `CONTEXT.md` pin == authority-manifest current
  `847d710abe87e2ed211a72d6455f3f1326b1476eca1711ab8be900080ec2984d`,
  candidates 1–6 seals re-digested == sidecars (candidate-5 stays consumed
  terminal history, round-5 verdicts unrelabeled). Run transcript of
  record `/tmp/opencode/t6_run_output.txt` (candidate-6's retained
  `result.json` / `receipt.json` / `cleanup.json` /
  `artifact-manifest.sha256` carry the bytes) outside the repo. Books:
  ticket `04-round6-one-launch.md` + this row + E116 evidence row +
  AI_HANDOFF terminal block, one commit. The candidate-6 authorization is
  consumed terminal history (identities never relabeled/re-launched); NEXT
  FRONTIER — ticket 06 delivered-class reconciliation, whose adjudication
  now needs the operator: the round-6 outcome class is COMPLETE-not-
  delivered (`CARGOFLOW2_LOADED_NEVER_DELIVERED`), a class ticket 06's
  current text does not yet spell out; downstream tickets 08–13 unchanged
  blocked.
- 2026-11-05 — T-006 reframed by explicit operator decision ("Reframe 06
  now") — the delivered-class reconciliation ticket now admits TWO
  outcome classes and completes on either: (a) a delivered launch
  (delivery receipts inside the ladder) or (b) a COMPLETE-not-delivered
  run — `NATIVE_CARGOFLOW2_COMPLETE` with the attempt's own delivery
  verdict of record — whose ledger row records the load-latched-never-
  unloaded fact, the production fences that passed as recorded, and the
  E114-twin-vs-native funds cross-reality UNKNOWN carried verbatim. A
  terminal halt still routes through ticket 05. Blocked-by updated: 04's
  terminal COMPLETE receipt of record (round-6 candidate-6, `rc 0
  NATIVE_CARGOFLOW2_COMPLETE`, verdict `CARGOFLOW2_LOADED_NEVER_DELIVERED`,
  E116) satisfies it. The reframe grants nothing further: the ticket's
  read-only reconciliation loop (verdict replay + funds fence native-side
  check + ledger row + integrity close) executes only under its own
  explicit operator approval; tickets 08–13 unchanged blocked.
