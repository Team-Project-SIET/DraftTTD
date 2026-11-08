# 05 — Build and prove the loop product

Type: task
Status: in-progress (offline build complete 2026-11-07; native proof run pending)
Blocked by: 04

## Question

Carry the decided architecture into the product: the loop engine runs
analyze → plan → play cycles on one live ramrom world with the spectator
GUI, CP-SAT selecting services per cycle, soft operator-close handling,
per-cycle recording, and the feasibility fixes of ticket 03 behind the
qualification layer. The proof of record: the full offline build suite
the change touches stays green, the tickets' offline fixtures show
cycles qualifying, and then the operator-granted native proof run
executes at least one full loop cycle delivering on screen with the
replay/report artifacts retained. Regression note of record (user
decision): the FULL offline suite including the 53 legacy reds becomes
an EXIT gate of the map — while tasks remain open it is not run as a
gate; this ticket's own touched suites must be green.

## Build record (2026-11-07 offline round)

- `run_loops` + `loop_gate` (`app/simulation/openttd/proof/freight_delivery.py`,
  working-tree sha256 prefix `7c3e31555b44aaed`): the loop branch inside
  `run()` executes `m["loop_cycles"]` sealed cycles on one launch — cycle 1
  reuses the attempt's connection, later cycles reconnect once at the cycle
  top (spec §3.2: one connect per cycle, none inside), write their
  `loop-cycle-{k}` directory with byte-equal copies of `PRELAUNCH.json`,
  `PRELAUNCH.sha256`, `CLAIM.json` and `frozen-source.zip`, their own
  `runtime-identity.json`, their own `before`/`qualified`/`after` saves and a
  per-cycle `artifact-manifest.sha256`. Each cycle re-plans with
  `exclude=<built identities>` so CP-SAT forms only new services; a
  `NO_FEASIBLE_SERVICES` cycle is a typed `ZERO_SERVICE` outcome (soft end of
  record), and two consecutive zero-service cycles mark the world
  `abandoned_world` (spec §3.5) and end the attempt typed. Run statuses:
  `NATIVE_LOOP_DELIVERED_VERIFIED` / `NATIVE_LOOP_ZERO_SERVICES`.
- `exclude=()` threaded through `freight_native_network.py` (working tree
  sha256 prefix `707d34461cd8d726`): `execute_network` →
  `plan_network_world` → `_plan_network_world` → `network_from_facts`, where
  excluded (source, destination, cargo) identities skip before P08/P05 with a
  `SERVICE_ALREADY_BUILT` rejection record, and an all-excluded capture set
  raises `NO_FEASIBLE_SERVICES: all N captured relationships are excluded
  already-built services` (never "no supported engine", never infeasibility).
  `execute_network` now returns the selected services so the loop can derive
  exclusions in-process.
- Offline fixtures of record (`tests/test_freight_loops.py`, 14 tests,
  sha256 prefix `4d714fb322eb94ce`): a second-cycle plan on the qualified
  fixture excludes the built benchmark identity and keeps the other two;
  an all-excluded set raises the typed message; budgets scale only volume
  keys linearly with sealed cycles; the pause pause/resume pair fires once
  and records `pause_pairs` (failed resume recorded, never silent);
  `loop_gate`, `validate_loop_cycles`, prepare loop validation and the CLI
  `--cycles` ranges refuse out-of-band values.
- CLI `--cycles` (1..8, requires `--random-world`; sha256 prefix
  `394db0f460358c48`): sealed at prepare time into `PRELAUNCH.json`
  (`loop_cycles`, recorded only when > 1), budgets of
  `network_budgets(..., loop_cycles=k)` (requests, mutations,
  supplemental_requests, total_seconds, construction_commands × k) recomputed
  identically by `preflight`, `verify_finance_receipt`, `verify_receipt` and
  `verify_network_receipt`; the loop demo flow writes per-cycle P07 reports
  and a `loops.md` run summary (spec §3.6).
