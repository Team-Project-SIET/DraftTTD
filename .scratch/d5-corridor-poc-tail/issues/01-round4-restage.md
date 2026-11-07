# 01r4: Round-4 re-stage (post ticket-07 reconciliation of record)

**What:** a fresh staging round composed from the POST-ticket-07 source —
the reconciliation of the ticket-02 round-3 review finding (the one-entry
freeze-pin debt: candidate-3 was composed pre-07, its pinned contract bytes
stale after the 07 merge, preflight refusing by design). One prepare, new
fresh identity and seal; the corridor plan of record must remain
`5c0998f2…bf2d` byte-level (ticket-07's default-binding invariance);
candidates 1–3 stay sealed history, never reused.

**Status:** staged 2026-11-05, then **seal-superseded** in-session (append
row, PoC backlog) — a post-staging write cluster (the shared-language
append to the root `CONTEXT.md` + two comment rewordings) moved three
pinned sources; three live freeze-pin mismatches; the round's gates stay
closed; the NEXT fresh round (identity advance + ONE `prepare`,
single operator action) composes from the settled tree. Never signed,
claimed or launched; the seal stays byte-exact on disk.

- [x] Round identity advanced `candidate-3` → `candidate-4` (comment of
      record: reconciliation of the round-3 review finding; 1–3 sealed,
      never reused); focused suites re-run green on the edited module
      (83 + 11 + 39 = 133 exit 0), `ruff check` clean
- [x] ONE `prepare` (env of record) → `PRELAUNCH PASS` exit 0 first attempt;
      candidate of record
      `artifacts/experiments/d5-corridor-cargoflow2-native-candidate-4`;
      seal (PRELAUNCH.json sha256)
      `325910c3a4df325408fbb859b251a587232638d9abac73312bd502c793377c9f`
      — differs from all three predecessors (`c7a1c5d5…333b`,
      `f991a440…55d4e`, `42f6bbaf…e41d`)
- [x] **Reconciliation proof of record:** the frozen inventory pins
      `app/simulation/openttd/corridor_cargoflow2.py` at the POST-07 live
      bytes `477732f0…06f` (the exact entry that refused the round-3
      candidate) — all 3502 entries reconcile on the live tree
- [x] Plan digest of record unchanged `5c0998f2…bf2d` (ticket-07
      default-binding derivation); plan model digest `98d055c4…96f`;
      schedule version 1, ladder grid `d5-cargoflow2-ladder-grid-v1`;
      world lineage depot-mutation-3 after-save `183b2027…6a6`
      (`PREREQUISITE_ATTEMPT_SOURCE_SAVE_LOAD`); save-restore GS identity
      present; ports 37155/36957 fresh; workspace
      `isolated/openttd-15.3-9__6eu5v`; root exactly 4 entries
- [x] Read-only gates: standalone `preflight` → `PREFLIGHT PASS` exit 0;
      pre-auth `verify` → `CLAIM_ABSENT` / `AUTHORIZATION_UNVERIFIED`
      exit 1 by design (nothing signed, claimed or launched)
- [x] Candidates 1–3 seals re-digested byte-identical after the round; no
      `artifacts/` byte touched outside the fresh candidate-4 directory
