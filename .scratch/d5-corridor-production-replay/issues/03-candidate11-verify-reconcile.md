# Production round 03: verify + offline truth reconciliation

**What to build:** the production `verify` over candidate-11's consumed
launch (the E134 arm-inheritance fixed verifier in the tree) and the
fresh T09-class offline truth reconciliation driver over the retained
run evidence — the reconciliation-debt method of record under the round
grant. **Blocked by:** 02 (the ONE launch consumed). **Blocked-to:**
none (README update follows outside this tracker).

**Status:** done 2026-11-06 (verify exit 0 `CARGOFLOW2_COMPLETION_VERIFIED`
with the phase verdict replayed verbatim; reconciliation
`T09-CLASS RECONCILIATION PASS — 18 PASS / 0 FAIL` exit 0; one commit,
no repo code change, no push)

- [x] **The production verify passed with the phase verdict of record
      replayed verbatim:** the E134 arm-inheritance-fixed verifier ran
      on candidate-11 and exited 0 with the top-level verification
      `CARGOFLOW2_COMPLETION_VERIFIED`; its independent replay
      re-derived `CARGOFLOW2_COMPLETE` with the phase verdict
      **`CARGOFLOW2_LOADED_NEVER_DELIVERED`** and its statement "a
      load was latched, but no unloaded amount reached the bay
      acceptance chain inside the ladder" — the replay is arm-correct
      in the tree and matches the launch figures figure-for-figure
      (anchor 712232 tick 291; the four loads; the departure
      flow-09 20 day 712274 tick 3397; the bay arrivals flow-04 0
      day 712251 tick 1676 and flow-12 20 day 712291 tick 4648;
      `unloadings` []; the finance day 712292 delivered 0 income 0
      funds 484764 tick 4711; the finish-00 `PHASE_STOPPED` RUNNING
      speed 36 tick 4712; running cost 421)
- [x] **The offline truth reconciliation driver passed
      T09-class:** script + transcript
      `/tmp/opencode/t03_c11_reconcile.py` +
      `/tmp/opencode/t03_c11_reconcile_output.txt` (read-only over
      the retained run evidence; no repo write;
      adapted fresh from the t07 candidate-9 driver with
      candidate-11's constants of record): **`T09-CLASS
      RECONCILIATION PASS — 18 PASS / 0 FAIL` exit 0** — the run
      terminal fact binds rc 0 + complete + verified;
      `CLAIM.json` single-use bound to the seal `a6aa529f…4473c564`
      + the authorization record `c6ff5a9c…40ddf1` + the operator
      key identity `cbb63ff5…40c614` with launches_allowed 1 /
      retries 0; the load → departure → arrival → unload-attraction
      → bay-acceptance chain rows verbatim (the three flow-08 loads
      5/10/15 day 712271 ticks 3173/3193/3213 plus the NEW flow-09
      20-load day 712272 tick 3233 — four loads, candidate-9 had
      three; the departure flow-09 20 day 712274 tick 3397; the bay
      arrivals flow-04 0 day 712251 tick 1676 and flow-12 20
      day 712291 tick 4648; then the chain stops — `unloadings`
      empty — and the bay acceptance never moved: finance delivered
      0 income 0 last_accepted 0 funds 484764 tick 4711); the
      finish-00 of record `PHASE_STOPPED` vehicle RUNNING (load 20,
      speed 36, tick 4712); the anchor day 712232 tick 291; verdict
      COMPLETE + LOADED_NEVER_DELIVERED never stretched; the ADR-0001
      funds fence zero-residual at every observed instant via the
      reconciliation's own ONE offline replay invocation over the
      retained request/response files (arm-correct `parse_for`,
      the delivered schedule of record, the offline engine verdict
      and every chain row byte-equal to the retained rails); the
      observed funds walk spans 489650 → 484764 over 26 receipts
      with the purchase instant 489650 → 485221 at tick 17
      (purchase 4429) and every engine income delta observed 0
      (26 deltas, ADR D2) with the D1 running-cost attribution 421
      exact (E114-class); the script-tick discipline held 26/26
      (every receipt day rides its observation tick); the E114 twin
      figure rode read-only: twin(E114) 484775 vs native
      (candidate-11) 484764 — comparison stays UNKNOWN, never
      reconciled by hand
- [x] **E36/E114 disposition of this round rides the books:** E36
      stays OPEN — candidate-11 is the same delivered arm through
      the same discharged-bay spec, not a genuinely competing
      executable route; the delivered-miss is now twice-reproduced
      on fresh identities (candidate-9 E131–E135, candidate-11
      E136–E138) and E36's own rule keeps it open until native
      DELIVERED receipts arrive from a genuinely competing route;
      E114 stays UNKNOWN (the twin figure class is untouched; the
      native close of record is now 484764 twice, candidate-9 and
      candidate-11, against the twin offline walk 484775)
- [x] Books: this ticket, backlog row, E138 row, AI_HANDOFF tail
      cell; one commit; no push; no repo source change this ticket
      (transcript note: the AI_HANDOFF tail was first written with
      the ticket-02 cell landing after the ticket-03 cell and the
      E136 cell's next-frontier tail clobbered by a wrong-anchor
      replacement; found in the post-commit order scan, spliced
      back into the correct E136 → E137 → E138 order, and the
      round's single commit amended with the corrected bytes —
      the broken intermediate was never referenced anywhere
      (audit honesty note))
