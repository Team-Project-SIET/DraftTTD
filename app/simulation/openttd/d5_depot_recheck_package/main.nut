/* Separate bounded observe-only depot reload handler (protocol 10).
 * Additive: no existing frozen package is modified, imported or replaced.
 * The D5-F12-DEPOT-RELOAD-1 attempt (the round-3 recheck of the Path A
 * design record) reloads the retained authoritative post-mutation world of
 * record — the consumed D5-F12-DEPOT-3 candidate's saved ``after.sav`` —
 * and re-measures the freight-relevant facts through the depot observe
 * instrument: GSRoad.IsRoadDepotTile / GetRoadDepotFrontTile / GetOwner /
 * IsRoadTile / AreRoadTilesConnected over the pinned depot tile 45487 and
 * its front 45743.
 *
 * The observe subset carries no mutating dispatch of any kind: demolish,
 * road, depot and fleet handlers are absent by construction, no game
 * command is ever issued, no readback cost is ever nonzero and the funds
 * rows carry the balance at the exchange boundary only. The reload cannot
 * and must not save: the world of record stays the staged authoritative
 * depot after-save before and after this attempt.
 *
 * The handler mirrors the depot mutation package's proven guard machinery
 * field for field minus every mutating op: corridor identity pins, the
 * one-shot 32-request dispatcher accounting (unique ids — this package is
 * staged alone; the attempt of record carries exactly one planned
 * exchange), the plan digest latch and the prefix-preserving halt
 * discipline. Every reply carries the bank balance at the exchange
 * boundary and the zero cost of record (an observe readback can never
 * spend). The wire ``max_cost`` echo stays the depot contract's forced
 * attempt echo (3000) exactly as the pinned protocol-10 nonce of record —
 * the recheck's own attempt-level spend ceiling is zero Python-side and
 * no spend-capable op exists in this package's handler set. The one
 * planned exchange (``reload-00``, observe) is a fixed-fact gate of
 * record: Python compares every measured fact against the round-2
 * binding's transcribed facts-of-record (the E82 after-00 measurement)
 * and refuses any divergence STALE_PIN-preservingly.
 *
 * Save-restore identity: the retained frozen-source.zip info.nut declares
 * CreateInstance() returning "NetworkFreightProof"; the empty bridge
 * subclass at the end satisfies that contract without modifying any
 * retained identity byte. */

class D5DepotRecheckProof extends GSController {
    /* Schedule state: `recheck_stage` is the index of the one planned
     * exchange that may run next; `recheck_halted` stops every later
     * exchange after any success frame failed to produce its exact planned
     * status. */
    recheck_stage = 0
    recheck_halted = false
    /* One-shot dispatcher budget accounting (unique ids, the shared
     * 32-request family cap; the attempt of record carries one planned
     * exchange and binds requests = 1 Python-side). */
    requests = 0
    used = null
    /* Latched prelaunch plan digest: the first accepted exchange fixes the
     * attempt's plan identity; every later exchange must match it. */
    plan_id = null

    /* Baked corridor identity pins of the consumed D4/A1/depot lineage
     * (the same pins every protocol-5/6/9/10 exchange echoes; the reload
     * never touches an unpinned tile — it touches no tile at all). */
    pickup = 45748
    delivery = 50351
    depot_tile = 45487
    depot_front_tile = 45743
    /* Fixed corridor identity for the recheck session. */
    DEPOT_RECHECK_COMPANY = 0
    DEPOT_RECHECK_CARGO = 1
    /* The wire echo of record (the depot contract's forced attempt echo):
     * identical on the one request echo and rejected in every other
     * figure; the recheck's own spend ceiling is zero and no spend-capable
     * op exists in this handler. */
    MAX_DEPOT_MUTATION_COST = 3000
    /* The bounded fleet diagnostic budget stays a shared-family guard
     * constant; the observe-only recheck can never ride it (no fleet op
     * exists, and the wire never carries fleet fields on observe). */
    MAX_FLEET_ROWS = 4
    /* 1 planned exchange, plus dispatcher budget slack only through unique
     * ids: request 33 is the first one the dispatcher drops. */
    max_requests = 32

    /* The fixed one-exchange reload schedule: [request_id, op, success
     * status], numbered in the Python contract's recheck schedule order.
     * The reload gate runs alone so a drifted world is caught at the one
     * exchange itself; nothing follows it in this package. */
    recheck_planned = [
        ["reload-00", "observe", "READY"]
    ]

    /* The observe-only recheck carries no command op of any kind. */
    function RecheckOpAllowed(op) {
        return op == "observe"
    }

    function RecheckPlannedIndex(q) {
        for (local i = 0; i < recheck_planned.len(); i++)
            if (recheck_planned[i][0] == q.request_id && recheck_planned[i][1] == q.op) return i
        return -1
    }

