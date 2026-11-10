# 06 — Console echo handshake for pause/unpause (Attempt-5 save-stall class)

Type: task
Status: open (proposal of record; implementation pending review + fresh explicit operator grant for any native proof)
Blocked by: 05 (attempt-5 attempt path must stay sealed; no code may run natively for this)

## Question

Close the Attempt-5 failure class before any next native attempt:
`TimeoutError: owned native save completion missing` was typed at the
15 s marker guard because the runner's `console()` is fire-and-forget
and the game consumed the back-to-back `unpause` + `save` writes in a
way that left the `save` line unexecuted for the full guard window;
the buffered line then executed right after the failure-path save's
new stdin write. Full record:
`.scratch/ramrom-product/research/03-attempt5-save-stall-forensics.md`.

## Scope

- `road_mutation.py`: add `console_ack(backend, prepared, command, marker, *, timeout=10)` next to `console()` (same fresh-tail marker polling as `save()`; typed `TimeoutError("console echo acknowledgement missing")`, never retried).
- `freight_native_network.py`: `paused_world_clock` gains a `prepared` parameter and handshakes both commands — `console_ack(..., "pause", "Game paused (manual)")` on entry, `console_ack(..., "unpause", "Game unpaused (manual)")` in the `finally`; keep `diagnostic["pause_pairs"]`/`pause_resume_error` accounting. Single call site updated (375-390).
- `save()` itself stays untouched; no other `console()` call site exists on the attempt path.

## Acceptance

- Offline: T1-T4 regression tests of the research note pass (handshake ordering, typed timeout, no-unacked-in-flight AST invariant, adjacency red-green) plus the existing capture suites (43/43 focused suite status at `42bbe5f` as the baseline set).
- The touched modules stay ruff/py_compile/ty/diff-check clean.
- Native proof of the fix requires a fresh explicit operator grant; the sealed Attempt-5 record is never relabeled or retried.

## Status notes

- 2026-11-10: written from the attempt-5 forensics; attempt-5 stays FAILED/SEALED at `42bbe5f` (addendum 2, `AI_HANDOFF.md`).
