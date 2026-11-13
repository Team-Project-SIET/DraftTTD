# Project closure plan — 2026-11-12

**Status:** FINAL REVIEWED DRAFT for operator commit — uncommitted. Plans nothing
that runs without its own explicit operator grant. Every native item below is marked
**NATIVE — GRANT REQUIRED** and stops at the decision unless and until the operator
approves it in-session.
**Safety of record:** no OpenTTD launch, no AdminPort connection, no staging, no
signing, no claim, no retry of a consumed attempt, no evidence regeneration, no
sealed-`artifacts/` mutation, no push. FAILED terminals and `INCOMPLETE_EVIDENCE`
statements are never relabeled. Phase A–C closure records and every UNKNOWN are preserved.
**Companion documents:** `CUSTOMER_HANDOVER_GAP_ANALYSIS.md` (classification),
`docs/phase-d-scope-proposal-2026-11-12.md` (Phase D scope of record).

## 1. Mandatory MVP closure vs optional Phase D workstreams

The agreed MVP handover is: a truthful package around the **natively verified
fixed-demo demonstration** (planner pipeline P08 → P05 → ExecutionPlan → native
freight delivery with attributed payment), the **proven corridor construction and
census chain** (D4/D5), the **closed Phase B economy pipeline**, and honest disclosure
of the open findings (E36, FD-C-2, random-world, OPEX/ROI).

**No Phase D ticket is a mandatory customer-delivery requirement.** Phase D is the
operator-approved optional continuation (M0 granted 2026-11-12; M1 quality floor
already passed). Its native rounds (tickets 24–29) are options, not handover blockers.

## 2. Prioritized plan

### P0 — blockers to honest customer handover (offline only, no grants)

| # | Item | Current status | Required evidence | Dependencies | Verification | Deliverable |
| --- | --- | --- | --- | --- | --- | --- |
| P0-1 | Book the uncommitted M0 state | **Prepared (uncommitted):** EVIDENCE_INDEX dated addendum + row E208 drafted; REPRODUCE.md's duplicate quality-floor addenda consolidated into one section carrying the M0 approval pointer, the exact command, counts, exit code, and capture identity | One commit; the prepared E208 row records the green rerun (6327/0/55, exit 0) **without** touching E207 | Operator commit decision | `git status` clean of M0 debt; index row present; E207 row byte-identical | M0/M1 state of record |
| P0-2 | Publish the handover disclosure set | Draft (this pair of documents) | Operator-committed `CUSTOMER_HANDOVER_GAP_ANALYSIS.md` + `PROJECT_CLOSURE_PLAN.md` + handover package assembled from §3 | P0-1, operator review | Reviewer reads package against evidence index | Customer-ready disclosure |
| P0-3 | Claims-hygiene sweep of customer-facing docs | README honesty boundaries already correct (:174, 851–855); sweep for any stale sentence contradicting the matrix | Documented sweep result | None | grep for claim vocabulary (profit/OPEX/delivered/random-world) against §3 of the gap analysis | Sweep record |
| P0-4 | Reproducible demonstration freeze | Commands of record exist in `REPRODUCE.md`; demo scenario not yet packaged for a customer | The demo runbook (§3.4) citing retained evidence for every claimed number | None | Offline reviewer can replay every cited artifact reference | Demo runbook |

All P0 items are **offline-sufficient**; no native execution, no grant. Historical
retained artifacts are read-only throughout.

### P1 — essential technical closure (offline unless noted)

| # | Item | Current status | Required evidence | Dependencies | Verification | Native? | Deliverable |
| --- | --- | --- | --- | --- | --- | --- | --- |
| P1-1 | E36 disposition for handover | OPEN by rule; zero corridor DELIVERED receipts (E124/E133/E134); **disclose-only statement prepared — §3.1** | The §3.1 statement, citing the finding, its closure rule, the diagnosis of record (E128), and the fixed-demo lineage distinction | Operator adopts §3.1 as published text | The statement cites E36/E124/E128/E133/E134 verbatim | Disclose-only: no. Rounds 27/28 remain optional operator choices, not prepared and not required | E36 disclosure section |
| P1-2 | FD-C-2 / Phase C terminal statement publication | `INCOMPLETE_EVIDENCE` stands (E142/E204); attempts 1–7 typed terminals (E150–E157, E197); battery bar not met (E198–E201) | Disclosure text citing the terminal rows verbatim | None | Row-by-row citation check | No | Phase C disclosure section |
| P1-3 | Regression gate of record committed | Green rerun exists uncommitted (ticket 11) | P0-1 commit + the frozen full-suite command and three-point cadence in `REPRODUCE.md` | P0-1 | One more full-suite run only if the operator wants a committed-run receipt; otherwise the existing capture is cited | No | Green-gate citation |
| P1-4 | Installation and operation runbook | README carries the commands; operator-facing runbook not assembled | A runbook: env pins (`OPENTTD_BINARY`, `OPENTTD_OPENGFX_ARCHIVE`, pinned SHAs), `uv sync --locked`, offline commands (`plan`/`check`/`report`/`compare`), demo invocation, what each exit means | None | Follow-the-runbook dry pass (offline steps only) | No | Operator runbook |

