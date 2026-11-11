"""Offline regression for the T-036 fresh-world GUI probe family.

Zero native processes: identity separation from every canonical/demo
identity, the no-canonical-input structure of both stages, the demo-seed
refusal at the runtime welcome seam, prepare refusals + real offline
staging, preflight passes, and verify states. The GUI client is only
ever a stub here; nothing launches.
"""

import asyncio
import json
from types import SimpleNamespace

import pytest

from app.simulation.openttd.proof import canonical_fleet as driver
from app.simulation.openttd.proof import canonical_fleet_exercise as exercise
from app.simulation.openttd.proof import canonical_fleet_gui as gui_probe
from app.simulation.openttd.proof import fresh_world_gui as fresh
from app.simulation.openttd.proof.harness import manifest, sha256, write_json


def assets_present():
    return fresh.freight.BINARY.is_file() and fresh.freight.GRAPHICS_ARCHIVE.is_file()


def rewrite_status(directory, name, **updates):
    """result/cleanup mutation helper; write_json is exclusive-mode."""
    data = json.loads((directory / name).read_bytes())
    data.update(updates)
    (directory / name).unlink()
    write_json(directory / name, data)
    (directory / "artifact-manifest.sha256").write_text(manifest(directory))


def fresh_creation_fixture(tmp_path):
    """A receipt-complete FRESH_WORLD_CREATE_VERIFIED attempt (offline)."""
    directory = tmp_path / fresh.FRESH_CREATE
    directory.mkdir(parents=True)
    (directory / "effective-openttd.cfg").write_text(
        "[network]\n[game_scripts]\nRoadFreightProof = \n"
    )
    save_path = directory / "fresh-world.sav"
    save_path.write_bytes(b"fresh-world-save-bytes")
    world_generation = dict(
        seed=fresh.FRESH_SEED,
        map_x=fresh.FRESH_MAP_X,
        map_y=fresh.FRESH_MAP_Y,
        heightmap_sha256="h" * 64,
    )
    write_json(
        directory / "PRELAUNCH.json",
        dict(
            schema=fresh.SCHEMA,
            qualification_id=fresh.FRESH_CREATE,
            execution_contract=fresh.CREATE_CONTRACT,
            world_generation=world_generation,
        ),
    )
    (directory / "PRELAUNCH.sha256").write_text(sha256(directory / "PRELAUNCH.json") + "\n")
    write_json(
        directory / "CLAIM.json",
        dict(
            consumed=True,
            prelaunch_digest=sha256(directory / "PRELAUNCH.json"),
            launches_allowed=1,
            retries=0,
        ),
    )
    write_json(
        directory / "result.json",
        dict(status=fresh.FRESH_CREATE_VERIFIED, launches=1, connections=0),
    )
    write_json(
        directory / "cleanup.json",
        dict(
            reaped=True,
            workspace_disposed=True,
            credential_removed=True,
            sockets_closed=True,
        ),
    )
    write_json(
        directory / "world.json",
        dict(world_generation=world_generation, fresh_save_sha256=sha256(save_path)),
    )
    (directory / "artifact-manifest.sha256").write_text(manifest(directory))
    return directory


def test_family_identities_are_independent():
    for identity in (fresh.FRESH_CREATE, fresh.FRESH_GUI):
        assert identity not in (
            driver.CREATE,
            driver.RELOAD,
            exercise.EXERCISE,
            gui_probe.GUI_PROBE,
        )
    assert fresh.FRESH_SEED != fresh.DEMO_SEED == 42
    assert fresh.CREATE_CONTRACT["generation"]["seed"] == fresh.FRESH_SEED
    assert "seed 42" in fresh.CREATE_CONTRACT["generation"]["demo_world_forbidden"]
    for name in ("purchase", "dispatch", "unpause"):
        assert fresh.CREATE_CONTRACT[name] is False
        assert fresh.GUI_CONTRACT[name] is False
    assert fresh.GUI_CONTRACT["welcome"] == dict(
        revision="15.3",
        seed=fresh.FRESH_SEED,
        width=fresh.FRESH_WIDTH,
        height=fresh.FRESH_HEIGHT,
    )
    assert "no Phase B ticket receipts" in fresh.GUI_CONTRACT["receipts"]
    assert "no virtual display" in fresh.GUI_CONTRACT["gui_client"]["video"]


