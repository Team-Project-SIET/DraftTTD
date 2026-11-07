# 11: Funds-taxonomy decision (T-021a)

**What to build:** the operator's funds taxonomy decision recorded as an
ADR-class document — the running-cost category under the halt-on-unexplained-
drift rule settled once, with the reporting rules pinned for the corridor
experiments: operating expense categories are observed native cash deltas
only, derived aggregates stay labeled DERIVED, unmeasured categories stay
UNKNOWN, revenue is timing-dependent and never reported as profit. The
decision is the operator's; this ticket drafts the record, surfaces any
decision options, and lands the confirmation — it never licenses new
mutation.

**Blocked by:** 10 (Selected-route delivered attempt).

**Status:** done 2026-11-06 (the draft round granted in-session as the
frontier instruction "do Ticket 11"; the operator adopted the record via
the explicit in-session gate option "Confirm decision of record"; the
decision-of-record landed, supersession-only thereafter; no push, no
mutation)

- [x] Draft decision record exists: **`docs/adr/0001-funds-taxonomy-of-record.md`**
      (ADR-0001) — the taxonomy of record in seven decisions: D1 the
      charge set {vehicle purchase, monthly loan interest, station-value
      fee, road-vehicle running cost} with one category per mechanism and
      no per-calendar-day OPEX bucket (the E113 event lattice bills; the
      round-5 `arrive-00` day-frame residual is the recorded example of
      the rejected reading); D2 income measured never modeled (engine
      readback at the observation instants, per-span attribution); D3
      OPEX = OBSERVED native deltas only + the four label classes
      (OBSERVED / DERIVED / CONTROLLED / UNKNOWN); D4 unexplained movement
      stays UNKNOWN and is never reclassified; D5 revenue never profit;
      D6 the zero-residual fence carries into reports and replays; D7 the
      reporting rules (attribution travels, labels travel, script-tick
      rates, fresh sibling outputs). Its four rejected alternatives
      (calendar-day bucketing, nearest-exchange allocation, DERIVED as
      truth, revenue-as-profit) each carry their recorded reason.
- [x] Each fact of record separated OBSERVED / DERIVED / CONTROLLED in
      the draft — the four label classes are defined with their own
      truth conditions (D3's list); the UNKNOWN set enumerated by D4
      (unallocated cash decreases stay UNKNOWN — the fence closes them,
      the taxonomy never does)
- [x] The draft binds rounds of record as its evidence anchors: the
      round-3-class depot-chain receipts (`D5-F12-DEPOT-3`, founding
      funds 489650, after-save pin `183b2027…6ea6`), the round-6 corridor
      receipts on the delivered v1 arm (E116/E117 — the exact charge set
      live-true), and the round-7 corridor receipts on the second
      v2/corner-swap route (E124 — the per-exchange `income_deltas`
      table, `running_cost 421` exact under the lattice, finance 484769)
      — plus the spec's M7 block and the design record §4.2–4.4 as the
      settled event law of record
- [x] Operator confirmation session held (2026-11-06, in-session): the
      draft surfaced the decision options (adopt as decision-of-record /
      amend draft first / defer), the operator confirmed inline via the
      explicit gate option; the record marked **CONFIRMED DECISION OF
      RECORD** in its own status section — no further edit without a
      supersession of record; no mutation licensed by the decision
      (offline-only; native runs stay per-gate)
- [x] Every sub-step's ledger row + status-log entry; `git diff --check`
      clean; `CONTEXT.md` pin intact; committed once with the formed
      ticket; no push ever