### P2 — documentation, demonstration, operational readiness

| # | Item | Current status | Required evidence | Dependencies | Verification | Native? | Deliverable |
| --- | --- | --- | --- | --- | --- | --- | --- |
| P2-1 | Customer demo scenario | Evidence retained; live demo not scheduled | Runbook walking the retained E1 demo figures, the corridor construction chain (E35 → E40/E44 → E49), and Phase B economy receipts (E195) | P0-4 | Walkthrough against retained bytes | **NATIVE — GRANT REQUIRED** only if the customer wants a fresh live run; the packaged demo uses retained evidence | Demo script |
| P2-2 | Handover package assembly | Sections listed in §3; drafts possible now | Committed package | P0-1, P0-2, P1-1, P1-2 | Acceptance checklist §4 signed off item-by-item | No | Handover package |
| P2-3 | Version/release-notes discipline | Recorded by ticket 11 (uncommitted) | The discipline section lands with P0-1 | P0-1 | Section present in `REPRODUCE.md` of record | No | Release notes convention |
| P2-4 | Customer acceptance session | Not scheduled | Checklist §4 countersigned by the customer | P2-2 | Each checklist item initialed with its evidence citation | Customer's choice | Signed checklist |

### P3 — deferred / future enhancements (not handover requirements)

- Phase D native rounds: battery seeds 11/12/13 (tickets 24–26), delivered-class
  candidate + contingency rounds (27–28), GUI capstone (29) — **each NATIVE — GRANT
  REQUIRED**, budget ≤ 8 total per the proposal.
- Phase D offline backbone M2 (tickets 12–23): window v2 budget field, capture
  scheduler capacity, census integration surface, backbone offline bar,
  delivered-class diagnosis/fix, rail tracer/orders/lifecycle/planning depth, typed
  feedback implementation, receipt-shape audit, per-cycle PnL record.
- Observation-window redesign (fresh operator decision; corridor-lineage deliveries
  are not relabeled by it — AI_HANDOFF terminal analysis).
- Closed-loop optimization, arbitrary maps, rail delivery, concurrent native
  vehicles, paid shared-asset reuse proof, OPEX instrumentation to UNKNOWN → OBSERVED.

## 3. Proposed customer handover package

1. **Executive summary** — what was demonstrated natively (fixed-demo delivery chain,
   corridor construction + census, five-year economy pipeline), what stands open
   (E36, FD-C-2, random-world, OPEX/ROI), and the one-line verdict vocabulary
   (VERIFIED / PROVEN / PREPARED / PARTIAL / FAILED / UNKNOWN — AI_HANDOFF definitions).
2. **System architecture and component responsibilities** — CLI → isolated OpenTTD
   runtime → qualified observations → P08 bounded road candidates → P05 CP-SAT
   selection → ExecutionPlan → freight compiler/executor → encrypted AdminPort +
   GameScript bridge → independent readback → retained receipts → P07 offline
   reporting. Planning in Python; GameScript executes company commands only under
   `GSCompanyMode`; readback independent of execution.
3. **Verified feature matrix** — the table in §2.1 of the gap analysis, verbatim.
4. **Reproducible demonstration scenario** — the P0-4/P2-1 runbook; every figure
   cited to its retained artifact (E1 demo figures; corridor chain E35/E40/E44/E49;
   ladder executions E116/E117/E124/E133; economy years E195).
5. **Test and native evidence references** — `EVIDENCE_INDEX.md` E1–E207;
   `REPRODUCE.md` commands of record including the full-suite command and its green
   rerun once committed (P0-1); the 32 `LAUNCH-CONSUMED.json` markers and 40/40 seal
   sweep of record (E127).
6. **Known limitations and unresolved findings** — §2.2–§2.4 of the gap analysis,
   verbatim; E36 and E114 carried open by the PoC declaration; Phase C
   `INCOMPLETE_EVIDENCE` quoted.