- M2 capture pacing (ticket 03 family decision of record in
  [docs/random-world-capture-pacing-decision-2026-11-07.md](../../../docs/random-world-capture-pacing-decision-2026-11-07.md)):
  `paused_world_clock()` pauses the world for each random-world supplemental
  capture and resumes in `finally`; `pause_pairs`/`pause_resume_error`
  recorded per attempt.

## Touched suites of record (2026-11-07, all green)

`tests/test_freight_loops.py` (14), `tests/test_native_freight_network.py`,
`tests/test_freight_network.py`, `tests/test_network_world_preparation.py`,
`tests/test_freight_continuous.py`, `tests/test_openttd_demo.py` (expected
prepare kwargs updated for the `loop_cycles` keyword),
`tests/test_freight_delivery.py` — 151 passed. ruff/format/`py_compile`
clean; `git diff --check` clean; `ty` reports 1 diagnostic on the touched
files (the pre-existing `viewer.log.closed` count, never repaired).

## Verify-fix round (2026-11-07 later, E144 offline; fixes E143's false claims)

E143 asserted `verify_network_receipt` recomputes scaled budgets and that
per-cycle replay works; both were false at `6dbbcf5`. This round makes them
true and completes the §3.5 recording discipline. All offline, no native
authority consumed (E141 grant stayed consumed).

Fixed implementation defects (all pre-existing at `6dbbcf5`):

1. `verify_network_receipt` recomputed budgets without `loop_cycles` — every
   cycle verify failed "network seal or budgets mismatch". The verify prologue
   is extracted as `_replay_network_world` and seals
   `network_budgets(..., loop_cycles=metadata.get("loop_cycles", 1))`.
2. Per-cycle recording was absent: now every `loop-cycle-{k}` dir carries its
   own `frames.json` (root-frame slice per `loop-cycle.json`'s
   `frames_start`), `qualification-prefix-frames.json` written as
   `backend.planning_frames[backend.planning_frames_start:]`
   (`freight_runtime_planning.py`), scoped per-cycle `result.json` (delivery)
   or `cycle-result.json` (zero) pinned at one connection, and
   cleanup/log copies with a final manifest rewrite in `run()`'s `finally`.
3. Funding is verified once per attempt: cycle 1 gets the capital file copies
   and `loop-cycle.json` says `funding_frames=4`; later cycles say 0 and
   `freight_planning_replay.py` skips the funding replay; the root funding of
   record replays via `verify_capital_frames(root, frames[5:9])` inside
   `verify_loop_receipt`.
4. Fresh `ScenarioPlanningAccounting` per connection with `enter("setup")` and
   re-subscribe on reconnect (the frame machine of record is per single
   connection; raw rows still append to the shared root `frames` list);
   `result["connections"]` now counts reconnects.
5. Prior cycles' plan digests thread as `foreign_plans` through
   `execute_network` → `service_construction` →
   `command_readback_evidence`, so the shared one-server-log construction
   lines of prior cycles are skipped instead of tripping "construction
   command provenance mismatch".
6. `on_delivered` receives the cycle's prepared directory, so the demo viewer
   reads that cycle's `receipt.json` (the root has none in loop mode).
7. New `verify_loop_receipt(directory)` walks the root status, derives prior
   cycles' exclude sets from their sealed `loop-excluded-sources.json`
   (service triples recorded at run time; the demand-id reverse map was
   dropped as unreliable), and replays each delivery cycle via
   `verify_network_receipt(exclude=..., foreign_plans=...)` or each
   zero-service cycle via new `verify_loop_zero_service_cycle` (typed error
   reproduction + diagnostic + cleanup). The `main()` verify branch calls it.
8. Repo-gate lint regressions inherited from E143's round are repaired
   (`drequests` percent-format, one long budget line, one long signature ×2).

Offline top-up tests (9 new; `tests/test_freight_loops.py`, sha256 prefix
`be63cacc0c4d6f51`): missing/tampered/non-loop/failed loop recordings all fail
typed before any cycle replay; a bad `loop-cycle.json` marker refuses
`replay_qualified_world`; `command_readback_evidence` skips known foreign
plan digests (same cycle and prior cycles) and refuses unknown digests.

