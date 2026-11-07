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

## 2026-11-01 addendum — D5 freight delivery v2 offline validation (checked)

The D5 Freight Delivery v2 implementation of record (protocol-8 wire contract
`app/simulation/openttd/corridor_freight_v2.py`, save-restore-bounded
GameScript package `app/simulation/openttd/d5_freight_v2_package/`, staged
runner `app/simulation/openttd/proof/corridor_freight_v2_native.py` and the
repo-local stub `typings/squirrel.pyi`; no staging, no signing, no launch,
no AdminPort, no claim, nothing written under `artifacts/`). Two focused
offline suites in one run — E51 of record 48 + 67 passed; the E53 fix round
(2026-11-01) of record 61 + 67 passed with 0 failed (exit 0, every dot green;
the `-rs` output is pattern-only, so read the dots):

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest \
  tests/test_corridor_freight_v2.py \
  tests/test_corridor_freight_v2_native.py \
  -q -p no:cacheprovider -rs
```

Offline facts re-derivable in a plain interpreter (values of record — E53
updated: the schedule digest of record is now
`ed5bad8237dd68985ab712a2df6430564be4d9077d770f2b78ff84a684eb1ff4` because
every watch window now stages the uniform 10-economy-day lease; plan-model
digest `779ff9ee5ef452c4d05a2a432b979095f2cb8055554f7121f950241db9de12c4`,
route digest `b2f80f46…7131` distinct from the witness digest
`f1f00e13…686c`, 30 exchanges = fixed 10 + 6 cycles×3 + tail 2 inside the
32-unique-id request budget, a 640-byte site request inside the 768-byte
bound (`load` watch window 415 B), staged attempt `D5-FREIGHT-2` bound to
the A1 close-out lineage, and the phase-budget exchange timeouts of record
10 s for fixed-request exchanges and 65 s for a watch window):

```bash
.venv/bin/python - <<'EOF'
from app.simulation.openttd.proof import corridor_freight_v2_native as w
from app.simulation.openttd.proof.corridor_freight_v2_native import (
    _freight_exchange_request,
)
plan = w.freight_plan_v2()
sched = w.freight_schedule()
site = _freight_exchange_request(sched[0], "0" * 64, plan, {})
req = _freight_exchange_request(
    next(e for e in sched if e["op"] == "vread"), "0" * 64, plan, {"vehicle": 9}
)
watch = _freight_exchange_request(
    next(e for e in sched if e["op"] == "load-watch"), "0" * 64, plan,
    {"site": None,
     "engine": __import__("types").SimpleNamespace(engine=123, quote=4429),
     "vehicle": 9},
)
print("plan digest   ", w.plan_digest_of(sched))
print("plan model    ", plan.digest)
print("route digest  ", plan.route_digest)
print("witness digest", plan.witness_digest)
print("schedule      ", len(sched), "exchanges,", plan.cycles, "cycles")
print("watch leases  ", [e["watch_days"] for e in sched if e["op"].endswith("-watch")][:3])
print("budgets       ", w.budgets()["planned_exchanges"], w.budgets()["requests"])
print("site request  ", len(site.model_dump_json().encode()), "bytes (bound 768)")
print("exchange time ", w.exchange_timeout_seconds(req, budget_table=w.budgets()), "s",
      w.exchange_timeout_seconds(watch, budget_table=w.budgets()), "s")
EOF
```

Both suites are fully offline: neither file references `artifacts/` (verified
again for the E53 fix round by grep over both files), so they do not depend
on retained evidence bytes and lose nothing on a clone. The v2 runner's
remaining entry points (`execute_freight_attempt_v2` and the replay verifier
`verify_freight_attempt` with its verify CLI) stay behind the operator gates
of the design review §10 item 5: after the 2026-11-01 staging grant recorded
below (E52), staging approval is granted, and independent review, Gate C
signing and a separate explicit launch approval each remain ungranted. The
v1 protocol-5 bytes (`corridor_freight.py`, `d5_freight_package/`), the root
`--version` file and every retained artifact are out of scope for this
section; nothing in it stages, signs, launches or claims. Lint and type
checks of record for the E53 fix round: `ruff check` and `git diff --check`
both clean squarely on the touched paths; `uvx ty check` on the wire
contract, the runner and both suites reports only the same five pre-existing
diagnostics already present at `bf6cc0b`.

## 2026-11-01 addendum — D5 freight delivery v2 E53 fix round (checked)

The E53 fix round against the independent design review
([docs/d5-freight-delivery-v2-design-review-2026-11-01.md](docs/d5-freight-delivery-v2-design-review-2026-11-01.md)
§12) restored `CONTEXT.md` byte-exact to the authority-supersession pin
(`sha256 36648f9c2fee4106efb35ae4ee8722983ebdfb482889e66ad53d759f6fa7cc29`),
fixed the freight state transitions (a wait-only pre-pickup/pickup-standing
window, an at-bay-and-empty delivery gate with the echoed bay tile, a
verified-departure LOADED snapshot bound to its matching pickup-monitor
echo), enforced the 60-day aggregate economy-day authority across the three
per-cycle windows, and hardened the replay verifier against drifted watch
requests. Verified offline facts, one run (exit 0):

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest \
  tests/test_corridor_freight_v2.py \
  tests/test_corridor_freight_v2_native.py \
  -q -p no:cacheprovider -rs
# → 61 + 67 passed, 0 failed

PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest \
  tests/test_authority_supersession.py tests/test_historical_protection.py \
  tests/test_industry_production_proof.py tests/test_structural_production.py \
  -q -p no:cacheprovider
# → 118 passed (the protected authority tests pass with the pinned bytes)

ruff check app/simulation/openttd/corridor_freight_v2.py \
  app/simulation/openttd/d5_freight_v2_package \
  app/simulation/openttd/proof/corridor_freight_v2_native.py \
  tests/test_corridor_freight_v2.py tests/test_corridor_freight_v2_native.py
git diff --check
```

The staged candidate of record is now
`artifacts/experiments/d5-corridor-freight-native-candidate-3` (E54,
2026-11-02) binding the E53 schedule: its proof commands sit in the staged
addendum section below. The earlier staged candidate
`artifacts/experiments/d5-corridor-freight-native-candidate-2` keeps the
pre-E53 sealed plan digest `22bdb874…60f` and stays byte-untouched: it is
stale-by-source-drift against this working tree by construction (no
re-stage, no re-seal), and both candidates' authorization states remain
`PENDING`/`CLAIM_ABSENT` exactly as recorded in their staging addenda.

## 2026-11-01 addendum — D5 freight delivery v2 staging (checked, gated at one gate)

Explicit operator authorization granted in-session covered the staging gate
only. The staging command of record, one run, first attempt, exit 0:

```bash
.venv/bin/python -m app.simulation.openttd.proof.corridor_freight_v2_native \
  prepare artifacts/experiments/d5-corridor-freight-native-candidate-2
# → PRELAUNCH PASS /home/fed/codes/softdev2/artifacts/experiments/d5-corridor-freight-native-candidate-2
```

Re-runnable read-only proofs on the staged candidate (never a re-stage, never
a re-seal, never an execution):

