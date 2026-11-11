# T-036 — Fresh-world GUI native probe (T-035 follow-up)

Status: creation `fresh-world-create-t036-3` executed once under grant A3 and is terminal `FRESH_WORLD_CREATE_VERIFIED` (E175: the GameScript of record started natively during generation and the console save digest is pinned `fddd6f5d28a578cc…7c2b35`) — it stays the source of record. The first GUI attempt `fresh-world-gui-probe-t036-1` (grant B, E174) and the first post-fix GUI attempt `fresh-world-gui-probe-t036-2` (grant B2, E176) are both terminal typed FAILED; E176's root cause: the E174 GameScript staging is proven at the load seam (the save's GSDT boots the script), but the bridge's reload contract only resumes a `constructed`-fleet save, and the fresh creation save is `preconstruction`, so the restarted script's `PrepareDemo()` refuses the already-prepared world. The operator approved the gate-correction shape: the GUI stage now connects the AdminPort directly after launch and the native welcome tripwire (revision `15.3`, seed `1181`, 64×64 of the loaded save) is the world proof and the connection gate — no GameScript marker gate; the script-death lines are retained as documented evidence of the reload-contract limit of a fleetless save (commit `3eb8f5e`). The re-staged `fresh-world-gui-probe-t036-3` awaits its own fresh grant B3. T-035's sealed evidence (`canonical-fleet-gui-probe-t035-3`, E170) is terminal VERIFIED and untouched.

## Purpose

T-035 proved the desktop-GUI probe guarantees over the frozen demo-lane world (the E2 canonical save). The operator's acceptance target is a **newly generated world visibly running in the actual OpenTTD GUI, not the Sunningbury demo**. This family reuses the T-035 machinery end to end but swaps the world source: the hosted world is generated fresh at attempt time from an explicit seed and fixed map parameters, saved under a digest-pinned attempt identity, hosted by the dedicated server, and joined by the real desktop GUI client as a spectator.

## Family of record

Separately authorized attempts (two identities, two grants, one launch each), strictly sequential:

1. `fresh-world-create-t036-3` — schema `fresh-world-prelaunch-v1`, terminal status `FRESH_WORLD_CREATE_VERIFIED`. The creation launch now **stages the byte-pinned bridge and configures `[game_scripts] RoadFreightProof = ` at generation time** (the proven canonical-CREATE form), so the generated world embeds the GameScript in its save (GSDT); `bridge_sha256` is pinned in `PRELAUNCH.json`. Executed once under grant A3, terminal VERIFIED (E175: native `BRIDGE_STARTED`/`FREIGHT_DELIVERY_READY` during generation, save digest-pinned `fddd6f5d28a578cc…`, cleanup all-true, manifest 0 mismatches). Supersessions: `fresh-world-create-t036-2` executed once under grant A2, terminal VERIFIED (E173: seed-1181 save digest-pinned `8e7d0109012863ec…`) — **its world carries no GameScript** (the creation config of that identity deliberately omitted `[game_scripts]`), so it can never host the probe; `fresh-world-create-t036-1` executed once under grant A, E172 — typed FAILED at the seal seam after native generation + save; grant A consumed and void.
2. `fresh-world-gui-probe-t036-3` — schema `fresh-world-prelaunch-v1`, client receipt schema `fresh-world-gui-client-v1`, terminal status `FRESH_WORLD_GUI_PROBE_VERIFIED`. Loads the t036-3 save; the save's GSDT names the GameScript, so the GUI stage stages the bridge package only (the scanner resolves the saved name from `game/RoadFreightProof/`) and appends **nothing** to the config (OpenTTD 15.3 `game_sl.cpp` wipes runtime GameScript config on save load — `GameConfig::GetConfig(SSS_FORCE_GAME)->Change(std::nullopt)`). **The run connects the AdminPort directly after launch — there is NO GameScript marker gate**: the pinned bridge's reload contract only resumes a `constructed`-fleet save while the fresh save is fleetless `preconstruction`, so the GameScript restarts, refuses the already-prepared world (`NETWORK_REQUIRES_EMPTY_WORLD`) and dies; the welcome tripwire `require_fresh_welcome` (revision `15.3`, seed `1181`, 64×64 reported natively by the loaded save) is the world proof and the connection gate, and the script-death lines are retained evidence of that documented limit. Awaits its own fresh grant B3. Supersessions: `fresh-world-gui-probe-t036-2` executed once under grant B2, E176 — typed FAILED (`RuntimeError: Native script/asset error`, the script death above) at the old marker gate, server alive the whole window, sealed; `fresh-world-gui-probe-t036-1` executed once under grant B, E174 — typed FAILED at the 45 s `wait_log` readiness gate with a GameScript-less save; both grants consumed and void.

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

`pause_on_newgame = false` in the creation config: the world runs live after generation, so the console save captures a running world. The creation config now carries `[game_scripts] RoadFreightProof = ` **before `[game_creation]`** (placement and case mirror the proven canonical-CREATE staging) and the creation workspace stages the byte-pinned bridge under `game/RoadFreightProof/` — this is what writes the GameScript selection into the save's GSDT chunk. The GUI stage configures nothing: a loaded save's GameScript comes only from the save (OpenTTD 15.3 `src/saveload/game_sl.cpp` GSDT chunk); the GUI workspace still stages the bridge package so the scanner can resolve the saved name by its pinned bytes. Creation budget 300 s; GUI budget `freight.network_budgets(3)` with `total_seconds=1200`.