Preflight of record (offline only, no launch): binary + OpenGFX pinned
(`check(graphical=False)`); `--cycles 2` sealed budgets hold
requests 87→174, mutations 33→66, supplemental_requests 33345→66690,
total_seconds 1200→2400, construction_commands 192→384, selected_services 3,
launches 1; `verify` CLI on a loop root fails typed
("loop cycle recording missing: loop-cycle-1", rc 1); retained E139 demo read
only, `frames.json`/`qualification-prefix-frames.json` untouched
(prefix==slice still holds).

Touched suites of record all green again: 160 passed (151 previous + 9 new);
ruff/format/`py_compile` clean on every touched path (now including the two
inherited lint fixes); `uvx ty check` clean on all six touched paths.

## Native proof still owed by this ticket (per-attempt grant required)

### Attempt E145 (2026-11-07): granted two-cycle attempt failed typed pre-launch; repaired offline same day (E146)

The one granted attempt of the command of record below failed typed before
any OpenTTD launch:

```
Demo startup/run failed: STAGING_SEAM_DRIFT: delivery.nut seam drequests>=87 matched 0 times, expected 1
```

Retained directory `artifacts/demos/playable-demo-7b178d7093d9452a8f4d08806efa1b60`
(graphics-identity + empty `isolated/`; no runtime bytes beyond staging).
Root cause: the loop-scaled seam was stamped into `delivery.nut` before
`stage_random`, whose seam audit anchors the pre-stage shape; repaired
offline (E146) — pre-stage seam restored, `stage_random` now stamps the
scaled floor via keyword `seam_requests`, and the reopen-verify replica
recomposes with `loop_cycles`. The staging audit now passes offline
end-to-end for `--cycles 2` (tests in `test_random_capture_budgets.py`).
### E147 (2026-11-08): the staging lifecycle proven offline end-to-end

The E146 repair is pinned by lifecycle tests, not unit seams alone
(E147 in `EVIDENCE_INDEX.md`; `REPRODUCE.md` addendum #5; TASKS ledger
row). New offline tests only, `tests/test_random_capture_budgets.py`
(sha256 prefix `f6a432e2b771231b`): the full `prepare`+`preflight`
lifecycle at `--cycles 2` with the command-of-record capture profile
(sealed budgets 174/66/66,690/2400/384; scaled seam `drequests>=174` once
per file in BOTH the workspace package and the frozen-source `staged/`
bytes; no claim); the `--cycles 1` lifecycle byte-parity with the retained
proven composition (whole staged package); a spy pinning the stage
call-site contract `seam_requests == network_budgets(...)["requests"]` for
`loop_cycles` 1/2/8 (87/174/696 — composition-side scaling cannot silently
diverge from the audited stage or the sealed budget); boundary pins for
the two-service legacy seam (58) and the audited pre-stage shape at k=2/8.
Staging suite 13 passed; adjacent tuple 260 passed; planning tuple
120 passed + 1 self-skipped native-gated proof.

**Verdict: `OFFLINE FIX VERIFIED` / `NATIVE VERIFICATION PENDING`** — the
staging path provably passes its audit offline for every cycle depth; the
world, capture pacing, reconnect and loop recordings remain unproven
natively; the next attempt requires a fresh explicit operator grant.

1. ONE operator grant: the loop command of record below runs `--cycles 2`.
2. The first cycle delivers ≥1 verified service on screen; the second cycle
   reconnects once and verifies its own delivery (or the world types
   `abandoned_world` after two zero-service cycles).
3. Per-cycle `loop-cycle-{k}` directories replay: `python -m
   app.simulation.openttd.proof.freight_delivery verify <run-dir>` must
   verify every cycle's retained readback and print `verified_loop_cycles`.
4. The pacing fence holds: `pause_pairs == captured_relationships` per
   cycle diagnostic, console log shows the exact pairs, no
   `pause_resume_error`; a stalled paused capture types
   `PAUSED_CAPTURE_UNRESPONSIVE` and the decision returns to the operator
   with evidence (see pacing decision §4.5).
