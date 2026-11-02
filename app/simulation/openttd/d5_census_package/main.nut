/* Separate bounded native corridor box-census handler (protocol 9).
 * Additive: no existing frozen package is modified or imported. The census
 * is strictly read-only — every operation is observation in company mode
 * (GSStation.GetCoverageRadius, GSTile.GetCargoAcceptance,
 * GSIndustry.GetLastMonthProduction, GSIndustry.IsCargoAccepted,
 * GSIndustry.GetIndustryID) and there is no cost-bearing or mutation-
 * capable command of any kind. Demolition, terraforming, road, station,
 * depot, orders, purchase, vehicle and save commands are absent by
 * construction.
 *
 * The handler mirrors the proven protocol-6 SurveyHandle guards field for
 * field: corridor identity pins, the one-shot 32-request budget accounting
 * (unique ids shared only in spirit — this package is staged alone), the
 * plan_id latch and the prefix-preserving halt discipline. Its own work is
 * the box scan of record, mirroring the v2 site gate's DiscoveryBoxes
 * exactly: a fresh radius read, the tile box around the pinned centre in
 * DiscoveryBoxes iteration order (dy outer, dx inner, ascending tile), one
 * row per distinct industry {id, tile = minimum member tile, p, a}, page
 * slices ascending by industry id on the static cursor grid 0/3/6, a
 * READY-empty drained page, and an overflow kept as an explicit finding —
 * the v2 gate's own exactly-one enforcement is never reproduced here; the
 * census measures, it does not admit.
 *
 * Save-restore identity: the retained frozen-source.zip info.nut declares
 * CreateInstance() returning "NetworkFreightProof"; the empty bridge
 * subclass at the end satisfies that contract without modifying any
 * retained identity byte. */

class D5CensusProof extends GSController {
    /* Schedule state: `census_stage` is the index of the one planned
     * exchange that may run next; `census_halted` stops every later
     * exchange after any success frame failed to produce its exact planned
     * status. */
    census_stage = 0
    census_halted = false
    /* One-shot dispatcher budget accounting (unique ids, 32-request cap). */
    requests = 0
    used = null
    /* Latched prelaunch plan digest: the first accepted exchange fixes the
     * attempt's plan identity; every later exchange must match it. */
    plan_id = null

    /* Baked corridor identity pins of the consumed D4/A1 lineage (the same
     * pins every protocol-5/6 exchange echoes; the census never queries an
     * unpinned tile). */
    pickup = 45748
    delivery = 50351
    depot_tile = 45487
    /* Box scan centres of record: the v2 pickup stop (producer box) and the
     * A1 bay stop 50862 that the E58 design re-pins as the D5-FREIGHT-4
     * delivery stop (acceptor box). */
    PBOX_CENTRE = 45748
    DBOX_CENTRE = 50862
    /* The pinned chain-continuity spot tiles (E49 re-measures). */
    SPOT_CONTROL = 50351
    SPOT_STOP = 50862
    /* Fixed corridor identity for the census session. */
    CENSUS_COMPANY = 0
    CENSUS_CARGO = 1
    CENSUS_PROD_INDUSTRY = 0
    /* Page geometry of record (E59 §3.1). */
    MAX_PAGE_ROWS = 3
    /* 10 planned exchanges, plus dispatcher slack only through unique ids:
     * request 33 is the first one the dispatcher drops. */
    max_requests = 32

    /* The fixed ten-exchange census schedule: [request_id, op, success
     * status], the same order the Python contract's CENSUS_EXCHANGE_IDS
     * pins. Spots run first so a wrong-world load is caught before any box
     * row is trusted; box pages follow. */
    census_planned = [
        ["radius-00", "radius", "READY"],
        ["acc-00", "accept", "READY"],
        ["acc-01", "accept", "READY"],
        ["prod-00", "prod", "READY"],
        ["pbox-00", "box", "READY"],
        ["pbox-01", "box", "READY"],
        ["pbox-02", "box", "READY"],
        ["dbox-00", "box", "READY"],
        ["dbox-01", "box", "READY"],
        ["dbox-02", "box", "READY"]
    ]

