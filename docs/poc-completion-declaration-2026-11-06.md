# PoC completion declaration — D5 corridor PoC (2026-11-06)

**Class: the single assembly of record that declares the corridor PoC
complete.** Ticket 13 (T-022) of `docs/specs/d5-corridor-poc-tail.md`, round
granted in-session by the operator instruction "do next Ticket"; offline
assembly only — no staging, no claim, no signature, no launch, no native run,
no push. Spec of record referenced throughout: the corridor PoC tail spec
declaring this declaration the finish line of the Phase A tail
(FD-A-2 … FD-A-6 of `docs/roadmap-and-scope-2026-11-05.md` §2).

## Operator adjudication of record (before assembly)

Ticket 13's evidence item "full delivery receipts of both delivered attempts
(corridor route + selected route)" conflicts with the retained record: both
consumed corridor rounds (6 and 7) terminated COMPLETE-not-delivered
(`NATIVE_CARGOFLOW2_COMPLETE` verified true, verdict
`CARGOFLOW2_LOADED_NEVER_DELIVERED`, delivery leg in transit at finish,
`unloadings []`), and no freight-DELIVERED receipt exists anywhere in the
retained lineage. Per the ticket-06/ticket-10 precedents the item was
adjudicated explicitly in-session (2026-11-06), never silently reinterpreted:

**Adjudication:** the item is satisfied by the COMPLETE-not-delivered class
of record — the corridor receipts stand as they are, cited verbatim below;
E36 stays open by its own rule and is carried as an open finding; the ticket
wording diverges from the record and the divergence is recorded here and in
the ticket file. No native run was or is authorized by this declaration.

## Evidence set of record (assembly; invention forbidden)

### 1. Corridor receipts of record — adjudicated COMPLETE-not-delivered

- Depot chain `D5-F12-DEPOT-3`
  (`artifacts/experiments/d5-corridor-depot-mutation-native-candidate-3/`):
  `NATIVE_DEPOT_MUTATION_COMPLETE` verified true, 6 retained receipt rows
  with the zero-residual funds chain joined (founding funds 489,650), zero
  residual per E82 class. Replayed of record: E126
  (`artifacts/experiments/p07-replay-d5-corridor-2026-11-06/round3-depot-chain/`).
- Corridor round-6 `D5-CARGOFLOW-2` (route-v1 pre-parameterization)
  (`artifacts/experiments/d5-corridor-cargoflow2-native-candidate-6/`, seal
  `e929d7b2…ec49`): `NATIVE_CARGOFLOW2_COMPLETE` verified true, verdict
  `CARGOFLOW2_LOADED_NEVER_DELIVERED`; 25 exchange receipt rows, funds echo
  at every instant, finance close funds 484,769 / income 0 / delivered 0;
  offset-35 funds 484,986 vs round-7's 484,985 (the one-unit divergence of
  record, carried verbatim never reconciled). Reconciliation of record E117
  (zero residual at all 25 observed instants, model end == finance 484,769).
  Replay of record: E126 (`route-v1-round6/`).
- Corridor round-7 `D5-CARGOFLOW-2` (the adjudicated v2 corner-swap arm)
  (`artifacts/experiments/d5-corridor-cargoflow2-native-candidate-7/`, seal
  `9c5f7272…e19257`): `NATIVE_CARGOFLOW2_COMPLETE` verified true, verdict
  `CARGOFLOW2_LOADED_NEVER_DELIVERED`; 25 exchange receipt rows, funds echo
  at every instant (series [485,217 … 484,770]), same verbatim finance
  close. Launched once with explicit operator authorization, no retry, no
  reconnect: E124. Replay of record: E126 (`route-v2-round7/`).
- The freight facts both arms share verbatim: empty bay arrival 712,250 (v2)
  vs 712,251 (v1); loads 5/10/15 @712,271; loaded departure 20 t @712,274;
  delivery leg in transit at finish, `unloadings []`. Day/tick figures are
  script-tick instants of the pinned observation script, never steady-state
  (ADR-0001 note). Corner edge 50,351↔50,352 strictly unobserved (v2 drove
  the full order path un-halted).

### 2. Both-route evidence with the selection artifact

- ≥2-executable-routes record: the bounded planning pipeline derived exactly
  two distinct simple paths between the pinned stops on the same pinned
  corridor world — the delivered route of record v1 and the corner-swap
  candidate v2 — at the freight-v2 3..32 class, each admitted by the same
  checks: E118 (offline derivation), E122 (round-7 staged at the v2-carrying
  composition, review 21/21 exit 0 zero findings), E124 (the v2 native
  ladder ran true end-to-end).
- Selection artifact of record: E119 — the P05 selection layer drove the
  frozen ticket-08 admitted set {v1, v2} and selected **v1**, candidate id
  `corridor-b2f80f46513436a102005f10`, selection digest == the
  `FREIGHT_ROUTE_DIGEST_V2` `b2f80f46…1f7131` of record; v2 remains
  ticket-08-admitted and unselected (never de-admitted, never relabeled).
- Identity discipline across the two arms of record: the one ladder schedule
  digest `5c0998f2…bf2d` byte-equal across both rounds; distinct plan-model
  digests (v1 `98d055c4…f506ca`, v2 `e1cafb23…c08b0`); round-6
  pre-parameterization (route_version None by resolver) vs round-7
  route_version 2; the attempt-identity guard refuses two shared
  `attempt_id` directories in one invocation by design, so the arms replay
  as separate siblings, never pooled (E126).

### 3. Taxonomy decision of record

- ADR-0001 (`docs/adr/0001-funds-taxonomy-of-record.md`, E125): OBSERVED
  retained receipt reads / DERIVED labeled arithmetic / CONTROLLED pinned
  ceilings / UNKNOWN stays; script-tick instants never steady-state; revenue
  is never reported as profit. Traveling in every replayed document of E126
  and asserted by the ticket-12 audit and suite.

