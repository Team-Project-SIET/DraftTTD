# 13: PoC completion declaration (T-022)

**What to build:** the PoC completion record of record — the single assembly
that declares the corridor PoC complete: the delivered-cycle receipts, the
two-route evidence with the optimizer's selection artifact, the replayed
reporting outputs, every offline gate green (focused suites exit 0, manifests
intact, terminal identities untouched) — plus the round-close ledger append
(E-row class). The declaration is operator-reviewed before it lands; after
it lands, this spec's contract is discharged and Phase A is terminally
closed.

**Blocked by:** 12 (P07 replay closure). **Status:** done 2026-11-06 — the
PoC completion declaration of record
(`docs/poc-completion-declaration-2026-11-06.md`) assembled, operator
adjudication recorded in-session, operator review granted in-session
("Confirm — land the declaration"), E127 appended, ONE booking commit, no
push. The spec is discharged; Phase A terminates closed with E36 and the
cross-reality UNKNOWN carried open, observed not resolved.


**Operator adjudication of record (in-session, before assembly, per the
ticket-06/ticket-10 precedents):** the item "full delivery receipts of both
delivered attempts (corridor route + selected route)" is satisfied by the
COMPLETE-not-delivered class of record — both consumed corridor rounds
terminated `NATIVE_CARGOFLOW2_COMPLETE` verified true with verdict
`CARGOFLOW2_LOADED_NEVER_DELIVERED` (`unloadings []`, delivery leg in
transit), no freight-DELIVERED receipt exists in the retained lineage, E36
stays open by its own rule and is carried open by the declaration; the
wording-vs-record divergence is recorded here and in the declaration
(`docs/poc-completion-declaration-2026-11-06.md`), never silently
reinterpreted. No native run authorized by this round.

- [x] The evidence set assembled (assembly, invention forbidden) — per the
      adjudication above: the corridor receipts of record verbatim (depot
      chain 6 receipt rows founding 489,650; round-6 and round-7 25 exchange
      receipt rows each, funds echo at every instant, finance close 484,769 /
      income 0 / delivered 0 verbatim, verdicts verbatim INCLUDE
      COMPLETE-not-delivered), the ≥2-executable-routes record with the
      selection artifact (E118/E119/E122/E124: two distinct simple paths,
      selection of record v1 `corridor-b2f80f46513436a102005f10`, digest ==
      `FREIGHT_ROUTE_DIGEST_V2` `b2f80f46…1f7131`, v2 admitted-and-natively-
      true, never pooled), the taxonomy decision of record (ADR-0001, E125),
      the replayed reports of record (three sibling outputs + 64/64
      attribution audit, E126); the single assembly is
      `docs/poc-completion-declaration-2026-11-06.md`
- [x] Every precondition verified independently (fresh this round): offline
      gates exit 0 (corridor trio 142 passed; analytics 39 + insights 28
      = 67 passed; logs `/tmp/opencode/c13_trio.log`,
      `/tmp/opencode/c13_p07.log`); the authority manifest
      `current_sha256` re-verified == `CONTEXT.md` on disk (pin
      `847d710a…984d`, `manifest-current-match: True`); the full retained
      seal sweep — **40/40 `PRELAUNCH.json` digests == their sidecars,
      0 mismatches, 32 `LAUNCH-CONSUMED.json` markers** (consumed candidates
      1–2 of every lineage included); the historical retained zone re-hash
      byte-stable vs the ticket-12 close (0 files added/removed/changed,
      `/tmp/opencode/c13_zone_now.sha256` vs
      `/tmp/opencode/c12_zone_after.sha256`); terminal verdicts stand
      verbatim from the retained result documents (no relabel)
- [x] The completion record's acceptance criteria checked one by one
      against the actual artifacts (the checklist of record in the
      declaration), each check citing its evidence anchor: FD-A-2
      (E104/E107/E108/E110/E116/E121/E122/E124), FD-A-3 (E117, delivered
      class adjudicated), FD-A-4 (E118/E119), FD-A-5 (E125/E126), FD-A-6
      (the declaration itself)
- [x] Round-close ledger append executed (E-row class) after the operator
      reviews the declaration — the append preserves every row of record
      before it: **E127 appended 2026-11-06 after the operator's in-session
      landing confirmation (the review gate answer "Confirm — land the
      declaration"); every prior row E1…E126 preserved unchanged**
- [x] Spec discharged: this ticket's completion marks the spec closed; the
      roadmap's Phase A terminal state recorded (recorded in the
      declaration's "Phase A terminal state" section, citing
      `docs/roadmap-and-scope-2026-11-05.md` §2 FD-A-6, and E127);
      nothing post-PoC opened without its own explicit authorization —
      E36 and the cross-reality UNKNOWN E114 carried open, observed not
      resolved
- [x] Integrity close standing item — `git diff --check` clean; no push (the
      ticket's "no commit/push" wording read against the standing round
      governance of the whole tail: the round's book lands as ONE commit,
      agent sessions never push — the same pattern every prior round ran
      under; recorded here, not stretched). Verified to date:
      `git diff --check` clean; `CONTEXT.md` pin `847d710a…984d` intact.