5. The 53-legacy-red FULL regression stays the map EXIT gate; not this
   ticket's gate.

Command of record for the native loop proof (requires OPENTTD_BINARY and
OPENTTD_OPENGFX_ARCHIVE set before Python starts, exactly like the E141
widened-seal attempt):

```bash
.venv/bin/python -m app.openttd_demo run --headless --random-world \
  --seed 2026 --towns 3 --industries 3 --stop-on-delivery --cycles 2
```

## Execution-mode decision (2026-11-08, E148: GUI vs `--headless`)

Spec §1/§3.3 make the spectator window and its window-close soft end part of
the finished product, while the qualification command of record above runs
`--headless`. Decided of record
([docs/gui-headless-execution-mode-decision-2026-11-08.md](../../../docs/gui-headless-execution-mode-decision-2026-11-08.md)):
the qualification attempt of record keeps `--headless` exactly as commanded,
because every acceptance bar of this ticket is receipt-based (≥1 verified
service, `verified_loop_cycles` replay, pacing fences, honestly typed
terminals) and names no GUI, and the whole native history of the loop line
(E139/E141/E145) is headless. The §1 spectator GUI and the §3.3
window-close soft end stay product-definition scope that their own later,
separately granted GUI-bearing element must exercise natively (without
`--stop-on-delivery`, with the viewing hold, ended-by-operator never typed
as a system failure); until then they are owed, not satisfied: a headless
run's only operator soft end is Ctrl+C. No command, criterion or budget of
the record changed.

## GUI product-scope build record (2026-11-08 offline round, E149)

The E148 owed element's code half is implemented offline; the native GUI
probe stays owed. Touched files and digests of record:
`app/simulation/openttd/proof/freight_delivery.py` (`4bbff81a0cd5fc52`) and
`app/openttd_demo.py` (`db2051dea8885642`), tests
`tests/test_openttd_demo.py` (`9c38d38f334d77fc`).

- **Typed soft end (harness):** new `OperatorWindowClosed(RuntimeError)`
  documented as the spec §1/§3.3 soft ended-by-operator phase end;
  `run` initializes `backend.client_soft = None` and `soft_gate()` raises
  the typed soft end from the flag — planted at the AdminPort exchange
  boundaries (`query()`, both scenario-capital exchanges, the planner
  admission exchange, the `before` save); the new
  `except OperatorWindowClosed` branch types `result` as
  `ENDED_BY_OPERATOR` with `operator_soft_end` and no `error` key; the
  unchanged `finally` still seals the retained receipts, saves, frames,
  cleanup and manifest exactly as before, and every verifier keeps
  refusing the non-verified root status (exact-status comparisons).
- **Viewer classification (demo):** `Viewer.check_client_exit()` — an owned
  spectator client exiting rc 0 raises the typed soft end after stamping
  `backend.client_soft`; a non-zero exit keeps the exact E140-shape typed
  failure; the watch loop and `delivered()` use it; the startup
  `require_alive()` keeps its hard typing (the E8 spectator class); a close
  during the delivered view-hold ends the hold softly after completion and
  never retypes a verified run; `run_demo` maps `ENDED_BY_OPERATOR` to a
  clean rc 0 honest print.
- **Tests of record:** 5 new offline tests (viewer classification pair,
  exchange-boundary gate, network-path surfacing with sealed cleanup,
  view-hold close, run_demo rc-0 mapping) under the file's autouse
  no-native guard; adjacent tuple 265 passed / 0 failed; ruff/format/
  `py_compile`/`git diff --check` clean; `ty` clean on both app files,
  one pre-existing counted diagnostic on the test file.
- **Not claimed:** no native GUI evidence exists. The GUI-bearing native
  probe (product line WITHOUT `--stop-on-delivery`, with the view hold,
  real window close, ended-by-operator record) stays owed behind a fresh
  per-attempt grant. Headless loop behavior of record is byte-preserved:
  `--stop-on-delivery` short-circuit, headless Viewer branches, budgets,
  AdminPort boundaries, the ticket-05 command of record and its staging
  suites are untouched and green.

