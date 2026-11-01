# Reproduce and verify — 2026-10-17 (checkpoint addendum 2026-10-18)

Run from the repository root. Read CONTEXT, AI_HANDOFF and TASKS first. Python
3.14+ is required; `pyproject.toml` and `uv.lock` are dependency authority.
Use `uv sync --locked` when provisioning a new environment. Preserve the existing
environment for inspection. No PostgreSQL or Docker is required for the demo.

## Inspect without native execution

```bash
git branch --show-current
git rev-parse HEAD
git status --short --untracked-files=all
git ls-files --others --ignored --exclude-standard --directory
.venv/bin/python -m app.openttd_demo check
.venv/bin/python -m app.openttd_demo plan
.venv/bin/python -m app.openttd_demo plan --random-world --seed 17 \
  --map-size 256 --climate temperate --terrain 0 --towns 1 --industries 2 \
  --max-candidates 16 --max-services 4 --max-vehicles 4 --planning-seconds 30
```

`check` validates binary/assets/desktop only. Add `--headless` for no-desktop
prerequisite checking. Fixed `plan` writes offline scenario selection/results;
random `plan` writes a generation recipe, not an observed world or selected plan.
Commands write fresh UUID output directories where applicable. Check local
resources before installing anything; dependency setup was not rerun here.

## Focused controlled regression

Read the tests before expanding scope. These test files use controlled peers/VM,
retained offline replay and Python solver workers, with native seams blocked:

```bash
.venv/bin/pytest -q tests/test_demo_random.py tests/test_demo_random_native.py \
  tests/test_random_distance.py tests/test_random_capture_schema.py \
  tests/test_random_capture_budgets.py tests/test_demo_operations.py \
  tests/test_demo_smoke_preflight.py tests/test_openttd_demo.py
git diff --check
```

Some tests require ignored retained evidence and pinned external assets. A clone
without those files may fail; do not silently replace native evidence with
synthetic fixtures. Fresh results for this handoff are in
[validation.md](docs/handoff/2026-10-17/validation.md).
Prior extension suite counts and VM results are historical, not rerun claims.
Full-tree test/lint/type health remains UNKNOWN beyond recorded checks.
Never enable `--run-openttd` or `--run-postgres` for an offline handoff.

## Native demo — requires separate authorization

Provision the exact OpenTTD 15.3 Linux generic amd64 distribution and OpenGFX 8.0.
Set paths **before** Python imports the runner:

```bash
export OPENTTD_BINARY="/absolute/path/to/openttd-15.3-linux-generic-amd64/openttd"
export OPENTTD_OPENGFX_ARCHIVE="/absolute/path/to/opengfx-8.0-all.zip"
```

The public runner supports these overrides; inspect `proof/freight_delivery.py`.
Pinned binary SHA-256:
`276d5b698a6b706154f3af588f6f885b3aebe518f4ecc8f869abf71383b1904c`.
Pinned OpenGFX archive SHA-256:
`43a0c1dabf39cb865394f3a6cc36d4da5c10ecfaaf55652043104806810903be`.
Keep language/distribution assets beside the executable. Read
[the demo guide](examples/openttd-demo/README.md) for setup and spectator controls.

Stable command (starts server and spectator):

```bash
.venv/bin/python -m app.openttd_demo --view-seconds 300
```

Future random smoke command shape, only after fresh preparation, independent
preflight and explicit one-shot authority:

```bash
.venv/bin/python -m app.openttd_demo run --random-world --seed 17 \
  --map-size 256 --climate temperate --terrain 0 --towns 1 --industries 2 \
  --max-candidates 16 --max-services 4 --max-vehicles 4 --planning-seconds 30 \
  --stop-on-delivery
```

This is a command reference, not authority to invoke it or retry historical runs.
The CLI defaults to `run` when the command is omitted. `--headless` still launches
the native server. Historical preflight/launch harnesses contain consumed paths
and authorizations; never execute them as reusable reproduction scripts.

A new run requires frozen code/config/assets, effective settings and source-trust
checks, bounded ports/time/requests, one encrypted session, independent readback,
receipt replay and full owned-process/credential/workspace cleanup. Failure stops
without retry/reconnect and retains partial evidence. Cleanup does not delete
historical saves/logs. `--view-seconds` uses the existing total runtime deadline.

## Offline reports after accepted native evidence

```bash
.venv/bin/python -m app.openttd_demo report --source /absolute/path/to/completed-demo
.venv/bin/python -m app.openttd_demo compare --source /absolute/path/to/report-a \
  --compare-with /absolute/path/to/report-b
```

