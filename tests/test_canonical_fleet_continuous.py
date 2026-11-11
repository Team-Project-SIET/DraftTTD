"""Offline regression for the T-032 five-year continuous stage of record.

Zero native processes: identity separation, prepare refusals and one real
offline staging, contract/finalization shaping, and the conductor wiring
with the monitor seam.
"""

import asyncio
import json
from types import SimpleNamespace

import pytest
from test_freight_canonical import observation, parse

from app.simulation.openttd import freight_canonical_runtime, freight_continuous
from app.simulation.openttd.proof import canonical_fleet as driver
from app.simulation.openttd.proof import canonical_fleet_continuous as continuous
from app.simulation.openttd.proof import canonical_fleet_exercise as exercise
from app.simulation.openttd.proof import canonical_fleet_matched as matched


def stage_metadata(canonical_directory, **extra):
    return dict(
        schema=exercise.SCHEMA,
        qualification_id=continuous.CONTINUOUS,
        execution_contract=continuous.continuous_contract(),
        canonical_directory=canonical_directory,
        capacity_telemetry=dict(version=2, vehicle_count=3, max_tick_gap=continuous.MAX_TICK_GAP),
        budgets=continuous.arm_budgets("A"),
        **extra,
    )


def test_continuous_identity_is_independent():
    assert continuous.CONTINUOUS not in (
        driver.CREATE,
        driver.RELOAD,
        exercise.EXERCISE,
        matched.ARM_A,
        matched.ARM_B,
    )
    contract = continuous.continuous_contract()
    assert contract["purchase"] is False
    assert contract["telemetry"] == dict(version=2, vehicle_count=3, max_tick_gap=100)
    assert contract["finalization"] == "continuous-summary + finalization record"


def test_prepare_requires_canonical_evidence_before_any_write(tmp_path):
    directory = tmp_path / continuous.CONTINUOUS
    with pytest.raises(ValueError, match="stage requires canonical"):
        continuous.prepare(directory, canonical=None)
    assert not directory.exists()


def test_prepare_stages_seal_offline(tmp_path, monkeypatch):
    created = SimpleNamespace(source_save_sha256="a" * 64)
    canonical = tmp_path / "canonical-source"
    canonical.mkdir()
    for service in range(3):
        (canonical / f"native-plan-{service}.json").write_text("{}")
    (canonical / "effective-openttd.cfg").write_text("[network]\n")
    monkeypatch.setattr(driver, "verify_created_source", lambda _: created)
    monkeypatch.setattr(freight_canonical_runtime, "verify_save", lambda *a, **k: None)
    prepared = continuous.prepare(tmp_path / continuous.CONTINUOUS, canonical=canonical)
    metadata = json.loads((prepared.directory / "PRELAUNCH.json").read_bytes())
    assert metadata["qualification_id"] == continuous.CONTINUOUS
    assert metadata["execution_contract"] == continuous.continuous_contract()
    assert metadata["capacity_telemetry"] == dict(version=2, vehicle_count=3, max_tick_gap=100)
    assert metadata["budgets"] == continuous.arm_budgets("A")
    assert metadata["budgets"]["monitor_polls"] == freight_continuous.MAX_POLLS
    assert (prepared.directory / "PRELAUNCH.sha256").is_file()


