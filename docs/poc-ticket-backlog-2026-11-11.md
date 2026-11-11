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
