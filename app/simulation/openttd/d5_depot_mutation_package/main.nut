/* Separate bounded native depot-connectivity mutation handler (protocol 10).
 * Additive: no existing frozen package is modified or imported. The
 * D5-F12-DEPOT attempt carries the E58 §2.1 prescribed world fix over the
 * consumed A1 close-out world: demolish the pinned depot 45487, lay the
 * 2-tile road pair 45743 <-> 45487 (the span API needs start != end and
 * building road pieces into a standing depot tile is refuted), then
 * rebuild the depot at 45487 against its pinned front 45743 (the depot
 * build auto-clears the S bit the road pair laid on 45487 via
 * CMD_LANDSCAPE_CLEAR; the N stub persists on 45743). Exactly three
 * cost-bearing mutating ops exist — GSTile.DemolishTile, GSRoad.BuildRoad,
 * GSRoad.BuildRoadDepot — each pinned to D4's depot tile 45487 and its
 * front 45743, and exactly two sparse observation ops: the v2
 * ObserveDepot fact set (observe) and the company's primary vehicles
 * through GSVehicleList (fleet). Orders, station, refit, selling,
 * second-vehicle, terraform, save and purchase commands are absent by
 * construction. The depot tile and front of every mutating exchange are
 * re-observed immediately before the one command dispatch; any drift
 * stops the phase with STALE_PIN and preserves the verified prefix.
 *
 * The handler mirrors the proven protocol-6/9 guards field for field:
 * corridor identity pins, the one-shot 32-request budget accounting
 * (unique ids — this package is staged alone), the plan_id latch and the
 * prefix-preserving halt discipline. Every reply carries the bank balance
 * at the exchange boundary and a signed cost of record
 * (cost = GetBankBalance before - after; a demolish refund class may
 * credit, so cost may be negative); the funds chain
 * funds_after == funds_before - cost is checked Python-side against the
 * pinned A1 close-out opening level. The attempt-level max_cost ceiling
 * is 3000 and every request must echo exactly that budget; any other
 * figure is dropped before accounting. The before/after observe exchanges
 * are fixed-fact gates of record (the E58 diagnosis and its prescribed
 * resolution); the fleet exchange demands the retained zero fleet, so the
 * v2 plan model's vacuous in_depot clause (every cycle ends in the depot)
 * stands satisfied because no vehicle exists to report one.
 *
 * Save-restore identity: the retained frozen-source.zip info.nut declares
 * CreateInstance() returning "NetworkFreightProof"; the empty bridge
 * subclass at the end satisfies that contract without modifying any
 * retained identity byte. */

class D5DepotMutationProof extends GSController {
    /* Schedule state: `depot_stage` is the index of the one planned
     * exchange that may run next; `depot_halted` stops every later
     * exchange after any success frame failed to produce its exact planned
     * status. */
    depot_stage = 0
    depot_halted = false
    /* One-shot dispatcher budget accounting (unique ids, 32-request cap). */
    requests = 0
    used = null
    /* Latched prelaunch plan digest: the first accepted exchange fixes the
     * attempt's plan identity; every later exchange must match it. */
    plan_id = null

    /* Baked corridor identity pins of the consumed D4/A1 lineage (the same
     * pins every protocol-5/6/9 exchange echoes; the mutation never
     * touches an unpinned tile). */
    pickup = 45748
    delivery = 50351
    depot_tile = 45487
    depot_front_tile = 45743
    /* Fixed corridor identity for the mutation session. */
    DEPOT_COMPANY = 0
    DEPOT_CARGO = 1
    /* The attempt-level cost ceiling of record (E58 §2.1); identical on
     * every request echo and rejected in every other figure. */
    MAX_DEPOT_MUTATION_COST = 3000
    /* The bounded fleet diagnostic budget (the D5 world's retained fact is
     * the zero fleet; four rows cap a halt record, never a runaway dump —
     * a larger fleet is an unsupported native fact, which halts anyway). */
    MAX_FLEET_ROWS = 4
    /* 6 planned exchanges, plus dispatcher slack only through unique ids:
     * request 33 is the first one the dispatcher drops. */
    max_requests = 32

