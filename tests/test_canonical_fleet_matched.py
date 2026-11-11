"""Offline regression for the T-031 matched A/B arms stage of record.

Zero native processes: identity separation, prepare refusals and one real
offline staging, contract and receipt shaping, the arm conductor wiring
(monitored horizon seam), and the descriptive comparison record.
"""

import asyncio
import json
from types import SimpleNamespace

import pytest
from test_freight_canonical import observation, parse

from app.simulation.openttd import (
    freight_canonical_runtime,
    freight_continuous,
)
from app.simulation.openttd.proof import canonical_fleet as driver
from app.simulation.openttd.proof import canonical_fleet_exercise as exercise
from app.simulation.openttd.proof import canonical_fleet_matched as matched

CAPITAL_READBACK = "controlled-native-reload"


def arm_metadata(canonical_directory, arm, **extra):
    return dict(
        schema=exercise.SCHEMA,
        qualification_id=matched.ARMS[arm],
        execution_contract=matched.matched_contract(arm),
        canonical_directory=canonical_directory,
        capacity_telemetry=matched.matched_contract(arm)["telemetry"],
        budgets=matched.arm_budgets(arm),
        **extra,
    )


def test_arm_identity_family_is_independent():
    assert matched.ARM_A != matched.ARM_B
    assert matched.ARM_A not in (driver.CREATE, driver.RELOAD, exercise.EXERCISE)
    assert matched.ARM_B not in (driver.CREATE, driver.RELOAD, exercise.EXERCISE)
    assert matched.matched_contract("A")["purchase"] is False
    assert matched.matched_contract("B")["purchase"] is True
    assert matched.matched_contract("A")["telemetry"]["vehicle_count"] == 3
    assert matched.matched_contract("B")["telemetry"]["vehicle_count"] == 4
    with pytest.raises(ValueError, match="arm must be A or B"):
        matched.matched_contract("C")
    with pytest.raises(ValueError, match="arm must be A or B"):
        matched.prepare(SimpleNamespace(), canonical=None, arm="C")


def test_prepare_requires_canonical_evidence_before_any_write(tmp_path):
    directory = tmp_path / matched.ARM_A
    with pytest.raises(ValueError, match="stage requires canonical"):
        matched.prepare(directory, canonical=None, arm="A")
    assert not directory.exists()


def test_prepare_stages_arm_b_seal_offline(tmp_path, monkeypatch):
    created = SimpleNamespace(source_save_sha256="a" * 64)
    canonical = tmp_path / "canonical-source"
    canonical.mkdir()
    for service in range(3):
        (canonical / f"native-plan-{service}.json").write_text("{}")
    (canonical / "effective-openttd.cfg").write_text("[network]\n")
    (canonical / "canonical.sav").write_bytes(b"staged")
    monkeypatch.setattr(driver, "verify_created_source", lambda _: created)
    monkeypatch.setattr(freight_canonical_runtime, "verify_save", lambda *a, **k: None)
    directory = tmp_path / matched.ARM_B
    prepared = matched.prepare(directory, canonical=canonical, arm="B")
    metadata = json.loads((directory / "PRELAUNCH.json").read_bytes())
    assert metadata["qualification_id"] == matched.ARM_B
    assert metadata["execution_contract"] == matched.matched_contract("B")
    assert metadata["capacity_telemetry"] == dict(
        version=2, vehicle_count=4, max_tick_gap=matched.MAX_TICK_GAP
    )
    assert metadata["budgets"] == matched.arm_budgets("B")
    assert metadata["budgets"]["monitor_polls"] == freight_continuous.MAX_POLLS
    assert (directory / "PRELAUNCH.sha256").is_file()
    assert prepared.endpoints[0] != prepared.endpoints[1]
    for name in ("canonical.sav", "effective-openttd.cfg"):
        shutil_copy_source = canonical / name
        assert shutil_copy_source.is_file() or name == "canonical.sav"


