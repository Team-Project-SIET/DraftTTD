# 04r6: Round-6: the one launch

**What to build:** the single native launch of the signed round-6 candidate —
exactly one run at the recorded invocation shape, then the read-only replay
of record (once), the integrity sweep (manifest, seals, historical zones,
pins), and the certified cleanup (reaped process, closed sockets, disposed
workspace, removed credential, released reservations). The attempt's outcome
is terminal either way: completion evidence of record if the ladder
completes, or a preserved halt of record — never a retry, a reconnect, a
relabel or a relaunch.

**Blocked by:** 03r6 (Round-6 Gate C signature) — the operator launch
approval is the separate in-session gate that authorizes it.

**Status:** done 2026-11-05 (operator approval in-session; ONE native
launch, first attempt, rc 0 `NATIVE_CARGOFLOW2_COMPLETE`; no retries,
no reconnects)

- [x] Pre-launch gates re-verified fresh (read-only): gate surface = 5
      entries (4 staged files + `AUTHORIZATION.json` + `isolated/`), no
      CLAIM / LAUNCH-CONSUMED / launch receipts; seal == sidecar ==
      approved seal `e929d7b2e749f2a14af9bb19fdf12f76f96fe912e7f1d716af733a44d926ec49`;
      authorization record `e938eb62807965e864f3c5dade973d5259675187a406745a963bb724712f7e5c`
      bound (claim mints at the launch boundary); binary sha256 == pin
      `276d5b698a6b706154f3af588f6f885b3aebe518f4ecc8f869abf71383b1904c`, no
      openttd processes. Binary resolution correction of record: the cargo-
      flow-2 pipeline resolves the binary from the harness filesystem pin
      (`harness.py` `BINARY = /home/fed/Downloads/openttd-15.3-linux-generic-amd64/openttd`,
      re-verified sha + no-processes at run start, launch guard line
      `sha256(BINARY) != BINARY_SHA256 or matching_processes(BINARY)`) —
      **no `OPENTTD_BINARY` export is needed** for this entrypoint (corrects
      the round-5 ticket's env-export note; the `OPENTTD_BINARY` env override
      belongs to other entrypoints); no env export was performed and the
      graphics resolve from the staged candidate, so the run needed nothing
      exported
- [x] The launch command of record executed exactly once
      (`corridor_cargoflow2_native run <candidate-6>`, transcript
      `/tmp/opencode/t6_run_output.txt`, run return code 0); nothing
      else launched
- [x] Claim mint + single-use consumption: `CLAIM.json` bound
      `prelaunch_digest e929d7b2…ec49` / `authorization_sha256
      e938eb62…c7e5c` / operator identity `cbb63ff5…40c614`,
      `consumed=true / launches_allowed=1 / retries=0`;
      `LAUNCH-CONSUMED.json` sha256
      `329334b7d887037797ed29b9d39238c676cf8094a0e8939da7b0e4b717b02f02`
- [x] Ladder of record 25/25, zero halt (`"halt": null`): site-00 READY
      (tick 15, funds 489650); engine-00 READY (round-2's
      `ENGINE_PIN_MISMATCH` class absent, E111 census fix live-true,
      running_cost 421); purchase-00 BUILT (quote 4429 exact, funds
      485221, under the 5,000 fence); vread-00 READ; order-00/order-01
      ORDERED; order-read-00 ORDER_SET_VERIFIED; monitor-00 ARMED;
      start-00 STARTED; vread-01 READ; **arrive-00 ANCHORED** at
      (712232, 292) observed funds 485217 — the round-5
      `CARGOFLOW2_FUNDS_DIVERGED` halt class did NOT recur; flow-00..
      flow-11 READY with the native observed funds series
      [485217, 485212, 485206, 485201, 485195, 484997, 484991, 484986,
      484980, 484974, 484776, 484770] and zero observed income;
      finance-00 FINANCE_VERIFIED (day 712287, funds 484769, income 0,
      delivered 0); finish-00 PHASE_STOPPED. Run JSON of record:
      `{"status":"NATIVE_CARGOFLOW2_COMPLETE","verified":true,
      "returncode":0,"cleanup_complete":true,"state_changed":true,
      "command_accepted":true,"halt":null,"native_launches":1,
      "connections":1,"requests":25}`; phase verification
      `CARGOFLOW2_COMPLETE`; phase seal == `e929d7b2…ec49`, phase
      plan_digest `98d055c4e826296f79a8e7d70275be14256229732637fc6cdf547dca47f506ca`
