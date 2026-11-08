# Map: the ramrom-seed product

## Destination

The repo's random-world line is the product: on a recorded, always-random
"ramrom" seed (a normal `new game`), it generates a 256×256 temperate,
flat-terrain world starting 1950-01-01, analyzes the map's assets
(materials, industry factories, yields), plans with the CP-SAT optimizer,
and plays live on real OpenTTD with the spectator GUI showing the process —
and it LOOPs: one continuous world stays alive across analyze → plan → play
cycles that keep forming and delivering freight services in that one world.
A closed spectator window ends a phase softly (ended-by-operator, never a
system failure), the game window plus the console plus a per-run HTML
report carry the whole story, service feasibility works predictably enough
that ramrom seeds produce services (typed honest failure still exists but
is the exception, not the rule), and when all tasks are done the FULL
offline regression passed including the 53 legacy reds. Every native
attempt under the effort runs once, only on the operator's explicit
in-session grant.

## Notes

- The operator watched the fixed seed-42 demo and named the product there:
  Q1–Q8 of the opening interview fixed the destination (their answers are
  its clauses).
- Repo safety stays supreme: native OpenTTD runs are user-gated per
  attempt (one attempt, no retry, no reconnect; honestly recorded either
  way); `artifacts/` evidence is immutable; books discipline = ticket file
  + backlog row + one commit per round.
- Decision tickets run the grilling + domain-modeling skills; research
  tickets run the research skill; the operator reads caveman-terse chat
  but persisted files get full sentences.
