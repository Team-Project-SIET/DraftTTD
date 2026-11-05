# 04: Round-3: the one launch

**What to build:** the single native launch of the signed round-3 candidate —
exactly one run under the pinned binary and graphics at the recorded
invocation shape, then the read-only replay of record (once), the integrity
sweep (manifest, seals, historical zones, pins), and the certified cleanup
(reaped process, closed sockets, disposed workspace, removed credential,
released reservations). The attempt's outcome is terminal either way:
delivered-class evidence if the ladder completes, or a preserved halt of
record — never a retry, a reconnect, a relabel or a relaunch.

**Blocked by:** 03 (Round-3 Gate C signature) — the operator launch approval
is the separate in-session gate that authorizes it.

**Status:** ready-for-agent

- [ ] Pre-launch gates re-verified fresh (no server process, gate surface
      shape, seal == sidecar == approved seal, authorization verified through
      the production surface, binary/OpenGFX/save pins re-digested, budgets
      of record: launches 1 / retries 0 / reconnects 0)
- [ ] The launch command of record executed exactly once with the
      environment exported before Python starts; nothing else launched
- [ ] Post-run evidence of record complete: result, frames, requests/
      responses, logs, session-before save, runtime identity, claim and
      launch-consumed markers with their bindings; manifest re-verified
- [ ] Read-only replay of record executed once and reconciling the run
      verdict exactly (exit status as designed)
- [ ] Certified cleanup of record all-true with no remaining process and
      endpoints verified released; no server process after
- [ ] If the ladder completed: delivery cycle receipts exist (purchase,
      departure, cycles, arrival, unload attraction) and the outcome matches
      the funds fence expectations — hand over to ticket 06
- [ ] If the ladder halted: halt class typed and preserved as terminal
      evidence, `HALTED_BEFORE_MUTATION` honored, nothing mutated beyond the
      documented clock behavior — hand over to ticket 05
- [ ] Integrity close: `git diff --check` clean; `CONTEXT.md` pin intact;
      candidates 1–2 untouched; ledger row appended (RC, verdict, halt
      class / delivered status); no commit/push
