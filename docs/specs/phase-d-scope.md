# Spec: Phase D — Closed-Loop Optimization + Productization

Spec of record for the wayfinder effort `.scratch/phase-d-scope/map.md`. It
synthesizes the approved-shape scope proposal
`docs/phase-d-scope-proposal-2026-11-12.md` (Stage-1 interview decisions
D1–D19 of record) into implementable form. **Status: ready-for-agent — for
offline work only, and only where the governing decision ticket under
`.scratch/phase-d-scope/issues/` is resolved.** Every native gate (staging,
independent review, Gate C signing, launch), every commit, and the M0 proposal
approval itself remain explicit in-session operator decisions. This spec
grants no launch, no AdminPort connection, no staging, no signing, no claim,
no retry of a consumed attempt, no evidence mutation, and no commit.

Vocabulary (VERIFIED / PROVEN / PREPARED / PARTIAL / FAILED / UNKNOWN,
consumed, sealed, one-shot) means exactly what `AI_HANDOFF.md` defines.
Phase D terms of record (Backbone, Quality floor, Observation window v2,
Typed feedback, Delivered class, Capstone) are defined in the proposal's
vocabulary section — `CONTEXT.md` stays byte-pinned and untouched.

## Problem Statement

Phase A–C are terminally closed (E127, E195, E202) and the program's headline
capability still does not exist anywhere in the evidence: **no verified native
plan + delivery cycle on a random world**. The Phase C battery was consumed
honestly and missed its bar (E198–E201); the corridor's delivered class
(`CARGOFLOW2_LOADED_NEVER_DELIVERED`) is twice-reproduced and undiagnosed
(E36 open by rule); the first full-suite baseline ever recorded (E207) shows
57 failing tests with no per-class disposition behind them, 4 of them of
unknown new-vs-pre-existing status; the three roadmap headings "Closed-Loop
Optimization", "Productization" and "Final Release" were undefined (E203);
no full-suite command of record exists in `REPRODUCE.md`; and rail has zero
code and zero evidence. The operator needs a governed Phase D that: gives the
random-world bar a fair attempt on fresh seed identities instead of consumed
ones; installs a regression quality floor before any native spend; grows rail
without native risk; derives economics only from retained receipts; and keeps
every terminal typed — all without relabeling, retrying, or regenerating a
single retained byte.

## Solution

Phase D exists under the two operator-defined headings **"Closed-Loop
Optimization"** and **"Productization"**; "Final Release" stays undefined
(D6). Its program backbone is the **ramrom seed-loop product**
(`docs/specs/ramrom-product.md`, whose operator clauses Q1–Q8 remain
constitution): the built-and-standing loop engine carried to its
honestly-unmet native bar on fresh seed identities. The destination bar of
record is **≥1 verified native plan + delivery cycle on a random world
without a `NO_FEASIBLE_SERVICES` terminal, every terminal honestly typed**,
pursued by six workstreams:

- **WS-D1 Advanced World & Terrain** — deliver the current bounded 256×256
  profile by removing the three named blockers (observation-window v2,
  capture-scheduler capacity, per-world census integration). No new world
  capability (D9, D10).
- **WS-D2 Closed-Loop Optimization** — the backbone battery: ×3 native
  one-shots on fresh seeds 11/12/13 (D18, D19), then the loop closes via
  typed, opt-in, evidence-gated feedback — never automatic (D11).
- **WS-D3 Delivered class / E36** — offline diagnosis to the E105/E111
  standard, one fix offline, then ×1 candidate round (+ ×1 corrective
  contingency); E36 closes only on actual DELIVERED receipts (D5).
- **WS-D4 Rail Logistics** — an offline build only: planning candidates, a
  rail wire contract (next free protocol numbers), a rail GameScript package
  family, orders/vehicle lifecycle, controlled tests. Zero native launches
  in Phase D (D12).
