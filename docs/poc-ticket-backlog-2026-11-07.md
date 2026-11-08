# Full-Scope Functional PoC — ticket backlog (2026-11-07)

Round record for the ramrom-product wayfinder effort
(`.scratch/ramrom-product/map.md`). Objective of the round: close the
books on 2026-11-07's two natively executed attempts and resolve the
feasibility-diagnosis research ticket, all offline over retained bytes;
native-run grants for the fix proof remain per-attempt decisions of the
operator.

## Status log (2026-11-07)

- Books of record for the two one-shot native attempts of this day:
  (a) the random-world seed-2026 run
  `artifacts/demos/playable-demo-3e93cc7d1e8d43aab66a4f653665caaa` — typed
  terminal `ValueError: NO_FEASIBLE_SERVICES: no supported full-load road
  engine and supply`, `result.json` status FAILED, connections 1, requests
  0; artifact manifest 1556/1556 verified; cleanup all-true; no openttd
  process remained. Evidence index E139.
  (b) the seed-42 demo run
  `artifacts/demos/playable-demo-1570c66a2e564613a102b3e95647e8b1` —
  typed FAILED when the operator closed the game window mid-run
  (`RuntimeError: Graphical client exited (0)`); P05 had selected 3
  services, 33 construction mutations and 1 funding mutation landed,
  deliveries did not finish before the close; one attempt, no retry.
  This run is the recorded evidence behind the soft-close design clause
  of the ramrom product. Evidence index E140.
- Research ticket `01-feasibility-diagnosis.md` resolved (offline, zero
  native attempts): the funnel of record is capture-seal geometry — 14/16
  compatible relationships rejected `CAPTURE_TILE_BUDGET` before any
  engine/supply facts were gathered; discovery truncated at the
  16-relationship cap (`CANDIDATE_SEARCH_LIMIT`, 146 of 8192 pair
  checks); the 2 captured coal relationships then failed
  `NO_BOUNDED_CORRIDOR` both times at the same town-road band
  (x≈183..192) inside detour-free strips, reproduced on the raw capture
  bytes offline; the engine catalog (Balogh Coal Truck, engine 123) and
  supply gates were never the bottleneck; CP-SAT was never invoked.
  Findings file of record:
  `.scratch/ramrom-product/research/01-feasibility-diagnosis.md`
  (§1–§7 byte-cited; §8 OpenTTD-wiki verification addendum).
- Legacy 53 offline reds: untouched, tracked in the map fog; the full
  regression (including them) stays the wayfinder EXIT gate per the
  operator's standing decision — not run while map tasks remain open.
- No native run this round; no grant consumed; no `artifacts/` byte
  modified; conservation of supersession: failed and aborted attempts
  recorded at their own identities, never relabeled.

## Status log (2026-11-07, granted native proof of ticket 03)

- The operator granted ONE native attempt in session: the widened-seal
  command of record on seed 2026, world settings of record (towns 3,
  industries 3). The attempt ran once and is recorded honestly at its own
  identity (`artifacts/demos/playable-demo-9b9a398e406f4ec1bf8e37a69116ac93`,
  evidence index E141). Typed terminal:
  `PlanningFactError: supplemental capture outside final M2 month` — the
  qualified-month gate refused fact capture whose economy dates crossed the
  M2 window end (712282) at live game speed. Relationship n0 captured
  completely (832 reads) inside the window; n1 was interrupted at read 703;
  2238 capture reads completed overall; no `NO_FEASIBLE_SERVICES` and no
  engine/supply rejection occurred — the funnel advanced past both E139
  gates. The acceptance bar `≥1 verified plan+delivery terminal` is NOT
  met by this run; it stays open evidence-indexed, not relabeled.
- Next decision of record (unresolved): capture-read pace must fit the
  qualified in-game month — the candidate design is pausing the world
  clock during fact capture (recorded in the diagnostic), or an equivalent
  pacing boundary. No further native attempt is scheduled without a fresh
  per-attempt operator grant.

## Status log (2026-11-07, Project Phase C offline round — FD-C-1/FD-C-2)

- Offline only: no OpenTTD launch, no AdminPort connection, no candidate
  staging or signing, no claim consumption, no native receipt, no
  `artifacts/` byte modified; one commit, no push. Full record:
  [docs/phase-c-reconciliation-feasibility-2026-11-07.md](phase-c-reconciliation-feasibility-2026-11-07.md).
