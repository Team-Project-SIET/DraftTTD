# Future development opportunities (2026-11-13)

This document presents the future development opportunities the customer asked
about, grounded in the operator-approved Phase D scope of record
([phase-d-scope-proposal-2026-11-12.md](phase-d-scope-proposal-2026-11-12.md))
and the standing ledgers. Everything here is **planned or opportunistic — none
of it is implemented by this document**, and **none of it is an automatic MVP
handover blocker**: Phase D's native rounds are optional future work under
per-round explicit operator grants (README §Phase D status).

Status labels follow [CUSTOMER_PRESENTATION_INDEX.md](CUSTOMER_PRESENTATION_INDEX.md) §1.

## 1. Where Phase D stands today

| Milestone | Meaning | Status |
| --- | --- | --- |
| M0 | Scope proposal approved by the operator | DONE (2026-11-12) |
| M1 | Offline quality floor: typed dispositions + extras repair + full-suite rerun — green 6327 passed / 55 skipped / 0 failed, exit 0 | DONE (E208; prepared, uncommitted at time of writing) |
| M2 | Backbone offline bar (WS-D1 fix tickets; offline backbone, tickets 12–23) | PLANNED — not an MVP handover requirement |
| M3 | Backbone battery rounds 1–3 (seeds 11/12/13) | PLANNED — native ×3, per-round grants |
| M4 | Delivered-class round(s) (candidate round → fix → contingency) | PLANNED — native ×1–2, independent of M3 |
| M5 | Typed feedback + economics (ticket 06, WS-D5) | PLANNED — offline, after ≥1 verified cycle |
| M6 | Rail offline build (ticket 04 → contract → build) | PLANNED — offline, anytime; zero native claims |
| M7 | GUI capstone | PLANNED — native ×1, only after M3 retains ≥1 verified headless cycle |

Native budget of record: **≤ 8 launches total** (battery ×3, delivered-class
×2, GUI capstone ×1, operator reserve ×2) — a ceiling, with every round keeping
all four gates (staging → review → Gate C signing → separate launch approval).

## 2. The six workstreams

### WS-D1 — Advanced World & Terrain: deliver the current profile

Make the existing bounded 256×256 random profile actually deliverable by
removing three named, evidenced blockers: P08
`INCOMPLETE_TILE_CLASSIFICATION`; capture-scheduler capacity policy (seed-8
`CAPTURE_SCHEDULE_EMPTY`, E200); observation-window distance sensitivity
(E206). No new world capability is promised: slopes/obstructed clearing as
executable construction, bridges/tunnels, >256×256 and >32 industries stay
OUT. Feasibility beyond recorded slices stays UNKNOWN (every bounded random
search to date has `search_truncated: true`, E202).

### WS-D2 — Closed-Loop Optimization: the ramrom backbone

Carry the standing loop engine (`run_loops`, `loop_gate`, per-cycle
recordings, `verify_loop_receipt` — offline-verified, E143) to its honestly
unmet native bar: **≥1 verified native plan + delivery cycle without a
`NO_FEASIBLE_SERVICES` terminal**, every terminal honestly typed, and
per-cycle replay `verify <run-dir>` rc 0. Consumed seeds (2026/7/8/9) are
never re-run; fresh identities on seeds 11/12/13. Once ≥1 verified cycle is
retained, typed feedback (ticket 06) becomes implementable and WS-D5's
economics gain inputs — this is the workstream that would first make
**closed-loop optimization** more than an UNPROVEN label.

### WS-D3 — Delivered class / E36

Give the corridor's twice-reproduced `CARGOFLOW2_LOADED_NEVER_DELIVERED`
terminal (candidates 9 and 11) a diagnosed root cause to the E105/E111
evidence standard, an offline fix, and one fresh gated candidate round (+ one
corrective contingency). **E36 closes only on actual native DELIVERED
receipts (E135 rule); otherwise it stays open honestly.** This is the designed
path to finally proving corridor cargo delivery — today's most material open
gap.

### WS-D4 — Rail Logistics: offline build only

A rail capability *build*, never a native run in Phase D: rail planning
candidates, a rail construction wire contract (next free protocol number), a
rail GameScript package family (additive composition — frozen road packages
are never edited), orders/vehicle lifecycle, controlled tests. The 15.3 script
API study of record (`.scratch/phase-d-scope/research/01-rail-api-surface-study.md`)
confirms the full rail build surface exists (track, depots, stations,
waypoints, signals, GS-side orders since 14.0) with five named hard gaps (no
block-occupancy readback, no slope→track oracle, no curve-limit API,
base-price-only quoting, precondition aborts). Explicit non-goals: rail native
construction and rail delivery. Today rail is NOT IMPLEMENTED; this workstream
is how it would first exist — offline.

### WS-D5 — Long-Run Economics: offline P&L from receipts

Once the backbone retains ≥1 verified cycle, derive per-cycle P&L (freight
revenue, vehicle running cost, cash delta) offline from existing receipt
shapes, extending the T-033 consolidation pattern to the random world. Every
number carries its OBSERVED / DERIVED / CONTROLLED / UNKNOWN label and source
digest; OPEX categories and ROI stay typed UNKNOWN wherever no native
accounting observation exists (E203 §4 item 9 preserved). This is the honest
path toward the currently UNKNOWN OPEX/ROI question — it can produce labeled
derivations, never a profit certificate (ADR-0001 D5 stands).

### WS-D6 — Productization: minimal release discipline

The quality floor (typed dispositions + extras repair + full-suite rerun gate
— M1, done), the full-suite command of record written into REPRODUCE.md (none
existed before E207), and version/release notes discipline. Deliberately no
packaging, no CI, no ops runbooks in this scope.

## 3. Opportunities beyond the approved Phase D scope (not scheduled)

These are candidate directions an operator could authorize later; none has a
ticket, a budget allocation, or a promise behind it today:

- **Corridor delivery closure beyond E36** — if WS-D3 produces DELIVERED
  receipts, the broader corridor product (multi-corridor networks, shared
  depots) becomes designable on proven ground.
- **Concurrency / paid shared-asset reuse** — both UNPROVEN today; they would
  need their own scoped proposal, acceptance bars and budgets. No design of
  record exists yet.
- **Random-world window redesign** — the seed-7 plan exposed the
  observation-window boundary; any window redesign is a fresh operator
  decision (README §Open disclosures), not an automatic follow-on.
- **GUI product scope** — capability probes are VERIFIED (E170, E180); the
  product scope owed by E148/E149 is unbuilt and remains a separate operator
  decision.
- **Cross-reality twin study** — E114 (twin-vs-native cross-reality) is a
  typed open UNKNOWN carried terminally closed with Phase A (E127); any study
  would be new scoped work.

## 4. What future work will not do (standing rules)

- Never relabel a FAILED terminal or regenerate retained evidence.
- Never count planned work as implemented in customer materials.
- Never re-run consumed candidates, seeds or one-shot claims.
- Never transfer OpenTTD 13.4 history as 15.3 proof; 15.3 remains the primary
  target.
- Never present revenue as profit or fill an UNKNOWN with a guess.

## Related documents

- Scope of record: [phase-d-scope-proposal-2026-11-12.md](phase-d-scope-proposal-2026-11-12.md)
- Closure plan: [PROJECT_CLOSURE_PLAN.md](PROJECT_CLOSURE_PLAN.md)
- Gap analysis: [CUSTOMER_HANDOVER_GAP_ANALYSIS.md](CUSTOMER_HANDOVER_GAP_ANALYSIS.md)
- Use cases: [customer-use-cases.md](customer-use-cases.md)