    function CensusOpAllowed(op) {
        return op == "radius" || op == "accept" || op == "prod" || op == "box"
    }

    function CensusPlannedIndex(q) {
        for (local i = 0; i < census_planned.len(); i++)
            if (census_planned[i][0] == q.request_id && census_planned[i][1] == q.op) return i
        return -1
    }

    function SpotPinned(tile) {
        return tile == SPOT_CONTROL || tile == SPOT_STOP
    }

    function BoxPinned(tile) {
        return tile == PBOX_CENTRE || tile == DBOX_CENTRE
    }

    function CensusGuard(r) {
        if (r.funds < -2147483648 || r.funds > 2147483647 || r.cost < 0 ||
            r.cost > 2147483647) throw "D5_RESPONSE_OUT_OF_BOUNDS"
        if ("tile" in r && (r.tile < 0 || r.tile > 65535)) throw "D5_RESPONSE_OUT_OF_BOUNDS"
        if ("cursor" in r && (r.cursor < 0 || r.cursor > 65535)) throw "D5_RESPONSE_OUT_OF_BOUNDS"
        if ("radius" in r && (r.radius < 0 || r.radius > 255)) throw "D5_RESPONSE_OUT_OF_BOUNDS"
        if ("accept" in r && (r.accept < 0 || r.accept > 8)) throw "D5_RESPONSE_OUT_OF_BOUNDS"
        if ("prod" in r && (r.prod < 0 || r.prod > 2147483647)) throw "D5_RESPONSE_OUT_OF_BOUNDS"
        if ("count" in r && (r.count < 0 || r.count > 65535)) throw "D5_RESPONSE_OUT_OF_BOUNDS"
        if ("more" in r && typeof r.more != "bool") throw "D5_RESPONSE_OUT_OF_BOUNDS"
        if ("rows" in r) {
            if (typeof r.rows != "array" || r.rows.len() > MAX_PAGE_ROWS)
                throw "D5_RESPONSE_OUT_OF_BOUNDS"
            foreach (row in r.rows) {
                if (typeof row != "table" || !("id" in row) || !("tile" in row) ||
                    !("p" in row) || !("a" in row)) throw "D5_RESPONSE_OUT_OF_BOUNDS"
                if (row.id < 0 || row.id > 65535 || row.tile < 0 || row.tile > 65535 ||
                    row.p < 0 || row.p > 2147483647 || row.a < 0 || row.a > 2)
                    throw "D5_RESPONSE_OUT_OF_BOUNDS"
            }
        }
    }

    /* -- op: radius (pure observation, zero cost) --------------------------- */
    function CensusRadiusOp(r) {
        local radius = GSStation.GetCoverageRadius(GSStation.STATION_TRUCK_STOP)
        if (radius < 0 || radius > 255) throw "D5_NATIVE_FACT"
        r.radius <- radius
        r.status = "READY"
    }

    /* -- op: accept (one pinned spot, zero cost) ----------------------------- */
    function CensusAcceptOp(q, r) {
        /* Tile defence in depth: only the pinned control or the pinned A1
         * bay stop may be queried; any other tile is an out-of-census
         * location, refused before any observation. */
        if (!SpotPinned(q.tile)) {
            r.status = "INVALID_LOCATION"
            return
        }
        local radius = GSStation.GetCoverageRadius(GSStation.STATION_TRUCK_STOP)
        if (radius < 0 || radius > 255) throw "D5_NATIVE_FACT"
        local accept = GSTile.GetCargoAcceptance(q.tile, CENSUS_CARGO, 1, 1, radius)
        if (accept < 0 || accept > 8) throw "D5_NATIVE_FACT"
        /* A zero here is a MEASURED zero only under this correlated READY
         * reply with the native radius echo attached; refusals carry no
         * observation at all. */
        r.tile <- q.tile
        r.accept <- accept
        r.radius <- radius
        r.status = "READY"
    }

