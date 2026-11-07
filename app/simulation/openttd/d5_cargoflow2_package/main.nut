/* Separate bounded native cargo-flow delivery handler (protocol 11).
 * Additive: no existing frozen package is modified or imported — protocols
 * 8/9/10 stay historical instruments of record and the sat agent dispatches
 * protocol-11 tables through this package alone. The attempt is the fixed
 * 26-exchange delivered schedule of record
 * (docs/d5-cargoflow-delivery-design-2026-11-04.md and the delivered-class
 * tail spec
 * docs/specs/d5-delivered-class-tail.md
 * §5.2/§5.3): the freight-family instrument chain (site re-pin, engine
 * census admission, quote-first purchase, two independent order readbacks,
 * monitor arming, start) follows the proven freight v2 op meanings; then
 * the new bounded first-arrival watch latches the ladder anchor at the
 * pickup stop, the thirteen-sample delivered flow ladder observes exactly
 * anchor + its planned offset every 5 economy days (flow-12 at anchor+60
 * is the settle margin that completes the delivery cycle), and the two
 * read-only tail exchanges run in the delivered flow-12 economy day —
 * 26 requests inside the 32-request budget.
 *
 * Observation set of a flow sample (§5.4): the E99 sample set (stockpiles,
 * waiting and planned families at both stops, monthly production and
 * transported, date, tick) plus the funds echo read at the post-wait
 * instant (§4.5: one response, one instant), the quarter income and
 * delivered reads, the vehicle state echo and the cycle latches the
 * per-tick poll gathered during the in-package wait (§5.3: every arrival
 * at either stop, every load/departure with its load count and every
 * unload with its delivered amount, each with its own (day, tick)). A
 * latch array that would overflow CARGOFLOW2_LATCH_LIMIT refuses the
 * exchange — latches are never truncated to fit. On any ladder sample
 * `stock_pickup` stays the pinned -1 non-producer fact (E65): any other
 * value refuses the exchange; `stock_bay` and the producer-side prod/trans
 * families carry the -1 fact verbatim with their log markers.
 *
 * Boundaries of record (§5.3): arrive-00 is bounded at 5 economy days
 * (deadline day 712233); a timeout — including a stalled clock or a
 * windowed-out flight — is a terminal ARRIVE_TIMEOUT, never a retry, and
 * the ladder never starts without its anchor. Flow steps wait for exactly
 * anchor + their planned offset (overshoot = WINDOW_EXHAUSTED; tick
 * regression = CLOCK_STALLED; both typed IN THE FLOW OP ONLY — the
 * arrive-watch maps the same window faults onto its own terminal
 * ARRIVE_TIMEOUT). A ladder step whose target day exceeds the launch-day
 * plus the 65-economy-day delivered authority (712293) refuses
 * AUTHORITY_EXCEEDED before any wait (the dual-package/pipeline
 * enforcement). The tail exchanges run instantly after flow-12's response
 * in the same economy day and re-check the anchor arithmetic themselves.
 *
 * Financial fence: the funds model and its zero-residual reconciliation
 * are Python-side (§4); this package only echoes its measured funds at
 * the exchange instant (post-wait for the ladder ops) and the pinned
 * engine census admission (engine-00 pins the running cost of record
 * through GSEngine.GetRunningCost — on the pinned binary that read IS
 * the 421 per-economy-year display figure, compared to its pin with no
 * second shift; the funds model derives day charges as display/365).
 * funding/quote/cost refusals fail closed before any mutation, and the
 * purchase realizes exactly its tested quote once.
 *
 * Wire discipline: the guard ladder mirrors the Python validator's
 * quiet/pitched request-shape rules; a request the Python contract could
 * never build is silently dropped (no reply, no budget). Accepted
 * exchanges answer exactly once, echoing the full correlation stride;
 * refusals carry no observation field at all; the flow window echoes
 * (WINDOW_EXHAUSTED/CLOCK_STALLED) carry exactly anchor/tick/day. Every
 * success frame carries the op's complete subset plus tick, day and its
 * own income read. The one-shot latch: the first accepted exchange fixes
 * the attempt's plan identity; a one-shot 32-id budget counts unique ids
 * only; only the exact planned success status advances the stage and any
 * other terminal status halts the schedule prefix-preservingly.
 *
 * Native API pins carried from the proven 15.3 records: GSDate,
 * GSGame.IsPaused, GSCompany.{ResolveCompanyID,GetBankBalance,
 * GetQuarterlyIncome,GetQuarterlyCargoDelivered}, GSCompanyMode,
 * GSEngine.{IsBuildable,GetCargoType,GetCapacity,GetPrice,GetMaxSpeed,
 * GetRunningCost}, GSVehicle.{IsValidVehicle,IsPrimaryVehicle,GetOwner,
 * GetEngineType,BuildVehicle,StartStopVehicle,GetLocation,GetCapacity,
 * GetState,IsInDepot,GetCurrentSpeed,GetCargoLoad}, GSOrder.{AreOrderFlagsValid
 * (two-argument tile destination form),AppendOrder(stop TILE),GetOrderCount,
 * GetOrderDestination,GetOrderFlags,IsGotoStationOrder}, GSStation.
 * {IsValidStation,GetStationID,GetCargoWaiting,GetCargoWaitingFrom,
 * GetCargoPlanned,GetCargoPlannedFrom}, GSIndustry.{IsValidIndustry,
 * GetStockpiledCargo,GetLastMonthProduction,GetLastMonthTransported,
 * GetCargoLastAcceptedDate}, GSCargoMonitor.{GetIndustryPickupAmount,
 * GetIndustryDeliveryAmount}, GSRoad.IsRoadDepotTile, GSAccounting,
 * GSTestMode. GSVehicle.BuildVehicle answers the new VehicleID in real
 * mode (0 on success in test mode like the proven quote path).
 *
 * Save-restore identity: the retained frozen-source.zip info.nut declares
 * CreateInstance() returning "NetworkFreightProof"; the empty bridge
 * subclass at the end satisfies that contract without modifying any
 * retained identity byte. */
class D5CargoFlow2Proof extends GSController {
    /* Schedule state: `cargoflow_stage` is the index of the one planned
     * exchange that may run next; `cargoflow_halted` stops every later
     * exchange after any success frame failed to produce its exact planned
     * status. `cargoflow_anchor` is the one economy-day anchor the first
     * arrival latches; every ladder exchange must carry it unchanged. */
    cargoflow_stage = 0
    cargoflow_halted = false
    cargoflow_anchor = null
    /* One-shot dispatcher budget accounting (unique ids, 32-request cap). */
    requests = 0
    used = null
    /* Latched prelaunch plan digest: the first accepted exchange fixes the
     * attempt's plan identity; every later exchange must match it. */
    plan_id = null
    /* Latched admission facts (one attempt: one engine, one vehicle). */
    engine_id = -1
    engine_quote = 0
    vehicle_id = -1
    monitor_armed = false

    /* Baked corridor identity pins of the consumed depot-chain lineage
     * (world-pin version 3; the same pins every protocol-5/8/9/10 exchange
     * echoes; the attempt never queries a foreign tile or foreign sid). */
    pickup = 45748
    delivery = 50862
    depot_tile = 45487
    /* Station identities of record: the corridor pickup stop and the A1
     * delivery bay. */
    PICKUP_SID = 0
    BAY_SID = 2
    /* Industry identities of record: the producing pickup industry 0 and
     * the accepting bay industry 1 (the census receipt rows). */
    PICKUP_IND = 0
    BAY_IND = 1
    /* Fixed corridor identity for the attempt. */
    CARGOFLOW2_COMPANY = 0
    CARGOFLOW2_CARGO = 1

