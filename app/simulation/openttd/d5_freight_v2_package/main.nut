/* Separate bounded native corridor-freight v2 handler (protocol 8). Additive:
 * no existing frozen package is modified or imported; the frozen protocol-5
 * package (d5_freight_package) keeps its bytes and its own schedule. The only
 * native mutation commands are GSVehicle.BuildVehicle (once), GSOrder
 * .AppendOrder (twice: pickup stop tile with OF_NONE, delivery stop tile with
 * OF_NO_LOAD — N1/N2/N3 of the v2 resolution: the 15.x append takes the stop
 * TILE, OF_FULL_LOAD is never issued, and AreOrderFlagsValid is the
 * two-argument destination form) and GSVehicle.StartStopVehicle (start once,
 * stop once at finish) in company mode, each executed at most once against
 * the fixed thirty-exchange schedule; demolition, terraforming, road,
 * station, depot, refit, selling and second-vehicle commands are absent by
 * construction. GSCargoMonitor arming, consumption and re-arming are
 * observation state, not commands.
 *
 * The v2 schedule is the cycle-looped block the wire contract pins: ten fixed
 * exchanges (site, engine, purchase, vread, two order appends, order
 * inventory, monitor arming, start, second vread), six full load/transit/
 * deliver cycles, then finance corroboration and finish — thirty exchanges,
 * the §4 arithmetic 10 + 2 + 3*6 <= 32 resolved at staging. Per cycle the
 * departure snapshot gates 0 < load <= capacity (partial loads legal, full
 * load never demanded), the arrival gate reads that same load at the pinned
 * delivery bay, and the delivery window reconciles both industry monitor
 * deltas against the departure snapshot exactly, then consumes BOTH monitors
 * with keep=false behind that gate and re-arms them by observing zero residue
 * with keep=true. A departure with zero cargo is a typed ZERO_DEPARTED (F-11):
 * it is never a success, never WINDOW_EXHAUSTED, and the schedule continues —
 * the cycle is simply recorded as evidence with an empty load, so a zero
 * cycle arrives at the bay, reads both monitors zero, consumes zero and
 * re-arms zero (exactly what the honest empty run does).
 *
 * The handler re-binds the A1 close-out geometry: pickup stop 45748 (front
 * 45747), delivery bay 50862 (front 50863), depot 45487 (front 45743), and
 * the ordered 29-tile vehicle route re-checked connected on the company's
 * own road; cargo 1. The industry ids are NEVER pinned (F-3): the site
 * exchange discovers exactly one cargo-producing industry inside the pickup
 * stop's measured stop-radius box and exactly one cargo-accepting industry
 * inside the delivery bay's box (the unique-cargo-industry policy), latches
 * both ids and refuses to proceed on any other count. The directed depot
 * edge (F-12) is probed with GSRoad.AreRoadTilesConnected in both directions
 * before the site exchange may report READY.
 *
 * The engine admission is the fail-closed pinned-engine policy (F-10): every
 * non-site request ships ENGINE_PIN (the provisional offline census pin, 123)
 * and the handler admits exactly that identity — no lowest-compatible
 * fallback exists in this machinery. A pulse that names a different engine,
 * or a pin that is not a buildable compatible road truck for cargo 1, is
 * refused UNAVAILABLE_ENGINE / ENGINE_PIN_MISMATCH before any purchase
 * mutation. The engine reply echoes the bounded compatible-universe census
 * (buildable road engine ids, descending, capped at 12) beside the pinned
 * engine's own price, capacity, cargo and speed.
 *
 * Every exchange is one fixed stage of the plan: request id AND op must
 * equal the planned exchange of the current stage, so any replay or reorder
 * becomes OUT_OF_ORDER. Watch windows poll one script tick per sample with
 * clock sanity (regression/stall fail-closed, pause checked first), and
 * window/day caps bounded by the request echoes and the module constants
 * (2048 ticks; the per-cycle economy-day lease comes in the request echo and
 * is bounded by the 60-day attempt budget) — caps, never promises. Every
 * success, typed-zero and inconclusive reply carries the quarter income so
 * each exchange span attributes its funds delta; refusals carry no
 * observation set at all. A refusal or an inconclusive window halts the
 * schedule prefix-preservingly: later exchanges answer OUT_OF_ORDER, no op
 * is ever reordered or retried, and no failed command is ever reported as
 * leaving the world unchanged.
 *
 * Native API pins carried from the proven 15.3 records (all opened natively
 * before): GSVehicle.{IsPrimaryVehicle,BuildVehicle,StartStopVehicle,
 * GetEngineType,GetOwner,GetLocation,GetCapacity,IsInDepot,GetCurrentSpeed,
 * GetState,GetCargoLoad}, GSEngine enumeration with GetCargoType/GetCapacity/
 * GetPrice/GetMaxSpeed/Syntax for the bounded compatible universe, GSOrder.
 * {AppendOrder,AreOrderFlagsValid(two-arg destination),GetOrderCount,
 * GetOrderDestination,GetOrderFlags,IsGotoStationOrder}, GSIndustry.
 * {IsValidIndustry,GetIndustryID,GetLastMonthProduction,IsCargoAccepted
 * (CAS_ACCEPTED)}, GSCompany.{GetBankBalance,GetQuarterlyIncome,
 * GetQuarterlyCargoDelivered} with GSCompany.CURRENT_QUARTER, GSCargoMonitor
 * .GetIndustry{Pickup,Delivery}Amount(company,cargo,industry,keep),
 * GSRoad.AreRoadTilesConnected for the directed edge and per-pair witness
 * re-check, GSGame.IsPaused, GSDate.GetCurrentDate. GSVehicle.BuildVehicle
 * returns the new VehicleID in real mode (0 in test mode on success, any
 * other value on failure, exactly like the proven lifecycle kernel's
 * purchase quote).
 *
 * The delivery acceptance fact is read through the proven catchment
 * predicate GSTile.GetCargoAcceptance(delivery_tile, cargo, 1, 1, radius)
 * with the truck-stop coverage radius — 0..8 eighths; the v2 admission binds
 * the pinned census bound 8/8 exactly (the A0 survey's delivery-bay
 * observation of record), so a lower measured value is an INVALID_SITE
 * refusal, not a downgrade. The vehicle readback's cargo slot is the
 * admitted corridor cargo: no refit exists in this machinery, and a vehicle
 * carrying any other cargo reads capacity 0 there and is refused on that
 * capacity. */
class D5FreightV2Proof extends GSController {
    /* Schedule state: `stage` is the index of the one planned exchange that
     * may run next; `halted` stops every later exchange after any success
     * frame failed to produce its exact planned status (a typed ZERO_DEPARTED
     * load reply is the one continuing non-success: it advances the stage as
     * its cycle's honest empty-run evidence without ever becoming a success
     * or re-arming anything beyond what the deliver window owns). */
    stage = 0
    halted = false
    /* One-shot dispatcher budget accounting (unique ids, 32-request cap). */
    requests = 0
    used = null
    /* Latched prelaunch plan digest: the first accepted exchange fixes the
     * attempt's plan identity; every later exchange must match it. */
    plan_id = null
    /* Latched route digest supplied by the site exchange. Squirrel has no
     * SHA-256, so this is an opaque consistency tag, not independent
     * authentication: Python derives it from FreightPlanV2 and verifies
     * every request before dispatch. The GameScript's guarantee is narrower
     * but real: once the site route is latched, every later exchange must
     * present the same digest, so a stale route is refused before purchase. */
    route_digest = null
    /* Latched construction-witness digest (site request only): the opaque
     * tag binding the site route to the physical 31-tile extension witness
     * it was derived from. Echoed on the site reply; never on later ops. */
    witness_digest = null

    /* Latched execution geometry. The site request carries the derived
     * vehicle route; these fields are initialized from the A1 close-out
     * defaults only so the class is constructible before the site exchange,
     * and are replaced atomically when a valid route is latched. */
    pickup = -1
    pickup_front = -1
    delivery = -1
    delivery_front = -1
    depot_tile = -1
    depot_front = -1
    route = null

    constructor() {
        this.pickup = PICKUP
        this.pickup_front = PICKUP_FRONT
        this.delivery = DELIVERY
        this.delivery_front = DELIVERY_FRONT
        this.depot_tile = DEPOT_TILE
        this.depot_front = DEPOT_FRONT
        this.route = []
        foreach (tile in BAKED_ROUTE) this.route.append(tile)
    }

    /* Baked staged pins of the A1 close-out world (the consumed
     * D5-CORRIDOR-EXTENSION-3 after-save): the defaults used when no site
     * route has been latched, and the demonstrated geometry the derived
     * route round-trips in staging. */
    PICKUP = 45748
    PICKUP_FRONT = 45747
    DELIVERY = 50862
    DELIVERY_FRONT = 50863
    DEPOT_TILE = 45487
    DEPOT_FRONT = 45743
    /* The ordered vehicle route (29 tiles, 28 pairs): the pinned 31-tile
     * construction witness minus the stale D4 bay tile 50351 and the
     * backtracked repeat of its front tile 50095. The vehicle drive is
     * validated against the latched ordered list; the witness stays a
     * Python-side digest on the wire, never a.nut route here. */
    BAKED_ROUTE = [
        45748, 45747, 45746, 45745, 45744, 45743, 45999, 46255, 46511, 46767,
        47023, 47279, 47535, 47791, 48047, 48303, 48559, 48815, 49071, 49327,
        49583, 49839, 50095, 50096, 50352, 50608, 50864, 50863, 50862
    ]
    MAX_ROUTE_TILES = 32
    /* F-10: the provisional offline engine pin of record (the attempt19
     * census identity). Every non-site request ships it; the handler admits
     * exactly this id and never substitutes a lowest-compatible fallback. */
    ENGINE_PIN = 123
    /* Fixed corridor freight idents (the plan only drives this geometry). */
    FREIGHT_COMPANY = 0
    FREIGHT_CARGO = 1
    /* Real 15.x order-flag values (N2). OF_FULL_LOAD is DOCUMENTED as
     * forbidden: v2 orders never carry it, and neither flag constant here
     * feeds an append. */
    OF_NONE = 0
    OF_FULL_LOAD_FORBIDDEN = 64
    OF_NO_LOAD = 128
    /* Per-watch window caps: the tick cap is the module bound; the day cap
     * is the 60-economy-day attempt budget the request echo is bounded by
     * (caps, never promises). */
    MAX_TICKS = 2048
    MAX_DAYS = 60
    /* The bounded compatible-universe echo (F-10): at most this many
     * buildable road engine ids join the engine reply, descending. */
    FLEET_ECHO = 12
    /* Industry discovery bounds (F-3): the stop-radius boxes scan at most
     * this many distinct industry ids before refusing the discovery. */

