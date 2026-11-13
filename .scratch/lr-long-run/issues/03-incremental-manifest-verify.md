# 03 — Incremental manifest and verify command of record

Type: wayfinder:grilling (HITL)
Blocked by: 02 (journal schema)

## Question

Decide the LR incremental-manifest design and the LR verify command of record
as reviewable design criteria (not code) — mid-run integrity for a 2 h run,
where the existing finalize-at-end `artifact-manifest.sha256` pattern does not
apply.

The decision must fix, as reviewable criteria:

1. The incremental integrity mechanism: manifest chunks (per journal window or
   per cycle), their hash-chain or digest-binding scheme, and how the final
   complete `artifact-manifest.sha256` is composed at terminal so the standing
   manifest-sweep discipline still verifies it.
2. What each chunk covers (journal segments, receipts, checkpoints) and the
   crash-consistency rule: a chunk is closed only at a verified boundary —
   never mid-cycle.
3. The LR verify command of record: its name, inputs (run dir), and the exact
   checks it performs (seal, journal replay, per-cycle receipt replay, chunk
   verification, checkpoint digests, typed terminal acceptance) — the LR
   successor of `verify_loop_receipt` (E144/E158), reusing its per-cycle
   replay pattern.
4. Failure semantics: what verify does on a torn/incomplete chunk, a missing
   receipt, or a digest mismatch — typed refusals, never repair, never
   regeneration.
5. The offline test shape: chunk-level contract tests + a torn-run fixture
   proving typed refusal.

Constraints: design-only; no code; no sealed identity touched; the command of
record is frozen only at the LR commands-freeze milestone (after tickets
05+08 and the M2 gate).