    /* The pinned vehicle admission (F-10, the freight v2 pin carried on):
     * the engine census facts the engine exchange re-derives fail-closed. */
    ENGINE_PIN = 123
    ENGINE_QUOTE = 4429
    ENGINE_MAX_COST = 5000
    CAPACITY_PIN = 20
    SPEED_PIN = 48
    /* The pinned running-cost display figure (§4.1, the E111 correction):
     * GSEngine.GetRunningCost returns the display figure directly, so the
     * census join compares it to 421 with no further shift; the value
     * itself rides the engine readback. */
    RUNNING_DISPLAY_PIN = 421

    /* Real 15.x order-flag values (N2, carried from freight v2): the
     * pickup stop order carries OF_NONE, the bay's OF_NO_LOAD; a
     * full-load flag is never appended anywhere in this machinery. */
    OF_NONE = 0
    OF_NO_LOAD = 128

    /* Schedule boundaries of record (§5.3): the launch day L = 712228,
     * the 5-day arrival bound (deadline day 712233) and the delivered
     * 65-day attempt authority (last admissible observation day 712293 =
     * L + 65, enforced package-side before every ladder wait — the v1
     * envelope's 60-day figures belong to the consumed v1 candidates,
     * not to this package's ladder). */
    LAUNCH_DAY = 712228
    ARRIVE_MAX_DAYS = 5
    ARRIVE_DEADLINE = 712233
    DAY_BUDGET = 65
    AUTHORITY_LAST_DAY = 712293
    /* Per-window caps: the tick cap is the live in-package ceiling; the
     * exact equality ladder itself is the day authority. */
    WAIT_MAX_TICKS = 2048
    /* Per-flow-sample latch bound (§5.3): overflow refuses, never truncates. */
    LATCH_LIMIT = 8
    /* 26 planned exchanges, plus dispatcher slack only through unique ids:
     * request 33 is the first one the dispatcher drops. */
    max_requests = 32

    /* The fixed 26-exchange delivered schedule: [request_id, op, offset
     * echo, success status] — the third column mirrors the Python wire's
     * request-offset table exactly (-1 everywhere off the ladder, the
     * planned step on flow rows and the delivered 60 tail step), and the
     * fourth column is the contract's per-op success status. */
    cargoflow2_planned = [
        ["site-00", "site", -1, "READY"],
        ["engine-00", "engine", -1, "READY"],
        ["purchase-00", "purchase", -1, "BUILT"],
        ["vread-00", "vread", -1, "READ"],
        ["order-00", "order", -1, "ORDERED"],
        ["order-01", "order", -1, "ORDERED"],
        ["order-read-00", "order-read", -1, "ORDER_SET_VERIFIED"],
        ["monitor-00", "monitor", -1, "ARMED"],
        ["start-00", "start", -1, "STARTED"],
        ["vread-01", "vread", -1, "READ"],
        ["arrive-00", "arrive-watch", -1, "ANCHORED"],
        ["flow-00", "flow", 0, "READY"],
        ["flow-01", "flow", 5, "READY"],
        ["flow-02", "flow", 10, "READY"],
        ["flow-03", "flow", 15, "READY"],
        ["flow-04", "flow", 20, "READY"],
        ["flow-05", "flow", 25, "READY"],
        ["flow-06", "flow", 30, "READY"],
        ["flow-07", "flow", 35, "READY"],
        ["flow-08", "flow", 40, "READY"],
        ["flow-09", "flow", 45, "READY"],
        ["flow-10", "flow", 50, "READY"],
        ["flow-11", "flow", 55, "READY"],
        ["flow-12", "flow", 60, "READY"],
        ["finance-00", "finance", 60, "FINANCE_VERIFIED"],
        ["finish-00", "finish", 60, "PHASE_STOPPED"]
    ]

    /* Every observation field of the readback, in bridge-attach order;
     * the refusal strip deletes exactly this registry. */
    observation_fields = [
        "anchor", "tick", "day", "year", "month", "day_of_month",
        "stock_pickup", "stock_bay",
        "wait_pickup", "wait_pickup_from0", "wait_pickup_from1",
        "wait_bay", "wait_bay_from0", "wait_bay_from1",
        "count_pickup", "count_bay",
        "planned_pickup_from0", "planned_pickup_from1",
        "planned_bay_from0", "planned_bay_from1",
        "prod_pickup", "prod_bay", "trans_pickup", "trans_bay",
        "location", "state", "in_depot", "speed", "load", "capacity",
        "cargo", "owner", "running_cost", "order_len",
        "dest0", "flags0", "goto0", "dest1", "flags1", "goto1",
        "dest", "flags", "goto",
        "pickup_amount", "delivery_amount", "delivered", "last_accepted",
        "stop_issued", "latches"
    ]

    function CargoFlow2OpAllowed(op) {
        return op == "site" || op == "engine" || op == "purchase" ||
            op == "vread" || op == "order" || op == "order-read" ||
            op == "monitor" || op == "start" || op == "arrive-watch" ||
            op == "flow" || op == "finance" || op == "finish"
    }

    function CargoFlow2PlannedIndex(q) {
        /* The planned exchange carrying BOTH the request id and its op. */
        for (local i = 0; i < cargoflow2_planned.len(); i++)
            if (cargoflow2_planned[i][0] == q.request_id &&
                cargoflow2_planned[i][1] == q.op) return i
        return -1
    }

    /* The planned ladder offset of one planned row (the handler's own
     * offset echo check against the request's claim). */
    function CargoFlow2PlannedOffset(idx) {
        return cargoflow2_planned[idx][2]
    }

    /* The flow request-shape rule (mirrored from the Python request
     * validator): the id must be a planned flow row and its offset echo
     * must be exactly its planned ladder step. */
    function CargoFlow2FlowOffsetOk(q) {
        for (local i = 0; i < cargoflow2_planned.len(); i++)
            if (cargoflow2_planned[i][0] == q.request_id &&
                cargoflow2_planned[i][1] == "flow" &&
                cargoflow2_planned[i][2] == q.offset) return true
        return false
    }

    /* The tail request-shape rule (mirrored from the Python request
     * validator): the id must be a planned finance or finish row and its
     * offset echo must be exactly that row's planned ladder step — the
     * tails ride their own planned economy day. */
    function CargoFlow2TailOffsetOk(q) {
        for (local i = 0; i < cargoflow2_planned.len(); i++)
            if (cargoflow2_planned[i][0] == q.request_id &&
                (q.op == "finance" || q.op == "finish") &&
                cargoflow2_planned[i][1] == q.op &&
                cargoflow2_planned[i][2] == q.offset) return true
        return false
    }

    /* The planned tail ladder step of record: the finance row's own
     * planned offset (the tails ride the delivered flow-12 economy day). */
    function CargoFlow2TailStep() {
        for (local i = 0; i < cargoflow2_planned.len(); i++)
            if (cargoflow2_planned[i][1] == "finance") return cargoflow2_planned[i][2]
        return -1
    }

