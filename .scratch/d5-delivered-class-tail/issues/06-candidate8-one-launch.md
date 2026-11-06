# 06: Candidate-8: the one launch (delivered-class attempt)

**What to build:** the single native launch of the signed candidate-8,
exactly once, then the read-only post-state; outcome terminal either way.
The round needs its own explicit in-session native-run approval — never
granted by any book, doc or prior round.

**Blocked by:** 05. **Blocked-to:** 07 on DELIVERED / delivered-miss; the
E112-class loop branch on a preserved halt (a sibling diagnosis round
under a fresh identity)

**Status:** done 2026-11-06 (the ONE native launch, under the
operator's combined in-session grant "Grant Gate C + ONE launch —
Recommended"; exactly one attempt, no retry, no reconnect; outcome
terminal, rc-verbatim, never stretched; one commit, no push)

- [x] Pre-launch gates re-verified fresh: no openttd process; root
      5 entries with the authorization present; seal == sidecar ==
      the approved seal `b29c03a4…9389fa`; the authorization verified
      through the production surface (`verify_authorization` → record
      `0cbc505e…6095`, operator key identity `cbb63ff5…40c614`);
      binary pin re-digested `276d5b69…904c`; budgets launches 1 /
      retries 0 / reconnects 0
- [x] The ONE launch executed exactly once (`run` exit 0; `returncode`
      0; `native_launches` 1; `connections` 1; `requests` 26; preflight
      PASS at run start); `CLAIM.json` consumed single-use bound to the
      seal + record + identity (consumed true, launches_allowed 1,
      retries 0); `LAUNCH-CONSUMED.json` written (schema
      `d5-native-launch-consume`, all three bindings)
- [x] Outcome of record rc-verbatim, never stretched: verification
      `CARGOFLOW2_COMPLETE` — the full 26-row delivered ladder ran with
      zero halts (anchor 712232 at tick 289; latches: cargo 0
      arrival_pickup day 712232, cargo 0 arrival_bay flow-04 day
      712250, cargo 0 arrival_pickup flow-08 day 712270, loads 5/10/15
      at flow-08 day 712271, departure cargo 20 flow-09 day 712274,
      arrival_bay cargo 20 flow-12 day 712291 tick 4646; finance-00
      `FINANCE_VERIFIED` delivered 0 income 0 funds 484764; finish-00
      `PHASE_STOPPED`, vehicle RUNNING at the bay tile 50862 with load
      20) — and the verdict
      `CARGOFLOW2_LOADED_NEVER_DELIVERED`: "a load was latched, but no
      unloaded amount reached the bay acceptance chain inside the
      ladder" — `unloadings` empty, delivered 0, income 0, no bay
      acceptance the whole run. E36 stays open; this is the
      delivered-miss branch → ticket 07 proceeds
- [x] Post-consume certified: 68-entry `artifact-manifest.sha256` OK
      (zero mismatches); seal byte-equal after the run; certified
      cleanup all-true (`credential_removed`, `graceful_attempted`,
      `reaped`, `sockets_closed`, `workspace_disposed`), workspace
      disposed, no openttd process remains; candidates 3–9 PRELAUNCH
      byte-pictures equal to their signed/sealed state; `CONTEXT.md`
      pin `847d710a…984d` intact; one commit, no push
- [x] **The finding of record for ticket 07** (never stretched): the
      post-run standalone `verify` REFUSED — `finance-00` /
      `finish-00` / `flow-12` retained responses fail the readback
      model's ladder pins because the file-replay path constructs the
      readback WITHOUT the arm inheritance the wire seam `parse_for`
      applies ("the response composer never carries the arm key, so
      the readback inherits the correlated request's arm"); the
      retained requests carry `schedule_version` 2, the retained
      responses never do (by design), so the replay defaults to the v1
      arm. The run-time reconciliation itself was arm-correct
      (`verified: true`); no retained byte is wrong — this is a
      verification-surface defect found by the retained bytes' refuse,
      the E129-class surface family; ticket 07's round fixes the
      narrowest layer and re-reconciles
