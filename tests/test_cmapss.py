from pathlib import Path

import pandas as pd

from ml.cmapss import add_training_rul, split_by_engine


def test_rul_is_derived_from_each_engine_failure_horizon():
    frame = pd.DataFrame(
        {
            "unit_id": [1, 1, 1, 2, 2],
            "cycle": [1, 2, 3, 1, 2],
        }
    )
    result = add_training_rul(frame, cap=None)
    assert result[result.unit_id == 1]["rul_raw"].tolist() == [2, 1, 0]
    assert result[result.unit_id == 2]["rul_raw"].tolist() == [1, 0]


def test_group_split_never_leaks_engine_ids():
    rows = []
    for unit_id in range(1, 11):
        for cycle in range(1, 4):
            rows.append({"unit_id": unit_id, "cycle": cycle})
    frame = pd.DataFrame(rows)
    train, validation = split_by_engine(frame, validation_fraction=0.2)
    assert set(train.unit_id).isdisjoint(set(validation.unit_id))
    assert len(set(validation.unit_id)) == 2
