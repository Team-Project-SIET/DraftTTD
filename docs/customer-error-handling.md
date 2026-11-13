# Error handling and edge cases (2026-11-13)

This document describes how the system behaves when things go wrong: the
fail-closed gates, typed failure classes, one-shot consumption, no-retry
policy, and the edge cases the design explicitly handles. Every claim is
anchored to source on branch `miles/fright-delivery` (HEAD `90ebadb`) or to an
evidence row in [EVIDENCE_INDEX.md](../EVIDENCE_INDEX.md). Documentation only
— no runtime authorization.

## 1. Design posture: fail closed, stop, retain

The system is built so that an unexpected state **stops the attempt** rather
than being absorbed, retried, or papered over:

- Any failure halts without retry or reconnect and retains partial evidence
  verbatim ([REPRODUCE.md](../REPRODUCE.md) §Native demo). The launch engine
  itself refuses a second launch outright:
  `proof/native.py:275-276` raises `RuntimeError("No launch retry")` once
  `_launched` is set.
- FAILED terminal outcomes are immutable: consumed attempts stay consumed and
  are never relabeled (ledger discipline; see
  [PROJECT_CLOSURE_PLAN.md](PROJECT_CLOSURE_PLAN.md)).

## 2. Fail-closed gates at the seams

| Gate | Behavior | Source |
| --- | --- | --- |
| Frozen-source pinning | Every frozen file is re-hashed before launch; any drift refuses the launch outright | `proof/harness.py:102-104` — `raise ValueError("Frozen source/input changed; no launch permitted")` |
| Encrypted framing | A frame with bad length/framing permanently closes the cipher before any decrypt | `admin_crypto.py:105-114` (`self.close()` then raise) |
| MAC failure | A failed packet authentication closes the cipher and raises; no partial plaintext escapes | `admin_crypto.py:129-132` — `plaintext is None` → `CryptoError("packet authentication failed")` |
| Encrypted oversize | A packet that would exceed the maximum frame length is refused and the cipher closed | `admin_crypto.py:118-121` |
| Outbound protocol gating | Application traffic before the `ACTIVE` state raises `AuthProtocolError` | `secure_admin.py:188-191` |
| Connect failures | Timeout → `AuthTimeout`; OS error → `AuthDisconnected` — typed, never swallowed | `secure_admin.py:180-185` |
| Operation budgets | Any operation past its budget raises `TransportProtocolError("protocol operation budget exhausted")` | `gamescript_transport.py:105-108`; class budgets `MAX_REQUESTS = 256`, `MAX_PRODUCTION_SESSION_REQUESTS = 96 + 32 * MAX_INDUSTRY_CARGOES` at `:235-236` |
| Planning boundary | Typed `PlanningFailureCode` refusals: `UNSUPPORTED_PLAN_VERSION`, `INVALID_PLAN`, identity-mismatch checks | `app/planning/validation.py:73-77`, `:83-89` |
| Runtime isolation | A workspace resolving inside the user's OpenTTD profile is refused | `runtime/config.py:52-56` — `raise ValueError("Workspace must not be inside the user's OpenTTD profile")` |

## 3. One-shot consumption (no second attempt, ever)

- **Grant refusal:** a candidate whose `CLAIM.json` already exists can never
  mint a grant again — `proof/operator_authorization.py:347-348` raises
  `ClearingAuthorizationError("one native attempt already consumed")`.
- **Process-boundary refusal:** the launch marker is created with
  `O_CREAT | O_EXCL`; a second launcher loses the race at the marker, not at
  `Popen` — `proof/terrain_clearing.py:1376-1382`.
- **Launch-level refusal:** `proof/native.py:275-276` (above).

Together these make "run it again to see if it works this time" structurally
impossible for a consumed candidate; a new attempt requires fresh staging and
a fresh operator grant.

## 4. Receipt, replay and cleanup verification

After the run, the attempt's own retained bytes are re-verified fail-closed:

- Intent/source-save binding: `proof/road_mutation.py:603-604` refuses an
  intent whose source save digest does not match the retained `before.sav`.
- Receipt/plan/save coherence: `:605-606` refuses on any mismatch between the
  retained receipt, the plan digest and the authoritative after-save.
- **Cleanup certification gate:** `:607-612` requires every cleanup flag
  (`reaped`, `sockets_closed`, `workspace_disposed`, `credential_removed`)
  to be `true` — `"receipt cleanup incomplete"` otherwise. Cleanup failure
  fails the verification; it is never waved through.
- Replay re-derivation: independent replay re-derives the whole attempt from
  retained bytes (for the corridor cargo-flow pipeline this is
  `verify_cargoflow2_attempt` → `CARGOFLOW2_COMPLETION_VERIFIED` exit 0 on
  the fixed surface, E134), and the zero-residual funds fence reports any
  divergence as a finding — it never normalizes, rounds or reconciles by
  hand (ADR-0001 D6; the round-6 vs round-7 one-unit divergence
  `484986` vs `484985` is carried verbatim, E126).

## 5. Typed failure classes (no stringly-typed errors)

Failure modes surface as named classes, each actionable:

- **Crypto:** `CryptoError` with specific messages (`invalid cryptographic
  field length`, `public key does not match secret`, `packet authentication
  failed` — `admin_crypto.py:22,34,132`).
