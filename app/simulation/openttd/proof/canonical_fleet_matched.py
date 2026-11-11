"""T-031 matched A/B arms stage of record (Phase B, separately authorized).

Additive canonical stage family: two fresh arms load the SAME frozen E2
canonical evidence under the SAME byte-pinned bridge package. Arm A adds
nothing; arm B adds only its service-1 vehicle through the paused
capacity-add intervention. Each arm is its own identity, its own CLAIM,
its own explicit authorization; no authorization is shared with the
T-030 exercise, between the arms, or with any earlier attempt. After the
arm's dispatch, the run is monitored to five native economy anniversaries
with the retained continuous machinery; the comparison record is
descriptive only. Preparation never launches or connects.
"""

import json
import shutil
import sys
from pathlib import Path

from app.simulation.openttd.freight_continuous import monitoring_budgets
from app.simulation.openttd.freight_delivery import DeliveryPlan
from app.simulation.openttd.freight_telemetry import validate_bindings

from . import canonical_fleet as driver
from . import canonical_fleet_exercise as exercise
from . import freight_delivery as freight
from .harness import write_json

ARM_A = "canonical-fleet-matched-a-t031-3"
ARM_B = "canonical-fleet-matched-b-t031-1"
ARMS = {"A": ARM_A, "B": ARM_B}
MATCHED_VERIFIED = "CANONICAL_FLEET_MATCHED_VERIFIED"
MAX_TICK_GAP = 100


def matched_contract(arm):
    if arm not in ARMS:
        raise ValueError("canonical matched arm must be A or B")
    return dict(
        mode="canonical-fleet-matched-ab",
        arm=arm,
        purchase=arm == "B",
        dispatch=True,
        unpause=True,
        intervention_service=1 if arm == "B" else None,
        horizon="five-native-anniversaries",
        telemetry=dict(version=2, vehicle_count=3 if arm == "A" else 4, max_tick_gap=MAX_TICK_GAP),
        correspondence="exact-native-semantic-state",
        comparison="descriptive-only",
    )


def arm_budgets(arm):
    return freight.network_budgets(3) | monitoring_budgets(3 if arm == "A" else 4)


def prepare(directory, *, canonical, arm):
    if arm not in ARMS:
        raise ValueError("canonical matched arm must be A or B")
    return exercise.prepare(
        directory,
        canonical=canonical,
        identity=ARMS[arm],
        contract=matched_contract(arm),
        budgets=arm_budgets(arm),
        capacity_telemetry=dict(
            version=2, vehicle_count=3 if arm == "A" else 4, max_tick_gap=MAX_TICK_GAP
        ),
        authorization=(
            "separate explicit authorization; one launch; one connection; no retry/reconnect; "
            f"matched arm {arm} dispatch and five-anniversary observation; "
            "stop on unexpected failure"
        ),
    )


def preflight(prepared, *, arm):
    return exercise.preflight(prepared, identity=ARMS[arm], contract=matched_contract(arm))


def verify(directory, *, arm):
    return exercise.verify(directory, contract=matched_contract(arm), status=MATCHED_VERIFIED)


def arm_receipts(created, dispatch, plans, arm):
    """Per-service receipts in the continuous evidence shape.

    Zero in-run construction spending is OBSERVED (the arms construct
    nothing); the originals' historical construction cost stays UNKNOWN and
    belongs to the E2 create attempt's receipts, never to an arm.
    """
    receipts = []
    for n, vehicle in enumerate(created.state.vehicles):
        receipts.append(
            dict(
                service=n,
                vehicle=vehicle.vehicle,
                route_id=plans[n].digest,
                construction_purchase_spending=0,
            )
        )
    if arm == "B":
        binding = dispatch["binding"]
        extras = [
            dict(
                service=1,
                vehicle=binding["vehicle"],
                purchase_capex=dispatch["purchase_capex"],
            )
        ]
        receipts[1]["additional_vehicles"] = extras
    else:
        extras = []
    bindings = [dict(service=r["service"], vehicle=r["vehicle"]) for r in receipts]
    bindings.extend(dict(service=e["service"], vehicle=e["vehicle"]) for e in extras)
    validate_bindings(bindings)
    return receipts


def _read_dispatch(prepared):
    return json.loads((prepared.directory / "canonical-dispatch.json").read_bytes())