## Anti-fallback defense (no silent demo world)

- The creation stage has no canonical input structurally: no `canonical_directory`, no `canonical_save_sha256`, no `source.sav`; preflight refuses both canonical keys and re-checks the heightmap digest. The creation argv ends `-G 1181` and stages no `source.sav`; the GUI argv uses `-g source.sav` and carries no `-G`.
- The GUI stage's only permitted source is `verify_fresh_creation(...)` output: an immutable, manifest-sealed, `FRESH_WORLD_CREATE_VERIFIED` attempt whose `fresh-world.sav` digest still matches its `world.json` pin. Any other directory — including the canonical demo evidence — refuses typed: `fresh-world creation evidence required (never the canonical demo world)`.
- Preflight re-verifies the staged `source.sav` digest against the pin and re-checks that the staged save is a real file, not a symlink.
- Runtime no-fallback tripwire: `require_fresh_welcome` demands the AdminPort welcome frame report revision `15.3`, seed `1181`, width 64, height 64. The demo lane's seed 42 refuses typed (`fresh-world secure runtime identity mismatch`).

## Guarantees carried over from T-035 unchanged

One-shot authorization (`CLAIM.json` consumed before preflight, no retries, stop on unexpected failure); process ownership (`validate_launch` seals argv, binary SHA-256, no matching processes); AdminPort isolation (encrypted `PlannerDeliverySession`, own key material per attempt, allowlist never widened); server-side-only join verification; owned exit/terminate of the GUI client before server cleanup; log capture; `cleanup.json` + `result.json` + `artifact-manifest.sha256` sealing; typed `verify` states via the shared `exercise.verify`.

## Procedure of record (nothing below authorizes a launch)

```
# stage 1 — creation (offline staging; NO launch in this round)
.venv/bin/python -m app.simulation.openttd.proof.fresh_world_gui create artifacts/runtime/fresh-world-create-t036-3
# preflight
.venv/bin/python -m app.simulation.openttd.proof.fresh_world_gui preflight artifacts/runtime/fresh-world-create-t036-3
# run — REQUIRES a fresh explicit operator grant, one launch, no retry
.venv/bin/python -m app.simulation.openttd.proof.fresh_world_gui run artifacts/runtime/fresh-world-create-t036-3 --authorize-one-launch
# verify
.venv/bin/python -m app.simulation.openttd.proof.fresh_world_gui verify artifacts/runtime/fresh-world-create-t036-3

# stage 2 — GUI probe (only after stage 1 verifies VERIFIED)
.venv/bin/python -m app.simulation.openttd.proof.fresh_world_gui gui artifacts/runtime/fresh-world-gui-probe-t036-3 --fresh-world artifacts/runtime/fresh-world-create-t036-3
.venv/bin/python -m app.simulation.openttd.proof.fresh_world_gui preflight artifacts/runtime/fresh-world-gui-probe-t036-3
.venv/bin/python -m app.simulation.openttd.proof.fresh_world_gui run artifacts/runtime/fresh-world-gui-probe-t036-3 --authorize-one-launch
.venv/bin/python -m app.simulation.openttd.proof.fresh_world_gui verify artifacts/runtime/fresh-world-gui-probe-t036-3
```

## Evidence expectations

Creation attempt: `world.json` (generation parameters, argv, save name + SHA-256), native generation marker in retained `stderr.log`, **the GameScript ready marker family in retained `stderr.log`** (`dbg: [script:4] [N] [I] BRIDGE_STARTED` / `FREIGHT_DELIVERY_READY` — the GSDT of the console save embeds the GameScript), one launch, **zero** admin connections, all-true cleanup, sealed manifest.

GUI attempt: `runtime-identity.json` (welcome frame = seed 1181 world of the loaded save — the welcome tripwire is the world proof and the connection gate; there is NO GameScript marker gate, and the retained stderr documents the GameScript restart-and-death `NETWORK_REQUIRES_EMPTY_WORLD` as the pinned bridge's reload-contract limit for a fleetless `preconstruction` save), `gui-client.json` (client receipt: argv, client name `Fresh World GUI Probe`, join marker `*** Fresh World GUI Probe has joined the game`, server-side `join_verified`, observation end, owned stop), one launch, one connection, one join, all-true cleanup, sealed manifest.

Offline regression: `tests/test_fresh_world_gui.py` (18 tests, zero native processes) — identity independence, canonical refusals, drift/failed-creation refusals, offline staging of both attempts (creation now stages the bridge + `[game_scripts]`; the GUI config inherits exactly one section from the creation source and never re-appends), preflight passes, authorization gates, welcome tripwire, verify states, fresh client spawn/receipt identity, conduct wiring.

## Grant discipline

Each attempt consumes its OWN fresh explicit grant (never inherited, never batched): the creation grant covers exactly one dedicated-server launch with no admin connection; the GUI grant covers exactly one dedicated-server launch, one AdminPort connection, and one GUI client join. A failed attempt is terminal FAILED evidence; the fix path is a new identity and a new grant, never a relabel.
