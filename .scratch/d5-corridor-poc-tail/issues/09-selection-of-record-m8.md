# 09: Selection of record (M8 part 2)

**What to build:** the optimizer's selection of record over the admitted
corridor route set — the pure selection layer run under its standing
boundedness (bounded simulation, ≤16 relationships, ≤8 services, bounded
solve time), producing the reproducible selection artifact naming the route
the delivered attempt will carry next. No attempt runs in this ticket; the
selection must be re-derivable from its frozen inputs.

**Blocked by:** 08 (Second-route admission).

**Status:** ready-for-agent

- [ ] The selection artifact of record exists: the frozen input set (the two
      admitted route bindings with their identities/facts) + the optimizer's
      chosen route + the provenance of every constraint applied
- [ ] Reproducibility asserted: re-running the selection over the same
      frozen inputs reproduces the same choice (deterministic contract; any
      bounded-solver nondeterminism property-recorded, never hidden)
- [ ] The selected route's binding re-validated post-selection (composition
      consistency suite green; the refused arms documented)
- [ ] Out-of-bounds or empty admitted sets surface as typed infeasibility of
      record — never a soft default to the delivered route
- [ ] No candidate lifecycle action inside this ticket (no staging / no
      signing / no claim / no launch)
- [ ] Ledger row appended (selection artifact digest, route of record,
      bis-reported bounds); `git diff --check` clean; `CONTEXT.md` pin
      intact; no commit/push
