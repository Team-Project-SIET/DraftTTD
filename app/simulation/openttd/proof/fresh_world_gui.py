"""T-036 fresh-world GUI native probe family (T-035 follow-up, independent).

T-035 proved the GUI probe guarantees over the frozen demo-lane world (the
E2 canonical save). This follow-up proves them over a world generated fresh
at attempt time, in TWO separately authorized attempts:

1. `fresh-world-create-*`: ONE dedicated-server launch generates a NEW world
   from the explicit seed and map parameters of record (`-g <flat
   heightmap> -G <seed>` + the proven [game_creation] config; native marker
   "Map generated, starting game"), then console-saves it into the attempt
   directory where its digest is pinned (world.json). No admin connection,
   no canonical input, no bridge staged.
2. `fresh-world-gui-probe-*`: the byte-pinned bridge host launches from the
   digest-pinned fresh save, the runtime welcome frame must report the fresh
   seed and map size (the demo lane's seed 42 refuses typed), and a real
   desktop GUI client joins the running fresh world as a spectator (the
   T-035 join machinery, verified server-side).

No canonical/demo world input exists anywhere in this family: the creation
stage accepts none structurally, the GUI stage refuses any directory that is
not the verified fresh creation attempt, and preflight refuses canonical
keys. Both stages keep the T-035 guarantees (one-shot authorization, owned
processes, AdminPort isolation, sealed receipts, owned cleanup, manifest,
typed verify). T-035's sealed evidence is untouched and stays terminal
VERIFIED.
"""

import asyncio
import json
import os
import shutil
import sys
import zipfile
from dataclasses import asdict
from pathlib import Path
from types import SimpleNamespace

from app.simulation.openttd.admin_crypto import AuthorizedKey
from app.simulation.openttd.runtime.base import LaunchSpecification
from app.simulation.openttd.runtime.config import AdminSettings, RuntimeWorkspace
from app.simulation.openttd.runtime.identity import RuntimeIdentity
from app.simulation.openttd.secure_admin import AuthState

from . import canonical_fleet as driver
from . import canonical_fleet_exercise as exercise
from . import canonical_fleet_gui as gui_probe
from . import freight_delivery as freight
from .endpoints import verify_cleanup_endpoints
from .graphics import stage_opengfx
from .harness import (
    BINARY_SHA256,
    PROJECT,
    EndpointReservation,
    PreparedProof,
    manifest,
    sha256,
    source_freeze,
    verify_freeze,
    write_json,
)
from .road_mutation import save, wait_log

FRESH_CREATE = "fresh-world-create-t036-3"
FRESH_GUI = "fresh-world-gui-probe-t036-2"
FRESH_CREATE_VERIFIED = "FRESH_WORLD_CREATE_VERIFIED"
FRESH_GUI_VERIFIED = "FRESH_WORLD_GUI_PROBE_VERIFIED"
SCHEMA = "fresh-world-prelaunch-v1"
FRESH_GUI_CLIENT_SCHEMA = "fresh-world-gui-client-v1"
GENERATION_MARKER = "Map generated, starting game"

# World generation parameters of record. A change here is a source change and
# therefore a new staging identity, never a runtime flag.
FRESH_SEED = 1181
FRESH_MAP_X = 6
FRESH_MAP_Y = 6
FRESH_WIDTH = 1 << FRESH_MAP_X
FRESH_HEIGHT = 1 << FRESH_MAP_Y
FRESH_LANDSCAPE = "temperate"
FRESH_STARTING_YEAR = 1950
DEMO_SEED = 42  # the demo-lane world's pin; refused typed at the welcome seam

CLIENT_NAME = "Fresh World GUI Probe"
JOIN_MARKER = f"*** {CLIENT_NAME} has joined the game"
JOIN_SECONDS = gui_probe.JOIN_SECONDS
OBSERVATION_SECONDS = gui_probe.OBSERVATION_SECONDS

