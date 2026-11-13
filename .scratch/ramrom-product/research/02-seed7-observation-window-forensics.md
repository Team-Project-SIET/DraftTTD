# Seed-7 observation-window forensics (P2, offline, 2026-11-12)

Round scope: read-only analysis of the sealed E199 run bytes
(`artifacts/demos/playable-demo-d140ff9223ea4314a587e8d28808e8bb/`) to
answer the three questions E203 item 4 / E205 named: which
`verify_observation` check failed, what `observation_budget` computed,
and why the fourth observe receipt never landed. No launch, no
AdminPort, no grant, no sealed byte modified, no code change (any code
change would be a separate operator decision), no relabeling. This note
is a research record, not a decision of record.

## 1. The three answers of record

**Q1 — which `verify_observation` check failed: the first one, the
status check.** The run terminal (`result.json`) is
`"error": "ValueError: bounded native observation failed or
inconclusive"` — the message of the generic check block at
`app/simulation/openttd/freight_delivery.py:199` (`verify_observation`).
Receipt 3 (`s0-observe-2-response.json`) came back with
`"status": "WINDOW_EXHAUSTED"`, not `"OBSERVED"` — so the check
`r.status != "OBSERVED"` fired before any other check could. (The
phase-2 specific check would also have failed — `s[8]=38858` vs the
destination `a[6]=33228`, `s[9]=0`, `s[11]=22` still loaded — but the
status check fires first.)

**Q2 — what `observation_budget` computed: 4440 ticks, and it was never
the binding constraint.** `plan.a = [9, 12, 8, 147, 40145, 40144,
33228, 33484, 33741, 40144]` (`native-plan-0.json`): source tile
`a[4]=40145`, destination `a[6]=33228`; world width 256
(`runtime-identity.json`). Python:
`distance = |40145%256 − 33228%256| + |40145//256 − 33228//256| + 2
= |209−204| + |156−129| + 2 = 5 + 27 + 2 = 34`;
`budget = min(OBS_TICKS, 2048 + 128·34) = min(4440, 6400) = 4440`
(`freight_delivery.py:14` `OBS_TICKS = 4440`, `:161`). The .nut side
agrees: `ObservationBudget()` = min(4440, 2048+128·(DistanceManhattan+2))
(`freight_delivery_package/main.nut:137-141`). Receipt 3's bounded-
window figures were far inside: `s[0]−s[26] = 10484−9710 = 774` ticks
(check allows ≤ 4440) and `s[27] = 775` polls (check allows ≤ 4441) —
both PASS. The 60-economy-day guard, not the tick budget, ended the
window (§2).

**Q3 — why the fourth observe receipt never landed: it was never
issued.** The live loop issued `s0-observe-0/1/2` and verified each
inline (`freight_native_network.py:1133-1135`); the observe-2
verification raised the ValueError and the run terminalized FAILED, so
`s0-observe-3` was never requested (no
`s0-observe-3-request.json` exists in the sealed dir). The evaluator
reproduction later hit `KeyError: 's0-observe-3'` at
`freight_native_network.py:1551` — the offline re-verify path looks up
all four expected records
(`[records[cid(f"s{n}-observe-{i}")] for i in range(4)]`) and the
fourth is absent. Both errors are consistent views of one terminal:
the gate fired at receipt 3; the fourth receipt never existed.

## 2. Why the window exhausted: the 60-economy-day guard vs a long haul

The .nut Observe loop sets `WINDOW_EXHAUSTED` on five branches
(`main.nut:151,155,171`); with 774 ticks elapsed against a 4440-tick
budget, the tick branches cannot fire — the branch that fired is the
economy guard at `main.nut:151`:

```
s[1] − baseline[1] > 60  →  WINDOW_EXHAUSTED
```

`baseline` is the pre-start snapshot (`main.nut:204`), date
`baseline[1] = 712290` (matches `s0-read-8-response.json` `s[1]`, the
Python baseline of record). Receipt dates:

