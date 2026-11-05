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

**Status:** ready-for-agent

- [ ] The competing route is a pipeline fact: derived on the qualified
      corridor facts by the bounded routing machinery, never a hand-drawn
      tile list; its path admission of record (road-legal, 2..47-tile bound,
      funds bounds) asserted by the same checks the delivered route used
- [ ] The route is genuinely competing — distinct path identity from the
      delivered route; descriptive duplicates refuse
- [ ] The route binding lands through ticket 07's parameterization with its
      full composition consistency suite green (schedule, plan digests,
      pin table, funds-model wiring)
- [ ] Infeasibility arm: if no second candidate is admitted, the round
      records the completed-search infeasibility with its diagnostics
      (the standing precedent from the random-world bounds) and the M8
      block's next steps are re-planned on that record rather than
      stretched
- [ ] No native launch, no claim, no signature in this ticket; any staging
      of this binding happens only under its own later operator approval
- [ ] Ledger row appended (route identity digests, admission evidence, the
      E36 context); `git diff --check` clean; `CONTEXT.md` pin intact; no
      commit/push
