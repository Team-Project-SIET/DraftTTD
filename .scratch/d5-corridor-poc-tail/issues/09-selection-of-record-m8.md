# 09: Selection of record (M8 part 2)

**What to build:** the optimizer's selection of record over the admitted
corridor route set — the pure selection layer run under its standing
boundedness (bounded simulation, ≤16 relationships, ≤8 services, bounded
solve time), producing the reproducible selection artifact naming the route
the delivered attempt will carry next. No attempt runs in this ticket; the
selection must be re-derivable from its frozen inputs.

**Blocked by:** 08 (Second-route admission).

**Status:** done (2026-11-06; selection of record derived and booked; one
commit, per the round grant below)

- [x] The selection artifact of record exists: the frozen input set (the two
      admitted route bindings with their identities/facts) + the optimizer's
      chosen route + the provenance of every constraint applied
- [x] Reproducibility asserted: re-running the selection over the same
      frozen inputs reproduces the same choice (deterministic contract; any
      bounded-solver nondeterminism property-recorded, never hidden)
      — 5/5 selection runs identical: selected action ids + route tiles +
      solver plan_hash `313294ab…47fd93` byte-equal across every re-run
- [x] The selected route's binding re-validated post-selection (composition
      consistency suite green; the refused arms documented) — the v1 arm's
      composition re-validated in-driver (plan digest `98d055c4…f506ca`
      byte-equal, ladder rows byte-equal, funds pins of record) plus a
      fresh wire+VM suite run (96 passed); the refused arm (v2) documented
- [x] Out-of-bounds or empty admitted sets surface as typed infeasibility of
      record — never a soft default to the delivered route — the typed arm
      is wired in the driver (OptimizerFailure verbatim → recorded refusal,
      no default); this round the machinery returned a selection, so the
      arm was not exercised
- [x] No candidate lifecycle action inside this ticket (no staging / no
      signing / no claim / no launch) — none performed
- [x] Ledger row appended (selection artifact digest, route of record,
      bis-reported bounds); `git diff --check` clean; `CONTEXT.md` pin
      intact; no push (the commit is covered by the round grant — the
      established round convention, noted below)

**Round record (granted 2026-11-06, booked same day).** Operator granted
the offline selection round ("Run 09 offline round") explicitly covering
the derivation + reproducibility proof + refused-arm documentation +
ledger/books and one commit — the ticket's original "no commit" line is
superseded by that grant per the established round convention. No push,
no staging, no signing, no claim, no launch: none granted or performed.

**Selection of record (driver `/tmp/opencode/c6_t09_select.py`,
transcript `/tmp/opencode/c6_t09_select_output.txt`, rc 0, `T09
SELECTION-AUDIT PASS` 13 PASS / 0 FAIL; no repo code touched by the
round):** the frozen input set = the two ticket-08 admitted bindings
(v1 digest `9a4a0778…93e45e`, v2 digest `26408e77…6b274`) + the corridor
facts surface of record (31-tile A1 witness chain re-verified, 30-tile
road-of-record set, depot 45487 off-route, funds gates via the optimizer's
own `_validated_input`) + ONE frozen enumeration of record (the two
29-tile candidates, both re-validated through `_validate_freight_route_v2`).
The selection layer of record (`_scenario` → P05
`optimize_candidate_network` under its standing boundedness ≤16
relationships / ≤8 services / bounded solve time) selected with the exact
optimize_corridor_route validation checks byte-equal (the route-tile
bound moved to the freight-v2 3..32 class — the module's own 3..24
instance bound refuses both admitted candidates, property-recorded, not
stretched):

- **Selected arm: the delivered route of record (v1)** — candidate id
  `corridor-b2f80f46513436a102005f10`, route digest ==
  `FREIGHT_ROUTE_DIGEST_V2` `b2f80f46…1f7131` (the descriptive duplicate
  of ticket 08 is the route the selection carries), 29 tiles, depot 45487
  touching exactly interior 45743, endpoints exact, all inside the
  available-tile surface.
- **Refused arm: the second admission (v2, corner-swap)** — digest
  `d14587b2…c4dd482`; still ticket-08-admitted, never de-admitted,
  never relabeled, a registry citizen of record.
- **Reproducibility 5/5**: identical selected action ids + route tiles +
  solver plan hash across all re-runs (deterministic contract observed;
  no bounded-solver nondeterminism seen — typed to the frozen inputs).
- **Solver-reported metrics of record**: plan hash
  `313294ab4163364724f3b994514a902b8c1da38b467c962229f8f1110118fd93`,
  estimator `candidate-network-optimizer` v1, assumptions digest
  `8801de2c…9ef5e`, infrastructure spend £55 (the 2·27+1 road-piece
  estimate — the admitted set is capex-equal and the deterministic
  machinery resolves it), vehicle purchase £4429, horizon 1, GBP.
- **Post-selection re-validation**: the selected v1 binding's plan
  digest `98d055c4…f506ca` byte-equal, ladder rows byte-equal, funds pins
  489650/4429; fresh wire+VM suite run 96 passed; native suite
  (39) untouched — no repo code changed this round (the selection drives
  the module's own machinery; its landing surface needs no edit).

**M8-tail reading of record (typed, not stretched):** the optimizer's
selection of record carries the delivered route — ticket 10's
selected-route delivered attempt proceeds per the spec's own optimizer
sentence (a fresh candidate round + its own gate ladder); the corner-swap
v2 stays admitted-but-unselected, and the E36 finding still closes only
when a genuinely competing executable route carries NATIVE receipts
(ticket 10 is not that closure by default — its full meaning is settled
at ticket 10 under its own approvals).
