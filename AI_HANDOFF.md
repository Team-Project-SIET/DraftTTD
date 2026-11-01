# OpenTTD AI handoff — 2026-10-17 (V2-capture addendum 2026-10-18)

This is a vendor-neutral continuation guide for the **actual local worktree**.
Read [CONTEXT](CONTEXT.md), this file, [TASKS](TASKS.md),
[EVIDENCE_INDEX](EVIDENCE_INDEX.md), then [REPRODUCE](REPRODUCE.md).
Use repository files and retained evidence as authority; prior chat, provider
memory, personal skills and temporary agent directories are not prerequisites.
This documentation task authorizes no game launch, AdminPort connection or retry.

## Checkout and transfer

Repository: https://github.com/Team-Project-SIET/softdev2.git
Branch: `devmodule2`. Inspected HEAD and stable playable-demo checkpoint:
`a3480169dcbefefff7b1adfb060449643c8eb04c`.
Primary target: OpenTTD 15.3, Linux amd64; Python 3.14+.

HEAD alone is incomplete: Random World, distance support and substantial earlier
engineering remain modified/untracked locally. See the exact
[status inventory](docs/handoff/2026-10-17/git-status-before.txt),
[tracked diff summary](docs/handoff/2026-10-17/tracked-diff-before.stat),
[implementation hashes](docs/handoff/2026-10-17/implementation-before.json) and
[ignored path inventory](docs/handoff/2026-10-17/ignored-paths-before.txt).
These are inspection snapshots, not commits or a substitute for file backups.
Preserve the unknown untracked root file `--version`; do not execute it.

Uncommitted implementation includes demo orchestration/monitoring/random staging,
P05 contracts/selection, P08 roads/network generation, supplemental capture,
freight runtime/replay, GameScript planner/funding, canonical fleet, continuous
operation/capacity, terrain preparation/proofs and associated tests. A change
being present here does not imply it was published or accepted natively.

Transfer tracked modifications and untracked source/tests/docs along with the
Git history. Transfer ignored evidence separately through a reviewed secure
archive; it is not backed up by Git. Exclude `.env`, private keys, account/cache
folders and temporary credentials. Preserve frozen attempt bytes and required
provenance paths. Missing artifacts on another machine are **UNKNOWN**, not a
reason to regenerate historical evidence. Compare hashes after transfer.

No AGENTS.md was found in this repository or its ancestor chain. Existing CONTEXT,
specifications, validators and evidence-preservation contracts apply. Recheck for
additional rules in the destination checkout. No Git staging, commit or push was
performed for this handoff. Older handoff versions are preserved under
[the dated snapshot](docs/handoff/2026-10-17/previous-AI_HANDOFF.md).

## Current evidence-backed state

VERIFIED below means supported by inspected retained reports, within the stated
scope. This handoff did not repeat native execution or comprehensively replay
all historical packages. Fresh controlled validation is recorded in REPRODUCE.
PREPARED is implementation awaiting native qualification; PARTIAL is incomplete
acceptance; FAILED is an immutable consumed outcome; UNKNOWN means missing facts.