    /* Per-op request echo coherence, mirroring the Python validator's
     * quiet/pitched rules exactly; any incoherence is a malformed request
     * the dispatcher silently drops. Every non-site op ships the pinned
     * engine identity (F-10); the site request ships none. (The Python
     * validation leaves order_flags free on arrive-watch and flow; the
     * mirror keeps that width so the drop ladder matches verbatim.) */
    function CargoFlow2EchoOk(q) {
        if (typeof q.engine != "integer" || q.engine < -1 || q.engine > 65535)
            return false
        if (typeof q.vehicle != "integer" || q.vehicle < -1 || q.vehicle > 65535)
            return false
        if (typeof q.expected_cost != "integer" || q.expected_cost < 0 ||
            q.expected_cost > 2147483647) return false
        if (typeof q.order_index != "integer" || q.order_index < -1 ||
            q.order_index > 1) return false
        if (typeof q.order_flags != "integer" || q.order_flags < -1 ||
            q.order_flags > 255) return false
        if (typeof q.watch_days != "integer" || q.watch_days < -1 ||
            q.watch_days > 60) return false
        if (typeof q.offset != "integer" || q.offset < -1 || q.offset > 60)
            return false
        local quiet = q.expected_cost == 0 && q.order_index == -1 &&
            q.order_flags == -1 && q.watch_days == -1 && q.offset == -1
        if (q.op == "site")
            return q.engine == -1 && q.vehicle == -1 && quiet
        if (q.engine != this.ENGINE_PIN) return false
        if (q.op == "engine")
            return q.vehicle == -1 && quiet
        if (q.op == "purchase")
            return q.vehicle == -1 && q.order_index == -1 &&
                q.order_flags == -1 && q.watch_days == -1 &&
                q.offset == -1 && q.expected_cost == this.ENGINE_QUOTE &&
                q.max_cost == this.ENGINE_MAX_COST
        if (q.op == "vread")
            return q.vehicle >= 0 && quiet
        if (q.op == "order")
            return q.vehicle >= 0 && (q.order_index == 0 || q.order_index == 1) &&
                q.expected_cost == 0 && q.watch_days == -1 && q.offset == -1 &&
                q.order_flags ==
                    (q.order_index == 0 ? this.OF_NONE : this.OF_NO_LOAD)
        if (q.op == "order-read" || q.op == "monitor" || q.op == "start")
            return q.vehicle >= 0 && quiet
        if (q.op == "arrive-watch")
            return q.vehicle >= 0 && q.order_index == -1 &&
                q.watch_days == this.ARRIVE_MAX_DAYS && q.offset == -1 &&
                q.expected_cost == 0
        if (q.op == "flow")
            return q.vehicle >= 0 && q.order_index == -1 &&
                q.expected_cost == 0 && q.watch_days == -1 &&
                q.offset >= 0 && CargoFlow2FlowOffsetOk(q)
        /* finance / finish: the tail echoes the vehicle identity and its
         * planned tail ladder step only (the planned table's own tail
         * economy day). */
        return q.vehicle >= 0 && q.order_index == -1 && q.order_flags == -1 &&
            q.watch_days == -1 && q.offset >= 0 &&
            CargoFlow2TailOffsetOk(q) && q.expected_cost == 0
    }

    /* Corridor-pin defence in depth: a drifted pin echo (or a ladder-step
     * echo that does not equal its planned value) is stale admission; at
     * the site exchange it is the INVALID_SITE refusal of record. */
    function CargoFlow2PinsDrifted(q) {
        if (q.pickup != this.pickup || q.delivery != this.delivery ||
            q.depot != this.depot_tile) return true
        local idx = CargoFlow2PlannedIndex(q)
        if (idx >= 0 && CargoFlow2PlannedOffset(idx) != q.offset) return true
        return false
    }

    /* The live vehicle identity check every post-purchase exchange makes
     * against the built engine and vehicle. */
    function VehicleReady(q) {
        return this.vehicle_id >= 0 &&
            GSVehicle.IsValidVehicle(this.vehicle_id) &&
            GSVehicle.IsPrimaryVehicle(this.vehicle_id) &&
            GSVehicle.GetOwner(this.vehicle_id) == q.company &&
            q.engine == this.ENGINE_PIN && q.engine == this.engine_id &&
            q.vehicle == this.vehicle_id &&
            q.pickup == this.pickup && q.delivery == this.delivery &&
            q.depot == this.depot_tile
    }

