# Full-Scope Functional PoC — ticket backlog (2026-11-11)

Round record for the Phase B opener (feature dir
`.scratch/phase-b-t030/`). Objective of the round: reach Ticket T-030
(Fleet & Capacity, Phase B) by mapping every dependency, executing the
unblocked offline work, and preparing the native attempt up to its
fresh-explicit-authorization gate — zero launches, zero AdminPort, no
retained evidence byte touched. Native-run grants remain per-attempt
decisions of the operator; all prior grants are void for reuse.

## Status log (2026-11-11)

- Dependency map of record closed (spec
  `docs/specs/t030-fleet-capacity-exercise.md`): Phase A closed
  (T-022, E127); F06/F11 prerequisites DONE (E2 — canonical
  constructed-fleet creation + fresh-process reload-only
  correspondence; both q3 run dirs' manifests re-verified 0
  mismatches, protected save
  `51e45689ae40dfa53c2cc150a05076fcb6e5cc2f38ec4eff56908372ab1297eb`
  unchanged); exercise machinery offline DONE at HEAD (dispatch wire,
  collectors, byte-pinned staged bridge carrying the full handler
  vocabulary, q3-era VM validation record still matching
  `package_bytes()` composition byte-for-byte); runnable exercise
  stage of record — the one MISSING piece — built this round; gate
  ladder prepared; post-run receipts + E-row wait on authorization.
- **Ticket 01 (exercise conductor) resolved** — commit `c6ec803`:
  `app/simulation/openttd/proof/canonical_fleet_exercise.py` additive
  to the frozen `proof/canonical_fleet.py` (identity
  `canonical-fleet-exercise-t030-1`, own
  `canonical-fleet-exercise-prelaunch-v1` contract, prepare staged
  from the E2 created evidence under the q3 byte-pin
  (`artifacts/validation/canonical-fleet-reload-q3/suspension.json`),
  fail-closed preflight, `conduct_exercise` proving reload
  correspondence first then ONE `dispatch_loaded_arm(arm="B")`
  purchase→dispatch→unpause with the three receipt digests bound in
  `exercise-correspondence.json`, typed
  `CANONICAL_FLEET_EXERCISE_VERIFIED`; `run` authorize gate, CLAIM
  launches_allowed=1 retries=0, welcome identity ("15.3", 42, 64, 64),
  q3-shell owned cleanup). 12 offline tests
  (`tests/test_canonical_fleet_exercise.py`); lane suites 126 passed /
  0 failed across the nine lane files (the q3 no-purchase tripwire
  `test_canonical_reload_only.py` stays green — the frozen lane stays
  unreachable from the exercise module); statics clean (ruff, format,
  py_compile, scoped `uvx ty`, `git diff --check`). Reconciliation:
  the real `verify_reloaded` signature takes the source save sha256
  internally from `created`; the frozen `canonical_fleet.py` call
  site already matches — no latent inconsistency; nothing in the
  frozen lane was touched.
- **Ticket 02 (attempt package) claimed, at the gate** —
  `.scratch/phase-b-t030/issues/02-attempt-package.md`: staging →
  preflight → ONE run under `--authorize-one-launch` → independent
  verify, with preconditions (clean tree at `c6ec803`, binary pin
  `276d5b698a…`/OpenGFX pin `43a0c1da…`, `pgrep -x openttd` empty, E2
  manifest re-verified), the grant text (one execution, no
  retry/relaunch/reconnect, no seed or scope change, stop on
  unexpected failure, receipts retained whatever the outcome), the
  expected receipts, and the fail-closed rules (partial mutation
  records its physical vehicle id and is never retried or accepted;
  failure stops before further boundaries; cleanup still runs;
  nothing relabeled).
- **Not claimed:** the native T-030 exercise attempt itself — it
  needs a fresh explicit operator authorization after independent
  review and Gate C signing; no feasibility/economics claim outside
  the receipts (OPEX/ROI stay UNKNOWN; T-031's matched A/B is a
  separate later effort). FD-C-2's Attempt-7 package (E160) remains
  prepared, not executed, under the same void-grant rule.
