"""Offline regression for the T-035 GUI native probe stage of record.

Zero native processes: identity separation, the fail-closed desktop
requirement, prepare refusals and one real offline staging, the client
spawn argv (no -D, no -f), the server-side join verification, the typed
observation ends, the conductor wiring (dispatch=False), and verify
states. The GUI client is only ever a stub here.
"""

import asyncio
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from app.simulation.openttd import freight_canonical_runtime
from app.simulation.openttd.proof import canonical_fleet as driver
from app.simulation.openttd.proof import canonical_fleet_exercise as exercise
from app.simulation.openttd.proof import canonical_fleet_gui as gui
from app.simulation.openttd.proof import canonical_fleet_matched as matched
from app.simulation.openttd.proof import freight_delivery


def test_gui_probe_identity_and_contract_are_independent():
    assert gui.GUI_PROBE not in (
        driver.CREATE,
        driver.RELOAD,
        exercise.EXERCISE,
        matched.ARM_A,
        matched.ARM_B,
    )
    contract = gui.GUI_PROBE_CONTRACT
    assert contract["purchase"] is False
    assert contract["dispatch"] is False
    assert contract["unpause"] is False
    assert contract["gui_client"]["fork_forbidden"] is True
    assert contract["gui_client"]["observation_seconds"] == 600
    assert "no Phase B ticket receipts" in contract["receipts"]
    assert "no virtual display" in contract["gui_client"]["video"]


def test_desktop_session_is_required_fail_closed(monkeypatch):
    for name in ("DISPLAY", "WAYLAND_DISPLAY", "XDG_SESSION_TYPE"):
        monkeypatch.delenv(name, raising=False)
    with pytest.raises(ValueError, match="no graphical desktop detected"):
        gui.require_desktop_session()
    monkeypatch.setenv("DISPLAY", ":0")
    env = gui.require_desktop_session()
    assert env["DISPLAY"] == ":0"


def test_prepare_requires_canonical_evidence_and_desktop(tmp_path, monkeypatch):
    monkeypatch.setenv("DISPLAY", ":0")
    directory = tmp_path / gui.GUI_PROBE
    with pytest.raises(ValueError, match="stage requires canonical"):
        gui.prepare(directory, canonical=None)
    assert not directory.exists()
    monkeypatch.delenv("DISPLAY", raising=False)
    monkeypatch.delenv("WAYLAND_DISPLAY", raising=False)
    with pytest.raises(ValueError, match="no graphical desktop detected"):
        gui.prepare(directory, canonical=tmp_path)


def test_prepare_stages_seal_offline(tmp_path, monkeypatch):
    monkeypatch.setenv("DISPLAY", ":0")
    created = SimpleNamespace(source_save_sha256="a" * 64)
    canonical = tmp_path / "canonical-source"
    canonical.mkdir()
    for service in range(3):
        (canonical / f"native-plan-{service}.json").write_text("{}")
    (canonical / "effective-openttd.cfg").write_text("[network]\n")
    (canonical / "canonical.sav").write_bytes(b"staged")
    monkeypatch.setattr(driver, "verify_created_source", lambda _: created)
    monkeypatch.setattr(freight_canonical_runtime, "verify_save", lambda *a, **k: None)
    prepared = gui.prepare(tmp_path / gui.GUI_PROBE, canonical=canonical)
    metadata = json.loads((prepared.directory / "PRELAUNCH.json").read_bytes())
    assert metadata["qualification_id"] == gui.GUI_PROBE
    assert metadata["execution_contract"] == gui.GUI_PROBE_CONTRACT
    assert (prepared.directory / "PRELAUNCH.sha256").is_file()
    assert metadata["budgets"]["total_seconds"] >= 1200


class FakeProcess:
    def __init__(self):
        self.returncode = None
        self.terminated = False

    def poll(self):
        return self.returncode

    def terminate(self):
        self.terminated = True
        self.returncode = -15

    def kill(self):
        self.returncode = -9

    def wait(self, timeout=None):
        return self.returncode


def staged_prepared(tmp_path, *, server_log=""):
    root = tmp_path / "workspace"
    (root / "baseset").mkdir(parents=True)
    directory = tmp_path / gui.GUI_PROBE
    directory.mkdir()
    (directory / "PRELAUNCH.json").write_text(
        json.dumps(
            dict(
                schema=exercise.SCHEMA,
                qualification_id=gui.GUI_PROBE,
                execution_contract=gui.GUI_PROBE_CONTRACT,
                canonical_directory=str(tmp_path),
            )
        )
    )
    stdout = directory / "stdout.log"
    stdout.write_text(server_log)
    return SimpleNamespace(
        directory=directory,
        endpoints=[(127 << 24) | 1, 3979],
        spec=SimpleNamespace(workspace=SimpleNamespace(root=root), stdout_path=stdout),
    )


