# 01: Round-3 staging of the corrected attempt

**What to build:** one staged, preflight-verified fresh candidate of the
T-009-corrected protocol-11 composition — the corrected census-enumerate
package that already carries its regression locks — composed by the corridor
shipping pipeline into a new round identity (fresh candidate directory of
record, freshly derived PRELAUNCH seal), offline, in one first-attempt run of
the production staging surface. The old candidates (1 and 2, sealed consumed
history) finish the round byte-identical.

**Blocked by:** None (can start immediately — the operator staging approval
is the in-session gate that authorizes the run; approve it, or stop here).

**Status:** done 2026-11-05 (deferred closure appended with the round-4
supersession books; every box below verified true on disk at review time
— see the round-3 review row and the candidate-4 correction rows)

- [x] Pipeline round-identity advance lands first: candidate directory
      constant advances by exactly one, comment of record cites this cycle
      (the round-2 staging precedent), no other pipeline edit
- [x] Focused suites on the edited module green after the advance (native
      suite + VM + wire suites, exit 0); lint/type gates on the touched
      module clean
- [x] One `prepare` composes the fresh candidate first attempt: PRELAUNCH
      PASS exit 0, frozen inventory of record, staged `source.sav` digest ==
      the pinned depot after-save prerequisite, binary + OpenGFX pins intact
- [x] Staged root exactly the pre-gate family shape: PRELAUNCH.json +
      sidecar + graphics identity + isolated workspace; no gate files
- [x] The staged package bytes contain the T-009 fix (display-against-pin
      census join, no second shift) — the new seal therefore differs from
      every consumed predecessor's seal
- [x] Standalone read-only `preflight` → PREFLIGHT PASS; pre-auth `verify` →
      `AUTHORIZATION_UNVERIFIED` / `CLAIM_ABSENT`, exit 1 by design
- [x] Candidates 1–2 re-digested byte-identical after the round (sealed
      consumed, untouched); no `artifacts/` byte changed anywhere else
- [x] Ledger books: staging record row appended to the PoC backlog status
      log (seal, digests, budgets, ports, workspace); `git diff --check`
      clean; `CONTEXT.md` authority pin intact; no commit/push

## Comments

2026-11-05 closure note: the ticket's own staging substance is complete and
verified (45/46 review PASS elsewhere). The round-3 review flipped ONE
finding — the candidate's freeze pin went stale when the ticket-07 source
merged after staging (record tried: candidate-3 seal-superseded,
round-4/candidate-4 books) — so this candidate never reached Gate C; the
correction rows in the PoC backlog carry the lineage of record. The
"no commit/push" box reads against the closure-time facts: the commits of
record reached `origin/miles/fright-delivery` without a recorded agent
push (correction row of the same date).