7. **Installation and operation instructions** — the P1-4 runbook.
8. **Customer acceptance checklist** — §4 below.
9. **Future development roadmap** — Phase D scope proposal (workstreams WS-D1..D6,
   operator-gated), the P3 list, and the E127 rule that successor work needs its own
   authorization.

### 3.1 E36 disclosure statement (customer-facing, verbatim-ready)

> **E36 — corridor delivered-class finding. Status: OPEN, disclosed.**
>
> In the corridor lineage, no native freight DELIVERED receipt exists. Every
> corridor cargo-flow round executed natively — rounds 6, 7, and candidate 9 —
> terminated `NATIVE_CARGOFLOW2_COMPLETE` with the verdict
> `CARGOFLOW2_LOADED_NEVER_DELIVERED`: cargo was loaded and carried to the
> destination bay, but no unloaded amount reached the bay acceptance chain inside
> the plan's observation ladder (E124, E133, E134). The diagnosis of record
> attributes this to the plan's ladder composition, not to any world or machinery
> defect (E128); the acceptance machinery itself is present and typed
> (`CARGOFLOW2_DELIVERY_VERIFIED` class). The fixed-corridor-only and M8
> limitations stand with this finding (E36-a).
>
> **What would close it:** only a genuinely competing executable route carrying
> valid native DELIVERED receipts. This closure rule is unchanged by the handover;
> no evidence was relabeled and no acceptance criterion was redefined.
>
> **Related disclosures:** FD-C-2 and Phase C stand `INCOMPLETE_EVIDENCE`
> (E142, re-confirmed E204); attempts 1–7 ended in typed terminals (E150–E157,
> E197) and the random-world battery bar was not met (E198–E201). Random-world
> end-to-end delivery is therefore UNPROVEN. OPEX, ROI, and profitability remain
> UNKNOWN (ADR-0001 decision D5: revenue is never reported as profit; README
> honesty lines 851–855). Attempt 4 and Attempt 9 delivery proofs belong to the
> fixed-demo lineage and are presented as such. Corridor construction (E35)
> proves infrastructure build, not cargo delivery.

### 3.2 Required-disclosures register (must appear in the published package)

1. E36 remains OPEN: no corridor DELIVERED receipts exist.
2. FD-C-2 remains `INCOMPLETE_EVIDENCE`; Phase C's terminal statement is unchanged.
3. Random-world delivery remains UNPROVEN (battery bar not met, E198–E201).
4. OPEX / ROI / profit remain UNKNOWN; revenue never proves profit (ADR-0001 D5).
5. GUI product scope remains a separate decision; only the probes are VERIFIED
   (E170/E180) and the E148/E149 scope debt is unbuilt.
6. Phase D native rounds (tickets 24–29) are optional operator-gated future work,
   not automatic handover requirements.
7. Corridor construction (E35 PROVEN) never implies cargo delivery.

## 4. Proposed customer acceptance checklist

Each item is initialed only when its evidence citation is shown to the customer.

- [ ] Stable-demo native demonstration figures reproduced/retained per E1.
- [ ] Planner-driven delivery chain (P08 → P05 → native delivery, attributed payment) shown per the attempt-9 record.
- [ ] Corridor construction PROVEN scope walked per E35; extension per E44 (after-save `3748e00c…5420bd`); census per E49.
- [ ] Corridor ladder executions shown with their terminal verdicts verbatim (`CARGOFLOW2_LOADED_NEVER_DELIVERED`) — presented as execution evidence, not delivery evidence.
- [ ] Five-year economy receipts (E195) available for inspection.
- [ ] P07 analytics outputs available offline per E126.
- [ ] Full-suite regression command of record and its result shown (6327/0/55, exit 0 — post-disposition rerun, cited after P0-1; E207 baseline disclosed as-is).
- [ ] Open findings disclosed: E36, E114, FD-C-2 `INCOMPLETE_EVIDENCE`, random-world battery bar not met, Attempt-2 qualification FAILED.
- [ ] Honesty boundaries acknowledged: OPEX/ROI UNKNOWN; no optimization-improvement claim; no random-world claim; no rail/arbitrary-map claim.
- [ ] Pins disclosed: binary `276d5b69…1904c`, OpenGFX `43a0c1da…03be`, protected save `51e45689…1297eb`; other versions unsupported.
- [ ] Runtime boundary acknowledged: offline commands need no grant; every native action needs a fresh explicit authorization.

## 5. Operator decisions required next

1. **Commit M0** (P0-1) — approve one commit of the 12 modified files + untracked
   Phase D docs/tracker, plus one EVIDENCE_INDEX addendum row for the green rerun.
2. **Publish the handover package** (P0-2) — approve committing these draft documents
   after review; push remains a separate decision.