The CLI writes fresh sibling output. Preserve source packages. P07 needs completed
native receipts; Seed 17's failed smoke supports diagnostics, not P07 deliveries.
Comparisons are descriptive across distinct seeds/configurations, not causal
matched experiments. Recompute current hashes from the dated handoff inventory
before transfer/use; this inventory is not a historical resealing authority.

## 2026-10-18 checkpoint addendum — checked commands

The evidence-aware insights subcommand regenerates P07 read-only reports offline
(no native process underneath; the attempt source is a consumed attempt, so the
analysis output keeps the FAILED terminal visible):

```bash
.venv/bin/python -m app.experiments.cli analyze-performance-insights \
  artifacts/experiments/p07-attempt19-five-year-offline \
  --output <fresh-output-directory> \
  --compare artifacts/demos/playable-demo-25d891bc9f3444aca73058165d10055a-report
```

Focused classification-V2/P07 suites used for the 2026-10-18 documentation
checkpoint (all offline; 151 passed):

```bash
.venv/bin/pytest tests/test_performance_insights.py tests/test_world_correspondence.py \
  tests/test_classification_capture.py tests/test_classification_execution.py \
  tests/test_gamescript_transport_classification.py tests/test_tile_classification_receipt.py \
  tests/test_p08_classification_workflow.py tests/test_terrain_classification_preparation.py \
  tests/test_tile_classification.py tests/test_p08_feasibility_classification.py
```

Consumed Tile Classification V2 capture integrity (read-only; verifies the
retained 90-page receipts/pages/verdict candidate bytes):

```bash
cd artifacts/demos/classification-exec-seed17-3a8f9e46 && sha256sum -c artifact-manifest.sha256
```

The completed capture's fusion result is REJECTED (83 PROJECTED_FLAGS_DIFFER,
nothing fused): reproducing that binding offline means re-running only the
sweep/receipt classes over those retained page bytes (see
[the completion record](docs/p08-classification-v2-native-capture-completion.md)),
not any new launch. Native capture runs remain one-shot authorized events with
consumed identities; never re-run them from this file.

## 2026-10-31 addendum — D5-CORRIDOR-EXTENSION-3 offline validation (checked)

The terrain-survey pipeline's documented offline command of record (no launch,
no AdminPort, no candidate lifecycle; exact result 2026-10-31: 130 passed,
1 skipped, 0 failed, 0 errors; the skip is the `typeof` note at
`tests/test_corridor_terrain_survey.py:346`):

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest \
  tests/test_secure_admin.py \
  tests/test_corridor_terrain_survey.py \
  tests/test_corridor_terrain_survey_native.py \
  -q -p no:cacheprovider -rs
```

Read-only status proves on retained D5-CORRIDOR-EXTENSION-3 candidates (never
a reproduction of any consumed attempt; candidate-2 is stale-by-source-drift
and never-consumed, candidate-3 is consumed COMPLETE — `SURVEY_COMPLETION_VERIFIED`):

```bash
.venv/bin/python -m app.simulation.openttd.proof.corridor_terrain_survey_native \
  verify artifacts/experiments/d5-corridor-extension-3-survey-native-candidate-2

.venv/bin/python -m app.simulation.openttd.proof.corridor_terrain_survey_native \
  verify artifacts/experiments/d5-corridor-extension-3-survey-native-candidate-3
```

`PRELAUNCH`/`preflight`/`run` are staging or native-execution entry points:
run them only under the exact staging/approval gates recorded in phase-a
record §11.4. A candidate whose staged bytes verify is one operator signature
and one launch approval away from execution — neither is granted by a
documentation task.

## 2026-11-01 addendum — D5 A1 v2 offline implementation validation (checked)

The corridor-extension A1 implementation of record (phase-a §14; no launch,
no AdminPort, no staging, no claim). All five offline suites in one run,
exact result 2026-11-01: 240 passed, 0 failed (exit 0):

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest \
  tests/test_corridor_extension.py \
  tests/test_corridor_extension_native.py \
  tests/test_corridor_construction_native.py \
  tests/test_corridor_terrain_survey_native.py \
  tests/test_corridor_construction.py \
  -q -p no:cacheprovider -rs
```