def test_stage_writes_admin_auth_trio(tmp_path, monkeypatch):
    """The t035-2 refusal class of record: the staged workspace must carry
    the admin auth material the server needs to start its admin network
    under allow_insecure_admin_login = false (E168) — private.cfg with the
    generated key's public hex, secrets.cfg with the password line, and
    the .admin-secret matching the PRELAUNCH public key."""
    created = SimpleNamespace(source_save_sha256="a" * 64)
    canonical = tmp_path / "canonical-source"
    canonical.mkdir()
    for service in range(3):
        (canonical / f"native-plan-{service}.json").write_text("{}")
    (canonical / "effective-openttd.cfg").write_text("[network]\n")
    (canonical / "canonical.sav").write_bytes(b"staged")
    monkeypatch.setattr(driver, "verify_created_source", lambda _: created)
    monkeypatch.setattr(freight_canonical_runtime, "verify_save", lambda *a, **k: None)
    prepared = gui.prepare(tmp_path / gui.GUI_PROBE, canonical=canonical)
    metadata = json.loads((prepared.directory / "PRELAUNCH.json").read_bytes())
    root = prepared.spec.workspace.root
    private = (root / "private.cfg").read_text()
    assert f"[admin_authorized_keys]\n{metadata['public_key']}\n" in private
    secrets = (root / "secrets.cfg").read_text()
    assert "admin_password = " in secrets
    assert metadata["public_key"] != "0" * 64
    from app.simulation.openttd.admin_crypto import AuthorizedKey

    key = AuthorizedKey.from_bytes(prepared.key_path.read_bytes())
    assert key.public_hex == metadata["public_key"]
    mode = (root / ".admin-secret").stat().st_mode & 0o777
    assert mode == 0o600


def test_client_spawn_argv_has_no_fork_or_dedicated(tmp_path, monkeypatch):
    prepared = staged_prepared(tmp_path)
    recorded = {}

    class Recorder:
        def __init__(self, argv, cwd=None, stdout=None, stderr=None):
            recorded["argv"] = tuple(argv)
            recorded["cwd"] = cwd
            recorded["stdout"] = stdout

        def poll(self):
            return None

    monkeypatch.setattr(gui.subprocess, "Popen", Recorder)
    monkeypatch.setattr(gui.time, "sleep", lambda s: None)
    client = gui.GuiClient(prepared)
    argv = client.spawn()
    assert argv == recorded["argv"]
    assert "-D" not in argv and "-f" not in argv
    assert "-X" in argv and "-x" in argv
    assert "-n" in argv
    join_index = argv.index("-n")
    assert argv[join_index + 1].startswith("127.0.0.1:") and argv[join_index + 1].endswith("#255")
    assert recorded["cwd"] == prepared.directory / "gui-client"
    assert (prepared.directory / "gui-client" / "baseset").is_dir()
    cfg = (prepared.directory / "gui-client" / "openttd.cfg").read_text()
    assert "client_name = Canonical GUI Probe" in cfg


def test_client_join_verified_from_server_stdout(tmp_path):
    prepared = staged_prepared(tmp_path)
    backend = SimpleNamespace(health=lambda: None)
    client = gui.GuiClient(prepared)
    client.process = FakeProcess()
    with pytest.raises(TimeoutError, match="join marker missing"):
        asyncio.run(client.verify_joined(backend, deadline_seconds=0.1))
    prepared.spec.stdout_path.write_text(
        f"*** Game paused (connecting clients)\n{gui.JOIN_MARKER} (Client #2)\n"
    )
    assert asyncio.run(client.verify_joined(backend, deadline_seconds=1)) is True


def test_client_join_typed_when_client_dies(tmp_path):
    prepared = staged_prepared(tmp_path)
    client = gui.GuiClient(prepared)
    client.process = FakeProcess()
    client.process.returncode = 1
    with pytest.raises(RuntimeError, match="GUI client exited \\(1\\)"):
        asyncio.run(client.verify_joined(SimpleNamespace(health=lambda: None), 1))


def test_observation_ends_typed(tmp_path):
    prepared = staged_prepared(tmp_path)
    client = gui.GuiClient(prepared)
    client.process = FakeProcess()
    ended = asyncio.run(client.observe(SimpleNamespace(health=lambda: None), 0))
    assert ended["end"] == "OBSERVATION_WINDOW_ELAPSED"
    assert ended["alive_seconds"] >= 0
    stopped = client.stop()
    assert stopped["owned_exit"] == dict(code=-15, owned_terminate=True)
    assert stopped["client_terminated_before_server_cleanup"] is True
    client2 = gui.GuiClient(prepared)
    client2.process = FakeProcess()
    client2.process.returncode = 0
    closed = asyncio.run(client2.observe(SimpleNamespace(health=lambda: None), 5))
    assert closed["end"] == "OPERATOR_CLOSED_WINDOW"
    assert closed["note"] == "spectator window closed by operator (client exited 0)"


def test_client_crash_is_typed_failure(tmp_path):
    prepared = staged_prepared(tmp_path)
    client = gui.GuiClient(prepared)
    client.process = FakeProcess()
    client.process.returncode = 139
    with pytest.raises(RuntimeError, match="GUI client exited \\(139\\)"):
        asyncio.run(client.observe(SimpleNamespace(health=lambda: None), 5))