# The GameScript of record is configured at GENERATION time: OpenTTD 15.3
# stores the GameScript selection inside the save itself (GSDT chunk), so a
# world generated without it never runs one and no runtime config append can
# inject it into a loaded save (the fresh-world-gui-probe-t036-1 FAILED
# round). Placement and case mirror the proven canonical-CREATE staging.
WORLD_SECTIONS = (
    "\n[misc]\ngraphicsset = OpenGFX\n[ai]\nai_in_multiplayer = true\n"
    "[game_scripts]\nRoadFreightProof = \n"
    "[game_creation]\n"
    f"map_x = {FRESH_MAP_X}\nmap_y = {FRESH_MAP_Y}\n"
    f"landscape = {FRESH_LANDSCAPE}\nstarting_year = {FRESH_STARTING_YEAR}\n"
    "land_generator = 1\nheightmap_height = 1\n"
    "tree_placer = 0\namount_of_rivers = 0\n[difficulty]\nnumber_towns = 4\n"
    "industry_density = 0\nmax_no_competitors = 0\n"
    "vehicle_breakdowns = 0\ndisasters = false\n"
    "infinite_money = false\n[economy]\ntimekeeping_units = 0\n"
    "multiple_industry_per_town = true\n"
    "[newgrf]\n[company]\nengine_renew = false\n"
    "[construction]\ncommand_pause_level = 3\n"
)

WORLD_GENERATION = dict(
    argv_shape="-g <workspace>/heightmap.png -G <seed of record>",
    seed=FRESH_SEED,
    map_x=FRESH_MAP_X,
    map_y=FRESH_MAP_Y,
    landscape=FRESH_LANDSCAPE,
    starting_year=FRESH_STARTING_YEAR,
    heightmap="flat 64x64 grayscale 1 (freight.flat_heightmap)",
    demo_world_forbidden="seed 42 or any canonical save must never be generated, loaded or copied",
)

CREATE_CONTRACT = dict(
    mode="fresh-world-create",
    purchase=False,
    dispatch=False,
    unpause=False,
    world_state="newly generated from the explicit seed of record",
    generation=WORLD_GENERATION,
    save="fresh-world (owned console save in this attempt directory, digest-pinned)",
    receipts="world generation + native save digest; no Phase B ticket receipts",
)

GUI_CONTRACT = dict(
    mode="fresh-world-gui-probe",
    purchase=False,
    dispatch=False,
    unpause=False,
    world_state="running fresh generated world (the digest-pinned fresh-world.sav)",
    welcome=dict(revision="15.3", seed=FRESH_SEED, width=FRESH_WIDTH, height=FRESH_HEIGHT),
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
    correspondence="none — a fresh world has no canonical observation to compare",
    receipts="welcome/seed identity + gui-client receipt; no Phase B ticket receipts",
)


def require_desktop_session():
    """Re-exported fail-closed display check (T-035 semantics, unchanged)."""
    return gui_probe.require_desktop_session()


def require_bridge_validation(package):
    """The staged byte pin owned by the q3-era exact 15.3 VM validation record."""
    return exercise.require_bridge_validation(package)


def expected_welcome():
    """The welcome identity of record, from the same constants the GUI
    contract pins (revision, seed, width, height)."""
    return ("15.3", FRESH_SEED, FRESH_WIDTH, FRESH_HEIGHT)


def require_fresh_welcome(welcome, expected):
    """The runtime no-fallback proof of record: the hosted world must report
    the fresh seed and map size of record; the demo lane's seed 42 (and any
    other world) refuses typed."""
    if (
        welcome is None
        or (welcome.revision, welcome.seed, welcome.width, welcome.height) != expected
    ):
        raise ValueError(
            "fresh-world secure runtime identity mismatch"
            " (a demo-lane or canonical world must never be hosted)"
        )
    return welcome


