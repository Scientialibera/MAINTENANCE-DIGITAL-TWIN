from __future__ import annotations

import argparse
from pathlib import Path

from ml.cmapss import add_training_rul, read_cmapss, split_by_engine
from ml.rul_model import QuantileForestRUL


def main() -> None:
    parser = argparse.ArgumentParser(description="Train a C-MAPSS FD001 RUL benchmark model")
    parser.add_argument("--data", default="data/raw/CMAPSSData/train_FD001.txt")
    parser.add_argument("--output", default="models/cmapss_fd001_rul.joblib")
    args = parser.parse_args()

    source = Path(args.data)
    if not source.exists():
        raise FileNotFoundError(
            f"{source} does not exist. Run: python scripts/fetch_nasa_data.py --cmapss"
        )

    frame = add_training_rul(read_cmapss(source), cap=125)
    train, validation = split_by_engine(frame, validation_fraction=0.2)
    model = QuantileForestRUL(random_state=42)
    evaluation = model.fit(train, validation)
    model.save(Path(args.output))

    print("Training complete")
    print(f"Validation engines: {evaluation.validation_engines}")
    print(f"RMSE: {evaluation.rmse:.3f}")
    print(f"MAE: {evaluation.mae:.3f}")
    print(f"NASA asymmetric score: {evaluation.nasa_score:.3f}")
    print(f"P10-P90 interval coverage: {evaluation.interval_80_coverage:.3%}")
    print(f"Saved: {args.output}")


if __name__ == "__main__":
    main()
