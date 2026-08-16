from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

from api.core import settings
from ml.rul_model import QuantileForestRUL


class RULModelService:
    def __init__(self) -> None:
        self.path = settings.resolve(settings.rul_model_path)
        self._model: QuantileForestRUL | None = None

    @property
    def available(self) -> bool:
        return self.path.exists()

    def model(self) -> QuantileForestRUL | None:
        if not self.available:
            return None
        if self._model is None:
            self._model = QuantileForestRUL.load(self.path)
        return self._model

    def status(self) -> dict:
        model = self.model()
        evaluation = None
        if model and model.evaluation:
            evaluation = asdict(model.evaluation)
        return {
            "trained_model_available": model is not None,
            "artifact_path": str(self.path),
            "model_type": "RandomForestRegressor with empirical tree quantiles",
            "target": "Remaining useful life in C-MAPSS engine cycles",
            "rul_cap_cycles": 125,
            "validation": (
                "Whole-engine holdout. Engine trajectories are never split across training and validation."
            ),
            "evaluation": evaluation,
            "boundary": (
                "C-MAPSS is simulator-generated benchmark data. Plant deployment requires "
                "retraining and calibration on asset-specific telemetry and maintenance events."
            ),
        }
