# Master completion tracker — 2026-11-11

Compiled from the sources of record (TASKS.md, AI_HANDOFF.md,
EVIDENCE_INDEX.md, README.md, CONTEXT.md, REPRODUCE.md,
docs/roadmap-and-scope-2026-11-05.md, docs/requirements-evidence-matrix.md,
docs/poc-ticket-backlog-2026-11-04/07/11.md,
docs/poc-completion-declaration-2026-11-06.md, docs/specs/*,
.scratch/*/issues/*) at HEAD `2e5fcc9`, branch `miles/fright-delivery`.
Trust order: retained `artifacts/` evidence > ledgers > docs. FAILED
terminal results are never relabeled; every consumed attempt stays
consumed (roadmap :20-23, :253-258). This tracker authorizes nothing.

## 1. Phase map — remaining work

### Phase A — Corridor PoC: TERMINALLY CLOSED (E127)
Closed by the completion declaration
(docs/poc-completion-declaration-2026-11-06.md). It carries two open
findings: **E36** (delivered-class) and **E114** (twin divergence).

### Phase B — native closure outstanding (the active front)
Refrain of record (docs/poc-ticket-backlog-2026-11-11.md:325-327):
"Phase B native closure outstanding — T-030 ×1, T-031 arm A ×1 + arm B
×1, T-032 ×1, each its own fresh grant, each inheriting both
exercise-core fixes (E167 + E169)."
Internal order (roadmap :159-161): "T-030 → T-031 → T-032 → T-033,
T-034 as the standing qualification gate (re-runnable any round)".

| Task | Launches (fresh grants) | Staging state at `2e5fcc9` (2026-11-11) | Done-ness (roadmap :151-157) |
| --- | --- | --- | --- |
| T-030 fleet & capacity exercise | ×1 | **EXECUTED 2026-11-11 under the operator's fresh grant (E182): terminal `CANONICAL_FLEET_EXERCISE_VERIFIED` rc 0 — CLOSED.** `canonical-fleet-exercise-t030-1/` sealed; exercise-correspondence typed `EXACT_NATIVE_SEMANTIC_CORRESPONDENCE`; capacity-add £4,429; dispatch + re-pause receipts; cleanup all-true, manifest 0 mismatches, post-run verify rc 0 | Native exercise receipts + canonical correspondence record + E-row — **MET** |
| T-031 matched arms | ×2, arm A strictly before arm B's authorization (03:19-22); separate grant per arm (02:37-41, 03:43-44) | **DONE — CLOSED.** Arm A attempt 3 `canonical-fleet-matched-a-t031-3` VERIFIED once under its fresh grant (E190: `CANONICAL_FLEET_MATCHED_VERIFIED` rc 0, binding null, five annual receipts 1951–1955, sealed). Arm B `canonical-fleet-matched-b-t031-1` VERIFIED once under its own fresh grant after arm A completed (E191: rc 0, mutations 3, binding `{purchase_capex: 4429, service: 1, vehicle: 7}` — the fourth vehicle, five annual receipts, sealed; ordering of record held). `compare_arms` descriptive B-vs-A record produced offline (E192: closing cash +10910, freight revenue +17443, delivered cargo +980, revenue/day +9.55, capex 4429; UNKNOWN preserved; four guards stand; no profit claim). Attempt history: t031-1 FAILED E183, t031-2 FAILED E185; fix/diagnosis rounds E184/E186/E187/E188; create-q5 anchor verified E189 | Per-arm receipts typed `CANONICAL_FLEET_MATCHED_VERIFIED` (E190 + E191) + `compare_arms` descriptive B-vs-A record (E192) + E-rows — **MET; T-031 CLOSED** |
| T-032 five-year continuous | ×1 | **DONE — CLOSED.** `canonical-fleet-continuous-t032-1/` EXECUTED once under the operator's fresh T-032 grant at HEAD `7d29994` (E193): typed `CANONICAL_FIVE_YEAR_CONTINUOUS_VERIFIED` rc 0 — launches 1 / connections 1 / mutations 2 / requests 10861; reload correspondence `EXACT_NATIVE_SEMANTIC_CORRESPONDENCE` (cash 471157), `continuous-begin` ok through the E184 fixed armed seal, FIVE complete native economy years observed (annual receipts economy years 1951–1955, elapsed economy days 365→1826, + 60 monthly + 20 quarterly + telemetry 4/5/6) within the documented budget; cleanup all-true, manifest match True, sealed read-only. Pre-launch: superseded pre-fix staging replaced (re-prepared with the fixed package + create-q5 anchor); ordering held (T-031 closed first) | Per-year OPEX/ROI derived only from observed accounting + E-row — **native receipts exist and are sealed (E193); the offline derivation is T-033's job** |
| T-033 consolidated OPEX/ROI | 0 (offline) | resolved E164; **RE-DERIVED 2026-11-12 after Phase B native closure (E194)** — the record of record is `artifacts/experiments/phase-b-consolidation-2026-11-12/`: all four native sources VERIFIED (0 UNKNOWN-PENDING); consolidated vehicle-purchase CAPEX £8,858 OBSERVED (T-030 £4,429 + arm B £4,429 + arm A £0 + T-032 £0); revenue OBSERVED from the receipts' own `freight_revenue` (arm A 50,940 / arm B 68,383 / T-032 50,940; T-030 UNKNOWN — no financial summary in its flow); OPEX/ROI DERIVED for arms + T-032; OPEX categories stay UNKNOWN until their own native observations exist; latent key fix: module read `income`, real receipts key `freight_revenue` (the financial_attribution vocabulary) — fixed with tests | Aggregation record; OBSERVED/DERIVED/CONTROLLED segregation; UNKNOWN stays UNKNOWN — **MET (E194); T-033 CLOSED** |
| T-034 standing regression | 0 (offline) | resolved E165 (6286 passed / 56 legacy-red by ID / 0 errors / 50 skipped at `f0f0155`); **RE-RUN 2026-11-12 at the Phase B closure HEAD (E195): first gate at `dc86b51` surfaced 2 new round-adjacent IDs, both diagnosed fixture-stale with no app change (the E167-era GUI preflight test pinned the superseded create-q3 anchor — verify_created_source correctly binds the E186/E189 CREATE constant of record create-q5; the native-save-path seam double lacked the post-E179 `_scan_fatal` member); fix round `3b2b618` (test files only); FINAL GATE at `3b2b618`: 6379 collected / 6272 passed / 56 failed / 0 errors / 51 skipped — the E165 legacy-red set reproduced EXACTLY by ID, zero failures in any round-touched file; statics 12 pre-existing in three never-touched files; manifest sweep 214 / 0 mismatches; pins hold; pgrep empty** | Regression suite result + E-row — **MET (E195); T-034 CLOSED; Phase B fully closed** |

Closed, carries no Phase B credit: **T-035** GUI probe terminal
`CANONICAL_FLEET_GUI_PROBE_VERIFIED` (E170; genealogy t035-1 refused →
t035-2 FAILED E168 → t035-3 VERIFIED) and **T-036** fresh-world GUI
family terminal `FRESH_WORLD_GUI_PROBE_VERIFIED` (E180, CLOSED; genealogy
create A FAILED E172 → A2 VERIFIED E173 → A3 VERIFIED E175; GUI B FAILED
E174 → B2 FAILED E176 → B3 FAILED E178 → B4 FAILED E179 → B5 VERIFIED).

### Phase C — Random World (roadmap §4 :165-193)
- Seed-17 generation/discovery/GUI PROVEN (E4, E8; matrix :13); service
  execution on random worlds never native-verified (roadmap :175).
- FD-C-2 loop attempts 1–6 consumed terminal (E150–E158, E159);
  FD-C-2 stays `INCOMPLETE_EVIDENCE`. **Attempt 7 package is
  READY_FOR_OPERATOR_AUTHORIZATION (E160), not executed** — and
  re-confirmed fresh at the Phase B closure HEAD `ccdab65` (E196:
  `p08_road.py`/`freight_delivery.py` untouched since the audit; fix
  body in place; seven-file set 172/0/0/0; statics clean; prereqs
  re-proven; `pgrep -x openttd` empty) — and **EXECUTED exactly once
  under the operator's fresh attempt-7 grant (E197, 2026-11-12, at
  `ac504f8`): typed terminal `NATIVE_LOOP_ZERO_SERVICES`, evaluator
  of record rc 0 with both cycles independently `ZERO_SERVICE`
  (verbatim `NO_FEASIBLE_SERVICES` error); the remediation's
  classification goal proven on fresh bytes — cycle 1's refusal is
  the fix's explicit `NATIVE_CORRIDOR_BOUND: requires 2..47 road
  tiles` (first native appearance), cycle 2's the witness-fallback
  `NO_BOUNDED_CORRIDOR` (38/20 stops disconnected), ZERO
  `SEARCH_LIMIT_EXCEEDED` anywhere; funnel: compatible 16, captured
  1 (832/832 reads, pause_pairs 1), 10 × `CAPTURE_TILE_BUDGET`,
  `CANDIDATE_SEARCH_LIMIT controls 146`, `search_truncated: true`.
  FD-C-2 stays `INCOMPLETE_EVIDENCE`; run dir
  `playable-demo-743dee713b2841baa1bcbc0f115ee901` sealed read-only;
  cleanup all-true, manifest match True. Phase C done-ness item 3
  ("attempt 7 consumed under a fresh grant → typed terminal
  adjudicated") — MET.**
- Tile V2 capture native-VERIFIED but SOURCE_SAVE_FUSION sealed
  REJECTED (83 disagreements, E16): P08 stands at
  `INCOMPLETE_TILE_CLASSIFICATION`; the fusion gate is CLOSED.
- **Ramrom seed battery of record**
  (docs/specs/ramrom-product.md:71-84): offline bar **MET 2026-11-12
  (E196)** — widened-shape allocation tests + the retained strip
  re-derivation re-run fresh 80 collected / 0 failed / 0 skipped (no
  skip-typed; `TestRetainedDecision` derived the real decision from
  the E139/E141 retained bytes); native one-shots each under its own
  fresh grant: seed 2026 re-run as a NEW identity (E139 never
  relabeled), then seeds 7, 8, 9. The bar: ≥1 verified native plan +
  delivery cycle without a `NO_FEASIBLE_SERVICES` terminal; every
  terminal honestly typed. Command of record:
  `python -m app.openttd_demo run --random-world --seed N` (profile
  `random-rectangle-2048-v1`, 2048-tile seal).
  **Seed-2026 re-run EXECUTED once under its fresh grant (E198,
  2026-11-12, at `fc25760`): typed terminal `FAILED` /
  `NO_FEASIBLE_SERVICES` — the funnel moved deeper than E139 and
  E141 (captured 1, 832/832 reads completed with `pause_pairs: 1` —
  the month-pace gate did not fire; sole candidate refusal the
  explicit `NATIVE_CORRIDOR_BOUND`); `search_truncated: true`;
  manifest match True, cleanup all-true, sealed read-only. Battery
  bar NOT met by this run (honestly); seeds 7/8/9 next, each its own
  fresh grant.**
  **Seed-7 one-shot EXECUTED once under the battery grant (E199,
  2026-11-12, at `90ca45a`): the FIRST battery seed to produce a
  native plan — `PLANNED`, candidate_count 1, `selected_service_
  count: 1` (industry-9 → industry-12, 22 cargo units); the vehicle
  was constructed and reached RUNNING; terminal typed `bounded
  native observation failed or inconclusive` (the designed
  observation gate `freight_delivery.py:199`; evaluator reproduces
  with `KeyError: 's0-observe-3'` — 3 of 4 observe receipts);
  manifest match True, cleanup all-true, sealed read-only. Battery
  bar NOT met by this run (delivery cycle's bounded verification
  incomplete); seed 8 next.**
  **Seed-8 one-shot EXECUTED once under the battery grant (E200,
  2026-11-12, at `90ca45a`): typed terminal `CAPTURE_SCHEDULE_EMPTY`
  — the capture scheduler's capacity policy deferred both
  relationships (estimated live-rate spans 26d/28d from planned
  start 712290 overshoot the exclusive window ending 712312);
  captured 0, reads 0/0, candidates None; manifest match True,
  cleanup all-true, sealed read-only. Battery bar NOT met by this
  run; seed 9 next.**
  **Seed-9 one-shot EXECUTED once under the battery grant (E201,
  2026-11-12, at `90ca45a`): typed terminal `NO_FEASIBLE_SERVICES`
  — captured 1 (1372/1372 reads completed, `pause_pairs: 1`), sole
  candidate refusal `NO_BOUNDED_CORRIDOR` (20/12 stops
  disconnected); manifest match True, cleanup all-true, sealed
  read-only.**
  **BATTERY COMPLETE — bar NOT met (honestly), every terminal
  honestly typed:** four one-shots, each its own fresh grant, each
  exactly once, none relabeled — seed 2026 `NO_FEASIBLE_SERVICES`
  (E198, `NATIVE_CORRIDOR_BOUND`), seed 7 bounded-observation
  inconclusive (E199, the battery's only PLANNED run — plan selected
  and executed natively, observe receipts 3/4), seed 8
  `CAPTURE_SCHEDULE_EMPTY` (E200, capacity policy, zero reads),
  seed 9 `NO_FEASIBLE_SERVICES` (E201, `NO_BOUNDED_CORRIDOR`). Seed
  7 came closest (construction, vehicle, service RUNNING; delivery
  cycle's bounded verification incomplete). Phase C native items now
  all consumed or honestly terminal (FD-C-2 attempts 1–7 E197;
  battery E198–E201); FD-C-2 stays `INCOMPLETE_EVIDENCE`;
  remaining Phase C work is offline-only.

### Phase C terminal statement and acceptance audit (E202, 2026-11-12, offline at `c654bf9`)

**Terminal statement of record.** The roadmap's infeasibility clause
(:186-188 — "Phase C ends there with the statement as its terminal
evidence") did **not** fire, and no feasibility was proven: every
recorded bounded random-world search carries `search_truncated: true`
(E142's zero observed-world-infeasibility rows stand), and no verified
native plan + delivery cycle exists on a random world. **The decision
of record `INCOMPLETE_EVIDENCE` (E142 report sha `67183cf6…31fa4`,
pinned offline by `TestRetainedDecision`) stands as the Phase C
terminal statement**, now carried by the sealed battery bytes: FD-C-1
verified (E142); FD-C-2 attempts 1–7 terminal, FD-C-2 stays
`INCOMPLETE_EVIDENCE` (E197); the ramrom battery consumed with the
bar honestly NOT met and every terminal honestly typed (E198–E201).
Strongest verified facts: seed 7's plan selection + native
construction + RUNNING service (the battery's only selected plan;
digests `0762af45…`/`126a6767…`); pause pacing proven twice; four
typed terminal classes, zero masking. Roadmap :175's "Service
execution on random worlds has never been native-verified" is
superseded by the sealed bytes: service execution was native-attempted
to battery exhaustion — selection, construction and a running service
are each once-verified in the seed-7 slice; a verified delivery cycle
is not; no feasibility or infeasibility claim extends beyond the
recorded slices; every identity sealed, never relabeled. The E36 rule
is untouched (closed only on actual DELIVERED receipts — none exist).
**No Phase D exists on file** (roadmap §4 is the last phase).

**Acceptance audit (every Phase C criterion):**

| # | Criterion (source) | Classification | Evidence |
|---|---|---|---|
| 1 | Random World generation, discovery, spectator, cleanup (matrix; roadmap :167) | **MET** | E4, E8 (sealed, unchanged) |
| 2 | Seed-17 coal-pair feasibility through P08/P05 (roadmap :168-170) | **NOT MET** — honest FAILED terminal with complete-search infeasibility for that slice | E8–E10 |
| 3 | FD-C-1 offline reconciliation disposition (roadmap :179-182) | **MET** | E142 (verified, not rebuilt; 77+6+0+0; binding `allowed=true`/`p08_complete=false`) |
| 4 | `SOURCE_SAVE_FUSION` correspondence / fusion gate | **NOT MET** — sealed REJECTED, CLOSED | E16, ADR-010 |
| 5 | FD-C-2 feasibility statement decision (roadmap :183-188) | **INCOMPLETE_EVIDENCE** — decision of record `INCOMPLETE_EVIDENCE`; attempts 1–7 terminal; neither gate branch fired | E142, E150–E157, E197 |
| 6 | Standing fences on native work (:190-193: frozen code, finite budgets, one server + encrypted Admin, zero retry/reconnect, certified cleanup, unsupported-world result distinct from delivery) | **MET** in every native run of record | E197–E201 preflight/cleanup/manifest seals |
| 7 | ramrom offline bar (spec :76-78) | **MET** | E196 (80/0/0/0, re-derivation ran) |
| 8 | ramrom battery bar: ≥1 verified native plan + delivery cycle without `NO_FEASIBLE_SERVICES` (spec :78-84) | **NOT MET** (honest) | E198–E201 |
| 9 | ramrom reporting clause: every terminal honestly typed (spec :84) | **MET** | E198–E201 |
| 10 | Done-ness item 3: attempt 7 consumed → typed terminal adjudicated | **MET** | E197 |
| 11 | Done-ness item 4: battery bar met OR every terminal honestly typed | **MET via the OR clause** | E198–E201 |
| 12 | Done-ness item 6: Phase C terminal statement per roadmap :186-193 | **INCOMPLETE_EVIDENCE** — recorded (E202); neither the feasibility nor the infeasibility branch fired | E202 |
| 13 | E36 disposition under its own rule | **Rule upheld** — stays open; no DELIVERED receipts exist | E135 |
| 14 | Roadmap :175 "service execution never native-verified" | **Superseded by sealed bytes** — native-attempted to exhaustion; selection/construction/running once-verified (seed-7 slice); delivery cycle unverified | E197–E201 |

**Remaining offline follow-ups on file (none launched; each awaits
operator direction where it creates new records):** (a) offline Phase
C decision re-derivation consuming the battery diagnostics as new
digest-pinned inputs to the E142 engine — a successor decision report
under a new identity, never relabeling E142's; (b) seed-7 bounded-
observation-window forensics from the sealed bytes (which
`verify_observation` phase check failed, what `observation_budget`
computed) — analysis only, no code change without an operator
decision; (c) ramrom ticket 05's native-proof clause adjudicated by
the battery record — operator disposition pending; (d) DG-7 funds
taxonomy (outstanding since E50) and the three undefined headings
("Closed-Loop Optimization", "Productization", "Final Release")
remain open operator decisions — nothing invented for them; DG-9's
native authorizations were opened and consumed as E197–E201 under
fresh grants (the roadmap gate table's "⏳ not opened" text is its
historical record; this tracker is the living authority).

### Phases with no definitions on file
"Closed-Loop Optimization", "Productization", "Final Release" appear 0
times across roadmap-and-scope-2026-11-05.md, requirements-evidence-matrix.md,
specs/ramrom-product.md and poc-ticket-backlog-2026-11-07.md; no literal
"Definition of Done" phrase exists anywhere. Nearest anchors: README.md:174
rows ("Arbitrary maps, rail delivery, concurrent native vehicles,
closed-loop optimization | Outside the demonstrated native MVP") and
README.md:853-855 ("Comparisons do not establish native feasibility or
demonstrated optimization improvement. Full OPEX, ROI, and profitability
remain unknown."). Any work under those three headings needs an operator
decision to define scope first — nothing can be tracked against them.

## 2. Terminal-FAILED history (immutable; never retry or relabel)

- FD-C-2 attempts 1–6 (E150–E157; attempt-6 designed terminal
  `NATIVE_LOOP_ZERO_SERVICES`).
- Seed-17 smoke (`NO_BOUNDED_CORRIDOR`, roadmap :167-170); seed-2026
  `NO_FEASIBLE_SERVICES` (E139), widened-seal re-run
  `supplemental capture outside final M2 month` (E141), E145
  `STAGING_SEAM_DRIFT`.
- D5 corridor: candidate-1 E36 class; candidate-5 round-5 halt;
  candidate-9 + candidate-11 both `CARGOFLOW2_LOADED_NEVER_DELIVERED`
  (twice-reproduced; verify replays the terminal, not a delivery);
  E56, E64, E68, E92, E97 chain halts; D4-CORRIDOR-3/4 partials.
- Native attempts 10 (`NETWORK_INDUSTRY_BUILD_FAILED`), 15
  (`RecordConstruction` crash), 16 (£1 residual defect), 18
  (`CONTINUOUS_AUTORENEW_ENABLED`), 19 (five-year FAILED terminal).
- T-035 t035-1 (refused, preserved) + t035-2 (E168); T-036 create A
  (E172) + GUI B/B2/B3/B4 (E174, E176, E178, E179).
- E114 twin divergence carried with E36; DG-7 funds taxonomy
  outstanding since E50 (roadmap :204); DG-8/9/10 open.

## 3. Project-wide Definition of Done

No literal DoD statement exists in any source doc. Reconstructed
minimal conjunction from the acceptance statements on file
(RECONSTRUCTED, not quoted as a whole):

1. Four separately authorized fresh-grant launches consumed exactly
   once — T-030 ×1, T-031 arm A ×1 then arm B ×1, T-032 ×1 — each
   producing its typed receipts and E-row (backlog-11:325-327;
   T-031 03:19-22). Consumed so far: T-030 (E182, verified);
   T-031 arm A attempts 1 AND 2 (E183 armed-seal script death; E185
   correspondence refusal of the bridge change — both grants consumed
   and void; fresh grants advance identities, never a retry); the
   canonical-fleet-create-q4 anchor attempt (E187 `KeyError: 'world'`
   — unstaged world facts, fixed E188); the canonical-fleet-create-q5
   anchor (E189, VERIFIED rc 0 — the fixed-bridge anchor exists).
   Arm A t031-3 is EXECUTED and VERIFIED (E190, `CANONICAL_FLEET_MATCHED_VERIFIED`
   rc 0 — arm A's done-ness part met). Arm B t031-1 EXECUTED and
   VERIFIED (E191, rc 0, after arm A completed; ordering held); the
   `compare_arms` record produced offline (E192) — T-031 CLOSED.
   The canonical-fleet-continuous-t032-1 launch EXECUTED and VERIFIED
   (E193, `CANONICAL_FIVE_YEAR_CONTINUOUS_VERIFIED` rc 0) — the
   four-launch ledger of record is complete.
2. T-031 `compare_arms` descriptive record lands (E192 — done); T-032
   per-year
   OPEX/ROI derived only from observed accounting (E193 — native
   receipts sealed); T-033 re-derived with UNKNOWN preserved (E194 —
   done).
3. FD-C-2 Attempt 7 consumed under a fresh grant → typed terminal
   adjudicated — **DONE (E197, 2026-11-12):** `NATIVE_LOOP_ZERO_
   SERVICES` typed, evaluator rc 0 both cycles verified, remediation
   classification goal proven (explicit bound terminals, zero
   `SEARCH_LIMIT_EXCEEDED`); FD-C-2 stays `INCOMPLETE_EVIDENCE`.
4. ramrom seed battery bar met, or every terminal honestly typed
   (ramrom-product.md:78-84) — **DONE via the OR clause (E198–E201,
   2026-11-12):** the battery is consumed (four one-shots, each its
   own fresh grant, each exactly once); the bar is honestly NOT met
   (seed 7 closest — plan selected and executed natively, delivery
   cycle's bounded verification incomplete); every terminal of
   every run honestly typed.
5. E36 dispositioned under its own rule: closed only on actual
   DELIVERED receipts; otherwise stays open — no definition stretched
   (E135, EVIDENCE_INDEX.md:473).
6. Phase C terminal statement per roadmap :186-193: native random
   delivery pursued only if supported-construction feasibility is
   proven; otherwise the infeasibility statement is the terminal
   evidence of Phase C.

## 4. UNKNOWN ledger (never invent)

Full OPEX, net profit, ROI (matrix :35; README :33); concurrency and
concurrent throughput (README :133, :1096-1097); paid shared-asset
reuse (README :802-803); arbitrary maps / rail / >256×256 / bridges &
tunnels (roadmap :58-62, README :174); economy-time milestones
(README :1154-1159); per-service revenue (README :1334); fresh native
cost bounds / A/B feasibility (README :972-975, BLOCKED by launch
policy on cloned saves); the four T-033 native sources until the
Phase B attempts run (E164); OPEX categories beyond observed cash
deltas until DG-7 + T-032/T-033 (roadmap :244-245); clone portability
of `artifacts/` (AI_HANDOFF :36); remote documentation availability
(CONTEXT.md :170).

## 5. Next operator actions (each its own session, own fresh grant)

1. **T-030** — DONE (E182): the one authorized launch verified
   (`CANONICAL_FLEET_EXERCISE_VERIFIED` rc 0, sealed
   `canonical-fleet-exercise-t030-1/`); grant consumed and void.
2. **T-033** — DONE (E194): the offline re-derivation regenerated
   (`artifacts/experiments/phase-b-consolidation-2026-11-12/`); the
   T-034 gate re-run clean at `3b2b618` (E195) — **PHASE B FULLY
   CLOSED**.
3. FD-C-2 Attempt 7: **DONE (E197)** — executed once under its fresh
   grant; typed terminal `NATIVE_LOOP_ZERO_SERVICES`; FD-C-2 stays
   `INCOMPLETE_EVIDENCE`.
4. ramrom battery: **CONSUMED (E198–E201)** — offline bar met (E196),
   then all four one-shots executed once under their own fresh
   grants; bar honestly NOT met, every terminal honestly typed; the
   infeasibility/no-plan statement of record stands from the sealed
   battery bytes (spec §bar).