    /* The fixed six-exchange mutation schedule: [request_id, op, success
     * status], the same order the Python contract's
     * DEPOT_MUTATION_EXCHANGE_IDS pins. The before gate runs first so a
     * drifted world is caught before any command; the three prescribed
     * mutations follow in the E58 §2.1 order; the after gate and the
     * fleet gate close the phase. */
    depot_planned = [
        ["before-00", "observe", "READY"],
        ["demo-00", "demolish", "READY"],
        ["road-00", "road", "READY"],
        ["depot-00", "depot", "READY"],
        ["after-00", "observe", "READY"],
        ["fleet-00", "fleet", "READY"]
    ]

    function DepotOpAllowed(op) {
        return op == "observe" || op == "demolish" || op == "road" ||
            op == "depot" || op == "fleet"
    }

    function DepotPlannedIndex(q) {
        for (local i = 0; i < depot_planned.len(); i++)
            if (depot_planned[i][0] == q.request_id && depot_planned[i][1] == q.op) return i
        return -1
    }

    /* -- the v2 ObserveDepot fact set (the depot/edge instrument) ---------- */
    /* Raw reads for the observe op and for every mutating exchange's
     * pre-dispatch precondition re-observation. front_read/owner keep the
     * native -1 invalid fact (GSRoad.GetRoadDepotFrontTile's INVALID_TILE
     * and GSTile.GetOwner's COMPANY_INVALID share it); the fixed-fact
     * gates refuse it, never relabel it. */
    function DepotObserveFacts(company) {
        local depot = GSRoad.IsRoadDepotTile(this.depot_tile)
        local front_read = depot ? GSRoad.GetRoadDepotFrontTile(this.depot_tile) : -1
        local owner = depot ? GSTile.GetOwner(this.depot_tile) : -1
        /* Ownership and the front tile alone never prove the vehicle can
         * enter the depot; the entry bit must read connected
         * front-to-depot AND depot-to-front (the F-12 instrument). */
        local linked = depot && front_read == this.depot_front_tile &&
            GSTile.GetOwner(this.depot_tile) == company &&
            GSTile.GetOwner(this.depot_front_tile) == company &&
            GSRoad.IsRoadTile(this.depot_front_tile)
        local cfd = false
        local dtf = false
        if (linked) {
            cfd = GSRoad.AreRoadTilesConnected(this.depot_front_tile, this.depot_tile)
            dtf = GSRoad.AreRoadTilesConnected(this.depot_tile, this.depot_front_tile)
        }
        return {depot = depot, front_read = front_read, owner = owner,
            linked = linked, cfd = cfd, dtf = dtf}
    }

    function DepotObserveOp(q, r) {
        local facts = this.DepotObserveFacts(q.company)
        r.depot_present <- facts.depot
        r.front_read <- facts.front_read
        r.owner <- facts.owner
        r.depot_linked <- facts.linked
        r.connected_front_to_depot <- facts.cfd
        r.connected_depot_to_front <- facts.dtf
        r.status = "READY"
    }

    /* -- op: demolish (E58 §2.1 step 1) ----------------------------------- */
    function DepotDemolishOp(q, r) {
        /* Pre-dispatch precondition re-observation, STALE_PIN on drift,
         * before any command: the E58 pre-fix diagnosis verbatim — the
         * standing depot with its pinned front, owned by this company,
         * and the missing stub on BOTH directions. */
        local facts = this.DepotObserveFacts(q.company)
        if (!facts.depot || facts.front_read != this.depot_front_tile ||
            facts.owner != this.DEPOT_COMPANY || !facts.linked ||
            facts.cfd || facts.dtf) {
            r.status = "STALE_PIN"
            return
        }
        local funds_before = GSCompany.GetBankBalance(q.company)
        if (!GSTile.DemolishTile(this.depot_tile)) throw "D5_NATIVE_FACT"
        local funds_after = GSCompany.GetBankBalance(q.company)
        r.cost = funds_before - funds_after
        r.funds = funds_after
        r.status = "READY"
    }

