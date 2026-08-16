from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from ml.bearing_features import vibration_features


def load_measurement(path: Path, channel: int) -> np.ndarray:
    frame = pd.read_csv(path, sep=r"\s+", header=None)
    if channel < 0 or channel >= frame.shape[1]:
        raise ValueError(f"Channel {channel} is outside the measurement width {frame.shape[1]}")
    return frame.iloc[:, channel].to_numpy(dtype=float)


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract RMS/kurtosis/crest/spectral features from IMS files")
    parser.add_argument("directory", type=Path)
    parser.add_argument("--channel", type=int, default=0)
    parser.add_argument("--output", type=Path, default=Path("data/processed/ims_features.csv"))
    args = parser.parse_args()

    files = sorted(path for path in args.directory.rglob("*") if path.is_file() and path.suffix.lower() in {"", ".txt"})
    rows = []
    for path in files:
        try:
            features = vibration_features(load_measurement(path, args.channel))
        except (ValueError, pd.errors.ParserError):
            continue
        rows.append({"file": str(path), **features})
    if not rows:
        raise RuntimeError("No compatible IMS vibration measurements were found")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(args.output, index=False)
    print(f"Wrote {len(rows)} feature rows to {args.output}")


if __name__ == "__main__":
    main()