- Offline verification of record: `sha256sum -c` inside both q3 run
  dirs 0 mismatches; lane suites green; `package_bytes()` ↔
  suspension.json byte-pin verified live at HEAD.

Ledger pairing: this file + `.scratch/phase-b-t030/issues/` +
EVIDENCE_INDEX E161 + AI_HANDOFF/TASKS addenda of the same date. One
commit pair (code+tests `c6ec803`, docs this commit); never pushed.

## T-031 matched A/B — conductor resolved, arm packages at the gate (2026-11-11)

- **Ticket 01 (arms conductor) resolved, commit `a9291c2`** —
  `.scratch/phase-b-t031/issues/01-arms-conductor.md`: stage core
  generalized default-behavior preserving in
  `canonical_fleet_exercise.py`; new
  `canonical_fleet_matched.py` (identities
  `canonical-fleet-matched-a/b-t031-1`, matched contracts, same-E2
  same-byte bridge staging, telemetry v2 vehicle_count 3/4
  max_tick_gap=100, five-anniversary horizon via the retained
  `monitor_network`, receipts with honest provenance, typed
  `CANONICAL_FLEET_MATCHED_VERIFIED`, descriptive-only `compare_arms`,
  CLI). 11 matched + 14 exercise offline tests; lane suites green;
  statics clean.
- **Latent blocker found and fixed the same commit:** the q3-era
  suspension.json helper pins bind the RETAINED q3 frozen-source bytes
  (`canonical_protocol_vm.nut` drifted post-q3 via E92 readback
  fidelity) — the old check would have refused every fresh T-030/T-031
  prepare at grant time; the record's package byte-pin holds.
  `require_retained_vm_helpers` verifies record helper digests against
  the retained q3 `frozen-source.zip` (fail-closed); live helpers
  sealed per-stage; frozen driver's identical check byte-untouched
  (consumed q3 identities never re-prepared).
- **Tickets 02/03 (arm A / arm B attempt packages) claimed, at the
  gate** — `.scratch/phase-b-t031/issues/02-arm-a-attempt-package.md`
  and `03-arm-b-attempt-package.md`: staging → preflight → verify
  (AUTHORIZATION_UNVERIFIED) → ONE run under `--authorize-one-launch`
  each; separate fresh authorizations (arm A first, arm B after arm A's
  attempt completes; never shared with the T-030 exercise or any
  earlier attempt); expected receipts per arm + fail-closed rules +
  post-arms offline `compare` command.
- **Not claimed:** the two native T-031 arm attempts — each needs its
  OWN fresh explicit operator authorization after independent review
  and Gate C signing; all prior grants void; comparison record + E-row
  only after both arms' receipts; OPEX/ROI stay UNKNOWN outside
  receipts. The T-030 package (ticket-02, E161) and FD-C-2 Attempt-7
  package (E160) remain prepared, not executed, under the same
  void-grant rule.

Ledger pairing: this file + `.scratch/phase-b-t031/issues/` +
EVIDENCE_INDEX E162 + AI_HANDOFF/TASKS addenda of the same date. One
commit pair (code+tests `a9291c2`, docs this commit); never pushed.

## T-032 five-year continuous — conductor resolved, package at the gate (2026-11-11)

- **Ticket 01 (continuous attempt package) claimed, at the gate** —
  spec `docs/specs/t032-five-year-continuous.md`, package
  `.scratch/phase-b-t032/issues/01-continuous-attempt-package.md`;
  conductor resolved by commit `b63eb16` (identity
  `canonical-fleet-continuous-t032-1`, own finalization contract, adds
  nothing, five native economy anniversaries, telemetry v2 3 vehicles,
  retained monitor loop, `continuous-finalization.json` provenance
  labels, typed `CANONICAL_FIVE_YEAR_CONTINUOUS_VERIFIED`); 7 offline
  tests + all sibling suites green; statics clean.