    /* -- op: road (E58 §2.1 step 2: the missing stub) ---------------------- */
    function DepotRoadOp(q, r) {
        /* Pre-dispatch precondition re-observation, STALE_PIN on drift,
         * before any command: the depot is gone and its tile is bare; the
         * stub is still missing in both directions. */
        if (GSRoad.IsRoadDepotTile(this.depot_tile) ||
            GSRoad.IsRoadTile(this.depot_tile) ||
            GSRoad.AreRoadTilesConnected(this.depot_front_tile, this.depot_tile)) {
            r.status = "STALE_PIN"
            return
        }
        if (!GSRoad.IsRoadTypeAvailable(GSRoad.ROADTYPE_ROAD)) throw "D5_NATIVE_FACT"
        GSRoad.SetCurrentRoadType(GSRoad.ROADTYPE_ROAD)
        local funds_before = GSCompany.GetBankBalance(q.company)
        if (!GSRoad.BuildRoad(this.depot_tile, this.depot_front_tile)) throw "D5_NATIVE_FACT"
        local funds_after = GSCompany.GetBankBalance(q.company)
        r.cost = funds_before - funds_after
        r.funds = funds_after
        r.status = "READY"
    }

    /* -- op: depot (E58 §2.1 step 3: the rebuild against its stub) --------- */
    function DepotDepotOp(q, r) {
        /* Pre-dispatch precondition re-observation, STALE_PIN on drift,
         * before any command: the road pair carries the stub (front side
         * reads connected both ways), the target tile is a bare road
         * piece of this company. */
        if (GSRoad.IsRoadDepotTile(this.depot_tile) ||
            !GSRoad.IsRoadTile(this.depot_tile) ||
            !GSRoad.AreRoadTilesConnected(this.depot_front_tile, this.depot_tile)) {
            r.status = "STALE_PIN"
            return
        }
        if (!GSRoad.IsRoadTypeAvailable(GSRoad.ROADTYPE_ROAD)) throw "D5_NATIVE_FACT"
        GSRoad.SetCurrentRoadType(GSRoad.ROADTYPE_ROAD)
        local funds_before = GSCompany.GetBankBalance(q.company)
        /* The depot build rides CMD_LANDSCAPE_CLEAR on the target tile in
         * the non-rotate path (road_cmd.cpp), so the S bit the road pair
         * laid there is auto-cleared and the door bit replaces it; the N
         * stub persists on the front. */
        if (!GSRoad.BuildRoadDepot(this.depot_tile, this.depot_front_tile))
            throw "D5_NATIVE_FACT"
        local funds_after = GSCompany.GetBankBalance(q.company)
        r.cost = funds_before - funds_after
        r.funds = funds_after
        r.status = "READY"
    }

    /* -- op: fleet (the zero-fleet gate) ----------------------------------- */
    function DepotFleetOp(r) {
        local list = GSVehicleList()
        local count = list.Count()
        /* The row budget is a response bound, never a truncation: a fleet
         * larger than the pinned diagnostic budget is an unsupported
         * native fact (the phase halts on it either way via the Python
         * zero-fleet gate). */
        if (count < 0 || count > 65535 || count > MAX_FLEET_ROWS) throw "D5_NATIVE_FACT"
        local rows = []
        foreach (vid, _ in list) {
            local tile = GSVehicle.GetLocation(vid)
            local in_depot = GSVehicle.IsInDepot(vid)
            if (tile < 0 || tile > 65535 || in_depot == null) throw "D5_NATIVE_FACT"
            rows.append({id = vid, tile = tile, in_depot = in_depot})
        }
        r.count <- count
        r.vehicles <- rows
        r.status = "READY"
    }