- **WS-D5 Long-Run Economics** — per-cycle P&L derived offline from the
  loop's retained receipts, OBSERVED/DERIVED/UNKNOWN-labeled, under a new
  identity (D13).
- **WS-D6 Productization** — minimal release discipline: the quality floor,
  the full-suite command of record in `REPRODUCE.md`, version/release notes.
  No packaging, no CI, no ops runbooks (D16).

Definition-of-Done shape: **offline bar + native proof on the core** (D4).
Native budget is a ledger, a ceiling not a promise: **backbone ×3 +
delivered-class ×2 + GUI capstone ×1 + operator-held reserve ×2 (≤8
one-shots)**, each round its own four-gate discipline (D3, D18). The quality
floor gates Phase D's first native round (D7, D15). AFK agents execute the
offline work; the operator alone gates native rounds and commits.

## User Stories

### Quality floor and productization (WS-D6)

1. As the operator, I want every E207 failing-test class dispositioned as
   repair-or-seal-with-typed-reason, so that no red stands unexplained before
   Phase D spends native budget.
2. As the operator, I want the four E207 extra reds' new-vs-pre-existing
   status resolved by evidence, so that the recorded UNKNOWN does not
   silently become an assumption.
3. As the operator, I want a full-suite re-run that is green or carries a
   typed disposition on every remaining red, so that the quality floor is a
   checkable gate, not a promise.
4. As the operator, I want the full-suite command of record written into
   `REPRODUCE.md` (none exists today), so that any future session reproduces
   the same baseline instead of inventing one.
5. As the operator, I want version and release-notes discipline in
   `REPRODUCE.md`, so that each round's identity and artifacts are traceable
   without packaging or CI overhead.
6. As an AFK agent, I want the quality floor defined as
   "green-or-honestly-triaged", so that I know when repair is required and
   when sealing with a typed reason is the honest outcome.

### World & terrain fixes (WS-D1)

7. As the operator, I want the observation window decided as a
   distance-scaled v2 carried in a versioned budget field sealed at prepare,
   so that seed-7-class expiries stop being design defaults and v1 records
   stay byte-equal (ticket 01).
8. As the operator, I want the capture-scheduler capacity policy redesigned
   so a seed-8-class relationship produces captured reads instead of an
   empty schedule, so that candidates are not lost to window arithmetic
   alone (ticket 02).
9. As the operator, I want pause-the-clock pacing and the month-pace gate
   preserved with their typed surfaces intact, so that the redesign cannot
   silently weaken natively proven pacing (four E150/E198/E199/E201
   proofs).
10. As the operator, I want per-world tile classification to ride the loop's
    capture path as an additive wire protocol — or an explicit decision not
    to integrate — so that P08 stops refusing on
    `INCOMPLETE_TILE_CLASSIFICATION` where classification could be observed
    (ticket 03; the fusion gate stays CLOSED).
11. As an AFK agent, I want v1 window and budget identities pinned by
    byte-compat tests, so that my v2 work can never reinterpret a retained
    record.
12. As the operator, I want Phase D to deliver the current bounded 256×256
    profile only, so that world-capability creep (slopes, bridges, larger
    maps, more industries) cannot consume the budget.

### Backbone battery (WS-D2)

13. As the operator, I want the ramrom loop engine carried to its native bar
    on three fresh never-consumed seeds (proposed 11/12/13, verified at grant
    time), so that the honestly-unmet Phase C bar gets a fair attempt by new
    means.
14. As the operator, I want each battery run staged, independently reviewed,
    Gate C signed, and separately launch-approved in-session, so that one
    explicit human decision stands behind every launch.
15. As the operator, I want typed terminals accepted as honest outcomes and
    never retried on the same identity, so that a failure is retained
    evidence, not waste.
16. As an AFK agent, I want the battery commands of record frozen and
    documented before the first grant, so that no run improvises its own
    invocation.
17. As the operator, I want per-cycle replay verification — the `verify`
    path returning rc 0 with every cycle independently verified from
    retained receipts — so that the loop's evidence is machine-checkable
    offline after each run.