    /* -- op: prod (chain-continuity production control, zero cost) ----------- */
    function CensusProdOp(r) {
        local production = GSIndustry.GetLastMonthProduction(
            CENSUS_PROD_INDUSTRY, CENSUS_CARGO)
        if (production < 0) throw "D5_NATIVE_FACT"
        r.prod <- production
        r.status = "READY"
    }

    /* -- op: box (the census core: the DiscoveryBoxes scan of record) -------- */
    function CensusBoxOp(q, r) {
        /* Centre defence in depth: only the pinned v2 pickup stop or the
         * pinned A1 bay delivery stop may be scanned. */
        if (!BoxPinned(q.tile)) {
            r.status = "INVALID_LOCATION"
            return
        }
        /* The measured native radius re-read fresh each exchange gates the
         * scan size exactly as the v2 DiscoveryBoxes does (1..8). */
        local radius = GSStation.GetCoverageRadius(GSStation.STATION_TRUCK_STOP)
        if (radius < 0 || radius > 255) throw "D5_NATIVE_FACT"
        if (radius < 1 || radius > 8) throw "D5_NATIVE_FACT"
        local wy = GSMap.GetMapSizeY()
        local wx = GSMap.GetMapSizeX()
        local ty = q.tile / wx
        local tx = q.tile % wx
        local member = {}
        for (local dy = -radius; dy <= radius; dy++) {
            for (local dx = -radius; dx <= radius; dx++) {
                if (ty + dy < 0 || ty + dy >= wy || tx + dx < 0 || tx + dx >= wx) continue
                local tile = (ty + dy) * wx + (tx + dx)
                if (!GSMap.IsValidTile(tile)) continue
                local ind = GSIndustry.GetIndustryID(tile)
                if (ind == null || ind < 0 || !GSIndustry.IsValidIndustry(ind))
                    continue
                if (ind in member) continue
                local production = GSIndustry.GetLastMonthProduction(ind, CENSUS_CARGO)
                if (production < 0 || production > 2147483647) throw "D5_NATIVE_FACT"
                local accepted = GSIndustry.IsCargoAccepted(ind, CENSUS_CARGO)
                if (accepted < 0 || accepted > 2) throw "D5_NATIVE_FACT"
                /* dx ascending within dy ascending visits tiles in ascending
                 * index order, so the first sighting carries the minimum
                 * member tile: the deterministic row anchor of record. */
                member[ind] <- {tile = tile, p = production, a = accepted}
            }
        }
        /* Ascending-id membership: identical page slices across the pages of
         * one box. A mid-session membership change shows up as a real count
         * divergence on the Python side; it is recorded, never retried. */
        local ids = []
        foreach (id, _ in member) ids.append(id)
        ids.sort()
        local count = ids.len()
        local rows = []
        for (local i = 0; i < MAX_PAGE_ROWS; i++) {
            local pos = q.cursor + i
            if (pos >= count) break
            local info = member[ids[pos]]
            rows.append({id = ids[pos], tile = info.tile, p = info.p, a = info.a})
        }
        /* A page beyond the drained membership is READY-empty: a
         * measurement of absence, never a refusal. Past the third page a
         * remaining membership stays visible as more = true — an explicit
         * overflow finding, never a silent discard. */
        r.count <- count
        r.more <- (count > q.cursor + rows.len())
        r.rows <- rows
        r.status = "READY"
    }