| Area | State and boundary |
|---|---|
| Stable fixed demo | VERIFIED native 15.3 gameplay: P08/P05 selected 3 freight services, vehicles 4/5/6 constructed, 60 coal delivered, £1,022 revenue; spectator joined/inspected; fresh P07, cleanup and evidence checks passed. E1. |
| Canonical creation Q3 | PROVEN in retained native engineering evidence; result `CANONICAL_CREATED_PENDING_FRESH_PROCESS_RELOAD`, 1 launch/connection, 27 mutations. E2. |
| Fresh-process reload Q3 | PROVEN reload-only: `CANONICAL_RELOAD_ONLY_VERIFIED`, exact semantic correspondence, 1 launch/connection, 0 mutations. Purchase/dispatch/unpause disabled. E2. |
| Attempt 19 | Five economy years recorded, original native terminal FAILED at finalization (`company-policy.json` already existed). Separate offline recovery valid within derived scope; never relabel original terminal. E3. |
| Random World implementation | Controlled/offline implementation available in dirty tree; native generation/discovery/GUI verified in Seed 17, native service execution remains unverified. E4/E5. |
| Tile Classification V2 capture | NATIVE VERIFIED capture completed 2026-10-18 (90/90 pages, 450/450 tiles, schema 2, staged AI + GameScript startup, zero script deaths, 0 mutations, cleanup PASS); SOURCE_SAVE_FUSION verdict **REJECTED** — 83 projected-flag disagreements, nothing fused; the 19 historically UNKNOWN tiles were observed CLEAR in the fresh census and stay UNKNOWN in the retained assessment; P08 remains `INCOMPLETE_TILE_CLASSIFICATION`. E16. |
| D4 corridor construction | Native road + station construction PROVEN for the reviewed v3 scope (candidate-5, `RECEIPT_VERIFIED`, authoritative after-save `a81ac836…ef261`; £492,149 funds pin). E35. |
| D5 corridor freight | ATTEMPTED, NOT DELIVERED: `D5-FREIGHT-1` consumed with the native delivery-stop cargo-1 acceptance 0 finding of record; no freight delivery, no OPEX/profit fact. M8 optimizer route-selection NOT demonstrated (no competing executable route). E36. |
| D5 corridor extension | A0 SURVEY COMPLETE — VERIFIED NATIVE (E40); A1 NATIVE COMPLETE, VERIFIED (`D5-CORRIDOR-EXTENSION-3` consumed, `EXTENSION_COMPLETION_VERIFIED`, after-save `3748e00c…5420bd`, funds £490,257; E42–E44, phase-a §15–§17). **POST-A1 CENSUS OFFLINE IMPLEMENTATION COMPLETE (E46, design §8)**: protocol-6 retargeted to `D5-ACCEPT-SURVEY-2` — version selector `SURVEY_SCHEDULE_VERSION = 2` + versioned plan contract in the wire module (v1 plan digest `2d2e47b2…02e7` byte-preserved, consumed candidate-1 still replays `SURVEY_COMPLETION_VERIFIED` through the production verifier), native versioning on the extension precedent (attempt map, schema map, prerequisite pins with v2 = consumed A1 candidate-3 end-to-end re-verified), 4-exchange census (radius-00, accept-00 control 50351 = 0, accept-01 stop 50862, prod-00), B1 GameScript re-bake (4 rows, `ACCEPT_CANDIDATES [50862]`, no handler-logic change), suites green (65 + four-suite 148/1-skip + freight 42 + A1 240-baseline). **CENSUS FRESH CANDIDATE STAGED, READY-FOR-GATE-C (E47, design §9)**: `d5-accept-survey-native-candidate-2/` staged offline via production `prepare` → `PRELAUNCH PASS`, read-only `preflight` → `PREFLIGHT PASS`, `verify` → `AUTHORIZATION_UNVERIFIED`/`CLAIM_ABSENT` (exit 1); seal `237a4f84…37daa4`, v2 plan digest `67fce856…80be2`, schedule digest `1222db02…389d`, authorization payload digest `b1f3e209…00bd`, world = A1 after-save `3748e00c…5420bd` (staged source.sav verified), hypotheses {50351: 0, 50862: 8}, funds 490,257 proven from A1 route receipts, frozen closure 3,491 entries, no authorization/claim/journal anywhere; independent fresh-context prerequisite inspection `PREREQUISITE VERIFIED` and staged-byte review `READY-FOR-GATE-C` (0 blockers/majors/minors). **GATE C OPTION-1 SIGNED (E48, design §10)**: `AUTHORIZATION.json` written exactly once after full identity re-validation and clean refusal gates; record sha == `authorization_sha256` `d87c2c450e192e4341f8bf4ac6a6ff553194ac0134f8353293bff42250bf4ae3`, `operator_key_identity` `sha256-ed25519-public-key:cbb63ff5…c614`, payload binds attempt `D5-ACCEPT-SURVEY-2`/milestone `D5-ACCEPT-SURVEY`/seal `237a4f84…37daa4`; seed env-only and cleared after final use; two earlier internal script invocations refused cleanly before any write (recorded in §10); post-signing `verify` → `AUTHORIZATION_UNVERIFIED`/`CLAIM_ABSENT` (exit 1), `preflight` → `PREFLIGHT PASS`, exactly one new file in the candidate root; all consumed precedent records re-sealed byte-identical. **Nothing claimed, launched or executed for the census**; remaining gates: the separate native launch approval, then the census report — each its own operator gate. Freight delivery and M8 route-selection proof remain separate future attempts; wheel reachability, road-bit directions and pathfinding stay UNKNOWN (census proves acceptance only, never traversal). E37–E47, phase-a record §10–§17, [design doc](docs/d5-post-a1-acceptance-survey-design.md) §1–§9. |
| Seed 17 smoke | FAILED under old capture-area gate; no service construction/delivery; P05 NOT_RUN. E4. |
| Larger random capture | Controlled/offline correction, no new native run: 512 fully observed tiles per rectangle; fixed demo stays 256; road path stays 47. E5. |
| Fourth vehicle / matched experiments | Native intervention and matched A/B outcome not established by reload-only Q3. Retain as future scoped work. |
| OpenTTD 13.4 proofs | Historical regression evidence only; cannot establish 15.3 compatibility. |

