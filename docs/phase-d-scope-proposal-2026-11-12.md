# Phase D scope proposal — 2026-11-12

**Status: APPROVED — M0 granted by the operator in-session, 2026-11-12. The
approval covers offline implementation under the decision-ticket graph
(`.scratch/phase-d-scope/issues/`, spec `docs/specs/phase-d-scope.md`); it
grants no runtime authority of any kind:** no OpenTTD launch, no AdminPort
connection, no staging, no signing, no claim, no retry of a consumed attempt,
no evidence regeneration; commits and pushes remain separate operator
decisions. Every gate named below still requires its own explicit operator
approval in-session. Vocabulary
(VERIFIED / PROVEN / PREPARED / PARTIAL / FAILED / UNKNOWN, consumed, sealed)
means exactly what `AI_HANDOFF.md` defines.

Provenance: this proposal was produced by the Stage-1/Stage-2 scope-definition
session of 2026-11-12 (requirements interview + wayfinder charting), after the
Phase C terminal statement (E202), the Phase D discovery record (E203) and the
P1/P2/P4 offline rounds (E204–E207). Strict session boundaries were honored: no
application code modified, no native run, no evidence mutation, no commit. All
artifacts of this session are uncommitted working-tree files:

- this proposal (`docs/phase-d-scope-proposal-2026-11-12.md`),
- the wayfinder map (`.scratch/phase-d-scope/map.md`) and its seven decision
  tickets (`.scratch/phase-d-scope/issues/01…07`),
- one background rail-API research note (to be filed at
  `.scratch/phase-d-scope/research/01-rail-api-surface-study.md`).

## 1. Scope finding of record

The three undefined headings on file were "Closed-Loop Optimization",
"Productization", "Final Release" (E203: 0 occurrences anywhere before this
session). **This proposal defines Phase D under the first two headings and
leaves "Final Release" undefined.** The ramrom seed-loop line
(`docs/specs/ramrom-product.md`) is the backbone: Phase D's destination is
**≥1 verified native plan + delivery cycle on a random world** — the battery
bar that was honestly NOT met in Phase C (E198–E201) — pursued by new means on
fresh seed identities, plus four supporting workstreams and a quality floor.
Phase D existence itself is an operator decision (E205 deferred it); this
document is that decision's subject matter, not its approval.

## 2. Decisions of record (Stage-1 interview, 2026-11-12)

| # | Question | Decision |
|---|---|---|
| D1 | Which of the six proposed workstreams are Phase D candidates? | WS1 World&Terrain, WS3 Closed-Loop, WS4 Rail, WS5 Economics **in**; E36 delivered-class **in as its own workstream**; WS2 (concurrency/shared infrastructure) and WS6 (full productization) **out as standalone workstreams** |
| D2 | Program backbone | **Ramrom seed-loop product** (spec §1); other workstreams justify themselves by serving it |
| D3 | Native-launch appetite | **4–8 one-shots**, each its own 4-gate round; count is a ceiling, not a promise |
| D4 | Definition-of-Done shape | **Offline bar + native proof on the core** (backbone); typed terminals throughout |
| D5 | E36 (delivered class) | **Owned by Phase D as its own workstream** (WS-D3) |
| D6 | Heading mapping | **Closed-Loop Optimization + Productization**; "Final Release" stays undefined |
| D7 | E207 regression debt | **Quality floor first** — gates Phase D's first native round |
| D8 | Proposal artifact | **Uncommitted docs file** + map; commit is a separate operator decision |
| D9 | WS1 concrete target | **Deliver the current bounded 256×256 profile** — no slopes/bridges/>256×256/>32-industries work |
| D10 | Observation window | **Distance-scaled v2** (the E206-named fresh operator decision, now taken at proposal level; formula is decision-ticket 01) |
| D11 | "Closed-Loop Optimization" meaning | **Operation loop + typed, opt-in, evidence-gated feedback** (extends the existing feedback-informed comparison path); **never automatic** (README :853-855 preserved) |
| D12 | Rail acceptance bar | **Offline build only** — zero native launches in Phase D |
| D13 | Economics bar | **Offline per-cycle P&L from loop receipts**; UNKNOWN stays UNKNOWN where no native accounting exists |
| D14 | GUI-bearing native probe | **In budget, as the capstone one-shot** (spec §1/§3.3 product scope; discharges the E148/E149 owed element) |
| D15 | Quality-floor DoD | Diagnose/repair the 4 E207 extras; per-class triage-and-seal for the legacy reds; full-suite re-run green-or-honestly-triaged **before the first native round** |
| D16 | Productization content | **Minimal release discipline**: the quality floor + the full-suite command of record + version/release notes in REPRODUCE.md; no packaging/CI/ops runbooks |
| D17 | Planning artifacts | Map + decision tickets under `.scratch/phase-d-scope/` alongside the proposal |
| D18 | Native one-shot split | **Backbone ×3 + delivered-class ×2 + GUI capstone ×1 + operator-held reserve ×2** |
| D19 | Backbone battery seeds | **Three named fresh seeds** (proposed 11, 12, 13 — never-consumed status verified at grant time); each run its own grant |

