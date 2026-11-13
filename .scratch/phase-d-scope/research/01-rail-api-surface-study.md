# Phase D research note — OpenTTD 15.3 GameScript API surface for RAIL freight services

READ-ONLY study, 2026-11-12. Repo root: `/home/fed/codes/softdev2` (branch devmodule2).
Cited paths are relative to that root unless absolute. Key roots:
- `ottd/src/script/api/` = pinned OpenTTD 15.3 script API sources.
- `OpenTTD-Knowledge/` = repo reference vault (road-centric).
- `app/simulation/openttd/` = existing road-freight execution stack.

---

## §1 Verdict summary

- **Full rail build surface exists in 15.3**: `ScriptRail` (@api `ai game`, `script_rail.hpp:21,23`) covers track (`BuildRailTrack` :375, `BuildRail` :425, `RemoveRail` :443), depots (`BuildRailDepot` :242), stations (`BuildRailStation` :268, `BuildNewGRFRailStation` :307), waypoints (`BuildRailWaypoint` :322), signals (`BuildSignal` :465, `RemoveSignal` :477, `GetSignalType` :452), costs/limits (`GetBuildCost` :486, `GetMaxSpeed` :498).
- **GameScripts CAN issue orders in 15.3**: `ScriptOrder` is `@api ai game` (`script_order.hpp:18`) and all order-setting methods were added to the GS API in 14.0 (`game_changelog.hpp:51-67`).
- **Vehicles: engine-only build + manual wagon assembly**: `ScriptVehicle::BuildVehicle` docs warn "wagons are not automatically attached to trains" (`script_vehicle.hpp:332-335`); consist assembly is `MoveWagon`/`MoveWagonChain` (:408, :424, VT_RAIL preconditions :403-404).
- **Signals exist but are electric-only and read-only-ish**: `BuildSignal` always emits `SIG_ELECTRIC` (`script_rail.cpp:469`); no signal-block occupancy/reservation query exists — only per-tile per-direction `GetSignalType` (`script_rail.cpp:412-430`).
- **No offline slope→track oracle**: `BuildRail` just throws `ERR_LAND_SLOPED_WRONG` (`script_rail.hpp:367`); the API provides `GetSlope` (`script_tile.hpp:303`) but nothing that maps a slope to permitted track bits — that mapping must be modelled in Python from engine tables.
- **No curve/turn-limit API**: `grep -rn -i "curve" ottd/src/script/api/*.hpp` returns nothing; train-length is only `GetLength` in 1/16-tile (`script_vehicle.hpp:554,560`) and `ERR_VEHICLE_TOO_LONG` (:69).
- **Costs are base-price only**: `ScriptRail::GetBuildCost` (`script_rail.cpp:491-503`) ignores terrain/slope/economy multipliers; faithful quoting needs in-session `ScriptTestMode` + `ScriptAccounting` (`script_testmode.hpp:20-23`, `script_accounting.hpp:16-27`) or the repo's native tested-quote pattern.
- **Hardest gaps for a Python-planned rail analog**: (1) signaling design with no occupancy readback; (2) multi-part train assembly + platform-length matching; (3) `BuildRail`'s drag semantics (`SimulateDrag`, `script_rail.cpp:293-349,365`) making route→track-piece prediction non-trivial offline; (4) station placement validation is only thin (orientation limited to 2 axes, :253) and real acceptance/rating effects stay native; (5) every mutating call requires `ScriptCompanyMode::IsValid()` (e.g. `script_rail.hpp:257`) and precondition violations abort the Squirrel callback, so the .nut refusal ladder must pre-validate everything.
- **Search-absence confirmations**: greps for `GSRail` in `app/` hit only a *forbidden-symbol* list (`app/simulation/openttd/proof/harness.py:320`) — no rail code exists yet; `curve` (above); no signal-reservation API (full 509-line read of `script_rail.hpp`).

---

## §2 API inventory

### (a) Rail track construction — `script_rail.{hpp,cpp}`