3. **E36 disposition** — disclose-only statement §3.1 is prepared as the published
   position; adopting it (recommended) requires no native action. Delivered-class
   rounds 27/28 remain available as separate optional operator decisions
   (**NATIVE — GRANT REQUIRED**); neither is required for handover.
4. **Phase D native rounds** — separately approve, defer, or decline tickets 24–29;
   none is required for handover.
5. **GUI capstone scope** — decide whether any GUI surface enters the handover beyond
   the verified probes (E148/E149 debt).
6. **Customer live demo** — decide whether the demonstration uses retained evidence
   only (offline, no grant) or a fresh native run (**NATIVE — GRANT REQUIRED**).

## 6. Verdict

**CONDITIONALLY READY WITH DISCLOSED LIMITATIONS.**

Justification, by evidence:

- **Ready side:** the fixed-demo MVP chain is natively verified end-to-end (E1; the
  attempt-4/9/12 delivery records); corridor construction is PROVEN (E35) with the
  A1 extension and census VERIFIED (E40/E44, E49); Phase B is fully closed with five
  native economy years observed (E182–E195); the planning pipeline (P08 → P05 →
  ExecutionPlan → delivery) is verified on the demonstrated slice; the funds taxonomy
  and zero-residual reconciliation discipline hold across every observed instant
  (ADR-0001, E126/E134); the regression floor is green post-disposition (ticket 11).
- **Conditions (all disclosure, not engineering):** E36 is open — **no corridor
  DELIVERED receipt exists** (E124/E133/E134 terminal verdicts verbatim); Phase C
  stands `INCOMPLETE_EVIDENCE` (E142/E204) and the random-world battery bar was not
  met (E198–E201); OPEX/ROI/profitability are UNKNOWN (README 851–855, E194, ADR-0001
  D5); paid shared-asset reuse and closed-loop optimization are unproven; the green
  regression rerun is uncommitted, so the handover's strongest offline fact is not
  yet evidence of record; the GUI product scope owed by E148/E149 is unbuilt.
- **Not READY** because those open findings and the unbooked M0 state are material to
  any honest customer claim; the package must disclose them before handover.
- **READY** is unreachable without either closing E36 via a genuinely competing
  executable route carrying native DELIVERED receipts (native rounds, operator-gated)
  or the customer accepting corridor delivery as out of scope — the operator's call,
  not this audit's.

The disclose-only E36 statement (§3.1) and the prepared E208 booking remove the two
preparation gaps this session could close offline; the remaining conditions are
customer-facing disclosures, not engineering debt. The verdict stands.

This document is an audit-and-planning artifact. It approves nothing. Work stops here
pending operator review.

## 7. Proposed commit plan (nothing committed — operator approval required)

Branch confirmed `miles/fright-delivery` at HEAD `90ebadb`. `git diff --check` clean
(run at preparation time; re-run before each commit). Sealed `artifacts/` untouched —
no artifact path appears in `git status`; `artifacts/` is git-ignored and transfer-only
by the standing rule.

Three proposed commits, in order:

1. **Phase D M0/M1 evidence + quality floor** — `REPRODUCE.md` (consolidated
   addendum), the 8 test/fixture files
   (`tests/fixtures/cargo_catalog_checkpoint/runtime-identity.json`,
   `tests/fixtures/p08_controlled_e2e/{accepted-digests,correspondence,manifest,recipe,supplemental,verification}.json`,
   `tests/test_classification_execution.py`, `tests/test_corridor_cargoflow2_vm.py`,
   `tests/test_qualification_preparation.py`,
   `tests/test_terrain_classification_preparation.py`,
   `tests/test_world_correspondence.py`), and `EVIDENCE_INDEX.md` (dated addendum +
   row E208). Message intent: book M0/M1 — dispositions + green full-suite rerun,
   E207 preserved.
2. **Phase D scope of record** — `docs/phase-d-scope-proposal-2026-11-12.md`,
   `docs/specs/phase-d-scope.md`, `.scratch/phase-d-scope/` (map, 29 tickets,
   2 research notes). Message intent: land the approved Phase D scope documents.
3. **Customer handover package** — `docs/CUSTOMER_HANDOVER_GAP_ANALYSIS.md`,
   `docs/PROJECT_CLOSURE_PLAN.md`. Message intent: handover gap analysis + closure
   plan, verdict CONDITIONALLY READY WITH DISCLOSED LIMITATIONS.

Commit 2 and commit 3 may be swapped by operator preference; commit 1 should land
first so the handover package cites a committed E208. Push is a separate decision,
not included in this plan.