    function CensusHandle(q) {
        if (!("op" in q) || typeof q.op != "string" || !CensusOpAllowed(q.op)) return
        if (!("request_id" in q) || typeof q.request_id != "string" ||
            q.request_id.len() < 1 || q.request_id.len() > 32 ||
            !IdShape(q.request_id)) return
        if (!("plan" in q) || typeof q.plan != "string" || !Hex64(q.plan)) return
        if (!("company" in q) || typeof q.company != "integer" ||
            q.company < 0 || q.company > 14) return
        if (!("max_cost" in q) || typeof q.max_cost != "integer" || q.max_cost != 0) return
        if (!("pickup" in q) || typeof q.pickup != "integer" ||
            q.pickup < 0 || q.pickup > 65535 ||
            !("delivery" in q) || typeof q.delivery != "integer" ||
            q.delivery < 0 || q.delivery > 65535 ||
            !("depot" in q) || typeof q.depot != "integer" ||
            q.depot < 0 || q.depot > 65535 ||
            q.pickup == q.delivery || q.depot == q.pickup ||
            q.depot == q.delivery) return
        /* tile is required (an integer in map bounds) on accept and box
         * exactly and null on the other census ops; cursor is required on
         * box exactly. The wire serializes their absence. */
        if (!("tile" in q)) return
        if (q.op == "accept" || q.op == "box") {
            if (typeof q.tile != "integer" || q.tile < 0 || q.tile > 65535) return
        } else if (q.tile != null) return
        if (!("cursor" in q)) return
        if (q.op == "box") {
            if (typeof q.cursor != "integer" || q.cursor < 0 || q.cursor > 65535) return
        } else if (q.cursor != null) return
        /* One-shot budget accounting: unique request ids, the 32-request
         * cap; a duplicate id or an exhausted budget is silently dropped. */
        if (used == null) used = {}
        if (q.request_id in used || this.requests >= this.max_requests) return
        used[q.request_id] <- true
        this.requests++
        local r = {
            protocol = 9, op = q.op, request_id = q.request_id, plan = q.plan,
            company = q.company, max_cost = q.max_cost, pickup = q.pickup,
            delivery = q.delivery, depot = q.depot, status = "OUT_OF_ORDER",
            funds = 0, cost = 0
        }
        /* The tile and cursor echoes attach before the refusal ladder (the
         * survey-6 precedent): refusals carry the echoes, never the data. */
        if (q.op == "accept" || q.op == "box") r.tile <- q.tile
        if (q.op == "box") r.cursor <- q.cursor
        local idx = CensusPlannedIndex(q)
        if (idx < 0 || idx != this.census_stage || this.census_halted) {
            r.status = "OUT_OF_ORDER"
        } else if (this.plan_id != null && this.plan_id != q.plan) {
            r.status = "OUT_OF_ORDER"
        } else if (GSCompany.ResolveCompanyID(q.company) != q.company ||
                   q.company != CENSUS_COMPANY) {
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
                        /* Every census reply carries the bank balance at the
                         * exchange boundary (recorded, never changed: the
                         * census has no cost-bearing operation). */
                        r.funds = GSCompany.GetBankBalance(q.company)
                        if (q.op == "radius") {
                            CensusRadiusOp(r)
                        } else if (q.op == "accept") {
                            CensusAcceptOp(q, r)
                        } else if (q.op == "box") {
                            CensusBoxOp(q, r)
                        } else {
                            CensusProdOp(r)
                        }
                    }
                } catch (error) {
                    r.status = "UNSUPPORTED_NATIVE_FACT"
                }
            }
        }
        CensusGuard(r)
        if (!GSAdmin.Send(r)) throw "D5_RESPONSE_SEND_FAILED"
        GSLog.Info("D5_CENSUS " + q.request_id + " " + r.status)
        /* Census schedule accounting: only the exact READY status of the
         * planned exchange advances the census stage; every other terminal
         * status halts the census prefix-preservingly. Evidence, never
         * retries. */
        if (idx >= 0) {
            if (r.status == census_planned[idx][2]) {
                if (idx == this.census_stage && !this.census_halted) this.census_stage = idx + 1
            } else {
                this.census_halted = true
            }
        }
    }

    function Handle(q) {
        if (typeof q != "table") return
        if (!("protocol" in q)) return
        /* Protocol 9 is the read-only box census; the census package carries
         * no other protocol family of any kind. */
        if (q.protocol != 9) return
        CensusHandle(q)
    }

    function Start() {
        GSLog.Info("D5_CENSUS_READY")
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
class NetworkFreightProof extends D5CensusProof {
}
