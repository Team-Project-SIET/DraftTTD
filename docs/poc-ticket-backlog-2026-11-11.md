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
