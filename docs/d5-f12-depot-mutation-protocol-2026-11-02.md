# D5-F12-DEPOT — depot-connectivity mutation protocol (design + implementation of record)

Status: offline implementation round, 2026-11-02. Implemented and offline-validated
only. No OpenTTD launch, no AdminPort connection, no candidate staging into the
repo tree, no authorization signing, no claim consumption, no `artifacts/` write,
no Git mutation. `E58` §2.1 is the prescription of record; this record implements
it as a dedicated one-shot native mutation workflow so the F-12 depot-edge fix
never rides a `D5-FREIGHT-4` request. All historical candidates and census
results preserved byte-untouched; `E68`'s `FAILED_CLEANUP` verdict stays
unchanged.

## 1. Purpose and evidence base

`E57`/`E58` root-caused the v2 `site-00` `INVALID_SITE` halt to branch 4 (F-12):
OpenTTD 15.3 `AreRoadTilesConnected` requires the neighbor-facing road bit on
both tiles (`ottd/src/script/api/script_road.cpp:107-125`) and the depot tile
contributes only its exit bit (`ottd/src/road_map.cpp:54-70`), so both probe
directions hinge on a depot-facing (north) stub on road tile 45743 that no
retained operation ever built. `E58` §2.1 prescribes the fix, in order:

1. demolish the depot at tile 45487;
2. build the road pair `45743 ↔ 45487` (the span API needs `start != end`),
   which lays the missing north stub at 45743;
3. rebuild the depot at 45487 with front 45743 — `CmdBuildRoadDepot`
   (`ottd/src/road_cmd.cpp:1137`) auto-clears the pair's south bit on 45487 in
   the non-rotate path, keeping the rebuild legal; the north stub persists on
   45743.

Progress beyond hallmarks: before-gate and after-gate both probe
`AreRoadTilesConnected` **in both directions**; after-gate additionally
requires depot identity (`depot_present`, `front_read 45743`, owner 0,
`depot_linked`) to survive unchanged, and a final fleet read closing the phase
on the retained zero fleet of the D5 world.

## 2. Contract family decision

A new, non-retrofittable family: **protocol 10**, the next integer over
protocols 4/5/6/7/8/9 (additive-allocation precedent). Plan
`DepotMutationPlan` (attempt identity `D5-F12-DEPOT-1` feeds it):

- plan/schedule digest of record `8be74b2c651e35228618f06f177c2142dcc62edaf3d6b7bde3f7f6976e7ccc18`
- attempt `D5-F12-DEPOT-1`, milestone `D5-F12-DEPOT`, kind `depot-mutation`
- prelaunch schema `d5-f12-depot-prelaunch-v1`
- mutation profile `d5-f12-depot-mutation-profile-v1` (`permitted_ops`
  observe/demolish/road/depot/fleet, `mutating_ops` demolish/road/depot,
  `max_cost 3000`, `funds_readback_required`)
- cross-session guard `d5-f12-depot-cross-guard-v1`
- receipt `company-depot-mutation-receipt-v1`, phase outcome
  `depot-mutation-phase-outcome-v1` with MEASURED/REFUSED/MALFORMED kinds and
  prefix-preserving halt
- verdicts `F12_MUTATION_COMPLETION_VERIFIED` /
  `PHASE_HALTED_EVIDENCE_PRESERVED` / `AUTHORIZATION_UNVERIFIED` /
  `ATTEMPT_FAILED_EVIDENCE_PRESERVED`

Only `DepotMutationPlan` enters the depot pipeline (`_require_depot_plan`);
cross-family requests (protocol 5/6/9) cannot traverse the depot session and
vice versa — every frame class is refused before any handler runs.

## 3. Wire contract (`app/simulation/openttd/corridor_depot_mutation.py`)

