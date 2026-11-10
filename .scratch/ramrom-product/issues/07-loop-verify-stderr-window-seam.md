# 07 — Loop verify stderr-window seam (Attempt-6 verify refusal class)

Type: defect
Status: implemented offline (E158; fix + regressions committed `5118f8c`
2026-11-11; the sealed Attempt 6 now verifies read-only end to end; no
native run needed, no operator grant consumed)
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

- [x] Red-first offline regression reproduces the exact Attempt-6 mismatch
  shape and then passes green under the chosen contract for both cycles
  (`verified_loop_cycles` with the recorded `ZERO_SERVICE` terminal each).
- [x] `verify_loop_receipt` on Attempt 6 runs read-only and returns the
  recorded truth; the run dir bytes stay identical (root manifest and
  `result.json` re-hashed byte-equal before/after the verify run).
- [x] Touched files stay ruff/format/py_compile/ty/diff-check clean; the
  targeted set of record is 151 passed / 0 failed (144 prior + 7 new).
- [x] No relabel of `result.json` (`NATIVE_LOOP_ZERO_SERVICES` stays the
  terminal of record), no evidence regeneration, no native run needed.

## Implementation record (E158, commit `5118f8c`)

- Recording contract: `collect_qualified_world` now self-writes
  `qualification-log-window.json`
  (`{"schema": "qualification-stderr-window-v1", "start": <bytes>}`) at the
  window claim, so future always recordings carry their own cut origin; the
  run-path copy set and manifests are unchanged (the file is a chain
  self-write, like `qualification-prefix-frames.json`).
- Replay contract (`freight_planning_replay.py`): the retained log vs
  recorded digest cut now starts at the recorded window when present; for
  recordings made before the record existed (Attempt 6 of record) the origin
  is derived by line-boundary digest anchoring — exactly one cut origin
  must match the smallest recorded slice, after which EVERY recorded digest
  is re-verified against that cut. Zero matches keep the verbatim
  `ValueError: qualification log prefix digest mismatch`; multiple matches
  raise the new typed
  `ValueError: qualification log prefix window start ambiguous`.
  Pre-window whole-file recordings (E153-era shape) derive 0 and keep the
  exact legacy byte semantics.
- Zero-service recordings (second seam found during this fix): the run
  raises at `network_from_facts` before writing
  `prepared-source-links.json`/`planning-policy.json`, so
  `_replay_network_world` gains `zero_service=True` (only
  `verify_loop_zero_service_cycle` calls it): links derive from the retained
  `native-save-correspondence.json` with save digests pinned against
  `sha256` of the retained `.sav` files and the replayed world's own
  digests; policy derives from the seal metadata and the function's
  existing per-field checks still validate it. Delivery-path replays are
  untouched (`zero_service` defaults False).
- Root scope accounting: `verify_loop_receipt` compares parked totals with
  `result.get(key, 0)` — zero-service roots legitimately lack
  `supplemental_requests`/`qualification_requests` because the planning
  refusal unwinds before `execute_network` updates them
  (`freight_native_network.py:1050`); the cycle-side sum already defaulted
  to 0 and is unchanged.
- Attempt 6 windows of record (derived, then crypt-confirmed by all 516
  recorded digests): cycle-1 `7549`, cycle-2 `168958`; no byte was modified
  or regenerated anywhere.
