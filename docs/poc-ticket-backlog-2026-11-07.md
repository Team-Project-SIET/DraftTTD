# Full-Scope Functional PoC — ticket backlog (2026-11-07)

Round record for the ramrom-product wayfinder effort
(`.scratch/ramrom-product/map.md`). Objective of the round: close the
books on 2026-11-07's two natively executed attempts and resolve the
feasibility-diagnosis research ticket, all offline over retained bytes;
native-run grants for the fix proof remain per-attempt decisions of the
operator.

## Status log (2026-11-07)

- Books of record for the two one-shot native attempts of this day:
  (a) the random-world seed-2026 run
  `artifacts/demos/playable-demo-3e93cc7d1e8d43aab66a4f653665caaa` — typed
  terminal `ValueError: NO_FEASIBLE_SERVICES: no supported full-load road
  engine and supply`, `result.json` status FAILED, connections 1, requests
  0; artifact manifest 1556/1556 verified; cleanup all-true; no openttd
  process remained. Evidence index E139.
  (b) the seed-42 demo run
  `artifacts/demos/playable-demo-1570c66a2e564613a102b3e95647e8b1` —
  typed FAILED when the operator closed the game window mid-run
  (`RuntimeError: Graphical client exited (0)`); P05 had selected 3
  services, 33 construction mutations and 1 funding mutation landed,
  deliveries did not finish before the close; one attempt, no retry.
  This run is the recorded evidence behind the soft-close design clause
  of the ramrom product. Evidence index E140.
- Research ticket `01-feasibility-diagnosis.md` resolved (offline, zero
  native attempts): the funnel of record is capture-seal geometry — 14/16
  compatible relationships rejected `CAPTURE_TILE_BUDGET` before any
  engine/supply facts were gathered; discovery truncated at the
  16-relationship cap (`CANDIDATE_SEARCH_LIMIT`, 146 of 8192 pair
  checks); the 2 captured coal relationships then failed
  `NO_BOUNDED_CORRIDOR` both times at the same town-road band
  (x≈183..192) inside detour-free strips, reproduced on the raw capture
  bytes offline; the engine catalog (Balogh Coal Truck, engine 123) and
  supply gates were never the bottleneck; CP-SAT was never invoked.
  Findings file of record:
  `.scratch/ramrom-product/research/01-feasibility-diagnosis.md`
  (§1–§7 byte-cited; §8 OpenTTD-wiki verification addendum).
- Legacy 53 offline reds: untouched, tracked in the map fog; the full
  regression (including them) stays the wayfinder EXIT gate per the
  operator's standing decision — not run while map tasks remain open.
- No native run this round; no grant consumed; no `artifacts/` byte
  modified; conservation of supersession: failed and aborted attempts
  recorded at their own identities, never relabeled.

## Status log (2026-11-07, granted native proof of ticket 03)

- The operator granted ONE native attempt in session: the widened-seal
  command of record on seed 2026, world settings of record (towns 3,
  industries 3). The attempt ran once and is recorded honestly at its own
  identity (`artifacts/demos/playable-demo-9b9a398e406f4ec1bf8e37a69116ac93`,
  evidence index E141). Typed terminal:
  `PlanningFactError: supplemental capture outside final M2 month` — the
  qualified-month gate refused fact capture whose economy dates crossed the
  M2 window end (712282) at live game speed. Relationship n0 captured
  completely (832 reads) inside the window; n1 was interrupted at read 703;
  2238 capture reads completed overall; no `NO_FEASIBLE_SERVICES` and no
  engine/supply rejection occurred — the funnel advanced past both E139
  gates. The acceptance bar `≥1 verified plan+delivery terminal` is NOT
  met by this run; it stays open evidence-indexed, not relabeled.
- Next decision of record (unresolved): capture-read pace must fit the
  qualified in-game month — the candidate design is pausing the world
  clock during fact capture (recorded in the diagnostic), or an equivalent
  pacing boundary. No further native attempt is scheduled without a fresh
  per-attempt operator grant.
