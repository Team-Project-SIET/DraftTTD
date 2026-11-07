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
**The next attempt needs a fresh explicit operator grant.**

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
