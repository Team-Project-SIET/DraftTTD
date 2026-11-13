# 02 — Journal schema and event taxonomy

Type: wayfinder:grilling (HITL)
Blocked by: 01 (controller state machine)

## Question

Decide the append-only LR journal's schema and event taxonomy as reviewable
design criteria (not code) — the evidence backbone every LR contract
(checkpoints, manifests, reports, replay) reads from.

The decision must fix, as reviewable criteria:

1. The event types of record and their minimal payloads: run-lifecycle events
   (t0/deadline/pause-resume/terminal), journal ticks (the monthly proven-fact
   set of D18), planning-cycle events (trigger evaluation result, plan digest,
   per-cycle budget lines), execution events (command receipts by reference,
   never by copy where a receipt file exists), verification events (replay
   verdicts), checkpoint events (save digest + cursor + receipt set).
2. Binding rules: how every event binds to its source receipt digest, how the
   journal cursor advances, and what makes a cursor position
   checkpoint-eligible (the D17 verified-cycle definition).
3. Schema versioning: the versioned journal header, forward-compatibility
   rules, and the guarantee that v1 loop/corridor recordings stay byte-equal
   (new identity family — nothing retained is reinterpreted).
4. Volume and honesty labels: every fact carries OBSERVED/DERIVED/UNKNOWN at
   write time; backlog stays a point-sample; no UNKNOWN is promoted to a
   number.
5. The offline test shape: contract tests over synthetic journals + retained
   receipt fixtures (never mutating sealed bytes).

Constraints: design-only; no code; PostgreSQL out; the journal is new
machinery — never presented as an extension of the finalize-at-end manifest
pattern it replaces for LR runs.