def test_desktop_required_for_gui_only(monkeypatch, tmp_path):
    for name in ("DISPLAY", "WAYLAND_DISPLAY", "XDG_SESSION_TYPE"):
        monkeypatch.delenv(name, raising=False)
    with pytest.raises(ValueError, match="no graphical desktop detected"):
        fresh.prepare_gui(tmp_path / fresh.FRESH_GUI, fresh_world=None)
    monkeypatch.setenv("DISPLAY", ":0")
    assert fresh.require_desktop_session()["DISPLAY"] == ":0"


def test_create_prepare_refuses_wrong_identity(tmp_path):
    with pytest.raises(ValueError, match="exact fresh-world creation identity"):
        fresh.prepare_create(tmp_path / "fresh-world-create-wrong")
    with pytest.raises(ValueError, match="exact fresh-world GUI probe identity"):
        fresh.prepare_gui(
            tmp_path / "fresh-world-gui-wrong",
            fresh_world=fresh_creation_fixture(tmp_path / "fixture"),
        )


def test_gui_prepare_refuses_canonical_demo_evidence(tmp_path, monkeypatch):
    """The no-silent-fallback refusal of record: a canonical/demo evidence
    directory is never acceptable as the fresh world source."""
    monkeypatch.setenv("DISPLAY", ":0")
    canonical = tmp_path / driver.CREATE
    canonical.mkdir()
    with pytest.raises(ValueError, match="fresh-world creation evidence required"):
        fresh.prepare_gui(tmp_path / fresh.FRESH_GUI, fresh_world=canonical)
    assert not (tmp_path / fresh.FRESH_GUI).exists()


def test_gui_prepare_refuses_drifted_fresh_save(tmp_path, monkeypatch):
    monkeypatch.setenv("DISPLAY", ":0")
    directory = fresh_creation_fixture(tmp_path)
    (directory / "fresh-world.sav").write_bytes(b"drifted-after-seal")
    with pytest.raises(ValueError, match="fresh-world creation evidence required"):
        fresh.prepare_gui(tmp_path / fresh.FRESH_GUI, fresh_world=directory)


def test_gui_prepare_refuses_failed_creation(tmp_path, monkeypatch):
    monkeypatch.setenv("DISPLAY", ":0")
    directory = fresh_creation_fixture(tmp_path)
    rewrite_status(directory, "result.json", status="FAILED")
    with pytest.raises(ValueError, match="fresh-world creation evidence required"):
        fresh.prepare_gui(tmp_path / fresh.FRESH_GUI, fresh_world=directory)


def test_create_prepare_stages_fresh_world_offline(tmp_path):
    if not assets_present():
        pytest.skip("pinned native assets not present on this clone")
    prepared = fresh.prepare_create(tmp_path / fresh.FRESH_CREATE)
    metadata = json.loads((prepared.directory / "PRELAUNCH.json").read_bytes())
    assert metadata["qualification_id"] == fresh.FRESH_CREATE
    assert metadata["execution_contract"] == fresh.CREATE_CONTRACT
    assert metadata["world_generation"]["seed"] == fresh.FRESH_SEED
    assert metadata["world_generation"]["map_x"] == fresh.FRESH_MAP_X
    assert "canonical_directory" not in metadata
    assert "canonical_save_sha256" not in metadata
    argv = metadata["argv"]
    assert argv[argv.index("-g") + 1].endswith("heightmap.png")
    assert argv[-2:] == ["-G", str(fresh.FRESH_SEED)]
    root = prepared.spec.workspace.root
    assert not (root / "source.sav").exists()
    assert (root / "heightmap.png").is_file()
    assert "[admin_authorized_keys]" in (root / "private.cfg").read_text()
    assert "admin_password = " in (root / "secrets.cfg").read_text()
    config = (root / "openttd.cfg").read_text()
    assert "pause_on_newgame = false" in config
    assert f"map_x = {fresh.FRESH_MAP_X}" in config
    assert "[game_scripts]" in config
    assert "RoadFreightProof = " in config
    assert (root / "game" / "RoadFreightProof").is_dir()
    assert "bridge_sha256" in metadata
    assert (prepared.directory / "PRELAUNCH.sha256").is_file()