class FreshWorldBackend(freight.PlannerBackend):
    """The proven backend minus the canonical planning-frame wiring; the
    launch identity check is the fresh attempt's own sealed argv."""

    def validate_launch(self, prepared):
        metadata = json.loads((prepared.directory / "PRELAUNCH.json").read_bytes())
        if (
            prepared.spec.argv != tuple(metadata["argv"])
            or sha256(freight.BINARY) != BINARY_SHA256
            or freight.vehicle.matching_processes(freight.BINARY)
        ):
            raise ValueError("fresh-world native launch identity/ownership mismatch")


def _stage_fresh_workspace(directory, reservation):
    """Fresh RuntimeWorkspace + admin auth trio (the E169-proven staging) and
    the proven world-generation config sections of record."""
    workspace = RuntimeWorkspace.create(directory / "isolated", retain=True)
    secret = workspace.root / ".admin-secret"
    try:
        key = AuthorizedKey.generate()
        with os.fdopen(
            os.open(secret, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600), "wb"
        ) as stream:
            stream.write(key._secret)
        workspace.write_config(
            AdminSettings(
                password="",
                port=reservation.admin_port,
                game_port=reservation.game_port,
                authorized_public_key_hex=key.public_hex,
            )
        )
        config = workspace.config.read_text().replace(
            "pause_on_newgame = true", "pause_on_newgame = false"
        )
        config += WORLD_SECTIONS
        workspace.config.write_text(config)
    except BaseException:
        secret.unlink(missing_ok=True)
        workspace.close()
        raise
    return workspace, key, secret


def prepare_create(directory):
    if Path(directory).name != FRESH_CREATE:
        raise ValueError("exact fresh-world creation identity required")
    directory = Path(directory).resolve()
    directory.mkdir(parents=True, exist_ok=False)
    reservation = EndpointReservation.allocate()
    workspace = None
    secret = directory / "isolated" / ".admin-secret"
    try:
        workspace, key, secret = _stage_fresh_workspace(directory, reservation)
        (workspace.root / "heightmap.png").write_bytes(freight.flat_heightmap())
        shutil.copyfile(workspace.root / "heightmap.png", directory / "heightmap.png")
        # the byte-pinned bridge must exist at generation time: the scanner
        # resolves the [game_scripts] entry only from the runtime's game/ tree.
        package = driver.package_bytes()
        require_bridge_validation(package)
        target = workspace.game / "RoadFreightProof"
        target.mkdir()
        for name, data in package.items():
            (target / name).write_bytes(data)
        graphics = stage_opengfx(freight.GRAPHICS_ARCHIVE, workspace.root / "baseset/OpenGFX")
        write_json(
            directory / "graphics-identity.json",
            dict(asdict(graphics), directory=str(graphics.directory)),
        )
        shutil.copyfile(workspace.config, directory / "effective-openttd.cfg")
        endpoints = (reservation.game_port, reservation.admin_port)
        argv = freight.vehicle.load_argv(
            freight.BINARY.resolve(),
            workspace.config,
            reservation.game_port,
            workspace.root / "heightmap.png",
        ) + ("-G", str(FRESH_SEED))
        spec = LaunchSpecification(
            workspace,
            RuntimeIdentity(freight.BINARY.resolve(), "15.3", BINARY_SHA256),
            argv,
            workspace.root,
            workspace.environment,
            workspace.logs / "stdout.log",
            workspace.logs / "stderr.log",
        )
        frozen = source_freeze()
        frozen[str(freight.BINARY)] = sha256(freight.BINARY)
        for path in workspace.root.rglob("*"):
            if path.is_file() and path != secret:
                frozen[str(path.resolve())] = sha256(path)
        for path in directory.rglob("*"):
            if path.is_file() and path != secret:
                frozen[str(path.resolve())] = sha256(path)
        metadata = dict(
            schema=SCHEMA,
            qualification_id=FRESH_CREATE,
            execution_contract=CREATE_CONTRACT,
            workspace=str(workspace.root),
            argv=list(argv),
            binary=str(freight.BINARY),
            public_key=key.public_hex,
            game_port=reservation.game_port,
            admin_port=reservation.admin_port,
            bridge_sha256=driver.bridge_digest(package),
            frozen=frozen,
            world_generation=WORLD_GENERATION
            | dict(heightmap_sha256=sha256(directory / "heightmap.png")),
            configuration_sha256=driver.configuration_digest(workspace.config),
            budgets=dict(total_seconds=300),
            authorization=(
                "separate explicit authorization; ONE dedicated-server launch; NO admin"
                " connection; the generated world is console-saved into this attempt"
                " directory and digest-pinned; no retry; stop on unexpected failure"
            ),
        )
        write_json(directory / "PRELAUNCH.json", metadata)
        (directory / "PRELAUNCH.sha256").write_text(sha256(directory / "PRELAUNCH.json") + "\n")
        return PreparedProof(directory, spec, secret, key.public_hex, endpoints)
    except BaseException:
        if secret.is_file():
            secret.unlink()
        if workspace is not None:
            workspace.close()
        raise
    finally:
        reservation.close()