| Receipt | status | tick s[0] | date s[1] | s[1]−712290 | reads s[26]/s[27] |
|---|---|---|---|---|---|
| s0-observe-0 | OBSERVED | 8166 | 712319 | 29 | 6044 / 2123 |
| s0-observe-1 | OBSERVED | 9709 | 712340 | 50 | 8167 / 1543 |
| s0-observe-2 | **WINDOW_EXHAUSTED** | 10484 | 712351 | **61 > 60** | 9710 / 775 |

The guard is one shared 60-day economy budget
(`observation_economy_days: 60` in `PRELAUNCH.json` `budgets`) across
all four phases, starting at the pre-start date. The chain of record:

1. **The full-load wait consumed 50 of the 60 days.** Phase 1
   (`full native source loading observed`: `s[8]==a[4]` and
   `s[11]==f[5]=22`) completed only at day 712340 — 50 days after
   pre-start — because the source industry's supply rate filled the
   22-unit load target slowly under the full-load order.
2. **Ten days remained for transit + arrival + unload; the haul needs
   far more.** The source→destination Manhattan distance is 32 tiles;
   at the guard's expiry the vehicle stood at tile 38858 (row 151,
   col 202) — still ≥ 24 Manhattan tiles short of the destination
   (row 129, col 204). Movement continued throughout (the
   `MOVEMENT_STALLED` branch never fired).
3. **Derived pace estimate (supporting color, not a claim):** the
   vehicle covered ≥ 12 Manhattan tiles between receipts 2 and 3
   (40145 → 38858) in ≤ 775 ticks; at the record's 74-ticks-per-economy-
   -day day-roll (ADR-0001), 775 ticks ≈ 10.5 days ≈ the 11-day date
   gap (712340 → 712351) ✓ — i.e. ~1.1–1.2 tiles/day, so the remaining
   24-tile leg needs roughly 20+ more days. Even the best-case reading
   leaves the phase-2 arrival far outside the remaining window. The
   exact per-tile trajectory is UNKNOWN (the raw AdminPort frame dump
   `frames.json`, 2763 hex frames, was not parsed this round).

**Conclusion of record:** the designed gate fired as designed. Not a
code defect and not a capture defect: the selected seed-7 service
(a 32-tile-Manhattan haul whose full-load wait took 50 economy days)
cannot complete its delivery leg inside the 60-economy-day observation
window that the fences prescribe. The observation window is
distance- and production-rate-sensitive; seed-7's plan is the first
on-file random-world plan long enough (and its source industry slow
enough) to expose that boundary. Corridor-lineage deliveries fit the
window on short hauls; nothing here relabels them.

## 3. What this informs (a future design decision, never a claim)

Any future random-world observation design decision would weigh:
a longer `observation_economy_days`, a per-phase window split, a
distance-aware budget (`observation_budget` already scales with tile
distance in ticks, but the 60-day economy guard does not scale with
haul length), a start-to-load pacing change, or a different
full-load policy. All of those are design choices behind fresh operator
decisions and, where they touch native runs, fresh grants. This note
asserts none.

## 4. UNKNOWNs preserved

- The exact per-tile vehicle trajectory and true route length
  (parseable from `frames.json` hex; out of this round's scope).
- The source industry's production curve (why full load took 50 days;
  only the two endpoint dates are on file).
- Whether ANY pacing/policy variant could complete a 32-tile haul
  inside the designed fences — a design question, not answered here.
- Transit-time adequacy of `observation_budget` in general — the
  E203 UNKNOWN ledger item stands unchanged.

## 5. Traceability

Sealed bytes read (read-only): `result.json`, `native-plan-0.json`,
`s0-observe-{0,1,2}-request.json` / `-response.json`,
`s0-read-8-response.json`, `runtime-identity.json`, `PRELAUNCH.json`,
`frames.json` (structure only). Code of record pinned at HEAD
`f7b481a`: `app/simulation/openttd/freight_delivery.py:14,158-190,199`,
`app/simulation/openttd/freight_native_network.py:1133-1135,1541,1551`,
`app/simulation/openttd/freight_delivery_package/main.nut:137-141,151,155,171,204`.
Evidence lineage: E199 untouched at its own identity; this note adds
no bytes to any sealed directory.