### 4. Replayed reporting outputs of record

- Three fresh sibling outputs under
  `artifacts/experiments/p07-replay-d5-corridor-2026-11-06/`
  (`round3-depot-chain/`, `route-v1-round6/`, `route-v2-round7/`), one
  `analyze-native-attempts` invocation per consumed identity, commands of
  record in `REPRODUCE.md` (E126, ticket 12).
- Attribution audit of record: `/tmp/opencode/c12_p07_replay_audit.py` +
  transcript `/tmp/opencode/c12_p07_replay_audit_output.txt` — **64/64
  PASS, 0 FAIL** (identity rows world/save/seed 17/plan per attempt;
  prelaunch == sidecar seals; result digests re-hashed; corridor arms share
  the pinned corridor world, depot world distinct; ladder byte-equal across
  arms; plan-model digests distinct; route_version identities verbatim).

## Precondition verification (fresh, this round 2026-11-06)

- Offline gates exit 0: corridor trio (wire 85 + VM 11 + native 46) —
  **142 passed, exit 0**; P07 offline pair (`test_native_attempt_analytics.py`
  39 + `test_performance_insights.py` 28) — **67 passed, exit 0**
  (logs `/tmp/opencode/c13_trio.log`, `/tmp/opencode/c13_p07.log`).
- Manifests re-verified intact: `docs/authority/context-authority-supersession.json`
  `current_sha256` matches `CONTEXT.md` on disk — verified this round
  (`manifest-current-match: True`), pin `847d710a…984d`.
- Consumed identities sealed and untouched: full sweep over every retained
  PRELAUNCH tree — **40/40 `PRELAUNCH.json` digests == their sidecars, 0
  mismatches; 32 trees carry `LAUNCH-CONSUMED.json`** (consumed candidates
  1–2 of every lineage included); historical retained zone re-hash —
  **byte-stable vs the ticket-12 close (0 files added/removed/changed)**
  (`/tmp/opencode/c13_zone_now.sha256` compared with
  `/tmp/opencode/c12_zone_after.sha256`).
- Terminal identity verdicts stand verbatim from the retained result
  documents (no relabeling): `INVALID_SITE` round-1, `ENGINE_PIN_MISMATCH`
  round-2 halts preserved as evidence (E36 class); the six
  `NATIVE_*`/`PHASE_*` terminal states above.

## Acceptance criteria checklist (each cited to its anchor)

1. **Fresh candidate round walked (FD-A-2, T-002..T-005 gates)** — the
   staging/review/Gate-C/one-launch discipline executed every native round:
   consumed candidates staged fresh, reviewed independently, signed at the
   boundary, launched once each — anchors: E104 (round-1 one launch,
   `INVALID_SITE` halt preserved), E110 (round-2 one launch,
   `ENGINE_PIN_MISMATCH` halt preserved), E116 (round-6 one launch,
   COMPLETE), E124 (round-7 one launch, COMPLETE), with the staging/review
   rows E107/E108 and E121/E122. **PASS.**
2. **Verdict reconciliation (FD-A-3, T-006)** — the offline truth replay of
   record reproduced round-6's walk exactly, zero residual at all 25
   observed instants, model end == finance 484,769 — anchor: E117.
   **PASS** (delivered class adjudicated COMPLETE-not-delivered; see
   adjudication above and open item E36).
3. **≥2 natively executable routes + optimizer selection (FD-A-4, T-020
   M8)** — exactly two distinct simple paths derived and admitted by the
   same machinery; the selection layer selected v1 with the selection
   artifact of record; v2 admitted, invariant-pinned, and natively ran true
   — anchors: E118, E119, E122, E124. **PASS.**
4. **Funds taxonomy settled (FD-A-5, T-021 first half)** — the operator
   decision recorded as ADR-0001 with the OBSERVED/DERIVED/CONTROLLED/UNKNOWN
   discipline traveling in every replayed document — anchors: E125, E126,
   E124's funds-series verification. **PASS.**
5. **Reporting closure looped on corridor native receipts (FD-A-5, T-021
   second half)** — the D5 receipt generations replayed into three fresh
   sibling outputs of record with world/seed/plan attribution intact,
   64/64 audit PASS, failed plannings never dressed as delivery receipts —
   anchor: E126. **PASS.**
6. **Completion declaration assembled (FD-A-6, T-022)** — this document,
   operator-reviewed before ledger landing; the E-row append follows below
   — anchor: this file + E127. **PASS** (on landing).

## Open items carried by their own rules (never fudged)

- **E36 — the delivered-class finding**: D5 native freight **delivery**
  remains not proven; both corridor attempts loaded and departed but no
  delivered receipt exists. Closes only when a genuinely competing
  executable route carries native DELIVERED receipts. Carried open,
  observed, UNKNOWN outcome — not discharged by this declaration.
- **E114 twin-vs-native cross-reality**: twin walks 484,775 vs native
  484,769/484,770 — UNKNOWN, carried open by its own rule.

## Phase A terminal state

With this declaration landed (its E-row appended, preserving every prior
row) and the round committed, Phase A of `docs/roadmap-and-scope-2026-11-05.md`
is terminally closed: FD-A-2 … FD-A-6 all walked under per-round operator
gates; the corridor PoC stands declared complete on the record above; the
spec `docs/specs/d5-corridor-poc-tail.md` is discharged. Nothing post-PoC is
opened by this document; any successor work needs its own explicit
authorization. Open items E36 and the cross-reality UNKNOWN persist as open
findings of the record — Phase A closes with them observed, not resolved.
