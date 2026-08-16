from __future__ import annotations

from fastapi import APIRouter, HTTPException

from services.fleet_repository import FleetRepository

router = APIRouter(prefix="/api", tags=["fleet"])


@router.get("/fleet")
def fleet() -> dict:
    return FleetRepository().fleet()


@router.get("/assets/{asset_id}")
def asset(asset_id: str) -> dict:
    try:
        return FleetRepository().asset(asset_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Unknown asset: {asset_id}") from exc
