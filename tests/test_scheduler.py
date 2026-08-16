from optimization.scheduler import MaintenanceJob, optimize_schedule


def test_scheduler_respects_single_crew_capacity_and_prioritizes_high_value_work():
    jobs = [
        MaintenanceJob("A", 2, 500_000, 20_000, 5_000, 0.9),
        MaintenanceJob("B", 2, 300_000, 20_000, 5_000, 0.7),
        MaintenanceJob("C", 2, 40_000, 30_000, 8_000, 0.1),
    ]
    result = optimize_schedule(jobs, crew_count=1, horizon_slots=4)
    selected = {item["asset_id"] for item in result["schedule"]}
    assert "A" in selected
    assert "B" in selected
    assert "C" not in selected

    active = [0] * 4
    for item in result["schedule"]:
        for slot in range(item["start_slot"], item["start_slot"] + item["duration_slots"]):
            active[slot] += 1
    assert max(active) <= 1