    /* -- the v2 ObserveDepot fact set (the depot/edge instrument,
     *    verbatim from the depot mutation package's sparse observation) —
     *    ------------------------------------------------------------- */
    /* Raw reads for the observe op. front_read/owner keep the native -1
     * invalid fact (GSRoad.GetRoadDepotFrontTile's INVALID_TILE and
     * GSTile.GetOwner's COMPANY_INVALID share it); the fixed-fact
     * comparison of record refuses it, never relabels it. */
    function RecheckObserveFacts(company) {
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

    function RecheckObserveOp(q, r) {
        local facts = this.RecheckObserveFacts(q.company)
        r.depot_present <- facts.depot
        r.front_read <- facts.front_read
        r.owner <- facts.owner
        r.depot_linked <- facts.linked
        r.connected_front_to_depot <- facts.cfd
        r.connected_depot_to_front <- facts.dtf
        /* The observe readback never spends: the cost of record stays the
         * default zero and the funds carry the balance at the exchange
         * boundary only (set by the guard ladder below). */
        r.status = "READY"
    }

    /* -- the depot guard machinery, field for field ----------------------- */
    /* Every reply field is bounded before it can ever reach the wire; the
     * mirror is kept complete minus nothing that can arrive (the observe
     * subset can never carry count/vehicle rows, and this guard keeps
     * refusing them if any table ever tries). */
    function RecheckGuard(r) {
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

    function RecheckHandle(q) {
        if (!("op" in q) || typeof q.op != "string" || !RecheckOpAllowed(q.op)) return
        if (!("request_id" in q) || typeof q.request_id != "string" ||
            q.request_id.len() < 1 || q.request_id.len() > 32 ||
            !IdShape(q.request_id)) return
        if (!("plan" in q) || typeof q.plan != "string" || !Hex64(q.plan)) return
        if (!("company" in q) || typeof q.company != "integer" ||
            q.company < 0 || q.company > 14) return
        /* The wire echo of record is baked: only the pinned depot-contract
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
        /* The sparse observations carry no tile and no front tile: the wire
         * serializes the absence itself. An observe request that carries a
         * non-null tile echo of any kind is dropped (the reload never
         * touches a tile); a missing or null key is the native absence. */
        if (("tile" in q && q.tile != null) ||
            ("front_tile" in q && q.front_tile != null)) return
        /* One-shot budget accounting: unique request ids, the 32-request
         * family cap; a duplicate id or an exhausted budget is silently
         * dropped. */
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
        local idx = RecheckPlannedIndex(q)
        if (idx < 0 || idx != this.recheck_stage || this.recheck_halted) {
            r.status = "OUT_OF_ORDER"
        } else if (this.plan_id != null && this.plan_id != q.plan) {
            r.status = "OUT_OF_ORDER"
        } else if (GSCompany.ResolveCompanyID(q.company) != q.company ||
                   q.company != this.DEPOT_RECHECK_COMPANY) {
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
                        /* The funds of the reload readback: the balance at
                         * the exchange boundary of the loaded world of
                         * record; the observe op never spends, so the cost
                         * of record stays the default zero. */
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
                        } else {
                            this.RecheckObserveOp(q, r)
                        }
                    }
                } catch (error) {
                    /* The inner native error text is evidence: logged with
                     * the exchange label before the refusal status, so the
                     * retained session's stderr carries the exact thrown
                     * fact and the readback never needs to. */
                    GSLog.Info("D5_F12_DEPOT_RECHECK_THROW " + q.request_id + " " +
                        (typeof error == "string" ? error : typeof error))
                    r.status = "UNSUPPORTED_NATIVE_FACT"
                }
            }
        }
        RecheckGuard(r)
        if (!GSAdmin.Send(r)) throw "D5_RESPONSE_SEND_FAILED"
        GSLog.Info("D5_F12_DEPOT_RECHECK " + q.request_id + " " + r.status)
        /* Reload schedule accounting: only the exact READY status of the
         * one planned exchange advances the stage; every other terminal
         * status halts the recheck prefix-preservingly. Evidence, never
         * retries. */
        if (idx >= 0) {
            if (r.status == recheck_planned[idx][2]) {
                if (idx == this.recheck_stage && !this.recheck_halted) this.recheck_stage = idx + 1
            } else {
                this.recheck_halted = true
            }
        }
    }

    function Handle(q) {
        if (typeof q != "table") return
        if (!("protocol" in q)) return
        /* Protocol 10 is the depot family's schema; the recheck package
         * carries no other protocol family of any kind. */
        if (q.protocol != 10) return
        RecheckHandle(q)
    }

    function Start() {
        GSLog.Info("D5_F12_DEPOT_RECHECK_READY")
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
class NetworkFreightProof extends D5DepotRecheckProof {
}