    function DepotGuard(r) {
        if (r.funds < -2147483648 || r.funds > 2147483647 ||
            r.cost < -2147483648 || r.cost > 2147483647)
            throw "D5_RESPONSE_OUT_OF_BOUNDS"
        if ("tile" in r && (r.tile < 0 || r.tile > 65535)) throw "D5_RESPONSE_OUT_OF_BOUNDS"
        if ("front_tile" in r && (r.front_tile < 0 || r.front_tile > 65535))
            throw "D5_RESPONSE_OUT_OF_BOUNDS"
        if ("depot_present" in r && typeof r.depot_present != "bool" ||
            "depot_linked" in r && typeof r.depot_linked != "bool" ||
            "connected_front_to_depot" in r && typeof r.connected_front_to_depot != "bool" ||
            "connected_depot_to_front" in r && typeof r.connected_depot_to_front != "bool")
            throw "D5_RESPONSE_OUT_OF_BOUNDS"
        if ("front_read" in r && (r.front_read < -1 || r.front_read > 65535))
            throw "D5_RESPONSE_OUT_OF_BOUNDS"
        if ("owner" in r && (r.owner < -1 || r.owner > 255)) throw "D5_RESPONSE_OUT_OF_BOUNDS"
        if ("count" in r && (r.count < 0 || r.count > 65535)) throw "D5_RESPONSE_OUT_OF_BOUNDS"
        if ("vehicles" in r) {
            if (typeof r.vehicles != "array" || r.vehicles.len() > MAX_FLEET_ROWS)
                throw "D5_RESPONSE_OUT_OF_BOUNDS"
            foreach (row in r.vehicles) {
                if (typeof row != "table" || !("id" in row) || !("tile" in row) ||
                    !("in_depot" in row) || typeof row.in_depot != "bool" ||
                    row.id < 0 || row.id > 65535 || row.tile < 0 || row.tile > 65535)
                    throw "D5_RESPONSE_OUT_OF_BOUNDS"
            }
        }
    }