The fixed demo remains the stable default. Its CLI is:

```bash
.venv/bin/python -m app.openttd_demo --view-seconds 300
```

This command **launches native processes**; use only under separate runtime
authorization. The client is a spectator. Direct player control of the
Python-operated company is unsupported. Services run serial delivery batches,
one vehicle per service, then trucks park. Revenue is timing-dependent and is
not profit. The bundled Attempt 17 sample (£1,018) is a different run.

## Architecture map and code entry points

```mermaid
flowchart LR
  CLI[Python demo CLI] --> R[Isolated OpenTTD runtime]
  R --> O[Qualified world and supplemental facts]
  O --> P08[Bounded P08 road candidates]
  P08 --> P05[P05 CP-SAT selection]
  P05 --> P[Validated ExecutionPlan]
  P --> C[Checked freight compiler]
  C --> A[Encrypted AdminPort and GameScript]
  A --> N[Company commands and independent readback]
  N --> V[Retained receipts and replay]
  V --> P07[P07 evaluation and reports]
```

| Responsibility | Read these files when changing it |
|---|---|
| Public fixed/random CLI, spectator lifecycle | `app/openttd_demo.py`, `tests/test_openttd_demo.py`, `examples/openttd-demo/README.md` |
| Random recipe, discovery, budgets, diagnostics, bounded solver | `app/demo_random.py`, `app/demo_random_native.py`, `tests/test_demo_random*.py`, `tests/test_random_*.py` |
| Native lifecycle, isolated assets/configuration, cleanup/retention | `app/simulation/openttd/proof/freight_delivery.py`, `proof/harness.py`, `runtime/`, `proof/ownership.py`, `proof/historical_protection.py` |
| Qualified observations and complete supplemental capture | `freight_runtime_planning.py`, `supplemental_planning_facts.py`, `world_planning_observation.py`, `planning_fact_input.py` under `app/simulation/openttd/` |
| P08 adaptation/road search/network composition | `app/planning/p08_adapter.py`, `p08_road.py`, `p08_network.py`, `preparation/` |
| P05 pure selection and contracts | `app/planning/domain.py`, `canonical.py`, `optimizer.py`, `validation.py`; `docs/specs/planning-executor-boundary.md` |
| Compile/admit/execute/replay | `app/simulation/openttd/freight_planning.py`, `freight_native_network.py`, `freight_delivery.py`, `freight_planning_replay.py` |
| Wire transport and native bridge | `gamescript_transport.py`, `secure_admin.py`, `freight_delivery_package/*.nut`; planner, network and funding composition is staged by the Python proof runner |
| P07 and operational monitoring | `app/planning/network_cli.py`, `app/experiments/freight_network.py`, `app/demo_operations.py`, `tests/test_demo_operations.py` |
| Canonical state/save/reload | `app/simulation/openttd/proof/canonical_fleet.py`, `freight_canonical*.py`, package `canonical*.nut`; `docs/capacity-experiment.md` |

