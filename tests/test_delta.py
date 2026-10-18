from deltalake import DeltaTable

from petrichor.delta import LOG_COLUMNS, append_delta


def _row(day, zone, deficit):
    return {
        "date": day,
        "zone": zone,
        "deficit_mm": deficit,
        "rain_next_2d_mm": 0.0,
        "verdict": "OK",
    }


def test_delta_append_and_time_travel(tmp_path):
    delta_path = tmp_path / "nested" / "watering_log_delta"
    first_run = [_row("2026-09-25", "tomatoes", 7.7)]
    second_run = [_row("2026-09-26", "tomatoes", 8.9)]

    append_delta(delta_path, first_run)
    append_delta(delta_path, second_run)

    table = DeltaTable(str(delta_path))
    current = table.to_pandas()
    assert table.version() == 1
    assert list(current.columns) == LOG_COLUMNS
    current_rows = sorted(
        current.to_dict(orient="records"), key=lambda row: row["date"]
    )
    assert current_rows == first_run + second_run

    first_version = DeltaTable(str(delta_path), version=0).to_pandas()
    assert first_version.to_dict(orient="records") == first_run
