# Phase D discovery — what exists after Phase C (offline, 2026-11-12)

Round scope: offline discovery only — reading the on-file record, no
OpenTTD launch, no AdminPort connection, no grant consumed, no evidence
byte mutated, no push; ONE docs commit. This record invents no tickets,
no phases, and no definitions of done. Head of record at round start:
`09edf35`.

## 1. The scope finding of record

**No Phase D exists on file.** Verified by exhaustive grep over `docs/`,
`.scratch/`, and root ledgers: the only "Phase D" strings in the
repository are the E202 statements recording its absence. The roadmap's
last phase is §4 Phase C — Random World (:165-193); §5-§9 are the
decision-gates ledger, dependency graph, risk register, invariants and
scope disclaimers. The tracker records (E202): "No Phase D exists on
file (roadmap §4 is the last phase); any successor scope under the
three undefined headings ('Closed-Loop Optimization', 'Productization',
'Final Release') requires an operator decision first — nothing
invented." The three headings appear **0 times** across
roadmap-and-scope-2026-11-05.md, requirements-evidence-matrix.md,
specs/ramrom-product.md and poc-ticket-backlog-2026-11-07.md; no literal
"Definition of Done" phrase exists anywhere (tracker, "Phases with no
definitions on file").

**Consequence:** a "Phase D" can only come into existence by an
operator decision — either a scope definition under one of the three
headings, or a named continuation of the on-file open items. This
discovery record maps what the on-file record already offers; it
defines nothing.

## 2. Successor-scope anchors already on file (pointers, not scope)

- **README :174 feature-inventory boundary:** "Arbitrary maps, rail
  delivery, concurrent native vehicles, closed-loop optimization |
  Outside the demonstrated native MVP." The nearest on-file statement
  of what lies beyond the demonstrated MVP.
- **README :853-855 honesty boundaries:** "Comparisons do not establish
  native feasibility or demonstrated optimization improvement. Full
  OPEX, ROI, and profitability remain unknown. No parameters change
  automatically, and no retraining or native execution occurs."
- **Roadmap §7 risk register:** launch-gate-only defect risk (resolved
  in practice by Phase B's four verified launches), E111 residuals
  (recorded UNKNOWN, none guessed), finance truth (see §3 below), clone
  drift, and the two-authorities rule ("if any ledger and this document
  disagree on live status, the ledger wins; file an erratum here
  instead of rewriting there").
- **Roadmap §8 invariants:** `artifacts/` immutable, transfer-only,
  never regenerated; consumed attempts stay consumed; native runs
  operator-gated, one launch, no retries; `CONTEXT.md` byte-pinned;
  GameScript executes only commands; nothing relabeled.
- **Project-wide Definition of Done** (tracker §3, RECONSTRUCTED — not
  quoted as a whole): items 1–4 are DONE (E182–E195 native closure;
  E197; E198–E201), item 5 is E36's own rule (stays open), item 6 is
  recorded (E202, INCOMPLETE_EVIDENCE). The reconstructed conjunction
  is fully adjudicated.

## 3. The decision-gates ledger is fully discharged

Roadmap §5 gates, disposition as of this round:

| Gate | On-file state this round |
|---|---|
| DG-1 | ✅ approved + executed offline as T-009 (roadmap's own text) |
| DG-2..DG-5 | per-round, in-session — no round pending |
| DG-6 | in place (recorded discipline) |
| DG-7 | **Resolved:** ADR-0001 funds taxonomy of record landed CONFIRMED DECISION OF RECORD 2026-11-06 (E125, operator-adopted via the explicit in-session gate option "Confirm decision of record"; supersession-only thereafter) and T-032/T-033 consumed it (E193/E194: consolidated OPEX/ROI re-derived with all four sources verified, capex 8858 OBSERVED). The roadmap's "⏳ outstanding since E50" and the tracker history line "DG-7 funds taxonomy outstanding since E50" are stale historical text — the immutable history section stays as written (no relabel); the erratum discipline (ledger wins, errata filed rather than rewritten) is honored by this paragraph. The surviving UNKNOWN is the product-scope one (README :855), not the taxonomy. |
| DG-8 | Consumed: Phase B's ticket authorizations were opened and consumed under fresh grants; Phase B fully closed at E195. |
| DG-9 | Consumed: Phase C's native authorizations were opened and consumed as E197–E201 under fresh grants. |
| DG-10 | Per-round commit/staging authority, exercised in-session every round; no round pending. |

## 4. Open follow-up map (every item on file, nothing invented)

| # | Item | Class | Status of record | What it needs |
|---|---|---|---|---|
| 1 | **E36** (D5 native freight delivery not proven; candidate-1 class) + carried **E114** twin divergence | Rule-bound | Stays open by its own rule (E135): closes only on actual DELIVERED receipts; none exist in any lineage | A future genuinely competing executable route carrying native DELIVERED receipts — operator-gated native work; **not actionable offline** |
| 2 | **FD-C-2** (feasibility statement decision) | Decision of record | `INCOMPLETE_EVIDENCE` (E142, sha `67183cf6…31fa4`, pinned by `TestRetainedDecision`); attempts 1–7 terminal (E150–E157, E197), never relabeled | Only offline continuation: the re-derivation (item 4). Any new native attempt = new operator decision + fresh grants |
| 3 | **Offline Phase C decision re-derivation** | Offline task, READY | Named in E202(a); the E142 engine (`app/planning/phase_c_feasibility.py`) accepts digest-pinned inputs; the battery's five run dirs (`playable-demo-743dee7…`, `-1a5b456b…`, `-d140ff92…`, `-49d9e9f8…`, `-b326925a…`) hold `planning-diagnostic.json` + receipts as candidate inputs (seed 7's diagnostic additionally carries `candidate_count 1`, `selected_service_count 1`, and `network-bindings.json` with `execution_plan_digest 0762af45…`/`native_plan_digest 126a6767…`) | An offline round only: read sealed bytes, derive a successor decision report under a NEW identity, never relabeling E142's. No grant. No code change |
| 4 | **Seed-7 observation-window forensics** | Offline task, READY | Named in E202(b): the terminal `bounded native observation failed or inconclusive` came from the designed gate `app/simulation/openttd/freight_delivery.py:199` (`verify_observation`); the evaluator reproduced it with `KeyError: 's0-observe-3'` (3 of 4 observe receipts) | An offline analysis round (which phase check failed, what `observation_budget` computed, why receipt 4 never landed). Analysis only — any code change would be a separate operator decision |
| 5 | **Ramrom ticket 05 disposition** (`native proof run pending` → adjudicated) | Operator decision | Native proof consumed as honest typed terminals (E197 + E198–E201); the ≥1 verified plan+delivery bar NOT met; ticket status updated 2026-11-12 with the battery closure note | Operator chooses: close the ticket with the honestly-unmet native-proof record, or hold it open pending a future grant decision |
| 6 | **GUI-bearing native probe** (ticket-05 §1/§3.3 product scope; E148 decision) | Owed element, operator-gated | Code half implemented offline (E149); the native GUI run of the product line (no `--stop-on-delivery`, view hold, real window close, typed `ENDED_BY_OPERATOR`) stays owed behind a fresh per-attempt grant | A fresh explicit operator grant if ever pursued; otherwise stays owed, not satisfied |
| 7 | **Map EXIT regression** (the 53 legacy offline reds: controlled P08 e2e ×51, corridor ladder VM ×1, structural-world fixture ×1) | Offline gate, BLOCKED | Ramrom map: "the 53 stay sealed until the full regression, which runs only once the map's remaining tasks are closed (the prior /tmp regression capture expired; a fresh run is required then)"; backlog calls it the wayfinder EXIT gate | Only blocker: item 5's disposition (ticket 05 is the map's last open task). Then ONE offline full-suite round |
| 8 | **Three undefined headings** ("Closed-Loop Optimization", "Productization", "Final Release") | Operator decision only | No definitions on file; untracked by operator choice (2026-11-12 hold) | An operator scope decision; nothing can be tracked against them before it |
| 9 | **UNKNOWN ledger items** (tracker §4) | Honest UNKNOWNs | Full OPEX/net-profit/ROI as a product claim (README :855; T-033 preserved UNKNOWN for the random-world slice even though the corridor five-year OPEX is OBSERVED); concurrency and concurrent throughput (README :133, :1096-1097); closed-loop optimization improvement | Their own evidence classes; never filled by derivation. Any pursuit = operator-defined scope |
| 10 | **Backlog capture-pace note** ("Next decision of record (unresolved): capture-read pace…", backlog :60-64) | **Superseded** | The pause-the-clock design was decided 2026-11-07 (map decision entry; `docs/random-world-capture-pacing-decision-2026-11-07.md`), built in ticket 05, and proven natively four times (`pause_pairs` complete reads: E150 cycle-1 832/832, E153-era attempts, E198 832/832, E199 831/831, E201 1372/1372; the E141 month-pace gate never fired again) | Nothing — historical note stays as written; this paragraph is the erratum-of-record pointer |

## 5. Confirmed requirements vs UNKNOWNs

**Confirmed (each cited above):** Phases A (E127 terminally closed),
B (E195 fully closed), C (E202 terminal statement + audit) — all
sealed; every decision gate discharged (§3); the open-item map (§4)
complete at ten entries; the evidence infrastructure of record stands
(fences, evaluator of record, manifests, E-row discipline, ADR-0001
labels, roadmap §8 invariants).

**UNKNOWN (never invent):** whether any random-world seed admits a
verified native delivery cycle (the battery is exhausted; new seeds =
a new operator decision, never a relabel or retry); the random-world
OPEX/ROI truth (needs native accounting evidence that does not exist);
concurrency/throughput; closed-loop optimization improvement; rail
delivery; arbitrary maps beyond the bounded 256 profile; the
observation-window adequacy question (item 4's forensics would inform
a future design decision, and makes no claim today); whether seed-7's
3-of-4 observe receipts reflect a budget, a pace, or a world property
(precisely what the forensics would establish from the sealed bytes).

## 6. Prioritized execution plan (on-file items only)

- **P1 — Offline Phase C decision re-derivation (item 3).** The next
  actionable offline task. Rationale: it is the only open item that
  continues a decision chain of record (FD-C-2 → the E142 decision),
  it consumes the freshly sealed E197–E201 bytes while they are the
  newest evidence, it requires no operator decision and no grant, and
  its output (a successor decision report under a new identity) either
  strengthens the record's dimensions or confirms `INCOMPLETE_EVIDENCE`
  against the battery bytes — both honest outcomes. Read-only inputs;
  one new report directory under `artifacts/experiments/`; never
  relabeling E142's report.
- **P2 — Seed-7 observation-window forensics (item 4).** Small,
  read-only, and it informs any future observation-budget design
  decision; it creates a research note, not a decision of record.
- **P3 — Ticket-05 disposition (item 5).** Operator decision; on
  "close", the map's tasks are all closed and P4 unblocks.
- **P4 — Map EXIT regression (item 7).** ONE offline full-suite round
  (fresh /tmp capture; the 53 legacy reds run as the exit gate's
  known-red set); runnable the moment P3 closes the map.
- **P5 — Operator decisions (items 1, 5, 6, 8).** E36 stays rule-bound;
  ticket-05 disposition; GUI-bearing probe grant if ever wanted; the
  three undefined headings. None of these is invented work — each is a
  gate the on-file record already names.

**Next actionable offline task: P1, the offline Phase C decision
re-derivation.** It waits only on the operator's go for this round;
this discovery round itself executes nothing beyond this record.

## 7. What a Phase D would need, if the operator defines one

No invention — the record already holds everything a definition would
bind to: the standing fences (roadmap :190-193), the evidence
discipline (roadmap §8; AGENTS.md safety rules), the acceptance-bar
pattern used by every prior phase (offline bar first, then fresh-grant
one-shots with honestly typed terminals), and the anchors of §2. A
Phase D would be an operator-written scope under one of the three
headings (or a named continuation of §4's items); until that decision
exists, nothing is tracked, nothing is scheduled, and no definition of
done exists for it.

## 8. P1 status (2026-11-12, E204)

P1 (item 3, the offline Phase C decision re-derivation) is **done**:
the decision of record `INCOMPLETE_EVIDENCE` is re-derived and
confirmed at the current tree under a successor identity
(`artifacts/experiments/phase-c-feasibility-2026-11-12/`,
deterministic, byte-equal across independent derivations; decision
structure identical to E142's — 2 VERIFIED + 8 PARTIAL), and the
sealed battery evidence is mapped onto the decision vocabulary by the
companion `battery-evidence-mapping.md` (non-authoritative, flips no
engine level; admitting battery diagnostics as engine rows would be a
`phase-c-feasibility/2` operator decision). No completed-search
infeasibility row exists; no feasibility is proven. The next open
items are unchanged: P2 (seed-7 forensics, offline, READY), P3
(ticket-05 disposition, operator), P4 (map EXIT regression, blocked on
P3), P5 (operator decisions). Evidence index E204.

## 9. Scope-definition session status (2026-11-12, E205)

The operator's round-1 decisions: (a) **Phase D existence — deferred**
("I will do it later"): the three headings stay undefined and
untracked; no acceptance criterion, ticket, or definition of done was
authored, and the dependent round-2 questions were not asked;
(b) **`phase-c-feasibility/2` NOT commissioned** — the companion
mapping of §8 stands as the offline consumption of record;
(c) **ticket-05 CLOSED** (`Status: resolved`, honestly-unmet
native-proof record, GUI-bearing probe still owed behind a fresh
grant) — with this closure the ramrom map's tasks are all closed and
the EXIT regression gate (the 53 legacy offline reds) is **unblocked**;
(d) **P2 ordered** as the next round (the seed-7 observation-window
forensics, read-only, no grant, no code change). Evidence index E205.

## 10. P2 status (2026-11-12, E206)

P2 (item 4, the seed-7 observation-window forensics) is **done** —
research note of record
[.scratch/ramrom-product/research/02-seed7-observation-window-forensics.md](../.scratch/ramrom-product/research/02-seed7-observation-window-forensics.md).
All three named questions answered from the sealed E199 bytes: (Q1)
the failing `verify_observation` check is the status check — receipt 3
returned `WINDOW_EXHAUSTED`, not `OBSERVED`; (Q2) the observation
budget computed 4440 ticks (capped; 2048+128·34=6400 at width 256) and
was never binding (774 ticks elapsed); (Q3) the fourth observe receipt
was never issued — the run terminalized at receipt 3's inline
verification and the evaluator's `KeyError: 's0-observe-3'` is the
4-record lookup at `freight_native_network.py:1551`. Root cause of
record: the designed 60-economy-day guard (`main.nut:151`, shared
across all four phases from the pre-start date 712290) vs a
32-tile-Manhattan haul — the full-load wait consumed 50 of the 60
days and the vehicle was still ≥ 24 Manhattan tiles short of the
destination at expiry: **the designed gate fired as designed; no code
defect and no capture defect.** The observation window is distance-
and production-rate-sensitive; any future window redesign is a fresh
operator decision (fresh grants where native). The queue after P2:
P4 (the map EXIT regression, unblocked and ordered "right after P2" in
the E205 session round 2), then P5 (operator decisions). Evidence
index E206.

## 11. P4 status (2026-11-12, E207)

The operator-ordered P4 round — the first recorded full-suite exit-gate
regression — completed end-to-end offline at HEAD `74c8152`. Command of
record (none existed on file; REPRODUCE.md records focused suites only):

```bash
.venv/bin/pytest tests/ -p no:cacheprovider
# 57 failed, 6271 passed, 54 skipped in 3797.26s (1:03:17)   rc=1
```

6382 tests across 239 files, no collection errors (57 + 6271 + 54 = 6382
exactly); the 54 skips are the offline self-skips of the
native/postgres-gated tests. Compared against the 53 legacy known-reds:

- **Group A (controlled P08 e2e) ×51 — reproduced exactly**, mechanism
  matching the legacy triage's frozen-fixture digest drift.
- **Group C (structural-world fixture) ×1 — reproduced exactly** (same test
  ID; `cargo_catalog_checkpoint` manifest sha256 drift; the "may pass on
  Linux (CRLF)" hypothesis is NOT confirmed — failed on Linux with a digest
  mismatch).
- **Corridor family ×1 — at the map's count, but the failing test is
  `test_corridor_cargoflow2_vm.py::test_ladder_of_record_runs_green`**
  ("package dropped request finance-00: no reply"); the triage's named
  target `test_delivered_verdict_never_fires_on_the_terminal_class` PASSED.
  The two on-file descriptions of the historical red disagree; both facts
  recorded, no force-fit.
- **4 additional reds NOT in the legacy 53:** `test_sealed_budgets`
  (`assert 410 == 103`), `test_prepare_materializes_a_pending_
  authorization_candidate` (budgets 410 pages / 208280 bytes vs sealed
  103 / 52324), `test_fallback_schedule_is_sealed_and_explicit`
  (`assert 208280 == (103 * 508)`), and
  `test_finalization_failure_cannot_publish_qualification[terminal]`
  (workspace retained after FAILED finalization). Items 1–3 share one
  signature (computed 410 × 508 budgets vs sealed 103 × 508 constants);
  item 4 is a separate mechanism.

**Outcome of record:** the exit gate does NOT pass (57 reds vs 53). The 4
additional reds' new-vs-pre-existing status is UNKNOWN (no prior full-suite
baseline exists on file — this is the first recorded full-suite run). Root
causes and any fixes remain separate operator decisions (the triage report's
fix-branch proposals stand unexecuted, per E36's rule); the gate stays
sealed/open exactly as the map states. Research note of record:
`.scratch/ramrom-product/research/07-exit-regression-full-suite-2026-11-12.md`.
UNKNOWNs preserved: new-vs-pre-existing for the 4 extras; the historical
corridor red's intended test; Group C's actual fixture-drift mechanism;
flakiness/ordering sensitivity (single offline capture only). Nothing
relabeled. Evidence index E207.
