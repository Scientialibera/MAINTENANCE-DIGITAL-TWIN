from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_fleet_returns_assets_and_source_boundary():
    response = client.get("/api/fleet")
    assert response.status_code == 200
    payload = response.json()
    assert payload["assets"]
    assert payload["source_mode"].startswith("nasa-cmapss")
    assert "source_note" in payload


def test_twin_scenario_changes_rul():
    fleet = client.get("/api/fleet").json()
    asset_id = fleet["assets"][0]["asset_id"]
    response = client.post(
        f"/api/assets/{asset_id}/simulate",
        json={
            "load_multiplier": 1.35,
            "ambient_temperature_delta_c": 8,
            "vibration_multiplier": 1.5,
            "bearing_degradation": 0.5,
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["projection"]["rul"]["p50"] < payload["baseline"]["rul"]["p50"]


def test_maintenance_optimizer_endpoint():
    response = client.post(
        "/api/maintenance/optimize",
        json={"crew_count": 2, "horizon_slots": 14, "slot_hours": 12, "risk_tolerance": 1.0},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["solver"] == "scipy.optimize.milp"
    assert "net_expected_value" in payload["summary"]