| API | header:line | purpose | notable constraints / errors |
|---|---|---|---|
| `ScriptRail::IsRailTypeAvailable` | script_rail.hpp:155 / cpp:70-76 | rail-type availability per company | requires deity or company mode (cpp:72) |
| `GetCurrentRailType`/`SetCurrentRailType` | script_rail.hpp:161,167 / cpp:78-88 | per-script rail-type state | Set silently no-ops if unavailable (cpp:83-88) |
| `GetRailTracks` | script_rail.hpp:357 / cpp:235-243 | track bits on a tile; depots have none (cpp:241) | returns RAILTRACK_INVALID if not rail tile |
| `BuildRailTrack` | script_rail.hpp:375 / cpp:245-255 | single-tile single-track build (CMD_BUILD_RAILROAD_TRACK, cpp:254) | one track only (:251, note :372-373); errors ERR_AREA_NOT_CLEAR, ERR_LAND_SLOPED_WRONG, ERR_ALREADY_BUILT (hpp:366-370) |
| `BuildRail` | script_rail.hpp:425 / cpp:351-367 | "drag" build from/tile/to (CMD_BUILD_RAILROAD_TRACK, auto-continue=true, cpp:366) | geometric pres (hpp:409-415); obstacles fail construction (hpp:422); SimulateDrag reshapes `to` (cpp:293-349,365) |
| `RemoveRail`/`RemoveRailTrack` | script_rail.hpp:443,389 / cpp:369-384,257-266 | removal | ERR_UNSUITABLE_TRACK (hpp:384,440) |
| `AreTilesConnected` | script_rail.hpp:401 / cpp:268-287 | connectivity check from/tile/to | manhattan-1 pres (hpp:397-398) |
| `IsRailTile` | script_rail.hpp:117 / cpp:34-40 | rail tile incl. stations/waypoints/crossings | excludes blocked station tiles (cpp:39) |
| `ConvertRailType` | script_rail.hpp:211 / cpp:113-121 | rectangle rail-type conversion (CMD_CONVERT_RAIL) | ERR_UNSUITABLE_TRACK (hpp:208) |
| `GetRailType` (tile) | script_rail.hpp:197 / cpp:106-111 | rail type under a tile | RAILTYPE_INVALID if no rail |
| `TrainCanRunOnRail`/`TrainHasPowerOnRail` | script_rail.hpp:179,189 / cpp:90-104 | engine-vs-track compatibility | run≠power (note hpp:176-177) |

### (b) Rail stations, waypoints, depots