    /* The fixed thirty-exchange schedule: [request_id, op, success status],
     * the same order the Python contract's FREIGHT_EXCHANGE_IDS_V2 pins
     * (ten fixed rows, six cycle blocks, two tail rows). */
    planned = [
        ["site-00", "site", "READY"],
        ["engine-00", "engine", "READY"],
        ["purchase-00", "purchase", "BUILT"],
        ["vread-00", "vread", "READ"],
        ["order-00", "order", "ORDERED"],
        ["order-01", "order", "ORDERED"],
        ["order-read-00", "order-read", "ORDER_SET_VERIFIED"],
        ["monitor-00", "monitor", "ARMED"],
        ["start-00", "start", "STARTED"],
        ["vread-01", "vread", "READ"],
        ["load-00", "load-watch", "LOADED"],
        ["transit-00", "transit-watch", "AT_DELIVERY"],
        ["deliver-00", "deliver-watch", "DELIVERED"],
        ["load-01", "load-watch", "LOADED"],
        ["transit-01", "transit-watch", "AT_DELIVERY"],
        ["deliver-01", "deliver-watch", "DELIVERED"],
        ["load-02", "load-watch", "LOADED"],
        ["transit-02", "transit-watch", "AT_DELIVERY"],
        ["deliver-02", "deliver-watch", "DELIVERED"],
        ["load-03", "load-watch", "LOADED"],
        ["transit-03", "transit-watch", "AT_DELIVERY"],
        ["deliver-03", "deliver-watch", "DELIVERED"],
        ["load-04", "load-watch", "LOADED"],
        ["transit-04", "transit-watch", "AT_DELIVERY"],
        ["deliver-04", "deliver-watch", "DELIVERED"],
        ["load-05", "load-watch", "LOADED"],
        ["transit-05", "transit-watch", "AT_DELIVERY"],
        ["deliver-05", "deliver-watch", "DELIVERED"],
        ["finance-00", "finance", "FINANCE_VERIFIED"],
        ["finish-00", "finish", "PHASE_STOPPED"]
    ]
    /* 30 planned exchanges, plus dispatcher slack only through unique ids:
     * request 33 is the first one the dispatcher drops. */
    max_requests = 32

    /* Latched admission facts (one attempt: one site, one engine, one
     * vehicle). The industry ids are the natively discovered unique
     * cargo-producer (pickup box) and cargo-acceptor (delivery box) — never
     * pinned, latched at the site exchange only. */
    site_sid0 = -1
    site_sid1 = -1
    site_waiting = -1
    site_production = -1
    pickup_industry = -1
    delivery_industry = -1
    engine_id = -1
    engine_capacity = -1
    engine_quote = 0
    vehicle_id = -1
    monitor_armed = false
    armed_income = 0
    armed_delivered = 0
    observed_load = 0

    function PlannedIndex(q) {
        /* The planned exchange carrying BOTH the request id and its op. */
        for (local i = 0; i < planned.len(); i++)
            if (planned[i][0] == q.request_id && planned[i][1] == q.op) return i
        return -1
    }

    function OpAllowed(op) {
        return op == "site" || op == "engine" || op == "purchase" ||
            op == "vread" || op == "order" || op == "order-read" ||
            op == "monitor" || op == "start" || op == "load-watch" ||
            op == "transit-watch" || op == "deliver-watch" ||
            op == "finance" || op == "finish"
    }

    function Hex64(s) {
        if (s.len() != 64) return false
        for (local i = 0; i < 64; i++) {
            local c = s[i]
            if (!((c >= 48 && c <= 57) || (c >= 97 && c <= 102))) return false
        }
        return true
    }

    function IdShape(s) {
        for (local i = 0; i < s.len(); i++) {
            local c = s[i]
            if (!(c == 45 || (c >= 48 && c <= 57) || (c >= 97 && c <= 122)))
                return false
        }
        return true
    }

    function Adjacent(a, b) {
        local wx = GSMap.GetMapSizeX()
        local ax = a % wx
        local ay = a / wx
        local bx = b % wx
        local by = b / wx
        return (ax == bx && (ay == by + 1 || ay == by - 1)) ||
            (ay == by && (ax == bx + 1 || ax == bx - 1))
    }

    /* Validate the derived vehicle route before latching any of it. The
     * same invariants the Python wire contract checks: 3..32 unique,
     * in-bounds, cardinally adjacent tiles, pinned endpoints and fronts,
     * and exactly the pinned depot front joined to the depot. */
    function RouteOk(route, pickup, delivery, depot) {
        if (typeof route != "array" || route.len() < 3 ||
            route.len() > MAX_ROUTE_TILES) return false
        if (route[0] != this.PICKUP || route[1] != this.PICKUP_FRONT)
            return false
        if (route[route.len() - 1] != this.DELIVERY ||
            route[route.len() - 2] != this.DELIVERY_FRONT) return false
        local wx = GSMap.GetMapSizeX()
        local seen = {}
        for (local i = 0; i < route.len(); i++) {
            local tile = route[i]
            if (typeof tile != "integer" || tile < 0 || tile > 65535)
                return false
            if (!GSMap.IsValidTile(tile) || GSMap.GetTileX(tile) != tile % wx ||
                GSMap.GetTileY(tile) != tile / wx) return false
            if (tile in seen) return false
            seen[tile] <- true
            if (i > 0 && !Adjacent(route[i - 1], tile)) return false
        }
        if (depot in seen) return false
        local fronts = 0
        for (local i = 1; i + 1 < route.len(); i++)
            if (Adjacent(depot, route[i])) {
                fronts++
                if (route[i] != this.DEPOT_FRONT) return false
            }
        return fronts == 1
    }

    /* Latch the validated route and its derived fronts atomically. */
    function LatchRoute(q) {
        this.pickup = q.pickup
        this.pickup_front = q.route[1]
        this.delivery = q.delivery
        this.delivery_front = q.route[q.route.len() - 2]
        this.depot_tile = q.depot
        this.depot_front = this.DEPOT_FRONT
        this.route = []
        foreach (tile in q.route) this.route.append(tile)
        this.route_digest = q.route_digest
        this.witness_digest = q.witness_digest
    }

    /* Per-op request echo coherence, mirroring the Python validator's
     * quiet/pitched rules exactly; any incoherence is a malformed request
     * the dispatcher silently drops. Every non-site op ships the pinned
     * engine identity (F-10); the site request ships none. */
    function EchoOk(q) {
        if (typeof q.engine != "integer" || q.engine < -1 || q.engine > 65535)
            return false
        if (typeof q.vehicle != "integer" || q.vehicle < -1 || q.vehicle > 65535)
            return false
        if (typeof q.expected_cost != "integer" || q.expected_cost < 0 ||
            q.expected_cost > 2147483647) return false
        if (typeof q.order_index != "integer" || q.order_index < -1 ||
            q.order_index > 1) return false
        if (typeof q.watch_ticks != "integer" || q.watch_ticks < -1 ||
            q.watch_ticks > MAX_TICKS) return false
        if (typeof q.watch_days != "integer" || q.watch_days < -1 ||
            q.watch_days > MAX_DAYS) return false
        local quiet = q.expected_cost == 0 && q.order_index == -1 &&
            q.watch_ticks == -1 && q.watch_days == -1
        if (q.op == "site")
            return q.engine == -1 && q.vehicle == -1 && quiet
        /* Every other op ships the pinned engine id — anything else is a
         * request the Python contract could never have built. */
        if (q.engine != this.ENGINE_PIN) return false
        if (q.op == "engine")
            return q.vehicle == -1 && quiet
        if (q.op == "purchase")
            return q.vehicle == -1 &&
                q.order_index == -1 && q.watch_ticks == -1 &&
                q.watch_days == -1 && q.expected_cost > 0 &&
                q.expected_cost <= q.max_cost
        if (q.op == "vread" || q.op == "order-read" || q.op == "monitor" ||
            q.op == "start" || q.op == "finance" || q.op == "finish")
            return q.vehicle >= 0 && quiet
        if (q.op == "order")
            return q.vehicle >= 0 &&
                (q.order_index == 0 || q.order_index == 1) &&
                q.expected_cost == 0 && q.watch_ticks == -1 &&
                q.watch_days == -1
        if (q.op == "load-watch")
            return q.vehicle >= 0 && q.order_index == -1 &&
                q.expected_cost == 0 &&
                q.watch_ticks >= 1 && q.watch_days >= 1
        /* transit-watch / deliver-watch */
        return q.vehicle >= 0 && q.order_index == -1 && q.expected_cost == 0 &&
            q.watch_ticks >= 1 && q.watch_days == -1
    }

    function ObserveStop(tile, front, company) {
        local wx = GSMap.GetMapSizeX()
        if (!GSMap.IsValidTile(tile) || GSMap.GetTileX(tile) != tile % wx ||
            GSMap.GetTileY(tile) != tile / wx) throw "D5_NATIVE_FACT"
        if (!GSMap.IsValidTile(front) || GSMap.GetTileX(front) != front % wx ||
            GSMap.GetTileY(front) != front / wx) throw "D5_NATIVE_FACT"
        local stop_tile = GSRoad.IsRoadStationTile(tile)
        local drive_through = stop_tile && GSRoad.IsDriveThroughRoadStationTile(tile)
        local sid = stop_tile ? GSStation.GetStationID(tile) : -1
        local truck = stop_tile && !drive_through && GSStation.IsValidStation(sid) &&
            GSStation.HasStationType(sid, GSStation.STATION_TRUCK_STOP) &&
            !GSStation.HasStationType(sid, GSStation.STATION_BUS_STOP)
        local linked = stop_tile && GSStation.IsValidStation(sid) &&
            !drive_through && GSRoad.GetRoadStationFrontTile(tile) == front
        return {
            stop = stop_tile,
            truck = truck,
            sid = sid,
            linked = linked,
            owner = GSTile.GetOwner(tile),
            front_owner = GSTile.GetOwner(front),
            funds = GSCompany.GetBankBalance(company)
        }
    }