## Attempt-1 record — Phase C headless loop qualification: EXECUTED ONCE, FAILED, SEALED (2026-11-08, E150)

The operator's verbatim one-attempt grant ("No retry, no seed change, no
additional launch, and no execution outside the approved scope. Stop
immediately on any unexpected failure. Preserve all sealed historical
evidence. After execution, independently verify both cycles and reassess
FD-C-2 using fresh digest-pinned evidence.") authorized the single attempt
of record; it ran exactly once with the unchanged command of record and
FAILED with exit 1 before any cycle completed, so the stop constraint was
honored with no retry, no relaunch and no seed change. The run dir of
record `artifacts/demos/playable-demo-246dc3a4f4fc4b40aee0f73696455473` is
sealed and immutable: `status=FAILED`, error
`FileNotFoundError: [Errno 2] No such file or directory:
'.../loop-cycle-1/graphics-identity.json'`, launches 1 / connections 1 /
requests 0 / mutations 0 with the cycle-1 funding retained (2 requests, 1
mutation), `failure_save_error="owned native save completion missing"`,
cleanup fully reaped at root and cycle level, and no `loop-cycle-2`.

Facts captured before the crash stay evidence: the native capture phase
completed 832/832 read pairs inside the qualified M2 month with
`pause_pairs=1` and no `pause_resume_error` (first native confirmation of
the E143 pacing fence), `compatible_relationships=16`, and the retained
`planning-n0-*` pairs; `search_truncated=true` and
`captured_relationships=0` type the search as truncated, so FD-C-2 stays
`INCOMPLETE_EVIDENCE` — no feasibility claim may be built on attempt 1.

Root cause: the cycle-1 `execute_network` flow digests
`graphics-identity.json` from the cycle dir (supplemental planning facts
content digest in `freight_runtime_planning.py`) while the per-cycle copy
set carried only `PRELAUNCH.json`, `PRELAUNCH.sha256`, `CLAIM.json` and
`frozen-source.zip`. Fix of record (E150 offline round): the cycle staging
copies a content-identical `graphics-identity.json` per cycle
(`app/simulation/openttd/proof/freight_delivery.py`, digest
`6f913b555e05ca05`; E143's guaranteed per-cycle list is superseded by the
E150 row), pinned by
`test_loop_cycle_recording_copies_the_graphics_identity_per_cycle` in
`tests/test_openttd_demo.py` (`2934214451eb1e2d`). Adjacent tuple
266 passed / 0 failed; ruff/format/`py_compile`/`git diff --check` clean;
`ty` clean on both app files with the single pre-existing counted
diagnostic on the test file.

The command of record stays byte-unchanged for the next attempt, which
waits on a fresh explicit operator grant; consumed grants (E141, E142,
E145, attempt-1) are void for reuse. The GUI-bearing native probe remains
a separate, later grant.

## Post-attempt-1 audit note — cycle-chain artifact audit closed offline (2026-11-08, E151)

Offline follow-up under the E150 fix, no app code changed (no launch, no
AdminPort, no staging, no claim). The full run-time cycle-1 recording
and planning path was audited again for missing artifacts: nothing
further is missing. Every plain-constant `prepared.directory` read in
the run-time chain (`freight_native_network.py` +
`freight_runtime_planning.py`) classifies per occurrence into exactly
six names: root-stage copies (`PRELAUNCH.json`,
`graphics-identity.json`), the per-cycle staging self-write
(`runtime-identity.json`), the chain self-write before read
(`qualification-prefix-frames.json`), and exchange-disc packets
(`capacity-add-response.json`, `capacity-read-response.json`);
verify-path plain `directory` reads are a different layer covered by the
E150 copy set plus the finalize copies. The audit is pinned by an AST
drift-guard test, so any future unclassified chain read fails its own
test instead of a native launch.

