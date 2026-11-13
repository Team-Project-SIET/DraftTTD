# 18: Rail tracer corridor

Type: task
**What to build:** the rail family's tracer bullet, all offline: one straight flat rail corridor (depot + two stations + single track) planned as a candidate, compiled to wire ops on a new rail protocol contract, executed against the rail package in the VM, and verified by offline replay — digests pinned, the three-file suite layout established. From the operator's perspective: rail exists as an additive capability with zero native exposure.

**Blocked by:** 08 (rail offline-build scope decision).

**Status:** ready-for-agent
**Gates:** implementation starts only after M0 approval; rail is offline-build only in Phase D (zero native claims); frozen road packages are never edited; no commit.

- [ ] Rail wire contract on the next free protocol number (claimed after census integration per the ledger note), additive against the frozen families.
- [ ] Rail package composed mirroring the proven package-family pattern; the flat tracer corridor executed in the package VM.
- [ ] Offline replay verify path reproduces the run digest-for-digest.
- [ ] Three-file suite layout (wire / package-VM / staging-replay) green; pinned digests byte-stable.
- [ ] Ticket 08's v1 exclusions enforced as typed refusals; zero native claims; no commit.
