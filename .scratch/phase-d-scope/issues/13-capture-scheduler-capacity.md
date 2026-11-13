# 13: Capture-scheduler capacity

Type: task
**What to build:** ticket 02's chosen mechanism, implemented so a seed-8-class relationship produces captured reads offline instead of an empty schedule — with pause-the-clock pacing and the month-pace gate typed-intact, and retained seed-8/seed-9 bytes used as fixtures (never targets).

**Blocked by:** 02 (capture-scheduler capacity decision), 01 (window-v2 formula decision — the window interaction ticket 02 must respect).

**Status:** ready-for-agent
**Gates:** implementation starts only after M0 approval; the scheduler's native behavior is a later granted round inside the backbone battery; no commit.

- [ ] Chosen mechanism implemented exactly as ticket 02 decided (pacing / cross-session split / window widening / honest typed per-relationship skip).
- [ ] Retained seed-8 and seed-9 fixture bytes produce captured relationships (non-empty schedules) offline, without changing any sealed identity.
- [ ] Pause-the-clock pacing and the month-pace gate keep their typed surfaces (typed-preservation tests).
- [ ] v1 scheduler identities byte-equal wherever the decision requires; focused suites green; lint and type checks clean.
- [ ] No native run; no commit.