| API | header:line | purpose | notable constraints / errors |
|---|---|---|---|
| `BuildRailDepot` | script_rail.hpp:242 / cpp:137-149 | CMD_BUILD_TRAIN_DEPOT (cpp:148) | tile≠front, straight line (cpp:143); ERR_FLAT_LAND_REQUIRED, ERR_AREA_NOT_CLEAR (hpp:238-239) |
| `GetRailDepotFrontTile` | script_rail.hpp:219 / cpp:123-128 | entrance tile of a depot | invalid if not depot tile |
| `BuildRailStation` | script_rail.hpp:268 / cpp:151-163 | CMD_BUILD_RAIL_STATION (cpp:162) | direction only NE_SW/NW_SE (hpp:253); platforms,length ≤255 (hpp:254-255); join via STATION_NEW/JOIN_ADJACENT/StationID (hpp:256); errors: TOO_CLOSE/TOO_MANY/TOO_MANY_IN_TOWN + ERR_BRIDGE_TOO_LOW/ERR_STATION_TOO_SPREAD_OUT (hpp:258-265) |
| `BuildNewGRFRailStation` | script_rail.hpp:307 / cpp:165-204 | callback-18 NewGRF station w/ default fallback (cpp:193-203) | same errors + cargo/industry pres (hpp:293-296) |
| `BuildRailWaypoint` | script_rail.hpp:322 / cpp:206-215 | CMD_BUILD_RAIL_WAYPOINT (cpp:214) | single tile, straight track only (hpp:313-315); waypoint-too-close errors (script_waypoint.hpp:33-36) |
| `GetRailStationDirection` | script_rail.hpp:227 / cpp:130-135 | station tile orientation | only RAILTRACK_NE_SW/NW_SE (hpp:225) |
| `RemoveRailStationTileRectangle`/`RemoveRailWaypointTileRectangle` | script_rail.hpp:348,335 / cpp:226-233,217-224 | partial removal, keep_rail | ERR_UNSUITABLE_TRACK (hpp:332,345) |
| `ScriptRailTypeList` | script_railtypelist.hpp:20-23 / cpp:17-23 | all available railtypes | deity-or-company filter (cpp:19-23) |
| `ScriptDepotList` | script_depotlist.hpp:21-26 | own depots by transport type | TRANSPORT_RAIL from script_tile.hpp:103 |
| `ScriptStation::STATION_TRAIN` | script_station.hpp:47 | train-facility flag | — |
| `ScriptStation::GetCoverageRadius`/`GetStationCoverageRadius` | script_station.hpp:201,209 | catchment radius | radius only, not acceptance |
| `ScriptStation::GetCargoWaiting*`/`GetCargoPlanned*` | script_station.hpp:78-171 | per-cargo/from/via waiting & planned flows | fuel for the Python planner |
| `ScriptStation::GetCargoRating`/`HasCargoRating` | script_station.hpp:192,181 | rating % | pre HasCargoRating |
| `ScriptBaseStation::STATION_NEW/JOIN_ADJACENT/INVALID` | script_basestation.hpp:24-26 | join constants | — |
| `ScriptBaseStation::GetLocation/GetConstructionDate/SetName` | script_basestation.hpp:73,81,63 | identity/audit | SetName exceptions ERR_NAME_IS_NOT_UNIQUE (:60) |
| `ScriptWaypoint::IsValidWaypoint/GetWaypointID/HasWaypointType` | script_waypoint.hpp:54,63,71 | waypoint identity | WAYPOINT_RAIL (:44) |
| `ScriptInfrastructure::GetRailPieceCount/GetMonthlyRailCosts` | script_infrastructure.hpp:38,64 | infra usage & maintenance costs | per company+railtype |

### (c) Buying/selling/running rail vehicles — `script_vehicle.{hpp,cpp}`, `script_engine.hpp`

