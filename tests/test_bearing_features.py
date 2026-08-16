import numpy as np

from ml.bearing_features import vibration_features


def test_vibration_features_detect_larger_impulse_energy():
    base = np.sin(np.linspace(0, 20, 2048))
    fault = base.copy()
    fault[100::250] += 7
    base_features = vibration_features(base)
    fault_features = vibration_features(fault)
    assert fault_features["rms"] > base_features["rms"]
    assert fault_features["kurtosis"] > base_features["kurtosis"]
    assert fault_features["crest_factor"] > base_features["crest_factor"]