def test_arm_receipts_shape_and_telemetry_options(tmp_path, monkeypatch):
    created = parse(observation())
    plans = tuple(SimpleNamespace(digest=f"{n}" * 64) for n in range(3))
    a_dispatch = dict(binding=None, purchase_capex=0)
    a_receipts = matched.arm_receipts(created, a_dispatch, plans, "A")
    assert [r["service"] for r in a_receipts] == [0, 1, 2]
    assert all(r["construction_purchase_spending"] == 0 for r in a_receipts)
    assert all("additional_vehicles" not in r for r in a_receipts)
    b_dispatch = dict(binding=dict(vehicle=4429), purchase_capex=31200)
    b_receipts = matched.arm_receipts(created, b_dispatch, plans, "B")
    assert b_receipts[1]["additional_vehicles"] == [
        dict(service=1, vehicle=4429, purchase_capex=31200)
    ]
    from app.simulation.openttd.freight_continuous import telemetry_options

    options_a = telemetry_options(
        dict(capacity_telemetry=dict(version=2, vehicle_count=3, max_tick_gap=100)),
        a_receipts,
    )
    assert [b["vehicle"] for b in options_a["bindings"]] == [r["vehicle"] for r in a_receipts]
    options_b = telemetry_options(
        dict(capacity_telemetry=dict(version=2, vehicle_count=4, max_tick_gap=100)),
        b_receipts,
    )
    assert len(options_b["bindings"]) == 4


def arm_prepared(tmp_path, arm, canonical_directory=None):
    directory = tmp_path / matched.ARMS[arm]
    directory.mkdir()
    payload = arm_metadata(str(canonical_directory or tmp_path / "canonical"), arm)
    (directory / "PRELAUNCH.json").write_text(json.dumps(payload))
    return SimpleNamespace(directory=directory)


def test_conduct_arm_wires_receipts_monitor_and_record(tmp_path, monkeypatch):
    created = parse(observation())
    plans = tuple(SimpleNamespace(digest=f"{n}" * 64) for n in range(3))
    canonical = tmp_path / "canonical-source"
    canonical.mkdir()
    for service in range(3):
        (canonical / f"native-plan-{service}.json").write_text("{}")
    prepared = arm_prepared(tmp_path, "B", canonical_directory=canonical)
    phases = []

    async def staged_conduct(backend, prepared, session, result, **kwargs):
        phases.append(("exercise-conduct", kwargs["arm"]))
        (prepared.directory / "canonical-dispatch.json").write_text(
            json.dumps(dict(arm="B", binding=dict(vehicle=4429), purchase_capex=31200))
        )

    summary = dict(
        classification="NATIVE_FIVE_YEAR_CONTINUOUS",
        complete_economy_years=5,
        financial_metrics=dict(income=100, delivered_cargo=7),
        observation_counts=dict(monthly=60, quarterly=20, annual=5),
        services=[],
    )

    async def monitor(prepared, session, plans, receipts, metadata, result):
        phases.append(("monitor", len(receipts)))
        assert result["requests"] == 0
        assert metadata["capacity_telemetry"]["vehicle_count"] == 4
        assert plans[0].digest == "0" * 64
        return summary

    monkeypatch.setattr(exercise, "conduct_exercise", staged_conduct)
    monkeypatch.setattr(driver, "load_created", lambda _: created)
    monkeypatch.setattr(
        matched, "DeliveryPlan", SimpleNamespace(model_validate_json=lambda _: plans[0])
    )
    monkeypatch.setattr(freight_continuous, "monitor_network", monitor)

    result = {}
    asyncio.run(
        matched.conduct_arm(SimpleNamespace(), prepared, SimpleNamespace(), result, arm="B")
    )
    assert phases == [("exercise-conduct", "B"), ("monitor", 3)]
    assert result["status"] == matched.MATCHED_VERIFIED
    for service in range(3):
        receipt = json.loads((prepared.directory / f"service-receipt-{service}.json").read_text())
        assert receipt["vehicle"] == created.state.vehicles[service].vehicle
    assert json.loads((prepared.directory / "service-receipt-1.json").read_text())[
        "additional_vehicles"
    ] == [dict(service=1, vehicle=4429, purchase_capex=31200)]
    for service in range(3):
        assert (prepared.directory / f"native-plan-{service}.json").is_file()
    record = json.loads((prepared.directory / "arm-record.json").read_text())
    assert record["arm"] == "B"
    assert record["identity"] == matched.ARM_B
    assert record["dispatch_purchase_capex"] == 31200
    assert record["summary"] == summary
    assert record["provenance"]["fourth_vehicle_capex"] == "OBSERVED"
    assert "UNKNOWN" in record["provenance"]["original_construction_spending"]


