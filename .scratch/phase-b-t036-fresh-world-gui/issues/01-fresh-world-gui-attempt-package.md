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

1. `fresh-world-create-t036-2` — ONE dedicated-server launch generates a
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

## Supersession record (2026-11-11, E172): t036-1 executed once under grant A — typed FAILED at the owned-cleanup seal seam after generation + save succeeded natively; fix landed (commit `6a2e893`); identity advanced to `fresh-world-create-t036-2`

Grant A (operator's explicit in-session "Grant A: authorize the one
launch" answer) was consumed by exactly one launch of
`fresh-world-create-t036-1`. Native outcome inside that launch: stderr
`Map generated, starting game`, stdout `Map successfully saved to
'…/fresh-world.sav'`, `world.json` `fresh_save_sha256`
`77b5431650e9c31d…` matching the save (10536 bytes) — the seed-1181
64×64 world WAS generated and saved. The attempt is nevertheless typed
terminal FAILED: the shared seal called the async `DemoBackend.cleanup`
without await, the owned reap never ran (the server pid 40019 stayed
alive until the operator-side owned SIGTERM, reaped rc 0), and
`cleanup.json`/`result.json`/manifest were never written. The t036-1
bytes are preserved untouched — no synthetic receipts were ever
substituted, nothing relabeled.

Fix of record (offline, zero native): `_seal_attempt` now awaits
`backend.cleanup(prepared)`; regression test
`test_seal_attempt_awaits_cleanup_and_writes_receipts` pins the full
failure-path receipt write; identity advanced to
`fresh-world-create-t036-2` (the t036-1 directory is unreachable from
the family by name). Grant A is consumed and void. The t036-2 staging
below is the attempt of record: prepare → **preflight PASS** → verify
`AUTHORIZATION_UNVERIFIED` as of 2026-11-11. **The creation re-RUN
awaits a FRESH explicit one-launch operator grant (grant A2).** Nothing
here re-launches.

## Attempt record (2026-11-11, E173): t036-2 executed once under the operator's explicit grant A2 — FRESH_WORLD_CREATE_VERIFIED, terminal

The t036-2 attempt ran exactly once under the operator's fresh explicit
in-session grant. `result.json`
`{status: FRESH_WORLD_CREATE_VERIFIED, launches: 1, connections: 0}`
rc 0. Native proof of record: stderr `Map generated, starting game`;
stdout `Map successfully saved to '…/fresh-world-create-t036-2/
fresh-world.sav'`; `world.json` pins seed 1181 / 64×64 / temperate /
1950 / heightmap digest and `fresh_save_sha256`
`8e7d0109012863ec931a9d20f4c492e1297a84d3b953ba90e0e8c767bc2a645e`
matching the save (10536 bytes). No admin connection ever made.
Cleanup certified all-true (pid 43421 `quit` → reaped rc 0, listener
closed, reservation released, workspace disposed, credential removed,
sockets closed); manifest 0 mismatches; post-run `verify` →
`FRESH_WORLD_CREATE_VERIFIED` rc 0 (after the `de42d10` CLI fix — the
first sweep crashed reopening the disposed workspace, a defect fixed
offline without touching the sealed bytes); `pgrep -x openttd` empty.
Dir sealed read-only.

**Grant A2 is consumed and void. The GUI stage is next, under its OWN
fresh grant (grant B)** — staging, preflight, run, and join all
operator-gated:

```
.venv/bin/python -m app.simulation.openttd.proof.fresh_world_gui gui \
  artifacts/runtime/fresh-world-gui-probe-t036-1 \
  --fresh-world artifacts/runtime/fresh-world-create-t036-2
.venv/bin/python -m app.simulation.openttd.proof.fresh_world_gui preflight \
  artifacts/runtime/fresh-world-gui-probe-t036-1
.venv/bin/python -m app.simulation.openttd.proof.fresh_world_gui run \
  artifacts/runtime/fresh-world-gui-probe-t036-1 --authorize-one-launch
.venv/bin/python -m app.simulation.openttd.proof.fresh_world_gui verify \
  artifacts/runtime/fresh-world-gui-probe-t036-1   # expect FRESH_WORLD_GUI_PROBE_VERIFIED
```

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
  artifacts/runtime/fresh-world-create-t036-2 --authorize-one-launch
.venv/bin/python -m app.simulation.openttd.proof.fresh_world_gui verify \
  artifacts/runtime/fresh-world-create-t036-2   # expect FRESH_WORLD_CREATE_VERIFIED
```

After stage 1 verifies VERIFIED, stage 2 stages under a FRESH explicit
grant (grant B), one launch + one AdminPort connection + one GUI join:

```
.venv/bin/python -m app.simulation.openttd.proof.fresh_world_gui gui \
  artifacts/runtime/fresh-world-gui-probe-t036-1 \
  --fresh-world artifacts/runtime/fresh-world-create-t036-2
.venv/bin/python -m app.simulation.openttd.proof.fresh_world_gui preflight \
  artifacts/runtime/fresh-world-gui-probe-t036-1
.venv/bin/python -m app.simulation.openttd.proof.fresh_world_gui run \
  artifacts/runtime/fresh-world-gui-probe-t036-1 --authorize-one-launch
.venv/bin/python -m app.simulation.openttd.proof.fresh_world_gui verify \
  artifacts/runtime/fresh-world-gui-probe-t036-1   # expect FRESH_WORLD_GUI_PROBE_VERIFIED
```

## Grant texts of record (paste per authorization, one per attempt)

Grant A (creation): "Authorize exactly one fresh-world creation launch:
`fresh_world_gui run artifacts/runtime/fresh-world-create-t036-2
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
