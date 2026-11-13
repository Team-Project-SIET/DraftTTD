# 15: Backbone offline bar (M2 exit)

Type: task
**What to build:** the loop's offline lifecycle green end-to-end at the v2 window, with the battery commands of record frozen and documented — the last offline bar before any battery grant request. From the operator's perspective: the whole WS-D1 fix set is integrated and the battery's invocation is no longer designable, only approvable.

**Blocked by:** 12 (window-v2 budget field), 13 (capture-scheduler capacity), 14 (loop census integration).

**Status:** ready-for-agent
**Gates:** implementation starts only after M0 approval; this ticket requests no grant, stages nothing, launches nothing; no commit.

- [ ] The `--cycles N` prepare/preflight lifecycle green at the v2 window, end-to-end offline.
- [ ] The three landed WS-D1 fixes integrated without weakening any typed surface (integration checks over all three).
- [ ] Battery commands of record frozen and documented in the run's doc of record, before any grant request.
- [ ] Focused suites green; lint and type checks of record clean on touched paths.
- [ ] No native run, no staging, no grant requested; no commit.
