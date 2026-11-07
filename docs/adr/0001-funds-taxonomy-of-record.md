# ADR-0001: The corridor funds taxonomy of record

## Status

CONFIRMED DECISION OF RECORD (2026-11-06, the operator confirmation
session of ticket 11 T-021a — the operator adopted this record via the
explicit in-session gate option "Confirm decision of record"). Any
further change is a supersession of record, never an edit.

## Context

The D5 corridor PoC contracts every attempt to a **zero-residual funds
fence with halt-on-unexplained-drift**: at every exchange, `residual =
observed_funds − modeled_funds` must be exactly 0, and any unexplained
divergence halts the attempt (`docs/d5-cargoflow-delivery-design-2026-11-04.md`
§4.4). The fence's charge model is settled as the settled event law of
record (the E113 15.3 source pin, the E114 offline fix, and the E115
design-record carries): road-vehicle running cost bills at every charge
event of the E113 event lattice — events at the day-roll anchor + 1 +
k·74, keyed by their own rolled economy day, the unstop partial inside
the first billed event, silent pre-count events (rt ≤ 0), the exact 8.8
fixed-point carry from the pinned display figure with the uint8-wrap
borrow kernel unchanged — while loan interest and the station-value fee
bill at economy-month boundaries, purchase is an exact whole-unit debit,
and delivery income is engine-read at the same observation instants as
the funds echo.

The spec's M7 block leaves the **reporting taxonomy** decision
outstanding (`docs/specs/d5-corridor-poc-tail.md`, "Funds taxonomy");
ticket 11 (T-021a) implements it. The decision question of record: what
single class of native measurements counts as operating expense (OPEX)
for every corridor report, what stays labeled DERIVED, what stays
UNKNOWN, and how revenue is reported. This record settles that decision
once, covering the corridor lineage's receipts (the native evidence
anchors, no new mutations): the round-3-class depot-chain receipts
(the `D5-F12-DEPOT-3` prerequisite lineage — the founding-funds and
depot-chain class), the round-6 corridor receipts on the delivered v1
arm (E116/E117 — the
`CARGOFLOW2_LOADED_NEVER_DELIVERED` terminal with the exact charge
class live-true), and the round-7 corridor receipts on the second
(v2/corner-swap) route (E124 — the complete `income_deltas` table
engine-read at every exchange, `running_cost 421` exact under the
lattice, every income delta 0 at the 25 observed instants). The round-6
and round-7 attempts are consumed terminal history; the taxonomy binds
their receipts, it licenses no new attempt.

## Decision

The taxonomy of record comes in seven decisions: one category set, four
label classes, and two reporting rules.

### D1. The charge-set taxonomy of record — one category per mechanism

Every observed corridor cash decrease belongs to exactly one charging
category of the model of record. The category set of record is:

1. **Vehicle purchase** — the exact recorded quote as a single
   whole-unit debit at the `purchase-00` exchange (command results pay
   through `SubtractMoneyFromCompany`; observed natively both rounds:
   489650 → 485221, quote 4429 exact);
2. **Monthly loan interest** — the staircase installment
   `yearly·(m+1)/12 − yearly·m/12` at each economy month boundary on
   `yearly = current_loan · rate / 100` (whole units, integer division;
   observed class: 167 at both in-ladder boundaries);
3. **Station-value fee** — `_price[PR_STATION_VALUE] >> 2` at each
   economy month boundary (25 per boundary; the E99 cross-check class
   192 − 167 = 25);
4. **Road-vehicle running cost** — billed at every charge event of the
   E113 event lattice of record (the `T0 + 1 + 74k` spread-slot events
   keyed by their own rolled day; amount = `raw · rt / (365 · 74)` in
   8.8 fixed point paid through `SubtractMoneyFromCompanyFract` with the
   uint8-wrap borrow kernel unchanged; driving and loading both accrue;
   breakdowns move no money; pre-count events silent). This category
   carries the fractional-carry accounting of §4.3 — it is the only
   category that touches `money_fraction`.

There is **no "per calendar day" OPEX bucket**: the running cost is
billed by the event lattice, never averaged by day. There are **no
other charge categories of record** (no inflation, no infrastructure
maintenance, no property charges, no other vehicle classes — the design
record's §4.2 item 5), so the taxonomy of record's charge set is
exactly {purchase, monthly loan interest, station-value fee,
road-vehicle running cost}.

### D2. Income attribution

Delivery income is **measured, never modeled**: every exchange from
`site-00` onward carries the engine's own quarterly-income readback at
the same observation instant as the funds echo, and the model
attributes income deltas per-span. Income deltas are a native
measurement class, not an OPEX category, and the income term keeps the
fence residual-free by attribution (an income delta may appear without
a latched delivery? — never: a span containing a latched unload must
corroborate; no unexplained income exists; the engine accounting
corroborates the payment chain instead of absorbing it).

### D3. The OPEX class of record — OBSERVED native cash deltas only

`OPEX` of record = the sum of **observed** native cash deltas
attributed to one of the D1 charge classes at their billing instants.
Derived aggregates (per-report sums, per-exchange allocations, per-day
normalizations, expected-trajectory walks) are always labeled
**DERIVED** — they carry the analysis, they are never the OPEX truth
class. A report's OPEX line cites its native evidence anchor (the
retained receipts of the rounds listed above).

**The four label classes of record** (every reported figure carries
exactly one):