- **FD-C-1 verified rather than rebuilt.** The 2026-10-18/10-25
  reconciliation chain (policy `vacant-projection-1`, ADR-012/013) was
  re-derived from the retained seed-17 census inputs: five reports
  byte-equal (reconciliation `c1cfa970…`, ADR-012 `221ce926…`, ADR-013
  `7616f626…`, combined rebinding `079fce64…`, ADR-012-only rebinding
  `c9d11d41…`) and the 19-tile unknown-occupancy diagnosis (`66ed07cc…`)
  JSON-value-identical only (retained serialization came from a one-off
  driver) — counts 83→77 definitional + 6 temporal + 0 contradictions +
  0 unresolved, sealed `SOURCE_SAVE_FUSION REJECTED` and retained
  `INCOMPLETE_TILE_CLASSIFICATION` untouched, 19 UNKNOWN tiles map to
  `TERRAIN_MODIFICATION` in the derived planning layer only
  (`p08_binding.allowed=true`, `p08_complete=false`). Focused suites 83
  passed.
- **FD-C-2 built and offline-verified.** New typed decision engine
  `app/planning/phase_c_feasibility.py` `phase-c-feasibility/1`)
  with ten required dimensions, the five outcome classes under a
  deterministic precedence (`UNSUPPORTED_CAPABILITY` > completed-search
  `INFEASIBLE_FOR_OBSERVED_WORLD` > `SEPARATE_SCOPE_EXTENSION` >
  `INCOMPLETE_EVIDENCE` > `FEASIBLE_…`), a typed P05 prerequisite gate
  mirroring `freight_native_network.py:178`, single-domain evidence rows
  that refuse Candidate-11/D5/fixed-scenario domains at construction
  (both as strings and by set-disjointness), fail-closed absence rows
  carrying real file digests, and limits regex-pinned against their own
  source bytes (drift refuses). 48 focused tests green.
- **Decision of record**: `artifacts/experiments/phase-c-feasibility-
  2026-11-07/feasibility-decision-report.json` (sha256 `67183cf6…31fa4`)
  — outcome **`INCOMPLETE_EVIDENCE`**: 2 VERIFIED dimensions
  (industry_cargo_compatibility, supported_map_search_limits), 8 PARTIAL,
  27 digest-pinned rows, zero observed-world-infeasibility rows (every
  recorded bounded random-world search was truncated). Recommended next
  action: the capture-pacing design decision (ticket-03 family) under the
  roadmap fences, then a fresh gated native capture round.
- Verification ledger: both suites 131 passed; ruff/format/`py_compile`
  clean on touched paths; `git diff --check` clean; `ty` reports 1
  diagnostic on the touched files (deliberate runtime-validated refusal,
  counted, never repaired).

## Status log (2026-11-07, Phase C continuation — ticket-05 loop engine built offline + M2 pacing decided)

- Offline only: no OpenTTD launch, no AdminPort connection, no candidate
  staging or signing, no claim consumption, no native receipt, no
  `artifacts/` byte modified; one commit, no push. Recorded at
  `.scratch/ramrom-product/issues/05-build-loop-product.md` (build record
  section), `.scratch/ramrom-product/map.md` and
  [docs/random-world-capture-pacing-decision-2026-11-07.md](random-world-capture-pacing-decision-2026-11-07.md).
- **Ticket-05 loop engine built offline.** `run_loops`/`loop_gate`
  (working-tree sha256 prefix `7c3e3155…`): sealed `loop_cycles` cycles run
  on ONE launch with one fresh connect per cycle (spec §3.2), per-cycle
  `loop-cycle-{k}` directories carrying byte-equal identity copies
  (PRELAUNCH.json/sha256, CLAIM.json, frozen-source.zip), their own
  runtime-identity, own before/qualified/after saves and their own
  artifact-manifest; runs report `NATIVE_LOOP_DELIVERED_VERIFIED` or
  `NATIVE_LOOP_ZERO_SERVICES`, with two consecutive zero-service cycles
  typing `abandoned_world` (§3.5 K=2) — never a relabeled defect.
- **`exclude=()` threading** (`freight_native_network.py`, `707d3446…`):
  loop cycles pass already-built `(source, destination, cargo)` identities
  into `network_from_facts`, which skips them before P08/P05 with
  `SERVICE_ALREADY_BUILT` rejections; an all-excluded set raises the typed
  `NO_FEASIBLE_SERVICES: all N captured relationships are excluded
  already-built services`. `execute_network` returns its selected services
  so exclusions derive in-process.
