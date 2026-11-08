"""Public demo smoke tests use controlled peers, never a native game/client."""

import asyncio
import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace

import pytest

from app import openttd_demo as demo
from app.simulation.openttd.proof import freight_delivery as native


@pytest.fixture(autouse=True)
def no_native(monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("offline demo smoke attempted a native process")

    monkeypatch.setattr(demo.subprocess, "Popen", forbidden)


def test_startup_fails_before_prepare_without_desktop(monkeypatch, capsys):
    monkeypatch.setattr(demo, "sha256", lambda _: demo.BINARY_SHA256)
    monkeypatch.setattr(demo, "BINARY", Path(__file__))
    monkeypatch.setattr(native, "GRAPHICS_ARCHIVE", Path(__file__))
    monkeypatch.setattr(native, "ARCHIVE_SHA256", demo.BINARY_SHA256)
    monkeypatch.delenv("DISPLAY", raising=False)
    monkeypatch.delenv("WAYLAND_DISPLAY", raising=False)
    monkeypatch.setattr(native, "prepare", lambda *a, **k: pytest.fail("must fail before staging"))
    assert demo.main(["run"]) == 1
    assert "No graphical desktop" in capsys.readouterr().err


def test_offline_sample_runs_real_p05_and_selects_three_services(tmp_path):
    from app.planning.domain import ExecutionPlan, PlanningScenario
    from app.planning.optimizer import optimize_candidate_network
    from app.planning.validation import validate_execution_plan

    scenario = PlanningScenario.model_validate_json(demo.SAMPLE.read_bytes())
    plan = optimize_candidate_network(scenario).plan
    validate_execution_plan(plan, scenario)
    assert len(plan.routes) == 3
    (tmp_path / "planning-scenario.json").write_bytes(demo.SAMPLE.read_bytes())
    (tmp_path / "execution-plan.json").write_text(plan.model_dump_json())
    assert len(demo.selections(tmp_path)) == 3
    assert all("industry-" in row for row in demo.selections(tmp_path))
    assert ExecutionPlan.model_validate_json(plan.model_dump_json()) == plan


def test_viewer_launches_isolated_spectator_and_reaps_only_owned_client(tmp_path, monkeypatch):
    assets = tmp_path / "server/baseset"
    assets.mkdir(parents=True)
    (assets / "test.obg").write_text("controlled asset")
    root = tmp_path / "run"
    root.mkdir()
    calls = []

    class Process:
        returncode = None

        def poll(self):
            return self.returncode

        def terminate(self):
            calls.append("terminate")
            self.returncode = 0

        def wait(self, timeout=None):
            calls.append("reap")
            return self.returncode

    def launch(argv, **kwargs):
        calls.append(argv)
        assert kwargs["cwd"] == root / "client"
        assert "-D" not in argv
        assert argv[-1] == "127.0.0.1:12345#255"
        assert "server" not in argv[2]
        return Process()

    monkeypatch.setattr(demo.subprocess, "Popen", launch)
    viewer = demo.Viewer(root, headless=False, view_seconds=0)
    prepared = SimpleNamespace(
        directory=root,
        endpoints=(12345, 23456),
        spec=SimpleNamespace(workspace=SimpleNamespace(root=assets.parent)),
    )

    async def smoke():
        await viewer.ready(None, prepared)
        await viewer.close()

    asyncio.run(smoke())
    assert calls[-2:] == ["terminate", "reap"]
    assert (root / "client/baseset/test.obg").exists()
    assert viewer.log.closed


@pytest.mark.parametrize("failure", [None, "ready", "delivered", "closing"])
def test_native_runner_hooks_deliver_then_close_client_before_server(
    tmp_path, monkeypatch, failure
):
    calls = []
    workspace = tmp_path / "isolated/world"
    logs = workspace / "logs"
    logs.mkdir(parents=True)
    key = workspace / ".admin-secret"
    key.write_bytes(native.AuthorizedKey.generate()._secret)
    prepared = SimpleNamespace(
        directory=tmp_path,
        key_path=key,
        endpoints=(1, 2),
        spec=SimpleNamespace(
            workspace=SimpleNamespace(
                root=workspace, logs=logs, close=lambda: shutil.rmtree(workspace)
            )
        ),
    )
    (tmp_path / "PRELAUNCH.json").write_text(
        json.dumps(dict(demo=True, planner=True, network=True, budgets={"total_seconds": 5}))
    )

    @dataclass
    class Welcome:
        revision: str = "15.3"
        seed: int = 42
        width: int = 64
        height: int = 64

    class Session:
        welcome = Welcome()
        protocol = object()
        state = native.AuthState.ACTIVE

        @classmethod
        async def connect_secure(cls, *args, **kwargs):
            calls.append("secure-connect")
            return cls()

        async def authenticate(self, *args, **kwargs):
            pass

    class Backend:
        process = None
        planning_read_count = 0

        async def launch(self, p):
            self.process = object()
            calls.append("server-start")

        async def cleanup(self, p):
            calls.append("server-close")
            return dict(reaped=True, cleanup_error=[], sockets_closed=True)

    async def noop(*args, **kwargs):
        pass

    async def execute(*args):
        calls.append("native-three-service-executor")

    async def ready(*args):
        calls.append("client-ready")
        if failure == "ready":
            raise RuntimeError("client startup failed")

    async def delivered(*args):
        calls.append("delivery-view")
        if failure == "delivered":
            raise RuntimeError("client died")

    async def closing():
        calls.append("client-close")
        if failure == "closing":
            raise RuntimeError("client cleanup failed")

    from app.simulation.openttd import freight_native_network

    monkeypatch.setattr(native, "preflight", lambda _: None)
    monkeypatch.setattr(native, "backend_for", lambda _: Backend())
    monkeypatch.setattr(
        native,
        "ScenarioPlanningAccounting",
        lambda _: SimpleNamespace(observe=lambda *a: None, enter=lambda *a: None),
    )
    monkeypatch.setattr(native, "PlannerDeliverySession", Session)
    monkeypatch.setattr(native, "GameScriptTransport", lambda *a: SimpleNamespace(subscribe=noop))
    monkeypatch.setattr(native, "wait_log", noop)
    monkeypatch.setattr(native, "save", noop)
    monkeypatch.setattr(native, "console", lambda *a: None)
    monkeypatch.setattr(native, "verify_cleanup_endpoints", lambda *a: {})
    monkeypatch.setattr(freight_native_network, "execute_network", execute)
    result = asyncio.run(
        native.run(prepared, on_ready=ready, on_delivered=delivered, on_closing=closing)
    )
    assert calls.count("server-start") == calls.count("secure-connect") == 1
    assert calls.index("client-close") < calls.index("server-close")
    assert not workspace.exists()
    if failure is None:
        assert calls.index("native-three-service-executor") < calls.index("delivery-view")
        assert result["status"] == "NATIVE_MULTI_SERVICE_DELIVERY_VERIFIED"
    else:
        assert result["status"].startswith("FAILED")
        assert "client" in result.get("error", result.get("client_cleanup_error", ""))


def test_results_display_and_sample_p07(tmp_path, capsys):
    source = tmp_path
    (source / "receipt.json").write_text(
        json.dumps(
            {"services": [{"source": 4, "destination": 5, "delivered": 20, "payment_income": 341}]}
        )
    )
    (source / "financial-reconciliation.json").write_text(
        json.dumps(
            {
                "final_cash": 471492,
                "freight_revenue": 1018,
                "command_construction_purchase_costs": 28459,
                "unallocated_company_cash_decrease": 1067,
            }
        )
    )
    demo.show_results(source)
    text = capsys.readouterr().out
    assert "471492" in text and "1018" in text and "UNKNOWN" in text
    evaluation = json.loads((demo.SAMPLE.parent / "sample-report/evaluation.json").read_bytes())
    assert evaluation["verified_service_count"] == 3
    assert any(
        m["name"] == "delivered_cargo" and m["actual"] == "60" for m in evaluation["metrics"]
    )


def test_failed_preparation_disposes_its_unconsumed_workspace(tmp_path, monkeypatch):
    monkeypatch.setattr(demo, "check", lambda **kwargs: None)
    monkeypatch.setattr(demo, "RUNS", tmp_path)
    created = []

    def prepare(root, **kwargs):
        workspace = demo.RuntimeWorkspace.create(root / "isolated", retain=True)
        (workspace.root / ".admin-secret").write_text("controlled test secret")
        created.append(workspace.root)
        raise ValueError("controlled staging failure")

    monkeypatch.setattr(native, "prepare", prepare)
    assert demo.main(["run", "--headless"]) == 1
    assert created and not created[0].exists()


def test_public_run_uses_fresh_identity_existing_executor_and_p07(tmp_path, monkeypatch):
    monkeypatch.setattr(demo, "check", lambda **kwargs: None)
    monkeypatch.setattr(demo, "RUNS", tmp_path)
    calls = []

    def prepare(root, **kwargs):
        assert root.parent == tmp_path
        assert root.name.startswith("playable-demo-")
        assert native.attempt_number(root) == 1
        assert kwargs == dict(
            demo=True,
            planner=True,
            network=True,
            scenario="high-budget-500k",
            network_service_limit=3,
            loop_cycles=1,
        )
        root.mkdir()
        return SimpleNamespace(directory=root)

    async def run(prepared, **kwargs):
        assert set(kwargs) == {"on_ready", "on_delivered", "on_closing"}
        calls.append("existing-native-runner")
        return {"status": "NATIVE_MULTI_SERVICE_DELIVERY_VERIFIED"}

    def report(source, output):
        calls.append("p07")
        assert output != source and not output.is_relative_to(source)

    monkeypatch.setattr(native, "prepare", prepare)
    monkeypatch.setattr(native, "run", run)
    monkeypatch.setattr(demo, "report", report)
    assert demo.main(["run", "--headless", "--stop-on-delivery"]) == 0
    assert calls == ["existing-native-runner", "p07"]


# --- GUI product scope (spec §1/§3.3, E148 owed element; offline typing) ----


def test_viewer_types_the_operator_window_close_as_the_soft_end(tmp_path):
    backend = SimpleNamespace(client_soft=None)
    viewer = demo.Viewer(tmp_path, headless=False, view_seconds=0)
    viewer.backend = backend
    viewer.process = SimpleNamespace(returncode=0, poll=lambda: 0)  # ty: ignore[invalid-assignment]
    with pytest.raises(native.OperatorWindowClosed) as soft:
        asyncio.run(viewer.progress(tmp_path))
    message = "spectator window closed by operator (client exited 0)"
    assert str(soft.value) == message
    assert backend.client_soft == message

    viewer.process = SimpleNamespace(returncode=7, poll=lambda: 7)  # ty: ignore[invalid-assignment]
    backend.client_soft = None
    with pytest.raises(RuntimeError) as crash:
        viewer.check_client_exit()
    assert type(crash.value) is RuntimeError
    assert str(crash.value) == f"Graphical client exited (7); see {tmp_path / 'client/client.log'}"
    assert backend.client_soft is None


def _soft_end_harness(tmp_path, monkeypatch, calls):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    keys = tmp_path / ".admin-secret"
    keys.write_bytes(native.AuthorizedKey.generate()._secret)
    workspace = tmp_path / "workspace"
    prepared = SimpleNamespace(
        directory=tmp_path,
        key_path=keys,
        endpoints=(1, 2),
        spec=SimpleNamespace(
            workspace=SimpleNamespace(
                root=workspace, logs=tmp_path / "logs", close=lambda: shutil.rmtree(workspace)
            )
        ),
    )

    @dataclass
    class Welcome:
        revision: str = "15.3"
        seed: int = 42
        width: int = 64
        height: int = 64

    class Session:
        welcome = Welcome()
        protocol = object()
        state = native.AuthState.ACTIVE

        @classmethod
        async def connect_secure(cls, *args, **kwargs):
            calls.append("secure-connect")
            return cls()

        async def authenticate(self, *args, **kwargs):
            pass

    class Backend:
        process = None
        planning_read_count = 0

        async def launch(self, p):
            self.process = object()
            calls.append("server-start")

        async def cleanup(self, p):
            calls.append("server-close")
            return dict(reaped=True, cleanup_error=[], sockets_closed=True)

    async def noop(*args, **kwargs):
        pass

    return prepared, Session, Backend, noop


def test_operator_window_close_gates_the_attempt_at_the_exchange_boundary(tmp_path, monkeypatch):
    calls = []
    prepared, Session, Backend, noop = _soft_end_harness(tmp_path, monkeypatch, calls)
    (tmp_path / "PRELAUNCH.json").write_text(json.dumps(dict(budgets={"total_seconds": 5})))

    async def ready(backend, p):
        calls.append("client-ready")
        backend.client_soft = "spectator window closed by operator (client exited 0)"

    monkeypatch.setattr(native, "preflight", lambda _: None)
    monkeypatch.setattr(native, "backend_for", lambda _: Backend())
    monkeypatch.setattr(native, "DeliverySession", Session)
    monkeypatch.setattr(native, "GameScriptTransport", lambda *a: SimpleNamespace(subscribe=noop))
    monkeypatch.setattr(native, "wait_log", noop)
    monkeypatch.setattr(native, "save", noop)
    monkeypatch.setattr(native, "verify_cleanup_endpoints", lambda *a: {})
    result = asyncio.run(native.run(prepared, on_ready=ready))
    assert result["status"] == "ENDED_BY_OPERATOR"
    assert result["operator_soft_end"] == "spectator window closed by operator (client exited 0)"
    assert "error" not in result
    assert result["launches"] == 1 and result["connections"] == 1 and result["requests"] == 0
    assert calls.index("client-ready") < calls.index("server-close")
    assert not (tmp_path / "workspace").exists()
    stored = json.loads((tmp_path / "result.json").read_text())
    assert stored["status"] == "ENDED_BY_OPERATOR"
    assert (tmp_path / "cleanup.json").is_file()
    assert (tmp_path / "artifact-manifest.sha256").is_file()


def test_operator_soft_end_surfaces_with_sealed_cleanup(tmp_path, monkeypatch):
    calls = []
    prepared, Session, Backend, noop = _soft_end_harness(tmp_path, monkeypatch, calls)
    (tmp_path / "PRELAUNCH.json").write_text(
        json.dumps(dict(demo=True, planner=True, network=True, budgets={"total_seconds": 5}))
    )

    async def execute(session, *args):
        calls.append("native-three-service-executor")
        raise native.OperatorWindowClosed("spectator window closed by operator (client exited 0)")

    async def ready(*args):
        calls.append("client-ready")

    async def delivered(*args):
        calls.append("delivery-view")

    async def closing(*args):
        calls.append("client-close")

    from app.simulation.openttd import freight_native_network

    monkeypatch.setattr(native, "preflight", lambda _: None)
    monkeypatch.setattr(native, "backend_for", lambda _: Backend())
    monkeypatch.setattr(
        native,
        "ScenarioPlanningAccounting",
        lambda _: SimpleNamespace(observe=lambda *a: None, enter=lambda *a: None),
    )
    monkeypatch.setattr(native, "PlannerDeliverySession", Session)
    monkeypatch.setattr(native, "GameScriptTransport", lambda *a: SimpleNamespace(subscribe=noop))
    monkeypatch.setattr(native, "wait_log", noop)
    monkeypatch.setattr(native, "save", noop)
    monkeypatch.setattr(native, "console", lambda *a: None)
    monkeypatch.setattr(native, "verify_cleanup_endpoints", lambda *a: {})
    monkeypatch.setattr(freight_native_network, "execute_network", execute)
    result = asyncio.run(
        native.run(prepared, on_ready=ready, on_delivered=delivered, on_closing=closing)
    )
    assert result["status"] == "ENDED_BY_OPERATOR"
    assert result["operator_soft_end"] == "spectator window closed by operator (client exited 0)"
    assert "error" not in result
    assert calls.index("client-close") < calls.index("server-close")
    assert calls.index("native-three-service-executor") < calls.index("client-close")
    assert not (tmp_path / "workspace").exists()
    stored = json.loads((tmp_path / "result.json").read_text())
    assert stored["status"] == "ENDED_BY_OPERATOR"
    assert (tmp_path / "cleanup.json").is_file()
    assert (tmp_path / "artifact-manifest.sha256").is_file()


def test_loop_cycle_recording_copies_the_graphics_identity_per_cycle(tmp_path, monkeypatch):
    """E150 pin: attempt 1 failed natively because the supplemental planning
    facts digest graphics-identity.json from the cycle dir, which was never
    copied per cycle; the recording now carries a content-identical copy."""
    calls = []
    prepared, Session, Backend, noop = _soft_end_harness(tmp_path, monkeypatch, calls)
    (tmp_path / "PRELAUNCH.json").write_text(
        json.dumps(
            dict(
                planner=True,
                network=True,
                loop_cycles=2,
                budgets={"total_seconds": 5, "requests": 10},
            )
        )
    )
    (tmp_path / "graphics-identity.json").write_text(json.dumps(dict(archive_sha256="a" * 64)))
    (tmp_path / "PRELAUNCH.sha256").write_text(native.sha256(tmp_path / "PRELAUNCH.json") + "\n")
    (tmp_path / "frozen-source.zip").write_bytes(b"pin")

    async def execute_network(*args, **kwargs):
        calls.append("cycle-execute-start")
        assert kwargs.get("exclude", ()) == () and kwargs.get("foreign_plans", ()) == ()
        raise RuntimeError("pin: cycle recording carries the projection of record")

    monkeypatch.setattr(native, "preflight", lambda _: None)
    monkeypatch.setattr(native, "backend_for", lambda _: Backend())
    monkeypatch.setattr(
        native,
        "ScenarioPlanningAccounting",
        lambda _: SimpleNamespace(observe=lambda *a: None, enter=lambda *a: None),
    )
    monkeypatch.setattr(native, "PlannerDeliverySession", Session)
    monkeypatch.setattr(native, "GameScriptTransport", lambda *a: SimpleNamespace(subscribe=noop))
    monkeypatch.setattr(native, "wait_log", noop)
    monkeypatch.setattr(native, "save", noop)
    monkeypatch.setattr(native, "verify_cleanup_endpoints", lambda *a: {})
    from app.simulation.openttd import freight_native_network

    monkeypatch.setattr(freight_native_network, "execute_network", execute_network)
    result = asyncio.run(native.run(prepared))
    assert result["status"] == "FAILED"
    assert "pin: cycle recording carries the projection of record" in result["error"]
    assert calls == ["server-start", "secure-connect", "cycle-execute-start", "server-close"]
    cycle_dir = tmp_path / "loop-cycle-1"
    assert not (tmp_path / "loop-cycle-2").exists()
    for name in (
        "PRELAUNCH.json",
        "PRELAUNCH.sha256",
        "CLAIM.json",
        "frozen-source.zip",
        "graphics-identity.json",
    ):
        assert (cycle_dir / name).is_file()
        assert (cycle_dir / name).read_bytes() == (tmp_path / name).read_bytes()
    assert json.loads((cycle_dir / "loop-cycle.json").read_text())["loop_cycles"] == 2
    stored = json.loads((tmp_path / "result.json").read_text())
    assert stored["status"] == "FAILED"
    assert (tmp_path / "cleanup.json").is_file()


def test_closing_during_the_view_hold_ends_softly_after_a_verified_delivery(tmp_path, capsys):
    viewer = demo.Viewer(tmp_path, headless=False, view_seconds=5)
    polls = {"n": 0}

    class HoldProcess:
        returncode = None

        def poll(self):
            polls["n"] += 1
            return 0 if polls["n"] > 1 else None

    viewer.process = HoldProcess()  # ty: ignore[invalid-assignment]
    directory = tmp_path / "run"
    directory.mkdir()
    (directory / "receipt.json").write_bytes(
        json.dumps(
            {"services": [{"source": 4, "destination": 5, "delivered": 20, "payment_income": 341}]}
        ).encode()
    )
    (directory / "financial-reconciliation.json").write_bytes(
        json.dumps(
            {
                "final_cash": 471492,
                "freight_revenue": 1018,
                "command_construction_purchase_costs": 28459,
                "unallocated_company_cash_decrease": 1067,
            }
        ).encode()
    )
    backend = SimpleNamespace(health=lambda: None)
    asyncio.run(viewer.delivered(backend, SimpleNamespace(directory=directory)))
    assert "Deliveries complete" in capsys.readouterr().out


def test_run_demo_maps_the_operator_soft_end_to_a_clean_zero_exit(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(demo, "check", lambda **kwargs: None)
    monkeypatch.setattr(demo, "RUNS", tmp_path)

    def prepare(root, **kwargs):
        return SimpleNamespace(directory=root)

    async def run(prepared, **kwargs):
        assert set(kwargs) == {"on_ready", "on_delivered", "on_closing"}
        return dict(
            status="ENDED_BY_OPERATOR",
            operator_soft_end="spectator window closed by operator (client exited 0)",
        )

    monkeypatch.setattr(native, "prepare", prepare)
    monkeypatch.setattr(native, "run", run)
    assert demo.main(["run", "--headless", "--stop-on-delivery"]) == 0
    assert "ended-by-operator" in capsys.readouterr().out
