# 03 — Attempt 5 save-stall forensics (read-only)

Base: run dir
`artifacts/demos/playable-demo-48abc4b955c14e0fadea7730cd487d86`
(Attempt 5, FAILED typed, sealed), repo `42bbe5f`, OpenTTD 15.3
primary source (github.com/OpenTTD/OpenTTD at tag `15.3`). No native
execution, no evidence bytes touched. 2026-11-10.

## 1. The decisive record

| when (UTC+7) | event | evidence |
|---|---|---|
| 23:02:47.648 | final capture readback `planning-n0-831` response written (dates 712287) | mtime, `loop-cycle-1/planning-n0-831-response.json` |
| 23:02:47.66..79 | runner exits `paused_world_clock` → `console()` writes `unpause` to game stdin pipe | `freight_native_network.py:236/241` (`round_mutation.console`), `finally` at 240-247 |
| 23:02:47.79..84 | runner writes `save "<cycle-dir>/qualified"` (issue of `road_mutation.save`) | `freight_native_network.py:405` → `road_mutation.save:342` |
| 23:02:48 → 23:03:02.8 | game prints NO console output; marker absent; `stdout.log` has no 5th `Saving map...`; stderr silent (`[script:*]` last at 23:02:22) | `stdout.log`, `stderr.log` |
| 23:03:02.86 | runner's 15 s marker guard expires → `TimeoutError("owned native save completion missing")` | `road_mutation.save:366-367`; deadline = issue + 15 s |
| ≈23:03:02.9 | failure handler writes `save ".../failure"` (3rd stdin write) | `freight_delivery.py:2044-2050` |
| 23:03:02.85-03.2 | game processes all queued console lines: `unpause` echo, `Saving map...` → `Map successfully saved` (qualified), then `Saving map...` → failure save | `stdout.log` line order; `qualified.sav` mtime 23:03:02.968; `failure.sav` ack 23:03:03.2 |
| 23:03:03.3 | admin disconnect, cleanup certified, process quits rc=0 | `stderr.log`, `cleanup.json` |

The failing save completed about 0.13 s after the guard had already
typed the run FAILED. The `qualified.sav` exists and is valid
(sha256 `4993714a90c1fc8c551889bbff3ba9d581fd18d6e548e58e7955acf999c45030`,
80,516 bytes) but arrives after the typed outcome — it is evidence,
not the world of record for any verified status.

## 2. What the game was NOT doing wrong

- Admin/GameScript path healthy to the last instant: 832 tile reads
  (`planning-n0-0..831`, `kind:"tile"`) serviced at ≈26 ms/pair cadence
  23:02:25.09 → 23:02:47.65, all matched request/response files retained.
- The pause was honored: capture-side dates frozen at 712287 (the
  `network-facts-0.json` window), manual `pause` echo present in
  `stdout.log`.
- No GameScript watchdog/abort lines anywhere in `stderr.log`
  (grep `mistake|watchdog|aborted` → 0); process quit cleanly rc=0.
- Saves themselves are fast once executed: `failure.sav` command
  written ≈23:03:02.9, ack 23:03:03.2 (≈0.3 s); the prior three saves
  (root `before`, cycle `before`, capital funding block) all acked in
  well under a second at 23:00:15-16.
- `planning_read` handlers log nothing by design
  (`freight_delivery_package/planner.nut` `PlanningRead` has no
  `GSLog.Info`), so the GameScript stderr silence during the capture
  is expected, not a script death.

## 3. What the delay is made of

The ~15.05 s is exactly the runner's own guard window plus the raise
propagation, and the stall released only when the runner itself wrote
to the game's stdin again (the failure-path save). Two consumer-side
facts pin this:

- `VideoDriver_Dedicated::MainLoop` ("dedicated" video driver,
  `--headless` runs `videodriver="dedicated"`, `src/openttd.cpp` case
  'D') calls `DedicatedHandleKeyInput()` once per iteration:
  `if (!InputWaiting()) return;` — `InputWaiting()` is a `select()` on
  raw fd 0 with a 1 µs budget — and only then a single
  `std::getline(std::cin, ...)` executed via `IConsoleCmdExec`
  (`src/video/dedicated_v.cpp`, UNIX branch).
- `std::getline` underflows `std::cin`'s streambuf with one `read(2)`
  that can consume more than one queued line and leftovers stay in the
  C++ streambuf, which `select()` cannot see; the loop keeps rolling
  (paused fast-path `StateGameLoop`, network band, 30 Hz cadence:
  `GetGameInterval()` returns `MILLISECONDS_PER_TICK` when
  `_pause_mode.Any()`) while the leftover command never execs — until
  new bytes arrive on fd 0 and the next `getline` drains the buffered
  line first.

