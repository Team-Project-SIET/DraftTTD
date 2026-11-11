"""T-035 GUI native probe stage of record (Phase B-adjacent, independent).

A fresh stage loads the SAME frozen E2 canonical evidence under the SAME
byte-pinned bridge package, proves the q3 reload-only correspondence
(paused, nothing purchased, nothing dispatched, nothing unpaused), and
then launches a SECOND real OpenTTD 15.3 desktop client that joins the
live canonical world as a visible spectator on the operator's own
desktop session (X11/XWayland). The probe never substitutes a virtual
display, never forks into the background, and never relabels a missing
window as success: without a desktop session it refuses typed, and the
window-visibility judgement stays the operator's (the probe records only
machine-verified facts: process, argv, server-side join marker,
liveness, owned exit). The probe produces NONE of the Phase B ticket
receipts; it is its own ticket with its own fresh explicit grant.
"""

import asyncio
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

from . import canonical_fleet as driver
from . import canonical_fleet_exercise as exercise
from .harness import BINARY, sha256, write_json

GUI_PROBE = "canonical-fleet-gui-probe-t035-1"
GUI_PROBE_VERIFIED = "CANONICAL_FLEET_GUI_PROBE_VERIFIED"
CLIENT_NAME = "Canonical GUI Probe"
JOIN_MARKER = f"*** {CLIENT_NAME} has joined the game"
JOIN_SECONDS = 60
OBSERVATION_SECONDS = 600

GUI_PROBE_CONTRACT = dict(
    mode="canonical-fleet-gui-probe",
    purchase=False,
    dispatch=False,
    unpause=False,
    world_state="paused canonical reload correspondence",
    gui_client=dict(
        process="second real OpenTTD 15.3 desktop client on the operator's desktop",
        video="the operator's own X11/XWayland session is REQUIRED; no virtual display,"
        " no headless fallback, no -f fork",
        join="127.0.0.1:<game-port>#255 spectator",
        client_name=CLIENT_NAME,
        fork_forbidden=True,
        join_seconds=JOIN_SECONDS,
        observation_seconds=OBSERVATION_SECONDS,
    ),
    correspondence="exact-native-semantic-state (reload-only, proven q3 machinery)",
    receipts="reload correspondence + gui-client receipt; no Phase B ticket receipts",
)