18. As the operator, I want the two reserve one-shots held by me with no
    default claimant, so that a new halt class can be corrected without
    breaking the ceiling.

### Delivered class (WS-D3)

19. As the operator, I want the twice-reproduced
    `CARGOFLOW2_LOADED_NEVER_DELIVERED` terminal diagnosed over retained
    candidate bytes to the E105/E111 evidence standard, so that the fix is
    designed from a source-confirmed root cause, not a hypothesis (ticket 05).
20. As the operator, I want one fresh delivered-class candidate round plus a
    corrective contingency from the ×2 allocation, so that E36 gets its one
    honest closure attempt.
21. As the operator, I want E36 to close only when actual DELIVERED receipts
    exist, so that closure can never be a relabel — it stays open honestly
    otherwise.

### Rail (WS-D4)

22. As the operator, I want rail built offline only — candidates, wire
    contract, package family, orders/vehicle lifecycle, controlled tests —
    so that capability grows with zero native risk in Phase D.
23. As an AFK agent, I want the rail build to mirror the proven road-side
    pattern families (wire contract, package, staged pipeline) and never edit
    a frozen road package, so that additive composition stays provable.
24. As the operator, I want the five 15.3 API gaps (no block-occupancy
    readback, no slope→track oracle, no curve-limit API, base-price-only
    quoting, precondition aborts) carried as typed constraints, so that rail
    v1 refuses honestly what it cannot observe.

### Economics (WS-D5)

25. As the operator, I want per-cycle P&L (freight revenue, vehicle running
    cost, cash delta) derived offline from the loop's existing receipt
    shapes under a new identity, so that economics exist without consuming
    native budget.
26. As the evidence auditor, I want every P&L number labeled OBSERVED,
    DERIVED, or UNKNOWN with its source digest, so that no UNKNOWN is ever
    promoted to a number.

### Typed feedback (WS-D2's optimization half)

27. As the operator, I want P05 cost assumptions seeded only from verified
    P07 evidence classes, opt-in at plan time with provenance recorded in the
    plan contract, so that "Optimization" is real but never automatic
    (ticket 06).
28. As an AFK agent, I want default behavior proven byte-unchanged when
    feedback flags are absent, so that opt-in can never leak into the
    default path.
29. As the evidence auditor, I want the record's honesty boundary preserved
    (no parameters change automatically), so that the constitution of the
    program survives Phase D intact.

### Governance

30. As the operator, I want the native budget visible as a ledger
    (3 + 2 + 1 + 2, ceiling not promise), so that I can see remaining
    authority at any moment.
31. As the next-session agent, I want the UNKNOWN ledger updated and nothing
    relabeled at Phase D's close, so that the terminal state is honest for
    whoever continues.

## Implementation Decisions

### Scope and headings

- Phase D is defined under "Closed-Loop Optimization" + "Productization";
  "Final Release" remains undefined (D6). WS2 (concurrency / shared-asset
  reuse) and WS6 (full productization: packaging, CI, ops runbooks) are out
  as standalone workstreams (D1).
- The ramrom seed-loop product is the backbone; every other workstream
  justifies itself by serving it (D2). `docs/specs/ramrom-product.md` stays
  the product constitution; this spec is the phase-level overlay — on
  conflict, the ramrom operator clauses win for product behavior and this
  spec's decisions of record win for phase-level budget and sequencing.

### WS-D1 — the three fixes, additive only

- **Observation window v2 (ticket 01):** distance-scaled successor of the
  60-economy-day guard, decided as a reviewable formula (what it scales
  with, floor, ceiling, load-wait treatment, extreme-distance behavior) and
  carried as a **versioned budget field sealed at prepare** — v1 identities
  stay byte-equal, never reinterpreted. E206 remains the forensics of
  record; the guard fired as designed.