```bash
.venv/bin/python -m app.simulation.openttd.proof.corridor_freight_v2_native \
  preflight artifacts/experiments/d5-corridor-freight-native-candidate-2
# → PREFLIGHT PASS

.venv/bin/python -m app.simulation.openttd.proof.corridor_freight_v2_native \
  verify artifacts/experiments/d5-corridor-freight-native-candidate-2
# → {"authorization_state": "CLAIM_ABSENT", "statement": "the candidate was
#    never consumed by an operator authorization; no verified receipt is
#    possible", "verification": "AUTHORIZATION_UNVERIFIED"} — exit 1 by design
```

Facts of record: attempt `D5-FREIGHT-2`, kind `freight`, schema
`d5-freight2-prelaunch-v1`, seal (`PRELAUNCH.json` sha256)
`35557a74c33188fb2555a43871025099b2998eea317d8bbf9cf047a8d5b676d4`, pinned
prerequisite `d5-corridor-extension-native-candidate-3` re-verified (attempt
`D5-CORRIDOR-EXTENSION-3`, after-save `3748e00c…5420bd`), plan digest
`22bdb874…60f` and the 1-launch / 32-request / 60-day budgets unchanged, the
pinned binary sha `276d5b…904c` verified with no identical process running,
endpoints game 57627 / admin 34189 reserved and released, isolated retained
workspace with an owned session key, argv recorded and never executed,
`AUTHORIZATION.json` absent, no claim consumed. The `run` subcommand stays
behind Gate C signing and a separate explicit launch approval; nothing in
this section stages again, signs, launches or consumes.

## 2026-11-02 addendum — D5 freight delivery v2 fresh staging (E54, gated at one gate)

Explicit operator authorization granted in-session covered the staging gate
only, after the identity step of record (attempt `D5-FREIGHT-2` →
`D5-FREIGHT-3` in `corridor_freight_v2.py`, so the once-staged
never-consumed `D5-FREIGHT-2` name is never reused; this moves the
plan-model digest of record to `19112a9b…76e0`). The staging command of
record, one run, first attempt, exit 0:

```bash
.venv/bin/python -m app.simulation.openttd.proof.corridor_freight_v2_native \
  prepare artifacts/experiments/d5-corridor-freight-native-candidate-3
# → PRELAUNCH PASS /home/fed/codes/softdev2/artifacts/experiments/d5-corridor-freight-native-candidate-3
```

Re-runnable read-only proofs on the staged candidate (never a re-stage,
never a re-seal, never an execution):

```bash
.venv/bin/python -m app.simulation.openttd.proof.corridor_freight_v2_native \
  preflight artifacts/experiments/d5-corridor-freight-native-candidate-3
# → PREFLIGHT PASS

.venv/bin/python -m app.simulation.openttd.proof.corridor_freight_v2_native \
  verify artifacts/experiments/d5-corridor-freight-native-candidate-3
# → {"authorization_state": "CLAIM_ABSENT", "statement": "the candidate was
#    never consumed by an operator authorization; no verified receipt is
#    possible", "verification": "AUTHORIZATION_UNVERIFIED"} — exit 1 by design
```

Facts of record: attempt `D5-FREIGHT-3`, kind `freight`, schema
`d5-freight2-prelaunch-v1`, seal (`PRELAUNCH.json` sha256, also
`PRELAUNCH.sha256`)
`f308d32722508e3ed29bd3d297e9152cc5f8b33dae1ff1f666c02cd5bfd18a0e`, the
**E53 schedule of record** with plan/schedule digest
`ed5bad82…b1ff4` (staged == live derivation; uniform 10-economy-day
`window_day_cap` lease on all three watch windows) and plan-model digest
`19112a9b…76e0`, route `b2f80f46…7131` / witness `f1f00e13…686c`
unchanged; budgets unchanged {1 launch, 1 connection, 32 requests, 30
planned, 6 cycles, 60 days, window_day_cap 10, watch_ticks 2048,
running_cost_allowance 12, max_cost 5000, funds 490257, cycle_wall_cap
180, total 900}; pinned prerequisite `d5-corridor-extension-native-candidate-3`
re-verified (`D5-CORRIDOR-EXTENSION-3`, seal `404d42d9…6acd8` consumed,
after-save `3748e00c…5420bd`, `EXTENSION_COMPLETION_VERIFIED`), world =
the A1 `after.sav` in the prerequisite source-save load mode with the
pinned welcome (seed 17, 15.3, 256×256, start_day 712223); pinned binary
sha `276d5b…904c` verified with no identical process running, endpoints
game 58339 / admin 44483 reserved and released, isolated retained
workspace `openttd-15.3-uwcxtrxo` with the composed v2 GameScript, launch
argv recorded and never executed, frozen closure 3,493 entries pinning the
wire module `1efa9421…13a8`, runner module `176b0096…82ca`, package
`main.nut` `6704aa6e…952d` (== shipped package == isolated
`game/RoadFreightProof/main.nut`) and `info.nut` `03e5af7b…f7b`.
`AUTHORIZATION.json` absent, no claim consumed; candidate-1 (consumed) and
the stale-by-source-drift candidate-2 byte-untouched. The `run`
subcommand stays behind Gate C signing and a separate explicit launch
approval; nothing in this section stages again, signs, launches or
consumes.

## 2026-11-02 addendum — D5 freight delivery v2 Gate C Option-1 signing (E55, gated at one gate)

Explicit operator authorization in-session covered the Gate C signing gate
only, on the E54 staged bytes (seal `f308d327…18a0e` re-verified; the same
session's read-only evidence verification had first confirmed seal,
manifest, source freeze, prerequisite, HEAD and working-tree identity). One
earlier invocation of the checklist was interrupted by a transport failure
before any write (no authorization existed, no signature ever produced);
state was checked read-only and the complete checklist then executed
exactly once from the refusal gates. The pipeline of record is the
[key provisioning doc §1/§2/§4](docs/handoff/2026-10-17/
operator-key-provisioning.md) Option-1 checklist (refusal gates → checked
seed extraction → derived-key ≡ pinned-anchor check → one
`sign_authorization_record` run → signature verified under the pinned
anchor before any write → `write_authorization_record` → seed cleared),
as executed for the A1 §12.5/E39/E43 record.

Facts of record: canonical authorization payload sha256
`9cad63e481af565d67207424bc24c1e372b8e120a286b0a05c88327a897fa62b`;
`AUTHORIZATION.json` sha256
`3153d3407432be68038f1aaa390a8f3c5ec440834ea0e5983f8cde7b47f1dda5`;
`verify_authorization` PASS under the pinned anchor
`sha256-ed25519-public-key:cbb63ff58f17f13df3e1be0735fad18497e3a0c6ad6b5dd55491d708ae40c614`
binding attempt `D5-FREIGHT-3` / milestone `D5-FREIGHT` to seal
`f308d327…18a0e` (payload includes `operation_schedule`, `plan_digest`
`ed5bad82…b1ff4`, the exact budget table and the exact approved execution
command). `CLAIM.json` and `LAUNCH-CONSUMED.json` stay absent (created only
at launch). Re-runnable read-only proofs and their current outputs:
`preflight` → `PREFLIGHT PASS` exit 0; `verify` →
`{"authorization_state": "CLAIM_ABSENT", …, "verification":
"AUTHORIZATION_UNVERIFIED"}` exit 1 by design (authorized, never
consumed). The signature is binding only and is NOT launch approval: the
final remaining gate is one separate explicit operator launch approval for
exactly one native attempt, then replay + certified cleanup; nothing in
this section signs again, claims, launches or consumes.