## 3. Vocabulary of record (new Phase D terms)

`CONTEXT.md` is byte-pinned and prepend-only; these terms live here, not there.

- **Backbone** — the ramrom seed-loop product line; Phase D's primary
  destination bar and the consumer of the ×3 native battery allocation.
- **Quality floor** — the offline regression gate (E207 remediation +
  dispositions) that must pass green-or-honestly-triaged before Phase D's
  first native round.
- **Observation window v2** — the distance-scaled successor of the
  60-economy-day observation guard, versioned as a sealed budget field; v1
  identities stay byte-equal and are never reinterpreted (E206 is the
  forensics of record; the guard fired as designed).
- **Typed feedback** — P05 cost assumptions seeded only from verified P07
  evidence classes, opt-in at plan time, provenance-labeled, never automatic.
- **Delivered class** — the `CARGOFLOW2_LOADED_NEVER_DELIVERED` terminal
  family on the corridor line; closes E36 only on actual DELIVERED receipts.
- **Capstone** — the GUI-bearing product-scope one-shot (no
  `--stop-on-delivery`, view hold, real window close, `ENDED_BY_OPERATOR`),
  the backbone's final native round.

## 4. Workstreams

### WS-D1 — Advanced World & Terrain: deliver the current profile

**Goal.** Make the existing bounded 256×256 random profile actually deliverable
by removing the three named, evidenced blockers. No new world capability.

| Capability class | Items |
|---|---|
| PROVEN (boundary of this WS) | 256×256 flat-temperate generation/discovery/spectator (E4/E8); native clearing + bounded terraforming (D3, E19); Tile-V2 native census capture mechanics (E16); pause-the-clock pacing natively 4× (E150/E198/E199/E201) |
| PARTIAL / PREPARED (the work) | P08 `INCOMPLETE_TILE_CLASSIFICATION`; capture-scheduler capacity policy (seed-8 `CAPTURE_SCHEDULE_EMPTY`, E200); observation-window distance sensitivity (E206); per-world census integration (fusion gate stays CLOSED, E16 sealed) |
| UNKNOWN (preserved) | Feasibility beyond recorded slices — every bounded random search has `search_truncated: true` (E202) |
| OUT | Slopes/obstructed clearing as executable construction, bridges/tunnels, >256×256, >32 industries (README :174, roadmap §1) |

**Offline bar.** Decision tickets 01–03 resolved; window-v2 + scheduler +
census-integration implemented additive-only with focused suites green
(named at implementation time), v1 byte-compat pinned, sealed consumed
identities untouched.

**Native surface.** None by itself; WS-D1's fixes are consumed by the backbone
battery rounds.

### WS-D2 — Closed-Loop Optimization: the ramrom backbone

**Goal.** Carry the built-and-standing loop engine (ticket-05 build: `run_loops`,
`loop_gate`, per-cycle recordings, `verify_loop_receipt` — all offline-verified)
to its honestly-unmet native bar.

