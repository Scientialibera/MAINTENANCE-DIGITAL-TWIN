from __future__ import annotations

import numpy as np
import pandas as pd

from ml.cmapss import FD001_INFORMATION_SENSORS


def _rolling_slope(values: np.ndarray) -> float:
    if len(values) < 2:
        return 0.0
    x = np.arange(len(values), dtype=float)
    x_centered = x - x.mean()
    denominator = float(np.sum(x_centered**2))
    if denominator <= 0:
        return 0.0
    y = values.astype(float)
    return float(np.sum(x_centered * (y - y.mean())) / denominator)


def build_cycle_features(
    frame: pd.DataFrame,
    sensors: list[str] | None = None,
    windows: tuple[int, ...] = (5, 15),
) -> pd.DataFrame:
    sensors = sensors or FD001_INFORMATION_SENSORS
    missing = [sensor for sensor in sensors if sensor not in frame.columns]
    if missing:
        raise ValueError(f"Missing sensor columns: {missing}")

    result = frame.copy().sort_values(["unit_id", "cycle"]).reset_index(drop=True)
    grouped = result.groupby("unit_id", group_keys=False)

    for sensor in sensors:
        for window in windows:
            result[f"{sensor}_mean_{window}"] = grouped[sensor].transform(
                lambda series: series.rolling(window, min_periods=1).mean()
            )
            result[f"{sensor}_std_{window}"] = grouped[sensor].transform(
                lambda series: series.rolling(window, min_periods=2).std().fillna(0.0)
            )
            result[f"{sensor}_slope_{window}"] = grouped[sensor].transform(
                lambda series: series.rolling(window, min_periods=2).apply(
                    _rolling_slope, raw=True
                ).fillna(0.0)
            )

    result["cycle_fraction_proxy"] = result["cycle"] / result.groupby("unit_id")[
        "cycle"
    ].transform("max")
    return result


def feature_columns(frame: pd.DataFrame) -> list[str]:
    excluded = {"unit_id", "rul", "rul_raw"}
    return [
        column
        for column in frame.columns
        if column not in excluded and pd.api.types.is_numeric_dtype(frame[column])
    ]
