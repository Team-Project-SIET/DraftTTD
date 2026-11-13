# Live demo workflow and readiness (2026-11-13)

This document describes the workflow a customer-facing live demo would follow,
and the readiness of each demonstrable capability. It is documentation only:
**no statement here authorizes a runtime action.** Native runs (OpenTTD launch,
AdminPort connection, `--run-openttd` / `--run-postgres`) happen only when the
operator explicitly authorizes them, once, with no retry and no reconnect.

## 1. Readiness summary

| Capability | Status | Evidence |
| --- | --- | --- |
| Fixed-demo MVP: plan → build → deliver → report (one server, one spectator, one encrypted Admin connection; 3 services, 60 coal, £1,022 revenue, fresh P07 reporting, replay, certified cleanup) | VERIFIED | E1 |
| Standalone freight delivery (fixed plan, 20 units) | VERIFIED | Attempt 4 receipt (README §Customer handover) |
| Planner-driven delivery with attributed payment (20 coal) | VERIFIED | Attempt 9 |
| Two and three serial P05-selected services delivered in one world | VERIFIED | Attempts 12/14/17 (Attempt 17: 60 coal, £1,018 revenue, £28,459 CAPEX) |
| Corridor road/station/depot construction | PROVEN for exactly the reviewed v3 scope only | E35 |
| Corridor survey, extension and acceptance census | VERIFIED | E40, E44, E49 |
| Corridor cargo **delivery** | NOT PROVEN — every corridor cargo-flow round ended `CARGOFLOW2_LOADED_NEVER_DELIVERED`; no DELIVERED receipt exists | E36 (open), E124, E133, E134 |
| Random-world service execution | FAILED typed terminals; delivery UNPROVEN (Phase C `INCOMPLETE_EVIDENCE`) | E142, E204; attempts E150–E157, E197; seed battery E198–E201 |
| Canonical five economy years 1951–1955 observed | VERIFIED | E195 (Phase B closed) |
| OPEX / ROI / profitability | UNKNOWN — revenue is never reported as profit (ADR-0001 D5) | ADR-0001 |

The honest headline for a demo: **the fixed-demo MVP is the stable, verified
showpiece; everything else is shown from retained evidence with its scope
limits stated.**

## 2. Prerequisites (before Python starts)

Per [REPRODUCE.md](../REPRODUCE.md) — the commands of record:

- OpenTTD **15.3** Linux generic amd64 binary and OpenGFX 8.0 archive,
  with paths exported **before** Python imports the runner:

  ```bash
  export OPENTTD_BINARY="/absolute/path/to/openttd-15.3-linux-generic-amd64/openttd"
  export OPENTTD_OPENGFX_ARCHIVE="/absolute/path/to/opengfx-8.0-all.zip"
  ```

- Pinned SHA-256s are re-verified at run start — binary
  `276d5b698a6b706154f3af588f6f885b3aebe518f4ecc8f869abf71383b1904c`,
  OpenGFX archive
  `43a0c1dabf39cb865394f3a6cc36d4da5c10ecfaaf55652043104806810903be`.
  Other binary or graphics versions are unsupported.
- Python 3.14+ via `.venv/bin/python` from the repository root; dependencies
  via `uv sync --locked` on a fresh environment. No PostgreSQL or Docker is
  required for the demo.
- Demo guide for setup and spectator controls:
  [examples/openttd-demo/README.md](../examples/openttd-demo/README.md).

## 3. The demo workflow, stage by stage

### Stage 0 — offline inspection (no launch, safe anytime)

```bash
.venv/bin/python -m app.openttd_demo check
.venv/bin/python -m app.openttd_demo plan
```

`check` validates binary/assets/desktop only (add `--headless` for
no-desktop checking). `plan` writes offline scenario selection/results.
A random-world plan is also offline:

```bash
.venv/bin/python -m app.openttd_demo plan --random-world --seed 17 \
  --map-size 256 --climate temperate --terrain 0 --towns 1 --industries 2 \
  --max-candidates 16 --max-services 4 --max-vehicles 4 --planning-seconds 30
```

This writes a generation recipe — not an observed world or selected plan.

