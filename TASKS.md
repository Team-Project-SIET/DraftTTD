# Continuation tasks — 2026-10-17

Read AI_HANDOFF, CONTEXT and EVIDENCE_INDEX first. This list grants no runtime
authority. Current product priority is the stable demo plus bounded Random World.
Canonical creation/reload Q3 are historical PROVEN milestones, not pending tasks.

1. **Offline transfer verification.** Compare branch/HEAD, dirty paths and source
   hashes with `docs/handoff/2026-10-17/`. Confirm required ignored artifacts exist
   and verify selected evidence hashes. Report missing bytes as UNKNOWN. Done:
   reviewed source/evidence inventory, no secret transfer and no historical edits.
2. **Offline fresh random readiness.** Review the 512-tile profile, legacy 256
   compatibility, staged bridge, capture budgets, qualified-month window, native
   47-tile path filter, P05 timeout, diagnostics/replay and cleanup. Run focused
   controlled tests from REPRODUCE. Prepare only a new uniquely named package if
   preparation is requested; preserve consumed sources and claims. Done: concrete
   frozen-input identity and independent preflight report, with staleness and
   runtime blockers explicit; zero launches/Admin connections during preparation.
3. **Separate authorization: one new Seed 17 native smoke.** Use seed 17, 256×256,
   temperate/terrain 0/towns 1/industries 2, freshly frozen current code and finite
   settings/budgets. One server and encrypted Admin session; spectator only when
   included in the reviewed scope. Capture all required tiles, coverage, settings,
   engines and same-session source correspondence. Run P08/P05 only on admitted
   native facts. Retain diagnostics on infeasibility; no retry/reconnect. Done:
   independently replayable generation/qualification/capture, explicit candidate
   and selection results, any authorized construction/delivery receipts, and full
   owned-runtime cleanup. A valid unsupported-world result remains distinct from
   a successful delivery. Do not promise the coal pair will yield a feasible road.
   The offline readiness/observation-inventory record is
   [the observation inventory](docs/random-world-observation-inventory.md).
   The prepared, independently reviewed fresh smoke identity for the
   future authorized one-shot run (run dir `playable-demo-698799a2d…`, frozen
   inputs, verdict with all 9 offline preflight checks PASS, launch command,
   capture checklist, budgets, cleanup plan) is
   [the smoke preparation record](docs/seed17-native-smoke-preparation.md).
   **Update:** that authorization was consumed (one-shot, 2026-10-17). Native
   facts were complete but P08 found `NO_BOUNDED_CORRIDOR` on the only
   capturable pair (coal), giving 0 candidates, P05 not run and
   `NO_FEASIBLE_SERVICES`; no construction or delivery. Read the record's
   "Consumed outcome" section for the retained evidence.
4. **Offline P07 continuation after accepted delivery.** Replay into a fresh sibling
   output. Verify per-service totals, charts/history, world/seed/plan attribution,
   null/UNKNOWN behavior and comparisons. Done: reproducible reports with native
   measurements distinct from derivations; no invented OPEX/profit/ROI.
5. **Later product work, separately scoped.** Improve support for obstructed terrain,
   long corridors, >32 industries or larger maps only with explicit contracts and
   bounded observation/search/execution. Current implementation does not support
   arbitrary slopes, clearing, bridges/tunnels or arbitrary-world road feasibility.
   **Update (2026-10-17, offline):** P08 now runs a bounded terrain-aware
   reachability oracle before candidate selection, and the retained Seed 17
   `NO_BOUNDED_CORRIDOR` was proven a complete-search infeasibility for the coal
   pair (construction-extension classification included; no supported construction
   connects it). See
   [the bounded routing record](docs/p08-bounded-terrain-aware-routing.md).
   **Update (2026-10-17, second, offline):** bounded terrain-modification
   planning/validation is implemented (`app/planning/p08_terrain.py`, hooked
   into both `NO_BOUNDED_CORRIDOR` branches of `generate_road_scenario` as
   planning-only diagnostics): the retained Seed 17 levelling question is
   answered structurally — all 23 height-step adjacencies are fenced by
   unclassifiable obstruction tiles (house/station class dropped by the
   `TileFact` projection), so `NO_CONNECTED_LEVELED_CORRIDOR` reproduces and
   nothing connects the coal pair even with levelling classified. Native
   execution stays unsupported pending a fresh authorization. See
   [the bounded terrain-modification record](docs/p08-bounded-terrain-modification-support.md).
   **Update (2026-10-17, third, offline):** native tile classification and
   generalized feasibility are implemented additive-only: schema-2
   `tile_classification_page` contracts plus a composed classification bridge
   (no frozen path changed; the capture still requires a fresh one-shot
   authorization), five deterministic corridor segment classes with
   conflicting evidence downgraded to UNKNOWN (never inferred), a three-tier
   bounded `assess_world_feasibility` diagnosis (world identity, industry
   relationship, observed coverage, per-class corridor, required-op
   inventory) attached to `NO_BOUNDED_CORRIDOR` without changing pinned
   strings, a construction-readiness registry with exact per-op blockers, and
   additive diagnostic codes. Retained Seed 17 assessment: 450 tiles = 339
   ROAD_BUILDABLE + 63 SUPPORTED_CLEARING + 19 UNKNOWN + 29 UNSUPPORTED;
   `INCOMPLETE_TILE_CLASSIFICATION` — a corridor exists only through tiles
   whose class the retained evidence dropped. See
   [the classification record](docs/p08-native-tile-classification.md).
   **Update (2026-10-17, fourth, offline):** Tile Classification V2 native
   capture is prepared, not executed: receipt/correlation/census-binding
   layer (`TileClassificationReceipt`/`TileClassificationExchange`/
   `TileClassificationSweep` with the deterministic multi-band request plan —
   the Seed 17 15×30, 450-tile census becomes exactly 90 ≤256-tile-band
   pages), staged classification candidate
   (`proof/terrain_classification_preparation.py` refuse-on-missing-seam
   staging; `PENDING_AUTHORIZATION`, zero launches, zero requests, claim
   untouched), a Task D readiness projection per classified obstacle
   (planning vs native support stated per record), and an offline retained
   replay that fuses a synthetic census (19 projection-dropped tiles stay
   UNKNOWN, one same-instant ground-agreement semantics fix in
   `classify_segment`, all pinned suites intact) reproducing the retained
   assessment digest-for-digest. Exact launch template, budgets, receipts and
   cleanup are recorded in the candidate; no native claim is possible until
   the fresh one-shot capture runs. See
   [the preparation record](docs/p08-classification-v2-native-capture-preparation.md).
6. **Separate engineering backlog.** Fourth-vehicle intervention, matched A/B runs,
   continuous dispatch and five-year experiments require their own reviewed
   contracts/authorization. Reload-only Q3 proves correspondence and heartbeat,
   not purchase or unpause. Attempt 19 is contextual history, not a matched arm.
   Preserve terrain-proof offline acceptance gaps and missing canonical inputs;
   historical REAL_PASS does not fill them. See `docs/capacity-experiment.md` and
   `docs/specs/openttd-offline-evidence-freeze.md` before that work.
7. **Tile Classification V2 executable path (done offline, awaiting
   authorization).** The four execution blockers are implemented and validated
   offline (`classification_execution.py` staging bound to actual
   source/package/config/argv digests + byte-verified retained `before.sav`,
   schema-2 AdminPort dispatch keyed `(request_id, region, cursor)`, the
   bounded 90-page runner with byte retention and freight-mirroring cleanup,
   and the fail-closed correspondence policy); the frozen prepared candidate
   stays byte-unchanged and the SAME_SESSION fallback is a review-only
   schedule. Native validation of save-load GameScript resolution and the
   census itself require ONE fresh operator authorization; a mismatch fails
   closed (TransportTimeout on page 1 + stderr markers), never silently. See
   [the execution path record](docs/p08-classification-v2-execution-path.md).
   **Update (2026-10-18, native):** the one-shot authorization of execution
   candidate `classification-exec-seed17-e71c95a3` (attempt
   `750167949a4f46af…`) was consumed by a single authorized launch. All
   pre-launch gates passed, the staged composition resolved against the
   save's stored GameScript identity and started, but the instance died
   unexpectedly (no `Load()` hook for the retained save data) before any
   AdminPort page: 0 requests/0 pages, world correspondence NOT established,
   the 19 unknown tiles remain UNKNOWN and the retained
   `INCOMPLETE_TILE_CLASSIFICATION` assessment is unchanged; terminal
   `FAILED_CLEANUP` evidence is preserved in the candidate directory. Read
   [the terminal outcome record](docs/p08-classification-v2-native-capture-outcome.md).
   **Update (2026-10-18, offline diagnosis + repair):** the death was
   re-diagnosed from OpenTTD 15.3 sources + the pinned binary as a **benign,
   engine-designed dummy-AI fallback death misattributed by the runner's
   fatal-log health check**: the staged runtime staged no AI, so the save's
   stored `RoadProofCompany`/1 resolve fell back to the instant-dying dummy
   AI (three `[0] [E]` lines → `Start()` returns → `Died()`), while the
   GameScript itself survived (`[18] BRIDGE_STARTED`; the two post-death
   `[18] [W]` save warnings at the single exit-save prove liveness). Minimal
   repair, no historical bytes touched: the runner health vocabulary now
   recognizes OpenTTD 15.3's `which is no longer available` save-load
   fallback (always fatal), adds a `[S]`-severity tripwire, and exempts
   exactly the designed dummy-AI death (full three-line sequence + direct
   script-log adjacency, once, never for a second death); SOURCE_SAVE
   staging now stages the retained AI package (`RoadProofCompany`, provably
   never dies), sealing its digest in the composition/candidate/PRELAUNCH
   records with byte-exact preflight verification. Fresh non-executed
   candidate `classification-exec-seed17-3a8f9e46` (attempt
   `556e97b81230bfd3…`, composition `3a8f9e46969687b6…` including the staged
   AI package digest `3708a4181df49a3e…`) staged `PENDING_AUTHORIZATION`,
   preflight PASS; 35 focused + 213 broader controlled tests re-run green;
   no launch, no connection, no claim consumed. Read
   [the diagnosis/repair record](docs/p08-classification-v2-native-capture-diagnosis.md).
   **Update (2026-10-18, native):** that fresh one-shot authorization was
   consumed and Tile Classification V2 completed natively
   (`TILE_CLASSIFICATION_V2_CAPTURED_INCOHERENT`): 90/90 pages, 450/450 tiles,
   schema-2 exchange for every page, staged AI (`RoadProofCompany READY`) and
   GameScript (`BRIDGE_STARTED protocol=1 api=15`) starting with zero script
   deaths, exact per-page byte budgets held and cleanup completed (process
   reaped, sockets closed, credential removed, workspace disposed). The
   SOURCE_SAVE_FUSION correspondence verdict is **`REJECTED`** with 83
   `PROJECTED_FLAGS_DIFFER` contradictions; nothing was fused, the
   historically UNKNOWN 19 tiles were all observed CLEAR+buildable in the
   fresh census and, as contradictions, are NOT accepted into the retained
   assessment; P08 stays `INCOMPLETE_TILE_CLASSIFICATION`. An offline
   rebinding of the retained page bytes reproduced the recorded completeness
   byte-equal, and the 198-file artifact manifest hash-verifies. Capture
   success is not world correspondence; reconciling the fresh census with the
   historical projection is separately scoped future work. Read
   [the completion record](docs/p08-classification-v2-native-capture-completion.md).
8. **Milestone D3 complete; Milestone D4 (native road + station construction)
   attempt consumed 2026-10-22 — INCOMPLETE.** D3 closed 2026-10-22: the two bounded
   clears (45999, 49326, £30/£45) and the 16-compiled-S-corner terraforming phase
   (£3,382) all replay-`RECEIPT_VERIFIED`, finances reconciled to £496,543, and
   the receipt-bound post-D3 world (`fbebef54…d59e`) proves the planned 24-tile
   corridor flat min-height 2, slope 0, CLEAR, unowned on every tile. Read
   [the D3 close-out record](docs/handoff/2026-10-22/d3-terraform-native-candidate-1-outcome.md).
   D4 stages ONE candidate (`D4-CORRIDOR-1`, additive wire contract + package +
   `proof/corridor_construction_native.py` reusing the shared D2/D3 machinery)
   from that world: 2 straight `BuildRoadFull` runs, the 2-tile corner piece,
   2 truck stops (pickup 45748 front 45747; delivery 50351 front 50095) and the
   depot at 45487 facing 45743 — `PENDING_AUTHORIZATION`, no claim consumption,
   strict offline validation, catchment/acceptance re-checked natively only at
   construction admission. Staging completed 2026-10-22: the candidate is staged
   with `PRELAUNCH PASS` + read-only `PREFLIGHT PASS` (19 planned protocol-4
   exchanges, 640-B response bound, fail-closed never-consumed verify verdict;
   superseded intermediate stages (pre-fix/pre-lint frozen bytes) were deleted
   and re-staged fresh from the final reviewed bytes). Read [the D4 staging
   record](docs/handoff/2026-10-22/d4-corridor-native-candidate-1-preparation.md).
   **Update (2026-10-22, native):** the operator authorization was consumed by ONE
   launch; the corridor ceremony ended `PHASE_HALTED_PREFIX_PRESERVED` with
   `verified: false`, so Milestone D4 remains INCOMPLETE. Only `op-00` was
   verified (5-tile road run at £785, independently re-read, funds £496,543 →
   £495,758); `op-01` was refused at admission because its native quote £2,549
   exceeded the £2,000 per-operation ceiling (no native command issued), and
   `op-02`–`op-05` plus the route read were never executed — no receipt or
   `after.sav` exists. The read-only replay verifier was repaired offline
   (26 → 29 PASS; wire suite 21 PASS). The consumed candidate `D4-CORRIDOR-1` must
   never be edited or reused; a future attempt requires a fresh staged candidate
   plus fresh explicit operator authorization, and none has been staged or
   authorized. Read
   [the D4 close-out record](docs/handoff/2026-10-22/d4-corridor-native-candidate-1-outcome.md).
   **Update (2026-10-22, offline — Option C restage decision implemented):** the
   staging-time Option C decision was implemented offline as compiled code and
   tests (no launch, no authorization, no candidate staging): the corridor
   schedule is staged as **8 ops** — run A, the compiled 17-tile run B as its two
   contiguous straight segments (45999→48047, 9 tiles; 48303→50095, 8 tiles) plus
   a separate interior road join 48047↔48303 built after both segments, the
   unchanged corner join, both truck stops and the depot — so every op is
   individually re-quoted natively inside the **unchanged £2,000 per-operation
   ceiling**; there is deliberately no aggregate phase budget (worst-case
   theoretical exposure 8 × £2,000 = £16,000 is an exposure bound, not a budget).
   A schedule-version selector (`schedule_version 2` for fresh staging; v1 kept
   compiled from the same pinned facts) keeps the consumed attempt's read-only
   replay re-derivable (`PHASE_HALTED_EVIDENCE_PRESERVED` unchanged); the witness
   route, `corridor_facts()`, `route_policy()` and the wire contract are
   untouched; 25 planned exchanges (budget 31). Controlled suites 55 PASS (wire
   23 + native 32) with compileall/ruff/`git diff --check` clean; the two prior
   review concerns are covered by new dispatcher-budget, GameScript-key,
   segment-reassembly, version-binding and site-op `_pins()` tests. The
   historical £2,549/£785 quotes are controlled references of the consumed
   attempt — no native quote, command, receipt or authorization exists for the
   new schedule, so **Milestone D4 stays INCOMPLETE (native)**; next steps are an
   independent offline review of this implementation, then fresh candidate
   staging and ONE fresh explicit operator authorization. Read
   [the Option C implementation record](docs/handoff/2026-10-22/d4-corridor-option-c-implementation.md).
   **Update (2026-10-22, offline — independent review):** an independent read-only
   review of the Option C implementation returned **`PASS WITH CONCERNS`**
   (E23): focused suites re-executed fresh 55/55 PASS (wire 23 + native 32,
   0 skipped) with ruff/compileall/`git diff --check` clean; the eight-op
   derivation, geometry, version selector (fail-closed on unknown versions),
   25/31 request budgeting and dispatcher cap refusal were re-verified
   independently; the production read-only replay of the consumed candidate
   reproduced the E21 verdict byte-identically (v1 re-derivation bound by
   digest); the consumed candidate's artifact manifest hash-verified 28/28
   before and after the review's runs and D2/D3 evidence stayed unchanged.
   Findings: one vault documentation defect fixed in review (a broken Markdown
   table row), two non-blocking fail-safe observations recorded in the review
   record (latent v1/v2 planned-count skew in the completed-receipt replay
   branch, unreachable today; `schedule_version` not itself a signed payload
   key). The old attempt remains halted; no native quote/command/receipt/
   authorization exists for the new schedule and Milestone D4 stays INCOMPLETE
   (native). The implementation is review-cleared for fresh-candidate
   preparation, which remains a separate future step requiring ONE fresh
   explicit operator authorization before any launch. Read
   [the independent review record](docs/handoff/2026-10-22/d4-corridor-option-c-implementation-review.md).
   **Update (2026-10-22, offline — staging done, then read-only payload
   verification):** the fresh candidate **`D4-CORRIDOR-2`** is staged at
   `artifacts/experiments/d4-corridor-native-candidate-2/` (E24; record:
   [the candidate-2 staging record](docs/handoff/2026-10-22/d4-corridor-native-candidate-2-preparation.md))
   after the operator-approved one-constant identity bump, with `PRELAUNCH
   PASS` + read-only `PREFLIGHT PASS`, seal
   `de0e16f7…04f00` (full
   `de0e16f73d71efbad636271217a4981b4e6350412184bdbdfa17533e3d304f00`; an
   earlier `…2bf00` shorthand in active notes was corrected 2026-10-22), plan
   digest `2a30e95048e89ffa1420e0ae392b79f4d051f447d7a15a3edb896b4bbdcabb3a`
   (v2, eight ops), 25 planned exchanges / budget 31, source world byte-bound
   to the D3 after-save `fbebef54…d59e`, suites re-run 55/55 PASS. The staged
   authorization payload was then re-verified read-only (record:
   [the payload verification record](docs/handoff/2026-10-22/d4-corridor-native-candidate-2-payload-verification.md)):
   the canonical payload rebuilt offline from the staged `PRELAUNCH.json`
   equals the staged digest
   `e85ea64ba8ec15c383e913a72df7d1e4bd13569496a83d297bf7ee2c1952ff17`
   (2,393 bytes) and the frozen closure hash-verifies 3,447/3,447 (0 missing,
   0 mismatches) — verification only: nothing signed, no
   `AUTHORIZATION.json`/`CLAIM.json`, no launch, no Git staging; the
   remaining step is unchanged. A documentation pass also corrected same-day
   inconsistencies explicitly (seal shorthand, the staging record's §8
   pointer and a duplicated clause, the overbroad "byte-for-byte" claim for
   `Next Actions.md` — self-written by the review session, prior bytes
   UNKNOWN) and vault copies were refreshed. **Milestone D4 stays INCOMPLETE
   (native); candidate-2 stays `PENDING_AUTHORIZATION`; next: ONE fresh
   explicit operator authorization.**

   **Update (2026-10-25, offline — authority-pin repair + fresh candidate-3):**
   the explicit operator-authorized `CONTEXT.md` pin repair (E26, ADR-014) keeps
   every retained manifest byte-unchanged and scopes exactly one path/digest
   transition through a fail-closed record; the three former baseline failures
   now pass. A read-only preflight then proved `D4-CORRIDOR-2` stale
   (`verify_freeze`) because its frozen closure predates the accepted
   ADR-012/ADR-013 source edits; it was never consumed and was not edited. A
   fresh never-consumed candidate **`D4-CORRIDOR-3`** was staged from the
   current reviewed bytes and the verified D3 after-save (`fbebef54…d59e`):
   `PRELAUNCH PASS` + read-only `PREFLIGHT PASS`, seal `8cc8c1f7…7d24`, plan
   digest `2a30e950…cabb3a`, rebuildable payload `e1163d09…068d`, 3,448-entry
   frozen closure, focused suites 55/55 PASS. No authorization, claim, launch,
   AdminPort access or native quote exists; D4 remains INCOMPLETE (native). The
   next step is ONE fresh explicit operator authorization for
   `D4-CORRIDOR-3`. Records:
   `docs/handoff/2026-10-25/context-authority-pin-repair.md` and
   `docs/handoff/2026-10-25/d4-corridor-native-candidate-3-preparation.md`.

   **Update (2026-10-25, native run consumed — E28):** `D4-CORRIDOR-3` was
   signed, verified and then consumed by exactly one operator-authorized native
   run. `op-00`–`op-02` built and read back (£785 + £1,398 + £1,151; funds
   £496,543 → £493,209); `op-03` (interior join `48047↔48303`) was refused at
   admission as `NOT_BUILDABLE` with cost 0, so the runner halted with
   `ValueError: native READY admission with positive tested cost required`.
   `op-04`–`op-07` and the route read never executed. Result:
   `PARTIAL_EXECUTION_EVIDENCE`, `verified: false`, `status: FAILED_CLEANUP`;
   `after-diagnostic.sav` is not an authoritative save, no `after.sav` or
   `receipt.json` exists, and read-only replay refuses `halted attempt cleanup
   incomplete` (a TCP state-5 observation aborted workspace/credential
   disposal; no listener remains). No retry, re-sign or replacement candidate
   was attempted. **Milestone D4 remains INCOMPLETE (native).** Record:
   `docs/handoff/2026-10-25/d4-corridor-native-candidate-3-outcome.md`.

   **Update (2026-10-25, offline `op-03` root cause — E29):** the failure was a
   scheduling/modeling defect, not an admission bug. Scripted `BuildRoadFull`
   builds both straight road bits at both span endpoints, so the collinear
   run-B segments already auto-connect at `48047↔48303`; the native
   `pairs_ok 1` observation was correct and the road admission rightly refused
   an already-connected pair. The perpendicular corner `45743↔45999` still
   needs its own `BuildRoad`. The fresh schedule is now v3 with 7 ops and no
   interior join (`SCHEDULE_VERSION = 3`, `ROAD_OP_COUNT = 7`, 22 planned
   exchanges, budget 28); v2/v1 remain read-only replay derivations. The Nut
   `StageIndex`, budget, offline endpoint-bit model and regression tests are
   updated. Focused suites 55/55 PASS; ruff, `py_compile` and
   `git diff --check` clean. No native run, candidate reuse/staging or evidence
   modification. Record: `docs/handoff/2026-10-25/d4-corridor-op03-root-cause.md`.

   **Update (2026-10-25, cleanup remediation verified — E30):** the reported
   `D4-CORRIDOR-3` credential removal and workspace disposal were verified
   read-only and without accessing any credential. `cleanup.json` now records
   `credential_removed: true` and `workspace_disposed: true`; the workspace is
   absent, `isolated/` is empty, and no candidate-3 secret/config file or
   process/listener remains. The historical TCP state-5 `verification_error` is
   retained, `sockets_closed` is still absent, and `result.json` remains
   `FAILED_CLEANUP` / `verified: false`; read-only replay still refuses
   `halted attempt cleanup incomplete`. The candidate manifest re-verifies
   48/48 against the remediated record (regenerated after remediation). This is
   not native success and does not complete D4. Record:
   `docs/handoff/2026-10-25/d4-corridor-native-candidate-3-cleanup-remediation.md`.

   **Update (2026-10-25, fresh candidate-4 staged — E31):** `D4-CORRIDOR-4` is
   staged at `artifacts/experiments/d4-corridor-native-candidate-4/` from the
   reviewed v3 schedule (one identity constant advanced from candidate-3; no
   other source/test/package byte changed). `PRELAUNCH PASS` + read-only
   `PREFLIGHT PASS`; seal `88cd1ecc…fd22c3`, v3 plan digest `b5b472ff…2283a78`,
   payload `4037c5d8…487c7f` over 2,307 canonical bytes; 7 road ops, 22 planned
   exchanges, request cap 28, per-op ceiling £2,000, no redundant interior
   join, perpendicular corner retained; source world unchanged D3 after-save
   `fbebef54…d59e`; focused suites 55/55 PASS. No authorization, claim, signing,
   launch or native quote exists. **Milestone D4 remains INCOMPLETE (native);**
   next is independent review, then separate explicit operator authorization
   for signing and one native attempt. Record:
   `docs/handoff/2026-10-25/d4-corridor-native-candidate-4-preparation.md`.

   **Update (2026-10-25, native candidate-4 consumed — E32):** the cleanup
   certification question was resolved as attempt-scoped: candidate-3's
   historical `FAILED_CLEANUP`/absent `sockets_closed` stays unchanged and is
   not a hard prerequisite for a fresh candidate, while current isolation was
   verified independently (no process, listener, workspace or staged secret;
   candidate-3 and candidate-4 ports free). `D4-CORRIDOR-4` was signed under
   the pinned anchor (authorization `b069b484…5db6d`, 64-byte signature,
   payload `4037c5d8…487c7f`, 2,307 bytes) and consumed exactly once.
   `op-00`–`op-05` built and read back (£785 + £1,398 + £1,151 + £71 + £307 +
   £292 = £4,004; funds £496,543 → £492,539), including the perpendicular
   corner `45743↔45999` and both stops. `op-06` (depot `45487`) was dispatched:
   the native log reports `D4_RESPONSE depot-06 BUILT` and the retained frame
   reports `BUILT`/£390/£492,149, but its 513-byte GameScript payload exceeded
   the 512-byte application limit, so the client raised
   `MalformedMessage: GameScript packet exceeds application limit` before
   parsing. No `confirm-06`, `receipt.json` or authoritative `after.sav`
   exists; `after-diagnostic.sav` is non-authoritative. Phase
   `PARTIAL_EXECUTION_EVIDENCE`, `verified: false`,
   `status: PHASE_HALTED_PREFIX_PRESERVED`; cleanup is certified (all four
   fields true) and the manifest is 80/80 OK. Read-only replay raised the same
   `MalformedMessage` before a verdict at the time. No retry, re-sign,
   replacement or claim reuse; **Milestone D4 remains INCOMPLETE (native)**. Record:
   `docs/handoff/2026-10-25/d4-corridor-native-candidate-4-outcome.md`.

   **Offline correction (2026-10-25, E33):** the terminal defect was an
   application-bound mismatch, not an oversized frame. Protocol 4 permits
   640-byte responses, but `decode_gamescript` applied the version-one 512-byte
   limit to every protocol. `encode_gamescript`/`decode_gamescript` now take a
   validated opt-in `max_payload_bytes` (default unchanged 512; absolute
   frame-body ceiling 32763), and protocol 4 uses its documented 640-byte bound
   in `CorridorReadback.parse_for`, the live exchange and retained-frame replay.
   The retained 517-byte depot frame decodes to a 513-byte payload and parses to
   `BUILT`; exact 640 passes, 641 fails, and malformed/truncated/duplicate/
   invalid-UTF-8 bodies still fail closed. Focused suites 129/129 PASS;
   `ruff check --ignore UP037` on the touched files passed, while full
   `ruff check` reports only four pre-existing `UP037` findings at unchanged
   `corridor_construction.py` lines 116/214/534; `py_compile` and
   `git diff --check` clean. This creates no receipt and does
   not verify the consumed attempt: replay now reaches the next honest refusal
   (missing `depot-06-response.json`), and D4 remains INCOMPLETE (native).
   Record: `docs/handoff/2026-10-25/d4-corridor-response-limit-fix.md`.

   **Native completion (2026-10-26, E35):** under the operator's explicit
   written authorization (signing of `D4-CORRIDOR-5` plus exactly one native
   attempt), every pre-signing gate was re-verified fresh — identity/seal
   `505b5d49…4a7c`, payload `77a965f0…0e4` over 2,307 canonical bytes, plan
   digest `b5b472ff…2283a78`, schedule v3 invariants (7 ops, 22 planned, cap
   28, £2,000 per-op, no interior join, corner `45743↔45999`), source save
   `fbebef54…d59e`, 3,448-entry frozen closure re-hashed by a fresh read-only
   `PREFLIGHT PASS`, independent review PASS (20/20), implementation-vs-review
   freeze binding, protocol 640/512/32763 statics + dynamics, quote/budget
   machinery, runtime isolation, never-consumed state, and focused suites
   129/129 PASS. The candidate was signed exactly by the documented approved
   checklist (Option 1 repository tooling; seed captured, never displayed,
   never written or passed as an argument; signature verified under the pinned
   production anchor before writing; seed cleared right after signing) and the
   resulting record (`55486971…dec03`, operator identity
   `sha256-ed25519-public-key:cbb63ff5…40c614`) re-verifies. The single native
   attempt ran to completion; no retry, reconnect or second launch: 1 launch /
   1 encrypted X25519 connection / 22 of 28 requests; all seven scheduled ops
   dispatched exactly once, each with a positive tested quote equal to its
   native cost within the £2,000 per-op ceiling and each independently read
   back via its `confirm-XX` — op-00 £785, op-01 £1,398, op-02 £1,151, op-03
   corner £71, op-04 £307, op-05 £292, op-06 depot £390 (the durable 513-byte
   `depot-06-response.json` retained under the E33 640-byte bound, readback
   digest matched). Funds reconcile exactly £496,543 − £4,394 = £492,149,
   confirmed by the route read. Route receipt `ROUTE_VERIFIED` 23/23;
   `receipt.json` binds before-save `a3e6b510…5c5c` and the authoritative
   after-save `a81ac836…ef261`; `after-diagnostic.sav` retained, never a
   substitute. Cleanup certified (all four fields true, return code 0,
   endpoints certified, workspace disposed, credit/credential removed); no
   process or listener remains and `isolated/` is empty. Manifest 90/90 OK;
   read-only replay returns **`RECEIPT_VERIFIED`**. Candidate-1/2/3/4 and D3
   evidence re-verified byte-unchanged (candidate-4 manifest 80/80). **D4
   Native Road & Station Construction is COMPLETE for the reviewed v3 scope
   (`NATIVE_CORRIDOR_VERIFIED`);** no vehicle/delivery/OPEX/ROI claim and no
   new authorization is implied. Record:
   `docs/handoff/2026-10-26/d4-corridor-native-candidate-5-outcome.md`.

