from __future__ import annotations

from domain.health import failure_probability, health_score, risk_band
from domain.twin import TwinScenario, perturb_telemetry, simulate_rul
from services.fleet_repository import FleetRepository


class TwinService:
    def __init__(self) -> None:
        self.repository = FleetRepository()

    def simulate(self, asset_id: str, scenario: TwinScenario) -> dict:
        asset = self.repository.asset(asset_id)
        projected_rul = simulate_rul(
            asset["rul"]["p10"],
            asset["rul"]["p50"],
            asset["rul"]["p90"],
            scenario,
        )
        probability = failure_probability(
            projected_rul["p50"],
            projected_rul["p90"] - projected_rul["p10"],
        )
        return {
            "asset_id": asset_id,
            "baseline": {
                "rul": asset["rul"],
                "health_score": asset["health_score"],
                "failure_probability": asset["failure_probability"],
                "risk_band": asset["risk_band"],
                "telemetry": asset["telemetry"],
            },
            "scenario": {
                "load_multiplier": scenario.load_multiplier,
                "ambient_temperature_delta_c": scenario.ambient_temperature_delta_c,
                "vibration_multiplier": scenario.vibration_multiplier,
                "bearing_degradation": scenario.bearing_degradation,
            },
            "projection": {
                "rul": {key: round(value, 2) for key, value in projected_rul.items() if key != "wear_acceleration"},
                "wear_acceleration": round(projected_rul["wear_acceleration"], 3),
                "health_score": health_score(projected_rul["p50"]),
                "failure_probability": round(probability, 4),
                "risk_band": risk_band(probability),
                "telemetry": perturb_telemetry(asset["telemetry"], scenario),
            },
            "boundary": (
                "Scenario acceleration is a reduced-order engineering what-if layer around "
                "the prognostic estimate. It is not a validated physics-of-failure model."
            ),
        }
