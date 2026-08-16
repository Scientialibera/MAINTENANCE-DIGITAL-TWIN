from __future__ import annotations

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class TwinScenario:
    load_multiplier: float = 1.0
    ambient_temperature_delta_c: float = 0.0
    vibration_multiplier: float = 1.0
    bearing_degradation: float = 0.0


def wear_acceleration(scenario: TwinScenario) -> float:
    load = max(0.6, min(1.6, scenario.load_multiplier))
    vibration = max(0.8, min(2.5, scenario.vibration_multiplier))
    bearing = max(0.0, min(1.0, scenario.bearing_degradation))
    temperature = max(-10.0, min(25.0, scenario.ambient_temperature_delta_c))

    load_term = load**1.55
    temperature_term = math.exp(max(0.0, temperature) * 0.012)
    vibration_term = vibration**0.45
    bearing_term = 1.0 + 0.75 * bearing
    return load_term * temperature_term * vibration_term * bearing_term


def simulate_rul(
    p10: float,
    p50: float,
    p90: float,
    scenario: TwinScenario,
) -> dict[str, float]:
    acceleration = wear_acceleration(scenario)
    projection = {
        "p10": max(0.0, p10 / acceleration),
        "p50": max(0.0, p50 / acceleration),
        "p90": max(0.0, p90 / acceleration),
    }
    projection["wear_acceleration"] = acceleration
    return projection


def perturb_telemetry(
    telemetry: dict[str, float],
    scenario: TwinScenario,
) -> dict[str, float]:
    result = dict(telemetry)
    load = scenario.load_multiplier
    heat = scenario.ambient_temperature_delta_c
    vibration = scenario.vibration_multiplier
    bearing = scenario.bearing_degradation

    if "sensor_2" in result:
        result["sensor_2"] += (load - 1.0) * 3.2 + heat * 0.05
    if "sensor_3" in result:
        result["sensor_3"] += (load - 1.0) * 18.0 + heat * 0.12
    if "sensor_4" in result:
        result["sensor_4"] += (load - 1.0) * 24.0 + heat * 0.18
    if "sensor_15" in result:
        result["sensor_15"] *= 1.0 + 0.025 * bearing
    if "sensor_20" in result:
        result["sensor_20"] -= 0.15 * bearing
    if "sensor_21" in result:
        result["sensor_21"] -= 0.11 * bearing

    result["vibration_index"] = (1.0 + 1.7 * bearing) * vibration
    return {key: round(float(value), 5) for key, value in result.items()}
