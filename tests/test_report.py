import pandas as pd
import pytest

from petrichor.delta import append_delta
from petrichor.report import load_log, summarize


def _frame():
    return pd.DataFrame(
        [
            {"date": "2026-09-24", "zone": "tomatoes", "deficit_mm": 7.7,
             "rain_next_2d_mm": 0.0, "verdict": "OK"},
            {"date": "2026-09-25", "zone": "tomatoes", "deficit_mm": 18.9,
             "rain_next_2d_mm": 0.0, "verdict": "OK"},
            {"date": "2026-09-26", "zone": "tomatoes", "deficit_mm": 25.1,
             "rain_next_2d_mm": 0.0, "verdict": "WATER"},
            {"date": "2026-09-25", "zone": "succulents", "deficit_mm": 23.0,
             "rain_next_2d_mm": 5.0, "verdict": "SKIP (rain coming)"},
            {"date": "2026-09-26", "zone": "succulents", "deficit_mm": 21.0,
             "rain_next_2d_mm": 0.0, "verdict": "OK"},
        ]
    )


def test_summarize_counts_and_last_values():
    rows = {row["zone"]: row for row in summarize(_frame())}

    tomatoes = rows["tomatoes"]
    assert tomatoes["days_logged"] == 3
    assert tomatoes["water_days"] == 1
    assert tomatoes["skip_days"] == 0
    assert tomatoes["last_date"] == "2026-09-26"
    assert tomatoes["last_deficit_mm"] == 25.1
    assert tomatoes["last_verdict"] == "WATER"

    succulents = rows["succulents"]
    assert succulents["days_logged"] == 2
    assert succulents["water_days"] == 0
    assert succulents["skip_days"] == 1
    assert succulents["last_verdict"] == "OK"


def test_load_log_from_csv(tmp_path):
    log_path = tmp_path / "watering_log.csv"
    _frame().to_csv(log_path, index=False)

    frame = load_log(log_path=log_path)

    assert len(frame) == 5
    assert summarize(frame)[0]["zone"] in {"tomatoes", "succulents"}


def test_load_log_from_delta(tmp_path):
    delta_path = tmp_path / "watering_log_delta"
    append_delta(delta_path, _frame().to_dict(orient="records"))

    frame = load_log(delta_path=delta_path)

    assert len(frame) == 5
    rows = {row["zone"]: row for row in summarize(frame)}
    assert rows["tomatoes"]["water_days"] == 1


def test_load_log_missing_csv(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_log(log_path=tmp_path / "nope.csv")


def test_load_log_missing_delta(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_log(delta_path=tmp_path / "nope_delta")
