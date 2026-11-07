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

## Status log (2026-11-07, Project Phase C offline round — FD-C-1/FD-C-2)

- Offline only: no OpenTTD launch, no AdminPort connection, no candidate
  staging or signing, no claim consumption, no native receipt, no
  `artifacts/` byte modified; one commit, no push. Full record:
  [docs/phase-c-reconciliation-feasibility-2026-11-07.md](phase-c-reconciliation-feasibility-2026-11-07.md).
- **FD-C-1 verified rather than rebuilt.** The 2026-10-18/10-25
  reconciliation chain (policy `vacant-projection-1`, ADR-012/013) was
  re-derived from the retained seed-17 census inputs: five reports
  byte-equal (reconciliation `c1cfa970…`, ADR-012 `221ce926…`, ADR-013
  `7616f626…`, combined rebinding `079fce64…`, ADR-012-only rebinding
  `c9d11d41…`) and the 19-tile unknown-occupancy diagnosis (`66ed07cc…`)
  JSON-value-identical only (retained serialization came from a one-off
  driver) — counts 83→77 definitional + 6 temporal + 0 contradictions +
  0 unresolved, sealed `SOURCE_SAVE_FUSION REJECTED` and retained
  `INCOMPLETE_TILE_CLASSIFICATION` untouched, 19 UNKNOWN tiles map to
  `TERRAIN_MODIFICATION` in the derived planning layer only
  (`p08_binding.allowed=true`, `p08_complete=false`). Focused suites 83
  passed.
- **FD-C-2 built and offline-verified.** New typed decision engine
  `app/planning/phase_c_feasibility.py` `phase-c-feasibility/1`)
  with ten required dimensions, the five outcome classes under a
  deterministic precedence (`UNSUPPORTED_CAPABILITY` > completed-search
  `INFEASIBLE_FOR_OBSERVED_WORLD` > `SEPARATE_SCOPE_EXTENSION` >
  `INCOMPLETE_EVIDENCE` > `FEASIBLE_…`), a typed P05 prerequisite gate
  mirroring `freight_native_network.py:178`, single-domain evidence rows
  that refuse Candidate-11/D5/fixed-scenario domains at construction
  (both as strings and by set-disjointness), fail-closed absence rows
  carrying real file digests, and limits regex-pinned against their own
  source bytes (drift refuses). 48 focused tests green.
- **Decision of record**: `artifacts/experiments/phase-c-feasibility-
  2026-11-07/feasibility-decision-report.json` (sha256 `67183cf6…31fa4`)
  — outcome **`INCOMPLETE_EVIDENCE`**: 2 VERIFIED dimensions
  (industry_cargo_compatibility, supported_map_search_limits), 8 PARTIAL,
  27 digest-pinned rows, zero observed-world-infeasibility rows (every
  recorded bounded random-world search was truncated). Recommended next
  action: the capture-pacing design decision (ticket-03 family) under the
  roadmap fences, then a fresh gated native capture round.
- Verification ledger: both suites 131 passed; ruff/format/`py_compile`
  clean on touched paths; `git diff --check` clean; `ty` reports 1
  diagnostic on the touched files (deliberate runtime-validated refusal,
  counted, never repaired).

## Status log (2026-11-07, Phase C continuation — ticket-05 loop engine built offline + M2 pacing decided)

- Offline only: no OpenTTD launch, no AdminPort connection, no candidate
  staging or signing, no claim consumption, no native receipt, no
  `artifacts/` byte modified; one commit, no push. Recorded at
  `.scratch/ramrom-product/issues/05-build-loop-product.md` (build record
  section), `.scratch/ramrom-product/map.md` and
  [docs/random-world-capture-pacing-decision-2026-11-07.md](random-world-capture-pacing-decision-2026-11-07.md).
- **Ticket-05 loop engine built offline.** `run_loops`/`loop_gate`
  (working-tree sha256 prefix `7c3e3155…`): sealed `loop_cycles` cycles run
  on ONE launch with one fresh connect per cycle (spec §3.2), per-cycle
  `loop-cycle-{k}` directories carrying byte-equal identity copies
  (PRELAUNCH.json/sha256, CLAIM.json, frozen-source.zip), their own
  runtime-identity, own before/qualified/after saves and their own
  artifact-manifest; runs report `NATIVE_LOOP_DELIVERED_VERIFIED` or
  `NATIVE_LOOP_ZERO_SERVICES`, with two consecutive zero-service cycles
  typing `abandoned_world` (§3.5 K=2) — never a relabeled defect.
- **`exclude=()` threading** (`freight_native_network.py`, `707d3446…`):
  loop cycles pass already-built `(source, destination, cargo)` identities
  into `network_from_facts`, which skips them before P08/P05 with
  `SERVICE_ALREADY_BUILT` rejections; an all-excluded set raises the typed
  `NO_FEASIBLE_SERVICES: all N captured relationships are excluded
  already-built services`. `execute_network` returns its selected services
  so exclusions derive in-process.
- **CLI `--cycles`** (`app/openttd_demo.py`, `394db0f4…`): sealed at prepare
  (recorded in PRELAUNCH.json only when > 1), 1..8 validated, requires
  `--random-world`; volume budgets (`requests`, `mutations`,
  `supplemental_requests`, `total_seconds`, `construction_commands`) scale
  linearly via `network_budgets(..., loop_cycles=k)` and every recompute
  site (preflight, verify_finance_receipt, verify_receipt,
  verify_network_receipt) passes the sealed count; legacy single-cycle
  metadata bytes unchanged (byte-parity asserted by the untouched suites).
- **M2 capture pacing decided** (`019c605e…`): pause the world clock around
  every random-world supplemental capture (`paused_world_clock`, one
  pause/resume pair per relationship, `pause_pairs`/
  `pause_resume_error` in the planning diagnostic); rejects page-critical
  reordering and any widening of the M2 gate; per-attempt fences and the
  first-run pause-stall risk (`PAUSED_CAPTURE_UNRESPONSIVE`) in the decision
  doc.
- **Tests of record:** new `tests/test_freight_loops.py` (14: exclude
  selects only new services, typed all-excluded raise, budget scaling,
  bounds, pause pair/failed-resume, loop_gate, prepare gates, CLI errors)
  plus touched suites; total 151 passed. ruff/format/`py_compile` clean,
  `git diff --check` clean, `ty` 1 pre-existing count diagnostic
  (`viewer.log.closed`), never repaired.
- **Still owed by the ticket:** the operator-granted native loop proof —
  one launch, `--cycles 2`, first cycle delivering ≥1 verified service,
  per-cycle replay via `verify` printing `verified_loop_cycles`, pacing
  fences observed. Command of record in the ticket file. The 53-legacy-red
  FULL regression remains the wayfinder EXIT gate, not run this round.