- **Session/transport:** `AuthTimeout`, `AuthDisconnected`,
  `AuthProtocolError`, `AdminSessionStopped`, `TransportProtocolError`.
- **Planning:** `PlanningFailureCode` enum values carried by
  `PlanningValidationError` (e.g. `UNSUPPORTED_PLAN_VERSION`, `INVALID_PLAN`).
- **Authorization:** `ClearingAuthorizationError` (one-shot violations).
- **Native phase outcomes:** typed terminal statuses retained verbatim, e.g.
  `NATIVE_CARGOFLOW2_COMPLETE` with the honest sub-verdict
  `CARGOFLOW2_LOADED_NEVER_DELIVERED` (E124/E133 — the run "succeeds" as a
  run, and the verdict still refuses to call it a delivery).

## 6. Anti-bypass hardening

The public prelaunch validation boundary re-parses even already-typed inputs
through the models, because `model_copy(update=...)` bypasses Pydantic
validation — `app/planning/validation.py:78-86`:

```python
# model_copy(update=...) bypasses Pydantic validation. Reparse even typed
# inputs so this public prelaunch boundary cannot be bypassed that way.
plan = ExecutionPlan.model_validate_json(plan.model_dump_json())
scenario = PlanningScenario.model_validate_json(scenario.model_dump_json())
```

A caller cannot hand the validator a "validated" object that quietly differs
from what the models would accept.

## 7. Edge cases explicitly handled

| Edge case | Handling | Anchor |
| --- | --- | --- |
| Key material exposure in logs/reprs | Secret fields declared `repr=False` on frozen dataclasses (`AuthorizedKey._secret`, `DerivedKeys` directional keys) | `admin_crypto.py:25-27`, `:63-66` |
| Zero-service loop cycles | A cycle with no services is a typed outcome (`NATIVE_LOOP_ZERO_SERVICES`); two consecutive zero-service cycles type the world `abandoned_world` (K=2 rule) instead of looping forever | E143 (`proof/freight_delivery.py` loop engine) |
| Absence of data is a measurement | Census drained pages report emptiness as READY-empty findings; overflow past the page budget is an explicit finding, nothing silently discarded | E59/E60 (`corridor_box_census.py`) |
| Native facts that don't fit the model | The 15.3 non-producer fact rides the wire verbatim as `p = -1` (never translated into a count); other unsupported facts refuse | E65 (`corridor_box_census.py` census row domain) |
| Malformed / hostile responses | Census phase outcomes are typed `MEASURED / REFUSED / MISSING / MALFORMED` with prefix-preserving halt; `INVALID_COMPANY`, `OUT_OF_ORDER`, `STALE_PIN` refusal classes are tested | E60 (`tests/test_corridor_box_census_vm.py`, `tests/test_corridor_box_census_native.py`) |
| Delayed ACK completing a later request | Transport rejects ID reuse on a connection; one correlated request at a time | `gamescript_transport.py:229-233` |
| Vehicle cannot complete its cycle inside the observation window | The ladder ended one interval short of the delivery leg — diagnosed as a plan-composition root cause (E128), not papered over; the fix keyed a delivered arm by the `(route_version, schedule_version)` pairing with v1 digests byte-equal (E129) | E128/E129 |
| Funds arithmetic drift | Zero-residual fence: divergence → halt/finding, never normalization | ADR-0001 D6; E117, E126 |
| Clone without retained evidence | Offline tests that need retained artifacts fail loudly (missing evidence), never substitute synthetic fixtures | AGENTS.md safety rules; REPRODUCE.md |
| Historical protection | Retained attempt bytes are never modified or regenerated; historical artifacts are transfer-only | `proof/historical_protection.py`; `tests/test_historical_protection.py` |

## 8. What failure looks like to an operator

1. The attempt halts at the first failing gate (staging, preflight, signing,
   launch, readback, or replay) — prefix-preserving, with everything before
   the failure retained.
2. Exit codes are meaningful (e.g. `AUTHORIZATION_UNVERIFIED`/`CLAIM_ABSENT`
   → exit 1 by design on a pre-auth verify).
3. Cleanup runs and is certified; the certification itself is gated by
   verification (`road_mutation.py:607-612`).
4. The outcome lands as a typed terminal and is recorded verbatim in the
   ledger; retrying requires a new authorization decision, not a keystroke.

## 9. Honest limitations

- The no-retry rule means transient environmental failures consume the
  attempt; this is a deliberate trade of convenience for evidence integrity,
  not an oversight.
- Error handling is strongest at the security and evidence seams; wide
  orchestration modules rely on the same typed-exception discipline but have
  more surface area by design (see
  [customer-solid-analysis.md](customer-solid-analysis.md) §6).
- Diagnosed failure classes (e.g. the corridor delivery-window boundary,
  E128) are fixed at the narrowest layer with regression tests, but
  unproven capabilities (corridor delivery, random-world delivery) remain
  unproven — error handling does not convert them into successes.

## Related documents

- Use cases and statuses: [customer-use-cases.md](customer-use-cases.md)
- Security/threat analysis: [customer-security-threat-analysis.md](customer-security-threat-analysis.md)
- Commands of record: [REPRODUCE.md](../REPRODUCE.md)