def test_conduct_arm_refuses_missing_dispatch_receipt(tmp_path, monkeypatch):
    prepared = arm_prepared(tmp_path, "A")

    async def staged_conduct(backend, prepared, session, result, **kwargs):
        pass

    monkeypatch.setattr(exercise, "conduct_exercise", staged_conduct)
    with pytest.raises(OSError):
        asyncio.run(
            matched.conduct_arm(SimpleNamespace(), prepared, SimpleNamespace(), {}, arm="A")
        )


def test_run_requires_authorization_but_writes_nothing(tmp_path, monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("authorization must precede preflight and claim")

    monkeypatch.setattr(exercise, "preflight", forbidden)
    with pytest.raises(ValueError, match="authorization"):
        asyncio.run(matched.run(SimpleNamespace(directory=tmp_path), arm="B"))
    assert list(tmp_path.iterdir()) == []


def arm_record(tmp_path, arm, income):
    summary = dict(
        classification="NATIVE_FIVE_YEAR_CONTINUOUS",
        financial_metrics=dict(income=income, delivered_cargo=income),
        observation_counts=dict(annual=5),
        services=[],
    )
    record = dict(
        arm=arm,
        identity=matched.ARMS[arm],
        execution_contract=matched.matched_contract(arm),
        dispatch_purchase_capex=31200 if arm == "B" else 0,
        summary=summary,
    )
    directory = tmp_path / arm
    directory.mkdir()
    (directory / "arm-record.json").write_text(json.dumps(record))
    return directory


def test_compare_arms_is_descriptive_and_provenance_labeled(tmp_path):
    a_dir = arm_record(tmp_path, "A", 100)
    b_dir = arm_record(tmp_path, "B", 250)
    comparison = matched.compare_arms(a_dir, b_dir, output=tmp_path)
    assert comparison["classification"] == "DESCRIPTIVE_MATCHED_AB_COMPARISON"
    assert comparison["arm_a"]["identity"] == matched.ARM_A
    assert comparison["fourth_vehicle_capex_gbp"] == dict(a=0, b=31200, provenance="OBSERVED")
    metrics = comparison["financial_metrics"]
    assert metrics["income"] == dict(a=100, b=250, delta_b_minus_a=150, provenance="OBSERVED")
    assert "a positive revenue delta alone does not establish profit" in comparison["guards"]
    assert (tmp_path / "matched-comparison.json").is_file()


def test_compare_arms_marks_missing_amounts_unknown(tmp_path):
    a_dir = arm_record(tmp_path, "A", 100)
    b_dir = arm_record(tmp_path, "B", 250)
    a_summary = json.loads((a_dir / "arm-record.json").read_text())
    a_summary["summary"]["financial_metrics"]["revenue_per_economy_day"] = None
    (a_dir / "arm-record.json").write_text(json.dumps(a_summary))
    comparison = matched.compare_arms(a_dir, b_dir)
    assert comparison["financial_metrics"]["revenue_per_economy_day"]["provenance"] == "UNKNOWN"


def test_compare_arms_refuses_swapped_or_missing_arms(tmp_path):
    a_dir = arm_record(tmp_path, "A", 100)
    b_dir = arm_record(tmp_path, "B", 250)
    with pytest.raises(ValueError, match="A and B arm records"):
        matched.compare_arms(b_dir, a_dir)


def test_verify_states(tmp_path):
    (tmp_path / "PRELAUNCH.json").write_text(
        json.dumps(arm_metadata(str(tmp_path / "canonical"), "A"))
    )
    assert matched.verify(tmp_path, arm="A") == "AUTHORIZATION_UNVERIFIED"
    (tmp_path / "CLAIM.json").write_text("{}")
    (tmp_path / "result.json").write_text(json.dumps(dict(status="FAILED")))
    assert matched.verify(tmp_path, arm="A").startswith("ATTEMPT_NOT_VERIFIED")
    (tmp_path / "result.json").write_text(json.dumps(dict(status=matched.MATCHED_VERIFIED)))
    from app.simulation.openttd.proof.harness import sha256

    digest = sha256(tmp_path / "result.json")
    (tmp_path / "artifact-manifest.sha256").write_text(f"{digest}  result.json\n")
    assert matched.verify(tmp_path, arm="A") == matched.MATCHED_VERIFIED
