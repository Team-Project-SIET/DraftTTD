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

**Status:** reviewed 2026-11-05 — verdict `REVIEW-FINDINGS` (45/46,
exit 0; NOT ready-for-Gate-C; 1 reconciliation debt recorded; script +
transcript outside the repo)

- [x] One fresh audit script (per-round precedent; never the candidate-bound
      old script) re-derives every binding and writes its full output
      transcript outside the repo tree
- [x] The staged candidate is untouched throughout: seal re-digested
      unchanged at the audit's end; root-shape invariants held
- [ ] Fix-carry proof: the staged package bytes contain the T-009 fix exactly
      where the reviewed source puts it; staged↔source byte-equality holds
      for both AI and package; ~~frozen-inventory digests reconcile~~ —
      **NOT reconciled: 1 of 3502 entries**
      (`app/simulation/openttd/corridor_cargoflow2.py`, staged
      `d72d1762…` vs live `477732f0…` — the check that failed, check 37;
      the byte-equality sub-classes and fix-carry subsets themselves PASS)
- [x] Every consumed/staged predecessor re-digested byte-identical; no write
      inside the repo; no staging rerun; no signing; no claim; no launch
- [ ] Verdict of record ~~`READY-FOR-GATE-C`~~ with zero reconciliation debt —
      **actual verdict: `REVIEW-FINDINGS`** with the debt: a fresh T-002
      round must stage a new candidate from the post-07 source (ticket-07
      default-binding digests reconcile byte-equal live, checks 32–33), then
      re-review, then Gate C, then the ONE launch
- [ ] Review row appended to the PoC backlog status log (DONE — row written
      above); `git diff --check` clean; `CONTEXT.md` authority pin intact;
      no commit/push