9. **Native execution attempt analytics (done offline; integrated).** A parallel
   workstream ("OpenTTD Analytics Feature Completion") implemented and verified
   offline, read-only run-level analytics over the retained native attempt
   records in an isolated worktree (same base `775ecab`), and it is now
   integrated into the main checkout: `app/experiments/native_attempt_analytics.py`,
   the additive `analyze-native-attempts SOURCE… --output DIR` CLI subcommand in
   `app/experiments/cli.py`, `tests/test_native_attempt_analytics.py` and
   [the analytics record](docs/native-attempt-analytics.md). It reads only
   retained `PRELAUNCH.json`/`result.json`/`cleanup.json` plus consumption
   markers, copies statuses and `verified` flags verbatim, never counts an
   unverified/partial attempt as a verified success (D4's three attempts stay
   partial/failed and verified_outcomes counts only E17/E19/D2/D3 verified
   records), keeps missing fields UNKNOWN (no OPEX/net-profit/ROI), certifies
   cleanup fail-closed, refuses pooled comparisons across unrelated source
   worlds and states schedule-revision contrasts without causal claims.
   Integration preserved the E33 protocol-fix files byte-unchanged and
   re-verified the feature fresh in the main checkout: focused suite 34/34
   PASS, adjacent experiment/CLI/analytics suites 84 PASS, ruff/format/
   compileall/`git diff --check` clean, deterministic outputs (two runs,
   byte-identical), and the seven retained attempt directories hash-verify
   byte-identical (626 files) before and after the analysis runs. Evidence:
   E34. **This integrates no native evidence, verifies no consumed attempt,
   stages no candidate, consumes no claim or authorization; Milestone D4
   remains INCOMPLETE (native); a fresh attempt still requires a fresh
   candidate, independent review and separate explicit operator
   authorization.**

10. **D5 corridor freight cycle — implementation-ready design (done offline;
    2026-10-26; not committed at design time).** After the E35 close-out, the
    next objective-advancing milestone was selected and designed offline:
    **D5 = complete exactly one native pickup→delivery freight cycle for
    cargo 1 on the D4-built corridor over the candidate-5 `after.sav`
    world** — site admission, one engine purchase under a positive tested
    quote ≤ £2,000, the exact two-stop order set (pickup `OF_FULL_LOAD`,
    delivery `OF_NO_LOAD`), observed loading → transit along the verified
    witness → unloading with GSCargoMonitor pickup/delivery amounts equal to
    the observed load, per-exchange funds reconciliation, and a
    receipt-bound before/after save pair replay-verifiable to
    `RECEIPT_VERIFIED`. Design record:
    `docs/d5-corridor-freight-design.md` (problem/objective, in/out of
    scope, architecture, protocol-5 entities/messages/state/failure
    taxonomy, trust boundaries, offline+native test strategy, required
    machine-verifiable evidence, budget/packet/cleanup/replay/idempotency
    constraints, explicit A1–A12 pass/fail acceptance criteria, risks and
    fallbacks, dependency-ordered tasks T1–T12, and the future
    independent-review + explicit-authorization gates). It reuses the proven
    corridor ceremony machinery (E35), the proven vehicle
    admission/lifecycle semantics (legacy lane) and the proven delivery
    evidence contract (`NATIVE_MULTI_SERVICE_DELIVERY_VERIFIED` legacy
    attempt) without relabeling any historical lane. **Status discipline:**
    D5 is a designed plan only — no candidate, claim, seal, signature or
    authorization exists; nothing here grants launch authority; full
    OPEX/net-profit/ROI remain UNKNOWN and are out of scope; staging (T8)
    is gated on the independent review (T7), and any signing or launch (T9)
    requires a fresh explicit operator authorization. Next tasks: T1–T6
    offline implementation, then T7 review.
    **Update (2026-10-26, offline):** T5 and T6 are complete. The active
    protocol/cargo agent, the fifteen-exchange package (`site` through
    `finish-00`), the staging/preflight/replay proof module, and two test
    suites now exist uncommitted. `tests/test_corridor_freight.py` passes
    32/32 controlled VM tests and `tests/test_corridor_freight_native.py`
    passes 29/29 temporary-staging tests, including the pinned D4
    prerequisite, tamper/seal/claim/freeze refusals, request mapping, budgets
    and the unconsumed fail-closed verdict. The T6 record
    (`docs/d5-corridor-freight-preparation.md`) documents the TileID/65535
    safety bound, 13 logical ops versus 15 exchanges, the actual
    `GSStation.GetCoverageRadius` + `GSTile.GetCargoAcceptance` API (no
    `GSStation.GetCargoAcceptance` in 15.3), and pre-departure transit
    behavior in the depot. No native candidate, claim, signature,
    authorization, launch or AdminPort interaction occurred; D5 native
    freight delivery remains UNKNOWN. T7 independent review is the next
    gate; the eventual POC still needs an optimizer-produced route in place
    of the fixed compiled plan.
    **Update (2026-10-27, offline):** The 2026-10-26 note is superseded on
    two points. (1) The T5/T6 implementation is committed (the reviewed
    bytes are the `f67f107`…`70d4ce7` lineage on `devmodule2`), not
    uncommitted. (2) The optimizer-produced route now exists: the staged D5
    plan is derived through the production `optimize_candidate_network`
    path (`route_from_d5_map`/`optimized_freight_route` in
    `app/simulation/openttd/proof/corridor_freight_native.py`) and the
    selected route is digest-bound into the wire plan; the staged candidate
    still round-trips the single retained D4 corridor witness (no competing
    executable route is demonstrated — recorded as M8 in
    `docs/d5-corridor-freight-t7-review.md`). T7 review and two offline
    remediation rounds are complete and recorded in that review document;
    native freight delivery remains UNKNOWN, no candidate, claim,
    signature or authorization exists, and T8 staging plus Gate C remain
    separate explicit gates.

**Update (2026-10-27, native — E36):** T8 staging and the Gate C
signing-and-single-attempt authorization were granted and consumed for a
fixed-corridor POC. Candidate `D5-FREIGHT-1` staged fresh from the
reviewed bytes: `PRELAUNCH PASS` + fresh read-only `PREFLIGHT PASS`, seal
`c8bdc65f…d0f7c9`, authorization payload `fdb1325f…3f75c7` (2,410 bytes,
rebuild-verified), source world bound to candidate-5 after-save
`a81ac836…ef261`, 3,486-entry frozen closure, 15 planned exchanges /
request cap 32. Signing followed the documented Option-1 checklist
(seed captured never displayed, signature verified under the pinned
anchor before writing; record `f99e8233…7fde`, operator identity
`sha256-ed25519-public-key:cbb63ff5…40c614`) — including two signing-
debug substeps in which nothing was ever written before signature
verification. The one attempt ran once: 1 launch (15.3 dedicated,
pid 15053), 1 encrypted connection, welcome identity matched, staged
composition started (`D5_READY`). The native `site-00` readback
(`site-00-response.json`) is READY with all pinned corridor facts
correct — funds £492,149 exactly, `pairs_ok 23`/23, production 104,
owner 0, vehicles 0 — but the delivery-stop cargo-1 acceptance read
**0** (< the required 1/8), so the pinned admission refused before any
mutation: no order, no engine, no purchase, cost £0, funds unchanged,
`state_changed false`, phase `PARTIAL_EXECUTION_EVIDENCE`, terminal
`PHASE_HALTED_PREFIX_PRESERVED`, `verified: false`, exit 1, cleanup
certified, manifest 16/16 OK. Read-only replay returns
`PHASE_HALTED_EVIDENCE_PRESERVED` on the same first refusal. **This is
   the D5 design's anticipated finding of record: the pinned delivery stop
   `50351` (front `50095`) has zero native cargo-1 acceptance on the fixed
   corridor. D5 is ATTEMPTED, NOT DELIVERED; no freight delivery, no
   optimizer-route claim (M8 unchanged), no OPEX/profit/ROI fact, and the
   consumed identity is closed forever.** A future POC attempt requires a
fresh reviewed candidate whose delivery-stop acceptance fact is newly
derived natively first (different stop placement or a separately
reviewed design change), plus fresh staging, review and explicit
operator authorization. Prior candidate-5 (90/90) and candidate-4 (80/80) manifest verification
re-verified byte-unchanged after the attempt; analytics over
the attempt ran twice byte-identical. Record:
`docs/handoff/2026-10-27/d5-corridor-freight-native-candidate-1-outcome.md`.

