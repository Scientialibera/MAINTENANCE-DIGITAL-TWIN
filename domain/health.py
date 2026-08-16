from __future__ import annotations

import math


def failure_probability(rul_cycles: float, uncertainty_width: float = 20.0) -> float:
    """Dashboard prioritization transform, not a calibrated plant failure probability."""
    width = max(5.0, uncertainty_width)
    centre = 28.0
    return 1.0 / (1.0 + math.exp((rul_cycles - centre) / (width / 3.0)))


def health_score(rul_cycles: float, max_reference_rul: float = 125.0) -> float:
    score = 100.0 * max(0.0, min(1.0, rul_cycles / max_reference_rul))
    return round(score, 1)


def risk_band(probability: float) -> str:
    if probability >= 0.75:
        return "critical"
    if probability >= 0.45:
        return "high"
    if probability >= 0.20:
        return "watch"
    return "normal"