| API | header:line | purpose | notable constraints / errors |
|---|---|---|---|
| `ScriptVehicle::BuildVehicle` | script_vehicle.hpp:340 / cpp:91-94 | CMD_BUILD_VEHICLE at depot (cpp:85) | engine must be buildable; ERR_VEHICLE_TOO_MANY/BUILD_DISABLED/WRONG_DEPOT (hpp:326-328); **wagons not auto-attached to trains** (hpp:332-335); test-mode quirk (hpp:336-338) |
| `BuildVehicleWithRefit` | script_vehicle.hpp:362 / cpp:96-100 | build+refit | same errors (hpp:352-354) |
| `GetBuildWithRefitCapacity` | script_vehicle.hpp:375 / cpp:102-108 | capacity quote via CMD QueryCost (cpp:107) | per single vehicle, not composed train |
| `MoveWagon`/`MoveWagonChain` | script_vehicle.hpp:408,424 | attach wagons to trains | VT_RAIL pres (:403-404,:419-420) |
| `SellVehicle`/`SellWagon`/`SellWagonChain` | script_vehicle.hpp:465,480,495 | disposal | NOT_IN_DEPOT error (:60) |
| `RefitVehicle`/`GetRefitCapacity` | script_vehicle.hpp:452,436 | refit | vehicle must be stopped in depot (:434) |
| `SendVehicleToDepot(ForServicing)` | script_vehicle.hpp:506,517 | service runs | ERR_VEHICLE_CANNOT_SEND_TO_DEPOT (:45) |
| `StartStopVehicle` | script_vehicle.hpp:529 | start/stop | ERR_VEHICLE_NO_POWER for trains (:66,526) |
| `ReverseVehicle` | script_vehicle.hpp:541 | direction flip | VT_ROAD/VT_RAIL only (:534); not always possible (note :538-539) |
| `GetLength` | script_vehicle.hpp:560 | total length in 1/16 tiles (:554) | basis for platform-length matching |
| `GetNumWagons`/`GetWagonEngineType`/`GetWagonAge` | script_vehicle.hpp:124,169,207 | consist introspection | — |
| `GetState` (VS_RUNNING…VS_CRASHED) | script_vehicle.hpp:244, 87-95 | coarse runtime state | no finer path-occupancy API |
| `GetCapacity`/`GetCargoLoad` | script_vehicle.hpp:551,570 | cargo telemetry | per cargo type |
| `GetMaximumOrderDistance` | script_vehicle.hpp:618 | order-range limit | units unspecified (script_order.hpp:602-603) |
| Error enum incl. `ERR_VEHICLE_TOO_LONG` | script_vehicle.hpp:30-69 | typed refusals | TOO_LONG :69; WRONG_DEPOT :42; NO_POWER :66 |
| `ScriptEngine::IsBuildable` | script_engine.hpp:40 | buildability gate | GS must be in company mode (game_changelog.hpp:306) |
| `GetCargoType/CanRefitCargo/CanPullCargo/GetCapacity` | script_engine.hpp:57,71,84,93 | cargo compatibility | CanPullCargo matters for consists |
| `GetMaxSpeed/GetPrice/GetPower/GetWeight/GetMaxTractiveEffort` | script_engine.hpp:115,123,150,159,168 | engine physics | **per engine** — composed-train physics is Python's job |
| `IsWagon/CanRunOnRail/HasPowerOnRail/GetRailType/GetAllRailTypes` | script_engine.hpp:194,207,218,259,268 | rail compatibility | 15.0 note: GetRailType returns only first railtype (game_changelog.hpp:40) |
| `GetMaximumOrderDistance` | script_engine.hpp:301 | order-range limit | see script_order.hpp:596 |
| `ScriptGroup::CreateGroup/MoveVehicle/SetAutoReplace/EnableWagonRemoval/EnableAutoReplaceProtection` | script_group.hpp:43,160,192,171,111 | fleet grouping, auto-replace | GS-usable since 14.0 (game_changelog.hpp:76-90) |

### (d) Orders — `script_order.hpp` (available to GS since 14.0, game_changelog.hpp:51-67)

| API | header:line | purpose | notable constraints / errors |
|---|---|---|---|
| `AppendOrder`/`InsertOrder` | script_order.hpp:445,475 | goto station/depot/waypoint order | destination is a **tile**; ERR_ORDER_TOO_MANY :32, ERR_ORDER_TOO_FAR_AWAY_FROM_PREVIOUS_DESTINATION :35 (exceptions :440-442) |
| `ScriptOrderFlags` | script_order.hpp:44-85 | OF_NONE=0, OF_FULL_LOAD=2<<5 (=64) :61, OF_FULL_LOAD_ANY :63, OF_NO_LOAD=1<<7 (=128) :65, OF_SERVICE_IF_NEEDED :68, OF_STOP_IN_DEPOT :70, OF_GOTO_NEAREST_DEPOT :72 | repo pins match: OF_NONE_V2=0, OF_FULL_LOAD_FORBIDDEN_V2=64, OF_NO_LOAD_V2=128 (corridor_freight_v2.py:175-177) |
| `SetOrderFlags` | script_order.hpp:521 | flag edit | OF_GOTO_NEAREST_DEPOT invariance pre (:516) |
| `SetStopLocation`/`GetStopLocation` | script_order.hpp:417,336 | train stop position in station | VT_RAIL pres (:411,332); StopLocation enum :136-141 |
| `SetOrderRefit` | script_order.hpp:430 | per-order refit incl. CT_AUTO_REFIT | CT_AUTO_REFIT only on goto-station orders (:425) |
| `RemoveOrder/MoveOrder/SkipToOrder/CopyOrders/ShareOrders/UnshareOrders` | script_order.hpp:501,539,550,565,579,589 | order list management | — |
| Conditional orders | script_order.hpp:90-121,354-403 | OC_* conditions, CF_* comparators, setters | value range 0..2047 (:399) |
| `GetOrderDistance` | script_order.hpp:606 | vehicle-type-specific distance | **units unspecified, must calibrate natively** (:602-603) |
| Depot order flags | script_order.hpp:68-72 | service-if-needed / stop-in-depot / nearest-depot | — |