def preflight_create(prepared):
    directory = prepared.directory
    metadata = json.loads((directory / "PRELAUNCH.json").read_bytes())
    if (
        metadata["qualification_id"] != FRESH_CREATE
        or directory.name != FRESH_CREATE
        or metadata["schema"] != SCHEMA
        or (directory / "CLAIM.json").exists()
        or sha256(directory / "PRELAUNCH.json")
        != (directory / "PRELAUNCH.sha256").read_text().strip()
    ):
        raise ValueError("fresh-world sealed identity/claim mismatch")
    exercise.require_contract(metadata, CREATE_CONTRACT)
    verify_freeze(metadata["frozen"])
    if (
        driver.configuration_digest(prepared.spec.workspace.config)
        != metadata["configuration_sha256"]
    ):
        raise ValueError("fresh-world configuration mismatch")
    if "canonical_directory" in metadata or "canonical_save_sha256" in metadata:
        raise ValueError("fresh-world creation must never stage canonical evidence")
    if sha256(directory / "heightmap.png") != metadata["world_generation"]["heightmap_sha256"]:
        raise ValueError("fresh-world heightmap drift")
    backend = FreshWorldBackend(authorized_one_launch=True)
    backend.preflight(prepared)
    backend.validate_launch(prepared)
    reservation = EndpointReservation.allocate(*prepared.endpoints)
    reservation.close()
    return metadata


def verify_fresh_creation(directory):
    """Accept only an immutable successful fresh-world creation attempt; any
    other directory (including the canonical demo evidence) refuses typed."""
    directory = Path(directory)
    if directory.name != FRESH_CREATE:
        raise ValueError("fresh-world creation evidence required (never the canonical demo world)")
    directory = directory.resolve()
    metadata = json.loads((directory / "PRELAUNCH.json").read_bytes())
    result = json.loads((directory / "result.json").read_bytes())
    cleanup = json.loads((directory / "cleanup.json").read_bytes())
    world = json.loads((directory / "world.json").read_bytes())
    if (
        metadata["qualification_id"] != FRESH_CREATE
        or metadata["schema"] != SCHEMA
        or sha256(directory / "PRELAUNCH.json")
        != (directory / "PRELAUNCH.sha256").read_text().strip()
        or not (directory / "CLAIM.json").is_file()
        or result.get("status") != FRESH_CREATE_VERIFIED
        or result.get("launches") != 1
        or result.get("connections") != 0
        or not all(
            cleanup.get(k) is True
            for k in ("reaped", "workspace_disposed", "credential_removed", "sockets_closed")
        )
        or cleanup.get("cleanup_error")
        or cleanup.get("remaining_processes")
        or manifest(directory) != (directory / "artifact-manifest.sha256").read_text()
        or world["world_generation"]["seed"] != FRESH_SEED
        or world["fresh_save_sha256"] != sha256(directory / "fresh-world.sav")
    ):
        raise ValueError("fresh-world creation evidence required (never the canonical demo world)")
    return world


