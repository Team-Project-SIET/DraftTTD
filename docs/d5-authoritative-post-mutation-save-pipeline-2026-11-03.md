# Path A — Authoritative post-mutation save pipeline (design record, 2026-11-03)

Status: **DESIGN ONLY.** This document changes no source, stages no candidate,
signs nothing, launches nothing and consumes nothing. `D5-FREIGHT-4` stays
staged-only and byte-untouched; consumed candidates and terminal verdicts stay
verbatim; the `CONTEXT.md` authority pin is untouched. Implementation is gated:
each round below needs its own operator approval sequence before any write.

## 1. The E77 gap, restated as a design problem

The implemented depot-mutation pipeline (`proof/corridor_depot_mutation_native.py`)
proves the E58 §2.1 fix natively and certifies it inside one consume-once
runtime: it retains the pre-mutation `session-before.sav`, emits only a
diagnostic `after-diagnostic.sav` (`diagnostic=True` — no strict health gate),
retains logs, then reaps and disposes the owned workspace. Its world binding of
record deliberately stays the pinned A1 prerequisite after-save
`3748e00c…5420bd` (never modified; re-digested intact post-run).

E77 measured the consequence: a downstream freight attempt loads that same A1
after-save verbatim (`PREREQUISITE_ATTEMPT_SOURCE_SAVE_LOAD`), and the
F-12-DEPOT-2 run itself measured that loaded world reading
`connected_depot_to_front false` / `connected_front_to_depot false` at
`before-00`. The freight `site-00` admission demands the exact opposite
(`corridor_freight_v2.py:1276-1278`, E58 branch-4 strict), so any freight
attempt bound to the A1 after-save is a foreknown single-exchange refusal.

The E58 sequencing presupposed a **post-fix after-save** that the implemented
depot pipeline never emits. Path A closes exactly that gap:

> A depot-mutation pipeline variant that **produces, retains and independently
> verifies an authoritative post-mutation after-save**, which a fresh freight
> attempt then loads as its source world — with the mutation facts retained on
> disk and re-proven, so branch-4 strictness holds *strictly* (never relaxed).

## 2. Precedent already in the tree

The save-and-retention machinery exists and is proven; Path A reuses it
verbatim (no new save mechanism):

- `app/simulation/openttd/proof/road_mutation.py:325` —
  `async def save(backend, prepared, name, *, diagnostic=False)`: strict
  process health (skipped only in diagnostic mode), native console `save` with
  an absolute quoted path, single completion marker
  (`"Map successfully saved to '…'"`), duplicate-marker and native-failure
  refusal, nonregular/symlink/redirect/empty-file refusals, 15 s bounded wait,
  and the returned value is the **sha256 of the saved bytes**.
- `app/simulation/openttd/proof/corridor_extension_native.py:1513` — the A1
  extension attempt saved the authoritative world **in the same session,
  after the phase gate completed the prescribed work and before the finally
  cleanup**: `after_save = await save(backend, prepared, "after")`, bound into
  `receipt.json` as `after_save_sha256`, and the `verify` replay requires the
  retained attempt to bind its own after save (binding tuple above, e.g.
  `corridor_extension_native.py:1188`, `:1199`).
- `app/simulation/openttd/proof/corridor_freight_v2_native.py` (`freight_facts()`)
  — the consumption-side model: the freight family re-validates the
  prerequisite attempt's identity, consumed claim, after-save digest against
  the pinned constant, receipt binding, station/route receipts — staging
  refuses on any drift, before any run.

Path A bestows this exact A1 pattern on the depot family: the depot attempt
of record saves its own `after.sav` authoritatively, and the freight family
gains a versioned branch that consumes it the same way `freight_facts()`
consumes the A1 extension today.

## 3. Data flow (end to end)