- **Capture-scheduler capacity (ticket 02):** redesign chosen among pacing,
  cross-session split, window widening, or honest typed per-relationship
  skip — under the constraint that pause-the-clock pacing and the
  month-pace gate keep their typed surfaces, and that retained seed-8/seed-9
  bytes become offline fixtures (never targets).
- **Census integration (ticket 03, blocked by 01):** per-world tile
  classification rides the loop capture as an additive protocol in the
  wire-contract family (protocol numbers 4–11 are taken; the next free
  numbers apply), reusing the schema-2 page contracts proven natively; the
  sealed `SOURCE_SAVE_FUSION` REJECTED verdict is not re-opened — the fusion
  gate stays CLOSED and no retained census record is relabeled.
- Delivered profile: current bounded 256×256 flat-temperate generation,
  bounded terraforming, Tile-V2 census mechanics, pause pacing — no slopes,
  bridges, tunnels, >256×256, or >32 industries (D9).

### WS-D2 — backbone and the loop's feedback half

- Offline bar first: tickets 01–03 landed with focused suites green, the
  `--cycles N` prepare/preflight lifecycle green at the v2 window, and the
  battery commands of record frozen and documented **before the first
  grant**.
- Battery: ×3 one-shots, seeds 11/12/13, each its own grant, each round the
  full four-gate discipline (staging approval → independent review → Gate C
  signing → separate launch approval), one launch, no retry/reconnect,
  certified cleanup, stop on first unexpected failure (D18, D19). The
  consumed seeds 2026/7/8/9 are never re-run.
- Bar of record (restated from the ramrom spec): ≥1 verified native plan +
  delivery cycle without `NO_FEASIBLE_SERVICES`, all terminals honestly
  typed; plus per-cycle replay — the verify path rc 0 with every cycle
  independently verified.
- **Typed feedback (ticket 06):** P05 cost assumptions seeded only from
  verified P07 evidence classes; opt-in flags at plan time; every seeded
  assumption carries its provenance and source digest in the plan contract;
  default behavior byte-unchanged (expand-only parameterization precedent);
  never automatic — no parameter changes between cycles, no retraining, no
  UNKNOWN promoted to a number (D11; README honesty boundary preserved).
- **GUI capstone:** the final backbone round runs with the spectator GUI
  product scope (no `--stop-on-delivery`, view hold, real window close,
  `ENDED_BY_OPERATOR` typed softly), only after ≥1 headless verified cycle
  exists; it discharges the E148/E149 owed element (D14).

### WS-D3 — delivered class

- Diagnosis gate first (ticket 05): an offline diagnosis record over
  retained corridor candidate bytes to the E105/E111 standard —
  source-verified semantics, each candidate explanation confirmed or
  eliminated by named evidence — before any fix candidate may be staged.
- Fix lands offline with suites green; then ×1 candidate round through all
  four gates, typed terminal whatever it is; ×2 is the corrective
  contingency. E36 closes **only** on actual DELIVERED receipts (E135
  rule); the `d5-delivered-class-tail` ladder is the designed closure path.
- This workstream runs on the corridor line, independent of the backbone
  battery; interleaving is the operator's call.

### WS-D4 — rail offline build

- v1 capability set decided by ticket 08 from the resolved API-surface study
  (signaling scheme, terrain basis, consist policy, station join policy,
  quote fidelity, explicit exclusions) — the five hard gaps become typed
  constraints, and unsupported checks are refused honestly offline.
- The rail capability is a **new additive package composition** mirroring
  the road-side pattern families: planning candidates, a rail wire contract
  on the next free protocol numbers, a rail GameScript package family,
  orders/vehicle lifecycle, and controlled tests. Frozen road packages are
  never edited.
- Zero native claims in Phase D (D12); every pinned digest of record stays
  byte-stable; the D-road contracts are untouched.

### WS-D5 — economics