    function ObserveDepot(company) {
        local wx = GSMap.GetMapSizeX()
        if (!GSMap.IsValidTile(this.depot_tile) ||
            GSMap.GetTileX(this.depot_tile) != this.depot_tile % wx ||
            GSMap.GetTileY(this.depot_tile) != this.depot_tile / wx) throw "D5_NATIVE_FACT"
        local depot = GSRoad.IsRoadDepotTile(this.depot_tile)
        local front_id = depot ? GSRoad.GetRoadDepotFrontTile(this.depot_tile) : -1
        /* F-12: the directed depot-entry probe. Ownership and the front tile
         * alone never prove the vehicle can enter the depot; the entry bit
         * must read connected front-to-depot AND depot-to-front. */
        local edge = false
        if (front_id == this.depot_front && GSTile.GetOwner(this.depot_tile) == company &&
            GSTile.GetOwner(this.depot_front) == company &&
            GSRoad.IsRoadTile(this.depot_front)) {
            edge = GSRoad.AreRoadTilesConnected(this.depot_front, this.depot_tile) &&
                GSRoad.AreRoadTilesConnected(this.depot_tile, this.depot_front)
        }
        return {
            depot = depot,
            front_id = front_id,
            owner = depot ? GSTile.GetOwner(this.depot_tile) : GSCompany.COMPANY_INVALID,
            linked = depot && front_id == this.depot_front &&
                GSTile.GetOwner(this.depot_tile) == company &&
                GSTile.GetOwner(this.depot_front) == company &&
                GSRoad.IsRoadTile(this.depot_front),
            edge = edge
        }
    }

    /* Vehicle-route re-check: every adjacent pair along the ordered route
     * must be joined by this company's road. Pure observation; the stops
     * attach through their fronts, which lie on the route itself. */
    function Witness(company) {
        local pairs_ok = 0
        local pair_total = this.route.len() - 1
        local wx = GSMap.GetMapSizeX()
        for (local i = 1; i < this.route.len(); i++) {
            local a = this.route[i - 1]
            local b = this.route[i]
            if (!GSMap.IsValidTile(a) || GSMap.GetTileX(a) != a % wx ||
                GSMap.GetTileY(a) != a / wx) throw "D5_NATIVE_FACT"
            if (!GSMap.IsValidTile(b) || GSMap.GetTileX(b) != b % wx ||
                GSMap.GetTileY(b) != b / wx) throw "D5_NATIVE_FACT"
            local joined = GSRoad.AreRoadTilesConnected(a, b) &&
                GSRoad.AreRoadTilesConnected(b, a) &&
                GSTile.GetOwner(a) == company && GSTile.GetOwner(b) == company
            if (joined) pairs_ok++
        }
        return {pairs_ok = pairs_ok, pair_total = pair_total}
    }

    /* The live vehicle position inside the ordered route, or -1 when it
     * stands anywhere else. */
    function RouteIndex(tile) {
        for (local i = 0; i < this.route.len(); i++)
            if (this.route[i] == tile) return i
        return -1
    }

    /* F-3 industry discovery (bounded): the distinct industry ids observed
     * inside the stop-radius box around one stop tile, filtered by the stop's
     * unique-cargo role. The producer side reads last-month production of the
     * corridor cargo; the acceptor side reads the native IsCargoAccepted
     * status (CAS_ACCEPTED). Small bounded scan; no list race, no invention —
     * the ids are read from the live ground. */
    function DiscoveryBoxes(q, stop, acceptor) {
        local radius = GSStation.GetCoverageRadius(GSStation.STATION_TRUCK_STOP)
        if (radius < 1 || radius > 8) throw "D5_NATIVE_FACT"
        local wx = GSMap.GetMapSizeX()
        local ty = stop / wx
        local tx = stop % wx
        local ids = {}
        local order = []
        for (local dy = -radius; dy <= radius; dy++) {
            for (local dx = -radius; dx <= radius; dx++) {
                if (ty + dy < 0 || ty + dy >= GSMap.GetMapSizeY() ||
                    tx + dx < 0 || tx + dx >= wx) continue
                local tile = (ty + dy) * wx + (tx + dx)
                if (!GSMap.IsValidTile(tile)) continue
                local ind = GSIndustry.GetIndustryID(tile)
                if (ind == null || ind < 0 || !GSIndustry.IsValidIndustry(ind))
                    continue
                if (ind in ids) continue
                /* The role filter comes after the id is known: the scan of
                 * record counts industries the stop's cargo role can use. */
                if (acceptor) {
                    if (GSIndustry.IsCargoAccepted(ind, FREIGHT_CARGO) !=
                        GSIndustry.CAS_ACCEPTED) continue
                } else {
                    local produced = GSIndustry.GetLastMonthProduction(
                        ind, FREIGHT_CARGO)
                    if (produced <= 0) continue
                }
                ids[ind] <- true
                order.append(ind)
                if (order.len() > 8) throw "D5_NATIVE_FACT"
            }
        }
        local list = []
        foreach (id in order) list.append(id)
        return {ids = list, radius = radius}
    }

    /* Compatible buildable road truck engine predicate for the corridor
     * cargo, identical to the proven lifecycle kernel: default cargo IS the
     * corridor cargo, no refit exists in this machinery. */
    function Compatible(e) {
        return GSEngine.IsBuildable(e) && GSEngine.IsValidEngine(e) &&
            GSEngine.GetVehicleType(e) == GSVehicle.VT_ROAD &&
            !GSEngine.IsArticulated(e) &&
            GSEngine.CanRunOnRoad(e, 0) && GSEngine.HasPowerOnRoad(e, 0) &&
            GSCargo.IsValidCargo(GSEngine.GetCargoType(e)) &&
            GSEngine.GetCargoType(e) == FREIGHT_CARGO &&
            GSRoad.GetRoadVehicleTypeForCargo(GSEngine.GetCargoType(e)) ==
                GSRoad.ROADVEHTYPE_TRUCK &&
            GSEngine.CanRefitCargo(e, GSEngine.GetCargoType(e)) &&
            GSEngine.GetCapacity(e) > 0
    }

    /* One tested native quote for one engine at the depot: the fixed-demo
     * test-mode pattern (BuildVehicle answers 0 on success in test mode,
     * any other value on failure). */
    function QuoteBuild(engine) {
        local accounting = GSAccounting()
        local testing = GSTestMode()
        local value = GSVehicle.BuildVehicle(this.depot_tile, engine)
        local cost = accounting.GetCosts()
        testing = null
        accounting = null
        return [value == 0, cost]
    }

    /* The live vehicle's report, read natively. The cargo slot is the
     * admitted corridor cargo: a vehicle carrying any other cargo reads
     * capacity 0 there and the windows refuse on that capacity. */
    function VState(company) {
        local v = vehicle_id
        return {
            owner = GSVehicle.GetOwner(v),
            engine = GSVehicle.GetEngineType(v),
            location = GSVehicle.GetLocation(v),
            capacity = GSVehicle.GetCapacity(v, FREIGHT_CARGO),
            state_int = GSVehicle.GetState(v),
            in_depot = GSVehicle.IsInDepot(v),
            speed = GSVehicle.GetCurrentSpeed(v),
            load = GSVehicle.GetCargoLoad(v, FREIGHT_CARGO),
            funds = GSCompany.GetBankBalance(company)
        }
    }

    function StateName(s) {
        if (s == GSVehicle.VS_IN_DEPOT) return "IN_DEPOT"
        if (s == GSVehicle.VS_RUNNING) return "RUNNING"
        if (s == GSVehicle.VS_AT_STATION) return "AT_STATION"
        if (s == GSVehicle.VS_STOPPED) return "STOPPED"
        if (s == GSVehicle.VS_BROKEN) return "BROKEN"
        if (s == GSVehicle.VS_CRASHED) return "CRASHED"
        return "INVALID"
    }

    /* The live vehicle identity check every post-purchase exchange makes
     * against the latched engine and vehicle. */
    function VehicleReady(q) {
        return this.vehicle_id >= 0 &&
            GSVehicle.IsValidVehicle(this.vehicle_id) &&
            GSVehicle.IsPrimaryVehicle(this.vehicle_id) &&
            GSVehicle.GetOwner(this.vehicle_id) == q.company &&
            q.engine == this.engine_id && q.vehicle == this.vehicle_id &&
            q.pickup == this.pickup && q.delivery == this.delivery &&
            q.depot == this.depot_tile
    }

