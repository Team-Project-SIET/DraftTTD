# 06 — Final offline readiness audit of the FD-C-2 remediation

> **UPDATE 2026-11-12 (E197):** this package was EXECUTED exactly once
> under the operator's fresh explicit attempt-7 grant at HEAD
> `ac504f8` — typed terminal `NATIVE_LOOP_ZERO_SERVICES`, evaluator of
> record rc 0 with both cycles independently `ZERO_SERVICE` (verbatim
> `NO_FEASIBLE_SERVICES: no supported full-load road engine and
> supply`). The remediation's classification goal is proven on fresh
> native bytes: cycle 1's candidate refusal is the fix's explicit
> `NATIVE_CORRIDOR_BOUND: requires 2..47 road tiles`, cycle 2's is the
> witness-fallback `NO_BOUNDED_CORRIDOR` (38/20 stops disconnected);
> zero `SEARCH_LIMIT_EXCEEDED` anywhere. Funnel: compatible 16,
> captured 1 (832/832 reads, pause_pairs 1), 10 × `CAPTURE_TILE_
> BUDGET`, `CANDIDATE_SEARCH_LIMIT controls 146`, `search_truncated:
> true`. FD-C-2 stays `INCOMPLETE_EVIDENCE`. Run dir
> `artifacts/demos/playable-demo-743dee713b2841baa1bcbc0f115ee901`
> sealed read-only; cleanup all-true, manifest match True. Nothing
> below is changed — the package text stands as the pre-execution
> record.

Audited 2026-11-11, fully offline (no native execution, no AdminPort, no
evidence byte written). Scope: the FD-C-2 remediation chain
`71f6e7d` (fix + sealed pins) + `9194184` (docs, E159, includes E159's
offline funnel root-cause closure), HEAD `9194184`, branch
`miles/fright-delivery` (ahead of origin by 16 by design — repo policy:
local commits only, never push).

## Findings

1. **Fix of record verified in place** (`app/planning/p08_road.py`):
   shared `CORRIDOR_INTERIOR_MIN, CORRIDOR_INTERIOR_MAX = 2, 47` +
   `CORRIDOR_INTERIOR` (lines 61–62); the incumbent pair loop skips
   assembled paths outside the bound without consuming pairs (line 426,
   explicit `continue`); pairs whose delivery's complete-reachability
   witness is over-bound are pruned WITHOUT charging the aggregate
   expansion budget (line 409), so a recorded refusal can never flip to
   `SEARCH_LIMIT_EXCEEDED`; the witness fallback still assembles an
   over-bound route when no supported corridor exists (no-supported-
   corridor worlds keep the explicit `NATIVE_CORRIDOR_BOUND` /
   `NO_BOUNDED_CORRIDOR` terminals).
2. **Tests re-run fresh under the audit**:
   - Six-file targeted set of record
     (`test_freight_loops.py test_road_mutation.py
     test_native_freight_network.py test_native_save_path.py
     test_capture_scheduling.py test_console_echo_handshake.py`):
     **154 passed / 0 failed** — includes the three sealed FD-C-2 pins
     (`test_sealed_attempt2_candidate_rejections_replay`,
     `test_sealed_attempt2_witness_refusals_are_complete`,
     `test_sealed_attempt6_candidate_rejections_replay`) and the
     attempt-6 e2e pin.
   - `tests/test_p08_bounded_routing.py` (masking red/green +
     seed-17 retained-replay corridor pin): **18 passed**.
3. **Statics on the touched paths** (`app/planning/p08_road.py`,
   `tests/test_freight_loops.py`,
   `tests/test_p08_bounded_routing.py`,
   `app/simulation/openttd/proof/freight_delivery.py`):
   `ruff check` clean; `ruff format --check` clean; `py_compile` clean;
   scoped `uvx ty check` → `All checks passed!`; `git diff --check`
   clean. Repo-wide ruff/format are dirty in pre-existing untouched
   files (15 errors / 51 files) — committed WIP outside this remediation,
   counted, never relabeled, not blockers for the touched paths.
4. **Pre-existing e2e failures, identity re-proven by ID, not just
   count**: `tests/test_p08_controlled_e2e.py` 62 collected, **51
   failed / 11 passed** under the fix. A detached worktree at the
   pre-fix commit `a8bc8e3` (`.venv`/`artifacts` bound via symlink, no
   checkout flip, no sealed read-modify) reproduced **exactly the same
   51 FAILED IDs** (diff empty). Same scope as E159 recorded it:
   outside the corridor chain, left for its own reviewed round, not a
   blocker.