- Per-cycle P&L derived offline from the loop's existing receipt shapes,
  extending the consolidated OPEX/ROI pattern (T-033) to the random world —
  only after the backbone retains ≥1 verified cycle. The derivation record
  lands under a new identity in the experiments tree; E194's record is never
  relabeled. Every number carries an OBSERVED / DERIVED / UNKNOWN label and
  its source digest; OPEX categories and ROI stay typed UNKNOWN wherever no
  native accounting observation exists (D13).

### WS-D6 — quality floor and release discipline

- **Quality floor (gates the first native round, D15/D7):** repair the four
  E207 extra reds; per-class triage-and-seal dispositions for the legacy red
  classes (ticket 07 decides each: repair, or seal with a typed reason);
  then a full-suite re-run that is green or every remaining red carrying a
  typed disposition.
- The full-suite command of record (the E207 baseline shape — the whole test
  tree in one run) is written into `REPRODUCE.md` together with
  version/release-notes discipline (D16). No packaging, CI, or ops runbooks.
- Full-suite gate cadence during Phase D: decided by ticket 07's disposition
  record (which landings re-run the suite).

### Cross-cutting architecture (what changes, what doesn't)

- **Unchanged:** Python owns optimization/identity/validation/deadlines;
  GameScript executes company commands only under the company mode; one
  encrypted Admin connection per attempt (loop cycles reconnect once per
  cycle top); bounded CP-SAT service selection and bounded corridor
  admission; the four-gate native discipline; per-attempt claim identity;
  the wire-protocol family pattern.
- **Changed additively only:** window v2 as a versioned budget field;
  scheduler capacity policy; per-world census protocol in the loop capture;
  typed-feedback opt-in flags (default byte-unchanged); the rail family.
- **Never changed:** attempt/claim identity discipline (no concurrency);
  the honesty boundary (no automatic parameter change); no retained-record
  reinterpretation; no evidence regeneration; `artifacts/` immutable.

### Sequencing of record

- M0 proposal approval (operator) → M1 quality floor → M2 backbone offline
  bar (tickets 01→03, 02) → M3 battery ×3 → M5 typed feedback + economics →
  M7 GUI capstone; M4 delivered-class round(s) branch independently and may
  interleave by operator choice; M6 rail offline build runs anytime offline.
- Hard rules: the quality floor gates the first native round; the capstone
  waits for a headless verified cycle; economics and typed feedback wait for
  retained verified-cycle receipts; nothing native happens on rail.
- Every native round appends its evidence rows; the UNKNOWN ledger is
  updated; FAILED stays FAILED.

## Testing Decisions

**What makes a good test here.** Tests assert external behavior at the
existing seams — the offline CLI of record, the wire-contract /
package-family triads, the sealed budget tables and versioned identity
fields, the typed refusal surfaces, the P07 replay/verify path, and the
full-suite gate — never implementation internals. Typed outcomes are
asserted as typed: a test that expects refusal names the refusal class.
Byte-stability is pinned: v1 window/budget identities, profile shapes, and
sealed digests have explicit byte-compat tests so additive change cannot
reinterpret history. Retained evidence bytes appear only as **fixtures**
(seed-8/seed-9 scheduler fixtures, retained facts re-derivations), never as
re-run targets, and synthetic fixtures never substitute for missing native
evidence. Tests backed by retained `artifacts/` may fail on a clone — that
means missing evidence, never a code bug.

**Modules and seams tested, by workstream:**

- WS-D1: the window-v2 budget-field arithmetic (floor/ceiling/extremes, v1
  byte-compat pins); the scheduler capacity policy over retained seed-8/9
  fixture bytes (produces captured relationships, typed surfaces intact);
  the census-integration contract (additive protocol, fusion gate closed);
  focused suites on exactly the touched paths.
- WS-D2: the loop lifecycle offline (`--cycles N` prepare/preflight), the
  per-cycle replay verification shape, and the typed-feedback contract
  (default byte-unchanged; every seeded-provenance path; "never automatic"
  negative tests). Native validation rides the battery rounds, never a
  separate native round.