    function DepotHandle(q) {
        if (!("op" in q) || typeof q.op != "string" || !DepotOpAllowed(q.op)) return
        if (!("request_id" in q) || typeof q.request_id != "string" ||
            q.request_id.len() < 1 || q.request_id.len() > 32 ||
            !IdShape(q.request_id)) return
        if (!("plan" in q) || typeof q.plan != "string" || !Hex64(q.plan)) return
        if (!("company" in q) || typeof q.company != "integer" ||
            q.company < 0 || q.company > 14) return
        /* The attempt ceiling of record is baked: only the pinned 3000
         * echo is accounted, everything else is dropped. */
        if (!("max_cost" in q) || typeof q.max_cost != "integer" ||
            q.max_cost != MAX_DEPOT_MUTATION_COST) return
        if (!("pickup" in q) || typeof q.pickup != "integer" ||
            q.pickup < 0 || q.pickup > 65535 ||
            !("delivery" in q) || typeof q.delivery != "integer" ||
            q.delivery < 0 || q.delivery > 65535 ||
            !("depot" in q) || typeof q.depot != "integer" ||
            q.depot < 0 || q.depot > 65535 ||
            q.pickup == q.delivery || q.depot == q.pickup ||
            q.depot == q.delivery) return
        /* tile (and, for road/depot, front_tile) are required (integers in
         * map bounds) on the mutating ops exactly and null on the sparse
         * observations; the native span API needs start != end. The wire
         * serializes their absence. */
        if (!("tile" in q)) return
        if (q.op == "demolish" || q.op == "road" || q.op == "depot") {
            if (typeof q.tile != "integer" || q.tile < 0 || q.tile > 65535) return
        } else if (q.tile != null) return
        if (!("front_tile" in q)) return
        if (q.op == "road" || q.op == "depot") {
            if (typeof q.front_tile != "integer" || q.front_tile < 0 ||
                q.front_tile > 65535 || q.front_tile == q.tile) return
        } else if (q.front_tile != null) return
        /* One-shot budget accounting: unique request ids, the 32-request
         * cap; a duplicate id or an exhausted budget is silently dropped. */
        if (used == null) used = {}
        if (q.request_id in used || this.requests >= this.max_requests) return
        used[q.request_id] <- true
        this.requests++
        local r = {
            protocol = 10, op = q.op, request_id = q.request_id, plan = q.plan,
            company = q.company, max_cost = q.max_cost, pickup = q.pickup,
            delivery = q.delivery, depot = q.depot, status = "OUT_OF_ORDER",
            funds = 0, cost = 0
        }
        /* The tile (and front-tile) echoes attach before the refusal
         * ladder (the census precedence): refusals carry the echoes, never
         * the data. */
        if (q.op == "demolish" || q.op == "road" || q.op == "depot") r.tile <- q.tile
        if (q.op == "road" || q.op == "depot") r.front_tile <- q.front_tile
        local idx = DepotPlannedIndex(q)
        if (idx < 0 || idx != this.depot_stage || this.depot_halted) {
            r.status = "OUT_OF_ORDER"
        } else if (this.plan_id != null && this.plan_id != q.plan) {
            r.status = "OUT_OF_ORDER"
        } else if (GSCompany.ResolveCompanyID(q.company) != q.company ||
                   q.company != this.DEPOT_COMPANY) {
            r.status = "INVALID_COMPANY"
        } else if (q.pickup != this.pickup || q.delivery != this.delivery ||
                   q.depot != this.depot_tile) {
            r.status = "STALE_PIN"
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
                        /* The funds default: the balance at the exchange
                         * boundary for every observation op; the mutating
                         * ops overwrite both funds and cost with the
                         * measured before/after arithmetic. */
                        r.funds = GSCompany.GetBankBalance(q.company)
                        /* The per-script road context every ScriptRoad probe
                         * fail-closes on (15.3 script_storage initializes it
                         * INVALID_ROADTYPE; E72 root cause): set + assert
                         * before any probe, the D4/D5-v2 per-request pattern
                         * verbatim. */
                        GSRoad.SetCurrentRoadType(GSRoad.ROADTYPE_ROAD)
                        if (GSRoad.GetCurrentRoadType() != 0 ||
                            !GSRoad.IsRoadTypeAvailable(0)) {
                            r.status = "UNSUPPORTED_NATIVE_FACT"
                        } else if (q.op == "observe") {
                            this.DepotObserveOp(q, r)
                        } else if (q.op == "demolish") {
                            this.DepotDemolishOp(q, r)
                        } else if (q.op == "road") {
                            this.DepotRoadOp(q, r)
                        } else if (q.op == "depot") {
                            this.DepotDepotOp(q, r)
                        } else {
                            this.DepotFleetOp(r)
                        }
                    }
                } catch (error) {
                    /* The inner native error text is evidence: logged with
                     * the exchange label before the refusal status, so the
                     * retained session's stderr carries the exact thrown
                     * fact and the readback never needs to. */
                    GSLog.Info("D5_F12_DEPOT_THROW " + q.request_id + " " +
                        (typeof error == "string" ? error : typeof error))
                    r.status = "UNSUPPORTED_NATIVE_FACT"
                }
            }
        }
        DepotGuard(r)
        if (!GSAdmin.Send(r)) throw "D5_RESPONSE_SEND_FAILED"
        GSLog.Info("D5_F12_DEPOT " + q.request_id + " " + r.status)
        /* Mutation schedule accounting: only the exact READY status of the
         * planned exchange advances the stage; every other terminal status
         * halts the phase prefix-preservingly. Evidence, never retries. */
        if (idx >= 0) {
            if (r.status == depot_planned[idx][2]) {
                if (idx == this.depot_stage && !this.depot_halted) this.depot_stage = idx + 1
            } else {
                this.depot_halted = true
            }
        }
    }

    function Handle(q) {
        if (typeof q != "table") return
        if (!("protocol" in q)) return
        /* Protocol 10 is the depot-connectivity mutation phase; the depot
         * mutation package carries no other protocol family of any kind. */
        if (q.protocol != 10) return
        DepotHandle(q)
    }

    function Start() {
        GSLog.Info("D5_F12_DEPOT_READY")
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
     * package family shares (copied verbatim from the frozen freight
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
class NetworkFreightProof extends D5DepotMutationProof {
}