5. **Sealed evidence integrity re-proven read-only**:
   - `sha256sum -c artifact-manifest.sha256` from inside each of the 6
     verification roots (attempt-6 root + both cycles, attempt-2 root +
     both cycles): **0 mismatches total**.
   - Verify of record: `.venv/bin/python -m
     app.simulation.openttd.proof.freight_delivery verify
     artifacts/demos/playable-demo-0751d73c44054941bd77f05300b6c1a5`
     → **rc 0**, `verified_loop_cycles` = cycle-1 and cycle-2 both
     `"status": "ZERO_SERVICE"` with verbatim
     `NO_FEASIBLE_SERVICES: no supported full-load road engine and
     supply`.
   - Hash snapshot of attempt-6 root manifest + both cycle manifests +
     `result.json` and attempt-2 root + cycle-1 manifests captured
     BEFORE the replay-bearing probes; re-hashed after — **byte-
     identical** (diff empty). Candidate rejection parity itself is the
     green sealed pins of item 2 (byte-identical replay), driving the
     sealed funnel read-only through the ticket-07 replay machinery.
6. **Git state**: `git status -sb` clean at `miles/fright-delivery` on
   `9194184`; `stash@{0}` (`WIP on devmodule2: b352375 …`) untouched;
   16 commits ahead, never pushed. Temp probes in `/tmp/opencode`
   removed (`fdc2-baseline` worktree deleted).
7. **Runtime prerequisites for a native attempt** (offline checks
   only): pinned binary
   `/home/fed/Downloads/openttd-15.3-linux-generic-amd64/openttd`
   sha256 `276d5b698a6b706154f3af588f6f885b3aebe518f4ecc8f869abf71383b1904c`
   — re-hashed, equals pin. Pinned OpenGFX
   `artifacts/runtime/verified-assets/opengfx-8.0-all.zip` sha256
   `43a0c1dabf39cb865394f3a6cc36d4da5c10ecfaaf55652043104806810903be`
   — re-hashed, equals pin. Offline preflight (REPRODUCE.md command of
   record): `python -m app.openttd_demo check` → `Binary, assets and
   desktop prerequisites found; no game launched.` `pgrep -x openttd`
   → no common openttd process present.

## Verdict

**READY_FOR_OPERATOR_AUTHORIZATION.** No blockers in the audited state.
A reduced label authorizes nothing: Attempt 7 still requires a fresh
explicit operator grant in its own session (all earlier grants void:
E141, E142, E145, attempts 1–6), one launch, no retries, and the
byte-unchanged command of record below.

Residual risk (documented, not a blocker): this audit proves offline
closure, tests and evidence integrity — it does NOT claim live-world
behavior, and it makes no feasibility or infeasibility claim for any
territory outside the recorded truncated slices (`search_truncated=true`
throughout; FD-C-2 stays `INCOMPLETE_EVIDENCE`).

## Attempt-7 authorization package — PREPARED, NOT EXECUTED

Approved execution contract for the authorized ONE attempt (nothing
launched; this package only states what an explicit grant would
legitimize):

- Command of record, byte-unchanged since attempt-1:
  `OPENTTD_BINARY=/home/fed/Downloads/openttd-15.3-linux-generic-amd64/openttd
  OPENTTD_OPENGFX_ARCHIVE=/home/fed/codes/softdev2/artifacts/runtime/verified-assets/opengfx-8.0-all.zip
  .venv/bin/python -m app.openttd_demo run --headless --random-world
  --seed 2026 --towns 3 --industries 3 --stop-on-delivery --cycles 2`.
- Code state under test: `71f6e7d` reviewed change on `9194184` (this
  audit), tree clean, staged packages composed at run time from this
  state.
- Scope: exactly one launch, one fresh connection per cycle (2 total),
  funding on the single cycle-1 connection only, loop-scaled sealed
  budgets, no retries, no seed change, no additional launch, no scope
  expansion. Stop immediately on any unexpected failure.
- Expected evidence: the digest-pinned run tree of record under
  `artifacts/demos/` (`result.json` with a native terminal status,
  `PRELAUNCH.json`/`CLAIM.json`, `frozen-source.zip`,
  `graphics-identity.json`, `runtime-identity.json`, `stderr.log`,
  `artifact-manifest.sha256`, `cleanup.json`, two-cycle `loops` list,
  per-cycle copy set + `cycle-result.json` + receipts), sealed on
  completion and never regenerated.
- Success evaluator of record (offline, after the run):
  `.venv/bin/python -m app.simulation.openttd.proof.freight_delivery
  verify <run-dir>` must reach rc 0 with both cycles independently
  verified (`verified_loop_cycles` statuses), every retained manifest
  re-derived digest-for-digest equal, and cycle-2 polls sourced from
  cycle-2's own stderr window. FD-C-2 is reassessed ONLY from fresh
  digest-pinned bytes; a rerun terminal proves nothing beyond its own
  slice (truncated searches and typed failures stay `INCOMPLETE_
  EVIDENCE`).
- Stop conditions: any unexpected typed failure; any manifest
  mismatch; any requirement to relaunch; cleanup not fully certified;
  any scope creep. On completion, independently verify both cycles
  before any closure claim.
- Guards remain in the runner: binary/OpenGFX digests, no-matching-
  process gate, `launches_allowed=1 retries=0`.

A `READY` verdict plus this package is NOT a grant; granting happens
only when the operator states it explicitly in a live session.