    /* -- op: site admission (pure observation, zero cost) ------------------- */
    function SiteOp(q, r) {
        local obs = null
        try {
            local paused = GSGame.IsPaused()
            local pup = ObserveStop(this.pickup, this.pickup_front, q.company)
            local del = ObserveStop(this.delivery, this.delivery_front, q.company)
            local dep = ObserveDepot(q.company)
            local wit = Witness(q.company)
            local fleet = 0
            local list = GSVehicleList()
            for (local i = list.Begin(); !list.IsEnd(); i = list.Next())
                if (GSVehicle.IsValidVehicle(i) && GSVehicle.IsPrimaryVehicle(i) &&
                    GSVehicle.GetOwner(i) == q.company) fleet++
            obs = {
                paused = paused, pup = pup, del = del, depot = dep,
                wit = wit, fleet = fleet
            }
        } catch (error) {
            r.status = "UNSUPPORTED_NATIVE_FACT"
            return
        }
        r.funds = obs.pup.funds
        if (obs.paused) {
            r.status = "PAUSED"
        } else if (!obs.pup.stop || !obs.pup.truck || obs.pup.sid < 0 ||
                   !obs.pup.linked || obs.pup.owner != q.company) {
            r.status = "INVALID_SITE"
        } else if (!obs.del.stop || !obs.del.truck || obs.del.sid < 0 ||
                   obs.del.sid == obs.pup.sid || !obs.del.linked ||
                   obs.del.owner != q.company) {
            r.status = "INVALID_SITE"
        } else if (!obs.depot.depot || obs.depot.owner != q.company ||
                   obs.depot.front_id != this.depot_front || !obs.depot.linked) {
            r.status = "INVALID_SITE"
        } else if (!obs.depot.edge) {
            /* F-12: the directed depot-entry probe must read connected in
             * both directions before the site exchange admits anything. */
            r.status = "INVALID_SITE"
        } else if (obs.wit.pairs_ok != obs.wit.pair_total) {
            r.status = "INVALID_SITE"
        } else if (obs.fleet != 0) {
            /* A v2 site admits only a company with zero vehicles. This
             * refusal is issued before any observation field attaches, so
             * the reply keeps the contract's refusal shape (a refusal
             * readback carries no observation set). */
            r.status = "INVALID_SITE"
        } else {
            /* The acceptance fact is the proven catchment predicate over the
             * delivery stop tile (0..8 eighths) and it must read the pinned
             * census bound 8/8 exactly: the A1 bay of record accepts cargo 1
             * at 8/8, and a lower measured value is an INVALID_SITE refusal,
             * never a downgrade. The discovery then inspects each stop's
             * measured-radius box: exactly one cargo-producing industry in
             * the pickup box, exactly one cargo-accepting industry in the
             * delivery box — both ids latched here, never pinned. The
             * production and waiting levels are reported as facts; they gate
             * the honest load window later, not admission. */
            try {
                local radius = GSStation.GetCoverageRadius(GSStation.STATION_TRUCK_STOP)
                if (radius < 0) throw "D5_NATIVE_FACT"
                local accept = GSTile.GetCargoAcceptance(this.delivery, FREIGHT_CARGO, 1, 1, radius)
                if (accept < 0 || accept > 8) throw "D5_NATIVE_FACT"
                if (accept != 8) {
                    r.status = "INVALID_SITE"
                    return
                }
                local producing = DiscoveryBoxes(q, this.pickup, false)
                local accepting = DiscoveryBoxes(q, this.delivery, true)
                if (producing.ids.len() != 1 || accepting.ids.len() != 1) {
                    r.status = "INVALID_SITE"
                    return
                }
                local production = GSIndustry.GetLastMonthProduction(
                    producing.ids[0], FREIGHT_CARGO)
                local waiting = GSStation.GetCargoWaiting(obs.pup.sid, FREIGHT_CARGO)
                if (production < 0 || waiting < 0)
                    throw "D5_NATIVE_FACT"
                local income = GSCompany.GetQuarterlyIncome(
                    q.company, GSCompany.CURRENT_QUARTER)
                if (income < -2147483648 || income > 2147483647)
                    throw "D5_NATIVE_FACT"
                r.paused <- obs.paused
                r.truck0 <- obs.pup.truck
                r.sid0 <- obs.pup.sid
                r.truck1 <- obs.del.truck
                r.sid1 <- obs.del.sid
                r.depot_ok <- obs.depot.depot && obs.depot.linked
                r.owner <- obs.depot.owner
                r.pairs_ok <- obs.wit.pairs_ok
                r.pair_total <- obs.wit.pair_total
                r.road_ready <-
                    GSRoad.GetCurrentRoadType() == 0 && GSRoad.IsRoadTypeAvailable(0)
                r.depot_edge <- obs.depot.edge
                r.accept <- accept
                r.pickup_radius <- producing.radius
                r.delivery_radius <- accepting.radius
                r.pickup_industry <- producing.ids[0]
                r.pickup_industry_count <- producing.ids.len()
                r.delivery_industry <- accepting.ids[0]
                r.delivery_industry_count <- accepting.ids.len()
                r.prod <- production
                r.wait <- waiting
                r.vehicles <- obs.fleet
                r.income <- income
                r.status = "READY"
                this.site_sid0 = obs.pup.sid
                this.site_sid1 = obs.del.sid
                this.site_waiting = waiting
                this.site_production = production
                this.pickup_industry = producing.ids[0]
                this.delivery_industry = accepting.ids[0]
            } catch (error) {
                r.status = "UNSUPPORTED_NATIVE_FACT"
            }
        }
    }

    /* -- op: pinned engine admission (observation + one test quote) --------- */
    function EngineOp(q, r) {
        if (GSGame.IsPaused()) {
            r.status = "PAUSED"
            return
        }
        try {
            /* F-10: no enumeration fallback. TheRequest's pinned id is the
             * admitted identity; the bounded census echo around it stays
             * observational, never a selection. */
            local pinned = q.engine
            if (pinned != this.ENGINE_PIN) {
                r.status = "ENGINE_PIN_MISMATCH"
                return
            }
            if (!Compatible(pinned)) {
                r.status = "ENGINE_PIN_MISMATCH"
                return
            }
            /* The bounded compatible-universe echo: descending, at most
             * FLEET_ECHO ids, with the full compatible count beside it. */
            local list = GSEngineList(GSVehicle.VT_ROAD)
            local fleet = []
            local fleet_count = 0
            for (local e = list.Begin(); !list.IsEnd(); e = list.Next()) {
                if (!Compatible(e)) continue
                fleet_count++
                if (fleet.len() < this.FLEET_ECHO) fleet.append(e)
            }
            /* Insertion sort, descending, bounded list. */
            for (local i = 1; i < fleet.len(); i++) {
                local value = fleet[i]
                local j = i - 1
                while (j >= 0 && fleet[j] < value) {
                    fleet[j + 1] = fleet[j]
                    j--
                }
                fleet[j + 1] = value
            }
            local funds = GSCompany.GetBankBalance(q.company)
            r.funds = funds
            if (!GSEngine.IsBuildable(pinned)) {
                r.status = "UNAVAILABLE_ENGINE"
                return
            }
            local tested = QuoteBuild(pinned)
            if (!tested[0] || tested[1] <= 0) {
                r.status = "UNAVAILABLE_ENGINE"
                return
            }
            /* The engine reply's tested quote must equal the engine's own
             * price: a differently priced world is refused outright. */
            if (tested[1] != GSEngine.GetPrice(pinned)) {
                r.status = "COST_CHANGED"
                return
            }
            if (tested[1] > q.max_cost) {
                r.status = "COST_LIMIT"
                return
            }
            if (funds < tested[1]) {
                r.status = "INSUFFICIENT_FUNDS"
                return
            }
            local income = GSCompany.GetQuarterlyIncome(
                q.company, GSCompany.CURRENT_QUARTER)
            if (income < -2147483648 || income > 2147483647)
                throw "D5_NATIVE_FACT"
            local capacity = GSEngine.GetCapacity(pinned)
            r.available <- true
            r.compatible <- true
            r.capacity <- capacity
            r.cargo <- GSEngine.GetCargoType(pinned)
            r.price <- GSEngine.GetPrice(pinned)
            r.max_speed <- GSEngine.GetMaxSpeed(pinned)
            r.fleet <- fleet
            r.fleet_count <- fleet_count
            r.income <- income
            r.engine = pinned
            r.cost = tested[1]
            r.status = "READY"
            this.engine_id = pinned
            this.engine_capacity = capacity
            this.engine_quote = tested[1]
        } catch (error) {
            r.status = "UNSUPPORTED_NATIVE_FACT"
        }
    }

    /* -- op: purchase (one test-equal re-quote, one real BuildVehicle) ------ */
    function PurchaseOp(q, r) {
        if (GSGame.IsPaused()) {
            r.status = "PAUSED"
            return
        }
        if (this.engine_id < 0 || this.site_sid0 < 0 || this.site_sid1 < 0 ||
            q.engine != this.engine_id || q.expected_cost != this.engine_quote) {
            r.status = "STALE_ADMISSION"
            return
        }
        try {
            local funds = GSCompany.GetBankBalance(q.company)
            r.funds = funds
            local quote = QuoteBuild(q.engine)
            if (!quote[0] || quote[1] <= 0) {
                r.status = "UNAVAILABLE_ENGINE"
                return
            }
            if (quote[1] != q.expected_cost || quote[1] > q.max_cost) {
                r.status = "COST_CHANGED"
                return
            }
            if (funds < quote[1]) {
                r.status = "INSUFFICIENT_FUNDS"
                return
            }
            /* The one real build command: accounting around it records the
             * realized cost; BuildVehicle answers the new VehicleID. */
            local accounting = GSAccounting()
            local built = GSVehicle.BuildVehicle(this.depot_tile, q.engine)
            local cost = accounting.GetCosts()
            accounting = null
            if (!GSVehicle.IsValidVehicle(built)) {
                r.status = "UNSUPPORTED_NATIVE_FACT"
                return
            }
            if (cost != quote[1]) {
                r.status = "COST_CHANGED"
                return
            }
            local after = GSCompany.GetBankBalance(q.company)
            if (funds - after != cost) {
                r.status = "READBACK_MISMATCH"
                return
            }
            local income = GSCompany.GetQuarterlyIncome(
                q.company, GSCompany.CURRENT_QUARTER)
            if (income < -2147483648 || income > 2147483647)
                throw "D5_NATIVE_FACT"
            r.funds = after
            r.cost = cost
            r.income <- income
            r.vehicle = built
            r.status = "BUILT"
            this.vehicle_id = built
        } catch (error) {
            r.status = "UNSUPPORTED_NATIVE_FACT"
        }
    }

    /* -- op: independent vehicle readback (pure observation, zero cost) ----- */
    function VReadOp(q, r) {
        if (!VehicleReady(q)) {
            r.status = "STALE_ADMISSION"
            return
        }
        try {
            local obs = VState(q.company)
            if (obs.owner != q.company || obs.capacity < 0 || obs.speed < 0 ||
                obs.load < 0 || obs.in_depot == null) {
                r.status = "UNSUPPORTED_NATIVE_FACT"
                return
            }
            local income = GSCompany.GetQuarterlyIncome(
                q.company, GSCompany.CURRENT_QUARTER)
            if (income < -2147483648 || income > 2147483647)
                throw "D5_NATIVE_FACT"
            r.funds = obs.funds
            r.owner <- obs.owner
            r.location <- obs.location
            r.capacity <- obs.capacity
            r.cargo <- FREIGHT_CARGO
            r.state <- StateName(obs.state_int)
            r.in_depot <- obs.in_depot
            r.speed <- obs.speed
            r.income <- income
            r.status = "READ"
        } catch (error) {
            r.status = "UNSUPPORTED_NATIVE_FACT"
        }
    }

