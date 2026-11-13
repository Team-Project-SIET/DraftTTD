# 06 — Typed-feedback policy

Type: wayfinder:grilling (HITL)
Blocked by: nothing (evidence-gated: its inputs exist only after the backbone's first verified cycle)

## Question

Decide the typed, evidence-gated shape of "Closed-Loop Optimization"'s
feedback half, so the heading's word "Optimization" is carried without
crossing the record's honesty boundary ("no parameters change automatically",
README :853-855) and without weakening the OBSERVED/DERIVED/CONTROLLED
segregation.

The decision must fix, as reviewable criteria (not code):

1. Which P05 parameters may be seeded from which P07 evidence classes (the
   existing opt-in path: one verified P07 history entry feeding a comparison
   of controlled cost assumptions — README §"Compare optional feedback-
   informed planning scenarios"). Candidates: infrastructure cost estimates
   (the Attempt-9 £1,003 forecast-error class), vehicle purchase prices,
   supply limits. Each must name its evidence class and provenance label.
2. The opt-in mechanics: explicit flags at plan time, default behavior
   byte-unchanged (the expand-only parameterization precedent), every seeded
   assumption recorded in the plan contract with its source digest.
3. What never happens: no automatic parameter change between cycles, no
   retraining, no native execution implied by a comparison, no UNKNOWN
   promoted to a number.
4. The acceptance shape: offline contract tests pinning default-unchanged
   behavior and every seeded-provenance path; native validation rides the
   backbone's verified-cycle receipts (never a separate native round).

Constraints: this ticket's decision can be written now, but its implementation
and validation land only after the backbone produces ≥1 verified cycle with
per-cycle receipts.