### (e) Signals — `script_rail.{hpp,cpp}`

| API | header:line | purpose | notable constraints / errors |
|---|---|---|---|
| `SignalType` enum | script_rail.hpp:68-84 | NORMAL/ENTRY/EXIT/COMBO/PBS/PBS_ONEWAY + TWOWAY masks (:74-77) | full PBS palette available |
| `BuildSignal` | script_rail.hpp:465 / cpp:442-470 | CMD_BUILD_SINGLE_SIGNAL | always `SIG_ELECTRIC` (cpp:469); plain-rail tiles only, no station/waypoint tiles (hpp:460, cpp:446); twoway vs oneway handled via `signal_cycles` (cpp:462-466) |
| `GetSignalType` | script_rail.hpp:452 / cpp:412-430 | signal type facing `front` | per tile+direction only; **no block occupancy/reservation query anywhere** (absent from full 509-line header) |
| `RemoveSignal` | script_rail.hpp:477 / cpp:472-489 | remove | pre: GetSignalType != NONE (hpp:472) |

### (f) Terrain, bridges/tunnels, cost quoting, error taxonomy

| API | header:line | purpose | notable constraints / errors |
|---|---|---|---|
| `ScriptTile::GetSlope/GetMinHeight/GetMaxHeight` | script_tile.hpp:303,323,332 | slope/height reads for placement planning | steep/halftile flags :216,226 |
| `ScriptTile::IsBuildable(IsBuildableRectangle)` | script_tile.hpp:151,164 | vacancy check | — |
| `ScriptTile::GetCargoAcceptance/GetCargoProduction` | script_tile.hpp:387,404 | tile-based acceptance/production probes | acceptance depends on station coverage, not settable here |
| `ScriptTile::RaiseTile/LowerTile` | script_tile.hpp:437,454 | CMD_TERRAFORM_LAND | repo treats LevelTiles as prohibited (OpenTTD-Knowledge/99-Source-Documents/EVIDENCE_INDEX.md:230) |
| `ScriptMap::IsValidTile/GetTileX/Y/DistanceManhattan` | script_map.hpp:29,59,68,90 | geometry | BuildRail pres depend on these (script_rail.hpp:409-415) |
| `ScriptBridge::BuildBridge(VT_RAIL,…)` | script_bridge.hpp:156 | rail bridges over water | GetMaxSpeed :86, GetPrice :96, GetMaxLength/MinLength :104,112; ERR_BRIDGE_TOO_LOW (script_error.hpp:180; also station/waypoint contexts script_rail.hpp:264,318) |
| `ScriptTunnel::BuildTunnel(VT_RAIL,…)` | script_tunnel.hpp:102 | rail tunnels | GetOtherTunnelEnd :64 |
| `ScriptTestMode` | script_testmode.hpp:20-25 | commands are cost-checked, not executed | the quoting primitive |
| `ScriptAccounting::GetCosts/ResetCosts` | script_accounting.hpp:51,58 | measured cost of a command block | works in test & exec mode (:16-17) |
| `ScriptCompanyMode` | script_companymode.hpp:30,58,66 | GS-only company scope (`@api game`) | company funds bind the action (:20-27) |
| `ScriptError::GetErrorCategory/GetLastError/GetLastErrorString` | script_error.hpp:188,194,200 | typed-refusal mapping source | ERR_CAT_RAIL :108, ERR_CAT_ORDER :110, ERR_CAT_WAYPOINT :112; ERR_LAND_SLOPED_WRONG :165, ERR_FLAT_LAND_REQUIRED :162, ERR_AREA_NOT_CLEAR :153, ERR_ALREADY_BUILT :150, ERR_OWNED_BY_ANOTHER_COMPANY :156 |

---

## §3 Gaps & risks for the offline (no-native-launch) rail build