- [x] Delivery verdict of record (the attempt's own class):
      `CARGOFLOW2_LOADED_NEVER_DELIVERED` — "a load was latched, but no
      unloaded amount reached the bay acceptance chain inside the
      ladder". Observed chain: the corridor's empty bay arrival at
      day 712251 (flow-04, tick 1677); pickup arrival flow-08 at 712270
      (tick 3086); loads 5 / 10 / 15 at 712271 (flow-08, ticks
      3174/3194/3214) + 20 at 712272 (flow-09); loaded departure
      20 t cargo-0 at 712274 (flow-09, tick 3398); the delivery leg
      still in transit at finish (location 50095, RUNNING) with
      `unloadings: []`; the 55-day ladder's last stop (finance-00,
      712287 = anchor 712232 + 55) precedes the delivery leg's return —
      a load latched and never unloaded inside the ladder is the
      terminal fact, not a relabeled halt
- [x] Native funds cross-reality booked UNKNOWN (ticket 06 material):
      the production fences of record all passed as recorded —
      arrive-00 anchored exactly on the E114-recorded walk level
      (485217 == 485217) and finance-00 FINANCE_VERIFIED — yet the E114
      probe/VM twin's later walk-of-record levels (flow-01 485217 → …
      flow-06 484996 → … flow-11 484775) differ from the native
      observed series (flow-01 485212 → … last flow 484770, finance
      484769, a consistent corridor-tail offset); the reconciliation
      between the twin's probe-derived figures and the native observed
      series is UNRESOLVED ledger material carried to ticket 06 —
      never reconciled by hand, never fudged
- [x] Post-run evidence of record complete: root 68 entries;
      25 request/response receipt pairs + `frames.json` + `receipt.json`
      + `result.json` + `cleanup.json` + `runtime-identity.json` +
      `session-before-identity.json` + `session-before.sav` +
      `after-diagnostic.sav` + `artifact-manifest.sha256` re-validated
      **66/66 OK, 0 non-OK**; `PRELAUNCH.json` seal byte-equal +
      sidecar after the run; `isolated/` disposed empty shell
- [x] Read-only replay of record executed once post-consume (`verify`
      exit 0 — completion verified by the module's exit rule of
      record); certified cleanup of record all-true:
      `reaped / sockets_closed / workspace_disposed / credential_removed`
      all true, `remaining_processes: []`, endpoint checks
      `connection_closed=true` (game 36457 / admin 58297, kernel states
      recorded); post-run process check: no openttd process
- [x] Integrity close booked in one commit: ticket + backlog row + E116
      evidence row + AI_HANDOFF cargo-flow-2 terminal block;
      `git diff --check` clean; `CONTEXT.md` pin == authority-manifest
      current `847d710abe87e2ed211a72d6455f3f1326b1476eca1711ab8be900080ec2984d`;
      candidates 1–6 PRELAUNCH seals re-digested == sidecars
      (candidate-5 stays consumed terminal history, round-5 verdicts
      unrelabeled); no push (agent sessions never push)
- [x] Hand-over: delivered-class loop returns to ticket 06 — the round-6
      outcome class is COMPLETE-not-delivered
      (`NATIVE_CARGOFLOW2_COMPLETE` with delivery verdict
      `CARGOFLOW2_LOADED_NEVER_DELIVERED`), which ticket 06's current
      text does not yet spell out ("only a delivered launch completes
      this ticket; a halt routes through ticket 05") — the adjudication
      framing for this complete-not-delivered class is put to the
      operator; no further approvals implied by this booking
