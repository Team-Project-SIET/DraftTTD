# 03: Candidate-8 staging (delivered-class round)

**What to build:** one staging round advancing the lineage identity to
candidate-8 — composing once from the settled tree with the
operator-approved binding choice — after which the staged state is
review-perfect and pre-consumption.

**Blocked by:** 02. **Blocked-to:** 04 (independent review)

**Status:** done 2026-11-06 (the round granted in-session by the
operator's "do all tasks until end" direction; the binding adjudication
carried on the spec default = the v2 corner-swap, binding id 2, the
delivered (2, 2) arm; offline staging only — no native run; one commit,
no push)

**Supersession of record inside this round**: the first composition
identity candidate-8 froze its staged byte-picture and was then refused
by the attempt's own preflight surface — the staged budget and
expected-readback pins had ridden the v1 arm (planned_exchanges 25)
over the correct delivered policy (route_version 2 / schedule_version
2, 26 rows, grid `d5-cargoflow2-ladder-grid-v2`). The tree's
`prepare` was arm-fixed in place (the budget, expected-readback and
CLI `--schedule-version` surfaces now resolve the arm), the failed
staged bytes stay preserved at their failed state under their own
directory — never signed, claimed or launched, never relabeled or
regenerated — and the identity advanced candidate-8 → candidate-9 by
the standing stale-supersession rule (the candidates-3/4 precedent).

- [x] Identity advanced at the round-identity constant with the
      lineage comment carried truthfully (1–2 consumed verdicts of
      record; 3–4 seal-superseded; 5 terminal halt-class; 6–7 terminal
      COMPLETE-not-delivered; 8 staged superseded by its own staging
      defect of record; 9 the delivered-class attempt —
      `d5-corridor-cargoflow2-native-candidate-9`)
- [x] The binding adjudication recorded before composition (the spec
      default carried: the v2 corner-swap, binding id 2, per the E36
      closure rule and the operator's in-session full-tail direction);
      ONE `prepare` from the settled tree at the arm-fixed state —
      `PRELAUNCH PASS` first attempt (exit 0), standalone `preflight`
      → `PREFLIGHT PASS` (exit 0), pre-auth `verify` →
      `AUTHORIZATION_UNVERIFIED` / `CLAIM_ABSENT` (exit 1 by design)
- [x] Staged figures of record: seal == sidecar ==
      `b29c03a4388d87262377cbf96d3b206feea33623400f338b20f95559d49389fa`
      ; `schedule_version` 2 beside `route_version` 2; staged plan
      digest `313879bd…216fda` and staged schedule digest
      `3132bfa0…5e0527` (26 rows, tails at 60); frozen chain 3,502;
      prerequisite after-save `183b2027…6ea6` re-verified; grid
      `d5-cargoflow2-ladder-grid-v2` (budget 65, tail 60, offsets
      0..60); pre-consumption root exactly the staged 4 entries — no
      CLAIM / AUTHORIZATION / LAUNCH-CONSUMED / result marker
- [x] Native composition suite re-run after the identity advance (48
      passed); `ruff` clean; `git diff --check` clean; `CONTEXT.md`
      pin `847d710a…984d` intact; the new `--schedule-version` CLI
      surface landed with the composition (option + arm-passing
      metadata); one commit, no push; no staging rerun after
      supersession (a fresh identity only, as recorded)