    /* One tested native quote for one engine at the depot: the fixed-demo
     * test-mode pattern (BuildVehicle answers 0 on success in test mode). */
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
     * admitted corridor cargo. */
    function VState(company) {
        local v = vehicle_id
        return {
            owner = GSVehicle.GetOwner(v),
            engine = GSVehicle.GetEngineType(v),
            location = GSVehicle.GetLocation(v),
            capacity = GSVehicle.GetCapacity(v, CARGOFLOW2_CARGO),
            state_int = GSVehicle.GetState(v),
            in_depot = GSVehicle.IsInDepot(v),
            speed = GSVehicle.GetCurrentSpeed(v),
            load = GSVehicle.GetCargoLoad(v, CARGOFLOW2_CARGO),
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

    /* The observation instant of record: a guarded clock read every
     * success frame attaches. */
    function Instant(r) {
        local tick = GetTick()
        if (tick < 0 || tick > 2147483647) throw "D5_NATIVE_FACT"
        local day = GSDate.GetCurrentDate()
        if (day < 0 || day > 2147483647) throw "D5_NATIVE_FACT"
        r.tick <- tick
        r.day <- day
        return [tick, day]
    }

    function Income(q) {
        local income = GSCompany.GetQuarterlyIncome(
            q.company, GSCompany.CURRENT_QUARTER)
        if (income < -2147483648 || income > 2147483647) throw "D5_NATIVE_FACT"
        return income
    }

    /* Strip every observation field from a half-read reply: the wire
     * refuses a spoofed hybrid, so a refusal frame carries no observation
     * set at all. */
    function StripObservations(r) {
        foreach (name in this.observation_fields) {
            if (name in r) delete r[name]
        }
    }

    /* -- op: site re-pin (pure observation, zero cost) ----------------------- */
    function SiteOp(q, r) {
        /* The tile predicates of the join consult the per-instance current
         * road type; a fresh instance starts at INVALID_ROADTYPE and a
         * GSRoad tile predicate fails closed (script_road.cpp), so the
         * road type of record is pinned first (the freight v2 Handle
         * idiom, T-006 root cause of the INVALID_SITE halt). */
        GSRoad.SetCurrentRoadType(GSRoad.ROADTYPE_ROAD)
        /* Re-pin gate: the corridor station/industry identity of record is
         * re-derived from the live world before anything else observes it
         * (any drift is the INVALID_SITE refusal of record). */
        if (GSStation.GetStationID(this.pickup) != this.PICKUP_SID ||
            GSStation.GetStationID(this.delivery) != this.BAY_SID ||
            !GSStation.IsValidStation(this.PICKUP_SID) ||
            !GSStation.IsValidStation(this.BAY_SID) ||
            !GSIndustry.IsValidIndustry(this.PICKUP_IND) ||
            !GSIndustry.IsValidIndustry(this.BAY_IND) ||
            !GSRoad.IsRoadDepotTile(this.depot_tile)) {
            r.status = "INVALID_SITE"
            return
        }
        local instant = Instant(r)
        local income = Income(q)
        r.cargo <- CARGOFLOW2_CARGO
        r.pickup_sid <- this.PICKUP_SID
        r.bay_sid <- this.BAY_SID
        r.pickup_industry <- this.PICKUP_IND
        r.bay_industry <- this.BAY_IND
        r.income <- income
        r.status = "READY"
    }

    /* -- op: pinned engine admission (observation, zero cost) --------------- */
    function EngineOp(q, r) {
        if (this.engine_id >= 0 || this.vehicle_id >= 0) {
            r.status = "STALE_ADMISSION"
            return
        }
        local pinned = q.engine
        if (pinned != this.ENGINE_PIN) {
            r.status = "ENGINE_PIN_MISMATCH"
            return
        }
        /* F-10: no enumeration fallback. The request's pinned id is the
         * admitted identity; a buildable fact is the one availability
         * gate — a non-buildable pin is UNAVAILABLE_ENGINE, never a
         * lowest-compatible substitute. */
        if (!GSEngine.IsBuildable(pinned)) {
            r.status = "UNAVAILABLE_ENGINE"
            return
        }
        /* The pinned census admission of record (§5.2): cargo 1,
         * capacity 20, price 4429, max_speed 48 and the running-cost
         * display figure 421 (the E111 correction: the script surface
         * returns the display figure directly, so the comparison applies
         * no second shift; the ≤2^31 sanity guard stays fail-closed).
         * Any other world refuses outright. */
        local cargo = GSEngine.GetCargoType(pinned)
        local capacity = GSEngine.GetCapacity(pinned)
        local price = GSEngine.GetPrice(pinned)
        local speed = GSEngine.GetMaxSpeed(pinned)
        local display = GSEngine.GetRunningCost(pinned)
        if (cargo < 0 || capacity < 0 || price < 0 || speed < 0 ||
            display < 1 || display > 2147483647) throw "D5_NATIVE_FACT"
        if (cargo != CARGOFLOW2_CARGO || capacity != this.CAPACITY_PIN ||
            price != this.ENGINE_QUOTE || speed != this.SPEED_PIN ||
            display != this.RUNNING_DISPLAY_PIN) {
            r.status = "ENGINE_PIN_MISMATCH"
            return
        }
        local instant = Instant(r)
        local income = Income(q)
        r.cargo <- cargo
        r.capacity <- capacity
        r.price <- price
        r.max_speed <- speed
        r.running_cost <- display
        r.income <- income
        r.status = "READY"
        this.engine_id = pinned
        this.engine_quote = price
    }

    /* -- op: purchase (one test-equal re-quote, one real BuildVehicle) ------ */
    function PurchaseOp(q, r) {
        if (this.vehicle_id >= 0 ||
            this.engine_id < 0 || this.engine_quote != this.ENGINE_QUOTE ||
            q.engine != this.ENGINE_PIN ||
            q.expected_cost != this.engine_quote) {
            r.status = "STALE_ADMISSION"
            return
        }
        local funds = GSCompany.GetBankBalance(q.company)
        if (funds < -2147483648 || funds > 2147483647) throw "D5_NATIVE_FACT"
        local quote = QuoteBuild(q.engine)
        if (!quote[0] || quote[1] <= 0) {
            r.status = "UNAVAILABLE_ENGINE"
            return
        }
        if (quote[1] != q.expected_cost) {
            r.status = "COST_CHANGED"
            return
        }
        if (quote[1] > q.max_cost) {
            r.status = "COST_LIMIT"
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
        if (!GSVehicle.IsValidVehicle(built)) throw "D5_NATIVE_FACT"
        if (cost != quote[1]) {
            r.status = "COST_CHANGED"
            return
        }
        local after = GSCompany.GetBankBalance(q.company)
        if (funds - after != cost) {
            r.status = "READBACK_MISMATCH"
            return
        }
        /* The built frame's funds echo is the post-debit level at the same
         * instant (the model reconciles the pre-debit level beside it). */
        if (after < -2147483648 || after > 2147483647) throw "D5_NATIVE_FACT"
        r.funds = after
        r.cost = cost
        local instant = Instant(r)
        local income = Income(q)
        r.income <- income
        r.vehicle = built
        r.status = "BUILT"
        this.vehicle_id = built
    }

    /* -- op: independent vehicle readback (pure observation, zero cost) ----- */
    function VReadOp(q, r) {
        if (!VehicleReady(q)) {
            r.status = "STALE_ADMISSION"
            return
        }
        local obs = VState(q.company)
        if (obs.owner != q.company || obs.capacity < 0 || obs.speed < 0 ||
            obs.load < 0 || obs.location < 0 || obs.location > 65535 ||
            obs.in_depot == null) {
            r.status = "UNSUPPORTED_NATIVE_FACT"
            return
        }
        /* The built identity re-pins itself: the vehicle must still be the
         * admitted engine (a swapped one is a readback mismatch). */
        if (obs.engine != this.ENGINE_PIN) {
            r.status = "READBACK_MISMATCH"
            return
        }
        r.funds = obs.funds
        local instant = Instant(r)
        local income = Income(q)
        r.owner <- obs.owner
        r.location <- obs.location
        r.capacity <- obs.capacity
        r.cargo <- CARGOFLOW2_CARGO
        r.state <- StateName(obs.state_int)
        r.in_depot <- obs.in_depot
        r.speed <- obs.speed
        r.load <- obs.load
        r.income <- income
        r.status = "READ"
    }

    /* -- op: order appends (stop TILES of the re-pinned site, pinned flags) -- */
    function OrderOp(q, r) {
        if (GSGame.IsPaused()) {
            r.status = "PAUSED"
            return
        }
        if (!VehicleReady(q)) {
            r.status = "STALE_ADMISSION"
            return
        }
        /* N1 (15.3, E92): the append takes the stop TILE and stores the
         * station the tile resolves to; the readback is tile-form and is
         * deepened with the resolved station identity. */
        local dest = q.order_index == 0 ? this.pickup : this.delivery
        /* N2: the real 15.x flag values (OF_NONE then OF_NO_LOAD). */
        local flags = q.order_index == 0 ? this.OF_NONE : this.OF_NO_LOAD
        local expected_sid = q.order_index == 0 ? this.PICKUP_SID : this.BAY_SID
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
        if (d != dest || GSStation.GetStationID(d) != expected_sid ||
            f != flags || g != true) {
            r.status = "READBACK_MISMATCH"
            return
        }
        r.funds = GSCompany.GetBankBalance(q.company)
        local instant = Instant(r)
        local income = Income(q)
        r.dest <- dest
        r.flags <- f
        r.goto <- g
        r.income <- income
        r.status = "ORDERED"
    }

    /* -- op: exact order inventory (tile destinations, real flag values) ---- */
    function OrderReadOp(q, r) {
        if (!VehicleReady(q)) {
            r.status = "STALE_ADMISSION"
            return
        }
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
        /* N1 (15.3, E92): the inventory readback is tile-form, deepened
         * with each tile's resolved station identity; the flags are the
         * real appended values, both goto-station. */
        if (d0 != this.pickup ||
            GSStation.GetStationID(d0) != this.PICKUP_SID ||
            f0 != this.OF_NONE || g0 != true ||
            d1 != this.delivery ||
            GSStation.GetStationID(d1) != this.BAY_SID ||
            f1 != this.OF_NO_LOAD || g1 != true) {
            r.status = "READBACK_MISMATCH"
            return
        }
        r.funds = GSCompany.GetBankBalance(q.company)
        local instant = Instant(r)
        local income = Income(q)
        r.order_len <- count
        r.dest0 <- d0
        r.flags0 <- f0
        r.goto0 <- g0
        r.dest1 <- d1
        r.flags1 <- f1
        r.goto1 <- g1
        r.income <- income
        r.status = "ORDER_SET_VERIFIED"
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
        local pickup = GSCargoMonitor.GetIndustryPickupAmount(
            q.company, CARGOFLOW2_CARGO, this.PICKUP_IND, true)
        local delivery = GSCargoMonitor.GetIndustryDeliveryAmount(
            q.company, CARGOFLOW2_CARGO, this.BAY_IND, true)
        if (pickup < 0 || delivery < 0) throw "D5_NATIVE_FACT"
        /* A nonzero pre-start monitor baseline is a refused observation
         * set, never a claimed ARMED state. */
        if (pickup != 0 || delivery != 0) {
            r.status = "READBACK_MISMATCH"
            return
        }
        r.funds = GSCompany.GetBankBalance(q.company)
        local instant = Instant(r)
        local income = Income(q)
        r.pickup_amount <- pickup
        r.delivery_amount <- delivery
        r.income <- income
        r.status = "ARMED"
        this.monitor_armed = true
    }

    /* -- op: start (the one start command of the attempt) -------------------- */
    function StartOp(q, r) {
        if (GSGame.IsPaused()) {
            r.status = "PAUSED"
            return
        }
        if (!VehicleReady(q)) {
            r.status = "STALE_ADMISSION"
            return
        }
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
        r.funds = GSCompany.GetBankBalance(q.company)
        local instant = Instant(r)
        local income = Income(q)
        r.state <- state
        r.speed <- speed
        r.income <- income
        r.status = "STARTED"
    }

    /* -- op: the bounded first-arrival watch (the ladder anchor of record) --- */
    function ArriveWatchOp(q, r) {
        if (!VehicleReady(q)) {
            r.status = "STALE_ADMISSION"
            return
        }
        if (this.cargoflow_anchor != null) {
            /* The anchor is latched exactly once, at the first arrival. */
            r.status = "STALE_ADMISSION"
            return
        }
        local prev = GetTick()
        if (prev < 0 || prev > 2147483647) throw "D5_NATIVE_FACT"
        local samples = 0
        for (;;) {
            if (GSGame.IsPaused()) {
                r.status = "PAUSED"
                return
            }
            if (samples > 0) {
                Sleep(1)
                local now = GetTick()
                /* A stalled or regressing clock in the flight window is
                 * this watch's own terminal timeout, never a retry. */
                if (now <= prev) {
                    r.status = "ARRIVE_TIMEOUT"
                    return
                }
                prev = now
            }
            local day = GSDate.GetCurrentDate()
            if (day < 0 || day > 2147483647) throw "D5_NATIVE_FACT"
            /* The 5-economy-day bound of record: timeout by day 712233,
             * fail-closed on the tick ceiling too. */
            if (day > this.ARRIVE_DEADLINE || samples >= this.WAIT_MAX_TICKS) {
                r.status = "ARRIVE_TIMEOUT"
                return
            }
            local loc = GSVehicle.GetLocation(this.vehicle_id)
            if (loc < 0 || loc > 65535) throw "D5_NATIVE_FACT"
            if (loc == this.pickup) {
                local load = GSVehicle.GetCargoLoad(this.vehicle_id, CARGOFLOW2_CARGO)
                if (load < 0 || load > 2147483647) throw "D5_NATIVE_FACT"
                /* The pinned empty load of record: the selector was
                 * closed before this arrival (§5.2 item 2). */
                if (load != 0) {
                    r.status = "READBACK_MISMATCH"
                    return
                }
                local tick = GetTick()
                r.funds = GSCompany.GetBankBalance(q.company)
                if (r.funds < -2147483648 || r.funds > 2147483647)
                    throw "D5_NATIVE_FACT"
                local income = Income(q)
                /* The anchor of record is the arrival instant's own day;
                 * the anchored arrival carries its own latch. */
                this.cargoflow_anchor = day
                local latch = {
                    kind = "arrival_pickup", day = day, tick = tick,
                    cargo = load
                }
                r.anchor <- day
                r.location <- loc
                r.load <- load
                r.latches <- [latch]
                r.tick <- tick
                r.day <- day
                r.income <- income
                r.status = "ANCHORED"
                return
            }
            samples++
        }
    }

    /* -- op: one ladder step of the flow sample set (§5.4) ------------------- */
    function FlowOp(q, r) {
        if (!VehicleReady(q)) {
            r.status = "STALE_ADMISSION"
            return
        }
        local anchor = this.cargoflow_anchor
        if (anchor == null) {
            /* The ladder never starts without its anchor (§5.3). */
            r.status = "STALE_ADMISSION"
            return
        }
        local target = anchor + q.offset
        /* Dual enforcement of the delivered day authority, package side:
         * any ladder step whose target day exceeds the authority refuses
         * before any wait. */
        if (target > this.AUTHORITY_LAST_DAY) {
            r.status = "AUTHORITY_EXCEEDED"
            return
        }
        /* The in-package wait latches the cycle events of record (§5.3):
         * every arrival at either stop, every load/departure with its
         * load count and every unload with its delivered amount, each
         * with its own (day, tick). */
        local latches = []
        local prev = GetTick()
        if (prev < 0 || prev > 2147483647) throw "D5_NATIVE_FACT"
        local prev_loc = GSVehicle.GetLocation(this.vehicle_id)
        local prev_load = GSVehicle.GetCargoLoad(this.vehicle_id, CARGOFLOW2_CARGO)
        if (prev_loc < 0 || prev_loc > 65535 || prev_load < 0 ||
            prev_load > 2147483647) throw "D5_NATIVE_FACT"
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
                    /* Tick regression: the window echo of record carries
                     * exactly the ladder clock (flow only). */
                    r.anchor <- anchor
                    r.tick <- now
                    r.day <- GSDate.GetCurrentDate()
                    r.status = "CLOCK_STALLED"
                    return
                }
                prev = now
            }
            local day = GSDate.GetCurrentDate()
            if (day < 0 || day > 2147483647) throw "D5_NATIVE_FACT"
            local loc = GSVehicle.GetLocation(this.vehicle_id)
            local load = GSVehicle.GetCargoLoad(this.vehicle_id, CARGOFLOW2_CARGO)
            if (loc < 0 || loc > 65535 || load < 0 || load > 2147483647)
                throw "D5_NATIVE_FACT"
            /* Per-tick event latching (edges only, never truncated). */
            if (loc == this.pickup && prev_loc != this.pickup) {
                if (latches.len() >= this.LATCH_LIMIT) {
                    r.status = "LATCH_OVERFLOW"
                    return
                }
                latches.append({ kind = "arrival_pickup", day = day, tick = prev,
                                 cargo = load })
            } else if (loc == this.delivery && prev_loc != this.delivery) {
                if (latches.len() >= this.LATCH_LIMIT) {
                    r.status = "LATCH_OVERFLOW"
                    return
                }
                latches.append({ kind = "arrival_bay", day = day, tick = prev,
                                 cargo = load })
            }
            if (loc == this.pickup && load > prev_load) {
                if (latches.len() >= this.LATCH_LIMIT) {
                    r.status = "LATCH_OVERFLOW"
                    return
                }
                latches.append({ kind = "load", day = day, tick = prev,
                                 cargo = load })
            }
            if (prev_loc == this.pickup && loc != this.pickup && load > 0) {
                if (latches.len() >= this.LATCH_LIMIT) {
                    r.status = "LATCH_OVERFLOW"
                    return
                }
                latches.append({ kind = "departure", day = day, tick = prev,
                                 cargo = load })
            }
            if (loc == this.delivery && load < prev_load) {
                if (latches.len() >= this.LATCH_LIMIT) {
                    r.status = "LATCH_OVERFLOW"
                    return
                }
                latches.append({ kind = "unload", day = day, tick = prev,
                                 cargo = prev_load - load })
            }
            prev_loc = loc
            prev_load = load
            if (day == target) break
            if (day > target) {
                /* The clock already passed this step's planned day between
                 * exchanges: the exact ladder cannot be measured anymore;
                 * fail closed with the honest window echo. */
                r.anchor <- anchor
                r.tick <- prev
                r.day <- day
                r.status = "WINDOW_EXHAUSTED"
                return
            }
            if (samples >= this.WAIT_MAX_TICKS) {
                r.anchor <- anchor
                r.tick <- prev
                r.day <- day
                r.status = "WINDOW_EXHAUSTED"
                return
            }
            samples++
        }
        /* Post-wait observation instant of record (§4.5): the funds echo
         * reads after the wait, at the ladder's own day. The vehicle echo
         * re-reads in the same instant (no tick passes between these
         * reads and the calendar features below). */
        local funds = GSCompany.GetBankBalance(q.company)
        if (funds < -2147483648 || funds > 2147483647) throw "D5_NATIVE_FACT"
        r.funds = funds
        local tick = GetTick()
        if (tick < 0 || tick > 2147483647) throw "D5_NATIVE_FACT"
        local day = GSDate.GetCurrentDate()
        if (day != target) throw "D5_NATIVE_FACT"
        local loc = GSVehicle.GetLocation(this.vehicle_id)
        local load = GSVehicle.GetCargoLoad(this.vehicle_id, CARGOFLOW2_CARGO)
        if (loc < 0 || loc > 65535 || load < 0 || load > 2147483647)
            throw "D5_NATIVE_FACT"
        /* The calendar features of record (the 15.3 1-based month facts). */
        local year = GSDate.GetYear(day)
        if (year < 0 || year > 2147483647) throw "D5_NATIVE_FACT"
        local month = GSDate.GetMonth(day)
        if (month < 1 || month > 12) throw "D5_NATIVE_FACT"
        local day_of_month = GSDate.GetDayOfMonth(day)
        if (day_of_month < 1 || day_of_month > 31) throw "D5_NATIVE_FACT"
        /* The accepted pile of the producing pickup industry stays the
         * pinned -1 non-producer fact on every sample (§5.2 item 4): any
         * other value refuses the exchange fail-closed. */
        local stock_p = GSIndustry.GetStockpiledCargo(this.PICKUP_IND, CARGOFLOW2_CARGO)
        if (stock_p == -1) {
            GSLog.Info("D5_CARGOFLOW2_STOCK_NOT_ACCEPTED " + this.PICKUP_IND)
        } else {
            throw "D5_NATIVE_FACT"
        }
        local stock_b = GSIndustry.GetStockpiledCargo(this.BAY_IND, CARGOFLOW2_CARGO)
        if (stock_b == -1) {
            GSLog.Info("D5_CARGOFLOW2_STOCK_NOT_ACCEPTED " + this.BAY_IND)
        } else if (stock_b < 0 || stock_b > 65535) {
            throw "D5_NATIVE_FACT"
        }
        /* The station waiting family at both stops (totals plus the two
         * per-source forms the 15.3 API allows). A negative here is a
         * stale station/cargo fact: refused. */
        local wait_p = GSStation.GetCargoWaiting(this.PICKUP_SID, CARGOFLOW2_CARGO)
        if (wait_p < 0 || wait_p > 2147483647) throw "D5_NATIVE_FACT"
        local wait_p0 = GSStation.GetCargoWaitingFrom(
            this.PICKUP_SID, this.PICKUP_SID, CARGOFLOW2_CARGO)
        if (wait_p0 < 0 || wait_p0 > 2147483647) throw "D5_NATIVE_FACT"
        local wait_p2 = GSStation.GetCargoWaitingFrom(
            this.PICKUP_SID, this.BAY_SID, CARGOFLOW2_CARGO)
        if (wait_p2 < 0 || wait_p2 > 2147483647) throw "D5_NATIVE_FACT"
        local wait_b = GSStation.GetCargoWaiting(this.BAY_SID, CARGOFLOW2_CARGO)
        if (wait_b < 0 || wait_b > 2147483647) throw "D5_NATIVE_FACT"
        local wait_b0 = GSStation.GetCargoWaitingFrom(
            this.BAY_SID, this.PICKUP_SID, CARGOFLOW2_CARGO)
        if (wait_b0 < 0 || wait_b0 > 2147483647) throw "D5_NATIVE_FACT"
        local wait_b2 = GSStation.GetCargoWaitingFrom(
            this.BAY_SID, this.BAY_SID, CARGOFLOW2_CARGO)
        if (wait_b2 < 0 || wait_b2 > 2147483647) throw "D5_NATIVE_FACT"
        /* The station planned family (the per-month flows of record). */
        local count_p = GSStation.GetCargoPlanned(this.PICKUP_SID, CARGOFLOW2_CARGO)
        if (count_p < 0 || count_p > 2147483647) throw "D5_NATIVE_FACT"
        local count_b = GSStation.GetCargoPlanned(this.BAY_SID, CARGOFLOW2_CARGO)
        if (count_b < 0 || count_b > 2147483647) throw "D5_NATIVE_FACT"
        local pl_p0 = GSStation.GetCargoPlannedFrom(
            this.PICKUP_SID, this.PICKUP_SID, CARGOFLOW2_CARGO)
        if (pl_p0 < 0 || pl_p0 > 2147483647) throw "D5_NATIVE_FACT"
        local pl_p2 = GSStation.GetCargoPlannedFrom(
            this.PICKUP_SID, this.BAY_SID, CARGOFLOW2_CARGO)
        if (pl_p2 < 0 || pl_p2 > 2147483647) throw "D5_NATIVE_FACT"
        local pl_b0 = GSStation.GetCargoPlannedFrom(
            this.BAY_SID, this.PICKUP_SID, CARGOFLOW2_CARGO)
        if (pl_b0 < 0 || pl_b0 > 2147483647) throw "D5_NATIVE_FACT"
        local pl_b2 = GSStation.GetCargoPlannedFrom(
            this.BAY_SID, this.BAY_SID, CARGOFLOW2_CARGO)
        if (pl_b2 < 0 || pl_b2 > 2147483647) throw "D5_NATIVE_FACT"
        /* The monthly production machine's own verdict (both industries):
         * -1 rides verbatim exactly as the census measured the acceptor's
         * non-producer fact (E65). */
        local prod_p = GSIndustry.GetLastMonthProduction(
            this.PICKUP_IND, CARGOFLOW2_CARGO)
        if (prod_p == -1) {
            GSLog.Info("D5_CARGOFLOW2_NON_PRODUCER " + this.PICKUP_IND)
        } else if (prod_p < 0 || prod_p > 2147483647) {
            throw "D5_NATIVE_FACT"
        }
        local prod_b = GSIndustry.GetLastMonthProduction(
            this.BAY_IND, CARGOFLOW2_CARGO)
        if (prod_b == -1) {
            GSLog.Info("D5_CARGOFLOW2_NON_PRODUCER " + this.BAY_IND)
        } else if (prod_b < 0 || prod_b > 2147483647) {
            throw "D5_NATIVE_FACT"
        }
        local trans_p = GSIndustry.GetLastMonthTransported(
            this.PICKUP_IND, CARGOFLOW2_CARGO)
        if (trans_p == -1) {
            GSLog.Info("D5_CARGOFLOW2_NON_TRANSPORT_LOG " + this.PICKUP_IND)
        } else if (trans_p < 0 || trans_p > 2147483647) {
            throw "D5_NATIVE_FACT"
        }
        local trans_b = GSIndustry.GetLastMonthTransported(
            this.BAY_IND, CARGOFLOW2_CARGO)
        if (trans_b == -1) {
            GSLog.Info("D5_CARGOFLOW2_NON_TRANSPORT_LOG " + this.BAY_IND)
        } else if (trans_b < 0 || trans_b > 2147483647) {
            throw "D5_NATIVE_FACT"
        }
        /* The vehicle echo and the exchange-boundary income/delivered
         * reads complete the sample set (§5.4). */
        local in_depot = GSVehicle.IsInDepot(this.vehicle_id)
        local speed = GSVehicle.GetCurrentSpeed(this.vehicle_id)
        if (speed < 0 || in_depot == null) throw "D5_NATIVE_FACT"
        local income = Income(q)
        local delivered = GSCompany.GetQuarterlyCargoDelivered(
            q.company, GSCompany.CURRENT_QUARTER)
        if (delivered < 0 || delivered > 2147483647) throw "D5_NATIVE_FACT"
        r.anchor <- anchor
        r.tick <- tick
        r.day <- day
        r.year <- year
        r.month <- month
        r.day_of_month <- day_of_month
        r.stock_pickup <- stock_p
        r.stock_bay <- stock_b
        r.wait_pickup <- wait_p
        r.wait_pickup_from0 <- wait_p0
        r.wait_pickup_from1 <- wait_p2
        r.wait_bay <- wait_b
        r.wait_bay_from0 <- wait_b0
        r.wait_bay_from1 <- wait_b2
        r.count_pickup <- count_p
        r.count_bay <- count_b
        r.planned_pickup_from0 <- pl_p0
        r.planned_pickup_from1 <- pl_p2
        r.planned_bay_from0 <- pl_b0
        r.planned_bay_from1 <- pl_b2
        r.prod_pickup <- prod_p
        r.prod_bay <- prod_b
        r.trans_pickup <- trans_p
        r.trans_bay <- trans_b
        r.location <- loc
        r.load <- load
        r.in_depot <- in_depot
        r.speed <- speed
        r.delivered <- delivered
        r.latches <- latches
        r.income <- income
        r.status = "READY"
    }

