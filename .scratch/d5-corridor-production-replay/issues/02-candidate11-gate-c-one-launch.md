# Production round 02: Gate C + the ONE launch

**What to build:** the Gate C signature over staged candidate-11 (ONE
`AUTHORIZATION.json` write, operator-held PEM, seed memory/env-only)
and then the ONE native launch of the delivered arm under its 1/0/0
budget — under the round grant of ticket 01. **Blocked by:** 01
(`READY-FOR-GATE-C` 40/0). **Blocked-to:** 03 (reconciliation).

**Status:** done 2026-11-06 (signed once, verify PASS; the ONE launch
executed exactly once, rc 0 `NATIVE_CARGOFLOW2_COMPLETE`; the phase
verdict `CARGOFLOW2_LOADED_NEVER_DELIVERED` stands verbatim; one
commit, no repo code change, no push)

- [x] **Gate C mechanics of record held exactly once:** pre-write
      refusal gates all held (root exactly the 4 staged entries with
      no consumption marker; live seal == sidecar ==
      `a6aa529f…4473c564` hard-asserted before any write;
      `public_from_seed(seed)` == the pinned anchor; operator key
      identity unchanged `sha256-ed25519-public-key:cbb63ff5…40c614`;
      the attempted scope binds candidate-11 with plan digest
      `3132bfa0…5e0527`); the authorization payload digest staged ==
      the production re-derivation `945b28d3…b4181d4`; the seed taken
      from the operator-held armored PEM in memory (final-32 RFC 8032
      window), carried env-only `CARGOFLOW_GATE_SEED` (base64), never
      printed, never filed, never passed on any command line; ONE
      sigop, ONE `AUTHORIZATION.json` write; the production
      `verify_authorization` PASS with the record digest bound
      (`c6ff5a9c…40ddf1`); the seed dropped from process memory
      immediately after the write (env unset, references deleted,
      `gc.collect()`); signer script + transcript
      `/tmp/opencode/gate_c_cargoflow2_c11.py` +
      `/tmp/opencode/gate_c_c11_output.txt`
- [x] **Post-sign gates held:** `AUTHORIZATION.json` present (root 5
      entries); the prelaunch byte-equal sweep candidates 3–11 re-run
      (digest lines captured pre-sign in
      `/tmp/opencode/t02_before.txt`, re-hashed post-sign —
      byte-equal, the seal never changed by a signature);
      `CARGOFLOW_GATE_SEED` unset in the interactive env;
      production `preflight` on candidate-11: `PREFLIGHT PASS`; the
      standalone `verify` at that point refused with `CLAIM_ABSENT`
      exit 1 — by design, the consumed-claim state had not been
      created yet
- [x] **Pre-launch gates re-verified fresh:** no `openttd` process;
      live seal == sidecar == `a6aa529f…4473c564`;
      `verify_authorization` PASS (record `c6ff5a9c…40ddf1`, operator
      identity `cbb63ff5…40c614`); budgets launches 1 / retries 0 /
      reconnects 0; the binary digest at the pinned
      `276d5b69…904c`; the round identity unchanged
- [x] **THE ONE launch executed exactly once:** the production run
      driver on candidate-11 exited 0 with
      `NATIVE_CARGOFLOW2_COMPLETE` rc 0, `native_launches` 1,
      `connections` 1, `requests` 26 (the full 26-exchange ladder
      site-00…finish-00 enumerated and accepted),
      `state_changed` true, `preflight` on launch `PASS`, `halt`
      null, `last_status` `PHASE_STOPPED`; full run JSON transcript
      `/tmp/opencode/t03_c11_run.txt`; rc verbatim — a 0 is a 0
- [x] **The launched phase outcome of record (from the run's own
      JSON, figures verbatim):** phase seal `a6aa529f…4473c564` and
      plan-model digest `313879bd…16fda`; the anchor day 712232
      tick 291 (`arrival_pickup`, cargo 0); loads
      5 @flow-08 day 712271 tick 3173,
      10 @flow-08 day 712271 tick 3193,
      15 @flow-08 day 712271 tick 3213, and a NEW 20-load
      @flow-09 day 712272 tick 3233 (four loads this round;
      candidate-9 had three departure-invisible loads at flow-08);
      the departure 20 @flow-09 day 712274 tick 3397; the bay
      arrivals 0 @flow-04 day 712251 tick 1676 and 20 @flow-12
      day 712291 tick 4648; the finance observation day 712292
      delivered 0 income 0 last_accepted 0 funds 484764 tick 4711;
      `unloadings` EMPTY (`[]` — verbatim in the transcript); the
      finish-00 vehicle block RUNNING (in_depot false, load 20,
      location 50862, speed 36) at the final sampled point; the
      sampled months 1950-01/02/03 with the pickup production
      prod_pickup 104/trans_pickup 67 and `wait_pickup` rising
      0→126 across the sampled offsets; the offset ladder rows
      0..55 (12 flow rows over 13 sampled points to offset 60, item
      60 carrying the tail observations); the series funds sampling
      walks 485217 → 484765; **verification
      `CARGOFLOW2_COMPLETE` and the phase verdict
      `CARGOFLOW2_LOADED_NEVER_DELIVERED` with the statement "a load
      was latched, but no unloaded amount reached the bay acceptance
      chain inside the ladder"** — the delivered-miss reproduces on
      the fresh staging (twice-reproduced now: candidate-9, then
      candidate-11 under its fresh identity and its own seal); E36
      stays open (same delivered arm, not a genuinely competing
      route), E114 stays UNKNOWN per its own rule
- [x] **Post-run state checks held:** `CLAIM.json` consumed
      (launches_allowed 1, retries 0); `LAUNCH-CONSUMED.json` at
      schema `d5-native-launch-consumed` binding the prelaunch seal
      `a6aa529f…`, the authorization record `c6ff5a9c…`, and the
      operator key identity `cbb63ff5…40c614`;
      `artifact-manifest.sha256` sha-verified 68/68 on its own
      directory (`sha256sum -c` — 68 rows `OK`, zero mismatches; one
      transcript note: the first in-chat manifest probe by the
      operator's agent mis-parsed the 2-column manifest rows
      (expected field grabbed the filename) and printed 68 bogus
      mismatches, corrected end-to-end in the same session with the
      standard verifier; retained bytes never touched); `cleanup.json`
      all-true (`credential_removed`, `graceful_attempted`, `reaped`,
      `sockets_closed`, `workspace_disposed` true; the endpoint
      verification closed the listener, reaped the process, released
      the reservation; the kernel socket states show only the closed
      TIME_WAIT pair); no `openttd` process; the seal byte-equal
      post-run accepted (`a6aa529f…4473c564` re-hashed live); the
      prelaunch byte-equal sweep 3–11 byte-equal post-run; the
      `CONTEXT.md` authority pin intact `847d710a…`
- [x] Books: this ticket, backlog row, E137 row, AI_HANDOFF tail
      cell; one commit; no push; no repo source change this ticket
