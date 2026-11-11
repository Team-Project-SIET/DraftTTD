# T-035 — GUI native probe (Phase B-adjacent, independent; operator-placed)

Goal: prove a real, visible, usable OpenTTD 15.3 desktop window on the
operator's own desktop session against the canonical-fleet lane, WITHOUT
substituting a virtual display, falling back headless, or forking into
the background, and WITHOUT touching the AdminPort wire, the one-shot
authorization machinery, runtime isolation, evidence capture, cleanup or
verification guarantees.

**Placement of record:** this is a NEW independent ticket. It is NOT
T-030, T-031, T-032 or T-034 and produces NONE of their receipts; adding
a T-035 row to `docs/roadmap-and-scope-2026-11-05.md` §3 is an operator
decision (the roadmap of record is not edited by this spec).

## CLI-surface facts of record (OpenTTD 15.3)

- `-D [ip:port]` starts a **dedicated** (windowless) server. Every
  consumed native attempt in this repo's history launched exactly this
  way (`harness.launch_argv`: `-D127.0.0.1:<port>`); the sealed evidence
  lane binds to it.
- There is NO command-line flag that hosts a network server from a
  visible GUI instance: hosting from the GUI requires the Multiplayer
  dialog (human clicks), which cannot carry a sealed conductor's
  staging/correspondence contract. The wiki CLI page (retrieved
  2026-11-11) lists only `-D` for hosting.
- `-n [ip:port#company]` starts a GUI client joining an existing server
  (`#255` = spectator). This is the demo lane's proven GUI client argv
  (`app/openttd_demo.py` Viewer: `[BINARY, -c cfg, -x, -X, -n
  127.0.0.1:<game-port>#255]`), typed-exit-classified since the demo
  attempts (`OperatorWindowClosed`, client-exit-0 soft end).

**Consequence of record:** a visible window against the canonical lane
is a SECOND real OpenTTD process — a GUI client joining the dedicated
host's world live. The host stays exactly the proven dedicated instance;
the client is the new surface. This is not a headless fallback: the
probe's purpose is the window, it refuses typed without a desktop
session, and the game window is genuinely visible and usable on the
operator's desktop (KDE Wayland + XWayland `:0` verified live
2026-11-11: `DISPLAY=:0`, `WAYLAND_DISPLAY=wayland-1`,
`/tmp/.X11-unix/X0` present, `kwin_wayland` running).

## Design of record

- **Identity of record:** `canonical-fleet-gui-probe-t035-1`; own CLAIM;
  own fresh explicit one-launch grant (never shared with the T-030
  exercise, the T-031 arms, the T-032 five-year stage, the FD-C-2 line,
  or any earlier attempt; all prior grants void).
- **Same start state, same bridge:** stages from the SAME E2 created
  evidence under the SAME byte-pinned bridge package; budgets
  `network_budgets(3) | total_seconds 1200` (join ≤ 60 s + observation
  600 s inside).
- **Native surface, minimal and proven:** reload-only correspondence
  (the q3 no-purchase contract: paused, nothing purchased, nothing
  dispatched, nothing unpaused) via `exercise.conduct_exercise(…,
  dispatch=False)` — a new `dispatch=False` seam in the generalized
  stage core (default behavior unchanged).
- **The new element — the window:** a second real OpenTTD 15.3 desktop
  client (`gui-client/` inside the stage dir; isolated config, OpenGFX
  baseset copied from the stage workspace, `client_name = Canonical GUI
  Probe`), spawned with the demo lane's argv byte-for-byte. NO `-f`,
  NO `-D` (typed asserts in code and tests). The process inherits the
  operator's real desktop environment (no DISPLAY manipulation, no
  Xvfb).