- WS-D3: the offline diagnosis record's re-derivations; fix suites on the
  corridor line.
- WS-D4: rail suites offline — the three-file family layout (wire contract
  / package-VM / staging-replay), pattern-family correspondence pinned by
  tests, zero native claims asserted.
- WS-D5: P&L derivation over retained receipt fixtures, label segregation
  asserted (OBSERVED/DERIVED/UNKNOWN per number).
- WS-D6: the full-suite re-run gate itself, plus lint and type checks of
  record (`ruff` clean on touched paths; `ty` clean or carrying only the
  tolerated pre-existing diagnostics).

**Prior art in the codebase:** the corridor census family's three-file
suite layout (wire / package-VM / staging-replay, 78 tests at E65); the
corridor freight v2 paired suites (61 + 67 at E53); fixture re-derivation
from retained facts bytes (the ramrom §2 offline bar); the expand-only
parameterization default-unchanged test pattern; and the E207 full-suite
baseline run (6382 collected / 57 failed / 54 skipped) as the command shape
to freeze.

## Out of Scope

- WS2 concurrency, shared-asset reuse, concurrent payment windows — the
  record's UNKNOWNs stay UNKNOWN; no contract work is planned.
- New world capabilities: slopes/obstructed clearing as executable
  construction, bridges/tunnels, maps >256×256, >32 industries.
- Rail native construction, rail delivery, path signals beyond what the
  offline build needs to type-refuse honestly.
- Full automatic optimization — anything that changes parameters without an
  explicit operator-granted, evidence-gated opt-in.
- Full productization: packaging, CI, ops runbooks.
- The "Final Release" heading — stays undefined.
- Re-running, re-signing, or relabeling any consumed identity; regenerating
  retained evidence; substituting synthetic fixtures for native evidence.
- PostgreSQL as a demo prerequisite.
- Any implementation before the operator approves the scope proposal (M0),
  and any commit — every commit is its own operator decision.

## Further Notes

- **Approval gate.** This spec is written; the M0 approval of the scope
  proposal is still the operator's. `ready-for-agent` here means: once M0
  lands, an AFK agent may pick up offline implementation for any workstream
  whose governing decision ticket is `resolved` (today: ticket 04 resolved;
  ticket 08 unblocked by it). HITL tickets (01, 02, 03, 05, 06, 07) need
  the operator first.
- **UNKNOWN ledger preserved** (never invent): feasibility of any
  particular ungenerated seed; random-world OPEX categories and ROI beyond
  observed cash deltas; concurrency and concurrent throughput; paid
  shared-asset reuse; the 4 E207 extras' new-vs-pre-existing status (until
  ticket 07's round); the delivered-class root cause (until the diagnosis
  record); whether the battery bar can be met at all under v2 — that is
  what the battery is for.
- **Budget discipline.** The ≤8 ledger is a ceiling, not a promise. If the
  ×3 battery honestly misses the bar and the reserve is spent, Phase D ends
  with the honestly-unmet statement — the Phase C precedent — and further
  seeds become a new operator decision.
- **Decision tickets of record** live at `.scratch/phase-d-scope/issues/`
  (01 window-v2 formula; 02 capture-scheduler capacity; 03 census
  integration; 04 rail API study — resolved with the note at
  `.scratch/phase-d-scope/research/01-rail-api-surface-study.md`; 05
  delivered-class diagnosis gate; 06 typed-feedback policy; 07 legacy-red
  triage disposition; 08 rail offline-build scope). This spec does not
  replace them; it consumes their answers as they resolve.
- **Evidence anchors:** E198–E202 (battery consumed, Phase C terminal),
  E203 (Phase D discovery), E204–E207 (P1/P2/P4 offline rounds, first
  full-suite baseline), E206 (observation-window forensics of record),
  E148/E149 (GUI probe owed element). Nothing in this spec modifies them.