- **Not claimed:** the native T-032 five-year attempt — needs a FRESH
  explicit operator authorization after independent review and Gate C
  signing; all prior grants void; per-year OPEX/ROI DERIVED record +
  E-row only after the attempt's receipts.

Ledger pairing: this file + `.scratch/phase-b-t032/issues/` +
EVIDENCE_INDEX E163 + AI_HANDOFF/TASKS addenda of the same date. One
commit pair (code+tests `b63eb16`, docs this commit); never pushed.

## T-033 consolidated OPEX/ROI — record built and generated (2026-11-11)

- **Ticket 01 resolved** — spec `docs/specs/t033-consolidated-opex-roi.md`,
  module `app/experiments/phase_b_consolidation.py`, generated record
  `artifacts/experiments/phase-b-consolidation-2026-11-11/` (all four
  native sources `UNKNOWN_PENDING_NATIVE_AUTHORIZATION`; E2 funding
  context OBSERVED 400,000 GBP; consolidated CAPEX UNKNOWN). 6 offline
  tests; statics clean.
- **Not claimed:** per-source OPEX/ROI stay UNKNOWN until the native
  attempts run under their own fresh grants (T-030 ×1, T-031 ×2, T-032
  ×1); the record re-derives offline after each attempt — no relabel,
  no manufacture.

Ledger pairing: this file + `.scratch/phase-b-t033/issues/` +
EVIDENCE_INDEX E164 + AI_HANDOFF/TASKS addenda of the same date. One
commit pair; never pushed.

## T-034 standing full 15.3 regression — run and recorded (2026-11-11)

- **Ticket 01 resolved** — spec `docs/specs/t034-standing-regression.md`:
  6342 collected / 6286 passed / 56 failed / 0 errors / 50 skipped
  (junitxml-counted, stable across two runs); legacy-red classified by
  ID, all pre-existing (E159/E155/E153 records + two IDs verified
  pre-existing at pre-round HEAD `f0b5960` this round); zero failures
  in any round-touched file; 197 retained manifests 0 mismatches;
  binary/OpenGFX/protected-save pins hold; no native process.
- **Not claimed:** Phase B native closure — blocked ONLY on four
  separate fresh explicit operator grants (T-030 ×1, T-031 arm A ×1,
  T-031 arm B ×1, T-032 ×1); packages prepared at the gates; all prior
  grants void; T-033's consolidated record re-derives offline after
  each attempt.

Ledger pairing: this file + `.scratch/phase-b-t034/issues/` +
EVIDENCE_INDEX E165 + AI_HANDOFF/TASKS addenda of the same date. One
commit; never pushed.

## T-035 GUI native probe — built offline, package at the gate (2026-11-11)

- **Operator ask:** a real, visible, usable OpenTTD 15.3 desktop window;
  no headless-only execution, no virtual display, no background-only
  process.
- **Design of record:** `-D` is windowless dedicated and no CLI flag
  hosts a visible server, so the probe = the proven dedicated host
  (byte-unchanged) + a SECOND real GUI client joining as spectator
  (`-n 127.0.0.1:<game-port>#255`, demo-lane argv byte-for-byte,
  `client_name = "Canonical GUI Probe"`). Join verified SERVER-side
  (`*** Canonical GUI Probe has joined the game` in the host's stdout;
  client.log stays empty in GUI mode; AdminPort allowlist NOT widened).
- **Guarantees preserved:** one-shot authorization (own identity
  `canonical-fleet-gui-probe-t035-1`, own CLAIM, own fresh grant),
  fail-closed desktop requirement at prepare AND preflight, reload-only
  paused correspondence via the new `dispatch=False` seam (T-030 default
  unchanged), 60 s join deadline, 600 s observation with typed ends
  (`OPERATOR_CLOSED_WINDOW` / `OBSERVATION_WINDOW_ELAPSED`), client
  terminated before the standard cleanup seal, full evidence capture +
  manifest verify. Honesty boundary: machine-verified facts only — the
  agent never claims it saw the window.
