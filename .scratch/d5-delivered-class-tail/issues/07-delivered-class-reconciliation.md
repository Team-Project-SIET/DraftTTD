# 07: Delivered-class reconciliation

**What to build:** the offline truth replay of record over the delivered
class (or the terminal state T-06 actually produced) — unload-chain
reconciliation, funds fence across the unload leg, labels of record —
read-only, one replay invocation.

**Blocked by:** 06. **Blocked-to:** 08 (the E36 closure decision)

**Status:** done 2026-11-06 (the round that fixed the E133 find at the
narrowest layer and re-reconciled; the offline truth replay executed as
its ONE replay invocation over the retained bytes; driver
`/tmp/opencode/t07_c9_reconcile.py` + transcript
`/tmp/opencode/t07_c9_reconcile_output.txt`; the fixed surface's own
`verify` re-run read-only; no native action, no candidate writes; one
commit, no push)

- [x] The verification-surface fix of record: `verify_cargoflow2_attempt`'s
      response-file replay loop now inherits the arm from the correlated
      retained request exactly as the wire seam `parse_for` does (the
      response composer never carries the arm key; retained requests
      carry `schedule_version` 2) — a `~5`-line change at the narrowest
      layer, no retained byte touched, no run behavior change, the v1
      candidates' replay math untouched (`parse_for` with an unnamed arm
      skips the injection and validates as before); focused suite
      re-run green (native 49 passed including the new
      `test_delivered_replay_inherits_the_retained_request_arm` chip:
      `parse_for` accepts the delivered-arm finance pair at tail 60
      while a raw `model_validate_json` re-parse refuses at the v1 tail
      55 — the replay defect of record pinned at the readback
      resolution); planning suite green (18); `ruff` clean; `uvx ty`
      returns only the pre-existing LSP diagnostic of record at the
      stated ceiling
- [x] The fixed surface's own re-reconcile: production `verify` on
      candidate-9 → `CARGOFLOW2_COMPLETION_VERIFIED` exit 0 with the
      phase verdict verbatim `CARGOFLOW2_LOADED_NEVER_DELIVERED` — the
      engine of record re-derives the whole attempt from the retained
      bytes fail-closed (fence zero-residual at every observed
      instant), no relabel, no stretch
- [x] The offline truth replay (`T09-CLASS RECONCILIATION PASS` — 14
      PASS / 0 FAIL, one replay invocation, read-only):
      load → departure → arrival → unload-attraction → bay-acceptance
      reconciled rows-verbatim (loads 5/10/15 at flow-08 day 712271;
      departure cargo 20 flow-09 day 712274 tick 3395; bay arrivals
      cargo 0 flow-04 day 712250 tick 1674 and cargo 20 flow-12 day
      712291 tick 4646; unloadings empty — the chain stops after the
      bay arrival; bay acceptance never moved: finance delivered 0,
      income 0, last_accepted 0); the funds fence via the engine of
      record zero-residual at every observed instant (running cost 421
      exact under the E113/E114 lattice, purchase debit 4429
      whole-unit, the walk 489650 → 484764 over 26 receipts, every
      income delta 0); ADR-0001 labels travel (OBSERVED retained rows,
      DERIVED attribute sums, UNKNOWN the E114 rail); every quoted day
      figure rides its script tick; audit-side honesty recorded (the
      first passes aborted on the driver's own drafting defects and a
      schema-key mis-read — corrected in-session, retained evidence
      never touched, the failed transcripts overwritten by the final
      corrected run)
- [x] The delivered-miss branch of record, never stretched: the
      delivered class did NOT land — the attempt's verdict of record
      stays `CARGOFLOW2_COMPLETE` + `CARGOFLOW2_LOADED_NEVER_DELIVERED`
      (a load was latched and carried to the bay, but no unloaded
      amount reached the bay acceptance chain inside the ladder); the
      E114 comparison rides read-only as observed (twin 484775 vs
      native close 484764) and stays UNKNOWN; E36 stays open for the
      ticket-08 closure decision; no attempt, candidate or history
      byte touched; `git diff --check` clean; `CONTEXT.md` pin
      `847d710a…984d` intact; one commit, no push
