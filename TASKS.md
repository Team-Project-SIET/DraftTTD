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
