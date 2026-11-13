# 01 — Controller loop architecture and state machine

Type: wayfinder:grilling (HITL)
Blocked by: nothing

## Question

Decide the LR controller's loop architecture and state machine as reviewable
design criteria (not code), so every later LR ticket and the eventual
implementation hang off one settled shape.

The decision must fix, as reviewable criteria:

1. The cycle state machine of record: OBSERVE → TRIGGER_EVAL →
   [PLAN → EXECUTE → VERIFY] → CHECKPOINT → next | terminal — including the
   exact transitions for typed per-cycle outcomes (`ZERO_CANDIDATES`,
   `BUDGET_REFUSED`, `WINDOW_REFUSED`) and each run terminal
   (`WALL_CLOCK_ELAPSED`, `ENDED_BY_OPERATOR`, `UNEXPECTED_FAILURE`,
   `CYCLE_BUDGET_EXHAUSTED`).
2. The wall-clock anchor and enforcement: deadline measured from the owned
   process spawn instant, typed into the journal as t0; how remaining-pause
   budget and remaining wall-clock interact at every trigger evaluation.
3. The pause/pacing seams: where the world clock pauses and resumes (the
   `paused_world_clock` decision of record), and the rule that every console
   save rides the `console_ack` echo handshake (ticket-06 fix, E157).
4. The per-cycle request-id namespace design at LR depth (the E155
   `cycle_request_id` fix extended) and the exchange-budget accounting per
   cycle.
5. Reuse boundaries: which existing machinery the controller composes
   (`run_loops`/`loop_gate` shapes, per-cycle recordings, owned cleanup,
   soft-end typing) versus what is new — and the guarantee that no existing
   loop/corridor/canonical identity is re-scoped.

Constraints: design-only; no code; no native authority; every consumed
identity stays consumed; the 2 h envelope is never exceeded by design; the
loop's `abandoned_world` K=2 fence is NOT carried into LR.
