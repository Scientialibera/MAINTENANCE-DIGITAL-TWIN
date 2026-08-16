from __future__ import annotations

import numpy as np


def vibration_features(signal: np.ndarray) -> dict[str, float]:
    """Extract standard time/frequency features from a bearing vibration window."""
    values = np.asarray(signal, dtype=float)
    if values.ndim != 1 or values.size < 8:
        raise ValueError("A one-dimensional vibration window with at least 8 samples is required")
    centred = values - values.mean()
    rms = float(np.sqrt(np.mean(centred**2)))
    std = float(np.std(centred))
    fourth = float(np.mean(centred**4))
    kurtosis = fourth / max(std**4, 1e-12)
    peak = float(np.max(np.abs(centred)))
    crest_factor = peak / max(rms, 1e-12)
    spectrum = np.fft.rfft(centred)
    spectral_energy = float(np.sum(np.abs(spectrum) ** 2) / values.size)
    return {
        "rms": rms,
        "kurtosis": kurtosis,
        "crest_factor": crest_factor,
        "spectral_energy": spectral_energy,
    }
