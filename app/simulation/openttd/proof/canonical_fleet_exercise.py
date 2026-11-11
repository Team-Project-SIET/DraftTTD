"""T-030 canonical fleet exercise stage of record (Phase B, separately authorized).

Additive to the frozen create/reload lane: the consumed
canonical-fleet-create/reload-q3 identities and their no-purchase reload
contract stay byte-untouched and unreachable from here. This module stages its
own identity from the E2 created evidence, re-proves the native reload
correspondence contract-first, then runs ONE paused purchase -> dispatch ->
unpause exercise under the same byte-pinned validated bridge package.
Preparation never launches or connects; runtime orchestration reuses freight's
secure session, canonical collectors, console saves and owned cleanup.
"""

import argparse
import asyncio
import configparser
import hashlib
import json
import os
import shutil
import sys
import zipfile
from dataclasses import asdict
from pathlib import Path
from types import SimpleNamespace

from app.simulation.openttd.admin_crypto import AuthorizedKey
from app.simulation.openttd.freight_canonical import compare_canonical
from app.simulation.openttd.gamescript_transport import GameScriptTransport
from app.simulation.openttd.proof.canonical_fleet import expected_argv
from app.simulation.openttd.runtime.base import LaunchSpecification
from app.simulation.openttd.runtime.config import AdminSettings, RuntimeWorkspace
from app.simulation.openttd.runtime.identity import RuntimeIdentity
from app.simulation.openttd.secure_admin import AuthState

from . import canonical_fleet as driver
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
from .road_mutation import wait_log

EXERCISE = "canonical-fleet-exercise-t030-1"
SCHEMA = "canonical-fleet-exercise-prelaunch-v1"
VM_HELPERS = (
    "tests/validate_canonical_squirrel.py",
    "tests/support/openttd_squirrel_suspend.cpp",
    "tests/support/canonical_startup_vm.nut",
    "tests/support/canonical_protocol_vm.nut",
)
RETAINED_VM_FROZEN_SOURCE = (
    PROJECT / "artifacts/runtime/canonical-fleet-reload-q3/frozen-source.zip"
)
EXERCISE_CONTRACT = dict(
    mode="canonical-fleet-exercise",
    purchase=True,
    dispatch=True,
    unpause=True,
    purchase_only=False,
    intervention_service=1,
    correspondence="exact-native-semantic-state",
    heartbeat="paused-before-and-after",
    armed_boundary="canonical-arm",
)


def require_bridge_validation(package):
    """The staged byte pin owned by the q3-era exact 15.3 VM validation record.

    The exercise stages the SAME package bytes the record validated; any drift
    in the record (missing, mutated) or the composition refuses.
    """
    validation = json.loads(driver.SUSPENSION_VALIDATION.read_bytes())
    if validation.get("source_commit") != "14ec60f248547d4d062a1160f0fc26d742319888":
        raise ValueError("exact OpenTTD 15.3 VM validation/package correspondence required")
    actual = {name: hashlib.sha256(data).hexdigest() for name, data in sorted(package.items())}
    if validation.get("package_sha256") != actual:
        raise ValueError("exact OpenTTD 15.3 VM validation/package correspondence required")
    return validation


def require_retained_vm_helpers(validation):
    """The q3 record's helper pins bind the RETAINED q3-era tooling bytes.

    The retained frozen-source.zip proves the record's validator provenance;
    the live tree's helpers may legitimately be newer (E92 readback fidelity)
    and are sealed per-stage in the stage's own frozen-source seal.
    """
    with zipfile.ZipFile(RETAINED_VM_FROZEN_SOURCE) as z:
        for name in VM_HELPERS:
            digest = hashlib.sha256(z.read(name)).hexdigest()
            if validation["helper_sha256"].get(str(PROJECT / name)) != digest:
                raise ValueError("retained VM validation helper evidence drifted")


def require_contract(metadata, contract):
    if metadata.get("execution_contract") != contract:
        raise ValueError("sealed canonical stage contract required")
    return metadata


def require_exercise_contract(metadata):
    return require_contract(metadata, EXERCISE_CONTRACT)


