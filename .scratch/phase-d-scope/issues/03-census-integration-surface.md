# 03 — Census integration surface

Type: wayfinder:grilling (HITL)
Blocked by: 01

## Question

Decide whether and how per-world tile classification rides the loop's capture
path, so that a random-world delivery attempt classifies the tiles it plans
over (the P08 `INCOMPLETE_TILE_CLASSIFICATION` state, and the corridor-bound
refusals that consumed the 2026 battery: `NATIVE_CORRIDOR_BOUND` E198,
`NO_BOUNDED_CORRIDOR` E201).

The decision must fix, as reviewable criteria (not code):

1. Surface: an additive protocol in the wire-contract family (protocol numbers
   4–11 are taken; the box census is 9, depot mutation 10, cargoflow-2 is 11),
   reusing the schema-2 `tile_classification_page` contracts proven natively
   in the Seed-17 census (E16: 90/90 pages, 450/450 tiles) — or an explicit
   decision NOT to integrate (and what classification evidence the backbone
   then plans on).
2. What the loop does with UNKNOWN-class tiles: typed corridor-bound refusal
   (today's honest behavior) vs planning-with-classification (the D-chain
   approach), and where each is allowed.
3. The fusion gate stays CLOSED: the sealed `SOURCE_SAVE_FUSION` REJECTED
   verdict (E16, 83 disagreements; ADR-010/012/013 policy layers) is not
   re-opened by this work — state how the new per-world census relates to the
   retained seed-17 census without relabeling anything.
4. The offline acceptance shape: contract tests + a synthetic-census replay
   fixture (the E16-era pattern) — and the fact that native validation rides
   the backbone battery rounds, not a separate capture attempt.

Constraints: this ticket is blocked by ticket 01 because the window-v2 budget
shape determines the capture plan's sealed budget arithmetic.
