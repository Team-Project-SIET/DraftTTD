# 08 — Offline acceptance bar and milestone ladder

Type: wayfinder:grilling (HITL)
Blocked by: 01–07 (all design tickets)

## Question

Decide the LR offline acceptance bar and the milestone ladder's exit criteria
as reviewable criteria (not code) — what "offline bar MET" means for LR, and
what each M-LR milestone concretely requires, before any implementation ticket
is published or any grant is requested.

The decision must fix, as reviewable criteria:

1. The M-LR-2 implementation-bar checklist: which suites/fixture classes
   constitute green (controller lifecycle over every terminal class; journal
   contract tests; chunk-manifest + torn-run refusal tests; budget-schema
   derivation tests from observed costs; package-VM Save/Load round-trip pins;
   per-cycle replay verify tests; v1 byte-compatibility pins for
   loop/corridor/canonical identities), all derived from retained bytes as
   fixtures, never targets.
2. The threshold-validation method of record: how the trigger thresholds
   (backlog T3, cooldown K=2) and the per-cycle pause-cost estimate (3–6 min)
   get validated offline before any native round — the named fixtures, the
   measurement protocol, and the re-derivation of the in-game expectation
   band.
3. The milestone exit criteria for M-LR-0 through M-LR-5, each with its
   evidence artifact (resolved tickets, suite results, E-rows, ledger rows,
   REPRODUCE addenda) and its gate owner (operator vs offline-verifiable).
4. The full-suite gate cadence for LR rounds (aligned with the REPRODUCE
   three-point cadence: pre-native-round / post-seal-or-fixture change /
   effort close) and the version/release-notes discipline for LR identities.
5. The dependency-of-record statement: M-LR-2 cannot exit before Phase D M2
   (tickets 12–15) lands (D20) — and what LR does meanwhile (design tickets
   only).

Constraints: design-only; no code; no grant requested by this ticket; the bar
is stated as criteria, never as a claim that it is met.
