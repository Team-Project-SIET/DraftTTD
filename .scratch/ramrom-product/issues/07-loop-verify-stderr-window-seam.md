# 07 — Loop verify stderr-window seam (Attempt-6 verify refusal class)

Type: defect
Status: open (localized read-only against the sealed Attempt-6 bytes
2026-11-11; fix is an offline code change; the sealed run bytes are never
touched; re-running raw `verify` against the sealed dir after the fix is
read-only and needs no operator grant)
Blocked by: 05's seal discipline (no evidence regeneration; no relabel)

## Question

`verify_loop_receipt` (the loop-attempt `verify` CLI entry of record,
`.venv/bin/python -m app.simulation.openttd.proof.freight_delivery verify
<run-dir>`) refused Attempt 6 typed rc=1 at the first cycle's retained
qualification replay: `ValueError: qualification log prefix digest
mismatch` (`freight_planning_replay.py:157`).

Decisive digests from the sealed bytes
(`artifacts/demos/playable-demo-0751d73c44054941bd77f05300b6c1a5`):
all 263 recorded prefix entries in `loop-cycle-1/` and all 253 in
`loop-cycle-2/` mismatch; each cycle's `stderr.log` is byte-identical to
the root per-attempt shared stderr (324,124 bytes,
sha256 `4e64bf7aaf5dd6351470246f50a206d5287efc0910ec41990cad7a967c887a26`).

Mechanism (three commits' contracts, all read-only confirmed):

- Live recording: `collect_qualified_world` claims one shared per-attempt
  stderr per session (`backend.stderr_window = stderr_path.stat().st_size`,
  `freight_runtime_planning.py:212`) and records
  `bytes = len(raw_log), sha256 = sha256(raw_log)` per request
  (`:249-261`) — window-RELATIVE segments.
- Per-cycle staging: loop finalization copies the FULL root
  `stdout.log`/`stderr.log` into every `loop-cycle-N`
  (`freight_delivery.py:2080`).
- Retained replay: `replay_qualified_world` computes
  `sha256(stderr.log[:size])` from byte ZERO against each recorded
  window-relative digest (`freight_planning_replay.py:146-162`), and the
  replay backend's `stderr_window` is unset (default 0).

So for any loop cycle whose qualification session begins after prior
stderr content — every loop cycle (generation + prior-cycle markers) —
every entry mismatches: the staging copy contract (full shared log) and
the replay cut contract (from byte 0 against window-relative digests)
can never agree. The harness at the replay is launch-free by construction
(`backend.process = object()`, opaque ownership handles
`freight_planning_replay.py:112-114`), so this defect touches only the
independent verify instrument, never the run path.

Offline gap: the 9 loop-verify tests of record (E144) stop at prologue
refusals (`tests/test_freight_loops.py` `staged_loop_root` has no cycle
recordings); none exercised the retained-replay digest seam, so the
mismatch was never reproduced offline before Attempt 6.

## Scope

- Decide the recording contract of record and make the two sides agree,
  one way, with a red-first regression against the sealed Attempt-6
  digest fixtures:
  (a) keep the full-log staging copy and make the replay cut
  window-relative (the per-cycle stderr window offset must then be
  recorded at staging time, e.g. in `loop-cycle.json` alongside
  `frames_start` — NOT recomputed from bytes, or the seal discipline
  weakens), or
  (b) keep the window-relative recorded digests and stage a window-cut
  per-cycle `stderr.log` instead of the full shared copy (root keeps the
  full log for root-level reads).
- Do not modify any sealed run bytes; do not alter the recording writer's
  digest semantics (item (b) would need the writer unchanged and only the
  finalization copy changed; item (a) needs a marker field added).
- Loop `verify` prologue checks already passed on Attempt 6 (root
  manifest, PRELAUNCH seal, CLAIM, marker frames, cleanup, terminal
  status) — the fix must not gate those again.

## Acceptance

- Red-first offline regression reproduces the exact Attempt-6 mismatch
  shape from the sealed digest fixtures, then passes green under the
  chosen contract for both cycles (`verified_loop_cycles` with
  `ZERO_SERVICE_REPLAYED` for each).
- `verify_loop_receipt` on Attempt 6 in its final form runs read-only and
  returns whatever the chosen contract says is the truth — the run dir
  bytes stay identical (root manifest unchanged).
- Touched files stay ruff/format/py_compile/ty/diff-check clean; focused
  loop-verify plus qualification suites green.
- No relabel of `result.json` (`NATIVE_LOOP_ZERO_SERVICES` stays the
  terminal of record), no evidence regeneration, no native run needed.
