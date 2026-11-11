# 01: Fresh-world GUI probe attempt package (T-036)

**Type:** gate package
**Status:** re-staged 2026-11-11 (E174) — authorizes nothing by itself;
each stage requires the operator's separate fresh explicit authorization
**Spec:** `docs/specs/t036-fresh-world-gui-probe.md`
**Module of record:** `app/simulation/openttd/proof/fresh_world_gui.py`
(commit `9731d2b`); offline regression `tests/test_fresh_world_gui.py`
(18 tests, zero native processes, all green with the lane suites).

## Family shape

Two separately authorized attempts, strictly sequential:

1. `fresh-world-create-t036-3` — ONE dedicated-server launch generates a
   new OpenTTD 15.3 world from the seed and map parameters of record
   (`FRESH_SEED = 1181`, `map_x = map_y = 6` → 64×64, temperate, 1950,
   flat 64×64 heightmap; `-g heightmap.png -G 1181` over the proven
   `[game_creation]` config; native marker `Map generated, starting
   game`), then console-saves `fresh-world.sav` into the attempt
   directory where its SHA-256 is pinned in `world.json`. The generation
   workspace stages the byte-pinned bridge under `game/RoadFreightProof/`
   and carries `[game_scripts] RoadFreightProof = ` before
   `[game_creation]` (`bridge_sha256` pinned in `PRELAUNCH.json`), so
   the save embeds the GameScript in its GSDT. NO admin connection, no
   canonical input (preflight refuses canonical keys typed).
2. `fresh-world-gui-probe-t036-2` — the byte-pinned bridge host launches
   from the digest-pinned fresh save (`-g source.sav`, no `-G`); the
   save's GSDT names the GameScript, so the GUI stage stages the bridge
   package only and appends **nothing** to the config (OpenTTD 15.3
   `game_sl.cpp` wipes runtime GameScript config on save load); the
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

## Attempt record (2026-11-11, E174): first GUI attempt executed once under grant B — typed FAILED at the readiness gate; fix landed `9731d2b`; identities advanced

Grant B (operator's explicit in-session "Grant B — launch now" answer)
was consumed by exactly one launch of `fresh-world-gui-probe-t036-1`
from the E173-verified save. `result.json`
`{status: FAILED, launches: 1, connections: 0, error: "TimeoutError:
explicit native readiness marker missing: FREIGHT_DELIVERY_READY"}` rc 1;
`failure.sav` console-saved by the server; CLAIM consumed; zero admin
connections (the 45 s `wait_log` gate at `road_mutation.py:290` precedes
the connect). Retained stderr: zero `[script:` lines (31 grf + 21 net —
identical to the VERIFIED T-035 sequence up to the final GRFInfo pairs,
then nothing for the whole window). Seal of record: cleanup all-true
(reaped rc 0, listener closed, reservation released, workspace
disposed, credential removed, sockets closed); manifest 0 mismatches;
post-run `verify` → `ATTEMPT_NOT_VERIFIED: FAILED` rc 1. The t036-1
bytes are sealed untouched, never relabeled.

Root cause of record (read-only over the sealed bytes + OpenTTD 15.3
`src/saveload/game_sl.cpp`): the GSDT chunk stores the GameScript
selection inside the save; on load OpenTTD wipes runtime GameScript
config (`GameConfig::GetConfig(SSS_FORCE_GAME)->Change(std::nullopt)`)
and starts only what the save names — an empty name means the game runs
without a GameScript, silently. The E173 creation save was generated
WITHOUT `[game_scripts]`/bridge, so its GSDT is empty and the GUI
stage's config append was inert on a loaded save (a config section can
only seed a GameScript for a newly generated world). T-035 (E170) was
unaffected: the canonical demo save's GSDT names the GameScript staged
by the driver's proven CREATE staging (`canonical_fleet.py:129-146`).

