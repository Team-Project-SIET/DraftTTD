# Spec — D5 corridor PoC tail (round 3 → completion)

**Status: `ready-for-agent` (2026-11-05). Spec of record for the Phase A tail
defined in `docs/roadmap-and-scope-2026-11-05.md` §2 (FD-A-2 … FD-A-6). It
binds the PoC backlog's round-3 gates (T-002/T-003/T-004/T-005), T-006,
T-020, T-021 and T-022. This document grants no runtime authority: every
staging, review, Gate C signing and launch named below remains a separate
explicit in-session operator approval. Nothing is scheduled.**

## Problem Statement

The corridor PoC has burned two native candidates on correctable
implementation defects (`INVALID_SITE` in round 1, `ENGINE_PIN_MISMATCH` in
round 2), both fixed offline with their regression locks green — yet no
freight has been delivered on the corridor. The route-selection optimizer has
never demonstrated a choice among executable corridor routes; the reporting
pipeline has never closed the loop on corridor native receipts; the
operating-expense taxonomy decision is outstanding. Until the gated tail of
the PoC is walked, the project cannot declare its first genuine finish line.

## Solution

One gated execution tail that, in order and always under operator approval:

1. takes the corrected protocol-11 composition through a fresh candidate
   round (stage → independent review → Gate C sign → ONE launch), diagnoses
   and preserves any halt class instead of retrying, and closes the delivered
   class (verdict reconciliation) when a launch completes its cycle;
2. establishes ≥2 natively executable corridor routes so the optimizer makes
   the selection of record among them, with the selected route landing in its
   own delivered attempt;
3. settles the funds taxonomy and replays native receipts into fresh
   reporting output that keeps OBSERVED/DERIVED/UNKNOWN segregated;
4. assembles and records the PoC completion declaration.

## User Stories

1. As the operator, I want each round's staging to derive a fresh candidate
   identity programmatically, so that no consumed identity or stale seal can
   ever be staged again.
2. As the operator, I want the staging gate to refuse when any prerequisite
   pin (world after-save, binary, OpenGFX, funds floor) drifts, so that a bad
   composition never reaches a signature.
3. As the operator, I want pre-launch `verify` to report
   `AUTHORIZATION_UNVERIFIED`/`CLAIM_ABSENT` until my claim exists, so that
   the claim is minted only at the launch boundary.
4. As the operator, I want Gate C to bind my signature to the exact freshly
   staged seal, so that no signature can be reused across candidates.
5. As the operator, I want exactly one launch per candidate with no retry,
   no reconnect and no second attempt, so that consumed outcomes stay
   immutable history.
6. As the operator, I want every halt preserved byte-for-byte with its
   prefix, frames and cleanup certified, so that a halt is evidence rather
   than a failure to delete or relabel.
7. As the operator, I want a halt class to spawn its own recorded diagnosis
   and offline fix round with a fresh identity, so that the corrective loop
   stays bounded and auditable.
8. As the operator, I want the funds taxonomy decision settled as a recorded
   ADR-class decision, so that operating-expense accounting stops being an
   open question inherited from an old design condition.
9. As the operator, I want the completion declaration to be a checkable
   assembly of named artifacts, so that "the PoC is done" either verifies or
   it does not.
10. As a continuation agent, I want staging to carry the corrected package
    bytes and correspond byte-exactly to the shipped composition, so that
    what was signed is precisely what launches.
11. As a continuation agent, I want the independent review to re-derive
    every binding from disk and live modules, so that review is a proof, not
    an opinion.
12. As a continuation agent, I want halt diagnostics executed read-only on
    preserved evidence only, so that no diagnosis ever needs a second launch.
13. As a continuation agent, I want the second corridor route admitted by
    the same bounded admission machinery as the delivered one, so that "two
    executable routes" is a pipeline fact, not a hand assertion.
14. As a continuation agent, I want the selected route to be the optimizer's
    own output over the admitted route set, so that the selection artifact is
    reproducible from its inputs.
15. As an evidence auditor, I want every ledger row to carry the numbers of
    record (suite counts, digests, seals, funds levels), so that rows can be
    re-derived on a fresh clone.
16. As an evidence auditor, I want the funds fence to keep proving the wire
    model and the stub reimplementation agree, so that financial truth is
    double-generated, never single-sourced.
17. As an evidence auditor, I want revenue, OPEX and profit contexts kept
    separate with unmeasured categories UNKNOWN, so that no report can
    manufacture economics.
18. As a reporting consumer, I want corridor reports replayed into fresh
    sibling output with world/seed/plan attribution, so that charts and
    totals are attributable to their attempt identities.
19. As a comparison consumer, I want distinct seed/config/experiment
    identities across any compared attempts, so that comparisons cannot
    conflate lineages.
20. As a maintainer, I want optimization, identity, validation and deadline
    logic to stay in Python while the GameScript only executes company
    commands, so that the trust boundary never drifts.
21. As a maintainer, I want the no-second-shift census lock and its sibling
    regression locks to keep failing the suite the day they would matter, so
    that the round-2 halt class cannot return silently.
22. As a maintainer, I want staging, sealing and manifest machinery shared
    with the family's precedent rounds unchanged, so that identity advance
    stays mechanical and reviewable.

## Implementation Decisions

- **Round identity of record**: each round advances the candidate directory
  constant by exactly one; staging composes from live sources; the PRELAUNCH
  seal is freshly derived; consumed candidates 1–2 remain sealed history and
  are never re-staged or relabeled.
