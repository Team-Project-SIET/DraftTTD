# 04 — Attempt 6 native readiness audit (read-only)

Covers `1023cca` (fix: handshake) + `20ac708` (docs), HEAD `20ac708`,
branch `miles/fright-delivery` (ahead of origin by 10 by design — repo
policy: local commits only, never push). Audited 2026-11-11 offline: no
native execution, no evidence bytes touched, no relabeling of Attempt 5
(FAILED/SEALED at `42bbe5f`, E156 addendum 2).

## Findings

1. `console_ack` (road_mutation.py, committed additive block of 24
   insertions between `console()` and `owned_save_path`): log offsets
   snapshotted BEFORE the single write — the load-bearing order for the
   fast-echo case (same order as `save()`); typed
   `TimeoutError("console echo acknowledgement missing")` on expiry,
   one write, no retry; `backend.health()` each poll. `save()` itself
   byte-untouched: `git diff 42bbe5f..1023cca` on the file is
   insertions-only in one hunk.
2. Handshake integration: `paused_world_clock(backend, prepared, *,
   diagnostic=None)` handshakes `pause` on entry and `unpause` in the
   `finally`; single production call site updated
   (`freight_native_network.py:381`); `pause_pairs`/`pause_resume_error`
   accounting preserved: unpause failure recorded, body error still
   propagates. The per-cycle
   `save "qualified"` (≈line 410) is issued strictly after the unpause
   echo is observed — the sealed Attempt-5 `unpause → save` adjacency
   is closed. `grep console(` in `freight_native_network.py` = 0 hits:
   the module has no direct console issuers left.
3. Tests re-run fresh: 144 passed
   (the prior 137 targeted set — `test_freight_loops`,
   `test_road_mutation`, `test_native_freight_network`,
   `test_native_save_path`, `test_capture_scheduling` — plus the new
   `test_console_echo_handshake` 7 incl. T1 ordering, T2 typed timeout,
   T3 AST invariant, T4 Attempt-5 adjacency red-green). Static checks
   on the four touched paths: `ruff check`, `ruff format --check`,
   `py_compile`, `uvx ty check`, `git diff --check` — all clean.
4. Bare-console scope remaining (out of ticket-06 attempt path,
   documented in the T3 test docstring):
   `freight_canonical_dispatch.unpause_native` (correlated GS receipt
   via `exchange` directly after), corridor/terrain bootstrap commands,
   `canonical_fleet.py:572/771`, `road_freight_infrastructure.py:113`,
   `freight_delivery.py:1657` start_ai, `road_mutation.run:413` start_ai
   (exempt: `wait_log("ROAD_PROOF_COMPANY_READY")` directly after gates
   processing before any following save — held clean in attempts 4+5).
   Every console issuer attempt 6 reaches is acked, save()-self-acked,
   or start_ai-gated by a following log wait.
5. Assets and preflight: pinned binary
   `/home/fed/Downloads/openttd-15.3-linux-generic-amd64/openttd`
   sha256 `276d5b698a6b706154f3af588f6f885b3aebe518f4ecc8f869abf71383b1904c`
   — re-hashed, equals pin. Pinned OpenGFX archive
   `artifacts/runtime/verified-assets/opengfx-8.0-all.zip` sha256
   `43a0c1dabf39cb865394f3a6cc36d4da5c10ecfaaf55652043104806810903be` —
   re-hashed, equals pin, and equals the sealed attempt-5
   `graphics-identity.json` `archive_sha256`: same asset envelope as
   the attempt of record. `python -m app.openttd_demo check --headless`
   (REPRODUCE.md command of record): `Binary, assets and desktop
   prerequisites found; no game launched.` Per-run launch-time gates
   re-verify graphics identity + binary sha + no matching processes
   (`freight_delivery.py:241-243`).
6. Clean state: `git status --porcelain` empty; chain
   `efbe036 → f437d7a → 09c8641 → 42bbe5f → 4c399f7 → e8acf09 →
   1023cca → 20ac708` intact; `stash@{0}` untouched; not pushed.
   Sealed attempt-5 evidence verified against its own
   `artifact-manifest.sha256` (18/18 entries OK re-hashed);
   `loop-cycle-1/qualified.sav` re-hashes to
   `4993714a90c1fc8c551889bbff3ba9d581fd18d6e548e58e7955acf999c45030`
   (the recorded digest); `result.json` still typed
   `TimeoutError: owned native save completion missing` FAILED;
   `CLAIM.json` `launches_allowed=1 retries=0`; `cleanup.json`
   certified (`workspace_disposed`, `credential_removed`, rc 0 — the
   absent per-run `isolated/` tree is that certified disposal;
   attempt 6 stages a fresh isolation from the same pinned binary +
   archive).

## Verdict

**READY_FOR_OPERATOR_AUTHORIZATION.** No blockers identified in the
committed state: the fix closes the sealed loss class by construction
and by offline red-green evidence; assets, preflight, go state and
sealed evidence all verified. A `READY_FOR_OPERATOR_AUTHORIZATION`
label never authorizes a run by itself: the native Attempt 6 needs a
fresh explicit operator grant in its own session, one launch, no
retries, and `launches_allowed=1 retries=0` enforcement remains in
`CLAIM.json`/preflight.

Residual risk (documented, not a blocker): this audit proves offline
closure of the class, not live-game behavior; timeout guard on
`console_ack` is 10 s, far above the ≤30 ms echo cadence observed
in the sealed runs.
