# 01: GUI native probe attempt package (T-035)

**Type:** gate package
**Status:** prepared 2026-11-11 — authorizes nothing by itself; the
launch requires the operator's separate fresh explicit authorization
**Spec:** `docs/specs/t035-gui-native-probe.md`

## Supersession record (2026-11-11, E167)

The first staging under identity `canonical-fleet-gui-probe-t035-1`
refused typed at preflight before any grant (`ValueError: canonical
save must be an existing protected regular file`); root cause and fix
of record in the spec's Supersession section (commit `132e2ea`). The
refused staging bytes stay preserved untouched at
`artifacts/runtime/canonical-fleet-gui-probe-t035-1/` (sealed,
pre-consumption, no CLAIM). The attempt of record is the t035-2
staging below — prepare → **preflight PASS** → verify
`AUTHORIZATION_UNVERIFIED` as of 2026-11-11.

## Attempt record (2026-11-11, E168): t035-2 executed once under the operator's explicit one-launch grant — typed FAILED, sealed

The t035-2 attempt ran exactly once. `result.json`
`{status: FAILED, launches: 1, connections: 0, error: "AuthDisconnected:
Admin connection failed"}`: the server's admin listener never started
(see below), the conductor's `connect_secure` refused, and the failure
preceded all correspondence and the client stage — **no window ever
appeared** (the GUI outcome is NOT REACHED; this is not a GUI defect).
The failure path ran as designed: `failure.sav`, owned cleanup (all-true),
manifest 0 mismatches, `verify` → `ATTEMPT_NOT_VERIFIED: FAILED`; the
dir is sealed read-only.

Root cause (read-only diagnosis): the exercise-core `stage_workspace`
writes only `openttd.cfg`; every working stage calls
`RuntimeWorkspace.write_config(AdminSettings(...))` to also produce
`private.cfg` (`[admin_authorized_keys] <public_hex>`) and
`secrets.cfg` (`admin_password`) — with `allow_insecure_admin_login =
false` and no auth material, OpenTTD 15.3 does not start the admin
network. Second latent exercise-core blocker of the E167 class,
unreachable offline.

**Status: the t035-2 identity is consumed terminal history and the
one-launch grant is consumed and void.** A re-attempt requires a NEW
staging identity (`canonical-fleet-gui-probe-t035-3`) under the fix of
record (mirror `write_config` into `stage_workspace`, regression test
pinning the staged auth trio) AND a FRESH explicit one-launch operator
grant. Nothing here re-launches.

## Second supersession (2026-11-11, E169): fix landed (commit `0a95c75`), t035-3 staged at the fresh-grant gate

Under the operator's in-session "Fix + re-stage" answer: `stage_workspace`
now mirrors the driver's `write_config` (private.cfg
`[admin_authorized_keys]` + secrets.cfg `admin_password`, exactly the
proven staging shape); identity advanced to
`canonical-fleet-gui-probe-t035-3` (stale-supersession); the t035-3
staging is at
`artifacts/runtime/canonical-fleet-gui-probe-t035-3/` — prepare →
**preflight PASS** → verify `AUTHORIZATION_UNVERIFIED`, staged
`source.sav` == protected pin `51e45689…1297eb`, auth trio present
(pinned by `test_stage_writes_admin_auth_trio`). **The t035-3 re-RUN
awaits a FRESH explicit one-launch operator grant** — the commands of
record above now point at the t035-3 directory.

## Attempt record (2026-11-11, E170): t035-3 executed once under a fresh explicit operator grant — CANONICAL_FLEET_GUI_PROBE_VERIFIED, terminal

The t035-3 attempt ran exactly once under the operator's fresh explicit
one-launch grant. `result.json`
`{status: CANONICAL_FLEET_GUI_PROBE_VERIFIED, launches: 1,
connections: 1, mutations: 0, gui_client: OBSERVATION_WINDOW_ELAPSED}`,
rc 0: the server (window 15:18:57 → 15:29:38) bound the game listener
`:49457` AND the admin listener `:33873`, authenticated the admin
client `Canonical-exercise` (the E168 blocker closed natively), ran
the establishment/reload correspondence, and loaded the source save
(protected pin). The GUI client joined as a spectator with the
byte-for-byte argv (`-n 127.0.0.1:49457#255`, `client_name "Canonical
GUI Probe"`) under the real desktop display env (`DISPLAY=:0`/
`WAYLAND_DISPLAY=wayland-1`/`XDG_SESSION_TYPE=wayland`); join verified
SERVER-side (marker line 8 `*** Canonical GUI Probe has joined the
game (Client #2)`); alive the full 600 s observation window, ended by
the probe's owned terminate (`code: -9, owned_terminate: true`); the
server then saw `…has left the game (connection lost)` and saved
`reload-readback.sav`. `client.log` stayed 0 bytes (GUI mode; join
verification is SERVER-side by design).

**Honesty boundary:** machine-verified facts only; the agent does not
claim to have seen the window.

**Seal:** `cleanup.json` all-true (pid 28460 quit → reaped rc 0);
manifest 0 mismatches; post-run `verify` →
`CANONICAL_FLEET_GUI_PROBE_VERIFIED` rc 0; `pgrep -x openttd` empty;
dir sealed read-only.

