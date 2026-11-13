# 07 — Legacy-red triage disposition

Type: wayfinder:grilling (HITL)
Blocked by: nothing
**Status:** resolved (2026-11-12 — operator decision of record; see Answer)

## Question

Decide the per-class repair-vs-seal disposition for the E207 full-suite exit
gate (the first recorded full-suite baseline: 6382 collected, 57 failed,
54 skipped), so the quality floor's "green-or-honestly-triaged" bar has a
decision behind every red class.

The red classes to disposition:

1. **P08 controlled e2e ×51** — legacy known-reds, mechanism matching the
   legacy triage's frozen-fixture digest drift. Repair the fixture generator
   or seal each with a typed reason?
2. **Budget-signature ×3** (NOT in the legacy 53; new-vs-pre-existing status
   UNKNOWN — no prior full-suite baseline exists): `test_sealed_budgets`
   (`assert 410 == 103`), `test_prepare_materializes_a_pending_authorization_candidate`
   (410 pages / 208280 bytes vs sealed 103 / 52324),
   `test_fallback_schedule_is_sealed_and_explicit` (`assert 208280 == 103×508`).
   One shared signature: computed 410×508 vs sealed 103×508 constants.
3. **Workspace-retention ×1** (`test_finalization_failure_cannot_publish_qualification[terminal]`
   — workspace retained after FAILED finalization), separate mechanism, also
   UNKNOWN-status.
4. **Corridor family ×1** — at the legacy count but the failing test is
   `test_corridor_cargoflow2_vm.py::test_ladder_of_record_runs_green`
   ("package dropped request finance-00: no reply"); the triage's named
   target `test_delivered_verdict_never_fires_on_the_terminal_class` PASSED.
   The two on-file descriptions of the historical red disagree — no force-fit;
   decide which description is the triage of record.
5. **Structural-world fixture ×1** — legacy, `cargo_catalog_checkpoint`
   manifest sha256 drift (failed on Linux; the CRLF hypothesis is NOT
   confirmed).

The decision must fix: per class, repair or seal-with-typed-reason; who
verifies the 4 extras' new-vs-pre-existing status (the UNKNOWN of record); and
the re-run gate that ends the quality floor (full-suite green or every
remaining red carrying a typed disposition) BEFORE Phase D's first native
round.

## Answer

Resolved 2026-11-12 by the operator in-session, on the dossier of record
([research/02-e207-triage-dossier.md](../research/02-e207-triage-dossier.md)):
**repair ×4, typed seal ×1.**

1. **P08 controlled e2e ×51 — REPAIR.** Restore the six re-serialized fixture
   JSONs to the canonical compact serialization their seals and the test's
   byte-comparison expect (the `materialize()` form). Content identical — a
   re-serialization restore, not regeneration, not a code change; validated
   end-to-end by the dossier's probe.
2. **Budget-signature ×3 — REPAIR.** Update the three stale 512-era seals to
   the widened constants of record (410 pages / 208,280 bytes — the intended
   2048-tile state since `5e398db`, 2026-11-07). Pin the literals as the new
   values of record; do not derive the assertions from the same constants
   they pin. Extras' status closed: pre-existing since 2026-11-07.
3. **Workspace-retention ×1 — SEAL (typed).** Typed reason names the
   mechanism (an unrelated machine socket on the frozen ephemeral ports
   skips the sole disposal call; kernel rows not retained; capable code
   predates the legacy freeze). No production cleanup-code change in the
   quality floor.
4. **Corridor ×1 — REPAIR (re-key).** Red of record is
   `test_corridor_cargoflow2_vm.py::test_ladder_of_record_runs_green`
   (composition drift: delivered-composition tail step 60 vs the v1
   schedule's 55). Re-key the ladder tail to the delivered composition of
   record; every other rung stays pinned; the ladder must still fail if the
   package drops a request.
5. **Structural-world ×1 — REPAIR.** Restore `runtime-identity.json`'s
   serialization to the exact byte form its checkpoint manifest pins;
   verify the manifest digest passes afterward. CRLF hypothesis retired.

The four extras' UNKNOWN is closed as recorded: budget trio pre-existing
since 2026-11-07; workspace-retention "answered in part" (path predates the
freeze; pre-E207 firing unanswerable — no prior baseline, kernel rows not
retained). Nothing promoted beyond its evidence.

Execution belongs to ticket 10; the full-suite re-run gate is ticket 11.