- **CLI `--cycles`** (`app/openttd_demo.py`, `394db0f4…`): sealed at prepare
  (recorded in PRELAUNCH.json only when > 1), 1..8 validated, requires
  `--random-world`; volume budgets (`requests`, `mutations`,
  `supplemental_requests`, `total_seconds`, `construction_commands`) scale
  linearly via `network_budgets(..., loop_cycles=k)` and every recompute
  site (preflight, verify_finance_receipt, verify_receipt,
  verify_network_receipt) passes the sealed count; legacy single-cycle
  metadata bytes unchanged (byte-parity asserted by the untouched suites).
- **M2 capture pacing decided** (`019c605e…`): pause the world clock around
  every random-world supplemental capture (`paused_world_clock`, one
  pause/resume pair per relationship, `pause_pairs`/
  `pause_resume_error` in the planning diagnostic); rejects page-critical
  reordering and any widening of the M2 gate; per-attempt fences and the
  first-run pause-stall risk (`PAUSED_CAPTURE_UNRESPONSIVE`) in the decision
  doc.
- **Tests of record:** new `tests/test_freight_loops.py` (14: exclude
  selects only new services, typed all-excluded raise, budget scaling,
  bounds, pause pair/failed-resume, loop_gate, prepare gates, CLI errors)
  plus touched suites; total 151 passed. ruff/format/`py_compile` clean,
  `git diff --check` clean, `ty` 1 pre-existing count diagnostic
  (`viewer.log.closed`), never repaired.
- **Still owed by the ticket:** the operator-granted native loop proof —
  one launch, `--cycles 2`, first cycle delivering ≥1 verified service,
  per-cycle replay via `verify` printing `verified_loop_cycles`, pacing
  fences observed. Command of record in the ticket file. The 53-legacy-red
  FULL regression remains the wayfinder EXIT gate, not run this round.

## Status log (2026-11-08, Phase C continuation — execution-mode decision: spectator GUI stays product scope, attempt of record stays `--headless`)

- Docs-only decision round: no launch, no AdminPort connection, no staging,
  no `artifacts/` byte modified, no operator grant consumed; one commit, no
  push. Decision of record
  [docs/gui-headless-execution-mode-decision-2026-11-08.md](gui-headless-execution-mode-decision-2026-11-08.md);
  recorded at E148 (`EVIDENCE_INDEX.md`), the TASKS ledger,
  `AI_HANDOFF.md`, `REPRODUCE.md` addendum #6, ticket-05 (appended
  section) and `.scratch/ramrom-product/map.md`.
- **The GUI-vs-headless discrepancy is resolved without changing anything of
  the record.** Spec §1 (lines 17–21) and §3 item 3 (lines 104–108) give the
  finished product a spectator window whose close ends a phase softly; the
  qualification command of record runs `--headless --stop-on-delivery`
  (ticket-05 lines 194–208; `REPRODUCE.md` addenda #2–#5), launches no
  graphical client, and can never exercise that window close. Decided: the
  attempt of record keeps `--headless` — every acceptance bar is
  receipt-based (spec §2 lines 78–84; ticket-05 lines 196–207) and names no
  GUI, and the loop line's native history is headless (E139/E141/E145).
- **The spectator GUI and its window-close soft end stay owed as
  product-definition scope** for their own later, separately granted
  GUI-bearing probe (without `--stop-on-delivery`, with the viewing hold,
  ended-by-operator never typed as a system failure — E140's historical
  window close typed FAILED `RuntimeError: Graphical client exited (0)`).
  Until that probe runs, the window-close soft end is natively
  unexercised; a headless attempt's only operator soft end is Ctrl+C.
- **Offline checks:** staging suite `tests/test_random_capture_budgets.py`
  13 passed; `git diff --check` clean; source digests of record unchanged
  (`258ba9dbe19c7284`, `2cce3070c125bd41`, `f6a432e2b771231b`). No code
  change; the native command of record is unchanged and remains gated on a
  fresh explicit operator grant.

## Status log (2026-11-08, Phase C continuation — GUI product scope §1/§3.3 implemented offline: typed `ENDED_BY_OPERATOR` soft end)

- Offline implementation round: no OpenTTD launch, no AdminPort connection,
  no staging, no claim consumption, no native receipt, no `artifacts/` byte
  modified; one commit, no push. Recorded at E149 (`EVIDENCE_INDEX.md`), the
  TASKS ledger, `AI_HANDOFF.md`, `REPRODUCE.md` addendum #7, ticket-05 (GUI
  build-record section) and `.scratch/ramrom-product/map.md`.
