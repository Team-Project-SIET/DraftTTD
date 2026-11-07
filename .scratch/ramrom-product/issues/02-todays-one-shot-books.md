# 02 — Books: the two one-shot results of 2026-11-07

Type: task
Status: open
Blocked by: none

## Question

Record today's two honestly-terminated native results in the books so no
session reads a phantom: (a) the seed-2026 random run
`artifacts/demos/playable-demo-3e93cc7d1e8d43aab66a4f653665caaa` —
`NO_FEASIBLE_SERVICES` typed FAILED terminal, 1556/1556 manifest rows
verified, cleanup all-true, no openttd process; (b) the seed-42 demo run
`artifacts/demos/playable-demo-1570c66a2e564613a102b3e95647e8b1` —
aborted typed FAILED when the operator closed the game window mid-run
(client exited 0; P05 had selected 3 services, 33 construction mutations
and the funding mutation landed; deliveries did not finish before the
close; one attempt, no retry). The row belongs in the ledger
(`docs/poc-ticket-backlog-*.md`) and both run facts ride the map's
reading (the second run is the soft-close evidence). No relabeling, no
regeneration, no repo code change; one commit.