    /* -- op: finance corroboration (income/delivered/accepted, tail offset) -- */
    function FinanceOp(q, r) {
        if (!VehicleReady(q) || !this.monitor_armed ||
            this.cargoflow_anchor == null) {
            r.status = "STALE_ADMISSION"
            return
        }
        if (this.cargoflow_anchor + this.CargoFlow2TailStep()
            > this.AUTHORITY_LAST_DAY) {
            r.status = "AUTHORITY_EXCEEDED"
            return
        }
        local day = GSDate.GetCurrentDate()
        if (day != this.cargoflow_anchor + this.CargoFlow2TailStep()) {
            r.status = "READBACK_MISMATCH"
            return
        }
        local tick = GetTick()
        if (tick < 0 || tick > 2147483647) throw "D5_NATIVE_FACT"
        local delivered = GSCompany.GetQuarterlyCargoDelivered(
            q.company, GSCompany.CURRENT_QUARTER)
        if (delivered < 0 || delivered > 2147483647) throw "D5_NATIVE_FACT"
        /* The bay industry's raw accepted date of record: the 15.3 native
         * returns the raw date int, -1 when the cargo was never accepted. */
        local last_accepted = GSIndustry.GetCargoLastAcceptedDate(
            this.BAY_IND, CARGOFLOW2_CARGO)
        if (last_accepted < -1 || last_accepted > 2147483647)
            throw "D5_NATIVE_FACT"
        r.funds = GSCompany.GetBankBalance(q.company)
        if (r.funds < -2147483648 || r.funds > 2147483647) throw "D5_NATIVE_FACT"
        local income = Income(q)
        r.tick <- tick
        r.day <- day
        r.anchor <- this.cargoflow_anchor
        r.delivered <- delivered
        r.last_accepted <- last_accepted
        r.income <- income
        r.status = "FINANCE_VERIFIED"
    }