- World settings of record for the product: map 256×256, climate
  temperate, terrain type 0 (flat), towns 3, industries 3, start 1950
  (the world's native epoch), seed always recorded (0..4294967294).
- Spec of record for the design tickets:
  `docs/specs/ramrom-product.md` (§1 product, §2 feasibility fix, §3
  loop architecture, §4 out of scope).
- The seed-42 demo fix (33 construction mutations, 3 P05 services, then
  the operator closed the window mid-run — typed FAILED) is evidence for
  the soft-close clause, not a defect to relabel.
- The 53 legacy offline reds (controlled P08 e2e ×51, corridor ladder VM
  ×1, structural-world fixture ×1) are sealed until the exit regression
  pass; they are never mixed into feasibility engineering work.

## Decisions so far

- [Why no ramrom seed qualified: the NO_FEASIBLE_SERVICES diagnosis](issues/01-feasibility-diagnosis.md): findings file `.scratch/ramrom-product/research/01-feasibility-diagnosis.md`; failure is capture-seal geometry (silent distance gate) + detour-free strips severed by a town-road band, NOT engines/planner; CP-SAT never invoked; discovery truncated at the 16-relationship cap.
- [Books for the two 2026-11-07 native one-shots](issues/02-todays-one-shot-books.md): E139 (seed-2026, typed `NO_FEASIBLE_SERVICES`) and E140 (seed-42, operator window-close abort) recorded at their own identities; the abort is the soft-close evidence, never a relabeled defect.
- [Widen the capture seal (feasibility fix)](issues/03-feasibility-fix-decision.md): `capture_tile_limit` gains 2048 (new profile `random-rectangle-2048-v1`, 512-v1/256 byte-compatible), spare budget grows the shorter capture axis with a `capture_edge_pad` (default 6), every typed rejection stays honest, command-of-record defaults `--capture-tiles 2048 --capture-seconds 120 --capture-pad 6`. Implemented with offline tests; native proof runs await per-attempt grants.
- [Continuous-world loop architecture](issues/04-loop-architecture.md): one cycle = fresh qualified-month read → P05/CP-SAT → execution → verified deliveries on the same alive world (never stale facts); reconnect per cycle under the one-attempt-per-connect discipline; soft cycle ends (delivery-verified / ended-by-operator / time budget); the company keeps funds and vehicles (each cycle's save is the next cycle's before); fresh seed after 2 consecutive zero-service cycles; per-cycle receipts, diagnostic and HTML report. Build = ticket 05.
- [M2 capture pacing = pause the world clock per capture](../../docs/random-world-capture-pacing-decision-2026-11-07.md): decided 2026-11-07 — one `pause`/`unpause` pair around each random-world supplemental capture (owned console), E141's wall-clock race (2048-tile capture vs `month.end_date`) removed with the qualified-month gate and all wall budgets unchanged; page-critical-first and contract-widening rejected; per-attempt fences (`pause_pairs == captured_relationships`, failed resume is a typed attempt failure, unobserved pause-stall first types `PAUSED_CAPTURE_UNRESPONSIVE`). Tickets 03-family decision, wired and offline-tested.
- [Loop engine built offline (ticket 05 build record)](issues/05-build-loop-product.md): `run_loops`/`loop_gate`, sealed `loop_cycles` (CLI `--cycles`, budgets scale volume keys ×cycles), `exclude=()` threading so each cycle plans only new services with `SERVICE_ALREADY_BUILT` rejections and the typed all-excluded zero-service outcome, per-cycle `loop-cycle-{k}` recording (identity copies, own saves, own manifest, per-cycle P07 report + `loops.md`), soft `ZERO_SERVICE`/`abandoned_world` ends (K=2). Touched suites 151 passed; native loop proof (≥1 full cycle delivering) still needs its per-attempt grant.
- [Execution mode: the qualification attempt stays `--headless`](../../docs/gui-headless-execution-mode-decision-2026-11-08.md): decided 2026-11-08 — the GUI-vs-headless discrepancy against spec §1/§3.3 resolves without changing any command or criterion; every qualification acceptance bar is receipt-based (spec §2/ticket-05) and the loop line's native history (E139/E141/E145) is headless, so `--headless --stop-on-delivery` stays the attempt mode of record; the §1 spectator GUI and its §3.3 window-close soft end remain product-definition scope owed by their own later GUI-bearing probe (owed, never silently dropped: headless soft end is Ctrl+C only, and E140's window close typed FAILED).
- [GUI product scope implemented offline: typed `ENDED_BY_OPERATOR` soft end](../../docs/gui-headless-execution-mode-decision-2026-11-08.md): landed 2026-11-08 — the operator's spectator window close now types the soft ended-by-operator phase end (`OperatorWindowClosed` + `backend.client_soft` + `soft_gate()` at the AdminPort exchange boundaries; `run` writes `ENDED_BY_OPERATOR` with `operator_soft_end`, never a system failure, no error key), a non-zero client exit keeps the exact E140-shape typed failure, a close during the view-hold never retypes a verified run, and `run_demo` maps the soft end to rc 0; 5 offline tests + adjacent tuple 265 passed; the native GUI-bearing probe (GUI run of the product line without `--stop-on-delivery`) stays owed behind a fresh per-attempt grant, and the headless loop of record is byte-preserved.
- [Attempt-1 loop qualification FAILED once and was sealed; per-cycle `graphics-identity.json` fix landed offline](../../EVIDENCE_INDEX.md): the one-attempt grant ran the command of record once on 2026-11-08 and it failed (`FileNotFoundError: .../loop-cycle-1/graphics-identity.json`, exit 1, no cycle completed, cleanup fully reaped); the cycle staging now copies a content-identical `graphics-identity.json` per cycle with a pin test, superseding E143's guaranteed per-cycle list; the cycle-1 diagnostic settled the native pacing datum (832/832 capture pairs inside the qualified M2 month, `pause_pairs=1`, no `pause_resume_error`) while `search_truncated=true` keeps FD-C-2 at `INCOMPLETE_EVIDENCE`; the command of record stays byte-unchanged and the next attempt waits on a fresh explicit grant.
- [Cycle-chain artifact audit closed offline after the E150 fix (E151)](../../EVIDENCE_INDEX.md): nothing further is missing — every plain-constant `prepared.directory` read in the run-time cycle chain classifies per occurrence into exactly six names (root-stage copies, the per-cycle staging self-write, the chain self-write before read, exchange-disc packets), pinned by an AST drift-guard test; two e2e offline tests drive the real `capture_planning_facts` against a staged `loop-cycle-1` recording alone (the exact seam attempt 1 died at) and pin the sealed attempt-1 bytes read-only forever; the 13-file adjacent tuple runs 269 passed + 13 more in the controlled harness; no app code changed and the command of record stays byte-unchanged at the fresh-grant gate.

## Not yet specified

<!-- graduated to tickets as the frontier advances -->

- Legacy-53 re-read stays exit-gate fog: the feasibility fix landed in
  the random-world capture/region surfaces (demo_random, supplemental
  facts, classification census, runtime planning) and the touched
  suites are green, so no legacy controlled-e2e red moved; the 53 stay
  sealed until the full regression, which runs only once the map's
  remaining tasks are closed (the prior /tmp regression capture
  expired; a fresh run is required then).

## Out of scope

<!-- work ruled beyond the destination; closes with one line here -->

- The corridor Cargoflow-2 production line: random seeds do not apply to
  its fixed corridor composition; ramrom work must not re-scope the
  consumed corridors, their sealed evidence or their E36/E114 rails.
- An in-window UI overlay or live web dashboard inside the OpenTTD
  process: the operator chose game window + console + HTML report.
- Relabeling or re-running any consumed attempt: supersession is always
  a fresh identity, never a rerun.
- The granted seed-2026 widened-seal run (E141) typed
  `supplemental capture outside final M2 month`: the widened rectangle's
  capture-read pace raced the in-game month at live speed. Honest note:
  the funnel advanced past E139's capture-budget wall (n0 captured
  completely; engines/supply never refused); the binding constraint moved
  to capture pacing. Candidate fix designs are recorded in the research
  file §9; no further native attempt without a fresh grant.
