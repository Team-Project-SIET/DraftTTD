# Main use cases supported by current capabilities (2026-11-13)

This document lists the main use cases the system supports today, each with
its honest status, and the use cases it explicitly does **not** support.
Statuses follow the vocabulary in
[CUSTOMER_PRESENTATION_INDEX.md](CUSTOMER_PRESENTATION_INDEX.md) §1; every
status carries its evidence anchor. Branch of record:
`miles/fright-delivery`, HEAD `90ebadb`. Documentation only — no runtime
authorization.

## Part A — supported use cases

### UC-1 · Fixed-demo planning-to-delivery MVP — VERIFIED (E1)

- **Actor:** operator (presenter); the planner acts autonomously in-game.
- **Flow:** one isolated OpenTTD 15.3 server, one graphical spectator, one
  encrypted Admin connection; the Python planner selects services (P05) and
  drives construction and freight delivery; independent readback produces
  receipts; P07 reporting, replay verification and certified cleanup follow.
- **Observed result:** 3 services/vehicles, 60 coal delivered, £1,022 revenue,
  £28,459 CAPEX; spectator inspection, P07, cleanup and integrity PASS.
- **Limits:** no direct company control; no full OPEX/ROI. This is the stable
  showpiece of record.

### UC-2 · Freight delivery on a fixed plan — VERIFIED

- **Standalone delivery:** Attempt 4 delivered 20 units with a verified
  receipt.
- **Planner-driven delivery:** Attempt 9 delivered 20 coal units with an
  attributed payment.
- **Multi-service delivery:** Attempts 12/14/17 delivered two and three
  serial P05-selected services in one world (Attempt 17: 60 coal, £1,018
  revenue, £28,459 CAPEX).
- **Limits:** fixed prepared worlds and pinned scopes; not arbitrary maps.

### UC-3 · Corridor infrastructure construction — PROVEN (v3 scope only, E35)

- **Actor:** planner via the staged native pipeline.
- **Flow:** one authorized launch builds the corridor, stops and depot; every
  operation is quoted, dispatched once, and independently read back
  (`NATIVE_STATE_CHANGED`); a receipt-bound authoritative after-save is
  produced.
- **Limits:** PROVEN for exactly the reviewed v3 scope; construction proves
  infrastructure build, **not** cargo delivery.

### UC-4 · Corridor survey and acceptance census — VERIFIED (E40, E44, E49)

- **Flow:** read-only survey sessions measure buildability, acceptance radii
  and production (delivery-stop tile 50862: 8/8 cargo acceptance, control
  0/8); the census lifecycle returns `SURVEY_COMPLETION_VERIFIED` under
  read-only replay.
- **Limits:** zero-mutation read-only sessions; acceptance measured, delivery
  still not proven (E36 open).

### UC-5 · Random-world generation and planning feasibility — PARTIAL

- **Works (CONTROLLED/offline):** `plan --random-world` generates a recipe
  (seed, size, climate, towns, industries, candidate/service/vehicle bounds,
  planning seconds); the Phase C feasibility engine classifies candidate
  spaces with typed outcomes; the seed-17 census reconciliation is verified
  (FD-C-1, E142).
- **Not proven:** observed-world service **execution and delivery** in
  random worlds — attempts 1–7 ended in typed terminals (E150–E157, E197)
  and Phase C/FD-C-2 stand `INCOMPLETE_EVIDENCE` (E142, E204); the seed
  battery was consumed with its bar honestly not met (E198–E201).
- **Rule:** random-world native runs remain operator-gated, one-shot.

### UC-6 · Long-horizon economy observation — VERIFIED (E195)

- **Flow:** the canonical continuous pipeline observed five complete native
  economy years, 1951–1955, with the standing 15.3 regression gate at the
  Phase B closure HEAD (`CANONICAL_FIVE_YEAR_CONTINUOUS_VERIFIED`).
- **Limits:** observation and reporting only; it is not an optimization
  claim.

### UC-7 · Offline inspection, reporting and comparison — CONTROLLED (always available)

- **Flow:** `check` (binary/assets/desktop validation), `plan` (offline
  selection), `report` (P07 read-only reports from completed native
  receipts), `compare` (descriptive across distinct seeds/configurations);
  plus the evidence-aware insights subcommand over retained attempt
  directories (REPRODUCE.md §2026-10-18 addendum).
- **Limits:** P07 needs completed native receipts; no PostgreSQL/Docker
  required; reports never invent missing facts.

### UC-8 · Operator-authorized native experiment lifecycle — VERIFIED mechanism

- **Flow:** staging → `PRELAUNCH` seal → `PREFLIGHT` → independent review →
  Gate C signing (pinned operator key, seed handled memory-only) → one-shot
  claim → single launch → independent readback → replay → certified cleanup →
  retained immutable evidence (`CLAIM.json` refuses re-minting,
  `proof/operator_authorization.py:347-348`).
- **Limits:** every native round needs its own explicit grant; this is a
  governance use case, not a product feature.

## Part B — explicitly NOT supported (honest boundary)

| Use case | Status | Anchor |
| --- | --- | --- |
| Rail freight delivery | NOT IMPLEMENTED — no code on the branch; Phase D treats it as offline-only planned work | Phase D scope proposal |
| Corridor cargo **delivery** (as distinct from construction) | NOT PROVEN — every corridor cargo-flow round ended `CARGOFLOW2_LOADED_NEVER_DELIVERED`; E36 open | E36, E124, E133, E134 |
| Concurrent multi-company / multi-session operation | UNPROVEN — no accepted concurrent-run evidence | Gap analysis of record |
| Paid shared-asset reuse across services | UNPROVEN | Gap analysis of record |
| Closed-loop optimization (delivery feedback changing plans) | UNPROVEN — planning and execution are currently one-way per attempt | Gap analysis of record |
| Arbitrary maps / unbounded worlds | NOT SUPPORTED — pinned worlds and bounded candidates (P08) only | P08 scope |
| GUI product scope | NOT BUILT — GUI capability probes are VERIFIED (E170, E180) but the product scope owed by E148/E149 is unbuilt | E148/E149 |
| OPEX / ROI / profitability reporting | UNKNOWN — revenue is never profit (ADR-0001 D5); CAPEX OBSERVED, margins DERIVED only | ADR-0001 |
| OpenTTD versions other than 15.3 (primary target) | NOT SUPPORTED — 13.4 material is regression history, never 15.3 proof | Handover docs |

## Part C — how a customer request maps to what exists

| Customer ask | Nearest supported capability | Gap |
| --- | --- | --- |
| "Deliver freight automatically" | UC-1/UC-2 (fixed prepared worlds) | Corridor/random-world delivery unproven |
| "Build the infrastructure too" | UC-3/UC-4 (v3 scope, read-only census) | Delivery over built corridors not proven |
| "Plan on a fresh random map" | UC-5 (generation + feasibility) | Observed-world execution unproven |
| "Show long-run behavior" | UC-6 (five economy years) | Not an optimization or profit claim |
| "Show me the numbers" | UC-7 (P07 reports, comparisons) | No OPEX/ROI; revenue ≠ profit |
| "Extend to rail" | — | NOT IMPLEMENTED; Phase D offline-only planned |

## Related documents

- Live demo workflow: [customer-live-demo-workflow.md](customer-live-demo-workflow.md)
- Error behavior: [customer-error-handling.md](customer-error-handling.md)
- Full capability classification: [CUSTOMER_HANDOVER_GAP_ANALYSIS.md](CUSTOMER_HANDOVER_GAP_ANALYSIS.md)