## 2026-11-02 addendum — D5 freight delivery v2 launch executed exactly once (E56, terminal)

One explicit operator launch approval in-session covered exactly one native
OpenTTD 15.3 attempt for `D5-FREIGHT-3`, no retries, no reconnects. The
launch command of record, executed once, exit 1:

```bash
.venv/bin/python -m app.simulation.openttd.proof.corridor_freight_v2_native \
  run artifacts/experiments/d5-corridor-freight-native-candidate-3
# → {"cleanup_complete": true, "connections": 1, "exchanges": [], "halt":
#    {"error": "ValueError: freight exchange site-00 failed verification:
#    freight v2 exchange site-00 ended INVALID_SITE", "label": "site-00"},
#    "last_status": "NOT_DISPATCHED", "native_launches": 1, "requests": 1,
#    "returncode": 0, "state_changed": false, "status":
#    "PHASE_HALTED_PREFIX_PRESERVED", "verified": false} — run-exit=1
```

Facts of record: preflight PASS; the one-shot claim consumed exactly once
(`CLAIM.json` + `LAUNCH-CONSUMED.json` with the E55 authorization sha
`3153d340…f1dda5` and key identity `…cbb63ff5…40c614`); exchange `site-00`
(pickup 45748, delivery 50862, depot 45487, company 0, route
`b2f80f46…7131` and witness `f1f00e13…686c` both == staged) read back
`INVALID_SITE`, cost 0, funds 490257 unchanged, nothing dispatched, world
`HALTED_BEFORE_MUTATION`; certified cleanup all-true (credential removed,
listener closed, only an ephemeral `TIME_WAIT` on game port 58339 / admin
44483). Official read-only replay (never a re-run):

```bash
.venv/bin/python -m app.simulation.openttd.proof.corridor_freight_v2_native \
  verify artifacts/experiments/d5-corridor-freight-native-candidate-3
# → {"failed": {"error": "freight v2 exchange site-00 ended INVALID_SITE",
#    "label": "site-00", "status": "INVALID_SITE",
#    "world_state": "HALTED_BEFORE_MUTATION", "zero_seen": false},
#    "result_status": "PHASE_HALTED_PREFIX_PRESERVED",
#    "verification": "PHASE_HALTED_EVIDENCE_PRESERVED"} — exit 1
```

The site gate is an 8-branch refusal chain and a refused readback carries
no observation set by contract, so the fired branch is not disclosed on
the wire; preflight and the E55 closure pins stayed intact, so this is the
A1-anchored native world disagreeing with at least one site-admission
observation the staged E53 schedule assumed — not staged-source drift.
The attempt is terminal: no retry, re-stage, re-seal, re-sign or relaunch
ever; diagnosis and any fresh `D5-FREIGHT-4` candidate are separate
operator-approved gates. Nothing in this section launches again.

## 2026-11-02 addendum — D5-BOX-CENSUS-1 offline implementation (E60, checked)

Implementation of the E58-prescribed, E59-designed read-only box census,
strictly offline per its design: new additive protocol-9 wire contract
`app/simulation/openttd/corridor_box_census.py` (appenditive against the
frozen protocol-5/-6/-8 families), staging pipeline
`app/simulation/openttd/proof/corridor_box_census_native.py`, composed
GameScript package `app/simulation/openttd/d5_census_package/`
(`NetworkFreightProof extends D5CensusProof`), and the offline suites
`tests/test_corridor_box_census.py`,
`tests/test_corridor_box_census_vm.py` +
`tests/test_corridor_box_census_native.py`.
Verification of record (one run each, exit 0):

```bash
.venv/bin/python -m pytest tests/test_corridor_box_census.py \
  tests/test_corridor_box_census_vm.py tests/test_corridor_box_census_native.py \
  -q -p no:cacheprovider
# → 34 + 8 + 35 = 77 passed
```

Suite layout = E59 §9 items 4–6 as three files: the wire suite
(`test_corridor_box_census.py`, 34 tests), the package-VM suite
(`test_corridor_box_census_vm.py`, 8 tests — imports the wire file's VM
stubs and shared fixtures), and the staging/replay suite
(`test_corridor_box_census_native.py`, 35 tests).

ruff check app/simulation/openttd/corridor_box_census.py \
  app/simulation/openttd/proof/corridor_box_census_native.py \
  app/simulation/openttd/d5_census_package \
  tests/test_corridor_box_census.py tests/test_corridor_box_census_vm.py \
  tests/test_corridor_box_census_native.py
# → All checks passed!

uvx ty check app/simulation/openttd/corridor_box_census.py \
  app/simulation/openttd/proof/corridor_box_census_native.py \
  tests/test_corridor_box_census.py tests/test_corridor_box_census_vm.py \
  tests/test_corridor_box_census_native.py
# → 1 diagnostic (the frozen-mirror `invalid-method-override connect` class
#    the survey pipeline already carries); rest clean

git diff --check
```

Commands of record for the census candidate lifecycle (each a separate
operator gate after implementation; nothing was executed against any
retained directory, so no line below has been run against `artifacts/`):

```bash
.venv/bin/python -m app.simulation.openttd.proof.corridor_box_census_native \
  prepare <staging-directory>
#  → PRELAUNCH PASS <staging-directory>
.venv/bin/python -m app.simulation.openttd.proof.corridor_box_census_native \
  preflight <staging-directory>
#  → PREFLIGHT PASS
.venv/bin/python -m app.simulation.openttd.proof.corridor_box_census_native \
  run <candidate-directory>          # launch-gated, never yet authorized
.venv/bin/python -m app.simulation.openttd.proof.corridor_box_census_native \
  verify <candidate-directory>
#  → CENSUS_COMPLETION_VERIFIED (exit 0) or PHASE_HALTED_EVIDENCE_PRESERVED
```

`--prerequisite` defaults to the consumed A1 attempt directory
`artifacts/experiments/d5-corridor-extension-native-candidate-3`
(after-save `3748e00c…5420bd`), exactly as the survey pipeline binds it.
One implementation probe run of `prepare` against a `/tmp` staging path
(not this repo's tree, not `artifacts/`) proved the staging pipeline
end-to-end (`PRELAUNCH PASS`) and was discarded; the test suites stage
fresh candidates under `pytest` tmp directories through the same
production function, offline and consumable by the replay verifier only
after the missing post-launch artifacts are provided by the test.

## 2026-11-02 addendum — D5-BOX-CENSUS-1 staged (E61, checked)

Operator-authorized offline staging of the E60 census implementation of
record; one first-attempt run each, outputs verbatim, nothing launched:

```bash
.venv/bin/python -m app.simulation.openttd.proof.corridor_box_census_native \
  prepare artifacts/experiments/d5-box-census-native-candidate-1
#  → PRELAUNCH PASS /home/fed/codes/softdev2/artifacts/experiments/d5-box-census-native-candidate-1

.venv/bin/python -m app.simulation.openttd.proof.corridor_box_census_native \
  preflight artifacts/experiments/d5-box-census-native-candidate-1
#  → PREFLIGHT PASS

.venv/bin/python -m app.simulation.openttd.proof.corridor_box_census_native \
  verify artifacts/experiments/d5-box-census-native-candidate-1
