from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor

from ml.features import build_cycle_features, feature_columns
from ml.metrics import interval_coverage, regression_metrics


@dataclass(frozen=True)
class ModelEvaluation:
    rmse: float
    mae: float
    nasa_score: float
    interval_80_coverage: float
    validation_engines: list[int]
    validation_rows: int


class QuantileForestRUL:
    """Random-forest RUL regressor with empirical tree-prediction intervals."""

    def __init__(self, random_state: int = 42) -> None:
        self.estimator = RandomForestRegressor(
            n_estimators=240,
            max_depth=18,
            min_samples_leaf=3,
            max_features=0.72,
            n_jobs=-1,
            random_state=random_state,
        )
        self.feature_names: list[str] = []
        self.evaluation: ModelEvaluation | None = None

    def fit(self, train_frame: pd.DataFrame, validation_frame: pd.DataFrame) -> ModelEvaluation:
        train_features = build_cycle_features(train_frame)
        validation_features = build_cycle_features(validation_frame)
        self.feature_names = feature_columns(train_features)

        self.estimator.fit(train_features[self.feature_names], train_features["rul"])
        predictions = self.predict(validation_features)
        metrics = regression_metrics(
            validation_features["rul"].to_numpy(),
            predictions["p50"],
        )
        coverage = interval_coverage(
            validation_features["rul"].to_numpy(),
            predictions["p10"],
            predictions["p90"],
        )
        self.evaluation = ModelEvaluation(
            rmse=metrics["rmse"],
            mae=metrics["mae"],
            nasa_score=metrics["nasa_score"],
            interval_80_coverage=coverage,
            validation_engines=sorted(validation_features["unit_id"].unique().tolist()),
            validation_rows=len(validation_features),
        )
        return self.evaluation

    def predict(self, featured_frame: pd.DataFrame) -> dict[str, np.ndarray]:
        if not self.feature_names:
            raise RuntimeError("Model has not been fitted")
        matrix = featured_frame[self.feature_names]
        tree_predictions = np.vstack(
            [tree.predict(matrix) for tree in self.estimator.estimators_]
        )
        return {
            "p10": np.quantile(tree_predictions, 0.10, axis=0),
            "p50": np.quantile(tree_predictions, 0.50, axis=0),
            "p90": np.quantile(tree_predictions, 0.90, axis=0),
        }

    def predict_latest(self, trajectory: pd.DataFrame) -> dict[str, float]:
        featured = build_cycle_features(trajectory)
        prediction = self.predict(featured.tail(1))
        p10 = max(0.0, float(prediction["p10"][0]))
        p50 = max(p10, float(prediction["p50"][0]))
        p90 = max(p50, float(prediction["p90"][0]))
        return {"p10": p10, "p50": p50, "p90": p90}

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(
            {
                "estimator": self.estimator,
                "feature_names": self.feature_names,
                "evaluation": asdict(self.evaluation) if self.evaluation else None,
            },
            path,
        )

    @classmethod
    def load(cls, path: Path) -> "QuantileForestRUL":
        artifact: dict[str, Any] = joblib.load(path)
        model = cls()
        model.estimator = artifact["estimator"]
        model.feature_names = list(artifact["feature_names"])
        evaluation = artifact.get("evaluation")
        if evaluation:
            model.evaluation = ModelEvaluation(**evaluation)
        return model
