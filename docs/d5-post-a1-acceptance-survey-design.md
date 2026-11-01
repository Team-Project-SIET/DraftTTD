# D5 post-A1 cargo-1 acceptance survey — offline design and staging checklist

Appended 2026-11-01. Offline design only: no code, no staging, no
signing, no claim, no launch, no AdminPort connection, no candidate
created or consumed in this record. Stopped at the next operator
approval gate.

## 1. What this census must prove, and its exact world

The consumed A1 attempt `D5-CORRIDOR-EXTENSION-3`
(`artifacts/experiments/d5-corridor-extension-native-candidate-3/`,
phase-a §17, E44) left an authoritative after-save:

- `after.sav` sha
  `3748e00ce57bcb076466f50cac3776c202b4fd130d6c6071935e9d43e45420bd`
  (bound into `receipt.json`; `session-before.sav` sha
  `59fbb20a…5397c`; diagnostic `ca08e171…dd84b`), replay verdict
  `EXTENSION_COMPLETION_VERIFIED`, one-shot claim consumed, funds at
  A1 close read natively £490,257.

Its receipt carries the statement of record (verbatim): "acceptance
recheck happens in a separate read-only survey session on this
attempt's after-save, before any freight order or vehicle purchase",
with `acceptance_recheck.instrument` pre-pinned in the staged plan
policy to
`app.simulation.openttd.proof.corridor_accept_survey_native`
(`corridor_extension_native.py:754–757`). The census of record that a
post-A1 freight attempt must re-derive natively
(`docs/handoff/2026-10-27/d5-corridor-freight-native-candidate-1-outcome.md`
finding §3): delivery-stop cargo-1 acceptance before any ordering;
the pinned freight admission (`admit_freight_site`, 1/8 minimum)
refuses with typed `INVALID_SITE` before mutation otherwise.

## 2. Instrument of record, and why it must be retargeted (not re-run)

The matching instrument exists: the
`D5-ACCEPT-SURVEY` protocol-6 pipeline
(`app/simulation/openttd/proof/corridor_accept_survey_native.py`,
`AcceptSurveyPlan`, per-exchange
`survey_phase_outcome`, replay `verify_survey_attempt`), consumed once
as `D5-ACCEPT-SURVEY-1`
(`d5-accept-survey-native-candidate-1`, `SURVEY_COMPLETION_VERIFIED`).
Its radius-before-acceptance ordering, control-first observation and
read-only contract are exactly the census semantics required here.

It cannot bind the A1 after-save as-is, by design:

- `survey_prerequisite_binding()` (corridor_accept_survey_native.py:406–451)
  hard-pins `PINNED_PREREQUISITE = d4-corridor-native-candidate-5`,
  refuses any other directory, and requires `attempt == "D4-CORRIDOR-5"`
  plus receipt replay `RECEIPT_VERIFIED`.
- Preflight (725–744) and replay (1187–1215) additionally demand
  `save_sha256 == PINNED_PREREQUISITE_AFTER_SAVE = a81ac836…ef261`.

The A1 candidate satisfies every *generic* binding requirement —
consumed `CLAIM.json` (`prelaunch_digest == seal`), retained
`after.sav`, receipt `after_save_sha256 == 3748e00c…5420bd`, replay
verdict `EXTENSION_COMPLETION_VERIFIED`, welcome-identity fact carried
in its retained `runtime-identity.json` — and fails only the four
*D4-pinned* identity gates. Therefore the design is a **versioned
retarget of the same pipeline**, following the established
`EXTENSION_SCHEDULE_VERSION = 2` precedent
(`corridor_extension_native.py` §14, E41):

- `ACCEPT_SURVEY_SCHEDULE_VERSION: 1 → 2`; consumed candidate-1 stays
  permanent history, byte-untouched, never re-staged or re-signed
  (v1 schedule remains re-derivable, like `extension_schedule_v1()`).
