# Spec: the ramrom-seed product (production, not demo)

Spec of record for the wayfinder effort `.scratch/ramrom-product/map.md`.
Operator clauses Q1–Q8 (2026-11-07 sessions) are its constitution; this
book records the decided designs (tickets 03 and 04) and the acceptance
bar of record. Status: active — feasibility-fix implementation landed in
this round; loop engine build is the open frontier (ticket 05).

## 1. Product definition

The repo's random-world line (`python -m app.openttd_demo run
--random-world …`) is the product, not the corridor demo. On an
always-random recorded ramrom seed (0..4294967294), it generates one
256×256 temperate flat (terrain type 0) world starting 1950-01-01
(towns 3, industries 3 as used at check), analyzes the world's assets
(materials, industry factories, yields), plans with the CP-SAT optimizer
(P05), and plays on real OpenTTD 15.3 with the spectator GUI showing the
process. One continuous world stays alive across analyze → plan → play
cycles, growing the company, until nothing more forms; a fresh seed then
starts a new life. Closing the spectator window ends a phase softly
(ended-by-operator, never a system failure). The story lives in the game
window, the console, and a per-run HTML report — no web dashboard, no
in-window overlay. Every native attempt is user-gated per attempt, one
attempt, no retry. Honest typed failure (`NO_FEASIBLE_SERVICES…`) stays
in the vocabulary but must become the exception, not the rule.

## 2. The feasibility-fix decision (ticket 03)

Operator grant for the decision: the in-session directive "now develop
this software to production not demo, do until end of all tasks"
(2026-11-07) — the fix approach is decided by the diagnosis of record
(E139 + `.scratch/ramrom-product/research/01-feasibility-diagnosis.md`),
not re-opened for a menu.

**Diagnosis recap (the decided fix answers it):** 87.5% of candidates
died before any engine or supply facts existed, inside the ≤512-tile
anchor±2 capture rectangle — a silent distance gate — and both surviving
pairs died at one town-road band because the strips leave no room to
route around an obstacle. Engines (Balogh Coal Truck class, per wiki)
and supply were never the bottleneck; CP-SAT never got a chance to run.

**Fix of record: widen the capture seal.**

1. `capture_tile_limit` accepts 256 | 512 | **2048** (new production
   size of record). The 256/512 paths are byte-compatible with every
   retained identity (profile name, shapes, request arithmetic all
   unchanged at those sizes).
2. New region shape use: after the anchor bounding rectangle (+2 tiles
   per side, unchanged), the remaining budget is consumed by growing
   the **shorter axis** (the perpendicular-to-catchment direction), up
   to the `capture_edge_pad` budget (new field, default 6 tiles of
   extra perpendicular width per side), clipped at the map interior.
   Reason: detour room is the missing ingredient; growth is centered on
   the perpendicular axis where the traversal actually needs slack,
   and it is budget-capped so the capture read-cost stays bounded.
3. The plan of record keeps the typed failure surface intact:
   `CAPTURE_TILE_BUDGET` (relationship too spread to seal),
   `NO_BOUNDED_CORRIDOR` (terrain proves infeasibility inside the
   seal), `NO_SUPPORTED_FULL_LOAD_ENGINE`, and the final
   `NO_FEASIBLE_SERVICES` all remain honestly typed. Client-visible
   behavior changes only in that far more relationships are actually
   captured and only then gate-tested.
4. New 2048-tile surfaces get a distinct profile identity
   `random-rectangle-2048-v1` (never reinterpret a 512-v1 record).
   `RandomCaptureRegion`/`MAX_RANDOM_TILES` widen to carry it.
5. Command-of-record defaults: `run --random-world` defaults
   `--capture-tiles 2048`, `--capture-seconds 120`,
   `--capture-pad 6`; the operator can pin the legacy demo shape with
   explicit `--capture-tiles 512`.

**Acceptance bar of record (the seed battery):**

- Offline (must pass before any native grant): the widened-shape unit
  tests pin the allocation math (perpendicular first, budget-capped,
  interior-clipped, byte-stable at 256/512), and the two recorded
  seed-2026 strips re-derive their allocation offline from the retained
  facts bytes as fixtures.
- Native proof (each run its own operator grant, one attempt each, no
  retry): seed 2026 re-run under the widened seal as a NEW run identity
  (E139 is never relabeled or re-interpreted), then—if the operator
  grants the battery—seeds 7, 8, 9 as fresh one-shots. The bar: the
  battery produces ≥1 verified native plan + delivery cycle without a
  `NO_FEASIBLE_SERVICES` terminal, and every terminal of any battery
  run stays honestly typed in the report.

## 3. The continuous-world loop architecture (ticket 04)

Decision of record (decided with the operator's standing Q5/Q6/Q7
answers; remaining sub-choices fixed as below):

1. **Cycle shape.** One loop cycle = one native planning-and-execution
   round on the continuous world: re-read the live qualified month
   (fresh qualified observation, never stale facts — the wiki caution
   stands: towns grow roads and industries change), plan with P05/CP-SAT
   on the current economy, execute the selected services, verify
   deliveries, retain receipts, write the per-cycle report next to the
   run, and hand back to analysis on the same alive world.
2. **Re-entry mechanism.** Reconnect per cycle under the repo's
   existing reconnect discipline (one connect per cycle, no reconnect
   inside a cycle). Holding one AdminPort session across cycles is
   rejected for now: the executor's receipts and budgets prove one
   attempt per connection; re-entry via reconnect keeps that identity
   discipline without new protocol surface.
3. **Cycle end (soft).** A cycle's play phase ends when its selected
   services are verified delivered, OR the operator closes the window
   (ended-by-operator phase end, the loop waits for the operator rather
   than failing), OR its time budget expires. Closing the game window
   is never a system failure.
4. **Funds and inventory.** The company keeps its own money and
   purchased vehicles across cycles — the world is simply continued
   (the save of record after each cycle is the next cycle's before),
   no reset, no re-foundation.
5. **World abandonment.** A fresh ramrom seed is drawn only when K
   consecutive cycles form zero new services on the live world
   (K=2 of record: one zero-service cycle may be a slow month; two
   consecutive is the recorded call for a new life), or the operator
   ends the program.
6. **Recording.** Every cycle appends its own receipts, diagnostic, and
   HTML report under the run's directory; the run's final report indexes
   the cycles. The seed, cycle index, and world identity ride every
   record.

Implementation surface for §2/§3 is ticket 05 (build). The ticket-05
slice landed in this round is the §2 fix implementation with its offline
tests; the §3 loop engine is the remaining open work of that ticket.
Native proof runs need their own per-attempt grants; none existed when
this spec was written.

## 4. Out of scope

- Corridor Cargoflow-2 production line: no re-scoping of the fixed
  corridor, its sealed evidence, or E36/E114 rails (E36 stays open by
  its own rule; E114 stays UNKNOWN).
- In-window UI overlays and live web dashboards (operator chose
  game window + console + HTML report).
- Relabeling, re-running or regenerating any retained attempt byte.
- The controller's offline suite (legacy 53 reds): tracked in map fog;
  the full regression (including them) is the wayfinder EXIT gate, not
  run while map tasks remain open.