Fix of record (commit `9731d2b`, offline, zero native): the creation
stage stages the byte-pinned bridge and carries
`[game_scripts] RoadFreightProof = ` before `[game_creation]`
(mirroring the proven canonical-CREATE staging), so the generated world
embeds the GameScript in its GSDT; `bridge_sha256` pinned in the
creation `PRELAUNCH.json`; the GUI stage drops the refuted append and
keeps only the package the saved GameScript name resolves against.
Tests updated: `tests/test_fresh_world_gui.py` 18 green (creation
staging asserts section + staged bridge + pin; GUI staging asserts
exactly one `[game_scripts]` section inherited from the creation
source, never re-appended); lane suites 46 green; ruff/format/
py_compile/scoped `uvx ty` clean. Identities advanced by
stale-supersession (E130/E167/E172 precedent):
`fresh-world-create-t036-2` → `fresh-world-create-t036-3` (the VERIFIED
save stays sealed history but can never host the probe — its world
carries no GameScript) and `fresh-world-gui-probe-t036-1` →
`fresh-world-gui-probe-t036-2`. Both superseded dirs stay sealed
terminal history, unreachable from the family by name.

**Grant B is consumed and void. The re-run is strictly sequential:
creation t036-3 under a FRESH grant A3 first; only after it verifies
VERIFIED does the GUI stage re-stage (`gui --fresh-world …/t036-3`),
preflight, and run under its OWN fresh grant B2.** The t036-3 staging
of record: prepare → **preflight PASS** → verify
`AUTHORIZATION_UNVERIFIED` as of 2026-11-11; staged config carries
`[game_scripts] RoadFreightProof = ` (lines 21-22), bridge staged,
`bridge_sha256` pinned, argv tail `-G 1181` unchanged, budget 300 s.

## Attempt record (2026-11-11, E175): t036-3 executed once under grant A3 — FRESH_WORLD_CREATE_VERIFIED, terminal; the fix is proven at the creation seam

The t036-3 attempt ran exactly once under the operator's fresh explicit
in-session grant A3 (HEAD `5726bc0`, tree clean, `pgrep -x openttd`
empty). `result.json`
`{status: FRESH_WORLD_CREATE_VERIFIED, launches: 1, connections: 0}`
rc 0. Native proof of record: stderr `Map generated, starting game` AND
the full GameScript boot the E174 run never had —
`FREIGHT_GAME_TIME_START`, six `FREIGHT_NETWORK_INDUSTRY_BUILT`
(industries 0-5), `FREIGHT_NETWORK_WORLD_READY cleared_bound=78`,
`BRIDGE_STARTED protocol=1 api=15`, `FREIGHT_DELIVERY_READY` (stderr
lines 61-70) — direct evidence the generated world's GSDT embeds the
GameScript. `world.json` pins seed 1181 / 64×64 / temperate / 1950 /
heightmap digest and `fresh_save_sha256`
`fddd6f5d28a578cc784aa25c330fd1141a5c5f73f5e2258aeebae9c3ea7c2b35`
matching the save; `PRELAUNCH.json` pins `bridge_sha256`
`0fa190a0b3770a28aff92b10c89c5c83d2ef267095f285d3f05e2921de6fc12e`. No
admin connection ever made. Cleanup certified all-true; manifest 0
mismatches; post-run `verify` → `FRESH_WORLD_CREATE_VERIFIED` rc 0;
`pgrep -x openttd` empty. Dir sealed read-only.

**Grant A3 is consumed and void. The GUI stage `fresh-world-gui-probe-
t036-2` is next, under its OWN fresh grant (grant B2)** — staging and
preflight are offline; the run is operator-gated:

```
.venv/bin/python -m app.simulation.openttd.proof.fresh_world_gui gui \
  artifacts/runtime/fresh-world-gui-probe-t036-2 \
  --fresh-world artifacts/runtime/fresh-world-create-t036-3
.venv/bin/python -m app.simulation.openttd.proof.fresh_world_gui preflight \
  artifacts/runtime/fresh-world-gui-probe-t036-2
.venv/bin/python -m app.simulation.openttd.proof.fresh_world_gui run \
  artifacts/runtime/fresh-world-gui-probe-t036-2 --authorize-one-launch
.venv/bin/python -m app.simulation.openttd.proof.fresh_world_gui verify \
  artifacts/runtime/fresh-world-gui-probe-t036-2   # expect FRESH_WORLD_GUI_PROBE_VERIFIED
```