Python owns optimization, identity, validation, deadlines and evidence binding.
GameScript executes synchronous commands under `GSCompanyMode`, returns bounded
correlated messages and exposes readback. Keep route optimization in Python.
P05 selects supplied candidates; P08 is bounded flat-land routing. Neither is
OpenTTD YAPF or an arbitrary-world route planner. Source trust and prepared-save,
world/scenario/plan identities remain mandatory through compilation and replay.

Random staging adapts the fixed bridge to 256×256 and sealed budgets. Editing the
base `.nut` source alone is insufficient: inspect staged package correspondence,
legacy sealed profiles and independent replay. GUI lifecycle owns only its client;
cleanup must reap owned processes, close sockets, remove credentials and dispose
owned workspaces while retaining observations. PostgreSQL is optional research
persistence, not a prerequisite for the public demo.

## Random World limits and Seed 17

Read [random demo](docs/random-world-demo.md) for interfaces and CLI, and
[distance correction](docs/random-world-distance-support.md) for the current gate.
Native generation accepts explicit seed/settings, supports 256×256 only, observes
at most 32 industries, considers at most 16 relationships and selects up to
8 services/vehicles. One vehicle per service; effective capacity is the smaller
service/vehicle ceiling. P05 is bounded to 1–60 seconds. Fixed Scenario is default.

Seed 17 used temperate, terrain 0, towns 1, industries 2. Retained native evidence
shows 10 industries, 11 cargo types and six compatible relationships, with native
generation, discovery and spectator navigation verified. All six failed the old
256-tile **rectangular area** limit, not a 256 Manhattan-distance limit.
No service was built/delivered and P05 did not run. Funding setup is separate from
service construction; the smoke records one funding mutation.

| Cargo | Manhattan distance | Rectangle area (tiles) | New 512-tile capture admission |
|---|---:|---:|---|
| Coal | 37 | 450 | YES, observation only |
| Wood | 185 | 1122 | NO |
| Livestock | 260 | 17947 | NO |
| Grain | 260 | 17947 | NO |
| Oil | 179 | 8436 | NO |
| Iron ore | 94 | 2457 | NO |

New random profile `random-rectangle-512-v1` requires every tile and both declared
cargo-coverage scopes, 45 seconds per capture and at most 546 reads. The global
guard is `(capture_tile_limit + 36) × max_relationships + 1` (8769 at 16).
Replies remain bounded to 512 bytes, with exactly 19 integers per tile response.
Fixed and legacy sealed random captures remain 256; preserve their old identities.
Native road paths still require 2..47 road tiles and independent admission.

The consumed Seed 17 run has no planning tile/engine capture. Terrain, vacancy,
catchment, compatible engine/capacity and costs are missing. Coal admission only
means 450 tiles fit the budget. The synthetic flat fixture's 31-road-tile route,
one selected service and £1,830 estimated construction/purchase are CONTROLLED,
not Seed 17 native results. A new native run needs fresh reviewed frozen inputs
and separate authorization. Never retry a consumed identity.

## Reports and financial boundaries

Terminal monitoring reads existing retained files, adding no Admin requests.
P07 final reporting requires independent replay of native receipts. Outputs include
`results.md`, `evaluation.json`, `operations.html`, SVG charts and
`operational-history.json`; comparisons retain distinct seed/config/experiment
identities. Failed planning retains JSON/HTML diagnostics, not delivery receipts.

Keep OBSERVED native measurements, DERIVED aggregates/rates and CONTROLLED inputs
separate. Missing samples are UNKNOWN. Cargo waiting is a backlog point sample,
not demand. Milestone rates use script ticks and include serial setup/waiting;
they are not steady-state throughput. Full OPEX, net profit and ROI remain UNKNOWN.
Unallocated cash decreases do not establish operating expense categories.

