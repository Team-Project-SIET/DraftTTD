# 08 — Rail offline-build scope

Type: wayfinder:grilling (HITL)
Blocked by: 04 (resolved — the fact base now exists)

## Question

Decide which capabilities enter the rail workstream's v1 offline build, using
the ticket-04 study as the fact base
([research/01-rail-api-surface-study.md](../research/01-rail-api-surface-study.md),
§5). The five operator questions to settle, each with the note's citation:

1. Signaling scheme for the planned corridor — PBS vs plain block — given
   there is no block-occupancy/reservation query (only per-tile
   `GetSignalType`); or v1 runs signal-less single-train corridors and
   signals are typed out of scope.
2. Terrain basis — reuse the proven flat-corridor discipline (the road stack's
   bounded flat corridors; the demo corridor was proven flat post-D3) vs a
   slope-aware extension (which would need a Python-modelled slope→track-bits
   oracle — the API provides none).
3. Consist policy — fixed engine + wagons assembled via `MoveWagon` vs
   group-based auto-replace; and whether composed-train physics stays
   Python-modelled arithmetic.
4. Station join policy — always `STATION_NEW` vs `STATION_JOIN_ADJACENT`, and
   whether coverage-radius contracts get pinned like the road census.
5. Quote fidelity — in-session `ScriptTestMode`+`ScriptAccounting` quoting
   (the road "tested quote" discipline) as the offline contract's cost model,
   and how `GetOrderDistance`'s unspecified units are handled (calibrate
   natively later, or refuse the check offline).

The decision must also fix what v1 explicitly excludes (bridges/tunnels?
NewGRF stations? conditional orders?) so the offline bar stays testable, and
it must respect the operator's Round-2 decision that rail is offline-build
only in Phase D — no native validation is scheduled.