Ops: `observe` (read-only before/after identity + both-direction connectivity),
`demolish` (tile 45487; signed cost — the refund class may credit −100),
`road` (tile 45487, front 45743; `start != end` enforced), `depot` (tile 45487,
front 45743 — the rebuild that auto-clears the pair's S bit), and `fleet`
(company 0 zero-fleet gate with bounded per-vehicle `in_depot` rows, ≤ 4).

Echo discipline: observe reads carry no tile; mutating exchanges ride exactly
`{tile}` or `{tile, front_tile}`; `max_cost` is the pinned 3000 echo; refusal
readbacks carry echoes and funds only, never an unclaimed observation set.
Success readbacks for observe must carry the complete six-fact gate set
(`depot_present`, `front_read`, `owner`, `depot_linked`,
`connected_front_to_depot`, `connected_depot_to_front`); fleet success must
carry `count` and ascending rows. 512-byte request/response bounds with the
largest possible fleet response measured inside the wire margin.

Funds chain of record — the phase enforces
`funds_after == funds_before - cost` verbatim across all six exchanges over
opening `FUNDS_AT_F12_OPEN = 490257`:
490257 (before-00) → 490357 (demo-00, refund −100) → 490157 (road-00, +200) →
488957 (depot-00, +1200) → 488957 (after-00) → 488957 (fleet-00).

## 4. Execution schedule (exact: six planned exchanges)

| exchange | op | tile | front_tile | purpose |
|---|---|---|---|---|
| before-00 | observe | — | — | E58 diagnosis verbatim; HALT before any mutation on divergence |
| demo-00 | demolish | 45487 | — | refund-class credit, plan pin `(45487, None)` |
| road-00 | road | 45487 | 45743 | the pair build laying 45743's north stub |
| depot-00 | depot | 45487 | 45743 | the rebuild; auto-clears 45487's S bit |
| after-00 | observe | — | — | same identity; **both directions connected true** |
| fleet-00 | fleet | — | — | zero fleet with per-vehicle `in_depot` rows on any halt |

Budgets: 1 launch / 1 connection / 32-request one-shot / max_cost 3000 /
expected funds 490257. `state_changed` is true when at least one mutating
exchange stands READY; a phase with only observe/fleet readbacks is not a
mutation.

Gates of record (fixed facts, never invented measurements): the before-gate is
E57's measured diagnosis verbatim — depot present, front_read 45743, owner 0,
depot_linked true, **both** `AreRoadTilesConnected` directions **false** — and
the after-gate is the same identity with both directions **true**. Any
divergence halts `STALE_PIN`/STALE-identity with the measured-vs-prescribed
verbatim in the error (halting evidence, never a degraded gate). The fleet
gate demands count 0; a non-zero fleet halts listing every row
`id/tile/in_depot`.

## 5. Hypothesis state of record

`RETAINED_E58_REBOUND`: the hypothesis state re-binds the E58 design doc
(`docs/d5-freight-4-f12-branch8-design-resolution-2026-11-02.md`) by path +
sha256 `39b44853ffdf9c51856f17ec9027d086d50cd685d1dc240bdaa45f20ce96d6b8`
through the depot precondition-derivation pipeline; with the doc absent the
state is `RETAINED_E58_ABSENT` (fail-closed, never invented). Tests cover both
arms; preflight refuses a PRELAUNCH.json whose hypothesis state drifted.

## 6. GameScript package (`app/simulation/openttd/d5_depot_mutation_package/`)

Composed package separate from the frozen families' sources; the
`depot_planned` table and the pin constants (`depot_tile 45487`,
`depot_front_tile 45743`, pickup 45748, delivery 50351,
`MAX_DEPOT_MUTATION_COST 3000`, `DEPOT_COMPANY 0`, `MAX_FLEET_ROWS 4`) are
byte-pinned against the Python schedule of record by a native test that reads
the shipped package bytes. Bridge `NetworkFreightProof extends
D5DepotMutationProof`; ready marker `D5_F12_DEPOT`, log prefix discipline and
the one-shot 32-request budget with duplicate drop mirror the census handler.

## 7. Native pipeline (`app/simulation/openttd/proof/corridor_depot_mutation_native.py`)

Staging/preflight/run/verify over the imported frozen machinery, exactly as
the survey/census pipelines are:

- prerequisite lineage re-binds the shared survey binding A1
  (`D5-CORRIDOR-EXTENSION-3`, after-save
  `3748e00ce57bcb076466f50cac3776c202b4fd130d6c6071935e9d43e45420bd`) through
  `depot_prerequisite_binding` over `survey_prerequisite_binding(version=2)`;
  anything else refuses at staging ("requires the pinned A1").
- `prepare_depot_mutation_candidate` composes the workspace, freezes the
  manifest, and preflights offline; staging into a caller-owned path only.
- `verify` replays fail-closed: claim→seal binding, manifest exhaustiveness,
  schema check, authorization-state call, frame-correlated six-exchange
  phase replay against the wire contract, result-label consistency
  (`native_launches`, `requests`, `mutated` inventory), durable response
  files, cleanup certification, and the attempt-identity drift/floated
  refusal classes. A forced `NATIVE_DEPOT_MUTATION_COMPLETE` label without a
  consumed authorization verifies as `AUTHORIZATION_UNVERIFIED`, never as a
  completion.

## 8. Tests of record (offline, 73 passed exit 0)

- `tests/test_corridor_depot_mutation.py` — 29 wire tests: pinned schedule/plan
  constants and digest stability, request byte audit and verifier refusals,
  parse echo subsets (tile/front echoes, funding costs, fact completeness,
  refusal observability boundaries), full-schedule funds chain, before-gate
  divergence matrix (six facts × wrong values), after-gate both-directions
  matrix, fleet halt rows, funds-chain-break halt, ceiling refusal,
  refusal/malformed fail-closed, out-of-order/unscheduled refusals, plan-drift
  gates, plus the Squirrel VM scaffolding fixtures the VM suite imports.
- `tests/test_corridor_depot_mutation_vm.py` — 8 tests through the real
  Squirrel VM: full schedule + ready markers, real stub-world mutation
  (before/after facts, the stub cost chain −100/200/1200), road/depot echoes
  and tile shapes, refusal ladder (INVALID_COMPANY / STALE_PIN / PAUSED /
  OUT_OF_ORDER / latched halt), 32-request budget + duplicate drop, foreign-
  shape drops (protocol 5/6/9, non-hex plan, off-echo max_cost, tile-on-observe,
  start==end span).
- `tests/test_corridor_depot_mutation_native.py` — 36 tests: plan-model
  exclusivity, cross-session guards, pinned schedule/requests, staged lineage
  metadata, foreign-attempt-id absence, A1 prerequisite binding, source-save
  identity, staged composition/reuse, authorization-payload re-derivation,
  preflight re-derivation + seal/attempt/schema/kind/milestone/schedule/
  profile/world/hypotheses tamper matrixes, hypotheses over the E58 record
  sha + absent-doc arm, expected-readback policy, exchange pair persistence,
  malformed/stale/empty-reply refusals, exact 512 bounds, frame replay parser,
  unconsumed fail-closed, claim-mismatch/stray/unknown-schema refusals,
  attempt-identity matrix, exit-status discipline, the synthetic consumed
  attempt verified end-to-end through the production replay (funds chain,
  gates, mutations, fleet, before/after facts), tampered receipt/response/
  result refusals, the shipped-package pin-table binding, and cross-family
  parse refusals.

Static checks: `ruff` clean on all six touched paths; `uvx ty check` clean;
`git diff --check` clean; `CONTEXT.md` sha256 unchanged
`36648f9c2fee4106efb35ae4ee8722983ebdfb482889e66ad53d759f6fa7cc29`.

## 9. Implementation disclosures (this record)

1. One real implementation defect found by the offline native suite and fixed:
   the per-row plan-pin preflight check rejected `demo-00`'s legitimate
   `depot_front=None`; the check now accepts a None front on the pre-connection
   demolish row and still refuses a drifted front.
2. One real fixture defect in the synthetic consumed attempt fixed: the
   after-00/fleet-00 funds must stand at the post-depot level (488957), not at
   the opening level, for `funds_after == funds_before - cost` to hold.
3. The over-ceiling refusal is enforced by `depot_phase_outcome` on mutating
   exchanges' signed cost; parse itself carries no ceiling on `funds` echoes —
   covered by the dedicated wire test instead of an exchange-helper probe.

## 10. What this record does not do

No staging into the repo tree (`prepare` blocked), no signing, no launch, no
AdminPort connection, no claim consumption, no `artifacts/` write, no census
rerun, no `D5-FREIGHT-3` rerun, no relabel of any retained verdict (`E68`
stays `FAILED_CLEANUP`), no Git mutation. Remaining ungranted operator gates,
in order: staging approval for a fresh `D5-F12-DEPOT-1` candidate under its
own seal → independent read-only review → Gate C signing → one separate
explicit launch approval. Nothing here authorizes or performs any of them;
`REPRODUCE.md` carries the commands of record for later rounds.