- **Tests/statics:** `tests/test_canonical_fleet_gui.py` 12 passed;
  exercise 14 + matched 11 + continuous 7 green; lane suites green incl.
  the q3 tripwire; ruff/format/py_compile/ty/`git diff --check` clean.
- **Independence verdict:** satisfies NONE of T-030/T-031/T-032's
  done-ness criteria; must not be assumed to replace any native attempt
  nor be smuggled into their sealed packages. Adding a roadmap §3 row is
  an operator decision.
- **Spec:** `docs/specs/t035-gui-native-probe.md`. Package:
  `.scratch/phase-b-t035-gui-probe/issues/01-gui-probe-attempt-package.md`
  (staging → preflight → ONE run under `--authorize-one-launch`, from a
  desktop terminal).

Ledger pairing: this file + `.scratch/phase-b-t035-gui-probe/issues/` +
EVIDENCE_INDEX E166 + AI_HANDOFF/TASKS addenda of the same date. One
docs commit; never pushed.

## T-035 gate round — preflight refusal, fix + re-stage (2026-11-11)

- **Gate walk:** prepare staged offline OK at
  `canonical-fleet-gui-probe-t035-1`; preflight REFUSED typed
  (`canonical save must be an existing protected regular file`).
  Stopped at the gate per the operator's standing instruction.
- **Root cause:** the shared exercise-core `prepare` never staged
  `source.sav` (driver prepare `canonical_fleet.py:158` does); every
  exercise-core package (T-030/T-031×2/T-032) would have refused
  identically at grant-time preflight — none had staged yet, so the
  fix lands before their attempt day.
- **Fix + re-stage (operator's in-session "Fix + re-stage" answer; fix
  commit `132e2ea`):** one-line copy in `exercise.prepare`; identity
  advanced `…t035-1` → `…t035-2` (stale-supersession, E130); refused
  staging preserved untouched; unpatched real-staging preflight test
  added (the gap: earlier tests patched both verify functions). 45
  family tests green; lane suites rc=0; statics clean. t035-2
  re-staged: prepare → **preflight PASS** → verify
  `AUTHORIZATION_UNVERIFIED`; staged `source.sav` == protected pin.
- **Spec + package** updated to t035-2 with the supersession record.
- **Blocked:** the native GUI attempt needs the operator's FRESH
  explicit one-launch grant (zero launches / zero AdminPort / zero
  grants this round).

Ledger pairing: this file + `.scratch/phase-b-t035-gui-probe/issues/` +
EVIDENCE_INDEX E167 + AI_HANDOFF/TASKS addenda of the same date. One
docs commit; never pushed.

## T-035 attempt executed once — typed FAILED at the admin-connect seam (2026-11-11)

- **The grant:** the operator's explicit in-session one-launch grant
  after the E167 gate round. The attempt ran exactly once; no retry.
- **Outcome of record:** `result.json` `{status: FAILED, launches: 1,
  connections: 0, error: "AuthDisconnected: Admin connection failed"}`.
  Bridge started, `FREIGHT_DELIVERY_READY` logged, source save loaded
  clean, game listener bound — no admin listener on `49895`. The
  conductor's `connect_secure` refused → typed failure BEFORE all
  correspondence and the client stage: **no window ever appeared**
  (GUI outcome not reached — not a GUI defect). Failure path as
  designed: `failure.sav`, owned cleanup (pid 22971 reaped rc 0,
  all-true), manifest 0 mismatches, `verify` →
  `ATTEMPT_NOT_VERIFIED: FAILED`, dir sealed read-only at
  `artifacts/runtime/canonical-fleet-gui-probe-t035-2/`.
- **Root cause (read-only):** `stage_workspace` never calls
  `RuntimeWorkspace.write_config(AdminSettings(...))` — the admin auth
  trio (`private.cfg` `[admin_authorized_keys]` + `secrets.cfg`
  `admin_password`) every working stage writes is missing; with
  `allow_insecure_admin_login = false` OpenTTD 15.3 never starts the
  admin network. Second latent exercise-core blocker of the E167
  class, unreachable offline.
