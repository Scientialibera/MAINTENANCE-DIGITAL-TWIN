from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from api.core import settings
from domain.health import failure_probability, health_score, risk_band
from ml.cmapss import add_training_rul, read_cmapss
from services.model_service import RULModelService


SENSOR_KEYS = ["sensor_2", "sensor_3", "sensor_4", "sensor_7", "sensor_11", "sensor_15", "sensor_20", "sensor_21"]

# Known FD001 failure horizons for engines 1-10, surfaced by public C-MAPSS references.
# Used only to construct an offline demonstration fleet when the full NASA archive
# has not been downloaded. It is not model output.
FD001_FAILURE_HORIZONS = {
    1: 192,
    2: 287,
    3: 179,
    4: 189,
    5: 269,
    6: 188,
    7: 259,
    8: 150,
    9: 201,
    10: 222,
}


@dataclass
class FleetData:
    frame: pd.DataFrame
    source_mode: str
    source_note: str


class FleetRepository:
    def __init__(self) -> None:
        self.model_service = RULModelService()

    def _full_training_path(self) -> Path:
        return settings.resolve(settings.cmapss_data_dir) / "train_FD001.txt"

    def _sample_path(self) -> Path:
        return settings.sample_dir / "cmapss_fd001_excerpt.csv"

    def load(self) -> FleetData:
        path = self._full_training_path()
        if path.exists():
            frame = add_training_rul(read_cmapss(path), cap=125)
            return FleetData(
                frame=frame,
                source_mode="nasa-cmapss-fd001",
                source_note=(
                    "Full NASA C-MAPSS FD001 training trajectories. RUL labels are benchmark "
                    "ground truth derived from known run-to-failure horizons."
                ),
            )

        sample = pd.read_csv(self._sample_path())
        # The excerpt contains actual NASA C-MAPSS rows for engine 1. RUL is known
        # because FD001 engine 1 fails at cycle 192.
        sample["rul_raw"] = 192 - sample["cycle"]
        sample["rul"] = sample["rul_raw"].clip(upper=125)
        return FleetData(
            frame=sample,
            source_mode="nasa-cmapss-excerpt",
            source_note=(
                "Bundled real FD001 excerpt for engine 1. Multi-asset plant positions below "
                "are deterministic demonstration states until the full NASA archive is fetched."
            ),
        )

    def fleet(self, limit: int | None = None) -> dict[str, Any]:
        data = self.load()
        limit = limit or settings.max_fleet_assets
        model = self.model_service.model()

        if data.source_mode == "nasa-cmapss-fd001":
            assets = []
            for unit_id, trajectory in data.frame.groupby("unit_id"):
                if len(assets) >= limit:
                    break
                latest = trajectory.sort_values("cycle").iloc[-1]
                if model:
                    estimate = model.predict_latest(trajectory)
                    estimate_source = "trained-model"
                else:
                    known_rul = float(latest["rul"])
                    estimate = {
                        "p10": max(0.0, known_rul - 9.0),
                        "p50": known_rul,
                        "p90": known_rul + 13.0,
                    }
                    estimate_source = "benchmark-label-display"
                assets.append(
                    self._asset_record(
                        unit_id=int(unit_id),
                        cycle=int(latest["cycle"]),
                        estimate=estimate,
                        telemetry={key: float(latest[key]) for key in SENSOR_KEYS},
                        estimate_source=estimate_source,
                        source_mode=data.source_mode,
                    )
                )
        else:
            assets = self._offline_demo_fleet(data.frame, limit)

        availability = 100.0 * sum(asset["risk_band"] != "critical" for asset in assets) / max(1, len(assets))
        predicted_failures = sum(asset["failure_probability"] >= 0.45 for asset in assets)
        oee_proxy = max(
            0.0,
            min(
                100.0,
                91.8
                - 0.7 * predicted_failures
                - 0.12 * sum(100 - asset["health_score"] for asset in assets) / max(1, len(assets)),
            ),
        )
        return {
            "source_mode": data.source_mode,
            "source_note": data.source_note,
            "model_trained": model is not None,
            "kpis": {
                "asset_availability_pct": round(availability, 1),
                "oee_proxy_pct": round(oee_proxy, 1),
                "critical_assets": sum(asset["risk_band"] == "critical" for asset in assets),
                "predicted_failures": predicted_failures,
                "maintenance_backlog": sum(asset["risk_band"] in {"critical", "high", "watch"} for asset in assets),
            },
            "assets": assets,
        }

    def asset(self, asset_id: str) -> dict[str, Any]:
        fleet = self.fleet(limit=50)
        match = next((asset for asset in fleet["assets"] if asset["asset_id"] == asset_id), None)
        if match is None:
            raise KeyError(asset_id)

        data = self.load()
        unit_id = int(asset_id.split("-")[-1])
        if data.source_mode == "nasa-cmapss-fd001" and unit_id in data.frame["unit_id"].unique():
            trajectory = data.frame[data.frame["unit_id"] == unit_id].sort_values("cycle").tail(80)
        else:
            trajectory = self._demo_trajectory(data.frame, match)

        return {
            **match,
            "source_note": fleet["source_note"],
            "telemetry_history": [
                {
                    "cycle": int(row["cycle"]),
                    **{key: round(float(row[key]), 5) for key in SENSOR_KEYS if key in row},
                }
                for _, row in trajectory.iterrows()
            ],
            "maintenance": self._maintenance_parameters(match),
        }

    def _asset_record(
        self,
        unit_id: int,
        cycle: int,
        estimate: dict[str, float],
        telemetry: dict[str, float],
        estimate_source: str,
        source_mode: str,
    ) -> dict[str, Any]:
        uncertainty = max(6.0, estimate["p90"] - estimate["p10"])
        probability = failure_probability(estimate["p50"], uncertainty)
        return {
            "asset_id": f"ENG-{unit_id:03d}",
            "asset_name": f"Compressor Train {unit_id:02d}",
            "cell": f"Cell {((unit_id - 1) // 4) + 1}",
            "cycle": cycle,
            "rul": {key: round(float(value), 1) for key, value in estimate.items()},
            "health_score": health_score(estimate["p50"]),
            "failure_probability": round(probability, 4),
            "risk_band": risk_band(probability),
            "telemetry": {key: round(float(value), 5) for key, value in telemetry.items()},
            "estimate_source": estimate_source,
            "source_mode": source_mode,
        }

    def _offline_demo_fleet(self, sample: pd.DataFrame, limit: int) -> list[dict[str, Any]]:
        latest = sample.sort_values("cycle").iloc[-1]
        base_telemetry = {key: float(latest[key]) for key in SENSOR_KEYS}
        chosen_rul = [14, 24, 37, 51, 66, 78, 89, 103, 114, 121]
        assets = []
        for offset, (unit_id, max_cycle) in enumerate(FD001_FAILURE_HORIZONS.items()):
            if len(assets) >= limit:
                break
            p50 = float(chosen_rul[offset])
            p10 = max(0.0, p50 - (7 + offset % 4))
            p90 = min(150.0, p50 + (10 + offset % 5))
            telemetry = {
                key: value * (1.0 + (offset - 4.5) * 0.0007)
                for key, value in base_telemetry.items()
            }
            cycle = max(1, int(max_cycle - p50))
            assets.append(
                self._asset_record(
                    unit_id=unit_id,
                    cycle=cycle,
                    estimate={"p10": p10, "p50": p50, "p90": p90},
                    telemetry=telemetry,
                    estimate_source="offline-scenario-seed",
                    source_mode="nasa-cmapss-excerpt",
                )
            )
        return assets

    def _demo_trajectory(self, sample: pd.DataFrame, asset: dict[str, Any]) -> pd.DataFrame:
        ordered = sample.sort_values("cycle").copy()
        # Preserve the real C-MAPSS signal shape while translating the cycle window
        # to the demonstration asset's current benchmark position.
        last_cycle = int(asset["cycle"])
        start = max(1, last_cycle - len(ordered) + 1)
        ordered["cycle"] = np.arange(start, start + len(ordered))
        scale = 1.0 + (int(asset["asset_id"].split("-")[-1]) - 5) * 0.0006
        for key in SENSOR_KEYS:
            ordered[key] = ordered[key] * scale
        return ordered

    @staticmethod
    def _maintenance_parameters(asset: dict[str, Any]) -> dict[str, Any]:
        probability = float(asset["failure_probability"])
        severity = 1.0 + probability * 1.8
        return {
            "duration_slots": 1 if probability < 0.45 else 2,
            "expected_failure_cost": round(180_000 * severity, 2),
            "maintenance_cost": round(24_000 + 19_000 * probability, 2),
            "production_loss_per_slot": round(13_500 + 8_500 * probability, 2),
        }