Best-fit mechanism for the sealed facts (cannot be proven further
from the sealed bytes alone — `frames.json` has no per-frame
timestamps, and no side channel shows the game's iteration pace):

1. `console()` is fire-and-forget: two writes back-to-back
   (`unpause` at ≈.66, `save` at ≈.84) with no echo acknowledgement
   (`road_mutation.console` writes and flushes only).
2. One loop-iteration `read(2)` consumed both lines; `getline`
   executed `unpause` and left `save …/qualified` in the streambuf;
   `select()` went blind on an empty pipe for the following ~450
   iterations (~15.02 s).
3. The guard fired at 23:03:02.86; the failure-path write ≈23:03:02.9
   made fd 0 readable; the buffered line was then first in line for
   `getline`, so the qualified save executed 23:03:02.93.something,
   followed immediately by the failure save — matching `stdout.log`
   order (`unpaused` → `Saving map...` → saved(Q) → saved(F)) and the
   mtimes exactly.

Attempt-4's sealed record shows the same run had three clean
`pause`/`unpause` pairs and even an `unpause` → `save(failure)`
adjacency with no stall — the same class, no loss. So the pairing is
a race (write/iteration phasing decides whether one read() gets one
line or two), not a deterministic poison, and attempt 5 hit the loss
side on its first `unpause → save(qualified)` adjacency. The
paused-capture exit path (`paused_world_clock` finally-`unpause`
immediately followed by the per-cycle `save`) is the adjacency that
makes this fail window live in the chain of record.

## 4. Classification

- NOT a game-performance/IO-load artifact: saves run ≈0.3 s; the
  release is exactly our own third write, not wall-clock decay.
- NOT the E156 month gate or any month-pacing logic: capture and the
  preflight completed; dates inside the month; the guard that typed
  the failure is the pre-existing `road_mutation.save` marker guard.
- The defect class: runner-console synchronization gap
  (fire-and-forget `console()`, no per-command execution
  acknowledgement) × OpenTTD dedicated stdin consumption
  (select-gated `getline` can leave a queued line in the C++
  streambuf invisible to `select()`). Trigger: the remove-capture
  `unpause → save` adjacency introduced by the paused-capture exit
  path. First lossy incidence: Attempt 5. Observable consequence:
  a runnable save typed as a guard timeout and the attempt terminal.
- Root-cause status: mechanism evidenced to the OpenTTD source line
  level and consistent with every sealed byte; the exact
  one-read-two-lines-vs-three-lines-queued bookkeeping at
  23:03:02.85-03.2 is not distinguishable from the record — the
  remediation below closes the class without needing that last detail.

## 5. Smallest safe remediation (proposal — no code changed here)

Serialize console commands with an execution acknowledgement; the
single adjacency is the `paused_world_clock` exit seam:

1. New helper in `road_mutation.py` beside `console()`/`save()`:
   `console_ack(backend, prepared, command, marker, *, timeout=10)` —
   writes the command, then polls the fresh tails of
   `prepared.spec.stdout_path`/`stderr_path` (same offset machinery as
   `save()`) for `marker` in the window after the offsets; on expiry
   raise a typed `TimeoutError("console echo acknowledgement missing")`
   (never retried).
2. `paused_world_clock(backend, prepared, *, diagnostic=None)`: on
   entry `console_ack(..., "pause", "Game paused (manual)")`; in the
   `finally` `console_ack(..., "unpause", "Game unpaused (manual)")`.
   Substring markers (the console prefixes `*** \u2011` style lines);
   keep `diagnostic["pause_pairs"]` accounting. The handshake
   guarantees at most one un-acked console line in flight, so a
   following `save()` can never be swallowed behind an unresolved
   line — the failure class closes without touching `save()` at all.
3. Callers pass the cycle `prepared` (single call site,
   `freight_native_network.py:375-390`).

Non-goals: no change to `save()`'s guard, no replay of the sealed
attempt, no new native authorization for this remediation; native
proof is a fresh operator grant.

## 6. Regression tests (sketch, offline)

In the offline capture suite (`tests/test_capture_scheduling.py`
family, stub backend with a scripted log/marker pump):

- T1 handshake ordering: with a fake backend whose scripted stdin
  consumer delays echoes, `paused_world_clock` does not release until
  the pause echo is present; the `finally` awaits the unpause echo
  before its context exits — assert the echo markers and the call
  order (`pause`, capture read set, `unpause`).
- T2 typed timeout: scripted pump never delivers `unpause` echo →
  `console_ack` raises the typed `TimeoutError` at `timeout`, and the
  typed name is quoted in the diagnostic (`pause_resume_error`
  equivalent), never retried.
- T3 no-unacked-in-flight invariant: a small helper test asserting
  every `console()` issuer in the proof/ loop modules goes through
  either `save()` or `console_ack` (AST walk over
  `app/simulation/openttd/`, `app/`: `console(` call sites outside
  `road_mutation.save`/`console_ack` are a failure).
- T4 adjacency red-green: simulate the attempt-5 shape (echo of
  `unpause` delivered on the same read that swallows the next line)
  with the old `console()` path and the new handshake: the old path
  loses the `save` line (documented loss), the new one waits and
  then issues `save` only after the echo — the test locks the
  guarantee the run actually needed.

## 7. Evidence list

- Sealed attempt-5 dir `artifacts/demos/playable-demo-48abc4b955c14e0fadea7730cd487d86`
  (`result.json`, `CLAIM.json`, `cleanup.json`, `frames.json`,
  `stdout.log`, `stderr.log`, `planning-diagnostic.json`,
  `loop-cycle-1/*` mtimes, `qualified.sav` digest above).
- Attempt-4 sealed dir
  `artifacts/demos/playable-demo-da185e2c41dd45278e4152dcd7521af8`
  (`stdout.log` pair sequence, `result.json` typed error).
- OpenTTD 15.3 source (tag `15.3`): `src/video/dedicated_v.cpp`
  (`DedicatedHandleKeyInput`, `InputWaiting`, `MainLoop`),
  `src/video/video_driver.cpp` / `video_driver.hpp`
  (`GameLoop` tick interval, pause fast path, `SleepTillNextTick`),
  `src/openttd.cpp` (dedicated driver selection for `-D`/headless).
- Runner-side: `app/simulation/openttd/proof/road_mutation.py`
  (`console`, `owned_save_path`, `save`), `freight_native_network.py`
  (`paused_world_clock`, capture loop, `save` call), `proof/freight_delivery.py`
  (failure handler, cleanup).
