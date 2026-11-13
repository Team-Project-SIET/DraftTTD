# 04 — Rail script-API surface study

Type: wayfinder:research (AFK)
Status: resolved (2026-11-12 — read-only subagent study complete; note of
record [research/01-rail-api-surface-study.md](../research/01-rail-api-surface-study.md),
161 lines, every claim file:line-cited)
Blocked by: nothing

## Question

Establish, from local sources only, what OpenTTD 15.3's script API provides and
lacks for a rail analog of the road-freight stack — the fact base the Phase D
proposal's rail workstream (offline build only) needs before its contract
shape can be decided.

Resolved this session by a read-only subagent study over:

- `ottd/src/script/api/` — the pinned 15.3 sources: `script_rail.*`,
  `script_railtypelist.*`, `script_basestation.*`, `script_station.*`,
  `script_waypoint.*`, `script_depotlist.*`, `script_vehicle.*`,
  `script_engine.*` — build/construction methods, stations/depots, vehicle
  purchase, orders, signaling, error semantics.
- `OpenTTD-Knowledge/` — rail constraints in the local reference docs.
- `app/simulation/openttd/` — the three pattern families a rail build must
  mirror: wire-contract protocols (corridor_*.py, protocols 4–11), GameScript
  packages (d5_*_package/main.nut pin tables + refusal ladders), proof
  pipelines (proof/*_native.py: prepare|preflight|run|verify).

Output of record: [research/01-rail-api-surface-study.md](../research/01-rail-api-surface-study.md) — RESOLVED
2026-11-12. Verdict: the 15.3 script API provides the full rail build surface
(track, depots, stations, waypoints, signals, costs) and GS-side orders since
14.0; the five hard gaps are (1) signals are electric-only with **no
block-occupancy/reservation query**, (2) no slope→track oracle (only
`ERR_LAND_SLOPED_WRONG` + `GetSlope`), (3) no curve-limit API, (4)
`GetBuildCost` is base-price only so quoting needs `ScriptTestMode` +
`ScriptAccounting`, (5) precondition violations abort the Squirrel callback so
the .nut refusal ladder must pre-validate everything. `GSRail` appears in the
repo **only** as a forbidden symbol in the observe-only bridge gate
(`proof/harness.py:320`) — a rail analog is a new additive package
composition, never an edit of frozen road packages. The note's §5 lists five
operator questions that graduate into ticket 08 (rail offline-build scope).

Facts already verified this session: no rail code exists anywhere in `app/`
(grep hits were `CheckConstraint` false positives); rail delivery is named
outside the demonstrated MVP (README :174); rail is offline-build-only in
Phase D (operator decision, Round 2) — the study must NOT scope native work.