- **OBSERVED** — a number read from a retained native receipt (a funds
  echo, an income readback, a latched load, a position, a manifest
  hash): the evidence itself, immutable under the retained-artifact
  discipline.
- **DERIVED** — any arithmetic whose inputs are OBSERVED/DERIVED
  figures (sums, allocations, walks, margins): labeled, with its inputs
  cited, recomputable, never the truth class of an OPEX row.
- **CONTROLLED** — a number the contract pins rather than measures
  (the world pins, the budget table, the request/exchange schedule,
  the seeded constants, the harness pins): an input of record, cited
  to its pin, never evidence that the world did anything.
- **UNKNOWN** — a fact that no retained receipt or pinned input
  establishes (D4's unallocated movement, any unmeasured category): it
  stays UNKNOWN — never reclassified, never silently filled.

### D4. The UNKNOWN class — unexplained stays unclassified

Unmeasured or unallocated cash movement is class **UNKNOWN**. An
observed funds decrease outside the D1 charge set plus measured income
is **divergence → halt** under the fence — it is never reclassified
into an OPEX category to close the books, and it is never silently
absorbed. The halt-on-unexplained-drift rule stands unchanged by this
taxonomy; the taxonomy only names what was already evidenced.

### D5. Revenue is never profit

Revenue (delivery income) is timing-dependent engine accounting; it is
never reported as profit. Margin classes (net of OPEX, gain/loss, the
E36-class delivery-ledger judgement) stay labeled DERIVED with their
inputs cited. The corridor finding history stands: round-6 and round-7
both terminated `CARGOFLOW2_LOADED_NEVER_DELIVERED` — the taxonomy
reports the observed state, it does not improve the reported picture.

### D6. The fence discipline carries

The zero-residual fence (`residual == 0` at every exchange, no
tolerance) carries into every future corridor attempt and every report
that replays retained receipts. A replay that cannot reconcile a
retained receipt exactly reports the reconciliation failure as a
finding — it never normalizes, rounds, or absorbs the residual.

### D7. Reporting rules of record

- Attribution (world / save / seed / plan identity) travels with every
  reported number.
- OBSERVED / DERIVED / CONTROLLED / UNKNOWN labels travel with the
  numbers they qualify.
- Milestone rates are reported as **script-tick rates** (rates of the
  pinned observation script), never as steady-state throughput.
- Reports replay receipts into fresh sibling outputs — no historical
  output is overwritten and no old receipt is retread as new.

## Alternatives considered and rejected

- **Calendar-day OPEX bucketing** — rejected: it contradicts the E113
  event law of record; the round-5 `arrive-00` halt class (residual +1
  from a day-frame walk error) is the recorded live example of exactly
  this error; day-frame accounting was corrected by the E114 offline
  fix, not doubled down on.
- **Nearest-exchange charge attribution** (allocating each charge to
  the closest exchange in time) — rejected: the uint8-wrap borrow
  kernel and the unstop count start make per-event billing the only
  faithful assignment; a nearest-exchange rule double-counts or
  mis-counts whole units inside the very first billed event.
- **DERIVED aggregates accepted as the OPEX truth class** — rejected:
  the OPEX class is OBSERVED-only; a derived sum can be recomputed and
  rebound, an observed delta cannot.
- **Revenue reported as profit / margin presented without citation**
  — rejected: violates the spec's auditor class ("revenue, OPEX and
  profit contexts kept distinct", user story 17) and D5.

## Consequences

- **Ticket 12 (P07 replay closure)** consumes this taxonomy: the
  reporting labels of D3/D5/D7 pin the sibling outputs' label
  discipline, and the D1 charge set names every OPEX row's category.
- **Ticket 13 (PoC completion declaration)** cites this record as the
  OPEX decision of record; its reported margins must carry the DERIVED
  label with D3-cited inputs.
- The taxonomy decision is **offline-only**: it licenses no new
  staging, no new claim, no signature, no launch; native runs stay
  gated by their own explicit operator approvals per the standing
  discipline.
- The E113/E114/E115 event-law records and the `CONTEXT.md` shared
  terms (day-roll anchor 48, charge event, unstop count start) carry;
  this record adds no new `CONTEXT.md` term.

## Evidence anchors of record

- `docs/specs/d5-corridor-poc-tail.md`, M7 "Funds taxonomy" block +
  "Reporting closure" block (the outstanding decision this record
  settles).
- `docs/d5-cargoflow-delivery-design-2026-11-04.md` §4.2 (the complete
  charge set), §4.3 (the exact fractional carry), §4.4 (the
  zero-residual fence) — the settled event law of record.
- The round-3-class depot-chain receipts: the `D5-F12-DEPOT-3`
  prerequisite lineage (founding funds 489650, the depot-chain class,
  after-save pin `183b2027…6ea6`).
- The round-6 corridor receipts (delivered v1 arm): E116/E117 — the
  COMPLETE-not-delivered terminal with the exact charge set live-true
  (funds series [485217…484770], finance 484769, income 0).
- The round-7 corridor receipts (second v2/corner-swap route): E124 —
  the unique per-exchange `income_deltas` table (every income delta 0
  engine-read at all 25 instants), `running_cost 421` exact under the
  lattice, the wrap-borrow rows recorded (billed at the `74`-class
  instants), finance 484769.
- The `CONTEXT.md` day-roll-anchor / charge-event / unstop-count-start
  rows (transition 3, sha-pinned `847d710a…984d`).
