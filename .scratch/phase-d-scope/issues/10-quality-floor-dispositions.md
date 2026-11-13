# 10: Quality-floor dispositions

Type: task
**What to build:** ticket 07's per-class dispositions, executed: every E207 failing test either repaired (real defect fixed or stale fixture generator made coherent again) or sealed with a typed reason of record. End state from the operator's perspective: each previously red class is green or honestly sealed, and the budget-signature class is root-caused — never constant-patched.

**Blocked by:** 07 (legacy-red triage disposition), 09 (E207 triage dossier).

**Status:** resolved (2026-11-12 — dispositions executed; see Answer)
**Gates:** no native run, no evidence mutation, no commit; `artifacts/` and `CONTEXT.md` read-only.

- [ ] Every ticket-07 disposition executed: repaired tests pass; sealed tests carry their typed reason where the triage of record says it lives.
- [ ] Repairs are real: fixture generators regenerate coherently, sealed constants stay sealed while computed constants are re-derived, and no test is weakened to pass.
- [ ] Focused suites for each touched class green, with no new reds introduced on untouched classes.
- [ ] Lint and type checks of record clean on touched paths.
- [ ] Retained evidence bytes and consumed identities untouched.

## Answer

Resolved 2026-11-12. Ticket 07's dispositions executed (repair ×4, typed seal ×1); 12 files changed, all uncommitted; nothing committed.

- **P08 ×51**: six fixture files restored byte-exact to the canonical compact serialization (the `b10cd2d`/`bf6cc0b^` blobs the seal pins); all five payload digests match; suite **62 passed** (was 51 red at E207).
- **Budget ×3**: seals pinned to the widened values of record (410 pages / 208,280 bytes) with the `5e398db` widening comment; suites 16 + 10 + 8 passed.
- **Corridor ×1**: VM ladder re-keyed to the delivered (2,2) arm — 26 exchanges, tail step 60, plan digest `313879bd…` == `DELIVERED_PLAN_DIGEST_OF_RECORD`; every assertion preserved (drop refusal intact); suite 11 passed; untouched neighbor suite 90 passed.
- **Structural-world ×1**: `runtime-identity.json` restored byte-exact to the `b6f5cfa` blob; checkpoint manifest check passes 6/6, manifest not re-sealed; suite 65 passed.
- **Workspace-retention ×1**: `[terminal]` sealed via typed-reason skip (body byte-untouched; `[integrity]` sibling live); suite 59 passed + 1 skipped. Seal wording of record in the test file, provenance ticket 07 + dossier §3.

Lint: `ruff` clean on all touched paths; `git diff --check` clean. No new failures in any touched file; probes under `/tmp/opencode/`; `artifacts/`/`CONTEXT.md` untouched.
