# 01r6: Round-6 stage (the settled-tree round of record)

**What to build:** the fresh staging round composed from the settled
post-settle-then-freeze tree — every frozen file byte-matches its sealed
pin (the E114 funds-model fix `1724b00` and the E115 doc freeze `540b955`
landed BEFORE this staging, the settle-then-freeze order of record). One
operator-approved action of record: identity advance `candidate-5` →
`candidate-6` + ONE `prepare`.

**Status:** done 2026-11-05 (operator approval in-session "approve
stagging"; single action; first attempt)

- [x] Identity advance `candidate-5` → `candidate-6` (only pipeline edit;
      lineage comment of record updated); focused suites 134 exit 0
      (84 + 11 + 39); ruff clean; ty = the one frozen-mirror `connect`
      baseline diagnostic (E98 census baseline, untouched region)
- [x] ONE `prepare` → `PRELAUNCH PASS` exit 0 first attempt; candidate of
      record `artifacts/experiments/d5-corridor-cargoflow2-native-candidate-6`;
      seal `e929d7b2e749f2a14af9bb19fdf12f76f96fe912e7f1d716af733a44d926ec49`
      — differs from all five predecessors
- [x] Zero freeze-pin mismatches across all 3502 sealed entries (the
      settle-then-freeze order held); plan digest of record unchanged
      `5c0998f2…bf2d`; plan model digest fresh `98d055c4e826…`
- [x] Ladder grid v1, 25 exchanges, max_cost 5000, company 0; workspace
      `isolated/openttd-15.3-m6aqc6ph`; ports game 36457 / admin 58297;
      root exactly 4 entries
- [x] Standalone read-only `preflight` → `PREFLIGHT PASS` exit 0;
      pre-auth `verify` → `AUTHORIZATION_UNVERIFIED` / `CLAIM_ABSENT`
      (exit 1 by design, authorized never consumed); candidates 1–5
      seals re-digested byte-identical
- [x] Nothing signed, claimed or launched; no `artifacts/` byte touched
      outside the fresh candidate-6 directory; no push
