# Phase D scope — wayfinder map

Label: wayfinder:map (local-markdown tracker; per-ticket journals in `issues/`).
Status: CHARTED 2026-11-12, during the Stage-1/Stage-2 scope-definition session.
This map is a planning artifact: it authorizes no launch, no connection, no
staging, no signing, no claim, no evidence mutation and no commit. Nothing is
implemented from it until the operator approves the scope proposal of record
([docs/phase-d-scope-proposal-2026-11-12.md](../../docs/phase-d-scope-proposal-2026-11-12.md)).

## Destination

An approved Phase D under the operator-defined headings "Closed-Loop
Optimization" + "Productization": the ramrom seed-loop line is the backbone,
carried to **≥1 verified native plan + delivery cycle on a random world** (the
honestly-unmet bar of record, pursued by new means on fresh seed identities),
plus the delivered-class/E36 round, the rail offline build, offline per-cycle
economics, and the regression quality floor — every native round through the
four operator gates, every terminal honestly typed, nothing relabeled.

## Notes

- Domain vocabulary and status classes (VERIFIED/PROVEN/PREPARED/PARTIAL/
  FAILED/UNKNOWN, consumed, sealed) mean exactly what `AI_HANDOFF.md` defines.
- Standing fences inherited unchanged: `artifacts/` immutable, transfer-only,
  never regenerated; consumed attempts stay consumed; native runs operator-gated
  (staging → independent review → Gate C signing → launch, in-session), one
  launch, no retry/reconnect; certified cleanup; stop on first unexpected
  failure.
- `CONTEXT.md` is byte-pinned and prepend-only: new Phase D terms live in the
  proposal's vocabulary section, never edited into `CONTEXT.md`.
- Every file this effort creates is uncommitted; any commit is its own
  DG-10-style operator decision.
- Skills for grilling-type tickets: call the Skill tool twice, for "grilling"
  and "domain-modeling". Research tickets resolve against local sources only
  (`ottd/src/script/api/`, `OpenTTD-Knowledge/`, retained evidence); no web
  claims without a local anchor.
- Native budget of record: 4–8 one-shots, pre-allocated 3 (backbone battery) +
  2 (delivered class) + 1 (GUI capstone) + 2 operator-held reserve. The count
  is a ceiling, not a promise; every round keeps its own four approvals.
- Spec of record published 2026-11-12 via to-spec:
  [docs/specs/phase-d-scope.md](../../docs/specs/phase-d-scope.md) —
  whole-phase spec, `Status: ready-for-agent` scoped to offline work after M0
  approval and resolved governing decision tickets; existing testing seams
  only (offline CLI of record, wire/package triads, sealed budgets, typed
  refusals, P07 replay, full-suite gate). It grants no native authority and
  no commit.
- Implementation tickets published 2026-11-12 via to-tickets:
  `issues/09…29` (tracer-bullet slices in dependency order, blocked by the
  decision tickets 01–08). 09–23 are `ready-for-agent` (offline, M0-gated);
  24–29 are the native one-shot rounds as `ready-for-human` tickets carrying
  the four-gate chain; the operator reserve (×2) stays unticketed.
- **M0 granted 2026-11-12** (operator, in-session): proposal APPROVED; the
  offline implementation frontier is open per the ticket graph. Native gates
  (24–29), staging, signing, launch, and every commit stay separate operator
  decisions. Ticket 09 (E207 triage dossier) claimed — diagnosis only,
  main tree (retained `artifacts/` evidence is not present in fresh
  worktrees).

## Decisions so far

