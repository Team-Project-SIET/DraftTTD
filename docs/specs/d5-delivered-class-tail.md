# Spec — D5 delivered-class tail (the E36 closure)

**Status: `ready-for-operator-review` (draft 2026-11-06). Spec draft of
record for the corridor freight lineage's one open finding: the
COMPLETE-not-delivered class (E36), carried open through the PoC
completion declaration (`docs/poc-completion-declaration-2026-11-06.md`)
by the operator's adjudication. This document grants no runtime
authority: every staging, review, Gate C signing and launch named below
remains a separate explicit in-session operator approval, and the single
native run of the tail passes only its own explicit native-run grant.
Nothing is scheduled.**

## Problem Statement

Every executed corridor freight attempt loaded its vehicle and departed,
and no run ever delivered: round-6 and round-7 both terminated
`NATIVE_CARGOFLOW2_COMPLETE` verified true with verdict
`CARGOFLOW2_LOADED_NEVER_DELIVERED` — loads 5/10/15 at day 712,271 plus 20
at 712,272, loaded departure 20 t at 712,274 (`unloadings []`), the
delivery leg still in transit at the run's final observation, day
712,287 (anchor 712,232 + 55). The ladder of record carries
load-observation exchanges but no unload/cycle-completion observation
stop, so the delivery cycle cannot complete — cannot be *observed
completing* — inside the authored plan. The record's loudest open
finding, E36, closes only when a genuinely competing executable route
carries native DELIVERED receipts.

## Solution

One gated delivered-class tail, in order and always under separate
operator approvals: (1) read-only diagnosis of the terminal in-transit
class over the retained round-6/round-7 receipt timelines; (2) the
offline fix of record that lets the cycle complete within the authority —
typically ladder/observation extensions through the standing
parameterization machinery, never a pin loosening; (3) one fresh
candidate identity through the full gate ladder (stage → review →
Gate C → ONE launch) on the adjudicated binding, with any halt terminal
for that identity and re-entering the ticket-05-class loop; (4) the
delivered-class reconciliation proving the unload chain from the native
receipts; (5) the E36 closure decision and the declaration addendum.

The delivered-class round rides the **v2 corner-swap binding** by
default — the ticket-10 adjudicated competing route, already
ticket-08-admitted and natively driveable (E124) — per the E36 closure
rule ("a genuinely competing executable route carries native DELIVERED
receipts"); the operator confirms or adjudicates the binding at the
staging ticket's round before any composition.

## User Stories

1. As the operator, I want the diagnosis executed read-only on preserved
   bytes, so no diagnosis ever needs a second launch.
2. As the operator, I want the delivery cycle to complete *inside the
   ladder*, so the receipts of record themselves prove the delivery.
3. As the operator, I want the native run to need its own explicit
   approval, and any halt preserved byte-for-byte, so history stays
   immutable either way.
4. As the operator, I want the E36 closure decided on the unload-chain
   receipts with me confirming in-session, so the closure is adjudicated,
   not automatic.
5. As a continuation agent, I want the fix to ride the existing
   parameterization machinery, so no fail-closed gate loosens and every
   v1 byte stays byte-equal.
6. As an evidence auditor, I want the funds fence and the ADR-0001 labels
   to travel to the delivered class, so no report can manufacture
   economics.

## Implementation Decisions

- **Read-only diagnosis**: anchored in the retained timelines
  (`phase.receipts` rows day 712,228…712,287, loads day-converted through
  the E113 clock law `date = 712,229 + floor((tick − 48) / 74)`,
  `DAY_TICKS = 74`, departures vs the finish instant 712,287 tick 4,342);
  hypotheses dispositioned with dispositions of record, residual
  unknowns carried UNKNOWN (the E105/E112 method).
- **Offline fix**: extension of the exchange ladder (and/or the
  observation set) through `schedule_version` advance / the binding
  derivations as architectured at tickets 10–12 of the corridor tail; the
  delivered-class typing added to the wire contract's verification
  surface (the `CARGOFLOW2_LOADED_NEVER_DELIVERED` verdict's delivered
  counterpart) with regression locks born from the failing state; zero
  pin modifications; v1 byte-equality re-proven.
- **One fresh identity**: candidate-8 of the lineage round-identity
  constant; staged once from the settled tree; fresh seal; pre-auth
  `CLAIM_ABSENT` exit 1 by design; the claim mints at the launch
  boundary.
- **One launch, terminal either way**: a preserved halt class is terminal
  for candidate-8 and re-enters via the ticket-05 mechanism under a new
  identity — no retry, no reconnect, no relabel. A completed ladder with
  the unload chain observed lands the DELIVERED verdict of record.
- **Delivered-class reconciliation**: the offline truth replay extends to
  the unload chain (loads → departure → arrival → unload attraction →
  bay acceptance `unloadings` rows), funds fence zero-residual across
  every observed instant, OBSERVED/DERIVED/CONTROLLED/UNKNOWN labels per
  ADR-0001, script-tick day/tick figures never steady-state.
- **E36 closure**: decided in-session on the actual DELIVERED receipts;
  if the receipts do not materialize, E36 stays open — no definition is
  stretched to close it. The completion declaration gets an addendum
  recording the closure (or the open state), supersession-disciplined.
- **Out of scope**: the E114 twin-vs-native cross-reality (stays open by
  its own rule; only its figures ride the reconciliation read-only, never
  reconciled by hand); Phase B/C work of any kind; no roadmap reopening.

## Testing Decisions

- The delivered-class lock fails the suite the day a composition ships a
  ladder with no cycle-completion observation stop — it must fail on the
  exact defect class the two terminal rounds exhibit.
- The funds fence keeps proving the wire model and the E113 law agree at
  every charge event, now across the unload leg too.
- The verdict lock accepts nothing a `CARGOFLOW2_LOADED_NEVER_DELIVERED`
  outcome would have passed; the unload-chain receipt rows are pinned
  verbatim in the reconciliation fixtures.
- Focused suites of record re-run green: the corridor trio (wire + VM +
  native) at its new count, `test_native_attempt_analytics.py`,
  `test_performance_insights.py`, `ruff`, `uvx ty` (the 3 pre-existing
  analytics diagnostics of record stay the ceiling), `git diff --check`.