def prepare_gui(directory, *, fresh_world):
    require_desktop_session()
    if Path(directory).name != FRESH_GUI:
        raise ValueError("exact fresh-world GUI probe identity required")
    if fresh_world is None:
        raise ValueError("gui stage requires fresh-world creation evidence")
    world = verify_fresh_creation(fresh_world)
    package = driver.package_bytes()
    require_bridge_validation(package)
    directory = Path(directory).resolve()
    directory.mkdir(parents=True, exist_ok=False)
    reservation = EndpointReservation.allocate()
    workspace = None
    secret = directory / "isolated" / ".admin-secret"
    try:
        workspace, key, secret = exercise.stage_workspace(
            directory, canonical=Path(fresh_world), reservation=reservation
        )
        # mirror of the E167 fix line with the FRESH save as the source:
        # preflight and the -g launch argv both resolve this exact path.
        shutil.copyfile(Path(fresh_world) / "fresh-world.sav", workspace.root / "source.sav")
        # The staged save carries the GameScript of record (GSDT chunk): the
        # byte-pinned bridge package is staged only so the scanner can resolve
        # the saved GameScript name; a runtime config append can never inject
        # a GameScript into a loaded save. Its ready marker still gates the
        # admin connection.
        target = workspace.game / "RoadFreightProof"
        target.mkdir()
        for name, data in package.items():
            (target / name).write_bytes(data)
        graphics = stage_opengfx(freight.GRAPHICS_ARCHIVE, workspace.root / "baseset/OpenGFX")
        write_json(
            directory / "graphics-identity.json",
            dict(asdict(graphics), directory=str(graphics.directory)),
        )
        shutil.copyfile(workspace.config, directory / "effective-openttd.cfg")
        endpoints = (reservation.game_port, reservation.admin_port)
        provisional = SimpleNamespace(
            spec=SimpleNamespace(workspace=workspace), endpoints=endpoints
        )
        argv = driver.expected_argv(provisional, FRESH_GUI)
        spec = LaunchSpecification(
            workspace,
            RuntimeIdentity(freight.BINARY.resolve(), "15.3", BINARY_SHA256),
            argv,
            workspace.root,
            workspace.environment,
            workspace.logs / "stdout.log",
            workspace.logs / "stderr.log",
        )
        frozen = source_freeze()
        validation = require_bridge_validation(package)
        exercise.require_retained_vm_helpers(validation)
        for name in exercise.VM_HELPERS:
            helper = PROJECT / name
            frozen[str(helper)] = sha256(helper)
        import openttdlab

        for path in (Path(openttdlab.__file__), driver.SUSPENSION_VALIDATION):
            frozen[str(path.resolve())] = sha256(path)
        for root in (
            PROJECT / "app/planning",
            freight.PACKAGE,
            PROJECT / "app/simulation/openttd/road_company_package",
        ):
            for path in root.rglob("*"):
                if path.is_file() and path.suffix in (".py", ".nut"):
                    frozen[str(path.resolve())] = sha256(path)
        archive = directory / "frozen-source.zip"
        with zipfile.ZipFile(archive, "x", compression=zipfile.ZIP_DEFLATED) as z:
            for filename in sorted(frozen):
                path = Path(filename)
                if path.is_relative_to(PROJECT):
                    z.writestr(str(path.relative_to(PROJECT)), path.read_bytes())
            for name, data in package.items():
                z.writestr("staged/" + name, data)
            z.writestr("staged/openttd.cfg", workspace.config.read_bytes())
        for path in Path(fresh_world).rglob("*"):
            if path.is_file():
                frozen[str(path.resolve())] = sha256(path)
        frozen[str(archive)] = sha256(archive)
        frozen[str(freight.BINARY)] = sha256(freight.BINARY)
        for path in workspace.root.rglob("*"):
            if path.is_file() and path != secret:
                frozen[str(path.resolve())] = sha256(path)
        metadata = dict(
            schema=SCHEMA,
            qualification_id=FRESH_GUI,
            execution_contract=GUI_CONTRACT,
            workspace=str(workspace.root),
            argv=list(argv),
            binary=str(freight.BINARY),
            public_key=key.public_hex,
            game_port=reservation.game_port,
            admin_port=reservation.admin_port,
            frozen=frozen,
            fresh_world_directory=str(Path(fresh_world).resolve()),
            fresh_save_sha256=world["fresh_save_sha256"],
            configuration_sha256=driver.configuration_digest(workspace.config),
            bridge_sha256=driver.bridge_digest(package),
            budgets=freight.network_budgets(3) | dict(total_seconds=1200),
            authorization=(
                "separate explicit authorization; ONE dedicated-server launch; ONE"
                " AdminPort connection; ONE GUI client join; no retry/reconnect; the"
                " fresh world runs unpaused; the probe ends when the operator closes"
                " the window or the observation window elapses; stop on unexpected"
                " failure"
            ),
        )
        write_json(directory / "PRELAUNCH.json", metadata)
        (directory / "PRELAUNCH.sha256").write_text(sha256(directory / "PRELAUNCH.json") + "\n")
        return PreparedProof(directory, spec, secret, key.public_hex, endpoints)
    except BaseException:
        if secret.is_file():
            secret.unlink()
        if workspace is not None:
            workspace.close()
        raise
    finally:
        reservation.close()


