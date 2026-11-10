"""Offline regression for the canonical fleet exercise stage of record.

Zero native processes: preparation refusals, the q3 byte-pin drift guard and
the conductor wiring are all controlled; nothing launches or connects.
"""

import asyncio
import json
from types import SimpleNamespace

import pytest
from test_freight_canonical import observation, parse

from app.simulation.openttd import freight_canonical_dispatch, freight_canonical_runtime
from app.simulation.openttd.freight_canonical_dispatch import BoundaryReceipt
from app.simulation.openttd.proof import canonical_fleet as driver
from app.simulation.openttd.proof import canonical_fleet_exercise as exercise

CAPITAL_READBACK = "controlled-native-reload"


def exercise_metadata(canonical_directory, **extra):
    return dict(
        schema=exercise.SCHEMA,
        qualification_id=exercise.EXERCISE,
        execution_contract=exercise.EXERCISE_CONTRACT,
        canonical_directory=canonical_directory,
        bridge_sha256="b" * 64,
        configuration_sha256="c" * 64,
        **extra,
    )


def test_identity_family_is_independent(tmp_path, monkeypatch):
    assert exercise.EXERCISE not in (driver.CREATE, driver.RELOAD)
    assert driver.CREATE != driver.RELOAD

    def forbidden(*args, **kwargs):
        pytest.fail("workspace creation must be refused at the identity gate")

    monkeypatch.setattr(driver.RuntimeWorkspace, "create", forbidden)
    directory = tmp_path / driver.RELOAD
    with pytest.raises(ValueError, match="exact independent canonical exercise identity"):
        exercise.prepare(directory, canonical=tmp_path)
    assert not directory.exists()


def test_prepare_requires_canonical_evidence_before_any_write(tmp_path):
    directory = tmp_path / exercise.EXERCISE
    with pytest.raises(ValueError, match="exercise requires canonical"):
        exercise.prepare(directory, canonical=None)
    assert not directory.exists()


def test_prepare_refuses_drifted_staged_bridge_before_workspace(tmp_path, monkeypatch):
    created = SimpleNamespace(source_save_sha256="a" * 64)
    monkeypatch.setattr(driver, "verify_created_source", lambda _: created)
    monkeypatch.setattr(freight_canonical_runtime, "verify_save", lambda *a, **k: None)

    def drifted():
        return {"main.nut": b"drifted-bridge"}

    monkeypatch.setattr(driver, "package_bytes", drifted)
    directory = tmp_path / exercise.EXERCISE
    with pytest.raises(ValueError, match="exact OpenTTD 15.3 VM validation"):
        exercise.prepare(directory, canonical=tmp_path / "canonical-source")
    assert not directory.exists()


def test_bridge_validation_missing_record_refuses(tmp_path, monkeypatch):
    monkeypatch.setattr(driver, "SUSPENSION_VALIDATION", tmp_path / "absent-suspension.json")
    with pytest.raises((OSError, ValueError)):
        exercise.require_bridge_validation(driver.package_bytes())


def test_bridge_validation_pin_holds_at_head():
    # Retained-record dependent: skip-typed on clones without artifacts/.
    record = driver.SUSPENSION_VALIDATION
    if not record.is_file():
        pytest.skip("retained q3 validation record absent on this clone")
    else:
        exercise.require_bridge_validation(driver.package_bytes())
        package = driver.package_bytes()
        drifted = {name: data + b" " for name, data in package.items()}
        with pytest.raises(ValueError, match="exact OpenTTD 15.3 VM validation"):
            exercise.require_bridge_validation(drifted)


def test_contract_refusal(tmp_path):
    metadata = exercise_metadata(str(tmp_path))
    exercise.require_exercise_contract(metadata)
    drifted = dict(metadata)
    drifted["execution_contract"] = dict(exercise.EXERCISE_CONTRACT, unpause=False)
    with pytest.raises(ValueError, match="exercise contract"):
        exercise.require_exercise_contract(drifted)