    /* -- op: order appends (stop TILES of the site readback, pinned v2 flags) */
    function OrderOp(q, r) {
        if (GSGame.IsPaused()) {
            r.status = "PAUSED"
            return
        }
        if (!VehicleReady(q)) {
            r.status = "STALE_ADMISSION"
            return
        }
        /* N1: the 15.x append takes the stop TILE, not the station id; the
         * pinned stop tiles resolve to their stations natively and the
         * readback verifies that resolution against the site-latched sids. */
        local dest = q.order_index == 0 ? this.pickup : this.delivery
        /* N2: the real 15.x flag values. The pickup stop order carries
         * OF_NONE (no load policy), the delivery bay's OF_NO_LOAD (never
         * unload here). OF_FULL_LOAD is documented forbidden and is never
         * issued in any branch of this machinery. */
        local flags = q.order_index == 0 ? this.OF_NONE : this.OF_NO_LOAD
        if (dest < 0) {
            r.status = "STALE_ADMISSION"
            return
        }
        try {
            /* Stopped-style preconditions: the vehicle reads stopped in its
             * building depot and the order list is exactly this index long. */
            if (!GSVehicle.IsInDepot(this.vehicle_id) ||
                GSOrder.GetOrderCount(this.vehicle_id) != q.order_index) {
                r.status = "STALE_ADMISSION"
                return
            }
            /* N3: AreOrderFlagsValid is the two-argument destination form. */
            if (!GSOrder.AreOrderFlagsValid(dest, flags) ||
                !GSOrder.AppendOrder(this.vehicle_id, dest, flags)) {
                r.status = "UNSUPPORTED_NATIVE_FACT"
                return
            }
            local d = GSOrder.GetOrderDestination(this.vehicle_id, q.order_index)
            local f = GSOrder.GetOrderFlags(this.vehicle_id, q.order_index)
            local g = GSOrder.IsGotoStationOrder(this.vehicle_id, q.order_index)
            /* The stored destination must be the station the stop tile
             * resolves to (N1: tile in, station stored), the stored flags
             * must equal the appended policy exactly, and the order must be
             * goto-station. */
            local expected_sid = q.order_index == 0 ? this.site_sid0 : this.site_sid1
            if (d != expected_sid || f != flags || g != true) {
                r.status = "READBACK_MISMATCH"
                return
            }
            local income = GSCompany.GetQuarterlyIncome(
                q.company, GSCompany.CURRENT_QUARTER)
            if (income < -2147483648 || income > 2147483647)
                throw "D5_NATIVE_FACT"
            r.dest <- dest
            r.flags <- f
            r.goto <- g
            r.income <- income
            r.status = "ORDERED"
        } catch (error) {
            r.status = "UNSUPPORTED_NATIVE_FACT"
        }
    }

    /* -- op: exact order inventory (tile destinations, real flag values) ---- */
    function OrderReadOp(q, r) {
        if (!VehicleReady(q)) {
            r.status = "STALE_ADMISSION"
            return
        }
        try {
            local count = GSOrder.GetOrderCount(this.vehicle_id)
            if (count != 2) {
                r.status = "READBACK_MISMATCH"
                return
            }
            local d0 = GSOrder.GetOrderDestination(this.vehicle_id, 0)
            local f0 = GSOrder.GetOrderFlags(this.vehicle_id, 0)
            local g0 = GSOrder.IsGotoStationOrder(this.vehicle_id, 0)
            local d1 = GSOrder.GetOrderDestination(this.vehicle_id, 1)
            local f1 = GSOrder.GetOrderFlags(this.vehicle_id, 1)
            local g1 = GSOrder.IsGotoStationOrder(this.vehicle_id, 1)
            /* N1/N2 of the inventory: the stored destinations are the
             * site-latched station ids the stop tiles resolve to, the stored
             * flags are the real appended values (OF_NONE then OF_NO_LOAD),
             * both goto-station. */
            if (d0 != this.site_sid0 || f0 != this.OF_NONE || g0 != true ||
                d1 != this.site_sid1 || f1 != this.OF_NO_LOAD || g1 != true) {
                r.status = "READBACK_MISMATCH"
                return
            }
            local income = GSCompany.GetQuarterlyIncome(
                q.company, GSCompany.CURRENT_QUARTER)
            if (income < -2147483648 || income > 2147483647)
                throw "D5_NATIVE_FACT"
            r.order_len <- count
            r.dest0 <- this.pickup
            r.flags0 <- f0
            r.goto0 <- g0
            r.dest1 <- this.delivery
            r.flags1 <- f1
            r.goto1 <- g1
            r.income <- income
            r.status = "ORDER_SET_VERIFIED"
        } catch (error) {
            r.status = "UNSUPPORTED_NATIVE_FACT"
        }
    }

    /* -- op: pre-start monitor arming (keep_monitoring=true, zero baseline) -- */
    function MonitorOp(q, r) {
        if (GSGame.IsPaused()) {
            r.status = "PAUSED"
            return
        }
        if (!VehicleReady(q)) {
            r.status = "STALE_ADMISSION"
            return
        }
        if (this.pickup_industry < 0 || this.delivery_industry < 0 ||
            this.pickup_industry == this.delivery_industry) {
            r.status = "STALE_ADMISSION"
            return
        }
        try {
            local pickup = GSCargoMonitor.GetIndustryPickupAmount(
                q.company, FREIGHT_CARGO, this.pickup_industry, true)
            local delivery = GSCargoMonitor.GetIndustryDeliveryAmount(
                q.company, FREIGHT_CARGO, this.delivery_industry, true)
            local income = GSCompany.GetQuarterlyIncome(q.company, GSCompany.CURRENT_QUARTER)
            local delivered = GSCompany.GetQuarterlyCargoDelivered(q.company, GSCompany.CURRENT_QUARTER)
            if (pickup < 0 || delivery < 0 || delivered < 0 ||
                income < -2147483648 || income > 2147483647) {
                r.status = "UNSUPPORTED_NATIVE_FACT"
                return
            }
            if (pickup != 0 || delivery != 0) {
                /* A nonzero pre-start monitor baseline is a refused
                 * observation set, never a claimed ARMED state. */
                r.status = "READBACK_MISMATCH"
                return
            }
            r.pickup_amount <- pickup
            r.delivery_amount <- delivery
            r.income <- income
            r.delivered <- delivered
            r.status = "ARMED"
            this.monitor_armed = true
            this.armed_income = income
            this.armed_delivered = delivered
        } catch (error) {
            r.status = "UNSUPPORTED_NATIVE_FACT"
        }
    }

    /* -- op: start ---------------------------------------------------------- */
    function StartOp(q, r) {
        if (GSGame.IsPaused()) {
            r.status = "PAUSED"
            return
        }
        if (!VehicleReady(q)) {
            r.status = "STALE_ADMISSION"
            return
        }
        try {
            if (!GSVehicle.StartStopVehicle(this.vehicle_id)) {
                r.status = "UNSUPPORTED_NATIVE_FACT"
                return
            }
            local state = StateName(GSVehicle.GetState(this.vehicle_id))
            local speed = GSVehicle.GetCurrentSpeed(this.vehicle_id)
            if (state != "RUNNING" || speed < 0) {
                r.status = "READBACK_MISMATCH"
                return
            }
            local income = GSCompany.GetQuarterlyIncome(
                q.company, GSCompany.CURRENT_QUARTER)
            if (income < -2147483648 || income > 2147483647)
                throw "D5_NATIVE_FACT"
            r.state <- state
            r.speed <- speed
            r.income <- income
            r.status = "STARTED"
        } catch (error) {
            r.status = "UNSUPPORTED_NATIVE_FACT"
        }
    }

    /* -- watch window helpers ------------------------------------------------ */
    function WindowCaps(q) {
        local cap_t = q.watch_ticks < MAX_TICKS ? q.watch_ticks : MAX_TICKS
        /* transit/deliver windows carry no day echo (-1); they are bounded by
         * the module day cap, not by a nonsensical negative budget. */
        local cap_d = q.watch_days < 0 ? MAX_DAYS :
            (q.watch_days < MAX_DAYS ? q.watch_days : MAX_DAYS)
        return [cap_t, cap_d]
    }

    /* -- op: load-watch (window 1: one positive departure-load snapshot) ----- */
    function LoadWatch(q, r) {
        if (!VehicleReady(q)) {
            r.status = "STALE_ADMISSION"
            return
        }
        try {
            local caps = WindowCaps(q)
            local cap_t = caps[0]
            local cap_d = caps[1]
            local capacity = GSVehicle.GetCapacity(this.vehicle_id, FREIGHT_CARGO)
            if (capacity != this.engine_capacity) {
                r.status = "READBACK_MISMATCH"
                return
            }
            local prev = GetTick()
            local started_day = GSDate.GetCurrentDate()
            if (started_day < 0) {
                r.status = "UNSUPPORTED_NATIVE_FACT"
                return
            }
            local samples = 0
            for (;;) {
                /* Pause is refused on every sample (fail-closed, first
                 * sample included); the clock sanity follows only real
                 * sleeps: a regression or a non-advancing tick is stalled. */
                if (GSGame.IsPaused()) {
                    r.status = "PAUSED"
                    return
                }
                if (samples > 0) {
                    Sleep(1)
                    local now = GetTick()
                    if (now <= prev) {
                        r.tick <- now
                        r.day <- GSDate.GetCurrentDate()
                        r.status = "CLOCK_STALLED"
                        return
                    }
                    prev = now
                }
                local day = GSDate.GetCurrentDate()
                if (day - started_day >= cap_d) {
                    r.tick <- prev
                    r.day <- day
                    r.status = "WINDOW_EXHAUSTED"
                    return
                }
                local load = GSVehicle.GetCargoLoad(this.vehicle_id, FREIGHT_CARGO)
                if (load < 0) {
                    r.status = "UNSUPPORTED_NATIVE_FACT"
                    return
                }
                /* The departure gate of record: any positive load within the
                 * vehicle's capacity is a departure snapshot (partial loads
                 * legal; full load never demanded). */
                if (load > 0) {
                    if (load > capacity) {
                        r.status = "UNSUPPORTED_NATIVE_FACT"
                        return
                    }
                    local wait = GSStation.GetCargoWaiting(this.site_sid0, FREIGHT_CARGO)
                    if (wait < 0) {
                        r.status = "UNSUPPORTED_NATIVE_FACT"
                        return
                    }
                    local income = GSCompany.GetQuarterlyIncome(
                        q.company, GSCompany.CURRENT_QUARTER)
                    if (income < -2147483648 || income > 2147483647)
                        throw "D5_NATIVE_FACT"
                    r.paused <- false
                    r.load <- load
                    r.capacity <- capacity
                    r.wait <- wait
                    r.income <- income
                    r.tick <- prev
                    r.day <- day
                    r.status = "LOADED"
                    this.observed_load = load
                    return
                }
                /* F-11: a departure with no cargo is its own typed outcome.
                 * The vehicle waiting at the pickup stop (route index 0) or
                 * standing in the pinned depot is pre-departure waiting; any
                 * other on-route tile proves the truck left the pickup empty,
                 * and that observation is carried honestly as ZERO_DEPARTED
                 * (never LOADED, never WINDOW_EXHAUSTED). The schedule
                 * continues: the deliver window of this cycle reconciles an
                 * empty load against zero monitors. */
                local loc = GSVehicle.GetLocation(this.vehicle_id)
                if (loc != this.depot_tile && loc != this.pickup) {
                    local income = GSCompany.GetQuarterlyIncome(
                        q.company, GSCompany.CURRENT_QUARTER)
                    if (income < -2147483648 || income > 2147483647)
                        throw "D5_NATIVE_FACT"
                    r.paused <- false
                    r.load <- load
                    r.income <- income
                    r.tick <- prev
                    r.day <- day
                    r.status = "ZERO_DEPARTED"
                    this.observed_load = 0
                    return
                }
                samples++
                if (samples > cap_t) {
                    r.tick <- prev
                    r.day <- day
                    r.status = "WINDOW_EXHAUSTED"
                    return
                }
            }
        } catch (error) {
            r.status = "UNSUPPORTED_NATIVE_FACT"
        }
    }

