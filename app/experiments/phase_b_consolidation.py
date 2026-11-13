"""T-033 consolidated OPEX/ROI record of record (Phase B).

Aggregates the Phase B canonical-fleet attempts (T-030 exercise, T-031
matched arms A/B, T-032 five-year continuous) with the E2 canonical
funding context into one record with provenance labels. Native attempt
receipts that do not exist yet (the launches are separately authorized)
stay UNKNOWN-PENDING — never zero, never manufactured. Retained
evidence directories are read-only; the output goes to a fresh
non-retained directory.
"""

import json
import sys
from pathlib import Path

from .financial_attribution import UNKNOWN_NOTE

EVIDENCE_ROOT = "artifacts/runtime"
E2_CANONICAL = "canonical-fleet-create-q3"

PHASE_B_SOURCES = (
    ("T-030", "canonical-fleet-exercise-t030-1", "canonical fleet/capacity exercise"),
    ("T-031-A", "canonical-fleet-matched-a-t031-3", "matched arm A (adds nothing)"),
    ("T-031-B", "canonical-fleet-matched-b-t031-1", "matched arm B (service-1 fourth vehicle)"),
    ("T-032", "canonical-fleet-continuous-t032-1", "five-year continuous operation"),
)

PENDING = "UNKNOWN_PENDING_NATIVE_AUTHORIZATION"
CLASSIFICATION = "PHASE_B_CONSOLIDATED_OPEX_ROI_RECORD"

VERIFIED_STATUSES = {
    "CANONICAL_FLEET_EXERCISE_VERIFIED",
    "CANONICAL_FLEET_MATCHED_VERIFIED",
    "CANONICAL_FIVE_YEAR_CONTINUOUS_VERIFIED",
}


def _amount(value):
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return value
    return None


def _unknown_opex():
    return dict(
        vehicle_running=None,
        loan_interest=None,
        property_maintenance=None,
        provenance="UNKNOWN",
        note="the retained quarterly expense aggregate cannot be split through the read API;"
        " each category stays UNKNOWN until its own native observations exist",
    )


def _dispatch_capex(directory):
    """OBSERVED in-run vehicle-purchase capex from the stage's own dispatch receipt.

    The stages construct nothing in-run (construction spending is
    OBSERVED-zero); the originals' historical construction cost stays
    UNKNOWN and belongs to the E2 create attempt's receipts.
    """
    path = directory / "canonical-dispatch.json"
    if not path.is_file():
        return dict(
            amount_gbp=None,
            provenance="UNKNOWN",
            note="no attempt receipts exist yet; UNKNOWN is not zero",
        )
    amount = _amount(json.loads(path.read_bytes()).get("purchase_capex"))
    return dict(
        amount_gbp=amount,
        provenance="OBSERVED" if amount is not None else "UNKNOWN",
        note="from the attempt's own canonical-dispatch receipt; in-run construction"
        " spending is OBSERVED-zero (the stages construct nothing); the originals'"
        " historical construction cost is UNKNOWN and belongs to the E2 create attempt",
    )


def _source_row(ticket, identity, role, root):
    directory = root / identity
    if not directory.is_dir():
        return dict(
            ticket=ticket,
            identity=identity,
            role=role,
            status=PENDING,
            authorization_gate="separate fresh explicit operator authorization required",
            capex_vehicle_purchase=dict(
                amount_gbp=None,
                provenance="UNKNOWN",
                note="no attempt receipts exist yet; UNKNOWN is not zero",
            ),
            opex=_unknown_opex(),
            revenue=dict(amount_gbp=None, provenance="UNKNOWN"),
            opex_roi=dict(
                provenance="UNKNOWN",
                note="per-year OPEX/ROI are DERIVED only from observed native accounting"
                " in the retained continuous snapshots",
            ),
        )
    result = json.loads((directory / "result.json").read_bytes())
    status = result.get("status")
    financial = {}
    for name in ("arm-record.json", "continuous-finalization.json", "continuous-summary.json"):
        path = directory / name
        if path.is_file():
            summary = json.loads(path.read_bytes())
            financial = (summary.get("summary") or summary).get("financial_metrics") or {}
            break
    return dict(
        ticket=ticket,
        identity=identity,
        role=role,
        status=status if status in VERIFIED_STATUSES else f"NOT_VERIFIED: {status}",
        result_status=status,
        capex_vehicle_purchase=_dispatch_capex(directory),
        opex=_unknown_opex(),
        revenue=dict(
            amount_gbp=_amount(financial.get("freight_revenue")),
            provenance="OBSERVED" if financial else "UNKNOWN",
        ),
        opex_roi=(
            dict(
                financial_metrics=financial,
                provenance="DERIVED" if status in VERIFIED_STATUSES else "UNKNOWN",
            )
            if financial
            else dict(
                provenance="UNKNOWN",
                note="per-year OPEX/ROI are DERIVED only from observed native accounting"
                " in the retained continuous snapshots",
            )
        ),
    )


