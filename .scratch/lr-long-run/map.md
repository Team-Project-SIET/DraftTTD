# LR long-run closed-loop experiment — wayfinder map

Label: wayfinder:map (local-markdown tracker; per-ticket journals in `issues/`).
Status: CHARTED 2026-11-13, during the LR Stage-1/Stage-2 design session.
This map is a planning artifact: it authorizes no launch, no connection, no
staging, no signing, no claim, no evidence mutation and no commit. Nothing is
implemented from it until the operator approves the scope proposal of record
([docs/lr-long-run-scope-proposal-2026-11-13.md](../../docs/lr-long-run-scope-proposal-2026-11-13.md)).

## Destination

An approved LR effort: a persistent two-hour closed-loop simulation experiment —
fresh 256×256 random world, normal speed, wall-clock primary, in-game years a
measured outcome — in which the Python logistics system repeatedly observes,
plans, executes bounded expand-only operations, verifies, and feeds verified
actuals into subsequent cycles, with a complete machine-verifiable history
(append-only journal, per-cycle receipts, incremental manifests, final report,
replay). Every native attempt through the four operator gates; every terminal
honestly typed; nothing relabeled. Working name LR; formal successor naming is a
later operator decision.

## Notes

- Vocabulary and status classes (VERIFIED/PROVEN/PREPARED/PARTIAL/FAILED/
  UNKNOWN, consumed, sealed) mean exactly what `AI_HANDOFF.md` defines. New LR
  terms live in the proposal's §3 vocabulary section — `CONTEXT.md` is
  byte-pinned and prepend-only, never edited here.
- Decisions of record: the Stage-1 grilling settled D1–D21 with the operator
  (2026-11-13); the question-and-answer record is the session transcript and
  the proposal's §2 is the decision table. Per-ticket decisions append below
  as tickets close.
- Standing fences inherited unchanged: `artifacts/` immutable, transfer-only,
  never regenerated; consumed attempts stay consumed; native runs operator-gated
  (staging → independent review → Gate C signing → launch, in-session), one
  launch, no retry/reconnect; certified cleanup; stop on first unexpected
  failure.
- LR native ceiling 5 (D13), serial, each its own four-gate ceremony, completely
  separate from Phase D's native budget; ceiling ≠ authorization.
- Hard implementation gate: Phase D M2 (tickets 12–15) must land before LR
  implementation; Phase D battery outcomes inform the risk register only (D20).
- No Phase D ticket (01–29) is re-scoped, reopened, or duplicated; E36 stays
  OPEN and FD-C-2 stays `INCOMPLETE_EVIDENCE`; Phase A–C records and UNKNOWNs
  are preserved.
- Every file this effort creates is uncommitted; any commit is its own
  operator decision.
- Skills for grilling-type tickets: call the Skill tool twice, for "grilling"
  and "domain-modeling". Proposed parameters (per-cycle pause 3–6 min,
  cooldown K, thresholds, bands, shakedown bound) are proposals pending offline
  validation — never acceptance criteria, never silently promoted to facts.
- Selecting closed-loop mode authorizes nothing autonomically.

## Decisions so far

(The Stage-1 interview settled these with the operator; the full
question-and-answer record is the proposal's §2. Per-ticket decisions append
as tickets close.)

- [§2 D1–D21](../../docs/lr-long-run-scope-proposal-2026-11-13.md): wall-clock
  primary, recovery rounds, expand-only bounded cycles, event-driven cadence,
  verified-boundary checkpoints, append-only evidence architecture, successor
  charter, `long-run-prelaunch-v1` schema, fresh-world cycle 0, qualify-once +
  typed staleness events, planning caps (8 cycles / 2400 s paused), typed
  per-cycle outcomes with the four-run-terminal taxonomy, native ceiling 5,
  aggregate-only OPEX, digest-only in-run checkpoint binding, shakedown
  `LIFECYCLE_PROVEN`/`LIFECYCLE_PARTIAL` (never manufactured), verified-cycle
  definition, proven-fact monthly observation set, trigger set T1–T6,
  Phase-D-M2 hard gate, carried corrections (Ctrl-C soft end, recovery rewind,
  2 h envelope).

## Not yet specified

- Controller loop architecture and state machine — ticket 01.
- Journal schema and event taxonomy — ticket 02.
- Incremental manifest design and the LR verify command of record — ticket 03.
- `long-run-prelaunch-v1` budget arithmetic (linear-in-cycles derivation from
  observed single-cycle costs; caps; typed exhaustion) — ticket 04.
- Shakedown contract of record, including the `LIFECYCLE_PROVEN` /
  `LIFECYCLE_PARTIAL` criteria and what the shakedown may never manufacture —
  ticket 05.
- Recovery package design (identity binding to checkpoint + journal cursor;
  rewind-consistency checks) — ticket 06.
- Final report schema and P07 integration — ticket 07.
- Offline acceptance bar and milestone ladder for LR implementation — ticket 08.
- Threshold-validation method for the trigger set (backlog threshold, cooldown
  K) — graduates after ticket 08, consuming M2-landed machinery and retained
  battery fixtures.
- Battery-outcome risk-register amendments — graduate as Phase D tickets 24–26
  resolve.
- LR commands-of-record freeze — graduates after tickets 05+08 and the M2 gate.
- Native pacing/packet-budget behavior at LR depth — graduates from shakedown
  evidence.
- Implementation-ticket publication — graduates only on operator approval of
  the proposal (the Phase D pattern: decision tickets now, implementation
  tickets later).
- Unused-allocation disposition for the ×2 recovery rounds and the optional
  second full attempt — graduates from run outcomes (the ticket-28
  honestly-not-needed pattern).

## Out of scope

- WS2 Advanced Logistics Network (concurrency, shared-asset reuse, concurrent
  payment windows) — stays excluded (Phase D operator decision).
- New world capabilities — slopes/obstructed clearing as executable
  construction, bridges/tunnels, >256×256 maps, >32 industries (README :174).
- Service teardown, vehicle retirement, unrestricted replanning.
- Automatic parameter change, retraining, any non-opt-in feedback.
- Binary patching or any game-speed modification; behavior beyond the 2 h
  envelope.
- Starting from Phase D battery checkpoints; battery worlds are Phase D's.
- PostgreSQL persistence in the LR demo path.
- Rail construction or delivery of any kind in LR.
- GUI window semantics in LR headless runs (the GUI capstone is Phase D's
  ticket 29).
- Formal successor naming ("Phase E") — a later operator decision.
- Re-running, re-signing or relabeling any consumed identity; regenerating
  retained evidence; any implementation before the proposal is approved.