### Stage 1 — authorization ceremony (operator-gated)

A native attempt goes through the staged ceremony of record: staging
(`PRELAUNCH` seal), independent `PREFLIGHT`, fresh independent review,
Gate C signing under the operator's pinned key, and a one-shot
`CLAIM.json` / `LAUNCH-CONSUMED.json` consumption chain
(`app/simulation/openttd/proof/operator_authorization.py:347-348`,
`proof/terrain_clearing.py:1376-1382`). A candidate whose claim already
exists can never mint a grant again. **This ceremony is the authorization
boundary; a customer demo inherits it — the operator, not the presenter,
grants the launch.**

### Stage 2 — the single native run

Stable fixed-demo command of record:

```bash
.venv/bin/python -m app.openttd_demo --view-seconds 300
```

What happens inside, per the standing pipeline: frozen code/config/assets,
effective settings and source-trust checks, bounded ports/time/requests, one
encrypted session (X25519/Monocypher), independent readback, receipt replay,
and full owned-process/credential/workspace cleanup. Failure stops without
retry or reconnect and retains partial evidence
([REPRODUCE.md](../REPRODUCE.md) §Native demo; `proof/native.py:275-276`
refuses a second launch). `--view-seconds` rides the existing total runtime
deadline.

The random-world run shape exists as a command reference only, **after**
fresh preparation, independent preflight and explicit one-shot authority —
and random-world *delivery* is currently UNPROVEN, so a random-world demo
would demonstrate generation and planning, not verified delivery.

### Stage 3 — offline reporting after an accepted run

```bash
.venv/bin/python -m app.openttd_demo report --source /absolute/path/to/completed-demo
.venv/bin/python -m app.openttd_demo compare --source /path/to/report-a \
  --compare-with /path/to/report-b
```

P07 reporting needs completed native receipts; comparisons across distinct
seeds/configurations are descriptive, not causal matched experiments.

## 4. Demo-day guidance (what to show, what to say)

| If the audience asks… | Show | Say |
| --- | --- | --- |
| "Does it actually deliver freight?" | The fixed-demo MVP (E1) and the multi-service attempts — from retained receipts or a fresh authorized fixed-demo run | Yes, for the verified scopes; corridor cargo delivery specifically is not yet proven |
| "Can it build roads/stations itself?" | Corridor construction receipts (E35) and census (E49) | PROVEN for the reviewed v3 scope; construction is not delivery |
| "Does it work on any map?" | Offline `plan --random-world` output | Generation and planning yes; observed-world delivery is unproven and the seed battery was honestly not met |
| "Is it profitable?" | Nothing — there is no profit figure | OPEX/ROI are UNKNOWN; revenue is never reported as profit (ADR-0001 D5); CAPEX figures are OBSERVED, margins DERIVED |
| "Can you just retry the run?" | — | No: one attempt, no retry, no reconnect — by design; FAILED outcomes stay FAILED |

**Never claim during a demo:** corridor DELIVERED receipts (none exist),
random-world delivery proof, rail delivery (NOT IMPLEMENTED), concurrency,
paid shared-asset reuse, closed-loop optimization, GUI product scope
(probes VERIFIED E170/E180; the owed product scope E148/E149 is unbuilt),
or any profit figure.

## 5. Failure behavior during a demo

If a native run fails mid-demo: it halts prefix-preserving, cleanup is
certified (reaped / sockets closed / workspace disposed / credential removed
— `proof/road_mutation.py:607-612`), partial evidence is retained verbatim,
and there is no automatic retry. The correct demo posture is to present the
retained verified evidence instead; a second native attempt requires a fresh
operator authorization and is not a demo recovery step.

## 6. Related documents

- Commands of record: [REPRODUCE.md](../REPRODUCE.md)
- Demo setup and spectator controls: [examples/openttd-demo/README.md](../examples/openttd-demo/README.md)
- Capability classification: [CUSTOMER_HANDOVER_GAP_ANALYSIS.md](CUSTOMER_HANDOVER_GAP_ANALYSIS.md)
- Use cases: [customer-use-cases.md](customer-use-cases.md)