11. **D5 follow-up — `D5-ACCEPT-SURVEY-1` read-only native acceptance survey
    prepared offline (2026-10-27; uncommitted).** After E36's zero-acceptance
    finding of record, the next step was prepared strictly offline: an
    additive **protocol 6** acceptance-survey wire contract
    (`app/simulation/openttd/corridor_accept_survey.py`: pinned
    `AcceptSurveyPlan`, strict request/readback subsets, fail-closed parse
    surfaces, the request-vs-plan verifier and the fail-closed
    `survey_phase_outcome` replay verifier that distinguishes a measured
    zero from refused/missing/malformed/out-of-range/stale), an additive
    protocol-6 `SurveyHandle` in the shipped `d5_freight_package/main.nut`
    (own prefix-preserving survey stage accounting, shared 32-request
    budget, funds readback per exchange, pin/company/pause defences, a
    handler-side pinned-tile set — control `50351` + candidates `50607`,
    `50863`, `51119`, `51375`, `50605` — and zero observation fields on any
    refusal; the protocol-5 freight schedule is byte-identical), and a new
    offline suite `tests/test_corridor_accept_survey.py` (25 tests) that
    runs the shipped package in the real Squirrel VM. The candidate
    acceptance values are retained pre-construction census **hypotheses**
    (candidates census 8, control census 0), re-bound by a census-guarding
    test, and are not valid stops, not proven buildable and not a route
    claim. Verification in this tree: survey 25/25, freight regressions
    42/42 + 55/55, ruff/py_compile/`git diff --check` clean; no launch, no
    AdminPort, no staged candidate, no claim/signature/authorization, no
    repository mutation of authoritative evidence. The staging/claim
    machinery is freight-plan-bound today, so execution requires the
    separate `corridor_accept_survey_native.py` ceremony increment (smallest
    safe fix, documented) plus the independent review and a fresh explicit
    operator authorization covering exactly the one read-only survey
    session. Record:
    `docs/d5-acceptance-survey-1-preparation.md`.

    **Update (2026-10-27, offline — the ceremony increment implemented).**
    `app/simulation/openttd/proof/corridor_accept_survey_native.py` (new)
    closes the freight-plan-bound staging gap: its own narrow pipeline is
    explicitly bound to `AcceptSurveyPlan` (`_require_survey_plan` refuses
    any other plan model — a `FreightPlan` cannot be staged, sealed or
    replayed as a survey) and to the fixed eight-exchange `radius` →
    control/candidate `accept` → pickup `prod` schedule; it reuses the
    proven shared ceremony by import (the D4 candidate-5 after-save
    prerequisite binding, runtime freeze/dependency identity, one-launch
    backend, authorization-payload builder, cleanup discipline) — never by
    copy — while its wire session parses protocol-6 `SurveyRequest`s only
    (a freight frame fails the survey session's protocol-6 schema check and
    a survey frame fails the freight session's protocol-5 check), its
    schedule admits only the read-only `radius`/`accept`/`prod` ops,
    `max_cost` is 0 everywhere, funds are read back per exchange, and
    cleanup certification gates every completion verdict. Staging re-parses
    the retained pre-construction census as `HYPOTHESIS` rows only (absence
    recorded as `CENSUS_ABSENT`, never invented) and a measured value
    differing from its hypothesis is a recorded finding
    (`compare_census_findings`), never normalized or refused. The read-only
    replay verifier (`verify_survey_attempt`) re-derives every binding
    (schema, lineage, prerequisite, after-save, welcome, schedule, plan
    digest, budgets, world pins, hypotheses) and re-verifies all eight
    exchanges through the production `survey_phase_outcome`;
    `SURVEY_COMPLETE` is impossible without a full verified schedule plus
    certified cleanup, the retained receipt's phase must replay byte-equal,
    `state_changed` must be false, and a forced success label with no
    operator authorization returns structured `AUTHORIZATION_UNVERIFIED`.
    New suite `tests/test_corridor_accept_survey_native.py` (22 tests):
    staged candidate + payload rebuild + preflight re-derivation,
    cross-session freight/survey refusal both ways, mutation-op and
    exchange-budget refusals, census hypothesis/finding semantics, exchange
    request/response persistence plus malformed/stale/truncated/over-512
    failures, and replay fail-closed verdicts (claim absent, claim/
    manifest/schema/seal tamper, forced labels, exit-status discipline).
    Actual runs this session (offline; no launch, no AdminPort, no staged
    runtime-area candidate, no claim/signature/authorization): survey
    native 22/22 PASS, survey 25/25, freight 42/42, freight-native 55/55
    (122/122 combined), construction wire/native + route-optimizer 84/84,
    transport/protocol 80/80; fresh `PRELAUNCH PASS` from the shipped
    package under the real staging path; ruff check/format clean on the
    touched files, `py_compile` clean, `git diff --check` clean, TASKS
    mirror byte-identical. Survey preparation doc updated with the
    implementation status. Executing the survey still requires fresh
    independent review plus the ONE explicit operator authorization
    described in the preparation record §7.

### 2026-10-27 — `D5-ACCEPT-SURVEY-1` executed and verified (candidate-1 consumed)

The survey was authorized, staged from the reviewed bytes, sealed,
authorized (operator anchor unchanged), launched exactly once on OpenTTD
15.3 and completed all eight read-only exchanges with zero world mutation.
Measured: native truck-stop coverage radius 3; control tile 50351
acceptance 0 (E36 finding of record re-confirmed); candidate tiles 50607,
50863, 51119, 51375, 50605 each accept 8/8; pickup production 104; funds
£492,149 every exchange; no census divergence. Replay verifier
`SURVEY_COMPLETION_VERIFIED` exit 0, cleanup certified, no process or
listener remains. Full record:
docs/handoff/2026-10-27/d5-accept-survey-native-candidate-1-outcome.md.
Post-attempt correction: the replay receipt-arm comparison now reads the
flat retained-receipt shape exactly as the run writes it
(`corridor_accept_survey_native.py`), with synthetic consumed-frame
replay + tamper regression tests added (survey-native now 25/25, survey
25/25, freight 42/42 + freight-native 55/55 re-ran PASS after the change).
Both the survey and freight identities remain consumed; the next freight
phase needs a new design, new candidate and NEW explicit authorization.
Nothing was committed or pushed; HEAD stayed `1e6d6c1`.
### 2026-10-28 — D5 corridor extension: offline design + implementation (review, geometry, package, native pipeline)

`D5-ACCEPT-SURVEY-1` measured facts consumed by design only: radius 3,
control 0 at 50351, `accept 8` at 50607/50863/51119/51375/50605, prod 104.
Survey replay fix audited by a fresh-context independent reviewer:
`MATERIAL DEFECT: no` (3 minor findings retained as standing remediations;
full report in docs/handoff/2026-10-28/). Corridor geometry verified
offline from the D4 route read + retained census: run A y=178 x=175-180,
run B x=175 y=179-195, terminus front 50095=(175,195), dead-end stop
50351=(175,196), accepting industry tile 51373=(173,200); acceptance
pattern is Chebyshev-consistent with radius 3; all branch tiles flat/
vacant. Recommended placement: primary stop 50607 via east branch
(full 50096-50608, road 50095-50096, station 50607 front 50608 with
`GSStation.STATION_NEW` — distinct new station, sid {0,1} is a fail-closed
merge defect); fallback 50605 mirrored west branch. No terrain
modification. Prepared offline, all uncommitted:
`d5_extension_package/main.nut` (VM-tested 23/23 incl. no-auto-join
probe), `proof/corridor_extension_native.py` (D4 candidate-5
prerequisite binding, evidence-derived schedule with census
cross-check, prepare/preflight/execute/replay fail-closed verifier,
funds arithmetic from the 492,149 pin, budget 16, per-op 2000),
extension-native tests 43/43, plus the design record
`docs/handoff/2026-10-28/d5-corridor-extension-design.md`. The
acceptance recheck stays a SEPARATE read-only survey session on the
extension after-save before any freight attempt. No commit, no launch,
no candidate staged in the runtime area.

### 2026-10-31 — D5-CORRIDOR-EXTENSION-3 journal-ordering correction + independent review (offline)

Appended to the terrain-survey pipeline record
(`docs/d5-corridor-extension-3-phase-a.md`): (1) a source-backed journal-ordering
correction (§10) fixing §9.3's overstated sequence — the `TerrainAttemptJournal`
object is constructed before `backend.preflight` but writes nothing; the first
`journal.stage("RUN_PREFLIGHT")` after a successful read-only
`backend.preflight` creates `attempt-progress.json`, both preflight stages are
recorded at boundary completion before the claim, and a backend-preflight
failure leaves no journal, no `CLAIM.json`, no `LAUNCH-CONSUMED.json`, replaying
`AUTHORIZATION_UNVERIFIED`/`CLAIM_ABSENT` (not evidence of consumption or
success); (2) a schema-hygiene observation that `LAUNCH_BOUNDARY` is declared
but never journaled and is required by no replay verdict (left unchanged for a
future schema revision); (3) the corrected comment at
`corridor_terrain_survey_native.py` `execute_terrain_attempt` (comment only,
behavior unchanged); (4) the §11 continuation record: an independent
six-workstream remediation review with all six verdicts **PASS** (ordering,
atomic claim, launch trust chain/binary/launch-critical identity, Popen-seam
marker, journal/handshake lifecycle, replay fail-closed), three harmless
schema-hygiene observations retained, and the actual offline suite result
**130 passed, 1 skipped, 0 failed, 0 errors** for the documented three-file
command (skip = `test_corridor_terrain_survey.py:346` `typeof` note), equal to
the historical baseline. Because the comment correction changed the file's
bytes, the never-consumed, signed candidate-2 is now **stale-by-source-drift**
(read-only preflight fails `verify_freeze`; replay still `CLAIM_ABSENT`): its
retained state stands unchanged and it is never edited, re-signed, re-claimed
or launched. **No candidate-3 has been staged, signed or authorized, no launch
occurred, Gate C signing has not been requested for anything, and staging,
signing and launch each remain separate explicit operator approval gates** —
the fresh-candidate checklist (identity bump `D5CE3-SURVEY-2` → a fresh ≤24-byte
identity, new directory, fresh seal/freeze/payload, staged-bytes review,
preflight, Gate C Option-1 local signing, separate launch approval) is prepared
in the phase-a record §11.4. D5 stays ATTEMPTED, NOT DELIVERED: freight delivery
unproven (`D5-FREIGHT-1` failed-of-record retained), M8 optimizer route
selection not demonstrated, and the A0 native survey still requires the fresh
candidate plus operator gates.

### 2026-10-31 — D5-CORRIDOR-EXTENSION-3 fresh candidate-3 staged (offline, operator-approved)

Following the 2026-10-31 correction/review/checklist entry above, one explicit
operator staging approval was granted and the §11.4 checklist was executed.
The one-constant identity bump `TERRAIN_SURVEY_ATTEMPT` `D5CE3-SURVEY-2` →
`D5CE3-SURVEY-3` (14 UTF-8 bytes, never-consumed; milestone unchanged) plus its
two review-facing test constants was applied, and the documented three-file
offline suite re-ran at its exact baseline (**130 passed, 1 skipped, 0
failed**, exit 0). `corridor_terrain_survey_native prepare` staged
`artifacts/experiments/d5-corridor-extension-3-survey-native-candidate-3/`
(`PRELAUNCH PASS`; fresh EndpointReservation admin 44109 / game 60181; fresh
credential, never displayed). Seal
`6743fc3c8400723854cde6f2f1d643188a9c2c5583d02a7acff7e241d6898df8` ≡
`PRELAUNCH.sha256`; authorization payload digest
`75a5d226ea598056c5b32240d1c984f3f1a8578058d062213cb88548ba0ae991`; frozen
closure 3,491 entries pinning the bumped source
`1b92d191994d26f55c6c75028dacb9f886719ea39aeae730636f351c156c7d5e` and the
byte-identical staged GameScript; prerequisite freshly re-bound to the pinned
D4 candidate-5 after-save `a81ac83677732f99…6cef261`; schedule digest
unchanged `f091754de6d364d226b77555766ed5d2f3f3dfb38e23f42f5d3757fd62246c3a`.
Standalone read-only preflight: **PASS**. Independent fresh-context review:
**PASS** (full frozen sweep re-hashed 3,491 OK / 0 mismatch; lifecycle
`AUTHORIZATION_UNVERIFIED`/`CLAIM_ABSENT`; secret-adjacent files confirmed by
name/digest only). Stale candidate-2 re-verified byte-untouched (seal
`c76992…aaa2b6`). Record: phase-a record §12; evidence index E38. **Next
gates: operator Gate C Option-1 signing over `75a5d226…e991` bound to
`D5CE3-SURVEY-3` (fresh authorization; no candidate-2 authorization reuse),
then a separate explicit launch approval for exactly one survey attempt
through the remediated lifecycle, then replay + certified cleanup — never
retried on any failure. Nothing is signed, claimed, consumed or launched by
this entry.** D5 stays ATTEMPTED, NOT DELIVERED: freight delivery unproven
(`D5-FREIGHT-1` failed-of-record retained), M8 optimizer route selection not
demonstrated.

### 2026-10-31 — D5-CORRIDOR-EXTENSION-3 candidate-3 signed under Gate C (offline, operator-approved)

Following the candidate-3 staging entry above, one explicit operator Gate C
Option-1 approval was granted and the documented signing checklist
(operator-key-provisioning §1/§2/§4, the E36-validated repository-tooling
pipeline) was executed. Refusal gates were checked first and immediately
before signing (`AUTHORIZATION.json`/`CLAIM.json`/`LAUNCH-CONSUMED.json`
absent; payload digest re-verified `75a5d226…e991` over the exact canonical
bytes). The seed was extracted from the operator-held PEM into a shell
variable only (corrected exit-status/shape-checked pipeline; never printed,
argument-passed or written), the derived public key was checked equal to
the pinned anchor `5063982b…4880f`, the 64-byte Ed25519 signature was
verified under the pinned anchor **before** any write, and
`AUTHORIZATION.json` was written (sha-256
`a481dfb51d80766e8f75ae5e9ae19dc1b9758098682ee72540e9aca4abac8261`); the
seed was cleared immediately after final use. One first invocation aborted
at a verifier-API name check (`is_valid` vs `verify`) before any signature
or write — the seed was cleared there and the complete checklist re-ran
once; `sign_authorization_record` executed exactly once. Read-only
post-write verification: `verify_authorization` PASS,
`operator_key_identity` = `sha256-ed25519-public-key:cbb63ff5…40c614`
(unchanged production anchor); payload binds `attempt D5CE3-SURVEY-3` /
milestone `D5-CORRIDOR-EXTENSION-3` to seal
`6743fc3c…898df8`; `CLAIM.json`, `LAUNCH-CONSUMED.json` and the attempt
journal remain absent; read-only `verify` still returns
`AUTHORIZATION_UNVERIFIED`/`CLAIM_ABSENT` (authorized, never consumed);
standalone `preflight` → `PREFLIGHT PASS`; stale candidate-2 re-verified
byte-untouched. Record: phase-a record §12.5; evidence index E39. **Next
and final gate: one separate explicit operator launch approval, then
exactly one native survey attempt through the remediated lifecycle (the run
consumes the one-shot claim; no retry on any failure), then replay +
certified cleanup. The signature is not launch approval; nothing is
claimed, consumed or launched by this entry.** D5 stays ATTEMPTED, NOT
DELIVERED: freight delivery unproven (`D5-FREIGHT-1` failed-of-record
retained), M8 optimizer route selection not demonstrated.

### 2026-10-31 — D5-CORRIDOR-EXTENSION-3 A0 native survey COMPLETE (operator-approved launch)

Following the candidate-3 signing entry above, one separate explicit
operator launch approval was granted and `D5CE3-SURVEY-3` was executed
exactly once through the remediated lifecycle
(`corridor_terrain_survey_native run`, exit 0). The one-shot `CLAIM.json`
and `LAUNCH-CONSUMED.json` (`d5-native-launch-consumed`) were consumed
exactly once: 1 native launch (OpenTTD 15.3, pid 54600), 1 encrypted X25519
connection, 10/10 planned exchanges (`radius-00`, `tile-00`…`tile-06`,
`accept-00`, `accept-01`), 0 retries, `state_changed: false`. All native
success conditions met: runtime identity matched the pinned D4 prerequisite
world (`15.3`, seed `17`, 256×256, `start_day 712223`, encrypted); handshake
`join_secure AUTHENTICATED`, `welcome VERIFIED` (the 14-byte identity
passing the encoder that refused the 32-byte historical identity);
`result.json` `verified: true` / `NATIVE_TERRAIN_COMPLETE`, `receipt.json`
`SURVEY_COMPLETE`, every receipt funds £492,149; read-only replay →
**`SURVEY_COMPLETION_VERIFIED`** (exit 0); certified cleanup (reaped rc 0,
no remaining processes, sockets closed, credential removed, reservation
released, workspace disposed, endpoint kernel `TIME_WAIT` record,
`cleanup_complete: true`, 38-file manifest re-hash 0 mismatches); journal
stages in the exact remediated order with `CLEANUP_COMPLETED` before
`TERMINAL_SUCCESS`. Findings of record: stop tile `50862` reports **8/8**
cargo-1 acceptance in its measured radius-3 footprint, control `50351`
reports 0/8; `50096`/`50352`/`50608` buildable slopes 12/12/8,
`50864`/`50863`/`50862` flat/buildable/unowned/roadless; six
census-vs-native deviations captured as findings, nothing fused;
protocol-7 blind spots (vehicle reachability, road-bit directions,
front-road station buildability, pathfinding) stay UNKNOWN. Record:
phase-a record §13; evidence index E40. **A0_SURVEY: COMPLETE — VERIFIED
NATIVE. Candidate-3 is permanently consumed history: never re-run,
re-signed or re-claimed; stale candidate-2 stays preserved untouched.
A1 (corridor spur + bay truck stop) is unblocked but needs its own scoped
design, fresh never-consumed candidate staging, independent review, fresh
Gate C signature and a separate explicit launch approval.** D5's freight
delivery (`D5-FREIGHT-1` FAILED-of-record) and M8 optimizer route selection
remain unproven and are not covered by the survey result.

A documentation-only handoff is complete when links and evidence references are
valid, implementation bytes remain unchanged, the final diff is reviewed and fresh
checks are reported separately from inherited validation. No commit/push is needed.

### 2026-11-01 — D5 A1 v2 offline design carried through implementation (offline, no staging)

The A1 design of record (postmortem §3; phase-a §14.1) is carried through
source, GameScript and tests offline. Four-op v2 schedule: op-0 `full`
`ROAD_FULL 50096 → 50864` (branch run 4 tiles), op-1 `road`
`50095 ↔ 50096` (the wall join), op-2 dedicated **`spur`** kind — its own
admission clause, never a broadening of `full`/`road` —
`GSRoad.BuildRoadFull(50864, 50863)` (company-road start corner into
company-invalid roadless ground, `covered==1/pairs_ok==0` pre,
`covered==2/pairs_ok==1` post), op-3 bay truck stop at tile **50862**
fronting **50863** (`STATION_NEW`, non-drive-through). Witness of record:
31 tiles / 30 pairs ending `… 50864, 50863, 50862`; the 50862-facing road
bit of 50863 is provable only by the terminal route-witness pair (no
road-bits getter in the 15.3 GameScript API), so the terminal station
facts gate the route read. `EXTENSION_SCHEDULE_VERSION = 2`, attempt
`D5-CORRIDOR-EXTENSION-3`; the consumed v1 candidate-2 stays preserved
forever and replays read-only (`ATTEMPT_FAILED_EVIDENCE_PRESERVED`
verified live) against `extension_schedule_v1()` re-derivation (digest
match True). v2 plan digest of record:
`aa88bc99fb80056423b4d1fdc40994abf66aff3afffeb51c710e163ba5447535`.
Budgets: 13 planned exchanges (4 × 3 + route read) in an 18-request cap;
funds arithmetic `492149 − (454+71+143+307) = 491174`. Survey rebinds to
the consumed A0 candidate-3 evidence (plan `82246eb6…`, seal `6743fc3c…`,
tiles += 50862 flat/buildable/roadless, acceptance `{50351: 0, 50862: 8}`).

Files of record: `app/simulation/openttd/corridor_construction.py`
(shared protocol-4 `spur` contract + `verify_corridor_route` pairwise
adjacency rule), `app/simulation/openttd/proof/corridor_extension_native.py`
(v2 pipeline, version selector, version-scoped attempt identity,
extension-local `expected_readback_policy()` with the spur admission
prose, replay inventory guard), `app/simulation/openttd/d5_extension_package/main.nut`
(4 stages, spur RunCommand/Eligible/PostHolds/Step, dispatcher + `q.op`
whitelist — a missing spur whitelist was found by tests and closed),
`tests/test_corridor_extension.py` (33 PASS) and
`tests/test_corridor_extension_native.py` (79 PASS, incl. v1
re-derivation, version selector, version-scoped identity, terminal
witness-pair semantics, consumed candidate-2 read-only replay). All five
focused suites green in one run (exit 0, 240 tests). Independent
fresh-context review: no blockers or majors; applied minors recorded
(route adjacency validator, replay inventory guard, expected-readback
prose, docstring/comment wording, append-only v2-correction note in the
2026-10-28 handoff design doc). Route wire sizing offline: 636 ≤ 640
bound (thin but bound, not assumed). Nothing staged, signed, authorized,
launched or claimed; no commit. Risks/UNKNOWN stance unchanged: wheel
reachability, road-bit directions, pathfinding and the spur's native
quote stay UNKNOWN until native admission. Next: fresh never-consumed
candidate staging (`d5-corridor-extension-native-candidate-3`), PRELAUNCH
- independent review, Gate C Option-1 signing, separate explicit launch
  approval — each its own operator-approved step. Record: phase-a §14;
  evidence index E41.

### 2026-11-01 — D5-CORRIDOR-EXTENSION-3 fresh A1 candidate-3 staged (offline, operator-approved)

The operator authorized staging ONE fresh never-consumed extension
candidate at
`artifacts/experiments/d5-corridor-extension-native-candidate-3/`:
signing, authorization, claim and launch explicitly out of scope. Target
verified absent; production CLI `prepare`
(`prepare_extension_candidate` + `extension_preflight`, pinned D4
candidate-5 prerequisite) returned **PRELAUNCH PASS**, then standalone
read-only `preflight` returned **PREFLIGHT PASS**; standalone `verify`
returns the expected structured `AUTHORIZATION_UNVERIFIED`/`CLAIM_ABSENT`.

Staged identity of record: attempt `D5-CORRIDOR-EXTENSION-3` (the
consumed v1 attempt name `D5-CORRIDOR-EXTENSION-2` appears zero times in
the staged bytes); seal
`404d42d9fa1e113542e74655858f6bc669407d611057eec0c036612ddfa6acd8`
(`PRELAUNCH.sha256` == recomputed sha256 of `PRELAUNCH.json`);
authorization payload digest
`c511dd38a068c1cef5539d3cc422819ef76d73842c42e4d1601b4199debdf94f`
(independently recomputed offline from the staged canonical bytes);
schedule `EXTENSION_SCHEDULE_VERSION == 2` — op-0 `full` 50096→50864,
op-1 `road` 50095↔50096, op-2 `spur` 50864→50863, op-3 station 50862
fronting 50863 — with digest
`aa88bc99fb80056423b4d1fdc40994abf66aff3afffeb51c710e163ba5447535`
(staged == derived); budgets {1 launch, 1 connection, 0 retries/
reconnects, 18-request cap, 13 planned, 512/640 wire bounds, per-op
ceiling 2000, expected funds 492149}; witness 31 tiles / 30 pairs ending
`… 50864, 50863, 50862`; design pins
`d5-corridor-extension-design-pins-v2` (spur_start 50864, spur_end
50863, branch_stop 50862, branch_front 50863); world bound to the pinned
D4 candidate-5 after-save
`a81ac83677732f9951f5acb3a119395020e49b2317adb3419edf6bc626cef261`
(after.sav); A0 survey rebind to the consumed
`d5-corridor-extension-3-survey-native-candidate-3` (plan digest
`82246eb6…ef8d9` and seal `6743fc3c…898df8`, each appearing exactly once
in the staged bytes); v2 expected-readback prose with the spur admission
clause embedded; frozen closure 3,490 entries pinning the v2 GameScript
`RoadFreightProof/main.nut` (`78e5476f…da46a`, byte-identical to the
live source) and `corridor_extension_native.py` (`afdaa970…382a9`).

Inventory: `PRELAUNCH.json`, `PRELAUNCH.sha256`,
`graphics-identity.json`, `isolated/` pre-launch skeleton with all
runtime directories empty. No `AUTHORIZATION.json`, no `CLAIM.json`, no
`LAUNCH-CONSUMED.json`, no journal, no saves, no launch artifacts exist.
Consumed evidence untouched: extension candidate-2 manifest re-verifies 0
mismatches (48 entries), survey candidate-3 listing complete and
unchanged (Oct 31 mtimes). Independent fresh-context review:
**READY-FOR-GATE-C** — zero blockers, zero majors, zero minors; three
historical documentation notes only (postmortem §1 digest/seal wording,
missing literal E-row for the consumed v1 directory, artifacts/ gitignored
untracked), none touching the staged bytes.

**Nothing was signed, authorized, claimed, consumed, launched or
committed by this entry; no commit landed.** D5 stays ATTEMPTED, NOT
DELIVERED: freight delivery unproven (`D5-FREIGHT-1` failed-of-record
retained), M8 optimizer route selection not demonstrated, wheel
reachability / road-bit directions / pathfinding / the spur native quote
stay UNKNOWN. Stopped at the Gate C signing approval: Option-1 signing
over seal
`404d42d9fa1e113542e74655858f6bc669407d611057eec0c036612ddfa6acd8` /
payload
`c511dd38a068c1cef5539d3cc422819ef76d73842c42e4d1601b4199debdf94f` and
the separate explicit launch approval remain ungranted operator gates. Record: phase-a §15; evidence index E42.

### 2026-11-01 — D5-CORRIDOR-EXTENSION-3 A1 candidate-3 Gate C Option-1 signed (operator-approved)

The operator authorized Gate C Option-1 signing of the existing staged
candidate `artifacts/experiments/d5-corridor-extension-native-candidate-3/`
(no claim, no launch, no candidate modification; launch approval remains
a separate gate). The documented checklist
([key provisioning §1/§2/§4](docs/handoff/2026-10-17/operator-key-provisioning.md),
pipeline of §12.5/E39) was executed: refusal gates first (no
`AUTHORIZATION.json`/`CLAIM.json`/`LAUNCH-CONSUMED.json`/journal), seal
re-verified `404d42d9fa1e113542e74655858f6bc669407d611057eec0c036612ddfa6acd8`,
payload digest re-verified
`c511dd38a068c1cef5539d3cc422819ef76d73842c42e4d1601b4199debdf94f`,
seed handled only as an environment variable via the corrected pipeline
(never printed/argument-passed/written, cleared after final use), derived
key ≡ pinned production anchor `5063982b…4880f`, signature verified
under the pinned anchor over the exact canonical payload bytes before
any write; `AUTHORIZATION.json` written exactly once, record sha
`371a524b85add4347a991478909a04da3e7dac8b62b2636b6c7694b32bebe200`. A
first invocation failed at shell setup (`shopt -s pipefail`) before any
seed extraction or write and was re-run once from the refusal gates. A
single read-only inspection of procedure/candidate state was delegated
to a fresh subagent; the READY-FOR-GATE-C review was not repeated.

Post-sign read-only state: `verify_authorization` → PASS with
`operator_key_identity sha256-ed25519-public-key:cbb63ff58f17f13df3e1be0735fad18497e3a0c6ad6b5dd55491d708ae40c614`;
`CLAIM.json`/`LAUNCH-CONSUMED.json` remain absent; standalone `verify` →
`AUTHORIZATION_UNVERIFIED`/`CLAIM_ABSENT` (exit 1); standalone
`preflight` → **PREFLIGHT PASS**. No native execution, no AdminPort
connection, no OpenTTD launch, no restage, no commit.

**Signing is not launch approval.** D5 stays ATTEMPTED, NOT DELIVERED:
freight delivery unproven, M8 route selection not demonstrated. Stopped
at the separate Native Launch Approval gate. Record: phase-a §16;
evidence index E43.

### 2026-11-01 — D5-CORRIDOR-EXTENSION-3 A1 candidate-3 native launch COMPLETE (verified)

The operator granted exactly one native launch of A1 candidate-3 (no
retry, no new candidate, no freight/M8 progression). The remediated
lifecycle ran once: `corridor_extension_native run
artifacts/experiments/d5-corridor-extension-native-candidate-3` →
**exit 0, `NATIVE_EXTENSION_VERIFIED`, verified true**. Consumption:
preflight PASS, one-shot `CLAIM.json` consumed (bound to authorization
sha `371a524b85add4347a991478909a04da3e7dac8b62b2636b6c7694b32bebe200`,
operator identity
`sha256-ed25519-public-key:cbb63ff5…40c614`), `LAUNCH-CONSUMED.json`
written; 1 launch (OpenTTD 15.3, pid 29574), 1 connection, 13/18
requests, 0 retries. All four v2 ops built, each a `NATIVE_STATE_CHANGED`
with native quote == cost under the £2,000 per-op ceiling: op-00 full
50096→50864 £1,144; op-01 road 50095↔50096 £142; op-02 spur
50864→50863 £299 (first native spur); op-03 station 50862 fronting
50863 £307 with `DISTINCT_NEW_STATION` (sid 2 vs 0/1). Route
`ROUTE_VERIFIED` 30/30 pairs, funds read natively £490,257 (start
£492,149, spend £1,892). Phase `PHASE_COMPLETE`; saves: before
`59fbb20a…5397c` (== staged world bind), authoritative `after.sav`
`3748e00c…5420bd` bound into `receipt.json`, diagnostic
`ca08e171…dd84b`. Replay `verify` → `EXTENSION_COMPLETION_VERIFIED`
(exit 0); certified cleanup all flags true (reaped pid 29574, sockets
closed, credential removed, reservation released, workspace disposed,
kernel `TIME_WAIT` record); manifest 0 mismatches.

Wide-open A1 risk status update: wheel reachability, road-bit
directions and pathfinding remain demonstrated for construction only —
actual truck traversal is freight scope. The cargo-1 acceptance census
on this attempt's after-save is, per the receipt statement, a separate
gated read-only survey session required before any freight order or
vehicle purchase; no candidate was staged and no freight/M8 work was
started. D5 stays ATTEMPTED, NOT DELIVERED: freight delivery
(`D5-FREIGHT-1` FAILED-of-record) and M8 route selection remain
unproven. A1 construction is COMPLETE (verified native) within its v2
scope. Nothing committed. Record: phase-a §17; evidence index E44.

### 2026-11-01 — D5 post-A1 acceptance census designed (offline, independent review applied)

Offline only (fresh-context inspection + review subagents; no code,
no staging, no signing, no claim, no launch, no AdminPort): the
cargo-1 acceptance census for the consumed A1 world was designed —
[docs/d5-post-a1-acceptance-survey-design.md](docs/d5-post-a1-acceptance-survey-design.md).
Instrument: versioned retarget of the protocol-6 `D5-ACCEPT-SURVEY`
pipeline to attempt `D5-ACCEPT-SURVEY-2` (`SURVEY_SCHEDULE_VERSION 2`,
`EXTENSION_SCHEDULE_VERSION` precedent), prerequisite = consumed A1
candidate-3 (attempt `D5-CORRIDOR-EXTENSION-3`, after-save
`3748e00c…5420bd`, replay `EXTENSION_COMPLETION_VERIFIED`). 4-exchange
census: radius-00 (tile null), accept-00 control 50351 = 0
(positive-control anomaly halts, never relabeled), accept-01 stop
50862 = 8/8, prod-00 = 104; `max_cost = 0`, zero mutation expected;
cleanup certified; replay must return `SURVEY_COMPLETION_VERIFIED`.
Implementation plan (§5): version selector + v2 schedule/plan literal
in `corridor_accept_survey_native.py`, plan contract versioned
(`schema_version` 2, funds pin 490,257, tile set, drift assertion),
v2 GameScript re-bake limited to pin-table data guards +
`survey_planned` rows (B1: 50862 is not pinned in the v1 Nut table
and the 8-row stage matcher would halt a 4-exchange census), pin/
schedule wire↔Nut binding test, consumed `D5-ACCEPT-SURVEY-1` +
A1 candidate-3 byte-frozen. Vehicle reachability, road-bit directions
and pathfinding stay open (census proves acceptance only, not
traversal). No candidate created, nothing consumed, nothing committed.
Next gates: implementation review, then fresh never-consumed staging
approval (`d5-accept-survey-native-candidate-2`), then Gate C signing,
then a separate launch approval — each its own record. Record: design
doc §7; evidence index E45.

### 2026-11-01 — D5-ACCEPT-SURVEY-2 implemented offline (independent review applied)

Offline only (no staging, no signing, no claim, no launch, no
AdminPort, nothing written under `artifacts/`): the §5 implementation
plan is complete. `app/simulation/openttd/corridor_accept_survey.py`
carries the version selector (`SURVEY_SCHEDULE_VERSION = 2`, in the
wire module per the latest decision, superseding the design doc §7
M3 proof-module wording) and the versioned plan contract
(`schema_version` 2, funds pin 490,257, tiles 50351/50862, four-row
schedule, v1+v2 drift assertions, branched `coherent()` with the v1
pins and messages byte-exact, `survey_plan_v2()`,
`staged_survey_plan()`). The v1 plan digest is preserved:
`2d2e47b2…02e7` equals the consumed candidate-1 pinned
`plan_model_digest`. `corridor_accept_survey_native.py` carries the
native versioning on the extension precedent: attempt map
(`D5-ACCEPT-SURVEY-1` history / `D5-ACCEPT-SURVEY-2` current), schema
map, per-version prerequisite pins (v2 = consumed A1 candidate-3,
after-save `3748e00c…5420bd`, end-to-end re-verified through seal,
consumed claim, receipt binding, `EXTENSION_COMPLETION_VERIFIED`
replay and welcome identity), version-scoped schedules (the consumed
8-row v1 record reproduced exactly; the fresh 4-row v2 census),
policy/budgets/hypotheses/census re-bound fail-closed from the A0
acceptance facts, and version-aware preflight/replay identity/replay
verification. `main.nut` re-baked exactly to B1's scope: 4-row
`survey_planned`, `ACCEPT_CANDIDATES [50862]`, comments; no
handler-logic change. Tests rewritten for v2 with a v1
replay-compatibility block: 30 + 35 PASS; consumed v1 candidate-1
replays `SURVEY_COMPLETION_VERIFIED` through the production verifier;
wire↔Nut pin-binding test; drift tests tamper only tmp copies.
Evidence runs all exit 0: two suites 65 tests; four-suite (incl.
terrain-survey pairs) 148 passed + 1 skipped; protocol-5 freight
suite 42 passed; A1 five-suite 240-test baseline. All consumed
precedent records byte-verified through their own seals/claims after
the edit session. Independent fresh-context review (design doc §8):
READY; 3 minors + 1 nit applied (v1 byte-exact strings restored with
the v2-facing renames recorded; symmetric version-isolation tests
added A1-refuses-v1; fail-closed census-state gates; implicit v1
default argument removed). Vehicle reachability, road-bit directions
and pathfinding stay open (census proves acceptance only, not
traversal). Nothing committed. Next gates (each its own operator
record): §6 item-3 fresh never-consumed staging approval
(`d5-accept-survey-native-candidate-2`), fact recording, Gate C
signing, separate launch approval, census report. Record: design doc
§8; evidence index E46.

### 2026-11-01 — D5-ACCEPT-SURVEY-2 fresh candidate staged (offline, READY-FOR-GATE-C)

One operator approval, this gate only. Production CLI `prepare` on a
fresh never-consumed directory
`artifacts/experiments/d5-accept-survey-native-candidate-2/` →
`PRELAUNCH PASS` (exit 0); standalone read-only `preflight` →
`PREFLIGHT PASS` (exit 0); standalone `verify` →
`AUTHORIZATION_UNVERIFIED`/`CLAIM_ABSENT` (exit 1, correct
pre-signing state). No signing, no claim, no launch, no AdminPort,
no OpenTTD execution, no retry, no directory reuse. Fresh-context
prerequisite inspection: `PREREQUISITE VERIFIED` — A1 candidate-3
seal `404d42d9…6acd8` intact, claim consumed, after-save
`3748e00c…5420bd` verified, receipt binding + acceptance-recheck
statement verbatim, funds 490,257 proven from the A1 route receipts
(lives in `receipt.json`/`result.json` `route.funds`, not the A1
PRELAUNCH.json), A0 census {50351: 0, 50862: 8}, GameScript census
pin table confirmed (4 rows, control 50351, candidate 50862, zero
v1 ids). Staged facts: seal `237a4f84…37daa4`; attempt
`D5-ACCEPT-SURVEY-2`, schema `d5-accept-survey-prelaunch-v2`;
v1 consumed name zero occurrences in staged text files; v2 plan
model digest `67fce856…80be2` == `survey_plan_v2().digest`;
schedule digest `1222db02…389d` (staged == derivation); budgets
1/1/32-cap/4-planned, 512/640 bytes, funds 490,257, `max_cost 0`;
hypotheses `RETAINED_CENSUS_REBOUND` {50351: 0, 50862: 8} from the
consumed A0 facts; staged `main.nut` byte-identical to the shipped
package; staged `source.sav` == A1 after-save; welcome equality
with the A1 record; frozen closure 3,491 entries (14 sampled
recomputes, 0 mismatches) pinning wire module `abe668f0…1eb2`,
native module `4f28e9ee…7d41`, GameScript `0337fb36…97ae` and the
after-save; authorization payload digest `b1f3e209…00bd` recomputed
independently; no authorization/claim/launch-consumed/journal file
anywhere in the tree. Independent fresh-context staged-byte review:
`READY-FOR-GATE-C`, 0 blockers/majors/minors, 2 recorded NITs
(`plan_digest_of` hashes the list-of-dict form; staged
`info.nut` is the by-design save-restore identity via
`staged_composition()`, preflight-verified, not drift). All
consumed precedent records byte-untouched, seals re-verified before
and after. Nothing committed. Stop: Gate C Option-1 signing over
`237a4f84…37daa4`/`b1f3e209…00bd` and the separate launch approval
are ungranted operator gates. Record: design doc §9; evidence index
E47.

### 2026-11-01 — Gate C Option-1 signing executed for D5-ACCEPT-SURVEY-2 (E48, design §10)

One operator approval, this signing operation only. Pre-signing
re-validation matched every expected identity exactly: seal
`237a4f84…37daa4`, payload digest `b1f3e209…00bd`, plan digest
`67fce856…80be2`, schedule digest `1222db02…389d`, A1 after-save
`3748e00c…5420bd`, A1 prereq seal `404d42d9…6acd8`; refusal gates all
clean (`AUTHORIZATION.json`/`CLAIM.json`/`LAUNCH-CONSUMED.json`/
journal absent). Documented checklist executed: seed env-only
(no seed material in chat/logs/files), derived key == anchor
`5063982b…4880f`, signature verified under anchor pre-write, single
`write_authorization_record`, `unset SEED_HEX` after final use.
Two earlier internal script invocations refused cleanly with nothing
written: run 1 `AttributeError: … ed25519_rfc8032 has no attribute
public_key_hex` (module exposes `public_from_seed`), run 2
`REFUSED: signature does not verify under the anchor` (anchor hex
string passed instead of `bytes` to total `verify`; script bug, not
tooling). Result: `AUTHORIZATION.json` record sha ==
`authorization_sha256` `d87c2c450e192e4341f8bf4ac6a6ff553194ac0134f
8353293bff42250bf4ae3`, `operator_key_identity`
`sha256-ed25519-public-key:cbb63ff58f17f13df3e1be0735fad18497e3a0c6a
d6b5dd55491d708ae40c614`, payload binds attempt `D5-ACCEPT-SURVEY-2`/
milestone `D5-ACCEPT-SURVEY`/seal `237a4f84…37daa4`. Post-signing
read-only re-checks: `verify` → `AUTHORIZATION_UNVERIFIED`/
`CLAIM_ABSENT` (exit 1), `preflight` → `PREFLIGHT PASS`; exactly one
new file in the candidate root, all other staged bytes unchanged. All
consumed precedent records re-sealed byte-identical after signing
(candidate-1 `38b7667e…b06b`, A1 candidate-3 `404d42d9…6acd8`,
extension candidate-2 `6d912a3d…c15d`, A0 survey candidate-3
`6743fc3c…8df8`). No claim, no launch-consumption, no journal, no
native execution, no commit. Signature is NOT launch approval: the
separate explicit native launch approval is the next ungranted
operator gate. Record: design doc §10; evidence index E48.

### 2026-11-01 — D5-ACCEPT-SURVEY-2 native census lifecycle COMPLETE (E49, design §11)

One operator approval, this lifecycle only. Pre-launch revalidation
matched all identities cryptographically (seal `237a4f84…37daa4`,
payload `b1f3e209…00bd`, record `d87c2c45…4ae3` =
`VerifiedAuthorization` under anchor `cbb63ff5…c614`, plan
`67fce856…80be2`, schedule `1222db02…389d`, schema v2, A1 after-save
`3748e00c…5420bd`, A1 prereq seal `404d42d9…6acd8` consumed);
preflight `PREFLIGHT PASS` immediately before consumption; executed
the signed `execution_command` exactly. `CLAIM.json` consumed once
(`launches_allowed: 1`, `retries: 0`, binding all three digests),
`LAUNCH-CONSUMED.json` schema `d5-native-launch-consumed`. One
OpenTTD 15.3 launch (pid 71098), one encrypted X25519 connection, 4
of 32 requests, 0 retries/reconnects, welcome == signed expectation
(seed 17, 15.3, 256×256, start day 712223). Observed census: radius
**3**; control 50351 acceptance **0**; A1 station 50862 acceptance
**8/8**; production **104**; all receipts sealed + plan-bound with
funds £490,257; every response `cost: 0`; `state_changed: false`.
No mutation of any kind. Run exit 0 `NATIVE_SURVEY_COMPLETE`
`verified: true`; replay `verify` → `SURVEY_COMPLETION_VERIFIED`
exit 0. Session-owned `session-before.sav` re-save sha
`1966b5c7…d40b7` bound into the receipt (OpenTTD re-serialization of
the identical pinned world state; verifier re-derives and accepts —
documented owned-save behavior, not drift); A1 record `after.sav`
re-hashed exactly `3748e00c…5420bd` post-run. Cleanup certified:
`reaped: true` (returncode 0), credentials removed, sockets closed,
AdminPort 53023 canceled + probe false + rebindable, workspace
disposed, zero cleanup errors; manifest 24 entries 0 mismatches;
frames/requests/responses/identities/logs retained. No freight
delivery, no reachability, no traversal, no YAPF, no M8 claims. No
commit. Record: design doc §11; evidence index E49.

### 2026-11-01 — D5 Freight Delivery v2 design review COMPLETE (offline, three fresh-context reviewers; E50)

Explicit operator request (full key-file refresh chosen; `OpenTTD-Knowledge/`
left untouched). Baseline verified first: branch `miles/fright-delivery`,
HEAD `fee7459`, working tree clean; no git mutations, no launch, no
AdminPort, no candidate, no claim, no signing at any point before, during or
after this documentation step. Three fresh-context read-only reviewer
agents (engine/world, protocol/budget, accounting/proof) cross-reviewed
against primary sources. Verdict: **`DESIGN READY WITH CONDITIONS`**. One
BLOCKER (no offline engine-ID provenance authority on disk; legacy engine-123
enumeration is a different world) plus MAJORs: 31-tile witness vs 24-cap
route shape, A1-world pins stale (funds 490,257, bay 50862/sid 2, delivery
industry UNKNOWN), `OF_FULL_LOAD`/full-load pins, single-cycle-only
schedule/verifier, funds ledger enforcing only purchase with running-cost
attribution needing an operator decision, no per-attempt 60-day authority.
Code-verified arithmetic: fixed 10 + per-cycle 3 + tail 2 within cap 32 →
max **6 cycles** (5 with per-cycle finance read, ~4 wall-saturated); plan the
count at staging. Quote-first purchase feasible as built; quote==realized
native precedent is legacy-lane only. Zero-file-write review constraints
were followed exactly; the four cross-references plus the review record are
the only files this step created (new record +
EVIDENCE_INDEX/AI_HANDOFF/TASKS/README pointers, no historical bytes edited).
No implementation authorized; the next phase needs separate explicit
operator authorization. Record:
[docs/d5-freight-delivery-v2-design-review-2026-11-01.md](docs/d5-freight-delivery-v2-design-review-2026-11-01.md);
evidence index E50.

### 2026-11-01 — D5 Freight Delivery v2 offline implementation complete (E51)

Explicit operator authorization covered offline source implementation and
offline testing only. Additive over the frozen v1 protocol-5 bytes, which were
never modified: wire contract `app/simulation/openttd/corridor_freight_v2.py`
(protocol 8; 768/1400/1450; schedule version 2; 30 exchanges = fixed 10 +
6 cycles×3 + tail 2 fixed by the E50 §4 arithmetic; strict per-op echo
subsets; provisional census engine pin 123 verified natively fail-closed per
Option B; quote-first purchase ≤ £5,000; 60-day per-attempt authority with a
10-day cycle lease; `OF_FULL_LOAD` never issued; partial departure gate
`0 < load ≤ capacity`; monitor latch, typed `ZERO_DEPARTED`, funds ledger
with a 0-residual equation and duration echoes),
`app/simulation/openttd/d5_freight_v2_package/main.nut` (save-restore-bounded
v2 handler + `NetworkFreightProof` bridge), and
`app/simulation/openttd/proof/corridor_freight_v2_native.py` (pinned A1
candidate-3 prerequisite binding re-verified end-to-end; witness-derivation
route provenance, distinct route/witness digests; preflight refusal gates;
ACTIVE-only protocol-8 secure session; production site request exactly
640 B; exchange timing from phase windows with clamps; per-request wire
trust anchor; one-launch executor; replay arms `RECEIPT_VERIFIED` / `PHASE_HALTED_EVIDENCE_PRESERVED` /
`UNRESOLVED_ATTEMPT_EVIDENCE_PRESERVED` / `ATTEMPT_FAILED_EVIDENCE_PRESERVED`).
Offline validation in one session: `tests/test_corridor_freight_v2.py` 48
passed and `tests/test_corridor_freight_v2_native.py` 67 passed (both exit 0,
all dots), the v2 VM suite stayed 48-green across the runner fix, protocol-8
site probe re-ran 640 B / vread 409 B, ruff clean and `ty` clean on all v2
test files (`typings/squirrel.pyi` stub added); one latent runner defect was
fixed during validation (`prepare_candidate` `pin_provenance.source` bound
the staged scalar) and the re-seal proof sites were made JSON round-trip
stable. Nothing staged, signed, authorized, launched, claimed or committed;
nothing written under `artifacts/`; the root `--version` file untouched.
Stop point: §10 item-5 gates — staging approval, independent review, Gate C
signing and a separate explicit launch approval each remain ungranted
operator gates. Evidence index E51.

### 2026-11-01 — D5 Freight Delivery v2 candidate staged (E52)

Explicit operator authorization granted in-session covered the staging gate
only (§10 item 5, first gate), nothing else. One command, first attempt, exit
0: `.venv/bin/python
-m app.simulation.openttd.proof.corridor_freight_v2_native prepare
artifacts/experiments/d5-corridor-freight-native-candidate-2` printed
`PRELAUNCH PASS`. The staged candidate of record:
`artifacts/experiments/d5-corridor-freight-native-candidate-2/`, attempt
`D5-FREIGHT-2`, kind `freight`, schema `d5-freight2-prelaunch-v1`, seal
(`PRELAUNCH.json` sha256, also `PRELAUNCH.sha256`)
`35557a74c33188fb2555a43871025099b2998eea317d8bbf9cf047a8d5b676d4`; the
pinned prerequisite re-verified against the retained
`d5-corridor-extension-native-candidate-3` record (attempt
`D5-CORRIDOR-EXTENSION-3`, after-save `3748e00c…5420bd`); plan/schedule
digest `22bdb874…60f` and the budgets 1 launch / 32 requests / 60 days
unchanged from the E51 pins; binary sha `276d5b…904c` verified and no
identical process running; endpoints reserved then released (game 57627,
admin 34189); an isolated retained workspace with an owned session key and
the composed v2 GameScript was created, the launch argv was recorded and
never executed. Read-only re-proofs: standalone `preflight` →
`PREFLIGHT PASS`; `verify` → `AUTHORIZATION_UNVERIFIED` / `CLAIM_ABSENT`,
exit 1 ("the candidate was never consumed by an operator authorization; no
verified receipt is possible"). `AUTHORIZATION.json` does not exist and no
claim was consumed: staging wrote no authorization. Nothing was signed,
launched, connected or attempted; the v1 candidate-1 record, the root
`--version` file and every other retained artifact stayed untouched; no
commit or push. Remaining operator gates: independent read-only review,
Gate C signing and a separate explicit launch approval. Evidence index E52.

### 2026-11-01 — D5 Freight Delivery v2 E53 fix round (offline, no staging)

Offline fix round against the independent implementation review of the
E51/E52 work (branch `miles/fright-delivery` HEAD `bf6cc0b`; the v2
implementation and E52 staging-record documentation were committed as
`bf6cc0b` before this round). Applied, all offline:

1. **Freight state transitions fail-closed (blockers a–c):**
   `d5_freight_v2_package/main.nut` LoadWatch now gates the typed
   `ZERO_DEPARTED` event on a sampled pickup visit plus a past-the-stop
   reading with zero load and a zero pickup-monitor keeper reading — the
   depot-to-pickup travel leg and standing-at-stop samples stay waiting
   (`WINDOW_EXHAUSTED`, lease-bounded), off-route samples type
   `INVALID_ROUTE` loaded or empty; LOADED is typed only at the verified
   departure sample with `GetIndustryPickupAmount(keep=true) == load` and a
   new `pickup_amount` echo; DeliverWatch gates every sample on
   `loc == this.delivery` and the `DELIVERED` reply echoes `r.position`.
   The wire contract (`corridor_freight_v2.py`) gained the matching echo
   subsets and Python-level evidence gates
   (`verify_freight_loaded_v2`/`verify_freight_zero_departed_v2`
   monitor requirements, `verify_freight_delivered_v2` pinned-bay
   requirement).
2. **60-day aggregate economy-day authority enforced (blocker d):** all
   three watch windows stage the uniform 10-economy-day lease
   (`window_day_cap`; `FREIGHT_CYCLE_DAY_CAP_V2 × 6 == 60` import
   invariant). `StartOp` echoes its day of record; the day ledger is
   latched at `start-00`; `_freight_day_authority` gates every watch
   dispatch pre-send; `_freight_verify_step_v2` hardens replay (staged
   budget-echo drift refusals, missing day reference, ledger span
   regression or > 60 typed defects);
   `verify_freight_attempt_v2` emits `day_ledger`.
3. **CONTEXT.md authority restored:** `bf6cc0b` had re-tabbed two JSON
   code-fence hunks inside the pinned file; the exact pinned bytes
   (sha256 `36648f9c…cc29`, supersession record ADR-014) were restored and
   sha256-verified against the pinned commit's `CONTEXT.md` (`fee7459`).
   The protected authority checks pass again (see 4).
4. **Verification of record (all offline, exit 0 where stated):**
   `tests/test_corridor_freight_v2.py` 61 passed +
   `tests/test_corridor_freight_v2_native.py` 67 passed in one run
   (13 new E53 regression tests in the VM suite); protected authority
   checks 118 passed (test_authority_supersession + test_historical_protection
   + test_industry_production_proof + test_structural_production);
   `ruff check` clean on every touched path; `git diff --check` clean;
   `uvx ty` reports only the same five pre-existing diagnostics present at
   `bf6cc0b`. New schedule/plan digest of record
   `ed5bad82…b1ff4` (E51/E52's `22bdb874…60f` stages exactly the pre-E53
   schedule); plan-model `779ff9ee…12c4`, route `b2f80f46…7131`, witness
   `f1f00e13…686c` unchanged.
5. **Docs corrected:** REPRODUCE.md (suite counts, phase-budget exchange
   timeouts of record 10 s/65 s, updated digest, E53 addendum), AI_HANDOFF.md
   (commit of record `bf6cc0b` acknowledged; CONTEXT.md pin status
   restored), review doc §12 E53 section appended, evidence index E53 row.
6. **Staged-candidate staleness recorded:** the staged, never-consumed
   `artifacts/experiments/d5-corridor-freight-native-candidate-2` keeps the
   pre-E53 seal and becomes stale-by-source-drift against this working
   tree by construction — never re-staged, re-sealed or relabeled; its
   authorization state stays `PENDING` (`AUTHORIZATION_UNVERIFIED` /
   `CLAIM_ABSENT`). Pre-launch gates reset: the next candidate must be
   staged fresh, independently reviewed, Gate C signed and separately
   launch-approved.

Nothing staged, signed, authorized, launched, claimed or committed by this
round; nothing written under `artifacts/`; the root `--version` file
untouched. One pre-existing baseline failure unrelated to D5 was observed
during validation and recorded unchanged
(test_structural_world cargo-catalog fixture manifest digest mismatch,
present at `bf6cc0b`; evidence intact, not regenerated). Evidence index
E53; review doc §12 is the authoritative fix record.

### 2026-11-02 — D5 Freight Delivery v2 candidate staged fresh (D5-FREIGHT-3, E54)

Explicit operator authorization in-session covered the staging gate only
(review §10 item 5, first gate). Identity step of record first (E37
precedent): `FREIGHT_ATTEMPT_V2` bumped `D5-FREIGHT-2` → `D5-FREIGHT-3` in
`corridor_freight_v2.py` (module docstring and the one literal test
assertion updated with it) so the once-staged, never-consumed
`D5-FREIGHT-2` name is never reused for a fresh candidate; the attempt
identity feeds the plan model, so the plan-model digest of record moved to
`19112a9b…76e0` (pre-edit `779ff9ee…12c4` stays on the stale candidate-2).
Both v2 suites re-verified exit 0 (61 + 67) and ruff stayed clean on the
touched paths before staging.

One command, first attempt, exit 0: `.venv/bin/python
-m app.simulation.openttd.proof.corridor_freight_v2_native prepare
artifacts/experiments/d5-corridor-freight-native-candidate-3` printed
`PRELAUNCH PASS`. The staged candidate of record:
`artifacts/experiments/d5-corridor-freight-native-candidate-3/`, attempt
`D5-FREIGHT-3`, kind `freight`, schema `d5-freight2-prelaunch-v1`, seal
(`PRELAUNCH.json` sha256, also `PRELAUNCH.sha256`)
`f308d32722508e3ed29bd3d297e9152cc5f8b33dae1ff1f666c02cd5bfd18a0e`; the
**E53 schedule of record** is what this candidate binds: plan/schedule
digest `ed5bad82…b1ff4` (staged == live derivation; uniform 10-economy-day
`window_day_cap` lease on all three watch windows), plan model
`19112a9b…76e0`, route `b2f80f46…7131` / witness `f1f00e13…686c`
unchanged; budgets unchanged {1 launch, 1 connection, 32 requests, 30
planned, 6 cycles, 60 days, window_day_cap 10, watch_ticks 2048,
running_cost_allowance 12, max_cost 5000, funds 490257}; the pinned A1
prerequisite re-verified end-to-end (`D5-CORRIDOR-EXTENSION-3`, seal
`404d42d9…6acd8`, after-save `3748e00c…5420bd`,
`EXTENSION_COMPLETION_VERIFIED`; world = the A1 `after.sav` in the
prerequisite source-save load mode, pinned welcome seed 17 / 15.3 /
256×256 / start_day 712223); binary sha `276d5b…904c`; endpoints game
58339 / admin 44483 reserved then released; isolated retained workspace
`openttd-15.3-uwcxtrxo` with the composed v2 GameScript (frozen closure
3,493 entries pinning the wire module `1efa9421…13a8`, runner module
`176b0096…82ca`, package `main.nut` `6704aa6e…952d` == shipped package ==
isolated `game/RoadFreightProof/main.nut`, and `info.nut`
`03e5af7b…f7b`); the launch argv was recorded and never executed.
Read-only re-proofs: standalone `preflight` → `PREFLIGHT PASS`; `verify`
→ `AUTHORIZATION_UNVERIFIED` / `CLAIM_ABSENT`, exit 1
(authorized-never-consumed). `AUTHORIZATION.json` does not exist and no
claim was consumed: staging wrote no authorization. Nothing was signed,
launched, connected or attempted; candidate-1 (consumed `D5-FREIGHT-1`)
and the stale-by-source-drift candidate-2 byte-untouched; the root
`--version` file untouched; no commit or push. The E53 fix round itself was
committed by the operator as `a7d06fc` (2026-11-02 07:00 +0700) before this
staging step; the E54 identity edit and today's records are uncommitted on
top of it. Remaining operator gates:
independent read-only review, Gate C signing and a separate explicit
launch approval. Evidence index E54.

### 2026-11-02 — D5 Freight Delivery v2 Gate C Option-1 signing (E55)

Explicit operator authorization in-session covered the Gate C signing gate
only ("Gate C agree Operator Signing for Candidate-3"), after the same
session's read-only evidence verification of the E54 staged bytes (six
checks OK; not a code review). Documented Option-1 checklist
([key provisioning doc §1/§2/§4](docs/handoff/2026-10-17/operator-key-provisioning.md),
A1 §12.5/E39/E43 pipeline). One earlier invocation was interrupted by a
transport failure mid-flight; read-only state check confirmed it died
before any write (`AUTHORIZATION.json`, `CLAIM.json`,
`LAUNCH-CONSUMED.json` all absent, no signature existed) and the complete
checklist then executed exactly once from the refusal gates — no signature
was ever produced twice. Refusal gates first; canonical authorization
payload sha256
`9cad63e481af565d67207424bc24c1e372b8e120a286b0a05c88327a897fa62b`; seed
handled only as the exit-status/shape-checked pipeline variable (never
printed, written or argument-passed); derived key equal to the pinned
production anchor `5063982b…4880f` before signing; a single
`sign_authorization_record` run; the 64-byte signature verified under the
pinned anchor over the exact canonical bytes before any write;
`AUTHORIZATION.json` written (record sha256
`3153d3407432be68038f1aaa390a8f3c5ec440834ea0e5983f8cde7b47f1dda5`);
seed unset-verified empty. Read-only post-checks: `verify_authorization` →
PASS binding attempt `D5-FREIGHT-3` / milestone `D5-FREIGHT` to prelaunch
seal `f308d327…18a0e` with `operator_key_identity`
`sha256-ed25519-public-key:cbb63ff5…40c614` (unchanged production anchor);
standalone `preflight` → `PREFLIGHT PASS` exit 0; standalone `verify` →
`AUTHORIZATION_UNVERIFIED`/`CLAIM_ABSENT`, exit 1 (authorized, never
consumed); candidate-2 seal re-verified unchanged `35557a74…76d4`;
candidate-3 `PRELAUNCH.json` bytes untouched; no claim, no launch, no
connection, no gate retried. The signature is binding only and is NOT
launch approval: the final remaining gate is one separate explicit
operator launch approval for exactly one native attempt through the
no-retry lifecycle, then replay + certified cleanup. Evidence index E55.

### 2026-11-02 — D5 Freight Delivery v2 native launch executed exactly once (E56)

Explicit operator authorization in-session covered exactly one native
OpenTTD 15.3 launch (`D5-FREIGHT-3`), no retries, no reconnects. The `run`
subcommand ran once and returned exit 1 with status
`PHASE_HALTED_PREFIX_PRESERVED`: preflight PASS, the one-shot operator claim
consumed exactly once (`CLAIM.json` + `LAUNCH-CONSUMED.json` carry the E55
authorization sha `3153d340…f1dda5` and the pinned key identity), 1 native
launch, 1 connection, 1 request executed of the 32-request budget, and the
first exchange `site-00` (pickup 45748, delivery 50862, depot 45487,
company 0) read back `INVALID_SITE` — cost 0, funds 490,257 unchanged,
`command_accepted` false, `state_changed` false, no vehicle dispatched,
world `HALTED_BEFORE_MUTATION`, decision-log decisive line
`[18] [I] D5_V2_RESPONSE site-00 INVALID_SITE`. Certified cleanup
completed all-true (credential removed, admin listener closed, only an
ephemeral `TIME_WAIT` kernel state left on game port 58339 / admin 44483).
Official read-only replay `verify` →
`PHASE_HALTED_EVIDENCE_PRESERVED` exit 1 with the same halt facts. The
GameScript site gate is an 8-branch refusal chain (pickup stop, delivery
stop, depot identity, the F-12 directed depot-edge probe in both
directions, witness pairs, zero-fleet, delivery acceptance exactly 8/8,
discovery boxes exactly-one); a refused readback carries no observation set
by contract, so the fired branch is not disclosed on the wire. Preflight
passed and the E55 closure pins stayed intact, so this is the A1-anchored
native world disagreeing with at least one site-admission observation the
staged E53 schedule assumed — not staged-source drift; the candidate's
staged bytes and the retained attempt evidence are byte-preserved for
replay. Nothing was retried, re-staged, re-sealed, re-signed or relaunched;
candidate-1 (consumed) and candidate-2 (stale-by-drift, never-consumed)
stayed byte-untouched; the root `--version` file untouched; no commit or
push. Diagnosis or a fix round is NOT started: any deeper census/analysis
is a separate operator-approved step (E53 precedent), and any next
candidate must be staged fresh under a fresh attempt identity
(`D5-FREIGHT-4`), independently reviewed, Gate-C re-signed and separately
launch-approved. Evidence index E56.

### 2026-11-02 — D5 Freight Delivery v2 read-only diagnosis census (E57)

**Operator-approved census gate over the retained E56 bytes.** Scope was
strictly offline and read-only: diagnosis of which of the eight `site-00`
admission branches fired `INVALID_SITE` in the consumed single launch
(`D5-FREIGHT-3`, E56). Nothing was launched, connected, signed, consumed or
retried; no source or candidate bytes changed; no evidence was regenerated;
all retained artifacts (including `session-before.sav`) are byte-untouched;
no commit or push; no general code review, no fix round.

**Verdict — firing branch: the F-12 directed depot-entry probe (branch 4 of
8).** The v2 site admission evaluates branch 4 as
`else if (obs.depot.edge)` → `INVALID_SITE`
(`app/simulation/openttd/d5_freight_v2_package/main.nut:628-631`), where the
observation was built pre-verdict as
`edge = GSRoad.AreRoadTilesConnected(45743, 45487) &&
GSRoad.AreRoadTilesConnected(45487, 45743)` (`main.nut:432-446`).

**Classification: stale assumption at the design layer.** Not a world-state
mismatch — the session world is consistent with every retained receipt — and
not a runtime/implementation defect: the `.nut` faithfully implements the
gate the v2 design demanded, and the demanded bit does not exist and could
not have been created by any operation in this world's history.

Branch census (all facts from retained receipts, plus the vendored OpenTTD
15.3 source for the probe semantics):

| # | Branch | Verdict | Evidence |
|---|--------|---------|----------|
| 1 | pickup stop | PASS (receipt-proven) | `d4-corridor-native-candidate-4/confirm-04-response.json` + candidate-5 `confirm-04-response.json`: stop 45748, truck true, sid 0, stop_owner 0, front 45747, `linked true` — D4 station semantics `GSRoad.GetRoadStationFrontTile(45748) == 45747` (`d4_corridor_package/main.nut:184-190`); state survives A1 (A1 built only the extension side: `full-00` 50096→50864, `road-01` 50095→50096, `spur-02` 50864→50863, `station-03` delivery side; post-A1 `route-00` re-read pickup stop sid 0). |
| 2 | delivery stop | PASS (receipt-proven) | A1 `station-03-response.json`: sid 2, front 50863, `linked true`, stop_owner 0. |
| 3 | depot identity | PASS (receipt-proven) | D4 candidate-5 `depot-06-response.json` (BUILT) + `confirm-06-response.json`: depot true, front_id 45743, depot_linked true, owners 0. |
| 4 | depot edge (F-12) | **FAIL — the firing branch** | see proof below. |
| 5 | witness pairs | PASS (receipt-proven) | v2 `Witness` iterates the 29-tile route (28 pairs, two-directional + owner-0, `main.nut:453-466`); every route pair is one of the A1 `route-00` proven 30/30 connected pairs (`d5_extension_package/main.nut:200` = identical semantics, `first_fail -1`). |
| 6 | zero-fleet | PASS (well-supported) | no BuildVehicle op in any retained dispatch of the lineage; funds 490257 == expected throughout. |
| 7 | acceptance 8/8 | PASS (receipt-proven) | census `d5-accept-survey-native-candidate-2/accept-01-response.json`: `GSTile.GetCargoAcceptance(50862, cargo 1, 1, 1, radius 3) == 8` — the exact probe signature of branch 7, measured on the same post-A1 world. |
| 8 | discovery boxes exactly-one | UNKNOWN (moot) | no receipt ever enumerated stop-radius box membership; `prod-00` measured only the pinned industry's production. Sits after the firing branch in the chain. |

**Why branch 4 is deterministically false on this world** (this is the reason
the census could conclude without a `.sav` parse — per-session save bytes
differ by design, re-serializing the same content):

- OpenTTD 15.3 `AreRoadTilesConnected(t1, t2)` requires the neighbor-facing
  road bit on BOTH tiles (`ottd/src/script/api/script_road.cpp:107-125`);
  for the depot tile, `GetAnyRoadBits` returns only its single exit bit
  toward the front (`ottd/src/road_map.cpp:54-70`,
  `DiagDirToRoadBits(GetRoadDepotDirection(tile))`). Both directions of the
  F-12 pair therefore hinge on the same single fact: a depot-facing (north)
  road stub on road tile 45743.
- Extensive sweep of every retained build receipt in the whole lineage
  (all `artifacts/experiments/*`, statuses BUILT/CLEARED/PLANTED): tile
  45487 appears **only** in `depot-06-response.json` (the depot build
  itself: tile 45487, front 45743). No road op ever laid an edge into the
  depot tile. The D4 schedule laid run 45747→45743, run Bs 45999→48047 and
  48303→50095, and the corner join (45743, 45999) — corridor-facing bits
  only; A1 built only the extension side (full-00 50096→50864, road-01
  50095→50096, spur-02 50864→50863).
- `CmdBuildRoadDepot` (`ottd/src/road_cmd.cpp:1137`) touches only its own
  tile (landscape-clear + `MakeRoadDepot`); it lays no stub on the front
  tile, and road cannot be laid into a depot tile after the build. So the
  depot-facing bit at 45743 has never existed and could not have been
  created by the pipeline.

**The stale point in the record**: F-12 (MINOR, D3,
`docs/d5-freight-delivery-v2-design-review-2026-11-01.md`) rests on the
mitigation claim "`BuildRoadFull` builds both straight bits at span
endpoints … which includes 45743"
(`docs/handoff/2026-10-25/d4-corridor-op03-root-cause.md`). Span endpoints
carry corridor-facing bits only — that same doc states perpendicular pairs
do not carry facing bits — so the claim covers the corridor bits at 45743,
not a depot-facing stub. The D4-era `depot_linked` probe was deliberately
identity-only (`d4_corridor_package/main.nut:184-190`), so the depot-edge
fact was never built and never measured until the v2 gate demanded it.

**Stop.** E57 ends at diagnosis: no fix round, no general code review, no
commit. Any correction (e.g. a fix round or a fresh candidate identity
`D5-FREIGHT-4` with its own staging, review, Gate C signing and launch
approval) is a separate operator-approved gate. Evidence index E57.

### 2026-11-02 — F-12 + branch-8 design/evidence resolution (E58)

Offline docs-only record
([details](docs/d5-freight-4-f12-branch8-design-resolution-2026-11-02.md)):
read-only over `artifacts/` and `ottd/`; no source change, no candidate
change, no evidence regeneration, no launch/connection/signing/claim/retry;
prior text intact; `D5-FREIGHT-3` and all historical evidence byte-unchanged.

**Branch 4 (F-12) — closed at design level.** Instrument kept (source
semantics verified again: `script_road.cpp:107-125`, `road_map.cpp:54-70`,
`follow_track.hpp:272-312`); the world fix is prescribed, not implemented:
demolish depot 45487 → build the road pair 45743↔45487 (this lays the missing
N stub on 45743) → rebuild `BuildRoadDepot(45487, front 45743)`. New
feasibility check of record: `CmdBuildRoadDepot` (`ottd/src/road_cmd.cpp:1137`)
itself runs `CMD_LANDSCAPE_CLEAR` on the target in the non-rotate path, so the
rebuild is legal over the pair's S bit; road pieces into a standing depot stay
refuted (`road_cmd.cpp:516-518`) and script span APIs require `start != end`,
so the demolish is unavoidable. The fix is mandatory: the plan model ends each
cycle `in_depot`, so an un-fixed world fails at depot return even with a
relaxed gate — branches stay strict. After the fix, `D5-FREIGHT-4`'s
prerequisite chain re-binds to the post-fix after-save.

**Branch 8 (discovery boxes exactly-one) — unresolved from retained
evidence; census prescribed.** The gate needs distinct cargo-role member
counts of the two radius-3 boxes; the only industry inventories on disk are
attempt19-world: a complete 6-industry page (ids 0–5, every entry
`tile = x + y·64`, synthetic layout, max tile 3364 < 4096) that cannot
describe the pinned 256×256 seed-17 D5 world (§2.1 of the preparation doc;
D5 live tiles exceed 4096); `network-facts` coverage and
`world-planning-observation` lifetimes are the same attempt19 world; D2/D3
reads show per-tile `industry: null` only. E49 measured aggregates (8/8 at
50862 r3, 0 at 50351, prod id 0 = 104) that cannot split into member counts.
Prescription: **`D5-BOX-CENSUS-1`** — E49-class read-only census (fresh
identity, own staging/review/Gate C/launch approval) that scans the pickup
box (center 45748 = (180,178), r 3) and the delivery box (center 50862 =
(174,198), r 3) and reports per-industry {id, tile, role fact} lists, never
enforcing exactly-one so every outcome is learnable; box counts 1/1 mean the
v2 gate cannot surprise, ≠1 means the site plan adapts first (the gate never
downgrades).

**Sequencing of record:** `D5-BOX-CENSUS-1` → F-12 world fix (own mutation
candidate + post-fix verification) → fresh `D5-FREIGHT-4` (staging,
independent review, Gate C re-sign, separate launch approval).

**Stop.** E58 ends at the same line as E57: no fix round, no census launch,
no general code review, no commit; every next step is a separate
operator-approved gate. Evidence index E58.

### 2026-11-02 — D5-BOX-CENSUS-1 protocol design (E59)

Offline docs-only design of the E58-prescribed read-only census
([details](docs/d5-box-census-1-protocol-design-2026-11-02.md)): no source
implementation, no candidate staging, no evidence mutation, no signing, no
AdminPort connection, no launch, no Git mutation; prior text intact;
`D5-FREIGHT-3` and all historical evidence byte-unchanged.

**Protocol 9, additive.** New module `corridor_box_census.py`; number
allocation 4/5/6/7/8 taken (E51 precedent: consumed contract families are
never retrofitted — list-shaped rows do not fit `SurveyReadback`'s scalar
subsets). Four ops: the three E49 spot re-measures (`radius` 3, `accept`
50351 = 0, `accept` 50862 = 8, `prod` id 0 = 104 — chain-continuity
controls, halt-on-divergence, never relabeled) and the new `box` op: a
49-tile scan of each stop's radius-3 box in exact `DiscoveryBoxes`
iteration order, one row per distinct industry —
`{id ≤ 65535, tile = min member tile, p, a}` with
`p = GSIndustry.GetLastMonthProduction`, `a = GSIndustry.IsCargoAccepted`
(source-verified: 0 = `CAS_NOT_ACCEPTED`, 1 = `CAS_ACCEPTED`,
2 = `CAS_TEMP_REFUSED`).

**Every outcome observable.** Static cursor grid (0/3/6) per box; drained
pages measured READY-empty (absence is a measurement); a third page still
`more = true` is an explicit overflow finding; roles are derived
Python-side (producer iff `p > 0`, acceptor iff `a == 1`, matching the v2
gate verbatim) so the branch-8 verdict is offline-replayable from rows; no
exactly-one enforcement anywhere in the census.

**Exact schedule (10 planned of 32 budget):** radius-00; acc-00 (50351);
acc-01 (50862); prod-00; pbox-00..02 (45748, cursors 0/3/6); dbox-00..02
(50862, cursors 0/3/6). Spots run before box pages; a spot divergence
halts prefix-preservingly. `max_cost 0`, funds pin 490257, one launch and
connection, zero retries. Measured wire audit: worst box request 217 B;
worst page-3 box response 431 B (page 3/box chosen over page 4's thin
33 B margin; 9 ids/box exceeds the v2 8-role bound).

**Bindings and shapes:** prerequisite = consumed A1 extension candidate-3
after-save `3748e00c…5420bd` (the E47 anchor; every D5 session since A1
reloads identical world state); prelaunch schema
`d5-box-census-prelaunch-v1`, attempt map `{1: D5-BOX-CENSUS-1}`;
GameScript lives in a separate composed package `d5_census_package/` so
the frozen `d5_freight_package` source the E47 composition pinned
(`0337fb36…97ae`) does not drift. Receipt `company-box-census-receipt-v1`;
fail-closed outcome `box-census-phase-outcome-v1` (MEASURED/REFUSED/
MISSING/MALFORMED, first halt ends verification, pending never manufactures
success); replay arms `CENSUS_COMPLETION_VERIFIED` /
`CENSUS_HALTED_EVIDENCE_PRESERVED`.

**Next-gate ladder:** 1/1 boxes → fix round then `D5-FREIGHT-4`; ≠1, empty
box or overflow → site-plan adaptation round first; spot divergence →
halt and lineage investigation. Implementation (wire module, native
pipeline, census package, three test suites, `REPRODUCE.md` commands of
record) is its own operator-approved round — this record creates none of
it.

**Stop.** E59 ends at protocol design: implementation, staging, review,
Gate C signing and launch approval each remain separate operator gates;
no census launch; no commit. Evidence index E59.

### 2026-11-02 — D5-BOX-CENSUS-1 offline implementation (E60)

Implementation of the E59 protocol, strictly offline per its design ([§3.4
updated](docs/d5-box-census-1-protocol-design-2026-11-02.md)): no candidate
staging, no evidence mutation, no signing/claim/AdminPort/launch; nothing
written under `artifacts/`; `D5-FREIGHT-3` and all historical evidence
byte-unchanged; `CONTEXT.md` pin `36648f9c…cc29` intact after the edits.

**Delivered:** protocol-9 wire module `corridor_box_census.py`
(plan/schedule pins, per-op echo subsets, spot controls
`{acc-00: 0, acc-01: 8}` and `prod` 104 halt-on-divergence, box pages on
cursors 0/3/6 with `more == (count > cursor + len(rows))`, drained pages
READY-empty, receipts `company-box-census-receipt-v1`, phase outcome
MEASURED/REFUSED/MISSING/MALFORMED with prefix-preserving halt);
staging pipeline `proof/corridor_box_census_native.py` (pinned consumed A1
prerequisite `3748e00c…5420bd`, hypotheses `RETAINED_CENSUS_REBOUND` re-bound
from the E49 receipt, verify arms `CENSUS_COMPLETION_VERIFIED` /
`PHASE_HALTED_EVIDENCE_PRESERVED`, exit-status discipline); census package
`d5_census_package/` (`census_planned` == the Python schedule, bridge
`NetworkFreightProof extends D5CensusProof`).

**Verification of record:** E59 §9 items 4–6 as three suites —
`tests/test_corridor_box_census.py` (wire, 34 passed) +
`tests/test_corridor_box_census_vm.py` (package-VM handler tests, 8 passed;
imports the wire file's VM stubs and shared fixtures) +
`tests/test_corridor_box_census_native.py` (staging/replay, 35 passed)
(77, exit 0; the native suite stages real candidates from the consumed A1
prerequisite through the production `prepare` function and replays a
synthetic consumed attempt through the production verifier); ruff clean on
all six touched paths; `git diff --check` clean; `uvx ty check` only the
one frozen-mirror `connect` override diagnostic (survey pipeline carries
the identical class).
One real `prepare` probe run against a `/tmp` staging path (offline,
discarded) proved staging end-to-end (`PRELAUNCH PASS`).

**Disclosures:** (a) E59 §3.4's drafted `count >= cursor + len(rows)` page-3
validator contradicted the READY-empty drained-page rule and was not
implemented; the implemented rule is `more == (count > cursor + len(rows))`.
(b) The §3.4 wire audit re-measured exact: request 217 B, handler-emitted
page-3 response 431 B (slack 81), page-4 shadow 478 B (margin 34; E59's
'33 B margin' wording corrected); the audit additionally records the
null-inclusive Python canonical parse-side 471 B — never wire bytes; no
wire byte changed. (c) Runtime defects fixed during validation: verifier
membership lookup `request.tile not in plan.box_centres`, request `rows`
lifted to a tuple, per-box `last_id` seeded `-1` instead of null.

**Stop.** E60 ends at implementation: staging approval, independent review,
Gate C signing and a separate launch approval each remain ungranted
operator gates; the census `run` CLI stays unused; no commit by this round.
Evidence index E60.

### 2026-11-02 — D5-BOX-CENSUS-1 staged (E61)

Operator-authorized offline staging of the E60 implementation of record:
`artifacts/experiments/d5-box-census-native-candidate-1` created in one
first-attempt run of `prepare` (which self-runs preflight): `PRELAUNCH PASS`,
exit 0. Seal of record (PRELAUNCH.json sha256, recomputed == PRELAUNCH.sha256):
`c4497053…e381`. Attempt
`D5-BOX-CENSUS-1`, schema `d5-box-census-prelaunch-v1`; prerequisite the
consumed A1 `D5-CORRIDOR-EXTENSION-3` (after-save `3748e00c…5420bd`,
prerequisite seal `404d42d9…acd8`); world mode
`PREREQUISITE_ATTEMPT_SOURCE_SAVE_LOAD` (seed 17, revision 15.3, start_day
712223); binary sha `276d5b69…1904c`; key identity public_key
`cdc03e4b…0706`; budgets 1 launch / 10 exchanges / 32 requests /
max_cost 0 / funds £490,257; guard `d5-box-census-cross-guard-v1`.

Read-only gates after staging: independent `preflight` → `PREFLIGHT
PASS`; `verify` → `AUTHORIZATION_UNVERIFIED` / `CLAIM_ABSENT`, exit 1
(no AUTHORIZATION.json / CLAIM.json anywhere in the candidate). The E60
`/tmp` probe staging stays discarded; not this record.

**Stop.** Staging approval consumed; independent review, Gate C signing and
a separate launch approval remain ungranted operator gates; the `run`
subcommand was never invoked; no evidence bytes mutated; no commit by this
round. Evidence index E61.

### 2026-11-02 — D5-BOX-CENSUS-1 independent read-only verification (E62)

Read-only verification of the E61 staged candidate
`artifacts/experiments/d5-box-census-native-candidate-1`. Gates re-run:
`preflight` → `PREFLIGHT PASS`; `verify` → `AUTHORIZATION_UNVERIFIED` /
`CLAIM_ABSENT`, exit 1 (correct — still unconsumed).

**13/13 audit axes PASS, READY-FOR-GATE-C:** seal recompute; identity
constants; three-way world/prerequisite binding (staged `source.sav` == A1
after-save `3748e00c…5420bd` == recorded digest, prereq seal `404d42d9…acd8`); binary bytes == staged + frozen pins
(`276d5b69…1904c`); OpenGFX `validate_baseset` in-place re-validation
(archive `43a0c1da–03be`); 4 staged `.nut` byte-equal to sources with
bridge `NetworkFreightProof extends D5CensusProof`; staged `census_planned`
== derived schedule; budgets == `census_budgets()`; cross-guard pinned;
refusal surface clean (23 staged files, no launch artifacts); lineage clean;
key pair derived from the staged credential == record public_key;
3495 frozen entries re-digested, none uncovered.

**Disclosed limitation:** the fresh-context subagent review was unavailable
(provider free-usage limit); this was an in-session independent-machinery
audit — source-derived re-derivation + byte comparisons + credential
key-pair derivation — with no candidate writes; a true fresh-context
review remains available to the operator on request. Two mid-round FAIL
lines were auditor script artifacts, not candidate findings.

**Stop.** No launch/sign/claim; no candidate bytes mutated; no commit by
this round. Evidence index E62.

### 2026-11-02 — D5-BOX-CENSUS-1 Gate C Option-1 signed (E63)

In-session operator authorization covered exactly the Gate C signing gate,
on the E61 staged bytes (seal re-verified) after the E62 read-only
verification. `AUTHORIZATION.json` written exactly once from the clean
refusal gates, per the [key provisioning doc §1/§2/§4]
(docs/handoff/2026-10-17/operator-key-provisioning.md) Option-1 checklist:
refusal gates (twice, rechecked immediately before signing) → checked
seed extraction (captured in-shell, never printed/filed/arg-passed) →
derived public ≡ pinned anchor `5063982b…880f` (identity
`cbb63ff5…40c614`) → exactly one `sign_authorization_record` run →
signature verified under the pinned anchor before any write →
`write_authorization_record` → `verify_authorization` PASS on the written
bytes → seed cleared.

One earlier invocation was interrupted by an auditor script compile error
before any execution (no key read into Python, no signature produced, no
write); clean state confirmed read-only, then the checklist ran exactly
once (interrupted-before-write precedent).

Facts of record: payload sha256 `cd124c9e…4147` (attempt, milestone,
schema, prelaunch seal binding, workspace, binary sha, source_world A1
after-save binding `3748e00c…5420bd`, budget table, plan
`operation_schedule`+`plan_digest`, exact `execution_command`);
`AUTHORIZATION.json` sha256 `b9b9c0f4…49f7`; candidate 24 files;
`CLAIM.json`/`LAUNCH-CONSUMED.json` absent. Post-state: `preflight` →
`PREFLIGHT PASS`; `verify` → `AUTHORIZATION_UNVERIFIED`/`CLAIM_ABSENT`
exit 1 by design (authorized, never consumed); census and A1 record bytes
re-digested unchanged.

**Stop.** Signature binding only and NOT launch approval: the final
remaining gate is one separate explicit operator launch approval for
exactly one native attempt; the `run` subcommand stays unused; nothing
signs again, claims, launches or consumes; no commit by this round.
Evidence index E63.

### 2026-11-02 — D5-BOX-CENSUS-1 native launch consumed (E64)

One in-session operator launch approval (question tool, “Approved — run once,
now”) was consumed for exactly one attempt on the E63-signed candidate
(seal and AUTHORIZATION bytes re-verified post-launch). The run of record
(`... run artifacts/experiments/d5-box-census-native-candidate-1`) exited 1,
terminal on this candidate: halt arm `UNSUPPORTED_NATIVE_FACT` on the first
delivery-side census exchange `dbox-00`, result status
`PHASE_HALTED_PREFIX_PRESERVED`, phase verification `CENSUS_INCOMPLETE`.

Measured facts of record: 7/10 exchanges READY (radius-00, acc-00, acc-01,
prod-00, pbox-00/01/02); spot controls radius 3, (50351, 0) accept, (50862, 8)
accept, prod 104; producer box **45748 measured exactly-1** (`exactly_one:
true`, member id 0 / tile 44983 / p 104 / a 0, pages 1+empty+empty, no
overflow); delivery box **50862 not measured on halt** (dbox-00 ended
`UNSUPPORTED_NATIVE_FACT`, `count: null`, rows [], cost 0, funds constant
£490257 — nothing dispatched); budgets requests 8/32, connections 1,
native_launches 1, preflight PASS, state_changed false, cleanup_complete true
(`cleanup.json`: credential_removed, listener_closed, process_reaped,
remaining_processes [], workspace_disposed); welcome world matches the A1
after-save binding (rev 15.3, seed 17, start_day 712223, dedicated).
Independent official read-only replay: `verify` →
`PHASE_HALTED_EVIDENCE_PRESERVED` exit 1 from retained bytes, no forced
relabel. 32 files retained under the candidate, covered by
`artifact-manifest.sha256`; session saves and per-exchange request/response
JSONs retained.

**Interpretation (E59 §8 matrix):** both-boxes-exactly-1 is NOT met, so the
next action is the **site-plan adaptation/design round first** (stop re-pin /
pre-build acceptance; combine the “any box ≠ 1” adaptation branch with the
refusal/halt row); branch8 verdict of record is
`CENSUS_GATE_UNDECIDED_INCOMPLETE`. This is a producer-box exactly-1
measurement made, never a manufactured verdict — the delivery-side refusal
(`UNSUPPORTED_NATIVE_FACT`) needs the design round to decide what the
census should measure instead before any F-12 fix round / `D5-FREIGHT-4`.

**Stop.** E63 authorization consumed; `CLAIM.json` shows one attempt
(`launches_allowed: 1`, `retries: 0`), terminal for this candidate; further
launch on it is refused by the CLAIM gate (no `run` re-execution attempted);
any census re-attempt requires a fresh staging → review → Gate C cycle on
a new candidate + seal and a fresh operator launch approval. No commit by
this round. Evidence index E64.

### 2026-11-02 — D5-BOX-CENSUS-2 adaptation round implemented + staged (E65/E66)

E65: root cause of the E64 terminal halt pinned at source — the 15.3
`GetLastMonthProduction` of record returns -1 for any industry that does
not handle the queried cargo as produced, and `IsCargoAccepted` never
throws for valid arguments. Adapted the contract to carry the fact
verbatim: `CensusRow.p ∈ {-1} ∪ [0, 2^31-1]`, `-1` = the native
non-producer fact, never translated; roles untouched (producer iff
`p > 0`, acceptor iff `a == 1`); handler logs
`D5_CENSUS_BOX_NON_PRODUCER`/`D5_CENSUS_THROW`; every other negative
read stays refused; schedule, pins, budget, grid unchanged; plan digest
survives byte-exact; attempt identity → `D5-BOX-CENSUS-2`. Suites
35 + 8 + 35 = 78 passed; ruff clean; `uvx ty` only the one tolerated
frozen-mirror `connect` diagnostic. Design record: §12 addendum in the
census design doc.

E66: candidate-2 staged offline (`prepare`, `PRELAUNCH PASS`), 23 files;
seal `deb121ada1e73376…`; payload digest `1116d140c2c0b423…`
(two independent derivations agree); plan `ee47cc…` byte-exact in the
staged prelaunch; package bytes tree↔candidate identical; preflight
re-run `PREFLIGHT PASS`; `verify` `CLAIM_ABSENT` exit 1 by design.
READY-FOR-GATE-C on the E65-adapted bytes.

**Stop.** Remaining gates: Gate C signing needs one separate explicit
operator approval; then the launch needs one further explicit operator
approval (one attempt, no retry). No commit by this round.

### 2026-11-02 — D5-BOX-CENSUS-2 Gate C Option-1 signed (E67)

In-session operator authorization covered exactly the Gate C signing gate of
candidate-2. `AUTHORIZATION.json` written exactly once from the clean
refusal gates per the key-provisioning doc Option-1 checklist: checked
seed extraction (in-shell, never printed/filed/arg-passed, cleared) →
derived public ≡ pinned anchor `5063982b…880f` (identity
`cbb63ff5…40c614`) → exactly one signing run → signature verified
under the pinned anchor before any write → in-process verify PASS.

Facts of record: payload sha256 `1116d140…86` (attempt `D5-BOX-CENSUS-2`,
seal `deb121ada…` binding, plan `operation_schedule`+`plan_digest`,
A1 source_world `3748e00c…`, budgets, exact `execution_command`);
`AUTHORIZATION.json` sha256 `ea74e1f8…c9`; candidate 24 files;
`CLAIM.json`/`LAUNCH-CONSUMED.json` absent. Post-gate: `preflight`
`PREFLIGHT PASS`; `verify` `CLAIM_ABSENT` exit 1 by design.

**Stop.** Signature binding only and NOT launch approval; the final gate
is one separate explicit operator launch approval for exactly one native
attempt. No commit by this round.

### 2026-11-02 — D5-BOX-CENSUS-2 launch consumed: complete measured census,
cleanup certification refused (E68)

One in-session operator launch approval consumed for exactly one attempt on
the E67-signed candidate-2. ALL 10 exchanges measured READY, funds
£490257 constant, cost £0, state_changed false, phase verification
`CENSUS_COMPLETE`, plan `ee47cc…` byte-pinned.

Measured memberships of record (the question both rounds existed to
answer): pickup box 45748 = exactly-one producer member — industry 0, tile
44983, p 104, a 0 (pages 1+empty+empty, no overflow). Delivery box 50862 =
exactly-one acceptor member — industry 1, tile 51116, **p -1** (the carried
15.3 native non-producer fact, never translated), a 1 (cargo 1 accepted;
pages 1+empty+empty, no overflow). Branch-8 offline recompute:
`CENSUS_GATE_PASSES`, role_counts {producer: 1, acceptor: 1}.

Terminal classification: run exit 1, `FAILED_CLEANUP` with
`prior_status NATIVE_CENSUS_COMPLETE`. The attempt-completion gate refused
on the one post-reap endpoint observation: kernel TCP_CLOSING (state 11)
on the loopback client socket (42838→57125, inode 0) instead of TIME_WAIT
(6); policy `linux-kernel-endpoint-closure-v1` of record allows residual
TIME_WAIT only (ambiguous=FAIL_CLOSED, no sleeps, no retries). The
observation instant landed inside the simultaneous-close transition. The
process reaped cleanly (returncode 0, remaining_processes []), but the
certification gate is not met, so the attempt cannot verify as complete.

Independent replay: `verify` → `ATTEMPT_FAILED_EVIDENCE_PRESERVED` exit 1
from retained bytes, no forced relabel. 58 files retained under
candidate-2 incl. all ten request/response JSONs (first-ever READY dbox
pages), session saves, receipts, frames.

**Interpretation (E59 §8):** the “both boxes role-filtered exactly 1”
facts ARE MET on the measured bytes; the census's own evidence prescribes
no site-plan adaptation. The attempt verdict of record stays
FAILED_CLEANUP (an attempt-ceremony refusal, never a census finding).
Promoting the F-12-fix → `D5-FREIGHT-4` sequencing on these bytes is a
design-review decision on the retained evidence, not an automatic gate
closure; re-running the census needs a fresh staging → review → Gate C
+ separate launch approval (this candidate terminal). No commit by this
round.

### 2026-11-02 — D5-F12-DEPOT depot-connectivity mutation protocol designed + offline-implemented (E69–E71)

E58 §2.1 implemented as a dedicated one-shot native mutation workflow, offline
only: new protocol-10 wire contract
`app/simulation/openttd/corridor_depot_mutation.py`, GameScript package
`app/simulation/openttd/d5_depot_mutation_package/`, native pipeline
`app/simulation/openttd/proof/corridor_depot_mutation_native.py`, and the
design record `docs/d5-f12-depot-mutation-protocol-2026-11-02.md`.

- Six-exchange schedule of record: before-00 observe → demo-00 demolish 45487
  → road-00 build pair 45743↔45487 → depot-00 rebuild 45487 (front 45743) →
  after-00 observe → fleet-00 fleet. Plan/schedule digest
  `8be74b2c651e…ccc18`; attempt `D5-F12-DEPOT-1`, milestone `D5-F12-DEPOT`;
  schemas `d5-f12-depot-prelaunch-v1` / mutation profile / cross guard;
  receipt `company-depot-mutation-receipt-v1`; max_cost 3000; funds chain
  enforced verbatim 490257 → 490357 (−100 refund) → 490157 (+200) → 488957
  (+1200) → 488957 → 488957.
- Gates: before-00 reproduces the E57/E58 diagnosis verbatim (both
  `AreRoadTilesConnected` directions false; any divergence halts
  `STALE_PIN` before any mutation); after-00 demands the same identity with
  both directions true; fleet-00 demands the zero fleet with per-vehicle
  `in_depot` rows on any halt. Hypothesis state `RETAINED_E58_REBOUND`
  re-binding the E58 doc sha `39b44853…d6b8` (absent doc →
  `RETAINED_E58_ABSENT`).
- Offline validation (E70): suites 29 + 8 + 36 = 73 passed exit 0
  (`tests/test_corridor_depot_mutation.py` + `_vm` + `_native`); ruff clean
  on all six touched paths; `uvx ty check` clean; `git diff --check` clean;
  `CONTEXT.md` pin `36648f9c…cc29` intact. Disclosures: the preflight
  plan-pin defect (demo-00's legitimate None front) found by the suite and
  fixed; the synthetic-fixture funds chain corrected to post-depot 488957.
- Preserved: all historical candidates and census results; `E68`'s
  `FAILED_CLEANUP` verdict unchanged; no census or `D5-FREIGHT-3` rerun; no
  `artifacts/` write; no commit or push.

Remaining ungranted operator gates (each separate, in order): staging
approval for a fresh `D5-F12-DEPOT-1` candidate → independent review →
Gate C signing → one explicit launch approval. REPRODUCE.md carries the
commands of record.

### 2026-11-03 — D5-F12-DEPOT-1 consumed (terminal halt) + E72 read-only A1 world evidence review

The three D5-F12-DEPOT gates were granted as separate operator approvals and
consumed in order: staging (`d5-corridor-depot-mutation-native-candidate-1`,
`PRELAUNCH PASS`, seal `9b0e01417a3e5a8ae9584a6d86285c9ee0b7f89517f970b38331102938ae12fe`,
plan schedule `49f5b510…1382` / mutation `8be74b2c…ccc18`), independent
read-only verification (READY-FOR-GATE-C), Gate C Option-1 signing (auth
record `73734487…463`; one prior invocation died before any write and was
re-run once from the refusal gates per the interruption precedent), and one
launch approval consumed exactly once.

- Terminal state (preserved verbatim): first exchange `before-00` measured
  `depot_present False / front_read −1 / owner −1 / depot_linked False`
  against the E58 before-gate; the harness refused fail-closed `STALE_PIN`
  before any dispatch — `exchanges []`, `mutated []`, 1 request,
  `state_changed false`, run exit 1 `PHASE_HALTED_PREFIX_PRESERVED`. Claim
  consumed once. Cleanup: reaped cleanly (returncode 0, no remaining
  processes) but `cleanup_failure: true` on the live-or-ambiguous-endpoint
  socket fact. Costs: 1 launch / 1 connection / 1 request of 32. The
  attempt is terminal and byte-preserved; no retry, no relabel.
- E72 read-only review (no source change, no candidate, no launch, no
  AdminPort, no `artifacts/` write, no Git mutation; [design doc](docs/d5-e72-a1-world-f12-instrument-review-2026-11-03.md)):
  - `44983` producer id 0/`p 104` — CENSUS_VERIFIED (`pbox-00` row +
    `prod-00`, box exactly-one).
  - `51116` acceptor id 1/`p −1`/`a 1` — CENSUS_VERIFIED (`dbox-00`;
    `acc-01` acceptance 8 at 50862 r3).
  - `45743` road tile + directed depot-edge false both ways —
    RECEIPT_VERIFIED (D4 route read 23/23; E56 branch order + E57).
  - `45487` depot EXISTS company-0/front `45743`/identity-linked —
    RECEIPT_VERIFIED (D4 `depot-06` BUILT + `confirm-06` READ; A1 has no
    demolish receipt; A1 `after.sav` re-digests
    `3748e00ce57bcb076466f50cac3776c202b4fd130d6c6071935e9d43e45420bd`).
  - The F-12 before-00 depot-absent measurement is CONTRADICTED — an
    **instrument false negative**: the 15.3 script road probes fail closed
    while the per-script current road type is unset
    (`ottd/src/script/script_storage.hpp:67` initializes `INVALID_ROADTYPE`;
    `ottd/src/script/api/script_road.cpp:44-51`/`:111`/`:497-502`); the
    F-12 package is the only family member whose observe/gate dispatch
    never calls `SetCurrentRoadType` (its two call sites sit AFTER the
    road/depot ops' STALE_PIN pre-checks; D4 `main.nut:660-662` and D5-v2
    `main.nut:1684-1690` set+assert per request before ops).
  - Verdict: no E58 world assumption was incorrect; the defect is
    bridge-layer, script-only.
- Corrected design (F-12b, awaiting its own operator fix-round approval):
  set+assert `GSRoad.ROADTYPE_ROAD` at `DepotHandle` dispatch entry before
  any probe (D4/v2 pattern verbatim), keep the existing in-op sets, NO
  runner/contract change; then stage a fresh `D5-F12-DEPOT-2` through the
  full gate sequence (staging → independent verification → Gate C → one
  launch approval). The consumed `D5-F12-DEPOT-1` remains terminal
  `PHASE_HALTED_PREFIX_PRESERVED`.
- `D5-FREIGHT-4` staging remains blocked until a verified F-12 completion
  with certified cleanup; the E65 census facts and E53 budgets stay
  preserved for it unchanged.
- Preserved: E68 `FAILED_CLEANUP` unchanged; no historical bytes touched;
  no commit or push.

### 2026-11-03 — F-12b fix round implemented offline (E73)

The E72 §6.1 correction implemented exactly as prescribed, offline only (no
staging, no signing, no launch, no AdminPort, no `artifacts/` write, no
commit). `D5-F12-DEPOT-1` and all historical evidence untouched; CONTEXT
pin `36648f9c…cc29` intact.

- Fix (`app/simulation/openttd/d5_depot_mutation_package/main.nut`):
  `DepotHandle` dispatch entry, after the funds readback and before any
  probe — `GSRoad.SetCurrentRoadType(GSRoad.ROADTYPE_ROAD)` + fail-closed
  assert `GSRoad.GetCurrentRoadType() != 0 || !GSRoad.IsRoadTypeAvailable(0)`
  → `UNSUPPORTED_NATIVE_FACT` (already a contract-legal refusal status).
  The D4/v2 per-request pattern verbatim; in-op sets kept as idempotent
  re-assertions. No runner, wire-contract, schedule, gate, budget or
  E58 change.
- Regression wall: the shared VM stub `GSRoad` now models the 15.3
  fail-close faithfully — context initializes `INVALID_ROADTYPE = 63`
  (`road_type.h:28`), depot/edge probes gate on the current road type
  (`script_road.cpp:44-51`/`:111`/`:497-502`), set no-ops unavailable
  types, `IsRoadTile` unguarded like the engine. Offline fidelity probe
  (discarded): unset → `IsRoadDepotTile(45487) false`, after set → `true`
  — the exact consumed-attempt reading. Two focused tests added:
  `test_dispatch_establishes_the_native_road_context_before_probes` and
  `test_dispatch_assert_refuses_when_the_road_type_is_unavailable`.
- Validation exit 0: suites `29 + 10 + 36 = 75 passed`
  (`test_corridor_depot_mutation.py` + `_vm` + `_native`), ruff
  all-passed on the touched python paths + package dir, `uvx ty` clean,
  `git diff --check` clean.
- Tree: `main.nut` + the two test files modified, uncommitted (habitual
  WIP discipline). Zero other behavior changed.
- Remaining: the road-context fact is native-runtime behavior — the next
  native proof is the `D5-F12-DEPOT-2` launch itself (expected before-00
  read pinned at E72 §6.4). Staging approval for the fresh identity
  `D5-F12-DEPOT-2` remains ungranted; `D5-FREIGHT-4` stays blocked until
  verified F-12 completion + certified cleanup.

### 2026-11-03 — D5-F12-DEPOT-2 lifecycle + verified world binding

Operator blanket approval ("agree Stage D5-F12-DEPOT-2 allow and agree all")
consumed as the chain authorization for this one attempt: staging,
read-only verification, Gate C signing, one native launch. Per the standing
convention the chain authorization covers nothing else:
`D5-FREIGHT-4` staging remains its own approval ask.

- Identity bump (E24 precedent): `DEPOT_MUTATION_ATTEMPT`
  `"D5-F12-DEPOT-1"` → `"D5-F12-DEPOT-2"` in
  `app/simulation/openttd/proof/corridor_depot_mutation_native.py` (E72/E73
  lineage recorded in the comment; consumed attempt-1 stays terminal
  `PHASE_HALTED_PREFIX_PRESERVED`); two attempt pins in
  `tests/test_corridor_depot_mutation_native.py` updated and the drift-tamper
  foreign value moved to `"D5-F12-DEPOT-3"` so the refusal test keeps its
  intent. Suites 75 dots exit 0; `uvx ruff`/`uvx ty` clean;
  `git diff --check` clean.
- Staged fresh (one first-attempt run):
  `prepare artifacts/experiments/d5-corridor-depot-mutation-native-candidate-2`
  → `PRELAUNCH PASS` exit 0. Seal
  `16592103df23669ab46210d956d337344722b3dc9c61877ba0417e743fd8544a`;
  plan digest `49f5b510…1382` + plan model `8be74b2c…ccc18` unchanged vs
  candidate-1; 3496-entry frozen closure re-derived 0 mismatch; staged
  `game/RoadFreightProof/main.nut` (workspace `openttd-15.3-y687ctzl`)
  ≡ live fixed package `e00eeecb…5d67`; gate files absent at staging;
  `preflight` PASS exit 0; `verify` refusal
  `AUTHORIZATION_UNVERIFIED`/`CLAIM_ABSENT` exit 1 (pre-auth shape).
- Gate C (E75): Option-1 checklist, single invocation, first-try success —
  payload sha `1957e2dc…3171`, record sha `9628bcb5…450b`, key identity
  `cbb63ff5…40c614` (production anchor unchanged), signature verified under
  the pinned anchor over the exact canonical bytes before write,
  `binds_seal true`; seed env-only, cleared in both python and shell, never
  printed/filed/arg-passed.
- Launch (one approved attempt, env digests re-verified against pins
  pre-launch): run **exit 0** `NATIVE_DEPOT_MUTATION_COMPLETE`, `verified
  true` — 1 launch, 1 connection, 6/6 exchanges READY:
  `before-00` measured exactly the E72 §6.4 pinned expected read
  (`depot_present true / front_read 45743 / owner 0 / depot_linked true /
  both directions false`) — the F-12b dispatch-context fix proven natively,
  E72's instrument false negative closed at its native gate;
  `demo-00` £60 → `road-00` £142 (front 45743) → `depot-00` £405
  (front 45743), funds chain 490257→490197→490055→489650→489650→489650
  enforced verbatim; `after-00` both `AreRoadTilesConnected` directions true
  with identical identity facts; `fleet-00` zero fleet;
  `DEPOT_MUTATION_GATE_PASSES` (vacuous `in_depot` clause satisfied),
  `state_changed true`, receipts carry seal `16592103…544a` + plan digest
  `8be74b2c…ccc18`.
- Independent replay `verify` → **`F12_MUTATION_COMPLETION_VERIFIED` exit 0**
  with `before_save_sha256` `34903af7ed6c7c75df91ace8ad0a51eeffaf88432aba61e
  286c1e259a1c802bc`. World binding of record: the depot milestone issues no
  authoritative new save — its binding stays the pinned A1 prerequisite
  after-save `3748e00c…5420bd`, re-digested intact on disk post-run; the
  candidate's own saves are retained `session-before.sav` (`34903af7…2bc`)
  and diagnostic-only `after-diagnostic.sav` (`d18caff4…7d0b`).
- Cleanup certified complete: process reaped (pid 38112, returncode 0),
  credential removed, workspace disposed, sockets closed, reservation
  released, `remaining_processes []`; one client-side socket
  `127.0.0.1:37226 → admin 40873` kernel row `TIME_WAIT (inode 0)` — the
  policy-required state (`cleanup_complete: true`; the E68 `TCP_CLOSING`
  refusal does not recur), preserved verbatim. Post-run `preflight` cannot
  reopen the disposed workspace (`FileNotFoundError` on
  `isolated/openttd-15.3-y687ctzl`) — terminal-expected consume-once shape,
  recorded verbatim; `preflight` is a pre-launch gate of record.
- Artifact manifest audit 28/28 match (attempt-1's 16/16 unchanged).
  Attempt-2 terminal COMPLETE; attempt-1 stays terminal
  `PHASE_HALTED_PREFIX_PRESERVED`; E68 stays `FAILED_CLEANUP`; no commit;
  `CONTEXT.md` pin intact.
- Next: `D5-FREIGHT-4` staging is unblocked by verified F-12 completion +
  certified cleanup; fresh staging → review → Gate C → separate launch
  approval all remain its own future gates per the E58 sequencing.

### 2026-11-03 — D5-FREIGHT-4 staged at the approved boundary (E76)

Separate staging approval only ("Approve staging"): prepare + read-only
gates, stopped before review/sign/launch.

- Identity bump (E54 precedent): `FREIGHT_ATTEMPT_V2` `"D5-FREIGHT-3"` →
  `"D5-FREIGHT-4"` in `app/simulation/openttd/corridor_freight_v2.py`
  (attempt-3 stays terminal with its E56 `site-00` `INVALID_SITE` halt
  verbatim); proof docstring + one test pin updated. Suites 128 passed
  exit 0; `uvx ruff` clean; `uvx ty` = the five tolerated pre-existing
  diagnostics (`bf6cc0b` baseline); `git diff --check` clean.
- `prepare artifacts/experiments/d5-corridor-freight-native-candidate-4`
  → `PRELAUNCH PASS` exit 0. Seal `82effd43…5540`; plan digest
  `ed5bad82…b1ff4` byte-exact; fresh plan-model digest `885d9200…a7ff`
  (identity feeds the model); route/witness unchanged; frozen closure
  3497 entries (v2 GameScript `6704aa6e…952d` == live package); prereq =
  A1 after-save `3748e00c…5420bd` (E75-established binding — the depot
  milestone issued no authoritative save); binary `276d5b69…1904c`; gate
  files absent.
- Read-only: `preflight` PASS exit 0; `verify` →
  `AUTHORIZATION_UNVERIFIED`/`CLAIM_ABSENT` exit 1. STOP — no signing, no
  launch. Independent review → Gate C → separate launch approval remain
  ungranted future gates.

### 2026-11-03 — D5-FREIGHT-4 review PASS / world-lineage BLOCKED before Gate C (E77)

The operator six-step workflow consumed steps 1–2 read-only, then stopped
per its own STOP rule. No signature, no launch, nothing consumed.

- Step 1 (independent review, no general code review) — PASS: frozen
  closure 3497/0/0; composed GameScript
  `isolated/openttd-15.3-gvspt11o/game/RoadFreightProof/main.nut` ≡ live
  package `6704aa6e…952d`; seal ≡ `PRELAUNCH.sha256`; plan `ed5bad82…b1ff4`
  / model `885d9200…a7ff` / route `b2f80f46…7131` / witness
  `f1f00e13…686c` / budgets as staged; gate files absent; historical bytes
  untouched.
- Step 2 (world-lineage verification) — NEGATIVE on measured evidence:
  the freight runtime world is the A1 after-save `3748e00c…5420bd`
  (`PREREQUISITE_ATTEMPT_SOURCE_SAVE_LOAD`), and the F-12-DEPOT-2 run
  measured that same world's `before-00` gate: `connected_depot_to_front
  false / connected_front_to_depot false` before mutating its own disposed
  copy. No authoritative post-fix save exists (depot pipeline emits none by
  design; `after-diagnostic.sav d18caff4…7d0b` has zero on-disk consumers)
  and the freight contract/package/runner carry no mutation ops.
  `site-00` demands `depot_edge is True` (`corridor_freight_v2.py:1276`
  -1278) and would read false: a foreknown single-exchange refusal
  (E56 `INVALID_SITE` shape) that would consume the one launch budget.
- Classification: design-level lineage gap between the E58 sequencing
  ("census → F-12 fix candidate (post-fix after-save) → fresh
  `D5-FREIGHT-4`") and the implemented depot-mutation pipeline
  (consume-once isolation, no authoritative save emission). Not a runtime
  defect, not a world mismatch, nothing relabeled.
- STOP honored at step 2: no Gate C signing, no launch. Candidate-4 stays
  staged-only (gate files absent). Future unblocking paths (NOT executed):
  (a) a depot-mutation variant that emits + retains an authoritative
  post-fix after-save for the freight lineage, (b) a freight schedule
  carrying the prescribed mutation itself, (c) an evidence-driven change
  to branch-4 strictness — each needs its own design record + full gate
  sequence.
- Verdict of the workflow: **BLOCKED** (at step 2, before any approval
  gate was requested); consumed candidates 1/2/3 and attempt-1/.-2
  terminals stay verbatim; `CONTEXT.md` pin intact.

### 2026-11-03 — Path A design record (E78, design only)

Wrote `docs/d5-authoritative-post-mutation-save-pipeline-2026-11-03.md`:
the authoritative post-mutation save pipeline closing the E77 lineage gap.
No source change, nothing staged/signed/launched/consumed.

- R2 `D5-F12-DEPOT-3`: strict post-gate save emission on the
  `DEPOT_MUTATION_COMPLETE` branch; `after_save_sha256` bound into
  receipt/result/binding; terminal `PHASE_COMPLETE_SAVE_REFUSED` arm.
- R3 `D5-F12-DEPOT-RELOAD-1`: observe-only 1-exchange recheck over a fresh
  copy of the R2 after.sav; facts of record (edge TRUE both directions,
  front 45743, owner 0, funds 489650, fleet 0) via
  `DEPOT_RELOAD_FACTS_VERIFIED`.
- R4 `D5-FREIGHT-5`: additive freight v3 world-pin (`WORLD_PIN_VERSION = 3`,
  schema `d5-freight2-prelaunch-v2`); freight family requires the
  consumed-extension receipts AND the R2+R3 chain; source world is a fresh
  copy of R2/after.sav. Branch-4 strictness preserved — `site-00` keeps
  `depot_edge is True`, satisfiable in runtime now.
- Every round: offline implementation first, then its own gate sequence,
  every gate asked explicitly. STOP for operator review before R2.

### 2026-11-03 — Path A R2 offline implementation (approved; no staging/signing/launch)

Implemented and verified offline per docs/
d5-authoritative-post-mutation-save-pipeline-2026-11-03.md Round 2:

- `DEPOT_MUTATION_ATTEMPT` bump to `D5-F12-DEPOT-3` (consumed -1/-2
  histories recorded; identities never reused); prelaunch schema
  `d5-f12-depot-prelaunch-v2`; new Path A constants
  (`DEPOT_AFTER_SAVE_NAME`/`BINDING_NAME`/`BINDING_SCHEMA`/`SAVED_AT`).
- `depot_prerequisite_binding()` refuses staging / preflight on a
  prerequisite whose pinned after-save is not a retained regular file with
  its recorded digest (retention check; read-only).
- `execute_depot_mutation_attempt()`: on the verified
  `DEPOT_MUTATION_COMPLETE` branch the strict (never diagnostic)
  `save(backend, prepared, "after")` writes the authoritative
  `directory/after.sav`; digest + size bind into `result.json` and
  `receipt.json`; save failure on the complete path is terminal
  `PHASE_COMPLETE_SAVE_REFUSED` (save_error bound verbatim; never a
  diagnostic fallback, never a claim).
- `verify_depot_mutation_attempt()`: a completion without its hard
  result/receipt/retained-after.sav digest+size triple refuses; the
  verified replay derives (or byte-exactly re-derives)
  `after-save-binding.json`
  (`d5-f12-depot-after-save-binding-v1`: attempt, milestone, directory,
  prelaunch seal, digest, size, saved_at fleet-00, source_world =
  pinned A1 after-save, funds_at_close from the measured funds chain,
  after-00 edge facts, zero fleet); a manifest may carry the binding
  (re-rendered) or stand without it; any other unmanifested file refuses.
  A `PHASE_COMPLETE_SAVE_REFUSED` result is a terminal verdict arm with
  its own contradiction checks; it never writes a binding.
- `tests/test_corridor_depot_mutation_native.py`: pins bumped; consumed
  fixture fabrication decomposed (`_fabricate_consumed_depot_frames`,
  `_fabricate_consumed_depot_records`); the authoritative save triple and
  binding idempotency, refusal terminal/contradiction arms, and
  digest/size/save drift all replay-tested against the production paths.
- Verification: 41/41 native suite + companion wire-contract/VM suites
  green; `ruff check` clean on touched paths; `uvx ty check` clean;
  `git diff --check` clean. No OpenTTD launch, no claim, no staging of a
  candidate, no signature, nothing consumed; `D5-F12-DEPOT-1`/`-2` and
  `D5-FREIGHT-4` stay byte-verbatim; `CONTEXT.md` pin
  `36648f9c2fee4106` intact.

STOPPED at the natural gate sequence: staging approval → read-only review
→ Gate C (one signing) → one launch approval must each be asked explicitly
before the staged `D5-F12-DEPOT-3` candidate exists or runs.

### 2026-11-03 — D5-F12-DEPOT-3 staged + review PASS (E79/E80)

- Staging approval consumed as its own gate: one `prepare` → `PRELAUNCH
  PASS`; seal `4df12e1fbc15e164…`; schema v2; A1 prereq after-save
  retention check passing; frozen 3496/0; composed GameScript ≡ live
  `e00eeecb…`; gate files + binding absent; re-run `PREFLIGHT PASS`;
  `verify` → CLAIM_ABSENT exit 1 pre-auth (E79).
- Independent in-session review (read-only, no candidate writes): 35-axis
  audit PASS — READY-FOR-GATE-C (E80). Full digests on disk at the
  candidate's own PRELAUNCH.json; nothing signed, nothing launched.
- NEXT: Gate C (one signing approval) → one separate launch approval.

### 2026-11-03 — D5-F12-DEPOT-3 Gate C signed (E81)

Option-1 checklist executed exactly once under the explicit operator
signing approval: refusal gates clean + re-checked; payload digest
`14f6dc92…90822` over the canonical bytes; seed env-only (never
printed/filed/arg-passed), shape-checked; anchor cross-check
`5063982b…4880f` BEFORE signing; one `sign_authorization_record` call;
signature verified under the pinned anchor BEFORE any write;
`AUTHORIZATION.json` written once — record sha `2d318dbe…accf2`,
operator_key_identity `cbb63ff5…40c614` unchanged; seed cleared
afterwards (empty verified). Post-write: `PREFLIGHT PASS`,
`verify` CLAIM_ABSENT exit 1 pre-consumption; CLAIM/LAUNCH-CONSUMED
absent. Signature is NOT launch approval — one separate explicit
operator launch approval remains.

### 2026-11-03 — D5-F12-DEPOT-3 launched once: COMPLETE + authoritative after.sav (E82)

One operator launch approval (separate from Gate C); one run, terminal:

- Pre-launch digest gates: binary `276d5b69…1904c`, OpenGFX
  `43a0c1da…03be`, process exclusivity, CLAIM absent, after.sav absent.
- Run exit 0 `NATIVE_DEPOT_MUTATION_COMPLETE` verified=true; 6 exchanges;
  before-00 = E58 diagnosis verbatim; after-00 both directions TRUE;
  fleet 0; funds `490257→490197→490055→489650→489650→489650`;
  `DEPOT_MUTATION_GATE_PASSES`; halt null.
- Path A strict save emitted: after.sav 61992 bytes, digest
  `183b20273a54ebe1a2cd9306145a9ea820bbd6114b1608c42079b4e1b1efe6a6`
  triple-bound (result == receipt == retained file);
  `PHASE_COMPLETE_SAVE_REFUSED` did not occur.
- Replay `verify` → `F12_MUTATION_COMPLETION_VERIFIED` exit 0;
  `after-save-binding.json` derived byte-exactly (schema
  `d5-f12-depot-after-save-binding-v1`, source_world = A1 pin
  `3748e00c…5420bd`, funds_at_close 489650, edge_facts both-TRUE, fleet 0)
  and idempotent on re-verify; cleanup certified; manifest 29/29 with
  after.sav covered; diagnostic save stands diagnostic-only.
- Candidate is terminal COMPLETE and consumed; the world of record for
  R3/R4 is candidate-3/after.sav. STOPPED before R3 (its own approval).

### 2026-11-03 — R3 `D5-F12-DEPOT-RELOAD-1` observe-only reload implemented offline (E83)

Per the Path A design record `docs/d5-authoritative-post-mutation-save-pipeline-2026-11-03.md`
(R3 at L88–96, L257–264). Implementation round only — no staging, no
signing, no launch, nothing consumed:

- Observe-only GameScript package `app/simulation/openttd/d5_depot_recheck_package/main.nut`
  (additive, 324 lines): marker `D5_F12_DEPOT_RECHECK_READY`, bridge
  `class NetworkFreightProof extends D5DepotRecheckProof` (retained
  save-restore identity name), one planned exchange `reload-00` over the
  depot observe subset (protocol 10): `IsRoadDepotTile` /
  `GetRoadDepotFrontTile` / `GetOwner` / `IsRoadTile` /
  `AreRoadTilesConnected` at depot 45487 / front 45743; zero
  spend, zero tile echo, zero fleet rows, no game command, no save of any
  kind; the E72 dispatch-entry set+assert of the native road context
  carried over verbatim; wire `max_cost` echo stays 3000 (contract
  forced) while the attempt ceiling is 0; the one-shot 32-request budget
  and duplicate drop guard mirrored.
- Pipeline `app/simulation/openttd/proof/corridor_depot_recheck_native.py`
  (additive, 2122 lines): KIND `depot-recheck`, attempt
  `D5-F12-DEPOT-RELOAD-1`, milestone `D5-F12-DEPOT-RELOAD`, prelaunch
  schema `d5-f12-depot-reload-prelaunch-v1`, prerequisite schema
  `d5-native-prerequisite-attempt-v1`, receipt
  `after-reload-receipt.json` / `d5-f12-depot-reload-receipt-v1` (nested
  phase of record), launch-consumed schema `d5-native-launch-consumed`;
  schedules the one pinned observe exchange with zero-mutation markers
  (`mutated`/`state_changed` structurally empty/false), arms
  `DEPOT_RELOAD_OBSERVED`/`DEPOT_RELOAD_INCOMPLETE`, gate
  `DEPOT_RELOAD_GATE_PASSES`/`DIVERGED`/`UNDECIDED_INCOMPLETE`, verify
  arm `DEPOT_RELOAD_FACTS_VERIFIED` (+ preserved/halt/unresolved
  evidence arms), welcome floor `start_day >= 712223`, budgets
  1/1/1/512/512/0s; prerequisite binding = a pinned copy of the consumed
  `D5-F12-DEPOT-3` after-save `183b2027…6a6` (E82) re-verifying the
  round-2 facts of record (both directions TRUE, front 45743, owner 0,
  depot_linked TRUE, funds 489650, fleet 0) through the consumed depot
  attempt's own binding; zero-save discipline enforced post-run
  (`after.sav`/`session-before.sav`/`after-diagnostic.sav`/
  `session-before-identity.json`/`receipt.json` all forbidden in the
  candidate); loaded-source binding three-way (staged record == run
  record == retained depot save). Reuses the depot wire contract
  observe subset and shared frame machinery; no frozen file modified.
- Suites: `tests/test_d5_depot_recheck_package_vm.py` 12 passed (VM,
  imported depot scaffolding), `tests/test_corridor_depot_recheck_native.py`
  28 passed (constants/schedule/request gates, session write policy,
  phase arms, prerequisite binding + fake-dir refusals, staging,
  composition `RoadFreightProof` identity, freeze closure, preflight
  tamper refusals, synthetic consumed replay +
  `AUTHORIZATION_UNVERIFIED`/funds-drift/fact-divergence/receipt-drift/
  zero-save-artifact-refusal/halt-preservation arms); companion depot
  suites re-run green 39 + 41. All offline, exit 0.
- Gates of record: `.venv/bin/ruff` clean on the touched paths;
  `uvx ty check` (`All checks passed!` on the three .py paths; `.nut`
  files out of scope by tooling); `git diff --check` clean; ws-clean —
  `workspace/` clean, `artifacts/` byte-untouched (candidate-3 after.sav
  re-digests `183b2027…6a6` and its binding re-digests `0d7fc617…7b95`),
  `CONTEXT.md` pin `36648f9c2fee4106` intact, root `--version` intact.
- Suite-caught defects fixed in round: a real `NameError` in
  `verify_depot_recheck_attempt` (`outbound` destructured as `_outbound`);
  the dead local `schedule = recheck_schedule()` removed from staging;
  receipt written nested-first (schema/attempt/milestone before phase);
  the verify halted-collection guard now requires the request file
  before claiming the exchange's evidence; `.nut` tile-guard corrected to
  a type-shaped guard (typed observe carries NO tile keys — drop only
  non-null tile/front_tile echoes); depot-session cross-arm corrected
  (protocol-10 observe IS accepted by the depot session — the session
  guard is protocol/op-set level, not label).
- `artifacts/` never written; historical candidates byte-verbatim; no
  commit. NEXT: R3 staging approval for `D5-F12-DEPOT-RELOAD-1`
  (prepare + read-only gates only), then read-only review → Gate C →
  one launch, each an explicit operator ask. Evidence index E83.

### 2026-11-03 — D5-F12-DEPOT-RELOAD-1 staged (E84)

One operator staging approval consumed (PRELAUNCH only; no review, no
Gate C, no launch):

- Refusal gates clean (no prior recheck candidate on disk); ONE
  first-attempt `prepare artifacts/experiments/d5-corridor-depot-recheck-native-candidate-1`
  → `PRELAUNCH PASS` exit 0.
- Seal `0093577a7c84df352190df096245dd5e990e63e0c95d99b8b9630a526522c2e6`
  == `PRELAUNCH.sha256`; attempt `D5-F12-DEPOT-RELOAD-1`, schema
  `d5-f12-depot-reload-prelaunch-v1`, kind `depot-recheck`, milestone
  `D5-F12-DEPOT-RELOAD`.
- Prerequisite = the consumed `D5-F12-DEPOT-3` after-save
  `183b2027…6a6` (staged `world.save_sha256` equal) with the retention
  check passing; binary `276d5b69…1904c` == pin, no other openttd
  process; fresh session key `b02eea77…` (not the anchor); frozen
  closure 3497/0; budgets 1/1/1 / max_cost 0; schedule = `reload-00`.
- Composed GameScript `isolated/openttd-15.3-ncjrhz4i/game/RoadFreightProof/main.nut`
  ≡ live recheck package `5e2ee281…a243` byte-exact, bridge
  `… extends D5DepotRecheckProof`; AUTHORIZATION/CLAIM/LAUNCH-CONSUMED
  absent.
- Read-only gates: re-run `preflight` → `PREFLIGHT PASS` exit 0;
  `verify` → `AUTHORIZATION_UNVERIFIED`/`CLAIM_ABSENT` exit 1 (pre-auth
  by design).

NEXT GATES (each its own explicit operator approval): independent
read-only review → Gate C signing → one launch. STOPPED before review.

### 2026-11-03 — D5-F12-DEPOT-RELOAD-1 review PASS (E85)

One operator review approval consumed (read-only; no signing, no launch):

- 38-check in-session audit: ALL PASS. Seal `0093577a…c2e6` ≡
  `PRELAUNCH.sha256`; identity exact; binary `276d5b69…1904c` == pin.
- The module's own prerequisite re-derivation exact
  (`staged_prerequisite == _recheck_prerequisite_record(binding())`):
  pinned copy of the consumed `D5-F12-DEPOT-3` after-save
  `183b2027…6a6`, retention check regular-file digest PASS, depot
  binding `source_world` = A1 pin `3748e00c…5420bd`, round-2 facts of
  record both-TRUE, funds 489650, fleet 0; staged `source.sav`
  digest-verified; welcome floor 712223.
- Plan policy: single `reload-00` observe exchange; plan digest
  re-derives; plan model `8be74b2c…`; budgets 1/1/1/max_cost 0; profile
  `permitted_ops ["observe"]` / `mutating_ops []`; wire echo 3000;
  zero-save `save_policy`.
- Composition: `isolated/openttd-15.3-ncjrhz4i/game/RoadFreightProof/main.nut`
  ≡ live package `5e2ee281…a243`; OpenGFX `43a0c1da…03be` == pin;
  frozen closure 3497/0; fresh session key `b02eea77…` (not the anchor).
- Refusal gates: AUTHORIZATION/CLAIM/LAUNCH-CONSUMED and every
  zero-save artifact name absent; candidate files exactly 3; re-run
  `preflight` → `PREFLIGHT PASS` exit 0; `verify` →
  `AUTHORIZATION_UNVERIFIED`/`CLAIM_ABSENT` exit 1.
- Historical bytes untouched: depot manifests 29/29 + 28/28 + 16/16,
  census manifests 36/36 + 31/31, D5-FREIGHT-4 seal `82effd43…5540`
  byte-exact; `CONTEXT.md` pin intact; `git diff --check` clean.
- Disclosures: two first-script audit bugs (wrong key path
  `provenance["source_world"]`; a `json.load`/`read_text` slip) re-ran
  PASS — no staging defect; in-session machinery per E62/E80 precedent.

READY-FOR-GATE-C. NEXT: Gate C signing (one explicit operator approval,
Option-1 checklist, verify under the pinned anchor before write, seed
env-only) → one separate launch approval. STOPPED before Gate C.

### 2026-11-03 — D5-F12-DEPOT-RELOAD-1 Gate C signed (E86)

One operator Gate C approval consumed (Option-1 checklist; one write,
signature only — NOT launch approval):

- Refusal gates re-checked: seal `0093577a…c2e6` re-verified,
  AUTHORIZATION/CLAIM/LAUNCH-CONSUMED absent.
- Seed env-only (PEM → 32-byte RFC 8032 hex into `SEED_HEX`; never
  printed/filed/arg-passed; pipefail + shape `^[0-9a-f]{64}$` checks);
  seed-derived public key == pinned anchor `5063982b…4880f` BEFORE
  signing.
- Signed once over the canonical payload bytes (payload digest
  `002f336dcc786324ffee03db4d59415dfe647f68184b48835a8877fc3c3c6856`
  — full binding set incl. `operation_schedule` `reload-00`,
  `plan_digest`, budgets, the pinned `183b2027…6a6` source world and
  the exact `execution_command`).
- Signature verified under the pinned anchor BEFORE any write;
  `AUTHORIZATION.json` written exactly once — record sha
  `e2b5ebb04e4afeb362c0207af6f395f9fbbf6cc4596ea89a683e971d4f914864`;
  `verify_authorization` PASS binding `D5-F12-DEPOT-RELOAD-1` to seal;
  `operator_key_identity` `sha256-ed25519-public-key:cbb63ff5…40c614`
  (unchanged production anchor); seed cleared (unset, empty verified).
- Post-write read-only gates: `preflight` → `PREFLIGHT PASS`;
  `verify` → `AUTHORIZATION_UNVERIFIED`/`CLAIM_ABSENT` exit 1
  (authorized, never consumed); CLAIM/LAUNCH-CONSUMED absent;
  candidate files 5.

FINAL REMAINING GATE: one separate explicit operator launch approval
(both outcomes terminal, no retry), then post-run read-only replay
gates. STOPPED before launch.

### 2026-11-03 — D5-F12-DEPOT-RELOAD-1 launched once: COMPLETE + FACTS VERIFIED (E87)

One operator launch approval consumed; one run, terminal:

- Pre-launch env-of-record: binary re-digest `276d5b69…1904c` == pin,
  OpenGFX `43a0c1da…03be` == pin, no other openttd process.
- Run exit 0 `NATIVE_DEPOT_RELOAD_COMPLETE` verified=true; 1 launch /
  1 connection / 1 request; `reload-00` READY measuring the round-2
  facts of record verbatim (both directions TRUE, front 45743, owner 0,
  depot_linked true, depot_present true); funds 489650 constant; cost 0;
  `mutated []`; `state_changed false`; `halt null`;
  `DEPOT_RELOAD_GATE_PASSES`; `loaded_source_sha256 183b2027…6a6`
  three-way (staged == run == retained depot after-save).
- Zero save of any kind emitted; the world of record stays
  candidate-3/after.sav.
- Replay `verify` → `DEPOT_RELOAD_FACTS_VERIFIED` exit 0;
  `after-reload-receipt.json` (`d5-f12-depot-reload-receipt-v1`) bound
  to the seal and the loaded source, funds 489650, fleet 0, phase
  `DEPOT_RELOAD_OBSERVED`; claim consumed once; cleanup certified
  (pid 75588 reaped rc 0, TIME_WAIT + closed sockets, workspace
  disposed, credential removed); manifest 15/15 exactly balanced; A1
  prerequisite after-save re-digested byte-exact; `CONTEXT.md` pin
  intact.

Candidate terminal COMPLETE; never re-launch. R3 outcome: the round-2
world survives its own re-measure. NEXT: R4 (freight v3 world-pin
version `WORLD_PIN_VERSION 3`, identity `D5-FREIGHT-5`, R2+R3 receipts
required in `freight_facts()`, source world = fresh copy of R2
after.sav) — offline implementation is its own round, its own explicit
operator approvals.

### 2026-11-03 — R4 Path A freight v3 offline implemented (E88)

The operator approved R4 for exactly: additive freight v3 world-pin
version `WORLD_PIN_VERSION 3`, schema `d5-freight2-prelaunch-v2`,
identity `D5-FREIGHT-5` (D5-FREIGHT-4 staged-once name never reused),
R2+R3 receipts required in `freight_facts()`, source world = fresh copy
of the consumed D5-F12-DEPOT-3 after-save, site gate
`corridor_freight_v2.py:1277-1278` (`depot_edge is True`) untouched.

Implementation delivered:

- Wire module `corridor_freight_v2.py`: header/docstrings re-pointed to
  the post-mutation world of record (`183b2027…6a6` at £489,650);
  `FREIGHT_ATTEMPT_V2 = "D5-FREIGHT-5"` (the once-staged never-consumed
  D5-FREIGHT-4 stays byte-verbatim stale-by-construction);
  `FUNDS_AT_DEPOT_MUTATION_CLOSE = 489650` beside the kept
  `FUNDS_AT_A1_CLOSE = 490257`; plan validator + site refusals bind the
  depot-mutation close-out funds exactly. Package bytes untouched.
- Native pipeline `proof/corridor_freight_v2_native.py`:
  `WORLD_PIN_VERSION = 3`; schema bump; pins `DEPOT_PREREQUISITE`
  (candidate-3) / `DEPOT_PREREQUISITE_AFTER_SAVE 183b2027…6a6` /
  `RELOAD_PREREQUISITE` (recheck candidate-1); `freight_facts()` now
  runs the full chain — A1 candidate-3 lineage unchanged, depot chain
  (`F12_MUTATION_COMPLETION_VERIFIED`, both-TRUE edge facts, front
  45743, owner 0, funds 489650, fleet 0, saved-at fleet-00), reload
  chain (receipt three-way `loaded_source_sha256` binding +
  `DEPOT_RELOAD_FACTS_VERIFIED`); `prerequisite_binding()` carries
  nested provenance (`a1_extension_lineage` / `depot_mutation_chain` /
  `reload_chain`) with flat `world_pin_version` + `funds_of_record`;
  plan/budgets/policy/staging/preflight/replay guards all re-pointed.
  Plan model digest fresh `1acaa75d4ae2b00e…`; schedule digest policy
  unchanged.
- Suites: `tests/test_corridor_freight_v2.py` 61 passed (stub funds
  489650) and `tests/test_corridor_freight_v2_native.py` 67 passed —
  128 total exit 0. Live offline verification: `freight_facts()` executed
  in-session, both prerequisite replays green, three-way chain binds.
- Gates: ruff clean on the four touched files (one I001 import-order
  repair), ty 5 diagnostics all pre-existing baseline in untouched
  regions, `git diff --check` clean, ws-clean byte-untouched
  (candidate-3 `after.sav` `183b2027…6a6`, binding `0d7fc617f058b12b…`,
  D5-FREIGHT-4 seal `82effd43…5540`, `CONTEXT.md` pin `36648f9c2fee4106`
  intact, root `--version` preserved).

Mid-suite fixes were test-file only (payload `source_world` pin, world
`expected_funds` assert, provenance flat-key KeyError → per-directory
seal compares). No production revert; zero `artifacts/` writes; zero
native runs. NEXT: the R4 staging gate for `D5-FREIGHT-5` (one prepare
run + read-only preflight/verify only) is an explicit operator ask,
then independent review → Gate C → one launch, each its own approval.

### 2026-11-03 — R4 staging: D5-FREIGHT-5 staged (E89)

Operator approved the staging gate as exactly one prepare run plus
read-only preflight/verify. First invocation refused fail-closed before
any write (CLI `--prerequisite` default still A1-pinned; one-line
default fix in the module; ruff + both suites re-run green post-fix).
No bytes written by the refusal — the approved attempt is the first.

- `prepare d5-corridor-freight-native-candidate-5` → `PRELAUNCH PASS`
  exit 0; seal `57e37573f46ffa57…6bf9`; attempt `D5-FREIGHT-5`, schema
  `d5-freight2-prelaunch-v2`; plan digest `ed5bad82…` byte-identical to
  candidate-4's (schedule policy unchanged), plan model fresh
  `1acaa75d4ae2b00e…`; prerequisite = consumed `D5-F12-DEPOT-3`
  (candidate-3, after-save `183b2027…6a6`); provenance
  `world_pin_version 3`; staged `source.sav` == depot pin (fresh COPY);
  gate files absent.
- Read-only: `preflight` → `PREFLIGHT PASS` exit 0; `verify` →
  `AUTHORIZATION_UNVERIFIED`/`CLAIM_ABSENT` exit 1 (pre-auth by design).
- ws-clean: candidate-3 `after.sav` + binding byte-untouched,
  D5-FREIGHT-4 seal historic, `CONTEXT.md` pin intact, root
  `--version` preserved; `git diff --check` clean.

Candidate staged-only, byte-frozen. NEXT: independent read-only review
→ Gate C signing → one launch, each its own explicit operator ask.

### 2026-11-03 — R4 review: D5-FREIGHT-5 READY-FOR-GATE-C (E90)

Operator approved the in-session read-only review (E80/E85 precedent).
26-axis audit re-derived every staged fact from its sources of record:
- Full `freight_facts()` replay run with before/after byte snapshots:
  depot after-save/binding, reload receipt and every prelaunch digest
  identical across the run — replay is read-only, chain verified
  (`F12_MUTATION_COMPLETION_VERIFIED` + `DEPOT_RELOAD_FACTS_VERIFIED` +
  A1 lineage unchanged).
- Staged `prerequisite` + `prerequisite_provenance` byte-equal to the
  live `prerequisite_binding()` re-derivation (`world_pin_version 3`);
  staged `source.sav` == depot pin `183b2027…e6a6` (fresh COPY).
- Plan digest byte-identical to candidate-4's (schedule policy
  unchanged); plan model fresh `1acaa75d4ae2b00e…`; budgets funds
  489650; composed GameScript ≡ live package `6704aa6e…952d`; frozen
  closure 3498 entries, 8 sampled re-hashes exact.
- Re-run gates: `preflight` → `PREFLIGHT PASS`; `verify` →
  `AUTHORIZATION_UNVERIFIED`/`CLAIM_ABSENT` exit 1 (pre-auth by design).
- Disclosures: two audit-script bugs rerun PASS (flat-dict mis-read of
  the frozen block; dict slicing); the old binding-digest shorthand
  `…7b95` corrected — the full file digest is
  `0d7fc617f058b12b…9b95`, head stable across every check.

No writes, no signing, no launch, nothing consumed. NEXT: Gate C
signing (one explicit operator approval, Option-1, seed env-only) →
one separate launch approval.

### 2026-11-03 — R4 Gate C: D5-FREIGHT-5 signed (E91)

Operator Gate C approval consumed in-session, Option-1 checklist,
exactly one authorization-record write, signature only (NOT launch
approval):
- Refusal gates re-checked first: gate files absent; live seal
  re-digested `57e37573f46ffa57…6bf9` == `PRELAUNCH.sha256` == the
  reviewed record.
- Seed env-only via the operator-held PEM, never printed, filed or
  arg-passed; seed-derived public key == pinned anchor
  `5063982b…4880f` BEFORE signing; key identity
  `sha256-ed25519-public-key:cbb63ff5…40c614` unchanged.
- Canonical payload digest `cdd11859…5276` binding attempt
  `D5-FREIGHT-5`, schema `d5-freight2-prelaunch-v2`, the reviewed seal,
  source world `183b2027…6a6`, `operation_schedule` (30 exchanges) and
  `plan_digest` `ed5bad8237dd6898…`.
- 64-byte RFC 8032 signature verified under the pinned anchor BEFORE
  any write; `AUTHORIZATION.json` written exactly once — record sha256
  `83ca881e7cebd3d903889c83b5e9ebb6b09b3ce189fb85d80c8332f6c65c3a68`;
  `verify_authorization` PASS binding D5-FREIGHT-5 to the seal; seed
  cleared (unset, empty verified).
- Disclosures: two earlier gate-script invocations exited 94
  (seed-extractor off-by-one — `range(len(der) - 32)` excludes the
  final 32-byte window of the 48-byte PKCS#8 DER) and died before any
  write; seed never rested on disk across either (captured extraction
  file deleted before the re-run); the fixed standalone extractor
  (`len(der) - 31`, validated by `public_from_seed` == pinned anchor)
  was re-pointed into the gate script and consumed in the single
  successful invocation. No candidate defect; seed not visible in any
  output.
- Post-write read-only gates: `preflight` → `PREFLIGHT PASS` exit 0;
  `verify` → `AUTHORIZATION_UNVERIFIED`/`CLAIM_ABSENT` exit 1
  (authorized, never consumed — pre-launch state shape of
  E67/E81/E86); CLAIM/LAUNCH-CONSUMED/receipt absent; candidate root =
  5 entries (4 staged + AUTHORIZATION.json); staged seal re-digested
  byte-exact.
- ws-clean: depot after.sav `183b2027…6a6`, binding
  `0d7fc617f058b12b…9b95`, D5-FREIGHT-4 seal `82effd43…5540`,
  `CONTEXT.md` pin `36648f9c2fee4106`, root `--version` preserved;
  `git diff --check` clean.

Signature binding only — NOT launch approval. FINAL REMAINING GATE:
one separate explicit operator launch approval (both outcomes
terminal, no retry), then post-run replay verification + cleanup
certification + manifest audit.

### 2026-11-03 — R4 launch: D5-FREIGHT-5 terminal halt at order-00 (E92)

The operator launch approval was consumed for exactly one run. Outcome:
terminal `PHASE_HALTED_PREFIX_PRESERVED`, exit 1, verified=false —
never retried, never relabeled.

- Pre-launch gates PASS: seal == reviewed record; binary
  `276d5b69…904c` == pin == disk; OpenGFX `43a0c1da…03be` == pin;
  process exclusivity; authorization record present (CLAIM absent);
  `verify_authorization` PASS under the pinned anchor `cbb63ff5…40c614`;
  budget 1 launch / 1 connection / 0 retries.
- Run: 1 launch / 1 connection / 5 requests, returncode 0,
  `state_changed true`. Prefix preserved exactly:
  - `site-00` SITE_ADMITTED — accept 8, production 104,
    `pickup_sid 0`, `delivery_sid 2`, **`depot_edge true`**: the site
    gate of record passes natively on the v3 depot-mutation world.
  - `engine-00` ENGINE_ADMITTED (pin 123, quote 4429).
  - `purchase-00` BUILT (cost 4429, funds 489650 → 485221, vehicle 1).
  - `vread-00` READ (NATIVE_STATE_CHANGED).
  - Halt at `order-00`: `status READBACK_MISMATCH`, cost 0,
    `world_state UNCERTAIN_AFTER_FAILED_COMMAND`, 0 cycles completed.
- Replay `verify` → `PHASE_HALTED_EVIDENCE_PRESERVED` exit 1.
- Attempt terminal; claim consumed once (CLAIM.json + LAUNCH-CONSUMED.json
  both bind authorization record `83ca881e…`).
- Certified cleanup: reaped rc 0, graceful, credential removed,
  workspace disposed, socket state `TIME_WAIT (inode 0)` (the policy
  state of record), `remaining_processes []`, `cleanup_error []`,
  `cleanup_complete true`.
- Manifest 25/25 entries exact; diagnostic-only save `fa32868b…`
  digest-bound in result.json — no authoritative new save.

#### Root cause (read-only, source-level): instrument defect, E72 class

The 15.3 script order API is natively TILE-based both directions:

- `AppendOrder(vehicle, tile, flags)` stores
  `MakeGoToStation(GetStationIndex(tile))`
  (`ottd/src/script/api/script_order.cpp:455-500`).
- `GetOrderDestination` returns, for a goto-station order, the
  station's canonical TILE (`st->truck_stops->xy`;
  `script_order.cpp:241, 267-284`) — never a StationID.

The package order readback compares the readback value against the
site-latched StationIDs (latch: `GSStation.GetStationID` →
`pickup_sid 0` / `delivery_sid 2`; comparison `main.nut:937-939`,
order-read `:978-980`; the N1 comment `:897-900` assumed a sid-form
readback). The offline stub shares the conflation
(`tests/support/canonical_protocol_vm.nut:94` — `GetStationID` returns
the tile-as-id; `:112` — `GetOrderDestination` returns
`orders[n].tile`), so both suites stayed green while the native trip is
statically certain: tile-form value (≈45748-class) is never equal to
station id 0/2, and `d != expected_sid` short-circuits first.
AppendOrder itself returned true; the pick stop may well be stored.

The family had NEVER natively measured `order-00`: historical
candidates 1 and 3 halted at `site-00` and candidate-4 never launched —
candidate-5 is the first family member past the site gate and the first
producer of this readback observation. NOT a world defect (the site
facts re-measured verbatim on the loaded v3 world) and NOT a
staging/signing defect.

#### Post-run state

Staged bytes unchanged (seal + sidecar + AUTHORIZATION record re-digested
byte-exact); historical bytes untouched (depot after.sav `183b2027…6a6`,
binding `0d7fc617…9b95`, reload receipt `abf6a79e…151d`, D5-FREIGHT-4
seal `82effd43…5540`); `CONTEXT.md` pin `36648f9c2fee4106` intact;
root `--version` preserved; `git diff --check` clean.

NEXT: fresh design round required for the instrument fix — 15.3
tile-form-faithful order readback (`d == pinned stop tile &&
GSStation.GetStationID(d) == latched sid && f == flags && g == true`,
mirrored in order-read) plus faithful stub modeling, under a fresh
freight identity (`D5-FREIGHT-6`) with its own design record and
explicit operator approvals end-to-end. Nothing slated in-session.

### 2026-11-03 — Fix round: order-readback implemented offline (E93)

Three explicit operator gates consumed — design-record approval
("record as written", sha `538065fd89ea5ea3…03a6`), implementation
approval, and the disclosed scope-correction approval (first battery
run 100 passed / 28 failed — fail-closed on the wire suite's own
embedded `GSOrder` fixture, then corrected under approval). No
staging, no signing, no launch, nothing consumed.

- Design record: `docs/d5-order-readback-tile-form-2026-11-03.md`
  (gate sha `538065fd89ea5ea3…03a6`; §3.4 amended one paragraph
  naming the actual fixture file → `e3897c8d8494b560…7b160`).
- Package (`d5_freight_v2_package/main.nut`): both readback condition
  blocks re-modelled — OrderOp (lines 939-942) and OrderReadOp
  (lines 983-990) compare the readback destination against the
  pinned stop tiles and deepen with
  `GSStation.GetStationID(d) == latched sid` (stricter instrument);
  N1 comments re-state the 15.3 two-way tile model with the E92
  citations.
- `tests/support/canonical_protocol_vm.nut`: `GetOrderDestination`
  membership edit; parse-verified via the embedded 15.3 Squirrel
  `compile` (the standalone validator's prepared engine tree is
  absent in this VM — never a recorded gate here; disclosed).
- Identity: `FREIGHT_ATTEMPT_V2 → "D5-FREIGHT-6"` (attempt-5 spent,
  never re-used); the native suite's pin test literal moved with the
  bump (E74 precedent).
- Wire fixture correction (scope-corrected, operator-approved):
  `tests/test_corridor_freight_v2.py` embedded `GSOrder` now stores
  `{d = appended stop tile, sid = resolved sid, f = flags}`
  (append-call audit unchanged), `IsGotoStationOrder` reads the
  stored sid, and `test_stub_appends_carry_tile_destinations_and_real_flags`
  asserts the stored shape (d == pinned tiles, sid == 0/2).
- Battery: pytest 61 wire + 67 native = **128 passed, exit 0**
  (second run); scoped `ruff check` (REPRODUCE.md touched paths)
  clean; `uvx ty check` = exactly the 5 recorded baseline
  diagnostics (untouched regions); `git diff --check` clean.
- ws-clean: depot after.sav `183b2027…6a6`, binding, reload receipt
  `abf6a79e…151d`, D5-FREIGHT-4 seal `82effd43…5540`, candidate-5
  seal + AUTHORIZATION `83ca881e…` byte-exact (consumed-side evidence
  untouched), `CONTEXT.md` pin `36648f9c2fee4106`, root `--version`.
  Full-tree lint/type health stays UNKNOWN beyond the recorded
  checks (REPRODUCE.md:46 discipline) — the 15 full-tree ruff hits
  sit in files no round edit ever touched.

NEXT GATES (each its own explicit operator approval): staging for
`D5-FREIGHT-6` (prepare + read-only preflight/verify) → independent
read-only review (composed GameScript digest re-derived against the
new package bytes) → Gate C → one launch.

### 2026-11-03 — Fix round: D5-FREIGHT-6 staged (E94)

Operator staging approval, ONE prepare invocation, first-attempt
success (`PRELAUNCH PASS
artifacts/experiments/d5-corridor-freight-native-candidate-6` exit 0).
- Seal `b2ff1b40471810f52586a8051eeb62bd7849fd17691b4d55780058f8afccd639`
  == `PRELAUNCH.sha256`; attempt `D5-FREIGHT-6`, schema
  `d5-freight2-prelaunch-v2`, kind `freight`; provenance
  `world_pin_version 3`.
- Plan digest `ed5bad8237dd6898…` byte-identical (schedule digest
  policy unchanged); plan model fresh `da576ae59527aa53…`.
- Prerequisites = the consumed chain of record; staged `source.sav`
  == depot pin `183b2027…6a6` (fresh COPY verified, single file);
  budgets funds 489650; fresh session key `3600fd62…` (not the
  anchor); gate files absent; root = 4 entries.
- Composed GameScript
  `isolated/openttd-15.3-g1gbthgk/game/RoadFreightProof/main.nut`
  ≡ live fixed package `e8c603d5be1a41d6…` byte-exact — the new
  package digest after the order-readback fix; the retired E76
  constant `6704aa6e…952d` lives only in the historical candidates.
- Read-only gates: `preflight` → `PREFLIGHT PASS` exit 0; `verify` →
  `AUTHORIZATION_UNVERIFIED`/`CLAIM_ABSENT` exit 1 (authorized, never
  consumed).
- ws-clean all pins hold (depot after.sav/binding, reload receipt
  `abf6a79e…151d`, D5-FREIGHT-4 seal `82effd43…5540`, candidate-5
  seal + AUTHORIZATION `83ca881e…` byte-exact — consumed-side
  evidence untouched); `CONTEXT.md` pin `36648f9c2fee4106`; root
  `--version`; `git diff --check` clean.

NEXT: independent read-only review → Gate C signing → one launch,
each its own explicit operator approval.

### 2026-11-03 — Fix round: candidate-6 independent review PASS (E95)

Operator review approval consumed in-session (read-only, per the
E80/E85/E90 precedent). The audit script
`/tmp/opencode/r5_review_c6.py` ran 20 axes → **20 PASS / 0 FAIL,
exit 0 on the FIRST invocation** (no rerun, nothing disclosed).

- Identity: seal `b2ff1b40471810f5…d639` == sidecar; attempt
  `D5-FREIGHT-6` / schema `d5-freight2-prelaunch-v2` / kind
  `freight` == module re-derivations; binary pin `276d5b69…904c`
  == staged == disk; process exclusivity; staged key `3600fd62…`
  ≠ anchor; root exactly the 4-entry staged set; gate files absent.
- Full prerequisite replay read-only; snapshot set before == after
  across all 9 pins byte-identical (depot after.sav `183b2027…6a6`,
  binding `0d7fc617…9b95`, reload receipt `abf6a79e…151d`,
  depot/reload prelaunch `4df12e1f…`/`0093577a…`, A1 after
  `3748e00c…5420bd` + prelaunch `404d42d9…6acd8`, candidate-5 seal
  `57e37573…6bf9` + AUTHORIZATION `83ca881e…3a68`) — nothing
  retained mutated.
- Facts re-derived: wpv3, save == depot pin, funds 489650,
  `F12_MUTATION_COMPLETION_VERIFIED` + `DEPOT_RELOAD_FACTS_VERIFIED`,
  A1 funds-at-close 490257, retained welcome `start_day 712223`;
  prerequisite binding == staged per key incl. provenance; staged
  `source.sav` == pin (fresh COPY); schedule v2 / 30 exchanges /
  planned ids / 6 cycles; plan digest `ed5bad8237dd6898…`
  byte-identical, plan model fresh `da576ae59527aa53…`; budgets
  funds 489650 / max_cost 5000 / gsadmin 1450 / connection 1 /
  retries 0; engine pin 123, target 45748, company 0.
- **The fix verified inside the staged record**: the live package
  carries the approved tile-form conditions verbatim (OrderOp
  `expected_tile` + `GSStation.GetStationID(d) != expected_sid`;
  OrderReadOp `GetStationID(d0)`, `GetStationID(d1)` identity
  deepening), and the composed GameScript ≡ live package byte-exact
  at the NEW digest `e8c603d5be1a41d6…` (retired `6704aa6e…` absent
  from the live record); OpenGFX pin in graphics identity; frozen
  closure 3498 entries / 8 sampled re-hashes exact; candidate-5
  consumed evidence immutable (snapshot tail).
- The review wrote nothing under `artifacts/` (script lived in
  /tmp); ws-clean unchanged.

NEXT: Gate C signing — one explicit operator approval, Option-1
checklist re-derived for candidate-6 (attempt `D5-FREIGHT-6`, seal
`b2ff1b40…d639`, source world `183b2027…6a6`, `operation_schedule`
30 + `plan_digest` `ed5bad82…` in the payload; seed env-only via the
fixed extractor, anchor-verified before any write, unset after) —
then ONE separate launch approval.

### 2026-11-03 — R4c Gate C: D5-FREIGHT-6 signed (E96)

Operator Gate C approval consumed in-session, Option-1 checklist,
exactly one authorization-record write, signature only (NOT launch
approval):

- Gate scripts RE-DERIVED for candidate-6 before any invocation
  (fresh `/tmp/opencode/r5_gate_c.sh` + `/tmp/opencode/r5_sign_gate_c.py`;
  the candidate-5-bound `r4_*` pair never invoked). Constants from
  the reviewed record: attempt `D5-FREIGHT-6`, schema
  `d5-freight2-prelaunch-v2`, seal `b2ff1b40…d639`, source world
  `183b2027…6a6`, `operation_schedule` 30 + `plan_digest`
  `ed5bad82…`.
- Refusal gates re-checked immediately pre-sign: gate files absent;
  live seal re-digested == `PRELAUNCH.sha256` == the E94/E95
  reviewed record.
- Seed env-only via the operator-held PEM through the fixed
  extractor, never printed, filed or arg-passed; seed-derived
  public key == pinned anchor `5063982b…4880f` BEFORE signing; key
  identity `sha256-ed25519-public-key:cbb63ff5…40c614` unchanged.
- Canonical payload digest
  `9b11f2c6af4d2269c1b3e994eec77b1e7dd78850fd566b14d5299a40987d3084`;
  64-byte RFC 8032 signature verified under the pinned anchor
  BEFORE any write; `AUTHORIZATION.json` written exactly once —
  record sha256
  `2701cd8703266d35754446216d75d4fe31ba1d29c3053bef0710df2073d5eef2`;
  `verify_authorization` PASS binding D5-FREIGHT-6 to the seal;
  seed cleared (unset, empty verified).
- Exit 0 FIRST invocation — no refusal, no extractor incident to
  disclose (E91's off-by-one already fixed and surviving).
- Post-write read-only gates: `preflight` → `PREFLIGHT PASS` exit 0;
  `verify` → `AUTHORIZATION_UNVERIFIED`/`CLAIM_ABSENT` exit 1
  (authorized, never consumed); CLAIM/LAUNCH-CONSUMED/receipt
  absent; candidate root = 5 entries (4 staged +
  AUTHORIZATION.json); staged seal re-digested byte-exact.
- ws-clean: depot after.sav `183b2027…6a6`, binding
  `0d7fc617…9b95`, reload receipt `abf6a79e…151d`, candidate-5 seal
  + AUTHORIZATION `83ca881e…` byte-exact, `CONTEXT.md` pin
  `36648f9c2fee4106`, root `--version`; `git diff --check` clean.

Signature binding only — NOT launch approval. FINAL REMAINING GATE:
one separate explicit operator launch approval (both outcomes
terminal, no retry), then post-run replay verification + cleanup
certification + manifest audit.

### 2026-11-03 — R4c launch: D5-FREIGHT-6 terminal halt at transit-00 after the order fix verified natively (E97)

The operator launch approval was consumed for exactly one run. Outcome:
terminal `PHASE_HALTED_PREFIX_PRESERVED`, exit 1, verified=false —
never retried, never relabeled. **The round's fix was measured by the
run itself: the family's FIRST native order-set verification.**

- Pre-launch gates PASS: seal == reviewed record; binary `276d5b69…904c`
  == pin == disk; OpenGFX `43a0c1da…03be` == pin; process exclusivity;
  AUTHORIZATION present (CLAIM absent); `verify_authorization` PASS
  under the pinned anchor `cbb63ff5…40c614`; budget 1 launch / 1
  connection / 0 retries / 0 reconnects.
- Run: 1 launch / 1 connection / **12 requests**, returncode 0,
  `state_changed true`. Preserved prefix, eleven completed exchanges:
  - `site-00` SITE_ADMITTED — accept 8, production 104, sids 0+2,
    `depot_edge true` (the v3 world gate of record passes again).
  - `engine-00` ENGINE_ADMITTED (pin 123, quote 4429); `purchase-00`
    BUILT (cost 4429, funds 489650 → 485221, vehicle 1); `vread-00`
    VAN `IN_DEPOT` speed 0 `in_depot true` (frame evidence,
    `frames.json`).
  - **The fix of record verified natively**: `order-00` ORDERED
    (`dest 45748 stop_tile`, flags 0, goto true), `order-01` ORDERED
    (`dest 50862 stop_tile`, flags 128, goto true), `order-read-00`
    `NATIVE_ORDER_SET_VERIFIED` with the tile-form inventory — the
    E92 `READBACK_MISMATCH` never recurred.
  - `monitor-00` NATIVE_MONITOR_ARMED (baselines 0); `start-00`
    NATIVE_STATE_CHANGED; `vread-01` VAN **`RUNNING` speed 2
    `in_depot false`** — the vehicle departed the depot (45487).
  - `load-00` day 712234 tick 485: `load 0`, `pickup_amount 0` →
    typed `ZERO_DEPARTED` (F-11, `NATIVE_ZERO_DEPARTED` verification),
    watch budget 10 days / 2048 ticks.
  - Halt at `transit-00` day 712244 tick 1158: second full window,
    `WINDOW_EXHAUSTED`, funds 485221 → 485214 (running costs),
    `world_state INCONCLUSIVE_WINDOW`, `zero_seen false`,
    0 completed cycles, `PARTIAL_EXECUTION_EVIDENCE`.
- Replay `verify` → `PHASE_HALTED_EVIDENCE_PRESERVED` exit 1.
- Attempt terminal; claim consumed once (CLAIM.json + LAUNCH-CONSUMED.json
  bind the signed record `2701cd87…eef2` and seal `b2ff1b40…d639`;
  `launches_allowed 1`, `consumed true`, `retries 0`; operator id
  ≡ anchor-derived).
- Certified cleanup: reaped rc 0, graceful, credential removed,
  workspace disposed, kernel socket `TIME_WAIT (inode 0)` (the
  policy state of record), `remaining_processes []`,
  `cleanup_error []`, `cleanup_complete true`.
- Manifest **39/39 entries exact**; diagnostic-only save `2f6ba84a…`
  digest-bound in result.json — no authoritative new save.

#### Diagnosis boundary (read-only)

NOT an instrument defect: the tile-form + station-identity readback
instrument of record verified the order set NATIVELY at both stops
with exact flags and goto-station, and the E92-halt exchange never
re-triggered. NOT a staging/signing defect (plan/policy receipts
consistent under the signed record binding). The halt of record is a
**world-behavior observation**: the started RUNNING vehicle never
took cargo — zero dispatch flow measured into the pickup stop across
two full typed watch windows (≈ 2 × 10 days / 2048 ticks after a
712223 start-day clock). The family's ZERO_DEPARTED/F-11 typed-class
machinery was measured first-hand; departure-to-delivery mechanics in
this loaded-pin v3 world remain unproven — industrial cargo
distribution to the fixed pickup station is the next design round's
investigation subject. Nothing slated in-session.

#### Post-run state

Staged + signed bytes unchanged (seal + sidecar + AUTHORIZATION
re-digested byte-exact); historical zones untouched (depot after.sav
`183b2027…6a6`, binding `0d7fc617…9b95`, reload receipt
`abf6a79e…151d`, candidate-5 zone incl. AUTHORIZATION `83ca881e…`);
`CONTEXT.md` pin `36648f9c2fee4106` intact; root `--version`
preserved; `git diff --check` clean.

NEXT: fresh design round required for the departure/cargo-flow
investigation (its own design record + explicit operator approvals
end-to-end). Nothing slated in-session.

### 2026-11-04 — R5 implementation: D5-CARGOFLOW-1 cargo-dispatch probe implemented offline (E98)

The operator-approved design record
([`docs/d5-cargo-dispatch-probe-2026-11-04.md`](docs/d5-cargo-dispatch-probe-2026-11-04.md),
sha `d7dab83c939b5966…ecdc`, plan digest `d7bf746676d0ee0d…0fb7`) was
implemented strictly offline. Probe scope of record: **read-only observation
only** — zero company commands, no freight relaunch; consumed `D5-FREIGHT-6`
stays terminal; probe verdicts can never re-open a freight attempt. No
staging, no review, no Gate C, no launch, nothing consumed.

- **Wire contract** `app/simulation/openttd/corridor_cargoflow.py`
  (`ce15bbd4c898a3bf…4445ecc`): Protocol 10; identity `D5-CARGOFLOW-1`, kind
  `cargoflow`, milestone `D5-CARGOFLOW`, prelaunch schema
  `d5-cargoflow-prelaunch-v1`, read-only schema `d5-cargoflow-readonly-v1`,
  ready marker `D5_CARGOFLOW_READY`, receipt verification
  `CARGOFLOW_SAMPLE_MEASURED`, phases
  `CARGOFLOW_COMPLETE`/`CARGOFLOW_INCOMPLETE`, result
  `NATIVE_CARGOFLOW_COMPLETE`, replay `CARGOFLOW_COMPLETION_VERIFIED`; 14
  samples `sample-00`…`sample-13`, offsets 0..65 step 5.
  - Window echo class `_CARGOFLOW_WINDOW_ECHO_STATUS` =
    {`WINDOW_EXHAUSTED`, `CLOCK_STALLED`} carrying exactly
    {`anchor`, `tick`, `day`} (`_CARGOFLOW_WINDOW_ECHO_FIELDS`), mirroring
    the freight-v2 inconclusive family; every other refusal carries zero
    observation fields.
  - E65 `-1` fact family extended to `prod_*`/`trans_*` (`ge=-1`); waits,
    planned and counts stay non-negative; stockpiles uint16-capped.
  - Fail-closed phase verifier + offline verdict: three terminal observations
    (`DISPATCH_OBSERVED_LATE` / `DISPATCH_REFUSED_AT_SELECTOR` /
    `DISPATCH_STOCKPILE_STATIC`), `CARGOFLOW_GATE_UNDECIDED_INCOMPLETE` never
    manufactures success; `pending` semantics = census precedent (the halted
    label leaves pending, `EXCHANGES[1:]` after a sample-00 halt).
  - Measured bytes: request-00 210 B canonical (pinned), request-13 211 B,
    window echo 302 B, `CLOCK_STALLED` 298 B, worst-case READY 833 B
    (prod/trans maxed 2147483647, never -1), realistic READY 664 B; ladder
    months `[[1951,4],[1951,5],[1951,6]]`; request budget 32 one-shot.
- **GameScript package** `app/simulation/openttd/d5_cargoflow_package/`
  (`main.nut` `7826b8ff74f5bb85…d5f52b`, `info.nut`
  `ee670075c3cecef4…9e0dd`): read-only sample handler, bridge
  `class NetworkFreightProof extends D5CargoFlowProof` (frozen save-restore
  identity intact), 14 planned rows with exact offsets, bank balance echoed
  per exchange (never changed), one-shot 32-id budget, halt discipline =
  census precedent byte-identically (any on-ladder exchange with terminal
  status ≠ planned READY permanently halts prefix-preservingly);
  compile-verified in the real Squirrel VM. Three suite-caught handler
  defects fixed in round:
  1. `CargoFlowPlannedIndex` matched the offset column against `q.op` — no
     row ever matched (every request `OUT_OF_ORDER`); fixed to `q.offset`.
  2. `CargoFlowGuard` refused its own measured `prod_*`/`trans_*` = -1; the
     E65 `-1` allowance extended to those families.
  3. the `catch` path typing `UNSUPPORTED_NATIVE_FACT` now deletes the
     partial observation prelude — a half-read sample's echo prelude is
     data, never echo language (no census contradiction: the census echo
     class is request echoes `tile`/`cursor`).
- **Native pipeline**
  `app/simulation/openttd/proof/corridor_cargoflow_native.py`
  (`b76dc20cf70b4372…04685`): staging/preflight/session/exchange/execute/
  replay/verify/exit-status/main. Prerequisite =
  `freight_v2_native.prerequisite_binding` imported (never re-derived),
  wrapped as `CargoflowStagingError(FreightV2StagingError)` — the consumed
  depot-mutation attempt of record `D5-F12-DEPOT-3` (dir
  `d5-corridor-depot-mutation-native-candidate-3`, after-save
  `183b2027…6a6`, welcome `start_day 712223`); verification names
  `F12_MUTATION_COMPLETION_VERIFIED` + a probe-scoped statement; budgets
  requests 32 / 512-1400 B / 900 s / funds 489650 / max_cost 0; probe
  hypotheses `RETAINED_CENSUS_REBOUND` re-bound from the retained census
  receipt `d5-box-census-native-candidate-2` exactly-one members (producer
  {`a`:0,`id`:0,`p`:104,`tile`:44983}; acceptor
  {`a`:1,`id`:1,`p`:-1,`tile`:51116}) with `RETAINED_CENSUS_ABSENT` refusal
  and `HYPOTHESIS` kind always.
- **Suites** (all offline, exit 0): probe trio 42 + 8 + 35 = **85 passed**;
  touched-path neighbors re-run green: census trio, freight wire pair, and
  the native neighbor battery — freight_native (55) + freight_v2_native
  (67) + depot_mutation (29) + depot_mutation_vm (10) + depot_mutation_native
  (41) + depot_recheck_native (28) = **230 passed exit 0**.
- **Gates**: scoped `ruff` clean on the 5 touched paths; `uvx ty check` on
  the 5 touched paths = exactly one diagnostic (the frozen-mirror `connect`
  LSP override, byte-identical to the census native-suite baseline);
  `git diff --check` clean; standalone SQVM compile pass of the edited
  package.
- **Disclosures**: `pending` test expectations corrected to the census
  precedent (implementation kept); full-tree lint/type health stays UNKNOWN
  by design; pre-existing E96/E97 lineage edits in the tree untouched — E98
  touched exactly 7 new files (the digests listed above); `artifacts/`
  byte-untouched; `CONTEXT.md` pin `36648f9c2fee4106` intact; root
  `--version` preserved; no commit.

NEXT GATES (each its own explicit operator ask — STOP before each): probe
staging = ONE `prepare` + read-only `preflight`/`verify` for
`D5-CARGOFLOW-1`; then independent read-only review; then Gate C (fresh
re-derived signer for the probe attempt); then ONE launch approval.

Evidence index E98.

### 2026-11-04 — R5b probe consumption: D5-CARGOFLOW-1 staged → reviewed → Gate C-signed → launched once → terminal halt `PHASE_HALTED_PREFIX_PRESERVED` at `sample-07` (E99)

The E98 probe was consumed in one operator round. This round's single
blanket operator approval ("agrees all approval all") was consumed per the
E74 precedent as a **chain authorization**: probe staging → read-only gates
→ independent review → Gate C → ONE launch, executed in that order, with
the first refusal stopping everything. One attempt consumed, no retry, no
relaunch; R4c `D5-FREIGHT-6` stays terminal; probe verdicts can never
re-open a freight attempt.

- **Staging** (ONE `prepare`, first attempt): candidate of record
  `artifacts/experiments/d5-corridor-cargoflow-native-candidate-1` →
  `PRELAUNCH PASS`; prelaunch seal `41ca61c4bdd4e33d…ba60` ≡
  `PRELAUNCH.sha256`; root = 4 staged entries, no gate files; read-only
  `preflight` PASS exit 0; pre-auth `verify` →
  `AUTHORIZATION_UNVERIFIED`/`CLAIM_ABSENT` exit 1.
- **Independent review** (read-only, in-session): `/tmp/opencode/e98_review_c1.py`
  re-derived fresh — 30/30 checks PASS exit 0, READY-FOR-GATE-C (identity,
  root shape, prerequisite duplicate of `D5-F12-DEPOT-3`, welcome floor
  712223, 14-sample ladder, plan digest, policy pins, budgets, hypothesis
  rows == live module output, composed package == live `main.nut`, OpenGFX
  pin, historical zones re-digested intact, `CONTEXT.md` pin);
  production preflight/verify re-derived inside the audit. Disclosed: two
  audit-script incidents, zero staged defects, zero staging rewrites
  (invocation-1 died pre-write on an unimported `CARGOFLOW_EXCHANGE_IDS`;
  invocation-2 alias mismatches re-verified against the real rows —
  `hypotheses-rows` exact-dict omitted the `centre` field; binding keys
  `after_save_sha256`/`source_world`/`funds_at_close`/`fleet_count`/
  `saved_at_fleet_exchange`; recheck receipt carries `funds_of_record`,
  not `depot_facts`).
- **Gate C** (fresh signer `/tmp/opencode/e98_gate_c.sh`, refusal gates
  pre-write): operator seed env-only (`CARGOFLOW_GATE_SEED`), never
  printed/filed/argument-passed, unset + printenv-empty verified after;
  disclosed pre-write refusal — invocation-1 aborted at the seed→anchor
  assertion because E91's recorded `len(der) - 31` window does not fit this
  host's 48-byte PKCS#8 DER (measured seed window = final 32 bytes,
  `len(der) - 32`), no write in the refusing invocation; signed exit 0 —
  canonical payload sha256 `c114e185…d7d53`, record `AUTHORIZATION.json`
  sha256 `523ace64…ad0eb`, operator identity unchanged
  `sha256-ed25519-public-key:cbb63ff5…40c614`; post-write preflight PASS,
  verify still `CLAIM_ABSENT`, seal byte-equal.
- **ONE launch** (binary `276d5b69…904c` + OpenGFX `43a0c1da…03be`
  pre-verified, no other openttd process): terminal halt
  `PHASE_HALTED_PREFIX_PRESERVED` at `sample-07` on the funds-fence refusal
  `cargo-flow funds must equal the close-out level exactly`; preserved
  prefix = 7 completed MEASURED exchanges `sample-00`…`sample-06`
  (offsets 0–30, days 712228–712258), 8 requests, 1 launch/1 connection,
  returncode 0, `state_changed false`, `verified false`; **run of record =
  appended `/tmp/opencode/probe_run.log` line `run exit=1`** (an
  interactive chained-`$?` echo printed `run exit=0`, not a verdict).
- **Post-run**: replay `verify` → `PHASE_HALTED_EVIDENCE_PRESERVED` exit 1,
  no relabel, prefix untouched; claim consumed once (`CLAIM.json` +
  `LAUNCH-CONSUMED.json` bind record `523ace64…ad0eb` + seal
  `41ca61c4…ba60`, `launches_allowed 1`); cleanup certified (pid 22584
  reaped rc 0, TIME_WAIT inode-0 socket state, `remaining_processes []`,
  `cleanup_complete true`); manifest 31/31 exact; `after-diagnostic.sav`
  diagnostic-only, no consumers.
- **Measured facts of record**: prefix `stock_pickup [-1 ×7]`,
  `stock_bay [0 ×7]`, waits all 0, funds constant 489650 through samples
  00–06 (days 712228–712258, spanning the February rollover),
  `prod_pickup [104,104,104,104,104,104,117]` (rose at the rollover),
  `sampled_months [[1950,1],[1950,2]]`; partial verdict
  `DISPATCH_STOCKPILE_STATIC` ("no measured stockpile nor pickup waiting
  ever rose above its anchor sample: the production-to-stockpile path
  itself stayed closed across the sampled span (H1)").
- **Halt diagnosis boundary** (not a probe defect): `sample-07` measured
  READY, observation intact (stockpiles/waits zero, `prod_pickup 117`,
  cost 0), funds `489458` vs the funds-of-record 489650 — the zero-fleet,
  zero-command observe-only world self-drained 192 in the sampled-gap span
  between the last clean funds reading (day 712258) and the halt reading
  (day 712263; round shorthand `(712259, 712263]`) with zero vehicles,
  zero commands, zero cost. Mechanism not established, not troubleshooted;
  not month-start infrastructure maintenance (funds unchanged across
  Feb 1 = day 712254; still 489650 at day 712258). The funds fence refused
  fail-closed exactly as designed and preserves the halt evidence.
- **Status**: attempt terminal and consumed; `sample-07` left pending with
  suffix samples `sample-08`…`sample-13`; no relaunch, no further candidate
  work beyond `d5-corridor-cargoflow-native-candidate-1`; a dedicated
  observe-only funds-telemetry probe (its own design record + explicit
  operator approvals) is the recorded next-round subject; funds-drain
  hypothesis NOT confirmed this round and never reused as a finding.
  E98's per-gate NEXT-GATES plan was consumed this round as ONE blanket
  chain approval, recorded here as this round's authorization shape.

Evidence index E99.

### 2026-11-07 — Project Phase C offline round: FD-C-1 verified, FD-C-2 built + decided (E142)

Offline only: no OpenTTD launch, no AdminPort connection, no candidate
staging/signing/claim, no native receipt; retained `artifacts/` bytes
untouched (digests re-verified); one commit, no push. Record doc of record:
[docs/phase-c-reconciliation-feasibility-2026-11-07.md](docs/phase-c-reconciliation-feasibility-2026-11-07.md).

- **FD-C-1 (reconciliation record-of-record):** verified, not rebuilt.
  Independent re-derivation from the retained seed-17 census inputs
  reproduced the 2026-10-18/10-25 chain byte-exactly — reconciliation
  `c1cfa970…`, ADR-012 `221ce926…`, ADR-013 `7616f626…`, combined
  rebinding `079fce64…`, ADR-012-only rebinding `c9d11d41…` — with 83
  disagreements → 77 definitional + 6 temporal (43951/47286/47288/48042/
  48309/51378) + 0 contradictions + 0 unresolved, and `p08_binding
  .allowed=true` for planning-classification only (`p08_complete=false`,
  19 UNKNOWN → `TERRAIN_MODIFICATION` in the derived layer; the 19-tile
  diagnosis `66ed07cc…` JSON-value-identical, retained serialization was
  a one-off driver). Focused suites 83 passed.
- **FD-C-2 (Random World feasibility decision):** new engine
  `app/planning/phase_c_feasibility.py` (committed sha256 prefix
  `c585874d9c547ae5…`; policy `phase-c-feasibility/1`): ten required
  dimensions; five outcome classes with deterministic precedence;
  typed single-domain evidence rows with the prohibited
  Candidate-11/D5/fixed-scenario set refused at construction;
  completed-search-only `INFEASIBLE_FOR_OBSERVED_WORLD` rows (verbatim
  tag, direct flag refused); typed P05 prerequisite gate
  (`UNKNOWN_CANDIDATE_COUNT`/`EMPTY_CANDIDATE_SET`/`INVALID_CANDIDATE_SET`
  /`ADMISSIBLE`) mirroring `freight_native_network.py:178`;
  fail-closed unobserved rows carrying real digests; limits regex-pinned
  against their own bytes. 48 focused tests green.
- **Decision of record** `artifacts/experiments/phase-c-feasibility-
  2026-11-07/` (JSON sha256 `67183cf6…31fa4`, MD `edeac983…5dab`):
  outcome `INCOMPLETE_EVIDENCE` — 2 VERIFIED dimensions
  (industry_cargo_compatibility, supported_map_search_limits), 8 PARTIAL,
  19 digest-pinned present inputs, 27 rows, zero observed-world-
  infeasibility rows because every recorded bounded random-world search
  was truncated (`search_truncated true`); P05 gate refusal
  `EMPTY_CANDIDATE_SET` recorded from the seed-2026 terminal.
- **Recommended next action carried by the report:** the capture-pacing
  design decision (ticket-03 family, e.g. pause-the-clock capture) under
  the roadmap fences, then a fresh gated native capture round; no
  feasibility flip without new native evidence.
- **Verification:** suites 83 + 48 = 131 passed; ruff/format clean
  (touched paths); `py_compile` clean; `git diff --check` clean; `ty`
  1 diagnostic on the touched files (deliberate runtime-validated
  refusal; counted, never repaired).

Evidence index E142.

### 2026-11-07 — Phase C continuation: ticket-05 loop engine built offline, M2 capture pacing decided (E143)

Offline only: no OpenTTD launch, no AdminPort connection, no candidate
staging/signing/claim, no native receipt; retained `artifacts/` bytes
untouched; one commit, no push. Working tree sha256 prefixes of the touched
sources: `app/simulation/openttd/proof/freight_delivery.py` `7c3e3155…`,
`app/simulation/openttd/freight_native_network.py` `707d3446…`,
`app/openttd_demo.py` `394db0f4…`, `tests/test_freight_loops.py`
`4d714fb3…`, decision doc `019c605e…` (record doc:
`.scratch/ramrom-product/issues/05-build-loop-product.md`, normalization by
`.scratch/ramrom-product/map.md`).

- **Loop engine (`run_loops`/`loop_gate`):** sealed `loop_cycles` (CLI
  `--cycles`, 1..8, `--random-world`-gated, recorded in PRELAUNCH.json only
  when > 1) run on one launch; one connect per cycle (§3.2), per-cycle
  `loop-cycle-{k}` directories with identity copies, own
  runtime-identity/saves/manifest, per-cycle P07 reports + run `loops.md`
  (§3.6); statuses `NATIVE_LOOP_DELIVERED_VERIFIED` /
  `NATIVE_LOOP_ZERO_SERVICES`; K=2 consecutive zero-service cycles type
  `abandoned_world` (§3.5).
- **Exclude threading:** `execute_network` → `plan_network_world` →
  `network_from_facts` skip already-built `(src,dst,cargo)` identities
  before P08/P05 with `SERVICE_ALREADY_BUILT` rejections; all-excluded sets
  raise the typed zero-service message; `execute_network` returns selected
  services for in-process exclusions.
- **M2 pacing decision:** pause the world clock per supplemental capture
  (`paused_world_clock`, diagnostic `pause_pairs`/`pause_resume_error`);
  document of record
  `docs/random-world-capture-pacing-decision-2026-11-07.md` incl. bounded
  settings and per-attempt evidence fences; first-run pause-stall types
  `PAUSED_CAPTURE_UNRESPONSIVE`.
- **Budgets:** volume budget keys scale `×loop_cycles` at prepare
  (`network_budgets(..., loop_cycles=k)`), recomputed identically by
  preflight and all verify paths; the bridge `drequests` floor follows the
  scaled count; legacy shapes byte-unchanged at `loop_cycles=1`.
- **Verification:** new suite `tests/test_freight_loops.py` 14 passed +
  touched suites (`test_native_freight_network`, `test_freight_network`,
  `test_network_world_preparation`, `test_freight_continuous`,
  `test_openttd_demo` — its prepare-kwargs expectation updated for the new
  `loop_cycles=` keyword — and `test_freight_delivery`): 151 passed.
  ruff/format/`py_compile` clean; `git diff --check` clean; `ty`
  1 diagnostic on the touched files (pre-existing `viewer.log.closed`
  count; counted, never repaired).
- **Native remainder (grant-gated):** one operator grant for the loop
  command of record (ticket file) — first cycle delivers ≥1 verified
  service, second cycle reconnects and verifies; per-cycle replay prints
  `verified_loop_cycles`; pacing fences hold (pause_pairs == captured, no
  pause_resume_error). The 53-legacy-red FULL regression stays the map EXIT
  gate, not run this round.

Evidence index E143.

### 2026-11-07 — Loop verify/record fix round: E143's false verify claims made true, per-cycle recording discipline completed (E144)

Offline only: no OpenTTD launch, no AdminPort connection, no candidate
staging/signing/claim, no native receipt; retained `artifacts/` bytes
untouched; one commit, no push. Working tree sha256 prefixes of the touched
sources: `app/simulation/openttd/proof/freight_delivery.py` `8011b1c2a3c39240`,
`app/simulation/openttd/freight_native_network.py` `35d4edfa92ee77fd`,
`app/simulation/openttd/freight_runtime_planning.py` `7217039218d3e92d`,
`app/simulation/openttd/freight_planning_replay.py` `cd86d3aaece14619`,
`tests/test_freight_loops.py` `be63cacc0c4d6f51`, `app/openttd_demo.py`
`394db0f460358c48` (unchanged this round; record doc:
`.scratch/ramrom-product/issues/05-build-loop-product.md`).

- **Correction of record for E143:** its claims that
  `verify_network_receipt` recomputes scaled budgets (incl. `loop_cycles`)
  and that per-cycle replay works were false at its commit `6dbbcf5`; this
  round makes both true. E143's row is retained verbatim; this row supersedes
  it where they conflict.
- **Per-cycle recording:** every `loop-cycle-{k}` directory now carries its
  own `frames.json` (root-frame slice per the sealed `loop-cycle.json`
  marker), sliced `qualification-prefix-frames.json`, a scoped
  `result.json`/`cycle-result.json` pinned at one connection, and
  cleanup/log copies with final manifests written in `run()`'s `finally` so
  early-exit paths still finalize; fresh `ScenarioPlanningAccounting` +
  `enter("setup")` + GameScript re-subscribe per reconnect.
- **Funding once per attempt:** cycle 1 holds the capital copies
  (`funding_frames=4`), later cycles 0; `replay_qualified_world` skips the
  funding replay exactly on the marker; root funding replays once via
  `verify_capital_frames(root, frames[5:9])` in the new
  `verify_loop_receipt` (the `verify` CLI entry for loop attempts).
- **Foreign-plan provenance:** prior cycles' `DeliveryPlan` digests thread as
  `foreign_plans` through `execute_network` → `service_construction` →
  `command_readback_evidence`; prior-cycle excludes derive from new sealed
  per-cycle `loop-excluded-sources.json` (service triples recorded at run
  time) and cross-check via the P05 replay.
- **Zero-service replay:** new `verify_loop_zero_service_cycle` replays the
  typed error exactly, checks the diagnostic FAILED/error/relationships and
  the cleanup; zero cycles write `cycle-result.json`, delivery cycles
  `result.json` of the exact legacy shape `(1, 1, 29·N, 11·N, …VERIFIED)`.
- **Inherited lint repairs:** UP031 `drequests` percent-format, long
  budget/signature lines (E143-era repo-gate regressions) fixed.
- **Verification:** 9 new offline tests in `tests/test_freight_loops.py`
  (missing/tampered/seal/non-loop/failed recordings, bad replay marker,
  foreign-digest share/skip/refuse contracts); touched suites of record
  160 passed (151 previous + 9 new); ruff/format/`py_compile` clean on all
  touched paths; `git diff --check` clean; `uvx ty check` clean on all six
  touched paths.
- **Offline preflight:** `check(graphical=False)` passes (binary + OpenGFX
  pinned); `--cycles 2` seal budgets — requests 87→174, mutations 33→66,
  supplemental_requests 33345→66690, total_seconds 1200→2400,
  construction_commands 192→384, selected_services 3, launches 1;
  `verify` on a recording-less loop root fails typed rc 1; retained E139
  demo dir read-only intact.
- **Native remainder (grant-gated, unchanged):** ONE fresh per-attempt
  operator grant for the loop command of record (`--cycles 2`) + per-cycle
  `verify` printing `verified_loop_cycles`; FD-C-2 `INCOMPLETE_EVIDENCE`
  (E142) flips only on completed bounded native search evidence. Risks to
  carry into the attempt: native pause behavior on a paused-world console
  unproven; per-cycle `verified_exchanges` byte-counted uniqueness could
  false-trip on identical response bytes across cycles (accepted);
  reconnect establishment never natively exercised; two-cycle pacing
  budget; abandon semantics exercised offline only.

Evidence index E144.

### 2026-11-07 — granted native attempt E145: typed terminal pre-launch (staging seam drift) + same-day offline repair E146

The operator granted exactly one two-cycle attempt of the Phase C loop
command of record. **The attempt failed typed before any OpenTTD launch and
before any AdminPort connection**: `ValueError: STAGING_SEAM_DRIFT:
delivery.nut seam drequests>=87 matched 0 times, expected 1` from
`stage_random`'s `_SEAM_COUNTS` pre-stage audit; exit code 1; retained run
directory `artifacts/demos/playable-demo-7b178d7093d9452a8f4d08806efa1b60`
(`graphics-identity.json` + empty `isolated/`; no workspace, no
runtime-identity, no process). No retry, no relabeling; the grant is
consumed by the attempt of record. Working tree sha256 prefixes of the fix:
`app/demo_random_native.py` `258ba9dbe19c7284`,
`app/simulation/openttd/proof/freight_delivery.py` `2cce3070c125bd41`,
`tests/test_random_capture_budgets.py` `4c27ff878a285ae2`.

- **Root cause (E143-era):** composition stamped the loop-scaled floor
  `drequests>=174` into `delivery.nut` before `stage_random`, whose
  `_SEAM_COUNTS` audit anchors the pre-stage template on the proven
  serial-executor shape (87 once in `delivery.nut`, once in `main.nut`) and
  stamps the final floor itself. No offline test ever composed the full
  package at `loop_cycles=2`, so the drift survived the offline rounds.
- **Fix:** composition restores the legacy per-run pre-stage seam;
  `stage_random(out, budgets, *, seam_requests=None)` stamps the final
  run-level floor (loop attempts pass
  `network_budgets(...)["requests"]` = 174; default keeps byte parity with
  the retained frozen-source copy); the reopen-verify replica recomposes
  with `loop_cycles=m.get("loop_cycles", 1)` (second drift of the same
  family: without it every loop attempt would trip "stale delivery
  package").
- **Offline tests:** 2 new staging tests (the E145 repro + the scaled-seam
  composition of record); adjacent suites of record 256 passed (incl. the
  retained frozen-source `stage_random` byte-parity); ruff/format/
  `py_compile`/`git diff --check` clean; `uvx ty check` clean on the three
  touched paths.
- **Native remainder (grant-gated):** the E145 grant is consumed; a fresh
  explicit operator grant is required before the next attempt of record
  (same command of record; preflight now includes the staging audit).

Evidence index E145 + E146.

### 2026-11-08 — E147: `--cycles 2` staging lifecycle proven offline end-to-end

Offline only; no launch, no AdminPort, no claim, no `artifacts/` mutation;
one commit, no push. The E146 repair is now pinned by end-to-end lifecycle
tests, not unit seams alone. Working tree sha256 prefix of the touched
source: `tests/test_random_capture_budgets.py` `f6a432e2b771231b` (no app
code changed this round).

- **Lifecycle trace verified of record:** (1) initial composition
  `staged_package` keeps the legacy per-profile pre-stage seams (87 for the
  random-forced three-service profile, 58 for the two-service non-random
  profile); (2) `prepare` seals
  `m["budgets"] = network_budgets(..., loop_cycles=k)` into
  `PRELAUNCH.json` under the gates
  (`network + planner + demo + random_world`, no continuous); (3)
  `stage_random` first runs the `_SEAM_COUNTS` audit on the audited
  pre-stage bytes, then stamps the final run-level floor
  (`drequests>=29·3·k`) once per file plus the planner/256-map seams; (4)
  `preflight` recomputes the sealed budgets with the metadata's own
  `loop_cycles`, verifies the frozen sources, and recomposes the workspace
  package with `loop_cycles=m.get("loop_cycles", 1)` (the "stale delivery
  package" check) — the E146 keyword `seam_requests` threads the same
  sealed value; (5) the verify side reads the same composition through the
  frozen-source `staged/` correspondence.
- **New offline tests (4):** `--cycles 2` full
  `prepare`+`preflight` lifecycle with the command-of-record capture
  profile (budgets 174/66/66,690/2400/384 pinned; scaled seam exactly once
  per file in BOTH the workspace package and the frozen-source `staged/`
  bytes; zero 87-residue; no claim);
  `--cycles 1` byte-parity lifecycle (workspace bytes == the retained
  proven `stage_random(base)` output; `preflight` recomputes the same
  budgets object); the `stage_random` call-site contract captured through
  a spy (`seam_requests == network_budgets(...)["requests"]` for k=1,2,8 —
  the composition-side scaling cannot silently diverge from the audited
  stage); boundary/profile pins (two-service legacy seam 58; pre-stage
  audit shape holds for k=2 and k=8 — stamped 174/696 exactly once).
- **Suites of record:** staging suite 13 passed; the full adjacent tuple
  (capture budgets, demo-random-native, native network,
  network-world-preparation, loops, scenario capital, canonical
  persistence/transport, continuous, finance, demo, delivery, network) —
  260 passed; the planning-side tuple (planning execution, planning
  transport, freight planning, P07 proof harness, planning transport live)
  — 120 passed + 1 self-skipped native-gated proof. The documented
  53-legacy-red FULL regression stays the wayfinder EXIT gate (not this
  round's gate).
- **Hygiene:** ruff/format/`py_compile`/`git diff --check` clean;
  `uvx ty check` clean on the touched path.
- **Status:** `OFFLINE FIX VERIFIED` — the complete `--cycles 2`
  composition, sealing, staging audit, preflight recomposition and frozen
  correspondence are deterministic offline. `NATIVE VERIFICATION PENDING`:
  the world, capture pacing, reconnect and loop recordings remain unproven
  natively; the E145 grant is consumed and the next attempt of record
  requires a fresh explicit operator grant.

Evidence index E147.

### 2026-11-08 — E148 execution-mode decision: GUI vs `--headless` for the qualification attempt of record

Docs-only decision round (offline; no launch, no AdminPort, no staging, no
`artifacts/` mutation, no grant consumed; one commit, no push). Decision of
record `docs/gui-headless-execution-mode-decision-2026-11-08.md`, E148 in
`EVIDENCE_INDEX.md`, `REPRODUCE.md` addendum #6, ticket-05 appended section,
map decision line, backlog status-log entry.

- **Decision:** the next native qualification attempt keeps `--headless`
  (`--stop-on-delivery`, `--cycles 2`, seed 2026, towns 3, industries 3).
  Every acceptance bar of record is receipt-based and names no GUI (spec
  §2 lines 78–84; ticket-05 lines 196–207), and the loop line's native
  history is headless (E139/E141/E145). The §1 spectator GUI and the §3.3
  window-close soft end stay product-definition scope for their own later,
  separately granted GUI-bearing probe — owed, never silently dropped or
  satisfied; headless soft end is Ctrl+C only, and E140's window close was
  historically typed FAILED.
- **No code change; no criterion, command or budget changed; digests of
  record unchanged** (`258ba9dbe19c7284`, `2cce3070c125bd41`,
  `f6a432e2b771231b`).
- **Offline checks:** staging suite 13 passed (`tests/
  test_random_capture_budgets.py`); `git diff --check` clean; ruff/py_compile
  not applicable (docs only).
- **Status:** decision recorded; the qualification attempt remains gated on
  a fresh explicit operator grant (E145 grant consumed, not reusable).

Evidence index E148.

### 2026-11-08 — E149 GUI product scope implemented offline: typed `ENDED_BY_OPERATOR` soft end

Offline only; no launch, no AdminPort connection, no staging, no claim, no
`artifacts/` mutation; one commit, no push. The E148 owed element's code half
lands with its deterministic tests; the native GUI probe stays owed.

- **Typed soft end:** `OperatorWindowClosed` + `backend.client_soft` flag +
  `soft_gate()` at the AdminPort exchange boundaries (`query()`, both capital
  exchanges, the planner admission exchange, the `before` save) in
  `app/simulation/openttd/proof/freight_delivery.py` (`4bbff81a0cd5fc52`);
  `run` types `result["status"] = "ENDED_BY_OPERATOR"` with
  `operator_soft_end` and no `error` key — a system failure is never typed
  for an operator close; cleanup/manifest/result.json finalization and every
  verifier's exact-status refusals are unchanged.
- **Viewer classification:** `Viewer.check_client_exit()` in
  `app/openttd_demo.py` (`db2051dea8885642`) — rc 0 = operator soft end
  (flag stamped, typed soft end raised); rc != 0 = the exact E140-shape
  failure; startup `require_alive()` keeps its hard typing; a close during
  the delivered view-hold never retypes a verified run; `run_demo` maps the
  soft end to rc 0 with the honest ended-by-operator print.
- **Tests:** 5 new offline tests in `tests/test_openttd_demo.py`
  (`9c38d38f334d77fc`) under the file's autouse no-native guard; adjacent
  tuple 265 passed / 0 failed; ruff/format/`py_compile`/`git diff --check`
  clean; `uvx ty check` clean on both app files, one pre-existing
  book-recorded diagnostic on the test file (counted, never repaired).
- **Status split:** `IMPLEMENTATION VERIFIED` (offline) /
  `NATIVE GUI VERIFICATION PENDING` — the native GUI-bearing probe (product
  line without `--stop-on-delivery`, with the view hold, real window close,
  ended-by-operator record) stays owed behind a fresh per-attempt grant;
  headless loop of record byte-preserved (command of record, budgets,
  AdminPort boundaries, staging suites still green).

Evidence index E149.

### 2026-11-08 — E150 attempt-1 of the loop qualification executed once under grant and FAILED (typed); root cause fixed offline

The verbatim one-attempt grant was consumed on 2026-11-08: the command of
record ran exactly once, failed, and the stop constraint was honored (no
retry, no relaunch, no seed change; sealed bytes untouched by the
post-mortem). Recorded at E150 (`EVIDENCE_INDEX.md`), REPRODUCE addendum #8,
ticket-05 attempt record, map line, backlog status-log entry.

- **Sealed failure of record:** run dir
  `artifacts/demos/playable-demo-246dc3a4f4fc4b40aee0f73696455473`,
  `status=FAILED` with
  `FileNotFoundError: [Errno 2] No such file or directory:
  '.../loop-cycle-1/graphics-identity.json'`, launches 1 / connections 1 /
  requests 0 / mutations 0, the funded cycle-1 capital retained
  (funding_requests 2, funding_mutations 1),
  `failure_save_error="owned native save completion missing"`, cleanup fully
  reaped at root and cycle level, no `loop-cycle-2`, attempt exit 1.
- **Native pacing datum:** cycle-1 capture ran 832/832 read pairs natively
  inside the qualified M2 month with `pause_pairs=1`, no
  `pause_resume_error` — the E143 pacing fence held natively;
  `compatible_relationships=16`; `search_truncated=true`,
  `captured_relationships=0`.
- **FD-C-2: `INCOMPLETE_EVIDENCE` (unchanged)** — no performing search
  completed; a truncated search never supports a feasibility claim.
- **Root cause + smallest fix:** the cycle flow digests
  `graphics-identity.json` from the cycle dir while the per-cycle copy set
  carried only PRELAUNCH/sha256/CLAIM/frozen-source — the copy set now
  includes a content-identical `graphics-identity.json`
  (`freight_delivery.py` `6f913b555e05ca05`), superseding E143's guaranteed
  per-cycle list; pin test
  `test_loop_cycle_recording_copies_the_graphics_identity_per_cycle` in
  `tests/test_openttd_demo.py` (`2934214451eb1e2d`).
- **Status:** adjacent tuple 266 passed / 0 failed; hygiene clean; the
  command of record stays byte-unchanged and the next attempt waits on a
  fresh explicit operator grant (all earlier grants consumed and void).

Evidence index E150.

### 2026-11-08 — Ticket-05 Phase C follow-up: cycle-chain artifact audit closed + e2e offline tests + attempt-1 pin (E151)

Offline only (branch `miles/fright-delivery` from `81eba19`; no launch, no
AdminPort, no staging, no claim, no `artifacts/` write; app code
unchanged; one commit, no push).

- **Audit verdict:** the full run-time cycle-1 recording and planning
  path was re-audited for additional missing-artifact defects like the
  E150 crash; nothing further is missing. Every plain-constant
  `prepared.directory` read in the chain classifies per occurrence into
  exactly six names: root-stage copies (`PRELAUNCH.json`,
  `graphics-identity.json`), the per-cycle staging self-write
  (`runtime-identity.json`), the chain self-write before read
  (`qualification-prefix-frames.json`), and exchange-disc packets
  (`capacity-add-response.json`, `capacity-read-response.json`). The
  audit itself is pinned by a new AST drift-guard test, so any future
  unclassified chain read fails its own test.
- **Three new offline tests** (`tests/test_freight_loops.py`, 283 lines
  added, 26 passed = 23 prior + 3): (1) the drift guard (staging tuple
  equality, the per-cycle `runtime-identity.json` write pin, the capital
  funding five-file tuple pin); (2) an end-to-end capture test stages an
  `attempt/loop-cycle-1` exactly like `run_loops` does and drives the
  real `capture_planning_facts` offline against the staged recording
  alone (450 tiles / 900 coverage, region == `relationship_region(...)`,
  `content_digest` == sha256 of the staged per-cycle
  `graphics-identity.json`, `generation_seed` 17 read from the per-cycle
  runtime identity, `supplemental-planning-facts.json` retained,
  `require_world` passes, the `planning-n0-*` packets land in the cycle
  dir) — the exact seam attempt 1 died at; (3) a read-only pin test
  re-derives the sealed attempt-1 manifest at root and `loop-cycle-1/`,
  its typed FAILED identity (verbatim error shape, 1/1 launches/-
  connections, 0/0 requests/mutations, funding 2/1,
  `failure_save_error="owned native save completion missing"`, no
  `loop-cycle-2`, 832/832 capture, `pause_pairs` 1, 16 compatible, no
  `pause_resume_error`, qualified M2 month) — a clone without the
  retained bytes fails as missing evidence, never regeneration.
- **Verification:** the 13-file adjacent tuple of record 269 passed /
  0 failed (E150's 266 + 3) plus `tests/test_random_distance.py` 13 in
  the same run (rc 0); ruff/format/`py_compile`/`git diff --check`
  clean; `ty` clean on the test file + both chain modules +
  `freight_delivery.py` (the single pre-existing counted
  `viewer.log.closed` diagnostic stands). Digests of record unchanged
  from E150; FD-C-2 stays `INCOMPLETE_EVIDENCE` and every truncated-
  search limitation binds.
- **Status:** Attempt 2 still waits on a fresh explicit operator grant
  with the byte-unchanged command of record (`--headless --random-world
  --seed 2026 --towns 3 --industries 3 --stop-on-delivery --cycles 2`);
  consumed grants (E141, E142, E145, attempt-1) are void for reuse; the
  offline success evaluator stays `verify <run-dir>` →
  `verified_loop_cycles`; the GUI-bearing native probe remains a
  separate later grant.

Evidence index E151.
