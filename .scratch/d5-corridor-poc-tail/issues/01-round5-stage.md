# 01r5: Round-5 stage (the settled-tree round of record)

**What to build:** the fresh staging round composed from the settled
post-write-cluster tree — every frozen file byte-matches its sealed pin
(verified at staging time; the class that superseded rounds 3 and 4). One
operator-approved action of record: identity advance `candidate-4` →
`candidate-5` + ONE `prepare`.

**Status:** done 2026-11-05 (operator approval in-session; single action;
first attempt)

- [x] Identity advance `candidate-4` → `candidate-5` (only pipeline edit;
      lineage comment of record updated); suites 133 exit 0; ruff/ty clean
- [x] ONE `prepare` → `PRELAUNCH PASS` exit 0 first attempt; candidate of
      record `artifacts/experiments/d5-corridor-cargoflow2-native-candidate-5`;
      seal `d4715fd3b2d0a9f5be831dfcd9f80188a87ef6460173a55763a2ee2457537741`
      — differs from all four predecessors
- [x] **Zero freeze-pin mismatches** across all 3502 sealed entries (the
      first fully-reconciling staging since the write-cluster discipline:
      the round-3/4 debt class cannot recur on this composition)
- [x] Plan digest of record unchanged `5c0998f2…bf2d`; ladder grid v1;
      exit 0 gates; workspace `isolated/openttd-15.3-7wet880f`; ports
      41129/53847; root exactly 4 entries
- [x] Standalone read-only `preflight` → `PREFLIGHT PASS`; pre-auth
      `verify` → `CLAIM_ABSENT` / `AUTHORIZATION_UNVERIFIED`;
      candidates 1–4 seals re-digested byte-identical
- [x] Nothing signed, claimed or launched; no `artifacts/` byte touched
      outside the fresh candidate-5 directory