def stage_workspace(directory, *, canonical, reservation):
    """Fresh isolated runtime + credentials; callers write the identity files."""
    workspace = RuntimeWorkspace.create(directory / "isolated", retain=True)
    private = workspace.root / ".admin-secret"
    try:
        key = AuthorizedKey.generate()
        with os.fdopen(
            os.open(private, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600), "wb"
        ) as stream:
            stream.write(key._secret)
        # mirror of the driver's staging: the server starts its admin
        # network only with auth material present (private.cfg carries the
        # authorized key, secrets.cfg the password) under
        # allow_insecure_admin_login = false; without it the t035-2
        # attempt refused the AdminPort connect typed (E168).
        workspace.write_config(
            AdminSettings(
                password="",
                port=reservation.admin_port,
                game_port=reservation.game_port,
                authorized_public_key_hex=key.public_hex,
            )
        )
        config = configparser.ConfigParser(interpolation=None)
        config.read_string((canonical / "effective-openttd.cfg").read_text())
        config.set("network", "server_port", str(reservation.game_port))
        config.set("network", "server_admin_port", str(reservation.admin_port))
        with workspace.config.open("w") as stream:
            config.write(stream)
    except BaseException:
        private.unlink(missing_ok=True)
        workspace.close()
        raise
    return workspace, key, private