- **Join verification (machine, server-side):** the client's own log
  stays empty in GUI mode (every retained demo `client.log` is 0
  bytes), so the join of record comes from the SERVER's own stdout:
  `*** Canonical GUI Probe has joined the game (Client #N)` — the exact
  marker family retained demo logs show (`*** Python Demo Viewer has
  joined the game (Client #2)`). Deadline 60 s, typed
  `TimeoutError: server-side GUI client join marker missing: …`. The
  AdminPort allowlist is NOT widened for this (the observer's outbound
  allowlist stays JOIN/QUIT/UPDATE_FREQUENCY/POLL/PING over
  DATE/COMPANY_INFO/COMPANY_ECONOMY/COMPANY_STATS).
- **Observation window:** 600 s of typed liveness (client `poll()` +
  server `backend.health()`), ending typed: `OPERATOR_CLOSED_WINDOW`
  (client exit 0 — the demo lane's soft ended-by-operator end) or
  `OBSERVATION_WINDOW_ELAPSED` (probe terminates the client it owns,
  never a user's). Client exit != 0 or server death = typed failure,
  stop, receipts retained, no retry.
- **Honesty boundary of record:** the probe records machine-verified
  facts only (process, argv, display env, server-side join marker,
  liveness seconds, owned exit, client.log sha256). The agent never
  claims it SAW the window; visual confirmation is the operator's
  optional post-run note. `gui-client.json` schema
  `canonical-fleet-gui-client-v1`; the stage's standard
  `artifact-manifest.sha256` covers it.
- **Cleanup guarantee:** the client is terminated (and its exit
  recorded as `client_terminated_before_server_cleanup`) BEFORE the
  stage's standard cleanup seal reaps the server, so the proven
  `cleanup.json`/manifest/verify machinery runs byte-untouched.
- **Result of record:** typed `CANONICAL_FLEET_GUI_PROBE_VERIFIED`.

## Launch procedure of record (attempt day, after the fresh grant)

```bash
export OPENTTD_BINARY=/home/fed/Downloads/openttd-15.3-linux-generic-amd64/openttd
export OPENTTD_OPENGFX_ARCHIVE=artifacts/runtime/verified-assets/opengfx-8.0-all.zip
.venv/bin/python -m app.simulation.openttd.proof.canonical_fleet_gui prepare \
  artifacts/runtime/canonical-fleet-gui-probe-t035-1 \
  --canonical artifacts/runtime/canonical-fleet-create-q3
.venv/bin/python -m app.simulation.openttd.proof.canonical_fleet_gui preflight \
  artifacts/runtime/canonical-fleet-gui-probe-t035-1
.venv/bin/python -m app.simulation.openttd.proof.canonical_fleet_gui verify \
  artifacts/runtime/canonical-fleet-gui-probe-t035-1   # AUTHORIZATION_UNVERIFIED
.venv/bin/python -m app.simulation.openttd.proof.canonical_fleet_gui run \
  artifacts/runtime/canonical-fleet-gui-probe-t035-1 --authorize-one-launch
.venv/bin/python -m app.simulation.openttd.proof.canonical_fleet_gui verify \
  artifacts/runtime/canonical-fleet-gui-probe-t035-1   # typed post-run status
```

Run from a desktop terminal (DISPLAY or WAYLAND_DISPLAY must be set —
the stage refuses typed otherwise). The operator may close the window at
any time; that is the designed soft end and the probe then finalizes.

## Prerequisites (offline-checkable)

- Desktop session alive with a real display (not SSH): `DISPLAY` or
  `WAYLAND_DISPLAY` set; XWayland running for `:0` (verified live:
  `pgrep -a Xorg` shows `kwin_wayland_wrapper --xwayland`).
- Binary pin `276d5b698a6b706154f3af588f6f885b3aebe518f4ecc8f869abf71383b1904c`;
  OpenGFX pin
  `43a0c1dabf39cb865394f3a6cc36d4da5c10ecfaaf55652043104806810903be`.
- `pgrep -x openttd` empty before the run (no server, no user client).
- E2 manifest re-verified inside
  `artifacts/runtime/canonical-fleet-create-q3/` (0 mismatches; part of
  the 197-manifest E165 sweep); no byte modified by the check.
- Clean tree, branch `miles/fright-delivery`; `stash@{0}` untouched.

## Expected GUI behavior

1. After the reload correspondence completes, a normal desktop window
   titled with the client's title bar appears via XWayland on the
   operator's desktop, showing the paused canonical world (seed 42,
   64×64, three original services parked at their stations) from the
   spectator seat.
2. The spectator can scroll/zoom/inspect freely (usable); joining a
   company would be an operator action OUTSIDE the probe's contract and
   is not required (the world stays paused; the probe claims nothing
   about operator interaction).
3. The server's stdout logs the join marker; the probe's receipt pins
   it. Note: a joining client pauses the server by default
   (`pause_on_join`) — the canonical world is already paused by
   contract, so nothing changes.
4. Closing the window ends the probe softly and the stage finalizes
   (server reaped by the standard owned cleanup).

## Evidence collected of record

- Reload-only correspondence receipts (`reload-observation.json`,
  `reload-correspondence.json`) bound to the probe contract.
- `gui-client.json` (schema `canonical-fleet-gui-client-v1`): argv,
  display env, join marker + `join_verified`, observation end + alive
  seconds, owned-stop record, client.log sha256.
- Server `stdout.log`/`stderr.log` copied into the stage (manifest
  covered) with the join lines of record.
- `cleanup.json` certified (server reaped, workspace disposed,
  credential removed) with the client terminated first; manifest 0
  mismatches; then the E-row.

## Failure conditions of record (typed, never relabeled)

- No desktop session → typed refusal at prepare AND preflight
  (before any write); no fallback is ever attempted.
- Client spawn fails or exits nonzero → typed failure
  (`GUI client exited (<code>); see …/client.log`), stop.
- Join marker missing within 60 s → typed `TimeoutError`, stop.
- Server death mid-observation → `backend.health()` typed failure, stop.
- Unexpected failure → the standard failure path: failure save, owned
  cleanup, receipts retained, nothing relabeled, attempt dir read-only
  hereafter. One execution; no retry; the grant is consumed whatever
  the outcome.

## Independence verdict (Phase B acceptance criteria)

The GUI probe satisfies NONE of the existing Phase B done-ness
criteria and must not be assumed to replace any native attempt:

- T-030's receipts are the exercise correspondence (purchase/dispatch/
  unpause with `exercise-correspondence.json`) — the probe dispatches
  nothing by contract.
