# 05: Halt-class loop (conditional arm)

**What to build:** the corrective branch of the round-3 machinery. If the
round-3 launch preserved a halt of record, this ticket produces the diagnosis
of record (read-only forensic method of the standing precedent:
source-level root cause with confidence stated, hypothesis matrix
dispositioned, residual unknowns kept UNKNOWN, corrective direction and
regression-lock matrix documented), then the offline fix executed with the
fix-round precedent (one source defect class at a time, every regression
lock the class needs, focused suites + lint/type gates), then re-entry into
ticket 01 as a fresh candidate round with its own operator-gated ladder. If
round 3 delivered, this ticket resolves trivially as "not needed".

**Blocked by:** 04 (Round-3: the one launch). Its "not needed" arm needs
nothing further.

**Status:** in-progress 2026-11-05 — diagnosis-of-record complete (E112);
offline fix + fresh-round re-entry gates remain, each its own explicit
operator approval

- [x] Branch decision of record stated from the round-5 outcome (delivered →
      not needed; halt → proceed)
- [x] On the halt arm: preflight of record shows staged bytes untouched by
      the diagnosis; no candidate reconnection; prior terminal verdicts
      unrelabeled; the diagnosis runs read-only on preserved evidence only
- [x] Diagnosis of record: emitter traced exactly, root cause at source
      level with a confidence class, the family precedent cited, ledger +
      status-log records written; consumed identities untouched
- [ ] Offline fix of record: no wire/protocol loosening, no fail-closed gate
      widened, regression locks for the whole defect class (the class must
      fail the suite pre-fix), suites + lint/type gates green,
      `git diff --check` clean, `CONTEXT.md` pin intact
- [x] Cards block: the next candidate round requires the same staging →
      review → signing → launch gates of tickets 01–04, each its own
      explicit operator approval — this ticket authorizes none of them
- [x] Ledger row appended for every executed sub-step; nothing scheduled
      beyond what the operator approves in-session; no commit/push

**Round-5 arm — diagnosis of record (2026-11-05, E112):** branch decision =
proceed (the round-5 launch preserved the terminal halt class
`CARGOFLOW2_FUNDS_DIVERGED` at `arrive-00`; E110). Bounded read-only
forensics executed on preserved evidence only — script of record
`/tmp/opencode/t005_r5_diag_arrive00.py` + transcript
`/tmp/opencode/t005_r5_diag_arrive00_output.txt` (exit 0, tree clean,
manifest 37/37). Emitter traced exactly: the fence of record
(`Cargoflow2FundsModel.reconcile` residual check, `corridor_cargoflow2.py:1599-1617`)
composed by the runner wrapper (`proof/corridor_cargoflow2_native.py:1572`);
the production replay reproduces the retained phase outcome full-field and
the verbatim halt ValueError. **Root cause (CONFIRMED, high — source level):
the fence's day-charge walk diverges from the observed 4-debit native class
at three term level** — (1) model-only start-day partial charge
(rt = 74−27 = 47 → whole 1; native charged nothing pre-first-rollover),
(2) model-only day-230 borrow bonus (the `(fraction − low) % 256` scheme
books whole 2 where the class charges 1), (3) the unmodeled in-window
day-232 rollover (onset tick 270 ≤ read tick 292; the walk books
`range(prev_day, day)`). Closure: modeled 5 − observed 4 == 2 − 1 ==
residual +1. Native-internal mechanism kept UNKNOWN per discipline: two
policies — (A) flat 1 whole coin per rollover with internal retention and
(B) scalar cumulative `floor(421·elapsed/(365·74))` — both reproduce all 11
retained instants exactly; the fix targets the observed trajectory class,
not an asserted internal policy. Family precedent: E111 (method), E97
(funds-window bound); consumed candidate-5 untouched, round-5 verdicts
unrelabeled.

**Cards block of record (next candidate round):** the round-6 cycle
re-enters ticket 01's ladder with a fresh identity — pipeline constant
`candidate-5` → `candidate-6`, ONE staging `prepare`; then fresh
independent review (ticket 02 method), Gate C signing (ticket 03), ONE
launch (ticket 04) — four separate operator approvals, none authorized by
this ticket; settle-then-freeze: all remaining doc/vocabulary writes land
and are committed before round-6's identity advance.