```
A1 after-save 3748e00c…5420bd            (immutable pinned prerequisite)
        │  staged fresh copy as source.sav (retained save never opened/moved)
        ▼
[D5-F12-DEPOT-3]  one native attempt, schema d5-f12-depot-prelaunch-v2
   6/6 exchanges … phase gate DEPOT_MUTATION_GATE_PASSES
   └─ on the complete path, BEFORE cleanup (still inside the live session):
        after_save = await save(backend, prepared, "after")     # strict health
        receipt.json += {after_save_sha256: <digest>, save_size_bytes, …}
        result.after_save_sha256 = same
        artifacts/…candidate-3/after.sav retained           ← THE new world of record
        cleanup unchanged (reap, credential, dispose workspace)
   verify (offline) requires:
        receipt binding + digest equality + POST_MUTATION_SAFE …
        plus the round-3 reload receipt (below) for full facts
        verification arm: F12_MUTATION_COMPLETION_VERIFIED (existing identity)
        + NEW binding file after-save-binding.json
        operator decisions: staging approval → review → Gate C → one launch
        (same gates as candidate-2; new attempt identity, no re-labelled reuse)
        │
        ▼
[D5-F12-DEPOT-RELOAD-1]  family corridor_depot_recheck (observe-only),
   schema d5-f12-depot-reload-prelaunch-v1, prereq = candidate-3 after.sav
   (fresh copy; retained save never opened/moved: same discipline as A1)
   1 exchange (observe at the depot), 1 connection, zero mutation,
   measures EXACTLY the freight v3 world facts:
     depot 45487 present/front 45743/owner 0/linked,
     edge TRUE both directions; funds 489650; fleet 0 (empty in_depot rows)
   recording after-reload-receipt.json (facts + loaded-source digest bound)
        verification arm: DEPOT_RELOAD_FACTS_VERIFIED
        operator decisions: staging → review → Gate C → one launch (observe
        only has always been a live OpenTTD native session: like the
        accepted-survey family; not a locked GSVehicle claim)
        │
        ▼
[D5-FREIGHT-5]  family corridor_freight_v2, version-pinned
   WORLD_PIN_VERSION = 3, schema d5-freight2-prelaunch-v2
   prereq = the extension lineage receipts (history unchanged,
   still verified from the pinned A1 candidate-3)  AND
   the depot-mutation attempt of record (chain) AND  its
   after-save-file digest == reload's loaded-source digest == new pin
   source world = a fresh COPY of candidate-3/after.sav (never the file)
   package/composition/schedule/schedule digest: BYTE-IDENTICAL v2 policies
   (route/witness unchanged; max_cost 5000 unchanged; but the funds WORLD
   pin moves with the save: FUNDS_AT_DEPOT_MUTATION_CLOSE = 489650)
   site-00 gate yard: depot_edge strictly TRUE — UNCHANGED at
   corridor_freight_v2.py:1276-1278 (branch-4 strictness is PRESERVED, and
   now it is satisfiable in the runtime instead of faked)
```

## 4. Save provenance, integrity, retention, lifecycle, cleanup, failure handling

- **Provenance.** The authoritative save is written only by the run of the
  consumed completed attempt (`DEPOT_MUTATION_COMPLETE` reached with the
  recorded receipts), inside the live session after the phase gate and before
  the finally cleanup, through the strict (non-diagnostic) `save()`. Its
  schema line binds: `attempt`, `milestone`, `directory`, `prelaunch_sha256`,
  `after_save_sha256`, `save_size_bytes`, `saved_at_fleet_exchange =
  "fleet-00"`, `source_world = 3748e00c…5420bd` (the staged fresh copy), the
  depot front/owner witness recorded in the after gate, and the closing funds
  489650 — the same receipt-binding tuple shape the A1 attempt used
  (`corridor_extension_native.py:1188`).
- **Integrity.** No line of source reads, copies silently, moves, or
  rewrites the retained save after `save()` returns. The digest is frozen
  into (a) `receipt.json`, (b) the run `result.json`, and (c) the executed
  `after-save-binding.json`. `verify` (offline, no connection) re-reads the
  file and refuses any drift between these three points. The reload attempt
  in round 3 re-loads a **fresh copy** and binds the loaded-source digest,
  giving the downstream three-way chain: run-time digest == retained-file
  digest == reload-session loaded-source digest.
- **Retention.** The save lives in the consuming attempt's own candidate
  directory (`artifacts/…/d5-corridor-depot-mutation-native-candidate-3/
  after.sav`), exactly like the A1 attempt's `after.sav`. The workspace copy
  created by native save is never moved: the runner copies the file into the
  candidate directory at the same moment it receives the digest, and the
  cleanup policy (dispose owned workspace) therefore never touches the
  retained copy.
