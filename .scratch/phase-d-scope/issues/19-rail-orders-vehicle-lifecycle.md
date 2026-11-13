# 19: Rail orders/vehicle lifecycle

Type: task
**What to build:** engine and wagon consist plus GS-side orders through the rail package, offline: purchase, consist assembly, order assignment, and dispatch-shape verification — the road side's vehicle lifecycle mirrored for rail, per ticket 08's consist and station-join decisions.

**Blocked by:** 18 (rail tracer corridor).

**Status:** ready-for-agent
**Gates:** implementation starts only after M0 approval; offline only, zero native claims; no commit.

- [ ] Consist policy implemented exactly as ticket 08 decided (fixed engine + wagons assembled via wagon-move ops, or the decided alternative).
- [ ] Orders lifecycle implemented per ticket 08 (GS-side orders; station join policy per decision).
- [ ] Vehicle lifecycle types honestly: purchase, depot, and order refusals carry named classes.
- [ ] Suites extended and green; pinned digests byte-stable; zero native claims; no commit.
