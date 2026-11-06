# 04r7: Round-7 ONE launch

**What to build:** the single native launch of the Gate-C-signed round-7
candidate-7 via the production pipeline CLI — ONE attempt, first
invocation, no retry, no reconnect — the round's outcome recorded
verbatim (rc, status, phase verification, verdict), the single-use
claim consumed and bound to the round's seal + authorization record +
operator identity, the retained evidence replay-verified read-only after
the run, and the post-consume state certified (cleanup, manifest,
seal integrity, no process, no second launch).

**Blocked by:** 03r7 (Round-7 Gate C signature) — the native-run
approval is the in-session gate that authorizes it (granted in-session
2026-11-06 via the explicit gate option "Grant the ONE launch", the
round-6 launch precedent; one attempt, no retry, no reconnect).

**Status:** done 2026-11-06 (native-run approval in-session; ONE
invocation, rc 0; the outcome recorded verbatim, never stretched)

- [x] THE ONE native run executed exactly once: `run
      artifacts/experiments/d5-corridor-cargoflow2-native-candidate-7`
      via the production CLI — **rc 0
      `NATIVE_CARGOFLOW2_COMPLETE`** (`verified: true,
      cleanup_complete: true, state_changed: true, halt: null`,
      1 native launch / 1 connection / 25 requests, command accepted,
      last status `PHASE_STOPPED`); binary resolved from the harness
      filesystem pin (no env export, sha re-verified at run start with
      the no-processes pre-check); no retry, no reconnect
- [x] The 25-exchange ladder ran true end-to-end: site-00 READY 489650
      → engine-00 READY → purchase-00 BUILT 485221 (quote 4429 exact) →
      vread-00/01 READ → order-00/order-01 ORDERED → order-read-00
      ORDER_SET_VERIFIED → monitor-00 ARMED → start-00 STARTED →
      **arrive-00 ANCHORED** (712232, 289) 485217 → flow-00..flow-11
      READY with the native funds series
      [485217, 485212, 485206, 485201, 485195, 484997, 484991, 484985,
      484980, 484974, 484776, 484770] → finance-00 FINANCE_VERIFIED
      484769 income 0 delivered 0 → finish-00 PHASE_STOPPED; no halt
      class fired anywhere in the ladder
- [x] The delivery verdict of record, recorded verbatim:
      `CARGOFLOW2_LOADED_NEVER_DELIVERED` ("a load was latched, but no
      unloaded amount reached the bay acceptance chain inside the
      ladder") — the round-6 terminal COMPLETE-not-delivered class,
      now carried by the adjudicated v2 arm: empty bay arrival 712250
      (flow-04, vehicle location 50862), pickup arrival 712270
      (flow-08), loads 5/10/15 latched at 712271 (flow-08), loaded
      departure 20 t at 712274 (flow-09, tick 3395), the delivery leg
      in transit at finish (location 50095, RUNNING, speed 36-38,
      load 20) with `unloadings: []`
- [x] The two admitted routes' native divergence observed and recorded:
      the round-7 empty bay arrival on the v2 arm is one day earlier
      than round-6's on the delivered v1 arm of record (712250 vs the
      round-6 record's 712251, same endpoints) — direct native
      behavioral divergence of the two routes' geometry; the round-7
      funds series differs from round-6's by exactly one unit at
      offset 35 (484985 vs the round-6 record's 484986) — never
      reconciled by hand, never fudged
- [x] The corner edge 50351↔50352 (the typed open precondition riding
      the v2 route): the observation ladder of record pins positions at
      the 25 exchange instants — the vehicle drove the staged v2 order
      path across its full outbound + return span with observed
      positions 45748, 45744, 47791, 49839, 50862 (bay), 50095, 48047,
      45743 (depot), 45748, 45743, 47791, 50095 — and NO halt fired
      anywhere on the path; the corner tiles themselves were not a
      pinned observation instant, so the strict direct corner-tile
      observation stays open while the v2 arm's native end-to-end
      driveability (un-halted, protocol-complete, sealed) is now native
      evidence of record
- [x] The single-use claim consumed exactly once: `CLAIM.json`
      bound `prelaunch_digest 9c5f7272…e19257` /
      `authorization_sha256 24ccab3e…6417` / operator identity
      `sha256-ed25519-public-key:cbb63ff5…40c614`
      (`consumed: true, launches_allowed: 1, retries: 0`);
      `LAUNCH-CONSUMED.json` present binding the same record
- [x] Post-run read-only replay: production `verify` re-run
      **`CARGOFLOW2_COMPLETION_VERIFIED` exit 0** (`before_save_sha256
      d16ceeec…f5e71`, phase seal == the round's seal
      `9c5f7272…e19257`, plan digest `e1cafb23…c08b0`, sampled months
      [1950-01, 1950-02, 1950-03], the funds-model walk and its
      income-delta table reconciled inside the verified outcome)
- [x] Post-consume state certified: root exactly 68 entries; the run
      artifact manifest re-hashed **66/66 OK** (0 missing, 0
      mismatched); certified cleanup all-true (pid 14346 quit_requested
      → reaped rc 0, game port 56209 / admin port 58985 listener and
      connection closed, `remaining_processes: []`, workspace disposed,
      credentials removed — verified at the OS level: no openttd
      process remains); candidates 1–7 PRELAUNCH seals == sidecars
      (candidate-7's seal byte-equal after the run); no second launch,
      no relabel, historical zones byte-untouched; `git diff --check`
      clean; `CONTEXT.md` pin intact
- [x] Transcripts of record (outside the repo tree):
      `/tmp/opencode/c7_launch_output.txt`,
      `/tmp/opencode/c7_launch_verify_output.txt`
- [x] Launch row appended to the PoC backlog status log (verbatim
      figures, the one-invocation discipline, the class-of-record
      statement); ticket + row booked in one commit per the grant
