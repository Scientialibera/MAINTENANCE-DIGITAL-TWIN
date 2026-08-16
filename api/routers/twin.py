from __future__ import annotations

from fastapi import APIRouter, HTTPException

from api.schemas import TwinScenarioRequest
from domain.twin import TwinScenario
from services.twin_service import TwinService

router = APIRouter(prefix="/api/assets", tags=["digital-twin"])


@router.post("/{asset_id}/simulate")
def simulate(asset_id: str, request: TwinScenarioRequest) -> dict:
    try:
        return TwinService().simulate(asset_id, TwinScenario(**request.model_dump()))
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Unknown asset: {asset_id}") from exc