**Acceptance bar of record** (the ramrom spec's bar, restated for Phase D):
the battery produces **≥1 verified native plan + delivery cycle without a
`NO_FEASIBLE_SERVICES` terminal**, and every terminal of every battery run
stays honestly typed. A second bar element from the loop design: per-cycle
replay — `verify <run-dir>` rc 0 with every cycle independently verified.

**Offline bar.** Tickets 01–03 landed; loop suites green; `--cycles N`
prepare/preflight lifecycle green at the v2 window; command-of-record freeze
documented before the first grant.

**Native surface.** ×3 one-shots on seeds 11/12/13 (fresh identities; the
consumed 2026/7/8/9 are never re-run). Each round: staging → independent
review → Gate C signing → separate launch approval, in-session, one launch,
no retry, stop on first unexpected failure. Typed terminals are acceptable
honest outcomes (Phase C precedent); the reserve exists for design-iteration
rounds if a halt class appears.

**Then the operation loop closes.** With ≥1 verified cycle retained, ticket 06
(typed feedback) becomes implementable and WS-D5's economics have inputs.

### WS-D3 — Delivered class / E36

**Goal.** Give the corridor's twice-reproduced
`CARGOFLOW2_LOADED_NEVER_DELIVERED` terminal (candidates 9, 11) a diagnosed
root cause and one fresh candidate round; E36 closes **only** on actual
DELIVERED receipts (E135 rule) — otherwise it stays open honestly.

**Steps.** (1) Offline diagnosis over retained bytes to the E105/E111 evidence
standard (ticket 05 decides the plan + ready-gate). (2) Fix offline, suites
green. (3) One gated candidate round (×1 of the ×2 allocation), typed terminal
whatever it is; the second allocation is the corrective contingency if a halt
class appears. The `d5-delivered-class-tail` ladder (issues 06→07→08) is the
designed closure path this workstream executes.

### WS-D4 — Rail Logistics: offline build only

**Goal.** A rail capability *build*, never a native run in Phase D: rail
planning candidates, a rail construction wire contract (next free protocol
number), a rail GameScript package family, orders/vehicle lifecycle, and
controlled tests — mirroring the three road-side pattern families.

**Offline bar.** Focused suites green; every pinned digest of record
byte-stable; the D-road contracts untouched. Explicit non-goals: rail native
construction, rail delivery, path signals beyond what the offline build needs
to type-refuse honestly.

**Research input.** Ticket 04's API-surface study is RESOLVED — note of record
[`.scratch/phase-d-scope/research/01-rail-api-surface-study.md`](../.scratch/phase-d-scope/research/01-rail-api-surface-study.md):
the 15.3 script API provides the full rail build surface (track, depots,
stations, waypoints, signals) and GS-side orders since 14.0; the five hard
gaps are no block-occupancy readback, no slope→track oracle, no curve-limit
API, base-price-only quoting, and precondition aborts. The contract shape
(ticket 08) decides the v1 capability set from the study's §5; `GSRail`
appears in the repo only as a forbidden symbol in the observe-only bridge
gate, so the rail analog is a new additive package composition — frozen road
packages are never edited.

### WS-D5 — Long-Run Economics: offline P&L from receipts

**Goal.** Once the backbone retains ≥1 verified cycle, derive per-cycle P&L
(freight revenue, vehicle running cost, cash delta) offline from the loop's
existing receipt shapes, extending T-033's consolidation pattern to the random
world. OPEX categories and ROI stay typed UNKNOWN wherever no native
accounting observation exists (E203 §4 item 9 preserved).

**Offline bar.** Derivation record under a new identity in
`artifacts/experiments/` (never relabeling E194's); OBSERVED/DERIVED/
CONTROLLED segregation; no new native round consumed by this workstream.

### WS-D6 — Productization: minimal release discipline

**Goal.** Discharge the "Productization" heading with exactly what the
program needs to be operable: the quality floor (ticket 07's dispositions +
the extras repair + the full-suite re-run gate), the full-suite command of
record written into `REPRODUCE.md` (none existed before E207), and version/
release notes discipline. No packaging, no CI, no ops runbooks.

## 5. Native budget ledger

| Allocation | Rounds | Workstream | Notes |
|---|---|---|---|
| Backbone battery | ×3 | WS-D2 | Seeds 11/12/13, each its own grant |
| Delivered class | ×2 | WS-D3 | Candidate round + corrective contingency |
| GUI capstone | ×1 | WS-D2 | After ≥1 headless verified cycle exists |
| Operator reserve | ×2 | any | Held by the operator; no default claimant |
| **Total** | **≤8** | | Count is a ceiling; every round keeps all four gates |

Gate discipline (unchanged from the roadmap §8 invariants): staging approval →
independent review → Gate C signing → separate explicit launch approval, all
in-session; one launch, no retry/reconnect; certified cleanup; stop on first
unexpected failure; consumed identities never reused; `artifacts/` immutable.

## 6. Dependencies and sequencing

```text
M0 proposal approval (operator)
 └─ M1 quality floor (WS-D6; tickets 05-ticket-07 + 07 + repair)   [offline]
     └─ M2 backbone offline bar (WS-D1 fixes: tickets 01→03, 02)   [offline]
         └─ M3 battery rounds 1–3 (seeds 11/12/13)                 [native ×3]
             └─ M5 typed feedback + economics (tickets 06, WS-D5)  [offline]
     └─ M4 delivered-class round(s) (ticket 05 → fix → round)      [native ×1–2]
         (independent of M3; interleaving is the operator's call)
 └─ M6 rail offline build (ticket 04 → contract → build)           [offline, anytime]
 └─ M7 GUI capstone                                                [native ×1, after M3 ≥1 verified cycle]
```

Hard rules: the quality floor gates the first native round (D15); the capstone
waits for a headless verified cycle; WS-D5 and ticket 06 wait for retained
verified-cycle receipts; nothing native happens on rail.

## 7. Architecture and technology choices (what changes, what doesn't)

- **Unchanged:** Python owns optimization/identity/validation/deadlines;
  GameScript executes commands under `GSCompanyMode`; one encrypted Admin
  connection per attempt (loop cycles reconnect once per cycle top, spec §3.2);
  P05 bounded CP-SAT selection; P08 bounded corridor admission; the 4-gate
  native discipline; the wire-protocol family pattern; per-attempt claim
  identity.
- **Changed additively:** observation window becomes distance-scaled v2 (a
  versioned budget field, sealed at prepare, v1 byte-equal); capture-scheduler
  capacity policy redesigned around the seed-8 class; per-world census pages
  become an additive protocol in the loop capture (fusion gate stays closed);
  typed-feedback opt-in flags extend the existing comparison path
  (default byte-unchanged); rail gains its own protocol/package/pipeline
  family offline.
- **Explicitly not changed:** the attempt/claim identity discipline (no
  concurrency); the honesty boundary at README :853-855; no automatic
  parameter change; no retained-record reinterpretation.

## 8. Acceptance criteria and evidence classes (summary)

| Workstream | Machine-verifiable acceptance | Evidence class |
|---|---|---|
| WS-D1 | Focused suites green on touched paths; v1 byte-compat pin tests; seed-8/9 fixtures produce non-empty capture schedules offline | CONTROLLED (offline tests) |
| WS-D2 | Battery bar: ≥1 verified native plan+delivery cycle, no `NO_FEASIBLE_SERVICES` terminal, all terminals honestly typed; `verify` rc 0 with `verified_loop_cycles` | OBSERVED native receipts + offline replay |
| WS-D3 | Diagnosis record at the E105/E111 standard; one candidate round through all four gates; E36 closed iff DELIVERED receipts exist | OBSERVED (native) + offline reconciliation |
| WS-D4 | Rail suites green offline; zero native claims; pattern-family correspondence (wire/package/pipeline) pinned by tests | CONTROLLED |
| WS-D5 | Per-cycle P&L record under a new identity; every number carries OBSERVED/DERIVED/UNKNOWN label and source digest | DERIVED from OBSERVED receipts |
| WS-D6 | Full-suite re-run: green or every remaining red carrying a typed disposition; command of record in REPRODUCE.md | CONTROLLED (offline gate) |

## 9. Offline/native verification strategy

1. **Offline bar first** — every workstream lands implemented + controlled
   tested before any grant is requested (the A–C pattern).
2. **Fresh-grant one-shots** — native validation only through the 4-gate
   round; command of record frozen and documented before staging.
3. **Honest typed terminals** — failure is a typed, retained outcome
   (`WINDOW_EXHAUSTED`, `NATIVE_CORRIDOR_BOUND`, `CAPTURE_SCHEDULE_EMPTY`,
   halt classes…), never relabeled, never retried on the same identity.
4. **Replay of record** — `verify` subcommands reproduce retained receipts
   digest-for-digest; manifests re-derive; cleanup certified; FAILED stays
   FAILED.
5. **Evidence discipline** — new records under new identities; `artifacts/`
   untouched by anything in this proposal; no synthetic fixture substitutes
   for missing native evidence.

## 10. Risks, constraints, authorization gates

- **Launch-gate-only defect risk** (roadmap §7): purchase/departure/cycle/
  delivery tails have first-execution risk; each new halt class costs a
  corrective round — the reserve ×2 exists for this, and the delivered-class
  allocation carries its own contingency.
- **Window-v2 reinterpretation risk**: v2 must never reinterpret v1 records;
  byte-compat pin tests are part of the offline bar.
- **Scheduler redesign interaction**: pause pacing and the month-pace gate are
  proven; the redesign must keep their typed surfaces intact (ticket 02's
  constraint list).
- **Rail greenfield risk**: zero code/evidence today; mitigated by
  offline-only scope and the API-surface study (ticket 04) preceding any
  contract design.
- **Honesty-boundary risk on typed feedback**: mitigated by opt-in flags,
  provenance labels, default byte-unchanged, "never automatic" tests.
- **Budget-exhaustion risk**: if the ×3 battery honestly misses the bar and
  the reserve is spent, Phase D ends with the honestly-unmet statement — the
  Phase C precedent — and further seeds become a new operator decision.
- **Clone drift**: tests backed by retained `artifacts/` may fail on a clone;
  that is missing evidence, never a code bug.
- **Authorization gates**: every native round = 4 operator approvals
  in-session; every commit = its own DG-10-style decision; this proposal's
  approval is itself an operator gate and creates no runtime authority.

## 11. Milestones and proposed Definition of Done

**Milestones.** M0 approval → M1 quality floor → M2 backbone offline bar →
M3 battery ×3 → M4 delivered-class round(s) → M5 typed feedback + economics →
M6 rail offline build → M7 GUI capstone. Native rounds are serial; M4 may
interleave with M3 by operator choice.

**Proposed Phase D Definition of Done** (checkable, in the A–C style):

1. The quality floor passed: full-suite re-run green-or-honestly-triaged
   before the first native round; dispositions recorded per class (M1).
2. The backbone bar adjudicated: ≥1 verified native plan+delivery cycle on a
   fresh seed, **or** every battery terminal honestly typed with the
   honestly-unmet statement of record (M3).
3. The delivered-class round(s) consumed through the four gates with a typed
   terminal; E36 closed only if DELIVERED receipts exist (M4).
4. Rail offline build landed with suites green and zero native claims (M6).
5. Typed-feedback policy decided and, if ≥1 verified cycle exists,
   implemented offline with default byte-unchanged proven (M5).
6. Per-cycle P&L record produced if ≥1 verified cycle exists, UNKNOWNs
   preserved (M5).
7. GUI capstone consumed with `ENDED_BY_OPERATOR` typed softly — or honestly
   not reached, with the owed element recorded as owed (M7).
8. Every native round's receipts verified offline; E-rows appended per round;
   the UNKNOWN ledger updated; nothing relabeled; no scope creep.

## 12. Out of scope (explicit)

WS2 concurrency and shared-asset reuse (UNKNOWNs stay UNKNOWN); slopes/
bridges/tunnels/>256×256/>32 industries; rail native construction or delivery;
full automatic optimization; packaging/CI/ops runbooks; the "Final Release"
heading; re-running any consumed identity; evidence regeneration or relabeling;
PostgreSQL as a demo prerequisite; any implementation before this proposal is
approved.

## 13. What stays UNKNOWN (never invent)

Feasibility of any particular ungenerated seed; random-world OPEX categories
and ROI beyond observed cash deltas; concurrency and concurrent throughput;
paid shared-asset reuse; the 4 E207 extras' new-vs-pre-existing status (until
ticket 07's round); the delivered-class root cause (until the diagnosis
record); rail's exact 15.3 API gaps (until the ticket-04 note is filed);
whether the battery bar can be met at all under v2 — that is what the battery
is for.

## 14. Map and decision tickets

The unresolved decisions live as tickets under `.scratch/phase-d-scope/`:
01 window-v2 formula · 02 capture-scheduler capacity · 03 census integration
(blocked by 01) · 04 rail API surface (**resolved** — research note filed at
`research/01-rail-api-surface-study.md`) · 05 delivered-class diagnosis gate ·
06 typed-feedback policy · 07 legacy-red triage disposition · 08 rail
offline-build scope (graduated from the study's §5). The map indexes the
decisions above and carries the fog ("Not yet specified") and the full
out-of-scope list. None of the tickets is an implementation ticket;
implementation begins only after the operator approves this proposal.
