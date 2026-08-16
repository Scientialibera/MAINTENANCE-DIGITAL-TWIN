from domain.twin import TwinScenario, simulate_rul, wear_acceleration


def test_high_load_and_bearing_degradation_accelerate_wear():
    baseline = wear_acceleration(TwinScenario())
    stressed = wear_acceleration(
        TwinScenario(load_multiplier=1.35, ambient_temperature_delta_c=8, vibration_multiplier=1.6, bearing_degradation=0.6)
    )
    assert baseline == 1.0
    assert stressed > baseline


def test_stressed_scenario_reduces_all_rul_quantiles():
    result = simulate_rul(
        25,
        40,
        58,
        TwinScenario(load_multiplier=1.3, bearing_degradation=0.5),
    )
    assert result["p10"] < 25
    assert result["p50"] < 40
    assert result["p90"] < 58
    assert result["p10"] <= result["p50"] <= result["p90"]
