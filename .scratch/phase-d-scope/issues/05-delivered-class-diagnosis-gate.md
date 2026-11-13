# 05 — Delivered-class diagnosis gate

Type: wayfinder:grilling (HITL)
Blocked by: nothing

## Question

Decide the diagnosis method and the ready-gate for the delivered-class
workstream over the twice-reproduced `CARGOFLOW2_LOADED_NEVER_DELIVERED`
terminal (corridor candidates 9 and 11: loads latched and carried to the bay,
zero unloadings, zero bay acceptance; `verify` replays the terminal, not a
delivery). E36 closes only on actual DELIVERED receipts — none exist in any
lineage (E135).

The decision must fix, as reviewable criteria (not code):

1. The diagnosis plan of record over the retained candidate-9/candidate-11
   bytes: which receipts/frames/saves are read, in which order, and what the
   candidate explanations of the unload-chain silence are (unload chain,
   bay-stop geometry, order semantics, watch-window ends) — each with the
   evidence that would confirm or eliminate it.
2. The ready-gate: what the offline diagnosis record must contain before a fix
   candidate round may be staged (a confirmed root cause with the E105/E111
   method's evidence standard — source-verified semantics, not hypothesis).
3. The discipline guardrails: candidates 9 and 11 are consumed forever and
   never re-run; the delivered-class round(s) come from the Phase D native
   budget's ×2 allocation (one candidate round + one corrective contingency);
   E36 stays open until DELIVERED receipts exist, whatever this workstream
   achieves.

Constraints: this workstream runs on the corridor (Cargoflow-2) line; it does
not touch the ramrom loop. Its native rounds are independent of the backbone
battery and may be interleaved by operator choice.