    /* -- op: finish (the certified cleanup evidence; no stop command) -------- */
    function FinishOp(q, r) {
        if (!VehicleReady(q) || this.cargoflow_anchor == null) {
            r.status = "STALE_ADMISSION"
            return
        }
        if (this.cargoflow_anchor + this.CargoFlow2TailStep()
            > this.AUTHORITY_LAST_DAY) {
            r.status = "AUTHORITY_EXCEEDED"
            return
        }
        local day = GSDate.GetCurrentDate()
        if (day != this.cargoflow_anchor + this.CargoFlow2TailStep()) {
            r.status = "READBACK_MISMATCH"
            return
        }
        local tick = GetTick()
        if (tick < 0 || tick > 2147483647) throw "D5_NATIVE_FACT"
        local state_int = GSVehicle.GetState(this.vehicle_id)
        local speed = GSVehicle.GetCurrentSpeed(this.vehicle_id)
        local in_depot = GSVehicle.IsInDepot(this.vehicle_id)
        if (speed < 0 || in_depot == null) throw "D5_NATIVE_FACT"
        r.funds = GSCompany.GetBankBalance(q.company)
        if (r.funds < -2147483648 || r.funds > 2147483647) throw "D5_NATIVE_FACT"
        local income = Income(q)
        /* The two-order loop keeps running beneath the ladder's end (§6
         * item 7): this attempt's schedule issues no command, so the
         * stop_issued echo is false of record, never a claimed stop. */
        r.tick <- tick
        r.day <- day
        r.anchor <- this.cargoflow_anchor
        r.state <- StateName(state_int)
        r.speed <- speed
        r.in_depot <- in_depot
        r.stop_issued <- false
        r.income <- income
        r.status = "PHASE_STOPPED"
    }

