"""Offline regression for the T-033 consolidated OPEX/ROI record of record.

Zero native processes: pending-row honesty, observed capex aggregation
from staged receipts, funding context, totals and guards, markdown
rendering, and the retained-evidence output guard.
"""

import json

import pytest

from app.experiments import phase_b_consolidation as pbc


def test_pending_sources_stay_unknown_not_zero(tmp_path):
    record = pbc.consolidate(tmp_path)
    assert record["classification"] == pbc.CLASSIFICATION
    assert record["totals"]["unknown_pending"] == 4
    assert record["totals"]["verified"] == 0
    assert record["totals"]["capex_vehicle_purchase_gbp"] == dict(
        amount_gbp=None,
        provenance="UNKNOWN",
        note=pbc.consolidate(tmp_path)["totals"]["capex_vehicle_purchase_gbp"]["note"],
    )
    for row in record["sources"]:
        assert row["status"] == pbc.PENDING
        assert row["capex_vehicle_purchase"]["amount_gbp"] is None
        assert row["capex_vehicle_purchase"]["provenance"] == "UNKNOWN"
        assert row["opex"]["vehicle_running"] is None
        assert row["revenue"]["amount_gbp"] is None
        assert row["opex_roi"]["provenance"] == "UNKNOWN"
    assert "UNKNOWN is not zero; missing transactions are never manufactured." in record["guards"]


def _stage(tmp_path, identity, *, status, purchase_capex, financial=None):
    directory = tmp_path / identity
    directory.mkdir()
    (directory / "result.json").write_text(json.dumps(dict(status=status)))
    (directory / "canonical-dispatch.json").write_text(
        json.dumps(dict(purchase_capex=purchase_capex))
    )
    if financial is not None:
        (directory / "arm-record.json").write_text(
            json.dumps(dict(summary=dict(financial_metrics=financial)))
        )


def test_observed_capex_and_revenue_labeled_from_own_receipts(tmp_path):
    _stage(
        tmp_path,
        "canonical-fleet-exercise-t030-1",
        status="CANONICAL_FLEET_EXERCISE_VERIFIED",
        purchase_capex=31200,
    )
    _stage(
        tmp_path,
        "canonical-fleet-matched-a-t031-3",
        status="CANONICAL_FLEET_MATCHED_VERIFIED",
        purchase_capex=0,
    )
    _stage(
        tmp_path,
        "canonical-fleet-matched-b-t031-1",
        status="CANONICAL_FLEET_MATCHED_VERIFIED",
        purchase_capex=31200,
        financial=dict(freight_revenue=100, delivered_cargo=7),
    )
    _stage(
        tmp_path,
        "canonical-fleet-continuous-t032-1",
        status="FAILED",
        purchase_capex=0,
        financial=dict(freight_revenue=42),
    )
    record = pbc.consolidate(tmp_path)
    rows = {row["ticket"]: row for row in record["sources"]}
    assert rows["T-030"]["capex_vehicle_purchase"] == dict(
        amount_gbp=31200,
        provenance="OBSERVED",
        note=rows["T-030"]["capex_vehicle_purchase"]["note"],
    )
    assert rows["T-031-A"]["capex_vehicle_purchase"]["amount_gbp"] == 0
    assert rows["T-031-B"]["revenue"] == dict(amount_gbp=100, provenance="OBSERVED")
    assert rows["T-031-B"]["opex_roi"]["provenance"] == "DERIVED"
    assert rows["T-030"]["status"] == "CANONICAL_FLEET_EXERCISE_VERIFIED"
    assert rows["T-032"]["status"].startswith("NOT_VERIFIED: FAILED")
    assert rows["T-032"]["opex_roi"]["provenance"] == "UNKNOWN"
    assert record["totals"]["verified"] == 3
    assert record["totals"]["unknown_pending"] == 0
    # Every attempt dir exists with its own dispatch receipt, so the
    # consolidated capex total is OBSERVED even though one row is FAILED
    # (the FAILED status stays visible on that row; pending attempts,
    # which have no receipts at all, keep the total UNKNOWN).
    assert record["totals"]["capex_vehicle_purchase_gbp"]["amount_gbp"] == 62400
    assert record["totals"]["capex_vehicle_purchase_gbp"]["provenance"] == "OBSERVED"


def test_funding_context_from_retained_e2_readback(tmp_path):
    e2 = tmp_path / pbc.E2_CANONICAL
    e2.mkdir()
    (e2 / "capital-initialize-response.json").write_text(
        json.dumps(dict(completed=True, delta=400000))
    )
    context = pbc.consolidate(tmp_path)["funding_context"]
    assert context["capital_gift_gbp"] == 400000
    assert context["provenance"] == "OBSERVED"
    (e2 / "capital-initialize-response.json").write_text(
        json.dumps(dict(completed=False, delta=400000))
    )
    assert pbc.consolidate(tmp_path)["funding_context"]["provenance"] == "UNKNOWN"


def test_render_markdown_carries_labels_and_guards(tmp_path):
    record = pbc.consolidate(tmp_path)
    rendered = pbc.render_markdown(record)
    assert pbc.CLASSIFICATION in rendered
    assert "| T-032 | `canonical-fleet-continuous-t032-1` | UNKNOWN_PENDING" in rendered
    assert rendered.count("UNKNOWN") >= 4
    for guard in record["guards"]:
        assert guard in rendered


def test_cli_refuses_output_under_retained_evidence(tmp_path):
    out = tmp_path / "artifacts" / "inside"
    with pytest.raises(ValueError, match="must not modify retained evidence"):
        _run_main(tmp_path, out)


def _run_main(tmp_path, output):
    import sys as _sys

    argv = _sys.argv
    _sys.argv = [
        "consolidate",
        "--artifacts-root",
        str(tmp_path / "artifacts"),
        "--output",
        str(output),
    ]
    try:
        return pbc.main()
    finally:
        _sys.argv = argv


def test_cli_writes_record_outside_retained_evidence(tmp_path):
    out = tmp_path / "analysis" / "phase-b"
    assert _run_main(tmp_path, out) == 0
    record = json.loads((out / "phase-b-consolidated-opex.json").read_text())
    assert record["classification"] == pbc.CLASSIFICATION
    assert (out / "phase-b-consolidated-opex.md").is_file()
