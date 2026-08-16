from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from typing import Iterable

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import lil_matrix


@dataclass(frozen=True)
class MaintenanceJob:
    asset_id: str
    duration_slots: int
    expected_failure_cost: float
    maintenance_cost: float
    production_loss_per_slot: float
    failure_probability: float


@dataclass(frozen=True)
class ScheduledJob:
    asset_id: str
    start_slot: int
    duration_slots: int
    expected_failure_cost_avoided: float
    maintenance_cost: float
    production_loss: float


def optimize_schedule(
    jobs: Iterable[MaintenanceJob],
    crew_count: int,
    horizon_slots: int = 14,
    slot_hours: int = 12,
    risk_tolerance: float = 1.0,
    start_time: datetime | None = None,
) -> dict:
    jobs = list(jobs)
    if not jobs:
        return {"schedule": [], "summary": _summary([], jobs), "slots": []}
    if crew_count < 1:
        raise ValueError("crew_count must be at least 1")
    if horizon_slots < 1:
        raise ValueError("horizon_slots must be positive")

    candidates: list[tuple[int, int]] = []
    for job_index, job in enumerate(jobs):
        for start_slot in range(0, horizon_slots - job.duration_slots + 1):
            candidates.append((job_index, start_slot))

    coefficients = np.zeros(len(candidates))
    for variable_index, (job_index, _) in enumerate(candidates):
        job = jobs[job_index]
        avoided = job.expected_failure_cost * job.failure_probability * risk_tolerance
        planned = job.maintenance_cost + job.production_loss_per_slot * job.duration_slots
        coefficients[variable_index] = planned - avoided

    rows = len(jobs) + horizon_slots
    matrix = lil_matrix((rows, len(candidates)), dtype=float)
    lower = np.full(rows, -np.inf)
    upper = np.ones(rows)

    for variable_index, (job_index, start_slot) in enumerate(candidates):
        matrix[job_index, variable_index] = 1.0
        job = jobs[job_index]
        for slot in range(start_slot, start_slot + job.duration_slots):
            matrix[len(jobs) + slot, variable_index] = 1.0

    for slot in range(horizon_slots):
        upper[len(jobs) + slot] = float(crew_count)

    result = milp(
        c=coefficients,
        integrality=np.ones(len(candidates)),
        bounds=Bounds(np.zeros(len(candidates)), np.ones(len(candidates))),
        constraints=LinearConstraint(matrix.tocsr(), lower, upper),
        options={"time_limit": 8.0},
    )
    if not result.success:
        raise RuntimeError(f"Maintenance optimization failed: {result.message}")

    scheduled: list[ScheduledJob] = []
    for variable_index, selected in enumerate(result.x):
        if selected < 0.5:
            continue
        job_index, start_slot = candidates[variable_index]
        job = jobs[job_index]
        scheduled.append(
            ScheduledJob(
                asset_id=job.asset_id,
                start_slot=start_slot,
                duration_slots=job.duration_slots,
                expected_failure_cost_avoided=(
                    job.expected_failure_cost * job.failure_probability * risk_tolerance
                ),
                maintenance_cost=job.maintenance_cost,
                production_loss=job.production_loss_per_slot * job.duration_slots,
            )
        )

    scheduled.sort(key=lambda item: (item.start_slot, item.asset_id))
    start_time = start_time or datetime(2026, 8, 17, 6, 0)
    slots = [
        {
            "slot": slot,
            "start": (start_time + timedelta(hours=slot * slot_hours)).isoformat(),
            "hours": slot_hours,
        }
        for slot in range(horizon_slots)
    ]
    return {
        "schedule": [asdict(item) for item in scheduled],
        "summary": _summary(scheduled, jobs),
        "slots": slots,
        "solver": "scipy.optimize.milp",
        "objective": "maintenance + production loss - risk-weighted expected failure cost avoided",
    }


def _summary(scheduled: list[ScheduledJob], jobs: list[MaintenanceJob]) -> dict[str, float]:
    baseline_expected_failure = sum(
        job.expected_failure_cost * job.failure_probability for job in jobs
    )
    avoided = sum(item.expected_failure_cost_avoided for item in scheduled)
    maintenance = sum(item.maintenance_cost for item in scheduled)
    production_loss = sum(item.production_loss for item in scheduled)
    return {
        "scheduled_assets": float(len(scheduled)),
        "baseline_expected_failure_cost": round(baseline_expected_failure, 2),
        "failure_cost_avoided": round(avoided, 2),
        "maintenance_cost": round(maintenance, 2),
        "production_loss": round(production_loss, 2),
        "net_expected_value": round(avoided - maintenance - production_loss, 2),
    }