def test_create_preflight_passes_and_claim_refuses(tmp_path):
    if not assets_present():
        pytest.skip("pinned native assets not present on this clone")
    prepared = fresh.prepare_create(tmp_path / fresh.FRESH_CREATE)
    reopened = driver.reopen(prepared.directory)
    metadata = fresh.preflight_create(reopened)
    assert metadata["world_generation"]["seed"] == fresh.FRESH_SEED
    write_json(prepared.directory / "CLAIM.json", dict(consumed=True, launches_allowed=1))
    with pytest.raises(ValueError, match="fresh-world sealed identity/claim mismatch"):
        fresh.preflight_create(driver.reopen(prepared.directory))


def test_runs_require_authorization_but_write_nothing(tmp_path, monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("authorization must precede preflight and claim")

    monkeypatch.setattr(fresh, "preflight_create", forbidden)
    monkeypatch.setattr(fresh, "preflight_gui", forbidden)
    with pytest.raises(ValueError, match="authorization"):
        asyncio.run(fresh.run_create(SimpleNamespace(directory=tmp_path)))
    with pytest.raises(ValueError, match="authorization"):
        asyncio.run(fresh.run_gui(SimpleNamespace(directory=tmp_path)))
    assert list(tmp_path.iterdir()) == []


def test_gui_prepare_stages_fresh_save_offline(tmp_path, monkeypatch):
    if not assets_present():
        pytest.skip("pinned native assets not present on this clone")
    monkeypatch.setenv("DISPLAY", ":0")
    creation = fresh_creation_fixture(tmp_path)
    prepared = fresh.prepare_gui(tmp_path / fresh.FRESH_GUI, fresh_world=creation)
    metadata = json.loads((prepared.directory / "PRELAUNCH.json").read_bytes())
    assert metadata["qualification_id"] == fresh.FRESH_GUI
    assert metadata["execution_contract"] == fresh.GUI_CONTRACT
    assert metadata["fresh_save_sha256"] == sha256(creation / "fresh-world.sav")
    assert "canonical_directory" not in metadata
    assert "canonical_save_sha256" not in metadata
    root = prepared.spec.workspace.root
    staged = (root / "source.sav").read_bytes()
    assert staged == (creation / "fresh-world.sav").read_bytes()
    assert staged != b"staged"  # never the canonical fixture's demo save
    assert "[admin_authorized_keys]" in (root / "private.cfg").read_text()
    assert "admin_password = " in (root / "secrets.cfg").read_text()
    config = (root / "openttd.cfg").read_text()
    assert "[game_scripts]" in config
    # inherited from the creation source's own config; never re-appended
    # (OpenTTD wipes runtime GameScript config on save load — GSDT rules).
    assert config.count("[game_scripts]") == 1
    assert (root / "game" / "RoadFreightProof").is_dir()
    argv = metadata["argv"]
    assert argv[argv.index("-g") + 1].endswith("source.sav")
    assert "-G" not in argv
    assert metadata["budgets"]["total_seconds"] >= 1200


def test_gui_preflight_passes_offline(tmp_path, monkeypatch):
    if not assets_present():
        pytest.skip("pinned native assets not present on this clone")
    monkeypatch.setenv("DISPLAY", ":0")
    creation = fresh_creation_fixture(tmp_path)
    prepared = fresh.prepare_gui(tmp_path / fresh.FRESH_GUI, fresh_world=creation)
    metadata = fresh.preflight_gui(driver.reopen(prepared.directory))
    assert metadata["fresh_save_sha256"] == sha256(creation / "fresh-world.sav")


def test_require_fresh_welcome_rejects_demo_seed():
    """The runtime no-fallback tripwire: the hosted world must report the
    fresh seed and map size; the demo lane's seed 42 refuses typed."""
    expected = fresh.expected_welcome()
    good = SimpleNamespace(
        revision="15.3",
        seed=fresh.FRESH_SEED,
        width=fresh.FRESH_WIDTH,
        height=fresh.FRESH_HEIGHT,
    )
    assert fresh.require_fresh_welcome(good, expected) is good
    for wrong in (
        SimpleNamespace(
            revision="15.3", seed=42, width=fresh.FRESH_WIDTH, height=fresh.FRESH_HEIGHT
        ),
        SimpleNamespace(revision="15.3", seed=fresh.FRESH_SEED, width=128, height=128),
        SimpleNamespace(
            revision="1.0",
            seed=fresh.FRESH_SEED,
            width=fresh.FRESH_WIDTH,
            height=fresh.FRESH_HEIGHT,
        ),
        None,
    ):
        with pytest.raises(ValueError, match="fresh-world secure runtime identity mismatch"):
            fresh.require_fresh_welcome(wrong, expected)


def test_seal_attempt_awaits_cleanup_and_writes_receipts(tmp_path, monkeypatch):
    """The t036-1 failure class of record: DemoBackend.cleanup is async; the
    shared seal never awaited it, so the crashed first attempt left the
    server alive and no cleanup/result/manifest bytes. The seal must await
    the backend cleanup and still write the receipts on the failure path."""
    recorded = {}

    def fake_verify_endpoints(prepared, cleanup):
        recorded["verified"] = True
        return dict(endpoint_closure_verified=True)

    monkeypatch.setattr(fresh, "verify_cleanup_endpoints", fake_verify_endpoints)
    directory = tmp_path / fresh.FRESH_CREATE
    directory.mkdir()
    write_json(
        directory / "PRELAUNCH.json",
        dict(
            schema=fresh.SCHEMA,
            qualification_id=fresh.FRESH_CREATE,
            execution_contract=fresh.CREATE_CONTRACT,
        ),
    )
    (directory / "PRELAUNCH.sha256").write_text(sha256(directory / "PRELAUNCH.json") + "\n")
    logs = tmp_path / "logs"
    logs.mkdir()
    (logs / "stdout.log").write_bytes(b"stdout-bytes")
    root = tmp_path / "ws"
    root.mkdir()
    workspace = SimpleNamespace(logs=logs, root=root, close=lambda: None)
    prepared = SimpleNamespace(
        directory=directory,
        endpoints=(13971, 23971),
        spec=SimpleNamespace(workspace=workspace),
        key_path=tmp_path / "absent-key",
    )

    class FakeBackend:
        async def cleanup(self, prepared):
            recorded["cleaned"] = True
            return dict(reaped=True, remaining_processes=[], cleanup_error=None)

    result = dict(status="FAILED", launches=1)
    asyncio.run(fresh._seal_attempt(prepared, result, FakeBackend()))
    assert recorded == {"cleaned": True, "verified": True}
    cleanup = json.loads((directory / "cleanup.json").read_bytes())
    assert cleanup["reaped"] is True and cleanup["endpoint_closure_verified"] is True
    assert (directory / "stdout.log").read_bytes() == b"stdout-bytes"
    sealed = json.loads((directory / "result.json").read_bytes())
    assert sealed["status"] == "FAILED"
    write_json(
        directory / "CLAIM.json",
        dict(consumed=True, prelaunch_digest=sha256(directory / "PRELAUNCH.json")),
    )
    assert (directory / "artifact-manifest.sha256").is_file()
    assert fresh.verify_create(directory) == "ATTEMPT_NOT_VERIFIED: FAILED"


def test_verify_cli_never_reopens_workspace(tmp_path, monkeypatch):
    """The t036-2 verify sweep defect class: after a VERIFIED run the owned
    cleanup disposed the workspace, so reopening it crashes; the verify
    command must read sealed receipts only."""
    directory = fresh_creation_fixture(tmp_path)
    monkeypatch.setattr(
        fresh.driver,
        "reopen",
        lambda *a, **k: pytest.fail("verify must not reopen the disposed workspace"),
    )
    monkeypatch.setattr("sys.argv", ["fresh_world_gui", "verify", str(directory)])
    assert fresh.main() == 0


def test_verify_states_offline(tmp_path):
    directory = fresh_creation_fixture(tmp_path)
    assert fresh.verify_create(directory) == fresh.FRESH_CREATE_VERIFIED
    rewrite_status(directory, "result.json", status="FAILED")
    assert fresh.verify_create(directory) == "ATTEMPT_NOT_VERIFIED: FAILED"
    (directory / "CLAIM.json").unlink()
    (directory / "artifact-manifest.sha256").write_text(manifest(directory))
    assert fresh.verify_create(directory) == "AUTHORIZATION_UNVERIFIED"


def test_gui_verify_unverified_without_claim(tmp_path, monkeypatch):
    if not assets_present():
        pytest.skip("pinned native assets not present on this clone")
    monkeypatch.setenv("DISPLAY", ":0")
    creation = fresh_creation_fixture(tmp_path)
    prepared = fresh.prepare_gui(tmp_path / fresh.FRESH_GUI, fresh_world=creation)
    assert fresh.verify_gui(prepared.directory) == "AUTHORIZATION_UNVERIFIED"


def test_fresh_client_spawn_and_receipt_use_fresh_identity(tmp_path, monkeypatch):
    root = tmp_path / "workspace"
    (root / "baseset").mkdir(parents=True)
    directory = tmp_path / fresh.FRESH_GUI
    directory.mkdir()
    prepared = SimpleNamespace(
        directory=directory,
        endpoints=[3979],
        spec=SimpleNamespace(workspace=SimpleNamespace(root=root)),
    )
    recorded = {}

    class Recorder:
        def __init__(self, argv, cwd=None, stdout=None, stderr=None):
            recorded["argv"] = tuple(argv)
            recorded["cwd"] = cwd
            recorded["stdout"] = stdout

        def poll(self):
            return None

    monkeypatch.setattr(gui_probe.subprocess, "Popen", Recorder)
    monkeypatch.setattr(gui_probe.time, "sleep", lambda s: None)
    client = gui_probe.GuiClient(
        prepared,
        client_name=fresh.CLIENT_NAME,
        identity=fresh.FRESH_GUI,
        join_marker=fresh.JOIN_MARKER,
        schema=fresh.FRESH_GUI_CLIENT_SCHEMA,
    )
    argv = client.spawn()
    assert argv == recorded["argv"]
    assert "-D" not in argv and "-f" not in argv
    assert "-n" in argv and argv[argv.index("-n") + 1].endswith("#255")
    cfg = (directory / "gui-client" / "openttd.cfg").read_text()
    assert f"client_name = {fresh.CLIENT_NAME}" in cfg
    assert f"client_name = {gui_probe.CLIENT_NAME}" not in cfg
    receipt = client.receipt(
        argv=argv,
        display_env={"DISPLAY": ":0"},
        join_verified=True,
        observation={"end": "OPERATOR_CLOSED_WINDOW", "note": "closed", "alive_seconds": 7},
        owned_stop={"owned_exit": None, "client_terminated_before_server_cleanup": True},
    )
    assert receipt["schema"] == fresh.FRESH_GUI_CLIENT_SCHEMA
    assert receipt["identity"] == fresh.FRESH_GUI
    assert receipt["client_name"] == fresh.CLIENT_NAME
    assert receipt["join_marker"] == fresh.JOIN_MARKER


def test_conduct_wires_fresh_client(tmp_path, monkeypatch):
    monkeypatch.setenv("DISPLAY", ":0")
    directory = tmp_path / fresh.FRESH_GUI
    directory.mkdir()
    prepared = SimpleNamespace(
        directory=directory, spec=SimpleNamespace(stdout_path=directory / "stdout.log")
    )
    phases = []
    observation = dict(end="OPERATOR_CLOSED_WINDOW", note="closed", alive_seconds=7)

    class StubClient:
        def __init__(self, prepared, **kwargs):
            phases.append((kwargs["client_name"], kwargs["identity"], kwargs["schema"]))
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
            return dict(client_terminated_before_server_cleanup=True, owned_exit=None)

        def receipt(self, **kwargs):
            return dict(**kwargs, client_terminated_before_server_cleanup=True)

    monkeypatch.setattr(gui_probe, "GuiClient", StubClient)
    result = {}
    asyncio.run(fresh.conduct_fresh_gui(SimpleNamespace(), prepared, SimpleNamespace(), result))
    assert phases[0] == (fresh.CLIENT_NAME, fresh.FRESH_GUI, fresh.FRESH_GUI_CLIENT_SCHEMA)
    assert [phase[0] for phase in phases[1:]] == ["spawn", "join", "observe", "stop"]
    assert result["status"] == fresh.FRESH_GUI_VERIFIED
    assert result["gui_client"] == "OPERATOR_CLOSED_WINDOW"
    receipt = json.loads((directory / "gui-client.json").read_text())
    assert receipt["join_verified"] is True
    assert receipt["observation"] == observation
    assert receipt["display_env"]["DISPLAY"] == ":0"