def test_conduct_continuous_wires_receipts_monitor_and_finalization(tmp_path, monkeypatch):
    created = parse(observation())
    plans = tuple(SimpleNamespace(digest=f"{n}" * 64) for n in range(3))
    canonical = tmp_path / "canonical-source"
    canonical.mkdir()
    for service in range(3):
        (canonical / f"native-plan-{service}.json").write_text("{}")
    directory = tmp_path / continuous.CONTINUOUS
    directory.mkdir()
    (directory / "PRELAUNCH.json").write_text(json.dumps(stage_metadata(str(canonical))))
    (directory / "canonical-dispatch.json").write_text(
        json.dumps(dict(arm="A", binding=None, purchase_capex=0))
    )
    prepared = SimpleNamespace(directory=directory)
    phases = []

    async def staged_conduct(backend, prepared, session, result, **kwargs):
        phases.append(("exercise-conduct", kwargs["arm"]))

    summary = dict(
        classification="NATIVE_FIVE_YEAR_CONTINUOUS",
        complete_economy_years=5,
        financial_metrics=dict(income=42),
        observation_counts=dict(annual=5),
        services=[],
    )

    async def monitor(prepared, session, plans, receipts, metadata, result):
        phases.append(("monitor", len(receipts)))
        assert result["requests"] == 0
        assert metadata["capacity_telemetry"]["vehicle_count"] == 3
        assert plans[0].digest == "0" * 64
        return summary

    monkeypatch.setattr(exercise, "conduct_exercise", staged_conduct)
    monkeypatch.setattr(driver, "load_created", lambda _: created)
    monkeypatch.setattr(continuous, "DeliveryPlan", None, raising=False)

    class FakePlan:
        @staticmethod
        def model_validate_json(_):
            return plans[len(phases) - 1]

    monkeypatch.setattr("app.simulation.openttd.freight_delivery.DeliveryPlan", FakePlan)
    monkeypatch.setattr(freight_continuous, "monitor_network", monitor)

    result = {}
    asyncio.run(
        continuous.conduct_continuous(SimpleNamespace(), prepared, SimpleNamespace(), result)
    )
    assert phases == [("exercise-conduct", "A"), ("monitor", 3)]
    assert result["status"] == continuous.CONTINUOUS_VERIFIED
    for service in range(3):
        receipt = json.loads((directory / f"service-receipt-{service}.json").read_text())
        assert receipt["vehicle"] == created.state.vehicles[service].vehicle
        assert (directory / f"native-plan-{service}.json").is_file()
    record = json.loads((directory / "continuous-finalization.json").read_text())
    assert record["identity"] == continuous.CONTINUOUS
    assert record["summary"] == summary
    assert record["provenance"]["classification"] == "NATIVE_FIVE_YEAR_CONTINUOUS"
    assert record["provenance"]["fourth_vehicle_capex"].startswith("NOT-APPLICABLE")
    assert "UNKNOWN" in record["provenance"]["original_construction_spending"]
    assert "DERIVED" in record["provenance"]["per_year_opex_roi"]


def test_conduct_continuous_refuses_missing_dispatch_receipt(tmp_path, monkeypatch):
    directory = tmp_path / continuous.CONTINUOUS
    directory.mkdir()
    (directory / "PRELAUNCH.json").write_text(json.dumps(stage_metadata(str(tmp_path))))

    async def staged_conduct(*args, **kwargs):
        pass

    monkeypatch.setattr(exercise, "conduct_exercise", staged_conduct)
    with pytest.raises(OSError):
        asyncio.run(
            continuous.conduct_continuous(
                SimpleNamespace(), SimpleNamespace(directory=directory), SimpleNamespace(), {}
            )
        )


def test_run_requires_authorization_but_writes_nothing(tmp_path, monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("authorization must precede preflight and claim")

    monkeypatch.setattr(exercise, "preflight", forbidden)
    with pytest.raises(ValueError, match="authorization"):
        asyncio.run(continuous.run(SimpleNamespace(directory=tmp_path)))
    assert list(tmp_path.iterdir()) == []


def test_verify_states(tmp_path):
    (tmp_path / "PRELAUNCH.json").write_text(
        json.dumps(stage_metadata(str(tmp_path / "canonical")))
    )
    assert continuous.verify(tmp_path) == "AUTHORIZATION_UNVERIFIED"
    (tmp_path / "CLAIM.json").write_text("{}")
    (tmp_path / "result.json").write_text(json.dumps(dict(status="FAILED")))
    assert continuous.verify(tmp_path).startswith("ATTEMPT_NOT_VERIFIED")
    (tmp_path / "result.json").write_text(json.dumps(dict(status=continuous.CONTINUOUS_VERIFIED)))
    from app.simulation.openttd.proof.harness import sha256

    digest = sha256(tmp_path / "result.json")
    (tmp_path / "artifact-manifest.sha256").write_text(f"{digest}  result.json\n")
    assert continuous.verify(tmp_path) == continuous.CONTINUOUS_VERIFIED