def test_conduct_wires_reload_only_then_client(tmp_path, monkeypatch):
    prepared = staged_prepared(tmp_path)
    phases = []

    async def staged_exercise(backend, prepared, session, result, **kwargs):
        phases.append(("reload-only", kwargs["dispatch"]))

    observation = dict(end="OPERATOR_CLOSED_WINDOW", note="closed", alive_seconds=7)

    class StubClient:
        def __init__(self, prepared):
            phases.append(("client-init", None))
            self.prepared = prepared
            self.directory = prepared.directory / "gui-client"
            self.process = None
            self.exit = None

        def spawn(self):
            phases.append(("spawn", None))
            return ("-bin", "-c", "cfg", "-x", "-X", "-n", "127.0.0.1:3979#255")

        async def verify_joined(self, backend):
            phases.append(("join", None))
            return True

        async def observe(self, backend):
            phases.append(("observe", None))
            return observation

        def stop(self):
            phases.append(("stop", None))
            return dict(
                client_terminated_before_server_cleanup=True,
                owned_exit=None,
            )

        def receipt(self, **kwargs):
            return dict(
                **kwargs,
                identity=gui.GUI_PROBE,
                client_terminated_before_server_cleanup=True,
            )

    monkeypatch.setattr(exercise, "conduct_exercise", staged_exercise)
    monkeypatch.setattr(gui, "GuiClient", StubClient)
    result = {}
    asyncio.run(gui.conduct_gui_probe(SimpleNamespace(), prepared, SimpleNamespace(), result))
    assert phases == [
        ("reload-only", False),
        ("client-init", None),
        ("spawn", None),
        ("join", None),
        ("observe", None),
        ("stop", None),
    ]
    assert result["status"] == gui.GUI_PROBE_VERIFIED
    assert result["gui_client"] == "OPERATOR_CLOSED_WINDOW"
    receipt = json.loads((prepared.directory / "gui-client.json").read_text())
    assert receipt["join_verified"] is True
    assert receipt["observation"] == observation
    assert receipt["client_terminated_before_server_cleanup"] is True
    assert receipt["display_env"]["DISPLAY"]


def test_verify_states(tmp_path):
    (tmp_path / "PRELAUNCH.json").write_text(
        json.dumps(
            dict(
                schema=exercise.SCHEMA,
                qualification_id=gui.GUI_PROBE,
                execution_contract=gui.GUI_PROBE_CONTRACT,
                canonical_directory=str(tmp_path),
            )
        )
    )
    assert gui.verify(tmp_path) == "AUTHORIZATION_UNVERIFIED"
    (tmp_path / "CLAIM.json").write_text("{}")
    (tmp_path / "result.json").write_text(json.dumps(dict(status="FAILED")))
    assert gui.verify(tmp_path).startswith("ATTEMPT_NOT_VERIFIED")
    (tmp_path / "result.json").write_text(json.dumps(dict(status=gui.GUI_PROBE_VERIFIED)))
    from app.simulation.openttd.proof.harness import sha256

    digest = sha256(tmp_path / "result.json")
    (tmp_path / "artifact-manifest.sha256").write_text(f"{digest}  result.json\n")
    assert gui.verify(tmp_path) == gui.GUI_PROBE_VERIFIED


def test_run_requires_authorization_but_writes_nothing(tmp_path, monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("authorization must precede preflight and claim")

    monkeypatch.setattr(exercise, "preflight", forbidden)
    with pytest.raises(ValueError, match="authorization"):
        asyncio.run(gui.run(SimpleNamespace(directory=tmp_path)))
    assert list(tmp_path.iterdir()) == []


def test_preflight_passes_on_real_staging_unpatched(tmp_path):
    """The t035-1 refusal class of record: preflight must pass over a REAL
    staging from the retained E2 evidence with verify_created_source and
    verify_save UNPATCHED (E167). Skip-typed as missing evidence on clones
    without the retained bytes (E151 precedent). The canonical anchor is
    the module's CREATE constant of record — create-q3 at E167, advanced
    to create-q5 by the E186/E189 bridge-fix rounds (identities advance,
    never a retry); verify_created_source refuses any other name."""
    canonical = Path(__file__).resolve().parents[1] / "artifacts/runtime" / driver.CREATE
    binary = freight_delivery.BINARY
    graphics = freight_delivery.GRAPHICS_ARCHIVE
    if (
        not (canonical / "canonical.sav").is_file()
        or not binary.is_file()
        or not graphics.is_file()
    ):
        pytest.skip("retained native evidence not present on this clone")
    prepared = gui.prepare(tmp_path / gui.GUI_PROBE, canonical=canonical)
    created = driver.load_created(canonical)
    freight_canonical_runtime.verify_save(prepared.spec.workspace.root / "source.sav", created)
    metadata = exercise.preflight(prepared, identity=gui.GUI_PROBE, contract=gui.GUI_PROBE_CONTRACT)
    assert metadata["qualification_id"] == gui.GUI_PROBE
    assert metadata["canonical_save_sha256"] == created.source_save_sha256