(The Stage-1 interview settled these with the operator; the full question-and-
answer record is the proposal's §2. One line each, zoom the proposal for detail.)

- [§2 D1–D8](../../docs/phase-d-scope-proposal-2026-11-12.md): workstreams in scope = WS1 World&Terrain, WS3 Closed-Loop, WS4 Rail (offline only), WS5 Economics, E36 delivered-class as its own workstream; WS2 concurrency and WS6 full productization excluded; ramrom loop is the backbone; DoD = offline bar + native proof on the core; native appetite 4–8 one-shots; deliverable = uncommitted docs file + this map.
- [§2 D9–D17](../../docs/phase-d-scope-proposal-2026-11-12.md): WS1 delivers the current bounded profile only (no slopes/bridges/>256/>32 industries); observation window becomes distance-scaled v2 (fresh operator decision per E206, now taken); "Closed-Loop Optimization" = operation loop + typed, opt-in, evidence-gated feedback (never automatic); economics = offline per-cycle P&L from receipts with UNKNOWN preserved; GUI-bearing probe is the capstone one-shot; quality floor gates the first native round; Productization = minimal release discipline.
- [§2 D18–D19](../../docs/phase-d-scope-proposal-2026-11-12.md): native split 3+2+1+2; backbone battery = three named fresh seeds (proposed 11/12/13, never-consumed verified at grant time), each run its own grant.
- [Rail script-API surface study](research/01-rail-api-surface-study.md) (ticket 04, resolved 2026-11-12): the 15.3 GS API provides the full rail build surface and GS-side orders since 14.0; five hard gaps (no block-occupancy readback, no slope→track oracle, no curve-limit API, base-price-only quoting, precondition aborts); `GSRail` appears in the repo only as a forbidden symbol in the observe-only bridge gate (`proof/harness.py:320`) — rail is a new additive package composition, never an edit of frozen road packages. Ticket 08 graduates from its §5.
- [Spec of record](../../docs/specs/phase-d-scope.md) (2026-11-12): Phase D synthesized into the spec template (problem/solution/31 user stories/implementation + testing decisions/out-of-scope/notes) from proposal D1–D19; operator confirmed whole-phase coverage and existing-seams-only testing. Still gated by M0 proposal approval.
- [E207 triage dossier](research/02-e207-triage-dossier.md) (ticket 09, resolved 2026-11-12): per-class mechanisms proven with file:line + commit-dating — P08 ×51 fixture byte-serialization drift at `bf6cc0b` (repair; legacy "schema/policy digest drift" refuted); budget ×3 stale 512-era seals after the intentional 2048 widening at `5e398db` (repair; extras **ANSWERED: pre-existing since 2026-11-07**); workspace-retention ×1 endpoint-closure flake (operator choice: seal or narrow repair; extras answered in part); corridor ×1 ladder composition drift (repair-or-seal; the description conflict closed — the ladder test is the red of record); structural-world ×1 re-indent without re-seal (repair). Feeds decision ticket 07.
- **Ticket 07 resolved** (2026-11-12, operator): **repair ×4, typed seal ×1** — P08 serialization restore; budget seals to the 2048-era constants (410/208,280, literals pinned); corridor ladder re-key; structural-world serialization restore; workspace-retention sealed with its flake mechanism as the typed reason. Execution = ticket 10; the full-suite re-run gate = ticket 11.
- **Ticket 10 resolved** (2026-11-12): dispositions executed — 12 files uncommitted; per-class suites green (P08 e2e 62; budget trio 16+10+8; corridor VM 11; structural-world 65; qualification 59 passed + 1 sealed skip, `[integrity]` live); ruff clean; no new failures. M1 exit = ticket 11.
- **Ticket 11 resolved — M1 exit passed** (2026-11-12): full-suite re-run **green** — 6327 passed / 55 skipped / 0 failed, exit 0 (fresh run; E207 unrelabelled). Full-suite command of record + release discipline + three-point gate cadence frozen into `REPRODUCE.md` (2026-11-12 addendum). Quality floor passed; native rounds remain gated by M2 (tickets 12–15) and decision tickets 01/02/03.

## Not yet specified

- Exact observation-window v2 formula, versioned budget-field shape, byte-compat
  rule for v1 identities, and the extreme-distance behavior — ticket 01.
- Capture-scheduler capacity-policy redesign (the seed-8 `CAPTURE_SCHEDULE_
  EMPTY` class) — ticket 02.
- Census-integration protocol surface for per-world tile classification in the
  loop capture (fusion gate stays CLOSED) — ticket 03, blocked by 01.
- Rail offline-build contract shape (wire-protocol number allocation, package
  family, proof pipeline) — graduated: now ticket 08, sharpened by the
  resolved ticket-04 study.
- Delivered-class fix design — graduates after the diagnosis gate (ticket 05).
- Typed-feedback parameter/policy surface — ticket 06; its evidence inputs
  exist only after the backbone's first verified cycle.
- Per-class repair-vs-seal dispositions for the E207 reds — ticket 07.
- Battery commands-of-record freeze (graduates after tickets 01+02 land).
- WS5 receipt-shape audit (graduates after ≥1 verified backbone cycle exists).
- Full-suite gate cadence during Phase D (re-run after which landings?).

## Out of scope

- WS2 Advanced Logistics Network (concurrency, shared-asset reuse, concurrent
  payment windows): excluded by the operator (Round 1). The record's UNKNOWNs
  (README :133, :802-803) stay UNKNOWN; no contract work is planned.
- New world capabilities — arbitrary slopes/obstructed clearing as executable
  construction, bridges/tunnels, >256×256 maps, >32 industries (Round 2).
  These stay "outside the demonstrated MVP" (README :174).
- Rail native construction or delivery (Round 2: offline build only).
- Full automatic optimization (P07→P05 parameters changing automatically) —
  crosses the honesty boundary at README :853-855; the typed-feedback path is
  opt-in and evidence-gated instead.
- Full productization (packaging, CI, ops runbooks) — Round 2 kept only minimal
  release discipline.
- The "Final Release" heading (Round 1 mapping: stays undefined).
- Re-running, re-signing or relabeling any consumed identity; regenerating
  retained evidence; any implementation before the proposal is approved.
