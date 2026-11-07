# 02: Offline delivered-cycle fix + typing

**What to build:** the offline fix of record that lets the delivery cycle
complete inside the ladder — ladder/observation extensions through the
standing parameterization machinery plus the delivered-class verdict
typing in the wire contract — with regression locks born from the failing
state and the discipline of the E114/T-009 fix precedent (lock RED
pre-fix, GREEN post-fix).

**Blocked by:** 01. **Blocked-to:** 03 (staging, the operator binding
decision in-session)

**Status:** done 2026-11-06 (the round's operator grant given in-session;
offline-only — no staging, no claim, no signature, no launch, no native
run; RED-first locks observed RED, then GREEN post-fix; one commit, no
push)

**The delivered arm of record** (the (2, 2) pairing): the 26-row ladder
derives `flow-12` at anchor+60 = day 712,292 (the settle margin over the
loaded return's unload ETA 712,289–712,290) with both tails riding that
same economy day, inside the 65-economy-day day budget (authority last
day 712,293 = L + 65). The extension rides the v2-bound derivation and
the binding-shared surfaces: the module's own canonical encoder drops
the None `schedule_version` key, so every v1 digest stays byte-equal.
Figures of record at the GREEN gate: delivered plan digest
`313879bd…216fda`, delivered schedule digest `3132bfa0…e0527`, delivered
funds walk finish figure 488,069 (leg charges 6 across flow-11→flow-12).

- [x] The composition fix executed per the diagnosed fix space:
      cycle-completion observation stop (`flow-12`) appended to the
      ladder through the standing parameterization machinery as the
      (route_version=2, schedule_version=2) arm; `schedule_version`
      carried by the plan / requests / readbacks as the arm key (the
      handler never echoes it — `parse_for` injects the correlated
      request's arm and a disagreeing frame refuses); the delivered-class
      verification typed by the standing contract (`CARGOFLOW2_
      DELIVERY_VERIFIED` accepts, and the verdict lock proves the
      round-6/7 terminal class can never reach it)
- [x] No fail-closed pin modified; every v1 digest byte-equal
      (`REQUEST_PLAN_DIGEST` `98d055c4…f506ca`, binding v1
      `9a4a0778…93e45e`, binding v2 `26408e77…b274`, the (2, 1) plan
      `e1cafb23…c08b0`, v1 schedule digest `5c0998f2…bf2d`) — observed
      byte-equal through the landed encoder; the delivered arm lands its
      own constants/sequences/maps/assert cluster beside the untouched
      v1 cluster
- [x] Regression locks: the delivered-class lock and the (2, 2)-keying
      locks observed RED (`AttributeError` / `unknown cargo-flow
      delivery schedule version: 2`) and GREEN post-fix; the verdict lock
      replays the retained round-6/7 phases and types
      `CARGOFLOW2_LOADED_NEVER_DELIVERED` (never the delivered class);
      the funds-fence walk covers the unload leg (flow-12 + both tails
      reconcile the standing charge lattice, `_LEG_RUNNING_CHARGES` = 6)
- [x] Focused suites green: wire 90 + native 48 (the corridor's new
      count, +5 wire / +2 native delivered locks) + P07 pair (39/28)
      unchanged; `ruff` clean (all touched paths); `uvx ty` = the
      pre-existing tolerated corridor `connect` diagnostic + the 3
      pre-existing analytics diagnostics, no new findings; `git diff
      --check` clean; the `CONTEXT.md` sha256 of record
      `847d710a…984d` intact; one commit, no push. Zone evidence: the tree's
      diff against `5cdfb83` names exactly the five files this round
      edits (wire module, native module, shipped `main.nut`, wire
      tests, native tests) and no `artifacts/` byte moved (the
      `/tmp/opencode/c13_zone_now.sha256` baseline was absent when
      re-checked — /tmp cleaned between sessions; the diff-names
      against the last committed tree carry the same claim)