def preflight_gui(prepared):
    require_desktop_session()
    directory = prepared.directory
    metadata = json.loads((directory / "PRELAUNCH.json").read_bytes())
    if (
        metadata["qualification_id"] != FRESH_GUI
        or directory.name != FRESH_GUI
        or metadata["schema"] != SCHEMA
        or (directory / "CLAIM.json").exists()
        or sha256(directory / "PRELAUNCH.json")
        != (directory / "PRELAUNCH.sha256").read_text().strip()
    ):
        raise ValueError("fresh-world sealed identity/claim mismatch")
    exercise.require_contract(metadata, GUI_CONTRACT)
    verify_freeze(metadata["frozen"])
    if (
        driver.bridge_digest(driver.package_bytes()) != metadata["bridge_sha256"]
        or driver.configuration_digest(prepared.spec.workspace.config)
        != metadata["configuration_sha256"]
    ):
        raise ValueError("fresh-world package/configuration mismatch")
    world = verify_fresh_creation(metadata["fresh_world_directory"])
    if world["fresh_save_sha256"] != metadata["fresh_save_sha256"]:
        raise ValueError("fresh-world save pin drift")
    staged = prepared.spec.workspace.root / "source.sav"
    if staged.is_symlink() or not staged.is_file():
        raise ValueError("fresh-world staged save missing")
    if sha256(staged) != metadata["fresh_save_sha256"]:
        raise ValueError("fresh-world staged save digest mismatch")
    if "canonical_directory" in metadata or "canonical_save_sha256" in metadata:
        raise ValueError("fresh-world GUI stage must never stage canonical evidence")
    backend = FreshWorldBackend(authorized_one_launch=True)
    backend.preflight(prepared)
    backend.validate_launch(prepared)
    reservation = EndpointReservation.allocate(*prepared.endpoints)
    reservation.close()
    return metadata


