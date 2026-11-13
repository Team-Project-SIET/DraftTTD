# 06 — Recovery package design

Type: wayfinder:grilling (HITL)
Blocked by: 01 (controller state machine), 02 (journal schema), 03 (incremental manifest + verify)

## Question

Decide the LR recovery package's contract as reviewable design criteria (not
code) — the D2/D21 recovery rounds: fresh identity + fresh operator grant,
resuming from the last verified checkpoint only.

The decision must fix, as reviewable criteria:

1. The recovery identity's binding of record: which checkpoint (save digest +
   journal cursor + receipt set), which journal lineage it continues, and how
   the recovery attempt's seal references the failed attempt's sealed terminal
   without relabeling it.
2. The rewind-consistency checks of record: world state and the exclusion
   ledger rewind together — the recovered plan set derives from verified-cycle
   exclusions only; a service built in the crashed (unverified) cycle is
   rolled back and may be re-planned without a false duplicate.
3. The correspondence verification of record at recovery: full
   `EXACT_NATIVE_SEMANTIC_CORRESPONDENCE`-shape replay of the loaded
   checkpoint (the D15 limitation — in-run binding was digest-only; recovery
   is where semantic consistency is verified), plus post-run replay.
4. What recovery may never do: replay uncertain commands of the crashed cycle;
   resume mid-cycle; retry in-session; consume anything but a fresh grant;
   load a non-verified checkpoint; load anything but a constructed-fleet save
   (the E176 restore-contract boundary).
5. The typed recovery outcomes: `RECOVERY_VERIFIED` and honest failure classes;
   the D13 accounting (×2 recovery rounds, serial, four-gate ceremony each;
   unused allocations return to ceiling accounting with the reason of record).

Constraints: design-only; no code; no native authority; native recovery
behavior stays UNKNOWN until a real recovery round runs (risk-register item;
never drilled in the shakedown per D16).