- Attempt name: `D5-ACCEPT-SURVEY-2` (never-consumed fresh identity;
  the consumed `D5-ACCEPT-SURVEY-1` name appears zero times in new
  staged bytes, matching E42's identity rule).
- Prerequisite of record (v2): the consumed A1 attempt —

  | field | value |
  | --- | --- |
  | directory | `artifacts/experiments/d5-corridor-extension-native-candidate-3/` |
  | attempt | `D5-CORRIDOR-EXTENSION-3` |
  | milestone / seal | `D5-CORRIDOR-EXTENSION` / `404d42d9…6acd8` |
  | after_save_sha256 | `3748e00c…5420bd` |
  | replay requirement | `verify_extension_attempt` → `EXTENSION_COMPLETION_VERIFIED` |

  The binding function gains a v2 branch: a generic consumed-prerequisite
  check (same tuple discipline as `terrain_terraform_native.py::prerequisite_source_binding`,
  391–455) plus the A1-specific identity equality above, in place of the
  v1 `attempt == "D4-CORRIDOR-5"` refusal. Preflight and replay enforce
  the identical v2 tuple; `world` = `stage_world` over the A1
  `after.sav` (`PREREQUISITE_ATTEMPT_SOURCE_SAVE_LOAD`,
  `source_save = after.sav`); the world tuple carries
  `qualified_save_sha256` as mechanically derived from the A1
  candidate-3 world (value `null` there, per its retained record).

## 3. Schedule, controls, observations, expected evidence

Eight→four exchange schedule (minimal census; within the historical
32-request budget but planned smaller on purpose):

| id | op | tile | expected | role |
| --- | --- | --- | --- | --- |
| `radius-00` | `radius` | none (tile `null` on the wire; the op reads the global `GSStation.GetCoverageRadius(STATION_TRUCK_STOP)`) | coverage radius natively measured (record `radius: 3`) | radius first, hard-ordered before any acceptance |
| `accept-00` | `accept` | 50351 | cargo-1 acceptance **0** | **negative control of record** (A0 §13.3: 0/8 pre-construction; consumed `D5-FREIGHT-1` freight candidate-1 `site-00`: accept 0 post-refusal, E36) |
| `accept-01` | `accept` | 50862 | cargo-1 acceptance **8/8** under measured radius 3 | the A1 feasibility fact: strong acceptance persists at the live bay-stop tile (A1 station sid 2, `DISTINCT_NEW_STATION`) |
| `prod-00` | `prod` | pickup industry | cargo 1 production 104 (production readback of record) | production continuity across the A1 world |

Controls and halt rules (carried from the
`D5-ACCEPT-SURVEY-1` preparation doc §4):

- Control 50351 must read 0. Any other value is a **positive control
  anomaly → halt for review**, never relabeled, never "compensated".
- `accept-01` below `/8` negative is the critical failure the census
  exists to catch: it re-proves `D5-FREIGHT-1`'s refusal condition at
  the new site; expected 8 (record A0: 8/8 flat/buildable pre-A1; A1
  built the stop natively without merging, `DISTINCT_NEW_STATION`).
- Radius drop below the measured 3 is a finding-of-record change.
- Every deviation from hypothesis is retained as a `FINDING` row
  (measured-vs-hypothesis, never refused into success).
- The acceptance census **proves nothing about vehicle traversal**;
  see §4. It gives the freight flow the pinned perquisite fact only:
  `admit_freight_site` needs the native 1/8 acceptance readback at a
  fresh attempt's own `site-00` in any case.

Expected evidence (per the remediated lifecycle, all force-carrying):

- `PRELAUNCH.json` + `PRELAUNCH.sha256` (`d5-accept-survey-prelaunch-v2`),
  staged `source.sav` re-hashing to `3748e00c…5420bd` byte-for-byte.
- Authorization payload digest recomputed at Gate C (value recorded
  when staged); Option-1 operator signing under the pinned anchor
  `5063982b…4880f`; one-shot `CLAIM.json`; `LAUNCH-CONSUMED.json`
  (`D5_FREIGHT_LAUNCH_CONSUMED_SCHEMA`).
- Live session: welcome identity matched to the A1 world's retained
  identity; `session-before.sav` copy; 4 exchanges each
  `SURVEY_OBSERVED` with per-exchange funds readback = £490,257 and
  `max_cost = 0` on the wire (hard-checked in preflight 687–688 and
  replay 1237–1238); zero `NATIVE_STATE_CHANGED`; script-log health
  gate; `receipt.json` with `before_save_sha256` + census findings;
  certified cleanup all-true; `artifact-manifest.sha256` 0 mismatches.
- Replay: `corridor_accept_survey_native verify` →
  `SURVEY_COMPLETION_VERIFIED` (exit 0); consumed v1 candidate-1
  re-verified untouched by a fresh listing.
- Acceptance criterion (pass): control 0, stop 8, radius 3, prod 104,
  zero mutation, cleanup certified, replay verified. The census alone
  unlocks the *next gate* (freight staging design review); it does not
  itself order or purchase anything.

## 4. Remaining uncertainties this census does not close (fact-of-record)

- **Vehicle reachability of the bay stop**: postmortem §2.4 and
  phase-a §3/§13.3/§14.4 — the GameScript surface exposes no
  road-bits getter; `AreRoadTilesConnected` proves adjacency between
  the road-bit graph (A1 route readback: 30/30 pairs, terminal
  witness pair `50863→50862` fail-closed), but nothing in the census
  or the readbacks proves an engine's YAPF road pathfinder can route
  a truck from pickup 50351 to delivery 50862's single bay-entrance
  bit. Only a live vehicle traversal (freight scope) closes this.
- **Road-bit directions on the escarpment ramp**: proven only through
  the fail-closed witnesses; no surface readback exists.
- The offline road-graph oracle
  (`app/planning/p08_road.py::corridor_reachability`, bounded and
  deterministic) shares the same road-bit graph the engine's
  pathfinder uses (postmortem §2.3) but is still not a live-vehicle
  proof; it may be quoted in freight design as supporting evidence
  only.
- The census observes industry catchment, not truck-stop catchment
  overlap or cargo ordering dynamics; freight delivery proof remains
  a separate gated flow (M8's optimizer round-trip limitation
  unchanged — `optimized_freight_route()` passes exactly one witness,
  no "optimizer-selected" claim may ever be made).

## 5. Implementation plan (offline, no code yet)

Narrowest responsible change, mirroring the A1 precedent — with the
independent-review corrections (§7) folded in:

- `app/simulation/openttd/proof/corridor_accept_survey_native.py`:
  version selector constant here (precedent: `EXTENSION_SCHEDULE_VERSION`
  lives in `corridor_extension_native.py:287`; today
  `SURVEY_SCHEDULE_VERSION = 1` and the attempt name live in
  `corridor_accept_survey_native.py:134`, schedule `survey_schedule()`
  at 162): `SURVEY_SCHEDULE_VERSION = 2`, `survey_schedule_v2()` with
  the §3 table, v2 constants (`SURVEY_ATTEMPT = "D5-ACCEPT-SURVEY-2"`,
  prelaunch schema `d5-accept-survey-prelaunch-v2`), v2
  `survey_prerequisite_binding()` (generic consumed-prerequisite check
  + A1 identity equality, replacing the v1 `attempt ==
  "D4-CORRIDOR-5"` branch under the version selector — the v1 path
  stays byte-for-byte for consumed-candidate-1 replay).
- **The plan contract itself must be versioned** (review M3):
  `AcceptSurveyPlan` hard-binds the v1 world
  (`corridor_accept_survey.py:174–213` — `schema_version: Literal[1]`,
  funds pin 492,149, `SURVEY_OBSERVATION_TILES`, 8-exchange schedule,
  plus an import-time tile/schedule drift assertion at :146–159). v2
  needs a versioned plan literal (schema_version 2, funds pin 490,257,
  v2 tile set {50351 (control), 50862 (stop)}, 4-exchange schedule)
  and a v2 `staged_survey_authorization_payload_digest` composition —
  otherwise v2 has no constructible plan digest and the drift
  assertion refuses at import.
- **The staged GameScript package must be re-baked for v2** (review
  B1): `app/simulation/openttd/d5_freight_package/main.nut` hard-bakes
  `ACCEPT_CANDIDATES = [50607, 50863, 51119, 51375, 50605]` with
  `ACCEPT_CONTROL = 50351` (:191–192) and the 8-row `survey_planned`
  table (:175–184) that the one-shot stage matcher consumes
  (`idx == survey_stage`, :295). 50862 is **not pinned**, so
  `accept-01` would be refused `INVALID_LOCATION` and the 4-exchange
  schedule fails the stage matcher at row 4. v2 GameScript change
  scope: **pin-table data guards and `survey_planned` rows only** —
  no handler-logic change; the v1 package and its staged bytes stay
  untouched (consumed candidates byte-frozen). The new staged
  GameScript digest gets pinned in the staged bytes and re-checked in
  preflight/replay like every closure entry.
- Tests (new/updated, offline only): tests/test_corridor_accept_survey.py
  and tests/test_corridor_accept_survey_native.py — v2 schedule
  derivation and digest, version-scoped identity (consumed
  `D5-ACCEPT-SURVEY-1` name zero times), v2 prerequisite binding
  accept/reject (wrong after-save digest, unconsumed claim, wrong
  replay verdict all refuse), read-only `max_cost = 0` on every
  exchange, control-halt semantics, a preserved replay of consumed
  candidate-1 still returning `SURVEY_COMPLETION_VERIFIED`, **and a
  test binding the staged Nut pin table + `survey_planned` rows to
  the v2 Python schedule** (review B1 follow-up) so the wire and
  GameScript pins cannot drift apart.
- Suites to re-run at baseline (currently 25 + 25 def tests plus the
  A1-based five-suite 240-test run of record):
  `pytest tests/test_corridor_accept_survey.py
  tests/test_corridor_accept_survey_native.py
  tests/test_corridor_terrain_survey.py
  tests/test_corridor_terrain_survey_native.py -q -p no:cacheprovider -rs`.

## 6. Fresh candidate staging checklist (§14.6-style; each item its own record)
1. Implement §5 offline; suites green; consumed precedent candidates
   (accept-survey-1, A1 candidate-3) byte-verified untouched by
   listing/digest after the edit session ends.
2. Independent fresh-context review of the implementation (design doc
   §2–§5 as the spec): identity/pin equality, version isolation,
   prerequisite tuple enforcement in stale/consumed directions.
3. Stage ONE fresh never-consumed candidate, operator-approved:

   production CLI `.venv/bin/python -m
   app.simulation.openttd.proof.corridor_accept_survey_native prepare
   artifacts/experiments/d5-accept-survey-native-candidate-2`
   (`prepare_survey_candidate` v2 branch; `--prerequisite` defaults
   to the pinned A1 directory) → **PRELAUNCH PASS** expected; then
   standalone read-only `preflight` → **PREFLIGHT PASS**; standalone
   `verify` → `AUTHORIZATION_UNVERIFIED`/`CLAIM_ABSENT` (exit 1,
   correct pre-signing state); no `AUTHORIZATION.json`, no
   `CLAIM.json`, no `LAUNCH-CONSUMED.json`, no journal.
4. Record staged facts: seal (`PRELAUNCH.sha256` == recomputed),
   authorization payload digest independently recomputed, schedule
   digest, staged source.sav sha == `3748e00c…5420bd`, frozen closure
   inventory, attempt `D5-ACCEPT-SURVEY-2`.
5. Gate C Option-1 signing: refusal gates first (no
   authorization/claim/launched-consumed/journal files); seed via the
   corrected env-var pipeline only; derived key ≡ pinned anchor; verify
   signature under the anchor before any write; write
   `AUTHORIZATION.json` exactly once; seed cleared; read-only
   `verify_authorization` PASS; `PREFLIGHT PASS`; stop.
6. **Separate explicit launch approval** (not granted by this design):
   one census launch, 4 exchanges, zero mutation expected, then
   replay + certified cleanup, and a fresh finding report (census
   against §3). No freight order, no vehicle purchase, no M8 in the
   same approval.
7. Gates 5 and 6 are separate operator actions exactly as every
   predecessor gate in the phase-a record; each stops and reports
   before the next.

## 7. Independent fresh-context review (appended 2026-11-01)

Verdict: the §1–§4 facts of record verified exactly on disk (seal,
after-save digests, prerequisite hard-pin semantics in staging
preflight **and** replay, census numbers, funds-at-A1-close £490,257,
precedent versioning pattern, plus tests) before the corrections
below; the review was applied in place and the design now carries it:

- **B1 (blocker, applied)**: the existing protocol-6 GameScript
  handler cannot serve the v2 census — `ACCEPT_CANDIDATES` excludes
  50862 (`INVALID_LOCATION` refusal) and the 8-row `survey_planned`
  stage matcher rejects the 4-exchange sequence. §5 now scopes a v2
  GameScript re-bake limited to pin-table data guards + `survey_planned`
  rows, with a pinned digest and a wire↔Nut pin-binding test.
- **M1**: `radius-00` carries tile `null` on the wire
  (`SurveyRequest.coherent` refuses non-null tile on non-accept ops);
  schedule table corrected.
- **M2**: the `site-00` `accept 0` evidence belongs to consumed
  `D5-FREIGHT-1` freight candidate-1 (E36), not an extension attempt;
  citation corrected.
- **M3**: version selector lives in the proof module (per
  `EXTENSION_SCHEDULE_VERSION` precedent); the plan contract itself
  must be versioned (`schema_version` 2, funds pin, tile set, drift
  assertion) or v2 has no constructible plan digest; §5 corrected.
- **M4**: `qualified_save_sha256` noted in the world tuple (value
  `null` in the A1 record); §2 corrected.
- **M5**: `accept-01` attribution softened — 50862 is a live station
  tile (sid 2) post-A1, no longer a bare pre-construction raw-tile
  fact; deviations land in `census_findings`. §3 corrected.

No blockers, no majors outstanding after the corrections. The next
gate after implementation is the §6 item-3 staging approval (separate
operator action).

## 8. Implementation record (appended 2026-11-01, offline)

§6 item 1 (implement offline) and item 2 (independent fresh-context
review) are complete. Nothing was staged, signed, claimed, launched,
connected to an AdminPort, or written under `artifacts/`; the
consumed precedent records (`d5-accept-survey-native-candidate-1`,
`d5-corridor-extension-native-candidate-3`,
`d5-corridor-extension-native-candidate-2`, and the earlier survey
candidate-3 tree) were byte-verified through their own seals and
claim-digest consistency after the edit session and carry zero
changes.

**Code of record.** The version selector and the plan-contract
versioning live in `app/simulation/openttd/corridor_accept_survey.py`
(the wire contract): `SURVEY_SCHEDULE_VERSION = 2`, funds pin
`FUNDS_AT_A1_CLOSE = 490257`, A1 stop tile `SURVEY_A1_STOP_TILE =
50862`, v2 observation tuple `(50351, 50862)`, the four-row
`_SURVEY_SEQUENCE_V2` (radius-00, accept-00, accept-01, prod-00), a
union `SURVEY_PINNED_TILES` for request-tile validation, a v1+v2
drift assertion pair, `AcceptSurveyPlan.schema_version: Literal[1,
2]` with a branched `coherent()` validator (the v1 branch keeps the
historical pins and messages), `survey_plan_v2()`, and a
version-dispatching `staged_survey_plan(policy)`. Note: this places
the version selector in the wire module, superseding review §7 M3's
proof-module wording — the design decision recorded there is
otherwise unchanged (the plan contract itself had to carry the
versioning, which it now does).

`app/simulation/openttd/proof/corridor_accept_survey_native.py`
carries the native versioning on the extension precedent
(`EXTENSION_ATTEMPTS`/`EXTENSION_SCHEDULE_VERSION`): attempt map
`SURVEY_ATTEMPTS = {1: D5-ACCEPT-SURVEY-1, 2: D5-ACCEPT-SURVEY-2}`
(fresh staging carries the current version only), prelaunch schema
map (`…-v1`/`…-v2`), per-version prerequisite pin map with the v2
entry resolving to the consumed A1 record
`d5-corridor-extension-native-candidate-3` at the pinned after-save
digest `3748e00c…5420bd`, version-scoped schedule derivations
(`survey_schedule_v1` reproducing the consumed eight-row record
exactly, `survey_schedule_v2`, and a dispatching
`survey_schedule()`), version-scoped plan policy and budgets
(planned exchanges 8/4, funds 492,149/490,257, `max_cost = 0`
everywhere), `census_hypotheses(version)` with the v2 rows re-bound
fail-closed from the consumed A0 acceptance facts through
`corridor_extension_native.terrain_survey_facts()` (control 50351 =
0, A1 stop 50862 = 8; absent evidence refuses staging rather than
inventing hypotheses), a v2 prerequisite binding that re-verifies the
consumed A1 record end-to-end (seal integrity, consumed one-shot
claim, after-save digest, receipt `after_save_sha256` binding plus
the verbatim `acceptance_recheck` statement, the full
`verify_extension_attempt` replay
`EXTENSION_COMPLETION_VERIFIED`, and the welcome identity), and
version-aware preflight, replay identity, and replay verification.
The replay's schedule binding is now the staged record's own
version: a retained v1 record re-derives the v1 schedule and the v1
plan exactly, a v2 record the v2 census, and any crossed pairing
refuses. `main()`'s `--prerequisite` default resolves to the pinned
A1 directory.

The GameScript re-bake (`d5_freight_package/main.nut`) is strictly
the §3/§5-scoped change: the `survey_planned` table collapses from
eight rows to the four census rows, `ACCEPT_CANDIDATES` becomes
`[50862]` (control `ACCEPT_CONTROL = 50351` unchanged), and the
comment blocks name `D5-ACCEPT-SURVEY-2` and restate that a measured
acceptance value proves catchment only, never traversal. No handler
logic changed.

**Tests.** `tests/test_corridor_accept_survey.py` (30 tests) covers
the v2 contract, the shipped package in the real VM, and a v1
replay-compatibility block. `tests/test_corridor_accept_survey_native.py`
(35 tests) covers v2 staging over the A1 prerequisite, the refusals,
the synthetic consumed-frame replay, and the consumed v1 candidate-1
record's real production replay (`SURVEY_COMPLETION_VERIFIED`).
Evidence runs, all exit 0: the two suites 65 passed; the four-suite
command (these two plus `test_corridor_terrain_survey.py` and
`test_corridor_terrain_survey_native.py`) 148 passed, 1 skipped; the
protocol-5 freight suite 42 passed; the A1 five-suite 240-test
baseline from `REPRODUCE.md` all dots.

**Independent review (§6 item 2), applied.** A fresh-context review
returned READY for the staging gate and confirmed every invariant:
the consumed candidate-1 record replays through the production
verifier without a skip, the recomputed v1 plan digest equals the
consumed record's pinned `plan_model_digest` `2d2e47b2…`, version
pairing refuses on all identity fields, the A1 binding gates were
each read back against disk facts, no code path writes into
`artifacts/`, the copy-based drift tests tamper only tmp copies with
the module pin monkeypatched, the new prose disclaims traversal
evidence everywhere a value is cited, and `git diff main.nut` is
exactly the scoped hunk. Three MINOR findings and one NIT were
applied in place afterwards:

- **MIN 1 (applied as byte-exact restoration)**: three v1-reachable
  refusal strings had drifted in the retarget (the retained
  prerequisite-drift message, the phase funds-drift message, and the
  unknown-prelaunch-schema statement). The v1 branches now emit the
  exact pre-retarget strings again (the funds and prerequisite
  messages are version-aware, naming D4 for v1 and A1 for v2), and
  the renamed v2-facing wording is recorded here so the drift is on
  the ledger, not silent.
- **MIN 2 (applied)**: version-isolation tests were asymmetric —
  only v2-record-cross-v1-identity refusals were exercised. Added
  tests now refuse the A1 directory through the v1 binding
  (`version=1`) and refuse a v1-shaped record (the consumed
  candidate-1 metadata read read-only and tampered in memory)
  carrying the v2 attempt name or v2 schema.
- **MIN 3 (applied)**: the hypothesis-staleness gate in preflight
  and in replay identity was conditional on the staged record
  declaring `RETAINED_CENSUS_REBOUND`; a relabeled state would have
  escaped the retained-bytes comparison. Both sites now compare the
  staged state against the version's own derivation and refuse any
  other state (the consumed v1 record's staged state matches its
  derivation on the evidence checkout, verified by the still-green
  replay).
- **NIT (applied)**: `_survey_exchange_ids` lost its implicit v1
  default argument; every call now names its version's id tuple.

With these applied the suites were re-run green (65 tests, exit 0)
before this addendum. The task stops here as designed: §6 items 3–7
(staging approval, fact recording, Gate C signing, the separate
launch approval, and the census report) each remain their own
operator action, and this session grants none of them.

## 9. Fresh candidate staging record (appended 2026-11-01, offline)

§6 item 3 is complete under one fresh operator approval granted for
this staging step and this step only. One fresh never-consumed
candidate was staged at `artifacts/experiments/d5-accept-survey-…`
`-native-candidate-2/` with the production CLI `prepare` (exit 0,
`PRELAUNCH PASS`), followed by the standalone read-only `preflight`
(exit 0, `PREFLIGHT PASS`) and the standalone `verify` (exit 1,
`AUTHORIZATION_UNVERIFIED` with `CLAIM_ABSENT` — the correct
pre-signing state). Nothing was signed, claimed, launched,
connected to an AdminPort, or executed in OpenTTD; no retry occurred
and no candidate directory was reused.

Fresh-context inspection of the prerequisite returned
`PREREQUISITE VERIFIED`: the A1 record's seal `404d42d9…6acd8`
recomputed equal, its claim consumed with a matching prelaunch
digest, its `after.sav` at `3748e00c…5420bd`, its receipt binding
that save with the verbatim `acceptance_recheck` statement, the
close-out funds 490,257 recorded in its route receipt and result
(the value lives in `receipt.json`/`result.json` under `route.funds`,
not in the A1 `PRELAUNCH.json` — the pipeline pin `FUNDS_AT_A1_CLOSE`
is the constant that binds the receipts), the A0 census facts
`{50351: 0, 50862: 8}` on the consumed A0 survey record, and the
GameScript pin table exactly the four-row census with
`ACCEPT_CONTROL = 50351` / `ACCEPT_CANDIDATES = [50862]`.

Staged facts of record: seal `237a4f84…37daa4` (`PRELAUNCH.sha256`
== recomputed); attempt `D5-ACCEPT-SURVEY-2`, schema
`d5-accept-survey-prelaunch-v2` (the consumed v1 attempt name appears
zero times in every staged text file); v2 plan model digest
`67fce856130310b540dd384d4a903468da02b4afecde9c791eda76513d480be2`
(staged == `survey_plan_v2().digest`); schedule digest
`1222db02bdb96b1724010bf1444b09ef03e788f82e9ce2b7191dbdbae775389d`
(staged == the module's own derivation); budgets 1 launch, 1
connection, 32-request cap, 4 planned exchanges, 512/640 wire bytes,
expected funds 490,257, `max_cost = 0`, zero retries/reconnects;
census hypotheses `RETAINED_CENSUS_REBOUND` rows {50351: 0,
50862: 8} re-bound from the consumed A0 facts; world bound to the
A1 after-save with the staged `source.sav` verified at
`3748e00c…5420bd` and `expected_welcome` equal to the A1 record's
(seed 17, OpenTTD 15.3, 256×256, landscape 0); frozen closure of
3,491 entries pinning the shipped wire module, the native module,
the census GameScript (`0337fb36…97ae`, byte-identical to the shipped
package) and the after-save digest; authorization payload digest
`b1f3e209e71090e970d68a7f419a05e3e66c0963acbb7f956e50b8abe8dc00bd`
independently recomputed. No `AUTHORIZATION.json`, no `CLAIM.json`,
no `LAUNCH-CONSUMED.json`, and no journal exist anywhere in the
candidate tree.

An independent fresh-context review of the staged bytes returned
**READY-FOR-GATE-C** with zero blockers, majors or minors, and two
recorded NITs: `plan_digest_of` hashes the list-of-dict schedule
form (feeding the bare id tuple yields a different, expected hash) —
the staged digest verifies against the correct input shape; and the
staged `game/RoadFreightProof/info.nut` intentionally differs from
the shipped source package's `info.nut` because the staged
composition carries the save's stored GameScript identity through
`staged_composition()`, preflight-verified — not drift. The review
additionally re-ran both production CLIs read-only, re-sampled 14
frozen-closure entries (0 mismatches), and re-snapshotted the
prerequisite and v1 records before and after its checks (identical
digests and mtimes: no evidence mutation).

The task stops at §6 item 5: Gate C Option-1 signing over seal
`237a4f84…37daa4` and payload digest `b1f3e209…00bd`, and then the
separate explicit launch approval, each remain ungranted operator
actions exactly like every predecessor gate.

## 10. Gate C Option-1 signing record (appended 2026-11-01, operator-approved)

Following one explicit operator approval ("Execute Gate C Option-1
Signing — D5 Acceptance Survey Candidate-2", which authorized this exact
signing operation only and explicitly did not authorize candidate
consumption, native execution or OpenTTD launch), the documented
repository-tooling signing checklist
([key provisioning §1/§2/§4](docs/handoff/2026-10-17/operator-key-provisioning.md),
same pipeline as the A1 precedent, phase-a §16) was executed for
`artifacts/experiments/d5-accept-survey-native-candidate-2/` and no
other candidate:

- Every refusal gate was checked first: `AUTHORIZATION.json`,
  `CLAIM.json`, `LAUNCH-CONSUMED.json` and any attempt journal were all
  absent, and no conflicting authorization or consumption state had
  appeared since staging.
- The staged identity was re-validated live against the expected values
  before any signing: seal `237a4f84cb7fc1c880ad23321c3e06663dbdc7d61
  ff82c72687fc962af37daa4` (`PRELAUNCH.sha256` == recomputed sha256 of
  `PRELAUNCH.json`), authorization payload digest
  `b1f3e209e71090e970d68a7f419a05e3e66c0963acbb7f956e50b8abe8dc00bd`
  over the canonical recomputed bytes, plan model digest
  `67fce856130310b540dd384d4a903468da02b4afecde9c791eda76513d480be2`,
  schedule digest
  `1222db02bdb96b1724010bf1444b09ef03e788f82e9ce2b7191dbdbae775389d`,
  A1 after-save binding `3748e00ce57bcb076466f50cac3776c202b4fd130d6c
  6071935e9d43e45420bd`, and A1 prerequisite seal
  `404d42d9fa1e113542e74655858f6bc669407d611057eec0c036612ddfa6acd8`.
  All matched exactly; nothing was repaired, regenerated or restaged.
- The private seed never entered chat, logs or any file: it was
  extracted from the operator-held PEM through the documented pipeline
  directly into the shell environment, and `unset SEED_HEX` ran in the
  same shell immediately after the final use (verified empty).
- The derived public key from the seed was checked equal to the pinned
  production anchor
  `5063982bd28d48573705f334ed4f396618c4930ce21083789dfbbf13a564880f`
  before any signing step.
- Two earlier internal invocations of the signing script were refused
  cleanly before any write and are recorded here for the trail. First,
  during one checklist invocation the shell hit the documented
  `set -o pipefail` lesson (the E43 episode: the checklist must be run
  as `bash -c` with pipefail set in the invocation itself, which is why
  the refusal-gate hygiene check survived a failed inner script); then
  invocation 1 of the Python helper failed with
  `AttributeError: module 'app.simulation.openttd.proof.ed25519_rfc8032' has no attribute 'public_key_hex'`
  (the module exposes `public_from_seed`, not a hex accessor — script
  bug, tooling correct), and invocation 2 failed with
  `REFUSED: signature does not verify under the anchor` because that
  script passed the anchor's hex string instead of `bytes` to the total
  `ed25519_cryptography.verify` primitive, which returns `False` on
  malformed input types rather than raising. Both refusals happened
  before `write_authorization_record`; nothing was written, and the
  seed was cleared after each invocation. A dry diagnostic run (without
  writing) then confirmed the derived key equals the anchor through
  both verifiers, after which the corrected invocation proceeded.
- The corrected invocation executed exactly once: pre-write
  verification of the signature under the anchor succeeded, and
  `write_authorization_record` was called exactly once.
- Resulting record of record: `AUTHORIZATION.json` sha256 and
  `authorization_sha256`
  `d87c2c450e192e4341f8bf4ac6a6ff553194ac0134f8353293bff42250bf4ae3`,
  `operator_key_identity`
  `sha256-ed25519-public-key:cbb63ff58f17f13df3e1be0735fad18497e3a0c6a
  d6b5dd55491d708ae40c614`, binding attempt `D5-ACCEPT-SURVEY-2`,
  milestone `D5-ACCEPT-SURVEY`, and seal `237a4f84…37daa4` in the
  signed payload.
- Post-signing read-only re-checks: standalone `verify` →
  `AUTHORIZATION_UNVERIFIED` / `CLAIM_ABSENT` (exit 1, correct
  authorized-but-never-consumed state); standalone `preflight` →
  `PREFLIGHT PASS` (exit 0). The candidate root now contains exactly
  one new file, `AUTHORIZATION.json`; every other staged byte is
  unchanged. `CLAIM.json`, `LAUNCH-CONSUMED.json` and the attempt
  journal remain absent.
- All consumed precedent records were re-sealed byte-identical after
  signing: survey candidate-1 `38b7667e…b06b` (consumed, replay-compat),
  A1 candidate-3 `404d42d9…6acd8` (consumed), extension candidate-2
  `6d912a3d…c15d` (consumed), A0 survey candidate-3 `6743fc3c…8df8`
  (consumed).
- The authorization signature is NOT launch approval. The next gate is
  a separate explicit operator launch approval for the census lifecycle,
  per the phase-a precedent (§16 then §17 as two distinct approvals).
  This record reached that gate and stopped.
