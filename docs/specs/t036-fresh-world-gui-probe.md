# T-036 — Fresh-world GUI native probe (T-035 follow-up)

Status: BUILT OFFLINE (E171). No native run has happened; both attempts await their own fresh explicit grant. T-035's sealed evidence (`canonical-fleet-gui-probe-t035-3`, E170) is terminal VERIFIED and untouched.

## Purpose

T-035 proved the desktop-GUI probe guarantees over the frozen demo-lane world (the E2 canonical save). The operator's acceptance target is a **newly generated world visibly running in the actual OpenTTD GUI, not the Sunningbury demo**. This family reuses the T-035 machinery end to end but swaps the world source: the hosted world is generated fresh at attempt time from an explicit seed and fixed map parameters, saved under a digest-pinned attempt identity, hosted by the dedicated server, and joined by the real desktop GUI client as a spectator.

## Family of record

Two **separately authorized** attempts (two identities, two grants, one launch each):

1. `fresh-world-create-t036-1` — schema `fresh-world-prelaunch-v1`, terminal status `FRESH_WORLD_CREATE_VERIFIED`.
2. `fresh-world-gui-probe-t036-1` — schema `fresh-world-prelaunch-v1`, client receipt schema `fresh-world-gui-client-v1`, terminal status `FRESH_WORLD_GUI_PROBE_VERIFIED`.

Genealogy is strictly sequential: the GUI stage refuses any source that is not the verified fresh creation attempt. Neither stage ever consumes Phase B ticket receipts; both are their own tickets.

## World of record

Module constants (NOT CLI flags — a change is a source change and therefore a new staging identity):

| Parameter | Value |
| --- | --- |
| Seed | `FRESH_SEED = 1181` (≠ demo 42) |
| Map size | `map_x = map_y = 6` → 64×64 |
| Landscape / year | temperate / 1950 |
| Heightmap | flat 64×64 grayscale-1 (`freight.flat_heightmap()`) |
| Generation argv shape | `-g <workspace>/heightmap.png -G 1181` over the proven `[game_creation]` config sections |
| Generation proof | native stderr marker `Map generated, starting game` (proven on q3 CREATE) |
| Capture | owned console save `fresh-world.sav` into the attempt directory, digest pinned in `world.json` |

`pause_on_newgame = false` in the creation config: the world runs live after generation, so the console save captures a running world that the GUI stage loads unpaused. Creation config omits `[game_scripts]` (no bridge staged); the GUI stage appends `RoadFreightProof = ` (the proven `FREIGHT_DELIVERY_READY` marker). Creation budget 300 s; GUI budget `freight.network_budgets(3)` with `total_seconds=1200`.

## Anti-fallback defense (no silent demo world)

- The creation stage has no canonical input structurally: no `canonical_directory`, no `canonical_save_sha256`, no `source.sav`; preflight refuses both canonical keys and re-checks the heightmap digest.
- The GUI stage's only permitted source is `verify_fresh_creation(...)` output: an immutable, manifest-sealed, `FRESH_WORLD_CREATE_VERIFIED` attempt whose `fresh-world.sav` digest still matches its `world.json` pin. Any other directory — including the canonical demo evidence — refuses typed: `fresh-world creation evidence required (never the canonical demo world)`.
- Preflight re-verifies the staged `source.sav` digest against the pin and re-checks that the staged save is a real file, not a symlink.
- Runtime no-fallback tripwire: `require_fresh_welcome` demands the AdminPort welcome frame report revision `15.3`, seed `1181`, width 64, height 64. The demo lane's seed 42 refuses typed (`fresh-world secure runtime identity mismatch`).
- Test assertions pin argv shape: creation argv ends `-G 1181` and stages no `source.sav`; GUI argv uses `-g source.sav` and carries no `-G`.

## Guarantees carried over from T-035 unchanged

One-shot authorization (`CLAIM.json` consumed before preflight, no retries, stop on unexpected failure); process ownership (`validate_launch` seals argv, binary SHA-256, no matching processes); AdminPort isolation (encrypted `PlannerDeliverySession`, own key material per attempt, allowlist never widened); server-side-only join verification; owned exit/terminate of the GUI client before server cleanup; log capture; `cleanup.json` + `result.json` + `artifact-manifest.sha256` sealing; typed `verify` states via the shared `exercise.verify`.

## Procedure of record (nothing below authorizes a launch)

```
# stage 1 — creation (offline staging; NO launch in this round)
.venv/bin/python -m app.simulation.openttd.proof.fresh_world_gui create artifacts/runtime/fresh-world-create-t036-1
# preflight
.venv/bin/python -m app.simulation.openttd.proof.fresh_world_gui preflight artifacts/runtime/fresh-world-create-t036-1
# run — REQUIRES a fresh explicit operator grant, one launch, no retry
.venv/bin/python -m app.simulation.openttd.proof.fresh_world_gui run artifacts/runtime/fresh-world-create-t036-1 --authorize-one-launch
# verify
.venv/bin/python -m app.simulation.openttd.proof.fresh_world_gui verify artifacts/runtime/fresh-world-create-t036-1

# stage 2 — GUI probe (only after stage 1 verifies VERIFIED)
.venv/bin/python -m app.simulation.openttd.proof.fresh_world_gui gui artifacts/runtime/fresh-world-gui-probe-t036-1 --fresh-world artifacts/runtime/fresh-world-create-t036-1
.venv/bin/python -m app.simulation.openttd.proof.fresh_world_gui preflight artifacts/runtime/fresh-world-gui-probe-t036-1
.venv/bin/python -m app.simulation.openttd.proof.fresh_world_gui run artifacts/runtime/fresh-world-gui-probe-t036-1 --authorize-one-launch
.venv/bin/python -m app.simulation.openttd.proof.fresh_world_gui verify artifacts/runtime/fresh-world-gui-probe-t036-1
```

## Evidence expectations

Creation attempt: `world.json` (generation parameters, argv, save name + SHA-256), native generation marker in retained `stderr.log`, one launch, **zero** admin connections, all-true cleanup, sealed manifest.

GUI attempt: `runtime-identity.json` (welcome frame = seed 1181 world), `gui-client.json` (client receipt: argv, client name `Fresh World GUI Probe`, join marker `*** Fresh World GUI Probe has joined the game`, server-side `join_verified`, observation end, owned stop), one launch, one connection, one join, all-true cleanup, sealed manifest.

Offline regression: `tests/test_fresh_world_gui.py` (15 tests, zero native processes) — identity independence, canonical refusals, drift/failed-creation refusals, offline staging of both attempts, preflight passes, authorization gates, welcome tripwire, verify states, fresh client spawn/receipt identity, conduct wiring.

## Grant discipline

Each attempt consumes its OWN fresh explicit grant (never inherited, never batched): the creation grant covers exactly one dedicated-server launch with no admin connection; the GUI grant covers exactly one dedicated-server launch, one AdminPort connection, and one GUI client join. A failed attempt is terminal FAILED evidence; the fix path is a new identity and a new grant, never a relabel.
