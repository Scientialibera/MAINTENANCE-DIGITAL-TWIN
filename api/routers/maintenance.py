from __future__ import annotations

from fastapi import APIRouter

from api.schemas import MaintenanceOptimizeRequest
from optimization.scheduler import MaintenanceJob, optimize_schedule
from services.fleet_repository import FleetRepository

router = APIRouter(prefix="/api/maintenance", tags=["maintenance"])


@router.post("/optimize")
def optimize(request: MaintenanceOptimizeRequest) -> dict:
    repository = FleetRepository()
    fleet = repository.fleet()
    jobs = []
    for asset in fleet["assets"]:
        detail = repository.asset(asset["asset_id"])
        parameters = detail["maintenance"]
        jobs.append(
            MaintenanceJob(
                asset_id=asset["asset_id"],
                duration_slots=int(parameters["duration_slots"]),
                expected_failure_cost=float(parameters["expected_failure_cost"]),
                maintenance_cost=float(parameters["maintenance_cost"]),
                production_loss_per_slot=float(parameters["production_loss_per_slot"]),
                failure_probability=float(asset["failure_probability"]),
            )
        )
    result = optimize_schedule(
        jobs,
        crew_count=request.crew_count,
        horizon_slots=request.horizon_slots,
        slot_hours=request.slot_hours,
        risk_tolerance=request.risk_tolerance,
    )
    result["input_assets"] = len(jobs)
    result["boundary"] = (
        "Cost values are transparent demonstration assumptions. Replace them with plant-specific "
        "maintenance, downtime and failure consequences for production decisions."
    )
    return result