async def _seal_attempt(prepared, result, backend):
    """The shared owned-cleanup finally block (exercise.run semantics)."""
    cleanup = await backend.cleanup(prepared)
    for name in ("stdout.log", "stderr.log"):
        source = prepared.spec.workspace.logs / name
        if source.is_file():
            try:
                with (
                    source.open("rb") as incoming,
                    (prepared.directory / name).open("xb") as out,
                ):
                    shutil.copyfileobj(incoming, out)
            except Exception as error:
                result["evidence_error"] = type(error).__name__ + ": " + str(error)
                result["status"] = "FAILED_EVIDENCE"
    try:
        cleanup.update(verify_cleanup_endpoints(prepared, cleanup))
        if not cleanup["reaped"] or cleanup["cleanup_error"]:
            raise ValueError("incomplete cleanup")
        prepared.spec.workspace.close()
        cleanup["workspace_disposed"] = not prepared.spec.workspace.root.exists()
        cleanup["credential_removed"] = not prepared.key_path.exists()
    except Exception as error:
        cleanup["verification_error"] = str(error)
        result["status"] = "FAILED_CLEANUP"
    write_json(prepared.directory / "cleanup.json", cleanup)
    write_json(prepared.directory / "result.json", result)
    (prepared.directory / "artifact-manifest.sha256").write_text(manifest(prepared.directory))


async def run_create(prepared, *, authorize_one_launch=False):
    if authorize_one_launch is not True:
        raise ValueError("separate explicit one-launch authorization required")
    metadata = preflight_create(prepared)
    seal = sha256(prepared.directory / "PRELAUNCH.json")
    write_json(
        prepared.directory / "CLAIM.json",
        dict(consumed=True, prelaunch_digest=seal, launches_allowed=1, retries=0),
    )
    backend = FreshWorldBackend(authorized_one_launch=True)
    result = dict(status="FAILED", launches=0, connections=0)
    try:
        async with asyncio.timeout(metadata["budgets"]["total_seconds"]):
            await backend.launch(prepared)
            result["launches"] = 1
            await wait_log(backend, prepared, GENERATION_MARKER)
            digest = await save(backend, prepared, "fresh-world")
            write_json(
                prepared.directory / "world.json",
                dict(
                    schema="fresh-world-create-world-v1",
                    identity=FRESH_CREATE,
                    world_generation=metadata["world_generation"],
                    argv=list(metadata["argv"]),
                    fresh_save_name="fresh-world.sav",
                    fresh_save_sha256=digest,
                ),
            )
            result["status"] = FRESH_CREATE_VERIFIED
    except BaseException as error:
        result["error"] = type(error).__name__ + ": " + str(error)
        try:
            result.update(driver.failure_details(prepared, error))
        except (OSError, ValueError) as reporting_error:
            result["failure_reporting_error"] = str(reporting_error)
        if backend.process is not None:
            try:
                await driver.protected_save(backend, prepared, "failure")
            except Exception as failure:
                result["failure_save_error"] = str(failure)
    finally:
        await _seal_attempt(prepared, result, backend)
    return result


async def conduct_fresh_gui(backend, prepared, session, result):
    """The fresh world is already running; spawn the window, verify the join
    server-side, observe, stop owned."""
    display_env = require_desktop_session()
    client = gui_probe.GuiClient(
        prepared,
        client_name=CLIENT_NAME,
        identity=FRESH_GUI,
        join_marker=JOIN_MARKER,
        schema=FRESH_GUI_CLIENT_SCHEMA,
    )
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
    result["status"] = FRESH_GUI_VERIFIED


