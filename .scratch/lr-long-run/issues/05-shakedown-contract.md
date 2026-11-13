# 05 — Shakedown contract of record

Type: wayfinder:grilling (HITL)
Blocked by: 01 (controller state machine), 04 (budget schema)

## Question

Decide the LR shakedown attempt's contract of record as reviewable design
criteria (not code) — the first native LR attempt (native ×1 of the D13
ceiling), carrying the operator's Q16 correction verbatim.

The decision must fix, as reviewable criteria:

1. The command-of-record shape (identity family `lr-shakedown-*`, ≤900 s
   proposed bound, fresh 256×256 world at product defaults with an
   operator-selected never-consumed seed) — frozen only at the LR
   commands-freeze milestone.
2. The two terminal outcomes and their exact criteria:
   - `LIFECYCLE_PROVEN`: a **genuine** post-cycle-0 closed-loop planning cycle
     completes — trigger fired from observed signals only, plan/execute/verify
     receipts retained, offline replay rc 0, verified checkpoints taken at
     genuine verified-cycle boundaries (≥2 **only if** ≥2 genuine boundaries
     occurred within the window).
   - `LIFECYCLE_PARTIAL`: cycle 0, observation, trigger evaluation, journal,
     incremental manifest, and clean wall-clock termination complete, but no
     planning cycle occurred because no legitimate trigger fired.
3. The anti-manufacturing rules (operator's correction, verbatim): the
   shakedown never manufactures a trigger or a checkpoint to satisfy its own
   acceptance criteria; `LIFECYCLE_PARTIAL` is never represented as
   closed-loop proof — planning capability stays UNKNOWN until a genuine
   planning cycle is verified.
4. What the shakedown does NOT prove: native recovery (stays UNKNOWN until a
   real recovery round needs it — risk-register item), LR-depth packet
   behavior beyond the window, any bar beyond its own window.
5. The gate chain of record: staging approval → independent review → Gate C
   signing → separate explicit launch approval, each its own in-session
   operator decision; one launch; no retry/reconnect; certified cleanup; stop
   on first unexpected failure; the consumed grant void for reuse.

Constraints: design-only; no code; no staging/signing/launch now; the shakedown
authorizes nothing by existing.
