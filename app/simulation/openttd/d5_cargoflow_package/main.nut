/* Separate bounded native cargo-dispatch probe handler (protocol 10).
 * Additive: no existing frozen package is modified or imported. The probe
 * is strictly read-only — every operation is observation in company mode
 * (GSDate, GSIndustry.GetStockpiledCargo/GetLastMonthProduction/
 * GetLastMonthTransported, GSStation.GetCargoWaiting/GetCargoWaitingFrom/
 * GetCargoPlanned/GetCargoPlannedFrom, GSCompany.GetBankBalance) and there
 * is no cost-bearing or mutation-capable command of any kind. Demolition,
 * terraforming, road, station, depot, orders, purchase, vehicle and save
 * commands are absent by construction.
 *
 * The handler mirrors the proven protocol-9 census guards field for field:
 * corridor identity pins, the one-shot 32-request budget accounting
 * (unique ids shared only in spirit — this package is staged alone), the
 * plan_id latch and the prefix-preserving halt discipline. Its own work is
 * the fixed fourteen-sample dispatch ladder of record
 * (docs/d5-cargo-dispatch-probe-2026-11-04.md §5): the first sample latches
 * the anchor to the loaded world's own economy clock once, and every later
 * sample sleeps in-package (the freight v2 watch idiom, equality-gated)
 * until the clock reaches exactly anchor + its planned offset, then measures
 * the full 24-field observation set: the anchor, the clock facts (tick,
 * day, year, month, day-of-month), both industry stockpiles, the waiting
 * and planned families at both pinned stops (totals plus the two
 * station-sourced forms the 15.3 API actually allows — from station 0 and
 * from station 2), and the monthly production and transported levels of
 * both industries. Native fact families ride verbatim: production/
 * transported and stockpiles may read the 15.3 -1 fact (E65: an industry
 * without a produced/accepted slot for the measured cargo returns -1,
 * never a count); every other measured value is bounded non-negative and
 * any other native error refuses the exchange terminally.
 *
 * Save-restore identity: the retained frozen-source.zip info.nut declares
 * CreateInstance() returning "NetworkFreightProof"; the empty bridge
 * subclass at the end satisfies that contract without modifying any
 * retained identity byte. */

class D5CargoFlowProof extends GSController {
    /* Schedule state: `cargoflow_stage` is the index of the one planned
     * sample that may run next; `cargoflow_halted` stops every later
     * sample after any success frame failed to produce its exact planned
     * status. `cargoflow_anchor` is the one economy-day anchor the first
     * sample latches; every later sample must carry it unchanged. */
    cargoflow_stage = 0
    cargoflow_halted = false
    cargoflow_anchor = null
    /* One-shot dispatcher budget accounting (unique ids, 32-request cap). */
    requests = 0
    used = null
    /* Latched prelaunch plan digest: the first accepted exchange fixes the
     * attempt's plan identity; every later exchange must match it. */
    plan_id = null

    /* Baked corridor identity pins of the consumed depot-chain lineage
     * (world-pin version 3; the same pins every protocol-5/8/9/10 exchange
     * echoes; the probe never queries a foreign tile or foreign sid). */
    pickup = 45748
    delivery = 50862
    depot_tile = 45487
    /* Station identities of record: the corridor pickup stop and the A1
     * delivery bay (the A1 extension receipt's route_delivery_sid). */
    PICKUP_SID = 0
    BAY_SID = 2
    /* Industry identities of record: the retained census receipt rebound
     * as hypotheses pins the producing pickup industry 0 (tile 44983) and
     * the accepting bay industry 1 (tile 51116). */
    PICKUP_IND = 0
    BAY_IND = 1
    /* Fixed corridor identity for the probe session. */
    CARGOFLOW_COMPANY = 0
    CARGOFLOW_CARGO = 1
    /* Wait-window bounds of record (the freight-8 precedence scale): the
     * tick cap is the live in-package window ceiling; the day cap is the
     * wire echo bound of the wait family — the exact equality ladder
     * itself is the day authority (a sample never waits past its own
     * planned 5-day step, so the 60-day cap never binds). */
    WAIT_MAX_TICKS = 2048
    WAIT_DAY_CAP = 60
    /* 14 planned samples, plus dispatcher slack only through unique ids:
     * request 33 is the first one the dispatcher drops. */
    max_requests = 32