1. **Signaling without occupancy readback** — `BuildSignal` can place PBS/block signals (`script_rail.hpp:465`; SIGNALTYPE_PBS :74), but the only signal query is per-tile direction `GetSignalType` (`script_rail.cpp:412-430`); no API exposes path reservation or block occupancy. Deadlock-freedom must be proven by design + observed runtime state (`ScriptVehicle::GetState`, script_vehicle.hpp:244,87-95) or accepted as an offline-planned risk. (Also: signals are always electric, `script_rail.cpp:469`.)
2. **Multi-part train assembly** — `BuildVehicle` alone yields an engine; wagons need `MoveWagon`/`MoveWagonChain` (`script_vehicle.hpp:332-335,408,424`), and no API composes per-engine physics (`GetPower/GetWeight/GetMaxTractiveEffort`, script_engine.hpp:150,159,168) into a validated consist. Train-length limit is only `ERR_VEHICLE_TOO_LONG` (script_vehicle.hpp:69) + `GetLength` 1/16-tile (script_vehicle.hpp:554,560); platform-length matching is Python arithmetic.
3. **Slope handling is trial-and-error at the API level** — `BuildRail`/`BuildRailTrack` surface `ERR_LAND_SLOPED_WRONG`/`ERR_AREA_NOT_CLEAR`/`ERR_ALREADY_BUILT` (script_rail.hpp:366-370); there is no slope→track-bits oracle (`grep -i curve` over api headers: no match; full read of script_rail.hpp). The repo's road stack dodges this with bounded flat corridors + explicit budgets (OpenTTD-Knowledge/00-Project/Scope and Non-Goals.md:50-52); post-D3 the demo corridor was proven flat (`OpenTTD-Knowledge/99-Source-Documents/EVIDENCE_INDEX.md:239`), so a rail analog can start flat-then-extend.
4. **Cost quoting fidelity** — `GetBuildCost` is base price only (script_rail.cpp:491-503); real command cost (terrain, funds gate) differs. The road stack already uses a tested-quote discipline (`corridor_freight_v2_native.py` docstring "the tested quote" — corridor_freight_v2.py F-series pins, corridor_freight_v2.py:20-27); rail must reuse ScriptTestMode/ScriptAccounting (script_testmode.hpp:20-23; script_accounting.hpp:51) plus CMD QueryCost echoes like `GetBuildWithRefitCapacity` (script_vehicle.cpp:102-108). Test/exec divergence is a known repo hazard class (LevelTiles prohibition, OpenTTD-Knowledge/99-Source-Documents/EVIDENCE_INDEX.md:230).
5. **Station placement validation is thin** — only 2 orientations (script_rail.hpp:253), ≤255 platforms/length (hpp:254-255), join semantics via constants (script_basestation.hpp:24-25), and place-time errors TOO_CLOSE/TOO_MANY/TOO_MANY_IN_TOWN/BRIDGE_TOO_LOW/TOO_SPREAD_OUT (script_rail.hpp:258-265). Catchment radius is queryable (script_station.hpp:201,209) and tile acceptance is probeable (script_tile.hpp:387), but rating-driven acceptance evolution is native-only — the repo already treats catchment/acceptance as native re-checks (OpenTTD-Knowledge/00-Project/Scope and Non-Goals.md:58; OpenTTD-Knowledge/01-Architecture/OpenTTD Integration.md:89).
6. **Order-distance units are unspecified** — `GetOrderDistance`/`GetMaximumOrderDistance` (script_order.hpp:606; script_engine.hpp:301; script_vehicle.hpp:618) cannot be compared with map distances offline (script_order.hpp:602-603); `ERR_ORDER_TOO_FAR_AWAY_FROM_PREVIOUS_DESTINATION` (script_order.hpp:35) needs native calibration.
7. **Precondition aborts, not refusals** — failing any `@pre` aborts the Squirrel callback rather than returning false, so the .nut package must pre-validate every argument (the d5 packages' refusal ladders do exactly this: `app/simulation/openttd/d5_freight_v2_package/main.nut:51-56`, :347-368, :636).
8. **Knowledge vault has no rail reference** — greps for rail/signals/train-length/curve across `OpenTTD-Knowledge/**.md` return only scope/evidence mentions (e.g. "Rail/air/water delivery: outside the demonstrated native MVP", OpenTTD-Knowledge/00-Project/Scope and Non-Goals.md:58); the only API catalog is road-centric (OpenTTD-Knowledge/01-Architecture/OpenTTD Integration.md:75-90). Any rail engine-truth claim must come from `ottd/` sources, not the vault's wiki-traditions — currently none are recorded there.

---

## §4 Mirror-points — repo pattern families a rail analog must follow

All paths under `/home/fed/codes/softdev2/app/simulation/openttd/`.

1. **Wire-contract / versioned protocol family** (typed requests/responses, additive protocols): `corridor_freight.py:1` (protocol 5), `corridor_accept_survey.py:1` (6), `corridor_terrain_survey.py:1` (7), `corridor_freight_v2.py:1-3` (8, new alongside frozen 5; F-4 order-flag pins :24-27, constants :173-177), `corridor_box_census.py:1` (9), `corridor_depot_mutation.py:1` (10 mutation), `corridor_cargoflow.py:1` (10 observation probe), `corridor_cargoflow2.py:1` (11). A rail freight contract would be a new additive protocol with its own pinned flag/geometry tables.
2. **GameScript package pattern** (staged `info.nut` + `main.nut`, pin tables + refusal ladders, thin GSCompanyMode execution): staging via `gamescript_bridge.py:1-8` (`stage_bridge`, "version-15 no-mutation … staging never launches a game"); package example `d5_freight_v2_package/main.nut` — baked staged pins :152, route-vs-witness binding :162, `ENGINE_PIN = 123` :176, fail-closed engine admission refusal ladder :51-56, pinned-engine dispatch gate :347-368, refusal-before-observation rule :636; a mutation package must enumerate its only-allowed commands up front (`d5_extension_package/main.nut:3-5`: "the only native mutation commands are GSRoad.BuildRoadFull, GSRoad.BuildRoad and GSRoad.BuildRoadStation … executed at most once"); observe-only bridges keep a frozen-API/forbidden-symbol gate (`proof/harness.py:314-330`, where `GSRail` appears only as forbidden). The rail analog adds a NEW package composition (e.g. `GSRail.BuildRailTrack/BuildRailDepot/BuildRailStation/BuildSignal` + `GSVehicle.BuildVehicle`/`GSOrder.*`), never edits frozen ones — the road packages already prove the command-catalog discipline.
3. **Proof / staging pipeline** (`prepare|preflight|run|verify`): `proof/corridor_freight_v2_native.py:2289` (argparse verbs), `prepare_candidate` :1024, `preflight` :1224, `verify_freight_attempt` :2026, plus the one-shot-claim/no-launch staging discipline in its docstring (:1-30). A rail candidate follows the same prepare→preflight→run→verify lifecycle with a `PENDING_AUTHORIZATION` staged claim and zero launches in preparation.

---

## §5 Open questions for the operator

1. Which signaling scheme is the rail plan targeting — PBS (`SIGNALTYPE_PBS`, script_rail.hpp:74) vs plain block — given there is no occupancy/reservation readback (script_rail.cpp:412-430)?
2. Must the rail corridor reuse the post-D3 leveled 24-tile corridor (OpenTTD-Knowledge/99-Source-Documents/EVIDENCE_INDEX.md:239) or extend to new terrain, which would re-open the slope/terrain-verification question (script_rail.hpp:366-370)?
3. Is consist policy fixed-engine+wagons assembled via MoveWagon (script_vehicle.hpp:408) or group-based auto-replace/wagon-removal (script_group.hpp:192,171)?
4. Should rail stations always be STATION_NEW or STATION_JOIN_ADJACENT (script_basestation.hpp:24-25), and does the offline planner need GetCoverageRadius (script_station.hpp:201) contracts pinned like the road census?
5. Should order/vehicle quantities be quoted in-session via ScriptTestMode+ScriptAccounting (script_testmode.hpp:20-23; script_accounting.hpp:51) like the road "tested quote", and can `GetOrderDistance` units (script_order.hpp:602-603) be calibrated without a native run?