def boundary_receipt(request_type, tick, created, *, started):
    rows = [
        (v.service, v.vehicle, v.tile, 0, 0, 0 if not started else 4)
        for v in created.state.vehicles
    ]
    return BoundaryReceipt(
        protocol=1,
        type=request_type + "-result",
        request_id=request_type,
        service=-1,
        status="ok",
        tick=tick,
        economy_date=created.state.economy_date,
        paused=True,
        command_pause_level=2,
        restored=True,
        originals=[tuple(row) for row in rows],
        extra=None,
        cash=created.state.cash,
        loan=created.state.loan,
    )


def exercise_prepared(tmp_path):
    prepared = SimpleNamespace(directory=tmp_path)
    payload = exercise_metadata(str(tmp_path / "canonical"))
    (tmp_path / "PRELAUNCH.json").write_text(json.dumps(payload))
    return prepared


def test_conductor_wires_reload_correspondence_then_purchase_dispatch_unpause(
    tmp_path, monkeypatch
):
    created = parse(observation())
    loaded = created.model_copy(update={"qualification_id": exercise.EXERCISE + "-loaded"})
    prepared = exercise_prepared(tmp_path)
    phases = []

    async def context(*args):
        phases.append("reload-context")

    async def saved(backend, prepared, name):
        assert name == "reload-readback"
        phases.append("reload-save")
        return CAPITAL_READBACK

    async def reloader(session, directory, **kwargs):
        phases.append("verify-reloaded")
        assert kwargs["identity"] == exercise.EXERCISE + "-reload"
        assert kwargs["bridge_sha256"] == "b" * 64
        assert kwargs["created"] is created
        return loaded

    receipts = [
        boundary_receipt("reload-before", 10, created, started=False),
        boundary_receipt("reload-after", 11, created, started=False),
    ]

    async def boundary(session, directory, name):
        phases.append(name)
        return receipts.pop(0)

    async def dispatch(backend, prepared, session, *, created, loaded, arm):
        phases.append("dispatch")
        assert arm == "B"
        (prepared.directory / "canonical-dispatch.json").write_text(
            json.dumps(dict(purchase_capex=4429))
        )
        return dict(arm="B", purchase_capex=4429)

    monkeypatch.setattr(driver, "load_created", lambda _: created)
    monkeypatch.setattr(driver, "establish_reload_context", context)
    monkeypatch.setattr(driver, "protected_save", saved)
    monkeypatch.setattr(freight_canonical_runtime, "verify_reloaded", reloader)
    monkeypatch.setattr(freight_canonical_dispatch, "read_boundary", boundary)
    monkeypatch.setattr(freight_canonical_dispatch, "dispatch_loaded_arm", dispatch)

    result = {}
    asyncio.run(exercise.conduct_exercise(SimpleNamespace(), prepared, SimpleNamespace(), result))
    assert phases == [
        "reload-context",
        "reload-before",
        "reload-save",
        "verify-reloaded",
        "reload-after",
        "dispatch",
    ]
    assert result["status"] == "CANONICAL_FLEET_EXERCISE_VERIFIED"
    correspondence = json.loads((tmp_path / "reload-correspondence.json").read_text())
    assert correspondence["status"] == "EXACT_NATIVE_SEMANTIC_CORRESPONDENCE"
    assert correspondence["execution_contract"] == exercise.EXERCISE_CONTRACT
    from app.simulation.openttd.proof.harness import sha256

    assert correspondence["observation_sha256"] == sha256(tmp_path / "reload-observation.json")
    record = json.loads((tmp_path / "exercise-correspondence.json").read_text())
    assert record["purchase_capex"] == 4429
    assert record["dispatch_correspondence_sha256"] == sha256(tmp_path / "canonical-dispatch.json")
    assert record["execution_contract"] == exercise.EXERCISE_CONTRACT


def test_conductor_refuses_unrestored_boundary(tmp_path, monkeypatch):
    created = parse(observation())
    loaded = created.model_copy(update={"qualification_id": exercise.EXERCISE + "-loaded"})
    prepared = exercise_prepared(tmp_path)
    before = boundary_receipt("reload-before", 10, created, started=False).model_copy(
        update={"restored": False}
    )
    after = boundary_receipt("reload-before", 11, created, started=False).model_copy(
        update={"restored": False}
    )

    async def boundary(session, directory, name):
        return after if name == "reload-after" else before

    async def context(*args):
        return None

    async def saved(*args):
        return CAPITAL_READBACK

    async def reloader(*args, **kwargs):
        return loaded

    monkeypatch.setattr(driver, "load_created", lambda _: created)
    monkeypatch.setattr(driver, "establish_reload_context", context)
    monkeypatch.setattr(driver, "protected_save", saved)
    monkeypatch.setattr(freight_canonical_runtime, "verify_reloaded", reloader)
    monkeypatch.setattr(freight_canonical_dispatch, "read_boundary", boundary)
    with pytest.raises(ValueError, match="restored originals-only boundary"):
        asyncio.run(exercise.conduct_exercise(SimpleNamespace(), prepared, SimpleNamespace(), {}))
    assert not (tmp_path / "exercise-correspondence.json").exists()


