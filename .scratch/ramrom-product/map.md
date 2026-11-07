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
- The seed-42 demo fix (33 construction mutations, 3 P05 services, then
  the operator closed the window mid-run — typed FAILED) is evidence for
  the soft-close clause, not a defect to relabel.
- The 53 legacy offline reds (controlled P08 e2e ×51, corridor ladder VM
  ×1, structural-world fixture ×1) are sealed until the exit regression
  pass; they are never mixed into feasibility engineering work.

## Decisions so far

- [Why no ramrom seed qualified: the NO_FEASIBLE_SERVICES diagnosis](issues/01-feasibility-diagnosis.md): findings file `.scratch/ramrom-product/research/01-feasibility-diagnosis.md`; failure is capture-seal geometry (silent distance gate) + detour-free strips severed by a town-road band, NOT engines/planner; CP-SAT never invoked; discovery truncated at the 16-relationship cap.

## Not yet specified

<!-- graduated to tickets as the frontier advances -->

- Legacy-53 diagnosis scope: sharp only after ticket 03 decides what the
  feasibility work touches (if the engine changes rip into the old
  controlled-e2e fixtures, the legacy reds shrink or move).
- The seed battery of record: which seeds certify "predictably produces
  services" (offline fixture seeds + native proof seeds) — specifiable
  once ticket 03 fixes the acceptance bar.
- Product command surface and docs (README how-to, REPRODUCE commands of
  record) — graduates after ticket 04 fixes the loop architecture.

## Out of scope

<!-- work ruled beyond the destination; closes with one line here -->

- The corridor Cargoflow-2 production line: random seeds do not apply to
  its fixed corridor composition; ramrom work must not re-scope the
  consumed corridors, their sealed evidence or their E36/E114 rails.
- An in-window UI overlay or live web dashboard inside the OpenTTD
  process: the operator chose game window + console + HTML report.
- Relabeling or re-running any consumed attempt: supersession is always
  a fresh identity, never a rerun.
