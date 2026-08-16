from __future__ import annotations

from pydantic import BaseModel, Field


class TwinScenarioRequest(BaseModel):
    load_multiplier: float = Field(1.0, ge=0.6, le=1.6)
    ambient_temperature_delta_c: float = Field(0.0, ge=-10, le=25)
    vibration_multiplier: float = Field(1.0, ge=0.8, le=2.5)
    bearing_degradation: float = Field(0.0, ge=0, le=1)


class MaintenanceOptimizeRequest(BaseModel):
    crew_count: int = Field(2, ge=1, le=8)
    horizon_slots: int = Field(14, ge=4, le=28)
    slot_hours: int = Field(12, ge=4, le=24)
    risk_tolerance: float = Field(1.0, ge=0.5, le=2.5)
