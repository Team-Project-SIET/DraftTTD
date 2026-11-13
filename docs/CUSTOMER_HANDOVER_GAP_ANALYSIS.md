# Customer handover gap analysis — 2026-11-12

**Status:** FINAL REVIEWED DRAFT for operator commit — uncommitted; the commit and
any push are operator decisions. Reviewed and finalized by the 2026-11-12 handover
session against the repository state at HEAD `90ebadb`.
**Provenance:** produced by the 2026-11-12 handover-audit session. Offline and read-only;
no OpenTTD launch, no AdminPort connection, no staging, no signing, no claim, no evidence
mutation, no application-code change, no commit, no push during the audit.
**Trust order:** retained `artifacts/` evidence > ledgers (`EVIDENCE_INDEX.md`, `AI_HANDOFF.md`,
`TASKS.md`) > docs. FAILED terminal results are never relabeled; consumed attempts stay
consumed; UNKNOWNs are preserved, never filled.

## 1. Audit snapshot (verified against the repository, not assumed)

- Branch `miles/fright-delivery`, HEAD `90ebadb` (the E207 docs commit).
- Working tree carries **uncommitted** Phase D M0 work: the quality-floor dispositions
  (ticket 10 — repair ×4 + typed seal ×1), the full-suite command of record and its
  post-disposition rerun addenda in `REPRODUCE.md` (ticket 11), plus the untracked
  Phase D scope proposal (`docs/phase-d-scope-proposal-2026-11-12.md`,
  `docs/specs/phase-d-scope.md`) and the `.scratch/phase-d-scope/` tracker.
- **EVIDENCE_INDEX row E208 is prepared (uncommitted)** for the post-disposition
  full-suite rerun (6327 passed / 0 failed / 55 skipped, exit 0 — ticket 11 answer),
  with its dated addendum paragraph. E207 (first baseline of record: 57 failed /
  54 skipped, exit 1 at `74c8152`) is **not relabeled** and remains the first
  full-suite baseline of record. The transient capture
  `/tmp/opencode/quality-floor-rerun-2026-11-12/pytest-full.out` exists on disk
  (final line `PYTEST_EXIT_CODE=0`) at audit time; it is transient, not retained
  evidence — the retained proof rides the REPRODUCE.md addenda and the prepared
  E208 row.
- The repo-root file named `--version` is preserved unexecuted (accidental artifact,
  kept for integrity).
- Phase A: **TERMINALLY CLOSED** (E127, `docs/poc-completion-declaration-2026-11-06.md`)
  carrying two open findings: **E36** (delivered-class) and **E114** (twin-vs-native
  cross-reality divergence, UNKNOWN).
- Phase B: **FULLY CLOSED** (T-030 → T-034, E182–E195), including five complete native
  economy years 1951–1955 observed through the canonical continuous pipeline
  (`CANONICAL_FIVE_YEAR_CONTINUOUS_VERIFIED`, E195).
- Phase C: terminal statement of record is **`INCOMPLETE_EVIDENCE`** (E142, re-confirmed
  E204). FD-C-2 attempts 1–7 each ended in a typed terminal (E150–E157, E197); the
  random-world battery was consumed with its bar honestly **not met** (E198–E201).
- Phase D: exists only via the operator-approved M0 of the scope proposal
  (2026-11-12). M0 covers offline work under the decision-ticket graph only — it
  grants **no runtime authority of any kind**. Tickets 04/07/09/10/11 resolved;
  12–23 ready-for-agent (offline backbone); 24–29 ready-for-human (native rounds,
  each its own grant; total native budget in the proposal ≤ 8).

## 2. Classification

### 2.1 Verified and deliverable (supported by valid retained evidence)

