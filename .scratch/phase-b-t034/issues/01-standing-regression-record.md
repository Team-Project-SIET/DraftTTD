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
