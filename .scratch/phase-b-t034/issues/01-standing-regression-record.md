# 01: Standing full 15.3 regression record (T-034)

**Type:** task
**Status:** resolved 2026-11-11 (commit this round)
**Spec:** `docs/specs/t034-standing-regression.md`

**What to run:** the full offline suite
(`pytest -m 'not openttd'`, the command of record) over every ticket's
new tests, legacy-red failures classified by ID against the
pre-existing records, statics snapshot, and the retained-artifact
manifest integrity sweep; record + E-row. Run LAST so it covers all
Phase B round tests.

## Answer

Resolved. 6342 collected / 6286 passed / 56 failed / 0 errors /
50 skipped (junitxml-counted; ~68 min). All 56 failures pre-existing
by ID: 51 in `test_p08_controlled_e2e.py` (E159 scope) + 5 singles
(two newly verified pre-existing at pre-round HEAD `f0b5960` in a
detached symlink-bound worktree; three already recorded at E153/E155).
Zero failures in any round-touched file. Repo-wide ruff finds 12
pre-existing errors in three never-touched files (counted, not
relabeled). Manifest sweep: 197 manifests / 0 mismatches; binary +
OpenGFX + protected-save pins hold; `pgrep -x openttd` empty. Zero
launches; zero AdminPort; no retained `artifacts/` byte touched.

## Re-run of record (2026-11-12, at the Phase B closure HEAD)

First full offline gate at the closure HEAD `dc86b51`: 6379 collected /
58 failed / 0 errors / 51 skipped — 51 p08 (legacy) + 5 legacy singles +
TWO NEW round-adjacent IDs, both diagnosed fixture-stale with no
app-code change: `test_canonical_fleet_gui.py::test_preflight_passes_
on_real_staging_unpatched` (the E167-era test pinned the superseded
`canonical-fleet-create-q3` anchor while `verify_created_source` now
binds the E186/E189 `CREATE` constant of record — create-q5) and
`test_native_save_path.py::test_real_failure_save_seam_ignores_prior_
script_fatal_only` (the local Backend double borrowed only pre-E179
`_check_logs`; E179's behavior-preserving split moved the fatal scan
into `_scan_fatal`; `FreshWorldBackend` resolves it via its MRO — app
fine). Fix round `3b2b618` (test files only): the GUI test follows
`driver.CREATE`; the double borrows `_scan_fatal`. Both files green
(43 tests), ruff/format/compile clean.

Final gate of record at `3b2b618`: **6379 collected / 6272 passed /
56 failed / 0 errors / 51 skipped** — the E165 legacy-red set
reproduced EXACTLY by ID (51 in `test_p08_controlled_e2e.py` + the 5
verified singles); the two fixed IDs gone; ZERO failures in any
round-touched file. Skips 51 = E165's 50 + the round's known
skip-typed `test_prepare_seals_current_helpers_despite_record_pin_
drift` (q4 pin drift, honest). Statics unchanged: 12 pre-existing
errors in three never-touched files. Manifest sweep: 214 manifests /
0 mismatches (E165 was 197 — the continuation's six new attempt/anchor
manifests included, all verified). Pins hold (save `51e45689…`,
OpenGFX `43a0c1da…`, binary `276d5b69…`); `pgrep -x openttd` empty.
Zero launches; zero AdminPort; no retained `artifacts/` byte touched.