**Status: T-035 is typed terminal VERIFIED at
`canonical-fleet-gui-probe-t035-3`; both one-launch grants (t035-2,
t035-3) are consumed and void.** Any further T-035 run needs a NEW
staging identity AND a FRESH explicit one-launch grant. The probe
satisfies none of the Phase B done-ness criteria (verdict section
below); a roadmap §3 T-035 row is an operator decision.

## Preconditions (all offline-checkable, verified 2026-11-11)

- Run from a desktop terminal on the operator's session (verified live:
  `DISPLAY=:0`, `WAYLAND_DISPLAY=wayland-1`, `XDG_SESSION_TYPE=wayland`,
  XWayland `:0` via `kwin_wayland_wrapper --xwayland`, `/tmp/.X11-unix/X0`
  present). The stage refuses typed without a desktop session — it
  never falls back to headless or a virtual display.
- Binary pin `276d5b698a6b706154f3af588f6f885b3aebe518f4ecc8f869abf71383b1904c`;
  OpenGFX pin
  `43a0c1dabf39cb865394f3a6cc36d4da5c10ecfaaf55652043104806810903be`
  (`artifacts/runtime/verified-assets/opengfx-8.0-all.zip`).
- `pgrep -x openttd` empty before the run (no server, no user client).
- E2 manifest re-verified inside
  `artifacts/runtime/canonical-fleet-create-q3/` (0 mismatches, part of
  the E165 197-manifest sweep); no byte modified by the check.
- Clean tree at the commit of record (≥ the fix commit `0a95c75`),
  branch
  `miles/fright-delivery`; `stash@{0}` untouched.
- `OPENTTD_BINARY` and `OPENTTD_OPENGFX_ARCHIVE` set before Python
  starts (exact values above).

## Commands of record (ONE server launch + ONE client join, no retry)

```bash
.venv/bin/python -m app.simulation.openttd.proof.canonical_fleet_gui prepare \
  artifacts/runtime/canonical-fleet-gui-probe-t035-3 \
  --canonical artifacts/runtime/canonical-fleet-create-q3
.venv/bin/python -m app.simulation.openttd.proof.canonical_fleet_gui preflight \
  artifacts/runtime/canonical-fleet-gui-probe-t035-3
.venv/bin/python -m app.simulation.openttd.proof.canonical_fleet_gui verify \
  artifacts/runtime/canonical-fleet-gui-probe-t035-3   # AUTHORIZATION_UNVERIFIED
.venv/bin/python -m app.simulation.openttd.proof.canonical_fleet_gui run \
  artifacts/runtime/canonical-fleet-gui-probe-t035-3 --authorize-one-launch
```

Then the window appears. The operator may watch it and close it at any
time — closing it is the designed typed soft end and the stage then
finalizes (owned cleanup reaps the server and seals the receipts).
Otherwise the probe ends itself after the 600 s observation window.

## Grant text style (of record)

One execution only; no retry, no relaunch, no reconnect; no seed, world
or scope change; stop on unexpected failure and retain the receipts;
failure is never retried or relabeled; receipts retained whatever the
outcome. This authorization is NOT shared with the T-030 exercise, the
T-031 arms, the T-032 five-year attempt, the FD-C-2 line, or any
earlier attempt (all prior grants void).

## Expected receipts (T-035)

- `result.json` typed `CANONICAL_FLEET_GUI_PROBE_VERIFIED`, with
  `gui_client` = `OPERATOR_CLOSED_WINDOW` or
  `OBSERVATION_WINDOW_ELAPSED`.
- Reload-only correspondence receipts (`reload-observation.json`,
  `reload-correspondence.json`) — paused, nothing purchased, nothing
  dispatched, nothing unpaused.
- `gui-client.json` (schema `canonical-fleet-gui-client-v1`): client
  argv (no `-D`, no `-f`), display env, join marker
  `*** Canonical GUI Probe has joined the game` with
  `join_verified: true`, observation end + alive seconds, owned-stop
  record, client.log sha256.
- Server `stdout.log`/`stderr.log` copied into the stage with the join
  lines of record (manifest-covered).
- `cleanup.json` certified with `client_terminated_before_server_cleanup`
  inside the client receipt; manifest 0 mismatches → then the E-row.

## Failure conditions (typed, never relabeled)

- No desktop session → typed refusal at prepare/preflight, before any
  write; no fallback ever attempted.
- Client spawn failure or nonzero exit → typed failure, stop.
- Join marker missing within 60 s → typed `TimeoutError`, stop.
- Server death mid-observation → typed failure via health, stop.
- Unexpected failure → standard failure path: failure save, owned
  cleanup (client terminated first), receipts retained, nothing
  relabeled, attempt dir read-only hereafter.

## Verdict on Phase B acceptance criteria (of record)

This probe satisfies NONE of T-030/T-031/T-032's done-ness criteria and
must NOT be assumed to replace any of them (see the spec's independence
verdict). It is its own ticket with its own grant. A window on a Phase B
attempt itself would be a NEW reviewed package decision per attempt,
never this probe.
