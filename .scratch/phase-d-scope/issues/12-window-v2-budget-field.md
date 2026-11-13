# 12: Window-v2 budget field

Type: task
**What to build:** ticket 01's decided distance-scaled observation-window v2, implemented as a versioned budget field sealed at prepare: random-world plans carry the v2 window, every v1 identity re-derives byte-equal, and extreme-distance behavior types honestly. From the operator's perspective: a seed-7-class haul no longer expires by design default, and no retained record is reinterpreted.

**Blocked by:** 01 (window-v2 formula decision).

**Status:** ready-for-agent
**Gates:** implementation starts only after M0 approval; any native use of v2 is a later, separately granted round; sealed consumed identities untouched; no commit.

- [ ] v2 formula implemented exactly as ticket 01 decided (scale term, floor, ceiling, load-wait treatment, extreme-distance behavior).
- [ ] Versioned surface: the window lives in the sealed budget field, versioned — v1 identities byte-equal, pinned by tests.
- [ ] Existing typed outcomes preserved as ticket 01 fixed them: the WINDOW_EXHAUSTED semantics, the 60-economy-day lifecycle bound treatment, the no-movement guard.
- [ ] Focused suite green on touched paths; lint and type checks of record clean.
- [ ] No native run; no staging; no commit.