    function CargoFlow2Guard(r) {
        if (r.funds < -2147483648 || r.funds > 2147483647 || r.cost < 0 ||
            r.cost > 2147483647) throw "D5_RESPONSE_OUT_OF_BOUNDS"
        if (r.offset < -1 || r.offset > 60) throw "D5_RESPONSE_OUT_OF_BOUNDS"
        foreach (name in ["anchor", "tick", "day", "year"]) {
            if (!(name in r)) continue
            local v = r[name]
            if (v < 0 || v > 2147483647) throw "D5_RESPONSE_OUT_OF_BOUNDS"
        }
        if ("month" in r && (r.month < 1 || r.month > 12))
            throw "D5_RESPONSE_OUT_OF_BOUNDS"
        if ("day_of_month" in r && (r.day_of_month < 1 || r.day_of_month > 31))
            throw "D5_RESPONSE_OUT_OF_BOUNDS"
        /* The -1 allowance is the 15.3 native fact for a measured industry
         * family without a produced/accepted slot for the cargo (E65);
         * every other negative stays out of the response domain. The
         * stockpiles are uint16 piles (capped 65535). */
        if ("stock_pickup" in r && (r.stock_pickup > 65535 ||
            (r.stock_pickup < 0 && r.stock_pickup != -1)))
            throw "D5_RESPONSE_OUT_OF_BOUNDS"
        if ("stock_bay" in r && (r.stock_bay > 65535 ||
            (r.stock_bay < 0 && r.stock_bay != -1)))
            throw "D5_RESPONSE_OUT_OF_BOUNDS"
        foreach (name in ["wait_pickup", "wait_pickup_from0",
                          "wait_pickup_from1", "wait_bay",
                          "wait_bay_from0", "wait_bay_from1",
                          "count_pickup", "count_bay",
                          "planned_pickup_from0", "planned_pickup_from1",
                          "planned_bay_from0", "planned_bay_from1"]) {
            if (!(name in r)) continue
            local v = r[name]
            if (v < 0 || v > 2147483647) throw "D5_RESPONSE_OUT_OF_BOUNDS"
        }
        foreach (name in ["prod_pickup", "prod_bay",
                          "trans_pickup", "trans_bay"]) {
            if (!(name in r)) continue
            local v = r[name]
            if (v > 2147483647 || (v < 0 && v != -1))
                throw "D5_RESPONSE_OUT_OF_BOUNDS"
        }
        foreach (name in ["location", "dest0", "dest1", "dest"]) {
            if (!(name in r)) continue
            local v = r[name]
            if (typeof v != "integer" || v < 0 || v > 65535)
                throw "D5_RESPONSE_OUT_OF_BOUNDS"
        }
        if ("state" in r && typeof r.state != "string")
            throw "D5_RESPONSE_OUT_OF_BOUNDS"
        foreach (name in ["in_depot", "goto0", "goto1", "goto", "stop_issued"]) {
            if (!(name in r)) continue
            if (typeof r[name] != "bool") throw "D5_RESPONSE_OUT_OF_BOUNDS"
        }
        foreach (name in ["speed", "load", "capacity", "pickup_amount",
                          "delivery_amount", "delivered"]) {
            if (!(name in r)) continue
            local v = r[name]
            if (v < 0 || v > 2147483647) throw "D5_RESPONSE_OUT_OF_BOUNDS"
        }
        if ("cargo" in r && (r.cargo < 0 || r.cargo > 63))
            throw "D5_RESPONSE_OUT_OF_BOUNDS"
        if ("owner" in r && (r.owner < -1 || r.owner > 65535))
            throw "D5_RESPONSE_OUT_OF_BOUNDS"
        if ("running_cost" in r && (r.running_cost < 1 || r.running_cost > 2147483647))
            throw "D5_RESPONSE_OUT_OF_BOUNDS"
        if ("order_len" in r && (r.order_len < 0 || r.order_len > 65535))
            throw "D5_RESPONSE_OUT_OF_BOUNDS"
        foreach (name in ["flags0", "flags1", "flags"]) {
            if (!(name in r)) continue
            if (r[name] < 0 || r[name] > 255) throw "D5_RESPONSE_OUT_OF_BOUNDS"
        }
        if ("last_accepted" in r && (r.last_accepted < -1 ||
            r.last_accepted > 2147483647)) throw "D5_RESPONSE_OUT_OF_BOUNDS"
        /* The engine/site re-pin echoes the Python model does not declare
         * yet (site sids/industries, engine price/max_speed): guarded
         * locally so no out-of-domain value ever leaves the package. */
        foreach (name in ["pickup_sid", "bay_sid", "pickup_industry",
                          "bay_industry"]) {
            if (!(name in r)) continue
            local v = r[name]
            if (v < 0 || v > 65535) throw "D5_RESPONSE_OUT_OF_BOUNDS"
        }
        foreach (name in ["price", "max_speed"]) {
            if (!(name in r)) continue
            local v = r[name]
            if (v < 0 || v > 2147483647) throw "D5_RESPONSE_OUT_OF_BOUNDS"
        }
        /* The latch rows of record: kind literal, own instant, count. */
        if ("latches" in r) {
            local rows = r.latches
            if (typeof rows != "array" || rows.len() > this.LATCH_LIMIT)
                throw "D5_RESPONSE_OUT_OF_BOUNDS"
            foreach (row in rows) {
                if (typeof row != "table" || !("kind" in row) ||
                    !("day" in row) || !("tick" in row) || !("cargo" in row) ||
                    typeof row.kind != "string" ||
                    (row.kind != "arrival_pickup" && row.kind != "arrival_bay" &&
                     row.kind != "load" && row.kind != "departure" &&
                     row.kind != "unload") ||
                    row.day < 0 || row.day > 2147483647 ||
                    row.tick < 0 || row.tick > 2147483647 ||
                    row.cargo < 0 || row.cargo > 2147483647)
                    throw "D5_RESPONSE_OUT_OF_BOUNDS"
            }
        }
    }