def _funding_context(root):
    directory = root / E2_CANONICAL
    note_base = "E2 canonical funding context"
    if not directory.is_dir():
        return dict(
            source=E2_CANONICAL,
            capital_gift_gbp=None,
            provenance="UNKNOWN",
            note=note_base + " not found under the artifacts root",
        )
    path = directory / "capital-initialize-response.json"
    if not path.is_file():
        return dict(
            source=E2_CANONICAL,
            capital_gift_gbp=None,
            provenance="UNKNOWN",
            note=note_base + ": no retained capital readback",
        )
    document = json.loads(path.read_bytes())
    amount = _amount(document.get("delta"))
    observed = document.get("completed") and amount is not None
    return dict(
        source=E2_CANONICAL,
        evidence_file=path.name,
        completed=bool(document.get("completed")),
        capital_gift_gbp=amount,
        provenance="OBSERVED" if observed else "UNKNOWN",
        note="OBSERVED gift delta from the retained completed capital readback (E2)",
    )


def consolidate(root=None):
    """Build the consolidated record over whatever retained receipts exist."""
    root = Path(root or EVIDENCE_ROOT)
    rows = [_source_row(*source, root=root) for source in PHASE_B_SOURCES]
    all_observed = all(row["capex_vehicle_purchase"]["provenance"] == "OBSERVED" for row in rows)
    total = (
        sum(row["capex_vehicle_purchase"]["amount_gbp"] for row in rows) if all_observed else None
    )
    return dict(
        classification=CLASSIFICATION,
        funding_context=_funding_context(root),
        sources=rows,
        totals=dict(
            sources=len(rows),
            verified=sum(
                1
                for row in rows
                if isinstance(row["status"], str) and row["status"] in VERIFIED_STATUSES
            ),
            unknown_pending=sum(1 for row in rows if row["status"] == PENDING),
            capex_vehicle_purchase_gbp=dict(
                amount_gbp=total,
                provenance="OBSERVED" if all_observed else "UNKNOWN",
                note="KNOWN only when every attempt's own receipts exist; otherwise UNKNOWN"
                " (UNKNOWN is not zero)",
            ),
        ),
        guards=(
            UNKNOWN_NOTE,
            "per-year OPEX/ROI are DERIVED only from observed native accounting",
            "no per-service revenue is implied",
            "no numeric improvement is forecast",
            "a positive revenue delta alone does not establish profit",
        ),
    )


def render_markdown(record):
    lines = [
        f"# {CLASSIFICATION}",
        "",
        "Funding context: {} {} GBP ({})".format(
            record["funding_context"]["provenance"],
            record["funding_context"]["capital_gift_gbp"],
            record["funding_context"]["note"],
        ),
        "",
        "| Ticket | Identity | Status | CAPEX vehicle purchase | OPEX/ROI |",
        "|---|---|---|---|---|",
    ]
    for row in record["sources"]:
        capex = row["capex_vehicle_purchase"]
        amount = capex["amount_gbp"] if capex["amount_gbp"] is not None else "UNKNOWN"
        lines.append(
            f"| {row['ticket']} | `{row['identity']}` | {row['status']}"
            f" | {amount} ({capex['provenance']}) | {row['opex_roi']['provenance']} |"
        )
    lines += ["", "Guards:", *(f"- {guard}" for guard in record["guards"])]
    return "\n".join(lines) + "\n"


def main():
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifacts-root", type=Path, default=Path(EVIDENCE_ROOT))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    if output.is_relative_to(Path(EVIDENCE_ROOT).resolve()) or output.is_relative_to(
        args.artifacts_root.resolve()
    ):
        raise ValueError("consolidated output must not modify retained evidence")
    output.mkdir(parents=True)
    record = consolidate(args.artifacts_root)
    (output / "phase-b-consolidated-opex.json").write_text(
        json.dumps(record, indent=2, sort_keys=True) + "\n"
    )
    (output / "phase-b-consolidated-opex.md").write_text(render_markdown(record))
    print(json.dumps(record["totals"], sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
