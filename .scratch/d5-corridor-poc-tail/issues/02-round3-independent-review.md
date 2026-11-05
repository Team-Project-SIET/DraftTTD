# 02: Round-3 independent review (read-only)

**What to build:** a fresh-context, read-only re-derivation audit of the
staged round-3 candidate — every binding asserted from disk and the live
production modules against the staged bytes (seal, identity quartet, plan
digests, schedule, world pins, funds model statements, budgets, prerequisite
lineage, GameScript byte-correspondence, proverbial frozen inventory) —
ending in the verdict `READY-FOR-GATE-C`, the same method and checks class
the round-2 review of record used, with every script-side incident
self-caught and disclosed.

**Blocked by:** 01 (Round-3 staging of the corrected attempt).

**Status:** ready-for-agent

- [ ] One fresh audit script (per-round precedent; never the candidate-bound
      old script) re-derives every binding and writes its full output
      transcript outside the repo tree
- [ ] The staged candidate is untouched throughout: seal re-digested
      unchanged at the audit's end; root-shape invariants held
- [ ] Fix-carry proof: the staged package bytes contain the T-009 fix exactly
      where the reviewed source puts it; staged↔source byte-equality holds
      for both AI and package; frozen-inventory digests reconcile
- [ ] Every consumed/staged predecessor re-digested byte-identical; no write
      inside the repo; no staging rerun; no signing; no claim; no launch
- [ ] Verdict of record `READY-FOR-GATE-C` with zero reconciliation debt;
      residual risks recorded for the next gates (not blocking)
- [ ] Review row appended to the PoC backlog status log (script, output
      path, checks count, verdict); `git diff --check` clean; `CONTEXT.md`
      authority pin intact; no commit/push