    /* The fixed fourteen-sample ladder: [request_id, offset, success
     * status], the same order and offsets the Python contract's
     * CARGOFLOW_EXCHANGE_IDS pins. The 65-day span (14 samples, 5-day
     * cadence) crosses at least two month boundaries of any OpenTTD
     * calendar pair. */
    cargoflow_planned = [
        ["sample-00", 0, "READY"],
        ["sample-01", 5, "READY"],
        ["sample-02", 10, "READY"],
        ["sample-03", 15, "READY"],
        ["sample-04", 20, "READY"],
        ["sample-05", 25, "READY"],
        ["sample-06", 30, "READY"],
        ["sample-07", 35, "READY"],
        ["sample-08", 40, "READY"],
        ["sample-09", 45, "READY"],
        ["sample-10", 50, "READY"],
        ["sample-11", 55, "READY"],
        ["sample-12", 60, "READY"],
        ["sample-13", 65, "READY"]
    ]

    function CargoFlowOpAllowed(op) {
        return op == "sample"
    }

    function CargoFlowPlannedIndex(q) {
        for (local i = 0; i < cargoflow_planned.len(); i++)
            if (cargoflow_planned[i][0] == q.request_id &&
                cargoflow_planned[i][1] == q.offset) return i
        return -1
    }

    function CargoFlowGuard(r) {
        if (r.funds < -2147483648 || r.funds > 2147483647 || r.cost < 0 ||
            r.cost > 2147483647) throw "D5_RESPONSE_OUT_OF_BOUNDS"
        if (r.offset < 0 || r.offset > 65) throw "D5_RESPONSE_OUT_OF_BOUNDS"
        if ("anchor" in r && (r.anchor < 0 || r.anchor > 2147483647))
            throw "D5_RESPONSE_OUT_OF_BOUNDS"
        if ("tick" in r && (r.tick < 0 || r.tick > 2147483647))
            throw "D5_RESPONSE_OUT_OF_BOUNDS"
        if ("day" in r && (r.day < 0 || r.day > 2147483647))
            throw "D5_RESPONSE_OUT_OF_BOUNDS"
        if ("year" in r && (r.year < 0 || r.year > 2147483647))
            throw "D5_RESPONSE_OUT_OF_BOUNDS"
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
    }