Two more end-to-end offline tests pin the fixed seam and the sealed
history: one stages an `attempt/loop-cycle-1` exactly like `run_loops`
does and drives the real `capture_planning_facts` offline against the
staged recording alone (450 tiles / 900 coverage, digest-bound
`content_digest` from the per-cycle `graphics-identity.json`,
`generation_seed` 17 from the per-cycle runtime identity, retained
`supplemental-planning-facts.json` and `planning-n0-*` packets); the
other re-derives the sealed attempt-1 manifest at root and `loop-cycle-1/`
with its typed FAILED identity verbatim — a clone without the retained
bytes fails as missing evidence, never regeneration.

Verification: `tests/test_freight_loops.py` 26 passed (23 prior + 3);
the 13-file adjacent tuple of record 269 passed / 0 failed plus
`tests/test_random_distance.py` 13, rc 0; ruff/format/`py_compile`/
`git diff --check` clean; `ty` clean on the touched files (single
pre-existing counted `viewer.log.closed` diagnostic stands). Digests of
record unchanged from E150; FD-C-2 stays `INCOMPLETE_EVIDENCE`. The
command of record stays byte-unchanged; Attempt 2 waits on a fresh
explicit operator grant (consumed: E141, E142, E145, attempt-1 — void
for reuse); the GUI-bearing native probe remains a separate later grant.

## Attempt-2 record — Phase C loop qualification: EXECUTED ONCE, FAILED, SEALED (2026-11-08, E152)

The operator's fresh explicit grant ran the byte-unchanged command of
record once (seed 2026, 3 towns / 3 industries, headless random world,
two cycles, one launch with one qualified connection per cycle). It
stopped typed on the first unexpected failure — no retry, no relaunch,
no artifact mutation, strictly no code change under the grant. Run dir
of record: `artifacts/demos/playable-demo-e6852692d0ef40199db0c71b101b2dda`
(root `status=FAILED`, `ValueError: duplicate/out-of-order native read
evidence`, launches 1 / connections 2 / requests 0 / mutations 0,
funding 2/1, owned failure save completed and retained — attempt-1's
save defect does not recur).

The E150 per-cycle copy-set fix is PROVEN LIVE: `graphics-identity.json`
is present and digest-covered in both cycle dirs and the chain passed
attempt-1's crash seam. Cycle 1 recorded natively end-to-end to a typed
zero-service terminal: `cycle-result.json`
`NATIVE_LOOP_ZERO_SERVICES` with `planning_error="ValueError:
NO_FEASIBLE_SERVICES: no supported full-load road engine and supply"`,
9,702/9,702 capture pairs completed, `pause_pairs=6` with no
`pause_resume_error`, compatible 16 / captured 6 / `search_truncated
=true` / candidates 0, per-cycle cleanup fully certified. Cycle 2 staged
correctly (full copy set + runtime identity + `loop-cycle.json`
frames_start 20463 / funding_frames 0) and failed at its first
qualification clock poll before any capture: the qualification evidence
parser reads the ONE shared per-attempt server `stderr.log` while
per-cycle sessions restart poll counters at 1 under the constant session
id `freight-plan`, so every clock request id appears exactly twice in
the retained stderr (e.g. `freight-plan-clock-1` at lines 87–89 and
1143–1145) and the typed duplicate/out-of-order guard fired before
cycle-2's own markers — never the deadline. Classification: the same
defect family as E150 (a per-attempt-shared artifact consumed per-cycle
with per-cycle-reset identity state), second instance, new surface.

FD-C-2 stays `INCOMPLETE_EVIDENCE` from fresh digest-pinned evidence:
cycle-1's search is typed truncated with candidates 0, and its
zero-service terminal is an observed outcome, never a completed
feasibility search. All three retained manifests re-derive digest-for-
digest equal (root 18, cycle-1 19,440, cycle-2 13 entries); the loop-
receipt instrument refuses the dir typed
(`loop attempt did not reach a verified terminal status`) with no forced
relabel; no native OpenTTD process remains.

**Stop point:** no fix applied under the consumed attempt-2 grant. The
repair design (per-cycle qualification request-id namespace or a
cycle-scoped stderr marker window) and its offline round are a separate
operator-approved step; Attempt 3 then needs a fresh explicit operator
grant with the byte-unchanged command of record. The GUI-bearing native
probe remains a separate later grant.