    /* -- op: transit-watch (window 2: the ordered route walk to delivery) --- */
    function TransitWatch(q, r) {
        if (!VehicleReady(q)) {
            r.status = "STALE_ADMISSION"
            return
        }
        try {
            local caps = WindowCaps(q)
            local cap_t = caps[0]
            local cap_d = caps[1]
            local capacity = GSVehicle.GetCapacity(this.vehicle_id, FREIGHT_CARGO)
            if (capacity != this.engine_capacity) {
                r.status = "READBACK_MISMATCH"
                return
            }
            local prev = GetTick()
            local started_day = GSDate.GetCurrentDate()
            if (started_day < 0) {
                r.status = "UNSUPPORTED_NATIVE_FACT"
                return
            }
            local samples = 0
            local last_progress = -1
            for (;;) {
                if (GSGame.IsPaused()) {
                    r.status = "PAUSED"
                    return
                }
                if (samples > 0) {
                    Sleep(1)
                    local now = GetTick()
                    if (now <= prev) {
                        r.tick <- now
                        r.day <- GSDate.GetCurrentDate()
                        r.status = "CLOCK_STALLED"
                        return
                    }
                    prev = now
                }
                local day = GSDate.GetCurrentDate()
                if (day - started_day >= cap_d) {
                    r.tick <- prev
                    r.day <- day
                    r.status = "WINDOW_EXHAUSTED"
                    return
                }
                local loc = GSVehicle.GetLocation(this.vehicle_id)
                /* Pre-departure observation: the vehicle stands in the pinned
                 * depot (off the ordered route by construction) until it
                 * leaves; that is waiting, not a routing defect. Any other
                 * off-route tile is a typed INVALID_ROUTE: the vehicle drove
                 * where the corridor receipt never built road. */
                if (loc != this.depot_tile && RouteIndex(loc) < 0) {
                    r.status = "INVALID_ROUTE"
                    return
                }
                local progress = RouteIndex(loc)
                /* Sampled-direction monotonicity: this window's samples may
                 * only advance along the ordered route. A sample behind an
                 * earlier one is a backward drive (or a revisit) the corridor
                 * receipt never describes: typed INVALID_ROUTE, fail-closed.
                 * This is sampled evidence, not tile-by-tile continuity. */
                if (progress >= 0) {
                    if (last_progress >= 0 && progress < last_progress) {
                        r.status = "INVALID_ROUTE"
                        return
                    }
                    last_progress = progress
                }
                local load = GSVehicle.GetCargoLoad(this.vehicle_id, FREIGHT_CARGO)
                if (load < 0) {
                    r.status = "UNSUPPORTED_NATIVE_FACT"
                    return
                }
                /* The arrival binds the departure snapshot: the load read at
                 * the bay must equal the load that left the pickup (a zero
                 * snapshot arrives zero — the honest empty run of a
                 * zero-departed cycle). A mid-route load change is drift. */
                if (load != this.observed_load) {
                    r.status = "READBACK_MISMATCH"
                    return
                }
                if (loc == this.delivery) {
                    local income = GSCompany.GetQuarterlyIncome(
                        q.company, GSCompany.CURRENT_QUARTER)
                    if (income < -2147483648 || income > 2147483647)
                        throw "D5_NATIVE_FACT"
                    r.paused <- false
                    r.position <- loc
                    r.progress <- progress
                    r.load <- load
                    r.income <- income
                    r.tick <- prev
                    r.day <- day
                    r.status = "AT_DELIVERY"
                    return
                }
                samples++
                if (samples > cap_t) {
                    r.tick <- prev
                    r.day <- day
                    if (progress >= 0) r.progress <- progress
                    r.status = "WINDOW_EXHAUSTED"
                    return
                }
            }
        } catch (error) {
            r.status = "UNSUPPORTED_NATIVE_FACT"
        }
    }

    /* -- op: deliver-watch (window 3: unload + per-cycle monitor arithmetic) -- */
    function DeliverWatch(q, r) {
        if (!VehicleReady(q)) {
            r.status = "STALE_ADMISSION"
            return
        }
        if (this.pickup_industry < 0 || this.delivery_industry < 0) {
            r.status = "STALE_ADMISSION"
            return
        }
        try {
            local caps = WindowCaps(q)
            local cap_t = caps[0]
            local cap_d = caps[1]
            local prev = GetTick()
            local started_day = GSDate.GetCurrentDate()
            if (started_day < 0) {
                r.status = "UNSUPPORTED_NATIVE_FACT"
                return
            }
            local samples = 0
            for (;;) {
                if (GSGame.IsPaused()) {
                    r.status = "PAUSED"
                    return
                }
                if (samples > 0) {
                    Sleep(1)
                    local now = GetTick()
                    if (now <= prev) {
                        r.tick <- now
                        r.day <- GSDate.GetCurrentDate()
                        r.status = "CLOCK_STALLED"
                        return
                    }
                    prev = now
                }
                local day = GSDate.GetCurrentDate()
                if (day - started_day >= cap_d) {
                    r.tick <- prev
                    r.day <- day
                    r.status = "WINDOW_EXHAUSTED"
                    return
                }
                local load = GSVehicle.GetCargoLoad(this.vehicle_id, FREIGHT_CARGO)
                if (load < 0) {
                    r.status = "UNSUPPORTED_NATIVE_FACT"
                    return
                }
                if (load == 0) {
                    local pickup = GSCargoMonitor.GetIndustryPickupAmount(
                        q.company, FREIGHT_CARGO, this.pickup_industry, true)
                    local delivery = GSCargoMonitor.GetIndustryDeliveryAmount(
                        q.company, FREIGHT_CARGO, this.delivery_industry, true)
                    if (pickup < 0 || delivery < 0) {
                        r.status = "UNSUPPORTED_NATIVE_FACT"
                        return
                    }
                    /* Per-cycle monitor arithmetic must reconcile this
                     * cycle's departure snapshot exactly before anything is
                     * consumed (a zero snapshot reconciles zero: the honest
                     * empty run of a zero-departed cycle). */
                    if (pickup != this.observed_load ||
                        delivery != this.observed_load) {
                        r.status = "READBACK_MISMATCH"
                        return
                    }
                    /* The per-cycle consumptions (keep_monitoring=false) of
                     * BOTH monitors, behind the equal-readback gate: each
                     * consumed value must equal the departure snapshot and
                     * the re-armed monitors must both read zero residue, so
                     * the next cycle snapshots exactly itself again. */
                    local consumed_pickup = GSCargoMonitor.GetIndustryPickupAmount(
                        q.company, FREIGHT_CARGO, this.pickup_industry, false)
                    local consumed_delivery = GSCargoMonitor.GetIndustryDeliveryAmount(
                        q.company, FREIGHT_CARGO, this.delivery_industry, false)
                    if (consumed_pickup != this.observed_load ||
                        consumed_delivery != this.observed_load) {
                        r.status = "READBACK_MISMATCH"
                        return
                    }
                    local recheck_pickup = GSCargoMonitor.GetIndustryPickupAmount(
                        q.company, FREIGHT_CARGO, this.pickup_industry, true)
                    local recheck_delivery = GSCargoMonitor.GetIndustryDeliveryAmount(
                        q.company, FREIGHT_CARGO, this.delivery_industry, true)
                    if (recheck_pickup != 0 || recheck_delivery != 0) {
                        r.status = "READBACK_MISMATCH"
                        return
                    }
                    local income = GSCompany.GetQuarterlyIncome(
                        q.company, GSCompany.CURRENT_QUARTER)
                    if (income < -2147483648 || income > 2147483647)
                        throw "D5_NATIVE_FACT"
                    r.paused <- false
                    r.load <- load
                    r.pickup_amount <- pickup
                    r.delivery_amount <- delivery
                    r.recheck <- true
                    r.income <- income
                    r.tick <- prev
                    r.day <- day
                    r.status = "DELIVERED"
                    return
                }
                samples++
                if (samples > cap_t) {
                    r.tick <- prev
                    r.day <- day
                    r.status = "WINDOW_EXHAUSTED"
                    return
                }
            }
        } catch (error) {
            r.status = "UNSUPPORTED_NATIVE_FACT"
        }
    }

