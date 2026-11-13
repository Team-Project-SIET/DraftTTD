"""T-032 five-year continuous operation stage of record (Phase B).

Thin reuse of the T-031 matched-arms machinery with its own identity and
finalization contract: a fresh arm loads the SAME frozen E2 canonical
evidence under the SAME byte-pinned bridge package, adds nothing, and is
monitored to five native economy anniversaries through the retained
continuous machinery. The finalization record binds the retained
continuous summary plus provenance labels (per-year OPEX/ROI are DERIVED
only from observed native accounting; the originals' historical
construction cost stays UNKNOWN and belongs to the E2 create attempt).
Preparation never launches or connects.
"""

import json
import shutil
import sys
from pathlib import Path

from . import canonical_fleet as driver
from . import canonical_fleet_exercise as exercise
from .canonical_fleet_matched import (
    MAX_TICK_GAP,
    arm_budgets,
    arm_receipts,
)
from .harness import write_json

CONTINUOUS = "canonical-fleet-continuous-t032-1"
CONTINUOUS_VERIFIED = "CANONICAL_FIVE_YEAR_CONTINUOUS_VERIFIED"


def continuous_contract():
    return dict(
        mode="canonical-five-year-continuous",
        purchase=False,
        dispatch=True,
        unpause=True,
        intervention_service=None,
        horizon="five-native-anniversaries",
        telemetry=dict(version=2, vehicle_count=3, max_tick_gap=MAX_TICK_GAP),
        correspondence="exact-native-semantic-state",
        finalization="continuous-summary + finalization record",
    )


def prepare(directory, *, canonical):
    return exercise.prepare(
        directory,
        canonical=canonical,
        identity=CONTINUOUS,
        contract=continuous_contract(),
        budgets=arm_budgets("A"),
        capacity_telemetry=dict(version=2, vehicle_count=3, max_tick_gap=MAX_TICK_GAP),
        authorization=(
            "separate explicit authorization; one launch; one connection; no retry/reconnect; "
            "five-anniversary continuous observation; stop on unexpected failure"
        ),
    )


def preflight(prepared):
    return exercise.preflight(prepared, identity=CONTINUOUS, contract=continuous_contract())


def verify(directory):
    return exercise.verify(directory, contract=continuous_contract(), status=CONTINUOUS_VERIFIED)


async def conduct_continuous(backend, prepared, session, result):
    """Reload correspondence, arm-A dispatch (adds nothing), then monitoring."""
    from app.simulation.openttd import freight_continuous
    from app.simulation.openttd.freight_delivery import DeliveryPlan

    await exercise.conduct_exercise(
        backend,
        prepared,
        session,
        result,
        identity=CONTINUOUS,
        contract=continuous_contract(),
        arm="A",
    )
    metadata = json.loads((prepared.directory / "PRELAUNCH.json").read_bytes())
    canonical = Path(metadata["canonical_directory"])
    created = driver.load_created(canonical)
    plans = tuple(
        DeliveryPlan.model_validate_json((canonical / f"native-plan-{n}.json").read_bytes())
        for n in range(3)
    )
    for n, plan in enumerate(plans):
        shutil.copyfile(
            canonical / f"native-plan-{n}.json", prepared.directory / f"native-plan-{n}.json"
        )
    dispatch = json.loads((prepared.directory / "canonical-dispatch.json").read_bytes())
    receipts = arm_receipts(created, dispatch, plans, "A")
    for n, receipt in enumerate(receipts):
        write_json(prepared.directory / f"service-receipt-{n}.json", receipt)
    result["requests"] = 0
    summary = await freight_continuous.monitor_network(
        prepared, session, plans, receipts, metadata, result
    )
    write_json(
        prepared.directory / "continuous-finalization.json",
        dict(
            identity=CONTINUOUS,
            execution_contract=continuous_contract(),
            summary=summary,
            provenance=dict(
                classification="NATIVE_FIVE_YEAR_CONTINUOUS",
                per_year_opex_roi=(
                    "DERIVED only from the observed native accounting in the retained"
                    " continuous snapshots; never manufactured"
                ),
                original_construction_spending=(
                    "UNKNOWN here; it belongs to the E2 create attempt's receipts"
                ),
                fourth_vehicle_capex="NOT-APPLICABLE (this stage adds nothing)",
            ),
        ),
    )
    result["status"] = CONTINUOUS_VERIFIED


async def run(prepared, *, authorize_one_launch=False):
    if authorize_one_launch is not True:
        raise ValueError("separate explicit one-launch authorization required")
    return await exercise.run(
        prepared,
        authorize_one_launch=True,
        identity=CONTINUOUS,
        contract=continuous_contract(),
        conduct=conduct_continuous,
    )


def main():
    import argparse
    import asyncio

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
            print("canonical five-year continuous preflight PASS")
            return 0
        result = asyncio.run(run(prepared, authorize_one_launch=args.authorize_one_launch))
        print(json.dumps(result, sort_keys=True))
        return 0 if result["status"] == CONTINUOUS_VERIFIED else 1
    status = verify(args.directory)
    print(status)
    return 0 if status == CONTINUOUS_VERIFIED else 1


if __name__ == "__main__":
    sys.exit(main())
