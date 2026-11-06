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

**Status:** terminal-by-supersession (2026-11-06, operator-authorized
close-out round) — the one launch this ticket describes never reached and
will never run at its round identity: the round-3 review's verdict of
record was `REVIEW-FINDINGS` 45/46, and the post-review ticket-07
parameterization made the freshly staged candidate-3 seal
(`42f6bbaf…e41d`) stale — the freeze-pin machinery refused the post-07
composition by design (the round-3 staging row + the
`docs/poc-ticket-backlog-2026-11-04.md` status log carry the
supersession of record). A seal-superseded candidate is never signed,
never launched, never relabeled — no native run exists for this identity
and none was ever authorized. The cycle re-entered at round-5, whose gate
files (01/02/03/04 round-5) are all `done` with the round terminal
COMPLETE-not-delivered (E116), reconciliation E117, and the tail closed at
tickets 08–13. Nothing in this file's checklist ever executed; the items
below stay unchecked as the honest record of a gate that cannot run.

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
