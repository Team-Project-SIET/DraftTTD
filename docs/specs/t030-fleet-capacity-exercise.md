# T-030 — Fleet/capacity native exercise (Phase B, P2 backlog)

Canonical fleet lane of record (E2 family). Goal of record
(`docs/roadmap-and-scope-2026-11-05.md` §3, T-030 row): a native
purchase/dispatch/unpause exercise at 15.3 with canonical correspondence;
done-ness = native exercise receipts + canonical correspondence record +
E-row. E2 (`artifacts/runtime/canonical-fleet-create-q3/`,
`canonical-fleet-reload-q3/`) proves the two prerequisite capabilities:
canonical constructed-fleet creation
(`CANONICAL_CREATED_PENDING_FRESH_PROCESS_RELOAD`, protected save
sha256 `51e45689ae40dfa53c2cc150a05076fcb6e5cc2f38ec4eff56908372ab1297eb`)
and fresh-process reload-only correspondence
(`CANONICAL_RELOAD_ONLY_VERIFIED`, purchase/dispatch/unpause disabled by
contract).

## Dependency map (2026-11-11 audit)

1. Phase A terminal closed (T-022, E127, 2026-11-06) — DONE.
2. F06/F11 prerequisite capabilities (create + fresh reload, E2) — DONE;
   retained bytes re-verified 2026-11-11 (both run-dir manifests 0
   mismatches, no byte modified).
3. Exercise machinery offline — DONE and re-verified at HEAD: wire
   contract `app/simulation/openttd/freight_canonical_dispatch.py`
   (`BoundaryRequest`/`BoundaryReceipt`, `require_stable_boundary`,
   `dispatch_common` purchase→dispatch→unpause,
   `qualify_paused_purchase`, `unpause_native`), collectors
   (`verify_intervention_snapshot`), the byte-pinned staged bridge
   (`freight.staged_package(..., canonical=True)` composing
   `canonical.nut`/`canonical-collector.nut`): the bridge source is
   titled "Qualification-only stopped-fleet acquisition and
   acknowledged dispatch" and carries every handler the exercise
   needs (`canonical-arm`, `canonical-start`,
   `canonical-dispatch-read`, `canonical-dispatched`,
   `capacity-add` with pause-level and date-equality gates,
   `capacity-read`). Lane suites green at HEAD: `test_canonical_fleet_driver`
   19, `test_freight_canonical_dispatch`+`test_freight_canonical_integration`+
   `test_freight_canonical_transport` 25, `test_canonical_reload_only`+
   `test_canonical_reload_context`+`test_canonical_failure_reporting`+
   `test_freight_canonical_runtime` 8 — 52 passed, 0 failed.
   Bridge byte-pin to the q3-era exact-15.3 VM validation record
   (`artifacts/validation/canonical-fleet-reload-q3/suspension.json`,
   source_commit `14ec60f248547d4d062a1160f0fc26d742319888`) holds:
   `package_bytes()` composes byte-identical package SHA-256s at HEAD.
4. Runnable exercise stage of record — MISSING. The proven reload branch
   (`proof/canonical_fleet.py run` RELOAD arm) stops at
   `CANONICAL_RELOAD_ONLY_VERIFIED` by its own frozen no-purchase
   contract (tripwired by `test_canonical_reload_only.py`); the
   purchase/dispatch conductor exists but is CLI-unreachable. Building
   it is this spec's implementation ticket
   (`.scratch/phase-b-t030/issues/01-exercise-conductor.md`).
5. Gate ladder for the ONE native attempt (staged candidate → preflight
   PASS → verify → `AUTHORIZATION_UNVERIFIED`/`CLAIM_ABSENT` →
   independent review → Gate C signing → fresh explicit ONE-launch
   authorization) — OFFLINE preparable; the launch is operator-gated.
6. Post-run: exercise receipts + canonical correspondence record + E-row
   (after item 5's authorization).

## Execution contract of record (T-030 exercise attempt)

- New attempt identity (never reuse or mutate the consumed q1/q2/q3
  identities or their bytes): qualification id
  `canonical-fleet-exercise-t030-1`, one launch, one fresh secure
  connection, launches_allowed=1, retries=0.
- Sequence: preflight-verified staging from the E2 protected canonical
  evidence (create-q3 `canonical.sav` + provenance) → launch in paused
  state under the SAME byte-pinned validated bridge package (`G 42`
  fixed seeded world, 64×64, engine/config correspondence pins as
  reload-q3) → `establish_reload_context` →
  `verify_reloaded` full semantic correspondence → armed paused
  boundary → `capacity-add` service 1 with `max_cost` bound →
  `capacity-read` → `canonical-start` → `canonical-dispatch-read` →
  single owned-console `unpause` → `canonical-dispatched`
  acknowledgement (unpaused, tick/economy advanced) → owned cleanup
  certified. Receipts of record: the reload correspondence pair,
  `canonical-dispatch.json` (binding/capex/before/dispatch/unpause),
  the intervention snapshot set (owned `purchase-readback`-classed
  saves per snapshot), `result.json` typed
  `CANONICAL_FLEET_EXERCISE_VERIFIED`.
- Fail-closed: any drift from the paused construction gates refuses;
  partial mutation records its physical vehicle id and is never
  retried or accepted as a complete receipt; failure stops before
  further boundaries; cleanup still runs; nothing relabeled.
- No feasibility/economics claim outside the receipts (OPEX/ROI stay
  UNKNOWN; T-031's matched A/B is a separate later effort).

## Boundary of this spec

Offline only. This spec authorizes no launch, no AdminPort connection,
no staging beyond the new attempt's prepare/preflight/verify (offline,
argv never executed), and never modifies retained evidence. The native
attempt waits for a fresh explicit operator authorization after
independent review and Gate C signing.
