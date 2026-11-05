# 06: Delivered-class reconciliation (T-006)

**What to build:** the corridor delivery ledger reconciliation of record —
once a round-3-class launch completed its cycle with delivery receipts, the
outcome class is reconciled read-only into the delivery ledger: the verdict
replay re-executed against the terminal evidence, the funds fence applied
over the native receipts (the funds model of record walked against the
attempt's observed cash path), the finding of record archived. Only a
delivered launch completes this ticket; a halt routes through ticket 05 and
returns.

**Blocked by:** 04 (Round-3: the one launch), with the delivered arm
resolved — ticket 05's loop must resolve without an open halt first.

**Status:** ready-for-agent

- [ ] Replay of record re-run read-only on the delivered candidate's
      terminal evidence: `CARGOFLOW2_COMPLETION_VERIFIED` (or the family
      verdict of record) reconciled against every exchange of the run
- [ ] Delivery ledger row assembled: the delivered cycle's identities (world
      save, seal, plan digest), the bill-of-cycle receipts (vehicle built at
      the pinned quote once; departure gate behavior of record: partial
      load ≤ capacity, a full-load flag never issued; per-cycle monitor
      snapshots; arrival latches; bay unload attraction series), funds
      levels and income reads of record
- [ ] Funds fence native-side check: the model of record reproduces the
      attempt's observed funds at the observation instants with the 8.8
      carry exact — any unexplained drift is a typed halt of record, never a
      numeric fudge
- [ ] The E36 context of record (no competing executable route) re-affirmed
      as still-open pending ticket 10's closure
- [ ] The old "attempted, not delivered" finding is closed only by this
      delivered record — never relabeled or merged into predecessor rows
- [ ] Integrity close: consumed candidate untouched; `git diff --check`
      clean; `CONTEXT.md` pin intact; ledger row appended; no commit/push
