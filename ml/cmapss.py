from __future__ import annotations

from pathlib import Path

import pandas as pd

CMAPSS_COLUMNS = [
    "unit_id",
    "cycle",
    "setting_1",
    "setting_2",
    "setting_3",
    *[f"sensor_{index}" for index in range(1, 22)],
]

FD001_INFORMATION_SENSORS = [
    "sensor_2",
    "sensor_3",
    "sensor_4",
    "sensor_7",
    "sensor_8",
    "sensor_9",
    "sensor_11",
    "sensor_12",
    "sensor_13",
    "sensor_14",
    "sensor_15",
    "sensor_17",
    "sensor_20",
    "sensor_21",
]


def read_cmapss(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(path, sep=r"\s+", header=None, names=CMAPSS_COLUMNS)
    frame["unit_id"] = frame["unit_id"].astype(int)
    frame["cycle"] = frame["cycle"].astype(int)
    return frame


def add_training_rul(frame: pd.DataFrame, cap: int | None = 125) -> pd.DataFrame:
    result = frame.copy()
    max_cycles = result.groupby("unit_id")["cycle"].transform("max")
    result["rul_raw"] = max_cycles - result["cycle"]
    result["rul"] = result["rul_raw"].clip(upper=cap) if cap is not None else result["rul_raw"]
    return result


def add_test_rul(frame: pd.DataFrame, final_rul: pd.Series, cap: int | None = 125) -> pd.DataFrame:
    result = frame.copy()
    unit_ids = sorted(result["unit_id"].unique())
    values = final_rul.reset_index(drop=True)
    if len(values) != len(unit_ids):
        raise ValueError("Test RUL vector length does not match test engine count")

    final_lookup = {unit_id: float(values.iloc[index]) for index, unit_id in enumerate(unit_ids)}
    max_test_cycle = result.groupby("unit_id")["cycle"].transform("max")
    result["rul_raw"] = (
        max_test_cycle - result["cycle"] + result["unit_id"].map(final_lookup).astype(float)
    )
    result["rul"] = result["rul_raw"].clip(upper=cap) if cap is not None else result["rul_raw"]
    return result


def split_by_engine(
    frame: pd.DataFrame,
    validation_fraction: float = 0.2,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Keep complete engine trajectories together to avoid temporal leakage."""
    unit_ids = sorted(frame["unit_id"].unique())
    if len(unit_ids) < 5:
        raise ValueError("At least five engine trajectories are required for a group split")
    split_index = max(1, int(round(len(unit_ids) * (1.0 - validation_fraction))))
    train_ids = set(unit_ids[:split_index])
    validation_ids = set(unit_ids[split_index:])
    return (
        frame[frame["unit_id"].isin(train_ids)].copy(),
        frame[frame["unit_id"].isin(validation_ids)].copy(),
    )