- **State of record:** the t035-2 identity is consumed terminal
  history; the grant is consumed and void. The fix (mirror
  `write_config` into `stage_workspace` + auth-trio regression test)
  and any re-attempt (`canonical-fleet-gui-probe-t035-3`) need the
  operator's separate authorizations.

Ledger pairing: this file + `.scratch/phase-b-t035-gui-probe/issues/` +
EVIDENCE_INDEX E168 + AI_HANDOFF/TASKS addenda of the same date. One
docs commit; never pushed.

## T-035 fix round — admin auth trio staged, t035-3 at the fresh-grant gate (2026-11-11)

- **Fix (commit `0a95c75`, operator's in-session "Fix + re-stage"
  answer):** `stage_workspace` mirrors the driver's `write_config` —
  stages `private.cfg` (`[admin_authorized_keys] <public_hex>`) +
  `secrets.cfg` (`admin_password`) beside the canonical-derived
  `openttd.cfg`, the exact shape every working stage carries. Closes
  the E168 refusal class at the staging seam.
- **Identity:** advanced `canonical-fleet-gui-probe-t035-2` →
  `canonical-fleet-gui-probe-t035-3` (stale-supersession); the sealed
  t035-2 attempt and its consumed/void grant untouched.
- **Tests/statics:** gui 14 + exercise 14 + matched 11 + continuous 7
  = 46 green; reload-only + reload-context rc=0; ruff/format/
  py_compile/ty/`git diff --check` clean.
- **Re-stage:** `artifacts/runtime/canonical-fleet-gui-probe-t035-3/` —
  prepare → **preflight PASS** → verify `AUTHORIZATION_UNVERIFIED`;
  staged `source.sav` == protected pin; auth trio present. Spec +
  package updated to t035-3.
- **Blocked:** the t035-3 re-RUN needs the operator's FRESH explicit
  one-launch grant (zero launches / zero AdminPort / zero grants this
  round).

Ledger pairing: this file + `.scratch/phase-b-t035-gui-probe/issues/` +
EVIDENCE_INDEX E169 + AI_HANDOFF/TASKS addenda of the same date. One
docs commit; never pushed.

## T-035 attempt executed once under a fresh explicit grant — VERIFIED (2026-11-11)

- **The grant:** the operator's fresh explicit one-launch grant after
  E169. The t035-3 attempt ran exactly once; no retry/reconnect.
- **Outcome of record:** `result.json`
  `{status: CANONICAL_FLEET_GUI_PROBE_VERIFIED, launches: 1,
  connections: 1, gui_client: OBSERVATION_WINDOW_ELAPSED}` rc 0. A
  real GUI client joined the live dedicated host as a spectator
  (`-n 127.0.0.1:49457#255`, `client_name "Canonical GUI Probe"`) on
  the real desktop (`DISPLAY=:0`/`WAYLAND_DISPLAY=wayland-1`/
  `XDG_SESSION_TYPE=wayland`); join verified SERVER-side (marker line
  8 `*** Canonical GUI Probe has joined the game (Client #2)`); alive
  the full 600 s observation window; ended by the probe's owned
  terminate (`code: -9, owned_terminate: true`); the server then saw
  `…has left the game (connection lost)` and saved
  `reload-readback.sav`. Honest boundary: machine-verified facts
  only; the agent does not claim to have seen the window.
- **Seal:** cleanup certified all-true (pid 28460 quit → reaped
  rc 0); manifest 0 mismatches; post-run `verify` →
  `CANONICAL_FLEET_GUI_PROBE_VERIFIED` rc 0; `pgrep -x openttd`
  empty; dir sealed read-only at
  `artifacts/runtime/canonical-fleet-gui-probe-t035-3/`.
- **Grants + identity:** t035-2 and t035-3 grants consumed and void;
  genealogy t035-1 (refused, preserved) → t035-2 (FAILED, sealed) →
  t035-3 (VERIFIED, terminal); any further T-035 run needs a NEW
  identity + FRESH grant.