- **The operator's spectator window close is now the typed soft end of
  record.** `OperatorWindowClosed` (a typed ended-by-operator soft end,
  never a system failure) plus `backend.client_soft` and `soft_gate()` in
  `app/simulation/openttd/proof/freight_delivery.py` (`4bbff81a0cd5fc52`):
  the attempt stops at the next AdminPort exchange boundary (`query()`,
  both scenario-capital exchanges, the planner admission exchange, the
  `before` save) and `run` types `result["status"] = "ENDED_BY_OPERATOR"`
  with `operator_soft_end` and no `error` key; the unchanged `finally`
  still seals receipts, saves, frames, cleanup and the manifest, and every
  verifier keeps refusing the non-verified root status.
- **Viewer classification** in `app/openttd_demo.py` (`db2051dea8885642`):
  `Viewer.check_client_exit()` types an owned client's rc 0 exit as the
  operator soft end and a non-zero exit as the exact E140-shape
  `RuntimeError: Graphical client exited (...)`; the startup
  `require_alive()` keeps its hard typing; a close during the delivered
  view-hold never retypes a verified run; `run_demo` maps the soft end to
  a clean rc 0.
- **Tests of record:** 5 new offline tests in `tests/test_openttd_demo.py`
  (`9c38d38f334d77fc`) under the file's autouse no-native guard; the
  adjacent tuple (13 files total) 265 passed / 0 failed; ruff/format/
  `py_compile`/`git diff --check` clean; `uvx ty check` clean on both app
  files with the one pre-existing counted `viewer.log.closed` diagnostic on
  the test file.
- **Kept separate from Phase C headless verification:** the headless loop
  command of record, its budgets, AdminPort boundaries and the
  staging/lifecycle suites are untouched and still green; `--stop-on-delivery`
  still short-circuits the view hold headlessly.
- **Native GUI verification pending:** the `IMPLEMENTATION VERIFIED` /
  `NATIVE GUI VERIFICATION PENDING` split of E149 holds — the spectator
  window process, the real close interaction and the ended-by-operator
  record need the GUI-bearing native probe (product line without
  `--stop-on-delivery`) behind its own fresh per-attempt grant; no
  feasibility or product-scope claim is made until that evidence exists.

## Status log (2026-11-08, Phase C continuation — attempt-1 loop qualification consumed one grant and FAILED; sealed; offline fix)

- The operator's verbatim one-attempt grant authorized the Phase C loop
  qualification attempt of record; it executed exactly once with the
  unchanged command of record (headless, `--seed 2026`, `--cycles 2`) and
  FAILED with exit 1 before any cycle completed; the stop constraint was
  honored with no retry, no relaunch and no seed change. Recorded at E150
  (`EVIDENCE_INDEX.md`), the TASKS ledger, `AI_HANDOFF.md`,
  `REPRODUCE.md` addendum #8, ticket-05 attempt-1 record and
  `.scratch/ramrom-product/map.md`.
- **Sealed failure of record (run dir
  `artifacts/demos/playable-demo-246dc3a4f4fc4b40aee0f73696455473`,
  read-only hereafter):** `status=FAILED`, error
  `FileNotFoundError: [Errno 2] No such file or directory:
  '.../loop-cycle-1/graphics-identity.json'`, launches 1 / connections 1 /
  requests 0 / mutations 0, cycle-1 funding retained (2 requests, 1
  mutation), `failure_save_error="owned native save completion missing"`,
  cleanup fully reaped/disposed at root and cycle level, no `loop-cycle-2`.
- **Native pacing datum (first of its kind):** the cycle-1 diagnostic shows
  the capture phase completed 832/832 read pairs inside the qualified M2
  month with `pause_pairs=1` and no `pause_resume_error` — the E143 pacing
  fence held natively; `compatible_relationships=16`;
  `captured_relationships=0`, `search_truncated=true`.
- **FD-C-2 stays `INCOMPLETE_EVIDENCE`:** the attempt failed before any
  performing search completed and every captured search is truncated; no
  feasibility or infeasibility claim may be built on attempt 1.