## Attempt record (2026-11-11, E176): first post-fix GUI attempt executed once under grant B2 — typed FAILED; the bridge's reload contract refused the fleetless save; fix-design decision pending operator approval

Grant B2 (operator's explicit in-session "Grant B2 — launch now" answer)
was consumed by exactly one launch of `fresh-world-gui-probe-t036-2`
from the E175-verified save (HEAD `6231f08`, tree clean, preflight
PASS). `result.json`
`{status: FAILED, launches: 1, connections: 0, error: "RuntimeError:
Native script/asset error"}` rc 1; `failure.sav` console-saved (10888
bytes); CLAIM consumed; zero admin connections (the marker gate
precedes the connect). Retained stderr timeline (all 19:49:05): the
save's GSDT **boot the GameScript** (`FREIGHT_GAME_TIME_START
date=712223 tick=1` — the E174 fix proven at the load seam), then
`CanonicalFreightProof` → … → `PlannerFreightProof::Start`
(`network-parent.nut:8`) → `ContinuousFreightProof::PrepareDemo` →
`restored_fleet` false → `NetworkFreightProof.PrepareDemo` →
`throw "NETWORK_REQUIRES_EMPTY_WORLD"` (the world already carries the
6 industries built at generation) → "The script died unexpectedly." →
the server stayed alive the whole 45 s `wait_log` window → owned
shutdown. Seal of record: cleanup all-true; manifest 0 mismatches;
post-run `verify` → `ATTEMPT_NOT_VERIFIED: FAILED` rc 1; `pgrep -x
openttd` empty. The t036-2 bytes are sealed untouched, never relabeled.

Root cause of record (read-only over the sealed bytes + bridge sources
`freight_delivery_package/{continuous,network,planner,demo}.nut`): on
save load OpenTTD restarts the GameScript fresh and applies the save's
script state via `Load(version,data)`;
`ContinuousFreightProof::Save()` types a fleetless tick-1 save
`fleet_status="preconstruction"` and its `Load()` returns BEFORE
setting `restored_fleet` (the `constructed` branch — fleet restored,
funding completed — is the only path that sets it); `PrepareDemo()`
then runs the network build whose first check demands an empty world.
T-035's E2 source save (`canonical-fleet-create-q3`, E170) carries
`constructed` fleet + completed capital funding → restore path →
`PrepareDemo` skipped → `BRIDGE_STARTED`/`FREIGHT_DELIVERY_READY`. The
`restored_fleet` guard is the pinned bridge's ONLY reload-tolerance.
The E174 fix is proven at BOTH seams (GSDT embedded at generation,
script boots at load) — the remaining gap is the save's script-state
SHAPE, not GameScript injection.

**Grant B2 is consumed and void; grants A, A2, B, A3 are all consumed
and void. The E175-verified creation save `fresh-world-create-t036-3`
stays sealed terminal VERIFIED and untouched. Two honest fix shapes are
identified offline, BOTH awaiting operator approval before any code
moves — (a) reshape the creation stage to the proven `canonical_fleet.py`
CREATE machinery at seed 1181 (the script builds network + capital +
fleet via AdminPort; the save is taken at the `constructed` state the
reload path accepts; ~1200 s creation budget), or (b) keep the minimal
preconstruction creation (the E175 save stays the source of record) and
correct the GUI gate: welcome-tripwire-first (seed 1181/64×64 native
proof) + server-side join + GUI liveness, with the script-death lines
retained as the documented reload-contract limit of a fleetless save.**
Identities advance by stale-supersession when the operator picks.

## Attempt record (2026-11-11, E178): first gate-corrected GUI attempt executed once under grant B3 — typed FAILED; the connect raced the AdminPort listener bind; the approved shape completed with a native bind-line wait

Grant B3 (operator's explicit in-session "Grant B3 — launch now"
answer) was consumed by exactly one launch of
`fresh-world-gui-probe-t036-3` (HEAD `cc1ae2a`, tree clean, preflight
PASS). `result.json`
`{status: FAILED, launches: 1, connections: 0, error: "AuthDisconnected:
Admin connection failed", failure_save_error: "owned native save
completion missing"}` rc 1; CLAIM consumed; NO `failure.sav` (the
failure-path console save raced the startup console reader — its
absence is part of the record, never substituted). The server DID come
up and the E176 contract played out exactly as documented: game+admin
listeners bound (`127.0.0.1:58175`/`44797`), the save's GSDT booted the
GameScript (`FREIGHT_GAME_TIME_START`), the restarted script refused the
already-prepared world (`NETWORK_REQUIRES_EMPTY_WORLD`,
`network-parent.nut:8` → `continuous-parent.nut:39`) and died; 11
`[script:` lines retained; the server stayed alive until the owned
shutdown. Root cause of record: `connect_secure`'s
`asyncio.open_connection` converts ECONNREFUSED to an instant
`AuthDisconnected` (no retry) and `backend.launch` returns at process
spawn while the AdminPort listener binds ~1 s later — every prior lane
waited for a pre-connect marker and never raced; the gate correction
removed the wait without replacing it. Seal of record: cleanup
all-true; manifest 0 mismatches; post-run `verify` →
`ATTEMPT_NOT_VERIFIED: FAILED` rc 1; `pgrep -x openttd` empty. The
t036-3 bytes are sealed untouched, never relabeled.

Fix of record completing the approved shape (commit `7a5319b`, offline,
zero native): `run_gui` awaits the native bind marker
`Listening on 127.0.0.1:<admin_port> (IPv4)` (emitted by OpenTTD's
network core, independent of the GameScript) between launch and
connect; the welcome tripwire stays the world proof and the connection
gate; the failure-path console save now always lands after the console
reader is up. Tests 18 + lane suites 46 green (64 total); statics
clean. Identity advanced by stale-supersession:
`fresh-world-gui-probe-t036-3` → `fresh-world-gui-probe-t036-4` (the
t036-3 dir stays sealed terminal FAILED history, unreachable from the
family by name). The re-staged `fresh-world-gui-probe-t036-4`: prepare →
**preflight PASS** → verify `AUTHORIZATION_UNVERIFIED` as of
2026-11-11 (source t036-3, save digest `fddd6f5d…` == pin, bridge
`0fa190a0…` == pin, argv `-g source.sav`).

**Grant B3 is consumed and void; grants A, A2, B, A3, B2, B3 are all
consumed and void.**

## Attempt record (2026-11-11, E179): second gate-corrected GUI attempt executed once under grant B4 — the approved shape's proofs all landed (bind wait, connections 1, welcome tripwire PASSED) but the shared fatal-log scan fired on the documented death; fix landed `420574a`; identity advanced to `fresh-world-gui-probe-t036-5`

Grant B4 (operator's explicit in-session "Grant B4 — launch now"
answer) was consumed by exactly one launch of
`fresh-world-gui-probe-t036-4` (HEAD `c51e1a5`, tree clean, preflight
PASS). `result.json`
`{status: FAILED, launches: 1, connections: 1, error: "RuntimeError:
Native script/asset error"}` rc 1; `failure.sav` console-saved (10936
bytes — the E178 failure-path race fix proven); CLAIM consumed.
Timeline: the E178 bind wait held; the AdminPort connect +
authenticate SUCCEEDED (connections 1); the welcome tripwire PASSED
(`runtime-identity.json` sealed: revision `15.3`, seed `1181`,
width/height `64` — the world proof of record); the documented
contract played out (`NETWORK_REQUIRES_EMPTY_WORLD` + "The script died
unexpectedly."); the GUI client spawned (its `gui-client/` home
retained) — and the join-marker wait's `health()` polls hit the shared
fatal-log scan (`NativeBackend._check_logs` treats the death summary
as fatal) before any join marker could appear. Root cause: every prior
lane's scripts run to completion, so the shared scan never met a
documented expected death; the fresh lane's fleetless save dies BY
CONTRACT. Seal of record: cleanup all-true; manifest 0 mismatches;
post-run `verify` → `ATTEMPT_NOT_VERIFIED: FAILED` rc 1; `pgrep -x
openttd` empty. The t036-4 bytes are sealed untouched, never
relabeled.

Fix of record (commit `420574a`, offline, zero native): `native.py`
`_check_logs` split into `_check_logs` + `_scan_fatal`
(behavior-preserving refactor); `FreshWorldBackend._check_logs` strips
the death-summary lines ONLY when `NETWORK_REQUIRES_EMPTY_WORLD` is
present in the same logs, then delegates — any other fatal marker, or
any death without the expected throw, still raises; new test
`test_health_tolerates_only_the_documented_reload_death` pins all four
branches. Tests 19 + lane suites 46 green (65 total); statics clean.
Identity advanced by stale-supersession:
`fresh-world-gui-probe-t036-4` → `fresh-world-gui-probe-t036-5` (the
t036-4 dir stays sealed terminal FAILED history, unreachable from the
family by name). The re-staged `fresh-world-gui-probe-t036-5`: prepare
→ **preflight PASS** → verify `AUTHORIZATION_UNVERIFIED` as of
2026-11-11 (source t036-3, save digest `fddd6f5d…` == pin, bridge
`0fa190a0…` == pin, argv `-g source.sav`).

**Grant B4 is consumed and void; grants A, A2, B, A3, B2, B3, B4 are
all consumed and void.**

## Fix record (2026-11-11, E176 follow-up): operator approved the gate-correction shape — GUI gate is now welcome-tripwire-first; identity advanced to `fresh-world-gui-probe-t036-3`

The operator answered "Correct the GUI gate (Recommended)" in-session:
keep the minimal preconstruction creation (the E175-verified
`fresh-world-create-t036-3` save stays the source of record — no
creation re-run), and correct the GUI stage's gate. Fix of record
(commit `3eb8f5e`, offline, zero native): the run connects the
AdminPort **directly after launch** — the `wait_log` marker gate is
gone, because the pinned bridge's reload contract only resumes a
`constructed`-fleet save while this save is fleetless
`preconstruction` and its GameScript restarts, refuses the
already-prepared world (`NETWORK_REQUIRES_EMPTY_WORLD`) and dies before
any marker could appear; the native welcome tripwire
`require_fresh_welcome` (revision `15.3`, seed `1181`, 64×64 reported
by the loaded save itself) is the world proof and the connection gate;
the GameScript death lines are retained evidence of that documented
limit, never a failure to hide. Tests unchanged in count (18 green +
lane suites 46; the deletion is documented in the module docstring,
staging comment and inline gate comment). Identity advanced by
stale-supersession: `fresh-world-gui-probe-t036-2` →
`fresh-world-gui-probe-t036-3` (the t036-2 dir stays sealed terminal
FAILED history, unreachable from the family by name). The re-staged
`fresh-world-gui-probe-t036-3`: prepare → **preflight PASS** → verify
`AUTHORIZATION_UNVERIFIED` as of 2026-11-11 (source t036-3, save digest
`fddd6f5d…` == pin, bridge `0fa190a0…` == pin, argv `-g source.sav`).

**Grant B5 (GUI probe, only attempt of record now):** "Authorize
exactly one fresh-world GUI probe run: `fresh_world_gui run
artifacts/runtime/fresh-world-gui-probe-t036-5 --authorize-one-launch`.
One dedicated-server launch from the digest-pinned fresh save; the run
waits for the native AdminPort bind, connects and requires the welcome
frame to report revision 15.3, seed 1181 and 64×64 (the world proof),
and the fatal-log scan tolerates only the documented GameScript
restart-and-death; one real desktop GUI client join as spectator,
observation window, owned stop; no retry, no reconnect; stop on
unexpected failure."

## Grant texts of record (paste per authorization, one per attempt)

Grant A3 (creation) — CONSUMED 2026-11-11, void.

Grant B2 (GUI probe) — CONSUMED 2026-11-11, void.

Fresh grants will be requested per attempt after the operator picks the
fix shape; grant texts will be regenerated for the advancing identities.

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