## Preservation and next action

Preserve every consumed attempt, seal, source archive, save, manifest, log and
terminal result. Offline recovery belongs in a separate derived directory.
Do not reset/clean, broad-stage, overwrite historical files, recreate consumed
packages, weaken correspondence checks or infer runtime proof from controlled tests.
Use a reviewed staging allowlist only if a later commit is explicitly requested.

Next (per the 2026-10-18 addendum): the Seed 17 smoke and the Tile
Classification V2 capture are consumed (E8, E16). The open continuation is the
offline semantic reconciliation of the fresh V2 census against the historical
TileFact projection — analyzing the 83 `PROJECTED_FLAGS_DIFFER` disagreements,
the 19 fresh-CLEAR/retained-UNKNOWN tiles and the resulting feasibility
statement — which needs its own reviewed record; anything beyond offline
analysis requires fresh, separately authorized frozen inputs. Stable demo
verification and canonical engineering do not remove the missing random facts.

Next for D5 (per the 2026-10-31 record): D5-CORRIDOR-EXTENSION-3 **Phase A-A0
is COMPLETE — VERIFIED NATIVE (E40)**: candidate-3 `D5CE3-SURVEY-3` was
launched exactly once under all operator gates, the one-shot claim was
consumed, the replay verdict is `SURVEY_COMPLETION_VERIFIED`, cleanup is
certified, and the ten-exchange survey observed delivery-stop tile `50862`
at 8/8 cargo-1 acceptance (control `50351` 0/8). The candidate is consumed
history: never re-run, re-signed or re-claimed; candidate-2 (stale,
never-consumed) stays preserved untouched. The next step is **A1
(corridor spur + bay-truck-stop construction, phase-a §1 solver work)**, a
separate native attempt: its **v2 design is now carried offline (2026-11-01,
phase-a §14, E41)** — the postmortem §3 four-op schedule (dedicated `spur`
road op 50864→50863 then the bay stop 50862 fronting 50863 with
`STATION_NEW`) is implemented in the shared protocol-4 contract, the
extension staging pipeline (`EXTENSION_SCHEDULE_VERSION = 2`, attempt
`D5-CORRIDOR-EXTENSION-3`) and the GameScript handler, validated by the
five focused suites (240 tests) plus a read-only replay of the consumed v1
candidate-2 that still returns `ATTEMPT_FAILED_EVIDENCE_PRESERVED`. What
remains for A1 is exactly the gated sequence: a fresh never-consumed
candidate staging (`d5-corridor-extension-native-candidate-3`), PRELAUNCH
plus independent review, Gate C Option-1 signing and a separate explicit
launch approval. All of the signing-side work is now done (2026-11-01,
phase-a §16, E43): the candidate is staged, reviewed (READY-FOR-GATE-C)
and Gate-C-signed — `AUTHORIZATION.json` sha
`371a524b85add4347a991478909a04da3e7dac8b62b2636b6c7694b32bebe200`
verified under the pinned production anchor (operator identity
`sha256-ed25519-public-key:cbb63ff5…40c614`) over seal
`404d42d9…6acd8` / payload `c511dd38…f94f`; `PREFLIGHT PASS`; claim and
launch-consumed markers absent; `verify` →
`AUTHORIZATION_UNVERIFIED`/`CLAIM_ABSENT`. The remaining gate for A1 is
a separate explicit operator launch approval, then a single native
attempt through the remediated lifecycle. The attempt has now been
granted and executed exactly once (2026-11-01, phase-a §17, E44):
exit 0, `NATIVE_EXTENSION_VERIFIED` — all four v2 ops built and
independently confirmed (spur 50864→50863 and bay stop 50862 fronting
50863 included), route `ROUTE_VERIFIED` 30/30 pairs with funds read
natively £490,257, replay `EXTENSION_COMPLETION_VERIFIED`, certified
cleanup all-true, manifest 0 mismatches, claim consumed once. The
remaining D5 A1 gate is the cargo-1 acceptance census on this
attempt's after-save (a separate read-only survey session, required
before any freight order or vehicle purchase); freight delivery and
M8 route selection remain unproven and are never covered by A1. The
census is now designed offline (2026-11-01,
[docs/d5-post-a1-acceptance-survey-design.md](docs/d5-post-a1-acceptance-survey-design.md),
E45): a versioned `D5-ACCEPT-SURVEY-2` retarget of the protocol-6
survey pipeline bound to the consumed A1 candidate-3 after-save
`3748e00c…5420bd`, 4-exchange census (radius 3 first, control 50351
= 0, stop 50862 = 8/8, prod 104), zero mutation, replay
`SURVEY_COMPLETION_VERIFIED`; independent review applied (v2
GameScript pin-table re-bake required; plan contract versioned).
**The implementation of that design is complete offline (2026-11-01,
E46, design §8), the fresh census candidate
`d5-accept-survey-native-candidate-2/` is STAGED, READY-FOR-GATE-C
(2026-11-01, E47, design §9: seal `237a4f84…37daa4`), and Gate C
Option-1 signing is EXECUTED (2026-11-01, E48, design §10:
`AUTHORIZATION.json` record sha `d87c2c45…4ae3`, verified under the
production anchor; signature only — no claim, no launch).** The
signature is a prerequisite, not approval: the separate explicit
native launch approval is the next operator gate; freight delivery
and M8 stay unproven. Freight
delivery and M8 route-selection proof remain separate, unsatisfied D5
requirements and are never covered by the A0 survey. CONTEXT.md is not
edited here: its bytes stay pinned by the E26 authority record.