- **Root cause + fix (offline, smallest):** the cycle flow digests
  `graphics-identity.json` from the cycle dir while E143's per-cycle copy
  set carried only `PRELAUNCH.json`, `PRELAUNCH.sha256`, `CLAIM.json` and
  `frozen-source.zip`; the copy set now includes a content-identical
  `graphics-identity.json` (`freight_delivery.py` `6f913b555e05ca05`,
  superseding E143's guaranteed per-cycle list), pinned by
  `test_loop_cycle_recording_copies_the_graphics_identity_per_cycle`
  (`tests/test_openttd_demo.py` `2934214451eb1e2d`). Adjacent tuple
  266 passed / 0 failed; ruff/format/`py_compile`/`git diff --check`
  clean; `ty` clean on both app files with the single pre-existing counted
  test-file diagnostic.
- **Gate of record:** the command of record stays byte-unchanged; the next
  Phase C attempt waits on a fresh explicit operator grant (consumed
  grants: E141, E142, E145, attempt-1 — all void for reuse); the
  GUI-bearing native probe remains a separate later grant; the 53-legacy-red
  FULL regression stays the wayfinder EXIT gate.
- **E151 offline follow-up (2026-11-08):** the full run-time cycle-1
  chain audit found nothing further missing after the E150 fix — every
  plain-constant `prepared.directory` read in
  `freight_native_network.py` + `freight_runtime_planning.py`
  classifies per occurrence into exactly six names (root-stage copies
  `PRELAUNCH.json`/`graphics-identity.json`, the per-cycle staging
  self-write `runtime-identity.json`, the chain self-write
  `qualification-prefix-frames.json`, and exchange-disc packets
  `capacity-add-response.json`/`capacity-read-response.json`), pinned by
  an AST drift-guard test in `tests/test_freight_loops.py` (three new
  tests: drift guard, staged-cycle-dir e2e capture through the real
  `capture_planning_facts` — 450 tiles / 900 coverage, digest-bound
  `content_digest`, `generation_seed` 17 from the per-cycle identity —
  and the sealed attempt-1 read-only pin re-deriving its manifest and
  typed FAILED identity). 13-file adjacent tuple 269 passed / 0 failed
  plus `tests/random_distance` 13; hygiene clean; `ty` clean on touched
  files; no app code changed (digests unchanged from E150).
- **Gate of record:** unchanged — Attempt 2 waits on a fresh explicit
  operator grant with the byte-unchanged command of record; consumed
  grants (E141, E142, E145, attempt-1) void for reuse; FD-C-2 stays
  `INCOMPLETE_EVIDENCE`; the 53-legacy-red FULL regression stays the
  wayfinder EXIT gate.
- **E152 attempt-2 (2026-11-08, native):** the fresh explicit grant ran
  the byte-unchanged command of record once; it failed typed and was
  sealed (`playable-demo-e6852692d0ef40199db0c71b101b2dda`:
  `duplicate/out-of-order native read evidence`, launches 1 /
  connections 2, owned failure save completed and retained, cleanup
  fully certified at root and both cycles). Outcomes: the E150
  per-cycle copy set is proven live (the crash seam of attempt 1
  passed); cycle 1 completed a full native recording to a typed
  zero-service terminal (`NATIVE_LOOP_ZERO_SERVICES`, 9,702/9,702
  capture pairs, `pause_pairs=6`, truncated search / candidates 0);
  cycle 2 died at its first qualification clock poll — per-cycle poll
  counters restart at 1 under the constant `freight-plan` session id,
  so every clock request id appears twice in the ONE shared server
  `stderr.log` and the typed duplicate guard fired before cycle-2's own
  markers (same defect family as E150: per-attempt-shared artifact
  consumed per-cycle; new surface).
- **FD-C-2:** still `INCOMPLETE_EVIDENCE` (truncated search, candidates
  0; zero-service observed, never a completed feasibility search). All
  three retained manifests re-derive equal; the loop-receipt instrument
  refuses the dir typed, no forced relabel; no native process remains.
- **Gate of record:** no fix under the consumed attempt-2 grant; an
  offline repair round (per-cycle qualification id namespace or
  cycle-scoped stderr window) is a separate operator-approved step;
  Attempt 3 then needs a fresh explicit operator grant with the
  byte-unchanged command of record. The GUI-bearing native probe
  remains a separate later grant; the 53-legacy-red FULL regression
  stays the wayfinder EXIT gate.