    /* -- op: finance corroboration (quarter income/delivered/accepted) ------- */
    function FinanceOp(q, r) {
        if (!VehicleReady(q)) {
            r.status = "STALE_ADMISSION"
            return
        }
        if (!this.monitor_armed || this.delivery_industry < 0) {
            r.status = "STALE_ADMISSION"
            return
        }
        try {
            local income = GSCompany.GetQuarterlyIncome(q.company, GSCompany.CURRENT_QUARTER)
            local delivered = GSCompany.GetQuarterlyCargoDelivered(q.company, GSCompany.CURRENT_QUARTER)
            local last_accepted = GSIndustry.GetCargoLastAcceptedDate(
                this.delivery_industry, FREIGHT_CARGO)
            if (income < -2147483648 || income > 2147483647 || delivered < 0 ||
                last_accepted < -1) {
                r.status = "UNSUPPORTED_NATIVE_FACT"
                return
            }
            r.income <- income
            r.delivered <- delivered
            r.last_accepted <- last_accepted
            r.status = "FINANCE_VERIFIED"
        } catch (error) {
            r.status = "UNSUPPORTED_NATIVE_FACT"
        }
    }

    /* -- op: finish (the issued stop; the vehicle is never sold) ------------- */
    function FinishOp(q, r) {
        if (!VehicleReady(q)) {
            r.status = "STALE_ADMISSION"
            return
        }
        try {
            /* StartStopVehicle is a toggle: read the current state first and
             * stop only an un-stopped vehicle, then prove the final readback
             * stopped. An already-stopped vehicle is not commanded again and
             * reports stop_issued = false, which the Python verifier refuses
             * (an honest halt, never a claimed stop that did not happen). */
            local state = StateName(GSVehicle.GetState(this.vehicle_id))
            if (GSVehicle.GetCurrentSpeed(this.vehicle_id) < 0) {
                r.status = "UNSUPPORTED_NATIVE_FACT"
                return
            }
            local issued = false
            if (state != "STOPPED" && state != "IN_DEPOT") {
                if (!GSVehicle.StartStopVehicle(this.vehicle_id)) {
                    r.status = "UNSUPPORTED_NATIVE_FACT"
                    return
                }
                issued = true
            }
            local in_depot = GSVehicle.IsInDepot(this.vehicle_id)
            local speed = GSVehicle.GetCurrentSpeed(this.vehicle_id)
            if (speed < 0 || in_depot == null) {
                r.status = "UNSUPPORTED_NATIVE_FACT"
                return
            }
            state = StateName(GSVehicle.GetState(this.vehicle_id))
            if (speed != 0 || (state != "STOPPED" && state != "IN_DEPOT")) {
                r.status = "READBACK_MISMATCH"
                return
            }
            local income = GSCompany.GetQuarterlyIncome(
                q.company, GSCompany.CURRENT_QUARTER)
            if (income < -2147483648 || income > 2147483647)
                throw "D5_NATIVE_FACT"
            r.state <- state
            r.speed <- speed
            r.in_depot <- in_depot
            r.stop_issued <- issued
            r.income <- income
            r.status = "PHASE_STOPPED"
        } catch (error) {
            r.status = "UNSUPPORTED_NATIVE_FACT"
        }
    }

    /* -- the guarded wire entry point --------------------------------------- */
    function Handle(q) {
        if (typeof q != "table") return
        if (!("protocol" in q)) return
        if (q.protocol != 8) return
        if (!("op" in q) || typeof q.op != "string" || !OpAllowed(q.op)) return
        if (!("request_id" in q) || typeof q.request_id != "string" ||
            q.request_id.len() < 1 || q.request_id.len() > 32 ||
            !IdShape(q.request_id)) return
        if (!("plan" in q) || typeof q.plan != "string" || !Hex64(q.plan)) return
        if (!("route_digest" in q) || typeof q.route_digest != "string" ||
            !Hex64(q.route_digest)) return
        /* The construction-witness digest rides the site exchange only; the
         * wire serializes its absence as null on every other op. */
        if (!("witness_digest" in q)) return
        if (q.op == "site") {
            if (typeof q.witness_digest != "string" || !Hex64(q.witness_digest))
                return
        } else if (q.witness_digest != null) return
        if (!("company" in q) || typeof q.company != "integer" ||
            q.company < 0 || q.company > 14) return
        if (!("max_cost" in q) || typeof q.max_cost != "integer" ||
            q.max_cost < 0 || q.max_cost > 2147483647) return
        if (!("pickup" in q) || typeof q.pickup != "integer" ||
            q.pickup < 0 || q.pickup > 65535 ||
            !("delivery" in q) || typeof q.delivery != "integer" ||
            q.delivery < 0 || q.delivery > 65535 ||
            !("depot" in q) || typeof q.depot != "integer" ||
            q.depot < 0 || q.depot > 65535 ||
            q.pickup == q.delivery || q.depot == q.pickup ||
            q.depot == q.delivery) return
        /* The site exchange carries the derived vehicle route. Later
         * exchanges omit it (the wire serializes the absent field as null);
         * a route on any other op is malformed at the wire layer. */
        if (q.op == "site") {
            if (!("route" in q) || typeof q.route != "array" ||
                q.route.len() < 3 || q.route.len() > MAX_ROUTE_TILES) return
        } else if (("route" in q) && q.route != null) return
        /* Every request echoes the full correlation stride. */
        if (!("engine" in q) || !("vehicle" in q) || !("expected_cost" in q) ||
            !("order_index" in q) || !("watch_ticks" in q) ||
            !("watch_days" in q)) return
        if (!EchoOk(q)) return
        /* One-shot budget accounting: unique request ids, capped count; a
         * duplicate id or an exhausted budget is silently dropped. */
        if (used == null) used = {}
        if (q.request_id in used || this.requests >= this.max_requests) return
        used[q.request_id] <- true
        this.requests++
        /* Base response: every contract-required key echoes the request
         * correlation set; per-op observation fields attach below. */
        local r = {
            protocol = 8, op = q.op, request_id = q.request_id, plan = q.plan,
            company = q.company, max_cost = q.max_cost, pickup = q.pickup,
            delivery = q.delivery, depot = q.depot,
            route_digest = q.route_digest, engine = q.engine,
            vehicle = q.vehicle, expected_cost = q.expected_cost,
            order_index = q.order_index, watch_ticks = q.watch_ticks,
            watch_days = q.watch_days, status = "OUT_OF_ORDER", funds = 0,
            cost = 0
        }
        if (q.op == "site") r.witness_digest <- q.witness_digest
        local idx = PlannedIndex(q)
        if (idx < 0 || idx != this.stage || this.halted) {
            r.status = "OUT_OF_ORDER"
        } else if (this.plan_id != null && this.plan_id != q.plan) {
            r.status = "OUT_OF_ORDER"
        } else if (GSCompany.ResolveCompanyID(q.company) != q.company ||
                   q.company != FREIGHT_COMPANY) {
            /* Company defence-in-depth: the Python plan and verifier pin
             * company FREIGHT_COMPANY; the native handler refuses any other
             * resolvable company outright, before any admission or command. */
            r.status = "INVALID_COMPANY"
        } else {
            if (this.plan_id == null) this.plan_id = q.plan
            if (q.op == "site" && !RouteOk(q.route, q.pickup, q.delivery, q.depot)) {
                r.status = "INVALID_ROUTE"
            } else if (q.op != "site" &&
                       (q.pickup != this.pickup || q.delivery != this.delivery ||
                        q.depot != this.depot_tile ||
                        this.route_digest == null || q.route_digest != this.route_digest)) {
                r.status = "STALE_ADMISSION"
            } else {
                if (q.op == "site") LatchRoute(q)
                local company = GSCompanyMode(q.company)
                if (!GSCompanyMode.IsValid()) {
                    r.status = "INVALID_COMPANY"
                } else {
                    GSRoad.SetCurrentRoadType(GSRoad.ROADTYPE_ROAD)
                    /* Per-exchange funds readback: every reply carries the
                     * company balance at the exchange boundary, and the ops
                     * below attach the quarter income their F-6 ledger span
                     * attributes. */
                    r.funds = GSCompany.GetBankBalance(q.company)
                    if (GSRoad.GetCurrentRoadType() != 0 || !GSRoad.IsRoadTypeAvailable(0)) {
                        r.status = "UNSUPPORTED_NATIVE_FACT"
                    } else if (q.op == "site") {
                        SiteOp(q, r)
                    } else if (q.op == "engine") {
                        EngineOp(q, r)
                    } else if (q.op == "purchase") {
                        PurchaseOp(q, r)
                    } else if (q.op == "vread") {
                        VReadOp(q, r)
                    } else if (q.op == "order") {
                        OrderOp(q, r)
                    } else if (q.op == "order-read") {
                        OrderReadOp(q, r)
                    } else if (q.op == "monitor") {
                        MonitorOp(q, r)
                    } else if (q.op == "start") {
                        StartOp(q, r)
                    } else if (q.op == "load-watch") {
                        LoadWatch(q, r)
                    } else if (q.op == "transit-watch") {
                        TransitWatch(q, r)
                    } else if (q.op == "deliver-watch") {
                        DeliverWatch(q, r)
                    } else if (q.op == "finance") {
                        FinanceOp(q, r)
                    } else if (q.op == "finish") {
                        FinishOp(q, r)
                    }
                }
                company = null
            }
        }
        Guard(r)
        if (!GSAdmin.Send(r)) throw "D5_RESPONSE_SEND_FAILED"
        GSLog.Info("D5_V2_RESPONSE " + q.request_id + " " + r.status)
        /* Schedule accounting: only the exact planned status of the planned
         * exchange advances the stage — with the one F-11 exception: a typed
         * ZERO_DEPARTED load reply is the scheduled cycle's honest empty-run
         * evidence, so it advances the schedule (and never becomes a success
         * status); every other terminal status halts the schedule
         * prefix-preservingly. Evidence, never retries. */
        if (idx >= 0) {
            if (r.status == planned[idx][2] ||
                (q.op == "load-watch" && r.status == "ZERO_DEPARTED")) {
                if (idx == this.stage && !this.halted) this.stage = idx + 1
            } else {
                this.halted = true
            }
        }
    }