- **Not claimed:** independence verdict stands (satisfies none of
  the Phase B done-ness criteria); roadmap §3 T-035 row = operator
  decision; Phase B native closure outstanding — T-030 ×1, T-031 arm
  A ×1 + arm B ×1, T-032 ×1, each its own fresh grant, each
  inheriting both exercise-core fixes (E167 + E169).

Ledger pairing: this file + `.scratch/phase-b-t035-gui-probe/issues/` +
EVIDENCE_INDEX E170 + AI_HANDOFF/TASKS addenda of the same date. One
docs commit; never pushed.

## 2026-11-11 — T-036 fresh-world GUI probe family (T-035 follow-up, E171): BUILT OFFLINE, creation stage at the fresh-grant gate

- **Ask of record:** a genuinely fresh OpenTTD 15.3 world visible through
  the real GUI — a newly generated world visibly running in the actual
  OpenTTD GUI, not the existing Sunningbury demo; sealed T-035 evidence
  untouched; no launch, no authorization consumed this round.
- **Family of record:** two separately authorized attempts, strictly
  sequential (`app/simulation/openttd/proof/fresh_world_gui.py`, commit
  `68dbd36`): `fresh-world-create-t036-1` → `FRESH_WORLD_CREATE_VERIFIED`
  (world generated inside the one launch: `-g heightmap.png -G 1181` +
  proven `[game_creation]` config, native marker `Map generated,
  starting game`; console save `fresh-world.sav` digest-pinned in
  `world.json`; no admin connection, no bridge, no canonical input) →
  `fresh-world-gui-probe-t036-1` → `FRESH_WORLD_GUI_PROBE_VERIFIED`
  (bridge host loads the fresh save `-g source.sav`, welcome frame must
  report `15.3`/seed `1181`/64×64 — demo seed 42 refuses typed — and the
  real desktop GUI client `Fresh World GUI Probe` joins as spectator,
  server-side verified, T-035 join machinery unchanged).
- **World constants of record** (module constants, NOT CLI flags — a
  change is a new staging identity): seed 1181 (≠ demo 42), 64×64
  (`map_x = map_y = 6`), temperate, 1950, flat 64×64 heightmap;
  `pause_on_newgame = false`; creation config without `[game_scripts]`,
  GUI config with `RoadFreightProof`.
- **Anti-fallback tripwires:** neither stage accepts canonical keys; the
  GUI stage's only permitted source is `verify_fresh_creation(...)` — an
  immutable sealed `FRESH_WORLD_CREATE_VERIFIED` attempt with the save
  digest still matching its pin — any other directory refuses typed
  `fresh-world creation evidence required (never the canonical demo
  world)`; staged save digest re-verified at preflight; runtime welcome
  seam refuses seed 42. Offline regression `tests/test_fresh_world_gui.py`
  (15 tests, zero native processes) pins argv shapes both ways.
- **State:** creation attempt staged offline at
  `artifacts/runtime/fresh-world-create-t036-1/` — prepare → preflight
  PASS → `AUTHORIZATION_UNVERIFIED` rc 1. **Creation RUN awaits a FRESH
  explicit one-launch grant (grant A); the GUI run needs its OWN fresh
  grant (grant B) after stage 1 verifies.** Grant texts + commands of
  record: `.scratch/phase-b-t036-fresh-world-gui/issues/01-fresh-world-gui-attempt-package.md`,
  `docs/specs/t036-fresh-world-gui-probe.md`.
- **Not claimed:** no native run; the fresh world has not been seen in
  the GUI yet; satisfies none of the Phase B done-ness criteria; Phase B
  native closure outstanding — T-030 ×1, T-031 arm A ×1 + arm B ×1,
  T-032 ×1, each its own fresh grant, each inheriting both exercise-core
  fixes (E167 + E169). T-035 stays terminal VERIFIED at E170.

Ledger pairing: this file + `.scratch/phase-b-t036-fresh-world-gui/issues/`
+ EVIDENCE_INDEX E171 + AI_HANDOFF/TASKS addenda of the same date. One
docs commit; never pushed.