#  → {"authorization_state": "CLAIM_ABSENT", "statement": "the census
#     candidate was never consumed by an operator authorization; no verified
#     completion is possible", "verification": "AUTHORIZATION_UNVERIFIED"}
#    exit=1 (correct for an unconsumed candidate)
```

Candidate of record `artifacts/experiments/d5-box-census-native-candidate-1`
(attempt `D5-BOX-CENSUS-1`, schema `d5-box-census-prelaunch-v1`): seal
(PRELAUNCH.json sha256, recomputed == `PRELAUNCH.sha256`)
`c4497053de7f2a280e41c771876deb45d299dcc74cde9f8eed97c8b30091e381`;
prerequisite the consumed A1 `D5-CORRIDOR-EXTENSION-3`
(`prerequisite` defaults to
`artifacts/experiments/d5-corridor-extension-native-candidate-3`, whose own
seal `404d42d9…acd8` matched), after-save `3748e00c…5420bd`; world mode
`PREREQUISITE_ATTEMPT_SOURCE_SAVE_LOAD` (seed 17, revision 15.3, start_day
712223); OpenTTD binary sha256 `276d5b69…1904c`; authorization key identity
public_key `cdc03e4b…0706`; budgets 1 launch / 10 planned exchanges / 32
requests / max_cost 0 / expected funds 490257 / reconnects 0 / retries 0.
No AUTHORIZATION.json or CLAIM.json exists in the candidate; `run` was never
invoked. The E60 `/tmp/opencode/census-prep-probe` staging was a discarded
probe and is not this record.

## 2026-11-02 addendum — D5-BOX-CENSUS-1 independent read-only verification (E62, checked)

Read-only re-verification of the E61 candidate
`artifacts/experiments/d5-box-census-native-candidate-1`:

```bash
.venv/bin/python -m app.simulation.openttd.proof.corridor_box_census_native \
  preflight artifacts/experiments/d5-box-census-native-candidate-1
#  → PREFLIGHT PASS
.venv/bin/python -m app.simulation.openttd.proof.corridor_box_census_native \
  verify artifacts/experiments/d5-box-census-native-candidate-1
#  → AUTHORIZATION_UNVERIFIED / CLAIM_ABSENT, exit 1 (still unconsumed)
```

Then a 13-axis read-only byte audit (source-derived re-derivation script; no
candidate writes, `.venv/bin/python -B`): 13/13 PASS, READY-FOR-GATE-C —
seal `c4497053…e381` recompute; identity constants; three-way world/prereq
binding `3748e00c…5420bd` + prereq seal `404d42d9…acd8`; binary bytes re-hashed
`276d5b69…1904c`; OpenGFX `validate_baseset` in-place (archive
`43a0c1da…03be`); 4 staged `.nut` byte-equal (bridge `NetworkFreightProof
extends D5CensusProof`); `census_planned` == derived schedule; budgets ==
`census_budgets()`; cross-guard ops pinned; refusal surface clean (23 files);
lineage clean; `x25519(.admin-secret) == public_key`; frozen record 3495
entries re-digested, none uncovered.

Disclosed limitation: the fresh-context subagent review was unavailable this
round (provider free-usage limit); the audit was performed in-session with
independent machinery — a true fresh-context review remains an operator
option. No launch/sign/claim; no candidate bytes mutated.

## 2026-11-02 addendum — D5-BOX-CENSUS-1 Gate C Option-1 signing (E63, gated at one gate)

In-session operator authorization covered exactly the Gate C signing gate, on
the E61 staged bytes (seal `c4497053…e381` re-verified) after the E62
read-only verification. The pipeline of record is the
[key provisioning doc §1/§2/§4](docs/handoff/2026-10-17/operator-key-provisioning.md)
Option-1 checklist (refusal gates → checked seed extraction → derived-key ≡
pinned-anchor check → one `sign_authorization_record` run → signature verified
under the pinned anchor before any write → `write_authorization_record` → seed
cleared), as executed for the survey E48 and freight E55 records. One earlier
invocation was interrupted by an auditor script compile error before any
execution — no key read into Python, no signature produced, no write; state
was confirmed clean read-only (23 files) and the complete checklist then
executed exactly once from the refusal gates.

Facts of record: canonical authorization payload sha256
`cd124c9e0dcb92a9b27c7a18fa587677825f88217749a37f44c2162534f64147`;
`AUTHORIZATION.json` sha256
`b9b9c0f4871f77965096a1ac5aa1046919421725b2652a303e5d71d6d1d449f7`;
`verify_authorization` PASS under the pinned anchor
`sha256-ed25519-public-key:cbb63ff58f17f13df3e1be0735fad18497e3a0c6ad6b5dd55491d708ae40c614`
binding attempt `D5-BOX-CENSUS-1` / milestone `D5-BOX-CENSUS` to seal
`c4497053…e381` (payload includes `operation_schedule`, `plan_digest`, the
exact budget table, the A1 `source_world` binding
`3748e00c…5420bd`, and the exact approved execution command). `CLAIM.json` and
`LAUNCH-CONSUMED.json` stay absent (created only at launch). Re-runnable
read-only proofs, current outputs: `preflight` → `PREFLIGHT PASS` exit 0;
`verify` → `AUTHORIZATION_UNVERIFIED`/`CLAIM_ABSENT` exit 1 by design
(authorized, never consumed); the census `PRELAUNCH.json` re-digested
unchanged `c4497053de7f2a28…` and the A1 prerequisite record byte-unchanged
`404d42d9fa1e1135…`. The signature is binding only and is NOT launch approval:
the final remaining gate is one separate explicit operator launch approval for
exactly one native attempt, then replay + certified cleanup; nothing in this
section signs again, claims, launches or consumes.

## 2026-11-02 addendum — D5-BOX-CENSUS-1 native launch consumed (E64, terminal)

One in-session operator launch approval ("Approved — run once, now") was
consumed for exactly one native attempt on the E63-signed candidate (seal
`c4497053…e381`, AUTHORIZATION `b9b9c0f4…49f7`, both byte-re-verified after
launch). Commands and outputs of record:

```
.venv/bin/python -m app.simulation.openttd.proof.corridor_box_census_native \
  run artifacts/experiments/d5-box-census-native-candidate-1