def test_conductor_refuses_boundary_drift(tmp_path, monkeypatch):
    created = parse(observation())
    loaded = created.model_copy(update={"qualification_id": exercise.EXERCISE + "-loaded"})
    prepared = exercise_prepared(tmp_path)
    drifted = boundary_receipt("reload-before", 10, created, started=False).model_copy(
        update={"cash": created.state.cash + 1}
    )
    before = boundary_receipt("reload-before", 10, created, started=False)

    async def boundary(session, directory, name):
        return drifted if name == "reload-after" else before

    async def context(*args):
        return None

    async def saved(*args):
        return None

    async def reloader(*args, **kwargs):
        return loaded

    monkeypatch.setattr(driver, "load_created", lambda _: created)
    monkeypatch.setattr(driver, "establish_reload_context", context)
    monkeypatch.setattr(driver, "protected_save", saved)
    monkeypatch.setattr(freight_canonical_runtime, "verify_reloaded", reloader)
    monkeypatch.setattr(freight_canonical_dispatch, "read_boundary", boundary)
    with pytest.raises(ValueError, match="drift|finance/date mismatch"):
        asyncio.run(exercise.conduct_exercise(SimpleNamespace(), prepared, SimpleNamespace(), {}))


def test_run_requires_authorization_but_writes_nothing(tmp_path, monkeypatch):
    def forbidden(*args):
        pytest.fail("authorization must precede preflight and claim")

    monkeypatch.setattr(exercise, "preflight", forbidden)
    with pytest.raises(ValueError, match="authorization"):
        asyncio.run(exercise.run(SimpleNamespace(directory=tmp_path)))
    assert list(tmp_path.iterdir()) == []


def test_mutation_receipts_count_from_retained_bytes(tmp_path):
    prepared = SimpleNamespace(directory=tmp_path)
    assert exercise.mutation_receipts(prepared) == 0
    for name in (
        "capacity-add-response.json",
        "canonical-start-response.json",
        "canonical-dispatched-response.json",
    ):
        (tmp_path / name).write_text("{}")
    assert exercise.mutation_receipts(prepared) == 3


def test_verify_states(tmp_path):
    payload = exercise_metadata(str(tmp_path / "canonical"))
    (tmp_path / "PRELAUNCH.json").write_text(json.dumps(payload))
    assert exercise.verify(tmp_path) == "AUTHORIZATION_UNVERIFIED"
    (tmp_path / "CLAIM.json").write_text("{}")
    (tmp_path / "result.json").write_text(json.dumps(dict(status="FAILED")))
    assert exercise.verify(tmp_path).startswith("ATTEMPT_NOT_VERIFIED")
    (tmp_path / "result.json").write_text(
        json.dumps(dict(status="CANONICAL_FLEET_EXERCISE_VERIFIED"))
    )
    from app.simulation.openttd.proof.harness import sha256

    digest = sha256(tmp_path / "result.json")
    (tmp_path / "artifact-manifest.sha256").write_text(f"{digest}  result.json\n")
    (tmp_path / "result.json").write_text(
        json.dumps(dict(status="CANONICAL_FLEET_EXERCISE_VERIFIED"))
    )
    assert exercise.verify(tmp_path) == "CANONICAL_FLEET_EXERCISE_VERIFIED"
    (tmp_path / "tamper.json").write_text("{}")
    (tmp_path / "artifact-manifest.sha256").write_text(
        f"{digest}  result.json\n{'0' * 64}  tamper.json\n"
    )
    assert exercise.verify(tmp_path) == "MANIFEST_MISMATCH: tamper.json"
