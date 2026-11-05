# 04r5: Round-5: the one launch

**What to build:** the single native launch of the signed round-5 candidate —
exactly one run under the pinned binary and graphics at the recorded
invocation shape, then the read-only replay of record (once), the integrity
sweep (manifest, seals, historical zones, pins), and the certified cleanup
(reaped process, closed sockets, disposed workspace, removed credential,
released reservations). The attempt's outcome is terminal either way:
delivered-class evidence if the ladder completes, or a preserved halt of
record — never a retry, a reconnect, a relabel or a relaunch.

**Blocked by:** 03r5 (Round-5 Gate C signature) — the operator launch
approval is the separate in-session gate that authorizes it.

**Status:** done 2026-11-05 (operator approval in-session; ONE native
launch, first attempt; terminal halt of record; no retries, no reconnects)

- [x] Pre-launch gates re-verified fresh (`/tmp/opencode/` script +
      `t005_r5_prelaunch_gates_output.txt`; nothing stale): no server
      process; gate surface = 4 staged files + AUTHORIZATION.json +
      isolated/, no launch receipts; seal == sidecar == approved seal
      `d4715fd3…41ad`; `verify_authorization` PASS through the production
      surface (record `57284ae0…b01e`, payload `aa936f19…`
      == `staged_cargoflow2_authorization_payload_digest`, operator
      identity `cbb63ff5…40c614`); binary sha256 == pin `276d5b69…904c`;
      staged `source.sav` == world bind `183b2027…efe6a6`; argv pins
      `-D127.0.0.1:41129` / cfg / `-g source.sav` /
      `-dscript=4,grf=1,net=3`; budgets launches 1 / retries 0 /
      reconnects 0 / connection_attempts 1; OpenGFX-8.0 present
- [x] The launch command of record executed exactly once with
      `OPENTTD_BINARY` + `OPENTTD_OPENGFX_ARCHIVE` exported before Python
      starts (`corridor_cargoflow2_native run <candidate-5>`,
      transcript `/tmp/opencode/t005_r5_launch_output.txt`,
      run return code 1); nothing else launched
- [x] Post-run evidence of record complete: 38 retained files + `isolated/`
      empty shell; `LAUNCH-CONSUMED.json` (`schema d5-native-launch-consumed`)
      binds authorization record `57284ae0…b01e` + seal `d4715fd3…41ad` +
      operator identity `cbb63ff5…40c614`; `CLAIM.json` `consumed=true /
      launches_allowed=1 / retries=0`; `artifact-manifest.sha256`
      re-verified **37/37 OK, 0 non-OK**; `PRELAUNCH.json` seal byte-equal +
      sidecar after the run
- [x] Read-only replay of record executed once and reconciling the run
      verdict exactly (`verify` → `PHASE_HALTED_EVIDENCE_PRESERVED`, halt
      label `arrive-00`, `HALTED_BEFORE_MUTATION`, exit 1; transcript
      `/tmp/opencode/t005_r5_replay_output.txt`)
- [x] Certified cleanup of record all-true with no remaining process:
      `reaped=true / sockets_closed=true / workspace_disposed=true /
      credential_removed=true`, `cleanup_error=[]`,
      `remaining_processes=[]`, `returncode=0`; post-run process check:
      no openttd process; workspace isolated dir disposed to empty shell
- [ ] If the ladder completed: — N/A, the ladder did not complete
- [x] If the ladder halted: halt class typed and preserved as terminal
      evidence: 10 of 15 exchanges clean — `site-00 READY` (tick 15,
      funds 489650 — funds fence intact), **`engine-00 READY` (tick 16 —
      round-2's `ENGINE_PIN_MISMATCH` class did NOT recur; the T-009 and
      E111 fixes measured live-true this round)**, `purchase-00 BUILT`
      (tick 18, funds 485221; under the 5,000 max-cost fence), `vread-00
      READ`, `order-00`/`order-01 ORDERED`, `order-read-00
      ORDER_SET_VERIFIED`, `monitor-00 ARMED`, `start-00 STARTED`,
      `vread-01 READ`; then the halt of record at `arrive-00`:
      `cargo-flow 2 funds diverged from the modeled trajectory: arrive-00
      observed 485217, modeled 485216, residual 1` (status ANCHORED,
      world state `HALTED_BEFORE_MUTATION`); phase verdict
      `CARGOFLOW2_GATE_UNDECIDED_INCOMPLETE`, verification
      `CARGOFLOW2_INCOMPLETE`; run JSON `{"preflight":"PASS",
      "native_launches":1,"connections":1,"requests":11,
      "command_accepted":true,"state_changed":true,"verified":false,
      "returncode":0,"status":"PHASE_HALTED_PREFIX_PRESERVED"}` —
      hand over to ticket 05 (halt-class loop); no diagnosis recorded
      here (diagnosis needs a new explicit approval); nothing relabeled
- [x] Integrity close: `git diff --check` clean; `CONTEXT.md` pin intact;
      candidates 1–4 re-digested byte-identical; ledger row appended
      (RC 1, verdict, halt class); no commit/push