def prepare(
    directory,
    *,
    canonical,
    identity=EXERCISE,
    contract=EXERCISE_CONTRACT,
    budgets=None,
    capacity_telemetry=None,
    authorization=None,
):
    if directory.name != identity:
        raise ValueError("exact independent canonical stage identity required")
    if canonical is None:
        raise ValueError("stage requires canonical creation evidence")
    from app.simulation.openttd.freight_canonical_runtime import verify_save

    created = driver.verify_created_source(Path(canonical))
    verify_save(Path(canonical) / "canonical.sav", created)
    require_bridge_validation(driver.package_bytes())
    directory = Path(directory).resolve()
    directory.mkdir(parents=True, exist_ok=False)
    reservation = EndpointReservation.allocate()
    workspace = None
    secret = directory / "isolated" / ".admin-secret"
    try:
        workspace, key, secret = stage_workspace(
            directory, canonical=Path(canonical), reservation=reservation
        )
        # mirror of driver.prepare: preflight and the -g launch argv both
        # resolve this exact path; without it every exercise-core staging
        # refuses at preflight (t035-1 refused state, E167).
        shutil.copyfile(Path(canonical) / "canonical.sav", workspace.root / "source.sav")
        graphics = stage_opengfx(freight.GRAPHICS_ARCHIVE, workspace.root / "baseset/OpenGFX")
        write_json(
            directory / "graphics-identity.json",
            dict(asdict(graphics), directory=str(graphics.directory)),
        )
        package = driver.package_bytes()
        target = workspace.game / "RoadFreightProof"
        target.mkdir()
        for name, data in package.items():
            (target / name).write_bytes(data)
        target = workspace.ai / "RoadProofCompany"
        target.mkdir()
        for path in (PROJECT / "app/simulation/openttd/road_company_package").glob("*.nut"):
            shutil.copyfile(path, target / path.name)
        shutil.copyfile(workspace.config, directory / "effective-openttd.cfg")
        endpoints = (reservation.game_port, reservation.admin_port)
        provisional = SimpleNamespace(
            spec=SimpleNamespace(workspace=workspace), endpoints=endpoints
        )
        argv = expected_argv(provisional, identity)
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
        require_retained_vm_helpers(validation)
        for name in VM_HELPERS:
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
        for path in Path(canonical).rglob("*"):
            if path.is_file():
                frozen[str(path.resolve())] = sha256(path)
        frozen[str(archive)] = sha256(archive)
        frozen[str(freight.BINARY)] = sha256(freight.BINARY)
        for path in workspace.root.rglob("*"):
            if path.is_file() and path != secret:
                frozen[str(path.resolve())] = sha256(path)
        metadata = dict(
            schema=SCHEMA,
            qualification_id=identity,
            execution_contract=contract,
            workspace=str(workspace.root),
            argv=list(argv),
            binary=str(freight.BINARY),
            public_key=key.public_hex,
            game_port=reservation.game_port,
            admin_port=reservation.admin_port,
            frozen=frozen,
            canonical_directory=str(Path(canonical).resolve()),
            canonical_save_sha256=created.source_save_sha256,
            configuration_sha256=driver.configuration_digest(workspace.config),
            bridge_sha256=driver.bridge_digest(package),
            predecessor=dict(executor_source_digest=sha256(archive)),
            network_service_limit=3,
            delivery_batch_limit=20,
            planning_budget_gbp="500000",
            financial_reconciliation_version=1,
            game_time_metrics_version=1,
            budgets=(
                budgets
                if budgets is not None
                else freight.network_budgets(3) | dict(total_seconds=1200)
            ),
            **({"capacity_telemetry": capacity_telemetry} if capacity_telemetry else {}),
            authorization=(
                authorization
                if authorization is not None
                else (
                    "separate explicit authorization; one launch; one connection; "
                    "no retry/reconnect; "
                    "paused purchase/dispatch/unpause exercise; stop on unexpected failure"
                )
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


def preflight(prepared, *, identity=EXERCISE, contract=EXERCISE_CONTRACT):
    directory = prepared.directory
    metadata = json.loads((directory / "PRELAUNCH.json").read_bytes())
    if (
        metadata["qualification_id"] != identity
        or directory.name != identity
        or metadata["schema"] != SCHEMA
        or (directory / "CLAIM.json").exists()
        or sha256(directory / "PRELAUNCH.json")
        != (directory / "PRELAUNCH.sha256").read_text().strip()
    ):
        raise ValueError("canonical stage sealed identity/claim mismatch")
    require_contract(metadata, contract)
    verify_freeze(metadata["frozen"])
    if (
        driver.bridge_digest(driver.package_bytes()) != metadata["bridge_sha256"]
        or driver.configuration_digest(prepared.spec.workspace.config)
        != metadata["configuration_sha256"]
    ):
        raise ValueError("canonical package/configuration mismatch")
    from app.simulation.openttd.freight_canonical_runtime import verify_save

    canonical = Path(metadata["canonical_directory"])
    driver.verify_created_source(canonical)
    created = driver.load_created(canonical)
    verify_save(prepared.spec.workspace.root / "source.sav", created)
    if created.source_save_sha256 != metadata["canonical_save_sha256"]:
        raise ValueError("canonical created evidence drift")
    backend = driver.CanonicalBackend(authorized_one_launch=True)
    backend.preflight(prepared)
    backend.validate_launch(prepared)
    reservation = EndpointReservation.allocate(*prepared.endpoints)
    reservation.close()
    return metadata


def verify(
    directory,
    *,
    contract=EXERCISE_CONTRACT,
    status="CANONICAL_FLEET_EXERCISE_VERIFIED",
):
    """Offline receipts check: contract, typed status, digests. Never launches."""
    directory = Path(directory)
    metadata = json.loads((directory / "PRELAUNCH.json").read_bytes())
    if not (directory / "CLAIM.json").exists():
        return "AUTHORIZATION_UNVERIFIED"
    require_contract(metadata, contract)
    result = json.loads((directory / "result.json").read_bytes())
    if result["status"] != status:
        return "ATTEMPT_NOT_VERIFIED: " + result["status"]
    for line in (directory / "artifact-manifest.sha256").read_text().splitlines():
        digest, path = line.split("  ", 1)
        if sha256(directory / path) != digest:
            return "MANIFEST_MISMATCH: " + path
    return status


async def conduct_exercise(
    backend,
    prepared,
    session,
    result,
    *,
    identity=EXERCISE,
    contract=EXERCISE_CONTRACT,
    arm="B",
    dispatch=True,
):
    """Reload correspondence first, then ONE purchase/dispatch/unpause arm.

    dispatch=False stops at the proven reload-only correspondence (the
    q3 no-purchase contract); the caller owns anything after that.
    """
    from app.simulation.openttd.freight_canonical_dispatch import (
        dispatch_loaded_arm,
        read_boundary,
        require_stable_boundary,
    )
    from app.simulation.openttd.freight_canonical_runtime import verify_reloaded

    metadata = json.loads((prepared.directory / "PRELAUNCH.json").read_bytes())
    require_contract(metadata, contract)
    canonical = Path(metadata["canonical_directory"])
    created = driver.load_created(canonical)
    await driver.establish_reload_context(session, prepared.directory, canonical)
    before = await read_boundary(session, prepared.directory, "reload-before")
    await driver.protected_save(backend, prepared, "reload-readback")
    loaded = await verify_reloaded(
        session,
        prepared.directory,
        created=created,
        save=canonical / "canonical.sav",
        identity=identity + "-reload",
        runtime_sha256=BINARY_SHA256,
        bridge_sha256=metadata["bridge_sha256"],
        configuration_sha256=metadata["configuration_sha256"],
        snapshot_path=prepared.directory / "reload-readback.sav",
    )
    after = await read_boundary(session, prepared.directory, "reload-after")
    require_stable_boundary(before, after)
    for receipt in (before, after):
        if not receipt.restored or receipt.extra is not None:
            raise ValueError("reload restored originals-only boundary required")
        for row, vehicle in zip(receipt.originals, created.state.vehicles, strict=True):
            if row[:5] != (vehicle.service, vehicle.vehicle, vehicle.tile, 0, 0):
                raise ValueError("reload original service binding mismatch")
        if (receipt.cash, receipt.loan, receipt.economy_date) != (
            created.state.cash,
            created.state.loan,
            created.state.economy_date,
        ):
            raise ValueError("reload boundary finance/date mismatch")
    compare_canonical(created, loaded)
    write_json(prepared.directory / "reload-observation.json", loaded.model_dump(mode="json"))
    write_json(
        prepared.directory / "reload-correspondence.json",
        dict(
            status="EXACT_NATIVE_SEMANTIC_CORRESPONDENCE",
            execution_contract=contract,
            source_save_sha256=loaded.source_save_sha256,
            observation_sha256=sha256(prepared.directory / "reload-observation.json"),
            before=before.model_dump(mode="json"),
            after=after.model_dump(mode="json"),
        ),
    )
    if not dispatch:
        return dict(
            loaded=loaded,
            before=before.model_dump(mode="json"),
            after=after.model_dump(mode="json"),
        )
    dispatch = await dispatch_loaded_arm(
        backend, prepared, session, created=created, loaded=loaded, arm=arm
    )
    write_json(
        prepared.directory / "exercise-correspondence.json",
        dict(
            status="EXACT_NATIVE_SEMANTIC_CORRESPONDENCE",
            execution_contract=contract,
            reload_correspondence_sha256=sha256(prepared.directory / "reload-correspondence.json"),
            observation_sha256=sha256(prepared.directory / "reload-observation.json"),
            dispatch_correspondence_sha256=sha256(prepared.directory / "canonical-dispatch.json"),
            source_save_sha256=loaded.source_save_sha256,
            purchase_capex=dispatch["purchase_capex"],
        ),
    )
    result["status"] = "CANONICAL_FLEET_EXERCISE_VERIFIED"


def mutation_receipts(prepared):
    names = (
        "capacity-add-response.json",
        "canonical-start-response.json",
        "canonical-dispatched-response.json",
    )
    return sum(1 for name in names if (prepared.directory / name).is_file())


async def run(
    prepared,
    *,
    authorize_one_launch=False,
    identity=EXERCISE,
    contract=EXERCISE_CONTRACT,
    conduct=None,
):
    if authorize_one_launch is not True:
        raise ValueError("separate explicit one-launch authorization required")
    metadata = preflight(prepared, identity=identity, contract=contract)
    seal = sha256(prepared.directory / "PRELAUNCH.json")
    write_json(
        prepared.directory / "CLAIM.json",
        dict(consumed=True, prelaunch_digest=seal, launches_allowed=1, retries=0),
    )
    backend = driver.CanonicalBackend(authorized_one_launch=True)
    frames = []
    accounting = freight.ScenarioPlanningAccounting(frames)
    backend.planning_frame_observer = lambda direction, frame: frames.append(
        (direction, frame.hex())
    )
    backend.planning_frames = frames
    result = dict(status="FAILED", launches=0, connections=0, mutations=0)
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
                frame_observer=accounting.observe,
            )
            backend.session = session
            result["connections"] = 1
            await session.authenticate("Canonical-exercise", "1", timeout=10)
            w = session.welcome
            if (
                session.state is not AuthState.ACTIVE
                or w is None
                or (w.revision, w.seed, w.width, w.height) != ("15.3", 42, 64, 64)
            ):
                raise ValueError("canonical secure runtime identity mismatch")
            write_json(
                prepared.directory / "runtime-identity.json",
                dict(encrypted=True, welcome=asdict(w)),
            )
            if session.protocol is None:
                raise ValueError("native Admin protocol missing")
            accounting.enter("setup")
            await GameScriptTransport(session, session.protocol).subscribe()
            session._frame_observer = backend.planning_frame_observer
            await (conduct or conduct_exercise)(backend, prepared, session, result)
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
        try:
            result["mutations"] = mutation_receipts(prepared)
            write_json(prepared.directory / "frames.json", frames)
        except Exception as error:
            result["evidence_error"] = type(error).__name__ + ": " + str(error)
            result["status"] = "FAILED_EVIDENCE"
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
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prepare", "preflight", "verify", "run"))
    parser.add_argument("directory", type=Path)
    parser.add_argument("--canonical", type=Path)
    parser.add_argument(
        "--authorize-one-launch",
        action="store_true",
        help="fresh explicit operator authorization required for the ONE launch",
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
            print("canonical fleet exercise preflight PASS")
            return 0
        result = asyncio.run(run(prepared, authorize_one_launch=args.authorize_one_launch))
        print(json.dumps(result, sort_keys=True))
        return 0 if result["status"] == "CANONICAL_FLEET_EXERCISE_VERIFIED" else 1
    status = verify(args.directory)
    print(status)
    return 0 if status == "CANONICAL_FLEET_EXERCISE_VERIFIED" else 1


if __name__ == "__main__":
    sys.exit(main())