| Capability | Evidence |
| --- | --- |
| Stable fixed-demo native run: 3 services, 60 coal, £1,022 revenue, spectator mode, P07 evaluation | E1 |
| Canonical create/reload correspondence | E2 |
| Standalone native freight delivery (fixed demo world): 20 units, verified receipt and certified cleanup | README capability table; attempt-4 retained evidence |
| Planner-driven native delivery: qualified observation → P08 → P05 → ExecutionPlan → 20 coal units delivered with attributed payment | README capability table; attempt-9 retained evidence |
| Two P05-selected services delivered in one native world | Attempt 12 evidence (README capability table) |
| Native road/station/depot construction on the corridor, exactly the reviewed v3 scope | E35 (D4 PROVEN) |
| D5 A0 survey and A1 corridor extension, with receipt-bound after-save `3748e00c…5420bd` | E40 / E44 (VERIFIED) |
| Acceptance census lifecycle, read-only, `SURVEY_COMPLETION_VERIFIED` | E49 |
| Corridor cargo-flow native ladder execution: full 25/26-exchange ladders ran true end-to-end, verified true, zero halts | E116/E117 (round 6), E124 (round 7), E133 (candidate 9) — **execution machinery proven; delivery verdict of record stays `CARGOFLOW2_LOADED_NEVER_DELIVERED`** |
| Funds taxonomy of record and zero-residual funds reconciliation across all observed instants | ADR-0001 (E125), E126/E134 |
| P07 post-play evaluation, run history, charts, evidence-aware analytics (bottlenecks, advisories, comparisons) | E126 + analytics record; offline replay of retained attempts |
| Five complete native economy years (1951–1955) with monthly/quarterly receipts and per-vehicle telemetry | E195 (Phase B closed, E182–E195) |
| GUI capability probes (T-035/T-036) | E170 / E180 (VERIFIED) |
| Consolidated CAPEX observed: £8,858; revenue observed per attempt | E194 (OPEX/ROI remain UNKNOWN — see 2.3) |
| Regression quality floor: full suite green post-disposition (6327 passed / 0 failed / 55 skipped, exit 0), full-suite command of record frozen into `REPRODUCE.md` | ticket 10 + ticket 11 answers — **uncommitted; needs operator commit + evidence row** |
| Runtime pins: binary `276d5b69…1904c`, OpenGFX `43a0c1da…03be`, protected save `51e45689…1297eb` | pin records of record |

### 2.2 Incomplete (implementation or verification unfinished)

| Item | State of record |
| --- | --- |
| **E36 — delivered-class finding** | OPEN by its own rule. Closes only when a genuinely competing executable route carries **native DELIVERED receipts**. No such receipt exists in the corridor lineage: rounds 6, 7 and candidate 9 all terminated `NATIVE_CARGOFLOW2_COMPLETE` with verdict `CARGOFLOW2_LOADED_NEVER_DELIVERED` (`unloadings []`, bay acceptance never moved — E124, E133, E134). Root cause diagnosed: the plan's ladder composition; the loaded return missed the final stand by 2–3 days; delivered-arm (2,2) extension still did not unload (E128, E133, E134). |
| **FD-C-2 / Phase C** | Terminal statement of record `INCOMPLETE_EVIDENCE` (E142, re-confirmed E204). Attempts 1–7 consumed with typed terminals; the random-world battery consumed, bar not met (E198–E201). Nothing is relabeled. |
| **Random-world delivery** | The seed-7 plan was the first on-file random-world plan long enough to expose the observation-window boundary; the designed gate fired as designed (no code or capture defect — AI_HANDOFF terminal analysis). Requirements-evidence-matrix row: random-world service execution stands on FAILED typed terminals. Any window redesign is a fresh operator decision. |
| **Phase D M0/M1 booking** | Prepared as EVIDENCE_INDEX addendum + row **E208** (uncommitted): M0 approval of record cited from the scope proposal; the dispositions and the green rerun recorded with exact command, counts, exit code, and capture identity. Until committed, the green state is not yet committed evidence of record; E207 stands untouched either way. |
| **Phase D M2 backbone (tickets 12–23)** | Ready-for-agent, not started. Offline only. |
| **Qualification Attempt 2** | Overall post-run acceptance remains FAILED (README capability table). Preserved as evidence. |
| **E114 twin divergence** | Cross-reality UNKNOWN preserved (twin 484,775 vs native 484,764/769/770). |
| **GUI product scope** | Probes VERIFIED (E170/E180), but the GUI product scope owed by E148/E149 is unbuilt. |

### 2.3 Unproven (no sufficient evidence exists — must not be claimed)