    /* -- op: sample (the read-only dispatch probe exchange) ------------------ */
    function CargoFlowSampleOp(q, r) {
        /* Station defence in depth: a pinned identity that vanished makes
         * the world stale for the whole ladder; refused fail-closed. */
        if (!GSStation.IsValidStation(this.PICKUP_SID) ||
            !GSStation.IsValidStation(this.BAY_SID)) {
            r.status = "STALE_PIN"
            return
        }
        /* The anchor of record latches exactly once, at the first sample:
         * every later sample measures the same anchor the Python phase
         * verifier re-derives, so a mid-ladder latch change becomes a
         * divergence on the Python side, never a silent re-anchor. */
        if (this.cargoflow_anchor == null) {
            local anchor_day = GSDate.GetCurrentDate()
            if (anchor_day < 0 || anchor_day > 2147483647) throw "D5_NATIVE_FACT"
            this.cargoflow_anchor = anchor_day
        }
        local anchor = this.cargoflow_anchor
        local target = anchor + q.offset
        /* Wait-window machinery (the freight v2 watch idiom, equality-
         * gated): the sample sleeps in-package until the clock reaches
         * exactly its planned ladder day. A pause refuses, tick regression
         * types CLOCK_STALLED, and ANY overshoot past the exact target day
         * is a fail-closed ladder break (WINDOW_EXHAUSTED): the ladder of
         * record can never be reshuffled by the clock. */
        local prev = GetTick()
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
            if (day == target) break
            if (day > target) {
                /* The clock already passed this sample's planned day
                 * between exchanges: the exact ladder cannot be measured
                 * anymore; fail closed with the honest echo. */
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
        /* The target day bound: measure the full observation set of record.
         * Every read is guarded at use; a negative (or out-of-domain)
         * native fact refuses the exchange before any response is sent. */
        local sid_p = this.PICKUP_SID
        local sid_b = this.BAY_SID
        r.anchor <- anchor
        r.tick <- GetTick()
        local day = GSDate.GetCurrentDate()
        if (day < 0 || day > 2147483647) throw "D5_NATIVE_FACT"
        r.day <- day
        /* The 1-based month and 1-based day-of-month are the 15.3 script
         * API facts of record (script_date.cpp: ymd.month + 1). */
        r.year <- GSDate.GetYear(day)
        if (r.year < 0 || r.year > 2147483647) throw "D5_NATIVE_FACT"
        r.month <- GSDate.GetMonth(day)
        if (r.month < 1 || r.month > 12) throw "D5_NATIVE_FACT"
        r.day_of_month <- GSDate.GetDayOfMonth(day)
        if (r.day_of_month < 1 || r.day_of_month > 31) throw "D5_NATIVE_FACT"
        /* The industry-side accepted piles. -1 is the 15.3 native fact of
         * record (E65 family): an industry without an accepted slot for
         * this cargo returns -1, never a count — carried verbatim and
         * logged; any other negative is an unsupported native fact. */
        local stock_p = GSIndustry.GetStockpiledCargo(this.PICKUP_IND, CARGOFLOW_CARGO)
        if (stock_p == -1) {
            GSLog.Info("D5_CARGOFLOW_STOCK_NOT_ACCEPTED " + this.PICKUP_IND)
        } else if (stock_p < 0 || stock_p > 65535) {
            throw "D5_NATIVE_FACT"
        }
        r.stock_pickup <- stock_p
        local stock_b = GSIndustry.GetStockpiledCargo(this.BAY_IND, CARGOFLOW_CARGO)
        if (stock_b == -1) {
            GSLog.Info("D5_CARGOFLOW_STOCK_NOT_ACCEPTED " + this.BAY_IND)
        } else if (stock_b < 0 || stock_b > 65535) {
            throw "D5_NATIVE_FACT"
        }
        r.stock_bay <- stock_b
        /* The station waiting family at both stops: the totals
         * (GetCargoWaiting) and the two per-source forms the 15.3 API
         * allows — from the pickup stop and from the bay stop. A negative
         * here is a stale station/cargo fact: refused. */
        local wait_p = GSStation.GetCargoWaiting(sid_p, CARGOFLOW_CARGO)
        if (wait_p < 0 || wait_p > 2147483647) throw "D5_NATIVE_FACT"
        r.wait_pickup <- wait_p
        local wait_p0 = GSStation.GetCargoWaitingFrom(sid_p, sid_p, CARGOFLOW_CARGO)
        if (wait_p0 < 0 || wait_p0 > 2147483647) throw "D5_NATIVE_FACT"
        r.wait_pickup_from0 <- wait_p0
        local wait_p2 = GSStation.GetCargoWaitingFrom(sid_p, sid_b, CARGOFLOW_CARGO)
        if (wait_p2 < 0 || wait_p2 > 2147483647) throw "D5_NATIVE_FACT"
        r.wait_pickup_from1 <- wait_p2
        local wait_b = GSStation.GetCargoWaiting(sid_b, CARGOFLOW_CARGO)
        if (wait_b < 0 || wait_b > 2147483647) throw "D5_NATIVE_FACT"
        r.wait_bay <- wait_b
        local wait_b0 = GSStation.GetCargoWaitingFrom(sid_b, sid_p, CARGOFLOW_CARGO)
        if (wait_b0 < 0 || wait_b0 > 2147483647) throw "D5_NATIVE_FACT"
        r.wait_bay_from0 <- wait_b0
        local wait_b2 = GSStation.GetCargoWaitingFrom(sid_b, sid_b, CARGOFLOW_CARGO)
        if (wait_b2 < 0 || wait_b2 > 2147483647) throw "D5_NATIVE_FACT"
        r.wait_bay_from1 <- wait_b2
        /* The planned family (the per-month flows of record): the totals
         * (GetCargoPlanned) and the two per-source forms
         * (GetCargoPlannedFrom, from the pickup stop / from the bay
         * stop — per the 15.3 API the "from-self" form is the station's
         * own produced planned flow). */
        local count_p = GSStation.GetCargoPlanned(sid_p, CARGOFLOW_CARGO)
        if (count_p < 0 || count_p > 2147483647) throw "D5_NATIVE_FACT"
        r.count_pickup <- count_p
        local count_b = GSStation.GetCargoPlanned(sid_b, CARGOFLOW_CARGO)
        if (count_b < 0 || count_b > 2147483647) throw "D5_NATIVE_FACT"
        r.count_bay <- count_b
        local pl_p0 = GSStation.GetCargoPlannedFrom(sid_p, sid_p, CARGOFLOW_CARGO)
        if (pl_p0 < 0 || pl_p0 > 2147483647) throw "D5_NATIVE_FACT"
        r.planned_pickup_from0 <- pl_p0
        local pl_p2 = GSStation.GetCargoPlannedFrom(sid_p, sid_b, CARGOFLOW_CARGO)
        if (pl_p2 < 0 || pl_p2 > 2147483647) throw "D5_NATIVE_FACT"
        r.planned_pickup_from1 <- pl_p2
        local pl_b0 = GSStation.GetCargoPlannedFrom(sid_b, sid_p, CARGOFLOW_CARGO)
        if (pl_b0 < 0 || pl_b0 > 2147483647) throw "D5_NATIVE_FACT"
        r.planned_bay_from0 <- pl_b0
        local pl_b2 = GSStation.GetCargoPlannedFrom(sid_b, sid_b, CARGOFLOW_CARGO)
        if (pl_b2 < 0 || pl_b2 > 2147483647) throw "D5_NATIVE_FACT"
        r.planned_bay_from1 <- pl_b2
        /* The monthly production machine's own verdict of record (both
         * industries). -1 rides verbatim exactly as the census measured
         * the acceptor's non-producer fact (E65); the honest monthly
         * boundary bound: the ladder samples at least two month
         * boundaries, so a decaying production curve stays legible. */
        local prod_p = GSIndustry.GetLastMonthProduction(
            this.PICKUP_IND, CARGOFLOW_CARGO)
        if (prod_p == -1) {
            GSLog.Info("D5_CARGOFLOW_NON_PRODUCER " + this.PICKUP_IND)
        } else if (prod_p < 0 || prod_p > 2147483647) {
            throw "D5_NATIVE_FACT"
        }
        r.prod_pickup <- prod_p
        local prod_b = GSIndustry.GetLastMonthProduction(
            this.BAY_IND, CARGOFLOW_CARGO)
        if (prod_b == -1) {
            GSLog.Info("D5_CARGOFLOW_NON_PRODUCER " + this.BAY_IND)
        } else if (prod_b < 0 || prod_b > 2147483647) {
            throw "D5_NATIVE_FACT"
        }
        r.prod_bay <- prod_b
        local trans_p = GSIndustry.GetLastMonthTransported(
            this.PICKUP_IND, CARGOFLOW_CARGO)
        if (trans_p == -1) {
            GSLog.Info("D5_CARGOFLOW_NON_TRANSPORT_LOG " + this.PICKUP_IND)
        } else if (trans_p < 0 || trans_p > 2147483647) {
            throw "D5_NATIVE_FACT"
        }
        r.trans_pickup <- trans_p
        local trans_b = GSIndustry.GetLastMonthTransported(
            this.BAY_IND, CARGOFLOW_CARGO)
        if (trans_b == -1) {
            GSLog.Info("D5_CARGOFLOW_NON_TRANSPORT_LOG " + this.BAY_IND)
        } else if (trans_b < 0 || trans_b > 2147483647) {
            throw "D5_NATIVE_FACT"
        }
        r.trans_bay <- trans_b
        r.status = "READY"
    }

    function CargoFlowHandle(q) {
        if (!("op" in q) || typeof q.op != "string" || !CargoFlowOpAllowed(q.op)) return
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
        /* offset is required (an integer on the pinned ladder scale) on
         * the sample op — the one op this package carries. */
        if (!("offset" in q) || typeof q.offset != "integer" ||
            q.offset < 0 || q.offset > 65) return
        /* One-shot budget accounting: unique request ids, the 32-request
         * cap; a duplicate id or an exhausted budget is silently dropped. */
        if (used == null) used = {}
        if (q.request_id in used || this.requests >= this.max_requests) return
        used[q.request_id] <- true
        this.requests++
        local r = {
            protocol = 10, op = q.op, request_id = q.request_id, plan = q.plan,
            company = q.company, max_cost = q.max_cost, pickup = q.pickup,
            delivery = q.delivery, depot = q.depot, offset = q.offset,
            status = "OUT_OF_ORDER",
            funds = 0, cost = 0
        }
        /* The offset echo attaches before the refusal ladder (the survey-6
         * precedent): refusals carry the echoes, never the data. */
        local idx = CargoFlowPlannedIndex(q)
        if (idx < 0 || idx != this.cargoflow_stage || this.cargoflow_halted) {
            r.status = "OUT_OF_ORDER"
        } else if (this.plan_id != null && this.plan_id != q.plan) {
            r.status = "OUT_OF_ORDER"
        } else if (GSCompany.ResolveCompanyID(q.company) != q.company ||
                   q.company != CARGOFLOW_COMPANY) {
            r.status = "INVALID_COMPANY"
        } else if (q.pickup != this.pickup || q.delivery != this.delivery ||
                   q.depot != this.depot_tile ||
                   cargoFlowPlannedOffset(idx) != q.offset) {
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
                        /* Every probe reply carries the bank balance at the
                         * exchange boundary (recorded, never changed: the
                         * probe has no cost-bearing operation). */
                        r.funds = GSCompany.GetBankBalance(q.company)
                        CargoFlowSampleOp(q, r)
                    }
                } catch (error) {
                    /* The inner native error text is evidence: logged with
                     * the exchange label before the refusal status, so the
                     * retained session's stderr carries the exact thrown
                     * fact and the readback never needs to. The echo prelude
                     * of a half-read sample is data, never echo language:
                     * the refusal frame of record carries none of the
                     * observation set (the wire refuses a spoofed hybrid). */
                    GSLog.Info("D5_CARGOFLOW_THROW " + q.request_id + " " +
                        (typeof error == "string" ? error : typeof error))
                    foreach (name in ["anchor", "tick", "day", "year", "month",
                                      "day_of_month", "stock_pickup",
                                      "stock_bay", "wait_pickup",
                                      "wait_pickup_from0", "wait_pickup_from1",
                                      "wait_bay", "wait_bay_from0",
                                      "wait_bay_from1", "count_pickup",
                                      "count_bay", "planned_pickup_from0",
                                      "planned_pickup_from1",
                                      "planned_bay_from0",
                                      "planned_bay_from1", "prod_pickup",
                                      "prod_bay", "trans_pickup",
                                      "trans_bay"]) {
                        if (name in r) delete r[name]
                    }
                    r.status = "UNSUPPORTED_NATIVE_FACT"
                }
            }
        }
        CargoFlowGuard(r)
        if (!GSAdmin.Send(r)) throw "D5_RESPONSE_SEND_FAILED"
        GSLog.Info("D5_CARGOFLOW " + q.request_id + " " + r.status)
        /* Probe schedule accounting: only the exact READY status of the
         * planned sample advances the stage; every other terminal status
         * halts the ladder prefix-preservingly. Evidence, never retries. */
        if (idx >= 0) {
            if (r.status == cargoflow_planned[idx][2]) {
                if (idx == this.cargoflow_stage && !this.cargoflow_halted)
                    this.cargoflow_stage = idx + 1
            } else {
                this.cargoflow_halted = true
            }
        }
    }

    /* The pinned ladder offset of one planned row (the handler's own pin
     * echo check against the request's offset claim). */
    function cargoFlowPlannedOffset(idx) {
        return cargoflow_planned[idx][1]
    }

    function Handle(q) {
        if (typeof q != "table") return
        if (!("protocol" in q)) return
        /* Protocol 10 is the read-only dispatch probe; this package
         * carries no other protocol family of any kind. */
        if (q.protocol != 10) return
        CargoFlowHandle(q)
    }

    function Start() {
        GSLog.Info("D5_CARGOFLOW_READY")
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
class NetworkFreightProof extends D5CargoFlowProof {
}