def require_desktop_session():
    """Fail-closed display check; the probe never falls back headless."""
    if not (os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY")):
        raise ValueError(
            "no graphical desktop detected; the GUI probe requires the operator's"
            " desktop session and never substitutes a virtual display or a headless"
            " fallback — run it from a desktop terminal"
        )
    return dict(
        DISPLAY=os.environ.get("DISPLAY"),
        WAYLAND_DISPLAY=os.environ.get("WAYLAND_DISPLAY"),
        XDG_SESSION_TYPE=os.environ.get("XDG_SESSION_TYPE"),
        XAUTHORITY=os.environ.get("XAUTHORITY"),
    )


def prepare(directory, *, canonical):
    require_desktop_session()
    return exercise.prepare(
        directory,
        canonical=canonical,
        identity=GUI_PROBE,
        contract=GUI_PROBE_CONTRACT,
        authorization=(
            "separate explicit authorization; ONE dedicated-server launch; ONE AdminPort"
            " connection; ONE GUI client join; no retry/reconnect; reload-only, paused;"
            " the probe ends when the operator closes the window or the observation"
            " window elapses; stop on unexpected failure"
        ),
    )


def preflight(prepared):
    require_desktop_session()
    return exercise.preflight(prepared, identity=GUI_PROBE, contract=GUI_PROBE_CONTRACT)


def verify(directory):
    return exercise.verify(directory, contract=GUI_PROBE_CONTRACT, status=GUI_PROBE_VERIFIED)


class GuiClient:
    """Own the one GUI client this stage launched; never touch a user's client.

    The spawn argv is the demo lane's proven spectator client byte-for-byte
    (no -D, no -f); the join is verified from the SERVER's own stdout (the
    client's own log stays empty in GUI mode, as every retained demo run
    shows), so the AdminPort allowlist stays untouched.
    """

    def __init__(self, prepared):
        self.prepared = prepared
        self.directory = prepared.directory / "gui-client"
        self.process = None
        self.exit = None

    def spawn(self):
        if self.process is not None:
            raise ValueError("GUI client already spawned")
        self.directory.mkdir()
        shutil.copytree(self.prepared.spec.workspace.root / "baseset", self.directory / "baseset")
        cfg = self.directory / "openttd.cfg"
        cfg.write_text(f"[misc]\ngraphicsset = OpenGFX\n[network]\nclient_name = {CLIENT_NAME}\n")
        log = (self.directory / "client.log").open("wb")
        argv = (
            str(BINARY),
            "-c",
            str(cfg),
            "-x",
            "-X",
            "-n",
            f"127.0.0.1:{self.prepared.endpoints[0]}#255",
        )
        for forbidden in ("-D", "-f"):
            if any(a.startswith(forbidden) for a in argv):
                raise ValueError("GUI probe client must not fork or run dedicated")
        self.process = subprocess.Popen(
            argv,
            cwd=self.directory,
            stdout=log,
            stderr=subprocess.STDOUT,
        )
        time.sleep(1.0)
        self.require_alive()
        return argv

    def require_alive(self):
        if self.process is not None and self.process.poll() is not None:
            raise RuntimeError(
                f"GUI client exited ({self.process.returncode}); "
                f"see {self.directory / 'client.log'}"
            )

    def client_exit(self):
        """Typed client-exit classification (demo lane precedent)."""
        code = None if self.process is None else self.process.poll()
        if code is None:
            return None
        if code == 0:
            return "spectator window closed by operator (client exited 0)"
        raise RuntimeError(f"GUI client exited ({code}); see {self.directory / 'client.log'}")

    async def verify_joined(self, backend, deadline_seconds=JOIN_SECONDS):
        deadline = time.monotonic() + deadline_seconds
        stdout_path = self.prepared.spec.stdout_path
        while True:
            backend.health()
            if JOIN_MARKER in stdout_path.read_text(errors="replace"):
                return True
            self.client_exit()
            self.require_alive()
            if time.monotonic() >= deadline:
                raise TimeoutError("server-side GUI client join marker missing: " + JOIN_MARKER)
            await asyncio.sleep(0.5)

    async def observe(self, backend, deadline_seconds=OBSERVATION_SECONDS):
        """Watch the window's liveness until the operator ends it or time is up."""
        started = time.monotonic()
        deadline = started + deadline_seconds
        while True:
            backend.health()
            note = self.client_exit()
            if note is not None:
                return dict(
                    end="OPERATOR_CLOSED_WINDOW",
                    note=note,
                    alive_seconds=int(time.monotonic() - started),
                )
            if time.monotonic() >= deadline:
                return dict(
                    end="OBSERVATION_WINDOW_ELAPSED",
                    note="client terminated by the probe after the observation window",
                    alive_seconds=int(time.monotonic() - started),
                )
            await asyncio.sleep(0.5)

    def stop(self):
        if self.process is None or self.process.poll() is not None:
            return dict(
                client_terminated_before_server_cleanup=True,
                owned_exit=self.exit,
            )
        self.process.terminate()
        try:
            self.process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.process.wait(timeout=5)
        self.exit = dict(code=self.process.returncode, owned_terminate=True)
        return dict(
            client_terminated_before_server_cleanup=True,
            owned_exit=self.exit,
        )

    def receipt(self, *, argv, display_env, join_verified, observation, owned_stop):
        log = self.directory / "client.log"
        return dict(
            schema="canonical-fleet-gui-client-v1",
            identity=GUI_PROBE,
            client_argv=list(argv),
            client_name=CLIENT_NAME,
            spectator_company="255",
            display_env=display_env,
            server_stdout_path="stdout.log",
            join_marker=JOIN_MARKER,
            join_verified=join_verified,
            observation=observation,
            client_log_sha256=sha256(log) if log.is_file() else None,
            **owned_stop,
        )


async def conduct_gui_probe(backend, prepared, session, result):
    """Reload correspondence (paused, nothing dispatched), then the window."""
    await exercise.conduct_exercise(
        backend,
        prepared,
        session,
        result,
        identity=GUI_PROBE,
        contract=GUI_PROBE_CONTRACT,
        dispatch=False,
    )
    display_env = require_desktop_session()
    client = GuiClient(prepared)
    observation = None
    try:
        argv = client.spawn()
        await client.verify_joined(backend)
        observation = await client.observe(backend)
    finally:
        owned_stop = client.stop()
    write_json(
        prepared.directory / "gui-client.json",
        client.receipt(
            argv=argv,
            display_env=display_env,
            join_verified=True,
            observation=observation,
            owned_stop=owned_stop,
        ),
    )
    result["gui_client"] = observation["end"]
    result["status"] = GUI_PROBE_VERIFIED


async def run(prepared, *, authorize_one_launch=False):
    return await exercise.run(
        prepared,
        authorize_one_launch=authorize_one_launch,
        identity=GUI_PROBE,
        contract=GUI_PROBE_CONTRACT,
        conduct=conduct_gui_probe,
    )


def main():
    import argparse
    import asyncio

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prepare", "preflight", "verify", "run"))
    parser.add_argument("directory", type=Path)
    parser.add_argument("--canonical", type=Path)
    parser.add_argument(
        "--authorize-one-launch",
        action="store_true",
        help="fresh explicit operator authorization required for the ONE server launch",
    )
    args = parser.parse_args()
    if args.command == "prepare":
        if args.canonical is None:
            parser.error("prepare requires --canonical pointing at the E2 created evidence")
        prepared = prepare(args.directory, canonical=args.canonical)
        print(f"prepared {prepared.directory} (offline; no launch)")
        return 0
    if args.command in ("preflight", "run"):
        prepared = driver.reopen(args.directory)
        if args.command == "preflight":
            preflight(prepared)
            print("canonical GUI probe preflight PASS")
            return 0
        result = asyncio.run(run(prepared, authorize_one_launch=args.authorize_one_launch))
        print(json.dumps(result, sort_keys=True))
        return 0 if result["status"] == GUI_PROBE_VERIFIED else 1
    status = verify(args.directory)
    print(status)
    return 0 if status == GUI_PROBE_VERIFIED else 1


if __name__ == "__main__":
    sys.exit(main())