- **Corrective loop semantics**: a launch halt is terminal for that
  candidate. The halt class is diagnosed read-only (E105/E111 method —
  source-level, hypotheses dispositioned, residual unknowns recorded), the
  fix lands offline with regression locks per the E106/T-009 precedent, and
  only then a fresh round identity is staged. No fix ever widens a pin
  fail-closed gate; no verification ever loosens.
- **Second-route admission (M8 block)**: the competing route must be
  produced by the bounded planning pipeline on the same pinned corridor
  world — same stations, same domain families, road-legal path within the
  2..47-tile bound and the funds bounds — and admitted by the same checks the
  delivered route passed. Descriptive duplicates of the delivered route do
  not count; the E36 finding closes only when a genuinely competing
  executable route carries native receipts.
- **Optimizer selection**: selection runs over the admitted route set with
  its existing boundedness (≤16 relationships, ≤8 services, bounded solve
  time) and returns the selection-of-record artifact; the selected route then
  proceeds through its own fresh candidate round and its own gate ladder to a
  delivered attempt. If the admitted set ever falls below two, the round
  records the infeasibility instead of stretching a definition.
- **Funds taxonomy**: the operator decision enumerates the running-cost
  category under the halt-on-unexplained-drift rule (the model of record
  bills the road-vehicle running cost at every charge event of the E113
  event lattice — events at the day-roll anchor + 1 + k·74, keyed by
  their own rolled day, the unstop partial inside the first billed
  event, silent pre-count events, the exact 8.8 carry from the pinned
  display figure with the uint8-wrap borrow kernel unchanged; monthly
  interest + station fees at economy-month boundaries, income
  attributed at the observation instants). OPEX = observed
  native cash deltas only; DERIVED aggregates stay labeled; anything
  unmeasured stays UNKNOWN; revenue is never reported as profit. The
  decision lands as an ADR-class record it can be pointed at later.
- **Reporting closure**: final reports replay native receipts into fresh
  sibling output; attribution (world/seed/plan identity) travels with every
  output; failed planning retains diagnostics, never delivery receipts;
  milestone rates remain script-tick rates, not steady-state throughput.
- **Declaration assembly**: the completion record bundles the delivered-cycle
  receipts, both-route evidence with the selection artifact, the replayed
  reports, gate outputs (offline suites exit 0, manifests intact, terminal
  identities untouched) and the round-close ledger append.
- **Trust boundary**: route optimization, identity, validation, deadlines and
  evidence binding stay Python-side; the GameScript layer executes company
  commands synchronously and returns bounded correlated messages only.
  Source trust, prepared-save and plan identities remain mandatory through
  compilation and replay. No dates or effort forecasts are recorded; progress
  is expressed in gated rounds.

## Testing Decisions

- A good test here pins external behavior — verdicts, statuses, funds
  levels, refusal classes — and never internal call structure; it must fail
  on the defect class it was born from (the inversion lock accepts nothing a
  shifted admission would have passed; the road-type lock fails the suite on
  a package that opens an op without pinning its road type of record).
- Module coverage rides the four existing seams, highest-first:
  1. the production replay verifier over fixture candidate trees — verdict
     reconciliation, halt-class typing, pre-auth `CLAIM_ABSENT`,
     relabel/refusal regressions;
  2. the funds fence — the model of record walked against the stub world's
     independent charge-event reimplementation of the same E113 law to the
     pinned walk levels (485221 → 484775, the two ×192 monthly fees, the
     exact 8.8 whole rows);
  3. the VM package suite against the stub world (including the 15.3
     fail-close road-type idiom) — census admission, purchase quote
     realization, order/loop and cycle semantics;
  4. the wire-to-Nut byte bindings — pin table ↔ ladder/contract equality,
     schedule boundary identities, and the byte-level locks of record.
- The second-route block reuses seam 3's stub world: route admission is
  asserted as the same bounded admission the production pipeline applies,
  and the selection artifact is asserted reproducible from its inputs
  (seam 1/2 fixtures carry the delivered arm).
- Prior art: the consumed-candidate fixture trees, the pin-table binding
  test, the readback-coherence refusal tables and the funds walk of record
  are the templates every new test follows.
- Native runs are never test proof: staging/preflight/verify remain read-only
  artifact-side checks; nothing in the suite mints claims or launches.

## Out of Scope

- Phase B research tickets (fleet/capacity exercise, matched A/B, five-year
  economics, consolidated OPEX/ROI, full regression) — separately approved,
  not part of PoC completion.
- Phase C Random World work (reconciliation, any native random generation or
  delivery).
- executable terrain preparation (obstructed clearing, bridges/tunnels),
  > 256×256 worlds, > 32 industries, direct player control of the
  Python-operated company.
- Evidence regeneration of any kind; ledger rewrites; historical zone
  modifications; wall-clock schedules.
- Commit/push authority (staging allowlist is a separate operator decision).

## Further Notes

- The gates remain individually binding even for the agent assigned this
  spec: approval for staging is explicitly in-session; review labeling never
  substitutes for the operator's own requirement gate; a launch without the
  operator's separate approval is a defect in the process, not a rounding.
- Halt-class contingency content (diagnosis/fix rounds) is part of this
  spec's semantics, not a change of scope: the ladder is expected to require
  zero or more such rounds before the delivered class.
- On completion, the round-close E-row appends and this spec's contract is
  discharged.