async def conduct_arm(backend, prepared, session, result, *, arm):
    """Reload correspondence, one arm dispatch, then five-anniversary monitoring."""
    from app.simulation.openttd import freight_continuous

    await exercise.conduct_exercise(
        backend,
        prepared,
        session,
        result,
        identity=ARMS[arm],
        contract=matched_contract(arm),
        arm=arm,
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
    dispatch = _read_dispatch(prepared)
    receipts = arm_receipts(created, dispatch, plans, arm)
    for n, receipt in enumerate(receipts):
        write_json(prepared.directory / f"service-receipt-{n}.json", receipt)
    result["requests"] = 0
    summary = await freight_continuous.monitor_network(
        prepared, session, plans, receipts, metadata, result
    )
    write_json(
        prepared.directory / "arm-record.json",
        dict(
            arm=arm,
            identity=ARMS[arm],
            execution_contract=matched_contract(arm),
            dispatch_purchase_capex=dispatch["purchase_capex"],
            summary=summary,
            provenance=dict(
                in_run_construction_spending="OBSERVED-zero (the arm constructs nothing)",
                original_construction_spending=(
                    "UNKNOWN here; it belongs to the E2 create attempt's receipts"
                ),
                fourth_vehicle_capex="OBSERVED" if arm == "B" else "NOT-APPLICABLE",
            ),
        ),
    )
    result["status"] = MATCHED_VERIFIED


async def run(prepared, *, arm, authorize_one_launch=False):
    return await exercise.run(
        prepared,
        authorize_one_launch=authorize_one_launch,
        identity=ARMS[arm],
        contract=matched_contract(arm),
        conduct=lambda backend, session_prepared, sess, res: conduct_arm(
            backend, session_prepared, sess, res, arm=arm
        ),
    )


def _numeric_delta(a, b):
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return dict(a=a, b=b, delta_b_minus_a=b - a, provenance="OBSERVED")
    return dict(a=a, b=b, provenance="UNKNOWN")


def compare_arms(a_directory, b_directory, *, output=None):
    """Descriptive B-vs-A record from the arms' own receipts. Never a claim."""
    a_directory, b_directory = Path(a_directory), Path(b_directory)
    a_record = json.loads((a_directory / "arm-record.json").read_bytes())
    b_record = json.loads((b_directory / "arm-record.json").read_bytes())
    if a_record["arm"] != "A" or b_record["arm"] != "B":
        raise ValueError("descriptive comparison requires the A and B arm records")
    metrics = {
        key: _numeric_delta(
            a_record["summary"]["financial_metrics"].get(key),
            b_record["summary"]["financial_metrics"].get(key),
        )
        for key in sorted(
            set(a_record["summary"]["financial_metrics"])
            | set(b_record["summary"]["financial_metrics"])
        )
    }
    comparison = dict(
        classification="DESCRIPTIVE_MATCHED_AB_COMPARISON",
        arm_a=dict(identity=a_record["identity"], directory=str(a_directory)),
        arm_b=dict(identity=b_record["identity"], directory=str(b_directory)),
        fourth_vehicle_capex_gbp=dict(
            a=0, b=b_record["dispatch_purchase_capex"], provenance="OBSERVED"
        ),
        financial_metrics=metrics,
        observation_counts=dict(
            a=a_record["summary"]["observation_counts"],
            b=b_record["summary"]["observation_counts"],
        ),
        guards=(
            "a positive revenue delta alone does not establish profit",
            "no per-service revenue is implied",
            "no numeric improvement is forecast",
            "UNKNOWN is not zero",
        ),
    )
    if output is not None:
        write_json(Path(output) / "matched-comparison.json", comparison)
    return comparison


def main():
    import argparse
    import asyncio

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prepare", "preflight", "verify", "run", "compare"))
    parser.add_argument("directory", type=Path)
    parser.add_argument("--canonical", type=Path)
    parser.add_argument("--arm", choices=("A", "B"))
    parser.add_argument("--other-arm-directory", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--authorize-one-launch",
        action="store_true",
        help="fresh explicit operator authorization required for the ONE launch",
    )
    args = parser.parse_args()
    if args.command == "compare":
        comparison = compare_arms(args.directory, args.other_arm_directory, output=args.output)
        print(json.dumps(comparison, sort_keys=True))
        return 0
    if args.arm is None:
        parser.error("matched arms require --arm A or B")
    if args.command == "prepare":
        if args.canonical is None:
            parser.error("prepare requires --canonical pointing at the E2 created evidence")
        prepared = prepare(args.directory, canonical=args.canonical, arm=args.arm)
        print(f"prepared {prepared.directory} arm {args.arm} (offline; no launch)")
        return 0
    if args.command in ("preflight", "run"):
        prepared = driver.reopen(args.directory)
        if args.command == "preflight":
            preflight(prepared, arm=args.arm)
            print(f"canonical matched arm {args.arm} preflight PASS")
            return 0
        result = asyncio.run(
            run(prepared, arm=args.arm, authorize_one_launch=args.authorize_one_launch)
        )
        print(json.dumps(result, sort_keys=True))
        return 0 if result["status"] == MATCHED_VERIFIED else 1
    status = verify(args.directory, arm=args.arm)
    print(status)
    return 0 if status == MATCHED_VERIFIED else 1


if __name__ == "__main__":
    sys.exit(main())