    function CargoFlow2Handle(q) {
        if (!("op" in q) || typeof q.op != "string" ||
            !CargoFlow2OpAllowed(q.op)) return
        if (!("request_id" in q) || typeof q.request_id != "string" ||
            q.request_id.len() < 1 || q.request_id.len() > 32 ||
            !IdShape(q.request_id)) return
        if (!("plan" in q) || typeof q.plan != "string" || !Hex64(q.plan)) return
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
        /* Every request echoes the full correlation stride; a payload the
         * Python contract could never build is silently dropped. */
        if (!("engine" in q) || !("vehicle" in q) ||
            !("expected_cost" in q) || !("order_index" in q) ||
            !("order_flags" in q) || !("watch_days" in q) ||
            !("offset" in q)) return
        if (!CargoFlow2EchoOk(q)) return
        /* One-shot budget accounting: unique request ids, the 32-request
         * cap; a duplicate id or an exhausted budget is silently dropped. */
        if (used == null) used = {}
        if (q.request_id in used || this.requests >= this.max_requests) return
        used[q.request_id] <- true
        this.requests++
        local r = {
            protocol = 11, op = q.op, request_id = q.request_id, plan = q.plan,
            company = q.company, max_cost = q.max_cost, pickup = q.pickup,
            delivery = q.delivery, depot = q.depot, engine = q.engine,
            vehicle = q.vehicle, expected_cost = q.expected_cost,
            order_index = q.order_index, order_flags = q.order_flags,
            watch_days = q.watch_days, offset = q.offset,
            status = "OUT_OF_ORDER",
            funds = 0, cost = 0
        }
        /* The offset echo attaches before the refusal ladder (the survey-6
         * precedent): refusals carry the echoes, never the data. */
        local idx = CargoFlow2PlannedIndex(q)
        if (idx < 0 || idx != this.cargoflow_stage || this.cargoflow_halted) {
            r.status = "OUT_OF_ORDER"
        } else if (this.plan_id != null && this.plan_id != q.plan) {
            r.status = "OUT_OF_ORDER"
        } else if (GSCompany.ResolveCompanyID(q.company) != q.company ||
                   q.company != CARGOFLOW2_COMPANY) {
            r.status = "INVALID_COMPANY"
        } else if (CargoFlow2PinsDrifted(q)) {
            r.status = q.op == "site" ? "INVALID_SITE" : "STALE_ADMISSION"
        } else {
            if (this.plan_id == null) this.plan_id = q.plan
            if (GSGame.IsPaused()) {
                r.status = "PAUSED"
            } else {
                try {
                    local company = GSCompanyMode(q.company)
                    if (!GSCompanyMode.IsValid()) {
                        r.status = "INVALID_COMPANY"
                    } else {
                        /* Every reply carries the bank balance at the
                         * exchange boundary; the waiting ops below
                         * re-read it at their own post-wait instant. */
                        r.funds = GSCompany.GetBankBalance(q.company)
                        if (q.op == "site") {
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
                        } else if (q.op == "arrive-watch") {
                            ArriveWatchOp(q, r)
                        } else if (q.op == "flow") {
                            FlowOp(q, r)
                        } else if (q.op == "finance") {
                            FinanceOp(q, r)
                        } else if (q.op == "finish") {
                            FinishOp(q, r)
                        }
                    }
                } catch (error) {
                    /* The inner native error text is evidence: logged with
                     * the exchange label before the refusal status. The
                     * echo prelude of a half-read exchange is data, never
                     * echo language: the refusal frame of record carries
                     * none of the observation set (any watch/window echo
                     * included — the strip is the one discipline all
                     * prompts share). */
                    GSLog.Info("D5_CARGOFLOW2_THROW " + q.request_id + " " +
                        (typeof error == "string" ? error : typeof error))
                    StripObservations(r)
                    r.status = "UNSUPPORTED_NATIVE_FACT"
                }
            }
        }
        CargoFlow2Guard(r)
        if (!GSAdmin.Send(r)) throw "D5_RESPONSE_SEND_FAILED"
        GSLog.Info("D5_CARGOFLOW2 " + q.request_id + " " + r.status)
        /* Schedule accounting: only the exact planned status of the planned
         * exchange advances the stage; every other terminal status halts
         * the schedule prefix-preservingly. Evidence, never retries. */
        if (idx >= 0) {
            if (r.status == cargoflow2_planned[idx][3]) {
                if (idx == this.cargoflow_stage && !this.cargoflow_halted)
                    this.cargoflow_stage = idx + 1
            } else {
                this.cargoflow_halted = true
            }
        }
    }

    function Handle(q) {
        if (typeof q != "table") return
        if (!("protocol" in q)) return
        /* Protocol 11 is the cargo-flow delivery attempt; this package
         * carries no other protocol family of any kind. */
        if (q.protocol != 11) return
        CargoFlow2Handle(q)
    }

    function Start() {
        GSLog.Info("D5_CARGOFLOW2_READY")
        while (true) {
            while (GSEventController.IsEventWaiting()) {
                local event = GSEventController.GetNextEvent()
                if (event.GetEventType() == GSEvent.ET_ADMIN_PORT)
                    Handle(GSEventAdminPort.Convert(event).GetObject())
            }
            Sleep(1)
        }
    }

    /* Squirrel char-code forms of the request-shape helpers the whole
     * package family shares (copied verbatim from the frozen census
     * package source so the guard semantics stay byte-comparable). */
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
}

/* Save-restore identity bridge: the retained frozen-source.zip info.nut
 * declares CreateInstance() returning "NetworkFreightProof". This subclass
 * satisfies that contract without modifying any retained identity byte. */
class NetworkFreightProof extends D5CargoFlow2Proof {
}
