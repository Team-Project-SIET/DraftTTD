"""Public OpenTTD 15.3 demo: check, plan offline, or run a visible local game."""

import argparse
import asyncio
import json
import os
import shutil
import subprocess
import sys
import uuid
from pathlib import Path

from app.demo_operations import (
    compare_operational_reports,
    operational_snapshot,
    terminal_status,
    write_operational_report,
)
from app.demo_random import (
    DemoBudgets,
    RandomWorldSettings,
    diagnostic_status,
    prepare_random,
)
from app.simulation.openttd.proof import freight_delivery as native
from app.simulation.openttd.proof.harness import BINARY_SHA256, PROJECT, sha256
from app.simulation.openttd.runtime.config import RuntimeWorkspace

BINARY = native.BINARY

SAMPLE = PROJECT / "examples/openttd-demo/scenario.json"
RUNS = PROJECT / "artifacts/demos"


def check(*, graphical=True):
    if not BINARY.is_file() or sha256(BINARY) != BINARY_SHA256:
        raise ValueError(f"Install the pinned OpenTTD 15.3 binary at {BINARY}")
    if (
        not native.GRAPHICS_ARCHIVE.is_file()
        or sha256(native.GRAPHICS_ARCHIVE) != native.ARCHIVE_SHA256
    ):
        raise ValueError(f"Pinned OpenGFX archive missing or changed: {native.GRAPHICS_ARCHIVE}")
    if graphical and not (os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY")):
        raise ValueError(
            "No graphical desktop detected; run from a desktop terminal or use --headless"
        )


def selections(directory):
    plan = json.loads((directory / "execution-plan.json").read_bytes())
    scenario = json.loads((directory / "planning-scenario.json").read_bytes())
    demands = {d["demand_id"]: d for d in scenario["cargo_demands"]}
    rows = []
    for index, route in enumerate(plan["routes"], 1):
        assignment = route["cargo_assignments"][0]
        d = demands[assignment["demand_id"]]
        rows.append(
            f"Service {index}: {d['origin_id']} -> {d['destination_id']}, "
            f"{assignment['quantity']} cargo units"
        )
    return rows


def show_results(directory):
    receipt = json.loads((directory / "receipt.json").read_bytes())
    print("\nVerified delivery batches:", flush=True)
    for index, service in enumerate(receipt["services"], 1):
        print(
            f"  Service {index} ({service['source']} -> {service['destination']}): "
            f"{service['delivered']} cargo; "
            f"revenue GBP {service['payment_income']}",
            flush=True,
        )
    finance = json.loads((directory / "financial-reconciliation.json").read_bytes())
    print(
        f"Cash GBP {finance['final_cash']}; revenue GBP {finance['freight_revenue']}; "
        f"construction/vehicles GBP {finance['command_construction_purchase_costs']}",
        flush=True,
    )
    print(
        f"Unallocated cash decrease GBP {finance['unallocated_company_cash_decrease']} "
        "(expense category UNKNOWN)",
        flush=True,
    )
    print("Operating costs / ROI: UNKNOWN. These are short delivery batches.", flush=True)


def pipeline_stage(directory, elapsed=0.0):
    """Furthest completed backend stage, from the progress markers the native
    runner already writes between exchanges. The watcher prints this instead of
    a static waiting line, so a slow or blocked run names its exact stage and
    keeps the honest ``operational samples UNKNOWN`` label until a plan exists.
    Markers are staged non-atomically of record: a mid-write file reads as
    absent or malformed and is retried on the next watcher tick."""
    diagnostic = directory / "planning-diagnostic.json"
    if diagnostic.is_file():
        try:
            value = json.loads(diagnostic.read_bytes())
        except json.JSONDecodeError:
            return None
        return "FAILED: " + diagnostic_status(value)
    if (directory / "qualified.sav").is_file():
        return (
            "Qualified world saved; P05 bounded optimizer selecting services; "
            f"elapsed {elapsed:.0f}s; operational samples UNKNOWN."
        )
    candidates = directory / "network-candidates.json"
    if candidates.is_file():
        try:
            total = len(json.loads(candidates.read_bytes())["relationships"])
            captured = len(list(directory.glob("network-facts-*.json")))
        except json.JSONDecodeError, KeyError, TypeError:
            pass
        else:
            return (
                f"Capturing bounded planning facts {captured}/{total} relationships; "
                f"elapsed {elapsed:.0f}s; operational samples UNKNOWN."
            )
    for message, markers in (
        (
            "World qualified; P08 bounded relationship discovery running",
            ("qualification-session.json", "world-planning-observation.json"),
        ),
        (
            "Qualification running; native economy-month rollover waits",
            ("qualification-log-window.json",),
        ),
        ("World launched; qualification preparing", ("before.sav",)),
        ("Run claimed; native world launching", ("CLAIM.json",)),
    ):
        if any((directory / marker).is_file() for marker in markers):
            return f"{message}; elapsed {elapsed:.0f}s; operational samples UNKNOWN."
    return f"Staging the native run; elapsed {elapsed:.0f}s; operational samples UNKNOWN."


class Viewer:
    """Own only the GUI client launched for this run; never touch a user's client."""

    def __init__(self, root, *, headless, view_seconds):
        self.root = root
        self.headless = headless
        self.view_seconds = view_seconds
        self.process = None
        self.log = None
        self.watcher = None
        self.backend = None

    async def ready(self, backend, prepared):
        self.backend = backend
        self.watcher = asyncio.create_task(self.progress(prepared.directory))
        if self.headless:
            print("Headless mode: GUI/playability is not being tested.", flush=True)
            return
        client = self.root / "client"
        client.mkdir()
        # Isolate client settings and content from both server secrets and user profile.
        shutil.copytree(prepared.spec.workspace.root / "baseset", client / "baseset")
        cfg = client / "openttd.cfg"
        cfg.write_text(
            "[misc]\ngraphicsset = OpenGFX\n[network]\nclient_name = Python Demo Viewer\n"
        )
        self.log = (client / "client.log").open("wb")
        self.process = subprocess.Popen(
            [
                str(BINARY),
                "-c",
                str(cfg),
                "-x",
                "-X",
                "-n",
                f"127.0.0.1:{prepared.endpoints[0]}#255",
            ],
            cwd=client,
            stdout=self.log,
            stderr=subprocess.STDOUT,
        )
        await asyncio.sleep(1)
        self.require_alive()
        print(
            "GUI client started (connection/visibility requires live verification). "
            "Inspect vehicles, stations and company finances as a spectator. "
            "Use Multiplayer to create a separate company for manual building.",
            flush=True,
        )

    def require_alive(self):
        if self.process is not None and self.process.poll() is not None:
            raise RuntimeError(
                f"Graphical client exited ({self.process.returncode}); "
                f"see {self.root / 'client/client.log'}"
            )

    def check_client_exit(self):
        """Typed client-exit classification of record (spec §1/§3.3): the
        operator's window close is the soft ended-by-operator end; a crashed
        client stays the honest typed failure of E140's shape."""
        code = None if self.process is None else self.process.poll()
        if code is None:
            return
        if code == 0:
            message = "spectator window closed by operator (client exited 0)"
            if self.backend is not None:
                self.backend.client_soft = message
            raise native.OperatorWindowClosed(message)
        raise RuntimeError(
            f"Graphical client exited ({code}); see {self.root / 'client/client.log'}"
        )

    async def progress(self, directory):
        started = asyncio.get_running_loop().time()
        shown = set()
        service_count = 0
        previous_status = None
        last_status_time = 0.0
        while True:
            self.check_client_exit()
            if "plan" not in shown:
                try:
                    rows = selections(directory)
                except FileNotFoundError, json.JSONDecodeError:
                    pass
                else:
                    print("\nP08/P05 selected:\n  " + "\n  ".join(rows), flush=True)
                    shown.add("plan")
                    service_count = len(rows)
            for n in range(service_count):
                path = directory / f"service-receipt-{n}.json"
                if n not in shown and path.exists():
                    try:
                        row = json.loads(path.read_bytes())
                    except json.JSONDecodeError:
                        continue
                    print(
                        f"Service {n + 1} delivered: "
                        f"{row['delivered']} cargo, GBP {row['payment_income']}",
                        flush=True,
                    )
                    shown.add(n)
            if service_count:
                snapshot = operational_snapshot(directory, service_count)
                status = terminal_status(snapshot)
                now = asyncio.get_running_loop().time()
                if status != previous_status or now - last_status_time >= 10:
                    print(status, flush=True)
                    previous_status = status
                    last_status_time = now
            elif asyncio.get_running_loop().time() - last_status_time >= 10:
                now = asyncio.get_running_loop().time()
                stage = pipeline_stage(directory, now - started)
                if stage is not None:
                    print(stage, flush=True)
                    last_status_time = now
            await asyncio.sleep(0.5)

    async def delivered(self, backend, prepared):
        if self.watcher is not None and self.watcher.done():
            await self.watcher  # Surface a client startup/runtime failure.
        self.check_client_exit()
        show_results(prepared.directory)
        if self.headless or self.view_seconds == 0:
            return
        print(
            f"Deliveries complete. Game stays open for up to {self.view_seconds}s. "
            "Close the client or press Ctrl+C to finish. "
            "Python's selected trucks are parked after their delivery batches.",
            flush=True,
        )
        if self.process is None:
            raise RuntimeError("Graphical client was not started")
        deadline = asyncio.get_running_loop().time() + self.view_seconds
        while self.process.poll() is None and asyncio.get_running_loop().time() < deadline:
            backend.health()
            await asyncio.sleep(0.5)

    async def close(self):
        if self.watcher is not None:
            self.watcher.cancel()
            await asyncio.gather(self.watcher, return_exceptions=True)
        try:
            if self.process is not None:
                if self.process.poll() is None:
                    self.process.terminate()
                    try:
                        await asyncio.to_thread(self.process.wait, timeout=5)
                    except subprocess.TimeoutExpired:
                        self.process.kill()
                        await asyncio.to_thread(self.process.wait, timeout=5)
                else:
                    self.process.wait()
        finally:
            if self.log is not None:
                self.log.close()


def report(directory, output):
    from app.planning.network_cli import main as p07

    result = p07(
        [
            str(directory / "planning-scenario.json"),
            "--native-network-directory",
            str(directory),
            "--output",
            str(output),
        ]
    )
    if result:
        return result
    evaluation = json.loads((output / "evaluation.json").read_bytes())
    lines = [
        "# OpenTTD freight results",
        "",
        "P07 verified native delivery batches.",
        "",
        "| Metric | Actual | Unit |",
        "|---|---:|---|",
    ]
    for metric in evaluation["metrics"]:
        actual = metric["actual"] if metric["actual"] is not None else "UNKNOWN"
        lines.append(f"| {metric['name']} | {actual} | {metric['unit']} |")
    lines.extend(
        [
            "",
            "Services:",
            "",
            *("- " + row for row in selections(directory)),
            "",
            "These services ran serially. Full operating costs and ROI are UNKNOWN.",
            "Source: " + str(directory),
            "",
        ]
    )
    write_operational_report(directory, output, len(selections(directory)))
    lines.extend(["", "[Operational status and charts](operations.html)", ""])
    (output / "results.md").write_text("\n".join(lines))
    return result


def run_demo(
    *, headless=False, view_seconds=120, random_world=None, random_budget=None, loop_cycles=1
):
    check(graphical=not headless)
    root = RUNS / ("playable-demo-" + uuid.uuid4().hex)
    if random_world is not None:
        print(
            f"Preparing native random 256x256 seed-{random_world['seed']} world. Run: {root}",
            flush=True,
        )
    else:
        print(f"Preparing deterministic seed-42, 64x64 freight world. Run: {root}", flush=True)
    try:
        prepared = native.prepare(
            root,
            demo=True,
            planner=True,
            network=True,
            scenario="high-budget-500k",
            network_service_limit=3,
            loop_cycles=loop_cycles,
            **(
                dict(random_world=random_world, random_budget=random_budget)
                if random_world is not None
                else {}
            ),
        )
        viewer = Viewer(root, headless=headless, view_seconds=view_seconds)
        result = asyncio.run(
            native.run(
                prepared,
                on_ready=viewer.ready,
                on_delivered=viewer.delivered,
                on_closing=viewer.close,
            )
        )
    except KeyboardInterrupt:
        print(f"Stopped. Partial observations and cleanup: {root}", flush=True)
        return 130
    finally:
        # Preparation/preflight failures occur before the native runner owns cleanup.
        if not (root / "CLAIM.json").exists():
            for workspace in (root / "isolated").glob("openttd-15.3-*"):
                RuntimeWorkspace.reopen(workspace).close()
    if result["status"] == "NATIVE_MULTI_SERVICE_DELIVERY_VERIFIED":
        output = RUNS / (root.name + "-report")
        if report(root, output):
            print(f"P07 report verification failed: {output}", file=sys.stderr)
            return 1
        print(f"P07 results: {output / 'results.md'}\nGame save: {root / 'after.sav'}", flush=True)
        return 0
    if result["status"] in ("NATIVE_LOOP_DELIVERED_VERIFIED", "NATIVE_LOOP_ZERO_SERVICES"):
        # Spec §3.6: every cycle keeps its own receipt set and report; the run
        # summary at the root indexes the cycles.
        output = RUNS / (root.name + "-loop-report")
        output.mkdir()
        lines = ["# Loop run cycles", "", "| Cycle | Status | Selected |", "|---|---|---|"]
        for entry in result.get("loops", []):
            cycle_dir = root / f"loop-cycle-{entry['cycle']}"
            if (cycle_dir / "receipt.json").is_file():
                if report(cycle_dir, output / f"cycle-{entry['cycle']}"):
                    print(
                        f"P07 report verification failed: {output / f'cycle-{entry["cycle"]}'}",
                        file=sys.stderr,
                    )
                    return 1
            selected = ", ".join(entry.get("selected", [])) if "selected" in entry else "—"
            abandoned = " (abandoned world)" if entry.get("abandoned_world") else ""
            lines.append(f"| {entry['cycle']} | {entry['status']}{abandoned} | {selected} |")
        (output / "loops.md").write_text("\n".join(lines) + "\n")
        print(f"Loop results: {output / 'loops.md'}", flush=True)
        return 0 if result["status"] == "NATIVE_LOOP_DELIVERED_VERIFIED" else 1
    if result["status"] == "ENDED_BY_OPERATOR":
        print(
            f"Spectator window closed by operator; run ended softly "
            f"(ended-by-operator, never a system failure). "
            f"Sealed receipts and cleanup records: {root}",
            flush=True,
        )
        return 0
    print(f"Demo failed: {result.get('error', result['status'])}. Logs: {root}", file=sys.stderr)
    return 1


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command", choices=("check", "plan", "run", "report", "compare"), nargs="?", default="run"
    )
    parser.add_argument("--headless", action="store_true", help="Server only; no GUI validation")
    parser.add_argument(
        "--view-seconds",
        type=int,
        default=120,
        help="Keep game open after all selected deliveries (0..300 seconds)",
    )
    parser.add_argument(
        "--stop-on-delivery",
        action="store_true",
        help="Close after all selected services deliver; no viewing hold",
    )
    parser.add_argument(
        "--random-world",
        action="store_true",
        help="Use the bounded native 256x256 random-world profile",
    )
    parser.add_argument("--seed", type=int)
    parser.add_argument("--map-size", type=int, choices=(256,))
    parser.add_argument("--climate", choices=("temperate", "arctic", "tropic", "toyland"))
    parser.add_argument("--terrain", type=int, choices=range(6))
    parser.add_argument("--towns", type=int, choices=range(4))
    parser.add_argument("--industries", type=int, choices=range(5))
    parser.add_argument("--max-services", type=int)
    parser.add_argument("--max-vehicles", type=int)
    parser.add_argument("--max-candidates", type=int)
    parser.add_argument("--planning-seconds", type=int)
    parser.add_argument(
        "--capture-tiles",
        type=int,
        choices=(256, 512, 2048),
        default=2048,
        help="Widened ramrom capture seal of record (2048); 512 pins the legacy demo shape",
    )
    parser.add_argument(
        "--capture-seconds",
        type=int,
        default=120,
        help="Capture wall-clock budget per relationship (1..180 seconds)",
    )
    parser.add_argument(
        "--capture-pad",
        type=int,
        default=6,
        help="Extra growth per side on the shorter capture axis, 2048 profile (0..32)",
    )
    parser.add_argument(
        "--cycles",
        type=int,
        default=1,
        help="Sealed loop cycles for the ramrom loop product (1..8; requires --random-world)",
    )
    parser.add_argument(
        "--source", type=Path, help="Existing demo evidence directory, for offline report only"
    )
    parser.add_argument(
        "--compare-with", type=Path, nargs="+", help="Additional P07 report directories"
    )
    args = parser.parse_args(argv)
    if not 0 <= args.view_seconds <= 300:
        parser.error("--view-seconds must be between 0 and 300")
    random_values = (
        args.seed,
        args.map_size,
        args.climate,
        args.terrain,
        args.towns,
        args.industries,
        args.max_services,
        args.max_vehicles,
        args.max_candidates,
        args.planning_seconds,
    )
    capture_nondefault = (
        args.capture_tiles != 2048 or args.capture_seconds != 120 or args.capture_pad != 6
    )
    if (any(v is not None for v in random_values) or capture_nondefault) and not args.random_world:
        parser.error("world/planner settings require --random-world")
    if not 1 <= args.capture_seconds <= 180:
        parser.error("--capture-seconds must be between 1 and 180")
    if not 0 <= args.capture_pad <= 32:
        parser.error("--capture-pad must be between 0 and 32")
    if not 1 <= args.cycles <= 8:
        parser.error("--cycles must be between 1 and 8")
    if args.cycles > 1 and not args.random_world:
        parser.error("--cycles greater than 1 requires --random-world")
    if args.source is not None and args.command not in ("report", "compare"):
        parser.error("--source is only valid with report/compare")
    if args.command == "report" and (args.source is None or args.random_world):
        parser.error("report requires --source and cannot use --random-world")
    if args.compare_with is not None and args.command != "compare":
        parser.error("--compare-with is only valid with compare")
    if args.command == "compare" and (
        args.source is None or not args.compare_with or args.random_world
    ):
        parser.error("compare requires --source and --compare-with; no --random-world")
    try:
        if args.command == "compare":
            output = RUNS / ("comparison-" + uuid.uuid4().hex)
            compare_operational_reports([args.source, *args.compare_with], output)
            print(f"Comparison: {output / 'comparison.html'}")
            return 0
        if args.command == "report":
            output = RUNS / ("offline-report-" + uuid.uuid4().hex)
            result = report(args.source.resolve(), output)
            print(f"Report: {output / 'results.md'}")
            return result
        if args.random_world:
            settings = RandomWorldSettings(
                **{
                    k: v
                    for k, v in dict(
                        seed=args.seed,
                        map_size=args.map_size,
                        climate=args.climate,
                        terrain=args.terrain,
                        towns=args.towns,
                        industries=args.industries,
                    ).items()
                    if v is not None
                }
            )
            budgets = DemoBudgets(
                **{
                    k: v
                    for k, v in dict(
                        max_services=args.max_services,
                        max_vehicles=args.max_vehicles,
                        max_relationships=args.max_candidates,
                        planning_seconds=args.planning_seconds,
                        capture_tile_limit=args.capture_tiles,
                        capture_seconds=args.capture_seconds,
                        capture_edge_pad=args.capture_pad,
                    ).items()
                    if v is not None
                }
            )
            if args.command == "run":
                return run_demo(
                    headless=args.headless,
                    view_seconds=0 if args.stop_on_delivery else args.view_seconds,
                    random_world=settings.model_dump(),
                    random_budget=budgets.model_dump(),
                    loop_cycles=args.cycles,
                )
            if args.command == "check":
                check(graphical=not args.headless)
                print(
                    "Random settings and prerequisites validated; "
                    "no world generated or game launched."
                )
                return 0
            output = RUNS / ("random-preparation-" + uuid.uuid4().hex)
            prepare_random(output, settings, budgets)
            print(
                f"PREPARED_RECIPE_ONLY: {output}; no world generated or plan selected. "
                "Planning requires observed state from a separately authorized native run."
            )
            return 0
        if args.command == "check":
            check(graphical=not args.headless)
            print("Binary, assets and desktop prerequisites found; no game launched.")
            return 0
        if args.command == "plan":
            from app.planning.network_cli import main as planner

            output = RUNS / ("offline-plan-" + uuid.uuid4().hex)
            return planner([str(SAMPLE), "--output", str(output)])
        return run_demo(
            headless=args.headless, view_seconds=0 if args.stop_on_delivery else args.view_seconds
        )
    except (OSError, ValueError, RuntimeError) as error:
        print(f"Demo startup/run failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
