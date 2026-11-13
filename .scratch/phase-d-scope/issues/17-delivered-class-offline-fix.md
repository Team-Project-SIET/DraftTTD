# 17: Delivered-class offline fix

Type: task
**What to build:** the diagnosed root cause fixed offline on the corridor line: the fix lands with suites green and the ready-gate satisfied, so the ×1 candidate round (ticket 27) has a fix waiting. From the operator's perspective: the twice-reproduced terminal has a designed answer, unproven until the gated round.

**Blocked by:** 16 (delivered-class diagnosis).

**Status:** ready-for-agent
**Gates:** implementation starts only after M0 approval; no native run; E36 remains open pending actual DELIVERED receipts; no commit.

- [ ] Fix implemented against the confirmed root cause only — no speculative hardening beyond it.
- [ ] Corridor-line focused suites green; the fix's typed surfaces stay honest (no new silent paths).
- [ ] Sealed corridor contracts and digests of record byte-stable wherever unchanged; additive changes versioned.
- [ ] Lint and type checks of record clean on touched paths.
- [ ] No native run; no commit.
