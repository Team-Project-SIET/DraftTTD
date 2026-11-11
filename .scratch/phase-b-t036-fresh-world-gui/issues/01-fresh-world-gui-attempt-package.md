# 01: Fresh-world GUI probe attempt package (T-036)

**Type:** gate package
**Status:** prepared 2026-11-11 — authorizes nothing by itself; each
stage requires the operator's separate fresh explicit authorization
**Spec:** `docs/specs/t036-fresh-world-gui-probe.md`
**Module of record:** `app/simulation/openttd/proof/fresh_world_gui.py`
(commit `68dbd36`); offline regression `tests/test_fresh_world_gui.py`
(15 tests, zero native processes, all green with the T-035 suites).

## Family shape

Two separately authorized attempts, strictly sequential:

1. `fresh-world-create-t036-1` — ONE dedicated-server launch generates a
   new OpenTTD 15.3 world from the seed and map parameters of record
   (`FRESH_SEED = 1181`, `map_x = map_y = 6` → 64×64, temperate, 1950,
   flat 64×64 heightmap; `-g heightmap.png -G 1181` over the proven
   `[game_creation]` config; native marker `Map generated, starting
   game`), then console-saves `fresh-world.sav` into the attempt
   directory where its SHA-256 is pinned in `world.json`. NO admin
   connection, no bridge staged, no canonical input (preflight refuses
   canonical keys typed).
2. `fresh-world-gui-probe-t036-1` — the byte-pinned bridge host launches
   from the digest-pinned fresh save (`-g source.sav`, no `-G`); the
   AdminPort welcome frame MUST report revision `15.3`, seed `1181`,
   64×64 (the demo lane's seed 42 refuses typed at
   `require_fresh_welcome`); then the real desktop GUI client
   (`Fresh World GUI Probe`) joins `127.0.0.1:<game-port>#255` as a
   spectator, join verified server-side only, observation window, owned
   stop. No virtual display, no headless fallback, no `-f` fork.

Both stages keep the T-035 guarantees: one-shot `CLAIM.json`
authorization, process ownership, AdminPort isolation (encrypted
session, per-attempt key material), evidence capture + manifest sealing,
owned cleanup, typed verify. T-035's sealed evidence
(`canonical-fleet-gui-probe-t035-3`, E170, terminal VERIFIED) is
untouched and unreachable from this family.

## Attempt record (2026-11-11, E171): creation stage staged at the fresh-grant gate

`artifacts/runtime/fresh-world-create-t036-1/` — prepare (offline, no
launch) → **preflight PASS** → verify `AUTHORIZATION_UNVERIFIED`.
Staged: isolated workspace with the admin auth trio (E169-proven
staging), `heightmap.png` = `flat_heightmap()` bytes (digest pinned in
`PRELAUNCH.json` `world_generation.heightmap_sha256`),
`effective-openttd.cfg` with `pause_on_newgame = false` + the world
sections of record and NO `[game_scripts]`, argv of record ending
`-G 1181`. Budget 300 s.

**The creation RUN awaits a FRESH explicit one-launch operator grant
(grant A).** It covers exactly one dedicated-server launch that
generates the world and console-saves it; NO admin connection. No
retry; stop on unexpected failure. Commands of record:

```
.venv/bin/python -m app.simulation.openttd.proof.fresh_world_gui run \
  artifacts/runtime/fresh-world-create-t036-1 --authorize-one-launch
.venv/bin/python -m app.simulation.openttd.proof.fresh_world_gui verify \
  artifacts/runtime/fresh-world-create-t036-1   # expect FRESH_WORLD_CREATE_VERIFIED
```

After stage 1 verifies VERIFIED, stage 2 stages under a FRESH explicit
grant (grant B), one launch + one AdminPort connection + one GUI join:

```
.venv/bin/python -m app.simulation.openttd.proof.fresh_world_gui gui \
  artifacts/runtime/fresh-world-gui-probe-t036-1 \
  --fresh-world artifacts/runtime/fresh-world-create-t036-1
.venv/bin/python -m app.simulation.openttd.proof.fresh_world_gui preflight \
  artifacts/runtime/fresh-world-gui-probe-t036-1
.venv/bin/python -m app.simulation.openttd.proof.fresh_world_gui run \
  artifacts/runtime/fresh-world-gui-probe-t036-1 --authorize-one-launch
.venv/bin/python -m app.simulation.openttd.proof.fresh_world_gui verify \
  artifacts/runtime/fresh-world-gui-probe-t036-1   # expect FRESH_WORLD_GUI_PROBE_VERIFIED
```

## Grant texts of record (paste per authorization, one per attempt)

Grant A (creation): "Authorize exactly one fresh-world creation launch:
`fresh_world_gui run artifacts/runtime/fresh-world-create-t036-1
--authorize-one-launch`. One dedicated-server launch that generates the
seed-1181 64×64 world and console-saves fresh-world.sav; no admin
connection; no retry; stop on unexpected failure."

Grant B (GUI probe): "Authorize exactly one fresh-world GUI probe run:
`fresh_world_gui run artifacts/runtime/fresh-world-gui-probe-t036-1
--authorize-one-launch`. One dedicated-server launch from the
digest-pinned fresh save, one AdminPort connection, one real desktop GUI
client join as spectator, observation window, owned stop; no retry, no
reconnect; stop on unexpected failure."

## Acceptance target

A newly generated 64×64 seed-1181 temperate world visibly running in the
actual OpenTTD 15.3 GUI on the operator's desktop — never the Sunningbury
demo lane — with `world.json`, `runtime-identity.json`, `gui-client.json`
and the retained logs recording generation parameters, save digest, host
identity, GUI client identity, and the server-side join marker.

## Failure discipline

Any FAILED attempt is terminal sealed history; its grant is consumed and
void. A re-attempt requires a NEW staging identity and a FRESH explicit
grant. Sealed T-035/T-036 evidence bytes are never modified or
relabeled.
