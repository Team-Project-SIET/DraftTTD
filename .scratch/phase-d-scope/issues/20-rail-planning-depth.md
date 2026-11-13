# 20: Rail planning depth

Type: task
**What to build:** rail planning candidates over random-world geometry with honest typed refusals: distance/geometry classes, the quoting contract as ticket 08's cost model, and the five 15.3 API gaps enforced as typed constraints. From the operator's perspective: rail v1 refuses, never assumes, what the script API cannot observe.

**Blocked by:** 18 (rail tracer corridor).

**Status:** ready-for-agent
**Gates:** implementation starts only after M0 approval; offline only, zero native claims; no commit.

- [ ] Candidate generation over random-world geometry per ticket 08's terrain-basis decision; unsupported shapes refuse with named classes.
- [ ] Quoting contract per ticket 08 (in-session test-mode quoting as the offline cost model; the order-distance handling the decision fixed).
- [ ] The five API gaps (no block-occupancy readback, no slope→track oracle, no curve-limit API, base-price-only quoting, precondition aborts) each carry a typed refusal or a modeled constraint exactly as the decision fixed.
- [ ] Suites green offline; v1 exclusions (bridges/tunnels, NewGRF stations, conditional orders — as decided) typed out of scope; zero native claims; no commit.