    /* Numeric bounds keep even the largest response honest and small; the
     * largest v2 reply is the engine census (the compatible-universe echo
     * under the protocol-8 1400-byte response bound,
     * MAX_FREIGHT_RESPONSE_BYTES_V2). They mirror the FreightReadbackV2
     * field bounds exactly (flags bound 0..255 — the real 15.x value space,
     * so OF_NO_LOAD 128 fits where protocol 5's 4-bit bound would not). */
    function Guard(r) {
        if ("route_digest" in r &&
            (typeof r.route_digest != "string" || !Hex64(r.route_digest)))
            throw "D5_RESPONSE_OUT_OF_BOUNDS"
        if ("witness_digest" in r &&
            (r.witness_digest != null &&
             (typeof r.witness_digest != "string" || !Hex64(r.witness_digest))))
            throw "D5_RESPONSE_OUT_OF_BOUNDS"
        if (r.funds < -2147483648 || r.funds > 2147483647 || r.cost < 0 ||
            r.cost > 2147483647) throw "D5_RESPONSE_OUT_OF_BOUNDS"
        if (r.engine < -1 || r.engine > 65535 || r.vehicle < -1 ||
            r.vehicle > 65535) throw "D5_RESPONSE_OUT_OF_BOUNDS"
        if (r.expected_cost < 0 || r.expected_cost > 2147483647 ||
            r.order_index < -1 || r.order_index > 1 ||
            r.watch_ticks < -1 || r.watch_ticks > MAX_TICKS ||
            r.watch_days < -1 || r.watch_days > MAX_DAYS)
            throw "D5_RESPONSE_OUT_OF_BOUNDS"
        if ("paused" in r && typeof r.paused != "bool") throw "D5_RESPONSE_OUT_OF_BOUNDS"
        if ("truck0" in r && typeof r.truck0 != "bool") throw "D5_RESPONSE_OUT_OF_BOUNDS"
        if ("truck1" in r && typeof r.truck1 != "bool") throw "D5_RESPONSE_OUT_OF_BOUNDS"
        if ("depot_ok" in r && typeof r.depot_ok != "bool") throw "D5_RESPONSE_OUT_OF_BOUNDS"
        if ("road_ready" in r && typeof r.road_ready != "bool")
            throw "D5_RESPONSE_OUT_OF_BOUNDS"
        if ("depot_edge" in r && typeof r.depot_edge != "bool")
            throw "D5_RESPONSE_OUT_OF_BOUNDS"
        if ("available" in r && typeof r.available != "bool") throw "D5_RESPONSE_OUT_OF_BOUNDS"
        if ("compatible" in r && typeof r.compatible != "bool") throw "D5_RESPONSE_OUT_OF_BOUNDS"
        if ("in_depot" in r && typeof r.in_depot != "bool") throw "D5_RESPONSE_OUT_OF_BOUNDS"
        if ("goto" in r && typeof r.goto != "bool") throw "D5_RESPONSE_OUT_OF_BOUNDS"
        if ("goto0" in r && typeof r.goto0 != "bool") throw "D5_RESPONSE_OUT_OF_BOUNDS"
        if ("goto1" in r && typeof r.goto1 != "bool") throw "D5_RESPONSE_OUT_OF_BOUNDS"
        if ("recheck" in r && typeof r.recheck != "bool") throw "D5_RESPONSE_OUT_OF_BOUNDS"
        if ("stop_issued" in r && typeof r.stop_issued != "bool")
            throw "D5_RESPONSE_OUT_OF_BOUNDS"
        if ("sid0" in r && (r.sid0 < -1 || r.sid0 > 1073741824)) throw "D5_RESPONSE_OUT_OF_BOUNDS"
        if ("sid1" in r && (r.sid1 < -1 || r.sid1 > 1073741824)) throw "D5_RESPONSE_OUT_OF_BOUNDS"
        if ("dest0" in r && (r.dest0 < -1 || r.dest0 > 1073741824)) throw "D5_RESPONSE_OUT_OF_BOUNDS"
        if ("dest1" in r && (r.dest1 < -1 || r.dest1 > 1073741824)) throw "D5_RESPONSE_OUT_OF_BOUNDS"
        if ("dest" in r && (r.dest < 0 || r.dest > 1073741824)) throw "D5_RESPONSE_OUT_OF_BOUNDS"
        if ("owner" in r && (r.owner < -1 || r.owner > 14)) throw "D5_RESPONSE_OUT_OF_BOUNDS"
        if ("pairs_ok" in r && (r.pairs_ok < 0 || r.pairs_ok > 63)) throw "D5_RESPONSE_OUT_OF_BOUNDS"
        if ("pair_total" in r && (r.pair_total < 0 || r.pair_total > 63))
            throw "D5_RESPONSE_OUT_OF_BOUNDS"
        if ("pickup_radius" in r && (r.pickup_radius < 1 || r.pickup_radius > 255))
            throw "D5_RESPONSE_OUT_OF_BOUNDS"
        if ("delivery_radius" in r && (r.delivery_radius < 1 || r.delivery_radius > 255))
            throw "D5_RESPONSE_OUT_OF_BOUNDS"
        if ("pickup_industry" in r &&
            (r.pickup_industry < 0 || r.pickup_industry > 65535))
            throw "D5_RESPONSE_OUT_OF_BOUNDS"
        if ("pickup_industry_count" in r &&
            (r.pickup_industry_count < 0 || r.pickup_industry_count > 8))
            throw "D5_RESPONSE_OUT_OF_BOUNDS"
        if ("delivery_industry" in r &&
            (r.delivery_industry < 0 || r.delivery_industry > 65535))
            throw "D5_RESPONSE_OUT_OF_BOUNDS"
        if ("delivery_industry_count" in r &&
            (r.delivery_industry_count < 0 || r.delivery_industry_count > 8))
            throw "D5_RESPONSE_OUT_OF_BOUNDS"
        if ("fleet" in r) {
            if (typeof r.fleet != "array" || r.fleet.len() > FLEET_ECHO)
                throw "D5_RESPONSE_OUT_OF_BOUNDS"
            foreach (e in r.fleet)
                if (typeof e != "integer" || e < 0 || e > 65535)
                    throw "D5_RESPONSE_OUT_OF_BOUNDS"
        }
        if ("fleet_count" in r && (r.fleet_count < 0 || r.fleet_count > 255))
            throw "D5_RESPONSE_OUT_OF_BOUNDS"
        if ("accept" in r && (r.accept < 0 || r.accept > 8)) throw "D5_RESPONSE_OUT_OF_BOUNDS"
        if ("prod" in r && (r.prod < 0 || r.prod > 2147483647)) throw "D5_RESPONSE_OUT_OF_BOUNDS"
        if ("wait" in r && (r.wait < 0 || r.wait > 2147483647)) throw "D5_RESPONSE_OUT_OF_BOUNDS"
        if ("vehicles" in r && (r.vehicles < 0 || r.vehicles > 2147483647))
            throw "D5_RESPONSE_OUT_OF_BOUNDS"
        if ("capacity" in r && (r.capacity < 0 || r.capacity > 2147483647))
            throw "D5_RESPONSE_OUT_OF_BOUNDS"
        if ("cargo" in r && (r.cargo < 0 || r.cargo > 63)) throw "D5_RESPONSE_OUT_OF_BOUNDS"
        if ("price" in r && (r.price < 0 || r.price > 2147483647))
            throw "D5_RESPONSE_OUT_OF_BOUNDS"
        if ("max_speed" in r && (r.max_speed < 0 || r.max_speed > 2147483647))
            throw "D5_RESPONSE_OUT_OF_BOUNDS"
        if ("location" in r && (r.location < 0 || r.location > 65535))
            throw "D5_RESPONSE_OUT_OF_BOUNDS"
        if ("state" in r && typeof r.state != "string") throw "D5_RESPONSE_OUT_OF_BOUNDS"
        if ("speed" in r && (r.speed < 0 || r.speed > 2147483647)) throw "D5_RESPONSE_OUT_OF_BOUNDS"
        if ("flags" in r && (r.flags < 0 || r.flags > 255)) throw "D5_RESPONSE_OUT_OF_BOUNDS"
        if ("flags0" in r && (r.flags0 < 0 || r.flags0 > 255)) throw "D5_RESPONSE_OUT_OF_BOUNDS"
        if ("flags1" in r && (r.flags1 < 0 || r.flags1 > 255)) throw "D5_RESPONSE_OUT_OF_BOUNDS"
        if ("order_len" in r && (r.order_len < 0 || r.order_len > 65535))
            throw "D5_RESPONSE_OUT_OF_BOUNDS"
        if ("pickup_amount" in r && (r.pickup_amount < 0 || r.pickup_amount > 2147483647))
            throw "D5_RESPONSE_OUT_OF_BOUNDS"
        if ("delivery_amount" in r && (r.delivery_amount < 0 || r.delivery_amount > 2147483647))
            throw "D5_RESPONSE_OUT_OF_BOUNDS"
        if ("income" in r && (r.income < -2147483648 || r.income > 2147483647))
            throw "D5_RESPONSE_OUT_OF_BOUNDS"
        if ("delivered" in r && (r.delivered < 0 || r.delivered > 2147483647))
            throw "D5_RESPONSE_OUT_OF_BOUNDS"
        if ("load" in r && (r.load < 0 || r.load > 2147483647)) throw "D5_RESPONSE_OUT_OF_BOUNDS"
        if ("position" in r && (r.position < 0 || r.position > 65535))
            throw "D5_RESPONSE_OUT_OF_BOUNDS"
        if ("progress" in r && (r.progress < 0 || r.progress > 63)) throw "D5_RESPONSE_OUT_OF_BOUNDS"
        if ("tick" in r && (r.tick < 0 || r.tick > 2147483647)) throw "D5_RESPONSE_OUT_OF_BOUNDS"
        if ("day" in r && (r.day < 0 || r.day > 2147483647)) throw "D5_RESPONSE_OUT_OF_BOUNDS"
        if ("last_accepted" in r && (r.last_accepted < -1 || r.last_accepted > 2147483647))
            throw "D5_RESPONSE_OUT_OF_BOUNDS"
    }

    function Start() {
        GSLog.Info("D5_V2_READY")
        while (true) {
            while (GSEventController.IsEventWaiting()) {
                local event = GSEventController.GetNextEvent()
                if (event.GetEventType() == GSEvent.ET_ADMIN_PORT)
                    Handle(GSEventAdminPort.Convert(event).GetObject())
            }
            Sleep(1)
        }
    }
}

/* Save-restore identity bridge: the retained staged info.nut (the A1 source
 * world's stored GameScript identity) declares CreateInstance() returning
 * "NetworkFreightProof". This subclass satisfies that contract without
 * modifying any retained identity byte; the staged composition re-bakes this
 * main.nut under the retained identity at staging time. */
class NetworkFreightProof extends D5FreightV2Proof {
}
