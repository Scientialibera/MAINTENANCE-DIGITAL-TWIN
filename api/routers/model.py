from __future__ import annotations

from fastapi import APIRouter

from services.model_service import RULModelService

router = APIRouter(prefix="/api/model", tags=["model"])


@router.get("/status")
def status() -> dict:
    return RULModelService().status()


@router.get("/validation")
def validation() -> dict:
    status_payload = RULModelService().status()
    return {
        "trained_model_available": status_payload["trained_model_available"],
        "evaluation": status_payload["evaluation"],
        "benchmark_protocol": {
            "dataset": "NASA C-MAPSS FD001",
            "grouping": "whole engine trajectories",
            "target": "capped RUL, maximum 125 cycles",
            "point_metrics": ["RMSE", "MAE", "NASA asymmetric score"],
            "uncertainty_metric": "P10-P90 empirical tree interval coverage",
        },
        "note": (
            "No metric is manufactured when the trained artifact is absent. "
            "Run scripts/train_rul_model.py after downloading the NASA archive."
        ),
    }