- **Corridor native freight DELIVERED receipts** — none exist anywhere in the corridor
  lineage (E36 rule; E124/E133/E134).
- **Random-world end-to-end delivery cycle** — battery bar not met (E198–E201);
  observation-window boundary documented, not redesigned.
- **OPEX, ROI, profitability** — README honesty line (851–855): "Full OPEX, ROI, and
  profitability remain unknown. No parameters change automatically, and no retraining
  or native execution occurs." ADR-0001 D5: revenue is never reported as profit.
  CAPEX £8,858 and revenues are OBSERVED; margins are DERIVED; OPEX truth class is
  UNKNOWN (E194).
- **Paid shared-asset reuse** — unproven (attempt-12 record).
- **Closed-loop optimization** — outside the demonstrated native MVP (README :174).
- **Per-cycle PnL record** — Phase D ticket 23, not built.

### 2.4 Known limitation (explicitly outside the demonstrated scope)

- Arbitrary maps, rail delivery, concurrent native vehicles, closed-loop optimization —
  README :174 "Outside the demonstrated native MVP".
- Fixed-corridor-only and M8 limitations standing with E36 (E36-a addendum).
- P05/P07/P08 planning integration is evidenced on the **once-verified seed-7 slice**
  plus the fixed-demo attempts; no broader-world statistical claim is supported.
- Offline "alternatives" analyses apply a uniform transferred error ratio — an explicit
  transfer assumption, one observation, no calibrated prediction (README 844–849).

### 2.5 Future enhancement (not required for the agreed MVP handover)

- Phase D optional workstreams as operator-gated options: WS-D2 rail offline build
  scope; WS-D3 loop/census integration; WS-D4 observation window v2 (tickets 12–15,
  then 24–26); delivered-class candidate/contingency rounds (tickets 16–17, 27–28);
  GUI capstone round (ticket 29).
- Per-cycle PnL record and richer OPEX instrumentation (ticket 23).
- Any successor work beyond the PoC declaration needs its own explicit authorization
  (E127 terminal rule).

### 2.6 Operator decision required (cannot proceed without authorization)

1. **Commit and book the uncommitted M0 work** — or decide to hold it uncommitted and
   say so; an uncommitted green rerun is not evidence of record. Requires an
   EVIDENCE_INDEX addendum row for the post-disposition rerun (E207 stays untouched).
2. **Phase D native rounds** — tickets 24–26 (battery seeds 11/12/13), 27–28
   (delivered-class candidate + contingency), 29 (GUI capstone). Each round its own
   explicit grant; the proposal's total budget ≤ 8 launches. **Not approved by this
   audit; approval is neither implied nor recommended as mandatory for handover.**
3. **E36 disposition for handover** — keep it open with written disclosure (the
   recommended default, zero native cost), or authorize delivered-class rounds 27/28
   (native, gated).
4. **Observation-window redesign** — fresh operator decision with fresh grants where
   native; not an MVP item.
5. **GUI capstone scope** — whether the customer handover includes any GUI surface
   beyond the verified probes.
6. **Publication of this handover package** — committing the draft documents and any
   push remains a separate operator decision.

## 3. What the customer materials must never claim

Delivery in the corridor lineage, random-world delivery capability, optimization
improvement demonstrated natively, profitability or OPEX figures, paid shared-asset
reuse, closed-loop optimization, arbitrary-map or rail capability. Historical FAILED
terminals and the `INCOMPLETE_EVIDENCE` Phase C statement are cited as-is. E36 and
FD-C-2 are open findings, not closed ones.

## 4. Bottom line

The fixed-demo MVP demonstration is natively verified end-to-end; corridor
construction and census are PROVEN/VERIFIED; the planning-to-execution pipeline is
verified on the demonstrated slice; the regression floor is green (pending booking).
What is owed is disclosure, not engineering: corridor DELIVERED receipts do not exist
(E36), Phase C stands `INCOMPLETE_EVIDENCE`, random-world delivery is unproven, and
OPEX/ROI are UNKNOWN. The prioritized closure of that disclosure debt is in
`PROJECT_CLOSURE_PLAN.md`.