- **Lifecycle.** The save is immutable from the moment `save()` returns:
  never rewritten by a later attempt, never regenerated, and never the input
  of another save. Round-3 reload or any future re-run must copy it
  (`shutil.copyfile`), exactly as the A1 world was copied into each staging
  workspace (`verify_staged_source_save` checks the staged copy each time).
- **Cleanup.** The existing cleanup policy list gains one line — the
  authoritative save is retention IN ADDITION to (not in the place of) the
  existing "retain session logs and the pre-mutation save; remove
  credential; dispose owned workspace; never modify the retained save or any
  historical artifact" statements. Cleanup/disposal therefore never removes
  the authoritative save once written to the candidate directory. The socket
  policy and all E68-style endpoint certifications are UNCHANGED by this
  design. The workspace disposal still removes the staged composition — the
  delta is positive (one extra retained file) only in the candidate dir.
- **Failure handling.** If the strict `save()` raises inside the complete
  path (health, marker, bounded wait, empty file), the `finally` diagnostic
  path of the depot pipeline stays as it is today (diagnostic-only,
  non-blocking), and the attempt is not allowed to claim completion: the
  runner writes the discriminating terminal status
  `PHASE_COMPLETE_SAVE_REFUSED` (schema `depot-mutation-phase-outcome-v1`
  records `save_error` verbatim like `after_save_error` today)
  on TOP of the phase receipts, and `verify` refuses any completion claim
  without the authoritative digest (it becomes a hard receipt field). The
  attempt is then terminal and byte-preserved — consumed, never retried,
  never relabeled; the operator's next step is a fresh identity. The E68
  socket-INode ambiguity precedent is preserved as-is: `cleanup.json` keeps
  reporting the Erlang endpoint policy verbatim.
- **Save content sanity (cheap offline checks at verify time only).** The
  retained save must (a) fit the A1 welcome class (`seed 17`, start day
  712223, 256×256, revision 15.3) because the freight world-composition
  expectations rest on those facts, and (b) hash non-empty, non-regular and
  not-symlink rejections (enforced inside `save()` itself). No byte-level
  determinism across attempts is claimed or required: one attempt → one
  authoritative save → the digest pins the exact bytes of record.

## 5. Branch-4 strictness is preserved, not weakened

Nothing in Path A relaxes acceptance criteria:

- The `site-00` gate (`corridor_freight_v2.py:1276-1278`) keeps demanding
  `depot_edge is True` — and every other admission line of §"site
  admission" (unpaused world, zero vehicles, funds exact, road-ready read,
  both truck stops, station radii, acceptance 8/8 witness, route pairs).