Offline facts re-derivable in a plain interpreter (values of record:
schedule kinds full/road/spur/station, 31-tile witness ending
50864, 50863, 50862, plan digest
aa88bc99fb80056423b4d1fdc40994abf66aff3afffeb51c710e163ba5447535,
budgets 13 planned / 18-cap, attempt D5-CORRIDOR-EXTENSION-3,
FUNDS_PIN − Σ(454,71,143,307) = 491174):

```bash
.venv/bin/python - <<'EOF'
from app.simulation.openttd.proof import corridor_extension_native as e
from app.simulation.openttd.proof.corridor_construction_native import plan_digest_of
sched = e.extension_schedule()
print([x["kind"] for x in sched], e.PINNED_WITNESS[-3:], len(e.PINNED_WITNESS))
print(plan_digest_of(sched), e.PLANNED_EXTENSION_REQUESTS, e.EXTENSION_REQUEST_BUDGET)
print(e.EXTENSION_ATTEMPT, e.FUNDS_PIN - sum((454, 71, 143, 307)))
print(e.extension_schedule_v1())
EOF
```

Read-only consumed-record proof (never a reproduction of a consumed
attempt; candidate-2 is permanent consumed history and stays byte-untouched;
exact results: v1 re-derivation digest match True and schedule equal,
live replay ATTEMPT_FAILED_EVIDENCE_PRESERVED, result_status FAILED):

```bash
.venv/bin/python - <<'EOF'
import json
from pathlib import Path
from app.simulation.openttd.proof import corridor_extension_native as e
from app.simulation.openttd.proof.corridor_construction_native import plan_digest_of
d = Path("artifacts/experiments/d5-corridor-extension-native-candidate-2")
plan = json.loads((d / "PRELAUNCH.json").read_text())["plan_policy"]
sched = e._staged_extension_schedule(plan)
print(plan["plan_digest"] == plan_digest_of(sched), plan["schedule"] == sched)
print(e.verify_extension_attempt(d)["verification"])
EOF
```

The extension module's `prepare_extension_candidate`/`extension_preflight`
/`run` are staging or native-execution entry points: run them only under the
staging/approval gates of phase-a record §14.5. The staged A1 record
(dated 2026-11-01, checked): `artifacts/experiments/d5-corridor-extension-native-candidate-3/`
seal `404d42d9fa1e113542e74655858f6bc669407d611057eec0c036612ddfa6acd8`,
payload digest `c511dd38a068c1cef5539d3cc422819ef76d73842c42e4d1601b4199debdf94f`,
Gate-C Option-1 signed (2026-11-01, phase-a §16/E43):
`AUTHORIZATION.json` sha `371a524b85add4347a991478909a04da3e7dac8b62b2636b6c7694b32bebe200`,
`verify_authorization` PASS under the pinned anchor
`sha256-ed25519-public-key:cbb63ff58f17f13df3e1be0735fad18497e3a0c6ad6b5dd55491d708ae40c614`,
`PREFLIGHT PASS`; read-only `verify` →
`AUTHORIZATION_UNVERIFIED`/`CLAIM_ABSENT` (authorized, never consumed)
and standalone `preflight` → `PREFLIGHT PASS` remain re-runnable
read-only proofs. Staging and signing are complete; the launch was granted and executed
exactly once (2026-11-01, phase-a §17/E44): `run` → exit 0,
`NATIVE_EXTENSION_VERIFIED`, claim consumed once, all four ops built
with native-quote-verified costs (spur £299, station £307,
`DISTINCT_NEW_STATION`), route `ROUTE_VERIFIED` 30/30 pairs, funds
£490,257, authoritative `after.sav` sha
`3748e00ce57bcb076466f50cac3776c202b4fd130d6c6071935e9d43e45420bd`,
replay `verify` → `EXTENSION_COMPLETION_VERIFIED` (exit 0), certified
cleanup all-true, manifest 0 mismatches. Read-only reproduction of the
consumed attempt (never a re-run):

```bash
.venv/bin/python - <<'EOF'
import json
from pathlib import Path
from app.simulation.openttd.proof import corridor_extension_native as e
from app.simulation.openttd.proof.operator_authorization import verify_authorization
from app.simulation.openttd.proof.harness import sha256
d = Path("artifacts/experiments/d5-corridor-extension-native-candidate-3")
metadata = json.loads((d / "PRELAUNCH.json").read_text())
v = verify_authorization(d, metadata, sha256(d / "PRELAUNCH.json"))
print(v.authorization_sha256, v.operator_key_identity)
print(e.verify_extension_attempt(d)["verification"])
EOF
```