- T-031's receipts are the two arms' `arm-record.json` + the
  descriptive comparison — the probe is neither arm.
- T-032's receipts are the five-anniversary `continuous-summary.json` —
  the probe runs no monitoring loop.
- All three need the conductor's AdminPort/GameScript exchange with the
  hosting instance; a GUI spectator contributes observation, not
  receipts. Each attempt's package stays one sealed launch with its own
  bytes; a probe client inside them would change those bytes and
  invalidate the packages of record. If the operator later WANTS a
  window on a Phase B attempt, that is a NEW reviewed package decision
  per attempt — not this probe.

## Offline regression of record

`tests/test_canonical_fleet_gui.py` 12 passed: identity/contract
independence; fail-closed desktop requirement (refusal before any
write); real offline staging with seal assertions; client argv asserts
(no `-D`/`-f`, spectator `#255`, isolated config + baseset); join
verification from server stdout (marker hit, deadline typed, client
death typed); observation ends typed (operator close / window elapsed +
owned stop); client-crash typed failure; conductor wiring
(`dispatch=False`, client lifecycle order, receipt shape); verify
states; authorization gate. Family suites green (exercise 14, matched
11, continuous 7); lane suites green including the q3 no-purchase
tripwire `test_canonical_reload_only.py`. Statics clean (ruff, format,
py_compile, scoped `uvx ty`, `git diff --check`).
