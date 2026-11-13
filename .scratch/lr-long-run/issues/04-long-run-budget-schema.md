# 04 — long-run-prelaunch-v1 budget arithmetic

Type: wayfinder:grilling (HITL)
Blocked by: 01 (controller state machine)

## Question

Decide the `long-run-prelaunch-v1` sealed budget schema's arithmetic as
reviewable design criteria (not code) — the LR successor of the loop's sealed
budget family (E146: requests 87→174, mutations 33→66, supplemental
33,345→66,690, total_seconds 1200→2400, construction_commands 192→384 for
`--cycles 2`).

The decision must fix, as reviewable criteria:

1. The schema's fields of record: per-cycle request/mutation/construction/
   observation caps, the total-pause budget (`max_total_paused_seconds = 2400`,
   D11), `max_planning_cycles = 8` (D11), the wall-clock budget (7200 s full /
   ≤900 s shakedown, proposed), and deadline/typed-exhaustion lines.
2. The linear-in-cycles derivation method of record, computed from **observed**
   single-cycle costs of record (qualification ~260 requests; capture
   832–1372 exchange pairs; build ops from the loop's scaled seals) — with
   every derivation labeled OBSERVED-basis or PROPOSED, and a hard ceiling per
   field with typed `*_BUDGET_EXHAUSTED`/`*_REFUSED` outcomes (never silent
   overruns).
3. Versioning and identity separation: `long-run-prelaunch-v1` is a new seal
   family — loop/corridor/canonical seals stay byte-equal; no retained record
   is reinterpreted.
4. The per-cycle request-id namespace's budget interaction (E155 fix
   extended): uniqueness guarantees across ≥8 cycles + monthly ticks, and the
   512-byte reply bound + per-request wire trust anchor carried unchanged.
5. The offline validation plan for the proposed per-cycle pause cost (3–6 min)
   and the derived in-game expectation band (~3.5–7 years) — what must be
   measured offline before any native round, and that bands are recomputed,
   never asserted.

Constraints: design-only; no code; no native authority; proposed values stay
proposals until offline validation; budgets seal at prepare, never at runtime.
