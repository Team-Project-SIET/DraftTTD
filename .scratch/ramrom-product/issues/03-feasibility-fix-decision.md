# 03 — The feasibility-fix decision

Type: grilling
Status: resolved
Blocked by: 01

## Question

The diagnosis of ticket 01 will rank suspected root causes behind
`NO_FEASIBLE_SERVICES` (compatible=16, candidates=0). This ticket decides
the fix-of-record approach for the ramrom product line: which layer
changes (the P08 qualification gates, the capture budgets/rectangular
seals, the engine-catalog matching, the discovery filters, or the world
settings the product generates with), what the new acceptance bar is
(the seed battery of record — offline fixture seeds that must qualify
through the extended surface, plus the native proof seeds to be granted
per attempt), and what stays honestly-typed on a seed that yields no
service. Anchored on the user decisions already taken: "make feasibility
work", the world settings clause (256×256 temperate flat 1950-01-01,
towns 3 / industries 3), and the per-attempt native grant rule.

## Answer

Decided 2026-11-07 under the operator's in-session directive ("develop to
production, do until end of all tasks"); the decision rides the diagnosis
of record rather than re-opening a menu. Spec of record:
`docs/specs/ramrom-product.md` §2. In one line: widen the capture seal —
`capture_tile_limit` gains 2048 (profile `random-rectangle-2048-v1`,
never reinterpreting 512-v1), the spare budget is consumed on the
shorter axis with a `capture_edge_pad` (default 6) so corridors get real
detour room; every typed rejection stays honestly typed; command-of-record
defaults `--capture-tiles 2048 --capture-seconds 120 --capture-pad 6` on
`run --random-world`. Acceptance bar: offline shape/fixture tests first,
then per-attempt granted natives (seed 2026 new identity, seeds 7/8/9 if
granted; battery bar = ≥1 verified plan+delivery terminal).

