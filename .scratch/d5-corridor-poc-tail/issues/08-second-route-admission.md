# 08: Second-route admission (M8 part 1)

**What to build:** a second natively-admitted executable route on the pinned
corridor world, derived offline by the bounded planning pipeline from the
native facts of record — same pickup domain, same corridor stations and
pinned identities, a road-legal bounded path admitted through the same
bounded machinery the delivered route passed — with the route pinned into
the parameterized contract as a named binding whose composition is staged-
and-preflight verifiable (staging itself is a separate operator approval; no
launch happens in this ticket). A recorded proof of infeasibility (the
executed route is the only admitted candidate under the standing bounds) is
an acceptable terminal outcome of this ticket and re-routes the M8 block
accordingly.

**Blocked by:** 06 (Delivered-class reconciliation), 07 (Route-admission
contract parameterization).

**Status:** done (2026-11-06; binding v2 registered through ticket 07's
parameterization; one commit, per the round grant below)

- [x] The competing route is a pipeline fact: derived on the qualified
      corridor facts by the bounded routing machinery, never a hand-drawn
      tile list; its path admission of record (road-legal, 2..47-tile bound,
      funds bounds) asserted by the same checks the delivered route used
- [x] The route is genuinely competing — distinct path identity from the
      delivered route; descriptive duplicates refuse
- [x] The route binding lands through ticket 07's parameterization with its
      full composition consistency suite green (schedule, plan digests,
      pin table, funds-model wiring)
- [ ] Infeasibility arm: not taken — the admission arm is the round's
      outcome (the recorded completed-search diagnostics thereof are
      booked in E118 alongside the admission record)
- [x] No native launch, no claim, no signature in this ticket; any staging
      of this binding happens only under its own later operator approval
- [x] Ledger row appended (route identity digests, admission evidence, the
      E36 context); `git diff --check` clean; `CONTEXT.md` pin intact; no
      push (see round-grant note below)

**Round record (granted 2026-11-05, landed and booked 2026-11-06).**
Operator granted the offline round ("Run 08 offline round") and, on its
presented outcome, granted "Register binding v2"; the same grants covered
this ledger row, these books and one commit — the ticket's original "no
commit" line is superseded by that grant per the established round
convention. No push, no native launch, no claim, no signature, no staging:
none of it granted or performed.

Offline admission round (driver `/tmp/opencode/c6_t08_admit.py`,
transcript `/tmp/opencode/c6_t08_admit_output.txt`, `T08 ADMISSION-AUDIT
PASS`, exit 0): the 31-tile A1 witness of record re-verified against the
retained D4 route read (30 unique road tiles, 29 cardinal traversed
edges); the only unmeasured road adjacency of record is the corner pair
(50351, 50352); the funds-bounds gates of record hold (quote 4429 ≤
ceiling 5000 ≤ funds 489650, via the optimizer's own `_validated_input`).
Enumeration 1 (the corridor route optimizer's `_candidate_routes` at its
own 3..24 instance bound) refuses with `RouteOptimizationError` — the
delivered 29-tile class escapes that bound, recorded and not stretched.
Enumeration 2 (the bounded k-shortest enumerator `_bounded_paths` at the
freight-v2 3..32 bound class, limit 256) returns exactly two distinct
simple paths between the pinned stops, both 29 tiles and both passing
`_validate_freight_route_v2`: the delivered route of record (digest
`b2f80f46…1f7131` == `FREIGHT_ROUTE_DIGEST_V2`, identified as its
descriptive duplicate and refused as the second route on that digest rule)
and the second candidate `witness[:23] + (50351, 50352) + witness[27:]`
(distinct digest `d14587b2…c4dd482`). The corner edge 50351↔50352 carries
a typed open precondition on the landed binding: it was never traversed in
any retained witness of record and the stale D4 bay's drive-through axis
is unmeasured offline, so its native connectivity resolves only under a
later native route-read probe under its own explicit operator approval —
none granted by this round (E36 stays open until a competing route
carries native receipts; ticket 10's ground).

Landing: `CARGOFLOW2_ROUTE_SECOND_ADMISSION` (route_version 2, pins
pin-for-pin equal to the route of record — the candidate's physical tile
path lives in the derived evidence, never in the binding contract),
registered in `CARGOFLOW2_ROUTE_BINDINGS`; module import guard widened to
the {1, 2} map of record with the v2-equals-v1-pins clause; the two
ticket-07 v1-only tests advanced truthfully to the new registry of record
plus a new composition-of-record test over the real pair; every v1 digest
assertion untouched (`REQUEST_PLAN_DIGEST` `98d055c4…f506ca` byte-equal;
native pipeline stays v1-locked, `proof/corridor_cargoflow2_native.py`
untouched). Suite of record: 135 passed (85 wire + 11 VM + 39 native);
`ruff check` and `uvx ty check` clean on both touched paths;
`git diff --check` clean; `CONTEXT.md` sha256 pin
`847d710a…984d` intact. Digests of record: binding v2
`26408e77…6b274`, binding v1 `9a4a0778…93e45e` (unchanged), plan v2
`e1cafb23…c08b0`, plan v1 `98d055c4…f506ca` (byte-equal).