- The freight schedule, package, and all existing budgets stay byte-identical.
  The mutation is carried BY THE WORLD of a fresh upstream consumer chain
  (the F-12 attempt's receipts), exactly the way the A1 extension world
  carried the construction facts the freight family today consumes through
  receipts (`freight_facts()`).
- What was never true never becomes true: Path A only makes the propagated
  facts *loadable* natively in a fresh runtime world. The loader refuses any
  post-save receipt that is out-of-line with the pinned depot receipts
  (both-directions TRUE edge, front 45743, owner 0, funds 489650, fleet 0) —
  a strict increase in back-checks, none lessened.

## 6. Unchanged artefacts (must remain byte-identical)

- `D5-F12-DEPOT-1` (terminal `PHASE_HALTED_PREFIX_PRESERVED`),
  `D5-F12-DEPOT-2` (terminal `NATIVE_DEPOT_MUTATION_COMPLETE` with its
  pre-mutation binding intact).
- `D5-FREIGHT-4` stays **staged-only** (`PRELAUNCH.sha256` seal),
  un-consumed, and byte-untouched forever. It is not "repaired in place":
  a consumed attempt is never edited; the lines that changed for the world
  (schedule digests etc.) instead require a new identity. After Path A the
  freight identity becomes `D5-FREIGHT-5` and the staged versioned schema
  becomes `d5-freight2-prelaunch-v2`, never a silent in-place mutation of
  consumed artifacts (E54 lineage precedent: the once-staged never-consumed
  name `D5-FREIGHT-4` is not reused by attempt 5).
- The depot pipeline family keeps every current behavioral branch:
  E72 "instrument false negative" documentation, E73 fix round, the six
  exchange counts, the cash chain, and both receipts schemas.

## 7. Implementation plan (offline, gated — nothing executes without its own approval sequence)

Each round is an **offline implementation round first** (tests, ruff, ty,
ws-clean), and only then the normal operator gate sequence. No round starts
because another one ran; approval is asked at every gate.

**Round 1 — this design record (no source change).** This document; E78
ledger row; task/handoff updates at review time. STOP for operator review
before any implementation.

**Round 2 — depot save emission (offline).**

- Identity bump: `DEPOT_MUTATION_ATTEMPT = "D5-F12-DEPOT-3"` with the
  E24/E54 comment-record pattern (consumed -1 terminal, consumed -2 terminal,
  no name reuse); docstring updated; test pins updated.
- `corridor_depot_mutation_native.py`: on the `DEPOT_MUTATION_COMPLETE`
  branch (after `receipt.json` write, before the finally cleanup) call
  `await save(backend, prepared, "after")` (strict), bind
  `after_save_sha256` into `receipt.json` and the result; add the
  `PHASE_COMPLETE_SAVE_REFUSED` failure arm (save failures are terminal,
  preserved, never retried).
- New `after-save-binding.json` (schema `d5-f12-depot-after-save-binding-v1`)
  written by `verify` only when the digest triple is consistent:
  `{attempt, prelaunch_seal, after_save_sha256, save_size_bytes,
  source_world: 3748e00c…5420bd, saved_at: "fleet-00", funds_at_close:
  489650, edge_facts: {depot_present, front_read: 45743, owner: 0,
  depot_linked, both_directions: true}, …}`.
- New prereq-version constants: schema `d5-f12-depot-prelaunch-v2`
  (candidate-1/2 keep binding the v1 schema bytes they carry); the
  prerequisite machinery gains the after-save-retention checks that refuse
  staging without `after.sav`/binding consistency (a staged world of record
  must ALWAYS be exactly one digest, the retained authoritative save).
- Tests: native replay tests for the save arm, the binding file and the
  refusal arm; VM suite untouched (Squirrel world unchanged); ruff/ty/ws
  clean; REPRODUCE updated at each executed gate only.
- Gates upon approval: staging approval → read-only review → Gate C (one
  signing, Option-1) → one launch approval → post-run `verify`
  (`F12_MUTATION_COMPLETION_VERIFIED`, now requiring the retained digest) →
  cleanup certified as today → manifest including `after.sav`.

**Round 3 — reload family (offline, new small family).**

- `proof/corridor_depot_recheck_native.py`: observe-only depot attempt,
  1 exchange (`reload-00`, the depot observe op), budgets
  (1 launch / 1 connection / 1 request / max_cost 0 / readiness 45 s /
  request 10 s / total 120 s), prereq = the round-2 candidate directory
  (fresh copy of its `after.sav`; retained file never opened), package = the
  depot composition (same staged bytes), staged under identity
  `D5-F12-DEPOT-RELOAD-1` with schema `d5-f12-depot-reload-prelaunch-v1`;
  verify arm `DEPOT_RELOAD_FACTS_VERIFIED` requiring the measured facts to
  equal the round-2 binding exactly (digests AND facts).
- Tests: native replay for the recheck family, VM reuse of the depot stub
  (Squirrel precursor), ruff/ty/ws.
- Gates upon approval: staging → review → Gate C → one launch (an observe
  session requires a native runtime, same as the accepted-survey family).

**Round 4 — freight v3 world-pin version (offline, additive family version).**

- `app/simulation/openttd/corridor_freight_v2.py`: NEW constants additive
  next to the v2 ones: `WORLD_PIN_VERSION = 3` (composed constants naming
  per E51: the depot-mutation lineage pins the new after-save byte digest
  and the funds-at-mutation value), `FREIGHT_ATTEMPT_V2` naming updated by
  the E54 pattern to `D5-FREIGHT-5`.
- `proof/corridor_freight_v2_native.py`: `freight_facts()` gains the
  versioned branch (the consumed-extension receipts of the pinned A1
  candidate-3 remain required history AND the round-2 depot attempt + round-3
  recheck receipts are also required, digests cross-bound; staging copies
  `candidate-3/after.sav` instead of the A1 save, digest re-checked in the
  staged copy via `verify_staged_source_save`).
- `d5-freight2-prelaunch-v2` schema (additive; D5-FREIGHT-4 keeps replaying
  its v1 bytes), schedules/packages/digests untouched.
- Tests: prereq-addressing tests for the new lineage; both-families replay;
  ruff/ty/ws.
- Gates upon approval: staging → review → Gate C → one launch → This round
  CLOSES F-12 finally (E-vocabulary: `D5-FREIGHT-5` delivered-with-native
  evidence; site → arm → unload → monitor — the existing E58 branch-4-closed
  freight design, strictly satisfied now in runtime).

**Round 5 — final verification of record.** Nothing executes in 5 beyond
REPRODUCE/ledger row updates (E79+), the manifest/package checks, and the
rounds' own evidence updates; the six-step workflow's step 6 closes a
FREIGHT-5 attempt, not any signal of round 5 (it is a new workflow).

## 8. Risks and mitigations

| Risk | Mitigation of record |
|---|---|
| Save happens while the live GS/AI session still holds state (fleet-00 just measured) — mid-session mutation receipts could differ from the loaded-back world | The reload round (3) exists precisely for this: the digest-only round-2 binding is never trusted alone; the freight family binds the round-3 measured facts (the A1 pattern of receipts + the load re-check) before any construction |
| Native save file bytes are not deterministic across attempts (timestamps/RNG state in the OpenTTD save format) | Not required. One attempt issues one authoritative save; the binding pins those exact bytes; later rounds consume the file, never re-run the race |
| Freight `expected_funds` pin drift (490257 → 489650) | Round-4 makes the funds pin explicit per world-pin version (the A1 pin stays untouched for its own history), and the site-00 gate then enforces the exact mutation-close funds consumed from the source world receipts — no silent drift |
| The lake of evidence already consumed (census/survey/depot E-series) binds the A1 after-save as the world of record | Those attempts are terminal and byte-frozen; the new versioned constants live ADDITIVELY in the flat family-across-space (no retrofit); monthly evidence handlers unaffected |
| The depot attempt's strict save fails in mid-session, turning a completed mutation into a refused NON-completion | `PHASE_COMPLETE_SAVE_REFUSED` remains terminal evidence and the mutation gates stay refused until the fresh identity; never silently falls back to a diagnostic save as the authoritative record |
| Retained-file accidental modification on later copies | Every downstream read uses fresh copies staged by the consumers with `verify_staged_source_save`; the retained file itself is never the input of a write, move or save anywhere |
| `D5-FREIGHT-4` byte-replay breaks if freight v2 pins are retouched in place | They are NOT. Freight v2 constants keep pinning the consumed A1 world; Path A's freight version is v3 (WORLD_PIN_VERSION 2→…; schema d5-freight2-prelaunch-v2; identity D5-FREIGHT-5), additive, E51 convention |
| Reload session requires update-based formatting into census/depot observed worlds | None needed: the `observe` family at the depot reads live facts (census children) that are already verified; the recheck family re-uses the depot observe op verbatim |

## 9. Open operator decisions at review time (nothing executes before these)

1. Approve Round 2 offline implementation (identity bump + save arm).
2. Approve Round 3 offline implementation (recheck family; identity choice
   `D5-F12-DEPOT-RELOAD-1` vs folding into a v2 schedule version — this
   design prefers the separate family, mirroring the accept-survey
   precedent, because the budgets and gates for a retry-class world-recheck
   attempt are cleanly isolated from the mutation attempt's one-shot
   signaling).
3. Approve Round 4 offline implementation (freight v3 version constants).
4. After offline implementation, each round's own natural gates run in
   sequence (staging → review → Gate C → one launch), every one asked
   explicitly.

Nothing in this document authorizes execution of any kind.