# run-exit=1 (terminal on this candidate)
```

Verbatim verdict (`result.json`): `"status":
"PHASE_HALTED_PREFIX_PRESERVED"`, `"verified": false`, phase verification
`CENSUS_INCOMPLETE`, halt `"error": "ValueError: the census exchange dbox-00
failed verification: census exchange dbox-00 ended UNSUPPORTED_NATIVE_FACT"`,
label `dbox-00`; exchanges READY 7/10 (`radius-00`, `acc-00`, `acc-01`,
`prod-00`, `pbox-00`, `pbox-01`, `pbox-02`), pending `dbox-00`/`dbox-01`/
`dbox-02`; budgets `requests: 8`/32, `connections: 1`, `native_launches: 1`,
`preflight: "PASS"`, `command_accepted: true`, `returncode: 0`,
`state_changed: false`, `cleanup_complete: true`, funds £490257 constant,
cost £0 — nothing dispatched. Measured facts: spot controls radius 3, `acc-00`
(50351, 0), `acc-01` (50862, 8), prod 104; producer box 45748 measured
exactly-1 (`exactly_one: true`, member `{a: 0, id: 0, p: 104, tile: 44983}`,
pages `pbox-00` cursor 0 row_count 1 `more: false`, `pbox-01`/`pbox-02` empty,
no overflow); delivery box 50862 not measured on halt (`dbox-00` response
`"status": "UNSUPPORTED_NATIVE_FACT"`, `cost: 0`, `funds: 490257`,
`max_cost: 0`; `count: null`, `rows: []`, `exactly_one: false`); branch8
verdict `CENSUS_GATE_UNDECIDED_INCOMPLETE` ("an unevidenced role-filtered
membership can decide nothing; this is a recorded fact, never a manufactured
verdict").

Independent official read-only replay of record:

```
.venv/bin/python -m app.simulation.openttd.proof.corridor_box_census_native \
  verify artifacts/experiments/d5-box-census-native-candidate-1
{"error": "census exchange dbox-00 ended UNSUPPORTED_NATIVE_FACT", "failed":
 {"label": "dbox-00", "status": "UNSUPPORTED_NATIVE_FACT",
  "world_state": "HALTED_BEFORE_MUTATION"}, "pending": ["dbox-01", "dbox-02"],
 "result_status": "PHASE_HALTED_PREFIX_PRESERVED",
 "verification": "PHASE_HALTED_EVIDENCE_PRESERVED"}
# verify-exit=1
```

One-attempt conservation and cleanup: `CLAIM.json`
`{"consumed": true, "launches_allowed": 1, "retries": 0}`,
`LAUNCH-CONSUMED.json` schema `d5-native-launch-consumed`; further launch on
this candidate is refused by the pre-existing `grant_launch` CLAIM gate
(covered by the offline suite; no `run` re-execution attempted this round).
`cleanup.json`: `credential_removed: true`, `listener_closed: true`,
`process_reaped: true`, `remaining_processes: []`, `workspace_disposed: true`;
welcome world matches the A1 after-save binding (rev 15.3, seed 17,
start_day 712223, dedicated). Retained bytes: 32 files under the candidate,
covered by `artifact-manifest.sha256`, including `session-before.sav`
(sha256 prefix `1966b5c7e9e2c0d6`), `after-diagnostic.sav`
(`b6731d399f4e46a3`) and the per-exchange request/response JSONs.

Interpretation (E59 §8 outcome matrix): the "both boxes role-filtered exactly
1" row is NOT met, so the next action is the **site-plan adaptation/design
round first** (stop re-pin / pre-build acceptance), deliberately its own round
per §10.4; neither an F-12-fix round nor `D5-FREIGHT-4` is opened from this
record; measured facts and the refusal stand as recorded, never relabelled.
Re-attempting the census on this candidate is impossible — any new attempt
needs a fresh staging → review → Gate C cycle on a new candidate + seal and a
fresh operator launch approval. No commit by the agent.

## 2026-11-02 addendum — D5-BOX-CENSUS-2 adaptation + staging (E65/E66)

Root cause of the E64 terminal halt, pinned at source for the open of record:
OpenTTD 15.3 `src/script/api/script_industry.cpp` (`ScriptIndustry::
GetLastMonthProduction`) returns `-1` for any industry that does not handle
the queried cargo as produced and never throws for valid arguments;
`IsCargoAccepted` returns 0/1/2. The delivery box's acceptors do not produce
cargo 1, so the E59-consistent `production < 0` guard fired inside
`CensusBoxOp` and the blanket catch mapped the fact to
`UNSUPPORTED_NATIVE_FACT`. The E65 addendum (§12 of the census design doc)
carries the fact verbatim: `CensusRow.p` domain widens to `{-1} ∪
[0, 2147483647]` with `-1` meaning only the native non-producer fact; roles
stay `p > 0` / `a == 1`; the handler logs
`D5_CENSUS_BOX_NON_PRODUCER <industry> <first-sighting-tile>` per
non-producer and `D5_CENSUS_THROW <request_id> <fact>` inside the blanket
catch; every other negative read stays refused. Attempt identity of record
becomes `D5-BOX-CENSUS-2`.

Offline verification: suites 35 + 8 + 35 = 78 passed, exit 0; ruff clean on
all six touched paths; `uvx ty` leaves only the pre-existing tolerated
frozen-mirror `connect` diagnostic; `git diff --check` clean. Staging:
`.venv/bin/python -m app.simulation.openttd.proof.corridor_box_census_native
prepare artifacts/experiments/d5-box-census-native-candidate-2` → `PRELAUNCH
PASS` (23 files), seal (PRELAUNCH.json sha256)
`deb121ada1e7337692b4daadb01e59978b066d00298ceca00dc51f6b2684690f`;
independent payload derivation
`1116d140c2c0b423…` (derived == pipeline key pair); plan digest
`ee47cc14065201d9…` re-derived from the module and pinned byte-exact in the
staged prelaunch; staged package `sha256 93c04d12856b3e3f…` byte-identical
to the tree's adapted `main.nut`; preflight `PREFLIGHT PASS` exit 0; verify
`AUTHORIZATION_UNVERIFIED`/`CLAIM_ABSENT` exit 1 by design.

## 2026-11-02 addendum — D5-BOX-CENSUS-2 Gate C Option-1 signing (E67, one gate)

In-session operator authorization covered exactly the Gate C signing gate of
candidate-2 (E66-staged bytes, seal re-verified). The pipeline of record is
the key-provisioning doc Option-1 checklist (refusal gates → checked seed
extraction in-shell, never printed/filed/arg-passed, cleared →
derived-key ≡ pinned-anchor check → one `sign_authorization_record` run →
signature verified under the pinned anchor before any write →
`write_authorization_record` → in-process verify → seed cleared
(`SEED_CLEARED`)). Facts of record: payload sha256
`1116d140c2c0b4237b938aeb95ae229bc1e9f7cc75ed45a34c281e69493e2f86`;
`AUTHORIZATION.json` sha256
`ea74e1f8c595fc1a7832f7d5ca1954d3a5b328684c8646b7c99cf637c8aff3c9`;
operator key identity
`sha256-ed25519-public-key:cbb63ff58f17f13df3e1be0735fad18497e3a0c6ad6b5dd55491d708ae40c614`
binding attempt `D5-BOX-CENSUS-2`/milestone `D5-BOX-CENSUS` to seal
`deb121ada1e7337692b4daadb01e59978b066d00298ceca00dc51f6b2684690f` (payload
includes `operation_schedule`+`plan_digest`, the exact budget table, the A1
`source_world` binding `3748e00c…`, and the exact approved
`execution_command`). `CLAIM.json`/`LAUNCH-CONSUMED.json` stay absent
(created only at launch). Re-runnable read-only proofs: `preflight` →
`PREFLIGHT PASS` exit 0; `verify` → `AUTHORIZATION_UNVERIFIED`/`CLAIM_ABSENT`
exit 1 by design (authorized, never consumed). The signature is binding only
and is NOT launch approval: the final gate is one separate explicit operator
launch approval for exactly one native attempt, then replay + certified
cleanup; nothing in this section signs again, claims, launches or consumes.

## 2026-11-02 addendum — D5-BOX-CENSUS-2 launch consumed (E68, terminal)

One in-session operator launch approval ("Approved — run once, now") was
consumed for exactly one attempt on the E67-signed candidate-2 (seal and
AUTHORIZATION bytes re-verified post-launch). Command of record:

```
.venv/bin/python -m app.simulation.openttd.proof.corridor_box_census_native \
  run artifacts/experiments/d5-box-census-native-candidate-2
# run-exit=1 (terminal on this candidate)
```

Measured census facts of record: ALL 10 exchanges READY — radius 3, spots
(50351, 0) / (50862, 8), prod 104, funds £490257 constant, cost £0,
state_changed false, requests 10/32, connections 1, `preflight: "PASS"`,
phase verification `CENSUS_COMPLETE`, plan `ee47cc…` byte-pinned. The
both-boxes memberships the census exists to name, now measured once and
kept under `result.json` + per-exchange JSONs:

- pickup box 45748: exactly-one producer member — `{id: 0, tile: 44983,
  p: 104, a: 0}`; pages cursor 0/3/6 = row_count 1/0/0, `more: false`
  everywhere, `overflow: false`.
- delivery box 50862: exactly-one acceptor member — `{id: 1, tile: 51116,
  p: -1, a: 1}`; pages cursor 0/3/6 = row_count 1/0/0, `more: false`
  everywhere, `overflow: false`. The `p: -1` is the adapted E65 native
  non-producer fact (15.3 `GetLastMonthProduction`), carried verbatim from
  the handler logs (`D5_CENSUS_BOX_NON_PRODUCER 1 51116`) to the wire.
- branch-8 offline recompute on those rows: verdict `CENSUS_GATE_PASSES`,
  role_counts {producer: 1, acceptor: 1}, statement "the role-filtered
  recompute from the listed census rows matches the v2 gate's own
  exactly-one check on both boxes".

Terminal classification: `status: "FAILED_CLEANUP"`,
`prior_status: "NATIVE_CENSUS_COMPLETE"`. The attempt's completion gate
refused on the one post-reap endpoint observation (verbatim
`cleanup.json`): `verification_error: "Live or ambiguous endpoint socket:
{'table': 'tcp', 'local': '127.0.0.1', 'local_port': 42838, 'remote':
'127.0.0.1', 'remote_port': 57125, 'state': 11, 'inode': 0}"` — kernel
state 11 = TCP_CLOSING, not 6 = TCP_TIME_WAIT; the frozen
`linux-kernel-endpoint-closure-v1` policy allows residual TIME_WAIT only
(ambiguous=FAIL_CLOSED, sleeps 0, retries 0), so the observation instant
landed inside the loopback simultaneous-close transition it cannot
certify. The process itself reaped cleanly (`returncode 0`,
`remaining_processes: []`, `cleanup_error: []`), but the certification
gate is therefore not met and the attempt cannot verify as complete.

Independent official read-only replay of record:

```
.venv/bin/python -m app.simulation.openttd.proof.corridor_box_census_native \
  verify artifacts/experiments/d5-box-census-native-candidate-2
{"cleanup_complete": false,
 "cleanup_verification_error": "Live or ambiguous endpoint socket: …state 11…",
 "result_status": "FAILED_CLEANUP",
 "verification": "ATTEMPT_FAILED_EVIDENCE_PRESERVED"}
# verify-exit=1
```

One-attempt conservation: `CLAIM.json` `{"consumed": true,
"launches_allowed": 1, "retries": 0}`, `LAUNCH-CONSUMED.json` schema
`d5-native-launch-consumed`; the E67 authorization is consumed and any
further launch on this candidate refuses on the CLAIM gate. 58 files
retained under candidate-2, covered by `artifact-manifest.sha256`.

Interpretation (E59 §8 matrix): the "both boxes role-filtered exactly 1"
row's facts ARE MET on the measured bytes (branch-8 `CENSUS_GATE_PASSES`),
and the census's own evidence prescribes no site-plan adaptation. The
attempt verdict of record stays FAILED_CLEANUP — an attempt-ceremony
refusal at its one unmet gate, never a census finding, never relabelled.
Promoting the F-12-fix → `D5-FREIGHT-4` sequencing on these bytes is a
design-review decision on the retained evidence, not an automatic gate
closure. Re-attempting the census needs a fresh staging → review → Gate C
cycle on a new candidate + seal and a fresh operator launch approval; both
consumed attempts (candidate-1, candidate-2) stay terminal. No commit by
the agent.

## 2026-11-02 addendum — D5-F12-DEPOT depot-connectivity mutation offline implementation (E69–E71, checked)

The E58 §2.1 F-12 fix implemented as a dedicated one-shot native mutation
workflow, offline only: new additive protocol-10 wire contract
`app/simulation/openttd/corridor_depot_mutation.py`, composed GameScript
package `app/simulation/openttd/d5_depot_mutation_package/`
(`NetworkFreightProof extends D5DepotMutationProof`), staging pipeline
`app/simulation/openttd/proof/corridor_depot_mutation_native.py` (prerequisite
re-binds the consumed A1 candidate-3 after-save `3748e00c…5420bd` via the
shared survey binding), design record
`docs/d5-f12-depot-mutation-protocol-2026-11-02.md`, and the offline suites
`tests/test_corridor_depot_mutation.py`,
`tests/test_corridor_depot_mutation_vm.py` +
`tests/test_corridor_depot_mutation_native.py`.
Verification of record (one run each, exit 0):

```bash
.venv/bin/python -m pytest tests/test_corridor_depot_mutation.py \
  tests/test_corridor_depot_mutation_vm.py tests/test_corridor_depot_mutation_native.py \
  -q -p no:cacheprovider
# → 29 + 8 + 36 = 73 passed
```

Suite layout = wire suite (29) importing the shared VM stubs for the package
suite (8, real Squirrel), and the staging/replay suite (36).

Static checks of record:

```bash
ruff check app/simulation/openttd/corridor_depot_mutation.py \
  app/simulation/openttd/proof/corridor_depot_mutation_native.py \
  app/simulation/openttd/d5_depot_mutation_package \
  tests/test_corridor_depot_mutation.py tests/test_corridor_depot_mutation_vm.py \
  tests/test_corridor_depot_mutation_native.py
# → All checks passed!

uvx ty check app/simulation/openttd/corridor_depot_mutation.py \
  app/simulation/openttd/proof/corridor_depot_mutation_native.py \
  tests/test_corridor_depot_mutation_native.py tests/test_corridor_depot_mutation_vm.py
# → All checks passed!

git diff --check
sha256sum CONTEXT.md
# → 36648f9c2fee4106efb35ae4ee8722983ebdfb482889e66ad53d759f6fa7cc29
```

Commands of record for the depot candidate lifecycle (each a separate
operator gate after implementation; nothing was executed against any
retained directory, so no line below has been run against `artifacts/`):

```bash
.venv/bin/python -m app.simulation.openttd.proof.corridor_depot_mutation_native \
  prepare <staging-directory>
#  → PRELAUNCH PASS <staging-directory>
.venv/bin/python -m app.simulation.openttd.proof.corridor_depot_mutation_native \
  preflight <staging-directory>
#  → PREFLIGHT PASS
.venv/bin/python -m app.simulation.openttd.proof.corridor_depot_mutation_native \
  run <candidate-directory>          # launch-gated, never yet authorized
.venv/bin/python -m app.simulation.openttd.proof.corridor_depot_mutation_native \
  verify <candidate-directory>
#  → F12_MUTATION_COMPLETION_VERIFIED (exit 0) or PHASE_HALTED_EVIDENCE_PRESERVED
```

`--prerequisite` defaults to the consumed A1 attempt directory
`artifacts/experiments/d5-corridor-extension-native-candidate-3`
(after-save `3748e00c…5420bd`), exactly as the survey and census pipelines
bind it. Nothing is staged, signed, authorized, launched, claimed or
consumed in this round: all four native gates (staging approval, independent
review, Gate C signing, separate launch approval) remain ungranted operator
approvals, each one attempt, no retry. The `run` line exists for a later
approved round only.

### Executed lifecycle (2026-11-03, E74/E75)

The gates above were granted and consumed exactly once for attempt
`D5-F12-DEPOT-2` on
`artifacts/experiments/d5-corridor-depot-mutation-native-candidate-2`
under one operator chain approval ("agree Stage D5-F12-DEPOT-2 allow and
agree all"): `prepare` → `PRELAUNCH PASS` (seal `16592103…544a`), read-only
audit (frozen closure 3496/0, staged package ≡ live fixed package
`e00eeecb…5d67`), gate-C `PREFLIGHT PASS` + pre-auth
`AUTHORIZATION_UNVERIFIED`/`CLAIM_ABSENT`, Option-1 signing (record sha
`9628bcb5…450b`, anchor `cbb63ff5…40c614`), one launch — run exit 0
`NATIVE_DEPOT_MUTATION_COMPLETE` with the before gate measuring the E72
§6.4 pinned expected read — replay `verify` →
`F12_MUTATION_COMPLETION_VERIFIED` exit 0, certified cleanup complete
(`cleanup_complete: true`; client-side `TIME_WAIT (inode 0)` preserved
as-is), artifact manifest 28/28. The depot milestone issues no
authoritative new save: its world binding stays the pinned A1
prerequisite after-save `3748e00c…5420bd`, verified intact post-run. The
attempt is terminal COMPLETE; consumed-candidate `run`/launch gates must
never be re-executed, and post-run `preflight` cannot reopen the disposed
workspace (expected consume-once shape). Caveat of record: these
executed-gate lines are the already-consumed attempt of record — do not
rerun them against any consumed candidate; a future attempt needs a fresh
staging under a new identity.

## 2026-11-03 addendum — D5-FREIGHT-4 staged (E76)

Separate operator staging approval covered exactly: the FREIGHT-4 identity
step (`FREIGHT_ATTEMPT_V2` → `D5-FREIGHT-4` in `corridor_freight_v2.py`,
consumed terminal attempt-3 preserved), suites check (freight v2 + native,
128 passed, exit 0), and one `prepare` run — exit 0
`PRELAUNCH PASS artifacts/experiments/d5-corridor-freight-native-candidate-4`
with read-only `preflight` PASS and pre-auth
`AUTHORIZATION_UNVERIFIED`/`CLAIM_ABSENT` (exit 1). Stopped at the
approved boundary: the review, Gate C signing and launch gates for this
candidate remain ungranted; do not sign, launch or consume from this
section — those each need their own explicit future operator approval
recorded as its own addendum.

## 2026-11-03 addendum — D5-FREIGHT-4 BLOCKED before Gate C (E77)

The six-step workflow above consumed its read-only steps 1-2 and stopped by
its own STOP rule: no signature exists, no launch, nothing consumed.
Blocking fact of record (measured): the freight runtime world is the A1
after-save `3748e00c…5420bd` loaded verbatim, and the F-12-DEPOT-2 run
measured that same loaded world reading `connected_depot_to_front false` /
`connected_front_to_depot false` at `before-00` before mutating its own
disposed copy — no authoritative post-fix save exists anywhere and the
freight family carries no mutation ops, so this candidate's `site-00`
admission (`depot_edge is True`, `corridor_freight_v2.py:1276-1278`) can
only read false. Do NOT sign, launch or consume
`artifacts/experiments/d5-corridor-freight-native-candidate-4` from this
section; closing the lineage gap is a design round of its own (three paths
recorded at E77), each needing a fresh staging under a fresh identity.

## 2026-11-03 addendum — Path A R2: D5-F12-DEPOT-3 staged (E78/E79)

The strict after-save emission round is implemented offline (R2, approved)
and one candidate exists: `artifacts/experiments/
d5-corridor-depot-mutation-native-candidate-3`, attempt `D5-F12-DEPOT-3`,
schema `d5-f12-depot-prelaunch-v2`, seal `4df12e1fbc15e164…`. Its flow of
record (no signature, no claim, no launch on its own):

    .venv/bin/python -m app.simulation.openttd.proof.\
        corridor_depot_mutation_native prepare \
        artifacts/experiments/d5-corridor-depot-mutation-native-candidate-3
    # → PRELAUNCH PASS;  then the read-only gates:
    .venv/bin/python -m app.simulation.openttd.proof.\
        corridor_depot_mutation_native preflight \
        artifacts/experiments/d5-corridor-depot-mutation-native-candidate-3
    .venv/bin/python -m app.simulation.openttd.proof.\
        corridor_depot_mutation_native verify \
        artifacts/experiments/d5-corridor-depot-mutation-native-candidate-3
    # verify exits 1 pre-authorization (CLAIM_ABSENT) by design.

On a launch, the verified completion MUST emit the authoritative
`after.sav` (strict save; digest/size bound into receipt.json/result.json
and re-derived into `after-save-binding.json`); a strict save refusal on
the complete path is terminal `PHASE_COMPLETE_SAVE_REFUSED` and is never
retried or relabeled. Do not treat the diagnostic-only `after-diagnostic.sav`
as the world of record; it was never an authoritative artifact.

### Executed launch (2026-11-03, E82) — terminal, do not rerun

Under one explicit operator launch approval (separate from Gate C), the
signed candidate ran exactly once with the env-of-record paths set before
Python started:

```bash
export OPENTTD_BINARY="/home/fed/Downloads/openttd-15.3-linux-generic-amd64/openttd"
export OPENTTD_OPENGFX_ARCHIVE="/home/fed/codes/softdev2/artifacts/runtime/verified-assets/opengfx-8.0-all.zip"
.venv/bin/python -m app.simulation.openttd.proof.corridor_depot_mutation_native run \
    artifacts/experiments/d5-corridor-depot-mutation-native-candidate-3
```

Outcome of record: exit 0 `NATIVE_DEPOT_MUTATION_COMPLETE` verified=true;
before-00 reproduced the E58 diagnosis verbatim (both directions false);
after-00 measured both directions TRUE (front 45743, owner 0); fleet 0;
funds `490257→490197→490055→489650→489650→489650`; the strict save emitted
the authoritative `after.sav` — 61992 bytes, digest
`183b20273a54ebe1a2cd9306145a9ea820bbd6114b1608c42079b4e1b1efe6a6` bound
three-way (result.json == receipt.json == retained file) — and replay
`verify` → `F12_MUTATION_COMPLETION_VERIFIED` exit 0 with
`after-save-binding.json` derived byte-exactly (source_world = the pinned
A1 after-save `3748e00c…5420bd`, funds_at_close 489650, edge_facts
both-TRUE, fleet 0). Cleanup certified; artifact manifest 29/29 including
after.sav (only the replay-derived binding stands outside it, by the
manifest-balance rule); `after-diagnostic.sav` remains diagnostic-only.
This attempt is terminal COMPLETE and consumed: never re-run `run` on
this candidate. The authoritative post-mutation world of record for the
downstream freight lineage (R3 reload + R4 freight v3) is
`artifacts/experiments/d5-corridor-depot-mutation-native-candidate-3/after.sav`.

## 2026-11-06 — ticket-12 P07 replay closure (commands of record)

The corridor lineage's terminal receipts replay into the three fresh sibling
output directories of record (offline, read-only over the retained attempt
trees; regenerate only into a NEW output directory — never into a retained
one):

```bash
.venv/bin/python -m app.experiments.cli analyze-native-attempts \
  artifacts/experiments/d5-corridor-depot-mutation-native-candidate-3 \
  --output artifacts/experiments/p07-replay-d5-corridor-2026-11-06/round3-depot-chain

.venv/bin/python -m app.experiments.cli analyze-native-attempts \
  artifacts/experiments/d5-corridor-cargoflow2-native-candidate-6 \
  --output artifacts/experiments/p07-replay-d5-corridor-2026-11-06/route-v1-round6

.venv/bin/python -m app.experiments.cli analyze-native-attempts \
  artifacts/experiments/d5-corridor-cargoflow2-native-candidate-7 \
  --output artifacts/experiments/p07-replay-d5-corridor-2026-11-06/route-v2-round7
```

The arm refuses two directories with the same attempt id in one invocation —
round-6 and round-7 (both `D5-CARGOFLOW-2`) replay as separate siblings of
record, never pooled. Labels travel per ADR-0001; the funds echoes and the
verbatim finance blocks ride the receipt rows; the offset-35 one-unit funds
divergence of record (round-6 484986 vs round-7 484985) stands carried
verbatim.

Focused replay gate of record:

```bash
.venv/bin/pytest tests/test_native_attempt_analytics.py \
  tests/test_performance_insights.py
```

## 2026-11-06 — delivered-class tail close (commands of record)

The tail's consumed candidate (the delivered `(route_version 2,
schedule_version 2)` arming, candidate-9) verifies offline, read-only,
through the production surface — arm-correct since the E134 fix (the
replay readback inherits the arm from the correlated retained request,
exactly as the wire seam does):

```bash
.venv/bin/python -m app.simulation.openttd.proof.corridor_cargoflow2_native \
  verify \
  artifacts/experiments/d5-corridor-cargoflow2-native-candidate-9
```

Output of record: exit 0, `verification == CARGOFLOW2_COMPLETION_VERIFIED`,
phase verdict verbatim `CARGOFLOW2_LOADED_NEVER_DELIVERED` (the 26-row
delivered ladder with `unloadings []`, finance close 484,764 / delivered 0
/ income 0 — the delivered-miss class of record, E133/E134/E135). Before
those run bytes existed, `preflight` ran read-only over the staged tree:

```bash
.venv/bin/python -m app.simulation.openttd.proof.corridor_cargoflow2_native \
  preflight \
  artifacts/experiments/d5-corridor-cargoflow2-native-candidate-9
```

Never `run` on this candidate: the launch claim is single-use and consumed
`d5-native-launch-consumed` at the ONE authorized launch (E133); a further
native attempt needs its own staged candidate, independent review, Gate C
signature and explicit operator authorization.

## 2026-11-06 — corridor production round over candidate-11 (commands of record)

The round staged, reviewed and consumed a fresh delivered-arm candidate
(`d5-corridor-cargoflow2-native-candidate-11`, E136–E138), superseded by a
fresh identity only: the round's first staging (`…candidate-10`) carried the
un-bumped candidate-9 identity badge over its own tree, its staged bytes stay
preserved at that failed-identity state (seal `a01a5929…f8da68`), never
signed, claimed or launched, and its `preflight` refuses fail-closed through
the frozen-source gate. The offline replay surface of record on the consumed
candidate-11 (the round's THIRD command of record, after `prepare` into a new
directory and `preflight`):

```bash
.venv/bin/python -m app.simulation.openttd.proof.corridor_cargoflow2_native \
  verify \
  artifacts/experiments/d5-corridor-cargoflow2-native-candidate-11
```

Output of record: exit 0, `verification == CARGOFLOW2_COMPLETION_VERIFIED`,
phase verdict verbatim `CARGOFLOW2_LOADED_NEVER_DELIVERED` — the
delivered-miss twice-reproduced on retained evidence (E137/E138): four loads
latched (5/10/15 @flow-08 day 712271, the NEW 20-load @flow-09 day 712272),
the 20-ton truck departed (day 712274) and arrived at the bay (day 712291),
`unloadings []`, bay acceptance never moved (finance day 712292: delivered 0,
income 0, funds 484,764), finish `PHASE_STOPPED` with the vehicle still
RUNNING loaded at the bay. Both consumed candidates verify through the same
command shape (`candidate-9` above, `candidate-11` here); never `run` on
either — each launch claim is single-use and consumed
`d5-native-launch-consumed` at its ONE authorized launch; a further native
attempt needs its own staged candidate, independent review, Gate C signature
and explicit operator authorization.

## 2026-11-07 addendum — Project Phase C offline verification (FD-C-1 / FD-C-2, checked)

Offline only: no OpenTTD launch, no AdminPort connection, no candidate work,
no `artifacts/` mutation. Record doc:
[docs/phase-c-reconciliation-feasibility-2026-11-07.md](docs/phase-c-reconciliation-feasibility-2026-11-07.md).

```bash
# FD-C-1 re-derivation (byte-compares to the retained reports of record)
.venv/bin/python -m app.simulation.openttd.v2_semantic_reconciliation \
  artifacts/demos/playable-demo-698799a2dfb146948fd2983ff2032253/network-facts-0.json \
  artifacts/demos/classification-exec-seed17-3a8f9e46 \
  /tmp/opencode/fdc1_recheck \
  --apply-adr-012 --apply-adr-013 --rebind-p08
# → verdict SEMANTICALLY_RECONCILED_TEMPORAL_UNRESOLVED; raw_gate=83,
#   definitional=77, temporal=6, contradictions=0, unresolved=0; the four
#   retained reports digest-equal (c1cfa970…, 221ce926…, 7616f626…,
#   079fce64…); p08-policy-rebinding c9d11d41… byte-equal; the
#   unknown-occupancy diagnosis 66ed07cc… JSON-value-equal only.

# FD-C-2 decision of record (derived output, git-ignored artifacts dir)
.venv/bin/python -m app.planning.phase_c_feasibility \
  artifacts/experiments/phase-c-feasibility-2026-11-07 \
  --project-root /home/fed/codes/softdev2
# → outcome INCOMPLETE_EVIDENCE, 19 inputs; report JSON sha256
#   67183cf6…31fa4, Markdown sha256 edeac983…5dab; two independent
#   derivations are byte-equal.

# Focused suites of record (131 tests total)
.venv/bin/pytest tests/test_v2_semantic_reconciliation.py \
  tests/test_census_authority_policy.py \
  tests/test_p08_policy_rebinding.py \
  tests/test_p08_v2_snapshot.py
# → 83 passed
.venv/bin/pytest tests/test_phase_c_feasibility.py
# → 48 passed (retained-evidence pins skip honestly when evidence absent)

# Touch-path hygiene
.venv/bin/ruff check app/planning/phase_c_feasibility.py tests/test_phase_c_feasibility.py
.venv/bin/ruff format --check app/planning/phase_c_feasibility.py tests/test_phase_c_feasibility.py
.venv/bin/python -m py_compile app/planning/phase_c_feasibility.py tests/test_phase_c_feasibility.py
git diff --check
uvx ty check app/planning/phase_c_feasibility.py tests/test_phase_c_feasibility.py
# → ruff/format/compile/diff-check clean; ty 1 diagnostic (deliberate
#   runtime-validated refusal in the test file; counted, never repaired).
```
