# Customer presentation index — 2026-11-13

This index maps the ten customer-requested documentation topics to the documents
that cover them. It is the entry point for a customer presentation; every linked
document states its own scope and status vocabulary. Offline and read-only: this
index and the documents it lists contain no runtime authorization of any kind.

**Branch of record:** `miles/fright-delivery`, HEAD `90ebadb` (docs of record carry
uncommitted Phase D M0/M1 state — see §2). **Primary runtime target:** OpenTTD
15.3 Linux amd64; historical OpenTTD 13.4 evidence is regression history only and
is never presented as 15.3 proof.

## 1. Status vocabulary used across these documents

| Label | Meaning |
| --- | --- |
| VERIFIED / PROVEN | Supported by retained native evidence, within the stated scope. Scope limits always accompany the claim. |
| CONTROLLED | Verified offline (tests, replay, derivation). Never a substitute for native proof. |
| PREPARED / PLANNED | Implemented or designed, awaiting explicitly authorized native qualification. |
| PARTIAL | Incomplete acceptance; partial evidence is retained verbatim. |
| FAILED | Immutable consumed outcome. Never relabeled. |
| UNKNOWN | Missing fact. Never invented. |
| NOT IMPLEMENTED | No code on the branch (e.g., rail delivery). |

## 2. Topic map

| # | Topic | Document(s) |
| --- | --- | --- |
| 1 | Current working scope and verified capabilities | [README.md](../README.md) (Quick start, capability table, customer handover status), [CUSTOMER_HANDOVER_GAP_ANALYSIS.md](CUSTOMER_HANDOVER_GAP_ANALYSIS.md) §2, [customer-use-cases.md](customer-use-cases.md) |
| 2 | System architecture overview | [customer-architecture.md](customer-architecture.md), [CONTEXT.md](../CONTEXT.md) §5 (architecture authority), [AI_HANDOFF.md](../AI_HANDOFF.md) architecture map |
| 3 | UML class diagram and object relationships | [customer-uml-classes.md](customer-uml-classes.md) |
| 4 | SOLID, high cohesion and low coupling with source examples | [customer-solid-analysis.md](customer-solid-analysis.md) |
| 5 | Live demo workflow and readiness | [customer-live-demo-workflow.md](customer-live-demo-workflow.md), [REPRODUCE.md](../REPRODUCE.md) (commands of record), [examples/openttd-demo/README.md](../examples/openttd-demo/README.md) |
| 6 | Main use cases supported by current capabilities | [customer-use-cases.md](customer-use-cases.md) |
| 7 | Error handling and edge cases | [customer-error-handling.md](customer-error-handling.md), README troubleshooting section |
| 8 | Future development opportunities | [customer-future-development.md](customer-future-development.md), [phase-d-scope-proposal-2026-11-12.md](phase-d-scope-proposal-2026-11-12.md) (scope of record) |
| 9 | Security and threat analysis (DFD, misuse cases, asset inventory, security requirements, risk register, secure coding, refactoring) | [customer-security-threat-analysis.md](customer-security-threat-analysis.md), [secure-admin-transport.md](secure-admin-transport.md) (transport design of record) |
| 10 | Requirements traceability matrix | [requirements-traceability-matrix.md](requirements-traceability-matrix.md), [requirements-evidence-matrix.md](requirements-evidence-matrix.md) (requirements → evidence view of record) |

## 3. Top-level summary of record (one paragraph, evidence-anchored)

The natively verified fixed-demo MVP is: one isolated OpenTTD 15.3 server, one
graphical spectator, one encrypted Admin connection; three P05-selected services
built and driven by the Python planner, 60 coal delivered and £1,022 revenue with
fresh P07 reporting, replay and certified cleanup (E1). Delivery capability is
individually proven by Attempt 4 (standalone, 20 units), Attempt 9 (planner-driven,
attributed payment) and Attempt 12/14/17 (two and three serial services in one
world; Attempt 17 = 60 coal, £1,018 revenue, £28,459 CAPEX). Corridor road/station
construction is PROVEN for exactly the reviewed v3 scope (E35) and the D5 survey,
extension and census chain is VERIFIED (E40, E44, E49). Five complete native
economy years (1951–1955) were observed through the canonical continuous pipeline
(E195, Phase B closed). What is **not** proven is disclosed, not hidden: corridor
DELIVERED receipts do not exist (E36 open; every corridor cargo-flow round ended
`CARGOFLOW2_LOADED_NEVER_DELIVERED`); random-world service execution stands on
FAILED typed terminals and delivery is UNPROVEN (Phase C `INCOMPLETE_EVIDENCE`,
E142/E204); OPEX, ROI and profitability remain UNKNOWN and revenue is never
reported as profit (ADR-0001 decision D5); concurrency, paid shared-asset reuse
and closed-loop optimization are unproven. Full classification:
[CUSTOMER_HANDOVER_GAP_ANALYSIS.md](CUSTOMER_HANDOVER_GAP_ANALYSIS.md).

## 4. Evidence system pointers

- **Evidence rows E1–E208:** [EVIDENCE_INDEX.md](../EVIDENCE_INDEX.md). Retained
  bytes live under git-ignored `artifacts/` and are transfer-only; a clone without
  them reports missing evidence rather than a code defect.
- **Ledgers:** [AI_HANDOFF.md](../AI_HANDOFF.md), [TASKS.md](../TASKS.md),
  [REPRODUCE.md](../REPRODUCE.md) (commands of record).
- **Trust order:** retained `artifacts/` evidence > ledgers > docs. FAILED terminals
  are never relabeled; consumed attempts stay consumed; UNKNOWNs are preserved.
- **Working-tree note:** the Phase D M0/M1 booking (green full-suite rerun,
  6327 passed / 55 skipped / 0 failed, exit 0 — E208) is prepared but uncommitted
  at the time of writing; E207 (57 failed / 54 skipped baseline) stands unchanged.
  Commit and push remain operator decisions.

## 5. Presentation boundaries (what must never be claimed)

Per [PROJECT_CLOSURE_PLAN.md](PROJECT_CLOSURE_PLAN.md) §3.2: no corridor DELIVERED
receipts exist; random-world delivery is unproven; no OPEX/ROI/profit figures; no
paid shared-asset reuse, closed-loop optimization, arbitrary-map or rail capability;
revenue is never profit; corridor construction never implies cargo delivery; Phase D
native rounds are optional operator-gated work, not handover blockers. The
`docs/examsrs.md` file is an unrelated course template and is not part of this
system's documentation.
