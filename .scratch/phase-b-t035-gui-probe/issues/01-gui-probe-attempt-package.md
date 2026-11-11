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
- Clean tree at the commit of record (≥ the fix commit `132e2ea`),
  branch
  `miles/fright-delivery`; `stash@{0}` untouched.
- `OPENTTD_BINARY` and `OPENTTD_OPENGFX_ARCHIVE` set before Python
  starts (exact values above).

## Commands of record (ONE server launch + ONE client join, no retry)

```bash
.venv/bin/python -m app.simulation.openttd.proof.canonical_fleet_gui prepare \
  artifacts/runtime/canonical-fleet-gui-probe-t035-2 \
  --canonical artifacts/runtime/canonical-fleet-create-q3
.venv/bin/python -m app.simulation.openttd.proof.canonical_fleet_gui preflight \
  artifacts/runtime/canonical-fleet-gui-probe-t035-2
.venv/bin/python -m app.simulation.openttd.proof.canonical_fleet_gui verify \
  artifacts/runtime/canonical-fleet-gui-probe-t035-2   # AUTHORIZATION_UNVERIFIED
.venv/bin/python -m app.simulation.openttd.proof.canonical_fleet_gui run \
  artifacts/runtime/canonical-fleet-gui-probe-t035-2 --authorize-one-launch
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