async def run_gui(prepared, *, authorize_one_launch=False):
    if authorize_one_launch is not True:
        raise ValueError("separate explicit one-launch authorization required")
    metadata = preflight_gui(prepared)
    seal = sha256(prepared.directory / "PRELAUNCH.json")
    write_json(
        prepared.directory / "CLAIM.json",
        dict(consumed=True, prelaunch_digest=seal, launches_allowed=1, retries=0),
    )
    backend = FreshWorldBackend(authorized_one_launch=True)
    result = dict(status="FAILED", launches=0, connections=0)
    try:
        async with asyncio.timeout(metadata["budgets"]["total_seconds"]):
            await backend.launch(prepared)
            result["launches"] = 1
            await wait_log(backend, prepared, "FREIGHT_DELIVERY_READY")
            session = await freight.PlannerDeliverySession.connect_secure(
                "127.0.0.1",
                prepared.endpoints[1],
                5,
                key=AuthorizedKey.from_bytes(prepared.key_path.read_bytes()),
            )
            backend.session = session
            result["connections"] = 1
            await session.authenticate("Fresh-world-gui", "1", timeout=10)
            w = session.welcome
            if session.state is not AuthState.ACTIVE or w is None:
                raise ValueError("fresh-world secure runtime identity mismatch")
            require_fresh_welcome(w, expected_welcome())
            write_json(
                prepared.directory / "runtime-identity.json",
                dict(encrypted=True, welcome=asdict(w)),
            )
            if session.protocol is None:
                raise ValueError("native Admin protocol missing")
            await conduct_fresh_gui(backend, prepared, session, result)
    except BaseException as error:
        result["error"] = type(error).__name__ + ": " + str(error)
        try:
            result.update(driver.failure_details(prepared, error))
        except (OSError, ValueError) as reporting_error:
            result["failure_reporting_error"] = str(reporting_error)
        if backend.process is not None:
            try:
                await driver.protected_save(backend, prepared, "failure")
            except Exception as failure:
                result["failure_save_error"] = str(failure)
    finally:
        await _seal_attempt(prepared, result, backend)
    return result


def verify_create(directory):
    return exercise.verify(directory, contract=CREATE_CONTRACT, status=FRESH_CREATE_VERIFIED)


def verify_gui(directory):
    return exercise.verify(directory, contract=GUI_CONTRACT, status=FRESH_GUI_VERIFIED)


def main():
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("create", "gui", "preflight", "run", "verify"))
    parser.add_argument("directory", type=Path)
    parser.add_argument("--fresh-world", type=Path, dest="fresh_world")
    parser.add_argument(
        "--authorize-one-launch",
        action="store_true",
        help="fresh explicit operator authorization required for the ONE launch",
    )
    args = parser.parse_args()
    if args.command == "create":
        prepared = prepare_create(args.directory)
        print(f"prepared {prepared.directory} (offline; no launch)")
        return 0
    if args.command == "gui":
        if args.fresh_world is None:
            parser.error("--fresh-world must point at the verified fresh-world creation attempt")
        prepared = prepare_gui(args.directory, fresh_world=args.fresh_world)
        print(f"prepared {prepared.directory} (offline; no launch)")
        return 0
    if args.directory.name not in (FRESH_CREATE, FRESH_GUI):
        raise ValueError("unknown fresh-world attempt directory")
    if args.command in ("preflight", "run"):
        prepared = driver.reopen(args.directory)
        if args.command == "preflight":
            if prepared.directory.name == FRESH_CREATE:
                preflight_create(prepared)
                print("fresh-world create preflight PASS")
            else:
                preflight_gui(prepared)
                print("fresh-world GUI probe preflight PASS")
            return 0
        run = run_create if prepared.directory.name == FRESH_CREATE else run_gui
        result = asyncio.run(run(prepared, authorize_one_launch=args.authorize_one_launch))
        print(json.dumps(result, sort_keys=True))
        expected = (
            FRESH_CREATE_VERIFIED if prepared.directory.name == FRESH_CREATE else FRESH_GUI_VERIFIED
        )
        return 0 if result["status"] == expected else 1
    # verify reads sealed receipts only: the run-time workspace is disposed
    # by owned cleanup, so reopening it here would crash a VERIFIED attempt.
    status = (
        verify_create(args.directory)
        if args.directory.name == FRESH_CREATE
        else verify_gui(args.directory)
    )
    print(status)
    return 0 if status in (FRESH_CREATE_VERIFIED, FRESH_GUI_VERIFIED) else 1


if __name__ == "__main__":
    sys.exit(main())
