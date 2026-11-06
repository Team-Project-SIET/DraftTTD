# Production round 01: candidate-11 staging + independent review

**What to build:** a fresh full staging of the production corridor
Cargoflow-2 delivered arm plus its independent fresh-context review —
under the operator's in-session directive of 2026-11-06 ("now I want it
can play on real OpenTTD pls do it … goal is do the production not
demo"), the combined grant for this round (this ticket, the Gate C +
ONE launch ticket, and the reconciliation ticket), one native attempt
at its end, no retry.

**Blocked by:** the closed delivered-class tail (E135) whose
reconciliation method this round reuses. **Blocked-to:** 02.

**Status:** done 2026-11-06 (staged, reviewed `READY-FOR-GATE-C` 40/0,
E136; one commit, no push)

- [x] The staging-defect find of record: the first staging of this
      round (directory `d5-corridor-cargoflow2-native-candidate-10`)
      composed exit 0 `PRELAUNCH PASS` over the delivered arm but its
      staged metadata carried the un-bumped round-identity badge
      (`candidate_directory` literal `…candidate-9` over the
      `…candidate-10` tree) — the per-round badge convention of record
      (candidates 6→7→8→9) missed its move. The staged bytes stay
      preserved at that failed-identity state (seal
      `a01a5929…f8da68`, 32× candidate-10 path literals, 1 stale
      candidate-9 badge literal), never signed, claimed or launched,
      never relabeled or regenerated — the candidate-8 precedent; after
      the badge fix its `preflight` refuses through the frozen-source
      gate ("Frozen source/input changed; no launch permitted"),
      fail-closed, the found defect recorded here
- [x] The fix of record: `CARGOFLOW2_CANDIDATE_DIRECTORY` advanced
      candidate-9 → candidate-11 (supersession = fresh identity only,
      candidate-10 skipped as consumed-by-defect), the lineage comment
      extended with the candidate-10 story, the pinned test literal
      moved with it; focused suites green (native 49/49, planning
      18/18), `ruff` clean; candidate-11 staged fresh from the
      badge-fixed tree — `PRELAUNCH PASS` exit 0, root exactly the 4
      staged entries, no consumption marker, badge == constant ==
      disk (`…candidate-11`, 32 path literals, zero stale 7/8/9/10
      literals), seal `a6aa529f…4473c564` == sidecar
- [x] The independent review (fresh-context read-only re-derivation
      per the E122 method; script + transcript
      `/tmp/opencode/t01_c11_review.py` +
      `/tmp/opencode/t01_c11_review_output.txt`; no repo write by the
      audit): **`READY-FOR-GATE-C` — 40 checks, 0 findings, exit 0** —
      every binding re-derived from disk and the live tree: staged plan
      policy == live `cargoflow2_plan_policy(2, 2)` field-for-field;
      staged schedule == `cargoflow2_schedule(2)` re-digesting to its
      own `plan_digest` `3132bfa0…5e0527`; plan-model digest
      `313879bd…16fda`; instrument tables == their live arm
      derivations (budgets, expected-readback, ladder grid, funds
      fence, world); the freeze-pin chain + D2 closure + dependency
      inventory re-verified; the v1 digests of record byte-equal
      (`98d055c4…f506ca`, `9a4a0778…93e45e`, `26408e77…6b274`,
      `e1cafb23…c08b0`, `5c0998f2…bf2d`); the depot prerequisite
      re-hashed on disk (`4df12e1f…9aab`, after-save `183b2027…6ea6`)
      with the staged source save re-verified through the production
      surface; the 26-row delivered ladder with its full 0..60 offset
      set; authority bounds held (5 + 60 == 65; launch 712228 + 65 ==
      712293); budgets 1 launch / 0 retries / 32 requests; the world
      mode `PREREQUISITE_ATTEMPT_SOURCE_SAVE_LOAD`; the pre-consumption
      root exactly the staged 4 entries; `binary_sha256` at the pinned
      `276d5b69…904c`; authorization still `PENDING`; the seal sweep
      candidates 3–9 (plus the preserved candidate-10 failed bytes)
      all byte-equal to their sidecars; candidates 7/8/9/10 identity
      literals absent from the staged bytes
- [x] Books: this ticket, backlog row, E136 row, AI_HANDOFF tail cell;
      one commit, no push