## Shared language for continuation

**Canonical constructed fleet**: The common paused state containing the three
original services and three stopped empty vehicles, before intervention or dispatch.
A matching DTO alone is not native state correspondence.

**Matched arm**: A separately authorized experimental branch of that same verified
canonical state. Historical Attempt 19 is a contextual baseline, not matched arm A.

**Native terminal result**: The immutable result of a consumed game-process attempt.
Separate derived offline recovery does not change that result.

**Prepared qualification**: Frozen inputs and controlled checks awaiting separate
native authorization. It is not an accepted save, reload, or experiment.

## CONTEXT.md addendum status (not committed)

The 2026-10-18 header addendum to [CONTEXT.md](CONTEXT.md) — the brief current
handoff plus the shared-language definitions above — is prepend-only and remains
in the working tree, but is NOT included in the documentation commit: repo-root
CONTEXT.md bytes are pinned by retained authority manifests captured
2026-10-08 (sha256 b94b966...) — the two historical-integrity.json
freezes (attempt1, prelaunch-v4) and the structural-world-real-prelaunch
source-freeze.json — and the file has drifted past those pins since
bdbec43 (2026-10-11), so both protected-authority tests and
test_industry_production_proof::test_architecture_authority_unchanged
fail at baseline independently of this update. Resolving that conflict requires a separate,
explicitly authorized pin-repair or re-capture decision; until then no byte
change is landed into git history for CONTEXT.md. The disputed addendum text is
duplicate here so it is not lost.

## Starter instruction for the next AI provider

> Work in this repository on `devmodule2`. Read CONTEXT.md, AI_HANDOFF.md,
> TASKS.md, EVIDENCE_INDEX.md and REPRODUCE.md before editing. Verify live Git
> identity/status against the dated snapshot; preserve all dirty and ignored
> evidence. Continue with the offline Random World readiness task in TASKS.
> Keep the fixed demo stable. Do not launch OpenTTD, connect to AdminPort, retry
> a consumed attempt, overwrite evidence or stage/commit/push without the relevant
> explicit authority. Report native observations, controlled results, derived
> recovery and missing facts separately. Use source files and local reports,
> not assumptions from earlier provider conversations.

The final documentation/architecture review is recorded in
[review.md](docs/handoff/2026-10-17/review.md).
